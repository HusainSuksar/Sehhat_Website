"""
Serializers for the Evaluation app
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import (
    EvaluationCriteria, EvaluationAnswerOption, EvaluationForm, EvaluationSubmission,
    EvaluationResponse, EvaluationSession, CriteriaRating, Evaluation,
    EvaluationTemplate, TemplateCriteria, EvaluationReport, EvaluationHistory
)
from moze.models import Moze

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


class MozeBasicSerializer(serializers.ModelSerializer):
    aamil_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Moze
        fields = ['id', 'name', 'location', 'aamil_name', 'is_active']
        read_only_fields = fields
    
    def get_aamil_name(self, obj):
        return obj.aamil.get_full_name() if obj.aamil else None


# Evaluation Answer Option Serializer
class EvaluationAnswerOptionSerializer(serializers.ModelSerializer):
    criteria_name = serializers.SerializerMethodField()
    
    class Meta:
        model = EvaluationAnswerOption
        fields = [
            'id', 'criteria', 'criteria_name', 'option_text', 'weight', 'order', 
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_criteria_name(self, obj):
        return obj.criteria.name


# Evaluation Criteria Serializer
class EvaluationCriteriaSerializer(serializers.ModelSerializer):
    answer_options = EvaluationAnswerOptionSerializer(many=True, read_only=True)
    category_display = serializers.SerializerMethodField()
    question_type_display = serializers.SerializerMethodField()
    score_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = EvaluationCriteria
        fields = [
            'id', 'name', 'description', 'weight', 'max_score', 'question_type', 
            'question_type_display', 'is_required', 'category', 'category_display',
            'is_active', 'order', 'answer_options', 'score_percentage',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_category_display(self, obj):
        return obj.get_category_display()
    
    def get_question_type_display(self, obj):
        return obj.get_question_type_display()
    
    def get_score_percentage(self, obj):
        """Calculate the percentage weight of this criteria"""
        # This would typically be calculated based on all criteria in a template/form
        return round((obj.weight / 10.0) * 100, 2)


# Evaluation Response Serializer
class EvaluationResponseSerializer(serializers.ModelSerializer):
    criteria = EvaluationCriteriaSerializer(read_only=True)
    criteria_id = serializers.PrimaryKeyRelatedField(
        queryset=EvaluationCriteria.objects.all(), write_only=True, source='criteria'
    )
    score_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = EvaluationResponse
        fields = [
            'id', 'criteria', 'criteria_id', 'score', 'score_percentage', 
            'comment', 'created_at'
        ]
        read_only_fields = ['created_at']
    
    def get_score_percentage(self, obj):
        if obj.criteria.max_score > 0:
            return round((obj.score / obj.criteria.max_score) * 100, 2)
        return 0


# Evaluation Submission Serializer
class EvaluationSubmissionSerializer(serializers.ModelSerializer):
    evaluator = UserBasicSerializer(read_only=True)
    evaluator_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='evaluator', required=False
    )
    target_user = UserBasicSerializer(read_only=True)
    target_user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='target_user', required=False
    )
    target_moze = MozeBasicSerializer(read_only=True)
    target_moze_id = serializers.PrimaryKeyRelatedField(
        queryset=Moze.objects.all(), write_only=True, source='target_moze', required=False
    )
    responses = EvaluationResponseSerializer(many=True, read_only=True)
    response_count = serializers.SerializerMethodField()
    completion_percentage = serializers.SerializerMethodField()
    average_score = serializers.SerializerMethodField()
    days_since_submission = serializers.SerializerMethodField()
    
    class Meta:
        model = EvaluationSubmission
        fields = [
            'id', 'form', 'evaluator', 'evaluator_id', 'target_user', 'target_user_id',
            'target_moze', 'target_moze_id', 'total_score', 'comments', 'is_complete',
            'responses', 'response_count', 'completion_percentage', 'average_score',
            'days_since_submission', 'submitted_at', 'updated_at'
        ]
        read_only_fields = ['submitted_at', 'updated_at']
    
    def get_response_count(self, obj):
        return obj.responses.count()
    
    def get_completion_percentage(self, obj):
        # This would need to be calculated based on required criteria in the form
        total_criteria = obj.form.criteria.filter(is_active=True).count() if hasattr(obj.form, 'criteria') else 0
        completed_responses = obj.responses.count()
        if total_criteria > 0:
            return round((completed_responses / total_criteria) * 100, 2)
        return 0
    
    def get_average_score(self, obj):
        responses = obj.responses.all()
        if responses:
            return round(sum(r.score for r in responses) / len(responses), 2)
        return 0
    
    def get_days_since_submission(self, obj):
        return (timezone.now().date() - obj.submitted_at.date()).days


# Evaluation Form Serializer
class EvaluationFormSerializer(serializers.ModelSerializer):
    created_by = UserBasicSerializer(read_only=True)
    created_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='created_by', required=False
    )
    submissions = EvaluationSubmissionSerializer(many=True, read_only=True)
    evaluation_type_display = serializers.SerializerMethodField()
    target_role_display = serializers.SerializerMethodField()
    submission_count = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    days_until_due = serializers.SerializerMethodField()
    
    class Meta:
        model = EvaluationForm
        fields = [
            'id', 'title', 'description', 'evaluation_type', 'evaluation_type_display',
            'target_role', 'target_role_display', 'is_active', 'is_anonymous', 'due_date',
            'created_by', 'created_by_id', 'submissions', 'submission_count', 
            'is_overdue', 'days_until_due', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_evaluation_type_display(self, obj):
        return obj.get_evaluation_type_display()
    
    def get_target_role_display(self, obj):
        return obj.get_target_role_display()
    
    def get_submission_count(self, obj):
        return obj.submissions.count()
    
    def get_is_overdue(self, obj):
        if obj.due_date:
            return timezone.now() > obj.due_date
        return False
    
    def get_days_until_due(self, obj):
        if obj.due_date:
            delta = obj.due_date.date() - timezone.now().date()
            return delta.days
        return None


# Evaluation Session Serializer
class EvaluationSessionSerializer(serializers.ModelSerializer):
    form = EvaluationFormSerializer(read_only=True)
    form_id = serializers.PrimaryKeyRelatedField(
        queryset=EvaluationForm.objects.all(), write_only=True, source='form'
    )
    created_by = UserBasicSerializer(read_only=True)
    created_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='created_by', required=False
    )
    is_ongoing = serializers.SerializerMethodField()
    days_until_start = serializers.SerializerMethodField()
    duration_days = serializers.SerializerMethodField()
    
    class Meta:
        model = EvaluationSession
        fields = [
            'id', 'title', 'description', 'form', 'form_id', 'start_date', 'end_date',
            'is_active', 'created_by', 'created_by_id', 'is_ongoing', 'days_until_start',
            'duration_days', 'created_at'
        ]
        read_only_fields = ['created_at']
    
    def get_is_ongoing(self, obj):
        now = timezone.now()
        return obj.start_date <= now <= obj.end_date
    
    def get_days_until_start(self, obj):
        if obj.start_date > timezone.now():
            delta = obj.start_date.date() - timezone.now().date()
            return delta.days
        return 0
    
    def get_duration_days(self, obj):
        delta = obj.end_date.date() - obj.start_date.date()
        return delta.days + 1


# Criteria Rating Serializer
class CriteriaRatingSerializer(serializers.ModelSerializer):
    criteria = EvaluationCriteriaSerializer(read_only=True)
    criteria_id = serializers.PrimaryKeyRelatedField(
        queryset=EvaluationCriteria.objects.all(), write_only=True, source='criteria'
    )
    score_percentage = serializers.SerializerMethodField()
    weighted_score = serializers.SerializerMethodField()
    
    class Meta:
        model = CriteriaRating
        fields = [
            'id', 'criteria', 'criteria_id', 'score', 'score_percentage', 
            'weighted_score', 'comment'
        ]
    
    def get_score_percentage(self, obj):
        return round((obj.score / 10) * 100, 2)
    
    def get_weighted_score(self, obj):
        return round(obj.score * obj.criteria.weight, 2)


# Main Evaluation Serializer
class EvaluationSerializer(serializers.ModelSerializer):
    moze = MozeBasicSerializer(read_only=True)
    moze_id = serializers.PrimaryKeyRelatedField(
        queryset=Moze.objects.all(), write_only=True, source='moze'
    )
    evaluator = UserBasicSerializer(read_only=True)
    evaluator_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='evaluator', required=False
    )
    reviewed_by = UserBasicSerializer(read_only=True)
    reviewed_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='reviewed_by', required=False
    )
    ratings = CriteriaRatingSerializer(many=True, read_only=True)
    
    # Computed fields
    evaluation_period_display = serializers.SerializerMethodField()
    overall_grade_display = serializers.SerializerMethodField()
    certification_status_display = serializers.SerializerMethodField()
    category_breakdown = serializers.SerializerMethodField()
    is_passing = serializers.SerializerMethodField()
    needs_attention = serializers.SerializerMethodField()
    days_since_evaluation = serializers.SerializerMethodField()
    is_reviewed = serializers.SerializerMethodField()
    
    class Meta:
        model = Evaluation
        fields = [
            'id', 'moze', 'moze_id', 'evaluator', 'evaluator_id', 'evaluation_period',
            'evaluation_period_display', 'overall_grade', 'overall_grade_display',
            'overall_score', 'infrastructure_score', 'medical_quality_score',
            'staff_performance_score', 'patient_satisfaction_score', 'administration_score',
            'safety_score', 'equipment_score', 'accessibility_score', 'strengths',
            'weaknesses', 'recommendations', 'action_items', 'follow_up_required',
            'follow_up_date', 'compliance_issues', 'certification_status',
            'certification_status_display', 'evaluation_date', 'evaluation_duration_hours',
            'is_draft', 'is_published', 'is_confidential', 'reviewed_by', 'reviewed_by_id',
            'reviewed_at', 'reviewer_notes', 'ratings', 'category_breakdown',
            'is_passing', 'needs_attention', 'days_since_evaluation', 'is_reviewed',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['overall_score', 'overall_grade', 'created_at', 'updated_at']
    
    def get_evaluation_period_display(self, obj):
        return obj.get_evaluation_period_display()
    
    def get_overall_grade_display(self, obj):
        return obj.get_overall_grade_display() if obj.overall_grade else None
    
    def get_certification_status_display(self, obj):
        return obj.get_certification_status_display()
    
    def get_category_breakdown(self, obj):
        return obj.get_category_breakdown()
    
    def get_is_passing(self, obj):
        return obj.is_passing_grade()
    
    def get_needs_attention(self, obj):
        return obj.needs_immediate_attention()
    
    def get_days_since_evaluation(self, obj):
        return (timezone.now().date() - obj.evaluation_date).days
    
    def get_is_reviewed(self, obj):
        return obj.reviewed_by is not None and obj.reviewed_at is not None


# Evaluation Create Serializer (simplified for creation)
class EvaluationCreateSerializer(serializers.ModelSerializer):
    moze_id = serializers.PrimaryKeyRelatedField(
        queryset=Moze.objects.all(), source='moze'
    )
    evaluator_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='evaluator', required=False
    )
    
    class Meta:
        model = Evaluation
        fields = [
            'moze_id', 'evaluator_id', 'evaluation_period', 'infrastructure_score',
            'medical_quality_score', 'staff_performance_score', 'patient_satisfaction_score',
            'administration_score', 'safety_score', 'equipment_score', 'accessibility_score',
            'strengths', 'weaknesses', 'recommendations', 'action_items',
            'follow_up_required', 'follow_up_date', 'compliance_issues',
            'certification_status', 'evaluation_date', 'evaluation_duration_hours',
            'is_draft', 'is_published', 'is_confidential'
        ]


# Template Criteria Serializer
class TemplateCriteriaSerializer(serializers.ModelSerializer):
    criteria = EvaluationCriteriaSerializer(read_only=True)
    criteria_id = serializers.PrimaryKeyRelatedField(
        queryset=EvaluationCriteria.objects.all(), write_only=True, source='criteria'
    )
    effective_weight = serializers.SerializerMethodField()
    
    class Meta:
        model = TemplateCriteria
        fields = [
            'id', 'criteria', 'criteria_id', 'is_required', 'custom_weight',
            'effective_weight', 'order'
        ]
    
    def get_effective_weight(self, obj):
        return obj.custom_weight if obj.custom_weight else obj.criteria.weight


# Evaluation Template Serializer
class EvaluationTemplateSerializer(serializers.ModelSerializer):
    created_by = UserBasicSerializer(read_only=True)
    created_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='created_by', required=False
    )
    templatecriteria_set = TemplateCriteriaSerializer(many=True, read_only=True)
    evaluation_type_display = serializers.SerializerMethodField()
    criteria_count = serializers.SerializerMethodField()
    total_weight = serializers.SerializerMethodField()
    
    class Meta:
        model = EvaluationTemplate
        fields = [
            'id', 'name', 'description', 'evaluation_type', 'evaluation_type_display',
            'is_active', 'is_default', 'created_by', 'created_by_id',
            'templatecriteria_set', 'criteria_count', 'total_weight',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_evaluation_type_display(self, obj):
        return obj.get_evaluation_type_display()
    
    def get_criteria_count(self, obj):
        return obj.templatecriteria_set.count()
    
    def get_total_weight(self, obj):
        return sum(tc.effective_weight for tc in obj.templatecriteria_set.all())


# Evaluation Report Serializer
class EvaluationReportSerializer(serializers.ModelSerializer):
    generated_by = UserBasicSerializer(read_only=True)
    generated_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='generated_by', required=False
    )
    mozes = MozeBasicSerializer(many=True, read_only=True)
    moze_ids = serializers.PrimaryKeyRelatedField(
        queryset=Moze.objects.all(), many=True, write_only=True, source='mozes', required=False
    )
    report_type_display = serializers.SerializerMethodField()
    period_duration = serializers.SerializerMethodField()
    moze_count = serializers.SerializerMethodField()
    days_since_generated = serializers.SerializerMethodField()
    
    class Meta:
        model = EvaluationReport
        fields = [
            'id', 'title', 'report_type', 'report_type_display', 'mozes', 'moze_ids',
            'evaluation_period_start', 'evaluation_period_end', 'period_duration',
            'report_data', 'summary', 'recommendations', 'generated_by', 'generated_by_id',
            'moze_count', 'days_since_generated', 'generated_at', 'is_published'
        ]
        read_only_fields = ['generated_at']
    
    def get_report_type_display(self, obj):
        return obj.get_report_type_display()
    
    def get_period_duration(self, obj):
        delta = obj.evaluation_period_end - obj.evaluation_period_start
        return delta.days + 1
    
    def get_moze_count(self, obj):
        return obj.mozes.count()
    
    def get_days_since_generated(self, obj):
        return (timezone.now().date() - obj.generated_at.date()).days


# Evaluation History Serializer
class EvaluationHistorySerializer(serializers.ModelSerializer):
    changed_by = UserBasicSerializer(read_only=True)
    evaluation_title = serializers.SerializerMethodField()
    
    class Meta:
        model = EvaluationHistory
        fields = [
            'id', 'evaluation', 'evaluation_title', 'field_name', 'old_value',
            'new_value', 'changed_by', 'changed_at', 'change_reason'
        ]
        read_only_fields = ['changed_at']
    
    def get_evaluation_title(self, obj):
        return str(obj.evaluation)


# Statistics Serializers
class EvaluationStatsSerializer(serializers.Serializer):
    total_evaluations = serializers.IntegerField()
    published_evaluations = serializers.IntegerField()
    draft_evaluations = serializers.IntegerField()
    evaluations_by_grade = serializers.DictField()
    evaluations_by_period = serializers.DictField()
    average_overall_score = serializers.FloatField()
    mozes_needing_attention = serializers.IntegerField()


class CriteriaStatsSerializer(serializers.Serializer):
    total_criteria = serializers.IntegerField()
    active_criteria = serializers.IntegerField()
    criteria_by_category = serializers.DictField()
    criteria_by_type = serializers.DictField()
    average_weight = serializers.FloatField()


# Search Serializers
class EvaluationSearchSerializer(serializers.Serializer):
    moze_name = serializers.CharField(required=False)
    evaluator = serializers.CharField(required=False)
    evaluation_period = serializers.CharField(required=False)
    overall_grade = serializers.CharField(required=False)
    certification_status = serializers.CharField(required=False)
    is_published = serializers.BooleanField(required=False)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)