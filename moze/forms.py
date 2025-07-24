from django import forms
from django.contrib.auth import get_user_model
from .models import Moze, MozeComment, MozeSettings

User = get_user_model()


class MozeForm(forms.ModelForm):
    """Form for creating and editing Moze instances"""
    
    class Meta:
        model = Moze
        fields = [
            'name', 'location', 'address', 'aamil', 'moze_coordinator', 
            'team_members', 'established_date', 'is_active', 'capacity',
            'contact_phone', 'contact_email'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Moze name'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter location'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter full address'
            }),
            'aamil': forms.Select(attrs={'class': 'form-control'}),
            'moze_coordinator': forms.Select(attrs={'class': 'form-control'}),
            'team_members': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'size': '6'
            }),
            'established_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '1000'
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890'
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'contact@moze.com'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter aamil choices to only Aamil role users
        self.fields['aamil'].queryset = User.objects.filter(role='aamil', is_active=True)
        
        # Filter coordinator choices
        self.fields['moze_coordinator'].queryset = User.objects.filter(
            role='moze_coordinator', 
            is_active=True
        )
        
        # Filter team members (exclude current aamil and coordinator to avoid duplication)
        team_queryset = User.objects.filter(is_active=True).exclude(
            role='badri_mahal_admin'
        )
        self.fields['team_members'].queryset = team_queryset
        
        # If user is Aamil, set themselves as default and make field readonly
        if user and user.role == 'aamil':
            self.fields['aamil'].initial = user
            if not user.role == 'admin':
                self.fields['aamil'].widget.attrs['readonly'] = True
                self.fields['aamil'].disabled = True
        
        # Set required fields
        self.fields['name'].required = True
        self.fields['location'].required = True
        self.fields['aamil'].required = True
        
        # Add help text
        self.fields['team_members'].help_text = 'Hold Ctrl/Cmd to select multiple team members'
        self.fields['capacity'].help_text = 'Maximum number of patients that can be handled'
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            # Check for unique name (case insensitive)
            existing = Moze.objects.filter(name__iexact=name)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError('A Moze with this name already exists.')
        return name
    
    def clean_contact_phone(self):
        phone = self.cleaned_data.get('contact_phone')
        if phone:
            # Basic phone validation
            cleaned_phone = ''.join(filter(str.isdigit, phone))
            if len(cleaned_phone) < 10:
                raise forms.ValidationError('Please enter a valid phone number with at least 10 digits.')
        return phone
    
    def clean(self):
        cleaned_data = super().clean()
        aamil = cleaned_data.get('aamil')
        moze_coordinator = cleaned_data.get('moze_coordinator')
        team_members = cleaned_data.get('team_members')
        
        # Ensure aamil and coordinator are different
        if aamil and moze_coordinator and aamil == moze_coordinator:
            raise forms.ValidationError('Aamil and Moze Coordinator must be different people.')
        
        # Check if aamil/coordinator are in team members (they'll be added automatically)
        if team_members:
            if aamil and aamil in team_members:
                team_members = team_members.exclude(pk=aamil.pk)
                cleaned_data['team_members'] = team_members
            if moze_coordinator and moze_coordinator in team_members:
                team_members = team_members.exclude(pk=moze_coordinator.pk)
                cleaned_data['team_members'] = team_members
        
        return cleaned_data


class MozeCommentForm(forms.ModelForm):
    """Form for posting comments on Moze"""
    
    class Meta:
        model = MozeComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write your comment here...',
                'required': True
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].required = True
        self.fields['content'].label = 'Comment'
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if content:
            if len(content.strip()) < 5:
                raise forms.ValidationError('Comment must be at least 5 characters long.')
            if len(content) > 1000:
                raise forms.ValidationError('Comment cannot exceed 1000 characters.')
        return content


class MozeSettingsForm(forms.ModelForm):
    """Form for configuring Moze settings"""
    
    class Meta:
        model = MozeSettings
        fields = [
            'allow_walk_ins', 'appointment_duration', 'working_hours_start',
            'working_hours_end', 'working_days', 'emergency_contact',
            'special_instructions'
        ]
        widgets = {
            'allow_walk_ins': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'appointment_duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '15',
                'max': '180',
                'step': '15'
            }),
            'working_hours_start': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'working_hours_end': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'emergency_contact': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency contact number'
            }),
            'special_instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Any special instructions for this Moze...'
            }),
        }
    
    working_days_choices = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    working_days = forms.MultipleChoiceField(
        choices=working_days_choices,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        required=False,
        help_text='Select working days for this Moze'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set default working days if creating new
        if not self.instance.pk:
            self.fields['working_days'].initial = [0, 1, 2, 3, 4]  # Monday to Friday
        
        # Add help text
        self.fields['appointment_duration'].help_text = 'Default appointment duration in minutes'
        self.fields['allow_walk_ins'].help_text = 'Allow patients to walk in without appointments'
    
    def clean_appointment_duration(self):
        duration = self.cleaned_data.get('appointment_duration')
        if duration and (duration < 15 or duration > 180):
            raise forms.ValidationError('Appointment duration must be between 15 and 180 minutes.')
        return duration
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('working_hours_start')
        end_time = cleaned_data.get('working_hours_end')
        
        if start_time and end_time:
            if start_time >= end_time:
                raise forms.ValidationError('Working hours end time must be after start time.')
        
        return cleaned_data


class MozeSearchForm(forms.Form):
    """Form for searching and filtering Mozes"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, location, or Aamil...'
        })
    )
    
    status = forms.ChoiceField(
        choices=[
            ('', 'All Status'),
            ('active', 'Active'),
            ('inactive', 'Inactive'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by location...'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['search'].label = 'Search'
        self.fields['status'].label = 'Status'
        self.fields['location'].label = 'Location'


class BulkMozeUploadForm(forms.Form):
    """Form for bulk uploading Mozes via CSV"""
    
    csv_file = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': '.csv'
        }),
        help_text='Upload a CSV file with Moze data'
    )
    
    def clean_csv_file(self):
        csv_file = self.cleaned_data.get('csv_file')
        if csv_file:
            if not csv_file.name.endswith('.csv'):
                raise forms.ValidationError('Please upload a CSV file.')
            if csv_file.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError('File size should not exceed 5MB.')
        return csv_file