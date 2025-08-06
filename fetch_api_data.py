#!/usr/bin/env python3
"""
API Data Fetcher for Umoor Sehhat
This script fetches data from Beeceptor mock API and populates Django models
Covers all 9 Django apps with 500+ records
"""

import os
import django
import requests
import json
from datetime import datetime, date
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
# CONFIGURATION
# =============================================================================
# Replace 'your-endpoint' with your actual Beeceptor endpoint
API_BASE_URL = 'https://your-endpoint.free.beeceptor.com'  # UPDATE THIS!

def print_status(message):
    print(f"✅ {message}")

def print_info(message):
    print(f"ℹ️  {message}")

def print_error(message):
    print(f"❌ {message}")

def print_warning(message):
    print(f"⚠️  {message}")

def fetch_api_data(endpoint):
    """Fetch data from API endpoint"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        print_info(f"Fetching data from: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get('results', data)
    except requests.exceptions.RequestException as e:
        print_error(f"API request failed for {endpoint}: {e}")
        return []
    except json.JSONDecodeError as e:
        print_error(f"JSON decode error for {endpoint}: {e}")
        return []

def safe_date_parse(date_string):
    """Safely parse date string"""
    if not date_string:
        return None
    try:
        if 'T' in date_string:
            return datetime.fromisoformat(date_string.replace('Z', '+00:00')).date()
        else:
            return datetime.strptime(date_string, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return timezone.now().date()

def safe_datetime_parse(datetime_string):
    """Safely parse datetime string"""
    if not datetime_string:
        return timezone.now()
    try:
        if 'T' in datetime_string:
            return datetime.fromisoformat(datetime_string.replace('Z', '+00:00'))
        else:
            return timezone.now()
    except (ValueError, TypeError):
        return timezone.now()

# =============================================================================
# DATA IMPORT FUNCTIONS
# =============================================================================

@transaction.atomic
def import_users():
    """Import users from API"""
    print_info("Importing users...")
    users_data = fetch_api_data('/api/users/')
    
    if not users_data:
        print_warning("No users data received from API")
        return
    
    User.objects.filter(is_superuser=False).delete()  # Keep superusers
    
    users_created = 0
    for user_data in users_data:
        try:
            user = User.objects.create_user(
                username=user_data.get('username'),
                email=user_data.get('email'),
                password='test123456',  # Default password for all test users
                first_name=user_data.get('first_name', ''),
                last_name=user_data.get('last_name', ''),
                role=user_data.get('role', 'user'),
                its_id=user_data.get('its_id', ''),
                phone_number=user_data.get('phone_number', ''),
                is_active=user_data.get('is_active', True),
                is_staff=user_data.get('is_staff', False),
            )
            users_created += 1
        except Exception as e:
            print_error(f"Error creating user {user_data.get('username')}: {e}")
    
    print_status(f"Created {users_created} users")

@transaction.atomic
def import_moze():
    """Import Moze centers from API"""
    print_info("Importing Moze centers...")
    moze_data = fetch_api_data('/api/moze/')
    
    if not moze_data:
        print_warning("No Moze data received from API")
        return
    
    Moze.objects.all().delete()
    
    moze_created = 0
    for moze_item in moze_data:
        try:
            # Get aamil and coordinator users
            aamil = None
            coordinator = None
            
            if moze_item.get('aamil_id'):
                aamil = User.objects.filter(role='aamil').first()
            
            if moze_item.get('moze_coordinator_id'):
                coordinator = User.objects.filter(role='moze_coordinator').first()
            
            if not aamil:
                print_warning(f"No aamil found for Moze {moze_item.get('name')}")
                continue
            
            moze = Moze.objects.create(
                name=moze_item.get('name'),
                location=moze_item.get('location', ''),
                address=moze_item.get('address', ''),
                aamil=aamil,
                moze_coordinator=coordinator,
                contact_phone=moze_item.get('contact_phone', ''),
                contact_email=moze_item.get('contact_email', ''),
                established_date=safe_date_parse(moze_item.get('established_date')),
                is_active=moze_item.get('is_active', True),
                capacity=moze_item.get('capacity', 100),
            )
            moze_created += 1
        except Exception as e:
            print_error(f"Error creating Moze {moze_item.get('name')}: {e}")
    
    print_status(f"Created {moze_created} Moze centers")

@transaction.atomic
def import_courses():
    """Import courses from API"""
    print_info("Importing courses...")
    courses_data = fetch_api_data('/api/courses/')
    
    if not courses_data:
        print_warning("No courses data received from API")
        return
    
    Course.objects.all().delete()
    
    courses_created = 0
    for course_data in courses_data:
        try:
            course = Course.objects.create(
                code=course_data.get('code'),
                name=course_data.get('name'),
                credits=course_data.get('credits', 3),
                is_active=course_data.get('is_active', True),
            )
            courses_created += 1
        except Exception as e:
            print_error(f"Error creating course {course_data.get('code')}: {e}")
    
    print_status(f"Created {courses_created} courses")

@transaction.atomic
def import_students():
    """Import students from API"""
    print_info("Importing students...")
    students_data = fetch_api_data('/api/students/')
    
    if not students_data:
        print_warning("No students data received from API")
        return
    
    Student.objects.all().delete()
    
    students_created = 0
    student_users = User.objects.filter(role='student')
    
    for i, student_data in enumerate(students_data):
        try:
            if i >= student_users.count():
                break
                
            user = student_users[i]
            
            student = Student.objects.create(
                user=user,
                student_id=student_data.get('student_id'),
                academic_level=student_data.get('academic_level', 'undergraduate'),
                enrollment_status=student_data.get('enrollment_status', 'active'),
                enrollment_date=safe_date_parse(student_data.get('enrollment_date')),
                expected_graduation=safe_date_parse(student_data.get('expected_graduation')),
            )
            students_created += 1
        except Exception as e:
            print_error(f"Error creating student {student_data.get('student_id')}: {e}")
    
    print_status(f"Created {students_created} students")

@transaction.atomic
def import_doctors():
    """Import doctors from API"""
    print_info("Importing doctors...")
    doctors_data = fetch_api_data('/api/doctors/')
    
    if not doctors_data:
        print_warning("No doctors data received from API")
        return
    
    Doctor.objects.all().delete()
    
    doctors_created = 0
    doctor_users = User.objects.filter(role='doctor')
    
    for i, doctor_data in enumerate(doctors_data):
        try:
            if i >= doctor_users.count():
                break
                
            user = doctor_users[i]
            
            doctor = Doctor.objects.create(
                user=user,
                name=doctor_data.get('name', user.get_full_name()),
                its_id=doctor_data.get('its_id', f'{user.id:08d}'),
                specialty=doctor_data.get('specialty', 'General Medicine'),
                qualification=doctor_data.get('qualification', 'MBBS'),
                experience_years=doctor_data.get('experience_years', 5),
                license_number=doctor_data.get('license_number', f'DOC{user.id:06d}'),
                consultation_fee=doctor_data.get('consultation_fee', 1000),
                is_verified=doctor_data.get('is_verified', True),
                is_available=doctor_data.get('is_available', True),
                phone=doctor_data.get('phone', user.phone_number),
                email=doctor_data.get('email', user.email),
                languages_spoken=doctor_data.get('languages_spoken', 'Urdu, English'),
            )
            doctors_created += 1
        except Exception as e:
            print_error(f"Error creating doctor {doctor_data.get('name')}: {e}")
    
    print_status(f"Created {doctors_created} doctors")

@transaction.atomic
def import_hospitals():
    """Import hospitals from API"""
    print_info("Importing hospitals...")
    hospitals_data = fetch_api_data('/api/hospitals/')
    
    if not hospitals_data:
        print_warning("No hospitals data received from API")
        return
    
    Hospital.objects.all().delete()
    
    hospitals_created = 0
    for hospital_data in hospitals_data:
        try:
            hospital = Hospital.objects.create(
                name=hospital_data.get('name'),
                description=hospital_data.get('description', ''),
                address=hospital_data.get('address'),
                phone=hospital_data.get('phone'),
                email=hospital_data.get('email'),
                hospital_type=hospital_data.get('hospital_type', 'general'),
                total_beds=hospital_data.get('total_beds', 100),
                available_beds=hospital_data.get('available_beds', 50),
                emergency_beds=hospital_data.get('emergency_beds', 10),
                icu_beds=hospital_data.get('icu_beds', 5),
                is_active=hospital_data.get('is_active', True),
                is_emergency_capable=hospital_data.get('is_emergency_capable', True),
                has_pharmacy=hospital_data.get('has_pharmacy', True),
                has_laboratory=hospital_data.get('has_laboratory', True),
            )
            hospitals_created += 1
        except Exception as e:
            print_error(f"Error creating hospital {hospital_data.get('name')}: {e}")
    
    print_status(f"Created {hospitals_created} hospitals")

@transaction.atomic
def import_patients():
    """Import patients from API"""
    print_info("Importing patients...")
    patients_data = fetch_api_data('/api/patients/')
    
    if not patients_data:
        print_warning("No patients data received from API")
        return
    
    Patient.objects.all().delete()
    
    patients_created = 0
    for patient_data in patients_data:
        try:
            patient = Patient.objects.create(
                its_id=patient_data.get('its_id'),
                first_name=patient_data.get('first_name'),
                last_name=patient_data.get('last_name'),
                arabic_name=patient_data.get('arabic_name', ''),
                date_of_birth=safe_date_parse(patient_data.get('date_of_birth')),
                gender=patient_data.get('gender'),
                phone_number=patient_data.get('phone_number'),
                email=patient_data.get('email', ''),
                address=patient_data.get('address'),
                emergency_contact_name=patient_data.get('emergency_contact_name'),
                emergency_contact_phone=patient_data.get('emergency_contact_phone'),
                emergency_contact_relationship=patient_data.get('emergency_contact_relationship'),
                blood_group=patient_data.get('blood_group', 'O+'),
                allergies=patient_data.get('allergies', ''),
                chronic_conditions=patient_data.get('chronic_conditions', ''),
            )
            patients_created += 1
        except Exception as e:
            print_error(f"Error creating patient {patient_data.get('first_name')}: {e}")
    
    print_status(f"Created {patients_created} patients")

@transaction.atomic
def import_medical_records():
    """Import medical records from API"""
    print_info("Importing medical records...")
    records_data = fetch_api_data('/api/medical-records/')
    
    if not records_data:
        print_warning("No medical records data received from API")
        return
    
    MedicalRecord.objects.all().delete()
    
    records_created = 0
    patients = list(Patient.objects.all())
    doctors = list(Doctor.objects.all())
    
    for record_data in records_data:
        try:
            # Get patient and doctor
            patient_id = record_data.get('patient_id', 1)
            doctor_id = record_data.get('doctor_id', 1)
            
            patient = patients[patient_id - 1] if patient_id <= len(patients) else patients[0]
            doctor = doctors[doctor_id - 1] if doctor_id <= len(doctors) else doctors[0]
            
            if not patient or not doctor:
                continue
            
            record = MedicalRecord.objects.create(
                patient=patient,
                diagnosis=record_data.get('diagnosis', 'General checkup'),
                symptoms=record_data.get('symptoms', ''),
                treatment_plan=record_data.get('treatment_plan', ''),
                medications=record_data.get('medications', ''),
                notes=record_data.get('notes', ''),
                visit_date=safe_date_parse(record_data.get('visit_date')),
                follow_up_date=safe_date_parse(record_data.get('follow_up_date')),
            )
            records_created += 1
        except Exception as e:
            print_error(f"Error creating medical record: {e}")
    
    print_status(f"Created {records_created} medical records")

@transaction.atomic
def import_appointments():
    """Import appointments from API"""
    print_info("Importing appointments...")
    appointments_data = fetch_api_data('/api/appointments/')
    
    if not appointments_data:
        print_warning("No appointments data received from API")
        return
    
    Appointment.objects.all().delete()
    
    appointments_created = 0
    patients = list(Patient.objects.all())
    doctors = list(Doctor.objects.all())
    
    for appointment_data in appointments_data:
        try:
            # Get patient and doctor
            patient_id = appointment_data.get('patient_id', 1)
            doctor_id = appointment_data.get('doctor_id', 1)
            
            patient = patients[patient_id - 1] if patient_id <= len(patients) else patients[0]
            doctor = doctors[doctor_id - 1] if doctor_id <= len(doctors) else doctors[0]
            
            if not patient or not doctor:
                continue
            
            appointment = Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                appointment_date=safe_date_parse(appointment_data.get('appointment_date')),
                appointment_time=appointment_data.get('appointment_time', '10:00'),
                status=appointment_data.get('status', 'scheduled'),
                appointment_type=appointment_data.get('appointment_type', 'consultation'),
                reason=appointment_data.get('reason', 'General consultation'),
                notes=appointment_data.get('notes', ''),
            )
            appointments_created += 1
        except Exception as e:
            print_error(f"Error creating appointment: {e}")
    
    print_status(f"Created {appointments_created} appointments")

@transaction.atomic
def import_surveys():
    """Import surveys from API"""
    print_info("Importing surveys...")
    surveys_data = fetch_api_data('/api/surveys/')
    
    if not surveys_data:
        print_warning("No surveys data received from API")
        return
    
    Survey.objects.all().delete()
    
    surveys_created = 0
    admin_users = User.objects.filter(role='badri_mahal_admin')
    
    for survey_data in surveys_data:
        try:
            created_by = admin_users.first() if admin_users.exists() else None
            if not created_by:
                continue
            
            survey = Survey.objects.create(
                title=survey_data.get('title'),
                description=survey_data.get('description', ''),
                created_by=created_by,
                is_active=survey_data.get('is_active', True),
                start_date=safe_date_parse(survey_data.get('start_date')),
                end_date=safe_date_parse(survey_data.get('end_date')),
                max_responses=survey_data.get('max_responses', 1000),
                is_anonymous=survey_data.get('is_anonymous', True),
            )
            surveys_created += 1
        except Exception as e:
            print_error(f"Error creating survey {survey_data.get('title')}: {e}")
    
    print_status(f"Created {surveys_created} surveys")

@transaction.atomic
def import_evaluation_forms():
    """Import evaluation forms from API"""
    print_info("Importing evaluation forms...")
    forms_data = fetch_api_data('/api/evaluation-forms/')
    
    if not forms_data:
        print_warning("No evaluation forms data received from API")
        return
    
    EvaluationForm.objects.all().delete()
    
    forms_created = 0
    admin_users = User.objects.filter(role='badri_mahal_admin')
    
    for form_data in forms_data:
        try:
            created_by = admin_users.first() if admin_users.exists() else None
            if not created_by:
                continue
            
            form = EvaluationForm.objects.create(
                title=form_data.get('title'),
                description=form_data.get('description', ''),
                target_role=form_data.get('target_role', 'all'),
                created_by=created_by,
                is_active=form_data.get('is_active', True),
            )
            forms_created += 1
        except Exception as e:
            print_error(f"Error creating evaluation form {form_data.get('title')}: {e}")
    
    print_status(f"Created {forms_created} evaluation forms")

@transaction.atomic
def import_petitions():
    """Import petitions from API"""
    print_info("Importing petitions...")
    petitions_data = fetch_api_data('/api/araz/')
    
    if not petitions_data:
        print_warning("No petitions data received from API")
        return
    
    # Create categories first
    categories = ['Academic Issues', 'Administrative Issues', 'Infrastructure', 'Health Services', 'General Complaints']
    for cat_name in categories:
        PetitionCategory.objects.get_or_create(
            name=cat_name,
            defaults={'description': f'Category for {cat_name.lower()}'}
        )
    
    Petition.objects.all().delete()
    
    petitions_created = 0
    users = User.objects.filter(is_active=True)
    categories_objs = PetitionCategory.objects.all()
    
    for petition_data in petitions_data:
        try:
            created_by = users.first() if users.exists() else None
            category = categories_objs.first() if categories_objs.exists() else None
            
            if not created_by or not category:
                continue
            
            petition = Petition.objects.create(
                title=petition_data.get('title'),
                description=petition_data.get('description', ''),
                category=category,
                status=petition_data.get('status', 'pending'),
                created_by=created_by,
            )
            petitions_created += 1
        except Exception as e:
            print_error(f"Error creating petition {petition_data.get('title')}: {e}")
    
    print_status(f"Created {petitions_created} petitions")

@transaction.atomic
def import_photo_albums():
    """Import photo albums from API"""
    print_info("Importing photo albums...")
    albums_data = fetch_api_data('/api/photo-albums/')
    
    if not albums_data:
        print_warning("No photo albums data received from API")
        return
    
    PhotoAlbum.objects.all().delete()
    
    albums_created = 0
    admin_users = User.objects.filter(role='badri_mahal_admin')
    mozes = Moze.objects.all()
    
    for album_data in albums_data:
        try:
            created_by = admin_users.first() if admin_users.exists() else None
            moze = mozes.first() if mozes.exists() else None
            
            if not created_by or not moze:
                continue
            
            album = PhotoAlbum.objects.create(
                name=album_data.get('name'),
                description=album_data.get('description', ''),
                moze=moze,
                created_by=created_by,
                is_public=album_data.get('is_public', True),
                allow_uploads=album_data.get('allow_uploads', True),
                event_date=safe_date_parse(album_data.get('event_date')),
            )
            albums_created += 1
        except Exception as e:
            print_error(f"Error creating photo album {album_data.get('name')}: {e}")
    
    print_status(f"Created {albums_created} photo albums")

def main():
    """Main function to import all data"""
    print("🏥 UMOOR SEHHAT API DATA IMPORTER")
    print("=" * 50)
    print(f"API Base URL: {API_BASE_URL}")
    print("=" * 50)
    
    if 'your-endpoint' in API_BASE_URL:
        print_error("❌ Please update API_BASE_URL with your actual Beeceptor endpoint!")
        print_info("Edit the script and replace 'your-endpoint' with your Beeceptor URL")
        return
    
    try:
        # Test API connection
        print_info("Testing API connection...")
        test_data = fetch_api_data('/api/summary/')
        if not test_data:
            print_error("❌ Cannot connect to API. Check your endpoint URL.")
            return
        
        print_status("✅ API connection successful!")
        
        # Import data in correct order (respecting foreign key dependencies)
        import_users()
        import_moze()
        import_courses()
        import_students()
        import_doctors()
        import_hospitals()
        import_patients()
        import_medical_records()
        import_appointments()
        import_surveys()
        import_evaluation_forms()
        import_petitions()
        import_photo_albums()
        
        print("\n" + "=" * 50)
        print("📊 IMPORT SUMMARY")
        print("=" * 50)
        
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
        
        print("\n🎉 API data import completed successfully!")
        print("📈 Your dashboard should now show comprehensive statistics!")
        print("🔄 Reload your PythonAnywhere web app to see the changes.")
        
    except Exception as e:
        print_error(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()