"""
Unit tests for DoctorDirectory API
"""
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from datetime import date, time, timedelta

from moze.models import Moze
from ..models import (
    Doctor, DoctorSchedule, PatientLog, DoctorAvailability,
    MedicalService, Patient, Appointment, MedicalRecord,
    Prescription, LabTest, VitalSigns
)

User = get_user_model()


class DoctorDirectoryAPITestCase(APITestCase):
    """Base test case for DoctorDirectory API tests"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test users
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            role='badri_mahal_admin'
        )
        
        self.doctor_user = User.objects.create_user(
            username='doctor',
            email='doctor@test.com',
            password='testpass123',
            role='doctor'
        )
        
        self.patient_user = User.objects.create_user(
            username='patient',
            email='patient@test.com',
            password='testpass123',
            role='student'
        )
        
        self.aamil_user = User.objects.create_user(
            username='aamil',
            email='aamil@test.com',
            password='testpass123',
            role='aamil'
        )
        
        # Create test Moze
        self.moze = Moze.objects.create(
            name='Test Moze',
            location='Test Location',
            aamil=self.aamil_user,
            address='Test Address'
        )
        
        # Create test Doctor
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            name='Dr Test Doctor',
            its_id='12345678',
            specialty='General Medicine',
            qualification='MBBS',
            experience_years=5,
            assigned_moze=self.moze,
            is_verified=True,
            is_available=True,
            license_number='DOC123',
            consultation_fee=Decimal('500.00'),
            phone='1234567890',
            email='doctor@test.com',
            bio='Test doctor bio'
        )
        
        # Create test Patient
        self.patient = Patient.objects.create(
            user=self.patient_user,
            date_of_birth=date(1990, 1, 1),
            gender='M',
            blood_group='A+',
            emergency_contact='9876543210'
        )
        
        # Create test Medical Service
        self.service = MedicalService.objects.create(
            doctor=self.doctor,
            name='General Consultation',
            service_type='consultation',
            description='General medical consultation',
            duration_minutes=30,
            fee=Decimal('500.00')
        )


class DoctorAPITests(DoctorDirectoryAPITestCase):
    """Test cases for Doctor API endpoints"""
    
    def test_list_doctors_authenticated(self):
        """Test listing doctors as authenticated user"""
        self.client.force_authenticate(user=self.patient_user)
        url = reverse('doctordirectory_api:doctor_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_list_doctors_unauthenticated(self):
        """Test listing doctors as unauthenticated user"""
        url = reverse('doctordirectory_api:doctor_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_doctor_admin(self):
        """Test creating doctor as admin"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('doctordirectory_api:doctor_list_create')
        
        # Create another doctor user
        doctor_user = User.objects.create_user(
            username='doctor2',
            email='doctor2@test.com',
            password='testpass123',
            role='doctor'
        )
        
        data = {
            'user_id': doctor_user.id,
            'name': 'Dr New Doctor',
            'its_id': '87654321',
            'specialty': 'Cardiology',
            'qualification': 'MBBS, MD',
            'experience_years': 10,
            'is_verified': True,
            'is_available': True,
            'consultation_fee': '750.00'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Doctor.objects.count(), 2)
    
    def test_create_doctor_non_admin(self):
        """Test creating doctor as non-admin (should fail)"""
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('doctordirectory_api:doctor_list_create')
        
        # Create a doctor user for valid data
        new_doctor_user = User.objects.create_user(
            username='newdoctor',
            email='newdoctor@test.com',
            password='testpass123',
            role='doctor'
        )
        
        data = {
            'user_id': new_doctor_user.id,
            'name': 'Dr Unauthorized',
            'its_id': '11111111',
            'specialty': 'Test',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_retrieve_doctor(self):
        """Test retrieving specific doctor"""
        self.client.force_authenticate(user=self.patient_user)
        url = reverse('doctordirectory_api:doctor_detail', kwargs={'pk': self.doctor.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Dr Test Doctor')
    
    def test_update_doctor_owner(self):
        """Test updating doctor profile by owner"""
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('doctordirectory_api:doctor_detail', kwargs={'pk': self.doctor.id})
        
        data = {
            'bio': 'Updated bio for test doctor',
            'consultation_fee': '600.00'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.doctor.refresh_from_db()
        self.assertEqual(self.doctor.bio, 'Updated bio for test doctor')
    
    def test_search_doctors(self):
        """Test doctor search functionality"""
        self.client.force_authenticate(user=self.patient_user)
        url = reverse('doctordirectory_api:doctor_search')
        
        # Search by specialty
        response = self.client.get(url, {'specialty': 'General'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Search by name (search for "Test" which is in the name)
        response = self.client.get(url, {'search': 'Test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class PatientAPITests(DoctorDirectoryAPITestCase):
    """Test cases for Patient API endpoints"""
    
    def test_list_patients_doctor(self):
        """Test listing patients as doctor"""
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('doctordirectory_api:patient_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_patient(self):
        """Test creating patient"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('doctordirectory_api:patient_list_create')
        
        patient_user = User.objects.create_user(
            username='newpatient',
            email='newpatient@test.com',
            password='testpass123'
        )
        
        data = {
            'user_id': patient_user.id,
            'date_of_birth': '1995-05-15',
            'gender': 'F',
            'blood_group': 'B+',
            'emergency_contact': '9999999999'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Patient.objects.count(), 2)
    
    def test_retrieve_patient_own_profile(self):
        """Test patient retrieving own profile"""
        self.client.force_authenticate(user=self.patient_user)
        url = reverse('doctordirectory_api:patient_detail', kwargs={'pk': self.patient.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], 'patient')


class AppointmentAPITests(DoctorDirectoryAPITestCase):
    """Test cases for Appointment API endpoints"""
    
    def setUp(self):
        super().setUp()
        # Create test appointment
        tomorrow = timezone.now().date() + timedelta(days=1)
        self.appointment = Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            service=self.service,
            appointment_date=tomorrow,
            appointment_time=time(10, 0),
            reason_for_visit='Routine checkup',
            status='pending'
        )
    
    def test_list_appointments_patient(self):
        """Test listing appointments as patient"""
        self.client.force_authenticate(user=self.patient_user)
        url = reverse('doctordirectory_api:appointment_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_list_appointments_doctor(self):
        """Test listing appointments as doctor"""
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('doctordirectory_api:appointment_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_appointment(self):
        """Test creating appointment"""
        self.client.force_authenticate(user=self.patient_user)
        url = reverse('doctordirectory_api:appointment_list_create')
        
        tomorrow = timezone.now().date() + timedelta(days=1)
        data = {
            'doctor_id': self.doctor.id,
            'patient_id': self.patient.id,
            'service_id': self.service.id,
            'appointment_date': tomorrow.isoformat(),
            'appointment_time': '14:00:00',
            'reason_for_visit': 'Follow-up consultation'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Appointment.objects.count(), 2)
    
    def test_update_appointment_status_doctor(self):
        """Test updating appointment status as doctor"""
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('doctordirectory_api:appointment_detail', kwargs={'pk': self.appointment.id})
        
        data = {'status': 'confirmed'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, 'confirmed')
    
    def test_search_appointments(self):
        """Test appointment search functionality"""
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('doctordirectory_api:appointment_search')
        
        # Search by status
        response = self.client.get(url, {'status': 'pending'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class MedicalRecordAPITests(DoctorDirectoryAPITestCase):
    """Test cases for Medical Record API endpoints"""
    
    def setUp(self):
        super().setUp()
        # Create test medical record
        self.medical_record = MedicalRecord.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            diagnosis='Common Cold',
            symptoms='Fever, cough, headache',
            treatment_plan='Rest and medication',
            medications='Paracetamol, Cough syrup'
        )
    
    def test_list_medical_records_doctor(self):
        """Test listing medical records as doctor"""
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('doctordirectory_api:medical_record_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_list_medical_records_patient(self):
        """Test listing medical records as patient"""
        self.client.force_authenticate(user=self.patient_user)
        url = reverse('doctordirectory_api:medical_record_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_medical_record_doctor(self):
        """Test creating medical record as doctor"""
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('doctordirectory_api:medical_record_list_create')
        
        data = {
            'patient_id': self.patient.id,
            'doctor_id': self.doctor.id,
            'diagnosis': 'Hypertension',
            'symptoms': 'High blood pressure',
            'treatment_plan': 'Lifestyle changes and medication',
            'medications': 'Amlodipine 5mg',
            'follow_up_required': True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MedicalRecord.objects.count(), 2)
    
    def test_retrieve_medical_record_patient(self):
        """Test retrieving medical record as patient"""
        self.client.force_authenticate(user=self.patient_user)
        url = reverse('doctordirectory_api:medical_record_detail', kwargs={'pk': self.medical_record.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['diagnosis'], 'Common Cold')


class DoctorScheduleAPITests(DoctorDirectoryAPITestCase):
    """Test cases for Doctor Schedule API endpoints"""
    
    def setUp(self):
        super().setUp()
        # Create test schedule
        tomorrow = timezone.now().date() + timedelta(days=1)
        self.schedule = DoctorSchedule.objects.create(
            doctor=self.doctor,
            date=tomorrow,
            start_time=time(9, 0),
            end_time=time(17, 0),
            moze=self.moze,
            max_patients=20,
            schedule_type='regular'
        )
    
    def test_list_schedules_doctor(self):
        """Test listing schedules as doctor"""
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('doctordirectory_api:schedule_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_schedule_doctor(self):
        """Test creating schedule as doctor"""
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('doctordirectory_api:schedule_list_create')
        
        day_after_tomorrow = timezone.now().date() + timedelta(days=2)
        data = {
            'date': day_after_tomorrow.isoformat(),
            'start_time': '08:00:00',
            'end_time': '16:00:00',
            'moze_id': self.moze.id,
            'max_patients': 15,
            'schedule_type': 'regular'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DoctorSchedule.objects.count(), 2)
    
    def test_access_schedules_non_doctor(self):
        """Test accessing schedules as non-doctor (should fail)"""
        self.client.force_authenticate(user=self.patient_user)
        url = reverse('doctordirectory_api:schedule_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class MedicalServiceAPITests(DoctorDirectoryAPITestCase):
    """Test cases for Medical Service API endpoints"""
    
    def test_list_services_doctor(self):
        """Test listing services as doctor"""
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('doctordirectory_api:service_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_list_services_patient(self):
        """Test listing services as patient (should see all active services)"""
        self.client.force_authenticate(user=self.patient_user)
        url = reverse('doctordirectory_api:service_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_service_doctor(self):
        """Test creating service as doctor"""
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('doctordirectory_api:service_list_create')
        
        data = {
            'name': 'Cardiology Consultation',
            'service_type': 'consultation',
            'description': 'Specialized heart consultation',
            'duration_minutes': 45,
            'fee': '800.00'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MedicalService.objects.count(), 2)


class StatisticsAPITests(DoctorDirectoryAPITestCase):
    """Test cases for Statistics API endpoints"""
    
    def test_doctor_statistics_admin(self):
        """Test doctor statistics as admin"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('doctordirectory_api:doctor_stats')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_doctors', response.data)
        self.assertEqual(response.data['total_doctors'], 1)
    
    def test_patient_statistics_doctor(self):
        """Test patient statistics as doctor"""
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('doctordirectory_api:patient_stats')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_patients', response.data)
    
    def test_appointment_statistics_patient(self):
        """Test appointment statistics as patient"""
        self.client.force_authenticate(user=self.patient_user)
        url = reverse('doctordirectory_api:appointment_stats')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_appointments', response.data)
    
    def test_dashboard_data_doctor(self):
        """Test dashboard data as doctor"""
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('doctordirectory_api:dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('doctor_stats', response.data)
        self.assertIn('patient_stats', response.data)
        self.assertIn('appointment_stats', response.data)


class PermissionTests(DoctorDirectoryAPITestCase):
    """Test cases for permission enforcement"""
    
    def test_unauthorized_access_denied(self):
        """Test that unauthenticated requests are denied"""
        url = reverse('doctordirectory_api:doctor_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_patient_cannot_access_all_patients(self):
        """Test that patients cannot see all patients"""
        self.client.force_authenticate(user=self.patient_user)
        
        # Create another patient
        other_user = User.objects.create_user(
            username='otherpatient',
            email='other@test.com',
            password='testpass123'
        )
        other_patient = Patient.objects.create(
            user=other_user,
            date_of_birth=date(1985, 1, 1)
        )
        
        url = reverse('doctordirectory_api:patient_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only see own patient profile
        self.assertEqual(len(response.data['results']), 1)
    
    def test_doctor_can_see_own_patients(self):
        """Test that doctors can see patients they've treated"""
        self.client.force_authenticate(user=self.doctor_user)
        
        # Create appointment to establish doctor-patient relationship
        tomorrow = timezone.now().date() + timedelta(days=1)
        Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            appointment_date=tomorrow,
            appointment_time=time(10, 0),
            reason_for_visit='Test'
        )
        
        url = reverse('doctordirectory_api:patient_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)


class FilteringAndSearchTests(DoctorDirectoryAPITestCase):
    """Test cases for filtering and search functionality"""
    
    def setUp(self):
        super().setUp()
        # Create additional test data
        self.doctor_user2 = User.objects.create_user(
            username='doctor2',
            email='doctor2@test.com',
            password='testpass123',
            role='doctor'
        )
        
        self.doctor2 = Doctor.objects.create(
            user=self.doctor_user2,
            name='Dr Second Doctor',
            its_id='87654321',
            specialty='Cardiology',
            qualification='MBBS, MD',
            experience_years=8,
            is_verified=True,
            is_available=False,  # Different availability
            license_number='DOC456'
        )
    
    def test_doctor_filtering(self):
        """Test filtering doctors by various criteria"""
        self.client.force_authenticate(user=self.patient_user)
        url = reverse('doctordirectory_api:doctor_list_create')
        
        # Filter by specialty
        response = self.client.get(url, {'specialty': 'General Medicine'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Filter by availability (patients should only see available doctors)
        response = self.client.get(url, {'is_available': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_doctor_search(self):
        """Test searching doctors"""
        self.client.force_authenticate(user=self.admin_user)  # Admin can see all
        url = reverse('doctordirectory_api:doctor_search')
        
        # Search by name
        response = self.client.get(url, {'search': 'Second'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Search by specialty
        response = self.client.get(url, {'specialty': 'Cardiology'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_appointment_filtering(self):
        """Test filtering appointments"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Create test appointments
        tomorrow = timezone.now().date() + timedelta(days=1)
        appointment1 = Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            appointment_date=tomorrow,
            appointment_time=time(10, 0),
            reason_for_visit='Test 1',
            status='pending'
        )
        
        appointment2 = Appointment.objects.create(
            doctor=self.doctor2,
            patient=self.patient,
            appointment_date=tomorrow,
            appointment_time=time(11, 0),
            reason_for_visit='Test 2',
            status='confirmed'
        )
        
        url = reverse('doctordirectory_api:appointment_list_create')
        
        # Filter by doctor
        response = self.client.get(url, {'doctor': self.doctor.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Filter by status
        response = self.client.get(url, {'status': 'confirmed'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)