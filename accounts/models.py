from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.core.validators import RegexValidator
from django.db.models.signals import post_save, post_delete, m2m_changed
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
    AuditLog.objects.create(
        user=user,
        action='login',
        object_type='User',
        object_id=str(user.pk),
        object_repr=str(user),
        extra_data={'ip': request.META.get('REMOTE_ADDR')}
    )

@receiver(user_logged_out)
def log_user_logout(sender, user, request, **kwargs):
    AuditLog.objects.create(
        user=user,
        action='logout',
        object_type='User',
        object_id=str(user.pk),
        object_repr=str(user),
        extra_data={'ip': request.META.get('REMOTE_ADDR')}
    )

@receiver(post_save, sender=User)
def log_user_save(sender, instance, created, **kwargs):
    AuditLog.objects.create(
        user=instance,
        action='create' if created else 'update',
        object_type='User',
        object_id=str(instance.pk),
        object_repr=str(instance),
        extra_data={}
    )

@receiver(post_delete, sender=User)
def log_user_delete(sender, instance, **kwargs):
    # Create audit log without user reference since user is being deleted
    # Set user to None to avoid referential integrity issues
    AuditLog.objects.create(
        user=None,  # User is being deleted, can't reference it
        action='delete',
        object_type='User',
        object_id=str(instance.pk) if instance.pk else 'unknown',
        object_repr=str(instance) if instance else 'Deleted User',
        extra_data={
            'deleted_user_username': getattr(instance, 'username', 'unknown'),
            'deleted_user_email': getattr(instance, 'email', 'unknown'),
            'deletion_timestamp': timezone.now().isoformat()
        }
    )

@receiver(m2m_changed, sender=User.groups.through)
def log_group_membership_change(sender, instance, action, pk_set, **kwargs):
    if action in ['post_add', 'post_remove', 'post_clear']:
        try:
            # Safely handle group names with proper error handling
            group_names = []
            if pk_set:
                for pk in pk_set:
                    try:
                        group = Group.objects.get(pk=pk)
                        group_names.append(group.name)
                    except Group.DoesNotExist:
                        group_names.append(f'Unknown Group (ID: {pk})')
            
            AuditLog.objects.create(
                user=instance,
                action='permission_change',
                object_type='User',
                object_id=str(instance.pk) if instance.pk else 'unknown',
                object_repr=str(instance) if instance else 'Unknown User',
                extra_data={
                    'groups': group_names,
                    'action': action
                }
            )
        except Exception as e:
            # Log the error but don't break the signal
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error logging group membership change: {e}")

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
