from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
import traceback

# Import all models
from accounts.models import User, UserProfile
from moze.models import Moze, MozeComment, MozeSettings
from doctordirectory.models import Doctor, Specialty, Appointment, MedicalRecord
from mahalshifa.models import Hospital, Department, Patient, MedicalRecord as MahalMedicalRecord, Appointment as MahalAppointment
from students.models import Student, AcademicRecord, Course, Grade
from evaluation.models import EvaluationForm, EvaluationSubmission, EvaluationQuestion
from surveys.models import Survey, SurveyResponse, SurveyQuestion
from araz.models import Petition, PetitionStatus
from photos.models import Album, Photo

User = get_user_model()

class Command(BaseCommand):
    help = 'Create minimal test data for all apps'

    def handle(self, *args, **options):
        self.stdout.write("🚀 Starting minimal test data generation...")
        
        try:
            with transaction.atomic():
                # Create 1 admin
                self.stdout.write("📋 Creating admin...")
                admin = User.objects.create_user(
                    username='admin_1',
                    email='admin@test.com',
                    password='admin123',
                    role='badri_mahal_admin',
                    its_id='12345678'
                )
                
                # Create 1 staff
                self.stdout.write("👥 Creating staff...")
                staff = User.objects.create_user(
                    username='staff_1',
                    email='staff@test.com',
                    password='staff123',
                    role='staff',
                    its_id='12345679'
                )
                
                # Create 1 aamil and 1 moze
                self.stdout.write("🏢 Creating Moze and Aamil...")
                aamil = User.objects.create_user(
                    username='aamil_1',
                    email='aamil@test.com',
                    password='aamil123',
                    role='aamil',
                    its_id='12345680'
                )
                
                moze = Moze.objects.create(
                    name='Test Moze',
                    aamil=aamil,
                    location='Test City',
                    address='Test Address',
                    phone='1234567890',
                    email='moze@test.com',
                    description='Test moze description'
                )
                
                # Create 1 doctor
                self.stdout.write("👨‍⚕️ Creating Doctor...")
                specialty = Specialty.objects.create(name='Cardiology')
                doctor = Doctor.objects.create(
                    user=User.objects.create_user(
                        username='doctor_1',
                        email='doctor@test.com',
                        password='doctor123',
                        role='doctor',
                        its_id='12345681'
                    ),
                    specialty=specialty,
                    experience_years=5,
                    phone='1234567891',
                    address='Doctor Address',
                    is_verified=True
                )
                
                # Create 1 hospital
                self.stdout.write("🏥 Creating Hospital...")
                hospital = Hospital.objects.create(
                    name='Test Hospital',
                    moze=moze,
                    address='Hospital Address',
                    phone='1234567892',
                    email='hospital@test.com'
                )
                
                # Create 1 student
                self.stdout.write("👨‍🎓 Creating Student...")
                student = Student.objects.create(
                    user=User.objects.create_user(
                        username='student_1',
                        email='student@test.com',
                        password='student123',
                        role='student',
                        its_id='12345682'
                    ),
                    moze=moze,
                    student_id='STU001',
                    enrollment_date=timezone.now().date()
                )
                
                # Create 1 patient
                self.stdout.write("👥 Creating Patient...")
                patient = Patient.objects.create(
                    name='Test Patient',
                    hospital=hospital,
                    moze=moze,
                    age=30,
                    gender='M',
                    phone='1234567893',
                    address='Patient Address'
                )
                
                # Create 1 medical record
                self.stdout.write("📋 Creating Medical Record...")
                medical_record = MahalMedicalRecord.objects.create(
                    patient=patient,
                    doctor=doctor,
                    moze=moze,
                    diagnosis='Test diagnosis',
                    treatment='Test treatment',
                    notes='Test notes'
                )
                
                # Create 1 appointment
                self.stdout.write("📅 Creating Appointment...")
                appointment = MahalAppointment.objects.create(
                    patient=patient,
                    doctor=doctor,
                    moze=moze,
                    appointment_date=timezone.now() + timedelta(days=7),
                    status='scheduled',
                    notes='Test appointment'
                )
                
                # Create 1 evaluation form
                self.stdout.write("📊 Creating Evaluation Form...")
                evaluation_form = EvaluationForm.objects.create(
                    title='Test Evaluation',
                    description='Test evaluation description',
                    moze=moze,
                    is_active=True
                )
                
                # Create 1 survey
                self.stdout.write("📝 Creating Survey...")
                survey = Survey.objects.create(
                    title='Test Survey',
                    description='Test survey description',
                    moze=moze,
                    is_active=True,
                    questions={'questions': [{'text': 'Test question', 'type': 'text'}]}
                )
                
                # Create 1 petition
                self.stdout.write("📜 Creating Petition...")
                petition = Petition.objects.create(
                    title='Test Petition',
                    description='Test petition description',
                    petitioner=patient,
                    status='pending'
                )
                
                # Create 1 album
                self.stdout.write("📸 Creating Album...")
                album = Album.objects.create(
                    title='Test Album',
                    description='Test album description',
                    moze=moze
                )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        "✅ Minimal test data created successfully!\n"
                        "Created: 1 admin, 1 staff, 1 aamil, 1 moze, 1 doctor, 1 hospital, "
                        "1 student, 1 patient, 1 medical record, 1 appointment, "
                        "1 evaluation form, 1 survey, 1 petition, 1 album"
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error during data creation: {e}")
            )
            traceback.print_exc()
            raise