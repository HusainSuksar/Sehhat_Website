"""
Mock ITS API Service for simulating user data fetching
This will be replaced with actual ITS API integration
"""
import random
from datetime import datetime
from typing import Dict, Optional


class MockITSService:
    """Mock service to simulate ITS API responses"""
    
    # Sample data pools for generating realistic mock data
    PREFIXES = ['Mr', 'Mrs', 'Ms', 'Dr', 'Prof']
    OCCUPATIONS = ['Engineer', 'Doctor', 'Teacher', 'Business Owner', 'Accountant', 'Consultant']
    QUALIFICATIONS = ['Bachelor of Engineering', 'MBBS', 'Masters in Business Administration', 'PhD in Computer Science']
    IDARAS = ['Mumbai', 'Delhi', 'Karachi', 'Dubai', 'London', 'New York']
    CATEGORIES = ['Student', 'Professional', 'Business', 'Retired']
    ORGANIZATIONS = ['Tata Consultancy Services', 'Reliance Industries', 'Al-Jamea-tus-Saifiyah', 'Independent']
    JAMAATS = ['Mumbai Central', 'Delhi Shahdara', 'Karachi Saddar', 'Dubai Karama']
    NATIONALITIES = ['Indian', 'Pakistani', 'UAE', 'British', 'American']
    VATANS = ['Mumbai', 'Karachi', 'Ahmedabad', 'Dubai', 'London']
    CITIES = ['Mumbai', 'Delhi', 'Karachi', 'Dubai', 'London', 'New York']
    COUNTRIES = ['India', 'Pakistan', 'UAE', 'UK', 'USA']
    
    @classmethod
    def fetch_user_data(cls, its_id: str) -> Optional[Dict]:
        """
        Mock function to simulate fetching user data from ITS API
        
        Args:
            its_id: 8-digit ITS ID
            
        Returns:
            Dictionary containing all 21 ITS fields or None if not found
        """
        if not its_id or len(its_id) != 8 or not its_id.isdigit():
            return None
            
        # Simulate API delay (in real implementation, this would be an HTTP request)
        # Generate deterministic data based on ITS ID for consistency
        random.seed(int(its_id))
        
        # Generate mock data for all 21 fields
        first_name = random.choice(['Ahmed', 'Fatima', 'Mohammed', 'Aisha', 'Ali', 'Zainab', 'Hassan', 'Mariam'])
        last_name = random.choice(['Khan', 'Sheikh', 'Patel', 'Shaikh', 'Ahmed', 'Ali', 'Hussein', 'Abdulla'])
        
        mock_data = {
            # 1. ITS ID
            'its_id': its_id,
            
            # 2-3. Full Name & Arabic Full Name
            'first_name': first_name,
            'last_name': last_name,
            'arabic_full_name': f'{first_name} {last_name}',  # Simplified for mock
            
            # 4. Prefix
            'prefix': random.choice(cls.PREFIXES),
            
            # 5. Age, Gender
            'age': random.randint(18, 65),
            'gender': random.choice(['male', 'female']),
            
            # 6. Marital Status, Misaq
            'marital_status': random.choice(['single', 'married', 'divorced', 'widowed']),
            'misaq': f'Misaq {random.randint(1400, 1445)}H',
            
            # 7. Occupation
            'occupation': random.choice(cls.OCCUPATIONS),
            
            # 8. Qualification
            'qualification': random.choice(cls.QUALIFICATIONS),
            
            # 9. Idara
            'idara': random.choice(cls.IDARAS),
            
            # 10. Category
            'category': random.choice(cls.CATEGORIES),
            
            # 11. Organization
            'organization': random.choice(cls.ORGANIZATIONS),
            
            # 12. Email ID
            'email': f'{first_name.lower()}.{last_name.lower()}@example.com',
            
            # 13. Mobile No.
            'mobile_number': f'+91{random.randint(9000000000, 9999999999)}',
            
            # 14. WhatsApp No.
            'whatsapp_number': f'+91{random.randint(9000000000, 9999999999)}',
            
            # 15. Address
            'address': f'{random.randint(1, 999)} {random.choice(["Main Street", "Park Road", "Market Square"])}, {random.choice(cls.CITIES)}',
            
            # 16. Jamaat, Jamiaat
            'jamaat': random.choice(cls.JAMAATS),
            'jamiaat': random.choice(cls.JAMAATS) + ' Jamiaat',
            
            # 17. Nationality
            'nationality': random.choice(cls.NATIONALITIES),
            
            # 18. Vatan
            'vatan': random.choice(cls.VATANS),
            
            # 19. City, Country
            'city': random.choice(cls.CITIES),
            'country': random.choice(cls.COUNTRIES),
            
            # 20. Hifz Sanad
            'hifz_sanad': 'Complete' if random.choice([True, False]) else 'Partial',
            
            # 21. Photograph (URL to a placeholder image)
            'photograph': f'https://via.placeholder.com/150x150?text={first_name}',
            
            # Metadata
            'sync_timestamp': datetime.now().isoformat(),
            'data_source': 'mock_its_api'
        }
        
        return mock_data
    
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
        
        Args:
            user_data: ITS user data dictionary
            
        Returns:
            Role string for Django User model
        """
        qualification = user_data.get('qualification', '').lower()
        occupation = user_data.get('occupation', '').lower()
        category = user_data.get('category', '').lower()
        organization = user_data.get('organization', '').lower()
        
        # Role determination logic based on ITS data
        # Doctor roles
        if 'mbbs' in qualification or 'doctor' in occupation or 'md' in qualification:
            return 'doctor'
        
        # Admin roles (based on organization or category)
        if 'jamea' in organization.lower() or 'admin' in category:
            return 'badri_mahal_admin'
        
        # Aamil roles
        if 'aamil' in occupation or 'coordinator' in occupation:
            return 'aamil'
        
        # Student roles (default for most users)
        if 'student' in category or user_data.get('age', 0) < 30:
            return 'student'
        
        # Default fallback
        return 'student'

# Instance for easy importing
mock_its_service = MockITSService()