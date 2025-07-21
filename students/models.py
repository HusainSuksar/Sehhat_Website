from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from moze.models import Moze


class StudentProfile(models.Model):
    """Extended profile for students"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile',
        limit_choices_to={'role': 'student'}
    )
    its_id = models.CharField(
        max_length=8,
        unique=True,
        validators=[RegexValidator(
            regex=r'^\d{8}$',
            message='ITS ID must be exactly 8 digits'
        )]
    )
    
    # Academic information
    college = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    year_of_study = models.PositiveIntegerField(
        choices=[
            (1, 'First Year'),
            (2, 'Second Year'),
            (3, 'Third Year'),
            (4, 'Fourth Year'),
            (5, 'Fifth Year'),
            (6, 'Sixth Year'),
            (7, 'Postgraduate'),
        ],
        default=1
    )
    enrollment_date = models.DateField()
    expected_graduation = models.DateField(blank=True, null=True)
    current_semester = models.CharField(max_length=20, blank=True, null=True)
    
    # Personal information
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(
        max_length=10,
        choices=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other')
        ],
        blank=True,
        null=True
    )
    nationality = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    # Contact information
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True, null=True)
    emergency_contact_relationship = models.CharField(max_length=50, blank=True, null=True)
    
    # Academic performance
    current_gpa = models.FloatField(blank=True, null=True)
    academic_standing = models.CharField(
        max_length=20,
        choices=[
            ('excellent', 'Excellent'),
            ('good', 'Good'),
            ('satisfactory', 'Satisfactory'),
            ('probation', 'Academic Probation'),
        ],
        blank=True,
        null=True
    )
    
    # Mentorship
    mentor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mentored_students'
    )
    assigned_moze = models.ForeignKey(
        Moze,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_students'
    )
    
    # Status and verification
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    verification_document = models.FileField(upload_to='student_documents/', blank=True, null=True)
    
    # Additional information
    interests = models.TextField(blank=True, null=True, help_text='Academic and personal interests')
    skills = models.TextField(blank=True, null=True, help_text='Special skills or talents')
    goals = models.TextField(blank=True, null=True, help_text='Academic and career goals')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Student Profile'
        verbose_name_plural = 'Student Profiles'
        ordering = ['its_id']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.its_id} ({self.college})"
    
    def get_full_name(self):
        return self.user.get_full_name()
    
    def has_mentor(self):
        return self.mentor is not None
    
    def get_academic_year_display(self):
        return f"Year {self.year_of_study} - {self.specialization}"


class MentorshipRequest(models.Model):
    """Requests for mentorship from students"""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='mentorship_requests')
    requested_mentor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mentorship_requests_received',
        blank=True,
        null=True
    )
    
    # Request details
    reason = models.TextField(help_text='Why do you need mentorship?')
    areas_of_interest = models.TextField(help_text='Areas where you need guidance')
    preferred_meeting_frequency = models.CharField(
        max_length=20,
        choices=[
            ('weekly', 'Weekly'),
            ('bi_weekly', 'Bi-weekly'),
            ('monthly', 'Monthly'),
            ('as_needed', 'As Needed'),
        ],
        default='monthly'
    )
    
    # Status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('assigned', 'Mentor Assigned'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Assignment details
    assigned_mentor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_mentorship_requests'
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mentorship_assignments_made'
    )
    assigned_at = models.DateTimeField(null=True, blank=True)
    
    # Response and notes
    admin_notes = models.TextField(blank=True, null=True)
    mentor_response = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Mentorship Request'
        verbose_name_plural = 'Mentorship Requests'
    
    def __str__(self):
        return f"Mentorship request by {self.student.get_full_name()} - {self.get_status_display()}"


class AidRequest(models.Model):
    """Requests for financial or academic aid"""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='aid_requests')
    
    # Request type
    AID_TYPES = [
        ('financial', 'Financial Aid'),
        ('academic', 'Academic Support'),
        ('medical', 'Medical Assistance'),
        ('equipment', 'Equipment/Books'),
        ('transportation', 'Transportation'),
        ('accommodation', 'Accommodation'),
        ('emergency', 'Emergency Assistance'),
        ('other', 'Other'),
    ]
    aid_type = models.CharField(max_length=20, choices=AID_TYPES, default='financial')
    
    # Request details
    amount_requested = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='Amount in local currency (if applicable)'
    )
    reason = models.TextField(help_text='Detailed reason for the aid request')
    urgency_level = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('emergency', 'Emergency'),
        ],
        default='medium'
    )
    
    # Financial information (if applicable)
    family_income = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    number_of_dependents = models.PositiveIntegerField(blank=True, null=True)
    other_aid_received = models.TextField(blank=True, null=True, help_text='Other aid or scholarships received')
    
    # Supporting documents
    supporting_documents = models.FileField(upload_to='aid_documents/', blank=True, null=True)
    additional_documents = models.FileField(upload_to='aid_documents/', blank=True, null=True)
    
    # Status tracking
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('additional_info_required', 'Additional Information Required'),
        ('approved', 'Approved'),
        ('partially_approved', 'Partially Approved'),
        ('rejected', 'Rejected'),
        ('disbursed', 'Aid Disbursed'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='submitted')
    
    # Review and approval
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_aid_requests'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    approved_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    review_comments = models.TextField(blank=True, null=True)
    
    # Disbursement details
    disbursement_method = models.CharField(
        max_length=20,
        choices=[
            ('bank_transfer', 'Bank Transfer'),
            ('cash', 'Cash'),
            ('check', 'Check'),
            ('direct_payment', 'Direct Payment to Institution'),
            ('in_kind', 'In-Kind Assistance'),
        ],
        blank=True,
        null=True
    )
    disbursement_date = models.DateField(blank=True, null=True)
    disbursement_reference = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Aid Request'
        verbose_name_plural = 'Aid Requests'
    
    def __str__(self):
        return f"Aid request by {self.student.get_full_name()} - {self.get_aid_type_display()} - {self.get_status_display()}"
    
    def is_urgent(self):
        return self.urgency_level in ['high', 'emergency']


class StudentMeeting(models.Model):
    """Meeting records between students and mentors/counselors"""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='meetings')
    mentor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_meetings'
    )
    
    # Meeting details
    meeting_date = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=30)
    location = models.CharField(max_length=200, blank=True, null=True)
    meeting_type = models.CharField(
        max_length=20,
        choices=[
            ('in_person', 'In Person'),
            ('video_call', 'Video Call'),
            ('phone_call', 'Phone Call'),
            ('email', 'Email'),
        ],
        default='in_person'
    )
    
    # Meeting content
    agenda = models.TextField(blank=True, null=True)
    discussion_topics = models.TextField()
    outcomes = models.TextField(blank=True, null=True)
    action_items = models.TextField(blank=True, null=True)
    next_meeting_date = models.DateTimeField(blank=True, null=True)
    
    # Status
    is_completed = models.BooleanField(default=False)
    student_feedback = models.TextField(blank=True, null=True)
    mentor_notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-meeting_date']
        verbose_name = 'Student Meeting'
        verbose_name_plural = 'Student Meetings'
    
    def __str__(self):
        return f"Meeting: {self.student.get_full_name()} with {self.mentor.get_full_name()} on {self.meeting_date.date()}"


class StudentAchievement(models.Model):
    """Track student achievements and milestones"""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='achievements')
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    achievement_type = models.CharField(
        max_length=20,
        choices=[
            ('academic', 'Academic Achievement'),
            ('research', 'Research Achievement'),
            ('extracurricular', 'Extracurricular Activity'),
            ('volunteer', 'Volunteer Work'),
            ('leadership', 'Leadership Role'),
            ('competition', 'Competition/Contest'),
            ('certification', 'Certification'),
            ('other', 'Other'),
        ],
        default='academic'
    )
    
    date_achieved = models.DateField()
    institution_organization = models.CharField(max_length=200, blank=True, null=True)
    certificate_document = models.FileField(upload_to='achievement_certificates/', blank=True, null=True)
    
    # Verification
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_achievements'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_achieved']
        verbose_name = 'Student Achievement'
        verbose_name_plural = 'Student Achievements'
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.title}"
