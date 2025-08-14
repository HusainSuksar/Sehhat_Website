#!/usr/bin/env python3
"""
Simplified Data Population Script for Umoor Sehhat
Creates users and basic data without problematic models
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

# Import models that work
from accounts.models import User
from moze.models import Moze
from students.models import Student, Course
from mahalshifa.models import Hospital, Department, MedicalService
from araz.models import Petition, PetitionCategory
from surveys.models import Survey
from photos.models import PhotoAlbum
from evaluation.models import EvaluationForm

User = get_user_model()

class SimpleDataPopulator:
    """Simplified data populator focusing on working models"""
    
    def __init__(self):
        self.created_users = []
        self.created_mozes = []
        self.created_hospitals = []
        self.created_services = []
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
        
        self.cities = [
            'Mumbai', 'Delhi', 'Karachi', 'Dubai', 'London', 'New York', 'Ahmedabad', 
            'Pune', 'Bangalore', 'Chennai', 'Hyderabad', 'Kolkata', 'Jaipur', 'Lucknow',
            'Kanpur', 'Nagpur', 'Indore', 'Thane', 'Bhopal', 'Patna', 'Vadodara'
        ]
        
        self.countries = [
            'India', 'Pakistan', 'UAE', 'UK', 'USA', 'Canada', 'Australia', 'Germany',
            'France', 'Singapore', 'Malaysia', 'Saudi Arabia', 'Qatar', 'Kuwait'
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
        
        print(f"✅ Successfully created {len(self.created_users)} users in MOCKITS")
    
    def create_mozes_and_hospitals(self):
        """Create mozes and hospitals"""
        print("🏢 Creating mozes and hospitals...")
        
        # Get aamils for moze creation
        aamils = [u['user'] for u in self.created_users if u['role'] == 'aamil']
        coordinators = [u['user'] for u in self.created_users if u['role'] == 'moze_coordinator']
        
        # Create 20 mozes
        for i in range(20):
            city = random.choice(self.cities)
            country = random.choice(self.countries)
            
            moze = Moze.objects.create(
                name=f"Moze {chr(65 + i // 2)}{i % 2 + 1} - {city}",
                location=f"{city}, {country}",
                address=f"Address {i+1}, {city}, {country}",
                contact_phone=f"+91{random.randint(6000000000, 9999999999)}",
                contact_email=f"moze{i+1}@example.com",
                aamil=aamils[i] if i < len(aamils) else aamils[0],
                moze_coordinator=coordinators[i] if i < len(coordinators) else coordinators[0],
                capacity=random.randint(100, 500),
                established_date=timezone.now().date() - timedelta(days=random.randint(365, 1825)),
                is_active=True
            )
            
            self.created_mozes.append(moze)
            self.log_creation("Moze", f"{moze.name}")
        
        # Create hospitals and departments
        hospital_names = [
            'City General Hospital', 'Central Medical Center', 'Community Health Hospital',
            'Regional Medical Center', 'Specialty Care Hospital', 'Emergency Care Center'
        ]
        
        department_names = [
            'General Medicine', 'Cardiology', 'Pediatrics', 'Gynecology', 'Orthopedics',
            'Dermatology', 'Neurology', 'Psychiatry', 'Ophthalmology', 'ENT', 'Dental',
            'Surgery', 'Emergency Medicine', 'Internal Medicine', 'Family Medicine'
        ]
        
        for i, name in enumerate(hospital_names):
            city = random.choice(self.cities)
            country = random.choice(self.countries)
            
            hospital = Hospital.objects.create(
                name=f"{name} - {city}",
                description=f"Comprehensive healthcare facility in {city}",
                address=f"Hospital Address {i+1}, {city}, {country}",
                phone=f"+91{random.randint(6000000000, 9999999999)}",
                email=f"hospital{i+1}@example.com",
                hospital_type=random.choice(['general', 'specialty', 'clinic', 'emergency', 'rehabilitation']),
                total_beds=random.randint(50, 200),
                available_beds=random.randint(10, 100),
                emergency_beds=random.randint(5, 20),
                icu_beds=random.randint(2, 10),
                is_active=True,
                is_emergency_capable=random.choice([True, False]),
                has_pharmacy=random.choice([True, False]),
                has_laboratory=random.choice([True, False])
            )
            
            self.created_hospitals.append(hospital)
            self.log_creation("Hospital", f"{hospital.name}")
            
            # Create departments for this hospital
            hospital_departments = []
            for j, dept_name in enumerate(random.sample(department_names, random.randint(3, 8))):
                department = Department.objects.create(
                    hospital=hospital,
                    name=dept_name,
                    description=f"Department of {dept_name} at {hospital.name}",
                    floor_number=str(random.randint(1, 5)),
                    phone_extension=str(random.randint(100, 999)),
                    is_active=True
                )
                hospital_departments.append(department)
            
            # Store departments for later use
            hospital.departments_list = hospital_departments
        
        print(f"✅ Created {len(self.created_mozes)} mozes and {len(self.created_hospitals)} hospitals with departments")
    
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
        
        for service_data in services:
            service = MedicalService.objects.create(
                name=service_data['name'],
                description=f"Professional {service_data['name'].lower()} service",
                category=service_data['category'],
                duration_minutes=service_data['duration'],
                cost=Decimal(service_data['cost']),
                is_active=True
            )
            self.created_services.append(service)
            self.log_creation("Medical Service", f"{service.name}")
        
        print(f"✅ Created {len(self.created_services)} medical services")
    
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
                created_by=petitioner['user'],
                petitioner_name=petitioner['user'].get_full_name(),
                petitioner_mobile=f"+91{random.randint(6000000000, 9999999999)}",
                petitioner_email=petitioner['user'].email,
                its_id=petitioner['user'].its_id,
                moze=moze,
                category=category,
                priority=random.choice(['low', 'medium', 'high']),
                status=random.choice(['pending', 'in_progress', 'resolved', 'rejected'])
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
                created_by=creator['user'],
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
                name=f"Album {i+1}: {random.choice(['Community Event', 'Health Camp', 'Educational Program', 'Social Gathering', 'Religious Ceremony'])}",
                description=f"Photos from {random.choice(['recent', 'annual', 'special', 'community'])} {random.choice(['event', 'program', 'celebration', 'gathering'])} in {moze.name}.",
                created_by=creator['user'],
                moze=moze,
                is_public=random.choice([True, False]),
                allow_uploads=random.choice([True, False]),
                event_date=timezone.now().date() - timedelta(days=random.randint(1, 365)) if random.choice([True, False]) else None
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
                evaluation_type=random.choice(['performance', 'satisfaction', 'quality', 'training', 'service', 'facility']),
                target_role=random.choice(['all', 'doctor', 'student', 'aamil', 'moze_coordinator', 'admin']),
                created_by=creator['user'],
                is_active=True,
                is_anonymous=random.choice([True, False]),
                due_date=timezone.now() + timedelta(days=random.randint(30, 90)) if random.choice([True, False]) else None
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
        for i, course_name in enumerate(courses):
            course, created = Course.objects.get_or_create(
                name=course_name,
                defaults={
                    'code': f'COURSE{i+1:03d}',
                    'description': f'Course in {course_name}',
                    'credits': random.randint(2, 6),
                    'level': random.choice(['beginner', 'intermediate', 'advanced']),
                    'is_active': True
                }
            )
            created_courses.append(course)
        
        # Create student profiles
        student_users = [u for u in self.created_users if u['role'] == 'student']
        for i, user_data in enumerate(student_users):
            student = Student.objects.create(
                user=user_data['user'],
                student_id=f"STU{user_data['user'].its_id}",
                academic_level=random.choice(['undergraduate', 'postgraduate', 'doctoral', 'diploma']),
                enrollment_status=random.choice(['active', 'suspended', 'graduated', 'withdrawn']),
                enrollment_date=timezone.now().date() - timedelta(days=random.randint(30, 365)),
                expected_graduation=timezone.now().date() + timedelta(days=random.randint(30, 730)) if random.choice([True, False]) else None
            )
            
            self.log_creation("Student Profile", f"{student.user.get_full_name()} - {student.student_id}")
        
        print(f"✅ Created {len(student_users)} student profiles")
    
    def generate_comprehensive_report(self):
        """Generate comprehensive data report"""
        print("\n" + "="*80)
        print("📊 SIMPLIFIED DATA POPULATION REPORT")
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
        print(f"   Medical Services: {len(self.created_services)}")
        
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
        
        print(f"\n✅ SIMPLIFIED DATA POPULATION COMPLETED SUCCESSFULLY!")
        print("="*80)
    
    def run_comprehensive_population(self):
        """Run the complete data population process"""
        print("🚀 Starting simplified data population...")
        
        try:
            with transaction.atomic():
                # Create users in MOCKITS
                self.create_mock_its_users()
                
                # Create infrastructure
                self.create_mozes_and_hospitals()
                
                # Create medical services
                self.create_medical_services()
                
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
    print("🏥 SIMPLIFIED DATA POPULATION FOR UMOOR SEHHAT")
    print("="*60)
    
    populator = SimpleDataPopulator()
    populator.run_comprehensive_population()

if __name__ == "__main__":
    main()