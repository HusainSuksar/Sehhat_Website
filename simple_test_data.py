#!/usr/bin/env python3
"""
Simple Test Data Generator for Umoor Sehhat
Creates minimal test data for all 9 apps
"""

import os
import sys
import django
import random
import traceback
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.hashers import make_password

# Import all models
from accounts.models import User, UserProfile, AuditLog
from moze.models import Moze, MozeComment, MozeSettings
from mahalshifa.models import Hospital, Department, Patient, MedicalRecord, Appointment
from doctordirectory.models import Doctor, Appointment as DoctorAppointment
from students.models import Student, Course, Grade
from evaluation.models import EvaluationForm, EvaluationSubmission, EvaluationCriteria
from surveys.models import Survey, SurveyResponse
from araz.models import Petition, PetitionCategory, PetitionStatus
from photos.models import PhotoAlbum, Photo

User = get_user_model()

def create_simple_test_data():
    """Create minimal test data for all apps"""
    print("🚀 Starting simple test data generation...")
    
    try:
        with transaction.atomic():
            # Create base users
            print("\n📋 Creating base users...")
            admin_user, created = User.objects.get_or_create(
                username='admin_1',
                defaults={
                    'email': 'admin@test.com',
                    'password': make_password('admin123'),
                    'role': 'badri_mahal_admin',
                    'its_id': '12345678'
                }
            )
            
            staff_user, created = User.objects.get_or_create(
                username='staff_1',
                defaults={
                    'email': 'staff@test.com',
                    'password': make_password('staff123'),
                    'role': 'staff',
                    'its_id': '12345679'
                }
            )
            
            # Create one moze with aamil
            print("\n🏢 Creating Moze and Aamil...")
            aamil_user, created = User.objects.get_or_create(
                username='aamil_1',
                defaults={
                    'email': 'aamil@test.com',
                    'password': make_password('aamil123'),
                    'role': 'aamil',
                    'its_id': '12345680'
                }
            )
            
            moze, created = Moze.objects.get_or_create(
                name='Test Moze',
                defaults={
                    'aamil': aamil_user,
                    'location': 'Test City',
                    'address': 'Test Address',
                    'phone': '1234567890',
                    'email': 'moze@test.com',
                    'description': 'Test Moze Description'
                }
            )
            
            # Create one doctor
            print("\n👨‍⚕️ Creating Doctor...")
            doctor_user, created = User.objects.get_or_create(
                username='doctor_1',
                defaults={
                    'email': 'doctor@test.com',
                    'password': make_password('doctor123'),
                    'role': 'doctor',
                    'its_id': '12345681'
                }
            )
            

            
            # Create one hospital
            print("\n🏥 Creating Hospital...")
            hospital, created = Hospital.objects.get_or_create(
                name='Test Hospital',
                defaults={
                    'address': 'Hospital Address',
                    'phone': '1234567892',
                    'email': 'hospital@test.com',
                    'description': 'Test Hospital Description'
                }
            )
            
            department, created = Department.objects.get_or_create(
                name='General Department',
                hospital=hospital,
                defaults={
                    'description': 'Test Department'
                }
            )
            
            # Create mahalshifa Doctor
            from mahalshifa.models import Doctor as MahalShifaDoctor
            
            mahalshifa_doctor, created = MahalShifaDoctor.objects.get_or_create(
                user=doctor_user,
                defaults={
                    'license_number': 'LIC123456',
                    'specialization': 'General Medicine',
                    'qualification': 'MBBS, MD',
                    'experience_years': 5,
                    'hospital': hospital,
                    'department': department,
                    'is_available': True,
                    'consultation_fee': Decimal('50.00')
                }
            )
            
            # Create one student
            print("\n👨‍🎓 Creating Student...")
            student_user, created = User.objects.get_or_create(
                username='student_1',
                defaults={
                    'email': 'student@test.com',
                    'password': make_password('student123'),
                    'role': 'student',
                    'its_id': '12345682'
                }
            )
            
            student, created = Student.objects.get_or_create(
                user=student_user,
                defaults={
                    'student_id': 'STU001',
                    'academic_level': 'undergraduate',
                    'enrollment_status': 'active',
                    'enrollment_date': timezone.now().date()
                }
            )
            
            # Create one patient
            print("\n👥 Creating Patient...")
            patient, created = Patient.objects.get_or_create(
                its_id='12345683',
                defaults={
                    'first_name': 'Test',
                    'last_name': 'Patient',
                    'date_of_birth': timezone.now().date() - timedelta(days=30*365),
                    'gender': 'male',
                    'phone_number': '1234567893',
                    'address': 'Patient Address',
                    'emergency_contact_name': 'Emergency Contact',
                    'emergency_contact_phone': '1234567894',
                    'emergency_contact_relationship': 'Spouse',
                    'registered_moze': moze
                }
            )
            
            # Create one medical record
            print("\n📋 Creating Medical Record...")
            medical_record, created = MedicalRecord.objects.get_or_create(
                patient=patient,
                doctor=mahalshifa_doctor,
                moze=moze,
                defaults={
                    'chief_complaint': 'Test Complaint',
                    'diagnosis': 'Test Diagnosis',
                    'treatment_plan': 'Test Treatment Plan',
                    'medications_prescribed': 'Test Medication'
                }
            )
            
            # Create one appointment
            print("\n📅 Creating Appointment...")
            appointment, created = Appointment.objects.get_or_create(
                patient=patient,
                doctor=mahalshifa_doctor,
                moze=moze,
                appointment_date=timezone.now().date() + timedelta(days=1),
                appointment_time=datetime.now().time(),
                defaults={
                    'reason': 'Test Appointment Reason',
                    'status': 'scheduled',
                    'appointment_type': 'regular',
                    'duration_minutes': 30
                }
            )
            
            # Create one evaluation form
            print("\n📊 Creating Evaluation Form...")
            criteria, created = EvaluationCriteria.objects.get_or_create(
                name='Test Criteria',
                defaults={
                    'description': 'Test Criteria Description',
                    'weight': 1.0,
                    'max_score': 10,
                    'category': 'medical_quality'
                }
            )
            
            evaluation_form, created = EvaluationForm.objects.get_or_create(
                title='Test Evaluation',
                defaults={
                    'evaluation_type': 'performance',
                    'target_role': 'all',
                    'description': 'Test Evaluation Description',
                    'is_active': True,
                    'created_by': admin_user
                }
            )
            
            # Create one survey
            print("\n📝 Creating Survey...")
            survey, created = Survey.objects.get_or_create(
                title='Test Survey',
                defaults={
                    'description': 'Test Survey Description',
                    'is_active': True,
                    'questions': {'questions': [{'question': 'Test Question', 'type': 'text'}]},
                    'created_by': admin_user,
                    'target_role': 'all'
                }
            )
            
            # Create one petition
            print("\n📜 Creating Petition...")
            petition_category, created = PetitionCategory.objects.get_or_create(
                name='Test Category',
                defaults={
                    'description': 'Test Category Description'
                }
            )
            
            petition_status, created = PetitionStatus.objects.get_or_create(
                name='Pending',
                defaults={
                    'color': '#ffc107',
                    'is_final': False,
                    'order': 1
                }
            )
            
            petition, created = Petition.objects.get_or_create(
                title='Test Petition',
                created_by=admin_user,
                category=petition_category,
                moze=moze,
                defaults={
                    'description': 'Test Petition Description',
                    'status': 'pending',
                    'priority': 'medium'
                }
            )
            
            # Create one album
            print("\n📸 Creating Album...")
            album, created = PhotoAlbum.objects.get_or_create(
                name='Test Album',
                moze=moze,
                defaults={
                    'description': 'Test Album Description',
                    'created_by': admin_user
                }
            )
            
            # Print summary
            print("\n✅ Simple test data creation completed!")
            print(f"📊 Created:")
            print(f"  - 1 Admin user")
            print(f"  - 1 Staff user")
            print(f"  - 1 Aamil user")
            print(f"  - 1 Doctor user")
            print(f"  - 1 Student user")
            print(f"  - 1 Moze")
            print(f"  - 1 Hospital with 1 Department")
            print(f"  - 1 Patient")
            print(f"  - 1 Medical Record")
            print(f"  - 1 Appointment")
            print(f"  - 1 Evaluation Form with 1 Category")
            print(f"  - 1 Survey")
            print(f"  - 1 Petition with 1 Category and 1 Status")
            print(f"  - 1 Photo Album")
            
            return True
            
    except Exception as e:
        print(f"❌ Error during data creation: {e}")
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = create_simple_test_data()
    if success:
        print("\n🎉 Test data generation completed successfully!")
    else:
        print("\n💥 Test data generation failed!")
        sys.exit(1)