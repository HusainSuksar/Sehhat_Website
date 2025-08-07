"""
URL Configuration for the MahalShifa API
"""
from django.urls import path, include
from . import api_views

urlpatterns = [
    # Dashboard
    path('dashboard/', api_views.mahalshifa_dashboard_api, name='mahalshifa_dashboard_api'),
    
    # Hospital Management
    path('hospitals/', api_views.HospitalListCreateAPIView.as_view(), name='hospital_list_create'),
    path('hospitals/<int:pk>/', api_views.HospitalDetailAPIView.as_view(), name='hospital_detail'),
    
    # Department Management
    path('departments/', api_views.DepartmentListCreateAPIView.as_view(), name='department_list_create'),
    path('departments/<int:pk>/', api_views.DepartmentDetailAPIView.as_view(), name='department_detail'),
    
    # Doctor Management
    path('doctors/', api_views.DoctorListCreateAPIView.as_view(), name='doctor_list_create'),
    path('doctors/<int:pk>/', api_views.DoctorDetailAPIView.as_view(), name='doctor_detail'),
    path('doctors/search/', api_views.DoctorSearchAPIView.as_view(), name='doctor_search'),
    
    # Hospital Staff Management
    path('staff/', api_views.HospitalStaffListCreateAPIView.as_view(), name='hospital_staff_list_create'),
    
    # Medical Services
    path('services/', api_views.MedicalServiceListCreateAPIView.as_view(), name='medical_service_list_create'),
    
    # Patient Management
    path('patients/', api_views.PatientListCreateAPIView.as_view(), name='patient_list_create'),
    path('patients/<int:pk>/', api_views.PatientDetailAPIView.as_view(), name='patient_detail'),
    path('patients/search/', api_views.PatientSearchAPIView.as_view(), name='patient_search'),
    
    # Emergency Contacts
    path('emergency-contacts/', api_views.EmergencyContactListCreateAPIView.as_view(), name='emergency_contact_list_create'),
    
    # Insurance
    path('insurance/', api_views.InsuranceListCreateAPIView.as_view(), name='insurance_list_create'),
    
    # Appointment Management
    path('appointments/', api_views.AppointmentListCreateAPIView.as_view(), name='appointment_list_create'),
    path('appointments/<int:pk>/', api_views.AppointmentDetailAPIView.as_view(), name='appointment_detail'),
    path('appointments/search/', api_views.AppointmentSearchAPIView.as_view(), name='appointment_search'),
    
    # Medical Records
    path('medical-records/', api_views.MedicalRecordListCreateAPIView.as_view(), name='medical_record_list_create'),
    path('medical-records/<int:pk>/', api_views.MedicalRecordDetailAPIView.as_view(), name='medical_record_detail'),
    
    # Prescriptions
    path('prescriptions/', api_views.PrescriptionListCreateAPIView.as_view(), name='prescription_list_create'),
    
    # Lab Tests
    path('lab-tests/', api_views.LabTestListCreateAPIView.as_view(), name='lab_test_list_create'),
    
    # Vital Signs
    path('vital-signs/', api_views.VitalSignsListCreateAPIView.as_view(), name='vital_signs_list_create'),
    
    # Room Management
    path('rooms/', api_views.RoomListCreateAPIView.as_view(), name='room_list_create'),
    
    # Medication Management
    path('medications/', api_views.MedicationListCreateAPIView.as_view(), name='medication_list_create'),
    
    # Admission and Discharge
    path('admissions/', api_views.AdmissionListCreateAPIView.as_view(), name='admission_list_create'),
    path('discharges/', api_views.DischargeListCreateAPIView.as_view(), name='discharge_list_create'),
    
    # Treatment Plans
    path('treatment-plans/', api_views.TreatmentPlanListCreateAPIView.as_view(), name='treatment_plan_list_create'),
    
    # Inventory Management
    path('inventory/', api_views.InventoryListCreateAPIView.as_view(), name='inventory_list_create'),
    path('inventory-items/', api_views.InventoryItemListCreateAPIView.as_view(), name='inventory_item_list_create'),
    
    # Statistics
    path('stats/hospitals/', api_views.hospital_stats_api, name='hospital_stats'),
    path('stats/patients/', api_views.patient_stats_api, name='patient_stats'),
    path('stats/appointments/', api_views.appointment_stats_api, name='appointment_stats'),
]