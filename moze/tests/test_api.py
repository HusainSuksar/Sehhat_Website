"""
Unit tests for the Moze API
"""
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import date, time, timedelta
import json

from moze.models import Moze, UmoorSehhatTeam, MozeComment, MozeSettings

User = get_user_model()


class MozeAPITestCase(APITestCase):
    """Base test case for Moze API tests"""
    
    def setUp(self):
        """Set up test data"""
        # Create users with different roles
        self.admin_user = User.objects.create_user(
            username='admin_user',
            email='admin@test.com',
            password='testpass123',
            role='badri_mahal_admin',
            first_name='Admin',
            last_name='User'
        )
        
        self.aamil_user = User.objects.create_user(
            username='aamil_user',
            email='aamil@test.com',
            password='testpass123',
            role='aamil',
            first_name='Aamil',
            last_name='User'
        )
        
        self.coordinator_user = User.objects.create_user(
            username='coordinator_user',
            email='coordinator@test.com',
            password='testpass123',
            role='moze_coordinator',
            first_name='Coordinator',
            last_name='User'
        )
        
        self.team_member_user = User.objects.create_user(
            username='team_member',
            email='team@test.com',
            password='testpass123',
            role='patient',
            first_name='Team',
            last_name='Member'
        )
        
        self.regular_user = User.objects.create_user(
            username='regular_user',
            email='regular@test.com',
            password='testpass123',
            role='patient',
            first_name='Regular',
            last_name='User'
        )
        
        # Create test Moze
        self.moze = Moze.objects.create(
            name='Test Moze',
            location='Test Location',
            address='123 Test Street',
            aamil=self.aamil_user,
            moze_coordinator=self.coordinator_user,
            established_date=date(2020, 1, 1),
            capacity=100,
            contact_phone='123-456-7890',
            contact_email='test@moze.com'
        )
        
        # Add team member to Moze
        self.moze.team_members.add(self.team_member_user)
        
        # Create Moze settings
        self.moze_settings = MozeSettings.objects.create(
            moze=self.moze,
            allow_walk_ins=True,
            appointment_duration=30,
            working_hours_start=time(9, 0),
            working_hours_end=time(17, 0),
            working_days=[0, 1, 2, 3, 4, 5],  # Monday to Saturday
            emergency_contact='emergency-123'
        )
        
        # Create Umoor Sehhat team member
        self.team_member = UmoorSehhatTeam.objects.create(
            moze=self.moze,
            category='medical',
            member=self.team_member_user,
            position='Nurse',
            contact_number='987-654-3210'
        )
        
        # Create test comment
        self.comment = MozeComment.objects.create(
            moze=self.moze,
            author=self.aamil_user,
            content='Test comment content'
        )
        
        self.client = APIClient()


class MozeAPITests(MozeAPITestCase):
    """Test Moze CRUD operations"""
    
    def test_list_mozes_admin(self):
        """Test admin can list all mozes"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('moze_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Moze')
    
    def test_list_mozes_aamil(self):
        """Test aamil can list their mozes"""
        self.client.force_authenticate(user=self.aamil_user)
        url = reverse('moze_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_list_mozes_coordinator(self):
        """Test coordinator can list their mozes"""
        self.client.force_authenticate(user=self.coordinator_user)
        url = reverse('moze_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_list_mozes_team_member(self):
        """Test team member can list mozes they're part of"""
        self.client.force_authenticate(user=self.team_member_user)
        url = reverse('moze_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_list_mozes_regular_user(self):
        """Test regular user cannot see any mozes"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('moze_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
    
    def test_create_moze_admin(self):
        """Test admin can create moze"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('moze_list_create')
        data = {
            'name': 'New Moze',
            'location': 'New Location',
            'address': '456 New Street',
            'aamil_id': self.aamil_user.id,
            'capacity': 150
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Moze.objects.count(), 2)
    
    def test_create_moze_aamil(self):
        """Test aamil can create moze"""
        self.client.force_authenticate(user=self.aamil_user)
        url = reverse('moze_list_create')
        data = {
            'name': 'Aamil Moze',
            'location': 'Aamil Location',
            'aamil_id': self.aamil_user.id,
            'capacity': 120
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_create_moze_non_aamil_forbidden(self):
        """Test non-aamil cannot create moze"""
        self.client.force_authenticate(user=self.team_member_user)
        url = reverse('moze_list_create')
        data = {
            'name': 'Forbidden Moze',
            'location': 'Forbidden Location',
            'aamil_id': self.aamil_user.id
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_retrieve_moze(self):
        """Test retrieving a specific moze"""
        self.client.force_authenticate(user=self.aamil_user)
        url = reverse('moze_detail', kwargs={'pk': self.moze.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Moze')
        self.assertIn('settings', response.data)
        self.assertIn('umoor_teams', response.data)
    
    def test_update_moze_aamil(self):
        """Test aamil can update their moze"""
        self.client.force_authenticate(user=self.aamil_user)
        url = reverse('moze_detail', kwargs={'pk': self.moze.pk})
        data = {
            'name': 'Updated Moze Name',
            'location': self.moze.location,
            'aamil_id': self.aamil_user.id
        }
        
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.moze.refresh_from_db()
        self.assertEqual(self.moze.name, 'Updated Moze Name')
    
    def test_delete_moze_admin(self):
        """Test admin can delete moze"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('moze_detail', kwargs={'pk': self.moze.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Moze.objects.count(), 0)
    
    def test_search_mozes(self):
        """Test moze search functionality"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('moze_search')
        response = self.client.get(url, {'name': 'Test'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class UmoorSehhatTeamAPITests(MozeAPITestCase):
    """Test Umoor Sehhat Team CRUD operations"""
    
    def test_list_teams_admin(self):
        """Test admin can list all teams"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('team_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_list_teams_aamil(self):
        """Test aamil can list teams from their mozes"""
        self.client.force_authenticate(user=self.aamil_user)
        url = reverse('team_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_team_member_aamil(self):
        """Test aamil can create team members"""
        self.client.force_authenticate(user=self.aamil_user)
        url = reverse('team_list_create')
        data = {
            'moze': self.moze.id,
            'category': 'sports',
            'member_id': self.regular_user.id,
            'position': 'Sports Coordinator'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UmoorSehhatTeam.objects.count(), 2)
    
    def test_create_team_member_non_aamil_forbidden(self):
        """Test non-aamil cannot create team members"""
        self.client.force_authenticate(user=self.team_member_user)
        url = reverse('team_list_create')
        data = {
            'moze': self.moze.id,
            'category': 'medical',
            'member_id': self.regular_user.id
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_search_teams(self):
        """Test team search functionality"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('team_search')
        response = self.client.get(url, {'category': 'medical'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class MozeSettingsAPITests(MozeAPITestCase):
    """Test Moze Settings CRUD operations"""
    
    def test_list_settings_admin(self):
        """Test admin can list all settings"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('moze_settings_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_retrieve_settings(self):
        """Test retrieving moze settings with computed fields"""
        self.client.force_authenticate(user=self.aamil_user)
        url = reverse('moze_settings_detail', kwargs={'pk': self.moze_settings.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('working_hours_display', response.data)
        self.assertIn('is_currently_open', response.data)
    
    def test_update_settings_aamil(self):
        """Test aamil can update settings for their moze"""
        self.client.force_authenticate(user=self.aamil_user)
        url = reverse('moze_settings_detail', kwargs={'pk': self.moze_settings.pk})
        data = {
            'appointment_duration': 45,
            'allow_walk_ins': False
        }
        
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.moze_settings.refresh_from_db()
        self.assertEqual(self.moze_settings.appointment_duration, 45)


class MozeCommentAPITests(MozeAPITestCase):
    """Test Moze Comments CRUD operations"""
    
    def test_list_comments_team_member(self):
        """Test team member can list comments from accessible mozes"""
        self.client.force_authenticate(user=self.team_member_user)
        url = reverse('comment_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_comment_aamil(self):
        """Test aamil can create comment"""
        self.client.force_authenticate(user=self.aamil_user)
        url = reverse('comment_list_create')
        data = {
            'moze': self.moze.id,
            'content': 'New comment from aamil'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MozeComment.objects.count(), 2)
    
    def test_create_comment_unauthorized_user(self):
        """Test unauthorized user cannot comment"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('comment_list_create')
        data = {
            'moze': self.moze.id,
            'content': 'Unauthorized comment'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_comment_author(self):
        """Test comment author can update their comment"""
        self.client.force_authenticate(user=self.aamil_user)
        url = reverse('comment_detail', kwargs={'pk': self.comment.pk})
        data = {
            'content': 'Updated comment content'
        }
        
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, 'Updated comment content')
    
    def test_create_reply_comment(self):
        """Test creating a reply to a comment"""
        self.client.force_authenticate(user=self.coordinator_user)
        url = reverse('comment_list_create')
        data = {
            'moze': self.moze.id,
            'parent': self.comment.id,
            'content': 'This is a reply'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that the reply is properly nested
        self.client.force_authenticate(user=self.aamil_user)
        comment_url = reverse('comment_detail', kwargs={'pk': self.comment.pk})
        comment_response = self.client.get(comment_url)
        self.assertEqual(len(comment_response.data['replies']), 1)


class StatisticsAPITests(MozeAPITestCase):
    """Test statistics API endpoints"""
    
    def test_moze_stats_admin(self):
        """Test admin can access moze statistics"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('moze_stats_api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_mozes', response.data)
        self.assertIn('active_mozes', response.data)
        self.assertIn('total_team_members', response.data)
    
    def test_moze_stats_aamil(self):
        """Test aamil can access their moze statistics"""
        self.client.force_authenticate(user=self.aamil_user)
        url = reverse('moze_stats_api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_mozes'], 1)
    
    def test_team_stats_admin(self):
        """Test admin can access team statistics"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('team_stats_api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_team_members', response.data)
        self.assertIn('members_by_category', response.data)
    
    def test_stats_unauthorized_user(self):
        """Test unauthorized user cannot access statistics"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('moze_stats_api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class DashboardAPITests(MozeAPITestCase):
    """Test dashboard API functionality"""
    
    def test_dashboard_admin(self):
        """Test admin can access comprehensive dashboard"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('moze_dashboard_api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('moze_stats', response.data)
        self.assertIn('team_stats', response.data)
        self.assertIn('recent_mozes', response.data)
        self.assertIn('recent_team_members', response.data)
        self.assertIn('recent_comments', response.data)
    
    def test_dashboard_aamil(self):
        """Test aamil can access their dashboard"""
        self.client.force_authenticate(user=self.aamil_user)
        url = reverse('moze_dashboard_api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('moze_stats', response.data)
        self.assertEqual(response.data['moze_stats']['total_mozes'], 1)
    
    def test_dashboard_team_member(self):
        """Test team member can access their limited dashboard"""
        self.client.force_authenticate(user=self.team_member_user)
        url = reverse('moze_dashboard_api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('my_mozes', response.data)
        self.assertIn('my_team_memberships', response.data)
        self.assertEqual(len(response.data['my_mozes']), 1)


class PermissionTests(MozeAPITestCase):
    """Test role-based permissions"""
    
    def test_aamil_can_only_access_their_mozes(self):
        """Test aamil can only access mozes they manage"""
        # Create another aamil and moze
        other_aamil = User.objects.create_user(
            username='other_aamil',
            role='aamil',
            password='testpass123'
        )
        other_moze = Moze.objects.create(
            name='Other Moze',
            location='Other Location',
            aamil=other_aamil
        )
        
        self.client.force_authenticate(user=self.aamil_user)
        
        # Should see own moze
        url = reverse('moze_list_create')
        response = self.client.get(url)
        self.assertEqual(len(response.data['results']), 1)
        
        # Should not be able to access other moze
        url = reverse('moze_detail', kwargs={'pk': other_moze.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_coordinator_permissions(self):
        """Test coordinator can access mozes they coordinate"""
        self.client.force_authenticate(user=self.coordinator_user)
        url = reverse('moze_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_team_member_can_view_but_not_modify(self):
        """Test team member can view but not modify moze"""
        self.client.force_authenticate(user=self.team_member_user)
        
        # Can view
        url = reverse('moze_detail', kwargs={'pk': self.moze.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Cannot modify
        data = {'name': 'Modified Name'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class FilteringAndSearchTests(MozeAPITestCase):
    """Test filtering and search functionality"""
    
    def test_filter_mozes_by_active_status(self):
        """Test filtering mozes by active status"""
        # Create inactive moze
        inactive_moze = Moze.objects.create(
            name='Inactive Moze',
            location='Inactive Location',
            aamil=self.aamil_user,
            is_active=False
        )
        
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('moze_list_create')
        
        # Filter for active mozes
        response = self.client.get(url, {'is_active': 'true'})
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Moze')
        
        # Filter for inactive mozes
        response = self.client.get(url, {'is_active': 'false'})
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Inactive Moze')
    
    def test_search_mozes_by_location(self):
        """Test searching mozes by location"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('moze_search')
        
        response = self.client.get(url, {'location': 'Test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        response = self.client.get(url, {'location': 'Nonexistent'})
        self.assertEqual(len(response.data['results']), 0)
    
    def test_filter_teams_by_category(self):
        """Test filtering teams by category"""
        # Create team member in different category
        UmoorSehhatTeam.objects.create(
            moze=self.moze,
            category='sports',
            member=self.regular_user,
            position='Sports Coordinator'
        )
        
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('team_list_create')
        
        # Filter by medical category
        response = self.client.get(url, {'category': 'medical'})
        self.assertEqual(len(response.data['results']), 1)
        
        # Filter by sports category
        response = self.client.get(url, {'category': 'sports'})
        self.assertEqual(len(response.data['results']), 1)
    
    def test_search_teams_by_member_name(self):
        """Test searching teams by member name"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('team_search')
        
        response = self.client.get(url, {'member_name': 'Team'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        response = self.client.get(url, {'member_name': 'Nonexistent'})
        self.assertEqual(len(response.data['results']), 0)