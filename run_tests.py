#!/usr/bin/env python3
"""
Test runner script that handles Python path issues
"""
import os
import sys
import subprocess

def run_command(command, description):
    """Run a command and return success status"""
    print(f"\n🔧 {description}")
    print(f"Command: {command}")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=False, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code: {e.returncode}")
        return False

def main():
    """Main test runner"""
    print("🧪 Sehhat Website Test Runner")
    print("=" * 60)
    
    # Ensure we're in the right directory
    if not os.path.exists('manage.py'):
        print("❌ Error: manage.py not found. Run this script from the project root.")
        sys.exit(1)
    
    # Test options
    print("\nAvailable test options:")
    print("1. Quick API endpoint test")
    print("2. Run specific app tests")
    print("3. Run all unit tests (may have path issues)")
    print("4. Check server status")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        # Quick API test
        success = run_command("python test_all_apis.py", "Quick API endpoint testing")
        
    elif choice == "2":
        # Specific app tests
        print("\nAvailable apps:")
        apps = ["accounts", "araz", "doctordirectory", "mahalshifa", 
                "students", "moze", "evaluation", "surveys", "photos"]
        
        for i, app in enumerate(apps, 1):
            print(f"{i}. {app}")
        
        app_choice = input(f"\nEnter app number (1-{len(apps)}): ").strip()
        
        try:
            app_index = int(app_choice) - 1
            if 0 <= app_index < len(apps):
                app_name = apps[app_index]
                
                # Try multiple approaches
                print(f"\n🔧 Testing {app_name} app with different methods...")
                
                # Method 1: Direct test file
                success = run_command(
                    f"python -m pytest {app_name}/tests/test_api.py -v --tb=short", 
                    f"Testing {app_name}/tests/test_api.py with pytest"
                )
                
                if not success:
                    # Method 2: Django test runner with specific module
                    success = run_command(
                        f"python manage.py test {app_name}.tests.test_api --verbosity=1",
                        f"Testing {app_name}.tests.test_api with Django runner"
                    )
                
                if not success:
                    # Method 3: Run individual test file directly
                    success = run_command(
                        f"cd {app_name}/tests && python -m pytest test_api.py -v",
                        f"Testing {app_name} test file directly"
                    )
                
                if not success:
                    print(f"⚠️  All test methods failed for {app_name}. This might be due to:")
                    print(f"   - Missing dependencies")
                    print(f"   - Database issues")
                    print(f"   - Import path conflicts")
                    print(f"   Try: python test_all_apis.py for endpoint testing instead")
                    
            else:
                print("❌ Invalid app number")
                sys.exit(1)
        except ValueError:
            print("❌ Invalid input")
            sys.exit(1)
            
    elif choice == "3":
        # All unit tests with different approaches
        print("⚠️  Due to Python path issues with Django's test discovery,")
        print("    we'll use alternative approaches...")
        
        # Method 1: Try pytest with specific test files
        print("\n🔧 Method 1: Testing with pytest on specific files")
        apps = ["accounts", "araz", "doctordirectory", "mahalshifa", "students", 
                "moze", "evaluation", "surveys", "photos"]
        
        passed_apps = []
        failed_apps = []
        
        for app in apps:
            success = run_command(
                f"python -m pytest {app}/tests/test_api.py -v --tb=line", 
                f"Testing {app} API"
            )
            if success:
                passed_apps.append(app)
            else:
                failed_apps.append(app)
        
        print(f"\n📊 Pytest Results:")
        print(f"✅ Passed: {len(passed_apps)} apps - {passed_apps}")
        print(f"❌ Failed: {len(failed_apps)} apps - {failed_apps}")
        
        if failed_apps:
            print(f"\n🔧 Method 2: Trying Django test runner for failed apps")
            for app in failed_apps[:3]:  # Try first 3 failed apps
                run_command(
                    f"python manage.py test {app}.tests.test_api --verbosity=1", 
                    f"Django runner: {app}"
                )
    
    elif choice == "4":
        # Server status check
        success = run_command("python manage.py check", "Django system check")
        if success:
            print("\n✅ Server configuration is healthy")
            print("🚀 You can start the server with: python manage.py runserver")
        
    else:
        print("❌ Invalid choice")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("📖 For detailed testing instructions, see: API_TESTING_GUIDE_MACOS.md")
    print("🔧 For manual testing, start server: python manage.py runserver")

if __name__ == "__main__":
    main()