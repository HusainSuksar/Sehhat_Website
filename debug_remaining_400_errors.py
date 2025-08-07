#!/usr/bin/env python3
"""
Debug Remaining 400 Errors in Students App
Test attendance, grade, event, submission, and student group creation
"""

import os
import sys
import django
from datetime import date, timedelta, datetime

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

def debug_attendance_test():
    """Debug attendance creation - likely missing instructor_id or student_id"""
    from students.models import Course, Student, Attendance
    from moze.models import Moze
    User = get_user_model()
    
    print("🔍 DEBUGGING ATTENDANCE TEST")
    print("=" * 60)
    
    # Get existing users
    instructor_user = User.objects.filter(username__startswith='instructor_user').first()
    student_user = User.objects.filter(username__startswith='student_user').first()
    course = Course.objects.filter(code__startswith='DEBUG_').first()
    student = Student.objects.first()
    
    if not all([instructor_user, student_user, course, student]):
        print("❌ Missing test data")
        return False
    
    # Test the API call
    client = APIClient()
    client.force_authenticate(user=instructor_user)
    url = reverse('attendance_list_create')
    
    data = {
        'course_id': course.id,
        'student_id': student.id,
        'date': date.today().isoformat(),
        'status': 'present',
        'notes': 'Test attendance'
    }
    
    print(f"📋 Test Data: {data}")
    print(f"🔗 URL: {url}")
    print(f"👤 User: {instructor_user.username} (role: {instructor_user.role})")
    
    response = client.post(url, data, format='json')
    
    print(f"📊 Response Status: {response.status_code}")
    print(f"📝 Response Data: {response.data}")
    
    if response.status_code == 400:
        print("\n❌ VALIDATION ERRORS:")
        for field, errors in response.data.items():
            print(f"   {field}: {errors}")
    
    return response.status_code == 201

def debug_grade_test():
    """Debug grade creation - likely missing instructor_id or student_id"""
    from students.models import Course, Student, Grade, Assignment
    User = get_user_model()
    
    print("\n🔍 DEBUGGING GRADE TEST")
    print("=" * 60)
    
    # Get existing data
    instructor_user = User.objects.filter(username__startswith='instructor_user').first()
    student = Student.objects.first()
    assignment = Assignment.objects.first()
    
    if not all([instructor_user, student, assignment]):
        print("❌ Missing test data")
        return False
    
    # Test the API call
    client = APIClient()
    client.force_authenticate(user=instructor_user)
    url = reverse('grade_list_create')
    
    data = {
        'student_id': student.id,
        'course_id': assignment.course.id,
        'assignment_id': assignment.id,
        'points': 85,
        'max_points': 100,
        'comments': 'Good work!'
    }
    
    print(f"📋 Test Data: {data}")
    print(f"🔗 URL: {url}")
    print(f"👤 User: {instructor_user.username} (role: {instructor_user.role})")
    
    response = client.post(url, data, format='json')
    
    print(f"📊 Response Status: {response.status_code}")
    print(f"📝 Response Data: {response.data}")
    
    if response.status_code == 400:
        print("\n❌ VALIDATION ERRORS:")
        for field, errors in response.data.items():
            print(f"   {field}: {errors}")
    
    return response.status_code == 201

def debug_event_test():
    """Debug event creation - likely missing organizer_id"""
    from students.models import Event
    User = get_user_model()
    
    print("\n🔍 DEBUGGING EVENT TEST")
    print("=" * 60)
    
    # Get existing data
    admin_user = User.objects.filter(role='badri_mahal_admin').first()
    
    if not admin_user:
        print("❌ Missing admin user")
        return False
    
    # Test the API call
    client = APIClient()
    client.force_authenticate(user=admin_user)
    url = reverse('event_list_create')
    
    data = {
        'title': 'Test Event',
        'description': 'A test event',
        'event_type': 'workshop',
        'start_date': (timezone.now() + timedelta(days=7)).isoformat(),
        'end_date': (timezone.now() + timedelta(days=7, hours=2)).isoformat(),
        'location': 'Test Room',
        'max_participants': 50
    }
    
    print(f"📋 Test Data: {data}")
    print(f"🔗 URL: {url}")
    print(f"👤 User: {admin_user.username} (role: {admin_user.role})")
    
    response = client.post(url, data, format='json')
    
    print(f"📊 Response Status: {response.status_code}")
    print(f"📝 Response Data: {response.data}")
    
    if response.status_code == 400:
        print("\n❌ VALIDATION ERRORS:")
        for field, errors in response.data.items():
            print(f"   {field}: {errors}")
    
    return response.status_code == 201

def debug_submission_test():
    """Debug submission creation - likely missing student_id"""
    from students.models import Course, Student, Assignment, Submission
    User = get_user_model()
    
    print("\n🔍 DEBUGGING SUBMISSION TEST")
    print("=" * 60)
    
    # Get existing data
    student_user = User.objects.filter(role='student').first()
    student = Student.objects.filter(user=student_user).first()
    assignment = Assignment.objects.first()
    
    if not all([student_user, student, assignment]):
        print("❌ Missing test data")
        return False
    
    # Test the API call
    client = APIClient()
    client.force_authenticate(user=student_user)
    url = reverse('submission_list_create')
    
    data = {
        'assignment_id': assignment.id,
        'content': 'Test submission content',
        'submission_type': 'text'
    }
    
    print(f"📋 Test Data: {data}")
    print(f"🔗 URL: {url}")
    print(f"👤 User: {student_user.username} (role: {student_user.role})")
    print(f"🎓 Student: {student.student_id}")
    
    response = client.post(url, data, format='json')
    
    print(f"📊 Response Status: {response.status_code}")
    print(f"📝 Response Data: {response.data}")
    
    if response.status_code == 400:
        print("\n❌ VALIDATION ERRORS:")
        for field, errors in response.data.items():
            print(f"   {field}: {errors}")
    
    return response.status_code == 201

def debug_student_group_test():
    """Debug student group creation - likely missing created_by_id"""
    from students.models import StudentGroup
    User = get_user_model()
    
    print("\n🔍 DEBUGGING STUDENT GROUP TEST")
    print("=" * 60)
    
    # Get existing data
    admin_user = User.objects.filter(role='badri_mahal_admin').first()
    
    if not admin_user:
        print("❌ Missing admin user")
        return False
    
    # Test the API call
    client = APIClient()
    client.force_authenticate(user=admin_user)
    url = reverse('student_group_list_create')
    
    data = {
        'name': 'Test Study Group',
        'description': 'A test study group',
        'group_type': 'study_group',  # Fixed: use valid choice
        'max_members': 10
    }
    
    print(f"📋 Test Data: {data}")
    print(f"🔗 URL: {url}")
    print(f"👤 User: {admin_user.username} (role: {admin_user.role})")
    
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
    print("🚨 REMAINING 400 ERRORS DEBUGGER")
    print("=" * 70)
    print("Testing attendance, grade, event, submission, and student group creation")
    print("=" * 70)
    
    try:
        # Debug individual failing endpoints
        print("\n1. ATTENDANCE TEST:")
        attendance_success = debug_attendance_test()
        
        print("\n2. GRADE TEST:")
        grade_success = debug_grade_test()
        
        print("\n3. EVENT TEST:")
        event_success = debug_event_test()
        
        print("\n4. SUBMISSION TEST:")
        submission_success = debug_submission_test()
        
        print("\n5. STUDENT GROUP TEST:")
        group_success = debug_student_group_test()
        
        print(f"\n📊 SUMMARY:")
        results = {
            'Attendance': attendance_success,
            'Grade': grade_success,
            'Event': event_success,
            'Submission': submission_success,
            'Student Group': group_success
        }
        
        for test, success in results.items():
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"{status} {test}")
        
        total_passed = sum(results.values())
        total_tests = len(results)
        print(f"\n🎯 Overall: {total_passed}/{total_tests} tests passing ({total_passed/total_tests*100:.1f}%)")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()