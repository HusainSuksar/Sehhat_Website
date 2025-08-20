from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.utils import timezone
from datetime import datetime, timedelta, time
from decimal import Decimal

from appointments.models import (
    Appointment, TimeSlot, AppointmentStatus
)
from appointments.utils import (
    AppointmentScheduler, AppointmentNotificationService,
    AppointmentRemindersProcessor, WaitingListManager
)
from doctordirectory.models import Doctor, Patient, MedicalService
from moze.models import Moze

User = get_user_model()


class AppointmentIntegrationTest(TransactionTestCase):
    """Integration tests for appointment system with doctor and patient modules"""
    
    def setUp(self):
        # Create a moze (required for doctor)
        self.moze = Moze.objects.create(
            name='Test Moze',
            code='TM001',
            region='Test Region'
        )
        
        # Create doctor user and profile
        self.doctor_user = User.objects.create_user(
            username='doctor_integration',
            email='doctor@integration.com',
            password='test123',
            role='doctor',
            first_name='John',
            last_name='Smith',
            its_id='11111111'
        )
        
        self.doctor = Doctor.objects.create(
            name='Dr. John Smith',
            user=self.doctor_user,
            its_id='11111111',
            specialty='General Medicine',
            consultation_fee=200.00,
            phone='+1234567890',
            email='doctor@integration.com',
            address='123 Medical Street',
            assigned_moze=self.moze
        )
        
        # Create patient user and profile
        self.patient_user = User.objects.create_user(
            username='patient_integration',
            email='patient@integration.com',
            password='test123',
            role='student',
            first_name='Jane',
            last_name='Doe',
            its_id='22222222'
        )
        
        self.patient = Patient.objects.create(
            user=self.patient_user,
            date_of_birth=datetime(1990, 5, 15).date(),
            gender='female',
            blood_group='O+',
            emergency_contact='+9876543210'
        )
        
        # Create medical service
        self.service = MedicalService.objects.create(
            doctor=self.doctor,
            name='General Consultation',
            description='Regular health checkup',
            duration_minutes=30,
            price=200.00,
            is_available=True
        )
        
        self.future_date = timezone.now().date() + timedelta(days=7)
    
    def test_complete_appointment_workflow(self):
        """Test complete appointment workflow from booking to completion"""
        # 1. Create time slots
        time_slot = TimeSlot.objects.create(
            doctor=self.doctor,
            date=self.future_date,
            start_time=time(10, 0),
            end_time=time(12, 0),
            max_appointments=3
        )
        
        self.assertTrue(time_slot.can_book())
        
        # 2. Book appointment
        appointment = Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            service=self.service,
            time_slot=time_slot,
            appointment_date=self.future_date,
            appointment_time=time(10, 30),
            duration_minutes=30,
            reason_for_visit='Annual checkup',
            symptoms='None',
            booked_by=self.patient_user,
            booking_method='online'
        )
        
        # Check appointment details
        self.assertEqual(appointment.status, AppointmentStatus.PENDING)
        self.assertEqual(appointment.consultation_fee, Decimal('200.00'))
        self.assertFalse(appointment.is_paid)
        
        # 3. Confirm appointment
        appointment.confirm(confirmed_by=self.doctor_user)
        self.assertEqual(appointment.status, AppointmentStatus.CONFIRMED)
        self.assertIsNotNone(appointment.confirmed_at)
        
        # Check time slot update
        time_slot.refresh_from_db()
        self.assertEqual(time_slot.current_appointments, 1)
        
        # 4. Mark as in progress
        appointment.status = AppointmentStatus.IN_PROGRESS
        appointment.save()
        
        # 5. Complete appointment
        appointment.complete(
            completed_by=self.doctor_user,
            notes='Patient is in good health. Advised regular exercise.'
        )
        
        self.assertEqual(appointment.status, AppointmentStatus.COMPLETED)
        self.assertIsNotNone(appointment.completed_at)
        self.assertIn('good health', appointment.doctor_notes)
        
        # 6. Check appointment logs
        logs = appointment.logs.all()
        self.assertGreater(logs.count(), 0)
        
        # Verify log entries
        log_actions = [log.action for log in logs]
        self.assertIn('confirmed', log_actions)
        self.assertIn('completed', log_actions)
    
    def test_appointment_cancellation_workflow(self):
        """Test appointment cancellation and its effects"""
        # Create and confirm appointment
        time_slot = TimeSlot.objects.create(
            doctor=self.doctor,
            date=self.future_date,
            start_time=time(14, 0),
            end_time=time(15, 0),
            max_appointments=1
        )
        
        appointment = Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            time_slot=time_slot,
            appointment_date=self.future_date,
            appointment_time=time(14, 0),
            status=AppointmentStatus.CONFIRMED,
            reason_for_visit='Follow-up'
        )
        
        # Update time slot
        time_slot.current_appointments = 1
        time_slot.is_booked = True
        time_slot.save()
        
        # Cancel appointment
        appointment.cancel(
            cancelled_by=self.patient_user,
            reason='Emergency travel'
        )
        
        # Check appointment status
        self.assertEqual(appointment.status, AppointmentStatus.CANCELLED)
        self.assertEqual(appointment.cancelled_by, self.patient_user)
        self.assertEqual(appointment.cancellation_reason, 'Emergency travel')
        
        # Check time slot is freed
        time_slot.refresh_from_db()
        self.assertEqual(time_slot.current_appointments, 0)
        self.assertFalse(time_slot.is_booked)
    
    def test_appointment_rescheduling(self):
        """Test appointment rescheduling creates new appointment"""
        # Original appointment
        original = Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            appointment_date=self.future_date,
            appointment_time=time(11, 0),
            status=AppointmentStatus.CONFIRMED,
            reason_for_visit='Consultation'
        )
        
        # Create new appointment as rescheduled
        new_date = self.future_date + timedelta(days=2)
        new_appointment = Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            appointment_date=new_date,
            appointment_time=time(15, 0),
            status=AppointmentStatus.SCHEDULED,
            reason_for_visit='Consultation',
            rescheduled_from=original
        )
        
        # Cancel original
        original.cancel(
            cancelled_by=self.patient_user,
            reason=f'Rescheduled to {new_date}'
        )
        
        # Verify relationships
        self.assertEqual(new_appointment.rescheduled_from, original)
        self.assertEqual(original.status, AppointmentStatus.CANCELLED)
        self.assertEqual(new_appointment.status, AppointmentStatus.SCHEDULED)
    
    def test_doctor_availability_checking(self):
        """Test doctor availability checking functionality"""
        # Create multiple time slots
        for hour in [9, 10, 11, 14, 15]:
            TimeSlot.objects.create(
                doctor=self.doctor,
                date=self.future_date,
                start_time=time(hour, 0),
                end_time=time(hour + 1, 0),
                max_appointments=2
            )
        
        # Check availability
        available_slots = AppointmentScheduler.get_available_slots(
            self.doctor,
            self.future_date,
            duration_minutes=30
        )
        
        self.assertEqual(len(available_slots), 5)
        
        # Book some appointments
        for hour in [9, 10]:
            for i in range(2):  # Fill these slots
                Appointment.objects.create(
                    doctor=self.doctor,
                    patient=self.patient,
                    appointment_date=self.future_date,
                    appointment_time=time(hour, i * 30),
                    status=AppointmentStatus.CONFIRMED,
                    reason_for_visit=f'Appointment {hour}:{i*30}'
                )
        
        # Check availability again
        available_slots = AppointmentScheduler.get_available_slots(
            self.doctor,
            self.future_date,
            duration_minutes=30
        )
        
        # Should have 3 slots left (11, 14, 15)
        self.assertEqual(len(available_slots), 3)
    
    def test_appointment_conflict_prevention(self):
        """Test that conflicting appointments cannot be created"""
        # Create first appointment
        appointment1 = Appointment.objects.create(
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
            appointment2 = Appointment(
                doctor=self.doctor,
                patient=self.patient,
                appointment_date=self.future_date,
                appointment_time=time(10, 0),
                duration_minutes=30,
                reason_for_visit='Conflicting appointment'
            )
            appointment2.clean()
    
    def test_patient_appointment_history(self):
        """Test patient appointment history tracking"""
        # Create multiple appointments
        appointments = []
        for i in range(5):
            appointment_date = self.future_date + timedelta(days=i*7)
            appointment = Appointment.objects.create(
                doctor=self.doctor,
                patient=self.patient,
                appointment_date=appointment_date,
                appointment_time=time(10, 0),
                status=AppointmentStatus.COMPLETED if i < 3 else AppointmentStatus.SCHEDULED,
                reason_for_visit=f'Visit {i+1}'
            )
            appointments.append(appointment)
        
        # Get patient appointments
        patient_appointments = Appointment.objects.filter(patient=self.patient)
        self.assertEqual(patient_appointments.count(), 5)
        
        # Check completed appointments
        completed = patient_appointments.filter(status=AppointmentStatus.COMPLETED)
        self.assertEqual(completed.count(), 3)
        
        # Check upcoming appointments
        upcoming = patient_appointments.filter(
            status=AppointmentStatus.SCHEDULED,
            appointment_date__gte=timezone.now().date()
        )
        self.assertEqual(upcoming.count(), 2)
    
    def test_doctor_schedule_management(self):
        """Test doctor schedule and appointment management"""
        # Create recurring time slots
        weekdays = [0, 1, 2, 3, 4]  # Monday to Friday
        time_slots_config = [
            {'start_time': time(9, 0), 'end_time': time(9, 30), 'max_appointments': 2},
            {'start_time': time(9, 30), 'end_time': time(10, 0), 'max_appointments': 2},
            {'start_time': time(10, 0), 'end_time': time(10, 30), 'max_appointments': 2},
        ]
        
        created_slots = AppointmentScheduler.create_recurring_slots(
            self.doctor,
            self.future_date,
            self.future_date + timedelta(days=7),
            time_slots_config,
            weekdays
        )
        
        # Should create 3 slots per weekday
        expected_slots = 3 * len([d for d in range(8) if (self.future_date + timedelta(days=d)).weekday() in weekdays])
        self.assertEqual(len(created_slots), expected_slots)
        
        # Verify doctor's schedule
        doctor_slots = TimeSlot.objects.filter(
            doctor=self.doctor,
            date__gte=self.future_date,
            date__lte=self.future_date + timedelta(days=7)
        )
        self.assertEqual(doctor_slots.count(), expected_slots)
    
    def test_appointment_reminders_integration(self):
        """Test appointment reminders creation and processing"""
        # Create appointment
        appointment = Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            appointment_date=self.future_date,
            appointment_time=time(14, 0),
            status=AppointmentStatus.CONFIRMED,
            reason_for_visit='Checkup'
        )
        
        # Schedule default reminders
        reminders = AppointmentRemindersProcessor.schedule_default_reminders(appointment)
        
        self.assertEqual(len(reminders), 2)  # 24h and 2h reminders
        
        # Check reminder details
        reminder_types = [r.reminder_type for r in reminders]
        self.assertIn('email', reminder_types)
        self.assertIn('sms', reminder_types)
        
        # All reminders should be pending
        for reminder in reminders:
            self.assertEqual(reminder.status, 'pending')
            self.assertFalse(reminder.is_sent)
    
    def test_waiting_list_integration(self):
        """Test waiting list functionality with appointments"""
        from appointments.models import WaitingList
        
        # Create waiting list entry
        waiting_entry = WaitingList.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            preferred_date=self.future_date,
            preferred_time_start=time(10, 0),
            preferred_time_end=time(12, 0),
            appointment_type='consultation',
            reason='Regular checkup',
            priority=3
        )
        
        self.assertTrue(waiting_entry.is_active)
        self.assertFalse(waiting_entry.notified)
        
        # Create a time slot that matches waiting list preference
        time_slot = TimeSlot.objects.create(
            doctor=self.doctor,
            date=self.future_date,
            start_time=time(10, 30),
            end_time=time(11, 0)
        )
        
        # Check and notify waiting list
        notified_count = WaitingListManager.check_and_notify_waiting_list(
            self.doctor,
            self.future_date,
            time_slot
        )
        
        self.assertEqual(notified_count, 1)
        
        # Verify notification
        waiting_entry.refresh_from_db()
        self.assertTrue(waiting_entry.notified)
    
    def test_appointment_payment_tracking(self):
        """Test appointment payment tracking"""
        # Create paid appointment
        paid_appointment = Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            appointment_date=self.future_date,
            appointment_time=time(9, 0),
            status=AppointmentStatus.COMPLETED,
            consultation_fee=250.00,
            is_paid=True,
            payment_method='card',
            reason_for_visit='Consultation'
        )
        
        # Create unpaid appointment
        unpaid_appointment = Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            appointment_date=self.future_date + timedelta(days=1),
            appointment_time=time(10, 0),
            status=AppointmentStatus.COMPLETED,
            consultation_fee=250.00,
            is_paid=False,
            reason_for_visit='Follow-up'
        )
        
        # Calculate doctor's revenue
        completed_appointments = Appointment.objects.filter(
            doctor=self.doctor,
            status=AppointmentStatus.COMPLETED,
            is_paid=True
        )
        
        total_revenue = sum(app.consultation_fee for app in completed_appointments)
        self.assertEqual(total_revenue, Decimal('250.00'))
        
        # Verify unpaid appointments
        unpaid = Appointment.objects.filter(
            doctor=self.doctor,
            status=AppointmentStatus.COMPLETED,
            is_paid=False
        )
        self.assertEqual(unpaid.count(), 1)
        self.assertEqual(unpaid.first(), unpaid_appointment)