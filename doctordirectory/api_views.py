"""
API Views for the DoctorDirectory app
"""
from rest_framework import generics, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from django.db import transaction
from datetime import datetime, timedelta

from .models import (
    Doctor, DoctorSchedule, PatientLog, DoctorAvailability,
    MedicalService, Patient, Appointment, MedicalRecord,
    Prescription, LabTest, VitalSigns
)
from .serializers import (
    DoctorSerializer, DoctorCreateSerializer, DoctorScheduleSerializer,
    PatientLogSerializer, DoctorAvailabilitySerializer, MedicalServiceSerializer,
    PatientSerializer, PatientCreateSerializer, AppointmentSerializer,
    AppointmentCreateSerializer, MedicalRecordSerializer, MedicalRecordCreateSerializer,
    PrescriptionSerializer, LabTestSerializer, VitalSignsSerializer,
    DoctorStatsSerializer, PatientStatsSerializer, AppointmentStatsSerializer,
    DoctorSearchSerializer, AppointmentSearchSerializer
)

User = get_user_model()


# Custom Permission Classes
class IsDoctorOrAdmin(permissions.BasePermission):
    """Allow access to doctors and admins only"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.is_admin or request.user.role == 'doctor'


class IsPatientOwnerOrDoctorOrAdmin(permissions.BasePermission):
    """Allow patients to access their own records, doctors to access their patients, admins full access"""
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_admin or user.is_superuser:
            return True
        
        # For Patient objects
        if hasattr(obj, 'user'):
            return obj.user == user or user.role == 'doctor'
        
        # For objects with patient field
        if hasattr(obj, 'patient'):
            return obj.patient.user == user or (user.role == 'doctor' and hasattr(user, 'doctordirectory_profile'))
        
        # For objects with doctor field
        if hasattr(obj, 'doctor') and user.role == 'doctor':
            return hasattr(user, 'doctordirectory_profile') and obj.doctor == user.doctordirectory_profile
        
        return False


# Access Control Mixins
class DoctorAccessMixin:
    """Mixin to filter doctors based on user role"""
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_superuser:
            return Doctor.objects.all()
        elif user.role == 'doctor':
            # Doctors can see all doctors for collaboration
            return Doctor.objects.all()
        elif user.role in ['aamil', 'moze_coordinator']:
            # Aamils and coordinators can see doctors in their moze
            if hasattr(user, 'managed_mozes'):
                managed_moze_ids = user.managed_mozes.values_list('id', flat=True)
                return Doctor.objects.filter(assigned_moze_id__in=managed_moze_ids)
            return Doctor.objects.none()
        else:
            # Patients can see all doctors for booking appointments
            return Doctor.objects.filter(is_available=True, is_verified=True)


class PatientAccessMixin:
    """Mixin to filter patients based on user role"""
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_superuser:
            return Patient.objects.all()
        elif user.role == 'doctor':
            # Doctors can see patients they've treated or have appointments with
            if hasattr(user, 'doctordirectory_profile'):
                doctor = user.doctordirectory_profile
                patient_ids = set()
                # Patients from appointments
                patient_ids.update(doctor.directory_appointments.values_list('patient_id', flat=True))
                # Patients from medical records
                patient_ids.update(doctor.directory_medical_records.values_list('patient_id', flat=True))
                return Patient.objects.filter(id__in=patient_ids)
            return Patient.objects.none()
        else:
            # Users can only see their own patient profile
            try:
                return Patient.objects.filter(user=user)
            except:
                return Patient.objects.none()


class AppointmentAccessMixin:
    """Mixin to filter appointments based on user role"""
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_superuser:
            return Appointment.objects.all()
        elif user.role == 'doctor':
            if hasattr(user, 'doctordirectory_profile'):
                return Appointment.objects.filter(doctor=user.doctordirectory_profile)
            return Appointment.objects.none()
        else:
            # Patients can see their own appointments
            try:
                patient = user.patient_profile
                return Appointment.objects.filter(patient=patient)
            except:
                return Appointment.objects.none()


# Doctor API Views
class DoctorListCreateAPIView(DoctorAccessMixin, generics.ListCreateAPIView):
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['specialty', 'is_verified', 'is_available', 'assigned_moze']
    search_fields = ['name', 'specialty', 'qualification', 'bio']
    ordering_fields = ['name', 'specialty', 'experience_years', 'created_at']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DoctorCreateSerializer
        return DoctorSerializer
    
    def perform_create(self, serializer):
        # Only admins can create doctor profiles
        if not (self.request.user.is_admin or self.request.user.is_superuser):
            raise PermissionDenied("Only administrators can create doctor profiles")
        serializer.save()


class DoctorDetailAPIView(DoctorAccessMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        """Custom permissions for different actions"""
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            # Get doctor ID from URL kwargs to avoid recursion
            try:
                doctor_id = self.kwargs.get('pk')
                if doctor_id:
                    user = self.request.user
                    # Check if user has permission without calling get_object()
                    if user.is_admin or user.is_superuser:
                        return [permissions.IsAuthenticated()]
                    
                    # Doctors can update their own profile
                    if user.role == 'doctor' and hasattr(user, 'doctordirectory_profile'):
                        try:
                            doctor = Doctor.objects.get(pk=doctor_id)
                            if doctor == user.doctordirectory_profile:
                                return [permissions.IsAuthenticated()]
                        except Doctor.DoesNotExist:
                            pass
                
                return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
            except (ValueError, TypeError):
                return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]


class DoctorScheduleListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = DoctorScheduleSerializer
    permission_classes = [IsDoctorOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['doctor', 'date', 'schedule_type', 'is_available']
    ordering_fields = ['date', 'start_time']
    ordering = ['date', 'start_time']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_superuser:
            return DoctorSchedule.objects.all()
        elif user.role == 'doctor' and hasattr(user, 'doctordirectory_profile'):
            return DoctorSchedule.objects.filter(doctor=user.doctordirectory_profile)
        return DoctorSchedule.objects.none()
    
    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'doctor' and hasattr(user, 'doctordirectory_profile'):
            serializer.save(doctor=user.doctordirectory_profile)
        else:
            serializer.save()


class DoctorScheduleDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DoctorScheduleSerializer
    permission_classes = [IsDoctorOrAdmin]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_superuser:
            return DoctorSchedule.objects.all()
        elif user.role == 'doctor' and hasattr(user, 'doctordirectory_profile'):
            return DoctorSchedule.objects.filter(doctor=user.doctordirectory_profile)
        return DoctorSchedule.objects.none()


class DoctorAvailabilityListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = DoctorAvailabilitySerializer
    permission_classes = [IsDoctorOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['doctor', 'day_of_week', 'is_active']
    ordering_fields = ['day_of_week', 'start_time']
    ordering = ['day_of_week', 'start_time']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_superuser:
            return DoctorAvailability.objects.all()
        elif user.role == 'doctor' and hasattr(user, 'doctordirectory_profile'):
            return DoctorAvailability.objects.filter(doctor=user.doctordirectory_profile)
        return DoctorAvailability.objects.none()
    
    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'doctor' and hasattr(user, 'doctordirectory_profile'):
            serializer.save(doctor=user.doctordirectory_profile)
        else:
            serializer.save()


class MedicalServiceListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = MedicalServiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['doctor', 'service_type', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'fee', 'duration_minutes']
    ordering = ['name']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_superuser:
            return MedicalService.objects.all()
        elif user.role == 'doctor' and hasattr(user, 'doctordirectory_profile'):
            return MedicalService.objects.filter(doctor=user.doctordirectory_profile)
        else:
            # Patients can see all active services
            return MedicalService.objects.filter(is_active=True)
    
    def perform_create(self, serializer):
        user = self.request.user
        # Only doctors can create services
        if user.role != 'doctor' or not hasattr(user, 'doctordirectory_profile'):
            raise PermissionDenied("Only doctors can create medical services")
        
        if user.role == 'doctor' and hasattr(user, 'doctordirectory_profile'):
            serializer.save(doctor=user.doctordirectory_profile)
        else:
            serializer.save()


# Patient API Views
class PatientListCreateAPIView(PatientAccessMixin, generics.ListCreateAPIView):
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['gender', 'blood_group']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    ordering_fields = ['user__first_name', 'created_at']
    ordering = ['user__first_name']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PatientCreateSerializer
        return PatientSerializer


class PatientDetailAPIView(PatientAccessMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated, IsPatientOwnerOrDoctorOrAdmin]


# PatientLog API Views
class PatientLogListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = PatientLogSerializer
    permission_classes = [IsDoctorOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['seen_by', 'moze', 'visit_type']
    search_fields = ['patient_its_id', 'patient_name', 'ailment', 'diagnosis']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_superuser:
            return PatientLog.objects.all()
        elif user.role == 'doctor' and hasattr(user, 'doctordirectory_profile'):
            return PatientLog.objects.filter(seen_by=user.doctordirectory_profile)
        return PatientLog.objects.none()
    
    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'doctor' and hasattr(user, 'doctordirectory_profile'):
            serializer.save(seen_by=user.doctordirectory_profile)
        else:
            serializer.save()


# Appointment API Views
class AppointmentListCreateAPIView(AppointmentAccessMixin, generics.ListCreateAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['doctor', 'patient', 'status', 'appointment_date']
    ordering_fields = ['appointment_date', 'appointment_time', 'created_at']
    ordering = ['-appointment_date', '-appointment_time']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AppointmentCreateSerializer
        return AppointmentSerializer


class AppointmentDetailAPIView(AppointmentAccessMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsPatientOwnerOrDoctorOrAdmin]


# Medical Record API Views
class MedicalRecordListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = MedicalRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['doctor', 'patient', 'follow_up_required']
    search_fields = ['diagnosis', 'symptoms', 'treatment_plan']
    ordering_fields = ['visit_date']
    ordering = ['-visit_date']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_superuser:
            return MedicalRecord.objects.all()
        elif user.role == 'doctor' and hasattr(user, 'doctordirectory_profile'):
            return MedicalRecord.objects.filter(doctor=user.doctordirectory_profile)
        else:
            # Patients can see their own medical records
            try:
                patient = user.patient_profile
                return MedicalRecord.objects.filter(patient=patient)
            except:
                return MedicalRecord.objects.none()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MedicalRecordCreateSerializer
        return MedicalRecordSerializer
    
    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'doctor' and hasattr(user, 'doctordirectory_profile'):
            serializer.save(doctor=user.doctordirectory_profile)
        else:
            serializer.save()


class MedicalRecordDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MedicalRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsPatientOwnerOrDoctorOrAdmin]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_superuser:
            return MedicalRecord.objects.all()
        elif user.role == 'doctor' and hasattr(user, 'doctordirectory_profile'):
            return MedicalRecord.objects.filter(doctor=user.doctordirectory_profile)
        else:
            try:
                patient = user.patient_profile
                return MedicalRecord.objects.filter(patient=patient)
            except:
                return MedicalRecord.objects.none()


# Prescription API Views
class PrescriptionListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = PrescriptionSerializer
    permission_classes = [IsDoctorOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['doctor', 'patient', 'medical_record']
    search_fields = ['medication_name', 'instructions']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_superuser:
            return Prescription.objects.all()
        elif user.role == 'doctor' and hasattr(user, 'doctordirectory_profile'):
            return Prescription.objects.filter(doctor=user.doctordirectory_profile)
        return Prescription.objects.none()


# Lab Test API Views
class LabTestListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = LabTestSerializer
    permission_classes = [IsDoctorOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['doctor', 'patient', 'test_type', 'urgency']
    search_fields = ['test_name', 'instructions']
    ordering_fields = ['test_date', 'created_at']
    ordering = ['-test_date']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_superuser:
            return LabTest.objects.all()
        elif user.role == 'doctor' and hasattr(user, 'doctordirectory_profile'):
            return LabTest.objects.filter(doctor=user.doctordirectory_profile)
        return LabTest.objects.none()


# Vital Signs API Views
class VitalSignsListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = VitalSignsSerializer
    permission_classes = [IsDoctorOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['patient', 'medical_record']
    ordering_fields = ['recorded_at']
    ordering = ['-recorded_at']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_superuser:
            return VitalSigns.objects.all()
        elif user.role == 'doctor':
            # Doctors can see vital signs for their patients
            return VitalSigns.objects.filter(
                medical_record__doctor__user=user
            )
        return VitalSigns.objects.none()


# Search API Views
class DoctorSearchAPIView(DoctorAccessMixin, generics.ListAPIView):
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Start with base queryset from access mixin
        queryset = super().get_queryset()
        
        # Apply search filters
        specialty = self.request.query_params.get('specialty')
        if specialty:
            queryset = queryset.filter(specialty__icontains=specialty)
            
        is_available = self.request.query_params.get('is_available')
        if is_available is not None:
            is_available = is_available.lower() == 'true'
            queryset = queryset.filter(is_available=is_available)
            
        is_verified = self.request.query_params.get('is_verified')
        if is_verified is not None:
            is_verified = is_verified.lower() == 'true'
            queryset = queryset.filter(is_verified=is_verified)
            
        moze_id = self.request.query_params.get('moze_id')
        if moze_id:
            queryset = queryset.filter(assigned_moze_id=moze_id)
            
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(specialty__icontains=search) |
                Q(qualification__icontains=search) |
                Q(bio__icontains=search)
            )
        
        return queryset.distinct()


class AppointmentSearchAPIView(AppointmentAccessMixin, generics.ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        serializer = AppointmentSearchSerializer(data=self.request.query_params)
        
        if serializer.is_valid():
            data = serializer.validated_data
            
            if data.get('doctor_id'):
                queryset = queryset.filter(doctor_id=data['doctor_id'])
            if data.get('patient_id'):
                queryset = queryset.filter(patient_id=data['patient_id'])
            if data.get('status'):
                queryset = queryset.filter(status=data['status'])
            if data.get('date_from'):
                queryset = queryset.filter(appointment_date__gte=data['date_from'])
            if data.get('date_to'):
                queryset = queryset.filter(appointment_date__lte=data['date_to'])
        
        return queryset.distinct()


# Statistics API Views
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def doctor_stats_api(request):
    """Get doctor statistics"""
    user = request.user
    
    if user.is_admin or user.is_superuser:
        queryset = Doctor.objects.all()
    elif user.role in ['aamil', 'moze_coordinator']:
        if hasattr(user, 'managed_mozes'):
            managed_moze_ids = user.managed_mozes.values_list('id', flat=True)
            queryset = Doctor.objects.filter(assigned_moze_id__in=managed_moze_ids)
        else:
            queryset = Doctor.objects.none()
    else:
        queryset = Doctor.objects.filter(is_available=True, is_verified=True)
    
    total_doctors = queryset.count()
    verified_doctors = queryset.filter(is_verified=True).count()
    available_doctors = queryset.filter(is_available=True).count()
    
    # Doctors by specialty
    specialty_counts = queryset.values('specialty').annotate(
        count=Count('id')
    ).order_by('-count')
    doctors_by_specialty = {item['specialty']: item['count'] for item in specialty_counts}
    
    stats = {
        'total_doctors': total_doctors,
        'verified_doctors': verified_doctors,
        'available_doctors': available_doctors,
        'doctors_by_specialty': doctors_by_specialty,
    }
    
    serializer = DoctorStatsSerializer(stats)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def patient_stats_api(request):
    """Get patient statistics"""
    user = request.user
    
    if user.is_admin or user.is_superuser:
        queryset = Patient.objects.all()
    elif user.role == 'doctor' and hasattr(user, 'doctordirectory_profile'):
        doctor = user.doctordirectory_profile
        patient_ids = set()
        patient_ids.update(doctor.directory_appointments.values_list('patient_id', flat=True))
        patient_ids.update(doctor.directory_medical_records.values_list('patient_id', flat=True))
        queryset = Patient.objects.filter(id__in=patient_ids)
    else:
        queryset = Patient.objects.none()
    
    total_patients = queryset.count()
    
    # New patients this month
    current_month = timezone.now().replace(day=1)
    new_patients_this_month = queryset.filter(created_at__gte=current_month).count()
    
    # Patients by blood group
    blood_group_counts = queryset.exclude(blood_group__isnull=True).values('blood_group').annotate(
        count=Count('id')
    ).order_by('-count')
    patients_by_blood_group = {item['blood_group']: item['count'] for item in blood_group_counts}
    
    stats = {
        'total_patients': total_patients,
        'new_patients_this_month': new_patients_this_month,
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
    elif user.role == 'doctor' and hasattr(user, 'doctordirectory_profile'):
        queryset = Appointment.objects.filter(doctor=user.doctordirectory_profile)
    else:
        try:
            patient = user.patient_profile
            queryset = Appointment.objects.filter(patient=patient)
        except:
            queryset = Appointment.objects.none()
    
    total_appointments = queryset.count()
    pending_appointments = queryset.filter(status='pending').count()
    confirmed_appointments = queryset.filter(status='confirmed').count()
    completed_appointments = queryset.filter(status='completed').count()
    cancelled_appointments = queryset.filter(status='cancelled').count()
    
    # Appointments today
    today = timezone.now().date()
    appointments_today = queryset.filter(appointment_date=today).count()
    
    stats = {
        'total_appointments': total_appointments,
        'pending_appointments': pending_appointments,
        'confirmed_appointments': confirmed_appointments,
        'completed_appointments': completed_appointments,
        'cancelled_appointments': cancelled_appointments,
        'appointments_today': appointments_today,
    }
    
    serializer = AppointmentStatsSerializer(stats)
    return Response(serializer.data)


# Dashboard API View
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def doctordirectory_dashboard_api(request):
    """Get comprehensive DoctorDirectory dashboard data"""
    user = request.user
    
    # Calculate stats directly
    if user.is_admin or user.is_superuser:
        doctor_queryset = Doctor.objects.all()
        patient_queryset = Patient.objects.all()
        appointment_queryset = Appointment.objects.all()
    elif user.role == 'doctor' and hasattr(user, 'doctordirectory_profile'):
        doctor = user.doctordirectory_profile
        doctor_queryset = Doctor.objects.all()  # Doctors can see all doctors
        
        # Patients from appointments and medical records
        patient_ids = set()
        patient_ids.update(doctor.directory_appointments.values_list('patient_id', flat=True))
        patient_ids.update(doctor.directory_medical_records.values_list('patient_id', flat=True))
        patient_queryset = Patient.objects.filter(id__in=patient_ids)
        appointment_queryset = Appointment.objects.filter(doctor=doctor)
    else:
        try:
            patient = user.patient_profile
            doctor_queryset = Doctor.objects.filter(is_available=True, is_verified=True)
            patient_queryset = Patient.objects.filter(id=patient.id)
            appointment_queryset = Appointment.objects.filter(patient=patient)
        except:
            doctor_queryset = Doctor.objects.filter(is_available=True, is_verified=True)
            patient_queryset = Patient.objects.none()
            appointment_queryset = Appointment.objects.none()
    
    # Doctor stats
    doctor_stats = {
        'total_doctors': doctor_queryset.count(),
        'verified_doctors': doctor_queryset.filter(is_verified=True).count(),
        'available_doctors': doctor_queryset.filter(is_available=True).count(),
    }
    
    # Patient stats
    patient_stats = {
        'total_patients': patient_queryset.count(),
    }
    
    # Appointment stats
    today = timezone.now().date()
    appointment_stats = {
        'total_appointments': appointment_queryset.count(),
        'pending_appointments': appointment_queryset.filter(status='pending').count(),
        'confirmed_appointments': appointment_queryset.filter(status='confirmed').count(),
        'appointments_today': appointment_queryset.filter(appointment_date=today).count(),
    }
    
    # Recent items
    recent_appointments = appointment_queryset.order_by('-created_at')[:5]
    
    # Upcoming appointments
    upcoming_appointments = appointment_queryset.filter(
        appointment_date__gte=today,
        status__in=['confirmed', 'scheduled']
    ).order_by('appointment_date', 'appointment_time')[:5]
    
    dashboard_data = {
        'doctor_stats': doctor_stats,
        'patient_stats': patient_stats,
        'appointment_stats': appointment_stats,
        'recent_appointments': AppointmentSerializer(recent_appointments, many=True).data,
        'upcoming_appointments': AppointmentSerializer(upcoming_appointments, many=True).data,
    }
    
    return Response(dashboard_data)