# 🏥 Umoor Sehhat - Medical & Educational Management System

A comprehensive Django-based web application for managing medical and educational institutions, designed specifically for healthcare and academic management.

## 🌟 Features

### 🔐 User Management (Accounts)
- Role-based authentication system
- User profiles with ITS ID verification
- Multiple user roles: Admin, Aamil, Doctor, Student, Teacher, Staff

### 🎓 Student Management System
- Student enrollment and academic tracking
- Course management and scheduling
- Grade recording and analytics
- Attendance management
- Assignment submission system

### 📋 Survey System
- Dynamic survey creation with multiple question types
- Role-based survey distribution
- Response collection and analytics
- Anonymous survey support

### 🏥 Mahalshifa (Hospital Management)
- Hospital and patient management
- Appointment scheduling system
- Medical inventory tracking
- Healthcare analytics and reporting

### 🕌 Moze (Religious Center Management)
- Center management and administration
- Community engagement features
- Analytics and reporting

### 📸 Photo Gallery Management
- Album creation and organization
- Photo upload and management
- Tag-based photo categorization
- User photo sharing

### 👨‍⚕️ Doctor Directory
- Doctor profile management
- Appointment booking system
- Patient management
- Medical record keeping

### 📝 Evaluation System
- Performance evaluation forms
- Submission tracking
- Analytics and reporting
- Multi-criteria evaluation support

### 📄 Araz (Petition Management)
- Petition submission and tracking
- Workflow management
- Assignment system
- Status tracking and analytics

## 🛠️ Technology Stack

- **Backend**: Django 4.2+
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: HTML5, CSS3, Bootstrap
- **Authentication**: Django's built-in auth system with custom user model
- **File Storage**: Django file handling with Pillow for images

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd umoor_sehhat
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Open your browser and go to `http://localhost:8000`
   - Admin panel: `http://localhost:8000/admin/`

## 📱 Application Structure

```
umoor_sehhat/
├── accounts/           # User management and authentication
├── students/          # Student management system
├── surveys/           # Survey creation and management
├── mahalshifa/        # Hospital management
├── moze/              # Religious center management
├── photos/            # Photo gallery management
├── doctordirectory/   # Doctor profiles and appointments
├── evaluation/        # Evaluation system
├── araz/              # Petition management
├── templates/         # HTML templates
├── static/            # Static files (CSS, JS, images)
├── media/             # User-uploaded files
└── umoor_sehhat/      # Main project settings
```

## 👥 User Roles & Permissions

- **Admin**: Full system access and management
- **Aamil**: Regional management capabilities
- **Doctor**: Medical functionality and patient management
- **Student**: Educational features and personal data access
- **Teacher**: Course management and student evaluation
- **Staff**: Limited administrative functions

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=your-database-url
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Database Configuration
The project uses SQLite by default for development. For production, configure PostgreSQL in `settings.py`.

## 📊 Key Features

### Medical Management
- Patient registration and management
- Appointment scheduling
- Medical inventory tracking
- Healthcare analytics

### Educational Management
- Student enrollment and tracking
- Course and curriculum management
- Grade and attendance recording
- Academic analytics

### Administrative Tools
- User role management
- Survey and evaluation systems
- Petition and workflow management
- Comprehensive reporting

## 🛡️ Security Features

- Role-based access control
- User authentication and authorization
- Data validation and sanitization
- Secure file upload handling
- Session management

## 📈 Performance

- Optimized database queries
- Efficient template rendering
- Proper caching strategies
- Scalable architecture

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions, please contact the development team or create an issue in the repository.

---

**Built with ❤️ for healthcare and educational management**