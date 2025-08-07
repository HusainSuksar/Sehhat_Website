#!/usr/bin/env python3
"""
Setup Diagnostic Script
Checks if all required files are present and provides solutions
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath):
    """Check if a file exists and return status"""
    if os.path.exists(filepath):
        return f"✅ {filepath}"
    else:
        return f"❌ {filepath} - MISSING"

def main():
    print("🔍 Setup Diagnostic Script")
    print("=" * 50)
    
    # Check current directory
    current_dir = os.getcwd()
    print(f"📂 Current directory: {current_dir}")
    
    # Check if we're in the right project
    if "Sehhat_Website" not in current_dir:
        print("⚠️  You might not be in the Sehhat_Website directory")
        print("   Try: cd /path/to/your/Sehhat_Website")
    
    print("\n📋 Checking essential files...")
    
    # Check essential project files
    essential_files = [
        "manage.py",
        "requirements.txt",
        "test_all_apis.py",
        "test_simple.py",
        "API_TESTING_GUIDE_MACOS.md"
    ]
    
    for file in essential_files:
        print(check_file_exists(file))
    
    print("\n🧪 Checking test files...")
    
    # Check test files for each app
    apps = ["accounts", "araz", "doctordirectory", "mahalshifa", 
            "students", "moze", "evaluation", "surveys", "photos"]
    
    missing_tests = []
    
    for app in apps:
        test_file = f"{app}/tests/test_api.py"
        status = check_file_exists(test_file)
        print(status)
        
        if "MISSING" in status:
            missing_tests.append(app)
    
    print("\n📊 SUMMARY")
    print("=" * 50)
    
    if missing_tests:
        print(f"❌ Missing test files for: {', '.join(missing_tests)}")
        print("\n🔧 SOLUTIONS:")
        print("1. Pull latest changes from repository:")
        print("   git pull origin main")
        print()
        print("2. Check git status:")
        print("   git status")
        print()
        print("3. If files are still missing, try:")
        print("   git fetch origin")
        print("   git reset --hard origin/main")
        print()
        print("4. Alternative: Use endpoint testing instead:")
        print("   python test_all_apis.py")
    else:
        print("✅ All test files found!")
        print("\n🚀 You can now run:")
        print("   python test_simple.py")
        print("   python test_all_apis.py")
    
    print("\n🌐 Git Status Check:")
    print("-" * 30)
    
    try:
        import subprocess
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            if result.stdout.strip():
                print("📝 Uncommitted changes found:")
                print(result.stdout)
            else:
                print("✅ Working directory clean")
        else:
            print("❌ Could not check git status")
    except:
        print("❌ Git not available or not in git repository")
    
    print("\n📡 Remote Status Check:")
    print("-" * 30)
    
    try:
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            local_commit = result.stdout.strip()[:8]
            print(f"🏠 Local commit: {local_commit}")
            
            result = subprocess.run(['git', 'rev-parse', 'origin/main'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                remote_commit = result.stdout.strip()[:8]
                print(f"🌐 Remote commit: {remote_commit}")
                
                if local_commit == remote_commit:
                    print("✅ Local and remote are in sync")
                else:
                    print("⚠️  Local and remote are different - try: git pull origin main")
            else:
                print("❌ Could not check remote commit")
        else:
            print("❌ Could not check local commit")
    except:
        print("❌ Git command failed")

if __name__ == "__main__":
    main()