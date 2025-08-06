# Accounts App REST API Documentation

## Overview

The Accounts app provides a comprehensive REST API for user management, authentication, and ITS (Information Technology Services) integration. This API supports JWT-based authentication, role-based access control, and synchronization with external ITS systems.

## Base URL

All API endpoints are available under:
```
/api/accounts/
```

## Authentication

The API supports two authentication methods:

### 1. JWT Authentication (Recommended)
- **Access Token**: Valid for 60 minutes
- **Refresh Token**: Valid for 7 days
- **Header Format**: `Authorization: Bearer <access_token>`

### 2. Session Authentication
- Uses Django's built-in session framework
- Suitable for web applications

## API Endpoints

### Authentication Endpoints

#### POST /api/accounts/auth/login/
**JWT Token Generation**

Generate access and refresh tokens for authentication.

**Request Body:**
```json
{
    "username": "string",
    "password": "string"
}
```

Or with ITS ID:
```json
{
    "its_id": "12345678",
    "password": "string"
}
```

**Response (200 OK):**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "role": "student",
        "its_id": "12345678",
        // ... other user fields
    }
}
```

#### POST /api/accounts/auth/refresh/
**Token Refresh**

Refresh the access token using a valid refresh token.

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### POST /api/accounts/auth/login-session/
**Session-based Login**

Alternative login method using Django sessions.

**Request Body:**
```json
{
    "username": "string",
    "password": "string"
}
```

#### POST /api/accounts/auth/logout/
**Logout**

Logout and invalidate tokens.

**Request Body:**
```json
{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### User Profile Endpoints

#### GET /api/accounts/me/
**Get Current User Profile**

Retrieve the authenticated user's profile information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "role": "student",
    "its_id": "12345678",
    "arabic_full_name": "جون دو",
    "prefix": "Mr",
    "age": 25,
    "gender": "male",
    "marital_status": "single",
    "misaq": "Misaq 1445H",
    "occupation": "Student",
    "qualification": "Bachelor of Engineering",
    "idara": "Mumbai",
    "category": "Student",
    "organization": "Al-Jamea-tus-Saifiyah",
    "mobile_number": "+91-9876543210",
    "whatsapp_number": "+91-9876543210",
    "address": "123 Main Street, Mumbai",
    "jamaat": "Mumbai Central",
    "jamiaat": "Mumbai Central Jamiaat",
    "nationality": "Indian",
    "vatan": "Mumbai",
    "city": "Mumbai",
    "country": "India",
    "hifz_sanad": "Complete",
    "photograph": "/media/profile_photos/john.jpg",
    "phone_number": "+91-9876543210",
    "profile_photo": "https://example.com/photo.jpg",
    "specialty": "Computer Science",
    "college": "Al-Jamea-tus-Saifiyah",
    "specialization": "Software Engineering",
    "its_last_sync": "2025-01-03T10:30:00Z",
    "its_sync_status": "synced",
    "is_active": true,
    "date_joined": "2025-01-01T00:00:00Z",
    "last_login": "2025-01-03T09:00:00Z",
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-03T10:30:00Z"
}
```

#### PUT/PATCH /api/accounts/me/
**Update Current User Profile**

Update the authenticated user's profile information.

**Request Body (PATCH - partial update):**
```json
{
    "first_name": "Jonathan",
    "occupation": "Software Engineer",
    "city": "Pune"
}
```

### User Management Endpoints

#### GET /api/accounts/users/
**List Users**

Retrieve a paginated list of users with filtering and search capabilities.

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Number of results per page (default: 20)
- `search`: Search in name, email, username, ITS ID
- `role`: Filter by user role
- `jamaat`: Filter by jamaat
- `city`: Filter by city
- `country`: Filter by country
- `is_active`: Filter by active status
- `ordering`: Sort by fields (e.g., `first_name`, `-date_joined`)

**Example Request:**
```
GET /api/accounts/users/?role=student&city=Mumbai&search=ahmed&ordering=-date_joined
```

**Response (200 OK):**
```json
{
    "count": 150,
    "next": "http://localhost:8000/api/accounts/users/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "username": "ahmed_khan",
            "email": "ahmed@example.com",
            // ... other user fields
        }
        // ... more users
    ]
}
```

#### POST /api/accounts/users/
**Create User** (Admin Only)

Create a new user account.

**Request Body:**
```json
{
    "username": "new_user",
    "email": "newuser@example.com",
    "password": "SecurePass123!",
    "confirm_password": "SecurePass123!",
    "first_name": "Ahmed",
    "last_name": "Khan",
    "role": "student",
    "its_id": "87654321",
    "mobile_number": "+91-9876543210"
}
```

#### GET /api/accounts/users/{id}/
**Get User Details**

Retrieve details of a specific user.

#### PUT/PATCH /api/accounts/users/{id}/
**Update User**

Update a specific user's information. Users can only update their own profile unless they are administrators.

#### DELETE /api/accounts/users/{id}/
**Delete User** (Admin Only)

Delete a user account.

### Advanced Search

#### POST /api/accounts/users/search/
**Advanced User Search**

Perform advanced search with complex criteria.

**Request Body:**
```json
{
    "query": "ahmed",
    "role": "student",
    "jamaat": "Mumbai Central",
    "city": "Mumbai",
    "is_active": true
}
```

### ITS Synchronization Endpoints

#### POST /api/accounts/its/sync/
**Sync Single User from ITS**

Synchronize a user's data from the ITS system.

**Request Body:**
```json
{
    "its_id": "12345678",
    "force_update": false
}
```

**Response (201 Created - New User):**
```json
{
    "message": "User created successfully",
    "user": {
        // ... user data
    }
}
```

**Response (200 OK - Existing User):**
```json
{
    "message": "User updated successfully",
    "user": {
        // ... updated user data
    }
}
```

#### POST /api/accounts/its/bulk-sync/
**Bulk ITS Synchronization**

Synchronize multiple users from the ITS system.

**Request Body:**
```json
{
    "its_ids": ["12345678", "87654321", "11111111"]
}
```

**Response (200 OK):**
```json
{
    "message": "Processed 3 ITS IDs",
    "results": [
        {
            "its_id": "12345678",
            "status": "success",
            "data": {
                // ... user data
            }
        },
        {
            "its_id": "87654321",
            "status": "not_found",
            "error": "User not found in ITS system"
        }
        // ... more results
    ]
}
```

### Security Endpoints

#### POST /api/accounts/change-password/
**Change Password**

Change the authenticated user's password.

**Request Body:**
```json
{
    "old_password": "currentpass123",
    "new_password": "newpass456!",
    "confirm_password": "newpass456!"
}
```

### Statistics and Audit

#### GET /api/accounts/stats/
**User Statistics**

Get system-wide user statistics.

**Response (200 OK):**
```json
{
    "total_users": 500,
    "active_users": 450,
    "users_by_role": [
        {
            "role": "student",
            "count": 200
        },
        {
            "role": "doctor",
            "count": 50
        }
        // ... other roles
    ],
    "recent_registrations": 25,
    "its_synced_users": 400
}
```

#### GET /api/accounts/audit-logs/
**Audit Logs** (Admin Only)

Retrieve audit logs for user activities.

**Query Parameters:**
- `user`: Filter by user ID
- `action`: Filter by action type
- `ordering`: Sort by timestamp

## Error Responses

### 400 Bad Request
```json
{
    "error": "Validation failed",
    "details": {
        "field_name": ["Error message"]
    }
}
```

### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
    "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
    "detail": "Not found."
}
```

### 500 Internal Server Error
```json
{
    "error": "Internal server error",
    "detail": "An unexpected error occurred."
}
```

## User Roles

The system supports the following user roles:

- **aamil**: Community leader with management responsibilities
- **moze_coordinator**: Coordinator for Moze centers
- **doctor**: Medical practitioners
- **student**: Students and learners
- **badri_mahal_admin**: Administrative users

## ITS Integration

### Mock ITS Service

For development and testing, the system includes a mock ITS service that generates realistic user data based on ITS ID patterns.

### Real ITS Integration

In production, the system can be configured to connect to the actual ITS API by updating the `USER_API_URL` setting in Django configuration.

## Rate Limiting

- Authentication endpoints: 5 requests per minute per IP
- User creation: 10 requests per hour for non-admin users
- ITS sync: 100 requests per hour per user

## Data Privacy

- Personal data is handled according to privacy regulations
- Sensitive fields are not included in list views
- Users can only access their own data unless they have administrative privileges

## Testing

The API includes comprehensive test coverage:

```bash
# Run all API tests
python manage.py test accounts.tests.test_api

# Run specific test class
python manage.py test accounts.tests.test_api.AuthenticationAPITests

# Run with verbosity
python manage.py test accounts.tests.test_api -v 2
```

## Examples

### Complete Authentication Flow

```python
import requests

# 1. Login and get tokens
response = requests.post('http://localhost:8000/api/accounts/auth/login/', {
    'username': 'john_doe',
    'password': 'password123'
})
tokens = response.json()

# 2. Use access token for authenticated requests
headers = {
    'Authorization': f'Bearer {tokens["access"]}'
}

# 3. Get user profile
profile = requests.get(
    'http://localhost:8000/api/accounts/me/',
    headers=headers
).json()

# 4. Update profile
updated_profile = requests.patch(
    'http://localhost:8000/api/accounts/me/',
    headers=headers,
    json={'occupation': 'Software Engineer'}
).json()

# 5. Refresh token when needed
new_tokens = requests.post(
    'http://localhost:8000/api/accounts/auth/refresh/',
    json={'refresh': tokens['refresh']}
).json()
```

### ITS Synchronization Example

```python
# Sync a single user from ITS
sync_response = requests.post(
    'http://localhost:8000/api/accounts/its/sync/',
    headers=headers,
    json={
        'its_id': '12345678',
        'force_update': True
    }
)

# Bulk sync multiple users
bulk_sync = requests.post(
    'http://localhost:8000/api/accounts/its/bulk-sync/',
    headers=headers,
    json={
        'its_ids': ['12345678', '87654321', '11111111']
    }
)
```

## Pagination Example

```python
# Get first page of users
users_page1 = requests.get(
    'http://localhost:8000/api/accounts/users/?page=1&page_size=10',
    headers=headers
).json()

# Navigate through pages
next_url = users_page1.get('next')
if next_url:
    users_page2 = requests.get(next_url, headers=headers).json()
```

## Filtering and Search Example

```python
# Search for students in Mumbai
students = requests.get(
    'http://localhost:8000/api/accounts/users/',
    headers=headers,
    params={
        'role': 'student',
        'city': 'Mumbai',
        'search': 'ahmed',
        'is_active': True,
        'ordering': '-date_joined'
    }
).json()
```

This API documentation provides a complete reference for integrating with the Accounts app REST API, supporting user management, authentication, and ITS synchronization for the Umoor Sehhat healthcare management system.