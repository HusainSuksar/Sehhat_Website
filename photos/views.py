from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse, Http404
from django.db.models import Q, Count
from django.utils import timezone
from django.core.paginator import Paginator
from django.db import transaction
from django.conf import settings
import json
import os
from datetime import datetime, timedelta

from .models import PhotoAlbum, Photo, PhotoTag, PhotoComment, PhotoLike
from accounts.models import User
from moze.models import Moze


@login_required
def dashboard(request):
    """Photos dashboard with gallery overview"""
    user = request.user
    
    # Base queryset based on user role
    if user.role == 'admin':
        albums = PhotoAlbum.objects.all()
        photos = Photo.objects.all()
        can_manage = True
    elif user.role == 'aamil' or user.role == 'moze_coordinator':
        # Can see albums for their moze and albums they created
        albums = PhotoAlbum.objects.filter(
            Q(moze__aamil=user) | Q(moze__moze_coordinator=user) | Q(created_by=user)
        )
        photos = Photo.objects.filter(
            Q(moze__aamil=user) | Q(moze__moze_coordinator=user) | Q(uploaded_by=user)
        )
        can_manage = True
    else:
        # Regular users can see public albums and their own photos
        albums = PhotoAlbum.objects.filter(
            Q(is_public=True) | Q(created_by=user)
        )
        photos = Photo.objects.filter(
            Q(is_public=True) | Q(uploaded_by=user)
        )
        can_manage = False
    
    # Statistics
    total_albums = albums.count()
    total_photos = photos.count()
    public_albums = albums.filter(is_public=True).count()
    recent_uploads = photos.filter(
        created_at__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    # Recent albums
    recent_albums = albums.select_related(
        'created_by', 'moze'
    ).prefetch_related('photos').order_by('-created_at')[:8]
    
    # Recent photos
    recent_photos = photos.select_related(
        'uploaded_by', 'moze'
    ).order_by('-created_at')[:12]
    
    # Popular albums (by photo count)
    popular_albums = albums.annotate(
        photo_count=Count('photos')
    ).order_by('-photo_count')[:6]
    
    # Monthly upload trends
    monthly_stats = []
    for i in range(6):
        month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
        month_photos = photos.filter(
            created_at__year=month_start.year,
            created_at__month=month_start.month
        ).count()
        monthly_stats.append({
            'month': month_start.strftime('%b %Y'),
            'count': month_photos
        })
    
    # Tag cloud
    popular_tags = PhotoTag.objects.annotate(
        usage_count=Count('photos')
    ).order_by('-usage_count')[:10]
    
    # User's favorites
    my_favorites = Photo.objects.filter(
        likes__user=user
    )[:6]
    
    context = {
        'total_albums': total_albums,
        'total_photos': total_photos,
        'public_albums': public_albums,
        'recent_uploads': recent_uploads,
        'recent_albums': recent_albums,
        'recent_photos': recent_photos,
        'popular_albums': popular_albums,
        'monthly_stats': monthly_stats[::-1],
        'popular_tags': popular_tags,
        'my_favorites': my_favorites,
        'can_manage': can_manage,
        'user_role': user.get_role_display(),
    }
    
    return render(request, 'photos/dashboard.html', context)


class PhotoAlbumListView(LoginRequiredMixin, ListView):
    """List all photo albums with filtering"""
    model = PhotoAlbum
    template_name = 'photos/album_list.html'
    context_object_name = 'albums'
    paginate_by = 12
    
    def get_queryset(self):
        user = self.request.user
        
        # Base queryset based on user role
        if user.role == 'admin':
            queryset = PhotoAlbum.objects.all()
        elif user.role == 'aamil' or user.role == 'moze_coordinator':
            queryset = PhotoAlbum.objects.filter(
                Q(moze__aamil=user) | Q(moze__moze_coordinator=user) | Q(created_by=user)
            )
        else:
            queryset = PhotoAlbum.objects.filter(
                Q(is_public=True) | Q(created_by=user)
            )
        
        # Apply filters
        moze_filter = self.request.GET.get('moze')
        if moze_filter:
            queryset = queryset.filter(moze_id=moze_filter)
        
        privacy_filter = self.request.GET.get('privacy')
        if privacy_filter == 'public':
            queryset = queryset.filter(is_public=True)
        elif privacy_filter == 'private':
            queryset = queryset.filter(is_public=False)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(created_by__first_name__icontains=search) |
                Q(created_by__last_name__icontains=search)
            )
        
        return queryset.select_related('created_by', 'moze').prefetch_related(
            'photos'
        ).annotate(photo_count=Count('photos')).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if user.role == 'admin' or user.role == 'aamil' or user.role == 'moze_coordinator':
            context['moze_options'] = Moze.objects.filter(is_active=True)
        
        context['current_filters'] = {
            'moze': self.request.GET.get('moze', ''),
            'privacy': self.request.GET.get('privacy', ''),
            'search': self.request.GET.get('search', ''),
        }
        return context


class PhotoAlbumDetailView(LoginRequiredMixin, DetailView):
    """Detailed view of a photo album"""
    model = PhotoAlbum
    template_name = 'photos/album_detail.html'
    context_object_name = 'album'
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return PhotoAlbum.objects.all()
        elif user.role == 'aamil' or user.role == 'moze_coordinator':
            return PhotoAlbum.objects.filter(
                Q(moze__aamil=user) | Q(moze__moze_coordinator=user) | Q(created_by=user)
            )
        else:
            return PhotoAlbum.objects.filter(
                Q(is_public=True) | Q(created_by=user)
            )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        album = self.object
        user = self.request.user
        
        # Photos in album
        photos = album.photos.select_related('uploaded_by').prefetch_related(
            'tags', 'comments__user', 'likes__user'
        ).order_by('-created_at')
        
        # Pagination for photos
        paginator = Paginator(photos, 20)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context['photos'] = page_obj
        context['total_photos'] = photos.count()
        
        # Comments on album
        context['comments'] = album.comments.select_related('user').order_by('-created_at')
        
        # Permission checks
        context['can_edit'] = (
            user == album.created_by or 
            user.role == 'admin' or 
            (user.role == 'aamil' and album.moze and album.moze.aamil == user) or
            (user.role == 'moze_coordinator' and album.moze and album.moze.moze_coordinator == user)
        )
        
        context['can_upload'] = context['can_edit'] or album.allow_uploads
        
        # Tags
        context['all_tags'] = PhotoTag.objects.filter(
            photos__album=album
        ).distinct()
        
        return context


class PhotoAlbumCreateView(LoginRequiredMixin, CreateView):
    """Create a new photo album"""
    model = PhotoAlbum
    template_name = 'photos/album_form.html'
    fields = ['name', 'description', 'moze', 'is_public', 'allow_uploads']
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, f'Album "{self.object.name}" created successfully.')
        return response
    
    def get_success_url(self):
        return reverse_lazy('photos:album_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if user.role == 'admin':
            context['moze_options'] = Moze.objects.filter(is_active=True)
        elif user.role == 'aamil' or user.role == 'moze_coordinator':
            context['moze_options'] = Moze.objects.filter(
                Q(aamil=user) | Q(moze_coordinator=user)
            )
        else:
            context['moze_options'] = Moze.objects.none()
        
        return context


class PhotoDetailView(LoginRequiredMixin, DetailView):
    """Detailed view of a single photo"""
    model = Photo
    template_name = 'photos/photo_detail.html'
    context_object_name = 'photo'
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Photo.objects.all()
        elif user.role == 'aamil' or user.role == 'moze_coordinator':
            return Photo.objects.filter(
                Q(moze__aamil=user) | Q(moze__moze_coordinator=user) | Q(uploaded_by=user)
            )
        else:
            return Photo.objects.filter(
                Q(is_public=True) | Q(uploaded_by=user)
            )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        photo = self.object
        user = self.request.user
        
        # Comments
        context['comments'] = photo.comments.select_related('user').order_by('-created_at')
        
        # Likes
        context['likes_count'] = photo.likes.count()
        context['user_liked'] = photo.likes.filter(user=user).exists()
        
        # Related photos with same tags
        context['related_photos'] = Photo.objects.filter(
            tags__in=photo.tags.all()
        ).exclude(id=photo.id).distinct().order_by('?')[:6]
        
        # Permission checks
        context['can_edit'] = (
            user == photo.uploaded_by or 
            user.role == 'admin' or 
            (user.role == 'aamil' and photo.moze and photo.moze.aamil == user) or
            (user.role == 'moze_coordinator' and photo.moze and photo.moze.moze_coordinator == user)
        )
        
        # Navigation within related photos by moze
        moze_photos = list(Photo.objects.filter(moze=photo.moze).values_list('id', flat=True).order_by('created_at'))
        try:
            current_index = moze_photos.index(photo.id)
            context['prev_photo_id'] = moze_photos[current_index - 1] if current_index > 0 else None
            context['next_photo_id'] = moze_photos[current_index + 1] if current_index < len(moze_photos) - 1 else None
        except (ValueError, IndexError):
            context['prev_photo_id'] = None
            context['next_photo_id'] = None
        
        return context


@login_required
def upload_photos(request, album_id):
    """Upload photos to an album"""
    album = get_object_or_404(PhotoAlbum, id=album_id)
    user = request.user
    
    # Check permissions
    can_upload = (
        user == album.created_by or 
        user.role == 'admin' or 
        album.allow_uploads or
        (user.role == 'aamil' and album.moze and album.moze.aamil == user) or
        (user.role == 'moze_coordinator' and album.moze and album.moze.moze_coordinator == user)
    )
    
    if not can_upload:
        messages.error(request, "You don't have permission to upload to this album.")
        return redirect('photos:album_detail', pk=album_id)
    
    if request.method == 'POST':
        uploaded_files = request.FILES.getlist('photos')
        titles = request.POST.getlist('titles[]')
        descriptions = request.POST.getlist('descriptions[]')
        tag_names = request.POST.getlist('tags[]')
        
        uploaded_count = 0
        
        with transaction.atomic():
            for i, uploaded_file in enumerate(uploaded_files):
                try:
                    # Create photo
                    photo = Photo.objects.create(
                        image=uploaded_file,
                        title=titles[i] if i < len(titles) else f'Photo {i+1}',
                        description=descriptions[i] if i < len(descriptions) else '',
                        subject_tag=f'album_{album.id}',
                        uploaded_by=user,
                        moze=album.moze
                    )
                    
                    # Add tags
                    if i < len(tag_names) and tag_names[i]:
                        tag_list = [tag.strip() for tag in tag_names[i].split(',')]
                        for tag_name in tag_list:
                            if tag_name:
                                tag, created = PhotoTag.objects.get_or_create(name=tag_name.lower())
                                photo.tags.add(tag)
                    
                    uploaded_count += 1
                    
                except Exception as e:
                    messages.error(request, f'Error uploading file {i+1}: {str(e)}')
        
        if uploaded_count > 0:
            messages.success(request, f'{uploaded_count} photo(s) uploaded successfully.')
        
        return redirect('photos:album_detail', pk=album_id)
    
    context = {
        'album': album,
    }
    
    return render(request, 'photos/upload_photos.html', context)


@login_required
def add_photo_comment(request, photo_id):
    """Add a comment to a photo"""
    if request.method == 'POST':
        photo = get_object_or_404(Photo, id=photo_id)
        user = request.user
        
        # Check if user can view this photo
        can_view = (
            photo.is_public or
            user == photo.uploaded_by or
            user.role == 'admin' or
            (photo.moze and (
                (user.role == 'aamil' and photo.moze.aamil == user) or
                (user.role == 'moze_coordinator' and photo.moze.moze_coordinator == user)
            ))
        )
        
        if not can_view:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        content = request.POST.get('content', '').strip()
        if content:
            comment = PhotoComment.objects.create(
                photo=photo,
                user=user,
                content=content
            )
            
            return JsonResponse({
                'success': True,
                'comment': {
                    'id': comment.id,
                    'content': comment.content,
                    'user': comment.user.get_full_name(),
                    'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M'),
                }
            })
        
        return JsonResponse({'error': 'Comment content is required'}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def toggle_photo_like(request, photo_id):
    """Toggle like/unlike for a photo"""
    if request.method == 'POST':
        photo = get_object_or_404(Photo, id=photo_id)
        user = request.user
        
        # Check if user can view this photo
        can_view = (
            photo.is_public or
            user == photo.uploaded_by or
            user.role == 'admin' or
            (photo.moze and (
                (user.role == 'aamil' and photo.moze.aamil == user) or
                (user.role == 'moze_coordinator' and photo.moze.moze_coordinator == user)
            ))
        )
        
        if not can_view:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        like, created = PhotoLike.objects.get_or_create(
            photo=photo,
            user=user
        )
        
        if not created:
            like.delete()
            liked = False
        else:
            liked = True
        
        likes_count = photo.likes.count()
        
        return JsonResponse({
            'success': True,
            'liked': liked,
            'likes_count': likes_count
        })
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def search_photos(request):
    """Search photos and albums"""
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', 'all')  # all, albums, photos
    user = request.user
    
    results = {'albums': [], 'photos': []}
    
    if query:
        # Base queryset based on user permissions
        if user.role == 'admin':
            albums_qs = PhotoAlbum.objects.all()
            photos_qs = Photo.objects.all()
        elif user.role == 'aamil' or user.role == 'moze_coordinator':
            albums_qs = PhotoAlbum.objects.filter(
                Q(moze__aamil=user) | Q(moze__moze_coordinator=user) | Q(created_by=user)
            )
            photos_qs = Photo.objects.filter(
                Q(moze__aamil=user) | Q(moze__moze_coordinator=user) | Q(uploaded_by=user)
            )
        else:
            albums_qs = PhotoAlbum.objects.filter(
                Q(is_public=True) | Q(created_by=user)
            )
            photos_qs = Photo.objects.filter(
                Q(is_public=True) | Q(uploaded_by=user)
            )
        
        # Search albums
        if category in ['all', 'albums']:
            albums = albums_qs.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(created_by__first_name__icontains=query) |
                Q(created_by__last_name__icontains=query)
            ).select_related('created_by', 'moze').annotate(
                photo_count=Count('photos')
            )[:20]
            results['albums'] = list(albums)
        
        # Search photos
        if category in ['all', 'photos']:
            photos = photos_qs.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(tags__name__icontains=query) |
                Q(uploaded_by__first_name__icontains=query) |
                Q(uploaded_by__last_name__icontains=query)
            ).select_related('uploaded_by').distinct()[:20]
            results['photos'] = list(photos)
    
    context = {
        'query': query,
        'category': category,
        'results': results,
        'total_results': len(results['albums']) + len(results['photos']),
    }
    
    return render(request, 'photos/search_results.html', context)


@login_required
def photos_by_tag(request, tag_name):
    """Show all photos with a specific tag"""
    tag = get_object_or_404(PhotoTag, name=tag_name.lower())
    user = request.user
    
    # Base queryset based on user permissions
    if user.role == 'admin':
        photos = tag.photos.all()
    elif user.role == 'aamil' or user.role == 'moze_coordinator':
        photos = tag.photos.filter(
            Q(moze__aamil=user) | Q(moze__moze_coordinator=user) | Q(uploaded_by=user)
        )
    else:
        photos = tag.photos.filter(
            Q(is_public=True) | Q(uploaded_by=user)
        )
    
    photos = photos.select_related('uploaded_by').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(photos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tag': tag,
        'photos': page_obj,
        'total_photos': photos.count(),
    }
    
    return render(request, 'photos/photos_by_tag.html', context)


@login_required
def user_photos(request, user_id=None):
    """Show photos uploaded by a specific user"""
    if user_id:
        photo_user = get_object_or_404(User, id=user_id)
    else:
        photo_user = request.user
    
    user = request.user
    
    # Check permissions to view this user's photos
    if photo_user != user and not user.role == 'admin':
        # Can only see public photos of other users
        photos = Photo.objects.filter(
            uploaded_by=photo_user,
            is_public=True
        )
    else:
        # Can see all photos if it's your own or you're admin
        photos = Photo.objects.filter(uploaded_by=photo_user)
    
    photos = photos.select_related('album').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(photos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    total_photos = photos.count()
    total_albums = PhotoAlbum.objects.filter(created_by=photo_user).count()
    total_likes = PhotoLike.objects.filter(photo__uploaded_by=photo_user).count()
    
    context = {
        'photo_user': photo_user,
        'photos': page_obj,
        'total_photos': total_photos,
        'total_albums': total_albums,
        'total_likes': total_likes,
        'is_own_profile': photo_user == user,
    }
    
    return render(request, 'photos/user_photos.html', context)


@login_required
def export_album_data(request, album_id):
    """Export album data including photo metadata"""
    import csv
    
    album = get_object_or_404(PhotoAlbum, id=album_id)
    user = request.user
    
    # Check permissions
    can_export = (
        user == album.created_by or 
        user.role == 'admin' or 
        (user.role == 'aamil' and album.moze and album.moze.aamil == user) or
        (user.role == 'moze_coordinator' and album.moze and album.moze.moze_coordinator == user)
    )
    
    if not can_export:
        messages.error(request, "You don't have permission to export this album data.")
        return redirect('photos:album_detail', pk=album_id)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="album_{album.name}_data.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Photo ID', 'Title', 'Description', 'Subject Tag', 'Uploaded By', 'Upload Date',
        'Tags', 'Comments Count', 'Likes Count', 'File Size', 'Image URL'
    ])
    
    for photo in album.photos.select_related('uploaded_by').prefetch_related('tags', 'comments', 'likes'):
        tags = ', '.join([tag.name for tag in photo.tags.all()])
        
        writer.writerow([
            photo.id,
            photo.title,
            photo.description,
            photo.subject_tag,
            photo.uploaded_by.get_full_name(),
            photo.created_at.strftime('%Y-%m-%d %H:%M'),
            tags,
            photo.comments.count(),
            photo.likes.count(),
            photo.image.size if photo.image else 0,
            request.build_absolute_uri(photo.image.url) if photo.image else ''
        ])
    
    return response


@login_required
def bulk_delete_photos(request):
    """Bulk delete selected photos"""
    if request.method == 'POST':
        user = request.user
        photo_ids = request.POST.getlist('photo_ids[]')
        
        if not photo_ids:
            return JsonResponse({'error': 'No photos selected'}, status=400)
        
        # Get photos user can delete
        if user.role == 'admin':
            photos = Photo.objects.filter(id__in=photo_ids)
        else:
            photos = Photo.objects.filter(
                Q(id__in=photo_ids) &
                (Q(uploaded_by=user) |
                Q(moze__aamil=user) |
                Q(moze__moze_coordinator=user))
            )
        
        deleted_count = 0
        with transaction.atomic():
            for photo in photos:
                # Delete the file
                if photo.image and os.path.isfile(photo.image.path):
                    os.remove(photo.image.path)
                photo.delete()
                deleted_count += 1
        
        return JsonResponse({
            'success': True,
            'message': f'{deleted_count} photo(s) deleted successfully'
        })
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)
