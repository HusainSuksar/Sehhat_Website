#!/usr/bin/env python3
"""
Quick Test Script for All Django Apps
Run this after setting up to verify everything works
"""

import os
import sys
import django
import requests
from django.test import Client
from django.contrib.auth import get_user_model

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sehhat_website.settings')
django.setup()

def test_server_running():
    """Test if Django server is running"""
    try:
        response = requests.get('http://127.0.0.1:8000/', timeout=5)
        return response.status_code == 200
    except:
        return False

def test_database_data():
    """Test if test data exists in database"""
    User = get_user_model()
    
    print("🔍 Checking Database Data...")
    print(f"✅ Total Users: {User.objects.count()}")
    
    # Import models and check data
    try:
        from araz.models import Petition
        print(f"✅ Araz Petitions: {Petition.objects.count()}")
    except:
        print("❌ Araz app data issue")
    
    try:
        from moze.models import Moze
        print(f"✅ Moze Communities: {Moze.objects.count()}")
    except:
        print("❌ Moze app data issue")
    
    try:
        from surveys.models import Survey
        print(f"✅ Surveys: {Survey.objects.count()}")
    except:
        print("❌ Surveys app data issue")
    
    try:
        from doctordirectory.models import Doctor
        print(f"✅ Doctors: {Doctor.objects.count()}")
    except:
        print("❌ Doctor Directory data issue")

def test_urls_with_client():
    """Test URLs using Django test client"""
    client = Client()
    
    urls_to_test = [
        ('/', 'Home Page'),
        ('/araz/', 'Araz App'),
        ('/moze/', 'Moze App'),
        ('/photos/', 'Photos App'),
        ('/surveys/', 'Surveys App'),
        ('/students/', 'Students App'),
        ('/evaluation/', 'Evaluation App'),
        ('/mahalshifa/', 'Mahalshifa App'),
        ('/doctordirectory/', 'Doctor Directory App'),
        ('/accounts/login/', 'Login Page'),
        ('/admin/', 'Admin Panel'),
    ]
    
    print("\n🌐 Testing URL Accessibility...")
    for url, name in urls_to_test:
        try:
            response = client.get(url)
            if response.status_code in [200, 302]:  # 200 OK or 302 Redirect
                print(f"✅ {name}: {url} (Status: {response.status_code})")
            else:
                print(f"⚠️  {name}: {url} (Status: {response.status_code})")
        except Exception as e:
            print(f"❌ {name}: {url} (Error: {str(e)[:50]})")

def main():
    print("🚀 SEHHAT WEBSITE - COMPREHENSIVE TEST")
    print("=" * 50)
    
    # Test 1: Database Data
    test_database_data()
    
    # Test 2: URL Accessibility
    test_urls_with_client()
    
    # Test 3: Server Status
    print("\n🖥️  Checking Development Server...")
    if test_server_running():
        print("✅ Django server is running on http://127.0.0.1:8000/")
        print("\n🎯 RECOMMENDED TESTING FLOW:")
        print("1. Open browser: http://127.0.0.1:8000/")
        print("2. Test each app navigation")
        print("3. Login to admin: http://127.0.0.1:8000/admin/")
        print("4. Check data in admin panels")
        print("5. Test user authentication")
        print("6. Try CRUD operations")
    else:
        print("❌ Django server not running")
        print("💡 Start server with: python manage.py runserver")
    
    print("\n" + "=" * 50)
    print("🏆 TEST COMPLETE!")
    print("📊 Check results above for any issues")

if __name__ == "__main__":
    main()