#!/usr/bin/env python
"""
Test ITS data display in profile pages
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

def test_its_data_display():
    """Test ITS data display for different user types"""
    print("🔍 TESTING ITS DATA DISPLAY")
    print("=" * 50)
    
    client = Client()
    
    # Test different user roles
    test_roles = ['admin', 'doctor', 'patient', 'aamil', 'student']
    
    for role in test_roles:
        print(f"\n🧪 Testing {role.upper()} profile:")
        
        # Get user for this role
        if role == 'admin':
            user = User.objects.filter(is_superuser=True).first()
        else:
            user = User.objects.filter(role=role).first()
        
        if not user:
            print(f"❌ No {role} user found")
            continue
        
        print(f"User: {user.get_full_name()} (ITS: {user.its_id})")
        print(f"Sync status: {user.its_sync_status}")
        print(f"Last sync: {user.its_last_sync}")
        print(f"Occupation: {user.occupation}")
        print(f"Address: {user.address}")
        
        # Login
        login_response = client.post('/accounts/login/', {
            'its_id': user.its_id,
            'password': 'pass1234'
        })
        
        if login_response.status_code not in [200, 302]:
            print(f"❌ {role} login failed")
            continue
        
        # Check profile page
        profile_response = client.get('/accounts/profile/')
        
        if profile_response.status_code == 200:
            content = profile_response.content.decode()
            
            # Check for ITS data display
            if 'No ITS Data Available' in content:
                print("❌ Profile shows 'No ITS Data Available'")
                
                # Check if its_sync_available is in the template
                if 'its_sync_available' in content:
                    print("⚠️  its_sync_available variable is present but condition is failing")
                else:
                    print("❌ its_sync_available variable is missing from template")
                    
            elif 'ITS Profile Data' in content and user.get_full_name() in content:
                print("✅ ITS data is being displayed correctly")
                
                # Check for specific data fields
                data_fields = [
                    ('Full Name', user.get_full_name()),
                    ('Occupation', user.occupation),
                    ('Address', user.address),
                    ('Gender', user.gender),
                    ('Mobile', user.mobile_number),
                ]
                
                for field_name, field_value in data_fields:
                    if field_value and field_value in content:
                        print(f"  ✅ {field_name}: {field_value}")
                    elif field_value:
                        print(f"  ⚠️  {field_name}: {field_value} (not displayed)")
                    else:
                        print(f"  ➖ {field_name}: No data")
                        
            else:
                print("⚠️  ITS data section unclear")
            
            # Check for sync button
            if 'Sync ITS Data' in content:
                print("✅ Sync button is present")
            else:
                print("❌ Sync button is missing")
                
        else:
            print(f"❌ Profile page failed to load: {profile_response.status_code}")
        
        client.logout()
    
    print(f"\n✅ ITS DATA DISPLAY TESTING COMPLETED")
    return True

if __name__ == "__main__":
    test_its_data_display()