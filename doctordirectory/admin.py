from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import (
    Doctor, DoctorSchedule, PatientLog, DoctorAvailability,
    MedicalService, Patient, Appointment, MedicalRecord, 
    Prescription, LabTest, VitalSigns
)
# Import mahalshifa doctors for stats
from mahalshifa.models import Doctor as MahalShifaDoctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'specialty', 'is_verified', 'is_available', 'assigned_moze', 'get_patient_count', 'get_appointment_count', 'created_at']
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
    
    def get_queryset(self, request):
        """Annotate with patient and appointment counts"""
        return super().get_queryset(request).annotate(
            patient_count=Count('directory_appointments__patient', distinct=True),
            appointment_count=Count('directory_appointments')
        )
    
    def get_patient_count(self, obj):
        """Display patient count with color coding"""
        count = getattr(obj, 'patient_count', obj.directory_appointments.values('patient').distinct().count())
        if count > 0:
            return format_html('<span style="color: green;">{}</span>', count)
        return format_html('<span style="color: red;">{}</span>', count)
    get_patient_count.short_description = 'Patients'
    get_patient_count.admin_order_field = 'patient_count'
    
    def get_appointment_count(self, obj):
        """Display appointment count"""
        count = getattr(obj, 'appointment_count', obj.directory_appointments.count())
        return count
    get_appointment_count.short_description = 'Appointments'
    get_appointment_count.admin_order_field = 'appointment_count'


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
    list_display = ['user', 'date_of_birth', 'gender', 'blood_group', 'emergency_contact', 'get_appointment_count']
    list_filter = ['gender', 'blood_group', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'emergency_contact']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['user__first_name']
    
    def get_queryset(self, request):
        """Annotate with appointment count"""
        return super().get_queryset(request).annotate(
            appointment_count=Count('appointments')
        )
    
    def get_appointment_count(self, obj):
        """Display appointment count"""
        count = getattr(obj, 'appointment_count', obj.appointments.count())
        return count
    get_appointment_count.short_description = 'Appointments'
    get_appointment_count.admin_order_field = 'appointment_count'


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


# Add a custom admin view for doctor statistics
class DoctorStatsAdmin(admin.ModelAdmin):
    """Custom admin view for doctor statistics"""
    
    def changelist_view(self, request, extra_context=None):
        """Override to show doctor statistics"""
        extra_context = extra_context or {}
        
        # Get statistics from mahalshifa doctors
        total_doctors = MahalShifaDoctor.objects.filter(user__is_active=True).count()
        total_verified = MahalShifaDoctor.objects.filter(user__is_active=True, is_available=True).count()
        total_specialties = MahalShifaDoctor.objects.values('specialization').distinct().count()
        
        # Get top specialties
        top_specialties = MahalShifaDoctor.objects.values('specialization').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        extra_context.update({
            'total_doctors': total_doctors,
            'total_verified': total_verified,
            'total_specialties': total_specialties,
            'top_specialties': top_specialties,
        })
        
        return super().changelist_view(request, extra_context)
