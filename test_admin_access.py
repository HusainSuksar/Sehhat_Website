#!/usr/bin/env python
"""
Test script to check admin access permissions and identify security issues
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

def test_admin_access():
    """Test admin access for different user roles"""
    print("🔍 TESTING ADMIN ACCESS PERMISSIONS")
    print("=" * 60)
    
    # Get users of different roles
    test_users = {}
    for role in ['aamil', 'moze_coordinator', 'doctor', 'student', 'patient', 'badri_mahal_admin']:
        user = User.objects.filter(role=role).first()
        if user:
            test_users[role] = user
            print(f"Found {role}: {user.its_id} - {user.get_full_name()}")
    
    # Also get superuser
    superuser = User.objects.filter(is_superuser=True).first()
    if superuser:
        test_users['superuser'] = superuser
        print(f"Found superuser: {superuser.its_id} - {superuser.get_full_name()}")
    
    print(f"\nTesting {len(test_users)} different user types...")
    
    # Test admin access
    print(f"\n{'='*60}")
    print("🚨 TESTING ADMIN ACCESS")
    print(f"{'='*60}")
    
    admin_urls = [
        '/admin/',  # Django admin
        '/admin/auth/',  # Django admin auth
        '/admin/auth/user/',  # Django admin users
    ]
    
    client = Client()
    
    for role, user in test_users.items():
        print(f"\n🔍 Testing {role.upper()}: {user.get_full_name()}")
        print(f"   Role: {user.role}")
        print(f"   is_admin: {user.is_admin}")
        print(f"   is_superuser: {user.is_superuser}")
        print(f"   is_staff: {user.is_staff}")
        
        # Login as this user
        try:
            login_response = client.post('/accounts/login/', {
                'its_id': user.its_id,
                'password': 'pass1234'
            })
            
            if login_response.status_code in [200, 302]:
                print(f"   ✅ Login successful")
                
                # Test admin URLs
                for url in admin_urls:
                    try:
                        response = client.get(url)
                        if response.status_code == 200:
                            print(f"   🚨 SECURITY ISSUE: Can access {url} (Status: {response.status_code})")
                        elif response.status_code == 302:
                            print(f"   ⚠️  Redirected from {url} (Status: {response.status_code})")
                        elif response.status_code == 403:
                            print(f"   ✅ Properly denied access to {url} (Status: {response.status_code})")
                        elif response.status_code == 404:
                            print(f"   ⚠️  Not found {url} (Status: {response.status_code})")
                        else:
                            print(f"   ❓ Unexpected response for {url} (Status: {response.status_code})")
                    except Exception as e:
                        print(f"   ❌ Error accessing {url}: {e}")
                
                # Test root redirect
                try:
                    response = client.get('/')
                    if response.status_code == 302:
                        redirect_url = response.get('Location', 'Unknown')
                        print(f"   🔄 Root redirect: {redirect_url}")
                        if 'admin' in redirect_url.lower():
                            print(f"   🚨 REDIRECTS TO ADMIN: {redirect_url}")
                except Exception as e:
                    print(f"   ❌ Error testing root redirect: {e}")
                        
            else:
                print(f"   ❌ Login failed (Status: {login_response.status_code})")
                
        except Exception as e:
            print(f"   ❌ Login error: {e}")
        
        client.logout()
    
    # Test specific dashboard access
    print(f"\n{'='*60}")
    print("🔍 TESTING DASHBOARD ACCESS")
    print(f"{'='*60}")
    
    dashboard_urls = [
        '/doctordirectory/dashboard/',
        '/moze/dashboard/',
        '/students/dashboard/',
        '/evaluation/dashboard/',
        '/surveys/dashboard/',
        '/photos/dashboard/',
    ]
    
    for role, user in test_users.items():
        print(f"\n🔍 Testing {role.upper()} dashboard access:")
        
        # Login
        login_response = client.post('/accounts/login/', {
            'its_id': user.its_id,
            'password': 'pass1234'
        })
        
        if login_response.status_code in [200, 302]:
            # Test each dashboard
            for url in dashboard_urls:
                try:
                    response = client.get(url)
                    dashboard_name = url.split('/')[1]
                    
                    if response.status_code == 200:
                        print(f"   ✅ Can access {dashboard_name} dashboard")
                    elif response.status_code == 403:
                        print(f"   🚫 Denied access to {dashboard_name} dashboard")
                    elif response.status_code == 302:
                        print(f"   🔄 Redirected from {dashboard_name} dashboard")
                    elif response.status_code == 404:
                        print(f"   ❓ {dashboard_name} dashboard not found")
                    else:
                        print(f"   ❓ {dashboard_name} dashboard: Status {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ Error accessing {url}: {e}")
        
        client.logout()
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 SUMMARY")
    print(f"{'='*60}")
    print("Check the output above for:")
    print("🚨 SECURITY ISSUES: Users who can access admin URLs when they shouldn't")
    print("⚠️  REDIRECTS TO ADMIN: Users who get redirected to admin dashboards")
    print("🔄 UNEXPECTED ACCESS: Users accessing dashboards they shouldn't")
    print("\n✅ Expected behavior:")
    print("- Only superusers and badri_mahal_admin should access Django admin")
    print("- Each role should only access their designated dashboard")
    print("- Doctors should only access doctordirectory dashboard")

if __name__ == "__main__":
    test_admin_access()