"""
URL configuration for umoor_sehhat project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect


def dashboard_redirect(request):
    """Redirect root URL to dashboard based on user role"""
    if request.user.is_authenticated:
        if request.user.is_admin:
            return redirect('admin:index')
        elif request.user.is_aamil:
            return redirect('moze:dashboard')
        elif request.user.is_moze_coordinator:
            return redirect('moze:dashboard')
        elif request.user.is_doctor:
            return redirect('doctordirectory:dashboard')
        elif request.user.is_student:
            return redirect('students:dashboard')
        else:
            return redirect('accounts:profile')
    else:
        return redirect('accounts:login')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard_redirect, name='dashboard'),
    
    # App URLs
    path('accounts/', include('accounts.urls')),
    path('moze/', include('moze.urls')),
    path('mahalshifa/', include('mahalshifa.urls')),
    path('doctordirectory/', include('doctordirectory.urls')),
    path('surveys/', include('surveys.urls')),
    path('photos/', include('photos.urls')),
    path('evaluation/', include('evaluation.urls')),
    path('araz/', include('araz.urls')),
    path('students/', include('students.urls')),
    
    # API Integration URLs
    path('api/accounts/', include('accounts.api_urls')),
    path('api/araz/', include('araz.api_urls')),
    path('api/doctordirectory/', include('doctordirectory.api_urls')),
    path('api/mahalshifa/', include('mahalshifa.api_urls')),
    path('api/students/', include('students.api_urls')),
    
    # DRF URLs (if needed)
    path('api-auth/', include('rest_framework.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Customize admin site
admin.site.site_header = "Umoor Sehhat Administration"
admin.site.site_title = "Umoor Sehhat Admin"
admin.site.index_title = "Welcome to Umoor Sehhat Administration"
