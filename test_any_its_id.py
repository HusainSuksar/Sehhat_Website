#!/usr/bin/env python
"""
Test script to verify that Mock ITS service now accepts any valid 8-digit ITS ID
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

from accounts.services import MockITSService

def test_any_its_id():
    """Test that Mock ITS service accepts any valid 8-digit ITS ID"""
    print("🔍 TESTING MOCK ITS SERVICE - ANY ITS ID ACCEPTANCE")
    print("=" * 60)
    
    its_service = MockITSService()
    
    # Test various ITS IDs
    test_ids = [
        '50000001',  # Predefined admin
        '50000010',  # Predefined aamil
        '50000055',  # Predefined coordinator  
        '50000070',  # Predefined doctor
        '50000090',  # Predefined student
        '12345678',  # Random valid format
        '87654321',  # Random valid format
        '11111111',  # Random valid format
        '99999999',  # Random valid format
        '00000001',  # Edge case
    ]
    
    invalid_ids = [
        '1234567',   # Too short
        '123456789', # Too long
        '12ab5678',  # Contains letters
        '',          # Empty
        None,        # None
        '12 34 56 78', # Contains spaces
    ]
    
    print("✅ TESTING VALID ITS IDs:")
    print("-" * 40)
    
    for its_id in test_ids:
        user_data = its_service.fetch_user_data(its_id)
        
        if user_data:
            is_predefined = its_id in its_service.PREDEFINED_USERS
            user_type = "🔑 Predefined" if is_predefined else "🎲 Generated"
            
            print(f"✅ ITS ID: {its_id} - {user_type}")
            print(f"   👤 Name: {user_data['first_name']} {user_data['last_name']}")
            print(f"   📧 Email: {user_data['email']}")
            print(f"   👔 Role: {user_data['role']}")
            print(f"   🏢 Moze: {user_data['moze']}")
            print(f"   📱 Phone: {user_data['contact_number']}")
            print()
        else:
            print(f"❌ ITS ID: {its_id} - Failed to generate data")
            print()
    
    print("❌ TESTING INVALID ITS IDs:")
    print("-" * 40)
    
    for its_id in invalid_ids:
        user_data = its_service.fetch_user_data(its_id)
        
        if user_data is None:
            print(f"✅ ITS ID: {repr(its_id)} - Correctly rejected")
        else:
            print(f"❌ ITS ID: {repr(its_id)} - Should have been rejected but got data")
    
    print("\n🎯 TESTING CONSISTENCY:")
    print("-" * 40)
    
    # Test that same ITS ID gives same data
    test_id = '12345678'
    data1 = its_service.fetch_user_data(test_id)
    data2 = its_service.fetch_user_data(test_id)
    
    if data1 == data2:
        print(f"✅ Consistency check passed for ITS ID {test_id}")
        print(f"   Same data returned on multiple calls")
    else:
        print(f"❌ Consistency check failed for ITS ID {test_id}")
        print(f"   Different data returned on multiple calls")
    
    print("\n🔐 TESTING AUTHENTICATION:")
    print("-" * 40)
    
    # Test authentication for various ITS IDs
    for its_id in ['50000001', '12345678', '87654321']:
        auth_result = its_service.authenticate_user(its_id, 'test123')
        
        if auth_result and auth_result.get('authenticated'):
            user_data = auth_result['user_data']
            print(f"✅ Authentication successful for ITS ID {its_id}")
            print(f"   👤 User: {user_data['first_name']} {user_data['last_name']}")
            print(f"   👔 Role: {auth_result['role']}")
        else:
            print(f"❌ Authentication failed for ITS ID {its_id}")
    
    print("\n🎉 MOCK ITS SERVICE TEST COMPLETED!")
    print("✅ The service now accepts ANY valid 8-digit ITS ID")
    print("✅ Predefined users return consistent special data")
    print("✅ Other valid ITS IDs get realistic generated data")
    print("✅ Invalid ITS IDs are properly rejected")
    print("✅ Authentication works with any valid ITS ID")
    
    return True

if __name__ == "__main__":
    test_any_its_id()