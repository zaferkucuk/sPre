"""
Custom exceptions for the application.

This module defines custom exception classes used throughout
the application for better error handling and reporting.
"""


class BaseAppException(Exception):
    """
    Base exception class for all application exceptions.
    
    All custom exceptions should inherit from this class
    to allow for centralized exception handling.
    """
    
    def __init__(self, message: str, code: str = None):
        """
        Initialize the exception.
        
        Args:
            message: Human-readable error message
            code: Optional error code for programmatic handling
        """
        self.message = message
        self.code = code or self.__class__.__name__
        super().__init__(self.message)
    
    def __str__(self):
        return f"[{self.code}] {self.message}"


# ==================== Supabase Exceptions ====================

class SupabaseException(BaseAppException):
    """
    Base exception for Supabase-related errors.
    """
    pass


class SupabaseConnectionError(SupabaseException):
    """
    Raised when connection to Supabase fails.
    
    Example:
        >>> raise SupabaseConnectionError("Failed to connect to database")
    """
    pass


class SupabaseConfigurationError(SupabaseException):
    """
    Raised when Supabase configuration is invalid or missing.
    
    Example:
        >>> raise SupabaseConfigurationError("SUPABASE_URL not configured")
    """
    pass


class SupabaseQueryError(SupabaseException):
    """
    Raised when a Supabase query fails.
    
    Example:
        >>> raise SupabaseQueryError("Failed to fetch users")
    """
    pass


class ResourceNotFoundError(SupabaseException):
    """
    Raised when a requested resource is not found in the database.
    
    Example:
        >>> raise ResourceNotFoundError("User with id 123 not found")
    """
    pass


# ==================== Data Source Exceptions ====================

class DataSourceException(BaseAppException):
    """
    Base exception for data source related errors.
    """
    pass


class DataFetchError(DataSourceException):
    """
    Raised when fetching data from external source fails.
    
    Example:
        >>> raise DataFetchError("Failed to fetch match data from API")
    """
    pass


class DataParsingError(DataSourceException):
    """
    Raised when parsing external data fails.
    
    Example:
        >>> raise DataParsingError("Invalid JSON format received")
    """
    pass


class RateLimitExceededError(DataSourceException):
    """
    Raised when API rate limit is exceeded.
    
    Example:
        >>> raise RateLimitExceededError("API rate limit exceeded, retry after 60s")
    """
    pass


# ==================== Validation Exceptions ====================

class ValidationException(BaseAppException):
    """
    Base exception for validation errors.
    """
    pass


class InvalidInputError(ValidationException):
    """
    Raised when user input is invalid.
    
    Example:
        >>> raise InvalidInputError("Confidence score must be between 0 and 1")
    """
    pass


class DuplicateResourceError(ValidationException):
    """
    Raised when attempting to create a duplicate resource.
    
    Example:
        >>> raise DuplicateResourceError("Team with this name already exists")
    """
    pass


# ==================== Authentication Exceptions ====================

class AuthenticationException(BaseAppException):
    """
    Base exception for authentication errors.
    """
    pass


class InvalidCredentialsError(AuthenticationException):
    """
    Raised when provided credentials are invalid.
    
    Example:
        >>> raise InvalidCredentialsError("Invalid email or password")
    """
    pass


class UnauthorizedError(AuthenticationException):
    """
    Raised when user lacks permission for the requested action.
    
    Example:
        >>> raise UnauthorizedError("You don't have permission to access this resource")
    """
    pass


class TokenExpiredError(AuthenticationException):
    """
    Raised when authentication token has expired.
    
    Example:
        >>> raise TokenExpiredError("Your session has expired, please login again")
    """
    pass


# ==================== Prediction Exceptions ====================

class PredictionException(BaseAppException):
    """
    Base exception for prediction related errors.
    """
    pass


class ModelNotFoundError(PredictionException):
    """
    Raised when prediction model is not found or not loaded.
    
    Example:
        >>> raise ModelNotFoundError("Football prediction model not found")
    """
    pass


class InsufficientDataError(PredictionException):
    """
    Raised when insufficient data is available for prediction.
    
    Example:
        >>> raise InsufficientDataError("Need at least 5 matches for prediction")
    """
    pass


class PredictionFailedError(PredictionException):
    """
    Raised when prediction calculation fails.
    
    Example:
        >>> raise PredictionFailedError("Failed to generate prediction: invalid input data")
    """
    pass
