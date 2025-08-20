from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta, time
from decimal import Decimal

from appointments.models import (
    Appointment, TimeSlot, AppointmentLog, AppointmentReminder,
    WaitingList, AppointmentStatus, AppointmentType
)
from doctordirectory.models import Doctor, Patient, MedicalService
from moze.models import Moze

User = get_user_model()


class TimeSlotModelTest(TestCase):
    """Test TimeSlot model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='doctor1',
            email='doctor1@test.com',
            password='test123',
            role='doctor'
        )
        self.doctor = Doctor.objects.create(
            name='Dr. Test Doctor',
            user=self.user,
            specialty='General Medicine',
            consultation_fee=100.00
        )
        self.future_date = timezone.now().date() + timedelta(days=7)
    
    def test_create_time_slot(self):
        """Test creating a time slot"""
        slot = TimeSlot.objects.create(
            doctor=self.doctor,
            date=self.future_date,
            start_time=time(9, 0),
            end_time=time(9, 30),
            max_appointments=2
        )
        
        self.assertEqual(slot.doctor, self.doctor)
        self.assertEqual(slot.date, self.future_date)
        self.assertEqual(slot.duration_minutes, 30)
        self.assertTrue(slot.is_available)
        self.assertFalse(slot.is_booked)
        self.assertTrue(slot.can_book())
    
    def test_time_slot_validation(self):
        """Test time slot validation"""
        # Test end time before start time
        with self.assertRaises(ValidationError):
            slot = TimeSlot(
                doctor=self.doctor,
                date=self.future_date,
                start_time=time(10, 0),
                end_time=time(9, 0)
            )
            slot.clean()
    
    def test_recurring_time_slot(self):
        """Test recurring time slot"""
        slot = TimeSlot.objects.create(
            doctor=self.doctor,
            date=self.future_date,
            start_time=time(14, 0),
            end_time=time(15, 0),
            is_recurring=True,
            recurring_days='1,3,5',  # Tuesday, Thursday, Saturday
            recurring_end_date=self.future_date + timedelta(days=30)
        )
        
        self.assertTrue(slot.is_recurring)
        self.assertEqual(slot.recurring_days, '1,3,5')
    
    def test_can_book_logic(self):
        """Test can_book method logic"""
        # Past date slot
        past_slot = TimeSlot.objects.create(
            doctor=self.doctor,
            date=timezone.now().date() - timedelta(days=1),
            start_time=time(10, 0),
            end_time=time(11, 0)
        )
        self.assertFalse(past_slot.can_book())
        
        # Unavailable slot
        unavailable_slot = TimeSlot.objects.create(
            doctor=self.doctor,
            date=self.future_date,
            start_time=time(11, 0),
            end_time=time(12, 0),
            is_available=False
        )
        self.assertFalse(unavailable_slot.can_book())
        
        # Fully booked slot
        booked_slot = TimeSlot.objects.create(
            doctor=self.doctor,
            date=self.future_date,
            start_time=time(13, 0),
            end_time=time(14, 0),
            is_booked=True
        )
        self.assertFalse(booked_slot.can_book())


class AppointmentModelTest(TestCase):
    """Test Appointment model"""
    
    def setUp(self):
        # Create doctor user and doctor
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
        
        # Create patient user and patient
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
        
        # Create service
        self.service = MedicalService.objects.create(
            doctor=self.doctor,
            name='General Consultation',
            duration_minutes=30,
            price=150.00
        )
        
        self.future_date = timezone.now().date() + timedelta(days=7)
    
    def test_create_appointment(self):
        """Test creating an appointment"""
        appointment = Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            service=self.service,
            appointment_date=self.future_date,
            appointment_time=time(10, 0),
            duration_minutes=30,
            appointment_type=AppointmentType.CONSULTATION,
            reason_for_visit='Regular checkup',
            booked_by=self.patient_user
        )
        
        self.assertEqual(appointment.doctor, self.doctor)
        self.assertEqual(appointment.patient, self.patient)
        self.assertEqual(appointment.status, AppointmentStatus.PENDING)
        self.assertEqual(appointment.consultation_fee, Decimal('150.00'))
        self.assertTrue(appointment.is_upcoming)
        self.assertFalse(appointment.is_past)
        self.assertIsNotNone(appointment.appointment_id)
    
    def test_appointment_validation(self):
        """Test appointment validation"""
        # Test past date appointment
        with self.assertRaises(ValidationError):
            appointment = Appointment(
                doctor=self.doctor,
                patient=self.patient,
                appointment_date=timezone.now().date() - timedelta(days=1),
                appointment_time=time(10, 0),
                reason_for_visit='Test'
            )
            appointment.clean()
    
    def test_appointment_conflict_detection(self):
        """Test appointment conflict detection"""
        # Create first appointment
        Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            appointment_date=self.future_date,
            appointment_time=time(10, 0),
            duration_minutes=30,
            status=AppointmentStatus.CONFIRMED,
            reason_for_visit='First appointment'
        )
        
        # Try to create conflicting appointment
        with self.assertRaises(ValidationError):
            conflicting = Appointment(
                doctor=self.doctor,
                patient=self.patient,
                appointment_date=self.future_date,
                appointment_time=time(10, 0),
                duration_minutes=30,
                reason_for_visit='Conflicting appointment'
            )
            conflicting.clean()
    
    def test_appointment_end_time_calculation(self):
        """Test appointment end time calculation"""
        appointment = Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            appointment_date=self.future_date,
            appointment_time=time(14, 30),
            duration_minutes=45,
            reason_for_visit='Test'
        )
        
        self.assertEqual(appointment.end_time, time(15, 15))
    
    def test_appointment_status_transitions(self):
        """Test appointment status transitions"""
        appointment = Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            appointment_date=self.future_date,
            appointment_time=time(16, 0),
            reason_for_visit='Test'
        )
        
        # Test confirmation
        self.assertTrue(appointment.can_cancel())
        self.assertTrue(appointment.can_reschedule())
        
        appointment.confirm(confirmed_by=self.patient_user)
        self.assertEqual(appointment.status, AppointmentStatus.CONFIRMED)
        self.assertIsNotNone(appointment.confirmed_at)
        
        # Test cancellation
        appointment.cancel(cancelled_by=self.patient_user, reason='Test cancellation')
        self.assertEqual(appointment.status, AppointmentStatus.CANCELLED)
        self.assertIsNotNone(appointment.cancelled_at)
        self.assertEqual(appointment.cancelled_by, self.patient_user)
        self.assertEqual(appointment.cancellation_reason, 'Test cancellation')
        
        # Test can't cancel completed appointment
        completed_appointment = Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            appointment_date=self.future_date,
            appointment_time=time(17, 0),
            status=AppointmentStatus.COMPLETED,
            reason_for_visit='Test'
        )
        self.assertFalse(completed_appointment.can_cancel())
        self.assertFalse(completed_appointment.can_reschedule())
    
    def test_appointment_with_time_slot(self):
        """Test appointment with time slot integration"""
        time_slot = TimeSlot.objects.create(
            doctor=self.doctor,
            date=self.future_date,
            start_time=time(11, 0),
            end_time=time(12, 0),
            max_appointments=2
        )
        
        appointment = Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            time_slot=time_slot,
            appointment_date=self.future_date,
            appointment_time=time(11, 0),
            duration_minutes=30,
            status=AppointmentStatus.CONFIRMED,
            reason_for_visit='Test'
        )
        
        # Refresh time slot
        time_slot.refresh_from_db()
        self.assertEqual(time_slot.current_appointments, 1)
        self.assertFalse(time_slot.is_booked)  # Not fully booked yet
        
        # Add another appointment to fill the slot
        appointment2 = Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            time_slot=time_slot,
            appointment_date=self.future_date,
            appointment_time=time(11, 30),
            duration_minutes=30,
            status=AppointmentStatus.CONFIRMED,
            reason_for_visit='Test 2'
        )
        
        time_slot.refresh_from_db()
        self.assertEqual(time_slot.current_appointments, 2)
        self.assertTrue(time_slot.is_booked)  # Now fully booked


class AppointmentLogModelTest(TestCase):
    """Test AppointmentLog model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='test123'
        )
        self.doctor = Doctor.objects.create(
            name='Dr. Test',
            consultation_fee=100.00
        )
        self.patient = Patient.objects.create(
            user=self.user,
            date_of_birth=datetime(1990, 1, 1).date(),
            gender='male'
        )
        self.appointment = Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            appointment_date=timezone.now().date() + timedelta(days=7),
            appointment_time=time(10, 0),
            reason_for_visit='Test'
        )
    
    def test_create_appointment_log(self):
        """Test creating appointment log"""
        log = AppointmentLog.objects.create(
            appointment=self.appointment,
            action='created',
            performed_by=self.user,
            notes='Appointment created for testing'
        )
        
        self.assertEqual(log.appointment, self.appointment)
        self.assertEqual(log.action, 'created')
        self.assertEqual(log.performed_by, self.user)
        self.assertIsNotNone(log.timestamp)


class AppointmentReminderModelTest(TestCase):
    """Test AppointmentReminder model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='patient1',
            email='patient@test.com'
        )
        self.doctor = Doctor.objects.create(
            name='Dr. Test',
            consultation_fee=100.00
        )
        self.patient = Patient.objects.create(
            user=self.user,
            date_of_birth=datetime(1990, 1, 1).date(),
            gender='male'
        )
        self.appointment = Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            appointment_date=timezone.now().date() + timedelta(days=2),
            appointment_time=time(14, 0),
            reason_for_visit='Test'
        )
    
    def test_create_reminder(self):
        """Test creating appointment reminder"""
        scheduled_time = timezone.now() + timedelta(hours=24)
        reminder = AppointmentReminder.objects.create(
            appointment=self.appointment,
            reminder_type='email',
            scheduled_for=scheduled_time
        )
        
        self.assertEqual(reminder.appointment, self.appointment)
        self.assertEqual(reminder.reminder_type, 'email')
        self.assertEqual(reminder.status, 'pending')
        self.assertFalse(reminder.is_sent)
        self.assertIsNone(reminder.sent_at)
    
    def test_reminder_status_update(self):
        """Test updating reminder status"""
        reminder = AppointmentReminder.objects.create(
            appointment=self.appointment,
            reminder_type='sms',
            scheduled_for=timezone.now() + timedelta(hours=2)
        )
        
        # Simulate sending
        reminder.is_sent = True
        reminder.sent_at = timezone.now()
        reminder.status = 'sent'
        reminder.save()
        
        self.assertTrue(reminder.is_sent)
        self.assertIsNotNone(reminder.sent_at)
        self.assertEqual(reminder.status, 'sent')


class WaitingListModelTest(TestCase):
    """Test WaitingList model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='patient1',
            email='patient@test.com'
        )
        self.doctor = Doctor.objects.create(
            name='Dr. Test',
            consultation_fee=100.00
        )
        self.patient = Patient.objects.create(
            user=self.user,
            date_of_birth=datetime(1990, 1, 1).date(),
            gender='male'
        )
        self.future_date = timezone.now().date() + timedelta(days=14)
    
    def test_create_waiting_list_entry(self):
        """Test creating waiting list entry"""
        entry = WaitingList.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            preferred_date=self.future_date,
            preferred_time_start=time(9, 0),
            preferred_time_end=time(17, 0),
            appointment_type=AppointmentType.CONSULTATION,
            reason='Regular checkup',
            priority=3
        )
        
        self.assertEqual(entry.patient, self.patient)
        self.assertEqual(entry.doctor, self.doctor)
        self.assertEqual(entry.priority, 3)
        self.assertTrue(entry.is_active)
        self.assertFalse(entry.notified)
    
    def test_waiting_list_validation(self):
        """Test waiting list validation"""
        # Test past preferred date
        with self.assertRaises(ValidationError):
            entry = WaitingList(
                patient=self.patient,
                doctor=self.doctor,
                preferred_date=timezone.now().date() - timedelta(days=1),
                reason='Test'
            )
            entry.full_clean()
    
    def test_waiting_list_ordering(self):
        """Test waiting list ordering by priority"""
        # Create entries with different priorities
        WaitingList.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            preferred_date=self.future_date,
            reason='Low priority',
            priority=8
        )
        
        WaitingList.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            preferred_date=self.future_date,
            reason='High priority',
            priority=1
        )
        
        WaitingList.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            preferred_date=self.future_date,
            reason='Medium priority',
            priority=5
        )
        
        entries = list(WaitingList.objects.all())
        
        # Check ordering (highest priority first)
        self.assertEqual(entries[0].priority, 1)
        self.assertEqual(entries[1].priority, 5)
        self.assertEqual(entries[2].priority, 8)