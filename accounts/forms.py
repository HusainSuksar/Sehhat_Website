from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.html import escape
import re
from .models import User, UserProfile
from .services import MockITSService


class CustomLoginForm(forms.Form):
    """Custom login form using ITS ID instead of username"""
    
    its_id = forms.CharField(
        max_length=8,
        min_length=8,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '8-digit ITS ID',
            'autofocus': True,
            'autocomplete': 'username',
            'inputmode': 'numeric',
            'pattern': '[0-9]{8}',
            'title': 'Enter your 8-digit ITS ID'
        }),
        validators=[
            RegexValidator(
                regex=r'^\d{8}$',
                message='ITS ID must be exactly 8 digits'
            )
        ],
        error_messages={
            'required': 'ITS ID is required',
            'max_length': 'ITS ID must be exactly 8 digits',
            'min_length': 'ITS ID must be exactly 8 digits',
        }
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'autocomplete': 'current-password'
        }),
        max_length=128,
        error_messages={
            'required': 'Password is required',
        }
    )
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.user_cache = None
    
    def clean_its_id(self):
        """Validate and clean ITS ID"""
        its_id = self.cleaned_data.get('its_id')
        if its_id:
            # Sanitize input
            its_id = escape(its_id.strip())
            
            # Additional validation
            if not its_id.isdigit():
                raise ValidationError('ITS ID must contain only numbers')
            
            if len(its_id) != 8:
                raise ValidationError('ITS ID must be exactly 8 digits')
                
        return its_id
    
    def clean_password(self):
        """Validate and clean password"""
        password = self.cleaned_data.get('password')
        if password:
            # Sanitize input
            password = password.strip()
            
            # Basic password validation
            if len(password) < 4:
                raise ValidationError('Password too short')
            
            if len(password) > 128:
                raise ValidationError('Password too long')
                
        return password
    
    def clean(self):
        """Validate the form and authenticate user"""
        cleaned_data = super().clean()
        its_id = cleaned_data.get('its_id')
        password = cleaned_data.get('password')
        
        if its_id and password:
            try:
                # Fetch user data from ITS API
                its_service = MockITSService()
                user_data = its_service.fetch_user_data(its_id)
                
                if not user_data:
                    raise ValidationError('Invalid ITS ID. Please check your credentials.')
                
                # Simple password validation (for mock system, we'll accept any password)
                if len(password.strip()) < 1:
                    raise ValidationError('Password is required.')
                
                # Get or create user (but don't save during form validation)
                try:
                    user = User.objects.get(its_id=its_id)
                    # User exists, update their data
                    user.first_name = user_data.get('first_name', user.first_name)
                    user.last_name = user_data.get('last_name', user.last_name)
                    user.email = user_data.get('email', user.email)
                    user.role = user_data.get('role', user.role)
                    # Don't save here - will save after successful authentication
                    
                except User.DoesNotExist:
                    # Create new user
                    user = User(
                        its_id=its_id,
                        username=its_id,
                        first_name=user_data.get('first_name', ''),
                        last_name=user_data.get('last_name', ''),
                        email=user_data.get('email', ''),
                        role=user_data.get('role', 'student'),
                        is_active=True
                    )
                    # Don't save here - will save after successful authentication
                
                # Store user data for later use
                self._user_data = user_data
                self._user_instance = user
                self._is_new_user = not user.pk
                
                # For authentication, we'll use a simple approach
                # Set a temporary password if needed
                if not user.pk or not user.has_usable_password():
                    user.set_password(password)
                
                # Now authenticate
                if user.pk:
                    # Existing user - try to authenticate
                    authenticated_user = authenticate(
                        self.request,
                        username=user.username,
                        password=password
                    )
                    if not authenticated_user:
                        # Password might have changed, update it
                        user.set_password(password)
                        user.save()
                        authenticated_user = authenticate(
                            self.request,
                            username=user.username,
                            password=password
                        )
                else:
                    # New user - save first then authenticate
                    user.save()
                    authenticated_user = authenticate(
                        self.request,
                        username=user.username,
                        password=password
                    )
                
                if authenticated_user and authenticated_user.is_active:
                    self.user_cache = authenticated_user
                    
                    # Now safely update user data and profile
                    self._post_auth_updates()
                else:
                    raise ValidationError('Authentication failed. Please try again.')
                    
            except ValidationError:
                raise
            except Exception as e:
                # Log the error for debugging
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Login error for ITS ID {its_id}: {e}")
                raise ValidationError('Authentication system error. Please try again.')
        
        return cleaned_data
    
    def _post_auth_updates(self):
        """Update user data and profile after successful authentication"""
        try:
            user = self.user_cache
            user_data = self._user_data
            
            # Update user fields if needed
            user.first_name = user_data.get('first_name', user.first_name)
            user.last_name = user_data.get('last_name', user.last_name)
            user.email = user_data.get('email', user.email)
            user.role = user_data.get('role', user.role)
            user.save()
            
            # Update or create user profile
            profile, created = UserProfile.objects.get_or_create(user=user)
            
            # Update profile with ITS data
            profile_fields = [
                'contact_number', 'address', 'date_of_birth', 'gender',
                'jamaat', 'jamiaat', 'moze', 'misaq_date', 'education_level',
                'occupation', 'emergency_contact_name', 'emergency_contact_number',
                'blood_group', 'medical_conditions', 'medications', 'allergies',
                'marital_status', 'spouse_name', 'number_of_children'
            ]
            
            for field in profile_fields:
                if field in user_data and user_data[field]:
                    setattr(profile, field, user_data[field])
            
            profile.save()
            
        except Exception as e:
            # Log error but don't break authentication
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error updating user data after authentication: {e}")
    
    def get_user(self):
        """Return the authenticated user"""
        return self.user_cache


class UserRegistrationForm(UserCreationForm):
    """User registration form"""
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )
    its_id = forms.CharField(
        max_length=8,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '8-digit ITS ID',
            'pattern': r'\d{8}',
            'title': 'Please enter exactly 8 digits'
        })
    )
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'its_id', 'role', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
        }
    
    def clean_its_id(self):
        its_id = self.cleaned_data.get('its_id')
        if its_id and User.objects.filter(its_id=its_id).exists():
            raise forms.ValidationError('This ITS ID is already registered.')
        return its_id
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already registered.')
        return email


class UserProfileForm(forms.ModelForm):
    """User profile editing form"""
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone_number', 
            'arabic_full_name', 'profile_photo', 'specialty', 'college', 'specialization'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'arabic_full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'specialty': forms.TextInput(attrs={'class': 'form-control'}),
            'college': forms.TextInput(attrs={'class': 'form-control'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
        }


class UserProfileExtraForm(forms.ModelForm):
    """Extended user profile form"""
    class Meta:
        model = UserProfile
        fields = [
            'bio', 'location', 'date_of_birth', 
            'emergency_contact', 'emergency_contact_name'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class UserEditForm(forms.ModelForm):
    """Admin form for editing users"""
    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email', 'its_id', 'role',
            'phone_number', 'arabic_full_name', 'age', 'specialty', 'college', 
            'specialization', 'is_active', 'is_staff'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'its_id': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'arabic_full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'specialty': forms.TextInput(attrs={'class': 'form-control'}),
            'college': forms.TextInput(attrs={'class': 'form-control'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ITSVerificationForm(forms.Form):
    """Form for ITS ID verification"""
    its_id = forms.CharField(
        max_length=8,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter 8-digit ITS ID',
            'pattern': r'\d{8}',
            'title': 'Please enter exactly 8 digits'
        })
    )
    
    def clean_its_id(self):
        its_id = self.cleaned_data.get('its_id')
        if its_id and len(its_id) != 8:
            raise forms.ValidationError('ITS ID must be exactly 8 digits.')
        if its_id and not its_id.isdigit():
            raise forms.ValidationError('ITS ID must contain only numbers.')
        return its_id


class BulkUserUploadForm(forms.Form):
    """Form for bulk user upload via CSV"""
    csv_file = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': '.csv'
        }),
        help_text='Upload a CSV file with user data'
    )
    default_role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text='Default role for users without specified role'
    )
    send_email_notifications = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text='Send email notifications to new users'
    )
    
    def clean_csv_file(self):
        csv_file = self.cleaned_data.get('csv_file')
        if csv_file:
            if not csv_file.name.endswith('.csv'):
                raise forms.ValidationError('Please upload a CSV file.')
            if csv_file.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError('File size should not exceed 5MB.')
        return csv_file