# Create Badri Mahal Admin User

## Method 1: Using Django Shell (Recommended)

1. **Start Django shell:**
   ```bash
   python manage.py shell
   ```

2. **Run this code in the shell:**
   ```python
   from django.contrib.auth import get_user_model
   from accounts.services import ITSService
   
   User = get_user_model()
   
   # Create Badri Mahal Admin
   admin_its_id = '50000001'
   
   # Check if already exists
   if User.objects.filter(its_id=admin_its_id).exists():
       print("Admin already exists!")
       admin_user = User.objects.get(its_id=admin_its_id)
   else:
       # Create new admin
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
       print(f"✅ Created admin: {admin_user.get_full_name()}")
   
   # Verify admin properties
   print(f"is_admin: {admin_user.is_admin}")
   print(f"is_superuser: {admin_user.is_superuser}")
   print(f"role: {admin_user.role}")
   ```

## Method 2: Using Management Command

1. **Run the management command:**
   ```bash
   python manage.py create_admin
   ```

## Method 3: Using Django Admin Interface

1. **Create superuser first:**
   ```bash
   python manage.py createsuperuser
   ```

2. **Login to Django Admin** at `/admin/`

3. **Create new user with these details:**
   - Username: `badri_admin`
   - ITS ID: `50000001`
   - First name: `Badri Mahal`
   - Last name: `Admin`
   - Email: `admin@badrimahal.com`
   - Role: `badri_mahal_admin`
   - ✅ Superuser status: `True`
   - ✅ Staff status: `True`
   - ✅ Active: `True`
   - Password: `admin123`

## Login Credentials

After creating the admin user, you can login with:

- **ITS ID**: `50000001`
- **Password**: `admin123`

## Testing Appointment Booking

1. **Login** with ITS ID `50000001`
2. **Go to Doctor Directory**
3. **Click "Book Appointment"** on any doctor
4. **Enter ITS ID**: `10000007` (test patient)
5. **Click "Fetch"** to load patient data
6. **Fill appointment details** and submit

## Valid Test ITS IDs

Use these ITS IDs for testing patient booking:
- `10000007`
- `10000011` 
- `10000013`
- `20000014`
- `30000022`

These IDs will pass the validation and create test patients automatically.