# 🔄 **HYBRID API INTEGRATION SYSTEM**

## 📋 **OVERVIEW**

The Umoor Sehhat application now supports a **hybrid data approach** that combines:
- **Local Database Data** (your Django models)
- **External API Data** (from Beeceptor or other APIs)

This provides flexibility to show both internal and external data in a unified interface.

---

## 🏗️ **ARCHITECTURE**

### **Service Layer Architecture:**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Django Views  │    │  Data Service   │    │  API Service    │
│   (UI Layer)    │◄──►│  (Hybrid Logic) │◄──►│ (External APIs) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Local Database  │
                       │ (Django Models) │
                       └─────────────────┘
```

---

## 📂 **FILE STRUCTURE**

### **New Files Created:**
```
umoor_sehhat/
├── services/
│   ├── api_service.py          # External API integration
│   └── data_service.py         # Hybrid data service
├── accounts/
│   ├── views_api.py            # Hybrid views
│   └── urls_api.py             # API URLs
├── templates/accounts/
│   └── hybrid_dashboard.html   # Demo template
├── beeceptor_mock_api.js       # Mock API script
└── requirements.txt            # Updated with requests
```

---

## ⚙️ **CONFIGURATION**

### **1. Settings Configuration (`settings.py`):**
```python
# API Integration Settings
BEECEPTOR_API_URL = 'https://your-endpoint.free.beeceptor.com'
API_TIMEOUT = 30
API_CACHE_TIMEOUT = 300  # 5 minutes

# Cache configuration for API responses
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        # ... cache settings
    }
}
```

### **2. Environment Variables (Optional):**
```bash
export BEECEPTOR_API_URL="https://your-endpoint.free.beeceptor.com"
export API_TIMEOUT="30"
export API_CACHE_TIMEOUT="300"
```

---

## 🔧 **USAGE EXAMPLES**

### **1. Basic API Service Usage:**
```python
from services.api_service import api_service

# Get external doctors
external_doctors = api_service.get_external_doctors(specialty='Cardiology')

# Get API status
status = api_service.get_api_status()
print(f"API Available: {status['is_available']}")
```

### **2. Hybrid Data Service Usage:**
```python
from services.data_service import data_service

# Get all doctors (local + external)
all_doctors = data_service.get_all_doctors(include_external=True)
print(f"Local: {len(all_doctors['local_doctors'])}")
print(f"External: {len(all_doctors['external_doctors'])}")

# Get hybrid dashboard statistics
stats = data_service.get_dashboard_statistics()
print(f"Total users: {stats['combined_stats']['total_users']}")
```

### **3. In Django Views:**
```python
from services.data_service import data_service

def my_view(request):
    # Get hybrid hospital data
    hospitals = data_service.get_all_hospitals(include_partners=True)
    
    context = {
        'local_hospitals': hospitals['local_hospitals'],
        'partner_hospitals': hospitals['partner_hospitals'],
        'total_count': hospitals['total_count'],
    }
    return render(request, 'my_template.html', context)
```

---

## 🌐 **URL ENDPOINTS**

### **Hybrid Views:**
- `/api/hybrid-dashboard/` - Dashboard with local + external data
- `/api/hybrid-doctors/` - All doctors (local + external)
- `/api/hybrid-hospitals/` - All hospitals (local + partners)
- `/api/hybrid-surveys/` - All surveys (local + regional)

### **AJAX API Endpoints:**
- `/api/api/search-doctors/` - Search across both sources
- `/api/api/refresh-cache/` - Refresh external API cache
- `/api/api/system-status/` - Get system status
- `/api/api-config/` - API configuration page

---

## 📊 **DATA SOURCES**

### **Local Database (Django Models):**
- ✅ **Users, Students, Doctors** - Your internal users
- ✅ **Hospitals, Patients** - Local healthcare data
- ✅ **Surveys, Evaluations** - Internal forms
- ✅ **Petitions, Moze Centers** - Community data

### **External API (Beeceptor):**
- 🌐 **External Doctors** - Visiting specialists, consultants
- 🌐 **Partner Hospitals** - Referral centers
- 🌐 **Regional Surveys** - External feedback forms
- 🌐 **Regional Evaluations** - External assessments

---

## 🎯 **USE CASES**

### **1. Healthcare Network:**
```python
# Show both local staff and visiting doctors
doctors_data = data_service.get_all_doctors(include_external=True)

# Local: Your hospital's doctors
# External: Visiting specialists from partner hospitals
```

### **2. Multi-Location Management:**
```python
# Show both your hospitals and partner facilities
hospitals_data = data_service.get_all_hospitals(include_partners=True)

# Local: Your managed hospitals
# External: Partner hospitals for referrals
```

### **3. Regional Surveys:**
```python
# Combine internal and regional surveys
surveys_data = data_service.get_all_surveys(include_regional=True)

# Local: Your internal surveys
# External: Regional/national surveys
```

---

## 🔧 **CUSTOMIZATION**

### **1. Adding New External Data Sources:**

**Step 1:** Add method to `api_service.py`:
```python
def get_external_specialists(self, department: str) -> List[Dict]:
    data = self._get_cached_data(f"specialists_{department}", '/api/specialists/')
    return data.get('results', [])
```

**Step 2:** Add hybrid method to `data_service.py`:
```python
def get_all_specialists(self, include_external: bool = True) -> Dict:
    # Combine local and external specialists
    pass
```

**Step 3:** Create view in `views_api.py`:
```python
def hybrid_specialists_view(request):
    specialists = data_service.get_all_specialists()
    return render(request, 'hybrid_specialists.html', {'specialists': specialists})
```

### **2. Configuring Different API Endpoints:**
```python
# In api_service.py
class MultiAPIService:
    def __init__(self):
        self.beeceptor_url = settings.BEECEPTOR_API_URL
        self.partner_api_url = settings.PARTNER_API_URL
        self.regional_api_url = settings.REGIONAL_API_URL
```

---

## 🚀 **GETTING STARTED**

### **1. Setup Beeceptor:**
1. Go to [beeceptor.com](https://beeceptor.com)
2. Create endpoint: `your-endpoint.free.beeceptor.com`
3. Copy content from `beeceptor_mock_api.js`
4. Paste into Beeceptor's "Custom Script" section

### **2. Update Configuration:**
```python
# In settings.py or environment
BEECEPTOR_API_URL = 'https://your-endpoint.free.beeceptor.com'
```

### **3. Test the Integration:**
```bash
# Start Django development server
python manage.py runserver

# Visit the hybrid dashboard
http://localhost:8000/api/hybrid-dashboard/
```

### **4. Verify API Connection:**
- Check system status in the dashboard
- Green indicator = API connected
- Red indicator = API offline (falls back to local data only)

---

## 🎛️ **FEATURES**

### **✅ Automatic Caching:**
- API responses cached for 5 minutes (configurable)
- Reduces external API calls
- Improves performance

### **✅ Error Handling:**
- Graceful fallback to local data if API fails
- User-friendly error messages
- Automatic retry mechanisms

### **✅ Real-time Status:**
- Live API status monitoring
- Auto-refresh status indicators
- Health check endpoints

### **✅ Admin Controls:**
- Cache refresh buttons
- API configuration page
- System status dashboard

---

## 🔍 **MONITORING & DEBUGGING**

### **Logs:**
```bash
# API integration logs
tail -f logs/api.log

# Check for connection errors, timeouts, etc.
```

### **Cache Status:**
```python
from django.core.cache import cache
from services.api_service import api_service

# Check if API is available
print(api_service.is_api_available())

# Clear cache manually
api_service.clear_cache()
```

### **Debug Mode:**
```python
# In settings.py for development
LOGGING['loggers']['services.api_service']['level'] = 'DEBUG'
```

---

## 💡 **BENEFITS**

### **🔄 Flexibility:**
- Mix local and external data seamlessly
- Toggle external sources on/off
- Graceful degradation when APIs are unavailable

### **⚡ Performance:**
- Intelligent caching reduces API calls
- Local data always fast
- Non-blocking external data loading

### **🔧 Maintainability:**
- Clean service layer architecture
- Centralized API logic
- Easy to add new data sources

### **👥 User Experience:**
- Unified interface for all data
- Clear indication of data sources
- Real-time status feedback

---

**Your application now supports both local database and external API data in a unified, flexible system!** 🎉