#!/usr/bin/env python
"""
Quick test script for Football-Data.org API.

Usage:
    cd backend
    python test_api.py
"""

import os
import sys
import django

# Add backend to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

# Now we can import our client
from apps.matches.services.football_data_org_client import FootballDataOrgClient


def test_api():
    """Test Football-Data.org API connection."""
    print("🏟️  Testing Football-Data.org API...")
    print("-" * 50)
    
    # Initialize client
    client = FootballDataOrgClient()
    
    # Test connection
    print("\n1. Testing connection...")
    result = client.test_connection()
    
    if result['success']:
        print(f"   ✅ SUCCESS: {result['message']}")
        
        # Get Premier League standings
        print("\n2. Fetching Premier League standings...")
        standings = client.get_standings('PL')
        
        if standings:
            print(f"   ✅ Retrieved {len(standings)} teams")
            print("\n   Top 3 teams:")
            for i, team in enumerate(standings[:3], 1):
                print(f"   {i}. {team['team']['name']} - {team['points']} pts")
        else:
            print("   ⚠️ No standings available")
            
        # Get API stats
        print("\n3. API Usage Stats:")
        stats = client.get_request_stats()
        print(f"   Requests: {stats['requests_this_minute']}/{stats['rate_limit']}")
        print(f"   Remaining: {stats['remaining']}")
        
    else:
        print(f"   ❌ ERROR: {result.get('error', 'Unknown error')}")
        print(f"   Message: {result.get('message', '')}")
        print("\n   Please check:")
        print("   1. Is FOOTBALL_DATA_ORG_KEY set in .env file?")
        print("   2. Is the API key valid?")
        print("   3. Is internet connection working?")
    
    print("\n" + "-" * 50)
    print("Test complete!")


if __name__ == "__main__":
    test_api()
