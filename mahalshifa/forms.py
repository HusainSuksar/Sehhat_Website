from django import forms
from django.contrib.auth import get_user_model
from .models import Hospital, Patient, Appointment, MedicalRecord, Prescription, LabTest

User = get_user_model()


class HospitalForm(forms.ModelForm):
    """Form for creating and editing hospitals"""
    
    class Meta:
        model = Hospital
        fields = [
            'name', 'address', 'city', 'state', 'phone', 'email',
            'website', 'hospital_type', 'capacity', 'specialties',
            'emergency_services', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Hospital name'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Hospital address'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State/Province'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'hospital@example.com'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://hospital-website.com'
            }),
            'hospital_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '10000'
            }),
            'specialties': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'List specialties (comma separated)'
            }),
            'emergency_services': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class PatientForm(forms.ModelForm):
    """Form for creating and editing patient records"""
    
    class Meta:
        model = Patient
        fields = [
            'patient_id', 'date_of_birth', 'gender', 'blood_group',
            'emergency_contact_name', 'emergency_contact_phone',
            'address', 'allergies', 'medical_history', 'current_medications',
            'insurance_provider', 'insurance_policy_number', 'hospital'
        ]
        widgets = {
            'patient_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Patient ID'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control'
            }),
            'blood_group': forms.Select(attrs={
                'class': 'form-control'
            }),
            'emergency_contact_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency contact name'
            }),
            'emergency_contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency contact phone'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Patient address'
            }),
            'allergies': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Known allergies'
            }),
            'medical_history': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Medical history'
            }),
            'current_medications': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Current medications'
            }),
            'insurance_provider': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Insurance provider'
            }),
            'insurance_policy_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Policy number'
            }),
            'hospital': forms.Select(attrs={
                'class': 'form-control'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter active hospitals
        self.fields['hospital'].queryset = Hospital.objects.filter(is_active=True)


class AppointmentForm(forms.ModelForm):
    """Form for creating appointments"""
    
    class Meta:
        model = Appointment
        fields = [
            'patient', 'doctor', 'appointment_date', 'appointment_time',
            'appointment_type', 'reason', 'notes', 'status'
        ]
        widgets = {
            'patient': forms.Select(attrs={
                'class': 'form-control'
            }),
            'doctor': forms.Select(attrs={
                'class': 'form-control'
            }),
            'appointment_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'appointment_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'appointment_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Reason for appointment'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Additional notes (optional)'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            })
        }


class MedicalRecordForm(forms.ModelForm):
    """Form for creating medical records"""
    
    class Meta:
        model = MedicalRecord
        fields = [
            'patient', 'doctor', 'symptoms', 'diagnosis',
            'treatment', 'prescription', 'notes', 'follow_up_date'
        ]
        widgets = {
            'patient': forms.Select(attrs={
                'class': 'form-control'
            }),
            'doctor': forms.Select(attrs={
                'class': 'form-control'
            }),
            'symptoms': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Patient symptoms'
            }),
            'diagnosis': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Medical diagnosis'
            }),
            'treatment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Treatment plan'
            }),
            'prescription': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Prescribed medications'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes'
            }),
            'follow_up_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            })
        }


class PrescriptionForm(forms.ModelForm):
    """Form for creating prescriptions"""
    
    class Meta:
        model = Prescription
        fields = [
            'patient', 'doctor', 'medication_name', 'dosage',
            'frequency', 'duration', 'instructions', 'refills'
        ]
        widgets = {
            'patient': forms.Select(attrs={
                'class': 'form-control'
            }),
            'doctor': forms.Select(attrs={
                'class': 'form-control'
            }),
            'medication_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Medication name'
            }),
            'dosage': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dosage (e.g., 500mg)'
            }),
            'frequency': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Frequency (e.g., twice daily)'
            }),
            'duration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Duration (e.g., 7 days)'
            }),
            'instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Special instructions'
            }),
            'refills': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '12'
            })
        }


class LabTestForm(forms.ModelForm):
    """Form for ordering lab tests"""
    
    class Meta:
        model = LabTest
        fields = [
            'patient', 'doctor', 'test_name', 'test_type',
            'instructions', 'urgent', 'notes'
        ]
        widgets = {
            'patient': forms.Select(attrs={
                'class': 'form-control'
            }),
            'doctor': forms.Select(attrs={
                'class': 'form-control'
            }),
            'test_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Test name'
            }),
            'test_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Test instructions'
            }),
            'urgent': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Additional notes'
            })
        }


class PatientSearchForm(forms.Form):
    """Form for searching patients"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, patient ID, or phone...'
        })
    )
    
    hospital = forms.ModelChoiceField(
        queryset=Hospital.objects.filter(is_active=True),
        required=False,
        empty_label="All Hospitals",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    blood_group = forms.ChoiceField(
        choices=[('', 'All Blood Groups')] + Patient.BLOOD_GROUP_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class AppointmentFilterForm(forms.Form):
    """Form for filtering appointments"""
    
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + Appointment.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    appointment_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Appointment.APPOINTMENT_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
