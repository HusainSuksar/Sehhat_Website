# ITS API Production Transition Guide

This guide explains how to seamlessly transition from the current database simulation to the real ITS API in production.

## 🔧 Current State (Development)

- **Mode**: Database simulation
- **ITS Validation**: Only users from `generate_mock_data_enhanced.py` can login
- **Data Source**: Local database
- **Authentication**: Mock password validation (4+ characters)

## 🚀 Production Transition

### Step 1: Environment Configuration

Set these environment variables in your production environment:

```bash
# Enable real ITS API
export USE_REAL_ITS_API=True

# ITS API Endpoints
export ITS_API_URL=https://your-real-its-api.com/api/user
export ITS_AUTH_URL=https://your-real-its-api.com/api/authenticate

# ITS API Credentials
export ITS_API_KEY=your_actual_api_key
export ITS_API_SECRET=your_actual_api_secret

# Optional: Timeout and retry settings
export ITS_API_TIMEOUT=30
export ITS_API_RETRY_ATTEMPTS=3
export ITS_API_CACHE_TIMEOUT=300
```

### Step 2: Implement Real API Calls

Edit `/workspace/accounts/services.py` and replace the TODO sections:

#### A. In `fetch_user_data()` method (lines 120-134):

```python
# Replace this TODO section:
# TODO: Implement real ITS API call here

# With actual implementation:
import requests
from django.conf import settings

response = requests.post(
    settings.ITS_API_URL,
    json={
        'its_id': its_id,
        'api_key': settings.ITS_API_KEY
    },
    timeout=settings.ITS_API_TIMEOUT
)

if response.status_code == 200:
    api_data = response.json()
    return cls._format_its_api_response(api_data)
else:
    logger.error(f"ITS API returned {response.status_code} for ITS ID {its_id}")
    return None
```

#### B. In `authenticate_user()` method (lines 210-229):

```python
# Replace this TODO section:
# TODO: Implement real ITS API authentication here

# With actual implementation:
response = requests.post(
    settings.ITS_AUTH_URL,
    json={
        'its_id': its_id,
        'password': password,
        'api_key': settings.ITS_API_KEY
    },
    timeout=settings.ITS_API_TIMEOUT
)

if response.status_code == 200:
    api_response = response.json()
    if api_response.get('authenticated'):
        user_data = cls._format_its_api_response(api_response['user_data'])
        role = cls.determine_user_role(user_data)
        return {
            'authenticated': True,
            'user_data': user_data,
            'role': role,
            'login_timestamp': datetime.now().isoformat(),
            'auth_source': 'its_api'
        }
    else:
        return None
else:
    logger.error(f"ITS API auth returned {response.status_code} for ITS ID {its_id}")
    return None
```

### Step 3: Adjust Response Format Mapping

Update the `_format_its_api_response()` method (lines 279-308) to match your real ITS API response format:

```python
def _format_its_api_response(cls, api_data: Dict) -> Dict:
    """
    Format real ITS API response to match our expected format
    """
    # Adjust these field mappings based on your real ITS API
    return {
        'its_id': api_data.get('its_id'),
        'first_name': api_data.get('firstName'),  # Note: adjust field names
        'last_name': api_data.get('lastName'),
        'full_name': api_data.get('fullName'),
        'arabic_full_name': api_data.get('arabicName'),
        'prefix': api_data.get('title'),
        'age': api_data.get('age'),
        'gender': api_data.get('gender'),
        'marital_status': api_data.get('maritalStatus'),
        'misaq': api_data.get('misaqNumber'),
        'occupation': api_data.get('occupation'),
        'qualification': api_data.get('education'),
        'idara': api_data.get('idara'),
        'category': api_data.get('category'),
        'organization': api_data.get('organization'),
        'mobile_number': api_data.get('mobileNumber'),
        'whatsapp_number': api_data.get('whatsappNumber'),
        'address': api_data.get('address'),
        'jamaat': api_data.get('jamaat'),
        'jamiaat': api_data.get('jamiaat'),
        'nationality': api_data.get('nationality'),
        'vatan': api_data.get('vatan'),
        'city': api_data.get('city'),
        'country': api_data.get('country'),
        'hifz_sanad': api_data.get('hifzSanad'),
        'photograph': api_data.get('photoUrl'),
    }
```

### Step 4: Test the Transition

1. **Start with staging environment**:
   ```bash
   export USE_REAL_ITS_API=True
   export ITS_API_URL=https://staging-its-api.com/api/user
   # ... other staging settings
   ```

2. **Test key functionality**:
   - User login with real ITS credentials
   - ITS ID lookup in appointment booking
   - User registration flow
   - Role-based access control

3. **Monitor logs** for API call success/failure rates

### Step 5: Production Deployment

1. **Set production environment variables**
2. **Deploy updated code**
3. **Monitor system logs** for any issues
4. **Verify all features work** with real ITS data

## ✅ What Remains the Same

The following functionality will work **exactly the same** after transition:

- **8-digit ITS ID validation** ✅
- **Appointment booking forms** ✅
- **User role determination** ✅
- **Permission systems** ✅
- **Frontend ITS ID lookup** ✅
- **All existing templates and views** ✅

## 🔄 What Changes

- **Data source**: Database → Real ITS API
- **ITS ID acceptance**: Generated mock data only → Any valid ITS ID from API
- **Authentication**: Mock validation → Real ITS password validation
- **User creation**: Pre-generated → Dynamic from API data

## 🛡️ Error Handling

The system includes comprehensive error handling:

- **API timeouts**: Configurable timeout settings
- **Network failures**: Retry mechanisms
- **Invalid responses**: Graceful fallback
- **Logging**: Detailed error logging for debugging

## 📊 Benefits After Transition

1. **Real user data** from ITS system
2. **Dynamic user discovery** - any valid ITS ID works
3. **Authentic password validation**
4. **Up-to-date user information**
5. **Production-ready authentication**

## 🔧 Rollback Plan

If issues occur, you can quickly rollback:

```bash
# Switch back to database simulation
export USE_REAL_ITS_API=False
```

The system will immediately revert to using your generated mock data.

---

**The transition is designed to be seamless - your 8-digit ITS ID validation and all appointment functionality will work perfectly with real ITS API data!** 🚀