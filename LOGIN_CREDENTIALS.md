# 🔐 **LOGIN CREDENTIALS**

## 🚀 **Django Development Server**
The server is running at: **http://localhost:8000**

---

## 👑 **ADMIN/SUPERUSER**
- **Username:** `admin`
- **Password:** `admin123`
- **Email:** `admin@example.com`
- **Role:** Superuser (Full access)
- **Access:** Django Admin Panel + All Features

**Admin Panel:** http://localhost:8000/admin/

---

## 👥 **TEST USERS BY ROLE**

### 🕌 **Aamil (Mosque Administrator)**
- **Username:** `aamil1`
- **Password:** `test123`
- **Email:** `aamil@test.com`
- **Name:** Ahmed Ali
- **Role:** `aamil`
- **Access:** Moze management, evaluations

### 🎯 **Moze Coordinator**
- **Username:** `coordinator1`
- **Password:** `test123`
- **Email:** `coordinator@test.com`
- **Name:** Fatima Khan
- **Role:** `moze_coordinator`
- **Access:** Moze coordination, team management

### 👨‍⚕️ **Doctor**
- **Username:** `doctor1`
- **Password:** `test123`
- **Email:** `doctor@test.com`
- **Name:** Dr. Hassan Ahmed
- **Role:** `doctor`
- **Access:** Medical records, appointments, directory

### 🎓 **Student**
- **Username:** `student1`
- **Password:** `test123`
- **Email:** `student@test.com`
- **Name:** Sara Ali
- **Role:** `student`
- **Access:** Academic features, evaluations

### 🏥 **Badri Mahal Admin (Hospital Admin)**
- **Username:** `mahal_admin1`
- **Password:** `test123`
- **Email:** `mahal@test.com`
- **Name:** Ibrahim Hassan
- **Role:** `badri_mahal_admin`
- **Access:** Hospital management, Mahalshifa features

---

## 🌐 **ACCESS URLS**

### **Main Application:**
- **Login:** http://localhost:8000/accounts/login/
- **Dashboard:** http://localhost:8000/ (redirects based on role)

### **Role-Specific Dashboards:**
- **Admin:** http://localhost:8000/admin/
- **Aamil:** http://localhost:8000/moze/ 
- **Doctor:** http://localhost:8000/doctordirectory/
- **Student:** http://localhost:8000/students/
- **Mahal Admin:** http://localhost:8000/mahalshifa/

### **Hybrid API Features:**
- **Hybrid Dashboard:** http://localhost:8000/api/hybrid-dashboard/
- **Hybrid Doctors:** http://localhost:8000/api/hybrid-doctors/
- **Hybrid Hospitals:** http://localhost:8000/api/hybrid-hospitals/
- **API Config:** http://localhost:8000/api/api-config/

---

## 🎯 **QUICK LOGIN GUIDE**

### **Step 1: Access Login Page**
```
http://localhost:8000/accounts/login/
```

### **Step 2: Choose Your Test Account**
Use any of the credentials above based on the role you want to test.

### **Step 3: Explore Features**
Each role has different dashboard and features:

- **Admin** → Full system access
- **Aamil** → Moze management  
- **Coordinator** → Team coordination
- **Doctor** → Medical features
- **Student** → Academic features
- **Mahal Admin** → Hospital management

---

## 🔧 **TESTING FEATURES**

### **Test Hybrid API Integration:**
1. Login as **admin** (full access)
2. Visit: http://localhost:8000/api/hybrid-dashboard/
3. Check API status (should show online/offline)
4. Test cache refresh (admin only)

### **Test Role-Based Access:**
1. Login with different role accounts
2. Notice different dashboards and menus
3. Test feature restrictions per role

### **Test Management Commands:**
```bash
# Test API services
python manage.py test_api_services

# Check system status  
python manage.py check
```

---

## 📊 **DATABASE STATUS**
- ✅ **Migrations:** Applied successfully
- ✅ **Superuser:** Created (admin/admin123)
- ✅ **Test Users:** 5 users created across all roles
- ✅ **Tables:** All app tables created
- ✅ **Server:** Running on http://localhost:8000

---

## 🚨 **IMPORTANT NOTES**

### **For Development:**
- These are **test credentials** for development only
- **Never use these in production**
- Password is simple (`test123`) for easy testing

### **For Production:**
- Create strong passwords
- Use environment variables
- Enable proper authentication (ITS login)
- Configure secure settings

### **Troubleshooting:**
- If server not running: `python manage.py runserver`
- If login fails: Check credentials above
- If pages don't load: Ensure migrations ran successfully

---

**🎉 Your Django application is ready for testing with full hybrid API integration!**