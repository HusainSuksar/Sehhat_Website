# 🧪 **UMOOR SEHHAT TESTING GUIDE**

## **🎯 TESTING OBJECTIVES**

Test all functionality across different user roles without requiring ITS database integration.

## **🔑 TEST CREDENTIALS**

All test accounts use password: `test123456`

### **Admin Users**
- Username: `admin_user1` | Name: Ahmed Khan
- Username: `admin_user2` | Name: Fatima Ali

### **Students** 
- Username: `student_001` | Name: Mohammad Hassan
- Username: `student_002` | Name: Aisha Ahmed  
- Username: `student_003` | Name: Omar Sheikh

### **Doctors**
- Username: `doctor_001` | Name: Dr. Yasmin Rashid
- Username: `doctor_002` | Name: Dr. Imran Malik

### **Aamils** (Moze Managers)
- Username: `aamil_001` | Name: Abdullah Rahman
- Username: `aamil_002` | Name: Khadija Siddique

### **Coordinators**
- Username: `coordinator_001` | Name: Hassan Qureshi
- Username: `coordinator_002` | Name: Zainab Tariq

---

## **📋 TESTING SCENARIOS**

### **1. Admin Dashboard Testing**
**Login as:** `admin_user1`

**Test Cases:**
- [ ] Dashboard loads with statistics
- [ ] User management functionality
- [ ] Create evaluation forms
- [ ] View Moze prioritization dashboard
- [ ] Access all navigation links
- [ ] Edit/delete users
- [ ] View evaluation results

**Expected Results:**
- All statistics display correctly
- Can create/edit evaluation forms
- Moze prioritization shows evaluation data
- Full access to all system features

---

### **2. Student Dashboard Testing**
**Login as:** `student_001`, `student_002`, `student_003`

**Test Cases:**
- [ ] Dashboard displays student-specific data
- [ ] Access to student-only features
- [ ] Navigation menu shows appropriate links
- [ ] Can view own grades/analytics
- [ ] Cannot access admin features

**Expected Results:**
- Student-specific dashboard layout
- Restricted access (no admin/evaluation features)
- Personal data displays correctly

---

### **3. Doctor Dashboard Testing**
**Login as:** `doctor_001`, `doctor_002`

**Test Cases:**
- [ ] Doctor directory access
- [ ] Appointment management
- [ ] Patient records access
- [ ] Medical center integration
- [ ] Navigation shows doctor-specific links

**Expected Results:**
- Doctor-focused dashboard
- Medical features accessible
- Cannot access student/admin features

---

### **4. Aamil Dashboard Testing**
**Login as:** `aamil_001`, `aamil_002`

**Test Cases:**
- [ ] Can access evaluation forms
- [ ] Moze selection auto-populates
- [ ] Can submit evaluations
- [ ] Dashboard shows Moze management features
- [ ] Evaluation results hidden from aamil

**Expected Results:**
- Evaluation form shows assigned Moze
- Can complete evaluations
- Cannot see evaluation scores/grades
- Moze management features available

---

### **5. Coordinator Dashboard Testing**
**Login as:** `coordinator_001`, `coordinator_002`

**Test Cases:**
- [ ] Access to coordination features
- [ ] Can view assigned Mozes
- [ ] Academic affairs functionality
- [ ] Proper navigation restrictions

**Expected Results:**
- Coordinator-specific features
- Limited access compared to admin
- Moze coordination tools available

---

### **6. Evaluation System Testing**

**Admin Testing (admin_user1):**
- [ ] Create new evaluation forms
- [ ] Add questions with weighted answers
- [ ] Assign target roles
- [ ] View all evaluation results
- [ ] See Moze prioritization dashboard

**Aamil Testing (aamil_001):**
- [ ] Find "Evaluate" buttons on forms
- [ ] Moze field auto-selects assigned Moze
- [ ] Submit complete evaluation
- [ ] Cannot view scores/grades
- [ ] Results marked as confidential

**Result Verification:**
- [ ] Scores calculated correctly
- [ ] Grades assigned (A, B, C, D, E)
- [ ] Priority levels determined
- [ ] Results visible only to admin

---

### **7. Navigation & Access Control Testing**

**For Each Role:**
- [ ] Hamburger menu shows role-appropriate links
- [ ] Unauthorized pages redirect properly
- [ ] Dashboard displays correct features
- [ ] Role-specific statistics shown

**Cross-Role Testing:**
- [ ] Students cannot access admin features
- [ ] Doctors cannot see student data
- [ ] Aamils cannot view evaluation results
- [ ] Only admins see full system access

---

### **8. Data Integrity Testing**

**Test Scenarios:**
- [ ] User data displays correctly
- [ ] Relationships between users work
- [ ] Moze assignments function properly
- [ ] Evaluation submissions save correctly
- [ ] Statistics calculate accurately

---

### **9. Performance Testing**

**Test Cases:**
- [ ] Dashboard loads within 3 seconds
- [ ] Large datasets render properly
- [ ] Navigation is smooth
- [ ] Forms submit without delays
- [ ] Static files load correctly

---

### **10. Mobile Responsiveness Testing**

**Test on Different Devices:**
- [ ] Dashboards responsive on mobile
- [ ] Navigation menu works on tablets
- [ ] Forms usable on small screens
- [ ] Statistics display properly
- [ ] Premium UI effects work

---

## **🐛 COMMON ISSUES & SOLUTIONS**

### **Database Connection Issues**
```python
# Test database connection
python manage.py dbshell --settings=umoor_sehhat.settings_pythonanywhere
```

### **Static Files Not Loading**
```bash
python manage.py collectstatic --noinput --settings=umoor_sehhat.settings_pythonanywhere
```

### **User Authentication Issues**
```python
# Reset user passwords
python manage.py shell --settings=umoor_sehhat.settings_pythonanywhere
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(username='admin_user1')
user.set_password('test123456')
user.save()
```

### **Evaluation System Issues**
```python
# Verify evaluation data
from evaluation.models import EvaluationForm, EvaluationSubmission
print(f"Forms: {EvaluationForm.objects.count()}")
print(f"Submissions: {EvaluationSubmission.objects.count()}")
```

---

## **✅ TESTING CHECKLIST**

**Pre-Testing Setup:**
- [ ] PythonAnywhere deployment complete
- [ ] All test users created
- [ ] Sample data populated
- [ ] Static files collected
- [ ] Database migrations applied

**Core Functionality:**
- [ ] All dashboards load correctly
- [ ] Role-based access control works
- [ ] Navigation menus appropriate
- [ ] Statistics display properly
- [ ] Premium UI effects optimized

**Evaluation System:**
- [ ] Forms creation/editing works
- [ ] Question types function properly
- [ ] Weighted scoring calculates
- [ ] Grade assignments correct
- [ ] Result visibility controlled

**User Experience:**
- [ ] Mobile responsiveness verified
- [ ] Performance acceptable
- [ ] Error handling graceful
- [ ] Security measures active
- [ ] Backup/monitoring setup

---

## **🎯 SUCCESS CRITERIA**

The testing is successful when:
1. All user roles can access appropriate features
2. Evaluation system works end-to-end
3. No security vulnerabilities exposed
4. Performance meets expectations
5. Mobile users can use all features
6. Data integrity maintained throughout

---

## **📊 TESTING REPORT TEMPLATE**

After testing, document:
- **Tested Features:** List all tested functionality
- **Issues Found:** Document any bugs or problems
- **Performance Metrics:** Load times, responsiveness
- **User Experience:** Feedback on usability
- **Recommendations:** Improvements for production

---

**🌐 Test URL:** `https://yourusername.pythonanywhere.com`
**📧 Support:** Contact for any testing issues