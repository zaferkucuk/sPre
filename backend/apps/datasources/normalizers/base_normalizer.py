"""
Base data normalizer.

This module provides an abstract base class for data normalizers that
transform external API data into our database schema format.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime

from apps.core.exceptions import DataParsingError

logger = logging.getLogger(__name__)


class BaseNormalizer(ABC):
    """
    Abstract base class for data normalizers.
    
    Normalizers convert external API data formats into the schema
    used by our Supabase database.
    
    Usage:
        class MyNormalizer(BaseNormalizer):
            def normalize_league(self, raw_data):
                return {
                    'name': raw_data['league_name'],
                    'country': raw_data['country']
                }
    """
    
    def __init__(self, source_name: str):
        """
        Initialize the normalizer.
        
        Args:
            source_name: Name of the data source
        """
        self.source_name = source_name
        logger.info(f"Initialized {source_name} normalizer")
    
    @abstractmethod
    def normalize_league(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize league data.
        
        Args:
            raw_data: Raw league data from external API
            
        Returns:
            Normalized league dictionary for database
        """
        pass
    
    @abstractmethod
    def normalize_team(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize team data.
        
        Args:
            raw_data: Raw team data from external API
            
        Returns:
            Normalized team dictionary for database
        """
        pass
    
    @abstractmethod
    def normalize_match(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize match data.
        
        Args:
            raw_data: Raw match data from external API
            
        Returns:
            Normalized match dictionary for database
        """
        pass
    
    def safe_int(self, value: Any, default: Optional[int] = None) -> Optional[int]:
        """
        Safely convert value to integer.
        
        Args:
            value: Value to convert
            default: Default value if conversion fails
            
        Returns:
            Integer value or default
        """
        if value is None:
            return default
        
        try:
            return int(value)
        except (ValueError, TypeError):
            logger.warning(f"Failed to convert '{value}' to int")
            return default
    
    def safe_float(self, value: Any, default: Optional[float] = None) -> Optional[float]:
        """
        Safely convert value to float.
        
        Args:
            value: Value to convert
            default: Default value if conversion fails
            
        Returns:
            Float value or default
        """
        if value is None:
            return default
        
        try:
            return float(value)
        except (ValueError, TypeError):
            logger.warning(f"Failed to convert '{value}' to float")
            return default
    
    def safe_str(self, value: Any, default: str = '') -> str:
        """
        Safely convert value to string.
        
        Args:
            value: Value to convert
            default: Default value if None
            
        Returns:
            String value or default
        """
        if value is None:
            return default
        return str(value)
    
    def parse_datetime(
        self,
        date_str: Optional[str],
        default: Optional[datetime] = None
    ) -> Optional[datetime]:
        """
        Parse datetime string to datetime object.
        
        Args:
            date_str: Date string in ISO format
            default: Default value if parsing fails
            
        Returns:
            Datetime object or default
        """
        if not date_str:
            return default
        
        try:
            # Try ISO format with timezone
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            logger.warning(f"Failed to parse datetime: {date_str}")
            return default
    
    def validate_required_fields(
        self,
        data: Dict[str, Any],
        required_fields: List[str]
    ) -> None:
        """
        Validate that required fields are present.
        
        Args:
            data: Data dictionary to validate
            required_fields: List of required field names
            
        Raises:
            DataParsingError: If required fields are missing
        """
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        
        if missing_fields:
            raise DataParsingError(
                f"Missing required fields: {', '.join(missing_fields)}"
            )
