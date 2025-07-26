#!/usr/bin/env python3
"""
Script to commit the populated test data and create documentation
"""

import os
import subprocess
from datetime import datetime

def run_command(command):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def create_test_data_documentation():
    """Create documentation for the test data"""
    doc_content = f"""# 🏥 Umoor Sehhat - Test Data Documentation

**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Test Data Summary

This database contains comprehensive test data for all 9 Django applications in the Umoor Sehhat system.

### 👥 User Accounts

- **2 Admin Users** (admin_1, admin_2) - Password: `admin123`
- **100 Doctor Users** (doctor_001 to doctor_100) - Password: `doctor123`
- **500 Student Users** (student_001 to student_500) - Password: `student123`
- **10 Staff Users** (staff_1 to staff_10) - Password: `staff123`
- **20 Aamil Users** (aamil_1 to aamil_20) - Password: `aamil123`
- **15 Moze Coordinator Users** (coordinator_1 to coordinator_15) - Password: `coord123`

**Total Users: 647**

### 📚 Students App Data

- **500 Student Profiles** with complete academic information
- **10 Medical Courses** (ANAT101, PHYS102, BIOC103, etc.)
- **Student Enrollments** for 300 students across multiple courses
- **50 Academic Events** (lectures, workshops, seminars, etc.)
- **Course Announcements** for each course

### 📋 Surveys App Data

- **10 Comprehensive Surveys** covering various topics:
  - Medical Service Satisfaction
  - Educational Quality Assessment
  - Facility Infrastructure Review
  - Staff Performance Evaluation
  - Student Learning Experience
  - Healthcare Accessibility Survey
  - Technology Usage Assessment
  - Community Engagement Survey
  - Safety and Security Review
  - Future Improvement Suggestions
- **Survey Responses** from multiple users (20-100 responses per survey)

### 🕌 Moze App Data

- **72 Moze Centers** distributed across major Pakistani cities
- **Moze Comments** with community feedback and engagement
- Complete organizational structure with Aamils and Coordinators

### 🏥 Mahalshifa (Hospital Management) Data

- **20 Hospitals** with different types (general, specialty, clinic)
- **Hospital Doctors** linked to user accounts
- **200 Patients** with complete medical records
- **300 Appointments** across different statuses
- **Hospital Inventory** with medical supplies and equipment

### 👨‍⚕️ Doctor Directory Data

- **100 Doctor Profiles** with specializations and qualifications
- **150 Directory Patients** 
- **200 Medical Records** with treatment history
- Complete consultation and appointment system

### 📝 Evaluation App Data

- **20 Evaluation Forms** for different purposes
- **Evaluation Submissions** from various user roles
- Performance tracking and feedback system

### 📄 Araz (Petition Management) Data

- **100 Petitions** across different categories:
  - Medical complaints
  - Administrative requests
  - Academic issues
  - Facility concerns
- **Petition Comments** with internal and public feedback
- Complete workflow tracking

### 📸 Photos App Data

- **10 Photo Albums** covering various events:
  - Medical Conference 2024
  - Student Activities
  - Hospital Events
  - Moze Gatherings
  - Educational Workshops
  - Community Service
  - Sports Events
  - Cultural Programs
  - Graduation Ceremony
  - Research Projects
- **Photo Tags** for organized categorization
- **Dummy Images** for testing display functionality

## 🔐 Login Credentials

### Admin Access
- Username: `admin_1` or `admin_2`
- Password: `admin123`

### Quick Test Users
- **Doctor**: `doctor_001` / `doctor123`
- **Student**: `student_001` / `student123`
- **Aamil**: `aamil_1` / `aamil123`
- **Staff**: `staff_1` / `staff123`

## 🚀 Testing Instructions

1. **Start the server**: `python3 manage.py runserver`
2. **Access admin panel**: `http://localhost:8000/admin/`
3. **Test user dashboards**: Login with different user roles
4. **Explore each app**: Navigate through all 9 application modules

## 📱 Application URLs

- **Main Site**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/
- **Students**: http://localhost:8000/students/
- **Surveys**: http://localhost:8000/surveys/
- **Mahalshifa**: http://localhost:8000/mahalshifa/
- **Moze**: http://localhost:8000/moze/
- **Photos**: http://localhost:8000/photos/
- **Doctor Directory**: http://localhost:8000/doctordirectory/
- **Evaluation**: http://localhost:8000/evaluation/
- **Araz**: http://localhost:8000/araz/

## 🔄 Data Regeneration

To regenerate fresh test data:
```bash
python3 populate_test_data.py
```

⚠️ **Warning**: This will delete all existing data and create new test data.

## 📈 Performance Notes

- Database size: ~1.6MB with full test data
- All relationships properly configured
- Foreign key constraints maintained
- Realistic data distribution for testing

---

**System Status**: ✅ Ready for Testing  
**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    with open('TEST_DATA_DOCUMENTATION.md', 'w') as f:
        f.write(doc_content)
    
    print("✅ Test data documentation created: TEST_DATA_DOCUMENTATION.md")

def main():
    print("🔄 Committing test data to repository...")
    
    # Create documentation
    create_test_data_documentation()
    
    # Add all files
    success, stdout, stderr = run_command("git add .")
    if not success:
        print(f"❌ Failed to add files: {stderr}")
        return
    
    # Check if there are changes to commit
    success, stdout, stderr = run_command("git status --porcelain")
    if not stdout.strip():
        print("✅ No changes to commit - repository is up to date")
        return
    
    # Commit changes
    commit_message = f"""Add comprehensive test data for all 9 apps

🎯 TEST DATA POPULATED:
✅ 647 Users across all roles (Admin, Doctor, Student, Staff, Aamil, Coordinator)
✅ 500 Students with academic profiles and enrollments
✅ 50+ Doctors with specializations and profiles  
✅ 72 Moze centers with organizational structure
✅ 20 Hospitals with complete medical facilities
✅ 10 Comprehensive surveys with responses
✅ Photo galleries with organized albums
✅ Evaluation forms and submissions

🔐 LOGIN CREDENTIALS:
- Admin: admin_1 / admin123
- Doctor: doctor_001 / doctor123  
- Student: student_001 / student123
- Staff: staff_1 / staff123

🚀 READY FOR TESTING:
- All 9 Django apps fully populated
- Realistic data relationships
- Complete user workflows
- Cross-platform compatible

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
    
    success, stdout, stderr = run_command(f'git commit -m "{commit_message}"')
    if not success:
        print(f"❌ Failed to commit: {stderr}")
        return
    
    print("✅ Changes committed successfully")
    
    # Push to remote
    success, stdout, stderr = run_command("git push origin main")
    if success:
        print("✅ Changes pushed to remote repository")
        print("\n🎉 TEST DATA DEPLOYMENT COMPLETE!")
        print("\n📋 NEXT STEPS:")
        print("1. Pull the latest changes on your MacBook")
        print("2. Run: python3 manage.py runserver")
        print("3. Login with admin_1 / admin123")
        print("4. Test all 9 applications")
    else:
        print(f"⚠️  Push failed: {stderr}")
        print("💡 You may need to pull changes first")

if __name__ == "__main__":
    main()