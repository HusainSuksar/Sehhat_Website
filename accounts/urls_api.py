"""
URL patterns for API-integrated views
"""

from django.urls import path
from . import views_api

app_name = 'accounts_api'

urlpatterns = [
    # Hybrid Dashboard
    path('hybrid-dashboard/', views_api.hybrid_dashboard_view, name='hybrid_dashboard'),
    
    # Hybrid Data Views
    path('hybrid-doctors/', views_api.hybrid_doctors_view, name='hybrid_doctors'),
    path('hybrid-hospitals/', views_api.hybrid_hospitals_view, name='hybrid_hospitals'),
    path('hybrid-surveys/', views_api.hybrid_surveys_view, name='hybrid_surveys'),
    
    # AJAX API Endpoints
    path('api/search-doctors/', views_api.api_search_doctors, name='api_search_doctors'),
    path('api/refresh-cache/', views_api.api_refresh_cache, name='api_refresh_cache'),
    path('api/system-status/', views_api.api_system_status, name='api_system_status'),
    
    # API Configuration
    path('api-config/', views_api.api_configuration_view, name='api_configuration'),
]