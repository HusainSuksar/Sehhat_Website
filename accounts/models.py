from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


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
