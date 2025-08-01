#!/usr/bin/env python3
"""
Debug script to check exact HTML content
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from accounts.models import User

def debug_template():
    """Debug the template rendering"""
    print("🔍 Debugging Template Content...")
    
    admin_user = User.objects.filter(username='admin_1').first()
    client = Client()
    client.force_login(admin_user)
    
    try:
        url = reverse('mahalshifa:medical_record_list')
        response = client.get(url)
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Look for the button section
            if 'New Medical Record' in content:
                print("✅ Button text found")
                
                # Find the button section
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'New Medical Record' in line:
                        print(f"📋 Button line {i}: {line.strip()}")
                        # Show surrounding lines
                        for j in range(max(0, i-2), min(len(lines), i+3)):
                            print(f"   {j}: {lines[j].strip()}")
                        break
            else:
                print("❌ Button text not found")
            
            # Check for URL patterns
            if 'href=' in content:
                print("✅ href attributes found")
                # Look for medical record URLs
                if 'medical-records' in content:
                    print("✅ medical-records found in content")
                else:
                    print("❌ medical-records not found in content")
            else:
                print("❌ No href attributes found")
                
        else:
            print(f"❌ Response status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_template()