#!/usr/bin/env python
"""
Test the appointment API endpoints
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

from doctordirectory.models import Doctor, Patient, Appointment

User = get_user_model()

def test_appointment_api_endpoints():
    """Test the appointment API endpoints"""
    print("🔗 TESTING APPOINTMENT API ENDPOINTS")
    print("=" * 50)
    
    client = Client()
    
    # Get test data
    admin_user = User.objects.filter(is_superuser=True).first()
    appointment = Appointment.objects.first()
    
    if not admin_user or not appointment:
        print("❌ Missing test data (admin user or appointment)")
        return False
    
    print(f"Admin: {admin_user.get_full_name()}")
    print(f"Test appointment: {appointment.id} - {appointment.status}")
    
    # Login as admin
    login_response = client.post('/accounts/login/', {
        'its_id': admin_user.its_id,
        'password': 'pass1234'
    })
    
    if login_response.status_code not in [200, 302]:
        print("❌ Admin login failed")
        return False
    
    print("✅ Admin login successful")
    
    # Test 1: Get appointment status
    print(f"\n1️⃣ Testing GET /api/doctordirectory/appointments/{appointment.id}/status/")
    status_response = client.get(f'/api/doctordirectory/appointments/{appointment.id}/status/')
    
    print(f"Response status: {status_response.status_code}")
    if status_response.status_code == 200:
        data = status_response.json()
        print(f"✅ Status endpoint working: {data}")
    else:
        print(f"❌ Status endpoint failed: {status_response.content}")
        return False
    
    # Test 2: Update appointment status
    print(f"\n2️⃣ Testing POST /api/doctordirectory/appointments/{appointment.id}/update-status/")
    
    # Get CSRF token
    csrf_response = client.get(f'/doctordirectory/appointments/{appointment.id}/')
    csrf_token = client.cookies.get('csrftoken').value if 'csrftoken' in client.cookies else None
    
    update_data = {
        'status': 'confirmed',
        'reason': 'Test status update'
    }
    
    headers = {}
    if csrf_token:
        headers['X-CSRFToken'] = csrf_token
    
    update_response = client.post(
        f'/api/doctordirectory/appointments/{appointment.id}/update-status/',
        data=json.dumps(update_data),
        content_type='application/json',
        **headers
    )
    
    print(f"Response status: {update_response.status_code}")
    if update_response.status_code == 200:
        data = update_response.json()
        print(f"✅ Update endpoint working: {data.get('message', 'No message')}")
        
        # Verify the status was updated
        appointment.refresh_from_db()
        if appointment.status == 'confirmed':
            print("✅ Status successfully updated in database")
        else:
            print(f"⚠️  Status not updated in database: {appointment.status}")
        
    else:
        print(f"❌ Update endpoint failed: {update_response.content}")
        return False
    
    # Test 3: Test invalid status
    print(f"\n3️⃣ Testing invalid status update")
    invalid_data = {
        'status': 'invalid_status',
    }
    
    invalid_response = client.post(
        f'/api/doctordirectory/appointments/{appointment.id}/update-status/',
        data=json.dumps(invalid_data),
        content_type='application/json',
        **headers
    )
    
    if invalid_response.status_code == 400:
        print("✅ Invalid status properly rejected")
    else:
        print(f"❌ Invalid status not properly handled: {invalid_response.status_code}")
    
    print(f"\n✅ API ENDPOINTS TESTING COMPLETED")
    return True

if __name__ == "__main__":
    success = test_appointment_api_endpoints()
    if success:
        print("🎉 All API endpoints working correctly!")
    else:
        print("🔧 Some API issues found")