"""
PythonAnywhere Production Settings for Umoor Sehhat
"""
from .settings import *
import os
from decouple import config, Csv

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

# PythonAnywhere specific allowed hosts
# Update 'sehhat' with your actual PythonAnywhere username
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv(), default='sehhat.pythonanywhere.com,localhost,127.0.0.1')

# Database - Use MySQL on PythonAnywhere
# Update 'sehhat' with your actual PythonAnywhere username
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME', default='sehhat$umoor_sehhat'),
        'USER': config('DB_USER', default='sehhat'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='sehhat.mysql.pythonanywhere-services.com'),
        'PORT': config('DB_PORT', default='3306', cast=int),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Static files configuration for PythonAnywhere
STATIC_URL = '/static/'
STATIC_ROOT = config('STATIC_ROOT', default='/home/sehhat/umoor_sehhat/staticfiles')

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = config('MEDIA_ROOT', default='/home/sehhat/umoor_sehhat/media')

# Security settings (relaxed for PythonAnywhere testing)
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=False, cast=bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=False, cast=bool)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Email configuration (optional for testing)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@sehhat.pythonanywhere.com')

# Cache configuration - Use local memory cache for simplicity
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Redis configuration (optional - only if you have Redis set up)
REDIS_URL = config('REDIS_URL', default='')
if REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }

# Time zone
TIME_ZONE = config('TIME_ZONE', default='Asia/Karachi')

# Test mode flag
TEST_MODE = config('TEST_MODE', default=False, cast=bool)

# Logging configuration - Simplified for PythonAnywhere
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
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/home/sehhat/umoor_sehhat/error.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'umoor_sehhat': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Secret key - MUST be set in environment variables for security
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production-immediately')

# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 3600  # 1 hour

# File upload limits
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

# Internationalization
USE_I18N = True
USE_TZ = True

# Additional PythonAnywhere specific settings
FORCE_SCRIPT_NAME = None
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# For debugging - can be removed in production
if DEBUG:
    INTERNAL_IPS = ['127.0.0.1', 'localhost']