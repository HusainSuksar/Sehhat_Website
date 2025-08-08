#!/usr/bin/env python3
"""
Complete Data Setup Script
Finishes populating the database with remaining data:
- Medical records and appointments  
- Student courses and submissions
- 5 Surveys with responses
- 5 Evaluation forms with submissions
- Photos app data
- Analytics data
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
from django.utils import timezone

# Import all models
from moze.models import Moze, UmoorSehhatTeam
from students.models import Student, Course, Assignment, Submission
from doctordirectory.models import Doctor, Patient, Appointment, MedicalRecord
from mahalshifa.models import Doctor as MahalShifaDoctor, Hospital, Patient as MahalShifaPatient
from surveys.models import Survey, SurveyResponse
from evaluation.models import EvaluationForm, EvaluationSubmission, EvaluationResponse, EvaluationCriteria
from photos.models import PhotoAlbum, Photo
from araz.models import Petition, PetitionCategory

class DataCompleter:
    def __init__(self):
        self.users = User.objects.exclude(username='AnonymousUser')
        self.doctors = self.users.filter(role='doctor')
        self.students = self.users.filter(role='student')
        self.patients = self.users.filter(role='patient')
        self.admin_user = self.users.filter(role='badri_mahal_admin').first()
        self.mozes = list(Moze.objects.all())
        self.hospitals = list(Hospital.objects.all())

    def complete_medical_data(self):
        """Complete doctor/patient profiles and medical records"""
        print("\n🏥 Completing medical data...")
        
        # Create missing doctor profiles
        existing_doctor_users = set(Doctor.objects.values_list('user', flat=True))
        doctors_to_create = [d for d in self.doctors if d.id not in existing_doctor_users]
        
        specializations = ["Cardiology", "Neurology", "Orthopedics", "Pediatrics", "Dermatology", "Internal Medicine"]
        for i, doctor_user in enumerate(doctors_to_create):
            Doctor.objects.create(
                user=doctor_user,
                name=doctor_user.get_full_name(),
                its_id=doctor_user.its_id,
                specialty=random.choice(specializations),
                qualification=doctor_user.qualification or "MBBS",
                experience_years=random.randint(1, 25),
                license_number=f"DOC{5000+i:04d}",
                consultation_fee=Decimal(str(random.randint(100, 500))),
                is_verified=True,
                is_available=True,
                assigned_moze=random.choice(self.mozes) if self.mozes else None,
                phone=doctor_user.mobile_number,
                email=doctor_user.email,
                address=doctor_user.address
            )
        
        # Create missing patient profiles
        existing_patient_users = set(Patient.objects.values_list('user', flat=True))
        patients_to_create = [p for p in self.patients if p.id not in existing_patient_users]
        
        for i, patient_user in enumerate(patients_to_create):
            gender_mapping = {'male': 'M', 'female': 'F', 'other': 'O'}
            gender = gender_mapping.get(patient_user.gender.lower() if patient_user.gender else 'other', 'O')
            
            Patient.objects.create(
                user=patient_user,
                date_of_birth=date.today() - timedelta(days=random.randint(6570, 25550)),
                gender=gender,
                blood_group=random.choice(['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']),
                emergency_contact=f"+1-555-{6000+i:04d}",
                medical_history=f"Medical history for patient {i+1}",
                allergies="None known" if random.random() > 0.3 else "Seasonal allergies",
                current_medications="None" if random.random() > 0.4 else "Multivitamins"
            )
        
        # Create appointments and medical records
        if Appointment.objects.count() < 20:
            doctors = Doctor.objects.all()
            patients = Patient.objects.all()
            
            for i in range(25):
                if doctors and patients:
                    doctor = random.choice(doctors)
                    patient = random.choice(patients)
                    
                    appointment_date = timezone.now() - timedelta(days=random.randint(1, 90))
                    
                    appointment, created = Appointment.objects.get_or_create(
                        doctor=doctor,
                        patient=patient,
                        appointment_date=appointment_date.date(),
                        defaults={
                            'appointment_time': f"{random.randint(9, 17):02d}:{random.choice(['00', '30'])}",
                            'status': random.choice(['scheduled', 'completed', 'cancelled']),
                            'notes': f"Appointment {i+1} notes"
                        }
                    )
                    
                    # Create medical record for completed appointments
                    if created and appointment.status == 'completed':
                        MedicalRecord.objects.create(
                            patient=patient,
                            doctor=doctor,
                            diagnosis=f"Diagnosis for appointment {i+1}",
                            symptoms=f"Symptoms reported by patient",
                            treatment_plan=f"Treatment prescribed for patient",
                            notes=f"Medical notes for completed appointment {i+1}"
                        )
        
        print(f"✅ Medical data completed")
        print(f"   - Doctors: {Doctor.objects.count()}")
        print(f"   - Patients: {Patient.objects.count()}")
        print(f"   - Appointments: {Appointment.objects.count()}")
        print(f"   - Medical Records: {MedicalRecord.objects.count()}")

    def complete_student_data(self):
        """Complete student courses and submissions"""
        print("\n🎓 Completing student data...")
        
        # Create courses if they don't exist
        if Course.objects.count() < 5:
            course_names = [
                "Introduction to Islamic Medicine", "Anatomy and Physiology", 
                "Medical Ethics", "Community Health", "Pharmacology Basics"
            ]
            
            for course_name in course_names:
                Course.objects.get_or_create(
                    name=course_name,
                    defaults={
                        'code': f"COURSE{Course.objects.count()+1:03d}",
                        'credits': random.randint(2, 4),
                        'description': f"Description for {course_name}",
                        'instructor': random.choice(self.doctors) if self.doctors else self.admin_user
                    }
                )
        
        # Create student profiles
        existing_student_users = set(Student.objects.values_list('user', flat=True))
        students_to_create = [s for s in self.students if s.id not in existing_student_users]
        courses = list(Course.objects.all())
        
        for i, student_user in enumerate(students_to_create):
            Student.objects.create(
                user=student_user,
                student_id=f"STU{7000+i:04d}",
                academic_level=random.choice(['undergraduate', 'postgraduate', 'diploma']),
                enrollment_status='active',
                enrollment_date=date.today() - timedelta(days=random.randint(30, 1000)),
                expected_graduation=date.today() + timedelta(days=random.randint(365, 1460))
            )
        
        # Create assignments for courses
        if Assignment.objects.count() < 10:
            courses = list(Course.objects.all())
            for i, course in enumerate(courses):
                for j in range(3):  # 3 assignments per course
                    Assignment.objects.create(
                        course=course,
                        title=f"Assignment {j+1} - {course.name}",
                        description=f"Assignment description for {course.name}",
                        assignment_type=random.choice(['homework', 'project', 'quiz']),
                        due_date=timezone.now() + timedelta(days=random.randint(7, 30)),
                        max_points=100,
                        is_published=True
                    )
        
        # Create submissions
        if Submission.objects.count() < 30:
            students = Student.objects.all()
            assignments = list(Assignment.objects.all())
            for i in range(35):
                if students and assignments:
                    student = random.choice(students)
                    assignment = random.choice(assignments)
                    Submission.objects.create(
                        assignment=assignment,
                        student=student,
                        content=f"Submission content for {assignment.title}",
                        is_graded=random.choice([True, False]),
                        is_late=random.choice([True, False])
                    )
        
        print(f"✅ Student data completed")
        print(f"   - Courses: {Course.objects.count()}")
        print(f"   - Students: {Student.objects.count()}")
        print(f"   - Submissions: {Submission.objects.count()}")

    def complete_surveys(self):
        """Complete 5 surveys with responses"""
        print("\n📊 Completing surveys...")
        
        if Survey.objects.count() >= 5:
            print("   Surveys already exist")
            return
        
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
            respondents = random.sample(list(self.users), min(15, len(self.users)))
            for respondent in respondents:
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
                
                response = SurveyResponse.objects.create(
                    survey=survey,
                    respondent=respondent,
                    answers=answers_data,
                    is_complete=True
                )
                # Update created_at manually (auto_now_add doesn't allow manual setting)
                response.created_at = timezone.now() - timedelta(days=random.randint(1, 20))
                response.save()
        
        print(f"✅ Surveys completed: {Survey.objects.count()}")

    def complete_evaluations(self):
        """Complete 5 evaluation forms with submissions"""
        print("\n⭐ Completing evaluations...")
        
        if EvaluationForm.objects.count() >= 5:
            print("   Evaluations already exist")
            return
        
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
                evaluation_type=random.choice(['performance', 'satisfaction', 'quality', 'service']),
                target_role='all',
                created_by=self.admin_user,
                due_date=timezone.now() + timedelta(days=45),
                is_active=True,
                is_anonymous=False
            )
            
            # Create 8 criteria per evaluation  
            criteria_list = []
            for i, criteria_name in enumerate(criteria_names):
                criteria = EvaluationCriteria.objects.create(
                    name=criteria_name,
                    description=f"Evaluation criteria for {criteria_name.lower()}",
                    weight=1.0,
                    max_score=5,
                    order=i + 1,
                    category=random.choice(['medical_quality', 'staff_performance', 'infrastructure', 'safety'])
                )
                criteria_list.append(criteria)
            
            # Create evaluation submissions
            evaluators = random.sample(list(self.users), min(12, len(self.users)))
            for evaluator in evaluators:
                submission = EvaluationSubmission.objects.create(
                    form=eval_form,
                    evaluator=evaluator,
                    target_user=random.choice(self.users),
                    total_score=round(random.uniform(3.0, 5.0), 1),
                    is_complete=True,
                    comments=f"Evaluation comments from {evaluator.get_full_name()}"
                )
                
                # Create responses for each criteria
                for criteria in criteria_list:
                    score = random.randint(2, 5)
                    comment = f"Evaluation feedback for {criteria.name}"
                    
                    EvaluationResponse.objects.create(
                        submission=submission,
                        criteria=criteria,
                        score=score,
                        comment=comment
                    )
        
        print(f"✅ Evaluations completed: {EvaluationForm.objects.count()}")

    def complete_photos(self):
        """Complete photo albums and photos"""
        print("\n📸 Completing photos...")
        
        if PhotoAlbum.objects.count() >= 5:
            print("   Photo albums already exist")
            return
        
        album_names = [
            "Medical Conference 2024", "Community Health Drive", 
            "Student Graduation", "Hospital Opening", "Health Awareness Campaign"
        ]
        
        for album_name in album_names:
            album = PhotoAlbum.objects.create(
                name=album_name,
                description=f"Photo collection from {album_name}",
                moze=random.choice(self.mozes) if self.mozes else None,
                created_by=random.choice(self.users)
            )
            
            # Add photos to album (first create photos, then add to album)
            for i in range(random.randint(5, 12)):
                photo = Photo.objects.create(
                    title=f"Photo {i+1} from {album_name}",
                    description=f"Description for photo {i+1}",
                    moze=album.moze,
                    uploaded_by=album.created_by
                    # Skip image field for now to avoid file handling complexity
                )
                album.photos.add(photo)
        
        print(f"✅ Photo albums completed: {PhotoAlbum.objects.count()}")

    def complete_araz_petitions(self):
        """Complete Araz petitions"""
        print("\n📝 Completing Araz petitions...")
        
        if Petition.objects.count() >= 5:
            print("   Petitions already exist")
            return
        
        # Create petition categories first
        category_names = ['Medical', 'Administrative', 'Community', 'Infrastructure', 'Resources']
        categories = []
        for cat_name in category_names:
            category, created = PetitionCategory.objects.get_or_create(
                name=cat_name,
                defaults={
                    'description': f'Category for {cat_name.lower()} related petitions',
                    'color': random.choice(['#007bff', '#28a745', '#ffc107', '#dc3545', '#6f42c1'])
                }
            )
            categories.append(category)
        
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
                created_by=random.choice(self.users),
                category=random.choice(categories),
                priority=random.choice(['low', 'medium', 'high']),
                status=random.choice(['pending', 'in_progress', 'resolved', 'rejected']),
                moze=random.choice(self.mozes) if self.mozes else None
            )
        
        print(f"✅ Araz petitions completed: {Petition.objects.count()}")

    def run_completion(self):
        """Run all data completion tasks"""
        print("🚀 Starting data completion...")
        print("=" * 60)
        
        try:
            self.complete_medical_data()
            self.complete_student_data()
            self.complete_surveys()
            self.complete_evaluations()
            self.complete_photos()
            self.complete_araz_petitions()
            
            print("\n" + "=" * 60)
            print("🎉 DATA COMPLETION SUCCESSFUL!")
            print("\n📊 FINAL SUMMARY:")
            print(f"👥 Users: {User.objects.count()}")
            print(f"🏛️  Moze: {Moze.objects.count()}")
            print(f"🏥 Hospitals: {Hospital.objects.count()}")
            print(f"👨‍⚕️ Doctors: {Doctor.objects.count()}")
            print(f"🤒 Patients: {Patient.objects.count()}")
            print(f"🎓 Students: {Student.objects.count()}")
            print(f"📅 Appointments: {Appointment.objects.count()}")
            print(f"📋 Medical Records: {MedicalRecord.objects.count()}")
            print(f"📊 Surveys: {Survey.objects.count()}")
            print(f"⭐ Evaluations: {EvaluationForm.objects.count()}")
            print(f"📸 Photo Albums: {PhotoAlbum.objects.count()}")
            print(f"📝 Petitions: {Petition.objects.count()}")
            
            print("\n🎯 COMPLETE SUCCESS! All 9 Django apps populated with data!")
            return True
            
        except Exception as e:
            print(f"❌ Error during completion: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    completer = DataCompleter()
    success = completer.run_completion()
    sys.exit(0 if success else 1)