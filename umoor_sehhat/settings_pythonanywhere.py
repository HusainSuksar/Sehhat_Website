"""
PythonAnywhere settings for Umoor Sehhat
"""
from .settings import *
from decouple import config

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

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
        'NAME': config('DB_NAME', default='yourusername$umoor_sehhat'),
        'USER': config('DB_USER', default='yourusername'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='yourusername.mysql.pythonanywhere-services.com'),
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

# Static files configuration for PythonAnywhere
STATIC_URL = '/static/'
STATIC_ROOT = '/home/yourusername/umoor_sehhat/staticfiles'

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = '/home/yourusername/umoor_sehhat/media'

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

# Logging for debugging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/home/yourusername/umoor_sehhat/debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}