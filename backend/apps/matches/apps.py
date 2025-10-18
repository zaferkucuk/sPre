"""
Django app configuration for matches application.
"""

from django.apps import AppConfig


class MatchesConfig(AppConfig):
    """
    Configuration class for the matches application.
    
    This app manages match data, predictions, and analysis.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.matches'
    verbose_name = 'Matches'
    
    def ready(self):
        """
        Import signal handlers when the app is ready.
        """
        import apps.matches.signals  # noqa
