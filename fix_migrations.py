#!/usr/bin/env python3

import os
import django
import subprocess
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

def run_makemigrations():
    """Run makemigrations for each app individually, answering 'N' to rename questions"""
    
    apps = ['araz', 'doctordirectory', 'evaluation', 'mahalshifa', 'photos', 'students']
    
    for app in apps:
        print(f"\n🔧 Creating migrations for {app}...")
        
        # Use subprocess with input to answer 'N' to all rename questions
        process = subprocess.Popen(
            ['python3', 'manage.py', 'makemigrations', app],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        # Send 'N' responses for any rename questions (up to 20 possible questions)
        input_text = '\n'.join(['N'] * 20) + '\n'
        
        try:
            output, _ = process.communicate(input=input_text, timeout=60)
            print(output)
            
            if process.returncode == 0:
                print(f"✅ Successfully created migrations for {app}")
            else:
                print(f"❌ Failed to create migrations for {app}")
                
        except subprocess.TimeoutExpired:
            process.kill()
            print(f"⏰ Timeout while creating migrations for {app}")

if __name__ == "__main__":
    print("🚀 Starting migration creation process...")
    run_makemigrations()
    print("\n✅ Migration creation process completed!")