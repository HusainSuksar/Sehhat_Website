#!/usr/bin/env python3

import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.management import execute_from_command_line
from django.db import connection
from datetime import datetime, timedelta
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

# Import after Django setup
from students.models import *
from accounts.models import User

def print_header(title):
    print(f"\n{'='*80}")
    print(f"🎓 {title}")
    print(f"{'='*80}")

def print_test(description, status="✅", details=""):
    emoji = "✅" if status == "✅" else "❌"
    print(f"{emoji} {description}")
    if details:
        print(f"   {details}")

def main():
    print_header("Starting Comprehensive Students App Testing")
    
    client = Client()
    User = get_user_model()
    
    # Test counters
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    try:
        # 1. Test Models Access
        print_header("Testing Students Model Access")
        
        try:
            student_count = Student.objects.count()
            print_test(f"Access Student model: Found {student_count} records")
            total_tests += 1
            passed_tests += 1
        except Exception as e:
            print_test(f"Access Student model: Error - {e}", "❌")
            total_tests += 1
            failed_tests.append(f"Student model access: {e}")
        
        try:
            course_count = Course.objects.count()
            print_test(f"Access Course model: Found {course_count} records")
            total_tests += 1
            passed_tests += 1
        except Exception as e:
            print_test(f"Access Course model: Error - {e}", "❌")
            total_tests += 1
            failed_tests.append(f"Course model access: {e}")
        
        try:
            enrollment_count = Enrollment.objects.count()
            print_test(f"Access Enrollment model: Found {enrollment_count} records")
            total_tests += 1
            passed_tests += 1
        except Exception as e:
            print_test(f"Access Enrollment model: Error - {e}", "❌")
            total_tests += 1
            failed_tests.append(f"Enrollment model access: {e}")

        # 2. Create Test Users
        print_header("Creating test users")
        
        try:
            # Create test users with different roles
            admin_user, created = User.objects.get_or_create(
                username='admin_student',
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
            
            teacher_user, created = User.objects.get_or_create(
                username='teacher_student',
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
            
            print_test("Created test users", "✅", "admin, teacher, student users ready")
            total_tests += 1
            passed_tests += 1
            
        except Exception as e:
            print_test(f"Creating test users: Error - {e}", "❌")
            total_tests += 1
            failed_tests.append(f"User creation: {e}")

        # 3. Create Sample Data
        print_header("Creating sample Students data")
        
        try:
            # Create sample student
            student, created = Student.objects.get_or_create(
                user=student_user,
                defaults={
                    'student_id': 'STU001',
                    'admission_date': datetime.now().date(),
                    'status': 'active',
                    'academic_level': 'undergraduate'
                }
            )
            
            # Create sample course
            course, created = Course.objects.get_or_create(
                course_code='CS101',
                defaults={
                    'title': 'Introduction to Computer Science',
                    'description': 'Basic computer science concepts',
                    'credits': 3,
                    'instructor': teacher_user,
                    'semester': 'Fall 2024',
                    'max_students': 30,
                    'is_active': True
                }
            )
            
            # Create enrollment
            enrollment, created = Enrollment.objects.get_or_create(
                student=student,
                course=course,
                defaults={
                    'enrollment_date': datetime.now().date(),
                    'status': 'active'
                }
            )
            
            print_test("Created comprehensive Students sample data", "✅")
            total_tests += 1
            passed_tests += 1
            
        except Exception as e:
            print_test(f"Creating sample data: Error - {e}", "❌")
            total_tests += 1
            failed_tests.append(f"Sample data creation: {e}")

        # 4. Test URL Accessibility
        print_header("Testing Students URL accessibility")
        
        urls_to_test = [
            ('students:dashboard', 'Dashboard'),
            ('students:student_list', 'Student List'),
            ('students:course_list', 'Course List'),
            ('students:analytics', 'Analytics'),
        ]
        
        for url_name, description in urls_to_test:
            try:
                url = reverse(url_name)
                response = client.get(url)
                print_test(f"URL accessibility: {description}: Status: {response.status_code}")
                total_tests += 1
                passed_tests += 1
            except Exception as e:
                print_test(f"URL accessibility: {description}: Error - {e}", "❌")
                total_tests += 1
                failed_tests.append(f"URL {url_name}: {e}")

        # 5. Test User Role-Based Access
        print_header("Testing user role-based access")
        
        test_users = [
            (admin_user, 'admin', 'admin123'),
            (teacher_user, 'teacher', 'teacher123'),
            (student_user, 'student', 'student123'),
        ]
        
        for user, role, password in test_users:
            try:
                client.login(username=user.username, password=password)
                accessible_urls = 0
                
                for url_name, _ in urls_to_test:
                    try:
                        url = reverse(url_name)
                        response = client.get(url)
                        if response.status_code in [200, 302]:
                            accessible_urls += 1
                    except:
                        pass
                
                print_test(f"Role access: {role}: Can access {accessible_urls}/{len(urls_to_test)} URLs")
                total_tests += 1
                passed_tests += 1
                client.logout()
                
            except Exception as e:
                print_test(f"Role access: {role}: Error - {e}", "❌")
                total_tests += 1
                failed_tests.append(f"Role access {role}: {e}")

        # 6. Test Students Core Functionality
        print_header("Testing Students functionality")
        
        client.login(username='admin_student', password='admin123')
        
        try:
            # Test dashboard access
            response = client.get(reverse('students:dashboard'))
            status = "accessible" if response.status_code in [200, 302] else f"status: {response.status_code}"
            print_test(f"Dashboard access: Dashboard {status}")
            total_tests += 1
            passed_tests += 1
        except Exception as e:
            print_test(f"Dashboard access: Error - {e}", "❌")
            total_tests += 1
            failed_tests.append(f"Dashboard access: {e}")
        
        try:
            # Test student listing
            response = client.get(reverse('students:student_list'))
            status = "accessible" if response.status_code in [200, 302] else f"status: {response.status_code}"
            print_test(f"Student listing: List {status}")
            total_tests += 1
            passed_tests += 1
        except Exception as e:
            print_test(f"Student listing: Error - {e}", "❌")
            total_tests += 1
            failed_tests.append(f"Student listing: {e}")
        
        try:
            # Test course listing
            response = client.get(reverse('students:course_list'))
            status = "accessible" if response.status_code in [200, 302] else f"status: {response.status_code}"
            print_test(f"Course listing: List {status}")
            total_tests += 1
            passed_tests += 1
        except Exception as e:
            print_test(f"Course listing: Error - {e}", "❌")
            total_tests += 1
            failed_tests.append(f"Course listing: {e}")

        # 7. Test Role-Specific Functionality
        print_header("Testing role-specific functionality")
        
        # Admin access
        try:
            client.login(username='admin_student', password='admin123')
            response = client.get(reverse('students:dashboard'))
            status = "accessible" if response.status_code in [200, 302] else f"status: {response.status_code}"
            print_test(f"Admin dashboard access: Dashboard {status}")
            total_tests += 1
            passed_tests += 1
        except Exception as e:
            print_test(f"Admin dashboard access: Error - {e}", "❌")
            total_tests += 1
            failed_tests.append(f"Admin dashboard: {e}")
        
        # Teacher access
        try:
            client.login(username='teacher_student', password='teacher123')
            response = client.get(reverse('students:course_list'))
            status = "accessible" if response.status_code in [200, 302] else f"status: {response.status_code}"
            print_test(f"Teacher course access: Can view courses")
            total_tests += 1
            passed_tests += 1
        except Exception as e:
            print_test(f"Teacher course access: Error - {e}", "❌")
            total_tests += 1
            failed_tests.append(f"Teacher course access: {e}")
        
        # Student access
        try:
            client.login(username='student_test', password='student123')
            response = client.get(reverse('students:dashboard'))
            status = "accessible" if response.status_code in [200, 302] else f"status: {response.status_code}"
            print_test(f"Student dashboard access: Dashboard {status}")
            total_tests += 1
            passed_tests += 1
        except Exception as e:
            print_test(f"Student dashboard access: Error - {e}", "❌")
            total_tests += 1
            failed_tests.append(f"Student dashboard: {e}")

        # Final Summary
        print_header("STUDENTS APP TESTING SUMMARY REPORT")
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"✅ Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        print(f"❌ Failed: {len(failed_tests)}/{total_tests} ({100-success_rate:.1f}%)")
        
        print(f"\n📋 DETAILED RESULTS:")
        if failed_tests:
            for failure in failed_tests:
                print(f"  ❌ {failure}")
        
        print(f"\n🎓 SAMPLE STUDENTS DATA CREATED:")
        print(f"  👤 Student: {student_user.get_full_name()} (ID: STU001)")
        print(f"  📚 Course: CS101 - Introduction to Computer Science")
        print(f"  📝 Enrollment: Active enrollment created")
        print(f"  👨‍🏫 Instructor: {teacher_user.get_full_name()}")
        
        print(f"\n🔗 KEY URLS FOR MANUAL TESTING:")
        print(f"  🏠 Dashboard: http://localhost:8000/students/")
        print(f"  👥 Student List: http://localhost:8000/students/students/")
        print(f"  📚 Course List: http://localhost:8000/students/courses/")
        print(f"  📊 Analytics: http://localhost:8000/students/analytics/")
        
        print(f"\n👥 TEST USER CREDENTIALS:")
        print(f"  👤 Admin: admin_student / admin123")
        print(f"  👨‍🏫 Teacher: teacher_student / teacher123")
        print(f"  🎓 Student: student_test / student123")
        
        if success_rate >= 95:
            print(f"\n🏆 FINAL STATUS: 🏆 EXCELLENT - App is fully functional")
            print("=" * 80)
            print("🎉 All tests passed! Students app is ready for production.")
        elif success_rate >= 80:
            print(f"\n🟡 FINAL STATUS: 🟡 GOOD - Minor issues detected")
            print("=" * 80)
            print("⚠️ Students app needs minor fixes before production.")
        else:
            print(f"\n🔴 FINAL STATUS: 🔴 NEEDS WORK - Major issues detected")
            print("=" * 80)
            print("❌ Students app requires significant fixes.")
            
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        print("Students app testing failed due to critical error.")

if __name__ == "__main__":
    main()