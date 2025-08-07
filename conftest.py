"""
Pytest configuration for Django
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')

def pytest_configure():
    """Configure pytest for Django"""
    if not settings.configured:
        django.setup()

def pytest_unconfigure():
    """Clean up after pytest"""
    pass