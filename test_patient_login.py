#!/usr/bin/env python
"""
Test script to diagnose patient login issues
"""

import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model, authenticate
from django.urls import reverse

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

User = get_user_model()

def test_patient_login():
    """Comprehensive patient login testing"""
    print("🔍 TESTING PATIENT LOGIN FUNCTIONALITY")
    print("=" * 60)
    
    # Find patient users
    patient_users = User.objects.filter(role='patient')
    print(f"Found {patient_users.count()} patient users in database")
    
    if patient_users.count() == 0:
        print("❌ No patient users found in database!")
        return False
    
    # Test each patient
    client = Client()
    successful_logins = 0
    failed_logins = 0
    
    for i, patient in enumerate(patient_users[:5]):  # Test first 5 patients
        print(f"\n{'='*60}")
        print(f"🧪 TESTING PATIENT {i+1}: {patient.get_full_name()}")
        print(f"{'='*60}")
        
        print(f"📋 Patient Details:")
        print(f"   ITS ID: {patient.its_id}")
        print(f"   Username: {patient.username}")
        print(f"   Email: {patient.email}")
        print(f"   Role: {patient.role}")
        print(f"   Is Active: {patient.is_active}")
        print(f"   Is Staff: {patient.is_staff}")
        print(f"   Has Usable Password: {patient.has_usable_password()}")
        
        # Test 1: Direct authentication
        print(f"\n🔐 TESTING DIRECT AUTHENTICATION:")
        
        # Try with ITS ID
        auth_user = authenticate(username=patient.its_id, password='pass1234')
        if auth_user:
            print(f"   ✅ Direct auth with ITS ID successful")
        else:
            print(f"   ❌ Direct auth with ITS ID failed")
        
        # Try with username
        auth_user = authenticate(username=patient.username, password='pass1234')
        if auth_user:
            print(f"   ✅ Direct auth with username successful")
        else:
            print(f"   ❌ Direct auth with username failed")
        
        # Test 2: Login form test
        print(f"\n🌐 TESTING LOGIN FORM:")
        
        # Test with ITS ID
        login_data = {
            'its_id': patient.its_id,
            'password': 'pass1234'
        }
        
        try:
            response = client.post('/accounts/login/', login_data, follow=True)
            print(f"   📊 Login response status: {response.status_code}")
            
            if response.status_code == 200:
                # Check if user is authenticated
                if hasattr(response, 'wsgi_request') and response.wsgi_request.user.is_authenticated:
                    print(f"   ✅ Login successful - user authenticated")
                    print(f"   👤 Logged in as: {response.wsgi_request.user.get_full_name()}")
                    successful_logins += 1
                    
                    # Check redirect after login
                    if response.redirect_chain:
                        final_url = response.redirect_chain[-1][0]
                        print(f"   🔄 Final redirect URL: {final_url}")
                    
                elif b'error' in response.content.lower() or b'invalid' in response.content.lower():
                    print(f"   ❌ Login failed - error message in response")
                    failed_logins += 1
                    # Extract error message
                    content = response.content.decode('utf-8')
                    if 'error' in content.lower():
                        start = content.lower().find('error')
                        error_snippet = content[start:start+200]
                        print(f"   🚨 Error snippet: {error_snippet[:100]}...")
                else:
                    print(f"   ⚠️  Login status unclear - response received but authentication status unknown")
                    failed_logins += 1
            else:
                print(f"   ❌ Login failed - HTTP {response.status_code}")
                failed_logins += 1
                
        except Exception as e:
            print(f"   ❌ Login test failed with exception: {e}")
            failed_logins += 1
        
        # Test 3: Check password
        print(f"\n🔑 TESTING PASSWORD:")
        password_check = patient.check_password('pass1234')
        print(f"   Password check result: {password_check}")
        
        if not password_check:
            print(f"   🔧 Attempting to set password...")
            patient.set_password('pass1234')
            patient.save()
            new_check = patient.check_password('pass1234')
            print(f"   New password check result: {new_check}")
        
        # Test 4: Check if patient profile exists
        print(f"\n👤 CHECKING PATIENT PROFILE:")
        if hasattr(patient, 'patient_profile'):
            try:
                patient_profiles = patient.patient_profile.all()
                print(f"   Patient profiles found: {patient_profiles.count()}")
                for profile in patient_profiles:
                    print(f"   📋 Profile: {profile}")
            except Exception as e:
                print(f"   ❌ Error checking patient profile: {e}")
        else:
            print(f"   ⚠️  No patient_profile relationship found")
        
        client.logout()
        print(f"\n{'='*40}")
    
    # Test 5: Check authentication backend
    print(f"\n🔧 CHECKING AUTHENTICATION CONFIGURATION:")
    from django.conf import settings
    print(f"   Authentication backends: {getattr(settings, 'AUTHENTICATION_BACKENDS', 'Not configured')}")
    
    # Test 6: Check login view
    print(f"\n🌐 TESTING LOGIN VIEW ACCESS:")
    try:
        response = client.get('/accounts/login/')
        print(f"   Login page status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Login page accessible")
            # Check if form fields are present
            content = response.content.decode('utf-8')
            if 'its_id' in content:
                print(f"   ✅ ITS ID field found in form")
            else:
                print(f"   ❌ ITS ID field NOT found in form")
            if 'password' in content:
                print(f"   ✅ Password field found in form")
            else:
                print(f"   ❌ Password field NOT found in form")
        else:
            print(f"   ❌ Login page not accessible")
    except Exception as e:
        print(f"   ❌ Error accessing login page: {e}")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 PATIENT LOGIN TEST SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Successful logins: {successful_logins}")
    print(f"❌ Failed logins: {failed_logins}")
    print(f"📊 Total patients tested: {min(patient_users.count(), 5)}")
    
    if successful_logins == 0:
        print(f"\n🚨 CRITICAL ISSUE: NO PATIENTS CAN LOGIN!")
        print(f"Possible causes:")
        print(f"   1. Authentication backend issues")
        print(f"   2. Password problems")
        print(f"   3. Login form/view issues")
        print(f"   4. User account issues (inactive, no password, etc.)")
        return False
    elif failed_logins > successful_logins:
        print(f"\n⚠️  PARTIAL ISSUE: Some patients cannot login")
        return False
    else:
        print(f"\n✅ Patient login appears to be working")
        return True

if __name__ == "__main__":
    success = test_patient_login()
    if not success:
        print(f"\n🔧 PATIENT LOGIN NEEDS FIXING!")
        sys.exit(1)
    else:
        print(f"\n✅ PATIENT LOGIN IS WORKING!")
        sys.exit(0)