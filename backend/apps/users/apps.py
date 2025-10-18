"""
Django app configuration for users application.
"""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    Configuration class for the users application.
    
    This app manages user accounts, authentication, and user profiles.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    verbose_name = 'Users'
    
    def ready(self):
        """
        Import signal handlers when the app is ready.
        """
        import apps.users.signals  # noqa
