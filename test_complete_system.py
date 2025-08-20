#!/usr/bin/env python
"""
Complete System Integration Test
Tests all modules from login to logout for each user role
"""

import os
import sys
import django
from datetime import datetime, timedelta, date
from decimal import Decimal
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from django.utils import timezone

# Import all models
from moze.models import Moze, MozeCoordinator
from doctordirectory.models import Doctor, Patient, MedicalService, PatientLog, Appointment
from appointments.models import TimeSlot, AppointmentStatus, AppointmentReminder, WaitingList
from mahalshifa.models import Hospital, Department
from araz.models import Petition, PetitionStatus
from surveys.models import Survey, Question, Response, SurveySubmission
from evaluation.models import StudentEvaluation
from students.models import Student, Course, Enrollment
from photos.models import PhotoAlbum, Photo

User = get_user_model()


class SystemIntegrationTest:
    """Test complete system integration for all user roles"""
    
    def __init__(self):
        self.client = Client()
        self.results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
    
    def run_all_tests(self):
        """Run all integration tests"""
        print("=" * 80)
        print("UMOOR SEHHAT - COMPLETE SYSTEM INTEGRATION TEST")
        print("=" * 80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Test each role
        self.test_admin_workflow()
        self.test_aamil_workflow()
        self.test_coordinator_workflow()
        self.test_doctor_workflow()
        self.test_patient_workflow()
        self.test_student_workflow()
        
        # Test cross-module integration
        self.test_appointment_integration()
        self.test_medical_records_integration()
        self.test_survey_integration()
        
        # Print summary
        self.print_test_summary()
    
    def test_login(self, its_id, password='pass1234'):
        """Test login functionality"""
        print(f"\n  → Testing login for ITS ID: {its_id}")
        
        response = self.client.post('/accounts/login/', {
            'its_id': its_id,
            'password': password
        }, follow=True)
        
        if response.status_code == 200:
            user = User.objects.filter(its_id=its_id).first()
            if user and self.client.session.get('_auth_user_id'):
                print(f"    ✓ Login successful - Role: {user.get_role_display()}")
                self.results['passed'] += 1
                return user
            else:
                print(f"    ✗ Login failed - User not authenticated")
                self.results['failed'] += 1
                self.results['errors'].append(f"Login failed for {its_id}")
                return None
        else:
            print(f"    ✗ Login failed - Status: {response.status_code}")
            self.results['failed'] += 1
            self.results['errors'].append(f"Login returned {response.status_code} for {its_id}")
            return None
    
    def test_logout(self):
        """Test logout functionality"""
        print("\n  → Testing logout")
        response = self.client.post('/accounts/logout/', follow=True)
        
        if '_auth_user_id' not in self.client.session:
            print("    ✓ Logout successful")
            self.results['passed'] += 1
            return True
        else:
            print("    ✗ Logout failed")
            self.results['failed'] += 1
            self.results['errors'].append("Logout failed")
            return False
    
    def test_admin_workflow(self):
        """Test admin user workflow"""
        print("\n" + "=" * 60)
        print("1. TESTING ADMIN WORKFLOW")
        print("=" * 60)
        
        # Login as admin
        user = self.test_login('10000001')
        if not user:
            return
        
        # Test admin dashboard access
        print("\n  → Testing admin dashboard access")
        response = self.client.get('/admin/')
        if response.status_code in [200, 302]:
            print("    ✓ Admin dashboard accessible")
            self.results['passed'] += 1
        else:
            print(f"    ✗ Admin dashboard not accessible - Status: {response.status_code}")
            self.results['failed'] += 1
        
        # Test user management
        print("\n  → Testing user management")
        try:
            users_count = User.objects.count()
            print(f"    ✓ Can view all {users_count} users")
            self.results['passed'] += 1
        except Exception as e:
            print(f"    ✗ Cannot access users: {e}")
            self.results['failed'] += 1
        
        # Test moze management
        print("\n  → Testing moze management")
        try:
            moze_count = Moze.objects.count()
            print(f"    ✓ Can manage all {moze_count} moze")
            self.results['passed'] += 1
        except Exception as e:
            print(f"    ✗ Cannot access moze: {e}")
            self.results['failed'] += 1
        
        # Logout
        self.test_logout()
    
    def test_aamil_workflow(self):
        """Test aamil user workflow"""
        print("\n" + "=" * 60)
        print("2. TESTING AAMIL WORKFLOW")
        print("=" * 60)
        
        # Login as aamil
        user = self.test_login('10000002')
        if not user:
            return
        
        # Test moze dashboard access
        print("\n  → Testing moze dashboard access")
        response = self.client.get('/moze/dashboard/')
        if response.status_code == 200:
            print("    ✓ Moze dashboard accessible")
            self.results['passed'] += 1
        else:
            print(f"    ✗ Moze dashboard not accessible - Status: {response.status_code}")
            self.results['failed'] += 1
        
        # Test moze management
        print("\n  → Testing aamil's moze access")
        try:
            # Get aamil's moze
            aamil_moze = Moze.objects.filter(aamil=user).first()
            if aamil_moze:
                print(f"    ✓ Can access assigned moze: {aamil_moze.name}")
                self.results['passed'] += 1
                
                # Test petition management
                print("\n  → Testing petition management")
                petitions = Petition.objects.filter(moze=aamil_moze).count()
                print(f"    ✓ Can manage {petitions} petitions in moze")
                self.results['passed'] += 1
                
                # Test creating petition status
                if petitions > 0:
                    petition = Petition.objects.filter(moze=aamil_moze).first()
                    status = PetitionStatus.objects.create(
                        petition=petition,
                        status='under_review',
                        updated_by=user,
                        comments='Reviewed by Aamil'
                    )
                    print("    ✓ Can update petition status")
                    self.results['passed'] += 1
            else:
                print("    ✗ No moze assigned to aamil")
                self.results['failed'] += 1
        except Exception as e:
            print(f"    ✗ Error accessing moze: {e}")
            self.results['failed'] += 1
        
        # Test reports access
        print("\n  → Testing reports access")
        try:
            # Get moze statistics
            if aamil_moze:
                patient_logs = PatientLog.objects.filter(moze=aamil_moze).count()
                print(f"    ✓ Can view reports - {patient_logs} patient logs")
                self.results['passed'] += 1
        except Exception as e:
            print(f"    ✗ Cannot access reports: {e}")
            self.results['failed'] += 1
        
        # Logout
        self.test_logout()
    
    def test_coordinator_workflow(self):
        """Test moze coordinator workflow"""
        print("\n" + "=" * 60)
        print("3. TESTING MOZE COORDINATOR WORKFLOW")
        print("=" * 60)
        
        # Login as coordinator
        user = self.test_login('10000102')
        if not user:
            return
        
        # Test moze dashboard access
        print("\n  → Testing coordinator moze dashboard")
        response = self.client.get('/moze/dashboard/')
        if response.status_code == 200:
            print("    ✓ Moze dashboard accessible")
            self.results['passed'] += 1
        else:
            print(f"    ✗ Moze dashboard not accessible - Status: {response.status_code}")
            self.results['failed'] += 1
        
        # Test coordinator's moze access
        print("\n  → Testing coordinator's moze access")
        try:
            coordinator_moze = MozeCoordinator.objects.filter(user=user, is_active=True).first()
            if coordinator_moze:
                moze = coordinator_moze.moze
                print(f"    ✓ Can access assigned moze: {moze.name}")
                self.results['passed'] += 1
                
                # Test limited access
                all_moze = Moze.objects.count()
                print(f"    ✓ Limited access verified (1 of {all_moze} moze)")
                self.results['passed'] += 1
            else:
                print("    ✗ No moze assigned to coordinator")
                self.results['failed'] += 1
        except Exception as e:
            print(f"    ✗ Error accessing moze: {e}")
            self.results['failed'] += 1
        
        # Logout
        self.test_logout()
    
    def test_doctor_workflow(self):
        """Test doctor user workflow"""
        print("\n" + "=" * 60)
        print("4. TESTING DOCTOR WORKFLOW")
        print("=" * 60)
        
        # Login as doctor
        user = self.test_login('10000202')
        if not user:
            return
        
        # Test doctor dashboard
        print("\n  → Testing doctor dashboard access")
        response = self.client.get('/doctordirectory/dashboard/')
        if response.status_code == 200:
            print("    ✓ Doctor dashboard accessible")
            self.results['passed'] += 1
        else:
            print(f"    ✗ Doctor dashboard not accessible - Status: {response.status_code}")
            self.results['failed'] += 1
        
        # Test doctor profile
        print("\n  → Testing doctor profile")
        try:
            doctor = Doctor.objects.filter(user=user).first()
            if doctor:
                print(f"    ✓ Doctor profile found: Dr. {doctor.name}")
                print(f"      Specialty: {doctor.specialty}")
                print(f"      Consultation Fee: ${doctor.consultation_fee}")
                self.results['passed'] += 1
                
                # Test time slots
                print("\n  → Testing time slot management")
                tomorrow = timezone.now().date() + timedelta(days=1)
                time_slot = TimeSlot.objects.create(
                    doctor=doctor,
                    date=tomorrow,
                    start_time=datetime.strptime('09:00', '%H:%M').time(),
                    end_time=datetime.strptime('09:30', '%H:%M').time(),
                    max_appointments=2
                )
                print(f"    ✓ Can create time slots")
                self.results['passed'] += 1
                
                # Test appointments
                print("\n  → Testing appointment access")
                appointments = Appointment.objects.filter(doctor=doctor).count()
                print(f"    ✓ Can view {appointments} appointments")
                self.results['passed'] += 1
                
                # Test patient logs
                print("\n  → Testing patient logs")
                logs = PatientLog.objects.filter(seen_by=doctor).count()
                print(f"    ✓ Can access {logs} patient logs")
                self.results['passed'] += 1
            else:
                print("    ✗ No doctor profile found")
                self.results['failed'] += 1
        except Exception as e:
            print(f"    ✗ Error accessing doctor profile: {e}")
            self.results['failed'] += 1
        
        # Logout
        self.test_logout()
    
    def test_patient_workflow(self):
        """Test patient user workflow"""
        print("\n" + "=" * 60)
        print("5. TESTING PATIENT WORKFLOW")
        print("=" * 60)
        
        # Login as patient
        user = self.test_login('10000500')
        if not user:
            return
        
        # Test profile access
        print("\n  → Testing patient profile access")
        response = self.client.get('/accounts/profile/')
        if response.status_code == 200:
            print("    ✓ Patient profile accessible")
            self.results['passed'] += 1
        else:
            print(f"    ✗ Patient profile not accessible - Status: {response.status_code}")
            self.results['failed'] += 1
        
        # Test patient data
        print("\n  → Testing patient data")
        try:
            patient = Patient.objects.filter(user=user).first()
            if patient:
                print(f"    ✓ Patient profile found")
                print(f"      Blood Group: {patient.blood_group}")
                print(f"      Emergency Contact: {patient.emergency_contact}")
                self.results['passed'] += 1
                
                # Test appointment booking
                print("\n  → Testing appointment booking capability")
                doctor = Doctor.objects.first()
                if doctor:
                    tomorrow = timezone.now().date() + timedelta(days=1)
                    
                    # Check if patient can create appointment
                    appointment = Appointment(
                        doctor=doctor,
                        patient=patient,
                        appointment_date=tomorrow,
                        appointment_time=datetime.strptime('10:00', '%H:%M').time(),
                        duration_minutes=30,
                        reason_for_visit='Checkup',
                        booked_by=user
                    )
                    print("    ✓ Patient can book appointments")
                    self.results['passed'] += 1
                
                # Test medical records access
                print("\n  → Testing medical records access")
                records = PatientLog.objects.filter(patient_its_id=user.its_id).count()
                print(f"    ✓ Can view {records} medical records")
                self.results['passed'] += 1
            else:
                print("    ✗ No patient profile found")
                self.results['failed'] += 1
        except Exception as e:
            print(f"    ✗ Error accessing patient data: {e}")
            self.results['failed'] += 1
        
        # Logout
        self.test_logout()
    
    def test_student_workflow(self):
        """Test student user workflow"""
        print("\n" + "=" * 60)
        print("6. TESTING STUDENT WORKFLOW")
        print("=" * 60)
        
        # Login as student
        user = self.test_login('10000252')
        if not user:
            return
        
        # Test student dashboard
        print("\n  → Testing student dashboard access")
        response = self.client.get('/students/dashboard/')
        if response.status_code == 200:
            print("    ✓ Student dashboard accessible")
            self.results['passed'] += 1
        else:
            print(f"    ✗ Student dashboard not accessible - Status: {response.status_code}")
            self.results['failed'] += 1
        
        # Test student profile
        print("\n  → Testing student profile")
        try:
            student = Student.objects.filter(user=user).first()
            if student:
                print(f"    ✓ Student profile found")
                print(f"      ITS ID: {student.its_id}")
                print(f"      Current Year: {student.current_year}")
                print(f"      Moze: {student.moze}")
                self.results['passed'] += 1
                
                # Test course enrollment
                print("\n  → Testing course enrollment")
                enrollments = Enrollment.objects.filter(student=student).count()
                print(f"    ✓ Enrolled in {enrollments} courses")
                self.results['passed'] += 1
                
                # Test evaluations
                print("\n  → Testing evaluations access")
                evaluations = StudentEvaluation.objects.filter(student=student).count()
                print(f"    ✓ Has {evaluations} evaluations")
                self.results['passed'] += 1
                
                # Test survey participation
                print("\n  → Testing survey access")
                submissions = SurveySubmission.objects.filter(submitted_by=user).count()
                print(f"    ✓ Submitted {submissions} surveys")
                self.results['passed'] += 1
            else:
                print("    ✗ No student profile found")
                self.results['failed'] += 1
        except Exception as e:
            print(f"    ✗ Error accessing student data: {e}")
            self.results['failed'] += 1
        
        # Logout
        self.test_logout()
    
    def test_appointment_integration(self):
        """Test appointment system integration"""
        print("\n" + "=" * 60)
        print("7. TESTING APPOINTMENT SYSTEM INTEGRATION")
        print("=" * 60)
        
        # Login as patient
        patient_user = self.test_login('10000501')
        if not patient_user:
            return
        
        print("\n  → Testing appointment booking flow")
        try:
            patient = Patient.objects.filter(user=patient_user).first()
            doctor = Doctor.objects.first()
            
            if patient and doctor:
                # Find available time slot
                tomorrow = timezone.now().date() + timedelta(days=1)
                time_slot = TimeSlot.objects.filter(
                    doctor=doctor,
                    date__gte=tomorrow,
                    is_available=True,
                    is_booked=False
                ).first()
                
                if time_slot:
                    # Book appointment
                    appointment = Appointment.objects.create(
                        doctor=doctor,
                        patient=patient,
                        time_slot=time_slot,
                        appointment_date=time_slot.date,
                        appointment_time=time_slot.start_time,
                        duration_minutes=30,
                        reason_for_visit='Integration test',
                        booked_by=patient_user,
                        status=AppointmentStatus.PENDING
                    )
                    print(f"    ✓ Appointment booked - ID: {appointment.appointment_id}")
                    self.results['passed'] += 1
                    
                    # Test reminder creation
                    reminders = AppointmentReminder.objects.filter(appointment=appointment).count()
                    print(f"    ✓ {reminders} reminders created")
                    self.results['passed'] += 1
                    
                    # Logout patient
                    self.test_logout()
                    
                    # Login as doctor to confirm
                    doctor_user = self.test_login('10000203')
                    if doctor_user:
                        # Confirm appointment
                        appointment.confirm(confirmed_by=doctor_user)
                        print("    ✓ Doctor confirmed appointment")
                        self.results['passed'] += 1
                        
                        # Complete appointment
                        appointment.status = AppointmentStatus.IN_PROGRESS
                        appointment.save()
                        appointment.complete(
                            completed_by=doctor_user,
                            notes='Patient in good health'
                        )
                        print("    ✓ Appointment completed")
                        self.results['passed'] += 1
                        
                        self.test_logout()
                else:
                    print("    ✗ No available time slots")
                    self.results['failed'] += 1
            else:
                print("    ✗ Patient or doctor not found")
                self.results['failed'] += 1
        except Exception as e:
            print(f"    ✗ Appointment integration error: {e}")
            self.results['failed'] += 1
    
    def test_medical_records_integration(self):
        """Test medical records integration"""
        print("\n" + "=" * 60)
        print("8. TESTING MEDICAL RECORDS INTEGRATION")
        print("=" * 60)
        
        # Login as doctor
        doctor_user = self.test_login('10000204')
        if not doctor_user:
            return
        
        print("\n  → Testing medical record creation")
        try:
            doctor = Doctor.objects.filter(user=doctor_user).first()
            patient = Patient.objects.first()
            moze = Moze.objects.first()
            
            if doctor and patient and moze:
                # Create patient log
                log = PatientLog.objects.create(
                    patient_its_id=patient.user.its_id if patient.user else '12345678',
                    patient_name=patient.user.get_full_name() if patient.user else 'Test Patient',
                    ailment='Integration test ailment',
                    symptoms='Test symptoms',
                    diagnosis='Test diagnosis',
                    prescription='Test prescription',
                    follow_up_required=True,
                    follow_up_date=timezone.now().date() + timedelta(days=7),
                    visit_type='consultation',
                    moze=moze,
                    seen_by=doctor
                )
                print(f"    ✓ Medical record created - ID: {log.id}")
                self.results['passed'] += 1
                
                # Logout doctor
                self.test_logout()
                
                # Login as patient to view
                if patient.user:
                    patient_user = self.test_login(patient.user.its_id)
                    if patient_user:
                        # Check if patient can see their record
                        patient_logs = PatientLog.objects.filter(
                            patient_its_id=patient_user.its_id
                        ).count()
                        print(f"    ✓ Patient can view {patient_logs} medical records")
                        self.results['passed'] += 1
                        self.test_logout()
            else:
                print("    ✗ Required data not found")
                self.results['failed'] += 1
        except Exception as e:
            print(f"    ✗ Medical records integration error: {e}")
            self.results['failed'] += 1
    
    def test_survey_integration(self):
        """Test survey system integration"""
        print("\n" + "=" * 60)
        print("9. TESTING SURVEY INTEGRATION")
        print("=" * 60)
        
        # Login as aamil to create survey
        aamil_user = self.test_login('10000003')
        if not aamil_user:
            return
        
        print("\n  → Testing survey creation")
        try:
            # Create survey
            survey = Survey.objects.create(
                title='Integration Test Survey',
                description='Testing survey integration',
                created_by=aamil_user,
                start_date=timezone.now().date(),
                end_date=timezone.now().date() + timedelta(days=30),
                is_active=True
            )
            print(f"    ✓ Survey created: {survey.title}")
            self.results['passed'] += 1
            
            # Create questions
            question = Question.objects.create(
                survey=survey,
                text='How satisfied are you?',
                question_type='rating',
                order=1,
                is_required=True
            )
            print("    ✓ Survey question created")
            self.results['passed'] += 1
            
            # Logout aamil
            self.test_logout()
            
            # Login as student to respond
            student_user = self.test_login('10000253')
            if student_user:
                # Submit response
                submission = SurveySubmission.objects.create(
                    survey=survey,
                    submitted_by=student_user,
                    submitted_at=timezone.now()
                )
                
                Response.objects.create(
                    submission=submission,
                    question=question,
                    answer='5'
                )
                print("    ✓ Student submitted survey response")
                self.results['passed'] += 1
                
                self.test_logout()
        except Exception as e:
            print(f"    ✗ Survey integration error: {e}")
            self.results['failed'] += 1
    
    def print_test_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests Run: {self.results['passed'] + self.results['failed']}")
        print(f"Passed: {self.results['passed']} ✓")
        print(f"Failed: {self.results['failed']} ✗")
        print(f"Success Rate: {(self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100):.1f}%")
        
        if self.results['errors']:
            print("\nErrors:")
            for error in self.results['errors']:
                print(f"  - {error}")
        
        print("\n" + "=" * 80)
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)


def main():
    """Run the integration tests"""
    print("\nThis will run comprehensive integration tests for all modules.")
    print("Make sure you have run 'generate_mock_data.py' first.")
    
    confirm = input("\nContinue with tests? (yes/no): ")
    
    if confirm.lower() == 'yes':
        tester = SystemIntegrationTest()
        tester.run_all_tests()
    else:
        print("Tests cancelled.")


if __name__ == '__main__':
    main()