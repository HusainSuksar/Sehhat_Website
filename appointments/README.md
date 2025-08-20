# Appointment Module Documentation

## Overview

The Appointment Module is a comprehensive appointment management system for the Umoor Sehhat healthcare platform. It provides functionality for booking, managing, and tracking medical appointments between doctors and patients.

## Features

### Core Features
- **Appointment Booking**: Patients can book appointments with doctors
- **Time Slot Management**: Doctors can manage their availability through time slots
- **Appointment Status Tracking**: Track appointments through various stages (pending, confirmed, completed, cancelled)
- **Appointment Rescheduling**: Support for rescheduling appointments
- **Cancellation Management**: Handle appointment cancellations with reason tracking
- **Reminder System**: Automated email/SMS reminders for appointments
- **Waiting List**: Manage patients waiting for appointments
- **Payment Tracking**: Track consultation fees and payment status

### Advanced Features
- **Conflict Prevention**: Automatic detection and prevention of double-booking
- **Recurring Time Slots**: Create recurring availability patterns
- **Bulk Time Slot Creation**: Create multiple time slots at once
- **Appointment History**: Complete audit trail for all appointment changes
- **Statistics and Analytics**: Track appointment metrics and revenue

## Models

### 1. TimeSlot
Represents available time slots for doctors.

**Fields:**
- `doctor`: ForeignKey to Doctor
- `date`: Date of the time slot
- `start_time`: Start time
- `end_time`: End time
- `is_available`: Boolean indicating availability
- `is_booked`: Boolean indicating if fully booked
- `max_appointments`: Maximum appointments per slot
- `current_appointments`: Current appointment count
- `is_recurring`: Boolean for recurring slots
- `recurring_days`: Comma-separated weekday numbers
- `recurring_end_date`: End date for recurring slots

### 2. Appointment
Main appointment model with comprehensive tracking.

**Key Fields:**
- `appointment_id`: UUID for unique identification
- `doctor`: ForeignKey to Doctor
- `patient`: ForeignKey to Patient
- `time_slot`: Optional ForeignKey to TimeSlot
- `appointment_date`: Date of appointment
- `appointment_time`: Time of appointment
- `duration_minutes`: Duration in minutes
- `status`: Current status (pending, confirmed, completed, etc.)
- `consultation_fee`: Fee amount
- `is_paid`: Payment status
- `cancellation_reason`: Reason if cancelled
- `rescheduled_from`: Link to original appointment if rescheduled

### 3. AppointmentLog
Tracks all changes to appointments.

**Fields:**
- `appointment`: ForeignKey to Appointment
- `action`: Type of action (created, updated, confirmed, etc.)
- `performed_by`: User who performed the action
- `timestamp`: When the action occurred
- `notes`: Additional notes
- `old_values`: JSON field for previous values
- `new_values`: JSON field for new values

### 4. AppointmentReminder
Manages appointment reminders.

**Fields:**
- `appointment`: ForeignKey to Appointment
- `reminder_type`: Type (email, sms, whatsapp, push)
- `scheduled_for`: When to send the reminder
- `sent_at`: When it was actually sent
- `is_sent`: Boolean sent status
- `status`: Current status (pending, sent, failed, cancelled)

### 5. WaitingList
Manages patients waiting for appointments.

**Fields:**
- `patient`: ForeignKey to Patient
- `doctor`: ForeignKey to Doctor
- `preferred_date`: Preferred appointment date
- `preferred_time_start`: Start of preferred time range
- `preferred_time_end`: End of preferred time range
- `priority`: Priority level (1-10, 1 being highest)
- `is_active`: Boolean active status
- `notified`: Boolean notification status

## API Endpoints

### Appointments

#### List/Create Appointments
```
GET /api/appointments/appointments/
POST /api/appointments/appointments/
```

**Query Parameters (GET):**
- `status`: Filter by status
- `date_from`: Start date filter
- `date_to`: End date filter
- `doctor`: Filter by doctor ID
- `patient`: Filter by patient ID

**Request Body (POST):**
```json
{
    "doctor": 1,
    "patient": 1,
    "service": 1,
    "appointment_date": "2024-12-30",
    "appointment_time": "10:00",
    "duration_minutes": 30,
    "appointment_type": "consultation",
    "reason_for_visit": "Regular checkup",
    "symptoms": "None",
    "booking_method": "online"
}
```

#### Appointment Actions

**Confirm Appointment:**
```
POST /api/appointments/appointments/{id}/confirm/
```

**Cancel Appointment:**
```
POST /api/appointments/appointments/{id}/cancel/
```
Request Body:
```json
{
    "cancellation_reason": "Unable to attend due to emergency"
}
```

**Reschedule Appointment:**
```
POST /api/appointments/appointments/{id}/reschedule/
```
Request Body:
```json
{
    "new_date": "2024-12-31",
    "new_time": "11:00",
    "reason": "Conflict with another appointment"
}
```

**Complete Appointment:**
```
POST /api/appointments/appointments/{id}/complete/
```

**Mark as No-Show:**
```
POST /api/appointments/appointments/{id}/no_show/
```

#### Special Endpoints

**Today's Appointments:**
```
GET /api/appointments/appointments/today/
```

**Upcoming Appointments:**
```
GET /api/appointments/appointments/upcoming/
```

**Appointment Statistics:**
```
GET /api/appointments/appointments/statistics/
```

**Appointment Logs:**
```
GET /api/appointments/appointments/{id}/logs/
```

### Time Slots

#### List/Create Time Slots
```
GET /api/appointments/time-slots/
POST /api/appointments/time-slots/
```

**Query Parameters (GET):**
- `doctor`: Filter by doctor ID
- `date_from`: Start date filter
- `date_to`: End date filter
- `available_only`: Show only available slots (default: true)

#### Bulk Create Time Slots
```
POST /api/appointments/time-slots/bulk_create/
```
Request Body:
```json
{
    "doctor": 1,
    "start_date": "2024-12-25",
    "end_date": "2024-12-31",
    "start_time": "09:00",
    "end_time": "17:00",
    "slot_duration_minutes": 30,
    "break_duration_minutes": 15,
    "weekdays": [0, 1, 2, 3, 4],
    "max_appointments_per_slot": 2
}
```

### Availability Check

```
POST /api/appointments/check-availability/
```
Request Body:
```json
{
    "doctor_id": 1,
    "date": "2024-12-30",
    "duration_minutes": 30
}
```

### Waiting List

#### List/Create Waiting List Entries
```
GET /api/appointments/waiting-list/
POST /api/appointments/waiting-list/
```

#### Notify Patient
```
POST /api/appointments/waiting-list/{id}/notify/
```

#### Deactivate Entry
```
POST /api/appointments/waiting-list/{id}/deactivate/
```

## Usage Examples

### 1. Creating Time Slots for a Doctor

```python
from appointments.utils import AppointmentScheduler
from datetime import datetime, time, timedelta

# Define time slot configuration
time_slots_config = [
    {'start_time': time(9, 0), 'end_time': time(9, 30), 'max_appointments': 2},
    {'start_time': time(9, 30), 'end_time': time(10, 0), 'max_appointments': 2},
    # ... more slots
]

# Create recurring slots for weekdays
created_slots = AppointmentScheduler.create_recurring_slots(
    doctor=doctor,
    start_date=datetime.now().date(),
    end_date=datetime.now().date() + timedelta(days=30),
    time_slots_config=time_slots_config,
    weekdays=[0, 1, 2, 3, 4]  # Monday to Friday
)
```

### 2. Booking an Appointment

```python
from appointments.models import Appointment, AppointmentType

appointment = Appointment.objects.create(
    doctor=doctor,
    patient=patient,
    appointment_date=datetime(2024, 12, 30).date(),
    appointment_time=time(10, 0),
    duration_minutes=30,
    appointment_type=AppointmentType.CONSULTATION,
    reason_for_visit='Regular checkup',
    booked_by=patient.user
)

# Confirm the appointment
appointment.confirm(confirmed_by=doctor.user)
```

### 3. Checking Doctor Availability

```python
from appointments.utils import AppointmentScheduler

available_slots = AppointmentScheduler.get_available_slots(
    doctor=doctor,
    date=datetime(2024, 12, 30).date(),
    duration_minutes=30
)

for slot_info in available_slots:
    slot = slot_info['slot']
    available_count = slot_info['available_count']
    print(f"{slot.start_time} - {slot.end_time}: {available_count} slots available")
```

### 4. Processing Reminders

```python
from appointments.utils import AppointmentRemindersProcessor

# Process all pending reminders
processed, failed = AppointmentRemindersProcessor.process_pending_reminders()
print(f"Processed {processed} reminders, {failed} failed")
```

## Integration with Other Modules

### Doctor Directory Integration
- Uses `Doctor` model for doctor profiles
- Uses `Patient` model for patient profiles
- Uses `MedicalService` model for service definitions

### Accounts Integration
- Uses custom `User` model for authentication
- Respects user roles (doctor, patient, admin)

### Permissions
- Doctors can only see their own appointments
- Patients can only see their own appointments
- Admins have full access

## Admin Interface

The module includes a comprehensive Django admin interface with:

- **Appointment Management**: View, filter, and manage all appointments
- **Time Slot Management**: Create and manage doctor availability
- **Bulk Actions**: Confirm, cancel, or complete multiple appointments
- **Inline Editing**: View logs and reminders directly in appointment admin
- **Custom Filters**: Filter by status, date, doctor, payment status
- **Statistics**: View appointment counts and revenue

## Testing

The module includes comprehensive test coverage:

### Unit Tests
- Model validation and business logic
- Appointment conflict detection
- Status transition validation
- Time slot availability checking

### Integration Tests
- Complete appointment workflow
- Doctor-patient integration
- Payment tracking
- Reminder system

### API Tests
- All endpoint functionality
- Permission checking
- Data validation
- Error handling

To run tests:
```bash
python manage.py test appointments
```

## Configuration

### Email Settings
Configure email settings in `settings.py` for appointment notifications:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-password'
DEFAULT_FROM_EMAIL = 'noreply@umoorsehhat.com'
```

### Reminder Settings
Default reminder times can be configured in the `AppointmentRemindersProcessor` class.

## Best Practices

1. **Always validate appointment dates**: Ensure appointments are not in the past
2. **Use time slots**: Create time slots to manage availability
3. **Handle cancellations properly**: Always provide a reason for cancellations
4. **Schedule reminders**: Use the reminder system to reduce no-shows
5. **Track payments**: Keep payment status updated for financial tracking
6. **Use the waiting list**: Add patients to waiting list when fully booked
7. **Regular cleanup**: Archive old appointments periodically

## Troubleshooting

### Common Issues

1. **Appointment conflicts**: Check that time slots don't overlap and max_appointments is set correctly
2. **Reminder failures**: Verify email/SMS settings and check error logs
3. **Performance issues**: Use database indexes and optimize queries for large datasets
4. **Time zone issues**: Ensure TIME_ZONE is set correctly in Django settings

### Debug Commands

```python
# Check appointment conflicts
from appointments.models import Appointment
conflicts = Appointment.objects.filter(
    doctor=doctor,
    appointment_date=date,
    appointment_time=time,
    status__in=['confirmed', 'scheduled']
)

# Check available slots
from appointments.models import TimeSlot
available = TimeSlot.objects.filter(
    doctor=doctor,
    date=date,
    is_available=True,
    is_booked=False
)

# Check pending reminders
from appointments.models import AppointmentReminder
pending = AppointmentReminder.objects.filter(
    scheduled_for__lte=timezone.now(),
    is_sent=False,
    status='pending'
)
```

## Future Enhancements

1. **Video Consultation Support**: Add support for online consultations
2. **Recurring Appointments**: Support for regular follow-up appointments
3. **Group Appointments**: Support for group therapy or classes
4. **SMS/WhatsApp Integration**: Implement actual SMS and WhatsApp reminders
5. **Calendar Integration**: Sync with Google Calendar, Outlook, etc.
6. **Mobile App API**: Enhanced API for mobile applications
7. **Advanced Analytics**: Detailed reports and dashboards
8. **Insurance Integration**: Handle insurance claims and approvals