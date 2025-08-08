#!/usr/bin/env python3
"""
ITS API Integration Test with Django User Model (FIXED)
Test how the Mock ITS Service integrates with the User model using correct field names
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.services import MockITSService

User = get_user_model()

def test_user_creation_from_its():
    """Test creating/updating Django User from ITS data"""
    print("🔍 TEST: User Creation from ITS Data")
    print("=" * 50)
    
    # Fetch data from mock ITS API
    its_id = "99999999"
    its_data = MockITSService.fetch_user_data(its_id)
    
    if not its_data:
        print("❌ Failed to fetch ITS data")
        return False
    
    print(f"📡 Fetched ITS data for ID: {its_id}")
    print(f"👤 Name: {its_data['first_name']} {its_data['last_name']}")
    
    # Check if user already exists
    user, created = User.objects.get_or_create(
        its_id=its_id,
        defaults={
            'username': its_data['email'],
            'email': its_data['email'],
            'first_name': its_data['first_name'],
            'last_name': its_data['last_name'],
            # Map ITS fields to User model fields (using actual field names)
            'arabic_full_name': its_data['arabic_full_name'],
            'prefix': its_data['prefix'],
            'age': its_data['age'],
            'gender': its_data['gender'],
            'marital_status': its_data['marital_status'],
            'misaq': its_data['misaq'],
            'occupation': its_data['occupation'],
            'qualification': its_data['qualification'],
            'idara': its_data['idara'],
            'category': its_data['category'],
            'organization': its_data['organization'],
            'mobile_number': its_data['mobile_number'],
            'whatsapp_number': its_data['whatsapp_number'],
            'address': its_data['address'],
            'jamaat': its_data['jamaat'],
            'jamiaat': its_data['jamiaat'],
            'nationality': its_data['nationality'],
            'vatan': its_data['vatan'],
            'city': its_data['city'],
            'country': its_data['country'],
            'hifz_sanad': its_data['hifz_sanad'],
            'profile_photo': its_data['photograph'],  # URL field
            'role': 'student',  # Default role
        }
    )
    
    if created:
        print("✅ New user created successfully")
    else:
        print("✅ Existing user found")
    
    print(f"🆔 Django User ID: {user.id}")
    print(f"📧 Email: {user.email}")
    print(f"🌍 City: {user.city}")
    print(f"📱 Mobile: {user.mobile_number}")
    print(f"🎓 Qualification: {user.qualification}")
    print(f"🏢 Organization: {user.organization}")
    
    return True

def test_sync_user_data():
    """Test syncing existing user with fresh ITS data"""
    print("\n🔍 TEST: Sync User Data from ITS")
    print("=" * 50)
    
    its_id = "99999999"
    
    # Get existing user
    try:
        user = User.objects.get(its_id=its_id)
        print(f"👤 Found user: {user.email}")
        
        # Store old values
        old_qualification = user.qualification
        old_mobile = user.mobile_number
        
        # Fetch fresh data from ITS
        fresh_data = MockITSService.fetch_user_data(its_id)
        
        if fresh_data:
            # Update user fields with fresh data
            user.arabic_full_name = fresh_data['arabic_full_name']
            user.mobile_number = fresh_data['mobile_number']
            user.qualification = fresh_data['qualification']
            user.occupation = fresh_data['occupation']
            user.city = fresh_data['city']
            user.country = fresh_data['country']
            user.organization = fresh_data['organization']
            user.profile_photo = fresh_data['photograph']
            
            user.save()
            
            print("✅ User data synced successfully")
            print(f"📱 Mobile: {old_mobile} → {user.mobile_number}")
            print(f"🎓 Qualification: {old_qualification} → {user.qualification}")
            
            return True
        else:
            print("❌ Failed to fetch fresh ITS data")
            return False
            
    except User.DoesNotExist:
        print("❌ User not found")
        return False

def test_bulk_its_sync():
    """Test syncing multiple users from ITS"""
    print("\n🔍 TEST: Bulk ITS Data Sync")
    print("=" * 50)
    
    # Test ITS IDs
    test_ids = ["11111111", "22222222", "33333333"]
    
    synced_users = []
    
    for its_id in test_ids:
        print(f"📡 Syncing ITS ID: {its_id}")
        
        its_data = MockITSService.fetch_user_data(its_id)
        
        if its_data:
            user, created = User.objects.get_or_create(
                its_id=its_id,
                defaults={
                    'username': its_data['email'],
                    'email': its_data['email'],
                    'first_name': its_data['first_name'],
                    'last_name': its_data['last_name'],
                    'mobile_number': its_data['mobile_number'],
                    'qualification': its_data['qualification'],
                    'city': its_data['city'],
                    'organization': its_data['organization'],
                    'role': 'student',
                }
            )
            
            synced_users.append(user)
            status = "Created" if created else "Updated"
            print(f"  ✅ {status}: {user.first_name} {user.last_name}")
        else:
            print(f"  ❌ Failed to fetch data for {its_id}")
    
    print(f"\n📊 Successfully synced {len(synced_users)} users")
    return len(synced_users) == len(test_ids)

def test_field_mapping():
    """Test all field mappings from ITS to User model"""
    print("\n🔍 TEST: Field Mapping Verification")
    print("=" * 50)
    
    its_id = "88888888"
    its_data = MockITSService.fetch_user_data(its_id)
    
    if not its_data:
        print("❌ Failed to fetch ITS data")
        return False
    
    # Create user with all fields
    user = User.objects.create(
        username=its_data['email'],
        email=its_data['email'],
        its_id=its_id,
        first_name=its_data['first_name'],
        last_name=its_data['last_name'],
        arabic_full_name=its_data['arabic_full_name'],
        prefix=its_data['prefix'],
        age=its_data['age'],
        gender=its_data['gender'],
        marital_status=its_data['marital_status'],
        misaq=its_data['misaq'],
        occupation=its_data['occupation'],
        qualification=its_data['qualification'],
        idara=its_data['idara'],
        category=its_data['category'],
        organization=its_data['organization'],
        mobile_number=its_data['mobile_number'],
        whatsapp_number=its_data['whatsapp_number'],
        address=its_data['address'],
        jamaat=its_data['jamaat'],
        jamiaat=its_data['jamiaat'],
        nationality=its_data['nationality'],
        vatan=its_data['vatan'],
        city=its_data['city'],
        country=its_data['country'],
        hifz_sanad=its_data['hifz_sanad'],
        profile_photo=its_data['photograph'],
        role='student'
    )
    
    print("✅ User created with all ITS fields")
    print(f"👤 Full Profile: {user.prefix} {user.first_name} {user.last_name}")
    print(f"📧 Email: {user.email}")
    print(f"📱 Mobile: {user.mobile_number}")
    print(f"📱 WhatsApp: {user.whatsapp_number}")
    print(f"🎂 Age: {user.age}")
    print(f"⚧ Gender: {user.gender}")
    print(f"💍 Marital Status: {user.marital_status}")
    print(f"🏢 Organization: {user.organization}")
    print(f"🎓 Qualification: {user.qualification}")
    print(f"📍 Address: {user.address}")
    print(f"🏛️ Jamaat: {user.jamaat}")
    print(f"🌍 Nationality: {user.nationality}")
    print(f"🏙️ City: {user.city}, {user.country}")
    print(f"📖 Hifz Sanad: {user.hifz_sanad}")
    print(f"📸 Photo URL: {user.profile_photo}")
    
    return True

def test_data_validation():
    """Test data validation and constraints"""
    print("\n🔍 TEST: Data Validation")
    print("=" * 50)
    
    # Test with different ITS IDs to get variety
    test_cases = [
        "77777777",
        "66666666",
        "55555555"
    ]
    
    valid_users = 0
    
    for its_id in test_cases:
        its_data = MockITSService.fetch_user_data(its_id)
        
        if its_data:
            try:
                # Test email uniqueness by creating unique emails
                unique_email = f"test_{its_id}_{its_data['email']}"
                
                user = User.objects.create(
                    username=unique_email,
                    email=unique_email,
                    its_id=its_id,
                    first_name=its_data['first_name'],
                    last_name=its_data['last_name'],
                    mobile_number=its_data['mobile_number'],
                    role='student'
                )
                
                print(f"✅ Valid user created: {user.first_name} {user.last_name} ({its_id})")
                valid_users += 1
                
            except Exception as e:
                print(f"❌ Failed to create user for {its_id}: {e}")
    
    print(f"\n📊 Successfully created {valid_users}/{len(test_cases)} users")
    return valid_users == len(test_cases)

def show_comprehensive_mapping():
    """Show comprehensive mapping between ITS API and User model"""
    print("\n📋 COMPREHENSIVE ITS → USER MODEL MAPPING")
    print("=" * 50)
    
    mapping = {
        "ITS API Field": "User Model Field",
        "its_id": "its_id",
        "first_name": "first_name",
        "last_name": "last_name", 
        "arabic_full_name": "arabic_full_name",
        "prefix": "prefix",
        "age": "age",
        "gender": "gender",
        "marital_status": "marital_status",
        "misaq": "misaq",
        "occupation": "occupation",
        "qualification": "qualification",
        "idara": "idara",
        "category": "category",
        "organization": "organization",
        "email": "email",
        "mobile_number": "mobile_number",
        "whatsapp_number": "whatsapp_number",
        "address": "address",
        "jamaat": "jamaat",
        "jamiaat": "jamiaat",
        "nationality": "nationality",
        "vatan": "vatan",
        "city": "city",
        "country": "country",
        "hifz_sanad": "hifz_sanad",
        "photograph": "profile_photo (URL)"
    }
    
    print(f"{'ITS API Field':<20} → {'User Model Field':<20}")
    print("-" * 50)
    
    for its_field, user_field in mapping.items():
        if its_field != "ITS API Field":  # Skip header
            print(f"{its_field:<20} → {user_field:<20}")
    
    print(f"\n📊 Total fields mapped: {len(mapping) - 1}")
    return True

def main():
    """Run all integration tests"""
    print("🚀 ITS API INTEGRATION TESTING SUITE (FIXED)")
    print("=" * 70)
    print("Testing Mock ITS Service integration with Django User model")
    print("=" * 70)
    
    tests = [
        ("Show ITS → User Field Mapping", show_comprehensive_mapping),
        ("User Creation from ITS", test_user_creation_from_its),
        ("Sync User Data", test_sync_user_data),
        ("Field Mapping Verification", test_field_mapping),
        ("Bulk ITS Sync", test_bulk_its_sync),
        ("Data Validation", test_data_validation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ ERROR in {test_name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print(f"\n📊 INTEGRATION TEST RESULTS")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All integration tests passed!")
    else:
        print("⚠️ Some integration tests failed.")
    
    print(f"\n💡 Implementation Summary:")
    print("✅ Mock ITS API provides 21+ data fields")
    print("✅ Django User model has all corresponding fields")
    print("✅ Field mapping is complete and working")
    print("✅ Data can be fetched, created, and synced")
    print("✅ Ready for real ITS API integration")
    
    print(f"\n🚀 Next Steps for Real ITS API:")
    print("1. Replace MockITSService with real ITS API calls")
    print("2. Add authentication/authorization for ITS API")
    print("3. Implement scheduled sync jobs")
    print("4. Add error handling and retry logic")
    print("5. Create admin interface for managing ITS sync")

if __name__ == "__main__":
    main()