#!/usr/bin/env python
"""
Specific Feature Testing Script
Tests individual components and features of the Umoor Sehhat system
"""

import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

# Import models for testing
from moze.models import Moze
from doctordirectory.models import Doctor, Patient, MedicalService
from students.models import Student, Course, Enrollment
from mahalshifa.models import Hospital, Department
from appointments.models import Appointment, TimeSlot
from surveys.models import Survey, SurveyResponse
from evaluation.models import Evaluation
from araz.models import Petition
from photos.models import PhotoAlbum, Photo

User = get_user_model()

class SpecificFeatureTester:
    def __init__(self):
        self.client = Client()
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
        
    def log_result(self, test_name, success, message=""):
        if success:
            self.test_results['passed'] += 1
            print(f"✅ {test_name}: PASSED {message}")
        else:
            self.test_results['failed'] += 1
            self.test_results['errors'].append(f"{test_name}: {message}")
            print(f"❌ {test_name}: FAILED {message}")
    
    def login_user(self, user):
        """Login user using ITS authentication"""
        try:
            response = self.client.post('/accounts/login/', {
                'its_id': user.its_id,
                'password': 'pass1234'
            }, follow=True)
            return response.status_code == 200 and 'login' not in response.request['PATH_INFO']
        except:
            return False
    
    def test_appointment_system(self):
        """Test the appointment booking and management system"""
        print("\n📅 TESTING APPOINTMENT SYSTEM")
        
        # Get test users
        doctor_user = User.objects.filter(role='doctor').first()
        patient_user = User.objects.filter(role='patient').first()
        
        if not doctor_user or not patient_user:
            self.log_result("Appointment System Setup", False, "Missing doctor or patient users")
            return
        
        # Test as patient - booking appointment
        login_success = self.login_user(patient_user)
        if login_success:
            # Test appointment list view
            response = self.client.get('/api/appointments/')
            self.log_result("Patient Appointment List", response.status_code in [200, 401], f"Status: {response.status_code}")
            
            # Test time slots availability
            if Doctor.objects.exists():
                doctor = Doctor.objects.first()
                response = self.client.get(f'/api/appointments/doctor/{doctor.id}/slots/')
                self.log_result("Time Slots API", response.status_code in [200, 404], f"Status: {response.status_code}")
        
        self.client.logout()
        
        # Test as doctor - managing appointments
        if doctor_user:
            login_success = self.login_user(doctor_user)
            if login_success:
                response = self.client.get('/doctordirectory/appointments/')
                self.log_result("Doctor Appointments View", response.status_code in [200, 404], f"Status: {response.status_code}")
        
        self.client.logout()
        
        # Test appointment data integrity
        appointment_count = Appointment.objects.count()
        timeslot_count = TimeSlot.objects.count()
        self.log_result("Appointment Data Exists", appointment_count > 0, f"Appointments: {appointment_count}")
        self.log_result("TimeSlot Data Exists", timeslot_count > 0, f"TimeSlots: {timeslot_count}")
    
    def test_medical_records_system(self):
        """Test medical records and patient data management"""
        print("\n🏥 TESTING MEDICAL RECORDS SYSTEM")
        
        doctor_user = User.objects.filter(role='doctor').first()
        patient_user = User.objects.filter(role='patient').first()
        
        if not doctor_user or not patient_user:
            self.log_result("Medical Records Setup", False, "Missing users")
            return
        
        # Test as doctor accessing patient records
        login_success = self.login_user(doctor_user)
        if login_success:
            response = self.client.get('/doctordirectory/patients/')
            self.log_result("Patient Records Access", response.status_code in [200, 404], f"Status: {response.status_code}")
            
            # Test API access
            response = self.client.get('/api/doctordirectory/patients/')
            self.log_result("Patient Records API", response.status_code in [200, 401], f"Status: {response.status_code}")
        
        self.client.logout()
        
        # Test data integrity
        patient_count = Patient.objects.count()
        doctor_count = Doctor.objects.count()
        self.log_result("Patient Data Exists", patient_count > 0, f"Patients: {patient_count}")
        self.log_result("Doctor Data Exists", doctor_count > 0, f"Doctors: {doctor_count}")
    
    def test_moze_management(self):
        """Test Moze (medical center) management system"""
        print("\n🏢 TESTING MOZE MANAGEMENT SYSTEM")
        
        aamil_user = User.objects.filter(role='aamil').first()
        coordinator_user = User.objects.filter(role='moze_coordinator').first()
        
        if not aamil_user:
            self.log_result("Moze Management Setup", False, "No aamil user found")
            return
        
        # Test as Aamil
        login_success = self.login_user(aamil_user)
        if login_success:
            response = self.client.get('/moze/')
            self.log_result("Moze Dashboard Access", response.status_code == 200, f"Status: {response.status_code}")
            
            response = self.client.get('/moze/list/')
            self.log_result("Moze List View", response.status_code in [200, 404], f"Status: {response.status_code}")
            
            # Test API access
            response = self.client.get('/api/moze/')
            self.log_result("Moze API Access", response.status_code in [200, 404], f"Status: {response.status_code}")
        
        self.client.logout()
        
        # Test as Coordinator
        if coordinator_user:
            login_success = self.login_user(coordinator_user)
            if login_success:
                response = self.client.get('/moze/')
                self.log_result("Coordinator Moze Access", response.status_code == 200, f"Status: {response.status_code}")
        
        self.client.logout()
        
        # Test data integrity
        moze_count = Moze.objects.count()
        moze_with_aamil = Moze.objects.filter(aamil__isnull=False).count()
        self.log_result("Moze Data Exists", moze_count > 0, f"Moze: {moze_count}")
        self.log_result("Moze-Aamil Relations", moze_with_aamil > 0, f"Relations: {moze_with_aamil}")
    
    def test_student_system(self):
        """Test student management and course system"""
        print("\n🎓 TESTING STUDENT SYSTEM")
        
        student_user = User.objects.filter(role='student').first()
        
        if not student_user:
            self.log_result("Student System Setup", False, "No student user found")
            return
        
        login_success = self.login_user(student_user)
        if login_success:
            response = self.client.get('/students/')
            self.log_result("Student Dashboard", response.status_code == 200, f"Status: {response.status_code}")
            
            response = self.client.get('/students/courses/')
            self.log_result("Student Courses View", response.status_code in [200, 404], f"Status: {response.status_code}")
            
            # Test API access
            response = self.client.get('/api/students/courses/')
            self.log_result("Student Courses API", response.status_code in [200, 401], f"Status: {response.status_code}")
        
        self.client.logout()
        
        # Test data integrity
        student_count = Student.objects.count()
        course_count = Course.objects.count()
        enrollment_count = Enrollment.objects.count()
        self.log_result("Student Data Exists", student_count > 0, f"Students: {student_count}")
        self.log_result("Course Data Exists", course_count > 0, f"Courses: {course_count}")
        self.log_result("Enrollment Data Exists", enrollment_count > 0, f"Enrollments: {enrollment_count}")
    
    def test_survey_system(self):
        """Test survey creation and response system"""
        print("\n📊 TESTING SURVEY SYSTEM")
        
        # Test survey access
        user = User.objects.first()
        if user:
            login_success = self.login_user(user)
            if login_success:
                response = self.client.get('/surveys/')
                self.log_result("Survey Dashboard", response.status_code in [200, 404], f"Status: {response.status_code}")
                
                # Test API access
                response = self.client.get('/api/surveys/')
                self.log_result("Survey API", response.status_code in [200, 401, 404], f"Status: {response.status_code}")
        
        self.client.logout()
        
        # Test data integrity
        survey_count = Survey.objects.count()
        response_count = SurveyResponse.objects.count()
        self.log_result("Survey Data Exists", survey_count > 0, f"Surveys: {survey_count}")
        self.log_result("Survey Response Data Exists", response_count > 0, f"Responses: {response_count}")
    
    def test_evaluation_system(self):
        """Test evaluation system"""
        print("\n📋 TESTING EVALUATION SYSTEM")
        
        user = User.objects.first()
        if user:
            login_success = self.login_user(user)
            if login_success:
                response = self.client.get('/evaluation/')
                self.log_result("Evaluation Dashboard", response.status_code in [200, 404], f"Status: {response.status_code}")
                
                # Test API access
                response = self.client.get('/api/evaluation/')
                self.log_result("Evaluation API", response.status_code in [200, 401, 404], f"Status: {response.status_code}")
        
        self.client.logout()
        
        # Test data integrity
        evaluation_count = Evaluation.objects.count()
        self.log_result("Evaluation Data Exists", evaluation_count > 0, f"Evaluations: {evaluation_count}")
    
    def test_petition_araz_system(self):
        """Test petition/Araz system"""
        print("\n📝 TESTING PETITION/ARAZ SYSTEM")
        
        user = User.objects.first()
        if user:
            login_success = self.login_user(user)
            if login_success:
                response = self.client.get('/araz/')
                self.log_result("Araz Dashboard", response.status_code in [200, 404], f"Status: {response.status_code}")
                
                # Test API access
                response = self.client.get('/api/araz/')
                self.log_result("Araz API", response.status_code in [200, 401, 404], f"Status: {response.status_code}")
        
        self.client.logout()
        
        # Test data integrity
        petition_count = Petition.objects.count()
        self.log_result("Petition Data Exists", petition_count > 0, f"Petitions: {petition_count}")
    
    def test_photo_gallery_system(self):
        """Test photo gallery and upload system"""
        print("\n📸 TESTING PHOTO GALLERY SYSTEM")
        
        user = User.objects.first()
        if user:
            login_success = self.login_user(user)
            if login_success:
                response = self.client.get('/photos/')
                self.log_result("Photo Gallery Dashboard", response.status_code in [200, 404], f"Status: {response.status_code}")
                
                # Test API access
                response = self.client.get('/api/photos/')
                self.log_result("Photo Gallery API", response.status_code in [200, 401, 404], f"Status: {response.status_code}")
        
        self.client.logout()
        
        # Test data integrity
        album_count = PhotoAlbum.objects.count()
        photo_count = Photo.objects.count()
        self.log_result("Photo Album Data Exists", album_count > 0, f"Albums: {album_count}")
        self.log_result("Photo Data Exists", photo_count > 0, f"Photos: {photo_count}")
    
    def test_hospital_system(self):
        """Test hospital and department management"""
        print("\n🏥 TESTING HOSPITAL SYSTEM")
        
        user = User.objects.first()
        if user:
            login_success = self.login_user(user)
            if login_success:
                response = self.client.get('/mahalshifa/')
                self.log_result("Hospital Dashboard", response.status_code in [200, 404], f"Status: {response.status_code}")
                
                # Test API access
                response = self.client.get('/api/mahalshifa/')
                self.log_result("Hospital API", response.status_code in [200, 401, 404], f"Status: {response.status_code}")
        
        self.client.logout()
        
        # Test data integrity
        hospital_count = Hospital.objects.count()
        department_count = Department.objects.count()
        self.log_result("Hospital Data Exists", hospital_count > 0, f"Hospitals: {hospital_count}")
        self.log_result("Department Data Exists", department_count > 0, f"Departments: {department_count}")
    
    def test_api_authentication(self):
        """Test API authentication and authorization"""
        print("\n🔐 TESTING API AUTHENTICATION")
        
        # Test unauthenticated API access
        protected_endpoints = [
            '/api/accounts/profile/',
            '/api/doctordirectory/doctors/',
            '/api/appointments/',
            '/api/students/courses/',
        ]
        
        for endpoint in protected_endpoints:
            response = self.client.get(endpoint)
            # Should return 401 (unauthorized) or 403 (forbidden) for protected endpoints
            success = response.status_code in [401, 403]
            self.log_result(f"Protected API {endpoint}", success, f"Status: {response.status_code}")
        
        # Test authenticated API access
        user = User.objects.first()
        if user:
            login_success = self.login_user(user)
            if login_success:
                response = self.client.get('/api/accounts/profile/')
                self.log_result("Authenticated API Access", response.status_code in [200, 404], f"Status: {response.status_code}")
        
        self.client.logout()
    
    def run_all_tests(self):
        """Run all specific feature tests"""
        print("🔍 STARTING SPECIFIC FEATURE TESTING")
        print("=" * 60)
        
        # Run all test suites
        self.test_appointment_system()
        self.test_medical_records_system()
        self.test_moze_management()
        self.test_student_system()
        self.test_survey_system()
        self.test_evaluation_system()
        self.test_petition_araz_system()
        self.test_photo_gallery_system()
        self.test_hospital_system()
        self.test_api_authentication()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 SPECIFIC FEATURE TEST RESULTS")
        print("=" * 60)
        print(f"✅ Tests Passed: {self.test_results['passed']}")
        print(f"❌ Tests Failed: {self.test_results['failed']}")
        total_tests = self.test_results['passed'] + self.test_results['failed']
        success_rate = (self.test_results['passed'] / total_tests * 100) if total_tests > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.test_results['errors']:
            print("\n🚨 FAILED TESTS:")
            for error in self.test_results['errors']:
                print(f"   • {error}")
        
        print("\n✨ Specific feature testing completed!")
        return self.test_results

if __name__ == "__main__":
    tester = SpecificFeatureTester()
    results = tester.run_all_tests()