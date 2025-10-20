"""
Management command to test Football-Data.org API connection.

Usage:
    python manage.py test_football_api
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.matches.services.football_data_org_client import FootballDataOrgClient
import json


class Command(BaseCommand):
    help = 'Test Football-Data.org API connection and basic endpoints'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--league',
            type=str,
            default='PL',
            help='League code to test (default: PL for Premier League)'
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output'
        )
    
    def handle(self, *args, **options):
        """Execute the command."""
        league_code = options['league']
        verbose = options.get('verbose', False)
        
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f"\n🏟️  Testing Football-Data.org API..."
            )
        )
        
        # Initialize client
        client = FootballDataOrgClient()
        
        # Test 1: Connection Test
        self.stdout.write("\n1️⃣  Testing API connection...")
        result = client.test_connection()
        
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Connection successful!"
                )
            )
            if verbose and 'data' in result:
                self.stdout.write(
                    f"   Competition: {result['data'].get('name', 'N/A')}"
                )
                self.stdout.write(
                    f"   Current Season: {result['data'].get('currentSeason', {}).get('startDate', 'N/A')}"
                )
        else:
            self.stdout.write(
                self.style.ERROR(
                    f"❌ Connection failed: {result.get('message', 'Unknown error')}"
                )
            )
            return
        
        # Test 2: Get Standings
        self.stdout.write(f"\n2️⃣  Fetching {league_code} standings...")
        try:
            standings = client.get_standings(league_code)
            
            if standings:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Retrieved {len(standings)} teams"
                    )
                )
                
                # Show top 5 teams
                self.stdout.write("\n   Top 5 Teams:")
                for i, team in enumerate(standings[:5], 1):
                    self.stdout.write(
                        f"   {i}. {team['team']['name']} - "
                        f"{team['points']} pts "
                        f"(W:{team['won']} D:{team['draw']} L:{team['lost']})"
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        "⚠️  No standings data available"
                    )
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"❌ Error fetching standings: {str(e)}"
                )
            )
        
        # Test 3: Get Recent Matches
        self.stdout.write(f"\n3️⃣  Fetching recent matches...")
        try:
            matches = client.get_matches(
                league_code,
                status='FINISHED'
            )
            
            if matches:
                # Get last 5 matches
                recent_matches = matches[:5]
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Retrieved {len(matches)} matches"
                    )
                )
                
                self.stdout.write("\n   Recent Results:")
                for match in recent_matches:
                    home_team = match['homeTeam']['name']
                    away_team = match['awayTeam']['name']
                    home_score = match['score']['fullTime']['home']
                    away_score = match['score']['fullTime']['away']
                    
                    self.stdout.write(
                        f"   {home_team} {home_score} - {away_score} {away_team}"
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        "⚠️  No match data available"
                    )
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"❌ Error fetching matches: {str(e)}"
                )
            )
        
        # Test 4: API Rate Limit Stats
        self.stdout.write("\n4️⃣  API Usage Statistics:")
        stats = client.get_request_stats()
        
        self.stdout.write(
            f"   Requests this minute: {stats['requests_this_minute']}/{stats['rate_limit']}"
        )
        self.stdout.write(
            f"   Remaining: {stats['remaining']}"
        )
        self.stdout.write(
            f"   Usage: {stats['percentage_used']}%"
        )
        
        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                "\n✨ API test completed successfully!"
            )
        )
        
        # Available leagues
        if verbose:
            self.stdout.write("\n📋 Available Leagues (Free Tier):")
            for name, code in client.COMPETITIONS.items():
                if code in ['PL', 'PD', 'BL1', 'SA', 'FL1', 'DED', 'PPL', 'ELC']:
                    self.stdout.write(f"   {name}: {code}")
