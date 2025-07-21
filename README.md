# Umoor Sehhat Digital System

A comprehensive Django web application for managing healthcare services, built for the Umoor Sehhat organization. This system provides role-based access control for different types of users including Aamils, Moze Coordinators, Doctors, Students, and Badri Mahal Admins.

## Features

### Phase 1 - Core Features ✅
- **Multi-role Authentication System**: Custom user model with 5 distinct roles
- **Role-based Access Control**: Middleware and decorators for data isolation
- **Moze Management**: Medical center registration, team management, and coordination
- **Doctor Directory**: Doctor profiles, scheduling, and patient logs
- **Photo Gallery**: Organized photo management with categorization and tagging
- **Survey System**: Dynamic surveys with JSON-based questions and analytics
- **Evaluation System**: Moze evaluation with automated grading (A-E scale)
- **Dua Araz**: Patient request and petition management system
- **Student Management**: Academic profiles, mentorship, and aid requests
- **Medical Records**: Comprehensive patient care tracking in Mahal Shifa

### Phase 2 - Advanced Features (In Development)
- **ITS API Integration**: Mock ITS system for user verification
- **Email Notifications**: Automated notifications for key events
- **PDF Generation**: Export capabilities for schedules and reports
- **Advanced Search & Filtering**: Enhanced discovery across all modules
- **Bulk Upload**: CSV-based data import functionality
- **Mobile Responsive Design**: Bootstrap 5 with modern UI/UX

## Technology Stack

- **Backend**: Django 5.0.1
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Frontend**: Django Templates + Bootstrap 5
- **Authentication**: Custom AbstractUser with role-based permissions
- **File Handling**: Pillow for image processing
- **PDF Generation**: ReportLab + xhtml2pdf
- **API**: Django REST Framework (for future integrations)

## User Roles

| Role | Access Level | Permissions |
|------|-------------|-------------|
| **Badri Mahal Admin** | Full Access | Complete system administration |
| **Aamil** | Moze Management | Manage assigned Moze, team members, photos |
| **Moze Coordinator** | Operations | Coordinate Moze activities, surveys, directories |
| **Doctor** | Medical Care | Patient logs, schedules, medical records |
| **Student** | Academic | Profile management, mentorship, aid requests |

## Installation & Setup

### Prerequisites
- Python 3.8+
- Django 5.0.1
- Required packages (see below)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd umoor_sehhat
   ```

2. **Install dependencies**
   ```bash
   pip install Django==5.0.1 djangorestframework psycopg2-binary pillow reportlab xhtml2pdf django-extensions
   ```

3. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```
   - Use role: `badri_mahal_admin`
   - Provide a valid 8-digit ITS ID

5. **Run development server**
   ```bash
   python manage.py runserver
   ```

6. **Access the application**
   - Open http://127.0.0.1:8000
   - Login with your superuser credentials
   - Explore the role-based dashboard

### Default Credentials (for testing)
- **Username**: admin
- **Password**: admin123
- **Role**: Badri Mahal Admin
- **ITS ID**: 00000000

## Project Structure

```
umoor_sehhat/
├── accounts/           # User management & authentication
├── moze/              # Medical center management
├── doctordirectory/   # Doctor profiles & scheduling
├── mahalshifa/        # Patient care & medical records
├── photos/            # Photo gallery & management
├── surveys/           # Dynamic survey system
├── evaluation/        # Moze evaluation & grading
├── araz/              # Patient petitions & requests
├── students/          # Student profiles & services
├── templates/         # HTML templates
├── static/            # Static files (CSS, JS, images)
├── media/             # User uploads
└── manage.py
```

## Key Models

### User Management
- **User**: Extended AbstractUser with role field and ITS ID
- **UserProfile**: Additional profile information

### Medical Services
- **Moze**: Medical centers with team management
- **Doctor**: Doctor profiles with specializations
- **Patient**: Patient records with medical history
- **Appointment**: Medical appointment scheduling
- **MedicalRecord**: Consultation records and treatment plans

### Content Management
- **Photo**: Gallery with categorization and metadata
- **Survey**: Dynamic surveys with JSON questions
- **DuaAraz**: Patient requests and status tracking
- **Evaluation**: Moze performance evaluation system

## API Endpoints (Future)

The system is designed to support REST API endpoints for mobile applications and integrations:

```
/api/auth/          # Authentication endpoints
/api/users/         # User management
/api/moze/          # Moze operations
/api/doctors/       # Doctor directory
/api/patients/      # Patient management
/api/surveys/       # Survey operations
```

## Development Guidelines

### Adding New Features
1. Create models in the appropriate app
2. Add migrations: `python manage.py makemigrations`
3. Update admin.py for admin interface
4. Create views and URL patterns
5. Add templates with Bootstrap 5 styling
6. Test role-based access control

### Database Migrations
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset migrations (if needed)
python manage.py migrate <app_name> zero
```

### Testing
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts
```

## Production Deployment

### Environment Variables
```bash
DEBUG=False
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://user:pass@localhost/dbname
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### PostgreSQL Setup
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'umoor_sehhat_db',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Static Files
```bash
# Collect static files
python manage.py collectstatic
```

## Sample Data

To populate the system with sample data:

```bash
python manage.py shell
```

Then run the sample data creation scripts (to be provided).

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is developed for the Umoor Sehhat organization. All rights reserved.

## Support

For technical support or questions:
- Create an issue in the repository
- Contact the development team
- Review the documentation

---

**Version**: 1.0.0 (Phase 1 Complete)  
**Last Updated**: 2024  
**Developer**: Umoor Sehhat Development Team