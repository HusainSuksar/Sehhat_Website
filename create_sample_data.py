#!/usr/bin/env python3
"""
Sample Data Creation Script for Umoor Sehhat
This script creates sample data for all models to populate dashboard statistics
"""

import os
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings_pythonanywhere')
django.setup()

from accounts.models import User
from students.models import Student, Course
from moze.models import Moze
from mahalshifa.models import Hospital, Patient, MedicalRecord
from doctordirectory.models import Doctor
from surveys.models import Survey
from araz.models import Petition, PetitionCategory
from photos.models import PhotoAlbum

def print_status(message):
    print(f"✅ {message}")

def print_info(message):
    print(f"ℹ️  {message}")

def print_error(message):
    print(f"❌ {message}")

def create_students():
    """Create sample students"""
    print_info("Creating sample students...")
    
    # Get student users
    student_users = User.objects.filter(role='student')
    
    for user in student_users:
        try:
            student, created = Student.objects.get_or_create(
                user=user,
                defaults={
                    'student_id': f'STD{user.id:03d}',
                    'enrollment_date': timezone.now().date() - timedelta(days=365),
                    'academic_level': 'undergraduate',
                    'enrollment_status': 'active',
                }
            )
            if created:
                print_status(f"Created student: {student.user.get_full_name()}")
        except Exception as e:
            print_error(f"Error creating student for {user.username}: {e}")

def create_courses():
    """Create sample courses"""
    print_info("Creating sample courses...")
    
    courses_data = [
        {'code': 'MATH101', 'name': 'Mathematics I', 'credits': 3},
        {'code': 'ENG101', 'name': 'English Literature', 'credits': 3},
        {'code': 'SCI101', 'name': 'General Science', 'credits': 4},
        {'code': 'HIST101', 'name': 'Islamic History', 'credits': 2},
        {'code': 'ARAB101', 'name': 'Arabic Language', 'credits': 3},
    ]
    
    for course_data in courses_data:
        try:
            course, created = Course.objects.get_or_create(
                code=course_data['code'],
                defaults={
                    'name': course_data['name'],
                    'credits': course_data['credits'],
                    'is_active': True,
                }
            )
            if created:
                print_status(f"Created course: {course.name}")
        except Exception as e:
            print_error(f"Error creating course {course_data['code']}: {e}")

def create_moze_centers():
    """Create sample Moze centers"""
    print_info("Creating sample Moze centers...")
    
    # Get aamil and coordinator users
    aamils = User.objects.filter(role='aamil')
    coordinators = User.objects.filter(role='moze_coordinator')
    
    moze_data = [
        {
            'name': 'Karachi Central Moze',
            'location': 'Karachi, Pakistan',
            'phone': '+92-300-1234567',
            'email': 'karachi@moze.com',
        },
        {
            'name': 'Lahore North Moze',
            'location': 'Lahore, Pakistan', 
            'phone': '+92-300-2345678',
            'email': 'lahore@moze.com',
        },
        {
            'name': 'Islamabad Moze',
            'location': 'Islamabad, Pakistan',
            'phone': '+92-300-3456789',
            'email': 'islamabad@moze.com',
        },
    ]
    
    for i, moze_info in enumerate(moze_data):
        try:
            moze, created = Moze.objects.get_or_create(
                name=moze_info['name'],
                defaults={
                    'location': moze_info['location'],
                    'contact_phone': moze_info['phone'],
                    'contact_email': moze_info['email'],
                    'aamil': aamils[i % aamils.count()] if aamils.exists() else None,
                    'moze_coordinator': coordinators[i % coordinators.count()] if coordinators.exists() else None,
                    'is_active': True,
                }
            )
            if created:
                print_status(f"Created Moze center: {moze.name}")
        except Exception as e:
            print_error(f"Error creating Moze {moze_info['name']}: {e}")

def create_hospitals():
    """Create sample hospitals"""
    print_info("Creating sample hospitals...")
    
    hospitals_data = [
        {
            'name': 'Saifee Hospital',
            'address': 'Charni Road, Mumbai',
            'phone': '+91-22-67568000',
        },
        {
            'name': 'Burhani Hospital',
            'address': 'Mazgaon, Mumbai',
            'phone': '+91-22-23750000',
        },
        {
            'name': 'Karachi Saifee Hospital',
            'address': 'Karachi, Pakistan',
            'phone': '+92-21-35862000',
        },
    ]
    
    for hospital_data in hospitals_data:
        try:
            hospital, created = Hospital.objects.get_or_create(
                name=hospital_data['name'],
                defaults={
                    'address': hospital_data['address'],
                    'phone': hospital_data['phone'],
                    'email': f"info@{hospital_data['name'].lower().replace(' ', '')}.com",
                    'is_active': True,
                }
            )
            if created:
                print_status(f"Created hospital: {hospital.name}")
        except Exception as e:
            print_error(f"Error creating hospital {hospital_data['name']}: {e}")

def create_doctors():
    """Create sample doctors"""
    print_info("Creating sample doctors...")
    
    # Get doctor users
    doctor_users = User.objects.filter(role='doctor')
    
    specialties = ['General Medicine', 'Cardiology', 'Pediatrics', 'Orthopedics', 'Dermatology']
    
    for i, user in enumerate(doctor_users):
        try:
            doctor, created = Doctor.objects.get_or_create(
                user=user,
                defaults={
                    'name': user.get_full_name(),
                    'its_id': f'{user.id:08d}',  # 8-digit ITS ID
                    'specialty': specialties[i % len(specialties)],
                    'qualification': 'MBBS, MD',
                    'experience_years': 5 + (i * 2),
                    'license_number': f'DOC{user.id:04d}',
                    'is_available': True,
                    'is_verified': True,
                    'consultation_fee': 500.00,
                    'phone': user.phone_number,
                    'email': user.email,
                }
            )
            if created:
                print_status(f"Created doctor: {doctor.name}")
        except Exception as e:
            print_error(f"Error creating doctor for {user.username}: {e}")

def create_surveys():
    """Create sample surveys"""
    print_info("Creating sample surveys...")
    
    admin_user = User.objects.filter(role='badri_mahal_admin').first()
    if not admin_user:
        print_info("No admin user found, skipping surveys")
        return
    
    surveys_data = [
        {
            'title': 'Community Health Survey',
            'description': 'Survey about community health needs',
        },
        {
            'title': 'Education Feedback',
            'description': 'Feedback on educational programs',
        },
        {
            'title': 'Service Quality Assessment',
            'description': 'Assessment of service quality',
        },
    ]
    
    for survey_data in surveys_data:
        try:
            survey, created = Survey.objects.get_or_create(
                title=survey_data['title'],
                defaults={
                    'description': survey_data['description'],
                    'created_by': admin_user,
                    'is_active': True,
                }
            )
            if created:
                print_status(f"Created survey: {survey.title}")
        except Exception as e:
            print_error(f"Error creating survey {survey_data['title']}: {e}")

def create_petitions():
    """Create sample petitions"""
    print_info("Creating sample petitions...")
    
    # Create petition categories
    categories_data = [
        'Academic Issues',
        'Administrative Issues',
        'Infrastructure',
        'Health Services',
        'General Complaints',
    ]
    
    for cat_name in categories_data:
        try:
            category, created = PetitionCategory.objects.get_or_create(
                name=cat_name,
                defaults={'description': f'Category for {cat_name.lower()}'}
            )
            if created:
                print_status(f"Created petition category: {category.name}")
        except Exception as e:
            print_error(f"Error creating category {cat_name}: {e}")
    
    # Create petitions
    categories = PetitionCategory.objects.all()
    users = User.objects.filter(is_active=True)[:5]  # Use first 5 users
    
    petitions_data = [
        'Request for library extension hours',
        'Improvement in cafeteria services',
        'Additional parking space needed',
        'Medical facility enhancement',
        'Internet connectivity issues',
    ]
    
    for i, petition_title in enumerate(petitions_data):
        try:
            petition, created = Petition.objects.get_or_create(
                title=petition_title,
                defaults={
                    'description': f'Detailed description for {petition_title.lower()}',
                    'category': categories[i % categories.count()],
                    'created_by': users[i % users.count()],
                    'status': 'pending',
                }
            )
            if created:
                print_status(f"Created petition: {petition.title}")
        except Exception as e:
            print_error(f"Error creating petition {petition_title}: {e}")

def create_photo_albums():
    """Create sample photo albums"""
    print_info("Creating sample photo albums...")
    
    admin_user = User.objects.filter(role='badri_mahal_admin').first()
    if not admin_user:
        print_info("No admin user found, skipping photo albums")
        return
    
    albums_data = [
        {
            'title': 'Community Events 2024',
            'description': 'Photos from various community events',
        },
        {
            'title': 'Educational Programs',
            'description': 'Documentation of educational activities',
        },
        {
            'title': 'Health Camps',
            'description': 'Medical camps and health initiatives',
        },
        {
            'title': 'Cultural Programs',
            'description': 'Cultural and religious programs',
        },
    ]
    
    for album_data in albums_data:
        try:
            # PhotoAlbum requires a moze, so we'll skip if no mozes exist
            mozes = Moze.objects.all()
            if not mozes.exists():
                print_info("No Mozes found, skipping photo albums")
                return
                
            album, created = PhotoAlbum.objects.get_or_create(
                name=album_data['title'],
                defaults={
                    'description': album_data['description'],
                    'created_by': admin_user,
                    'moze': mozes.first(),
                    'is_public': True,
                }
            )
            if created:
                print_status(f"Created photo album: {album.name}")
        except Exception as e:
            print_error(f"Error creating album {album_data['title']}: {e}")

def create_patients_and_records():
    """Create sample patients and medical records"""
    print_info("Creating sample patients and medical records...")
    
    hospitals = Hospital.objects.all()
    if not hospitals.exists():
        print_info("No hospitals found, skipping patients")
        return
    
    # Create sample patients
    patients_data = [
        {'first_name': 'Ahmed', 'last_name': 'Hassan', 'phone': '+92-300-1111111', 'its_id': '12345678'},
        {'first_name': 'Fatima', 'last_name': 'Ali', 'phone': '+92-300-2222222', 'its_id': '12345679'},
        {'first_name': 'Mohammad', 'last_name': 'Khan', 'phone': '+92-300-3333333', 'its_id': '12345680'},
        {'first_name': 'Aisha', 'last_name': 'Sheikh', 'phone': '+92-300-4444444', 'its_id': '12345681'},
    ]
    
    for patient_data in patients_data:
        try:
            patient, created = Patient.objects.get_or_create(
                its_id=patient_data['its_id'],
                defaults={
                    'first_name': patient_data['first_name'],
                    'last_name': patient_data['last_name'],
                    'phone_number': patient_data['phone'],
                    'date_of_birth': timezone.now().date() - timedelta(days=25*365),  # 25 years old
                    'gender': 'male',
                    'address': 'Test Address',
                    'emergency_contact_name': 'Emergency Contact',
                    'emergency_contact_phone': '+92-300-0000000',
                    'emergency_contact_relationship': 'Family',
                }
            )
            if created:
                patient_name = f"{patient.first_name} {patient.last_name}"
                print_status(f"Created patient: {patient_name}")
                
                # Create medical record for this patient
                try:
                    record, record_created = MedicalRecord.objects.get_or_create(
                        patient=patient,
                        defaults={
                            'diagnosis': 'General checkup',
                            'treatment': 'Routine examination completed',
                            'date_created': timezone.now().date(),
                        }
                    )
                    if record_created:
                        print_status(f"Created medical record for: {patient_name}")
                except Exception as e:
                    print_error(f"Error creating medical record for {patient_name}: {e}")
        except Exception as e:
            print_error(f"Error creating patient {patient_data['first_name']} {patient_data['last_name']}: {e}")

def main():
    """Main function to create all sample data"""
    print("🏥 CREATING SAMPLE DATA FOR UMOOR SEHHAT")
    print("=" * 50)
    
    try:
        create_students()
        create_courses()
        create_moze_centers()
        create_hospitals()
        create_doctors()
        create_surveys()
        create_petitions()
        create_photo_albums()
        create_patients_and_records()
        
        print("\n" + "=" * 50)
        print("📊 FINAL STATISTICS")
        print("=" * 50)
        
        # Print final counts
        print(f"Users: {User.objects.count()}")
        print(f"Students: {Student.objects.count()}")
        print(f"Courses: {Course.objects.count()}")
        print(f"Moze Centers: {Moze.objects.count()}")
        print(f"Hospitals: {Hospital.objects.count()}")
        print(f"Doctors: {Doctor.objects.count()}")
        print(f"Surveys: {Survey.objects.count()}")
        print(f"Petitions: {Petition.objects.count()}")
        print(f"Photo Albums: {PhotoAlbum.objects.count()}")
        print(f"Patients: {Patient.objects.count()}")
        print(f"Medical Records: {MedicalRecord.objects.count()}")
        
        print("\n🎉 Sample data creation completed successfully!")
        print("📈 Dashboard statistics should now show meaningful numbers!")
        
    except Exception as e:
        print_error(f"Error in main execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()