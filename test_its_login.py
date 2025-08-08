#!/usr/bin/env python3
"""
Quick test script to verify ITS login functionality
Tests the authentication backend fix
"""

import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

def test_its_login():
    """Test ITS login API endpoint"""
    print("🔐 Testing ITS Login API")
    print("=" * 40)
    
    # Test data
    test_credentials = [
        {"its_id": "12345678", "password": "doctor123", "expected_role": "doctor"},
        {"its_id": "87654321", "password": "admin123", "expected_role": "badri_mahal_admin"},
        {"its_id": "99999999", "password": "student123", "expected_role": "student"},
    ]
    
    base_url = "http://127.0.0.1:8000"
    login_url = f"{base_url}/accounts/api/its-login/"
    
    for i, creds in enumerate(test_credentials, 1):
        print(f"\n🧪 Test {i}: {creds['its_id']} (Expected: {creds['expected_role']})")
        
        try:
            # Make login request
            response = requests.post(login_url, 
                json={
                    "its_id": creds["its_id"],
                    "password": creds["password"]
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    user = data.get('user', {})
                    print(f"✅ Login successful!")
                    print(f"   👤 User: {user.get('first_name')} {user.get('last_name')}")
                    print(f"   🎭 Role: {user.get('role')} ({user.get('role_display')})")
                    print(f"   🔗 Redirect: {data.get('redirect_url')}")
                    
                    # Verify expected role
                    if user.get('role') == creds['expected_role']:
                        print(f"   ✅ Role matches expected: {creds['expected_role']}")
                    else:
                        print(f"   ⚠️  Role mismatch: got {user.get('role')}, expected {creds['expected_role']}")
                else:
                    print(f"❌ Login failed: {data.get('error')}")
            else:
                print(f"❌ HTTP Error {response.status_code}: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection failed - make sure Django server is running")
            print("   Run: python manage.py runserver")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    print("🚀 ITS LOGIN TESTER")
    print("=" * 50)
    print("This script tests the ITS login authentication backend fix")
    print("Make sure Django server is running on http://127.0.0.1:8000")
    print()
    
    test_its_login()
    
    print(f"\n💡 Manual Testing:")
    print("1. Visit: http://127.0.0.1:8000/accounts/its-login/")
    print("2. Use any test credentials from above")
    print("3. Should login successfully without backend errors")

if __name__ == "__main__":
    main()