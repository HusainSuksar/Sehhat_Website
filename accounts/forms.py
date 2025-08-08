from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from .models import User, UserProfile

User = get_user_model()


class CustomLoginForm(forms.Form):
    """ITS-based login form - authenticates via ITS API only"""
    its_id = forms.CharField(
        label='ITS ID',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your ITS ID',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your ITS password'
        })
    )
    
    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        its_id = cleaned_data.get('its_id')
        password = cleaned_data.get('password')
        
        if its_id and password:
            from .services import MockITSService
            
            # Authenticate with ITS API
            auth_result = MockITSService.authenticate_user(its_id, password)
            
            if not auth_result or not auth_result.get('authenticated'):
                raise forms.ValidationError('Invalid ITS credentials. Please check your ITS ID and password.')
            
            # Get or create Django user with ITS data
            user_data = auth_result['user_data']
            role = auth_result['role']
            
            # Create or update Django user
            user, created = User.objects.get_or_create(
                its_id=its_id,
                defaults={
                    'username': user_data['email'],
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'arabic_full_name': user_data['arabic_full_name'],
                    'prefix': user_data['prefix'],
                    'age': user_data['age'],
                    'gender': user_data['gender'],
                    'marital_status': user_data['marital_status'],
                    'misaq': user_data['misaq'],
                    'occupation': user_data['occupation'],
                    'qualification': user_data['qualification'],
                    'idara': user_data['idara'],
                    'category': user_data['category'],
                    'organization': user_data['organization'],
                    'mobile_number': user_data['mobile_number'],
                    'whatsapp_number': user_data['whatsapp_number'],
                    'address': user_data['address'],
                    'jamaat': user_data['jamaat'],
                    'jamiaat': user_data['jamiaat'],
                    'nationality': user_data['nationality'],
                    'vatan': user_data['vatan'],
                    'city': user_data['city'],
                    'country': user_data['country'],
                    'hifz_sanad': user_data['hifz_sanad'],
                    'profile_photo': user_data['photograph'],
                    'role': role,
                    'is_active': True,
                }
            )
            
            # Update existing user data with fresh ITS data (sync ALL fields)
            if not created:
                user.first_name = user_data['first_name']
                user.last_name = user_data['last_name']
                user.email = user_data['email']
                user.arabic_full_name = user_data['arabic_full_name']
                user.prefix = user_data['prefix']
                user.age = user_data['age']
                user.gender = user_data['gender']
                user.marital_status = user_data['marital_status']
                user.misaq = user_data['misaq']
                user.occupation = user_data['occupation']
                user.qualification = user_data['qualification']
                user.idara = user_data['idara']
                user.category = user_data['category']
                user.organization = user_data['organization']
                user.mobile_number = user_data['mobile_number']
                user.whatsapp_number = user_data['whatsapp_number']
                user.address = user_data['address']
                user.jamaat = user_data['jamaat']
                user.jamiaat = user_data['jamiaat']
                user.nationality = user_data['nationality']
                user.vatan = user_data['vatan']
                user.city = user_data['city']
                user.country = user_data['country']
                user.hifz_sanad = user_data['hifz_sanad']
                user.profile_photo = user_data['photograph']
                user.role = role
                from django.utils import timezone
                user.its_last_sync = timezone.now()
                user.save()
            
            self.user_cache = user
        
        return cleaned_data
    
    def get_user(self):
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