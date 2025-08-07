"""
URL Configuration for the Photos API
"""
from django.urls import path
from . import api_views

urlpatterns = [
    # Dashboard
    path('dashboard/', api_views.photos_dashboard_api, name='photos_dashboard_api'),
    
    # Photo Management
    path('photos/', api_views.PhotoListCreateAPIView.as_view(), name='photo_list_create'),
    path('photos/<int:pk>/', api_views.PhotoDetailAPIView.as_view(), name='photo_detail'),
    path('photos/search/', api_views.PhotoSearchAPIView.as_view(), name='photo_search'),
    
    # Photo Albums
    path('albums/', api_views.PhotoAlbumListCreateAPIView.as_view(), name='album_list_create'),
    path('albums/<int:pk>/', api_views.PhotoAlbumDetailAPIView.as_view(), name='album_detail'),
    
    # Photo Comments
    path('comments/', api_views.PhotoCommentListCreateAPIView.as_view(), name='comment_list_create'),
    path('comments/<int:pk>/', api_views.PhotoCommentDetailAPIView.as_view(), name='comment_detail'),
    
    # Photo Likes
    path('likes/', api_views.PhotoLikeListCreateAPIView.as_view(), name='like_list_create'),
    path('likes/<int:pk>/', api_views.PhotoLikeDetailAPIView.as_view(), name='like_detail'),
    path('photos/<int:photo_id>/toggle-like/', api_views.toggle_like_api, name='toggle_like_api'),
    
    # Photo Tags
    path('tags/', api_views.PhotoTagListCreateAPIView.as_view(), name='tag_list_create'),
    path('tags/<int:pk>/', api_views.PhotoTagDetailAPIView.as_view(), name='tag_detail'),
    
    # Bulk Operations
    path('photos/bulk-update/', api_views.bulk_photo_update_api, name='bulk_photo_update_api'),
    path('photos/bulk-upload/', api_views.bulk_photo_upload_api, name='bulk_photo_upload_api'),
    
    # Statistics
    path('stats/photos/', api_views.photo_stats_api, name='photo_stats_api'),
    path('stats/albums/', api_views.album_stats_api, name='album_stats_api'),
]