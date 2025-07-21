from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from moze.models import Moze


class Doctor(models.Model):
    """Doctor profile linked to User model"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctordirectory_profile',
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


class MedicalService(models.Model):
    """Medical services offered by doctors"""
    SERVICE_TYPES = [
        ('consultation', 'General Consultation'),
        ('checkup', 'Health Checkup'),
        ('procedure', 'Medical Procedure'),
        ('therapy', 'Therapy Session'),
        ('emergency', 'Emergency Care'),
    ]
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=100)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES, default='consultation')
    description = models.TextField(blank=True, null=True)
    duration_minutes = models.PositiveIntegerField(default=30)
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Medical Service'
        verbose_name_plural = 'Medical Services'
    
    def __str__(self):
        return f"{self.name} - Dr. {self.doctor.name}"


class Patient(models.Model):
    """Patient profile linked to User model"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient_profile'
    )
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(
        max_length=10,
        choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')],
        blank=True,
        null=True
    )
    blood_group = models.CharField(
        max_length=5,
        choices=[
            ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
            ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')
        ],
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
        return f"{self.user.get_full_name()} - Patient"


class Appointment(models.Model):
    """Appointment booking system"""
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
    service = models.ForeignKey(MedicalService, on_delete=models.SET_NULL, null=True, blank=True)
    
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    reason_for_visit = models.CharField(max_length=200)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-appointment_date', '-appointment_time']
        unique_together = ['doctor', 'appointment_date', 'appointment_time']
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'
    
    def __str__(self):
        return f"{self.patient.user.get_full_name()} - Dr. {self.doctor.name} ({self.appointment_date})"


class MedicalRecord(models.Model):
    """Medical records for patient visits"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_records')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='directory_medical_records')
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True)
    
    visit_date = models.DateTimeField(auto_now_add=True)
    diagnosis = models.CharField(max_length=200)
    symptoms = models.TextField()
    treatment_plan = models.TextField()
    medications = models.TextField(blank=True, null=True)
    
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(blank=True, null=True)
    
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-visit_date']
        verbose_name = 'Medical Record'
        verbose_name_plural = 'Medical Records'
    
    def __str__(self):
        return f"{self.patient.user.get_full_name()} - {self.diagnosis} ({self.visit_date.date()})"


class Prescription(models.Model):
    """Prescription management"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='directory_prescriptions')
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='prescriptions')
    
    medication_name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=50)
    frequency = models.CharField(max_length=50)
    duration = models.CharField(max_length=50)
    instructions = models.TextField(blank=True, null=True)
    
    refills_allowed = models.PositiveIntegerField(default=0)
    refills_used = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Prescription'
        verbose_name_plural = 'Prescriptions'
    
    def __str__(self):
        return f"{self.medication_name} for {self.patient.user.get_full_name()}"


class LabTest(models.Model):
    """Lab test orders and results"""
    TEST_TYPES = [
        ('blood', 'Blood Test'),
        ('urine', 'Urine Test'),
        ('xray', 'X-Ray'),
        ('mri', 'MRI'),
        ('ct', 'CT Scan'),
        ('ultrasound', 'Ultrasound'),
        ('ecg', 'ECG'),
        ('other', 'Other'),
    ]
    
    URGENCY_CHOICES = [
        ('routine', 'Routine'),
        ('urgent', 'Urgent'),
        ('stat', 'STAT'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='lab_tests')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='lab_tests')
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='lab_tests', null=True, blank=True)
    
    test_name = models.CharField(max_length=100)
    test_type = models.CharField(max_length=20, choices=TEST_TYPES, default='blood')
    urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='routine')
    
    test_date = models.DateField()
    instructions = models.TextField(blank=True, null=True)
    
    results = models.TextField(blank=True, null=True)
    results_file = models.FileField(upload_to='lab_results/', blank=True, null=True)
    
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-test_date']
        verbose_name = 'Lab Test'
        verbose_name_plural = 'Lab Tests'
    
    def __str__(self):
        return f"{self.test_name} - {self.patient.user.get_full_name()}"


class VitalSigns(models.Model):
    """Patient vital signs recording"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='vital_signs')
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='vital_signs', null=True, blank=True)
    
    # Vital signs
    blood_pressure_systolic = models.PositiveIntegerField(null=True, blank=True)
    blood_pressure_diastolic = models.PositiveIntegerField(null=True, blank=True)
    heart_rate = models.PositiveIntegerField(null=True, blank=True)  # beats per minute
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)  # celsius
    respiratory_rate = models.PositiveIntegerField(null=True, blank=True)  # breaths per minute
    oxygen_saturation = models.PositiveIntegerField(null=True, blank=True)  # percentage
    
    # Physical measurements
    weight = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)  # kg
    height = models.PositiveIntegerField(null=True, blank=True)  # cm
    
    notes = models.TextField(blank=True, null=True)
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-recorded_at']
        verbose_name = 'Vital Signs'
        verbose_name_plural = 'Vital Signs'
    
    def __str__(self):
        return f"Vitals for {self.patient.user.get_full_name()} - {self.recorded_at.date()}"
