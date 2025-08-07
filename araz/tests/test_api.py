"""
Tests for the Araz app API
"""
import json
from datetime import datetime, timedelta
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone

from araz.models import (
    DuaAraz, Petition, PetitionCategory, PetitionComment, ArazComment,
    PetitionAssignment, ArazNotification
)
from doctordirectory.models import Doctor
from moze.models import Moze

User = get_user_model()


class ArazAPITestCase(APITestCase):
    """Base test case for Araz API tests"""
    
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
        
        self.doctor_user = User.objects.create_user(
            username='doctor',
            email='doctor@test.com',
            password='testpass123',
            first_name='Dr',
            last_name='Smith',
            role='doctor',
            its_id='11111111'
        )
        
        self.patient_user = User.objects.create_user(
            username='patient',
            email='patient@test.com',
            password='testpass123',
            first_name='Patient',
            last_name='User',
            role='student',
            its_id='22222222'
        )
        
        self.aamil_user = User.objects.create_user(
            username='aamil',
            email='aamil@test.com',
            password='testpass123',
            first_name='Aamil',
            last_name='User',
            role='aamil',
            its_id='33333333'
        )
        
        # Create doctor profile
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            name='Dr Smith',
            specialty='General Medicine',
            license_number='DOC123',
            its_id='11111111'
        )
        
        # Create Moze center
        self.moze = Moze.objects.create(
            name='Test Moze',
            location='Test Location',
            aamil=self.aamil_user,
            contact_phone='+91-9876543210',
            contact_email='moze@test.com'
        )
        
        # Create petition category
        self.category = PetitionCategory.objects.create(
            name='General Complaint',
            description='General complaints and issues',
            color='#007bff'
        )
        
        # Create JWT tokens
        self.admin_token = RefreshToken.for_user(self.admin_user)
        self.doctor_token = RefreshToken.for_user(self.doctor_user)
        self.patient_token = RefreshToken.for_user(self.patient_user)
        self.aamil_token = RefreshToken.for_user(self.aamil_user)
    
    def authenticate_user(self, user_type='patient'):
        """Helper method to authenticate users"""
        token_map = {
            'admin': self.admin_token,
            'doctor': self.doctor_token,
            'patient': self.patient_token,
            'aamil': self.aamil_token
        }
        token = token_map.get(user_type, self.patient_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')


class DuaArazAPITests(ArazAPITestCase):
    """Tests for DuaAraz API endpoints"""
    
    def test_create_araz_request(self):
        """Test creating a new Araz request"""
        self.authenticate_user('patient')
        url = reverse('araz_api:araz_list_create')
        data = {
            'patient_its_id': '22222222',
            'ailment': 'Severe headache and fever',
            'symptoms': 'Headache, fever, body ache',
            'urgency_level': 'high',
            'request_type': 'consultation',
            'preferred_doctor_id': self.doctor.id,
            'preferred_contact_method': 'phone'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DuaAraz.objects.count(), 1)
        
        araz = DuaAraz.objects.first()
        self.assertEqual(araz.patient_user, self.patient_user)
        self.assertEqual(araz.ailment, 'Severe headache and fever')
        self.assertEqual(araz.urgency_level, 'high')
        self.assertEqual(araz.preferred_doctor, self.doctor)
    
    def test_list_araz_requests_patient(self):
        """Test listing Araz requests as patient"""
        # Create test Araz
        araz = DuaAraz.objects.create(
            patient_user=self.patient_user,
            patient_its_id='22222222',
            patient_name='Patient User',
            ailment='Test ailment',
            urgency_level='medium',
            request_type='consultation'
        )
        
        self.authenticate_user('patient')
        url = reverse('araz_api:araz_list_create')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], araz.id)
    
    def test_list_araz_requests_doctor(self):
        """Test listing Araz requests as doctor"""
        # Create test Araz assigned to doctor
        araz = DuaAraz.objects.create(
            patient_user=self.patient_user,
            patient_its_id='22222222',
            patient_name='Patient User',
            ailment='Test ailment',
            urgency_level='medium',
            request_type='consultation',
            assigned_doctor=self.doctor
        )
        
        self.authenticate_user('doctor')
        url = reverse('araz_api:araz_list_create')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
    
    def test_update_araz_status_doctor(self):
        """Test updating Araz status as doctor"""
        araz = DuaAraz.objects.create(
            patient_user=self.patient_user,
            patient_its_id='22222222',
            patient_name='Patient User',
            ailment='Test ailment',
            urgency_level='medium',
            request_type='consultation',
            assigned_doctor=self.doctor,
            status='submitted'
        )
        
        self.authenticate_user('doctor')
        url = reverse('araz_api:araz_detail', kwargs={'pk': araz.id})
        data = {
            'status': 'in_progress',
            'admin_notes': 'Patient consultation scheduled'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        araz.refresh_from_db()
        self.assertEqual(araz.status, 'in_progress')
        self.assertEqual(araz.admin_notes, 'Patient consultation scheduled')
        
        # Check that status history was created
        self.assertTrue(araz.status_history.exists())
        
        # Check that notification was created for patient
        self.assertTrue(
            ArazNotification.objects.filter(
                araz=araz,
                recipient=self.patient_user,
                notification_type='status_update'
            ).exists()
        )
    
    def test_search_araz_requests(self):
        """Test advanced search for Araz requests"""
        # Create test Araz with specific criteria
        araz = DuaAraz.objects.create(
            patient_user=self.patient_user,
            patient_its_id='22222222',
            patient_name='Patient User',
            ailment='Diabetes management',
            urgency_level='high',
            request_type='chronic_care',
            status='submitted'
        )
        
        self.authenticate_user('admin')
        url = reverse('araz_api:araz_search')
        data = {
            'query': 'diabetes',
            'urgency_level': 'high',
            'request_type': 'chronic_care'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], araz.id)
    
    def test_araz_overdue_calculation(self):
        """Test overdue calculation in search"""
        # Create overdue emergency Araz (> 1 day old)
        old_date = timezone.now() - timedelta(days=2)
        araz = DuaAraz.objects.create(
            patient_user=self.patient_user,
            patient_its_id='22222222',
            patient_name='Patient User',
            ailment='Emergency case',
            urgency_level='emergency',
            request_type='emergency',
            status='submitted'
        )
        araz.created_at = old_date
        araz.save()
        
        self.authenticate_user('admin')
        url = reverse('araz_api:araz_search')
        data = {
            'is_overdue': True
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)


class PetitionAPITests(ArazAPITestCase):
    """Tests for Petition API endpoints"""
    
    def test_create_petition(self):
        """Test creating a new petition"""
        self.authenticate_user('patient')
        url = reverse('araz_api:petition_list_create')
        data = {
            'title': 'Facility Improvement Request',
            'description': 'Request for better facilities in the community center',
            'category_id': self.category.id,
            'priority': 'medium',
            'moze': self.moze.id
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Petition.objects.count(), 1)
        
        petition = Petition.objects.first()
        self.assertEqual(petition.created_by, self.patient_user)
        self.assertEqual(petition.title, 'Facility Improvement Request')
        self.assertEqual(petition.category, self.category)
    
    def test_list_petitions_aamil(self):
        """Test listing petitions as aamil"""
        # Create petition in aamil's Moze
        petition = Petition.objects.create(
            title='Test Petition',
            description='Test description',
            created_by=self.patient_user,
            category=self.category,
            moze=self.moze,
            priority='medium'
        )
        
        self.authenticate_user('aamil')
        url = reverse('araz_api:petition_list_create')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
    
    def test_assign_petition(self):
        """Test assigning petition to a user"""
        petition = Petition.objects.create(
            title='Test Petition',
            description='Test description',
            created_by=self.patient_user,
            category=self.category,
            priority='high'
        )
        
        self.authenticate_user('admin')
        url = reverse('araz_api:petition_assign', kwargs={'petition_id': petition.id})
        data = {
            'assigned_to_id': self.aamil_user.id,
            'notes': 'Please handle this urgent petition'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check assignment was created
        assignment = PetitionAssignment.objects.get(petition=petition)
        self.assertEqual(assignment.assigned_to, self.aamil_user)
        self.assertEqual(assignment.assigned_by, self.admin_user)
        self.assertTrue(assignment.is_active)
    
    def test_update_petition_status(self):
        """Test updating petition status"""
        petition = Petition.objects.create(
            title='Test Petition',
            description='Test description',
            created_by=self.patient_user,
            category=self.category,
            status='pending'
        )
        
        self.authenticate_user('admin')
        url = reverse('araz_api:petition_detail', kwargs={'pk': petition.id})
        data = {
            'status': 'resolved'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        petition.refresh_from_db()
        self.assertEqual(petition.status, 'resolved')
        self.assertIsNotNone(petition.resolved_at)
        
        # Check that update record was created
        self.assertTrue(petition.updates.exists())
    
    def test_search_petitions(self):
        """Test advanced search for petitions"""
        petition = Petition.objects.create(
            title='Infrastructure Issues',
            description='Problems with building infrastructure',
            created_by=self.patient_user,
            category=self.category,
            priority='high',
            status='pending'
        )
        
        self.authenticate_user('admin')
        url = reverse('araz_api:petition_search')
        data = {
            'query': 'infrastructure',
            'priority': 'high',
            'status': 'pending'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], petition.id)


class CategoryAPITests(ArazAPITestCase):
    """Tests for petition category API endpoints"""
    
    def test_list_categories(self):
        """Test listing petition categories"""
        self.authenticate_user('patient')
        url = reverse('araz_api:category_list_create')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], 'General Complaint')
    
    def test_create_category_admin(self):
        """Test creating category as admin"""
        self.authenticate_user('admin')
        url = reverse('araz_api:category_list_create')
        data = {
            'name': 'Facility Issues',
            'description': 'Issues related to facilities',
            'color': '#dc3545'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PetitionCategory.objects.count(), 2)
    
    def test_create_category_regular_user(self):
        """Test creating category as regular user (should fail)"""
        self.authenticate_user('patient')
        url = reverse('araz_api:category_list_create')
        data = {
            'name': 'New Category',
            'description': 'Test category'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CommentAPITests(ArazAPITestCase):
    """Tests for comment API endpoints"""
    
    def test_create_araz_comment(self):
        """Test creating Araz comment"""
        araz = DuaAraz.objects.create(
            patient_user=self.patient_user,
            patient_its_id='22222222',
            patient_name='Patient User',
            ailment='Test ailment',
            urgency_level='medium',
            request_type='consultation'
        )
        
        self.authenticate_user('patient')
        url = reverse('araz_api:araz_comments', kwargs={'araz_id': araz.id})
        data = {
            'content': 'Additional information about symptoms',
            'is_internal': False
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ArazComment.objects.count(), 1)
        
        comment = ArazComment.objects.first()
        self.assertEqual(comment.author, self.patient_user)
        self.assertEqual(comment.araz, araz)
    
    def test_create_petition_comment(self):
        """Test creating petition comment"""
        petition = Petition.objects.create(
            title='Test Petition',
            description='Test description',
            created_by=self.patient_user,
            category=self.category
        )
        
        self.authenticate_user('aamil')
        url = reverse('araz_api:petition_comments', kwargs={'petition_id': petition.id})
        data = {
            'content': 'We are looking into this issue',
            'is_internal': False
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PetitionComment.objects.count(), 1)


class StatisticsAPITests(ArazAPITestCase):
    """Tests for statistics API endpoints"""
    
    def setUp(self):
        super().setUp()
        # Create test data for statistics
        self.araz1 = DuaAraz.objects.create(
            patient_user=self.patient_user,
            patient_its_id='22222222',
            patient_name='Patient User',
            ailment='Test ailment 1',
            urgency_level='high',
            request_type='consultation',
            status='submitted'
        )
        
        self.araz2 = DuaAraz.objects.create(
            patient_user=self.patient_user,
            patient_its_id='22222222',
            patient_name='Patient User',
            ailment='Test ailment 2',
            urgency_level='emergency',
            request_type='emergency',
            status='completed'
        )
        
        self.petition1 = Petition.objects.create(
            title='Test Petition 1',
            description='Test description',
            created_by=self.patient_user,
            category=self.category,
            priority='high',
            status='pending'
        )
        
        self.petition2 = Petition.objects.create(
            title='Test Petition 2',
            description='Test description',
            created_by=self.patient_user,
            category=self.category,
            priority='medium',
            status='resolved'
        )
    
    def test_araz_statistics(self):
        """Test Araz statistics endpoint"""
        self.authenticate_user('admin')
        url = reverse('araz_api:araz_stats')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_araz'], 2)
        self.assertEqual(response.data['pending_araz'], 1)
        self.assertEqual(response.data['completed_araz'], 1)
        self.assertEqual(response.data['emergency_araz'], 1)
        
        # Check groupings
        self.assertIn('araz_by_type', response.data)
        self.assertIn('araz_by_urgency', response.data)
        self.assertIn('araz_by_status', response.data)
    
    def test_petition_statistics(self):
        """Test petition statistics endpoint"""
        self.authenticate_user('admin')
        url = reverse('araz_api:petition_stats')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_petitions'], 2)
        self.assertEqual(response.data['pending_petitions'], 1)
        self.assertEqual(response.data['resolved_petitions'], 1)
        
        # Check groupings
        self.assertIn('petitions_by_category', response.data)
        self.assertIn('petitions_by_priority', response.data)
        self.assertIn('petitions_by_status', response.data)
    
    def test_dashboard_data(self):
        """Test dashboard API endpoint"""
        self.authenticate_user('admin')
        url = reverse('araz_api:dashboard')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that all sections are present
        self.assertIn('araz_stats', response.data)
        self.assertIn('petition_stats', response.data)
        self.assertIn('recent_araz', response.data)
        self.assertIn('recent_petitions', response.data)
        self.assertIn('unread_notifications', response.data)
        self.assertIn('user_permissions', response.data)
        
        # Check user permissions for admin
        permissions = response.data['user_permissions']
        self.assertTrue(permissions['can_manage_araz'])
        self.assertTrue(permissions['can_manage_petitions'])
        self.assertTrue(permissions['can_create_categories'])


class NotificationAPITests(ArazAPITestCase):
    """Tests for notification API endpoints"""
    
    def test_list_notifications(self):
        """Test listing user notifications"""
        # Create test notification
        araz = DuaAraz.objects.create(
            patient_user=self.patient_user,
            patient_its_id='22222222',
            patient_name='Patient User',
            ailment='Test ailment',
            urgency_level='medium',
            request_type='consultation'
        )
        
        notification = ArazNotification.objects.create(
            araz=araz,
            recipient=self.patient_user,
            message='Your Araz request has been updated',
            notification_type='status_update'
        )
        
        self.authenticate_user('patient')
        url = reverse('araz_api:notifications')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], notification.id)
    
    def test_mark_notification_read(self):
        """Test marking notification as read"""
        araz = DuaAraz.objects.create(
            patient_user=self.patient_user,
            patient_its_id='22222222',
            patient_name='Patient User',
            ailment='Test ailment',
            urgency_level='medium',
            request_type='consultation'
        )
        
        notification = ArazNotification.objects.create(
            araz=araz,
            recipient=self.patient_user,
            message='Test notification',
            notification_type='status_update',
            is_read=False
        )
        
        self.authenticate_user('patient')
        url = reverse('araz_api:mark_notification_read', kwargs={'notification_id': notification.id})
        
        response = self.client.patch(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)
    
    def test_mark_all_notifications_read(self):
        """Test marking all notifications as read"""
        araz = DuaAraz.objects.create(
            patient_user=self.patient_user,
            patient_its_id='22222222',
            patient_name='Patient User',
            ailment='Test ailment',
            urgency_level='medium',
            request_type='consultation'
        )
        
        # Create multiple unread notifications
        for i in range(3):
            ArazNotification.objects.create(
                araz=araz,
                recipient=self.patient_user,
                message=f'Test notification {i}',
                notification_type='status_update',
                is_read=False
            )
        
        self.authenticate_user('patient')
        url = reverse('araz_api:mark_all_notifications_read')
        
        response = self.client.patch(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that all notifications are marked as read
        unread_count = ArazNotification.objects.filter(
            recipient=self.patient_user, 
            is_read=False
        ).count()
        self.assertEqual(unread_count, 0)


class PermissionTests(ArazAPITestCase):
    """Tests for API permissions and access control"""
    
    def test_patient_can_only_see_own_araz(self):
        """Test that patients can only see their own Araz requests"""
        # Create Araz for different users
        patient_araz = DuaAraz.objects.create(
            patient_user=self.patient_user,
            patient_its_id='22222222',
            patient_name='Patient User',
            ailment='Patient ailment',
            urgency_level='medium',
            request_type='consultation'
        )
        
        other_user = User.objects.create_user(
            username='other',
            email='other@test.com',
            password='testpass123',
            role='student'
        )
        
        other_araz = DuaAraz.objects.create(
            patient_user=other_user,
            patient_its_id='99999999',
            patient_name='Other User',
            ailment='Other ailment',
            urgency_level='medium',
            request_type='consultation'
        )
        
        self.authenticate_user('patient')
        url = reverse('araz_api:araz_list_create')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], patient_araz.id)
    
    def test_doctor_can_see_assigned_araz(self):
        """Test that doctors can see Araz assigned to them"""
        assigned_araz = DuaAraz.objects.create(
            patient_user=self.patient_user,
            patient_its_id='22222222',
            patient_name='Patient User',
            ailment='Test ailment',
            urgency_level='medium',
            request_type='consultation',
            assigned_doctor=self.doctor
        )
        
        self.authenticate_user('doctor')
        url = reverse('araz_api:araz_list_create')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
    
    def test_unauthorized_access_denied(self):
        """Test that unauthenticated requests are denied"""
        url = reverse('araz_api:araz_list_create')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class FilteringAndSearchTests(ArazAPITestCase):
    """Tests for filtering and search functionality"""
    
    def test_araz_filtering(self):
        """Test filtering Araz requests"""
        # Create Araz with different statuses
        DuaAraz.objects.create(
            patient_user=self.patient_user,
            patient_its_id='22222222',
            patient_name='Patient User',
            ailment='Pending ailment',
            urgency_level='medium',
            request_type='consultation',
            status='submitted'
        )
        
        DuaAraz.objects.create(
            patient_user=self.patient_user,
            patient_its_id='22222222',
            patient_name='Patient User',
            ailment='Completed ailment',
            urgency_level='low',
            request_type='follow_up',
            status='completed'
        )
        
        self.authenticate_user('patient')
        url = reverse('araz_api:araz_list_create')
        
        # Filter by status
        response = self.client.get(f'{url}?status=submitted')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        
        # Filter by urgency level
        response = self.client.get(f'{url}?urgency_level=medium')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
    
    def test_petition_search(self):
        """Test searching petitions"""
        Petition.objects.create(
            title='Water Supply Issues',
            description='Problems with water supply in the community',
            created_by=self.patient_user,
            category=self.category,
            priority='high'
        )
        
        self.authenticate_user('patient')
        url = reverse('araz_api:petition_list_create')
        
        # Search by title
        response = self.client.get(f'{url}?search=water')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
    
    def test_ordering(self):
        """Test ordering of results"""
        # Create multiple Araz with different dates
        old_araz = DuaAraz.objects.create(
            patient_user=self.patient_user,
            patient_its_id='22222222',
            patient_name='Patient User',
            ailment='Old ailment',
            urgency_level='medium',
            request_type='consultation'
        )
        old_araz.created_at = timezone.now() - timedelta(days=1)
        old_araz.save()
        
        new_araz = DuaAraz.objects.create(
            patient_user=self.patient_user,
            patient_its_id='22222222',
            patient_name='Patient User',
            ailment='New ailment',
            urgency_level='medium',
            request_type='consultation'
        )
        
        self.authenticate_user('patient')
        url = reverse('araz_api:araz_list_create')
        
        # Default ordering should be newest first
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['id'], new_araz.id)
        
        # Test explicit ordering
        response = self.client.get(f'{url}?ordering=created_at')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['id'], old_araz.id)