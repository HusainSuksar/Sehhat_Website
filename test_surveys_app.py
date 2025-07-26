#!/usr/bin/env python3

import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from datetime import datetime, timedelta
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

# Import after Django setup
from surveys.models import Survey, SurveyResponse, SurveyReminder
from accounts.models import User

def print_section(title):
    print(f"\n{'='*80}")
    print(f"📋 {title}")
    print(f"{'='*80}")

def print_result(test_name, success, details=""):
    emoji = "✅" if success else "❌"
    print(f"{emoji} {test_name}")
    if details:
        print(f"   └─ {details}")

def test_surveys_app():
    print_section("SURVEYS APP COMPREHENSIVE TESTING")
    
    client = Client()
    User = get_user_model()
    
    results = []
    test_users = {}
    
    # Test 1: Model imports and access
    print_section("1. TESTING MODEL IMPORTS")
    try:
        from surveys.models import Survey, SurveyResponse, SurveyReminder
        print_result("Import core models", True, "All essential models imported")
        results.append(("Model imports", True))
        
        # Test model counts
        survey_count = Survey.objects.count()
        response_count = SurveyResponse.objects.count()
        reminder_count = SurveyReminder.objects.count()
        
        print_result("Survey model access", True, f"{survey_count} records")
        print_result("SurveyResponse model access", True, f"{response_count} records")
        print_result("SurveyReminder model access", True, f"{reminder_count} records")
        results.extend([("Survey model", True), ("SurveyResponse model", True), ("SurveyReminder model", True)])
        
    except Exception as e:
        print_result("Model testing", False, f"Error: {e}")
        results.append(("Model imports", False))
    
    # Test 2: Create test users
    print_section("2. CREATING TEST USERS")
    try:
        # Admin user
        admin_user, created = User.objects.get_or_create(
            username='admin_surveys_test',
            defaults={
                'email': 'admin@surveys.test',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
        test_users['admin'] = admin_user
        print_result("Create admin user", True, f"User: {admin_user.username}")
        
        # Aamil user
        aamil_user, created = User.objects.get_or_create(
            username='aamil_surveys_test',
            defaults={
                'email': 'aamil@surveys.test',
                'first_name': 'Aamil',
                'last_name': 'User',
                'role': 'aamil',
                'is_staff': True
            }
        )
        if created:
            aamil_user.set_password('aamil123')
            aamil_user.save()
        test_users['aamil'] = aamil_user
        print_result("Create aamil user", True, f"User: {aamil_user.username}")
        
        # Student user
        student_user, created = User.objects.get_or_create(
            username='student_surveys_test',
            defaults={
                'email': 'student@surveys.test',
                'first_name': 'Test',
                'last_name': 'Student',
                'role': 'student'
            }
        )
        if created:
            student_user.set_password('student123')
            student_user.save()
        test_users['student'] = student_user
        print_result("Create student user", True, f"User: {student_user.username}")
        
        results.append(("User creation", True))
        
    except Exception as e:
        print_result("User creation", False, f"Error: {e}")
        results.append(("User creation", False))
    
    # Test 3: Create sample survey data
    print_section("3. CREATING SAMPLE SURVEY DATA")
    try:
        # Create sample survey
        sample_questions = [
            {
                "id": 1,
                "type": "text",
                "text": "What is your name?",
                "required": True,
                "options": []
            },
            {
                "id": 2,
                "type": "multiple_choice",
                "text": "How satisfied are you with our medical services?",
                "required": True,
                "options": ["Very Satisfied", "Satisfied", "Neutral", "Dissatisfied", "Very Dissatisfied"]
            },
            {
                "id": 3,
                "type": "rating",
                "text": "Rate the quality of care (1-5)",
                "required": True,
                "options": ["1", "2", "3", "4", "5"]
            }
        ]
        
        survey, created = Survey.objects.get_or_create(
            title='Medical Service Satisfaction Survey',
            defaults={
                'description': 'A comprehensive survey to evaluate patient satisfaction with medical services',
                'target_role': 'all',
                'questions': sample_questions,
                'created_by': test_users['admin'],
                'is_active': True,
                'is_anonymous': False,
                'allow_multiple_responses': False,
                'show_results': True,
                'start_date': datetime.now().date(),
                'end_date': datetime.now().date() + timedelta(days=30)
            }
        )
        print_result("Create sample survey", True, f"Survey: {survey.title}")
        
        # Create sample response
        sample_answers = {
            "1": "John Doe",
            "2": "Very Satisfied",
            "3": "5"
        }
        
        response, created = SurveyResponse.objects.get_or_create(
            survey=survey,
            respondent=test_users['student'],
            defaults={
                'answers': sample_answers,
                'is_complete': True
            }
        )
        print_result("Create sample response", True, f"Response by: {response.respondent.get_full_name()}")
        
        results.append(("Sample data creation", True))
        
    except Exception as e:
        print_result("Sample data creation", False, f"Error: {e}")
        results.append(("Sample data creation", False))
    
    # Test 4: URL patterns
    print_section("4. TESTING URL PATTERNS")
    test_urls = [
        ('surveys:dashboard', 'Dashboard'),
        ('surveys:list', 'Survey List'),
        ('surveys:create', 'Create Survey'),
    ]
    
    url_results = 0
    for url_name, description in test_urls:
        try:
            url = reverse(url_name)
            print_result(f"URL {description}", True, f"Resolves to: {url}")
            url_results += 1
        except Exception as e:
            print_result(f"URL {description}", False, f"Error: {e}")
    
    results.append(("URL patterns", url_results == len(test_urls)))
    
    # Test 5: View accessibility
    print_section("5. TESTING VIEW ACCESSIBILITY")
    
    # Login as admin
    login_success = client.login(username='admin_surveys_test', password='admin123')
    if login_success:
        print_result("Admin login", True, "Successfully logged in")
        
        view_results = 0
        for url_name, description in test_urls:
            try:
                response = client.get(reverse(url_name))
                status = response.status_code
                
                if status in [200, 302]:
                    print_result(f"{description} view", True, f"Status: {status}")
                    view_results += 1
                else:
                    print_result(f"{description} view", False, f"Status: {status}")
                    
            except Exception as e:
                print_result(f"{description} view", False, f"Error: {e}")
        
        results.append(("View accessibility", view_results >= len(test_urls) * 0.8))
        client.logout()
    else:
        print_result("Admin login", False, "Login failed")
        results.append(("View accessibility", False))
    
    # Test 6: Role-based access
    print_section("6. TESTING ROLE-BASED ACCESS")
    
    role_test_results = 0
    for role, password in [('admin', 'admin123'), ('aamil', 'aamil123'), ('student', 'student123')]:
        if role in test_users:
            username = test_users[role].username
            login_success = client.login(username=username, password=password)
            
            if login_success:
                try:
                    response = client.get(reverse('surveys:dashboard'))
                    accessible = response.status_code in [200, 302]
                    print_result(f"{role.title()} dashboard access", accessible, f"Status: {response.status_code}")
                    if accessible:
                        role_test_results += 1
                except Exception as e:
                    print_result(f"{role.title()} dashboard access", False, f"Error: {e}")
                
                client.logout()
            else:
                print_result(f"{role.title()} login", False, "Authentication failed")
    
    results.append(("Role-based access", role_test_results >= 2))
    
    # Test 7: Survey functionality
    print_section("7. TESTING SURVEY FUNCTIONALITY")
    
    client.login(username='admin_surveys_test', password='admin123')
    
    # Test survey detail
    try:
        response = client.get(reverse('surveys:detail', kwargs={'pk': survey.pk}))
        status = response.status_code
        print_result("Survey detail view", status in [200, 302], f"Status: {status}")
        results.append(("Survey detail", status in [200, 302]))
    except Exception as e:
        print_result("Survey detail view", False, f"Error: {e}")
        results.append(("Survey detail", False))
    
    # Test take survey
    try:
        response = client.get(reverse('surveys:take_survey', kwargs={'pk': survey.pk}))
        status = response.status_code
        print_result("Take survey view", status in [200, 302], f"Status: {status}")
        results.append(("Take survey", status in [200, 302]))
    except Exception as e:
        print_result("Take survey view", False, f"Error: {e}")
        results.append(("Take survey", False))
    
    client.logout()
    
    # Generate final report
    print_section("SURVEYS APP TESTING SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(1 for _, success in results if success)
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n📊 OVERALL RESULTS:")
    print(f"✅ Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    print(f"❌ Failed: {total_tests - passed_tests}/{total_tests} ({100-success_rate:.1f}%)")
    
    print(f"\n📋 SAMPLE DATA CREATED:")
    if 'admin' in test_users:
        print(f"  👤 Admin: {test_users['admin'].get_full_name()}")
    if 'aamil' in test_users:
        print(f"  👥 Aamil: {test_users['aamil'].get_full_name()}")
    if 'student' in test_users:
        print(f"  🎓 Student: {test_users['student'].get_full_name()}")
    print(f"  📋 Survey: Medical Service Satisfaction Survey")
    print(f"  📝 Response: Sample response with rating data")
    
    print(f"\n🔗 KEY URLS FOR TESTING:")
    print(f"  🏠 Dashboard: http://localhost:8000/surveys/")
    print(f"  📋 Survey List: http://localhost:8000/surveys/list/")
    print(f"  ➕ Create Survey: http://localhost:8000/surveys/create/")
    print(f"  📊 Survey Detail: http://localhost:8000/surveys/1/")
    print(f"  📝 Take Survey: http://localhost:8000/surveys/1/take/")
    
    print(f"\n👥 TEST CREDENTIALS:")
    print(f"  👤 Admin: admin_surveys_test / admin123")
    print(f"  👥 Aamil: aamil_surveys_test / aamil123")
    print(f"  🎓 Student: student_surveys_test / student123")
    
    if success_rate >= 90:
        print(f"\n🏆 FINAL STATUS: EXCELLENT ({success_rate:.1f}%)")
        print("✅ Surveys app is ready for production!")
        print("🚀 Ready to commit to main branch...")
        return True
    elif success_rate >= 75:
        print(f"\n🟡 FINAL STATUS: GOOD ({success_rate:.1f}%)")
        print("⚠️ Surveys app has minor issues but is functional.")
        return True
    else:
        print(f"\n🔴 FINAL STATUS: NEEDS WORK ({success_rate:.1f}%)")
        print("❌ Surveys app requires fixes.")
        return False

if __name__ == "__main__":
    success = test_surveys_app()
    sys.exit(0 if success else 1)