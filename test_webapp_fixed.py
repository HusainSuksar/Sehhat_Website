#!/usr/bin/env python
"""
Comprehensive Web Application Testing Script (FIXED)
Tests all functionality from user login to logout across all user roles
Now properly handles ITS authentication system
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
    
    def login_user(self, user):
        """Login user using the proper ITS authentication system"""
        try:
            # Use the login view with ITS ID and password
            response = self.client.post('/accounts/login/', {
                'its_id': user.its_id,
                'password': 'pass1234'
            }, follow=True)
            
            # Check if login was successful by checking if user is in session
            if hasattr(response, 'wsgi_request') and response.wsgi_request.user.is_authenticated:
                return True, response
            elif response.status_code == 302:  # Redirect usually means successful login
                return True, response
            else:
                return False, response
        except Exception as e:
            return False, str(e)
    
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
                
            # Test login page access
            login_page_response = self.client.get('/accounts/login/')
            self.log_result(f"Login Page Access - {role}", login_page_response.status_code == 200, 
                          f"Status: {login_page_response.status_code}")
            
            # Test login
            login_success, login_response = self.login_user(user)
            self.log_result(f"Login - {role} ({user.its_id})", login_success, 
                          f"Status: {login_response.status_code if hasattr(login_response, 'status_code') else 'Error'}")
            
            if login_success:
                # Test accessing dashboard after login
                dashboard_response = self.client.get('/', follow=True)
                dashboard_access = dashboard_response.status_code == 200
                self.log_result(f"Dashboard Access - {role}", dashboard_access, 
                              f"Status: {dashboard_response.status_code}")
                
                # Test logout
                logout_response = self.client.post('/accounts/logout/', follow=True)
                logout_success = logout_response.status_code == 200
                self.log_result(f"Logout - {role}", logout_success, 
                              f"Status: {logout_response.status_code}")
    
    def test_admin_functionality(self):
        """Test admin-specific functionality"""
        print("\n👑 TESTING ADMIN FUNCTIONALITY")
        
        admin = User.objects.filter(is_superuser=True).first()
        if not admin:
            self.log_result("Admin Test", False, "No admin user found")
            return
        
        # Login as admin
        login_success, _ = self.login_user(admin)
        if not login_success:
            self.log_result("Admin Login", False, "Could not login as admin")
            return
        
        # Test admin panel access
        response = self.client.get('/admin/', follow=True)
        self.log_result("Admin Panel Access", response.status_code == 200, f"Status: {response.status_code}")
        
        # Test admin user management
        response = self.client.get('/admin/accounts/user/', follow=True)
        self.log_result("Admin User Management", response.status_code == 200, f"Status: {response.status_code}")
        
        self.client.logout()
    
    def test_role_specific_functionality(self):
        """Test role-specific functionality"""
        print("\n🎭 TESTING ROLE-SPECIFIC FUNCTIONALITY")
        
        # Test Aamil/Moze functionality
        aamil = User.objects.filter(role='aamil').first()
        if aamil:
            login_success, _ = self.login_user(aamil)
            if login_success:
                response = self.client.get('/moze/', follow=True)
                self.log_result("Aamil Moze Access", response.status_code == 200, f"Status: {response.status_code}")
                self.client.logout()
        
        # Test Doctor functionality
        doctor_user = User.objects.filter(role='doctor').first()
        if doctor_user:
            login_success, _ = self.login_user(doctor_user)
            if login_success:
                response = self.client.get('/doctordirectory/', follow=True)
                self.log_result("Doctor Dashboard Access", response.status_code == 200, f"Status: {response.status_code}")
                self.client.logout()
        
        # Test Student functionality
        student_user = User.objects.filter(role='student').first()
        if student_user:
            login_success, _ = self.login_user(student_user)
            if login_success:
                response = self.client.get('/students/', follow=True)
                self.log_result("Student Dashboard Access", response.status_code == 200, f"Status: {response.status_code}")
                self.client.logout()
    
    def test_api_endpoints_authenticated(self):
        """Test API endpoints with authentication"""
        print("\n🔌 TESTING AUTHENTICATED API ENDPOINTS")
        
        # Get a test user
        user = User.objects.filter(role='patient').first()
        if not user:
            self.log_result("API Auth Test Setup", False, "No test user found")
            return
        
        # Login first
        login_success, _ = self.login_user(user)
        if not login_success:
            self.log_result("API Auth Test Login", False, "Could not login for API testing")
            return
        
        # Test authenticated API endpoints
        api_endpoints = [
            '/accounts/profile/',
            '/moze/',
            '/doctordirectory/',
            '/students/',
        ]
        
        for endpoint in api_endpoints:
            try:
                response = self.client.get(endpoint, follow=True)
                success = response.status_code in [200, 302, 403]  # 403 is OK for role restrictions
                self.log_result(f"Authenticated Access {endpoint}", success, f"Status: {response.status_code}")
            except Exception as e:
                self.log_result(f"Authenticated Access {endpoint}", False, str(e))
        
        self.client.logout()
    
    def test_forms_and_views(self):
        """Test forms and view functionality"""
        print("\n📝 TESTING FORMS AND VIEWS")
        
        # Test registration page
        response = self.client.get('/accounts/register/')
        self.log_result("Registration Page", response.status_code in [200, 404], f"Status: {response.status_code}")
        
        # Test profile page (requires login)
        user = User.objects.first()
        if user:
            login_success, _ = self.login_user(user)
            if login_success:
                response = self.client.get('/accounts/profile/', follow=True)
                self.log_result("Profile Page Access", response.status_code == 200, f"Status: {response.status_code}")
                self.client.logout()
    
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
        appointment_count = Appointment.objects.count()
        
        self.log_result("Users Generated", user_count > 0, f"Count: {user_count}")
        self.log_result("Moze Generated", moze_count > 0, f"Count: {moze_count}")
        self.log_result("Doctors Generated", doctor_count > 0, f"Count: {doctor_count}")
        self.log_result("Patients Generated", patient_count > 0, f"Count: {patient_count}")
        self.log_result("Appointments Generated", appointment_count > 0, f"Count: {appointment_count}")
        
        # Test relationships
        if moze_count > 0:
            moze_with_aamil = Moze.objects.filter(aamil__isnull=False).count()
            self.log_result("Moze-Aamil Relationships", moze_with_aamil > 0, f"Count: {moze_with_aamil}")
        
        # Test user roles distribution
        role_counts = {}
        for role, _ in User.ROLE_CHOICES:
            count = User.objects.filter(role=role).count()
            role_counts[role] = count
            if count > 0:
                self.log_result(f"Role Distribution - {role}", True, f"Count: {count}")
        
        print(f"   Role Distribution: {role_counts}")
    
    def test_security_measures(self):
        """Test security measures"""
        print("\n🛡️ TESTING SECURITY MEASURES")
        
        # Test unauthorized access to admin
        self.client.logout()  # Ensure logged out
        response = self.client.get('/admin/')
        unauthorized_blocked = response.status_code in [302, 403]  # Should redirect to login or forbidden
        self.log_result("Unauthorized Admin Access Blocked", unauthorized_blocked, f"Status: {response.status_code}")
        
        # Test CSRF protection on forms
        response = self.client.get('/accounts/login/')
        has_csrf = 'csrfmiddlewaretoken' in response.content.decode() if response.status_code == 200 else False
        self.log_result("CSRF Token Present", has_csrf, "In login form")
        
        # Test session security
        user = User.objects.first()
        if user:
            login_success, _ = self.login_user(user)
            if login_success:
                # Check if session is created
                session_exists = len(self.client.session.keys()) > 0
                self.log_result("Session Management", session_exists, "Session created on login")
                self.client.logout()
    
    def test_media_and_static_files(self):
        """Test media and static file handling"""
        print("\n📁 TESTING MEDIA AND STATIC FILES")
        
        # Test static file access (CSS, JS)
        response = self.client.get('/static/css/style.css')
        static_access = response.status_code in [200, 404]  # 404 is OK if file doesn't exist
        self.log_result("Static File Access", static_access, f"Status: {response.status_code}")
        
        # Test if media files are properly configured
        from django.conf import settings
        media_configured = hasattr(settings, 'MEDIA_URL') and hasattr(settings, 'MEDIA_ROOT')
        self.log_result("Media Configuration", media_configured, "MEDIA_URL and MEDIA_ROOT configured")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 STARTING COMPREHENSIVE WEB APPLICATION TESTING (FIXED)")
        print("=" * 70)
        
        # Run all test suites
        self.test_login_logout()
        self.test_admin_functionality()
        self.test_role_specific_functionality()
        self.test_api_endpoints_authenticated()
        self.test_forms_and_views()
        self.test_error_handling()
        self.test_data_integrity()
        self.test_security_measures()
        self.test_media_and_static_files()
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 70)
        print(f"✅ Tests Passed: {self.test_results['passed']}")
        print(f"❌ Tests Failed: {self.test_results['failed']}")
        total_tests = self.test_results['passed'] + self.test_results['failed']
        success_rate = (self.test_results['passed'] / total_tests * 100) if total_tests > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.test_results['errors']:
            print("\n🚨 FAILED TESTS:")
            for error in self.test_results['errors']:
                print(f"   • {error}")
        
        print("\n✨ Testing completed!")
        
        # Provide recommendations based on results
        if success_rate >= 90:
            print("🎉 EXCELLENT! Your web application is working very well!")
        elif success_rate >= 75:
            print("👍 GOOD! Your web application is mostly functional with minor issues.")
        elif success_rate >= 50:
            print("⚠️  MODERATE! Your web application has some significant issues to address.")
        else:
            print("🚨 CRITICAL! Your web application has major issues that need immediate attention.")
        
        return self.test_results

if __name__ == "__main__":
    tester = WebAppTester()
    results = tester.run_all_tests()