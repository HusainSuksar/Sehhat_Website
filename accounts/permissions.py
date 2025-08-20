"""
Role-based permissions for Umoor Sehhat
Defines permissions for each user role
"""

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.conf import settings
from rest_framework import permissions

# Role-based permission definitions
ROLE_PERMISSIONS = {
    'aamil': {
        'moze': {
            'view': True,
            'add': False,
            'change': True,
            'delete': False,
        },
        'patient': {
            'view': True,
            'add': True,
            'change': True,
            'delete': False,
        },
        'appointment': {
            'view': True,
            'add': True,
            'change': True,
            'delete': False,
        },
        'medical_record': {
            'view': True,
            'add': False,
            'change': False,
            'delete': False,
        },
        'doctor': {
            'view': True,
            'add': False,
            'change': False,
            'delete': False,
        },
        'survey': {
            'view': True,
            'add': True,
            'change': True,
            'delete': False,
        },
        'evaluation': {
            'view': True,
            'add': True,
            'change': True,
            'delete': False,
        },
        'araz': {
            'view': True,
            'add': True,
            'change': True,
            'delete': False,
        },
        'report': {
            'view': True,
            'generate': True,
        },
        'coordinator': {
            'assign': True,
            'manage': True,
        }
    },
    
    'moze_coordinator': {
        'moze': {
            'view': True,
            'add': False,
            'change': True,
            'delete': False,
        },
        'patient': {
            'view': True,
            'add': True,
            'change': True,
            'delete': False,
        },
        'appointment': {
            'view': True,
            'add': True,
            'change': True,
            'delete': False,
        },
        'medical_record': {
            'view': True,
            'add': False,
            'change': False,
            'delete': False,
        },
        'doctor': {
            'view': True,
            'add': False,
            'change': False,
            'delete': False,
        },
        'survey': {
            'view': True,
            'add': True,
            'change': True,
            'delete': False,
        },
        'evaluation': {
            'view': True,
            'add': True,
            'change': True,
            'delete': False,
        },
        'araz': {
            'view': True,
            'add': True,
            'change': True,
            'delete': False,
        },
        'report': {
            'view': True,
            'generate': True,
        }
    },
    
    'doctor': {
        'own_profile': {
            'view': True,
            'change': True,
        },
        'patient': {
            'view': True,
            'add': True,
            'change': True,
            'delete': False,
        },
        'medical_record': {
            'view': True,
            'add': True,
            'change': True,
            'delete': False,
        },
        'appointment': {
            'view': True,
            'add': True,
            'change': True,
            'delete': False,
        },
        'prescription': {
            'view': True,
            'add': True,
            'change': True,
            'delete': False,
        },
        'lab_test': {
            'view': True,
            'add': True,
            'change': True,
            'delete': False,
        },
        'vital_signs': {
            'view': True,
            'add': True,
            'change': True,
            'delete': False,
        },
        'duty_schedule': {
            'view': True,
            'change': False,
        }
    },
    
    'student': {
        'own_profile': {
            'view': True,
            'change': True,
        },
        'course': {
            'view': True,
            'add': False,
            'change': False,
            'delete': False,
        },
        'grade': {
            'view': True,
            'add': False,
            'change': False,
            'delete': False,
        },
        'survey': {
            'view': True,
            'add': True,
            'change': False,
            'delete': False,
        },
        'evaluation': {
            'view': True,
            'add': True,
            'change': False,
            'delete': False,
        }
    },
    
    'badri_mahal_admin': {
        'all': {
            'view': True,
            'add': True,
            'change': True,
            'delete': True,
        }
    }
}


def get_user_permissions(user):
    """
    Get permissions for a specific user based on their role
    """
    if not user.is_authenticated:
        return {}
    
    role = user.role
    if role not in ROLE_PERMISSIONS:
        return {}
    
    return ROLE_PERMISSIONS[role]


def can_user_access(user, model_name, action):
    """
    Check if user can perform action on model
    """
    if not user.is_authenticated:
        return False
    
    # Admin has all permissions
    if user.is_admin:
        return True
    
    role = user.role
    if role not in ROLE_PERMISSIONS:
        return False
    
    permissions = ROLE_PERMISSIONS[role]
    
    # Check if model exists in permissions
    if model_name not in permissions:
        return False
    
    # Check if action is allowed
    return permissions[model_name].get(action, False)


def get_moze_data_for_user(user):
    """
    Get Moze data that user has access to
    """
    if not user.is_authenticated:
        return None
    
    if user.is_admin:
        # Admin can see all Mozes
        from moze.models import Moze
        return Moze.objects.all()
    
    elif user.is_aamil:
        # Aamil can see their managed Mozes
        return user.managed_mozes.all()
    
    elif user.is_moze_coordinator:
        # Coordinator can see their coordinated Mozes
        return user.coordinated_mozes.all()
    
    elif user.is_doctor:
        # Doctor can see Mozes where they have appointments
        from mahalshifa.models import Appointment
        moze_ids = Appointment.objects.filter(
            doctor__user=user
        ).values_list('moze_id', flat=True).distinct()
        from moze.models import Moze
        return Moze.objects.filter(id__in=moze_ids)
    
    return None


def get_patient_data_for_user(user):
    """
    Get patient data that user has access to
    """
    if not user.is_authenticated:
        return None
    
    from mahalshifa.models import Patient
    
    if user.is_admin:
        # Admin can see all patients
        return Patient.objects.all()
    
    elif user.is_aamil or user.is_moze_coordinator:
        # Aamil/Coordinator can see patients in their Mozes
        mozes = get_moze_data_for_user(user)
        if mozes:
            return Patient.objects.filter(registered_moze__in=mozes)
    
    elif user.is_doctor:
        # Doctor can see their patients
        return Patient.objects.filter(
            appointments__doctor__user=user
        ).distinct()
    
    return None


def get_medical_records_for_user(user):
    """
    Get medical records that user has access to
    """
    if not user.is_authenticated:
        return None
    
    from mahalshifa.models import MedicalRecord
    
    if user.is_admin:
        # Admin can see all medical records
        return MedicalRecord.objects.all()
    
    elif user.is_doctor:
        # Doctor can see their medical records
        return MedicalRecord.objects.filter(doctor__user=user)
    
    elif user.is_aamil or user.is_moze_coordinator:
        # Aamil/Coordinator can view medical records in their Mozes
        mozes = get_moze_data_for_user(user)
        if mozes:
            return MedicalRecord.objects.filter(moze__in=mozes)
    
    return None


def get_appointments_for_user(user):
    """
    Get appointments that user has access to
    """
    if not user.is_authenticated:
        return None
    
    from mahalshifa.models import Appointment
    
    if user.is_admin:
        # Admin can see all appointments
        return Appointment.objects.all()
    
    elif user.is_doctor:
        # Doctor can see their appointments
        return Appointment.objects.filter(doctor__user=user)
    
    elif user.is_aamil or user.is_moze_coordinator:
        # Aamil/Coordinator can see appointments in their Mozes
        mozes = get_moze_data_for_user(user)
        if mozes:
            return Appointment.objects.filter(moze__in=mozes)
    
    return None


def can_user_edit_own_data(user, target_user):
    """
    Check if user can edit their own data
    """
    if not user.is_authenticated:
        return False
    
    # Users can always edit their own data
    if user == target_user:
        return True
    
    # Admin can edit any user's data
    if user.is_admin:
        return True
    
    return False


def can_user_manage_moze(user, moze):
    """
    Check if user can manage a specific Moze
    """
    if not user.is_authenticated:
        return False
    
    if user.is_admin:
        return True
    
    if user.is_aamil and moze in user.managed_mozes.all():
        return True
    
    if user.is_moze_coordinator and moze in user.coordinated_mozes.all():
        return True
    
    return False


# DRF Permission Classes
class IsDoctor(permissions.BasePermission):
    """
    Custom permission to only allow doctors to access certain views.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'is_doctor') and request.user.is_doctor


class IsPatient(permissions.BasePermission):
    """
    Custom permission to only allow patients to access certain views.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'is_patient') and request.user.is_patient


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    Assumes the model instance has an 'owner' or 'user' attribute.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the object.
        # Check for 'owner' attribute first, then 'user'
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'patient') and hasattr(obj.patient, 'user'):
            return obj.patient.user == request.user
        elif hasattr(obj, 'doctor') and hasattr(obj.doctor, 'user'):
            return obj.doctor.user == request.user
        
        return False