"""
Django settings for Render deployment.
Extends the base settings with Render-specific configurations.
"""
from .settings import *
import dj_database_url

# ============================================
# RENDER-SPECIFIC CONFIGURATION
# ============================================

# Support DATABASE_URL from Render
DATABASE_URL = config('DATABASE_URL', default=None)

if DATABASE_URL:
    # Use Render's PostgreSQL database URL
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }

# Render provides RENDER environment variable
IS_RENDER = config('RENDER', default=False, cast=bool)

if IS_RENDER:
    # Disable file-based logging on Render (ephemeral filesystem)
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'simple': {
                'format': '{levelname} {message}',
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
