"""
Django Models API Views
Demonstrates Django-only approach with optional user data API integration
"""

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.contrib import messages

# Import services - try multiple import strategies
try:
    # Try direct import first
    from services.data_service import data_service
    from services.api_service import user_api_service
except ImportError:
    # Fallback: Add project root to path and import
    import sys
    import os
    from pathlib import Path
    
    # Get the project root directory (where manage.py is located)
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    
    try:
        from services.data_service import data_service
        from services.api_service import user_api_service
    except ImportError as e:
        # Final fallback: create mock services for development
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Could not import services: {e}")
        
        # Create mock objects to prevent crashes
        class MockUserAPIService:
            def get_api_status(self):
                return {'is_available': False, 'base_url': 'mock', 'last_checked': 'now', 'cache_timeout': 300, 'service_type': 'mock'}
            def get_user_by_its_id(self, its_id):
                return None
            def search_users(self, query, filters=None):
                return []
            def clear_user_cache(self, its_id=None):
                pass
        
        class MockDataService:
            def get_dashboard_statistics(self):
                return {'users': 0, 'doctors': 0, 'hospitals': 0, 'surveys': 0}
            def get_all_users(self, role=None, is_active=True):
                return []
            def get_all_doctors(self, specialty=None, is_verified=None):
                return []
            def get_all_hospitals(self, is_active=True):
                return []
            def get_all_surveys(self, is_active=True):
                return []
            def get_system_status(self):
                return {'database_status': 'connected', 'data_source': 'mock'}
            def search_users(self, query, role=None):
                return []
            def search_doctors(self, query):
                return []
            def get_recent_activities(self, limit=10):
                return []
        
        user_api_service = MockUserAPIService()
        data_service = MockDataService()


@login_required
def django_dashboard_view(request):
    """
    Dashboard showing Django models data with optional user API integration
    """
    # Get Django models statistics
    stats = data_service.get_dashboard_statistics()
    
    # Get system status
    system_status = data_service.get_system_status()
    
    # Get user API status
    user_api_status = user_api_service.get_api_status()
    
    # Get recent activities
    recent_activities = data_service.get_recent_activities(limit=5)
    
    context = {
        'stats': stats,
        'system_status': system_status,
        'user_api_status': user_api_status,
        'recent_activities': recent_activities,
        'page_title': 'Django Models Dashboard',
    }
    
    return render(request, 'accounts/django_dashboard.html', context)


@login_required
def users_list_view(request):
    """
    Users listing from Django models with search functionality
    """
    role = request.GET.get('role', '')
    search_query = request.GET.get('q', '')
    
    if search_query:
        users = data_service.search_users(search_query, role if role else None)
    else:
        users = data_service.get_all_users(role if role else None)
    
    # Paginate results
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'users': page_obj,
        'role_filter': role,
        'search_query': search_query,
        'page_title': 'All Users',
    }
    
    return render(request, 'accounts/users_list.html', context)


@login_required
def doctors_list_view(request):
    """
    Doctors listing from Django models
    """
    specialty = request.GET.get('specialty', '')
    search_query = request.GET.get('q', '')
    
    if search_query:
        doctors = data_service.search_doctors(search_query)
    else:
        doctors = data_service.get_all_doctors(specialty if specialty else None)
    
    # Paginate results
    paginator = Paginator(doctors, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'doctors': page_obj,
        'specialty_filter': specialty,
        'search_query': search_query,
        'page_title': 'All Doctors',
    }
    
    return render(request, 'accounts/doctors_list.html', context)


@login_required
def hospitals_list_view(request):
    """
    Hospitals listing from Django models
    """
    hospitals = data_service.get_all_hospitals()
    
    # Paginate results
    paginator = Paginator(hospitals, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'hospitals': page_obj,
        'page_title': 'All Hospitals',
    }
    
    return render(request, 'accounts/hospitals_list.html', context)


@login_required
def surveys_list_view(request):
    """
    Surveys listing from Django models
    """
    surveys = data_service.get_all_surveys()
    
    # Paginate results
    paginator = Paginator(surveys, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'surveys': page_obj,
        'page_title': 'All Surveys',
    }
    
    return render(request, 'accounts/surveys_list.html', context)


@require_http_methods(["GET"])
def api_search_users(request):
    """
    AJAX endpoint for searching users in Django models
    """
    query = request.GET.get('q', '').strip()
    role = request.GET.get('role', '')
    
    if len(query) < 2:
        return JsonResponse({
            'error': 'Query must be at least 2 characters',
            'results': []
        })
    
    # Search using Django data service
    search_results = data_service.search_users(query, role if role else None)
    
    return JsonResponse({
        'query': query,
        'role': role,
        'results': search_results,
        'total_found': len(search_results),
    })


@require_http_methods(["GET"])
def api_search_doctors(request):
    """
    AJAX endpoint for searching doctors in Django models
    """
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({
            'error': 'Query must be at least 2 characters',
            'results': []
        })
    
    # Search using Django data service
    search_results = data_service.search_doctors(query)
    
    return JsonResponse({
        'query': query,
        'results': search_results,
        'total_found': len(search_results),
    })


@require_http_methods(["POST"])
@login_required
def api_sync_user_data(request):
    """
    AJAX endpoint to sync user data from external API (if available)
    """
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    its_id = request.POST.get('its_id', '').strip()
    if not its_id:
        return JsonResponse({'error': 'ITS ID is required'}, status=400)
    
    try:
        # Try to sync user data from external API
        user_data = user_api_service.sync_user_data(its_id)
        
        if user_data:
            return JsonResponse({
                'success': True,
                'message': f'User data synced successfully for ITS ID: {its_id}',
                'user_data': user_data
            })
        else:
            return JsonResponse({
                'success': False,
                'message': f'No user found with ITS ID: {its_id}'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@login_required
def api_clear_user_cache(request):
    """
    AJAX endpoint to clear user API cache
    """
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    its_id = request.POST.get('its_id', '')
    
    try:
        user_api_service.clear_user_cache(its_id if its_id else None)
        return JsonResponse({
            'success': True,
            'message': 'User cache cleared successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def api_system_status(request):
    """
    AJAX endpoint for system status check
    """
    django_status = data_service.get_system_status()
    user_api_status = user_api_service.get_api_status()
    
    return JsonResponse({
        'database_status': django_status['database_status'],
        'data_source': django_status['data_source'],
        'user_api_available': user_api_status['is_available'],
        'user_api_url': user_api_status['base_url'],
        'last_checked': user_api_status['last_checked'],
    })


@login_required
def system_configuration_view(request):
    """
    View for system configuration and status monitoring
    """
    if not request.user.is_staff:
        messages.error(request, "Permission denied")
        return redirect('dashboard')
    
    # Get current system status
    django_status = data_service.get_system_status()
    user_api_status = user_api_service.get_api_status()
    
    # Get model counts
    model_counts = data_service.get_model_counts()
    
    context = {
        'django_status': django_status,
        'user_api_status': user_api_status,
        'model_counts': model_counts,
        'page_title': 'System Configuration & Status',
    }
    
    return render(request, 'accounts/system_configuration.html', context)