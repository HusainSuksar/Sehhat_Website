#!/usr/bin/env python3
"""
Health Check Script for Umoor Sehhat on PythonAnywhere
This script performs comprehensive health checks on the deployed application
"""

import os
import sys
import django
import requests
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings_pythonanywhere')
django.setup()

from django.contrib.auth import get_user_model
from django.db import connection
from django.core.cache import cache
from django.conf import settings

User = get_user_model()

class HealthChecker:
    def __init__(self):
        self.checks = []
        self.passed = 0
        self.failed = 0
        
    def add_check(self, name, status, message=""):
        self.checks.append({
            'name': name,
            'status': status,
            'message': message,
            'timestamp': datetime.now()
        })
        
        if status:
            self.passed += 1
        else:
            self.failed += 1
    
    def print_status(self, message):
        print(f"✅ {message}")
    
    def print_error(self, message):
        print(f"❌ {message}")
    
    def print_warning(self, message):
        print(f"⚠️  {message}")
    
    def print_info(self, message):
        print(f"ℹ️  {message}")
    
    def check_database(self):
        """Check database connectivity and basic queries"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                
            if result[0] == 1:
                self.add_check("Database Connection", True, "MySQL connection successful")
                
                # Check user count
                user_count = User.objects.count()
                self.add_check("Database Data", user_count > 0, f"Found {user_count} users")
                
            else:
                self.add_check("Database Connection", False, "Query returned unexpected result")
                
        except Exception as e:
            self.add_check("Database Connection", False, f"Error: {str(e)}")
    
    def check_cache(self):
        """Check cache functionality"""
        try:
            test_key = "health_check_test"
            test_value = "test_value_123"
            
            # Set cache
            cache.set(test_key, test_value, 60)
            
            # Get cache
            cached_value = cache.get(test_key)
            
            if cached_value == test_value:
                self.add_check("Cache System", True, "Cache read/write successful")
                cache.delete(test_key)  # Cleanup
            else:
                self.add_check("Cache System", False, "Cache value mismatch")
                
        except Exception as e:
            self.add_check("Cache System", False, f"Error: {str(e)}")
    
    def check_static_files(self):
        """Check if static files are properly configured"""
        try:
            static_root = getattr(settings, 'STATIC_ROOT', None)
            static_url = getattr(settings, 'STATIC_URL', None)
            
            if static_root and os.path.exists(static_root):
                file_count = sum(len(files) for _, _, files in os.walk(static_root))
                self.add_check("Static Files", file_count > 0, f"Found {file_count} static files")
            else:
                self.add_check("Static Files", False, "Static root directory not found")
                
        except Exception as e:
            self.add_check("Static Files", False, f"Error: {str(e)}")
    
    def check_media_files(self):
        """Check media files configuration"""
        try:
            media_root = getattr(settings, 'MEDIA_ROOT', None)
            
            if media_root:
                if os.path.exists(media_root):
                    self.add_check("Media Directory", True, f"Media directory exists: {media_root}")
                else:
                    # Create media directory if it doesn't exist
                    os.makedirs(media_root, exist_ok=True)
                    self.add_check("Media Directory", True, f"Created media directory: {media_root}")
            else:
                self.add_check("Media Directory", False, "MEDIA_ROOT not configured")
                
        except Exception as e:
            self.add_check("Media Directory", False, f"Error: {str(e)}")
    
    def check_user_roles(self):
        """Check if test users with different roles exist"""
        roles_to_check = ['badri_mahal_admin', 'student', 'doctor', 'aamil', 'moze_coordinator']
        
        for role in roles_to_check:
            count = User.objects.filter(role=role).count()
            self.add_check(f"Users ({role})", count > 0, f"Found {count} {role} users")
    
    def check_django_settings(self):
        """Check critical Django settings"""
        # Check DEBUG setting
        debug_mode = getattr(settings, 'DEBUG', True)
        self.add_check("Debug Mode", not debug_mode, f"DEBUG = {debug_mode}")
        
        # Check SECRET_KEY
        secret_key = getattr(settings, 'SECRET_KEY', '')
        has_secret = len(secret_key) > 20 and not secret_key.startswith('django-insecure')
        self.add_check("Secret Key", has_secret, "Secret key configured" if has_secret else "Using default/insecure key")
        
        # Check ALLOWED_HOSTS
        allowed_hosts = getattr(settings, 'ALLOWED_HOSTS', [])
        self.add_check("Allowed Hosts", len(allowed_hosts) > 0, f"Configured: {allowed_hosts}")
    
    def check_web_app(self, username=None):
        """Check if the web application is responding"""
        if not username:
            username = os.environ.get('USER', 'yourusername')
        
        url = f"https://{username}.pythonanywhere.com"
        
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                self.add_check("Web Application", True, f"App responding at {url}")
            else:
                self.add_check("Web Application", False, f"HTTP {response.status_code} at {url}")
                
        except requests.exceptions.RequestException as e:
            self.add_check("Web Application", False, f"Connection error: {str(e)}")
    
    def check_evaluation_system(self):
        """Check if evaluation system components exist"""
        try:
            from evaluation.models import EvaluationForm
            form_count = EvaluationForm.objects.count()
            self.add_check("Evaluation Forms", form_count > 0, f"Found {form_count} evaluation forms")
        except Exception as e:
            self.add_check("Evaluation Forms", False, f"Error: {str(e)}")
        
        try:
            from moze.models import Moze
            moze_count = Moze.objects.count()
            self.add_check("Moze Records", moze_count > 0, f"Found {moze_count} Moze records")
        except Exception as e:
            self.add_check("Moze Records", False, f"Error: {str(e)}")
    
    def run_all_checks(self, check_web=False, username=None):
        """Run all health checks"""
        print("🏥 UMOOR SEHHAT HEALTH CHECK")
        print("=" * 50)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Run checks
        self.check_database()
        self.check_cache()
        self.check_static_files()
        self.check_media_files()
        self.check_user_roles()
        self.check_django_settings()
        self.check_evaluation_system()
        
        if check_web:
            self.check_web_app(username)
        
        # Print results
        print("📊 HEALTH CHECK RESULTS")
        print("-" * 30)
        
        for check in self.checks:
            status_icon = "✅" if check['status'] else "❌"
            print(f"{status_icon} {check['name']}: {check['message']}")
        
        print()
        print(f"📈 SUMMARY: {self.passed} passed, {self.failed} failed")
        
        if self.failed == 0:
            self.print_status("🎉 All health checks passed!")
            return True
        else:
            self.print_error(f"⚠️  {self.failed} health checks failed!")
            return False

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Health check for Umoor Sehhat')
    parser.add_argument('--web', action='store_true', help='Check web application response')
    parser.add_argument('--username', help='PythonAnywhere username for web check')
    
    args = parser.parse_args()
    
    checker = HealthChecker()
    success = checker.run_all_checks(check_web=args.web, username=args.username)
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()