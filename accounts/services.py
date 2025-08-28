"""
ITS API Service for user data fetching and authentication
Supports both Mock and Real ITS API integration
"""
import random
from datetime import datetime
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)

# Generate 100 moze names
MOZE_NAMES = [f"Moze {chr(65 + i // 4)}{i % 4 + 1}" for i in range(100)]  # A1-A4, B1-B4, ... Z1-Z4


class ITSService:
    """
    ITS Service for authentication and user data.
    Role determination based on ITS data:
    1. If occupation = "Doctor" -> role = "doctor"
    2. If category = "Amil" -> role = "aamil" 
    3. If ITS ID in uploaded coordinator list -> role = "moze_coordinator"
    4. If ITS ID in uploaded student list -> role = "student"
    5. All others -> role = "patient"
    """
    
    # Moze names
    MOZE_NAMES = MOZE_NAMES
    
    # Sample data pools for generating realistic mock data
    FIRST_NAMES = [
        'Mohammed', 'Ahmed', 'Ali', 'Hassan', 'Hussein', 'Fatima', 'Zainab', 'Khadija', 
        'Aisha', 'Mariam', 'Omar', 'Yusuf', 'Ibrahim', 'Ismail', 'Mustafa', 'Amina',
        'Safiya', 'Ruqayyah', 'Zahra', 'Maryam', 'Abdullah', 'Abdul Rahman', 'Khalid',
        'Bilal', 'Hamza', 'Umar', 'Uthman', 'Salman', 'Noor', 'Hanan', 'Ayesha',
        'Sakina', 'Taher', 'Abbas', 'Jafar', 'Murtaza', 'Burhanuddin', 'Qaidjoher'
    ]
    
    LAST_NAMES = [
        'Khan', 'Ali', 'Ahmed', 'Sheikh', 'Malik', 'Shah', 'Hussain', 'Qureshi',
        'Syed', 'Ansari', 'Shaikh', 'Patel', 'Merchant', 'Contractor', 'Engineer',
        'Doctor', 'Professor', 'Saifuddin', 'Najmuddin', 'Burhanuddin', 'Mohiyuddin',
        'Fakhruddin', 'Shamsuddin', 'Nooruddin', 'Ezzi', 'Bhinderwala', 'Rangwala'
    ]
    
    OCCUPATIONS = [
        'Student', 'Engineer', 'Teacher', 'Business Owner', 'Accountant', 
        'Consultant', 'Professional', 'Trader', 'Manager', 'Analyst',
        'Designer', 'Architect', 'Pharmacist', 'Nurse', 'Technician'
    ]
    
    QUALIFICATIONS = [
        'Bachelor of Science', 'Bachelor of Engineering', 'Bachelor of Commerce', 
        'MBA', 'Masters', 'PhD', 'Diploma', 'Certificate', 'High School',
        'Bachelor of Arts', 'Bachelor of Medicine', 'LLB', 'CA', 'CPA'
    ]
    
    CATEGORIES = ['General', 'Professional', 'Business', 'Service', 'Education']
    
    IDARAS = ['Mumbai', 'Delhi', 'Karachi', 'Dubai', 'London', 'New York', 'Ahmedabad', 'Pune', 'Bangalore', 'Surat']
    ORGANIZATIONS = ['Private', 'Government', 'Self-Employed', 'NGO', 'Educational Institution']
    JAMAATS = [
        'Mumbai Saifee', 'Mumbai Central', 'Delhi Nizamuddin', 'Karachi Saddar', 
        'Dubai Karama', 'London Northolt', 'Ahmedabad Kalupur', 'Pune Camp',
        'Bangalore Shivajinagar', 'Surat Rander', 'Kolkata Park Street'
    ]
    NATIONALITIES = ['Indian', 'Pakistani', 'UAE', 'British', 'American', 'Canadian', 'Kenyan', 'Tanzanian']
    CITIES = ['Mumbai', 'Delhi', 'Karachi', 'Dubai', 'London', 'New York', 'Ahmedabad', 'Pune', 'Bangalore', 'Surat']
    COUNTRIES = ['India', 'Pakistan', 'UAE', 'UK', 'USA', 'Canada', 'Kenya', 'Tanzania']
    
    # Lists to store uploaded ITS IDs for students and coordinators
    STUDENT_ITS_IDS = set()
    COORDINATOR_ITS_IDS = set()
    
    @classmethod
    def add_student_its_ids(cls, its_ids: List[str]):
        """Add ITS IDs to the student list"""
        cls.STUDENT_ITS_IDS.update(its_ids)
        logger.info(f"Added {len(its_ids)} student ITS IDs")
    
    @classmethod
    def add_coordinator_its_ids(cls, its_ids: List[str]):
        """Add ITS IDs to the coordinator list"""
        cls.COORDINATOR_ITS_IDS.update(its_ids)
        logger.info(f"Added {len(its_ids)} coordinator ITS IDs")
    
    @classmethod
    def fetch_user_data(cls, its_id: str) -> Optional[Dict]:
        """
        Fetch user data from ITS API (with database fallback for development)
        
        Args:
            its_id: 8-digit ITS ID
            
        Returns:
            Dictionary containing all ITS fields or None if not found
        """
        # Validate ITS ID format
        if not its_id or len(its_id) != 8 or not its_id.isdigit():
            return None
        
        # Convert to int for validation
        its_id_int = int(its_id)
        
        # Basic range validation
        if not (10000000 <= its_id_int <= 99999999):
            return None
        
        # TODO: Replace this section with real ITS API call in production
        # For now, check database first (development mode)
        from django.conf import settings
        from .models import User
        
        # Check if we should use real ITS API (production mode)
        use_real_its_api = getattr(settings, 'USE_REAL_ITS_API', False)
        
        if use_real_its_api:
            # PRODUCTION: Call real ITS API
            try:
                # TODO: Implement real ITS API call here
                # Example structure:
                # response = requests.post(settings.ITS_API_URL, {
                #     'its_id': its_id,
                #     'api_key': settings.ITS_API_KEY
                # })
                # if response.status_code == 200:
                #     api_data = response.json()
                #     return cls._format_its_api_response(api_data)
                # else:
                #     return None
                
                # For now, return None to indicate API not implemented
                logger.warning(f"Real ITS API not implemented yet for ITS ID: {its_id}")
                return None
                
            except Exception as e:
                logger.error(f"ITS API call failed for {its_id}: {str(e)}")
                return None
        else:
            # DEVELOPMENT: Use database as ITS API simulation
            try:
                existing_user = User.objects.get(its_id=its_id)
                logger.info(f"Found user {its_id} in database (development mode)")
                
                # Return data in ITS API format
                return {
                    'its_id': existing_user.its_id,
                    'first_name': existing_user.first_name,
                    'last_name': existing_user.last_name,
                    'full_name': existing_user.get_full_name(),
                    'arabic_full_name': existing_user.arabic_full_name,
                    'prefix': existing_user.prefix,
                    'age': existing_user.age,
                    'gender': existing_user.gender,
                    'marital_status': existing_user.marital_status,
                    'misaq': existing_user.misaq,
                    'occupation': existing_user.occupation,
                    'qualification': existing_user.qualification,
                    'idara': existing_user.idara,
                    'category': existing_user.category,
                    'organization': existing_user.organization,
                    'mobile_number': existing_user.mobile_number,
                    'whatsapp_number': existing_user.whatsapp_number,
                    'address': existing_user.address,
                    'jamaat': existing_user.jamaat,
                    'jamiaat': existing_user.jamiaat,
                    'nationality': existing_user.nationality,
                    'vatan': existing_user.vatan,
                    'city': existing_user.city,
                    'country': existing_user.country,
                    'hifz_sanad': existing_user.hifz_sanad,
                    'photograph': existing_user.profile_photo,
                }
            except User.DoesNotExist:
                logger.warning(f"User {its_id} not found in database (development mode)")
                return None

    
    @classmethod
    def authenticate_user(cls, its_id: str, password: str) -> Optional[Dict]:
        """
        Authenticate user against ITS API (with database fallback for development)
        
        Args:
            its_id: 8-digit ITS ID
            password: User's ITS password
            
        Returns:
            Authentication result with user data and role
        """
        # Validate ITS ID format
        if not cls.validate_its_id(its_id):
            logger.warning(f"Invalid ITS ID format: {its_id}")
            return None
        
        # Basic password validation
        if not password or len(password) < 4:
            logger.warning(f"Invalid password for ITS ID: {its_id}")
            return None
        
        from django.conf import settings
        from .models import User
        
        # Check if we should use real ITS API (production mode)
        use_real_its_api = getattr(settings, 'USE_REAL_ITS_API', False)
        
        if use_real_its_api:
            # PRODUCTION: Authenticate against real ITS API
            try:
                # TODO: Implement real ITS API authentication here
                # Example structure:
                # response = requests.post(settings.ITS_AUTH_URL, {
                #     'its_id': its_id,
                #     'password': password,
                #     'api_key': settings.ITS_API_KEY
                # })
                # if response.status_code == 200 and response.json().get('authenticated'):
                #     api_data = response.json()
                #     user_data = cls._format_its_api_response(api_data['user_data'])
                #     role = cls.determine_user_role(user_data)
                #     return {
                #         'authenticated': True,
                #         'user_data': user_data,
                #         'role': role,
                #         'login_timestamp': datetime.now().isoformat(),
                #         'auth_source': 'its_api'
                #     }
                # else:
                #     return None
                
                # For now, return None to indicate API not implemented
                logger.warning(f"Real ITS API authentication not implemented yet for ITS ID: {its_id}")
                return None
                
            except Exception as e:
                logger.error(f"ITS API authentication failed for {its_id}: {str(e)}")
                return None
        else:
            # DEVELOPMENT: Use database as ITS API simulation
            try:
                existing_user = User.objects.get(its_id=its_id)
                logger.info(f"Found existing user {its_id} in database (development mode)")
                
                # Get user data (will use database in development mode)
                user_data = cls.fetch_user_data(its_id)
                if not user_data:
                    logger.error(f"Failed to fetch user data for existing user: {its_id}")
                    return None
                
                # Use existing user's role or determine from ITS data
                role = existing_user.role or cls.determine_user_role(user_data)
                
                logger.info(f"User {its_id} authenticated successfully with role: {role}")
                
                # Return authentication result
                return {
                    'authenticated': True,
                    'user_data': user_data,
                    'role': role,
                    'login_timestamp': datetime.now().isoformat(),
                    'auth_source': 'database_simulation'
                }
                
            except User.DoesNotExist:
                logger.warning(f"User {its_id} not found in database (development mode)")
                return None
    
    @classmethod
    def _format_its_api_response(cls, api_data: Dict) -> Dict:
        """
        Format real ITS API response to match our expected format
        
        Args:
            api_data: Raw response from ITS API
            
        Returns:
            Formatted user data dictionary
        """
        # TODO: Adjust field mappings based on real ITS API response format
        # This is a template - modify based on actual ITS API structure
        return {
            'its_id': api_data.get('its_id'),
            'first_name': api_data.get('first_name'),
            'last_name': api_data.get('last_name'),
            'full_name': f"{api_data.get('first_name', '')} {api_data.get('last_name', '')}".strip(),
            'arabic_full_name': api_data.get('arabic_full_name', ''),
            'prefix': api_data.get('prefix', ''),
            'age': api_data.get('age'),
            'gender': api_data.get('gender'),
            'marital_status': api_data.get('marital_status'),
            'misaq': api_data.get('misaq', ''),
            'occupation': api_data.get('occupation', ''),
            'qualification': api_data.get('qualification', ''),
            'idara': api_data.get('idara', ''),
            'category': api_data.get('category', ''),
            'organization': api_data.get('organization', ''),
            'mobile_number': api_data.get('mobile_number', ''),
            'whatsapp_number': api_data.get('whatsapp_number', ''),
            'address': api_data.get('address', ''),
            'jamaat': api_data.get('jamaat', ''),
            'jamiaat': api_data.get('jamiaat', ''),
            'nationality': api_data.get('nationality', ''),
            'vatan': api_data.get('vatan', ''),
            'city': api_data.get('city', ''),
            'country': api_data.get('country', ''),
            'hifz_sanad': api_data.get('hifz_sanad', ''),
            'photograph': api_data.get('photograph', ''),
        }
    
    @classmethod
    def determine_user_role(cls, user_data: Dict) -> str:
        """
        Determine user role based on ITS data
        
        Logic:
        1. If occupation = "Doctor" -> role = "doctor"
        2. If category = "Amil" -> role = "aamil"
        3. If ITS ID in coordinator list -> role = "moze_coordinator"
        4. If ITS ID in student list -> role = "student"
        5. All others -> role = "patient"
        
        Args:
            user_data: ITS user data dictionary
            
        Returns:
            Role string for Django User model
        """
        its_id = user_data.get('its_id')
        occupation = user_data.get('occupation', '').lower()
        category = user_data.get('category', '').lower()
        
        # Check for admin (special case)
        if its_id == '50000001':
            return 'badri_mahal_admin'
        
        # 1. Check if doctor
        if occupation == 'doctor':
            return 'doctor'
        
        # 2. Check if Amil
        if category == 'amil':
            return 'aamil'
        
        # 3. Check if in coordinator list
        if its_id in cls.COORDINATOR_ITS_IDS:
            return 'moze_coordinator'
        
        # 4. Check if in student list
        if its_id in cls.STUDENT_ITS_IDS:
            return 'student'
        
        # 5. Default to patient
        return 'patient'
    
    @classmethod
    def validate_its_id(cls, its_id: str) -> bool:
        """Validate ITS ID format"""
        return its_id and len(its_id) == 8 and its_id.isdigit()
    
    @classmethod
    def search_users(cls, query: str, limit: int = 10) -> List[Dict]:
        """
        Search for ITS users (mock implementation)
        
        Args:
            query: Search query
            limit: Maximum results to return
            
        Returns:
            List of user data dictionaries
        """
        results = []
        
        # Generate some mock search results
        for i in range(min(limit, 5)):
            # Generate random ITS ID
            its_id = f"{random.randint(10000000, 99999999)}"
            user_data = cls.fetch_user_data(its_id)
            if user_data:
                # Check if name matches query
                full_name = f"{user_data['first_name']} {user_data['last_name']}".lower()
                if query.lower() in full_name or query in its_id:
                    results.append(user_data)
        
        return results
    
    @classmethod
    def bulk_fetch_users(cls, its_ids: List[str]) -> List[Dict]:
        """
        Fetch multiple users data at once
        
        Args:
            its_ids: List of ITS IDs
            
        Returns:
            List of user data dictionaries
        """
        results = []
        for its_id in its_ids:
            user_data = cls.fetch_user_data(its_id)
            if user_data:
                results.append(user_data)
        
        return results


# Create singleton instance
its_service = ITSService()

# For backward compatibility
MockITSService = ITSService
mock_its_service = its_service