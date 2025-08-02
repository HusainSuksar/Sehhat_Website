from django.contrib import admin
from .models import PhotoAlbum, Photo


@admin.register(PhotoAlbum)
class PhotoAlbumAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_by', 'is_public', 'created_at']
    list_filter = ['is_public', 'created_at']
    search_fields = ['name', 'description', 'created_by__username']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['title', 'moze', 'uploaded_by', 'created_at', 'file_size']
    list_filter = ['created_at', 'moze', 'category', 'is_public']
    search_fields = ['title', 'description', 'uploaded_by__username']
    readonly_fields = ['created_at', 'file_size']
    ordering = ['-created_at']
