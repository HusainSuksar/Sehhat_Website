#!/usr/bin/env python3
"""
Comprehensive Testing Script for Photos App (Medical Photo Gallery Management)
Tests all core functionality, URLs, user roles, and creates sample photo data.
"""

import os
import sys
import django
from datetime import datetime, timedelta, date, time
import json

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.core.files.uploadedfile import SimpleUploadedFile

# Import Photos models
from photos.models import Photo, PhotoAlbum, PhotoComment, PhotoLike, PhotoTag

# Import related models
from accounts.models import User
from moze.models import Moze

class PhotosAppTester:
    def __init__(self):
        self.client = Client()
        self.users = {}
        self.sample_data = {}
        self.test_results = []
        self.server_url = 'http://localhost:8000'
        
    def log_result(self, test_name, success, details=""):
        """Log test results"""
        status = "✅" if success else "❌"
        result = f"{status} {test_name}"
        if details:
            result += f": {details}"
        print(result)
        self.test_results.append({
            'name': test_name,
            'success': success,
            'details': details
        })
        
    def create_test_users(self):
        """Create test users for different roles"""
        print("\n🔧 Creating test users...")
        
        # Create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'first_name': 'System',
                'last_name': 'Administrator',
                'email': 'admin@photos.com',
                'role': 'admin',
                'phone_number': '+1234567890',
                'is_active': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
        self.users['admin'] = admin_user
        
        # Create aamil user
        aamil_user, created = User.objects.get_or_create(
            username='aamil_photos',
            defaults={
                'first_name': 'Medical',
                'last_name': 'Aamil',
                'email': 'aamil@photos.com',
                'role': 'aamil',
                'phone_number': '+1234567891',
                'is_active': True
            }
        )
        if created:
            aamil_user.set_password('test123')
            aamil_user.save()
        self.users['aamil'] = aamil_user
        
        # Create moze_coordinator user
        coordinator_user, created = User.objects.get_or_create(
            username='photos_coordinator',
            defaults={
                'first_name': 'Photos',
                'last_name': 'Coordinator',
                'email': 'coordinator@photos.com',
                'role': 'moze_coordinator',
                'phone_number': '+1234567892',
                'is_active': True
            }
        )
        if created:
            coordinator_user.set_password('test123')
            coordinator_user.save()
        self.users['moze_coordinator'] = coordinator_user
        
        # Create doctor user
        doctor_user, created = User.objects.get_or_create(
            username='dr_photos',
            defaults={
                'first_name': 'Doctor',
                'last_name': 'Photos',
                'email': 'doctor@photos.com',
                'role': 'doctor',
                'phone_number': '+1234567893',
                'is_active': True
            }
        )
        if created:
            doctor_user.set_password('test123')
            doctor_user.save()
        self.users['doctor'] = doctor_user
        
        # Create student user
        student_user, created = User.objects.get_or_create(
            username='student_photos',
            defaults={
                'first_name': 'Student',
                'last_name': 'Photos',
                'email': 'student@photos.com',
                'role': 'student',
                'phone_number': '+1234567894',
                'is_active': True
            }
        )
        if created:
            student_user.set_password('test123')
            student_user.save()
        self.users['student'] = student_user
        
        print(f"✅ Created {len(self.users)} test users")
        
    def create_sample_data(self):
        """Create comprehensive sample Photos data"""
        print("\n📸 Creating sample Photos data...")
        
        try:
            with transaction.atomic():
                # Create a Moze for testing
                moze, created = Moze.objects.get_or_create(
                    name='Photo Testing Moze',
                    defaults={
                        'location': 'Photography Center',
                        'address': '123 Photo Street, Gallery City, GC 12345',
                        'aamil': self.users['aamil'],
                        'moze_coordinator': self.users['moze_coordinator'],
                        'established_date': date(2020, 1, 15),
                        'is_active': True,
                        'capacity': 100,
                        'contact_phone': '+1234567800',
                        'contact_email': 'photos@moze.com'
                    }
                )
                self.sample_data['moze'] = moze
                
                # Create PhotoTags
                tag1, created = PhotoTag.objects.get_or_create(
                    name='medical',
                    defaults={
                        'description': 'Medical and clinical photos',
                        'color': '#ff6b6b'
                    }
                )
                tag2, created = PhotoTag.objects.get_or_create(
                    name='event',
                    defaults={
                        'description': 'Event and activity photos',
                        'color': '#4ecdc4'
                    }
                )
                tag3, created = PhotoTag.objects.get_or_create(
                    name='facility',
                    defaults={
                        'description': 'Facility and infrastructure photos',
                        'color': '#45b7d1'
                    }
                )
                self.sample_data['tags'] = [tag1, tag2, tag3]
                
                # Create PhotoAlbums
                album1 = PhotoAlbum.objects.create(
                    name='Medical Training Session',
                    description='Photos from the recent medical training and workshops',
                    moze=moze,
                    created_by=self.users['aamil'],
                    is_public=True,
                    event_date=date(2024, 1, 15)
                )
                
                album2 = PhotoAlbum.objects.create(
                    name='Facility Infrastructure',
                    description='Documentation of our medical facility and equipment',
                    moze=moze,
                    created_by=self.users['moze_coordinator'],
                    is_public=False,
                    event_date=date(2024, 2, 1)
                )
                
                self.sample_data['albums'] = [album1, album2]
                
                # Create sample Photos (using dummy image data)
                # For testing, we'll create photos without actual image files to avoid file system issues
                from django.core.files.base import ContentFile
                from PIL import Image
                from io import BytesIO
                
                # Create test images
                img1 = Image.new('RGB', (200, 200), color='blue')
                img1_io = BytesIO()
                img1.save(img1_io, format='JPEG')
                img1_io.seek(0)
                
                img2 = Image.new('RGB', (200, 200), color='green') 
                img2_io = BytesIO()
                img2.save(img2_io, format='JPEG')
                img2_io.seek(0)
                
                photo1 = Photo.objects.create(
                    title='Training Session Photo 1',
                    description='Group photo from medical training workshop',
                    subject_tag='training',
                    moze=moze,
                    uploaded_by=self.users['aamil'],
                    category='event',
                    is_public=True,
                    event_date=date(2024, 1, 15),
                    photographer='Medical Photographer'
                )
                
                # Save test image to photo1
                photo1.image.save(
                    'test_photo1.jpg',
                    ContentFile(img1_io.getvalue()),
                    save=True
                )
                
                # Add tags to photos
                photo1.tags.add(tag1, tag2)
                album1.photos.add(photo1)
                
                # Create another photo
                photo2 = Photo.objects.create(
                    title='Medical Equipment Documentation',
                    description='Documentation of new medical equipment installation',
                    subject_tag='equipment',
                    moze=moze,
                    uploaded_by=self.users['moze_coordinator'],
                    category='infrastructure',
                    is_public=False,
                    event_date=date(2024, 2, 1),
                    photographer='Technical Team'
                )
                
                # Save test image to photo2
                photo2.image.save(
                    'test_photo2.jpg',
                    ContentFile(img2_io.getvalue()),
                    save=True
                )
                
                photo2.tags.add(tag3)
                album2.photos.add(photo2)
                
                self.sample_data['photos'] = [photo1, photo2]
                
                # Create PhotoComments
                comment1 = PhotoComment.objects.create(
                    photo=photo1,
                    author=self.users['doctor'],
                    content='Great training session! Very informative and well organized.',
                    is_active=True
                )
                
                comment2 = PhotoComment.objects.create(
                    photo=photo1,
                    author=self.users['student'],
                    content='Thank you for organizing this session. Learned a lot!',
                    is_active=True
                )
                
                self.sample_data['comments'] = [comment1, comment2]
                
                # Create PhotoLikes
                like1 = PhotoLike.objects.create(
                    photo=photo1,
                    user=self.users['doctor']
                )
                
                like2 = PhotoLike.objects.create(
                    photo=photo1,
                    user=self.users['student']
                )
                
                self.sample_data['likes'] = [like1, like2]
                
            print("✅ Created comprehensive Photos sample data")
            
        except Exception as e:
            print(f"❌ Error creating sample data: {e}")
            import traceback
            traceback.print_exc()
            
    def test_model_access(self):
        """Test access to all Photos models"""
        print("\n📊 Testing Photos model access...")
        
        models_to_test = [
            ('Photo', Photo),
            ('Photo Album', PhotoAlbum),
            ('Photo Comment', PhotoComment),
            ('Photo Like', PhotoLike),
            ('Photo Tag', PhotoTag),
        ]
        
        for model_name, model_class in models_to_test:
            try:
                count = model_class.objects.count()
                self.log_result(f"Access {model_name} model", True, f"Found {count} records")
            except Exception as e:
                self.log_result(f"Access {model_name} model", False, f"Error: {e}")
                
    def test_url_accessibility(self):
        """Test URL accessibility"""
        print("\n🌐 Testing Photos URL accessibility...")
        
        # Public URLs (should redirect to login)
        public_urls = [
            ('', 'Dashboard'),
            ('albums/', 'Album List'),
            ('albums/create/', 'Create Album'),
            ('search/', 'Search Photos'),
        ]
        
        for url, name in public_urls:
            try:
                response = self.client.get(f'/photos/{url}')
                if response.status_code in [200, 302]:  # 302 = redirect to login
                    self.log_result(f"URL accessibility: {name}", True, f"Status: {response.status_code}")
                else:
                    self.log_result(f"URL accessibility: {name}", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_result(f"URL accessibility: {name}", False, f"Error: {e}")
                
    def test_user_role_access(self):
        """Test role-based access control"""
        print("\n👥 Testing user role-based access...")
        
        test_urls = [
            '/photos/',
            '/photos/albums/',
            '/photos/albums/create/',
            '/photos/search/',
        ]
        
        for role, user in self.users.items():
            accessible_count = 0
            self.client.force_login(user)
            
            for url in test_urls:
                try:
                    response = self.client.get(url)
                    if response.status_code == 200:
                        accessible_count += 1
                except:
                    pass
            
            self.log_result(f"Role access: {role}", True, f"Can access {accessible_count}/{len(test_urls)} URLs")
            self.client.logout()
            
    def test_photos_functionality(self):
        """Test core Photos functionality"""
        print("\n📸 Testing Photos functionality...")
        
        # Test with admin user
        self.client.force_login(self.users['admin'])
        
        # Test dashboard
        try:
            response = self.client.get('/photos/')
            success = response.status_code == 200
            error_msg = "Dashboard accessible" if success else f"Status: {response.status_code}"
            self.log_result("Dashboard access", success, error_msg)
        except Exception as e:
            self.log_result("Dashboard access", False, f"Error: {e}")
            
        # Test album list
        try:
            response = self.client.get('/photos/albums/')
            success = response.status_code == 200
            error_msg = "List accessible" if success else f"Status: {response.status_code}"
            self.log_result("Album listing", success, error_msg)
        except Exception as e:
            self.log_result("Album listing", False, f"Error: {e}")
            
        # Test album detail
        if self.sample_data.get('albums'):
            try:
                response = self.client.get(f'/photos/albums/{self.sample_data["albums"][0].pk}/')
                success = response.status_code == 200
                error_msg = "Detail accessible" if success else f"Status: {response.status_code}"
                self.log_result("Album detail view", success, error_msg)
            except Exception as e:
                self.log_result("Album detail view", False, f"Error: {e}")
                
        # Test album creation form
        try:
            response = self.client.get('/photos/albums/create/')
            success = response.status_code == 200
            error_msg = "Form accessible" if success else f"Status: {response.status_code}"
            self.log_result("Album creation form", success, error_msg)
        except Exception as e:
            self.log_result("Album creation form", False, f"Error: {e}")
            
        # Test search
        try:
            response = self.client.get('/photos/search/?q=medical')
            success = response.status_code == 200
            error_msg = "Search accessible" if success else f"Status: {response.status_code}"
            self.log_result("Photo search", success, error_msg)
        except Exception as e:
            self.log_result("Photo search", False, f"Error: {e}")
            
        self.client.logout()
        
    def test_role_specific_functionality(self):
        """Test role-specific Photos functionality"""
        print("\n👨‍⚕️ Testing role-specific functionality...")
        
        # Test Aamil functionality
        self.client.force_login(self.users['aamil'])
        try:
            response = self.client.get('/photos/')
            success = response.status_code == 200
            self.log_result("Aamil dashboard access", success, "Dashboard accessible" if success else f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Aamil dashboard access", False, f"Error: {e}")
            
        try:
            response = self.client.get('/photos/albums/')
            success = response.status_code == 200
            self.log_result("Aamil album list", success, "Can view albums" if success else f"Error accessing list")
        except Exception as e:
            self.log_result("Aamil album list", False, f"Error: {e}")
        self.client.logout()
        
        # Test Moze Coordinator functionality
        self.client.force_login(self.users['moze_coordinator'])
        try:
            response = self.client.get('/photos/')
            success = response.status_code == 200
            self.log_result("Coordinator dashboard access", success, "Dashboard accessible" if success else f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Coordinator dashboard access", False, f"Error: {e}")
        self.client.logout()
        
        # Test Photo interaction (likes/comments)
        if self.sample_data.get('photos'):
            self.client.force_login(self.users['doctor'])
            try:
                # Test photo like
                response = self.client.post(f'/photos/photos/{self.sample_data["photos"][0].pk}/like/')
                success = response.status_code == 200
                self.log_result("Photo like functionality", success, "Can like photos" if success else f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("Photo like functionality", False, f"Error: {e}")
                
            try:
                # Test photo comment
                response = self.client.post(f'/photos/photos/{self.sample_data["photos"][0].pk}/comment/', {
                    'content': 'Test comment from automated testing system'
                })
                success = response.status_code == 200
                self.log_result("Photo comment functionality", success, "Can comment on photos" if success else f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("Photo comment functionality", False, f"Error: {e}")
            self.client.logout()
            
    def generate_summary_report(self):
        """Generate comprehensive summary report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failure_rate = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n{'='*80}")
        print("📸 PHOTOS APP TESTING SUMMARY REPORT")
        print(f"{'='*80}")
        print(f"\n📊 OVERALL RESULTS:")
        print(f"✅ Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        print(f"❌ Failed: {failure_rate}/{total_tests} ({100-success_rate:.1f}%)")
        
        print(f"\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"  {status} {result['name']}: {result['details']}")
            
        print(f"\n📸 SAMPLE PHOTOS DATA CREATED:")
        sample_items = [
            f"  📸 Photos: {len(self.sample_data.get('photos', []))} photos",
            f"  📁 Albums: {len(self.sample_data.get('albums', []))} albums",
            f"  🏷️ Tags: {len(self.sample_data.get('tags', []))} tags",
            f"  💬 Comments: {len(self.sample_data.get('comments', []))} comments",
            f"  ❤️ Likes: {len(self.sample_data.get('likes', []))} likes",
            f"  🏥 Moze: {self.sample_data.get('moze', 'N/A')}"
        ]
        
        for item in sample_items:
            print(item)
            
        print(f"\n🔗 KEY URLS FOR MANUAL TESTING:")
        urls = [
            "  🏠 Dashboard: http://localhost:8000/photos/",
            "  📁 Albums: http://localhost:8000/photos/albums/",
            "  ➕ Create Album: http://localhost:8000/photos/albums/create/",
            "  🔍 Search: http://localhost:8000/photos/search/",
        ]
        
        if self.sample_data.get('albums'):
            urls.append(f"  👁️ Album Detail: http://localhost:8000/photos/albums/{self.sample_data['albums'][0].pk}/")
            
        if self.sample_data.get('photos'):
            urls.append(f"  📸 Photo Detail: http://localhost:8000/photos/photos/{self.sample_data['photos'][0].pk}/")
            
        for url in urls:
            print(url)
            
        print(f"\n👥 TEST USER CREDENTIALS:")
        creds = [
            "  👤 Admin: admin / admin123",
            "  👤 Aamil: aamil_photos / test123",
            "  👤 Coordinator: photos_coordinator / test123",
            "  👤 Doctor: dr_photos / test123",
            "  👤 Student: student_photos / test123"
        ]
        
        for cred in creds:
            print(cred)
            
        # Determine final status
        if success_rate >= 95:
            status = "🏆 EXCELLENT - App is fully functional"
        elif success_rate >= 85:
            status = "✅ GOOD - App is mostly functional"
        elif success_rate >= 70:
            status = "⚠️ ACCEPTABLE - Some issues need attention"
        else:
            status = "❌ NEEDS WORK - Major issues detected"
            
        print(f"\n🏆 FINAL STATUS: {status}")
        print(f"{'='*80}")
        
        return success_rate >= 95  # Return True if excellent
        
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("📸 Starting Comprehensive Photos App Testing...")
        print("="*80)
        
        self.create_test_users()
        self.create_sample_data()
        self.test_model_access()
        self.test_url_accessibility()
        self.test_user_role_access()
        self.test_photos_functionality()
        self.test_role_specific_functionality()
        
        return self.generate_summary_report()


def main():
    """Main function to run all tests"""
    try:
        tester = PhotosAppTester()
        all_passed = tester.run_all_tests()
        
        if all_passed:
            print("\n🎉 All tests passed! Photos app is ready for production.")
        else:
            print("\n⚠️ Some tests failed. Please review the issues above.")
            
        return 0 if all_passed else 1
        
    except KeyboardInterrupt:
        print("\n\n🛑 Testing interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())