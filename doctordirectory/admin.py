from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import (
    Doctor, DoctorSchedule, MedicalService, Patient, Appointment, PatientLog
)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'specialty', 'is_verified', 'is_available', 'assigned_moze', 'get_patient_count', 'get_appointment_count', 'created_at']
    list_filter = ['is_verified', 'is_available', 'specialty', 'assigned_moze', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'specialty', 'license_number']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['user__first_name', 'user__last_name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'its_id', 'user', 'specialty', 'qualification', 'experience_years')
        }),
        ('Professional Details', {
            'fields': ('verified_certificate', 'is_verified', 'is_available', 'license_number', 'consultation_fee', 'bio')
        }),
        ('Contact Information', {
            'fields': ('phone', 'email', 'address', 'languages_spoken')
        }),
        ('Assignment', {
            'fields': ('assigned_moze',)
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
    list_display = ['get_full_name', 'user', 'date_of_birth', 'gender', 'get_age', 'get_appointment_count', 'created_at']
    list_filter = ['gender', 'blood_group', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    readonly_fields = ['created_at', 'updated_at', 'get_age']
    ordering = ['user__first_name', 'user__last_name']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'date_of_birth', 'gender')
        }),
        ('Medical Information', {
            'fields': ('blood_group', 'allergies', 'medical_history', 'current_medications')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with appointment count"""
        return super().get_queryset(request).select_related('user').annotate(
            appointment_count=Count('appointments')
        )
    
    def get_full_name(self, obj):
        """Display patient full name"""
        return obj.user.get_full_name() if obj.user else 'Unknown'
    get_full_name.short_description = 'Full Name'
    get_full_name.admin_order_field = 'user__first_name'
    
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
    search_fields = ['patient__user__first_name', 'patient__user__last_name', 'doctor__user__first_name', 'doctor__user__last_name', 'reason_for_visit']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-appointment_date', '-appointment_time']
    date_hierarchy = 'appointment_date'
    
    fieldsets = (
        ('Appointment Details', {
            'fields': ('doctor', 'patient', 'appointment_date', 'appointment_time', 'status')
        }),
        ('Description', {
            'fields': ('service', 'reason_for_visit', 'notes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with related objects"""
        return super().get_queryset(request).select_related('patient__user', 'doctor__user', 'service')
    
    def get_patient_name(self, obj):
        """Display patient name"""
        return obj.patient.user.get_full_name() if obj.patient.user else 'Unknown'
    get_patient_name.short_description = 'Patient'
    get_patient_name.admin_order_field = 'patient__user__first_name'
    
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
    list_display = ['name', 'get_doctor_name', 'duration_minutes', 'price', 'is_available', 'created_at']
    list_filter = ['is_available', 'duration_minutes', 'created_at']
    search_fields = ['name', 'description', 'doctor__user__first_name', 'doctor__user__last_name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']
    
    fieldsets = (
        ('Service Details', {
            'fields': ('doctor', 'name', 'description')
        }),
        ('Service Configuration', {
            'fields': ('duration_minutes', 'price', 'is_available')
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
