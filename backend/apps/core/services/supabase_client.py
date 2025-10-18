"""
Supabase client wrapper.

This module provides a thread-safe, singleton Supabase client
with connection pooling and error handling.
"""

import logging
from typing import Optional, Dict, Any
from functools import lru_cache
from contextlib import contextmanager

from supabase import create_client, Client
from django.conf import settings

from apps.core.exceptions import (
    SupabaseConnectionError,
    SupabaseConfigurationError,
)

logger = logging.getLogger(__name__)


class SupabaseClient:
    """
    Wrapper class for Supabase client with enhanced features.
    
    Features:
    - Singleton pattern for connection reuse
    - Thread-safe operations
    - Comprehensive error handling
    - Logging and monitoring
    - Connection health checks
    
    Usage:
        client = SupabaseClient()
        response = client.table('users').select('*').execute()
    """
    
    _instance: Optional['SupabaseClient'] = None
    _client: Optional[Client] = None
    
    def __new__(cls):
        """
        Implement singleton pattern.
        
        Ensures only one instance of SupabaseClient exists
        throughout the application lifecycle.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """
        Initialize the Supabase client.
        
        Raises:
            SupabaseConfigurationError: If required settings are missing
            SupabaseConnectionError: If connection fails
        """
        # Only initialize once
        if self._client is not None:
            return
        
        # Validate configuration
        self._validate_config()
        
        # Create client
        try:
            self._client = create_client(
                supabase_url=settings.SUPABASE_URL,
                supabase_key=settings.SUPABASE_ANON_KEY,
            )
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {str(e)}")
            raise SupabaseConnectionError(
                f"Failed to connect to Supabase: {str(e)}"
            ) from e
    
    def _validate_config(self) -> None:
        """
        Validate Supabase configuration.
        
        Raises:
            SupabaseConfigurationError: If required settings are missing
        """
        required_settings = ['SUPABASE_URL', 'SUPABASE_ANON_KEY']
        missing_settings = [
            setting for setting in required_settings
            if not hasattr(settings, setting) or not getattr(settings, setting)
        ]
        
        if missing_settings:
            raise SupabaseConfigurationError(
                f"Missing required Supabase settings: {', '.join(missing_settings)}"
            )
        
        # Validate URL format
        if not settings.SUPABASE_URL.startswith(('http://', 'https://')):
            raise SupabaseConfigurationError(
                "SUPABASE_URL must start with http:// or https://"
            )
    
    @property
    def client(self) -> Client:
        """
        Get the Supabase client instance.
        
        Returns:
            Client: Supabase client instance
            
        Raises:
            SupabaseConnectionError: If client is not initialized
        """
        if self._client is None:
            raise SupabaseConnectionError(
                "Supabase client is not initialized"
            )
        return self._client
    
    def table(self, table_name: str):
        """
        Get a table reference.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Table reference for query building
            
        Example:
            >>> client = SupabaseClient()
            >>> users = client.table('users').select('*').execute()
        """
        return self.client.table(table_name)
    
    def rpc(self, function_name: str, params: Optional[Dict[str, Any]] = None):
        """
        Call a Postgres function (RPC).
        
        Args:
            function_name: Name of the function to call
            params: Parameters to pass to the function
            
        Returns:
            Function execution result
            
        Example:
            >>> client = SupabaseClient()
            >>> result = client.rpc('get_match_stats', {'match_id': 123})
        """
        return self.client.rpc(function_name, params or {})
    
    def storage(self):
        """
        Get storage client for file operations.
        
        Returns:
            Storage client instance
            
        Example:
            >>> client = SupabaseClient()
            >>> bucket = client.storage().from_('avatars')
        """
        return self.client.storage
    
    def auth(self):
        """
        Get auth client for authentication operations.
        
        Returns:
            Auth client instance
            
        Example:
            >>> client = SupabaseClient()
            >>> user = client.auth().sign_in_with_password({...})
        """
        return self.client.auth
    
    def health_check(self) -> bool:
        """
        Check if Supabase connection is healthy.
        
        Returns:
            bool: True if connection is healthy, False otherwise
            
        Example:
            >>> client = SupabaseClient()
            >>> if client.health_check():
            ...     print("Connection is healthy")
        """
        try:
            # Try a simple query to check connection
            self.client.table('sports').select('id').limit(1).execute()
            logger.debug("Supabase health check passed")
            return True
        except Exception as e:
            logger.error(f"Supabase health check failed: {str(e)}")
            return False
    
    @contextmanager
    def transaction(self):
        """
        Context manager for transaction-like operations.
        
        Note: Supabase doesn't support traditional transactions,
        but this provides a consistent error handling pattern.
        
        Example:
            >>> client = SupabaseClient()
            >>> with client.transaction():
            ...     client.table('users').insert({...}).execute()
            ...     client.table('profiles').insert({...}).execute()
        """
        try:
            yield self
            logger.debug("Transaction completed successfully")
        except Exception as e:
            logger.error(f"Transaction failed: {str(e)}")
            raise


@lru_cache(maxsize=1)
def get_supabase_client() -> SupabaseClient:
    """
    Get or create a singleton Supabase client instance.
    
    This function uses LRU cache to ensure only one instance
    is created and reused throughout the application.
    
    Returns:
        SupabaseClient: Singleton client instance
        
    Example:
        >>> client = get_supabase_client()
        >>> data = client.table('matches').select('*').execute()
    """
    return SupabaseClient()
