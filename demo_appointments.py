#!/usr/bin/env python3
"""
Appointment Module Demonstration Script
This script demonstrates all the functionality of the appointment module
"""

import os
import sys
from datetime import datetime, timedelta, time
from decimal import Decimal
import json

# Add the project to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')

# Mock Django setup for demonstration
class MockUser:
    def __init__(self, username, email, role, first_name, last_name):
        self.id = id(self)
        self.username = username
        self.email = email
        self.role = role
        self.first_name = first_name
        self.last_name = last_name
        self.is_authenticated = True
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __str__(self):
        return self.get_full_name()

class MockDoctor:
    def __init__(self, name, user, specialty, consultation_fee):
        self.id = id(self)
        self.name = name
        self.user = user
        self.specialty = specialty
        self.consultation_fee = consultation_fee
        self.phone = "+1234567890"
        self.email = user.email
        self.address = "123 Medical Center"
        self.is_available = True
    
    def get_full_name(self):
        return f"Dr. {self.user.get_full_name()}"
    
    def __str__(self):
        return self.get_full_name()

class MockPatient:
    def __init__(self, user, date_of_birth, gender):
        self.id = id(self)
        self.user = user
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.blood_group = "O+"
        self.emergency_contact = "+9876543210"
    
    def __str__(self):
        return self.user.get_full_name()

class MockTimeSlot:
    def __init__(self, doctor, date, start_time, end_time, max_appointments=2):
        self.id = id(self)
        self.doctor = doctor
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.max_appointments = max_appointments
        self.current_appointments = 0
        self.is_available = True
        self.is_booked = False
    
    def can_book(self):
        return (self.is_available and 
                not self.is_booked and 
                self.current_appointments < self.max_appointments)
    
    @property
    def duration_minutes(self):
        start_dt = datetime.combine(self.date, self.start_time)
        end_dt = datetime.combine(self.date, self.end_time)
        return int((end_dt - start_dt).total_seconds() / 60)
    
    def __str__(self):
        return f"{self.doctor.name} - {self.date} {self.start_time}-{self.end_time}"

class MockAppointment:
    STATUS_CHOICES = {
        'pending': 'Pending Confirmation',
        'confirmed': 'Confirmed',
        'scheduled': 'Scheduled',
        'in_progress': 'In Progress',
        'completed': 'Completed',
        'cancelled': 'Cancelled',
        'no_show': 'No Show',
        'rescheduled': 'Rescheduled'
    }
    
    def __init__(self, doctor, patient, appointment_date, appointment_time, **kwargs):
        self.id = id(self)
        self.appointment_id = f"APT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{self.id % 1000:03d}"
        self.doctor = doctor
        self.patient = patient
        self.appointment_date = appointment_date
        self.appointment_time = appointment_time
        self.duration_minutes = kwargs.get('duration_minutes', 30)
        self.status = kwargs.get('status', 'pending')
        self.appointment_type = kwargs.get('appointment_type', 'consultation')
        self.reason_for_visit = kwargs.get('reason_for_visit', '')
        self.symptoms = kwargs.get('symptoms', '')
        self.consultation_fee = kwargs.get('consultation_fee', doctor.consultation_fee)
        self.is_paid = kwargs.get('is_paid', False)
        self.payment_method = kwargs.get('payment_method', '')
        self.booked_by = kwargs.get('booked_by', patient.user)
        self.booking_method = kwargs.get('booking_method', 'online')
        self.time_slot = kwargs.get('time_slot', None)
        self.notes = kwargs.get('notes', '')
        self.doctor_notes = kwargs.get('doctor_notes', '')
        
        # Timestamps
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.confirmed_at = None
        self.cancelled_at = None
        self.completed_at = None
        self.cancelled_by = None
        self.cancellation_reason = ''
        
        # Logs
        self.logs = []
        self._add_log('created', self.booked_by, f'Appointment created by {self.booked_by}')
    
    def _add_log(self, action, user, notes=''):
        log = {
            'id': len(self.logs) + 1,
            'action': action,
            'performed_by': user,
            'timestamp': datetime.now(),
            'notes': notes
        }
        self.logs.append(log)
    
    def get_status_display(self):
        return self.STATUS_CHOICES.get(self.status, self.status)
    
    @property
    def end_time(self):
        start_dt = datetime.combine(self.appointment_date, self.appointment_time)
        end_dt = start_dt + timedelta(minutes=self.duration_minutes)
        return end_dt.time()
    
    @property
    def is_upcoming(self):
        appointment_dt = datetime.combine(self.appointment_date, self.appointment_time)
        return appointment_dt > datetime.now()
    
    @property
    def is_past(self):
        return not self.is_upcoming
    
    def can_cancel(self):
        return self.status not in ['completed', 'cancelled'] and self.is_upcoming
    
    def can_reschedule(self):
        return self.can_cancel()
    
    def confirm(self, confirmed_by):
        if self.status == 'pending':
            self.status = 'confirmed'
            self.confirmed_at = datetime.now()
            self.updated_at = datetime.now()
            self._add_log('confirmed', confirmed_by, 'Appointment confirmed')
            if self.time_slot:
                self.time_slot.current_appointments += 1
            return True
        return False
    
    def cancel(self, cancelled_by, reason=''):
        if self.can_cancel():
            self.status = 'cancelled'
            self.cancelled_at = datetime.now()
            self.cancelled_by = cancelled_by
            self.cancellation_reason = reason
            self.updated_at = datetime.now()
            self._add_log('cancelled', cancelled_by, f'Appointment cancelled. Reason: {reason}')
            if self.time_slot:
                self.time_slot.current_appointments -= 1
            return True
        return False
    
    def complete(self, completed_by, notes=''):
        if self.status in ['confirmed', 'scheduled', 'in_progress']:
            self.status = 'completed'
            self.completed_at = datetime.now()
            if notes:
                self.doctor_notes = notes
            self.updated_at = datetime.now()
            self._add_log('completed', completed_by, 'Appointment completed')
            return True
        return False
    
    def __str__(self):
        return f"{self.appointment_id} - {self.patient.user.get_full_name()} with {self.doctor.get_full_name()}"

class MockReminder:
    def __init__(self, appointment, reminder_type, scheduled_for):
        self.id = id(self)
        self.appointment = appointment
        self.reminder_type = reminder_type
        self.scheduled_for = scheduled_for
        self.is_sent = False
        self.sent_at = None
        self.status = 'pending'
        self.created_at = datetime.now()

class MockWaitingList:
    def __init__(self, patient, doctor, preferred_date, **kwargs):
        self.id = id(self)
        self.patient = patient
        self.doctor = doctor
        self.preferred_date = preferred_date
        self.preferred_time_start = kwargs.get('preferred_time_start')
        self.preferred_time_end = kwargs.get('preferred_time_end')
        self.appointment_type = kwargs.get('appointment_type', 'consultation')
        self.reason = kwargs.get('reason', '')
        self.priority = kwargs.get('priority', 5)
        self.is_active = True
        self.notified = False
        self.created_at = datetime.now()

# Demonstration Functions
def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'=' * 60}")
    print(f"{title.upper()}")
    print(f"{'=' * 60}")

def print_success(message):
    """Print success message"""
    print(f"✓ {message}")

def print_info(message):
    """Print info message"""
    print(f"  {message}")

def print_error(message):
    """Print error message"""
    print(f"✗ {message}")

def demonstrate_user_creation():
    """Demonstrate user and profile creation"""
    print_section("1. Creating Users and Profiles")
    
    # Create doctor user
    doctor_user = MockUser(
        username="dr_smith",
        email="dr.smith@hospital.com",
        role="doctor",
        first_name="John",
        last_name="Smith"
    )
    print_success(f"Created doctor user: {doctor_user.get_full_name()}")
    
    # Create doctor profile
    doctor = MockDoctor(
        name="Dr. John Smith",
        user=doctor_user,
        specialty="General Medicine",
        consultation_fee=Decimal("150.00")
    )
    print_success(f"Created doctor profile: {doctor.get_full_name()}")
    print_info(f"Specialty: {doctor.specialty}")
    print_info(f"Consultation Fee: ${doctor.consultation_fee}")
    
    # Create patient user
    patient_user = MockUser(
        username="jane_doe",
        email="jane.doe@email.com",
        role="student",
        first_name="Jane",
        last_name="Doe"
    )
    print_success(f"Created patient user: {patient_user.get_full_name()}")
    
    # Create patient profile
    patient = MockPatient(
        user=patient_user,
        date_of_birth=datetime(1990, 5, 15).date(),
        gender="female"
    )
    print_success(f"Created patient profile: {patient.user.get_full_name()}")
    print_info(f"Date of Birth: {patient.date_of_birth}")
    print_info(f"Blood Group: {patient.blood_group}")
    
    return doctor, patient

def demonstrate_time_slot_creation(doctor):
    """Demonstrate time slot creation"""
    print_section("2. Creating Time Slots")
    
    future_date = datetime.now().date() + timedelta(days=1)
    time_slots = []
    
    # Create morning slots
    morning_slots = [
        (time(9, 0), time(9, 30)),
        (time(9, 30), time(10, 0)),
        (time(10, 0), time(10, 30)),
        (time(10, 30), time(11, 0)),
        (time(11, 0), time(11, 30))
    ]
    
    for start, end in morning_slots:
        slot = MockTimeSlot(
            doctor=doctor,
            date=future_date,
            start_time=start,
            end_time=end,
            max_appointments=2
        )
        time_slots.append(slot)
    
    print_success(f"Created {len(morning_slots)} morning time slots for {future_date}")
    
    # Create afternoon slots
    afternoon_slots = [
        (time(14, 0), time(14, 30)),
        (time(14, 30), time(15, 0)),
        (time(15, 0), time(15, 30)),
        (time(15, 30), time(16, 0))
    ]
    
    for start, end in afternoon_slots:
        slot = MockTimeSlot(
            doctor=doctor,
            date=future_date,
            start_time=start,
            end_time=end,
            max_appointments=2
        )
        time_slots.append(slot)
    
    print_success(f"Created {len(afternoon_slots)} afternoon time slots")
    
    # Display available slots
    print_info(f"\nAvailable time slots for {future_date}:")
    for slot in time_slots:
        print_info(f"  {slot.start_time.strftime('%I:%M %p')} - {slot.end_time.strftime('%I:%M %p')}: "
                  f"{slot.max_appointments - slot.current_appointments} slots available")
    
    return time_slots

def demonstrate_appointment_booking(doctor, patient, time_slots):
    """Demonstrate appointment booking process"""
    print_section("3. Booking an Appointment")
    
    # Select a time slot
    selected_slot = time_slots[2]  # 10:00 - 10:30
    
    print_info(f"Selected time slot: {selected_slot.start_time.strftime('%I:%M %p')} - "
              f"{selected_slot.end_time.strftime('%I:%M %p')}")
    
    # Check if slot is available
    if selected_slot.can_book():
        print_success("Time slot is available for booking")
    else:
        print_error("Time slot is not available")
        return None
    
    # Create appointment
    appointment = MockAppointment(
        doctor=doctor,
        patient=patient,
        appointment_date=selected_slot.date,
        appointment_time=selected_slot.start_time,
        duration_minutes=30,
        appointment_type='consultation',
        reason_for_visit='Regular health checkup',
        symptoms='None - routine checkup',
        time_slot=selected_slot,
        booking_method='online',
        booked_by=patient.user
    )
    
    print_success(f"Appointment created successfully!")
    print_info(f"Appointment ID: {appointment.appointment_id}")
    print_info(f"Date: {appointment.appointment_date}")
    print_info(f"Time: {appointment.appointment_time.strftime('%I:%M %p')} - {appointment.end_time.strftime('%I:%M %p')}")
    print_info(f"Status: {appointment.get_status_display()}")
    print_info(f"Consultation Fee: ${appointment.consultation_fee}")
    print_info(f"Payment Status: {'Paid' if appointment.is_paid else 'Unpaid'}")
    
    return appointment

def demonstrate_appointment_confirmation(appointment, doctor):
    """Demonstrate appointment confirmation"""
    print_section("4. Confirming the Appointment")
    
    print_info(f"Current status: {appointment.get_status_display()}")
    
    # Confirm appointment
    if appointment.confirm(confirmed_by=doctor.user):
        print_success("Appointment confirmed successfully!")
        print_info(f"New status: {appointment.get_status_display()}")
        print_info(f"Confirmed at: {appointment.confirmed_at.strftime('%Y-%m-%d %I:%M %p')}")
        print_info(f"Time slot bookings: {appointment.time_slot.current_appointments}/{appointment.time_slot.max_appointments}")
    else:
        print_error("Failed to confirm appointment")

def demonstrate_reminders(appointment):
    """Demonstrate appointment reminders"""
    print_section("5. Setting Up Appointment Reminders")
    
    appointment_dt = datetime.combine(appointment.appointment_date, appointment.appointment_time)
    reminders = []
    
    # 24 hours before
    reminder1 = MockReminder(
        appointment=appointment,
        reminder_type='email',
        scheduled_for=appointment_dt - timedelta(hours=24)
    )
    reminders.append(reminder1)
    print_success(f"Created 24-hour email reminder")
    print_info(f"Scheduled for: {reminder1.scheduled_for.strftime('%Y-%m-%d %I:%M %p')}")
    
    # 2 hours before
    reminder2 = MockReminder(
        appointment=appointment,
        reminder_type='sms',
        scheduled_for=appointment_dt - timedelta(hours=2)
    )
    reminders.append(reminder2)
    print_success(f"Created 2-hour SMS reminder")
    print_info(f"Scheduled for: {reminder2.scheduled_for.strftime('%Y-%m-%d %I:%M %p')}")
    
    return reminders

def demonstrate_appointment_management(appointment, doctor):
    """Demonstrate appointment management features"""
    print_section("6. Appointment Management Features")
    
    # Check appointment capabilities
    print_info("Appointment capabilities:")
    print_info(f"  Can cancel: {appointment.can_cancel()}")
    print_info(f"  Can reschedule: {appointment.can_reschedule()}")
    print_info(f"  Is upcoming: {appointment.is_upcoming}")
    print_info(f"  Is past: {appointment.is_past}")
    
    # Display appointment logs
    print_info("\nAppointment history:")
    for log in appointment.logs:
        print_info(f"  [{log['timestamp'].strftime('%H:%M:%S')}] {log['action'].upper()}: {log['notes']}")

def demonstrate_rescheduling(doctor, patient, appointment, time_slots):
    """Demonstrate appointment rescheduling"""
    print_section("7. Rescheduling an Appointment")
    
    # Select new time slot
    new_slot = time_slots[6]  # 2:30 PM
    new_date = new_slot.date + timedelta(days=1)
    
    print_info(f"Original appointment: {appointment.appointment_date} at {appointment.appointment_time.strftime('%I:%M %p')}")
    print_info(f"New proposed time: {new_date} at {new_slot.start_time.strftime('%I:%M %p')}")
    
    # Create new appointment
    new_appointment = MockAppointment(
        doctor=doctor,
        patient=patient,
        appointment_date=new_date,
        appointment_time=new_slot.start_time,
        duration_minutes=appointment.duration_minutes,
        appointment_type=appointment.appointment_type,
        reason_for_visit=appointment.reason_for_visit,
        symptoms=appointment.symptoms,
        consultation_fee=appointment.consultation_fee,
        status='scheduled',
        booked_by=patient.user
    )
    
    # Cancel original appointment
    if appointment.cancel(cancelled_by=patient.user, reason=f"Rescheduled to {new_date}"):
        print_success("Original appointment cancelled")
        print_success(f"New appointment created: {new_appointment.appointment_id}")
        print_info(f"New date: {new_appointment.appointment_date}")
        print_info(f"New time: {new_appointment.appointment_time.strftime('%I:%M %p')}")
        return new_appointment
    else:
        print_error("Failed to reschedule appointment")
        return None

def demonstrate_waiting_list(doctor, patient):
    """Demonstrate waiting list functionality"""
    print_section("8. Waiting List Management")
    
    preferred_date = datetime.now().date() + timedelta(days=7)
    
    waiting_entry = MockWaitingList(
        patient=patient,
        doctor=doctor,
        preferred_date=preferred_date,
        preferred_time_start=time(9, 0),
        preferred_time_end=time(12, 0),
        appointment_type='consultation',
        reason='Prefer morning appointment for follow-up',
        priority=3
    )
    
    print_success("Added to waiting list")
    print_info(f"Preferred date: {waiting_entry.preferred_date}")
    print_info(f"Preferred time: {waiting_entry.preferred_time_start.strftime('%I:%M %p')} - "
              f"{waiting_entry.preferred_time_end.strftime('%I:%M %p')}")
    print_info(f"Priority: {waiting_entry.priority} (1=highest, 10=lowest)")
    print_info(f"Reason: {waiting_entry.reason}")
    
    return waiting_entry

def demonstrate_appointment_completion(appointment, doctor):
    """Demonstrate completing an appointment"""
    print_section("9. Completing an Appointment")
    
    # Mark appointment as in progress
    appointment.status = 'in_progress'
    appointment._add_log('in_progress', doctor.user, 'Patient arrived, consultation started')
    print_success("Appointment marked as in progress")
    
    # Complete appointment
    doctor_notes = "Patient is in good health. Advised regular exercise and balanced diet. Follow-up in 3 months."
    
    if appointment.complete(completed_by=doctor.user, notes=doctor_notes):
        print_success("Appointment completed successfully!")
        print_info(f"Completed at: {appointment.completed_at.strftime('%Y-%m-%d %I:%M %p')}")
        print_info(f"Doctor's notes: {appointment.doctor_notes}")
        
        # Mark as paid
        appointment.is_paid = True
        appointment.payment_method = 'card'
        print_success(f"Payment received: ${appointment.consultation_fee} via {appointment.payment_method}")
    else:
        print_error("Failed to complete appointment")

def demonstrate_statistics(doctor, appointments):
    """Demonstrate appointment statistics"""
    print_section("10. Appointment Statistics and Analytics")
    
    # Calculate statistics
    total = len(appointments)
    completed = sum(1 for a in appointments if a.status == 'completed')
    cancelled = sum(1 for a in appointments if a.status == 'cancelled')
    revenue = sum(a.consultation_fee for a in appointments if a.status == 'completed' and a.is_paid)
    
    print_info(f"Total appointments: {total}")
    print_info(f"Completed: {completed}")
    print_info(f"Cancelled: {cancelled}")
    print_info(f"Total revenue: ${revenue}")
    
    # Status breakdown
    print_info("\nAppointments by status:")
    status_counts = {}
    for appointment in appointments:
        status = appointment.get_status_display()
        status_counts[status] = status_counts.get(status, 0) + 1
    
    for status, count in status_counts.items():
        print_info(f"  {status}: {count}")

def demonstrate_api_examples():
    """Show API endpoint examples"""
    print_section("11. API Endpoint Examples")
    
    print_info("Book an appointment:")
    print_info("POST /api/appointments/appointments/")
    print(json.dumps({
        "doctor": 1,
        "patient": 1,
        "appointment_date": "2024-12-30",
        "appointment_time": "10:00",
        "duration_minutes": 30,
        "appointment_type": "consultation",
        "reason_for_visit": "Regular checkup"
    }, indent=2))
    
    print_info("\nCheck doctor availability:")
    print_info("POST /api/appointments/check-availability/")
    print(json.dumps({
        "doctor_id": 1,
        "date": "2024-12-30",
        "duration_minutes": 30
    }, indent=2))
    
    print_info("\nCancel appointment:")
    print_info("POST /api/appointments/appointments/{id}/cancel/")
    print(json.dumps({
        "cancellation_reason": "Unable to attend due to emergency"
    }, indent=2))
    
    print_info("\nReschedule appointment:")
    print_info("POST /api/appointments/appointments/{id}/reschedule/")
    print(json.dumps({
        "new_date": "2024-12-31",
        "new_time": "14:00",
        "reason": "Schedule conflict"
    }, indent=2))

def main():
    """Main demonstration function"""
    print("\n" + "=" * 60)
    print("APPOINTMENT MODULE COMPREHENSIVE DEMONSTRATION")
    print("=" * 60)
    
    try:
        # Track all appointments for statistics
        all_appointments = []
        
        # 1. Create users and profiles
        doctor, patient = demonstrate_user_creation()
        
        # 2. Create time slots
        time_slots = demonstrate_time_slot_creation(doctor)
        
        # 3. Book appointment
        appointment = demonstrate_appointment_booking(doctor, patient, time_slots)
        if appointment:
            all_appointments.append(appointment)
        
        # 4. Confirm appointment
        if appointment:
            demonstrate_appointment_confirmation(appointment, doctor)
        
        # 5. Set up reminders
        if appointment:
            reminders = demonstrate_reminders(appointment)
        
        # 6. Show management features
        if appointment:
            demonstrate_appointment_management(appointment, doctor)
        
        # 7. Demonstrate rescheduling
        if appointment:
            new_appointment = demonstrate_rescheduling(doctor, patient, appointment, time_slots)
            if new_appointment:
                all_appointments.append(new_appointment)
        
        # 8. Waiting list
        waiting_entry = demonstrate_waiting_list(doctor, patient)
        
        # 9. Complete an appointment
        # Create another appointment to complete
        completion_appointment = MockAppointment(
            doctor=doctor,
            patient=patient,
            appointment_date=datetime.now().date(),
            appointment_time=time(14, 0),
            duration_minutes=30,
            appointment_type='follow_up',
            reason_for_visit='Follow-up visit',
            status='confirmed'
        )
        all_appointments.append(completion_appointment)
        demonstrate_appointment_completion(completion_appointment, doctor)
        
        # 10. Show statistics
        demonstrate_statistics(doctor, all_appointments)
        
        # 11. API examples
        demonstrate_api_examples()
        
        print("\n" + "=" * 60)
        print("DEMONSTRATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
        print("\nSummary of Features Demonstrated:")
        print("✓ User and profile creation (Doctor & Patient)")
        print("✓ Time slot management")
        print("✓ Appointment booking with validation")
        print("✓ Appointment confirmation workflow")
        print("✓ Reminder scheduling")
        print("✓ Appointment rescheduling")
        print("✓ Waiting list management")
        print("✓ Appointment completion and payment")
        print("✓ Statistics and analytics")
        print("✓ Complete audit trail (logs)")
        print("✓ API endpoint examples")
        
        print("\nKey Features of the Appointment Module:")
        print("• Prevents double-booking through time slot management")
        print("• Tracks complete appointment lifecycle")
        print("• Supports multiple appointment types")
        print("• Automated reminder system")
        print("• Payment tracking and revenue calculation")
        print("• Comprehensive logging and audit trail")
        print("• RESTful API for integration")
        print("• Role-based access control")
        print("• Waiting list for fully booked slots")
        print("• Statistics and reporting capabilities")
        
    except Exception as e:
        print(f"\n✗ Error during demonstration: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()