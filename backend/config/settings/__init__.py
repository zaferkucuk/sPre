"""
Django settings package initialization.

By default, use development settings.
Set DJANGO_SETTINGS_MODULE environment variable to use different settings.
"""

import os

# Default to development settings
ENVIRONMENT = os.environ.get('DJANGO_ENVIRONMENT', 'development')

if ENVIRONMENT == 'production':
    from .production import *
elif ENVIRONMENT == 'development':
    from .development import *
else:
    from .base import *
