from django.contrib import admin
from django.utils.html import format_html
from .models import Petition, PetitionCategory, PetitionStatus


@admin.register(PetitionCategory)
class PetitionCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(PetitionStatus)
class PetitionStatusAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'is_final', 'order']
    list_filter = ['is_final']
    ordering = ['order']


@admin.register(Petition)
class PetitionAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'category', 'status', 'priority', 'created_at', 'resolved_at']
    list_filter = ['status', 'priority', 'category', 'created_at', 'resolved_at']
    search_fields = ['title', 'description', 'created_by__username', 'created_by__first_name', 'created_by__last_name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'created_by', 'category', 'status', 'priority')
        }),
        ('Resolution', {
            'fields': ('resolved_at', 'resolution_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
