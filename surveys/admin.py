from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Avg, Q
from .models import Survey, SurveyResponse, SurveyReminder, SurveyAnalytics


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ['title', 'target_role', 'created_by', 'is_active', 'get_responses_count', 'get_completion_rate', 'is_available']
    list_filter = ['target_role', 'is_active', 'is_anonymous', 'allow_multiple_responses', 'show_results', 'created_at']
    search_fields = ['title', 'description', 'created_by__username', 'created_by__first_name', 'created_by__last_name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'target_role')
        }),
        ('Survey Settings', {
            'fields': ('is_active', 'is_anonymous', 'allow_multiple_responses', 'show_results')
        }),
        ('Questions', {
            'fields': ('questions',),
            'description': 'JSON format questions. Use the sample structure as reference.'
        }),
        ('Time Settings', {
            'fields': ('start_date', 'end_date')
        }),
        ('Creator', {
            'fields': ('created_by',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Annotate with response counts"""
        return super().get_queryset(request).annotate(
            response_count=Count('responses'),
            complete_response_count=Count('responses', filter=Q(responses__is_complete=True))
        )
    
    def get_responses_count(self, obj):
        """Display response count with color coding"""
        count = getattr(obj, 'response_count', obj.responses.count())
        if count > 0:
            return format_html('<span style="color: green;">{}</span>', count)
        return format_html('<span style="color: red;">{}</span>', count)
    get_responses_count.short_description = 'Responses'
    get_responses_count.admin_order_field = 'response_count'
    
    def get_completion_rate(self, obj):
        """Display completion rate"""
        total = getattr(obj, 'response_count', obj.responses.count())
        complete = getattr(obj, 'complete_response_count', obj.responses.filter(is_complete=True).count())
        if total > 0:
            rate = (complete / total) * 100
            return format_html('{:.1f}%', rate)
        return '0%'
    get_completion_rate.short_description = 'Completion Rate'
    get_completion_rate.admin_order_field = 'complete_response_count'


@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ['survey', 'respondent', 'is_complete', 'completion_time', 'created_at', 'get_answers_preview']
    list_filter = ['is_complete', 'created_at', 'survey']
    search_fields = ['survey__title', 'respondent__username', 'respondent__first_name', 'respondent__last_name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Response Information', {
            'fields': ('survey', 'respondent', 'is_complete', 'completion_time')
        }),
        ('Answers', {
            'fields': ('answers',),
            'description': 'JSON format answers matching question IDs'
        }),
        ('Metadata', {
            'fields': ('ip_address', 'user_agent')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_answers_preview(self, obj):
        """Show preview of answers"""
        if obj.answers:
            preview = str(obj.answers)[:50]
            if len(str(obj.answers)) > 50:
                preview += '...'
            return preview
        return 'No answers'
    get_answers_preview.short_description = 'Answers Preview'


@admin.register(SurveyReminder)
class SurveyReminderAdmin(admin.ModelAdmin):
    list_display = ['survey', 'user', 'reminder_count', 'max_reminders', 'has_responded', 'is_active', 'last_reminder_sent']
    list_filter = ['has_responded', 'is_active', 'survey']
    search_fields = ['survey__title', 'user__username', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(SurveyAnalytics)
class SurveyAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['survey', 'total_invitations', 'total_responses', 'total_complete_responses', 'response_rate', 'completion_rate', 'avg_completion_time', 'last_calculated']
    list_filter = ['last_calculated']
    search_fields = ['survey__title']
    readonly_fields = ['last_calculated']
    ordering = ['-last_calculated']
    
    fieldsets = (
        ('Survey', {
            'fields': ('survey',)
        }),
        ('Response Statistics', {
            'fields': ('total_invitations', 'total_responses', 'total_complete_responses')
        }),
        ('Rates', {
            'fields': ('response_rate', 'completion_rate')
        }),
        ('Timing', {
            'fields': ('avg_completion_time',)
        }),
        ('Detailed Analytics', {
            'fields': ('detailed_analytics',),
            'description': 'JSON format detailed analytics data'
        }),
        ('Timestamps', {
            'fields': ('last_calculated',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Annotate with calculated rates"""
        return super().get_queryset(request)
    
    def response_rate(self, obj):
        """Display response rate with color coding"""
        if obj.total_invitations > 0:
            rate = (obj.total_responses / obj.total_invitations) * 100
            if rate >= 50:
                return format_html('<span style="color: green;">{:.1f}%</span>', rate)
            elif rate >= 25:
                return format_html('<span style="color: orange;">{:.1f}%</span>', rate)
            else:
                return format_html('<span style="color: red;">{:.1f}%</span>', rate)
        return '0%'
    response_rate.short_description = 'Response Rate'
    
    def completion_rate(self, obj):
        """Display completion rate with color coding"""
        if obj.total_responses > 0:
            rate = (obj.total_complete_responses / obj.total_responses) * 100
            if rate >= 80:
                return format_html('<span style="color: green;">{:.1f}%</span>', rate)
            elif rate >= 60:
                return format_html('<span style="color: orange;">{:.1f}%</span>', rate)
            else:
                return format_html('<span style="color: red;">{:.1f}%</span>', rate)
        return '0%'
    completion_rate.short_description = 'Completion Rate'
