#!/usr/bin/env python
import subprocess
import sys

def run_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        print(f"Command: {cmd}")
        print(f"Return code: {result.returncode}")
        if result.stdout:
            print(f"Output: {result.stdout}")
        if result.stderr:
            print(f"Error: {result.stderr}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"Command timed out: {cmd}")
        return False
    except Exception as e:
        print(f"Error running command: {e}")
        return False

def main():
    print("🚀 Starting git commit process...")
    
    # Add all changes
    if not run_command("git add ."):
        print("❌ Failed to add files")
        return False
    
    # Commit changes
    if not run_command('git commit -m "Add Django management command for test data generation"'):
        print("❌ Failed to commit changes")
        return False
    
    # Push to main branch
    if not run_command("git push origin main"):
        print("❌ Failed to push to main branch")
        return False
    
    print("✅ Successfully committed and pushed changes to main branch!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)