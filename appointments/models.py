from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

User = get_user_model()


class AppointmentStatus:
    """Constants for appointment statuses"""
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    SCHEDULED = 'scheduled'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    NO_SHOW = 'no_show'
    RESCHEDULED = 'rescheduled'

    CHOICES = [
        (PENDING, 'Pending Confirmation'),
        (CONFIRMED, 'Confirmed'),
        (SCHEDULED, 'Scheduled'),
        (IN_PROGRESS, 'In Progress'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
        (NO_SHOW, 'No Show'),
        (RESCHEDULED, 'Rescheduled'),
    ]


class AppointmentType:
    """Constants for appointment types"""
    CONSULTATION = 'consultation'
    FOLLOW_UP = 'follow_up'
    EMERGENCY = 'emergency'
    SCREENING = 'screening'
    VACCINATION = 'vaccination'
    TEST = 'test'
    THERAPY = 'therapy'
    
    CHOICES = [
        (CONSULTATION, 'General Consultation'),
        (FOLLOW_UP, 'Follow-up Visit'),
        (EMERGENCY, 'Emergency'),
        (SCREENING, 'Health Screening'),
        (VACCINATION, 'Vaccination'),
        (TEST, 'Medical Test'),
        (THERAPY, 'Therapy Session'),
    ]


class TimeSlot(models.Model):
    """Available time slots for appointments"""
    doctor = models.ForeignKey(
        'doctordirectory.Doctor',
        on_delete=models.CASCADE,
        related_name='time_slots'
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    is_booked = models.BooleanField(default=False)
    max_appointments = models.PositiveIntegerField(default=1)
    current_appointments = models.PositiveIntegerField(default=0)
    
    # For recurring slots
    is_recurring = models.BooleanField(default=False)
    recurring_days = models.CharField(
        max_length=20,
        blank=True,
        help_text="Comma-separated weekday numbers (0=Monday, 6=Sunday)"
    )
    recurring_end_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['date', 'start_time']
        unique_together = ['doctor', 'date', 'start_time']
        indexes = [
            models.Index(fields=['doctor', 'date', 'is_available']),
            models.Index(fields=['date', 'is_available', 'is_booked']),
        ]
    
    def __str__(self):
        return f"{self.doctor} - {self.date} {self.start_time}-{self.end_time}"
    
    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time")
        
        if self.current_appointments > self.max_appointments:
            raise ValidationError("Current appointments cannot exceed max appointments")
    
    @property
    def duration_minutes(self):
        """Calculate slot duration in minutes"""
        start_datetime = datetime.combine(self.date, self.start_time)
        end_datetime = datetime.combine(self.date, self.end_time)
        return int((end_datetime - start_datetime).total_seconds() / 60)
    
    def can_book(self):
        """Check if this slot can be booked"""
        return (
            self.is_available and 
            not self.is_booked and 
            self.current_appointments < self.max_appointments and
            self.date >= timezone.now().date()
        )


class Appointment(models.Model):
    """Enhanced appointment model with comprehensive features"""
    
    # Unique identifier
    appointment_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    
    # Core relationships
    doctor = models.ForeignKey(
        'doctordirectory.Doctor',
        on_delete=models.CASCADE,
        related_name='doctor_appointments'
    )
    patient = models.ForeignKey(
        'doctordirectory.Patient',
        on_delete=models.CASCADE,
        related_name='patient_appointments'
    )
    time_slot = models.ForeignKey(
        TimeSlot,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='appointments'
    )
    service = models.ForeignKey(
        'doctordirectory.MedicalService',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='service_appointments'
    )
    
    # Appointment details
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField(
        default=30,
        validators=[MinValueValidator(15), MaxValueValidator(180)]
    )
    appointment_type = models.CharField(
        max_length=20,
        choices=AppointmentType.CHOICES,
        default=AppointmentType.CONSULTATION
    )
    status = models.CharField(
        max_length=20,
        choices=AppointmentStatus.CHOICES,
        default=AppointmentStatus.PENDING
    )
    
    # Medical information
    reason_for_visit = models.TextField()
    symptoms = models.TextField(blank=True)
    chief_complaint = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    doctor_notes = models.TextField(blank=True)
    
    # Booking information
    booked_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='booked_appointments'
    )
    booking_method = models.CharField(
        max_length=20,
        choices=[
            ('online', 'Online'),
            ('phone', 'Phone'),
            ('walk_in', 'Walk-in'),
            ('referral', 'Referral'),
        ],
        default='online'
    )
    
    # Payment information
    consultation_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    is_paid = models.BooleanField(default=False)
    payment_method = models.CharField(
        max_length=20,
        choices=[
            ('cash', 'Cash'),
            ('card', 'Card'),
            ('insurance', 'Insurance'),
            ('online', 'Online Payment'),
        ],
        blank=True
    )
    
    # Additional features
    requires_confirmation = models.BooleanField(default=True)
    confirmation_sent = models.BooleanField(default=False)
    reminder_sent = models.BooleanField(default=False)
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    
    # Cancellation/Rescheduling
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancelled_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cancelled_appointments'
    )
    cancellation_reason = models.TextField(blank=True)
    rescheduled_from = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rescheduled_to'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-appointment_date', '-appointment_time']
        indexes = [
            models.Index(fields=['doctor', 'appointment_date', 'status']),
            models.Index(fields=['patient', 'appointment_date', 'status']),
            models.Index(fields=['appointment_date', 'appointment_time']),
            models.Index(fields=['status', 'appointment_date']),
            models.Index(fields=['appointment_id']),
        ]
    
    def __str__(self):
        patient_name = self.patient.user.get_full_name() if self.patient.user else 'Unknown Patient'
        return f"{patient_name} - Dr. {self.doctor.get_full_name()} on {self.appointment_date} at {self.appointment_time}"
    
    def clean(self):
        # Validate appointment date is not in the past
        if self.appointment_date < timezone.now().date():
            raise ValidationError("Appointment date cannot be in the past")
        
        # Validate appointment doesn't conflict with existing appointments
        if self.pk is None:  # Only for new appointments
            conflicting = Appointment.objects.filter(
                doctor=self.doctor,
                appointment_date=self.appointment_date,
                appointment_time=self.appointment_time,
                status__in=[
                    AppointmentStatus.CONFIRMED,
                    AppointmentStatus.SCHEDULED,
                    AppointmentStatus.IN_PROGRESS
                ]
            ).exists()
            if conflicting:
                raise ValidationError("This time slot is already booked")
    
    def save(self, *args, **kwargs):
        # Auto-set consultation fee from doctor or service
        if not self.consultation_fee and self.doctor:
            self.consultation_fee = self.doctor.consultation_fee
        
        # Update time slot booking status
        if self.time_slot:
            self.time_slot.current_appointments = self.time_slot.appointments.filter(
                status__in=[AppointmentStatus.CONFIRMED, AppointmentStatus.SCHEDULED]
            ).count()
            if self.time_slot.current_appointments >= self.time_slot.max_appointments:
                self.time_slot.is_booked = True
            self.time_slot.save()
        
        super().save(*args, **kwargs)
    
    @property
    def end_time(self):
        """Calculate appointment end time"""
        start_datetime = datetime.combine(self.appointment_date, self.appointment_time)
        end_datetime = start_datetime + timedelta(minutes=self.duration_minutes)
        return end_datetime.time()
    
    @property
    def is_upcoming(self):
        """Check if appointment is in the future"""
        appointment_datetime = datetime.combine(self.appointment_date, self.appointment_time)
        return appointment_datetime > timezone.now()
    
    @property
    def is_past(self):
        """Check if appointment is in the past"""
        appointment_datetime = datetime.combine(self.appointment_date, self.appointment_time)
        return appointment_datetime < timezone.now()
    
    def can_cancel(self):
        """Check if appointment can be cancelled"""
        return (
            self.status not in [
                AppointmentStatus.COMPLETED,
                AppointmentStatus.CANCELLED
            ] and
            self.is_upcoming
        )
    
    def can_reschedule(self):
        """Check if appointment can be rescheduled"""
        return self.can_cancel()
    
    def confirm(self, confirmed_by=None):
        """Confirm the appointment"""
        self.status = AppointmentStatus.CONFIRMED
        self.confirmed_at = timezone.now()
        self.save()
        
        # Create confirmation log
        AppointmentLog.objects.create(
            appointment=self,
            action='confirmed',
            performed_by=confirmed_by,
            notes=f"Appointment confirmed"
        )
    
    def cancel(self, cancelled_by=None, reason=''):
        """Cancel the appointment"""
        self.status = AppointmentStatus.CANCELLED
        self.cancelled_at = timezone.now()
        self.cancelled_by = cancelled_by
        self.cancellation_reason = reason
        self.save()
        
        # Free up the time slot
        if self.time_slot:
            self.time_slot.current_appointments -= 1
            self.time_slot.is_booked = False
            self.time_slot.save()
        
        # Create cancellation log
        AppointmentLog.objects.create(
            appointment=self,
            action='cancelled',
            performed_by=cancelled_by,
            notes=f"Appointment cancelled. Reason: {reason}"
        )
    
    def complete(self, completed_by=None, notes=''):
        """Mark appointment as completed"""
        self.status = AppointmentStatus.COMPLETED
        self.completed_at = timezone.now()
        if notes:
            self.doctor_notes = notes
        self.save()
        
        # Create completion log
        AppointmentLog.objects.create(
            appointment=self,
            action='completed',
            performed_by=completed_by,
            notes=f"Appointment completed"
        )


class AppointmentLog(models.Model):
    """Track all changes to appointments"""
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    action = models.CharField(
        max_length=50,
        choices=[
            ('created', 'Created'),
            ('updated', 'Updated'),
            ('confirmed', 'Confirmed'),
            ('cancelled', 'Cancelled'),
            ('rescheduled', 'Rescheduled'),
            ('completed', 'Completed'),
            ('no_show', 'Marked as No Show'),
            ('reminder_sent', 'Reminder Sent'),
        ]
    )
    performed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    old_values = models.JSONField(default=dict, blank=True)
    new_values = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.appointment} - {self.action} at {self.timestamp}"


class AppointmentReminder(models.Model):
    """Manage appointment reminders"""
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name='reminders'
    )
    reminder_type = models.CharField(
        max_length=20,
        choices=[
            ('email', 'Email'),
            ('sms', 'SMS'),
            ('whatsapp', 'WhatsApp'),
            ('push', 'Push Notification'),
        ]
    )
    scheduled_for = models.DateTimeField()
    sent_at = models.DateTimeField(null=True, blank=True)
    is_sent = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('sent', 'Sent'),
            ('failed', 'Failed'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending'
    )
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['scheduled_for']
        indexes = [
            models.Index(fields=['scheduled_for', 'is_sent']),
            models.Index(fields=['appointment', 'reminder_type']),
        ]
    
    def __str__(self):
        return f"Reminder for {self.appointment} - {self.reminder_type} at {self.scheduled_for}"


class WaitingList(models.Model):
    """Manage waiting list for appointments"""
    patient = models.ForeignKey(
        'doctordirectory.Patient',
        on_delete=models.CASCADE,
        related_name='waiting_list_entries'
    )
    doctor = models.ForeignKey(
        'doctordirectory.Doctor',
        on_delete=models.CASCADE,
        related_name='waiting_list'
    )
    preferred_date = models.DateField()
    preferred_time_start = models.TimeField(null=True, blank=True)
    preferred_time_end = models.TimeField(null=True, blank=True)
    appointment_type = models.CharField(
        max_length=20,
        choices=AppointmentType.CHOICES,
        default=AppointmentType.CONSULTATION
    )
    reason = models.TextField()
    priority = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="1=Highest priority, 10=Lowest priority"
    )
    is_active = models.BooleanField(default=True)
    notified = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['priority', 'created_at']
        indexes = [
            models.Index(fields=['doctor', 'preferred_date', 'is_active']),
            models.Index(fields=['patient', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.patient} waiting for {self.doctor} on {self.preferred_date}"