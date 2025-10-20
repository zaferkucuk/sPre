"""
API-Football client for fetching live sports data.

Features:
- Automatic rate limiting (100 requests/day)
- Response caching to minimize API calls
- Retry logic for failed requests
- Comprehensive error handling

Usage:
    client = APIFootballClient()
    standings = client.get_standings(league_id=39, season=2025)
"""

import requests
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class APIFootballClient:
    """
    Client for API-Football (v3).
    
    Handles all external API communication with rate limiting,
    caching, and error handling.
    """
    
    BASE_URL = settings.API_FOOTBALL_BASE_URL
    
    def __init__(self):
        """Initialize the API client with authentication."""
        self.api_key = settings.API_FOOTBALL_KEY
        self.headers = {
            'x-apisports-key': self.api_key,
            'x-rapidapi-host': 'v3.football.api-sports.io'
        }
        self.rate_limit = settings.API_FOOTBALL_RATE_LIMIT
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def _get_daily_request_count(self) -> int:
        """Get today's API request count from cache."""
        cache_key = f'api_football_count_{datetime.now().date()}'
        return cache.get(cache_key, 0)
    
    def _increment_request_count(self):
        """Increment today's request counter."""
        cache_key = f'api_football_count_{datetime.now().date()}'
        count = self._get_daily_request_count()
        # Cache expires at midnight
        seconds_until_midnight = (
            datetime.combine(datetime.now().date() + timedelta(days=1), datetime.min.time()) - 
            datetime.now()
        ).seconds
        cache.set(cache_key, count + 1, timeout=seconds_until_midnight)
        
        logger.info(f"API request count: {count + 1}/{self.rate_limit}")
    
    def _check_rate_limit(self):
        """Check if we've exceeded the daily rate limit."""
        current_count = self._get_daily_request_count()
        if current_count >= self.rate_limit:
            raise Exception(
                f"Daily API rate limit reached ({self.rate_limit} requests). "
                f"Resets at midnight."
            )
    
    def _make_request(
        self,
        endpoint: str,
        params: Dict[str, Any],
        cache_timeout: int = 3600,
        bypass_cache: bool = False
    ) -> Optional[Dict]:
        """
        Make HTTP request to API-Football with caching and error handling.
        
        Args:
            endpoint: API endpoint (e.g., 'standings', 'fixtures')
            params: Query parameters
            cache_timeout: Cache duration in seconds (default: 1 hour)
            bypass_cache: Force fresh API call, ignoring cache
        
        Returns:
            JSON response dict or None if error
        
        Raises:
            Exception: If rate limit exceeded or critical error
        """
        # Generate unique cache key
        cache_key = f"api_football:{endpoint}:{str(sorted(params.items()))}"
        
        # Try cache first (unless bypassed)
        if not bypass_cache:
            cached_data = cache.get(cache_key)
            if cached_data:
                logger.info(f"Cache HIT for {endpoint} - {params}")
                return cached_data
        
        # Check rate limit before making request
        self._check_rate_limit()
        
        # Make API request
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            logger.info(f"API request: {endpoint} - {params}")
            
            response = self.session.get(
                url,
                params=params,
                timeout=15
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Check API response structure
            if 'response' not in data:
                logger.error(f"Invalid API response structure: {data}")
                return None
            
            # Check for API errors
            if 'errors' in data and data['errors']:
                logger.error(f"API returned errors: {data['errors']}")
                return None
            
            # Increment request counter
            self._increment_request_count()
            
            # Cache successful response
            cache.set(cache_key, data, timeout=cache_timeout)
            
            logger.info(f"API request successful. Results: {len(data.get('response', []))}")
            return data
            
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout for {endpoint}")
            return None
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error for {endpoint}: {e}")
            if e.response.status_code == 429:
                logger.critical("Rate limit exceeded by API provider!")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {endpoint}: {e}")
            return None
            
        except Exception as e:
            logger.error(f"Unexpected error for {endpoint}: {e}")
            return None
    
    def get_standings(
        self,
        league_id: int,
        season: int
    ) -> List[Dict]:
        """
        Get league standings (puan durumu).
        
        Args:
            league_id: API-Football league ID
            season: Year (e.g., 2025)
        
        Returns:
            List of team standings with statistics
        """
        data = self._make_request(
            'standings',
            params={'league': league_id, 'season': season},
            cache_timeout=3600  # 1 hour
        )
        
        if not data or not data.get('response'):
            return []
        
        try:
            return data['response'][0]['league']['standings'][0]
        except (IndexError, KeyError, TypeError) as e:
            logger.error(f"Error parsing standings: {e}")
            return []
    
    def get_fixtures(
        self,
        league_id: int,
        from_date: str,
        to_date: str,
        season: Optional[int] = None
    ) -> List[Dict]:
        """
        Get fixtures in a date range.
        
        Args:
            league_id: API-Football league ID
            from_date: Start date (ISO format: YYYY-MM-DD)
            to_date: End date (ISO format: YYYY-MM-DD)
            season: Optional season filter
        
        Returns:
            List of fixtures
        """
        params = {
            'league': league_id,
            'from': from_date,
            'to': to_date
        }
        
        if season:
            params['season'] = season
        
        data = self._make_request(
            'fixtures',
            params=params,
            cache_timeout=7200  # 2 hours
        )
        
        if not data or not data.get('response'):
            return []
        
        return data['response']
    
    def get_fixture_by_id(
        self,
        fixture_id: int
    ) -> Optional[Dict]:
        """
        Get detailed information for a specific fixture.
        
        Args:
            fixture_id: API-Football fixture ID
        
        Returns:
            Fixture details or None
        """
        data = self._make_request(
            'fixtures',
            params={'id': fixture_id},
            cache_timeout=1800  # 30 minutes
        )
        
        if not data or not data.get('response'):
            return None
        
        return data['response'][0] if data['response'] else None
    
    def get_team_statistics(
        self,
        team_id: int,
        league_id: int,
        season: int
    ) -> Optional[Dict]:
        """
        Get detailed team statistics for a season.
        
        Args:
            team_id: API-Football team ID
            league_id: API-Football league ID
            season: Year (e.g., 2025)
        
        Returns:
            Team statistics dict or None
        """
        data = self._make_request(
            'teams/statistics',
            params={
                'team': team_id,
                'league': league_id,
                'season': season
            },
            cache_timeout=86400  # 24 hours
        )
        
        if not data or not data.get('response'):
            return None
        
        return data['response']
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test API connection and check status.
        
        Returns:
            Dict with connection status and account info
        """
        try:
            url = f"{self.BASE_URL}/status"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'success': True,
                'data': data,
                'message': 'API connection successful'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'API connection failed'
            }
    
    def get_request_stats(self) -> Dict[str, Any]:
        """
        Get current API usage statistics.
        
        Returns:
            Dict with request count and limit info
        """
        current_count = self._get_daily_request_count()
        
        return {
            'requests_today': current_count,
            'rate_limit': self.rate_limit,
            'remaining': self.rate_limit - current_count,
            'percentage_used': round((current_count / self.rate_limit) * 100, 2),
            'date': datetime.now().date().isoformat()
        }
