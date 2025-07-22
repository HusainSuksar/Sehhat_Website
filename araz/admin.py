from django.contrib import admin
from django.utils.html import format_html
from .models import (
    DuaAraz, Petition, PetitionCategory, PetitionComment, 
    PetitionAttachment, PetitionAssignment, PetitionUpdate,
    ArazComment, ArazAttachment, ArazStatusHistory,
    ArazNotification
)


@admin.register(PetitionCategory)
class PetitionCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color_display', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'name': ('name',)}
    
    def color_display(self, obj):
        return format_html(
            '<span style="color: {}; font-weight: bold;">●</span> {}',
            obj.color,
            obj.color
        )
    color_display.short_description = 'Color'


class PetitionCommentInline(admin.TabularInline):
    model = PetitionComment
    extra = 0
    readonly_fields = ['created_at']


class PetitionAttachmentInline(admin.TabularInline):
    model = PetitionAttachment
    extra = 0
    readonly_fields = ['uploaded_at']


class PetitionAssignmentInline(admin.TabularInline):
    model = PetitionAssignment
    extra = 0
    readonly_fields = ['assigned_at']


@admin.register(Petition)
class PetitionAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'status', 'priority', 'category', 'created_at']
    list_filter = ['status', 'priority', 'category', 'is_anonymous', 'created_at']
    search_fields = ['title', 'description', 'created_by__username', 'created_by__email']
    readonly_fields = ['created_at', 'updated_at', 'resolved_at']
    inlines = [PetitionCommentInline, PetitionAttachmentInline, PetitionAssignmentInline]
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'category')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority', 'is_anonymous')
        }),
        ('Location', {
            'fields': ('moze',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at', 'resolved_at'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


class ArazCommentInline(admin.TabularInline):
    model = ArazComment
    extra = 0
    readonly_fields = ['created_at', 'updated_at']


class ArazAttachmentInline(admin.TabularInline):
    model = ArazAttachment
    extra = 0
    readonly_fields = ['uploaded_at', 'file_size']


@admin.register(DuaAraz)
class DuaArazAdmin(admin.ModelAdmin):
    list_display = [
        'patient_name', 'patient_its_id', 'request_type', 
        'urgency_level', 'status', 'assigned_doctor', 'created_at'
    ]
    list_filter = [
        'request_type', 'urgency_level', 'status', 'priority',
        'preferred_contact_method', 'created_at'
    ]
    search_fields = [
        'patient_name', 'patient_its_id', 'patient_email', 
        'ailment', 'symptoms'
    ]
    readonly_fields = ['created_at', 'updated_at', 'assigned_date']
    inlines = [ArazCommentInline, ArazAttachmentInline]
    
    fieldsets = (
        ('Patient Information', {
            'fields': (
                'patient_its_id', 'patient_name', 'patient_phone', 
                'patient_email', 'patient_user'
            )
        }),
        ('Request Details', {
            'fields': (
                'ailment', 'symptoms', 'request_type', 'urgency_level'
            )
        }),
        ('Medical History', {
            'fields': (
                'previous_medical_history', 'current_medications', 'allergies'
            ),
            'classes': ('collapse',)
        }),
        ('Preferences', {
            'fields': (
                'preferred_doctor', 'preferred_location', 'preferred_time',
                'preferred_contact_method'
            )
        }),
        ('Status & Processing', {
            'fields': (
                'status', 'priority', 'assigned_doctor', 'assigned_date',
                'scheduled_date'
            )
        }),
        ('Notes', {
            'fields': ('admin_notes', 'patient_feedback'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(PetitionComment)
class PetitionCommentAdmin(admin.ModelAdmin):
    list_display = ['petition', 'user', 'content_preview', 'is_internal', 'created_at']
    list_filter = ['is_internal', 'created_at']
    search_fields = ['petition__title', 'user__username', 'content']
    readonly_fields = ['created_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'


@admin.register(ArazComment)
class ArazCommentAdmin(admin.ModelAdmin):
    list_display = ['araz', 'author', 'content_preview', 'is_internal', 'created_at']
    list_filter = ['is_internal', 'created_at']
    search_fields = ['araz__patient_name', 'author__username', 'content']
    readonly_fields = ['created_at', 'updated_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'


@admin.register(PetitionAssignment)
class PetitionAssignmentAdmin(admin.ModelAdmin):
    list_display = ['petition', 'assigned_to', 'assigned_by', 'is_active', 'assigned_at']
    list_filter = ['is_active', 'assigned_at']
    search_fields = ['petition__title', 'assigned_to__username', 'assigned_by__username']
    readonly_fields = ['assigned_at']


@admin.register(PetitionUpdate)
class PetitionUpdateAdmin(admin.ModelAdmin):
    list_display = ['petition', 'status', 'created_by', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['petition__title', 'description']
    readonly_fields = ['created_at']


@admin.register(ArazStatusHistory)
class ArazStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['araz', 'old_status', 'new_status', 'changed_by', 'changed_at']
    list_filter = ['old_status', 'new_status', 'changed_at']
    search_fields = ['araz__patient_name', 'changed_by__username', 'change_reason']
    readonly_fields = ['changed_at']


@admin.register(ArazNotification)
class ArazNotificationAdmin(admin.ModelAdmin):
    list_display = ['araz', 'recipient', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['araz__patient_name', 'recipient__username', 'message']
    readonly_fields = ['created_at']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected notifications as read"
    
    actions = [mark_as_read]
