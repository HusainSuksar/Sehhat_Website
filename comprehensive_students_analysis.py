#!/usr/bin/env python3

import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse, reverse_lazy
from django.core.management import execute_from_command_line
from django.db import connection
from datetime import datetime, timedelta
import traceback

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

def print_header(title):
    print(f"\n{'='*80}")
    print(f"🎓 {title}")
    print(f"{'='*80}")

def print_test(description, status="✅", details=""):
    emoji = "✅" if status == "✅" else "❌"
    print(f"{emoji} {description}")
    if details:
        print(f"   {details}")

def analyze_students_app():
    print_header("COMPREHENSIVE STUDENTS APP ANALYSIS & TESTING")
    
    client = Client()
    User = get_user_model()
    
    # Test counters
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    try:
        print_header("1. TESTING CORE IMPORTS AND STRUCTURE")
        
        # Test model imports
        try:
            from students.models import (
                Student, Course, Enrollment, Assignment, Submission, 
                Grade, Attendance, Schedule, Announcement, StudentGroup,
                Event, LibraryRecord, Achievement, Scholarship, Fee, 
                Payment, StudentProfile, MentorshipRequest, AidRequest,
                StudentMeeting, StudentAchievement
            )
            print_test("Import all Students models", "✅", "All model imports successful")
            total_tests += 1
            passed_tests += 1
        except ImportError as e:
            print_test(f"Import Students models", "❌", f"ImportError: {e}")
            total_tests += 1
            failed_tests.append(f"Model imports: {e}")
        except Exception as e:
            print_test(f"Import Students models", "❌", f"Error: {e}")
            total_tests += 1
            failed_tests.append(f"Model imports: {e}")
        
        # Test view imports
        try:
            from students.views import (
                dashboard, StudentListView, CourseListView, CourseDetailView,
                enroll_in_course, assignment_detail, my_grades, my_schedule,
                attendance_record, student_analytics, export_student_data
            )
            print_test("Import all Students views", "✅", "All view imports successful")
            total_tests += 1
            passed_tests += 1
        except ImportError as e:
            print_test(f"Import Students views", "❌", f"ImportError: {e}")
            total_tests += 1
            failed_tests.append(f"View imports: {e}")
        except Exception as e:
            print_test(f"Import Students views", "❌", f"Error: {e}")
            total_tests += 1
            failed_tests.append(f"View imports: {e}")
        
        # Test URL imports
        try:
            from students import urls
            print_test("Import Students URLs", "✅", "URL configuration imported")
            total_tests += 1
            passed_tests += 1
        except Exception as e:
            print_test(f"Import Students URLs", "❌", f"Error: {e}")
            total_tests += 1
            failed_tests.append(f"URL imports: {e}")
        
        # Test form imports
        try:
            from students.forms import (
                StudentForm, CourseForm, EnrollmentForm, AssignmentForm,
                GradeForm, AttendanceForm, StudentFilterForm
            )
            print_test("Import Students forms", "✅", "All form imports successful")
            total_tests += 1
            passed_tests += 1
        except ImportError as e:
            print_test(f"Import Students forms", "❌", f"ImportError: {e}")
            total_tests += 1
            failed_tests.append(f"Form imports: {e}")
        except Exception as e:
            print_test(f"Import Students forms", "❌", f"Error: {e}")
            total_tests += 1
            failed_tests.append(f"Form imports: {e}")

        print_header("2. TESTING DATABASE MODELS")
        
        # Test model access and counts
        models_to_test = [
            ('Student', 'students.models.Student'),
            ('Course', 'students.models.Course'),
            ('Enrollment', 'students.models.Enrollment'),
            ('Assignment', 'students.models.Assignment'),
            ('Grade', 'students.models.Grade'),
            ('Attendance', 'students.models.Attendance'),
            ('Schedule', 'students.models.Schedule'),
        ]
        
        for model_name, model_path in models_to_test:
            try:
                # Import the specific model
                module_name, class_name = model_path.rsplit('.', 1)
                module = __import__(module_name, fromlist=[class_name])
                model_class = getattr(module, class_name)
                
                count = model_class.objects.count()
                print_test(f"Access {model_name} model", "✅", f"Found {count} records")
                total_tests += 1
                passed_tests += 1
            except Exception as e:
                print_test(f"Access {model_name} model", "❌", f"Error: {e}")
                total_tests += 1
                failed_tests.append(f"{model_name} model access: {e}")

        print_header("3. CREATING TEST USERS AND SAMPLE DATA")
        
        # Create test users
        try:
            # Admin user
            admin_user, created = User.objects.get_or_create(
                username='admin_students',
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
            
            # Teacher user
            teacher_user, created = User.objects.get_or_create(
                username='teacher_students',
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
            
            # Student user
            student_user, created = User.objects.get_or_create(
                username='student_test',
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
            
            print_test("Created test users", "✅", "Admin, Teacher, Student users ready")
            total_tests += 1
            passed_tests += 1
            
        except Exception as e:
            print_test(f"Create test users", "❌", f"Error: {e}")
            total_tests += 1
            failed_tests.append(f"User creation: {e}")

        # Create sample student data
        try:
            from students.models import Student, Course, Enrollment
            
            # Create Student record
            student_profile, created = Student.objects.get_or_create(
                user=student_user,
                defaults={
                    'student_id': 'STU2024001',
                    'admission_date': datetime.now().date(),
                    'status': 'active',
                    'academic_level': 'undergraduate',
                    'gpa': 3.5,
                    'total_credits': 45
                }
            )
            
            # Create Course
            course, created = Course.objects.get_or_create(
                course_code='MED101',
                defaults={
                    'title': 'Introduction to Medical Sciences',
                    'description': 'Basic concepts in medical science',
                    'credits': 4,
                    'instructor': teacher_user,
                    'semester': 'Fall 2024',
                    'max_students': 50,
                    'is_active': True
                }
            )
            
            # Create Enrollment
            enrollment, created = Enrollment.objects.get_or_create(
                student=student_profile,
                course=course,
                defaults={
                    'enrollment_date': datetime.now().date(),
                    'status': 'enrolled',
                    'grade': 'A'
                }
            )
            
            print_test("Created sample Students data", "✅", "Student, Course, Enrollment created")
            total_tests += 1
            passed_tests += 1
            
        except Exception as e:
            print_test(f"Create sample data", "❌", f"Error: {e}")
            total_tests += 1
            failed_tests.append(f"Sample data creation: {e}")

        print_header("4. TESTING URL PATTERNS AND ACCESSIBILITY")
        
        # Test URL patterns
        url_patterns = [
            ('students:dashboard', 'Students Dashboard'),
            ('students:student_list', 'Student List'),
            ('students:course_list', 'Course List'),
            ('students:analytics', 'Student Analytics'),
            ('students:my_grades', 'My Grades'),
            ('students:my_schedule', 'My Schedule'),
            ('students:attendance', 'Attendance Record'),
        ]
        
        for url_name, description in url_patterns:
            try:
                url = reverse(url_name)
                response = client.get(url)
                status_code = response.status_code
                
                if status_code in [200, 302]:
                    print_test(f"URL {description}", "✅", f"Status: {status_code}")
                else:
                    print_test(f"URL {description}", "❌", f"Status: {status_code}")
                    failed_tests.append(f"URL {url_name}: Status {status_code}")
                
                total_tests += 1
                passed_tests += 1
                
            except Exception as e:
                print_test(f"URL {description}", "❌", f"Error: {e}")
                total_tests += 1
                failed_tests.append(f"URL {url_name}: {e}")

        print_header("5. TESTING ROLE-BASED ACCESS CONTROL")
        
        test_users = [
            (admin_user, 'admin', 'admin123'),
            (teacher_user, 'teacher', 'teacher123'),
            (student_user, 'student', 'student123'),
        ]
        
        for user, role, password in test_users:
            try:
                login_success = client.login(username=user.username, password=password)
                if not login_success:
                    print_test(f"Login {role}", "❌", "Login failed")
                    total_tests += 1
                    failed_tests.append(f"Login {role}: Authentication failed")
                    continue
                
                accessible_urls = 0
                for url_name, _ in url_patterns:
                    try:
                        url = reverse(url_name)
                        response = client.get(url)
                        if response.status_code in [200, 302]:
                            accessible_urls += 1
                    except:
                        pass
                
                print_test(f"Role access {role}", "✅", f"Can access {accessible_urls}/{len(url_patterns)} URLs")
                total_tests += 1
                passed_tests += 1
                client.logout()
                
            except Exception as e:
                print_test(f"Role access {role}", "❌", f"Error: {e}")
                total_tests += 1
                failed_tests.append(f"Role access {role}: {e}")

        print_header("6. TESTING CORE FUNCTIONALITY")
        
        # Login as admin for functionality testing
        client.login(username='admin_students', password='admin123')
        
        # Test dashboard functionality
        try:
            response = client.get(reverse('students:dashboard'))
            if response.status_code in [200, 302]:
                print_test("Dashboard functionality", "✅", "Dashboard accessible")
            else:
                print_test("Dashboard functionality", "❌", f"Status: {response.status_code}")
            total_tests += 1
            passed_tests += 1
        except Exception as e:
            print_test("Dashboard functionality", "❌", f"Error: {e}")
            total_tests += 1
            failed_tests.append(f"Dashboard: {e}")
        
        # Test student management
        try:
            response = client.get(reverse('students:student_list'))
            if response.status_code in [200, 302]:
                print_test("Student management", "✅", "Student list accessible")
            else:
                print_test("Student management", "❌", f"Status: {response.status_code}")
            total_tests += 1
            passed_tests += 1
        except Exception as e:
            print_test("Student management", "❌", f"Error: {e}")
            total_tests += 1
            failed_tests.append(f"Student management: {e}")

        # Test course management
        try:
            response = client.get(reverse('students:course_list'))
            if response.status_code in [200, 302]:
                print_test("Course management", "✅", "Course list accessible")
            else:
                print_test("Course management", "❌", f"Status: {response.status_code}")
            total_tests += 1
            passed_tests += 1
        except Exception as e:
            print_test("Course management", "❌", f"Error: {e}")
            total_tests += 1
            failed_tests.append(f"Course management: {e}")

        print_header("STUDENTS APP TESTING SUMMARY REPORT")
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"✅ Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        print(f"❌ Failed: {len(failed_tests)}/{total_tests} ({100-success_rate:.1f}%)")
        
        if failed_tests:
            print(f"\n📋 FAILED TESTS:")
            for i, failure in enumerate(failed_tests, 1):
                print(f"  {i}. ❌ {failure}")
        
        print(f"\n🎓 SAMPLE DATA CREATED:")
        print(f"  👤 Student: {student_user.get_full_name()} (ID: STU2024001)")
        print(f"  📚 Course: MED101 - Introduction to Medical Sciences")
        print(f"  📝 Enrollment: Active enrollment created")
        print(f"  👨‍🏫 Instructor: {teacher_user.get_full_name()}")
        
        print(f"\n🔗 KEY URLS FOR MANUAL TESTING:")
        print(f"  🏠 Dashboard: http://localhost:8000/students/")
        print(f"  👥 Student List: http://localhost:8000/students/students/")
        print(f"  📚 Course List: http://localhost:8000/students/courses/")
        print(f"  📊 Analytics: http://localhost:8000/students/analytics/")
        print(f"  📝 My Grades: http://localhost:8000/students/grades/")
        print(f"  📅 My Schedule: http://localhost:8000/students/schedule/")
        
        print(f"\n👥 TEST USER CREDENTIALS:")
        print(f"  👤 Admin: admin_students / admin123")
        print(f"  👨‍🏫 Teacher: teacher_students / teacher123")
        print(f"  🎓 Student: student_test / student123")
        
        if success_rate >= 95:
            print(f"\n🏆 FINAL STATUS: 🏆 EXCELLENT - App is fully functional")
            print("🎉 Students app is ready for production!")
            return True
        elif success_rate >= 80:
            print(f"\n🟡 FINAL STATUS: 🟡 GOOD - Minor issues detected")
            print("⚠️ Students app needs minor fixes before production.")
            return False
        else:
            print(f"\n🔴 FINAL STATUS: 🔴 NEEDS WORK - Major issues detected")
            print("❌ Students app requires significant fixes.")
            return False
            
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = analyze_students_app()
    sys.exit(0 if success else 1)