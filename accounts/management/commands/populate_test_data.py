from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta, date, time
from decimal import Decimal
import random

from accounts.models import UserProfile
from moze.models import Moze, MozeSettings, MozeComment
from doctordirectory.models import (
    Doctor, Patient, Appointment, MedicalRecord, Prescription,
    LabTest, VitalSigns, PatientLog, MedicalService
)
from surveys.models import Survey, SurveyResponse, SurveyReminder
from photos.models import PhotoAlbum, Photo

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate the database with comprehensive test data'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Starting comprehensive data population...')
        
        with transaction.atomic():
            self.create_users()
            self.create_moze_data()
            self.create_medical_data()
            self.create_survey_data()
            self.create_photo_data()
        
        self.stdout.write(self.style.SUCCESS('✅ Data population completed successfully!'))

    def create_users(self):
        self.stdout.write('👥 Creating users...')
        
        # Create admin user
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_user(
                username='admin',
                email='admin@umoor-sehhat.com',
                password='admin123',
                first_name='Admin',
                last_name='User',
                role='badri_mahal_admin',
                its_id='00000000',
                phone_number='+919876543210',
                is_active=True,
                is_staff=True,
                is_superuser=True
            )
            UserProfile.objects.create(user=admin)

        # Sample names for realistic data
        first_names = [
            'Aisha', 'Ahmed', 'Fatima', 'Hassan', 'Zainab', 'Ali', 'Khadija', 'Omar',
            'Maryam', 'Ibrahim', 'Nadia', 'Yusuf', 'Amina', 'Mustafa', 'Salma', 'Khalil',
            'Layla', 'Tariq', 'Safiya', 'Rashid', 'Zahra', 'Iqbal', 'Ruqayya', 'Bilal'
        ]
        
        last_names = [
            'Sheikh', 'Khan', 'Bharuchi', 'Khorakiwala', 'Najmuddin', 'Shaikh', 'Merchant',
            'Lokhandwala', 'Rangwala', 'Jamali', 'Mohammedi', 'Patel', 'Saiyed', 'Rajkotwala',
            'Kapasi', 'Husain', 'Tinwala', 'Najmi', 'Momin', 'Kothari'
        ]

        roles = ['aamil', 'moze_coordinator', 'doctor', 'student']
        
        for i in range(1, 60):  # Create 59 additional users
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            role = random.choice(roles)
            its_id = f"{random.randint(10000000, 99999999)}"
            
            user = User.objects.create_user(
                username=f"{first_name.lower().replace(' ', '').replace('.', '')}{i}",
                email=f"{first_name.lower().replace(' ', '').replace('.', '')}{i}@example.com",
                password='password123',
                first_name=first_name,
                last_name=last_name,
                role=role,
                its_id=its_id,
                phone_number=f"+91{random.randint(7000000000, 9999999999)}",
                is_active=True
            )
            UserProfile.objects.create(user=user)

    def create_moze_data(self):
        self.stdout.write('🏥 Creating Moze data...')
        
        moze_names = [
            'Saifee Mahal - Mumbai Central',
            'Najmuddin Mahal - Dongri',
            'Husaini Mahal - Mohammed Ali Road',
            'Tayyebi Mahal - Bhendi Bazaar',
            'Fatemi Mahal - Crawford Market',
            'Qutbi Mahal - Mazgaon',
            'Alavi Mahal - Pydhonie',
            'Bohra Mahal - Fort'
        ]
        
        areas = ['Mumbai Central', 'Dongri', 'Mohammed Ali Road', 'Bhendi Bazaar', 
                'Crawford Market', 'Mazgaon', 'Pydhonie', 'Fort']
        
        for i, name in enumerate(moze_names):
            area = areas[i]
            aamil = User.objects.filter(role='aamil').order_by('?').first()
            coordinator = User.objects.filter(role='moze_coordinator').order_by('?').first()
            
            moze = Moze.objects.create(
                name=name,
                location=f"{area}, Mumbai",
                address=f"Full address of {name}, {area}, Mumbai",
                aamil=aamil,
                moze_coordinator=coordinator,
                capacity=random.randint(50, 500),
                contact_phone=f"+91{random.randint(7000000000, 9999999999)}",
                contact_email=f"{name.lower().replace(' ', '').replace('-', '')}@moze.com",
                is_active=True
            )
            
            # Create Moze settings
            MozeSettings.objects.create(
                moze=moze,
                allow_walk_ins=random.choice([True, False]),
                appointment_duration=random.choice([30, 45, 60]),
                working_days={'monday': True, 'tuesday': True, 'wednesday': True, 
                            'thursday': True, 'friday': True, 'saturday': True, 'sunday': False},
                emergency_contact=f"+91{random.randint(9000000000, 9999999999)}",
                special_instructions="Special instructions for this Moze center"
            )
            
            # Create comments
            for j in range(random.randint(3, 8)):
                commenter = User.objects.order_by('?').first()
                MozeComment.objects.create(
                    moze=moze,
                    author=commenter,
                    content=f"Great facilities and services at {name}. Very helpful staff."
                )

    def create_medical_data(self):
        self.stdout.write('👨‍⚕️ Creating medical data...')
        
        specialties = ['Cardiology', 'Pediatrics', 'Dermatology', 'Orthopedics', 
                      'General Medicine', 'Psychiatry', 'Gynecology', 'Neurology']
        
        # Create doctors
        doctor_users = User.objects.filter(role='doctor')[:12]
        for i, doctor_user in enumerate(doctor_users):
            specialty = specialties[i % len(specialties)]
            moze = Moze.objects.order_by('?').first()
            
            doctor = Doctor.objects.create(
                user=doctor_user,
                name=f"Dr. {doctor_user.first_name} {doctor_user.last_name}",
                specialty=specialty,
                qualification="MBBS, MD",
                experience_years=random.randint(5, 25),
                consultation_fee=Decimal(str(random.randint(300, 1500))),
                moze=moze,
                is_available=True
            )
            
            # Create medical services
            services = ['Consultation', 'Follow-up', 'Diagnostic', 'Procedure']
            for service_name in services:
                MedicalService.objects.create(
                    doctor=doctor,
                    name=f"{specialty} {service_name}",
                    service_type='consultation',
                    description=f"{service_name} for {specialty}",
                    duration_minutes=random.choice([30, 45, 60]),
                    fee=Decimal(str(random.randint(200, 1000))),
                    is_active=True
                )
        
        # Create patients
        student_users = User.objects.filter(role='student')[:14]
        for patient_user in student_users:
            Patient.objects.create(
                user=patient_user,
                blood_group=random.choice(['A+', 'B+', 'AB+', 'O+', 'A-', 'B-', 'AB-', 'O-']),
                emergency_contact_name=f"{patient_user.first_name} Family",
                emergency_contact_phone=f"+91{random.randint(9000000000, 9999999999)}",
                medical_history="General medical history notes",
                allergies="No known allergies",
                chronic_conditions="None reported"
            )
        
        # Create appointments
        doctors = Doctor.objects.all()
        patients = Patient.objects.all()
        
        for i in range(random.randint(50, 100)):
            doctor = random.choice(doctors)
            patient = random.choice(patients)
            service = doctor.services.first()
            
            # Random date within last 30 days or next 30 days
            days_offset = random.randint(-30, 30)
            appointment_date = date.today() + timedelta(days=days_offset)
            appointment_time = time(random.randint(9, 17), random.choice([0, 30]))
            
            appointment = Appointment.objects.create(
                doctor=doctor,
                patient=patient,
                service=service,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                reason_for_visit=random.choice([
                    'Regular checkup', 'Follow-up consultation', 'Health screening',
                    'Vaccination', 'Diagnostic consultation'
                ]),
                status=random.choice(['pending', 'confirmed', 'completed', 'cancelled'])
            )
            
            # Create medical records for completed appointments
            if appointment.status == 'completed' and days_offset < 0:
                MedicalRecord.objects.create(
                    appointment=appointment,
                    patient=patient,
                    doctor=doctor,
                    diagnosis="Diagnosis notes",
                    symptoms="Patient symptoms",
                    treatment_plan="Treatment recommendations",
                    notes="Additional medical notes",
                    follow_up_required=random.choice([True, False])
                )
        
        # Create patient logs
        for i in range(random.randint(30, 60)):
            patient = random.choice(patients)
            doctor = random.choice(doctors)
            moze = random.choice(list(Moze.objects.all()))
            
            PatientLog.objects.create(
                patient_its_id=patient.user.its_id,
                patient_name=patient.user.get_full_name(),
                ailment=random.choice(['Fever', 'Headache', 'Cough', 'Back pain', 'Fatigue']),
                visit_type=random.choice(['consultation', 'follow_up', 'emergency', 'screening']),
                symptoms="Patient reported symptoms",
                diagnosis="Medical diagnosis",
                prescription="Prescribed medications",
                seen_by=doctor,
                moze=moze,
                timestamp=timezone.now() - timedelta(days=random.randint(1, 30))
            )

    def create_survey_data(self):
        self.stdout.write('📋 Creating survey data...')
        
        admin_user = User.objects.filter(role='badri_mahal_admin').first()
        
        surveys_data = [
            {
                'title': 'Community Health Assessment',
                'description': 'A comprehensive survey about community health needs and preferences.',
                'target_role': 'all',
                'questions': [
                    {'question': 'How would you rate the overall health services in your area?', 'type': 'rating'},
                    {'question': 'What health services do you need most?', 'type': 'text'},
                    {'question': 'How often do you visit health facilities?', 'type': 'choice'}
                ]
            },
            {
                'title': 'Moze Facilities Feedback',
                'description': 'Feedback on Moze facilities and services.',
                'target_role': 'aamil',
                'questions': [
                    {'question': 'How satisfied are you with the Moze facilities?', 'type': 'rating'},
                    {'question': 'What improvements would you suggest?', 'type': 'text'}
                ]
            },
            {
                'title': 'Student Academic Survey',
                'description': 'Survey about academic experience and needs.',
                'target_role': 'student',
                'questions': [
                    {'question': 'How is your academic progress?', 'type': 'choice'},
                    {'question': 'What support do you need?', 'type': 'text'}
                ]
            }
        ]
        
        for survey_data in surveys_data:
            survey = Survey.objects.create(
                title=survey_data['title'],
                description=survey_data['description'],
                created_by=admin_user,
                start_date=date.today() - timedelta(days=10),
                end_date=date.today() + timedelta(days=20),
                target_role=survey_data['target_role'],
                questions=survey_data['questions'],
                is_active=True,
                is_anonymous=False
            )
            
            # Create responses
            target_users = User.objects.filter(role=survey_data['target_role']) if survey_data['target_role'] != 'all' else User.objects.all()
            for user in target_users[:random.randint(5, min(15, target_users.count()))]:
                SurveyResponse.objects.create(
                    survey=survey,
                    respondent=user,
                    answers={'q1': 'Response answer', 'q2': 'Another response'},
                    completion_time=random.randint(120, 600),
                    is_complete=True,
                    created_at=timezone.now() - timedelta(days=random.randint(1, 8))
                )

    def create_photo_data(self):
        self.stdout.write('📸 Creating photo data...')
        
        albums_data = [
            {'name': 'Community Events', 'description': 'Photos from various community gatherings'},
            {'name': 'Religious Ceremonies', 'description': 'Religious events and ceremonies'},
            {'name': 'Health Camps', 'description': 'Medical camps and health initiatives'},
            {'name': 'Educational Programs', 'description': 'Educational activities and workshops'}
        ]
        
        for album_data in albums_data:
            moze = Moze.objects.order_by('?').first()
            album = PhotoAlbum.objects.create(
                name=album_data['name'],
                description=album_data['description'],
                moze=moze,
                created_by=User.objects.order_by('?').first()
            )
            
            # Create photos for each album
            for i in range(random.randint(5, 12)):
                photo = Photo.objects.create(
                    album=album,
                    title=f"Photo {i+1} - {album_data['name']}",
                    description=f"Description for photo {i+1}",
                    uploaded_by=User.objects.order_by('?').first(),
                    moze=moze
                )
                
                # Set a cover photo for the album
                if i == 0:
                    album.cover_photo = photo
                    album.save()

        self.stdout.write('✅ All test data created successfully!')