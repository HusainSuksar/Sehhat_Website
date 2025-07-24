# 🏥 Mahalshifa App - Comprehensive Testing Guide

## 📋 Table of Contents
1. [Quick Start](#quick-start)
2. [Manual Testing Checklist](#manual-testing-checklist)
3. [Role-Based Testing](#role-based-testing)
4. [Sample Data Creation](#sample-data-creation)
5. [Known Issues & Fixes](#known-issues--fixes)
6. [Important URLs](#important-urls)

---

## 🚀 Quick Start

### Prerequisites
```bash
# 1. Ensure Django server is running
python3 manage.py runserver 0.0.0.0:8000

# 2. Run automated tests first
python3 test_mahalshifa_app.py
```

### Test User Credentials
- **👤 Admin**: `admin` / `admin123`
- **👤 Aamil**: `aamil_medical` / `test123`
- **👤 Doctor**: `dr_ahmed` / `test123`
- **👤 Patient**: `patient_ali` / `test123`
- **👤 Moze Coordinator**: `moze_coord` / `test123`

---

## ✅ Manual Testing Checklist

### 🏠 Dashboard Testing
**URL**: `http://localhost:8000/mahalshifa/`

#### For Admin Users:
- [ ] Can view total patients count
- [ ] Can view today's appointments
- [ ] Can view pending/completed appointments
- [ ] Can view hospital statistics
- [ ] Can view recent appointments list
- [ ] Can view department statistics
- [ ] Can view emergency cases count
- [ ] Can view monthly appointment trends
- [ ] Can access all dashboard widgets

#### For Doctors:
- [ ] Can view their own patient statistics
- [ ] Can view their appointments
- [ ] Can view hospital they're affiliated with
- [ ] Dashboard shows doctor-specific data only

#### For Patients:
- [ ] Can view their own appointment history
- [ ] Can view their medical records summary
- [ ] Can access their hospital information
- [ ] Dashboard shows patient-specific data only

---

### 🏥 Hospital Management Testing
**URL**: `http://localhost:8000/mahalshifa/hospitals/`

#### Hospital Listing:
- [ ] Can view list of hospitals
- [ ] Can filter by hospital type
- [ ] Can search by hospital name/location
- [ ] Can view hospital details (beds, services, etc.)
- [ ] Pagination works correctly

#### Hospital Details:
**URL**: `http://localhost:8000/mahalshifa/hospitals/1/`
- [ ] Can view hospital information
- [ ] Can view departments list
- [ ] Can view doctors list
- [ ] Can view rooms and capacity
- [ ] Can view recent appointments
- [ ] Can view hospital statistics

---

### 🏥 Patient Management Testing
**URL**: `http://localhost:8000/mahalshifa/patients/`

#### Patient Listing:
- [ ] Can view patient list (role-based)
- [ ] Can filter by hospital
- [ ] Can filter by active/inactive status
- [ ] Can search by name/ITS ID
- [ ] Pagination works correctly

#### Patient Details:
**URL**: `http://localhost:8000/mahalshifa/patients/1/`
- [ ] Can view patient demographics
- [ ] Can view medical history
- [ ] Can view appointment history
- [ ] Can view prescriptions
- [ ] Can view lab tests
- [ ] Can view vital signs
- [ ] Can view emergency contacts
- [ ] Can view insurance information

---

### 📅 Appointment Management Testing
**URL**: `http://localhost:8000/mahalshifa/appointments/`

#### Appointment Listing:
- [ ] Can view appointments (role-based)
- [ ] Can filter by status
- [ ] Can filter by date (today/week)
- [ ] Can filter by doctor
- [ ] Can view appointment details

#### Appointment Creation:
**URL**: `http://localhost:8000/mahalshifa/appointments/create/`
- [ ] Can select patient (role-based)
- [ ] Can select doctor
- [ ] Can select hospital
- [ ] Can set appointment date/time
- [ ] Can set appointment type
- [ ] Can add reason and notes
- [ ] Form validation works
- [ ] Appointment is created successfully

#### Appointment Details:
**URL**: `http://localhost:8000/mahalshifa/appointments/1/`
- [ ] Can view appointment information
- [ ] Can view related medical records
- [ ] Can view prescriptions
- [ ] Can view lab tests
- [ ] Can view vital signs
- [ ] Can edit (if authorized)

---

### 📊 Medical Analytics Testing
**URL**: `http://localhost:8000/mahalshifa/analytics/`

#### Analytics Dashboard:
- [ ] Can view appointment statistics
- [ ] Can view patient statistics
- [ ] Can view department performance
- [ ] Can view monthly trends
- [ ] Can view top doctors by appointments
- [ ] Can view hospital comparison
- [ ] Charts and graphs load correctly

---

### 📦 Inventory Management Testing
**URL**: `http://localhost:8000/mahalshifa/inventory/`

#### Inventory Overview:
- [ ] Can view inventory items
- [ ] Can view low stock items
- [ ] Can view recent updates
- [ ] Can view inventory by hospital
- [ ] Can view total items count

---

### 📊 Data Export Testing
**URL**: `http://localhost:8000/mahalshifa/export/`

#### Export Functionality:
- [ ] Can export appointments as CSV
- [ ] Can export patients as CSV
- [ ] Downloads work correctly
- [ ] CSV format is correct

---

## 👥 Role-Based Testing Scenarios

### 🔑 Admin User Testing
Login as: `admin` / `admin123`

**Should Have Access To:**
- [ ] All hospitals, patients, appointments
- [ ] All analytics and reports
- [ ] All management features
- [ ] Data export functionality
- [ ] Inventory management

**Test Scenarios:**
1. View system-wide statistics
2. Access all patient records
3. View all hospital data
4. Export medical data
5. Manage inventory

### 🏥 Aamil User Testing
Login as: `aamil_medical` / `test123`

**Should Have Access To:**
- [ ] Hospitals they administer
- [ ] Patients in their hospitals
- [ ] Appointments in their hospitals
- [ ] Analytics for their hospitals
- [ ] Inventory for their hospitals

**Test Scenarios:**
1. View hospital-specific data
2. Manage patients in their hospitals
3. View hospital analytics
4. Cannot access other hospitals' data

### 👨‍⚕️ Doctor User Testing
Login as: `dr_ahmed` / `test123`

**Should Have Access To:**
- [ ] Their own appointments
- [ ] Their patients
- [ ] Their hospital information
- [ ] Cannot access analytics
- [ ] Cannot access inventory

**Test Scenarios:**
1. View own appointment schedule
2. View own patients
3. Create appointments for patients
4. Cannot view other doctors' data
5. Cannot access administrative features

### 🏥 Patient User Testing
Login as: `patient_ali` / `test123`

**Should Have Access To:**
- [ ] Own appointments
- [ ] Own medical records
- [ ] Own hospital information
- [ ] Appointment booking
- [ ] Cannot access other patients' data

**Test Scenarios:**
1. View own appointment history
2. View own medical records
3. Book new appointments
4. Cannot access other patients' information
5. Cannot access administrative features

### 👥 Moze Coordinator Testing
Login as: `moze_coord` / `test123`

**Should Have Access To:**
- [ ] Hospitals they coordinate
- [ ] Patients they coordinate
- [ ] Coordination-specific features

**Test Scenarios:**
1. View coordinated hospitals
2. Manage patient registrations
3. Coordinate appointments

---

## 🎯 Sample Data Creation

### Using Automated Script:
```bash
python3 test_mahalshifa_app.py
```

### Manual Sample Data:
The automated script creates:
- **1 Hospital**: Mahal Shifa General Hospital
- **1 Department**: Internal Medicine
- **1 Doctor**: Dr. Ahmed Hassan (Internal Medicine)
- **1 Patient**: Ali Mahmood (Diabetes patient)
- **1 Appointment**: Diabetes follow-up
- **1 Medical Record**: Diabetes consultation
- **1 Prescription**: Metformin
- **1 Lab Test**: HbA1c
- **1 Vital Signs**: Patient vitals
- **1 Medication**: Metformin details

---

## 🔧 Known Issues & Fixes

### Issue 1: Model Field Inconsistencies
**Problem**: Some views may reference fields that don't exist in models
**Fix**: Check model definitions in `mahalshifa/models.py` for correct field names

### Issue 2: Permission Errors
**Problem**: Users can't access certain features
**Fix**: Verify role-based permissions in views

### Issue 3: Dashboard Statistics
**Problem**: Dashboard may show incomplete statistics
**Fix**: Ensure sample data is created and models are properly linked

### Issue 4: Appointment Conflicts
**Problem**: Double-booking or time conflicts
**Fix**: Implement proper validation in appointment creation

---

## 🔗 Important URLs

### Main Application URLs:
- **🏠 Dashboard**: `http://localhost:8000/mahalshifa/`
- **🏥 Hospitals**: `http://localhost:8000/mahalshifa/hospitals/`
- **🏥 Patients**: `http://localhost:8000/mahalshifa/patients/`
- **📅 Appointments**: `http://localhost:8000/mahalshifa/appointments/`
- **📊 Analytics**: `http://localhost:8000/mahalshifa/analytics/`
- **📦 Inventory**: `http://localhost:8000/mahalshifa/inventory/`
- **📊 Export**: `http://localhost:8000/mahalshifa/export/`

### Specific Feature URLs:
- **📅 Create Appointment**: `http://localhost:8000/mahalshifa/appointments/create/`
- **🏥 Hospital Details**: `http://localhost:8000/mahalshifa/hospitals/1/`
- **🏥 Patient Details**: `http://localhost:8000/mahalshifa/patients/1/`
- **📅 Appointment Details**: `http://localhost:8000/mahalshifa/appointments/1/`

### API/Export URLs:
- **📊 Export Appointments**: `http://localhost:8000/mahalshifa/export/?type=appointments`
- **📊 Export Patients**: `http://localhost:8000/mahalshifa/export/?type=patients`

---

## 🎯 Testing Completion Checklist

### ✅ Core Functionality:
- [ ] Dashboard loads and shows statistics
- [ ] Hospital management works
- [ ] Patient management works
- [ ] Appointment management works
- [ ] Analytics display correctly
- [ ] Inventory management accessible
- [ ] Data export functions

### ✅ Role-Based Access:
- [ ] Admin can access everything
- [ ] Aamil can access hospital-specific data
- [ ] Doctors can access their data
- [ ] Patients can access own data
- [ ] Moze coordinators have appropriate access

### ✅ Data Integrity:
- [ ] Sample data is created correctly
- [ ] Relationships between models work
- [ ] Statistics are calculated correctly
- [ ] Search and filtering work

### ✅ User Experience:
- [ ] Navigation is intuitive
- [ ] Forms work correctly
- [ ] Error handling is appropriate
- [ ] Performance is acceptable

---

## 📝 Notes

- The Mahalshifa app is a comprehensive medical hospital management system
- It integrates with the existing user authentication system
- It uses the Moze model for patient registration coordination
- It connects with the Doctor Directory app for doctor profiles
- All medical data follows proper healthcare data models
- Role-based access ensures data privacy and security

---

## 🆘 Troubleshooting

### Common Issues:
1. **Server not running**: `python3 manage.py runserver 0.0.0.0:8000`
2. **Missing sample data**: Run `python3 test_mahalshifa_app.py`
3. **Permission denied**: Check user roles and login credentials
4. **404 errors**: Verify URL patterns in `mahalshifa/urls.py`
5. **Database errors**: Run migrations: `python3 manage.py migrate`

### Debug Steps:
1. Check Django server logs for errors
2. Verify database contains sample data
3. Confirm user authentication is working
4. Test with different user roles
5. Check browser console for JavaScript errors

**Happy Testing! 🏥✨**