#!/usr/bin/env python
"""
Test User Creation Script for Umoor Sehhat
This script creates representative users for testing all functionalities
without requiring actual ITS database integration.

Run with: python manage.py shell < create_test_users.py
"""

import os
import django
from django.contrib.auth import get_user_model
from faker import Faker

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings_pythonanywhere')
django.setup()

User = get_user_model()
fake = Faker()

def create_test_users():
    """Create comprehensive test users for all roles"""
    
    print("🚀 Creating test users for Umoor Sehhat...")
    
    # Clear existing users (except superuser)
    User.objects.filter(is_superuser=False).delete()
    
    # Test user data
    test_users = [
        # Admin Users
        {
            'username': 'admin_user1',
            'email': 'admin1@test.com',
            'first_name': 'Ahmed',
            'last_name': 'Khan',
            'role': 'badri_mahal_admin',
            'password': 'test123456',
            'is_staff': True,
        },
        {
            'username': 'admin_user2',
            'email': 'admin2@test.com',
            'first_name': 'Fatima',
            'last_name': 'Ali',
            'role': 'badri_mahal_admin',
            'password': 'test123456',
            'is_staff': True,
        },
        
        # Students
        {
            'username': 'student_001',
            'email': 'student1@test.com',
            'first_name': 'Mohammad',
            'last_name': 'Hassan',
            'role': 'student',
            'password': 'test123456',
            'student_id': 'STD001',
        },
        {
            'username': 'student_002',
            'email': 'student2@test.com',
            'first_name': 'Aisha',
            'last_name': 'Ahmed',
            'role': 'student',
            'password': 'test123456',
            'student_id': 'STD002',
        },
        {
            'username': 'student_003',
            'email': 'student3@test.com',
            'first_name': 'Omar',
            'last_name': 'Sheikh',
            'role': 'student',
            'password': 'test123456',
            'student_id': 'STD003',
        },
        
        # Doctors
        {
            'username': 'doctor_001',
            'email': 'doctor1@test.com',
            'first_name': 'Dr. Yasmin',
            'last_name': 'Rashid',
            'role': 'doctor',
            'password': 'test123456',
            'license_number': 'DOC001',
            'specialization': 'General Medicine',
        },
        {
            'username': 'doctor_002',
            'email': 'doctor2@test.com',
            'first_name': 'Dr. Imran',
            'last_name': 'Malik',
            'role': 'doctor',
            'password': 'test123456',
            'license_number': 'DOC002',
            'specialization': 'Cardiology',
        },
        
        # Aamils (Moze Managers)
        {
            'username': 'aamil_001',
            'email': 'aamil1@test.com',
            'first_name': 'Abdullah',
            'last_name': 'Rahman',
            'role': 'aamil',
            'password': 'test123456',
            'department': 'Moze Management',
        },
        {
            'username': 'aamil_002',
            'email': 'aamil2@test.com',
            'first_name': 'Khadija',
            'last_name': 'Siddique',
            'role': 'aamil',
            'password': 'test123456',
            'department': 'Moze Management',
        },
        
        # Moze Coordinators
        {
            'username': 'coordinator_001',
            'email': 'coord1@test.com',
            'first_name': 'Hassan',
            'last_name': 'Qureshi',
            'role': 'moze_coordinator',
            'password': 'test123456',
            'department': 'Academic Affairs',
        },
        {
            'username': 'coordinator_002',
            'email': 'coord2@test.com',
            'first_name': 'Zainab',
            'last_name': 'Tariq',
            'role': 'moze_coordinator',
            'password': 'test123456',
            'department': 'Student Affairs',
        },
        
        # Regular Users (for general access)
        {
            'username': 'user_001',
            'email': 'user1@test.com',
            'first_name': 'Ali',
            'last_name': 'Raza',
            'role': 'user',
            'password': 'test123456',
        },
        {
            'username': 'user_002',
            'email': 'user2@test.com',
            'first_name': 'Maryam',
            'last_name': 'Iqbal',
            'role': 'user',
            'password': 'test123456',
        },
    ]
    
    created_users = []
    
    for user_data in test_users:
        password = user_data.pop('password')
        
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=password,
            **{k: v for k, v in user_data.items() if k not in ['username', 'email']}
        )
        
        created_users.append(user)
        print(f"✅ Created {user.role}: {user.username} ({user.first_name} {user.last_name})")
    
    return created_users

def create_additional_test_data():
    """Create additional test data for relationships"""
    print("\n🔗 Creating additional test data...")
    
    # Import models
    from moze.models import Moze
    from evaluation.models import EvaluationForm, EvaluationQuestion, EvaluationAnswerOption
    
    # Get users
    aamils = User.objects.filter(role='aamil')
    coordinators = User.objects.filter(role='moze_coordinator')
    
    # Create some Moze records
    moze_data = [
        {
            'name': 'Mohammad Bilal',
            'email': 'bilal@test.com',
            'phone': '+92-300-1234567',
            'address': 'Karachi, Pakistan',
            'aamil': aamils.first() if aamils.exists() else None,
            'moze_coordinator': coordinators.first() if coordinators.exists() else None,
        },
        {
            'name': 'Ahmed Raza',
            'email': 'ahmed@test.com',
            'phone': '+92-300-7654321',
            'address': 'Lahore, Pakistan',
            'aamil': aamils.last() if aamils.count() > 1 else aamils.first(),
            'moze_coordinator': coordinators.last() if coordinators.count() > 1 else coordinators.first(),
        },
        {
            'name': 'Usman Ghani',
            'email': 'usman@test.com',
            'phone': '+92-300-9876543',
            'address': 'Islamabad, Pakistan',
            'aamil': aamils.first() if aamils.exists() else None,
            'moze_coordinator': coordinators.first() if coordinators.exists() else None,
        }
    ]
    
    for moze_info in moze_data:
        moze, created = Moze.objects.get_or_create(
            name=moze_info['name'],
            defaults=moze_info
        )
        if created:
            print(f"✅ Created Moze: {moze.name}")
    
    # Create sample evaluation form
    admin_user = User.objects.filter(role='badri_mahal_admin').first()
    if admin_user:
        form, created = EvaluationForm.objects.get_or_create(
            title='Moze Performance Evaluation',
            defaults={
                'description': 'Comprehensive evaluation form for Moze performance assessment',
                'target_role': 'all',
                'created_by': admin_user,
                'is_active': True,
            }
        )
        
        if created:
            print(f"✅ Created evaluation form: {form.title}")
            
            # Create sample questions
            questions_data = [
                {
                    'text': 'How would you rate the overall performance?',
                    'question_type': 'multiple_choice',
                    'order': 1,
                },
                {
                    'text': 'What is the attendance level?',
                    'question_type': 'dropdown',
                    'order': 2,
                },
                {
                    'text': 'How effective is the communication?',
                    'question_type': 'multiple_choice',
                    'order': 3,
                }
            ]
            
            for q_data in questions_data:
                question = EvaluationQuestion.objects.create(
                    form=form,
                    **q_data
                )
                
                # Create answer options with weights
                if question.question_type == 'multiple_choice':
                    options = [
                        ('Excellent', 5),
                        ('Good', 4),
                        ('Average', 3),
                        ('Poor', 2),
                        ('Very Poor', 1),
                    ]
                else:  # dropdown
                    options = [
                        ('Always Present', 5),
                        ('Usually Present', 4),
                        ('Sometimes Present', 3),
                        ('Rarely Present', 2),
                        ('Never Present', 1),
                    ]
                
                for option_text, weight in options:
                    EvaluationAnswerOption.objects.create(
                        question=question,
                        text=option_text,
                        weight=weight
                    )
                
                print(f"✅ Created question: {question.text[:50]}...")

def print_login_credentials():
    """Print login credentials for testing"""
    print("\n" + "="*60)
    print("🔑 TEST LOGIN CREDENTIALS")
    print("="*60)
    
    roles = [
        ('Admin Users', 'badri_mahal_admin'),
        ('Students', 'student'),
        ('Doctors', 'doctor'),
        ('Aamils', 'aamil'),
        ('Coordinators', 'moze_coordinator'),
        ('Regular Users', 'user'),
    ]
    
    for role_name, role_code in roles:
        print(f"\n📋 {role_name}:")
        users = User.objects.filter(role=role_code)
        for user in users:
            print(f"   Username: {user.username}")
            print(f"   Password: test123456")
            print(f"   Email: {user.email}")
            print(f"   Name: {user.first_name} {user.last_name}")
            print("   " + "-"*30)
    
    print(f"\n🌐 Test URL: https://yourusername.pythonanywhere.com")
    print(f"📧 All passwords: test123456")
    print("\n" + "="*60)

if __name__ == '__main__':
    # Create test users
    users = create_test_users()
    
    # Create additional test data
    create_additional_test_data()
    
    # Print credentials
    print_login_credentials()
    
    print(f"\n🎉 Successfully created {len(users)} test users!")
    print("🚀 Your application is ready for testing!")

# Run the script
create_test_users()
create_additional_test_data()
print_login_credentials()