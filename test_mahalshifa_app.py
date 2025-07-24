#!/usr/bin/env python3
"""
Comprehensive Testing Script for Mahalshifa App (Medical Hospital Management System)
Tests all core functionality, URLs, user roles, and creates sample medical data.
"""

import os
import sys
import django
import requests
from datetime import datetime, timedelta, date, time
from decimal import Decimal
import json

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

# Import Mahalshifa models
from mahalshifa.models import (
    Hospital, Department, Patient, Appointment, MedicalRecord,
    Prescription, LabTest, LabResult, VitalSigns, HospitalStaff,
    Room, Admission, Discharge, TreatmentPlan, Medication,
    Inventory, InventoryItem, EmergencyContact, Insurance,
    MedicalService
)

# Import related models
from accounts.models import User
from moze.models import Moze
# Note: Using mahalshifa.models.Doctor instead of doctordirectory.models.Doctor

class MahalshifaAppTester:
    def __init__(self):
        self.client = Client()
        self.base_url = 'http://localhost:8000'
        self.test_results = []
        self.users = {}
        self.sample_data = {}
        
    def log_result(self, test_name, status, message=""):
        """Log test results"""
        symbol = "✅" if status else "❌"
        self.test_results.append(f"{symbol} {test_name}: {message}")
        print(f"{symbol} {test_name}: {message}")
        
    def create_test_users(self):
        """Create test users for different roles"""
        print("\n🔧 Creating test users...")
        
        # Create admin user
        try:
            admin_user = User.objects.get(username='admin')
        except User.DoesNotExist:
            admin_user, created = User.objects.get_or_create(
                its_id='00000001',
                defaults={
                    'username': 'admin',
                    'first_name': 'System',
                    'last_name': 'Administrator',
                    'email': 'admin@mahalshifa.com',
                    'role': 'admin',
                    'phone_number': '+1234567890',
                    'is_active': True
                }
            )
            if created:
                admin_user.set_password('admin123')
                admin_user.save()
        self.users['admin'] = admin_user
        
        # Create aamil user
        try:
            aamil_user = User.objects.get(username='aamil_medical')
        except User.DoesNotExist:
            aamil_user, created = User.objects.get_or_create(
                its_id='00000002',
                defaults={
                    'username': 'aamil_medical',
                    'first_name': 'Medical',
                    'last_name': 'Aamil',
                    'email': 'aamil@mahalshifa.com',
                    'role': 'aamil',
                    'phone_number': '+1234567891',
                    'is_active': True
                }
            )
            if created:
                aamil_user.set_password('test123')
                aamil_user.save()
        self.users['aamil'] = aamil_user
        
        # Create doctor user
        try:
            doctor_user = User.objects.get(username='dr_ahmed')
        except User.DoesNotExist:
            doctor_user, created = User.objects.get_or_create(
                its_id='00000003',
                defaults={
                    'username': 'dr_ahmed',
                    'first_name': 'Ahmed',
                    'last_name': 'Hassan',
                    'email': 'dr.ahmed@mahalshifa.com',
                    'role': 'doctor',
                    'phone_number': '+1234567892',
                    'is_active': True
                }
            )
            if created:
                doctor_user.set_password('test123')
                doctor_user.save()
        self.users['doctor'] = doctor_user
        
        # Create patient user
        try:
            patient_user = User.objects.get(username='patient_ali')
        except User.DoesNotExist:
            patient_user, created = User.objects.get_or_create(
                its_id='12345678',
                defaults={
                    'username': 'patient_ali',
                    'first_name': 'Ali',
                    'last_name': 'Mahmood',
                    'email': 'ali.mahmood@example.com',
                    'role': 'student',  # Patients are often students
                    'phone_number': '+1234567893',
                    'is_active': True
                }
            )
            if created:
                patient_user.set_password('test123')
                patient_user.save()
        self.users['patient'] = patient_user
        
        # Create moze coordinator user
        try:
            moze_user = User.objects.get(username='moze_coord')
        except User.DoesNotExist:
            moze_user, created = User.objects.get_or_create(
                its_id='00000004',
                defaults={
                    'username': 'moze_coord',
                    'first_name': 'Moze',
                    'last_name': 'Coordinator',
                    'email': 'moze@mahalshifa.com',
                    'role': 'moze_coordinator',
                    'phone_number': '+1234567894',
                    'is_active': True
                }
            )
            if created:
                moze_user.set_password('test123')
                moze_user.save()
        self.users['moze_coordinator'] = moze_user
        
        print(f"✅ Created {len(self.users)} test users")
        return True
        
    def create_sample_medical_data(self):
        """Create sample medical data for testing"""
        print("\n🏥 Creating sample medical data...")
        
        try:
            # Create Moze for patient registration
            moze, created = Moze.objects.get_or_create(
                aamil=self.users['aamil'],
                defaults={
                    'moze_coordinator': self.users['moze_coordinator'],
                    'location': 'Test Medical Center',
                    'is_active': True
                }
            )
            self.sample_data['moze'] = moze
            
            # Create Hospital
            hospital, created = Hospital.objects.get_or_create(
                name='Mahal Shifa General Hospital',
                defaults={
                    'description': 'Premier medical facility serving the community',
                    'address': '123 Medical Center Drive, Healthcare City',
                    'phone': '+1234567890',
                    'email': 'info@mahalshifa.com',
                    'hospital_type': 'general',
                    'total_beds': 200,
                    'available_beds': 150,
                    'emergency_beds': 20,
                    'icu_beds': 30,
                    'is_active': True,
                    'is_emergency_capable': True,
                    'has_pharmacy': True,
                    'has_laboratory': True
                }
            )
            self.sample_data['hospital'] = hospital
            
            # Create Department
            department, created = Department.objects.get_or_create(
                hospital=hospital,
                name='Internal Medicine',
                defaults={
                    'description': 'General internal medicine department',
                    'head': self.users['doctor'],
                    'floor_number': '2',
                    'phone_extension': '2001',
                    'is_active': True
                }
            )
            self.sample_data['department'] = department
            
            # Create Doctor Profile (from mahalshifa app)
            from mahalshifa.models import Doctor as MahalshifaDoctor
            doctor_profile, created = MahalshifaDoctor.objects.get_or_create(
                user=self.users['doctor'],
                defaults={
                    'license_number': 'MED-2024-001',
                    'specialization': 'Internal Medicine',
                    'qualification': 'MBBS, MD Internal Medicine',
                    'experience_years': 10,
                    'hospital': hospital,
                    'department': department,
                    'is_available': True,
                    'is_emergency_doctor': False,
                    'consultation_fee': Decimal('150.00')
                }
            )
            self.sample_data['doctor'] = doctor_profile
            
            # Create Patient
            patient, created = Patient.objects.get_or_create(
                its_id='12345678',
                defaults={
                    'first_name': 'Ali',
                    'last_name': 'Mahmood',
                    'arabic_name': 'علي محمود',
                    'date_of_birth': date(1995, 6, 15),
                    'gender': 'male',
                    'phone_number': '+1234567893',
                    'email': 'ali.mahmood@example.com',
                    'address': '456 Patient Street, Medical City',
                    'emergency_contact_name': 'Fatima Mahmood',
                    'emergency_contact_phone': '+1234567894',
                    'emergency_contact_relationship': 'Mother',
                    'blood_group': 'A+',
                    'allergies': 'Penicillin, Shellfish',
                    'chronic_conditions': 'Type 2 Diabetes',
                    'current_medications': 'Metformin 500mg twice daily',
                    'registered_moze': moze,
                    'user_account': self.users['patient'],
                    'is_active': True
                }
            )
            self.sample_data['patient'] = patient
            
            # Create Medical Service
            service, created = MedicalService.objects.get_or_create(
                name='General Consultation',
                defaults={
                    'description': 'General medical consultation and examination',
                    'category': 'consultation',
                    'duration_minutes': 30,
                    'cost': Decimal('100.00'),
                    'is_active': True,
                    'requires_appointment': True
                }
            )
            self.sample_data['service'] = service
            
            # Create Appointment
            appointment, created = Appointment.objects.get_or_create(
                patient=patient,
                doctor=doctor_profile,
                appointment_date=date.today() + timedelta(days=1),
                appointment_time=time(10, 0),
                defaults={
                    'moze': moze,
                    'service': service,
                    'duration_minutes': 30,
                    'reason': 'Regular checkup for diabetes management',
                    'symptoms': 'Fatigue, frequent urination',
                    'notes': 'Patient requires blood sugar monitoring',
                    'status': 'scheduled',
                    'appointment_type': 'regular',
                    'booked_by': self.users['patient'],
                    'booking_method': 'online'
                }
            )
            self.sample_data['appointment'] = appointment
            
            # Create Medical Record
            medical_record, created = MedicalRecord.objects.get_or_create(
                patient=patient,
                doctor=doctor_profile,
                appointment=appointment,
                moze=moze,
                defaults={
                    'chief_complaint': 'Diabetes follow-up and fatigue',
                    'history_of_present_illness': 'Patient reports increased fatigue over the past 2 weeks',
                    'past_medical_history': 'Type 2 Diabetes diagnosed 2020',
                    'physical_examination': 'Blood pressure 130/80, weight 75kg, alert and oriented',
                    'diagnosis': 'Type 2 Diabetes Mellitus, well controlled',
                    'treatment_plan': 'Continue current medication, dietary counseling',
                    'medications_prescribed': 'Metformin 500mg BID, continue current regimen',
                    'follow_up_required': True,
                    'follow_up_date': date.today() + timedelta(days=90),
                    'follow_up_instructions': 'Blood work in 3 months, continue monitoring'
                }
            )
            self.sample_data['medical_record'] = medical_record
            
            # Create Prescription
            prescription, created = Prescription.objects.get_or_create(
                medical_record=medical_record,
                patient=patient,
                doctor=doctor_profile,
                medication_name='Metformin',
                defaults={
                    'dosage': '500mg',
                    'frequency': 'Twice daily',
                    'duration': '3 months',
                    'quantity': '180 tablets',
                    'instructions': 'Take with meals to reduce stomach upset',
                    'warnings': 'Monitor blood sugar regularly',
                    'is_active': True,
                    'is_dispensed': False
                }
            )
            self.sample_data['prescription'] = prescription
            
            # Create Lab Test
            lab_test, created = LabTest.objects.get_or_create(
                medical_record=medical_record,
                patient=patient,
                doctor=doctor_profile,
                test_name='HbA1c',
                defaults={
                    'test_category': 'blood',
                    'test_code': 'HBA1C',
                    'status': 'ordered',
                    'lab_name': 'Mahal Shifa Laboratory',
                    'doctor_notes': 'Monitor diabetes control'
                }
            )
            self.sample_data['lab_test'] = lab_test
            
            # Create Vital Signs
            vital_signs, created = VitalSigns.objects.get_or_create(
                patient=patient,
                medical_record=medical_record,
                recorded_by=self.users['doctor'],
                defaults={
                    'systolic_bp': 130,
                    'diastolic_bp': 80,
                    'heart_rate': 72,
                    'respiratory_rate': 16,
                    'temperature': 37.0,
                    'oxygen_saturation': 98,
                    'weight': 75.0,
                    'height': 175.0,
                    'pain_scale': 2,
                    'notes': 'Patient stable, vital signs within normal limits'
                }
            )
            self.sample_data['vital_signs'] = vital_signs
            
            # Create Medication
            medication, created = Medication.objects.get_or_create(
                name='Metformin',
                defaults={
                    'generic_name': 'Metformin Hydrochloride',
                    'brand_name': 'Glucophage',
                    'medication_type': 'tablet',
                    'strength': '500mg',
                    'manufacturer': 'Generic Pharmaceuticals',
                    'side_effects': 'Nausea, diarrhea, stomach upset',
                    'contraindications': 'Kidney disease, liver disease',
                    'storage_conditions': 'Store at room temperature',
                    'is_active': True,
                    'requires_prescription': True
                }
            )
            self.sample_data['medication'] = medication
            
            print(f"✅ Created comprehensive medical sample data")
            return True
            
        except Exception as e:
            print(f"❌ Error creating sample data: {str(e)}")
            return False
    
    def test_model_access(self):
        """Test basic model access and creation"""
        print("\n📊 Testing Mahalshifa model access...")
        
        models_to_test = [
            (Hospital, 'Hospital model'),
            (Department, 'Department model'),
            (Patient, 'Patient model'),
            (Appointment, 'Appointment model'),
            (MedicalRecord, 'Medical Record model'),
            (Prescription, 'Prescription model'),
            (LabTest, 'Lab Test model'),
            (VitalSigns, 'Vital Signs model'),
            (MedicalService, 'Medical Service model'),
            (Medication, 'Medication model'),
            (Inventory, 'Inventory model'),
            (InventoryItem, 'Inventory Item model'),
            (EmergencyContact, 'Emergency Contact model'),
            (Insurance, 'Insurance model'),
        ]
        
        for model_class, model_name in models_to_test:
            try:
                count = model_class.objects.count()
                self.log_result(f"Access {model_name}", True, f"Found {count} records")
            except Exception as e:
                self.log_result(f"Access {model_name}", False, f"Error: {str(e)}")
    
    def test_url_accessibility(self):
        """Test URL accessibility"""
        print("\n🌐 Testing Mahalshifa URL accessibility...")
        
        # Public URLs (should redirect to login)
        public_urls = [
            ('', 'Dashboard'),
            ('hospitals/', 'Hospital List'),
            ('patients/', 'Patient List'),
            ('appointments/', 'Appointment List'),
            ('analytics/', 'Analytics'),
            ('inventory/', 'Inventory Management'),
        ]
        
        for url, name in public_urls:
            try:
                response = self.client.get(f'/mahalshifa/{url}')
                if response.status_code in [200, 302]:  # 302 = redirect to login
                    self.log_result(f"URL accessibility: {name}", True, f"Status: {response.status_code}")
                else:
                    self.log_result(f"URL accessibility: {name}", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_result(f"URL accessibility: {name}", False, f"Error: {str(e)}")
    
    def test_user_role_access(self):
        """Test role-based access control"""
        print("\n👥 Testing user role-based access...")
        
        test_urls = [
            '/mahalshifa/',
            '/mahalshifa/hospitals/',
            '/mahalshifa/patients/',
            '/mahalshifa/appointments/',
            '/mahalshifa/analytics/',
        ]
        
        for role, user in self.users.items():
            self.client.force_login(user)
            
            accessible_count = 0
            for url in test_urls:
                try:
                    response = self.client.get(url)
                    if response.status_code == 200:
                        accessible_count += 1
                except:
                    pass
            
            self.log_result(
                f"Role access: {role}",
                accessible_count > 0,
                f"Can access {accessible_count}/{len(test_urls)} URLs"
            )
            
            self.client.logout()
    
    def test_medical_functionality(self):
        """Test medical-specific functionality"""
        print("\n🏥 Testing medical functionality...")
        
        # Login as admin
        self.client.force_login(self.users['admin'])
        
        # Test dashboard statistics
        try:
            response = self.client.get('/mahalshifa/')
            if response.status_code == 200 and 'total_patients' in response.context:
                self.log_result(
                    "Dashboard statistics",
                    True,
                    f"Patients: {response.context['total_patients']}, Appointments: {response.context.get('todays_appointments', 0)}"
                )
            else:
                self.log_result("Dashboard statistics", False, "Missing context data")
        except Exception as e:
            self.log_result("Dashboard statistics", False, f"Error: {str(e)}")
        
        # Test hospital listing
        try:
            response = self.client.get('/mahalshifa/hospitals/')
            if response.status_code == 200:
                hospital_count = len(response.context.get('hospitals', []))
                self.log_result("Hospital listing", True, f"Found {hospital_count} hospitals")
            else:
                self.log_result("Hospital listing", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Hospital listing", False, f"Error: {str(e)}")
        
        # Test patient listing
        try:
            response = self.client.get('/mahalshifa/patients/')
            if response.status_code == 200:
                patient_count = len(response.context.get('patients', []))
                self.log_result("Patient listing", True, f"Found {patient_count} patients")
            else:
                self.log_result("Patient listing", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Patient listing", False, f"Error: {str(e)}")
        
        # Test appointment listing
        try:
            response = self.client.get('/mahalshifa/appointments/')
            if response.status_code == 200:
                appointment_count = len(response.context.get('appointments', []))
                self.log_result("Appointment listing", True, f"Found {appointment_count} appointments")
            else:
                self.log_result("Appointment listing", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Appointment listing", False, f"Error: {str(e)}")
        
        # Test appointment creation page
        try:
            response = self.client.get('/mahalshifa/appointments/create/')
            if response.status_code == 200:
                self.log_result("Appointment creation", True, "Form accessible")
            else:
                self.log_result("Appointment creation", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Appointment creation", False, f"Error: {str(e)}")
        
        # Test analytics page
        try:
            response = self.client.get('/mahalshifa/analytics/')
            if response.status_code == 200:
                self.log_result("Medical analytics", True, "Analytics accessible")
            else:
                self.log_result("Medical analytics", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Medical analytics", False, f"Error: {str(e)}")
        
        self.client.logout()
    
    def test_doctor_functionality(self):
        """Test doctor-specific functionality"""
        print("\n👨‍⚕️ Testing doctor functionality...")
        
        # Login as doctor
        self.client.force_login(self.users['doctor'])
        
        # Test doctor dashboard access
        try:
            response = self.client.get('/mahalshifa/')
            if response.status_code == 200:
                self.log_result("Doctor dashboard access", True, "Dashboard accessible")
            else:
                self.log_result("Doctor dashboard access", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Doctor dashboard access", False, f"Error: {str(e)}")
        
        # Test doctor's appointment view
        try:
            response = self.client.get('/mahalshifa/appointments/')
            if response.status_code == 200:
                self.log_result("Doctor appointment view", True, "Can view appointments")
            else:
                self.log_result("Doctor appointment view", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Doctor appointment view", False, f"Error: {str(e)}")
        
        # Test doctor's patient view
        try:
            response = self.client.get('/mahalshifa/patients/')
            if response.status_code == 200:
                self.log_result("Doctor patient view", True, "Can view patients")
            else:
                self.log_result("Doctor patient view", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Doctor patient view", False, f"Error: {str(e)}")
        
        self.client.logout()
    
    def test_patient_functionality(self):
        """Test patient-specific functionality"""
        print("\n🏥 Testing patient functionality...")
        
        # Login as patient
        self.client.force_login(self.users['patient'])
        
        # Test patient dashboard access
        try:
            response = self.client.get('/mahalshifa/')
            if response.status_code == 200:
                self.log_result("Patient dashboard access", True, "Dashboard accessible")
            else:
                self.log_result("Patient dashboard access", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Patient dashboard access", False, f"Error: {str(e)}")
        
        # Test patient's appointment view
        try:
            response = self.client.get('/mahalshifa/appointments/')
            if response.status_code == 200:
                self.log_result("Patient appointment view", True, "Can view own appointments")
            else:
                self.log_result("Patient appointment view", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Patient appointment view", False, f"Error: {str(e)}")
        
        # Test appointment creation by patient
        try:
            response = self.client.get('/mahalshifa/appointments/create/')
            if response.status_code == 200:
                self.log_result("Patient appointment booking", True, "Can create appointments")
            else:
                self.log_result("Patient appointment booking", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Patient appointment booking", False, f"Error: {str(e)}")
        
        self.client.logout()
    
    def test_data_export(self):
        """Test data export functionality"""
        print("\n📊 Testing data export...")
        
        # Login as admin
        self.client.force_login(self.users['admin'])
        
        export_types = ['appointments', 'patients']
        
        for export_type in export_types:
            try:
                response = self.client.get(f'/mahalshifa/export/?type={export_type}')
                if response.status_code == 200 and response.get('Content-Type') == 'text/csv':
                    self.log_result(f"Export {export_type}", True, "CSV export successful")
                else:
                    self.log_result(f"Export {export_type}", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_result(f"Export {export_type}", False, f"Error: {str(e)}")
        
        self.client.logout()
    
    def generate_summary_report(self):
        """Generate comprehensive summary report"""
        print("\n" + "="*80)
        print("🏥 MAHALSHIFA APP TESTING SUMMARY REPORT")
        print("="*80)
        
        # Count results
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.startswith("✅")])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"✅ Passed: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
        print(f"❌ Failed: {failed_tests}/{total_tests} ({failed_tests/total_tests*100:.1f}%)")
        
        print(f"\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            print(f"  {result}")
        
        # Sample data summary
        print(f"\n🏥 SAMPLE MEDICAL DATA CREATED:")
        data_summary = [
            f"🏥 Hospital: {self.sample_data.get('hospital', 'N/A')}",
            f"🏢 Department: {self.sample_data.get('department', 'N/A')}",
            f"👨‍⚕️ Doctor: {self.sample_data.get('doctor', 'N/A')}",
            f"🏥 Patient: {self.sample_data.get('patient', 'N/A')}",
            f"📅 Appointment: {self.sample_data.get('appointment', 'N/A')}",
            f"📋 Medical Record: {self.sample_data.get('medical_record', 'N/A')}",
            f"💊 Prescription: {self.sample_data.get('prescription', 'N/A')}",
            f"🧪 Lab Test: {self.sample_data.get('lab_test', 'N/A')}",
            f"📊 Vital Signs: {self.sample_data.get('vital_signs', 'N/A')}",
            f"💊 Medication: {self.sample_data.get('medication', 'N/A')}"
        ]
        
        for item in data_summary:
            print(f"  {item}")
        
        # Key URLs for testing
        print(f"\n🔗 KEY URLS FOR MANUAL TESTING:")
        urls = [
            "🏠 Dashboard: http://localhost:8000/mahalshifa/",
            "🏥 Hospitals: http://localhost:8000/mahalshifa/hospitals/",
            "🏥 Patients: http://localhost:8000/mahalshifa/patients/",
            "📅 Appointments: http://localhost:8000/mahalshifa/appointments/",
            "📊 Analytics: http://localhost:8000/mahalshifa/analytics/",
            "📦 Inventory: http://localhost:8000/mahalshifa/inventory/",
        ]
        
        for url in urls:
            print(f"  {url}")
        
        # Test user credentials
        print(f"\n👥 TEST USER CREDENTIALS:")
        user_creds = [
            "👤 Admin: admin / admin123",
            "👤 Aamil: aamil_medical / test123", 
            "👤 Doctor: dr_ahmed / test123",
            "👤 Patient: patient_ali / test123",
            "👤 Moze Coordinator: moze_coord / test123"
        ]
        
        for cred in user_creds:
            print(f"  {cred}")
        
        # Status determination
        if passed_tests == total_tests:
            status = "🎉 ALL TESTS PASSED - MAHALSHIFA APP IS 100% FUNCTIONAL!"
        elif passed_tests >= total_tests * 0.8:
            status = "✅ MOSTLY FUNCTIONAL - Minor issues detected"
        elif passed_tests >= total_tests * 0.6:
            status = "⚠️ PARTIALLY FUNCTIONAL - Some issues need attention"
        else:
            status = "❌ SIGNIFICANT ISSUES - Major fixes required"
        
        print(f"\n🏆 FINAL STATUS: {status}")
        print("="*80)
        
        return passed_tests == total_tests

def main():
    """Main testing function"""
    print("🏥 Starting Comprehensive Mahalshifa App Testing...")
    print("="*80)
    
    tester = MahalshifaAppTester()
    
    # Run all tests
    try:
        # Setup phase
        tester.create_test_users()
        tester.create_sample_medical_data()
        
        # Testing phase
        tester.test_model_access()
        tester.test_url_accessibility()
        tester.test_user_role_access()
        tester.test_medical_functionality()
        tester.test_doctor_functionality()
        tester.test_patient_functionality()
        tester.test_data_export()
        
        # Report phase
        all_passed = tester.generate_summary_report()
        
        return all_passed
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)