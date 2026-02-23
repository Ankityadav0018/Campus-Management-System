"""
Django settings for campus_project.
"""
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-u$vs-*iw58g&n9p^9k5+fn!&php!3qwa$n*ys4&$&g3ecxe9dt'
DEBUG = True
ALLOWED_HOSTS = ['*']  # For development - restrict in production

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.users',
    'apps.attendance',
    'apps.food',
    'apps.resources',
    'apps.remedial',
    # 'apps.ai_module',
]

AUTH_USER_MODEL = 'users.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.gzip.GZipMiddleware',  # PERFORMANCE: Compress responses (70% size reduction)
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'campus_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'campus_project.wsgi.application'

# ============================================
# DATABASE CONFIGURATION - HIGHLY OPTIMIZED
# ============================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'ATOMIC_REQUESTS': True,  # Wrap each request in a transaction
        'CONN_MAX_AGE': 600,  # Keep connections alive for 10 minutes (connection pooling)
        'OPTIONS': {
            'timeout': 20,  # 20 second timeout for database locks
            'check_same_thread': False,  # Allow multi-threading
            'isolation_level': None,  # Autocommit mode for better concurrency
        },
    }
}

# ⚠️ CRITICAL: For production with >50 concurrent users, MUST use PostgreSQL:
# SQLite has major limitations with concurrent writes. Uncomment below for production:
#
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.environ.get('DB_NAME', 'campus_db'),
#         'USER': os.environ.get('DB_USER', 'postgres'),
#         'PASSWORD': os.environ.get('DB_PASSWORD', ''),
#         'HOST': os.environ.get('DB_HOST', 'localhost'),
#         'PORT': os.environ.get('DB_PORT', '5432'),
#         'ATOMIC_REQUESTS': True,
#         'CONN_MAX_AGE': 600,  # Connection pooling
#         'OPTIONS': {
#             'connect_timeout': 10,
#             'options': '-c statement_timeout=30000',  # 30 second query timeout
#         },
#     }
# }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================
# CACHING CONFIGURATION - CRITICAL FOR PERFORMANCE
# ============================================

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'campus-cache',
        'TIMEOUT': 300,  # 5 minutes default
        'OPTIONS': {
            'MAX_ENTRIES': 10000,  # Increased cache size
        }
    }
}

# For production with multiple servers, use Redis (10-100x faster):
# Install: pip install redis django-redis
# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
#         'OPTIONS': {
#             'CLIENT_CLASS': 'django_redis.client.DefaultClient',
#             'CONNECTION_POOL_KWARGS': {
#                 'max_connections': 50,
#                 'retry_on_timeout': True,
#             },
#             'SOCKET_CONNECT_TIMEOUT': 5,
#             'SOCKET_TIMEOUT': 5,
#             'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
#             'IGNORE_EXCEPTIONS': True,  # Fail gracefully if Redis is down
#         },
#         'KEY_PREFIX': 'campus',
#         'TIMEOUT': 300,
#     }
# }

# Session Configuration - Use cached sessions for 50% faster page loads
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_SAVE_EVERY_REQUEST = False  # Only save when modified

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

# ============================================
# LOGGING - MONITOR PERFORMANCE & ERRORS
# ============================================

# Create logs directory
(BASE_DIR / 'logs').mkdir(exist_ok=True)

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
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'db_queries': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'db_queries.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
            'filters': ['require_debug_true'],
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'django.db.backends': {
            'handlers': ['db_queries'],
            'level': 'INFO',  # Change to DEBUG to see all SQL queries
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'file'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# For production SMTP:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

# Auth URLs
LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# ============================================
# SECURITY SETTINGS (Enable in production)
# ============================================
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# ============================================
# PERFORMANCE OPTIMIZATION SETTINGS
# ============================================

# Database connection persistence
CONN_MAX_AGE = 600

# Optimize Django's internal caching
INTERNAL_IPS = ['127.0.0.1', 'localhost']

# Data encoding
DEFAULT_CHARSET = 'utf-8'

# Optimize query performance
# Set to True to see number of queries per request (development only)
if DEBUG:
    LOGGING['loggers']['django.db.backends']['level'] = 'DEBUG'
