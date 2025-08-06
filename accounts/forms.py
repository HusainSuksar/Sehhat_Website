from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from .models import User, UserProfile

User = get_user_model()


class CustomLoginForm(AuthenticationForm):
    """Custom login form with ITS ID or username"""
    username = forms.CharField(
        label='Username or ITS ID',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username or ITS ID',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
    )
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        
        # Try to find user by ITS ID if username doesn't exist
        if username and not User.objects.filter(username=username).exists():
            user = User.objects.filter(its_id=username).first()
            if user:
                return user.username
        
        return username


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