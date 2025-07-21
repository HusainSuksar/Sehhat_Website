from django.contrib import admin
from .models import Moze, MozeComment, MozeSettings


@admin.register(Moze)
class MozeAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'aamil', 'moze_coordinator', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at', 'established_date')
    search_fields = ('name', 'location', 'aamil__username', 'aamil__first_name', 'aamil__last_name')
    filter_horizontal = ('team_members',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'location', 'address', 'established_date')
        }),
        ('Management', {
            'fields': ('aamil', 'moze_coordinator', 'team_members')
        }),
        ('Contact & Settings', {
            'fields': ('contact_phone', 'contact_email', 'capacity', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MozeComment)
class MozeCommentAdmin(admin.ModelAdmin):
    list_display = ('moze', 'author', 'content_preview', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at', 'moze')
    search_fields = ('content', 'author__username', 'moze__name')
    readonly_fields = ('created_at', 'updated_at')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'


@admin.register(MozeSettings)
class MozeSettingsAdmin(admin.ModelAdmin):
    list_display = ('moze', 'allow_walk_ins', 'appointment_duration', 'working_hours_start', 'working_hours_end')
    list_filter = ('allow_walk_ins', 'created_at')
    search_fields = ('moze__name',)
