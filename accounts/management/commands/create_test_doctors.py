from django.core.management.base import BaseCommand
from accounts.models import User
from doctordirectory.models import Doctor, Service
from django.db.models import Count


class Command(BaseCommand):
    help = 'Create test doctor users if none exist'

    def handle(self, *args, **options):
        self.stdout.write("=== CURRENT USER ROLES ===")
        role_counts = User.objects.values('role').annotate(count=Count('role'))
        for item in role_counts:
            self.stdout.write(f"{item['role']}: {item['count']}")
        
        self.stdout.write("\n=== DOCTOR PROFILES ===")
        doctors = Doctor.objects.all()
        self.stdout.write(f"Doctor profiles count: {doctors.count()}")
        for doctor in doctors:
            self.stdout.write(f"Doctor: {doctor.user.username} | Speciality: {doctor.speciality}")
        
        # Check if we need to create doctor users
        doctor_users = User.objects.filter(role='doctor')
        if doctor_users.count() == 0:
            self.stdout.write("\n=== CREATING TEST DOCTOR USERS ===")
            
            # Create a few test doctor users
            test_doctors = [
                {
                    'username': '20000001',
                    'its_id': '20000001',
                    'first_name': 'Dr. Ahmed',
                    'last_name': 'Khan',
                    'email': 'ahmed.khan@example.com',
                    'role': 'doctor'
                },
                {
                    'username': '20000002', 
                    'its_id': '20000002',
                    'first_name': 'Dr. Fatima',
                    'last_name': 'Ali',
                    'email': 'fatima.ali@example.com',
                    'role': 'doctor'
                },
                {
                    'username': '20000003',
                    'its_id': '20000003', 
                    'first_name': 'Dr. Hassan',
                    'last_name': 'Sheikh',
                    'email': 'hassan.sheikh@example.com',
                    'role': 'doctor'
                }
            ]
            
            for doctor_data in test_doctors:
                try:
                    # Check if user already exists
                    if not User.objects.filter(its_id=doctor_data['its_id']).exists():
                        user = User.objects.create_user(
                            username=doctor_data['username'],
                            its_id=doctor_data['its_id'],
                            first_name=doctor_data['first_name'],
                            last_name=doctor_data['last_name'],
                            email=doctor_data['email'],
                            role=doctor_data['role']
                        )
                        self.stdout.write(self.style.SUCCESS(f"✅ Created doctor user: {user.username}"))
                        
                        # Create doctor profile
                        doctor_profile = Doctor.objects.create(
                            user=user,
                            speciality='General Medicine',
                            qualification='MBBS',
                            experience_years=5,
                            consultation_fee=500.00,
                            is_available=True
                        )
                        self.stdout.write(self.style.SUCCESS(f"✅ Created doctor profile for: {user.username}"))
                        
                        # Create a basic service
                        service = Service.objects.create(
                            doctor=doctor_profile,
                            name='General Consultation',
                            description='General medical consultation',
                            duration=30,
                            price=500.00
                        )
                        self.stdout.write(self.style.SUCCESS(f"✅ Created service for: {user.username}"))
                        
                    else:
                        self.stdout.write(self.style.WARNING(f"⚠️ User {doctor_data['its_id']} already exists"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"❌ Error creating doctor {doctor_data['username']}: {e}"))
            
            self.stdout.write("\n=== UPDATED USER ROLES ===")
            role_counts = User.objects.values('role').annotate(count=Count('role'))
            for item in role_counts:
                self.stdout.write(f"{item['role']}: {item['count']}")
        else:
            self.stdout.write(self.style.SUCCESS(f"\n✅ Found {doctor_users.count()} doctor users already"))