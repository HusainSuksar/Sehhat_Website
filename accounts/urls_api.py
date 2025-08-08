"""
URL patterns for Django Models API views
"""

from django.urls import path
from . import views_api

app_name = 'accounts_api'

urlpatterns = [
    # Django Models Dashboard
    path('django-dashboard/', views_api.django_dashboard_view, name='django_dashboard'),
    
    # Data Views
    path('users/', views_api.users_list_view, name='users_list'),
    path('doctors/', views_api.doctors_list_view, name='doctors_list'),
    path('hospitals/', views_api.hospitals_list_view, name='hospitals_list'),
    path('surveys/', views_api.surveys_list_view, name='surveys_list'),
    
    # AJAX API Endpoints
    path('api/search-users/', views_api.api_search_users, name='api_search_users'),
    path('api/search-doctors/', views_api.api_search_doctors, name='api_search_doctors'),
    path('api/sync-user-data/', views_api.api_sync_user_data, name='api_sync_user_data'),
    path('api/clear-user-cache/', views_api.api_clear_user_cache, name='api_clear_user_cache'),
    path('api/system-status/', views_api.api_system_status, name='api_system_status'),
    
    # System Configuration
    path('system-config/', views_api.system_configuration_view, name='system_configuration'),
]