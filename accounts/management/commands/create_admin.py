from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.services import ITSService

User = get_user_model()

class Command(BaseCommand):
    help = 'Create Badri Mahal Admin user'

    def handle(self, *args, **options):
        admin_its_id = '50000001'
        
        # Check if admin already exists
        if User.objects.filter(its_id=admin_its_id).exists():
            self.stdout.write(
                self.style.WARNING(f'Badri Mahal Admin with ITS ID {admin_its_id} already exists!')
            )
            admin_user = User.objects.get(its_id=admin_its_id)
        else:
            # Fetch data from ITS service
            its_data = ITSService.fetch_user_data(admin_its_id)
            
            if its_data:
                # Create admin user from ITS data
                admin_user = User.objects.create_user(
                    username='badri_admin',
                    its_id=admin_its_id,
                    first_name=its_data.get('first_name', 'Badri'),
                    last_name=its_data.get('last_name', 'Admin'),
                    email=its_data.get('email', 'admin@badrimahal.com'),
                    role='badri_mahal_admin',
                    is_superuser=True,
                    is_staff=True,
                    is_active=True
                )
                # Set a default password
                admin_user.set_password('admin123')
                admin_user.save()
                
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Created Badri Mahal Admin: {admin_user.get_full_name()}')
                )
            else:
                # Create admin user manually if ITS service fails
                admin_user = User.objects.create_user(
                    username='badri_admin',
                    its_id=admin_its_id,
                    first_name='Badri Mahal',
                    last_name='Admin',
                    email='admin@badrimahal.com',
                    role='badri_mahal_admin',
                    is_superuser=True,
                    is_staff=True,
                    is_active=True
                )
                admin_user.set_password('admin123')
                admin_user.save()
                
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Created Badri Mahal Admin manually: {admin_user.get_full_name()}')
                )
        
        # Display admin details
        self.stdout.write('\n' + '='*50)
        self.stdout.write('🏥 BADRI MAHAL ADMIN DETAILS')
        self.stdout.write('='*50)
        self.stdout.write(f'Name: {admin_user.get_full_name()}')
        self.stdout.write(f'Username: {admin_user.username}')
        self.stdout.write(f'ITS ID: {admin_user.its_id}')
        self.stdout.write(f'Email: {admin_user.email}')
        self.stdout.write(f'Role: {admin_user.role}')
        self.stdout.write(f'is_admin: {admin_user.is_admin}')
        self.stdout.write(f'is_superuser: {admin_user.is_superuser}')
        self.stdout.write(f'is_staff: {admin_user.is_staff}')
        self.stdout.write(f'is_active: {admin_user.is_active}')
        self.stdout.write('\n🔐 LOGIN CREDENTIALS:')
        self.stdout.write(f'ITS ID: {admin_its_id}')
        self.stdout.write('Password: admin123')
        self.stdout.write('\n✅ Ready for appointment booking testing!')