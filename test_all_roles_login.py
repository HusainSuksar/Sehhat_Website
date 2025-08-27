#!/usr/bin/env python
"""
Quick test to verify all user roles can still login after middleware fix
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

def test_all_roles():
    """Test that all user roles can login"""
    print("🔍 TESTING ALL USER ROLES LOGIN")
    print("=" * 50)
    
    roles_to_test = ['aamil', 'moze_coordinator', 'doctor', 'student', 'patient', 'badri_mahal_admin']
    
    client = Client()
    
    for role in roles_to_test:
        user = User.objects.filter(role=role).first()
        if user:
            print(f"\n🧪 Testing {role.upper()}: {user.get_full_name()}")
            
            login_response = client.post('/accounts/login/', {
                'its_id': user.its_id,
                'password': 'pass1234'
            }, follow=True)
            
            if login_response.status_code == 200:
                if hasattr(login_response, 'wsgi_request') and login_response.wsgi_request.user.is_authenticated:
                    print(f"   ✅ Login successful")
                    final_url = login_response.redirect_chain[-1][0] if login_response.redirect_chain else "No redirect"
                    print(f"   🔄 Final URL: {final_url}")
                else:
                    print(f"   ❌ Login failed - not authenticated")
            else:
                print(f"   ❌ Login failed - status {login_response.status_code}")
            
            client.logout()
        else:
            print(f"\n⚠️  No {role} user found")
    
    print(f"\n✅ All role login test completed!")

if __name__ == "__main__":
    test_all_roles()