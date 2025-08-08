from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.urls import include

app_name = 'accounts'

urlpatterns = [
    # Authentication URLs
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='accounts:login'), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),

    # Dashboard URL
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Profile URLs
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.EditProfileView.as_view(), name='edit_profile'),
    
    # Password management
    path('password/change/', auth_views.PasswordChangeView.as_view(
        template_name='accounts/password_change.html',
        success_url='/accounts/profile/'
    ), name='password_change'),
    path('password/reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset.html'
    ), name='password_reset'),
    
    # User management (for admins) - redirects to modern user directory
    path('users/', views.user_directory, name='user_list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/edit/', views.UserEditView.as_view(), name='user_edit'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),
    
    # ITS ID verification
    path('verify-its/', views.VerifyITSView.as_view(), name='verify_its'),

    # Audit log (admin only) - using function-based view below instead

    # Permission management (admin only)
    path('permissions/', views.PermissionManagementView.as_view(), name='permission_management'),

    # Object permission management (admin only)
    path('object-permissions/', views.ObjectPermissionManagementView.as_view(), name='object_permission_management'),
    
    # Modern user directory
    path('user-directory/', views.user_directory, name='user_directory'),

    path('user-management/', views.user_management_view, name='user_management'),
    path('profile/', views.profile_view, name='profile'),
    path('audit-logs/', views.audit_logs_view, name='audit_logs'),
    path('test-its-api/', views.test_its_api_view, name='test_its_api'),
    path('its-login/', views.its_login_view, name='its_login'),
    
    # AJAX endpoints
    path('ajax/users/', views.ajax_users_list, name='ajax_users_list'),
    path('ajax/users/<int:user_id>/delete/', views.ajax_delete_user, name='ajax_delete_user'),
    
    # API URLs
    path('api/', include('accounts.api_urls')),
]