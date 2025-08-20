#!/usr/bin/env python
"""
Generate Mock ITS Data and Complete Healthcare System Data

This script generates:
1. 1000 users with proper role distribution
2. 100 moze with aamils and coordinators
3. Medical records for all users
4. Araz (petitions)
5. Surveys and evaluations
6. 5 hospitals
7. 50 Mahal Shifa centers
8. Patient records linked to moze
"""

import os
import sys
import django
import random
from datetime import datetime, timedelta, date
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

# Import all models
from accounts.services import ITSService
from moze.models import Moze, MozeCoordinator
from doctordirectory.models import Doctor, Patient, MedicalService, PatientLog, DoctorSchedule
from mahalshifa.models import Hospital, Department, HospitalStaff
from araz.models import Petition, Document, PetitionStatus
from surveys.models import Survey, Question, Response, SurveySubmission
from evaluation.models import StudentEvaluation
from students.models import Student, Course, Enrollment
from photos.models import PhotoAlbum, Photo

User = get_user_model()


class MockDataGenerator:
    """Generate comprehensive mock data for the healthcare system"""
    
    def __init__(self):
        self.moze_list = []
        self.doctors = []
        self.hospitals = []
        self.mahal_shifas = []
        self.courses = []
        self.surveys = []
        
        # ITS ID ranges for different roles
        self.its_ranges = {
            'admin': range(10000001, 10000002),         # 1 admin
            'aamil': range(10000002, 10000102),         # 100 aamils (1 per moze)
            'coordinator': range(10000102, 10000202),   # 100 coordinators
            'doctor': range(10000202, 10000252),        # 50 doctors
            'student': range(10000252, 10000452),       # 200 students
            'patient': range(10000452, 10001002),       # 550 patients
        }
    
    @transaction.atomic
    def generate_all_data(self):
        """Generate all mock data"""
        print("Starting mock data generation...")
        
        # 1. Create Moze
        self.create_moze()
        
        # 2. Create Hospitals
        self.create_hospitals()
        
        # 3. Create Users with proper roles
        self.create_users()
        
        # 4. Create Medical Services
        self.create_medical_services()
        
        # 5. Create Courses for Students
        self.create_courses()
        
        # 6. Create Medical Records
        self.create_medical_records()
        
        # 7. Create Araz (Petitions)
        self.create_araz()
        
        # 8. Create Surveys
        self.create_surveys()
        
        # 9. Create Evaluations
        self.create_evaluations()
        
        # 10. Create Photo Albums
        self.create_photo_albums()
        
        print("\n✅ Mock data generation completed successfully!")
        self.print_summary()
    
    def create_moze(self):
        """Create 100 moze"""
        print("\n1. Creating Moze...")
        
        moze_names = [f"Moze {chr(65 + i // 4)}{i % 4 + 1}" for i in range(100)]
        regions = ['North', 'South', 'East', 'West', 'Central']
        
        for i, name in enumerate(moze_names):
            moze = Moze.objects.create(
                name=name,
                code=f"MZ{i+1:03d}",
                region=random.choice(regions),
                address=f"{random.randint(1, 999)} {name} Street, Mumbai",
                contact_number=f"+91{random.randint(7000000000, 9999999999)}",
                email=f"{name.lower().replace(' ', '')}@moze.com",
                description=f"Community center serving {name} area",
                established_date=date(2000 + i % 20, random.randint(1, 12), random.randint(1, 28)),
                is_active=True
            )
            self.moze_list.append(moze)
        
        print(f"  ✓ Created {len(self.moze_list)} moze")
    
    def create_hospitals(self):
        """Create 5 hospitals and 50 Mahal Shifa centers"""
        print("\n2. Creating Hospitals and Mahal Shifa...")
        
        # Create 5 main hospitals
        hospital_names = [
            "Saifee Hospital",
            "Burhani Hospital", 
            "Al-Shifa Medical Center",
            "Taher Memorial Hospital",
            "Syedna Hospital"
        ]
        
        for i, name in enumerate(hospital_names):
            hospital = Hospital.objects.create(
                name=name,
                address=f"{random.randint(1, 999)} Hospital Road, Mumbai",
                phone=f"+91{random.randint(2200000000, 2299999999)}",
                email=f"info@{name.lower().replace(' ', '')}.com",
                website=f"www.{name.lower().replace(' ', '')}.com",
                established_year=2000 + i * 3,
                bed_count=random.randint(100, 500),
                emergency_services=True,
                insurance_accepted=True,
                description=f"{name} - A leading healthcare facility",
                is_active=True
            )
            
            # Create departments
            dept_names = ['General Medicine', 'Surgery', 'Pediatrics', 'Gynecology', 'Orthopedics']
            for dept_name in dept_names:
                Department.objects.create(
                    hospital=hospital,
                    name=dept_name,
                    description=f"{dept_name} department at {name}",
                    head_doctor_name=f"Dr. {random.choice(['Ahmed', 'Ali', 'Hassan'])} {random.choice(['Khan', 'Sheikh'])}",
                    contact_number=f"+91{random.randint(7000000000, 9999999999)}",
                    is_active=True
                )
            
            self.hospitals.append(hospital)
        
        # Create 50 Mahal Shifa centers (distributed across moze)
        for i in range(50):
            moze = self.moze_list[i * 2]  # Assign to every other moze
            
            mahal_shifa = Hospital.objects.create(
                name=f"Mahal Shifa {moze.name}",
                address=f"Near {moze.name}, {moze.address}",
                phone=f"+91{random.randint(7000000000, 9999999999)}",
                email=f"mahalshifa.{moze.code.lower()}@healthcare.com",
                hospital_type='clinic',
                affiliated_moze=moze.name,
                established_year=2010 + i % 10,
                bed_count=random.randint(5, 20),
                emergency_services=random.choice([True, False]),
                description=f"Primary healthcare center serving {moze.name}",
                is_active=True
            )
            
            self.mahal_shifas.append(mahal_shifa)
        
        print(f"  ✓ Created {len(self.hospitals)} hospitals")
        print(f"  ✓ Created {len(self.mahal_shifas)} Mahal Shifa centers")
    
    def create_users(self):
        """Create users with proper role distribution"""
        print("\n3. Creating Users...")
        
        # Clear existing student/coordinator ITS IDs
        ITSService.STUDENT_ITS_IDS.clear()
        ITSService.COORDINATOR_ITS_IDS.clear()
        
        # Create Admin
        admin_its = '10000001'
        self._create_user(admin_its, 'admin')
        
        # Create Aamils (1 per moze)
        for i, moze in enumerate(self.moze_list):
            its_id = f"{10000002 + i:08d}"
            user = self._create_user(its_id, 'aamil')
            if user:
                moze.aamil = user
                moze.save()
        
        # Create Moze Coordinators
        coordinator_its_ids = []
        for i in range(100):
            its_id = f"{10000102 + i:08d}"
            coordinator_its_ids.append(its_id)
            user = self._create_user(its_id, 'coordinator')
            if user and i < len(self.moze_list):
                # Create MozeCoordinator entry
                MozeCoordinator.objects.create(
                    user=user,
                    moze=self.moze_list[i],
                    appointment_date=date.today() - timedelta(days=random.randint(30, 365)),
                    is_active=True
                )
        
        # Add coordinator ITS IDs to the service
        ITSService.add_coordinator_its_ids(coordinator_its_ids)
        
        # Create Doctors
        for i in range(50):
            its_id = f"{10000202 + i:08d}"
            user = self._create_user(its_id, 'doctor')
            if user:
                # Create doctor profile
                doctor = Doctor.objects.create(
                    user=user,
                    name=user.get_full_name(),
                    its_id=its_id,
                    specialty=random.choice([
                        'General Medicine', 'Cardiology', 'Pediatrics',
                        'Orthopedics', 'Gynecology', 'Dermatology'
                    ]),
                    qualification=user.qualification or 'MBBS, MD',
                    experience_years=random.randint(5, 25),
                    consultation_fee=Decimal(random.randint(200, 1000)),
                    phone=user.mobile_number or f"+91{random.randint(7000000000, 9999999999)}",
                    email=user.email,
                    address=user.address or "Mumbai",
                    languages_spoken='English, Hindi, Gujarati',
                    bio=f"Experienced {user.qualification} with expertise in patient care",
                    assigned_moze=random.choice(self.moze_list),
                    is_verified=True,
                    is_available=True
                )
                self.doctors.append(doctor)
        
        # Create Students
        student_its_ids = []
        for i in range(200):
            its_id = f"{10000252 + i:08d}"
            student_its_ids.append(its_id)
            user = self._create_user(its_id, 'student')
            if user:
                # Create student profile
                Student.objects.create(
                    user=user,
                    its_id=its_id,
                    moze=random.choice(self.moze_list),
                    enrollment_date=date.today() - timedelta(days=random.randint(30, 730)),
                    current_year=random.randint(1, 4),
                    total_years=4,
                    status='active'
                )
        
        # Add student ITS IDs to the service
        ITSService.add_student_its_ids(student_its_ids)
        
        # Create Patients
        for i in range(550):
            its_id = f"{10000452 + i:08d}"
            user = self._create_user(its_id, 'patient')
            if user:
                # Create patient profile
                Patient.objects.create(
                    user=user,
                    date_of_birth=date(
                        random.randint(1950, 2005),
                        random.randint(1, 12),
                        random.randint(1, 28)
                    ),
                    gender=user.gender or random.choice(['male', 'female']),
                    blood_group=random.choice(['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']),
                    emergency_contact=f"+91{random.randint(7000000000, 9999999999)}",
                    medical_history=random.choice([
                        'No significant medical history',
                        'Diabetes Type 2',
                        'Hypertension',
                        'Asthma',
                        'Allergies - Dust, Pollen'
                    ]),
                    allergies=random.choice(['None', 'Penicillin', 'Sulfa drugs', 'Peanuts']),
                    current_medications=random.choice(['None', 'Metformin', 'Amlodipine', 'Aspirin'])
                )
        
        print(f"  ✓ Created {User.objects.count()} users")
    
    def _create_user(self, its_id, expected_role):
        """Create a single user with ITS authentication"""
        try:
            # Authenticate with ITS (mock)
            auth_result = ITSService.authenticate_user(its_id, 'pass1234')
            if not auth_result:
                return None
            
            user_data = auth_result.get('user_data', {})
            role = auth_result.get('role')
            
            # Create or update user
            user, created = User.objects.update_or_create(
                its_id=its_id,
                defaults={
                    'username': its_id,
                    'first_name': user_data.get('first_name', ''),
                    'last_name': user_data.get('last_name', ''),
                    'email': user_data.get('email', ''),
                    'role': role,
                    'arabic_full_name': user_data.get('arabic_full_name', ''),
                    'prefix': user_data.get('prefix', ''),
                    'age': user_data.get('age'),
                    'gender': user_data.get('gender'),
                    'marital_status': user_data.get('marital_status'),
                    'misaq': user_data.get('misaq', ''),
                    'occupation': user_data.get('occupation', ''),
                    'qualification': user_data.get('qualification', ''),
                    'idara': user_data.get('idara', ''),
                    'category': user_data.get('category', ''),
                    'organization': user_data.get('organization', ''),
                    'mobile_number': user_data.get('mobile_number', ''),
                    'whatsapp_number': user_data.get('whatsapp_number', ''),
                    'address': user_data.get('address', ''),
                    'jamaat': user_data.get('jamaat', ''),
                    'jamiaat': user_data.get('jamiaat', ''),
                    'nationality': user_data.get('nationality', ''),
                    'vatan': user_data.get('vatan', ''),
                    'city': user_data.get('city', ''),
                    'country': user_data.get('country', ''),
                    'hifz_sanad': user_data.get('hifz_sanad', ''),
                    'profile_photo': user_data.get('photograph', ''),
                    'is_active': True
                }
            )
            
            if created:
                user.set_password('pass1234')
                user.save()
            
            return user
            
        except Exception as e:
            print(f"    Error creating user {its_id}: {e}")
            return None
    
    def create_medical_services(self):
        """Create medical services for doctors"""
        print("\n4. Creating Medical Services...")
        
        service_types = [
            ('General Consultation', 30, 200),
            ('Follow-up Visit', 20, 150),
            ('Emergency Consultation', 45, 500),
            ('Health Checkup', 60, 800),
            ('Vaccination', 15, 100),
            ('Minor Procedure', 45, 1000),
        ]
        
        for doctor in self.doctors:
            # Each doctor offers 2-4 services
            num_services = random.randint(2, 4)
            selected_services = random.sample(service_types, num_services)
            
            for service_name, duration, base_price in selected_services:
                MedicalService.objects.create(
                    doctor=doctor,
                    name=service_name,
                    description=f"{service_name} by {doctor.name}",
                    duration_minutes=duration,
                    price=Decimal(base_price + random.randint(-50, 150)),
                    is_available=True
                )
        
        print(f"  ✓ Created {MedicalService.objects.count()} medical services")
    
    def create_courses(self):
        """Create courses for students"""
        print("\n5. Creating Courses...")
        
        course_names = [
            'Basic Health Education',
            'First Aid Training',
            'Nutrition and Wellness',
            'Community Health',
            'Mental Health Awareness',
            'Disease Prevention',
            'Healthcare Ethics',
            'Patient Care Basics'
        ]
        
        for name in course_names:
            course = Course.objects.create(
                name=name,
                code=f"HC{random.randint(100, 999)}",
                description=f"Course on {name.lower()}",
                credits=random.randint(2, 4),
                duration_weeks=random.randint(8, 16),
                instructor_name=f"Dr. {random.choice(['Ahmed', 'Fatima', 'Hassan'])} {random.choice(['Ali', 'Khan'])}",
                max_students=random.randint(30, 60),
                is_active=True
            )
            self.courses.append(course)
            
            # Enroll random students
            students = Student.objects.all()
            enrolled_students = random.sample(list(students), min(len(students), random.randint(20, 40)))
            
            for student in enrolled_students:
                Enrollment.objects.create(
                    student=student,
                    course=course,
                    enrollment_date=date.today() - timedelta(days=random.randint(30, 180)),
                    status='active'
                )
        
        print(f"  ✓ Created {len(self.courses)} courses")
    
    def create_medical_records(self):
        """Create medical records and patient logs"""
        print("\n6. Creating Medical Records...")
        
        ailments = [
            'Common Cold', 'Fever', 'Headache', 'Body Pain',
            'Cough', 'Sore Throat', 'Stomach Pain', 'Allergic Reaction',
            'Skin Rash', 'Minor Injury', 'Hypertension', 'Diabetes Checkup'
        ]
        
        # Get all patients
        patients = Patient.objects.all()
        
        for patient in patients[:200]:  # Create records for first 200 patients
            # Create 1-3 medical records per patient
            num_records = random.randint(1, 3)
            
            for _ in range(num_records):
                doctor = random.choice(self.doctors)
                
                PatientLog.objects.create(
                    patient_its_id=patient.user.its_id if patient.user else f"{random.randint(10000000, 99999999)}",
                    patient_name=patient.user.get_full_name() if patient.user else "Unknown",
                    ailment=random.choice(ailments),
                    symptoms=f"Patient presents with {random.choice(['mild', 'moderate', 'severe'])} symptoms",
                    diagnosis=f"Diagnosed with {random.choice(ailments)}",
                    prescription=random.choice([
                        'Paracetamol 500mg twice daily for 3 days',
                        'Amoxicillin 500mg thrice daily for 5 days',
                        'Rest and plenty of fluids',
                        'Antihistamine once daily for 7 days'
                    ]),
                    follow_up_required=random.choice([True, False]),
                    follow_up_date=date.today() + timedelta(days=random.randint(7, 30)) if random.choice([True, False]) else None,
                    visit_type=random.choice(['consultation', 'follow_up', 'emergency', 'screening']),
                    moze=random.choice(self.moze_list),
                    seen_by=doctor
                )
        
        print(f"  ✓ Created {PatientLog.objects.count()} patient medical records")
    
    def create_araz(self):
        """Create Araz (petitions)"""
        print("\n7. Creating Araz (Petitions)...")
        
        petition_types = [
            'Medical Financial Assistance',
            'Surgery Support Request',
            'Medicine Assistance',
            'Medical Equipment Request',
            'Emergency Medical Help',
            'Chronic Disease Support'
        ]
        
        # Create petitions from random users
        users = User.objects.filter(role__in=['student', 'patient'])[:100]
        
        for user in users:
            petition = Petition.objects.create(
                petitioner=user,
                moze=random.choice(self.moze_list),
                subject=random.choice(petition_types),
                description=f"Request for {random.choice(petition_types).lower()}. "
                          f"Patient requires assistance due to financial constraints.",
                amount_requested=Decimal(random.randint(5000, 50000)),
                category=random.choice(['medical', 'education', 'financial', 'other']),
                priority=random.choice(['low', 'medium', 'high', 'urgent']),
                supporting_documents="Medical reports attached"
            )
            
            # Create status update
            PetitionStatus.objects.create(
                petition=petition,
                status=random.choice(['pending', 'under_review', 'approved', 'rejected']),
                updated_by=User.objects.filter(role='aamil').first(),
                comments=random.choice([
                    'Application received and under review',
                    'Approved for partial assistance',
                    'Required additional documentation',
                    'Forwarded to committee for approval'
                ])
            )
        
        print(f"  ✓ Created {Petition.objects.count()} petitions")
    
    def create_surveys(self):
        """Create surveys and responses"""
        print("\n8. Creating Surveys...")
        
        survey_titles = [
            'Patient Satisfaction Survey',
            'Healthcare Quality Assessment',
            'Community Health Needs Survey',
            'Medical Camp Feedback',
            'Hospital Services Evaluation'
        ]
        
        for title in survey_titles:
            survey = Survey.objects.create(
                title=title,
                description=f"Survey to assess {title.lower()}",
                created_by=User.objects.filter(role='aamil').first(),
                start_date=date.today() - timedelta(days=random.randint(30, 90)),
                end_date=date.today() + timedelta(days=random.randint(30, 90)),
                is_active=True,
                is_anonymous=random.choice([True, False])
            )
            
            # Create questions
            question_texts = [
                'How satisfied are you with our services?',
                'Would you recommend our services to others?',
                'How was your experience with the staff?',
                'Rate the cleanliness of our facilities',
                'Any suggestions for improvement?'
            ]
            
            questions = []
            for i, q_text in enumerate(question_texts):
                question = Question.objects.create(
                    survey=survey,
                    text=q_text,
                    question_type='rating' if i < 4 else 'text',
                    order=i + 1,
                    is_required=True
                )
                questions.append(question)
            
            # Create responses from random users
            respondents = User.objects.filter(role__in=['student', 'patient'])[:50]
            
            for user in random.sample(list(respondents), 20):
                submission = SurveySubmission.objects.create(
                    survey=survey,
                    submitted_by=user,
                    submitted_at=timezone.now() - timedelta(days=random.randint(1, 30))
                )
                
                for question in questions:
                    if question.question_type == 'rating':
                        answer = str(random.randint(1, 5))
                    else:
                        answer = random.choice([
                            'Excellent service',
                            'Good experience overall',
                            'Need improvement in waiting time',
                            'Very satisfied with the treatment'
                        ])
                    
                    Response.objects.create(
                        submission=submission,
                        question=question,
                        answer=answer
                    )
            
            self.surveys.append(survey)
        
        print(f"  ✓ Created {len(self.surveys)} surveys with responses")
    
    def create_evaluations(self):
        """Create student evaluations"""
        print("\n9. Creating Evaluations...")
        
        students = Student.objects.all()[:50]
        evaluators = User.objects.filter(role__in=['aamil', 'moze_coordinator'])
        
        for student in students:
            StudentEvaluation.objects.create(
                student=student,
                evaluator=random.choice(list(evaluators)),
                evaluation_date=date.today() - timedelta(days=random.randint(30, 180)),
                academic_performance=random.randint(60, 100),
                attendance_percentage=random.randint(70, 100),
                behavior_rating=random.randint(3, 5),
                participation_score=random.randint(60, 100),
                overall_grade=random.choice(['A', 'B', 'C', 'D']),
                strengths='Good academic performance, regular attendance',
                areas_of_improvement='Can improve in class participation',
                comments=f'Student shows {random.choice(["excellent", "good", "satisfactory"])} progress',
                semester=random.choice(['Fall 2023', 'Spring 2024', 'Fall 2024'])
            )
        
        print(f"  ✓ Created {StudentEvaluation.objects.count()} student evaluations")
    
    def create_photo_albums(self):
        """Create photo albums"""
        print("\n10. Creating Photo Albums...")
        
        album_titles = [
            'Medical Camp 2024',
            'Health Awareness Program',
            'Community Health Workshop',
            'Annual Health Checkup Drive',
            'Vaccination Campaign'
        ]
        
        for title in album_titles:
            album = PhotoAlbum.objects.create(
                title=title,
                description=f"Photos from {title}",
                event_date=date.today() - timedelta(days=random.randint(30, 180)),
                location=random.choice(['Mumbai', 'Pune', 'Ahmedabad', 'Surat']),
                created_by=User.objects.filter(role='aamil').first(),
                is_public=True
            )
            
            # Add random moze to album
            album.moze.add(*random.sample(self.moze_list, random.randint(1, 3)))
            
            # Create photos
            for i in range(random.randint(5, 15)):
                Photo.objects.create(
                    album=album,
                    caption=f"Event photo {i+1}",
                    uploaded_by=album.created_by,
                    image_url=f"https://picsum.photos/800/600?random={album.id}{i}",
                    order=i
                )
        
        print(f"  ✓ Created {PhotoAlbum.objects.count()} photo albums")
    
    def print_summary(self):
        """Print summary of generated data"""
        print("\n" + "="*60)
        print("MOCK DATA GENERATION SUMMARY")
        print("="*60)
        
        print(f"\nUsers:")
        for role, display in User.ROLE_CHOICES:
            count = User.objects.filter(role=role).count()
            print(f"  - {display}: {count}")
        print(f"  - Total: {User.objects.count()}")
        
        print(f"\nHealthcare Facilities:")
        print(f"  - Hospitals: {Hospital.objects.filter(hospital_type='hospital').count()}")
        print(f"  - Mahal Shifa Centers: {Hospital.objects.filter(hospital_type='clinic').count()}")
        print(f"  - Departments: {Department.objects.count()}")
        
        print(f"\nMedical Data:")
        print(f"  - Doctors: {Doctor.objects.count()}")
        print(f"  - Patients: {Patient.objects.count()}")
        print(f"  - Medical Services: {MedicalService.objects.count()}")
        print(f"  - Patient Records: {PatientLog.objects.count()}")
        
        print(f"\nEducation:")
        print(f"  - Students: {Student.objects.count()}")
        print(f"  - Courses: {Course.objects.count()}")
        print(f"  - Enrollments: {Enrollment.objects.count()}")
        print(f"  - Evaluations: {StudentEvaluation.objects.count()}")
        
        print(f"\nCommunity:")
        print(f"  - Moze: {Moze.objects.count()}")
        print(f"  - Petitions (Araz): {Petition.objects.count()}")
        print(f"  - Surveys: {Survey.objects.count()}")
        print(f"  - Survey Responses: {Response.objects.count()}")
        print(f"  - Photo Albums: {PhotoAlbum.objects.count()}")
        
        print("\n" + "="*60)
        print("Login Examples:")
        print("="*60)
        print("All users have password: pass1234")
        print("\nAdmin: 10000001")
        print("Aamil: 10000002 - 10000101")
        print("Coordinator: 10000102 - 10000201")
        print("Doctor: 10000202 - 10000251")
        print("Student: 10000252 - 10000451")
        print("Patient: 10000452 - 10001001")


if __name__ == '__main__':
    print("="*60)
    print("UMOOR SEHHAT - MOCK DATA GENERATOR")
    print("="*60)
    
    confirm = input("\nThis will generate mock data. Continue? (yes/no): ")
    
    if confirm.lower() == 'yes':
        generator = MockDataGenerator()
        generator.generate_all_data()
    else:
        print("Data generation cancelled.")