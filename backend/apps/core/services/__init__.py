"""
Core services package.

This package contains service classes that handle business logic
and external integrations.
"""

from .supabase_client import get_supabase_client, SupabaseClient
from .supabase_service import SupabaseService

__all__ = [
    'get_supabase_client',
    'SupabaseClient',
    'SupabaseService',
]
