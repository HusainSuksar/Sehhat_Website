# 🚀 **PYTHONANYWHERE DEPLOYMENT GUIDE**

## **Step 1: Sign Up & Account Setup**

1. Go to [pythonanywhere.com](https://pythonanywhere.com)
2. Sign up for **"Hacker" account** ($5/month) - recommended for custom domains
3. Or use **"Beginner" account** (free) for initial testing

## **Step 2: Upload Your Project**

Open a **Bash console** in PythonAnywhere and run:

```bash
# Clone your repository
cd ~
git clone https://github.com/HusainSuksar/Sehhat_Website.git umoor_sehhat
cd umoor_sehhat

# Create virtual environment
mkvirtualenv --python=/usr/bin/python3.10 umoor_sehhat_env

# Install dependencies
pip install -r requirements.txt
pip install mysqlclient  # For MySQL support
```

## **Step 3: Configure Settings**

1. **Update the settings file:**
   - Open `umoor_sehhat/settings_pythonanywhere.py`
   - Replace all instances of `yourusername` with your actual PythonAnywhere username
   - Generate a new SECRET_KEY:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

2. **Update the settings with your username and secret key**

## **Step 4: Database Setup**

1. Go to **"Databases"** tab in PythonAnywhere dashboard
2. Create a **MySQL database**: `yourusername$umoor_sehhat`
3. Note the password provided
4. Update the password in `settings_pythonanywhere.py`

## **Step 5: Run Migrations & Setup**

```bash
# Run migrations
python manage.py migrate --settings=umoor_sehhat.settings_pythonanywhere

# Create superuser
python manage.py createsuperuser --settings=umoor_sehhat.settings_pythonanywhere

# Create test users
python manage.py shell --settings=umoor_sehhat.settings_pythonanywhere < create_test_users.py

# Collect static files
python manage.py collectstatic --noinput --settings=umoor_sehhat.settings_pythonanywhere
```

## **Step 6: Web App Configuration**

1. Go to **"Web"** tab in PythonAnywhere dashboard
2. Click **"Add a new web app"**
3. Choose **"Manual configuration"** and **Python 3.10**
4. Set:
   - **Source code:** `/home/yourusername/umoor_sehhat`
   - **Working directory:** `/home/yourusername/umoor_sehhat`

## **Step 7: Configure WSGI**

1. In **Web** tab, click on **WSGI configuration file**
2. Replace the contents with:

```python
import os
import sys

# Add your project directory to the sys.path
path = '/home/yourusername/umoor_sehhat'  # Replace yourusername
if path not in sys.path:
    sys.path.insert(0, path)

# Set environment variable for Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings_pythonanywhere')

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## **Step 8: Configure Virtual Environment**

1. In **Web** tab, set **Virtualenv:** `/home/yourusername/.virtualenvs/umoor_sehhat_env`

## **Step 9: Static Files Configuration**

1. In **Web** tab, add **Static files mapping:**
   - **URL:** `/static/`
   - **Directory:** `/home/yourusername/umoor_sehhat/staticfiles`

## **Step 10: Reload and Test**

1. Click **"Reload"** button in Web tab
2. Visit your app at: `https://yourusername.pythonanywhere.com`

---

## **🔑 TEST LOGIN CREDENTIALS**

All test accounts use password: **`test123456`**

### **Admin Users**
- `admin_user1` (Ahmed Khan)
- `admin_user2` (Fatima Ali)

### **Students**
- `student_001` (Mohammad Hassan)
- `student_002` (Aisha Ahmed)
- `student_003` (Omar Sheikh)

### **Doctors**
- `doctor_001` (Dr. Yasmin Rashid)
- `doctor_002` (Dr. Imran Malik)

### **Aamils**
- `aamil_001` (Abdullah Rahman)
- `aamil_002` (Khadija Siddique)

### **Coordinators**
- `coordinator_001` (Hassan Qureshi)
- `coordinator_002` (Zainab Tariq)

---

## **🧪 TESTING CHECKLIST**

### **Admin Testing (admin_user1)**
- [ ] Dashboard loads with statistics
- [ ] Can create evaluation forms
- [ ] View Moze prioritization dashboard
- [ ] User management works
- [ ] All navigation links accessible

### **Aamil Testing (aamil_001)**
- [ ] Can access evaluation forms
- [ ] "Evaluate" buttons visible
- [ ] Moze field auto-selects
- [ ] Can submit evaluations
- [ ] Results hidden from aamil

### **Student Testing (student_001)**
- [ ] Student dashboard loads
- [ ] Statistics display correctly
- [ ] Limited access (no admin features)
- [ ] Navigation appropriate for role

### **Doctor Testing (doctor_001)**
- [ ] Doctor dashboard accessible
- [ ] Medical features available
- [ ] Proper role restrictions

### **Cross-Role Testing**
- [ ] Students can't access admin features
- [ ] Aamils can't see evaluation results
- [ ] Only admins see full system access

---

## **🐛 TROUBLESHOOTING**

### **If you get import errors:**
```bash
# Reinstall packages
pip install -r requirements.txt --force-reinstall
```

### **If database connection fails:**
- Check your database name matches: `yourusername$umoor_sehhat`
- Verify password in settings file
- Ensure MySQL is selected in database creation

### **If static files don't load:**
```bash
python manage.py collectstatic --noinput --settings=umoor_sehhat.settings_pythonanywhere
```

### **If you need to reset test users:**
```bash
python manage.py shell --settings=umoor_sehhat.settings_pythonanywhere < create_test_users.py
```

---

## **✅ SUCCESS CRITERIA**

Your deployment is successful when:
1. ✅ App loads at `https://yourusername.pythonanywhere.com`
2. ✅ All test users can log in
3. ✅ Admin can create evaluation forms
4. ✅ Aamils can submit evaluations
5. ✅ Role-based access control works
6. ✅ Dashboards display correctly for each role

---

**🎉 Once deployed, you'll have a fully functional production-level testing environment without needing ITS integration!**