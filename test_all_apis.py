#!/usr/bin/env python3
"""
Quick API Testing Script for Umoor Sehhat
Run this script to test all major API endpoints
"""

import requests
import json
import sys
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "username": "admin",
    "password": "admin123"  # Change this to your admin password
}

class APITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.token = None
        self.session = requests.Session()
        
    def authenticate(self):
        """Get JWT token for authentication"""
        url = f"{self.base_url}/api/accounts/auth/login/"
        response = self.session.post(url, json=TEST_USER)
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get('access')
            self.session.headers.update({
                'Authorization': f'Bearer {self.token}'
            })
            print("✅ Authentication successful")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    def test_endpoint(self, method, endpoint, data=None, files=None, expected_status=200):
        """Test a single API endpoint"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url)
            elif method.upper() == 'POST':
                if files:
                    response = self.session.post(url, data=data, files=files)
                else:
                    response = self.session.post(url, json=data)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url)
            else:
                print(f"❌ Unsupported method: {method}")
                return False
            
            if response.status_code == expected_status:
                print(f"✅ {method} {endpoint} - Status: {response.status_code}")
                return True
            else:
                print(f"⚠️  {method} {endpoint} - Expected: {expected_status}, Got: {response.status_code}")
                if response.status_code >= 400:
                    print(f"   Error: {response.text[:200]}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {method} {endpoint} - Connection error: {str(e)}")
            return False
    
    def run_tests(self):
        """Run all API endpoint tests"""
        print(f"\n🧪 Starting API Tests at {datetime.now()}")
        print(f"Base URL: {self.base_url}")
        print("=" * 60)
        
        # Check if server is running
        try:
            response = requests.get(f"{self.base_url}/admin/", timeout=5)
            print("✅ Server is running")
        except requests.exceptions.RequestException:
            print("❌ Server is not running. Start with: python manage.py runserver")
            return False
        
        # Authenticate
        if not self.authenticate():
            return False
        
        print("\n📋 Testing API Endpoints...")
        
        # Test results counter
        passed = 0
        total = 0
        
        # Define test cases
        test_cases = [
            # Accounts API
            ("GET", "/api/accounts/profile/me/", None, 200),
            ("GET", "/api/accounts/users/", None, 200),
            ("GET", "/api/accounts/stats/", None, 200),
            
            # Araz API
            ("GET", "/api/araz/dashboard/", None, 200),
            ("GET", "/api/araz/petitions/", None, 200),
            ("GET", "/api/araz/categories/", None, 200),
            
            # DoctorDirectory API
            ("GET", "/api/doctordirectory/dashboard/", None, 200),
            ("GET", "/api/doctordirectory/doctors/", None, 200),
            ("GET", "/api/doctordirectory/specializations/", None, 200),
            
            # MahalShifa API
            ("GET", "/api/mahalshifa/dashboard/", None, 200),
            ("GET", "/api/mahalshifa/appointments/", None, 200),
            ("GET", "/api/mahalshifa/medical-records/", None, 200),
            
            # Students API
            ("GET", "/api/students/dashboard/", None, 200),
            ("GET", "/api/students/courses/", None, 200),
            ("GET", "/api/students/enrollments/", None, 200),
            
            # Moze API
            ("GET", "/api/moze/dashboard/", None, 200),
            ("GET", "/api/moze/mozes/", None, 200),
            ("GET", "/api/moze/team-members/", None, 200),
            
            # Evaluation API
            ("GET", "/api/evaluation/dashboard/", None, 200),
            ("GET", "/api/evaluation/forms/", None, 200),
            ("GET", "/api/evaluation/criteria/", None, 200),
            
            # Surveys API
            ("GET", "/api/surveys/dashboard/", None, 200),
            ("GET", "/api/surveys/surveys/", None, 200),
            ("GET", "/api/surveys/analytics/", None, 200),
            
            # Photos API
            ("GET", "/api/photos/dashboard/", None, 200),
            ("GET", "/api/photos/photos/", None, 200),
            ("GET", "/api/photos/albums/", None, 200),
        ]
        
        # Run tests
        for method, endpoint, data, expected_status in test_cases:
            total += 1
            if self.test_endpoint(method, endpoint, data, expected_status=expected_status):
                passed += 1
            time.sleep(0.1)  # Small delay between requests
        
        # Summary
        print("\n" + "=" * 60)
        print(f"🎯 Test Results: {passed}/{total} passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 All tests passed! API is working correctly.")
        elif passed >= total * 0.8:
            print("✅ Most tests passed. API is mostly functional.")
        else:
            print("⚠️  Some tests failed. Check server logs for details.")
        
        return passed == total

def main():
    """Main function"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = BASE_URL
    
    tester = APITester(base_url)
    success = tester.run_tests()
    
    print(f"\n📖 For detailed testing instructions, see: API_TESTING_GUIDE_MACOS.md")
    print(f"🔧 To run unit tests: python manage.py test --verbosity=2")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()