"""
Test API-Football connection and verify credentials.

This command:
1. Tests API connectivity
2. Checks authentication
3. Verifies account status
4. Fetches sample data from Premier League

Usage:
    python manage.py test_api_connection
    python manage.py test_api_connection --full
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from apps.matches.services.api_client import APIFootballClient
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Test API-Football connection and verify setup'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--full',
            action='store_true',
            help='Run full test suite including data fetching',
        )
    
    def handle(self, *args, **options):
        """Execute the test command."""
        self.stdout.write(self.style.WARNING('\n' + '='*60))
        self.stdout.write(self.style.WARNING('🔧 API-FOOTBALL CONNECTION TEST'))
        self.stdout.write(self.style.WARNING('='*60 + '\n'))
        
        # Initialize client
        client = APIFootballClient()
        
        # Test 1: Configuration
        self.test_configuration()
        
        # Test 2: API Connection
        connection_ok = self.test_connection(client)
        
        if not connection_ok:
            self.stdout.write(
                self.style.ERROR('\n❌ Connection test failed. Please check your API key.\n')
            )
            return
        
        # Test 3: Usage Statistics
        self.test_usage_stats(client)
        
        # Test 4: Data Fetching (if --full flag)
        if options['full']:
            self.test_data_fetching(client)
        else:
            self.stdout.write(
                self.style.WARNING(
                    '\n💡 Tip: Run with --full flag to test data fetching\n'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS('\n✅ All tests completed!\n')
        )
    
    def test_configuration(self):
        """Test if settings are configured correctly."""
        self.stdout.write('📋 Testing Configuration...')
        
        required_settings = [
            'API_FOOTBALL_KEY',
            'API_FOOTBALL_BASE_URL',
            'API_FOOTBALL_RATE_LIMIT'
        ]
        
        all_ok = True
        for setting in required_settings:
            if hasattr(settings, setting):
                value = getattr(settings, setting)
                if setting == 'API_FOOTBALL_KEY':
                    # Mask API key for security
                    display_value = f"{value[:8]}...{value[-4:]}"
                else:
                    display_value = value
                
                self.stdout.write(f'  ✓ {setting}: {display_value}')
            else:
                self.stdout.write(
                    self.style.ERROR(f'  ✗ {setting}: NOT FOUND')
                )
                all_ok = False
        
        if all_ok:
            self.stdout.write(self.style.SUCCESS('  Configuration OK\n'))
        else:
            self.stdout.write(
                self.style.ERROR('  Configuration INCOMPLETE\n')
            )
        
        return all_ok
    
    def test_connection(self, client: APIFootballClient) -> bool:
        """Test API connection and authentication."""
        self.stdout.write('🔌 Testing API Connection...')
        
        result = client.test_connection()
        
        if result['success']:
            self.stdout.write(self.style.SUCCESS('  ✓ Connection successful'))
            
            # Display account info if available
            data = result.get('data', {})
            if 'response' in data:
                account = data['response'].get('account', {})
                self.stdout.write(f"  Account: {account.get('firstname', 'N/A')}")
                self.stdout.write(f"  Email: {account.get('email', 'N/A')}")
            
            self.stdout.write('')
            return True
        else:
            self.stdout.write(
                self.style.ERROR(f"  ✗ Connection failed: {result.get('error')}")
            )
            self.stdout.write('')
            return False
    
    def test_usage_stats(self, client: APIFootballClient):
        """Display current API usage statistics."""
        self.stdout.write('📊 API Usage Statistics...')
        
        stats = client.get_request_stats()
        
        self.stdout.write(f"  Date: {stats['date']}")
        self.stdout.write(
            f"  Requests today: {stats['requests_today']}/{stats['rate_limit']}"
        )
        self.stdout.write(
            f"  Remaining: {stats['remaining']} ({100 - stats['percentage_used']:.1f}%)"
        )
        
        # Color code usage percentage
        if stats['percentage_used'] < 50:
            color = self.style.SUCCESS
        elif stats['percentage_used'] < 80:
            color = self.style.WARNING
        else:
            color = self.style.ERROR
        
        self.stdout.write(
            color(f"  Usage: {stats['percentage_used']}%\n")
        )
    
    def test_data_fetching(self, client: APIFootballClient):
        """Test actual data fetching from API."""
        self.stdout.write(self.style.WARNING('🧪 Running Data Fetch Tests...\n'))
        
        # Test with Premier League (ID: 39, Season: 2025)
        league_id = 39
        season = 2025
        
        # Test 1: Get Standings
        self.stdout.write('  Test 1: Fetching Premier League standings...')
        standings = client.get_standings(league_id, season)
        
        if standings:
            self.stdout.write(
                self.style.SUCCESS(
                    f'    ✓ Retrieved {len(standings)} teams'
                )
            )
            # Show top 3 teams
            for i, team in enumerate(standings[:3], 1):
                team_name = team['team']['name']
                points = team['points']
                self.stdout.write(f'      {i}. {team_name} - {points} pts')
        else:
            self.stdout.write(
                self.style.ERROR('    ✗ Failed to fetch standings')
            )
        
        # Test 2: Get Fixtures (next 7 days)
        self.stdout.write('\n  Test 2: Fetching upcoming fixtures...')
        today = datetime.now().date()
        next_week = today + timedelta(days=7)
        
        fixtures = client.get_fixtures(
            league_id,
            today.isoformat(),
            next_week.isoformat(),
            season=season
        )
        
        if fixtures:
            self.stdout.write(
                self.style.SUCCESS(
                    f'    ✓ Retrieved {len(fixtures)} fixtures'
                )
            )
            # Show next 3 fixtures
            for fixture in fixtures[:3]:
                home = fixture['teams']['home']['name']
                away = fixture['teams']['away']['name']
                date = fixture['fixture']['date'][:10]
                status = fixture['fixture']['status']['short']
                self.stdout.write(f'      {date}: {home} vs {away} [{status}]')
        else:
            self.stdout.write(
                self.style.WARNING('    ⚠ No upcoming fixtures found')
            )
        
        # Test 3: Get Team Statistics
        self.stdout.write('\n  Test 3: Fetching team statistics...')
        if standings:
            # Get stats for first team in standings
            first_team = standings[0]
            team_id = first_team['team']['id']
            team_name = first_team['team']['name']
            
            stats = client.get_team_statistics(team_id, league_id, season)
            
            if stats:
                self.stdout.write(
                    self.style.SUCCESS(f'    ✓ Retrieved stats for {team_name}')
                )
                
                # Display key stats
                form = stats.get('form', 'N/A')
                fixtures_data = stats.get('fixtures', {})
                played = fixtures_data.get('played', {}).get('total', 0)
                goals_for = stats.get('goals', {}).get('for', {}).get('total', {}).get('total', 0)
                goals_against = stats.get('goals', {}).get('against', {}).get('total', {}).get('total', 0)
                
                self.stdout.write(f'      Form: {form}')
                self.stdout.write(f'      Matches: {played}')
                self.stdout.write(f'      Goals: {goals_for}:{goals_against}')
            else:
                self.stdout.write(
                    self.style.ERROR(f'    ✗ Failed to fetch stats for {team_name}')
                )
        
        self.stdout.write('')
        
        # Final usage check
        final_stats = client.get_request_stats()
        self.stdout.write(
            self.style.WARNING(
                f"  API Requests used in this test: "
                f"{final_stats['requests_today']}/{final_stats['rate_limit']}\n"
            )
        )