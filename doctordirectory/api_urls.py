"""
API URL Configuration for the DoctorDirectory app
"""
from django.urls import path
from . import api_views

app_name = 'doctordirectory_api'

urlpatterns = [
    # Dashboard
    path('dashboard/', api_views.doctordirectory_dashboard_api, name='dashboard'),
    
    # Doctor endpoints
    path('doctors/', api_views.DoctorListCreateAPIView.as_view(), name='doctor_list_create'),
    path('doctors/<int:pk>/', api_views.DoctorDetailAPIView.as_view(), name='doctor_detail'),
    path('doctors/search/', api_views.DoctorSearchAPIView.as_view(), name='doctor_search'),
    
    # Doctor Schedule endpoints
    path('schedules/', api_views.DoctorScheduleListCreateAPIView.as_view(), name='schedule_list_create'),
    path('schedules/<int:pk>/', api_views.DoctorScheduleDetailAPIView.as_view(), name='schedule_detail'),
    
    # Doctor Availability endpoints
    path('availability/', api_views.DoctorAvailabilityListCreateAPIView.as_view(), name='availability_list_create'),
    
    # Medical Services endpoints
    path('services/', api_views.MedicalServiceListCreateAPIView.as_view(), name='service_list_create'),
    
    # Patient endpoints
    path('patients/', api_views.PatientListCreateAPIView.as_view(), name='patient_list_create'),
    path('patients/<int:pk>/', api_views.PatientDetailAPIView.as_view(), name='patient_detail'),
    
    # Patient Log endpoints
    path('patient-logs/', api_views.PatientLogListCreateAPIView.as_view(), name='patient_log_list_create'),
    
    # Appointment endpoints
    path('appointments/', api_views.AppointmentListCreateAPIView.as_view(), name='appointment_list_create'),
    path('appointments/<int:pk>/', api_views.AppointmentDetailAPIView.as_view(), name='appointment_detail'),
    path('appointments/search/', api_views.AppointmentSearchAPIView.as_view(), name='appointment_search'),
    
    # Medical Record endpoints
    path('medical-records/', api_views.MedicalRecordListCreateAPIView.as_view(), name='medical_record_list_create'),
    path('medical-records/<int:pk>/', api_views.MedicalRecordDetailAPIView.as_view(), name='medical_record_detail'),
    
    # Prescription endpoints
    path('prescriptions/', api_views.PrescriptionListCreateAPIView.as_view(), name='prescription_list_create'),
    
    # Lab Test endpoints
    path('lab-tests/', api_views.LabTestListCreateAPIView.as_view(), name='lab_test_list_create'),
    
    # Vital Signs endpoints
    path('vital-signs/', api_views.VitalSignsListCreateAPIView.as_view(), name='vital_signs_list_create'),
    
    # Statistics endpoints
    path('stats/doctors/', api_views.doctor_stats_api, name='doctor_stats'),
    path('stats/patients/', api_views.patient_stats_api, name='patient_stats'),
    path('stats/appointments/', api_views.appointment_stats_api, name='appointment_stats'),
]