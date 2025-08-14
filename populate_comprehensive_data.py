#!/usr/bin/env python3
"""
Comprehensive Data Population Script for Umoor Sehhat
Creates 120 users in MOCKITS with all details and populates data for all apps
"""

import os
import sys
import django
from datetime import datetime, timedelta
import random
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings

# Import models
from accounts.models import User
from moze.models import Moze
from students.models import Student, Course
from doctordirectory.models import Doctor, Patient, Appointment as DoctorAppointment
from mahalshifa.models import (
    Hospital, Doctor as MahalShifaDoctor, Patient as MahalShifaPatient, 
    Appointment as MahalShifaAppointment, MedicalService, MedicalRecord
)
from araz.models import Petition, PetitionCategory
from surveys.models import Survey
from photos.models import PhotoAlbum, Photo
from evaluation.models import EvaluationForm, EvaluationResponse

User = get_user_model()

class ComprehensiveDataPopulator:
    """Comprehensive data populator for all apps"""
    
    def __init__(self):
        self.created_users = []
        self.created_mozes = []
        self.created_hospitals = []
        self.created_doctors = []
        self.created_patients = []
        self.created_appointments = []
        self.created_medical_records = []
        self.created_petitions = []
        self.created_surveys = []
        self.created_albums = []
        self.created_evaluations = []
        
        # Data pools for realistic generation
        self.first_names = [
            'Mohammed', 'Ahmed', 'Ali', 'Hassan', 'Hussein', 'Fatima', 'Zainab', 'Khadija', 
            'Aisha', 'Mariam', 'Omar', 'Yusuf', 'Ibrahim', 'Ismail', 'Mustafa', 'Amina',
            'Safiya', 'Ruqayyah', 'Zahra', 'Maryam', 'Abdullah', 'Abdul Rahman', 'Khalid',
            'Bilal', 'Hamza', 'Umar', 'Uthman', 'Salman', 'Noor', 'Hanan', 'Ahmad', 'Mahmoud',
            'Hassan', 'Hussein', 'Jaafar', 'Abbas', 'Hasan', 'Husain', 'Zain', 'Sajjad',
            'Baqir', 'Sadiq', 'Kazim', 'Ridha', 'Jawad', 'Hadi', 'Askari', 'Mahdi'
        ]
        
        self.last_names = [
            'Khan', 'Ali', 'Ahmed', 'Sheikh', 'Malik', 'Shah', 'Hussain', 'Qureshi',
            'Syed', 'Ansari', 'Shaikh', 'Patel', 'Merchant', 'Contractor', 'Engineer',
            'Doctor', 'Professor', 'Saifuddin', 'Najmuddin', 'Burhanuddin', 'Husaini',
            'Rizvi', 'Naqvi', 'Jafri', 'Zaidi', 'Abidi', 'Rizvi', 'Naqvi', 'Jafri'
        ]
        
        self.specializations = [
            'General Medicine', 'Cardiology', 'Pediatrics', 'Gynecology', 'Orthopedics',
            'Dermatology', 'Neurology', 'Psychiatry', 'Ophthalmology', 'ENT', 'Dental',
            'Surgery', 'Emergency Medicine', 'Internal Medicine', 'Family Medicine'
        ]
        
        self.qualifications = [
            'MBBS', 'MBBS, MD', 'MBBS, MS', 'MBBS, DNB', 'MBBS, FRCS', 'MBBS, MRCP',
            'MBBS, FRCSEd', 'MBBS, FRCSGlasg', 'MBBS, FRCSEng', 'MBBS, FRCSI'
        ]
        
        self.cities = [
            'Mumbai', 'Delhi', 'Karachi', 'Dubai', 'London', 'New York', 'Ahmedabad', 
            'Pune', 'Bangalore', 'Chennai', 'Hyderabad', 'Kolkata', 'Jaipur', 'Lucknow',
            'Kanpur', 'Nagpur', 'Indore', 'Thane', 'Bhopal', 'Patna', 'Vadodara'
        ]
        
        self.countries = [
            'India', 'Pakistan', 'UAE', 'UK', 'USA', 'Canada', 'Australia', 'Germany',
            'France', 'Singapore', 'Malaysia', 'Saudi Arabia', 'Qatar', 'Kuwait'
        ]
        
        self.blood_types = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
        
        self.ailments = [
            'Fever', 'Headache', 'Cough', 'Cold', 'Back Pain', 'Joint Pain', 'Diabetes',
            'Hypertension', 'Asthma', 'Allergies', 'Digestive Issues', 'Skin Problems',
            'Eye Problems', 'Dental Issues', 'Respiratory Problems', 'Cardiac Issues'
        ]
        
        self.symptoms = [
            'Pain', 'Fever', 'Cough', 'Fatigue', 'Nausea', 'Dizziness', 'Swelling',
            'Rash', 'Itching', 'Bleeding', 'Difficulty breathing', 'Chest pain'
        ]
        
        self.diagnoses = [
            'Viral infection', 'Bacterial infection', 'Chronic disease', 'Acute condition',
            'Allergic reaction', 'Inflammatory condition', 'Metabolic disorder'
        ]
        
        self.prescriptions = [
            'Paracetamol 500mg', 'Ibuprofen 400mg', 'Amoxicillin 500mg', 'Omeprazole 20mg',
            'Cetirizine 10mg', 'Salbutamol inhaler', 'Metformin 500mg', 'Amlodipine 5mg'
        ]
        
        self.petition_categories = [
            'Health & Medical', 'Education', 'Social Welfare', 'Infrastructure', 'Security',
            'Environment', 'Transportation', 'Employment', 'Housing', 'Community Services'
        ]
        
        self.survey_topics = [
            'Healthcare Satisfaction', 'Community Health', 'Education Quality', 'Social Services',
            'Infrastructure Needs', 'Security Concerns', 'Environmental Issues', 'Transportation'
        ]
        
    def log_creation(self, item_type, details=""):
        """Log creation of items"""
        print(f"✅ Created {item_type}: {details}")
    
    def create_mock_its_users(self):
        """Create 120 users in MOCKITS with comprehensive details"""
        print("👥 Creating 120 users in MOCKITS...")
        
        # Calculate distribution
        num_aamils = 20  # 20 mozes
        num_coordinators = 20  # 1 per moze
        num_doctors = 30  # 30 doctors
        num_students = 40  # 40 students
        num_admins = 10  # 10 admins
        
        total_users = num_aamils + num_coordinators + num_doctors + num_students + num_admins
        
        print(f"📊 User Distribution:")
        print(f"   Aamils: {num_aamils}")
        print(f"   Coordinators: {num_coordinators}")
        print(f"   Doctors: {num_doctors}")
        print(f"   Students: {num_students}")
        print(f"   Admins: {num_admins}")
        print(f"   Total: {total_users}")
        
        user_counter = 1
        
        # Create Aamils (Moze Managers)
        for i in range(num_aamils):
            first_name = random.choice(self.first_names)
            last_name = random.choice(self.last_names)
            username = f"aamil{i+1:02d}"
            its_id = f"500000{2+i:02d}"
            
            user = User.objects.create_user(
                username=username,
                its_id=its_id,
                first_name=first_name,
                last_name=last_name,
                email=f"{username}@mockits.com",
                role='aamil',
                is_active=True
            )
            user.set_password('testpass123')
            user.save()
            
            self.created_users.append({
                'user': user,
                'role': 'aamil',
                'its_id': its_id
            })
            
            self.log_creation("Aamil User", f"{user.get_full_name()} ({username})")
            user_counter += 1
        
        # Create Moze Coordinators
        for i in range(num_coordinators):
            first_name = random.choice(self.first_names)
            last_name = random.choice(self.last_names)
            username = f"coordinator{i+1:02d}"
            its_id = f"500000{22+i:02d}"
            
            user = User.objects.create_user(
                username=username,
                its_id=its_id,
                first_name=first_name,
                last_name=last_name,
                email=f"{username}@mockits.com",
                role='moze_coordinator',
                is_active=True
            )
            user.set_password('testpass123')
            user.save()
            
            self.created_users.append({
                'user': user,
                'role': 'moze_coordinator',
                'its_id': its_id
            })
            
            self.log_creation("Coordinator User", f"{user.get_full_name()} ({username})")
            user_counter += 1
        
        # Create Doctors
        for i in range(num_doctors):
            first_name = random.choice(self.first_names)
            last_name = random.choice(self.last_names)
            username = f"doctor{i+1:02d}"
            its_id = f"500000{42+i:02d}"
            
            user = User.objects.create_user(
                username=username,
                its_id=its_id,
                first_name=first_name,
                last_name=last_name,
                email=f"{username}@mockits.com",
                role='doctor',
                is_active=True
            )
            user.set_password('testpass123')
            user.save()
            
            self.created_users.append({
                'user': user,
                'role': 'doctor',
                'its_id': its_id
            })
            
            self.log_creation("Doctor User", f"{user.get_full_name()} ({username})")
            user_counter += 1
        
        # Create Students
        for i in range(num_students):
            first_name = random.choice(self.first_names)
            last_name = random.choice(self.last_names)
            username = f"student{i+1:02d}"
            its_id = f"500000{72+i:03d}"
            
            user = User.objects.create_user(
                username=username,
                its_id=its_id,
                first_name=first_name,
                last_name=last_name,
                email=f"{username}@mockits.com",
                role='student',
                is_active=True
            )
            user.set_password('testpass123')
            user.save()
            
            self.created_users.append({
                'user': user,
                'role': 'student',
                'its_id': its_id
            })
            
            self.log_creation("Student User", f"{user.get_full_name()} ({username})")
            user_counter += 1
        
        # Create Admins
        for i in range(num_admins):
            first_name = random.choice(self.first_names)
            last_name = random.choice(self.last_names)
            username = f"admin{i+1:02d}"
            its_id = f"500000{112+i:03d}"
            
            user = User.objects.create_user(
                username=username,
                its_id=its_id,
                first_name=first_name,
                last_name=last_name,
                email=f"{username}@mockits.com",
                role='badri_mahal_admin',
                is_active=True
            )
            user.set_password('testpass123')
            user.save()
            
            self.created_users.append({
                'user': user,
                'role': 'badri_mahal_admin',
                'its_id': its_id
            })
            
            self.log_creation("Admin User", f"{user.get_full_name()} ({username})")
            user_counter += 1
        
        print(f"✅ Successfully created {len(self.created_users)} users in MOCKITS")
    
    def create_mozes_and_hospitals(self):
        """Create mozes and hospitals"""
        print("🏢 Creating mozes and hospitals...")
        
        # Get aamils for moze creation
        aamils = [u for u in self.created_users if u['role'] == 'aamil']
        coordinators = [u for u in self.created_users if u['role'] == 'moze_coordinator']
        
        # Create 20 mozes
        for i in range(20):
            city = random.choice(self.cities)
            country = random.choice(self.countries)
            
            moze = Moze.objects.create(
                name=f"Moze {chr(65 + i // 2)}{i % 2 + 1} - {city}",
                address=f"Address {i+1}, {city}, {country}",
                phone=f"+91{random.randint(6000000000, 9999999999)}",
                email=f"moze{i+1}@example.com",
                aamil=aamils[i] if i < len(aamils) else aamils[0],
                moze_coordinator=coordinators[i] if i < len(coordinators) else coordinators[0],
                capacity=random.randint(100, 500),
                is_active=True
            )
            
            self.created_mozes.append(moze)
            self.log_creation("Moze", f"{moze.name}")
        
        # Create hospitals
        hospital_names = [
            'City General Hospital', 'Central Medical Center', 'Community Health Hospital',
            'Regional Medical Center', 'Specialty Care Hospital', 'Emergency Care Center'
        ]
        
        for i, name in enumerate(hospital_names):
            city = random.choice(self.cities)
            country = random.choice(self.countries)
            
            hospital = Hospital.objects.create(
                name=f"{name} - {city}",
                address=f"Hospital Address {i+1}, {city}, {country}",
                phone=f"+91{random.randint(6000000000, 9999999999)}",
                email=f"hospital{i+1}@example.com",
                capacity=random.randint(100, 300),
                is_active=True
            )
            
            self.created_hospitals.append(hospital)
            self.log_creation("Hospital", f"{hospital.name}")
        
        print(f"✅ Created {len(self.created_mozes)} mozes and {len(self.created_hospitals)} hospitals")
    
    def create_medical_services(self):
        """Create medical services"""
        print("🏥 Creating medical services...")
        
        services = [
            {'name': 'General Consultation', 'category': 'consultation', 'duration': 30, 'cost': 200},
            {'name': 'Specialist Consultation', 'category': 'specialist', 'duration': 45, 'cost': 500},
            {'name': 'Health Check', 'category': 'preventive', 'duration': 60, 'cost': 800},
            {'name': 'Emergency Care', 'category': 'emergency', 'duration': 20, 'cost': 1000},
            {'name': 'Diagnostic Services', 'category': 'diagnostic', 'duration': 30, 'cost': 300},
            {'name': 'Treatment', 'category': 'treatment', 'duration': 45, 'cost': 600},
            {'name': 'Rehabilitation', 'category': 'rehabilitation', 'duration': 60, 'cost': 400},
            {'name': 'Mental Health', 'category': 'mental_health', 'duration': 60, 'cost': 700}
        ]
        
        created_services = []
        for service_data in services:
            service = MedicalService.objects.create(
                name=service_data['name'],
                description=f"Professional {service_data['name'].lower()} service",
                category=service_data['category'],
                duration_minutes=service_data['duration'],
                cost=Decimal(service_data['cost']),
                is_active=True
            )
            created_services.append(service)
            self.log_creation("Medical Service", f"{service.name}")
        
        print(f"✅ Created {len(created_services)} medical services")
        return created_services
    
    def create_doctors_and_patients(self):
        """Create doctors and patients"""
        print("👨‍⚕️ Creating doctors and patients...")
        
        # Get doctor users
        doctor_users = [u for u in self.created_users if u['role'] == 'doctor']
        student_users = [u for u in self.created_users if u['role'] == 'student']
        
        # Create Doctor Directory doctors
        for i, user_data in enumerate(doctor_users):
            doctor = Doctor.objects.create(
                user=user_data['user'],
                specialization=random.choice(self.specializations),
                qualification=random.choice(self.qualifications),
                experience_years=random.randint(5, 25),
                phone=f"+91{random.randint(6000000000, 9999999999)}",
                email=user_data['user'].email,
                address=f"Doctor Address {i+1}, {random.choice(self.cities)}",
                is_available=True
            )
            
            self.created_doctors.append({
                'user_data': user_data,
                'doctor_dir': doctor
            })
            self.log_creation("Doctor Directory Doctor", f"Dr. {doctor.user.get_full_name()}")
        
        # Create Mahal Shifa doctors
        for i, user_data in enumerate(doctor_users):
            mahal_doctor = MahalShifaDoctor.objects.create(
                user=user_data['user'],
                hospital=random.choice(self.created_hospitals),
                department='General Medicine',
                specialization=random.choice(self.specializations),
                qualification=random.choice(self.qualifications),
                experience_years=random.randint(5, 25),
                phone=f"+91{random.randint(6000000000, 9999999999)}",
                email=user_data['user'].email,
                is_available=True,
                consultation_fee=Decimal(random.randint(200, 800))
            )
            
            # Link to existing doctor directory entry
            for doc in self.created_doctors:
                if doc['user_data']['user'] == user_data['user']:
                    doc['mahal_doctor'] = mahal_doctor
                    break
            
            self.log_creation("Mahal Shifa Doctor", f"Dr. {mahal_doctor.user.get_full_name()}")
        
        # Create patients (from student users)
        for i, user_data in enumerate(student_users):
            # Doctor Directory patient
            patient_dir = Patient.objects.create(
                user_account=user_data['user'],
                full_name=user_data['user'].get_full_name(),
                date_of_birth=timezone.now().date() - timedelta(days=random.randint(6570, 25550)),
                gender=random.choice(['male', 'female']),
                phone_number=f"+91{random.randint(6000000000, 9999999999)}",
                email=user_data['user'].email,
                address=f"Patient Address {i+1}, {random.choice(self.cities)}",
                blood_type=random.choice(self.blood_types),
                allergies=random.choice(['None', 'Peanuts', 'Dust', 'Pollen', '']),
                medical_history=random.choice(['None', 'Diabetes', 'Hypertension', 'Asthma', '']),
                emergency_contact=f"Emergency Contact {i+1}",
                emergency_phone=f"+91{random.randint(6000000000, 9999999999)}"
            )
            
            # Mahal Shifa patient
            patient_mahal = MahalShifaPatient.objects.create(
                its_id=user_data['user'].its_id,
                first_name=user_data['user'].first_name,
                last_name=user_data['user'].last_name,
                date_of_birth=patient_dir.date_of_birth,
                gender=patient_dir.gender,
                phone_number=patient_dir.phone_number,
                email=user_data['user'].email,
                address=patient_dir.address,
                blood_group=patient_dir.blood_type,
                allergies=patient_dir.allergies,
                chronic_conditions=patient_dir.medical_history,
                emergency_contact_name=patient_dir.emergency_contact,
                emergency_contact_phone=patient_dir.emergency_phone,
                registered_moze=random.choice(self.created_mozes),
                is_active=True
            )
            
            self.created_patients.append({
                'user_data': user_data,
                'patient_dir': patient_dir,
                'patient_mahal': patient_mahal
            })
            
            self.log_creation("Patient", f"{patient_dir.full_name}")
        
        print(f"✅ Created {len(self.created_doctors)} doctors and {len(self.created_patients)} patients")
    
    def create_appointments(self):
        """Create appointments"""
        print("📅 Creating appointments...")
        
        # Generate appointment dates (next 90 days)
        start_date = timezone.now().date()
        appointment_dates = [start_date + timedelta(days=i) for i in range(90)]
        
        # Generate appointment times (9 AM to 6 PM)
        appointment_times = [
            timezone.datetime.strptime(f"{hour:02d}:00", "%H:%M").time()
            for hour in range(9, 19)
        ]
        
        statuses = ['scheduled', 'confirmed', 'completed', 'cancelled', 'no_show']
        appointment_types = ['regular', 'follow_up', 'urgent', 'emergency', 'screening', 'consultation']
        
        # Create 60 appointments (30 for each system)
        for i in range(60):
            # Randomly select doctor and patient
            doctor_data = random.choice(self.created_doctors)
            patient_data = random.choice(self.created_patients)
            
            # Random appointment details
            appointment_date = random.choice(appointment_dates)
            appointment_time = random.choice(appointment_times)
            status = random.choice(statuses)
            appointment_type = random.choice(appointment_types)
            
            # Create Doctor Directory appointment
            appointment_dir = DoctorAppointment.objects.create(
                doctor=doctor_data['doctor_dir'],
                patient=patient_data['patient_dir'],
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                duration_minutes=random.randint(15, 60),
                status=status,
                reason=f"Appointment reason {i+1}: {random.choice(self.ailments)}",
                notes=f"Appointment notes {i+1}: {random.choice(self.symptoms)}",
                created_by=doctor_data['user_data']['user']
            )
            
            # Create Mahal Shifa appointment
            appointment_mahal = MahalShifaAppointment.objects.create(
                doctor=doctor_data['mahal_doctor'],
                patient=patient_data['patient_mahal'],
                moze=patient_data['patient_mahal'].registered_moze,
                service=random.choice(MedicalService.objects.all()),
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                duration_minutes=random.randint(15, 60),
                reason=f"Mahal Shifa appointment reason {i+1}: {random.choice(self.ailments)}",
                symptoms=f"Symptoms: {random.choice(self.symptoms)}",
                notes=f"Mahal Shifa appointment notes {i+1}",
                status=status,
                appointment_type=appointment_type,
                booked_by=doctor_data['user_data']['user'],
                booking_method=random.choice(['online', 'phone', 'walk_in', 'staff'])
            )
            
            self.created_appointments.append({
                'doctor_dir': appointment_dir,
                'mahal_shifa': appointment_mahal
            })
            
            if i % 10 == 0:
                self.log_creation("Appointment Batch", f"Created {i+1} appointments")
        
        print(f"✅ Created {len(self.created_appointments)} appointments")
    
    def create_medical_records(self):
        """Create medical records"""
        print("📋 Creating medical records...")
        
        # Create medical records for each patient
        for patient_data in self.created_patients:
            # Create multiple medical records per patient
            for i in range(random.randint(1, 3)):
                medical_record = MedicalRecord.objects.create(
                    patient=patient_data['patient_mahal'],
                    doctor=random.choice([d['mahal_doctor'] for d in self.created_doctors]),
                    moze=patient_data['patient_mahal'].registered_moze,
                    consultation_date=timezone.now() - timedelta(days=random.randint(1, 365)),
                    chief_complaint=random.choice(self.ailments),
                    history_of_present_illness=f"Patient reports {random.choice(self.symptoms)} for {random.randint(1, 7)} days",
                    past_medical_history=patient_data['patient_dir'].medical_history,
                    family_history="No significant family history",
                    social_history="Patient leads a normal lifestyle",
                    physical_examination=f"General examination reveals {random.choice(self.symptoms)}",
                    diagnosis=random.choice(self.diagnoses),
                    differential_diagnosis=f"Consider {random.choice(self.diagnoses)}",
                    treatment_plan=f"Treatment plan includes {random.choice(self.prescriptions)}",
                    medications_prescribed=random.choice(self.prescriptions),
                    lab_tests_ordered=random.choice(['Blood test', 'X-ray', 'ECG', 'None']),
                    imaging_ordered=random.choice(['Chest X-ray', 'Abdominal ultrasound', 'None']),
                    referrals=random.choice(['Specialist consultation', 'None']),
                    follow_up_required=random.choice([True, False]),
                    follow_up_date=timezone.now().date() + timedelta(days=random.randint(7, 30)) if random.choice([True, False]) else None,
                    follow_up_instructions=f"Follow up in {random.randint(1, 4)} weeks",
                    patient_education=f"Patient advised to {random.choice(['rest', 'exercise', 'diet modification', 'medication compliance'])}",
                    doctor_notes=f"Patient responded well to treatment. {random.choice(['Continue current medication', 'Adjust dosage', 'Monitor progress'])}"
                )
                
                self.created_medical_records.append(medical_record)
        
        print(f"✅ Created {len(self.created_medical_records)} medical records")
    
    def create_araz_petitions(self):
        """Create araz petitions"""
        print("📝 Creating araz petitions...")
        
        # Create petition categories
        for category_name in self.petition_categories:
            category, created = PetitionCategory.objects.get_or_create(
                name=category_name,
                defaults={'description': f'Category for {category_name.lower()}'}
            )
        
        # Create petitions
        for i in range(50):
            petitioner = random.choice(self.created_users)
            moze = random.choice(self.created_mozes)
            category = random.choice(PetitionCategory.objects.all())
            
            petition = Petition.objects.create(
                title=f"Petition {i+1}: {random.choice(['Improve', 'Request', 'Address', 'Support'])} {random.choice(['Healthcare', 'Education', 'Infrastructure', 'Services'])}",
                description=f"This petition seeks to {random.choice(['improve', 'establish', 'enhance', 'support'])} {random.choice(['community services', 'healthcare facilities', 'educational programs', 'infrastructure development'])} in {moze.name}.",
                petitioner=petitioner['user'],
                moze=moze,
                category=category,
                priority=random.choice(['low', 'medium', 'high', 'urgent']),
                status=random.choice(['pending', 'under_review', 'approved', 'rejected', 'implemented']),
                target_signatures=random.randint(50, 500),
                current_signatures=random.randint(10, 200),
                is_active=True
            )
            
            self.created_petitions.append(petition)
            
            if i % 10 == 0:
                self.log_creation("Petition Batch", f"Created {i+1} petitions")
        
        print(f"✅ Created {len(self.created_petitions)} petitions")
    
    def create_surveys(self):
        """Create surveys with JSON questions"""
        print("📊 Creating surveys...")
        
        # Sample question structures
        sample_questions = [
            [
                {
                    "id": 1,
                    "type": "text",
                    "question": "What is your name?",
                    "required": True,
                    "options": []
                },
                {
                    "id": 2,
                    "type": "multiple_choice",
                    "question": "How satisfied are you with our services?",
                    "required": True,
                    "options": ["Very Satisfied", "Satisfied", "Neutral", "Dissatisfied", "Very Dissatisfied"]
                },
                {
                    "id": 3,
                    "type": "rating",
                    "question": "Rate our service quality (1-5)",
                    "required": True,
                    "options": ["1", "2", "3", "4", "5"]
                }
            ],
            [
                {
                    "id": 1,
                    "type": "text",
                    "question": "What improvements would you suggest?",
                    "required": False,
                    "options": []
                },
                {
                    "id": 2,
                    "type": "checkbox",
                    "question": "Which services have you used?",
                    "required": True,
                    "options": ["Medical Consultation", "Health Screening", "Emergency Care", "Follow-up"]
                },
                {
                    "id": 3,
                    "type": "yes_no",
                    "question": "Would you recommend our services to others?",
                    "required": True,
                    "options": ["Yes", "No"]
                }
            ]
        ]
        
        # Create surveys
        for i in range(20):
            creator = random.choice([u for u in self.created_users if u['role'] in ['aamil', 'moze_coordinator', 'badri_mahal_admin']])
            
            survey = Survey.objects.create(
                title=f"Survey {i+1}: {random.choice(self.survey_topics)}",
                description=f"This survey aims to gather feedback on {random.choice(self.survey_topics).lower()} in our community.",
                target_role=random.choice(['all', 'aamil', 'doctor', 'student']),
                questions=random.choice(sample_questions),
                creator=creator['user'],
                is_active=True,
                is_anonymous=random.choice([True, False]),
                allow_multiple_responses=random.choice([True, False]),
                show_results=random.choice([True, False]),
                start_date=timezone.now() - timedelta(days=random.randint(1, 30)),
                end_date=timezone.now() + timedelta(days=random.randint(30, 90))
            )
            
            self.created_surveys.append(survey)
            
            if i % 5 == 0:
                self.log_creation("Survey Batch", f"Created {i+1} surveys")
        
        print(f"✅ Created {len(self.created_surveys)} surveys")
    
    def create_photo_albums(self):
        """Create photo albums"""
        print("📸 Creating photo albums...")
        
        # Create photo albums
        for i in range(15):
            creator = random.choice(self.created_users)
            moze = random.choice(self.created_mozes)
            
            album = PhotoAlbum.objects.create(
                title=f"Album {i+1}: {random.choice(['Community Event', 'Health Camp', 'Educational Program', 'Social Gathering', 'Religious Ceremony'])}",
                description=f"Photos from {random.choice(['recent', 'annual', 'special', 'community'])} {random.choice(['event', 'program', 'celebration', 'gathering'])} in {moze.name}.",
                creator=creator['user'],
                moze=moze,
                is_public=random.choice([True, False]),
                is_active=True
            )
            
            self.created_albums.append(album)
            
            if i % 5 == 0:
                self.log_creation("Album Batch", f"Created {i+1} albums")
        
        print(f"✅ Created {len(self.created_albums)} photo albums")
    
    def create_evaluations(self):
        """Create evaluation forms"""
        print("📋 Creating evaluation forms...")
        
        # Create evaluation forms
        for i in range(10):
            creator = random.choice([u for u in self.created_users if u['role'] in ['aamil', 'moze_coordinator', 'badri_mahal_admin']])
            
            evaluation = EvaluationForm.objects.create(
                title=f"Evaluation {i+1}: {random.choice(['Program Assessment', 'Service Review', 'Performance Evaluation', 'Quality Check'])}",
                description=f"This evaluation form is designed to assess {random.choice(['program effectiveness', 'service quality', 'performance metrics', 'community satisfaction'])}.",
                creator=creator['user'],
                moze=random.choice(self.created_mozes),
                is_active=True,
                start_date=timezone.now().date() - timedelta(days=random.randint(1, 30)),
                end_date=timezone.now().date() + timedelta(days=random.randint(30, 90))
            )
            
            self.created_evaluations.append(evaluation)
        
        print(f"✅ Created {len(self.created_evaluations)} evaluation forms")
    
    def create_students(self):
        """Create student profiles"""
        print("🎓 Creating student profiles...")
        
        # Create courses
        courses = [
            'Islamic Studies', 'Arabic Language', 'Religious Education', 'Community Service',
            'Healthcare Management', 'Social Work', 'Religious Leadership', 'Islamic Finance'
        ]
        
        created_courses = []
        for course_name in courses:
            course, created = Course.objects.get_or_create(
                name=course_name,
                defaults={
                    'description': f'Course in {course_name}',
                    'duration_months': random.randint(6, 24),
                    'is_active': True
                }
            )
            created_courses.append(course)
        
        # Create student profiles
        student_users = [u for u in self.created_users if u['role'] == 'student']
        for i, user_data in enumerate(student_users):
            student = Student.objects.create(
                user=user_data['user'],
                course=random.choice(created_courses),
                enrollment_date=timezone.now().date() - timedelta(days=random.randint(30, 365)),
                graduation_date=timezone.now().date() + timedelta(days=random.randint(30, 730)) if random.choice([True, False]) else None,
                is_active=True,
                academic_status=random.choice(['enrolled', 'graduated', 'suspended', 'withdrawn'])
            )
            
            self.log_creation("Student Profile", f"{student.user.get_full_name()} - {student.course.name}")
        
        print(f"✅ Created {len(student_users)} student profiles")
    
    def generate_comprehensive_report(self):
        """Generate comprehensive data report"""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE DATA POPULATION REPORT")
        print("="*80)
        
        print(f"\n👥 USER STATISTICS:")
        print(f"   Total Users Created: {len(self.created_users)}")
        print(f"   Aamils: {len([u for u in self.created_users if u['role'] == 'aamil'])}")
        print(f"   Coordinators: {len([u for u in self.created_users if u['role'] == 'moze_coordinator'])}")
        print(f"   Doctors: {len([u for u in self.created_users if u['role'] == 'doctor'])}")
        print(f"   Students: {len([u for u in self.created_users if u['role'] == 'student'])}")
        print(f"   Admins: {len([u for u in self.created_users if u['role'] == 'badri_mahal_admin'])}")
        
        print(f"\n🏢 INFRASTRUCTURE:")
        print(f"   Mozes: {len(self.created_mozes)}")
        print(f"   Hospitals: {len(self.created_hospitals)}")
        
        print(f"\n👨‍⚕️ MEDICAL PROFESSIONALS:")
        print(f"   Doctor Directory Doctors: {len(self.created_doctors)}")
        print(f"   Mahal Shifa Doctors: {len([d for d in self.created_doctors if 'mahal_doctor' in d])}")
        
        print(f"\n👥 PATIENTS:")
        print(f"   Doctor Directory Patients: {len(self.created_patients)}")
        print(f"   Mahal Shifa Patients: {len([p for p in self.created_patients if 'patient_mahal' in p])}")
        
        print(f"\n📅 APPOINTMENTS:")
        print(f"   Total Appointments: {len(self.created_appointments)}")
        print(f"   Doctor Directory: {len([a for a in self.created_appointments if 'doctor_dir' in a])}")
        print(f"   Mahal Shifa: {len([a for a in self.created_appointments if 'mahal_shifa' in a])}")
        
        print(f"\n📋 MEDICAL RECORDS:")
        print(f"   Total Medical Records: {len(self.created_medical_records)}")
        
        print(f"\n📝 ARAZ PETITIONS:")
        print(f"   Total Petitions: {len(self.created_petitions)}")
        
        print(f"\n📊 SURVEYS:")
        print(f"   Total Surveys: {len(self.created_surveys)}")
        
        print(f"\n📸 PHOTO ALBUMS:")
        print(f"   Total Albums: {len(self.created_albums)}")
        
        print(f"\n📋 EVALUATIONS:")
        print(f"   Total Evaluation Forms: {len(self.created_evaluations)}")
        
        print(f"\n🎓 STUDENTS:")
        print(f"   Total Student Profiles: {len([u for u in self.created_users if u['role'] == 'student'])}")
        
        print(f"\n🔐 LOGIN CREDENTIALS:")
        print(f"   All users created with password: testpass123")
        print(f"   Username format: role + number (e.g., aamil01, doctor01, student01)")
        print(f"   Email format: username@mockits.com")
        
        print(f"\n✅ DATA POPULATION COMPLETED SUCCESSFULLY!")
        print("="*80)
    
    def run_comprehensive_population(self):
        """Run the complete data population process"""
        print("🚀 Starting comprehensive data population...")
        
        try:
            with transaction.atomic():
                # Create users in MOCKITS
                self.create_mock_its_users()
                
                # Create infrastructure
                self.create_mozes_and_hospitals()
                
                # Create medical services
                self.create_medical_services()
                
                # Create doctors and patients
                self.create_doctors_and_patients()
                
                # Create appointments
                self.create_appointments()
                
                # Create medical records
                self.create_medical_records()
                
                # Create araz petitions
                self.create_araz_petitions()
                
                # Create surveys
                self.create_surveys()
                
                # Create photo albums
                self.create_photo_albums()
                
                # Create evaluations
                self.create_evaluations()
                
                # Create students
                self.create_students()
                
                # Generate report
                self.generate_comprehensive_report()
                
        except Exception as e:
            print(f"❌ Data population failed with error: {str(e)}")
            import traceback
            traceback.print_exc()

def main():
    """Main function to run the data population"""
    print("🏥 COMPREHENSIVE DATA POPULATION FOR UMOOR SEHHAT")
    print("="*60)
    
    populator = ComprehensiveDataPopulator()
    populator.run_comprehensive_population()

if __name__ == "__main__":
    main()