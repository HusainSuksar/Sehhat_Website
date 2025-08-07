"""
Serializers for the MahalShifa app
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from .models import (
    MedicalService, Patient, Appointment, MedicalRecord, Prescription,
    LabTest, VitalSigns, Hospital, Department, Doctor, HospitalStaff,
    Room, Medication, LabResult, Admission, Discharge, TreatmentPlan,
    TreatmentMedication, Inventory, InventoryItem, EmergencyContact,
    Insurance
)
from moze.models import Moze

User = get_user_model()


# Basic User serializer for nested relationships
class UserBasicSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'full_name']
        read_only_fields = fields
    
    def get_full_name(self, obj):
        return obj.get_full_name()


# Basic Moze serializer for nested relationships
class MozeBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Moze
        fields = ['id', 'name', 'location']
        read_only_fields = fields


# Medical Service serializers
class MedicalServiceSerializer(serializers.ModelSerializer):
    category_display = serializers.SerializerMethodField()
    cost_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = MedicalService
        fields = [
            'id', 'name', 'description', 'category', 'category_display',
            'duration_minutes', 'cost', 'cost_formatted', 'is_active',
            'requires_appointment', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_category_display(self, obj):
        return obj.get_category_display()
    
    def get_cost_formatted(self, obj):
        return f"${obj.cost:.2f}"


# Hospital and Department serializers
class DepartmentSerializer(serializers.ModelSerializer):
    head = UserBasicSerializer(read_only=True)
    head_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='head',
        required=False, allow_null=True
    )
    
    class Meta:
        model = Department
        fields = [
            'id', 'name', 'description', 'head', 'head_id', 'floor_number',
            'phone_extension', 'is_active', 'created_at'
        ]
        read_only_fields = ['created_at']


class HospitalSerializer(serializers.ModelSerializer):
    departments = DepartmentSerializer(many=True, read_only=True)
    hospital_type_display = serializers.SerializerMethodField()
    bed_occupancy_rate = serializers.SerializerMethodField()
    total_staff = serializers.SerializerMethodField()
    
    class Meta:
        model = Hospital
        fields = [
            'id', 'name', 'description', 'address', 'phone', 'email',
            'hospital_type', 'hospital_type_display', 'total_beds',
            'available_beds', 'emergency_beds', 'icu_beds', 'is_active',
            'is_emergency_capable', 'has_pharmacy', 'has_laboratory',
            'bed_occupancy_rate', 'total_staff', 'departments',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_hospital_type_display(self, obj):
        return obj.get_hospital_type_display()
    
    def get_bed_occupancy_rate(self, obj):
        if obj.total_beds > 0:
            occupied = obj.total_beds - obj.available_beds
            return round((occupied / obj.total_beds) * 100, 2)
        return 0
    
    def get_total_staff(self, obj):
        return obj.staff.count()


# Doctor and Staff serializers
class DoctorSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='user'
    )
    hospital = serializers.StringRelatedField(read_only=True)
    hospital_id = serializers.PrimaryKeyRelatedField(
        queryset=Hospital.objects.all(), write_only=True, source='hospital'
    )
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), write_only=True, source='department'
    )
    consultation_fee_formatted = serializers.SerializerMethodField()
    patients_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Doctor
        fields = [
            'id', 'user', 'user_id', 'license_number', 'specialization',
            'qualification', 'experience_years', 'hospital', 'hospital_id',
            'department', 'department_id', 'is_available', 'is_emergency_doctor',
            'consultation_fee', 'consultation_fee_formatted', 'patients_count',
            'created_at'
        ]
        read_only_fields = ['created_at']
    
    def get_consultation_fee_formatted(self, obj):
        return f"${obj.consultation_fee:.2f}"
    
    def get_patients_count(self, obj):
        return obj.medical_records.values('patient').distinct().count()


class HospitalStaffSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='user'
    )
    hospital = serializers.StringRelatedField(read_only=True)
    hospital_id = serializers.PrimaryKeyRelatedField(
        queryset=Hospital.objects.all(), write_only=True, source='hospital'
    )
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), write_only=True, source='department'
    )
    staff_type_display = serializers.SerializerMethodField()
    shift_display = serializers.SerializerMethodField()
    
    class Meta:
        model = HospitalStaff
        fields = [
            'id', 'user', 'user_id', 'hospital', 'hospital_id', 'department',
            'department_id', 'staff_type', 'staff_type_display', 'employee_id',
            'shift', 'shift_display', 'is_active', 'hire_date'
        ]
    
    def get_staff_type_display(self, obj):
        return obj.get_staff_type_display()
    
    def get_shift_display(self, obj):
        return obj.get_shift_display()


# Patient serializers
class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = [
            'id', 'name', 'relationship', 'phone_primary', 'phone_secondary',
            'email', 'address', 'is_primary', 'priority_order', 'created_at'
        ]
        read_only_fields = ['created_at']


class InsuranceSerializer(serializers.ModelSerializer):
    coverage_type_display = serializers.SerializerMethodField()
    is_valid_now = serializers.SerializerMethodField()
    coverage_amount_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = Insurance
        fields = [
            'id', 'insurance_company', 'policy_number', 'group_number',
            'coverage_type', 'coverage_type_display', 'coverage_amount',
            'coverage_amount_formatted', 'deductible', 'co_pay_percentage',
            'start_date', 'end_date', 'is_active', 'is_valid_now',
            'pre_authorization_required', 'network_hospitals', 'exclusions',
            'created_at'
        ]
        read_only_fields = ['created_at']
    
    def get_coverage_type_display(self, obj):
        return obj.get_coverage_type_display()
    
    def get_is_valid_now(self, obj):
        return obj.is_valid()
    
    def get_coverage_amount_formatted(self, obj):
        return f"${obj.coverage_amount:.2f}"


class PatientSerializer(serializers.ModelSerializer):
    user_account = UserBasicSerializer(read_only=True)
    user_account_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='user_account',
        required=False, allow_null=True
    )
    registered_moze = MozeBasicSerializer(read_only=True)
    registered_moze_id = serializers.PrimaryKeyRelatedField(
        queryset=Moze.objects.all(), write_only=True, source='registered_moze',
        required=False, allow_null=True
    )
    full_name = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    gender_display = serializers.SerializerMethodField()
    blood_group_display = serializers.SerializerMethodField()
    emergency_contacts = EmergencyContactSerializer(many=True, read_only=True)
    insurance_policies = InsuranceSerializer(many=True, read_only=True)
    total_appointments = serializers.SerializerMethodField()
    
    class Meta:
        model = Patient
        fields = [
            'id', 'its_id', 'first_name', 'last_name', 'arabic_name', 'full_name',
            'date_of_birth', 'age', 'gender', 'gender_display', 'phone_number',
            'email', 'address', 'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relationship', 'blood_group', 'blood_group_display',
            'allergies', 'chronic_conditions', 'current_medications',
            'registered_moze', 'registered_moze_id', 'registration_date',
            'is_active', 'user_account', 'user_account_id', 'emergency_contacts',
            'insurance_policies', 'total_appointments', 'created_at', 'updated_at'
        ]
        read_only_fields = ['registration_date', 'created_at', 'updated_at']
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_age(self, obj):
        return obj.get_age()
    
    def get_gender_display(self, obj):
        return obj.get_gender_display()
    
    def get_blood_group_display(self, obj):
        return obj.get_blood_group_display() if obj.blood_group else None
    
    def get_total_appointments(self, obj):
        return obj.appointments.count()


class PatientCreateSerializer(serializers.ModelSerializer):
    user_account_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user_account',
        required=False, allow_null=True
    )
    registered_moze_id = serializers.PrimaryKeyRelatedField(
        queryset=Moze.objects.all(), source='registered_moze',
        required=False, allow_null=True
    )
    
    class Meta:
        model = Patient
        fields = [
            'its_id', 'first_name', 'last_name', 'arabic_name', 'date_of_birth',
            'gender', 'phone_number', 'email', 'address', 'emergency_contact_name',
            'emergency_contact_phone', 'emergency_contact_relationship',
            'blood_group', 'allergies', 'chronic_conditions', 'current_medications',
            'registered_moze_id', 'user_account_id'
        ]


# Appointment serializers
class AppointmentSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(), write_only=True, source='patient'
    )
    doctor = DoctorSerializer(read_only=True)
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all(), write_only=True, source='doctor'
    )
    moze = MozeBasicSerializer(read_only=True)
    moze_id = serializers.PrimaryKeyRelatedField(
        queryset=Moze.objects.all(), write_only=True, source='moze'
    )
    service = MedicalServiceSerializer(read_only=True)
    service_id = serializers.PrimaryKeyRelatedField(
        queryset=MedicalService.objects.all(), write_only=True, source='service',
        required=False, allow_null=True
    )
    booked_by = UserBasicSerializer(read_only=True)
    booked_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='booked_by',
        required=False, allow_null=True
    )
    status_display = serializers.SerializerMethodField()
    appointment_type_display = serializers.SerializerMethodField()
    booking_method_display = serializers.SerializerMethodField()
    is_today = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'patient', 'patient_id', 'doctor', 'doctor_id', 'moze', 'moze_id',
            'service', 'service_id', 'appointment_date', 'appointment_time',
            'duration_minutes', 'reason', 'symptoms', 'notes', 'status',
            'status_display', 'appointment_type', 'appointment_type_display',
            'booked_by', 'booked_by_id', 'booking_method', 'booking_method_display',
            'reminder_sent', 'reminder_sent_at', 'is_today', 'is_overdue',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_status_display(self, obj):
        return obj.get_status_display()
    
    def get_appointment_type_display(self, obj):
        return obj.get_appointment_type_display()
    
    def get_booking_method_display(self, obj):
        return obj.get_booking_method_display()
    
    def get_is_today(self, obj):
        return obj.is_today()
    
    def get_is_overdue(self, obj):
        return obj.is_overdue()


class AppointmentCreateSerializer(serializers.ModelSerializer):
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(), source='patient'
    )
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all(), source='doctor'
    )
    moze_id = serializers.PrimaryKeyRelatedField(
        queryset=Moze.objects.all(), source='moze'
    )
    service_id = serializers.PrimaryKeyRelatedField(
        queryset=MedicalService.objects.all(), source='service',
        required=False, allow_null=True
    )
    booked_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='booked_by',
        required=False, allow_null=True
    )
    
    class Meta:
        model = Appointment
        fields = [
            'patient_id', 'doctor_id', 'moze_id', 'service_id', 'appointment_date',
            'appointment_time', 'duration_minutes', 'reason', 'symptoms', 'notes',
            'appointment_type', 'booked_by_id', 'booking_method'
        ]


# Medical Records and related serializers
class VitalSignsSerializer(serializers.ModelSerializer):
    recorded_by = UserBasicSerializer(read_only=True)
    recorded_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='recorded_by'
    )
    bmi_calculated = serializers.SerializerMethodField()
    blood_pressure = serializers.SerializerMethodField()
    
    class Meta:
        model = VitalSigns
        fields = [
            'id', 'patient', 'medical_record', 'systolic_bp', 'diastolic_bp', 
            'blood_pressure', 'heart_rate', 'respiratory_rate', 'temperature', 
            'oxygen_saturation', 'weight', 'height', 'bmi', 'bmi_calculated', 
            'pain_scale', 'notes', 'recorded_by', 'recorded_by_id', 'recorded_at'
        ]
        read_only_fields = ['recorded_at']
    
    def get_bmi_calculated(self, obj):
        return obj.calculate_bmi()
    
    def get_blood_pressure(self, obj):
        if obj.systolic_bp and obj.diastolic_bp:
            return f"{obj.systolic_bp}/{obj.diastolic_bp}"
        return None


class PrescriptionSerializer(serializers.ModelSerializer):
    doctor = DoctorSerializer(read_only=True)
    patient = PatientSerializer(read_only=True)
    
    class Meta:
        model = Prescription
        fields = [
            'id', 'prescription_date', 'medication_name', 'dosage', 'frequency',
            'duration', 'quantity', 'instructions', 'warnings', 'is_active',
            'is_dispensed', 'dispensed_date', 'dispensed_by', 'doctor',
            'patient', 'created_at'
        ]
        read_only_fields = ['prescription_date', 'created_at']


class LabTestSerializer(serializers.ModelSerializer):
    doctor = DoctorSerializer(read_only=True)
    patient = PatientSerializer(read_only=True)
    test_category_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    days_since_ordered = serializers.SerializerMethodField()
    
    class Meta:
        model = LabTest
        fields = [
            'id', 'test_name', 'test_category', 'test_category_display',
            'test_code', 'ordered_date', 'sample_collected_date', 'result_date',
            'status', 'status_display', 'result_text', 'result_file',
            'normal_range', 'is_abnormal', 'lab_name', 'lab_technician',
            'doctor_notes', 'lab_notes', 'days_since_ordered', 'doctor',
            'patient', 'created_at', 'updated_at'
        ]
        read_only_fields = ['ordered_date', 'created_at', 'updated_at']
    
    def get_test_category_display(self, obj):
        return obj.get_test_category_display()
    
    def get_status_display(self, obj):
        return obj.get_status_display()
    
    def get_days_since_ordered(self, obj):
        return (timezone.now().date() - obj.ordered_date).days


class MedicalRecordSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(), write_only=True, source='patient'
    )
    doctor = DoctorSerializer(read_only=True)
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all(), write_only=True, source='doctor'
    )
    appointment = AppointmentSerializer(read_only=True)
    appointment_id = serializers.PrimaryKeyRelatedField(
        queryset=Appointment.objects.all(), write_only=True, source='appointment',
        required=False, allow_null=True
    )
    moze = MozeBasicSerializer(read_only=True)
    moze_id = serializers.PrimaryKeyRelatedField(
        queryset=Moze.objects.all(), write_only=True, source='moze'
    )
    prescriptions = PrescriptionSerializer(many=True, read_only=True)
    lab_tests = LabTestSerializer(many=True, read_only=True)
    vital_signs_records = VitalSignsSerializer(many=True, read_only=True)
    
    class Meta:
        model = MedicalRecord
        fields = [
            'id', 'patient', 'patient_id', 'doctor', 'doctor_id', 'appointment',
            'appointment_id', 'moze', 'moze_id', 'consultation_date',
            'chief_complaint', 'history_of_present_illness', 'past_medical_history',
            'family_history', 'social_history', 'vital_signs', 'physical_examination',
            'diagnosis', 'differential_diagnosis', 'treatment_plan',
            'medications_prescribed', 'lab_tests_ordered', 'imaging_ordered',
            'referrals', 'follow_up_required', 'follow_up_date',
            'follow_up_instructions', 'patient_education', 'doctor_notes',
            'prescriptions', 'lab_tests', 'vital_signs_records',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['consultation_date', 'created_at', 'updated_at']


class MedicalRecordCreateSerializer(serializers.ModelSerializer):
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(), source='patient'
    )
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all(), source='doctor'
    )
    appointment_id = serializers.PrimaryKeyRelatedField(
        queryset=Appointment.objects.all(), source='appointment',
        required=False, allow_null=True
    )
    moze_id = serializers.PrimaryKeyRelatedField(
        queryset=Moze.objects.all(), source='moze'
    )
    
    class Meta:
        model = MedicalRecord
        fields = [
            'patient_id', 'doctor_id', 'appointment_id', 'moze_id',
            'chief_complaint', 'history_of_present_illness', 'past_medical_history',
            'family_history', 'social_history', 'vital_signs', 'physical_examination',
            'diagnosis', 'differential_diagnosis', 'treatment_plan',
            'medications_prescribed', 'lab_tests_ordered', 'imaging_ordered',
            'referrals', 'follow_up_required', 'follow_up_date',
            'follow_up_instructions', 'patient_education', 'doctor_notes'
        ]


# Room serializers
class RoomSerializer(serializers.ModelSerializer):
    hospital = serializers.StringRelatedField(read_only=True)
    hospital_id = serializers.PrimaryKeyRelatedField(
        queryset=Hospital.objects.all(), write_only=True, source='hospital'
    )
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), write_only=True, source='department'
    )
    room_type_display = serializers.SerializerMethodField()
    current_occupancy = serializers.SerializerMethodField()
    
    class Meta:
        model = Room
        fields = [
            'id', 'hospital', 'hospital_id', 'department', 'department_id',
            'room_number', 'room_type', 'room_type_display', 'capacity',
            'floor_number', 'is_available', 'is_operational', 'current_occupancy',
            'has_ac', 'has_wifi', 'has_tv'
        ]
    
    def get_room_type_display(self, obj):
        return obj.get_room_type_display()
    
    def get_current_occupancy(self, obj):
        return obj.admissions.filter(status='admitted').count()


# Medication and Treatment serializers
class MedicationSerializer(serializers.ModelSerializer):
    medication_type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Medication
        fields = [
            'id', 'name', 'generic_name', 'brand_name', 'medication_type',
            'medication_type_display', 'strength', 'manufacturer',
            'side_effects', 'contraindications', 'storage_conditions',
            'is_active', 'requires_prescription', 'created_at'
        ]
        read_only_fields = ['created_at']
    
    def get_medication_type_display(self, obj):
        return obj.get_medication_type_display()


class TreatmentMedicationSerializer(serializers.ModelSerializer):
    medication = MedicationSerializer(read_only=True)
    medication_id = serializers.PrimaryKeyRelatedField(
        queryset=Medication.objects.all(), write_only=True, source='medication'
    )
    
    class Meta:
        model = TreatmentMedication
        fields = [
            'id', 'medication', 'medication_id', 'dosage', 'frequency',
            'duration', 'instructions'
        ]


class TreatmentPlanSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(), write_only=True, source='patient'
    )
    doctor = DoctorSerializer(read_only=True)
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all(), write_only=True, source='doctor'
    )
    medical_record = MedicalRecordSerializer(read_only=True)
    medical_record_id = serializers.PrimaryKeyRelatedField(
        queryset=MedicalRecord.objects.all(), write_only=True, source='medical_record'
    )
    treatment_medications = TreatmentMedicationSerializer(many=True, read_only=True, source='treatmentmedication_set')
    status_display = serializers.SerializerMethodField()
    duration_days = serializers.SerializerMethodField()
    
    class Meta:
        model = TreatmentPlan
        fields = [
            'id', 'patient', 'patient_id', 'doctor', 'doctor_id',
            'medical_record', 'medical_record_id', 'plan_name', 'description',
            'objectives', 'start_date', 'end_date', 'duration_weeks',
            'duration_days', 'therapies', 'lifestyle_changes',
            'dietary_restrictions', 'monitoring_schedule', 'success_criteria',
            'status', 'status_display', 'treatment_medications',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_status_display(self, obj):
        return obj.get_status_display()
    
    def get_duration_days(self, obj):
        if obj.start_date and obj.end_date:
            return (obj.end_date - obj.start_date).days
        return None


# Admission and Discharge serializers
class AdmissionSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(), write_only=True, source='patient'
    )
    hospital = serializers.StringRelatedField(read_only=True)
    hospital_id = serializers.PrimaryKeyRelatedField(
        queryset=Hospital.objects.all(), write_only=True, source='hospital'
    )
    room = RoomSerializer(read_only=True)
    room_id = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.all(), write_only=True, source='room'
    )
    admitting_doctor = DoctorSerializer(read_only=True)
    admitting_doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all(), write_only=True, source='admitting_doctor'
    )
    admission_type_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    length_of_stay = serializers.SerializerMethodField()
    
    class Meta:
        model = Admission
        fields = [
            'id', 'patient', 'patient_id', 'hospital', 'hospital_id', 'room',
            'room_id', 'admitting_doctor', 'admitting_doctor_id',
            'admission_type', 'admission_type_display', 'admission_date',
            'expected_discharge_date', 'chief_complaint', 'diagnosis',
            'treatment_plan', 'status', 'status_display', 'bed_number',
            'admission_notes', 'length_of_stay', 'created_at'
        ]
        read_only_fields = ['created_at']
    
    def get_admission_type_display(self, obj):
        return obj.get_admission_type_display()
    
    def get_status_display(self, obj):
        return obj.get_status_display()
    
    def get_length_of_stay(self, obj):
        if obj.status == 'admitted':
            return (timezone.now().date() - obj.admission_date.date()).days
        return None


class DischargeSerializer(serializers.ModelSerializer):
    admission = AdmissionSerializer(read_only=True)
    admission_id = serializers.PrimaryKeyRelatedField(
        queryset=Admission.objects.all(), write_only=True, source='admission'
    )
    discharging_doctor = DoctorSerializer(read_only=True)
    discharging_doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all(), write_only=True, source='discharging_doctor'
    )
    discharge_type_display = serializers.SerializerMethodField()
    condition_at_discharge_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Discharge
        fields = [
            'id', 'admission', 'admission_id', 'discharging_doctor',
            'discharging_doctor_id', 'discharge_date', 'discharge_type',
            'discharge_type_display', 'final_diagnosis', 'treatment_summary',
            'discharge_medications', 'follow_up_instructions', 'next_appointment',
            'condition_at_discharge', 'condition_at_discharge_display',
            'discharge_summary', 'discharge_notes', 'created_at'
        ]
        read_only_fields = ['created_at']
    
    def get_discharge_type_display(self, obj):
        return obj.get_discharge_type_display()
    
    def get_condition_at_discharge_display(self, obj):
        return obj.get_condition_at_discharge_display()


# Inventory serializers
class InventoryItemSerializer(serializers.ModelSerializer):
    low_stock_alert = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    stock_value = serializers.SerializerMethodField()
    
    class Meta:
        model = InventoryItem
        fields = [
            'id', 'name', 'description', 'item_code', 'category',
            'current_stock', 'minimum_stock', 'maximum_stock', 'unit',
            'unit_cost', 'supplier', 'expiry_date', 'last_restocked',
            'is_active', 'requires_prescription', 'low_stock_alert',
            'is_expired', 'stock_value', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_low_stock_alert(self, obj):
        return obj.is_low_stock()
    
    def get_is_expired(self, obj):
        return obj.is_expired()
    
    def get_stock_value(self, obj):
        return float(obj.current_stock * obj.unit_cost)


class InventorySerializer(serializers.ModelSerializer):
    hospital = serializers.StringRelatedField(read_only=True)
    hospital_id = serializers.PrimaryKeyRelatedField(
        queryset=Hospital.objects.all(), write_only=True, source='hospital'
    )
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), write_only=True, source='department'
    )
    items = InventoryItemSerializer(many=True, read_only=True)
    inventory_type_display = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()
    
    class Meta:
        model = Inventory
        fields = [
            'id', 'hospital', 'hospital_id', 'name', 'description',
            'inventory_type', 'inventory_type_display', 'storage_location',
            'department', 'department_id', 'total_items', 'items', 'created_at'
        ]
        read_only_fields = ['created_at']
    
    def get_inventory_type_display(self, obj):
        return obj.get_inventory_type_display()
    
    def get_total_items(self, obj):
        return obj.items.count()


# Statistics serializers
class HospitalStatsSerializer(serializers.Serializer):
    total_hospitals = serializers.IntegerField()
    active_hospitals = serializers.IntegerField()
    total_beds = serializers.IntegerField()
    occupied_beds = serializers.IntegerField()
    bed_occupancy_rate = serializers.FloatField()


class PatientStatsSerializer(serializers.Serializer):
    total_patients = serializers.IntegerField()
    active_patients = serializers.IntegerField()
    new_patients_this_month = serializers.IntegerField()
    patients_by_gender = serializers.DictField()
    patients_by_blood_group = serializers.DictField()


class AppointmentStatsSerializer(serializers.Serializer):
    total_appointments = serializers.IntegerField()
    appointments_today = serializers.IntegerField()
    pending_appointments = serializers.IntegerField()
    completed_appointments = serializers.IntegerField()
    appointments_by_status = serializers.DictField()


# Search serializers
class PatientSearchSerializer(serializers.Serializer):
    its_id = serializers.CharField(required=False)
    name = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=False)
    blood_group = serializers.CharField(required=False)
    registered_moze = serializers.IntegerField(required=False)


class AppointmentSearchSerializer(serializers.Serializer):
    patient_id = serializers.IntegerField(required=False)
    doctor_id = serializers.IntegerField(required=False)
    status = serializers.CharField(required=False)
    appointment_type = serializers.CharField(required=False)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)


class DoctorSearchSerializer(serializers.Serializer):
    specialization = serializers.CharField(required=False)
    hospital_id = serializers.IntegerField(required=False)
    department_id = serializers.IntegerField(required=False)
    is_available = serializers.BooleanField(required=False)
    is_emergency_doctor = serializers.BooleanField(required=False)