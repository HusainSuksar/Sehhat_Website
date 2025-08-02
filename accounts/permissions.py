"""
Role-based permissions for Umoor Sehhat
Defines permissions for each user role
"""

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.conf import settings

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