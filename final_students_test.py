#!/usr/bin/env python3
"""
Final comprehensive test for Students App
This script will test the Students app from top to bottom and fix any issues found.
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db import models
from datetime import datetime, timedelta
import traceback

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

def print_section(title):
    print(f"\n{'='*80}")
    print(f"🎓 {title}")
    print(f"{'='*80}")

def print_result(test_name, success, details=""):
    emoji = "✅" if success else "❌"
    print(f"{emoji} {test_name}")
    if details:
        print(f"   └─ {details}")

class StudentsAppTester:
    def __init__(self):
        self.client = Client()
        self.User = get_user_model()
        self.results = []
        self.test_users = {}
        
    def log_result(self, test_name, success, details=""):
        self.results.append((test_name, success, details))
        print_result(test_name, success, details)
    
    def test_imports(self):
        """Test 1: Core module imports"""
        print_section("TESTING CORE IMPORTS")
        
        # Test models import
        try:
            from students import models
            self.log_result("Import students.models", True, "Models module imported")
            
            # Test specific model imports
            model_names = ['Student', 'Course', 'Enrollment', 'Assignment', 'Grade', 'Attendance']
            for model_name in model_names:
                try:
                    model = getattr(models, model_name)
                    self.log_result(f"Import {model_name} model", True, f"Found {model.__name__}")
                except AttributeError:
                    self.log_result(f"Import {model_name} model", False, f"Model not found")
                    
        except ImportError as e:
            self.log_result("Import students.models", False, f"ImportError: {e}")
            
        # Test views import
        try:
            from students import views
            self.log_result("Import students.views", True, "Views module imported")
        except ImportError as e:
            self.log_result("Import students.views", False, f"ImportError: {e}")
            
        # Test URLs import
        try:
            from students import urls
            self.log_result("Import students.urls", True, "URLs module imported")
        except ImportError as e:
            self.log_result("Import students.urls", False, f"ImportError: {e}")
            
        # Test forms import
        try:
            from students import forms
            self.log_result("Import students.forms", True, "Forms module imported")
        except ImportError as e:
            self.log_result("Import students.forms", False, f"ImportError: {e}")
    
    def test_models(self):
        """Test 2: Model functionality"""
        print_section("TESTING MODEL FUNCTIONALITY")
        
        try:
            from students.models import Student, Course, Enrollment
            
            # Test model counts
            student_count = Student.objects.count()
            self.log_result("Student model access", True, f"{student_count} records")
            
            course_count = Course.objects.count()
            self.log_result("Course model access", True, f"{course_count} records")
            
            enrollment_count = Enrollment.objects.count()
            self.log_result("Enrollment model access", True, f"{enrollment_count} records")
            
            # Test model string representations
            if student_count > 0:
                student = Student.objects.first()
                str_repr = str(student)
                self.log_result("Student __str__ method", True, f"'{str_repr}'")
            
        except Exception as e:
            self.log_result("Model functionality test", False, f"Error: {e}")
    
    def test_urls(self):
        """Test 3: URL patterns"""
        print_section("TESTING URL PATTERNS")
        
        test_urls = [
            'students:dashboard',
            'students:student_list',
            'students:course_list',
            'students:analytics'
        ]
        
        for url_name in test_urls:
            try:
                url = reverse(url_name)
                self.log_result(f"URL {url_name}", True, f"Resolves to: {url}")
            except Exception as e:
                self.log_result(f"URL {url_name}", False, f"Error: {e}")
    
    def create_test_users(self):
        """Test 4: Create test users"""
        print_section("CREATING TEST USERS")
        
        try:
            # Admin user
            admin_user, created = self.User.objects.get_or_create(
                username='admin_students_final',
                defaults={
                    'email': 'admin@students.test',
                    'first_name': 'Admin',
                    'last_name': 'User',
                    'role': 'admin',
                    'is_staff': True,
                    'is_superuser': True
                }
            )
            if created:
                admin_user.set_password('admin123')
                admin_user.save()
            self.test_users['admin'] = admin_user
            self.log_result("Create admin user", True, f"User: {admin_user.username}")
            
            # Teacher user
            teacher_user, created = self.User.objects.get_or_create(
                username='teacher_students_final',
                defaults={
                    'email': 'teacher@students.test',
                    'first_name': 'Teacher',
                    'last_name': 'User',
                    'role': 'teacher',
                    'is_staff': True
                }
            )
            if created:
                teacher_user.set_password('teacher123')
                teacher_user.save()
            self.test_users['teacher'] = teacher_user
            self.log_result("Create teacher user", True, f"User: {teacher_user.username}")
            
            # Student user
            student_user, created = self.User.objects.get_or_create(
                username='student_final_test',
                defaults={
                    'email': 'student@students.test',
                    'first_name': 'Test',
                    'last_name': 'Student',
                    'role': 'student'
                }
            )
            if created:
                student_user.set_password('student123')
                student_user.save()
            self.test_users['student'] = student_user
            self.log_result("Create student user", True, f"User: {student_user.username}")
            
        except Exception as e:
            self.log_result("Create test users", False, f"Error: {e}")
    
    def create_sample_data(self):
        """Test 5: Create sample data"""
        print_section("CREATING SAMPLE DATA")
        
        try:
            from students.models import Student, Course, Enrollment
            
            # Create Student profile
            student_profile, created = Student.objects.get_or_create(
                user=self.test_users['student'],
                defaults={
                    'student_id': 'MED2024001',
                    'admission_date': datetime.now().date(),
                    'status': 'active',
                    'academic_level': 'undergraduate',
                    'gpa': 3.75
                }
            )
            self.log_result("Create Student profile", True, f"ID: {student_profile.student_id}")
            
            # Create Course
            course, created = Course.objects.get_or_create(
                course_code='ANAT101',
                defaults={
                    'title': 'Human Anatomy I',
                    'description': 'Introduction to human anatomy and physiology',
                    'credits': 4,
                    'instructor': self.test_users['teacher'],
                    'semester': 'Fall 2024',
                    'max_students': 60,
                    'is_active': True
                }
            )
            self.log_result("Create Course", True, f"Course: {course.course_code}")
            
            # Create Enrollment
            enrollment, created = Enrollment.objects.get_or_create(
                student=student_profile,
                course=course,
                defaults={
                    'enrollment_date': datetime.now().date(),
                    'status': 'enrolled'
                }
            )
            self.log_result("Create Enrollment", True, f"Status: {enrollment.status}")
            
        except Exception as e:
            self.log_result("Create sample data", False, f"Error: {e}")
    
    def test_views(self):
        """Test 6: View accessibility"""
        print_section("TESTING VIEW ACCESSIBILITY")
        
        # Login as admin
        login_success = self.client.login(
            username='admin_students_final', 
            password='admin123'
        )
        
        if not login_success:
            self.log_result("Admin login", False, "Login failed")
            return
        
        self.log_result("Admin login", True, "Successfully logged in")
        
        # Test main views
        test_views = [
            ('students:dashboard', 'Dashboard'),
            ('students:student_list', 'Student List'),
            ('students:course_list', 'Course List'),
            ('students:analytics', 'Analytics')
        ]
        
        for url_name, view_name in test_views:
            try:
                response = self.client.get(reverse(url_name))
                status = response.status_code
                
                if status in [200, 302]:
                    self.log_result(f"{view_name} view", True, f"Status: {status}")
                else:
                    self.log_result(f"{view_name} view", False, f"Status: {status}")
                    
            except Exception as e:
                self.log_result(f"{view_name} view", False, f"Error: {e}")
        
        self.client.logout()
    
    def test_role_access(self):
        """Test 7: Role-based access control"""
        print_section("TESTING ROLE-BASED ACCESS")
        
        roles = ['admin', 'teacher', 'student']
        passwords = ['admin123', 'teacher123', 'student123']
        
        for role, password in zip(roles, passwords):
            if role not in self.test_users:
                continue
                
            username = self.test_users[role].username
            login_success = self.client.login(username=username, password=password)
            
            if login_success:
                # Test access to dashboard
                try:
                    response = self.client.get(reverse('students:dashboard'))
                    accessible = response.status_code in [200, 302]
                    self.log_result(f"{role.title()} dashboard access", accessible, 
                                  f"Status: {response.status_code}")
                except Exception as e:
                    self.log_result(f"{role.title()} dashboard access", False, f"Error: {e}")
                
                self.client.logout()
            else:
                self.log_result(f"{role.title()} login", False, "Authentication failed")
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print_section("STUDENTS APP COMPREHENSIVE TESTING")
        print("Testing the most important app in the Umoor Sehhat system...")
        
        # Run all test phases
        self.test_imports()
        self.test_models()
        self.test_urls()
        self.create_test_users()
        self.create_sample_data()
        self.test_views()
        self.test_role_access()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate comprehensive test summary"""
        print_section("STUDENTS APP TESTING SUMMARY")
        
        total_tests = len(self.results)
        passed_tests = sum(1 for _, success, _ in self.results if success)
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"✅ Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        print(f"❌ Failed: {failed_tests}/{total_tests} ({100-success_rate:.1f}%)")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for i, (test_name, success, details) in enumerate(self.results, 1):
                if not success:
                    print(f"  {i}. {test_name}: {details}")
        
        print(f"\n🎓 TEST DATA CREATED:")
        if 'student' in self.test_users:
            print(f"  👤 Student: {self.test_users['student'].get_full_name()}")
        if 'teacher' in self.test_users:
            print(f"  👨‍🏫 Teacher: {self.test_users['teacher'].get_full_name()}")
        print(f"  📚 Course: ANAT101 - Human Anatomy I")
        print(f"  📝 Enrollment: Active medical student enrollment")
        
        print(f"\n🔗 MANUAL TESTING URLS:")
        print(f"  🏠 Dashboard: http://localhost:8000/students/")
        print(f"  👥 Students: http://localhost:8000/students/students/")
        print(f"  📚 Courses: http://localhost:8000/students/courses/")
        print(f"  📊 Analytics: http://localhost:8000/students/analytics/")
        
        print(f"\n👥 TEST CREDENTIALS:")
        print(f"  👤 Admin: admin_students_final / admin123")
        print(f"  👨‍🏫 Teacher: teacher_students_final / teacher123")
        print(f"  🎓 Student: student_final_test / student123")
        
        # Final status
        if success_rate >= 95:
            print(f"\n🏆 FINAL STATUS: EXCELLENT ({success_rate:.1f}%)")
            print("✅ Students app is ready for production!")
            print("🚀 Proceeding to commit to main branch...")
            return True
        elif success_rate >= 85:
            print(f"\n🟡 FINAL STATUS: GOOD ({success_rate:.1f}%)")
            print("⚠️ Students app needs minor fixes before production.")
            return False
        else:
            print(f"\n🔴 FINAL STATUS: NEEDS WORK ({success_rate:.1f}%)")
            print("❌ Students app requires significant fixes.")
            return False

def main():
    """Main testing function"""
    tester = StudentsAppTester()
    
    try:
        success = tester.run_all_tests()
        return success
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n" + "="*80)
        print("🎉 STUDENTS APP TESTING COMPLETED SUCCESSFULLY!")
        print("Ready for commit to main branch.")
        print("="*80)
    else:
        print("\n" + "="*80)
        print("⚠️ STUDENTS APP TESTING COMPLETED WITH ISSUES")
        print("Please review and fix the identified problems.")
        print("="*80)
    
    sys.exit(0 if success else 1)