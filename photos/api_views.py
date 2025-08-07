"""
API Views for the Photos app
"""
from rest_framework import generics, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from datetime import timedelta
from django.core.files.storage import default_storage
import os

from .models import Photo, PhotoAlbum, PhotoComment, PhotoLike, PhotoTag
from .serializers import (
    PhotoSerializer, PhotoCreateSerializer, PhotoAlbumSerializer, PhotoAlbumCreateSerializer,
    PhotoCommentSerializer, PhotoCommentCreateSerializer, PhotoLikeSerializer, PhotoTagSerializer,
    PhotoStatsSerializer, AlbumStatsSerializer, PhotoSearchSerializer,
    BulkPhotoUpdateSerializer, PhotoUploadSerializer
)


# Custom Permission Classes
class IsPhotoOwnerOrAdmin(permissions.BasePermission):
    """
    Permission for photo owners and admins to manage photos
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Admin can access everything
        if user.is_admin or user.is_superuser:
            return True
        
        # Photo uploader can manage their photos
        if hasattr(obj, 'uploaded_by'):
            return obj.uploaded_by == user
        elif hasattr(obj, 'created_by'):
            return obj.created_by == user
        elif hasattr(obj, 'author'):
            return obj.author == user
        elif hasattr(obj, 'user'):
            return obj.user == user
        
        return False


class IsPhotoStaffOrAdmin(permissions.BasePermission):
    """
    Permission for photo staff (admin, aamil, coordinators) and admins
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Admin can access everything
        if user.is_admin or user.is_superuser:
            return True
        
        # Staff roles can access photos in their mozes
        if user.role in ['aamil', 'moze_coordinator']:
            # Get the moze from the object
            if hasattr(obj, 'moze'):
                return hasattr(user, 'managed_mozes') and obj.moze in user.managed_mozes.all()
            elif hasattr(obj, 'photo'):
                return hasattr(user, 'managed_mozes') and obj.photo.moze in user.managed_mozes.all()
        
        # For public content, allow read access
        if request.method in permissions.SAFE_METHODS:
            if hasattr(obj, 'is_public') and obj.is_public:
                return True
            elif hasattr(obj, 'photo') and obj.photo.is_public:
                return True
        
        return False


class CanAccessPhoto(permissions.BasePermission):
    """
    Permission to check if user can access a photo
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated or request.method == 'GET'
    
    def has_object_permission(self, request, view, obj):
        # For public photos, allow access
        if hasattr(obj, 'is_public') and obj.is_public:
            return True
        elif hasattr(obj, 'photo') and obj.photo.is_public:
            return True
        
        # For authenticated users, check moze access
        if request.user.is_authenticated:
            user = request.user
            
            # Admin can access everything
            if user.is_admin or user.is_superuser:
                return True
            
            # Check moze access
            if hasattr(obj, 'moze'):
                moze = obj.moze
            elif hasattr(obj, 'photo'):
                moze = obj.photo.moze
            else:
                return False
            
            # Staff can access photos in their mozes
            if user.role in ['aamil', 'moze_coordinator']:
                return hasattr(user, 'managed_mozes') and moze in user.managed_mozes.all()
            
            # Other users can access if they're part of the moze team
            # This would need to be implemented based on your team structure
            return True
        
        return False


# Access Control Mixins
class PhotoAccessMixin:
    """
    Mixin to filter photo data based on user role and permissions
    """
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            # Admin can see all photos
            return Photo.objects.all()
        elif user.role in ['aamil', 'moze_coordinator']:
            # Staff can see photos from their mozes or public photos
            if hasattr(user, 'managed_mozes'):
                return Photo.objects.filter(
                    Q(moze__in=user.managed_mozes.all()) | Q(is_public=True)
                ).distinct()
            else:
                return Photo.objects.filter(is_public=True)
        else:
            # Regular users can see public photos and photos they uploaded
            return Photo.objects.filter(
                Q(is_public=True) | Q(uploaded_by=user)
            ).distinct()


class AlbumAccessMixin:
    """
    Mixin to filter album data based on user role and permissions
    """
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            return PhotoAlbum.objects.all()
        elif user.role in ['aamil', 'moze_coordinator']:
            if hasattr(user, 'managed_mozes'):
                return PhotoAlbum.objects.filter(
                    Q(moze__in=user.managed_mozes.all()) | Q(is_public=True)
                ).distinct()
            else:
                return PhotoAlbum.objects.filter(is_public=True)
        else:
            return PhotoAlbum.objects.filter(
                Q(is_public=True) | Q(created_by=user)
            ).distinct()


# Photo API Views
class PhotoListCreateAPIView(PhotoAccessMixin, generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_public', 'is_featured', 'moze', 'uploaded_by']
    search_fields = ['title', 'description', 'subject_tag', 'location', 'photographer']
    ordering_fields = ['title', 'created_at', 'event_date', 'file_size']
    ordering = ['-created_at']
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PhotoCreateSerializer
        return PhotoSerializer
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class PhotoDetailAPIView(PhotoAccessMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PhotoSerializer
    permission_classes = [CanAccessPhoto]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsPhotoOwnerOrAdmin()]
        return super().get_permissions()
    
    def perform_destroy(self, instance):
        # Delete the actual image file
        if instance.image:
            try:
                default_storage.delete(instance.image.name)
            except Exception:
                pass  # File might not exist
        
        instance.delete()


# Photo Album API Views
class PhotoAlbumListCreateAPIView(AlbumAccessMixin, generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_public', 'allow_uploads', 'moze', 'created_by']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'event_date']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PhotoAlbumCreateSerializer
        return PhotoAlbumSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PhotoAlbumDetailAPIView(AlbumAccessMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PhotoAlbumSerializer
    permission_classes = [CanAccessPhoto]
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsPhotoOwnerOrAdmin()]
        return super().get_permissions()


# Photo Comment API Views
class PhotoCommentListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['photo', 'author', 'is_active']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PhotoCommentCreateSerializer
        return PhotoCommentSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            return PhotoComment.objects.all()
        elif user.role in ['aamil', 'moze_coordinator']:
            if hasattr(user, 'managed_mozes'):
                return PhotoComment.objects.filter(
                    Q(photo__moze__in=user.managed_mozes.all()) | Q(photo__is_public=True)
                ).distinct()
            else:
                return PhotoComment.objects.filter(photo__is_public=True)
        else:
            return PhotoComment.objects.filter(
                Q(photo__is_public=True) | Q(author=user)
            ).distinct()
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PhotoCommentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PhotoCommentSerializer
    permission_classes = [IsPhotoOwnerOrAdmin]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            return PhotoComment.objects.all()
        else:
            return PhotoComment.objects.filter(author=user)


# Photo Like API Views
class PhotoLikeListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = PhotoLikeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['photo', 'user']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            return PhotoLike.objects.all()
        elif user.role in ['aamil', 'moze_coordinator']:
            if hasattr(user, 'managed_mozes'):
                return PhotoLike.objects.filter(
                    Q(photo__moze__in=user.managed_mozes.all()) | Q(photo__is_public=True)
                ).distinct()
            else:
                return PhotoLike.objects.filter(photo__is_public=True)
        else:
            return PhotoLike.objects.filter(
                Q(photo__is_public=True) | Q(user=user)
            ).distinct()
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PhotoLikeDetailAPIView(generics.RetrieveDestroyAPIView):
    serializer_class = PhotoLikeSerializer
    permission_classes = [IsPhotoOwnerOrAdmin]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            return PhotoLike.objects.all()
        else:
            return PhotoLike.objects.filter(user=user)


# Photo Tag API Views
class PhotoTagListCreateAPIView(generics.ListCreateAPIView):
    queryset = PhotoTag.objects.all()
    serializer_class = PhotoTagSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsPhotoStaffOrAdmin()]
        return [permissions.IsAuthenticated()]


class PhotoTagDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PhotoTag.objects.all()
    serializer_class = PhotoTagSerializer
    permission_classes = [IsPhotoStaffOrAdmin]


# Search API Views
class PhotoSearchAPIView(generics.ListAPIView):
    serializer_class = PhotoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering = ['-created_at']
    
    def get_queryset(self):
        # Use PhotoAccessMixin logic
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            queryset = Photo.objects.all()
        elif user.role in ['aamil', 'moze_coordinator']:
            if hasattr(user, 'managed_mozes'):
                queryset = Photo.objects.filter(
                    Q(moze__in=user.managed_mozes.all()) | Q(is_public=True)
                ).distinct()
            else:
                queryset = Photo.objects.filter(is_public=True)
        else:
            queryset = Photo.objects.filter(
                Q(is_public=True) | Q(uploaded_by=user)
            ).distinct()
        
        # Apply search filters from query params
        title = self.request.query_params.get('title')
        description = self.request.query_params.get('description')
        subject_tag = self.request.query_params.get('subject_tag')
        category = self.request.query_params.get('category')
        photographer = self.request.query_params.get('photographer')
        location = self.request.query_params.get('location')
        moze_id = self.request.query_params.get('moze_id')
        uploaded_by = self.request.query_params.get('uploaded_by')
        is_public = self.request.query_params.get('is_public')
        is_featured = self.request.query_params.get('is_featured')
        event_date_from = self.request.query_params.get('event_date_from')
        event_date_to = self.request.query_params.get('event_date_to')
        upload_date_from = self.request.query_params.get('upload_date_from')
        upload_date_to = self.request.query_params.get('upload_date_to')
        has_comments = self.request.query_params.get('has_comments')
        has_likes = self.request.query_params.get('has_likes')
        tag_names = self.request.query_params.getlist('tag_names')
        
        if title:
            queryset = queryset.filter(title__icontains=title)
        if description:
            queryset = queryset.filter(description__icontains=description)
        if subject_tag:
            queryset = queryset.filter(subject_tag__icontains=subject_tag)
        if category:
            queryset = queryset.filter(category=category)
        if photographer:
            queryset = queryset.filter(photographer__icontains=photographer)
        if location:
            queryset = queryset.filter(location__icontains=location)
        if moze_id:
            queryset = queryset.filter(moze_id=moze_id)
        if uploaded_by:
            queryset = queryset.filter(
                Q(uploaded_by__first_name__icontains=uploaded_by) |
                Q(uploaded_by__last_name__icontains=uploaded_by) |
                Q(uploaded_by__username__icontains=uploaded_by)
            )
        if is_public is not None:
            queryset = queryset.filter(is_public=is_public.lower() == 'true')
        if is_featured is not None:
            queryset = queryset.filter(is_featured=is_featured.lower() == 'true')
        if event_date_from:
            queryset = queryset.filter(event_date__gte=event_date_from)
        if event_date_to:
            queryset = queryset.filter(event_date__lte=event_date_to)
        if upload_date_from:
            queryset = queryset.filter(created_at__gte=upload_date_from)
        if upload_date_to:
            queryset = queryset.filter(created_at__lte=upload_date_to)
        if has_comments is not None:
            has_comm = has_comments.lower() == 'true'
            if has_comm:
                queryset = queryset.filter(comments__isnull=False).distinct()
            else:
                queryset = queryset.filter(comments__isnull=True)
        if has_likes is not None:
            has_like = has_likes.lower() == 'true'
            if has_like:
                queryset = queryset.filter(likes__isnull=False).distinct()
            else:
                queryset = queryset.filter(likes__isnull=True)
        if tag_names:
            queryset = queryset.filter(tags__name__in=tag_names).distinct()
        
        return queryset.distinct().order_by('-created_at')


# Special API Views
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def toggle_like_api(request, photo_id):
    """
    API endpoint for toggling photo likes
    """
    try:
        photo = Photo.objects.get(id=photo_id)
    except Photo.DoesNotExist:
        return Response(
            {'error': 'Photo not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if user can access this photo
    user = request.user
    if not photo.is_public:
        if not (user.is_admin or 
                (hasattr(user, 'managed_mozes') and photo.moze in user.managed_mozes.all()) or
                user.role in ['aamil', 'moze_coordinator']):
            return Response(
                {'error': 'You do not have permission to like this photo'}, 
                status=status.HTTP_403_FORBIDDEN
            )
    
    # Toggle like
    like, created = PhotoLike.objects.get_or_create(
        photo=photo, user=user
    )
    
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    
    return Response({
        'liked': liked,
        'likes_count': photo.likes.count()
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def bulk_photo_update_api(request):
    """
    API endpoint for bulk photo operations
    """
    serializer = BulkPhotoUpdateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    photo_ids = data['photo_ids']
    action = data['action']
    
    # Get photos user can modify
    user = request.user
    if user.is_admin or user.is_superuser:
        photos = Photo.objects.filter(id__in=photo_ids)
    elif user.role in ['aamil', 'moze_coordinator']:
        if hasattr(user, 'managed_mozes'):
            photos = Photo.objects.filter(
                id__in=photo_ids,
                moze__in=user.managed_mozes.all()
            )
        else:
            photos = Photo.objects.none()
    else:
        photos = Photo.objects.filter(id__in=photo_ids, uploaded_by=user)
    
    if not photos.exists():
        return Response(
            {'error': 'No photos found or permission denied'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    updated_count = 0
    
    # Perform bulk action
    if action == 'set_public':
        updated_count = photos.update(is_public=True)
    elif action == 'set_private':
        updated_count = photos.update(is_public=False)
    elif action == 'set_featured':
        updated_count = photos.update(is_featured=True)
    elif action == 'unset_featured':
        updated_count = photos.update(is_featured=False)
    elif action == 'add_to_album':
        album_id = data.get('album_id')
        try:
            album = PhotoAlbum.objects.get(id=album_id)
            for photo in photos:
                album.photos.add(photo)
            updated_count = photos.count()
        except PhotoAlbum.DoesNotExist:
            return Response(
                {'error': 'Album not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    elif action == 'remove_from_album':
        album_id = data.get('album_id')
        try:
            album = PhotoAlbum.objects.get(id=album_id)
            for photo in photos:
                album.photos.remove(photo)
            updated_count = photos.count()
        except PhotoAlbum.DoesNotExist:
            return Response(
                {'error': 'Album not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    elif action == 'add_tags':
        tag_ids = data.get('tag_ids', [])
        tags = PhotoTag.objects.filter(id__in=tag_ids)
        for photo in photos:
            photo.tags.add(*tags)
        updated_count = photos.count()
    elif action == 'remove_tags':
        tag_ids = data.get('tag_ids', [])
        tags = PhotoTag.objects.filter(id__in=tag_ids)
        for photo in photos:
            photo.tags.remove(*tags)
        updated_count = photos.count()
    elif action == 'delete':
        # Delete image files
        for photo in photos:
            if photo.image:
                try:
                    default_storage.delete(photo.image.name)
                except Exception:
                    pass
        updated_count = photos.count()
        photos.delete()
    
    return Response({
        'message': f'Successfully {action} {updated_count} photos',
        'updated_count': updated_count
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def bulk_photo_upload_api(request):
    """
    API endpoint for bulk photo upload
    """
    serializer = PhotoUploadSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    images = data['images']
    moze = data['moze_id']
    album = data.get('album_id')
    
    # Check permissions
    user = request.user
    if not (user.is_admin or 
            (hasattr(user, 'managed_mozes') and moze in user.managed_mozes.all()) or
            user.role in ['aamil', 'moze_coordinator']):
        return Response(
            {'error': 'You do not have permission to upload to this Moze'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Create photos
    created_photos = []
    tag_ids = data.get('tag_ids', [])
    tags = PhotoTag.objects.filter(id__in=tag_ids) if tag_ids else []
    
    for i, image in enumerate(images):
        photo_data = {
            'image': image,
            'title': data.get('title', f'Photo {i+1}'),
            'subject_tag': data['subject_tag'],
            'moze': moze,
            'uploaded_by': user,
            'category': data['category'],
            'location': data.get('location'),
            'event_date': data.get('event_date'),
            'photographer': data.get('photographer'),
            'is_public': data['is_public']
        }
        
        photo = Photo.objects.create(**photo_data)
        
        # Add tags
        if tags:
            photo.tags.add(*tags)
        
        # Add to album
        if album:
            album.photos.add(photo)
        
        created_photos.append(photo)
    
    # Return created photos
    serializer = PhotoSerializer(created_photos, many=True, context={'request': request})
    return Response({
        'message': f'Successfully uploaded {len(created_photos)} photos',
        'photos': serializer.data
    }, status=status.HTTP_201_CREATED)


# Statistics API Views
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsPhotoStaffOrAdmin])
def photo_stats_api(request):
    """Get photo statistics"""
    user = request.user
    
    # Base queryset based on user role
    if user.is_admin or user.is_superuser:
        photos = Photo.objects.all()
        albums = PhotoAlbum.objects.all()
        comments = PhotoComment.objects.all()
        likes = PhotoLike.objects.all()
    elif user.role in ['aamil', 'moze_coordinator']:
        if hasattr(user, 'managed_mozes'):
            photos = Photo.objects.filter(moze__in=user.managed_mozes.all())
            albums = PhotoAlbum.objects.filter(moze__in=user.managed_mozes.all())
            comments = PhotoComment.objects.filter(photo__moze__in=user.managed_mozes.all())
            likes = PhotoLike.objects.filter(photo__moze__in=user.managed_mozes.all())
        else:
            photos = Photo.objects.none()
            albums = PhotoAlbum.objects.none()
            comments = PhotoComment.objects.none()
            likes = PhotoLike.objects.none()
    else:
        photos = Photo.objects.filter(uploaded_by=user)
        albums = PhotoAlbum.objects.filter(created_by=user)
        comments = PhotoComment.objects.filter(photo__uploaded_by=user)
        likes = PhotoLike.objects.filter(photo__uploaded_by=user)
    
    # Calculate stats
    total_photos = photos.count()
    total_albums = albums.count()
    total_comments = comments.count()
    total_likes = likes.count()
    
    # Photos by category
    photos_by_category = dict(
        photos.values_list('category')
        .annotate(count=Count('id'))
    )
    
    # Photos by moze
    photos_by_moze = dict(
        photos.values_list('moze__name')
        .annotate(count=Count('id'))
    )
    
    # Recent uploads
    recent_uploads = list(
        photos.order_by('-created_at')[:5]
        .values('id', 'title', 'created_at', 'uploaded_by__first_name', 'uploaded_by__last_name')
    )
    
    # Popular photos (most liked)
    popular_photos = list(
        photos.annotate(like_count=Count('likes'))
        .order_by('-like_count')[:5]
        .values('id', 'title', 'like_count')
    )
    
    # Storage usage
    total_size = photos.filter(file_size__isnull=False).aggregate(
        total=Sum('file_size')
    )['total'] or 0
    storage_usage_mb = round(total_size / (1024 * 1024), 2)
    
    # Average file size
    avg_size = photos.filter(file_size__isnull=False).aggregate(
        avg=Avg('file_size')
    )['avg'] or 0
    average_file_size_mb = round(avg_size / (1024 * 1024), 2)
    
    stats = {
        'total_photos': total_photos,
        'total_albums': total_albums,
        'total_comments': total_comments,
        'total_likes': total_likes,
        'photos_by_category': photos_by_category,
        'photos_by_moze': photos_by_moze,
        'recent_uploads': recent_uploads,
        'popular_photos': popular_photos,
        'storage_usage_mb': storage_usage_mb,
        'average_file_size_mb': average_file_size_mb
    }
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsPhotoStaffOrAdmin])
def album_stats_api(request):
    """Get album statistics"""
    user = request.user
    
    # Base queryset based on user role
    if user.is_admin or user.is_superuser:
        albums = PhotoAlbum.objects.all()
    elif user.role in ['aamil', 'moze_coordinator']:
        if hasattr(user, 'managed_mozes'):
            albums = PhotoAlbum.objects.filter(moze__in=user.managed_mozes.all())
        else:
            albums = PhotoAlbum.objects.none()
    else:
        albums = PhotoAlbum.objects.filter(created_by=user)
    
    # Calculate stats
    total_albums = albums.count()
    public_albums = albums.filter(is_public=True).count()
    private_albums = total_albums - public_albums
    
    # Albums by moze
    albums_by_moze = dict(
        albums.values_list('moze__name')
        .annotate(count=Count('id'))
    )
    
    # Largest albums
    largest_albums = list(
        albums.annotate(photo_count=Count('photos'))
        .order_by('-photo_count')[:5]
        .values('id', 'name', 'photo_count')
    )
    
    # Recent albums
    recent_albums = list(
        albums.order_by('-created_at')[:5]
        .values('id', 'name', 'created_at', 'created_by__first_name', 'created_by__last_name')
    )
    
    # Average photos per album
    avg_photos = albums.annotate(photo_count=Count('photos')).aggregate(
        avg=Avg('photo_count')
    )['avg'] or 0
    
    stats = {
        'total_albums': total_albums,
        'public_albums': public_albums,
        'private_albums': private_albums,
        'albums_by_moze': albums_by_moze,
        'largest_albums': largest_albums,
        'recent_albums': recent_albums,
        'average_photos_per_album': round(avg_photos, 2)
    }
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def photos_dashboard_api(request):
    """Get comprehensive dashboard data for photos app"""
    user = request.user
    
    if not user.is_authenticated:
        raise PermissionDenied("Authentication required.")
    
    dashboard_data = {}
    
    try:
        # Role-specific dashboard data
        if user.is_admin or user.role in ['aamil', 'moze_coordinator']:
            # Staff dashboard - compute stats directly
            if user.is_admin or user.is_superuser:
                photos = Photo.objects.all()
                albums = PhotoAlbum.objects.all()
                comments = PhotoComment.objects.all()
                likes = PhotoLike.objects.all()
            else:
                if hasattr(user, 'managed_mozes'):
                    photos = Photo.objects.filter(moze__in=user.managed_mozes.all())
                    albums = PhotoAlbum.objects.filter(moze__in=user.managed_mozes.all())
                    comments = PhotoComment.objects.filter(photo__moze__in=user.managed_mozes.all())
                    likes = PhotoLike.objects.filter(photo__moze__in=user.managed_mozes.all())
                else:
                    photos = Photo.objects.none()
                    albums = PhotoAlbum.objects.none()
                    comments = PhotoComment.objects.none()
                    likes = PhotoLike.objects.none()
            
            # Photo stats
            dashboard_data['photo_stats'] = {
                'total_photos': photos.count(),
                'public_photos': photos.filter(is_public=True).count(),
                'featured_photos': photos.filter(is_featured=True).count(),
                'photos_this_month': photos.filter(
                    created_at__gte=timezone.now().replace(day=1)
                ).count(),
                'total_storage_mb': round(
                    (photos.filter(file_size__isnull=False).aggregate(
                        total=Sum('file_size')
                    )['total'] or 0) / (1024 * 1024), 2
                )
            }
            
            # Album stats
            dashboard_data['album_stats'] = {
                'total_albums': albums.count(),
                'public_albums': albums.filter(is_public=True).count(),
                'albums_this_month': albums.filter(
                    created_at__gte=timezone.now().replace(day=1)
                ).count(),
                'average_photos_per_album': round(
                    albums.annotate(photo_count=Count('photos')).aggregate(
                        avg=Avg('photo_count')
                    )['avg'] or 0, 2
                )
            }
            
            # Engagement stats
            dashboard_data['engagement_stats'] = {
                'total_comments': comments.count(),
                'total_likes': likes.count(),
                'comments_this_week': comments.filter(
                    created_at__gte=timezone.now() - timedelta(days=7)
                ).count(),
                'likes_this_week': likes.filter(
                    created_at__gte=timezone.now() - timedelta(days=7)
                ).count()
            }
            
            # Recent activities
            dashboard_data['recent_photos'] = PhotoSerializer(
                photos.order_by('-created_at')[:6],
                many=True, context={'request': request}
            ).data
            
            dashboard_data['recent_albums'] = PhotoAlbumSerializer(
                albums.order_by('-created_at')[:4],
                many=True, context={'request': request}
            ).data
            
        else:
            # Regular user dashboard
            user_photos = Photo.objects.filter(uploaded_by=user)
            user_albums = PhotoAlbum.objects.filter(created_by=user)
            user_comments = PhotoComment.objects.filter(author=user)
            user_likes = PhotoLike.objects.filter(user=user)
            
            dashboard_data['my_photos'] = PhotoSerializer(
                user_photos.order_by('-created_at')[:10],
                many=True, context={'request': request}
            ).data
            
            dashboard_data['my_albums'] = PhotoAlbumSerializer(
                user_albums.order_by('-created_at')[:6],
                many=True, context={'request': request}
            ).data
            
            dashboard_data['my_stats'] = {
                'total_photos': user_photos.count(),
                'total_albums': user_albums.count(),
                'total_comments': user_comments.count(),
                'total_likes': user_likes.count(),
                'photos_this_month': user_photos.filter(
                    created_at__gte=timezone.now().replace(day=1)
                ).count()
            }
        
        # Common data for all users
        dashboard_data['featured_photos'] = PhotoSerializer(
            Photo.objects.filter(is_public=True, is_featured=True).order_by('-created_at')[:4],
            many=True, context={'request': request}
        ).data
        
        dashboard_data['public_albums'] = PhotoAlbumSerializer(
            PhotoAlbum.objects.filter(is_public=True).order_by('-created_at')[:3],
            many=True, context={'request': request}
        ).data
        
    except Exception as e:
        dashboard_data['error'] = str(e)
    
    return Response(dashboard_data)