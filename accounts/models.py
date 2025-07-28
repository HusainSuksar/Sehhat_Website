from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.db.models.signals import post_save, post_delete
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver


class User(AbstractUser):
    """Custom User model extending AbstractUser with role-based access"""
    
    ROLE_CHOICES = [
        ('aamil', 'Aamil'),
        ('moze_coordinator', 'Moze Coordinator'),
        ('doctor', 'Doctor'),
        ('student', 'Student'),
        ('badri_mahal_admin', 'Badri Mahal Admin'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
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
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    arabic_name = models.CharField(max_length=100, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    verified_certificate = models.FileField(upload_to='certificates/', blank=True, null=True)
    specialty = models.CharField(max_length=100, blank=True, null=True)
    
    # Additional fields for different roles
    college = models.CharField(max_length=100, blank=True, null=True)  # For students
    specialization = models.CharField(max_length=100, blank=True, null=True)  # For students
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    def get_full_name(self):
        if self.arabic_name:
            return self.arabic_name
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
    AuditLog.objects.create(
        user=instance,
        action='delete',
        object_type='User',
        object_id=str(instance.pk),
        object_repr=str(instance),
        extra_data={}
    )
