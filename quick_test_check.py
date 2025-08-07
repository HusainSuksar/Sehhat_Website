#!/usr/bin/env python3
"""
Quick Test Check - Verify if our specific fixes worked
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

def setup_django():
    """Setup Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
    django.setup()

def test_specific_fixes():
    """Test the specific issues we fixed"""
    print("🔍 TESTING SPECIFIC FIXES")
    print("=" * 50)
    
    setup_django()
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=False, keepdb=True, failfast=True)
    
    # Test specific methods we fixed
    specific_tests = [
        ("accounts.tests.test_api.AuthenticationAPITests.test_jwt_login_with_its_id", "JWT Login with ITS ID"),
        ("students.tests.test_api.AnnouncementAPITests.test_create_announcement_instructor", "Student Announcement Creation"),
        ("moze.tests.test_api.MozeCommentAPITests.test_create_comment_aamil", "Moze Comment Creation"),
        ("surveys.tests.test_api.FilteringAndSearchTests.test_search_surveys_by_title", "Survey Search"),
        ("photos.tests.test_api.FilteringAndSearchTests.test_search_photos_by_title", "Photo Search")
    ]
    
    results = {}
    
    for test_path, description in specific_tests:
        print(f"\n🧪 Testing: {description}")
        print(f"   Path: {test_path}")
        
        try:
            failures = test_runner.run_tests([test_path])
            if failures == 0:
                print(f"   ✅ PASSED - Fix worked!")
                results[description] = True
            else:
                print(f"   ❌ FAILED - Fix didn't work or other issues")
                results[description] = False
        except Exception as e:
            print(f"   ❌ ERROR - {e}")
            results[description] = False
    
    print(f"\n📊 SPECIFIC FIX RESULTS:")
    print("=" * 50)
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for description, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {description}")
    
    print(f"\n🎯 Fix Success Rate: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All our specific fixes worked! Other tests might be failing.")
    else:
        print("⚠️  Some of our fixes didn't work. Need to investigate further.")
    
    return results

def check_remaining_failures():
    """Check what other tests might be failing"""
    print("\n🔍 CHECKING FOR OTHER FAILURES")
    print("=" * 50)
    
    failed_apps = ["accounts", "students", "moze", "surveys", "photos"]
    
    for app in failed_apps:
        print(f"\n📱 {app.upper()} App:")
        print(f"   Run this to see all failures:")
        print(f"   python test_comprehensive_debug.py")
        print(f"   Then choose option 1 and select {app}")

def main():
    """Main function"""
    print("🚀 QUICK TEST CHECK")
    print("=" * 50)
    print("Verifying if our specific fixes resolved the reported issues")
    
    results = test_specific_fixes()
    check_remaining_failures()
    
    print(f"\n💡 NEXT STEPS:")
    print("1. If specific fixes worked, there are other failing tests")
    print("2. Use: python test_comprehensive_debug.py")
    print("3. Debug each failing app individually for remaining issues")

if __name__ == "__main__":
    main()