from django.contrib import admin
from .models import (
    EvaluationForm, EvaluationSubmission, EvaluationResponse,
    EvaluationCriteria, Evaluation, EvaluationSession,
    EvaluationTemplate, TemplateCriteria, EvaluationReport,
    EvaluationHistory
)

@admin.register(EvaluationCriteria)
class EvaluationCriteriaAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'weight', 'max_score', 'is_active', 'order']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['category', 'order', 'name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(EvaluationForm)
class EvaluationFormAdmin(admin.ModelAdmin):
    list_display = ['title', 'evaluation_type', 'target_role', 'is_active', 'created_by', 'created_at']
    list_filter = ['evaluation_type', 'target_role', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'created_by__username']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

@admin.register(EvaluationSubmission)
class EvaluationSubmissionAdmin(admin.ModelAdmin):
    list_display = ['form', 'evaluator', 'target_user', 'total_score', 'is_complete', 'submitted_at']
    list_filter = ['is_complete', 'submitted_at', 'form__evaluation_type']
    search_fields = ['form__title', 'evaluator__username', 'target_user__username']
    readonly_fields = ['submitted_at', 'updated_at']
    ordering = ['-submitted_at']

@admin.register(EvaluationResponse)
class EvaluationResponseAdmin(admin.ModelAdmin):
    list_display = ['submission', 'criteria', 'score', 'created_at']
    list_filter = ['score', 'created_at', 'criteria__category']
    search_fields = ['submission__form__title', 'criteria__name']
    readonly_fields = ['created_at']
    ordering = ['-created_at']

@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ['moze', 'evaluator', 'evaluation_period', 'overall_grade', 'overall_score', 'evaluation_date']
    list_filter = ['evaluation_period', 'overall_grade', 'evaluation_date', 'is_published']
    search_fields = ['moze__name', 'evaluator__username']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-evaluation_date']

@admin.register(EvaluationSession)
class EvaluationSessionAdmin(admin.ModelAdmin):
    list_display = ['title', 'form', 'start_date', 'end_date', 'is_active', 'created_by']
    list_filter = ['is_active', 'start_date', 'end_date']
    search_fields = ['title', 'form__title', 'created_by__username']
    readonly_fields = ['created_at']
    ordering = ['-created_at']

@admin.register(EvaluationTemplate)
class EvaluationTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'evaluation_type', 'is_active', 'is_default', 'created_by']
    list_filter = ['evaluation_type', 'is_active', 'is_default']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']

@admin.register(EvaluationReport)
class EvaluationReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'report_type', 'generated_by', 'generated_at', 'is_published']
    list_filter = ['report_type', 'is_published', 'generated_at']
    search_fields = ['title', 'generated_by__username']
    readonly_fields = ['generated_at']
    ordering = ['-generated_at']
