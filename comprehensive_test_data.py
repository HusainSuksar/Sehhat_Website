#!/usr/bin/env python3
"""
Comprehensive Test Data Generator for Umoor Sehhat
Creates production-like test data with specified volumes for stress testing
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

# Data specifications
DATA_SPECS = {
    'moze_count': 200,
    'students_count': 500,
    'admin_count': 2,
    'staff_count': 10,
    'hospitals_count': 120,
    'patients_count': 1200,
    'medical_records_count': 1200,
    'appointments_count': 200,
    'evaluation_forms_count': 20,
    'surveys_count': 20,
    'araz_count': 1200
}

# ID ranges to avoid conflicts with existing data
ID_RANGES = {
    'admin_start': 90000000,  # Start from 90M to avoid conflicts
    'staff_start': 91000000,   # Start from 91M
    'aamil_start': 92000000,   # Start from 92M
    'student_start': 93000000, # Start from 93M
    'doctor_start': 94000000,  # Start from 94M
    'patient_start': 95000000, # Start from 95M
}

def create_comprehensive_test_data():
    """Create comprehensive test data with proper volumes and relationships"""
    print("🚀 Starting comprehensive test data generation...")
    print(f"📊 Data volumes: {DATA_SPECS}")
    
    try:
        with transaction.atomic():
            # Step 1: Create admin and staff users
            print("\n👑 Creating admin and staff users...")
            admins = create_admin_users()
            staff = create_staff_users()
            
            # Step 2: Create Moze and Aamils
            print(f"\n🏢 Creating {DATA_SPECS['moze_count']} Moze with Aamils...")
            moze_data = create_moze_and_aamils()
            
            # Step 3: Create students
            print(f"\n👨‍🎓 Creating {DATA_SPECS['students_count']} students...")
            students = create_students(moze_data['moze_list'])
            
            # Step 4: Create hospitals
            print(f"\n🏥 Creating {DATA_SPECS['hospitals_count']} hospitals...")
            hospitals = create_hospitals(moze_data['moze_list'])
            
            # Step 5: Create doctors
            print(f"\n👨‍⚕️ Creating doctors for hospitals...")
            doctors = create_doctors(hospitals)
            
            # Step 6: Create patients
            print(f"\n👥 Creating {DATA_SPECS['patients_count']} patients...")
            patients = create_patients(moze_data['moze_list'])
            
            # Step 7: Create medical records
            print(f"\n📋 Creating {DATA_SPECS['medical_records_count']} medical records...")
            medical_records = create_medical_records(patients, doctors, moze_data['moze_list'])
            
            # Step 8: Create appointments
            print(f"\n📅 Creating {DATA_SPECS['appointments_count']} appointments...")
            appointments = create_appointments(patients, doctors, moze_data['moze_list'])
            
            # Step 9: Create evaluation forms
            print(f"\n📊 Creating {DATA_SPECS['evaluation_forms_count']} evaluation forms...")
            evaluations = create_evaluation_forms(moze_data['aamils'])
            
            # Step 10: Create surveys
            print(f"\n📝 Creating {DATA_SPECS['surveys_count']} surveys...")
            surveys = create_surveys(moze_data['aamils'])
            
            # Step 11: Create Araz petitions
            print(f"\n📜 Creating {DATA_SPECS['araz_count']} Araz petitions...")
            petitions = create_araz_petitions(students)
            
            print_summary()
            
    except Exception as e:
        print(f"❌ Error during data generation: {e}")
        traceback.print_exc()
        raise

def create_admin_users():
    """Create admin users"""
    admins = []
    timestamp = int(time.time())
    for i in range(DATA_SPECS['admin_count']):
        user = User.objects.create(
            username=f'admin_{timestamp}_{i+1}',
            email=f'admin{timestamp}_{i+1}@umoor-sehhat.com',
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

def create_staff_users():
    """Create staff users"""
    staff = []
    timestamp = int(time.time())
    for i in range(DATA_SPECS['staff_count']):
        user = User.objects.create(
            username=f'staff_{timestamp}_{i+1}',
            email=f'staff{timestamp}_{i+1}@umoor-sehhat.com',
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

def create_moze_and_aamils():
    """Create Moze with their Aamils"""
    moze_list = []
    aamils = []
    
    for i in range(DATA_SPECS['moze_count']):
        # Create Aamil user
        timestamp = int(time.time())
        aamil_user = User.objects.create(
            username=f'aamil_{timestamp}_{i+1}',
            email=f'aamil{timestamp}_{i+1}@umoor-sehhat.com',
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
            name=f'Moze {fake.city()} #{i+1}',
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
        
        if (i + 1) % 50 == 0:
            print(f"   Created {i + 1} Moze...")
    
    return {'moze_list': moze_list, 'aamils': aamils}

def create_students(moze_list):
    """Create students distributed across Moze"""
    students = []
    
    for i in range(DATA_SPECS['students_count']):
        # Create student user
        timestamp = int(time.time())
        student_user = User.objects.create(
            username=f'student_{timestamp}_{i+1}',
            email=f'student{timestamp}_{i+1}@example.com',
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
            student_id=f'STU{i+1:06d}',
            academic_level=random.choice(['undergraduate', 'postgraduate', 'doctoral', 'diploma']),
            enrollment_status=random.choice(['active', 'active', 'active', 'suspended']),  # 75% active
            enrollment_date=fake.date_between(start_date='-4y', end_date='today'),
            expected_graduation=fake.date_between(start_date='today', end_date='+2y') if random.choice([True, False]) else None
        )
        
        students.append(student)
        
        if (i + 1) % 100 == 0:
            print(f"   Created {i + 1} students...")
    
    return students

def create_hospitals(moze_list):
    """Create hospitals - distributed for coverage but not directly linked to specific Moze"""
    hospitals = []
    
    for i in range(DATA_SPECS['hospitals_count']):
        hospital = Hospital.objects.create(
            name=f'{fake.company()} Medical Center #{i+1}',
            description=fake.text(max_nb_chars=500),
            address=fake.address(),
            phone=fake.phone_number()[:20],
            email=f'hospital{i+1}@medical.com',
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
        
        if (i + 1) % 30 == 0:
            print(f"   Created {i + 1} hospitals...")
    
    return hospitals

def create_doctors(hospitals):
    """Create doctors for hospitals"""
    doctors = []
    
    for hospital in hospitals:
        # Create 2-5 doctors per hospital
        num_doctors = random.randint(2, 5)
        
        for i in range(num_doctors):
            # Create doctor user
            timestamp = int(time.time())
            doctor_user = User.objects.create(
                username=f'doctor_{timestamp}_{hospital.id}_{i+1}',
                email=f'doctor{timestamp}_{hospital.id}_{i+1}@medical.com',
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
                    license_number=f'LIC{len(doctors)+1:06d}',
                    specialization=doctor_user.specialty,
                    qualification=random.choice(['MBBS', 'MD', 'MS', 'FRCS', 'PhD']),
                    experience_years=random.randint(1, 30),
                    hospital=hospital,
                    department=department,
                    is_available=random.choice([True, True, False]),  # 67% available
                    is_emergency_doctor=random.choice([True, False]),
                    consultation_fee=random.uniform(50, 500)
                )
                doctors.append(doctor)
        
        if len(doctors) % 20 == 0:
            print(f"   Created {len(doctors)} doctors...")
    
    return doctors

def create_patients(moze_list):
    """Create patients distributed across Moze"""
    patients = []
    
    for i in range(DATA_SPECS['patients_count']):
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
            is_active=random.choice([True, True, True, False]),  # 75% active
            registered_moze=moze
        )
        
        patients.append(patient)
        
        if (i + 1) % 200 == 0:
            print(f"   Created {i + 1} patients...")
    
    return patients

def create_medical_records(patients, doctors, moze_list):
    """Create medical records for patients"""
    medical_records = []
    
    for i, patient in enumerate(patients[:DATA_SPECS['medical_records_count']]):
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
        
        if (i + 1) % 200 == 0:
            print(f"   Created {i + 1} medical records...")
    
    return medical_records

def create_appointments(patients, doctors, moze_list):
    """Create appointments"""
    appointments = []
    
    for i in range(DATA_SPECS['appointments_count']):
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
        
        if (i + 1) % 50 == 0:
            print(f"   Created {i + 1} appointments...")
    
    return appointments

def create_evaluation_forms(aamils):
    """Create evaluation forms with analytics"""
    evaluation_forms = []
    
    for i in range(DATA_SPECS['evaluation_forms_count']):
        creator = random.choice(aamils)
        
        form = EvaluationForm.objects.create(
            title=f'Evaluation Form #{i+1}: {fake.catch_phrase()}',
            description=fake.text(max_nb_chars=500),
            evaluation_type=random.choice(['performance', 'satisfaction', 'quality', 'training', 'service', 'facility']),
            target_role=random.choice(['all', 'doctor', 'student', 'aamil']),
            created_by=creator,
            is_active=random.choice([True, True, False]),  # 67% active
            is_anonymous=random.choice([True, False]),
            due_date=fake.date_time_between(start_date='now', end_date='+3m', tzinfo=timezone.get_current_timezone()) if random.choice([True, False]) else None
        )
        
        # Create submissions for analytics
        used_evaluators = set()
        submissions_to_create = min(random.randint(5, 50), len(aamils))  # Can't have more submissions than evaluators
        
        for _ in range(submissions_to_create):
            # Get an evaluator that hasn't submitted for this form yet
            available_evaluators = [e for e in aamils if e.id not in used_evaluators]
            if not available_evaluators:
                break
                
            evaluator = random.choice(available_evaluators)
            used_evaluators.add(evaluator.id)
            
            EvaluationSubmission.objects.create(
                form=form,
                evaluator=evaluator,
                total_score=round(random.uniform(60, 100), 2),
                comments=fake.text(max_nb_chars=300),
                is_complete=random.choice([True, True, False])  # 67% complete
            )
        
        evaluation_forms.append(form)
        
        if (i + 1) % 5 == 0:
            print(f"   Created {i + 1} evaluation forms...")
    
    return evaluation_forms

def create_surveys(aamils):
    """Create surveys with analytics"""
    surveys = []
    
    for i in range(DATA_SPECS['surveys_count']):
        creator = random.choice(aamils)
        
        # Create survey questions in JSON format
        questions = []
        question_types = ['text', 'multiple_choice', 'rating', 'checkbox']
        for j in range(random.randint(5, 15)):
            question_type = random.choice(question_types)
            question = {
                "id": j + 1,
                "type": question_type,
                "question": fake.sentence() + '?',
                "required": random.choice([True, False]),
                "options": []
            }
            
            if question_type in ['multiple_choice', 'checkbox']:
                question["options"] = [fake.word() for _ in range(random.randint(2, 5))]
            elif question_type == 'rating':
                question["options"] = ["1", "2", "3", "4", "5"]
            
            questions.append(question)
        
        survey = Survey.objects.create(
            title=f'Survey #{i+1}: {fake.catch_phrase()}',
            description=fake.text(max_nb_chars=500),
            created_by=creator,
            questions=questions,
            target_role=random.choice(['all', 'aamil', 'student', 'doctor']),
            is_active=random.choice([True, True, False]),  # 67% active
            is_anonymous=random.choice([True, False]),
            allow_multiple_responses=random.choice([True, False]),
            show_results=random.choice([True, False]),
            start_date=fake.date_time_between(start_date='-6m', end_date='now', tzinfo=timezone.get_current_timezone()),
            end_date=fake.date_time_between(start_date='now', end_date='+6m', tzinfo=timezone.get_current_timezone())
        )
        
        # Create responses for analytics
        used_respondents = set()
        responses_count = min(random.randint(10, 100), len(aamils))  # Can't have more responses than respondents
        complete_responses = 0
        
        for _ in range(responses_count):
            # Get a respondent that hasn't responded to this survey yet
            available_respondents = [r for r in aamils if r.id not in used_respondents]
            if not available_respondents:
                break
                
            respondent = random.choice(available_respondents)
            used_respondents.add(respondent.id)
            
            # Generate realistic answers
            answers = {}
            is_complete = random.choice([True, True, False])  # 67% complete
            if is_complete:
                complete_responses += 1
                
            for question in questions:
                if is_complete or random.choice([True, False]):
                    if question["type"] == "text":
                        answers[str(question["id"])] = fake.sentence()
                    elif question["type"] == "multiple_choice":
                        answers[str(question["id"])] = random.choice(question["options"])
                    elif question["type"] == "checkbox":
                        selected = random.sample(question["options"], random.randint(1, len(question["options"])))
                        answers[str(question["id"])] = selected
                    elif question["type"] == "rating":
                        answers[str(question["id"])] = random.choice(question["options"])
            
            SurveyResponse.objects.create(
                survey=survey,
                respondent=respondent,
                answers=answers,
                is_complete=is_complete,
                completion_time=random.randint(60, 1800) if is_complete else None,  # 1-30 minutes
                created_at=fake.date_time_between(start_date='-3m', end_date='now', tzinfo=timezone.get_current_timezone())
            )
        
        # Create analytics
        actual_responses = len(used_respondents)
        SurveyAnalytics.objects.create(
            survey=survey,
            total_invitations=actual_responses + random.randint(10, 50),
            total_responses=actual_responses,
            total_complete_responses=complete_responses,
            avg_completion_time=random.uniform(300, 900),  # 5-15 minutes average
            detailed_analytics={
                "question_analytics": {
                    f"q_{q['id']}": {
                        "response_count": random.randint(max(1, complete_responses//2), max(1, complete_responses)),
                        "most_common": fake.word() if q["type"] != "text" else None
                    } for q in questions
                }
            }
        )
        
        surveys.append(survey)
        
        if (i + 1) % 5 == 0:
            print(f"   Created {i + 1} surveys...")
    
    return surveys

def create_araz_petitions(students):
    """Create Araz petitions with random specifications"""
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
    
    for i in range(DATA_SPECS['araz_count']):
        student = random.choice(students)
        category = random.choice(categories)
        status_choice = random.choice(['pending', 'in_progress', 'resolved', 'rejected'])
        
        petition = Petition.objects.create(
            title=f'Petition #{i+1}: {fake.catch_phrase()}',
            description=fake.text(max_nb_chars=1000),
            created_by=student.user,
            category=category,
            status=status_choice,
            priority=random.choice(['low', 'medium', 'high']),
            resolved_at=fake.date_time_between(start_date='-1m', end_date='now', tzinfo=timezone.get_current_timezone()) if status_choice in ['resolved', 'rejected'] else None
        )
        
        petitions.append(petition)
        
        if (i + 1) % 200 == 0:
            print(f"   Created {i + 1} Araz petitions...")
    
    return petitions

def print_summary():
    """Print comprehensive summary of created data"""
    print("\n" + "="*60)
    print("📊 COMPREHENSIVE TEST DATA GENERATION COMPLETED!")
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
        'Evaluation Submissions': EvaluationSubmission.objects.count(),
        'Surveys': Survey.objects.count(),
        'Survey Analytics': SurveyAnalytics.objects.count(),
        'Survey Responses': SurveyResponse.objects.count(),
        'Araz Petitions': Petition.objects.count(),
        'Petition Categories': PetitionCategory.objects.count(),
        'Petition Statuses': PetitionStatus.objects.count(),
    }
    
    for item, count in counts.items():
        print(f"   {item}: {count:,}")
    
    print("\n🎯 Data Distribution:")
    print(f"   Average students per Moze: {counts['Students'] / counts['Moze']:.1f}")
    print(f"   Average patients per Moze: {counts['Patients'] / counts['Moze']:.1f}")
    print(f"   Hospitals coverage: {counts['Hospitals'] / counts['Moze'] * 100:.1f}% of Moze")
    
    print("\n🎉 Ready for comprehensive testing!")

if __name__ == '__main__':
    create_comprehensive_test_data()