"""
Test script for Premier League fixtures API.

This script tests the Premier League API endpoints to ensure
they are working correctly.

Usage:
    python test_premier_league.py
"""

import requests
import json
from datetime import datetime
from typing import Dict, List


BASE_URL = "http://localhost:8000/api/matches"
HEADERS = {
    "Content-Type": "application/json"
}


def print_header(text: str):
    """Print formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_success(text: str):
    """Print success message."""
    print(f"✅ {text}")


def print_error(text: str):
    """Print error message."""
    print(f"❌ {text}")


def print_info(text: str):
    """Print info message."""
    print(f"ℹ️  {text}")


def test_fixtures_list():
    """Test getting fixtures list."""
    print_header("Test 1: Get Premier League Fixtures")
    
    try:
        response = requests.get(
            f"{BASE_URL}/premier-league/fixtures/",
            params={"limit": 10},
            headers=HEADERS
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Status Code: {response.status_code}")
            print_info(f"Found {data['count']} fixtures (Total available: {data['total_available']})")
            print_info(f"League: {data['league']['name']}")
            
            if data['data']:
                fixture = data['data'][0]
                print_info(f"Sample fixture: {fixture['home_team']['name']} vs {fixture['away_team']['name']}")
                print_info(f"Date: {fixture['match_date']}")
                print_info(f"Status: {fixture['status']}")
            
            return True
        else:
            print_error(f"Status Code: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False


def test_fixtures_filtered():
    """Test getting filtered fixtures."""
    print_header("Test 2: Get Upcoming Fixtures Only")
    
    try:
        response = requests.get(
            f"{BASE_URL}/premier-league/fixtures/",
            params={
                "upcoming": "true",
                "limit": 5
            },
            headers=HEADERS
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Status Code: {response.status_code}")
            print_info(f"Found {data['count']} upcoming fixtures")
            
            if data['data']:
                for idx, fixture in enumerate(data['data'][:3], 1):
                    print_info(
                        f"{idx}. {fixture['home_team']['name']} vs {fixture['away_team']['name']} "
                        f"({fixture['match_date']})"
                    )
            
            return True
        else:
            print_error(f"Status Code: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False


def test_fixtures_by_status():
    """Test getting fixtures by status."""
    print_header("Test 3: Get Scheduled Fixtures")
    
    try:
        response = requests.get(
            f"{BASE_URL}/premier-league/fixtures/",
            params={
                "status": "scheduled",
                "limit": 5
            },
            headers=HEADERS
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Status Code: {response.status_code}")
            print_info(f"Found {data['count']} scheduled fixtures")
            return True
        else:
            print_error(f"Status Code: {response.status_code}")
            return False
    
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False


def test_teams_list():
    """Test getting teams list."""
    print_header("Test 4: Get Premier League Teams")
    
    try:
        response = requests.get(
            f"{BASE_URL}/premier-league/teams/",
            headers=HEADERS
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Status Code: {response.status_code}")
            print_info(f"Found {data['count']} teams")
            
            if data['data']:
                print_info("Sample teams:")
                for idx, team in enumerate(data['data'][:5], 1):
                    print_info(f"  {idx}. {team['name']} ({team.get('code', 'N/A')})")
            
            return True
        else:
            print_error(f"Status Code: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False


def test_teams_search():
    """Test searching teams."""
    print_header("Test 5: Search Teams")
    
    try:
        response = requests.get(
            f"{BASE_URL}/premier-league/teams/",
            params={"search": "Manchester"},
            headers=HEADERS
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Status Code: {response.status_code}")
            print_info(f"Found {data['count']} teams matching 'Manchester'")
            
            if data['data']:
                for team in data['data']:
                    print_info(f"  - {team['name']}")
            
            return True
        else:
            print_error(f"Status Code: {response.status_code}")
            return False
    
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False


def test_statistics():
    """Test getting statistics."""
    print_header("Test 6: Get Premier League Statistics")
    
    try:
        response = requests.get(
            f"{BASE_URL}/premier-league/stats/",
            headers=HEADERS
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Status Code: {response.status_code}")
            
            stats = data['data']['statistics']
            print_info(f"Total Teams: {stats['total_teams']}")
            print_info(f"Total Matches: {stats['total_matches']}")
            print_info(f"Scheduled: {stats['scheduled_matches']}")
            print_info(f"Finished: {stats['finished_matches']}")
            print_info(f"Live: {stats['live_matches']}")
            
            return True
        else:
            print_error(f"Status Code: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False


def test_error_handling():
    """Test error handling."""
    print_header("Test 7: Error Handling")
    
    try:
        # Test invalid status
        response = requests.get(
            f"{BASE_URL}/premier-league/fixtures/",
            params={"status": "invalid_status"},
            headers=HEADERS
        )
        
        if response.status_code == 400:
            print_success("Invalid status handled correctly (400)")
            return True
        else:
            print_error(f"Expected 400, got {response.status_code}")
            return False
    
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("\n" + "🏴󠁧󠁢󠁥󠁮󠁧󠁿" * 20)
    print("  Premier League API Test Suite")
    print("🏴󠁧󠁢󠁥󠁮󠁧󠁿" * 20)
    
    print_info(f"Base URL: {BASE_URL}")
    print_info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run tests
    tests = [
        ("Fixtures List", test_fixtures_list),
        ("Filtered Fixtures", test_fixtures_filtered),
        ("Fixtures by Status", test_fixtures_by_status),
        ("Teams List", test_teams_list),
        ("Teams Search", test_teams_search),
        ("Statistics", test_statistics),
        ("Error Handling", test_error_handling),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Test '{test_name}' crashed: {str(e)}")
            results.append((test_name, False))
    
    # Print summary
    print_header("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    failed = len(results) - passed
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print_success("\nAll tests passed! 🎉")
    else:
        print_error(f"\n{failed} test(s) failed!")
    
    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
    except Exception as e:
        print_error(f"Test suite crashed: {str(e)}")
