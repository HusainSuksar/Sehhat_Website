#!/usr/bin/env python3
"""
Detailed Test Runner - Shows actual test results and errors
"""

import sys
import os
import subprocess
import time

def setup_django_environment():
    """Set up Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
    
    try:
        import django
        django.setup()
        return True
    except ImportError:
        print("❌ Django not found. Make sure you're in the virtual environment:")
        print("   source venv/bin/activate")
        return False
    except Exception as e:
        print(f"❌ Django setup failed: {e}")
        return False

def run_detailed_pytest(app_name):
    """Run pytest with detailed output"""
    test_file = f"{app_name}/tests/test_api.py"
    
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return False
    
    print(f"\n🔍 Running detailed tests for {app_name}...")
    print("=" * 60)
    
    try:
        # Run pytest with verbose output
        result = subprocess.run([
            sys.executable, "-m", "pytest", test_file, 
            "-v", "--tb=short", "--no-header", "--maxfail=5"
        ], capture_output=True, text=True, timeout=300)
        
        print(f"📊 Return code: {result.returncode}")
        
        if result.stdout:
            print("📋 STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("⚠️  STDERR:")
            print(result.stderr)
        
        # Analyze results
        if result.returncode == 0:
            print(f"✅ {app_name}: ALL TESTS PASSED")
            return True
        elif result.returncode == 1:
            print(f"⚠️  {app_name}: SOME TESTS FAILED")
            return False
        elif result.returncode == 2:
            print(f"🔧 {app_name}: TEST INTERRUPTED OR CONFIGURATION ISSUE")
            return False
        else:
            print(f"❌ {app_name}: UNEXPECTED ERROR (code {result.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {app_name} tests timed out")
        return False
    except FileNotFoundError:
        print("❌ pytest not found. Try: pip install pytest pytest-django")
        return False
    except Exception as e:
        print(f"❌ Error running pytest on {app_name}: {e}")
        return False

def run_single_app_test():
    """Run a single app test interactively"""
    apps = ["accounts", "araz", "doctordirectory", "mahalshifa", 
            "students", "moze", "evaluation", "surveys", "photos"]
    
    print("\n🎯 Single App Detailed Testing")
    print("Available apps:")
    for i, app in enumerate(apps, 1):
        print(f"  {i}. {app}")
    
    try:
        choice = input(f"\nEnter app number (1-{len(apps)}) or 'all' for all apps: ").strip().lower()
        
        if choice == 'all':
            print("\n🚀 Running detailed tests for ALL apps...")
            passed = 0
            for app in apps:
                success = run_detailed_pytest(app)
                if success:
                    passed += 1
                print("\n" + "="*80 + "\n")
            
            print(f"\n📊 FINAL SUMMARY: {passed}/{len(apps)} apps passed")
            
        else:
            app_index = int(choice) - 1
            if 0 <= app_index < len(apps):
                app_name = apps[app_index]
                run_detailed_pytest(app_name)
            else:
                print("❌ Invalid app number")
                
    except ValueError:
        print("❌ Invalid input")
    except KeyboardInterrupt:
        print("\n👋 Testing interrupted by user")

def main():
    """Main function"""
    print("🔬 Detailed Test Runner")
    print("=" * 50)
    
    # Setup Django
    if not setup_django_environment():
        print("\n💡 Make sure you're in the virtual environment:")
        print("   source venv/bin/activate")
        return
    
    print("✅ Django setup successful")
    
    print("\nOptions:")
    print("1. Test single app (with detailed output)")
    print("2. Test all apps (with detailed output)")
    print("3. Quick endpoint test")
    
    try:
        choice = input("\nChoose option (1-3): ").strip()
        
        if choice == "1":
            run_single_app_test()
        elif choice == "2":
            apps = ["accounts", "araz", "doctordirectory", "mahalshifa", 
                    "students", "moze", "evaluation", "surveys", "photos"]
            
            print("\n🚀 Running detailed tests for ALL apps...")
            passed = 0
            for app in apps:
                success = run_detailed_pytest(app)
                if success:
                    passed += 1
                print("\n" + "="*80 + "\n")
                time.sleep(1)  # Brief pause between apps
            
            print(f"\n🎯 FINAL SUMMARY: {passed}/{len(apps)} apps passed")
            
        elif choice == "3":
            print("\n🚀 Running quick endpoint test...")
            try:
                result = subprocess.run([sys.executable, "test_all_apis.py"], 
                                      capture_output=True, text=True)
                print(result.stdout)
                if result.stderr:
                    print("Errors:", result.stderr)
            except Exception as e:
                print(f"❌ Error running endpoint test: {e}")
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n👋 Testing interrupted by user")

if __name__ == "__main__":
    main()