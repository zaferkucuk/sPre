"""
Management command for data synchronization.

This command allows manual triggering of data sync operations from the command line.
"""

import logging
from django.core.management.base import BaseCommand, CommandError

from apps.datasources.sync_service import DataSyncService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Django management command for syncing external data.
    
    Usage:
        # Sync leagues
        python manage.py sync_data --type leagues
        
        # Sync teams for Premier League
        python manage.py sync_data --type teams --league 39
        
        # Sync matches for Premier League
        python manage.py sync_data --type matches --league 39
        
        # Full sync (teams + matches)
        python manage.py sync_data --type full --league 39
    """
    
    help = 'Synchronize data from external sources to database'
    
    def add_arguments(self, parser):
        """
        Add command arguments.
        """
        parser.add_argument(
            '--type',
            type=str,
            required=True,
            choices=['leagues', 'teams', 'matches', 'full'],
            help='Type of data to sync'
        )
        
        parser.add_argument(
            '--league',
            type=str,
            help='League external ID (required for teams, matches, full)'
        )
        
        parser.add_argument(
            '--sport',
            type=int,
            default=1,
            help='Sport ID (default: 1 for football)'
        )
        
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days ahead to sync matches (default: 30)'
        )
    
    def handle(self, *args, **options):
        """
        Handle command execution.
        """
        sync_type = options['type']
        league_id = options.get('league')
        sport_id = options['sport']
        days_ahead = options['days']
        
        # Validate arguments
        if sync_type in ['teams', 'matches', 'full'] and not league_id:
            raise CommandError(f"--league is required for {sync_type} sync")
        
        self.stdout.write(f"Starting {sync_type} sync...")
        
        try:
            sync_service = DataSyncService()
            
            # Execute appropriate sync
            if sync_type == 'leagues':
                result = sync_service.sync_leagues(sport_id=sport_id)
                self._print_result('Leagues', result)
            
            elif sync_type == 'teams':
                result = sync_service.sync_teams(
                    league_external_id=league_id,
                    sport_id=sport_id
                )
                self._print_result('Teams', result)
            
            elif sync_type == 'matches':
                result = sync_service.sync_matches(
                    league_external_id=league_id,
                    days_ahead=days_ahead,
                    sport_id=sport_id
                )
                self._print_result('Matches', result)
            
            elif sync_type == 'full':
                results = sync_service.full_sync(league_external_id=league_id)
                self.stdout.write("\n=== Teams Sync ===")
                self._print_result('Teams', results['teams'])
                self.stdout.write("\n=== Matches Sync ===")
                self._print_result('Matches', results['matches'])
            
            # Cleanup
            sync_service.cleanup()
            
            self.stdout.write(self.style.SUCCESS('\nSync completed successfully!'))
        
        except Exception as e:
            logger.error(f"Sync failed: {str(e)}")
            raise CommandError(f"Sync failed: {str(e)}")
    
    def _print_result(self, data_type: str, result: dict):
        """
        Print sync result in a formatted way.
        """
        if not result:
            self.stdout.write(self.style.ERROR(f"{data_type}: No result"))
            return
        
        self.stdout.write(f"\n{data_type} Sync Result:")
        self.stdout.write(f"  Created: {result.get('created', 0)}")
        self.stdout.write(f"  Updated: {result.get('updated', 0)}")
        self.stdout.write(f"  Skipped: {result.get('skipped', 0)}")
        self.stdout.write(f"  Errors: {result.get('errors', 0)}")
        
        if result.get('error_messages'):
            self.stdout.write(self.style.ERROR("\nError Messages:"))
            for msg in result['error_messages']:
                self.stdout.write(f"  - {msg}")
        
        if result.get('success'):
            self.stdout.write(self.style.SUCCESS(f"  Status: ✓ Success"))
        else:
            self.stdout.write(self.style.WARNING(f"  Status: ⚠ Completed with errors"))
