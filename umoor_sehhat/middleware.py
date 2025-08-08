"""
Custom middleware for Umoor Sehhat Digital System
"""
import logging
import time
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Add security headers to all responses"""
    
    def process_response(self, request, response):
        # Security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # Remove server information
        if 'Server' in response:
            del response['Server']
            
        return response


class RequestLoggingMiddleware(MiddlewareMixin):
    """Log all requests for monitoring and debugging"""
    
    def process_request(self, request):
        request.start_time = time.time()
        
        # Log request details
        logger.info(f"Request: {request.method} {request.get_full_path()} "
                   f"from {request.META.get('REMOTE_ADDR')} "
                   f"User: {getattr(request.user, 'username', 'Anonymous')}")
        
        return None
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            logger.info(f"Response: {response.status_code} "
                       f"Duration: {duration:.2f}s "
                       f"Path: {request.get_full_path()}")
        
        return response


class APIErrorHandlingMiddleware(MiddlewareMixin):
    """Handle API errors gracefully"""
    
    def process_exception(self, request, exception):
        # Only handle API requests
        if request.path.startswith('/api/'):
            logger.error(f"API Error: {exception} "
                        f"Path: {request.get_full_path()} "
                        f"User: {getattr(request.user, 'username', 'Anonymous')}")
            
            return JsonResponse({
                'error': 'Internal server error',
                'message': 'An unexpected error occurred. Please try again later.',
                'status': 500
            }, status=500)
        
        return None


class RateLimitMiddleware(MiddlewareMixin):
    """Basic rate limiting for sensitive endpoints"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit_cache = {}
        super().__init__(get_response)
    
    def process_request(self, request):
        # Rate limit login attempts
        if request.path in ['/accounts/login/', '/api/login/', '/api/token/']:
            client_ip = request.META.get('REMOTE_ADDR')
            current_time = int(time.time())
            
            # Clean old entries (older than 1 hour)
            cutoff_time = current_time - 3600
            self.rate_limit_cache = {
                ip: timestamps for ip, timestamps in self.rate_limit_cache.items()
                if any(t > cutoff_time for t in timestamps)
            }
            
            # Check rate limit for this IP
            if client_ip in self.rate_limit_cache:
                recent_attempts = [t for t in self.rate_limit_cache[client_ip] if t > current_time - 300]  # 5 minutes
                if len(recent_attempts) >= 50:  # Max 50 attempts per 5 minutes (relaxed for testing)
                    logger.warning(f"Rate limit exceeded for IP {client_ip}")
                    return JsonResponse({
                        'error': 'Rate limit exceeded',
                        'message': 'Too many login attempts. Please try again later.',
                        'status': 429
                    }, status=429)
                
                self.rate_limit_cache[client_ip].append(current_time)
            else:
                self.rate_limit_cache[client_ip] = [current_time]
        
        return None