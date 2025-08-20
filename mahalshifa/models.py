from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from moze.models import Moze


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
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE, related_name='appointments')
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
        related_name='mahalshifa_booked_appointments'
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
        return f"{self.patient.get_full_name()} with Dr. {self.doctor.user.get_full_name()} on {self.appointment_date} at {self.appointment_time}"
    
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
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE, related_name='medical_records')
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
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE, related_name='prescriptions')
    
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
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE, related_name='ordered_lab_tests')
    
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


# Additional models that views expect
class Hospital(models.Model):
    """Hospital/Medical facility model"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    
    # Hospital details
    hospital_type = models.CharField(
        max_length=20,
        choices=[
            ('general', 'General Hospital'),
            ('specialty', 'Specialty Hospital'),
            ('clinic', 'Clinic'),
            ('emergency', 'Emergency Center'),
            ('rehabilitation', 'Rehabilitation Center'),
        ],
        default='general'
    )
    
    # Capacity and facilities
    total_beds = models.PositiveIntegerField(default=0)
    available_beds = models.PositiveIntegerField(default=0)
    emergency_beds = models.PositiveIntegerField(default=0)
    icu_beds = models.PositiveIntegerField(default=0)
    
    # Operational details
    is_active = models.BooleanField(default=True)
    is_emergency_capable = models.BooleanField(default=False)
    has_pharmacy = models.BooleanField(default=False)
    has_laboratory = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class Department(models.Model):
    """Hospital departments"""
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='departments')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Department head
    head = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_departments'
    )
    
    # Department details
    floor_number = models.CharField(max_length=10, blank=True)
    phone_extension = models.CharField(max_length=10, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['hospital', 'name']
    
    def __str__(self):
        return f"{self.hospital.name} - {self.name}"


class Doctor(models.Model):
    """Doctor model"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mahalshifa_doctor_profile'
    )
    
    # Professional details
    license_number = models.CharField(max_length=50, unique=True)
    specialization = models.CharField(max_length=100)
    qualification = models.CharField(max_length=200)
    experience_years = models.PositiveIntegerField(default=0)
    
    # Hospital affiliation
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='doctors')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='doctors')
    
    # Professional status
    is_available = models.BooleanField(default=True)
    is_emergency_doctor = models.BooleanField(default=False)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Dr. {self.user.get_full_name()} - {self.specialization}"


class HospitalStaff(models.Model):
    """Hospital staff model"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='hospital_staff'
    )
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='staff')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='staff')
    
    # Staff details
    staff_type = models.CharField(
        max_length=20,
        choices=[
            ('nurse', 'Nurse'),
            ('technician', 'Technician'),
            ('pharmacist', 'Pharmacist'),
            ('administrator', 'Administrator'),
            ('receptionist', 'Receptionist'),
            ('security', 'Security'),
            ('maintenance', 'Maintenance'),
            ('other', 'Other'),
        ]
    )
    
    employee_id = models.CharField(max_length=20, unique=True)
    shift = models.CharField(
        max_length=10,
        choices=[
            ('morning', 'Morning'),
            ('evening', 'Evening'),
            ('night', 'Night'),
            ('rotating', 'Rotating'),
        ],
        default='morning'
    )
    
    is_active = models.BooleanField(default=True)
    hire_date = models.DateField()
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_staff_type_display()}"


class Room(models.Model):
    """Hospital rooms"""
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='rooms')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='rooms')
    
    # Room details
    room_number = models.CharField(max_length=20)
    room_type = models.CharField(
        max_length=20,
        choices=[
            ('general', 'General Ward'),
            ('private', 'Private Room'),
            ('icu', 'ICU'),
            ('emergency', 'Emergency Room'),
            ('operation', 'Operation Theater'),
            ('consultation', 'Consultation Room'),
            ('laboratory', 'Laboratory'),
            ('pharmacy', 'Pharmacy'),
        ]
    )
    
    capacity = models.PositiveIntegerField(default=1)
    floor_number = models.CharField(max_length=10)
    
    # Status
    is_available = models.BooleanField(default=True)
    is_operational = models.BooleanField(default=True)
    
    # Amenities
    has_ac = models.BooleanField(default=False)
    has_wifi = models.BooleanField(default=False)
    has_tv = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['hospital', 'room_number']
        ordering = ['hospital', 'floor_number', 'room_number']
    
    def __str__(self):
        return f"{self.hospital.name} - Room {self.room_number}"


class Medication(models.Model):
    """Medication/Drug model"""
    name = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=200, blank=True)
    brand_name = models.CharField(max_length=200, blank=True)
    
    # Medication details
    medication_type = models.CharField(
        max_length=20,
        choices=[
            ('tablet', 'Tablet'),
            ('capsule', 'Capsule'),
            ('syrup', 'Syrup'),
            ('injection', 'Injection'),
            ('cream', 'Cream/Ointment'),
            ('drops', 'Drops'),
            ('inhaler', 'Inhaler'),
            ('other', 'Other'),
        ]
    )
    
    strength = models.CharField(max_length=50, help_text='e.g., 500mg, 10ml')
    manufacturer = models.CharField(max_length=200, blank=True)
    
    # Usage information
    side_effects = models.TextField(blank=True)
    contraindications = models.TextField(blank=True)
    storage_conditions = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)
    requires_prescription = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.strength})"


class LabResult(models.Model):
    """Laboratory test results"""
    lab_test = models.OneToOneField(LabTest, on_delete=models.CASCADE, related_name='result')
    
    # Result details
    result_data = models.JSONField(default=dict, help_text='Test results in JSON format')
    result_summary = models.TextField()
    normal_ranges = models.JSONField(default=dict, help_text='Normal value ranges')
    
    # Result interpretation
    is_normal = models.BooleanField(default=True)
    critical_values = models.TextField(blank=True)
    interpretation = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    
    # Technical details
    test_method = models.CharField(max_length=100, blank=True)
    equipment_used = models.CharField(max_length=100, blank=True)
    technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='performed_tests'
    )
    
    # Quality control
    quality_control_passed = models.BooleanField(default=True)
    qc_notes = models.TextField(blank=True)
    
    # Results timing
    completed_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reported_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-completed_at']
    
    def __str__(self):
        return f"Result for {self.lab_test.test_name} - {self.lab_test.patient.get_full_name()}"


class Admission(models.Model):
    """Patient hospital admissions"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='admissions')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='admissions')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='admissions')
    admitting_doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE, related_name='admitted_patients')
    
    # Admission details
    admission_type = models.CharField(
        max_length=20,
        choices=[
            ('emergency', 'Emergency'),
            ('elective', 'Elective'),
            ('urgent', 'Urgent'),
            ('observation', 'Observation'),
        ]
    )
    
    # Dates and times
    admission_date = models.DateTimeField()
    expected_discharge_date = models.DateField(null=True, blank=True)
    
    # Medical details
    chief_complaint = models.TextField()
    diagnosis = models.TextField()
    treatment_plan = models.TextField()
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('admitted', 'Admitted'),
            ('transferred', 'Transferred'),
            ('discharged', 'Discharged'),
            ('deceased', 'Deceased'),
        ],
        default='admitted'
    )
    
    # Administrative
    bed_number = models.CharField(max_length=10, blank=True)
    admission_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-admission_date']
    
    def __str__(self):
        return f"{self.patient.get_full_name()} admitted on {self.admission_date.date()}"


class Discharge(models.Model):
    """Patient discharge records"""
    admission = models.OneToOneField(Admission, on_delete=models.CASCADE, related_name='discharge')
    discharging_doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE, related_name='discharged_patients')
    
    # Discharge details
    discharge_date = models.DateTimeField()
    discharge_type = models.CharField(
        max_length=20,
        choices=[
            ('normal', 'Normal Discharge'),
            ('ama', 'Against Medical Advice'),
            ('transfer', 'Transfer to Another Facility'),
            ('deceased', 'Deceased'),
            ('absconded', 'Absconded'),
        ],
        default='normal'
    )
    
    # Medical information
    final_diagnosis = models.TextField()
    treatment_summary = models.TextField()
    discharge_medications = models.TextField(blank=True)
    follow_up_instructions = models.TextField()
    next_appointment = models.DateTimeField(null=True, blank=True)
    
    # Condition at discharge
    condition_at_discharge = models.CharField(
        max_length=20,
        choices=[
            ('excellent', 'Excellent'),
            ('good', 'Good'),
            ('fair', 'Fair'),
            ('poor', 'Poor'),
            ('critical', 'Critical'),
        ]
    )
    
    # Administrative
    discharge_summary = models.TextField()
    discharge_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Discharge of {self.admission.patient.get_full_name()} on {self.discharge_date.date()}"


class TreatmentPlan(models.Model):
    """Patient treatment plans"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='treatment_plans')
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE, related_name='treatment_plans')
    medical_record = models.ForeignKey(
        MedicalRecord,
        on_delete=models.CASCADE,
        related_name='treatment_plans'
    )
    
    # Plan details
    plan_name = models.CharField(max_length=200)
    description = models.TextField()
    objectives = models.TextField()
    
    # Timeline
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    duration_weeks = models.PositiveIntegerField(null=True, blank=True)
    
    # Plan components
    medications = models.ManyToManyField(Medication, through='TreatmentMedication', blank=True)
    therapies = models.TextField(blank=True)
    lifestyle_changes = models.TextField(blank=True)
    dietary_restrictions = models.TextField(blank=True)
    
    # Monitoring
    monitoring_schedule = models.TextField(blank=True)
    success_criteria = models.TextField(blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('completed', 'Completed'),
            ('modified', 'Modified'),
            ('discontinued', 'Discontinued'),
        ],
        default='active'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Treatment Plan: {self.plan_name} for {self.patient.get_full_name()}"


class TreatmentMedication(models.Model):
    """Through model for TreatmentPlan and Medication"""
    treatment_plan = models.ForeignKey(TreatmentPlan, on_delete=models.CASCADE)
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    instructions = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.medication.name} - {self.dosage}"


class Inventory(models.Model):
    """Hospital inventory management"""
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='inventories')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Inventory type
    inventory_type = models.CharField(
        max_length=20,
        choices=[
            ('medication', 'Medications'),
            ('equipment', 'Medical Equipment'),
            ('supplies', 'Medical Supplies'),
            ('consumables', 'Consumables'),
            ('furniture', 'Furniture'),
            ('other', 'Other'),
        ]
    )
    
    # Location
    storage_location = models.CharField(max_length=200)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='inventories')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.hospital.name} - {self.name}"


class InventoryItem(models.Model):
    """Individual inventory items"""
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='items')
    
    # Item details
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    item_code = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=100)
    
    # Quantity management
    current_stock = models.PositiveIntegerField(default=0)
    minimum_stock = models.PositiveIntegerField(default=0)
    maximum_stock = models.PositiveIntegerField(default=0)
    unit = models.CharField(max_length=20, default='units')
    
    # Pricing
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    supplier = models.CharField(max_length=200, blank=True)
    
    # Dates
    expiry_date = models.DateField(null=True, blank=True)
    last_restocked = models.DateField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    requires_prescription = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.current_stock} {self.unit})"
    
    def is_low_stock(self):
        return self.current_stock <= self.minimum_stock
    
    def is_expired(self):
        if self.expiry_date:
            from django.utils import timezone
            return self.expiry_date < timezone.now().date()
        return False


class EmergencyContact(models.Model):
    """Emergency contacts for patients"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='emergency_contacts')
    
    # Contact details
    name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=50)
    phone_primary = models.CharField(max_length=20)
    phone_secondary = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    
    # Priority
    is_primary = models.BooleanField(default=False)
    priority_order = models.PositiveIntegerField(default=1)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['patient', 'priority_order']
    
    def __str__(self):
        return f"{self.name} - {self.relationship} of {self.patient.get_full_name()}"


class Insurance(models.Model):
    """Patient insurance information"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='insurance_policies')
    
    # Insurance details
    insurance_company = models.CharField(max_length=200)
    policy_number = models.CharField(max_length=100)
    group_number = models.CharField(max_length=100, blank=True)
    
    # Coverage details
    coverage_type = models.CharField(
        max_length=20,
        choices=[
            ('basic', 'Basic Coverage'),
            ('standard', 'Standard Coverage'),
            ('premium', 'Premium Coverage'),
            ('comprehensive', 'Comprehensive'),
        ]
    )
    
    coverage_amount = models.DecimalField(max_digits=12, decimal_places=2)
    deductible = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    co_pay_percentage = models.FloatField(default=0)
    
    # Validity
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    
    # Additional information
    pre_authorization_required = models.BooleanField(default=False)
    network_hospitals = models.TextField(blank=True)
    exclusions = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.insurance_company} - {self.policy_number}"
    
    def is_valid(self):
        from django.utils import timezone
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date and self.is_active
