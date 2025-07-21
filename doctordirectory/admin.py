from django.contrib import admin
from .models import Doctor, DoctorSchedule, PatientLog, DoctorAvailability


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'its_id', 'specialty', 'assigned_moze', 'is_verified', 'is_available', 'created_at')
    list_filter = ('specialty', 'is_verified', 'is_available', 'assigned_moze', 'created_at')
    search_fields = ('name', 'its_id', 'specialty', 'user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'name', 'its_id', 'phone', 'email', 'address')
        }),
        ('Professional Information', {
            'fields': ('specialty', 'qualification', 'experience_years', 'license_number', 'consultation_fee')
        }),
        ('Assignment', {
            'fields': ('assigned_moze', 'is_verified', 'is_available')
        }),
        ('Documents', {
            'fields': ('verified_certificate',)
        }),
        ('Additional Details', {
            'fields': ('languages_spoken', 'bio'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DoctorSchedule)
class DoctorScheduleAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'date', 'start_time', 'end_time', 'moze', 'schedule_type', 'is_available')
    list_filter = ('date', 'schedule_type', 'is_available', 'moze', 'created_at')
    search_fields = ('doctor__name', 'moze__name', 'notes')
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Schedule Details', {
            'fields': ('doctor', 'date', 'start_time', 'end_time', 'moze')
        }),
        ('Configuration', {
            'fields': ('schedule_type', 'is_available', 'max_patients')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )


@admin.register(PatientLog)
class PatientLogAdmin(admin.ModelAdmin):
    list_display = ('patient_its_id', 'patient_name', 'seen_by', 'moze', 'visit_type', 'timestamp')
    list_filter = ('visit_type', 'follow_up_required', 'timestamp', 'moze', 'seen_by')
    search_fields = ('patient_its_id', 'patient_name', 'ailment', 'diagnosis')
    date_hierarchy = 'timestamp'
    readonly_fields = ('timestamp', 'updated_at')
    
    fieldsets = (
        ('Patient Information', {
            'fields': ('patient_its_id', 'patient_name', 'visit_type')
        }),
        ('Medical Details', {
            'fields': ('ailment', 'symptoms', 'diagnosis', 'prescription')
        }),
        ('Visit Information', {
            'fields': ('seen_by', 'moze', 'schedule')
        }),
        ('Follow-up', {
            'fields': ('follow_up_required', 'follow_up_date'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('timestamp', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'day_of_week_display', 'start_time', 'end_time', 'is_active')
    list_filter = ('day_of_week', 'is_active', 'doctor')
    search_fields = ('doctor__name',)
    
    def day_of_week_display(self, obj):
        return obj.get_day_of_week_display()
    day_of_week_display.short_description = 'Day of Week'
