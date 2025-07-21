# 🧪 UmoorSehhat Application Testing Guide

## 🎯 Overview
The UmoorSehhat application has been successfully populated with comprehensive test data. This guide helps you test all features systematically.

## 🔐 Test User Credentials

### All users have the password: `password123`

#### 👨‍💼 Badri Mahal Admin
- **Username**: `admin` | **Name**: admin | **ITS ID**: 00000000
- **Username**: `nafisa0` | **Name**: Nafisa Khorakiwala
- **Role**: Full system access, can manage all modules

#### 🕌 Aamils
- **Username**: `aisha24` | **Name**: Aisha Sheikh
- **Username**: `aisha34` | **Name**: Aisha Sheikh  
- **Role**: Moze management, community oversight

#### 🏥 Moze Coordinators
- **Username**: `ahmed20` | **Name**: Ahmed Bharuchi
- **Username**: `ahmed36` | **Name**: Ahmed Bharuchi
- **Role**: Facility coordination, scheduling

#### 👨‍⚕️ Doctors
- **Username**: `drammar40` | **Name**: Dr. Ammar Khorakiwala
- **Username**: `driqbal39` | **Name**: Dr. Iqbal Husain
- **Username**: `drmaryam1` | **Name**: Dr. Maryam Bhatty
- **Role**: Medical services, appointments, patient records

#### 🎓 Students
- **Username**: `ibrahim10` | **Name**: Ibrahim Najmi
- **Username**: `ibrahim37` | **Name**: Ibrahim Najmi
- **Role**: Survey participation, basic access

---

## 🚀 Testing Scenarios

### 1. 🔑 Authentication & Role-Based Access
1. **Login Testing**:
   - Go to: `http://localhost:8000/accounts/login/`
   - Test each role's login with credentials above
   - Verify role-specific dashboard appears

2. **Permission Testing**:
   - Try accessing admin features as a student (should be restricted)
   - Test doctor accessing patient records
   - Verify Moze coordinators can manage their facilities

### 2. 🏥 Moze Management
**Login as**: Moze Coordinator or Admin

1. **Moze Dashboard**:
   - Navigate to: `http://localhost:8000/moze/`
   - View list of 8 Mumbai-based Moze centers
   - Click on any Moze to see details

2. **Features to Test**:
   - View Moze details and contact information
   - Read existing comments from community members
   - Add new comments (if permissions allow)
   - Check facility schedules and settings
   - View assigned doctors and team members

### 3. 👨‍⚕️ Doctor Directory & Medical Services
**Login as**: Doctor, Moze Coordinator, or Admin

1. **Doctor Dashboard**:
   - Navigate to: `http://localhost:8000/doctordirectory/`
   - View 12 doctors across multiple specialties

2. **Features to Test**:
   - Browse doctor profiles (Cardiology, Pediatrics, etc.)
   - Check doctor availability schedules
   - View medical services offered
   - See consultation fees and contact details

3. **Appointment System**:
   - Book appointments with available doctors
   - View existing appointments (50-100 generated)
   - Check appointment statuses (pending, confirmed, completed)

4. **Medical Records** (Doctor login):
   - View patient medical records
   - Check prescriptions and medications
   - Review vital signs recordings
   - Access patient logs and visit history

### 4. 📋 Survey System
**Login as**: Any role

1. **Survey Dashboard**:
   - Navigate to: `http://localhost:8000/surveys/`
   - View 3 active surveys:
     - Community Health Assessment (all users)
     - Moze Facilities Feedback (aamils)
     - Student Academic Survey (students)

2. **Features to Test**:
   - Take surveys based on your role
   - View existing responses and analytics
   - Check survey completion rates
   - Review response summaries

3. **Survey Analytics** (Admin/Coordinator):
   - View response statistics
   - Export survey data
   - Monitor completion rates

### 5. 📸 Photo Gallery
**Login as**: Any role

1. **Photo Albums**:
   - Browse 4 photo albums:
     - Community Events
     - Religious Ceremonies  
     - Health Camps
     - Educational Programs

2. **Features to Test**:
   - View photo collections (5-12 photos per album)
   - Check photo details and descriptions
   - Browse by Moze location
   - View cover photos and metadata

### 6. 👤 User Profile Management
**Login as**: Any user

1. **Profile Features**:
   - Go to: `http://localhost:8000/accounts/profile/`
   - View complete user information
   - Check role-specific quick actions
   - Update profile information

2. **Role-Specific Dashboards**:
   - Each role has customized dashboard content
   - Quick access to relevant features
   - Statistics and recent activities

---

## 🔍 Advanced Testing Scenarios

### 1. 🩺 Complete Medical Workflow
**Login as Doctor**: `drammar40`

1. View your schedule and upcoming appointments
2. Access patient medical records
3. Add new medical records for completed visits
4. Prescribe medications
5. Record vital signs
6. Generate medical reports

### 2. 📊 Survey Analytics Deep Dive
**Login as Admin**: `admin`

1. Create a new survey with dynamic questions
2. Target specific user roles
3. Monitor response rates
4. Export survey data to CSV
5. Analyze response patterns

### 3. 🏥 Moze Operations
**Login as Moze Coordinator**: `ahmed20`

1. Manage your assigned Moze center
2. Update facility information
3. Coordinate doctor schedules
4. Manage patient flow
5. Respond to community feedback

### 4. 🔐 Administrative Tasks
**Login as Admin**: `admin`

1. User management and role assignments
2. System-wide analytics and reports
3. Content moderation (comments, photos)
4. Survey management and creation
5. Bulk data operations

---

## 📈 Data Statistics

The populated database contains:
- **60 Users** across all 5 roles
- **8 Moze Centers** with complete information
- **12 Doctors** with specialties and schedules
- **14 Patients** with medical histories
- **50-100 Appointments** (past and future)
- **Medical Records** for completed appointments
- **3 Surveys** with realistic responses
- **4 Photo Albums** with multiple photos each
- **Comments and Interactions** throughout the system

---

## 🚨 Common Test Cases

### Security Testing
1. **Role Isolation**: Ensure users can only access appropriate features
2. **Data Privacy**: Verify patient data is protected
3. **Authentication**: Test login/logout functionality

### Performance Testing
1. **Page Load Times**: Check all major pages load quickly
2. **Large Data Sets**: Test with multiple appointments/records
3. **Search Functionality**: Test search across users, doctors, surveys

### User Experience Testing
1. **Navigation**: Ensure intuitive menu and navigation
2. **Mobile Responsiveness**: Test on different screen sizes
3. **Form Validation**: Test required fields and data validation

---

## 🐛 Reporting Issues

If you encounter any issues during testing:

1. **Note the user role** you were logged in as
2. **Document the steps** to reproduce the issue
3. **Include any error messages** displayed
4. **Specify the URL** where the issue occurred

---

## 🎯 Testing Checklist

- [ ] Authentication works for all roles
- [ ] Role-based permissions are enforced
- [ ] Moze management features function properly
- [ ] Doctor directory and appointments work
- [ ] Medical records can be created and viewed
- [ ] Surveys can be taken and analyzed
- [ ] Photo galleries are accessible
- [ ] User profiles can be updated
- [ ] Navigation and UI are intuitive
- [ ] Mobile responsiveness works
- [ ] Search functionality operates correctly
- [ ] Reports and analytics generate properly

---

**🎉 Happy Testing! The UmoorSehhat application is ready for comprehensive evaluation with realistic, diverse test data.**