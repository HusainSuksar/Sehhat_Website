from django.contrib import admin
from django.utils.html import format_html
from .models import Hospital, Patient, Appointment, MedicalRecord, Prescription, LabTest


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'city', 'state', 'hospital_type', 'capacity',
        'emergency_services', 'is_active'
    ]
    list_filter = ['hospital_type', 'emergency_services', 'is_active', 'city', 'state']
    search_fields = ['name', 'city', 'state', 'specialties']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'hospital_type', 'capacity')
        }),
        ('Location', {
            'fields': ('address', 'city', 'state')
        }),
        ('Contact Information', {
            'fields': ('phone', 'email', 'website')
        }),
        ('Services', {
            'fields': ('specialties', 'emergency_services')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


class AppointmentInline(admin.TabularInline):
    model = Appointment
    extra = 0
    readonly_fields = ['created_at']
    fields = ['doctor', 'appointment_date', 'appointment_time', 'status', 'created_at']


class MedicalRecordInline(admin.TabularInline):
    model = MedicalRecord
    extra = 0
    readonly_fields = ['created_at']
    fields = ['doctor', 'diagnosis', 'created_at']


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'patient_id', 'age', 'gender', 'blood_group',
        'hospital', 'appointments_count'
    ]
    list_filter = ['gender', 'blood_group', 'hospital', 'created_at']
    search_fields = [
        'user__username', 'user__first_name', 'user__last_name',
        'patient_id', 'emergency_contact_name'
    ]
    readonly_fields = ['created_at', 'updated_at', 'age']
    inlines = [AppointmentInline, MedicalRecordInline]
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'patient_id')
        }),
        ('Personal Information', {
            'fields': ('date_of_birth', 'age', 'gender', 'blood_group')
        }),
        ('Contact Information', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'address')
        }),
        ('Medical Information', {
            'fields': ('allergies', 'medical_history', 'current_medications')
        }),
        ('Insurance Information', {
            'fields': ('insurance_provider', 'insurance_policy_number')
        }),
        ('Hospital Assignment', {
            'fields': ('hospital',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def appointments_count(self, obj):
        return obj.appointments.count()
    appointments_count.short_description = 'Appointments'


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        'patient', 'doctor', 'appointment_date', 'appointment_time',
        'appointment_type', 'status_display', 'created_at'
    ]
    list_filter = [
        'status', 'appointment_type', 'appointment_date', 'created_at'
    ]
    search_fields = [
        'patient__user__username', 'patient__patient_id',
        'doctor__user__username', 'reason'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Appointment Details', {
            'fields': ('patient', 'doctor', 'appointment_date', 'appointment_time')
        }),
        ('Type and Status', {
            'fields': ('appointment_type', 'status')
        }),
        ('Information', {
            'fields': ('reason', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def status_display(self, obj):
        colors = {
            'scheduled': 'blue',
            'confirmed': 'green',
            'completed': 'darkgreen',
            'cancelled': 'red',
            'no_show': 'orange'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Status'


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = [
        'patient', 'doctor', 'diagnosis_preview', 'created_at'
    ]
    list_filter = ['created_at', 'doctor']
    search_fields = [
        'patient__user__username', 'patient__patient_id',
        'doctor__user__username', 'diagnosis', 'symptoms'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Patient and Doctor', {
            'fields': ('patient', 'doctor')
        }),
        ('Medical Information', {
            'fields': ('symptoms', 'diagnosis', 'treatment')
        }),
        ('Prescription and Follow-up', {
            'fields': ('prescription', 'follow_up_date')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def diagnosis_preview(self, obj):
        return obj.diagnosis[:50] + '...' if len(obj.diagnosis) > 50 else obj.diagnosis
    diagnosis_preview.short_description = 'Diagnosis'


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = [
        'patient', 'doctor', 'medication_name', 'dosage',
        'frequency', 'duration', 'created_at'
    ]
    list_filter = ['created_at', 'doctor']
    search_fields = [
        'patient__user__username', 'patient__patient_id',
        'doctor__user__username', 'medication_name'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Patient and Doctor', {
            'fields': ('patient', 'doctor')
        }),
        ('Medication Details', {
            'fields': ('medication_name', 'dosage', 'frequency', 'duration')
        }),
        ('Instructions and Refills', {
            'fields': ('instructions', 'refills')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(LabTest)
class LabTestAdmin(admin.ModelAdmin):
    list_display = [
        'patient', 'doctor', 'test_name', 'test_type',
        'status', 'urgent', 'ordered_at'
    ]
    list_filter = ['test_type', 'status', 'urgent', 'ordered_at']
    search_fields = [
        'patient__user__username', 'patient__patient_id',
        'doctor__user__username', 'test_name'
    ]
    readonly_fields = ['ordered_at', 'updated_at']
    
    fieldsets = (
        ('Patient and Doctor', {
            'fields': ('patient', 'doctor')
        }),
        ('Test Information', {
            'fields': ('test_name', 'test_type', 'urgent')
        }),
        ('Instructions and Status', {
            'fields': ('instructions', 'status')
        }),
        ('Results', {
            'fields': ('results', 'result_date')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('ordered_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
