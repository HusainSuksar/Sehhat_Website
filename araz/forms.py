from django import forms
from django.contrib.auth import get_user_model
from .models import (
    Petition, PetitionCategory, PetitionComment, PetitionAttachment,
    DuaAraz, ArazComment, ArazAttachment
)
from moze.models import Moze
from doctordirectory.models import Doctor

User = get_user_model()


class PetitionForm(forms.ModelForm):
    """Form for creating and editing petitions"""
    
    # ITS ID field for auto-populating user data
    its_id = forms.CharField(
        max_length=8,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter ITS ID to auto-fill details',
            'id': 'id_its_id',
            'pattern': '[0-9]{8}',
            'title': 'ITS ID must be exactly 8 digits',
            'maxlength': '8',
            'minlength': '8'
        }),
        help_text='Enter ITS ID to automatically fetch name, mobile, and email'
    )
    
    # Fields to display fetched ITS data
    petitioner_name = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Full name of petitioner',
            'id': 'id_petitioner_name',
            'maxlength': '200'
        }),
        help_text='Will be auto-filled from ITS ID or enter manually'
    )
    
    petitioner_mobile = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mobile number',
            'id': 'id_petitioner_mobile',
            'maxlength': '20',
            'pattern': '[+]?[0-9]{10,15}',
            'title': 'Enter a valid mobile number'
        }),
        help_text='Will be auto-filled from ITS ID or enter manually'
    )
    
    petitioner_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email address',
            'id': 'id_petitioner_email',
            'maxlength': '254'
        }),
        help_text='Will be auto-filled from ITS ID or enter manually'
    )
    
    class Meta:
        model = Petition
        fields = [
            'its_id', 'petitioner_name', 'petitioner_mobile', 'petitioner_email',
            'title', 'description', 'category', 'priority', 'moze', 'is_anonymous'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter a clear title for your petition',
                'maxlength': 200
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Provide detailed description of your petition...',
                'rows': 6
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-control'
            }),
            'moze': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_anonymous': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set active categories only
        self.fields['category'].queryset = PetitionCategory.objects.filter(is_active=True)
        
        # Pre-fill petitioner information with current user's data if available
        if user and not self.instance.pk:  # Only for new petitions
            if hasattr(user, 'its_id') and user.its_id:
                self.fields['its_id'].initial = user.its_id
            
            # Set petitioner name from user's full name
            full_name = user.get_full_name()
            if full_name and full_name.strip():
                self.fields['petitioner_name'].initial = full_name
            else:
                self.fields['petitioner_name'].initial = f"{user.first_name} {user.last_name}".strip()
            
            # Set mobile and email if available
            if hasattr(user, 'mobile_number') and user.mobile_number:
                self.fields['petitioner_mobile'].initial = user.mobile_number
            
            if user.email:
                self.fields['petitioner_email'].initial = user.email
        
        # Customize moze queryset based on user permissions
        if user:
            if user.is_admin:
                self.fields['moze'].queryset = Moze.objects.filter(is_active=True)
            else:
                self.fields['moze'].queryset = Moze.objects.filter(is_active=True)
    
    def clean_petitioner_name(self):
        """Validate petitioner name is not empty"""
        name = self.cleaned_data.get('petitioner_name')
        if not name or not name.strip():
            raise forms.ValidationError("Petitioner name is required.")
        return name.strip()
    
    def clean_its_id(self):
        """Validate ITS ID format if provided"""
        its_id = self.cleaned_data.get('its_id')
        if its_id and its_id.strip():
            its_id = its_id.strip()
            if len(its_id) != 8 or not its_id.isdigit():
                raise forms.ValidationError("ITS ID must be exactly 8 digits.")
        return its_id
    
    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()
        
        # If ITS ID is provided, try to validate against it
        its_id = cleaned_data.get('its_id')
        petitioner_name = cleaned_data.get('petitioner_name')
        
        if its_id and not petitioner_name:
            raise forms.ValidationError("Petitioner name is required when ITS ID is provided.")
        
        return cleaned_data


class PetitionCommentForm(forms.ModelForm):
    """Form for adding comments to petitions"""
    
    class Meta:
        model = PetitionComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Add your comment...',
                'rows': 3
            })
        }


class DuaArazForm(forms.ModelForm):
    """Form for Dua Araz (medical requests)"""
    
    class Meta:
        model = DuaAraz
        fields = [
            'patient_its_id', 'patient_name', 'patient_phone', 'patient_email',
            'ailment', 'symptoms', 'urgency_level', 'request_type',
            'previous_medical_history', 'current_medications', 'allergies',
            'preferred_doctor', 'preferred_location', 'preferred_time',
            'preferred_contact_method'
        ]
        widgets = {
            'patient_its_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '12345678',
                'pattern': '[0-9]{8}',
                'title': 'Please enter exactly 8 digits'
            }),
            'patient_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full name of patient'
            }),
            'patient_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890',
                'type': 'tel'
            }),
            'patient_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'patient@example.com'
            }),
            'ailment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe the medical condition or concern...',
                'rows': 4
            }),
            'symptoms': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Detailed symptoms (optional)...',
                'rows': 3
            }),
            'urgency_level': forms.Select(attrs={
                'class': 'form-control'
            }),
            'request_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'previous_medical_history': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Previous medical history (optional)...',
                'rows': 3
            }),
            'current_medications': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Current medications (optional)...',
                'rows': 2
            }),
            'allergies': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Known allergies (optional)...',
                'rows': 2
            }),
            'preferred_doctor': forms.Select(attrs={
                'class': 'form-control'
            }),
            'preferred_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Preferred location for consultation'
            }),
            'preferred_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'preferred_contact_method': forms.Select(attrs={
                'class': 'form-control'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set doctors queryset to active doctors only
        try:
            self.fields['preferred_doctor'].queryset = Doctor.objects.filter(is_verified=True)
            self.fields['preferred_doctor'].empty_label = "No preference"
        except:
            pass


class PetitionFilterForm(forms.Form):
    """Form for filtering petitions"""
    
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + Petition.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    priority = forms.ChoiceField(
        choices=[('', 'All Priorities')] + Petition.PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    category = forms.ModelChoiceField(
        queryset=PetitionCategory.objects.filter(is_active=True),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search petitions...'
        })
    )
