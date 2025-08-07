"""
Tests for the accounts app API
"""
import json
from datetime import datetime, timedelta
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch

from accounts.models import User, UserProfile, AuditLog
from accounts.services import mock_its_service

User = get_user_model()


class AccountsAPITestCase(APITestCase):
    """Base test case for accounts API tests"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test users
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            first_name='Admin',
            last_name='User',
            role='badri_mahal_admin',
            its_id='12345678',
            is_staff=True,
            is_superuser=True
        )
        
        self.regular_user = User.objects.create_user(
            username='regular',
            email='regular@test.com',
            password='testpass123',
            first_name='Regular',
            last_name='User',
            role='student',
            its_id='87654321'
        )
        
        # Create JWT tokens
        self.admin_token = RefreshToken.for_user(self.admin_user)
        self.regular_token = RefreshToken.for_user(self.regular_user)
    
    def authenticate_user(self, user_type='regular'):
        """Helper method to authenticate users"""
        if user_type == 'admin':
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token.access_token}')
        else:
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.regular_token.access_token}')


class AuthenticationAPITests(AccountsAPITestCase):
    """Tests for authentication endpoints"""
    
    def test_jwt_login_success(self):
        """Test successful JWT login"""
        url = reverse('accounts_api:token_obtain_pair')
        data = {
            'username': 'regular',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'regular')
    
    def test_jwt_login_with_its_id(self):
        """Test JWT login using ITS ID"""
        url = reverse('accounts_api:token_obtain_pair')
        data = {
            'its_id': '87654321',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertEqual(response.data['user']['its_id'], '87654321')
    
    def test_jwt_login_invalid_credentials(self):
        """Test JWT login with invalid credentials"""
        url = reverse('accounts_api:token_obtain_pair')
        data = {
            'username': 'regular',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_token_refresh(self):
        """Test JWT token refresh"""
        url = reverse('accounts_api:token_refresh')
        data = {
            'refresh': str(self.regular_token)
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_logout(self):
        """Test logout endpoint"""
        self.authenticate_user('regular')
        url = reverse('accounts_api:logout')
        data = {
            'refresh_token': str(self.regular_token)
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Logout successful')


class UserProfileAPITests(AccountsAPITestCase):
    """Tests for user profile endpoints"""
    
    def test_get_current_user_profile(self):
        """Test getting current user profile"""
        self.authenticate_user('regular')
        url = reverse('accounts_api:user_profile')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'regular')
        self.assertEqual(response.data['its_id'], '87654321')
    
    def test_update_current_user_profile(self):
        """Test updating current user profile"""
        self.authenticate_user('regular')
        url = reverse('accounts_api:user_profile')
        data = {
            'first_name': 'Updated',
            'occupation': 'Software Engineer',
            'city': 'Mumbai'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')
        self.assertEqual(response.data['occupation'], 'Software Engineer')
        self.assertEqual(response.data['city'], 'Mumbai')
        
        # Verify in database
        user = User.objects.get(id=self.regular_user.id)
        self.assertEqual(user.first_name, 'Updated')
        self.assertEqual(user.occupation, 'Software Engineer')
    
    def test_get_profile_unauthenticated(self):
        """Test getting profile without authentication"""
        url = reverse('accounts_api:user_profile')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserManagementAPITests(AccountsAPITestCase):
    """Tests for user management endpoints"""
    
    def test_list_users_as_admin(self):
        """Test listing users as admin"""
        self.authenticate_user('admin')
        url = reverse('accounts_api:user_list_create')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)  # admin + regular user
    
    def test_list_users_as_regular_user(self):
        """Test listing users as regular user"""
        self.authenticate_user('regular')
        url = reverse('accounts_api:user_list_create')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Regular users can see user list but with limited info
    
    def test_create_user_as_admin(self):
        """Test creating user as admin"""
        self.authenticate_user('admin')
        url = reverse('accounts_api:user_list_create')
        data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'newpass123',
            'confirm_password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'student',
            'its_id': '11111111'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'newuser')
        self.assertEqual(response.data['its_id'], '11111111')
        
        # Verify user was created
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_create_user_as_regular_user(self):
        """Test creating user as regular user (should fail)"""
        self.authenticate_user('regular')
        url = reverse('accounts_api:user_list_create')
        data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'newpass123'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_user_detail(self):
        """Test getting user detail"""
        self.authenticate_user('regular')
        url = reverse('accounts_api:user_detail', kwargs={'pk': self.regular_user.pk})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'regular')
    
    def test_update_own_user(self):
        """Test updating own user data"""
        self.authenticate_user('regular')
        url = reverse('accounts_api:user_detail', kwargs={'pk': self.regular_user.pk})
        data = {
            'first_name': 'Updated Regular'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated Regular')
    
    def test_update_other_user_as_regular(self):
        """Test updating other user as regular user (should fail)"""
        self.authenticate_user('regular')
        url = reverse('accounts_api:user_detail', kwargs={'pk': self.admin_user.pk})
        data = {
            'first_name': 'Hacked Admin'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_search_users(self):
        """Test user search functionality"""
        self.authenticate_user('regular')
        url = reverse('accounts_api:user_search')
        data = {
            'query': 'regular',
            'role': 'student'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['username'], 'regular')


class ITSSyncAPITests(AccountsAPITestCase):
    """Tests for ITS synchronization endpoints"""
    
    @patch('accounts.services.mock_its_service.fetch_user_data')
    def test_its_sync_new_user(self, mock_fetch):
        """Test ITS sync for new user"""
        # Mock ITS API response
        mock_fetch.return_value = {
            'its_id': '99999999',
            'first_name': 'Ahmed',
            'last_name': 'Khan',
            'email': 'ahmed.khan@example.com',
            'arabic_full_name': 'Ahmed Khan',
            'prefix': 'Mr',
            'age': 30,
            'gender': 'male',
            'occupation': 'Engineer',
            'city': 'Mumbai'
        }
        
        self.authenticate_user('admin')
        url = reverse('accounts_api:its_sync')
        data = {
            'its_id': '99999999',
            'force_update': False
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'User created successfully')
        self.assertEqual(response.data['user']['its_id'], '99999999')
        
        # Verify user was created
        user = User.objects.get(its_id='99999999')
        self.assertEqual(user.first_name, 'Ahmed')
        self.assertEqual(user.occupation, 'Engineer')
    
    @patch('accounts.services.mock_its_service.fetch_user_data')
    def test_its_sync_existing_user(self, mock_fetch):
        """Test ITS sync for existing user"""
        mock_fetch.return_value = {
            'its_id': '87654321',
            'first_name': 'Updated Regular',
            'occupation': 'Updated Engineer'
        }
        
        self.authenticate_user('admin')
        url = reverse('accounts_api:its_sync')
        data = {
            'its_id': '87654321',
            'force_update': True
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'User updated successfully')
    
    @patch('accounts.services.mock_its_service.fetch_user_data')
    def test_its_sync_user_not_found(self, mock_fetch):
        """Test ITS sync when user not found in ITS"""
        mock_fetch.return_value = None
        
        self.authenticate_user('admin')
        url = reverse('accounts_api:its_sync')
        data = {
            'its_id': '00000000'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('User not found in ITS system', response.data['error'])
    
    def test_bulk_its_sync(self):
        """Test bulk ITS synchronization"""
        self.authenticate_user('admin')
        url = reverse('accounts_api:bulk_its_sync')
        data = {
            'its_ids': ['11111111', '22222222', '33333333']
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        self.assertIn('Processed 3 ITS IDs', response.data['message'])


class PasswordChangeAPITests(AccountsAPITestCase):
    """Tests for password change endpoint"""
    
    def test_change_password_success(self):
        """Test successful password change"""
        self.authenticate_user('regular')
        url = reverse('accounts_api:change_password')
        data = {
            'old_password': 'testpass123',
            'new_password': 'newpass456',
            'confirm_password': 'newpass456'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Password changed successfully')
        
        # Verify password was changed
        user = User.objects.get(id=self.regular_user.id)
        self.assertTrue(user.check_password('newpass456'))
    
    def test_change_password_wrong_old_password(self):
        """Test password change with wrong old password"""
        self.authenticate_user('regular')
        url = reverse('accounts_api:change_password')
        data = {
            'old_password': 'wrongpassword',
            'new_password': 'newpass456',
            'confirm_password': 'newpass456'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Old password is incorrect', str(response.data))
    
    def test_change_password_mismatch(self):
        """Test password change with mismatched new passwords"""
        self.authenticate_user('regular')
        url = reverse('accounts_api:change_password')
        data = {
            'old_password': 'testpass123',
            'new_password': 'newpass456',
            'confirm_password': 'differentpass'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('New passwords do not match', str(response.data))


class UserStatsAPITests(AccountsAPITestCase):
    """Tests for user statistics endpoint"""
    
    def test_user_stats(self):
        """Test user statistics endpoint"""
        self.authenticate_user('admin')
        url = reverse('accounts_api:user_stats')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_users', response.data)
        self.assertIn('active_users', response.data)
        self.assertIn('users_by_role', response.data)
        self.assertEqual(response.data['total_users'], 2)


class MockITSServiceTests(TestCase):
    """Tests for the mock ITS service"""
    
    def test_fetch_user_data_valid_id(self):
        """Test fetching user data with valid ITS ID"""
        data = mock_its_service.fetch_user_data('12345678')
        
        self.assertIsNotNone(data)
        self.assertEqual(data['its_id'], '12345678')
        self.assertIn('first_name', data)
        self.assertIn('last_name', data)
        self.assertIn('email', data)
    
    def test_fetch_user_data_invalid_id(self):
        """Test fetching user data with invalid ITS ID"""
        data = mock_its_service.fetch_user_data('invalid')
        
        self.assertIsNone(data)
    
    def test_validate_its_id(self):
        """Test ITS ID validation"""
        self.assertTrue(mock_its_service.validate_its_id('12345678'))
        self.assertFalse(mock_its_service.validate_its_id('1234567'))  # Too short
        self.assertFalse(mock_its_service.validate_its_id('123456789'))  # Too long
        self.assertFalse(mock_its_service.validate_its_id('abcdefgh'))  # Not digits
        self.assertFalse(mock_its_service.validate_its_id(''))  # Empty
    
    def test_search_users(self):
        """Test user search functionality"""
        results = mock_its_service.search_users('Ahmed')
        
        self.assertIsInstance(results, list)
        self.assertLessEqual(len(results), 5)  # Should return max 5 results


class FiltersAndPaginationTests(AccountsAPITestCase):
    """Tests for filtering and pagination"""
    
    def setUp(self):
        super().setUp()
        # Create additional test users
        for i in range(15):
            User.objects.create_user(
                username=f'user{i}',
                email=f'user{i}@test.com',
                password='testpass123',
                role='student' if i % 2 == 0 else 'doctor',
                jamaat='Mumbai Central' if i % 3 == 0 else 'Delhi Shahdara'
            )
    
    def test_user_list_pagination(self):
        """Test user list pagination"""
        self.authenticate_user('admin')
        url = reverse('accounts_api:user_list_create')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 17)  # Default page size is 20
    
    def test_user_list_filtering_by_role(self):
        """Test filtering users by role"""
        self.authenticate_user('admin')
        url = reverse('accounts_api:user_list_create')
        
        response = self.client.get(f'{url}?role=student')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for user in response.data['results']:
            self.assertEqual(user['role'], 'student')
    
    def test_user_list_search(self):
        """Test searching users"""
        self.authenticate_user('admin')
        url = reverse('accounts_api:user_list_create')
        
        response = self.client.get(f'{url}?search=admin')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['count'], 1)
    
    def test_user_list_ordering(self):
        """Test ordering users"""
        self.authenticate_user('admin')
        url = reverse('accounts_api:user_list_create')
        
        response = self.client.get(f'{url}?ordering=first_name')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify ordering (basic check)
        self.assertGreater(len(response.data['results']), 0)