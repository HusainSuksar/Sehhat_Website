from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class NotificationService:
    """Service for sending various types of notifications"""
    
    @staticmethod
    def send_email_notification(to_emails, subject, template_name, context, from_email=None):
        """
        Send HTML email notification
        
        Args:
            to_emails: List of email addresses or single email
            subject: Email subject
            template_name: Template name (without .html extension)
            context: Context data for template
            from_email: From email address (optional)
        """
        if isinstance(to_emails, str):
            to_emails = [to_emails]
        
        if not from_email:
            from_email = settings.DEFAULT_FROM_EMAIL
        
        try:
            # Render HTML content
            html_content = render_to_string(f'emails/{template_name}.html', context)
            text_content = strip_tags(html_content)
            
            # Create email message
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=to_emails
            )
            msg.attach_alternative(html_content, "text/html")
            
            # Send email
            msg.send()
            
            logger.info(f"Email sent successfully to {to_emails}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_emails}: {str(e)}")
            return False
    
    @staticmethod
    def send_appointment_confirmation(appointment):
        """Send appointment confirmation email"""
        if not appointment.patient.user.email:
            return False
        
        context = {
            'appointment': appointment,
            'patient': appointment.patient,
            'doctor': appointment.doctor,
            'site_name': 'Umoor Sehhat'
        }
        
        return NotificationService.send_email_notification(
            to_emails=appointment.patient.user.email,
            subject=f'Appointment Confirmation - {appointment.appointment_date}',
            template_name='appointment_confirmation',
            context=context
        )
    
    @staticmethod
    def send_appointment_reminder(appointment):
        """Send appointment reminder email"""
        if not appointment.patient.user.email:
            return False
        
        context = {
            'appointment': appointment,
            'patient': appointment.patient,
            'doctor': appointment.doctor,
            'site_name': 'Umoor Sehhat'
        }
        
        return NotificationService.send_email_notification(
            to_emails=appointment.patient.user.email,
            subject=f'Appointment Reminder - Tomorrow',
            template_name='appointment_reminder',
            context=context
        )
    
    @staticmethod
    def send_doctor_schedule_notification(doctor, schedule_date, appointments):
        """Send daily schedule notification to doctor"""
        if not doctor.user.email:
            return False
        
        context = {
            'doctor': doctor,
            'schedule_date': schedule_date,
            'appointments': appointments,
            'total_appointments': len(appointments),
            'site_name': 'Umoor Sehhat'
        }
        
        return NotificationService.send_email_notification(
            to_emails=doctor.user.email,
            subject=f'Your Schedule for {schedule_date.strftime("%B %d, %Y")}',
            template_name='doctor_daily_schedule',
            context=context
        )
    
    @staticmethod
    def send_dua_araz_completion_notification(dua_araz):
        """Send notification when Dua Araz is completed"""
        if not dua_araz.petitioner.email:
            return False
        
        context = {
            'dua_araz': dua_araz,
            'petitioner': dua_araz.petitioner,
            'site_name': 'Umoor Sehhat'
        }
        
        return NotificationService.send_email_notification(
            to_emails=dua_araz.petitioner.email,
            subject='Your Dua Araz Request Update',
            template_name='dua_araz_completion',
            context=context
        )
    
    @staticmethod
    def send_survey_invitation(survey, users):
        """Send survey invitation to multiple users"""
        if not users:
            return False
        
        successful_sends = 0
        
        for user in users:
            if not user.email:
                continue
            
            context = {
                'survey': survey,
                'user': user,
                'survey_url': f"/surveys/{survey.id}/",
                'site_name': 'Umoor Sehhat'
            }
            
            success = NotificationService.send_email_notification(
                to_emails=user.email,
                subject=f'Survey Invitation: {survey.title}',
                template_name='survey_invitation',
                context=context
            )
            
            if success:
                successful_sends += 1
        
        logger.info(f"Survey invitation sent to {successful_sends}/{len(users)} users")
        return successful_sends
    
    @staticmethod
    def send_survey_reminder(survey, users):
        """Send survey reminder to users who haven't responded"""
        if not users:
            return False
        
        successful_sends = 0
        
        for user in users:
            if not user.email:
                continue
            
            context = {
                'survey': survey,
                'user': user,
                'survey_url': f"/surveys/{survey.id}/",
                'days_remaining': (survey.end_date - timezone.now().date()).days,
                'site_name': 'Umoor Sehhat'
            }
            
            success = NotificationService.send_email_notification(
                to_emails=user.email,
                subject=f'Reminder: {survey.title}',
                template_name='survey_reminder',
                context=context
            )
            
            if success:
                successful_sends += 1
        
        logger.info(f"Survey reminder sent to {successful_sends}/{len(users)} users")
        return successful_sends
    
    @staticmethod
    def send_welcome_email(user, temporary_password=None):
        """Send welcome email to new user"""
        if not user.email:
            return False
        
        context = {
            'user': user,
            'temporary_password': temporary_password,
            'login_url': '/accounts/login/',
            'site_name': 'Umoor Sehhat'
        }
        
        return NotificationService.send_email_notification(
            to_emails=user.email,
            subject='Welcome to Umoor Sehhat',
            template_name='welcome_email',
            context=context
        )
    
    @staticmethod
    def send_password_reset_notification(user, reset_link):
        """Send password reset notification"""
        if not user.email:
            return False
        
        context = {
            'user': user,
            'reset_link': reset_link,
            'site_name': 'Umoor Sehhat'
        }
        
        return NotificationService.send_email_notification(
            to_emails=user.email,
            subject='Password Reset Request',
            template_name='password_reset',
            context=context
        )
    
    @staticmethod
    def send_moze_comment_notification(comment):
        """Send notification when new comment is added to Moze"""
        # Get Moze team members to notify
        moze = comment.moze
        recipients = []
        
        # Add Aamil
        if moze.aamil and moze.aamil.email and moze.aamil != comment.author:
            recipients.append(moze.aamil)
        
        # Add Coordinator
        if moze.moze_coordinator and moze.moze_coordinator.email and moze.moze_coordinator != comment.author:
            recipients.append(moze.moze_coordinator)
        
        # Add team members (limit to prevent spam)
        team_members = moze.team_members.filter(
            email__isnull=False
        ).exclude(
            id=comment.author.id
        )[:10]  # Limit to 10 team members
        
        recipients.extend(team_members)
        
        if not recipients:
            return False
        
        context = {
            'comment': comment,
            'moze': moze,
            'author': comment.author,
            'moze_url': f"/moze/{moze.id}/",
            'site_name': 'Umoor Sehhat'
        }
        
        successful_sends = 0
        for recipient in recipients:
            success = NotificationService.send_email_notification(
                to_emails=recipient.email,
                subject=f'New comment on {moze.name}',
                template_name='moze_comment_notification',
                context={**context, 'recipient': recipient}
            )
            
            if success:
                successful_sends += 1
        
        return successful_sends
    
    @staticmethod
    def send_bulk_notification(users, subject, message, template_name='bulk_notification'):
        """Send bulk notification to multiple users"""
        if not users:
            return False
        
        successful_sends = 0
        
        for user in users:
            if not user.email:
                continue
            
            context = {
                'user': user,
                'message': message,
                'site_name': 'Umoor Sehhat'
            }
            
            success = NotificationService.send_email_notification(
                to_emails=user.email,
                subject=subject,
                template_name=template_name,
                context=context
            )
            
            if success:
                successful_sends += 1
        
        logger.info(f"Bulk notification sent to {successful_sends}/{len(users)} users")
        return successful_sends


class ScheduledNotifications:
    """Service for handling scheduled notifications"""
    
    @staticmethod
    def send_daily_appointment_reminders():
        """Send appointment reminders for tomorrow's appointments"""
        from doctordirectory.models import Appointment
        
        tomorrow = timezone.now().date() + timedelta(days=1)
        
        appointments = Appointment.objects.filter(
            appointment_date=tomorrow,
            status__in=['scheduled', 'confirmed'],
            patient__user__email__isnull=False
        ).select_related('patient__user', 'doctor__user')
        
        sent_count = 0
        for appointment in appointments:
            if NotificationService.send_appointment_reminder(appointment):
                sent_count += 1
        
        logger.info(f"Sent {sent_count} appointment reminders for {tomorrow}")
        return sent_count
    
    @staticmethod
    def send_doctor_daily_schedules():
        """Send daily schedules to doctors"""
        from doctordirectory.models import Doctor, Appointment
        
        tomorrow = timezone.now().date() + timedelta(days=1)
        
        doctors = Doctor.objects.filter(
            is_verified=True,
            user__email__isnull=False
        ).select_related('user')
        
        sent_count = 0
        for doctor in doctors:
            appointments = Appointment.objects.filter(
                doctor=doctor,
                appointment_date=tomorrow,
                status__in=['scheduled', 'confirmed']
            ).select_related('patient__user')
            
            if appointments.exists():
                if NotificationService.send_doctor_schedule_notification(
                    doctor, tomorrow, appointments
                ):
                    sent_count += 1
        
        logger.info(f"Sent {sent_count} daily schedules to doctors for {tomorrow}")
        return sent_count
    
    @staticmethod
    def send_survey_reminders():
        """Send reminders for active surveys"""
        from surveys.models import Survey, SurveyResponse
        
        # Find surveys ending in 3 days
        reminder_date = timezone.now().date() + timedelta(days=3)
        
        active_surveys = Survey.objects.filter(
            is_active=True,
            end_date=reminder_date
        )
        
        total_sent = 0
        for survey in active_surveys:
            # Get users who haven't responded
            responded_user_ids = SurveyResponse.objects.filter(
                survey=survey
            ).values_list('user_id', flat=True)
            
            target_users = User.objects.filter(
                role__in=survey.target_audience,
                email__isnull=False,
                is_active=True
            ).exclude(id__in=responded_user_ids)
            
            if target_users.exists():
                sent_count = NotificationService.send_survey_reminder(survey, target_users)
                total_sent += sent_count
        
        logger.info(f"Sent {total_sent} survey reminders")
        return total_sent
    
    @staticmethod
    def send_weekly_summary():
        """Send weekly summary to administrators"""
        from django.db.models import Count
        from doctordirectory.models import Appointment
        from surveys.models import SurveyResponse
        from moze.models import MozeComment
        
        # Calculate weekly stats
        week_start = timezone.now().date() - timedelta(days=7)
        week_end = timezone.now().date()
        
        stats = {
            'appointments': Appointment.objects.filter(
                created_at__date__range=[week_start, week_end]
            ).count(),
            'survey_responses': SurveyResponse.objects.filter(
                completed_at__date__range=[week_start, week_end]
            ).count(),
            'moze_comments': MozeComment.objects.filter(
                created_at__date__range=[week_start, week_end]
            ).count(),
            'new_users': User.objects.filter(
                date_joined__date__range=[week_start, week_end]
            ).count(),
        }
        
        # Get admin users
        admin_users = User.objects.filter(
            role='badri_mahal_admin',
            email__isnull=False,
            is_active=True
        )
        
        context = {
            'stats': stats,
            'week_start': week_start,
            'week_end': week_end,
            'site_name': 'Umoor Sehhat'
        }
        
        sent_count = 0
        for admin in admin_users:
            success = NotificationService.send_email_notification(
                to_emails=admin.email,
                subject=f'Weekly Summary - {week_start.strftime("%B %d")} to {week_end.strftime("%B %d, %Y")}',
                template_name='weekly_summary',
                context={**context, 'admin': admin}
            )
            
            if success:
                sent_count += 1
        
        logger.info(f"Sent weekly summary to {sent_count} administrators")
        return sent_count