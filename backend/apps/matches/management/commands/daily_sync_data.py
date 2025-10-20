"""
Daily incremental data sync.

Updates only recent/changed data:
- Current standings
- Yesterday's results
- Next week's fixtures

Usage:
    python manage.py daily_sync_data
    python manage.py daily_sync_data --verbose
    
Cron: Run daily at 3 AM
    0 3 * * * cd /path/to/spre && python manage.py daily_sync_data
"""

from django.core.management.base import BaseCommand
from apps.matches.services.data_sync_service import DataSyncService
from apps.matches.services.api_client import APIFootballClient


class Command(BaseCommand):
    help = '📅 Daily incremental data sync (automated)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed sync progress'
        )
    
    def handle(self, *args, **options):
        """Execute daily sync."""
        
        verbose = options.get('verbose', False)
        
        client = APIFootballClient()
        service = DataSyncService()
        
        # Show API usage before sync
        usage = client.get_request_stats()
        self.stdout.write(
            f"\n📊 API Usage: {usage['requests_today']}/{usage['rate_limit']}"
        )
        
        if usage['remaining'] < 10:
            self.stdout.write(
                self.style.WARNING(
                    f"⚠️  Low API quota remaining: {usage['remaining']} requests"
                )
            )
        
        # Execute daily sync
        self.stdout.write('\n🔄 Starting daily sync...\n')
        
        try:
            stats = service.sync_all_leagues_daily(verbose=verbose)
            
            # Show final API usage
            final_usage = client.get_request_stats()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✅ Daily sync completed!"
                )
            )
            self.stdout.write(
                f"   API Usage: {final_usage['requests_today']}/{final_usage['rate_limit']}"
            )
            self.stdout.write(
                f"   Requests Used: {stats['total_requests']}"
            )
            self.stdout.write(
                f"   Leagues Synced: {stats['leagues_synced']}"
            )
            self.stdout.write(
                f"   Total Updates: {stats['total_updates']}\n"
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'\n❌ Sync failed: {e}\n')
            )
            raise
