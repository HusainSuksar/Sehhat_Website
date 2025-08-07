"""
Django management command to test Django models and user API services
Usage: python manage.py test_api_services
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import sys
from pathlib import Path

# Add project root to Python path for services import
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from services.api_service import user_api_service
from services.data_service import data_service


class Command(BaseCommand):
    help = 'Test Django models and user API services functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-user-api',
            action='store_true',
            help='Test user API connectivity',
        )
        parser.add_argument(
            '--test-django-data',
            action='store_true',
            help='Test Django models data service',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Run all tests',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Testing Django Models & User API Services...\n')
        )

        if options['all'] or options['test_user_api']:
            self.test_user_api_service()

        if options['all'] or options['test_django_data']:
            self.test_django_data_service()

        if not any([options['test_user_api'], options['test_django_data'], options['all']]):
            # Default: run basic tests
            self.test_basic_functionality()

        self.stdout.write(
            self.style.SUCCESS('\n🎉 Services testing completed!')
        )

    def test_user_api_service(self):
        """Test user API service"""
        self.stdout.write('\n👥 Testing User API Service:')
        
        # Test API status
        try:
            status = user_api_service.get_api_status()
            if status['is_available']:
                self.stdout.write(
                    self.style.SUCCESS(f"  ✅ User API Available: {status['base_url']}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"  ⚠️  User API Offline: {status['base_url']}")
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"  ❌ User API Status Error: {e}")
            )

        # Test user data fetching (if API available)
        try:
            # Test search functionality
            search_results = user_api_service.search_users("test")
            self.stdout.write(
                self.style.SUCCESS(f"  ✅ User Search: {len(search_results)} results found")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"  ❌ User Search Error: {e}")
            )

    def test_django_data_service(self):
        """Test Django models data service"""
        self.stdout.write('\n🗄️  Testing Django Data Service:')
        
        try:
            # Test dashboard statistics
            stats = data_service.get_dashboard_statistics()
            self.stdout.write(
                self.style.SUCCESS(f"  ✅ Dashboard Stats: {len(stats)} metrics available")
            )
            
            # Display key statistics
            for key, value in stats.items():
                if key != 'users_by_role':
                    self.stdout.write(f"    📊 {key.replace('_', ' ').title()}: {value}")
            
            # Test users
            users = data_service.get_all_users()
            self.stdout.write(
                self.style.SUCCESS(f"  ✅ Users: {len(users)} total users")
            )
            
            # Test doctors
            doctors = data_service.get_all_doctors()
            self.stdout.write(
                self.style.SUCCESS(f"  ✅ Doctors: {len(doctors)} total doctors")
            )
            
            # Test hospitals
            hospitals = data_service.get_all_hospitals()
            self.stdout.write(
                self.style.SUCCESS(f"  ✅ Hospitals: {len(hospitals)} total hospitals")
            )
            
            # Test surveys
            surveys = data_service.get_all_surveys()
            self.stdout.write(
                self.style.SUCCESS(f"  ✅ Surveys: {len(surveys)} total surveys")
            )
            
            # Test recent activities
            activities = data_service.get_recent_activities(limit=3)
            self.stdout.write(
                self.style.SUCCESS(f"  ✅ Recent Activities: {len(activities)} activities")
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"  ❌ Django Data Service Error: {e}")
            )

    def test_basic_functionality(self):
        """Test basic functionality"""
        self.stdout.write('\n🔧 Basic Functionality Test:')
        
        # Test imports
        self.stdout.write(
            self.style.SUCCESS("  ✅ Service imports successful")
        )
        
        # Test configuration
        user_api_url = getattr(settings, 'USER_API_URL', 'Not configured')
        cache_timeout = getattr(settings, 'API_CACHE_TIMEOUT', 'Not configured')
        
        self.stdout.write(f"  📋 User API URL: {user_api_url}")
        self.stdout.write(f"  📋 Cache Timeout: {cache_timeout} seconds")
        
        # Test Django data service
        try:
            django_status = data_service.get_system_status()
            self.stdout.write(
                self.style.SUCCESS("  ✅ Django data service working")
            )
            self.stdout.write(f"    🗄️  Database: {django_status['database_status']}")
            self.stdout.write(f"    📊 Data Source: {django_status['data_source']}")
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"  ❌ Django Data Service Error: {e}")
            )
        
        # Test user API service
        try:
            user_api_status = user_api_service.get_api_status()
            self.stdout.write(
                self.style.SUCCESS("  ✅ User API service working")
            )
            self.stdout.write(f"    📡 API: {'Available' if user_api_status['is_available'] else 'Offline'}")
            self.stdout.write(f"    🔧 Service Type: {user_api_status['service_type']}")
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"  ❌ User API Service Error: {e}")
            )