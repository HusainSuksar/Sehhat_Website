"""
API URL Configuration for the DoctorDirectory app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

app_name = 'doctordirectory_api'

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'doctors', api_views.DoctorViewSet)
router.register(r'patients', api_views.PatientViewSet)
router.register(r'appointments', api_views.AppointmentViewSet)
router.register(r'schedules', api_views.DoctorScheduleViewSet)
router.register(r'services', api_views.MedicalServiceViewSet)

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Statistics endpoints
    path('stats/system/', api_views.system_stats, name='system_stats'),
    
    # Search endpoints
    path('search/doctors/', api_views.search_doctors, name='search_doctors'),
]