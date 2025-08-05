"""
WSGI config for PythonAnywhere deployment of Umoor Sehhat
"""

import os
import sys

# Add your project directory to the sys.path
path = '/home/yourusername/umoor_sehhat'  # Replace 'yourusername' with your actual username
if path not in sys.path:
    sys.path.insert(0, path)

# Set environment variable for Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings_pythonanywhere')

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()