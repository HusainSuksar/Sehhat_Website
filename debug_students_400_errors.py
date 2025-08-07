#!/usr/bin/env python3
"""
Debug Students 400 Errors
Capture actual error messages from failing tests
"""
import os
import sys

# 🔧 Setup Django BEFORE any Django-related imports
def setup_django():
    """Setup Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
    import django
    django.setup()

setup_django()
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from datetime import date, timedelta


def debug_announcement_test():
    """Debug the announcement creation test to see actual error"""
    setup_django()
    
    # Import models after Django setup
    from students.models import Course, Student, Moze
    from moze.models import Moze
    User = get_user_model()
    
    print("🔍 DEBUGGING ANNOUNCEMENT TEST")
    print("=" * 60)
    
    # Create test users
    admin_user = User.objects.create_user(
        username='admin_user',
        email='admin@test.com',
        password='testpass123',
        role='badri_mahal_admin',
        first_name='Admin',
        last_name='User'
    )
    
    instructor_user = User.objects.create_user(
        username='instructor_user',
        email='instructor@test.com',
        password='testpass123',
        role='doctor',
        first_name='Dr. Jane',
        last_name='Smith'
    )
    
    # Create Moze for foreign key relationships
    moze = Moze.objects.create(
        name='Test Moze',
        location='Test Location',
        aamil=admin_user,
        address='123 Test Street'
    )
    
    # Create Course
    course = Course.objects.create(
        code='CS101',
        name='Introduction to Computer Science',
        description='Basic computer science concepts',
        credits=3,
        level='beginner',
        instructor=instructor_user,
        is_active=True,
        max_students=30
    )
    
    # Test the API call
    client = APIClient()
    client.force_authenticate(user=instructor_user)
    url = reverse('announcement_list_create')
    
    data = {
        'title': 'New Assignment Posted',
        'content': 'Please check the new assignment in CS101',
        'course_id': course.id,
        'is_published': True,
        'is_urgent': False
    }
    
    print(f"📋 Test Data: {data}")
    print(f"🔗 URL: {url}")
    print(f"👤 User: {instructor_user.username} (role: {instructor_user.role})")
    print(f"📚 Course: {course.code} (ID: {course.id})")
    
    response = client.post(url, data, format='json')
    
    print(f"📊 Response Status: {response.status_code}")
    print(f"📝 Response Data: {response.data}")
    
    if response.status_code == 400:
        print("\n❌ VALIDATION ERRORS:")
        for field, errors in response.data.items():
            print(f"   {field}: {errors}")
    
    return response.status_code == 201

def debug_enrollment_test():
    """Debug the enrollment creation test"""
    setup_django()
    
    from students.models import Course, Student, Enrollment
    from moze.models import Moze
    User = get_user_model()
    
    print("\n🔍 DEBUGGING ENROLLMENT TEST")
    print("=" * 60)
    
    # Create test data
    admin_user = User.objects.create_user(
        username='admin_user2',
        email='admin2@test.com',
        password='testpass123',
        role='badri_mahal_admin'
    )
    
    instructor_user = User.objects.create_user(
        username='instructor_user2',
        email='instructor2@test.com',
        password='testpass123',
        role='doctor'
    )
    
    student_user = User.objects.create_user(
        username='student_user2',
        email='student2@test.com',
        password='testpass123',
        role='student'
    )
    
    moze = Moze.objects.create(
        name='Test Moze 2',
        location='Test Location 2',
        aamil=admin_user,
        address='456 Test Avenue'
    )
    
    # Create Student record
    student = Student.objects.create(
        user=student_user,
        student_id='STU001',
        academic_level='undergraduate',
        enrollment_status='active',
        enrollment_date=date.today() - timedelta(days=365),
        expected_graduation=date.today() + timedelta(days=730)
    )
    
    # Create Course
    course = Course.objects.create(
        code='CS201',
        name='Data Structures',
        credits=3,
        level='intermediate',
        instructor=instructor_user,
        is_active=True,
        max_students=20
    )
    
    # Test the API call
    client = APIClient()
    client.force_authenticate(user=student_user)
    url = reverse('enrollment_list_create')
    
    data = {
        'course_id': course.id,
        'status': 'enrolled'
    }
    
    print(f"📋 Test Data: {data}")
    print(f"🔗 URL: {url}")
    print(f"👤 User: {student_user.username} (role: {student_user.role})")
    print(f"🎓 Student: {student.student_id}")
    print(f"📚 Course: {course.code} (ID: {course.id})")
    
    response = client.post(url, data, format='json')
    
    print(f"📊 Response Status: {response.status_code}")
    print(f"📝 Response Data: {response.data}")
    
    if response.status_code == 400:
        print("\n❌ VALIDATION ERRORS:")
        for field, errors in response.data.items():
            print(f"   {field}: {errors}")
    
    return response.status_code == 201

def main():
    """Main debugging function"""
    print("🚨 STUDENTS APP 400 ERROR DEBUGGER")
    print("=" * 70)
    print("This will show the ACTUAL error messages causing 400 responses")
    print("=" * 70)
    
    try:
        # Clean up any existing test data
        setup_django()
        User = get_user_model()
        User.objects.filter(username__startswith='admin_user').delete()
        User.objects.filter(username__startswith='instructor_user').delete()
        User.objects.filter(username__startswith='student_user').delete()
        
        # Debug individual tests
        print("\n1. ANNOUNCEMENT TEST DEBUG:")
        announcement_success = debug_announcement_test()
        
        print("\n2. ENROLLMENT TEST DEBUG:")
        enrollment_success = debug_enrollment_test()
        
        print(f"\n📊 SUMMARY:")
        print(f"✅ Announcement: {'PASSED' if announcement_success else 'FAILED'}")
        print(f"✅ Enrollment: {'PASSED' if enrollment_success else 'FAILED'}")
        
        if not announcement_success and not enrollment_success:
            print("\n💡 LIKELY ISSUES:")
            print("- Missing required fields not obvious from serializer")
            print("- Model validation constraints")
            print("- Permission issues")
            print("- Foreign key constraint violations")
            print("- URL routing problems")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()