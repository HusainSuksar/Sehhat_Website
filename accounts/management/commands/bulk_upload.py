from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from doctordirectory.models import Doctor, Patient
from moze.models import Moze
from umoor_sehhat.notifications import NotificationService
import csv
import logging
from datetime import datetime
import secrets
import string

User = get_user_model()
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Bulk upload users, doctors, or patients from CSV files'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to CSV file'
        )
        
        parser.add_argument(
            '--type',
            type=str,
            choices=['users', 'doctors', 'patients'],
            required=True,
            help='Type of data to import'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Perform a dry run without actually creating records'
        )
        
        parser.add_argument(
            '--send-welcome-emails',
            action='store_true',
            help='Send welcome emails to new users'
        )
        
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Skip existing users (by email or ITS ID)'
        )
    
    def handle(self, *args, **options):
        csv_file = options['csv_file']
        data_type = options['type']
        dry_run = options['dry_run']
        send_emails = options['send_welcome_emails']
        skip_existing = options['skip_existing']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No records will be created')
            )
        
        self.stdout.write(f'Starting bulk upload: {data_type} from {csv_file}')
        start_time = timezone.now()
        
        try:
            if data_type == 'users':
                results = self.import_users(csv_file, dry_run, send_emails, skip_existing)
            elif data_type == 'doctors':
                results = self.import_doctors(csv_file, dry_run, send_emails, skip_existing)
            elif data_type == 'patients':
                results = self.import_patients(csv_file, dry_run, send_emails, skip_existing)
            
            duration = timezone.now() - start_time
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Bulk upload completed! '
                    f'Success: {results["success"]}, '
                    f'Skipped: {results["skipped"]}, '
                    f'Errors: {results["errors"]}, '
                    f'Duration: {duration.total_seconds():.2f}s'
                )
            )
            
            if results['error_details']:
                self.stdout.write(self.style.WARNING('Errors encountered:'))
                for error in results['error_details']:
                    self.stdout.write(f'  - {error}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during bulk upload: {str(e)}')
            )
            logger.error(f'Error in bulk upload: {str(e)}')
            raise
    
    def import_users(self, csv_file, dry_run, send_emails, skip_existing):
        """
        Import users from CSV
        Expected columns: first_name, last_name, email, role, its_id, phone_number, arabic_name
        """
        results = {'success': 0, 'skipped': 0, 'errors': 0, 'error_details': []}
        
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            with transaction.atomic():
                for row_num, row in enumerate(reader, 1):
                    try:
                        # Validate required fields
                        if not row.get('email') or not row.get('role'):
                            results['errors'] += 1
                            results['error_details'].append(f'Row {row_num}: Missing email or role')
                            continue
                        
                        email = row['email'].strip().lower()
                        its_id = row.get('its_id', '').strip()
                        
                        # Check for existing user
                        existing_user = None
                        if email:
                            existing_user = User.objects.filter(email=email).first()
                        if not existing_user and its_id:
                            existing_user = User.objects.filter(its_id=its_id).first()
                        
                        if existing_user and skip_existing:
                            results['skipped'] += 1
                            self.stdout.write(f'Skipping existing user: {email}')
                            continue
                        elif existing_user:
                            results['errors'] += 1
                            results['error_details'].append(f'Row {row_num}: User already exists: {email}')
                            continue
                        
                        # Validate role
                        valid_roles = ['aamil', 'moze_coordinator', 'doctor', 'student', 'badri_mahal_admin']
                        if row['role'] not in valid_roles:
                            results['errors'] += 1
                            results['error_details'].append(f'Row {row_num}: Invalid role: {row["role"]}')
                            continue
                        
                        if not dry_run:
                            # Generate temporary password
                            temp_password = self.generate_password()
                            
                            # Create user
                            user = User.objects.create_user(
                                username=email,
                                email=email,
                                first_name=row.get('first_name', '').strip(),
                                last_name=row.get('last_name', '').strip(),
                                role=row['role'],
                                its_id=its_id if its_id else None,
                                phone_number=row.get('phone_number', '').strip() or None,
                                arabic_name=row.get('arabic_name', '').strip() or None,
                                password=temp_password
                            )
                            
                            # Send welcome email
                            if send_emails and user.email:
                                NotificationService.send_welcome_email(user, temp_password)
                            
                            self.stdout.write(f'Created user: {user.email} ({user.get_role_display()})')
                        
                        results['success'] += 1
                        
                    except Exception as e:
                        results['errors'] += 1
                        results['error_details'].append(f'Row {row_num}: {str(e)}')
                        logger.error(f'Error creating user from row {row_num}: {str(e)}')
        
        return results
    
    def import_doctors(self, csv_file, dry_run, send_emails, skip_existing):
        """
        Import doctors from CSV
        Expected columns: first_name, last_name, email, its_id, phone_number, 
                         license_number, specialty, experience_years, moze_name
        """
        results = {'success': 0, 'skipped': 0, 'errors': 0, 'error_details': []}
        
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            with transaction.atomic():
                for row_num, row in enumerate(reader, 1):
                    try:
                        # Validate required fields
                        if not row.get('email') or not row.get('license_number'):
                            results['errors'] += 1
                            results['error_details'].append(f'Row {row_num}: Missing email or license_number')
                            continue
                        
                        email = row['email'].strip().lower()
                        its_id = row.get('its_id', '').strip()
                        
                        # Check for existing user
                        existing_user = User.objects.filter(email=email).first()
                        if existing_user and skip_existing:
                            results['skipped'] += 1
                            continue
                        elif existing_user:
                            results['errors'] += 1
                            results['error_details'].append(f'Row {row_num}: User already exists: {email}')
                            continue
                        
                        if not dry_run:
                            # Generate temporary password
                            temp_password = self.generate_password()
                            
                            # Create user
                            user = User.objects.create_user(
                                username=email,
                                email=email,
                                first_name=row.get('first_name', '').strip(),
                                last_name=row.get('last_name', '').strip(),
                                role='doctor',
                                its_id=its_id if its_id else None,
                                phone_number=row.get('phone_number', '').strip() or None,
                                specialty=row.get('specialty', '').strip() or None,
                                password=temp_password
                            )
                            
                            # Find assigned moze
                            assigned_moze = None
                            moze_name = row.get('moze_name', '').strip()
                            if moze_name:
                                assigned_moze = Moze.objects.filter(name__icontains=moze_name).first()
                            
                            # Create doctor profile
                            doctor = Doctor.objects.create(
                                user=user,
                                license_number=row['license_number'].strip(),
                                experience_years=int(row.get('experience_years', 0) or 0),
                                assigned_moze=assigned_moze,
                                is_verified=False  # Require manual verification
                            )
                            
                            # Send welcome email
                            if send_emails and user.email:
                                NotificationService.send_welcome_email(user, temp_password)
                            
                            self.stdout.write(f'Created doctor: {user.email} (License: {doctor.license_number})')
                        
                        results['success'] += 1
                        
                    except Exception as e:
                        results['errors'] += 1
                        results['error_details'].append(f'Row {row_num}: {str(e)}')
                        logger.error(f'Error creating doctor from row {row_num}: {str(e)}')
        
        return results
    
    def import_patients(self, csv_file, dry_run, send_emails, skip_existing):
        """
        Import patients from CSV
        Expected columns: first_name, last_name, email, its_id, phone_number, 
                         date_of_birth, emergency_contact, medical_history
        """
        results = {'success': 0, 'skipped': 0, 'errors': 0, 'error_details': []}
        
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            with transaction.atomic():
                for row_num, row in enumerate(reader, 1):
                    try:
                        # For patients, email is optional but ITS ID should be available
                        email = row.get('email', '').strip().lower() or None
                        its_id = row.get('its_id', '').strip()
                        
                        if not its_id and not email:
                            results['errors'] += 1
                            results['error_details'].append(f'Row {row_num}: Missing both email and ITS ID')
                            continue
                        
                        # Check for existing user
                        existing_user = None
                        if email:
                            existing_user = User.objects.filter(email=email).first()
                        if not existing_user and its_id:
                            existing_user = User.objects.filter(its_id=its_id).first()
                        
                        if existing_user and skip_existing:
                            results['skipped'] += 1
                            continue
                        elif existing_user:
                            results['errors'] += 1
                            results['error_details'].append(f'Row {row_num}: User already exists')
                            continue
                        
                        if not dry_run:
                            # Generate username and temporary password
                            username = email or f"patient_{its_id}"
                            temp_password = self.generate_password()
                            
                            # Parse date of birth
                            date_of_birth = None
                            if row.get('date_of_birth'):
                                try:
                                    date_of_birth = datetime.strptime(row['date_of_birth'], '%Y-%m-%d').date()
                                except ValueError:
                                    pass
                            
                            # Create user
                            user = User.objects.create_user(
                                username=username,
                                email=email,
                                first_name=row.get('first_name', '').strip(),
                                last_name=row.get('last_name', '').strip(),
                                role='student',  # Default role for patients
                                its_id=its_id if its_id else None,
                                phone_number=row.get('phone_number', '').strip() or None,
                                password=temp_password
                            )
                            
                            # Create patient profile
                            patient = Patient.objects.create(
                                user=user,
                                date_of_birth=date_of_birth,
                                emergency_contact=row.get('emergency_contact', '').strip() or None,
                                medical_history=row.get('medical_history', '').strip() or None
                            )
                            
                            # Send welcome email
                            if send_emails and user.email:
                                NotificationService.send_welcome_email(user, temp_password)
                            
                            self.stdout.write(f'Created patient: {user.get_full_name()} (ITS: {its_id})')
                        
                        results['success'] += 1
                        
                    except Exception as e:
                        results['errors'] += 1
                        results['error_details'].append(f'Row {row_num}: {str(e)}')
                        logger.error(f'Error creating patient from row {row_num}: {str(e)}')
        
        return results
    
    def generate_password(self, length=12):
        """Generate a secure temporary password"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))