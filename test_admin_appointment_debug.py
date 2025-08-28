#!/usr/bin/env python
"""
Debug script to test admin appointment booking functionality
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

from accounts.models import User
from doctordirectory.models import Doctor, Patient, Appointment
from doctordirectory.forms import AppointmentForm
from accounts.services import ITSService

def test_admin_appointment_booking():
    print("🔍 Testing Admin Appointment Booking")
    print("=" * 50)
    
    # 1. Check if admin user exists
    print("\n1. Checking Admin User:")
    try:
        admin_user = User.objects.filter(role='badri_mahal_admin').first()
        if admin_user:
            print(f"   ✅ Admin user found: {admin_user.its_id} - {admin_user.get_full_name()}")
            print(f"   ✅ is_admin: {admin_user.is_admin}")
        else:
            print("   ❌ No admin user found!")
            # Try to find any admin-like user
            admin_users = User.objects.filter(role__in=['admin', 'badri_mahal_admin'])
            if admin_users.exists():
                print(f"   Found {admin_users.count()} admin users:")
                for user in admin_users:
                    print(f"      - {user.its_id} - {user.role} - {user.get_full_name()}")
            return False
    except Exception as e:
        print(f"   ❌ Error checking admin user: {e}")
        return False
    
    # 2. Check available doctors
    print("\n2. Checking Available Doctors:")
    doctors = Doctor.objects.filter(is_available=True)[:5]
    if doctors.exists():
        print(f"   ✅ Found {doctors.count()} available doctors:")
        for doctor in doctors:
            print(f"      - {doctor.user.get_full_name()} (ID: {doctor.id})")
        test_doctor = doctors.first()
    else:
        print("   ❌ No available doctors found!")
        return False
    
    # 3. Check available patient ITS IDs
    print("\n3. Checking Available Patient ITS IDs:")
    patient_users = User.objects.filter(role='patient')[:5]
    if patient_users.exists():
        print(f"   ✅ Found {patient_users.count()} patient users:")
        for user in patient_users:
            print(f"      - {user.its_id} - {user.get_full_name()}")
        test_patient_its_id = patient_users.first().its_id
    else:
        print("   ❌ No patient users found!")
        return False
    
    # 4. Test ITS API lookup
    print(f"\n4. Testing ITS API Lookup for {test_patient_its_id}:")
    try:
        its_data = ITSService.fetch_user_data(test_patient_its_id)
        if its_data:
            print(f"   ✅ ITS data fetched successfully:")
            print(f"      - Name: {its_data.get('first_name')} {its_data.get('last_name')}")
            print(f"      - ITS ID: {its_data.get('its_id')}")
        else:
            print(f"   ❌ Failed to fetch ITS data for {test_patient_its_id}")
            return False
    except Exception as e:
        print(f"   ❌ Error fetching ITS data: {e}")
        return False
    
    # 5. Test form validation
    print(f"\n5. Testing Appointment Form Validation:")
    try:
        form_data = {
            'doctor': test_doctor.id,
            'patient_its_id': test_patient_its_id,
            'appointment_date': '2024-02-01',
            'appointment_time': '10:00',
            'reason_for_visit': 'Test appointment',
            'notes': 'Admin booking test'
        }
        
        form = AppointmentForm(data=form_data, doctor=test_doctor, user=admin_user)
        print(f"   Form created with data: {form_data}")
        
        if form.is_valid():
            print("   ✅ Form validation passed!")
            cleaned_data = form.cleaned_data
            print(f"   ✅ Patient assigned: {cleaned_data.get('patient')}")
        else:
            print("   ❌ Form validation failed!")
            print(f"   Errors: {form.errors}")
            print(f"   Non-field errors: {form.non_field_errors()}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing form: {e}")
        return False
    
    print("\n✅ All tests passed! Admin appointment booking should work.")
    return True

def show_debug_info():
    print("\n🔧 Debug Information:")
    print("=" * 30)
    
    # Show database mode
    from django.conf import settings
    use_real_its = getattr(settings, 'USE_REAL_ITS_API', False)
    print(f"ITS API Mode: {'Real API' if use_real_its else 'Database Simulation'}")
    
    # Show user counts by role
    print("\nUser counts by role:")
    roles = User.objects.values_list('role', flat=True).distinct()
    for role in roles:
        count = User.objects.filter(role=role).count()
        print(f"  {role}: {count}")
    
    # Show appointment form field info
    print("\nAppointment form fields:")
    form = AppointmentForm()
    for field_name, field in form.fields.items():
        required = "Required" if field.required else "Optional"
        print(f"  {field_name}: {required}")

if __name__ == '__main__':
    show_debug_info()
    test_admin_appointment_booking()