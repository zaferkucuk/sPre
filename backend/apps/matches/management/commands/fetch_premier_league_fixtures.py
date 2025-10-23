"""
Management command to fetch Premier League fixtures from API-Football.

This command fetches upcoming and recent fixtures for Premier League
and saves them to the database.

Usage:
    python manage.py fetch_premier_league_fixtures
    python manage.py fetch_premier_league_fixtures --days 60  # Fetch 60 days of fixtures
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.datasources.fetchers.football_api_fetcher import FootballAPIFetcher
from apps.matches.models import League, Team, Match

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Management command to fetch Premier League fixtures.
    
    Features:
    - Fetches fixtures from API-Football
    - Creates or updates leagues, teams, and matches in database
    - Handles duplicates gracefully
    - Provides detailed progress feedback
    
    Examples:
        # Fetch next 30 days of fixtures (default)
        python manage.py fetch_premier_league_fixtures
        
        # Fetch next 60 days of fixtures
        python manage.py fetch_premier_league_fixtures --days 60
        
        # Verbose output
        python manage.py fetch_premier_league_fixtures -v 2
    """
    
    help = 'Fetch Premier League fixtures from API-Football'
    
    # Premier League ID in API-Football
    PREMIER_LEAGUE_ID = 39
    PREMIER_LEAGUE_NAME = "Premier League"
    PREMIER_LEAGUE_COUNTRY = "England"
    
    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days of fixtures to fetch (default: 30)'
        )
        
        parser.add_argument(
            '--from-date',
            type=str,
            help='Start date in YYYY-MM-DD format (default: today)'
        )
        
        parser.add_argument(
            '--to-date',
            type=str,
            help='End date in YYYY-MM-DD format (default: today + days)'
        )
    
    def handle(self, *args, **options):
        """Execute the command."""
        try:
            # Get command options
            days = options['days']
            from_date_str = options.get('from_date')
            to_date_str = options.get('to_date')
            
            # Parse dates
            if from_date_str:
                from_date = datetime.strptime(from_date_str, '%Y-%m-%d')
            else:
                from_date = datetime.now()
            
            if to_date_str:
                to_date = datetime.strptime(to_date_str, '%Y-%m-%d')
            else:
                to_date = from_date + timedelta(days=days)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n{'='*60}\n"
                    f"  Fetching Premier League Fixtures\n"
                    f"{'='*60}\n"
                )
            )
            
            self.stdout.write(f"Period: {from_date.date()} to {to_date.date()}")
            self.stdout.write(f"Days: {days}\n")
            
            # Initialize fetcher
            self.stdout.write("Initializing API-Football fetcher...")
            fetcher = FootballAPIFetcher()
            
            # Step 1: Get or create league
            self.stdout.write("\nStep 1: Setting up Premier League...")
            league = self._get_or_create_league(fetcher)
            self.stdout.write(
                self.style.SUCCESS(f"✓ League ready: {league.name}")
            )
            
            # Step 2: Fetch fixtures
            self.stdout.write("\nStep 2: Fetching fixtures from API...")
            fixtures_data = fetcher.fetch_matches(
                league_id=self.PREMIER_LEAGUE_ID,
                from_date=from_date,
                to_date=to_date,
                season=from_date.year
            )
            
            if not fixtures_data:
                self.stdout.write(
                    self.style.WARNING(
                        f"No fixtures found for the specified period"
                    )
                )
                return
            
            self.stdout.write(
                self.style.SUCCESS(f"✓ Fetched {len(fixtures_data)} fixtures")
            )
            
            # Step 3: Process and save fixtures
            self.stdout.write("\nStep 3: Processing fixtures...")
            stats = self._process_fixtures(league, fixtures_data)
            
            # Display summary
            self._display_summary(stats, from_date, to_date)
            
        except Exception as e:
            logger.exception("Error fetching Premier League fixtures")
            raise CommandError(f"Failed to fetch fixtures: {str(e)}")
    
    def _get_or_create_league(self, fetcher: FootballAPIFetcher) -> League:
        """
        Get or create Premier League in database.
        
        Args:
            fetcher: Football API fetcher instance
            
        Returns:
            League instance
        """
        try:
            # Check if league already exists
            league = League.objects.filter(
                external_id=str(self.PREMIER_LEAGUE_ID)
            ).first()
            
            if league:
                return league
            
            # Fetch league data from API
            leagues_data = fetcher.fetch_leagues(sport_id=1)
            
            # Find Premier League in fetched data
            pl_data = None
            for league_data in leagues_data:
                if league_data.get('external_id') == str(self.PREMIER_LEAGUE_ID):
                    pl_data = league_data
                    break
            
            if not pl_data:
                # Create with minimal data if not found in API
                pl_data = {
                    'external_id': str(self.PREMIER_LEAGUE_ID),
                    'name': self.PREMIER_LEAGUE_NAME,
                    'country': self.PREMIER_LEAGUE_COUNTRY,
                    'season': str(datetime.now().year),
                }
            
            # Create league
            league = League.objects.create(
                external_id=pl_data['external_id'],
                name=pl_data.get('name', self.PREMIER_LEAGUE_NAME),
                country=pl_data.get('country', self.PREMIER_LEAGUE_COUNTRY),
                logo_url=pl_data.get('logo_url'),
                season=pl_data.get('season', str(datetime.now().year)),
            )
            
            logger.info(f"Created league: {league.name}")
            return league
            
        except Exception as e:
            logger.error(f"Error getting/creating league: {str(e)}")
            raise
    
    def _process_fixtures(
        self,
        league: League,
        fixtures_data: list
    ) -> dict:
        """
        Process and save fixtures to database.
        
        Args:
            league: League instance
            fixtures_data: List of fixture dictionaries from API
            
        Returns:
            Statistics dictionary
        """
        stats = {
            'total': len(fixtures_data),
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'teams_created': 0,
        }
        
        with transaction.atomic():
            for idx, fixture_data in enumerate(fixtures_data, 1):
                try:
                    # Progress indicator
                    if idx % 10 == 0 or idx == 1:
                        self.stdout.write(
                            f"  Processing fixture {idx}/{stats['total']}...",
                            ending='\r'
                        )
                    
                    # Get or create teams
                    home_team = self._get_or_create_team(
                        external_id=fixture_data['home_team_external_id'],
                        name=fixture_data['home_team_name'],
                        league=league
                    )
                    
                    away_team = self._get_or_create_team(
                        external_id=fixture_data['away_team_external_id'],
                        name=fixture_data['away_team_name'],
                        league=league
                    )
                    
                    if not home_team or not away_team:
                        stats['skipped'] += 1
                        continue
                    
                    # Check if match already exists
                    match = Match.objects.filter(
                        external_id=fixture_data['external_id']
                    ).first()
                    
                    # Prepare match data
                    match_data = {
                        'home_team': home_team,
                        'away_team': away_team,
                        'league': league,
                        'match_date': fixture_data.get('match_date'),
                        'venue': fixture_data.get('venue'),
                        'status': fixture_data.get('status', 'scheduled'),
                        'home_score': fixture_data.get('home_score'),
                        'away_score': fixture_data.get('away_score'),
                        'round': fixture_data.get('round'),
                    }
                    
                    if match:
                        # Update existing match
                        for key, value in match_data.items():
                            setattr(match, key, value)
                        match.save()
                        stats['updated'] += 1
                    else:
                        # Create new match
                        match = Match.objects.create(
                            external_id=fixture_data['external_id'],
                            **match_data
                        )
                        stats['created'] += 1
                    
                except Exception as e:
                    logger.error(
                        f"Error processing fixture {fixture_data.get('external_id')}: {str(e)}"
                    )
                    stats['skipped'] += 1
                    continue
        
        self.stdout.write()  # New line after progress indicator
        return stats
    
    def _get_or_create_team(
        self,
        external_id: str,
        name: str,
        league: League
    ) -> Optional[Team]:
        """
        Get or create team in database.
        
        Args:
            external_id: External team ID from API
            name: Team name
            league: League instance
            
        Returns:
            Team instance or None
        """
        try:
            # Try to get existing team
            team = Team.objects.filter(external_id=external_id).first()
            
            if team:
                return team
            
            # Create new team
            team = Team.objects.create(
                external_id=external_id,
                name=name,
                country=league.country,
            )
            
            # Add league to team's leagues
            team.leagues.add(league)
            
            logger.info(f"Created team: {team.name}")
            return team
            
        except Exception as e:
            logger.error(f"Error getting/creating team {name}: {str(e)}")
            return None
    
    def _display_summary(
        self,
        stats: dict,
        from_date: datetime,
        to_date: datetime
    ):
        """
        Display command execution summary.
        
        Args:
            stats: Statistics dictionary
            from_date: Start date
            to_date: End date
        """
        self.stdout.write(
            f"\n{'='*60}\n"
            f"  Summary\n"
            f"{'='*60}\n"
        )
        
        self.stdout.write(f"Period: {from_date.date()} to {to_date.date()}")
        self.stdout.write(f"Total fixtures fetched: {stats['total']}")
        self.stdout.write(
            self.style.SUCCESS(f"✓ Created: {stats['created']}")
        )
        self.stdout.write(
            self.style.WARNING(f"↻ Updated: {stats['updated']}")
        )
        
        if stats['skipped'] > 0:
            self.stdout.write(
                self.style.ERROR(f"✗ Skipped: {stats['skipped']}")
            )
        
        self.stdout.write(f"\n{'='*60}\n")
        
        # Success message
        if stats['created'] > 0 or stats['updated'] > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✓ Successfully processed Premier League fixtures!\n"
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"\n⚠ No new fixtures were added or updated.\n"
                )
            )
