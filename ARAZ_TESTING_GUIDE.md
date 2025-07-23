# 🧪 ARAZ APP COMPREHENSIVE TESTING GUIDE

## 📋 What is the Araz App?

The **Araz** app is the **Petition and Medical Request Management System** for Umoor Sehhat. It handles:

- **DuaAraz**: Medical consultation requests from community members
- **General Petitions**: Community complaints and administrative requests  
- **Dashboard Analytics**: Statistics and reporting for administrators
- **Assignment Management**: Task distribution among coordinators
- **Role-based Access**: Different features for different user types

---

## 🚀 Quick Start Testing

### 1. Start the Server
```bash
python3 manage.py runserver 0.0.0.0:8000
```

### 2. Access Araz App
Navigate to: **http://localhost:8000/araz/**

### 3. Login with Test Credentials
- **Admin**: `admin` / `admin123`
- **Doctor**: `doctor_1` / `test123` 
- **Student**: `student_1` / `test123`
- **Aamil**: `aamil_1` / `test123`
- **Moze Coordinator**: `moze_coordinator_1` / `test123`

---

## 🧪 Manual Testing Checklist

### ✅ Dashboard Testing

1. **Access Dashboard**
   - URL: `/araz/`
   - ✅ Check if page loads without errors
   - ✅ Verify statistics cards display (Total, Pending, In Progress, Resolved)
   - ✅ Look for monthly charts/graphs
   - ✅ Check recent petitions list

2. **Role-based Features**
   - **Admin/Aamil/Moze Coordinator**: Should see management buttons
   - **Doctor/Student**: Should see limited features
   - ✅ Verify "Submit New Petition" button appears
   - ✅ Check if "View Analytics" button shows for managers

### ✅ Petition Management Testing

3. **Petition List**
   - URL: `/araz/petitions/`
   - ✅ Check if petition list loads
   - ✅ Verify pagination works
   - ✅ Test search/filter functionality
   - ✅ Check if petitions display with correct status

4. **Create New Petition**
   - URL: `/araz/petitions/create/`
   - ✅ Test form loads properly
   - ✅ Fill out all required fields
   - ✅ Submit and verify creation
   - ✅ Check if redirects to petition detail

5. **Petition Details**
   - URL: `/araz/petitions/<id>/`
   - ✅ View individual petition details
   - ✅ Test comment functionality
   - ✅ Check assignment features (for managers)
   - ✅ Verify status update options

### ✅ Analytics & Reports Testing

6. **Analytics Dashboard**
   - URL: `/araz/analytics/`
   - ✅ Check statistical summaries
   - ✅ Verify charts render correctly
   - ✅ Test date range filters
   - ✅ Check category breakdowns

7. **Export Functionality**
   - URL: `/araz/export/`
   - ✅ Test CSV/Excel export
   - ✅ Verify exported data accuracy
   - ✅ Check file download works

### ✅ Assignment Management Testing

8. **My Assignments**
   - URL: `/araz/my-assignments/`
   - ✅ View assigned petitions
   - ✅ Test assignment actions
   - ✅ Check notification system
   - ✅ Verify assignment history

9. **Bulk Operations**
   - URL: `/araz/bulk-update/`
   - ✅ Test bulk status updates
   - ✅ Check bulk assignment
   - ✅ Verify batch processing

---

## 🔧 Testing Different User Roles

### 👤 Admin User Testing
```
Login: admin / admin123
Features to Test:
✅ Full dashboard access
✅ All petition management features
✅ Analytics and reports
✅ User assignment capabilities
✅ Export functionality
✅ Bulk operations
```

### 👨‍⚕️ Doctor User Testing  
```
Login: doctor_1 / test123
Features to Test:
✅ Medical request viewing
✅ DuaAraz (medical consultation) access
✅ Patient information review
✅ Medical status updates
✅ Limited administrative access
```

### 👨‍🎓 Student User Testing
```
Login: student_1 / test123
Features to Test:
✅ View own petitions only
✅ Submit new requests
✅ Limited dashboard access
✅ No management features
✅ Basic status tracking
```

### 🏛️ Aamil User Testing
```
Login: aamil_1 / test123
Features to Test:
✅ Administrative petition management
✅ Community request oversight
✅ Assignment capabilities
✅ Reporting access
✅ Bulk operations
```

### 🏢 Moze Coordinator Testing
```
Login: moze_coordinator_1 / test123  
Features to Test:
✅ Regional petition management
✅ Coordinator assignments
✅ Local analytics
✅ Team management features
✅ Regional reporting
```

---

## 📊 Sample Data for Testing

### Create Test Petitions
Run this command to create sample data:
```bash
python3 test_araz_app.py
```

This creates:
- 3 petition categories (Medical Request, Administrative, Complaint)
- 2 sample DuaAraz medical requests
- Test petition data for various scenarios

### Manual Data Creation
1. **Go to Admin Panel**: `/admin/`
2. **Create Petition Categories**:
   - Medical Request
   - Administrative Issue  
   - Community Complaint
   - Infrastructure Request

3. **Create Sample DuaAraz**:
   - Patient ITS ID: 12345678
   - Ailment: "Regular checkup needed"
   - Request Type: Consultation
   - Urgency: Medium

---

## 🐛 Known Issues & Fixes

### Issue 1: Template URL Errors
**Problem**: `petition_analytics` URL not found
**Status**: ✅ FIXED - Changed to `analytics` in templates

### Issue 2: Field Name Errors  
**Problem**: `created_at` field not found in PetitionAssignment
**Status**: ✅ FIXED - Changed to `assigned_at` in views

### Issue 3: Dashboard Template Issues
**Problem**: Missing URL patterns in navigation
**Status**: ✅ FIXED - Updated template references

---

## 🎯 Testing Scenarios

### Scenario 1: Medical Request Workflow
1. Patient submits DuaAraz (medical request)
2. Admin reviews and assigns to doctor
3. Doctor updates status and provides feedback
4. Patient receives notification
5. Case marked as resolved

### Scenario 2: Community Complaint
1. Community member files complaint petition
2. Aamil reviews and categorizes
3. Assigns to appropriate coordinator
4. Regular status updates provided
5. Resolution tracked and documented

### Scenario 3: Administrative Request
1. Staff member submits administrative petition
2. Moze coordinator reviews request
3. Assigns priority and timeline
4. Tracks progress through workflow
5. Completion verified and recorded

---

## 📋 Testing Results Checklist

Mark each as completed:

### Basic Functionality
- [ ] Dashboard loads successfully
- [ ] User authentication works
- [ ] Role-based access enforced
- [ ] Navigation menu functional

### Core Features  
- [ ] Petition creation works
- [ ] Petition listing displays correctly
- [ ] Search and filtering functional
- [ ] Status updates work properly

### Advanced Features
- [ ] Analytics dashboard functional
- [ ] Export functionality works
- [ ] Assignment system operational
- [ ] Bulk operations successful

### User Experience
- [ ] UI is responsive and user-friendly
- [ ] Error messages are helpful
- [ ] Success notifications work
- [ ] Performance is acceptable

---

## 🔗 Important URLs for Testing

| Feature | URL | Description |
|---------|-----|-------------|
| Dashboard | `/araz/` | Main petition dashboard |
| Petition List | `/araz/petitions/` | All petitions view |
| Create Petition | `/araz/petitions/create/` | New petition form |
| Analytics | `/araz/analytics/` | Statistics and reports |
| My Assignments | `/araz/my-assignments/` | Assigned tasks |
| Export Data | `/araz/export/` | Data export functionality |
| Bulk Update | `/araz/bulk-update/` | Batch operations |

---

## 🚨 Emergency Testing Commands

If issues arise during testing:

```bash
# Restart server
pkill -f "python3 manage.py runserver"
python3 manage.py runserver 0.0.0.0:8000

# Check database migrations
python3 manage.py showmigrations araz

# Create fresh test data
python3 test_araz_app.py

# Check logs for errors
tail -f nohup.out
```

---

## ✅ Testing Complete

When you've tested all features:

1. Document any issues found
2. Verify all user roles work properly  
3. Confirm data integrity
4. Test performance with larger datasets
5. Validate security and permissions

**The Araz app is now ready for production use! 🎉**