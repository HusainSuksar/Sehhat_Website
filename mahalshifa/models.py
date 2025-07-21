from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from moze.models import Moze
from doctordirectory.models import Doctor


class MedicalService(models.Model):
    """Available medical services"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(
        max_length=50,
        choices=[
            ('consultation', 'General Consultation'),
            ('specialist', 'Specialist Consultation'),
            ('diagnostic', 'Diagnostic Services'),
            ('treatment', 'Treatment'),
            ('preventive', 'Preventive Care'),
            ('emergency', 'Emergency Services'),
            ('rehabilitation', 'Rehabilitation'),
            ('mental_health', 'Mental Health'),
        ],
        default='consultation'
    )
    duration_minutes = models.PositiveIntegerField(default=30)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    requires_appointment = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'name']
        verbose_name = 'Medical Service'
        verbose_name_plural = 'Medical Services'
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class Patient(models.Model):
    """Patient records for Mahal Shifa"""
    its_id = models.CharField(
        max_length=8,
        unique=True,
        validators=[RegexValidator(
            regex=r'^\d{8}$',
            message='ITS ID must be exactly 8 digits'
        )]
    )
    
    # Personal information
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    arabic_name = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField()
    gender = models.CharField(
        max_length=10,
        choices=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other')
        ]
    )
    
    # Contact information
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField()
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=15)
    emergency_contact_relationship = models.CharField(max_length=50)
    
    # Medical information
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
    allergies = models.TextField(blank=True, null=True, help_text='Known allergies')
    chronic_conditions = models.TextField(blank=True, null=True, help_text='Chronic medical conditions')
    current_medications = models.TextField(blank=True, null=True, help_text='Current medications')
    
    # Registration details
    registered_moze = models.ForeignKey(
        Moze,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='registered_patients'
    )
    registration_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    # Linked user account (optional)
    user_account = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='patient_record'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.its_id})"
    
    def get_full_name(self):
        if self.arabic_name:
            return self.arabic_name
        return f"{self.first_name} {self.last_name}"
    
    def get_age(self):
        from django.utils import timezone
        today = timezone.now().date()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )


class Appointment(models.Model):
    """Medical appointments"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    moze = models.ForeignKey(Moze, on_delete=models.CASCADE, related_name='appointments')
    service = models.ForeignKey(MedicalService, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Appointment details
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField(default=30)
    
    # Appointment reason and notes
    reason = models.TextField(help_text='Reason for appointment')
    symptoms = models.TextField(blank=True, null=True, help_text='Patient symptoms')
    notes = models.TextField(blank=True, null=True, help_text='Additional notes')
    
    # Status tracking
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('checked_in', 'Checked In'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
        ('rescheduled', 'Rescheduled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # Appointment type
    APPOINTMENT_TYPES = [
        ('regular', 'Regular Appointment'),
        ('follow_up', 'Follow-up'),
        ('urgent', 'Urgent'),
        ('emergency', 'Emergency'),
        ('screening', 'Health Screening'),
        ('consultation', 'Consultation'),
    ]
    appointment_type = models.CharField(max_length=20, choices=APPOINTMENT_TYPES, default='regular')
    
    # Booking information
    booked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='booked_appointments'
    )
    booking_method = models.CharField(
        max_length=20,
        choices=[
            ('online', 'Online Booking'),
            ('phone', 'Phone Call'),
            ('walk_in', 'Walk-in'),
            ('staff', 'Booked by Staff'),
        ],
        default='online'
    )
    
    # Reminders and notifications
    reminder_sent = models.BooleanField(default=False)
    reminder_sent_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['appointment_date', 'appointment_time']
        unique_together = ['doctor', 'appointment_date', 'appointment_time']
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'
    
    def __str__(self):
        return f"{self.patient.get_full_name()} with Dr. {self.doctor.name} on {self.appointment_date} at {self.appointment_time}"
    
    def is_today(self):
        from django.utils import timezone
        return self.appointment_date == timezone.now().date()
    
    def is_overdue(self):
        from django.utils import timezone
        now = timezone.now()
        appointment_datetime = timezone.datetime.combine(self.appointment_date, self.appointment_time)
        appointment_datetime = timezone.make_aware(appointment_datetime)
        return now > appointment_datetime and self.status not in ['completed', 'cancelled', 'no_show']


class MedicalRecord(models.Model):
    """Medical consultation records"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_records')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='medical_records')
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='medical_record'
    )
    moze = models.ForeignKey(Moze, on_delete=models.CASCADE, related_name='medical_records')
    
    # Consultation details
    consultation_date = models.DateTimeField(auto_now_add=True)
    chief_complaint = models.TextField(help_text='Main complaint or reason for visit')
    history_of_present_illness = models.TextField(blank=True, null=True)
    past_medical_history = models.TextField(blank=True, null=True)
    family_history = models.TextField(blank=True, null=True)
    social_history = models.TextField(blank=True, null=True)
    
    # Physical examination
    vital_signs = models.JSONField(default=dict, help_text='Blood pressure, temperature, pulse, etc.')
    physical_examination = models.TextField(blank=True, null=True)
    
    # Assessment and plan
    diagnosis = models.TextField()
    differential_diagnosis = models.TextField(blank=True, null=True)
    treatment_plan = models.TextField()
    
    # Prescriptions and recommendations
    medications_prescribed = models.TextField(blank=True, null=True)
    lab_tests_ordered = models.TextField(blank=True, null=True)
    imaging_ordered = models.TextField(blank=True, null=True)
    referrals = models.TextField(blank=True, null=True)
    
    # Follow-up
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(blank=True, null=True)
    follow_up_instructions = models.TextField(blank=True, null=True)
    
    # Additional information
    patient_education = models.TextField(blank=True, null=True, help_text='Patient education provided')
    doctor_notes = models.TextField(blank=True, null=True, help_text='Private doctor notes')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-consultation_date']
        verbose_name = 'Medical Record'
        verbose_name_plural = 'Medical Records'
    
    def __str__(self):
        return f"Medical record for {self.patient.get_full_name()} - {self.consultation_date.date()}"


class Prescription(models.Model):
    """Prescription records"""
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='prescriptions')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='prescriptions')
    
    # Prescription details
    prescription_date = models.DateField(auto_now_add=True)
    medication_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100, help_text='How often to take the medication')
    duration = models.CharField(max_length=100, help_text='Duration of treatment')
    quantity = models.CharField(max_length=50, help_text='Quantity to dispense')
    
    # Instructions
    instructions = models.TextField(help_text='Special instructions for taking the medication')
    warnings = models.TextField(blank=True, null=True, help_text='Warnings and precautions')
    
    # Status
    is_active = models.BooleanField(default=True)
    is_dispensed = models.BooleanField(default=False)
    dispensed_date = models.DateField(blank=True, null=True)
    dispensed_by = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-prescription_date']
        verbose_name = 'Prescription'
        verbose_name_plural = 'Prescriptions'
    
    def __str__(self):
        return f"Prescription: {self.medication_name} for {self.patient.get_full_name()}"


class LabTest(models.Model):
    """Laboratory test orders and results"""
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='lab_tests')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='lab_tests')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='ordered_lab_tests')
    
    # Test details
    test_name = models.CharField(max_length=200)
    test_category = models.CharField(
        max_length=50,
        choices=[
            ('blood', 'Blood Test'),
            ('urine', 'Urine Test'),
            ('stool', 'Stool Test'),
            ('imaging', 'Imaging'),
            ('biopsy', 'Biopsy'),
            ('culture', 'Culture'),
            ('other', 'Other'),
        ],
        default='blood'
    )
    test_code = models.CharField(max_length=20, blank=True, null=True)
    
    # Status and dates
    ordered_date = models.DateField(auto_now_add=True)
    sample_collected_date = models.DateField(blank=True, null=True)
    result_date = models.DateField(blank=True, null=True)
    
    STATUS_CHOICES = [
        ('ordered', 'Ordered'),
        ('sample_collected', 'Sample Collected'),
        ('in_lab', 'In Laboratory'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ordered')
    
    # Results
    result_text = models.TextField(blank=True, null=True)
    result_file = models.FileField(upload_to='lab_results/', blank=True, null=True)
    normal_range = models.CharField(max_length=200, blank=True, null=True)
    is_abnormal = models.BooleanField(default=False)
    
    # Lab information
    lab_name = models.CharField(max_length=100, blank=True, null=True)
    lab_technician = models.CharField(max_length=100, blank=True, null=True)
    
    # Notes
    doctor_notes = models.TextField(blank=True, null=True)
    lab_notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-ordered_date']
        verbose_name = 'Lab Test'
        verbose_name_plural = 'Lab Tests'
    
    def __str__(self):
        return f"{self.test_name} for {self.patient.get_full_name()} - {self.get_status_display()}"


class VitalSigns(models.Model):
    """Patient vital signs records"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='vital_signs')
    medical_record = models.ForeignKey(
        MedicalRecord,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vital_signs_records'
    )
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Vital signs
    systolic_bp = models.PositiveIntegerField(blank=True, null=True, help_text='Systolic Blood Pressure (mmHg)')
    diastolic_bp = models.PositiveIntegerField(blank=True, null=True, help_text='Diastolic Blood Pressure (mmHg)')
    heart_rate = models.PositiveIntegerField(blank=True, null=True, help_text='Heart Rate (bpm)')
    respiratory_rate = models.PositiveIntegerField(blank=True, null=True, help_text='Respiratory Rate (breaths/min)')
    temperature = models.FloatField(blank=True, null=True, help_text='Temperature (°C)')
    oxygen_saturation = models.PositiveIntegerField(blank=True, null=True, help_text='Oxygen Saturation (%)')
    weight = models.FloatField(blank=True, null=True, help_text='Weight (kg)')
    height = models.FloatField(blank=True, null=True, help_text='Height (cm)')
    
    # Additional measurements
    bmi = models.FloatField(blank=True, null=True, help_text='Body Mass Index')
    pain_scale = models.PositiveIntegerField(
        blank=True,
        null=True,
        choices=[(i, str(i)) for i in range(11)],
        help_text='Pain scale 0-10'
    )
    
    # Notes
    notes = models.TextField(blank=True, null=True)
    
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-recorded_at']
        verbose_name = 'Vital Signs'
        verbose_name_plural = 'Vital Signs'
    
    def __str__(self):
        return f"Vital signs for {self.patient.get_full_name()} - {self.recorded_at.date()}"
    
    def calculate_bmi(self):
        """Calculate BMI if height and weight are available"""
        if self.height and self.weight and self.height > 0:
            height_m = self.height / 100  # Convert cm to meters
            self.bmi = round(self.weight / (height_m ** 2), 2)
            return self.bmi
        return None
    
    def save(self, *args, **kwargs):
        # Auto-calculate BMI
        self.calculate_bmi()
        super().save(*args, **kwargs)
