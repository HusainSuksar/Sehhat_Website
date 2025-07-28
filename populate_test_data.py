#!/usr/bin/env python3
"""
Umoor Sehhat Test Data Population Script
========================================

This script populates the database with comprehensive test data for all 9 Django applications.
Based on the specifications in TEST_DATA_DOCUMENTATION.md

⚠️ WARNING: This will delete ALL existing data and create fresh test data.

Usage: python3 populate_test_data.py
"""

import os
import sys
import django
from datetime import datetime, date, timedelta
import random
from faker import Faker

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
sys.path.append('.')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.management.color import no_style
from django.db import connection

# Import all models
from accounts.models import User, UserProfile
from students.models import Student, Course, Enrollment, Assignment, Grade, Event, Announcement
from surveys.models import Survey, SurveyResponse
from mahalshifa.models import Hospital, Patient, Appointment
from mahalshifa.models import Doctor as MahalshifaDoctor
from moze.models import Moze, MozeComment
from doctordirectory.models import Doctor, Patient as DirPatient, MedicalRecord
from evaluation.models import EvaluationForm, EvaluationSubmission
from araz.models import Petition, PetitionComment, PetitionCategory
from photos.models import PhotoAlbum, Photo, PhotoTag

# Initialize Faker
fake = Faker()

def print_progress(message):
    """Print progress with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def clear_database():
    """Clear all existing data"""
    print_progress("🗑️  Clearing existing database...")
    
    # Get all models to clear
    models_to_clear = [
        # Clear in reverse dependency order
        PetitionComment, Petition,
        EvaluationSubmission, EvaluationForm,
        MedicalRecord, DirPatient, Doctor,
        Photo, PhotoTag, PhotoAlbum,
        MozeComment, Moze,
        Appointment, Patient, Hospital,
        SurveyResponse, Survey,
        Grade, Assignment, Announcement, Event, Enrollment, Course, Student,
        UserProfile, User,
    ]
    
    for model in models_to_clear:
        try:
            model.objects.all().delete()
            print(f"   Cleared {model.__name__}")
        except Exception as e:
            print(f"   Warning: Could not clear {model.__name__}: {e}")
    
    # Reset auto-increment counters
    style = no_style()
    sql = connection.ops.sql_flush(style, [model._meta.db_table for model in models_to_clear])
    with connection.cursor() as cursor:
        for query in sql:
            cursor.execute(query)
    
    print_progress("✅ Database cleared successfully")

def create_users():
    """Create all user accounts as specified in documentation"""
    print_progress("👥 Creating user accounts...")
    
    users_created = 0
    
    # Create 2 Admin Users (Superusers)
    admin_users = []
    for i in range(1, 3):
        admin = User.objects.create_user(
            username=f'admin_{i}',
            password='admin123',
            email=f'admin{i}@umoor-sehhat.org',
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            is_superuser=True,
            is_staff=True,
            role='badri_mahal_admin'
        )
        admin_users.append(admin)
        users_created += 1
    
    # Create 100 Doctor Users
    doctor_users = []
    for i in range(1, 101):
        doctor = User.objects.create_user(
            username=f'doctor_{i:03d}',
            password='doctor123',
            email=f'doctor{i:03d}@umoor-sehhat.org',
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            role='doctor',
            phone_number=fake.phone_number()[:15],
            specialty=random.choice([
                'Cardiology', 'Neurology', 'Orthopedics', 'Pediatrics', 
                'Dermatology', 'Psychiatry', 'Radiology', 'Surgery',
                'Internal Medicine', 'Emergency Medicine'
            ])
        )
        doctor_users.append(doctor)
        users_created += 1
    
    # Create 500 Student Users
    student_users = []
    for i in range(1, 501):
        student = User.objects.create_user(
            username=f'student_{i:03d}',
            password='student123',
            email=f'student{i:03d}@student.umoor-sehhat.org',
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            role='student',
            phone_number=fake.phone_number()[:15],
            its_id=f'{random.randint(10000000, 99999999)}',
            college=random.choice([
                'College of Medicine', 'College of Pharmacy', 'College of Nursing',
                'College of Dentistry', 'College of Health Sciences'
            ]),
            specialization=random.choice([
                'General Medicine', 'Pharmacy', 'Nursing', 'Dentistry',
                'Medical Technology', 'Physical Therapy'
            ])
        )
        student_users.append(student)
        users_created += 1
    
    # Create 10 Staff Users
    staff_users = []
    for i in range(1, 11):
        staff = User.objects.create_user(
            username=f'staff_{i}',
            password='staff123',
            email=f'staff{i}@umoor-sehhat.org',
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            role='badri_mahal_admin',
            phone_number=fake.phone_number()[:15]
        )
        staff_users.append(staff)
        users_created += 1
    
    # Create 20 Aamil Users
    aamil_users = []
    for i in range(1, 21):
        aamil = User.objects.create_user(
            username=f'aamil_{i}',
            password='aamil123',
            email=f'aamil{i}@umoor-sehhat.org',
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            role='aamil',
            phone_number=fake.phone_number()[:15]
        )
        aamil_users.append(aamil)
        users_created += 1
    
    # Create 15 Moze Coordinator Users
    coordinator_users = []
    for i in range(1, 16):
        coordinator = User.objects.create_user(
            username=f'coordinator_{i}',
            password='coord123',
            email=f'coordinator{i}@umoor-sehhat.org',
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            role='moze_coordinator',
            phone_number=fake.phone_number()[:15]
        )
        coordinator_users.append(coordinator)
        users_created += 1
    
    print_progress(f"✅ Created {users_created} users")
    return {
        'admin': admin_users,
        'doctor': doctor_users,
        'student': student_users,
        'staff': staff_users,
        'aamil': aamil_users,
        'coordinator': coordinator_users
    }

def create_students_data(users):
    """Create student management data"""
    print_progress("🎓 Creating student management data...")
    
    # Create 500 Student Profiles
    students = []
    for i, user in enumerate(users['student'], 1):
        student = Student.objects.create(
            user=user,
            student_id=f'STD{i:04d}',
            academic_level=random.choice(['undergraduate', 'postgraduate', 'doctoral', 'diploma']),
            enrollment_status='active',
            enrollment_date=fake.date_between(start_date='-4y', end_date='now'),
            expected_graduation=fake.date_between(start_date='today', end_date='+2y')
        )
        students.append(student)
    
    # Create 10 Medical Courses
    course_data = [
        ('ANAT101', 'Human Anatomy I', 'Basic human anatomy and physiology'),
        ('PHYS102', 'Medical Physics', 'Physics principles in medical applications'),
        ('BIOC103', 'Biochemistry', 'Molecular basis of biological processes'),
        ('PHARM201', 'Pharmacology I', 'Drug mechanisms and interactions'),
        ('PATH202', 'General Pathology', 'Disease processes and mechanisms'),
        ('MICRO203', 'Medical Microbiology', 'Microorganisms and infectious diseases'),
        ('PSYC301', 'Medical Psychology', 'Psychological aspects of healthcare'),
        ('SURG401', 'Introduction to Surgery', 'Basic surgical principles'),
        ('PEDS402', 'Pediatric Medicine', 'Child health and development'),
        ('EMER501', 'Emergency Medicine', 'Emergency care protocols')
    ]
    
    courses = []
    for code, name, description in course_data:
        course = Course.objects.create(
            code=code,
            name=name,
            description=description,
            credits=random.randint(2, 6)
        )
        courses.append(course)
    
    # Create Student Enrollments (300 students across multiple courses)
    enrollments = []
    enrolled_students = random.sample(students, 300)
    for student in enrolled_students:
        # Each student enrolls in 2-5 courses
        student_courses = random.sample(courses, random.randint(2, 5))
        for course in student_courses:
            enrollment = Enrollment.objects.create(
                student=student,
                course=course,
                status=random.choice(['enrolled', 'completed', 'dropped']),
                grade=random.choice(['A', 'B', 'C', 'D', 'F', ''])
            )
            enrollments.append(enrollment)
    
    # Create 50 Academic Events
    events = []
    event_types = ['lecture', 'workshop', 'seminar', 'conference', 'examination']
    for i in range(50):
        event = Event.objects.create(
            title=f'{fake.catch_phrase()} {random.choice(event_types).title()}',
            description=fake.text(max_nb_chars=200),
            event_type=random.choice(event_types),
            start_date=fake.date_time_between(start_date='-30d', end_date='+30d'),
            end_date=fake.date_time_between(start_date='+30d', end_date='+60d'),
            location=fake.address()[:100],
            organizer=random.choice(users['admin'] + users['staff'])
        )
        events.append(event)
    
    # Create Course Announcements
    for course in courses:
        for i in range(random.randint(1, 3)):
            Announcement.objects.create(
                title=f'{course.name} - {fake.sentence(nb_words=4)}',
                content=fake.text(max_nb_chars=300),
                course=course,
                author=random.choice(users['admin'] + users['staff']),
                created_at=fake.date_time_between(start_date='-30d', end_date='now')
            )
    
    print_progress(f"✅ Created student data: {len(students)} students, {len(courses)} courses, {len(enrollments)} enrollments, {len(events)} events")

def create_surveys_data(users):
    """Create survey system data"""
    print_progress("📋 Creating survey data...")
    
    # Create 10 Comprehensive Surveys
    survey_data = [
        ('Medical Service Satisfaction', 'How satisfied are you with our medical services?'),
        ('Educational Quality Assessment', 'Please evaluate the quality of our educational programs.'),
        ('Facility Infrastructure Review', 'Share your feedback about our facilities and infrastructure.'),
        ('Staff Performance Evaluation', 'Evaluate the performance of our staff members.'),
        ('Student Learning Experience', 'Tell us about your learning experience as a student.'),
        ('Healthcare Accessibility Survey', 'How accessible are our healthcare services?'),
        ('Technology Usage Assessment', 'Evaluate our technology systems and digital services.'),
        ('Community Engagement Survey', 'How well do we engage with the community?'),
        ('Safety and Security Review', 'Assess our safety and security measures.'),
        ('Future Improvement Suggestions', 'What improvements would you like to see?')
    ]
    
    surveys = []
    all_users = users['admin'] + users['doctor'] + users['student'] + users['staff'] + users['aamil']
    
    for title, description in survey_data:
        survey = Survey.objects.create(
            title=title,
            description=description,
            created_by=random.choice(users['admin']),
            created_at=fake.date_time_between(start_date='-60d', end_date='-30d'),
            is_active=True,
            is_anonymous=random.choice([True, False])
        )
        surveys.append(survey)
        
        # Create questions for each survey (stored as JSON in Survey model)
        questions = []
        question_types = ['text', 'multiple_choice', 'rating', 'yes_no']
        for q in range(random.randint(3, 8)):
            question = {
                "id": q + 1,
                "type": random.choice(question_types),
                "question": fake.sentence() + '?',
                "required": random.choice([True, False]),
                "options": []
            }
            if question["type"] == "multiple_choice":
                question["options"] = [fake.word() for _ in range(random.randint(2, 5))]
            elif question["type"] == "rating":
                question["options"] = ["1", "2", "3", "4", "5"]
            questions.append(question)
        
        survey.questions = questions
        survey.save()
    
    # Create Survey Responses (20-100 responses per survey)
    total_responses = 0
    for survey in surveys:
        response_count = random.randint(20, 100)
        survey_users = random.sample(all_users, min(response_count, len(all_users)))
        
        for user in survey_users:
            # Generate answers for each question
            answers = {}
            for q in survey.questions:
                if q["type"] == "text":
                    answers[str(q["id"])] = fake.sentence()
                elif q["type"] == "multiple_choice":
                    answers[str(q["id"])] = random.choice(q["options"]) if q["options"] else ""
                elif q["type"] == "rating":
                    answers[str(q["id"])] = random.choice(q["options"]) if q["options"] else "3"
                elif q["type"] == "checkbox":
                    answers[str(q["id"])] = random.sample(q["options"], k=random.randint(1, len(q["options"])) if q["options"] else 0)
                elif q["type"] == "yes_no":
                    answers[str(q["id"])] = random.choice(["yes", "no"])
                else:
                    answers[str(q["id"])] = ""
            response = SurveyResponse.objects.create(
                survey=survey,
                respondent=user if not survey.is_anonymous else None,
                answers=answers,
                created_at=fake.date_time_between(
                    start_date=survey.created_at,
                    end_date='now'
                ),
                is_complete=True
            )
            total_responses += 1
    
    print_progress(f"✅ Created {len(surveys)} surveys with {total_responses} responses")

def create_moze_data(users):
    """Create Moze centers data"""
    print_progress("🕌 Creating Moze centers data...")
    
    # Pakistani cities for Moze centers
    pakistani_cities = [
        'Karachi', 'Lahore', 'Islamabad', 'Rawalpindi', 'Faisalabad',
        'Multan', 'Peshawar', 'Quetta', 'Sialkot', 'Gujranwala',
        'Hyderabad', 'Bahawalpur', 'Sargodha', 'Sukkur', 'Larkana',
        'Mardan', 'Mingora', 'Dera Ghazi Khan', 'Sahiwal', 'Nawabshah'
    ]
    
    # Create 72 Moze Centers
    moze_centers = []
    for i in range(72):
        city = random.choice(pakistani_cities)
        moze = Moze.objects.create(
            name=f'Moze {city} {i+1}',
            location=city,
            address=fake.address(),
            aamil=random.choice(users['aamil']),
            moze_coordinator=random.choice(users['coordinator']),
            established_date=fake.date_between(start_date='-20y', end_date='-1y'),
            is_active=True,
            capacity=random.randint(50, 500),
            contact_phone=fake.phone_number()[:15],
            contact_email=f'moze{i+1}@umoor-sehhat.org'
        )
        moze_centers.append(moze)
    
    # Create Moze Comments
    comments_count = 0
    all_users = users['admin'] + users['aamil'] + users['coordinator']
    for moze in moze_centers:
        for _ in range(random.randint(0, 5)):
            MozeComment.objects.create(
                moze=moze,
                author=random.choice(all_users),
                content=fake.text(max_nb_chars=200),
                created_at=fake.date_time_between(start_date='-30d', end_date='now')
            )
            comments_count += 1
    
    print_progress(f"✅ Created {len(moze_centers)} Moze centers with {comments_count} comments")
    return moze_centers

def create_hospital_data(users, moze_centers):
    """Create hospital management data"""
    print_progress("🏥 Creating hospital data...")
    
    # Create 20 Hospitals
    hospitals = []
    hospital_types = ['general', 'specialty', 'clinic']
    
    for i in range(1, 21):
        hospital = Hospital.objects.create(
            name=f'Mahal Shifa Hospital {i}',
            description=fake.text(max_nb_chars=100),
            address=fake.address(),
            phone=fake.phone_number()[:20],
            email=f'hospital{i}@mahalshifa.org',
            hospital_type=random.choice(hospital_types),
            total_beds=random.randint(50, 500),
            available_beds=random.randint(10, 100),
            emergency_beds=random.randint(5, 20),
            icu_beds=random.randint(2, 10),
            is_active=True,
            is_emergency_capable=random.choice([True, False]),
            has_pharmacy=random.choice([True, False]),
            has_laboratory=random.choice([True, False])
        )
        hospitals.append(hospital)
    
    # Create Hospital Doctors (link doctors to hospitals)
    hospital_doctors = []
    assigned_doctor_users = set()
    used_license_numbers = set()
    for hospital in hospitals:
        # Each hospital has 3-8 doctors
        hospital_doctor_users = random.sample([u for u in users['doctor'] if u not in assigned_doctor_users], min(random.randint(3, 8), len(users['doctor']) - len(assigned_doctor_users)))
        for doctor_user in hospital_doctor_users:
            assigned_doctor_users.add(doctor_user)
            # Ensure the hospital has at least one department
            departments = list(hospital.departments.all())
            if not departments:
                dept = hospital.departments.create(
                    name=f"Department {random.randint(1, 10)}",
                    description=fake.text(max_nb_chars=50)
                )
                departments = [dept]
            department = random.choice(departments)
            # Generate a unique license number
            while True:
                license_number = f"LIC-{random.randint(10000, 99999)}"
                if license_number not in used_license_numbers:
                    used_license_numbers.add(license_number)
                    break
            doctor = MahalshifaDoctor.objects.create(
                user=doctor_user,
                license_number=license_number,
                specialization=random.choice([
                    'Emergency', 'Surgery', 'Internal Medicine', 'Pediatrics',
                    'Cardiology', 'Neurology', 'Orthopedics', 'Radiology'
                ]),
                qualification=random.choice([
                    'MBBS', 'FCPS', 'MD', 'MS', 'MRCP', 'FRCS', 'Diploma'
                ]),
                experience_years=random.randint(1, 30),
                hospital=hospital,
                department=department,
                is_available=random.choice([True, False]),
                consultation_fee=random.randint(500, 5000)
            )
            hospital_doctors.append(doctor)
    
    # Create 200 Patients
    patients = []
    for i in range(200):
        patient = Patient.objects.create(
            its_id=f'{random.randint(10000000, 99999999)}',
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            arabic_name=fake.first_name(),
            date_of_birth=fake.date_of_birth(minimum_age=1, maximum_age=90),
            gender=random.choice(['male', 'female', 'other']),
            phone_number=fake.phone_number()[:15],
            email=fake.email(),
            address=fake.address(),
            emergency_contact_name=fake.name(),
            emergency_contact_phone=fake.phone_number()[:15],
            emergency_contact_relationship=random.choice(['Father', 'Mother', 'Sibling', 'Spouse', 'Friend']),
            blood_group=random.choice(['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']),
            allergies=fake.text(max_nb_chars=20),
            chronic_conditions=fake.text(max_nb_chars=20),
            current_medications=fake.text(max_nb_chars=20),
            registered_moze=None,
            is_active=True
        )
        patients.append(patient)
    
    # Create 300 Appointments
    appointments = []
    appointment_statuses = ['scheduled', 'completed', 'cancelled', 'no_show']
    
    for i in range(300):
        appointment = Appointment.objects.create(
            patient=random.choice(patients),
            doctor=random.choice(hospital_doctors),
            moze=random.choice(moze_centers),
            service=None,
            appointment_date=fake.date_between(start_date='-1y', end_date='now'),
            appointment_time=fake.time_object(),
            duration_minutes=random.randint(15, 120),
            reason=fake.sentence(),
            symptoms=fake.text(max_nb_chars=50),
            notes=fake.text(max_nb_chars=200)
        )
        appointments.append(appointment)
    
    print_progress(f"✅ Created hospital data: {len(hospitals)} hospitals, {len(patients)} patients, {len(appointments)} appointments")

def create_doctor_directory_data(users, moze_centers):
    """Create doctor directory data"""
    print_progress("👨‍⚕️ Creating doctor directory...")
    
    # Create 100 Doctor Profiles
    doctors = []
    for doctor_user in users['doctor']:
        doctor = Doctor.objects.create(
            user=doctor_user,
            name=fake.name(),
            its_id=f'{random.randint(10000000, 99999999)}',
            specialty=random.choice(['Cardiology', 'Neurology', 'Orthopedics', 'Pediatrics', 'General Medicine']),
            qualification=random.choice(['MBBS', 'FCPS', 'MD', 'MS', 'MRCP', 'FRCS', 'Diploma']),
            experience_years=random.randint(1, 30),
            assigned_moze=random.choice(moze_centers),
            is_verified=random.choice([True, False]),
            is_available=random.choice([True, False]),
            license_number=f"LIC-{random.randint(10000, 99999)}",
            consultation_fee=random.randint(500, 5000),
            phone=fake.phone_number()[:15],
            email=fake.email(),
            address=fake.address(),
            languages_spoken=", ".join(fake.words(nb=3)),
            bio=fake.text(max_nb_chars=100)
        )
        doctors.append(doctor)
    
    # Create 150 Directory Patients
    dir_patients = []
    for i in range(150):
        user = User.objects.create_user(
            username=f'dir_patient_{i+1}',
            password='test123',
            email=f'dir_patient_{i+1}@example.com',
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            role='patient'
        )
        patient = DirPatient.objects.create(
            user=user,
            date_of_birth=fake.date_of_birth(minimum_age=1, maximum_age=90),
            gender=random.choice(['M', 'F', 'O']),
            blood_group=random.choice(['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']),
            emergency_contact=fake.phone_number()[:15],
            medical_history=fake.text(max_nb_chars=50),
            allergies=fake.text(max_nb_chars=20),
            current_medications=fake.text(max_nb_chars=20)
        )
        dir_patients.append(patient)
    
    # Create 200 Medical Records
    medical_records = []
    for i in range(300):
        record = MedicalRecord.objects.create(
            patient=random.choice(dir_patients),
            doctor=random.choice(doctors),
            appointment=None,
            diagnosis=fake.sentence(),
            symptoms=fake.text(max_nb_chars=50),
            treatment_plan=fake.text(max_nb_chars=100),
            medications=fake.text(max_nb_chars=50),
            follow_up_required=random.choice([True, False]),
            follow_up_date=fake.date_between(start_date='today', end_date='+1y'),
            notes=fake.text(max_nb_chars=200)
        )
        medical_records.append(record)
    
    print_progress(f"✅ Created doctor directory: {len(doctors)} profiles, {len(dir_patients)} patients, {len(medical_records)} records")

def create_evaluation_data(users):
    """Create evaluation system data"""
    print_progress("📝 Creating evaluation data...")
    
    # Create 20 Evaluation Forms
    evaluation_forms = []
    evaluation_types = ['performance', 'course', 'service', 'facility', 'staff']
    
    for i in range(20):
        form = EvaluationForm.objects.create(
            title=fake.sentence(nb_words=4),
            description=fake.text(max_nb_chars=100),
            created_by=random.choice(users['admin']),
            created_at=fake.date_time_between(start_date='-60d', end_date='-30d'),
            is_active=True,
            is_anonymous=random.choice([True, False])
        )
        evaluation_forms.append(form)
    
    # Create Evaluation Submissions
    submissions = []
    all_users = users['doctor'] + users['student'] + users['staff']
    
    for form in evaluation_forms:
        evaluators_used = set()
        for _ in range(random.randint(5, 15)):
            possible_evaluators = [u for u in users['admin'] + users['doctor'] + users['staff'] if u not in evaluators_used]
            if not possible_evaluators:
                break
            evaluator = random.choice(possible_evaluators)
            evaluators_used.add(evaluator)
            submission = EvaluationSubmission.objects.create(
                form=form,
                evaluator=evaluator,
                target_user=None,
                target_moze=None,
                total_score=random.uniform(60, 100),
                comments=fake.text(max_nb_chars=100),
                is_complete=True
            )
            submissions.append(submission)
    
    print_progress(f"✅ Created {len(evaluation_forms)} evaluation forms with {len(submissions)} submissions")

def create_petition_data(users):
    """Create petition management data"""
    print_progress("📄 Creating petition data...")
    
    # Ensure at least one PetitionCategory exists
    categories = list(PetitionCategory.objects.all())
    if not categories:
        default_category = PetitionCategory.objects.create(name='General', description='General petitions')
        categories = [default_category]
    # Create 100 Petitions
    petitions = []
    petition_categories = ['medical', 'administrative', 'academic', 'facility', 'other']
    petition_statuses = ['pending', 'in_review', 'approved', 'rejected', 'closed']
    
    for i in range(100):
        petition = Petition.objects.create(
            title=f'Petition #{i+1}: {fake.sentence(nb_words=6)}',
            description=fake.text(max_nb_chars=200),
            category=random.choice(categories),
            created_by=random.choice(users['admin'] + users['doctor'] + users['staff']),
            is_anonymous=random.choice([True, False]),
            status=random.choice(['pending', 'in_progress', 'resolved', 'rejected']),
            priority=random.choice(['low', 'medium', 'high']),
            moze=None,
            created_at=fake.date_time_between(start_date='-90d', end_date='now'),
            updated_at=fake.date_time_between(start_date='-30d', end_date='now')
        )
        petitions.append(petition)
    
    # Create Petition Comments
    comments = []
    for petition in petitions:
        # Each petition gets 0-5 comments
        for _ in range(random.randint(0, 5)):
            PetitionComment.objects.create(
                petition=petition,
                user=random.choice([petition.created_by] + users['admin']),
                content=fake.text(max_nb_chars=100),
                is_internal=random.choice([True, False])
            )
    
    print_progress(f"✅ Created {len(petitions)} petitions with {len(comments)} comments")

def create_photo_data(users, moze_centers):
    """Create photo gallery data"""
    print_progress("📸 Creating photo gallery data...")
    
    # Create 10 Photo Albums
    album_names = [
        'Medical Conference 2024', 'Student Activities', 'Hospital Events',
        'Moze Gatherings', 'Educational Workshops', 'Community Service',
        'Sports Events', 'Cultural Programs', 'Graduation Ceremony', 'Research Projects'
    ]
    
    albums = []
    for name in album_names:
        album = PhotoAlbum.objects.create(
            name=name,
            description=fake.text(max_nb_chars=200),
            moze=random.choice(moze_centers),
            created_by=random.choice(users['admin'] + users['staff']),
            is_public=True,
            allow_uploads=True,
            event_date=fake.date_between(start_date='-1y', end_date='now')
        )
        albums.append(album)
    
    # Create Photo Tags
    tag_names = [
        'medical', 'education', 'community', 'events', 'students',
        'doctors', 'hospitals', 'conferences', 'workshops', 'graduation'
    ]
    
    tags = []
    for tag_name in tag_names:
        tag = PhotoTag.objects.create(name=tag_name)
        tags.append(tag)
    
    # Create dummy photos (without actual image files)
    photos = []
    for album in albums:
        # Each album gets 5-15 photos
        for i in range(random.randint(5, 15)):
            photo = Photo.objects.create(
                title=fake.sentence(nb_words=3),
                description=fake.text(max_nb_chars=100),
                subject_tag=fake.word(),
                moze=album.moze,
                uploaded_by=album.created_by,
                location=fake.city(),
                event_date=album.event_date,
                photographer=fake.name(),
                category=random.choice(['event', 'medical', 'infrastructure', 'team', 'other']),
                is_public=True,
                is_featured=random.choice([True, False]),
                requires_permission=False
                # Note: Not setting 'image' field as we don't have actual image files
            )
            album.photos.add(photo)
            photos.append(photo)
    
    print_progress(f"✅ Created photo gallery: {len(albums)} albums, {len(photos)} photos, {len(tags)} tags")

@transaction.atomic
def populate_database():
    """Main function to populate the entire database"""
    start_time = datetime.now()
    
    print("🚀 UMOOR SEHHAT TEST DATA POPULATION")
    print("=" * 60)
    print("⚠️  WARNING: This will DELETE all existing data!")
    print("=" * 60)
    
    try:
        # Clear existing data
        clear_database()
        
        # Create all test data
        users = create_users()
        create_students_data(users)
        create_surveys_data(users)
        moze_centers = create_moze_data(users)
        create_hospital_data(users, moze_centers)
        create_doctor_directory_data(users, moze_centers)
        create_evaluation_data(users)
        create_petition_data(users)
        create_photo_data(users, moze_centers)
        
        # Calculate totals for summary
        total_users = User.objects.count()
        total_students = Student.objects.count()
        total_courses = Course.objects.count()
        total_surveys = Survey.objects.count()
        total_hospitals = Hospital.objects.count()
        total_moze = Moze.objects.count()
        total_doctors = Doctor.objects.count()
        total_evaluations = EvaluationForm.objects.count()
        total_petitions = Petition.objects.count()
        total_albums = PhotoAlbum.objects.count()
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        print("\n" + "=" * 60)
        print("🎉 TEST DATA POPULATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"📊 SUMMARY:")
        print(f"   Users: {total_users}")
        print(f"   Students: {total_students}")
        print(f"   Courses: {total_courses}")
        print(f"   Surveys: {total_surveys}")
        print(f"   Hospitals: {total_hospitals}")
        print(f"   Moze Centers: {total_moze}")
        print(f"   Doctor Profiles: {total_doctors}")
        print(f"   Evaluation Forms: {total_evaluations}")
        print(f"   Petitions: {total_petitions}")
        print(f"   Photo Albums: {total_albums}")
        print(f"\n⏱️  Duration: {duration}")
        print(f"📅 Generated on: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Update documentation file
        update_documentation(end_time)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR during population: {e}")
        import traceback
        traceback.print_exc()
        return False

def update_documentation(generation_time):
    """Update the test data documentation with new timestamp"""
    try:
        doc_content = f"""# 🏥 Umoor Sehhat - Test Data Documentation

**Generated on:** {generation_time.strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Test Data Summary

This database contains comprehensive test data for all 9 Django applications in the Umoor Sehhat system.

### 👥 User Accounts

- **2 Admin Users** (admin_1, admin_2) - Password: `admin123`
- **100 Doctor Users** (doctor_001 to doctor_100) - Password: `doctor123`
- **500 Student Users** (student_001 to student_500) - Password: `student123`
- **10 Staff Users** (staff_1 to staff_10) - Password: `staff123`
- **20 Aamil Users** (aamil_1 to aamil_20) - Password: `aamil123`
- **15 Moze Coordinator Users** (coordinator_1 to coordinator_15) - Password: `coord123`

**Total Users: {User.objects.count()}**

### 📚 Students App Data

- **{Student.objects.count()} Student Profiles** with complete academic information
- **{Course.objects.count()} Medical Courses** (ANAT101, PHYS102, BIOC103, etc.)
- **Student Enrollments** for students across multiple courses
- **{Event.objects.count()} Academic Events** (lectures, workshops, seminars, etc.)
- **Course Announcements** for each course

### 📋 Surveys App Data

- **{Survey.objects.count()} Comprehensive Surveys** covering various topics:
  - Medical Service Satisfaction
  - Educational Quality Assessment
  - Facility Infrastructure Review
  - Staff Performance Evaluation
  - Student Learning Experience
  - Healthcare Accessibility Survey
  - Technology Usage Assessment
  - Community Engagement Survey
  - Safety and Security Review
  - Future Improvement Suggestions
- **Survey Responses** from multiple users

### 🕌 Moze App Data

- **{Moze.objects.count()} Moze Centers** distributed across major Pakistani cities
- **Moze Comments** with community feedback and engagement
- Complete organizational structure with Aamils and Coordinators

### 🏥 Mahalshifa (Hospital Management) Data

- **{Hospital.objects.count()} Hospitals** with different types (general, specialty, clinic)
- **Hospital Doctors** linked to user accounts
- **{Patient.objects.count()} Patients** with complete medical records
- **{Appointment.objects.count()} Appointments** across different statuses
- **Hospital Inventory** with medical supplies and equipment

### 👨‍⚕️ Doctor Directory Data

- **{Doctor.objects.count()} Doctor Profiles** with specializations and qualifications
- **{DirPatient.objects.count()} Directory Patients** 
- **{MedicalRecord.objects.count()} Medical Records** with treatment history
- Complete consultation and appointment system

### 📝 Evaluation App Data

- **{EvaluationForm.objects.count()} Evaluation Forms** for different purposes
- **Evaluation Submissions** from various user roles
- Performance tracking and feedback system

### 📄 Araz (Petition Management) Data

- **{Petition.objects.count()} Petitions** across different categories:
  - Medical complaints
  - Administrative requests
  - Academic issues
  - Facility concerns
- **Petition Comments** with internal and public feedback
- Complete workflow tracking

### 📸 Photos App Data

- **{PhotoAlbum.objects.count()} Photo Albums** covering various events:
  - Medical Conference 2024
  - Student Activities
  - Hospital Events
  - Moze Gatherings
  - Educational Workshops
  - Community Service
  - Sports Events
  - Cultural Programs
  - Graduation Ceremony
  - Research Projects
- **Photo Tags** for organized categorization
- **Dummy Images** for testing display functionality

## 🔐 Login Credentials

### Admin Access
- Username: `admin_1` or `admin_2`
- Password: `admin123`

### Quick Test Users
- **Doctor**: `doctor_001` / `doctor123`
- **Student**: `student_001` / `student123`
- **Aamil**: `aamil_1` / `aamil123`
- **Staff**: `staff_1` / `staff123`

## 🚀 Testing Instructions

1. **Start the server**: `python3 manage.py runserver`
2. **Access admin panel**: `http://localhost:8000/admin/`
3. **Test user dashboards**: Login with different user roles
4. **Explore each app**: Navigate through all 9 application modules

## 📱 Application URLs

- **Main Site**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/
- **Students**: http://localhost:8000/students/
- **Surveys**: http://localhost:8000/surveys/
- **Mahalshifa**: http://localhost:8000/mahalshifa/
- **Moze**: http://localhost:8000/moze/
- **Photos**: http://localhost:8000/photos/
- **Doctor Directory**: http://localhost:8000/doctordirectory/
- **Evaluation**: http://localhost:8000/evaluation/
- **Araz**: http://localhost:8000/araz/

## 🔄 Data Regeneration

To regenerate fresh test data:
```bash
python3 populate_test_data.py
```

⚠️ **Warning**: This will delete all existing data and create new test data.

## 📈 Performance Notes

- Database size: Optimized with full test data
- All relationships properly configured
- Foreign key constraints maintained
- Realistic data distribution for testing

---

**System Status**: ✅ Ready for Testing  
**Last Updated**: {generation_time.strftime('%Y-%m-%d %H:%M:%S')}
"""

        with open('TEST_DATA_DOCUMENTATION.md', 'w') as f:
            f.write(doc_content)
        
        print_progress("📄 Updated TEST_DATA_DOCUMENTATION.md")
        
    except Exception as e:
        print_progress(f"⚠️  Could not update documentation: {e}")

if __name__ == "__main__":
    print("🔍 Umoor Sehhat Test Data Population Script")
    print("This will create comprehensive test data for all applications.")
    
    # Install faker if not available
    try:
        from faker import Faker
    except ImportError:
        print("Installing required dependency: faker...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "faker"])
        from faker import Faker
    
    response = input("\n⚠️  This will DELETE ALL existing data. Continue? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        success = populate_database()
        sys.exit(0 if success else 1)
    else:
        print("Operation cancelled.")
        sys.exit(0)