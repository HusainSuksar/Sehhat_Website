"""
API Views for the Survey app
"""
from rest_framework import generics, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from datetime import timedelta
import json

from .models import Survey, SurveyResponse, SurveyReminder, SurveyAnalytics
from .serializers import (
    SurveySerializer, SurveyCreateSerializer, SurveyResponseSerializer,
    SurveyResponseCreateSerializer, SurveyReminderSerializer, SurveyAnalyticsSerializer,
    SurveyStatsSerializer, ResponseStatsSerializer, QuestionAnalysisSerializer,
    SurveySearchSerializer
)


# Custom Permission Classes
class IsSurveyCreatorOrAdmin(permissions.BasePermission):
    """
    Permission for survey creators and admins to manage surveys
    """
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                (request.user.is_admin or 
                 request.user.role in ['aamil', 'moze_coordinator', 'badri_mahal_admin']))
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Admin can access everything
        if user.is_admin or user.is_superuser:
            return True
        
        # Creator can manage their own surveys
        if hasattr(obj, 'created_by'):
            return obj.created_by == user
        elif hasattr(obj, 'survey'):
            return obj.survey.created_by == user
        
        return False


class IsSurveyStaffOrAdmin(permissions.BasePermission):
    """
    Permission for survey staff (admin, aamil, coordinators) and admins
    """
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        
        # Admin can access everything
        if user.is_admin or user.is_superuser:
            return True
        
        # Staff roles can access surveys
        if user.role in ['aamil', 'moze_coordinator', 'badri_mahal_admin']:
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Admin can access everything
        if user.is_admin or user.is_superuser:
            return True
        
        # Staff roles can access surveys
        if user.role in ['aamil', 'moze_coordinator', 'badri_mahal_admin']:
            return True
        
        # For responses, users can access their own
        if hasattr(obj, 'respondent'):
            return obj.respondent == user
        elif hasattr(obj, 'user'):
            return obj.user == user
        
        return False


class CanRespondToSurvey(permissions.BasePermission):
    """
    Permission to check if user can respond to a survey
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated or request.method == 'GET'
    
    def has_object_permission(self, request, view, obj):
        # For anonymous surveys, allow access
        if hasattr(obj, 'survey') and obj.survey.is_anonymous:
            return True
        
        # For authenticated users, check role targeting
        if request.user.is_authenticated:
            survey = obj.survey if hasattr(obj, 'survey') else obj
            
            # Check role targeting
            if survey.target_role != 'all' and request.user.role != survey.target_role:
                return False
            
            # Check if survey is available
            if not survey.is_available():
                return False
            
            return True
        
        return False


# Access Control Mixins
class SurveyAccessMixin:
    """
    Mixin to filter survey data based on user role
    """
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            # Admin can see all surveys
            return Survey.objects.all()
        elif user.role in ['aamil', 'moze_coordinator', 'badri_mahal_admin']:
            # Staff can see all active surveys plus ones they created
            return Survey.objects.filter(
                Q(is_active=True) | Q(created_by=user)
            ).distinct()
        else:
            # Regular users can see surveys targeted to them or all users
            return Survey.objects.filter(
                is_active=True,
                target_role__in=['all', user.role]
            )


class ResponseAccessMixin:
    """
    Mixin to filter response data based on user role
    """
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            return SurveyResponse.objects.all()
        elif user.role in ['aamil', 'moze_coordinator', 'badri_mahal_admin']:
            # Staff can see responses for surveys they created
            return SurveyResponse.objects.filter(survey__created_by=user)
        else:
            # Users can see their own responses
            return SurveyResponse.objects.filter(respondent=user)


# Survey API Views
class SurveyListCreateAPIView(SurveyAccessMixin, generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['target_role', 'is_active', 'is_anonymous', 'allow_multiple_responses', 'show_results']
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'created_at', 'start_date', 'end_date']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SurveyCreateSerializer
        return SurveySerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsSurveyCreatorOrAdmin()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class SurveyDetailAPIView(SurveyAccessMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SurveySerializer
    permission_classes = [IsSurveyStaffOrAdmin]
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsSurveyCreatorOrAdmin()]
        return super().get_permissions()


# Survey Response API Views
class SurveyResponseListCreateAPIView(ResponseAccessMixin, generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['survey', 'is_complete', 'respondent']
    search_fields = ['answers']
    ordering_fields = ['created_at', 'completion_time']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SurveyResponseCreateSerializer
        return SurveyResponseSerializer
    
    def perform_create(self, serializer):
        # Set respondent to current user for authenticated responses
        survey = serializer.validated_data.get('survey')
        
        # For anonymous surveys, don't set respondent
        if survey and not survey.is_anonymous:
            serializer.save(respondent=self.request.user)
        else:
            serializer.save()
        
        # Update analytics if exists
        self._update_survey_analytics(survey)
    
    def _update_survey_analytics(self, survey):
        """Update survey analytics after response creation"""
        try:
            analytics, created = SurveyAnalytics.objects.get_or_create(survey=survey)
            analytics.total_responses = survey.responses.count()
            analytics.total_complete_responses = survey.responses.filter(is_complete=True).count()
            
            # Calculate average completion time
            avg_time = survey.responses.filter(
                completion_time__isnull=False
            ).aggregate(avg=Avg('completion_time'))['avg']
            if avg_time:
                analytics.avg_completion_time = avg_time
            
            analytics.calculate_rates()
        except Exception:
            # Don't fail response creation if analytics update fails
            pass


class SurveyResponseDetailAPIView(ResponseAccessMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SurveyResponseSerializer
    permission_classes = [IsSurveyStaffOrAdmin]
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH']:
            # Users can update their own responses
            return [permissions.IsAuthenticated()]
        elif self.request.method == 'DELETE':
            return [IsSurveyCreatorOrAdmin()]
        return super().get_permissions()


# Survey Reminder API Views
class SurveyReminderListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = SurveyReminderSerializer
    permission_classes = [IsSurveyCreatorOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['survey', 'has_responded', 'is_active']
    ordering_fields = ['created_at', 'last_reminder_sent']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            return SurveyReminder.objects.all()
        else:
            # Users can see reminders for surveys they created
            return SurveyReminder.objects.filter(survey__created_by=user)
    
    def perform_create(self, serializer):
        serializer.save()


class SurveyReminderDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SurveyReminderSerializer
    permission_classes = [IsSurveyCreatorOrAdmin]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            return SurveyReminder.objects.all()
        else:
            return SurveyReminder.objects.filter(survey__created_by=user)


# Survey Analytics API Views
class SurveyAnalyticsListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = SurveyAnalyticsSerializer
    permission_classes = [IsSurveyStaffOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['survey']
    ordering_fields = ['last_calculated', 'response_rate', 'completion_rate']
    ordering = ['-last_calculated']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            return SurveyAnalytics.objects.all()
        else:
            # Users can see analytics for surveys they created
            return SurveyAnalytics.objects.filter(survey__created_by=user)
    
    def perform_create(self, serializer):
        analytics = serializer.save()
        analytics.calculate_rates()


class SurveyAnalyticsDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SurveyAnalyticsSerializer
    permission_classes = [IsSurveyStaffOrAdmin]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            return SurveyAnalytics.objects.all()
        else:
            return SurveyAnalytics.objects.filter(survey__created_by=user)


# Search API Views
class SurveySearchAPIView(generics.ListAPIView):
    serializer_class = SurveySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering = ['-created_at']
    
    def get_queryset(self):
        # Use SurveyAccessMixin logic
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            queryset = Survey.objects.all()
        elif user.role in ['aamil', 'moze_coordinator', 'badri_mahal_admin']:
            queryset = Survey.objects.filter(
                Q(is_active=True) | Q(created_by=user)
            ).distinct()
        else:
            queryset = Survey.objects.filter(
                is_active=True,
                target_role__in=['all', user.role]
            )
        
        # Apply search filters from query params
        title = self.request.query_params.get('title')
        target_role = self.request.query_params.get('target_role')
        created_by = self.request.query_params.get('created_by')
        is_active = self.request.query_params.get('is_active')
        is_anonymous = self.request.query_params.get('is_anonymous')
        start_date_from = self.request.query_params.get('start_date_from')
        start_date_to = self.request.query_params.get('start_date_to')
        end_date_from = self.request.query_params.get('end_date_from')
        end_date_to = self.request.query_params.get('end_date_to')
        has_responses = self.request.query_params.get('has_responses')
        
        if title:
            queryset = queryset.filter(title__icontains=title)
        if target_role:
            queryset = queryset.filter(target_role=target_role)
        if created_by:
            queryset = queryset.filter(
                Q(created_by__first_name__icontains=created_by) |
                Q(created_by__last_name__icontains=created_by) |
                Q(created_by__username__icontains=created_by)
            )
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        if is_anonymous is not None:
            queryset = queryset.filter(is_anonymous=is_anonymous.lower() == 'true')
        if start_date_from:
            queryset = queryset.filter(start_date__gte=start_date_from)
        if start_date_to:
            queryset = queryset.filter(start_date__lte=start_date_to)
        if end_date_from:
            queryset = queryset.filter(end_date__gte=end_date_from)
        if end_date_to:
            queryset = queryset.filter(end_date__lte=end_date_to)
        if has_responses is not None:
            has_resp = has_responses.lower() == 'true'
            if has_resp:
                queryset = queryset.filter(responses__isnull=False).distinct()
            else:
                queryset = queryset.filter(responses__isnull=True)
        
        return queryset.distinct().order_by('-created_at')


# Public Survey Views (for anonymous access)
class PublicSurveyListAPIView(generics.ListAPIView):
    """
    Public endpoint for anonymous surveys
    """
    serializer_class = SurveySerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Survey.objects.filter(
            is_active=True,
            is_anonymous=True
        )


class PublicSurveyDetailAPIView(generics.RetrieveAPIView):
    """
    Public endpoint for viewing anonymous surveys
    """
    serializer_class = SurveySerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return Survey.objects.filter(
            is_active=True,
            is_anonymous=True
        )


# Take Survey API View
@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def take_survey_api(request, survey_id):
    """
    API endpoint for taking a survey
    """
    try:
        survey = Survey.objects.get(id=survey_id)
    except Survey.DoesNotExist:
        return Response(
            {'error': 'Survey not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if user can access this survey
    user = request.user
    
    # Check role targeting
    if survey.target_role != 'all' and user.role != survey.target_role:
        return Response(
            {'error': 'You are not authorized to access this survey'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check if survey is available
    if not survey.is_available():
        return Response(
            {'error': 'This survey is not currently available'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if request.method == 'GET':
        # Return survey details for taking
        serializer = SurveySerializer(survey, context={'request': request})
        
        # Check if user has already responded
        existing_response = None
        if not survey.is_anonymous:
            try:
                existing_response = SurveyResponse.objects.get(
                    survey=survey, respondent=user
                )
            except SurveyResponse.DoesNotExist:
                pass
        
        data = serializer.data
        data['existing_response'] = None
        
        if existing_response:
            if not survey.allow_multiple_responses:
                data['message'] = 'You have already responded to this survey'
                data['existing_response'] = SurveyResponseSerializer(
                    existing_response, context={'request': request}
                ).data
            else:
                data['existing_response'] = SurveyResponseSerializer(
                    existing_response, context={'request': request}
                ).data
        
        return Response(data)
    
    elif request.method == 'POST':
        # Submit survey response
        data = request.data.copy()
        data['survey_id'] = survey_id
        
        # For non-anonymous surveys, set respondent
        if not survey.is_anonymous:
            data['respondent_id'] = user.id
        
        serializer = SurveyResponseCreateSerializer(data=data)
        if serializer.is_valid():
            response = serializer.save()
            
            # Update analytics
            try:
                analytics, created = SurveyAnalytics.objects.get_or_create(survey=survey)
                analytics.total_responses = survey.responses.count()
                analytics.total_complete_responses = survey.responses.filter(is_complete=True).count()
                
                # Calculate average completion time
                avg_time = survey.responses.filter(
                    completion_time__isnull=False
                ).aggregate(avg=Avg('completion_time'))['avg']
                if avg_time:
                    analytics.avg_completion_time = avg_time
                
                analytics.calculate_rates()
            except Exception:
                pass
            
            return Response(
                SurveyResponseSerializer(response, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Statistics API Views
@api_view(['GET'])
@permission_classes([IsSurveyStaffOrAdmin])
def survey_stats_api(request):
    """Get survey statistics"""
    user = request.user
    
    # Base queryset based on user role
    if user.is_admin or user.is_superuser:
        surveys = Survey.objects.all()
        responses = SurveyResponse.objects.all()
    elif user.role in ['aamil', 'moze_coordinator', 'badri_mahal_admin']:
        surveys = Survey.objects.filter(Q(created_by=user) | Q(is_active=True))
        responses = SurveyResponse.objects.filter(survey__created_by=user)
    else:
        surveys = Survey.objects.filter(created_by=user)
        responses = SurveyResponse.objects.filter(survey__created_by=user)
    
    # Calculate stats
    total_surveys = surveys.count()
    active_surveys = surveys.filter(is_active=True).count()
    total_responses = responses.count()
    total_complete_responses = responses.filter(is_complete=True).count()
    
    # Calculate average rates
    analytics = SurveyAnalytics.objects.filter(survey__in=surveys)
    avg_response_rate = analytics.aggregate(avg=Avg('response_rate'))['avg'] or 0
    avg_completion_rate = analytics.aggregate(avg=Avg('completion_rate'))['avg'] or 0
    
    # Surveys by role
    surveys_by_role = dict(
        surveys.values_list('target_role')
        .annotate(count=Count('id'))
    )
    
    # Surveys by status
    now = timezone.now()
    surveys_by_status = {
        'active': surveys.filter(is_active=True).count(),
        'inactive': surveys.filter(is_active=False).count(),
        'upcoming': surveys.filter(start_date__gt=now).count(),
        'expired': surveys.filter(end_date__lt=now).count(),
    }
    
    # Recent surveys
    recent_surveys = list(
        surveys.order_by('-created_at')[:5]
        .values('id', 'title', 'created_at')
    )
    
    # Top performing surveys
    top_performing = list(
        surveys.annotate(response_count=Count('responses'))
        .order_by('-response_count')[:5]
        .values('id', 'title', 'response_count')
    )
    
    stats = {
        'total_surveys': total_surveys,
        'active_surveys': active_surveys,
        'total_responses': total_responses,
        'total_complete_responses': total_complete_responses,
        'average_response_rate': round(avg_response_rate, 2),
        'average_completion_rate': round(avg_completion_rate, 2),
        'surveys_by_role': surveys_by_role,
        'surveys_by_status': surveys_by_status,
        'recent_surveys': recent_surveys,
        'top_performing_surveys': top_performing
    }
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([IsSurveyStaffOrAdmin])
def response_stats_api(request):
    """Get response statistics"""
    user = request.user
    
    # Base queryset based on user role
    if user.is_admin or user.is_superuser:
        responses = SurveyResponse.objects.all()
    elif user.role in ['aamil', 'moze_coordinator', 'badri_mahal_admin']:
        responses = SurveyResponse.objects.filter(survey__created_by=user)
    else:
        responses = SurveyResponse.objects.filter(survey__created_by=user)
    
    # Calculate stats
    total_responses = responses.count()
    complete_responses = responses.filter(is_complete=True).count()
    partial_responses = total_responses - complete_responses
    anonymous_responses = responses.filter(respondent__isnull=True).count()
    
    # Responses by role
    responses_by_role = dict(
        responses.exclude(respondent__isnull=True)
        .values_list('respondent__role')
        .annotate(count=Count('id'))
    )
    
    # Responses by survey
    responses_by_survey = dict(
        responses.values_list('survey__title')
        .annotate(count=Count('id'))
    )
    
    # Average completion time
    avg_completion_time = responses.filter(
        completion_time__isnull=False
    ).aggregate(avg=Avg('completion_time'))['avg'] or 0
    
    # Response trend (last 7 days)
    response_trend = []
    for i in range(7):
        date = timezone.now().date() - timedelta(days=i)
        count = responses.filter(created_at__date=date).count()
        response_trend.append({
            'date': date.isoformat(),
            'count': count
        })
    response_trend.reverse()
    
    stats = {
        'total_responses': total_responses,
        'complete_responses': complete_responses,
        'partial_responses': partial_responses,
        'anonymous_responses': anonymous_responses,
        'responses_by_role': responses_by_role,
        'responses_by_survey': responses_by_survey,
        'average_completion_time': round(avg_completion_time, 2),
        'response_trend': response_trend
    }
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([IsSurveyStaffOrAdmin])
def question_analysis_api(request, survey_id):
    """Get detailed analysis for survey questions"""
    try:
        survey = Survey.objects.get(id=survey_id)
    except Survey.DoesNotExist:
        return Response(
            {'error': 'Survey not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check permissions
    user = request.user
    if not (user.is_admin or user.is_superuser or survey.created_by == user):
        return Response(
            {'error': 'Permission denied'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    responses = survey.responses.all()
    total_responses = responses.count()
    
    question_analysis = []
    
    for question in survey.questions:
        question_id = str(question['id'])
        question_text = question['question']
        question_type = question['type']
        
        # Get answers for this question
        answers = []
        for response in responses:
            answer = response.answers.get(question_id)
            if answer is not None and answer != '':
                answers.append(answer)
        
        answered_count = len(answers)
        response_rate = (answered_count / total_responses * 100) if total_responses > 0 else 0
        
        # Calculate answer distribution
        answer_distribution = {}
        if answers:
            from collections import Counter
            if question_type in ['multiple_choice', 'dropdown', 'boolean']:
                answer_distribution = dict(Counter(answers))
            elif question_type == 'rating':
                # For rating questions, group by rating value
                answer_distribution = dict(Counter(answers))
            elif question_type == 'checkbox':
                # For checkbox questions, count each selected option
                all_selections = []
                for answer in answers:
                    if isinstance(answer, list):
                        all_selections.extend(answer)
                    elif isinstance(answer, str):
                        # Handle comma-separated values
                        all_selections.extend([a.strip() for a in answer.split(',')])
                answer_distribution = dict(Counter(all_selections))
            else:
                # For text questions, just count responses
                answer_distribution = {'responses': len(answers)}
        
        # Calculate most common answer
        most_common_answer = None
        if answer_distribution:
            most_common_answer = max(answer_distribution, key=answer_distribution.get)
        
        # Calculate average rating for rating questions
        average_rating = None
        if question_type == 'rating' and answers:
            try:
                numeric_answers = [float(a) for a in answers if str(a).replace('.', '').isdigit()]
                if numeric_answers:
                    average_rating = sum(numeric_answers) / len(numeric_answers)
            except (ValueError, TypeError):
                pass
        
        question_analysis.append({
            'question_id': int(question_id),
            'question_text': question_text,
            'question_type': question_type,
            'total_responses': answered_count,
            'response_rate': round(response_rate, 2),
            'answer_distribution': answer_distribution,
            'most_common_answer': most_common_answer,
            'average_rating': round(average_rating, 2) if average_rating else None
        })
    
    return Response(question_analysis)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def survey_dashboard_api(request):
    """Get comprehensive dashboard data for survey app"""
    user = request.user
    
    if not user.is_authenticated:
        raise PermissionDenied("Authentication required.")
    
    dashboard_data = {}
    
    try:
        # Role-specific dashboard data
        if user.is_admin or user.role in ['aamil', 'moze_coordinator', 'badri_mahal_admin']:
            # Staff dashboard - compute stats directly
            if user.is_admin or user.is_superuser:
                surveys = Survey.objects.all()
                responses = SurveyResponse.objects.all()
                analytics = SurveyAnalytics.objects.all()
            else:
                surveys = Survey.objects.filter(Q(created_by=user) | Q(is_active=True))
                responses = SurveyResponse.objects.filter(survey__created_by=user)
                analytics = SurveyAnalytics.objects.filter(survey__created_by=user)
            
            # Survey stats
            dashboard_data['survey_stats'] = {
                'total_surveys': surveys.count(),
                'active_surveys': surveys.filter(is_active=True).count(),
                'my_surveys': surveys.filter(created_by=user).count(),
                'average_response_rate': round(
                    analytics.aggregate(avg=Avg('response_rate'))['avg'] or 0, 2
                ),
                'surveys_needing_attention': surveys.filter(
                    end_date__lt=timezone.now() + timedelta(days=7),
                    end_date__gt=timezone.now()
                ).count()
            }
            
            # Response stats
            dashboard_data['response_stats'] = {
                'total_responses': responses.count(),
                'complete_responses': responses.filter(is_complete=True).count(),
                'recent_responses': responses.filter(
                    created_at__gte=timezone.now() - timedelta(days=7)
                ).count(),
                'average_completion_time': round(
                    responses.filter(completion_time__isnull=False).aggregate(
                        avg=Avg('completion_time')
                    )['avg'] or 0, 2
                )
            }
            
            # Recent activities
            dashboard_data['recent_surveys'] = SurveySerializer(
                surveys.order_by('-created_at')[:5],
                many=True, context={'request': request}
            ).data
            
            dashboard_data['recent_responses'] = SurveyResponseSerializer(
                responses.order_by('-created_at')[:5],
                many=True, context={'request': request}
            ).data
            
        else:
            # Regular user dashboard
            user_responses = SurveyResponse.objects.filter(respondent=user)
            available_surveys = Survey.objects.filter(
                is_active=True,
                target_role__in=['all', user.role]
            )
            
            dashboard_data['my_responses'] = SurveyResponseSerializer(
                user_responses.order_by('-created_at')[:10],
                many=True, context={'request': request}
            ).data
            
            dashboard_data['available_surveys'] = SurveySerializer(
                available_surveys.order_by('-created_at')[:5],
                many=True, context={'request': request}
            ).data
            
            dashboard_data['response_stats'] = {
                'total_responses': user_responses.count(),
                'completed_responses': user_responses.filter(is_complete=True).count(),
                'average_completion_time': round(
                    user_responses.filter(completion_time__isnull=False).aggregate(
                        avg=Avg('completion_time')
                    )['avg'] or 0, 2
                )
            }
        
        # Common data for all users
        dashboard_data['available_surveys_count'] = Survey.objects.filter(
            is_active=True,
            target_role__in=['all', user.role]
        ).count()
        dashboard_data['total_surveys_count'] = Survey.objects.filter(is_active=True).count()
        
    except Exception as e:
        dashboard_data['error'] = str(e)
    
    return Response(dashboard_data)