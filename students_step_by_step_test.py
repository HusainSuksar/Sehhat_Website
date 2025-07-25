#!/usr/bin/env python3

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

def test_step_1_imports():
    """Test 1: Check if all core modules can be imported"""
    print("🎓 STEP 1: Testing Students App Imports")
    print("-" * 50)
    
    results = []
    
    # Test models import
    try:
        from students import models
        print("✅ Students models imported successfully")
        results.append(("Models import", True, None))
    except Exception as e:
        print(f"❌ Students models import failed: {e}")
        results.append(("Models import", False, str(e)))
    
    # Test views import
    try:
        from students import views
        print("✅ Students views imported successfully")
        results.append(("Views import", True, None))
    except Exception as e:
        print(f"❌ Students views import failed: {e}")
        results.append(("Views import", False, str(e)))
    
    # Test URLs import
    try:
        from students import urls
        print("✅ Students URLs imported successfully")
        results.append(("URLs import", True, None))
    except Exception as e:
        print(f"❌ Students URLs import failed: {e}")
        results.append(("URLs import", False, str(e)))
    
    # Test forms import
    try:
        from students import forms
        print("✅ Students forms imported successfully")
        results.append(("Forms import", True, None))
    except Exception as e:
        print(f"❌ Students forms import failed: {e}")
        results.append(("Forms import", False, str(e)))
    
    return results

def test_step_2_models():
    """Test 2: Check model accessibility and basic operations"""
    print("\n🎓 STEP 2: Testing Students Models")
    print("-" * 50)
    
    results = []
    
    try:
        from students.models import Student
        count = Student.objects.count()
        print(f"✅ Student model: {count} records")
        results.append(("Student model", True, f"{count} records"))
    except Exception as e:
        print(f"❌ Student model error: {e}")
        results.append(("Student model", False, str(e)))
    
    try:
        from students.models import Course
        count = Course.objects.count()
        print(f"✅ Course model: {count} records")
        results.append(("Course model", True, f"{count} records"))
    except Exception as e:
        print(f"❌ Course model error: {e}")
        results.append(("Course model", False, str(e)))
    
    try:
        from students.models import Enrollment
        count = Enrollment.objects.count()
        print(f"✅ Enrollment model: {count} records")
        results.append(("Enrollment model", True, f"{count} records"))
    except Exception as e:
        print(f"❌ Enrollment model error: {e}")
        results.append(("Enrollment model", False, str(e)))
    
    return results

def test_step_3_urls():
    """Test 3: Check URL patterns"""
    print("\n🎓 STEP 3: Testing Students URLs")
    print("-" * 50)
    
    results = []
    
    try:
        from django.urls import reverse
        
        # Test main URLs
        test_urls = [
            'students:dashboard',
            'students:student_list', 
            'students:course_list',
            'students:analytics'
        ]
        
        for url_name in test_urls:
            try:
                url = reverse(url_name)
                print(f"✅ URL {url_name}: {url}")
                results.append((f"URL {url_name}", True, url))
            except Exception as e:
                print(f"❌ URL {url_name} error: {e}")
                results.append((f"URL {url_name}", False, str(e)))
                
    except Exception as e:
        print(f"❌ URL testing failed: {e}")
        results.append(("URL testing", False, str(e)))
    
    return results

def main():
    print("🎓 STUDENTS APP STEP-BY-STEP TESTING")
    print("=" * 60)
    
    all_results = []
    
    # Run tests step by step
    all_results.extend(test_step_1_imports())
    all_results.extend(test_step_2_models())
    all_results.extend(test_step_3_urls())
    
    # Summary
    print("\n🎓 TESTING SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success, _ in all_results if success)
    total = len(all_results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if total - passed > 0:
        print("\n❌ FAILED TESTS:")
        for test_name, success, details in all_results:
            if not success:
                print(f"  - {test_name}: {details}")
    
    success_rate = (passed / total * 100) if total > 0 else 0
    print(f"\n📊 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("🏆 Students app is in excellent condition!")
    elif success_rate >= 70:
        print("🟡 Students app needs minor fixes")
    else:
        print("🔴 Students app needs significant work")

if __name__ == "__main__":
    main()