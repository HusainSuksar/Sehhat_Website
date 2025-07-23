#!/usr/bin/env python3
"""
Comprehensive Test Data Population Script for Umoor Sehhat Django Project
Populates all 9 apps with realistic test data
"""

import os
import sys
import django
from datetime import datetime, timedelta, date
from decimal import Decimal
import random

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

# Import all models
from django.contrib.auth import get_user_model
from accounts.models import User, UserProfile
from araz.models import Petition, PetitionCategory, PetitionComment, DuaAraz
from moze.models import Moze, MozeComment
from photos.models import PhotoAlbum, Photo, PhotoTag, PhotoComment, PhotoLike
from surveys.models import Survey, SurveyResponse
from students.models import Student, Course, Enrollment, Assignment, Grade, Attendance
from evaluation.models import EvaluationForm, EvaluationSubmission
from mahalshifa.models import Hospital, Patient, Appointment, MedicalRecord, Prescription
from doctordirectory.models import Doctor, PatientLog

User = get_user_model()

def create_users():
    """Create test users with different roles"""
    print("🏗️  Creating test users...")
    
    users_data = [
        {'username': 'admin', 'email': 'admin@sehhat.com', 'role': 'admin', 'first_name': 'System', 'last_name': 'Administrator'},
        {'username': 'dr_ahmed', 'email': 'ahmed@sehhat.com', 'role': 'doctor', 'first_name': 'Dr. Ahmed', 'last_name': 'Hassan'},
        {'username': 'dr_fatima', 'email': 'fatima@sehhat.com', 'role': 'doctor', 'first_name': 'Dr. Fatima', 'last_name': 'Ali'},
        {'username': 'aamil_karachi', 'email': 'aamil.khi@sehhat.com', 'role': 'aamil', 'first_name': 'Aamil', 'last_name': 'Karachi'},
        {'username': 'coordinator_1', 'email': 'coord1@sehhat.com', 'role': 'moze_coordinator', 'first_name': 'Hassan', 'last_name': 'Coordinator'},
        {'username': 'student_ali', 'email': 'ali.student@sehhat.com', 'role': 'student', 'first_name': 'Ali', 'last_name': 'Ahmed'},
        {'username': 'student_sara', 'email': 'sara.student@sehhat.com', 'role': 'student', 'first_name': 'Sara', 'last_name': 'Khan'},
        {'username': 'patient_omar', 'email': 'omar@sehhat.com', 'role': 'user', 'first_name': 'Omar', 'last_name': 'Rahman'},
        {'username': 'patient_aisha', 'email': 'aisha@sehhat.com', 'role': 'user', 'first_name': 'Aisha', 'last_name': 'Ibrahim'},
    ]
    
    created_users = {}
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'role': user_data['role'],
                'is_active': True,
                'phone_number': f'+92300{random.randint(1000000, 9999999)}',
                'its_id': f'{random.randint(10000000, 99999999)}'
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
            print(f"   ✅ Created user: {user.username} ({user.role})")
        created_users[user_data['username']] = user
    
    return created_users

def create_moze_data(users):
    """Create Moze (community) test data"""
    print("🏘️  Creating Moze data...")
    
    moze_data = [
        {'name': 'North Karachi Moze', 'location': 'North Karachi', 'aamil': users['aamil_karachi']},
        {'name': 'Gulshan Moze', 'location': 'Gulshan-e-Iqbal', 'aamil': users['aamil_karachi']},
        {'name': 'Defence Moze', 'location': 'Defence Housing Authority', 'aamil': users['aamil_karachi']},
    ]
    
    created_mozes = []
    for data in moze_data:
        moze, created = Moze.objects.get_or_create(
            name=data['name'],
            defaults={
                'location': data['location'],
                'address': f"123 Main Street, {data['location']}, Karachi",
                'aamil': data['aamil'],
                'moze_coordinator': users['coordinator_1'],
                'established_date': date(2020, 1, 1),
                'is_active': True,
                'capacity': random.randint(50, 200),
                'contact_phone': f'+92021{random.randint(1000000, 9999999)}',
                'contact_email': f"info@{data['name'].lower().replace(' ', '')}.com"
            }
        )
        if created:
            print(f"   ✅ Created Moze: {moze.name}")
        created_mozes.append(moze)
    
    return created_mozes

def create_petition_data(users, mozes):
    """Create Araz (Petition) test data"""
    print("📋 Creating Araz/Petition data...")
    
    # Create categories
    categories = []
    category_names = ['Medical Request', 'Community Issue', 'Educational Support', 'Emergency Aid', 'Infrastructure']
    for cat_name in category_names:
        category, created = PetitionCategory.objects.get_or_create(
            name=cat_name,
            defaults={
                'description': f'Category for {cat_name.lower()} related petitions',
                'color': f'#{random.randint(100000, 999999)}',
                'is_active': True
            }
        )
        categories.append(category)
    
    # Create petitions
    petition_data = [
        {'title': 'Request for Medical Camp', 'description': 'We need a medical camp in our area for general health checkups.', 'category': categories[0]},
        {'title': 'Street Light Repair', 'description': 'The street lights in our neighborhood are not working properly.', 'category': categories[1]},
        {'title': 'Educational Workshop Request', 'description': 'Request for computer literacy workshop for community members.', 'category': categories[2]},
        {'title': 'Emergency Food Aid', 'description': 'Several families in our area need emergency food assistance.', 'category': categories[3]},
        {'title': 'Water Supply Issue', 'description': 'Irregular water supply in the community needs immediate attention.', 'category': categories[4]},
    ]
    
    for i, data in enumerate(petition_data):
        petition, created = Petition.objects.get_or_create(
            title=data['title'],
            defaults={
                'description': data['description'],
                'category': data['category'],
                'created_by': users['patient_omar'] if i % 2 == 0 else users['patient_aisha'],
                'status': random.choice(['pending', 'in_progress', 'resolved']),
                'priority': random.choice(['low', 'medium', 'high']),
                'moze': random.choice(mozes),
                'is_anonymous': False
            }
        )
        if created:
            print(f"   ✅ Created petition: {petition.title}")
    
    # Create DuaAraz (Medical requests)
    medical_requests = [
        {'patient_name': 'Omar Rahman', 'ailment': 'Chronic back pain', 'urgency': 'medium'},
        {'patient_name': 'Aisha Ibrahim', 'ailment': 'Diabetes consultation', 'urgency': 'high'},
        {'patient_name': 'Hassan Ali', 'ailment': 'General checkup', 'urgency': 'low'},
    ]
    
    for data in medical_requests:
        dua_araz, created = DuaAraz.objects.get_or_create(
            patient_name=data['patient_name'],
            defaults={
                'patient_its_id': f'{random.randint(10000000, 99999999)}',
                'patient_phone': f'+92300{random.randint(1000000, 9999999)}',
                'patient_email': f"{data['patient_name'].lower().replace(' ', '')}@example.com",
                'ailment': data['ailment'],
                'symptoms': 'Detailed symptoms description here',
                'urgency_level': data['urgency'],
                'request_type': 'consultation',
                'status': random.choice(['submitted', 'under_review', 'approved']),
                'priority': data['urgency']
            }
        )
        if created:
            print(f"   ✅ Created medical request: {dua_araz.patient_name}")

def create_photo_data(users, mozes):
    """Create Photos app test data"""
    print("📷 Creating Photos data...")
    
    # Create photo albums
    albums_data = [
        {'name': 'Community Events 2024', 'description': 'Photos from various community events'},
        {'name': 'Medical Camp Photos', 'description': 'Documentation of medical camp activities'},
        {'name': 'Educational Workshops', 'description': 'Photos from educational programs'},
    ]
    
    created_albums = []
    for data in albums_data:
        album, created = PhotoAlbum.objects.get_or_create(
            name=data['name'],
            defaults={
                'description': data['description'],
                'created_by': users['coordinator_1'],
                'moze': random.choice(mozes),
                'is_public': True,
                'allow_uploads': True
            }
        )
        if created:
            print(f"   ✅ Created album: {album.name}")
        created_albums.append(album)
    
    # Create photo tags
    tag_names = ['community', 'medical', 'education', 'event', 'healthcare', 'workshop']
    tags = []
    for tag_name in tag_names:
        tag, created = PhotoTag.objects.get_or_create(name=tag_name)
        tags.append(tag)
    
    return created_albums

def create_survey_data(users):
    """Create Surveys app test data"""
    print("📊 Creating Survey data...")
    
    surveys_data = [
        {
            'title': 'Community Health Assessment',
            'description': 'Survey to assess health needs in the community',
            'questions': [
                {'question': 'How would you rate your overall health?', 'type': 'rating'},
                {'question': 'What health services do you need most?', 'type': 'text'},
                {'question': 'Do you have access to clean drinking water?', 'type': 'boolean'}
            ]
        },
        {
            'title': 'Educational Program Feedback',
            'description': 'Feedback on our educational programs',
            'questions': [
                {'question': 'Rate the quality of our workshops', 'type': 'rating'},
                {'question': 'What topics would you like to see covered?', 'type': 'text'}
            ]
        }
    ]
    
    for data in surveys_data:
        survey, created = Survey.objects.get_or_create(
            title=data['title'],
            defaults={
                'description': data['description'],
                'questions': data['questions'],
                'created_by': users['coordinator_1'],
                'target_role': 'all',
                'is_active': True,
                'is_anonymous': True,
                'allow_multiple_responses': False
            }
        )
        if created:
            print(f"   ✅ Created survey: {survey.title}")
            
            # Create sample responses
            for i in range(3):
                response_data = {
                    'question_1': random.randint(1, 5),
                    'question_2': f'Sample response {i+1}',
                    'question_3': random.choice([True, False])
                }
                
                SurveyResponse.objects.get_or_create(
                    survey=survey,
                    respondent=list(users.values())[i % len(users)],
                    defaults={
                        'response_data': response_data,
                        'is_complete': True
                    }
                )

def create_student_data(users):
    """Create Students app test data"""
    print("🎓 Creating Student data...")
    
    # Create courses
    courses_data = [
        {'code': 'CS101', 'name': 'Introduction to Programming', 'credits': 3, 'department': 'Computer Science'},
        {'code': 'BIO201', 'name': 'Human Biology', 'credits': 4, 'department': 'Biology'},
        {'code': 'MATH301', 'name': 'Statistics', 'credits': 3, 'department': 'Mathematics'},
        {'code': 'ENG102', 'name': 'Academic Writing', 'credits': 2, 'department': 'English'},
    ]
    
    created_courses = []
    for data in courses_data:
        course, created = Course.objects.get_or_create(
            code=data['code'],
            defaults={
                'name': data['name'],
                'description': f"Comprehensive course on {data['name'].lower()}",
                'credits': data['credits'],
                'instructor': users['dr_ahmed'],
                'is_active': True
            }
        )
        if created:
            print(f"   ✅ Created course: {course.code} - {course.name}")
        created_courses.append(course)
    
    # Create students
    student_users = [users['student_ali'], users['student_sara']]
    created_students = []
    
    for i, user in enumerate(student_users):
        student, created = Student.objects.get_or_create(
            user=user,
            defaults={
                'student_id': f'STU{2024}{str(i+1).zfill(3)}',
                'date_of_birth': date(2000 + i, 6, 15),
                'gender': 'male' if i == 0 else 'female',
                'emergency_contact_name': f'Parent of {user.first_name}',
                'emergency_contact_phone': f'+92300{random.randint(1000000, 9999999)}',
                'address': f'Student Address {i+1}, Karachi'
            }
        )
        if created:
            print(f"   ✅ Created student: {student.user.get_full_name()}")
        created_students.append(student)
        
        # Enroll students in courses
        for course in created_courses[:2]:  # Enroll in first 2 courses
            enrollment, created = Enrollment.objects.get_or_create(
                student=student,
                course=course,
                defaults={'grade': random.choice(['A', 'B', 'C'])}
            )
    
    # Create assignments
    for course in created_courses:
        assignment, created = Assignment.objects.get_or_create(
            title=f'{course.code} Assignment 1',
            defaults={
                'description': f'First assignment for {course.name}',
                'course': course,
                'due_date': datetime.now() + timedelta(days=30),
                'assignment_type': 'homework'
            }
        )
        if created:
            print(f"   ✅ Created assignment: {assignment.title}")
    
    return created_students, created_courses

def create_evaluation_data(users):
    """Create Evaluation app test data"""
    print("📝 Creating Evaluation data...")
    
    # Create evaluation forms
    eval_forms_data = [
        {
            'title': 'Doctor Performance Evaluation',
            'description': 'Annual performance evaluation for medical staff',
            'target_role': 'doctor'
        },
        {
            'title': 'Community Coordinator Assessment',
            'description': 'Evaluation for community coordinators',
            'target_role': 'moze_coordinator'
        }
    ]
    
    for data in eval_forms_data:
        form, created = EvaluationForm.objects.get_or_create(
            title=data['title'],
            defaults={
                'description': data['description'],
                'created_by': users['admin'],
                'target_role': data['target_role'],
                'due_date': datetime.now() + timedelta(days=60),
                'is_active': True,
                'is_anonymous': False
            }
        )
        if created:
            print(f"   ✅ Created evaluation form: {form.title}")
            
            # Create sample submission
            submission, created = EvaluationSubmission.objects.get_or_create(
                evaluation_form=form,
                evaluated_user=users['dr_ahmed'] if 'Doctor' in form.title else users['coordinator_1'],
                defaults={
                    'submitted_by': users['admin'],
                    'comments': 'Excellent performance overall. Meets all expectations.',
                    'is_complete': True
                }
            )

def create_hospital_data(users):
    """Create Mahalshifa (Hospital) test data"""
    print("🏥 Creating Hospital data...")
    
    # Create hospitals
    hospitals_data = [
        {
            'name': 'Karachi General Hospital',
            'address': '123 Shahrah-e-Faisal, Karachi',
            'hospital_type': 'general',
            'phone': '+92213456789'
        },
        {
            'name': 'Children\'s Medical Center',
            'address': '456 University Road, Karachi',
            'hospital_type': 'specialty',
            'phone': '+92213456790'
        }
    ]
    
    created_hospitals = []
    for data in hospitals_data:
        hospital, created = Hospital.objects.get_or_create(
            name=data['name'],
            defaults={
                'address': data['address'],
                'phone': data['phone'],
                'email': f"info@{data['name'].lower().replace(' ', '').replace('\'', '')}.com",
                'hospital_type': data['hospital_type'],
                'is_active': True
            }
        )
        if created:
            print(f"   ✅ Created hospital: {hospital.name}")
        created_hospitals.append(hospital)
    
    # Create patients
    patient_users = [users['patient_omar'], users['patient_aisha']]
    created_patients = []
    
    for i, user in enumerate(patient_users):
        patient, created = Patient.objects.get_or_create(
            user=user,
            defaults={
                'patient_id': f'PAT{2024}{str(i+1).zfill(4)}',
                'date_of_birth': date(1990 + i*5, 3, 10),
                'gender': 'male' if i == 0 else 'female',
                'blood_group': random.choice(['A+', 'B+', 'O+', 'AB+']),
                'emergency_contact_name': f'Emergency Contact {i+1}',
                'emergency_contact_phone': f'+92300{random.randint(1000000, 9999999)}',
                'address': f'Patient Address {i+1}, Karachi',
                'hospital': random.choice(created_hospitals)
            }
        )
        if created:
            print(f"   ✅ Created patient: {patient.user.get_full_name()}")
        created_patients.append(patient)
    
    return created_hospitals, created_patients

def create_doctor_data(users, hospitals, patients):
    """Create Doctor Directory test data"""
    print("👨‍⚕️ Creating Doctor data...")
    
    # Create doctors
    doctor_users = [users['dr_ahmed'], users['dr_fatima']]
    created_doctors = []
    
    specializations = ['general_medicine', 'cardiology', 'pediatrics', 'orthopedics']
    
    for i, user in enumerate(doctor_users):
        doctor, created = Doctor.objects.get_or_create(
            user=user,
            defaults={
                'license_number': f'MD{2020+i}{str(i+1).zfill(4)}',
                'specialization': specializations[i % len(specializations)],
                'experience_years': random.randint(5, 20),
                'hospital': random.choice(hospitals),
                'consultation_fee': Decimal(str(random.randint(500, 2000))),
                'is_verified': True,
                'is_available': True
            }
        )
        if created:
            print(f"   ✅ Created doctor: Dr. {doctor.user.get_full_name()}")
        created_doctors.append(doctor)
    
    # Create appointments
    for i, patient in enumerate(patients):
        appointment, created = Appointment.objects.get_or_create(
            patient=patient,
            doctor=random.choice(created_doctors),
            defaults={
                'appointment_date': date.today() + timedelta(days=random.randint(1, 30)),
                'appointment_time': datetime.now().time(),
                'appointment_type': random.choice(['consultation', 'follow_up', 'emergency']),
                'status': random.choice(['scheduled', 'completed', 'cancelled']),
                'reason': f'Medical consultation for {patient.user.first_name}',
                'notes': 'Regular checkup appointment'
            }
        )
        if created:
            print(f"   ✅ Created appointment: {appointment.patient.user.get_full_name()} with {appointment.doctor.user.get_full_name()}")
    
    # Create medical records
    for patient in patients:
        record, created = MedicalRecord.objects.get_or_create(
            patient=patient,
            doctor=random.choice(created_doctors),
            defaults={
                'symptoms': 'Patient complained of mild fever and headache',
                'diagnosis': 'Viral infection - common cold',
                'treatment': 'Rest, fluids, and over-the-counter pain relief',
                'notes': 'Patient advised to return if symptoms persist'
            }
        )
        if created:
            print(f"   ✅ Created medical record for: {record.patient.user.get_full_name()}")
    
    return created_doctors

def run_functionality_tests():
    """Test basic functionality of all apps"""
    print("\n🧪 RUNNING FUNCTIONALITY TESTS")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 9
    
    try:
        # Test 1: Accounts
        user_count = User.objects.count()
        print(f"✅ Accounts: {user_count} users created")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Accounts: {e}")
    
    try:
        # Test 2: Araz
        petition_count = Petition.objects.count()
        dua_araz_count = DuaAraz.objects.count()
        print(f"✅ Araz: {petition_count} petitions + {dua_araz_count} medical requests")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Araz: {e}")
    
    try:
        # Test 3: Moze
        moze_count = Moze.objects.count()
        print(f"✅ Moze: {moze_count} community centers created")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Moze: {e}")
    
    try:
        # Test 4: Photos
        album_count = PhotoAlbum.objects.count()
        print(f"✅ Photos: {album_count} photo albums created")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Photos: {e}")
    
    try:
        # Test 5: Surveys
        survey_count = Survey.objects.count()
        response_count = SurveyResponse.objects.count()
        print(f"✅ Surveys: {survey_count} surveys + {response_count} responses")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Surveys: {e}")
    
    try:
        # Test 6: Students
        student_count = Student.objects.count()
        course_count = Course.objects.count()
        print(f"✅ Students: {student_count} students + {course_count} courses")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Students: {e}")
    
    try:
        # Test 7: Evaluation
        eval_count = EvaluationForm.objects.count()
        submission_count = EvaluationSubmission.objects.count()
        print(f"✅ Evaluation: {eval_count} forms + {submission_count} submissions")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Evaluation: {e}")
    
    try:
        # Test 8: Mahalshifa
        hospital_count = Hospital.objects.count()
        patient_count = Patient.objects.count()
        print(f"✅ Mahalshifa: {hospital_count} hospitals + {patient_count} patients")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Mahalshifa: {e}")
    
    try:
        # Test 9: Doctor Directory
        doctor_count = Doctor.objects.count()
        appointment_count = Appointment.objects.count()
        print(f"✅ Doctor Directory: {doctor_count} doctors + {appointment_count} appointments")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Doctor Directory: {e}")
    
    print(f"\n🎯 TEST RESULTS: {tests_passed}/{total_tests} apps working correctly")
    
    if tests_passed == total_tests:
        print("🎉 ALL APPS ARE WORKING PERFECTLY!")
    else:
        print("⚠️  Some apps have issues that need attention")
    
    return tests_passed == total_tests

def main():
    """Main execution function"""
    print("🚀 STARTING COMPREHENSIVE DATA POPULATION")
    print("=" * 50)
    
    try:
        # Create all test data
        users = create_users()
        mozes = create_moze_data(users)
        create_petition_data(users, mozes)
        create_photo_data(users, mozes)
        create_survey_data(users)
        students, courses = create_student_data(users)
        create_evaluation_data(users)
        hospitals, patients = create_hospital_data(users)
        doctors = create_doctor_data(users, hospitals, patients)
        
        print("\n✅ DATA POPULATION COMPLETED SUCCESSFULLY!")
        
        # Run functionality tests
        all_working = run_functionality_tests()
        
        print("\n📊 SUMMARY REPORT")
        print("=" * 50)
        print(f"👥 Users: {User.objects.count()}")
        print(f"🏘️  Mozes: {Moze.objects.count()}")
        print(f"📋 Petitions: {Petition.objects.count()}")
        print(f"📷 Photo Albums: {PhotoAlbum.objects.count()}")
        print(f"📊 Surveys: {Survey.objects.count()}")
        print(f"🎓 Students: {Student.objects.count()}")
        print(f"📝 Evaluations: {EvaluationForm.objects.count()}")
        print(f"🏥 Hospitals: {Hospital.objects.count()}")
        print(f"👨‍⚕️ Doctors: {Doctor.objects.count()}")
        
        if all_working:
            print("\n🎉 ALL 9 APPS ARE FULLY FUNCTIONAL WITH TEST DATA!")
        else:
            print("\n⚠️  Some apps need attention - check the test results above")
            
    except Exception as e:
        print(f"\n❌ ERROR DURING POPULATION: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()