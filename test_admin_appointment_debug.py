#!/usr/bin/env python
"""
Debug script to test admin appointment booking functionality
"""
import os
import sys
import django
from datetime import date, timedelta

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
    
    # 5. Test form validation with FUTURE date
    print(f"\n5. Testing Appointment Form Validation:")
    try:
        # Use tomorrow's date to avoid past date validation error
        future_date = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        form_data = {
            'doctor': test_doctor.id,
            'patient_its_id': test_patient_its_id,
            'appointment_date': future_date,
            'appointment_time': '10:00',
            'reason_for_visit': 'Test appointment',
            'notes': 'Admin booking test'
        }
        
        print(f"   Form data: {form_data}")
        form = AppointmentForm(data=form_data, doctor=test_doctor, user=admin_user)
        
        if form.is_valid():
            print("   ✅ Form validation passed!")
            cleaned_data = form.cleaned_data
            patient = cleaned_data.get('patient')
            print(f"   ✅ Patient assigned: {patient}")
            if patient:
                print(f"      - Patient name: {patient.user.get_full_name()}")
                print(f"      - Patient ITS ID: {patient.user.its_id}")
        else:
            print("   ❌ Form validation failed!")
            print(f"   Errors: {form.errors}")
            print(f"   Non-field errors: {form.non_field_errors()}")
            
            # Show detailed field errors
            for field, errors in form.errors.items():
                print(f"   Field '{field}' errors:")
                for error in errors:
                    print(f"      - {error}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing form: {e}")
        import traceback
        traceback.print_exc()
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
    
    # Show user counts by role (consolidated)
    print("\nUser counts by role:")
    from django.db.models import Count
    role_counts = User.objects.values('role').annotate(count=Count('role')).order_by('role')
    for item in role_counts:
        print(f"  {item['role']}: {item['count']}")
    
    # Show appointment form field info
    print("\nAppointment form fields:")
    form = AppointmentForm()
    for field_name, field in form.fields.items():
        required = "Required" if field.required else "Optional"
        print(f"  {field_name}: {required}")

def show_sample_its_ids():
    print("\n📋 Sample ITS IDs for Testing:")
    print("=" * 35)
    
    # Show sample ITS IDs for each role
    roles = ['badri_mahal_admin', 'aamil', 'moze_coordinator', 'doctor', 'student', 'patient']
    for role in roles:
        users = User.objects.filter(role=role)[:3]
        if users.exists():
            print(f"\n{role.title().replace('_', ' ')}:")
            for user in users:
                print(f"  - {user.its_id} - {user.get_full_name()}")

if __name__ == '__main__':
    show_debug_info()
    show_sample_its_ids()
    test_admin_appointment_booking()