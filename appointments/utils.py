from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from .models import Appointment, AppointmentReminder, TimeSlot, AppointmentStatus

logger = logging.getLogger(__name__)


class AppointmentNotificationService:
    """Service for handling appointment notifications"""
    
    @staticmethod
    def send_appointment_confirmation(appointment):
        """Send appointment confirmation email"""
        try:
            subject = f'Appointment Confirmation - {appointment.appointment_date}'
            
            context = {
                'appointment': appointment,
                'patient_name': appointment.patient.user.get_full_name() if appointment.patient.user else 'Patient',
                'doctor_name': appointment.doctor.get_full_name(),
                'appointment_datetime': datetime.combine(
                    appointment.appointment_date,
                    appointment.appointment_time
                ),
                'clinic_name': 'Umoor Sehhat Medical Center'
            }
            
            # For now, using a simple text message
            message = f"""
Dear {context['patient_name']},

Your appointment has been confirmed!

Details:
- Doctor: Dr. {context['doctor_name']}
- Date: {appointment.appointment_date.strftime('%B %d, %Y')}
- Time: {appointment.appointment_time.strftime('%I:%M %p')}
- Type: {appointment.get_appointment_type_display()}
- Duration: {appointment.duration_minutes} minutes

Please arrive 15 minutes before your scheduled appointment time.

If you need to cancel or reschedule, please contact us at least 24 hours in advance.

Thank you,
{context['clinic_name']}
            """
            
            recipient_email = appointment.patient.user.email if appointment.patient.user else None
            
            if recipient_email:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [recipient_email],
                    fail_silently=False,
                )
                
                appointment.confirmation_sent = True
                appointment.save()
                
                logger.info(f"Confirmation email sent for appointment {appointment.appointment_id}")
                return True
            
        except Exception as e:
            logger.error(f"Failed to send confirmation for appointment {appointment.appointment_id}: {str(e)}")
            return False
    
    @staticmethod
    def send_appointment_reminder(reminder):
        """Send appointment reminder"""
        try:
            appointment = reminder.appointment
            
            if reminder.reminder_type == 'email':
                subject = f'Appointment Reminder - {appointment.appointment_date}'
                
                time_until = datetime.combine(
                    appointment.appointment_date,
                    appointment.appointment_time
                ) - timezone.now()
                
                hours_until = int(time_until.total_seconds() / 3600)
                
                message = f"""
Dear {appointment.patient.user.get_full_name() if appointment.patient.user else 'Patient'},

This is a reminder about your upcoming appointment:

- Doctor: Dr. {appointment.doctor.get_full_name()}
- Date: {appointment.appointment_date.strftime('%B %d, %Y')}
- Time: {appointment.appointment_time.strftime('%I:%M %p')}
- Location: {appointment.doctor.address if appointment.doctor.address else 'Please check your appointment details'}

Your appointment is in approximately {hours_until} hours.

Please remember to bring:
- Your ID/ITS card
- Any relevant medical records
- List of current medications

If you need to cancel or reschedule, please contact us immediately.

Thank you,
Umoor Sehhat Medical Center
                """
                
                recipient_email = appointment.patient.user.email if appointment.patient.user else None
                
                if recipient_email:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [recipient_email],
                        fail_silently=False,
                    )
                    
                    reminder.is_sent = True
                    reminder.sent_at = timezone.now()
                    reminder.status = 'sent'
                    reminder.save()
                    
                    appointment.reminder_sent = True
                    appointment.save()
                    
                    logger.info(f"Reminder sent for appointment {appointment.appointment_id}")
                    return True
            
            elif reminder.reminder_type == 'sms':
                # SMS implementation would go here
                logger.info(f"SMS reminder for appointment {appointment.appointment_id} - Not implemented")
                return False
            
            elif reminder.reminder_type == 'whatsapp':
                # WhatsApp implementation would go here
                logger.info(f"WhatsApp reminder for appointment {appointment.appointment_id} - Not implemented")
                return False
                
        except Exception as e:
            reminder.status = 'failed'
            reminder.error_message = str(e)
            reminder.save()
            logger.error(f"Failed to send reminder {reminder.id}: {str(e)}")
            return False
    
    @staticmethod
    def send_cancellation_notification(appointment, reason=''):
        """Send appointment cancellation notification"""
        try:
            subject = f'Appointment Cancelled - {appointment.appointment_date}'
            
            message = f"""
Dear {appointment.patient.user.get_full_name() if appointment.patient.user else 'Patient'},

We regret to inform you that your appointment has been cancelled:

- Doctor: Dr. {appointment.doctor.get_full_name()}
- Date: {appointment.appointment_date.strftime('%B %d, %Y')}
- Time: {appointment.appointment_time.strftime('%I:%M %p')}

{f'Reason: {reason}' if reason else ''}

Please contact us to reschedule your appointment at your earliest convenience.

We apologize for any inconvenience.

Thank you,
Umoor Sehhat Medical Center
            """
            
            recipient_email = appointment.patient.user.email if appointment.patient.user else None
            
            if recipient_email:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [recipient_email],
                    fail_silently=False,
                )
                
                logger.info(f"Cancellation notification sent for appointment {appointment.appointment_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to send cancellation notification for appointment {appointment.appointment_id}: {str(e)}")
            return False


class AppointmentScheduler:
    """Utility class for appointment scheduling operations"""
    
    @staticmethod
    def get_available_slots(doctor, date, duration_minutes=30):
        """Get available time slots for a doctor on a specific date"""
        # Get all time slots for the doctor on the date
        time_slots = TimeSlot.objects.filter(
            doctor=doctor,
            date=date,
            is_available=True
        ).order_by('start_time')
        
        available_slots = []
        
        for slot in time_slots:
            if slot.can_book() and slot.duration_minutes >= duration_minutes:
                # Check for existing appointments in this slot
                conflicting_appointments = Appointment.objects.filter(
                    doctor=doctor,
                    appointment_date=date,
                    appointment_time__gte=slot.start_time,
                    appointment_time__lt=slot.end_time,
                    status__in=[
                        AppointmentStatus.CONFIRMED,
                        AppointmentStatus.SCHEDULED,
                        AppointmentStatus.IN_PROGRESS
                    ]
                ).count()
                
                if conflicting_appointments < slot.max_appointments:
                    available_slots.append({
                        'slot': slot,
                        'available_count': slot.max_appointments - conflicting_appointments
                    })
        
        return available_slots
    
    @staticmethod
    def create_recurring_slots(doctor, start_date, end_date, time_slots_config, weekdays=None):
        """Create recurring time slots for a doctor"""
        created_slots = []
        current_date = start_date
        
        while current_date <= end_date:
            # Check if this weekday should have slots
            if weekdays is None or current_date.weekday() in weekdays:
                for slot_config in time_slots_config:
                    # Check if slot already exists
                    if not TimeSlot.objects.filter(
                        doctor=doctor,
                        date=current_date,
                        start_time=slot_config['start_time']
                    ).exists():
                        slot = TimeSlot.objects.create(
                            doctor=doctor,
                            date=current_date,
                            start_time=slot_config['start_time'],
                            end_time=slot_config['end_time'],
                            max_appointments=slot_config.get('max_appointments', 1),
                            is_recurring=True,
                            recurring_days=','.join(map(str, weekdays)) if weekdays else ''
                        )
                        created_slots.append(slot)
            
            current_date += timedelta(days=1)
        
        return created_slots
    
    @staticmethod
    def check_doctor_availability(doctor, date, start_time, duration_minutes):
        """Check if doctor is available for a specific time"""
        end_time = (datetime.combine(date, start_time) + timedelta(minutes=duration_minutes)).time()
        
        # Check if there's a time slot covering this period
        covering_slot = TimeSlot.objects.filter(
            doctor=doctor,
            date=date,
            start_time__lte=start_time,
            end_time__gte=end_time,
            is_available=True
        ).first()
        
        if not covering_slot:
            return False, "No available time slot for this period"
        
        # Check for conflicting appointments
        conflicting_appointments = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=date,
            status__in=[
                AppointmentStatus.CONFIRMED,
                AppointmentStatus.SCHEDULED,
                AppointmentStatus.IN_PROGRESS
            ]
        ).filter(
            # Check for overlapping appointments
            appointment_time__lt=end_time,
            # This is a simplified check - in production, you'd want more sophisticated overlap detection
        ).count()
        
        if conflicting_appointments >= covering_slot.max_appointments:
            return False, "Doctor is fully booked for this time"
        
        return True, "Doctor is available"
    
    @staticmethod
    def get_next_available_slot(doctor, after_datetime=None):
        """Get the next available slot for a doctor"""
        if after_datetime is None:
            after_datetime = timezone.now()
        
        next_slot = TimeSlot.objects.filter(
            doctor=doctor,
            date__gte=after_datetime.date(),
            is_available=True,
            is_booked=False
        ).order_by('date', 'start_time').first()
        
        if next_slot:
            # Double-check by counting actual appointments
            appointments_count = Appointment.objects.filter(
                doctor=doctor,
                appointment_date=next_slot.date,
                appointment_time__gte=next_slot.start_time,
                appointment_time__lt=next_slot.end_time,
                status__in=[
                    AppointmentStatus.CONFIRMED,
                    AppointmentStatus.SCHEDULED
                ]
            ).count()
            
            if appointments_count < next_slot.max_appointments:
                return next_slot
        
        return None


class AppointmentRemindersProcessor:
    """Process and send appointment reminders"""
    
    @staticmethod
    def process_pending_reminders():
        """Process all pending reminders that are due"""
        notification_service = AppointmentNotificationService()
        
        # Get reminders that are due and not sent
        due_reminders = AppointmentReminder.objects.filter(
            scheduled_for__lte=timezone.now(),
            is_sent=False,
            status='pending'
        ).select_related('appointment', 'appointment__doctor', 'appointment__patient')
        
        processed = 0
        failed = 0
        
        for reminder in due_reminders:
            # Skip if appointment is cancelled
            if reminder.appointment.status == AppointmentStatus.CANCELLED:
                reminder.status = 'cancelled'
                reminder.save()
                continue
            
            # Send the reminder
            if notification_service.send_appointment_reminder(reminder):
                processed += 1
            else:
                failed += 1
        
        logger.info(f"Processed {processed} reminders, {failed} failed")
        return processed, failed
    
    @staticmethod
    def schedule_default_reminders(appointment):
        """Schedule default reminders for an appointment"""
        appointment_datetime = datetime.combine(
            appointment.appointment_date,
            appointment.appointment_time
        )
        
        # Don't schedule reminders for past appointments
        if appointment_datetime <= timezone.now():
            return []
        
        reminders = []
        
        # 24 hours before - Email
        reminder_24h = appointment_datetime - timedelta(hours=24)
        if reminder_24h > timezone.now():
            reminders.append(
                AppointmentReminder.objects.create(
                    appointment=appointment,
                    reminder_type='email',
                    scheduled_for=reminder_24h
                )
            )
        
        # 2 hours before - SMS
        reminder_2h = appointment_datetime - timedelta(hours=2)
        if reminder_2h > timezone.now():
            reminders.append(
                AppointmentReminder.objects.create(
                    appointment=appointment,
                    reminder_type='sms',
                    scheduled_for=reminder_2h
                )
            )
        
        return reminders


class WaitingListManager:
    """Manage waiting list operations"""
    
    @staticmethod
    def check_and_notify_waiting_list(doctor, date, time_slot=None):
        """Check waiting list and notify patients when slots become available"""
        from .models import WaitingList
        
        # Get active waiting list entries for this doctor and date
        waiting_entries = WaitingList.objects.filter(
            doctor=doctor,
            preferred_date=date,
            is_active=True,
            notified=False
        ).order_by('priority', 'created_at')
        
        notified_count = 0
        
        for entry in waiting_entries:
            # Check if the time preference matches
            if time_slot:
                if entry.preferred_time_start and entry.preferred_time_end:
                    if not (entry.preferred_time_start <= time_slot.start_time <= entry.preferred_time_end):
                        continue
            
            # Here you would implement the actual notification
            # For now, we'll just mark as notified
            entry.notified = True
            entry.save()
            notified_count += 1
            
            logger.info(f"Notified waiting list patient {entry.patient} for doctor {doctor} on {date}")
        
        return notified_count