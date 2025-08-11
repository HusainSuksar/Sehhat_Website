from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.utils import timezone
from datetime import time
from decimal import Decimal

User = get_user_model()


class Doctor(models.Model):
    """Doctor model for the doctor directory"""
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='doctor_profile'
    )
    license_number = models.CharField(
        max_length=50,
        unique=True,
        help_text='Medical license number'
    )
    specialty = models.CharField(max_length=100, blank=True, null=True)
    qualification = models.TextField(blank=True, null=True)
    experience_years = models.PositiveIntegerField(default=0)
    consultation_fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00')
    )
    bio = models.TextField(blank=True, null=True)
    profile_photo = models.ImageField(
        upload_to='doctors/photos/', 
        blank=True, 
        null=True
    )
    
    # Contact Information
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message='Phone number must be entered in the format: "+999999999". Up to 15 digits allowed.'
        )],
        blank=True,
        null=True
    )
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    # Professional Information
    hospital_affiliation = models.CharField(max_length=200, blank=True, null=True)
    consultation_hours = models.TextField(
        blank=True, 
        null=True,
        help_text='General consultation hours description'
    )
    
    # System fields
    is_active = models.BooleanField(default=True)
    is_accepting_patients = models.BooleanField(default=True)
    assigned_moze = models.ForeignKey(
        'moze.Moze',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_doctors'
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
            models.Index(fields=['is_active', 'is_accepting_patients']),
            models.Index(fields=['specialty']),
            models.Index(fields=['assigned_moze']),
            models.Index(fields=['created_at']),
            models.Index(fields=['user', 'is_active']),
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
        """Get total number of patients treated"""
        return self.appointments.values('patient').distinct().count()


class Patient(models.Model):
    """Patient model"""
    
    user_account = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='patient_profile',
        null=True,
        blank=True
    )
    
    # Personal Information
    full_name = models.CharField(max_length=200)
    date_of_birth = models.DateField()
    gender = models.CharField(
        max_length=10,
        choices=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other')
        ]
    )
    
    # Contact Information
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message='Phone number must be entered in the format: "+999999999". Up to 15 digits allowed.'
        )]
    )
    email = models.EmailField(blank=True, null=True)
    address = models.TextField()
    
    # Medical Information
    blood_group = models.CharField(
        max_length=5,
        choices=[
            ('A+', 'A+'), ('A-', 'A-'),
            ('B+', 'B+'), ('B-', 'B-'),
            ('AB+', 'AB+'), ('AB-', 'AB-'),
            ('O+', 'O+'), ('O-', 'O-'),
        ],
        blank=True,
        null=True
    )
    allergies = models.TextField(blank=True, null=True)
    medical_history = models.TextField(blank=True, null=True)
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=200)
    emergency_contact_phone = models.CharField(
        max_length=15,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message='Phone number must be entered in the format: "+999999999". Up to 15 digits allowed.'
        )]
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['full_name']
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'
        # Add database indexes for performance
        indexes = [
            models.Index(fields=['full_name']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['user_account']),
            models.Index(fields=['created_at']),
            models.Index(fields=['date_of_birth']),
        ]
    
    def __str__(self):
        return self.full_name
    
    @property
    def age(self):
        """Calculate age from date of birth"""
        today = timezone.now().date()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )


class Appointment(models.Model):
    """Appointment model"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Appointment details
    reason = models.TextField(
        help_text='Reason for the appointment'
    )
    notes = models.TextField(blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_appointments'
    )
    
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
        return f"{self.patient.full_name} - {self.doctor.get_full_name()} on {self.appointment_date}"


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
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Medical Service'
        verbose_name_plural = 'Medical Services'
        # Add database indexes for performance
        indexes = [
            models.Index(fields=['doctor', 'is_active']),
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.doctor.get_full_name()}"
