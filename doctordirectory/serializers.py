"""
Serializers for the DoctorDirectory app
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import (
    Doctor, DoctorSchedule, MedicalService, Patient, Appointment
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


class MedicalServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalService
        fields = [
            'id', 'name', 'description', 'duration_minutes', 'price', 
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class DoctorScheduleSerializer(serializers.ModelSerializer):
    doctor = serializers.StringRelatedField(read_only=True)
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all(), write_only=True, source='doctor'
    )
    
    class Meta:
        model = DoctorSchedule
        fields = [
            'id', 'doctor', 'doctor_id', 'date', 'start_time', 'end_time', 
            'is_available', 'max_patients', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate(self, data):
        if data.get('start_time') and data.get('end_time'):
            if data['start_time'] >= data['end_time']:
                raise serializers.ValidationError("End time must be after start time.")
        return data


class DoctorSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='doctor'), write_only=True, source='user'
    )
    assigned_moze = MozeBasicSerializer(read_only=True)
    assigned_moze_id = serializers.PrimaryKeyRelatedField(
        queryset=Moze.objects.all(), write_only=True, source='assigned_moze', required=False
    )
    medical_services = MedicalServiceSerializer(many=True, read_only=True)
    total_patients = serializers.ReadOnlyField()
    
    class Meta:
        model = Doctor
        fields = [
            'id', 'user', 'user_id', 'name', 'its_id', 'license_number', 'specialty', 'qualification',
            'experience_years', 'verified_certificate', 'is_verified', 'is_available', 'consultation_fee', 'bio',
            'phone', 'email', 'address', 'languages_spoken',
            'assigned_moze', 'assigned_moze_id', 'medical_services',
            'total_patients', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'total_patients']


class DoctorCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = [
            'name', 'its_id', 'license_number', 'specialty', 'qualification', 'experience_years',
            'verified_certificate', 'is_verified', 'is_available', 'consultation_fee', 'bio', 'phone', 'email', 'address',
            'languages_spoken', 'assigned_moze', 'user'
        ]


class PatientSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='user', required=False
    )
    age = serializers.ReadOnlyField()
    
    class Meta:
        model = Patient
        fields = [
            'id', 'user', 'date_of_birth', 'gender', 'blood_group',
            'emergency_contact', 'medical_history', 'allergies', 
            'current_medications', 'age', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'age']


class PatientCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            'date_of_birth', 'gender', 'blood_group', 'emergency_contact',
            'medical_history', 'allergies', 'current_medications', 'user'
        ]


class AppointmentSerializer(serializers.ModelSerializer):
    doctor = DoctorSerializer(read_only=True)
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.filter(is_verified=True), write_only=True, source='doctor'
    )
    patient = PatientSerializer(read_only=True)
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(), write_only=True, source='patient'
    )
    created_by = UserBasicSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'doctor', 'doctor_id', 'patient', 'patient_id', 'service',
            'appointment_date', 'appointment_time', 'status', 'status_display',
            'reason_for_visit', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_appointment_date(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError("Appointment date cannot be in the past.")
        return value


class AppointmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = [
            'doctor', 'patient', 'service', 'appointment_date', 'appointment_time',
            'reason_for_visit', 'notes'
        ]
    
    def validate_appointment_date(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError("Appointment date cannot be in the past.")
        return value


class AppointmentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['status', 'notes']


# Statistics Serializers
class DoctorStatsSerializer(serializers.Serializer):
    total_appointments = serializers.IntegerField()
    completed_appointments = serializers.IntegerField()
    pending_appointments = serializers.IntegerField()
    cancelled_appointments = serializers.IntegerField()
    completion_rate = serializers.FloatField()
    total_patients = serializers.IntegerField()


class AppointmentStatsSerializer(serializers.Serializer):
    total_appointments = serializers.IntegerField()
    appointments_today = serializers.IntegerField()
    appointments_this_week = serializers.IntegerField()
    appointments_this_month = serializers.IntegerField()
    by_status = serializers.DictField()
    by_doctor = serializers.ListField()


class SystemStatsSerializer(serializers.Serializer):
    total_doctors = serializers.IntegerField()
    active_doctors = serializers.IntegerField()
    total_patients = serializers.IntegerField()
    total_appointments = serializers.IntegerField()
    appointments_today = serializers.IntegerField()
    doctor_stats = DoctorStatsSerializer()
    appointment_stats = AppointmentStatsSerializer()