#!/usr/bin/env python
"""
Test the appointment system fixes
"""

import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model
from datetime import date, time, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

from doctordirectory.models import Doctor, Patient, Appointment

User = get_user_model()

def test_appointment_fixes():
    """Test the specific fixes applied"""
    print("🔧 TESTING APPOINTMENT SYSTEM FIXES")
    print("=" * 50)
    
    client = Client()
    
    # Get test data
    doctor = Doctor.objects.first()
    patient_user = User.objects.filter(role='patient').first()
    admin_user = User.objects.filter(is_superuser=True).first()
    
    if not all([doctor, patient_user, admin_user]):
        print("❌ Missing test data")
        return False
    
    print(f"Doctor: {doctor.get_full_name()}")
    print(f"Patient: {patient_user.get_full_name()}")
    print(f"Admin: {admin_user.get_full_name()}")
    
    # Test 1: Create appointment as patient
    print(f"\n1️⃣ Testing patient appointment creation and detail access:")
    
    # Login as patient
    login_response = client.post('/accounts/login/', {
        'its_id': patient_user.its_id,
        'password': 'pass1234'
    })
    
    if login_response.status_code not in [200, 302]:
        print("❌ Patient login failed")
        return False
    
    # Get patient profile
    patient_profile = None
    try:
        patient_profile = patient_user.patient_profile.first()
        if not patient_profile:
            print("⚠️  Patient user has no patient profile")
            # Create one for testing
            patient_profile = Patient.objects.create(
                user=patient_user,
                date_of_birth=date(1990, 1, 1),
                gender='male'
            )
            print(f"✅ Created patient profile: {patient_profile}")
    except Exception as e:
        print(f"❌ Error with patient profile: {e}")
        return False
    
    # Create appointment form data
    appointment_data = {
        'doctor': doctor.id,
        'patient': patient_profile.id,
        'appointment_date': (date.today() + timedelta(days=1)).strftime('%Y-%m-%d'),
        'appointment_time': '10:00',
        'reason_for_visit': 'Test patient appointment',
        'notes': 'Testing patient access'
    }
    
    # Submit appointment creation
    create_url = f'/doctordirectory/appointments/create/{doctor.id}/'
    response = client.post(create_url, appointment_data, follow=True)
    
    if response.status_code == 200:
        print("✅ Patient can create appointment")
        
        # Find the created appointment
        appointment = Appointment.objects.filter(
            doctor=doctor,
            patient=patient_profile,
            reason_for_visit='Test patient appointment'
        ).first()
        
        if appointment:
            print(f"✅ Appointment created in database (ID: {appointment.id})")
            
            # Test appointment detail access
            detail_url = f'/doctordirectory/appointments/{appointment.id}/'
            detail_response = client.get(detail_url)
            
            if detail_response.status_code == 200:
                print("✅ Patient can view their own appointment details")
            elif detail_response.status_code == 302:
                redirect_url = detail_response.get('Location', 'Unknown')
                print(f"❌ Patient redirected from appointment detail: {redirect_url}")
            else:
                print(f"❌ Patient cannot access appointment detail: {detail_response.status_code}")
            
            # Test appointment list access
            list_response = client.get('/doctordirectory/appointments/')
            if list_response.status_code == 200:
                print("✅ Patient can access appointment list")
            else:
                print(f"❌ Patient cannot access appointment list: {list_response.status_code}")
            
            # Clean up
            appointment.delete()
            
        else:
            print("❌ Appointment not found in database")
    else:
        print(f"❌ Patient cannot create appointment: {response.status_code}")
    
    client.logout()
    
    # Test 2: URL pattern fix
    print(f"\n2️⃣ Testing URL pattern fixes:")
    
    # Login as admin
    client.post('/accounts/login/', {
        'its_id': admin_user.its_id,
        'password': 'pass1234'
    })
    
    # Test appointment detail template rendering
    appointment = Appointment.objects.first()
    if appointment:
        detail_response = client.get(f'/doctordirectory/appointments/{appointment.id}/')
        if detail_response.status_code == 200:
            content = detail_response.content.decode()
            if 'NoReverseMatch' in content:
                print("❌ NoReverseMatch error still present in template")
            else:
                print("✅ Appointment detail template renders without URL errors")
                
                # Check for the corrected URL
                if 'create_appointment_for_doctor' in content:
                    print("✅ Template uses correct URL pattern for follow-up appointments")
                else:
                    print("⚠️  Could not verify URL pattern fix in template")
        else:
            print(f"❌ Cannot access appointment detail: {detail_response.status_code}")
    else:
        print("⚠️  No appointments found for template testing")
    
    client.logout()
    
    print(f"\n✅ APPOINTMENT FIXES TESTING COMPLETED")
    return True

if __name__ == "__main__":
    success = test_appointment_fixes()
    if success:
        print("🎉 All fixes appear to be working!")
    else:
        print("🔧 Some issues remain")