from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import Moze, MozeComment, MozeSettings


@admin.register(Moze)
class MozeAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'aamil', 'moze_coordinator', 'is_active', 'capacity', 'get_patient_count', 'get_doctor_count', 'get_hospital_info', 'created_at']
    list_filter = ['is_active', 'established_date', 'created_at']
    search_fields = ['name', 'location', 'aamil__first_name', 'aamil__last_name']
    filter_horizontal = ['team_members']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'location', 'address', 'established_date', 'is_active')
        }),
        ('Management', {
            'fields': ('aamil', 'moze_coordinator', 'team_members')
        }),
        ('Capacity & Contact', {
            'fields': ('capacity', 'contact_phone', 'contact_email')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Annotate with patient and doctor counts"""
        return super().get_queryset(request).annotate(
            patient_count=Count('registered_patients'),
            doctor_count=Count('appointments__doctor', distinct=True)
        )
    
    def get_patient_count(self, obj):
        """Display patient count with color coding"""
        count = getattr(obj, 'patient_count', obj.registered_patients.count())
        if count > 0:
            return format_html('<span style="color: green;">{}</span>', count)
        return format_html('<span style="color: red;">{}</span>', count)
    get_patient_count.short_description = 'Patients'
    get_patient_count.admin_order_field = 'patient_count'
    
    def get_doctor_count(self, obj):
        """Display doctor count with color coding"""
        count = getattr(obj, 'doctor_count', obj.appointments.values('doctor').distinct().count())
        if count > 0:
            return format_html('<span style="color: blue;">{}</span>', count)
        return format_html('<span style="color: red;">{}</span>', count)
    get_doctor_count.short_description = 'Doctors'
    get_doctor_count.admin_order_field = 'doctor_count'
    
    def get_hospital_info(self, obj):
        """Display hospital information"""
        hospitals = obj.appointments.values('doctor__hospital__name').distinct()
        if hospitals:
            hospital_names = [h['doctor__hospital__name'] for h in hospitals if h['doctor__hospital__name']]
            if hospital_names:
                return format_html('<span style="color: green;">{}</span>', ', '.join(set(hospital_names)))
        return format_html('<span style="color: red;">No Hospitals</span>')
    get_hospital_info.short_description = 'Mahal Shifa'


@admin.register(MozeComment)
class MozeCommentAdmin(admin.ModelAdmin):
    list_display = ['moze', 'author', 'content', 'parent', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'moze']
    search_fields = ['content', 'author__first_name', 'author__last_name', 'moze__name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Comment Information', {
            'fields': ('moze', 'author', 'content', 'parent', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MozeSettings)
class MozeSettingsAdmin(admin.ModelAdmin):
    list_display = ['moze', 'allow_walk_ins', 'appointment_duration', 'working_hours_start', 'working_hours_end']
    list_filter = ['allow_walk_ins', 'working_days']
    search_fields = ['moze__name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['moze__name']
    
    fieldsets = (
        ('Moze Settings', {
            'fields': ('moze', 'allow_walk_ins', 'appointment_duration')
        }),
        ('Working Hours', {
            'fields': ('working_hours_start', 'working_hours_end', 'working_days')
        }),
        ('Contact & Instructions', {
            'fields': ('emergency_contact', 'special_instructions')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
