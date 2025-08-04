from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from moze.models import Moze


class EvaluationCriteria(models.Model):
    """Criteria and questions for Moze evaluation"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    weight = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0.1), MaxValueValidator(10.0)],
        help_text='Weight/importance of this criteria (0.1 to 10.0)'
    )
    max_score = models.PositiveIntegerField(default=10, help_text='Maximum score for this criteria')
    
    # Question type and options
    QUESTION_TYPE_CHOICES = [
        ('dropdown', 'Dropdown'),
        ('multiple_choice', 'Multiple Choice'),
        ('rating', 'Rating Scale'),
        ('text', 'Text Input'),
        ('boolean', 'Yes/No'),
    ]
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, default='rating')
    is_required = models.BooleanField(default=True)
    
    # Category for grouping criteria
    CATEGORY_CHOICES = [
        ('infrastructure', 'Infrastructure & Facilities'),
        ('medical_quality', 'Medical Care Quality'),
        ('staff_performance', 'Staff Performance'),
        ('patient_satisfaction', 'Patient Satisfaction'),
        ('administration', 'Administration & Management'),
        ('safety', 'Safety & Hygiene'),
        ('equipment', 'Medical Equipment'),
        ('accessibility', 'Accessibility & Availability'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='medical_quality')
    
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text='Display order')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'order', 'name']
        verbose_name = 'Evaluation Criteria'
        verbose_name_plural = 'Evaluation Criteria'
    
    def __str__(self):
        return f"{self.name} (Weight: {self.weight})"
    
    def get_answer_options(self):
        """Get answer options for this criteria"""
        return self.answer_options.filter(is_active=True).order_by('order')


class EvaluationAnswerOption(models.Model):
    """Answer options for evaluation criteria with weights"""
    criteria = models.ForeignKey(EvaluationCriteria, on_delete=models.CASCADE, related_name='answer_options')
    option_text = models.CharField(max_length=200, help_text='Answer option text')
    weight = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        help_text='Score weight for this option (e.g., Option A = 5 pts, B = 3 pts)'
    )
    order = models.PositiveIntegerField(default=0, help_text='Display order')
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['criteria', 'order']
        unique_together = ['criteria', 'option_text']
        verbose_name = 'Evaluation Answer Option'
        verbose_name_plural = 'Evaluation Answer Options'
    
    def __str__(self):
        return f"{self.criteria.name} - {self.option_text} (Weight: {self.weight})"


# New models for views compatibility
class EvaluationForm(models.Model):
    """Evaluation form template"""
    EVALUATION_TYPE_CHOICES = [
        ('performance', 'Performance Evaluation'),
        ('satisfaction', 'Satisfaction Survey'),
        ('quality', 'Quality Assessment'),
        ('training', 'Training Evaluation'),
        ('service', 'Service Evaluation'),
        ('facility', 'Facility Evaluation'),
    ]
    
    TARGET_ROLE_CHOICES = [
        ('all', 'All Users'),
        ('doctor', 'Doctors'),
        ('student', 'Students'),
        ('aamil', 'Aamils'),
        ('moze_coordinator', 'Moze Coordinators'),
        ('admin', 'Administrators'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    evaluation_type = models.CharField(max_length=20, choices=EVALUATION_TYPE_CHOICES)
    target_role = models.CharField(max_length=20, choices=TARGET_ROLE_CHOICES, default='all')
    
    is_active = models.BooleanField(default=True)
    is_anonymous = models.BooleanField(default=False)
    due_date = models.DateTimeField(null=True, blank=True)
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class EvaluationSubmission(models.Model):
    """User's submission of an evaluation form"""
    form = models.ForeignKey(EvaluationForm, on_delete=models.CASCADE, related_name='submissions')
    evaluator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Evaluation target (could be a user, moze, or other entity)
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='received_evaluations',
        null=True, 
        blank=True
    )
    target_moze = models.ForeignKey(
        Moze, 
        on_delete=models.CASCADE, 
        related_name='evaluations_received',
        null=True, 
        blank=True
    )
    
    total_score = models.FloatField(default=0)
    comments = models.TextField(blank=True)
    is_complete = models.BooleanField(default=False)
    
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['form', 'evaluator']
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.form.title} by {self.evaluator.get_full_name()}"


class EvaluationResponse(models.Model):
    """Individual responses to evaluation criteria"""
    submission = models.ForeignKey(EvaluationSubmission, on_delete=models.CASCADE, related_name='responses')
    criteria = models.ForeignKey(EvaluationCriteria, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    comment = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['submission', 'criteria']
    
    def __str__(self):
        return f"{self.criteria.name}: {self.score}"


class EvaluationSession(models.Model):
    """Evaluation session for group evaluations"""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    form = models.ForeignKey(EvaluationForm, on_delete=models.CASCADE, related_name='sessions')
    
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class CriteriaRating(models.Model):
    """Individual rating for a criteria within an evaluation"""
    evaluation = models.ForeignKey('Evaluation', on_delete=models.CASCADE, related_name='ratings')
    criteria = models.ForeignKey(EvaluationCriteria, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    comment = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['evaluation', 'criteria']
    
    def __str__(self):
        return f"{self.criteria.name}: {self.score}/10"


class Evaluation(models.Model):
    """Moze evaluation with grades A-E"""
    moze = models.ForeignKey(Moze, on_delete=models.CASCADE, related_name='evaluations')
    evaluator = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='conducted_evaluations'
    )
    
    # Evaluation period
    evaluation_period = models.CharField(
        max_length=20,
        choices=[
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
            ('biannual', 'Bi-annual'),
            ('annual', 'Annual'),
            ('special', 'Special Assessment'),
        ],
        default='quarterly'
    )
    
    # Overall assessment
    overall_grade = models.CharField(
        max_length=2,
        choices=[
            ('A+', 'A+ (Excellent - 95-100%)'),
            ('A', 'A (Very Good - 85-94%)'),
            ('B', 'B (Good - 75-84%)'),
            ('C', 'C (Satisfactory - 65-74%)'),
            ('D', 'D (Needs Improvement - 55-64%)'),
            ('E', 'E (Unsatisfactory - Below 55%)'),
        ],
        blank=True,
        null=True
    )
    
    overall_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text='Overall score as percentage (0-100)'
    )
    
    # Detailed scores by category
    infrastructure_score = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    medical_quality_score = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    staff_performance_score = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    patient_satisfaction_score = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    administration_score = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    safety_score = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    equipment_score = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    accessibility_score = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    
    # Qualitative feedback
    strengths = models.TextField(blank=True, null=True, help_text='Key strengths observed')
    weaknesses = models.TextField(blank=True, null=True, help_text='Areas needing improvement')
    recommendations = models.TextField(blank=True, null=True, help_text='Specific recommendations')
    action_items = models.TextField(blank=True, null=True, help_text='Action items for improvement')
    
    # Additional assessment fields
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(blank=True, null=True)
    compliance_issues = models.TextField(blank=True, null=True)
    certification_status = models.CharField(
        max_length=20,
        choices=[
            ('certified', 'Certified'),
            ('provisional', 'Provisional'),
            ('warning', 'Warning Status'),
            ('suspended', 'Suspended'),
            ('revoked', 'Revoked'),
        ],
        default='certified'
    )
    
    # Evaluation metadata
    evaluation_date = models.DateField()
    evaluation_duration_hours = models.PositiveIntegerField(default=1, help_text='Duration in hours')
    
    # Status tracking
    is_draft = models.BooleanField(default=True)
    is_published = models.BooleanField(default=False)
    is_confidential = models.BooleanField(default=False)
    
    # Review and approval
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_evaluations'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewer_notes = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-evaluation_date', '-created_at']
        unique_together = ['moze', 'evaluation_period', 'evaluation_date']
    
    def __str__(self):
        return f"{self.moze.name} - {self.evaluation_period} ({self.overall_grade or 'Ungraded'})"
    
    def calculate_overall_score(self):
        """Calculate overall score based on weighted category scores"""
        scores = [
            self.infrastructure_score,
            self.medical_quality_score * 1.5,  # Higher weight for medical quality
            self.staff_performance_score * 1.2,
            self.patient_satisfaction_score * 1.3,
            self.administration_score,
            self.safety_score * 1.4,  # Higher weight for safety
            self.equipment_score,
            self.accessibility_score,
        ]
        weights = [1.0, 1.5, 1.2, 1.3, 1.0, 1.4, 1.0, 1.0]
        
        weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
        total_weight = sum(weights)
        
        if total_weight > 0:
            self.overall_score = weighted_sum / total_weight
        else:
            self.overall_score = 0.0
        
        # Assign grade based on score
        if self.overall_score >= 95:
            self.overall_grade = 'A+'
        elif self.overall_score >= 85:
            self.overall_grade = 'A'
        elif self.overall_score >= 75:
            self.overall_grade = 'B'
        elif self.overall_score >= 65:
            self.overall_grade = 'C'
        elif self.overall_score >= 55:
            self.overall_grade = 'D'
        else:
            self.overall_grade = 'E'
    
    def save(self, *args, **kwargs):
        if not self.is_draft:
            self.calculate_overall_score()
        super().save(*args, **kwargs)
    
    def get_category_breakdown(self):
        """Return category scores as a dictionary"""
        return {
            'Infrastructure': self.infrastructure_score,
            'Medical Quality': self.medical_quality_score,
            'Staff Performance': self.staff_performance_score,
            'Patient Satisfaction': self.patient_satisfaction_score,
            'Administration': self.administration_score,
            'Safety': self.safety_score,
            'Equipment': self.equipment_score,
            'Accessibility': self.accessibility_score,
        }
    
    def is_passing_grade(self):
        """Check if the evaluation has a passing grade"""
        return self.overall_grade in ['A+', 'A', 'B', 'C']
    
    def needs_immediate_attention(self):
        """Check if the evaluation indicates need for immediate attention"""
        return self.overall_grade in ['D', 'E'] or self.safety_score < 60


class EvaluationTemplate(models.Model):
    """Templates for different types of evaluations"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    evaluation_type = models.CharField(
        max_length=20,
        choices=[
            ('standard', 'Standard Assessment'),
            ('detailed', 'Detailed Assessment'),
            ('quick', 'Quick Assessment'),
            ('compliance', 'Compliance Check'),
            ('emergency', 'Emergency Assessment'),
        ],
        default='standard'
    )
    
    # Template configuration
    criteria = models.ManyToManyField(EvaluationCriteria, through='TemplateCriteria')
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.evaluation_type})"


class TemplateCriteria(models.Model):
    """Through model for EvaluationTemplate and EvaluationCriteria"""
    template = models.ForeignKey(EvaluationTemplate, on_delete=models.CASCADE)
    criteria = models.ForeignKey(EvaluationCriteria, on_delete=models.CASCADE)
    is_required = models.BooleanField(default=True)
    custom_weight = models.FloatField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        unique_together = ['template', 'criteria']


class EvaluationReport(models.Model):
    """Generated reports from evaluations"""
    title = models.CharField(max_length=200)
    report_type = models.CharField(
        max_length=20,
        choices=[
            ('individual', 'Individual Moze Report'),
            ('comparative', 'Comparative Report'),
            ('trend', 'Trend Analysis'),
            ('summary', 'Summary Report'),
            ('detailed', 'Detailed Analysis'),
        ]
    )
    
    # Report scope
    mozes = models.ManyToManyField(Moze, blank=True)
    evaluation_period_start = models.DateField()
    evaluation_period_end = models.DateField()
    
    # Report content
    report_data = models.JSONField(default=dict)  # Store chart data, statistics, etc.
    summary = models.TextField()
    recommendations = models.TextField(blank=True)
    
    # Report metadata
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    generated_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.title} ({self.report_type})"


class EvaluationHistory(models.Model):
    """Track changes to evaluations"""
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE, related_name='history')
    field_name = models.CharField(max_length=50)
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    changed_at = models.DateTimeField(auto_now_add=True)
    change_reason = models.CharField(max_length=200, blank=True)
    
    class Meta:
        ordering = ['-changed_at']
        verbose_name_plural = 'Evaluation Histories'
    
    def __str__(self):
        return f"{self.evaluation} - {self.field_name} changed"