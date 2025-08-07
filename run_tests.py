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
                success = run_command(
                    f"python -m pytest {app_name}/tests/ -v", 
                    f"Testing {app_name} app"
                )
                if not success:
                    # Fallback to Django test runner for single app
                    success = run_command(
                        f"python manage.py test {app_name} --verbosity=2",
                        f"Testing {app_name} app (Django runner)"
                    )
            else:
                print("❌ Invalid app number")
                sys.exit(1)
        except ValueError:
            print("❌ Invalid input")
            sys.exit(1)
            
    elif choice == "3":
        # All unit tests with different approaches
        print("⚠️  Trying different test runners due to potential path issues...")
        
        # Try pytest first
        success = run_command("python -m pytest --tb=short", "Running all tests with pytest")
        
        if not success:
            # Try Django test runner with specific apps
            apps = ["accounts.tests.test_api", "araz.tests.test_api", "doctordirectory.tests.test_api"]
            for app in apps[:3]:  # Test first 3 apps
                run_command(f"python manage.py test {app} --verbosity=1", f"Testing {app}")
    
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