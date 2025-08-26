#!/usr/bin/env python
"""
Enhanced Mock Data Generator for Umoor Sehhat System
====================================================

Features:
- Modern Python practices with type hints and dataclasses
- Progress tracking with rich progress bars
- Realistic data generation using Faker
- Comprehensive error handling and logging
- Configurable data volumes
- Better relationship management
- Performance optimizations with bulk operations
- Appointment system integration
- Photo and media file generation
- Advanced analytics and reporting data

Author: AI Assistant
Version: 2.0.0
"""

import os
import sys
import django
import random
import logging
from datetime import datetime, timedelta, date, time
from decimal import Decimal
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
import json
import uuid
from io import BytesIO

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

# Django imports
from django.contrib.auth import get_user_model
from django.db import transaction, connection
from django.utils import timezone
from django.core.files.base import ContentFile
from django.core.management.color import make_style

# Third-party imports for enhanced data generation
try:
    from faker import Faker
    from PIL import Image, ImageDraw, ImageFont
    from rich.console import Console
    from rich.progress import Progress, TaskID, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.table import Table
    from rich.panel import Panel
    ENHANCED_FEATURES = True
except ImportError:
    print("Installing required packages for enhanced features...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "faker", "pillow", "rich"])
    from faker import Faker
    from PIL import Image, ImageDraw, ImageFont
    from rich.console import Console
    from rich.progress import Progress, TaskID, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.table import Table
    from rich.panel import Panel
    ENHANCED_FEATURES = True

# Import all models
from accounts.services import ITSService
from moze.models import Moze
from doctordirectory.models import Doctor, Patient, MedicalService, PatientLog, DoctorSchedule
from mahalshifa.models import Hospital, Department, HospitalStaff
from araz.models import Petition, PetitionStatus
from surveys.models import Survey, SurveyResponse
from evaluation.models import Evaluation, EvaluationCriteria
from students.models import Student, Course, Enrollment
from photos.models import PhotoAlbum, Photo
from appointments.models import Appointment, TimeSlot, AppointmentLog, AppointmentReminder

User = get_user_model()

# Initialize Faker with available locales for diverse data
fake = Faker(['en_US', 'ar_SA', 'hi_IN'])
console = Console()
style = make_style()


@dataclass
class GenerationConfig:
    """Configuration for mock data generation"""
    # User counts
    admin_count: int = 1
    aamil_count: int = 100
    coordinator_count: int = 100
    doctor_count: int = 50
    student_count: int = 200
    patient_count: int = 550
    
    # Infrastructure counts
    moze_count: int = 100
    hospital_count: int = 5
    department_per_hospital: int = 5
    
    # Content counts
    course_count: int = 15
    survey_count: int = 10
    petition_count: int = 500
    appointment_count: int = 1000
    medical_record_count: int = 800
    photo_album_count: int = 20
    photos_per_album: int = 10
    
    # Data generation settings
    generate_photos: bool = True
    generate_appointments: bool = True
    generate_analytics: bool = True
    use_realistic_names: bool = True
    create_sample_files: bool = True
    
    # Performance settings
    bulk_create_batch_size: int = 100
    use_bulk_operations: bool = True


@dataclass
class GenerationStats:
    """Track generation statistics"""
    users_created: int = 0
    appointments_created: int = 0
    medical_records_created: int = 0
    photos_created: int = 0
    errors: List[str] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    @property
    def duration(self) -> Optional[timedelta]:
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None


class EnhancedMockDataGenerator:
    """Enhanced mock data generator with modern features"""
    
    def __init__(self, config: GenerationConfig = None):
        self.config = config or GenerationConfig()
        self.stats = GenerationStats()
        
        # Storage for created objects
        self.users: Dict[str, List[User]] = {
            'admin': [],
            'aamil': [],
            'moze_coordinator': [],
            'doctor': [],
            'student': [],
            'patient': []
        }
        
        self.moze_list: List[Moze] = []
        self.hospital_list: List[Hospital] = []
        self.doctor_objects: List[Doctor] = []
        self.patient_objects: List[Patient] = []
        self.courses: List[Course] = []
        self.photo_albums: List[PhotoAlbum] = []
        
        # Setup logging
        self._setup_logging()
        
        # Data pools for realistic generation
        self._initialize_data_pools()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('mock_data_generation.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _initialize_data_pools(self):
        """Initialize realistic data pools"""
        self.cities = [
            'Mumbai', 'Karachi', 'Houston', 'London', 'Dubai', 'Nairobi', 'Sydney',
            'Toronto', 'Dar es Salaam', 'Cairo', 'Istanbul', 'Jakarta', 'Delhi',
            'Lahore', 'Dhaka', 'Kuala Lumpur', 'Singapore', 'Bangkok', 'Manila'
        ]
        
        self.countries = [
            'India', 'Pakistan', 'USA', 'UK', 'UAE', 'Kenya', 'Australia',
            'Canada', 'Tanzania', 'Egypt', 'Turkey', 'Indonesia', 'Bangladesh',
            'Malaysia', 'Singapore', 'Thailand', 'Philippines'
        ]
        
        self.medical_specialties = [
            'General Medicine', 'Pediatrics', 'Cardiology', 'Orthopedics', 'Gynecology',
            'Dermatology', 'ENT', 'Ophthalmology', 'Psychiatry', 'Dentistry',
            'Neurology', 'Oncology', 'Radiology', 'Anesthesiology', 'Pathology',
            'Emergency Medicine', 'Family Medicine', 'Internal Medicine', 'Surgery'
        ]
        
        self.medical_conditions = [
            'Hypertension', 'Diabetes Type 2', 'Asthma', 'Arthritis', 'Migraine',
            'Allergies', 'Lower Back Pain', 'Anxiety Disorder', 'Depression',
            'Insomnia', 'GERD', 'Hypothyroidism', 'Osteoporosis', 'Chronic Fatigue',
            'Fibromyalgia', 'IBS', 'Sleep Apnea', 'High Cholesterol'
        ]
        
        self.symptoms = [
            'Fever', 'Persistent Cough', 'Severe Headache', 'Chronic Fatigue',
            'Nausea and Vomiting', 'Dizziness', 'Chest Pain', 'Shortness of Breath',
            'Joint Pain', 'Skin Rash', 'Abdominal Pain', 'Muscle Weakness',
            'Vision Problems', 'Hearing Loss', 'Memory Issues'
        ]
        
        self.course_subjects = [
            'Quran Studies', 'Arabic Language', 'Islamic History', 'Fiqh', 'Hadith Studies',
            'Islamic Philosophy', 'Comparative Religion', 'Islamic Finance', 'Dawah Methodology',
            'Islamic Psychology', 'Community Leadership', 'Interfaith Dialogue',
            'Islamic Art and Culture', 'Modern Islamic Thought', 'Islamic Ethics'
        ]
    
    def _create_realistic_user_data(self, role: str) -> Dict[str, Any]:
        """Generate realistic user data based on role"""
        profile = fake.profile()
        
        # Generate culturally appropriate names
        if random.choice([True, False]):
            # Arabic/Islamic names
            first_names = ['Ahmed', 'Ali', 'Omar', 'Hassan', 'Fatima', 'Aisha', 'Khadija', 'Mariam']
            last_names = ['Al-Rashid', 'Al-Mahmud', 'Al-Hassan', 'Khan', 'Sheikh', 'Patel', 'Ahmad']
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
        else:
            first_name = fake.first_name()
            last_name = fake.last_name()
        
        return {
            'first_name': first_name,
            'last_name': last_name,
            'email': f"{first_name.lower()}.{last_name.lower()}@{fake.domain_name()}",
            'arabic_full_name': fake.name() if random.choice([True, False]) else '',
            'prefix': random.choice(['Dr.', 'Mr.', 'Mrs.', 'Ms.', '']),
            'age': fake.random_int(min=18, max=80),
            'gender': random.choice(['male', 'female']),
            'marital_status': random.choice(['single', 'married', 'divorced', 'widowed']),
            'misaq': random.choice(['yes', 'no', 'pending']),
            'occupation': fake.job(),
            'qualification': fake.random_element(['Bachelor', 'Master', 'PhD', 'Diploma', 'Certificate']),
            'idara': fake.company(),
            'category': random.choice(['A', 'B', 'C']),
            'organization': fake.company(),
            'mobile_number': fake.phone_number()[:15],
            'whatsapp_number': fake.phone_number()[:15],
            'address': fake.address()[:200],
            'jamaat': fake.city(),
            'jamiaat': fake.city(),
            'nationality': fake.country(),
            'vatan': fake.country(),
            'city': random.choice(self.cities),
            'country': random.choice(self.countries),
            'hifz_sanad': random.choice(['yes', 'no', 'partial']),
        }
    
    def _create_user(self, its_id: str, role: str, progress_task: TaskID = None) -> Optional[User]:
        """Create a user with enhanced error handling"""
        try:
            # Check if user already exists
            if User.objects.filter(its_id=its_id).exists():
                self.logger.info(f"User {its_id} already exists")
                return User.objects.get(its_id=its_id)
            
            # Generate realistic user data
            user_data = self._create_realistic_user_data(role)
            
            # Create user
            user = User.objects.create(
                its_id=its_id,
                username=its_id,
                role=role,
                is_active=True,
                **user_data
            )
            user.set_password('pass1234')
            user.save()
            
            self.stats.users_created += 1
            self.users[role].append(user)
            
            if progress_task:
                console.print(f"✓ Created {role}: {user.get_full_name()} ({its_id})", style="green")
            
            return user
            
        except Exception as e:
            error_msg = f"Error creating user {its_id}: {str(e)}"
            self.logger.error(error_msg)
            self.stats.errors.append(error_msg)
            return None
    
    def _generate_sample_image(self, width: int = 400, height: int = 300, text: str = "Sample") -> ContentFile:
        """Generate a sample image file"""
        img = Image.new('RGB', (width, height), color=(random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)))
        draw = ImageDraw.Draw(img)
        
        # Add text
        try:
            font = ImageFont.load_default()
            text_width, text_height = draw.textsize(text, font=font)
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            draw.text((x, y), text, fill=(255, 255, 255), font=font)
        except:
            draw.text((50, height//2), text, fill=(255, 255, 255))
        
        # Save to BytesIO
        img_io = BytesIO()
        img.save(img_io, format='JPEG', quality=85)
        img_io.seek(0)
        
        return ContentFile(img_io.getvalue(), name=f"{text.lower().replace(' ', '_')}.jpg")
    
    def create_admin_users(self, progress: Progress, task: TaskID):
        """Create admin users"""
        console.print("\n[bold blue]Creating Admin Users...[/bold blue]")
        
        for i in range(self.config.admin_count):
            its_id = f"{10000001 + i:08d}"
            user = self._create_user(its_id, 'admin', task)
            if user:
                user.is_staff = True
                user.is_superuser = True
                user.save()
            progress.advance(task)
    
    def create_moze_with_aamils(self, progress: Progress, task: TaskID):
        """Create Moze with Aamils using bulk operations"""
        console.print("\n[bold blue]Creating Moze with Aamils...[/bold blue]")
        
        # Create Aamils first
        aamils = []
        for i in range(self.config.aamil_count):
            its_id = f"{10000002 + i:08d}"
            user = self._create_user(its_id, 'aamil', task)
            if user:
                aamils.append(user)
            progress.advance(task, 0.5)
        
        # Create Moze objects
        moze_objects = []
        for i, aamil in enumerate(aamils):
            city = random.choice(self.cities)
            moze = Moze(
                name=f"{city} Moze {i+1:03d}",
                location=f"Area {i+1}, {city}",
                aamil=aamil,
                established_date=fake.date_between(start_date='-10y', end_date='today'),
                is_active=True,
                capacity=fake.random_int(min=50, max=300),
                contact_phone=fake.phone_number()[:15],
                contact_email=f"moze{i+1}@{fake.domain_name()}"
            )
            moze_objects.append(moze)
            progress.advance(task, 0.5)
        
        # Bulk create Moze
        if self.config.use_bulk_operations:
            Moze.objects.bulk_create(moze_objects, batch_size=self.config.bulk_create_batch_size)
            self.moze_list = list(Moze.objects.all().order_by('id'))
        else:
            for moze in moze_objects:
                moze.save()
                self.moze_list.append(moze)
    
    def create_coordinators(self, progress: Progress, task: TaskID):
        """Create Moze Coordinators"""
        console.print("\n[bold blue]Creating Moze Coordinators...[/bold blue]")
        
        coordinator_its_ids = []
        coordinators = []
        
        for i in range(self.config.coordinator_count):
            its_id = f"{10000102 + i:08d}"
            coordinator_its_ids.append(its_id)
            user = self._create_user(its_id, 'moze_coordinator', task)
            
            if user and i < len(self.moze_list):
                # Assign coordinator to moze
                moze = self.moze_list[i]
                moze.moze_coordinator = user
                moze.save()
                coordinators.append(user)
            
            progress.advance(task)
        
        # Add coordinator ITS IDs to the service
        try:
            ITSService.add_coordinator_its_ids(coordinator_its_ids)
        except Exception as e:
            self.logger.warning(f"Could not add coordinator ITS IDs to service: {e}")
    
    def create_doctors_and_services(self, progress: Progress, task: TaskID):
        """Create doctors with medical services and schedules"""
        console.print("\n[bold blue]Creating Doctors and Medical Services...[/bold blue]")
        
        doctors = []
        medical_services = []
        schedules = []
        
        for i in range(self.config.doctor_count):
            its_id = f"{10000202 + i:08d}"
            user = self._create_user(its_id, 'doctor', task)
            
            if user:
                specialty = random.choice(self.medical_specialties)
                doctor = Doctor(
                    user=user,
                    name=user.get_full_name(),
                    its_id=its_id,
                    specialty=specialty,
                    qualification=f"MBBS, MD ({specialty})",
                    experience_years=fake.random_int(min=2, max=30),
                    consultation_fee=Decimal(fake.random_int(min=100, max=800)),
                    is_available=True,
                    is_verified=True,
                    assigned_moze=random.choice(self.moze_list) if self.moze_list else None,
                    languages_spoken=fake.random_element([
                        "English, Urdu, Gujarati",
                        "English, Arabic, Hindi",
                        "English, Urdu, Hindi, Gujarati",
                        "English, Arabic, Urdu"
                    ])
                )
                doctors.append(doctor)
                
                # Create medical services for this doctor
                for j in range(fake.random_int(min=2, max=6)):
                    service = MedicalService(
                        doctor=None,  # Will be set after doctor is saved
                        name=f"{specialty} {fake.random_element(['Consultation', 'Examination', 'Treatment', 'Follow-up', 'Screening'])}",
                        description=fake.text(max_nb_chars=200),
                        price=Decimal(fake.random_int(min=50, max=500)),
                        duration_minutes=fake.random_element([15, 30, 45, 60, 90])
                    )
                    medical_services.append((service, len(doctors) - 1))  # Store with doctor index
                
                # Create schedule for next 60 days
                for day_offset in range(60):
                    schedule_date = date.today() + timedelta(days=day_offset)
                    # Skip some weekends and random days
                    if schedule_date.weekday() < 5 and random.random() > 0.15:
                        schedule = DoctorSchedule(
                            doctor=None,  # Will be set after doctor is saved
                            date=schedule_date,
                            start_time=time(9, 0),  # Fixed start time
                            end_time=time(17, 0),   # Fixed end time
                            is_available=True,
                            max_patients=fake.random_int(min=8, max=25)
                        )
                        schedules.append((schedule, len(doctors) - 1))
            
            progress.advance(task)
        
        # Bulk create doctors
        if self.config.use_bulk_operations:
            Doctor.objects.bulk_create(doctors, batch_size=self.config.bulk_create_batch_size)
            self.doctor_objects = list(Doctor.objects.all().order_by('id'))
            
            # Set doctor references for services and schedules
            services_to_create = []
            for service, doctor_idx in medical_services:
                if doctor_idx < len(self.doctor_objects):
                    service.doctor = self.doctor_objects[doctor_idx]
                    services_to_create.append(service)
            
            schedules_to_create = []
            for schedule, doctor_idx in schedules:
                if doctor_idx < len(self.doctor_objects):
                    schedule.doctor = self.doctor_objects[doctor_idx]
                    schedules_to_create.append(schedule)
            
            MedicalService.objects.bulk_create(services_to_create, batch_size=self.config.bulk_create_batch_size)
            DoctorSchedule.objects.bulk_create(schedules_to_create, batch_size=self.config.bulk_create_batch_size)
        else:
            for doctor in doctors:
                doctor.save()
                self.doctor_objects.append(doctor)
    
    def create_students_and_courses(self, progress: Progress, task: TaskID):
        """Create students, courses, and enrollments"""
        console.print("\n[bold blue]Creating Students and Courses...[/bold blue]")
        
        # Create courses first
        courses = []
        for i, subject in enumerate(self.course_subjects):
            course = Course(
                name=f"{subject} - Level {fake.random_element(['I', 'II', 'III'])}",
                code=f"CRS{i+1:03d}",
                credits=fake.random_int(min=2, max=6),
                level=fake.random_element(['beginner', 'intermediate', 'advanced']),
                instructor=random.choice(self.users['aamil']) if self.users['aamil'] else None,
                description=fake.text(max_nb_chars=300)
            )
            courses.append(course)
        
        Course.objects.bulk_create(courses, batch_size=self.config.bulk_create_batch_size)
        self.courses = list(Course.objects.all().order_by('id'))
        
        # Add student ITS IDs to service
        student_its_ids = []
        for i in range(self.config.student_count):
            student_its_ids.append(f"{10000252 + i:08d}")
        
        try:
            ITSService.add_student_its_ids(student_its_ids)
        except Exception as e:
            self.logger.warning(f"Could not add student ITS IDs to service: {e}")
        
        # Create students
        students = []
        enrollments = []
        
        for i in range(self.config.student_count):
            its_id = student_its_ids[i]
            user = self._create_user(its_id, 'student', task)
            
            if user:
                enrollment_date = fake.date_between(start_date='-4y', end_date='today')
                student = Student(
                    user=user,
                    student_id=f"STD{i+1:06d}",
                    academic_level=fake.random_element(['undergraduate', 'postgraduate', 'doctorate']),
                    enrollment_status=fake.random_element(['active', 'graduated', 'suspended']),
                    enrollment_date=enrollment_date,
                    expected_graduation=enrollment_date + timedelta(days=fake.random_int(min=365, max=1825))
                )
                students.append(student)
                
                # Create enrollments for random courses
                selected_courses = random.sample(self.courses, min(fake.random_int(min=3, max=8), len(self.courses)))
                for course in selected_courses:
                    enrollment = Enrollment(
                        student=None,  # Will be set after student is saved
                        course=course,
                        status=fake.random_element(['enrolled', 'completed', 'dropped']),
                        grade=fake.random_element(['A', 'B', 'C', 'D', 'F', '']) if random.random() > 0.3 else '',
                        enrolled_date=enrollment_date
                    )
                    enrollments.append((enrollment, len(students) - 1))
            
            progress.advance(task)
        
        # Bulk create students and enrollments
        if self.config.use_bulk_operations:
            Student.objects.bulk_create(students, batch_size=self.config.bulk_create_batch_size)
            student_objects = list(Student.objects.all().order_by('id'))
            
            enrollments_to_create = []
            for enrollment, student_idx in enrollments:
                if student_idx < len(student_objects):
                    enrollment.student = student_objects[student_idx]
                    enrollments_to_create.append(enrollment)
            
            Enrollment.objects.bulk_create(enrollments_to_create, batch_size=self.config.bulk_create_batch_size)
    
    def create_patients(self, progress: Progress, task: TaskID):
        """Create patient profiles"""
        console.print("\n[bold blue]Creating Patients...[/bold blue]")
        
        blood_groups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
        patients = []
        
        for i in range(self.config.patient_count):
            its_id = f"{10000452 + i:08d}"
            user = self._create_user(its_id, 'patient', task)
            
            if user:
                patient = Patient(
                    user=user,
                    date_of_birth=fake.date_of_birth(minimum_age=1, maximum_age=90),
                    gender=fake.random_element(['male', 'female']),
                    blood_group=random.choice(blood_groups),
                    emergency_contact=fake.phone_number()[:15],
                    medical_history=random.choice(self.medical_conditions) if random.random() > 0.4 else '',
                    allergies=fake.random_element(['None', 'Peanuts', 'Shellfish', 'Dust', 'Pollen', 'Latex', 'Medications']),
                    current_medications=fake.random_element(['None', 'Aspirin', 'Metformin', 'Lisinopril', 'Atorvastatin']) if random.random() > 0.6 else ''
                )
                patients.append(patient)
            
            progress.advance(task)
        
        # Bulk create patients
        if self.config.use_bulk_operations:
            Patient.objects.bulk_create(patients, batch_size=self.config.bulk_create_batch_size)
            self.patient_objects = list(Patient.objects.all().order_by('id'))
        else:
            for patient in patients:
                patient.save()
                self.patient_objects.append(patient)
    
    def create_hospitals_and_departments(self, progress: Progress, task: TaskID):
        """Create hospitals with departments and staff"""
        console.print("\n[bold blue]Creating Hospitals and Departments...[/bold blue]")
        
        hospital_types = ['general', 'specialty', 'clinic', 'emergency', 'rehabilitation']
        hospitals = []
        departments = []
        staff_assignments = []
        
        for i in range(self.config.hospital_count):
            city = random.choice(self.cities)
            hospital = Hospital(
                name=f"{fake.company()} {fake.random_element(['Medical Center', 'Hospital', 'Clinic', 'Healthcare'])}",
                address=fake.address()[:200],
                phone=fake.phone_number()[:15],
                email=f"hospital{i+1}@{fake.domain_name()}",
                hospital_type=random.choice(hospital_types),
                total_beds=fake.random_int(min=20, max=500),
                available_beds=fake.random_int(min=5, max=100),
                emergency_beds=fake.random_int(min=2, max=25),
                icu_beds=fake.random_int(min=2, max=20),
                is_active=True,
                is_emergency_capable=fake.boolean(chance_of_getting_true=70),
                has_pharmacy=fake.boolean(chance_of_getting_true=80)
            )
            hospitals.append(hospital)
            
            # Create departments for this hospital
            dept_names = ['Emergency', 'Outpatient', 'Inpatient', 'Surgery', 'Pediatrics', 'Cardiology', 'Radiology']
            for j, dept_name in enumerate(random.sample(dept_names, min(self.config.department_per_hospital, len(dept_names)))):
                department = Department(
                    hospital=None,  # Will be set after hospital is saved
                    name=dept_name,
                    description=f"{dept_name} department providing specialized medical services",
                    floor_number=str(fake.random_int(min=1, max=5)),
                    phone_extension=str(fake.random_int(min=100, max=999)),
                    is_active=True
                )
                departments.append((department, len(hospitals) - 1))
            
            progress.advance(task)
        
        # Bulk create hospitals and departments
        if self.config.use_bulk_operations:
            Hospital.objects.bulk_create(hospitals, batch_size=self.config.bulk_create_batch_size)
            self.hospital_list = list(Hospital.objects.all().order_by('id'))
            
            # Create departments
            departments_to_create = []
            for department, hospital_idx in departments:
                if hospital_idx < len(self.hospital_list):
                    department.hospital = self.hospital_list[hospital_idx]
                    departments_to_create.append(department)
            
            Department.objects.bulk_create(departments_to_create, batch_size=self.config.bulk_create_batch_size)
            
            # Assign some doctors as hospital staff (ensuring no duplicates due to OneToOneField)
            all_departments = list(Department.objects.all())
            staff_to_create = []
            assigned_users = set()  # Track assigned users to avoid duplicates
            
            for hospital in self.hospital_list:
                hospital_departments = [d for d in all_departments if d.hospital == hospital]
                if hospital_departments and self.doctor_objects:
                    # Get available doctors (not already assigned)
                    available_doctors = [d for d in self.doctor_objects if d.user and d.user.id not in assigned_users]
                    
                    if available_doctors:
                        num_to_assign = min(fake.random_int(min=2, max=5), len(available_doctors))
                        selected_doctors = random.sample(available_doctors, num_to_assign)
                        
                        for j, doctor in enumerate(selected_doctors):
                            staff = HospitalStaff(
                                user=doctor.user,
                                hospital=hospital,
                                department=random.choice(hospital_departments),
                                staff_type='other',  # Using 'other' since 'doctor' is not in choices
                                employee_id=f"EMP{hospital.id:03d}{j+1:03d}",
                                shift=fake.random_element(['morning', 'evening', 'night', 'rotating']),
                                is_active=True,
                                hire_date=fake.date_between(start_date='-5y', end_date='today')
                            )
                            staff_to_create.append(staff)
                            assigned_users.add(doctor.user.id)  # Mark user as assigned
            
            if staff_to_create:
                HospitalStaff.objects.bulk_create(staff_to_create, batch_size=self.config.bulk_create_batch_size)
    
    def create_appointments(self, progress: Progress, task: TaskID):
        """Create comprehensive appointment system data"""
        if not self.config.generate_appointments:
            return
            
        console.print("\n[bold blue]Creating Appointments and Related Data...[/bold blue]")
        
        appointments = []
        appointment_logs = []
        appointment_reminders = []
        
        # Create time slots first
        slots = []
        for doctor in self.doctor_objects[:20]:  # Limit to first 20 doctors for performance
            schedules = DoctorSchedule.objects.filter(doctor=doctor, date__gte=date.today())[:30]
            for schedule in schedules:
                # Create time slots throughout the day
                current_time = datetime.combine(schedule.date, schedule.start_time)
                end_time = datetime.combine(schedule.date, schedule.end_time)
                
                while current_time < end_time:
                    slot = TimeSlot(
                        doctor=doctor,
                        date=schedule.date,
                        start_time=current_time.time(),
                        end_time=(current_time + timedelta(minutes=30)).time(),
                        is_available=fake.boolean(chance_of_getting_true=60),
                        max_appointments=1
                    )
                    slots.append(slot)
                    current_time += timedelta(minutes=30)
        
        TimeSlot.objects.bulk_create(slots[:500], batch_size=self.config.bulk_create_batch_size)
        created_slots = list(TimeSlot.objects.all()[:500])
        
        # Create appointments
        appointment_statuses = ['pending', 'confirmed', 'completed', 'cancelled', 'no_show']
        appointment_types = ['consultation', 'follow_up', 'emergency', 'screening']
        
        for i in range(min(self.config.appointment_count, len(created_slots), len(self.patient_objects))):
            slot = created_slots[i % len(created_slots)]
            patient = self.patient_objects[i % len(self.patient_objects)]
            
            appointment = Appointment(
                patient=patient,
                doctor=slot.doctor,
                time_slot=slot,
                appointment_date=slot.date,
                appointment_time=slot.start_time,
                appointment_type=random.choice(appointment_types),
                status=random.choice(appointment_statuses),
                reason_for_visit=random.choice(self.symptoms),
                chief_complaint=random.choice(self.symptoms),
                notes=fake.text(max_nb_chars=200) if random.random() > 0.5 else '',
                consultation_fee=slot.doctor.consultation_fee if slot.doctor else Decimal('100.00'),
                booked_by=patient.user if patient.user else None,
                follow_up_required=fake.boolean(chance_of_getting_true=30)
            )
            appointments.append(appointment)
            
            # Create appointment logs
            if random.random() > 0.3:
                log = AppointmentLog(
                    appointment=None,  # Will be set after appointment is saved
                    action=fake.random_element(['created', 'confirmed', 'completed', 'cancelled']),
                    notes=fake.text(max_nb_chars=200),
                    performed_by=slot.doctor.user if slot.doctor and slot.doctor.user else patient.user
                )
                appointment_logs.append((log, len(appointments) - 1))
            
            # Create appointment reminders
            if random.random() > 0.4:
                reminder = AppointmentReminder(
                    appointment=None,  # Will be set after appointment is saved
                    reminder_type=fake.random_element(['sms', 'email', 'whatsapp']),
                    scheduled_for=fake.date_time_between(start_date='-30d', end_date='+30d', tzinfo=timezone.get_current_timezone()),
                    is_sent=fake.boolean(chance_of_getting_true=60),
                    status='sent' if fake.boolean(chance_of_getting_true=60) else 'pending'
                )
                appointment_reminders.append((reminder, len(appointments) - 1))
            
            progress.advance(task)
        
        # Bulk create appointments and related data
        if self.config.use_bulk_operations:
            Appointment.objects.bulk_create(appointments, batch_size=self.config.bulk_create_batch_size)
            created_appointments = list(Appointment.objects.all().order_by('id'))
            
            # Create logs and reminders
            logs_to_create = []
            for log, appointment_idx in appointment_logs:
                if appointment_idx < len(created_appointments):
                    log.appointment = created_appointments[appointment_idx]
                    logs_to_create.append(log)
            
            reminders_to_create = []
            for reminder, appointment_idx in appointment_reminders:
                if appointment_idx < len(created_appointments):
                    reminder.appointment = created_appointments[appointment_idx]
                    reminders_to_create.append(reminder)
            
            AppointmentLog.objects.bulk_create(logs_to_create, batch_size=self.config.bulk_create_batch_size)
            AppointmentReminder.objects.bulk_create(reminders_to_create, batch_size=self.config.bulk_create_batch_size)
            
            self.stats.appointments_created = len(appointments)
    
    def create_medical_records(self, progress: Progress, task: TaskID):
        """Create comprehensive medical records"""
        console.print("\n[bold blue]Creating Medical Records...[/bold blue]")
        
        medical_logs = []
        record_count = 0
        
        # Select patients for medical records
        patients_sample = random.sample(
            self.patient_objects, 
            min(self.config.medical_record_count // 3, len(self.patient_objects))
        )
        
        for patient in patients_sample:
            # Create 1-5 medical records per patient
            num_records = fake.random_int(min=1, max=5)
            
            for _ in range(num_records):
                doctor = random.choice(self.doctor_objects) if self.doctor_objects else None
                moze = random.choice(self.moze_list) if self.moze_list else None
                
                if doctor and moze and patient.user:
                    # Generate realistic medical data
                    primary_symptom = random.choice(self.symptoms)
                    related_symptoms = random.sample(self.symptoms, fake.random_int(min=1, max=3))
                    condition = random.choice(self.medical_conditions)
                    
                    log = PatientLog(
                        patient_its_id=patient.user.its_id,
                        patient_name=patient.user.get_full_name(),
                        ailment=condition,
                        symptoms=', '.join([primary_symptom] + related_symptoms),
                        diagnosis=f"Diagnosed with {condition}. {fake.sentence()} Vital signs: {self._generate_vital_signs()}",
                        prescription=self._generate_prescription(),
                        follow_up_required=fake.boolean(chance_of_getting_true=40),
                        follow_up_date=fake.date_between(start_date='today', end_date='+90d') if fake.boolean(chance_of_getting_true=40) else None,
                        visit_type=fake.random_element(['consultation', 'follow_up', 'emergency', 'screening']),
                        moze=moze,
                        seen_by=doctor
                    )
                    medical_logs.append(log)
                    record_count += 1
            
            progress.advance(task)
        
        # Bulk create medical records
        if self.config.use_bulk_operations:
            PatientLog.objects.bulk_create(medical_logs, batch_size=self.config.bulk_create_batch_size)
        else:
            for log in medical_logs:
                log.save()
        
        self.stats.medical_records_created = record_count
        console.print(f"✓ Created {record_count} medical records")
    
    def _generate_prescription(self) -> str:
        """Generate realistic prescription text"""
        medications = [
            'Paracetamol 500mg', 'Ibuprofen 400mg', 'Amoxicillin 250mg', 
            'Metformin 500mg', 'Lisinopril 10mg', 'Atorvastatin 20mg',
            'Omeprazole 20mg', 'Aspirin 75mg', 'Losartan 50mg'
        ]
        
        frequencies = ['Once daily', 'Twice daily', 'Three times daily', 'As needed', 'Every 8 hours']
        durations = ['for 3 days', 'for 1 week', 'for 2 weeks', 'for 1 month', 'continue as prescribed']
        
        prescription_items = []
        num_items = fake.random_int(min=1, max=4)
        
        for _ in range(num_items):
            med = random.choice(medications)
            freq = random.choice(frequencies)
            duration = random.choice(durations)
            prescription_items.append(f"{med} - {freq} {duration}")
        
        return "; ".join(prescription_items)
    
    def _generate_vital_signs(self) -> str:
        """Generate realistic vital signs"""
        bp_systolic = fake.random_int(min=90, max=180)
        bp_diastolic = fake.random_int(min=60, max=120)
        pulse = fake.random_int(min=60, max=120)
        temp = round(random.uniform(96.5, 102.0), 1)
        
        return f"BP: {bp_systolic}/{bp_diastolic} mmHg, Pulse: {pulse} bpm, Temp: {temp}°F"
    
    def create_photo_albums_and_photos(self, progress: Progress, task: TaskID):
        """Create photo albums with sample images"""
        if not self.config.generate_photos:
            return
            
        console.print("\n[bold blue]Creating Photo Albums and Photos...[/bold blue]")
        
        album_themes = [
            'Medical Camp', 'Community Event', 'Educational Program', 'Health Awareness',
            'Volunteer Activities', 'Hospital Visit', 'Training Session', 'Cultural Program'
        ]
        
        albums = []
        photos = []
        
        for i in range(self.config.photo_album_count):
            theme = random.choice(album_themes)
            creator = random.choice(self.users['aamil'] + self.users['moze_coordinator']) if (self.users['aamil'] or self.users['moze_coordinator']) else None
            
            album = PhotoAlbum(
                title=f"{theme} {fake.date_between(start_date='-2y', end_date='today').year}",
                description=fake.text(max_nb_chars=200),
                created_by=creator,
                is_public=fake.boolean(chance_of_getting_true=70),
                moze=random.choice(self.moze_list) if self.moze_list else None
            )
            albums.append(album)
            
            progress.advance(task, 0.5)
        
        # Bulk create albums
        PhotoAlbum.objects.bulk_create(albums, batch_size=self.config.bulk_create_batch_size)
        self.photo_albums = list(PhotoAlbum.objects.all().order_by('id'))
        
        # Create photos for albums
        if self.config.create_sample_files:
            for album_idx, album in enumerate(self.photo_albums):
                for j in range(self.config.photos_per_album):
                    if self.config.create_sample_files:
                        # Generate sample image
                        image_file = self._generate_sample_image(
                            text=f"{album.title} {j+1}"
                        )
                    else:
                        image_file = None
                    
                    photo = Photo(
                        album=album,
                        title=f"Photo {j+1}",
                        description=fake.sentence(),
                        image=image_file,
                        uploaded_by=album.created_by,
                        is_featured=fake.boolean(chance_of_getting_true=20)
                    )
                    photos.append(photo)
                
                progress.advance(task, 0.5)
        
        # Bulk create photos
        if photos:
            Photo.objects.bulk_create(photos, batch_size=self.config.bulk_create_batch_size)
            self.stats.photos_created = len(photos)
    
    def create_surveys_and_evaluations(self, progress: Progress, task: TaskID):
        """Create comprehensive surveys and evaluations"""
        console.print("\n[bold blue]Creating Surveys and Evaluations...[/bold blue]")
        
        # Create evaluation criteria first
        criteria_data = [
            ('Academic Performance', 'Assessment of student academic achievements'),
            ('Class Participation', 'Level of engagement in classroom activities'),
            ('Attendance', 'Regularity and punctuality in attending classes'),
            ('Behavior and Conduct', 'Professional behavior and ethical conduct'),
            ('Assignment Quality', 'Quality and timeliness of submitted work'),
            ('Communication Skills', 'Verbal and written communication abilities'),
            ('Leadership Potential', 'Demonstration of leadership qualities'),
            ('Teamwork', 'Ability to work effectively in groups')
        ]
        
        criteria_objects = []
        for name, desc in criteria_data:
            criteria = EvaluationCriteria(
                name=name,
                description=desc,
                weight=100.0 / len(criteria_data),  # Equal weight
                is_active=True
            )
            criteria_objects.append(criteria)
        
        EvaluationCriteria.objects.bulk_create(criteria_objects, batch_size=self.config.bulk_create_batch_size)
        all_criteria = list(EvaluationCriteria.objects.all())
        
        # Create surveys
        survey_templates = [
            {
                'title': 'Healthcare Service Satisfaction Survey',
                'description': 'Please rate your experience with our healthcare services',
                'questions': [
                    {'id': 1, 'text': 'How satisfied are you with the doctor consultation?', 'type': 'rating', 'required': True, 'options': ['1', '2', '3', '4', '5']},
                    {'id': 2, 'text': 'How would you rate the appointment booking process?', 'type': 'rating', 'required': True, 'options': ['1', '2', '3', '4', '5']},
                    {'id': 3, 'text': 'Was the medical facility clean and well-maintained?', 'type': 'rating', 'required': True, 'options': ['1', '2', '3', '4', '5']},
                    {'id': 4, 'text': 'Would you recommend our services to others?', 'type': 'choice', 'required': True, 'options': ['Definitely', 'Probably', 'Not Sure', 'Probably Not', 'Definitely Not']},
                    {'id': 5, 'text': 'Any suggestions for improvement?', 'type': 'text', 'required': False}
                ]
            },
            {
                'title': 'Community Program Feedback',
                'description': 'Help us improve our community programs',
                'questions': [
                    {'id': 1, 'text': 'How useful was this program for you?', 'type': 'rating', 'required': True, 'options': ['1', '2', '3', '4', '5']},
                    {'id': 2, 'text': 'How would you rate the program organization?', 'type': 'rating', 'required': True, 'options': ['1', '2', '3', '4', '5']},
                    {'id': 3, 'text': 'What topics would you like to see covered in future programs?', 'type': 'text', 'required': False}
                ]
            }
        ]
        
        surveys = []
        survey_responses = []
        
        for i in range(self.config.survey_count):
            template = random.choice(survey_templates)
            creator = random.choice(self.users['aamil'] + self.users['moze_coordinator']) if (self.users['aamil'] or self.users['moze_coordinator']) else None
            
            survey = Survey(
                title=f"{template['title']} {i+1}",
                description=template['description'],
                questions=template['questions'],
                created_by=creator,
                start_date=timezone.make_aware(datetime.combine(fake.date_between(start_date='-6m', end_date='today'), datetime.min.time())),
                end_date=timezone.make_aware(datetime.combine(fake.date_between(start_date='today', end_date='+6m'), datetime.min.time())),
                is_active=fake.boolean(chance_of_getting_true=80),
                is_anonymous=fake.boolean(chance_of_getting_true=60)
            )
            surveys.append(survey)
            
            progress.advance(task, 0.5)
        
        # Bulk create surveys
        Survey.objects.bulk_create(surveys, batch_size=self.config.bulk_create_batch_size)
        created_surveys = list(Survey.objects.all().order_by('id'))
        
        # Create survey responses
        all_users = (self.users['student'] + self.users['patient'] + 
                    self.users['doctor'] + self.users['moze_coordinator'])
        
        for survey in created_surveys[:5]:  # Limit responses for performance
            respondents = random.sample(all_users, min(20, len(all_users))) if all_users else []
            
            for respondent in respondents:
                response_data = {}
                for question in survey.questions:
                    if question['type'] == 'rating':
                        response_data[str(question['id'])] = str(fake.random_int(min=1, max=5))
                    elif question['type'] == 'choice':
                        response_data[str(question['id'])] = random.choice(question['options'])
                    else:
                        response_data[str(question['id'])] = fake.sentence() if fake.boolean(chance_of_getting_true=70) else ''
                
                survey_response = SurveyResponse(
                    survey=survey,
                    respondent=respondent,
                    answers=response_data,
                    is_complete=fake.boolean(chance_of_getting_true=80),
                    completion_time=fake.random_int(min=60, max=1800)  # 1-30 minutes
                )
                survey_responses.append(survey_response)
            
            progress.advance(task, 0.5)
        
        SurveyResponse.objects.bulk_create(survey_responses, batch_size=self.config.bulk_create_batch_size)
        
        # Create evaluations
        evaluations = []
        students_sample = random.sample(self.users['student'], min(100, len(self.users['student']))) if self.users['student'] else []
        evaluators = self.users['aamil'] + self.users['moze_coordinator']
        
        for student in students_sample:
            if evaluators:
                evaluation = Evaluation(
                    moze=random.choice(self.moze_list),
                    evaluator=random.choice(evaluators),
                    evaluation_period=fake.random_element(['monthly', 'quarterly', 'biannual', 'annual']),
                    overall_grade=fake.random_element(['A+', 'A', 'B', 'C', 'D', 'E']),
                    overall_score=fake.random_int(min=60, max=100),
                    infrastructure_score=fake.random_int(min=50, max=100),
                    medical_quality_score=fake.random_int(min=60, max=100),
                    staff_performance_score=fake.random_int(min=55, max=100),
                    patient_satisfaction_score=fake.random_int(min=65, max=100),
                    administration_score=fake.random_int(min=50, max=100),
                    safety_score=fake.random_int(min=70, max=100),
                    equipment_score=fake.random_int(min=60, max=100),
                    accessibility_score=fake.random_int(min=55, max=100),
                    strengths=fake.text(max_nb_chars=200),
                    weaknesses=fake.text(max_nb_chars=200),
                    recommendations=fake.text(max_nb_chars=300),
                    evaluation_date=fake.date_between(start_date='-90d', end_date='today'),
                    follow_up_required=fake.boolean(chance_of_getting_true=30),
                    certification_status=fake.random_element(['certified', 'provisional', 'warning']),
                    is_draft=fake.boolean(chance_of_getting_true=20),
                    is_published=fake.boolean(chance_of_getting_true=70)
                )
                evaluations.append(evaluation)
        
        Evaluation.objects.bulk_create(evaluations, batch_size=self.config.bulk_create_batch_size)
        
        progress.advance(task)
    
    def create_petitions_and_requests(self, progress: Progress, task: TaskID):
        """Create comprehensive petition system"""
        console.print("\n[bold blue]Creating Petitions and Requests...[/bold blue]")
        
        petition_types = [
            'medical_assistance', 'financial_aid', 'educational_support',
            'housing_assistance', 'emergency_support', 'marriage_assistance',
            'business_support', 'travel_assistance', 'general_welfare'
        ]
        
        petitions = []
        
        all_petitioners = self.users['patient'] + self.users['student']
        
        for i in range(self.config.petition_count):
            if not all_petitioners or not self.moze_list:
                break
                
            petitioner = random.choice(all_petitioners)
            moze = random.choice(self.moze_list)
            petition_type = random.choice(petition_types)
            
            # Generate realistic amounts based on petition type
            amount_ranges = {
                'medical_assistance': (5000, 50000),
                'financial_aid': (10000, 100000),
                'educational_support': (5000, 25000),
                'housing_assistance': (20000, 200000),
                'emergency_support': (2000, 30000),
                'marriage_assistance': (50000, 300000),
                'business_support': (25000, 500000),
                'travel_assistance': (5000, 50000),
                'general_welfare': (1000, 20000)
            }
            
            min_amount, max_amount = amount_ranges.get(petition_type, (1000, 50000))
            requested_amount = Decimal(fake.random_int(min=min_amount, max=max_amount))
            
            status = fake.random_element(['pending', 'under_review', 'approved', 'rejected', 'partially_approved'])
            
            petition = Petition(
                moze=moze,
                title=f"{petition_type} Request - {fake.sentence(nb_words=4)}",
                description=self._generate_petition_description(petition_type),
                created_by=petitioner,
                petitioner_name=petitioner.get_full_name(),
                petitioner_email=petitioner.email if petitioner.email else fake.email(),
                petitioner_mobile=fake.phone_number()[:20],
                its_id=petitioner.its_id,
                status=fake.random_element(['pending', 'in_progress', 'resolved', 'rejected']),
                priority=fake.random_element(['low', 'medium', 'high']),
                is_anonymous=fake.boolean(chance_of_getting_true=10)
            )
            petitions.append(petition)
            
            progress.advance(task)
        
        # Bulk create petitions
        Petition.objects.bulk_create(petitions, batch_size=self.config.bulk_create_batch_size)
        # Note: PetitionStatus is a lookup table, not for tracking changes
        console.print(f"✓ Created {len(petitions)} petitions", style="green")
    
    def _generate_petition_description(self, petition_type: str) -> str:
        """Generate realistic petition descriptions"""
        descriptions = {
            'medical_assistance': [
                "Request for financial assistance for urgent medical treatment",
                "Support needed for surgery expenses and post-operative care",
                "Help required for ongoing medical treatment and medications"
            ],
            'financial_aid': [
                "Request for emergency financial support due to job loss",
                "Assistance needed for family expenses during difficult times",
                "Support required for debt relief and financial stability"
            ],
            'educational_support': [
                "Request for scholarship assistance for higher education",
                "Support needed for educational materials and fees",
                "Help required for vocational training program enrollment"
            ],
            'housing_assistance': [
                "Request for support with housing down payment",
                "Assistance needed for urgent home repairs",
                "Support required for relocation expenses"
            ]
        }
        
        default_descriptions = [
            f"Request for {petition_type.replace('_', ' ')} support",
            f"Assistance needed for {petition_type.replace('_', ' ')} related expenses",
            f"Support required for {petition_type.replace('_', ' ')} purposes"
        ]
        
        return random.choice(descriptions.get(petition_type, default_descriptions))
    
    def _generate_status_comment(self, status: str) -> str:
        """Generate realistic status comments"""
        comments = {
            'approved': [
                "Application reviewed and approved after thorough assessment",
                "Request approved based on merit and available resources",
                "Approved for the full requested amount"
            ],
            'rejected': [
                "Application does not meet current criteria",
                "Insufficient documentation provided",
                "Request exceeds available budget allocation"
            ],
            'under_review': [
                "Application is being reviewed by the committee",
                "Additional documentation requested from applicant",
                "Currently under evaluation for approval"
            ],
            'partially_approved': [
                "Approved for partial amount based on available resources",
                "Request approved with some modifications",
                "Partial approval granted pending additional review"
            ]
        }
        
        return random.choice(comments.get(status, [f"Status updated to {status}"]))
    
    def generate_summary_report(self) -> Table:
        """Generate a comprehensive summary report"""
        table = Table(title="Mock Data Generation Summary", show_header=True, header_style="bold magenta")
        table.add_column("Category", style="cyan", width=25)
        table.add_column("Count", justify="right", style="green", width=10)
        table.add_column("Details", style="yellow")
        
        # Count all created objects
        total_users = sum(len(users) for users in self.users.values())
        total_moze = Moze.objects.count()
        total_hospitals = Hospital.objects.count()
        total_doctors = Doctor.objects.count()
        total_patients = Patient.objects.count()
        total_students = Student.objects.count()
        total_appointments = Appointment.objects.count()
        total_medical_records = PatientLog.objects.count()
        total_petitions = Petition.objects.count()
        total_surveys = Survey.objects.count()
        total_evaluations = Evaluation.objects.count()
        total_photos = Photo.objects.count()
        
        table.add_row("Total Users", str(total_users), f"Admin: {len(self.users['admin'])}, Aamil: {len(self.users['aamil'])}, Coordinators: {len(self.users['moze_coordinator'])}")
        table.add_row("Healthcare Staff", str(len(self.users['doctor']) + len(self.users['patient'])), f"Doctors: {len(self.users['doctor'])}, Patients: {len(self.users['patient'])}")
        table.add_row("Students", str(len(self.users['student'])), f"Enrolled in {Course.objects.count()} courses")
        table.add_row("Infrastructure", str(total_moze + total_hospitals), f"Moze: {total_moze}, Hospitals: {total_hospitals}")
        table.add_row("Appointments", str(total_appointments), f"With notes and reminders")
        table.add_row("Medical Records", str(total_medical_records), f"Comprehensive patient logs")
        table.add_row("Petitions", str(total_petitions), f"Various assistance requests")
        table.add_row("Surveys", str(total_surveys), f"With responses and analytics")
        table.add_row("Evaluations", str(total_evaluations), f"Student and performance evaluations")
        table.add_row("Photos", str(total_photos), f"In {PhotoAlbum.objects.count()} albums")
        
        if self.stats.duration:
            table.add_row("Generation Time", f"{self.stats.duration.total_seconds():.1f}s", "Total time taken")
        
        if self.stats.errors:
            table.add_row("Errors", str(len(self.stats.errors)), "Check logs for details")
        
        return table
    
    @transaction.atomic
    def generate_all_data(self):
        """Generate all mock data with progress tracking"""
        self.stats.start_time = datetime.now()
        
        # Calculate total tasks for progress tracking
        total_tasks = (
            self.config.admin_count +
            self.config.aamil_count + self.config.moze_count +
            self.config.coordinator_count +
            self.config.doctor_count +
            self.config.student_count +
            self.config.patient_count +
            self.config.hospital_count +
            (self.config.medical_record_count // 3) +
            (self.config.appointment_count if self.config.generate_appointments else 0) +
            (self.config.photo_album_count if self.config.generate_photos else 0) +
            self.config.survey_count +
            (self.config.petition_count // 10)
        )
        
        console.print(Panel.fit(
            "[bold blue]Enhanced Mock Data Generator v2.0[/bold blue]\n"
            "[yellow]Generating comprehensive test data for Umoor Sehhat System[/yellow]\n"
            f"[green]Total estimated operations: {total_tasks:,}[/green]",
            title="Starting Generation",
            border_style="blue"
        ))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            try:
                # Create all tasks
                admin_task = progress.add_task("Creating Admins...", total=self.config.admin_count)
                moze_task = progress.add_task("Creating Moze & Aamils...", total=self.config.aamil_count + self.config.moze_count)
                coord_task = progress.add_task("Creating Coordinators...", total=self.config.coordinator_count)
                doctor_task = progress.add_task("Creating Doctors...", total=self.config.doctor_count)
                student_task = progress.add_task("Creating Students...", total=self.config.student_count)
                patient_task = progress.add_task("Creating Patients...", total=self.config.patient_count)
                hospital_task = progress.add_task("Creating Hospitals...", total=self.config.hospital_count)
                medical_task = progress.add_task("Creating Medical Records...", total=self.config.medical_record_count // 3)
                
                # Generate core data
                self.create_admin_users(progress, admin_task)
                self.create_moze_with_aamils(progress, moze_task)
                self.create_coordinators(progress, coord_task)
                self.create_doctors_and_services(progress, doctor_task)
                self.create_students_and_courses(progress, student_task)
                self.create_patients(progress, patient_task)
                self.create_hospitals_and_departments(progress, hospital_task)
                self.create_medical_records(progress, medical_task)
                
                # Generate optional data
                if self.config.generate_appointments:
                    appointment_task = progress.add_task("Creating Appointments...", total=self.config.appointment_count)
                    self.create_appointments(progress, appointment_task)
                
                if self.config.generate_photos:
                    photo_task = progress.add_task("Creating Photos...", total=self.config.photo_album_count)
                    self.create_photo_albums_and_photos(progress, photo_task)
                
                survey_task = progress.add_task("Creating Surveys...", total=self.config.survey_count)
                self.create_surveys_and_evaluations(progress, survey_task)
                
                petition_task = progress.add_task("Creating Petitions...", total=self.config.petition_count // 10)
                self.create_petitions_and_requests(progress, petition_task)
                
            except Exception as e:
                self.logger.error(f"Error during generation: {e}")
                self.stats.errors.append(str(e))
                console.print(f"[red]Error: {e}[/red]")
                raise
        
        self.stats.end_time = datetime.now()
        
        # Display summary
        console.print("\n")
        console.print(self.generate_summary_report())
        
        # Display sample login credentials
        console.print(Panel.fit(
            "[bold green]Sample Login Credentials[/bold green]\n"
            "[yellow]All users have password: pass1234[/yellow]\n\n"
            f"[cyan]Admin:[/cyan] 10000001\n"
            f"[cyan]Aamil:[/cyan] 10000002\n"
            f"[cyan]Coordinator:[/cyan] 10000102\n"
            f"[cyan]Doctor:[/cyan] 10000202\n"
            f"[cyan]Student:[/cyan] 10000252\n"
            f"[cyan]Patient:[/cyan] 10000452",
            title="Access Information",
            border_style="green"
        ))
        
        if self.stats.errors:
            console.print(f"\n[yellow]Warning: {len(self.stats.errors)} errors occurred. Check logs for details.[/yellow]")
        
        console.print(f"\n[bold green]✅ Generation completed in {self.stats.duration.total_seconds():.1f} seconds![/bold green]")


def main():
    """Main function with enhanced CLI"""
    console.print(Panel.fit(
        "[bold blue]Enhanced Mock Data Generator for Umoor Sehhat[/bold blue]\n"
        "[yellow]This will generate comprehensive test data including:[/yellow]\n"
        "• Users with realistic profiles and roles\n"
        "• Complete appointment system\n"
        "• Medical records and patient logs\n"
        "• Photo albums with sample images\n"
        "• Surveys, evaluations, and petitions\n"
        "• Hospital and Moze infrastructure\n\n"
        "[red]⚠️  WARNING: Only run on development/test databases![/red]",
        title="Mock Data Generator v2.0",
        border_style="blue"
    ))
    
    # Configuration options
    console.print("\n[bold]Configuration Options:[/bold]")
    console.print("1. Quick Test (Small dataset)")
    console.print("2. Standard Development (Default)")
    console.print("3. Full Production Test (Large dataset)")
    console.print("4. Custom Configuration")
    
    choice = console.input("\n[bold]Select configuration [2]: [/bold]") or "2"
    
    if choice == "1":
        config = GenerationConfig(
            aamil_count=10, coordinator_count=10, doctor_count=5,
            student_count=20, patient_count=50, moze_count=10,
            hospital_count=2, appointment_count=100, petition_count=50,
            generate_photos=False, create_sample_files=False
        )
        console.print("[green]Using Quick Test configuration[/green]")
    elif choice == "3":
        config = GenerationConfig(
            aamil_count=200, coordinator_count=200, doctor_count=100,
            student_count=500, patient_count=1000, moze_count=200,
            hospital_count=10, appointment_count=2000, petition_count=1000
        )
        console.print("[green]Using Full Production Test configuration[/green]")
    elif choice == "4":
        console.print("[yellow]Custom configuration not implemented in this demo[/yellow]")
        config = GenerationConfig()
    else:
        config = GenerationConfig()
        console.print("[green]Using Standard Development configuration[/green]")
    
    confirm = console.input(f"\n[bold]Proceed with data generation? [y/N]: [/bold]")
    
    if confirm.lower() in ['y', 'yes']:
        try:
            generator = EnhancedMockDataGenerator(config)
            generator.generate_all_data()
        except KeyboardInterrupt:
            console.print("\n[red]Generation cancelled by user[/red]")
        except Exception as e:
            console.print(f"\n[red]Generation failed: {e}[/red]")
            raise
    else:
        console.print("[yellow]Data generation cancelled[/yellow]")


if __name__ == '__main__':
    main()