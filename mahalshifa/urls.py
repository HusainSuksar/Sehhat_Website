from django.urls import path
from . import views

app_name = 'mahalshifa'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Hospital management
    path('hospitals/', views.HospitalListView.as_view(), name='hospital_list'),
    path('hospitals/create/', views.HospitalCreateView.as_view(), name='hospital_create'),
    path('hospitals/<int:pk>/', views.HospitalDetailView.as_view(), name='hospital_detail'),
    path('hospitals/<int:pk>/edit/', views.HospitalUpdateView.as_view(), name='hospital_update'),
    path('hospitals/<int:pk>/delete/', views.HospitalDeleteView.as_view(), name='hospital_delete'),
    
    # Patient management
    path('patients/', views.PatientListView.as_view(), name='patient_list'),
    path('patients/create/', views.PatientCreateView.as_view(), name='patient_create'),
    path('patients/<int:pk>/', views.patient_detail, name='patient_detail'),
    path('patients/<int:pk>/edit/', views.PatientUpdateView.as_view(), name='patient_update'),
    path('patients/<int:pk>/delete/', views.PatientDeleteView.as_view(), name='patient_delete'),
    
    # Appointment management
    path('appointments/', views.AppointmentListView.as_view(), name='appointment_list'),
    path('appointments/<int:pk>/', views.appointment_detail, name='appointment_detail'),
    path('appointments/create/', views.create_appointment, name='appointment_create'),
    path('appointments/<int:pk>/edit/', views.AppointmentUpdateView.as_view(), name='appointment_update'),
    path('appointments/<int:pk>/delete/', views.AppointmentDeleteView.as_view(), name='appointment_delete'),
    
    # Medical Record management
    path('medical-records/', views.MedicalRecordListView.as_view(), name='medical_record_list'),
    path('medical-records/create/', views.MedicalRecordCreateView.as_view(), name='medical_record_create'),
    path('medical-records/<int:pk>/', views.MedicalRecordDetailView.as_view(), name='medical_record_detail'),
    path('medical-records/<int:pk>/edit/', views.MedicalRecordUpdateView.as_view(), name='medical_record_update'),
    path('medical-records/<int:pk>/delete/', views.MedicalRecordDeleteView.as_view(), name='medical_record_delete'),
    
    # Analytics and reports
    path('analytics/', views.medical_analytics, name='analytics'),
    path('export/', views.export_medical_data, name='export_data'),
    
    # Inventory management
    path('inventory/', views.inventory_management, name='inventory_management'),
]
