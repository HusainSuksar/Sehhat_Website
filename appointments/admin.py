from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from .models import (
    Appointment, TimeSlot, AppointmentLog,
    AppointmentReminder, WaitingList
)


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = [
        'doctor', 'date', 'start_time', 'end_time',
        'is_available', 'is_booked', 'current_appointments',
        'max_appointments', 'duration_display'
    ]
    list_filter = [
        'date', 'is_available', 'is_booked', 'doctor',
        'is_recurring'
    ]
    search_fields = ['doctor__name', 'doctor__user__first_name', 'doctor__user__last_name']
    date_hierarchy = 'date'
    ordering = ['-date', 'start_time']
    
    def duration_display(self, obj):
        return f"{obj.duration_minutes} mins"
    duration_display.short_description = 'Duration'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('doctor', 'date', 'start_time', 'end_time')
        }),
        ('Availability', {
            'fields': ('is_available', 'is_booked', 'max_appointments', 'current_appointments')
        }),
        ('Recurring Settings', {
            'fields': ('is_recurring', 'recurring_days', 'recurring_end_date'),
            'classes': ('collapse',)
        }),
    )


class AppointmentLogInline(admin.TabularInline):
    model = AppointmentLog
    extra = 0
    readonly_fields = ['action', 'performed_by', 'timestamp', 'notes']
    can_delete = False


class AppointmentReminderInline(admin.TabularInline):
    model = AppointmentReminder
    extra = 0
    readonly_fields = ['sent_at', 'status', 'error_message']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        'appointment_id_short', 'patient_name', 'doctor_name',
        'appointment_date', 'appointment_time', 'status_badge',
        'appointment_type', 'is_paid', 'created_at'
    ]
    list_filter = [
        'status', 'appointment_type', 'appointment_date',
        'is_paid', 'doctor', 'booking_method', 'payment_method'
    ]
    search_fields = [
        'appointment_id', 'patient__user__first_name',
        'patient__user__last_name', 'doctor__name',
        'doctor__user__first_name', 'doctor__user__last_name',
        'reason_for_visit'
    ]
    date_hierarchy = 'appointment_date'
    ordering = ['-appointment_date', '-appointment_time']
    readonly_fields = [
        'appointment_id', 'created_at', 'updated_at',
        'confirmed_at', 'completed_at', 'cancelled_at'
    ]
    inlines = [AppointmentLogInline, AppointmentReminderInline]
    
    def appointment_id_short(self, obj):
        return str(obj.appointment_id)[:8] + '...'
    appointment_id_short.short_description = 'ID'
    
    def patient_name(self, obj):
        if obj.patient and obj.patient.user:
            return obj.patient.user.get_full_name()
        return 'Unknown Patient'
    patient_name.short_description = 'Patient'
    
    def doctor_name(self, obj):
        return obj.doctor.get_full_name()
    doctor_name.short_description = 'Doctor'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#FFA500',
            'confirmed': '#0066CC',
            'scheduled': '#0066CC',
            'in_progress': '#00AA00',
            'completed': '#008800',
            'cancelled': '#CC0000',
            'no_show': '#666666',
            'rescheduled': '#9900CC'
        }
        color = colors.get(obj.status, '#000000')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'appointment_id', 'doctor', 'patient', 'service',
                'appointment_date', 'appointment_time', 'duration_minutes',
                'appointment_type', 'status'
            )
        }),
        ('Medical Details', {
            'fields': (
                'reason_for_visit', 'symptoms', 'chief_complaint',
                'notes', 'doctor_notes'
            )
        }),
        ('Booking Information', {
            'fields': (
                'booked_by', 'booking_method', 'time_slot',
                'requires_confirmation', 'confirmation_sent',
                'reminder_sent'
            )
        }),
        ('Payment', {
            'fields': ('consultation_fee', 'is_paid', 'payment_method')
        }),
        ('Follow-up', {
            'fields': ('follow_up_required', 'follow_up_date'),
            'classes': ('collapse',)
        }),
        ('Cancellation/Rescheduling', {
            'fields': (
                'cancelled_at', 'cancelled_by', 'cancellation_reason',
                'rescheduled_from'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 'updated_at', 'confirmed_at', 'completed_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['confirm_appointments', 'cancel_appointments', 'mark_as_completed']
    
    def confirm_appointments(self, request, queryset):
        confirmed = 0
        for appointment in queryset:
            if appointment.status == 'pending':
                appointment.confirm(confirmed_by=request.user)
                confirmed += 1
        
        self.message_user(
            request,
            f'{confirmed} appointment(s) confirmed successfully.'
        )
    confirm_appointments.short_description = "Confirm selected appointments"
    
    def cancel_appointments(self, request, queryset):
        cancelled = 0
        for appointment in queryset:
            if appointment.can_cancel():
                appointment.cancel(
                    cancelled_by=request.user,
                    reason='Bulk cancellation by admin'
                )
                cancelled += 1
        
        self.message_user(
            request,
            f'{cancelled} appointment(s) cancelled successfully.'
        )
    cancel_appointments.short_description = "Cancel selected appointments"
    
    def mark_as_completed(self, request, queryset):
        completed = 0
        for appointment in queryset:
            if appointment.status in ['confirmed', 'scheduled', 'in_progress']:
                appointment.complete(completed_by=request.user)
                completed += 1
        
        self.message_user(
            request,
            f'{completed} appointment(s) marked as completed.'
        )
    mark_as_completed.short_description = "Mark selected appointments as completed"


@admin.register(AppointmentLog)
class AppointmentLogAdmin(admin.ModelAdmin):
    list_display = [
        'appointment', 'action', 'performed_by',
        'timestamp', 'notes_truncated'
    ]
    list_filter = ['action', 'timestamp']
    search_fields = [
        'appointment__appointment_id', 'notes',
        'performed_by__username', 'performed_by__first_name',
        'performed_by__last_name'
    ]
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
    readonly_fields = [
        'appointment', 'action', 'performed_by',
        'timestamp', 'old_values', 'new_values'
    ]
    
    def notes_truncated(self, obj):
        if obj.notes:
            return obj.notes[:50] + '...' if len(obj.notes) > 50 else obj.notes
        return '-'
    notes_truncated.short_description = 'Notes'


@admin.register(AppointmentReminder)
class AppointmentReminderAdmin(admin.ModelAdmin):
    list_display = [
        'appointment', 'reminder_type', 'scheduled_for',
        'is_sent', 'status_badge', 'sent_at'
    ]
    list_filter = [
        'reminder_type', 'status', 'is_sent',
        'scheduled_for'
    ]
    search_fields = ['appointment__appointment_id']
    date_hierarchy = 'scheduled_for'
    ordering = ['scheduled_for']
    readonly_fields = ['sent_at', 'is_sent']
    
    def status_badge(self, obj):
        colors = {
            'pending': '#FFA500',
            'sent': '#008800',
            'failed': '#CC0000',
            'cancelled': '#666666'
        }
        color = colors.get(obj.status, '#000000')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.status.upper()
        )
    status_badge.short_description = 'Status'
    
    actions = ['send_reminders']
    
    def send_reminders(self, request, queryset):
        sent = 0
        for reminder in queryset:
            if not reminder.is_sent:
                # Here you would implement actual sending logic
                reminder.is_sent = True
                reminder.sent_at = timezone.now()
                reminder.status = 'sent'
                reminder.save()
                sent += 1
        
        self.message_user(
            request,
            f'{sent} reminder(s) sent successfully.'
        )
    send_reminders.short_description = "Send selected reminders"


@admin.register(WaitingList)
class WaitingListAdmin(admin.ModelAdmin):
    list_display = [
        'patient_name', 'doctor_name', 'preferred_date',
        'appointment_type', 'priority_badge', 'is_active',
        'notified', 'created_at'
    ]
    list_filter = [
        'is_active', 'notified', 'appointment_type',
        'priority', 'preferred_date', 'doctor'
    ]
    search_fields = [
        'patient__user__first_name', 'patient__user__last_name',
        'doctor__name', 'doctor__user__first_name',
        'doctor__user__last_name', 'reason'
    ]
    date_hierarchy = 'preferred_date'
    ordering = ['priority', 'created_at']
    
    def patient_name(self, obj):
        if obj.patient and obj.patient.user:
            return obj.patient.user.get_full_name()
        return 'Unknown Patient'
    patient_name.short_description = 'Patient'
    
    def doctor_name(self, obj):
        return obj.doctor.get_full_name()
    doctor_name.short_description = 'Doctor'
    
    def priority_badge(self, obj):
        if obj.priority <= 3:
            color = '#CC0000'  # High priority - Red
        elif obj.priority <= 6:
            color = '#FFA500'  # Medium priority - Orange
        else:
            color = '#008800'  # Low priority - Green
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.priority
        )
    priority_badge.short_description = 'Priority'
    
    fieldsets = (
        ('Patient Information', {
            'fields': ('patient', 'doctor')
        }),
        ('Preferences', {
            'fields': (
                'preferred_date', 'preferred_time_start',
                'preferred_time_end', 'appointment_type'
            )
        }),
        ('Details', {
            'fields': ('reason', 'priority')
        }),
        ('Status', {
            'fields': ('is_active', 'notified')
        }),
    )
    
    actions = ['notify_patients', 'deactivate_entries']
    
    def notify_patients(self, request, queryset):
        notified = 0
        for entry in queryset:
            if entry.is_active and not entry.notified:
                # Here you would implement notification logic
                entry.notified = True
                entry.save()
                notified += 1
        
        self.message_user(
            request,
            f'{notified} patient(s) notified successfully.'
        )
    notify_patients.short_description = "Notify selected patients"
    
    def deactivate_entries(self, request, queryset):
        deactivated = queryset.filter(is_active=True).update(is_active=False)
        self.message_user(
            request,
            f'{deactivated} waiting list entries deactivated.'
        )
    deactivate_entries.short_description = "Deactivate selected entries"