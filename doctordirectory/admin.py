from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import (
    Doctor, DoctorSchedule, MedicalService, Patient, Appointment
)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'user', 'specialty', 'is_active', 'is_accepting_patients', 'assigned_moze', 'get_patient_count', 'get_appointment_count', 'created_at']
    list_filter = ['is_active', 'is_accepting_patients', 'specialty', 'assigned_moze', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'specialty', 'license_number']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['user__first_name', 'user__last_name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'license_number', 'specialty', 'qualification', 'experience_years')
        }),
        ('Professional Details', {
            'fields': ('consultation_fee', 'bio', 'hospital_affiliation', 'consultation_hours')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'email', 'address')
        }),
        ('Status & Assignment', {
            'fields': ('is_active', 'is_accepting_patients', 'assigned_moze')
        }),
        ('Media', {
            'fields': ('profile_photo',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Annotate with patient and appointment counts"""
        return super().get_queryset(request).select_related('user', 'assigned_moze').annotate(
            patient_count=Count('appointments__patient', distinct=True),
            appointment_count=Count('appointments')
        )
    
    def get_patient_count(self, obj):
        """Display patient count with color coding"""
        count = getattr(obj, 'patient_count', obj.appointments.values('patient').distinct().count())
        if count > 0:
            return format_html('<span style="color: green; font-weight: bold;">{}</span>', count)
        return format_html('<span style="color: gray;">0</span>')
    get_patient_count.short_description = 'Patients'
    get_patient_count.admin_order_field = 'patient_count'
    
    def get_appointment_count(self, obj):
        """Display appointment count with color coding"""
        count = getattr(obj, 'appointment_count', obj.appointments.count())
        if count > 10:
            color = 'green'
        elif count > 5:
            color = 'orange'
        else:
            color = 'gray'
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, count)
    get_appointment_count.short_description = 'Appointments'
    get_appointment_count.admin_order_field = 'appointment_count'


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'user_account', 'phone_number', 'date_of_birth', 'gender', 'get_age', 'get_appointment_count', 'created_at']
    list_filter = ['gender', 'blood_group', 'created_at']
    search_fields = ['full_name', 'phone_number', 'email', 'user_account__first_name', 'user_account__last_name']
    readonly_fields = ['created_at', 'updated_at', 'get_age']
    ordering = ['full_name']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('user_account', 'full_name', 'date_of_birth', 'gender')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'email', 'address')
        }),
        ('Medical Information', {
            'fields': ('blood_group', 'allergies', 'medical_history')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with appointment count"""
        return super().get_queryset(request).select_related('user_account').annotate(
            appointment_count=Count('appointments')
        )
    
    def get_age(self, obj):
        """Display calculated age"""
        return f"{obj.age} years"
    get_age.short_description = 'Age'
    
    def get_appointment_count(self, obj):
        """Display appointment count"""
        count = getattr(obj, 'appointment_count', obj.appointments.count())
        if count > 0:
            return format_html('<span style="color: blue; font-weight: bold;">{}</span>', count)
        return format_html('<span style="color: gray;">0</span>')
    get_appointment_count.short_description = 'Appointments'
    get_appointment_count.admin_order_field = 'appointment_count'


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['get_patient_name', 'get_doctor_name', 'appointment_date', 'appointment_time', 'status', 'created_at']
    list_filter = ['status', 'appointment_date', 'created_at']
    search_fields = ['patient__full_name', 'doctor__user__first_name', 'doctor__user__last_name', 'reason']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-appointment_date', '-appointment_time']
    date_hierarchy = 'appointment_date'
    
    fieldsets = (
        ('Appointment Details', {
            'fields': ('doctor', 'patient', 'appointment_date', 'appointment_time', 'status')
        }),
        ('Description', {
            'fields': ('reason', 'notes')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with related objects"""
        return super().get_queryset(request).select_related('patient', 'doctor__user', 'created_by')
    
    def get_patient_name(self, obj):
        """Display patient name"""
        return obj.patient.full_name
    get_patient_name.short_description = 'Patient'
    get_patient_name.admin_order_field = 'patient__full_name'
    
    def get_doctor_name(self, obj):
        """Display doctor name"""
        return obj.doctor.get_full_name()
    get_doctor_name.short_description = 'Doctor'
    get_doctor_name.admin_order_field = 'doctor__user__first_name'


@admin.register(DoctorSchedule)
class DoctorScheduleAdmin(admin.ModelAdmin):
    list_display = ['get_doctor_name', 'date', 'start_time', 'end_time', 'is_available', 'max_patients', 'created_at']
    list_filter = ['is_available', 'date', 'created_at']
    search_fields = ['doctor__user__first_name', 'doctor__user__last_name', 'notes']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-date', 'start_time']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Schedule Details', {
            'fields': ('doctor', 'date', 'start_time', 'end_time')
        }),
        ('Availability', {
            'fields': ('is_available', 'max_patients', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related('doctor__user')
    
    def get_doctor_name(self, obj):
        """Display doctor name"""
        return obj.doctor.get_full_name()
    get_doctor_name.short_description = 'Doctor'
    get_doctor_name.admin_order_field = 'doctor__user__first_name'


@admin.register(MedicalService)
class MedicalServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_doctor_name', 'duration_minutes', 'price', 'is_active', 'created_at']
    list_filter = ['is_active', 'duration_minutes', 'created_at']
    search_fields = ['name', 'description', 'doctor__user__first_name', 'doctor__user__last_name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']
    
    fieldsets = (
        ('Service Details', {
            'fields': ('doctor', 'name', 'description')
        }),
        ('Service Configuration', {
            'fields': ('duration_minutes', 'price', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related('doctor__user')
    
    def get_doctor_name(self, obj):
        """Display doctor name"""
        return obj.doctor.get_full_name()
    get_doctor_name.short_description = 'Doctor'
    get_doctor_name.admin_order_field = 'doctor__user__first_name'


# Admin site customization
admin.site.site_header = "Umoor Sehhat - Doctor Directory Admin"
admin.site.site_title = "Doctor Directory Admin"
admin.site.index_title = "Doctor Directory Management"
