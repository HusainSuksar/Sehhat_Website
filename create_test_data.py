#!/usr/bin/env python3
"""
Test data creation script for Moze Profile Page features
"""

import os
import django
from datetime import date, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

from django.contrib.auth import get_user_model
from moze.models import Moze, MozeComment, UmoorSehhatTeam
from mahalshifa.models import Patient, Doctor, MedicalRecord, Hospital, Department
from evaluation.models import Evaluation
from photos.models import Photo, PhotoAlbum
from django.core.files.base import ContentFile
from PIL import Image
import io

User = get_user_model()

def create_test_data():
    """Create test data for the moze detail page"""
    
    # Create test users
    aamil, created = User.objects.get_or_create(
        username='test_aamil',
        defaults={
            'first_name': 'Ahmed',
            'last_name': 'Al-Mahdi',
            'email': 'aamil@test.com',
            'role': 'aamil',
            'phone_number': '+966 50 123 4567'
        }
    )
    
    coordinator, created = User.objects.get_or_create(
        username='test_coordinator',
        defaults={
            'first_name': 'Fatima',
            'last_name': 'Ali',
            'email': 'coordinator@test.com',
            'role': 'moze_coordinator',
            'phone_number': '+966 50 234 5678'
        }
    )
    
    doctor_user, created = User.objects.get_or_create(
        username='test_doctor',
        defaults={
            'first_name': 'Dr. Mohammed',
            'last_name': 'Khan',
            'email': 'doctor@test.com',
            'role': 'doctor',
            'phone_number': '+966 50 345 6789'
        }
    )
    
    # Create hospital and department
    hospital, created = Hospital.objects.get_or_create(
        name='Test Hospital',
        defaults={
            'address': 'Test Address',
            'phone': '+966 11 123 4567',
            'email': 'hospital@test.com'
        }
    )
    
    department, created = Department.objects.get_or_create(
        name='General Medicine',
        hospital=hospital,
        defaults={
            'description': 'General Medicine Department'
        }
    )
    
    # Create doctor
    doctor, created = Doctor.objects.get_or_create(
        user=doctor_user,
        defaults={
            'license_number': 'DOC123456',
            'specialization': 'General Medicine',
            'qualification': 'MBBS, MD',
            'experience_years': 5,
            'hospital': hospital,
            'department': department
        }
    )
    
    # Create moze
    moze, created = Moze.objects.get_or_create(
        name='Test Moze',
        defaults={
            'location': 'Test Location',
            'address': 'Test Address',
            'aamil': aamil,
            'moze_coordinator': coordinator,
            'contact_phone': '+966 50 456 7890',
            'contact_email': 'moze@test.com',
            'established_date': date(2020, 1, 1),
            'capacity': 100
        }
    )
    
    # Add team members
    moze.team_members.add(aamil, coordinator, doctor_user)
    
    # Create Umoor Sehhat team members
    UmoorSehhatTeam.objects.get_or_create(
        moze=moze,
        member=aamil,
        category='medical',
        defaults={
            'position': 'Medical Coordinator',
            'contact_number': '+966 50 111 1111'
        }
    )
    
    UmoorSehhatTeam.objects.get_or_create(
        moze=moze,
        member=coordinator,
        category='sports',
        defaults={
            'position': 'Sports Coordinator',
            'contact_number': '+966 50 222 2222'
        }
    )
    
    # Create test patients
    patient1, created = Patient.objects.get_or_create(
        its_id='12345678',
        defaults={
            'first_name': 'Ali',
            'last_name': 'Hassan',
            'date_of_birth': date(1985, 5, 15),
            'gender': 'male',
            'phone_number': '+966 50 555 5555',
            'address': 'Patient Address 1',
            'emergency_contact_name': 'Hassan Ali',
            'emergency_contact_phone': '+966 50 666 6666',
            'emergency_contact_relationship': 'Father',
            'registered_moze': moze
        }
    )
    
    patient2, created = Patient.objects.get_or_create(
        its_id='87654321',
        defaults={
            'first_name': 'Aisha',
            'last_name': 'Mohammed',
            'date_of_birth': date(1990, 8, 20),
            'gender': 'female',
            'phone_number': '+966 50 777 7777',
            'address': 'Patient Address 2',
            'emergency_contact_name': 'Mohammed Ali',
            'emergency_contact_phone': '+966 50 888 8888',
            'emergency_contact_relationship': 'Husband',
            'registered_moze': moze
        }
    )
    
    # Create medical records
    medical_record1, created = MedicalRecord.objects.get_or_create(
        patient=patient1,
        doctor=doctor,
        moze=moze,
        defaults={
            'chief_complaint': 'Fever and cough',
            'diagnosis': 'Upper respiratory tract infection',
            'treatment_plan': 'Rest, fluids, and symptomatic treatment',
            'medications_prescribed': 'Paracetamol 500mg',
            'consultation_date': django.utils.timezone.now() - timedelta(days=5)
        }
    )
    
    medical_record2, created = MedicalRecord.objects.get_or_create(
        patient=patient2,
        doctor=doctor,
        moze=moze,
        defaults={
            'chief_complaint': 'Headache',
            'diagnosis': 'Tension headache',
            'treatment_plan': 'Pain management and stress reduction',
            'medications_prescribed': 'Ibuprofen 400mg',
            'consultation_date': django.utils.timezone.now() - timedelta(days=3)
        }
    )
    
    # Create evaluations
    evaluation1, created = Evaluation.objects.get_or_create(
        moze=moze,
        evaluator=aamil,
        evaluation_date=date(2024, 12, 1),
        defaults={
            'evaluation_period': 'quarterly',
            'overall_grade': 'A',
            'overall_score': 85.5,
            'medical_quality_score': 90.0,
            'staff_performance_score': 85.0,
            'patient_satisfaction_score': 88.0,
            'administration_score': 80.0,
            'safety_score': 87.0,
            'equipment_score': 82.0,
            'accessibility_score': 85.0,
            'is_published': True,
            'is_draft': False
        }
    )
    
    evaluation2, created = Evaluation.objects.get_or_create(
        moze=moze,
        evaluator=coordinator,
        evaluation_date=date(2024, 9, 1),
        defaults={
            'evaluation_period': 'quarterly',
            'overall_grade': 'B',
            'overall_score': 78.0,
            'medical_quality_score': 80.0,
            'staff_performance_score': 75.0,
            'patient_satisfaction_score': 82.0,
            'administration_score': 75.0,
            'safety_score': 80.0,
            'equipment_score': 78.0,
            'accessibility_score': 75.0,
            'is_published': True,
            'is_draft': False
        }
    )
    
    # Create comments
    comment1, created = MozeComment.objects.get_or_create(
        moze=moze,
        author=aamil,
        content='Excellent work this quarter. Team performance has improved significantly.',
        defaults={
            'created_at': django.utils.timezone.now() - timedelta(days=2)
        }
    )
    
    comment2, created = MozeComment.objects.get_or_create(
        moze=moze,
        author=coordinator,
        content='Need to focus on equipment maintenance and staff training.',
        defaults={
            'created_at': django.utils.timezone.now() - timedelta(days=1)
        }
    )
    
    # Create a simple test image for photos
    def create_test_image():
        """Create a simple test image"""
        img = Image.new('RGB', (300, 200), color='lightblue')
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG')
        img_io.seek(0)
        return ContentFile(img_io.getvalue(), 'test_image.jpg')
    
    # Create photo album
    album, created = PhotoAlbum.objects.get_or_create(
        name='Test Album',
        moze=moze,
        created_by=aamil,
        defaults={
            'description': 'Test photo album for moze',
            'event_date': date.today()
        }
    )
    
    # Create photos
    photo1, created = Photo.objects.get_or_create(
        title='Test Photo 1',
        moze=moze,
        uploaded_by=aamil,
        defaults={
            'description': 'Test photo for moze detail page',
            'subject_tag': 'test',
            'category': 'event',
            'is_public': True,
            'image': create_test_image()
        }
    )
    
    photo2, created = Photo.objects.get_or_create(
        title='Test Photo 2',
        moze=moze,
        uploaded_by=coordinator,
        defaults={
            'description': 'Another test photo',
            'subject_tag': 'test',
            'category': 'team',
            'is_public': True,
            'image': create_test_image()
        }
    )
    
    # Add photos to album
    album.photos.add(photo1, photo2)
    
    print(f"✅ Test data created successfully!")
    print(f"📋 Moze: {moze.name}")
    print(f"👥 Team Members: {moze.team_members.count()}")
    print(f"🏥 Patients: {Patient.objects.filter(registered_moze=moze).count()}")
    print(f"📊 Evaluations: {Evaluation.objects.filter(moze=moze).count()}")
    print(f"💬 Comments: {MozeComment.objects.filter(moze=moze).count()}")
    print(f"📸 Photos: {Photo.objects.filter(moze=moze).count()}")
    print(f"🔗 Moze Detail URL: http://localhost:8000/moze/{moze.id}/")

if __name__ == "__main__":
    create_test_data()