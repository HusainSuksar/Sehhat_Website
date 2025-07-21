from django.core.management.base import BaseCommand
from django.utils import timezone
from umoor_sehhat.notifications import ScheduledNotifications
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send scheduled notifications (appointment reminders, doctor schedules, survey reminders)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            choices=['appointments', 'schedules', 'surveys', 'weekly', 'all'],
            default='all',
            help='Type of notifications to send (default: all)'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Perform a dry run without actually sending notifications'
        )
    
    def handle(self, *args, **options):
        notification_type = options['type']
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No notifications will be sent')
            )
        
        self.stdout.write(f'Starting notification process: {notification_type}')
        start_time = timezone.now()
        
        total_sent = 0
        
        try:
            if notification_type in ['appointments', 'all']:
                self.stdout.write('Sending appointment reminders...')
                if not dry_run:
                    sent = ScheduledNotifications.send_daily_appointment_reminders()
                    total_sent += sent
                    self.stdout.write(
                        self.style.SUCCESS(f'Sent {sent} appointment reminders')
                    )
                else:
                    self.stdout.write('Would send appointment reminders')
            
            if notification_type in ['schedules', 'all']:
                self.stdout.write('Sending doctor daily schedules...')
                if not dry_run:
                    sent = ScheduledNotifications.send_doctor_daily_schedules()
                    total_sent += sent
                    self.stdout.write(
                        self.style.SUCCESS(f'Sent {sent} daily schedules')
                    )
                else:
                    self.stdout.write('Would send doctor daily schedules')
            
            if notification_type in ['surveys', 'all']:
                self.stdout.write('Sending survey reminders...')
                if not dry_run:
                    sent = ScheduledNotifications.send_survey_reminders()
                    total_sent += sent
                    self.stdout.write(
                        self.style.SUCCESS(f'Sent {sent} survey reminders')
                    )
                else:
                    self.stdout.write('Would send survey reminders')
            
            if notification_type in ['weekly', 'all']:
                # Only send weekly summary on Mondays
                if timezone.now().weekday() == 0:  # Monday
                    self.stdout.write('Sending weekly summary...')
                    if not dry_run:
                        sent = ScheduledNotifications.send_weekly_summary()
                        total_sent += sent
                        self.stdout.write(
                            self.style.SUCCESS(f'Sent {sent} weekly summaries')
                        )
                    else:
                        self.stdout.write('Would send weekly summary')
                else:
                    self.stdout.write('Weekly summary only sent on Mondays')
            
            duration = timezone.now() - start_time
            
            if not dry_run:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Notification process completed successfully! '
                        f'Total sent: {total_sent}, Duration: {duration.total_seconds():.2f}s'
                    )
                )
                logger.info(f'Scheduled notifications sent: {total_sent} in {duration.total_seconds():.2f}s')
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Dry run completed! Duration: {duration.total_seconds():.2f}s'
                    )
                )
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during notification process: {str(e)}')
            )
            logger.error(f'Error in scheduled notifications: {str(e)}')
            raise