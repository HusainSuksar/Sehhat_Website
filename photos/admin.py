from django.contrib import admin
from django.utils.html import format_html
from .models import PhotoAlbum, Photo, PhotoTag, PhotoComment, PhotoLike


class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 0
    readonly_fields = ['uploaded_at', 'uploaded_by']
    fields = ['title', 'image', 'uploaded_by', 'uploaded_at']


@admin.register(PhotoAlbum)
class PhotoAlbumAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'photo_count', 'is_public', 'allow_uploads', 'created_at']
    list_filter = ['is_public', 'allow_uploads', 'created_at', 'moze']
    search_fields = ['name', 'description', 'created_by__username']
    readonly_fields = ['created_at']
    inlines = [PhotoInline]
    
    def photo_count(self, obj):
        return obj.photos.count()
    photo_count.short_description = 'Photos'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


class PhotoCommentInline(admin.TabularInline):
    model = PhotoComment
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['title', 'album', 'uploaded_by', 'image_preview', 'likes_count', 'uploaded_at']
    list_filter = ['album', 'uploaded_at', 'moze']
    search_fields = ['title', 'description', 'uploaded_by__username', 'album__name']
    readonly_fields = ['uploaded_at', 'image_preview']
    filter_horizontal = ['tags']
    inlines = [PhotoCommentInline]
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 100px; max-height: 100px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Preview'
    
    def likes_count(self, obj):
        return obj.likes.count()
    likes_count.short_description = 'Likes'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(PhotoTag)
class PhotoTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'usage_count', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']
    
    def usage_count(self, obj):
        return obj.photos.count()
    usage_count.short_description = 'Used in photos'


@admin.register(PhotoComment)
class PhotoCommentAdmin(admin.ModelAdmin):
    list_display = ['photo', 'user', 'content_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['photo__title', 'user__username', 'content']
    readonly_fields = ['created_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'


@admin.register(PhotoLike)
class PhotoLikeAdmin(admin.ModelAdmin):
    list_display = ['photo', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['photo__title', 'user__username']
    readonly_fields = ['created_at']
