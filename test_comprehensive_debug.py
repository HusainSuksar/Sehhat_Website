#!/usr/bin/env python3
"""
Comprehensive Test Debugger - Shows all individual test failures in detail
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

def run_comprehensive_debug(app_name):
    """Run tests with comprehensive debugging for a specific app"""
    print(f"\n🔍 COMPREHENSIVE DEBUG: {app_name.upper()}")
    print("=" * 70)
    
    # Setup Django
    setup_django()
    
    # Get Django test runner with maximum verbosity and fail-fast disabled
    TestRunner = get_runner(settings)
    test_runner = TestRunner(
        verbosity=3, 
        interactive=False, 
        keepdb=True, 
        debug_mode=True, 
        failfast=False  # Don't stop on first failure
    )
    
    # Define test labels
    test_labels = [f'{app_name}.tests.test_api']
    
    try:
        print(f"📋 Running ALL tests for: {test_labels}")
        print("🔧 Settings: verbosity=3, failfast=False (show all failures)")
        print("-" * 70)
        
        # Run the tests with full detail
        failures = test_runner.run_tests(test_labels)
        
        print("-" * 70)
        print(f"\n📊 COMPREHENSIVE RESULTS FOR {app_name.upper()}:")
        if failures == 0:
            print(f"✅ ALL TESTS PASSED - READY FOR PRODUCTION")
            return True
        else:
            print(f"❌ {failures} TEST(S) FAILED")
            return False
            
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        return False

def run_all_apps_comprehensive():
    """Run comprehensive debugging for all failed apps"""
    failed_apps = ["accounts", "students", "moze", "surveys", "photos"]
    
    print("🐛 COMPREHENSIVE DEBUGGING FOR ALL FAILED APPS")
    print("=" * 80)
    print("This will show EVERY individual test failure with full details")
    print("=" * 80)
    
    results = {}
    
    for i, app in enumerate(failed_apps, 1):
        print(f"\n🔄 DEBUGGING APP {i}/{len(failed_apps)}: {app}")
        success = run_comprehensive_debug(app)
        results[app] = success
        
        if i < len(failed_apps):
            print("\n" + "🔄" * 80)
            input("Press Enter to continue to next app (or Ctrl+C to stop)...")
    
    print(f"\n🎯 FINAL COMPREHENSIVE SUMMARY")
    print("=" * 50)
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    print(f"📊 Success Rate: {passed}/{total} apps ({passed/total*100:.1f}%)")
    
    for app, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {app}")
    
    return results

def debug_single_app_menu():
    """Interactive menu for debugging a single app"""
    failed_apps = ["accounts", "students", "moze", "surveys", "photos"]
    
    print("\n🎯 SINGLE APP COMPREHENSIVE DEBUG")
    print("Failed apps to debug:")
    for i, app in enumerate(failed_apps, 1):
        print(f"  {i}. {app}")
    
    try:
        choice = input(f"\nChoose app to debug (1-{len(failed_apps)}): ").strip()
        app_index = int(choice) - 1
        
        if 0 <= app_index < len(failed_apps):
            app_name = failed_apps[app_index]
            print(f"\n🚀 Starting comprehensive debug for {app_name}...")
            success = run_comprehensive_debug(app_name)
            
            if success:
                print(f"\n🎉 {app_name} - ALL TESTS NOW PASSING!")
            else:
                print(f"\n⚠️  {app_name} - Still has failing tests. Check output above for details.")
        else:
            print("❌ Invalid choice")
            
    except ValueError:
        print("❌ Invalid input")
    except KeyboardInterrupt:
        print("\n👋 Debugging interrupted")

def main():
    """Main function"""
    print("🔬 COMPREHENSIVE TEST DEBUGGER")
    print("=" * 50)
    print("Shows ALL individual test failures with maximum detail")
    
    print("\nOptions:")
    print("1. Debug single app (detailed)")
    print("2. Debug all failed apps (comprehensive)")
    print("3. Quick status summary")
    print("4. Exit")
    
    try:
        choice = input("\nChoose option (1-4): ").strip()
        
        if choice == "1":
            debug_single_app_menu()
        elif choice == "2":
            run_all_apps_comprehensive()
        elif choice == "3":
            print("\n📊 CURRENT STATUS:")
            print("✅ PASSING: araz, doctordirectory, mahalshifa, evaluation")
            print("❌ FAILING: accounts, students, moze, surveys, photos")
            print("\n💡 Use option 1 or 2 for detailed debugging")
        elif choice == "4":
            print("👋 Goodbye!")
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n👋 Debugging interrupted")

if __name__ == "__main__":
    main()