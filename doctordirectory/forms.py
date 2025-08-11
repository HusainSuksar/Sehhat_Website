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
            'license_number', 'specialty', 'qualification', 'experience_years', 
            'consultation_fee', 'bio', 'hospital_affiliation', 'phone_number', 
            'email', 'address', 'is_active', 'is_accepting_patients', 'assigned_moze'
        ]
        widgets = {
            'license_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Medical license number'
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
            'consultation_fee': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Brief professional biography...'
            }),
            'hospital_affiliation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Hospital affiliation'
            }),
            'phone_number': forms.TextInput(attrs={
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
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_accepting_patients': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'assigned_moze': forms.Select(attrs={'class': 'form-control'}),
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
    """Form for creating and editing appointments"""
    
    class Meta:
        model = Appointment
        fields = ['doctor', 'patient', 'appointment_date', 'appointment_time', 'reason', 'notes']
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
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Reason for appointment...'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Additional notes...'
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
            'day_of_week', 'start_time', 'end_time', 'is_active'
        ]
        widgets = {
            'day_of_week': forms.Select(attrs={
                'class': 'form-control'
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set defaults
        if not self.instance.pk:
            self.fields['is_active'].initial = True
        
        # Add help text
        self.fields['is_active'].help_text = 'Mark as available for this day'


class PatientForm(forms.ModelForm):
    """Form for creating and editing patients"""
    
    class Meta:
        model = Patient
        fields = [
            'full_name', 'date_of_birth', 'gender', 'phone_number', 'email', 
            'address', 'blood_group', 'allergies', 'medical_history',
            'emergency_contact_name', 'emergency_contact_phone'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full name'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'patient@example.com'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Address'
            }),
            'blood_group': forms.Select(attrs={'class': 'form-control'}),
            'allergies': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Known allergies...'
            }),
            'medical_history': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Medical history...'
            }),
            'emergency_contact_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency contact name'
            }),
            'emergency_contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency contact phone'
            }),
        }


class MedicalServiceForm(forms.ModelForm):
    """Form for creating and editing medical services"""
    
    class Meta:
        model = MedicalService
        fields = ['doctor', 'name', 'description', 'duration_minutes', 'price', 'is_active']
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
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class PatientLogForm(forms.ModelForm):
    """Form for logging patient interactions"""
    
    class Meta:
        model = PatientLog
        fields = ['patient_its_id', 'patient_name', 'ailment', 'visit_type', 'symptoms', 'diagnosis', 'prescription']
        widgets = {
            'patient_its_id': forms.TextInput(attrs={'class': 'form-control'}),
            'patient_name': forms.TextInput(attrs={'class': 'form-control'}),
            'ailment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe the main ailment or complaint'
            }),
            'visit_type': forms.Select(attrs={'class': 'form-control'}),
            'symptoms': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Patient symptoms'
            }),
            'diagnosis': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Medical diagnosis'
            }),
            'prescription': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Prescribed medication and treatment'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set required fields
        self.fields['patient_its_id'].required = True
        self.fields['ailment'].required = True


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