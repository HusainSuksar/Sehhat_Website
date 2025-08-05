"""
Local testing version of PythonAnywhere settings for Umoor Sehhat
This uses SQLite for local testing before deploying to PythonAnywhere
"""
from .settings import *
import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True  # Enable for local testing

# Local testing allowed hosts
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'yourusername.pythonanywhere.com',  # Replace with your actual username
]

# Database - Use SQLite for local testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_pythonanywhere_test.sqlite3',
    }
}

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles_test'

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media_test'

# Security settings for testing
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Email configuration (for testing)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Cache configuration (simple for testing)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Time zone
TIME_ZONE = 'Asia/Karachi'

# Test mode flag
TEST_MODE = True

# Simplified logging for local testing
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Override secret key for testing
SECRET_KEY = 'django-insecure-local-test-key-for-pythonanywhere-testing-only'