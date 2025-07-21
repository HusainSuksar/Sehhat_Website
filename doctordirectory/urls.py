from django.urls import path
from . import views

app_name = 'doctordirectory'

urlpatterns = [
    # Dashboard and main views
    path('', views.dashboard, name='dashboard'),
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('doctors/<int:pk>/', views.doctor_detail, name='doctor_detail'),
    
    # Patient management
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/<int:pk>/', views.patient_detail, name='patient_detail'),
    path('patients/<int:patient_id>/add-record/', views.add_medical_record, name='add_medical_record'),
    
    # Appointments
    path('appointments/create/', views.create_appointment, name='create_appointment'),
    path('appointments/create/<int:doctor_id>/', views.create_appointment, name='create_appointment_for_doctor'),
    
    # Schedule management
    path('schedule/', views.schedule_management, name='schedule_management'),
    
    # Analytics
    path('analytics/', views.doctor_analytics, name='analytics'),
]