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


class Evaluation(models.Model):
    """Moze evaluation with grades A-E"""
    moze = models.ForeignKey(Moze, on_delete=models.CASCADE, related_name='evaluations')
    evaluator = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='conducted_evaluations'
    )
    
    # Evaluation period
    evaluation_period_start = models.DateField()
    evaluation_period_end = models.DateField()
    
    # Score details stored as JSON
    score_details = models.JSONField(
        default=dict,
        help_text='Detailed scores for each criteria in JSON format'
    )
    
    # Overall scores
    total_score = models.FloatField(default=0.0)
    max_possible_score = models.FloatField(default=0.0)
    percentage_score = models.FloatField(default=0.0)
    
    # Grade calculation
    GRADE_CHOICES = [
        ('A', 'A - Excellent (90-100%)'),
        ('B', 'B - Good (80-89%)'),
        ('C', 'C - Satisfactory (70-79%)'),
        ('D', 'D - Needs Improvement (60-69%)'),
        ('E', 'E - Poor (Below 60%)'),
    ]
    grade = models.CharField(max_length=1, choices=GRADE_CHOICES, blank=True)
    
    # Evaluation status
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('reviewed', 'Reviewed'),
        ('published', 'Published'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Comments and recommendations
    overall_comments = models.TextField(blank=True, null=True)
    recommendations = models.TextField(blank=True, null=True)
    action_items = models.TextField(blank=True, null=True)
    
    # Evaluation metadata
    evaluation_date = models.DateField(auto_now_add=True)
    is_published = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-evaluation_date']
        unique_together = ['moze', 'evaluation_period_start', 'evaluation_period_end']
        verbose_name = 'Evaluation'
        verbose_name_plural = 'Evaluations'
    
    def __str__(self):
        return f"Evaluation of {self.moze.name} - {self.evaluation_date} (Grade: {self.grade})"
    
    def calculate_grade(self):
        """Calculate grade based on percentage score"""
        if self.percentage_score >= 90:
            self.grade = 'A'
        elif self.percentage_score >= 80:
            self.grade = 'B'
        elif self.percentage_score >= 70:
            self.grade = 'C'
        elif self.percentage_score >= 60:
            self.grade = 'D'
        else:
            self.grade = 'E'
        self.save()
    
    def calculate_scores(self):
        """Calculate total and percentage scores from score_details"""
        total = 0.0
        max_possible = 0.0
        
        criteria = EvaluationCriteria.objects.filter(is_active=True)
        for criterion in criteria:
            score = self.score_details.get(str(criterion.id), {}).get('score', 0)
            weighted_score = score * criterion.weight
            max_weighted_score = criterion.max_score * criterion.weight
            
            total += weighted_score
            max_possible += max_weighted_score
        
        self.total_score = total
        self.max_possible_score = max_possible
        self.percentage_score = (total / max_possible * 100) if max_possible > 0 else 0
        
        self.calculate_grade()
    
    def get_criteria_score(self, criteria_id):
        """Get score for specific criteria"""
        return self.score_details.get(str(criteria_id), {})
    
    def set_criteria_score(self, criteria_id, score, comments=''):
        """Set score for specific criteria"""
        if str(criteria_id) not in self.score_details:
            self.score_details[str(criteria_id)] = {}
        
        self.score_details[str(criteria_id)]['score'] = score
        self.score_details[str(criteria_id)]['comments'] = comments
        self.save()


class EvaluationTemplate(models.Model):
    """Template for evaluations with predefined criteria"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    criteria = models.ManyToManyField(EvaluationCriteria, related_name='templates')
    
    # Template settings
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Evaluation Template'
        verbose_name_plural = 'Evaluation Templates'
    
    def __str__(self):
        return self.name
    
    def get_criteria_count(self):
        return self.criteria.count()


class EvaluationReport(models.Model):
    """Generated reports from evaluations"""
    evaluation = models.OneToOneField(Evaluation, on_delete=models.CASCADE, related_name='report')
    
    # Report data
    report_data = models.JSONField(default=dict, help_text='Compiled report data in JSON format')
    
    # Report files
    pdf_report = models.FileField(upload_to='evaluation_reports/', blank=True, null=True)
    excel_report = models.FileField(upload_to='evaluation_reports/', blank=True, null=True)
    
    # Report metadata
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Evaluation Report'
        verbose_name_plural = 'Evaluation Reports'
    
    def __str__(self):
        return f"Report for {self.evaluation}"


class EvaluationHistory(models.Model):
    """Track changes and history of evaluations"""
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE, related_name='history')
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Change details
    field_name = models.CharField(max_length=100)
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    change_reason = models.CharField(max_length=200, blank=True, null=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Evaluation History'
        verbose_name_plural = 'Evaluation Histories'
    
    def __str__(self):
        return f"Change in {self.field_name} for {self.evaluation} by {self.changed_by}"
