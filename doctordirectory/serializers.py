"""
Serializers for the DoctorDirectory app
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import (
    Doctor, DoctorSchedule, PatientLog, DoctorAvailability,
    MedicalService, Patient, Appointment, MedicalRecord,
    Prescription, LabTest, VitalSigns
)
from moze.models import Moze

User = get_user_model()


# Basic User serializer for nested relationships
class UserBasicSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'full_name']
        read_only_fields = fields
    
    def get_full_name(self, obj):
        return obj.get_full_name()


# Basic Moze serializer for nested relationships
class MozeBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Moze
        fields = ['id', 'name', 'location']
        read_only_fields = fields


# Doctor related serializers
class DoctorAvailabilitySerializer(serializers.ModelSerializer):
    day_of_week_display = serializers.SerializerMethodField()
    
    class Meta:
        model = DoctorAvailability
        fields = [
            'id', 'day_of_week', 'day_of_week_display', 'start_time', 
            'end_time', 'is_active'
        ]
    
    def get_day_of_week_display(self, obj):
        return obj.get_day_of_week_display()


class MedicalServiceSerializer(serializers.ModelSerializer):
    service_type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = MedicalService
        fields = [
            'id', 'name', 'service_type', 'service_type_display', 'description',
            'duration_minutes', 'fee', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_service_type_display(self, obj):
        return obj.get_service_type_display()


class DoctorScheduleSerializer(serializers.ModelSerializer):
    moze = MozeBasicSerializer(read_only=True)
    moze_id = serializers.PrimaryKeyRelatedField(
        queryset=Moze.objects.all(), write_only=True, source='moze'
    )
    schedule_type_display = serializers.SerializerMethodField()
    is_current = serializers.SerializerMethodField()
    duration_hours = serializers.SerializerMethodField()
    
    class Meta:
        model = DoctorSchedule
        fields = [
            'id', 'date', 'start_time', 'end_time', 'moze', 'moze_id',
            'is_available', 'max_patients', 'notes', 'schedule_type',
            'schedule_type_display', 'is_current', 'duration_hours',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_schedule_type_display(self, obj):
        return obj.get_schedule_type_display()
    
    def get_is_current(self, obj):
        return obj.is_current()
    
    def get_duration_hours(self, obj):
        return obj.get_duration_hours()


class DoctorSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='doctor'), write_only=True, source='user'
    )
    assigned_moze = MozeBasicSerializer(read_only=True)
    assigned_moze_id = serializers.PrimaryKeyRelatedField(
        queryset=Moze.objects.all(), write_only=True, source='assigned_moze',
        required=False, allow_null=True
    )
    
    # Nested serializers
    availability = DoctorAvailabilitySerializer(many=True, read_only=True)
    services = MedicalServiceSerializer(many=True, read_only=True)
    
    # Computed fields
    full_name = serializers.SerializerMethodField()
    current_schedule = serializers.SerializerMethodField()
    total_patients_seen = serializers.SerializerMethodField()
    languages_list = serializers.SerializerMethodField()
    
    class Meta:
        model = Doctor
        fields = [
            'id', 'user', 'user_id', 'name', 'its_id', 'specialty', 
            'qualification', 'experience_years', 'verified_certificate',
            'assigned_moze', 'assigned_moze_id', 'is_verified', 'is_available',
            'license_number', 'consultation_fee', 'phone', 'email', 'address',
            'languages_spoken', 'bio', 'created_at', 'updated_at',
            'full_name', 'current_schedule', 'total_patients_seen',
            'languages_list', 'availability', 'services'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_current_schedule(self, obj):
        schedule = obj.get_current_schedule()
        if schedule:
            return DoctorScheduleSerializer(schedule).data
        return None
    
    def get_total_patients_seen(self, obj):
        return obj.patient_logs.count()
    
    def get_languages_list(self, obj):
        if obj.languages_spoken:
            return [lang.strip() for lang in obj.languages_spoken.split(',')]
        return []


class DoctorCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='doctor'), source='user'
    )
    assigned_moze_id = serializers.PrimaryKeyRelatedField(
        queryset=Moze.objects.all(), source='assigned_moze',
        required=False, allow_null=True
    )
    
    class Meta:
        model = Doctor
        fields = [
            'user_id', 'name', 'its_id', 'specialty', 'qualification',
            'experience_years', 'verified_certificate', 'assigned_moze_id',
            'is_verified', 'is_available', 'license_number', 'consultation_fee',
            'phone', 'email', 'address', 'languages_spoken', 'bio'
        ]


# Patient related serializers
class PatientSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='user'
    )
    gender_display = serializers.SerializerMethodField()
    blood_group_display = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    
    class Meta:
        model = Patient
        fields = [
            'id', 'user', 'user_id', 'date_of_birth', 'gender', 'gender_display',
            'blood_group', 'blood_group_display', 'emergency_contact',
            'medical_history', 'allergies', 'current_medications', 'age',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_gender_display(self, obj):
        return obj.get_gender_display() if obj.gender else None
    
    def get_blood_group_display(self, obj):
        return obj.get_blood_group_display() if obj.blood_group else None
    
    def get_age(self, obj):
        if obj.date_of_birth:
            today = timezone.now().date()
            return today.year - obj.date_of_birth.year - (
                (today.month, today.day) < (obj.date_of_birth.month, obj.date_of_birth.day)
            )
        return None


class PatientCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user'
    )
    
    class Meta:
        model = Patient
        fields = [
            'user_id', 'date_of_birth', 'gender', 'blood_group',
            'emergency_contact', 'medical_history', 'allergies', 'current_medications'
        ]


# PatientLog serializer
class PatientLogSerializer(serializers.ModelSerializer):
    seen_by = serializers.StringRelatedField(read_only=True)
    seen_by_id = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all(), write_only=True, source='seen_by'
    )
    moze = MozeBasicSerializer(read_only=True)
    moze_id = serializers.PrimaryKeyRelatedField(
        queryset=Moze.objects.all(), write_only=True, source='moze'
    )
    schedule = DoctorScheduleSerializer(read_only=True)
    schedule_id = serializers.PrimaryKeyRelatedField(
        queryset=DoctorSchedule.objects.all(), write_only=True, source='schedule',
        required=False, allow_null=True
    )
    visit_type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = PatientLog
        fields = [
            'id', 'patient_its_id', 'patient_name', 'ailment', 'seen_by',
            'seen_by_id', 'moze', 'moze_id', 'schedule', 'schedule_id',
            'symptoms', 'diagnosis', 'prescription', 'follow_up_required',
            'follow_up_date', 'visit_type', 'visit_type_display',
            'timestamp', 'updated_at'
        ]
        read_only_fields = ['timestamp', 'updated_at']
    
    def get_visit_type_display(self, obj):
        return obj.get_visit_type_display()


# Appointment related serializers
class AppointmentSerializer(serializers.ModelSerializer):
    doctor = serializers.StringRelatedField(read_only=True)
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all(), write_only=True, source='doctor'
    )
    patient = PatientSerializer(read_only=True)
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(), write_only=True, source='patient'
    )
    service = MedicalServiceSerializer(read_only=True)
    service_id = serializers.PrimaryKeyRelatedField(
        queryset=MedicalService.objects.all(), write_only=True, source='service',
        required=False, allow_null=True
    )
    status_display = serializers.SerializerMethodField()
    is_upcoming = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'doctor', 'doctor_id', 'patient', 'patient_id', 'service',
            'service_id', 'appointment_date', 'appointment_time', 'status',
            'status_display', 'reason_for_visit', 'notes', 'is_upcoming',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_status_display(self, obj):
        return obj.get_status_display()
    
    def get_is_upcoming(self, obj):
        from datetime import datetime
        appointment_datetime = datetime.combine(obj.appointment_date, obj.appointment_time)
        # Make appointment_datetime timezone-aware
        appointment_datetime = timezone.make_aware(appointment_datetime) if timezone.is_naive(appointment_datetime) else appointment_datetime
        return appointment_datetime > timezone.now()


class AppointmentCreateSerializer(serializers.ModelSerializer):
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all(), source='doctor'
    )
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(), source='patient'
    )
    service_id = serializers.PrimaryKeyRelatedField(
        queryset=MedicalService.objects.all(), source='service',
        required=False, allow_null=True
    )
    
    class Meta:
        model = Appointment
        fields = [
            'doctor_id', 'patient_id', 'service_id', 'appointment_date',
            'appointment_time', 'reason_for_visit', 'notes'
        ]


# Medical records serializers
class VitalSignsSerializer(serializers.ModelSerializer):
    bmi = serializers.SerializerMethodField()
    
    class Meta:
        model = VitalSigns
        fields = [
            'id', 'blood_pressure_systolic', 'blood_pressure_diastolic',
            'heart_rate', 'temperature', 'respiratory_rate', 'oxygen_saturation',
            'weight', 'height', 'bmi', 'notes', 'recorded_at'
        ]
        read_only_fields = ['recorded_at']
    
    def get_bmi(self, obj):
        if obj.weight and obj.height:
            height_m = obj.height / 100  # Convert cm to meters
            return round(float(obj.weight) / (height_m * height_m), 2)
        return None


class PrescriptionSerializer(serializers.ModelSerializer):
    doctor = serializers.StringRelatedField(read_only=True)
    refills_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = Prescription
        fields = [
            'id', 'medication_name', 'dosage', 'frequency', 'duration',
            'instructions', 'refills_allowed', 'refills_used', 'refills_remaining',
            'doctor', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_refills_remaining(self, obj):
        return obj.refills_allowed - obj.refills_used


class LabTestSerializer(serializers.ModelSerializer):
    doctor = serializers.StringRelatedField(read_only=True)
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all(), write_only=True, source='doctor'
    )
    test_type_display = serializers.SerializerMethodField()
    urgency_display = serializers.SerializerMethodField()
    has_results = serializers.SerializerMethodField()
    
    class Meta:
        model = LabTest
        fields = [
            'id', 'test_name', 'test_type', 'test_type_display', 'urgency',
            'urgency_display', 'test_date', 'instructions', 'results',
            'results_file', 'notes', 'has_results', 'doctor', 'doctor_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_test_type_display(self, obj):
        return obj.get_test_type_display()
    
    def get_urgency_display(self, obj):
        return obj.get_urgency_display()
    
    def get_has_results(self, obj):
        return bool(obj.results or obj.results_file)


class MedicalRecordSerializer(serializers.ModelSerializer):
    doctor = serializers.StringRelatedField(read_only=True)
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all(), write_only=True, source='doctor'
    )
    patient = PatientSerializer(read_only=True)
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(), write_only=True, source='patient'
    )
    appointment = AppointmentSerializer(read_only=True)
    appointment_id = serializers.PrimaryKeyRelatedField(
        queryset=Appointment.objects.all(), write_only=True, source='appointment',
        required=False, allow_null=True
    )
    
    # Nested related objects
    prescriptions = PrescriptionSerializer(many=True, read_only=True)
    lab_tests = LabTestSerializer(many=True, read_only=True)
    vital_signs = VitalSignsSerializer(many=True, read_only=True)
    
    class Meta:
        model = MedicalRecord
        fields = [
            'id', 'patient', 'patient_id', 'doctor', 'doctor_id', 'appointment',
            'appointment_id', 'visit_date', 'diagnosis', 'symptoms', 'treatment_plan',
            'medications', 'follow_up_required', 'follow_up_date', 'notes',
            'prescriptions', 'lab_tests', 'vital_signs', 'created_at', 'updated_at'
        ]
        read_only_fields = ['visit_date', 'created_at', 'updated_at']


class MedicalRecordCreateSerializer(serializers.ModelSerializer):
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all(), source='doctor'
    )
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(), source='patient'
    )
    appointment_id = serializers.PrimaryKeyRelatedField(
        queryset=Appointment.objects.all(), source='appointment',
        required=False, allow_null=True
    )
    
    class Meta:
        model = MedicalRecord
        fields = [
            'patient_id', 'doctor_id', 'appointment_id', 'diagnosis', 'symptoms',
            'treatment_plan', 'medications', 'follow_up_required', 'follow_up_date', 'notes'
        ]


# Statistics serializers
class DoctorStatsSerializer(serializers.Serializer):
    total_doctors = serializers.IntegerField()
    verified_doctors = serializers.IntegerField()
    available_doctors = serializers.IntegerField()
    doctors_by_specialty = serializers.DictField()


class PatientStatsSerializer(serializers.Serializer):
    total_patients = serializers.IntegerField()
    new_patients_this_month = serializers.IntegerField()
    patients_by_blood_group = serializers.DictField()


class AppointmentStatsSerializer(serializers.Serializer):
    total_appointments = serializers.IntegerField()
    pending_appointments = serializers.IntegerField()
    confirmed_appointments = serializers.IntegerField()
    completed_appointments = serializers.IntegerField()
    cancelled_appointments = serializers.IntegerField()
    appointments_today = serializers.IntegerField()


# Search serializers
class DoctorSearchSerializer(serializers.Serializer):
    specialty = serializers.CharField(required=False)
    is_available = serializers.BooleanField(required=False)
    is_verified = serializers.BooleanField(required=False)
    moze_id = serializers.IntegerField(required=False)
    search = serializers.CharField(required=False)


class AppointmentSearchSerializer(serializers.Serializer):
    doctor_id = serializers.IntegerField(required=False)
    patient_id = serializers.IntegerField(required=False)
    status = serializers.CharField(required=False)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)