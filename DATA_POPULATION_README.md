# 🏥 Comprehensive Data Population for Umoor Sehhat

## 📋 Overview

This repository contains scripts to populate your Umoor Sehhat system with comprehensive test data, including 120 users in MOCKITS and data for all applications.

## 🎯 What Will Be Created

### 👥 **120 Users in MOCKITS**
- **20 Aamils** (Moze Managers)
- **20 Coordinators** (1 per moze)
- **30 Doctors** (Medical professionals)
- **40 Students** (Patients)
- **10 Admins** (System administrators)

### 🏢 **Infrastructure**
- **20 Mozes** (Community centers)
- **6 Hospitals** (Medical facilities)
- **8 Medical Services** (Consultation types)

### 👨‍⚕️ **Medical Data**
- **30 Doctor Profiles** (Both Doctor Directory & Mahal Shifa)
- **40 Patient Profiles** (Both Doctor Directory & Mahal Shifa)
- **60 Appointments** (30 for each system)
- **120+ Medical Records** (3 per patient)

### 📊 **Other Applications**
- **50 Araz Petitions** (Community requests)
- **20 Surveys** (Community feedback)
- **15 Photo Albums** (Community events)
- **10 Evaluation Forms** (Program assessment)
- **40 Student Profiles** (Educational records)

## 🚀 **How to Use**

### **Step 1: Run Data Population**
```bash
# Navigate to your project directory
cd /workspace

# Run the comprehensive data population script
python3 populate_comprehensive_data.py
```

### **Step 2: Verify Data Creation**
```bash
# Test the data population
python3 test_data_population.py
```

### **Step 3: Test the System**
```bash
# Start Django development server
python3 manage.py runserver

# Open browser and test with created users
```

## 🔐 **Login Credentials**

### **User Types & Credentials**

| Role | Username Format | Password | Example |
|------|----------------|----------|---------|
| **Aamil** | `aamil01`, `aamil02`, etc. | `testpass123` | `aamil01` / `testpass123` |
| **Coordinator** | `coordinator01`, `coordinator02`, etc. | `testpass123` | `coordinator01` / `testpass123` |
| **Doctor** | `doctor01`, `doctor02`, etc. | `testpass123` | `doctor01` / `testpass123` |
| **Student** | `student01`, `student02`, etc. | `testpass123` | `student01` / `testpass123` |
| **Admin** | `admin01`, `admin02`, etc. | `testpass123` | `admin01` / `testpass123` |

### **ITS IDs**
- **Aamils**: 50000002 - 50000021
- **Coordinators**: 50000022 - 50000041
- **Doctors**: 50000042 - 50000071
- **Students**: 50000072 - 50000111
- **Admins**: 50000112 - 50000121

## 🏥 **Appointment System Testing**

### **Test Scenarios**

1. **Login as Different Users**
   - Test role-based access control
   - Verify dashboard displays correct data

2. **Appointment Management**
   - Create new appointments
   - Edit existing appointments
   - Test status updates
   - Verify double booking prevention

3. **Medical Records**
   - View patient medical history
   - Create new medical records
   - Test doctor-patient relationships

4. **Araz Petitions**
   - Submit new petitions
   - View petition status
   - Test signature collection

5. **Surveys & Evaluations**
   - Create surveys
   - Submit responses
   - View results

## 📊 **Expected Data Counts**

After running the script, you should see:

```
👥 User Statistics:
   Total Users: 120
   Aamils: 20
   Coordinators: 20
   Doctors: 30
   Students: 40
   Admins: 10

🏢 Infrastructure:
   Mozes: 20
   Hospitals: 6

👨‍⚕️ Medical Professionals:
   Doctor Directory Doctors: 30
   Mahal Shifa Doctors: 30

👥 Patients:
   Doctor Directory Patients: 40
   Mahal Shifa Patients: 40

📅 Appointments:
   Doctor Directory: 60
   Mahal Shifa: 60

📋 Medical Records: 120+
📝 Araz Petitions: 50
📊 Surveys: 20
📸 Photo Albums: 15
📋 Evaluations: 10
🎓 Student Profiles: 40
```

## 🔍 **Testing the Appointment System**

### **1. Doctor Login Test**
```bash
# Login as doctor01 / testpass123
# Navigate to appointments
# Verify can see only their appointments
# Test appointment creation
```

### **2. Patient Login Test**
```bash
# Login as student01 / testpass123
# Navigate to appointments
# Verify can see only their appointments
# Test appointment booking
```

### **3. Admin Login Test**
```bash
# Login as admin01 / testpass123
# Navigate to appointments
# Verify can see all appointments
# Test appointment management
```

### **4. Aamil Login Test**
```bash
# Login as aamil01 / testpass123
# Navigate to moze management
# Verify can see moze-specific data
# Test appointment oversight
```

## ⚠️ **Important Notes**

### **Data Relationships**
- **Number of mozes = Number of aamils** (20 each)
- **Number of patients = Number of medical records** (40 patients, 120+ records)
- **Each moze has one coordinator**
- **Each patient has multiple medical records**
- **Appointments are distributed across both systems**

### **Mock ITS Integration**
- **User credentials and profile data** come from MOCKITS API
- **All other data** (appointments, medical records, etc.) comes from your database
- **No external API calls** during normal operation
- **Easy to switch** to real ITS API later

### **Test Data Quality**
- **Realistic names** from Islamic/Arabic culture
- **Proper medical terminology** for appointments and records
- **Geographic diversity** across multiple cities and countries
- **Varied medical conditions** and symptoms

## 🧹 **Cleanup (Optional)**

If you want to remove test data:

```bash
# Remove all test users (be careful!)
python3 manage.py shell
>>> from accounts.models import User
>>> User.objects.filter(username__startswith='test').delete()
>>> User.objects.filter(username__startswith='aamil').delete()
>>> User.objects.filter(username__startswith('coordinator').delete()
>>> User.objects.filter(username__startswith('doctor').delete()
>>> User.objects.filter(username__startswith('student').delete()
>>> User.objects.filter(username__startswith('admin').delete()
```

## 🎯 **Next Steps**

After data population:

1. **Test all user roles** and permissions
2. **Verify appointment system** functionality
3. **Test medical record** creation and viewing
4. **Verify dashboard** statistics
5. **Test araz petitions** and surveys
6. **Enhance frontend** based on testing results

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Import Errors**: Ensure all models are properly imported
2. **Database Constraints**: Check for unique constraints and foreign keys
3. **Permission Issues**: Verify user has proper database access
4. **Memory Issues**: For large datasets, consider running in smaller batches

### **Error Logs**
- Check Django console output for detailed error messages
- Verify database connection and permissions
- Ensure all required models exist and are migrated

## 📞 **Support**

If you encounter issues:

1. **Check the error messages** in the console
2. **Verify database migrations** are up to date
3. **Check model relationships** and constraints
4. **Review the test script** for any missing imports

## 🎉 **Success Indicators**

Your data population is successful when:

- ✅ **120 users created** with proper roles
- ✅ **All apps populated** with realistic data
- ✅ **Appointment system working** without errors
- ✅ **Role-based access** functioning correctly
- ✅ **Dashboard statistics** displaying properly
- ✅ **No duplicate data** or constraint violations

---

**Happy Testing! 🚀**

The Umoor Sehhat system will be fully populated and ready for comprehensive testing of all features.