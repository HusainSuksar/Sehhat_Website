"""
Mock ITS API Service for simulating user data fetching
This will be replaced with actual ITS API integration
"""
import random
from datetime import datetime
from typing import Dict, Optional, List


# Generate 50 moze names - defined outside class
MOZE_NAMES = [f"Moze {chr(65 + i // 2)}{i % 2 + 1}" for i in range(50)]  # A1, A2, B1, B2, etc.

class MockITSService:
    """
    Mock ITS Service for development and testing.
    Now accepts ANY valid 8-digit ITS ID and generates realistic data.
    
    Special predefined users:
    - 50000001: Admin User (badri_mahal_admin)
    - 50000002-51: 50 Aamils (1 per moze) 
    - 50000052-61: 10 Moze Coordinators
    - 50000062-81: 20 Doctors
    - 50000082-100: 19 Students
    
    For any other valid 8-digit ITS ID: Generates realistic student data
    """
    
    # Use the global MOZE_NAMES
    MOZE_NAMES = MOZE_NAMES
    
    # Predefined special users (for consistency)
    PREDEFINED_USERS = {
        # 1 Admin User
        '50000001': {'role': 'badri_mahal_admin', 'name': 'Admin', 'surname': 'User', 'moze': 'Central Administration'},
        
        # 50 Aamils (1 per moze) - IDs: 50000002 to 50000051
        **{
            f'500000{str(i+2).zfill(2)}': {
                'role': 'aamil',
                'name': f'Aamil{i+1}',
                'surname': f'Khan{i+1}',
                'moze': MOZE_NAMES[i]
            } for i in range(50)
        },
        
        # 10 Moze Coordinators - IDs: 50000052 to 50000061
        **{
            f'500000{str(i+52).zfill(2)}': {
                'role': 'moze_coordinator',
                'name': f'Coordinator{i+1}',
                'surname': f'Ahmed{i+1}',
                'moze': MOZE_NAMES[i * 5]  # Distribute across moze
            } for i in range(10)
        },
        
        # 20 Doctors - IDs: 50000062 to 50000081
        **{
            f'500000{str(i+62).zfill(2)}': {
                'role': 'doctor',
                'name': f'Dr{i+1}',
                'surname': f'Shaikh{i+1}',
                'moze': MOZE_NAMES[i % 50]  # Distribute across moze
            } for i in range(20)
        },
        
        # 19 Students - IDs: 50000082 to 50000100
        **{
            f'50000{str(i+82).zfill(3)}': {
                'role': 'student',
                'name': f'Student{i+1}',
                'surname': f'Ali{i+1}',
                'moze': MOZE_NAMES[i % 50]  # Distribute across moze
            } for i in range(19)
        }
    }
    
    # Sample data pools for generating realistic mock data
    FIRST_NAMES = [
        'Mohammed', 'Ahmed', 'Ali', 'Hassan', 'Hussein', 'Fatima', 'Zainab', 'Khadija', 
        'Aisha', 'Mariam', 'Omar', 'Yusuf', 'Ibrahim', 'Ismail', 'Mustafa', 'Amina',
        'Safiya', 'Ruqayyah', 'Zahra', 'Maryam', 'Abdullah', 'Abdul Rahman', 'Khalid',
        'Bilal', 'Hamza', 'Umar', 'Uthman', 'Salman', 'Noor', 'Hanan'
    ]
    
    LAST_NAMES = [
        'Khan', 'Ali', 'Ahmed', 'Sheikh', 'Malik', 'Shah', 'Hussain', 'Qureshi',
        'Syed', 'Ansari', 'Shaikh', 'Patel', 'Merchant', 'Contractor', 'Engineer',
        'Doctor', 'Professor', 'Saifuddin', 'Najmuddin', 'Burhanuddin'
    ]
    
    OCCUPATIONS = ['Student', 'Engineer', 'Doctor', 'Teacher', 'Business Owner', 'Accountant', 'Consultant', 'Professional']
    QUALIFICATIONS = ['Bachelor of Science', 'Bachelor of Engineering', 'Bachelor of Commerce', 'MBBS', 'MBA', 'Masters', 'PhD']
    IDARAS = ['Mumbai', 'Delhi', 'Karachi', 'Dubai', 'London', 'New York', 'Ahmedabad', 'Pune', 'Bangalore']
    ORGANIZATIONS = ['Student', 'TCS', 'Infosys', 'Reliance', 'Al-Jamea-tus-Saifiyah', 'Independent', 'Government']
    JAMAATS = ['Mumbai Central', 'Delhi Shahdara', 'Karachi Saddar', 'Dubai Karama', 'London Northolt', 'Ahmedabad']
    NATIONALITIES = ['Indian', 'Pakistani', 'UAE', 'British', 'American', 'Canadian']
    VATANS = ['Mumbai', 'Karachi', 'Ahmedabad', 'Dubai', 'London', 'New York', 'Delhi', 'Bangalore']
    CITIES = ['Mumbai', 'Delhi', 'Karachi', 'Dubai', 'London', 'New York', 'Ahmedabad', 'Pune', 'Bangalore']
    COUNTRIES = ['India', 'Pakistan', 'UAE', 'UK', 'USA', 'Canada']
    
    @classmethod
    def fetch_user_data(cls, its_id: str) -> Optional[Dict]:
        """
        Mock function to simulate fetching user data from ITS API
        Now accepts ANY valid 8-digit ITS ID and generates realistic data
        
        Args:
            its_id: 8-digit ITS ID
            
        Returns:
            Dictionary containing all 21 ITS fields or None if invalid format
        """
        # Validate ITS ID format
        if not its_id or len(its_id) != 8 or not its_id.isdigit():
            return None
        
        # Convert to int for seed generation
        its_id_int = int(its_id)
        
        # Use ITS ID as seed for consistent data generation
        random.seed(its_id_int)
        
        # Check if this is a predefined user
        if its_id in cls.PREDEFINED_USERS:
            user_info = cls.PREDEFINED_USERS[its_id]
            first_name = user_info['name']
            last_name = user_info['surname']
            role = user_info['role']
            moze = user_info.get('moze', 'General')
        else:
            # Generate data for any other valid ITS ID
            first_name = random.choice(cls.FIRST_NAMES)
            last_name = random.choice(cls.LAST_NAMES)
            role = 'student'  # Default role for non-predefined users
            moze = random.choice(cls.MOZE_NAMES)
        
        # Set occupation and qualification based on role
        if role == 'doctor':
            occupation = 'Doctor'
            qualification = 'MBBS'
        elif role == 'aamil':
            occupation = 'Aamil'
            qualification = 'Religious Affairs'
        elif role == 'moze_coordinator':
            occupation = 'Coordinator'
            qualification = 'Masters in Management'
        elif role == 'badri_mahal_admin':
            occupation = 'Administrator'
            qualification = 'Masters in Business Administration'
        else:  # student or default
            occupation = random.choice(cls.OCCUPATIONS)
            qualification = random.choice(cls.QUALIFICATIONS)
        
        # Generate consistent email
        email = f"{first_name.lower()}.{last_name.lower()}@example.com"
        
        # Generate other fields using the seeded random
        contact_number = f"+91{random.randint(6000000000, 9999999999)}"
        
        # Generate address
        city = random.choice(cls.CITIES)
        country = random.choice(cls.COUNTRIES)
        address = f"{random.randint(1, 999)} {random.choice(['Street', 'Road', 'Avenue'])}, {city}, {country}"
        
        # Generate date of birth (age between 18-65)
        birth_year = datetime.now().year - random.randint(18, 65)
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)  # Safe day for all months
        date_of_birth = f"{birth_year}-{birth_month:02d}-{birth_day:02d}"
        
        # Generate other fields
        gender = random.choice(['M', 'F'])
        jamaat = random.choice(cls.JAMAATS)
        jamiaat = random.choice(['Jamaat-e-Dawat', 'Al-Jamea-tus-Saifiyah', 'Local Jamaat'])
        
        # Misaq date (usually after 15-17 years old)
        misaq_year = birth_year + random.randint(15, 17)
        misaq_date = f"{misaq_year}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
        
        education_level = random.choice(['High School', 'Bachelors', 'Masters', 'PhD', 'Diploma'])
        
        emergency_contact_name = f"{random.choice(cls.FIRST_NAMES)} {random.choice(cls.LAST_NAMES)}"
        emergency_contact_number = f"+91{random.randint(6000000000, 9999999999)}"
        
        blood_group = random.choice(['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-'])
        medical_conditions = random.choice(['None', 'Diabetes', 'Hypertension', 'Asthma', 'Allergies'])
        medications = random.choice(['None', 'Insulin', 'Blood Pressure', 'Vitamins'])
        allergies = random.choice(['None', 'Peanuts', 'Shellfish', 'Dust', 'Pollen'])
        
        marital_status = random.choice(['Single', 'Married', 'Divorced', 'Widowed'])
        spouse_name = f"{random.choice(cls.FIRST_NAMES)} {random.choice(cls.LAST_NAMES)}" if marital_status == 'Married' else ""
        number_of_children = random.randint(0, 4) if marital_status == 'Married' else 0
        
        # Reset random seed to avoid affecting other operations
        random.seed()
        
        return {
            'its_id': its_id,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'contact_number': contact_number,
            'address': address,
            'date_of_birth': date_of_birth,
            'gender': gender,
            'jamaat': jamaat,
            'jamiaat': jamiaat,
            'moze': moze,
            'misaq_date': misaq_date,
            'education_level': education_level,
            'occupation': occupation,
            'emergency_contact_name': emergency_contact_name,
            'emergency_contact_number': emergency_contact_number,
            'blood_group': blood_group,
            'medical_conditions': medical_conditions,
            'medications': medications,
            'allergies': allergies,
            'marital_status': marital_status,
            'spouse_name': spouse_name,
            'number_of_children': number_of_children,
            'role': role
        }
    
    @classmethod
    def validate_its_id(cls, its_id: str) -> bool:
        """
        Validate ITS ID format
        
        Args:
            its_id: ITS ID to validate
            
        Returns:
            True if valid, False otherwise
        """
        return its_id and len(its_id) == 8 and its_id.isdigit()
    
    @classmethod
    def search_users(cls, query: str, limit: int = 10) -> list:
        """
        Mock search functionality for ITS users
        
        Args:
            query: Search query
            limit: Maximum results to return
            
        Returns:
            List of user data dictionaries
        """
        # Generate mock search results
        results = []
        for i in range(min(limit, 5)):  # Return max 5 mock results
            its_id = f'{random.randint(10000000, 99999999)}'
            user_data = cls.fetch_user_data(its_id)
            if user_data:
                results.append(user_data)
        
        return results

    @classmethod
    def authenticate_user(cls, its_id: str, password: str) -> Optional[Dict]:
        """
        Mock function to simulate ITS authentication
        In real implementation, this would validate credentials against ITS API
        
        Args:
            its_id: 8-digit ITS ID
            password: User's ITS password
            
        Returns:
            Authentication result with user data or None if invalid
        """
        # Validate ITS ID format first
        if not cls.validate_its_id(its_id):
            return None
        
        # Mock password validation (in real implementation, this would be sent to ITS API)
        # For demo purposes, we'll accept any password with specific rules
        if not password or len(password) < 4:
            return None
        
        # Fetch user data if authentication would succeed
        user_data = cls.fetch_user_data(its_id)
        if not user_data:
            return None
        
        # Determine user role based on ITS data
        # This is where you'd map ITS categories/qualifications to your app roles
        role = cls._determine_user_role(user_data)
        
        # Add authentication metadata
        auth_result = {
            'authenticated': True,
            'user_data': user_data,
            'role': role,
            'login_timestamp': datetime.now().isoformat(),
            'auth_source': 'its_api'
        }
        
        return auth_result
    
    @classmethod
    def _determine_user_role(cls, user_data: Dict) -> str:
        """
        Determine Django user role based on ITS data
        
        For Mock ITS, we use the explicit role from PREDEFINED_USERS.
        In a real ITS implementation, this would analyze ITS data fields.
        
        Args:
            user_data: ITS user data dictionary
            
        Returns:
            Role string for Django User model
        """
        its_id = user_data.get('its_id')
        
        # For Mock ITS: Use explicit role from PREDEFINED_USERS
        if its_id and its_id in cls.PREDEFINED_USERS:
            explicit_role = cls.PREDEFINED_USERS[its_id].get('role')
            if explicit_role:
                return explicit_role
        
        # Fallback logic for real ITS (analyze ITS data fields)
        # This part of the logic needs to be updated to reflect the new data structure
        # For now, it will return 'student' for all non-predefined users
        return 'student'

# Instance for easy importing
mock_its_service = MockITSService()