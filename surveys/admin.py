from django.contrib import admin
from django.utils.html import format_html
from .models import Survey, Question, Choice, Response, SurveySubmission


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0
    fields = ['text', 'question_type', 'is_required', 'order']
    ordering = ['order']


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0
    fields = ['text', 'order']
    ordering = ['order']


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'created_by', 'questions_count', 'submissions_count',
        'is_active', 'created_at'
    ]
    list_filter = ['is_active', 'is_anonymous', 'created_at']
    search_fields = ['title', 'description', 'created_by__username']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [QuestionInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description')
        }),
        ('Settings', {
            'fields': ('is_active', 'is_anonymous', 'allow_multiple_submissions')
        }),
        ('Access Control', {
            'fields': ('restricted_to_roles',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def questions_count(self, obj):
        return obj.questions.count()
    questions_count.short_description = 'Questions'
    
    def submissions_count(self, obj):
        return obj.submissions.count()
    submissions_count.short_description = 'Submissions'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = [
        'survey', 'text_preview', 'question_type', 'is_required',
        'choices_count', 'order'
    ]
    list_filter = ['question_type', 'is_required', 'survey']
    search_fields = ['text', 'survey__title']
    inlines = [ChoiceInline]
    ordering = ['survey', 'order']
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Question Text'
    
    def choices_count(self, obj):
        return obj.choices.count()
    choices_count.short_description = 'Choices'


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['question', 'text', 'order']
    list_filter = ['question__survey', 'question__question_type']
    search_fields = ['text', 'question__text', 'question__survey__title']
    ordering = ['question', 'order']


class ResponseInline(admin.TabularInline):
    model = Response
    extra = 0
    readonly_fields = ['question', 'answer_text', 'selected_choice']


@admin.register(SurveySubmission)
class SurveySubmissionAdmin(admin.ModelAdmin):
    list_display = [
        'survey', 'submitted_by', 'completion_status', 'submitted_at'
    ]
    list_filter = ['survey', 'submitted_at', 'is_complete']
    search_fields = [
        'survey__title', 'submitted_by__username',
        'submitted_by__first_name', 'submitted_by__last_name'
    ]
    readonly_fields = ['submitted_at']
    inlines = [ResponseInline]
    
    def completion_status(self, obj):
        if obj.is_complete:
            return format_html('<span style="color: green;">✓ Complete</span>')
        else:
            total_questions = obj.survey.questions.filter(is_required=True).count()
            answered_questions = obj.responses.filter(
                question__is_required=True
            ).count()
            percentage = (answered_questions / total_questions * 100) if total_questions > 0 else 0
            return format_html(
                '<span style="color: orange;">{:.0f}% ({}/{})</span>',
                percentage, answered_questions, total_questions
            )
    completion_status.short_description = 'Completion'


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = [
        'submission', 'question', 'answer_preview', 'selected_choice'
    ]
    list_filter = ['question__survey', 'question__question_type']
    search_fields = [
        'submission__survey__title', 'question__text', 'answer_text'
    ]
    
    def answer_preview(self, obj):
        if obj.answer_text:
            return obj.answer_text[:50] + '...' if len(obj.answer_text) > 50 else obj.answer_text
        return '-'
    answer_preview.short_description = 'Answer'
