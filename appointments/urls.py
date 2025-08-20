from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'appointments', views.AppointmentViewSet, basename='appointment')
router.register(r'time-slots', views.TimeSlotViewSet, basename='timeslot')
router.register(r'reminders', views.AppointmentReminderViewSet, basename='reminder')
router.register(r'waiting-list', views.WaitingListViewSet, basename='waitinglist')

app_name = 'appointments'

urlpatterns = [
    path('', include(router.urls)),
    path('check-availability/', views.DoctorAvailabilityView.as_view(), name='check-availability'),
]