from django.urls import path
from . import views

app_name = 'photos'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Album management (only existing views)
    path('albums/', views.PhotoAlbumListView.as_view(), name='album_list'),
    path('albums/<int:pk>/', views.PhotoAlbumDetailView.as_view(), name='album_detail'),
    path('albums/create/', views.PhotoAlbumCreateView.as_view(), name='album_create'),
    
    # Photo management (only existing views)
    path('photos/<int:pk>/', views.PhotoDetailView.as_view(), name='photo_detail'),
    path('photos/upload/', views.upload_photos, name='upload_photos'),
    path('photos/<int:album_id>/upload/', views.upload_photos, name='upload_to_album'),
    
    # Photo interactions (only existing views)
    path('photos/<int:photo_id>/comment/', views.add_photo_comment, name='add_comment'),
    path('photos/<int:photo_id>/like/', views.toggle_photo_like, name='toggle_like'),
    
    # Search and filtering (only existing views)
    path('search/', views.search_photos, name='search_photos'),
    path('tags/<str:tag_name>/', views.photos_by_tag, name='photos_by_tag'),
    path('users/<int:user_id>/photos/', views.user_photos, name='user_photos'),
    
    # Bulk operations (only existing views)
    path('albums/<int:album_id>/export/', views.export_album_data, name='export_album'),
    path('bulk-delete/', views.bulk_delete_photos, name='bulk_delete_photos'),
    
    # Slideshow functionality
    path('slideshow/', views.slideshow, name='slideshow'),
    path('albums/<int:album_id>/slideshow/', views.album_slideshow, name='album_slideshow'),
]
