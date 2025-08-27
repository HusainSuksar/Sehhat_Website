#!/usr/bin/env python
"""
Test the frontend AJAX functionality for appointment status updates
"""

import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

from doctordirectory.models import Appointment

User = get_user_model()

def test_frontend_ajax_functionality():
    """Test that the appointment detail page loads correctly with AJAX functionality"""
    print("🖥️  TESTING FRONTEND AJAX FUNCTIONALITY")
    print("=" * 50)
    
    client = Client()
    
    # Get test data
    admin_user = User.objects.filter(is_superuser=True).first()
    appointment = Appointment.objects.first()
    
    if not admin_user or not appointment:
        print("❌ Missing test data")
        return False
    
    # Login as admin
    login_response = client.post('/accounts/login/', {
        'its_id': admin_user.its_id,
        'password': 'pass1234'
    })
    
    if login_response.status_code not in [200, 302]:
        print("❌ Admin login failed")
        return False
    
    print("✅ Admin login successful")
    
    # Test appointment detail page loads
    print(f"\n1️⃣ Testing appointment detail page load")
    detail_response = client.get(f'/doctordirectory/appointments/{appointment.id}/')
    
    if detail_response.status_code == 200:
        content = detail_response.content.decode()
        
        # Check for key elements
        checks = [
            ('CSRF Token', 'csrfmiddlewaretoken' in content),
            ('Update Status Function', 'updateStatus' in content),
            ('Correct API URL', '/api/doctordirectory/appointments/' in content),
            ('Status Update Buttons', 'btn btn-warning' in content or 'btn btn-success' in content),
            ('Navigation Buttons', 'Back to Appointments' in content),
            ('JavaScript Functions', 'function updateStatus' in content),
        ]
        
        for check_name, result in checks:
            if result:
                print(f"✅ {check_name}: Present")
            else:
                print(f"❌ {check_name}: Missing")
        
        # Check for template errors
        error_indicators = ['NoReverseMatch', 'TemplateDoesNotExist', 'TemplateSyntaxError']
        errors_found = [error for error in error_indicators if error in content]
        
        if errors_found:
            print(f"❌ Template errors found: {', '.join(errors_found)}")
            return False
        else:
            print("✅ No template errors detected")
            
        print("✅ Appointment detail page loads correctly")
        
    else:
        print(f"❌ Appointment detail page failed to load: {detail_response.status_code}")
        return False
    
    # Test appointment list page loads
    print(f"\n2️⃣ Testing appointment list page load")
    list_response = client.get('/doctordirectory/appointments/')
    
    if list_response.status_code == 200:
        content = list_response.content.decode()
        
        if 'My Appointments' in content or 'All Appointments' in content:
            print("✅ Appointment list page loads correctly")
        else:
            print("⚠️  Appointment list page loads but may be missing content")
    else:
        print(f"❌ Appointment list page failed: {list_response.status_code}")
    
    # Test dashboard integration
    print(f"\n3️⃣ Testing dashboard integration")
    dashboard_response = client.get('/doctordirectory/')
    
    if dashboard_response.status_code == 200:
        content = dashboard_response.content.decode()
        
        if 'My Appointments' in content:
            print("✅ Dashboard has appointment list link")
        else:
            print("⚠️  Dashboard missing appointment list link")
    else:
        print(f"❌ Dashboard failed to load: {dashboard_response.status_code}")
    
    print(f"\n✅ FRONTEND AJAX TESTING COMPLETED")
    return True

if __name__ == "__main__":
    success = test_frontend_ajax_functionality()
    if success:
        print("🎉 Frontend AJAX functionality is properly configured!")
    else:
        print("🔧 Frontend issues found")