"""
Services for datasources application.

This module contains business logic for fetching data from external sources.
"""

import os
import requests
from typing import Dict, Any, Optional
from django.conf import settings
from .models import DataSource, SyncLog


class BaseDataSourceService:
    """
    Base class for data source services.
    
    Provides common functionality for fetching data from external APIs.
    """
    
    def __init__(self, data_source: DataSource):
        """
        Initialize service with data source.
        
        Args:
            data_source (DataSource): Data source instance
        """
        self.data_source = data_source
        self.api_url = data_source.api_url
        self.api_key = os.environ.get(data_source.api_key_name, '')
    
    def get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers for API requests.
        
        Returns:
            Dict[str, str]: HTTP headers
        """
        return {
            'Content-Type': 'application/json',
            'X-API-Key': self.api_key,
        }
    
    def make_request(
        self,
        endpoint: str,
        method: str = 'GET',
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to external API.
        
        Args:
            endpoint (str): API endpoint
            method (str): HTTP method
            params (dict): Query parameters
            data (dict): Request body data
        
        Returns:
            dict: API response data
        
        Raises:
            requests.RequestException: If request fails
        """
        url = f"{self.api_url}/{endpoint}"
        headers = self.get_headers()
        
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=data,
            timeout=30
        )
        
        response.raise_for_status()
        return response.json()
    
    def fetch_data(self) -> Dict[str, Any]:
        """
        Fetch data from external source.
        
        This method should be implemented by subclasses.
        
        Returns:
            dict: Fetched data
        
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError('Subclasses must implement fetch_data()')


class FootballAPIService(BaseDataSourceService):
    """
    Service for fetching football data from external API.
    
    Example API: API-Football (https://www.api-football.com/)
    """
    
    def fetch_matches(self, league_id: int, season: str) -> Dict[str, Any]:
        """
        Fetch matches for a specific league and season.
        
        Args:
            league_id (int): League ID
            season (str): Season (e.g., '2024')
        
        Returns:
            dict: Match data
        """
        return self.make_request(
            endpoint='fixtures',
            params={'league': league_id, 'season': season}
        )
    
    def fetch_teams(self, league_id: int, season: str) -> Dict[str, Any]:
        """
        Fetch teams for a specific league and season.
        
        Args:
            league_id (int): League ID
            season (str): Season
        
        Returns:
            dict: Team data
        """
        return self.make_request(
            endpoint='teams',
            params={'league': league_id, 'season': season}
        )
    
    def fetch_data(self) -> Dict[str, Any]:
        """
        Fetch all necessary data.
        
        Returns:
            dict: Combined data
        """
        # TODO: Implement actual data fetching logic
        return {
            'matches': [],
            'teams': [],
            'leagues': []
        }


class OddsAPIService(BaseDataSourceService):
    """
    Service for fetching betting odds from external API.
    
    Example API: The Odds API (https://the-odds-api.com/)
    """
    
    def fetch_odds(self, sport: str) -> Dict[str, Any]:
        """
        Fetch betting odds for a specific sport.
        
        Args:
            sport (str): Sport key (e.g., 'soccer_epl')
        
        Returns:
            dict: Odds data
        """
        return self.make_request(
            endpoint=f'sports/{sport}/odds',
            params={'regions': 'eu', 'markets': 'h2h'}
        )
    
    def fetch_data(self) -> Dict[str, Any]:
        """
        Fetch all necessary odds data.
        
        Returns:
            dict: Odds data
        """
        # TODO: Implement actual odds fetching logic
        return {
            'odds': []
        }


def get_service_for_source(data_source: DataSource) -> BaseDataSourceService:
    """
    Get appropriate service class for data source.
    
    Args:
        data_source (DataSource): Data source instance
    
    Returns:
        BaseDataSourceService: Service instance
    """
    service_map = {
        DataSource.SourceType.FOOTBALL_API: FootballAPIService,
        DataSource.SourceType.ODDS_API: OddsAPIService,
    }
    
    service_class = service_map.get(
        data_source.source_type,
        BaseDataSourceService
    )
    
    return service_class(data_source)
