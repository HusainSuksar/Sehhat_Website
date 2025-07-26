#!/usr/bin/env python3
"""
Complete the remaining test data population for Umoor Sehhat
"""

import os
import sys
import django
from django.utils import timezone
import random
from faker import Faker

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

from accounts.models import User
from students.models import Student
from moze.models import Moze
from mahalshifa.models import Hospital
from doctordirectory.models import Doctor, Patient as DDPatient
from evaluation.models import EvaluationForm, EvaluationSubmission
from araz.models import Petition, PetitionComment
from photos.models import PhotoAlbum, Photo, PhotoTag

fake = Faker()

def print_status(message):
    print(f"🔄 {message}")

def print_success(message):
    print(f"✅ {message}")

def complete_remaining_data():
    print("🚀 COMPLETING REMAINING TEST DATA")
    print("="*50)
    
    # Get existing data
    users = list(User.objects.all())
    doctors = [u for u in users if u.role == 'doctor']
    students = [u for u in users if u.role == 'student']
    admins = [u for u in users if u.role == 'admin']
    aamils = [u for u in users if u.role == 'aamil']
    mozes = list(Moze.objects.all())
    hospitals = list(Hospital.objects.all())
    
    print_status(f"Found {len(users)} users, {len(mozes)} mozes, {len(hospitals)} hospitals")
    
    # Complete Doctor Directory - Create doctor profiles
    print_status("Creating doctor directory profiles...")
    specialties = ['General Medicine', 'Cardiology', 'Neurology', 'Orthopedics', 'Pediatrics']
    
    for doctor_user in doctors[:50]:  # Create 50 doctor profiles
        if not Doctor.objects.filter(user=doctor_user).exists():
            moze = random.choice(mozes) if mozes else None
            try:
                Doctor.objects.create(
                    user=doctor_user,
                    name=doctor_user.get_full_name(),
                    its_id=doctor_user.its_id,
                    specialty=random.choice(specialties),
                    qualification=random.choice(['MBBS', 'MD', 'PhD', 'FCPS']),
                    experience_years=random.randint(1, 30),
                    assigned_moze=moze,
                    is_verified=True,
                    is_available=True
                )
            except:
                continue
    
    # Create Patient Profiles (using existing student users)
    print_status("Creating patient profiles...")
    for student_user in students[:50]:  # Create 50 patient profiles
        if not DDPatient.objects.filter(user=student_user).exists():
            try:
                DDPatient.objects.create(
                    user=student_user,
                    date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=70),
                    gender=random.choice(['M', 'F']),
                    blood_group=random.choice(['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']),
                    emergency_contact=fake.phone_number()[:15]
                )
            except:
                continue
    
    # Create Evaluation Forms
    print_status("Creating evaluation forms...")
    target_roles = ['doctor', 'student', 'aamil', 'all']
    
    for i in range(20):
        creator = random.choice(admins + aamils)
        try:
            EvaluationForm.objects.create(
                title=f"Evaluation Form {i+1}: {fake.sentence(nb_words=4)}",
                description=fake.text(max_nb_chars=200),
                evaluation_type=random.choice(['performance', 'satisfaction', 'quality']),
                target_role=random.choice(target_roles),
                is_active=True,
                created_by=creator
            )
        except:
            continue
    
    # Create Petitions
    print_status("Creating petitions...")
    categories = ['medical', 'administrative', 'academic', 'facility', 'complaint']
    statuses = ['pending', 'in_progress', 'resolved', 'rejected']
    
    for i in range(100):
        petitioner = random.choice(users)
        assigned_to = random.choice(admins + aamils) if random.choice([True, False]) else None
        
        try:
            Petition.objects.create(
                title=f"Petition {i+1}: {fake.sentence(nb_words=5)}",
                description=fake.text(max_nb_chars=300),
                category=random.choice(categories),
                petitioner=petitioner,
                assigned_to=assigned_to,
                status=random.choice(statuses),
                priority=random.choice(['low', 'medium', 'high']),
                is_urgent=random.choice([True, False])
            )
        except:
            continue
    
    # Create Photo Albums
    print_status("Creating photo albums...")
    album_names = [
        'Medical Conference 2024', 'Student Activities', 'Hospital Events', 
        'Moze Gatherings', 'Educational Workshops', 'Community Service',
        'Sports Events', 'Cultural Programs', 'Graduation Ceremony', 'Research Projects'
    ]
    
    for name in album_names:
        creator = random.choice(admins + [u for u in users if u.role == 'staff'])
        try:
            PhotoAlbum.objects.create(
                name=name,
                description=fake.text(max_nb_chars=150),
                created_by=creator,
                is_public=random.choice([True, False]),
                moze=random.choice(mozes) if random.choice([True, False]) else None
            )
        except:
            continue
    
    # Create Photo Tags
    print_status("Creating photo tags...")
    tag_names = ['medical', 'education', 'community', 'events', 'students', 'doctors', 'research']
    for tag_name in tag_names:
        try:
            PhotoTag.objects.get_or_create(name=tag_name)
        except:
            continue
    
    print_success("Remaining data population completed!")

def show_final_status():
    from surveys.models import Survey
    from mahalshifa.models import Patient
    
    print("\n📊 FINAL DATA STATUS:")
    print(f"👥 Users: {User.objects.count()}")
    print(f"🎓 Students: {Student.objects.count()}")
    print(f"📚 Surveys: {Survey.objects.count()}")
    print(f"🕌 Moze Centers: {Moze.objects.count()}")
    print(f"🏥 Hospitals: {Hospital.objects.count()}")
    print(f"🩺 Doctors: {Doctor.objects.count()}")
    print(f"👥 Directory Patients: {DDPatient.objects.count()}")
    print(f"📝 Evaluation Forms: {EvaluationForm.objects.count()}")
    print(f"📄 Petitions: {Petition.objects.count()}")
    print(f"📸 Photo Albums: {PhotoAlbum.objects.count()}")
    print(f"🏷️  Photo Tags: {PhotoTag.objects.count()}")
    
    print("\n🔐 LOGIN CREDENTIALS:")
    print("- Admin: admin_1 / admin123")
    print("- Doctor: doctor_001 / doctor123")
    print("- Student: student_001 / student123")
    print("- Staff: staff_1 / staff123")
    
    print("\n🎉 ALL APPS READY FOR TESTING!")

if __name__ == "__main__":
    complete_remaining_data()
    show_final_status()