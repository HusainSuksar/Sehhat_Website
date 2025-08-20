# ITS Authentication & Role Assignment Guide

## Overview

The Umoor Sehhat system uses ITS (Jamaat's IT System) for authentication and automatically assigns roles based on ITS data and uploaded lists.

## Role Assignment Logic

### 1. **Doctor Role**
- **Condition**: ITS API `occupation` field = "Doctor"
- **Access**: Doctor dashboard, patient management, appointments
- **Auto-created**: Doctor profile in `doctordirectory.Doctor`

### 2. **Aamil Role**
- **Condition**: ITS API `category` field = "Amil"
- **Access**: Moze dashboard, all moze activities, reports
- **Responsibility**: Manages moze operations, approves petitions

### 3. **Moze Coordinator Role**
- **Condition**: ITS ID exists in uploaded coordinator list
- **Access**: Moze dashboard (limited to assigned moze)
- **Upload Method**: CSV file via management command

### 4. **Student Role**
- **Condition**: ITS ID exists in uploaded student list
- **Access**: Student dashboard, courses, evaluations
- **Upload Method**: CSV file via management command

### 5. **Patient Role** (Default)
- **Condition**: All other authenticated ITS users
- **Access**: Profile page, medical records, appointments
- **Auto-created**: Patient profile in `doctordirectory.Patient`

## Uploading Student/Coordinator ITS IDs

### Via Management Command

```bash
# Upload student ITS IDs
python manage.py upload_its_ids sample_student_its_ids.csv --role student

# Upload coordinator ITS IDs
python manage.py upload_its_ids sample_coordinator_its_ids.csv --role coordinator

# Clear existing and upload new
python manage.py upload_its_ids new_students.csv --role student --clear
```

### CSV Format
```csv
its_id
10000252
10000253
10000254
```

### JSON Format
```json
{
  "its_ids": [
    "10000252",
    "10000253",
    "10000254"
  ]
}
```

### Plain Text Format
```
10000252
10000253
10000254
```

## Authentication Flow

1. **User enters ITS ID and password**
2. **System calls ITS API** (mock or real)
3. **ITS API returns user data** including:
   - Personal information (name, email, etc.)
   - Occupation
   - Category
   - Other profile fields
4. **System determines role** based on:
   - Occupation = "Doctor" → Doctor role
   - Category = "Amil" → Aamil role
   - ITS ID in coordinator list → Moze Coordinator role
   - ITS ID in student list → Student role
   - Default → Patient role
5. **User profile created/updated** with ITS data
6. **User redirected** to role-specific dashboard

## Mock Data Generation

Run the mock data generator to create a complete test environment:

```bash
python generate_mock_data.py
```

This creates:
- 1 Admin (ITS: 10000001)
- 100 Aamils (ITS: 10000002-10000101)
- 100 Coordinators (ITS: 10000102-10000201)
- 50 Doctors (ITS: 10000202-10000251)
- 200 Students (ITS: 10000252-10000451)
- 550 Patients (ITS: 10000452-10001001)

All mock users have password: `pass1234`

## ITS API Integration

### Mock ITS Service (Development)
- Located in `accounts/services.py`
- Generates consistent user data based on ITS ID
- Simulates role assignment logic

### Real ITS API (Production)
To integrate with real ITS API, update `ITSService` class:

```python
class ITSService:
    @classmethod
    def authenticate_user(cls, its_id, password):
        # Call actual ITS API
        response = requests.post(
            'https://its-api.example.com/authenticate',
            json={'its_id': its_id, 'password': password}
        )
        
        if response.status_code == 200:
            user_data = response.json()
            role = cls.determine_user_role(user_data)
            return {
                'authenticated': True,
                'user_data': user_data,
                'role': role
            }
        return None
```

## Role-Based Access Control

### Aamil Permissions
- View all moze in their region
- Manage moze coordinators
- Approve/reject petitions
- View all reports and statistics
- Access to all community data

### Moze Coordinator Permissions
- View assigned moze only
- Manage moze activities
- Create reports for their moze
- Limited petition management

### Doctor Permissions
- Manage patient appointments
- View patient medical records
- Create prescriptions
- Access doctor dashboard

### Student Permissions
- View enrolled courses
- Submit assignments
- View evaluations
- Access student resources

### Patient Permissions
- View own medical records
- Book appointments
- View prescriptions
- Update profile

## Testing Different Roles

### Test as Doctor
```
ITS ID: 10000202
Password: pass1234
Expected: Redirected to doctor dashboard
```

### Test as Aamil
```
ITS ID: 10000002
Password: pass1234
Expected: Redirected to moze dashboard with full access
```

### Test as Student
```
ITS ID: 10000252
Password: pass1234
Expected: Redirected to student dashboard
```

### Test as Patient
```
ITS ID: 10000500
Password: pass1234
Expected: Redirected to patient profile
```

## Troubleshooting

### User gets wrong role
1. Check ITS data occupation/category fields
2. Verify ITS ID is in correct uploaded list
3. Check `determine_user_role()` logic in `services.py`

### Cannot upload ITS IDs
1. Ensure CSV format is correct
2. Check file permissions
3. Verify ITS IDs are 8 digits

### Authentication fails
1. Check ITS ID format (8 digits)
2. Verify password meets requirements
3. Check ITS API connectivity

## Security Considerations

1. **ITS IDs are validated** for format (8 digits)
2. **Passwords are never stored** - only ITS authentication
3. **Role changes require** re-authentication
4. **Session timeout** after inactivity
5. **All ITS data is synced** on each login