"""
Django settings for sPre project.

This module contains base settings that are common across all environments.
Environment-specific settings are defined in development.py and production.py.
"""

import os
from pathlib import Path
from datetime import timedelta
import environ

# Initialize environment variables
env = environ.Env(
    DEBUG=(bool, False)
)

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Read .env file
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', default='django-insecure-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_extensions',
    
    # Local apps
    'apps.core',  # Core utilities and services
    'apps.users',
    'apps.matches',
    'apps.analytics',
    'apps.datasources',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': env.db('DATABASE_URL', default='sqlite:///db.sqlite3')
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Custom User Model
AUTH_USER_MODEL = 'users.User'


# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    ),
    'DATETIME_FORMAT': '%Y-%m-%dT%H:%M:%S.%fZ',
    'DATE_FORMAT': '%Y-%m-%d',
}


# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=env.int('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', default=30)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=env.int('JWT_REFRESH_TOKEN_EXPIRE_DAYS', default=7)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': env('JWT_ALGORITHM', default='HS256'),
    'SIGNING_KEY': env('JWT_SECRET_KEY', default=SECRET_KEY),
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}


# CORS Settings
CORS_ALLOWED_ORIGINS = env.list(
    'CORS_ALLOWED_ORIGINS',
    default=['http://localhost:3000', 'http://127.0.0.1:3000']
)
CORS_ALLOW_CREDENTIALS = True


# Supabase Configuration
SUPABASE_URL = env('SUPABASE_URL', default='')
SUPABASE_ANON_KEY = env('SUPABASE_ANON_KEY', default='')
SUPABASE_SERVICE_KEY = env('SUPABASE_SERVICE_KEY', default='')


# ========================================
# API-FOOTBALL CONFIGURATION
# ========================================
API_FOOTBALL_KEY = env('API_FOOTBALL_KEY', default='35fefc7e2a57cd2b9de7cfc330c0177b')
API_FOOTBALL_BASE_URL = 'https://v3.football.api-sports.io'
API_FOOTBALL_RATE_LIMIT = 100  # requests per day (free tier)

# Supported Leagues Configuration
SUPPORTED_LEAGUES = {
    'tier_1': [
        # xG supported leagues (Understat coverage)
        {
            'name': 'Premier League',
            'country': 'England',
            'api_id': 39,
            'understat_slug': 'EPL',
            'has_xg': True
        },
        {
            'name': 'La Liga',
            'country': 'Spain',
            'api_id': 140,
            'understat_slug': 'La_liga',
            'has_xg': True
        },
        {
            'name': 'Serie A',
            'country': 'Italy',
            'api_id': 135,
            'understat_slug': 'Serie_A',
            'has_xg': True
        },
        {
            'name': 'Bundesliga',
            'country': 'Germany',
            'api_id': 78,
            'understat_slug': 'Bundesliga',
            'has_xg': True
        },
        {
            'name': 'Ligue 1',
            'country': 'France',
            'api_id': 61,
            'understat_slug': 'Ligue_1',
            'has_xg': True
        },
    ],
    'tier_2': [
        # Standard leagues (no xG)
        {
            'name': 'Eredivisie',
            'country': 'Netherlands',
            'api_id': 88,
            'has_xg': False
        },
        {
            'name': 'Primeira Liga',
            'country': 'Portugal',
            'api_id': 94,
            'has_xg': False
        },
        {
            'name': 'Pro League',
            'country': 'Belgium',
            'api_id': 144,
            'has_xg': False
        },
        {
            'name': 'First League',
            'country': 'Czech Republic',
            'api_id': 345,
            'has_xg': False
        },
        {
            'name': 'Süper Lig',
            'country': 'Turkey',
            'api_id': 203,
            'has_xg': False
        },
    ]
}

# Cache configuration for API responses
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'api_cache_table',
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

# Data sync configuration
DATA_SYNC_CONFIG = {
    'daily_sync_time': '03:00',  # 3 AM
    'weekly_xg_sync_day': 0,  # Sunday (0=Sunday, 6=Saturday)
    'weekly_xg_sync_time': '23:00',  # 11 PM
    'fixtures_lookahead_days': 7,
    'results_lookback_days': 1,
}

# ========================================
# END API-FOOTBALL CONFIGURATION
# ========================================


# External API Keys (legacy, keeping for backwards compatibility)
FOOTBALL_API_KEY = env('FOOTBALL_API_KEY', default=API_FOOTBALL_KEY)
ODDS_API_KEY = env('ODDS_API_KEY', default='')


# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django_error.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': env('LOG_LEVEL', default='INFO'),
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file', 'error_file'],
            'level': env('LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'apps.matches.services': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Create logs directory if it doesn't exist
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)
