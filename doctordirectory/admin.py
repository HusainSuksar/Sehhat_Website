from django.contrib import admin
from .models import (
    Doctor, DoctorSchedule, PatientLog, DoctorAvailability,
    MedicalService, Patient, Appointment, MedicalRecord, 
    Prescription, LabTest, VitalSigns
)

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'specialty', 'is_verified', 'is_available', 'assigned_moze', 'created_at']
    list_filter = ['is_verified', 'is_available', 'specialty', 'assigned_moze', 'created_at']
    search_fields = ['name', 'user__first_name', 'user__last_name', 'specialty', 'its_id']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'its_id', 'specialty', 'qualification', 'experience_years')
        }),
        ('Verification & Status', {
            'fields': ('is_verified', 'is_available', 'verified_certificate', 'license_number')
        }),
        ('Assignment & Contact', {
            'fields': ('assigned_moze', 'consultation_fee', 'phone', 'email', 'address')
        }),
        ('Professional Details', {
            'fields': ('languages_spoken', 'bio')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(DoctorSchedule)
class DoctorScheduleAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'date', 'start_time', 'end_time', 'moze', 'is_available', 'schedule_type']
    list_filter = ['is_available', 'schedule_type', 'date', 'moze']
    search_fields = ['doctor__name', 'moze__name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-date', 'start_time']

@admin.register(PatientLog)
class PatientLogAdmin(admin.ModelAdmin):
    list_display = ['patient_name', 'seen_by', 'moze', 'visit_type', 'timestamp']
    list_filter = ['visit_type', 'follow_up_required', 'timestamp', 'moze']
    search_fields = ['patient_name', 'patient_its_id', 'seen_by__name']
    readonly_fields = ['timestamp', 'updated_at']
    ordering = ['-timestamp']

@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'day_of_week', 'start_time', 'end_time', 'is_active']
    list_filter = ['is_active', 'day_of_week']
    search_fields = ['doctor__name']
    ordering = ['doctor__name', 'day_of_week']

@admin.register(MedicalService)
class MedicalServiceAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'name', 'service_type', 'duration_minutes', 'fee', 'is_active']
    list_filter = ['service_type', 'is_active', 'doctor']
    search_fields = ['name', 'doctor__name']
    ordering = ['doctor__name', 'name']

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['user', 'date_of_birth', 'gender', 'blood_group', 'emergency_contact']
    list_filter = ['gender', 'blood_group', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'emergency_contact']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['user__first_name']

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'patient', 'appointment_date', 'appointment_time', 'status']
    list_filter = ['status', 'appointment_date', 'doctor']
    search_fields = ['doctor__name', 'patient__user__first_name', 'patient__user__last_name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-appointment_date', '-appointment_time']

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'visit_date', 'diagnosis']
    list_filter = ['visit_date', 'follow_up_required', 'doctor']
    search_fields = ['patient__user__first_name', 'patient__user__last_name', 'doctor__name']
    readonly_fields = ['visit_date', 'created_at', 'updated_at']
    ordering = ['-visit_date']

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'medication_name', 'dosage', 'created_at']
    list_filter = ['created_at', 'doctor']
    search_fields = ['medication_name', 'patient__user__first_name', 'doctor__name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

@admin.register(LabTest)
class LabTestAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'test_name', 'test_type', 'urgency', 'test_date']
    list_filter = ['test_type', 'urgency', 'test_date']
    search_fields = ['test_name', 'patient__user__first_name', 'doctor__name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-test_date']

@admin.register(VitalSigns)
class VitalSignsAdmin(admin.ModelAdmin):
    list_display = ['patient', 'recorded_at', 'blood_pressure_systolic', 'heart_rate', 'temperature']
    list_filter = ['recorded_at']
    search_fields = ['patient__user__first_name', 'patient__user__last_name']
    readonly_fields = ['recorded_at']
    ordering = ['-recorded_at']
