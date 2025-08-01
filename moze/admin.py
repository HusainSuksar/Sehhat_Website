from django.contrib import admin
from .models import Moze, MozeComment, MozeSettings

@admin.register(Moze)
class MozeAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'aamil', 'moze_coordinator', 'is_active', 'capacity', 'created_at']
    list_filter = ['is_active', 'established_date', 'created_at']
    search_fields = ['name', 'location', 'aamil__first_name', 'aamil__last_name']
    filter_horizontal = ['team_members']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'location', 'address', 'established_date', 'is_active')
        }),
        ('Management', {
            'fields': ('aamil', 'moze_coordinator', 'team_members')
        }),
        ('Capacity & Contact', {
            'fields': ('capacity', 'contact_phone', 'contact_email')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(MozeComment)
class MozeCommentAdmin(admin.ModelAdmin):
    list_display = ['moze', 'author', 'content', 'parent', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'moze']
    search_fields = ['content', 'author__first_name', 'author__last_name', 'moze__name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Comment Information', {
            'fields': ('moze', 'author', 'content', 'parent', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(MozeSettings)
class MozeSettingsAdmin(admin.ModelAdmin):
    list_display = ['moze', 'allow_walk_ins', 'appointment_duration', 'working_hours_start', 'working_hours_end']
    list_filter = ['allow_walk_ins', 'working_days']
    search_fields = ['moze__name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['moze__name']
    
    fieldsets = (
        ('Moze Settings', {
            'fields': ('moze', 'allow_walk_ins', 'appointment_duration')
        }),
        ('Working Hours', {
            'fields': ('working_hours_start', 'working_hours_end', 'working_days')
        }),
        ('Contact & Instructions', {
            'fields': ('emergency_contact', 'special_instructions')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
