# 🧪 Umoor Sehhat Testing Guide

This guide provides comprehensive instructions for testing your Umoor Sehhat application using bulk data upload and API testing features.

## 📊 **1. Bulk Data Upload for Testing**

### Quick Test Data (Recommended)
The simplest way to populate your application with test data:

```bash
python3 quick_test_data.py
```

**What it creates:**
- ✅ **15 Test Users** across all roles (3 users per role)
- ✅ **Admin Users**: admin_1, admin_2, admin_3
- ✅ **Doctor Users**: doctor_1, doctor_2, doctor_3  
- ✅ **Student Users**: student_1, student_2, student_3
- ✅ **Aamil Users**: aamil_1, aamil_2, aamil_3
- ✅ **Moze Coordinator Users**: moze_coordinator_1, moze_coordinator_2, moze_coordinator_3

**Test Login Credentials:**
- Original Admin: `admin` / `admin123`
- Test Users: `[role]_[number]` / `test123`
- Example: `doctor_1` / `test123`

### Benefits:
- 🚀 **Fast execution** (under 10 seconds)
- ✅ **Guaranteed to work** with current models
- 🎯 **Perfect for functionality testing**
- 👥 **Multiple user roles** to test permissions

---

## 🔌 **2. API Testing System**

### Mock ITS52.com API Server

The application includes a complete mock API system that simulates the ITS52.com integration:

#### Starting the Mock API Server:

```bash
python3 api_testing_system.py
```

Choose option **3** for "Start Server and Run Tests" for complete testing.

### API Features:

#### **Available Endpoints:**
- `POST /api/v1/user/verify` - Verify ITS user credentials
- `GET /api/v1/user/<its_id>` - Get user information
- `GET /api/v1/users/search` - Search users by criteria
- `PUT /api/v1/user/update` - Update user information
- `GET /api/v1/stats` - Get API statistics
- `GET /api/v1/health` - Health check

#### **Mock Data:**
- 🎯 **1000 Mock ITS Users** with realistic data
- 📊 **Comprehensive user profiles** including college, jamaat, status
- 🔐 **Authentication testing** with test password: `test123`
- 🔍 **Search functionality** by name, jamaat, status

#### **Testing Scenarios:**
1. **User Verification**: Test valid/invalid ITS credentials
2. **User Search**: Search by name, location, status
3. **Django Integration**: Create Django users from ITS data
4. **API Health**: Monitor API performance and availability
5. **Statistics**: Track API usage and user data

### Manual API Testing:

#### Test User Verification:
```bash
curl -X POST http://localhost:5000/api/v1/user/verify \
  -H "Content-Type: application/json" \
  -d '{"its_id": "12345678", "password": "test123"}'
```

#### Test User Search:
```bash
curl "http://localhost:5000/api/v1/users/search?q=Ahmed&limit=5"
```

#### Check API Health:
```bash
curl http://localhost:5000/api/v1/health
```

#### Get API Statistics:
```bash
curl http://localhost:5000/api/v1/stats
```

---

## 🎯 **3. Complete Testing Workflow**

### Step 1: Populate Test Data
```bash
# Create basic test users
python3 quick_test_data.py
```

### Step 2: Start Django Application
```bash
# Start the main application
python3 manage.py runserver
```

### Step 3: Test API Integration (Optional)
```bash
# In a new terminal, start API testing
python3 api_testing_system.py
# Choose option 3: "Start Server and Run Tests"
```

### Step 4: Manual Testing
1. **Login Testing**:
   - Visit: http://localhost:8000/accounts/login/
   - Try different user roles: `admin_1`, `doctor_1`, `student_1`, etc.
   - Password for all: `test123`

2. **Admin Panel Testing**:
   - Visit: http://localhost:8000/admin/
   - Login: `admin` / `admin123`
   - Verify all models are accessible

3. **App Functionality Testing**:
   - **Moze Management**: http://localhost:8000/moze/
   - **Student Portal**: http://localhost:8000/students/
   - **Survey System**: http://localhost:8000/surveys/
   - **Araz Requests**: http://localhost:8000/araz/
   - **Doctor Directory**: http://localhost:8000/doctordirectory/
   - **Hospital Management**: http://localhost:8000/mahalshifa/
   - **Evaluation System**: http://localhost:8000/evaluation/
   - **Photo Gallery**: http://localhost:8000/photos/

---

## 🔧 **4. Advanced Testing**

### Role-Based Access Testing
Test each user role's permissions:

1. **Admin Users** (`admin_1`):
   - Full access to all modules
   - Admin panel access
   - User management capabilities

2. **Doctor Users** (`doctor_1`):
   - Doctor directory access
   - Patient management
   - Medical records

3. **Student Users** (`student_1`):
   - Student portal access
   - Academic records
   - Survey participation

4. **Aamil Users** (`aamil_1`):
   - Moze management
   - Community coordination

5. **Moze Coordinator Users** (`moze_coordinator_1`):
   - Operational oversight
   - Activity coordination

### Integration Testing with ITS API

1. **Start Mock API**: `python3 api_testing_system.py`
2. **Test User Verification**: Create Django users from ITS data
3. **Test Search Functionality**: Find users by various criteria
4. **Test Data Synchronization**: Update user information

---

## 📋 **5. Testing Checklist**

### ✅ **Basic Functionality**
- [ ] User registration and login
- [ ] Admin panel access
- [ ] All 8 app modules accessible
- [ ] Database operations (CRUD)
- [ ] User role permissions

### ✅ **Data Testing**
- [ ] Test users created successfully
- [ ] User profiles working
- [ ] Role-based access control
- [ ] Data persistence across sessions

### ✅ **API Testing**
- [ ] Mock API server starts
- [ ] User verification works
- [ ] Search functionality works
- [ ] Django-API integration works
- [ ] API health checks pass

### ✅ **Security Testing**
- [ ] Authentication required for protected views
- [ ] Role-based access enforced
- [ ] CSRF protection working
- [ ] Invalid credentials rejected

---

## 🚀 **6. Production Preparation**

### Before Deploying:
1. **Remove Test Data**: Clear test users before production
2. **Update API URLs**: Replace mock API with real ITS52.com endpoints
3. **Configure Authentication**: Set up proper API keys and tokens
4. **Security Review**: Ensure all security measures are in place

### API Integration for Production:
1. **Replace Mock URLs**: Update API base URL to real ITS endpoints
2. **Add Authentication**: Include proper API keys/tokens
3. **Error Handling**: Implement proper error handling for API failures
4. **Rate Limiting**: Respect ITS API rate limits
5. **Data Mapping**: Adjust data field mappings if needed

---

## 🎯 **Quick Commands Reference**

```bash
# Bulk test data
python3 quick_test_data.py

# Start Django app
python3 manage.py runserver

# API testing (in new terminal)
python3 api_testing_system.py

# Test specific endpoints
curl http://localhost:8000/  # Main app
curl http://localhost:5000/api/v1/health  # API health

# Login credentials
# Admin: admin / admin123
# Test users: [role]_[number] / test123
```

---

## 🎉 **Success Metrics**

Your testing is successful when:
- ✅ **All user roles** can login and access appropriate features
- ✅ **All 8 app modules** are accessible and functional
- ✅ **API integration** works with mock ITS system
- ✅ **Database operations** work correctly
- ✅ **Security measures** are enforced properly

---

*This testing guide ensures your Umoor Sehhat application is fully functional and ready for production deployment!*