#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

from accounts.forms import CustomLoginForm
from django.test import RequestFactory

def test_login():
    """Test login functionality"""
    factory = RequestFactory()
    request = factory.post('/accounts/login/', {
        'its_id': '50000001',
        'password': 'test123'
    })
    
    form = CustomLoginForm(data={
        'its_id': '50000001',
        'password': 'test123'
    }, request=request)
    
    print("🔍 Testing login form...")
    
    if form.is_valid():
        user = form.get_user()
        print(f"✅ Login successful for user: {user.get_full_name()} ({user.get_role_display()})")
        print(f"📧 Email: {user.email}")
        print(f"🆔 ITS ID: {user.its_id}")
        return True
    else:
        print("❌ Login failed:")
        for field, errors in form.errors.items():
            print(f"  - {field}: {errors}")
        return False

if __name__ == "__main__":
    test_login()