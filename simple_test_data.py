#!/usr/bin/env python3
"""
Simple Test Data Generator for Umoor Sehhat System
Creates minimal but representative dataset for testing:
- 5 Mozes with 5 Aamils
- 10 Medical Students
- 2 Staff, 2 Admins
- 3 Hospitals
- 20 Patients
- 20 Medical Records
- 5 Appointments
- 2 Evaluation forms
- 2 Survey forms
- 5 Araz
- All users have ITS IDs
"""
import os
import sys
import django
import random
from datetime import date, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.db import transaction
from accounts.models import User, UserProfile, AuditLog
from moze.models import Moze, MozeComment, MozeSettings
from mahalshifa.models import (
    Hospital, Department, Doctor, Patient, Appointment, MedicalRecord
)
from doctordirectory.models import (
    Doctor as DoctorDirectory, DoctorSchedule, PatientLog, DoctorAvailability,
    MedicalService as DirectoryMedicalService, Patient as DirectoryPatient,
    Appointment as DirectoryAppointment, MedicalRecord as DirectoryMedicalRecord,
    Prescription as DirectoryPrescription, LabTest as DirectoryLabTest,
    VitalSigns as DirectoryVitalSigns
)
from evaluation.models import (
    EvaluationCriteria, EvaluationForm, EvaluationSubmission, EvaluationResponse,
    Evaluation, EvaluationSession, EvaluationTemplate, EvaluationReport
)
from surveys.models import Survey, SurveyResponse, SurveyReminder, SurveyAnalytics
from araz.models import (
    DuaAraz, PetitionCategory, Petition, ArazComment, PetitionComment
)
from students.models import (
    Student, Course, Enrollment, Assignment, Submission, Grade, Schedule,
    Attendance, Announcement, StudentGroup, GroupMembership, Event,
    LibraryRecord, Achievement, Scholarship, Fee, Payment, StudentProfile
)
from photos.models import Photo, PhotoAlbum, PhotoComment, PhotoLike, PhotoTag

def generate_its_id():
    """Generate a unique 8-digit ITS ID"""
    return str(random.randint(10000000, 99999999))

def create_simple_test_data():
    """Create simple test data for all apps"""
    print("🚀 Starting simple test data generation...")
    
    try:
        with transaction.atomic():
            # Create base users and data
            print("\n📋 Creating base users and administrators...")
            admins = create_admins()
            staff = create_staff()
            
            print("\n🏢 Creating Mozes and Aamils...")
            mozes = create_mozes_and_aamils()
            
            print("\n👨‍⚕️ Creating Doctors...")
            doctors = create_doctors(mozes)
            
            print("\n🏥 Creating Hospitals and Departments...")
            hospitals = create_hospitals_and_departments(mozes)
            
            print("\n👨‍🎓 Creating Medical Students...")
            students = create_medical_students(mozes)
            
            print("\n👥 Creating Patients...")
            patients = create_patients(hospitals, mozes)
            
            print("\n📋 Creating Medical Records...")
            medical_records = create_medical_records(patients, doctors)
            
            print("\n📅 Creating Appointments...")
            appointments = create_appointments(patients, doctors)
            
            print("\n📊 Creating Evaluation Forms and Data...")
            evaluation_data = create_evaluation_data(mozes, doctors)
            
            print("\n📝 Creating Survey Forms and Data...")
            survey_data = create_survey_data(mozes, doctors, students)
            
            print("\n📜 Creating Araz (Petitions)...")
            araz_data = create_araz_data(patients, doctors)
            
            print("\n📸 Creating Photo Albums and Photos...")
            photo_data = create_photo_data(mozes)
            
            print("\n🎓 Creating Student Academic Data...")
            student_data = create_student_academic_data(students)
            
            # Print summary
            print_summary()
            
            return True
            
    except Exception as e:
        print(f"❌ Error during data creation: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_admins():
    """Create 2 admin users"""
    admins = []
    admin_data = [
        {
            'username': 'admin_1',
            'first_name': 'Ahmed',
            'last_name': 'Al-Rashid',
            'email': 'admin1@umoorsehhat.com',
            'role': 'badri_mahal_admin'
        },
        {
            'username': 'admin_2',
            'first_name': 'Fatima',
            'last_name': 'Al-Zahra',
            'email': 'admin2@umoorsehhat.com',
            'role': 'badri_mahal_admin'
        }
    ]
    
    for data in admin_data:
        user, created = User.objects.get_or_create(
            username=data['username'],
            defaults={
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'email': data['email'],
                'role': data['role'],
                'its_id': generate_its_id(),
                'is_active': True,
                'is_staff': True,
                'is_superuser': True,
                'password': make_password('admin123456')
            }
        )
        if created:
            print(f"✅ Created admin: {user.get_full_name()}")
        admins.append(user)
    
    return admins

def create_staff():
    """Create 2 staff users"""
    staff = []
    staff_names = [
        ('Omar', 'Al-Hassan'), ('Layla', 'Al-Mahmoud')
    ]
    
    for i, (first_name, last_name) in enumerate(staff_names, 1):
        user, created = User.objects.get_or_create(
            username=f'staff_{i}',
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'email': f'staff{i}@umoorsehhat.com',
                'role': 'moze_coordinator',
                'its_id': generate_its_id(),
                'is_active': True,
                'password': make_password('staff123456')
            }
        )
        if created:
            print(f"✅ Created staff: {user.get_full_name()}")
        staff.append(user)
    
    return staff

def create_mozes_and_aamils():
    """Create 5 Mozes with 5 Aamils"""
    mozes = []
    cities = ['Riyadh', 'Jeddah', 'Mecca', 'Medina', 'Dammam']
    
    for i in range(1, 6):
        # Create Aamil
        aamil_user, created = User.objects.get_or_create(
            username=f'aamil_{i}',
            defaults={
                'first_name': f'Aamil{i}',
                'last_name': f'Al-Moze{i}',
                'email': f'aamil{i}@umoorsehhat.com',
                'role': 'aamil',
                'its_id': generate_its_id(),
                'is_active': True,
                'password': make_password('aamil123456')
            }
        )
        if created:
            print(f"✅ Created aamil: {aamil_user.get_full_name()}")
        
        # Create Moze
        city = cities[i-1]
        moze, created = Moze.objects.get_or_create(
            name=f"Moze {i} - {city}",
            defaults={
                'location': city,
                'address': f"Address {i}, {city}, Saudi Arabia",
                'aamil': aamil_user,
                'contact_phone': f'+9665{random.randint(10000000, 99999999)}',
                'contact_email': f'moze{i}@umoorsehhat.com',
                'capacity': random.randint(50, 200),
                'is_active': True,
                'established_date': date.today() - timedelta(days=random.randint(100, 1000))
            }
        )
        if created:
            print(f"✅ Created moze: {moze.name}")
        mozes.append(moze)
    
    return mozes

def create_doctors(mozes):
    """Create doctors for the system"""
    doctors = []
    specialties = [
        'Cardiology', 'Neurology', 'General Medicine', 'Pediatrics', 'Orthopedics'
    ]
    
    # Create doctors for each moze
    for i, moze in enumerate(mozes):
        num_doctors = random.randint(1, 2)  # 1-2 doctors per moze
        
        for j in range(num_doctors):
            doctor_user, created = User.objects.get_or_create(
                username=f'doctor_{moze.id}_{j+1}',
                defaults={
                    'first_name': f'Doctor{j+1}',
                    'last_name': f'Moze{moze.id}',
                    'email': f'doctor{moze.id}_{j+1}@umoorsehhat.com',
                    'role': 'doctor',
                    'its_id': generate_its_id(),
                    'is_active': True,
                    'password': make_password('doctor123456')
                }
            )
            if created:
                print(f"✅ Created doctor user: {doctor_user.get_full_name()}")
            
            # Create doctor profile in doctordirectory
            doctor_profile, created = DoctorDirectory.objects.get_or_create(
                user=doctor_user,
                defaults={
                    'name': f'Dr. {doctor_user.get_full_name()}',
                    'its_id': generate_its_id(),
                    'specialty': random.choice(specialties),
                    'qualification': 'MBBS, MD',
                    'experience_years': random.randint(3, 20),
                    'is_verified': True,
                    'is_available': True,
                    'assigned_moze': moze,
                    'consultation_fee': Decimal(random.uniform(50, 300)),
                    'phone': f'+9665{random.randint(10000000, 99999999)}',
                    'email': f'doctor{moze.id}_{j+1}@umoorsehhat.com',
                    'languages_spoken': 'English, Arabic',
                    'bio': f'Experienced {random.choice(specialties)} specialist'
                }
            )
            if created:
                print(f"✅ Created doctor profile: {doctor_profile.name}")
            doctors.append(doctor_profile)
    
    return doctors

def create_hospitals_and_departments(mozes):
    """Create 3 hospitals across 5 mozes"""
    hospitals = []
    hospital_types = ['general', 'specialty', 'clinic']
    
    # Create 3 hospitals
    for i in range(1, 4):
        moze = random.choice(mozes)
        hospital_type = random.choice(hospital_types)
        
        hospital, created = Hospital.objects.get_or_create(
            name=f"Hospital {i} - {moze.location}",
            defaults={
                'description': f"Comprehensive medical facility in {moze.location}",
                'address': f"Hospital Address {i}, {moze.location}",
                'phone': f'+9665{random.randint(10000000, 99999999)}',
                'email': f'hospital{i}@umoorsehhat.com',
                'hospital_type': hospital_type,
                'total_beds': random.randint(50, 500),
                'available_beds': random.randint(10, 100),
                'emergency_beds': random.randint(5, 50),
                'icu_beds': random.randint(2, 20),
                'is_active': True,
                'is_emergency_capable': random.choice([True, False]),
                'has_pharmacy': random.choice([True, False]),
                'has_laboratory': random.choice([True, False])
            }
        )
        if created:
            print(f"✅ Created hospital: {hospital.name}")
        
        # Create departments for this hospital
        departments = ['Emergency', 'Cardiology', 'Neurology', 'Pediatrics', 'Surgery', 'ICU']
        for dept_name in departments:
            dept, created = Department.objects.get_or_create(
                hospital=hospital,
                name=dept_name,
                defaults={
                    'description': f"{dept_name} department",
                    'floor_number': str(random.randint(1, 5)),
                    'phone_extension': str(random.randint(100, 999)),
                    'is_active': True
                }
            )
            if created:
                print(f"  ✅ Created department: {dept.name}")
        
        hospitals.append(hospital)
    
    return hospitals

def create_medical_students(mozes):
    """Create 10 medical students across 5 mozes"""
    students = []
    colleges = ['Medical College A', 'Medical College B', 'Medical College C']
    specializations = ['General Medicine', 'Surgery', 'Pediatrics', 'Cardiology', 'Neurology']
    
    # Distribute students across mozes (2 students per moze)
    student_counter = 1
    for i, moze in enumerate(mozes):
        for j in range(2):  # 2 students per moze
            student_user, created = User.objects.get_or_create(
                username=f'student_{student_counter}',
                defaults={
                    'first_name': f'Student{student_counter}',
                    'last_name': f'Medical{student_counter}',
                    'email': f'student{student_counter}@umoorsehhat.com',
                    'role': 'student',
                    'its_id': generate_its_id(),
                    'is_active': True,
                    'password': make_password('student123456')
                }
            )
            if created:
                print(f"✅ Created student user: {student_user.get_full_name()}")
            
            # Create student profile
            student_profile, created = StudentProfile.objects.get_or_create(
                user=student_user,
                defaults={
                    'its_id': generate_its_id(),
                    'college': random.choice(colleges),
                    'specialization': random.choice(specializations),
                    'year_of_study': random.randint(1, 6),
                    'enrollment_date': date.today() - timedelta(days=random.randint(100, 1000)),
                    'expected_graduation': date.today() + timedelta(days=random.randint(200, 800)),
                    'current_cgpa': round(random.uniform(2.0, 4.0), 2),
                    'total_credit_hours': random.randint(30, 120),
                    'is_active': True,
                    'is_verified': True
                }
            )
            if created:
                print(f"✅ Created student profile: {student_profile.user.get_full_name()}")
            students.append(student_profile)
            student_counter += 1
    
    return students

def create_patients(hospitals, mozes):
    """Create 20 patients across 3 hospitals from 5 mozes"""
    patients = []
    blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    genders = ['male', 'female']
    
    for i in range(1, 21):
        hospital = random.choice(hospitals)
        moze = random.choice(mozes)
        
        # Create patient user
        patient_user, created = User.objects.get_or_create(
            username=f'patient_{i}',
            defaults={
                'first_name': f'Patient{i}',
                'last_name': f'Medical{i}',
                'email': f'patient{i}@umoorsehhat.com',
                'role': 'student',  # Patients are typically students
                'its_id': generate_its_id(),
                'is_active': True,
                'password': make_password('patient123456')
            }
        )
        if created:
            print(f"✅ Created patient user: {patient_user.get_full_name()}")
        
        # Create patient record in mahalshifa
        patient, created = Patient.objects.get_or_create(
            its_id=generate_its_id(),
            defaults={
                'first_name': f'Patient{i}',
                'last_name': f'Medical{i}',
                'arabic_name': f'مريض{i}',
                'date_of_birth': date.today() - timedelta(days=random.randint(6570, 25550)),  # 18-70 years
                'gender': random.choice(genders),
                'phone_number': f'+9665{random.randint(10000000, 99999999)}',
                'email': f'patient{i}@umoorsehhat.com',
                'address': f"Patient Address {i}, Saudi Arabia",
                'emergency_contact_name': f'Emergency Contact {i}',
                'emergency_contact_phone': f'+9665{random.randint(10000000, 99999999)}',
                'emergency_contact_relationship': random.choice(['Spouse', 'Parent', 'Sibling', 'Child']),
                'blood_group': random.choice(blood_groups),
                'allergies': random.choice(['None', 'Penicillin', 'Latex', 'Peanuts', 'Dairy']),
                'chronic_conditions': random.choice(['None', 'Diabetes', 'Hypertension', 'Asthma', 'Heart Disease']),
                'current_medications': random.choice(['None', 'Insulin', 'Blood Pressure Medication', 'Inhaler']),
                'registered_moze': moze,
                'registration_date': date.today() - timedelta(days=random.randint(1, 365)),
                'is_active': True,
                'user_account': patient_user
            }
        )
        if created:
            print(f"✅ Created patient: {patient.get_full_name()}")
        patients.append(patient)
    
    return patients

def create_medical_records(patients, doctors):
    """Create 20 medical records for 20 patients"""
    medical_records = []
    
    for i, patient in enumerate(patients):
        doctor = random.choice(doctors)
        moze = doctor.assigned_moze
        
        # Create appointment first
        appointment, created = Appointment.objects.get_or_create(
            patient=patient,
            doctor=doctor,
            moze=moze,
            appointment_date=date.today() - timedelta(days=random.randint(1, 30)),
            appointment_time=timezone.now().time(),
            defaults={
                'reason': f"Medical consultation for {patient.get_full_name()}",
                'symptoms': random.choice([
                    'Fever and cough', 'Headache and dizziness', 'Chest pain',
                    'Abdominal pain', 'Fatigue and weakness', 'Joint pain'
                ]),
                'notes': f"Patient consultation notes for {patient.get_full_name()}",
                'status': random.choice(['completed', 'scheduled', 'confirmed']),
                'appointment_type': random.choice(['regular', 'follow_up', 'urgent']),
                'booking_method': random.choice(['online', 'phone', 'walk_in']),
                'duration_minutes': random.randint(15, 60)
            }
        )
        if created:
            print(f"✅ Created appointment for {patient.get_full_name()}")
        
        # Create medical record
        medical_record, created = MedicalRecord.objects.get_or_create(
            patient=patient,
            doctor=doctor,
            moze=moze,
            defaults={
                'appointment': appointment,
                'chief_complaint': f"Patient {patient.get_full_name()} presenting with symptoms",
                'history_of_present_illness': f"Patient reports symptoms for the past few days",
                'past_medical_history': f"Previous medical history for {patient.get_full_name()}",
                'family_history': f"Family medical history for {patient.get_full_name()}",
                'social_history': f"Social and lifestyle information for {patient.get_full_name()}",
                'physical_examination': f"Physical examination findings for {patient.get_full_name()}",
                'diagnosis': random.choice([
                    'Common cold', 'Hypertension', 'Diabetes', 'Anxiety',
                    'Migraine', 'Gastritis', 'Bronchitis', 'Sinusitis'
                ]),
                'differential_diagnosis': f"Differential diagnoses for {patient.get_full_name()}",
                'treatment_plan': f"Treatment plan for {patient.get_full_name()}",
                'medications_prescribed': random.choice([
                    'Paracetamol 500mg', 'Ibuprofen 400mg', 'Omeprazole 20mg',
                    'Metformin 500mg', 'Amlodipine 5mg'
                ]),
                'lab_tests_ordered': random.choice(['None', 'Blood test', 'Urine test', 'X-ray']),
                'imaging_ordered': random.choice(['None', 'Chest X-ray', 'CT scan', 'MRI']),
                'referrals': random.choice(['None', 'Cardiology', 'Neurology', 'Orthopedics']),
                'follow_up_required': random.choice([True, False]),
                'patient_education': f"Patient education provided to {patient.get_full_name()}",
                'doctor_notes': f"Doctor's private notes for {patient.get_full_name()}"
            }
        )
        if created:
            print(f"✅ Created medical record for {patient.get_full_name()}")
        medical_records.append(medical_record)
    
    return medical_records

def create_appointments(patients, doctors):
    """Create 5 additional appointments"""
    appointments = []
    
    for i in range(5):
        patient = random.choice(patients)
        doctor = random.choice(doctors)
        moze = doctor.assigned_moze
        
        appointment, created = Appointment.objects.get_or_create(
            patient=patient,
            doctor=doctor,
            moze=moze,
            appointment_date=date.today() + timedelta(days=random.randint(1, 30)),
            appointment_time=timezone.now().time(),
            defaults={
                'reason': f"Follow-up appointment for {patient.get_full_name()}",
                'symptoms': random.choice([
                    'Follow-up consultation', 'Routine checkup', 'Medication review',
                    'Test results review', 'Preventive care', 'Vaccination'
                ]),
                'notes': f"Appointment notes for {patient.get_full_name()}",
                'status': random.choice(['scheduled', 'confirmed', 'pending']),
                'appointment_type': random.choice(['regular', 'follow_up', 'screening']),
                'booking_method': random.choice(['online', 'phone', 'staff']),
                'duration_minutes': random.randint(15, 60)
            }
        )
        if created:
            print(f"✅ Created additional appointment for {patient.get_full_name()}")
        appointments.append(appointment)
    
    return appointments

def create_evaluation_data(mozes, doctors):
    """Create 2 evaluation forms with analytics"""
    evaluation_data = []
    
    # Create evaluation criteria
    criteria_data = [
        ('Infrastructure Quality', 'infrastructure', 2.0),
        ('Medical Care Standards', 'medical_quality', 3.0),
        ('Staff Performance', 'staff_performance', 2.5),
        ('Patient Satisfaction', 'patient_satisfaction', 2.0),
        ('Administrative Efficiency', 'administration', 1.5),
        ('Safety Protocols', 'safety', 2.0),
        ('Equipment Availability', 'equipment', 1.5),
        ('Accessibility', 'accessibility', 1.5)
    ]
    
    criteria_list = []
    for name, category, weight in criteria_data:
        criteria, created = EvaluationCriteria.objects.get_or_create(
            name=name,
            defaults={
                'description': f"Evaluation criteria for {name}",
                'weight': weight,
                'max_score': 10,
                'category': category,
                'is_active': True,
                'order': len(criteria_list) + 1
            }
        )
        if created:
            print(f"✅ Created evaluation criteria: {criteria.name}")
        criteria_list.append(criteria)
    
    # Create evaluation forms
    for i in range(1, 3):
        evaluator = random.choice(doctors).user
        moze = random.choice(mozes)
        
        evaluation, created = Evaluation.objects.get_or_create(
            moze=moze,
            evaluation_period='quarterly',
            evaluation_date=date.today() - timedelta(days=random.randint(30, 365)),
            defaults={
                'evaluator': evaluator,
                'overall_grade': random.choice(['A+', 'A', 'B', 'C']),
                'overall_score': random.uniform(75, 95),
                'infrastructure_score': random.uniform(70, 90),
                'medical_quality_score': random.uniform(75, 95),
                'staff_performance_score': random.uniform(70, 90),
                'patient_satisfaction_score': random.uniform(75, 95),
                'administration_score': random.uniform(70, 90),
                'safety_score': random.uniform(75, 95),
                'equipment_score': random.uniform(70, 90),
                'accessibility_score': random.uniform(75, 95),
                'strengths': f"Strong points for {moze.name} evaluation {i}",
                'weaknesses': f"Areas for improvement for {moze.name} evaluation {i}",
                'recommendations': f"Recommendations for {moze.name} evaluation {i}",
                'action_items': f"Action items for {moze.name} evaluation {i}",
                'is_draft': False,
                'is_published': True
            }
        )
        if created:
            print(f"✅ Created evaluation: {evaluation} for {moze.name}")
        evaluation_data.append(evaluation)
    
    return evaluation_data

def create_survey_data(mozes, doctors, students):
    """Create 2 survey forms with analytics"""
    survey_data = []
    
    survey_types = [
        'Patient Satisfaction Survey',
        'Staff Performance Survey'
    ]
    
    for i in range(1, 3):
        creator = random.choice(doctors).user
        survey_type = survey_types[i-1]
        
        # Create sample questions
        questions = [
            {
                "id": 1,
                "type": "rating",
                "question": "How satisfied are you with the medical care received?",
                "required": True,
                "options": ["1", "2", "3", "4", "5"]
            },
            {
                "id": 2,
                "type": "multiple_choice",
                "question": "How would you rate the cleanliness of the facility?",
                "required": True,
                "options": ["Excellent", "Good", "Average", "Poor", "Very Poor"]
            },
            {
                "id": 3,
                "type": "checkbox",
                "question": "Which services did you use during your visit?",
                "required": False,
                "options": ["Consultation", "Laboratory Tests", "Imaging", "Pharmacy", "Emergency Care"]
            },
            {
                "id": 4,
                "type": "text",
                "question": "Please provide any additional comments or suggestions:",
                "required": False,
                "options": []
            }
        ]
        
        survey, created = Survey.objects.get_or_create(
            title=f"{survey_type} {i}",
            defaults={
                'description': f"Comprehensive {survey_type.lower()} for quality assessment",
                'target_role': random.choice(['all', 'doctor', 'student', 'aamil']),
                'questions': questions,
                'created_by': creator,
                'is_active': True,
                'is_anonymous': random.choice([True, False]),
                'allow_multiple_responses': False,
                'show_results': True,
                'start_date': timezone.now() - timedelta(days=random.randint(1, 30)),
                'end_date': timezone.now() + timedelta(days=random.randint(1, 30))
            }
        )
        if created:
            print(f"✅ Created survey: {survey.title}")
        
        # Create survey responses
        num_responses = random.randint(5, 15)
        for j in range(num_responses):
            respondent = random.choice(doctors + students).user if random.choice([True, False]) else None
            
            answers = {
                "1": random.randint(1, 5),
                "2": random.choice(["Excellent", "Good", "Average", "Poor", "Very Poor"]),
                "3": random.sample(["Consultation", "Laboratory Tests", "Imaging", "Pharmacy", "Emergency Care"], 
                                  random.randint(1, 3)),
                "4": f"Sample comment {j} for survey {i}"
            }
            
            response, created = SurveyResponse.objects.get_or_create(
                survey=survey,
                respondent=respondent,
                defaults={
                    'answers': answers,
                    'is_complete': True,
                    'completion_time': random.randint(60, 300)
                }
            )
            if created:
                print(f"  ✅ Created survey response {j+1} for {survey.title}")
        
        survey_data.append(survey)
    
    return survey_data

def create_araz_data(patients, doctors):
    """Create 5 araz (petitions) from 20 patients"""
    araz_data = []
    request_types = [
        'consultation', 'prescription', 'follow_up', 'health_check', 'emergency'
    ]
    
    for i in range(1, 6):
        patient = random.choice(patients)
        doctor = random.choice(doctors)
        
        araz, created = DuaAraz.objects.get_or_create(
            patient_its_id=patient.its_id,
            defaults={
                'patient_name': patient.get_full_name(),
                'patient_phone': patient.phone_number,
                'patient_email': patient.email,
                'patient_user': patient.user_account,
                'ailment': f"Medical condition description for {patient.get_full_name()}",
                'symptoms': random.choice([
                    'Fever and fatigue', 'Chest pain', 'Headache', 'Abdominal pain',
                    'Joint pain', 'Shortness of breath', 'Dizziness', 'Nausea'
                ]),
                'urgency_level': random.choice(['low', 'medium', 'high', 'emergency']),
                'request_type': random.choice(request_types),
                'previous_medical_history': f"Previous medical history for {patient.get_full_name()}",
                'current_medications': random.choice(['None', 'Blood pressure medication', 'Diabetes medication']),
                'allergies': random.choice(['None', 'Penicillin', 'Latex', 'Peanuts']),
                'preferred_doctor': doctor,
                'preferred_location': doctor.assigned_moze.location,
                'status': random.choice(['submitted', 'under_review', 'approved', 'scheduled', 'completed']),
                'priority': random.choice(['low', 'medium', 'high', 'urgent']),
                'assigned_doctor': doctor,
                'admin_notes': f"Administrative notes for {patient.get_full_name()}'s request",
                'preferred_contact_method': random.choice(['phone', 'email', 'sms'])
            }
        )
        if created:
            print(f"✅ Created araz: {araz.patient_name} - {araz.request_type}")
        araz_data.append(araz)
    
    return araz_data

def create_photo_data(mozes):
    """Create photo albums and photos for mozes"""
    photo_data = []
    
    for moze in mozes:
        # Create photo album
        album, created = PhotoAlbum.objects.get_or_create(
            name=f"Moze {moze.id} Activities",
            moze=moze,
            defaults={
                'description': f"Photo album documenting activities at {moze.name}",
                'created_by': moze.aamil,
                'is_public': True,
                'allow_uploads': True,
                'event_date': date.today() - timedelta(days=random.randint(1, 30))
            }
        )
        if created:
            print(f"✅ Created photo album: {album.name}")
        
        # Create some sample photos (without actual image files)
        for i in range(random.randint(2, 5)):
            photo, created = Photo.objects.get_or_create(
                title=f"Activity Photo {i+1}",
                moze=moze,
                defaults={
                    'description': f"Photo documenting activity at {moze.name}",
                    'subject_tag': f"activity_{i+1}",
                    'uploaded_by': moze.aamil,
                    'location': moze.location,
                    'event_date': date.today() - timedelta(days=random.randint(1, 30)),
                    'photographer': f"Photographer {i+1}",
                    'category': random.choice(['medical', 'event', 'infrastructure', 'team']),
                    'is_public': True,
                    'is_featured': random.choice([True, False]),
                    'requires_permission': False
                }
            )
            if created:
                print(f"  ✅ Created photo: {photo.title}")
        
        photo_data.append(album)
    
    return photo_data

def create_student_academic_data(students):
    """Create academic data for students"""
    student_data = []
    
    # Create courses
    courses = []
    course_data = [
        ('MED101', 'Introduction to Medicine', 'Basic medical concepts'),
        ('MED102', 'Anatomy and Physiology', 'Human body structure and function'),
        ('MED103', 'Biochemistry', 'Medical biochemistry principles'),
        ('MED104', 'Pathology', 'Disease mechanisms and processes'),
        ('MED105', 'Pharmacology', 'Drug actions and interactions')
    ]
    
    for code, name, description in course_data:
        course, created = Course.objects.get_or_create(
            code=code,
            defaults={
                'name': name,
                'description': description,
                'credits': random.randint(2, 4),
                'level': random.choice(['beginner', 'intermediate', 'advanced']),
                'is_active': True,
                'max_students': random.randint(20, 50)
            }
        )
        if created:
            print(f"✅ Created course: {course.code} - {course.name}")
        courses.append(course)
    
    # Create enrollments and grades for students
    for student in students:
        # Enroll in random courses
        num_courses = random.randint(2, 4)
        selected_courses = random.sample(courses, min(num_courses, len(courses)))
        
        for course in selected_courses:
            enrollment, created = Enrollment.objects.get_or_create(
                student=student,
                course=course,
                defaults={
                    'status': random.choice(['enrolled', 'completed', 'dropped']),
                    'grade': random.choice(['A', 'B', 'C', 'D', 'F', ''])
                }
            )
            if created:
                print(f"✅ Enrolled {student.user.get_full_name()} in {course.code}")
        
        student_data.append(student)
    
    return student_data

def print_summary():
    """Print summary of created data"""
    print("\n" + "="*60)
    print("📊 SIMPLE TEST DATA SUMMARY")
    print("="*60)
    
    print(f"👥 Users:")
    print(f"   - Admins: {User.objects.filter(role='badri_mahal_admin').count()}")
    print(f"   - Staff: {User.objects.filter(role='moze_coordinator').count()}")
    print(f"   - Aamils: {User.objects.filter(role='aamil').count()}")
    print(f"   - Doctors: {User.objects.filter(role='doctor').count()}")
    print(f"   - Students: {User.objects.filter(role='student').count()}")
    
    print(f"\n🏢 Mozes:")
    print(f"   - Total Mozes: {Moze.objects.count()}")
    print(f"   - Active Mozes: {Moze.objects.filter(is_active=True).count()}")
    
    print(f"\n🏥 Hospitals:")
    print(f"   - Total Hospitals: {Hospital.objects.count()}")
    print(f"   - Departments: {Department.objects.count()}")
    
    print(f"\n👨‍⚕️ Medical Data:")
    print(f"   - Patients: {Patient.objects.count()}")
    print(f"   - Medical Records: {MedicalRecord.objects.count()}")
    print(f"   - Appointments: {Appointment.objects.count()}")
    print(f"   - Doctors (Mahal Shifa): {Doctor.objects.count()}")
    print(f"   - Doctors (Directory): {DoctorDirectory.objects.count()}")
    
    print(f"\n📊 Evaluations & Surveys:")
    print(f"   - Evaluations: {Evaluation.objects.count()}")
    print(f"   - Survey Forms: {Survey.objects.count()}")
    print(f"   - Survey Responses: {SurveyResponse.objects.count()}")
    
    print(f"\n📜 Araz (Petitions):")
    print(f"   - Total Araz: {DuaAraz.objects.count()}")
    
    print(f"\n📸 Photos:")
    print(f"   - Photo Albums: {PhotoAlbum.objects.count()}")
    print(f"   - Photos: {Photo.objects.count()}")
    
    print(f"\n🎓 Academic Data:")
    print(f"   - Students: {StudentProfile.objects.count()}")
    print(f"   - Courses: {Course.objects.count()}")
    print(f"   - Enrollments: {Enrollment.objects.count()}")
    
    print(f"\n✅ All users have ITS IDs: {User.objects.filter(its_id__isnull=False).count()}/{User.objects.count()}")
    print("="*60)
    print("🎉 Simple test data generation completed successfully!")
    print("="*60)

if __name__ == "__main__":
    create_simple_test_data()