from django.urls import path
from . import views

app_name = 'mahalshifa'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Hospital management
    path('hospitals/', views.HospitalListView.as_view(), name='hospital_list'),
    path('hospitals/<int:pk>/', views.HospitalDetailView.as_view(), name='hospital_detail'),
    path('hospitals/create/', views.HospitalCreateView.as_view(), name='hospital_create'),
    path('hospitals/<int:pk>/edit/', views.HospitalUpdateView.as_view(), name='hospital_update'),
    
    # Patient management
    path('patients/', views.PatientListView.as_view(), name='patient_list'),
    path('patients/<int:pk>/', views.patient_detail, name='patient_detail'),
    path('patients/create/', views.PatientCreateView.as_view(), name='patient_create'),
    path('patients/<int:pk>/edit/', views.PatientUpdateView.as_view(), name='patient_update'),
    
    # Appointment management
    path('appointments/', views.AppointmentListView.as_view(), name='appointment_list'),
    path('appointments/<int:pk>/', views.appointment_detail, name='appointment_detail'),
    path('appointments/create/', views.create_appointment, name='appointment_create'),
    path('appointments/<int:pk>/edit/', views.AppointmentUpdateView.as_view(), name='appointment_update'),
    
    # Medical records
    path('records/', views.MedicalRecordListView.as_view(), name='record_list'),
    path('records/<int:pk>/', views.MedicalRecordDetailView.as_view(), name='record_detail'),
    path('records/create/', views.MedicalRecordCreateView.as_view(), name='record_create'),
    
    # Prescriptions
    path('prescriptions/', views.PrescriptionListView.as_view(), name='prescription_list'),
    path('prescriptions/<int:pk>/', views.PrescriptionDetailView.as_view(), name='prescription_detail'),
    path('prescriptions/create/', views.PrescriptionCreateView.as_view(), name='prescription_create'),
    
    # Laboratory tests
    path('lab-tests/', views.LabTestListView.as_view(), name='labtest_list'),
    path('lab-tests/<int:pk>/', views.LabTestDetailView.as_view(), name='labtest_detail'),
    path('lab-tests/create/', views.LabTestCreateView.as_view(), name='labtest_create'),
    
    # Departments and staff
    path('departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('departments/<int:pk>/', views.DepartmentDetailView.as_view(), name='department_detail'),
    path('staff/', views.HospitalStaffListView.as_view(), name='staff_list'),
    path('doctors/', views.DoctorListView.as_view(), name='doctor_list'),
    
    # Room and admission management
    path('rooms/', views.RoomListView.as_view(), name='room_list'),
    path('admissions/', views.AdmissionListView.as_view(), name='admission_list'),
    path('admissions/<int:pk>/', views.AdmissionDetailView.as_view(), name='admission_detail'),
    path('discharges/', views.DischargeListView.as_view(), name='discharge_list'),
    
    # Inventory management
    path('inventory/', views.inventory_management, name='inventory_management'),
    path('inventory/<int:pk>/', views.InventoryDetailView.as_view(), name='inventory_detail'),
    
    # Analytics and reports
    path('analytics/', views.medical_analytics, name='analytics'),
    path('export/', views.export_medical_data, name='export_data'),
    
    # Emergency and insurance
    path('emergency-contacts/', views.EmergencyContactListView.as_view(), name='emergency_contact_list'),
    path('insurance/', views.InsuranceListView.as_view(), name='insurance_list'),
]
