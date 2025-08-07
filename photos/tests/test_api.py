"""
Unit tests for the Photos API
"""
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date, timedelta
from PIL import Image
import io
import json

from photos.models import Photo, PhotoAlbum, PhotoComment, PhotoLike, PhotoTag
from moze.models import Moze

User = get_user_model()


class PhotoAPITestCase(APITestCase):
    """Base test case for Photo API tests"""
    
    def setUp(self):
        """Set up test data"""
        # Create users with different roles
        self.admin_user = User.objects.create_user(
            username='admin_user',
            email='admin@test.com',
            password='testpass123',
            role='badri_mahal_admin',
            first_name='Admin',
            last_name='User'
        )
        
        self.aamil_user = User.objects.create_user(
            username='aamil_user',
            email='aamil@test.com',
            password='testpass123',
            role='aamil',
            first_name='Aamil',
            last_name='User'
        )
        
        self.coordinator_user = User.objects.create_user(
            username='coordinator_user',
            email='coordinator@test.com',
            password='testpass123',
            role='moze_coordinator',
            first_name='Coordinator',
            last_name='User'
        )
        
        self.doctor_user = User.objects.create_user(
            username='doctor_user',
            email='doctor@test.com',
            password='testpass123',
            role='doctor',
            first_name='Doctor',
            last_name='User'
        )
        
        self.student_user = User.objects.create_user(
            username='student_user',
            email='student@test.com',
            password='testpass123',
            role='student',
            first_name='Student',
            last_name='User'
        )
        
        # Create test moze
        self.moze = Moze.objects.create(
            name='Test Moze',
            location='Test Location',
            aamil=self.aamil_user,
            moze_coordinator=self.coordinator_user,
            is_active=True
        )
        
        # Create test photo tag
        self.tag = PhotoTag.objects.create(
            name='test-tag',
            description='Test tag for photos',
            color='#007bff'
        )
        
        # Create test image file
        self.test_image = self.create_test_image()
        
        # Create test photo
        self.photo = Photo.objects.create(
            image=self.test_image,
            title='Test Photo',
            description='Test photo for API testing',
            subject_tag='test',
            moze=self.moze,
            uploaded_by=self.admin_user,
            category='medical',
            is_public=True,
            is_featured=False,
            requires_permission=False
        )
        self.photo.tags.add(self.tag)
        
        # Create private photo
        self.private_photo = Photo.objects.create(
            image=self.create_test_image('private_test.jpg'),
            title='Private Photo',
            description='Private photo for testing',
            subject_tag='private',
            moze=self.moze,
            uploaded_by=self.aamil_user,
            category='team',
            is_public=False,
            is_featured=False,
            requires_permission=True
        )
        
        # Create test album
        self.album = PhotoAlbum.objects.create(
            name='Test Album',
            description='Test album for API testing',
            moze=self.moze,
            created_by=self.admin_user,
            is_public=True,
            allow_uploads=True,
            cover_photo=self.photo
        )
        self.album.photos.add(self.photo)
        
        # Create test comment
        self.comment = PhotoComment.objects.create(
            photo=self.photo,
            author=self.doctor_user,
            content='Great photo!',
            is_active=True
        )
        
        # Create test like
        self.like = PhotoLike.objects.create(
            photo=self.photo,
            user=self.student_user
        )
        
        self.client = APIClient()
    
    def create_test_image(self, filename='test.jpg'):
        """Create a test image file"""
        image = Image.new('RGB', (100, 100), color='red')
        image_file = io.BytesIO()
        image.save(image_file, format='JPEG')
        image_file.seek(0)
        
        return SimpleUploadedFile(
            filename,
            image_file.getvalue(),
            content_type='image/jpeg'
        )


class PhotoAPITests(PhotoAPITestCase):
    """Test Photo CRUD operations"""
    
    def test_list_photos_admin(self):
        """Test admin can list all photos"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('photo_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_list_photos_public_user(self):
        """Test regular user can see public photos and their own"""
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('photo_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should see only public photos
        self.assertEqual(len(response.data['results']), 1)
        self.assertTrue(response.data['results'][0]['is_public'])
    
    def test_create_photo_admin(self):
        """Test admin can create photo"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('photo_list_create')
        
        test_image = self.create_test_image('new_test.jpg')
        data = {
            'image': test_image,
            'title': 'New Test Photo',
            'description': 'New photo for testing',
            'subject_tag': 'new-test',
            'moze_id': self.moze.id,
            'category': 'event',
            'is_public': True,
            'tag_ids': [self.tag.id]
        }
        
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Photo.objects.count(), 3)
    
    def test_create_photo_unauthorized_user(self):
        """Test unauthorized user cannot create photo"""
        self.client.force_authenticate(user=self.student_user)
        url = reverse('photo_list_create')
        
        test_image = self.create_test_image('unauthorized.jpg')
        data = {
            'image': test_image,
            'title': 'Unauthorized Photo',
            'moze_id': self.moze.id,
            'subject_tag': 'unauthorized'
        }
        
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_retrieve_photo_with_computed_fields(self):
        """Test retrieving photo with computed fields"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('photo_detail', kwargs={'pk': self.photo.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('image_url', response.data)
        self.assertIn('comments_count', response.data)
        self.assertIn('likes_count', response.data)
        self.assertIn('can_edit', response.data)
        self.assertIn('can_delete', response.data)
        self.assertEqual(response.data['comments_count'], 1)
        self.assertEqual(response.data['likes_count'], 1)
    
    def test_update_photo_owner(self):
        """Test photo owner can update their photo"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('photo_detail', kwargs={'pk': self.photo.pk})
        data = {
            'title': 'Updated Photo Title',
            'description': 'Updated description'
        }
        
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.photo.refresh_from_db()
        self.assertEqual(self.photo.title, 'Updated Photo Title')
    
    def test_delete_photo_owner(self):
        """Test photo owner can delete their photo"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('photo_detail', kwargs={'pk': self.photo.pk})
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Photo.objects.filter(pk=self.photo.pk).count(), 0)


class PhotoAlbumAPITests(PhotoAPITestCase):
    """Test Photo Album CRUD operations"""
    
    def test_list_albums_admin(self):
        """Test admin can list all albums"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('album_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_album_admin(self):
        """Test admin can create album"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('album_list_create')
        data = {
            'name': 'New Test Album',
            'description': 'New album for testing',
            'moze_id': self.moze.id,
            'is_public': True,
            'allow_uploads': True
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PhotoAlbum.objects.count(), 2)
    
    def test_album_with_computed_fields(self):
        """Test album includes computed fields"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('album_detail', kwargs={'pk': self.album.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('photo_count', response.data)
        self.assertIn('latest_photos', response.data)
        self.assertIn('can_edit', response.data)
        self.assertIn('can_upload', response.data)
        self.assertEqual(response.data['photo_count'], 1)
    
    def test_update_album_creator(self):
        """Test album creator can update their album"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('album_detail', kwargs={'pk': self.album.pk})
        data = {
            'name': 'Updated Album Name',
            'description': 'Updated description'
        }
        
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.album.refresh_from_db()
        self.assertEqual(self.album.name, 'Updated Album Name')


class PhotoCommentAPITests(PhotoAPITestCase):
    """Test Photo Comment CRUD operations"""
    
    def test_list_comments_admin(self):
        """Test admin can list all comments"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('comment_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_comment_authorized_user(self):
        """Test authorized user can create comment"""
        self.client.force_authenticate(user=self.student_user)
        url = reverse('comment_list_create')
        data = {
            'photo_id': self.photo.id,
            'content': 'Nice photo!'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PhotoComment.objects.count(), 2)
    
    def test_comment_with_computed_fields(self):
        """Test comment includes computed fields"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('comment_detail', kwargs={'pk': self.comment.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('days_since_comment', response.data)
        self.assertIn('can_edit', response.data)
        self.assertIn('can_delete', response.data)
    
    def test_update_comment_author(self):
        """Test comment author can update their comment"""
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('comment_detail', kwargs={'pk': self.comment.pk})
        data = {
            'content': 'Updated comment content'
        }
        
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, 'Updated comment content')


class PhotoLikeAPITests(PhotoAPITestCase):
    """Test Photo Like operations"""
    
    def test_list_likes_admin(self):
        """Test admin can list all likes"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('like_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_like_user(self):
        """Test user can like a photo"""
        # Use a different user (admin) since student already liked in setup
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('like_list_create')
        data = {
            'photo_id': self.photo.id
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PhotoLike.objects.count(), 2)
    
    def test_toggle_like_api(self):
        """Test toggle like API functionality"""
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('toggle_like_api', kwargs={'photo_id': self.photo.pk})
        
        # First toggle - should create like
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['liked'])
        self.assertEqual(response.data['likes_count'], 2)  # Original + new
        
        # Second toggle - should remove like
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['liked'])
        self.assertEqual(response.data['likes_count'], 1)  # Back to original


class PhotoTagAPITests(PhotoAPITestCase):
    """Test Photo Tag CRUD operations"""
    
    def test_list_tags_user(self):
        """Test user can list all tags"""
        self.client.force_authenticate(user=self.student_user)
        url = reverse('tag_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_tag_admin(self):
        """Test admin can create tag"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('tag_list_create')
        data = {
            'name': 'new-tag',
            'description': 'New tag for testing',
            'color': '#ff0000'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PhotoTag.objects.count(), 2)
    
    def test_create_tag_unauthorized(self):
        """Test unauthorized user cannot create tag"""
        self.client.force_authenticate(user=self.student_user)
        url = reverse('tag_list_create')
        data = {
            'name': 'unauthorized-tag',
            'description': 'Unauthorized tag'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_tag_with_computed_fields(self):
        """Test tag includes computed fields"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('tag_detail', kwargs={'pk': self.tag.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('photo_count', response.data)
        self.assertEqual(response.data['photo_count'], 1)


class PhotoSearchAPITests(PhotoAPITestCase):
    """Test photo search functionality"""
    
    def test_search_photos_by_title(self):
        """Test searching photos by title"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('photo_search')
        response = self.client.get(url, {'title': 'Test'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertIn('Test', response.data['results'][0]['title'])
    
    def test_search_photos_by_category(self):
        """Test searching photos by category"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('photo_search')
        response = self.client.get(url, {'category': 'medical'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['category'], 'medical')
    
    def test_search_photos_by_moze(self):
        """Test searching photos by moze"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('photo_search')
        response = self.client.get(url, {'moze_id': self.moze.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_search_photos_by_public_status(self):
        """Test searching photos by public status"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('photo_search')
        
        # Search for public photos
        response = self.client.get(url, {'is_public': 'true'})
        self.assertEqual(len(response.data['results']), 1)
        
        # Search for private photos
        response = self.client.get(url, {'is_public': 'false'})
        self.assertEqual(len(response.data['results']), 1)


class BulkOperationsAPITests(PhotoAPITestCase):
    """Test bulk operations functionality"""
    
    def test_bulk_update_set_public(self):
        """Test bulk update to set photos public"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('bulk_photo_update_api')
        data = {
            'photo_ids': [self.photo.id, self.private_photo.id],
            'action': 'set_public'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['updated_count'], 2)
        
        # Verify photos are now public
        self.photo.refresh_from_db()
        self.private_photo.refresh_from_db()
        self.assertTrue(self.photo.is_public)
        self.assertTrue(self.private_photo.is_public)
    
    def test_bulk_update_add_tags(self):
        """Test bulk update to add tags"""
        # Create another tag
        new_tag = PhotoTag.objects.create(
            name='bulk-tag',
            description='Tag for bulk testing',
            color='#00ff00'
        )
        
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('bulk_photo_update_api')
        data = {
            'photo_ids': [self.photo.id],
            'action': 'add_tags',
            'tag_ids': [new_tag.id]
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify tag was added
        self.photo.refresh_from_db()
        self.assertIn(new_tag, self.photo.tags.all())
    
    def test_bulk_update_unauthorized(self):
        """Test bulk update with unauthorized access"""
        self.client.force_authenticate(user=self.student_user)
        url = reverse('bulk_photo_update_api')
        data = {
            'photo_ids': [self.photo.id],
            'action': 'set_public'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class StatisticsAPITests(PhotoAPITestCase):
    """Test statistics API endpoints"""
    
    def test_photo_stats_admin(self):
        """Test admin can access photo statistics"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('photo_stats_api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_photos', response.data)
        self.assertIn('total_albums', response.data)
        self.assertIn('total_comments', response.data)
        self.assertIn('total_likes', response.data)
        self.assertIn('photos_by_category', response.data)
        self.assertEqual(response.data['total_photos'], 2)
    
    def test_album_stats_admin(self):
        """Test admin can access album statistics"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('album_stats_api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_albums', response.data)
        self.assertIn('public_albums', response.data)
        self.assertIn('private_albums', response.data)
        self.assertIn('albums_by_moze', response.data)
        self.assertEqual(response.data['total_albums'], 1)
    
    def test_stats_unauthorized_user(self):
        """Test unauthorized user cannot access statistics"""
        self.client.force_authenticate(user=self.student_user)
        url = reverse('photo_stats_api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class DashboardAPITests(PhotoAPITestCase):
    """Test dashboard API functionality"""
    
    def test_dashboard_admin(self):
        """Test admin can access comprehensive dashboard"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('photos_dashboard_api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('photo_stats', response.data)
        self.assertIn('album_stats', response.data)
        self.assertIn('engagement_stats', response.data)
        self.assertIn('recent_photos', response.data)
        self.assertIn('recent_albums', response.data)
    
    def test_dashboard_staff(self):
        """Test staff can access their dashboard"""
        self.client.force_authenticate(user=self.aamil_user)
        url = reverse('photos_dashboard_api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('photo_stats', response.data)
        self.assertIn('album_stats', response.data)
    
    def test_dashboard_regular_user(self):
        """Test regular user can access their limited dashboard"""
        self.client.force_authenticate(user=self.student_user)
        url = reverse('photos_dashboard_api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('my_photos', response.data)
        self.assertIn('my_albums', response.data)
        self.assertIn('my_stats', response.data)


class PermissionTests(PhotoAPITestCase):
    """Test role-based permissions"""
    
    def test_photo_visibility_by_role(self):
        """Test photo visibility based on user role"""
        # Admin should see all photos
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('photo_list_create')
        response = self.client.get(url)
        self.assertEqual(len(response.data['results']), 2)
        
        # Regular user should see only public photos
        self.client.force_authenticate(user=self.doctor_user)
        response = self.client.get(url)
        self.assertEqual(len(response.data['results']), 1)
        
        # Photo uploader should see their own photos
        self.client.force_authenticate(user=self.aamil_user)
        response = self.client.get(url)
        photo_ids = [p['id'] for p in response.data['results']]
        self.assertIn(self.private_photo.id, photo_ids)
    
    def test_album_creation_permissions(self):
        """Test album creation permissions"""
        # Admin can create albums
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('album_list_create')
        data = {
            'name': 'Admin Album',
            'moze_id': self.moze.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Regular user cannot create albums for mozes they don't manage
        self.client.force_authenticate(user=self.student_user)
        data = {
            'name': 'Student Album',
            'moze_id': self.moze.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_photo_modification_permissions(self):
        """Test photo modification permissions"""
        # Photo owner can modify their photo
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('photo_detail', kwargs={'pk': self.photo.pk})
        data = {'title': 'Modified by owner'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Non-owner cannot modify photo
        self.client.force_authenticate(user=self.student_user)
        data = {'title': 'Modified by non-owner'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_comment_permissions(self):
        """Test comment permissions on public vs private photos"""
        # User can comment on public photo
        self.client.force_authenticate(user=self.student_user)
        url = reverse('comment_list_create')
        data = {
            'photo_id': self.photo.id,
            'content': 'Comment on public photo'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # User cannot comment on private photo they can't access
        data = {
            'photo_id': self.private_photo.id,
            'content': 'Comment on private photo'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ValidationTests(PhotoAPITestCase):
    """Test data validation"""
    
    def test_photo_file_validation(self):
        """Test photo file validation"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('photo_list_create')
        
        # Test with invalid file type
        invalid_file = SimpleUploadedFile(
            "test.txt",
            b"This is not an image",
            content_type="text/plain"
        )
        
        data = {
            'image': invalid_file,
            'title': 'Invalid File',
            'moze_id': self.moze.id,
            'subject_tag': 'invalid'
        }
        
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_album_name_uniqueness(self):
        """Test album name uniqueness within moze"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('album_list_create')
        
        # Try to create album with existing name in same moze
        data = {
            'name': 'Test Album',  # Same as existing album
            'moze_id': self.moze.id
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_bulk_update_validation(self):
        """Test bulk update validation"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('bulk_photo_update_api')
        
        # Test missing album_id for album action
        data = {
            'photo_ids': [self.photo.id],
            'action': 'add_to_album'
            # Missing album_id
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_tag_creation_validation(self):
        """Test tag creation validation"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('tag_list_create')
        
        # Test duplicate tag name
        data = {
            'name': 'test-tag',  # Same as existing tag
            'description': 'Duplicate tag'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class FilteringAndSearchTests(PhotoAPITestCase):
    """Test filtering and search functionality"""
    
    def test_filter_photos_by_category(self):
        """Test filtering photos by category"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('photo_list_create')
        
        # Filter by medical category
        response = self.client.get(url, {'category': 'medical'})
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['category'], 'medical')
        
        # Filter by team category
        response = self.client.get(url, {'category': 'team'})
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['category'], 'team')
    
    def test_filter_photos_by_public_status(self):
        """Test filtering photos by public status"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('photo_list_create')
        
        # Filter by public
        response = self.client.get(url, {'is_public': 'true'})
        public_count = len([p for p in response.data['results'] if p['is_public']])
        self.assertEqual(public_count, 1)
        
        # Filter by private
        response = self.client.get(url, {'is_public': 'false'})
        private_count = len([p for p in response.data['results'] if not p['is_public']])
        self.assertEqual(private_count, 1)
    
    def test_search_photos_by_title(self):
        """Test searching photos by title"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('photo_list_create')
        
        response = self.client.get(url, {'search': 'Test Photo'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Search should find photos containing "Test Photo" in title
        self.assertGreaterEqual(len(response.data['results']), 1)
        
        response = self.client.get(url, {'search': 'Private'})
        self.assertEqual(len(response.data['results']), 1)
        
        response = self.client.get(url, {'search': 'Nonexistent'})
        self.assertEqual(len(response.data['results']), 0)
    
    def test_filter_albums_by_moze(self):
        """Test filtering albums by moze"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('album_list_create')
        
        response = self.client.get(url, {'moze': self.moze.id})
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['moze']['id'], self.moze.id)
    
    def test_filter_comments_by_photo(self):
        """Test filtering comments by photo"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('comment_list_create')
        
        response = self.client.get(url, {'photo': self.photo.id})
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['photo']['id'], self.photo.id)
    
    def test_ordering_photos(self):
        """Test ordering photos by different fields"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('photo_list_create')
        
        # Order by created_at (default)
        response = self.client.get(url, {'ordering': '-created_at'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Order by title
        response = self.client.get(url, {'ordering': 'title'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)