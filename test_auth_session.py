#!/usr/bin/env python
"""
Test script to check authentication and session issues
"""

import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model
# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

from django.contrib.sessions.models import Session

User = get_user_model()

def test_auth_session():
    """Test authentication and session handling"""
    print("🔍 TESTING AUTHENTICATION & SESSION")
    print("=" * 60)
    
    # Get a patient user
    patient = User.objects.filter(role='patient').first()
    if not patient:
        print("❌ No patient user found")
        return
        
    print(f"Testing with patient: {patient.get_full_name()} (ITS: {patient.its_id})")
    
    client = Client()
    
    # Test 1: Check session before login
    print(f"\n1️⃣ SESSION BEFORE LOGIN:")
    print(f"   Session key: {client.session.session_key}")
    print(f"   Session data: {dict(client.session)}")
    
    # Test 2: Manual login process with session tracking
    print(f"\n2️⃣ MANUAL LOGIN PROCESS:")
    
    login_data = {
        'its_id': patient.its_id,
        'password': 'pass1234'
    }
    
    # Get CSRF token first
    login_page_response = client.get('/accounts/login/')
    csrf_token = login_page_response.context['csrf_token'] if login_page_response.context else None
    print(f"   CSRF token: {csrf_token}")
    
    # Submit login with CSRF
    if csrf_token:
        login_data['csrfmiddlewaretoken'] = csrf_token
    
    response = client.post('/accounts/login/', login_data, follow=False)
    print(f"   Login response status: {response.status_code}")
    print(f"   Login response headers: {dict(response.items())}")
    
    # Check session after login attempt
    print(f"\n3️⃣ SESSION AFTER LOGIN:")
    print(f"   Session key: {client.session.session_key}")
    print(f"   Session data: {dict(client.session)}")
    print(f"   User ID in session: {client.session.get('_auth_user_id', 'Not found')}")
    print(f"   Auth backend: {client.session.get('_auth_user_backend', 'Not found')}")
    
    # Test 3: Check if user is actually authenticated
    print(f"\n4️⃣ AUTHENTICATION STATUS:")
    
    # Force a new request to check authentication
    profile_response = client.get('/accounts/profile/', follow=False)
    print(f"   Profile response status: {profile_response.status_code}")
    
    if hasattr(profile_response, 'wsgi_request'):
        user = profile_response.wsgi_request.user
        print(f"   User in request: {user}")
        print(f"   Is authenticated: {user.is_authenticated}")
        print(f"   User ID: {user.id if user.is_authenticated else 'Anonymous'}")
    
    # Test 4: Check LoginRequiredMixin behavior
    print(f"\n5️⃣ LOGIN REQUIRED MIXIN TEST:")
    
    from django.contrib.auth.mixins import LoginRequiredMixin
    from django.conf import settings
    
    print(f"   LOGIN_URL setting: {getattr(settings, 'LOGIN_URL', 'Not set')}")
    print(f"   LOGIN_REDIRECT_URL setting: {getattr(settings, 'LOGIN_REDIRECT_URL', 'Not set')}")
    
    # Test 5: Check middleware
    print(f"\n6️⃣ MIDDLEWARE CHECK:")
    print(f"   MIDDLEWARE: {getattr(settings, 'MIDDLEWARE', 'Not found')}")
    
    # Test 6: Check authentication backends
    print(f"\n7️⃣ AUTHENTICATION BACKENDS:")
    print(f"   AUTHENTICATION_BACKENDS: {getattr(settings, 'AUTHENTICATION_BACKENDS', 'Not found')}")
    
    # Test 7: Direct authentication test
    print(f"\n8️⃣ DIRECT AUTHENTICATION TEST:")
    from django.contrib.auth import authenticate, login
    from django.http import HttpRequest
    
    auth_user = authenticate(username=patient.its_id, password='pass1234')
    print(f"   Authenticate result: {auth_user}")
    
    if auth_user:
        print(f"   User authenticated: {auth_user.get_full_name()}")
        print(f"   User is_active: {auth_user.is_active}")
        print(f"   User has_usable_password: {auth_user.has_usable_password()}")
        
        # Test session login
        print(f"\n   Testing session login...")
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get('/')
        request.session = client.session
        login(request, auth_user)
        print(f"   After login - session data: {dict(request.session)}")
    
    # Test 8: Check if there's a template issue
    print(f"\n9️⃣ TEMPLATE CHECK:")
    try:
        from django.template.loader import get_template
        template = get_template('accounts/profile.html')
        print(f"   Template found: {template.name}")
    except Exception as e:
        print(f"   Template error: {e}")
    
    # Test 9: Check if there's a redirect in the template or view
    print(f"\n🔟 CHECKING FOR HIDDEN REDIRECTS:")
    
    # Force login and check response content
    client.force_login(patient)
    response = client.get('/accounts/profile/', follow=False)
    print(f"   Status after force_login: {response.status_code}")
    
    if response.status_code == 302:
        print(f"   🚨 STILL REDIRECTING after force_login!")
        print(f"   Location header: {response.get('Location', 'None')}")
        
        # This means the view itself is causing the redirect
        print(f"   🔍 The ProfileView itself is causing the redirect")
    elif response.status_code == 200:
        print(f"   ✅ Profile accessible with force_login")
        print(f"   Content length: {len(response.content)}")

if __name__ == "__main__":
    test_auth_session()