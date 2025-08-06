"""
API URLs for the accounts app
"""
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from . import api_views

app_name = 'accounts_api'

urlpatterns = [
    # Authentication endpoints
    path('auth/login/', api_views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/login-session/', api_views.LoginAPIView.as_view(), name='login_session'),
    path('auth/logout/', api_views.LogoutAPIView.as_view(), name='logout'),
    
    # User profile endpoints
    path('me/', api_views.UserProfileAPIView.as_view(), name='user_profile'),
    path('change-password/', api_views.PasswordChangeAPIView.as_view(), name='change_password'),
    
    # User management endpoints
    path('users/', api_views.UserListCreateAPIView.as_view(), name='user_list_create'),
    path('users/<int:pk>/', api_views.UserDetailAPIView.as_view(), name='user_detail'),
    path('users/search/', api_views.UserSearchAPIView.as_view(), name='user_search'),
    
    # ITS synchronization endpoints
    path('its/sync/', api_views.ITSSyncAPIView.as_view(), name='its_sync'),
    path('its/bulk-sync/', api_views.bulk_its_sync_api, name='bulk_its_sync'),
    
    # Statistics and audit endpoints
    path('stats/', api_views.user_stats_api, name='user_stats'),
    path('audit-logs/', api_views.AuditLogListAPIView.as_view(), name='audit_logs'),
]