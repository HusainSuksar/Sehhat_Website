from django.db import models
from django.conf import settings
from django.utils import timezone
import json


class BulkUploadSession(models.Model):
    """Track bulk upload sessions and their results"""
    
    UPLOAD_TYPE_CHOICES = [
        ('users', 'Users'),
        ('students', 'Students'),
        ('doctors', 'Doctors'),
        ('moze', 'Moze Centers'),
        ('surveys', 'Surveys'),
        ('evaluations', 'Evaluations'),
        ('patients', 'Patients'),
        ('medical_records', 'Medical Records'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('partially_completed', 'Partially Completed'),
    ]
    
    # Session metadata
    upload_type = models.CharField(max_length=20, choices=UPLOAD_TYPE_CHOICES)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bulk_uploads'
    )
    
    # File information
    original_filename = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500, blank=True, null=True)
    file_size = models.PositiveIntegerField(help_text='File size in bytes')
    
    # Processing status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    # Results summary
    total_rows = models.PositiveIntegerField(default=0)
    successful_rows = models.PositiveIntegerField(default=0)
    failed_rows = models.PositiveIntegerField(default=0)
    skipped_rows = models.PositiveIntegerField(default=0)
    
    # Processing details
    validation_errors = models.JSONField(default=dict, blank=True)
    processing_log = models.JSONField(default=list, blank=True)
    
    # Configuration
    options = models.JSONField(default=dict, blank=True, help_text='Upload options and settings')
    
    class Meta:
        ordering = ['-started_at']
        verbose_name = 'Bulk Upload Session'
        verbose_name_plural = 'Bulk Upload Sessions'
    
    def __str__(self):
        return f"{self.get_upload_type_display()} upload by {self.uploaded_by.get_full_name()} on {self.started_at.strftime('%Y-%m-%d %H:%M')}"
    
    def get_success_rate(self):
        """Calculate success rate percentage"""
        if self.total_rows == 0:
            return 0
        return round((self.successful_rows / self.total_rows) * 100, 2)
    
    def add_log_entry(self, level, message, row_number=None):
        """Add an entry to the processing log"""
        log_entry = {
            'timestamp': timezone.now().isoformat(),
            'level': level,  # 'info', 'warning', 'error'
            'message': message,
            'row_number': row_number
        }
        self.processing_log.append(log_entry)
        self.save(update_fields=['processing_log'])
    
    def mark_completed(self):
        """Mark the upload session as completed"""
        self.status = 'completed' if self.failed_rows == 0 else 'partially_completed'
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])
    
    def mark_failed(self, error_message):
        """Mark the upload session as failed"""
        self.status = 'failed'
        self.completed_at = timezone.now()
        self.add_log_entry('error', f'Upload failed: {error_message}')
        self.save(update_fields=['status', 'completed_at'])


class BulkUploadRecord(models.Model):
    """Individual record within a bulk upload session"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped'),
    ]
    
    session = models.ForeignKey(
        BulkUploadSession,
        on_delete=models.CASCADE,
        related_name='records'
    )
    
    # Row information
    row_number = models.PositiveIntegerField()
    raw_data = models.JSONField(help_text='Original data from the row')
    processed_data = models.JSONField(blank=True, null=True, help_text='Processed/cleaned data')
    
    # Processing results
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    validation_errors = models.JSONField(default=list, blank=True)
    
    # Created object reference (if successful)
    created_object_type = models.CharField(max_length=50, blank=True, null=True)
    created_object_id = models.PositiveIntegerField(blank=True, null=True)
    
    # Timestamps
    processed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['row_number']
        unique_together = ['session', 'row_number']
        verbose_name = 'Bulk Upload Record'
        verbose_name_plural = 'Bulk Upload Records'
    
    def __str__(self):
        return f"Row {self.row_number} - {self.get_status_display()}"
    
    def mark_success(self, created_object=None):
        """Mark this record as successfully processed"""
        self.status = 'success'
        if created_object:
            self.created_object_type = created_object.__class__.__name__
            self.created_object_id = created_object.pk
        self.save(update_fields=['status', 'created_object_type', 'created_object_id'])
        
        # Update session counters
        self.session.successful_rows += 1
        self.session.save(update_fields=['successful_rows'])
    
    def mark_failed(self, error_message, validation_errors=None):
        """Mark this record as failed"""
        self.status = 'failed'
        self.error_message = error_message
        if validation_errors:
            self.validation_errors = validation_errors
        self.save(update_fields=['status', 'error_message', 'validation_errors'])
        
        # Update session counters
        self.session.failed_rows += 1
        self.session.save(update_fields=['failed_rows'])
    
    def mark_skipped(self, reason):
        """Mark this record as skipped"""
        self.status = 'skipped'
        self.error_message = reason
        self.save(update_fields=['status', 'error_message'])
        
        # Update session counters
        self.session.skipped_rows += 1
        self.session.save(update_fields=['skipped_rows'])


class UploadTemplate(models.Model):
    """Predefined templates for different upload types"""
    
    upload_type = models.CharField(max_length=20, choices=BulkUploadSession.UPLOAD_TYPE_CHOICES, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    # Template configuration
    required_columns = models.JSONField(help_text='List of required column names')
    optional_columns = models.JSONField(default=list, help_text='List of optional column names')
    column_mappings = models.JSONField(default=dict, help_text='Mapping from column names to model fields')
    validation_rules = models.JSONField(default=dict, help_text='Validation rules for each column')
    
    # Sample data
    sample_data = models.JSONField(default=list, help_text='Sample rows for the template')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['upload_type']
        verbose_name = 'Upload Template'
        verbose_name_plural = 'Upload Templates'
    
    def __str__(self):
        return f"{self.name} ({self.get_upload_type_display()})"
    
    def get_all_columns(self):
        """Get all columns (required + optional)"""
        return self.required_columns + self.optional_columns
    
    def validate_headers(self, headers):
        """Validate that all required headers are present"""
        missing_headers = []
        for required_col in self.required_columns:
            if required_col not in headers:
                missing_headers.append(required_col)
        return missing_headers
