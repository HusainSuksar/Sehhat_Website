#!/usr/bin/env python
"""
Test script to demonstrate the appointment module functionality
Run this after setting up the database and running migrations
"""

import os
import sys
import django
from datetime import datetime, timedelta, time
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from appointments.models import (
    Appointment, TimeSlot, AppointmentStatus, AppointmentType,
    AppointmentReminder, WaitingList
)
from appointments.utils import AppointmentScheduler, AppointmentRemindersProcessor
from doctordirectory.models import Doctor, Patient, MedicalService
from moze.models import Moze

User = get_user_model()


def create_test_data():
    """Create test data for demonstration"""
    print("Creating test data...")
    
    # Create a moze
    moze, created = Moze.objects.get_or_create(
        code='TM001',
        defaults={
            'name': 'Test Medical Center',
            'region': 'Test Region',
            'address': '123 Test Street'
        }
    )
    print(f"✓ Moze: {moze.name}")
    
    # Create doctor user
    doctor_user, created = User.objects.get_or_create(
        username='dr_smith',
        defaults={
            'email': 'dr.smith@test.com',
            'first_name': 'John',
            'last_name': 'Smith',
            'role': 'doctor',
            'its_id': '11111111'
        }
    )
    if created:
        doctor_user.set_password('doctor123')
        doctor_user.save()
    print(f"✓ Doctor User: {doctor_user.get_full_name()}")
    
    # Create doctor profile
    doctor, created = Doctor.objects.get_or_create(
        user=doctor_user,
        defaults={
            'name': 'Dr. John Smith',
            'specialty': 'General Medicine',
            'qualification': 'MBBS, MD',
            'experience_years': 10,
            'consultation_fee': 150.00,
            'phone': '+1234567890',
            'email': 'dr.smith@test.com',
            'address': '456 Medical Plaza',
            'assigned_moze': moze,
            'is_verified': True,
            'is_available': True
        }
    )
    print(f"✓ Doctor Profile: {doctor.get_full_name()}")
    
    # Create patient user
    patient_user, created = User.objects.get_or_create(
        username='jane_doe',
        defaults={
            'email': 'jane.doe@test.com',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'role': 'student',
            'its_id': '22222222',
            'age': 28,
            'gender': 'female'
        }
    )
    if created:
        patient_user.set_password('patient123')
        patient_user.save()
    print(f"✓ Patient User: {patient_user.get_full_name()}")
    
    # Create patient profile
    patient, created = Patient.objects.get_or_create(
        user=patient_user,
        defaults={
            'date_of_birth': datetime(1995, 6, 15).date(),
            'gender': 'female',
            'blood_group': 'O+',
            'emergency_contact': '+9876543210',
            'medical_history': 'No major health issues',
            'allergies': 'None'
        }
    )
    print(f"✓ Patient Profile: {patient.user.get_full_name()}")
    
    # Create medical services
    services = []
    service_data = [
        ('General Consultation', 'Regular health checkup', 30, 150.00),
        ('Follow-up Visit', 'Follow-up consultation', 20, 100.00),
        ('Comprehensive Checkup', 'Complete health examination', 60, 300.00)
    ]
    
    for name, desc, duration, price in service_data:
        service, created = MedicalService.objects.get_or_create(
            doctor=doctor,
            name=name,
            defaults={
                'description': desc,
                'duration_minutes': duration,
                'price': price,
                'is_available': True
            }
        )
        services.append(service)
    print(f"✓ Medical Services: {len(services)} services created")
    
    return doctor, patient, services[0]


def create_time_slots(doctor):
    """Create time slots for the doctor"""
    print("\nCreating time slots...")
    
    # Get dates for next 7 days
    start_date = timezone.now().date() + timedelta(days=1)
    end_date = start_date + timedelta(days=6)
    
    # Define time slot configuration
    time_slots_config = [
        {'start_time': time(9, 0), 'end_time': time(9, 30), 'max_appointments': 2},
        {'start_time': time(9, 30), 'end_time': time(10, 0), 'max_appointments': 2},
        {'start_time': time(10, 0), 'end_time': time(10, 30), 'max_appointments': 2},
        {'start_time': time(10, 30), 'end_time': time(11, 0), 'max_appointments': 2},
        {'start_time': time(11, 0), 'end_time': time(11, 30), 'max_appointments': 2},
        {'start_time': time(14, 0), 'end_time': time(14, 30), 'max_appointments': 2},
        {'start_time': time(14, 30), 'end_time': time(15, 0), 'max_appointments': 2},
        {'start_time': time(15, 0), 'end_time': time(15, 30), 'max_appointments': 2},
        {'start_time': time(15, 30), 'end_time': time(16, 0), 'max_appointments': 2},
        {'start_time': time(16, 0), 'end_time': time(16, 30), 'max_appointments': 2},
    ]
    
    # Create recurring slots for weekdays
    weekdays = [0, 1, 2, 3, 4]  # Monday to Friday
    
    created_slots = AppointmentScheduler.create_recurring_slots(
        doctor,
        start_date,
        end_date,
        time_slots_config,
        weekdays
    )
    
    print(f"✓ Created {len(created_slots)} time slots")
    print(f"  - Date range: {start_date} to {end_date}")
    print(f"  - Time range: 9:00 AM to 4:30 PM")
    print(f"  - Weekdays only (Mon-Fri)")
    
    return created_slots


def demonstrate_appointment_booking(doctor, patient, service):
    """Demonstrate appointment booking process"""
    print("\nDemonstrating appointment booking...")
    
    # Get tomorrow's date
    appointment_date = timezone.now().date() + timedelta(days=1)
    
    # Check available slots
    available_slots = AppointmentScheduler.get_available_slots(
        doctor,
        appointment_date,
        duration_minutes=30
    )
    
    print(f"✓ Found {len(available_slots)} available slots for {appointment_date}")
    
    if available_slots:
        # Book first available slot
        first_slot = available_slots[0]['slot']
        
        appointment = Appointment.objects.create(
            doctor=doctor,
            patient=patient,
            service=service,
            time_slot=first_slot,
            appointment_date=appointment_date,
            appointment_time=first_slot.start_time,
            duration_minutes=30,
            appointment_type=AppointmentType.CONSULTATION,
            reason_for_visit='Regular health checkup',
            symptoms='None - routine checkup',
            booking_method='online',
            booked_by=patient.user
        )
        
        print(f"✓ Appointment booked:")
        print(f"  - ID: {str(appointment.appointment_id)[:8]}...")
        print(f"  - Date: {appointment.appointment_date}")
        print(f"  - Time: {appointment.appointment_time.strftime('%I:%M %p')}")
        print(f"  - Status: {appointment.get_status_display()}")
        print(f"  - Fee: ${appointment.consultation_fee}")
        
        # Schedule reminders
        reminders = AppointmentRemindersProcessor.schedule_default_reminders(appointment)
        print(f"✓ Scheduled {len(reminders)} reminders")
        
        return appointment
    else:
        print("✗ No available slots found")
        return None


def demonstrate_appointment_management(appointment):
    """Demonstrate appointment management operations"""
    print("\nDemonstrating appointment management...")
    
    if not appointment:
        print("✗ No appointment to manage")
        return
    
    # 1. Confirm appointment
    appointment.confirm(confirmed_by=appointment.doctor.user)
    print(f"✓ Appointment confirmed at {appointment.confirmed_at.strftime('%Y-%m-%d %H:%M')}")
    
    # 2. Create appointment log
    from appointments.models import AppointmentLog
    log = AppointmentLog.objects.create(
        appointment=appointment,
        action='confirmed',
        performed_by=appointment.doctor.user,
        notes='Appointment confirmed by doctor'
    )
    print(f"✓ Created appointment log: {log.action}")
    
    # 3. Check appointment details
    print(f"\nAppointment Details:")
    print(f"  - Patient: {appointment.patient.user.get_full_name()}")
    print(f"  - Doctor: {appointment.doctor.get_full_name()}")
    print(f"  - Service: {appointment.service.name if appointment.service else 'General Consultation'}")
    print(f"  - Duration: {appointment.duration_minutes} minutes")
    print(f"  - Status: {appointment.get_status_display()}")
    print(f"  - Can Cancel: {appointment.can_cancel()}")
    print(f"  - Can Reschedule: {appointment.can_reschedule()}")


def demonstrate_waiting_list(doctor, patient):
    """Demonstrate waiting list functionality"""
    print("\nDemonstrating waiting list...")
    
    preferred_date = timezone.now().date() + timedelta(days=14)
    
    waiting_entry = WaitingList.objects.create(
        patient=patient,
        doctor=doctor,
        preferred_date=preferred_date,
        preferred_time_start=time(9, 0),
        preferred_time_end=time(12, 0),
        appointment_type=AppointmentType.CONSULTATION,
        reason='Prefer morning appointment',
        priority=3
    )
    
    print(f"✓ Added to waiting list:")
    print(f"  - Preferred date: {waiting_entry.preferred_date}")
    print(f"  - Preferred time: {waiting_entry.preferred_time_start} - {waiting_entry.preferred_time_end}")
    print(f"  - Priority: {waiting_entry.priority} (1=highest, 10=lowest)")
    print(f"  - Status: {'Active' if waiting_entry.is_active else 'Inactive'}")


def generate_statistics(doctor):
    """Generate appointment statistics"""
    print("\nAppointment Statistics:")
    
    # Total appointments
    total_appointments = Appointment.objects.filter(doctor=doctor).count()
    print(f"  - Total appointments: {total_appointments}")
    
    # By status
    for status, display in AppointmentStatus.CHOICES:
        count = Appointment.objects.filter(doctor=doctor, status=status).count()
        if count > 0:
            print(f"  - {display}: {count}")
    
    # Available slots for next 7 days
    total_available_slots = 0
    for i in range(7):
        date = timezone.now().date() + timedelta(days=i+1)
        available = TimeSlot.objects.filter(
            doctor=doctor,
            date=date,
            is_available=True,
            is_booked=False
        ).count()
        total_available_slots += available
    
    print(f"  - Available slots (next 7 days): {total_available_slots}")
    
    # Waiting list
    waiting_count = WaitingList.objects.filter(
        doctor=doctor,
        is_active=True
    ).count()
    print(f"  - Patients on waiting list: {waiting_count}")


def main():
    """Main demonstration function"""
    print("=" * 60)
    print("APPOINTMENT MODULE DEMONSTRATION")
    print("=" * 60)
    
    try:
        # Create test data
        doctor, patient, service = create_test_data()
        
        # Create time slots
        create_time_slots(doctor)
        
        # Book appointment
        appointment = demonstrate_appointment_booking(doctor, patient, service)
        
        # Manage appointment
        demonstrate_appointment_management(appointment)
        
        # Demonstrate waiting list
        demonstrate_waiting_list(doctor, patient)
        
        # Generate statistics
        generate_statistics(doctor)
        
        print("\n" + "=" * 60)
        print("DEMONSTRATION COMPLETE")
        print("=" * 60)
        
        print("\nLogin Credentials:")
        print("  Doctor: username='dr_smith', password='doctor123'")
        print("  Patient: username='jane_doe', password='patient123'")
        
        print("\nAPI Endpoints:")
        print("  - GET/POST /api/appointments/appointments/")
        print("  - GET/POST /api/appointments/time-slots/")
        print("  - POST /api/appointments/appointments/{id}/confirm/")
        print("  - POST /api/appointments/appointments/{id}/cancel/")
        print("  - POST /api/appointments/appointments/{id}/reschedule/")
        print("  - GET /api/appointments/appointments/statistics/")
        print("  - POST /api/appointments/check-availability/")
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()