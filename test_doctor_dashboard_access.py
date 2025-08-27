#!/usr/bin/env python
"""
Test script to specifically check doctor dashboard access security issue
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

def test_doctor_dashboard_access():
    """Test if non-doctors can access doctor dashboard"""
    print("🚨 TESTING DOCTOR DASHBOARD ACCESS SECURITY")
    print("=" * 60)
    
    # Get users of different roles
    test_users = {}
    for role in ['aamil', 'moze_coordinator', 'doctor', 'student', 'patient', 'badri_mahal_admin']:
        user = User.objects.filter(role=role).first()
        if user:
            test_users[role] = user
    
    # Also get superuser
    superuser = User.objects.filter(is_superuser=True).first()
    if superuser:
        test_users['superuser'] = superuser
    
    client = Client()
    doctor_dashboard_url = '/doctordirectory/'
    
    print(f"Testing access to {doctor_dashboard_url}")
    print("=" * 60)
    
    security_issues = []
    
    for role, user in test_users.items():
        print(f"\n🔍 Testing {role.upper()}: {user.get_full_name()}")
        
        # Login as this user
        try:
            login_response = client.post('/accounts/login/', {
                'its_id': user.its_id,
                'password': 'pass1234'
            })
            
            if login_response.status_code in [200, 302]:
                print(f"   ✅ Login successful")
                
                # Test doctor dashboard access
                response = client.get(doctor_dashboard_url)
                print(f"   📊 Doctor dashboard response: {response.status_code}")
                
                if response.status_code == 200:
                    # Check if this user should have access
                    should_have_access = (
                        role == 'doctor' or 
                        role == 'superuser' or 
                        role == 'badri_mahal_admin' or
                        user.is_admin
                    )
                    
                    if should_have_access:
                        print(f"   ✅ EXPECTED: {role} should have access")
                    else:
                        print(f"   🚨 SECURITY ISSUE: {role} should NOT have access!")
                        security_issues.append(f"{role} can access doctor dashboard")
                        
                        # Check what data they can see
                        if b'Dashboard' in response.content or b'dashboard' in response.content:
                            print(f"   📄 Can see dashboard content")
                        if b'patient' in response.content.lower():
                            print(f"   🩺 Can see patient data")
                        if b'appointment' in response.content.lower():
                            print(f"   📅 Can see appointment data")
                        if b'doctor' in response.content.lower():
                            print(f"   👨‍⚕️ Can see doctor data")
                            
                elif response.status_code == 403:
                    print(f"   ✅ GOOD: Access denied (403)")
                elif response.status_code == 302:
                    redirect_url = response.get('Location', 'Unknown')
                    print(f"   🔄 Redirected to: {redirect_url}")
                    if 'login' in redirect_url:
                        print(f"   ✅ GOOD: Redirected to login")
                    else:
                        print(f"   ⚠️  Unexpected redirect")
                else:
                    print(f"   ❓ Unexpected status: {response.status_code}")
                        
            else:
                print(f"   ❌ Login failed")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        client.logout()
    
    # Test other dashboards for comparison
    print(f"\n{'='*60}")
    print("🔍 TESTING OTHER DASHBOARDS FOR COMPARISON")
    print(f"{'='*60}")
    
    dashboard_urls = [
        ('/moze/', 'Moze Dashboard'),
        ('/students/', 'Students Dashboard'),
        ('/evaluation/', 'Evaluation Dashboard'),
        ('/accounts/dashboard/', 'Accounts Dashboard'),
    ]
    
    # Test with a patient user to see if they can access other dashboards
    patient_user = test_users.get('patient')
    if patient_user:
        print(f"\n🔍 Testing PATIENT access to other dashboards:")
        
        # Login as patient
        login_response = client.post('/accounts/login/', {
            'its_id': patient_user.its_id,
            'password': 'pass1234'
        })
        
        if login_response.status_code in [200, 302]:
            for url, name in dashboard_urls:
                try:
                    response = client.get(url)
                    if response.status_code == 200:
                        print(f"   🚨 Can access {name} at {url}")
                        security_issues.append(f"Patient can access {name}")
                    elif response.status_code == 403:
                        print(f"   ✅ Properly denied {name}")
                    elif response.status_code == 302:
                        print(f"   🔄 Redirected from {name}")
                    else:
                        print(f"   ❓ {name}: Status {response.status_code}")
                except Exception as e:
                    print(f"   ❌ Error testing {name}: {e}")
        
        client.logout()
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 SECURITY ANALYSIS SUMMARY")
    print(f"{'='*60}")
    
    if security_issues:
        print(f"🚨 CRITICAL SECURITY ISSUES FOUND ({len(security_issues)}):")
        for issue in security_issues:
            print(f"   • {issue}")
        
        print(f"\n💡 RECOMMENDED FIXES:")
        print(f"   1. Add permission decorators to dashboard views")
        print(f"   2. Use role-based access control mixins")
        print(f"   3. Implement proper access checks in each dashboard")
        print(f"   4. Add redirect logic for unauthorized users")
        
    else:
        print(f"✅ No security issues found - all dashboards properly protected")
    
    return security_issues

if __name__ == "__main__":
    issues = test_doctor_dashboard_access()
    if issues:
        print(f"\n🚨 Found {len(issues)} security issues that need immediate attention!")
        sys.exit(1)
    else:
        print(f"\n✅ All security checks passed!")
        sys.exit(0)