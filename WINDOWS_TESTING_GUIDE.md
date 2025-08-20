# Complete System Testing Guide for Windows

## Prerequisites

1. **Python 3.8+ installed**
2. **Git installed**
3. **PostgreSQL or SQLite** (SQLite is default, easier for testing)
4. **Code editor** (VS Code recommended)

## Step-by-Step Testing Guide

### 1. Setup Environment on Windows

Open Command Prompt or PowerShell as Administrator:

```cmd
# Clone the repository
cd C:\
git clone https://github.com/HusainSuksar/Sehhat_Website.git
cd Sehhat_Website

# Create virtual environment
python -m venv venv

# Activate virtual environment
# For Command Prompt:
venv\Scripts\activate

# For PowerShell:
.\venv\Scripts\Activate.ps1

# If PowerShell gives error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Install Dependencies

```cmd
# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# If you get errors, install packages one by one:
pip install Django==5.0.1
pip install djangorestframework==3.16.0
pip install psycopg2-binary==2.9.10
pip install pillow==11.3.0
```

### 3. Setup Database

```cmd
# Create migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### 4. Generate Mock Data

```cmd
# Generate complete test data
python generate_mock_data.py
# Type 'yes' when prompted
```

This creates:
- 1000 users with different roles
- 100 Moze with Aamils
- 50 Doctors
- 200 Students
- 550 Patients
- Medical records, appointments, surveys, etc.

### 5. Run the Server

```cmd
python manage.py runserver
```

Keep this terminal open. The server runs at: `http://localhost:8000`

### 6. Test Each User Role

Open a web browser and test each role:

#### A. Test Admin Role

1. **Open**: `http://localhost:8000/accounts/login/`
2. **Login with**:
   - ITS ID: `10000001`
   - Password: `pass1234`
3. **Expected**: Redirect to Admin Dashboard
4. **Test Features**:
   - Access Django Admin: `http://localhost:8000/admin/`
   - View all users
   - Manage all moze
   - Access all modules
5. **Logout**: Click logout button

#### B. Test Aamil Role

1. **Login with**:
   - ITS ID: `10000002`
   - Password: `pass1234`
2. **Expected**: Redirect to Moze Dashboard
3. **Test Features**:
   - View assigned moze details
   - Manage petitions (Araz)
   - View all moze reports
   - Access patient logs in moze
   - Create/manage surveys
4. **Check Permissions**:
   - Should see ALL activities in their moze
   - Can approve/reject petitions
5. **Logout**

#### C. Test Moze Coordinator Role

1. **Login with**:
   - ITS ID: `10000102`
   - Password: `pass1234`
2. **Expected**: Redirect to Moze Dashboard (limited view)
3. **Test Features**:
   - View ONLY assigned moze
   - Limited petition management
   - View moze activities
4. **Check Restrictions**:
   - Cannot see other moze data
   - Limited admin functions
5. **Logout**

#### D. Test Doctor Role

1. **Login with**:
   - ITS ID: `10000202`
   - Password: `pass1234`
2. **Expected**: Redirect to Doctor Dashboard
3. **Test Features**:
   - View doctor profile
   - Manage appointments
   - Create time slots
   - View patient medical records
   - Create prescriptions
4. **Test Appointment Flow**:
   - Go to time slots
   - Create new time slot for tomorrow
   - View appointments list
5. **Logout**

#### E. Test Patient Role

1. **Login with**:
   - ITS ID: `10000500`
   - Password: `pass1234`
2. **Expected**: Redirect to Patient Profile
3. **Test Features**:
   - View profile information
   - Book appointments
   - View medical records
   - Update personal information
4. **Test Appointment Booking**:
   - Find available doctor
   - Select time slot
   - Book appointment
   - View appointment status
5. **Logout**

#### F. Test Student Role

1. **Login with**:
   - ITS ID: `10000252`
   - Password: `pass1234`
2. **Expected**: Redirect to Student Dashboard
3. **Test Features**:
   - View enrolled courses
   - Check evaluations
   - Submit survey responses
   - View academic progress
4. **Check Restrictions**:
   - Limited to student features only
   - Cannot access medical data
5. **Logout**

### 7. Run Automated Integration Tests

Open a new terminal/command prompt:

```cmd
# Make sure virtual environment is activated
venv\Scripts\activate

# Run integration tests
python test_complete_system.py
# Type 'yes' when prompted
```

This will automatically test:
- Login/logout for all roles
- Role-based access control
- Cross-module integration
- Appointment system
- Medical records
- Surveys

### 8. Test Specific Modules

#### Test Appointments Module
```cmd
python manage.py test appointments
```

#### Test Moze Module
```cmd
python manage.py test moze
```

#### Test Doctor Directory
```cmd
python manage.py test doctordirectory
```

### 9. Manual Testing Checklist

#### ✅ Authentication
- [ ] Login with ITS ID works
- [ ] Wrong password shows error
- [ ] Logout clears session
- [ ] Role assignment is correct

#### ✅ Aamil Features
- [ ] Can see all moze data
- [ ] Can manage petitions
- [ ] Can create surveys
- [ ] Can view all reports

#### ✅ Doctor Features
- [ ] Can manage appointments
- [ ] Can create time slots
- [ ] Can view patient records
- [ ] Can update medical logs

#### ✅ Patient Features
- [ ] Can book appointments
- [ ] Can view own medical records
- [ ] Cannot see other patients' data
- [ ] Can update profile

#### ✅ Student Features
- [ ] Can view courses
- [ ] Can see evaluations
- [ ] Can submit surveys
- [ ] Limited to student area

#### ✅ Appointment System
- [ ] Booking works
- [ ] Cancellation works
- [ ] Rescheduling works
- [ ] Reminders created
- [ ] Time slots prevent double booking

#### ✅ Medical Records
- [ ] Doctors can create records
- [ ] Patients can view own records
- [ ] Privacy maintained
- [ ] Search works

#### ✅ Surveys
- [ ] Aamils can create surveys
- [ ] Users can respond
- [ ] Anonymous option works
- [ ] Results viewable

### 10. Common Windows Issues & Solutions

#### Issue: Module not found errors
```cmd
# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

#### Issue: Database errors
```cmd
# Reset database
python manage.py migrate --run-syncdb
python manage.py flush
python generate_mock_data.py
```

#### Issue: Port 8000 already in use
```cmd
# Use different port
python manage.py runserver 8080
```

#### Issue: Static files not loading
```cmd
# Collect static files
python manage.py collectstatic
```

### 11. Performance Testing

Check system performance:

```cmd
# Open Django shell
python manage.py shell

# Run performance checks
from django.contrib.auth import get_user_model
User = get_user_model()
print(f"Total users: {User.objects.count()}")
print(f"Doctors: {User.objects.filter(role='doctor').count()}")
print(f"Patients: {User.objects.filter(role='patient').count()}")

# Check appointments
from appointments.models import Appointment
print(f"Total appointments: {Appointment.objects.count()}")
```

### 12. API Testing with Postman/cURL

Test REST APIs:

```bash
# Login API (use Git Bash on Windows)
curl -X POST http://localhost:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{"its_id": "10000202", "password": "pass1234"}'

# Get appointments
curl http://localhost:8000/api/appointments/appointments/ \
  -H "Authorization: Token YOUR_TOKEN"
```

### 13. Database Inspection

Use Django Admin or DB Browser:

1. **Django Admin**: `http://localhost:8000/admin/`
   - Login with superuser
   - Browse all models
   - Check data integrity

2. **SQLite Browser** (if using SQLite):
   - Download: https://sqlitebrowser.org/
   - Open `db.sqlite3`
   - Inspect tables

### 14. Generate Test Report

After testing, create a report:

```cmd
# Generate test report
python test_complete_system.py > test_report.txt 2>&1
```

## Quick Reference

### Login Credentials
All users password: `pass1234`

| Role | ITS ID Range | Example | Dashboard |
|------|--------------|---------|-----------|
| Admin | 10000001 | 10000001 | /admin/ |
| Aamil | 10000002-10000101 | 10000002 | /moze/dashboard/ |
| Coordinator | 10000102-10000201 | 10000102 | /moze/dashboard/ |
| Doctor | 10000202-10000251 | 10000202 | /doctordirectory/dashboard/ |
| Student | 10000252-10000451 | 10000252 | /students/dashboard/ |
| Patient | 10000452-10001001 | 10000500 | /accounts/profile/ |

### Key URLs
- Login: `http://localhost:8000/accounts/login/`
- Admin: `http://localhost:8000/admin/`
- API Docs: `http://localhost:8000/api/`
- Appointments: `http://localhost:8000/api/appointments/`

### Testing Commands Summary
```cmd
# Setup
python manage.py migrate
python generate_mock_data.py

# Run server
python manage.py runserver

# Run tests
python test_complete_system.py
python manage.py test

# Upload ITS IDs
python manage.py upload_its_ids students.csv --role student
python manage.py upload_its_ids coordinators.csv --role coordinator
```

## Conclusion

This guide covers complete end-to-end testing of the Umoor Sehhat system. Each module has been integrated and can be tested independently or as part of the complete workflow. The role-based access control ensures proper data privacy and security.