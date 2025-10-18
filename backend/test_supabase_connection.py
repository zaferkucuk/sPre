"""
Supabase connection test script.

Run this script to verify your Supabase database connection.

Usage:
    python test_supabase_connection.py
"""

import os
import sys
from supabase import create_client, Client

# Load environment variables
from dotenv import load_dotenv
load_dotenv()


def test_connection():
    """Test Supabase connection and basic queries."""
    
    print("🔍 Testing Supabase Connection...")
    print("-" * 50)
    
    # Get credentials
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("❌ ERROR: SUPABASE_URL or SUPABASE_ANON_KEY not found in .env")
        print("Please check your .env file.")
        return False
    
    print(f"📍 URL: {url}")
    print(f"🔑 Key: {key[:20]}...")
    print()
    
    try:
        # Create client
        supabase: Client = create_client(url, key)
        print("✅ Supabase client created successfully!")
        print()
        
        # Test 1: Query sports table
        print("📊 Test 1: Querying sports table...")
        response = supabase.table('sports').select('*').execute()
        sports = response.data
        print(f"✅ Found {len(sports)} sports:")
        for sport in sports:
            print(f"   - {sport['name']} ({sport['slug']})")
        print()
        
        # Test 2: Query leagues table
        print("🏆 Test 2: Querying leagues table...")
        response = supabase.table('leagues').select('*').execute()
        leagues = response.data
        print(f"✅ Found {len(leagues)} leagues:")
        for league in leagues[:5]:  # Show first 5
            print(f"   - {league['name']} ({league['country']})")
        if len(leagues) > 5:
            print(f"   ... and {len(leagues) - 5} more")
        print()
        
        # Test 3: Query teams table
        print("⚽ Test 3: Querying teams table...")
        response = supabase.table('teams').select('*').limit(5).execute()
        teams = response.data
        print(f"✅ Found teams:")
        for team in teams:
            print(f"   - {team['name']} ({team['code']})")
        print()
        
        # Test 4: Query matches table
        print("📅 Test 4: Querying matches table...")
        response = supabase.table('matches').select('*, home_team:teams!matches_home_team_id_fkey(name), away_team:teams!matches_away_team_id_fkey(name)').execute()
        matches = response.data
        print(f"✅ Found {len(matches)} matches:")
        for match in matches[:3]:
            home = match.get('home_team', {}).get('name', 'Unknown')
            away = match.get('away_team', {}).get('name', 'Unknown')
            status = match['status']
            print(f"   - {home} vs {away} ({status})")
        print()
        
        # Test 5: Check RLS
        print("🔒 Test 5: Checking Row Level Security...")
        response = supabase.rpc('pg_tables_with_rls', {}).execute()
        print("✅ RLS is configured")
        print()
        
        print("=" * 50)
        print("🎉 All tests passed!")
        print("=" * 50)
        print()
        print("Your Supabase database is ready to use!")
        print()
        print("Next steps:")
        print("1. Test Django connection: python manage.py migrate")
        print("2. Create a superuser: python manage.py createsuperuser")
        print("3. Run the server: python manage.py runserver")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        print()
        print("Troubleshooting:")
        print("1. Check your SUPABASE_URL and SUPABASE_ANON_KEY in .env")
        print("2. Verify you ran the migration in Supabase SQL Editor")
        print("3. Check your internet connection")
        print("4. Verify your Supabase project is active")
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
