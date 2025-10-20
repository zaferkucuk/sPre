"""
Daily incremental sync command.

Updates only new/changed data.
Safe to run daily via cron.

Usage:
    python manage.py sync_daily_stats
    python manage.py sync_daily_stats --verbose
"""

from django.core.management.base import BaseCommand
from apps.matches.services.data_sync_service import DataSyncService
from apps.matches.services.api_client import APIFootballClient


class Command(BaseCommand):
    help = 'Daily sync: Update only new/changed data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed progress'
        )
    
    def handle(self, *args, **options):
        """Execute daily sync."""
        
        verbose = options['verbose']
        
        # Initialize service
        service = DataSyncService()
        client = APIFootballClient()
        
        if verbose:
            usage = client.get_request_stats()
            self.stdout.write(
                f"API usage before sync: {usage['requests_today']}/{usage['rate_limit']}\n"
            )
        
        # Execute daily sync
        try:
            stats = service.sync_all_leagues_daily(verbose=verbose)
            
            if not verbose:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Daily sync completed: "
                        f"{stats['leagues_synced']} leagues, "
                        f"{stats['total_updates']} updates, "
                        f"{stats['total_requests']} API requests"
                    )
                )
            
            # Show final usage
            final_usage = client.get_request_stats()
            if verbose:
                self.stdout.write(
                    f"API usage after sync: {final_usage['requests_today']}/{final_usage['rate_limit']}"
                )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Daily sync failed: {e}')
            )