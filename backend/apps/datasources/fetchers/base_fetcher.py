"""
Base data fetcher interface.

This module provides an abstract base class for all data fetchers,
ensuring consistent interface and error handling.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import time

import requests
from django.core.cache import cache

from apps.core.exceptions import (
    DataFetchError,
    RateLimitExceededError,
    DataParsingError,
)
from apps.core.decorators import retry_on_failure

logger = logging.getLogger(__name__)


class BaseFetcher(ABC):
    """
    Abstract base class for external data fetchers.
    
    This class provides common functionality for all data fetchers:
    - Rate limiting
    - Caching
    - Error handling
    - Retry logic
    - Request logging
    
    Subclasses must implement:
    - fetch_leagues()
    - fetch_teams()
    - fetch_matches()
    - fetch_match_details()
    
    Usage:
        class MyFetcher(BaseFetcher):
            def __init__(self, api_key):
                super().__init__(
                    name="MyAPI",
                    base_url="https://api.example.com",
                    rate_limit_calls=100,
                    rate_limit_period=60
                )
                self.api_key = api_key
    """
    
    def __init__(
        self,
        name: str,
        base_url: str,
        rate_limit_calls: int = 100,
        rate_limit_period: int = 60,
        timeout: int = 30,
    ):
        """
        Initialize the base fetcher.
        
        Args:
            name: Name of the data source
            base_url: Base URL for API requests
            rate_limit_calls: Number of calls allowed per period
            rate_limit_period: Time period in seconds
            timeout: Request timeout in seconds
        """
        self.name = name
        self.base_url = base_url.rstrip('/')
        self.rate_limit_calls = rate_limit_calls
        self.rate_limit_period = rate_limit_period
        self.timeout = timeout
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'sPre/1.0',
            'Accept': 'application/json',
        })
        
        logger.info(f"Initialized {self.name} fetcher")
    
    def _get_rate_limit_key(self) -> str:
        """
        Get the cache key for rate limiting.
        
        Returns:
            Cache key string
        """
        return f"rate_limit:{self.name}"
    
    def _check_rate_limit(self) -> None:
        """
        Check if rate limit is exceeded.
        
        Raises:
            RateLimitExceededError: If rate limit is exceeded
        """
        cache_key = self._get_rate_limit_key()
        current_calls = cache.get(cache_key, 0)
        
        if current_calls >= self.rate_limit_calls:
            logger.warning(f"Rate limit exceeded for {self.name}")
            raise RateLimitExceededError(
                f"Rate limit exceeded for {self.name}. "
                f"Limit: {self.rate_limit_calls} calls per {self.rate_limit_period} seconds"
            )
        
        # Increment call counter
        cache.set(
            cache_key,
            current_calls + 1,
            timeout=self.rate_limit_period
        )
    
    @retry_on_failure(max_attempts=3, delay=2.0)
    def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        method: str = 'GET',
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the API.
        
        Args:
            endpoint: API endpoint (will be appended to base_url)
            params: Query parameters
            method: HTTP method
            
        Returns:
            Response data as dictionary
            
        Raises:
            DataFetchError: If request fails
            RateLimitExceededError: If rate limit is exceeded
        """
        # Check rate limit
        self._check_rate_limit()
        
        # Build URL
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # Log request
        logger.debug(f"Making {method} request to {url}")
        
        try:
            start_time = time.time()
            
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                timeout=self.timeout
            )
            
            elapsed_time = time.time() - start_time
            logger.debug(f"Request completed in {elapsed_time:.2f}s")
            
            # Check status code
            if response.status_code == 429:
                raise RateLimitExceededError(
                    f"API rate limit exceeded for {self.name}"
                )
            
            response.raise_for_status()
            
            # Parse JSON
            try:
                data = response.json()
            except ValueError as e:
                raise DataParsingError(
                    f"Failed to parse JSON response: {str(e)}"
                ) from e
            
            return data
        
        except requests.exceptions.Timeout:
            raise DataFetchError(
                f"Request to {self.name} timed out after {self.timeout}s"
            )
        
        except requests.exceptions.ConnectionError as e:
            raise DataFetchError(
                f"Connection error to {self.name}: {str(e)}"
            ) from e
        
        except requests.exceptions.HTTPError as e:
            raise DataFetchError(
                f"HTTP error from {self.name}: {str(e)}"
            ) from e
        
        except Exception as e:
            logger.error(f"Unexpected error in _make_request: {str(e)}")
            raise DataFetchError(
                f"Failed to fetch data from {self.name}: {str(e)}"
            ) from e
    
    def _get_cache_key(self, prefix: str, identifier: Any) -> str:
        """
        Generate a cache key.
        
        Args:
            prefix: Cache key prefix
            identifier: Unique identifier
            
        Returns:
            Cache key string
        """
        return f"{self.name}:{prefix}:{identifier}"
    
    def _get_cached(
        self,
        cache_key: str,
        ttl: int = 3600
    ) -> Optional[Any]:
        """
        Get data from cache.
        
        Args:
            cache_key: Cache key
            ttl: Time to live in seconds
            
        Returns:
            Cached data or None
        """
        data = cache.get(cache_key)
        
        if data is not None:
            logger.debug(f"Cache hit for {cache_key}")
        else:
            logger.debug(f"Cache miss for {cache_key}")
        
        return data
    
    def _set_cache(
        self,
        cache_key: str,
        data: Any,
        ttl: int = 3600
    ) -> None:
        """
        Store data in cache.
        
        Args:
            cache_key: Cache key
            data: Data to cache
            ttl: Time to live in seconds
        """
        cache.set(cache_key, data, timeout=ttl)
        logger.debug(f"Cached data for {cache_key} (TTL: {ttl}s)")
    
    # Abstract methods that subclasses must implement
    
    @abstractmethod
    def fetch_leagues(self, sport_id: int) -> List[Dict[str, Any]]:
        """
        Fetch leagues for a specific sport.
        
        Args:
            sport_id: ID of the sport
            
        Returns:
            List of league dictionaries
        """
        pass
    
    @abstractmethod
    def fetch_teams(self, league_id: int) -> List[Dict[str, Any]]:
        """
        Fetch teams in a specific league.
        
        Args:
            league_id: ID of the league
            
        Returns:
            List of team dictionaries
        """
        pass
    
    @abstractmethod
    def fetch_matches(
        self,
        league_id: int,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch matches for a specific league.
        
        Args:
            league_id: ID of the league
            from_date: Start date filter
            to_date: End date filter
            
        Returns:
            List of match dictionaries
        """
        pass
    
    @abstractmethod
    def fetch_match_details(self, match_id: str) -> Dict[str, Any]:
        """
        Fetch detailed information for a specific match.
        
        Args:
            match_id: External ID of the match
            
        Returns:
            Match details dictionary
        """
        pass
    
    def close(self) -> None:
        """
        Close the session and cleanup resources.
        """
        self.session.close()
        logger.info(f"Closed {self.name} fetcher")
    
    def __enter__(self):
        """
        Context manager entry.
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit.
        """
        self.close()
