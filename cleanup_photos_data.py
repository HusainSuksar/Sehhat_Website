#!/usr/bin/env python3
"""
Cleanup script to fix corrupted photo data
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

from photos.models import Photo, PhotoAlbum, PhotoComment, PhotoLike
from django.db import transaction

def cleanup_photos_data():
    """Clean up any corrupted photo data"""
    print("🧹 Starting photos data cleanup...")
    
    try:
        with transaction.atomic():
            # Check for any PhotoComment records with invalid photo references
            print("Checking PhotoComment records...")
            invalid_comments = []
            for comment in PhotoComment.objects.all():
                try:
                    # Try to access the photo to see if it's valid
                    photo = comment.photo
                    if not isinstance(photo, Photo):
                        invalid_comments.append(comment.id)
                except Exception:
                    invalid_comments.append(comment.id)
            
            if invalid_comments:
                print(f"Found {len(invalid_comments)} invalid PhotoComment records")
                PhotoComment.objects.filter(id__in=invalid_comments).delete()
                print(f"Deleted {len(invalid_comments)} invalid PhotoComment records")
            else:
                print("No invalid PhotoComment records found")
            
            # Check for any PhotoLike records with invalid photo references
            print("Checking PhotoLike records...")
            invalid_likes = []
            for like in PhotoLike.objects.all():
                try:
                    # Try to access the photo to see if it's valid
                    photo = like.photo
                    if not isinstance(photo, Photo):
                        invalid_likes.append(like.id)
                except Exception:
                    invalid_likes.append(like.id)
            
            if invalid_likes:
                print(f"Found {len(invalid_likes)} invalid PhotoLike records")
                PhotoLike.objects.filter(id__in=invalid_likes).delete()
                print(f"Deleted {len(invalid_likes)} invalid PhotoLike records")
            else:
                print("No invalid PhotoLike records found")
            
            # Check for any Photo records with invalid moze references
            print("Checking Photo records...")
            invalid_photos = []
            for photo in Photo.objects.all():
                try:
                    # Try to access the moze to see if it's valid
                    moze = photo.moze
                    if not hasattr(moze, 'name'):
                        invalid_photos.append(photo.id)
                except Exception:
                    invalid_photos.append(photo.id)
            
            if invalid_photos:
                print(f"Found {len(invalid_photos)} invalid Photo records")
                Photo.objects.filter(id__in=invalid_photos).delete()
                print(f"Deleted {len(invalid_photos)} invalid Photo records")
            else:
                print("No invalid Photo records found")
            
            # Check for any PhotoAlbum records with invalid moze references
            print("Checking PhotoAlbum records...")
            invalid_albums = []
            for album in PhotoAlbum.objects.all():
                try:
                    # Try to access the moze to see if it's valid
                    moze = album.moze
                    if not hasattr(moze, 'name'):
                        invalid_albums.append(album.id)
                except Exception:
                    invalid_albums.append(album.id)
            
            if invalid_albums:
                print(f"Found {len(invalid_albums)} invalid PhotoAlbum records")
                PhotoAlbum.objects.filter(id__in=invalid_albums).delete()
                print(f"Deleted {len(invalid_albums)} invalid PhotoAlbum records")
            else:
                print("No invalid PhotoAlbum records found")
            
            print("✅ Photos data cleanup completed successfully!")
            
    except Exception as e:
        print(f"❌ Error during photos data cleanup: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    cleanup_photos_data()