# Araz App REST API Documentation

## Overview

The Araz app provides a comprehensive REST API for managing medical requests (DuaAraz) and general petitions/complaints. The system supports role-based access control, status tracking, comments, assignments, and notifications.

## Base URL

All API endpoints are available under:
```
/api/araz/
```

## Authentication

All endpoints require JWT authentication. Include the access token in the request header:
```
Authorization: Bearer <access_token>
```

## API Endpoints

### Dashboard

#### GET /api/araz/dashboard/
**Get comprehensive dashboard data**

Returns statistics, recent items, and user permissions for the Araz system.

**Response (200 OK):**
```json
{
    "araz_stats": {
        "total_araz": 150,
        "pending_araz": 45,
        "in_progress_araz": 30,
        "completed_araz": 65,
        "emergency_araz": 10,
        "overdue_araz": 8,
        "recent_araz": 15,
        "araz_by_type": {
            "consultation": 80,
            "emergency": 10,
            "follow_up": 25,
            "chronic_care": 15
        },
        "araz_by_urgency": {
            "low": 40,
            "medium": 70,
            "high": 30,
            "emergency": 10
        },
        "araz_by_status": {
            "submitted": 25,
            "in_progress": 30,
            "completed": 65,
            "cancelled": 10
        }
    },
    "petition_stats": {
        "total_petitions": 85,
        "pending_petitions": 20,
        "in_progress_petitions": 15,
        "resolved_petitions": 40,
        "rejected_petitions": 10,
        "overdue_petitions": 5,
        "recent_petitions": 12
    },
    "recent_araz": [...],
    "recent_petitions": [...],
    "unread_notifications": 3,
    "user_permissions": {
        "can_manage_araz": true,
        "can_manage_petitions": true,
        "can_create_categories": false
    }
}
```

## DuaAraz (Medical Requests) API

### List and Create Araz Requests

#### GET /api/araz/araz/
**List Araz requests**

Returns paginated list of Araz requests based on user permissions.

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Number of results per page (default: 20)
- `search`: Search in patient name, ITS ID, ailment, symptoms
- `status`: Filter by status (submitted, under_review, approved, etc.)
- `urgency_level`: Filter by urgency (low, medium, high, emergency)
- `request_type`: Filter by request type (consultation, emergency, etc.)
- `priority`: Filter by priority
- `assigned_doctor`: Filter by assigned doctor ID
- `ordering`: Sort by fields (e.g., `-created_at`, `urgency_level`)

**Example Request:**
```
GET /api/araz/araz/?urgency_level=high&status=submitted&ordering=-created_at
```

**Response (200 OK):**
```json
{
    "count": 25,
    "next": "http://localhost:8000/api/araz/araz/?page=2",
    "previous": null,
    "results": [
        {
            "id": 123,
            "patient_its_id": "12345678",
            "patient_name": "Ahmed Ali",
            "patient_phone": "+91-9876543210",
            "patient_email": "ahmed@example.com",
            "patient_user": {
                "id": 45,
                "username": "ahmed_ali",
                "first_name": "Ahmed",
                "last_name": "Ali"
            },
            "ailment": "Severe chest pain and shortness of breath",
            "symptoms": "Sharp chest pain, difficulty breathing, dizziness",
            "urgency_level": "high",
            "urgency_level_display": "High - Urgent attention needed",
            "request_type": "emergency",
            "request_type_display": "Emergency Case",
            "previous_medical_history": "History of heart disease",
            "current_medications": "Aspirin 75mg daily",
            "allergies": "Penicillin allergy",
            "preferred_doctor": {
                "id": 12,
                "user": 67,
                "full_name": "Dr. Sarah Khan",
                "specialty": "Cardiology",
                "license_number": "DOC789"
            },
            "preferred_location": "Mumbai Central Hospital",
            "preferred_time": "2025-01-04T14:00:00Z",
            "preferred_contact_method": "phone",
            "status": "submitted",
            "status_display": "Submitted",
            "priority": "urgent",
            "priority_display": "Urgent",
            "assigned_doctor": null,
            "assigned_date": null,
            "scheduled_date": null,
            "admin_notes": "",
            "patient_feedback": "",
            "created_at": "2025-01-03T10:30:00Z",
            "updated_at": "2025-01-03T10:30:00Z",
            "days_since_created": 1,
            "is_overdue": false,
            "comments": [],
            "attachments": [],
            "status_history": [],
            "notifications": []
        }
    ]
}
```

#### POST /api/araz/araz/
**Create new Araz request**

Create a new medical request.

**Request Body:**
```json
{
    "patient_its_id": "12345678",
    "patient_name": "Ahmed Ali",
    "patient_phone": "+91-9876543210",
    "patient_email": "ahmed@example.com",
    "ailment": "Severe headache and fever",
    "symptoms": "Persistent headache for 3 days, fever 101°F",
    "urgency_level": "high",
    "request_type": "consultation",
    "previous_medical_history": "No significant medical history",
    "current_medications": "Paracetamol as needed",
    "allergies": "None known",
    "preferred_doctor_id": 12,
    "preferred_location": "Mumbai Central",
    "preferred_time": "2025-01-04T14:00:00Z",
    "preferred_contact_method": "phone"
}
```

**Response (201 Created):**
```json
{
    "id": 124,
    "patient_its_id": "12345678",
    "patient_name": "Ahmed Ali",
    "ailment": "Severe headache and fever",
    // ... full Araz object
}
```

### Individual Araz Request Operations

#### GET /api/araz/araz/{id}/
**Get Araz request details**

Retrieve detailed information about a specific Araz request.

#### PATCH /api/araz/araz/{id}/
**Update Araz request**

Update an existing Araz request. Status changes automatically create history records and notifications.

**Request Body (partial update):**
```json
{
    "status": "in_progress",
    "assigned_doctor": 12,
    "admin_notes": "Patient consultation scheduled for tomorrow",
    "scheduled_date": "2025-01-04T10:00:00Z"
}
```

#### DELETE /api/araz/araz/{id}/
**Delete Araz request**

Delete an Araz request (restricted to patient, assigned doctor, or admin).

### Advanced Search

#### POST /api/araz/araz/search/
**Advanced Araz search**

Perform complex searches with multiple criteria.

**Request Body:**
```json
{
    "query": "diabetes",
    "status": "submitted",
    "urgency_level": "high",
    "request_type": "chronic_care",
    "priority": "urgent",
    "assigned_doctor": 12,
    "date_from": "2025-01-01T00:00:00Z",
    "date_to": "2025-01-31T23:59:59Z",
    "is_overdue": true
}
```

**Response (200 OK):**
```json
{
    "count": 5,
    "results": [
        // ... array of matching Araz objects
    ]
}
```

## Petition API

### List and Create Petitions

#### GET /api/araz/petitions/
**List petitions**

Returns paginated list of petitions based on user permissions.

**Query Parameters:**
- `page`: Page number
- `search`: Search in title, description
- `status`: Filter by status (pending, in_progress, resolved, rejected)
- `priority`: Filter by priority (low, medium, high)
- `category`: Filter by category ID
- `moze`: Filter by Moze center ID
- `ordering`: Sort by fields

#### POST /api/araz/petitions/
**Create new petition**

**Request Body:**
```json
{
    "title": "Facility Improvement Request",
    "description": "The community center needs better lighting and seating arrangements for elderly members.",
    "category_id": 3,
    "priority": "medium",
    "moze": 5,
    "is_anonymous": false
}
```

### Individual Petition Operations

#### GET /api/araz/petitions/{id}/
**Get petition details**

#### PATCH /api/araz/petitions/{id}/
**Update petition**

Status changes automatically create update records and set resolved_at timestamp.

#### DELETE /api/araz/petitions/{id}/
**Delete petition**

### Petition Search

#### POST /api/araz/petitions/search/
**Advanced petition search**

**Request Body:**
```json
{
    "query": "infrastructure",
    "status": "pending",
    "priority": "high",
    "category": 2,
    "created_by": 15,
    "assigned_to": 20,
    "moze": 5,
    "date_from": "2025-01-01T00:00:00Z",
    "date_to": "2025-01-31T23:59:59Z",
    "is_overdue": true
}
```

## Category Management

#### GET /api/araz/categories/
**List petition categories**

Returns active petition categories.

#### POST /api/araz/categories/
**Create category** (Admin only)

**Request Body:**
```json
{
    "name": "Infrastructure Issues",
    "description": "Problems related to building and facility infrastructure",
    "color": "#dc3545"
}
```

#### GET /api/araz/categories/{id}/
**Get category details**

#### PATCH /api/araz/categories/{id}/
**Update category** (Admin only)

#### DELETE /api/araz/categories/{id}/
**Delete category** (Admin only)

## Comments

### Araz Comments

#### GET /api/araz/araz/{araz_id}/comments/
**List Araz comments**

Returns comments for a specific Araz request. Internal comments are only visible to authorized users.

#### POST /api/araz/araz/{araz_id}/comments/
**Create Araz comment**

**Request Body:**
```json
{
    "content": "Patient has provided additional symptoms information",
    "is_internal": false
}
```

### Petition Comments

#### GET /api/araz/petitions/{petition_id}/comments/
**List petition comments**

#### POST /api/araz/petitions/{petition_id}/comments/
**Create petition comment**

**Request Body:**
```json
{
    "content": "We are reviewing this issue and will provide an update soon",
    "is_internal": false
}
```

## Assignment Management

#### POST /api/araz/petitions/{petition_id}/assign/
**Assign petition to user**

Assign a petition to a specific user for handling.

**Request Body:**
```json
{
    "assigned_to_id": 25,
    "notes": "Please handle this urgent petition regarding facility issues"
}
```

**Response (201 Created):**
```json
{
    "id": 15,
    "assigned_to": {
        "id": 25,
        "username": "aamil_user",
        "first_name": "Aamil",
        "last_name": "Rahman"
    },
    "assigned_by": {
        "id": 1,
        "username": "admin",
        "first_name": "Admin",
        "last_name": "User"
    },
    "assigned_at": "2025-01-03T15:30:00Z",
    "notes": "Please handle this urgent petition regarding facility issues",
    "is_active": true
}
```

## Statistics

#### GET /api/araz/stats/araz/
**Get Araz statistics**

Returns comprehensive statistics for Araz requests based on user permissions.

**Response (200 OK):**
```json
{
    "total_araz": 150,
    "pending_araz": 45,
    "in_progress_araz": 30,
    "completed_araz": 65,
    "emergency_araz": 10,
    "overdue_araz": 8,
    "recent_araz": 15,
    "araz_by_type": {
        "consultation": 80,
        "emergency": 10,
        "follow_up": 25,
        "chronic_care": 15,
        "prescription": 20
    },
    "araz_by_urgency": {
        "low": 40,
        "medium": 70,
        "high": 30,
        "emergency": 10
    },
    "araz_by_status": {
        "submitted": 25,
        "under_review": 20,
        "in_progress": 30,
        "completed": 65,
        "cancelled": 10
    }
}
```

#### GET /api/araz/stats/petitions/
**Get petition statistics**

Returns comprehensive statistics for petitions.

## Notifications

#### GET /api/araz/notifications/
**List user notifications**

Returns notifications for the authenticated user.

**Response (200 OK):**
```json
{
    "count": 5,
    "results": [
        {
            "id": 45,
            "message": "Your Araz request status has been updated to In Progress",
            "notification_type": "status_update",
            "recipient": {
                "id": 25,
                "username": "patient_user"
            },
            "is_read": false,
            "created_at": "2025-01-03T14:30:00Z"
        }
    ]
}
```

#### PATCH /api/araz/notifications/{notification_id}/read/
**Mark notification as read**

**Response (200 OK):**
```json
{
    "message": "Notification marked as read"
}
```

#### PATCH /api/araz/notifications/mark-all-read/
**Mark all notifications as read**

**Response (200 OK):**
```json
{
    "message": "All notifications marked as read"
}
```

## Data Models

### DuaAraz Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Unique identifier |
| `patient_its_id` | String | 8-digit ITS ID |
| `patient_name` | String | Patient's full name |
| `patient_phone` | String | Contact phone number |
| `patient_email` | Email | Contact email |
| `patient_user` | Object | Linked user account (if registered) |
| `ailment` | Text | Description of medical condition |
| `symptoms` | Text | Detailed symptoms |
| `urgency_level` | String | low, medium, high, emergency |
| `request_type` | String | consultation, emergency, follow_up, etc. |
| `previous_medical_history` | Text | Patient's medical history |
| `current_medications` | Text | Current medications |
| `allergies` | Text | Known allergies |
| `preferred_doctor` | Object | Preferred doctor details |
| `preferred_location` | String | Preferred consultation location |
| `preferred_time` | DateTime | Preferred appointment time |
| `preferred_contact_method` | String | phone, email, sms, whatsapp, in_person |
| `status` | String | submitted, under_review, approved, scheduled, in_progress, completed, rejected, cancelled, follow_up_required |
| `priority` | String | low, medium, high, urgent |
| `assigned_doctor` | Object | Assigned doctor details |
| `assigned_date` | DateTime | When doctor was assigned |
| `scheduled_date` | DateTime | Scheduled appointment time |
| `admin_notes` | Text | Internal administrative notes |
| `patient_feedback` | Text | Patient's feedback |
| `created_at` | DateTime | Creation timestamp |
| `updated_at` | DateTime | Last update timestamp |

### Petition Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Unique identifier |
| `title` | String | Petition title |
| `description` | Text | Detailed description |
| `category` | Object | Petition category |
| `created_by` | Object | User who created the petition |
| `is_anonymous` | Boolean | Whether petition is anonymous |
| `status` | String | pending, in_progress, resolved, rejected |
| `priority` | String | low, medium, high |
| `moze` | Object | Related Moze center |
| `created_at` | DateTime | Creation timestamp |
| `updated_at` | DateTime | Last update timestamp |
| `resolved_at` | DateTime | Resolution timestamp |

## Request Types

### DuaAraz Request Types

- `consultation` - Medical Consultation
- `prescription` - Prescription Request
- `follow_up` - Follow-up Appointment
- `health_check` - General Health Check
- `emergency` - Emergency Case
- `referral` - Specialist Referral
- `second_opinion` - Second Opinion
- `home_visit` - Home Visit Request
- `telemedicine` - Telemedicine Consultation
- `laboratory` - Laboratory Tests
- `imaging` - Medical Imaging
- `therapy` - Physical Therapy
- `vaccination` - Vaccination
- `chronic_care` - Chronic Disease Management
- `mental_health` - Mental Health Support
- `nutrition` - Nutrition Consultation
- `dental` - Dental Care
- `ophthalmology` - Eye Care
- `pediatric` - Pediatric Care
- `geriatric` - Geriatric Care
- `womens_health` - Women's Health
- `mens_health` - Men's Health
- `rehabilitation` - Rehabilitation Services
- `pain_management` - Pain Management
- `allergy` - Allergy Treatment
- `other` - Other

### Status Transitions

#### DuaAraz Status Flow
```
submitted → under_review → approved → scheduled → in_progress → completed
                      ↓
                   rejected
                      ↓
                   cancelled
```

#### Petition Status Flow
```
pending → in_progress → resolved
             ↓
          rejected
```

## Overdue Calculations

### DuaAraz Overdue Thresholds
- **Emergency**: > 1 day
- **High**: > 3 days
- **Medium**: > 7 days
- **Low**: > 14 days

### Petition Overdue Thresholds
- **High Priority**: > 3 days
- **Medium Priority**: > 7 days
- **Low Priority**: > 14 days

## Permissions and Access Control

### Role-Based Access

| Role | Araz Permissions | Petition Permissions |
|------|------------------|---------------------|
| **Admin** | Full access to all Araz requests | Full access to all petitions |
| **Doctor** | Assigned/preferred Araz + own submissions | Own petitions + assigned ones |
| **Aamil** | Own submissions + managed Moze Araz | Own + Moze petitions + assigned ones |
| **Moze Coordinator** | Own submissions + coordinated Moze Araz | Own + coordinated Moze petitions + assigned ones |
| **Patient/Student** | Own submissions only | Own petitions + assigned ones |

### Action Permissions

| Action | Who Can Perform |
|--------|-----------------|
| Create Araz | Any authenticated user |
| Update Araz | Patient, assigned doctor, admin |
| Delete Araz | Patient, assigned doctor, admin |
| Create Petition | Any authenticated user |
| Update Petition | Creator, assignee, admin |
| Delete Petition | Creator, assignee, admin |
| Assign Petition | Admin, aamil, moze coordinator |
| Create Category | Admin only |
| View Internal Comments | Admin, doctors (for Araz), admin/aamil/coordinator (for petitions) |

## Error Responses

### 400 Bad Request
```json
{
    "field_name": ["Error message"],
    "non_field_errors": ["General error message"]
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

## Example Usage

### Complete Araz Request Flow

```python
import requests

# 1. Create Araz request
headers = {'Authorization': 'Bearer <access_token>'}
araz_data = {
    'patient_its_id': '12345678',
    'ailment': 'Severe chest pain',
    'urgency_level': 'high',
    'request_type': 'emergency',
    'preferred_contact_method': 'phone'
}

response = requests.post(
    'http://localhost:8000/api/araz/araz/',
    json=araz_data,
    headers=headers
)
araz = response.json()

# 2. Doctor updates status
update_data = {
    'status': 'in_progress',
    'admin_notes': 'Patient scheduled for immediate consultation'
}

requests.patch(
    f'http://localhost:8000/api/araz/araz/{araz["id"]}/',
    json=update_data,
    headers=headers
)

# 3. Add comment
comment_data = {
    'content': 'Patient provided additional symptoms',
    'is_internal': False
}

requests.post(
    f'http://localhost:8000/api/araz/araz/{araz["id"]}/comments/',
    json=comment_data,
    headers=headers
)
```

### Petition Management Flow

```python
# 1. Create petition
petition_data = {
    'title': 'Facility Improvement',
    'description': 'Request for better facilities',
    'category_id': 1,
    'priority': 'medium'
}

response = requests.post(
    'http://localhost:8000/api/araz/petitions/',
    json=petition_data,
    headers=headers
)
petition = response.json()

# 2. Assign to user
assignment_data = {
    'assigned_to_id': 25,
    'notes': 'Please handle this facility request'
}

requests.post(
    f'http://localhost:8000/api/araz/petitions/{petition["id"]}/assign/',
    json=assignment_data,
    headers=headers
)

# 3. Update status
requests.patch(
    f'http://localhost:8000/api/araz/petitions/{petition["id"]}/',
    json={'status': 'resolved'},
    headers=headers
)
```

### Search and Analytics

```python
# Advanced search
search_data = {
    'query': 'diabetes',
    'urgency_level': 'high',
    'is_overdue': True
}

overdue_araz = requests.post(
    'http://localhost:8000/api/araz/araz/search/',
    json=search_data,
    headers=headers
).json()

# Get statistics
araz_stats = requests.get(
    'http://localhost:8000/api/araz/stats/araz/',
    headers=headers
).json()

petition_stats = requests.get(
    'http://localhost:8000/api/araz/stats/petitions/',
    headers=headers
).json()

# Dashboard data
dashboard = requests.get(
    'http://localhost:8000/api/araz/dashboard/',
    headers=headers
).json()
```

This comprehensive API enables efficient management of medical requests and community petitions with role-based access control, status tracking, and real-time notifications.