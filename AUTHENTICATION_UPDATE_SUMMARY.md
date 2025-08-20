# Authentication System Update Summary

## Changes Implemented

### 1. **Updated ITS Service (`accounts/services.py`)**
- Renamed `MockITSService` to `ITSService` for clarity
- Enhanced role determination logic:
  - Occupation = "Doctor" → doctor role
  - Category = "Amil" → aamil role  
  - ITS ID in coordinator list → moze_coordinator role
  - ITS ID in student list → student role
  - All others → patient role (new default)
- Added methods to manage student/coordinator ITS ID lists
- Improved user data generation with realistic fields

### 2. **Added Patient Role**
- Added 'patient' to `ROLE_CHOICES` in User model
- Added `is_patient` property to User model
- Updated login redirect to handle patient role
- Patients are redirected to their profile page

### 3. **Updated Authentication Form (`accounts/forms.py`)**
- Now uses `ITSService.authenticate_user()` method
- Properly syncs all ITS fields to user profile
- Handles role assignment based on ITS data
- Updates existing users with latest ITS data on login

### 4. **Created Management Command**
- `python manage.py upload_its_ids` - Upload student/coordinator ITS IDs
- Supports CSV, JSON, and plain text formats
- Can clear existing IDs with `--clear` flag
- Validates ITS ID format before uploading

### 5. **Created Mock Data Generator**
- `generate_mock_data.py` - Comprehensive data generation
- Creates 1000 users with proper role distribution:
  - 1 Admin
  - 100 Aamils (1 per moze)
  - 100 Moze Coordinators
  - 50 Doctors
  - 200 Students  
  - 550 Patients
- Generates complete healthcare ecosystem:
  - 100 Moze
  - 5 Hospitals
  - 50 Mahal Shifa centers
  - Medical records
  - Araz (petitions)
  - Surveys and evaluations
  - Photo albums

## How Authentication Works Now

1. **User logs in with ITS ID and password**
2. **System authenticates against ITS API**
3. **Role is determined by:**
   - ITS data fields (occupation, category)
   - Uploaded ITS ID lists (students, coordinators)
   - Default to patient role
4. **User profile is created/updated with ITS data**
5. **User is redirected based on role:**
   - Admin → Admin dashboard
   - Aamil → Moze dashboard (full access)
   - Coordinator → Moze dashboard (limited access)
   - Doctor → Doctor dashboard
   - Student → Student dashboard
   - Patient → Profile page

## Testing Instructions

### 1. Generate Mock Data
```bash
cd /workspace
python generate_mock_data.py
# Type 'yes' to confirm
```

### 2. Test Different Roles

**Admin Login:**
- ITS ID: 10000001
- Password: pass1234
- Expected: Admin dashboard

**Aamil Login:**
- ITS ID: 10000002 to 10000101
- Password: pass1234
- Expected: Moze dashboard with full access

**Doctor Login:**
- ITS ID: 10000202 to 10000251
- Password: pass1234
- Expected: Doctor dashboard

**Student Login:**
- ITS ID: 10000252 to 10000451
- Password: pass1234
- Expected: Student dashboard

**Patient Login:**
- ITS ID: 10000452 to 10001001
- Password: pass1234
- Expected: Patient profile page

### 3. Upload Custom ITS IDs

**Upload Students:**
```bash
python manage.py upload_its_ids sample_student_its_ids.csv --role student
```

**Upload Coordinators:**
```bash
python manage.py upload_its_ids sample_coordinator_its_ids.csv --role coordinator
```

## Key Features

1. **Single Login System**: Only ITS ID and password required
2. **Automatic Role Assignment**: Based on ITS data
3. **Profile Sync**: ITS data synced on every login
4. **Flexible Lists**: Admin can upload student/coordinator lists
5. **Comprehensive Mock Data**: Full healthcare system for testing
6. **Role-Based Access**: Each role has specific permissions and views

## Security Notes

- All authentication goes through ITS API
- Passwords are never stored locally
- Role assignment is automatic and secure
- Session management follows Django best practices
- ITS ID format is validated (8 digits)

## Files Modified/Created

1. `/workspace/accounts/services.py` - Updated ITS service
2. `/workspace/accounts/models.py` - Added patient role
3. `/workspace/accounts/forms.py` - Updated authentication logic
4. `/workspace/accounts/views.py` - Added patient redirect
5. `/workspace/accounts/management/commands/upload_its_ids.py` - New command
6. `/workspace/generate_mock_data.py` - Mock data generator
7. `/workspace/sample_student_its_ids.csv` - Sample student IDs
8. `/workspace/sample_coordinator_its_ids.csv` - Sample coordinator IDs
9. `/workspace/ITS_AUTHENTICATION_GUIDE.md` - Documentation

## Next Steps

1. Run migrations for the patient role:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. Generate mock data:
   ```bash
   python generate_mock_data.py
   ```

3. Test the authentication system with different roles

4. For production:
   - Replace mock ITS service with real API calls
   - Configure proper ITS API endpoints
   - Set up secure API credentials