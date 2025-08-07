"""
API URLs for the Araz app
"""
from django.urls import path
from . import api_views

app_name = 'araz_api'

urlpatterns = [
    # Dashboard
    path('dashboard/', api_views.araz_dashboard_api, name='dashboard'),
    
    # DuaAraz endpoints
    path('araz/', api_views.DuaArazListCreateAPIView.as_view(), name='araz_list_create'),
    path('araz/<int:pk>/', api_views.DuaArazDetailAPIView.as_view(), name='araz_detail'),
    path('araz/search/', api_views.DuaArazSearchAPIView.as_view(), name='araz_search'),
    
    # Araz comments
    path('araz/<int:araz_id>/comments/', api_views.ArazCommentListCreateAPIView.as_view(), name='araz_comments'),
    
    # Petition endpoints
    path('petitions/', api_views.PetitionListCreateAPIView.as_view(), name='petition_list_create'),
    path('petitions/<int:pk>/', api_views.PetitionDetailAPIView.as_view(), name='petition_detail'),
    path('petitions/search/', api_views.PetitionSearchAPIView.as_view(), name='petition_search'),
    
    # Petition comments
    path('petitions/<int:petition_id>/comments/', api_views.PetitionCommentListCreateAPIView.as_view(), name='petition_comments'),
    
    # Petition assignments
    path('petitions/<int:petition_id>/assign/', api_views.PetitionAssignmentCreateAPIView.as_view(), name='petition_assign'),
    
    # Categories
    path('categories/', api_views.PetitionCategoryListCreateAPIView.as_view(), name='category_list_create'),
    path('categories/<int:pk>/', api_views.PetitionCategoryDetailAPIView.as_view(), name='category_detail'),
    
    # Statistics
    path('stats/araz/', api_views.araz_stats_api, name='araz_stats'),
    path('stats/petitions/', api_views.petition_stats_api, name='petition_stats'),
    
    # Notifications
    path('notifications/', api_views.ArazNotificationListAPIView.as_view(), name='notifications'),
    path('notifications/<int:notification_id>/read/', api_views.mark_notification_read_api, name='mark_notification_read'),
    path('notifications/mark-all-read/', api_views.mark_all_notifications_read_api, name='mark_all_notifications_read'),
]