#!/usr/bin/env python3
"""
Quick Database Check and Population Script for PythonAnywhere
This script checks if sample data exists and creates it if missing
"""

import os
import django
from django.utils import timezone

# Setup Django for PythonAnywhere
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings_pythonanywhere')
django.setup()

from accounts.models import User
from students.models import Student
from moze.models import Moze
from mahalshifa.models import Hospital
from doctordirectory.models import Doctor
from surveys.models import Survey
from araz.models import Petition
from photos.models import PhotoAlbum

def print_status(message):
    print(f"✅ {message}")

def print_info(message):
    print(f"ℹ️  {message}")

def print_warning(message):
    print(f"⚠️  {message}")

def check_database_status():
    """Check current database status"""
    print("🔍 CHECKING DATABASE STATUS")
    print("=" * 40)
    
    counts = {
        'Users': User.objects.count(),
        'Students': Student.objects.count(),
        'Moze Centers': Moze.objects.count(),
        'Hospitals': Hospital.objects.count(),
        'Doctors': Doctor.objects.count(),
        'Surveys': Survey.objects.count(),
        'Petitions': Petition.objects.count(),
        'Photo Albums': PhotoAlbum.objects.count(),
    }
    
    for model_name, count in counts.items():
        if count == 0:
            print(f"❌ {model_name}: {count} (EMPTY)")
        else:
            print(f"✅ {model_name}: {count}")
    
    return counts

def create_minimal_sample_data():
    """Create minimal sample data for dashboard testing"""
    print_info("Creating minimal sample data...")
    
    # Create a few students from existing student users
    student_users = User.objects.filter(role='student')[:3]
    for i, user in enumerate(student_users):
        student, created = Student.objects.get_or_create(
            user=user,
            defaults={
                'student_id': f'STD{user.id:03d}',
                'enrollment_date': timezone.now().date(),
                'academic_level': 'undergraduate',
                'enrollment_status': 'active',
            }
        )
        if created:
            print_status(f"Created student: {student.user.get_full_name()}")
    
    # Create a few Moze centers
    aamils = User.objects.filter(role='aamil')
    coordinators = User.objects.filter(role='moze_coordinator')
    
    moze_data = [
        {'name': 'Karachi Central Moze', 'location': 'Karachi, Pakistan'},
        {'name': 'Lahore North Moze', 'location': 'Lahore, Pakistan'},
    ]
    
    for i, moze_info in enumerate(moze_data):
        moze, created = Moze.objects.get_or_create(
            name=moze_info['name'],
            defaults={
                'location': moze_info['location'],
                'aamil': aamils[i % aamils.count()] if aamils.exists() else None,
                'moze_coordinator': coordinators[i % coordinators.count()] if coordinators.exists() else None,
                'is_active': True,
            }
        )
        if created:
            print_status(f"Created Moze: {moze.name}")
    
    # Create a couple of hospitals
    hospitals_data = [
        {'name': 'Saifee Hospital', 'address': 'Mumbai, India', 'phone': '+91-22-67568000'},
        {'name': 'Karachi Saifee Hospital', 'address': 'Karachi, Pakistan', 'phone': '+92-21-35862000'},
    ]
    
    for hospital_data in hospitals_data:
        hospital, created = Hospital.objects.get_or_create(
            name=hospital_data['name'],
            defaults={
                'address': hospital_data['address'],
                'phone': hospital_data['phone'],
                'email': f"info@{hospital_data['name'].lower().replace(' ', '')}.com",
                'is_active': True,
            }
        )
        if created:
            print_status(f"Created hospital: {hospital.name}")
    
    # Create doctors from doctor users
    doctor_users = User.objects.filter(role='doctor')
    specialties = ['General Medicine', 'Cardiology', 'Pediatrics']
    
    for i, user in enumerate(doctor_users):
        doctor, created = Doctor.objects.get_or_create(
            user=user,
            defaults={
                'name': user.get_full_name(),
                'its_id': f'{user.id:08d}',
                'specialty': specialties[i % len(specialties)],
                'qualification': 'MBBS',
                'experience_years': 5,
                'is_available': True,
                'is_verified': True,
            }
        )
        if created:
            print_status(f"Created doctor: {doctor.name}")
    
    print_status("Minimal sample data created successfully!")

def main():
    print("🏥 UMOOR SEHHAT - DATABASE STATUS CHECK")
    print("=" * 50)
    
    try:
        # Check current status
        counts = check_database_status()
        
        # Check if we need to create sample data
        total_non_user_records = sum(count for key, count in counts.items() if key != 'Users')
        
        if total_non_user_records == 0:
            print_warning("No sample data found! Creating minimal sample data...")
            create_minimal_sample_data()
            print("\n" + "=" * 50)
            print("📊 UPDATED DATABASE STATUS")
            print("=" * 50)
            check_database_status()
        else:
            print_info("Sample data already exists!")
        
        print("\n🎉 Database check completed!")
        print("🔗 Your dashboard should now show statistics!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()