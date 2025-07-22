from django.contrib import admin
from django.utils.html import format_html
from .models import (
    EvaluationForm, EvaluationCriteria, EvaluationSubmission,
    EvaluationResponse, EvaluationSession
)


class EvaluationCriteriaInline(admin.TabularInline):
    model = EvaluationCriteria
    extra = 0
    fields = ['criteria_text', 'criteria_type', 'max_score', 'weight', 'is_required', 'order']
    ordering = ['order']


@admin.register(EvaluationForm)
class EvaluationFormAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'form_type', 'target_role', 'due_date',
        'submissions_count', 'is_active', 'created_by'
    ]
    list_filter = ['form_type', 'target_role', 'is_active', 'is_anonymous', 'created_at']
    search_fields = ['title', 'description', 'created_by__username']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [EvaluationCriteriaInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'form_type', 'target_role')
        }),
        ('Settings', {
            'fields': ('due_date', 'is_anonymous', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def submissions_count(self, obj):
        return obj.submissions.count()
    submissions_count.short_description = 'Submissions'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(EvaluationCriteria)
class EvaluationCriteriaAdmin(admin.ModelAdmin):
    list_display = [
        'evaluation_form', 'criteria_text_short', 'criteria_type',
        'max_score', 'weight', 'is_required', 'order'
    ]
    list_filter = ['criteria_type', 'is_required', 'evaluation_form']
    search_fields = ['criteria_text', 'evaluation_form__title']
    ordering = ['evaluation_form', 'order']
    
    def criteria_text_short(self, obj):
        return obj.criteria_text[:50] + '...' if len(obj.criteria_text) > 50 else obj.criteria_text
    criteria_text_short.short_description = 'Criteria Text'


class EvaluationResponseInline(admin.TabularInline):
    model = EvaluationResponse
    extra = 0
    readonly_fields = ['criteria']


@admin.register(EvaluationSubmission)
class EvaluationSubmissionAdmin(admin.ModelAdmin):
    list_display = [
        'evaluation_form', 'submitted_by', 'evaluated_user',
        'score', 'completion_percentage', 'submitted_at'
    ]
    list_filter = ['evaluation_form', 'submitted_at', 'is_complete']
    search_fields = [
        'evaluation_form__title', 'submitted_by__username',
        'evaluated_user__username'
    ]
    readonly_fields = ['submitted_at', 'completion_percentage', 'score']
    inlines = [EvaluationResponseInline]
    
    def completion_percentage(self, obj):
        total_criteria = obj.evaluation_form.criteria.filter(is_required=True).count()
        completed_responses = obj.responses.filter(
            criteria__is_required=True
        ).count()
        
        if total_criteria > 0:
            percentage = (completed_responses / total_criteria) * 100
            color = 'green' if percentage == 100 else 'orange' if percentage >= 50 else 'red'
            return format_html(
                '<span style="color: {};">{:.0f}%</span>',
                color, percentage
            )
        return 'N/A'
    completion_percentage.short_description = 'Completion'


@admin.register(EvaluationResponse)
class EvaluationResponseAdmin(admin.ModelAdmin):
    list_display = [
        'submission', 'criteria', 'response_type', 'score_value',
        'text_response_preview'
    ]
    list_filter = ['criteria__criteria_type', 'submission__evaluation_form']
    search_fields = [
        'submission__evaluation_form__title', 'criteria__criteria_text',
        'text_response'
    ]
    
    def response_type(self, obj):
        return obj.criteria.criteria_type
    response_type.short_description = 'Type'
    
    def text_response_preview(self, obj):
        if obj.text_response:
            return obj.text_response[:50] + '...' if len(obj.text_response) > 50 else obj.text_response
        return '-'
    text_response_preview.short_description = 'Text Response'


@admin.register(EvaluationSession)
class EvaluationSessionAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'start_date', 'end_date', 'forms_count',
        'target_users_count', 'is_active'
    ]
    list_filter = ['is_active', 'start_date', 'end_date']
    search_fields = ['title', 'description']
    filter_horizontal = ['evaluation_forms', 'target_users']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description')
        }),
        ('Configuration', {
            'fields': ('evaluation_forms', 'target_users')
        }),
        ('Schedule', {
            'fields': ('start_date', 'end_date', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        })
    )
    
    def forms_count(self, obj):
        return obj.evaluation_forms.count()
    forms_count.short_description = 'Forms'
    
    def target_users_count(self, obj):
        return obj.target_users.count()
    target_users_count.short_description = 'Target Users'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
