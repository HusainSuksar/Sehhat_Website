"""
ITS API Integration Service
This module handles communication with the ITS (Information Technology System) API
to fetch user data, photos, and team information.
"""

import requests
import logging
from typing import Dict, List, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class ITSAPIService:
    """Service class for ITS API integration"""
    
    def __init__(self):
        self.base_url = getattr(settings, 'ITS_API_BASE_URL', 'https://api.its.example.com')
        self.api_key = getattr(settings, 'ITS_API_KEY', None)
        self.timeout = getattr(settings, 'ITS_API_TIMEOUT', 30)
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make a request to the ITS API"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            url = f"{self.base_url}{endpoint}"
            response = requests.get(
                url, 
                params=params, 
                headers=headers, 
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"ITS API error: {response.status_code} - {response.text}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"ITS API request failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"ITS API unexpected error: {str(e)}")
            return None
    
    def fetch_user_data(self, its_id: str) -> Optional[Dict]:
        """
        Fetch user data from ITS API
        
        Args:
            its_id: The ITS ID of the user
            
        Returns:
            Dict containing user data or None if failed
        """
        return self._make_request('/api/users', {'its_id': its_id})
    
    def fetch_user_photo(self, its_id: str) -> Optional[str]:
        """
        Fetch user photo URL from ITS API
        
        Args:
            its_id: The ITS ID of the user
            
        Returns:
            Photo URL string or None if failed
        """
        data = self._make_request('/api/users/photo', {'its_id': its_id})
        return data.get('photo_url') if data else None
    
    def fetch_team_members(self, moze_id: str) -> Optional[List[Dict]]:
        """
        Fetch team members for a specific moze
        
        Args:
            moze_id: The moze identifier
            
        Returns:
            List of team member data or None if failed
        """
        return self._make_request('/api/teams', {'moze_id': moze_id})
    
    def fetch_team_photos(self, team_id: str) -> Optional[List[Dict]]:
        """
        Fetch team photos
        
        Args:
            team_id: The team identifier
            
        Returns:
            List of photo data or None if failed
        """
        return self._make_request('/api/teams/photos', {'team_id': team_id})
    
    def fetch_local_doctors(self, moze_id: str) -> Optional[List[Dict]]:
        """
        Fetch local doctors for a moze
        
        Args:
            moze_id: The moze identifier
            
        Returns:
            List of doctor data or None if failed
        """
        return self._make_request('/api/doctors', {'moze_id': moze_id})
    
    def fetch_moze_evaluations(self, moze_id: str) -> Optional[List[Dict]]:
        """
        Fetch moze evaluations
        
        Args:
            moze_id: The moze identifier
            
        Returns:
            List of evaluation data or None if failed
        """
        return self._make_request('/api/evaluations', {'moze_id': moze_id})


# Global instance
its_api = ITSAPIService()


def fetch_its_data(its_id: str) -> Optional[Dict]:
    """
    Convenience function to fetch ITS data
    
    Args:
        its_id: The ITS ID
        
    Returns:
        User data dictionary or None
    """
    return its_api.fetch_user_data(its_id)


def fetch_team_members(moze_id: str) -> Optional[List[Dict]]:
    """
    Convenience function to fetch team members
    
    Args:
        moze_id: The moze ID
        
    Returns:
        Team members list or None
    """
    return its_api.fetch_team_members(moze_id)


def fetch_user_photo(its_id: str) -> Optional[str]:
    """
    Convenience function to fetch user photo
    
    Args:
        its_id: The ITS ID
        
    Returns:
        Photo URL or None
    """
    return its_api.fetch_user_photo(its_id)


# Mock functions for development (remove when ITS API is available)
def mock_fetch_its_data(its_id: str) -> Dict:
    """Mock function for development - remove when ITS API is available"""
    return {
        'its_id': its_id,
        'name': f'Mock User {its_id}',
        'photo_url': None,
        'role': 'doctor',
        'contact_number': '+966 50 123 4567',
        'email': f'user{its_id}@example.com'
    }


def mock_fetch_team_members(moze_id: str) -> List[Dict]:
    """Mock function for development - remove when ITS API is available"""
    return [
        {
            'its_id': '12345678',
            'name': 'Dr. Ahmed Al-Mahdi',
            'category': 'medical',
            'photo_url': None,
            'contact_number': '+966 50 111 1111',
            'position': 'Medical Coordinator'
        },
        {
            'its_id': '87654321',
            'name': 'Fatima Ali',
            'category': 'sports',
            'photo_url': None,
            'contact_number': '+966 50 222 2222',
            'position': 'Sports Coordinator'
        }
    ]


def mock_fetch_user_photo(its_id: str) -> Optional[str]:
    """Mock function for development - remove when ITS API is available"""
    return None  # No photos in mock data