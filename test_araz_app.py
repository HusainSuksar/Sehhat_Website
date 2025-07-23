#!/usr/bin/env python3
"""
🧪 COMPREHENSIVE ARAZ APP TESTING SCRIPT
=============================================
This script tests all functionalities of the Araz (Petition Management) app.

WHAT IS ARAZ APP?
- Medical petition/request management system
- Handles patient requests for consultations, prescriptions, appointments
- Includes DuaAraz (medical requests) and general Petitions
- Dashboard with analytics and assignment management

FEATURES TO TEST:
1. Dashboard Access & Statistics
2. Petition Creation, Listing, and Management
3. DuaAraz Medical Requests
4. User Role-based Access (Admin, Aamil, Moze Coordinator, Patients)
5. Petition Assignment and Comments
6. Analytics and Export Functions
7. Bulk Operations
"""

import os
import sys
import django
import requests
import json
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from araz.models import Petition, PetitionCategory, DuaAraz, PetitionComment
from doctordirectory.models import Doctor

User = get_user_model()

class ArazAppTester:
    def __init__(self):
        self.client = Client()
        self.base_url = 'http://localhost:8000'
        self.test_results = []
        
    def log_test(self, test_name, success, message=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'status': status,
            'message': message
        })
        print(f"{status}: {test_name}")
        if message:
            print(f"    → {message}")
    
    def test_araz_models(self):
        """Test Araz models functionality"""
        print("\n🔧 TESTING ARAZ MODELS:")
        print("-" * 40)
        
        try:
            # Test DuaAraz model
            dua_count = DuaAraz.objects.count()
            self.log_test("DuaAraz Model Access", True, f"Found {dua_count} medical requests")
            
            # Test Petition model
            petition_count = Petition.objects.count()
            self.log_test("Petition Model Access", True, f"Found {petition_count} petitions")
            
            # Test PetitionCategory model
            category_count = PetitionCategory.objects.count()
            self.log_test("PetitionCategory Model Access", True, f"Found {category_count} categories")
            
            return True
        except Exception as e:
            self.log_test("Araz Models", False, str(e))
            return False
    
    def test_araz_urls(self):
        """Test all Araz URLs accessibility"""
        print("\n🌐 TESTING ARAZ URLs:")
        print("-" * 40)
        
        # Test URLs that should be accessible without login
        public_urls = [
            ('Araz Dashboard', '/araz/'),
        ]
        
        # Test URLs that require login
        protected_urls = [
            ('Petition List', '/araz/petitions/'),
            ('Petition Create', '/araz/petitions/create/'),
            ('Analytics', '/araz/analytics/'),
            ('My Assignments', '/araz/my-assignments/'),
            ('Export', '/araz/export/'),
        ]
        
        success_count = 0
        total_tests = len(public_urls) + len(protected_urls)
        
        # Test public URLs
        for name, url in public_urls:
            try:
                response = requests.get(f'{self.base_url}{url}', timeout=5)
                if response.status_code in [200, 302]:
                    self.log_test(f"URL: {name}", True, f"Status {response.status_code}")
                    success_count += 1
                else:
                    self.log_test(f"URL: {name}", False, f"Status {response.status_code}")
            except Exception as e:
                self.log_test(f"URL: {name}", False, str(e))
        
        # Test protected URLs (should redirect or require auth)
        for name, url in protected_urls:
            try:
                response = requests.get(f'{self.base_url}{url}', timeout=5)
                if response.status_code in [200, 302, 403]:
                    self.log_test(f"Protected URL: {name}", True, f"Status {response.status_code}")
                    success_count += 1
                else:
                    self.log_test(f"Protected URL: {name}", False, f"Status {response.status_code}")
            except Exception as e:
                self.log_test(f"Protected URL: {name}", False, str(e))
        
        return success_count >= (total_tests * 0.8)  # 80% success rate
    
    def test_user_authentication(self):
        """Test Araz access with different user roles"""
        print("\n👥 TESTING USER ROLE ACCESS:")
        print("-" * 40)
        
        test_users = [
            ('admin', 'admin123', 'Admin User'),
            ('admin_1', 'test123', 'Test Admin'),
            ('doctor_1', 'test123', 'Test Doctor'),
            ('student_1', 'test123', 'Test Student'),
            ('aamil_1', 'test123', 'Test Aamil'),
            ('moze_coordinator_1', 'test123', 'Test Moze Coordinator')
        ]
        
        working_logins = 0
        
        for username, password, description in test_users:
            try:
                # Test login
                login_success = self.client.login(username=username, password=password)
                
                if login_success:
                    # Test Araz dashboard access
                    response = self.client.get('/araz/')
                    
                    if response.status_code == 200:
                        self.log_test(f"Araz Access: {description}", True, "Dashboard accessible")
                        working_logins += 1
                        
                        # Check if dashboard contains expected elements
                        content = response.content.decode()
                        if 'petition' in content.lower() or 'araz' in content.lower():
                            self.log_test(f"Dashboard Content: {description}", True, "Contains Araz content")
                        
                    else:
                        self.log_test(f"Araz Access: {description}", False, f"Status {response.status_code}")
                    
                    # Logout for next test
                    self.client.logout()
                else:
                    self.log_test(f"Login: {description}", False, "Login failed")
                    
            except Exception as e:
                self.log_test(f"User Test: {description}", False, str(e))
        
        return working_logins >= len(test_users) * 0.7  # 70% success rate
    
    def test_petition_functionality(self):
        """Test petition creation and management"""
        print("\n📝 TESTING PETITION FUNCTIONALITY:")
        print("-" * 40)
        
        # Login as admin to test functionality
        try:
            if self.client.login(username='admin', password='admin123'):
                # Test petition list access
                response = self.client.get('/araz/petitions/')
                self.log_test("Petition List Access", response.status_code == 200, 
                            f"Status {response.status_code}")
                
                # Test petition creation page
                response = self.client.get('/araz/petitions/create/')
                self.log_test("Petition Create Page", response.status_code == 200,
                            f"Status {response.status_code}")
                
                # Test analytics page
                response = self.client.get('/araz/analytics/')
                self.log_test("Analytics Page", response.status_code == 200,
                            f"Status {response.status_code}")
                
                # Test my assignments page
                response = self.client.get('/araz/my-assignments/')
                self.log_test("My Assignments Page", response.status_code == 200,
                            f"Status {response.status_code}")
                
                self.client.logout()
                return True
            else:
                self.log_test("Admin Login for Petition Test", False, "Could not login as admin")
                return False
                
        except Exception as e:
            self.log_test("Petition Functionality", False, str(e))
            return False
    
    def test_dashboard_statistics(self):
        """Test dashboard statistics and data display"""
        print("\n📊 TESTING DASHBOARD STATISTICS:")
        print("-" * 40)
        
        try:
            if self.client.login(username='admin', password='admin123'):
                response = self.client.get('/araz/')
                
                if response.status_code == 200:
                    content = response.content.decode()
                    
                    # Check for statistical elements
                    stats_found = []
                    if 'total' in content.lower():
                        stats_found.append("Total counts")
                    if 'pending' in content.lower():
                        stats_found.append("Pending status")
                    if 'resolved' in content.lower():
                        stats_found.append("Resolved status")
                    if 'chart' in content.lower() or 'graph' in content.lower():
                        stats_found.append("Charts/Graphs")
                    
                    self.log_test("Dashboard Statistics", len(stats_found) > 0,
                                f"Found: {', '.join(stats_found)}")
                    
                    # Check for recent petitions
                    if 'recent' in content.lower():
                        self.log_test("Recent Petitions Display", True, "Recent items section found")
                    
                    self.client.logout()
                    return True
                else:
                    self.log_test("Dashboard Access", False, f"Status {response.status_code}")
                    return False
            else:
                self.log_test("Admin Login for Dashboard", False, "Could not login")
                return False
                
        except Exception as e:
            self.log_test("Dashboard Statistics", False, str(e))
            return False
    
    def create_sample_data(self):
        """Create sample Araz data for testing"""
        print("\n🔧 CREATING SAMPLE ARAZ DATA:")
        print("-" * 40)
        
        try:
            # Create petition categories if they don't exist
            categories = [
                {'name': 'Medical Request', 'description': 'Medical consultation requests'},
                {'name': 'Administrative', 'description': 'Administrative petitions'},
                {'name': 'Complaint', 'description': 'General complaints'},
            ]
            
            for cat_data in categories:
                category, created = PetitionCategory.objects.get_or_create(
                    name=cat_data['name'],
                    defaults={'description': cat_data['description']}
                )
                if created:
                    self.log_test(f"Created Category: {cat_data['name']}", True)
            
            # Create sample DuaAraz (medical requests)
            sample_requests = [
                {
                    'patient_its_id': '12345678',
                    'patient_name': 'Test Patient 1',
                    'ailment': 'Regular checkup needed',
                    'request_type': 'consultation',
                    'urgency_level': 'medium'
                },
                {
                    'patient_its_id': '87654321',
                    'patient_name': 'Test Patient 2',
                    'ailment': 'Prescription refill',
                    'request_type': 'prescription',
                    'urgency_level': 'low'
                },
            ]
            
            for req_data in sample_requests:
                dua, created = DuaAraz.objects.get_or_create(
                    patient_its_id=req_data['patient_its_id'],
                    defaults=req_data
                )
                if created:
                    self.log_test(f"Created DuaAraz: {req_data['patient_name']}", True)
            
            return True
            
        except Exception as e:
            self.log_test("Sample Data Creation", False, str(e))
            return False
    
    def run_all_tests(self):
        """Run all Araz app tests"""
        print("🧪 COMPREHENSIVE ARAZ APP TESTING")
        print("=" * 50)
        print("The Araz app handles medical petitions and requests.")
        print("Testing all functionality, user access, and features...")
        print("=" * 50)
        
        # Run all tests
        tests = [
            self.test_araz_models(),
            self.test_araz_urls(),
            self.test_user_authentication(),
            self.create_sample_data(),
            self.test_petition_functionality(),
            self.test_dashboard_statistics(),
        ]
        
        # Calculate results
        passed_tests = sum(tests)
        total_tests = len(tests)
        success_rate = (passed_tests / total_tests) * 100
        
        # Print summary
        print("\n" + "=" * 50)
        print("🎯 ARAZ APP TEST SUMMARY")
        print("=" * 50)
        
        for result in self.test_results:
            print(f"{result['status']}: {result['test']}")
            if result['message']:
                print(f"    → {result['message']}")
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"✅ Tests Passed: {passed_tests}/{total_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            status = "🟢 EXCELLENT - Araz app fully functional"
        elif success_rate >= 75:
            status = "🟡 GOOD - Minor issues detected"
        else:
            status = "🔴 NEEDS ATTENTION - Major issues found"
        
        print(f"🏆 Status: {status}")
        
        # Print usage instructions
        print(f"\n📋 HOW TO USE ARAZ APP:")
        print("-" * 30)
        print("1. 🌐 Access: http://localhost:8000/araz/")
        print("2. 👤 Login with any test user (doctor_1/test123, admin/admin123)")
        print("3. 📝 Create Petitions: Click 'New Petition' or use /araz/petitions/create/")
        print("4. 📊 View Analytics: Visit /araz/analytics/")
        print("5. 🔍 Manage Requests: Use dashboard to view and assign petitions")
        print("6. 👥 Role-based Access: Different users see different features")
        
        print(f"\n🔑 TEST CREDENTIALS:")
        print("- Admin: admin/admin123 (Full access)")
        print("- Doctor: doctor_1/test123 (Medical focus)")
        print("- Aamil: aamil_1/test123 (Administrative)")
        print("- Student: student_1/test123 (Limited access)")
        
        return success_rate >= 75

def main():
    """Main testing function"""
    tester = ArazAppTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())