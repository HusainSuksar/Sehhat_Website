"""
API-Integrated Views
Demonstrates hybrid approach using both local database and external API data
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
    from services.api_service import api_service
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
        from services.api_service import api_service
    except ImportError as e:
        # Final fallback: create mock services for development
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Could not import services: {e}")
        
        # Create mock objects to prevent crashes
        class MockAPIService:
            def get_api_status(self):
                return {'is_available': False, 'base_url': 'mock', 'last_checked': 'now', 'cache_timeout': 300}
            def get_external_doctors(self, specialty=None):
                return []
            def get_external_hospitals(self):
                return []
            def get_external_surveys(self, is_active=None):
                return []
        
        class MockDataService:
            def get_dashboard_statistics(self, include_external=True):
                return {'local_stats': {}, 'external_stats': {}, 'combined_stats': {}, 'external_available': False}
            def get_all_doctors(self, specialty=None, include_external=True):
                return {'local_doctors': [], 'external_doctors': [], 'total_count': 0, 'external_available': False}
            def get_all_hospitals(self, include_partners=True):
                return {'local_hospitals': [], 'partner_hospitals': [], 'total_count': 0, 'partners_available': False}
            def get_all_surveys(self, include_regional=True):
                return {'local_surveys': [], 'regional_surveys': [], 'total_count': 0, 'regional_available': False}
            def get_system_status(self):
                return {'database_status': 'connected', 'api_status': {'is_available': False}, 'cache_status': 'active'}
            def search_doctors(self, query, include_external=True):
                return {'local_results': [], 'external_results': [], 'query': query, 'total_found': 0}
            def refresh_external_cache(self):
                pass
        
        api_service = MockAPIService()
        data_service = MockDataService()


@login_required
def hybrid_dashboard_view(request):
    """
    Enhanced dashboard that shows both local and external data
    """
    # Get hybrid statistics
    stats = data_service.get_dashboard_statistics(include_external=True)
    
    # Get system status
    system_status = data_service.get_system_status()
    
    context = {
        'local_stats': stats['local_stats'],
        'external_stats': stats['external_stats'],
        'combined_stats': stats['combined_stats'],
        'external_available': stats['external_available'],
        'system_status': system_status,
        'page_title': 'Hybrid Dashboard',
    }
    
    # Add external error if any
    if 'external_error' in stats:
        context['external_error'] = stats['external_error']
        messages.warning(request, f"External API unavailable: {stats['external_error']}")
    
    return render(request, 'accounts/hybrid_dashboard.html', context)


@login_required
def hybrid_doctors_view(request):
    """
    Doctors listing that combines local and external doctors
    """
    specialty = request.GET.get('specialty', '')
    include_external = request.GET.get('include_external', 'true').lower() == 'true'
    
    # Get hybrid doctor data
    doctors_data = data_service.get_all_doctors(
        specialty=specialty if specialty else None,
        include_external=include_external
    )
    
    context = {
        'local_doctors': doctors_data['local_doctors'],
        'external_doctors': doctors_data['external_doctors'],
        'total_count': doctors_data['total_count'],
        'external_available': doctors_data['external_available'],
        'specialty_filter': specialty,
        'include_external': include_external,
        'page_title': 'All Doctors (Local + External)',
    }
    
    # Add external error if any
    if 'external_error' in doctors_data:
        context['external_error'] = doctors_data['external_error']
        messages.warning(request, "External doctors API unavailable")
    
    return render(request, 'accounts/hybrid_doctors.html', context)


@login_required
def hybrid_hospitals_view(request):
    """
    Hospitals listing that combines local and partner hospitals
    """
    include_partners = request.GET.get('include_partners', 'true').lower() == 'true'
    
    # Get hybrid hospital data
    hospitals_data = data_service.get_all_hospitals(include_partners=include_partners)
    
    context = {
        'local_hospitals': hospitals_data['local_hospitals'],
        'partner_hospitals': hospitals_data['partner_hospitals'],
        'total_count': hospitals_data['total_count'],
        'partners_available': hospitals_data['partners_available'],
        'include_partners': include_partners,
        'page_title': 'All Hospitals (Local + Partners)',
    }
    
    # Add partner error if any
    if 'partner_error' in hospitals_data:
        context['partner_error'] = hospitals_data['partner_error']
        messages.warning(request, "Partner hospitals API unavailable")
    
    return render(request, 'accounts/hybrid_hospitals.html', context)


@login_required
def hybrid_surveys_view(request):
    """
    Surveys listing that combines local and regional surveys
    """
    include_regional = request.GET.get('include_regional', 'true').lower() == 'true'
    
    # Get hybrid survey data
    surveys_data = data_service.get_all_surveys(include_regional=include_regional)
    
    context = {
        'local_surveys': surveys_data['local_surveys'],
        'regional_surveys': surveys_data['regional_surveys'],
        'total_count': surveys_data['total_count'],
        'regional_available': surveys_data['regional_available'],
        'include_regional': include_regional,
        'page_title': 'All Surveys (Local + Regional)',
    }
    
    # Add regional error if any
    if 'regional_error' in surveys_data:
        context['regional_error'] = surveys_data['regional_error']
        messages.warning(request, "Regional surveys API unavailable")
    
    return render(request, 'accounts/hybrid_surveys.html', context)


@require_http_methods(["GET"])
def api_search_doctors(request):
    """
    AJAX endpoint for searching doctors across both sources
    """
    query = request.GET.get('q', '').strip()
    include_external = request.GET.get('include_external', 'true').lower() == 'true'
    
    if len(query) < 2:
        return JsonResponse({
            'error': 'Query must be at least 2 characters',
            'results': []
        })
    
    # Search using hybrid service
    search_results = data_service.search_doctors(query, include_external)
    
    return JsonResponse({
        'query': query,
        'local_results': search_results['local_results'],
        'external_results': search_results['external_results'],
        'total_found': search_results['total_found'],
    })


@require_http_methods(["POST"])
@login_required
def api_refresh_cache(request):
    """
    AJAX endpoint to refresh external API cache
    """
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        data_service.refresh_external_cache()
        return JsonResponse({
            'success': True,
            'message': 'External API cache refreshed successfully'
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
    status = data_service.get_system_status()
    
    return JsonResponse({
        'database_status': status['database_status'],
        'api_available': status['api_status']['is_available'],
        'api_url': status['api_status']['base_url'],
        'cache_status': status['cache_status'],
        'last_checked': status['api_status']['last_checked'],
    })


@login_required
def api_configuration_view(request):
    """
    View for configuring API settings and viewing status
    """
    if not request.user.is_staff:
        messages.error(request, "Permission denied")
        return redirect('dashboard')
    
    # Get current API status
    system_status = data_service.get_system_status()
    
    # Get sample data from API if available
    sample_data = {}
    if system_status['api_status']['is_available']:
        try:
            sample_data = {
                'doctors_count': len(api_service.get_external_doctors()),
                'hospitals_count': len(api_service.get_external_hospitals()),
                'surveys_count': len(api_service.get_external_surveys()),
                'api_summary': api_service.get_api_summary(),
            }
        except:
            sample_data = {'error': 'Failed to fetch sample data'}
    
    context = {
        'system_status': system_status,
        'sample_data': sample_data,
        'api_base_url': api_service.base_url,
        'cache_timeout': api_service.cache_timeout,
        'request_timeout': api_service.timeout,
        'page_title': 'API Configuration & Status',
    }
    
    return render(request, 'accounts/api_configuration.html', context)