"""
Custom middleware for Umoor Sehhat Digital System
"""
import logging
import time
import json
from collections import defaultdict
from django.http import JsonResponse, HttpResponseForbidden
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.urls import reverse
from django.utils.html import escape
from django.core.exceptions import PermissionDenied, ValidationError
import re

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Add comprehensive security headers to all responses"""
    
    def process_response(self, request, response):
        # Content Security Policy
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' "
            "https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' "
            "https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "font-src 'self' https://cdnjs.cloudflare.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )
        
        response['Content-Security-Policy'] = csp_policy
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = (
            'camera=(), microphone=(), geolocation=(), '
            'payment=(), usb=(), magnetometer=(), gyroscope=()'
        )
        
        # Only add HSTS in production with HTTPS
        if not settings.DEBUG and request.is_secure():
            response['Strict-Transport-Security'] = (
                'max-age=31536000; includeSubDomains; preload'
            )
        
        return response


class RateLimitMiddleware(MiddlewareMixin):
    """Rate limiting middleware to prevent abuse"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limits = {
            'default': {'requests': 100, 'window': 300},  # 100 requests per 5 minutes
            'login': {'requests': 5, 'window': 300},       # 5 login attempts per 5 minutes
            'api': {'requests': 1000, 'window': 3600},     # 1000 API calls per hour
        }
    
    def process_request(self, request):
        # Get client IP
        ip = self.get_client_ip(request)
        
        # Determine rate limit type
        if '/accounts/login/' in request.path:
            limit_type = 'login'
        elif request.path.startswith('/api/'):
            limit_type = 'api'
        else:
            limit_type = 'default'
        
        # Check rate limit
        if self.is_rate_limited(ip, limit_type):
            return JsonResponse({
                'error': 'Rate limit exceeded. Please try again later.'
            }, status=429)
        
        return None
    
    def get_client_ip(self, request):
        """Get the real client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def is_rate_limited(self, ip, limit_type):
        """Check if IP is rate limited"""
        config = self.rate_limits[limit_type]
        cache_key = f"rate_limit:{limit_type}:{ip}"
        
        # Get current count
        current_requests = cache.get(cache_key, 0)
        
        if current_requests >= config['requests']:
            return True
        
        # Increment counter
        cache.set(cache_key, current_requests + 1, config['window'])
        return False


class RequestLoggingMiddleware(MiddlewareMixin):
    """Log requests for security monitoring"""
    
    def process_request(self, request):
        # Log suspicious patterns
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Check for common attack patterns
        suspicious_patterns = [
            r'<script[^>]*>.*?</script>',  # XSS attempts
            r'union.*select',              # SQL injection
            r'\.\./',                      # Path traversal
            r'eval\s*\(',                  # Code injection
        ]
        
        query_string = request.META.get('QUERY_STRING', '')
        path = request.path
        
        for pattern in suspicious_patterns:
            if re.search(pattern, query_string + path, re.IGNORECASE):
                logger.warning(
                    f"Suspicious request detected from {self.get_client_ip(request)}: "
                    f"Path: {path}, Query: {query_string}, UA: {user_agent}"
                )
                break
        
        return None
    
    def get_client_ip(self, request):
        """Get the real client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class APIErrorHandlingMiddleware(MiddlewareMixin):
    """Handle API errors consistently and securely"""
    
    def process_exception(self, request, exception):
        # Only handle API requests
        if not request.path.startswith('/api/'):
            return None
        
        # Log the error
        logger.error(f"API Error: {exception}", exc_info=True)
        
        # Return appropriate error response
        if isinstance(exception, PermissionDenied):
            return JsonResponse({
                'error': 'Permission denied',
                'code': 'PERMISSION_DENIED'
            }, status=403)
        
        elif isinstance(exception, ValidationError):
            return JsonResponse({
                'error': 'Validation error',
                'details': exception.message_dict if hasattr(exception, 'message_dict') else str(exception),
                'code': 'VALIDATION_ERROR'
            }, status=400)
        
        else:
            # Don't expose internal errors in production
            if settings.DEBUG:
                error_detail = str(exception)
            else:
                error_detail = 'An internal error occurred'
            
            return JsonResponse({
                'error': error_detail,
                'code': 'INTERNAL_ERROR'
            }, status=500)


class CSRFProtectionMiddleware(MiddlewareMixin):
    """Enhanced CSRF protection with additional validation"""
    
    def process_request(self, request):
        # Skip CSRF for safe methods
        if request.method in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            return None
        
        # For AJAX requests, ensure proper headers
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            # Check for custom CSRF header
            csrf_token = request.META.get('HTTP_X_CSRFTOKEN')
            if not csrf_token:
                return JsonResponse({
                    'error': 'CSRF token missing in AJAX request'
                }, status=403)
        
        return None


class InputSanitizationMiddleware(MiddlewareMixin):
    """Sanitize user input to prevent XSS and injection attacks"""
    
    def process_request(self, request):
        # Sanitize POST data
        if request.method == 'POST' and hasattr(request, 'POST'):
            self.sanitize_data(request.POST)
        
        # Sanitize GET parameters
        if hasattr(request, 'GET'):
            self.sanitize_data(request.GET)
        
        return None
    
    def sanitize_data(self, data):
        """Sanitize form data"""
        for key, value in data.items():
            if isinstance(value, str):
                # Basic XSS prevention
                value = escape(value)
                
                # Check for suspicious patterns
                if self.contains_malicious_pattern(value):
                    logger.warning(f"Malicious input detected in field '{key}': {value}")
    
    def contains_malicious_pattern(self, value):
        """Check for malicious patterns in input"""
        malicious_patterns = [
            r'<script[^>]*>',
            r'javascript:',
            r'on\w+\s*=',
            r'data:text/html',
            r'vbscript:',
        ]
        
        for pattern in malicious_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False