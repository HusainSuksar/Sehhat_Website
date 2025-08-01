#!/usr/bin/env python3
"""
Script to create sample data for testing medical record creation
"""
import os
import sys
import django
from datetime import date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

from accounts.models import User
from mahalshifa.models import Doctor, Patient, Hospital, Department, Moze
from moze.models import Moze as MozeModel

def create_sample_data():
    """Create sample data for testing"""
    print("🔧 Creating sample data for medical record testing...")
    
    # Create a test hospital if it doesn't exist
    hospital, created = Hospital.objects.get_or_create(
        name="Test General Hospital",
        defaults={
            'description': 'A test hospital for development',
            'address': '123 Test Street, Test City',
            'phone': '+1234567890',
            'email': 'test@hospital.com',
            'hospital_type': 'general',
            'total_beds': 100,
            'available_beds': 50,
            'is_active': True
        }
    )
    if created:
        print(f"✅ Created hospital: {hospital.name}")
    
    # Create a test department
    department, created = Department.objects.get_or_create(
        name="General Medicine",
        hospital=hospital,
        defaults={
            'description': 'General medicine department',
            'is_active': True
        }
    )
    if created:
        print(f"✅ Created department: {department.name}")
    
    # Create a test moze if it doesn't exist
    # First create an aamil user if it doesn't exist
    aamil_user, created = User.objects.get_or_create(
        username='test_aamil',
        defaults={
            'email': 'aamil@test.com',
            'first_name': 'Test',
            'last_name': 'Aamil',
            'role': 'aamil',
            'is_active': True
        }
    )
    if created:
        aamil_user.set_password('test123456')
        aamil_user.save()
        print(f"✅ Created aamil user: {aamil_user.username}")
    
    moze, created = MozeModel.objects.get_or_create(
        name="Test Moze",
        defaults={
            'location': 'Test City',
            'address': '456 Test Avenue, Test City',
            'aamil': aamil_user,
            'contact_phone': '+1234567891',
            'contact_email': 'moze@test.com',
            'is_active': True
        }
    )
    if created:
        print(f"✅ Created moze: {moze.name}")
    
    # Create a test doctor user
    doctor_user, created = User.objects.get_or_create(
        username='test_doctor',
        defaults={
            'email': 'doctor@test.com',
            'first_name': 'Test',
            'last_name': 'Doctor',
            'role': 'doctor',
            'is_active': True
        }
    )
    if created:
        doctor_user.set_password('test123456')
        doctor_user.save()
        print(f"✅ Created doctor user: {doctor_user.username}")
    
    # Create doctor profile
    doctor, created = Doctor.objects.get_or_create(
        user=doctor_user,
        defaults={
            'license_number': 'DOC123456',
            'specialization': 'General Medicine',
            'qualification': 'MBBS, MD',
            'experience_years': 5,
            'hospital': hospital,
            'department': department,
            'is_available': True,
            'consultation_fee': 50.00
        }
    )
    if created:
        print(f"✅ Created doctor profile: {doctor.user.get_full_name()}")
    
    # Create a test patient
    patient, created = Patient.objects.get_or_create(
        its_id='12345678',
        defaults={
            'first_name': 'Test',
            'last_name': 'Patient',
            'date_of_birth': date(1990, 1, 1),
            'gender': 'male',
            'phone_number': '+1234567892',
            'email': 'patient@test.com',
            'address': '789 Test Road, Test City',
            'emergency_contact_name': 'Emergency Contact',
            'emergency_contact_phone': '+1234567893',
            'emergency_contact_relationship': 'spouse',
            'registered_moze': moze,
            'is_active': True
        }
    )
    if created:
        print(f"✅ Created patient: {patient.get_full_name()}")
    
    print("\n🎯 Sample data created successfully!")
    print("📋 Test credentials:")
    print(f"   Doctor: {doctor_user.username} / test123456")
    print(f"   Patient ITS ID: {patient.its_id}")
    print(f"   Hospital: {hospital.name}")
    print(f"   Moze: {moze.name}")

if __name__ == "__main__":
    create_sample_data()