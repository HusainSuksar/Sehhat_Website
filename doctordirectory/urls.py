from django.urls import path
from . import views

app_name = 'doctordirectory'

urlpatterns = [
    # Dashboard and main views
    path('', views.dashboard, name='dashboard'),
    
    # Doctor management
    path('doctors/', views.DoctorListView.as_view(), name='doctor_list'),
    path('doctors/<int:pk>/', views.DoctorDetailView.as_view(), name='doctor_detail'),
    path('doctors/create/', views.DoctorCreateView.as_view(), name='doctor_create'),
    path('doctors/<int:pk>/edit/', views.DoctorUpdateView.as_view(), name='doctor_update'),
    
    # Patient management
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/<int:pk>/', views.patient_detail, name='patient_detail'),
    path('patients/create/', views.PatientCreateView.as_view(), name='patient_create'),
    path('patients/<int:pk>/edit/', views.PatientUpdateView.as_view(), name='patient_update'),
    path('patients/<int:patient_id>/add-record/', views.add_medical_record, name='add_medical_record'),
    
    # Appointments
    path('appointments/', views.AppointmentListView.as_view(), name='appointment_list'),
    path('appointments/<int:pk>/', views.AppointmentDetailView.as_view(), name='appointment_detail'),
    path('appointments/create/', views.create_appointment, name='create_appointment'),
    path('appointments/create/<int:doctor_id>/', views.create_appointment, name='create_appointment_for_doctor'),
    path('appointments/<int:pk>/edit/', views.AppointmentUpdateView.as_view(), name='appointment_update'),
    
    # Medical records
    path('records/', views.MedicalRecordListView.as_view(), name='medical_record_list'),
    path('records/<int:pk>/', views.MedicalRecordDetailView.as_view(), name='medical_record_detail'),
    path('records/create/', views.MedicalRecordCreateView.as_view(), name='medical_record_create'),
    
    # Prescriptions
    path('prescriptions/', views.PrescriptionListView.as_view(), name='prescription_list'),
    path('prescriptions/<int:pk>/', views.PrescriptionDetailView.as_view(), name='prescription_detail'),
    path('prescriptions/create/', views.PrescriptionCreateView.as_view(), name='prescription_create'),
    
    # Lab tests
    path('lab-tests/', views.LabTestListView.as_view(), name='labtest_list'),
    path('lab-tests/<int:pk>/', views.LabTestDetailView.as_view(), name='labtest_detail'),
    path('lab-tests/create/', views.LabTestCreateView.as_view(), name='labtest_create'),
    
    # Schedule management
    path('schedule/', views.schedule_management, name='schedule_management'),
    path('schedule/create/', views.ScheduleCreateView.as_view(), name='schedule_create'),
    path('availability/', views.DoctorAvailabilityListView.as_view(), name='availability_list'),
    
    # Analytics and reports
    path('analytics/', views.doctor_analytics, name='analytics'),
    path('export/', views.export_doctor_data, name='export_data'),
    
    # Services
    path('services/', views.MedicalServiceListView.as_view(), name='service_list'),
    path('services/<int:pk>/', views.MedicalServiceDetailView.as_view(), name='service_detail'),
    path('services/create/', views.MedicalServiceCreateView.as_view(), name='service_create'),
]