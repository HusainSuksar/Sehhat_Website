"""
API Views for the DoctorDirectory app
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta

from .models import (
    Doctor, DoctorSchedule, MedicalService, Patient, Appointment
)
from .serializers import (
    DoctorSerializer, DoctorCreateSerializer, DoctorScheduleSerializer,
    MedicalServiceSerializer, PatientSerializer, PatientCreateSerializer, 
    AppointmentSerializer, AppointmentCreateSerializer, AppointmentUpdateSerializer,
    DoctorStatsSerializer, AppointmentStatsSerializer, SystemStatsSerializer
)
from accounts.models import User


# Custom Permission Classes
class IsDoctorOrAdmin(permissions.BasePermission):
    """Allow access to doctors and admins only"""
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                (request.user.is_doctor or request.user.is_admin))


class IsPatientOwnerOrDoctorOrAdmin(permissions.BasePermission):
    """Allow access to patient owner, doctors, or admins"""
    def has_object_permission(self, request, view, obj):
        if request.user.is_admin or request.user.is_doctor:
            return True
        # For patients - check if they own the record
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False


# Custom Pagination
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# Doctor ViewSet
class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.select_related('user', 'assigned_moze').prefetch_related('medical_services')
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['specialty', 'is_available', 'assigned_moze']
    search_fields = ['user__first_name', 'user__last_name', 'specialty', 'qualification', 'bio']
    ordering_fields = ['user__first_name', 'specialty', 'experience_years', 'created_at']
    ordering = ['user__first_name']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DoctorCreateSerializer
        return DoctorSerializer
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get statistics for a specific doctor"""
        doctor = self.get_object()
        appointments = Appointment.objects.filter(doctor=doctor)
        
        stats = {
            'total_appointments': appointments.count(),
            'completed_appointments': appointments.filter(status='completed').count(),
            'pending_appointments': appointments.filter(status='pending').count(),
            'cancelled_appointments': appointments.filter(status='cancelled').count(),
            'total_patients': appointments.values('patient').distinct().count(),
        }
        
        total = stats['total_appointments']
        if total > 0:
            stats['completion_rate'] = round((stats['completed_appointments'] / total) * 100, 1)
        else:
            stats['completion_rate'] = 0
        
        serializer = DoctorStatsSerializer(stats)
        return Response(serializer.data)


# Patient ViewSet
class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.select_related('user').prefetch_related('appointments')
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated, IsPatientOwnerOrDoctorOrAdmin]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['gender', 'blood_group']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    ordering_fields = ['user__first_name', 'created_at']
    ordering = ['user__first_name']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PatientCreateSerializer
        return PatientSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Filter based on user role
        if user.is_admin:
            return queryset
        elif user.is_doctor:
            # Doctors can see patients they have appointments with
            try:
                doctor = Doctor.objects.get(user=user)
                return queryset.filter(appointments__doctor=doctor).distinct()
            except Doctor.DoesNotExist:
                return queryset.none()
        else:
            # Regular users can only see their own patient record
            return queryset.filter(user=user)


# Appointment ViewSet
class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.select_related(
        'doctor', 'patient__user'
    ).prefetch_related('doctor__medical_services')
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['doctor', 'patient', 'status', 'appointment_date']
    ordering_fields = ['appointment_date', 'appointment_time', 'created_at']
    ordering = ['-appointment_date', '-appointment_time']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return AppointmentCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return AppointmentUpdateSerializer
        return AppointmentSerializer
    
    def perform_create(self, serializer):
        serializer.save()
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Filter based on user role
        if user.is_admin:
            return queryset
        elif user.is_doctor:
            try:
                doctor = Doctor.objects.get(user=user)
                return queryset.filter(doctor=doctor)
            except Doctor.DoesNotExist:
                return queryset.none()
        else:
            # Regular users can see appointments where they are the patient
            return queryset.filter(patient__user=user)
    
    @action(detail=True, methods=['post'], url_path='update-status')
    def update_status(self, request, pk=None):
        """Update appointment status"""
        appointment = self.get_object()
        new_status = request.data.get('status')
        reason = request.data.get('reason', '')
        
        # Validate status
        valid_statuses = ['scheduled', 'confirmed', 'in_progress', 'completed', 'cancelled', 'no_show']
        if new_status not in valid_statuses:
            return Response({
                'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check permissions for status changes
        user = request.user
        if not (user.is_admin or user.is_doctor or 
                (hasattr(user, 'patient_profile') and appointment.patient.user == user)):
            return Response({
                'error': 'You do not have permission to update this appointment.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Patients can only cancel their appointments
        if (hasattr(user, 'patient_profile') and appointment.patient.user == user and 
            new_status != 'cancelled'):
            return Response({
                'error': 'Patients can only cancel their appointments.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Update appointment status
        old_status = appointment.status
        appointment.status = new_status
        
        # Handle cancellation reason
        if new_status == 'cancelled' and reason:
            appointment.cancellation_reason = reason
        
        appointment.save()
        
        return Response({
            'message': f'Appointment status updated from {old_status} to {new_status}',
            'appointment': AppointmentSerializer(appointment).data
        })
    
    @action(detail=True, methods=['get'], url_path='status')
    def get_status(self, request, pk=None):
        """Get current appointment status"""
        appointment = self.get_object()
        return Response({
            'status': appointment.status,
            'status_display': appointment.get_status_display(),
            'last_updated': appointment.updated_at if hasattr(appointment, 'updated_at') else None
        })


# DoctorSchedule ViewSet
class DoctorScheduleViewSet(viewsets.ModelViewSet):
    queryset = DoctorSchedule.objects.select_related('doctor__user')
    serializer_class = DoctorScheduleSerializer
    permission_classes = [IsDoctorOrAdmin]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['doctor', 'date', 'is_available']
    ordering_fields = ['date', 'start_time']
    ordering = ['date', 'start_time']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Filter based on user role
        if user.is_admin:
            return queryset
        elif user.is_doctor:
            try:
                doctor = Doctor.objects.get(user=user)
                return queryset.filter(doctor=doctor)
            except Doctor.DoesNotExist:
                return queryset.none()
        return queryset.none()


# MedicalService ViewSet
class MedicalServiceViewSet(viewsets.ModelViewSet):
    queryset = MedicalService.objects.select_related('doctor__user')
    serializer_class = MedicalServiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['doctor', 'is_available']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'duration_minutes']
    ordering = ['name']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Filter based on user role
        if user.is_admin:
            return queryset
        elif user.is_doctor:
            try:
                doctor = Doctor.objects.get(user=user)
                return queryset.filter(doctor=doctor)
            except Doctor.DoesNotExist:
                return queryset.none()
        else:
            # Non-doctors can only see active services
            return queryset.filter(is_available=True)


# Statistics API Views
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def system_stats(request):
    """Get overall system statistics"""
    if not (request.user.is_admin or request.user.is_doctor):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    today = timezone.now().date()
    
    # Basic counts
    total_doctors = Doctor.objects.filter(is_available=True).count()
    total_patients = Patient.objects.count()
    total_appointments = Appointment.objects.count()
    appointments_today = Appointment.objects.filter(appointment_date=today).count()
    
    # Doctor stats
    doctor_appointments = Appointment.objects.all()
    doctor_stats = {
        'total_appointments': doctor_appointments.count(),
        'completed_appointments': doctor_appointments.filter(status='completed').count(),
        'pending_appointments': doctor_appointments.filter(status='pending').count(),
        'cancelled_appointments': doctor_appointments.filter(status='cancelled').count(),
        'completion_rate': 0,
        'total_patients': doctor_appointments.values('patient').distinct().count(),
    }
    
    if doctor_stats['total_appointments'] > 0:
        doctor_stats['completion_rate'] = round(
            (doctor_stats['completed_appointments'] / doctor_stats['total_appointments']) * 100, 1
        )
    
    # Appointment stats
    this_week_start = today - timedelta(days=today.weekday())
    this_month_start = today.replace(day=1)
    
    appointment_stats = {
        'total_appointments': total_appointments,
        'appointments_today': appointments_today,
        'appointments_this_week': Appointment.objects.filter(
            appointment_date__gte=this_week_start
        ).count(),
        'appointments_this_month': Appointment.objects.filter(
            appointment_date__gte=this_month_start
        ).count(),
        'by_status': {},
        'by_doctor': []
    }
    
    # Status breakdown
    status_counts = Appointment.objects.values('status').annotate(count=Count('id'))
    appointment_stats['by_status'] = {item['status']: item['count'] for item in status_counts}
    
    # Top doctors by appointment count
    doctor_counts = Appointment.objects.values(
        'doctor__user__first_name', 'doctor__user__last_name'
    ).annotate(count=Count('id')).order_by('-count')[:5]
    
    appointment_stats['by_doctor'] = [
        {
            'name': f"{item['doctor__user__first_name']} {item['doctor__user__last_name']}",
            'appointments': item['count']
        }
        for item in doctor_counts
    ]
    
    stats = {
        'total_doctors': total_doctors,
        'active_doctors': total_doctors,  # Assuming active doctors are counted
        'total_patients': total_patients,
        'total_appointments': total_appointments,
        'appointments_today': appointments_today,
        'doctor_stats': doctor_stats,
        'appointment_stats': appointment_stats
    }
    
    serializer = SystemStatsSerializer(stats)
    return Response(serializer.data)


# Search API
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def search_doctors(request):
    """Search doctors with filters"""
    queryset = Doctor.objects.filter(is_available=True).select_related('assigned_moze')
    
    # Search parameters
    search = request.GET.get('search', '').strip()
    specialty = request.GET.get('specialty', '').strip()
    available_today = request.GET.get('available_today', '').lower() == 'true'
    
    if search:
        queryset = queryset.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(specialty__icontains=search) |
            Q(bio__icontains=search)
        )
    
    if specialty:
        queryset = queryset.filter(specialty__icontains=specialty)
    
    if available_today:
        today = timezone.now().date()
        queryset = queryset.filter(
            schedules__date=today,
            schedules__is_available=True
        ).distinct()
    
    # Pagination
    paginator = StandardResultsSetPagination()
    page = paginator.paginate_queryset(queryset, request)
    
    if page is not None:
        serializer = DoctorSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    serializer = DoctorSerializer(queryset, many=True)
    return Response(serializer.data)