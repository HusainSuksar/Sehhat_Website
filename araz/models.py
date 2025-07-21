from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from doctordirectory.models import Doctor


class DuaAraz(models.Model):
    """Model for Dua Araz (petitions/requests) from patients"""
    
    # Patient information
    patient_its_id = models.CharField(
        max_length=8,
        validators=[RegexValidator(
            regex=r'^\d{8}$',
            message='Patient ITS ID must be exactly 8 digits'
        )],
        help_text='8-digit ITS ID of the patient'
    )
    patient_name = models.CharField(max_length=100, blank=True, null=True)
    patient_phone = models.CharField(max_length=15, blank=True, null=True)
    patient_email = models.EmailField(blank=True, null=True)
    
    # For registered users (optional)
    patient_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='submitted_araz'
    )
    
    # Request details
    ailment = models.TextField(help_text='Description of the medical condition or concern')
    symptoms = models.TextField(blank=True, null=True, help_text='Detailed symptoms')
    urgency_level = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low - Routine checkup'),
            ('medium', 'Medium - Some concern'),
            ('high', 'High - Urgent attention needed'),
            ('emergency', 'Emergency - Immediate attention required')
        ],
        default='medium'
    )
    
    # Request type
    REQUEST_TYPES = [
        ('consultation', 'Medical Consultation'),
        ('prescription', 'Prescription Request'),
        ('follow_up', 'Follow-up Appointment'),
        ('referral', 'Specialist Referral'),
        ('certificate', 'Medical Certificate'),
        ('second_opinion', 'Second Opinion'),
        ('health_advice', 'General Health Advice'),
        ('other', 'Other'),
    ]
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPES, default='consultation')
    
    # Preferred appointment details
    preferred_date = models.DateField(blank=True, null=True)
    preferred_time = models.TimeField(blank=True, null=True)
    preferred_doctor = models.ForeignKey(
        Doctor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='requested_araz'
    )
    
    # Status tracking
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('assigned', 'Assigned to Doctor'),
        ('scheduled', 'Appointment Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    
    # Assignment details
    assigned_doctor = models.ForeignKey(
        Doctor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_araz'
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_araz'
    )
    assigned_at = models.DateTimeField(null=True, blank=True)
    
    # Response and resolution
    doctor_response = models.TextField(blank=True, null=True)
    resolution_notes = models.TextField(blank=True, null=True)
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(blank=True, null=True)
    
    # Administrative notes
    admin_notes = models.TextField(blank=True, null=True)
    internal_notes = models.TextField(blank=True, null=True)
    priority_score = models.PositiveIntegerField(default=0, help_text='Internal priority score (0-10)')
    
    # Timestamps
    date_submitted = models.DateTimeField(auto_now_add=True)
    date_completed = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_submitted']
        verbose_name = 'Dua Araz'
        verbose_name_plural = 'Dua Araz'
    
    def __str__(self):
        return f"Araz #{self.id} - {self.patient_its_id} ({self.get_status_display()})"
    
    def get_patient_display_name(self):
        if self.patient_name:
            return self.patient_name
        elif self.patient_user:
            return self.patient_user.get_full_name()
        else:
            return f"Patient {self.patient_its_id}"
    
    def is_urgent(self):
        return self.urgency_level in ['high', 'emergency']
    
    def is_overdue(self):
        from django.utils import timezone
        if self.status in ['submitted', 'under_review'] and self.is_urgent():
            # Consider urgent requests overdue after 24 hours
            return timezone.now() > self.date_submitted + timezone.timedelta(days=1)
        elif self.status in ['submitted', 'under_review']:
            # Consider normal requests overdue after 3 days
            return timezone.now() > self.date_submitted + timezone.timedelta(days=3)
        return False
    
    def get_time_since_submission(self):
        from django.utils import timezone
        return timezone.now() - self.date_submitted


class ArazComment(models.Model):
    """Comments and communication thread for Dua Araz"""
    araz = models.ForeignKey(DuaAraz, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    
    # Comment type
    COMMENT_TYPES = [
        ('patient', 'Patient Communication'),
        ('doctor', 'Doctor Response'),
        ('admin', 'Administrative Note'),
        ('system', 'System Update'),
    ]
    comment_type = models.CharField(max_length=20, choices=COMMENT_TYPES, default='admin')
    
    is_visible_to_patient = models.BooleanField(default=True)
    is_internal = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment on Araz #{self.araz.id} by {self.author.get_full_name()}"


class ArazAttachment(models.Model):
    """File attachments for Dua Araz"""
    araz = models.ForeignKey(DuaAraz, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='araz_attachments/%Y/%m/%d/')
    filename = models.CharField(max_length=255)
    description = models.CharField(max_length=200, blank=True, null=True)
    file_size = models.PositiveIntegerField(blank=True, null=True)
    
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # File type classification
    FILE_TYPES = [
        ('medical_report', 'Medical Report'),
        ('prescription', 'Prescription'),
        ('lab_result', 'Lab Result'),
        ('image', 'Image/Photo'),
        ('document', 'Document'),
        ('other', 'Other'),
    ]
    file_type = models.CharField(max_length=20, choices=FILE_TYPES, default='document')
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"Attachment: {self.filename} for Araz #{self.araz.id}"
    
    def get_file_size_mb(self):
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return None


class ArazStatusHistory(models.Model):
    """Track status changes for Dua Araz"""
    araz = models.ForeignKey(DuaAraz, on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    change_reason = models.TextField(blank=True, null=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Araz Status History'
        verbose_name_plural = 'Araz Status Histories'
    
    def __str__(self):
        return f"Araz #{self.araz.id}: {self.old_status} → {self.new_status}"


class ArazNotification(models.Model):
    """Notifications related to Dua Araz"""
    araz = models.ForeignKey(DuaAraz, on_delete=models.CASCADE, related_name='notifications')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    notification_type = models.CharField(
        max_length=30,
        choices=[
            ('status_update', 'Status Update'),
            ('doctor_assigned', 'Doctor Assigned'),
            ('doctor_response', 'Doctor Response'),
            ('appointment_scheduled', 'Appointment Scheduled'),
            ('follow_up_reminder', 'Follow-up Reminder'),
            ('completion_notice', 'Completion Notice'),
        ]
    )
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    is_email_sent = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification for {self.recipient.get_full_name()}: {self.title}"
