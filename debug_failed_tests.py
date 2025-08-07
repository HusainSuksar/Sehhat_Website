#!/usr/bin/env python3
"""
Debug Failed Tests - Help identify specific issues in failing apps
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

def debug_single_app(app_name):
    """Debug a single app with detailed output"""
    print(f"\n🔍 DEBUGGING {app_name.upper()} APP")
    print("=" * 60)
    
    # Setup Django
    setup_django()
    
    # Get Django test runner with maximum verbosity
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=3, interactive=False, keepdb=True, debug_mode=True, failfast=True)
    
    # Define test labels
    test_labels = [f'{app_name}.tests.test_api']
    
    try:
        print(f"📋 Running tests for: {test_labels}")
        
        # Run the tests with maximum detail
        failures = test_runner.run_tests(test_labels)
        
        print(f"\n📊 RESULTS FOR {app_name}:")
        if failures == 0:
            print(f"✅ ALL TESTS PASSED")
            return True
        else:
            print(f"❌ {failures} TEST(S) FAILED")
            print(f"\n💡 Common issues for {app_name}:")
            print_common_issues(app_name)
            return False
            
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        print(f"\n🔧 Troubleshooting for {app_name}:")
        print_troubleshooting(app_name)
        return False

def print_common_issues(app_name):
    """Print common issues for each app"""
    issues = {
        'accounts': [
            "- User model field mismatches",
            "- ITS service mocking issues", 
            "- JWT token configuration",
            "- Password validation errors",
            "- Permission system conflicts"
        ],
        'students': [
            "- Moze relationship setup issues",
            "- Course enrollment data problems",
            "- GPA calculation errors",
            "- Student status validation",
            "- Performance record creation"
        ],
        'moze': [
            "- Coordinator user assignment",
            "- Team member relationships",
            "- Moze settings configuration",
            "- Comment system permissions",
            "- Moze status validation"
        ],
        'surveys': [
            "- Survey question JSON validation",
            "- Response data structure issues",
            "- Date range validation",
            "- Analytics calculation errors",
            "- Reminder system problems"
        ],
        'photos': [
            "- Image file upload simulation",
            "- Photo album unique constraints",
            "- Like system duplicate issues",
            "- Permission checking problems",
            "- File cleanup in tests"
        ]
    }
    
    if app_name in issues:
        for issue in issues[app_name]:
            print(issue)

def print_troubleshooting(app_name):
    """Print troubleshooting steps"""
    print(f"1. Check test data setup in {app_name}/tests/test_api.py")
    print(f"2. Verify model relationships in {app_name}/models.py")
    print(f"3. Check serializer validation in {app_name}/serializers.py")
    print(f"4. Review permission classes in {app_name}/api_views.py")
    print(f"5. Look for unique constraint conflicts")

def main():
    """Main debugging function"""
    print("🐛 Failed Tests Debugger")
    print("=" * 50)
    
    failed_apps = ["accounts", "students", "moze", "surveys", "photos"]
    
    print("Failed apps to debug:")
    for i, app in enumerate(failed_apps, 1):
        print(f"  {i}. {app}")
    print(f"  {len(failed_apps) + 1}. Debug all failed apps")
    
    try:
        choice = input(f"\nChoose app to debug (1-{len(failed_apps) + 1}): ").strip()
        
        if choice == str(len(failed_apps) + 1):
            print("\n🚀 Debugging ALL failed apps...")
            for app in failed_apps:
                debug_single_app(app)
                print("\n" + "="*80 + "\n")
        else:
            app_index = int(choice) - 1
            if 0 <= app_index < len(failed_apps):
                app_name = failed_apps[app_index]
                debug_single_app(app_name)
            else:
                print("❌ Invalid choice")
                
    except ValueError:
        print("❌ Invalid input")
    except KeyboardInterrupt:
        print("\n👋 Debugging interrupted")

if __name__ == "__main__":
    main()