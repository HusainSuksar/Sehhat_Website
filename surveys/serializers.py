"""
Serializers for the Survey app
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import Survey, SurveyResponse, SurveyReminder, SurveyAnalytics

User = get_user_model()


# Basic serializers for nested relationships
class UserBasicSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'full_name', 'role']
        read_only_fields = fields
    
    def get_full_name(self, obj):
        return obj.get_full_name()


# Survey Question Validation Serializer
class SurveyQuestionSerializer(serializers.Serializer):
    """Serializer for validating individual survey questions"""
    id = serializers.IntegerField(min_value=1)
    type = serializers.ChoiceField(choices=[
        ('text', 'Text Input'),
        ('textarea', 'Text Area'),
        ('multiple_choice', 'Multiple Choice'),
        ('checkbox', 'Multiple Select'),
        ('rating', 'Rating Scale'),
        ('date', 'Date'),
        ('email', 'Email'),
        ('number', 'Number'),
        ('boolean', 'Yes/No'),
        ('dropdown', 'Dropdown')
    ])
    question = serializers.CharField(max_length=500)
    required = serializers.BooleanField(default=False)
    options = serializers.ListField(
        child=serializers.CharField(max_length=200),
        required=False,
        allow_empty=True
    )
    placeholder = serializers.CharField(max_length=200, required=False, allow_blank=True)
    description = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    
    def validate(self, data):
        """Validate question structure based on type"""
        question_type = data.get('type')
        options = data.get('options', [])
        
        # Question types that require options
        if question_type in ['multiple_choice', 'checkbox', 'rating', 'dropdown']:
            if not options:
                raise serializers.ValidationError(
                    f"Question type '{question_type}' requires options."
                )
        
        # Rating questions should have numeric options or range
        if question_type == 'rating':
            if not all(opt.isdigit() for opt in options):
                raise serializers.ValidationError(
                    "Rating questions should have numeric options."
                )
        
        return data


# Survey Serializer
class SurveySerializer(serializers.ModelSerializer):
    created_by = UserBasicSerializer(read_only=True)
    created_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='created_by', required=False
    )
    questions = SurveyQuestionSerializer(many=True)
    
    # Computed fields
    target_role_display = serializers.SerializerMethodField()
    questions_count = serializers.SerializerMethodField()
    responses_count = serializers.SerializerMethodField()
    is_available = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    days_until_end = serializers.SerializerMethodField()
    days_since_start = serializers.SerializerMethodField()
    duration_days = serializers.SerializerMethodField()
    completion_rate = serializers.SerializerMethodField()
    user_has_responded = serializers.SerializerMethodField()
    can_respond = serializers.SerializerMethodField()
    
    class Meta:
        model = Survey
        fields = [
            'id', 'title', 'description', 'target_role', 'target_role_display',
            'questions', 'created_by', 'created_by_id', 'is_active', 'is_anonymous',
            'allow_multiple_responses', 'show_results', 'start_date', 'end_date',
            'questions_count', 'responses_count', 'is_available', 'is_expired',
            'days_until_end', 'days_since_start', 'duration_days', 'completion_rate',
            'user_has_responded', 'can_respond', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_target_role_display(self, obj):
        return obj.get_target_role_display()
    
    def get_questions_count(self, obj):
        return obj.get_questions_count()
    
    def get_responses_count(self, obj):
        return obj.get_responses_count()
    
    def get_is_available(self, obj):
        return obj.is_available()
    
    def get_is_expired(self, obj):
        if obj.end_date:
            return timezone.now() > obj.end_date
        return False
    
    def get_days_until_end(self, obj):
        if obj.end_date:
            delta = obj.end_date.date() - timezone.now().date()
            return delta.days if delta.days > 0 else 0
        return None
    
    def get_days_since_start(self, obj):
        if obj.start_date:
            delta = timezone.now().date() - obj.start_date.date()
            return delta.days if delta.days >= 0 else 0
        return None
    
    def get_duration_days(self, obj):
        if obj.start_date and obj.end_date:
            delta = obj.end_date.date() - obj.start_date.date()
            return delta.days + 1
        return None
    
    def get_completion_rate(self, obj):
        if hasattr(obj, 'analytics'):
            return obj.analytics.completion_rate
        return 0.0
    
    def get_user_has_responded(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.responses.filter(respondent=request.user).exists()
        return False
    
    def get_can_respond(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return obj.is_anonymous and obj.is_available()
        
        user = request.user
        
        # Check if survey is available
        if not obj.is_available():
            return False
        
        # Check role targeting
        if obj.target_role != 'all' and user.role != obj.target_role:
            return False
        
        # Check if user has already responded
        if not obj.allow_multiple_responses:
            has_responded = obj.responses.filter(respondent=user).exists()
            if has_responded:
                return False
        
        return True
    
    def validate_questions(self, questions):
        """Validate questions structure"""
        if not questions:
            raise serializers.ValidationError("Survey must have at least one question.")
        
        # Check for duplicate question IDs
        question_ids = [q['id'] for q in questions]
        if len(question_ids) != len(set(question_ids)):
            raise serializers.ValidationError("Question IDs must be unique.")
        
        return questions
    
    def validate(self, data):
        """Validate survey data"""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError("End date must be after start date.")
        
        return data


# Survey Create/Update Serializer (simplified)
class SurveyCreateSerializer(serializers.ModelSerializer):
    created_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='created_by', required=False
    )
    
    class Meta:
        model = Survey
        fields = [
            'title', 'description', 'target_role', 'questions', 'created_by_id',
            'is_active', 'is_anonymous', 'allow_multiple_responses', 'show_results',
            'start_date', 'end_date'
        ]
    
    def validate_questions(self, questions):
        """Validate questions structure"""
        if not questions:
            raise serializers.ValidationError("Survey must have at least one question.")
        
        # Validate each question using the question serializer
        for question in questions:
            question_serializer = SurveyQuestionSerializer(data=question)
            if not question_serializer.is_valid():
                raise serializers.ValidationError(
                    f"Invalid question: {question_serializer.errors}"
                )
        
        return questions
    
    def validate(self, data):
        """Validate survey data"""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError("End date must be after start date.")
        
        return data


# Survey Response Serializer
class SurveyResponseSerializer(serializers.ModelSerializer):
    survey = SurveySerializer(read_only=True)
    survey_id = serializers.PrimaryKeyRelatedField(
        queryset=Survey.objects.all(), write_only=True, source='survey'
    )
    respondent = UserBasicSerializer(read_only=True)
    respondent_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='respondent', required=False
    )
    
    # Computed fields
    response_percentage = serializers.SerializerMethodField()
    time_taken_formatted = serializers.SerializerMethodField()
    days_since_response = serializers.SerializerMethodField()
    answered_questions = serializers.SerializerMethodField()
    unanswered_questions = serializers.SerializerMethodField()
    
    class Meta:
        model = SurveyResponse
        fields = [
            'id', 'survey', 'survey_id', 'respondent', 'respondent_id', 'answers',
            'ip_address', 'user_agent', 'completion_time', 'is_complete',
            'response_percentage', 'time_taken_formatted', 'days_since_response',
            'answered_questions', 'unanswered_questions', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_response_percentage(self, obj):
        """Calculate percentage of questions answered"""
        total_questions = obj.survey.get_questions_count()
        if total_questions == 0:
            return 100.0
        
        answered_count = len([v for v in obj.answers.values() if v is not None and v != ''])
        return round((answered_count / total_questions) * 100, 2)
    
    def get_time_taken_formatted(self, obj):
        """Format completion time in human-readable format"""
        if not obj.completion_time:
            return None
        
        seconds = obj.completion_time
        if seconds < 60:
            return f"{seconds} seconds"
        elif seconds < 3600:
            minutes = seconds // 60
            remaining_seconds = seconds % 60
            return f"{minutes}m {remaining_seconds}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"
    
    def get_days_since_response(self, obj):
        return (timezone.now().date() - obj.created_at.date()).days
    
    def get_answered_questions(self, obj):
        """Get list of answered question IDs"""
        return [qid for qid, answer in obj.answers.items() if answer is not None and answer != '']
    
    def get_unanswered_questions(self, obj):
        """Get list of unanswered question IDs"""
        survey_question_ids = set(str(q['id']) for q in obj.survey.questions)
        answered_question_ids = set(str(qid) for qid, answer in obj.answers.items() if answer is not None and answer != '')
        return list(survey_question_ids - answered_question_ids)
    
    def validate_answers(self, answers):
        """Validate answers against survey questions"""
        if not answers:
            return answers
        
        survey_id = self.initial_data.get('survey_id') or self.initial_data.get('survey')
        survey = None
        if survey_id:
            try:
                survey = Survey.objects.get(id=survey_id)
            except Survey.DoesNotExist:
                raise serializers.ValidationError("Invalid survey.")
        elif self.instance:
            survey = self.instance.survey
        if not survey:
            return answers
        
        # Validate answers against survey questions
        valid_question_ids = {str(q['id']) for q in survey.questions}
        
        for question_id, answer in answers.items():
            if str(question_id) not in valid_question_ids:
                raise serializers.ValidationError(
                    f"Question ID {question_id} does not exist in this survey."
                )
        
        return answers


# Survey Response Create Serializer (simplified)
class SurveyResponseCreateSerializer(serializers.ModelSerializer):
    survey_id = serializers.PrimaryKeyRelatedField(
        queryset=Survey.objects.all(), source='survey'
    )
    respondent_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='respondent', required=False
    )
    
    class Meta:
        model = SurveyResponse
        fields = [
            'survey_id', 'respondent_id', 'answers', 'completion_time', 'is_complete'
        ]
    
    def validate(self, data):
        """Validate response data"""
        survey = data.get('survey')
        respondent = data.get('respondent')
        
        if not survey:
            raise serializers.ValidationError("Survey is required.")
        
        # Check if survey is available
        if not survey.is_available():
            raise serializers.ValidationError("This survey is not currently available.")
        
        # Check role targeting for authenticated users
        if respondent and survey.target_role != 'all' and respondent.role != survey.target_role:
            raise serializers.ValidationError("You are not authorized to respond to this survey.")
        
        # Check for existing response if multiple responses not allowed
        if not survey.allow_multiple_responses and respondent:
            existing_response = SurveyResponse.objects.filter(
                survey=survey, respondent=respondent
            ).exists()
            if existing_response:
                raise serializers.ValidationError("You have already responded to this survey.")
        
        return data
    
    def validate_answers(self, answers):
        """Validate answers against survey questions"""
        if not answers:
            return answers
        
        survey_id = self.initial_data.get('survey_id') or self.initial_data.get('survey')
        survey = None
        if survey_id:
            try:
                survey = Survey.objects.get(id=survey_id)
            except Survey.DoesNotExist:
                raise serializers.ValidationError("Invalid survey.")
        elif self.instance:
            survey = self.instance.survey
        
        if not survey:
            return answers
        
        # Validate answers against survey questions
        valid_question_ids = {str(q['id']) for q in survey.questions}
        
        for question_id, answer in answers.items():
            if str(question_id) not in valid_question_ids:
                raise serializers.ValidationError(
                    f"Question ID {question_id} does not exist in this survey."
                )
        
        return answers


# Survey Reminder Serializer
class SurveyReminderSerializer(serializers.ModelSerializer):
    survey = SurveySerializer(read_only=True)
    survey_id = serializers.PrimaryKeyRelatedField(
        queryset=Survey.objects.all(), write_only=True, source='survey'
    )
    user = UserBasicSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='user'
    )
    
    # Computed fields
    can_send_reminder = serializers.SerializerMethodField()
    days_since_last_reminder = serializers.SerializerMethodField()
    reminders_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = SurveyReminder
        fields = [
            'id', 'survey', 'survey_id', 'user', 'user_id', 'reminder_count',
            'max_reminders', 'last_reminder_sent', 'has_responded', 'is_active',
            'can_send_reminder', 'days_since_last_reminder', 'reminders_remaining',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_can_send_reminder(self, obj):
        return obj.can_send_reminder()
    
    def get_days_since_last_reminder(self, obj):
        if obj.last_reminder_sent:
            return (timezone.now().date() - obj.last_reminder_sent.date()).days
        return None
    
    def get_reminders_remaining(self, obj):
        return max(0, obj.max_reminders - obj.reminder_count)


# Survey Analytics Serializer
class SurveyAnalyticsSerializer(serializers.ModelSerializer):
    survey = SurveySerializer(read_only=True)
    survey_id = serializers.PrimaryKeyRelatedField(
        queryset=Survey.objects.all(), write_only=True, source='survey'
    )
    
    # Computed fields
    average_completion_time_formatted = serializers.SerializerMethodField()
    response_trend = serializers.SerializerMethodField()
    completion_trend = serializers.SerializerMethodField()
    days_since_last_calculation = serializers.SerializerMethodField()
    
    class Meta:
        model = SurveyAnalytics
        fields = [
            'id', 'survey', 'survey_id', 'total_invitations', 'total_responses',
            'total_complete_responses', 'response_rate', 'completion_rate',
            'avg_completion_time', 'average_completion_time_formatted',
            'detailed_analytics', 'response_trend', 'completion_trend',
            'days_since_last_calculation', 'last_calculated'
        ]
        read_only_fields = ['last_calculated']
    
    def get_average_completion_time_formatted(self, obj):
        """Format average completion time in human-readable format"""
        if not obj.avg_completion_time:
            return None
        
        seconds = int(obj.avg_completion_time)
        if seconds < 60:
            return f"{seconds} seconds"
        elif seconds < 3600:
            minutes = seconds // 60
            remaining_seconds = seconds % 60
            return f"{minutes}m {remaining_seconds}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"
    
    def get_response_trend(self, obj):
        """Calculate response rate trend"""
        if obj.total_invitations > 0:
            if obj.response_rate >= 75:
                return "excellent"
            elif obj.response_rate >= 50:
                return "good"
            elif obj.response_rate >= 25:
                return "fair"
            else:
                return "poor"
        return "no_data"
    
    def get_completion_trend(self, obj):
        """Calculate completion rate trend"""
        if obj.total_responses > 0:
            completion_percentage = (obj.total_complete_responses / obj.total_responses) * 100
            if completion_percentage >= 90:
                return "excellent"
            elif completion_percentage >= 75:
                return "good"
            elif completion_percentage >= 50:
                return "fair"
            else:
                return "poor"
        return "no_data"
    
    def get_days_since_last_calculation(self, obj):
        return (timezone.now().date() - obj.last_calculated.date()).days


# Statistics Serializers
class SurveyStatsSerializer(serializers.Serializer):
    total_surveys = serializers.IntegerField()
    active_surveys = serializers.IntegerField()
    total_responses = serializers.IntegerField()
    total_complete_responses = serializers.IntegerField()
    average_response_rate = serializers.FloatField()
    average_completion_rate = serializers.FloatField()
    surveys_by_role = serializers.DictField()
    surveys_by_status = serializers.DictField()
    recent_surveys = serializers.ListField()
    top_performing_surveys = serializers.ListField()


class ResponseStatsSerializer(serializers.Serializer):
    total_responses = serializers.IntegerField()
    complete_responses = serializers.IntegerField()
    partial_responses = serializers.IntegerField()
    anonymous_responses = serializers.IntegerField()
    responses_by_role = serializers.DictField()
    responses_by_survey = serializers.DictField()
    average_completion_time = serializers.FloatField()
    response_trend = serializers.ListField()


# Survey Question Analysis Serializer
class QuestionAnalysisSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    question_text = serializers.CharField()
    question_type = serializers.CharField()
    total_responses = serializers.IntegerField()
    response_rate = serializers.FloatField()
    answer_distribution = serializers.DictField()
    most_common_answer = serializers.CharField(allow_null=True)
    average_rating = serializers.FloatField(allow_null=True)


# Survey Search Serializer
class SurveySearchSerializer(serializers.Serializer):
    title = serializers.CharField(required=False)
    target_role = serializers.CharField(required=False)
    created_by = serializers.CharField(required=False)
    is_active = serializers.BooleanField(required=False)
    is_anonymous = serializers.BooleanField(required=False)
    start_date_from = serializers.DateTimeField(required=False)
    start_date_to = serializers.DateTimeField(required=False)
    end_date_from = serializers.DateTimeField(required=False)
    end_date_to = serializers.DateTimeField(required=False)
    has_responses = serializers.BooleanField(required=False)