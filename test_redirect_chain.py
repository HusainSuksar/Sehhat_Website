#!/usr/bin/env python
"""
Test script to trace the redirect chain for patient login
"""

import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

User = get_user_model()

def test_redirect_chain():
    """Test the redirect chain to identify where the loop occurs"""
    print("🔍 TRACING PATIENT LOGIN REDIRECT CHAIN")
    print("=" * 60)
    
    # Get a patient user
    patient = User.objects.filter(role='patient').first()
    if not patient:
        print("❌ No patient user found")
        return
        
    print(f"Testing with patient: {patient.get_full_name()} (ITS: {patient.its_id})")
    
    client = Client()
    
    # Test 1: Manual step-by-step login process
    print(f"\n🔍 STEP-BY-STEP LOGIN PROCESS:")
    
    # Step 1: Access login page
    print(f"\n1️⃣ Accessing login page...")
    response = client.get('/accounts/login/')
    print(f"   Status: {response.status_code}")
    
    # Step 2: Submit login form
    print(f"\n2️⃣ Submitting login form...")
    login_data = {
        'its_id': patient.its_id,
        'password': 'pass1234'
    }
    
    try:
        response = client.post('/accounts/login/', login_data, follow=False)  # Don't follow redirects
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 302:
            redirect_url = response.get('Location', 'No location header')
            print(f"   Redirect to: {redirect_url}")
            
            # Step 3: Follow the first redirect manually
            print(f"\n3️⃣ Following first redirect to: {redirect_url}")
            response2 = client.get(redirect_url, follow=False)
            print(f"   Status: {response2.status_code}")
            
            if response2.status_code == 302:
                redirect_url2 = response2.get('Location', 'No location header')
                print(f"   Second redirect to: {redirect_url2}")
                
                # Step 4: Follow the second redirect manually
                print(f"\n4️⃣ Following second redirect to: {redirect_url2}")
                response3 = client.get(redirect_url2, follow=False)
                print(f"   Status: {response3.status_code}")
                
                if response3.status_code == 302:
                    redirect_url3 = response3.get('Location', 'No location header')
                    print(f"   Third redirect to: {redirect_url3}")
                    print(f"   🚨 REDIRECT LOOP DETECTED!")
                    
                    # Check if it's the same URL
                    if redirect_url == redirect_url2 or redirect_url2 == redirect_url3:
                        print(f"   ⚡ Loop between: {redirect_url} ↔ {redirect_url2}")
                else:
                    print(f"   ✅ Final destination reached")
            else:
                print(f"   ✅ Direct destination reached")
        else:
            print(f"   ⚠️  No redirect - login might have failed")
            
    except Exception as e:
        print(f"   ❌ Error during manual tracing: {e}")
    
    # Test 2: Check what URLs resolve to
    print(f"\n🔍 URL RESOLUTION TEST:")
    from django.urls import reverse
    
    try:
        profile_url = reverse('accounts:profile')
        print(f"   accounts:profile resolves to: {profile_url}")
    except Exception as e:
        print(f"   ❌ Error resolving accounts:profile: {e}")
    
    try:
        login_url = reverse('accounts:login')
        print(f"   accounts:login resolves to: {login_url}")
    except Exception as e:
        print(f"   ❌ Error resolving accounts:login: {e}")
    
    # Test 3: Check if there are conflicting URL patterns
    print(f"\n🔍 CHECKING URL PATTERNS:")
    
    # Test root URL
    print(f"\n   Testing root URL '/':")
    response = client.get('/', follow=False)
    print(f"   Status: {response.status_code}")
    if response.status_code == 302:
        print(f"   Redirects to: {response.get('Location', 'Unknown')}")
    
    # Test /login/ URL
    print(f"\n   Testing '/login/' URL:")
    response = client.get('/login/', follow=False)
    print(f"   Status: {response.status_code}")
    if response.status_code == 302:
        print(f"   Redirects to: {response.get('Location', 'Unknown')}")
    
    # Test 4: Check authentication status during redirect
    print(f"\n🔍 AUTHENTICATION STATUS TEST:")
    
    # Login and check authentication
    client.force_login(patient)  # Force login to bypass form
    print(f"   User after force_login: {client.session.get('_auth_user_id', 'Not authenticated')}")
    
    # Test profile access directly
    print(f"\n   Testing direct profile access:")
    response = client.get('/accounts/profile/')
    print(f"   Status: {response.status_code}")
    if response.status_code == 302:
        print(f"   Profile redirects to: {response.get('Location', 'Unknown')}")
    elif response.status_code == 200:
        print(f"   ✅ Profile accessible")
    
    # Test root URL after authentication
    print(f"\n   Testing root URL after authentication:")
    response = client.get('/', follow=False)
    print(f"   Status: {response.status_code}")
    if response.status_code == 302:
        print(f"   Root redirects to: {response.get('Location', 'Unknown')}")

if __name__ == "__main__":
    test_redirect_chain()