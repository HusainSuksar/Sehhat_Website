#!/usr/bin/env python3
"""
Debug 404 Permission Test - Exact Replication
Recreate the exact test scenario to see why 404 persists
"""

import os
import sys
import django
from datetime import date, timedelta, time

# Setup Django FIRST before any other imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

# Now import Django/DRF components after setup
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.utils import timezone

def debug_permission_test():
    """Replicate the exact test scenario"""
    from students.models import Course, Student, Assignment, Submission, Enrollment
    from moze.models import Moze
    User = get_user_model()
    
    print("🔍 DEBUGGING 404 PERMISSION TEST")
    print("=" * 60)
    
    # Clean up any existing test data first
    print("🧹 Cleaning up existing test data...")
    Course.objects.filter(code='CS101').delete()
    User.objects.filter(username__in=['admin_user', 'instructor_user', 'student_user']).delete()
    Student.objects.filter(student_id='STU001').delete()
    Moze.objects.filter(name='Test Moze').delete()
    
    # Create test users (EXACT SAME as test setUp)
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
    
    student_user = User.objects.create_user(
        username='student_user',
        email='student@test.com',
        password='testpass123',
        role='student',
        first_name='John',
        last_name='Doe'
    )
    
    # Create Moze for foreign key relationships
    moze = Moze.objects.create(
        name='Test Moze',
        location='Test Location',
        aamil=admin_user,
        address='123 Test Street'
    )
    
    # Create Student
    student = Student.objects.create(
        user=student_user,
        student_id='STU001',
        academic_level='undergraduate',
        enrollment_status='active',
        enrollment_date=date.today() - timedelta(days=365)
    )
    
    # Create Course (EXACT SAME as test setUp)
    course = Course.objects.create(
        code='CS101',
        name='Introduction to Computer Science',
        description='Basic computer science concepts',
        credits=3,
        level='beginner',
        instructor=instructor_user,  # THIS IS THE KEY!
        is_active=True,
        max_students=30
    )
    
    # Create Assignment
    assignment = Assignment.objects.create(
        course=course,
        title='First Assignment',
        description='Complete the first programming task',
        assignment_type='homework',
        due_date=timezone.now() + timedelta(days=7),
        max_points=100,
        is_published=True
    )
    
    print(f"👤 Created instructor: {instructor_user.username} (role: {instructor_user.role})")
    print(f"📚 Created course: {course.code} (instructor: {course.instructor.username if course.instructor else 'None'})")
    print(f"📋 Created assignment: {assignment.title}")
    print(f"🎓 Created student: {student.student_id}")
    
    # Create submission (EXACT SAME as test)
    submission = Submission.objects.create(
        assignment=assignment,
        student=student,
        content='Test submission',
        attempt_number=1
    )
    
    print(f"📄 Created submission ID: {submission.id}")
    
    # Test the queryset logic manually
    print("\n🔍 TESTING QUERYSET LOGIC:")
    
    # Import the view to test queryset
    from students.api_views import SubmissionDetailAPIView
    
    # Create a mock request object
    class MockRequest:
        def __init__(self, user):
            self.user = user
    
    # Test the instructor's queryset
    view = SubmissionDetailAPIView()
    view.request = MockRequest(instructor_user)
    instructor_queryset = view.get_queryset()
    
    print(f"🔍 Instructor queryset count: {instructor_queryset.count()}")
    print(f"🔍 All submissions count: {Submission.objects.count()}")
    
    # Check if the submission is in the instructor's queryset
    submission_in_queryset = instructor_queryset.filter(id=submission.id).exists()
    print(f"🔍 Submission in instructor queryset: {submission_in_queryset}")
    
    if not submission_in_queryset:
        print("\n❌ PROBLEM FOUND: Submission NOT in instructor queryset")
        
        # Debug the course filtering
        instructor_courses = Course.objects.filter(instructor=instructor_user)
        print(f"🔍 Instructor courses count: {instructor_courses.count()}")
        
        for course in instructor_courses:
            print(f"  - Course: {course.code} (instructor: {course.instructor.username if course.instructor else 'None'})")
        
        # Check assignment course relationship
        print(f"🔍 Assignment course: {assignment.course.code}")
        print(f"🔍 Assignment course instructor: {assignment.course.instructor.username if assignment.course.instructor else 'None'}")
        
        # Check submission assignment relationship
        print(f"🔍 Submission assignment: {submission.assignment.title}")
        print(f"🔍 Submission assignment course: {submission.assignment.course.code}")
        
        # Test the exact queryset filter
        submissions_for_instructor = Submission.objects.filter(assignment__course__in=instructor_courses)
        print(f"🔍 Submissions for instructor courses: {submissions_for_instructor.count()}")
    
    # Test the API call (EXACT SAME as test)
    client = APIClient()
    client.force_authenticate(user=instructor_user)
    url = reverse('submission_detail', kwargs={'pk': submission.id})
    
    print(f"\n🌐 TESTING API CALL:")
    print(f"🔗 URL: {url}")
    print(f"👤 Authenticated as: {instructor_user.username}")
    
    response = client.get(url)
    
    print(f"📊 Response status: {response.status_code}")
    
    if response.status_code == 404:
        print("❌ 404 CONFIRMED - Object not found in queryset")
        print("💡 This means the queryset filtering is excluding the submission")
    elif response.status_code == 200:
        print("✅ 200 OK - Working correctly!")
    else:
        print(f"❓ Unexpected status: {response.status_code}")
        print(f"📝 Response data: {response.data}")
    
    return response.status_code == 200

def main():
    """Main debugging function"""
    print("🚨 404 PERMISSION TEST DEBUGGER")
    print("=" * 70)
    print("Exact replication of the failing test scenario")
    print("=" * 70)
    
    try:
        success = debug_permission_test()
        
        if success:
            print("\n🎯 SUCCESS: Issue resolved!")
        else:
            print("\n❌ ISSUE PERSISTS: Need deeper investigation")
            print("\nPossible causes:")
            print("1. Queryset filtering logic is incorrect")
            print("2. Course-instructor relationship not established properly")
            print("3. Assignment-course relationship broken")
            print("4. Permission class logic overriding queryset")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()