from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin


class RoleBasedAccessMiddleware(MiddlewareMixin):
    """Middleware to enforce role-based access control"""
    
    def process_request(self, request):
        # Skip middleware for admin, login, logout, and static files
        if (request.path.startswith('/admin/') or 
            request.path.startswith('/accounts/login/') or
            request.path.startswith('/accounts/logout/') or
            request.path.startswith('/static/') or
            request.path.startswith('/media/')):
            return None
        
        # Skip for unauthenticated users on public paths
        if not request.user.is_authenticated:
            return None
        
        # Allow access based on role and path
        user = request.user
        path = request.path
        
        # Define role-based path restrictions
        role_paths = {
            'aamil': ['/moze/', '/photos/', '/'],
            'moze_coordinator': ['/moze/', '/doctordirectory/', '/photos/', '/surveys/', '/'],
            'doctor': ['/mahalshifa/', '/doctordirectory/', '/'],
            'student': ['/students/', '/araz/', '/'],
            'badri_mahal_admin': ['/'],  # Admin has access to everything
        }
        
        # Admin and superuser bypass all restrictions
        if user.is_admin or user.is_superuser:
            return None
        
        # Check if user's role allows access to the current path
        allowed_paths = role_paths.get(user.role, [])
        
        # Check if current path starts with any allowed path
        path_allowed = any(path.startswith(allowed_path) for allowed_path in allowed_paths)
        
        if not path_allowed and path != '/':
            messages.error(request, "You don't have permission to access this page.")
            return redirect('dashboard')
        
        return None