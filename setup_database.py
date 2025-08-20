#!/usr/bin/env python
"""Quick database setup script"""

import os
import subprocess
import sys

def run_command(cmd):
    """Run a command and return success status"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(result.stdout)
    return True

def main():
    print("Setting up database...")
    
    # Remove old database
    if os.path.exists('db.sqlite3'):
        os.remove('db.sqlite3')
        print("✓ Removed old database")
    
    # Create migrations
    if not run_command("python manage.py makemigrations"):
        print("Failed to create migrations")
        return
    
    # Run migrations
    if not run_command("python manage.py migrate"):
        print("Failed to run migrations")
        return
    
    print("\n✓ Database setup complete!")
    print("\nYou can now run: python generate_mock_data.py")

if __name__ == '__main__':
    main()