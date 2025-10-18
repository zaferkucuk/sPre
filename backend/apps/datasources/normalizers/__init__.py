"""
Data normalizers package.

This package contains normalizer classes that transform external API data
into the format expected by our Supabase database.
"""

from .base_normalizer import BaseNormalizer
from .football_normalizer import FootballNormalizer

__all__ = [
    'BaseNormalizer',
    'FootballNormalizer',
]
