"""
Unit tests for the Survey API
"""
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
import json

from surveys.models import Survey, SurveyResponse, SurveyReminder, SurveyAnalytics

User = get_user_model()


class SurveyAPITestCase(APITestCase):
    """Base test case for Survey API tests"""
    
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
        
        self.doctor_user = User.objects.create_user(
            username='doctor_user',
            email='doctor@test.com',
            password='testpass123',
            role='doctor',
            first_name='Doctor',
            last_name='User'
        )
        
        self.student_user = User.objects.create_user(
            username='student_user',
            email='student@test.com',
            password='testpass123',
            role='student',
            first_name='Student',
            last_name='User'
        )
        
        # Create test survey
        self.sample_questions = [
            {
                "id": 1,
                "type": "text",
                "question": "What is your name?",
                "required": True,
                "options": []
            },
            {
                "id": 2,
                "type": "multiple_choice",
                "question": "How satisfied are you with our services?",
                "required": True,
                "options": ["Very Satisfied", "Satisfied", "Neutral", "Dissatisfied", "Very Dissatisfied"]
            },
            {
                "id": 3,
                "type": "rating",
                "question": "Rate our service quality (1-5)",
                "required": True,
                "options": ["1", "2", "3", "4", "5"]
            }
        ]
        
        self.survey = Survey.objects.create(
            title='Test Survey',
            description='Test survey for API testing',
            target_role='doctor',
            questions=self.sample_questions,
            created_by=self.admin_user,
            is_active=True,
            is_anonymous=False,
            allow_multiple_responses=False,
            show_results=True,
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=30)
        )
        
        # Create anonymous survey
        self.anonymous_survey = Survey.objects.create(
            title='Anonymous Survey',
            description='Anonymous survey for testing',
            target_role='all',
            questions=self.sample_questions,
            created_by=self.admin_user,
            is_active=True,
            is_anonymous=True,
            allow_multiple_responses=True,
            show_results=False
        )
        
        # Create survey response
        self.response = SurveyResponse.objects.create(
            survey=self.survey,
            respondent=self.doctor_user,
            answers={
                "1": "Dr. John Doe",
                "2": "Very Satisfied",
                "3": "5"
            },
            completion_time=120,
            is_complete=True
        )
        
        # Create survey reminder
        self.reminder = SurveyReminder.objects.create(
            survey=self.survey,
            user=self.doctor_user,
            reminder_count=1,
            max_reminders=3,
            is_active=True
        )
        
        # Create survey analytics
        self.analytics = SurveyAnalytics.objects.create(
            survey=self.survey,
            total_invitations=10,
            total_responses=1,
            total_complete_responses=1,
            response_rate=10.0,
            completion_rate=10.0,
            avg_completion_time=120.0
        )
        
        self.client = APIClient()


class SurveyAPITests(SurveyAPITestCase):
    """Test Survey CRUD operations"""
    
    def test_list_surveys_admin(self):
        """Test admin can list all surveys"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('survey_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_list_surveys_doctor(self):
        """Test doctor can see surveys targeted to them"""
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('survey_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should see the anonymous survey (all roles) and doctor-targeted survey
        self.assertEqual(len(response.data['results']), 2)
    
    def test_list_surveys_student(self):
        """Test student can see surveys targeted to them"""
        self.client.force_authenticate(user=self.student_user)
        url = reverse('survey_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only see the anonymous survey (all roles)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['target_role'], 'all')
    
    def test_create_survey_admin(self):
        """Test admin can create survey"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('survey_list_create')
        data = {
            'title': 'New Test Survey',
            'description': 'New survey for testing',
            'target_role': 'student',
            'questions': self.sample_questions,
            'is_active': True,
            'is_anonymous': False,
            'allow_multiple_responses': True,
            'show_results': True
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Survey.objects.count(), 3)
    
    def test_create_survey_student_forbidden(self):
        """Test student cannot create survey"""
        self.client.force_authenticate(user=self.student_user)
        url = reverse('survey_list_create')
        data = {
            'title': 'Forbidden Survey',
            'target_role': 'all',
            'questions': self.sample_questions
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_retrieve_survey_with_computed_fields(self):
        """Test retrieving survey with computed fields"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('survey_detail', kwargs={'pk': self.survey.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('questions_count', response.data)
        self.assertIn('responses_count', response.data)
        self.assertIn('is_available', response.data)
        self.assertIn('can_respond', response.data)
        self.assertEqual(response.data['questions_count'], 3)
    
    def test_update_survey_creator(self):
        """Test survey creator can update their survey"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('survey_detail', kwargs={'pk': self.survey.pk})
        data = {
            'title': 'Updated Survey Title',
            'description': 'Updated description'
        }
        
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.survey.refresh_from_db()
        self.assertEqual(self.survey.title, 'Updated Survey Title')
    
    def test_delete_survey_creator(self):
        """Test survey creator can delete their survey"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('survey_detail', kwargs={'pk': self.survey.pk})
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Survey.objects.filter(pk=self.survey.pk).count(), 0)


class SurveyResponseAPITests(SurveyAPITestCase):
    """Test Survey Response CRUD operations"""
    
    def test_list_responses_admin(self):
        """Test admin can list all responses"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('response_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_list_responses_respondent(self):
        """Test respondent can see their responses"""
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('response_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_response_authorized_user(self):
        """Test authorized user can create response"""
        # Create a new survey to avoid unique constraint
        new_survey = Survey.objects.create(
            title='New Survey for Response',
            description='Test survey',
            target_role='doctor',
            questions=self.sample_questions,
            created_by=self.admin_user,
            is_active=True
        )
        
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('response_list_create')
        data = {
            'survey_id': new_survey.id,
            'answers': {
                "1": "Test Answer",
                "2": "Satisfied",
                "3": "4"
            },
            'completion_time': 90,
            'is_complete': True
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SurveyResponse.objects.count(), 2)
    
    def test_response_with_computed_fields(self):
        """Test response includes computed fields"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('response_detail', kwargs={'pk': self.response.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('response_percentage', response.data)
        self.assertIn('time_taken_formatted', response.data)
        self.assertIn('answered_questions', response.data)
        self.assertIn('unanswered_questions', response.data)
    
    def test_update_response_respondent(self):
        """Test respondent can update their response"""
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('response_detail', kwargs={'pk': self.response.pk})
        data = {
            'answers': {
                "1": "Updated Name",
                "2": "Very Satisfied",
                "3": "5"
            },
            'is_complete': True
        }
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TakeSurveyAPITests(SurveyAPITestCase):
    """Test take survey functionality"""
    
    def test_get_survey_for_taking(self):
        """Test getting survey details for taking"""
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('take_survey_api', kwargs={'survey_id': self.survey.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('questions', response.data)
        self.assertIn('existing_response', response.data)
        self.assertEqual(len(response.data['questions']), 3)
    
    def test_take_survey_unauthorized_role(self):
        """Test unauthorized role cannot access survey"""
        self.client.force_authenticate(user=self.student_user)
        url = reverse('take_survey_api', kwargs={'survey_id': self.survey.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_submit_survey_response(self):
        """Test submitting survey response"""
        # Create a new survey to avoid existing response
        new_survey = Survey.objects.create(
            title='Survey for Submission',
            description='Test survey',
            target_role='doctor',
            questions=self.sample_questions,
            created_by=self.admin_user,
            is_active=True
        )
        
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('take_survey_api', kwargs={'survey_id': new_survey.pk})
        data = {
            'answers': {
                "1": "Test Response",
                "2": "Satisfied",
                "3": "4"
            },
            'completion_time': 150,
            'is_complete': True
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SurveyResponse.objects.count(), 2)
    
    def test_survey_not_available(self):
        """Test taking inactive survey"""
        inactive_survey = Survey.objects.create(
            title='Inactive Survey',
            description='Inactive survey',
            target_role='doctor',
            questions=self.sample_questions,
            created_by=self.admin_user,
            is_active=False
        )
        
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('take_survey_api', kwargs={'survey_id': inactive_survey.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SurveyReminderAPITests(SurveyAPITestCase):
    """Test Survey Reminder CRUD operations"""
    
    def test_list_reminders_creator(self):
        """Test survey creator can list reminders"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('reminder_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_reminder_creator(self):
        """Test survey creator can create reminder"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('reminder_list_create')
        data = {
            'survey_id': self.survey.id,
            'user_id': self.student_user.id,
            'max_reminders': 2,
            'is_active': True
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SurveyReminder.objects.count(), 2)
    
    def test_reminder_computed_fields(self):
        """Test reminder includes computed fields"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('reminder_detail', kwargs={'pk': self.reminder.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('can_send_reminder', response.data)
        self.assertIn('reminders_remaining', response.data)


class SurveyAnalyticsAPITests(SurveyAPITestCase):
    """Test Survey Analytics CRUD operations"""
    
    def test_list_analytics_creator(self):
        """Test survey creator can list analytics"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('analytics_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_analytics_computed_fields(self):
        """Test analytics includes computed fields"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('analytics_detail', kwargs={'pk': self.analytics.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('average_completion_time_formatted', response.data)
        self.assertIn('response_trend', response.data)
        self.assertIn('completion_trend', response.data)


class PublicSurveyAPITests(SurveyAPITestCase):
    """Test public survey access"""
    
    def test_list_public_surveys(self):
        """Test listing public anonymous surveys"""
        url = reverse('public_survey_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only see anonymous surveys
        self.assertEqual(len(response.data['results']), 1)
        self.assertTrue(response.data['results'][0]['is_anonymous'])
    
    def test_retrieve_public_survey(self):
        """Test retrieving public anonymous survey"""
        url = reverse('public_survey_detail', kwargs={'pk': self.anonymous_survey.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.anonymous_survey.id)
        self.assertTrue(response.data['is_anonymous'])


class SurveySearchAPITests(SurveyAPITestCase):
    """Test survey search functionality"""
    
    def test_search_surveys_by_title(self):
        """Test searching surveys by title"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('survey_search')
        response = self.client.get(url, {'title': 'Test'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertIn('Test', response.data['results'][0]['title'])
    
    def test_search_surveys_by_role(self):
        """Test searching surveys by target role"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('survey_search')
        response = self.client.get(url, {'target_role': 'doctor'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['target_role'], 'doctor')
    
    def test_search_surveys_by_status(self):
        """Test searching surveys by active status"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('survey_search')
        response = self.client.get(url, {'is_active': 'true'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)


class StatisticsAPITests(SurveyAPITestCase):
    """Test statistics API endpoints"""
    
    def test_survey_stats_admin(self):
        """Test admin can access survey statistics"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('survey_stats_api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_surveys', response.data)
        self.assertIn('active_surveys', response.data)
        self.assertIn('total_responses', response.data)
        self.assertIn('surveys_by_role', response.data)
        self.assertEqual(response.data['total_surveys'], 2)
    
    def test_response_stats_admin(self):
        """Test admin can access response statistics"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('response_stats_api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_responses', response.data)
        self.assertIn('complete_responses', response.data)
        self.assertIn('responses_by_role', response.data)
        self.assertIn('response_trend', response.data)
        self.assertEqual(response.data['total_responses'], 1)
    
    def test_question_analysis_creator(self):
        """Test question analysis for survey creator"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('question_analysis_api', kwargs={'survey_id': self.survey.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # 3 questions
        for question_data in response.data:
            self.assertIn('question_id', question_data)
            self.assertIn('question_text', question_data)
            self.assertIn('question_type', question_data)
            self.assertIn('answer_distribution', question_data)
    
    def test_question_analysis_unauthorized(self):
        """Test unauthorized access to question analysis"""
        self.client.force_authenticate(user=self.student_user)
        url = reverse('question_analysis_api', kwargs={'survey_id': self.survey.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_stats_unauthorized_user(self):
        """Test unauthorized user cannot access statistics"""
        self.client.force_authenticate(user=self.student_user)
        url = reverse('survey_stats_api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class DashboardAPITests(SurveyAPITestCase):
    """Test dashboard API functionality"""
    
    def test_dashboard_admin(self):
        """Test admin can access comprehensive dashboard"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('survey_dashboard_api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('survey_stats', response.data)
        self.assertIn('response_stats', response.data)
        self.assertIn('recent_surveys', response.data)
        self.assertIn('recent_responses', response.data)
    
    def test_dashboard_staff(self):
        """Test staff can access their dashboard"""
        self.client.force_authenticate(user=self.aamil_user)
        url = reverse('survey_dashboard_api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('survey_stats', response.data)
        self.assertIn('response_stats', response.data)
    
    def test_dashboard_regular_user(self):
        """Test regular user can access their limited dashboard"""
        self.client.force_authenticate(user=self.student_user)
        url = reverse('survey_dashboard_api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('my_responses', response.data)
        self.assertIn('available_surveys', response.data)
        self.assertIn('response_stats', response.data)


class PermissionTests(SurveyAPITestCase):
    """Test role-based permissions"""
    
    def test_creator_can_only_manage_their_surveys(self):
        """Test creator can only manage their own surveys"""
        # Create another admin and survey
        other_admin = User.objects.create_user(
            username='other_admin',
            role='badri_mahal_admin',
            password='testpass123'
        )
        other_survey = Survey.objects.create(
            title='Other Survey',
            description='Survey by other admin',
            target_role='all',
            questions=self.sample_questions,
            created_by=other_admin
        )
        
        self.client.force_authenticate(user=self.admin_user)
        
        # Should see own survey
        url = reverse('survey_list_create')
        response = self.client.get(url)
        survey_ids = [s['id'] for s in response.data['results']]
        self.assertIn(self.survey.id, survey_ids)
        
        # Admin can see all surveys, but let's test a non-admin user instead
        self.client.force_authenticate(user=self.aamil_user)
        
        # Aamil should not be able to modify other's survey
        url = reverse('survey_detail', kwargs={'pk': other_survey.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_role_targeting_access(self):
        """Test role-based access to surveys"""
        # Create doctor-only survey
        doctor_survey = Survey.objects.create(
            title='Doctor Only Survey',
            description='Survey for doctors only',
            target_role='doctor',
            questions=self.sample_questions,
            created_by=self.admin_user,
            is_active=True
        )
        
        # Doctor should see it
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('survey_list_create')
        response = self.client.get(url)
        survey_titles = [s['title'] for s in response.data['results']]
        self.assertIn('Doctor Only Survey', survey_titles)
        
        # Student should not see it
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(url)
        survey_titles = [s['title'] for s in response.data['results']]
        self.assertNotIn('Doctor Only Survey', survey_titles)
    
    def test_anonymous_survey_access(self):
        """Test anonymous survey access"""
        # Anonymous survey should be accessible to all roles
        self.client.force_authenticate(user=self.student_user)
        url = reverse('survey_list_create')
        response = self.client.get(url)
        
        anonymous_surveys = [s for s in response.data['results'] if s['is_anonymous']]
        self.assertEqual(len(anonymous_surveys), 1)
        self.assertEqual(anonymous_surveys[0]['title'], 'Anonymous Survey')


class ValidationTests(SurveyAPITestCase):
    """Test data validation"""
    
    def test_survey_question_validation(self):
        """Test survey question structure validation"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('survey_list_create')
        
        # Test invalid question (missing options for multiple choice)
        invalid_questions = [
            {
                "id": 1,
                "type": "multiple_choice",
                "question": "Choose an option",
                "required": True,
                "options": []  # Should have options
            }
        ]
        
        data = {
            'title': 'Invalid Survey',
            'target_role': 'all',
            'questions': invalid_questions
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_survey_date_validation(self):
        """Test survey date validation"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('survey_list_create')
        
        future_date = timezone.now() + timedelta(days=30)
        past_date = timezone.now() - timedelta(days=1)
        
        data = {
            'title': 'Invalid Date Survey',
            'target_role': 'all',
            'questions': self.sample_questions,
            'start_date': future_date.isoformat(),
            'end_date': past_date.isoformat()  # End before start
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_duplicate_response_prevention(self):
        """Test preventing duplicate responses when not allowed"""
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('take_survey_api', kwargs={'survey_id': self.survey.pk})
        
        # Try to submit another response (should fail due to existing response)
        data = {
            'answers': {
                "1": "Another Response",
                "2": "Satisfied",
                "3": "3"
            },
            'is_complete': True
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class FilteringAndSearchTests(SurveyAPITestCase):
    """Test filtering and search functionality"""
    
    def test_filter_surveys_by_role(self):
        """Test filtering surveys by target role"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('survey_list_create')
        
        # Filter by doctor role
        response = self.client.get(url, {'target_role': 'doctor'})
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['target_role'], 'doctor')
        
        # Filter by all role
        response = self.client.get(url, {'target_role': 'all'})
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['target_role'], 'all')
    
    def test_filter_surveys_by_status(self):
        """Test filtering surveys by active status"""
        # Create inactive survey
        Survey.objects.create(
            title='Inactive Survey',
            description='Inactive survey',
            target_role='all',
            questions=self.sample_questions,
            created_by=self.admin_user,
            is_active=False
        )
        
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('survey_list_create')
        
        # Filter by active
        response = self.client.get(url, {'is_active': 'true'})
        active_count = len([s for s in response.data['results'] if s['is_active']])
        self.assertEqual(active_count, 2)
        
        # Filter by inactive
        response = self.client.get(url, {'is_active': 'false'})
        inactive_count = len([s for s in response.data['results'] if not s['is_active']])
        self.assertEqual(inactive_count, 1)
    
    def test_search_surveys_by_title(self):
        """Test searching surveys by title"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('survey_list_create')
        
        response = self.client.get(url, {'search': 'Test Survey'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Search should find surveys containing "Test Survey" in title
        self.assertGreaterEqual(len(response.data['results']), 1)
        
        response = self.client.get(url, {'search': 'Nonexistent'})
        self.assertEqual(len(response.data['results']), 0)
    
    def test_filter_responses_by_completion(self):
        """Test filtering responses by completion status"""
        # Create incomplete response
        incomplete_survey = Survey.objects.create(
            title='Incomplete Survey',
            description='Survey for incomplete response',
            target_role='student',
            questions=self.sample_questions,
            created_by=self.admin_user,
            is_active=True
        )
        
        SurveyResponse.objects.create(
            survey=incomplete_survey,
            respondent=self.student_user,
            answers={"1": "Partial"},
            is_complete=False
        )
        
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('response_list_create')
        
        # Filter by complete
        response = self.client.get(url, {'is_complete': 'true'})
        complete_count = len([r for r in response.data['results'] if r['is_complete']])
        self.assertEqual(complete_count, 1)
        
        # Filter by incomplete
        response = self.client.get(url, {'is_complete': 'false'})
        incomplete_count = len([r for r in response.data['results'] if not r['is_complete']])
        self.assertEqual(incomplete_count, 1)