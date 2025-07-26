#!/usr/bin/env python3
"""
Comprehensive Test Data Population Script for Umoor Sehhat
Populates all 9 Django apps with realistic test data
"""

import os
import sys
import django
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
import random
from faker import Faker
from PIL import Image
from django.core.files.base import ContentFile
import io

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

# Import all models after Django setup
from accounts.models import User
from students.models import Student, Course, Enrollment, Assignment, Grade, Attendance, Event, Announcement
from surveys.models import Survey, SurveyResponse
from mahalshifa.models import Hospital, Patient, Appointment, Doctor as MahalshifaDoctor, InventoryItem, Inventory
from moze.models import Moze, MozeComment
from photos.models import PhotoAlbum, Photo, PhotoTag
from doctordirectory.models import Doctor, MedicalRecord, Patient as DDPatient
from evaluation.models import EvaluationForm, EvaluationSubmission
from araz.models import Petition, PetitionComment

# Initialize Faker
fake = Faker()
Faker.seed(42)  # For reproducible data
random.seed(42)

class DataPopulator:
    def __init__(self):
        self.users = {}
        self.students = []
        self.doctors = []
        self.mozes = []
        self.hospitals = []
        self.courses = []
        
    def print_status(self, message):
        print(f"🔄 {message}")
        
    def print_success(self, message):
        print(f"✅ {message}")
        
    def print_section(self, title):
        print(f"\n{'='*60}")
        print(f"📋 {title}")
        print(f"{'='*60}")

    def clear_existing_data(self):
        """Clear all existing data to start fresh"""
        self.print_section("CLEARING EXISTING DATA")
        
        try:
            # Clear in reverse dependency order
            self.print_status("Clearing existing data...")
            
            # Clear app-specific data
            Appointment.objects.all().delete()
            InventoryItem.objects.all().delete()
            Inventory.objects.all().delete()
            Patient.objects.all().delete()
            MahalshifaDoctor.objects.all().delete()
            Hospital.objects.all().delete()
            
            MedicalRecord.objects.all().delete()
            DDPatient.objects.all().delete()
            Doctor.objects.all().delete()
            
            PetitionComment.objects.all().delete()
            Petition.objects.all().delete()
            
            EvaluationSubmission.objects.all().delete()
            EvaluationForm.objects.all().delete()
            
            SurveyResponse.objects.all().delete()
            Survey.objects.all().delete()
            
            Photo.objects.all().delete()
            PhotoAlbum.objects.all().delete()
            PhotoTag.objects.all().delete()
            
            MozeComment.objects.all().delete()
            Moze.objects.all().delete()
            
            Attendance.objects.all().delete()
            Grade.objects.all().delete()
            Assignment.objects.all().delete()
            Enrollment.objects.all().delete()
            Announcement.objects.all().delete()
            Event.objects.all().delete()
            Course.objects.all().delete()
            Student.objects.all().delete()
            
            # Clear users last
            User.objects.all().delete()
            
            self.print_success("All existing data cleared successfully")
            
        except Exception as e:
            self.print_status(f"Warning during cleanup: {e}")
            # Continue anyway

    def generate_its_id(self, prefix="", length=8):
        """Generate realistic ITS ID"""
        if not hasattr(self, '_its_id_counter'):
            self._its_id_counter = {}
        
        if prefix not in self._its_id_counter:
            self._its_id_counter[prefix] = 1
        
        if prefix:
            remaining = length - len(prefix)
            id_num = self._its_id_counter[prefix]
            self._its_id_counter[prefix] += 1
            return prefix + str(id_num).zfill(remaining)
        else:
            id_num = self._its_id_counter[prefix]
            self._its_id_counter[prefix] += 1
            return str(id_num).zfill(length)

    def create_dummy_image(self, size=(800, 600)):
        """Create a dummy image file for testing"""
        img = Image.new('RGB', size, color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG')
        img_io.seek(0)
        return ContentFile(img_io.read(), name=f'test_image_{random.randint(1000, 9999)}.jpg')

    def create_users(self):
        """Create all users with proper roles"""
        self.print_section("CREATING USERS")
        
        # Create 2 Admin users
        self.print_status("Creating 2 Admin users...")
        for i in range(2):
            admin = User.objects.create_user(
                username=f'admin_{i+1}',
                email=f'admin{i+1}@umoor.sehhat',
                password='admin123',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                role='admin',
                its_id=self.generate_its_id("ADM"),
                is_staff=True,
                is_superuser=True
            )
            self.users['admin'] = self.users.get('admin', []) + [admin]
        
        # Create 10 Staff users
        self.print_status("Creating 10 Staff users...")
        for i in range(10):
            staff = User.objects.create_user(
                username=f'staff_{i+1}',
                email=f'staff{i+1}@umoor.sehhat',
                password='staff123',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                role='staff',
                its_id=self.generate_its_id("STF"),
                is_staff=True
            )
            self.users['staff'] = self.users.get('staff', []) + [staff]
        
        # Create 100 Doctor users
        self.print_status("Creating 100 Doctor users...")
        for i in range(100):
            doctor = User.objects.create_user(
                username=f'doctor_{i+1:03d}',
                email=f'doctor{i+1:03d}@umoor.sehhat',
                password='doctor123',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                role='doctor',
                its_id=self.generate_its_id("DOC")
            )
            self.users['doctor'] = self.users.get('doctor', []) + [doctor]
        
        # Create 500 Student users
        self.print_status("Creating 500 Student users...")
        for i in range(500):
            student = User.objects.create_user(
                username=f'student_{i+1:03d}',
                email=f'student{i+1:03d}@umoor.sehhat',
                password='student123',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                role='student',
                its_id=self.generate_its_id("STU")
            )
            self.users['student'] = self.users.get('student', []) + [student]
        
        # Create Aamil and Moze Coordinator users
        self.print_status("Creating Aamil and Moze Coordinator users...")
        for i in range(20):
            aamil = User.objects.create_user(
                username=f'aamil_{i+1}',
                email=f'aamil{i+1}@umoor.sehhat',
                password='aamil123',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                role='aamil',
                its_id=self.generate_its_id("AAM"),
                is_staff=True
            )
            self.users['aamil'] = self.users.get('aamil', []) + [aamil]
        
        for i in range(15):
            coordinator = User.objects.create_user(
                username=f'coordinator_{i+1}',
                email=f'coordinator{i+1}@umoor.sehhat',
                password='coord123',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                role='moze_coordinator',
                its_id=self.generate_its_id("MOZ"),
                is_staff=True
            )
            self.users['moze_coordinator'] = self.users.get('moze_coordinator', []) + [coordinator]
        
        total_users = sum(len(users) for users in self.users.values())
        self.print_success(f"Created {total_users} users across all roles")

    def populate_students_app(self):
        """Populate Students app with comprehensive data"""
        self.print_section("POPULATING STUDENTS APP")
        
        # Create Student profiles
        self.print_status("Creating Student profiles...")
        academic_levels = ['undergraduate', 'postgraduate', 'doctoral', 'diploma']
        enrollment_statuses = ['active', 'suspended', 'graduated', 'withdrawn']
        
        for i, user in enumerate(self.users['student']):
            enrollment_date = fake.date_between(start_date='-4y', end_date=datetime.now().date())
            student = Student.objects.create(
                user=user,
                student_id=f'MED{2024000 + i + 1}',
                academic_level=random.choice(academic_levels),
                enrollment_status=random.choice(enrollment_statuses[:2]),  # Mostly active
                enrollment_date=enrollment_date,
                expected_graduation=fake.date_between(start_date=enrollment_date, end_date='+4y')
            )
            self.students.append(student)
        
        # Create Courses
        self.print_status("Creating medical courses...")
        course_data = [
            ('ANAT101', 'Human Anatomy I', 'Introduction to human anatomy and physiology', 4, 'beginner'),
            ('PHYS102', 'Medical Physiology', 'Comprehensive study of human physiology', 4, 'beginner'),
            ('BIOC103', 'Medical Biochemistry', 'Biochemical processes in human body', 3, 'intermediate'),
            ('PATH201', 'General Pathology', 'Principles of disease processes', 4, 'intermediate'),
            ('PHAR202', 'Pharmacology I', 'Basic principles of pharmacology', 3, 'intermediate'),
            ('MICR203', 'Medical Microbiology', 'Study of microorganisms and disease', 3, 'intermediate'),
            ('SURG301', 'Introduction to Surgery', 'Basic surgical principles', 4, 'advanced'),
            ('PEDI302', 'Pediatrics', 'Medical care of children', 4, 'advanced'),
            ('CARD303', 'Cardiology', 'Heart and cardiovascular system', 4, 'advanced'),
            ('NEUR304', 'Neurology', 'Nervous system disorders', 4, 'advanced'),
        ]
        
        for code, name, description, credits, level in course_data:
            instructor = random.choice(self.users.get('doctor', []) + self.users.get('admin', []))
            course = Course.objects.create(
                code=code,
                name=name,
                description=description,
                credits=credits,
                level=level,
                instructor=instructor,
                is_active=True,
                max_students=random.randint(30, 100)
            )
            self.courses.append(course)
        
        # Create Enrollments
        self.print_status("Creating student enrollments...")
        for student in self.students[:300]:  # Enroll 300 students
            num_courses = random.randint(3, 6)
            enrolled_courses = random.sample(self.courses, min(num_courses, len(self.courses)))
            
            for course in enrolled_courses:
                status = random.choice(['enrolled', 'completed', 'dropped'])
                grade = random.choice(['A', 'B', 'C', 'D', 'F', '']) if status == 'completed' else ''
                
                Enrollment.objects.create(
                    student=student,
                    course=course,
                    status=status,
                    grade=grade
                )
        
        # Create Events
        self.print_status("Creating academic events...")
        event_types = ['academic', 'cultural', 'sports', 'workshop', 'seminar', 'social']
        for i in range(50):
            start_date = fake.date_time_between(start_date='-1y', end_date='+1y')
            end_date = fake.date_time_between(start_date=start_date, end_date='+1y')
            organizer = random.choice(self.users.get('admin', []) + self.users.get('staff', []))
            
            Event.objects.create(
                title=f"{fake.catch_phrase()} - {random.choice(event_types).title()}",
                description=fake.text(max_nb_chars=200),
                start_date=start_date,
                end_date=end_date,
                location=fake.address(),
                event_type=random.choice(event_types),
                organizer=organizer,
                max_participants=random.randint(50, 500),
                registration_required=random.choice([True, False]),
                is_published=random.choice([True, False])
            )
        
        # Create Announcements
        self.print_status("Creating course announcements...")
        for course in self.courses:
            for _ in range(random.randint(2, 5)):
                Announcement.objects.create(
                    course=course,
                    title=f"Important: {fake.sentence(nb_words=4)}",
                    content=fake.text(max_nb_chars=300),
                    author=course.instructor,
                    is_urgent=random.choice([True, False])
                )
        
        self.print_success(f"Students app populated: {len(self.students)} students, {len(self.courses)} courses")

    def populate_surveys_app(self):
        """Populate Surveys app with 10 surveys"""
        self.print_section("POPULATING SURVEYS APP")
        
        survey_topics = [
            ("Medical Service Satisfaction", "How satisfied are you with our medical services?"),
            ("Educational Quality Assessment", "Evaluate the quality of education provided"),
            ("Facility Infrastructure Review", "Assessment of facility infrastructure"),
            ("Staff Performance Evaluation", "Rate the performance of our staff"),
            ("Student Learning Experience", "Share your learning experience feedback"),
            ("Healthcare Accessibility Survey", "Evaluate healthcare accessibility"),
            ("Technology Usage Assessment", "How do you use our technology resources?"),
            ("Community Engagement Survey", "Your involvement in community activities"),
            ("Safety and Security Review", "Assessment of safety measures"),
            ("Future Improvement Suggestions", "What improvements would you suggest?")
        ]
        
        self.print_status("Creating 10 comprehensive surveys...")
        surveys = []
        
        for i, (title, description) in enumerate(survey_topics):
            # Create sample questions for each survey
            questions = [
                {
                    "id": 1,
                    "type": "text",
                    "text": "What is your name?",
                    "required": False,
                    "options": []
                },
                {
                    "id": 2,
                    "type": "multiple_choice",
                    "text": description,
                    "required": True,
                    "options": ["Excellent", "Very Good", "Good", "Fair", "Poor"]
                },
                {
                    "id": 3,
                    "type": "rating",
                    "text": "Rate your overall experience (1-5)",
                    "required": True,
                    "options": ["1", "2", "3", "4", "5"]
                },
                {
                    "id": 4,
                    "type": "textarea",
                    "text": "Please provide additional comments or suggestions",
                    "required": False,
                    "options": []
                }
            ]
            
            creator = random.choice(self.users.get('admin', []) + self.users.get('aamil', []))
            survey = Survey.objects.create(
                title=title,
                description=description,
                target_role=random.choice(['all', 'student', 'doctor', 'aamil']),
                questions=questions,
                created_by=creator,
                is_active=True,
                is_anonymous=random.choice([True, False]),
                allow_multiple_responses=False,
                show_results=random.choice([True, False]),
                start_date=timezone.now() - timedelta(days=random.randint(1, 30)),
                end_date=timezone.now() + timedelta(days=random.randint(30, 90))
            )
            surveys.append(survey)
        
        # Create survey responses
        self.print_status("Creating survey responses...")
        all_users = []
        for user_list in self.users.values():
            all_users.extend(user_list)
        
        for survey in surveys:
            # Random number of responses per survey (20-100)
            num_responses = random.randint(20, 100)
            respondents = random.sample(all_users, min(num_responses, len(all_users)))
            
            for respondent in respondents:
                answers = {
                    "1": fake.name() if not survey.is_anonymous else "Anonymous",
                    "2": random.choice(["Excellent", "Very Good", "Good", "Fair", "Poor"]),
                    "3": str(random.randint(1, 5)),
                    "4": fake.text(max_nb_chars=100)
                }
                
                SurveyResponse.objects.create(
                    survey=survey,
                    respondent=respondent,
                    answers=answers,
                    is_complete=True,
                    completion_time=random.randint(60, 600)  # 1-10 minutes
                )
        
        self.print_success(f"Surveys app populated: {len(surveys)} surveys with responses")

    def populate_moze_app(self):
        """Populate Moze app with 72 centers"""
        self.print_section("POPULATING MOZE APP")
        
        # Create 72 Moze centers
        self.print_status("Creating 72 Moze centers...")
        cities = ['Karachi', 'Lahore', 'Islamabad', 'Rawalpindi', 'Faisalabad', 'Multan', 'Peshawar', 'Quetta']
        
        for i in range(72):
            aamil = random.choice(self.users.get('aamil', []))
            coordinator = random.choice(self.users.get('moze_coordinator', []))
            city = random.choice(cities)
            
            moze = Moze.objects.create(
                name=f"{fake.company()} Medical Center - {city} {i+1}",
                location=city,
                address=f"{fake.street_address()}, {city}, Pakistan",
                contact_phone=fake.phone_number()[:15],
                contact_email=f"moze{i+1}@{city.lower()}.com",
                established_date=fake.date_between(start_date='-20y', end_date='-1y'),
                aamil=aamil,
                moze_coordinator=coordinator,
                capacity=random.randint(50, 500),
                is_active=True
            )
            self.mozes.append(moze)
        
        # Create Moze comments
        self.print_status("Creating Moze comments...")
        for moze in self.mozes:
            num_comments = random.randint(2, 8)
            for _ in range(num_comments):
                commenter = random.choice(
                    self.users.get('admin', []) + 
                    self.users.get('doctor', []) + 
                    self.users.get('student', [])
                )
                MozeComment.objects.create(
                    moze=moze,
                    author=commenter,
                    content=fake.text(max_nb_chars=150)
                )
        
        self.print_success(f"Moze app populated: {len(self.mozes)} centers with comments")

    def populate_mahalshifa_app(self):
        """Populate Mahalshifa (Hospital Management) app"""
        self.print_section("POPULATING MAHALSHIFA APP")
        
        # Create hospitals
        self.print_status("Creating hospitals...")
        for i in range(20):
            total_beds = random.randint(50, 500)
            hospital = Hospital.objects.create(
                name=f"Mahal Shifa Hospital {i+1}",
                description=f"A leading medical facility providing comprehensive healthcare services in the region.",
                address=fake.address(),
                phone=fake.phone_number()[:15],
                email=f"hospital{i+1}@mahalshifa.com",
                hospital_type=random.choice(['general', 'specialty', 'clinic']),
                total_beds=total_beds,
                available_beds=random.randint(10, total_beds//2),
                emergency_beds=random.randint(5, 20),
                icu_beds=random.randint(2, 15),
                is_active=True,
                is_emergency_capable=random.choice([True, False]),
                has_pharmacy=random.choice([True, False]),
                has_laboratory=random.choice([True, False])
            )
            self.hospitals.append(hospital)
        
        # Create doctors in hospitals
        self.print_status("Creating hospital doctors...")
        specialties = ['Cardiology', 'Neurology', 'Orthopedics', 'Pediatrics', 'Surgery']
        
        for i, doctor_user in enumerate(self.users['doctor']):
            hospital = random.choice(self.hospitals)
            try:
                doctor = MahalshifaDoctor.objects.create(
                    user=doctor_user,
                    hospital=hospital,
                    specialty=random.choice(specialties),
                    license_number=f"LIC{random.randint(100000, 999999)}",
                    qualification=random.choice(['MBBS', 'MD', 'PhD', 'FCPS']),
                    experience_years=random.randint(1, 30),
                    consultation_fee=random.randint(1000, 5000),
                    is_available=True
                )
                self.doctors.append(doctor)
            except:
                continue  # Skip if doctor already exists
        
        # Create patients
        self.print_status("Creating patients...")
        patients = []
        blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        
        for i in range(200):
            patient = Patient.objects.create(
                its_id=self.generate_its_id("PAT"),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                date_of_birth=fake.date_of_birth(minimum_age=1, maximum_age=90),
                gender=random.choice(['male', 'female']),
                phone_number=fake.phone_number()[:15],
                email=fake.email(),
                address=fake.address(),
                emergency_contact_name=fake.name(),
                emergency_contact_phone=fake.phone_number()[:15],
                emergency_contact_relationship=random.choice(['spouse', 'parent', 'sibling', 'child', 'friend']),
                blood_group=random.choice(blood_groups) if random.choice([True, False]) else None,
                registered_moze=random.choice(self.mozes) if self.mozes and random.choice([True, False]) else None
            )
            patients.append(patient)
        
        # Create appointments
        self.print_status("Creating appointments...")
        for _ in range(300):
            doctor = random.choice(self.doctors)
            patient = random.choice(patients)
            
            Appointment.objects.create(
                doctor=doctor,
                patient=patient,
                appointment_date=fake.date_time_between(start_date='-30d', end_date='+30d'),
                reason=fake.sentence(nb_words=6),
                status=random.choice(['scheduled', 'completed', 'cancelled', 'no_show']),
                notes=fake.text(max_nb_chars=200) if random.choice([True, False]) else ""
            )
        
        # Create inventory
        self.print_status("Creating hospital inventory...")
        for hospital in self.hospitals:
            inventory = Inventory.objects.create(
                hospital=hospital,
                name=f"{hospital.name} Main Inventory"
            )
            
            # Create inventory items
            items = ['Surgical Masks', 'Gloves', 'Syringes', 'Bandages', 'Antibiotics', 
                    'Painkillers', 'Thermometers', 'Blood Pressure Monitors']
            
            for item_name in items:
                InventoryItem.objects.create(
                    inventory=inventory,
                    name=item_name,
                    description=f"Medical {item_name.lower()} for hospital use",
                    current_stock=random.randint(10, 1000),
                    minimum_stock=random.randint(5, 50),
                    unit_price=random.randint(10, 500),
                    supplier=fake.company()
                )
        
        self.print_success(f"Mahalshifa app populated: {len(self.hospitals)} hospitals, {len(self.doctors)} doctors")

    def populate_doctordirectory_app(self):
        """Populate Doctor Directory app"""
        self.print_section("POPULATING DOCTOR DIRECTORY APP")
        
        # Create doctor profiles
        self.print_status("Creating doctor directory profiles...")
        specialties = ['General Medicine', 'Cardiology', 'Neurology', 'Orthopedics', 'Pediatrics']
        
        for i, doctor_user in enumerate(self.users['doctor']):
            moze = random.choice(self.mozes) if self.mozes else None
            
            try:
                doctor = Doctor.objects.get_or_create(
                    user=doctor_user,
                    defaults={
                        'name': doctor_user.get_full_name(),
                        'its_id': doctor_user.its_id,
                        'specialty': random.choice(specialties),
                        'qualification': random.choice(['MBBS', 'MD', 'PhD', 'FCPS']),
                        'experience_years': random.randint(1, 30),
                        'assigned_moze': moze,
                        'is_verified': random.choice([True, False]),
                        'is_available': True,
                        'license_number': f"LIC{random.randint(100000, 999999)}",
                        'consultation_fee': random.randint(1000, 5000),
                        'phone': fake.phone_number()[:15],
                        'email': doctor_user.email,
                        'address': fake.address(),
                        'languages_spoken': random.choice(['English, Urdu', 'English, Urdu, Punjabi', 'English, Urdu, Sindhi']),
                        'bio': fake.text(max_nb_chars=200)
                    }
                )[0]
            except:
                continue
        
        # Create patients for doctor directory
        self.print_status("Creating doctor directory patients...")
        dd_patients = []
        for i in range(150):
            patient = DDPatient.objects.create(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                date_of_birth=fake.date_of_birth(minimum_age=1, maximum_age=90),
                gender=random.choice(['M', 'F']),
                phone=fake.phone_number()[:15],
                email=fake.email(),
                address=fake.address(),
                emergency_contact_name=fake.name(),
                emergency_contact_phone=fake.phone_number()[:15]
            )
            dd_patients.append(patient)
        
        # Create medical records
        self.print_status("Creating medical records...")
        doctors = Doctor.objects.all()
        for _ in range(200):
            doctor = random.choice(doctors)
            patient = random.choice(dd_patients)
            
            visit_date = fake.date_between(start_date='-1y', end_date=datetime.now().date())
            MedicalRecord.objects.create(
                patient=patient,
                doctor=doctor,
                visit_date=visit_date,
                diagnosis=fake.sentence(nb_words=4),
                treatment=fake.text(max_nb_chars=150),
                prescription=fake.text(max_nb_chars=100),
                follow_up_date=fake.date_between(start_date=visit_date, end_date='+30d') if random.choice([True, False]) else None,
                notes=fake.text(max_nb_chars=200)
            )
        
        self.print_success(f"Doctor Directory populated: {doctors.count()} doctors, {len(dd_patients)} patients")

    def populate_evaluation_app(self):
        """Populate Evaluation app"""
        self.print_section("POPULATING EVALUATION APP")
        
        # Create evaluation forms
        self.print_status("Creating evaluation forms...")
        evaluation_types = ['performance', 'satisfaction', 'quality', 'training', 'service']
        target_roles = ['doctor', 'student', 'aamil', 'all']
        
        forms = []
        for i in range(20):
            creator = random.choice(self.users.get('admin', []) + self.users.get('aamil', []))
            
            form = EvaluationForm.objects.create(
                title=f"Evaluation Form {i+1}: {fake.catch_phrase()}",
                description=fake.text(max_nb_chars=200),
                evaluation_type=random.choice(evaluation_types),
                target_role=random.choice(target_roles),
                is_active=True,
                is_anonymous=random.choice([True, False]),
                due_date=fake.date_time_between(start_date=datetime.now(), end_date='+60d'),
                created_by=creator
            )
            forms.append(form)
        
        # Create evaluation submissions
        self.print_status("Creating evaluation submissions...")
        all_users = []
        for user_list in self.users.values():
            all_users.extend(user_list)
        
        for form in forms:
            num_submissions = random.randint(10, 50)
            evaluators = random.sample(all_users, min(num_submissions, len(all_users)))
            
            for evaluator in evaluators:
                # Random target (could be user or moze)
                target_user = random.choice(all_users) if random.choice([True, False]) else None
                target_moze = random.choice(self.mozes) if random.choice([True, False]) and self.mozes else None
                
                EvaluationSubmission.objects.create(
                    form=form,
                    evaluator=evaluator,
                    target_user=target_user,
                    target_moze=target_moze,
                    score=random.randint(60, 100),
                    feedback=fake.text(max_nb_chars=200),
                    is_completed=True
                )
        
        self.print_success(f"Evaluation app populated: {len(forms)} forms with submissions")

    def populate_araz_app(self):
        """Populate Araz (Petition Management) app with 100 petitions"""
        self.print_section("POPULATING ARAZ APP")
        
        # Create 100 petitions
        self.print_status("Creating 100 petitions...")
        petition_categories = ['medical', 'administrative', 'academic', 'facility', 'complaint']
        statuses = ['pending', 'in_progress', 'resolved', 'rejected']
        priorities = ['low', 'medium', 'high', 'urgent']
        
        petitions = []
        all_users = []
        for user_list in self.users.values():
            all_users.extend(user_list)
        
        for i in range(100):
            petitioner = random.choice(all_users)
            assigned_to = random.choice(self.users.get('admin', []) + self.users.get('aamil', []))
            
            petition = Petition.objects.create(
                title=f"Petition {i+1}: {fake.sentence(nb_words=5)}",
                description=fake.text(max_nb_chars=300),
                category=random.choice(petition_categories),
                petitioner=petitioner,
                assigned_to=assigned_to if random.choice([True, False]) else None,
                status=random.choice(statuses),
                priority=random.choice(priorities),
                is_urgent=random.choice([True, False]),
                expected_resolution_date=fake.date_between(start_date=datetime.now().date(), end_date='+30d'),
                admin_notes=fake.text(max_nb_chars=100) if random.choice([True, False]) else ""
            )
            petitions.append(petition)
        
        # Create petition comments
        self.print_status("Creating petition comments...")
        for petition in petitions:
            num_comments = random.randint(1, 5)
            for _ in range(num_comments):
                commenter = random.choice([petition.petitioner, petition.assigned_to] if petition.assigned_to else [petition.petitioner])
                if commenter:
                    PetitionComment.objects.create(
                        petition=petition,
                        author=commenter,
                        content=fake.text(max_nb_chars=150),
                        is_internal=random.choice([True, False])
                    )
        
        self.print_success(f"Araz app populated: {len(petitions)} petitions with comments")

    def populate_photos_app(self):
        """Populate Photos app"""
        self.print_section("POPULATING PHOTOS APP")
        
        # Create photo albums
        self.print_status("Creating photo albums...")
        album_names = [
            'Medical Conference 2024', 'Student Activities', 'Hospital Events', 
            'Moze Gatherings', 'Educational Workshops', 'Community Service',
            'Sports Events', 'Cultural Programs', 'Graduation Ceremony', 'Research Projects'
        ]
        
        albums = []
        for i, name in enumerate(album_names):
            creator = random.choice(self.users.get('admin', []) + self.users.get('staff', []))
            
            album = PhotoAlbum.objects.create(
                name=name,
                description=fake.text(max_nb_chars=150),
                created_by=creator,
                is_public=random.choice([True, False]),
                moze=random.choice(self.mozes) if random.choice([True, False]) and self.mozes else None
            )
            albums.append(album)
        
        # Create photo tags
        self.print_status("Creating photo tags...")
        tag_names = ['medical', 'education', 'community', 'events', 'students', 'doctors', 'research', 'conference']
        tags = []
        
        for tag_name in tag_names:
            tag, created = PhotoTag.objects.get_or_create(name=tag_name)
            tags.append(tag)
        
        # Create photos
        self.print_status("Creating photos with dummy images...")
        all_users = []
        for user_list in self.users.values():
            all_users.extend(user_list)
        
        for album in albums:
            num_photos = random.randint(5, 15)
            for i in range(num_photos):
                uploader = random.choice(all_users)
                
                photo = Photo.objects.create(
                    title=f"Photo {i+1} - {fake.catch_phrase()}",
                    description=fake.text(max_nb_chars=100),
                    uploaded_by=uploader,
                    moze=album.moze,
                    subject_tag=f'album_{album.id}',
                    is_public=album.is_public,
                    image=self.create_dummy_image()
                )
                
                # Add random tags
                photo_tags = random.sample(tags, random.randint(1, 3))
                photo.tags.set(photo_tags)
        
        self.print_success(f"Photos app populated: {len(albums)} albums with photos")

    def run_population(self):
        """Run the complete data population process"""
        print("🚀 STARTING COMPREHENSIVE DATA POPULATION")
        print("This will create realistic test data for all 9 apps")
        print("⚠️  WARNING: This will DELETE all existing data!")
        print("=" * 60)
        
        try:
            # Clear existing data
            self.clear_existing_data()

            # Create all users first
            self.create_users()
            
            # Populate all apps
            self.populate_students_app()
            self.populate_surveys_app()
            self.populate_moze_app()
            self.populate_mahalshifa_app()
            self.populate_doctordirectory_app()
            self.populate_evaluation_app()
            self.populate_araz_app()
            self.populate_photos_app()
            
            # Final summary
            self.print_section("DATA POPULATION COMPLETE")
            total_users = sum(len(users) for users in self.users.values())
            
            print("✅ SUMMARY:")
            print(f"   👥 Total Users: {total_users}")
            print(f"   🎓 Students: {len(self.users.get('student', []))}")
            print(f"   👨‍⚕️ Doctors: {len(self.users.get('doctor', []))}")
            print(f"   👤 Admins: {len(self.users.get('admin', []))}")
            print(f"   👷 Staff: {len(self.users.get('staff', []))}")
            print(f"   🕌 Moze Centers: {len(self.mozes)}")
            print(f"   🏥 Hospitals: {len(self.hospitals)}")
            print(f"   📋 Surveys: 10")
            print(f"   📄 Petitions: 100")
            print(f"   📚 Courses: {len(self.courses)}")
            print(f"   📸 Photo Albums: 10")
            
            print("\n🎉 ALL APPS SUCCESSFULLY POPULATED WITH TEST DATA!")
            print("🔐 Default passwords:")
            print("   - Admins: admin123")
            print("   - Doctors: doctor123") 
            print("   - Students: student123")
            print("   - Staff: staff123")
            print("   - Aamils: aamil123")
            print("   - Coordinators: coord123")
            
        except Exception as e:
            print(f"❌ Error during population: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    populator = DataPopulator()
    populator.run_population()