from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta, time, date

from .models import (
    Doctor, DoctorSchedule, MedicalService, Patient, Appointment
)

User = get_user_model()


class DoctorForm(forms.ModelForm):
    """Form for creating and editing Doctor profiles"""
    
    class Meta:
        model = Doctor
        fields = [
            'name', 'its_id', 'specialty', 'qualification', 'experience_years', 
            'verified_certificate', 'is_verified', 'is_available', 'license_number', 
            'consultation_fee', 'phone', 'email', 'address', 'languages_spoken', 
            'bio', 'assigned_moze', 'user'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Doctor name'
            }),
            'its_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ITS ID'
            }),
            'specialty': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Medical specialty'
            }),
            'qualification': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Medical qualifications'
            }),
            'experience_years': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '50'
            }),
            'verified_certificate': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Certificate verification status'
            }),
            'is_verified': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_available': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'license_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Medical license number'
            }),
            'consultation_fee': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'doctor@example.com'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Address'
            }),
            'languages_spoken': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Languages spoken'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Brief professional biography...'
            }),
            'assigned_moze': forms.Select(attrs={'class': 'form-control'}),
            'user': forms.Select(attrs={'class': 'form-control'}),
        }


class DoctorScheduleForm(forms.ModelForm):
    """Form for creating and editing doctor schedules"""
    
    class Meta:
        model = DoctorSchedule
        fields = ['doctor', 'date', 'start_time', 'end_time', 'is_available', 'max_patients', 'notes']
        widgets = {
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'is_available': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'max_patients': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '50'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Schedule notes...'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time:
            if start_time >= end_time:
                raise forms.ValidationError('End time must be after start time.')
        
        return cleaned_data


class AppointmentForm(forms.ModelForm):
    """Form for creating and editing appointments"""
    
    # Add ITS ID field for patient lookup
    patient_its_id = forms.CharField(
        max_length=8,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter 8-digit ITS ID',
            'pattern': '[0-9]{8}',
            'title': 'Please enter exactly 8 digits',
            'id': 'patient_its_id'
        }),
        label='Patient ITS ID',
        help_text='Enter the 8-digit ITS ID to automatically fetch patient details'
    )
    
    # Display field for patient name (read-only)
    patient_name_display = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': True,
            'style': 'background-color: #f8f9fa;',
            'id': 'patient_name_display'
        }),
        label='Patient Name',
        help_text='Patient name will be fetched automatically from ITS'
    )
    
    def __init__(self, *args, **kwargs):
        # Extract custom parameters if provided
        doctor = kwargs.pop('doctor', None)
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Store user for validation
        self.user = user
        
        # If a doctor is provided, set it as the initial value and make it readonly
        if doctor:
            self.fields['doctor'].initial = doctor
            self.fields['doctor'].widget = forms.HiddenInput()  # Hide doctor field completely
            # Filter services to only show services for this doctor
            if hasattr(self.fields['service'], 'queryset'):
                from .models import MedicalService
                self.fields['service'].queryset = MedicalService.objects.filter(
                    doctor=doctor, 
                    is_available=True
                )
        elif user and user.is_doctor:
            # If logged in as doctor, auto-select the doctor and hide the field
            try:
                from .models import Doctor
                doctor_instance = Doctor.objects.get(user=user)
                self.fields['doctor'].initial = doctor_instance
                self.fields['doctor'].widget = forms.HiddenInput()  # Hide doctor field
                # Filter services to only show services for this doctor
                if hasattr(self.fields['service'], 'queryset'):
                    from .models import MedicalService
                    self.fields['service'].queryset = MedicalService.objects.filter(
                        doctor=doctor_instance, 
                        is_available=True
                    )
            except Doctor.DoesNotExist:
                # If doctor profile doesn't exist, show error
                pass
        else:
            # For admin users, show all available doctors
            from .models import Doctor
            self.fields['doctor'].queryset = Doctor.objects.filter(is_available=True)
        
        # Hide the original patient field and use ITS ID lookup instead
        self.fields['patient'].widget = forms.HiddenInput()
        self.fields['patient'].required = False
        
        # Handle patient field based on user role
        if user:
            if user.role == 'patient':
                # For patients: auto-populate their own ITS ID and name
                try:
                    patient_instance = user.patient_profile.first()
                    if patient_instance and user.its_id:
                        self.fields['patient'].initial = patient_instance
                        self.fields['patient_its_id'].initial = user.its_id
                        self.fields['patient_its_id'].widget.attrs.update({
                            'readonly': True,
                            'style': 'background-color: #f8f9fa;'
                        })
                        self.fields['patient_name_display'].initial = f"{user.get_full_name()} (You)"
                    elif user.its_id:
                        self.fields['patient_its_id'].initial = user.its_id
                        self.fields['patient_its_id'].widget.attrs.update({
                            'readonly': True,
                            'style': 'background-color: #f8f9fa;'
                        })
                        self.fields['patient_name_display'].initial = f"{user.get_full_name()} (You)"
                    else:
                        self.fields['patient_name_display'].initial = "Please complete your profile with ITS ID"
                        self.fields['patient_name_display'].widget.attrs.update({
                            'style': 'background-color: #fee2e2; color: #dc2626;'
                        })
                except Exception:
                    pass
            else:
                # For doctors/admins: they can enter any ITS ID
                self.fields['patient_its_id'].help_text = 'Enter the patient\'s 8-digit ITS ID to fetch their details automatically'
    
    def clean(self):
        cleaned_data = super().clean()
        patient_its_id = cleaned_data.get('patient_its_id')
        patient = cleaned_data.get('patient')
        
        # If patient is already set (for patient users), skip ITS ID validation
        if patient:
            return cleaned_data
        
        # Validate and fetch patient by ITS ID
        if patient_its_id:
            # Validate ITS ID format
            if len(patient_its_id) != 8 or not patient_its_id.isdigit():
                raise forms.ValidationError('ITS ID must be exactly 8 digits.')
            
            try:
                # First, try to find existing user with this ITS ID
                from accounts.models import User
                user = User.objects.filter(its_id=patient_its_id).first()
                
                if user:
                    # Check if user has a patient profile
                    patient_profile = user.patient_profile.first()
                    if patient_profile:
                        cleaned_data['patient'] = patient_profile
                    else:
                        # Create patient profile for existing user
                        from .models import Patient
                        from datetime import date
                        patient_profile = Patient.objects.create(
                            user=user,
                            date_of_birth=date(1990, 1, 1),  # Default DOB, can be updated later
                            gender='other'  # Default gender, can be updated later
                        )
                        cleaned_data['patient'] = patient_profile
                else:
                    # Fetch user data from ITS API
                    from accounts.services import ITSService
                    its_data = ITSService.fetch_user_data(patient_its_id)
                    
                    if its_data:
                        # Create new user from ITS data
                        user = User.objects.create_user(
                            username=patient_its_id,
                            its_id=patient_its_id,
                            first_name=its_data.get('first_name', ''),
                            last_name=its_data.get('last_name', ''),
                            email=its_data.get('email', f'{patient_its_id}@its.temp'),
                            phone_number=its_data.get('mobile_number', ''),
                            role='patient'  # Default to patient role
                        )
                        
                        # Create patient profile
                        from .models import Patient
                        from datetime import date
                        
                        # Parse date of birth if available
                        dob = date(1990, 1, 1)  # Default
                        if its_data.get('date_of_birth'):
                            try:
                                dob = datetime.strptime(its_data['date_of_birth'], '%Y-%m-%d').date()
                            except:
                                pass
                        
                        patient_profile = Patient.objects.create(
                            user=user,
                            date_of_birth=dob,
                            gender=its_data.get('gender', 'other').lower()
                        )
                        cleaned_data['patient'] = patient_profile
                    else:
                        raise forms.ValidationError(f'Could not fetch patient data for ITS ID: {patient_its_id}. Please verify the ITS ID.')
                        
            except Exception as e:
                raise forms.ValidationError(f'Error processing ITS ID: {str(e)}')
        else:
            # If no patient_its_id provided and no patient selected, require it
            if not patient:
                # For admin users, provide more helpful error message
                if hasattr(self, 'user') and self.user and self.user.is_admin:
                    raise forms.ValidationError('Please enter a valid 8-digit ITS ID in the Patient ITS ID field and click "Fetch" to load patient information before submitting.')
                else:
                    raise forms.ValidationError('Please enter a patient ITS ID and click "Fetch" to load patient information.')
        
        return cleaned_data
    
    class Meta:
        model = Appointment
        fields = ['doctor', 'patient', 'service', 'appointment_date', 'appointment_time', 'reason_for_visit', 'notes']
        widgets = {
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'appointment_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'appointment_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'service': forms.Select(attrs={'class': 'form-control'}),
            'reason_for_visit': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Reason for visit...'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Additional notes...'
            }),
        }
    
    def clean_appointment_date(self):
        appointment_date = self.cleaned_data.get('appointment_date')
        if appointment_date:
            if appointment_date < timezone.now().date():
                raise forms.ValidationError('Appointment date cannot be in the past.')
            # Don't allow appointments too far in the future (e.g., more than 6 months)
            max_future_date = timezone.now().date() + timedelta(days=180)
            if appointment_date > max_future_date:
                raise forms.ValidationError('Appointment date cannot be more than 6 months in the future.')
        return appointment_date
    
    def clean(self):
        cleaned_data = super().clean()
        appointment_date = cleaned_data.get('appointment_date')
        appointment_time = cleaned_data.get('appointment_time')
        doctor = cleaned_data.get('doctor')
        
        # Check for double booking if all required fields are present
        if appointment_date and appointment_time and doctor:
            existing_appointment = Appointment.objects.filter(
                doctor=doctor,
                appointment_date=appointment_date,
                appointment_time=appointment_time
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing_appointment.exists():
                raise forms.ValidationError(
                    'This time slot is already booked for this doctor. Please choose a different time.'
                )
        
        return cleaned_data


class PatientForm(forms.ModelForm):
    """Form for creating and editing patients"""
    
    class Meta:
        model = Patient
        fields = [
            'date_of_birth', 'gender', 'blood_group', 'emergency_contact', 
            'medical_history', 'allergies', 'current_medications', 'user'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'blood_group': forms.Select(attrs={'class': 'form-control'}),
            'emergency_contact': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency contact'
            }),
            'medical_history': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Medical history...'
            }),
            'allergies': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Known allergies...'
            }),
            'current_medications': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Current medications...'
            }),
            'user': forms.Select(attrs={'class': 'form-control'}),
        }


class MedicalServiceForm(forms.ModelForm):
    """Form for creating and editing medical services"""
    
    class Meta:
        model = MedicalService
        fields = ['doctor', 'name', 'description', 'duration_minutes', 'price', 'is_available']
        widgets = {
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Service name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Service description...'
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '5',
                'max': '480'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
            'is_available': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


# Simple form for medical record notes (since MedicalRecord model was removed)
class MedicalRecordForm(forms.Form):
    """Simple form for adding medical notes to appointments"""
    
    notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Medical notes and observations...'
        }),
        required=True,
        help_text='Enter medical notes for this appointment'
    )
    
    diagnosis = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Diagnosis'
        }),
        required=False,
        help_text='Primary diagnosis'
    )
    
    treatment = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Treatment plan...'
        }),
        required=False,
        help_text='Treatment recommendations'
    )


class DoctorSearchForm(forms.Form):
    """Form for searching doctors"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, specialty, or location...'
        })
    )
    
    specialty = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by specialty...'
        })
    )
    
    available_today = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Available today'
    )