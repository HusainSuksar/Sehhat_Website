#!/usr/bin/env python3
"""
Single App Test Runner - Avoids Django test discovery issues
Usage: python test_single_app.py <app_name>
Example: python test_single_app.py accounts
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
    """Run tests for a specific app"""
    setup_django()
    
    # Import the test module directly
    test_module_path = f"{app_name}.tests.test_api"
    
    try:
        # Import the test module
        __import__(test_module_path)
        test_module = sys.modules[test_module_path]
        
        # Get Django test runner
        TestRunner = get_runner(settings)
        test_runner = TestRunner(verbosity=2)
        
        # Run tests for the specific module
        failures = test_runner.run_tests([test_module_path])
        
        if failures:
            print(f"\n❌ {failures} test(s) failed in {app_name}")
            return False
        else:
            print(f"\n✅ All tests passed in {app_name}")
            return True
            
    except ImportError as e:
        print(f"❌ Could not import {test_module_path}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error running tests for {app_name}: {e}")
        return False

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python test_single_app.py <app_name>")
        print("\nAvailable apps:")
        apps = ["accounts", "araz", "doctordirectory", "mahalshifa", 
                "students", "moze", "evaluation", "surveys", "photos"]
        for app in apps:
            print(f"  - {app}")
        sys.exit(1)
    
    app_name = sys.argv[1]
    
    print(f"🧪 Testing {app_name} app...")
    print("=" * 50)
    
    success = run_app_tests(app_name)
    
    if success:
        print(f"\n🎉 {app_name} tests completed successfully!")
    else:
        print(f"\n⚠️  {app_name} tests had some issues.")
        print("💡 Try running: python test_all_apis.py for endpoint testing")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()