from django import forms
from django.contrib.auth import get_user_model
from .models import Hospital, Patient, Appointment, MedicalRecord, Prescription, LabTest, Doctor

User = get_user_model()


class HospitalForm(forms.ModelForm):
    """Form for creating and editing hospitals"""
    
    class Meta:
        model = Hospital
        fields = [
            'name', 'description', 'address', 'phone', 'email',
            'hospital_type', 'total_beds', 'available_beds', 'emergency_beds', 'icu_beds',
            'is_active', 'is_emergency_capable', 'has_pharmacy', 'has_laboratory'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Hospital name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Hospital description'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Hospital address'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'hospital@example.com'
            }),
            'hospital_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'total_beds': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '10000'
            }),
            'available_beds': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '10000'
            }),
            'emergency_beds': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '1000'
            }),
            'icu_beds': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '1000'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_emergency_capable': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'has_pharmacy': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'has_laboratory': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class PatientForm(forms.ModelForm):
    """Form for creating and editing patient records"""
    
    class Meta:
        model = Patient
        fields = [
            'its_id', 'first_name', 'last_name', 'arabic_name', 'date_of_birth', 'gender', 'blood_group',
            'phone_number', 'email', 'address', 'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relationship', 'allergies', 'chronic_conditions', 'current_medications',
            'registered_moze', 'is_active'
        ]
        widgets = {
            'its_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ITS ID (8 digits)',
                'pattern': '[0-9]{8}',
                'title': 'ITS ID must be exactly 8 digits'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last name'
            }),
            'arabic_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Arabic name (optional)'
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
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email address (optional)'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Address'
            }),
            'emergency_contact_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency contact name'
            }),
            'emergency_contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency contact phone'
            }),
            'emergency_contact_relationship': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Relationship to patient'
            }),
            'allergies': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Known allergies (optional)'
            }),
            'chronic_conditions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Chronic medical conditions (optional)'
            }),
            'current_medications': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Current medications (optional)'
            }),
            'registered_moze': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter active mozes
        from moze.models import Moze
        self.fields['registered_moze'].queryset = Moze.objects.filter(is_active=True)


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
    """Form for creating and editing medical records"""
    
    class Meta:
        model = MedicalRecord
        fields = [
            'patient', 'doctor', 'moze', 'chief_complaint', 'history_of_present_illness',
            'past_medical_history', 'family_history', 'social_history', 'physical_examination',
            'diagnosis', 'differential_diagnosis', 'treatment_plan', 'medications_prescribed',
            'lab_tests_ordered', 'imaging_ordered', 'referrals', 'follow_up_required',
            'follow_up_date', 'follow_up_instructions', 'patient_education', 'doctor_notes'
        ]
        widgets = {
            'patient': forms.Select(attrs={
                'class': 'form-control'
            }),
            'doctor': forms.Select(attrs={
                'class': 'form-control'
            }),
            'moze': forms.Select(attrs={
                'class': 'form-control'
            }),
            'chief_complaint': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Main complaint or reason for visit'
            }),
            'history_of_present_illness': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'History of present illness (optional)'
            }),
            'past_medical_history': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Past medical history (optional)'
            }),
            'family_history': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Family history (optional)'
            }),
            'social_history': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Social history (optional)'
            }),
            'physical_examination': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Physical examination findings (optional)'
            }),
            'diagnosis': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Diagnosis'
            }),
            'differential_diagnosis': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Differential diagnosis (optional)'
            }),
            'treatment_plan': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Treatment plan'
            }),
            'medications_prescribed': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Medications prescribed (optional)'
            }),
            'lab_tests_ordered': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Lab tests ordered (optional)'
            }),
            'imaging_ordered': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Imaging ordered (optional)'
            }),
            'referrals': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Referrals (optional)'
            }),
            'follow_up_required': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'follow_up_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'follow_up_instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Follow-up instructions (optional)'
            }),
            'patient_education': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Patient education provided (optional)'
            }),
            'doctor_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Private doctor notes (optional)'
            })
        }


class PrescriptionForm(forms.ModelForm):
    """Form for creating and editing prescriptions"""
    
    class Meta:
        model = Prescription
        fields = [
            'medical_record', 'patient', 'doctor', 'medication_name', 'dosage',
            'frequency', 'duration', 'quantity', 'instructions', 'warnings',
            'is_active', 'is_dispensed', 'dispensed_date', 'dispensed_by'
        ]
        widgets = {
            'medical_record': forms.Select(attrs={
                'class': 'form-control'
            }),
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
                'placeholder': 'e.g., 500mg, 10ml'
            }),
            'frequency': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Twice daily, Every 8 hours'
            }),
            'duration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 7 days, 2 weeks'
            }),
            'quantity': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 30 tablets, 100ml'
            }),
            'instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Special instructions for taking the medication'
            }),
            'warnings': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Warnings and precautions (optional)'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_dispensed': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'dispensed_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'dispensed_by': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Name of person who dispensed'
            })
        }


class LabTestForm(forms.ModelForm):
    """Form for creating and editing lab tests"""
    
    class Meta:
        model = LabTest
        fields = [
            'medical_record', 'patient', 'doctor', 'test_name', 'test_category',
            'test_code', 'status', 'result_text', 'normal_range', 'is_abnormal',
            'lab_name', 'lab_technician', 'doctor_notes', 'lab_notes'
        ]
        widgets = {
            'medical_record': forms.Select(attrs={
                'class': 'form-control'
            }),
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
            'test_category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'test_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Test code (optional)'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'result_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Test results (optional)'
            }),
            'normal_range': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Normal range (optional)'
            }),
            'is_abnormal': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'lab_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Laboratory name (optional)'
            }),
            'lab_technician': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Lab technician name (optional)'
            }),
            'doctor_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Doctor notes (optional)'
            }),
            'lab_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Lab notes (optional)'
            })
        }


class PatientSearchForm(forms.Form):
    """Form for searching patients"""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, ITS ID, or phone number'
        })
    )
    
    gender = forms.ChoiceField(
        required=False,
        choices=[('', 'All Genders')] + [
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    blood_group = forms.ChoiceField(
        required=False,
        choices=[('', 'All Blood Groups')] + [
            ('A+', 'A+'), ('A-', 'A-'),
            ('B+', 'B+'), ('B-', 'B-'),
            ('AB+', 'AB+'), ('AB-', 'AB-'),
            ('O+', 'O+'), ('O-', 'O-'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    is_active = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'All Status'),
            ('True', 'Active'),
            ('False', 'Inactive')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class AppointmentFilterForm(forms.Form):
    """Form for filtering appointments"""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by patient name, doctor name, or reason'
        })
    )
    
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Statuses')] + [
            ('scheduled', 'Scheduled'),
            ('confirmed', 'Confirmed'),
            ('checked_in', 'Checked In'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
            ('no_show', 'No Show'),
            ('rescheduled', 'Rescheduled'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    appointment_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Types')] + [
            ('regular', 'Regular Appointment'),
            ('follow_up', 'Follow-up'),
            ('urgent', 'Urgent'),
            ('emergency', 'Emergency'),
            ('screening', 'Health Screening'),
            ('consultation', 'Consultation'),
        ],
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
    
    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.filter(is_available=True),
        required=False,
        empty_label="All Doctors",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    hospital = forms.ModelChoiceField(
        queryset=Hospital.objects.filter(is_active=True),
        required=False,
        empty_label="All Hospitals",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
