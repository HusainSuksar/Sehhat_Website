#!/usr/bin/env python3
"""
Test script to verify admin appointment booking functionality
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/workspace')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')

try:
    django.setup()
except Exception as e:
    print(f"Django setup failed: {e}")
    sys.exit(1)

from accounts.models import User
from doctordirectory.models import Doctor, Patient, Appointment
from accounts.services import ITSService

def test_admin_functionality():
    print("🔍 Testing Admin Functionality...")
    
    # 1. Check if badri mahal admin exists
    print("\n1. Checking Badri Mahal Admin...")
    try:
        admin_user = User.objects.filter(role='badri_mahal_admin').first()
        if admin_user:
            print(f"✅ Found Badri Mahal Admin: {admin_user.get_full_name()} (ID: {admin_user.its_id})")
            print(f"   - is_admin: {admin_user.is_admin}")
            print(f"   - is_superuser: {admin_user.is_superuser}")
            print(f"   - is_staff: {admin_user.is_staff}")
            print(f"   - role: {admin_user.role}")
        else:
            print("❌ No Badri Mahal Admin found")
            
            # Create one for testing
            print("📝 Creating test Badri Mahal Admin...")
            admin_user = User.objects.create_user(
                username='admin',
                its_id='50000001',
                first_name='Badri',
                last_name='Admin',
                email='admin@badrimahal.com',
                role='badri_mahal_admin',
                is_superuser=True,
                is_staff=True
            )
            print(f"✅ Created Badri Mahal Admin: {admin_user.get_full_name()}")
            
    except Exception as e:
        print(f"❌ Error with admin user: {e}")
        return False
    
    # 2. Test ITS ID validation
    print("\n2. Testing ITS ID Validation...")
    test_its_ids = ['10000007', '10000011', '12345678', '50000001']
    
    for its_id in test_its_ids:
        its_data = ITSService.fetch_user_data(its_id)
        if its_data:
            print(f"✅ ITS ID {its_id}: Valid - {its_data.get('first_name')} {its_data.get('last_name')}")
        else:
            print(f"❌ ITS ID {its_id}: Invalid")
    
    # 3. Check doctors availability
    print("\n3. Checking Available Doctors...")
    doctors = Doctor.objects.filter(is_available=True)
    print(f"📊 Found {doctors.count()} available doctors:")
    for doctor in doctors[:5]:  # Show first 5
        print(f"   - Dr. {doctor.get_full_name()} (ID: {doctor.id})")
    
    # 4. Check patients
    print("\n4. Checking Patients...")
    patients = Patient.objects.all()
    print(f"📊 Found {patients.count()} patients in system")
    
    # 5. Test appointment creation permissions
    print("\n5. Testing Admin Permissions...")
    if admin_user:
        print(f"   - Can create appointments: {admin_user.is_admin}")
        print(f"   - Can access admin features: {admin_user.is_admin}")
        print(f"   - Can manage users: {admin_user.is_admin}")
    
    print("\n✅ Admin functionality test completed!")
    return True

def test_appointment_booking():
    print("\n🎯 Testing Appointment Booking Process...")
    
    try:
        # Get admin user
        admin_user = User.objects.filter(role='badri_mahal_admin').first()
        if not admin_user:
            print("❌ No admin user found for testing")
            return False
            
        # Get a doctor
        doctor = Doctor.objects.filter(is_available=True).first()
        if not doctor:
            print("❌ No available doctors found")
            return False
            
        print(f"👨‍⚕️ Using doctor: Dr. {doctor.get_full_name()}")
        
        # Test valid ITS ID
        test_its_id = '10000007'
        print(f"🆔 Testing with ITS ID: {test_its_id}")
        
        # Check if ITS ID is valid
        its_data = ITSService.fetch_user_data(test_its_id)
        if not its_data:
            print(f"❌ ITS ID {test_its_id} is not valid")
            return False
            
        print(f"✅ ITS ID valid: {its_data.get('first_name')} {its_data.get('last_name')}")
        
        # Check if user exists or create
        patient_user = User.objects.filter(its_id=test_its_id).first()
        if not patient_user:
            print("📝 Creating user from ITS data...")
            patient_user = User.objects.create_user(
                username=test_its_id,
                its_id=test_its_id,
                first_name=its_data.get('first_name', ''),
                last_name=its_data.get('last_name', ''),
                email=its_data.get('email', f'{test_its_id}@its.temp'),
                role='patient'
            )
            
        # Check if patient profile exists
        patient_profile = patient_user.patient_profile.first()
        if not patient_profile:
            print("📝 Creating patient profile...")
            from datetime import date
            patient_profile = Patient.objects.create(
                user=patient_user,
                date_of_birth=date(1990, 1, 1),
                gender=its_data.get('gender', 'other').lower()
            )
            
        print(f"👤 Patient ready: {patient_profile.user.get_full_name()}")
        
        # Count existing appointments
        existing_appointments = Appointment.objects.count()
        print(f"📊 Current appointments in system: {existing_appointments}")
        
        print("\n✅ Appointment booking test setup completed!")
        print("🎯 Ready for manual testing via web interface")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in appointment booking test: {e}")
        return False

if __name__ == "__main__":
    print("🏥 Umoor Sehhat Admin & Appointment Testing")
    print("=" * 50)
    
    # Test admin functionality
    admin_success = test_admin_functionality()
    
    if admin_success:
        # Test appointment booking setup
        booking_success = test_appointment_booking()
        
        if booking_success:
            print("\n🎉 All tests passed! Ready for manual appointment booking test.")
            print("\n📋 Manual Test Steps:")
            print("1. Login as Badri Mahal Admin (ITS ID: 50000001)")
            print("2. Go to Doctor Directory")
            print("3. Click 'Book Appointment' on any doctor")
            print("4. Enter ITS ID: 10000007")
            print("5. Click 'Fetch' to load patient data")
            print("6. Fill appointment details and submit")
        else:
            print("\n❌ Appointment booking test failed")
    else:
        print("\n❌ Admin functionality test failed")