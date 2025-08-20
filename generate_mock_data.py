#!/usr/bin/env python
"""
Generate Mock ITS Data - Fixed Version

This script generates mock data for the Umoor Sehhat system including:
- 1000 users with different roles
- 100 Moze with Aamils and Coordinators  
- Medical records, Araiz, Surveys, Evaluations
- 5 Hospitals, 50 Mahal Shifa
- Proper role-based relationships

All generated users have password: pass1234
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

# Django imports
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

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

User = get_user_model()


class MockDataGenerator:
    """Generate comprehensive mock data for the system"""
    
    def __init__(self):
        self.admin_list = []
        self.aamil_list = []
        self.coordinator_list = []
        self.doctor_list = []
        self.student_list = []
        self.patient_list = []
        self.moze_list = []
        self.hospital_list = []
        self.mahal_shifa_list = []
        
        # Common data
        self.cities = ['Mumbai', 'Karachi', 'Houston', 'London', 'Dubai', 'Nairobi', 'Sydney']
        self.countries = ['India', 'Pakistan', 'USA', 'UK', 'UAE', 'Kenya', 'Australia']
        self.specialties = ['General Medicine', 'Pediatrics', 'Cardiology', 'Orthopedics', 'Gynecology', 
                           'Dermatology', 'ENT', 'Ophthalmology', 'Psychiatry', 'Dentistry']
        self.medical_conditions = ['Hypertension', 'Diabetes', 'Asthma', 'Arthritis', 'Migraine', 
                                  'Allergies', 'Back Pain', 'Anxiety', 'Depression', 'Insomnia']
        self.symptoms = ['Fever', 'Cough', 'Headache', 'Fatigue', 'Nausea', 'Dizziness', 
                        'Chest Pain', 'Shortness of Breath', 'Joint Pain', 'Skin Rash']
        
    def _create_user(self, its_id, role_hint=None):
        """Create a user with ITS authentication"""
        try:
            # Check if user already exists
            existing_user = User.objects.filter(its_id=its_id).first()
            if existing_user:
                print(f"  → User {its_id} already exists")
                return existing_user
                
            # Simulate ITS authentication to get user data and role
            auth_result = ITSService.authenticate_user(its_id, 'pass1234')
            if not auth_result or not auth_result.get('authenticated'):
                print(f"  ✗ Failed to authenticate ITS ID: {its_id}")
                return None
            
            user_data = auth_result.get('user_data', {})
            role = auth_result.get('role', 'patient')
            
            # Create user
            user = User.objects.create(
                its_id=its_id,
                username=its_id,
                first_name=user_data.get('first_name', ''),
                last_name=user_data.get('last_name', ''),
                email=user_data.get('email', ''),
                arabic_full_name=user_data.get('arabic_full_name', ''),
                prefix=user_data.get('prefix', ''),
                age=user_data.get('age'),
                gender=user_data.get('gender'),
                marital_status=user_data.get('marital_status'),
                misaq=user_data.get('misaq', ''),
                occupation=user_data.get('occupation', ''),
                qualification=user_data.get('qualification', ''),
                idara=user_data.get('idara', ''),
                category=user_data.get('category', ''),
                organization=user_data.get('organization', ''),
                mobile_number=user_data.get('mobile_number', ''),
                whatsapp_number=user_data.get('whatsapp_number', ''),
                address=user_data.get('address', ''),
                jamaat=user_data.get('jamaat', ''),
                jamiaat=user_data.get('jamiaat', ''),
                nationality=user_data.get('nationality', ''),
                vatan=user_data.get('vatan', ''),
                city=user_data.get('city', ''),
                country=user_data.get('country', ''),
                hifz_sanad=user_data.get('hifz_sanad', ''),
                profile_photo=user_data.get('photograph', ''),
                role=role,
                is_active=True
            )
            user.set_password('pass1234')
            user.save()
            
            print(f"  ✓ Created {role} user: {user.get_full_name()} ({its_id})")
            return user
            
        except Exception as e:
            print(f"  ✗ Error creating user {its_id}: {e}")
            return None
    
    def create_admin(self):
        """Create admin user"""
        print("\n[1/10] Creating Admin...")
        its_id = '10000001'
        user = self._create_user(its_id, 'admin')
        if user:
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.admin_list.append(user)
    
    def create_moze_with_aamils(self):
        """Create 100 Moze with Aamils"""
        print("\n[2/10] Creating 100 Moze with Aamils...")
        
        for i in range(100):
            # Create Aamil
            its_id = f"{10000002 + i:08d}"
            aamil = self._create_user(its_id, 'aamil')
            
            if aamil:
                self.aamil_list.append(aamil)
                
                # Create Moze
                city = random.choice(self.cities)
                moze = Moze.objects.create(
                    name=f"{city} Moze {i+1:03d}",
                    location=f"Area {i+1}, {city}",
                    aamil=aamil,
                    established_date=date.today() - timedelta(days=random.randint(365, 3650)),
                    is_active=True,
                    capacity=random.randint(50, 200),
                    contact_phone=f"+1234567{i:04d}",
                    contact_email=f"moze{i+1}@example.com"
                )
                
                # Set ITS ID for the moze
                moze.its_id = f"M{i+1:06d}"
                moze.save()
                
                self.moze_list.append(moze)
                print(f"  ✓ Created Moze: {moze.name} with Aamil: {aamil.get_full_name()}")
    
    def create_coordinators(self):
        """Create Moze Coordinators"""
        print("\n[3/10] Creating Moze Coordinators...")
        
        # Add coordinator ITS IDs to the service first
        coordinator_its_ids = []
        for i in range(100):
            its_id = f"{10000102 + i:08d}"
            coordinator_its_ids.append(its_id)
            user = self._create_user(its_id, 'coordinator')
            if user and i < len(self.moze_list):
                # Assign coordinator to moze
                moze = self.moze_list[i]
                moze.moze_coordinator = user
                moze.save()
                self.coordinator_list.append(user)
        
        # Add coordinator ITS IDs to the service
        ITSService.add_coordinator_its_ids(coordinator_its_ids)
        
    def create_doctors(self):
        """Create 50 Doctors"""
        print("\n[4/10] Creating 50 Doctors...")
        
        for i in range(50):
            its_id = f"{10000202 + i:08d}"
            user = self._create_user(its_id, 'doctor')
            
            if user:
                # Create Doctor profile
                doctor = Doctor.objects.create(
                    user=user,
                    name=user.get_full_name(),
                    its_id=its_id,
                    specialty=random.choice(self.specialties),
                    qualification=f"MBBS, MD ({random.choice(self.specialties)})",
                    experience_years=random.randint(5, 25),
                    consultation_fee=Decimal(random.randint(100, 500)),
                    is_available=True,
                    is_verified=True,
                    assigned_moze=random.choice(self.moze_list) if self.moze_list else None,
                    languages_spoken="English, Urdu, Gujarati"
                )
                
                # Create medical services
                for j in range(random.randint(2, 5)):
                    MedicalService.objects.create(
                        doctor=doctor,
                        name=f"Service {j+1} - {doctor.specialty}",
                        description=f"Professional medical service",
                        price=Decimal(random.randint(50, 300)),
                        duration_minutes=random.choice([15, 30, 45, 60])
                    )
                
                # Create schedule for next 30 days
                for day_offset in range(30):
                    schedule_date = date.today() + timedelta(days=day_offset)
                    # Skip weekends (Saturday=5, Sunday=6)
                    if schedule_date.weekday() < 5 and random.random() > 0.2:  # 80% chance of working on weekdays
                        DoctorSchedule.objects.create(
                            doctor=doctor,
                            date=schedule_date,
                            start_time=datetime.strptime('09:00', '%H:%M').time(),
                            end_time=datetime.strptime('17:00', '%H:%M').time(),
                            is_available=True,
                            max_patients=random.randint(10, 20)
                        )
                
                self.doctor_list.append(doctor)
                print(f"  ✓ Created Doctor: Dr. {doctor.name} ({doctor.specialty})")
    
    def create_students(self):
        """Create 200 Students"""
        print("\n[5/10] Creating 200 Students...")
        
        # Add student ITS IDs to the service first
        student_its_ids = []
        for i in range(200):
            its_id = f"{10000252 + i:08d}"
            student_its_ids.append(its_id)
        
        ITSService.add_student_its_ids(student_its_ids)
        
        # Create courses first
        courses = []
        course_names = ['Quran Studies', 'Arabic Language', 'Islamic History', 'Fiqh', 'Hadith Studies']
        for name in course_names:
            course = Course.objects.create(
                name=name,
                code=f"CRS{len(courses)+1:03d}",
                credits=3,
                level=random.choice(['beginner', 'intermediate', 'advanced']),
                instructor=random.choice(self.aamil_list) if self.aamil_list else None
            )
            courses.append(course)
        
        # Create students
        for i in range(200):
            its_id = student_its_ids[i]
            user = self._create_user(its_id, 'student')
            
            if user:
                # Create Student profile
                student = Student.objects.create(
                    user=user,
                    student_id=f"STD{i+1:06d}",
                    academic_level=random.choice(['undergraduate', 'postgraduate']),
                    enrollment_status='active',
                    enrollment_date=date.today() - timedelta(days=random.randint(30, 1460)),
                    expected_graduation=date.today() + timedelta(days=random.randint(365, 1460))
                )
                
                # Enroll in courses
                for course in random.sample(courses, min(random.randint(2, 4), len(courses))):
                    enrollment = Enrollment.objects.create(
                        student=student,
                        course=course,
                        status=random.choice(['enrolled', 'completed']),
                        grade=random.choice(['A', 'B', 'C', 'D', '']) if random.random() > 0.3 else ''
                    )
                    # Set enrolled_date to match student enrollment
                    enrollment.enrolled_date = student.enrollment_date
                    enrollment.save()
                
                self.student_list.append(student)
                print(f"  ✓ Created Student: {user.get_full_name()} - {student.academic_level}")
    
    def create_patients(self):
        """Create 550 Patients"""
        print("\n[6/10] Creating 550 Patients...")
        
        blood_groups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
        
        for i in range(550):
            its_id = f"{10000452 + i:08d}"
            user = self._create_user(its_id, 'patient')
            
            if user:
                # Create Patient profile
                patient = Patient.objects.create(
                    user=user,
                    date_of_birth=date.today() - timedelta(days=random.randint(6570, 29200)),  # 18-80 years
                    gender=random.choice(['male', 'female']),
                    blood_group=random.choice(blood_groups),
                    emergency_contact=f"+1234568{i:04d}",
                    medical_history=random.choice(self.medical_conditions) if random.random() > 0.5 else '',
                    allergies='None' if random.random() > 0.3 else random.choice(['Peanuts', 'Dust', 'Pollen']),
                    current_medications=random.choice(['None', 'Aspirin', 'Metformin', 'Lisinopril']) if random.random() > 0.5 else ''
                )
                
                self.patient_list.append(patient)
                print(f"  ✓ Created Patient: {user.get_full_name()} ({patient.blood_group})")
    
    def create_hospitals_and_mahal_shifa(self):
        """Create 5 Hospitals and departments"""
        print("\n[7/10] Creating 5 Hospitals...")
        
        hospital_names = ['City General Hospital', 'Regional Medical Center', 'Community Hospital', 
                         'District Hospital', 'Central Medical Institute']
        
        for i, name in enumerate(hospital_names):
            city = random.choice(self.cities)
            hospital = Hospital.objects.create(
                name=name,
                address=f"Main Street {i+1}, {city}",
                phone=f"+1234569{i:04d}",
                email=f"hospital{i+1}@example.com",
                hospital_type=random.choice(['general', 'specialty', 'clinic']),
                total_beds=random.randint(50, 200),
                available_beds=random.randint(20, 100),
                emergency_beds=random.randint(5, 20),
                icu_beds=random.randint(5, 15),
                is_active=True,
                is_emergency_capable=random.choice([True, False]),
                has_pharmacy=random.choice([True, False])
            )
            
            # Create departments
            dept_names = ['Emergency', 'Outpatient', 'Inpatient', 'Surgery', 'Pediatrics']
            for dept_name in dept_names:
                Department.objects.create(
                    hospital=hospital,
                    name=dept_name,
                    head_of_department=f"Dr. {dept_name} Head",
                    contact_number=f"+1234570{i:04d}",
                    is_active=True
                )
            
            # Assign some doctors as hospital staff
            for j, doctor in enumerate(random.sample(self.doctor_list, min(5, len(self.doctor_list)))):
                if doctor.user:
                    HospitalStaff.objects.create(
                        user=doctor.user,
                        hospital=hospital,
                        department=hospital.departments.first(),
                        staff_type='other',  # Doctors are marked as 'other' staff type
                        employee_id=f"EMP{hospital.id:03d}{j+1:03d}",
                        shift=random.choice(['morning', 'evening', 'rotating']),
                        is_active=True,
                        hire_date=date.today() - timedelta(days=random.randint(30, 730))
                    )
            
            self.hospital_list.append(hospital)
            print(f"  ✓ Created Hospital: {hospital.name} in {city}")
    
    def create_medical_records(self):
        """Create medical records and patient logs"""
        print("\n[8/10] Creating Medical Records...")
        
        record_count = 0
        for patient in random.sample(self.patient_list, min(200, len(self.patient_list))):
            # Create 1-5 medical records per patient
            for _ in range(random.randint(1, 5)):
                doctor = random.choice(self.doctor_list) if self.doctor_list else None
                moze = random.choice(self.moze_list) if self.moze_list else None
                
                if doctor and moze:
                    log = PatientLog.objects.create(
                        patient_its_id=patient.user.its_id if patient.user else '12345678',
                        patient_name=patient.user.get_full_name() if patient.user else 'Unknown Patient',
                        ailment=random.choice(self.medical_conditions),
                        symptoms=', '.join(random.sample(self.symptoms, random.randint(1, 3))),
                        diagnosis=f"Diagnosed with {random.choice(self.medical_conditions)}",
                        prescription=f"Medicine {random.randint(1, 10)} - {random.choice(['Twice', 'Thrice'])} daily",
                        follow_up_required=random.random() > 0.5,
                        follow_up_date=date.today() + timedelta(days=random.randint(7, 30)) if random.random() > 0.5 else None,
                        visit_type=random.choice(['consultation', 'follow_up', 'emergency']),
                        moze=moze,
                        seen_by=doctor,
                        timestamp=timezone.now() - timedelta(days=random.randint(1, 365))
                    )
                    record_count += 1
        
        print(f"  ✓ Created {record_count} medical records")
    
    def create_araiz_petitions(self):
        """Create Araiz (Petitions)"""
        print("\n[9/10] Creating Araiz (Petitions)...")
        
        petition_types = ['medical_assistance', 'financial_aid', 'educational_support', 
                         'housing_assistance', 'general_welfare']
        
        petition_count = 0
        for moze in random.sample(self.moze_list, min(50, len(self.moze_list))):
            # Create 1-10 petitions per moze
            for _ in range(random.randint(1, 10)):
                petitioner = random.choice(self.patient_list + self.student_list)
                
                petition = Petition.objects.create(
                    moze=moze,
                    petition_type=random.choice(petition_types),
                    description=f"Request for {random.choice(petition_types).replace('_', ' ')}",
                    submitted_by=petitioner.user if hasattr(petitioner, 'user') else None,
                    petitioner_name=petitioner.user.get_full_name() if hasattr(petitioner, 'user') else 'Anonymous',
                    petitioner_its_id=petitioner.user.its_id if hasattr(petitioner, 'user') else '',
                    amount_requested=Decimal(random.randint(1000, 50000)) if random.random() > 0.5 else None,
                    amount_approved=Decimal(random.randint(500, 30000)) if random.random() > 0.7 else None,
                    status=random.choice(['pending', 'under_review', 'approved', 'rejected']),
                    priority=random.choice(['low', 'medium', 'high', 'urgent'])
                )
                
                # Add status updates
                if petition.status != 'pending':
                    PetitionStatus.objects.create(
                        petition=petition,
                        status=petition.status,
                        updated_by=moze.aamil,
                        comments=f"Reviewed and {petition.status}"
                    )
                
                petition_count += 1
        
        print(f"  ✓ Created {petition_count} petitions")
    
    def create_surveys_and_evaluations(self):
        """Create surveys and evaluations"""
        print("\n[10/10] Creating Surveys and Evaluations...")
        
        # Create surveys
        survey_count = 0
        for aamil in random.sample(self.aamil_list, min(10, len(self.aamil_list))):
            # Create questions as JSON
            questions = [
                {
                    'id': 1,
                    'text': 'How satisfied are you with our medical services?',
                    'type': 'rating',
                    'required': True,
                    'options': ['1', '2', '3', '4', '5']
                },
                {
                    'id': 2,
                    'text': 'How would you rate the doctor\'s consultation?',
                    'type': 'rating',
                    'required': True,
                    'options': ['1', '2', '3', '4', '5']
                },
                {
                    'id': 3,
                    'text': 'Was the appointment booking process easy?',
                    'type': 'rating',
                    'required': True,
                    'options': ['1', '2', '3', '4', '5']
                },
                {
                    'id': 4,
                    'text': 'Would you recommend our services to others?',
                    'type': 'rating',
                    'required': True,
                    'options': ['1', '2', '3', '4', '5']
                },
                {
                    'id': 5,
                    'text': 'Any suggestions for improvement?',
                    'type': 'text',
                    'required': False
                }
            ]
            
            survey = Survey.objects.create(
                title=f"Health & Wellness Survey {survey_count+1}",
                description="Please share your feedback about our health services",
                questions=questions,
                created_by=aamil,
                start_date=date.today() - timedelta(days=random.randint(30, 90)),
                end_date=date.today() + timedelta(days=random.randint(30, 90)),
                is_active=True,
                is_anonymous=random.random() > 0.5
            )
            
            # Create responses
            respondents = random.sample(self.patient_list + self.student_list, 
                                      min(20, len(self.patient_list + self.student_list)))
            
            for respondent in respondents:
                if hasattr(respondent, 'user'):
                    # Create response data
                    response_data = {}
                    for q in questions:
                        if q['type'] == 'rating':
                            response_data[str(q['id'])] = str(random.randint(1, 5))
                        else:
                            response_data[str(q['id'])] = f"Sample feedback from {respondent.user.get_full_name()}"
                    
                    SurveyResponse.objects.create(
                        survey=survey,
                        respondent=respondent.user,
                        responses=response_data,
                        submitted_at=timezone.now() - timedelta(days=random.randint(1, 30))
                    )
            
            survey_count += 1
        
        print(f"  ✓ Created {survey_count} surveys with responses")
        
        # Create evaluations
        criteria_list = []
        criteria_names = ['Academic Performance', 'Class Participation', 'Attendance', 'Behavior', 'Assignment Quality']
        
        for name in criteria_names:
            criteria = EvaluationCriteria.objects.create(
                name=name,
                description=f"Evaluation of student's {name.lower()}",
                weight=20.0,
                is_active=True
            )
            criteria_list.append(criteria)
        
        # Create student evaluations
        evaluation_count = 0
        students = random.sample(self.student_list, min(100, len(self.student_list)))
        evaluators = self.aamil_list + self.coordinator_list
        
        for student in students:
            if student.user and evaluators:
                evaluation = Evaluation.objects.create(
                    evaluatee=student.user,
                    evaluator=random.choice(evaluators),
                    evaluation_type='student_performance',
                    title=f"Term Evaluation for {student.user.get_full_name()}",
                    description="Regular academic performance evaluation",
                    period_start=date.today() - timedelta(days=90),
                    period_end=date.today(),
                    overall_rating=random.randint(3, 5),
                    overall_score=random.randint(60, 100),
                    status='completed',
                    completed_date=date.today() - timedelta(days=random.randint(1, 30))
                )
                
                evaluation.evaluator_comments = f"Student shows {random.choice(['excellent', 'good', 'satisfactory'])} progress"
                evaluation.save()
                
                evaluation_count += 1
        
        print(f"  ✓ Created {evaluation_count} student evaluations")
    
    @transaction.atomic
    def generate_all_data(self):
        """Generate all mock data in proper order"""
        print("\n" + "="*80)
        print("UMOOR SEHHAT - MOCK DATA GENERATION")
        print("="*80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        try:
            # Generate data in dependency order
            self.create_admin()
            self.create_moze_with_aamils()
            self.create_coordinators()
            self.create_doctors()
            self.create_students()
            self.create_patients()
            self.create_hospitals_and_mahal_shifa()
            self.create_medical_records()
            self.create_araiz_petitions()
            self.create_surveys_and_evaluations()
            
            # Print summary
            print("\n" + "="*80)
            print("GENERATION COMPLETE - SUMMARY")
            print("="*80)
            print(f"Admin Users: {len(self.admin_list)}")
            print(f"Aamils: {len(self.aamil_list)}")
            print(f"Coordinators: {len(self.coordinator_list)}")
            print(f"Doctors: {len(self.doctor_list)}")
            print(f"Students: {len(self.student_list)}")
            print(f"Patients: {len(self.patient_list)}")
            print(f"Moze: {len(self.moze_list)}")
            print(f"Hospitals: {len(self.hospital_list)}")
            print("="*80)
            print("\nAll users password: pass1234")
            print("\nExample logins:")
            print(f"  Admin: 10000001 / pass1234")
            print(f"  Aamil: 10000002 / pass1234")
            print(f"  Coordinator: 10000102 / pass1234")
            print(f"  Doctor: 10000202 / pass1234")
            print(f"  Student: 10000252 / pass1234")
            print(f"  Patient: 10000452 / pass1234")
            print("="*80)
            print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*80)
            
        except Exception as e:
            print(f"\n✗ Error during generation: {e}")
            import traceback
            traceback.print_exc()
            raise


def main():
    """Main function"""
    print("\nThis will generate comprehensive mock data for the Umoor Sehhat system.")
    print("WARNING: This should only be run on a development/test database!")
    
    confirm = input("\nProceed with data generation? (yes/no): ")
    
    if confirm.lower() == 'yes':
        generator = MockDataGenerator()
        generator.generate_all_data()
    else:
        print("Data generation cancelled.")


if __name__ == '__main__':
    main()