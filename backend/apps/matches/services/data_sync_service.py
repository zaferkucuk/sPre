"""
Main data synchronization service.

Handles:
- Initial data load (one-time, manual)
- Daily incremental updates (automated)
- Smart update detection (avoid redundant API calls)
"""

from datetime import datetime, timedelta
from django.utils import timezone
from apps.matches.models import League, Team, TeamStatistics, Season, Fixture
from .api_client import APIFootballClient
from .data_transformer import DataTransformer
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class DataSyncService:
    """
    Centralized service for data synchronization.
    
    Two main modes:
    1. Initial Load: Fetch all season data (one-time)
    2. Daily Sync: Update only new/changed data (automated)
    """
    
    def __init__(self):
        self.api_client = APIFootballClient()
        self.transformer = DataTransformer()
    
    def initial_load_league(
        self,
        league: League,
        season: Season,
        verbose: bool = True
    ) -> Dict[str, int]:
        """
        Initial data load for a league (ONE-TIME OPERATION).
        
        Fetches ALL season data from start to now:
        - Current standings
        - All fixtures (past + future)
        - All results
        """
        if verbose:
            print(f"\n{'='*60}")
            print(f"📥 INITIAL LOAD: {league.name} - {season.name}")
            print(f"{'='*60}\n")
        
        stats = {
            'teams_synced': 0,
            'fixtures_created': 0,
            'fixtures_updated': 0,
            'api_requests': 0
        }
        
        try:
            # Step 1: Load standings
            if verbose:
                print("Step 1/2: Loading team statistics from standings...")
            
            standings = self.api_client.get_standings(
                league_id=league.api_id,
                season=season.year
            )
            stats['api_requests'] += 1
            
            for standing_data in standings:
                try:
                    team = Team.objects.get(
                        external_id=str(standing_data['team']['id'])
                    )
                    
                    stat_fields = self.transformer.transform_standing_to_statistics(
                        standing_data,
                        team,
                        season
                    )
                    
                    if stat_fields:
                        TeamStatistics.objects.update_or_create(
                            team=team,
                            season=season,
                            defaults=stat_fields
                        )
                        stats['teams_synced'] += 1
                        
                        if verbose:
                            print(f"  ✓ {team.name}: {stat_fields['points']} pts")
                    
                except Team.DoesNotExist:
                    logger.warning(
                        f"Team {standing_data['team']['name']} not found in DB"
                    )
                    continue
            
            if verbose:
                print(f"\n  Synced {stats['teams_synced']} teams\n")
            
            # Step 2: Load ALL fixtures
            if verbose:
                print("Step 2/2: Loading all season fixtures...")
            
            season_start = datetime(season.year, 8, 1).date()
            season_end = datetime(season.year + 1, 5, 31).date()
            
            fixtures = self.api_client.get_fixtures(
                league_id=league.api_id,
                from_date=season_start.isoformat(),
                to_date=season_end.isoformat(),
                season=season.year
            )
            stats['api_requests'] += 1
            
            if verbose:
                print(f"  Found {len(fixtures)} fixtures")
            
            for fixture_data in fixtures:
                try:
                    fixture_fields = self.transformer.transform_fixture_to_model(
                        fixture_data,
                        league,
                        season
                    )
                    
                    if not fixture_fields:
                        continue
                    
                    api_fixture_id = fixture_fields.pop('api_fixture_id')
                    
                    fixture, created = Fixture.objects.update_or_create(
                        api_fixture_id=api_fixture_id,
                        defaults=fixture_fields
                    )
                    
                    if created:
                        stats['fixtures_created'] += 1
                    else:
                        stats['fixtures_updated'] += 1
                    
                except Exception as e:
                    logger.error(f"Error processing fixture: {e}")
                    continue
            
            if verbose:
                print(f"  ✓ Created: {stats['fixtures_created']}")
                print(f"  ✓ Updated: {stats['fixtures_updated']}\n")
                print(f"{'='*60}")
                print(f"✅ Initial load completed!")
                print(f"   Teams: {stats['teams_synced']}")
                print(f"   Fixtures: {stats['fixtures_created']} new, {stats['fixtures_updated']} updated")
                print(f"   API Requests: {stats['api_requests']}")
                print(f"{'='*60}\n")
            
            return stats
            
        except Exception as e:
            logger.error(f"Initial load failed for {league.name}: {e}")
            if verbose:
                print(f"\n❌ Error: {e}\n")
            return stats
    
    def daily_sync_league(
        self,
        league: League,
        season: Season,
        verbose: bool = False
    ) -> Dict[str, int]:
        """
        Daily incremental sync for a league.
        
        Updates ONLY:
        - Current standings (daily changes)
        - Recent results (last 24 hours)
        - Upcoming fixtures (next 7 days)
        
        Does NOT re-fetch old data!
        """
        stats = {
            'teams_updated': 0,
            'new_results': 0,
            'fixtures_updated': 0,
            'api_requests': 0
        }
        
        try:
            # Update 1: Current standings
            standings = self.api_client.get_standings(
                league_id=league.api_id,
                season=season.year
            )
            stats['api_requests'] += 1
            
            for standing_data in standings:
                try:
                    team = Team.objects.get(
                        external_id=str(standing_data['team']['id'])
                    )
                    
                    stat_fields = self.transformer.transform_standing_to_statistics(
                        standing_data,
                        team,
                        season
                    )
                    
                    if stat_fields:
                        TeamStatistics.objects.update_or_create(
                            team=team,
                            season=season,
                            defaults=stat_fields
                        )
                        stats['teams_updated'] += 1
                    
                except Team.DoesNotExist:
                    continue
            
            # Update 2: Recent results (last 24 hours)
            yesterday = (timezone.now() - timedelta(days=1)).date()
            today = timezone.now().date()
            
            recent_fixtures = self.api_client.get_fixtures(
                league_id=league.api_id,
                from_date=yesterday.isoformat(),
                to_date=today.isoformat(),
                season=season.year
            )
            stats['api_requests'] += 1
            
            for fixture_data in recent_fixtures:
                if fixture_data['fixture']['status']['short'] == 'FT':
                    fixture_fields = self.transformer.transform_fixture_to_model(
                        fixture_data,
                        league,
                        season
                    )
                    
                    if fixture_fields:
                        api_fixture_id = fixture_fields.pop('api_fixture_id')
                        
                        fixture, created = Fixture.objects.update_or_create(
                            api_fixture_id=api_fixture_id,
                            defaults=fixture_fields
                        )
                        
                        if fixture.status == 'FINISHED':
                            stats['new_results'] += 1
            
            # Update 3: Upcoming fixtures (next 7 days)
            tomorrow = (timezone.now() + timedelta(days=1)).date()
            next_week = (timezone.now() + timedelta(days=7)).date()
            
            upcoming_fixtures = self.api_client.get_fixtures(
                league_id=league.api_id,
                from_date=tomorrow.isoformat(),
                to_date=next_week.isoformat(),
                season=season.year
            )
            stats['api_requests'] += 1
            
            for fixture_data in upcoming_fixtures:
                fixture_fields = self.transformer.transform_fixture_to_model(
                    fixture_data,
                    league,
                    season
                )
                
                if fixture_fields:
                    api_fixture_id = fixture_fields.pop('api_fixture_id')
                    
                    if not Fixture.objects.filter(api_fixture_id=api_fixture_id).exists():
                        Fixture.objects.create(
                            api_fixture_id=api_fixture_id,
                            **fixture_fields
                        )
                        stats['fixtures_updated'] += 1
            
            if verbose:
                print(f"✓ {league.name}: {stats['teams_updated']} teams, "
                      f"{stats['new_results']} new results, "
                      f"{stats['fixtures_updated']} new fixtures")
            
            return stats
            
        except Exception as e:
            logger.error(f"Daily sync failed for {league.name}: {e}")
            return stats
    
    def sync_all_leagues_initial(self, verbose: bool = True):
        """Initial load for ALL configured leagues."""
        if verbose:
            print("\n" + "="*60)
            print("🚀 INITIAL DATA LOAD - ALL LEAGUES")
            print("="*60)
            print("⚠️  This will fetch ALL season data!")
            print("⚠️  Estimated API requests: ~40-50")
            print("="*60 + "\n")
        
        current_season = Season.objects.get(is_current=True)
        active_leagues = League.objects.filter(is_active=True)
        
        total_stats = {
            'leagues_synced': 0,
            'total_teams': 0,
            'total_fixtures': 0,
            'total_requests': 0
        }
        
        for league in active_leagues:
            stats = self.initial_load_league(league, current_season, verbose)
            
            total_stats['leagues_synced'] += 1
            total_stats['total_teams'] += stats['teams_synced']
            total_stats['total_fixtures'] += stats['fixtures_created']
            total_stats['total_requests'] += stats['api_requests']
        
        if verbose:
            print("\n" + "="*60)
            print("✅ INITIAL LOAD COMPLETED!")
            print("="*60)
            print(f"Leagues synced: {total_stats['leagues_synced']}")
            print(f"Teams synced: {total_stats['total_teams']}")
            print(f"Fixtures loaded: {total_stats['total_fixtures']}")
            print(f"API requests used: {total_stats['total_requests']}")
            print("="*60 + "\n")
        
        return total_stats
    
    def sync_all_leagues_daily(self, verbose: bool = False):
        """Daily sync for ALL configured leagues."""
        if verbose:
            print(f"\n📅 Daily Sync - {timezone.now().date()}\n")
        
        current_season = Season.objects.get(is_current=True)
        active_leagues = League.objects.filter(is_active=True)
        
        total_stats = {
            'leagues_synced': 0,
            'total_updates': 0,
            'total_requests': 0
        }
        
        for league in active_leagues:
            stats = self.daily_sync_league(league, current_season, verbose)
            
            total_stats['leagues_synced'] += 1
            total_stats['total_updates'] += (
                stats['teams_updated'] + 
                stats['new_results'] + 
                stats['fixtures_updated']
            )
            total_stats['total_requests'] += stats['api_requests']
        
        if verbose:
            print(f"\n✅ Daily sync completed!")
            print(f"   Leagues: {total_stats['leagues_synced']}")
            print(f"   Updates: {total_stats['total_updates']}")
            print(f"   API Requests: {total_stats['total_requests']}\n")
        
        return total_stats