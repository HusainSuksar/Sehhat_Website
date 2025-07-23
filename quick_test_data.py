#!/usr/bin/env python3
"""
Quick Test Data for Umoor Sehhat
Creates minimal test data to verify functionality
"""

import os
import sys
import django
from datetime import datetime, timedelta, date
import random

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

User = get_user_model()

def create_basic_test_data():
    """Create basic test data"""
    print("🚀 CREATING BASIC TEST DATA")
    print("=" * 50)
    
    try:
        with transaction.atomic():
            # Create a variety of test users
            test_users = []
            roles = ['admin', 'doctor', 'student', 'aamil', 'moze_coordinator']
            
            for i, role in enumerate(roles):
                for j in range(3):  # 3 users per role
                    username = f"{role}_{j+1}"
                    if not User.objects.filter(username=username).exists():
                        user = User.objects.create_user(
                            username=username,
                            email=f"{username}@test.com",
                            password='test123',
                            first_name=f"Test{role.title()}",
                            last_name=f"User{j+1}",
                            role=role,
                            its_id=f"{random.randint(10000000, 99999999)}",
                            phone_number=f"+1555000{i}{j+1}00",
                            age=random.randint(20, 60),
                            is_active=True
                        )
                        test_users.append(user)
                        print(f"✅ Created {role} user: {username}")
            
            print(f"\n📊 SUMMARY:")
            print(f"👥 Total Users: {User.objects.count()}")
            for role in roles:
                count = User.objects.filter(role=role).count()
                print(f"   {role.title()}: {count}")
            
            print(f"\n🔑 Test Login Credentials:")
            print(f"   Username: admin | Password: admin123 (Original)")
            print(f"   Username: admin_1 | Password: test123")
            print(f"   Username: doctor_1 | Password: test123")
            print(f"   Username: student_1 | Password: test123")
            print(f"   Username: aamil_1 | Password: test123")
            print(f"   Username: moze_coordinator_1 | Password: test123")
            
            print(f"\n✅ Basic test data created successfully!")
            print(f"🎯 You can now test the application with multiple user roles")
            
            return True
            
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_basic_test_data()
    sys.exit(0 if success else 1)