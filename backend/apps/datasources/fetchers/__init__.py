"""
Data fetchers package.

This package contains fetcher classes for external data sources.
"""

from .base_fetcher import BaseFetcher
from .football_api_fetcher import FootballAPIFetcher

__all__ = [
    'BaseFetcher',
    'FootballAPIFetcher',
]
