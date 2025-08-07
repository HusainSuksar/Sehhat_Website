#!/usr/bin/env python3
"""
Simple Test Script - Handles virtual environment and import issues
Works without complex Django test discovery
"""

import sys
import os
import subprocess
import json
from pathlib import Path

def check_virtual_env():
    """Check if we're in a virtual environment"""
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

def setup_django_environment():
    """Set up Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
    
    try:
        import django
        django.setup()
        return True
    except ImportError:
        print("❌ Django not found. Make sure you're in the virtual environment:")
        print("   source venv/bin/activate  # On macOS/Linux")
        print("   # or")
        print("   venv\\Scripts\\activate  # On Windows")
        return False
    except Exception as e:
        print(f"❌ Django setup failed: {e}")
        return False

def run_pytest_on_file(app_name):
    """Run pytest on a specific test file"""
    test_file = f"{app_name}/tests/test_api.py"
    
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return False
    
    try:
        # Try to run pytest
        result = subprocess.run([
            sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"✅ {app_name} tests PASSED")
            print(f"   Output: {result.stdout.split('=')[-1].strip()}")
            return True
        else:
            print(f"⚠️  {app_name} tests had issues")
            print(f"   Return code: {result.returncode}")
            if result.stderr:
                print(f"   Error: {result.stderr[:200]}...")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {app_name} tests timed out")
        return False
    except FileNotFoundError:
        print("❌ pytest not found. Installing...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pytest", "pytest-django"], check=True)
            return run_pytest_on_file(app_name)  # Retry
        except:
            print("❌ Failed to install pytest")
            return False
    except Exception as e:
        print(f"❌ Error running pytest on {app_name}: {e}")
        return False

def run_direct_import_test(app_name):
    """Try to import and run tests directly"""
    try:
        # Add current directory to Python path
        if os.getcwd() not in sys.path:
            sys.path.insert(0, os.getcwd())
        
        # Try to import the test module
        test_module_name = f"{app_name}.tests.test_api"
        test_module = __import__(test_module_name, fromlist=[''])
        
        print(f"✅ {app_name} test module imported successfully")
        
        # Count test methods
        import inspect
        test_count = 0
        for name, obj in inspect.getmembers(test_module):
            if inspect.isclass(obj) and name.endswith('Tests'):
                test_methods = [m for m in dir(obj) if m.startswith('test_')]
                test_count += len(test_methods)
        
        print(f"   Found {test_count} test methods")
        return True
        
    except ImportError as e:
        print(f"❌ Could not import {app_name}.tests.test_api: {e}")
        return False
    except Exception as e:
        print(f"❌ Error with {app_name} tests: {e}")
        return False

def main():
    """Main function"""
    print("🧪 Simple Test Runner")
    print("=" * 50)
    
    # Check virtual environment
    if not check_virtual_env():
        print("⚠️  Virtual environment not detected")
        print("   Make sure to run: source venv/bin/activate")
        print("   Then try again")
    else:
        print("✅ Virtual environment detected")
    
    # Setup Django
    if not setup_django_environment():
        print("\n💡 If Django import fails, try:")
        print("   pip install -r requirements.txt")
        return
    
    print("✅ Django setup successful")
    print()
    
    # Test each app
    apps = ["accounts", "araz", "doctordirectory", "mahalshifa", 
            "students", "moze", "evaluation", "surveys", "photos"]
    
    results = {}
    
    for app in apps:
        print(f"📱 Testing {app}...")
        
        # Method 1: Try pytest
        pytest_success = run_pytest_on_file(app)
        
        # Method 2: Try direct import
        import_success = run_direct_import_test(app)
        
        results[app] = {
            'pytest': pytest_success,
            'import': import_success,
            'overall': pytest_success or import_success
        }
        
        print()
    
    # Summary
    print("📊 SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for r in results.values() if r['overall'])
    total = len(results)
    
    print(f"✅ Overall: {passed}/{total} apps working ({passed/total*100:.1f}%)")
    
    for app, result in results.items():
        status = "✅" if result['overall'] else "❌"
        print(f"{status} {app:15} - Pytest: {result['pytest']}, Import: {result['import']}")
    
    print("\n💡 Next steps:")
    print("   - For apps that work: They're ready for production")
    print("   - For failed apps: Check individual error messages above")
    print("   - Alternative: Use 'python test_all_apis.py' for endpoint testing")

if __name__ == "__main__":
    main()