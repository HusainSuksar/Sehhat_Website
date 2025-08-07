"""
API Views for the MahalShifa app
"""
from rest_framework import generics, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q, Count, Avg
from django.shortcuts import get_object_or_404
from django.db import transaction
from datetime import datetime, timedelta

from .models import (
    MedicalService, Patient, Appointment, MedicalRecord, Prescription,
    LabTest, VitalSigns, Hospital, Department, Doctor, HospitalStaff,
    Room, Medication, LabResult, Admission, Discharge, TreatmentPlan,
    TreatmentMedication, Inventory, InventoryItem, EmergencyContact,
    Insurance
)
from .serializers import (
    MedicalServiceSerializer, PatientSerializer, PatientCreateSerializer,
    AppointmentSerializer, AppointmentCreateSerializer, MedicalRecordSerializer,
    MedicalRecordCreateSerializer, PrescriptionSerializer, LabTestSerializer,
    VitalSignsSerializer, HospitalSerializer, DepartmentSerializer,
    DoctorSerializer, HospitalStaffSerializer, RoomSerializer,
    MedicationSerializer, AdmissionSerializer, DischargeSerializer,
    TreatmentPlanSerializer, InventorySerializer, InventoryItemSerializer,
    EmergencyContactSerializer, InsuranceSerializer,
    HospitalStatsSerializer, PatientStatsSerializer, AppointmentStatsSerializer,
    PatientSearchSerializer, AppointmentSearchSerializer, DoctorSearchSerializer
)

User = get_user_model()


# Custom Permission Classes
class IsAdminOrStaff(permissions.BasePermission):
    """Allow access to admins and hospital staff only"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.is_admin or hasattr(request.user, 'hospital_staff')


class IsDoctorOrStaff(permissions.BasePermission):
    """Allow access to doctors and hospital staff"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return (request.user.is_admin or 
                hasattr(request.user, 'mahalshifa_doctor_profile') or 
                hasattr(request.user, 'hospital_staff'))


class IsPatientOwnerOrMedicalStaff(permissions.BasePermission):
    """Allow patients to access their own records, medical staff to access patient records"""
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_admin or user.is_superuser:
            return True
        
        # For Patient objects
        if hasattr(obj, 'user_account') and obj.user_account:
            if obj.user_account == user:
                return True
        
        # For objects with patient field
        if hasattr(obj, 'patient'):
            if hasattr(obj.patient, 'user_account') and obj.patient.user_account == user:
                return True
        
        # Medical staff can access patient records
        if (hasattr(user, 'mahalshifa_doctor_profile') or 
            hasattr(user, 'hospital_staff')):
            return True
        
        return False


# Access Control Mixins
class HospitalAccessMixin:
    """Mixin to filter hospitals based on user role"""
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_superuser:
            return Hospital.objects.all()
        elif hasattr(user, 'mahalshifa_doctor_profile'):
            # Doctors can see their hospital
            return Hospital.objects.filter(id=user.mahalshifa_doctor_profile.hospital.id)
        elif hasattr(user, 'hospital_staff'):
            # Staff can see their hospital
            return Hospital.objects.filter(id=user.hospital_staff.hospital.id)
        else:
            # Patients can see all active hospitals for appointment booking
            return Hospital.objects.filter(is_active=True)


class PatientAccessMixin:
    """Mixin to filter patients based on user role"""
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_superuser:
            return Patient.objects.all()
        elif hasattr(user, 'mahalshifa_doctor_profile'):
            # Doctors can see patients they've treated
            doctor = user.mahalshifa_doctor_profile
            patient_ids = set()
            patient_ids.update(doctor.appointments.values_list('patient_id', flat=True))
            patient_ids.update(doctor.medical_records.values_list('patient_id', flat=True))
            return Patient.objects.filter(id__in=patient_ids)
        elif hasattr(user, 'hospital_staff'):
            # Hospital staff can see patients in their hospital
            hospital = user.hospital_staff.hospital
            patient_ids = set()
            patient_ids.update(
                Appointment.objects.filter(doctor__hospital=hospital).values_list('patient_id', flat=True)
            )
            return Patient.objects.filter(id__in=patient_ids)
        else:
            # Users can only see their own patient record
            try:
                return Patient.objects.filter(user_account=user)
            except:
                return Patient.objects.none()


class AppointmentAccessMixin:
    """Mixin to filter appointments based on user role"""
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_superuser:
            return Appointment.objects.all()
        elif hasattr(user, 'mahalshifa_doctor_profile'):
            return Appointment.objects.filter(doctor=user.mahalshifa_doctor_profile)
        elif hasattr(user, 'hospital_staff'):
            return Appointment.objects.filter(doctor__hospital=user.hospital_staff.hospital)
        else:
            # Patients can see their own appointments
            try:
                patient = Patient.objects.filter(user_account=user).first()
                if patient:
                    return Appointment.objects.filter(patient=patient)
            except:
                pass
            return Appointment.objects.none()


# Hospital and Department API Views
class HospitalListCreateAPIView(HospitalAccessMixin, generics.ListCreateAPIView):
    serializer_class = HospitalSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['hospital_type', 'is_active', 'is_emergency_capable', 'has_pharmacy', 'has_laboratory']
    search_fields = ['name', 'description', 'address']
    ordering_fields = ['name', 'total_beds', 'created_at']
    ordering = ['name']
    
    def perform_create(self, serializer):
        # Only admins can create hospitals
        if not (self.request.user.is_admin or self.request.user.is_superuser):
            raise PermissionDenied("Only administrators can create hospitals")
        serializer.save()


class HospitalDetailAPIView(HospitalAccessMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = HospitalSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        """Custom permissions for different actions"""
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]


class DepartmentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminOrStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['hospital', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['hospital', 'name']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_superuser:
            return Department.objects.all()
        elif hasattr(user, 'mahalshifa_doctor_profile'):
            return Department.objects.filter(hospital=user.mahalshifa_doctor_profile.hospital)
        elif hasattr(user, 'hospital_staff'):
            return Department.objects.filter(hospital=user.hospital_staff.hospital)
        return Department.objects.none()


class DepartmentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminOrStaff]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_superuser:
            return Department.objects.all()
        elif hasattr(user, 'mahalshifa_doctor_profile'):
            return Department.objects.filter(hospital=user.mahalshifa_doctor_profile.hospital)
        elif hasattr(user, 'hospital_staff'):
            return Department.objects.filter(hospital=user.hospital_staff.hospital)
        return Department.objects.none()


# Doctor and Staff API Views
class DoctorListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['hospital', 'department', 'specialization', 'is_available', 'is_emergency_doctor']
    search_fields = ['user__first_name', 'user__last_name', 'specialization', 'qualification']
    ordering_fields = ['user__first_name', 'specialization', 'experience_years', 'created_at']
    ordering = ['user__first_name']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_superuser:
            return Doctor.objects.all()
        elif hasattr(user, 'hospital_staff'):
            return Doctor.objects.filter(hospital=user.hospital_staff.hospital)
        else:
            # Patients can see all available doctors
            return Doctor.objects.filter(is_available=True)
    
    def perform_create(self, serializer):
        # Only admins can create doctor profiles
        if not (self.request.user.is_admin or self.request.user.is_superuser):
            raise PermissionDenied("Only administrators can create doctor profiles")
        serializer.save()


class DoctorDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_superuser:
            return Doctor.objects.all()
        elif hasattr(user, 'hospital_staff'):
            return Doctor.objects.filter(hospital=user.hospital_staff.hospital)
        else:
            return Doctor.objects.filter(is_available=True)
    
    def get_permissions(self):
        """Custom permissions for different actions"""
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            try:
                doctor_id = self.kwargs.get('pk')
                if doctor_id:
                    user = self.request.user
                    if user.is_admin or user.is_superuser:
                        return [permissions.IsAuthenticated()]
                    
                    # Doctors can update their own profile
                    if hasattr(user, 'mahalshifa_doctor_profile'):
                        try:
                            doctor = Doctor.objects.get(pk=doctor_id)
                            if doctor == user.mahalshifa_doctor_profile:
                                return [permissions.IsAuthenticated()]
                        except Doctor.DoesNotExist:
                            pass
                
                return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
            except (ValueError, TypeError):
                return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]


class HospitalStaffListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = HospitalStaffSerializer
    permission_classes = [IsAdminOrStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['hospital', 'department', 'staff_type', 'shift', 'is_active']
    search_fields = ['user__first_name', 'user__last_name', 'employee_id']
    ordering_fields = ['user__first_name', 'staff_type', 'hire_date']
    ordering = ['user__first_name']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_superuser:
            return HospitalStaff.objects.all()
        elif hasattr(user, 'hospital_staff'):
            return HospitalStaff.objects.filter(hospital=user.hospital_staff.hospital)
        return HospitalStaff.objects.none()


# Medical Service API Views
class MedicalServiceListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = MedicalServiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active', 'requires_appointment']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'cost', 'duration_minutes', 'created_at']
    ordering = ['category', 'name']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_superuser or hasattr(user, 'hospital_staff'):
            return MedicalService.objects.all()
        else:
            # Patients can see all active services
            return MedicalService.objects.filter(is_active=True)
    
    def perform_create(self, serializer):
        # Only admins and staff can create services
        if not (self.request.user.is_admin or hasattr(self.request.user, 'hospital_staff')):
            raise PermissionDenied("Only administrators and hospital staff can create medical services")
        serializer.save()


# Patient API Views
class PatientListCreateAPIView(PatientAccessMixin, generics.ListCreateAPIView):
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['gender', 'blood_group', 'registered_moze', 'is_active']
    search_fields = ['its_id', 'first_name', 'last_name', 'arabic_name', 'phone_number']
    ordering_fields = ['first_name', 'last_name', 'registration_date', 'created_at']
    ordering = ['last_name', 'first_name']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PatientCreateSerializer
        return PatientSerializer


class PatientDetailAPIView(PatientAccessMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated, IsPatientOwnerOrMedicalStaff]


# Appointment API Views
class AppointmentListCreateAPIView(AppointmentAccessMixin, generics.ListCreateAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['doctor', 'patient', 'status', 'appointment_type', 'appointment_date']
    ordering_fields = ['appointment_date', 'appointment_time', 'created_at']
    ordering = ['appointment_date', 'appointment_time']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AppointmentCreateSerializer
        return AppointmentSerializer


class AppointmentDetailAPIView(AppointmentAccessMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsPatientOwnerOrMedicalStaff]


# Medical Record API Views
class MedicalRecordListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = MedicalRecordSerializer
    permission_classes = [IsDoctorOrStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['doctor', 'patient', 'follow_up_required']
    search_fields = ['chief_complaint', 'diagnosis', 'treatment_plan']
    ordering_fields = ['consultation_date']
    ordering = ['-consultation_date']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_superuser:
            return MedicalRecord.objects.all()
        elif hasattr(user, 'mahalshifa_doctor_profile'):
            return MedicalRecord.objects.filter(doctor=user.mahalshifa_doctor_profile)
        elif hasattr(user, 'hospital_staff'):
            return MedicalRecord.objects.filter(doctor__hospital=user.hospital_staff.hospital)
        else:
            # Patients can see their own medical records
            try:
                patient = Patient.objects.filter(user_account=user).first()
                if patient:
                    return MedicalRecord.objects.filter(patient=patient)
            except:
                pass
            return MedicalRecord.objects.none()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MedicalRecordCreateSerializer
        return MedicalRecordSerializer
    
    def perform_create(self, serializer):
        user = self.request.user
        if hasattr(user, 'mahalshifa_doctor_profile'):
            serializer.save(doctor=user.mahalshifa_doctor_profile)
        else:
            serializer.save()


class MedicalRecordDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MedicalRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsPatientOwnerOrMedicalStaff]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_superuser:
            return MedicalRecord.objects.all()
        elif hasattr(user, 'mahalshifa_doctor_profile'):
            return MedicalRecord.objects.filter(doctor=user.mahalshifa_doctor_profile)
        elif hasattr(user, 'hospital_staff'):
            return MedicalRecord.objects.filter(doctor__hospital=user.hospital_staff.hospital)
        else:
            try:
                patient = Patient.objects.filter(user_account=user).first()
                if patient:
                    return MedicalRecord.objects.filter(patient=patient)
            except:
                pass
            return MedicalRecord.objects.none()


# Prescription API Views
class PrescriptionListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = PrescriptionSerializer
    permission_classes = [IsDoctorOrStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['doctor', 'patient', 'is_active', 'is_dispensed']
    search_fields = ['medication_name', 'instructions']
    ordering_fields = ['prescription_date']
    ordering = ['-prescription_date']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_superuser:
            return Prescription.objects.all()
        elif hasattr(user, 'mahalshifa_doctor_profile'):
            return Prescription.objects.filter(doctor=user.mahalshifa_doctor_profile)
        elif hasattr(user, 'hospital_staff'):
            return Prescription.objects.filter(doctor__hospital=user.hospital_staff.hospital)
        return Prescription.objects.none()


# Lab Test API Views
class LabTestListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = LabTestSerializer
    permission_classes = [IsDoctorOrStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['doctor', 'patient', 'test_category', 'status', 'is_abnormal']
    search_fields = ['test_name', 'test_code']
    ordering_fields = ['ordered_date', 'result_date']
    ordering = ['-ordered_date']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_superuser:
            return LabTest.objects.all()
        elif hasattr(user, 'mahalshifa_doctor_profile'):
            return LabTest.objects.filter(doctor=user.mahalshifa_doctor_profile)
        elif hasattr(user, 'hospital_staff'):
            return LabTest.objects.filter(doctor__hospital=user.hospital_staff.hospital)
        return LabTest.objects.none()


# Vital Signs API Views
class VitalSignsListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = VitalSignsSerializer
    permission_classes = [IsDoctorOrStaff]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['patient', 'medical_record']
    ordering_fields = ['recorded_at']
    ordering = ['-recorded_at']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_superuser:
            return VitalSigns.objects.all()
        elif hasattr(user, 'mahalshifa_doctor_profile'):
            return VitalSigns.objects.filter(medical_record__doctor=user.mahalshifa_doctor_profile)
        elif hasattr(user, 'hospital_staff'):
            return VitalSigns.objects.filter(medical_record__doctor__hospital=user.hospital_staff.hospital)
        return VitalSigns.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(recorded_by=self.request.user)


# Room API Views
class RoomListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = RoomSerializer
    permission_classes = [IsAdminOrStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['hospital', 'department', 'room_type', 'is_available', 'is_operational']
    search_fields = ['room_number', 'floor_number']
    ordering_fields = ['room_number', 'floor_number', 'capacity']
    ordering = ['hospital', 'floor_number', 'room_number']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_superuser:
            return Room.objects.all()
        elif hasattr(user, 'mahalshifa_doctor_profile'):
            return Room.objects.filter(hospital=user.mahalshifa_doctor_profile.hospital)
        elif hasattr(user, 'hospital_staff'):
            return Room.objects.filter(hospital=user.hospital_staff.hospital)
        return Room.objects.none()


# Medication API Views
class MedicationListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = MedicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['medication_type', 'is_active', 'requires_prescription']
    search_fields = ['name', 'generic_name', 'brand_name', 'manufacturer']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        user = self.request.user
        if (user.is_admin or user.is_superuser or 
            hasattr(user, 'mahalshifa_doctor_profile') or 
            hasattr(user, 'hospital_staff')):
            return Medication.objects.all()
        else:
            # Patients can see only active medications
            return Medication.objects.filter(is_active=True)
    
    def perform_create(self, serializer):
        # Only medical staff can create medications
        if not (self.request.user.is_admin or 
                hasattr(self.request.user, 'mahalshifa_doctor_profile') or 
                hasattr(self.request.user, 'hospital_staff')):
            raise PermissionDenied("Only medical staff can create medications")
        serializer.save()


# Admission and Discharge API Views
class AdmissionListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = AdmissionSerializer
    permission_classes = [IsDoctorOrStaff]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['hospital', 'patient', 'admitting_doctor', 'admission_type', 'status']
    ordering_fields = ['admission_date']
    ordering = ['-admission_date']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_superuser:
            return Admission.objects.all()
        elif hasattr(user, 'mahalshifa_doctor_profile'):
            return Admission.objects.filter(
                Q(admitting_doctor=user.mahalshifa_doctor_profile) |
                Q(hospital=user.mahalshifa_doctor_profile.hospital)
            )
        elif hasattr(user, 'hospital_staff'):
            return Admission.objects.filter(hospital=user.hospital_staff.hospital)
        return Admission.objects.none()


class DischargeListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = DischargeSerializer
    permission_classes = [IsDoctorOrStaff]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['discharging_doctor', 'discharge_type', 'condition_at_discharge']
    ordering_fields = ['discharge_date']
    ordering = ['-discharge_date']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_superuser:
            return Discharge.objects.all()
        elif hasattr(user, 'mahalshifa_doctor_profile'):
            return Discharge.objects.filter(discharging_doctor=user.mahalshifa_doctor_profile)
        elif hasattr(user, 'hospital_staff'):
            return Discharge.objects.filter(admission__hospital=user.hospital_staff.hospital)
        return Discharge.objects.none()


# Treatment Plan API Views
class TreatmentPlanListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = TreatmentPlanSerializer
    permission_classes = [IsDoctorOrStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['doctor', 'patient', 'status']
    search_fields = ['plan_name', 'description', 'objectives']
    ordering_fields = ['created_at', 'start_date']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_superuser:
            return TreatmentPlan.objects.all()
        elif hasattr(user, 'mahalshifa_doctor_profile'):
            return TreatmentPlan.objects.filter(doctor=user.mahalshifa_doctor_profile)
        elif hasattr(user, 'hospital_staff'):
            return TreatmentPlan.objects.filter(doctor__hospital=user.hospital_staff.hospital)
        return TreatmentPlan.objects.none()


# Inventory API Views
class InventoryListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = InventorySerializer
    permission_classes = [IsAdminOrStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['hospital', 'inventory_type', 'department']
    search_fields = ['name', 'description', 'storage_location']
    ordering_fields = ['name', 'created_at']
    ordering = ['hospital', 'name']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_superuser:
            return Inventory.objects.all()
        elif hasattr(user, 'hospital_staff'):
            return Inventory.objects.filter(hospital=user.hospital_staff.hospital)
        return Inventory.objects.none()


class InventoryItemListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = InventoryItemSerializer
    permission_classes = [IsAdminOrStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['inventory', 'category', 'is_active', 'requires_prescription']
    search_fields = ['name', 'description', 'item_code', 'supplier']
    ordering_fields = ['name', 'current_stock', 'expiry_date', 'last_restocked']
    ordering = ['name']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_superuser:
            return InventoryItem.objects.all()
        elif hasattr(user, 'hospital_staff'):
            return InventoryItem.objects.filter(inventory__hospital=user.hospital_staff.hospital)
        return InventoryItem.objects.none()


# Emergency Contact and Insurance API Views
class EmergencyContactListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = EmergencyContactSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['patient', 'is_primary']
    ordering_fields = ['priority_order', 'created_at']
    ordering = ['patient', 'priority_order']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_superuser or hasattr(user, 'hospital_staff'):
            return EmergencyContact.objects.all()
        elif hasattr(user, 'mahalshifa_doctor_profile'):
            # Doctors can see emergency contacts for their patients
            doctor = user.mahalshifa_doctor_profile
            patient_ids = set()
            patient_ids.update(doctor.appointments.values_list('patient_id', flat=True))
            patient_ids.update(doctor.medical_records.values_list('patient_id', flat=True))
            return EmergencyContact.objects.filter(patient_id__in=patient_ids)
        else:
            # Users can see emergency contacts for their patient record
            try:
                patient = Patient.objects.filter(user_account=user).first()
                if patient:
                    return EmergencyContact.objects.filter(patient=patient)
            except:
                pass
            return EmergencyContact.objects.none()


class InsuranceListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = InsuranceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['patient', 'insurance_company', 'coverage_type', 'is_active']
    search_fields = ['insurance_company', 'policy_number', 'group_number']
    ordering_fields = ['start_date', 'end_date', 'created_at']
    ordering = ['-start_date']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_superuser or hasattr(user, 'hospital_staff'):
            return Insurance.objects.all()
        elif hasattr(user, 'mahalshifa_doctor_profile'):
            # Doctors can see insurance info for their patients
            doctor = user.mahalshifa_doctor_profile
            patient_ids = set()
            patient_ids.update(doctor.appointments.values_list('patient_id', flat=True))
            patient_ids.update(doctor.medical_records.values_list('patient_id', flat=True))
            return Insurance.objects.filter(patient_id__in=patient_ids)
        else:
            # Users can see insurance for their patient record
            try:
                patient = Patient.objects.filter(user_account=user).first()
                if patient:
                    return Insurance.objects.filter(patient=patient)
            except:
                pass
            return Insurance.objects.none()


# Search API Views
class PatientSearchAPIView(PatientAccessMixin, generics.ListAPIView):
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        serializer = PatientSearchSerializer(data=self.request.query_params)
        
        if serializer.is_valid():
            data = serializer.validated_data
            
            if data.get('its_id'):
                queryset = queryset.filter(its_id__icontains=data['its_id'])
            if data.get('name'):
                search_term = data['name']
                queryset = queryset.filter(
                    Q(first_name__icontains=search_term) |
                    Q(last_name__icontains=search_term) |
                    Q(arabic_name__icontains=search_term)
                )
            if data.get('phone_number'):
                queryset = queryset.filter(phone_number__icontains=data['phone_number'])
            if data.get('blood_group'):
                queryset = queryset.filter(blood_group=data['blood_group'])
            if data.get('registered_moze'):
                queryset = queryset.filter(registered_moze_id=data['registered_moze'])
        
        return queryset.distinct()


class AppointmentSearchAPIView(AppointmentAccessMixin, generics.ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        serializer = AppointmentSearchSerializer(data=self.request.query_params)
        
        if serializer.is_valid():
            data = serializer.validated_data
            
            if data.get('patient_id'):
                queryset = queryset.filter(patient_id=data['patient_id'])
            if data.get('doctor_id'):
                queryset = queryset.filter(doctor_id=data['doctor_id'])
            if data.get('status'):
                queryset = queryset.filter(status=data['status'])
            if data.get('appointment_type'):
                queryset = queryset.filter(appointment_type=data['appointment_type'])
            if data.get('date_from'):
                queryset = queryset.filter(appointment_date__gte=data['date_from'])
            if data.get('date_to'):
                queryset = queryset.filter(appointment_date__lte=data['date_to'])
        
        return queryset.distinct()


class DoctorSearchAPIView(generics.ListAPIView):
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_superuser or hasattr(user, 'hospital_staff'):
            queryset = Doctor.objects.all()
        else:
            queryset = Doctor.objects.filter(is_available=True)
        
        serializer = DoctorSearchSerializer(data=self.request.query_params)
        
        if serializer.is_valid():
            data = serializer.validated_data
            
            if data.get('specialization'):
                queryset = queryset.filter(specialization__icontains=data['specialization'])
            if data.get('hospital_id'):
                queryset = queryset.filter(hospital_id=data['hospital_id'])
            if data.get('department_id'):
                queryset = queryset.filter(department_id=data['department_id'])
            if data.get('is_available') is not None:
                queryset = queryset.filter(is_available=data['is_available'])
            if data.get('is_emergency_doctor') is not None:
                queryset = queryset.filter(is_emergency_doctor=data['is_emergency_doctor'])
        
        return queryset.distinct().order_by('user__first_name')


# Statistics API Views
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def hospital_stats_api(request):
    """Get hospital statistics"""
    user = request.user
    
    if user.is_admin or user.is_superuser:
        queryset = Hospital.objects.all()
    elif hasattr(user, 'mahalshifa_doctor_profile'):
        queryset = Hospital.objects.filter(id=user.mahalshifa_doctor_profile.hospital.id)
    elif hasattr(user, 'hospital_staff'):
        queryset = Hospital.objects.filter(id=user.hospital_staff.hospital.id)
    else:
        queryset = Hospital.objects.filter(is_active=True)
    
    total_hospitals = queryset.count()
    active_hospitals = queryset.filter(is_active=True).count()
    
    # Aggregate bed statistics
    bed_stats = queryset.aggregate(
        total_beds=Count('total_beds'),
        total_available=Count('available_beds')
    )
    
    total_beds = sum(h.total_beds for h in queryset)
    occupied_beds = sum(h.total_beds - h.available_beds for h in queryset)
    bed_occupancy_rate = round((occupied_beds / total_beds * 100), 2) if total_beds > 0 else 0
    
    stats = {
        'total_hospitals': total_hospitals,
        'active_hospitals': active_hospitals,
        'total_beds': total_beds,
        'occupied_beds': occupied_beds,
        'bed_occupancy_rate': bed_occupancy_rate,
    }
    
    serializer = HospitalStatsSerializer(stats)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def patient_stats_api(request):
    """Get patient statistics"""
    user = request.user
    
    if user.is_admin or user.is_superuser:
        queryset = Patient.objects.all()
    elif hasattr(user, 'mahalshifa_doctor_profile'):
        doctor = user.mahalshifa_doctor_profile
        patient_ids = set()
        patient_ids.update(doctor.appointments.values_list('patient_id', flat=True))
        patient_ids.update(doctor.medical_records.values_list('patient_id', flat=True))
        queryset = Patient.objects.filter(id__in=patient_ids)
    elif hasattr(user, 'hospital_staff'):
        hospital = user.hospital_staff.hospital
        patient_ids = set()
        patient_ids.update(
            Appointment.objects.filter(doctor__hospital=hospital).values_list('patient_id', flat=True)
        )
        queryset = Patient.objects.filter(id__in=patient_ids)
    else:
        queryset = Patient.objects.none()
    
    total_patients = queryset.count()
    active_patients = queryset.filter(is_active=True).count()
    
    # New patients this month
    current_month = timezone.now().replace(day=1)
    new_patients_this_month = queryset.filter(registration_date__gte=current_month).count()
    
    # Patients by gender
    gender_counts = queryset.values('gender').annotate(count=Count('id')).order_by('-count')
    patients_by_gender = {item['gender']: item['count'] for item in gender_counts}
    
    # Patients by blood group
    blood_group_counts = queryset.exclude(blood_group__isnull=True).values('blood_group').annotate(
        count=Count('id')
    ).order_by('-count')
    patients_by_blood_group = {item['blood_group']: item['count'] for item in blood_group_counts}
    
    stats = {
        'total_patients': total_patients,
        'active_patients': active_patients,
        'new_patients_this_month': new_patients_this_month,
        'patients_by_gender': patients_by_gender,
        'patients_by_blood_group': patients_by_blood_group,
    }
    
    serializer = PatientStatsSerializer(stats)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def appointment_stats_api(request):
    """Get appointment statistics"""
    user = request.user
    
    if user.is_admin or user.is_superuser:
        queryset = Appointment.objects.all()
    elif hasattr(user, 'mahalshifa_doctor_profile'):
        queryset = Appointment.objects.filter(doctor=user.mahalshifa_doctor_profile)
    elif hasattr(user, 'hospital_staff'):
        queryset = Appointment.objects.filter(doctor__hospital=user.hospital_staff.hospital)
    else:
        try:
            patient = Patient.objects.filter(user_account=user).first()
            if patient:
                queryset = Appointment.objects.filter(patient=patient)
            else:
                queryset = Appointment.objects.none()
        except:
            queryset = Appointment.objects.none()
    
    total_appointments = queryset.count()
    
    # Appointments today
    today = timezone.now().date()
    appointments_today = queryset.filter(appointment_date=today).count()
    
    # Appointments by status
    pending_appointments = queryset.filter(status='scheduled').count()
    completed_appointments = queryset.filter(status='completed').count()
    
    # Appointments by status breakdown
    status_counts = queryset.values('status').annotate(count=Count('id')).order_by('-count')
    appointments_by_status = {item['status']: item['count'] for item in status_counts}
    
    stats = {
        'total_appointments': total_appointments,
        'appointments_today': appointments_today,
        'pending_appointments': pending_appointments,
        'completed_appointments': completed_appointments,
        'appointments_by_status': appointments_by_status,
    }
    
    serializer = AppointmentStatsSerializer(stats)
    return Response(serializer.data)


# Dashboard API View
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def mahalshifa_dashboard_api(request):
    """Get comprehensive MahalShifa dashboard data"""
    user = request.user
    
    # Calculate stats directly based on user role
    if user.is_admin or user.is_superuser:
        hospital_queryset = Hospital.objects.all()
        patient_queryset = Patient.objects.all()
        appointment_queryset = Appointment.objects.all()
        doctor_queryset = Doctor.objects.all()
    elif hasattr(user, 'mahalshifa_doctor_profile'):
        doctor = user.mahalshifa_doctor_profile
        hospital_queryset = Hospital.objects.filter(id=doctor.hospital.id)
        
        # Patients from appointments and medical records
        patient_ids = set()
        patient_ids.update(doctor.appointments.values_list('patient_id', flat=True))
        patient_ids.update(doctor.medical_records.values_list('patient_id', flat=True))
        patient_queryset = Patient.objects.filter(id__in=patient_ids)
        appointment_queryset = Appointment.objects.filter(doctor=doctor)
        doctor_queryset = Doctor.objects.filter(hospital=doctor.hospital)
    elif hasattr(user, 'hospital_staff'):
        hospital = user.hospital_staff.hospital
        hospital_queryset = Hospital.objects.filter(id=hospital.id)
        
        patient_ids = set()
        patient_ids.update(
            Appointment.objects.filter(doctor__hospital=hospital).values_list('patient_id', flat=True)
        )
        patient_queryset = Patient.objects.filter(id__in=patient_ids)
        appointment_queryset = Appointment.objects.filter(doctor__hospital=hospital)
        doctor_queryset = Doctor.objects.filter(hospital=hospital)
    else:
        try:
            patient = Patient.objects.filter(user_account=user).first()
            if patient:
                hospital_queryset = Hospital.objects.filter(is_active=True)
                patient_queryset = Patient.objects.filter(id=patient.id)
                appointment_queryset = Appointment.objects.filter(patient=patient)
                doctor_queryset = Doctor.objects.filter(is_available=True)
            else:
                hospital_queryset = Hospital.objects.filter(is_active=True)
                patient_queryset = Patient.objects.none()
                appointment_queryset = Appointment.objects.none()
                doctor_queryset = Doctor.objects.filter(is_available=True)
        except:
            hospital_queryset = Hospital.objects.filter(is_active=True)
            patient_queryset = Patient.objects.none()
            appointment_queryset = Appointment.objects.none()
            doctor_queryset = Doctor.objects.filter(is_available=True)
    
    # Hospital stats
    total_beds = sum(h.total_beds for h in hospital_queryset)
    occupied_beds = sum(h.total_beds - h.available_beds for h in hospital_queryset)
    hospital_stats = {
        'total_hospitals': hospital_queryset.count(),
        'active_hospitals': hospital_queryset.filter(is_active=True).count(),
        'total_beds': total_beds,
        'occupied_beds': occupied_beds,
        'bed_occupancy_rate': round((occupied_beds / total_beds * 100), 2) if total_beds > 0 else 0,
    }
    
    # Patient stats
    patient_stats = {
        'total_patients': patient_queryset.count(),
        'active_patients': patient_queryset.filter(is_active=True).count(),
    }
    
    # Appointment stats
    today = timezone.now().date()
    appointment_stats = {
        'total_appointments': appointment_queryset.count(),
        'appointments_today': appointment_queryset.filter(appointment_date=today).count(),
        'pending_appointments': appointment_queryset.filter(status='scheduled').count(),
        'completed_appointments': appointment_queryset.filter(status='completed').count(),
    }
    
    # Doctor stats
    doctor_stats = {
        'total_doctors': doctor_queryset.count(),
        'available_doctors': doctor_queryset.filter(is_available=True).count(),
        'emergency_doctors': doctor_queryset.filter(is_emergency_doctor=True).count(),
    }
    
    # Recent items
    recent_appointments = appointment_queryset.order_by('-created_at')[:5]
    
    # Today's appointments
    todays_appointments = appointment_queryset.filter(
        appointment_date=today
    ).order_by('appointment_time')[:10]
    
    dashboard_data = {
        'hospital_stats': hospital_stats,
        'patient_stats': patient_stats,
        'appointment_stats': appointment_stats,
        'doctor_stats': doctor_stats,
        'recent_appointments': AppointmentSerializer(recent_appointments, many=True).data,
        'todays_appointments': AppointmentSerializer(todays_appointments, many=True).data,
    }
    
    return Response(dashboard_data)