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
        related_name='doctordirectory_profile',
        limit_choices_to={'role': 'doctor'}
    )
    # Fields aligned to migration schema
    name = models.CharField(max_length=100)
    its_id = models.CharField(
        max_length=8,
        unique=True,
        validators=[RegexValidator(regex=r'^\d{8}$', message='ITS ID must be exactly 8 digits')]
    )
    specialty = models.CharField(max_length=100)
    qualification = models.CharField(max_length=200, blank=True, null=True)
    experience_years = models.PositiveIntegerField(default=0)
    verified_certificate = models.FileField(upload_to='doctor_certificates/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    license_number = models.CharField(max_length=50, blank=True, null=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    languages_spoken = models.CharField(max_length=200, blank=True, null=True, help_text='Comma-separated languages')
    bio = models.TextField(blank=True, null=True)
    assigned_moze = models.ForeignKey(
        'moze.Moze',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_doctors'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Doctor'
        verbose_name_plural = 'Doctors'
        indexes = [
            models.Index(fields=['is_verified', 'is_available']),
            models.Index(fields=['specialty']),
            models.Index(fields=['assigned_moze']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_full_name(self):
        return self.name


class Patient(models.Model):
    """Patient model"""
    # Minimal fields aligned with migration schema to avoid DB mismatches
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], blank=True, null=True)
    blood_group = models.CharField(
        max_length=5,
        choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')],
        blank=True,
        null=True
    )
    emergency_contact = models.CharField(max_length=15, blank=True, null=True)
    medical_history = models.TextField(blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    current_medications = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['user__first_name', 'user__last_name']
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Appointment(models.Model):
    """Appointment model"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='directory_appointments')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    # service field exists in DB; keep optional mapping minimal to avoid mismatches in unused code
    # service = models.ForeignKey('MedicalService', on_delete=models.SET_NULL, null=True, blank=True)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reason_for_visit = models.CharField(max_length=200)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-appointment_date', '-appointment_time']
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'

    def __str__(self):
        return f"{self.patient} - {self.doctor} on {self.appointment_date}"


class DoctorSchedule(models.Model):
    """Doctor's daily schedule"""
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='schedules')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    max_patients = models.PositiveIntegerField(default=20)
    notes = models.TextField(blank=True, null=True)
    # Fields present in migration
    schedule_type = models.CharField(
        max_length=20,
        choices=[('regular', 'Regular'), ('emergency', 'Emergency'), ('special', 'Special Clinic')],
        default='regular'
    )
    moze = models.ForeignKey('moze.Moze', on_delete=models.CASCADE, related_name='doctor_schedules')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['date', 'start_time']
        verbose_name = 'Doctor Schedule'
        verbose_name_plural = 'Doctor Schedules'
        unique_together = [['doctor', 'date', 'start_time']]

    def __str__(self):
        return f"{self.doctor} - {self.date} ({self.start_time}-{self.end_time})"


class MedicalService(models.Model):
    """Medical services offered by doctors"""
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=100)
    service_type = models.CharField(
        max_length=20,
        choices=[
            ('consultation', 'General Consultation'),
            ('checkup', 'Health Checkup'),
            ('procedure', 'Medical Procedure'),
            ('therapy', 'Therapy Session'),
            ('emergency', 'Emergency Care'),
        ],
        default='consultation'
    )
    description = models.TextField(blank=True, null=True)
    duration_minutes = models.PositiveIntegerField(default=30)
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Medical Service'
        verbose_name_plural = 'Medical Services'

    def __str__(self):
        return f"{self.name} - {self.doctor}"
