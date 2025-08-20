from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
from .models import (
    Appointment, TimeSlot, AppointmentLog, 
    AppointmentReminder, WaitingList, AppointmentStatus, AppointmentType
)
from doctordirectory.models import Doctor, Patient, MedicalService
from doctordirectory.serializers import DoctorSerializer, PatientSerializer, MedicalServiceSerializer

User = get_user_model()


class TimeSlotSerializer(serializers.ModelSerializer):
    """Serializer for time slots"""
    doctor_name = serializers.CharField(source='doctor.get_full_name', read_only=True)
    can_book = serializers.SerializerMethodField()
    duration_minutes = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = TimeSlot
        fields = [
            'id', 'doctor', 'doctor_name', 'date', 'start_time', 'end_time',
            'is_available', 'is_booked', 'max_appointments', 'current_appointments',
            'is_recurring', 'recurring_days', 'recurring_end_date',
            'can_book', 'duration_minutes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['is_booked', 'current_appointments', 'created_at', 'updated_at']
    
    def get_can_book(self, obj):
        return obj.can_book()
    
    def validate(self, data):
        # Validate time slot duration
        if 'start_time' in data and 'end_time' in data:
            if data['start_time'] >= data['end_time']:
                raise serializers.ValidationError("End time must be after start time")
        
        # Validate date is not in the past
        if 'date' in data and data['date'] < timezone.now().date():
            raise serializers.ValidationError("Cannot create time slots for past dates")
        
        return data


class AppointmentSerializer(serializers.ModelSerializer):
    """Comprehensive appointment serializer"""
    doctor_name = serializers.CharField(source='doctor.get_full_name', read_only=True)
    patient_name = serializers.SerializerMethodField()
    service_name = serializers.CharField(source='service.name', read_only=True)
    appointment_type_display = serializers.CharField(source='get_appointment_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    end_time = serializers.TimeField(read_only=True)
    is_upcoming = serializers.BooleanField(read_only=True)
    is_past = serializers.BooleanField(read_only=True)
    can_cancel = serializers.SerializerMethodField()
    can_reschedule = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'appointment_id', 'doctor', 'doctor_name', 'patient', 'patient_name',
            'time_slot', 'service', 'service_name', 'appointment_date', 'appointment_time',
            'duration_minutes', 'appointment_type', 'appointment_type_display',
            'status', 'status_display', 'reason_for_visit', 'symptoms', 'chief_complaint',
            'notes', 'doctor_notes', 'booked_by', 'booking_method', 'consultation_fee',
            'is_paid', 'payment_method', 'requires_confirmation', 'confirmation_sent',
            'reminder_sent', 'follow_up_required', 'follow_up_date', 'cancelled_at',
            'cancelled_by', 'cancellation_reason', 'rescheduled_from', 'created_at',
            'updated_at', 'confirmed_at', 'completed_at', 'end_time', 'is_upcoming',
            'is_past', 'can_cancel', 'can_reschedule'
        ]
        read_only_fields = [
            'appointment_id', 'booked_by', 'cancelled_at', 'cancelled_by',
            'confirmed_at', 'completed_at', 'created_at', 'updated_at'
        ]
    
    def get_patient_name(self, obj):
        return obj.patient.user.get_full_name() if obj.patient.user else 'Unknown Patient'
    
    def get_can_cancel(self, obj):
        return obj.can_cancel()
    
    def get_can_reschedule(self, obj):
        return obj.can_reschedule()
    
    def validate(self, data):
        # Validate appointment date
        if 'appointment_date' in data:
            if data['appointment_date'] < timezone.now().date():
                raise serializers.ValidationError({
                    'appointment_date': 'Appointment date cannot be in the past'
                })
        
        # Validate appointment doesn't conflict
        if self.instance is None:  # Creating new appointment
            doctor = data.get('doctor')
            appointment_date = data.get('appointment_date')
            appointment_time = data.get('appointment_time')
            
            if doctor and appointment_date and appointment_time:
                conflicting = Appointment.objects.filter(
                    doctor=doctor,
                    appointment_date=appointment_date,
                    appointment_time=appointment_time,
                    status__in=[
                        AppointmentStatus.CONFIRMED,
                        AppointmentStatus.SCHEDULED,
                        AppointmentStatus.IN_PROGRESS
                    ]
                ).exists()
                
                if conflicting:
                    raise serializers.ValidationError({
                        'appointment_time': 'This time slot is already booked'
                    })
        
        return data
    
    def create(self, validated_data):
        # Set booked_by to current user
        validated_data['booked_by'] = self.context['request'].user
        return super().create(validated_data)


class AppointmentCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating appointments"""
    available_slots = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = [
            'doctor', 'patient', 'service', 'appointment_date', 'appointment_time',
            'duration_minutes', 'appointment_type', 'reason_for_visit', 'symptoms',
            'chief_complaint', 'notes', 'booking_method', 'available_slots'
        ]
    
    def get_available_slots(self, obj):
        """Get available time slots for the selected doctor and date"""
        request = self.context.get('request')
        if request and hasattr(request, 'query_params'):
            doctor_id = request.query_params.get('doctor')
            date = request.query_params.get('date')
            
            if doctor_id and date:
                slots = TimeSlot.objects.filter(
                    doctor_id=doctor_id,
                    date=date,
                    is_available=True,
                    is_booked=False
                ).values('id', 'start_time', 'end_time')
                return list(slots)
        return []


class AppointmentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating appointments"""
    class Meta:
        model = Appointment
        fields = [
            'appointment_date', 'appointment_time', 'duration_minutes',
            'status', 'notes', 'doctor_notes', 'follow_up_required',
            'follow_up_date'
        ]
    
    def validate_status(self, value):
        if self.instance and self.instance.status == AppointmentStatus.COMPLETED:
            raise serializers.ValidationError("Cannot update completed appointments")
        return value


class AppointmentCancelSerializer(serializers.Serializer):
    """Serializer for cancelling appointments"""
    cancellation_reason = serializers.CharField(required=True, max_length=500)
    
    def validate(self, data):
        appointment = self.context.get('appointment')
        if not appointment.can_cancel():
            raise serializers.ValidationError("This appointment cannot be cancelled")
        return data


class AppointmentRescheduleSerializer(serializers.Serializer):
    """Serializer for rescheduling appointments"""
    new_date = serializers.DateField()
    new_time = serializers.TimeField()
    reason = serializers.CharField(required=False, max_length=500)
    
    def validate(self, data):
        appointment = self.context.get('appointment')
        
        if not appointment.can_reschedule():
            raise serializers.ValidationError("This appointment cannot be rescheduled")
        
        # Check if new slot is available
        new_date = data['new_date']
        new_time = data['new_time']
        
        if new_date < timezone.now().date():
            raise serializers.ValidationError({
                'new_date': 'Cannot reschedule to a past date'
            })
        
        # Check for conflicts
        conflicting = Appointment.objects.filter(
            doctor=appointment.doctor,
            appointment_date=new_date,
            appointment_time=new_time,
            status__in=[
                AppointmentStatus.CONFIRMED,
                AppointmentStatus.SCHEDULED
            ]
        ).exclude(id=appointment.id).exists()
        
        if conflicting:
            raise serializers.ValidationError({
                'new_time': 'This time slot is already booked'
            })
        
        return data


class AppointmentLogSerializer(serializers.ModelSerializer):
    """Serializer for appointment logs"""
    performed_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = AppointmentLog
        fields = [
            'id', 'appointment', 'action', 'performed_by', 'performed_by_name',
            'timestamp', 'notes', 'old_values', 'new_values'
        ]
    
    def get_performed_by_name(self, obj):
        return obj.performed_by.get_full_name() if obj.performed_by else 'System'


class AppointmentReminderSerializer(serializers.ModelSerializer):
    """Serializer for appointment reminders"""
    appointment_details = serializers.SerializerMethodField()
    
    class Meta:
        model = AppointmentReminder
        fields = [
            'id', 'appointment', 'appointment_details', 'reminder_type',
            'scheduled_for', 'sent_at', 'is_sent', 'status', 'error_message',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['sent_at', 'is_sent', 'status', 'error_message']
    
    def get_appointment_details(self, obj):
        return {
            'id': obj.appointment.id,
            'date': obj.appointment.appointment_date,
            'time': obj.appointment.appointment_time,
            'doctor': obj.appointment.doctor.get_full_name(),
            'patient': obj.appointment.patient.user.get_full_name() if obj.appointment.patient.user else 'Unknown'
        }


class WaitingListSerializer(serializers.ModelSerializer):
    """Serializer for waiting list"""
    patient_name = serializers.SerializerMethodField()
    doctor_name = serializers.CharField(source='doctor.get_full_name', read_only=True)
    
    class Meta:
        model = WaitingList
        fields = [
            'id', 'patient', 'patient_name', 'doctor', 'doctor_name',
            'preferred_date', 'preferred_time_start', 'preferred_time_end',
            'appointment_type', 'reason', 'priority', 'is_active',
            'notified', 'created_at', 'updated_at'
        ]
        read_only_fields = ['notified', 'created_at', 'updated_at']
    
    def get_patient_name(self, obj):
        return obj.patient.user.get_full_name() if obj.patient.user else 'Unknown Patient'
    
    def validate(self, data):
        if 'preferred_date' in data and data['preferred_date'] < timezone.now().date():
            raise serializers.ValidationError({
                'preferred_date': 'Preferred date cannot be in the past'
            })
        
        if 'preferred_time_start' in data and 'preferred_time_end' in data:
            if data['preferred_time_start'] and data['preferred_time_end']:
                if data['preferred_time_start'] >= data['preferred_time_end']:
                    raise serializers.ValidationError({
                        'preferred_time_end': 'End time must be after start time'
                    })
        
        return data


class DoctorAvailabilitySerializer(serializers.Serializer):
    """Serializer for checking doctor availability"""
    doctor_id = serializers.IntegerField()
    date = serializers.DateField()
    duration_minutes = serializers.IntegerField(default=30)
    
    def validate_date(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError("Cannot check availability for past dates")
        return value


class BulkTimeSlotSerializer(serializers.Serializer):
    """Serializer for creating multiple time slots"""
    doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()
    slot_duration_minutes = serializers.IntegerField(default=30)
    break_duration_minutes = serializers.IntegerField(default=0)
    weekdays = serializers.ListField(
        child=serializers.IntegerField(min_value=0, max_value=6),
        required=False,
        help_text="List of weekday numbers (0=Monday, 6=Sunday)"
    )
    max_appointments_per_slot = serializers.IntegerField(default=1)
    
    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError({
                'end_date': 'End date must be after or equal to start date'
            })
        
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError({
                'end_time': 'End time must be after start time'
            })
        
        if data['start_date'] < timezone.now().date():
            raise serializers.ValidationError({
                'start_date': 'Cannot create slots for past dates'
            })
        
        return data