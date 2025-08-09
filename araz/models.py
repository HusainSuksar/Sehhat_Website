from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from django.utils import timezone
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
        ('health_check', 'General Health Check'),
        ('emergency', 'Emergency Case'),
        ('referral', 'Specialist Referral'),
        ('second_opinion', 'Second Opinion'),
        ('home_visit', 'Home Visit Request'),
        ('telemedicine', 'Telemedicine Consultation'),
        ('laboratory', 'Laboratory Tests'),
        ('imaging', 'Medical Imaging'),
        ('therapy', 'Physical Therapy'),
        ('vaccination', 'Vaccination'),
        ('chronic_care', 'Chronic Disease Management'),
        ('mental_health', 'Mental Health Support'),
        ('nutrition', 'Nutrition Consultation'),
        ('dental', 'Dental Care'),
        ('ophthalmology', 'Eye Care'),
        ('pediatric', 'Pediatric Care'),
        ('geriatric', 'Geriatric Care'),
        ('womens_health', 'Women\'s Health'),
        ('mens_health', 'Men\'s Health'),
        ('rehabilitation', 'Rehabilitation Services'),
        ('pain_management', 'Pain Management'),
        ('allergy', 'Allergy Treatment'),
        ('other', 'Other')
    ]
    
    request_type = models.CharField(
        max_length=30,
        choices=REQUEST_TYPES,
        default='consultation'
    )
    
    # Medical history
    previous_medical_history = models.TextField(blank=True, null=True)
    current_medications = models.TextField(blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    
    # Preferred doctor/location
    preferred_doctor = models.ForeignKey(
        Doctor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='requested_araz'
    )
    preferred_location = models.CharField(max_length=100, blank=True, null=True)
    preferred_time = models.DateTimeField(blank=True, null=True)
    
    # Status and processing
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('follow_up_required', 'Follow-up Required')
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    priority = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('urgent', 'Urgent')
        ],
        default='medium'
    )
    
    # Assignment and processing
    assigned_doctor = models.ForeignKey(
        Doctor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_araz'
    )
    assigned_date = models.DateTimeField(blank=True, null=True)
    scheduled_date = models.DateTimeField(blank=True, null=True)
    
    # Administrative notes
    admin_notes = models.TextField(blank=True, null=True)
    patient_feedback = models.TextField(blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Contact preferences
    preferred_contact_method = models.CharField(
        max_length=20,
        choices=[
            ('phone', 'Phone Call'),
            ('email', 'Email'),
            ('sms', 'SMS'),
            ('whatsapp', 'WhatsApp'),
            ('in_person', 'In Person')
        ],
        default='phone'
    )
    
    class Meta:
        verbose_name = 'Dua Araz'
        verbose_name_plural = 'Dua Araz'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.patient_name or self.patient_its_id} - {self.get_request_type_display()}"


# Petition models for views compatibility
class PetitionCategory(models.Model):
    """Categories for organizing petitions"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#007bff')  # Hex color
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Petition Categories'
    
    def __str__(self):
        return self.name


class Petition(models.Model):
    """General petition/complaint model"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(
        PetitionCategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='petitions'
    )
    
    # User information
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_petitions'
    )
    is_anonymous = models.BooleanField(default=False)
    
    # Petitioner details (can be filled from ITS or manually)
    petitioner_name = models.CharField(max_length=200, help_text="Full name of the petitioner")
    petitioner_mobile = models.CharField(max_length=20, blank=True, help_text="Mobile number of the petitioner")
    petitioner_email = models.EmailField(blank=True, help_text="Email address of the petitioner")
    its_id = models.CharField(max_length=8, blank=True, help_text="ITS ID if available")
    
    # Status and priority
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # Location reference
    moze = models.ForeignKey(
        'moze.Moze',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='petitions'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class ArazComment(models.Model):
    """Comments on Araz requests"""
    araz = models.ForeignKey(DuaAraz, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    is_internal = models.BooleanField(default=False)  # Internal notes vs public comments
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment on {self.araz} by {self.author}"


class PetitionComment(models.Model):
    """Comments on petitions"""
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    is_internal = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.user.get_full_name()}"


class ArazAttachment(models.Model):
    """File attachments for Araz requests"""
    araz = models.ForeignKey(DuaAraz, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='araz_attachments/')
    original_filename = models.CharField(max_length=255, default='unknown')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_size = models.PositiveIntegerField(help_text='File size in bytes', default=0)
    
    def __str__(self):
        return f"Attachment: {self.original_filename}"


class PetitionAttachment(models.Model):
    """File attachments for petitions"""
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='petition_attachments/')
    filename = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.filename


class ArazStatusHistory(models.Model):
    """Track status changes for Araz requests"""
    araz = models.ForeignKey(DuaAraz, on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    change_reason = models.TextField(blank=True, null=True)
    changed_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name_plural = 'Araz Status Histories'
        ordering = ['-changed_at']
    
    def __str__(self):
        return f"{self.araz} status changed from {self.old_status} to {self.new_status}"


class PetitionAssignment(models.Model):
    """Assignment of petitions to users"""
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE, related_name='assignments')
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='petition_assignments'
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assigned_petitions'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.petition.title} assigned to {self.assigned_to.get_full_name()}"


class PetitionUpdate(models.Model):
    """Status updates for petitions"""
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE, related_name='updates')
    status = models.CharField(max_length=20, choices=Petition.STATUS_CHOICES)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.petition.title} - {self.get_status_display()}"


class PetitionStatus(models.Model):
    """Status tracking for petitions (alternative approach)"""
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#6c757d')
    is_final = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name_plural = 'Petition Statuses'
        ordering = ['order']
    
    def __str__(self):
        return self.name


class ArazNotification(models.Model):
    """Notifications related to Araz requests"""
    araz = models.ForeignKey(DuaAraz, on_delete=models.CASCADE, related_name='notifications')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20,
        choices=[
            ('status_update', 'Status Update'),
            ('assignment', 'Assignment'),
            ('comment', 'New Comment'),
            ('reminder', 'Reminder'),
            ('escalation', 'Escalation')
        ]
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification for {self.recipient} about {self.araz}"
