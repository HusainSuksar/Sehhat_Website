from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta, time

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
    
    def __init__(self, *args, **kwargs):
        # Extract the doctor parameter if provided
        doctor = kwargs.pop('doctor', None)
        super().__init__(*args, **kwargs)
        
        # If a doctor is provided, set it as the initial value and make it readonly
        if doctor:
            self.fields['doctor'].initial = doctor
            self.fields['doctor'].widget.attrs['readonly'] = True
            # Filter services to only show services for this doctor
            if hasattr(self.fields['service'], 'queryset'):
                from .models import MedicalService
                self.fields['service'].queryset = MedicalService.objects.filter(
                    doctor=doctor, 
                    is_available=True
                )
    
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
        if appointment_date and appointment_date < timezone.now().date():
            raise forms.ValidationError('Appointment date cannot be in the past.')
        return appointment_date


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