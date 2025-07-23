#!/usr/bin/env python3
"""
Simple test script to populate basic data using existing database schema
"""

import os
import sys
import django
from datetime import datetime, timedelta, date
from decimal import Decimal
import random

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

# Import models that we know exist in the database
from django.contrib.auth import get_user_model
from accounts.models import User, UserProfile
from moze.models import Moze, MozeComment
from surveys.models import Survey, SurveyResponse

User = get_user_model()

def create_basic_users():
    """Create basic test users"""
    print("🏗️  Creating basic test users...")
    
    users_data = [
        {'username': 'admin', 'email': 'admin@sehhat.com', 'role': 'badri_mahal_admin', 'first_name': 'System', 'last_name': 'Administrator'},
        {'username': 'dr_ahmed', 'email': 'ahmed@sehhat.com', 'role': 'doctor', 'first_name': 'Dr. Ahmed', 'last_name': 'Hassan'},
        {'username': 'aamil_karachi', 'email': 'aamil.khi@sehhat.com', 'role': 'aamil', 'first_name': 'Aamil', 'last_name': 'Karachi'},
        {'username': 'coordinator_1', 'email': 'coord1@sehhat.com', 'role': 'moze_coordinator', 'first_name': 'Hassan', 'last_name': 'Coordinator'},
        {'username': 'student_ali', 'email': 'ali.student@sehhat.com', 'role': 'student', 'first_name': 'Ali', 'last_name': 'Ahmed'},
    ]
    
    created_users = {}
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'role': user_data['role'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'its_id': f"{random.randint(10000000, 99999999)}",
            }
        )
        if created:
            user.set_password('test123')
            user.save()
            print(f"  ✅ Created user: {user.username}")
        else:
            print(f"  ⚡ User already exists: {user.username}")
        
        created_users[user_data['role']] = user
        
        # Create user profile
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'bio': f'Test bio for {user.get_full_name()}',
                'location': 'Test Location',
            }
        )
        
    return created_users

def create_basic_mozes(users):
    """Create basic moze data"""
    print("🏘️  Creating basic Moze data...")
    
    moze_data = [
        {'name': 'Karachi Central Moze', 'location': 'Karachi, Sindh'},
        {'name': 'Lahore Medical Center', 'location': 'Lahore, Punjab'},
        {'name': 'Islamabad Health Center', 'location': 'Islamabad, ICT'},
    ]
    
    created_mozes = []
    for data in moze_data:
        moze, created = Moze.objects.get_or_create(
            name=data['name'],
            defaults={
                'location': data['location'],
                'aamil': users['aamil'],
                'moze_coordinator': users['moze_coordinator'],
                'address': f"Address for {data['name']}",
                'established_date': date.today() - timedelta(days=random.randint(365, 1825)),
                'capacity': random.randint(50, 200),
                'contact_phone': f"+92-{random.randint(300, 399)}-{random.randint(1000000, 9999999)}",
                'contact_email': f"contact@{data['name'].lower().replace(' ', '')}.com",
            }
        )
        
        if created:
            print(f"  ✅ Created Moze: {moze.name}")
        else:
            print(f"  ⚡ Moze already exists: {moze.name}")
            
        created_mozes.append(moze)
    
    return created_mozes

def create_basic_surveys(users):
    """Create basic survey data"""
    print("📋 Creating basic Survey data...")
    
    survey_data = [
        {
            'title': 'Medical Service Quality Survey',
            'description': 'Please rate the quality of medical services',
            'target_role': 'all',
            'questions': [
                {
                    "id": 1,
                    "type": "multiple_choice",
                    "question": "How satisfied are you with the medical services?",
                    "required": True,
                    "options": ["Very Satisfied", "Satisfied", "Neutral", "Dissatisfied", "Very Dissatisfied"]
                },
                {
                    "id": 2,
                    "type": "text",
                    "question": "What can we improve?",
                    "required": False,
                    "options": []
                }
            ]
        },
        {
            'title': 'Doctor Performance Feedback',
            'description': 'Feedback on doctor performance',
            'target_role': 'student',
            'questions': [
                {
                    "id": 1,
                    "type": "rating",
                    "question": "Rate the doctor's communication skills (1-5)",
                    "required": True,
                    "options": ["1", "2", "3", "4", "5"]
                }
            ]
        }
    ]
    
    created_surveys = []
    for data in survey_data:
        survey, created = Survey.objects.get_or_create(
            title=data['title'],
            defaults={
                'description': data['description'],
                'target_role': data['target_role'],
                'questions': data['questions'],
                'created_by': users['badri_mahal_admin'],
                'is_active': True,
                'start_date': datetime.now(),
                'end_date': datetime.now() + timedelta(days=30),
            }
        )
        
        if created:
            print(f"  ✅ Created Survey: {survey.title}")
        else:
            print(f"  ⚡ Survey already exists: {survey.title}")
            
        created_surveys.append(survey)
    
    return created_surveys

def main():
    """Main execution function"""
    print("🚀 STARTING BASIC DATA POPULATION")
    print("=" * 50)
    
    try:
        # Create users
        users = create_basic_users()
        
        # Create mozes
        mozes = create_basic_mozes(users)
        
        # Create surveys
        surveys = create_basic_surveys(users)
        
        print("\n✅ BASIC DATA POPULATION COMPLETED SUCCESSFULLY!")
        print(f"  - Created {len(users)} users")
        print(f"  - Created {len(mozes)} mozes")
        print(f"  - Created {len(surveys)} surveys")
        
    except Exception as e:
        print(f"\n❌ ERROR DURING POPULATION: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()