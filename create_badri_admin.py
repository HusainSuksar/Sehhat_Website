#!/usr/bin/env python3
"""
Simple script to create Badri Mahal Admin user
Run this in Django shell or as a management command
"""

# For Django shell usage:
from django.contrib.auth import get_user_model
from accounts.services import ITSService

User = get_user_model()

def create_badri_admin():
    admin_its_id = '50000001'
    
    print("🏥 Creating Badri Mahal Admin...")
    
    # Check if admin already exists
    if User.objects.filter(its_id=admin_its_id).exists():
        print(f"⚠️  Badri Mahal Admin with ITS ID {admin_its_id} already exists!")
        admin_user = User.objects.get(its_id=admin_its_id)
        print(f"✅ Found existing admin: {admin_user.get_full_name()}")
        return admin_user
    
    # Try to get data from ITS service
    print(f"🔍 Fetching data for ITS ID {admin_its_id}...")
    its_data = ITSService.fetch_user_data(admin_its_id)
    
    if its_data:
        print(f"✅ ITS data found: {its_data.get('first_name')} {its_data.get('last_name')}")
        
        # Create admin user from ITS data
        admin_user = User.objects.create_user(
            username='badri_admin',
            its_id=admin_its_id,
            first_name=its_data.get('first_name', 'Badri'),
            last_name=its_data.get('last_name', 'Admin'),
            email=its_data.get('email', 'admin@badrimahal.com'),
            role='badri_mahal_admin',
            is_superuser=True,
            is_staff=True,
            is_active=True
        )
    else:
        print("⚠️  ITS service returned no data, creating admin manually...")
        
        # Create admin user manually
        admin_user = User.objects.create_user(
            username='badri_admin',
            its_id=admin_its_id,
            first_name='Badri Mahal',
            last_name='Admin',
            email='admin@badrimahal.com',
            role='badri_mahal_admin',
            is_superuser=True,
            is_staff=True,
            is_active=True
        )
    
    # Set password
    admin_user.set_password('admin123')
    admin_user.save()
    
    print(f"✅ Created Badri Mahal Admin: {admin_user.get_full_name()}")
    
    # Display details
    print("\n" + "="*50)
    print("🏥 BADRI MAHAL ADMIN CREATED")
    print("="*50)
    print(f"Name: {admin_user.get_full_name()}")
    print(f"Username: {admin_user.username}")
    print(f"ITS ID: {admin_user.its_id}")
    print(f"Email: {admin_user.email}")
    print(f"Role: {admin_user.role}")
    print(f"is_admin: {admin_user.is_admin}")
    print(f"is_superuser: {admin_user.is_superuser}")
    print(f"is_staff: {admin_user.is_staff}")
    print(f"is_active: {admin_user.is_active}")
    print("\n🔐 LOGIN CREDENTIALS:")
    print(f"ITS ID: {admin_its_id}")
    print("Password: admin123")
    print("\n✅ Ready for testing!")
    
    return admin_user

# For direct execution
if __name__ == "__main__":
    import os
    import sys
    import django
    
    # Setup Django
    sys.path.append('/workspace')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
    django.setup()
    
    create_badri_admin()

# For Django shell usage, just run:
# exec(open('create_badri_admin.py').read())
# create_badri_admin()