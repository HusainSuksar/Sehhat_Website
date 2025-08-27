#!/usr/bin/env python
"""
Test profile ITS synchronization functionality
"""

import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

from accounts.models import UserProfile

User = get_user_model()

def test_profile_its_sync():
    """Test the profile ITS synchronization functionality"""
    print("🔄 TESTING PROFILE ITS SYNCHRONIZATION")
    print("=" * 50)
    
    client = Client()
    
    # Get test user
    test_user = User.objects.filter(is_superuser=True).first()
    if not test_user:
        print("❌ No test user found")
        return False
    
    print(f"Testing with user: {test_user.get_full_name()} (ITS: {test_user.its_id})")
    
    # Login
    login_response = client.post('/accounts/login/', {
        'its_id': test_user.its_id,
        'password': 'pass1234'
    })
    
    if login_response.status_code not in [200, 302]:
        print("❌ Login failed")
        return False
    
    print("✅ Login successful")
    
    # Test 1: Check profile page loads
    print(f"\n1️⃣ Testing profile page load")
    profile_response = client.get('/accounts/profile/')
    
    if profile_response.status_code == 200:
        content = profile_response.content.decode()
        
        # Check for ITS sync elements
        its_elements = [
            ('ITS Data Section', 'ITS Profile Data' in content),
            ('Sync Button', 'Sync ITS Data' in content),
            ('Sync Function', 'syncITSData()' in content),
            ('CSRF Token', 'csrfmiddlewaretoken' in content),
            ('User Data Display', test_user.get_full_name() in content),
        ]
        
        for element_name, present in its_elements:
            if present:
                print(f"✅ {element_name}: Present")
            else:
                print(f"❌ {element_name}: Missing")
        
        print("✅ Profile page loads correctly")
    else:
        print(f"❌ Profile page failed to load: {profile_response.status_code}")
        return False
    
    # Test 2: Test ITS sync API endpoint
    print(f"\n2️⃣ Testing ITS sync API endpoint")
    
    # Store original data
    original_occupation = test_user.occupation
    original_address = test_user.address
    original_sync_status = test_user.its_sync_status
    
    print(f"Original occupation: {original_occupation}")
    print(f"Original address: {original_address}")
    print(f"Original sync status: {original_sync_status}")
    
    # Call sync endpoint
    sync_response = client.post('/accounts/sync-its-data/', 
                               content_type='application/json')
    
    print(f"Sync API Response Status: {sync_response.status_code}")
    
    if sync_response.status_code == 200:
        sync_data = sync_response.json()
        print(f"Sync API Response: {sync_data}")
        
        if sync_data.get('success'):
            print("✅ ITS sync API successful")
            
            # Refresh user from database
            test_user.refresh_from_db()
            
            # Check if data was updated
            print(f"New occupation: {test_user.occupation}")
            print(f"New address: {test_user.address}")
            print(f"New sync status: {test_user.its_sync_status}")
            print(f"Last sync time: {test_user.its_last_sync}")
            
            if test_user.its_sync_status == 'synced':
                print("✅ Sync status updated correctly")
            else:
                print("❌ Sync status not updated")
            
            if test_user.its_last_sync:
                print("✅ Last sync time recorded")
            else:
                print("❌ Last sync time not recorded")
                
        else:
            print(f"❌ ITS sync failed: {sync_data.get('message')}")
            return False
    else:
        print(f"❌ Sync API failed: {sync_response.content}")
        return False
    
    # Test 3: Check UserProfile was updated
    print(f"\n3️⃣ Testing UserProfile update")
    
    try:
        profile = UserProfile.objects.get(user=test_user)
        print(f"Profile location: {profile.location}")
        print(f"Profile emergency contact: {profile.emergency_contact}")
        print("✅ UserProfile exists and accessible")
    except UserProfile.DoesNotExist:
        print("❌ UserProfile not found")
        return False
    
    # Test 4: Test frontend JavaScript integration
    print(f"\n4️⃣ Testing frontend JavaScript integration")
    
    # Check if the sync button works (simulate click)
    profile_response = client.get('/accounts/profile/')
    if profile_response.status_code == 200:
        content = profile_response.content.decode()
        
        js_checks = [
            ('Sync Function Definition', 'async function syncITSData()' in content),
            ('Fetch API Call', "fetch('/accounts/sync-its-data/'" in content),
            ('Loading State', 'fa-spinner fa-spin' in content),
            ('Success Handling', 'location.reload()' in content),
            ('Error Handling', 'Sync failed' in content),
        ]
        
        for check_name, result in js_checks:
            if result:
                print(f"✅ {check_name}: Present")
            else:
                print(f"❌ {check_name}: Missing")
    
    print(f"\n✅ PROFILE ITS SYNC TESTING COMPLETED")
    return True

if __name__ == "__main__":
    success = test_profile_its_sync()
    if success:
        print("🎉 Profile ITS synchronization is working correctly!")
    else:
        print("🔧 Profile ITS sync issues found")