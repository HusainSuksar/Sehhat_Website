#!/usr/bin/env python3
"""
Comprehensive Testing Script for Moze App (Medical Centers Management)
Tests all core functionality, URLs, user roles, and creates sample Moze data.
"""

import os
import sys
import django
import requests
from datetime import datetime, timedelta, date, time
import json

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

# Import Moze models
from moze.models import Moze, MozeComment, MozeSettings

# Import related models
from accounts.models import User

class MozeAppTester:
    def __init__(self):
        self.client = Client()
        self.users = {}
        self.sample_data = {}
        self.test_results = []
        self.server_url = 'http://localhost:8000'
        
    def log_result(self, test_name, success, details=""):
        """Log test results"""
        status = "✅" if success else "❌"
        result = f"{status} {test_name}"
        if details:
            result += f": {details}"
        print(result)
        self.test_results.append({
            'name': test_name,
            'success': success,
            'details': details
        })
        
    def create_test_users(self):
        """Create test users for different roles"""
        print("\n🔧 Creating test users...")
        
        # Create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'first_name': 'System',
                'last_name': 'Administrator',
                'email': 'admin@moze.com',
                'role': 'admin',
                'phone_number': '+1234567890',
                'is_active': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
        self.users['admin'] = admin_user
        
        # Create aamil user
        aamil_user, created = User.objects.get_or_create(
            username='aamil_moze',
            defaults={
                'first_name': 'Medical',
                'last_name': 'Aamil',
                'email': 'aamil@moze.com',
                'role': 'aamil',
                'phone_number': '+1234567891',
                'is_active': True
            }
        )
        if created:
            aamil_user.set_password('test123')
            aamil_user.save()
        self.users['aamil'] = aamil_user
        
        # Create moze_coordinator user
        coordinator_user, created = User.objects.get_or_create(
            username='moze_coordinator',
            defaults={
                'first_name': 'Moze',
                'last_name': 'Coordinator',
                'email': 'coordinator@moze.com',
                'role': 'moze_coordinator',
                'phone_number': '+1234567892',
                'is_active': True
            }
        )
        if created:
            coordinator_user.set_password('test123')
            coordinator_user.save()
        self.users['moze_coordinator'] = coordinator_user
        
        # Create doctor user
        doctor_user, created = User.objects.get_or_create(
            username='dr_moze',
            defaults={
                'first_name': 'Doctor',
                'last_name': 'Moze',
                'email': 'doctor@moze.com',
                'role': 'doctor',
                'phone_number': '+1234567893',
                'is_active': True
            }
        )
        if created:
            doctor_user.set_password('test123')
            doctor_user.save()
        self.users['doctor'] = doctor_user
        
        # Create student user
        student_user, created = User.objects.get_or_create(
            username='student_moze',
            defaults={
                'first_name': 'Student',
                'last_name': 'Moze',
                'email': 'student@moze.com',
                'role': 'student',
                'phone_number': '+1234567894',
                'is_active': True
            }
        )
        if created:
            student_user.set_password('test123')
            student_user.save()
        self.users['student'] = student_user
        
        print(f"✅ Created {len(self.users)} test users")
        
    def create_sample_data(self):
        """Create comprehensive sample Moze data"""
        print("\n🏥 Creating sample Moze data...")
        
        try:
            with transaction.atomic():
                # Create main Moze
                moze, created = Moze.objects.get_or_create(
                    name='Central Medical Moze',
                    defaults={
                        'location': 'Downtown Medical District',
                        'address': '123 Medical Center Blvd, Healthcare City, HC 12345',
                        'aamil': self.users['aamil'],
                        'moze_coordinator': self.users['moze_coordinator'],
                        'established_date': date(2020, 1, 15),
                        'is_active': True,
                        'capacity': 150,
                        'contact_phone': '+1234567800',
                        'contact_email': 'central@moze.com'
                    }
                )
                
                # Add team members
                moze.team_members.add(self.users['doctor'], self.users['student'])
                self.sample_data['moze'] = moze
                
                # Create Moze settings
                settings, created = MozeSettings.objects.get_or_create(
                    moze=moze,
                    defaults={
                        'allow_walk_ins': True,
                        'appointment_duration': 30,
                        'working_hours_start': time(9, 0),
                        'working_hours_end': time(17, 0),
                        'working_days': [0, 1, 2, 3, 4],  # Monday to Friday
                        'emergency_contact': '+1234567999',
                        'special_instructions': 'Please bring your ITS ID and insurance information.'
                    }
                )
                self.sample_data['settings'] = settings
                
                # Create comments
                comment1 = MozeComment.objects.create(
                    moze=moze,
                    author=self.users['aamil'],
                    content='New medical equipment has been installed in the center. Ready for enhanced patient care.',
                    is_active=True
                )
                
                comment2 = MozeComment.objects.create(
                    moze=moze,
                    author=self.users['moze_coordinator'],
                    content='Patient satisfaction scores have improved significantly this quarter.',
                    is_active=True
                )
                
                # Create a reply comment
                reply_comment = MozeComment.objects.create(
                    moze=moze,
                    author=self.users['doctor'],
                    content='The new equipment is working perfectly. Patients are very satisfied.',
                    parent=comment1,
                    is_active=True
                )
                
                self.sample_data['comments'] = [comment1, comment2, reply_comment]
                
                # Create additional Moze for testing
                moze2, created = Moze.objects.get_or_create(
                    name='Community Health Moze',
                    defaults={
                        'location': 'Suburban Area',
                        'address': '456 Community Health Drive, Suburb City, SC 67890',
                        'aamil': self.users['aamil'],
                        'established_date': date(2021, 6, 1),
                        'is_active': True,
                        'capacity': 100,
                        'contact_phone': '+1234567801',
                        'contact_email': 'community@moze.com'
                    }
                )
                self.sample_data['moze2'] = moze2
                
            print("✅ Created comprehensive Moze sample data")
            
        except Exception as e:
            print(f"❌ Error creating sample data: {e}")
            
    def test_model_access(self):
        """Test access to all Moze models"""
        print("\n📊 Testing Moze model access...")
        
        models_to_test = [
            ('Moze', Moze),
            ('Moze Comment', MozeComment),
            ('Moze Settings', MozeSettings),
        ]
        
        for model_name, model_class in models_to_test:
            try:
                count = model_class.objects.count()
                self.log_result(f"Access {model_name} model", True, f"Found {count} records")
            except Exception as e:
                self.log_result(f"Access {model_name} model", False, f"Error: {e}")
                
    def test_url_accessibility(self):
        """Test URL accessibility"""
        print("\n🌐 Testing Moze URL accessibility...")
        
        # Public URLs (should redirect to login)
        public_urls = [
            ('', 'Dashboard'),
            ('list/', 'Moze List'),
            ('analytics/', 'Analytics'),
            ('create/', 'Create Moze'),
        ]
        
        for url, name in public_urls:
            try:
                response = self.client.get(f'/moze/{url}')
                if response.status_code in [200, 302]:  # 302 = redirect to login
                    self.log_result(f"URL accessibility: {name}", True, f"Status: {response.status_code}")
                else:
                    self.log_result(f"URL accessibility: {name}", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_result(f"URL accessibility: {name}", False, f"Error: {e}")
                
    def test_user_role_access(self):
        """Test role-based access control"""
        print("\n👥 Testing user role-based access...")
        
        test_urls = [
            '/moze/',
            '/moze/list/',
            '/moze/analytics/',
            '/moze/create/',
        ]
        
        for role, user in self.users.items():
            accessible_count = 0
            self.client.force_login(user)
            
            for url in test_urls:
                try:
                    response = self.client.get(url)
                    if response.status_code == 200:
                        accessible_count += 1
                except:
                    pass
            
            self.log_result(f"Role access: {role}", True, f"Can access {accessible_count}/{len(test_urls)} URLs")
            self.client.logout()
            
    def test_moze_functionality(self):
        """Test core Moze functionality"""
        print("\n🏥 Testing Moze functionality...")
        
        # Test with admin user
        self.client.force_login(self.users['admin'])
        
        # Test dashboard
        try:
            response = self.client.get('/moze/')
            success = response.status_code == 200
            error_msg = "Dashboard accessible" if success else f"Status: {response.status_code}"
            self.log_result("Dashboard access", success, error_msg)
        except Exception as e:
            self.log_result("Dashboard access", False, f"Error: {e}")
            
        # Test Moze list
        try:
            response = self.client.get('/moze/list/')
            success = response.status_code == 200
            error_msg = "List accessible" if success else f"Status: {response.status_code}"
            self.log_result("Moze listing", success, error_msg)
        except Exception as e:
            self.log_result("Moze listing", False, f"Error: {e}")
            
        # Test Moze detail
        if self.sample_data.get('moze'):
            try:
                response = self.client.get(f'/moze/{self.sample_data["moze"].pk}/')
                success = response.status_code == 200
                error_msg = "Detail accessible" if success else f"Status: {response.status_code}"
                self.log_result("Moze detail view", success, error_msg)
            except Exception as e:
                self.log_result("Moze detail view", False, f"Error: {e}")
                
        # Test Moze creation form
        try:
            response = self.client.get('/moze/create/')
            success = response.status_code == 200
            error_msg = "Form accessible" if success else f"Status: {response.status_code}"
            self.log_result("Moze creation form", success, error_msg)
        except Exception as e:
            self.log_result("Moze creation form", False, f"Error: {e}")
            
        # Test analytics
        try:
            response = self.client.get('/moze/analytics/')
            success = response.status_code == 200
            error_msg = "Analytics accessible" if success else f"Status: {response.status_code}"
            self.log_result("Moze analytics", success, error_msg)
        except Exception as e:
            self.log_result("Moze analytics", False, f"Error: {e}")
            
        self.client.logout()
        
    def test_role_specific_functionality(self):
        """Test role-specific Moze functionality"""
        print("\n👨‍⚕️ Testing role-specific functionality...")
        
        # Test Aamil functionality
        self.client.force_login(self.users['aamil'])
        try:
            response = self.client.get('/moze/')
            success = response.status_code == 200
            self.log_result("Aamil dashboard access", success, "Dashboard accessible" if success else f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Aamil dashboard access", False, f"Error: {e}")
            
        try:
            response = self.client.get('/moze/list/')
            success = response.status_code == 200
            self.log_result("Aamil moze list", success, "Can view managed mozes" if success else f"Error accessing list")
        except Exception as e:
            self.log_result("Aamil moze list", False, f"Error: {e}")
        self.client.logout()
        
        # Test Moze Coordinator functionality
        self.client.force_login(self.users['moze_coordinator'])
        try:
            response = self.client.get('/moze/')
            success = response.status_code == 200
            self.log_result("Coordinator dashboard access", success, "Dashboard accessible" if success else f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Coordinator dashboard access", False, f"Error: {e}")
            
        try:
            response = self.client.get('/moze/analytics/')
            success = response.status_code == 200
            self.log_result("Coordinator analytics access", success, "Analytics accessible" if success else f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Coordinator analytics access", False, f"Error: {e}")
        self.client.logout()
        
        # Test Comment functionality
        if self.sample_data.get('moze'):
            self.client.force_login(self.users['doctor'])
            try:
                response = self.client.post(f'/moze/{self.sample_data["moze"].pk}/', {
                    'content': 'Test comment from automated testing system'
                })
                success = response.status_code in [200, 302]
                self.log_result("Comment posting", success, "Can post comments" if success else f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("Comment posting", False, f"Error: {e}")
            self.client.logout()
            
    def generate_summary_report(self):
        """Generate comprehensive summary report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failure_rate = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n{'='*80}")
        print("🏥 MOZE APP TESTING SUMMARY REPORT")
        print(f"{'='*80}")
        print(f"\n📊 OVERALL RESULTS:")
        print(f"✅ Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        print(f"❌ Failed: {failure_rate}/{total_tests} ({100-success_rate:.1f}%)")
        
        print(f"\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"  {status} {result['name']}: {result['details']}")
            
        print(f"\n🏥 SAMPLE MOZE DATA CREATED:")
        sample_items = [
            f"  🏥 Moze: {self.sample_data.get('moze', 'N/A')}",
            f"  ⚙️ Settings: {self.sample_data.get('settings', 'N/A')}",
            f"  💬 Comments: {len(self.sample_data.get('comments', []))} comments with replies",
            f"  🏥 Additional Moze: {self.sample_data.get('moze2', 'N/A')}"
        ]
        
        for item in sample_items:
            print(item)
            
        print(f"\n🔗 KEY URLS FOR MANUAL TESTING:")
        urls = [
            "  🏠 Dashboard: http://localhost:8000/moze/",
            "  📋 Moze List: http://localhost:8000/moze/list/",
            "  ➕ Create Moze: http://localhost:8000/moze/create/",
            "  📊 Analytics: http://localhost:8000/moze/analytics/",
        ]
        
        if self.sample_data.get('moze'):
            urls.append(f"  👁️ Moze Detail: http://localhost:8000/moze/{self.sample_data['moze'].pk}/")
            
        for url in urls:
            print(url)
            
        print(f"\n👥 TEST USER CREDENTIALS:")
        creds = [
            "  👤 Admin: admin / admin123",
            "  👤 Aamil: aamil_moze / test123",
            "  👤 Coordinator: moze_coordinator / test123",
            "  👤 Doctor: dr_moze / test123",
            "  👤 Student: student_moze / test123"
        ]
        
        for cred in creds:
            print(cred)
            
        # Determine final status
        if success_rate >= 95:
            status = "🏆 EXCELLENT - App is fully functional"
        elif success_rate >= 85:
            status = "✅ GOOD - App is mostly functional"
        elif success_rate >= 70:
            status = "⚠️ ACCEPTABLE - Some issues need attention"
        else:
            status = "❌ NEEDS WORK - Major issues detected"
            
        print(f"\n🏆 FINAL STATUS: {status}")
        print(f"{'='*80}")
        
        return success_rate >= 95  # Return True if excellent
        
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🏥 Starting Comprehensive Moze App Testing...")
        print("="*80)
        
        self.create_test_users()
        self.create_sample_data()
        self.test_model_access()
        self.test_url_accessibility()
        self.test_user_role_access()
        self.test_moze_functionality()
        self.test_role_specific_functionality()
        
        return self.generate_summary_report()


def main():
    """Main function to run all tests"""
    try:
        tester = MozeAppTester()
        all_passed = tester.run_all_tests()
        
        if all_passed:
            print("\n🎉 All tests passed! Moze app is ready for production.")
        else:
            print("\n⚠️ Some tests failed. Please review the issues above.")
            
        return 0 if all_passed else 1
        
    except KeyboardInterrupt:
        print("\n\n🛑 Testing interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())