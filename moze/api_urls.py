"""
URL Configuration for the Moze API
"""
from django.urls import path
from . import api_views

urlpatterns = [
    # Dashboard
    path('dashboard/', api_views.moze_dashboard_api, name='moze_dashboard_api'),
    
    # Moze Management
    path('mozes/', api_views.MozeListCreateAPIView.as_view(), name='moze_list_create'),
    path('mozes/<int:pk>/', api_views.MozeDetailAPIView.as_view(), name='moze_detail'),
    path('mozes/search/', api_views.MozeSearchAPIView.as_view(), name='moze_search'),
    
    # Moze Settings
    path('settings/', api_views.MozeSettingsListCreateAPIView.as_view(), name='moze_settings_list_create'),
    path('settings/<int:pk>/', api_views.MozeSettingsDetailAPIView.as_view(), name='moze_settings_detail'),
    
    # Umoor Sehhat Team Management
    path('teams/', api_views.UmoorSehhatTeamListCreateAPIView.as_view(), name='team_list_create'),
    path('teams/<int:pk>/', api_views.UmoorSehhatTeamDetailAPIView.as_view(), name='team_detail'),
    path('teams/search/', api_views.TeamSearchAPIView.as_view(), name='team_search'),
    
    # Comments System
    path('comments/', api_views.MozeCommentListCreateAPIView.as_view(), name='comment_list_create'),
    path('comments/<int:pk>/', api_views.MozeCommentDetailAPIView.as_view(), name='comment_detail'),
    
    # Statistics
    path('stats/mozes/', api_views.moze_stats_api, name='moze_stats_api'),
    path('stats/teams/', api_views.team_stats_api, name='team_stats_api'),
]