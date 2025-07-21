from django.urls import path
from . import views

app_name = 'mahalshifa'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Hospital management (only existing views)
    path('hospitals/', views.HospitalListView.as_view(), name='hospital_list'),
    path('hospitals/<int:pk>/', views.HospitalDetailView.as_view(), name='hospital_detail'),
    
    # Patient management (only existing views)
    path('patients/', views.PatientListView.as_view(), name='patient_list'),
    path('patients/<int:pk>/', views.patient_detail, name='patient_detail'),
    
    # Appointment management (only existing views)
    path('appointments/', views.AppointmentListView.as_view(), name='appointment_list'),
    path('appointments/<int:pk>/', views.appointment_detail, name='appointment_detail'),
    path('appointments/create/', views.create_appointment, name='appointment_create'),
    
    # Analytics and reports (only existing views)
    path('analytics/', views.medical_analytics, name='analytics'),
    path('export/', views.export_medical_data, name='export_data'),
    
    # Inventory management (only existing views)
    path('inventory/', views.inventory_management, name='inventory_management'),
]
