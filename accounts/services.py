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
        Fetch user data from ITS API (or generate mock data)
        
        Args:
            its_id: 8-digit ITS ID
            
        Returns:
            Dictionary containing all ITS fields or None if invalid
        """
        # Validate ITS ID format
        if not its_id or len(its_id) != 8 or not its_id.isdigit():
            return None
        
        # Convert to int for seed generation
        its_id_int = int(its_id)
        
        # More strict validation - only allow specific ranges for mock data
        # This prevents completely random ITS IDs from working
        if not (
            (10000000 <= its_id_int <= 99999999) and  # Valid 8-digit range
            (its_id_int % 7 == 0 or its_id_int % 11 == 0 or its_id_int % 13 == 0)  # Additional validation
        ):
            # Only allow some specific patterns to simulate real ITS validation
            return None
        
        # Use ITS ID as seed for consistent data generation
        random.seed(its_id_int)
        
        # Generate basic data
        first_name = random.choice(cls.FIRST_NAMES)
        last_name = random.choice(cls.LAST_NAMES)
        full_name = f"{first_name} {last_name}"
        arabic_full_name = f"عربي {full_name}"
        
        # Determine occupation and category for role assignment
        rand_num = random.random()
        
        if rand_num < 0.05:  # 5% doctors
            occupation = "Doctor"
            category = "Professional"
            qualification = "MBBS, MD"
            prefix = "Dr."
        elif rand_num < 0.10:  # 5% Amils
            occupation = "Religious Affairs"
            category = "Amil"  # This will trigger aamil role
            qualification = "Alim, Hafiz"
            prefix = "Janab"
        else:  # 90% general population
            occupation = random.choice(cls.OCCUPATIONS)
            category = random.choice(cls.CATEGORIES)
            qualification = random.choice(cls.QUALIFICATIONS)
            prefix = "Mr." if random.choice(['M', 'F']) == 'M' else "Ms."
        
        # Generate other fields
        age = random.randint(18, 65)
        gender = random.choice(['male', 'female'])
        marital_status = random.choice(['single', 'married', 'divorced', 'widowed'])
        
        # Contact information
        mobile = f"+91{random.randint(7000000000, 9999999999)}"
        whatsapp = mobile if random.random() > 0.3 else f"+91{random.randint(7000000000, 9999999999)}"
        email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 99)}@example.com"
        
        # Location information
        city = random.choice(cls.CITIES)
        country = random.choice(cls.COUNTRIES)
        address = f"{random.randint(1, 999)} {random.choice(['Street', 'Road', 'Avenue', 'Lane'])}, {city}"
        
        # Other fields
        jamaat = random.choice(cls.JAMAATS)
        moze = random.choice(cls.MOZE_NAMES)
        nationality = random.choice(cls.NATIONALITIES)
        vatan = random.choice(cls.CITIES)
        idara = random.choice(cls.IDARAS)
        organization = random.choice(cls.ORGANIZATIONS)
        
        # Misaq information
        misaq = f"Misaq-{random.randint(1000, 9999)}"
        hifz_sanad = f"HS-{random.randint(1000, 9999)}" if random.random() > 0.7 else ""
        
        # Reset random seed
        random.seed()
        
        return {
            # 21 ITS API fields
            'its_id': its_id,
            'arabic_full_name': arabic_full_name,
            'prefix': prefix,
            'first_name': first_name,
            'last_name': last_name,
            'age': age,
            'gender': gender,
            'marital_status': marital_status,
            'misaq': misaq,
            'occupation': occupation,
            'qualification': qualification,
            'idara': idara,
            'category': category,
            'organization': organization,
            'email': email,
            'mobile_number': mobile,
            'whatsapp_number': whatsapp,
            'address': address,
            'jamaat': jamaat,
            'jamiaat': f"{jamaat} Jamiaat",
            'nationality': nationality,
            'vatan': vatan,
            'city': city,
            'country': country,
            'hifz_sanad': hifz_sanad,
            'photograph': f"https://api.dicebear.com/7.x/avataaars/svg?seed={its_id}"
        }
    
    @classmethod
    def authenticate_user(cls, its_id: str, password: str) -> Optional[Dict]:
        """
        Authenticate user against ITS API
        
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
        
        # Mock password validation
        # In production, this would call actual ITS API
        if not password or len(password) < 4:
            logger.warning(f"Invalid password for ITS ID: {its_id}")
            return None
        
        # Fetch user data
        user_data = cls.fetch_user_data(its_id)
        if not user_data:
            logger.error(f"Failed to fetch user data for ITS ID: {its_id}")
            return None
        
        # Determine user role based on ITS data
        role = cls.determine_user_role(user_data)
        
        logger.info(f"User {its_id} authenticated successfully with role: {role}")
        
        # Return authentication result
        return {
            'authenticated': True,
            'user_data': user_data,
            'role': role,
            'login_timestamp': datetime.now().isoformat(),
            'auth_source': 'its_api'
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