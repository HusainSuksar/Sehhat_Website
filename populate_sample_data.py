#!/usr/bin/env python
"""
Sample Data Population Script for Umoor Sehhat
Populates all Django models with realistic sample data
"""

import os
import sys
import django
from datetime import datetime, date, timedelta
from decimal import Decimal
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.files.base import ContentFile

# Import all models
User = get_user_model()
from students.models import Student
from doctordirectory.models import Doctor
from mahalshifa.models import Hospital, Patient, Appointment, MedicalRecord, LabTest, Doctor as MahalshifaDoctor, Department
from surveys.models import Survey, SurveyResponse
from evaluation.models import EvaluationForm, EvaluationCriteria, EvaluationSubmission
from araz.models import Petition, PetitionCategory
from moze.models import Moze
from photos.models import PhotoAlbum


class SampleDataPopulator:
    """Populate Django models with comprehensive sample data"""
    
    def __init__(self):
        self.users_created = 0
        self.total_records = 0
        print("🚀 Starting Sample Data Population...")
    
    def create_users(self):
        """Create users for different roles"""
        print("\n👥 Creating Users...")
        
        # Admin users
        admin_users = [
            {'username': 'admin', 'email': 'admin@sehhat.com', 'first_name': 'System', 'last_name': 'Administrator', 'role': 'student', 'is_superuser': True, 'is_staff': True},
            {'username': 'manager', 'email': 'manager@sehhat.com', 'first_name': 'Hassan', 'last_name': 'Ahmed', 'role': 'student', 'is_staff': True},
        ]
        
        # Aamil users
        aamil_users = [
            {'username': 'aamil1', 'email': 'aamil1@sehhat.com', 'first_name': 'Ahmed', 'last_name': 'Ali', 'role': 'aamil', 'its_id': '12345678'},
            {'username': 'aamil2', 'email': 'aamil2@sehhat.com', 'first_name': 'Mohammad', 'last_name': 'Hassan', 'role': 'aamil', 'its_id': '12345679'},
            {'username': 'aamil3', 'email': 'aamil3@sehhat.com', 'first_name': 'Ibrahim', 'last_name': 'Omar', 'role': 'aamil', 'its_id': '12345680'},
        ]
        
        # Moze Coordinator users
        coordinator_users = [
            {'username': 'coord1', 'email': 'coord1@sehhat.com', 'first_name': 'Fatima', 'last_name': 'Khan', 'role': 'moze_coordinator', 'its_id': '12345681'},
            {'username': 'coord2', 'email': 'coord2@sehhat.com', 'first_name': 'Aisha', 'last_name': 'Ahmed', 'role': 'moze_coordinator', 'its_id': '12345682'},
            {'username': 'coord3', 'email': 'coord3@sehhat.com', 'first_name': 'Zainab', 'last_name': 'Ali', 'role': 'moze_coordinator', 'its_id': '12345683'},
        ]
        
        # Doctor users
        doctor_users = [
            {'username': 'dr_ahmed', 'email': 'dr.ahmed@sehhat.com', 'first_name': 'Dr. Ahmed', 'last_name': 'Hassan', 'role': 'doctor', 'its_id': '12345684'},
            {'username': 'dr_fatima', 'email': 'dr.fatima@sehhat.com', 'first_name': 'Dr. Fatima', 'last_name': 'Ali', 'role': 'doctor', 'its_id': '12345685'},
            {'username': 'dr_omar', 'email': 'dr.omar@sehhat.com', 'first_name': 'Dr. Omar', 'last_name': 'Khan', 'role': 'doctor', 'its_id': '12345686'},
            {'username': 'dr_aisha', 'email': 'dr.aisha@sehhat.com', 'first_name': 'Dr. Aisha', 'last_name': 'Ahmed', 'role': 'doctor', 'its_id': '12345687'},
            {'username': 'dr_hassan', 'email': 'dr.hassan@sehhat.com', 'first_name': 'Dr. Hassan', 'last_name': 'Omar', 'role': 'doctor', 'its_id': '12345688'},
        ]
        
        # Student users
        student_users = [
            {'username': 'student1', 'email': 'student1@sehhat.com', 'first_name': 'Sara', 'last_name': 'Ali', 'role': 'student', 'its_id': '12345689', 'college': 'Medical College', 'specialization': 'Medicine'},
            {'username': 'student2', 'email': 'student2@sehhat.com', 'first_name': 'Yusuf', 'last_name': 'Khan', 'role': 'student', 'its_id': '12345690', 'college': 'Engineering College', 'specialization': 'Computer Science'},
            {'username': 'student3', 'email': 'student3@sehhat.com', 'first_name': 'Mariam', 'last_name': 'Hassan', 'role': 'student', 'its_id': '12345691', 'college': 'Medical College', 'specialization': 'Nursing'},
            {'username': 'student4', 'email': 'student4@sehhat.com', 'first_name': 'Ali', 'last_name': 'Ahmed', 'role': 'student', 'its_id': '12345692', 'college': 'Business School', 'specialization': 'Management'},
            {'username': 'student5', 'email': 'student5@sehhat.com', 'first_name': 'Khadija', 'last_name': 'Omar', 'role': 'student', 'its_id': '12345693', 'college': 'Medical College', 'specialization': 'Pharmacy'},
        ]
        
        # Badri Mahal Admin users
        mahal_users = [
            {'username': 'mahal1', 'email': 'mahal1@sehhat.com', 'first_name': 'Ibrahim', 'last_name': 'Hassan', 'role': 'badri_mahal_admin', 'its_id': '12345694'},
            {'username': 'mahal2', 'email': 'mahal2@sehhat.com', 'first_name': 'Zara', 'last_name': 'Ali', 'role': 'badri_mahal_admin', 'its_id': '12345695'},
        ]
        
        all_users = admin_users + aamil_users + coordinator_users + doctor_users + student_users + mahal_users
        
        for user_data in all_users:
            if not User.objects.filter(username=user_data['username']).exists():
                password = 'test123'  # Simple password for development
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=password,
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    role=user_data.get('role', 'student'),
                    its_id=user_data.get('its_id'),
                    phone_number=f"+1234567{random.randint(1000, 9999)}",
                    age=random.randint(20, 65),
                    college=user_data.get('college'),
                    specialization=user_data.get('specialization'),
                    is_superuser=user_data.get('is_superuser', False),
                    is_staff=user_data.get('is_staff', False),
                )
                self.users_created += 1
                print(f"  ✅ Created {user_data.get('role', 'admin')} user: {user_data['username']}")
        
        print(f"  📊 Total users created: {self.users_created}")
    
    def create_students(self):
        """Create student records"""
        print("\n🎓 Creating Students...")
        
        student_users = User.objects.filter(role='student')
        count = 0
        
        for user in student_users:
            if not Student.objects.filter(user=user).exists():
                student = Student.objects.create(
                    user=user,
                    student_id=f"STU{user.id:04d}",
                    academic_level=random.choice(['undergraduate', 'postgraduate', 'diploma']),
                    enrollment_status=random.choice(['enrolled', 'graduated']),
                    enrollment_date=date.today() - timedelta(days=random.randint(30, 365)),
                    expected_graduation=date.today() + timedelta(days=random.randint(365, 1460)),
                )
                count += 1
                print(f"  ✅ Created student record for: {user.get_full_name()}")
        
        print(f"  📊 Total students created: {count}")
        self.total_records += count
    
    def create_doctors(self):
        """Create doctor records"""
        print("\n👨‍⚕️ Creating Doctors...")
        
        doctor_users = User.objects.filter(role='doctor')
        specialties = ['Cardiology', 'Neurology', 'Pediatrics', 'Orthopedics', 'General Medicine', 'Surgery', 'Dermatology']
        qualifications = ['MBBS, MD', 'MBBS, MS', 'MBBS, FCPS', 'MBBS, MRCP', 'MBBS, FRCS']
        
        count = 0
        for user in doctor_users:
            if not Doctor.objects.filter(user=user).exists():
                doctor = Doctor.objects.create(
                    user=user,
                    name=user.get_full_name(),
                    its_id=user.its_id or f"DR{user.id:04d}",
                    specialty=random.choice(specialties),
                    qualification=random.choice(qualifications),
                    experience_years=random.randint(2, 25),
                    consultation_fee=Decimal(str(random.randint(50, 300))),
                    phone=user.phone_number,
                    email=user.email,
                    license_number=f"LIC{random.randint(10000, 99999)}",
                    address=f"{random.randint(100, 999)} Medical Street, Healthcare District",
                    languages_spoken="English, Arabic",
                    bio=f"Experienced {random.choice(specialties).lower()} specialist with {random.randint(2, 25)} years of practice.",
                    is_verified=True,
                    is_available=random.choice([True, True, False]),  # 66% available
                )
                count += 1
                print(f"  ✅ Created doctor: {doctor.name} - {doctor.specialty}")
        
        print(f"  📊 Total doctors created: {count}")
        self.total_records += count
    
    def create_hospitals(self):
        """Create hospital records"""
        print("\n🏥 Creating Hospitals...")
        
        hospitals_data = [
            {
                'name': 'Badri Mahal Hospital',
                'description': 'Main community hospital providing comprehensive healthcare services',
                'address': '123 Main Street, Community Center',
                'phone': '+1234567890',
                'email': 'info@badrimahal.com',
                'hospital_type': 'general',
                'total_beds': 100,
                'available_beds': random.randint(10, 30),
            },
            {
                'name': 'Sehhat Medical Center',
                'description': 'Specialized medical center focusing on preventive care',
                'address': '456 Health Avenue, Medical District',
                'phone': '+1234567891',
                'email': 'contact@sehhatcenter.com',
                'hospital_type': 'specialized',
                'total_beds': 50,
                'available_beds': random.randint(5, 15),
            },
            {
                'name': 'Community Health Clinic',
                'description': 'Primary healthcare clinic serving the local community',
                'address': '789 Wellness Road, Health Zone',
                'phone': '+1234567892',
                'email': 'clinic@community.com',
                'hospital_type': 'clinic',
                'total_beds': 20,
                'available_beds': random.randint(2, 8),
            },
            {
                'name': 'Emergency Care Hospital',
                'description': '24/7 emergency care and trauma center',
                'address': '321 Emergency Lane, Critical Care District',
                'phone': '+1234567893',
                'email': 'emergency@carehosp.com',
                'hospital_type': 'emergency',
                'total_beds': 75,
                'available_beds': random.randint(8, 20),
            },
        ]
        
        count = 0
        for hospital_data in hospitals_data:
            if not Hospital.objects.filter(name=hospital_data['name']).exists():
                hospital = Hospital.objects.create(**hospital_data)
                count += 1
                print(f"  ✅ Created hospital: {hospital.name}")
        
        print(f"  📊 Total hospitals created: {count}")
        self.total_records += count
    
    def create_departments(self):
        """Create hospital departments"""
        print("\n🏥 Creating Hospital Departments...")
        
        hospitals = list(Hospital.objects.all())
        if not hospitals:
            print("  ⚠️ No hospitals found, skipping departments creation")
            return
        
        departments_data = [
            'Emergency Medicine',
            'Internal Medicine', 
            'Cardiology',
            'Neurology',
            'Pediatrics',
            'Orthopedics',
            'General Surgery',
            'Dermatology',
            'Radiology',
            'Laboratory',
        ]
        
        count = 0
        for hospital in hospitals:
            for dept_name in departments_data:
                if not Department.objects.filter(name=dept_name, hospital=hospital).exists():
                    department = Department.objects.create(
                        name=dept_name,
                        hospital=hospital,
                        description=f"{dept_name} department providing specialized medical services",
                        is_active=True,
                    )
                    count += 1
                    print(f"  ✅ Created department: {dept_name} at {hospital.name}")
        
        print(f"  📊 Total departments created: {count}")
        self.total_records += count
    
    def create_mahalshifa_doctors(self):
        """Create mahalshifa doctor records"""
        print("\n👨‍⚕️ Creating Mahalshifa Doctors...")
        
        doctor_users = User.objects.filter(role='doctor')
        hospitals = list(Hospital.objects.all())
        departments = list(Department.objects.all())
        
        if not hospitals or not departments:
            print("  ⚠️ No hospitals or departments found, skipping mahalshifa doctors creation")
            return
        
        specializations = ['Cardiology', 'Neurology', 'Pediatrics', 'Orthopedics', 'General Medicine', 'Surgery', 'Dermatology']
        qualifications = ['MBBS, MD', 'MBBS, MS', 'MBBS, FCPS', 'MBBS, MRCP', 'MBBS, FRCS']
        
        count = 0
        for user in doctor_users:
            if not MahalshifaDoctor.objects.filter(user=user).exists():
                doctor = MahalshifaDoctor.objects.create(
                    user=user,
                    license_number=f"LIC{random.randint(10000, 99999)}",
                    specialization=random.choice(specializations),
                    qualification=random.choice(qualifications),
                    experience_years=random.randint(2, 25),
                    hospital=random.choice(hospitals),
                    department=random.choice(departments),
                    consultation_fee=Decimal(str(random.randint(50, 300))),
                    is_available=random.choice([True, True, False]),  # 66% available
                    is_emergency_doctor=random.choice([True, False]),
                )
                count += 1
                print(f"  ✅ Created mahalshifa doctor: {user.get_full_name()} - {doctor.specialization}")
        
        print(f"  📊 Total mahalshifa doctors created: {count}")
        self.total_records += count
    
    def create_patients(self):
        """Create patient records"""
        print("\n🏥 Creating Patients...")
        
        # Create some patients from existing users and some standalone
        users = list(User.objects.all())
        hospitals = list(Hospital.objects.all())
        
        if not hospitals:
            print("  ⚠️ No hospitals found, skipping patients creation")
            return
        
        count = 0
        # Create patients from existing users
        for i, user in enumerate(users[:10]):  # First 10 users as patients
            phone = user.phone_number or f"+1234567{random.randint(1000, 9999)}"
            if not Patient.objects.filter(user_account=user).exists():
                patient = Patient.objects.create(
                    its_id=user.its_id or f"PAT{user.id:04d}",
                    first_name=user.first_name or "Unknown",
                    last_name=user.last_name or "User",
                    phone_number=phone,
                    email=user.email,
                    date_of_birth=date.today() - timedelta(days=random.randint(6570, 25550)),  # 18-70 years
                    gender=random.choice(['M', 'F']),
                    address=f"{random.randint(100, 999)} Patient Street, City",
                    emergency_contact_name=f"Emergency Contact {i+1}",
                    emergency_contact_phone=f"+1234567{random.randint(1000, 9999)}",
                    emergency_contact_relationship=random.choice(['Parent', 'Spouse', 'Sibling', 'Friend']),
                    blood_group=random.choice(['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']),
                    registration_date=date.today() - timedelta(days=random.randint(1, 365)),
                    is_active=True,
                    user_account=user,
                )
                count += 1
                print(f"  ✅ Created patient: {patient.first_name} {patient.last_name}")
        
        # Create additional standalone patients
        patient_data = [
            ('Omar', 'Abdullah', 'M'), ('Fatima', 'Hassan', 'F'), ('Ahmed', 'Khan', 'M'),
            ('Aisha', 'Omar', 'F'), ('Hassan', 'Ali', 'M'), ('Zainab', 'Ahmed', 'F'),
            ('Ibrahim', 'Hassan', 'M'), ('Mariam', 'Khan', 'F'), ('Ali', 'Omar', 'M'),
            ('Khadija', 'Ali', 'F'), ('Yusuf', 'Ahmed', 'M'), ('Sara', 'Hassan', 'F'),
        ]
        
        for first_name, last_name, gender in patient_data:
            phone = f"+1234567{random.randint(1000, 9999)}"
            if not Patient.objects.filter(phone_number=phone).exists():
                patient = Patient.objects.create(
                    its_id=f"PAT{random.randint(10000, 99999)}",
                    first_name=first_name,
                    last_name=last_name,
                    phone_number=phone,
                    email=f"{first_name.lower()}.{last_name.lower()}@email.com",
                    date_of_birth=date.today() - timedelta(days=random.randint(6570, 25550)),
                    gender=gender,
                    address=f"{random.randint(100, 999)} Patient Street, City",
                    emergency_contact_name=f"Emergency Contact",
                    emergency_contact_phone=f"+1234567{random.randint(1000, 9999)}",
                    emergency_contact_relationship=random.choice(['Parent', 'Spouse', 'Sibling', 'Friend']),
                    blood_group=random.choice(['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']),
                    registration_date=date.today() - timedelta(days=random.randint(1, 365)),
                    is_active=True,
                )
                count += 1
                print(f"  ✅ Created patient: {patient.first_name} {patient.last_name}")
        
        print(f"  📊 Total patients created: {count}")
        self.total_records += count
    
    def create_appointments(self):
        """Create appointment records"""
        print("\n📅 Creating Appointments...")
        
        doctors = list(MahalshifaDoctor.objects.all())
        patients = list(Patient.objects.all())
        moze_centers = list(Moze.objects.all())
        
        if not doctors or not patients or not moze_centers:
            print("  ⚠️ No doctors, patients, or moze centers found, skipping appointments creation")
            return
        
        count = 0
        statuses = ['scheduled', 'completed', 'cancelled', 'no_show']
        appointment_types = ['consultation', 'follow_up', 'emergency', 'check_up']
        
        for i in range(min(20, len(patients))):  # Create up to 20 appointments
            appointment_date = timezone.now() + timedelta(days=random.randint(-30, 60))
            
            appointment = Appointment.objects.create(
                patient=random.choice(patients),
                doctor=random.choice(doctors),
                moze=random.choice(moze_centers),
                appointment_date=appointment_date.date(),
                appointment_time=appointment_date.time(),
                appointment_type=random.choice(appointment_types),
                status=random.choice(statuses),
                reason=f"Medical consultation for {random.choice(appointment_types)}",
                notes=f"Sample appointment notes for {random.choice(appointment_types)}",
                duration_minutes=random.choice([30, 45, 60]),
                booking_method='online',
            )
            count += 1
            print(f"  ✅ Created appointment: {appointment.patient.first_name} {appointment.patient.last_name} with {appointment.doctor.user.get_full_name()}")
        
        print(f"  📊 Total appointments created: {count}")
        self.total_records += count
    
    def create_surveys(self):
        """Create survey records"""
        print("\n📊 Creating Surveys...")
        
        users = list(User.objects.filter(is_staff=True))
        if not users:
            users = list(User.objects.all()[:3])
        
        surveys_data = [
            {
                'title': 'Healthcare Service Quality Assessment',
                'description': 'Evaluate the quality of healthcare services provided in our facilities',
                'target_role': 'all',
                'is_anonymous': True,
                'questions': [
                    {'question': 'How would you rate the overall quality of healthcare services?', 'type': 'rating'},
                    {'question': 'How satisfied are you with the staff professionalism?', 'type': 'rating'},
                    {'question': 'Any additional comments?', 'type': 'text'}
                ],
            },
            {
                'title': 'Community Health Needs Survey',
                'description': 'Identify the primary health needs and concerns of our community',
                'target_role': 'all',
                'is_anonymous': False,
                'questions': [
                    {'question': 'What are your primary health concerns?', 'type': 'text'},
                    {'question': 'How often do you visit healthcare facilities?', 'type': 'choice'},
                ],
            },
            {
                'title': 'Medical Staff Performance Evaluation',
                'description': 'Assess the performance and professionalism of medical staff',
                'target_role': 'doctor',
                'is_anonymous': True,
                'questions': [
                    {'question': 'Rate the doctor\'s communication skills', 'type': 'rating'},
                    {'question': 'Rate the doctor\'s medical knowledge', 'type': 'rating'},
                ],
            },
            {
                'title': 'Patient Satisfaction Survey',
                'description': 'Measure patient satisfaction with medical care and facilities',
                'target_role': 'all',
                'is_anonymous': False,
                'questions': [
                    {'question': 'How satisfied are you with your treatment?', 'type': 'rating'},
                    {'question': 'Would you recommend our services?', 'type': 'choice'},
                ],
            },
            {
                'title': 'Health Education Program Feedback',
                'description': 'Gather feedback on health education and awareness programs',
                'target_role': 'student',
                'is_anonymous': True,
                'questions': [
                    {'question': 'How useful was the health education program?', 'type': 'rating'},
                    {'question': 'What topics would you like to see covered?', 'type': 'text'},
                ],
            },
        ]
        
        count = 0
        for survey_data in surveys_data:
            if not Survey.objects.filter(title=survey_data['title']).exists():
                survey = Survey.objects.create(
                    title=survey_data['title'],
                    description=survey_data['description'],
                    target_role=survey_data['target_role'],
                    questions=survey_data['questions'],
                    created_by=random.choice(users),
                    start_date=timezone.now() - timedelta(days=random.randint(1, 30)),
                    end_date=timezone.now() + timedelta(days=random.randint(30, 90)),
                    is_anonymous=survey_data['is_anonymous'],
                    allow_multiple_responses=random.choice([True, False]),
                    show_results=random.choice([True, False]),
                    is_active=True,
                )
                count += 1
                print(f"  ✅ Created survey: {survey.title}")
        
        print(f"  📊 Total surveys created: {count}")
        self.total_records += count
    
    def create_evaluation_forms(self):
        """Create evaluation form records"""
        print("\n📋 Creating Evaluation Forms...")
        
        users = list(User.objects.filter(is_staff=True))
        if not users:
            users = list(User.objects.all()[:3])
        
        evaluation_forms_data = [
            {
                'title': 'Doctor Performance Evaluation',
                'description': 'Comprehensive evaluation of doctor performance and patient care',
                'target_role': 'doctor',
            },
            {
                'title': 'Student Academic Assessment',
                'description': 'Evaluate student academic progress and practical skills',
                'target_role': 'student',
            },
            {
                'title': 'Aamil Community Leadership Evaluation',
                'description': 'Assess leadership effectiveness and community engagement',
                'target_role': 'aamil',
            },
            {
                'title': 'Coordinator Management Assessment',
                'description': 'Evaluate coordination skills and project management abilities',
                'target_role': 'moze_coordinator',
            },
            {
                'title': 'Hospital Administration Review',
                'description': 'Comprehensive review of hospital administrative performance',
                'target_role': 'badri_mahal_admin',
            },
        ]
        
        count = 0
        for form_data in evaluation_forms_data:
            if not EvaluationForm.objects.filter(title=form_data['title']).exists():
                evaluation_form = EvaluationForm.objects.create(
                    title=form_data['title'],
                    description=form_data['description'],
                    target_role=form_data['target_role'],
                    created_by=random.choice(users),
                    is_active=True,
                )
                count += 1
                print(f"  ✅ Created evaluation form: {evaluation_form.title}")
        
        print(f"  📊 Total evaluation forms created: {count}")
        self.total_records += count
    
    def create_petition_categories(self):
        """Create petition categories"""
        print("\n📂 Creating Petition Categories...")
        
        categories_data = [
            {'name': 'Medical Equipment', 'description': 'Requests related to medical equipment and supplies'},
            {'name': 'Healthcare Services', 'description': 'Requests for new or improved healthcare services'},
            {'name': 'Facility Improvement', 'description': 'Requests for facility upgrades and improvements'},
            {'name': 'Staff Training', 'description': 'Requests related to staff training and development'},
            {'name': 'Community Health', 'description': 'Requests related to community health initiatives'},
            {'name': 'Emergency Services', 'description': 'Requests related to emergency and urgent care'},
            {'name': 'Research & Development', 'description': 'Requests for medical research and development'},
            {'name': 'General', 'description': 'General requests and suggestions'},
        ]
        
        count = 0
        for category_data in categories_data:
            if not PetitionCategory.objects.filter(name=category_data['name']).exists():
                category = PetitionCategory.objects.create(
                    name=category_data['name'],
                    description=category_data['description'],
                    is_active=True,
                )
                count += 1
                print(f"  ✅ Created petition category: {category.name}")
        
        print(f"  📊 Total petition categories created: {count}")
        self.total_records += count
    
    def create_petitions(self):
        """Create petition records (Araz system)"""
        print("\n📝 Creating Petitions...")
        
        users = list(User.objects.all())
        petition_titles = [
            'Request for Medical Equipment Upgrade',
            'Community Health Program Proposal',
            'Hospital Facility Expansion Request',
            'Medical Staff Training Program',
            'Patient Care Quality Improvement',
            'Healthcare Accessibility Initiative',
            'Medical Research Collaboration',
            'Health Education Workshop Series',
            'Emergency Response System Enhancement',
            'Preventive Care Program Development',
        ]
        
        statuses = ['pending', 'approved', 'rejected', 'under_review']
        priorities = ['low', 'medium', 'high', 'urgent']
        
        moze_centers = list(Moze.objects.all())
        categories = list(PetitionCategory.objects.all())
        
        count = 0
        for title in petition_titles:
            if not Petition.objects.filter(title=title).exists():
                petition = Petition.objects.create(
                    title=title,
                    description=f"Detailed description for {title.lower()}. This petition outlines the requirements and benefits of implementing this initiative.",
                    created_by=random.choice(users),
                    category=random.choice(categories) if categories else None,
                    status=random.choice(statuses),
                    priority=random.choice(priorities),
                    moze=random.choice(moze_centers) if moze_centers else None,
                    is_anonymous=random.choice([True, False]),
                )
                count += 1
                print(f"  ✅ Created petition: {petition.title}")
        
        print(f"  📊 Total petitions created: {count}")
        self.total_records += count
    
    def create_moze_centers(self):
        """Create Moze center records"""
        print("\n🕌 Creating Moze Centers...")
        
        moze_centers_data = [
            {
                'name': 'Central Community Moze',
                'location': 'Central District',
                'address': '100 Central Avenue, Community District',
                'contact_phone': '+1234567800',
                'contact_email': 'central@moze.com',
            },
            {
                'name': 'North District Moze',
                'location': 'North District',
                'address': '200 North Street, Residential Zone',
                'contact_phone': '+1234567801',
                'contact_email': 'north@moze.com',
            },
            {
                'name': 'South Community Moze',
                'location': 'South District',
                'address': '300 South Boulevard, Commercial Area',
                'contact_phone': '+1234567802',
                'contact_email': 'south@moze.com',
            },
            {
                'name': 'East Side Moze',
                'location': 'East District',
                'address': '400 East Road, Suburban Area',
                'contact_phone': '+1234567803',
                'contact_email': 'east@moze.com',
            },
            {
                'name': 'West End Moze',
                'location': 'West District',
                'address': '500 West Avenue, Industrial Zone',
                'contact_phone': '+1234567804',
                'contact_email': 'west@moze.com',
            },
        ]
        
        aamil_users = list(User.objects.filter(role='aamil'))
        coordinator_users = list(User.objects.filter(role='moze_coordinator'))
        
        count = 0
        for i, moze_data in enumerate(moze_centers_data):
            if not Moze.objects.filter(name=moze_data['name']).exists():
                moze = Moze.objects.create(
                    name=moze_data['name'],
                    location=moze_data['location'],
                    address=moze_data['address'],
                    contact_phone=moze_data['contact_phone'],
                    contact_email=moze_data['contact_email'],
                    established_date=date.today() - timedelta(days=random.randint(365, 3650)),
                    capacity=random.randint(100, 500),
                    is_active=True,
                    aamil=aamil_users[i % len(aamil_users)] if aamil_users else None,
                    moze_coordinator=coordinator_users[i % len(coordinator_users)] if coordinator_users else None,
                )
                
                count += 1
                print(f"  ✅ Created Moze center: {moze.name}")
        
        print(f"  📊 Total Moze centers created: {count}")
        self.total_records += count
    
    def create_photo_albums(self):
        """Create photo album records"""
        print("\n📸 Creating Photo Albums...")
        
        users = list(User.objects.all())
        
        albums_data = [
            {
                'name': 'Healthcare Facilities',
                'description': 'Photos of our healthcare facilities and equipment',
                'is_public': True,
            },
            {
                'name': 'Community Events',
                'description': 'Images from community health events and programs',
                'is_public': True,
            },
            {
                'name': 'Medical Staff',
                'description': 'Professional photos of our medical team',
                'is_public': False,
            },
            {
                'name': 'Health Education Programs',
                'description': 'Documentation of health education and awareness programs',
                'is_public': True,
            },
            {
                'name': 'Patient Success Stories',
                'description': 'Inspiring stories and images of patient recovery',
                'is_public': False,
            },
        ]
        
        moze_centers = list(Moze.objects.all())
        
        count = 0
        for album_data in albums_data:
            if not PhotoAlbum.objects.filter(name=album_data['name']).exists():
                album = PhotoAlbum.objects.create(
                    name=album_data['name'],
                    description=album_data['description'],
                    created_by=random.choice(users),
                    moze=random.choice(moze_centers) if moze_centers else None,
                    is_public=album_data['is_public'],
                    allow_uploads=random.choice([True, False]),
                    event_date=date.today() - timedelta(days=random.randint(1, 365)),
                )
                count += 1
                print(f"  ✅ Created photo album: {album.name}")
        
        print(f"  📊 Total photo albums created: {count}")
        self.total_records += count
    
    def create_summary(self):
        """Display creation summary"""
        print("\n" + "="*60)
        print("📊 SAMPLE DATA POPULATION SUMMARY")
        print("="*60)
        
        # Count all records
        stats = {
            'Users': User.objects.count(),
            'Students': Student.objects.count(),
            'Doctors': Doctor.objects.count(),
            'Hospitals': Hospital.objects.count(),
            'Patients': Patient.objects.count(),
            'Appointments': Appointment.objects.count(),
            'Surveys': Survey.objects.count(),
            'Evaluation Forms': EvaluationForm.objects.count(),
            'Petitions': Petition.objects.count(),
            'Moze Centers': Moze.objects.count(),
            'Photo Albums': PhotoAlbum.objects.count(),
        }
        
        total_records = sum(stats.values())
        
        for model_name, count in stats.items():
            print(f"  📋 {model_name:<20}: {count:>3}")
        
        print("-" * 60)
        print(f"  🎯 TOTAL RECORDS CREATED: {total_records}")
        print("="*60)
        
        # Role distribution
        print("\n👥 USER ROLE DISTRIBUTION:")
        for role_code, role_name in User.ROLE_CHOICES:
            count = User.objects.filter(role=role_code).count()
            print(f"  {role_name:<20}: {count:>3}")
        
        print("\n✅ Sample data population completed successfully!")
        print("🔐 All user passwords are set to: test123")
        print("🌐 You can now test the application with realistic data!")


def main():
    """Main execution function"""
    populator = SampleDataPopulator()
    
    try:
        # Create data in logical order (dependencies first)
        populator.create_users()
        populator.create_students()
        populator.create_doctors()
        populator.create_hospitals()
        populator.create_departments()
        populator.create_mahalshifa_doctors()
        populator.create_moze_centers()  # Create moze centers before appointments
        populator.create_patients()
        populator.create_appointments()
        populator.create_surveys()
        populator.create_evaluation_forms()
        populator.create_petition_categories()
        populator.create_petitions()
        populator.create_photo_albums()
        
        # Show summary
        populator.create_summary()
        
    except Exception as e:
        print(f"\n❌ Error during data population: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)