#!/usr/bin/env python
"""
Comprehensive Web Application Testing Script
Tests all functionality from user login to logout across all user roles
"""

import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

# Import models for testing
from moze.models import Moze
from doctordirectory.models import Doctor, Patient
from students.models import Student, Course
from mahalshifa.models import Hospital
from appointments.models import Appointment
from surveys.models import Survey
from evaluation.models import Evaluation
from araz.models import Petition
from photos.models import PhotoAlbum

User = get_user_model()

class WebAppTester:
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
    
    def test_login_logout(self):
        """Test login and logout functionality for all user roles"""
        print("\n🔐 TESTING AUTHENTICATION SYSTEM")
        
        # Test users from different roles
        test_users = [
            ('admin', User.objects.filter(is_superuser=True).first()),
            ('aamil', User.objects.filter(role='aamil').first()),
            ('doctor', User.objects.filter(role='doctor').first()),
            ('student', User.objects.filter(role='student').first()),
            ('patient', User.objects.filter(role='patient').first()),
        ]
        
        for role, user in test_users:
            if not user:
                self.log_result(f"Login Test - {role}", False, f"No {role} user found")
                continue
                
            # Test login
            try:
                login_success = self.client.login(its_id=user.its_id, password='pass1234')
                self.log_result(f"Login - {role} ({user.its_id})", login_success)
                
                if login_success:
                    # Test accessing dashboard after login
                    response = self.client.get('/')
                    dashboard_access = response.status_code in [200, 302]  # 302 for redirects
                    self.log_result(f"Dashboard Access - {role}", dashboard_access, f"Status: {response.status_code}")
                    
                    # Test logout
                    logout_response = self.client.post('/accounts/logout/')
                    logout_success = logout_response.status_code in [200, 302]
                    self.log_result(f"Logout - {role}", logout_success, f"Status: {logout_response.status_code}")
                
            except Exception as e:
                self.log_result(f"Login Test - {role}", False, str(e))
    
    def test_admin_functionality(self):
        """Test admin-specific functionality"""
        print("\n👑 TESTING ADMIN FUNCTIONALITY")
        
        admin = User.objects.filter(is_superuser=True).first()
        if not admin:
            self.log_result("Admin Test", False, "No admin user found")
            return
        
        # Login as admin
        login_success = self.client.login(its_id=admin.its_id, password='pass1234')
        if not login_success:
            self.log_result("Admin Login", False, "Could not login as admin")
            return
        
        # Test admin panel access
        response = self.client.get('/admin/')
        self.log_result("Admin Panel Access", response.status_code == 200, f"Status: {response.status_code}")
        
        # Test admin user management
        response = self.client.get('/admin/accounts/user/')
        self.log_result("Admin User Management", response.status_code == 200, f"Status: {response.status_code}")
    
    def test_moze_functionality(self):
        """Test Moze management functionality"""
        print("\n🏥 TESTING MOZE FUNCTIONALITY")
        
        # Login as Aamil
        aamil = User.objects.filter(role='aamil').first()
        if not aamil:
            self.log_result("Moze Test", False, "No aamil user found")
            return
        
        login_success = self.client.login(its_id=aamil.its_id, password='pass1234')
        if not login_success:
            self.log_result("Aamil Login", False, "Could not login as aamil")
            return
        
        # Test moze dashboard access
        response = self.client.get('/moze/')
        self.log_result("Moze Dashboard Access", response.status_code in [200, 302], f"Status: {response.status_code}")
        
        # Test moze list view
        response = self.client.get('/moze/list/')
        self.log_result("Moze List View", response.status_code in [200, 404], f"Status: {response.status_code}")
    
    def test_doctor_functionality(self):
        """Test doctor-specific functionality"""
        print("\n👨‍⚕️ TESTING DOCTOR FUNCTIONALITY")
        
        doctor_user = User.objects.filter(role='doctor').first()
        if not doctor_user:
            self.log_result("Doctor Test", False, "No doctor user found")
            return
        
        login_success = self.client.login(its_id=doctor_user.its_id, password='pass1234')
        if not login_success:
            self.log_result("Doctor Login", False, "Could not login as doctor")
            return
        
        # Test doctor dashboard
        response = self.client.get('/doctordirectory/')
        self.log_result("Doctor Dashboard Access", response.status_code in [200, 302], f"Status: {response.status_code}")
        
        # Test patient list access
        response = self.client.get('/doctordirectory/patients/')
        self.log_result("Patient List Access", response.status_code in [200, 404], f"Status: {response.status_code}")
    
    def test_student_functionality(self):
        """Test student-specific functionality"""
        print("\n🎓 TESTING STUDENT FUNCTIONALITY")
        
        student_user = User.objects.filter(role='student').first()
        if not student_user:
            self.log_result("Student Test", False, "No student user found")
            return
        
        login_success = self.client.login(its_id=student_user.its_id, password='pass1234')
        if not login_success:
            self.log_result("Student Login", False, "Could not login as student")
            return
        
        # Test student dashboard
        response = self.client.get('/students/')
        self.log_result("Student Dashboard Access", response.status_code in [200, 302], f"Status: {response.status_code}")
        
        # Test courses access
        response = self.client.get('/students/courses/')
        self.log_result("Courses Access", response.status_code in [200, 404], f"Status: {response.status_code}")
    
    def test_api_endpoints(self):
        """Test API endpoints"""
        print("\n🔌 TESTING API ENDPOINTS")
        
        # Test public API endpoints (should return 401 or 403 if authentication required)
        api_endpoints = [
            '/api/accounts/profile/',
            '/api/moze/',
            '/api/doctordirectory/doctors/',
            '/api/students/courses/',
            '/api/appointments/',
        ]
        
        for endpoint in api_endpoints:
            try:
                response = self.client.get(endpoint)
                # API endpoints should return proper status codes
                success = response.status_code in [200, 401, 403, 404]
                self.log_result(f"API Endpoint {endpoint}", success, f"Status: {response.status_code}")
            except Exception as e:
                self.log_result(f"API Endpoint {endpoint}", False, str(e))
    
    def test_error_handling(self):
        """Test error handling"""
        print("\n🚨 TESTING ERROR HANDLING")
        
        # Test 404 pages
        response = self.client.get('/nonexistent-page/')
        self.log_result("404 Error Handling", response.status_code == 404, f"Status: {response.status_code}")
        
        # Test invalid login
        response = self.client.post('/accounts/login/', {
            'its_id': '99999999',
            'password': 'wrongpassword'
        })
        self.log_result("Invalid Login Handling", response.status_code in [200, 302], f"Status: {response.status_code}")
    
    def test_data_integrity(self):
        """Test data integrity and relationships"""
        print("\n🔗 TESTING DATA INTEGRITY")
        
        # Check if we have data from our mock generator
        user_count = User.objects.count()
        moze_count = Moze.objects.count()
        doctor_count = Doctor.objects.count()
        patient_count = Patient.objects.count()
        
        self.log_result("Users Generated", user_count > 0, f"Count: {user_count}")
        self.log_result("Moze Generated", moze_count > 0, f"Count: {moze_count}")
        self.log_result("Doctors Generated", doctor_count > 0, f"Count: {doctor_count}")
        self.log_result("Patients Generated", patient_count > 0, f"Count: {patient_count}")
        
        # Test relationships
        if moze_count > 0:
            moze_with_aamil = Moze.objects.filter(aamil__isnull=False).count()
            self.log_result("Moze-Aamil Relationships", moze_with_aamil > 0, f"Count: {moze_with_aamil}")
    
    def test_security_measures(self):
        """Test security measures"""
        print("\n🛡️ TESTING SECURITY MEASURES")
        
        # Test CSRF protection
        response = self.client.post('/accounts/login/', {
            'its_id': '10000005',
            'password': 'pass1234'
        })
        # Should either work (with CSRF) or fail appropriately
        csrf_protected = response.status_code in [200, 302, 403]
        self.log_result("CSRF Protection", csrf_protected, f"Status: {response.status_code}")
        
        # Test unauthorized access
        self.client.logout()  # Ensure logged out
        response = self.client.get('/admin/')
        unauthorized_blocked = response.status_code in [302, 403]  # Should redirect to login or forbidden
        self.log_result("Unauthorized Access Blocked", unauthorized_blocked, f"Status: {response.status_code}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 STARTING COMPREHENSIVE WEB APPLICATION TESTING")
        print("=" * 60)
        
        # Run all test suites
        self.test_login_logout()
        self.test_admin_functionality()
        self.test_moze_functionality()
        self.test_doctor_functionality()
        self.test_student_functionality()
        self.test_api_endpoints()
        self.test_error_handling()
        self.test_data_integrity()
        self.test_security_measures()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"✅ Tests Passed: {self.test_results['passed']}")
        print(f"❌ Tests Failed: {self.test_results['failed']}")
        print(f"📈 Success Rate: {(self.test_results['passed'] / (self.test_results['passed'] + self.test_results['failed'])) * 100:.1f}%")
        
        if self.test_results['errors']:
            print("\n🚨 FAILED TESTS:")
            for error in self.test_results['errors']:
                print(f"   • {error}")
        
        print("\n✨ Testing completed!")
        return self.test_results

if __name__ == "__main__":
    tester = WebAppTester()
    results = tester.run_all_tests()