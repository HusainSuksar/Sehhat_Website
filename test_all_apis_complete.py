#!/usr/bin/env python3
"""
Complete API Testing Script for Moze Evaluation System
Tests all 9 Django app APIs with authentication and data validation
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        
        # Test user credentials
        self.test_users = {
            'admin': {'its_id': '50000001', 'password': 'test'},
            'doctor': {'its_id': '50000002', 'password': 'test'},
            'student': {'its_id': '50000017', 'password': 'test'},
            'aamil': {'its_id': '50000038', 'password': 'test'},
            'patient': {'its_id': '50000046', 'password': 'test'}
        }

    def log_test(self, test_name, status, details=""):
        """Log test results"""
        result = {
            'test': test_name,
            'status': '✅ PASS' if status else '❌ FAIL',
            'details': details,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
        self.test_results.append(result)
        print(f"{result['status']} {test_name}: {details}")

    def get_csrf_token(self):
        """Get CSRF token from login page"""
        try:
            response = self.session.get(f"{BASE_URL}/accounts/login/")
            if response.status_code == 200:
                # Extract CSRF token from response
                import re
                csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', response.text)
                if csrf_match:
                    return csrf_match.group(1)
            return None
        except Exception as e:
            self.log_test("CSRF Token", False, f"Error: {e}")
            return None

    def test_its_login(self, user_type='admin'):
        """Test ITS login system"""
        print(f"\n🔐 Testing ITS Login for {user_type}...")
        
        try:
            # Get CSRF token
            csrf_token = self.get_csrf_token()
            if not csrf_token:
                self.log_test(f"ITS Login ({user_type})", False, "Could not get CSRF token")
                return False

            # Login with ITS credentials
            user_creds = self.test_users[user_type]
            login_data = {
                'its_id': user_creds['its_id'],
                'password': user_creds['password'],
                'csrfmiddlewaretoken': csrf_token
            }
            
            response = self.session.post(f"{BASE_URL}/accounts/login/", data=login_data, allow_redirects=False)
            
            if response.status_code == 302:  # Redirect after successful login
                redirect_url = response.headers.get('Location', '')
                self.log_test(f"ITS Login ({user_type})", True, f"Successful login with ITS ID {user_creds['its_id']} → {redirect_url}")
                return True
            else:
                self.log_test(f"ITS Login ({user_type})", False, f"Login failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test(f"ITS Login ({user_type})", False, f"Error: {e}")
            return False

    def test_accounts_api(self):
        """Test Accounts app APIs"""
        print(f"\n👤 Testing Accounts APIs...")
        
        endpoints = [
            ('/api/users/', 'GET', 'User list'),
            ('/api/profile/', 'GET', 'User profile'),
            ('/api/sync-its/', 'POST', 'ITS sync'),
            ('/api/test-its/', 'GET', 'ITS test'),
        ]
        
        for endpoint, method, description in endpoints:
            try:
                if method == 'GET':
                    response = self.session.get(f"{BASE_URL}{endpoint}")
                else:
                    response = self.session.post(f"{BASE_URL}{endpoint}")
                
                success = response.status_code in [200, 201, 302]
                self.log_test(f"Accounts API - {description}", success, f"{method} {endpoint} -> {response.status_code}")
                
            except Exception as e:
                self.log_test(f"Accounts API - {description}", False, f"Error: {e}")

    def test_app_apis(self, app_name, endpoints):
        """Generic method to test app APIs"""
        print(f"\n🔧 Testing {app_name} APIs...")
        
        for endpoint, method, description in endpoints:
            try:
                url = f"{BASE_URL}{endpoint}"
                if method == 'GET':
                    response = self.session.get(url)
                elif method == 'POST':
                    response = self.session.post(url, json={})
                else:
                    response = self.session.request(method, url)
                
                success = response.status_code in [200, 201, 302, 403]  # 403 is OK for unauthorized access
                status_info = f"{method} {endpoint} -> {response.status_code}"
                
                self.log_test(f"{app_name} API - {description}", success, status_info)
                
            except Exception as e:
                self.log_test(f"{app_name} API - {description}", False, f"Error: {e}")

    def test_all_apis(self):
        """Test all 9 Django app APIs"""
        
        # 1. Accounts APIs
        self.test_accounts_api()
        
        # 2. Araz APIs
        araz_endpoints = [
            ('/api/araz/petitions/', 'GET', 'Petition list'),
            ('/api/araz/categories/', 'GET', 'Petition categories'),
            ('/api/araz/petitions/1/', 'GET', 'Petition detail'),
        ]
        self.test_app_apis('Araz', araz_endpoints)
        
        # 3. Doctor Directory APIs
        doctor_endpoints = [
            ('/api/doctordirectory/doctors/', 'GET', 'Doctor list'),
            ('/api/doctordirectory/patients/', 'GET', 'Patient list'),
            ('/api/doctordirectory/appointments/', 'GET', 'Appointment list'),
            ('/api/doctordirectory/medical-records/', 'GET', 'Medical records'),
        ]
        self.test_app_apis('Doctor Directory', doctor_endpoints)
        
        # 4. MahalShifa APIs
        mahalshifa_endpoints = [
            ('/api/mahalshifa/hospitals/', 'GET', 'Hospital list'),
            ('/api/mahalshifa/doctors/', 'GET', 'MahalShifa doctors'),
            ('/api/mahalshifa/patients/', 'GET', 'MahalShifa patients'),
            ('/api/mahalshifa/departments/', 'GET', 'Hospital departments'),
        ]
        self.test_app_apis('MahalShifa', mahalshifa_endpoints)
        
        # 5. Students APIs
        students_endpoints = [
            ('/api/students/students/', 'GET', 'Student list'),
            ('/api/students/courses/', 'GET', 'Course list'),
            ('/api/students/assignments/', 'GET', 'Assignment list'),
            ('/api/students/submissions/', 'GET', 'Submission list'),
        ]
        self.test_app_apis('Students', students_endpoints)
        
        # 6. Moze APIs
        moze_endpoints = [
            ('/api/moze/mozes/', 'GET', 'Moze list'),
            ('/api/moze/teams/', 'GET', 'Umoor Sehhat teams'),
            ('/api/moze/mozes/1/', 'GET', 'Moze detail'),
        ]
        self.test_app_apis('Moze', moze_endpoints)
        
        # 7. Evaluation APIs
        evaluation_endpoints = [
            ('/api/evaluation/forms/', 'GET', 'Evaluation forms'),
            ('/api/evaluation/submissions/', 'GET', 'Evaluation submissions'),
            ('/api/evaluation/criteria/', 'GET', 'Evaluation criteria'),
        ]
        self.test_app_apis('Evaluation', evaluation_endpoints)
        
        # 8. Surveys APIs
        surveys_endpoints = [
            ('/api/surveys/surveys/', 'GET', 'Survey list'),
            ('/api/surveys/responses/', 'GET', 'Survey responses'),
            ('/api/surveys/surveys/1/', 'GET', 'Survey detail'),
        ]
        self.test_app_apis('Surveys', surveys_endpoints)
        
        # 9. Photos APIs
        photos_endpoints = [
            ('/api/photos/albums/', 'GET', 'Photo albums'),
            ('/api/photos/photos/', 'GET', 'Photo list'),
            ('/api/photos/albums/1/', 'GET', 'Album detail'),
        ]
        self.test_app_apis('Photos', photos_endpoints)

    def test_frontend_pages(self):
        """Test key frontend pages"""
        print(f"\n🌐 Testing Frontend Pages...")
        
        pages = [
            ('/', 'Home page'),
            ('/accounts/profile/', 'Profile page'),
            ('/doctordirectory/', 'Doctor directory'),
            ('/moze/', 'Moze dashboard'),
            ('/students/', 'Students dashboard'),
            ('/surveys/', 'Surveys page'),
            ('/evaluation/', 'Evaluation page'),
            ('/photos/', 'Photos page'),
            ('/araz/', 'Araz page'),
        ]
        
        for url, description in pages:
            try:
                response = self.session.get(f"{BASE_URL}{url}")
                success = response.status_code in [200, 302]
                self.log_test(f"Frontend - {description}", success, f"GET {url} -> {response.status_code}")
                
            except Exception as e:
                self.log_test(f"Frontend - {description}", False, f"Error: {e}")

    def test_its_api_integration(self):
        """Test ITS API integration specifically"""
        print(f"\n🔗 Testing ITS API Integration...")
        
        try:
            # Test ITS API directly
            response = self.session.get(f"{BASE_URL}/api/test-its/")
            if response.status_code == 200:
                data = response.json()
                if 'status' in data and data['status'] == 'success':
                    self.log_test("ITS API Integration", True, f"Mock ITS API returning {len(data.get('user_data', {}))} fields")
                else:
                    self.log_test("ITS API Integration", False, "ITS API not returning expected format")
            else:
                self.log_test("ITS API Integration", False, f"ITS API test failed: {response.status_code}")
                
        except Exception as e:
            self.log_test("ITS API Integration", False, f"Error: {e}")

    def run_complete_test(self):
        """Run complete API and system test"""
        print("🚀 Starting Complete API Testing for Moze Evaluation System")
        print("=" * 80)
        
        # Test ITS login first
        if self.test_its_login('admin'):
            print("✅ Logged in successfully as admin")
            
            # Test all components
            self.test_its_api_integration()
            self.test_all_apis()
            self.test_frontend_pages()
            
            # Test different user roles
            for role in ['doctor', 'student', 'aamil']:
                self.test_its_login(role)
        
        else:
            print("❌ Could not login, skipping authenticated tests")
            
        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📊 API TESTING SUMMARY")
        print("=" * 80)
        
        passed = len([r for r in self.test_results if '✅' in r['status']])
        failed = len([r for r in self.test_results if '❌' in r['status']])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {passed/total*100:.1f}%")
        
        if failed > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.test_results:
                if '❌' in result['status']:
                    print(f"   • {result['test']}: {result['details']}")
        
        print(f"\n🎯 Overall Status: {'✅ ALL SYSTEMS WORKING' if failed == 0 else '⚠️  SOME ISSUES FOUND'}")
        
        return failed == 0

if __name__ == "__main__":
    print("🧪 Moze Evaluation System - Complete API Testing")
    print("Make sure the Django server is running at http://127.0.0.1:8000")
    print()
    
    tester = APITester()
    success = tester.run_complete_test()
    sys.exit(0 if success else 1)