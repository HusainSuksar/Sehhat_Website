#!/usr/bin/env python3
"""
Fixed Offline Test Data Generator for Umoor Sehhat
This script generates comprehensive test data locally without needing external APIs
Covers all 9 Django apps with 500+ records - FIXED VERSION
"""

import os
import django
import random
from datetime import datetime, date, timedelta
from django.utils import timezone
from django.db import transaction

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings_pythonanywhere')
django.setup()

from accounts.models import User
from students.models import Student, Course
from moze.models import Moze
from mahalshifa.models import Hospital, Patient, MedicalRecord, Appointment
from doctordirectory.models import Doctor
from surveys.models import Survey
from araz.models import Petition, PetitionCategory
from photos.models import PhotoAlbum
from evaluation.models import EvaluationForm

# =============================================================================
# FIXED DATA POOLS AND GENERATORS
# =============================================================================

def print_status(message):
    print(f"✅ {message}")

def print_info(message):
    print(f"ℹ️  {message}")

def print_error(message):
    print(f"❌ {message}")

def generate_its_id():
    return str(random.randint(10000000, 99999999))

def generate_phone():
    return f"+92-300-{random.randint(1000000, 9999999)}"

def safe_random_date(start_date, end_date):
    """Safely generate random date ensuring end_date is after start_date"""
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Ensure end_date is after start_date
    if end_date <= start_date:
        end_date = start_date + timedelta(days=365)  # Add a year
    
    days_between = (end_date - start_date).days
    if days_between <= 0:
        days_between = 1
    
    random_days = random.randint(0, days_between)
    return start_date + timedelta(days=random_days)

def random_choice(arr):
    return random.choice(arr)

# Name pools
MALE_NAMES = ['Ahmed', 'Ali', 'Hassan', 'Hussein', 'Mohammad', 'Omar', 'Yusuf', 'Ibrahim', 'Ismail', 'Mustafa']
FEMALE_NAMES = ['Fatima', 'Aisha', 'Khadija', 'Maryam', 'Zainab', 'Hafsa', 'Ruqayyah', 'Umm Kulthum', 'Sakina', 'Zahra']
LAST_NAMES = ['Khan', 'Ali', 'Ahmed', 'Shah', 'Malik', 'Sheikh', 'Qureshi', 'Siddiqui', 'Ansari', 'Hashmi']
CITIES = ['Karachi', 'Lahore', 'Islamabad', 'Rawalpindi', 'Faisalabad', 'Multan', 'Peshawar', 'Quetta', 'Sialkot', 'Gujranwala']

# Medical data
SPECIALTIES = [
    'General Medicine', 'Cardiology', 'Pediatrics', 'Orthopedics', 'Dermatology',
    'Neurology', 'Gastroenterology', 'Oncology', 'Psychiatry', 'Ophthalmology'
]
QUALIFICATIONS = ['MBBS', 'MBBS, MD', 'MBBS, FCPS', 'MBBS, FRCS', 'MBBS, PhD']
BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
DIAGNOSES = [
    'Hypertension', 'Diabetes Type 2', 'Common Cold', 'Migraine', 'Gastritis',
    'Asthma', 'Arthritis', 'Anxiety Disorder', 'Back Pain', 'Allergic Rhinitis'
]

# Academic data
ACADEMIC_LEVELS = ['undergraduate', 'postgraduate', 'doctoral', 'diploma']
ENROLLMENT_STATUSES = ['active', 'suspended', 'graduated', 'withdrawn']

# Petition data
PETITION_CATEGORIES = ['Academic Issues', 'Administrative Issues', 'Infrastructure', 'Health Services', 'General Complaints']
PETITION_STATUSES = ['pending', 'under_review', 'approved', 'rejected', 'closed']
PRIORITIES = ['low', 'medium', 'high', 'urgent']

# =============================================================================
# FIXED DATA GENERATION FUNCTIONS
# =============================================================================

@transaction.atomic
def generate_users():
    """Generate 500 users with proper role distribution"""
    print_info("Generating 500 users...")
    
    # Keep existing superusers
    User.objects.filter(is_superuser=False).delete()
    
    # Role distribution
    roles = [
        # Admins (10)
        *(['badri_mahal_admin'] * 10),
        # Aamils (100) - one per Moze
        *(['aamil'] * 100),
        # Moze Coordinators (100) - one per Moze  
        *(['moze_coordinator'] * 100),
        # Doctors (100)
        *(['doctor'] * 100),
        # Students (100)
        *(['student'] * 100),
        # Regular users and others (90)
        *(['user'] * 90)
    ]
    
    users_created = 0
    for i, role in enumerate(roles):
        try:
            is_admin = role == 'badri_mahal_admin'
            gender = random.choice(['male', 'female'])
            first_name = random_choice(MALE_NAMES if gender == 'male' else FEMALE_NAMES)
            last_name = random_choice(LAST_NAMES)
            
            user = User.objects.create_user(
                username=f"{role}_{str(i + 1).zfill(3)}",
                email=f"{first_name.lower()}.{last_name.lower()}@test.com",
                password='test123456',
                first_name=first_name,
                last_name=last_name,
                role=role,
                its_id=generate_its_id(),
                phone_number=generate_phone(),
                is_active=True,
                is_staff=is_admin,
            )
            users_created += 1
            
        except Exception as e:
            print_error(f"Error creating user {role}_{i+1}: {e}")
    
    print_status(f"Created {users_created} users")

@transaction.atomic
def generate_moze():
    """Generate 100 Moze centers"""
    print_info("Generating 100 Moze centers...")
    
    Moze.objects.all().delete()
    
    moze_names = [
        'Karachi Central', 'Lahore North', 'Islamabad Main', 'Rawalpindi East', 'Faisalabad West',
        'Multan South', 'Peshawar Central', 'Quetta Main', 'Sialkot North', 'Gujranwala East'
    ]
    
    aamils = list(User.objects.filter(role='aamil'))
    coordinators = list(User.objects.filter(role='moze_coordinator'))
    
    moze_created = 0
    for i in range(100):
        try:
            base_name = random_choice(moze_names)
            aamil = aamils[i] if i < len(aamils) else None
            coordinator = coordinators[i] if i < len(coordinators) else None
            
            if not aamil:
                continue
                
            moze = Moze.objects.create(
                name=f"{base_name} Moze {i + 1}",
                location=f"{random_choice(CITIES)}, Pakistan",
                address=f"Street {i + 1}, Block {chr(65 + (i % 26))}, {random_choice(CITIES)}",
                aamil=aamil,
                moze_coordinator=coordinator,
                contact_phone=generate_phone(),
                contact_email=f"moze{i + 1}@umoor.com",
                established_date=safe_random_date(date(2010, 1, 1), date(2020, 1, 1)),
                is_active=True,
                capacity=random.randint(50, 250),
            )
            moze_created += 1
            
        except Exception as e:
            print_error(f"Error creating Moze {i + 1}: {e}")
    
    print_status(f"Created {moze_created} Moze centers")

@transaction.atomic
def generate_courses():
    """Generate academic courses"""
    print_info("Generating courses...")
    
    Course.objects.all().delete()
    
    courses_data = [
        {'code': 'MATH101', 'name': 'Mathematics I', 'credits': 3},
        {'code': 'ENG101', 'name': 'English Literature', 'credits': 3},
        {'code': 'SCI101', 'name': 'General Science', 'credits': 4},
        {'code': 'HIST101', 'name': 'Islamic History', 'credits': 2},
        {'code': 'ARAB101', 'name': 'Arabic Language', 'credits': 3},
        {'code': 'PHY101', 'name': 'Physics I', 'credits': 4},
        {'code': 'CHEM101', 'name': 'Chemistry I', 'credits': 4},
        {'code': 'BIO101', 'name': 'Biology I', 'credits': 4},
        {'code': 'COMP101', 'name': 'Computer Science', 'credits': 3},
        {'code': 'ECON101', 'name': 'Economics', 'credits': 3}
    ]
    
    courses_created = 0
    for course_data in courses_data:
        try:
            Course.objects.create(**course_data, is_active=True)
            courses_created += 1
        except Exception as e:
            print_error(f"Error creating course {course_data['code']}: {e}")
    
    print_status(f"Created {courses_created} courses")

@transaction.atomic
def generate_students():
    """Generate 100 students"""
    print_info("Generating 100 students...")
    
    Student.objects.all().delete()
    
    student_users = list(User.objects.filter(role='student'))
    students_created = 0
    
    for i, user in enumerate(student_users[:100]):
        try:
            student = Student.objects.create(
                user=user,
                student_id=f"STD{str(i + 1).zfill(6)}",
                academic_level=random_choice(ACADEMIC_LEVELS),
                enrollment_status=random_choice(ENROLLMENT_STATUSES),
                enrollment_date=safe_random_date(date(2020, 1, 1), date.today()),
                expected_graduation=safe_random_date(date(2024, 1, 1), date(2028, 1, 1)),
            )
            students_created += 1
            
        except Exception as e:
            print_error(f"Error creating student {user.username}: {e}")
    
    print_status(f"Created {students_created} students")

@transaction.atomic
def generate_doctors():
    """Generate 100 doctors"""
    print_info("Generating 100 doctors...")
    
    Doctor.objects.all().delete()
    
    doctor_users = list(User.objects.filter(role='doctor'))
    doctors_created = 0
    
    for i, user in enumerate(doctor_users[:100]):
        try:
            doctor = Doctor.objects.create(
                user=user,
                name=f"Dr. {user.first_name} {user.last_name}",
                its_id=user.its_id or generate_its_id(),
                specialty=random_choice(SPECIALTIES),
                qualification=random_choice(QUALIFICATIONS),
                experience_years=random.randint(1, 25),
                license_number=f"DOC{str(i + 1).zfill(6)}",
                consultation_fee=random.randint(500, 2500),
                is_verified=random.random() > 0.1,
                is_available=random.random() > 0.2,
                phone=user.phone_number or generate_phone(),
                email=user.email,
                languages_spoken='Urdu, English, Arabic',
            )
            doctors_created += 1
            
        except Exception as e:
            print_error(f"Error creating doctor {user.username}: {e}")
    
    print_status(f"Created {doctors_created} doctors")

@transaction.atomic
def generate_hospitals():
    """Generate hospitals"""
    print_info("Generating hospitals...")
    
    Hospital.objects.all().delete()
    
    hospitals_data = [
        {
            'name': 'Saifee Hospital Mumbai',
            'description': 'Premier healthcare facility in Mumbai',
            'address': 'Charni Road, Mumbai, India',
            'phone': '+91-22-67568000',
            'email': 'info@saifeehospital.org',
            'hospital_type': 'general',
            'total_beds': 200,
            'available_beds': 45,
            'emergency_beds': 20,
            'icu_beds': 15,
        },
        {
            'name': 'Burhani Hospital Mumbai',
            'description': 'Specialized medical care center',
            'address': 'Mazgaon, Mumbai, India',
            'phone': '+91-22-23750000',
            'email': 'info@burhanihospital.org',
            'hospital_type': 'specialty',
            'total_beds': 150,
            'available_beds': 30,
            'emergency_beds': 15,
            'icu_beds': 10,
        },
        {
            'name': 'Karachi Saifee Hospital',
            'description': 'Leading healthcare provider in Karachi',
            'address': 'Saddar, Karachi, Pakistan',
            'phone': '+92-21-35862000',
            'email': 'info@karachisaifee.org',
            'hospital_type': 'general',
            'total_beds': 300,
            'available_beds': 60,
            'emergency_beds': 25,
            'icu_beds': 20,
        }
    ]
    
    hospitals_created = 0
    for hospital_data in hospitals_data:
        try:
            Hospital.objects.create(
                **hospital_data,
                is_active=True,
                is_emergency_capable=True,
                has_pharmacy=True,
                has_laboratory=True,
            )
            hospitals_created += 1
        except Exception as e:
            print_error(f"Error creating hospital {hospital_data['name']}: {e}")
    
    print_status(f"Created {hospitals_created} hospitals")

@transaction.atomic
def generate_patients():
    """Generate 100 patients"""
    print_info("Generating 100 patients...")
    
    Patient.objects.all().delete()
    
    patients_created = 0
    for i in range(100):
        try:
            gender = random.choice(['male', 'female'])
            first_name = random_choice(MALE_NAMES if gender == 'male' else FEMALE_NAMES)
            last_name = random_choice(LAST_NAMES)
            
            patient = Patient.objects.create(
                its_id=generate_its_id(),
                first_name=first_name,
                last_name=last_name,
                arabic_name=f"{first_name} {last_name}",
                date_of_birth=safe_random_date(date(1950, 1, 1), date(2010, 1, 1)),
                gender=gender,
                phone_number=generate_phone(),
                email=f"patient{i + 1}@test.com",
                address=f"House {i + 1}, {random_choice(CITIES)}, Pakistan",
                emergency_contact_name=f"{random_choice(MALE_NAMES)} {random_choice(LAST_NAMES)}",
                emergency_contact_phone=generate_phone(),
                emergency_contact_relationship=random.choice(['Father', 'Mother', 'Spouse', 'Brother', 'Sister']),
                blood_group=random_choice(BLOOD_GROUPS),
                allergies='Penicillin, Dust' if random.random() > 0.7 else '',
                chronic_conditions='Diabetes, Hypertension' if random.random() > 0.8 else '',
            )
            patients_created += 1
            
        except Exception as e:
            print_error(f"Error creating patient {i + 1}: {e}")
    
    print_status(f"Created {patients_created} patients")

@transaction.atomic
def generate_medical_records():
    """Generate 100 medical records"""
    print_info("Generating 100 medical records...")
    
    MedicalRecord.objects.all().delete()
    
    patients = list(Patient.objects.all())
    doctors = list(Doctor.objects.all())
    
    if not patients or not doctors:
        print_error("No patients or doctors found for medical records")
        return
    
    records_created = 0
    for i in range(min(100, len(patients))):
        try:
            patient = patients[i]
            doctor = random.choice(doctors)
            
            # Use safe date ranges
            visit_date = safe_random_date(date(2023, 1, 1), date.today())
            follow_up_date = safe_random_date(date.today(), date(2024, 12, 31))
            
            record = MedicalRecord.objects.create(
                patient=patient,
                diagnosis=random_choice(DIAGNOSES),
                symptoms='Patient complaints of general discomfort',
                treatment_plan=random.choice([
                    'Medication prescribed', 'Rest and fluids', 'Physical therapy', 
                    'Dietary changes', 'Follow-up in 2 weeks'
                ]),
                medications='Paracetamol 500mg, Ibuprofen 400mg',
                notes='Patient responded well to treatment',
                visit_date=visit_date,
                follow_up_date=follow_up_date,
            )
            records_created += 1
            
        except Exception as e:
            print_error(f"Error creating medical record {i + 1}: {e}")
    
    print_status(f"Created {records_created} medical records")

@transaction.atomic
def generate_appointments():
    """Generate 100 appointments - FIXED VERSION"""
    print_info("Generating 100 appointments...")
    
    Appointment.objects.all().delete()
    
    patients = list(Patient.objects.all())
    doctor_users = list(User.objects.filter(role='doctor'))  # Get User objects, not Doctor objects
    
    if not patients or not doctor_users:
        print_error("No patients or doctor users found for appointments")
        return
    
    appointments_created = 0
    statuses = ['scheduled', 'confirmed', 'completed', 'cancelled', 'no_show']
    appointment_types = ['consultation', 'follow_up', 'emergency', 'routine_checkup']
    
    for i in range(min(100, len(patients))):
        try:
            patient = patients[i]
            doctor_user = random.choice(doctor_users)  # Use User object for doctor field
            
            appointment_date = safe_random_date(date(2024, 1, 1), date(2024, 12, 31))
            
            appointment = Appointment.objects.create(
                patient=patient,
                doctor=doctor_user,  # Pass User object, not Doctor object
                appointment_date=appointment_date,
                appointment_time=f"{random.randint(9, 16)}:{random.choice(['00', '30'])}",
                status=random_choice(statuses),
                appointment_type=random_choice(appointment_types),
                reason='General consultation and health checkup',
                notes='Patient appears healthy, routine checkup completed',
            )
            appointments_created += 1
            
        except Exception as e:
            print_error(f"Error creating appointment {i + 1}: {e}")
    
    print_status(f"Created {appointments_created} appointments")

@transaction.atomic
def generate_surveys():
    """Generate 10 surveys - FIXED VERSION"""
    print_info("Generating 10 surveys...")
    
    Survey.objects.all().delete()
    
    survey_titles = [
        'Community Health Assessment', 'Education Quality Survey', 'Service Satisfaction Survey',
        'Healthcare Access Survey', 'Moze Services Evaluation', 'Youth Engagement Survey',
        'Digital Services Feedback', 'Annual Community Survey', 'Infrastructure Assessment',
        'Social Services Survey'
    ]
    
    admin_users = User.objects.filter(role='badri_mahal_admin')
    if not admin_users.exists():
        print_error("No admin users found for surveys")
        return
    
    surveys_created = 0
    for i, title in enumerate(survey_titles):
        try:
            # Use safe date ranges
            start_date = safe_random_date(date(2024, 1, 1), date.today())
            end_date = safe_random_date(date.today(), date(2024, 12, 31))
            
            survey = Survey.objects.create(
                title=title,
                description=f"Comprehensive survey to assess {title.lower()}",
                created_by=admin_users.first(),
                is_active=True,
                start_date=start_date,
                end_date=end_date,
                max_responses=random.randint(100, 500),
                is_anonymous=random.random() > 0.3,
            )
            surveys_created += 1
            
        except Exception as e:
            print_error(f"Error creating survey {title}: {e}")
    
    print_status(f"Created {surveys_created} surveys")

@transaction.atomic
def generate_evaluation_forms():
    """Generate 10 evaluation forms"""
    print_info("Generating 10 evaluation forms...")
    
    EvaluationForm.objects.all().delete()
    
    form_titles = [
        'Moze Performance Evaluation', 'Leadership Assessment', 'Service Quality Evaluation',
        'Team Performance Review', 'Annual Evaluation Form', 'Skill Assessment Form',
        'Community Impact Evaluation', 'Efficiency Evaluation', 'Quality Assurance Form',
        'Comprehensive Performance Review'
    ]
    
    admin_users = User.objects.filter(role='badri_mahal_admin')
    if not admin_users.exists():
        print_error("No admin users found for evaluation forms")
        return
    
    forms_created = 0
    for title in form_titles:
        try:
            form = EvaluationForm.objects.create(
                title=title,
                description=f"Detailed evaluation form for {title.lower()}",
                target_role=random.choice(['aamil', 'moze_coordinator', 'all']),
                created_by=admin_users.first(),
                is_active=True,
            )
            forms_created += 1
            
        except Exception as e:
            print_error(f"Error creating evaluation form {title}: {e}")
    
    print_status(f"Created {forms_created} evaluation forms")

@transaction.atomic
def generate_petitions():
    """Generate 100 petitions"""
    print_info("Generating 100 petitions...")
    
    # Create categories first
    for cat_name in PETITION_CATEGORIES:
        PetitionCategory.objects.get_or_create(
            name=cat_name,
            defaults={'description': f'Category for {cat_name.lower()}'}
        )
    
    Petition.objects.all().delete()
    
    petition_titles = [
        'Request for library extension hours', 'Improvement in cafeteria services',
        'Additional parking space needed', 'Medical facility enhancement',
        'Internet connectivity issues', 'Air conditioning repair request',
        'Security system upgrade', 'Playground maintenance request',
        'Computer lab equipment update', 'Cleaning services improvement'
    ]
    
    users = User.objects.filter(is_active=True)
    categories = PetitionCategory.objects.all()
    
    if not users.exists() or not categories.exists():
        print_error("No users or categories found for petitions")
        return
    
    petitions_created = 0
    for i in range(100):
        try:
            title = random_choice(petition_titles)
            
            petition = Petition.objects.create(
                title=f"{title} - Request #{i + 1}",
                description=f"Detailed description for {title.lower()}. This petition addresses important community needs.",
                category=random.choice(categories),
                status=random_choice(PETITION_STATUSES),
                created_by=random.choice(users),
            )
            petitions_created += 1
            
        except Exception as e:
            print_error(f"Error creating petition {i + 1}: {e}")
    
    print_status(f"Created {petitions_created} petitions")

@transaction.atomic
def generate_photo_albums():
    """Generate 10 photo albums"""
    print_info("Generating 10 photo albums...")
    
    PhotoAlbum.objects.all().delete()
    
    album_titles = [
        'Community Events 2024', 'Educational Programs', 'Health Camps', 'Cultural Programs',
        'Religious Gatherings', 'Youth Activities', 'Medical Camps', 'Social Services',
        'Infrastructure Projects', 'Volunteer Activities'
    ]
    
    admin_users = User.objects.filter(role='badri_mahal_admin')
    mozes = Moze.objects.all()
    
    if not admin_users.exists() or not mozes.exists():
        print_error("No admin users or mozes found for photo albums")
        return
    
    albums_created = 0
    for title in album_titles:
        try:
            event_date = safe_random_date(date(2023, 1, 1), date.today())
            
            album = PhotoAlbum.objects.create(
                name=title,
                description=f"Photo collection from {title.lower()}",
                moze=random.choice(mozes),
                created_by=admin_users.first(),
                is_public=random.random() > 0.3,
                allow_uploads=random.random() > 0.4,
                event_date=event_date,
            )
            albums_created += 1
            
        except Exception as e:
            print_error(f"Error creating photo album {title}: {e}")
    
    print_status(f"Created {albums_created} photo albums")

def main():
    """Main function to generate all test data"""
    print("🏥 UMOOR SEHHAT OFFLINE TEST DATA GENERATOR - FIXED VERSION")
    print("=" * 60)
    print("Generating comprehensive test data for all 9 Django apps")
    print("=" * 60)
    
    try:
        # Generate data in correct order (respecting foreign key dependencies)
        generate_users()
        generate_moze()
        generate_courses()
        generate_students()
        generate_doctors()
        generate_hospitals()
        generate_patients()
        generate_medical_records()
        generate_appointments()
        generate_surveys()
        generate_evaluation_forms()
        generate_petitions()
        generate_photo_albums()
        
        print("\n" + "=" * 60)
        print("📊 GENERATION SUMMARY")
        print("=" * 60)
        
        # Print final counts
        print(f"Users: {User.objects.count()}")
        print(f"Moze Centers: {Moze.objects.count()}")
        print(f"Students: {Student.objects.count()}")
        print(f"Courses: {Course.objects.count()}")
        print(f"Doctors: {Doctor.objects.count()}")
        print(f"Hospitals: {Hospital.objects.count()}")
        print(f"Patients: {Patient.objects.count()}")
        print(f"Medical Records: {MedicalRecord.objects.count()}")
        print(f"Appointments: {Appointment.objects.count()}")
        print(f"Surveys: {Survey.objects.count()}")
        print(f"Evaluation Forms: {EvaluationForm.objects.count()}")
        print(f"Petitions: {Petition.objects.count()}")
        print(f"Photo Albums: {PhotoAlbum.objects.count()}")
        
        print("\n🎉 FIXED offline test data generation completed successfully!")
        print("📈 Your dashboard should now show comprehensive statistics!")
        print("🔄 Reload your PythonAnywhere web app to see the changes.")
        
        print("\n👥 TEST USER CREDENTIALS:")
        print("Password for all users: test123456")
        print("- Admin: badri_mahal_admin_001 to badri_mahal_admin_010")
        print("- Aamil: aamil_001 to aamil_100") 
        print("- Student: student_001 to student_100")
        print("- Doctor: doctor_001 to doctor_100")
        print("- Coordinator: moze_coordinator_001 to moze_coordinator_100")
        
    except Exception as e:
        print_error(f"❌ Generation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()