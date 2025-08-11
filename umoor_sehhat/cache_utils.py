"""
Cache utilities for performance optimization
"""
from functools import wraps
from django.core.cache import cache
from django.conf import settings
import hashlib


def cache_result(timeout=300, key_prefix='view'):
    """
    Decorator to cache function results
    
    Args:
        timeout: Cache timeout in seconds (default 5 minutes)
        key_prefix: Prefix for cache key
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = _generate_cache_key(func.__name__, args, kwargs, key_prefix)
            
            # Try to get from cache first
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result
        return wrapper
    return decorator


def cache_page_data(timeout=300):
    """
    Decorator specifically for view data caching
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # Include user role and page parameters in cache key
            user_role = getattr(request.user, 'role', 'anonymous') if request.user.is_authenticated else 'anonymous'
            cache_key = _generate_cache_key(
                func.__name__, 
                (user_role,) + args, 
                kwargs, 
                'page_data'
            )
            
            # Try cache first
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute and cache
            result = func(request, *args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result
        return wrapper
    return decorator


def cache_query_result(timeout=600, vary_on_user=False):
    """
    Decorator for caching database query results
    
    Args:
        timeout: Cache timeout in seconds (default 10 minutes)
        vary_on_user: Whether to include user in cache key
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract request if present
            request = None
            if args and hasattr(args[0], 'user'):
                request = args[0]
            
            # Build cache key
            cache_args = args
            if vary_on_user and request and request.user.is_authenticated:
                cache_args = (request.user.pk,) + args[1:]
            
            cache_key = _generate_cache_key(func.__name__, cache_args, kwargs, 'query')
            
            # Try cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute and cache
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result
        return wrapper
    return decorator


def _generate_cache_key(func_name, args, kwargs, prefix):
    """
    Generate a cache key from function name and arguments
    """
    # Convert args and kwargs to string
    args_str = str(args)
    kwargs_str = str(sorted(kwargs.items()))
    
    # Create hash for long keys
    key_data = f"{func_name}:{args_str}:{kwargs_str}"
    key_hash = hashlib.md5(key_data.encode()).hexdigest()
    
    return f"{prefix}:{key_hash}"


def invalidate_cache(pattern):
    """
    Invalidate cache keys matching a pattern
    """
    try:
        # This is a simplified version - in production you'd use Redis pattern matching
        if hasattr(cache, 'delete_pattern'):
            cache.delete_pattern(f"*{pattern}*")
        else:
            # Fallback for non-Redis backends
            cache.clear()
    except Exception:
        # Fail silently if cache operations fail
        pass


def warm_cache():
    """
    Pre-warm frequently accessed cache entries
    """
    from accounts.models import User
    from doctordirectory.models import Doctor, Appointment
    
    try:
        # Warm up user count cache
        cache.set('stats:total_users', User.objects.count(), 1800)  # 30 minutes
        
        # Warm up doctor count cache
        cache.set('stats:total_doctors', Doctor.objects.filter(is_active=True).count(), 1800)
        
        # Warm up today's appointments cache
        from django.utils import timezone
        today = timezone.now().date()
        cache.set(
            'stats:today_appointments',
            Appointment.objects.filter(appointment_date=today).count(),
            900  # 15 minutes
        )
        
    except Exception:
        # Fail silently if warmup fails
        pass