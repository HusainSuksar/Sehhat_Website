"""
URL Configuration for the Survey API
"""
from django.urls import path
from . import api_views

urlpatterns = [
    # Dashboard
    path('dashboard/', api_views.survey_dashboard_api, name='survey_dashboard_api'),
    
    # Survey Management
    path('surveys/', api_views.SurveyListCreateAPIView.as_view(), name='survey_list_create'),
    path('surveys/<int:pk>/', api_views.SurveyDetailAPIView.as_view(), name='survey_detail'),
    path('surveys/search/', api_views.SurveySearchAPIView.as_view(), name='survey_search'),
    
    # Survey Taking
    path('surveys/<int:survey_id>/take/', api_views.take_survey_api, name='take_survey_api'),
    
    # Survey Responses
    path('responses/', api_views.SurveyResponseListCreateAPIView.as_view(), name='response_list_create'),
    path('responses/<int:pk>/', api_views.SurveyResponseDetailAPIView.as_view(), name='response_detail'),
    
    # Survey Reminders
    path('reminders/', api_views.SurveyReminderListCreateAPIView.as_view(), name='reminder_list_create'),
    path('reminders/<int:pk>/', api_views.SurveyReminderDetailAPIView.as_view(), name='reminder_detail'),
    
    # Survey Analytics
    path('analytics/', api_views.SurveyAnalyticsListCreateAPIView.as_view(), name='analytics_list_create'),
    path('analytics/<int:pk>/', api_views.SurveyAnalyticsDetailAPIView.as_view(), name='analytics_detail'),
    
    # Question Analysis
    path('surveys/<int:survey_id>/analysis/', api_views.question_analysis_api, name='question_analysis_api'),
    
    # Statistics
    path('stats/surveys/', api_views.survey_stats_api, name='survey_stats_api'),
    path('stats/responses/', api_views.response_stats_api, name='response_stats_api'),
    
    # Public Survey Access (Anonymous)
    path('public/surveys/', api_views.PublicSurveyListAPIView.as_view(), name='public_survey_list'),
    path('public/surveys/<int:pk>/', api_views.PublicSurveyDetailAPIView.as_view(), name='public_survey_detail'),
]