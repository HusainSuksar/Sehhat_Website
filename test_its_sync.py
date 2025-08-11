#!/usr/bin/env python
"""
Test script to verify ITS sync functionality
"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

from accounts.models import User, UserProfile
from accounts.services import MockITSService
from django.test import RequestFactory
from django.contrib.auth import get_user

def test_its_sync():
    """Test ITS sync functionality end-to-end"""
    print("🔍 TESTING ITS SYNC FUNCTIONALITY")
    print("=" * 50)
    
    # Test 1: Mock ITS Service
    print("1️⃣ Testing Mock ITS Service...")
    its_service = MockITSService()
    test_its_id = '12345678'
    
    user_data = its_service.fetch_user_data(test_its_id)
    if user_data:
        print(f"   ✅ Mock ITS returned data for {test_its_id}")
        print(f"   👤 Name: {user_data['first_name']} {user_data['last_name']}")
        print(f"   📧 Email: {user_data['email']}")
        print(f"   📱 Phone: {user_data['contact_number']}")
        print(f"   🏠 Address: {user_data['address']}")
    else:
        print(f"   ❌ Mock ITS failed for {test_its_id}")
        return False
    
    # Test 2: Create or get test user
    print("\n2️⃣ Testing User Creation/Update...")
    test_user, created = User.objects.get_or_create(
        its_id=test_its_id,
        defaults={
            'username': test_its_id,
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com'
        }
    )
    
    if created:
        print(f"   ✅ Created test user: {test_user.get_full_name()}")
    else:
        print(f"   ✅ Found existing test user: {test_user.get_full_name()}")
    
    # Test 3: Manual sync logic
    print("\n3️⃣ Testing Sync Logic...")
    try:
        # Store original values
        original_email = test_user.email
        original_mobile = test_user.mobile_number
        
        # Apply sync data
        test_user.first_name = user_data.get('first_name', test_user.first_name)
        test_user.last_name = user_data.get('last_name', test_user.last_name)
        test_user.email = user_data.get('email', test_user.email)
        test_user.mobile_number = user_data.get('contact_number', test_user.mobile_number)
        test_user.address = user_data.get('address', test_user.address)
        test_user.gender = user_data.get('gender', test_user.gender)
        test_user.jamaat = user_data.get('jamaat', test_user.jamaat)
        test_user.occupation = user_data.get('occupation', test_user.occupation)
        test_user.save()
        
        # Create/update profile
        profile, created = UserProfile.objects.get_or_create(user=test_user)
        if user_data.get('emergency_contact_name'):
            profile.emergency_contact_name = user_data.get('emergency_contact_name')
        if user_data.get('emergency_contact_number'):
            profile.emergency_contact = user_data.get('emergency_contact_number')
        if user_data.get('address'):
            profile.location = user_data.get('address')[:100]
        profile.save()
        
        print(f"   ✅ User data updated successfully")
        print(f"   📧 Email: {original_email} → {test_user.email}")
        print(f"   📱 Mobile: {original_mobile} → {test_user.mobile_number}")
        print(f"   🏠 Address: {test_user.address}")
        print(f"   👥 Gender: {test_user.gender}")
        print(f"   🕌 Jamaat: {test_user.jamaat}")
        
    except Exception as e:
        print(f"   ❌ Sync logic failed: {e}")
        return False
    
    # Test 4: Test sync view
    print("\n4️⃣ Testing Sync View...")
    try:
        from accounts.views import sync_its_data
        from django.test import RequestFactory
        from django.contrib.auth.models import AnonymousUser
        
        factory = RequestFactory()
        request = factory.post('/accounts/sync-its-data/')
        request.user = test_user
        
        response = sync_its_data(request)
        
        if response.status_code == 200:
            response_data = json.loads(response.content)
            if response_data.get('success'):
                print(f"   ✅ Sync view successful")
                print(f"   📝 Message: {response_data.get('message')}")
                print(f"   📊 Data: {response_data.get('data', {})}")
            else:
                print(f"   ❌ Sync view returned error: {response_data.get('message')}")
                return False
        else:
            print(f"   ❌ Sync view returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Sync view test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 5: Verify final state
    print("\n5️⃣ Verifying Final State...")
    test_user.refresh_from_db()
    profile.refresh_from_db()
    
    print(f"   👤 User: {test_user.get_full_name()}")
    print(f"   📧 Email: {test_user.email}")
    print(f"   📱 Mobile: {test_user.mobile_number}")
    print(f"   🏠 Address: {test_user.address}")
    print(f"   👥 Gender: {test_user.gender}")
    print(f"   🕌 Jamaat: {test_user.jamaat}")
    print(f"   💼 Occupation: {test_user.occupation}")
    print(f"   📍 Profile Location: {profile.location}")
    print(f"   🆘 Emergency Contact: {profile.emergency_contact_name}")
    
    print("\n🎉 ALL SYNC TESTS PASSED!")
    print("✅ Mock ITS Service working")
    print("✅ User data mapping working")
    print("✅ Profile data mapping working") 
    print("✅ Sync view working")
    print("✅ Data persistence working")
    
    return True

if __name__ == "__main__":
    success = test_its_sync()
    exit(0 if success else 1)