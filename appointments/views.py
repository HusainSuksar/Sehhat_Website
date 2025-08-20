from rest_framework import generics, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Sum
from django.utils import timezone
from datetime import datetime, timedelta, date
import calendar

from .models import (
    Appointment, TimeSlot, AppointmentLog, 
    AppointmentReminder, WaitingList, AppointmentStatus
)
from .serializers import (
    AppointmentSerializer, AppointmentCreateSerializer,
    AppointmentUpdateSerializer, AppointmentCancelSerializer,
    AppointmentRescheduleSerializer, TimeSlotSerializer,
    AppointmentLogSerializer, AppointmentReminderSerializer,
    WaitingListSerializer, DoctorAvailabilitySerializer,
    BulkTimeSlotSerializer
)
from doctordirectory.models import Doctor, Patient
from accounts.permissions import IsDoctor, IsPatient, IsOwnerOrReadOnly


class TimeSlotViewSet(viewsets.ModelViewSet):
    """ViewSet for managing time slots"""
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Filter based on user role
        if user.is_doctor:
            doctor = Doctor.objects.filter(user=user).first()
            if doctor:
                queryset = queryset.filter(doctor=doctor)
        
        # Apply filters
        doctor_id = self.request.query_params.get('doctor')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        available_only = self.request.query_params.get('available_only', 'true').lower() == 'true'
        
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)
        
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        if available_only:
            queryset = queryset.filter(is_available=True, is_booked=False)
        
        return queryset.order_by('date', 'start_time')
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Create multiple time slots at once"""
        serializer = BulkTimeSlotSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        created_slots = []
        
        current_date = data['start_date']
        while current_date <= data['end_date']:
            # Check if this weekday is included
            if 'weekdays' in data and current_date.weekday() not in data['weekdays']:
                current_date += timedelta(days=1)
                continue
            
            # Create slots for this day
            current_time = datetime.combine(current_date, data['start_time'])
            end_datetime = datetime.combine(current_date, data['end_time'])
            
            while current_time < end_datetime:
                slot_end = current_time + timedelta(minutes=data['slot_duration_minutes'])
                
                if slot_end <= end_datetime:
                    # Check if slot already exists
                    if not TimeSlot.objects.filter(
                        doctor=data['doctor'],
                        date=current_date,
                        start_time=current_time.time()
                    ).exists():
                        slot = TimeSlot.objects.create(
                            doctor=data['doctor'],
                            date=current_date,
                            start_time=current_time.time(),
                            end_time=slot_end.time(),
                            max_appointments=data['max_appointments_per_slot']
                        )
                        created_slots.append(slot)
                
                # Add break time
                current_time = slot_end + timedelta(minutes=data['break_duration_minutes'])
            
            current_date += timedelta(days=1)
        
        return Response({
            'message': f'Created {len(created_slots)} time slots',
            'slots': TimeSlotSerializer(created_slots, many=True).data
        }, status=status.HTTP_201_CREATED)


class AppointmentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing appointments"""
    queryset = Appointment.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return AppointmentCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return AppointmentUpdateSerializer
        return AppointmentSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Filter based on user role
        if user.is_doctor:
            doctor = Doctor.objects.filter(user=user).first()
            if doctor:
                queryset = queryset.filter(doctor=doctor)
        elif user.is_student:
            patient = Patient.objects.filter(user=user).first()
            if patient:
                queryset = queryset.filter(patient=patient)
        
        # Apply filters
        status_filter = self.request.query_params.get('status')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        doctor_id = self.request.query_params.get('doctor')
        patient_id = self.request.query_params.get('patient')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        if date_from:
            queryset = queryset.filter(appointment_date__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(appointment_date__lte=date_to)
        
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)
        
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        
        return queryset.select_related('doctor', 'patient', 'service').order_by('-appointment_date', '-appointment_time')
    
    def perform_create(self, serializer):
        appointment = serializer.save(booked_by=self.request.user)
        
        # Create appointment log
        AppointmentLog.objects.create(
            appointment=appointment,
            action='created',
            performed_by=self.request.user,
            notes=f'Appointment created by {self.request.user.get_full_name()}'
        )
        
        # Schedule default reminders
        self._schedule_default_reminders(appointment)
    
    def _schedule_default_reminders(self, appointment):
        """Schedule default reminders for the appointment"""
        appointment_datetime = datetime.combine(
            appointment.appointment_date,
            appointment.appointment_time
        )
        
        # 24 hours before
        AppointmentReminder.objects.create(
            appointment=appointment,
            reminder_type='email',
            scheduled_for=appointment_datetime - timedelta(hours=24)
        )
        
        # 2 hours before
        AppointmentReminder.objects.create(
            appointment=appointment,
            reminder_type='sms',
            scheduled_for=appointment_datetime - timedelta(hours=2)
        )
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm an appointment"""
        appointment = self.get_object()
        
        if appointment.status != AppointmentStatus.PENDING:
            return Response(
                {'error': 'Only pending appointments can be confirmed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        appointment.confirm(confirmed_by=request.user)
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an appointment"""
        appointment = self.get_object()
        serializer = AppointmentCancelSerializer(
            data=request.data,
            context={'appointment': appointment}
        )
        serializer.is_valid(raise_exception=True)
        
        appointment.cancel(
            cancelled_by=request.user,
            reason=serializer.validated_data['cancellation_reason']
        )
        
        return Response({
            'message': 'Appointment cancelled successfully',
            'appointment': AppointmentSerializer(appointment).data
        })
    
    @action(detail=True, methods=['post'])
    def reschedule(self, request, pk=None):
        """Reschedule an appointment"""
        appointment = self.get_object()
        serializer = AppointmentRescheduleSerializer(
            data=request.data,
            context={'appointment': appointment}
        )
        serializer.is_valid(raise_exception=True)
        
        # Create new appointment
        new_appointment = Appointment.objects.create(
            doctor=appointment.doctor,
            patient=appointment.patient,
            service=appointment.service,
            appointment_date=serializer.validated_data['new_date'],
            appointment_time=serializer.validated_data['new_time'],
            duration_minutes=appointment.duration_minutes,
            appointment_type=appointment.appointment_type,
            reason_for_visit=appointment.reason_for_visit,
            symptoms=appointment.symptoms,
            chief_complaint=appointment.chief_complaint,
            notes=appointment.notes,
            booked_by=request.user,
            booking_method=appointment.booking_method,
            consultation_fee=appointment.consultation_fee,
            rescheduled_from=appointment,
            status=AppointmentStatus.SCHEDULED
        )
        
        # Cancel old appointment
        appointment.cancel(
            cancelled_by=request.user,
            reason=f"Rescheduled to {new_appointment.appointment_date} at {new_appointment.appointment_time}"
        )
        
        # Log the reschedule
        AppointmentLog.objects.create(
            appointment=new_appointment,
            action='rescheduled',
            performed_by=request.user,
            notes=f'Rescheduled from {appointment.appointment_date} at {appointment.appointment_time}'
        )
        
        # Schedule reminders for new appointment
        self._schedule_default_reminders(new_appointment)
        
        return Response({
            'message': 'Appointment rescheduled successfully',
            'old_appointment': AppointmentSerializer(appointment).data,
            'new_appointment': AppointmentSerializer(new_appointment).data
        })
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark appointment as completed"""
        appointment = self.get_object()
        
        if appointment.status != AppointmentStatus.IN_PROGRESS:
            return Response(
                {'error': 'Only in-progress appointments can be marked as completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        notes = request.data.get('notes', '')
        appointment.complete(completed_by=request.user, notes=notes)
        
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def no_show(self, request, pk=None):
        """Mark appointment as no-show"""
        appointment = self.get_object()
        
        if appointment.is_past and appointment.status in [AppointmentStatus.CONFIRMED, AppointmentStatus.SCHEDULED]:
            appointment.status = AppointmentStatus.NO_SHOW
            appointment.save()
            
            AppointmentLog.objects.create(
                appointment=appointment,
                action='no_show',
                performed_by=request.user,
                notes='Patient did not attend the appointment'
            )
            
            return Response({
                'message': 'Appointment marked as no-show',
                'appointment': AppointmentSerializer(appointment).data
            })
        
        return Response(
            {'error': 'Cannot mark this appointment as no-show'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """Get appointment logs"""
        appointment = self.get_object()
        logs = appointment.logs.all()
        serializer = AppointmentLogSerializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming appointments"""
        queryset = self.get_queryset().filter(
            appointment_date__gte=timezone.now().date(),
            status__in=[AppointmentStatus.CONFIRMED, AppointmentStatus.SCHEDULED]
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's appointments"""
        today = timezone.now().date()
        queryset = self.get_queryset().filter(appointment_date=today)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get appointment statistics"""
        queryset = self.get_queryset()
        
        # Date range filter
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(appointment_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(appointment_date__lte=date_to)
        
        stats = {
            'total': queryset.count(),
            'by_status': dict(queryset.values_list('status').annotate(count=Count('id'))),
            'by_type': dict(queryset.values_list('appointment_type').annotate(count=Count('id'))),
            'completed': queryset.filter(status=AppointmentStatus.COMPLETED).count(),
            'cancelled': queryset.filter(status=AppointmentStatus.CANCELLED).count(),
            'no_show': queryset.filter(status=AppointmentStatus.NO_SHOW).count(),
            'revenue': queryset.filter(
                status=AppointmentStatus.COMPLETED,
                is_paid=True
            ).aggregate(total=Sum('consultation_fee'))['total'] or 0
        }
        
        return Response(stats)


class DoctorAvailabilityView(generics.GenericAPIView):
    """Check doctor availability"""
    serializer_class = DoctorAvailabilitySerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        doctor_id = serializer.validated_data['doctor_id']
        date = serializer.validated_data['date']
        duration = serializer.validated_data['duration_minutes']
        
        # Get doctor's time slots for the date
        time_slots = TimeSlot.objects.filter(
            doctor_id=doctor_id,
            date=date,
            is_available=True
        ).order_by('start_time')
        
        # Get existing appointments
        appointments = Appointment.objects.filter(
            doctor_id=doctor_id,
            appointment_date=date,
            status__in=[
                AppointmentStatus.CONFIRMED,
                AppointmentStatus.SCHEDULED,
                AppointmentStatus.IN_PROGRESS
            ]
        ).order_by('appointment_time')
        
        available_slots = []
        
        for slot in time_slots:
            if slot.can_book():
                # Check if slot duration is sufficient
                slot_duration = slot.duration_minutes
                if slot_duration >= duration:
                    # Check for conflicts with existing appointments
                    has_conflict = False
                    for appointment in appointments:
                        if (slot.start_time <= appointment.appointment_time < slot.end_time):
                            has_conflict = True
                            break
                    
                    if not has_conflict:
                        available_slots.append({
                            'slot_id': slot.id,
                            'start_time': slot.start_time,
                            'end_time': slot.end_time,
                            'duration_minutes': slot_duration
                        })
        
        return Response({
            'doctor_id': doctor_id,
            'date': date,
            'available_slots': available_slots,
            'total_slots': len(available_slots)
        })


class AppointmentReminderViewSet(viewsets.ModelViewSet):
    """ViewSet for managing appointment reminders"""
    queryset = AppointmentReminder.objects.all()
    serializer_class = AppointmentReminderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by appointment if specified
        appointment_id = self.request.query_params.get('appointment')
        if appointment_id:
            queryset = queryset.filter(appointment_id=appointment_id)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(scheduled_for__gte=date_from)
        if date_to:
            queryset = queryset.filter(scheduled_for__lte=date_to)
        
        return queryset.order_by('scheduled_for')
    
    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Manually send a reminder"""
        reminder = self.get_object()
        
        if reminder.is_sent:
            return Response(
                {'error': 'Reminder has already been sent'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Here you would implement the actual reminder sending logic
        # For now, we'll just mark it as sent
        reminder.is_sent = True
        reminder.sent_at = timezone.now()
        reminder.status = 'sent'
        reminder.save()
        
        return Response({
            'message': 'Reminder sent successfully',
            'reminder': AppointmentReminderSerializer(reminder).data
        })


class WaitingListViewSet(viewsets.ModelViewSet):
    """ViewSet for managing waiting list"""
    queryset = WaitingList.objects.all()
    serializer_class = WaitingListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Filter based on user role
        if user.is_doctor:
            doctor = Doctor.objects.filter(user=user).first()
            if doctor:
                queryset = queryset.filter(doctor=doctor)
        elif user.is_student:
            patient = Patient.objects.filter(user=user).first()
            if patient:
                queryset = queryset.filter(patient=patient)
        
        # Apply filters
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        doctor_id = self.request.query_params.get('doctor')
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)
        
        return queryset.order_by('priority', 'created_at')
    
    @action(detail=True, methods=['post'])
    def notify(self, request, pk=None):
        """Notify patient about available slot"""
        waiting_list_entry = self.get_object()
        
        # Here you would implement the notification logic
        # For now, we'll just mark as notified
        waiting_list_entry.notified = True
        waiting_list_entry.save()
        
        return Response({
            'message': 'Patient notified successfully',
            'entry': WaitingListSerializer(waiting_list_entry).data
        })
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate waiting list entry"""
        waiting_list_entry = self.get_object()
        waiting_list_entry.is_active = False
        waiting_list_entry.save()
        
        return Response({
            'message': 'Waiting list entry deactivated',
            'entry': WaitingListSerializer(waiting_list_entry).data
        })