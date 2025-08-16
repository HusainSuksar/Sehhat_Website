from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.utils import timezone
from datetime import time
from decimal import Decimal

User = get_user_model()


class Doctor(models.Model):
    """Doctor model for the doctor directory - Updated to match database schema"""
    
    # Basic Information
    name = models.CharField(max_length=100)
    its_id = models.CharField(max_length=8, blank=True, null=True)
    specialty = models.CharField(max_length=100, blank=True, null=True)
    qualification = models.TextField(blank=True, null=True)
    experience_years = models.PositiveIntegerField(default=0)
    verified_certificate = models.CharField(max_length=100, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    
    # Professional Information
    license_number = models.CharField(max_length=50, blank=True, null=True)
    consultation_fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00')
    )
    
    # Contact Information
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    languages_spoken = models.CharField(max_length=200, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    
    # Relationships
    assigned_moze = models.ForeignKey(
        'moze.Moze',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_doctors'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='doctor_profile',
        null=True,
        blank=True
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['user__first_name', 'user__last_name']
        verbose_name = 'Doctor'
        verbose_name_plural = 'Doctors'
        # Add database indexes for performance
        indexes = [
            models.Index(fields=['is_verified', 'is_available']),
            models.Index(fields=['specialty']),
            models.Index(fields=['assigned_moze']),
            models.Index(fields=['created_at']),
            models.Index(fields=['user', 'is_verified']),
        ]
    
    def __str__(self):
        return f"Dr. {self.user.get_full_name()}"
    
    def get_full_name(self):
        return f"Dr. {self.user.get_full_name()}"
    
    @property
    def rating(self):
        """Calculate average rating (placeholder for future implementation)"""
        return 4.5  # Placeholder
    
    @property
    def total_patients(self):
        """Get total number of patients for this doctor"""
        return 0  # Placeholder - patients relationship not yet implemented
    
    @property
    def total_appointments(self):
        """Get total number of appointments for this doctor"""
        return self.appointments.count()


class Patient(models.Model):
    """Patient model for the doctor directory - Updated to match database schema"""
    
    # Basic Information
    date_of_birth = models.DateField()
    gender = models.CharField(
        max_length=10,
        choices=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other')
        ]
    )
    
    # Medical Information
    blood_group = models.CharField(
        max_length=5,
        choices=[
            ('A+', 'A+'), ('A-', 'A-'),
            ('B+', 'B+'), ('B-', 'B-'),
            ('AB+', 'AB+'), ('AB-', 'AB-'),
            ('O+', 'O+'), ('O-', 'O-')
        ],
        blank=True,
        null=True
    )
    emergency_contact = models.CharField(max_length=15, blank=True, null=True)
    medical_history = models.TextField(blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    current_medications = models.TextField(blank=True, null=True)
    
    # Relationships
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='patient_profile',
        null=True,
        blank=True
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['user__first_name', 'user__last_name']
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'
        # Add database indexes for performance
        indexes = [
            models.Index(fields=['date_of_birth']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.user.get_full_name() if self.user else 'Unknown Patient'
    
    @property
    def age(self):
        """Calculate patient age"""
        today = timezone.now().date()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    @property
    def total_appointments(self):
        """Get total number of appointments for this patient"""
        return self.appointments.count()


class Appointment(models.Model):
    """Appointment model for scheduling doctor visits - Updated to match database schema"""
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show')
    ]
    
    # Appointment Details
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled'
    )
    reason_for_visit = models.CharField(max_length=200, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    # Relationships
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    service = models.ForeignKey(
        'MedicalService',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='appointments'
    )
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-appointment_date', '-appointment_time']
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'
        # Add database indexes for performance
        indexes = [
            models.Index(fields=['doctor', 'appointment_date']),
            models.Index(fields=['patient', 'appointment_date']),
            models.Index(fields=['appointment_date', 'appointment_time']),
            models.Index(fields=['status']),
            models.Index(fields=['doctor', 'status']),
            models.Index(fields=['created_at']),
        ]
        
        # Prevent double booking
        unique_together = [
            ['doctor', 'appointment_date', 'appointment_time']
        ]
    
    def __str__(self):
        patient_name = self.patient.user.get_full_name() if self.patient.user else 'Unknown Patient'
        return f"{patient_name} - {self.doctor.get_full_name()} on {self.appointment_date}"


class PatientLog(models.Model):
    """Patient visit log for tracking consultations"""
    
    VISIT_TYPE_CHOICES = [
        ('consultation', 'Consultation'),
        ('follow_up', 'Follow-up'),
        ('emergency', 'Emergency'),
        ('screening', 'Screening')
    ]
    
    patient_its_id = models.CharField(
        max_length=8,
        validators=[RegexValidator(
            regex=r'^\d{8}$',
            message='Patient ITS ID must be exactly 8 digits'
        )]
    )
    patient_name = models.CharField(max_length=100, blank=True, null=True)
    ailment = models.TextField()
    symptoms = models.TextField(blank=True, null=True)
    diagnosis = models.TextField(blank=True, null=True)
    prescription = models.TextField(blank=True, null=True)
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(blank=True, null=True)
    visit_type = models.CharField(
        max_length=20,
        choices=VISIT_TYPE_CHOICES,
        default='consultation'
    )
    
    # Relationships
    moze = models.ForeignKey(
        'moze.Moze',
        on_delete=models.CASCADE,
        related_name='patient_logs'
    )
    schedule = models.ForeignKey(
        'DoctorSchedule',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='patient_logs'
    )
    seen_by = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='patient_logs'
    )
    
    # Metadata
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Patient Log'
        verbose_name_plural = 'Patient Logs'
        # Add database indexes for performance
        indexes = [
            models.Index(fields=['patient_its_id']),
            models.Index(fields=['seen_by', 'timestamp']),
            models.Index(fields=['moze', 'timestamp']),
            models.Index(fields=['visit_type']),
            models.Index(fields=['follow_up_required']),
        ]
    
    def __str__(self):
        return f"{self.patient_name} - {self.ailment} ({self.timestamp.strftime('%Y-%m-%d %H:%M')})"


class DoctorSchedule(models.Model):
    """Doctor's daily schedule"""
    
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='schedules'
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    max_patients = models.PositiveIntegerField(default=10)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['date', 'start_time']
        verbose_name = 'Doctor Schedule'
        verbose_name_plural = 'Doctor Schedules'
        # Add database indexes for performance
        indexes = [
            models.Index(fields=['doctor', 'date']),
            models.Index(fields=['date', 'is_available']),
            models.Index(fields=['doctor', 'is_available']),
        ]
        
        # Prevent overlapping schedules
        unique_together = [
            ['doctor', 'date', 'start_time']
        ]
    
    def __str__(self):
        return f"{self.doctor.get_full_name()} - {self.date} ({self.start_time}-{self.end_time})"


class MedicalService(models.Model):
    """Medical services offered by doctors"""
    
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='medical_services'
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    duration_minutes = models.PositiveIntegerField(default=30)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    is_available = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Medical Service'
        verbose_name_plural = 'Medical Services'
        # Add database indexes for performance
        indexes = [
            models.Index(fields=['doctor', 'is_available']),
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.doctor.get_full_name()}"
