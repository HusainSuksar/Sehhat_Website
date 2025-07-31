from django.contrib import admin
from .models import (
    MedicalService, Patient, Appointment, MedicalRecord, Prescription,
    LabTest, VitalSigns, Hospital, Department, Doctor, HospitalStaff,
    Room, Medication, LabResult, Admission, Discharge, TreatmentPlan,
    TreatmentMedication, Inventory, InventoryItem, EmergencyContact, Insurance
)


@admin.register(MedicalService)
class MedicalServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'duration_minutes', 'cost', 'is_active']
    list_filter = ['category', 'is_active', 'requires_appointment']
    search_fields = ['name', 'description']
    ordering = ['category', 'name']


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'its_id', 'gender', 'blood_group', 'is_active', 'registration_date']
    list_filter = ['gender', 'blood_group', 'is_active', 'registration_date']
    search_fields = ['first_name', 'last_name', 'arabic_name', 'its_id', 'phone_number']
    readonly_fields = ['registration_date', 'created_at', 'updated_at']
    ordering = ['last_name', 'first_name']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'appointment_date', 'appointment_time', 'status', 'appointment_type']
    list_filter = ['status', 'appointment_type', 'appointment_date', 'doctor__hospital']
    search_fields = ['patient__first_name', 'patient__last_name', 'doctor__user__first_name', 'reason']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-appointment_date', '-appointment_time']


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'consultation_date', 'diagnosis']
    list_filter = ['consultation_date', 'follow_up_required', 'doctor__hospital']
    search_fields = ['patient__first_name', 'patient__last_name', 'diagnosis', 'chief_complaint']
    readonly_fields = ['consultation_date', 'created_at', 'updated_at']
    ordering = ['-consultation_date']


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'medication_name', 'prescription_date', 'is_active', 'is_dispensed']
    list_filter = ['is_active', 'is_dispensed', 'prescription_date']
    search_fields = ['patient__first_name', 'patient__last_name', 'medication_name']
    readonly_fields = ['prescription_date', 'created_at']
    ordering = ['-prescription_date']


@admin.register(LabTest)
class LabTestAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'test_name', 'test_category', 'status', 'ordered_date']
    list_filter = ['test_category', 'status', 'is_abnormal', 'ordered_date']
    search_fields = ['patient__first_name', 'patient__last_name', 'test_name']
    readonly_fields = ['ordered_date', 'created_at', 'updated_at']
    ordering = ['-ordered_date']


@admin.register(VitalSigns)
class VitalSignsAdmin(admin.ModelAdmin):
    list_display = ['patient', 'recorded_by', 'systolic_bp', 'diastolic_bp', 'heart_rate', 'recorded_at']
    list_filter = ['recorded_at']
    search_fields = ['patient__first_name', 'patient__last_name']
    readonly_fields = ['recorded_at']
    ordering = ['-recorded_at']


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ['name', 'hospital_type', 'total_beds', 'available_beds', 'is_active', 'is_emergency_capable']
    list_filter = ['hospital_type', 'is_active', 'is_emergency_capable', 'has_pharmacy', 'has_laboratory']
    search_fields = ['name', 'description', 'address']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'hospital', 'head', 'floor_number', 'is_active']
    list_filter = ['is_active', 'hospital']
    search_fields = ['name', 'hospital__name']
    ordering = ['hospital', 'name']


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['user', 'license_number', 'specialization', 'hospital', 'department', 'is_available']
    list_filter = ['specialization', 'is_available', 'is_emergency_doctor', 'hospital']
    search_fields = ['user__first_name', 'user__last_name', 'license_number', 'specialization']
    ordering = ['user__last_name', 'user__first_name']


@admin.register(HospitalStaff)
class HospitalStaffAdmin(admin.ModelAdmin):
    list_display = ['user', 'hospital', 'department', 'staff_type', 'employee_id', 'is_active']
    list_filter = ['staff_type', 'is_active', 'shift', 'hospital']
    search_fields = ['user__first_name', 'user__last_name', 'employee_id']
    ordering = ['user__last_name', 'user__first_name']


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'hospital', 'department', 'room_type', 'capacity', 'is_available']
    list_filter = ['room_type', 'is_available', 'is_operational', 'hospital']
    search_fields = ['room_number', 'hospital__name']
    ordering = ['hospital', 'floor_number', 'room_number']


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ['name', 'medication_type', 'strength', 'manufacturer', 'is_active']
    list_filter = ['medication_type', 'is_active', 'requires_prescription']
    search_fields = ['name', 'generic_name', 'brand_name']
    ordering = ['name']


@admin.register(LabResult)
class LabResultAdmin(admin.ModelAdmin):
    list_display = ['lab_test', 'is_normal', 'completed_at', 'reviewed_at']
    list_filter = ['is_normal', 'quality_control_passed', 'completed_at']
    search_fields = ['lab_test__test_name', 'lab_test__patient__first_name']
    readonly_fields = ['completed_at']
    ordering = ['-completed_at']


@admin.register(Admission)
class AdmissionAdmin(admin.ModelAdmin):
    list_display = ['patient', 'hospital', 'admission_type', 'status', 'admission_date']
    list_filter = ['admission_type', 'status', 'admission_date']
    search_fields = ['patient__first_name', 'patient__last_name', 'chief_complaint']
    readonly_fields = ['created_at']
    ordering = ['-admission_date']


@admin.register(Discharge)
class DischargeAdmin(admin.ModelAdmin):
    list_display = ['admission', 'discharging_doctor', 'discharge_date', 'discharge_type', 'condition_at_discharge']
    list_filter = ['discharge_type', 'condition_at_discharge', 'discharge_date']
    search_fields = ['admission__patient__first_name', 'admission__patient__last_name']
    readonly_fields = ['created_at']
    ordering = ['-discharge_date']


@admin.register(TreatmentPlan)
class TreatmentPlanAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'plan_name', 'status', 'start_date']
    list_filter = ['status', 'start_date']
    search_fields = ['patient__first_name', 'patient__last_name', 'plan_name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(TreatmentMedication)
class TreatmentMedicationAdmin(admin.ModelAdmin):
    list_display = ['treatment_plan', 'medication', 'dosage', 'frequency', 'duration']
    search_fields = ['treatment_plan__plan_name', 'medication__name']
    ordering = ['treatment_plan', 'medication']


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'hospital', 'department', 'inventory_type']
    list_filter = ['inventory_type', 'hospital']
    search_fields = ['name', 'description', 'hospital__name']
    ordering = ['hospital', 'name']


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'inventory', 'current_stock', 'minimum_stock', 'unit_cost', 'is_active']
    list_filter = ['is_active', 'requires_prescription', 'inventory__inventory_type']
    search_fields = ['name', 'item_code', 'category']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']


@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ['patient', 'name', 'relationship', 'phone_primary', 'is_primary']
    list_filter = ['is_primary', 'relationship']
    search_fields = ['patient__first_name', 'patient__last_name', 'name']
    ordering = ['patient', 'priority_order']


@admin.register(Insurance)
class InsuranceAdmin(admin.ModelAdmin):
    list_display = ['patient', 'insurance_company', 'policy_number', 'coverage_type', 'is_active']
    list_filter = ['coverage_type', 'is_active', 'pre_authorization_required']
    search_fields = ['patient__first_name', 'patient__last_name', 'insurance_company', 'policy_number']
    readonly_fields = ['created_at']
    ordering = ['-start_date']
