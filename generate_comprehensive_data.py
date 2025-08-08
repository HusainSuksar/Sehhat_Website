#!/usr/bin/env python3
"""
Comprehensive Data Generation Script
Creates 50 users with proper role distribution and all related data:
- 1 Admin
- 20 Students  
- 15 Doctors
- 8 Aamils (matching 8 Moze)
- 6 Patients
- 5 Surveys (10 questions each)
- 5 Evaluation Forms (8 questions each)
- Medical records, photos, analytics data
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta, date
import random

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import User
from accounts.services import MockITSService
from django.utils import timezone

# Import all models
from moze.models import Moze, UmoorSehhatTeam
from students.models import Student, Course, Submission
from doctordirectory.models import Doctor, Patient, Appointment, MedicalRecord, Prescription
from mahalshifa.models import Doctor as MahalShifaDoctor, Hospital, Patient as MahalShifaPatient, Department
from surveys.models import Survey, SurveyResponse
from evaluation.models import EvaluationForm, EvaluationSubmission, EvaluationResponse, EvaluationCriteria
from photos.models import PhotoAlbum, Photo
from araz.models import Petition

class ComprehensiveDataGenerator:
    def __init__(self):
        self.created_users = []
        self.admin_user = None
        self.students = []
        self.doctors = []
        self.aamils = []
        self.patients = []
        self.mozes = []
        self.hospitals = []
        
    def generate_users(self):
        """Generate 50 users with proper role distribution"""
        print("🔧 Creating 50 users with ITS profile data...")
        
        # Check if users already exist
        if User.objects.count() > 45:  # 50 users + anonymous
            print("   Users already exist, loading existing users...")
            self.admin_user = User.objects.filter(role='badri_mahal_admin').first()
            self.students = list(User.objects.filter(role='student'))
            self.doctors = list(User.objects.filter(role='doctor'))
            self.aamils = list(User.objects.filter(role='aamil'))
            self.patients = list(User.objects.filter(role='patient'))
            self.created_users = list(User.objects.all())
            
            print(f"✅ Loaded {len(self.created_users)} existing users")
            print(f"   - Admin: {1 if self.admin_user else 0}")
            print(f"   - Students: {len(self.students)}")
            print(f"   - Doctors: {len(self.doctors)}")
            print(f"   - Aamils: {len(self.aamils)}")
            print(f"   - Patients: {len(self.patients)}")
            return
        
        # User distribution
        roles_distribution = [
            ('badri_mahal_admin', 1),  # 1 Admin
            ('student', 20),           # 20 Students  
            ('doctor', 15),            # 15 Doctors
            ('aamil', 8),              # 8 Aamils
            ('patient', 6),            # 6 Patients
        ]
        
        user_counter = 50000001  # Start from a high number to avoid conflicts
        
        for role, count in roles_distribution:
            for i in range(count):
                # Generate ITS ID
                its_id = f"{user_counter:08d}"  # 8-digit ITS ID
                
                # Get ITS data from Mock API
                its_data = MockITSService.fetch_user_data(its_id)
                if not its_data:
                    print(f"⚠️  Warning: Could not fetch ITS data for {its_id}")
                    continue
                
                # Create user with ITS data  
                # Generate unique username
                base_username = its_data['email'].split('@')[0] if its_data['email'] else f"user_{its_id}"
                username = base_username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}_{counter}"
                    counter += 1
                
                user = User.objects.create_user(
                    username=username,
                    email=its_data['email'],
                    first_name=its_data['first_name'],
                    last_name=its_data['last_name'],
                    its_id=its_id,
                    role=role,
                    
                    # All 21 ITS fields
                    arabic_full_name=its_data.get('arabic_full_name', ''),
                    prefix=its_data.get('prefix', ''),
                    age=its_data.get('age'),
                    gender=its_data.get('gender', ''),
                    marital_status=its_data.get('marital_status', ''),
                    misaq=its_data.get('misaq', ''),
                    occupation=its_data.get('occupation', ''),
                    qualification=its_data.get('qualification', ''),
                    idara=its_data.get('idara', ''),
                    category=its_data.get('category', ''),
                    organization=its_data.get('organization', ''),
                    mobile_number=its_data.get('mobile_number', ''),
                    whatsapp_number=its_data.get('whatsapp_number', ''),
                    address=its_data.get('address', ''),
                    jamaat=its_data.get('jamaat', ''),
                    jamiaat=its_data.get('jamiaat', ''),
                    nationality=its_data.get('nationality', ''),
                    vatan=its_data.get('vatan', ''),
                    city=its_data.get('city', ''),
                    country=its_data.get('country', ''),
                    hifz_sanad=its_data.get('hifz_sanad', ''),
                    profile_photo=its_data.get('photograph', ''),
                    
                    is_active=True,
                    its_last_sync=timezone.now(),
                    its_sync_status='synced'
                )
                
                # Set superuser for admin
                if role == 'badri_mahal_admin':
                    user.is_superuser = True
                    user.is_staff = True
                    user.save()
                    self.admin_user = user
                
                self.created_users.append(user)
                
                # Categorize users
                if role == 'student':
                    self.students.append(user)
                elif role == 'doctor':
                    self.doctors.append(user)
                elif role == 'aamil':
                    self.aamils.append(user)
                elif role == 'patient':
                    self.patients.append(user)
                
                user_counter += 1
                
                if user_counter % 10 == 0:
                    print(f"   Created {user_counter-1} users...")
        
        print(f"✅ Created {len(self.created_users)} users total")
        print(f"   - Admin: {1}")
        print(f"   - Students: {len(self.students)}")
        print(f"   - Doctors: {len(self.doctors)}")
        print(f"   - Aamils: {len(self.aamils)}")
        print(f"   - Patients: {len(self.patients)}")
    
    def create_moze_structure(self):
        """Create 8 Moze with coordinators and team members"""
        print("\n🏛️ Creating Moze structure...")
        
        # Check if Moze already exist
        if Moze.objects.count() > 5:
            print("   Moze already exist, loading existing ones...")
            self.mozes = list(Moze.objects.all())
            print(f"✅ Loaded {len(self.mozes)} existing Moze")
            return
        
        moze_names = [
            "Mumbai Central Moze", "Karachi Moze", "London Moze", "New York Moze",
            "Dubai Moze", "Sydney Moze", "Toronto Moze", "Chicago Moze"
        ]
        
        for i, moze_name in enumerate(moze_names):
            # Create or get Moze
            moze, created = Moze.objects.get_or_create(
                name=moze_name,
                defaults={
                    'location': f"Location of {moze_name}",
                    'address': f"Address for {moze_name}",
                    'contact_phone': f"+1-555-{1000+i:04d}",
                    'contact_email': f"moze{i+1}@sehhat.com",
                    'established_date': date.today() - timedelta(days=random.randint(365, 3650)),
                    'capacity': random.randint(50, 200),
                    'aamil': self.aamils[i] if i < len(self.aamils) else self.admin_user,
                    'moze_coordinator': self.aamils[i] if i < len(self.aamils) else None
                }
            )
            self.mozes.append(moze)
            
            # Add team members (some doctors and students)
            team_members = (
                self.doctors[i*2:(i*2)+2] if i*2 < len(self.doctors) else []
            ) + (
                self.students[i*3:(i*3)+3] if i*3 < len(self.students) else []
            )
            
            # Create UmoorSehhatTeam entries for each member
            categories = ['medical', 'sports', 'nazafat', 'environment']
            for j, member in enumerate(team_members):
                category = categories[j % len(categories)]
                UmoorSehhatTeam.objects.create(
                    moze=moze,
                    member=member,
                    category=category,
                    position=f"{category.title()} Team Member",
                    contact_number=member.mobile_number or f"+1-555-{4000+j:04d}",
                    is_active=True
                )
                moze.team_members.add(member)  # Also add to Moze team members
        
        print(f"✅ Created {len(self.mozes)} Moze with coordinators and teams")
    
    def create_hospitals_and_medical_data(self):
        """Create hospitals and medical data"""
        print("\n🏥 Creating hospitals and medical data...")
        
        hospital_names = [
            "Saifee Hospital", "Al-Mustafa Medical Center", "Umoor Sehhat Clinic",
            "Bohra Community Hospital", "Central Medical Hub"
        ]
        
        for hospital_name in hospital_names:
            hospital = Hospital.objects.create(
                name=hospital_name,
                description=f"Medical facility providing comprehensive healthcare services",
                address=f"Address for {hospital_name}",
                phone=f"+1-555-{2000+len(self.hospitals):04d}",
                email=f"contact@{hospital_name.lower().replace(' ', '')}.com",
                hospital_type=random.choice(['general', 'specialty', 'clinic']),
                total_beds=random.randint(50, 300),
                available_beds=random.randint(10, 50),
                emergency_beds=random.randint(5, 20),
                icu_beds=random.randint(5, 15),
                is_active=True,
                is_emergency_capable=True,
                has_pharmacy=True,
                has_laboratory=True
            )
            self.hospitals.append(hospital)
        
        # Create Doctor profiles in DoctorDirectory
        specializations = ["Cardiology", "Neurology", "Orthopedics", "Pediatrics", "Dermatology", "Internal Medicine"]
        for i, doctor_user in enumerate(self.doctors):
            Doctor.objects.create(
                user=doctor_user,
                name=doctor_user.get_full_name(),
                its_id=doctor_user.its_id,
                specialty=random.choice(specializations),
                qualification=doctor_user.qualification or "MBBS",
                experience_years=random.randint(1, 25),
                license_number=f"DOC{1000+i:04d}",
                consultation_fee=Decimal(str(random.randint(100, 500))),
                is_verified=True,
                is_available=True,
                assigned_moze=random.choice(self.mozes) if self.mozes else None,
                phone=doctor_user.mobile_number,
                email=doctor_user.email,
                address=doctor_user.address
            )
        
        # Create departments for hospitals
        departments_data = [
            "Emergency", "Cardiology", "Neurology", "Orthopedics", 
            "Pediatrics", "Dermatology", "Internal Medicine", "Surgery"
        ]
        

        departments = []
        for hospital in self.hospitals:
            for dept_name in departments_data[:4]:  # 4 departments per hospital
                dept = Department.objects.create(
                    hospital=hospital,
                    name=dept_name,
                    description=f"{dept_name} department at {hospital.name}",
                    is_active=True
                )
                departments.append(dept)
        
        # Create MahalShifa Doctor profiles
        for i, doctor_user in enumerate(self.doctors[:10]):  # First 10 doctors in MahalShifa
            MahalShifaDoctor.objects.create(
                user=doctor_user,
                license_number=f"MSH{2000+i:04d}",
                specialization=random.choice(specializations),
                qualification=doctor_user.qualification or "MBBS",
                experience_years=random.randint(1, 30),
                hospital=random.choice(self.hospitals),
                department=random.choice(departments),
                is_available=True,
                is_emergency_doctor=random.choice([True, False])
            )
        
        # Create Patient profiles
        for i, patient_user in enumerate(self.patients):
            gender_mapping = {'male': 'M', 'female': 'F', 'other': 'O'}
            gender = gender_mapping.get(patient_user.gender.lower() if patient_user.gender else 'other', 'O')
            
            Patient.objects.create(
                user=patient_user,
                date_of_birth=date.today() - timedelta(days=random.randint(6570, 25550)),  # 18-70 years
                gender=gender,
                blood_group=random.choice(['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']),
                emergency_contact=f"+1-555-{3000+i:04d}",
                medical_history=f"Medical history for patient {i+1}",
                allergies="None known" if random.random() > 0.3 else "Seasonal allergies",
                current_medications="None" if random.random() > 0.4 else "Multivitamins"
            )
            
            # Also create MahalShifa patient
            MahalShifaPatient.objects.create(
                its_id=patient_user.its_id,
                first_name=patient_user.first_name,
                last_name=patient_user.last_name,
                arabic_name=patient_user.arabic_full_name or "",
                date_of_birth=date.today() - timedelta(days=random.randint(6570, 25550)),
                gender=patient_user.gender.lower() if patient_user.gender else 'other',
                blood_group=random.choice(['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']),
                phone=patient_user.mobile_number or f"+1-555-{3100+i:04d}",
                email=patient_user.email,
                address=patient_user.address or f"Address for patient {i+1}",
                emergency_contact=f"+1-555-{3100+i:04d}",
                medical_history=f"Patient {i+1} medical history notes"
            )
        
        print(f"✅ Created {len(self.hospitals)} hospitals")
        print(f"✅ Created {len(self.doctors)} doctor profiles")
        print(f"✅ Created {len(self.patients)} patient profiles")
    
    def create_medical_records(self):
        """Create medical records and appointments"""
        print("\n📋 Creating medical records and appointments...")
        
        doctors = Doctor.objects.all()
        patients = Patient.objects.all()
        
        # Create appointments
        appointment_count = 0
        for i in range(30):  # 30 appointments
            doctor = random.choice(doctors)
            patient = random.choice(patients)
            
            appointment_date = timezone.now() - timedelta(days=random.randint(1, 90))
            
            appointment = Appointment.objects.create(
                doctor=doctor,
                patient=patient,
                appointment_date=appointment_date,
                appointment_time=f"{random.randint(9, 17):02d}:{random.choice(['00', '30'])}",
                status=random.choice(['scheduled', 'completed', 'cancelled']),
                notes=f"Appointment {i+1} notes"
            )
            appointment_count += 1
            
            # Create medical record for completed appointments
            if appointment.status == 'completed':
                MedicalRecord.objects.create(
                    patient=patient,
                    doctor=doctor,
                    diagnosis=f"Diagnosis for appointment {i+1}",
                    treatment=f"Treatment prescribed for patient",
                    notes=f"Medical notes for completed appointment {i+1}",
                    created_at=appointment_date
                )
        
        print(f"✅ Created {appointment_count} appointments and medical records")
    
    def create_student_data(self):
        """Create student courses and submissions"""
        print("\n🎓 Creating student courses and submissions...")
        
        # Create courses
        course_names = [
            "Introduction to Islamic Medicine", "Anatomy and Physiology", 
            "Medical Ethics", "Community Health", "Pharmacology Basics"
        ]
        
        courses = []
        for course_name in course_names:
            course = Course.objects.create(
                name=course_name,
                code=f"COURSE{len(courses)+1:03d}",
                credits=random.randint(2, 4),
                description=f"Description for {course_name}",
                instructor=random.choice(self.doctors) if self.doctors else self.admin_user
            )
            courses.append(course)
        
        # Create Student profiles
        for i, student_user in enumerate(self.students):
            Student.objects.create(
                user=student_user,
                student_id=f"STU{1000+i:04d}",
                course=random.choice(courses),
                year=random.randint(1, 4),
                gpa=round(random.uniform(2.5, 4.0), 2),
                enrollment_date=date.today() - timedelta(days=random.randint(30, 1000)),
                assigned_moze=random.choice(self.mozes) if self.mozes else None
            )
        
        # Create submissions
        students = Student.objects.all()
        for i in range(40):  # 40 submissions
            student = random.choice(students)
            submission = Submission.objects.create(
                student=student,
                title=f"Assignment {i+1}",
                description=f"Description for assignment {i+1}",
                course=student.course,
                submitted_at=timezone.now() - timedelta(days=random.randint(1, 60)),
                grade=random.choice(['A', 'B', 'C', 'D', 'F']) if random.random() > 0.3 else None
            )
        
        print(f"✅ Created {len(courses)} courses and student data")
    
    def create_surveys(self):
        """Create 5 surveys with 10 questions each using JSON structure"""
        print("\n📊 Creating 5 surveys with 10 questions each...")
        
        survey_titles = [
            "Community Health Assessment",
            "Healthcare Service Satisfaction",
            "Medical Education Feedback",
            "Nutrition and Wellness Survey",
            "Mental Health Awareness"
        ]
        
        question_templates = [
            "How would you rate {}?",
            "What is your experience with {}?", 
            "How satisfied are you with {}?",
            "How important is {} to you?",
            "What improvements would you suggest for {}?"
        ]
        
        topics = [
            "healthcare services", "medical facilities", "doctor consultations",
            "medication availability", "health education", "preventive care",
            "emergency services", "community support", "health awareness",
            "wellness programs"
        ]
        
        for survey_title in survey_titles:
            # Create 10 questions in JSON format
            questions_data = []
            for i in range(10):
                question_text = random.choice(question_templates).format(random.choice(topics))
                question_type = random.choice(['multiple_choice', 'text', 'rating', 'yes_no'])
                
                question_data = {
                    'id': i + 1,
                    'text': question_text,
                    'type': question_type,
                    'required': random.choice([True, False])
                }
                
                # Add choices for multiple choice questions
                if question_type == 'multiple_choice':
                    question_data['choices'] = ["Excellent", "Good", "Fair", "Poor"]
                elif question_type == 'rating':
                    question_data['max_rating'] = 5
                
                questions_data.append(question_data)
            
            survey = Survey.objects.create(
                title=survey_title,
                description=f"Comprehensive survey about {survey_title.lower()}",
                created_by=self.admin_user,
                start_date=timezone.now(),
                end_date=timezone.now() + timedelta(days=30),
                is_active=True,
                is_anonymous=True,
                questions=questions_data
            )
            
            # Create survey responses
            respondents = random.sample(self.created_users, min(15, len(self.created_users)))
            for respondent in respondents:
                # Create answers for each question
                answers_data = {}
                for question in questions_data:
                    if question['type'] == 'multiple_choice':
                        answer = random.choice(question.get('choices', ['Good']))
                    elif question['type'] == 'rating':
                        answer = random.randint(1, 5)
                    elif question['type'] == 'yes_no':
                        answer = random.choice(['Yes', 'No'])
                    else:
                        answer = f"Sample answer for question {question['id']}"
                    
                    answers_data[str(question['id'])] = answer
                
                SurveyResponse.objects.create(
                    survey=survey,
                    respondent=respondent,
                    answers=answers_data,
                    submitted_at=timezone.now() - timedelta(days=random.randint(1, 20))
                )
        
        print(f"✅ Created {len(survey_titles)} surveys with responses")
    
    def create_evaluations(self):
        """Create 5 evaluation forms with 8 criteria each"""
        print("\n⭐ Creating 5 evaluation forms with 8 criteria each...")
        
        evaluation_titles = [
            "Doctor Performance Evaluation",
            "Healthcare Service Quality",
            "Medical Training Assessment", 
            "Patient Care Evaluation",
            "Health Program Effectiveness"
        ]
        
        criteria_names = [
            "Overall Quality of Service",
            "Professional Interaction",
            "Timeliness and Efficiency",
            "Communication Clarity", 
            "Outcome Satisfaction",
            "Service Recommendation",
            "Facilities and Environment",
            "Overall Satisfaction"
        ]
        
        for eval_title in evaluation_titles:
            eval_form = EvaluationForm.objects.create(
                title=eval_title,
                description=f"Comprehensive evaluation for {eval_title.lower()}",
                created_by=self.admin_user,
                start_date=timezone.now().date(),
                end_date=timezone.now().date() + timedelta(days=45),
                is_active=True
            )
            
            # Create 8 criteria per evaluation
            criteria_list = []
            for i, criteria_name in enumerate(criteria_names):
                criteria = EvaluationCriteria.objects.create(
                    name=criteria_name,
                    description=f"Evaluation criteria for {criteria_name.lower()}",
                    weight=1.0,
                    max_score=5.0,
                    order=i + 1
                )
                criteria_list.append(criteria)
                eval_form.criteria.add(criteria)
            
            # Create evaluation submissions
            evaluators = random.sample(self.created_users, min(12, len(self.created_users)))
            for evaluator in evaluators:
                submission = EvaluationSubmission.objects.create(
                    evaluation_form=eval_form,
                    submitted_by=evaluator,
                    submitted_at=timezone.now() - timedelta(days=random.randint(1, 30)),
                    total_score=round(random.uniform(3.0, 5.0), 1)
                )
                
                # Create responses for each criteria
                for criteria in criteria_list:
                    score = round(random.uniform(2.0, 5.0), 1)
                    feedback = f"Evaluation feedback for {criteria.name}"
                    
                    EvaluationResponse.objects.create(
                        submission=submission,
                        criteria=criteria,
                        score=score,
                        feedback=feedback
                    )
        
        print(f"✅ Created {len(evaluation_titles)} evaluation forms with submissions")
    
    def create_photos_data(self):
        """Create photo albums and photos"""
        print("\n📸 Creating photo albums and photos...")
        
        album_names = [
            "Medical Conference 2024", "Community Health Drive", 
            "Student Graduation", "Hospital Opening", "Health Awareness Campaign"
        ]
        
        for album_name in album_names:
            album = PhotoAlbum.objects.create(
                title=album_name,
                description=f"Photo collection from {album_name}",
                created_by=random.choice(self.created_users),
                is_public=True,
                created_at=timezone.now() - timedelta(days=random.randint(1, 180))
            )
            
            # Add photos to album
            for i in range(random.randint(5, 12)):
                photo = Photo.objects.create(
                    title=f"Photo {i+1} from {album_name}",
                    description=f"Description for photo {i+1}",
                    album=album,
                    user=album.created_by,
                    image=f"https://via.placeholder.com/800x600?text=Photo+{i+1}",
                    uploaded_at=album.created_at + timedelta(hours=random.randint(1, 48))
                )
        
        print(f"✅ Created {len(album_names)} photo albums with sample photos")
    
    def create_araz_petitions(self):
        """Create some Araz petitions"""
        print("\n📝 Creating Araz petitions...")
        
        petition_topics = [
            "Request for Medical Equipment",
            "Community Health Program Proposal",
            "Healthcare Facility Improvement", 
            "Medical Training Resources",
            "Patient Care Enhancement"
        ]
        
        for topic in petition_topics:
            petition = Petition.objects.create(
                title=topic,
                description=f"Detailed petition regarding {topic.lower()}",
                submitted_by=random.choice(self.created_users),
                category=random.choice(['medical', 'administrative', 'community']),
                priority=random.choice(['low', 'medium', 'high']),
                status=random.choice(['pending', 'under_review', 'approved', 'rejected']),
                submitted_at=timezone.now() - timedelta(days=random.randint(1, 90))
            )
        
        print(f"✅ Created {len(petition_topics)} Araz petitions")
    
    def generate_all_data(self):
        """Generate all data in proper sequence"""
        print("🚀 Starting comprehensive data generation for 50 users...")
        print("=" * 70)
        
        try:
            # Step 1: Users with ITS profile data
            self.generate_users()
            
            # Step 2: Moze structure (8 Moze = 8 Aamils)
            self.create_moze_structure() 
            
            # Step 3: Medical infrastructure
            self.create_hospitals_and_medical_data()
            
            # Step 4: Medical records and appointments
            self.create_medical_records()
            
            # Step 5: Student data
            self.create_student_data()
            
            # Step 6: Surveys (5 surveys, 10 questions each)
            self.create_surveys()
            
            # Step 7: Evaluations (5 forms, 8 questions each)
            self.create_evaluations()
            
            # Step 8: Photos data
            self.create_photos_data()
            
            # Step 9: Araz petitions
            self.create_araz_petitions()
            
            print("\n" + "=" * 70)
            print("🎉 COMPREHENSIVE DATA GENERATION COMPLETED!")
            print("\n📊 SUMMARY:")
            print(f"👥 Users: {User.objects.count()}")
            print(f"🏛️  Moze: {Moze.objects.count()}")
            print(f"🏥 Hospitals: {Hospital.objects.count()}")
            print(f"👨‍⚕️ Doctors: {Doctor.objects.count()}")
            print(f"🤒 Patients: {Patient.objects.count()}")
            print(f"🎓 Students: {Student.objects.count()}")
            print(f"📊 Surveys: {Survey.objects.count()}")
            print(f"⭐ Evaluations: {EvaluationForm.objects.count()}")
            print(f"📸 Photo Albums: {PhotoAlbum.objects.count()}")
            print(f"📝 Petitions: {Petition.objects.count()}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during data generation: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    generator = ComprehensiveDataGenerator()
    success = generator.generate_all_data()
    sys.exit(0 if success else 1)