"""
Django app configuration for analytics application.
"""

from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    """
    Configuration class for the analytics application.
    
    This app manages data analysis, statistics, and ML models.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.analytics'
    verbose_name = 'Analytics'
