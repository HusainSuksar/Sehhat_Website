from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta, time

from .models import (
    Doctor, DoctorSchedule, PatientLog, DoctorAvailability,
    MedicalService, Patient, Appointment, MedicalRecord, Prescription, LabTest, VitalSigns
)

User = get_user_model()


class DoctorForm(forms.ModelForm):
    """Form for creating and editing Doctor profiles"""
    
    class Meta:
        model = Doctor
        fields = [
            'license_number', 'experience_years', 'consultation_fee',
            'assigned_moze', 'is_verified', 'bio'
        ]
        widgets = {
            'license_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Medical license number'
            }),
            'experience_years': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '50'
            }),
            'consultation_fee': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
            'assigned_moze': forms.Select(attrs={'class': 'form-control'}),
            'is_verified': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Brief professional biography...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set help text
        self.fields['license_number'].help_text = 'Official medical license number'
        self.fields['experience_years'].help_text = 'Years of medical practice experience'
        self.fields['consultation_fee'].help_text = 'Fee per consultation session'
        self.fields['is_verified'].help_text = 'Mark as verified doctor'
    
    def clean_license_number(self):
        license_number = self.cleaned_data.get('license_number')
        if license_number:
            # Check for unique license number
            existing = Doctor.objects.filter(license_number=license_number)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError('A doctor with this license number already exists.')
        return license_number


class AppointmentForm(forms.ModelForm):
    """Form for booking appointments"""
    
    class Meta:
        model = Appointment
        fields = [
            'doctor', 'patient', 'appointment_date', 'appointment_time',
            'service', 'reason_for_visit', 'notes'
        ]
        widgets = {
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'appointment_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': timezone.now().date().isoformat()
            }),
            'appointment_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'service': forms.Select(attrs={'class': 'form-control'}),
            'reason_for_visit': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief reason for the visit'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes (optional)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        doctor = kwargs.pop('doctor', None)
        super().__init__(*args, **kwargs)
        
        # Filter doctors to only verified ones
        self.fields['doctor'].queryset = Doctor.objects.filter(is_verified=True)
        
        # If specific doctor provided, set and hide the field
        if doctor:
            self.fields['doctor'].initial = doctor
            self.fields['doctor'].widget = forms.HiddenInput()
            
            # Filter services to this doctor's services
            self.fields['service'].queryset = MedicalService.objects.filter(
                doctor=doctor,
                is_active=True
            )
        else:
            self.fields['service'].queryset = MedicalService.objects.filter(is_active=True)
        
        # Set field requirements
        self.fields['appointment_date'].required = True
        self.fields['appointment_time'].required = True
        self.fields['reason_for_visit'].required = True
        
        # Add help text
        self.fields['appointment_date'].help_text = 'Select appointment date'
        self.fields['appointment_time'].help_text = 'Preferred appointment time'
    
    def clean_appointment_date(self):
        appointment_date = self.cleaned_data.get('appointment_date')
        if appointment_date:
            if appointment_date < timezone.now().date():
                raise forms.ValidationError('Appointment date cannot be in the past.')
            
            # Check if date is more than 3 months in future
            max_date = timezone.now().date() + timedelta(days=90)
            if appointment_date > max_date:
                raise forms.ValidationError('Appointments can only be booked up to 3 months in advance.')
        
        return appointment_date
    
    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        appointment_date = cleaned_data.get('appointment_date')
        appointment_time = cleaned_data.get('appointment_time')
        
        if doctor and appointment_date and appointment_time:
            # Check doctor availability
            availability = DoctorAvailability.objects.filter(
                doctor=doctor,
                date=appointment_date,
                start_time__lte=appointment_time,
                end_time__gte=appointment_time,
                is_available=True
            ).first()
            
            if not availability:
                raise forms.ValidationError('Doctor is not available at the selected time.')
            
            # Check for conflicting appointments
            existing_appointment = Appointment.objects.filter(
                doctor=doctor,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                status__in=['scheduled', 'confirmed']
            ).first()
            
            if existing_appointment:
                raise forms.ValidationError('This time slot is already booked.')
        
        return cleaned_data


class MedicalRecordForm(forms.ModelForm):
    """Form for creating medical records"""
    
    class Meta:
        model = MedicalRecord
        fields = [
            'diagnosis', 'symptoms', 'treatment_plan', 'medications',
            'follow_up_required', 'follow_up_date', 'notes'
        ]
        widgets = {
            'diagnosis': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Primary diagnosis'
            }),
            'symptoms': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Symptoms observed or reported'
            }),
            'treatment_plan': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Treatment plan and recommendations'
            }),
            'medications': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Prescribed medications'
            }),
            'follow_up_required': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'follow_up_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set required fields
        self.fields['diagnosis'].required = True
        self.fields['symptoms'].required = True
        self.fields['treatment_plan'].required = True
        
        # Add help text
        self.fields['follow_up_required'].help_text = 'Check if follow-up appointment is needed'
        self.fields['follow_up_date'].help_text = 'Recommended follow-up date'
    
    def clean_follow_up_date(self):
        follow_up_date = self.cleaned_data.get('follow_up_date')
        follow_up_required = self.cleaned_data.get('follow_up_required')
        
        if follow_up_required and not follow_up_date:
            raise forms.ValidationError('Follow-up date is required when follow-up is needed.')
        
        if follow_up_date and follow_up_date <= timezone.now().date():
            raise forms.ValidationError('Follow-up date must be in the future.')
        
        return follow_up_date


class PrescriptionForm(forms.ModelForm):
    """Form for creating prescriptions"""
    
    class Meta:
        model = Prescription
        fields = [
            'medication_name', 'dosage', 'frequency', 'duration',
            'instructions', 'refills_allowed'
        ]
        widgets = {
            'medication_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Medication name'
            }),
            'dosage': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 500mg'
            }),
            'frequency': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Twice daily'
            }),
            'duration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 7 days'
            }),
            'instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Special instructions for taking medication'
            }),
            'refills_allowed': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '12'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set required fields
        self.fields['medication_name'].required = True
        self.fields['dosage'].required = True
        self.fields['frequency'].required = True
        self.fields['duration'].required = True
        
        # Add help text
        self.fields['refills_allowed'].help_text = 'Number of allowed refills'


class DoctorScheduleForm(forms.ModelForm):
    """Form for managing doctor schedules"""
    
    class Meta:
        model = DoctorSchedule
        fields = [
            'date', 'start_time', 'end_time', 'is_available',
            'moze_location', 'notes'
        ]
        widgets = {
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
            'moze_location': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Schedule notes'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set default availability to True
        if not self.instance.pk:
            self.fields['is_available'].initial = True
        
        # Add help text
        self.fields['is_available'].help_text = 'Mark as available for appointments'
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time:
            if start_time >= end_time:
                raise forms.ValidationError('End time must be after start time.')
        
        return cleaned_data


class DoctorAvailabilityForm(forms.ModelForm):
    """Form for setting doctor availability"""
    
    class Meta:
        model = DoctorAvailability
        fields = [
            'date', 'start_time', 'end_time', 'is_available', 'max_appointments'
        ]
        widgets = {
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
            'max_appointments': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '20'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set defaults
        if not self.instance.pk:
            self.fields['is_available'].initial = True
            self.fields['max_appointments'].initial = 8
        
        # Add help text
        self.fields['max_appointments'].help_text = 'Maximum appointments for this time slot'


class PatientLogForm(forms.ModelForm):
    """Form for logging patient interactions"""
    
    class Meta:
        model = PatientLog
        fields = ['log_type', 'description', 'action_taken']
        widgets = {
            'log_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe the interaction or observation'
            }),
            'action_taken': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Action taken or recommended'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set required fields
        self.fields['log_type'].required = True
        self.fields['description'].required = True


class LabTestForm(forms.ModelForm):
    """Form for ordering lab tests"""
    
    class Meta:
        model = LabTest
        fields = [
            'test_name', 'test_type', 'test_date', 'urgency',
            'instructions', 'notes'
        ]
        widgets = {
            'test_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Name of the test'
            }),
            'test_type': forms.Select(attrs={'class': 'form-control'}),
            'test_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'urgency': forms.Select(attrs={'class': 'form-control'}),
            'instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Special instructions for the test'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Additional notes'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set required fields
        self.fields['test_name'].required = True
        self.fields['test_type'].required = True
        self.fields['test_date'].required = True
        
        # Set default test date to today
        if not self.instance.pk:
            self.fields['test_date'].initial = timezone.now().date()


class VitalSignsForm(forms.ModelForm):
    """Form for recording vital signs"""
    
    class Meta:
        model = VitalSigns
        fields = [
            'blood_pressure_systolic', 'blood_pressure_diastolic',
            'heart_rate', 'temperature', 'respiratory_rate',
            'oxygen_saturation', 'weight', 'height', 'notes'
        ]
        widgets = {
            'blood_pressure_systolic': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '70',
                'max': '300',
                'placeholder': 'mmHg'
            }),
            'blood_pressure_diastolic': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '40',
                'max': '200',
                'placeholder': 'mmHg'
            }),
            'heart_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '40',
                'max': '200',
                'placeholder': 'bpm'
            }),
            'temperature': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '35',
                'max': '45',
                'step': '0.1',
                'placeholder': '°C'
            }),
            'respiratory_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '8',
                'max': '40',
                'placeholder': 'breaths/min'
            }),
            'oxygen_saturation': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '70',
                'max': '100',
                'placeholder': '%'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '300',
                'step': '0.1',
                'placeholder': 'kg'
            }),
            'height': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '50',
                'max': '250',
                'placeholder': 'cm'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Additional observations'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add help text
        self.fields['blood_pressure_systolic'].help_text = 'Systolic pressure (mmHg)'
        self.fields['blood_pressure_diastolic'].help_text = 'Diastolic pressure (mmHg)'
        self.fields['heart_rate'].help_text = 'Heart rate (beats per minute)'
        self.fields['temperature'].help_text = 'Body temperature (°C)'
        self.fields['respiratory_rate'].help_text = 'Respiratory rate (breaths per minute)'
        self.fields['oxygen_saturation'].help_text = 'Oxygen saturation (%)'


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