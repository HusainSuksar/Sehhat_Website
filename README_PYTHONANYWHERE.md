# 🚀 **UMOOR SEHHAT - PYTHONANYWHERE DEPLOYMENT**

Complete guide for deploying Umoor Sehhat healthcare management system on PythonAnywhere.

## 📋 **QUICK START**

### **Option 1: Automated Setup (Recommended)**
```bash
# 1. Clone repository
cd ~
git clone https://github.com/HusainSuksar/Sehhat_Website.git umoor_sehhat
cd umoor_sehhat

# 2. Run quick setup script
chmod +x quick_setup.sh
./quick_setup.sh
```

### **Option 2: Manual Setup**
Follow the detailed steps in `PYTHONANYWHERE_SETUP.md`

---

## 📁 **FILE STRUCTURE**

```
umoor_sehhat/
├── 🚀 PYTHONANYWHERE FILES
│   ├── requirements_pythonanywhere.txt   # PythonAnywhere dependencies
│   ├── .env.pythonanywhere.template      # Environment variables template
│   ├── pythonanywhere_wsgi.py            # WSGI configuration
│   ├── quick_setup.sh                    # Automated setup script
│   ├── deploy_pythonanywhere.sh          # Full deployment script
│   ├── health_check.py                   # System health monitoring
│   ├── manage_database.py                # Database management utility
│   └── create_test_users.py              # Test user creation
│
├── ⚙️  DJANGO SETTINGS
│   ├── umoor_sehhat/settings_pythonanywhere.py      # Production settings
│   └── umoor_sehhat/settings_pythonanywhere_local.py # Local testing
│
├── 📚 DOCUMENTATION
│   ├── README_PYTHONANYWHERE.md          # This file
│   ├── PYTHONANYWHERE_SETUP.md           # Detailed setup guide
│   └── testing_guide.md                  # Testing scenarios
│
└── 🏥 APPLICATION CODE
    ├── accounts/      # User management
    ├── evaluation/    # Moze evaluation system
    ├── moze/         # Moze management
    ├── students/     # Student portal
    ├── doctors/      # Doctor directory
    └── ...           # Other modules
```

---

## 🔧 **CONFIGURATION FILES**

### **1. Environment Variables (.env)**
```bash
# Database (MySQL on PythonAnywhere)
DB_NAME=yourusername$umoor_sehhat
DB_USER=yourusername
DB_PASSWORD=your-mysql-password
DB_HOST=yourusername.mysql.pythonanywhere-services.com

# Security
SECRET_KEY=your-generated-secret-key
DEBUG=False
ALLOWED_HOSTS=yourusername.pythonanywhere.com

# File paths
STATIC_ROOT=/home/yourusername/umoor_sehhat/staticfiles
MEDIA_ROOT=/home/yourusername/umoor_sehhat/media
```

### **2. WSGI Configuration**
```python
# pythonanywhere_wsgi.py
import os
import sys

username = 'yourusername'  # CHANGE THIS!
path = f'/home/{username}/umoor_sehhat'

if path not in sys.path:
    sys.path.insert(0, path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings_pythonanywhere')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

---

## 👥 **TEST USERS**

All test users use password: **`test123456`**

| Role | Username | Name | Purpose |
|------|----------|------|---------|
| **Admin** | `admin_user1` | Ahmed Khan | Full system access |
| **Admin** | `admin_user2` | Fatima Ali | Full system access |
| **Aamil** | `aamil_001` | Abdullah Rahman | Moze evaluation |
| **Aamil** | `aamil_002` | Khadija Siddique | Moze evaluation |
| **Student** | `student_001` | Mohammad Hassan | Student portal |
| **Student** | `student_002` | Aisha Ahmed | Student portal |
| **Student** | `student_003` | Omar Sheikh | Student portal |
| **Doctor** | `doctor_001` | Dr. Yasmin Rashid | Medical services |
| **Doctor** | `doctor_002` | Dr. Imran Malik | Medical services |
| **Coordinator** | `coordinator_001` | Hassan Qureshi | Academic affairs |
| **Coordinator** | `coordinator_002` | Zainab Tariq | Student affairs |

---

## 🧪 **TESTING SCENARIOS**

### **Admin Testing**
```bash
# Login as: admin_user1
# Test: Full system access, user management, evaluation results
```

### **Aamil Testing**
```bash
# Login as: aamil_001
# Test: Moze evaluation, auto-selection, result confidentiality
```

### **Student Testing**
```bash
# Login as: student_001
# Test: Dashboard, grades, limited access
```

### **Cross-Role Testing**
- Verify role-based access control
- Test navigation restrictions
- Confirm data isolation

---

## 🛠️ **MAINTENANCE COMMANDS**

### **Health Check**
```bash
# Basic health check
python3.10 health_check.py

# Include web application check
python3.10 health_check.py --web --username yourusername
```

### **Database Management**
```bash
# Interactive database utility
python3.10 manage_database.py

# Reset test users
python3.10 create_test_users.py

# Run migrations
python3.10 manage.py migrate --settings=umoor_sehhat.settings_pythonanywhere
```

### **Static Files**
```bash
# Collect static files
python3.10 manage.py collectstatic --noinput --settings=umoor_sehhat.settings_pythonanywhere
```

---

## 🐛 **TROUBLESHOOTING**

### **Common Issues**

#### **1. Database Connection Error**
```bash
# Check MySQL password in .env file
# Verify database name: yourusername$umoor_sehhat
# Confirm database exists in PythonAnywhere dashboard
```

#### **2. Static Files Not Loading**
```bash
# Recollect static files
python3.10 manage.py collectstatic --noinput --settings=umoor_sehhat.settings_pythonanywhere

# Check static files mapping in Web tab:
# URL: /static/
# Directory: /home/yourusername/umoor_sehhat/staticfiles
```

#### **3. WSGI Configuration Error**
```bash
# Ensure username is updated in pythonanywhere_wsgi.py
# Check error logs in PythonAnywhere dashboard
# Verify virtualenv path: /home/yourusername/.local
```

#### **4. Import Errors**
```bash
# Reinstall dependencies
pip3.10 install --user -r requirements_pythonanywhere.txt

# Check Python path in WSGI file
# Verify Django settings module
```

### **Error Logs**
- **Location**: PythonAnywhere Dashboard → Web → Error log
- **Custom logs**: `/home/yourusername/umoor_sehhat/error.log`

---

## 📊 **PERFORMANCE MONITORING**

### **Health Checks**
- Database connectivity
- Cache functionality
- Static files
- User authentication
- Evaluation system

### **Key Metrics**
- Response time < 3 seconds
- Database queries optimized
- Static files cached
- Memory usage monitored

---

## 🔒 **SECURITY CONSIDERATIONS**

### **Production Settings**
- `DEBUG = False`
- Strong `SECRET_KEY`
- Proper `ALLOWED_HOSTS`
- HTTPS enforced (PythonAnywhere handles this)

### **Database Security**
- MySQL with authentication
- Connection encryption
- Regular backups (PythonAnywhere provides this)

### **User Data Protection**
- Role-based access control
- Evaluation results confidentiality
- Secure password handling

---

## 🚀 **DEPLOYMENT CHECKLIST**

### **Pre-Deployment**
- [ ] PythonAnywhere account created
- [ ] MySQL database created
- [ ] Repository cloned
- [ ] Dependencies installed

### **Configuration**
- [ ] .env file created with correct values
- [ ] Username updated in all files
- [ ] Database password configured
- [ ] Secret key generated

### **Django Setup**
- [ ] Migrations run successfully
- [ ] Static files collected
- [ ] Test users created
- [ ] Health check passed

### **Web App Configuration**
- [ ] Web app created (Manual, Python 3.10)
- [ ] Source code path set
- [ ] Working directory set
- [ ] Virtualenv configured
- [ ] WSGI file updated
- [ ] Static files mapping added
- [ ] Media files mapping added

### **Testing**
- [ ] Application loads successfully
- [ ] All user roles can login
- [ ] Dashboards display correctly
- [ ] Evaluation system works
- [ ] Role-based access enforced

---

## 📞 **SUPPORT**

### **Resources**
- **Setup Guide**: `PYTHONANYWHERE_SETUP.md`
- **Testing Guide**: `testing_guide.md`
- **Health Check**: `python3.10 health_check.py`
- **Database Management**: `python3.10 manage_database.py`

### **Quick Commands**
```bash
# Full deployment
./quick_setup.sh

# Health check with web test
python3.10 health_check.py --web --username yourusername

# Reset everything
python3.10 manage_database.py  # Option 4: Reset test users
```

---

## 🎯 **SUCCESS CRITERIA**

Your deployment is successful when:
1. ✅ App loads at `https://yourusername.pythonanywhere.com`
2. ✅ All test users can login with `test123456`
3. ✅ Admin can create evaluation forms
4. ✅ Aamils can submit evaluations
5. ✅ Role-based access control works
6. ✅ Dashboards display correctly for each role
7. ✅ Mobile responsiveness confirmed
8. ✅ Performance is acceptable (< 3s load time)

---

**🌟 Your Umoor Sehhat application is now ready for production-level testing on PythonAnywhere!**