#!/usr/bin/env python
"""
Comprehensive test script for admin appointment system
Tests all aspects of appointment booking from admin perspective
"""
import os
import sys
import django
from datetime import date, timedelta, time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

from accounts.models import User
from doctordirectory.models import Doctor, Patient, Appointment, MedicalService
from doctordirectory.forms import AppointmentForm
from accounts.services import ITSService
from django.test import RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse

class AdminAppointmentTester:
    def __init__(self):
        self.factory = RequestFactory()
        self.errors = []
        self.warnings = []
        self.success_count = 0
        self.test_count = 0
        
    def log_error(self, test_name, error):
        self.errors.append(f"❌ {test_name}: {error}")
        
    def log_warning(self, test_name, warning):
        self.warnings.append(f"⚠️ {test_name}: {warning}")
        
    def log_success(self, test_name):
        self.success_count += 1
        print(f"✅ {test_name}")
        
    def run_test(self, test_name, test_func):
        self.test_count += 1
        try:
            test_func()
            self.log_success(test_name)
        except Exception as e:
            self.log_error(test_name, str(e))
            
    def test_admin_user_exists(self):
        """Test if admin user exists and has correct permissions"""
        admin_user = User.objects.filter(role='badri_mahal_admin').first()
        if not admin_user:
            raise Exception("No admin user found")
        
        if not admin_user.is_admin:
            raise Exception(f"Admin user {admin_user.its_id} has is_admin=False")
            
        self.admin_user = admin_user
        
    def test_doctors_available(self):
        """Test if doctors are available for booking"""
        doctors = Doctor.objects.filter(is_available=True)
        if not doctors.exists():
            raise Exception("No available doctors found")
            
        if doctors.count() < 3:
            self.log_warning("test_doctors_available", f"Only {doctors.count()} doctors available")
            
        self.test_doctor = doctors.first()
        
    def test_patient_users_exist(self):
        """Test if patient users exist for booking"""
        patient_users = User.objects.filter(role='patient')
        if not patient_users.exists():
            raise Exception("No patient users found")
            
        self.test_patient_its_id = patient_users.first().its_id
        
    def test_its_api_lookup(self):
        """Test ITS API lookup functionality"""
        its_data = ITSService.fetch_user_data(self.test_patient_its_id)
        if not its_data:
            raise Exception(f"ITS API lookup failed for {self.test_patient_its_id}")
            
        required_fields = ['first_name', 'last_name', 'its_id']
        missing_fields = [field for field in required_fields if not its_data.get(field)]
        if missing_fields:
            raise Exception(f"Missing ITS data fields: {missing_fields}")
            
    def test_appointment_form_validation(self):
        """Test appointment form validation with valid data"""
        future_date = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        form_data = {
            'doctor': self.test_doctor.id,
            'patient_its_id': self.test_patient_its_id,
            'appointment_date': future_date,
            'appointment_time': '10:00',
            'reason_for_visit': 'Test appointment',
            'notes': 'Admin test booking'
        }
        
        form = AppointmentForm(data=form_data, doctor=self.test_doctor, user=self.admin_user)
        
        if not form.is_valid():
            error_details = []
            for field, errors in form.errors.items():
                error_details.append(f"{field}: {', '.join(errors)}")
            raise Exception(f"Form validation failed: {'; '.join(error_details)}")
            
        patient = form.cleaned_data.get('patient')
        if not patient:
            raise Exception("Form did not assign patient after validation")
            
    def test_appointment_form_edge_cases(self):
        """Test appointment form with various edge cases"""
        # Test with past date
        past_date = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        form_data = {
            'doctor': self.test_doctor.id,
            'patient_its_id': self.test_patient_its_id,
            'appointment_date': past_date,
            'appointment_time': '10:00',
            'reason_for_visit': 'Test appointment'
        }
        
        form = AppointmentForm(data=form_data, doctor=self.test_doctor, user=self.admin_user)
        if form.is_valid():
            raise Exception("Form should reject past dates but didn't")
            
        # Test with invalid ITS ID
        future_date = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        form_data = {
            'doctor': self.test_doctor.id,
            'patient_its_id': '12345678',  # Invalid ITS ID
            'appointment_date': future_date,
            'appointment_time': '10:00',
            'reason_for_visit': 'Test appointment'
        }
        
        form = AppointmentForm(data=form_data, doctor=self.test_doctor, user=self.admin_user)
        if form.is_valid():
            raise Exception("Form should reject invalid ITS ID but didn't")
            
    def test_doctor_services(self):
        """Test if doctors have medical services available"""
        services = MedicalService.objects.filter(doctor=self.test_doctor, is_available=True)
        if not services.exists():
            self.log_warning("test_doctor_services", f"Doctor {self.test_doctor.user.get_full_name()} has no available services")
            
    def test_appointment_creation(self):
        """Test actual appointment creation"""
        future_date = date.today() + timedelta(days=2)
        appointment_time = time(14, 30)  # 2:30 PM
        
        # Get or create patient
        patient_user = User.objects.get(its_id=self.test_patient_its_id)
        patient, created = Patient.objects.get_or_create(
            user=patient_user,
            defaults={
                'date_of_birth': date(1990, 1, 1),
                'gender': 'other'
            }
        )
        
        # Create appointment
        appointment = Appointment.objects.create(
            doctor=self.test_doctor,
            patient=patient,
            appointment_date=future_date,
            appointment_time=appointment_time,
            reason_for_visit='Admin test appointment',
            notes='Created during admin system test',
            status='scheduled'
        )
        
        if not appointment.id:
            raise Exception("Appointment was not saved to database")
            
        # Clean up
        appointment.delete()
        
    def test_appointment_permissions(self):
        """Test appointment-related permissions for admin"""
        if not self.admin_user.is_admin:
            raise Exception("Admin user lacks is_admin permission")
            
        # Test dashboard access permission
        if not (self.admin_user.is_admin or self.admin_user.is_doctor or 
                self.admin_user.is_aamil or self.admin_user.is_moze_coordinator):
            raise Exception("Admin user cannot access doctor dashboard")
            
        # Test appointment creation permission
        if not (self.admin_user.is_admin or self.admin_user.is_doctor or self.admin_user.is_patient):
            raise Exception("Admin user cannot create appointments")
            
    def test_database_integrity(self):
        """Test database integrity and relationships"""
        # Test User -> Doctor relationship
        doctor_users = User.objects.filter(role='doctor')
        doctor_profiles = Doctor.objects.all()
        
        if doctor_users.count() == 0 and doctor_profiles.count() > 0:
            self.log_warning("test_database_integrity", "Doctor profiles exist without corresponding users")
            
        # Test User -> Patient relationship
        patient_users = User.objects.filter(role='patient')
        patient_profiles = Patient.objects.all()
        
        if patient_users.count() > 0 and patient_profiles.count() == 0:
            self.log_warning("test_database_integrity", "Patient users exist but no patient profiles")
            
    def test_url_routing(self):
        """Test URL routing for appointment system"""
        # Test create appointment URL
        try:
            from django.urls import reverse
            url = reverse('doctordirectory:create_appointment')
            if not url:
                raise Exception("create_appointment URL not found")
        except Exception as e:
            raise Exception(f"URL routing error: {e}")
            
    def run_all_tests(self):
        """Run all tests and generate report"""
        print("🔍 Testing Admin Appointment System")
        print("=" * 50)
        
        tests = [
            ("Admin User Exists", self.test_admin_user_exists),
            ("Doctors Available", self.test_doctors_available),
            ("Patient Users Exist", self.test_patient_users_exist),
            ("ITS API Lookup", self.test_its_api_lookup),
            ("Appointment Form Validation", self.test_appointment_form_validation),
            ("Appointment Form Edge Cases", self.test_appointment_form_edge_cases),
            ("Doctor Services", self.test_doctor_services),
            ("Appointment Creation", self.test_appointment_creation),
            ("Appointment Permissions", self.test_appointment_permissions),
            ("Database Integrity", self.test_database_integrity),
            ("URL Routing", self.test_url_routing),
        ]
        
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
            
        self.generate_report()
        
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 50)
        print("📊 ADMIN APPOINTMENT SYSTEM TEST REPORT")
        print("=" * 50)
        
        print(f"\n📈 Summary:")
        print(f"  Total Tests: {self.test_count}")
        print(f"  Passed: {self.success_count}")
        print(f"  Failed: {len(self.errors)}")
        print(f"  Warnings: {len(self.warnings)}")
        
        success_rate = (self.success_count / self.test_count * 100) if self.test_count > 0 else 0
        print(f"  Success Rate: {success_rate:.1f}%")
        
        if self.errors:
            print(f"\n🚨 ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  {error}")
                
        if self.warnings:
            print(f"\n⚠️ WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  {warning}")
                
        if len(self.errors) == 0:
            print(f"\n🎉 All critical tests passed! Admin appointment system is working.")
        else:
            print(f"\n🔧 Issues found that need to be fixed:")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error.split(': ', 1)[1]}")
                
        return len(self.errors) == 0

def main():
    tester = AdminAppointmentTester()
    success = tester.run_all_tests()
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)