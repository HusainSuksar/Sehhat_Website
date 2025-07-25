#!/usr/bin/env python3

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

def test_students_app():
    print("🎓 Testing Students App - Quick Check")
    print("=" * 50)
    
    try:
        # Test 1: Import models
        print("📚 Testing model imports...")
        from students.models import Student, Course, Enrollment
        print("✅ Models imported successfully")
        
        # Test 2: Check model counts
        student_count = Student.objects.count()
        course_count = Course.objects.count()
        enrollment_count = Enrollment.objects.count()
        
        print(f"✅ Students: {student_count} records")
        print(f"✅ Courses: {course_count} records")
        print(f"✅ Enrollments: {enrollment_count} records")
        
        # Test 3: Test URLs
        print("\n🔗 Testing URL imports...")
        from students import urls
        print("✅ URLs imported successfully")
        
        # Test 4: Test views
        print("\n👁️ Testing view imports...")
        from students import views
        print("✅ Views imported successfully")
        
        # Test 5: Test forms
        print("\n📝 Testing form imports...")
        from students import forms
        print("✅ Forms imported successfully")
        
        print("\n🎉 Students app basic structure is working!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_students_app()