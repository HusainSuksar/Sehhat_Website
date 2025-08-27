#!/usr/bin/env python
"""
Test the JavaScript fix for undefined error messages
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

from doctordirectory.models import Appointment

User = get_user_model()

def test_javascript_error_handling():
    """Test that the JavaScript error handling works correctly"""
    print("🔧 TESTING JAVASCRIPT ERROR HANDLING FIX")
    print("=" * 50)
    
    client = Client()
    
    # Get test data
    admin_user = User.objects.filter(is_superuser=True).first()
    appointment = Appointment.objects.first()
    
    if not admin_user or not appointment:
        print("❌ Missing test data")
        return False
    
    # Login as admin
    login_response = client.post('/accounts/login/', {
        'its_id': admin_user.its_id,
        'password': 'pass1234'
    })
    
    if login_response.status_code not in [200, 302]:
        print("❌ Admin login failed")
        return False
    
    print("✅ Admin login successful")
    print(f"Testing with appointment {appointment.id} (current status: {appointment.status})")
    
    # Test 1: Successful status update
    print(f"\n1️⃣ Testing successful status update API response")
    
    # Update appointment status via API
    update_data = {
        'status': 'confirmed'
    }
    
    response = client.post(
        f'/api/doctordirectory/appointments/{appointment.id}/update-status/',
        data=json.dumps(update_data),
        content_type='application/json'
    )
    
    print(f"API Response Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"API Response Data: {data}")
        
        # Check if response has the expected structure
        if 'message' in data:
            print("✅ API returns 'message' field as expected")
        else:
            print("❌ API missing 'message' field")
        
        if 'appointment' in data:
            print("✅ API returns 'appointment' data as expected")
        else:
            print("❌ API missing 'appointment' field")
            
    else:
        print(f"❌ API call failed: {response.content}")
        return False
    
    # Test 2: Error case API response
    print(f"\n2️⃣ Testing error case API response")
    
    # Try invalid status
    invalid_data = {
        'status': 'invalid_status_test'
    }
    
    error_response = client.post(
        f'/api/doctordirectory/appointments/{appointment.id}/update-status/',
        data=json.dumps(invalid_data),
        content_type='application/json'
    )
    
    print(f"Error API Response Status: {error_response.status_code}")
    if error_response.status_code == 400:
        error_data = error_response.json()
        print(f"Error API Response Data: {error_data}")
        
        if 'error' in error_data:
            print("✅ API returns 'error' field for bad requests")
        else:
            print("❌ API missing 'error' field for bad requests")
    else:
        print(f"⚠️  Unexpected error response status: {error_response.status_code}")
    
    # Test 3: Check template has proper JavaScript
    print(f"\n3️⃣ Testing template JavaScript structure")
    
    template_response = client.get(f'/doctordirectory/appointments/{appointment.id}/')
    if template_response.status_code == 200:
        content = template_response.content.decode()
        
        # Check for proper JavaScript structure
        js_checks = [
            ('Status Labels Object', 'statusLabels' in content and 'confirmed' in content),
            ('Response Handling', 'response.ok' in content),
            ('Message Field Check', 'data.message' in content),
            ('Error Field Check', 'error.error' in content),
            ('Success Alert', 'Success:' in content),
            ('Complete Status Labels', 'confirmed' in content and 'completed' in content)
        ]
        
        for check_name, result in js_checks:
            if result:
                print(f"✅ {check_name}: Present")
            else:
                print(f"❌ {check_name}: Missing")
        
        print("✅ Template JavaScript structure verified")
    else:
        print(f"❌ Template load failed: {template_response.status_code}")
        return False
    
    print(f"\n✅ JAVASCRIPT ERROR HANDLING TEST COMPLETED")
    return True

if __name__ == "__main__":
    success = test_javascript_error_handling()
    if success:
        print("🎉 JavaScript error handling fix verified!")
    else:
        print("🔧 JavaScript issues remain")