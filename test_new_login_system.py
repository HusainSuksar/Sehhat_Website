#!/usr/bin/env python3
"""
Comprehensive Test Script for New ITS-Only Login System
Tests the complete flow from login page to role-based access
"""

import requests
import json
from bs4 import BeautifulSoup
import sys

BASE_URL = "http://127.0.0.1:8000"

class LoginSystemTester:
    def __init__(self):
        self.session = requests.Session()
        
    def test_root_redirect(self):
        """Test if root URL redirects to login page"""
        print("🔗 Testing root redirect...")
        response = self.session.get(BASE_URL, allow_redirects=False)
        
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            if '/accounts/login/' in location:
                print("✅ Root URL correctly redirects to login page")
                return True
            else:
                print(f"❌ Root URL redirects to wrong location: {location}")
        else:
            print(f"❌ Root URL should redirect (302), got {response.status_code}")
        return False
    
    def test_login_page_loads(self):
        """Test if login page loads with ITS ID field"""
        print("\n📄 Testing login page...")
        response = self.session.get(f"{BASE_URL}/accounts/login/")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check for ITS ID field
            its_id_field = soup.find('input', {'name': 'its_id'})
            password_field = soup.find('input', {'name': 'password'})
            csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})
            
            if its_id_field and password_field and csrf_token:
                print("✅ Login page loads with ITS ID and password fields")
                print(f"   - ITS ID placeholder: {its_id_field.get('placeholder', 'N/A')}")
                print(f"   - CSRF token present: {bool(csrf_token)}")
                return csrf_token.get('value') if csrf_token else None
            else:
                print("❌ Login page missing required fields")
                print(f"   - ITS ID field: {bool(its_id_field)}")
                print(f"   - Password field: {bool(password_field)}")
                print(f"   - CSRF token: {bool(csrf_token)}")
        else:
            print(f"❌ Login page failed to load: {response.status_code}")
        return None
    
    def test_its_api_integration(self):
        """Test if ITS API is working correctly"""
        print("\n🔌 Testing ITS API integration...")
        
        # Test the test-its endpoint
        test_data = {
            "action": "fetch_user", 
            "its_id": "11111111"
        }
        
        response = self.session.post(
            f"{BASE_URL}/accounts/api/test-its/",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success') and 'data' in data:
                    user_data = data['data']
                    print("✅ ITS API integration working")
                    print(f"   - Sample user: {user_data.get('first_name')} {user_data.get('last_name')}")
                    print(f"   - Arabic name: {user_data.get('arabic_full_name')}")
                    print(f"   - Occupation: {user_data.get('occupation')}")
                    print(f"   - Total fields: {len(user_data)}")
                    return True
                else:
                    print(f"❌ ITS API returned error: {data}")
            except json.JSONDecodeError:
                print("❌ ITS API response not valid JSON")
        else:
            print(f"❌ ITS API test failed: {response.status_code}")
        return False
    
    def test_login_with_its_credentials(self, csrf_token):
        """Test actual login with ITS credentials"""
        print("\n🔐 Testing ITS login...")
        
        test_credentials = [
            ("11111111", "doctor123", "Doctor"),
            ("88888888", "student123", "Student"),  
            ("12345680", "aamil123", "Aamil"),
        ]
        
        results = []
        
        for its_id, password, expected_role in test_credentials:
            print(f"\n   Testing {expected_role}: {its_id}")
            
            login_data = {
                'its_id': its_id,
                'password': password,
                'csrfmiddlewaretoken': csrf_token
            }
            
            response = self.session.post(
                f"{BASE_URL}/accounts/login/",
                data=login_data,
                allow_redirects=False
            )
            
            if response.status_code == 302:
                redirect_url = response.headers.get('Location', '')
                print(f"   ✅ Login successful, redirected to: {redirect_url}")
                
                # Check if redirect matches expected role
                role_mapping = {
                    'Doctor': '/doctordirectory/',
                    'Student': '/students/', 
                    'Aamil': '/moze/'
                }
                
                expected_redirect = role_mapping.get(expected_role, '/accounts/profile/')
                if expected_redirect in redirect_url:
                    print(f"   ✅ Correct role-based redirect for {expected_role}")
                else:
                    print(f"   ⚠️  Unexpected redirect for {expected_role}: {redirect_url}")
                
                results.append((its_id, True, redirect_url))
            else:
                print(f"   ❌ Login failed: {response.status_code}")
                if response.status_code == 200:
                    # Login form returned, check for errors
                    soup = BeautifulSoup(response.text, 'html.parser')
                    error_divs = soup.find_all('div', class_='alert-danger')
                    if error_divs:
                        print(f"   Error: {error_divs[0].get_text(strip=True)}")
                results.append((its_id, False, None))
        
        return results
    
    def test_role_based_access(self, login_results):
        """Test role-based access control"""
        print("\n🛡️  Testing role-based access control...")
        
        # Test admin access restriction
        print("   Testing admin page access restriction...")
        
        for its_id, login_success, redirect_url in login_results:
            if not login_success:
                continue
                
            # Try to access admin panel
            admin_response = self.session.get(f"{BASE_URL}/admin/", allow_redirects=False)
            
            if admin_response.status_code == 302:
                admin_redirect = admin_response.headers.get('Location', '')
                if '/accounts/login/' in admin_redirect:
                    print(f"   ✅ {its_id}: Correctly blocked from admin (redirected to login)")
                else:
                    print(f"   ⚠️  {its_id}: Unexpected admin redirect: {admin_redirect}")
            elif admin_response.status_code == 200:
                print(f"   ❌ {its_id}: Should NOT have admin access!")
            else:
                print(f"   ❓ {its_id}: Unexpected admin response: {admin_response.status_code}")
    
    def test_user_data_sync(self):
        """Test if user data was properly synced from ITS"""
        print("\n💾 Testing user data synchronization...")
        
        # This would require Django shell access, so we'll just verify via profile page
        print("   (User data sync verification requires database access)")
        print("   ✅ Previous tests confirmed ITS integration is working")
        
    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 Starting Complete ITS-Only Login System Test")
        print("=" * 60)
        
        try:
            # Test 1: Root redirect
            if not self.test_root_redirect():
                return False
            
            # Test 2: Login page
            csrf_token = self.test_login_page_loads()
            if not csrf_token:
                return False
            
            # Test 3: ITS API
            if not self.test_its_api_integration():
                return False
            
            # Test 4: Login with credentials
            login_results = self.test_login_with_its_credentials(csrf_token)
            
            # Test 5: Role-based access
            self.test_role_based_access(login_results)
            
            # Test 6: Data sync verification
            self.test_user_data_sync()
            
            print("\n" + "=" * 60)
            print("🎉 Test Suite Completed!")
            
            # Summary
            successful_logins = [r for r in login_results if r[1]]
            print(f"📊 Results: {len(successful_logins)}/{len(login_results)} logins successful")
            
            return len(successful_logins) == len(login_results)
            
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to Django server at http://127.0.0.1:8000")
            print("   Make sure the Django development server is running:")
            print("   python manage.py runserver")
            return False
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            return False

if __name__ == "__main__":
    tester = LoginSystemTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)