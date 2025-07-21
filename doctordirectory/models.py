from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from moze.models import Moze


class Doctor(models.Model):
    """Doctor profile linked to User model"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_profile',
        limit_choices_to={'role': 'doctor'}
    )
    name = models.CharField(max_length=100)  # Can be different from user's name
    its_id = models.CharField(
        max_length=8,
        unique=True,
        validators=[RegexValidator(
            regex=r'^\d{8}$',
            message='ITS ID must be exactly 8 digits'
        )]
    )
    specialty = models.CharField(max_length=100)
    qualification = models.CharField(max_length=200, blank=True, null=True)
    experience_years = models.PositiveIntegerField(default=0)
    verified_certificate = models.FileField(upload_to='doctor_certificates/', blank=True, null=True)
    assigned_moze = models.ForeignKey(
        Moze,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_doctors'
    )
    is_verified = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    license_number = models.CharField(max_length=50, blank=True, null=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Contact information
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    # Professional details
    languages_spoken = models.CharField(max_length=200, blank=True, null=True, help_text='Comma-separated languages')
    bio = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Doctor'
        verbose_name_plural = 'Doctors'
        ordering = ['name']
    
    def __str__(self):
        return f"Dr. {self.name} - {self.specialty}"
    
    def get_full_name(self):
        return f"Dr. {self.name}"
    
    def get_current_schedule(self):
        from django.utils import timezone
        today = timezone.now().date()
        return self.schedules.filter(date=today).first()


class DoctorSchedule(models.Model):
    """Doctor's schedule for specific dates and times"""
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='schedules')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    moze = models.ForeignKey(Moze, on_delete=models.CASCADE, related_name='doctor_schedules')
    is_available = models.BooleanField(default=True)
    max_patients = models.PositiveIntegerField(default=20)
    notes = models.TextField(blank=True, null=True)
    
    # Schedule type
    SCHEDULE_TYPES = [
        ('regular', 'Regular'),
        ('emergency', 'Emergency'),
        ('special', 'Special Clinic'),
    ]
    schedule_type = models.CharField(max_length=20, choices=SCHEDULE_TYPES, default='regular')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['doctor', 'date', 'start_time']
        ordering = ['date', 'start_time']
        verbose_name = 'Doctor Schedule'
        verbose_name_plural = 'Doctor Schedules'
    
    def __str__(self):
        return f"{self.doctor.name} - {self.date} ({self.start_time}-{self.end_time})"
    
    def is_current(self):
        from django.utils import timezone
        now = timezone.now()
        return (self.date == now.date() and 
                self.start_time <= now.time() <= self.end_time)
    
    def get_duration_hours(self):
        from datetime import datetime, timedelta
        start = datetime.combine(datetime.today(), self.start_time)
        end = datetime.combine(datetime.today(), self.end_time)
        duration = end - start
        return duration.total_seconds() / 3600


class PatientLog(models.Model):
    """Log of patients seen by doctors"""
    patient_its_id = models.CharField(
        max_length=8,
        validators=[RegexValidator(
            regex=r'^\d{8}$',
            message='Patient ITS ID must be exactly 8 digits'
        )]
    )
    patient_name = models.CharField(max_length=100, blank=True, null=True)
    ailment = models.TextField()
    seen_by = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='patient_logs')
    moze = models.ForeignKey(Moze, on_delete=models.CASCADE, related_name='patient_logs')
    schedule = models.ForeignKey(
        DoctorSchedule, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='patient_logs'
    )
    
    # Medical details
    symptoms = models.TextField(blank=True, null=True)
    diagnosis = models.TextField(blank=True, null=True)
    prescription = models.TextField(blank=True, null=True)
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(blank=True, null=True)
    
    # Visit details
    visit_type = models.CharField(
        max_length=20,
        choices=[
            ('consultation', 'Consultation'),
            ('follow_up', 'Follow-up'),
            ('emergency', 'Emergency'),
            ('screening', 'Screening')
        ],
        default='consultation'
    )
    
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Patient Log'
        verbose_name_plural = 'Patient Logs'
    
    def __str__(self):
        return f"Patient {self.patient_its_id} - {self.seen_by.name} ({self.timestamp.date()})"


class DoctorAvailability(models.Model):
    """Doctor's general availability schedule"""
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='availability')
    day_of_week = models.PositiveIntegerField(
        choices=[
            (0, 'Monday'),
            (1, 'Tuesday'),
            (2, 'Wednesday'),
            (3, 'Thursday'),
            (4, 'Friday'),
            (5, 'Saturday'),
            (6, 'Sunday'),
        ]
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['doctor', 'day_of_week', 'start_time']
        ordering = ['day_of_week', 'start_time']
        verbose_name = 'Doctor Availability'
        verbose_name_plural = 'Doctor Availabilities'
    
    def __str__(self):
        return f"{self.doctor.name} - {self.get_day_of_week_display()} ({self.start_time}-{self.end_time})"
