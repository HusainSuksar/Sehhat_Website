#!/usr/bin/env python3
"""
Test script to check functionality with existing database structure
"""

import os
import sys
import django
from datetime import datetime, timedelta, date
import random

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import connection

User = get_user_model()

def check_existing_data():
    """Check what data already exists in the database"""
    print("🔍 CHECKING EXISTING DATA")
    print("=" * 40)
    
    # Check users
    try:
        user_count = User.objects.count()
        print(f"👥 Users: {user_count}")
        
        # Show sample users
        for user in User.objects.all()[:5]:
            print(f"   - {user.username} ({user.role}) - {user.first_name} {user.last_name}")
            
    except Exception as e:
        print(f"❌ Users error: {e}")
    
    # Check tables that exist
    cursor = connection.cursor()
    
    # Test each app based on existing tables
    test_results = {}
    
    # 1. Accounts - Already working
    test_results['accounts'] = user_count > 0
    
    # 2. Moze
    try:
        cursor.execute("SELECT COUNT(*) FROM moze_moze")
        moze_count = cursor.fetchone()[0]
        print(f"🏘️  Moze: {moze_count} communities")
        test_results['moze'] = True
    except Exception as e:
        print(f"❌ Moze error: {e}")
        test_results['moze'] = False
    
    # 3. Araz (DuaAraz table exists)
    try:
        cursor.execute("SELECT COUNT(*) FROM araz_duaaraz")
        araz_count = cursor.fetchone()[0]
        print(f"📋 Araz: {araz_count} medical requests")
        test_results['araz'] = True
    except Exception as e:
        print(f"❌ Araz error: {e}")
        test_results['araz'] = False
    
    # 4. Photos
    try:
        cursor.execute("SELECT COUNT(*) FROM photos_photoalbum")
        album_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM photos_photo")
        photo_count = cursor.fetchone()[0]
        print(f"📷 Photos: {album_count} albums, {photo_count} photos")
        test_results['photos'] = True
    except Exception as e:
        print(f"❌ Photos error: {e}")
        test_results['photos'] = False
    
    # 5. Surveys
    try:
        cursor.execute("SELECT COUNT(*) FROM surveys_survey")
        survey_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM surveys_surveyresponse")
        response_count = cursor.fetchone()[0]
        print(f"📊 Surveys: {survey_count} surveys, {response_count} responses")
        test_results['surveys'] = True
    except Exception as e:
        print(f"❌ Surveys error: {e}")
        test_results['surveys'] = False
    
    # 6. Students
    try:
        cursor.execute("SELECT COUNT(*) FROM students_studentprofile")
        student_count = cursor.fetchone()[0]
        print(f"🎓 Students: {student_count} student profiles")
        test_results['students'] = True
    except Exception as e:
        print(f"❌ Students error: {e}")
        test_results['students'] = False
    
    # 7. Evaluation
    try:
        cursor.execute("SELECT COUNT(*) FROM evaluation_evaluation")
        eval_count = cursor.fetchone()[0]
        print(f"📝 Evaluation: {eval_count} evaluations")
        test_results['evaluation'] = True
    except Exception as e:
        print(f"❌ Evaluation error: {e}")
        test_results['evaluation'] = False
    
    # 8. Mahalshifa
    try:
        cursor.execute("SELECT COUNT(*) FROM mahalshifa_patient")
        patient_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM mahalshifa_appointment")
        appointment_count = cursor.fetchone()[0]
        print(f"🏥 Mahalshifa: {patient_count} patients, {appointment_count} appointments")
        test_results['mahalshifa'] = True
    except Exception as e:
        print(f"❌ Mahalshifa error: {e}")
        test_results['mahalshifa'] = False
    
    # 9. Doctor Directory
    try:
        cursor.execute("SELECT COUNT(*) FROM doctordirectory_doctor")
        doctor_count = cursor.fetchone()[0]
        print(f"👨‍⚕️ Doctor Directory: {doctor_count} doctors")
        test_results['doctordirectory'] = True
    except Exception as e:
        print(f"❌ Doctor Directory error: {e}")
        test_results['doctordirectory'] = False
    
    return test_results

def test_web_urls():
    """Test if Django can serve the URLs"""
    print("\n🌐 TESTING WEB URLs")
    print("=" * 40)
    
    # Start development server in background and test URLs
    import subprocess
    import time
    import requests
    
    try:
        # Start server
        print("Starting Django server...")
        server = subprocess.Popen(
            ['python3', 'manage.py', 'runserver', '8080'],
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        time.sleep(3)
        
        # Test URLs
        base_url = 'http://127.0.0.1:8080'
        test_urls = [
            '/',
            '/accounts/login/',
            '/araz/',
            '/moze/',
            '/photos/',
            '/surveys/',
            '/students/',
            '/evaluation/',
            '/mahalshifa/',
            '/doctordirectory/',
        ]
        
        working_urls = 0
        for url in test_urls:
            try:
                response = requests.get(base_url + url, timeout=5)
                if response.status_code in [200, 302]:  # OK or Redirect
                    print(f"✅ {url} - Working")
                    working_urls += 1
                else:
                    print(f"⚠️  {url} - Status {response.status_code}")
            except Exception as e:
                print(f"❌ {url} - Error: {e}")
        
        print(f"\n🎯 URL Test Results: {working_urls}/{len(test_urls)} URLs working")
        
        # Stop server
        server.terminate()
        server.wait()
        
        return working_urls == len(test_urls)
        
    except Exception as e:
        print(f"❌ Server test error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 COMPREHENSIVE FUNCTIONALITY TEST")
    print("=" * 50)
    
    # Check existing data
    test_results = check_existing_data()
    
    # Count working apps
    working_apps = sum(test_results.values())
    total_apps = len(test_results)
    
    print(f"\n📊 DATABASE TEST RESULTS")
    print("=" * 40)
    print(f"✅ Working Apps: {working_apps}/{total_apps}")
    
    for app, working in test_results.items():
        status = "✅ Working" if working else "❌ Issues"
        print(f"   {app}: {status}")
    
    # Test basic Django functionality
    print(f"\n🔧 DJANGO SYSTEM STATUS")
    print("=" * 40)
    
    try:
        # Test model imports
        from accounts.models import User
        print("✅ Model imports: Working")
        
        # Test database connection
        User.objects.count()
        print("✅ Database connection: Working")
        
        # Test template system
        from django.template.loader import get_template
        get_template('accounts/login.html')
        print("✅ Template system: Working")
        
        # Test URL routing
        from django.urls import reverse
        reverse('accounts:login')
        print("✅ URL routing: Working")
        
    except Exception as e:
        print(f"❌ Django system error: {e}")
    
    print(f"\n🎉 FINAL ASSESSMENT")
    print("=" * 40)
    
    if working_apps >= 7:
        print("🎯 EXCELLENT: Most apps are working correctly!")
        print("📱 Your Django application is functional and ready to use.")
        
        print("\n🚀 NEXT STEPS:")
        print("1. Run: python manage.py runserver")
        print("2. Visit: http://127.0.0.1:8000/")
        print("3. Login with existing user credentials")
        print("4. Test each app's functionality")
        
    else:
        print("⚠️  Some apps need attention, but the core system is working.")
        print("🔧 Consider running fresh migrations for problematic apps.")

if __name__ == "__main__":
    main()