"""
Core application configuration.
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """
    Configuration class for the core application.
    
    This app provides core utilities, services, and helpers
    that are used across the entire project.
    """
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    verbose_name = 'Core'
    
    def ready(self):
        """
        Perform initialization when the app is ready.
        
        This method is called when Django starts up.
        Use it to register signals or perform other startup tasks.
        """
        # Import signal handlers here if needed
        pass
