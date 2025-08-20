from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from datetime import datetime, timedelta, time
from decimal import Decimal
import json

from appointments.models import (
    Appointment, TimeSlot, AppointmentReminder,
    WaitingList, AppointmentStatus, AppointmentType
)
from doctordirectory.models import Doctor, Patient, MedicalService

User = get_user_model()


class TimeSlotAPITest(TestCase):
    """Test TimeSlot API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create doctor user
        self.doctor_user = User.objects.create_user(
            username='doctor1',
            email='doctor1@test.com',
            password='test123',
            role='doctor'
        )
        self.doctor = Doctor.objects.create(
            name='Dr. Test Doctor',
            user=self.doctor_user,
            specialty='General Medicine'
        )
        
        # Create patient user
        self.patient_user = User.objects.create_user(
            username='patient1',
            email='patient1@test.com',
            password='test123',
            role='student'
        )
        
        self.future_date = timezone.now().date() + timedelta(days=7)
        
    def test_list_time_slots(self):
        """Test listing time slots"""
        # Create some time slots
        TimeSlot.objects.create(
            doctor=self.doctor,
            date=self.future_date,
            start_time=time(9, 0),
            end_time=time(9, 30)
        )
        TimeSlot.objects.create(
            doctor=self.doctor,
            date=self.future_date,
            start_time=time(10, 0),
            end_time=time(10, 30)
        )
        
        self.client.force_authenticate(user=self.patient_user)
        response = self.client.get('/api/appointments/time-slots/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_filter_time_slots_by_doctor(self):
        """Test filtering time slots by doctor"""
        # Create another doctor
        other_doctor = Doctor.objects.create(
            name='Dr. Other',
            specialty='Cardiology'
        )
        
        # Create time slots for both doctors
        TimeSlot.objects.create(
            doctor=self.doctor,
            date=self.future_date,
            start_time=time(9, 0),
            end_time=time(9, 30)
        )
        TimeSlot.objects.create(
            doctor=other_doctor,
            date=self.future_date,
            start_time=time(9, 0),
            end_time=time(9, 30)
        )
        
        self.client.force_authenticate(user=self.patient_user)
        response = self.client.get(f'/api/appointments/time-slots/?doctor={self.doctor.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['doctor'], self.doctor.id)
    
    def test_create_time_slot_as_doctor(self):
        """Test creating time slot as doctor"""
        self.client.force_authenticate(user=self.doctor_user)
        
        data = {
            'doctor': self.doctor.id,
            'date': self.future_date.isoformat(),
            'start_time': '14:00',
            'end_time': '15:00',
            'max_appointments': 3
        }
        
        response = self.client.post('/api/appointments/time-slots/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TimeSlot.objects.count(), 1)
        
        slot = TimeSlot.objects.first()
        self.assertEqual(slot.doctor, self.doctor)
        self.assertEqual(slot.max_appointments, 3)
    
    def test_bulk_create_time_slots(self):
        """Test bulk creating time slots"""
        self.client.force_authenticate(user=self.doctor_user)
        
        data = {
            'doctor': self.doctor.id,
            'start_date': self.future_date.isoformat(),
            'end_date': (self.future_date + timedelta(days=7)).isoformat(),
            'start_time': '09:00',
            'end_time': '17:00',
            'slot_duration_minutes': 30,
            'break_duration_minutes': 15,
            'weekdays': [1, 2, 3, 4, 5],  # Monday to Friday
            'max_appointments_per_slot': 2
        }
        
        response = self.client.post('/api/appointments/time-slots/bulk_create/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertGreater(TimeSlot.objects.count(), 0)


class AppointmentAPITest(TestCase):
    """Test Appointment API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create users
        self.doctor_user = User.objects.create_user(
            username='doctor1',
            email='doctor1@test.com',
            password='test123',
            role='doctor'
        )
        self.doctor = Doctor.objects.create(
            name='Dr. Test Doctor',
            user=self.doctor_user,
            specialty='General Medicine',
            consultation_fee=150.00
        )
        
        self.patient_user = User.objects.create_user(
            username='patient1',
            email='patient1@test.com',
            password='test123',
            role='student',
            its_id='12345678'
        )
        self.patient = Patient.objects.create(
            user=self.patient_user,
            date_of_birth=datetime(1990, 1, 1).date(),
            gender='male'
        )
        
        self.service = MedicalService.objects.create(
            doctor=self.doctor,
            name='General Consultation',
            duration_minutes=30,
            price=150.00
        )
        
        self.future_date = timezone.now().date() + timedelta(days=7)
        
        # Create time slot
        self.time_slot = TimeSlot.objects.create(
            doctor=self.doctor,
            date=self.future_date,
            start_time=time(10, 0),
            end_time=time(11, 0)
        )
    
    def test_create_appointment(self):
        """Test creating an appointment"""
        self.client.force_authenticate(user=self.patient_user)
        
        data = {
            'doctor': self.doctor.id,
            'patient': self.patient.id,
            'service': self.service.id,
            'appointment_date': self.future_date.isoformat(),
            'appointment_time': '10:00',
            'duration_minutes': 30,
            'appointment_type': AppointmentType.CONSULTATION,
            'reason_for_visit': 'Regular checkup',
            'symptoms': 'None',
            'booking_method': 'online'
        }
        
        response = self.client.post('/api/appointments/appointments/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Appointment.objects.count(), 1)
        
        appointment = Appointment.objects.first()
        self.assertEqual(appointment.doctor, self.doctor)
        self.assertEqual(appointment.patient, self.patient)
        self.assertEqual(appointment.booked_by, self.patient_user)
        self.assertEqual(appointment.consultation_fee, Decimal('150.00'))
    
    def test_list_appointments_as_patient(self):
        """Test listing appointments as patient"""
        # Create appointments
        appointment1 = Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            appointment_date=self.future_date,
            appointment_time=time(10, 0),
            reason_for_visit='Checkup'
        )
        
        # Create another patient's appointment
        other_patient = Patient.objects.create(
            user=User.objects.create_user('patient2', 'p2@test.com', 'test123'),
            date_of_birth=datetime(1985, 1, 1).date(),
            gender='female'
        )
        Appointment.objects.create(
            doctor=self.doctor,
            patient=other_patient,
            appointment_date=self.future_date,
            appointment_time=time(11, 0),
            reason_for_visit='Other checkup'
        )
        
        self.client.force_authenticate(user=self.patient_user)
        response = self.client.get('/api/appointments/appointments/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['patient'], self.patient.id)
    
    def test_list_appointments_as_doctor(self):
        """Test listing appointments as doctor"""
        # Create appointments
        Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            appointment_date=self.future_date,
            appointment_time=time(10, 0),
            reason_for_visit='Checkup'
        )
        
        # Create another doctor's appointment
        other_doctor = Doctor.objects.create(
            name='Dr. Other',
            specialty='Cardiology'
        )
        other_patient = Patient.objects.create(
            user=User.objects.create_user('patient2', 'p2@test.com', 'test123'),
            date_of_birth=datetime(1985, 1, 1).date(),
            gender='female'
        )
        Appointment.objects.create(
            doctor=other_doctor,
            patient=other_patient,
            appointment_date=self.future_date,
            appointment_time=time(11, 0),
            reason_for_visit='Other checkup'
        )
        
        self.client.force_authenticate(user=self.doctor_user)
        response = self.client.get('/api/appointments/appointments/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['doctor'], self.doctor.id)
    
    def test_confirm_appointment(self):
        """Test confirming an appointment"""
        appointment = Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            appointment_date=self.future_date,
            appointment_time=time(14, 0),
            status=AppointmentStatus.PENDING,
            reason_for_visit='Test'
        )
        
        self.client.force_authenticate(user=self.doctor_user)
        response = self.client.post(f'/api/appointments/appointments/{appointment.id}/confirm/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, AppointmentStatus.CONFIRMED)
        self.assertIsNotNone(appointment.confirmed_at)
    
    def test_cancel_appointment(self):
        """Test cancelling an appointment"""
        appointment = Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            appointment_date=self.future_date,
            appointment_time=time(15, 0),
            status=AppointmentStatus.CONFIRMED,
            reason_for_visit='Test'
        )
        
        self.client.force_authenticate(user=self.patient_user)
        
        data = {
            'cancellation_reason': 'Unable to attend due to emergency'
        }
        
        response = self.client.post(
            f'/api/appointments/appointments/{appointment.id}/cancel/',
            data
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, AppointmentStatus.CANCELLED)
        self.assertIsNotNone(appointment.cancelled_at)
        self.assertEqual(appointment.cancelled_by, self.patient_user)
        self.assertEqual(appointment.cancellation_reason, 'Unable to attend due to emergency')
    
    def test_reschedule_appointment(self):
        """Test rescheduling an appointment"""
        appointment = Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            appointment_date=self.future_date,
            appointment_time=time(16, 0),
            status=AppointmentStatus.CONFIRMED,
            reason_for_visit='Test'
        )
        
        new_date = self.future_date + timedelta(days=1)
        
        self.client.force_authenticate(user=self.patient_user)
        
        data = {
            'new_date': new_date.isoformat(),
            'new_time': '11:00',
            'reason': 'Conflict with another appointment'
        }
        
        response = self.client.post(
            f'/api/appointments/appointments/{appointment.id}/reschedule/',
            data
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check old appointment is cancelled
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, AppointmentStatus.CANCELLED)
        
        # Check new appointment is created
        new_appointment = Appointment.objects.filter(
            rescheduled_from=appointment
        ).first()
        self.assertIsNotNone(new_appointment)
        self.assertEqual(new_appointment.appointment_date, new_date)
        self.assertEqual(new_appointment.appointment_time, time(11, 0))
        self.assertEqual(new_appointment.status, AppointmentStatus.SCHEDULED)
    
    def test_appointment_statistics(self):
        """Test appointment statistics endpoint"""
        # Create various appointments
        for i in range(5):
            Appointment.objects.create(
                doctor=self.doctor,
                patient=self.patient,
                appointment_date=self.future_date + timedelta(days=i),
                appointment_time=time(10, 0),
                status=AppointmentStatus.COMPLETED if i < 3 else AppointmentStatus.CONFIRMED,
                consultation_fee=150.00,
                is_paid=i < 3,
                reason_for_visit=f'Test {i}'
            )
        
        self.client.force_authenticate(user=self.doctor_user)
        response = self.client.get('/api/appointments/appointments/statistics/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total'], 5)
        self.assertEqual(response.data['completed'], 3)
        self.assertEqual(response.data['revenue'], 450.00)  # 3 * 150
    
    def test_today_appointments(self):
        """Test today's appointments endpoint"""
        today = timezone.now().date()
        
        # Create today's appointment
        Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            appointment_date=today,
            appointment_time=time(14, 0),
            reason_for_visit='Today appointment'
        )
        
        # Create future appointment
        Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            appointment_date=self.future_date,
            appointment_time=time(14, 0),
            reason_for_visit='Future appointment'
        )
        
        self.client.force_authenticate(user=self.doctor_user)
        response = self.client.get('/api/appointments/appointments/today/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['reason_for_visit'], 'Today appointment')
    
    def test_upcoming_appointments(self):
        """Test upcoming appointments endpoint"""
        # Create past appointment
        past_date = timezone.now().date() - timedelta(days=1)
        Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            appointment_date=past_date,
            appointment_time=time(10, 0),
            status=AppointmentStatus.COMPLETED,
            reason_for_visit='Past appointment'
        )
        
        # Create upcoming appointment
        Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            appointment_date=self.future_date,
            appointment_time=time(10, 0),
            status=AppointmentStatus.CONFIRMED,
            reason_for_visit='Upcoming appointment'
        )
        
        self.client.force_authenticate(user=self.patient_user)
        response = self.client.get('/api/appointments/appointments/upcoming/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['reason_for_visit'], 'Upcoming appointment')


class DoctorAvailabilityAPITest(TestCase):
    """Test doctor availability API"""
    
    def setUp(self):
        self.client = APIClient()
        
        self.user = User.objects.create_user(
            username='patient1',
            email='patient1@test.com',
            password='test123'
        )
        
        self.doctor = Doctor.objects.create(
            name='Dr. Test',
            specialty='General Medicine'
        )
        
        self.future_date = timezone.now().date() + timedelta(days=7)
    
    def test_check_doctor_availability(self):
        """Test checking doctor availability"""
        # Create time slots
        TimeSlot.objects.create(
            doctor=self.doctor,
            date=self.future_date,
            start_time=time(9, 0),
            end_time=time(12, 0),
            max_appointments=3
        )
        
        TimeSlot.objects.create(
            doctor=self.doctor,
            date=self.future_date,
            start_time=time(14, 0),
            end_time=time(17, 0),
            max_appointments=3
        )
        
        self.client.force_authenticate(user=self.user)
        
        data = {
            'doctor_id': self.doctor.id,
            'date': self.future_date.isoformat(),
            'duration_minutes': 30
        }
        
        response = self.client.post('/api/appointments/check-availability/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['doctor_id'], self.doctor.id)
        self.assertGreater(len(response.data['available_slots']), 0)


class WaitingListAPITest(TestCase):
    """Test WaitingList API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        
        self.patient_user = User.objects.create_user(
            username='patient1',
            email='patient1@test.com',
            password='test123',
            role='student'
        )
        self.patient = Patient.objects.create(
            user=self.patient_user,
            date_of_birth=datetime(1990, 1, 1).date(),
            gender='male'
        )
        
        self.doctor = Doctor.objects.create(
            name='Dr. Test',
            specialty='General Medicine'
        )
        
        self.future_date = timezone.now().date() + timedelta(days=14)
    
    def test_create_waiting_list_entry(self):
        """Test creating waiting list entry"""
        self.client.force_authenticate(user=self.patient_user)
        
        data = {
            'patient': self.patient.id,
            'doctor': self.doctor.id,
            'preferred_date': self.future_date.isoformat(),
            'preferred_time_start': '09:00',
            'preferred_time_end': '17:00',
            'appointment_type': AppointmentType.CONSULTATION,
            'reason': 'Regular checkup',
            'priority': 5
        }
        
        response = self.client.post('/api/appointments/waiting-list/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(WaitingList.objects.count(), 1)
        
        entry = WaitingList.objects.first()
        self.assertEqual(entry.patient, self.patient)
        self.assertEqual(entry.doctor, self.doctor)
        self.assertTrue(entry.is_active)
    
    def test_list_waiting_list_entries(self):
        """Test listing waiting list entries"""
        # Create entries
        WaitingList.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            preferred_date=self.future_date,
            reason='Test 1',
            priority=3
        )
        
        WaitingList.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            preferred_date=self.future_date + timedelta(days=1),
            reason='Test 2',
            priority=7
        )
        
        self.client.force_authenticate(user=self.patient_user)
        response = self.client.get('/api/appointments/waiting-list/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        # Check ordering by priority
        self.assertEqual(response.data['results'][0]['priority'], 3)
        self.assertEqual(response.data['results'][1]['priority'], 7)