#!/usr/bin/env python3
"""
Django Native Test Runner - Uses Django's built-in test runner
This should work reliably without pytest configuration issues
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

def run_app_tests(app_name):
    """Run tests for a specific app using Django's test runner"""
    print(f"\n🔍 Testing {app_name} with Django test runner...")
    print("=" * 60)
    
    # Setup Django
    setup_django()
    
    # Get Django test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=False, keepdb=True)
    
    # Define test labels
    test_labels = [f'{app_name}.tests.test_api']
    
    try:
        # Run the tests
        failures = test_runner.run_tests(test_labels)
        
        if failures == 0:
            print(f"✅ {app_name}: ALL TESTS PASSED")
            return True
        else:
            print(f"⚠️  {app_name}: {failures} TEST(S) FAILED")
            return False
            
    except Exception as e:
        print(f"❌ {app_name}: ERROR - {e}")
        return False

def run_single_app():
    """Run tests for a single app"""
    apps = ["accounts", "araz", "doctordirectory", "mahalshifa", 
            "students", "moze", "evaluation", "surveys", "photos"]
    
    print("\n🎯 Single App Testing (Django Runner)")
    print("Available apps:")
    for i, app in enumerate(apps, 1):
        print(f"  {i}. {app}")
    
    try:
        choice = input(f"\nEnter app number (1-{len(apps)}): ").strip()
        app_index = int(choice) - 1
        
        if 0 <= app_index < len(apps):
            app_name = apps[app_index]
            success = run_app_tests(app_name)
            
            if success:
                print(f"\n🎉 {app_name} tests completed successfully!")
            else:
                print(f"\n⚠️  {app_name} tests had some failures.")
        else:
            print("❌ Invalid app number")
            
    except ValueError:
        print("❌ Invalid input")
    except KeyboardInterrupt:
        print("\n👋 Testing interrupted by user")

def run_all_apps():
    """Run tests for all apps"""
    apps = ["accounts", "araz", "doctordirectory", "mahalshifa", 
            "students", "moze", "evaluation", "surveys", "photos"]
    
    print("\n🚀 Running Django tests for ALL apps...")
    
    results = {}
    passed = 0
    
    for app in apps:
        success = run_app_tests(app)
        results[app] = success
        if success:
            passed += 1
        print("\n" + "="*80 + "\n")
    
    print(f"\n📊 FINAL SUMMARY: {passed}/{len(apps)} apps passed")
    print("\n📋 Detailed Results:")
    for app, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {app}")
    
    return passed, len(apps)

def main():
    """Main function"""
    print("🏛️  Django Native Test Runner")
    print("=" * 50)
    print("Using Django's built-in test runner (more reliable than pytest)")
    
    print("\nOptions:")
    print("1. Test single app")
    print("2. Test all apps")
    print("3. Quick endpoint test")
    print("4. Exit")
    
    try:
        choice = input("\nChoose option (1-4): ").strip()
        
        if choice == "1":
            run_single_app()
        elif choice == "2":
            run_all_apps()
        elif choice == "3":
            print("\n🚀 Running quick endpoint test...")
            try:
                import subprocess
                result = subprocess.run([sys.executable, "test_all_apis.py"], 
                                      capture_output=True, text=True)
                print(result.stdout)
                if result.stderr:
                    print("Errors:", result.stderr)
            except Exception as e:
                print(f"❌ Error running endpoint test: {e}")
        elif choice == "4":
            print("👋 Goodbye!")
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n👋 Testing interrupted by user")

if __name__ == "__main__":
    main()