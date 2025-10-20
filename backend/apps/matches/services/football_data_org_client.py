"""
Football-Data.org API Client

Free access to Premier League, La Liga, Bundesliga, Serie A, Ligue 1.
Rate limit: 10 requests/minute (free tier).
Documentation: https://www.football-data.org/documentation/api
"""

import requests
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class FootballDataOrgClient:
    """
    Client for Football-Data.org API (v4).
    
    Handles API communication with rate limiting and caching.
    """
    
    BASE_URL = settings.FOOTBALL_DATA_ORG_URL
    
    # Competition IDs (Free tier)
    COMPETITIONS = {
        'Premier League': 'PL',
        'La Liga': 'PD',
        'Bundesliga': 'BL1',
        'Serie A': 'SA',
        'Ligue 1': 'FL1',
        'Eredivisie': 'DED',
        'Primeira Liga': 'PPL',
        'Championship': 'ELC',
        'European Championship': 'EC',
        'Champions League': 'CL',
        'Copa Libertadores': 'CLI',
        'World Cup': 'WC'
    }
    
    def __init__(self):
        """Initialize the API client."""
        self.api_key = settings.FOOTBALL_DATA_ORG_KEY
        self.headers = {
            'X-Auth-Token': self.api_key
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Rate limiting (10 req/min free tier)
        self.rate_limit = 10
        self.rate_window = 60  # seconds
    
    def _get_request_count(self) -> int:
        """Get current minute's request count."""
        cache_key = f'fdo_count_{datetime.now().minute}'
        return cache.get(cache_key, 0)
    
    def _increment_request_count(self):
        """Increment current minute's request counter."""
        current_minute = datetime.now().minute
        cache_key = f'fdo_count_{current_minute}'
        count = self._get_request_count()
        cache.set(cache_key, count + 1, timeout=60)
        
        logger.info(f"API request count: {count + 1}/{self.rate_limit}")
    
    def _check_rate_limit(self):
        """Check if rate limit exceeded."""
        current_count = self._get_request_count()
        if current_count >= self.rate_limit:
            raise Exception(
                f"Rate limit reached ({self.rate_limit} requests/minute). "
                f"Please wait a moment."
            )
    
    def _make_request(
        self,
        endpoint: str,
        params: Dict[str, Any] = None,
        cache_timeout: int = 3600
    ) -> Optional[Dict]:
        """
        Make HTTP request to Football-Data.org API.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            cache_timeout: Cache duration in seconds
        
        Returns:
            JSON response or None
        """
        # Generate cache key
        cache_key = f"fdo:{endpoint}:{str(sorted((params or {}).items()))}"
        
        # Try cache first
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info(f"Cache HIT: {endpoint}")
            return cached_data
        
        # Check rate limit
        self._check_rate_limit()
        
        # Make request
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            logger.info(f"API request: {endpoint}")
            
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            # Increment counter
            self._increment_request_count()
            
            # Cache response
            cache.set(cache_key, data, timeout=cache_timeout)
            
            logger.info(f"API request successful: {endpoint}")
            return data
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                logger.error("Rate limit exceeded!")
            else:
                logger.error(f"HTTP error: {e}")
            return None
            
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return None
    
    def get_competition_by_name(self, name: str) -> Optional[str]:
        """Get competition code by name."""
        return self.COMPETITIONS.get(name)
    
    def get_standings(self, competition_code: str, season: Optional[int] = None) -> List[Dict]:
        """
        Get league standings.
        
        Args:
            competition_code: Competition code (e.g., 'PL' for Premier League)
            season: Year (optional, defaults to current season)
        
        Returns:
            List of team standings
        """
        endpoint = f"competitions/{competition_code}/standings"
        params = {}
        if season:
            params['season'] = season
        
        data = self._make_request(endpoint, params, cache_timeout=3600)
        
        if not data or 'standings' not in data:
            return []
        
        # Return TOTAL standings (not HOME/AWAY)
        standings_list = data['standings']
        for standing in standings_list:
            if standing['type'] == 'TOTAL':
                return standing['table']
        
        return []
    
    def get_matches(
        self,
        competition_code: str,
        season: Optional[int] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict]:
        """
        Get matches for a competition.
        
        Args:
            competition_code: Competition code
            season: Year
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            status: Match status (SCHEDULED, LIVE, FINISHED, etc.)
        
        Returns:
            List of matches
        """
        endpoint = f"competitions/{competition_code}/matches"
        params = {}
        
        if season:
            params['season'] = season
        if date_from:
            params['dateFrom'] = date_from
        if date_to:
            params['dateTo'] = date_to
        if status:
            params['status'] = status
        
        data = self._make_request(endpoint, params, cache_timeout=1800)
        
        if not data or 'matches' not in data:
            return []
        
        return data['matches']
    
    def get_team(self, team_id: int) -> Optional[Dict]:
        """Get team details."""
        endpoint = f"teams/{team_id}"
        return self._make_request(endpoint, cache_timeout=86400)
    
    def test_connection(self) -> Dict[str, Any]:
        """Test API connection."""
        try:
            data = self._make_request('competitions/PL', cache_timeout=60)
            
            if data:
                return {
                    'success': True,
                    'message': 'API connection successful',
                    'data': data
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to fetch data'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'API connection failed'
            }
    
    def get_request_stats(self) -> Dict[str, Any]:
        """Get current API usage statistics."""
        current_count = self._get_request_count()
        
        return {
            'requests_this_minute': current_count,
            'rate_limit': self.rate_limit,
            'remaining': self.rate_limit - current_count,
            'percentage_used': round((current_count / self.rate_limit) * 100, 2)
        }
