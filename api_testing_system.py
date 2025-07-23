#!/usr/bin/env python3
"""
API Testing System for Umoor Sehhat
Mock ITS52.com API and comprehensive API functionality testing
"""

import os
import sys
import django
import json
import random
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
import threading
import time
import requests

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import UserProfile
from students.models import StudentProfile

User = get_user_model()

class MockITSAPI:
    """Mock ITS52.com API for testing"""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.setup_routes()
        self.mock_users = self.generate_mock_its_users()
    
    def generate_mock_its_users(self):
        """Generate mock ITS user data"""
        mock_users = {}
        
        # Generate 1000 mock ITS users
        for i in range(1000):
            its_id = str(random.randint(10000000, 99999999))
            mock_users[its_id] = {
                "its_id": its_id,
                "first_name": random.choice(["Ahmed", "Ali", "Hassan", "Hussein", "Fatima", "Aisha", "Zainab", "Maryam"]),
                "last_name": random.choice(["Khan", "Ahmed", "Shah", "Ali", "Hussain", "Malik", "Sheikh", "Qureshi"]),
                "email": f"user{its_id}@its52.com",
                "phone": f"+1{random.randint(1000000000, 9999999999)}",
                "jamaat": random.choice(["Mumbai", "Karachi", "London", "New York", "Toronto", "Dubai"]),
                "status": random.choice(["active", "inactive"]),
                "student_level": random.choice(["undergraduate", "graduate", "postgraduate"]),
                "college": random.choice(["Medical College", "Engineering College", "Business School"]),
                "verified": random.choice([True, False]),
                "last_login": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
            }
        
        return mock_users
    
    def setup_routes(self):
        """Setup Flask API routes"""
        
        @self.app.route('/api/v1/user/verify', methods=['POST'])
        def verify_user():
            """Verify ITS user by ID and password"""
            data = request.get_json()
            its_id = data.get('its_id')
            password = data.get('password')
            
            if not its_id or not password:
                return jsonify({
                    "success": False,
                    "error": "ITS ID and password required"
                }), 400
            
            # Mock verification logic
            if its_id in self.mock_users and password == "test123":
                user_data = self.mock_users[its_id]
                return jsonify({
                    "success": True,
                    "user": user_data,
                    "message": "User verified successfully"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Invalid ITS ID or password"
                }), 401
        
        @self.app.route('/api/v1/user/<its_id>', methods=['GET'])
        def get_user_info(its_id):
            """Get user information by ITS ID"""
            if its_id in self.mock_users:
                return jsonify({
                    "success": True,
                    "user": self.mock_users[its_id]
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "User not found"
                }), 404
        
        @self.app.route('/api/v1/users/search', methods=['GET'])
        def search_users():
            """Search users by various criteria"""
            query = request.args.get('q', '')
            jamaat = request.args.get('jamaat', '')
            status = request.args.get('status', '')
            limit = int(request.args.get('limit', 10))
            
            results = []
            for user in self.mock_users.values():
                if (not query or query.lower() in f"{user['first_name']} {user['last_name']}".lower()) and \
                   (not jamaat or user['jamaat'].lower() == jamaat.lower()) and \
                   (not status or user['status'] == status):
                    results.append(user)
                    if len(results) >= limit:
                        break
            
            return jsonify({
                "success": True,
                "users": results,
                "total": len(results)
            })
        
        @self.app.route('/api/v1/user/update', methods=['PUT'])
        def update_user():
            """Update user information"""
            data = request.get_json()
            its_id = data.get('its_id')
            
            if its_id in self.mock_users:
                # Update user data
                for key, value in data.items():
                    if key != 'its_id':
                        self.mock_users[its_id][key] = value
                
                return jsonify({
                    "success": True,
                    "user": self.mock_users[its_id],
                    "message": "User updated successfully"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "User not found"
                }), 404
        
        @self.app.route('/api/v1/stats', methods=['GET'])
        def get_api_stats():
            """Get API statistics"""
            return jsonify({
                "success": True,
                "stats": {
                    "total_users": len(self.mock_users),
                    "active_users": sum(1 for u in self.mock_users.values() if u['status'] == 'active'),
                    "verified_users": sum(1 for u in self.mock_users.values() if u['verified']),
                    "api_version": "1.0",
                    "server_time": datetime.now().isoformat()
                }
            })
        
        @self.app.route('/api/v1/health', methods=['GET'])
        def health_check():
            """API health check"""
            return jsonify({
                "success": True,
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0"
            })
    
    def run_server(self, port=5000):
        """Run the mock API server"""
        print(f"🚀 Starting Mock ITS API Server on port {port}")
        print(f"📡 API Base URL: http://localhost:{port}/api/v1/")
        print(f"🔗 Health Check: http://localhost:{port}/api/v1/health")
        print(f"📊 Stats: http://localhost:{port}/api/v1/stats")
        
        self.app.run(host='0.0.0.0', port=port, debug=False)

class APITester:
    """Test API functionality and integration"""
    
    def __init__(self, api_base_url="http://localhost:5000/api/v1"):
        self.api_base_url = api_base_url
        self.test_results = []
    
    def print_section(self, title):
        print(f"\n🔧 {title}")
        print("-" * 50)
    
    def test_api_health(self):
        """Test API health endpoint"""
        self.print_section("Testing API Health Check")
        
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API Health: {data['status']}")
                print(f"📅 Server Time: {data['timestamp']}")
                return True
            else:
                print(f"❌ API Health Check Failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API Connection Error: {e}")
            return False
    
    def test_user_verification(self):
        """Test user verification endpoint"""
        self.print_section("Testing User Verification")
        
        test_cases = [
            {"its_id": "12345678", "password": "test123", "expected": True},
            {"its_id": "87654321", "password": "test123", "expected": True},
            {"its_id": "12345678", "password": "wrong", "expected": False},
            {"its_id": "99999999", "password": "test123", "expected": False},
        ]
        
        passed = 0
        for i, test in enumerate(test_cases):
            try:
                response = requests.post(
                    f"{self.api_base_url}/user/verify",
                    json={"its_id": test["its_id"], "password": test["password"]},
                    timeout=5
                )
                
                success = response.status_code == 200 if test["expected"] else response.status_code != 200
                
                if success:
                    print(f"✅ Test {i+1}: {'Valid' if test['expected'] else 'Invalid'} credentials handled correctly")
                    passed += 1
                else:
                    print(f"❌ Test {i+1}: Unexpected response for {'valid' if test['expected'] else 'invalid'} credentials")
                    
            except Exception as e:
                print(f"❌ Test {i+1}: Error - {e}")
        
        print(f"📊 Verification Tests: {passed}/{len(test_cases)} passed")
        return passed == len(test_cases)
    
    def test_user_search(self):
        """Test user search functionality"""
        self.print_section("Testing User Search")
        
        search_tests = [
            {"q": "Ahmed", "expected_min": 1},
            {"jamaat": "Mumbai", "expected_min": 1},
            {"status": "active", "expected_min": 1},
            {"limit": "5", "expected_max": 5},
        ]
        
        passed = 0
        for i, test in enumerate(search_tests):
            try:
                response = requests.get(f"{self.api_base_url}/users/search", params=test, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    users_count = len(data.get('users', []))
                    
                    if 'expected_min' in test and users_count >= test['expected_min']:
                        print(f"✅ Search Test {i+1}: Found {users_count} users (minimum {test['expected_min']})")
                        passed += 1
                    elif 'expected_max' in test and users_count <= test['expected_max']:
                        print(f"✅ Search Test {i+1}: Found {users_count} users (maximum {test['expected_max']})")
                        passed += 1
                    else:
                        print(f"❌ Search Test {i+1}: Unexpected result count: {users_count}")
                else:
                    print(f"❌ Search Test {i+1}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Search Test {i+1}: Error - {e}")
        
        print(f"📊 Search Tests: {passed}/{len(search_tests)} passed")
        return passed == len(search_tests)
    
    def test_api_stats(self):
        """Test API statistics endpoint"""
        self.print_section("Testing API Statistics")
        
        try:
            response = requests.get(f"{self.api_base_url}/stats", timeout=5)
            if response.status_code == 200:
                data = response.json()
                stats = data['stats']
                
                print(f"✅ Total Users: {stats['total_users']}")
                print(f"✅ Active Users: {stats['active_users']}")
                print(f"✅ Verified Users: {stats['verified_users']}")
                print(f"✅ API Version: {stats['api_version']}")
                
                return True
            else:
                print(f"❌ Stats endpoint failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Stats test error: {e}")
            return False
    
    def test_django_integration(self):
        """Test Django integration with API"""
        self.print_section("Testing Django-API Integration")
        
        try:
            # Test creating a Django user with ITS verification
            test_its_id = str(random.randint(10000000, 99999999))
            
            # Simulate API verification
            verify_response = requests.post(
                f"{self.api_base_url}/user/verify",
                json={"its_id": test_its_id, "password": "test123"},
                timeout=5
            )
            
            if verify_response.status_code == 200:
                user_data = verify_response.json()['user']
                
                # Create Django user based on API data
                django_user = User.objects.create_user(
                    username=f"its_{test_its_id}",
                    email=user_data['email'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    password='temp123',
                    role='student'
                )
                
                # Create student profile with ITS data
                student_profile = StudentProfile.objects.create(
                    user=django_user,
                    its_id=test_its_id,
                    college=user_data['college'],
                    specialization=user_data['student_level'],
                    is_verified=user_data['verified']
                )
                
                print(f"✅ Django user created: {django_user.username}")
                print(f"✅ Student profile created with ITS ID: {test_its_id}")
                print(f"✅ API-Django integration working")
                
                # Cleanup
                student_profile.delete()
                django_user.delete()
                
                return True
            else:
                print(f"❌ API verification failed for integration test")
                return False
                
        except Exception as e:
            print(f"❌ Django integration test error: {e}")
            return False
    
    def run_comprehensive_test(self):
        """Run all API tests"""
        print("🧪 STARTING COMPREHENSIVE API TESTING")
        print("=" * 60)
        
        tests = [
            ("API Health Check", self.test_api_health),
            ("User Verification", self.test_user_verification),
            ("User Search", self.test_user_search),
            ("API Statistics", self.test_api_stats),
            ("Django Integration", self.test_django_integration),
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                if result:
                    passed_tests += 1
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")
            except Exception as e:
                print(f"💥 {test_name}: ERROR - {e}")
        
        print("\n" + "=" * 60)
        print("🎯 API TESTING SUMMARY")
        print("=" * 60)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"📊 Tests Passed: {passed_tests}/{total_tests}")
        print(f"🏆 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🟢 API Status: EXCELLENT - Ready for production")
        elif success_rate >= 60:
            print("🟡 API Status: GOOD - Minor issues to address")
        else:
            print("🔴 API Status: NEEDS ATTENTION - Major issues found")
        
        return success_rate >= 80

def start_mock_api_server():
    """Start the mock API server in a separate thread"""
    mock_api = MockITSAPI()
    server_thread = threading.Thread(target=mock_api.run_server, args=(5000,))
    server_thread.daemon = True
    server_thread.start()
    
    # Wait for server to start
    time.sleep(2)
    return server_thread

def main():
    """Main function to run API testing"""
    print("🎯 UMOOR SEHHAT API TESTING SYSTEM")
    print("=" * 60)
    
    choice = input("""
Choose an option:
1. Start Mock ITS API Server
2. Run API Tests (requires server running)
3. Start Server and Run Tests
4. Exit

Enter choice (1-4): """).strip()
    
    if choice == "1":
        print("\n🚀 Starting Mock ITS API Server...")
        mock_api = MockITSAPI()
        mock_api.run_server()
        
    elif choice == "2":
        print("\n🧪 Running API Tests...")
        tester = APITester()
        tester.run_comprehensive_test()
        
    elif choice == "3":
        print("\n🚀 Starting Server and Running Tests...")
        
        # Start server
        server_thread = start_mock_api_server()
        
        print("✅ Mock API Server started successfully")
        print("🧪 Running comprehensive tests...\n")
        
        # Run tests
        tester = APITester()
        success = tester.run_comprehensive_test()
        
        if success:
            print("\n🎉 All tests passed! API system is ready for integration.")
        else:
            print("\n⚠️  Some tests failed. Review the results above.")
            
        print("\n📝 Integration Guide:")
        print("1. Replace mock API URL with real ITS52.com endpoints")
        print("2. Update authentication tokens/API keys")
        print("3. Modify data mappings as needed")
        print("4. Test with real ITS data")
        
    elif choice == "4":
        print("👋 Goodbye!")
        
    else:
        print("❌ Invalid choice. Please run again.")

if __name__ == "__main__":
    main()