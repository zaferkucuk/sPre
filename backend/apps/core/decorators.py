"""
Utility decorators for the application.

This module provides reusable decorators for common patterns
like error handling, logging, caching, and performance monitoring.
"""

import logging
import time
import functools
from typing import Callable, Any

from apps.core.exceptions import (
    SupabaseQueryError,
    DataFetchError,
)

logger = logging.getLogger(__name__)


def handle_supabase_errors(func: Callable) -> Callable:
    """
    Decorator to handle Supabase operation errors.
    
    Wraps function to catch and log Supabase exceptions,
    converting them to application-specific exceptions.
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function with error handling
        
    Example:
        >>> @handle_supabase_errors
        >>> def get_user(user_id):
        ...     return client.table('users').select('*').eq('id', user_id).execute()
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Log the error with full context
            logger.error(
                f"Supabase error in {func.__name__}: {str(e)}",
                extra={
                    'function': func.__name__,
                    'args': args,
                    'kwargs': kwargs,
                },
                exc_info=True
            )
            
            # Convert to application exception
            raise SupabaseQueryError(
                f"Database operation failed in {func.__name__}: {str(e)}"
            ) from e
    
    return wrapper


def handle_external_api_errors(func: Callable) -> Callable:
    """
    Decorator to handle external API call errors.
    
    Wraps function to catch and log external API exceptions,
    providing consistent error handling for data source operations.
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function with error handling
        
    Example:
        >>> @handle_external_api_errors
        >>> def fetch_match_data(match_id):
        ...     return requests.get(f'https://api.example.com/matches/{match_id}').json()
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(
                f"External API error in {func.__name__}: {str(e)}",
                extra={
                    'function': func.__name__,
                    'args': args,
                    'kwargs': kwargs,
                },
                exc_info=True
            )
            
            raise DataFetchError(
                f"Failed to fetch data in {func.__name__}: {str(e)}"
            ) from e
    
    return wrapper


def log_execution_time(func: Callable) -> Callable:
    """
    Decorator to log function execution time.
    
    Useful for performance monitoring and identifying slow operations.
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function with execution time logging
        
    Example:
        >>> @log_execution_time
        >>> def complex_calculation():
        ...     # Some time-consuming operation
        ...     pass
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            execution_time = time.time() - start_time
            logger.info(
                f"{func.__name__} executed in {execution_time:.3f} seconds",
                extra={
                    'function': func.__name__,
                    'execution_time': execution_time,
                }
            )
    
    return wrapper


def retry_on_failure(max_attempts: int = 3, delay: float = 1.0):
    """
    Decorator to retry function on failure.
    
    Useful for operations that may fail transiently,
    such as network requests or database operations.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Delay between retries in seconds
        
    Returns:
        Decorator function
        
    Example:
        >>> @retry_on_failure(max_attempts=3, delay=2.0)
        >>> def fetch_data():
        ...     return requests.get('https://api.example.com/data').json()
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt < max_attempts:
                        logger.warning(
                            f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {str(e)}. "
                            f"Retrying in {delay} seconds..."
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"All {max_attempts} attempts failed for {func.__name__}: {str(e)}"
                        )
            
            # If we get here, all attempts failed
            raise last_exception
        
        return wrapper
    
    return decorator


def cache_result(ttl_seconds: int = 300):
    """
    Decorator to cache function results.
    
    Simple in-memory cache with time-to-live.
    For production, consider using Redis or similar.
    
    Args:
        ttl_seconds: Time to live for cached results in seconds
        
    Returns:
        Decorator function
        
    Example:
        >>> @cache_result(ttl_seconds=600)
        >>> def get_sports():
        ...     return client.table('sports').select('*').execute()
    """
    cache = {}
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = (
                func.__name__,
                str(args),
                str(sorted(kwargs.items()))
            )
            
            # Check if result is in cache and not expired
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if time.time() - timestamp < ttl_seconds:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return result
            
            # Execute function and cache result
            logger.debug(f"Cache miss for {func.__name__}")
            result = func(*args, **kwargs)
            cache[cache_key] = (result, time.time())
            
            return result
        
        return wrapper
    
    return decorator


def validate_input(**validators):
    """
    Decorator to validate function inputs.
    
    Args:
        **validators: Keyword arguments where key is parameter name
                     and value is validation function
        
    Returns:
        Decorator function
        
    Example:
        >>> @validate_input(
        ...     user_id=lambda x: isinstance(x, int) and x > 0,
        ...     email=lambda x: '@' in x
        ... )
        >>> def create_user(user_id, email):
        ...     pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get function signature
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Validate each parameter
            for param_name, validator in validators.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    if not validator(value):
                        raise ValueError(
                            f"Invalid value for parameter '{param_name}': {value}"
                        )
            
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def require_auth(func: Callable) -> Callable:
    """
    Decorator to require authentication for a function.
    
    This is a placeholder that should be customized based on
    your authentication mechanism.
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function with authentication check
        
    Example:
        >>> @require_auth
        >>> def get_user_profile(user_id):
        ...     return client.table('profiles').select('*').eq('id', user_id).execute()
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # TODO: Implement actual authentication check
        # For now, this is a placeholder
        # In a real implementation, you would check for:
        # - Valid session token
        # - User permissions
        # - Token expiration
        
        # Example:
        # if not is_authenticated():
        #     raise UnauthorizedError("Authentication required")
        
        return func(*args, **kwargs)
    
    return wrapper
