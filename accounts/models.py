from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models, transaction
from django.core.validators import RegexValidator
from django.db.models.signals import post_save, post_delete, m2m_changed, pre_save
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone


class User(AbstractUser):
    """Custom User model extending AbstractUser with role-based access and ITS integration"""
    
    ROLE_CHOICES = [
        ('aamil', 'Aamil'),
        ('moze_coordinator', 'Moze Coordinator'),
        ('doctor', 'Doctor'),
        ('student', 'Student'),
        ('patient', 'Patient'),
        ('badri_mahal_admin', 'Badri Mahal Admin'),
    ]
    
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    
    MARITAL_STATUS_CHOICES = [
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
    ]
    
    # Core fields
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    
    # ITS API Fields (21 fields total)
    # 1. ITS ID
    its_id = models.CharField(
        max_length=8, 
        unique=True, 
        null=True, 
        blank=True,
        validators=[RegexValidator(
            regex=r'^\d{8}$',
            message='ITS ID must be exactly 8 digits',
            code='invalid_its_id'
        )],
        help_text='8-digit ITS ID'
    )
    
    # 2-3. Full Name & Arabic Full Name (first_name, last_name inherited from AbstractUser)
    arabic_full_name = models.CharField(max_length=200, blank=True, null=True, help_text='Arabic Full Name')
    
    # 4. Prefix
    prefix = models.CharField(max_length=20, blank=True, null=True, help_text='Title prefix (Mr, Mrs, Dr, etc.)')
    
    # 5. Age, Gender
    age = models.PositiveIntegerField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    
    # 6. Marital Status, Misaq
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES, blank=True, null=True)
    misaq = models.CharField(max_length=100, blank=True, null=True, help_text='Misaq information')
    
    # 7. Occupation
    occupation = models.CharField(max_length=100, blank=True, null=True)
    
    # 8. Qualification
    qualification = models.CharField(max_length=200, blank=True, null=True)
    
    # 9. Idara
    idara = models.CharField(max_length=100, blank=True, null=True, help_text='Administrative division')
    
    # 10. Category
    category = models.CharField(max_length=50, blank=True, null=True)
    
    # 11. Organization
    organization = models.CharField(max_length=200, blank=True, null=True)
    
    # 12. Email ID (email inherited from AbstractUser)
    
    # 13. Mobile No.
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    
    # 14. WhatsApp No.
    whatsapp_number = models.CharField(max_length=15, blank=True, null=True)
    
    # 15. Address
    address = models.TextField(blank=True, null=True)
    
    # 16. Jamaat, Jamiaat
    jamaat = models.CharField(max_length=100, blank=True, null=True)
    jamiaat = models.CharField(max_length=100, blank=True, null=True)
    
    # 17. Nationality
    nationality = models.CharField(max_length=50, blank=True, null=True)
    
    # 18. Vatan
    vatan = models.CharField(max_length=100, blank=True, null=True, help_text='Original homeland')
    
    # 19. City, Country
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    
    # 20. Hifz Sanad
    hifz_sanad = models.CharField(max_length=100, blank=True, null=True, help_text='Quran memorization certificate')
    
    # 21. Photograph
    photograph = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    
    # Additional existing fields
    phone_number = models.CharField(max_length=15, blank=True, null=True)  # Keeping for backward compatibility
    profile_photo = models.URLField(blank=True, null=True)  # Keeping for backward compatibility
    verified_certificate = models.FileField(upload_to='certificates/', blank=True, null=True)
    specialty = models.CharField(max_length=100, blank=True, null=True)
    college = models.CharField(max_length=100, blank=True, null=True)  # For students
    specialization = models.CharField(max_length=100, blank=True, null=True)  # For students
    
    # ITS sync metadata
    its_last_sync = models.DateTimeField(blank=True, null=True, help_text='Last time data was synced from ITS API')
    its_sync_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('synced', 'Synced'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    def get_full_name(self):
        if self.arabic_full_name:
            return self.arabic_full_name
        return super().get_full_name() or self.username
    
    @property
    def is_aamil(self):
        return self.role == 'aamil'
    
    @property
    def is_moze_coordinator(self):
        return self.role == 'moze_coordinator'
    
    @property
    def is_doctor(self):
        return self.role == 'doctor'
    
    @property
    def is_student(self):
        return self.role == 'student'
    
    @property
    def is_patient(self):
        return self.role == 'patient'
    
    @property
    def is_admin(self):
        return self.role == 'badri_mahal_admin' or self.is_superuser
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['first_name', 'last_name']


class UserProfile(models.Model):
    """Extended profile information for users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    emergency_contact = models.CharField(max_length=15, blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Profile of {self.user.get_full_name()}"
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'


class AuditLog(models.Model):
    """General-purpose audit log for tracking user actions"""
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('permission_change', 'Permission Change'),
        ('other', 'Other'),
    ]
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    action = models.CharField(max_length=32, choices=ACTION_CHOICES)
    object_type = models.CharField(max_length=64, blank=True, null=True)
    object_id = models.CharField(max_length=64, blank=True, null=True)
    object_repr = models.CharField(max_length=256, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    extra_data = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'

    def __str__(self):
        return f"{self.user} {self.action} {self.object_type} {self.object_id} at {self.timestamp}"


@receiver(user_logged_in)
def log_user_login(sender, user, request, **kwargs):
    """Log user login with atomic transaction and error handling"""
    try:
        with transaction.atomic():
            # Safely get IP address
            ip_address = 'unknown'
            if request and hasattr(request, 'META'):
                ip_address = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
                if not ip_address:
                    ip_address = request.META.get('REMOTE_ADDR', 'unknown')
            
            AuditLog.objects.create(
                user=user,
                action='login',
                object_type='User',
                object_id=str(user.pk),
                object_repr=str(user),
                extra_data={
                    'ip': ip_address,
                    'user_agent': request.META.get('HTTP_USER_AGENT', '')[:500] if request else '',
                    'timestamp': timezone.now().isoformat()
                }
            )
    except Exception as e:
        # Log the error but don't break the login process
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to log user login for user {user.pk}: {e}")

@receiver(user_logged_out)
def log_user_logout(sender, user, request, **kwargs):
    """Log user logout with atomic transaction and error handling"""
    try:
        with transaction.atomic():
            # Handle case where user might be None
            if not user:
                return
            
            # Safely get IP address
            ip_address = 'unknown'
            if request and hasattr(request, 'META'):
                ip_address = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
                if not ip_address:
                    ip_address = request.META.get('REMOTE_ADDR', 'unknown')
            
            AuditLog.objects.create(
                user=user,
                action='logout',
                object_type='User',
                object_id=str(user.pk),
                object_repr=str(user),
                extra_data={
                    'ip': ip_address,
                    'timestamp': timezone.now().isoformat()
                }
            )
    except Exception as e:
        # Log the error but don't break the logout process
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to log user logout for user {user.pk if user else 'None'}: {e}")

@receiver(post_save, sender=User)
def log_user_save(sender, instance, created, **kwargs):
    """Log user creation/update with atomic transaction and duplicate prevention"""
    try:
        # Prevent recursive signal calls during signal handling
        if hasattr(instance, '_signal_processing'):
            return
        
        with transaction.atomic():
            instance._signal_processing = True
            
            # Prepare audit data
            action = 'create' if created else 'update'
            extra_data = {
                'timestamp': timezone.now().isoformat(),
                'role': getattr(instance, 'role', 'unknown'),
                'is_active': getattr(instance, 'is_active', False),
            }
            
            # Add change tracking for updates
            if not created and hasattr(instance, '_old_values'):
                changed_fields = []
                for field, old_value in instance._old_values.items():
                    new_value = getattr(instance, field, None)
                    if old_value != new_value:
                        changed_fields.append({
                            'field': field,
                            'old_value': str(old_value)[:100],
                            'new_value': str(new_value)[:100]
                        })
                extra_data['changed_fields'] = changed_fields
            
            AuditLog.objects.create(
                user=instance,
                action=action,
                object_type='User',
                object_id=str(instance.pk),
                object_repr=str(instance)[:256],  # Limit length
                extra_data=extra_data
            )
            
            # Create user profile if it doesn't exist
            if created:
                UserProfile.objects.get_or_create(user=instance)
            
            # Clean up flag
            delattr(instance, '_signal_processing')
            
    except Exception as e:
        # Clean up flag on error
        if hasattr(instance, '_signal_processing'):
            delattr(instance, '_signal_processing')
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to log user save for user {instance.pk}: {e}")

@receiver(post_delete, sender=User)
def log_user_delete(sender, instance, **kwargs):
    """Log user deletion with atomic transaction and safe handling"""
    try:
        with transaction.atomic():
            # Create audit log without user reference since user is being deleted
            AuditLog.objects.create(
                user=None,  # User is being deleted, can't reference it
                action='delete',
                object_type='User',
                object_id=str(instance.pk) if instance.pk else 'unknown',
                object_repr=str(instance)[:256] if instance else 'Deleted User',
                extra_data={
                    'deleted_user_username': getattr(instance, 'username', 'unknown'),
                    'deleted_user_email': getattr(instance, 'email', 'unknown'),
                    'deleted_user_role': getattr(instance, 'role', 'unknown'),
                    'deletion_timestamp': timezone.now().isoformat()
                }
            )
            
            # Clean up related data if needed
            # Note: Django CASCADE should handle most relationships
            
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to log user deletion for user {instance.pk if instance else 'unknown'}: {e}")

@receiver(m2m_changed, sender=User.groups.through)
def log_group_membership_change(sender, instance, action, pk_set, **kwargs):
    """Log group membership changes with atomic transaction and error handling"""
    if action not in ['post_add', 'post_remove', 'post_clear']:
        return
    
    try:
        with transaction.atomic():
            # Safely handle group names with proper error handling
            group_names = []
            if pk_set:
                # Use select_related to optimize queries
                groups = Group.objects.filter(pk__in=pk_set)
                group_names = [group.name for group in groups]
            
            AuditLog.objects.create(
                user=instance,
                action=f'group_{action.replace("post_", "")}',
                object_type='UserGroups',
                object_id=str(instance.pk),
                object_repr=f"{instance.username} group membership",
                extra_data={
                    'action': action,
                    'groups': group_names,
                    'group_count': len(group_names),
                    'timestamp': timezone.now().isoformat()
                }
            )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to log group membership change for user {instance.pk}: {e}")

@receiver(m2m_changed, sender=User.user_permissions.through)
def log_user_permission_change(sender, instance, action, pk_set, **kwargs):
    if action in ['post_add', 'post_remove', 'post_clear']:
        try:
            # Safely handle permission names with proper error handling
            permission_names = []
            if pk_set:
                for pk in pk_set:
                    try:
                        permission = Permission.objects.get(pk=pk)
                        permission_names.append(permission.codename)
                    except Permission.DoesNotExist:
                        permission_names.append(f'Unknown Permission (ID: {pk})')
            
            AuditLog.objects.create(
                user=instance,
                action='permission_change',
                object_type='User',
                object_id=str(instance.pk) if instance.pk else 'unknown',
                object_repr=str(instance) if instance else 'Unknown User',
                extra_data={
                    'permissions': permission_names,
                    'action': action
                }
            )
        except Exception as e:
            # Log the error but don't break the signal
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error logging user permission change: {e}")

@receiver(pre_save, sender=User)
def track_user_changes(sender, instance, **kwargs):
    """Track changes to user fields before saving"""
    try:
        if instance.pk:  # Only for existing instances
            try:
                old_instance = User.objects.get(pk=instance.pk)
                instance._old_values = {
                    'username': old_instance.username,
                    'email': old_instance.email,
                    'first_name': old_instance.first_name,
                    'last_name': old_instance.last_name,
                    'role': old_instance.role,
                    'is_active': old_instance.is_active,
                    'is_staff': old_instance.is_staff,
                    'is_superuser': old_instance.is_superuser,
                }
            except User.DoesNotExist:
                # Instance was deleted between operations
                pass
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to track user changes for user {instance.pk}: {e}")
