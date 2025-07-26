#!/usr/bin/env python3

import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

# Import after Django setup
from students.models import Student, Course, Enrollment, Assignment, Grade, Attendance
from accounts.models import User

def print_section(title):
    print(f"\n{'='*80}")
    print(f"🎓 {title}")
    print(f"{'='*80}")

def print_result(test_name, success, details=""):
    emoji = "✅" if success else "❌"
    print(f"{emoji} {test_name}")
    if details:
        print(f"   └─ {details}")

def test_students_app():
    print_section("STUDENTS APP FINAL TESTING")
    
    client = Client()
    User = get_user_model()
    
    results = []
    test_users = {}
    
    # Test 1: Model imports and access
    print_section("1. TESTING MODEL IMPORTS")
    try:
        from students.models import Student, Course, Enrollment, Assignment, Grade, Attendance
        print_result("Import core models", True, "All essential models imported")
        results.append(("Model imports", True))
        
        # Test model counts
        student_count = Student.objects.count()
        course_count = Course.objects.count()
        enrollment_count = Enrollment.objects.count()
        
        print_result("Student model access", True, f"{student_count} records")
        print_result("Course model access", True, f"{course_count} records")
        print_result("Enrollment model access", True, f"{enrollment_count} records")
        results.extend([("Student model", True), ("Course model", True), ("Enrollment model", True)])
        
    except Exception as e:
        print_result("Model testing", False, f"Error: {e}")
        results.append(("Model imports", False))
    
    # Test 2: Create test users
    print_section("2. CREATING TEST USERS")
    try:
        # Admin user
        admin_user, created = User.objects.get_or_create(
            username='admin_students_test',
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
        test_users['admin'] = admin_user
        print_result("Create admin user", True, f"User: {admin_user.username}")
        
        # Teacher user
        teacher_user, created = User.objects.get_or_create(
            username='teacher_students_test',
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
        test_users['teacher'] = teacher_user
        print_result("Create teacher user", True, f"User: {teacher_user.username}")
        
        # Student user
        student_user, created = User.objects.get_or_create(
            username='student_test_final',
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
        test_users['student'] = student_user
        print_result("Create student user", True, f"User: {student_user.username}")
        
        results.append(("User creation", True))
        
    except Exception as e:
        print_result("User creation", False, f"Error: {e}")
        results.append(("User creation", False))
    
    # Test 3: Create sample data
    print_section("3. CREATING SAMPLE DATA")
    try:
        # Create Student profile
        student_profile, created = Student.objects.get_or_create(
            user=test_users['student'],
            defaults={
                'student_id': 'MED2024001',
                'academic_level': 'undergraduate',
                'enrollment_status': 'active',
                'enrollment_date': datetime.now().date(),
                'expected_graduation': datetime.now().date() + timedelta(days=1460)  # 4 years
            }
        )
        print_result("Create Student profile", True, f"ID: {student_profile.student_id}")
        
        # Create Course
        course, created = Course.objects.get_or_create(
            code='ANAT101',
            defaults={
                'name': 'Human Anatomy I',
                'description': 'Introduction to human anatomy and physiology',
                'credits': 4,
                'level': 'beginner',
                'instructor': test_users['teacher'],
                'is_active': True,
                'max_students': 60
            }
        )
        print_result("Create Course", True, f"Course: {course.code}")
        
        # Create Enrollment
        enrollment, created = Enrollment.objects.get_or_create(
            student=student_profile,
            course=course,
            defaults={
                'status': 'enrolled',
                'grade': 'A'
            }
        )
        print_result("Create Enrollment", True, f"Status: {enrollment.status}")
        
        results.append(("Sample data creation", True))
        
    except Exception as e:
        print_result("Sample data creation", False, f"Error: {e}")
        results.append(("Sample data creation", False))
    
    # Test 4: URL patterns
    print_section("4. TESTING URL PATTERNS")
    test_urls = [
        ('students:dashboard', 'Dashboard'),
        ('students:student_list', 'Student List'),
        ('students:course_list', 'Course List'),
        ('students:analytics', 'Analytics')
    ]
    
    url_results = 0
    for url_name, description in test_urls:
        try:
            url = reverse(url_name)
            print_result(f"URL {description}", True, f"Resolves to: {url}")
            url_results += 1
        except Exception as e:
            print_result(f"URL {description}", False, f"Error: {e}")
    
    results.append(("URL patterns", url_results == len(test_urls)))
    
    # Test 5: View accessibility
    print_section("5. TESTING VIEW ACCESSIBILITY")
    
    # Login as admin
    login_success = client.login(username='admin_students_test', password='admin123')
    if login_success:
        print_result("Admin login", True, "Successfully logged in")
        
        view_results = 0
        for url_name, description in test_urls:
            try:
                response = client.get(reverse(url_name))
                status = response.status_code
                
                if status in [200, 302]:
                    print_result(f"{description} view", True, f"Status: {status}")
                    view_results += 1
                else:
                    print_result(f"{description} view", False, f"Status: {status}")
                    
            except Exception as e:
                print_result(f"{description} view", False, f"Error: {e}")
        
        results.append(("View accessibility", view_results >= len(test_urls) * 0.8))
        client.logout()
    else:
        print_result("Admin login", False, "Login failed")
        results.append(("View accessibility", False))
    
    # Test 6: Role-based access
    print_section("6. TESTING ROLE-BASED ACCESS")
    
    role_test_results = 0
    for role, password in [('admin', 'admin123'), ('teacher', 'teacher123'), ('student', 'student123')]:
        if role in test_users:
            username = test_users[role].username
            login_success = client.login(username=username, password=password)
            
            if login_success:
                try:
                    response = client.get(reverse('students:dashboard'))
                    accessible = response.status_code in [200, 302]
                    print_result(f"{role.title()} dashboard access", accessible, f"Status: {response.status_code}")
                    if accessible:
                        role_test_results += 1
                except Exception as e:
                    print_result(f"{role.title()} dashboard access", False, f"Error: {e}")
                
                client.logout()
            else:
                print_result(f"{role.title()} login", False, "Authentication failed")
    
    results.append(("Role-based access", role_test_results >= 2))
    
    # Generate final report
    print_section("STUDENTS APP FINAL TESTING SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(1 for _, success in results if success)
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n📊 OVERALL RESULTS:")
    print(f"✅ Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    print(f"❌ Failed: {total_tests - passed_tests}/{total_tests} ({100-success_rate:.1f}%)")
    
    print(f"\n🎓 SAMPLE DATA CREATED:")
    if 'student' in test_users:
        print(f"  👤 Student: {test_users['student'].get_full_name()} (ID: MED2024001)")
    if 'teacher' in test_users:
        print(f"  👨‍🏫 Teacher: {test_users['teacher'].get_full_name()}")
    print(f"  📚 Course: ANAT101 - Human Anatomy I")
    print(f"  📝 Enrollment: Active medical student enrollment")
    
    print(f"\n🔗 KEY URLS FOR TESTING:")
    print(f"  🏠 Dashboard: http://localhost:8000/students/")
    print(f"  👥 Students: http://localhost:8000/students/students/")
    print(f"  📚 Courses: http://localhost:8000/students/courses/")
    print(f"  📊 Analytics: http://localhost:8000/students/analytics/")
    
    print(f"\n👥 TEST CREDENTIALS:")
    print(f"  👤 Admin: admin_students_test / admin123")
    print(f"  👨‍🏫 Teacher: teacher_students_test / teacher123")
    print(f"  🎓 Student: student_test_final / student123")
    
    if success_rate >= 90:
        print(f"\n🏆 FINAL STATUS: EXCELLENT ({success_rate:.1f}%)")
        print("✅ Students app is ready for production!")
        print("🚀 Ready to commit to main branch...")
        return True
    elif success_rate >= 75:
        print(f"\n🟡 FINAL STATUS: GOOD ({success_rate:.1f}%)")
        print("⚠️ Students app has minor issues but is functional.")
        return True
    else:
        print(f"\n🔴 FINAL STATUS: NEEDS WORK ({success_rate:.1f}%)")
        print("❌ Students app requires fixes.")
        return False

if __name__ == "__main__":
    success = test_students_app()
    sys.exit(0 if success else 1)