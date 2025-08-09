from django.core.management.base import BaseCommand
from bulk_upload.models import UploadTemplate


class Command(BaseCommand):
    help = 'Create initial upload templates for different data types'

    def handle(self, *args, **options):
        templates = [
            {
                'upload_type': 'users',
                'name': 'Users Template',
                'description': 'Template for uploading user accounts with ITS integration',
                'required_columns': ['its_id', 'first_name', 'last_name', 'email', 'role'],
                'optional_columns': ['mobile_number', 'occupation', 'qualification', 'idara', 'category'],
                'column_mappings': {
                    'its_id': 'its_id',
                    'first_name': 'first_name',
                    'last_name': 'last_name',
                    'email': 'email',
                    'role': 'role',
                    'mobile_number': 'mobile_number',
                    'occupation': 'occupation',
                    'qualification': 'qualification',
                    'idara': 'idara',
                    'category': 'category'
                },
                'validation_rules': {
                    'its_id': {'type': 'string', 'length': 8, 'pattern': r'^\d{8}$'},
                    'email': {'type': 'email'},
                    'role': {'type': 'choice', 'choices': ['aamil', 'moze_coordinator', 'doctor', 'student', 'badri_mahal_admin']}
                },
                'sample_data': [
                    {
                        'its_id': '50000101',
                        'first_name': 'Ahmed',
                        'last_name': 'Khan',
                        'email': 'ahmed.khan@example.com',
                        'role': 'student',
                        'mobile_number': '+919876543210',
                        'occupation': 'Student',
                        'qualification': 'Bachelor of Arts',
                        'idara': 'Mumbai',
                        'category': 'Student'
                    },
                    {
                        'its_id': '50000102',
                        'first_name': 'Fatima',
                        'last_name': 'Ahmed',
                        'email': 'fatima.ahmed@example.com',
                        'role': 'doctor',
                        'mobile_number': '+919876543211',
                        'occupation': 'Doctor',
                        'qualification': 'MBBS',
                        'idara': 'Mumbai',
                        'category': 'Professional'
                    }
                ]
            },
            {
                'upload_type': 'students',
                'name': 'Students Template',
                'description': 'Template for uploading student records and academic information',
                'required_columns': ['its_id', 'student_id', 'first_name', 'last_name'],
                'optional_columns': ['email', 'academic_level', 'enrollment_status', 'enrollment_date', 'expected_graduation'],
                'column_mappings': {
                    'its_id': 'its_id',
                    'student_id': 'student_id',
                    'first_name': 'first_name',
                    'last_name': 'last_name',
                    'email': 'email',
                    'academic_level': 'academic_level',
                    'enrollment_status': 'enrollment_status',
                    'enrollment_date': 'enrollment_date',
                    'expected_graduation': 'expected_graduation'
                },
                'validation_rules': {
                    'its_id': {'type': 'string', 'length': 8, 'pattern': r'^\d{8}$'},
                    'academic_level': {'type': 'choice', 'choices': ['undergraduate', 'postgraduate', 'doctoral', 'diploma']},
                    'enrollment_status': {'type': 'choice', 'choices': ['active', 'suspended', 'graduated', 'withdrawn']},
                    'enrollment_date': {'type': 'date', 'format': 'YYYY-MM-DD'},
                    'expected_graduation': {'type': 'date', 'format': 'YYYY-MM-DD'}
                },
                'sample_data': [
                    {
                        'its_id': '50000101',
                        'student_id': 'STU001',
                        'first_name': 'Ahmed',
                        'last_name': 'Khan',
                        'email': 'ahmed.khan@student.example.com',
                        'academic_level': 'undergraduate',
                        'enrollment_status': 'active',
                        'enrollment_date': '2023-01-15',
                        'expected_graduation': '2027-06-30'
                    }
                ]
            },
            {
                'upload_type': 'doctors',
                'name': 'Doctors Template',
                'description': 'Template for uploading doctor profiles and medical information',
                'required_columns': ['its_id', 'first_name', 'last_name', 'specialization'],
                'optional_columns': ['email', 'license_number', 'experience_years', 'consultation_fee', 'qualifications', 'languages_spoken', 'clinic_address', 'is_available'],
                'column_mappings': {
                    'its_id': 'its_id',
                    'first_name': 'first_name',
                    'last_name': 'last_name',
                    'email': 'email',
                    'specialization': 'specialization',
                    'license_number': 'license_number',
                    'experience_years': 'experience_years',
                    'consultation_fee': 'consultation_fee',
                    'qualifications': 'qualifications',
                    'languages_spoken': 'languages_spoken',
                    'clinic_address': 'clinic_address',
                    'is_available': 'is_available'
                },
                'validation_rules': {
                    'its_id': {'type': 'string', 'length': 8, 'pattern': r'^\d{8}$'},
                    'experience_years': {'type': 'integer', 'min': 0, 'max': 50},
                    'consultation_fee': {'type': 'decimal', 'min': 0},
                    'is_available': {'type': 'boolean', 'values': ['true', 'false']}
                },
                'sample_data': [
                    {
                        'its_id': '50000201',
                        'first_name': 'Dr. Ahmed',
                        'last_name': 'Abdullah',
                        'email': 'dr.ahmed@example.com',
                        'specialization': 'Cardiology',
                        'license_number': 'LIC12345',
                        'experience_years': '10',
                        'consultation_fee': '1000.00',
                        'qualifications': 'MBBS, MD Cardiology',
                        'languages_spoken': 'English, Arabic, Hindi',
                        'clinic_address': 'Mumbai Central Hospital',
                        'is_available': 'true'
                    }
                ]
            },
            {
                'upload_type': 'patients',
                'name': 'Patients Template',
                'description': 'Template for uploading patient records and contact information',
                'required_columns': ['its_id', 'first_name', 'last_name'],
                'optional_columns': ['date_of_birth', 'gender', 'phone_number', 'email', 'address', 'emergency_contact_name', 'emergency_contact_phone'],
                'column_mappings': {
                    'its_id': 'its_id',
                    'first_name': 'first_name',
                    'last_name': 'last_name',
                    'date_of_birth': 'date_of_birth',
                    'gender': 'gender',
                    'phone_number': 'phone_number',
                    'email': 'email',
                    'address': 'address',
                    'emergency_contact_name': 'emergency_contact_name',
                    'emergency_contact_phone': 'emergency_contact_phone'
                },
                'validation_rules': {
                    'its_id': {'type': 'string', 'length': 8, 'pattern': r'^\d{8}$'},
                    'date_of_birth': {'type': 'date', 'format': 'YYYY-MM-DD'},
                    'gender': {'type': 'choice', 'choices': ['male', 'female', 'other']},
                    'phone_number': {'type': 'phone'},
                    'email': {'type': 'email'}
                },
                'sample_data': [
                    {
                        'its_id': '50000301',
                        'first_name': 'Fatima',
                        'last_name': 'Sheikh',
                        'date_of_birth': '1990-05-15',
                        'gender': 'female',
                        'phone_number': '+919876543210',
                        'email': 'fatima.sheikh@example.com',
                        'address': 'Mumbai, Maharashtra',
                        'emergency_contact_name': 'Ahmed Sheikh',
                        'emergency_contact_phone': '+919876543211'
                    }
                ]
            },
            {
                'upload_type': 'moze',
                'name': 'Moze Centers Template',
                'description': 'Template for uploading Moze center information and management details',
                'required_columns': ['name', 'location'],
                'optional_columns': ['address', 'aamil_its_id', 'coordinator_its_id', 'capacity', 'contact_phone', 'contact_email', 'is_active'],
                'column_mappings': {
                    'name': 'name',
                    'location': 'location',
                    'address': 'address',
                    'aamil_its_id': 'aamil_its_id',
                    'coordinator_its_id': 'coordinator_its_id',
                    'capacity': 'capacity',
                    'contact_phone': 'contact_phone',
                    'contact_email': 'contact_email',
                    'is_active': 'is_active'
                },
                'validation_rules': {
                    'name': {'type': 'string', 'max_length': 100},
                    'location': {'type': 'string', 'max_length': 200},
                    'aamil_its_id': {'type': 'string', 'length': 8, 'pattern': r'^\d{8}$'},
                    'coordinator_its_id': {'type': 'string', 'length': 8, 'pattern': r'^\d{8}$'},
                    'capacity': {'type': 'integer', 'min': 1, 'max': 1000},
                    'contact_email': {'type': 'email'},
                    'is_active': {'type': 'boolean', 'values': ['true', 'false']}
                },
                'sample_data': [
                    {
                        'name': 'Al-Noor Moze',
                        'location': 'Mumbai Central',
                        'address': '123 Main Street, Mumbai Central, Mumbai',
                        'aamil_its_id': '50000051',
                        'coordinator_its_id': '50000052',
                        'capacity': '150',
                        'contact_phone': '+912212345678',
                        'contact_email': 'alnoor@moze.example.com',
                        'is_active': 'true'
                    }
                ]
            }
        ]

        created_count = 0
        updated_count = 0

        for template_data in templates:
            template, created = UploadTemplate.objects.update_or_create(
                upload_type=template_data['upload_type'],
                defaults={
                    'name': template_data['name'],
                    'description': template_data['description'],
                    'required_columns': template_data['required_columns'],
                    'optional_columns': template_data['optional_columns'],
                    'column_mappings': template_data['column_mappings'],
                    'validation_rules': template_data['validation_rules'],
                    'sample_data': template_data['sample_data'],
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created template: {template.name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated template: {template.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Template creation completed! Created: {created_count}, Updated: {updated_count}'
            )
        )