from django.db import models
from django.conf import settings
import json


class Survey(models.Model):
    """Dynamic survey model with JSON-based questions"""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    TARGET_ROLE_CHOICES = [
        ('all', 'All Users'),
        ('aamil', 'Aamils'),
        ('moze_coordinator', 'Moze Coordinators'),
        ('doctor', 'Doctors'),
        ('student', 'Students'),
        ('badri_mahal_admin', 'Badri Mahal Admins'),
    ]
    target_role = models.CharField(max_length=20, choices=TARGET_ROLE_CHOICES, default='all')
    
    # JSON field to store survey questions
    questions = models.JSONField(
        default=list,
        help_text='List of questions in JSON format'
    )
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_surveys')
    
    # Survey settings
    is_active = models.BooleanField(default=True)
    is_anonymous = models.BooleanField(default=False)
    allow_multiple_responses = models.BooleanField(default=False)
    show_results = models.BooleanField(default=False, help_text='Show results to respondents')
    
    # Time settings
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Survey'
        verbose_name_plural = 'Surveys'
    
    def __str__(self):
        return self.title
    
    def get_questions_count(self):
        if isinstance(self.questions, list):
            return len(self.questions)
        return 0
    
    def get_responses_count(self):
        return self.responses.count()
    
    def is_available(self):
        from django.utils import timezone
        now = timezone.now()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return self.is_active
    
    def get_sample_questions_structure(self):
        """Returns sample structure for questions JSON"""
        return [
            {
                "id": 1,
                "type": "text",
                "question": "What is your name?",
                "required": True,
                "options": []
            },
            {
                "id": 2,
                "type": "multiple_choice",
                "question": "How satisfied are you with our services?",
                "required": True,
                "options": ["Very Satisfied", "Satisfied", "Neutral", "Dissatisfied", "Very Dissatisfied"]
            },
            {
                "id": 3,
                "type": "checkbox",
                "question": "Which services have you used?",
                "required": False,
                "options": ["Medical Consultation", "Health Screening", "Emergency Care", "Follow-up"]
            },
            {
                "id": 4,
                "type": "rating",
                "question": "Rate our service quality (1-5)",
                "required": True,
                "options": ["1", "2", "3", "4", "5"]
            }
        ]


class SurveyResponse(models.Model):
    """Individual survey response"""
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='responses')
    respondent = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='survey_responses',
        null=True,
        blank=True  # For anonymous surveys
    )
    
    # JSON field to store answers
    answers = models.JSONField(
        default=dict,
        help_text='Answers in JSON format matching question IDs'
    )
    
    # Response metadata
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    completion_time = models.PositiveIntegerField(blank=True, null=True, help_text='Time taken in seconds')
    
    is_complete = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['survey', 'respondent']  # Prevents duplicate responses if not allowed
        verbose_name = 'Survey Response'
        verbose_name_plural = 'Survey Responses'
    
    def __str__(self):
        respondent_name = self.respondent.get_full_name() if self.respondent else 'Anonymous'
        return f"Response to '{self.survey.title}' by {respondent_name}"
    
    def get_answer(self, question_id):
        """Get answer for a specific question ID"""
        return self.answers.get(str(question_id))
    
    def set_answer(self, question_id, answer):
        """Set answer for a specific question ID"""
        self.answers[str(question_id)] = answer
        self.save()


class SurveyReminder(models.Model):
    """Reminder system for survey responses"""
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='reminders')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Reminder settings
    reminder_count = models.PositiveIntegerField(default=0)
    max_reminders = models.PositiveIntegerField(default=3)
    last_reminder_sent = models.DateTimeField(blank=True, null=True)
    
    # Status
    has_responded = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['survey', 'user']
        verbose_name = 'Survey Reminder'
        verbose_name_plural = 'Survey Reminders'
    
    def __str__(self):
        return f"Reminder for {self.user.get_full_name()} - {self.survey.title}"
    
    def can_send_reminder(self):
        return (self.is_active and 
                not self.has_responded and 
                self.reminder_count < self.max_reminders)


class SurveyAnalytics(models.Model):
    """Analytics and statistics for surveys"""
    survey = models.OneToOneField(Survey, on_delete=models.CASCADE, related_name='analytics')
    
    total_invitations = models.PositiveIntegerField(default=0)
    total_responses = models.PositiveIntegerField(default=0)
    total_complete_responses = models.PositiveIntegerField(default=0)
    
    response_rate = models.FloatField(default=0.0, help_text='Response rate as percentage')
    completion_rate = models.FloatField(default=0.0, help_text='Completion rate as percentage')
    
    avg_completion_time = models.FloatField(default=0.0, help_text='Average completion time in seconds')
    
    # JSON field for detailed analytics
    detailed_analytics = models.JSONField(default=dict)
    
    last_calculated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Survey Analytics'
        verbose_name_plural = 'Survey Analytics'
    
    def __str__(self):
        return f"Analytics for {self.survey.title}"
    
    def calculate_rates(self):
        """Calculate response and completion rates"""
        if self.total_invitations > 0:
            self.response_rate = (self.total_responses / self.total_invitations) * 100
            self.completion_rate = (self.total_complete_responses / self.total_invitations) * 100
        self.save()
