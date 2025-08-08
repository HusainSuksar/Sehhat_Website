"""
Serializers for the Photos app
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import Photo, PhotoAlbum, PhotoComment, PhotoLike, PhotoTag
from moze.models import Moze

User = get_user_model()


# Basic serializers for nested relationships
class UserBasicSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'full_name', 'role']
        read_only_fields = fields
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class MozeBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Moze
        fields = ['id', 'name', 'location', 'is_active']
        read_only_fields = fields


# PhotoTag Serializer
class PhotoTagSerializer(serializers.ModelSerializer):
    photo_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PhotoTag
        fields = [
            'id', 'name', 'description', 'color', 'photo_count', 'created_at'
        ]
        read_only_fields = ['created_at']
    
    def get_photo_count(self, obj):
        return obj.photos.count()


# Photo Serializer
class PhotoSerializer(serializers.ModelSerializer):
    uploaded_by = UserBasicSerializer(read_only=True)
    uploaded_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='uploaded_by', required=False
    )
    moze = MozeBasicSerializer(read_only=True)
    moze_id = serializers.PrimaryKeyRelatedField(
        queryset=Moze.objects.all(), write_only=True, source='moze'
    )
    tags = PhotoTagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=PhotoTag.objects.all(), many=True, write_only=True, source='tags', required=False
    )
    
    # Computed fields
    category_display = serializers.SerializerMethodField()
    file_size_mb = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    is_liked_by_user = serializers.SerializerMethodField()
    albums_count = serializers.SerializerMethodField()
    days_since_upload = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()
    
    class Meta:
        model = Photo
        fields = [
            'id', 'image', 'title', 'description', 'subject_tag', 'moze', 'moze_id',
            'uploaded_by', 'uploaded_by_id', 'location', 'event_date', 'photographer',
            'category', 'category_display', 'is_public', 'is_featured', 'requires_permission',
            'file_size', 'file_size_mb', 'image_width', 'image_height', 'tags', 'tag_ids',
            'image_url', 'thumbnail_url', 'comments_count', 'likes_count', 'is_liked_by_user',
            'albums_count', 'days_since_upload', 'can_edit', 'can_delete',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'file_size', 'image_width', 'image_height']
    
    def get_category_display(self, obj):
        return obj.get_category_display()
    
    def get_file_size_mb(self, obj):
        return obj.get_file_size_mb()
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    def get_thumbnail_url(self, obj):
        # For now, return the same as image_url
        # In production, you might want to generate thumbnails
        return self.get_image_url(obj)
    
    def get_comments_count(self, obj):
        return obj.comments.filter(is_active=True).count()
    
    def get_likes_count(self, obj):
        return obj.likes.count()
    
    def get_is_liked_by_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
    
    def get_albums_count(self, obj):
        return obj.albums.count()
    
    def get_days_since_upload(self, obj):
        return (timezone.now().date() - obj.created_at.date()).days
    
    def get_can_edit(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user = request.user
            # Admin, uploader, or moze staff can edit
            return (user.is_admin or 
                    obj.uploaded_by == user or 
                    (hasattr(user, 'managed_mozes') and obj.moze in user.managed_mozes.all()) or
                    user.role in ['aamil', 'moze_coordinator'])
        return False
    
    def get_can_delete(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user = request.user
            # Admin, uploader, or moze admin can delete
            return (user.is_admin or 
                    obj.uploaded_by == user or 
                    (hasattr(user, 'managed_mozes') and obj.moze in user.managed_mozes.all()))
        return False


# Photo Create/Update Serializer (simplified)
class PhotoCreateSerializer(serializers.ModelSerializer):
    uploaded_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='uploaded_by', required=False
    )
    moze_id = serializers.PrimaryKeyRelatedField(
        queryset=Moze.objects.all(), source='moze'
    )
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=PhotoTag.objects.all(), many=True, source='tags', required=False
    )
    
    class Meta:
        model = Photo
        fields = [
            'image', 'title', 'description', 'subject_tag', 'moze_id', 'uploaded_by_id',
            'location', 'event_date', 'photographer', 'category', 'is_public', 'is_featured',
            'requires_permission', 'tag_ids'
        ]
    
    def validate_image(self, image):
        """Validate image file"""
        # Check file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if image.size > max_size:
            raise serializers.ValidationError("Image file too large. Maximum size is 10MB.")
        
        # Check file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
        if hasattr(image, 'content_type') and image.content_type not in allowed_types:
            raise serializers.ValidationError(
                "Unsupported image format. Allowed formats: JPEG, PNG, GIF, WebP."
            )
        
        return image
    
    def validate(self, data):
        """Validate photo data"""
        # Check if user has permission to upload to this moze
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user = request.user
            moze = data.get('moze')
            
            if not (user.is_admin or 
                    (hasattr(user, 'managed_mozes') and moze in user.managed_mozes.all()) or
                    user.role in ['aamil', 'moze_coordinator']):
                raise serializers.ValidationError("You don't have permission to upload photos to this Moze.")
        
        return data


# PhotoAlbum Serializer
class PhotoAlbumSerializer(serializers.ModelSerializer):
    created_by = UserBasicSerializer(read_only=True)
    created_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='created_by', required=False
    )
    moze = MozeBasicSerializer(read_only=True)
    moze_id = serializers.PrimaryKeyRelatedField(
        queryset=Moze.objects.all(), write_only=True, source='moze'
    )
    cover_photo = PhotoSerializer(read_only=True)
    cover_photo_id = serializers.PrimaryKeyRelatedField(
        queryset=Photo.objects.all(), write_only=True, source='cover_photo', required=False
    )
    photos = PhotoSerializer(many=True, read_only=True)
    photo_ids = serializers.PrimaryKeyRelatedField(
        queryset=Photo.objects.all(), many=True, write_only=True, source='photos', required=False
    )
    
    # Computed fields
    photo_count = serializers.SerializerMethodField()
    latest_photos = serializers.SerializerMethodField()
    days_since_creation = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()
    can_upload = serializers.SerializerMethodField()
    
    class Meta:
        model = PhotoAlbum
        fields = [
            'id', 'name', 'description', 'moze', 'moze_id', 'created_by', 'created_by_id',
            'photos', 'photo_ids', 'cover_photo', 'cover_photo_id', 'is_public', 'allow_uploads',
            'event_date', 'photo_count', 'latest_photos', 'days_since_creation',
            'can_edit', 'can_delete', 'can_upload', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_photo_count(self, obj):
        return obj.get_photo_count()
    
    def get_latest_photos(self, obj):
        """Get latest 4 photos for preview"""
        latest_photos = obj.photos.order_by('-created_at')[:4]
        return PhotoSerializer(latest_photos, many=True, context=self.context).data
    
    def get_days_since_creation(self, obj):
        return (timezone.now().date() - obj.created_at.date()).days
    
    def get_can_edit(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user = request.user
            return (user.is_admin or 
                    obj.created_by == user or 
                    (hasattr(user, 'managed_mozes') and obj.moze in user.managed_mozes.all()) or
                    user.role in ['aamil', 'moze_coordinator'])
        return False
    
    def get_can_delete(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user = request.user
            return (user.is_admin or 
                    obj.created_by == user or 
                    (hasattr(user, 'managed_mozes') and obj.moze in user.managed_mozes.all()))
        return False
    
    def get_can_upload(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user = request.user
            return (obj.allow_uploads and 
                    (user.is_admin or 
                     (hasattr(user, 'managed_mozes') and obj.moze in user.managed_mozes.all()) or
                     user.role in ['aamil', 'moze_coordinator']))
        return False


# PhotoAlbum Create/Update Serializer (simplified)
class PhotoAlbumCreateSerializer(serializers.ModelSerializer):
    created_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='created_by', required=False
    )
    moze_id = serializers.PrimaryKeyRelatedField(
        queryset=Moze.objects.all(), source='moze'
    )
    cover_photo_id = serializers.PrimaryKeyRelatedField(
        queryset=Photo.objects.all(), source='cover_photo', required=False
    )
    photo_ids = serializers.PrimaryKeyRelatedField(
        queryset=Photo.objects.all(), many=True, source='photos', required=False
    )
    
    class Meta:
        model = PhotoAlbum
        fields = [
            'name', 'description', 'moze_id', 'created_by_id', 'cover_photo_id',
            'photo_ids', 'is_public', 'allow_uploads', 'event_date'
        ]
    
    def validate(self, data):
        """Validate album data"""
        # Check if user has permission to create album for this moze
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user = request.user
            moze = data.get('moze')
            
            if not (user.is_admin or 
                    (hasattr(user, 'managed_mozes') and moze in user.managed_mozes.all()) or
                    user.role in ['aamil', 'moze_coordinator']):
                raise serializers.ValidationError("You don't have permission to create albums for this Moze.")
        
        # Check for duplicate album name within moze
        name = data.get('name')
        moze = data.get('moze')
        if name and moze:
            existing = PhotoAlbum.objects.filter(name=name, moze=moze)
            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise serializers.ValidationError("An album with this name already exists in this Moze.")
        
        return data


# PhotoComment Serializer
class PhotoCommentSerializer(serializers.ModelSerializer):
    author = UserBasicSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='author', required=False
    )
    photo = PhotoSerializer(read_only=True)
    photo_id = serializers.PrimaryKeyRelatedField(
        queryset=Photo.objects.all(), write_only=True, source='photo'
    )
    
    # Computed fields
    days_since_comment = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()
    
    class Meta:
        model = PhotoComment
        fields = [
            'id', 'photo', 'photo_id', 'author', 'author_id', 'content', 'is_active',
            'days_since_comment', 'can_edit', 'can_delete', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_days_since_comment(self, obj):
        return (timezone.now().date() - obj.created_at.date()).days
    
    def get_can_edit(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user = request.user
            return user.is_admin or obj.author == user
        return False
    
    def get_can_delete(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user = request.user
            return (user.is_admin or 
                    obj.author == user or 
                    (hasattr(user, 'managed_mozes') and obj.photo.moze in user.managed_mozes.all()))
        return False


# PhotoComment Create Serializer (simplified)
class PhotoCommentCreateSerializer(serializers.ModelSerializer):
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='author', required=False
    )
    photo_id = serializers.PrimaryKeyRelatedField(
        queryset=Photo.objects.all(), source='photo'
    )
    
    class Meta:
        model = PhotoComment
        fields = ['photo_id', 'author_id', 'content']
    
    def validate(self, data):
        """Validate comment data"""
        # Check if user can comment on this photo
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user = request.user
            photo = data.get('photo')
            
            # Check if photo is public or user has access to the moze
            if not photo.is_public:
                if not (user.is_admin or 
                        (hasattr(user, 'managed_mozes') and photo.moze in user.managed_mozes.all()) or
                        user.role in ['aamil', 'moze_coordinator']):
                    raise serializers.ValidationError("You don't have permission to comment on this photo.")
        
        return data


# PhotoLike Serializer
class PhotoLikeSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='user', 
        required=False, allow_null=True
    )
    photo = PhotoSerializer(read_only=True)
    photo_id = serializers.PrimaryKeyRelatedField(
        queryset=Photo.objects.all(), write_only=True, source='photo'
    )
    
    class Meta:
        model = PhotoLike
        fields = ['id', 'photo', 'photo_id', 'user', 'user_id', 'created_at']
        read_only_fields = ['created_at']
    
    def to_internal_value(self, data):
        """Override to handle user_id for authenticated users"""
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            # For authenticated users, don't require user_id (view will set it)
            if 'user_id' not in data:
                # Temporarily add a placeholder to pass validation
                data = data.copy()
                data['user_id'] = None
        
        # Continue with normal validation
        return super().to_internal_value(data)
    
    def validate(self, data):
        """Validate like data"""
        # First, handle user cleanup for authenticated users
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            # For authenticated users, remove the placeholder user
            if data.get('user') is None:
                data.pop('user', None)
        
        # Then continue with original validation logic
        # Check if user can like this photo
        if request and request.user.is_authenticated:
            user = request.user
            photo = data.get('photo')
            
            # Check if photo is public or user has access to the moze
            if not photo.is_public:
                if not (user.is_admin or 
                        (hasattr(user, 'managed_mozes') and photo.moze in user.managed_mozes.all()) or
                        user.role in ['aamil', 'moze_coordinator']):
                    raise serializers.ValidationError("You don't have permission to like this photo.")
        
        return data


# Statistics Serializers
class PhotoStatsSerializer(serializers.Serializer):
    total_photos = serializers.IntegerField()
    total_albums = serializers.IntegerField()
    total_comments = serializers.IntegerField()
    total_likes = serializers.IntegerField()
    photos_by_category = serializers.DictField()
    photos_by_moze = serializers.DictField()
    recent_uploads = serializers.ListField()
    popular_photos = serializers.ListField()
    storage_usage_mb = serializers.FloatField()
    average_file_size_mb = serializers.FloatField()


class AlbumStatsSerializer(serializers.Serializer):
    total_albums = serializers.IntegerField()
    public_albums = serializers.IntegerField()
    private_albums = serializers.IntegerField()
    albums_by_moze = serializers.DictField()
    largest_albums = serializers.ListField()
    recent_albums = serializers.ListField()
    average_photos_per_album = serializers.FloatField()


# Photo Search Serializer
class PhotoSearchSerializer(serializers.Serializer):
    title = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    subject_tag = serializers.CharField(required=False)
    category = serializers.CharField(required=False)
    photographer = serializers.CharField(required=False)
    location = serializers.CharField(required=False)
    moze_id = serializers.IntegerField(required=False)
    uploaded_by = serializers.CharField(required=False)
    is_public = serializers.BooleanField(required=False)
    is_featured = serializers.BooleanField(required=False)
    event_date_from = serializers.DateField(required=False)
    event_date_to = serializers.DateField(required=False)
    upload_date_from = serializers.DateTimeField(required=False)
    upload_date_to = serializers.DateTimeField(required=False)
    has_comments = serializers.BooleanField(required=False)
    has_likes = serializers.BooleanField(required=False)
    tag_names = serializers.ListField(child=serializers.CharField(), required=False)


# Bulk Operations Serializers
class BulkPhotoUpdateSerializer(serializers.Serializer):
    photo_ids = serializers.ListField(child=serializers.IntegerField())
    action = serializers.ChoiceField(choices=[
        ('set_public', 'Make Public'),
        ('set_private', 'Make Private'),
        ('set_featured', 'Set Featured'),
        ('unset_featured', 'Unset Featured'),
        ('add_to_album', 'Add to Album'),
        ('remove_from_album', 'Remove from Album'),
        ('add_tags', 'Add Tags'),
        ('remove_tags', 'Remove Tags'),
        ('delete', 'Delete Photos')
    ])
    album_id = serializers.IntegerField(required=False)
    tag_ids = serializers.ListField(child=serializers.IntegerField(), required=False)
    
    def validate(self, data):
        action = data.get('action')
        if action in ['add_to_album', 'remove_from_album'] and not data.get('album_id'):
            raise serializers.ValidationError("Album ID is required for album operations.")
        if action in ['add_tags', 'remove_tags'] and not data.get('tag_ids'):
            raise serializers.ValidationError("Tag IDs are required for tag operations.")
        return data


class PhotoUploadSerializer(serializers.Serializer):
    """Serializer for multiple photo upload"""
    images = serializers.ListField(
        child=serializers.ImageField(),
        allow_empty=False,
        max_length=20  # Max 20 photos at once
    )
    moze_id = serializers.PrimaryKeyRelatedField(queryset=Moze.objects.all())
    album_id = serializers.PrimaryKeyRelatedField(
        queryset=PhotoAlbum.objects.all(), required=False
    )
    category = serializers.ChoiceField(choices=Photo.CATEGORY_CHOICES, default='other')
    subject_tag = serializers.CharField(max_length=100)
    location = serializers.CharField(max_length=200, required=False)
    event_date = serializers.DateField(required=False)
    photographer = serializers.CharField(max_length=100, required=False)
    is_public = serializers.BooleanField(default=False)
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )
    
    def validate_images(self, images):
        """Validate uploaded images"""
        max_size = 10 * 1024 * 1024  # 10MB per image
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
        
        for image in images:
            if image.size > max_size:
                raise serializers.ValidationError(f"Image {image.name} is too large. Maximum size is 10MB.")
            
            if hasattr(image, 'content_type') and image.content_type not in allowed_types:
                raise serializers.ValidationError(
                    f"Image {image.name} has unsupported format. Allowed: JPEG, PNG, GIF, WebP."
                )
        
        return images