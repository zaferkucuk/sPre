"""
ONE-TIME initial data load command.

Fetches all season data from start to now.
Should only be run once per season!

Usage:
    python manage.py load_initial_data
    python manage.py load_initial_data --league "Premier League"
    python manage.py load_initial_data --dry-run
"""

from django.core.management.base import BaseCommand
from apps.matches.services.data_sync_service import DataSyncService
from apps.matches.services.api_client import APIFootballClient
from apps.matches.models import League, Season


class Command(BaseCommand):
    help = '⚠️  ONE-TIME: Load all season data from start to now'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--league',
            type=str,
            help='Specific league name to load (otherwise all leagues)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be loaded without actually loading'
        )
    
    def handle(self, *args, **options):
        """Execute initial data load."""
        
        # Confirmation check
        if not options['dry_run']:
            self.stdout.write(
                self.style.WARNING('\n⚠️  WARNING: INITIAL DATA LOAD ⚠️')
            )
            self.stdout.write(
                'This will fetch ALL season data from API-Football.'
            )
            self.stdout.write(
                'Estimated API requests: 40-50 (half your daily limit)\n'
            )
            
            confirm = input('Are you sure you want to continue? (yes/no): ')
            if confirm.lower() != 'yes':
                self.stdout.write(
                    self.style.ERROR('Operation cancelled.')
                )
                return
        
        # Initialize service
        service = DataSyncService()
        client = APIFootballClient()
        
        # Show current API usage
        usage = client.get_request_stats()
        self.stdout.write(
            f"\nCurrent API usage: {usage['requests_today']}/{usage['rate_limit']}"
        )
        self.stdout.write(
            f"Remaining: {usage['remaining']} requests\n"
        )
        
        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No data will be loaded\n')
            )
            
            # Show what would be loaded
            current_season = Season.objects.get(is_current=True)
            
            if options['league']:
                leagues = League.objects.filter(
                    name__icontains=options['league'],
                    is_active=True
                )
            else:
                leagues = League.objects.filter(is_active=True)
            
            self.stdout.write('Would load data for:')
            for league in leagues:
                team_count = league.teams.count()
                self.stdout.write(
                    f"  - {league.name} ({team_count} teams)"
                )
            
            estimated_requests = len(leagues) * 2  # standings + fixtures
            self.stdout.write(
                f"\nEstimated API requests: ~{estimated_requests}\n"
            )
            return
        
        # Execute initial load
        try:
            current_season = Season.objects.get(is_current=True)
            
            if options['league']:
                # Load specific league
                league = League.objects.get(
                    name__icontains=options['league'],
                    is_active=True
                )
                stats = service.initial_load_league(
                    league,
                    current_season,
                    verbose=True
                )
            else:
                # Load all leagues
                stats = service.sync_all_leagues_initial(verbose=True)
            
            # Show final API usage
            final_usage = client.get_request_stats()
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✅ Final API usage: {final_usage['requests_today']}/{final_usage['rate_limit']}"
                )
            )
            
        except Season.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    'No current season found! Please create a season first.'
                )
            )
        except League.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    f"League '{options['league']}' not found!"
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during initial load: {e}')
            )