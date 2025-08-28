from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponseRedirect
from .models import BulkUploadSession, BulkUploadRecord, UploadTemplate

@admin.register(BulkUploadSession)
class BulkUploadSessionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'upload_type', 'uploaded_by', 'original_filename',
        'status_badge', 'progress_display', 'started_at', 'file_size_display'
    ]
    list_filter = ['upload_type', 'status', 'started_at']
    search_fields = ['original_filename', 'uploaded_by__username']
    readonly_fields = [
        'started_at', 'completed_at', 'total_rows', 
        'successful_rows', 'failed_rows', 'file_size'
    ]
    ordering = ['-started_at']
    
    def status_badge(self, obj):
        colors = {
            'pending': '#FFA500',
            'processing': '#0066CC',
            'completed': '#008800',
            'failed': '#CC0000',
            'partially_completed': '#9900CC'
        }
        color = colors.get(obj.status, '#000000')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def progress_display(self, obj):
        if obj.total_rows > 0:
            percentage = (obj.successful_rows / obj.total_rows) * 100
            return f"{percentage:.1f}% ({obj.successful_rows}/{obj.total_rows})"
        return "N/A"
    progress_display.short_description = 'Progress'
    
    def file_size_display(self, obj):
        if obj.file_size:
            if obj.file_size > 1024 * 1024:
                return f"{obj.file_size / (1024 * 1024):.1f} MB"
            elif obj.file_size > 1024:
                return f"{obj.file_size / 1024:.1f} KB"
            else:
                return f"{obj.file_size} bytes"
        return "Unknown"
    file_size_display.short_description = 'File Size'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('upload_type', 'uploaded_by', 'original_filename', 'file_size')
        }),
        ('Status', {
            'fields': ('status', 'started_at', 'completed_at')
        }),
        ('Results', {
            'fields': ('total_rows', 'successful_rows', 'failed_rows', 'summary_report')
        }),
    )
    
    actions = ['retry_failed_uploads']
    
    def retry_failed_uploads(self, request, queryset):
        retried = 0
        for session in queryset.filter(status='failed'):
            session.status = 'pending'
            session.save()
            retried += 1
        
        self.message_user(
            request,
            f'{retried} upload session(s) queued for retry.'
        )
    retry_failed_uploads.short_description = "Retry failed uploads"

@admin.register(BulkUploadRecord)
class BulkUploadRecordAdmin(admin.ModelAdmin):
    list_display = ['session', 'row_number', 'status', 'processed_at', 'error_message_short']
    list_filter = ['status', 'processed_at', 'session__upload_type']
    search_fields = ['error_message', 'session__original_filename', 'raw_data']
    readonly_fields = ['session', 'row_number', 'status', 'error_message', 'processed_at', 'raw_data']
    ordering = ['-processed_at']
    
    def error_message_short(self, obj):
        if obj.error_message:
            return obj.error_message[:50] + '...' if len(obj.error_message) > 50 else obj.error_message
        return '-'
    error_message_short.short_description = 'Error Message'

@admin.register(UploadTemplate)
class UploadTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'upload_type', 'is_active', 'created_at']
    list_filter = ['upload_type', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['upload_type', 'name']
