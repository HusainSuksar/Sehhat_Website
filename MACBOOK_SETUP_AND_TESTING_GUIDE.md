# 🚀 **SEHHAT WEBSITE - COMPLETE MacBook SETUP & END-TO-END TESTING GUIDE**

## 📋 **TABLE OF CONTENTS**
1. [Initial Setup](#initial-setup)
2. [Database & Migration Setup](#database--migration-setup)
3. [Test Data Population](#test-data-population)
4. [Server Startup](#server-startup)
5. [End-to-End Testing](#end-to-end-testing)
6. [User Role Testing](#user-role-testing)
7. [App-by-App Testing](#app-by-app-testing)
8. [Admin Panel Testing](#admin-panel-testing)
9. [Troubleshooting](#troubleshooting)

---

## 🛠️ **1. INITIAL SETUP**

### **Step 1: Clone & Navigate**
```bash
cd ~/Desktop/Office/Web_App/
git pull origin main  # If already cloned
# OR
git clone https://github.com/HusainSuksar/Sehhat_Website.git
cd Sehhat_Website
```

### **Step 2: Create Virtual Environment**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify activation (should show (venv) in prompt)
which python
```

### **Step 3: Install Dependencies**
```bash
# Install required packages
pip install django
pip install pillow
pip install requests

# OR if requirements.txt exists:
pip install -r requirements.txt

# Verify Django installation
python -m django --version
```

---

## 🗄️ **2. DATABASE & MIGRATION SETUP**

### **Step 4: Apply Migrations**
```bash
# Apply all migrations
python manage.py migrate

# If you encounter migration errors, try:
python manage.py migrate --run-syncdb

# Verify migration status
python manage.py showmigrations
```

### **Step 5: Create Superuser**
```bash
# Create admin account
python manage.py createsuperuser

# Follow prompts:
# Username: admin
# Email: admin@sehhat.com  
# Password: (choose secure password)
```

---

## 📊 **3. TEST DATA POPULATION**

### **Step 6: Populate Comprehensive Test Data**
```bash
# Run the comprehensive test data script
python final_test_data.py

# Expected output:
# ✅ Created 84 test users across all roles
# ✅ Created 17 Moze communities  
# ✅ Created 8 surveys with responses
# ✅ Created 16 doctor profiles
# ✅ Created 7 photo albums
```

### **Step 7: Verify Data Population**
```bash
# Quick verification script
python quick_test_all.py

# This will show:
# - Database statistics
# - URL accessibility tests
# - Basic functionality verification
```

---

## 🌐 **4. SERVER STARTUP**

### **Step 8: Start Django Development Server**
```bash
# Start server
python manage.py runserver

# Server will start at: http://127.0.0.1:8000/
# Keep this terminal open
```

### **Step 9: Verify Server is Running**
Open a new terminal and test:
```bash
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/
# Should return: 302 (redirect to login)
```

---

## 🧪 **5. END-TO-END TESTING**

### **Step 10: Browser Testing Setup**
1. **Open your browser** (Chrome, Safari, Firefox)
2. **Navigate to**: `http://127.0.0.1:8000/`
3. **Expected**: Redirect to login page

### **Step 11: Test Login System**
**Login Credentials for Testing:**
```
Role: Aamil
Username: aamil_ali
Password: password123

Role: Doctor  
Username: dr_omar
Password: password123

Role: Student
Username: student_ahmed  
Password: password123

Role: Coordinator
Username: coord_hassan
Password: password123

Role: Regular User
Username: user_maryam
Password: password123
```

---

## 👥 **6. USER ROLE TESTING**

### **Test 1: Aamil Role (aamil_ali)**
```
✅ Login: http://127.0.0.1:8000/accounts/login/
✅ Dashboard access and navigation
✅ Moze management capabilities
✅ User oversight functions
✅ Administrative permissions
```

### **Test 2: Doctor Role (dr_omar)**
```
✅ Medical consultation access
✅ Patient management
✅ Doctor directory profile
✅ Medical records access
✅ Araz petition responses
```

### **Test 3: Student Role (student_ahmed)**
```
✅ Student portal access
✅ Academic features
✅ Survey participation
✅ Community engagement
✅ Resource access
```

### **Test 4: Coordinator Role (coord_hassan)**
```
✅ Community coordination
✅ Moze oversight
✅ Event management
✅ Survey creation
✅ Photo album management
```

### **Test 5: Regular User (user_maryam)**
```
✅ Basic portal access
✅ Survey participation
✅ Photo gallery viewing
✅ Community information
✅ Basic profile management
```

---

## 📱 **7. APP-BY-APP TESTING**

### **App 1: HOME & ACCOUNTS**
```
URL: http://127.0.0.1:8000/
URL: http://127.0.0.1:8000/accounts/

✅ Test Cases:
- User registration
- Login/logout functionality  
- Password reset
- Profile management
- Role-based navigation
- Session management
```

### **App 2: ARAZ (Petition System)**
```
URL: http://127.0.0.1:8000/araz/

✅ Test Cases:
- Submit new petition/request
- View petition status
- Doctor assignment
- Status updates
- Priority handling
- Medical consultation requests
```

### **App 3: MOZE (Community Management)**
```
URL: http://127.0.0.1:8000/moze/

✅ Test Cases:
- View Moze communities (17 available)
- Community details and information
- Team member management
- Community settings
- Contact information
- Capacity and location data
```

### **App 4: PHOTOS (Gallery System)**
```
URL: http://127.0.0.1:8000/photos/

✅ Test Cases:
- View photo albums (7 available)
- Browse community event photos
- Photo categories and tags
- Album management (if authorized)
- Photo metadata
- Public/private access
```

### **App 5: SURVEYS**
```
URL: http://127.0.0.1:8000/surveys/

✅ Test Cases:
- View available surveys (8 available)
- Complete survey responses
- View survey results (if permitted)
- Role-based survey access
- Analytics and statistics
- Survey creation (if authorized)
```

### **App 6: STUDENTS (Academic Management)**
```
URL: http://127.0.0.1:8000/students/

✅ Test Cases:
- Student profile management
- Academic records
- Mentorship requests
- Achievement tracking
- Aid requests
- Meeting scheduling
```

### **App 7: EVALUATION (Assessment System)**
```
URL: http://127.0.0.1:8000/evaluation/

✅ Test Cases:
- Evaluation forms
- Assessment criteria
- Performance tracking
- Evaluation submissions
- Report generation
- Quality metrics
```

### **App 8: MAHALSHIFA (Hospital Management)**
```
URL: http://127.0.0.1:8000/mahalshifa/

✅ Test Cases:
- Hospital information
- Medical services
- Appointment booking
- Patient management
- Medical records
- Prescription handling
```

### **App 9: DOCTOR DIRECTORY**
```
URL: http://127.0.0.1:8000/doctordirectory/

✅ Test Cases:
- Browse doctors (16 available)
- Doctor profiles and specializations
- Consultation booking
- Doctor availability
- Medical qualifications
- Contact information
```

---

## 🔧 **8. ADMIN PANEL TESTING**

### **Step 12: Admin Panel Access**
```
URL: http://127.0.0.1:8000/admin/
Login: Use superuser credentials created earlier

✅ Test Cases:
- User management (84 total users)
- Group and permissions
- All app data management:
  * Accounts (Users, Profiles)
  * Araz (Petitions, Requests) 
  * Moze (Communities, Settings)
  * Photos (Albums, Photos)
  * Surveys (Surveys, Responses)
  * Students (Profiles, Achievements)
  * Evaluation (Forms, Submissions)
  * Mahalshifa (Patients, Records)
  * Doctor Directory (Doctors, Schedules)
```

---

## 🔍 **9. COMPREHENSIVE TESTING CHECKLIST**

### **Navigation Testing**
- [ ] Home page loads correctly
- [ ] Menu navigation works
- [ ] Breadcrumbs function properly
- [ ] Footer links are functional
- [ ] Mobile responsive design

### **Authentication Testing**  
- [ ] Login with each user role
- [ ] Logout functionality
- [ ] Session timeout handling
- [ ] Permission-based access
- [ ] Password reset flow

### **CRUD Operations Testing**
- [ ] Create: Add new records in each app
- [ ] Read: View data lists and details
- [ ] Update: Edit existing records
- [ ] Delete: Remove records (where permitted)

### **Form Testing**
- [ ] Form validation works
- [ ] Required field enforcement
- [ ] Data type validation
- [ ] File upload functionality
- [ ] Form submission success

### **Search & Filter Testing**
- [ ] Search functionality
- [ ] Filter options work
- [ ] Sort by different criteria
- [ ] Pagination functions
- [ ] Results accuracy

### **Integration Testing**
- [ ] User role permissions
- [ ] Data relationships intact
- [ ] Cross-app functionality
- [ ] Email notifications (if enabled)
- [ ] File handling and storage

---

## ⚠️ **10. TROUBLESHOOTING**

### **Common Issues & Solutions**

#### **Migration Errors**
```bash
# If migration fails:
python manage.py migrate --fake-initial
python manage.py migrate

# Reset migrations (if needed):
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
python manage.py makemigrations
python manage.py migrate
```

#### **Server Won't Start**
```bash
# Check for port conflicts:
lsof -i :8000

# Use different port:
python manage.py runserver 8080

# Check for errors:
python manage.py check
```

#### **No Test Data**
```bash
# Repopulate test data:
python final_test_data.py

# Verify data exists:
python quick_test_all.py
```

#### **Login Issues**
```bash
# Create new superuser:
python manage.py createsuperuser

# Reset user password in Django shell:
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.get(username='aamil_ali')
>>> user.set_password('password123')
>>> user.save()
```

#### **Static Files Not Loading**
```bash
# Collect static files:
python manage.py collectstatic --noinput
```

---

## 📊 **11. TESTING COMPLETION VERIFICATION**

### **Database Verification**
Run this in Django shell (`python manage.py shell`):
```python
from django.contrib.auth import get_user_model
User = get_user_model()

print(f"Total Users: {User.objects.count()}")
print(f"Aamils: {User.objects.filter(role='aamil').count()}")
print(f"Doctors: {User.objects.filter(role='doctor').count()}")
print(f"Students: {User.objects.filter(role='student').count()}")

from moze.models import Moze
print(f"Moze Communities: {Moze.objects.count()}")

from surveys.models import Survey
print(f"Surveys: {Survey.objects.count()}")

from doctordirectory.models import Doctor  
print(f"Doctor Profiles: {Doctor.objects.count()}")
```

### **Expected Results:**
```
Total Users: 84
Aamils: 16
Doctors: 21  
Students: 23
Moze Communities: 17
Surveys: 8
Doctor Profiles: 16
```

---

## 🎯 **12. SUCCESS INDICATORS**

### **✅ All Tests Pass If:**
- All 9 apps load without errors
- User authentication works for all roles
- CRUD operations function properly
- Admin panel displays all data correctly
- No 404 or 500 errors during navigation
- Forms submit and validate correctly
- Database contains expected test data
- User permissions work as intended

### **🚀 Ready for Production If:**
- All end-to-end tests complete successfully
- No critical bugs found during testing
- Performance is acceptable
- Security measures are in place
- User experience is smooth and intuitive

---

## 📞 **SUPPORT & NEXT STEPS**

### **If Everything Works:**
🎉 **Congratulations!** Your Sehhat Website is fully functional with:
- 9 Django applications
- 84 test users across all roles
- Comprehensive healthcare management system
- Complete authentication and authorization
- Full CRUD functionality across all modules

### **If Issues Persist:**
1. Check the troubleshooting section above
2. Review server logs for specific errors
3. Verify all dependencies are installed correctly
4. Ensure virtual environment is activated
5. Check database file permissions

---

**🏆 HAPPY TESTING! Your Django healthcare platform is ready for comprehensive evaluation! 🚀**