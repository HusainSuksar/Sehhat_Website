# 🚀 **OFFLINE TEST DATA SETUP - PythonAnywhere**

## ⚡ **QUICK SOLUTION FOR PROXY RESTRICTIONS**

Since PythonAnywhere free accounts block external API connections, use this **offline solution** that generates the same comprehensive test data locally.

---

## 📋 **WHAT YOU GET:**

✅ **500 Users** (10 Admins, 100 Aamils, 100 Coordinators, 100 Doctors, 100 Students, 90 Others)
✅ **100 Moze Centers** with proper relationships  
✅ **100 Students** with academic data
✅ **100 Doctors** with specializations
✅ **100 Patients** with medical profiles
✅ **100 Medical Records** & **100 Appointments**
✅ **3 Major Hospitals** (Saifee Mumbai, Burhani Mumbai, Karachi Saifee)
✅ **10 Survey Forms** & **10 Evaluation Forms**
✅ **100 Araz Petitions** & **10 Photo Albums**

---

## 🔧 **SETUP STEPS (2 MINUTES):**

### **Step 1: Create the Script on PythonAnywhere**
```bash
cd ~/umoor_sehhat
nano generate_test_data_offline.py
```

**Copy and paste the entire content from `generate_test_data_offline.py`**

Save: `Ctrl + X`, `Y`, `Enter`

### **Step 2: Run the Script**
```bash
cd ~/umoor_sehhat
python3.10 generate_test_data_offline.py
```

### **Step 3: Expected Output**
```
🏥 UMOOR SEHHAT OFFLINE TEST DATA GENERATOR
==================================================
Generating comprehensive test data for all 9 Django apps
==================================================
ℹ️  Generating 500 users...
✅ Created 500 users
ℹ️  Generating 100 Moze centers...
✅ Created 100 Moze centers
ℹ️  Generating courses...
✅ Created 10 courses
ℹ️  Generating 100 students...
✅ Created 100 students
ℹ️  Generating 100 doctors...
✅ Created 100 doctors
ℹ️  Generating hospitals...
✅ Created 3 hospitals
ℹ️  Generating 100 patients...
✅ Created 100 patients
ℹ️  Generating 100 medical records...
✅ Created 100 medical records
ℹ️  Generating 100 appointments...
✅ Created 100 appointments
ℹ️  Generating 10 surveys...
✅ Created 10 surveys
ℹ️  Generating 10 evaluation forms...
✅ Created 10 evaluation forms
ℹ️  Generating 100 petitions...
✅ Created 100 petitions
ℹ️  Generating 10 photo albums...
✅ Created 10 photo albums

==================================================
📊 GENERATION SUMMARY
==================================================
Users: 500
Moze Centers: 100
Students: 100
Courses: 10
Doctors: 100
Hospitals: 3
Patients: 100
Medical Records: 100
Appointments: 100
Surveys: 10
Evaluation Forms: 10
Petitions: 100
Photo Albums: 10

🎉 Offline test data generation completed successfully!
📈 Your dashboard should now show comprehensive statistics!
🔄 Reload your PythonAnywhere web app to see the changes.

👥 TEST USER CREDENTIALS:
Password for all users: test123456
- Admin: badri_mahal_admin_001 to badri_mahal_admin_010
- Aamil: aamil_001 to aamil_100
- Student: student_001 to student_100
- Doctor: doctor_001 to doctor_100
- Coordinator: moze_coordinator_001 to moze_coordinator_100
```

### **Step 4: Reload Web App**
1. Go to **PythonAnywhere Web tab**
2. Click **"Reload"** button  
3. Wait for reload to complete

### **Step 5: Test Your Dashboard**
1. Visit: `https://sehhat.pythonanywhere.com`
2. Login with any test user (password: `test123456`)
3. **Dashboard statistics should now show real numbers!**

---

## 🧪 **TEST USERS:**

**All users have password: `test123456`**

### **Admins (Full Access):**
- `badri_mahal_admin_001` to `badri_mahal_admin_010`

### **Aamils (Moze Management):**
- `aamil_001` to `aamil_100`

### **Students (Academic Access):**
- `student_001` to `student_100`

### **Doctors (Medical Access):**
- `doctor_001` to `doctor_100`

### **Coordinators (Moze Coordination):**
- `moze_coordinator_001` to `moze_coordinator_100`

---

## ✅ **VERIFICATION:**

After running the script, your dashboard should show:

- **Total Users**: 500+ (instead of "--")
- **Students**: 100 (instead of "--")
- **Doctors**: 100 (instead of "--")
- **Hospitals**: 3 (instead of "--")
- **Moze Centers**: 100 (instead of "--")
- **Surveys**: 10 (instead of "--")
- **Petitions**: 100 (instead of "--")
- **Photo Albums**: 10 (instead of "--")

---

## 🎯 **FEATURES COVERED:**

✅ **All 9 Django Apps**: accounts, students, moze, mahalshifa, doctordirectory, surveys, araz, photos, evaluation
✅ **Realistic Relationships**: Moze-Aamil, Patient-Doctor, Student-Course  
✅ **Production Data Volume**: 500+ users across roles
✅ **Role-Based Testing**: Admin, Aamil, Student, Doctor access
✅ **Complete Medical Ecosystem**: Patients, Doctors, Appointments, Records
✅ **Academic System**: Students, Courses, Enrollments
✅ **Community Features**: Surveys, Petitions, Photo Albums
✅ **Evaluation System**: Forms, Submissions, Grading

---

## 🚀 **PERFECT FOR:**

🔥 **Stakeholder Demonstrations**  
🧪 **Production-Level Testing**
📊 **Performance Load Testing**
🎯 **User Acceptance Testing**
⚡ **Comprehensive Feature Testing**

**Your Umoor Sehhat application is now ready with comprehensive test data across all modules!**

---

## 🛠️ **TROUBLESHOOTING:**

**Issue: Permission errors**
```bash
chmod +x generate_test_data_offline.py
```

**Issue: Django settings error**
```bash
# Make sure you're in the right directory:
cd ~/umoor_sehhat
ls -la  # Should show manage.py
```

**Issue: Database connection**
```bash
python3.10 manage.py check --settings=umoor_sehhat.settings_pythonanywhere
```

**Success!** No external APIs needed - works 100% offline on PythonAnywhere!