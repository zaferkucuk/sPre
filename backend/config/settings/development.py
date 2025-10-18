"""
Development settings for sPre project.

These settings are used during local development.
"""

from .base import *

# Debug mode enabled
DEBUG = True

# Allow all hosts in development
ALLOWED_HOSTS = ['*']

# Development database (SQLite for quick setup)
# You can switch to PostgreSQL by updating DATABASE_URL in .env
DATABASES = {
    'default': env.db(
        'DATABASE_URL',
        default='sqlite:///' + str(BASE_DIR / 'db.sqlite3')
    )
}

# CORS - Allow all origins in development
CORS_ALLOW_ALL_ORIGINS = True

# Add django-debug-toolbar for development
INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# Debug toolbar configuration
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

# Email backend for development (console output)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable password validation in development
AUTH_PASSWORD_VALIDATORS = []

# Cache configuration for development (local memory)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Static files - simpler configuration for development
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Logging - more verbose in development
LOGGING['root']['level'] = 'DEBUG'
LOGGING['loggers']['django']['level'] = 'DEBUG'

# Development-specific settings
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
