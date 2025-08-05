"""
PythonAnywhere settings for Umoor Sehhat
"""
from .settings import *
import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# PythonAnywhere specific allowed hosts
ALLOWED_HOSTS = [
    'yourusername.pythonanywhere.com',  # Replace with your actual username
    'localhost',
    '127.0.0.1',
]

# Database - Use MySQL on PythonAnywhere
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'yourusername$umoor_sehhat',  # Replace yourusername
        'USER': 'yourusername',  # Replace yourusername
        'PASSWORD': 'your-mysql-password',  # Replace with actual password
        'HOST': 'yourusername.mysql.pythonanywhere-services.com',  # Replace yourusername
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Static files configuration for PythonAnywhere
STATIC_URL = '/static/'
STATIC_ROOT = '/home/yourusername/umoor_sehhat/staticfiles'  # Replace yourusername

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = '/home/yourusername/umoor_sehhat/media'  # Replace yourusername

# Security settings for testing
SECURE_SSL_REDIRECT = False  # PythonAnywhere handles HTTPS
SESSION_COOKIE_SECURE = False  # For testing
CSRF_COOKIE_SECURE = False   # For testing

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

# Logging for debugging (simplified for testing)
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

# Override secret key for testing (generate a new one)
SECRET_KEY = 'django-insecure-pythonanywhere-test-key-replace-with-real-key-in-production'