#!/usr/bin/env python3
"""
Optimized Comprehensive Test Data Generator for Umoor Sehhat
Creates production-like test data with better performance monitoring
"""

import os
import sys
import django
import random
import traceback
import time
from datetime import datetime, timedelta
from decimal import Decimal
from faker import Faker

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction, connection
from django.utils import timezone
from django.contrib.auth.hashers import make_password

# Import all models
from accounts.models import User, UserProfile, AuditLog
from moze.models import Moze, MozeComment, MozeSettings
from mahalshifa.models import Hospital, Department, Patient, MedicalRecord, Appointment
from mahalshifa.models import Doctor as MahalshifaDoctor
from doctordirectory.models import Doctor as DirectoryDoctor, Appointment as DoctorAppointment
from students.models import Student, Course, Grade
from evaluation.models import EvaluationForm, EvaluationSubmission, EvaluationCriteria
from surveys.models import Survey, SurveyResponse, SurveyAnalytics
from araz.models import Petition, PetitionCategory, PetitionStatus
from photos.models import PhotoAlbum, Photo

User = get_user_model()
fake = Faker(['en_US', 'ar_SA'])

# Optimized data specifications
OPTIMIZED_DATA_SPECS = {
    'moze_count': 50,  # Reduced from 200
    'students_count': 100,  # Reduced from 500
    'admin_count': 2,
    'staff_count': 5,  # Reduced from 10
    'hospitals_count': 30,  # Reduced from 120
    'patients_count': 200,  # Reduced from 1200
    'medical_records_count': 150,  # Reduced from 1200
    'appointments_count': 50,  # Reduced from 200
    'evaluation_forms_count': 10,  # Reduced from 20
    'surveys_count': 10,  # Reduced from 20
    'araz_count': 200  # Reduced from 1200
}

# ID ranges to avoid conflicts
ID_RANGES = {
    'admin_start': 90000000,
    'staff_start': 91000000,
    'aamil_start': 92000000,
    'student_start': 93000000,
    'doctor_start': 94000000,
    'patient_start': 95000000,
}

def create_optimized_test_data():
    """Create optimized test data with performance monitoring"""
    print("🚀 Starting optimized comprehensive test data generation...")
    print(f"📊 Optimized data volumes: {OPTIMIZED_DATA_SPECS}")
    
    start_time = time.time()
    
    try:
        with transaction.atomic():
            # Step 1: Create admin and staff users
            print("\n👑 Creating admin and staff users...")
            step_start = time.time()
            admins = create_optimized_admin_users()
            staff = create_optimized_staff_users()
            print(f"   ✅ Completed in {time.time() - step_start:.2f}s")
            
            # Step 2: Create Moze and Aamils
            print(f"\n🏢 Creating {OPTIMIZED_DATA_SPECS['moze_count']} Moze with Aamils...")
            step_start = time.time()
            moze_data = create_optimized_moze_and_aamils()
            print(f"   ✅ Completed in {time.time() - step_start:.2f}s")
            
            # Step 3: Create students
            print(f"\n👨‍🎓 Creating {OPTIMIZED_DATA_SPECS['students_count']} students...")
            step_start = time.time()
            students = create_optimized_students(moze_data['moze_list'])
            print(f"   ✅ Completed in {time.time() - step_start:.2f}s")
            
            # Step 4: Create hospitals
            print(f"\n🏥 Creating {OPTIMIZED_DATA_SPECS['hospitals_count']} hospitals...")
            step_start = time.time()
            hospitals = create_optimized_hospitals(moze_data['moze_list'])
            print(f"   ✅ Completed in {time.time() - step_start:.2f}s")
            
            # Step 5: Create doctors
            print(f"\n👨‍⚕️ Creating doctors for hospitals...")
            step_start = time.time()
            doctors = create_optimized_doctors(hospitals)
            print(f"   ✅ Completed in {time.time() - step_start:.2f}s")
            
            # Step 6: Create patients
            print(f"\n👥 Creating {OPTIMIZED_DATA_SPECS['patients_count']} patients...")
            step_start = time.time()
            patients = create_optimized_patients(moze_data['moze_list'])
            print(f"   ✅ Completed in {time.time() - step_start:.2f}s")
            
            # Step 7: Create medical records
            print(f"\n📋 Creating {OPTIMIZED_DATA_SPECS['medical_records_count']} medical records...")
            step_start = time.time()
            medical_records = create_optimized_medical_records(patients, doctors, moze_data['moze_list'])
            print(f"   ✅ Completed in {time.time() - step_start:.2f}s")
            
            # Step 8: Create appointments
            print(f"\n📅 Creating {OPTIMIZED_DATA_SPECS['appointments_count']} appointments...")
            step_start = time.time()
            appointments = create_optimized_appointments(patients, doctors, moze_data['moze_list'])
            print(f"   ✅ Completed in {time.time() - step_start:.2f}s")
            
            # Step 9: Create evaluation forms
            print(f"\n📊 Creating {OPTIMIZED_DATA_SPECS['evaluation_forms_count']} evaluation forms...")
            step_start = time.time()
            evaluations = create_optimized_evaluation_forms(moze_data['aamils'])
            print(f"   ✅ Completed in {time.time() - step_start:.2f}s")
            
            # Step 10: Create surveys
            print(f"\n📝 Creating {OPTIMIZED_DATA_SPECS['surveys_count']} surveys...")
            step_start = time.time()
            surveys = create_optimized_surveys(moze_data['aamils'])
            print(f"   ✅ Completed in {time.time() - step_start:.2f}s")
            
            # Step 11: Create Araz petitions
            print(f"\n📜 Creating {OPTIMIZED_DATA_SPECS['araz_count']} Araz petitions...")
            step_start = time.time()
            petitions = create_optimized_araz_petitions(students)
            print(f"   ✅ Completed in {time.time() - step_start:.2f}s")
            
            total_time = time.time() - start_time
            print(f"\n🎉 Optimized test completed in {total_time:.2f} seconds!")
            print_optimized_summary()
            
    except Exception as e:
        print(f"❌ Error during optimized data generation: {e}")
        traceback.print_exc()
        raise

def create_optimized_admin_users():
    """Create optimized admin users"""
    admins = []
    timestamp = int(time.time())
    for i in range(OPTIMIZED_DATA_SPECS['admin_count']):
        user = User.objects.create(
            username=f'opt_admin_{timestamp}_{i+1}',
            email=f'opt_admin{timestamp}_{i+1}@umoor-sehhat.com',
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            role='badri_mahal_admin',
            its_id=f'{ID_RANGES["admin_start"] + i}',
            phone_number=fake.phone_number()[:15],
            is_staff=True,
            is_superuser=True
        )
        user.set_password('admin123')
        user.save()
        
        UserProfile.objects.create(
            user=user,
            bio=fake.text(max_nb_chars=200),
            location=fake.city(),
            date_of_birth=fake.date_of_birth(minimum_age=30, maximum_age=60)
        )
        admins.append(user)
    
    return admins

def create_optimized_staff_users():
    """Create optimized staff users"""
    staff = []
    timestamp = int(time.time())
    for i in range(OPTIMIZED_DATA_SPECS['staff_count']):
        user = User.objects.create(
            username=f'opt_staff_{timestamp}_{i+1}',
            email=f'opt_staff{timestamp}_{i+1}@umoor-sehhat.com',
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            role='aamil',
            its_id=f'{ID_RANGES["staff_start"] + i}',
            phone_number=fake.phone_number()[:15],
            is_staff=True
        )
        user.set_password('staff123')
        user.save()
        
        UserProfile.objects.create(
            user=user,
            bio=fake.text(max_nb_chars=200),
            location=fake.city(),
            date_of_birth=fake.date_of_birth(minimum_age=25, maximum_age=55)
        )
        staff.append(user)
    
    return staff

def create_optimized_moze_and_aamils():
    """Create optimized Moze with their Aamils"""
    moze_list = []
    aamils = []
    
    for i in range(OPTIMIZED_DATA_SPECS['moze_count']):
        # Create Aamil user
        timestamp = int(time.time())
        aamil_user = User.objects.create(
            username=f'opt_aamil_{timestamp}_{i+1}',
            email=f'opt_aamil{timestamp}_{i+1}@umoor-sehhat.com',
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            role='aamil',
            its_id=f'{ID_RANGES["aamil_start"] + i}',
            phone_number=fake.phone_number()[:15]
        )
        aamil_user.set_password('aamil123')
        aamil_user.save()
        
        UserProfile.objects.create(
            user=aamil_user,
            bio=fake.text(max_nb_chars=200),
            location=fake.city(),
            date_of_birth=fake.date_of_birth(minimum_age=25, maximum_age=50)
        )
        
        # Create Moze
        moze = Moze.objects.create(
            name=f'Optimized Moze {fake.city()} #{i+1}',
            location=fake.city(),
            address=fake.address(),
            aamil=aamil_user,
            contact_phone=fake.phone_number()[:15],
            contact_email=fake.email(),
            established_date=fake.date_between(start_date='-10y', end_date='today'),
            capacity=random.randint(50, 500),
            is_active=True
        )
        
        moze_list.append(moze)
        aamils.append(aamil_user)
        
        if (i + 1) % 10 == 0:
            print(f"   Created {i + 1} Moze...")
    
    return {'moze_list': moze_list, 'aamils': aamils}

def create_optimized_students(moze_list):
    """Create optimized students"""
    students = []
    
    for i in range(OPTIMIZED_DATA_SPECS['students_count']):
        # Create student user
        timestamp = int(time.time())
        student_user = User.objects.create(
            username=f'opt_student_{timestamp}_{i+1}',
            email=f'opt_student{timestamp}_{i+1}@example.com',
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            role='student',
            its_id=f'{ID_RANGES["student_start"] + i}',
            phone_number=fake.phone_number()[:15],
            college=fake.company(),
            specialization=random.choice(['Engineering', 'Medicine', 'Business', 'Arts', 'Science'])
        )
        student_user.set_password('student123')
        student_user.save()
        
        UserProfile.objects.create(
            user=student_user,
            bio=fake.text(max_nb_chars=200),
            location=fake.city(),
            date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=30)
        )
        
        # Create Student profile
        student = Student.objects.create(
            user=student_user,
            student_id=f'OPT_STU{i+1:06d}',
            academic_level=random.choice(['undergraduate', 'postgraduate', 'doctoral', 'diploma']),
            enrollment_status=random.choice(['active', 'active', 'active', 'suspended']),
            enrollment_date=fake.date_between(start_date='-4y', end_date='today'),
            expected_graduation=fake.date_between(start_date='today', end_date='+2y') if random.choice([True, False]) else None
        )
        
        students.append(student)
        
        if (i + 1) % 20 == 0:
            print(f"   Created {i + 1} students...")
    
    return students

def create_optimized_hospitals(moze_list):
    """Create optimized hospitals"""
    hospitals = []
    
    for i in range(OPTIMIZED_DATA_SPECS['hospitals_count']):
        hospital = Hospital.objects.create(
            name=f'Optimized {fake.company()} Medical Center #{i+1}',
            description=fake.text(max_nb_chars=500),
            address=fake.address(),
            phone=fake.phone_number()[:20],
            email=f'opt_hospital{i+1}@medical.com',
            hospital_type=random.choice(['general', 'specialty', 'clinic', 'emergency', 'rehabilitation']),
            total_beds=random.randint(50, 500),
            available_beds=random.randint(10, 100),
            emergency_beds=random.randint(5, 50),
            icu_beds=random.randint(2, 20),
            is_active=True,
            is_emergency_capable=random.choice([True, False]),
            has_pharmacy=random.choice([True, False]),
            has_laboratory=random.choice([True, False])
        )
        
        # Create departments for each hospital
        departments = ['Emergency', 'Cardiology', 'Pediatrics', 'Surgery', 'Internal Medicine']
        for dept_name in random.sample(departments, random.randint(2, 4)):
            Department.objects.create(
                hospital=hospital,
                name=dept_name,
                description=fake.text(max_nb_chars=300)
            )
        
        hospitals.append(hospital)
        
        if (i + 1) % 10 == 0:
            print(f"   Created {i + 1} hospitals...")
    
    return hospitals

def create_optimized_doctors(hospitals):
    """Create optimized doctors for hospitals"""
    doctors = []
    
    for hospital in hospitals:
        # Create 2-3 doctors per hospital
        num_doctors = random.randint(2, 3)
        
        for i in range(num_doctors):
            # Create doctor user
            timestamp = int(time.time())
            doctor_user = User.objects.create(
                username=f'opt_doctor_{timestamp}_{hospital.id}_{i+1}',
                email=f'opt_doctor{timestamp}_{hospital.id}_{i+1}@medical.com',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                role='doctor',
                its_id=f'{ID_RANGES["doctor_start"] + len(doctors)}',
                phone_number=fake.phone_number()[:15],
                specialty=random.choice(['Cardiology', 'Pediatrics', 'Surgery', 'Internal Medicine', 'Emergency Medicine'])
            )
            doctor_user.set_password('doctor123')
            doctor_user.save()
            
            UserProfile.objects.create(
                user=doctor_user,
                bio=fake.text(max_nb_chars=200),
                location=fake.city(),
                date_of_birth=fake.date_of_birth(minimum_age=28, maximum_age=65)
            )
            
            # Get a random department from the hospital
            department = random.choice(hospital.departments.all()) if hospital.departments.exists() else None
            
            if department:
                doctor = MahalshifaDoctor.objects.create(
                    user=doctor_user,
                    license_number=f'OPT_LIC{len(doctors)+1:06d}',
                    specialization=doctor_user.specialty,
                    qualification=random.choice(['MBBS', 'MD', 'MS', 'FRCS', 'PhD']),
                    experience_years=random.randint(1, 30),
                    hospital=hospital,
                    department=department,
                    is_available=random.choice([True, True, False]),
                    is_emergency_doctor=random.choice([True, False]),
                    consultation_fee=random.uniform(50, 500)
                )
                doctors.append(doctor)
        
        if len(doctors) % 10 == 0:
            print(f"   Created {len(doctors)} doctors...")
    
    return doctors

def create_optimized_patients(moze_list):
    """Create optimized patients"""
    patients = []
    
    for i in range(OPTIMIZED_DATA_SPECS['patients_count']):
        moze = random.choice(moze_list)
        
        patient = Patient.objects.create(
            its_id=f'{ID_RANGES["patient_start"] + i}',
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            arabic_name=fake.name(),
            date_of_birth=fake.date_of_birth(minimum_age=1, maximum_age=90),
            gender=random.choice(['male', 'female', 'other']),
            phone_number=fake.phone_number()[:15],
            email=fake.email(),
            address=fake.address(),
            emergency_contact_name=fake.name(),
            emergency_contact_phone=fake.phone_number()[:15],
            emergency_contact_relationship=random.choice(['Spouse', 'Parent', 'Child', 'Sibling', 'Friend']),
            blood_group=random.choice(['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']),
            allergies=fake.text(max_nb_chars=200) if random.choice([True, False]) else '',
            chronic_conditions=fake.text(max_nb_chars=300) if random.choice([True, False]) else '',
            current_medications=fake.text(max_nb_chars=200) if random.choice([True, False]) else '',
            is_active=random.choice([True, True, True, False]),
            registered_moze=moze
        )
        
        patients.append(patient)
        
        if (i + 1) % 50 == 0:
            print(f"   Created {i + 1} patients...")
    
    return patients

def create_optimized_medical_records(patients, doctors, moze_list):
    """Create optimized medical records"""
    medical_records = []
    
    for i, patient in enumerate(patients[:OPTIMIZED_DATA_SPECS['medical_records_count']]):
        doctor = random.choice(doctors) if doctors else None
        moze = patient.registered_moze or random.choice(moze_list)
        
        if doctor:
            medical_record = MedicalRecord.objects.create(
                patient=patient,
                doctor=doctor,
                moze=moze,
                chief_complaint=fake.text(max_nb_chars=200),
                history_of_present_illness=fake.text(max_nb_chars=300),
                past_medical_history=fake.text(max_nb_chars=300),
                vital_signs={
                    'blood_pressure': f'{random.randint(90, 180)}/{random.randint(60, 120)}',
                    'temperature': round(random.uniform(97.0, 102.0), 1),
                    'pulse': random.randint(60, 120),
                    'weight': round(random.uniform(40, 120), 1)
                },
                physical_examination=fake.text(max_nb_chars=400),
                diagnosis=fake.text(max_nb_chars=300),
                treatment_plan=fake.text(max_nb_chars=400),
                medications_prescribed=fake.text(max_nb_chars=200),
                follow_up_required=random.choice([True, False]),
                follow_up_date=fake.date_between(start_date='today', end_date='+6m') if random.choice([True, False]) else None,
                doctor_notes=fake.text(max_nb_chars=300)
            )
            
            medical_records.append(medical_record)
        
        if (i + 1) % 50 == 0:
            print(f"   Created {i + 1} medical records...")
    
    return medical_records

def create_optimized_appointments(patients, doctors, moze_list):
    """Create optimized appointments"""
    appointments = []
    
    for i in range(OPTIMIZED_DATA_SPECS['appointments_count']):
        patient = random.choice(patients)
        doctor = random.choice(doctors) if doctors else None
        moze = patient.registered_moze or random.choice(moze_list)
        
        if doctor:
            appointment_date = fake.date_between(start_date='-1y', end_date='+3m')
            appointment_time = fake.time()
            
            appointment = Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                moze=moze,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                duration_minutes=random.choice([30, 45, 60]),
                reason=fake.text(max_nb_chars=200),
                symptoms=fake.text(max_nb_chars=300),
                notes=fake.text(max_nb_chars=200),
                status=random.choice(['scheduled', 'confirmed', 'completed', 'cancelled', 'no_show']),
                appointment_type=random.choice(['regular', 'follow_up', 'urgent', 'consultation']),
                booking_method=random.choice(['online', 'phone', 'walk_in', 'staff'])
            )
            
            appointments.append(appointment)
        
        if (i + 1) % 10 == 0:
            print(f"   Created {i + 1} appointments...")
    
    return appointments

def create_optimized_evaluation_forms(aamils):
    """Create optimized evaluation forms"""
    evaluation_forms = []
    
    for i in range(OPTIMIZED_DATA_SPECS['evaluation_forms_count']):
        creator = random.choice(aamils)
        
        form = EvaluationForm.objects.create(
            title=f'Optimized Evaluation Form #{i+1}: {fake.catch_phrase()}',
            description=fake.text(max_nb_chars=500),
            evaluation_type=random.choice(['performance', 'satisfaction', 'quality', 'training', 'service', 'facility']),
            target_role=random.choice(['all', 'doctor', 'student', 'aamil']),
            created_by=creator,
            is_active=random.choice([True, True, False]),
            is_anonymous=random.choice([True, False]),
            due_date=fake.date_time_between(start_date='now', end_date='+3m', tzinfo=timezone.get_current_timezone()) if random.choice([True, False]) else None
        )
        
        evaluation_forms.append(form)
    
    return evaluation_forms

def create_optimized_surveys(aamils):
    """Create optimized surveys"""
    surveys = []
    
    for i in range(OPTIMIZED_DATA_SPECS['surveys_count']):
        creator = random.choice(aamils)
        
        # Create survey questions in JSON format
        questions = []
        question_types = ['text', 'multiple_choice', 'rating', 'checkbox']
        for j in range(random.randint(5, 10)):
            question_type = random.choice(question_types)
            question = {
                "id": j + 1,
                "type": question_type,
                "question": fake.sentence() + '?',
                "required": random.choice([True, False]),
                "options": []
            }
            
            if question_type in ['multiple_choice', 'checkbox']:
                question["options"] = [fake.word() for _ in range(random.randint(2, 4))]
            elif question_type == 'rating':
                question["options"] = ["1", "2", "3", "4", "5"]
            
            questions.append(question)
        
        survey = Survey.objects.create(
            title=f'Optimized Survey #{i+1}: {fake.catch_phrase()}',
            description=fake.text(max_nb_chars=500),
            created_by=creator,
            questions=questions,
            target_role=random.choice(['all', 'aamil', 'student', 'doctor']),
            is_active=random.choice([True, True, False]),
            is_anonymous=random.choice([True, False]),
            allow_multiple_responses=random.choice([True, False]),
            show_results=random.choice([True, False]),
            start_date=fake.date_time_between(start_date='-6m', end_date='now', tzinfo=timezone.get_current_timezone()),
            end_date=fake.date_time_between(start_date='now', end_date='+6m', tzinfo=timezone.get_current_timezone())
        )
        
        surveys.append(survey)
    
    return surveys

def create_optimized_araz_petitions(students):
    """Create optimized Araz petitions"""
    # Create petition categories and statuses
    categories = []
    category_names = ['Academic', 'Financial', 'Housing', 'Medical', 'General', 'Administrative']
    for cat_name in category_names:
        category, created = PetitionCategory.objects.get_or_create(
            name=cat_name,
            defaults={'description': f'{cat_name} related petitions'}
        )
        categories.append(category)
    
    statuses = []
    status_names = ['Pending', 'Under Review', 'Approved', 'Rejected', 'Resolved']
    colors = ['#ffc107', '#17a2b8', '#28a745', '#dc3545', '#6c757d']
    for i, status_name in enumerate(status_names):
        status, created = PetitionStatus.objects.get_or_create(
            name=status_name,
            defaults={
                'color': colors[i % len(colors)],
                'is_final': status_name in ['Approved', 'Rejected', 'Resolved'],
                'order': i
            }
        )
        statuses.append(status)
    
    petitions = []
    
    for i in range(OPTIMIZED_DATA_SPECS['araz_count']):
        student = random.choice(students)
        category = random.choice(categories)
        status_choice = random.choice(['pending', 'in_progress', 'resolved', 'rejected'])
        
        petition = Petition.objects.create(
            title=f'Optimized Petition #{i+1}: {fake.catch_phrase()}',
            description=fake.text(max_nb_chars=1000),
            created_by=student.user,
            category=category,
            status=status_choice,
            priority=random.choice(['low', 'medium', 'high']),
            resolved_at=fake.date_time_between(start_date='-1m', end_date='now', tzinfo=timezone.get_current_timezone()) if status_choice in ['resolved', 'rejected'] else None
        )
        
        petitions.append(petition)
        
        if (i + 1) % 50 == 0:
            print(f"   Created {i + 1} Araz petitions...")
    
    return petitions

def print_optimized_summary():
    """Print optimized summary"""
    print("\n" + "="*60)
    print("📊 OPTIMIZED COMPREHENSIVE TEST COMPLETED!")
    print("="*60)
    
    # Count actual created records
    counts = {
        'Users': User.objects.count(),
        'Admins': User.objects.filter(role='badri_mahal_admin').count(),
        'Staff': User.objects.filter(role='aamil').count(),
        'Students': User.objects.filter(role='student').count(),
        'Moze': Moze.objects.count(),
        'Hospitals': Hospital.objects.count(),
        'Departments': Department.objects.count(),
        'Doctors': MahalshifaDoctor.objects.count(),
        'Patients': Patient.objects.count(),
        'Medical Records': MedicalRecord.objects.count(),
        'Appointments': Appointment.objects.count(),
        'Evaluation Forms': EvaluationForm.objects.count(),
        'Surveys': Survey.objects.count(),
        'Araz Petitions': Petition.objects.count(),
    }
    
    for item, count in counts.items():
        print(f"   {item}: {count:,}")
    
    print("\n🎯 Performance Metrics:")
    print(f"   Average users per Moze: {counts['Users'] / max(counts['Moze'], 1):.1f}")
    print(f"   Average patients per Moze: {counts['Patients'] / max(counts['Moze'], 1):.1f}")
    print(f"   Hospitals coverage: {counts['Hospitals'] / max(counts['Moze'], 1) * 100:.1f}% of Moze")
    
    print("\n✅ Optimized test successful - ready for production testing!")

if __name__ == '__main__':
    create_optimized_test_data()