"""
Django settings for Railway deployment.
Extends the base settings with Railway-specific configurations.
"""
from .settings import *
import dj_database_url

# ============================================
# RAILWAY-SPECIFIC CONFIGURATION
# ============================================

# Support DATABASE_URL from Railway
DATABASE_URL = config('DATABASE_URL', default=None)

if DATABASE_URL:
    # Use Railway's PostgreSQL database URL
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }

# Railway provides RAILWAY_ENVIRONMENT_NAME
IS_RAILWAY = config('RAILWAY_ENVIRONMENT_NAME', default=None) is not None

if IS_RAILWAY:
    # Disable file-based logging on Railway (ephemeral filesystem)
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'simple': {
                'format': '{levelname} {asctime} {message}',
                'style': '{',
            },
        },
        'handlers': {
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'level': 'INFO',
            },
            'django.request': {
                'handlers': ['console'],
                'level': 'ERROR',
                'propagate': False,
            },
        },
    }

# Redis caching (recommended on Railway)
if config('RAILWAY_REDIS_URL', default=None):
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': config('RAILWAY_REDIS_URL'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'PARSER_KWARGS': {'encoding': 'utf8'},
                'POOL_KWARGS': {
                    'max_connections': 50,
                    'retry_on_timeout': True,
                },
                'SOCKET_CONNECT_TIMEOUT': 5,
                'SOCKET_TIMEOUT': 5,
                'IGNORE_EXCEPTIONS': True,
            },
            'KEY_PREFIX': 'campus',
            'TIMEOUT': 300,
        }
    }
