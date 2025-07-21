import random
import json
from datetime import datetime, timedelta, date, time
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction

from moze.models import Moze, MozeComment, MozeSettings
from doctordirectory.models import (
    Doctor, Patient, Appointment, MedicalRecord, Prescription, 
    LabTest, VitalSigns, DoctorSchedule, PatientLog, DoctorAvailability,
    MedicalService
)
from surveys.models import Survey, SurveyResponse, SurveyReminder
from photos.models import PhotoAlbum, Photo
# from evaluation.models import DoctorEvaluation
# from araz.models import DuaAraz  
# from students.models import Student, Course, Enrollment

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate database with comprehensive test data for all modules'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=50,
            help='Number of users to create'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before populating'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            self.clear_data()

        with transaction.atomic():
            self.stdout.write('Creating test data...')
            
            # Create users and profiles
            users = self.create_users(options['users'])
            self.stdout.write(f'✅ Created {len(users)} users')
            
            # Create Moze data
            mozes = self.create_moze_data(users)
            self.stdout.write(f'✅ Created {len(mozes)} Mozes')
            
            # Create doctor and medical data
            doctors, patients = self.create_medical_data(users, mozes)
            self.stdout.write(f'✅ Created {len(doctors)} doctors and {len(patients)} patients')
            
            # Create survey data
            surveys = self.create_survey_data(users)
            self.stdout.write(f'✅ Created {len(surveys)} surveys')
            
            # Create photo albums
            albums = self.create_photo_data(users, mozes)
            self.stdout.write(f'✅ Created {len(albums)} photo albums')
            
            # TODO: Enable when these apps are ready
            # evaluations = self.create_evaluation_data(users, doctors)
            # araz_requests = self.create_araz_data(users)
            # students = self.create_student_data(users)
            evaluations = []
            araz_requests = []
            students = []

        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Successfully populated database with comprehensive test data!\n'
                f'📊 Summary:\n'
                f'   - {len(users)} Users (all roles)\n'
                f'   - {len(mozes)} Mozes with schedules\n'
                f'   - {len(doctors)} Doctors with availability\n'
                f'   - {len(patients)} Patients with records\n'
                f'   - {len(surveys)} Surveys with responses\n'
                f'   - {len(albums)} Photo albums\n'
                f'   - {len(evaluations)} Doctor evaluations\n'
                f'   - {len(araz_requests)} Dua Araz requests\n'
                f'   - {len(students)} Students with courses\n'
                f'\n🚀 Ready for comprehensive testing!'
            )
        )

    def clear_data(self):
        """Clear existing test data while preserving admin user"""
        User.objects.exclude(username='admin').delete()
        Moze.objects.all().delete()
        Doctor.objects.all().delete()
        Patient.objects.all().delete()
        Survey.objects.all().delete()
        PhotoAlbum.objects.all().delete()
        # DoctorEvaluation.objects.all().delete()
        # DuaAraz.objects.all().delete()
        # Student.objects.all().delete()

    def create_users(self, count):
        """Create diverse users across all roles"""
        users = []
        roles = ['aamil', 'moze_coordinator', 'doctor', 'student', 'badri_mahal_admin']
        
        # Sample names for different roles
        names_by_role = {
            'aamil': [
                ('Ali', 'Hassan'), ('Fatima', 'Khan'), ('Omar', 'Ahmed'),
                ('Aisha', 'Sheikh'), ('Hassan', 'Ali'), ('Zainab', 'Qureshi')
            ],
            'moze_coordinator': [
                ('Hussain', 'Memon'), ('Mariam', 'Dawood'), ('Ahmed', 'Bharuchi'),
                ('Kulsum', 'Vohra'), ('Mustafa', 'Jamali'), ('Sakina', 'Rangwala')
            ],
            'doctor': [
                ('Dr. Yusuf', 'Siddiqui'), ('Dr. Maryam', 'Bhatty'), ('Dr. Iqbal', 'Husain'),
                ('Dr. Rukhsana', 'Merchant'), ('Dr. Ammar', 'Khorakiwala'), ('Dr. Tahera', 'Mithaiwala')
            ],
            'student': [
                ('Murtaza', 'Kothari'), ('Fatema', 'Shikari'), ('Salman', 'Nomani'),
                ('Zahra', 'Kagalwala'), ('Ibrahim', 'Najmi'), ('Umme Salma', 'Tinwala')
            ],
            'badri_mahal_admin': [
                ('Shabir', 'Kagalwala'), ('Nafisa', 'Khorakiwala'), ('Tasneem', 'Soofi')
            ]
        }
        
        for i in range(count):
            role = random.choice(roles)
            first_name, last_name = random.choice(names_by_role[role])
            
            # Generate ITS ID (8 digits)
            its_id = f"{random.randint(10000000, 99999999)}"
            
            user = User.objects.create_user(
                username=f"{first_name.lower().replace(' ', '').replace('.', '')}{i}",
                email=f"{first_name.lower().replace(' ', '').replace('.', '')}{i}@example.com",
                password='password123',
                first_name=first_name,
                last_name=last_name,
                role=role,
                its_id=its_id,
                phone_number=f"+1{random.randint(1000000000, 9999999999)}",
                is_active=True
            )
            users.append(user)
        
        return users

    def create_moze_data(self, users):
        """Create Moze locations with schedules and comments"""
        moze_coordinators = [u for u in users if u.role == 'moze_coordinator']
        
        moze_locations = [
            ('Masjid-e-Noorani', 'Dadar', 'Mumbai'),
            ('Masjid-e-Husaini', 'Bandra', 'Mumbai'),
            ('Masjid-e-Qadri', 'Andheri', 'Mumbai'),
            ('Masjid-e-Askari', 'Kurla', 'Mumbai'),
            ('Burhani Masjid', 'Dongri', 'Mumbai'),
            ('Masjid-e-Saifee', 'Crawford Market', 'Mumbai'),
            ('Jamea Masjid', 'Mahim', 'Mumbai'),
            ('Masjid-e-Ali', 'Worli', 'Mumbai'),
        ]
        
        mozes = []
        for i, (name, area, city) in enumerate(moze_locations):
            coordinator = random.choice(moze_coordinators) if moze_coordinators else None
            aamil = random.choice([u for u in users if u.role == 'aamil']) if any(u.role == 'aamil' for u in users) else random.choice(users)
            
            moze = Moze.objects.create(
                name=name,
                location=f"{area}, {city}",
                address=f"Full address of {name}, {area}, {city}",
                aamil=aamil,
                moze_coordinator=coordinator,
                capacity=random.randint(50, 500),
                contact_phone=f"+91{random.randint(7000000000, 9999999999)}",
                contact_email=f"{name.lower().replace(' ', '').replace('-', '')}@moze.com",
                is_active=True
            )
            
            # Create comments
            for _ in range(random.randint(3, 8)):
                commenter = random.choice(users)
                MozeComment.objects.create(
                    moze=moze,
                    author=commenter,
                    content=random.choice([
                        "Excellent facilities and very clean environment.",
                        "Perfect location for daily prayers.",
                        "Great community feeling here.",
                        "Well-maintained and peaceful atmosphere.",
                        "Helpful and courteous staff.",
                        "Beautiful architecture and calming ambience."
                    ]),
                    created_at=timezone.now() - timedelta(days=random.randint(1, 90))
                )
            
            # Create settings
            MozeSettings.objects.create(
                moze=moze,
                allow_walk_ins=True,
                appointment_duration=random.choice([20, 30, 45]),
                working_days=[0, 1, 2, 3, 4, 5],  # Monday to Saturday
                emergency_contact=f"+91{random.randint(7000000000, 9999999999)}",
                special_instructions="Please arrive 15 minutes before appointment time."
            )
            
            mozes.append(moze)
        
        return mozes

    def create_medical_data(self, users, mozes):
        """Create comprehensive medical data"""
        doctors_users = [u for u in users if u.role == 'doctor']
        patient_users = [u for u in users if u.role in ['aamil', 'student']]
        
        doctors = []
        patients = []
        
        # Create doctors
        specialties = [
            'General Medicine', 'Cardiology', 'Pediatrics', 'Orthopedics',
            'Dermatology', 'Gynecology', 'Neurology', 'ENT', 'Ophthalmology'
        ]
        
        for doctor_user in doctors_users:
            doctor = Doctor.objects.create(
                user=doctor_user,
                name=doctor_user.get_full_name(),
                its_id=doctor_user.its_id,
                specialty=random.choice(specialties),
                qualification=random.choice([
                    'MBBS, MD', 'MBBS, MS', 'MBBS, DM', 'MBBS, MCh',
                    'MBBS, DNB', 'MBBS, FCPS'
                ]),
                experience_years=random.randint(2, 25),
                assigned_moze=random.choice(mozes),
                is_verified=True,
                is_available=True,
                license_number=f"MH{random.randint(10000, 99999)}",
                consultation_fee=Decimal(random.randint(200, 1000)),
                phone=doctor_user.phone_number,
                email=doctor_user.email,
                languages_spoken="English, Hindi, Gujarati, Urdu",
                bio=f"Experienced {random.choice(specialties)} specialist with {random.randint(5, 20)} years of practice."
            )
            
            # Create medical services
            service_types = ['consultation', 'checkup', 'procedure', 'therapy']
            for _ in range(random.randint(2, 4)):
                MedicalService.objects.create(
                    doctor=doctor,
                    name=f"{doctor.specialty} {random.choice(['Consultation', 'Checkup', 'Treatment'])}",
                    service_type=random.choice(service_types),
                    description=f"Professional {doctor.specialty.lower()} service",
                    duration_minutes=random.choice([30, 45, 60]),
                    fee=Decimal(random.randint(300, 800)),
                    is_active=True
                )
            
            # Create doctor availability
            for day in range(7):  # Monday to Sunday
                if random.choice([True, True, False]):  # 2/3 chance of being available
                    DoctorAvailability.objects.create(
                        doctor=doctor,
                        day_of_week=day,
                        start_time=time(random.randint(8, 10), random.choice([0, 30])),
                        end_time=time(random.randint(16, 18), random.choice([0, 30])),
                        is_active=True
                    )
            
            # Create schedules for next 30 days
            for days_ahead in range(30):
                schedule_date = date.today() + timedelta(days=days_ahead)
                if random.choice([True, True, False]):  # 2/3 chance
                    DoctorSchedule.objects.create(
                        doctor=doctor,
                        date=schedule_date,
                        start_time=time(9, 0),
                        end_time=time(17, 0),
                        moze=doctor.assigned_moze,
                        is_available=True,
                        max_patients=random.randint(15, 25),
                        schedule_type=random.choice(['regular', 'special'])
                    )
            
            doctors.append(doctor)
        
        # Create patients
        for patient_user in patient_users[:len(patient_users)//2]:  # Half of non-doctor users
            patient = Patient.objects.create(
                user=patient_user,
                date_of_birth=date.today() - timedelta(days=random.randint(6570, 25550)),  # 18-70 years
                gender=random.choice(['M', 'F']),
                blood_group=random.choice(['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']),
                emergency_contact=f"+91{random.randint(7000000000, 9999999999)}",
                medical_history=random.choice([
                    "No significant medical history",
                    "Hypertension, controlled with medication",
                    "Diabetes mellitus type 2",
                    "Asthma, well controlled",
                    "Previous surgery: appendectomy"
                ]),
                allergies=random.choice([
                    "No known allergies",
                    "Penicillin allergy",
                    "Peanut allergy",
                    "Dust mite allergy",
                    "None reported"
                ]),
                current_medications=random.choice([
                    "None",
                    "Metformin 500mg BD",
                    "Amlodipine 5mg OD",
                    "Salbutamol inhaler PRN",
                    "Multivitamin OD"
                ])
            )
            patients.append(patient)
        
        # Create appointments and medical records
        if doctors and patients:
            # Create past and future appointments
            for _ in range(random.randint(50, 100)):
                doctor = random.choice(doctors)
                patient = random.choice(patients)
                
                # Random date in past or future
                days_offset = random.randint(-60, 30)
                appointment_date = date.today() + timedelta(days=days_offset)
                
                appointment = Appointment.objects.create(
                    doctor=doctor,
                    patient=patient,
                    appointment_date=appointment_date,
                    appointment_time=time(random.randint(9, 16), random.choice([0, 30])),
                    status=random.choice(['pending', 'confirmed', 'completed', 'cancelled']),
                    reason_for_visit=random.choice([
                        "General checkup",
                        "Follow-up consultation",
                        "Fever and cough",
                        "Routine screening",
                        "Blood pressure check",
                        "Skin condition",
                        "Joint pain"
                    ]),
                    notes="Patient appointment for routine care"
                )
                
                # Create medical record for completed appointments
                if appointment.status == 'completed' and days_offset < 0:
                    medical_record = MedicalRecord.objects.create(
                        patient=patient,
                        doctor=doctor,
                        appointment=appointment,
                        diagnosis=random.choice([
                            "Hypertension",
                            "Common cold",
                            "Gastritis",
                            "Anxiety disorder",
                            "Migraine",
                            "Lower back pain",
                            "Allergic rhinitis"
                        ]),
                        symptoms=random.choice([
                            "Headache, fatigue",
                            "Cough, runny nose",
                            "Abdominal pain",
                            "Chest tightness",
                            "Joint stiffness",
                            "Skin rash",
                            "Dizziness"
                        ]),
                        treatment_plan="Rest, medication as prescribed, follow-up in 2 weeks",
                        medications="As per prescription",
                        follow_up_required=random.choice([True, False])
                    )
                    
                    # Create prescription
                    Prescription.objects.create(
                        patient=patient,
                        doctor=doctor,
                        medical_record=medical_record,
                        medication_name=random.choice([
                            "Paracetamol", "Amoxicillin", "Omeprazole",
                            "Cetirizine", "Ibuprofen", "Metformin"
                        ]),
                        dosage=random.choice(["500mg", "250mg", "10mg", "5mg"]),
                        frequency=random.choice(["Once daily", "Twice daily", "Three times daily"]),
                        duration=random.choice(["5 days", "7 days", "10 days", "2 weeks"]),
                        instructions="Take after meals",
                        refills_allowed=random.randint(0, 3)
                    )
                    
                    # Create vital signs
                    VitalSigns.objects.create(
                        patient=patient,
                        medical_record=medical_record,
                        blood_pressure_systolic=random.randint(110, 140),
                        blood_pressure_diastolic=random.randint(70, 90),
                        heart_rate=random.randint(60, 100),
                        temperature=round(random.uniform(98.0, 101.0), 1),
                        respiratory_rate=random.randint(12, 20),
                        oxygen_saturation=random.randint(95, 100),
                        weight=round(random.uniform(45.0, 90.0), 1),
                        height=random.randint(150, 185)
                    )
                    
                    # Create patient log
                    PatientLog.objects.create(
                        patient_its_id=patient.user.its_id,
                        patient_name=patient.user.get_full_name(),
                        ailment=medical_record.diagnosis,
                        seen_by=doctor,
                        moze=doctor.assigned_moze,
                        symptoms=medical_record.symptoms,
                        diagnosis=medical_record.diagnosis,
                        prescription=medical_record.medications,
                        visit_type=random.choice(['consultation', 'follow_up', 'screening'])
                    )
        
        return doctors, patients

    def create_survey_data(self, users):
        """Create surveys with responses"""
        survey_creators = [u for u in users if u.role in ['badri_mahal_admin', 'moze_coordinator']]
        
        survey_templates = [
            {
                'title': 'Community Health Assessment',
                'description': 'Annual health survey for community members',
                'target_role': 'all',
                'questions': [
                    {
                        "id": 1,
                        "type": "multiple_choice",
                        "text": "How would you rate your overall health?",
                        "required": True,
                        "options": ["Excellent", "Good", "Fair", "Poor"]
                    },
                    {
                        "id": 2,
                        "type": "checkbox",
                        "text": "Which health services have you used this year?",
                        "required": False,
                        "options": ["General consultation", "Specialist care", "Emergency services", "Health screening"]
                    },
                    {
                        "id": 3,
                        "type": "rating",
                        "text": "Rate the quality of medical services (1-5)",
                        "required": True,
                        "options": ["1", "2", "3", "4", "5"]
                    },
                    {
                        "id": 4,
                        "type": "textarea",
                        "text": "Any suggestions for improvement?",
                        "required": False
                    }
                ]
            },
            {
                'title': 'Moze Facilities Feedback',
                'description': 'Feedback on mosque facilities and services',
                'target_role': 'aamil',
                'questions': [
                    {
                        "id": 1,
                        "type": "rating",
                        "text": "Rate the cleanliness of facilities (1-5)",
                        "required": True,
                        "options": ["1", "2", "3", "4", "5"]
                    },
                    {
                        "id": 2,
                        "type": "multiple_choice",
                        "text": "How often do you visit the mosque?",
                        "required": True,
                        "options": ["Daily", "Weekly", "Monthly", "Occasionally"]
                    },
                    {
                        "id": 3,
                        "type": "text",
                        "text": "Which mosque do you primarily attend?",
                        "required": True
                    }
                ]
            },
            {
                'title': 'Student Academic Survey',
                'description': 'Survey for students about their academic experience',
                'target_role': 'student',
                'questions': [
                    {
                        "id": 1,
                        "type": "multiple_choice",
                        "text": "What is your current academic level?",
                        "required": True,
                        "options": ["Undergraduate", "Graduate", "Postgraduate", "Professional"]
                    },
                    {
                        "id": 2,
                        "type": "rating",
                        "text": "Rate your satisfaction with courses (1-5)",
                        "required": True,
                        "options": ["1", "2", "3", "4", "5"]
                    }
                ]
            }
        ]
        
        surveys = []
        for template in survey_templates:
            creator = random.choice(survey_creators) if survey_creators else random.choice(users)
            
            survey = Survey.objects.create(
                title=template['title'],
                description=template['description'],
                target_role=template['target_role'],
                questions=template['questions'],
                created_by=creator,
                is_active=True,
                is_anonymous=random.choice([True, False]),
                allow_multiple_responses=False,
                show_results=True,
                start_date=timezone.now() - timedelta(days=random.randint(1, 30)),
                end_date=timezone.now() + timedelta(days=random.randint(30, 90))
            )
            
            # Create responses
            eligible_users = users if template['target_role'] == 'all' else [u for u in users if u.role == template['target_role']]
            respondents = random.sample(eligible_users, min(len(eligible_users), random.randint(5, 15)))
            
            for respondent in respondents:
                answers = {}
                for question in template['questions']:
                    if question['type'] == 'multiple_choice':
                        answers[str(question['id'])] = random.choice(question['options'])
                    elif question['type'] == 'checkbox':
                        selected = random.sample(question['options'], random.randint(1, len(question['options'])))
                        answers[str(question['id'])] = selected
                    elif question['type'] == 'rating':
                        answers[str(question['id'])] = random.choice(question['options'])
                    elif question['type'] == 'text':
                        answers[str(question['id'])] = f"Sample text response from {respondent.get_full_name()}"
                    elif question['type'] == 'textarea':
                        answers[str(question['id'])] = "This is a detailed response with suggestions and feedback."
                
                response = SurveyResponse.objects.create(
                    survey=survey,
                    respondent=respondent if not survey.is_anonymous else None,
                    answers=answers,
                    completion_time=random.randint(60, 600),  # 1-10 minutes
                    is_complete=True
                )
                # Update created_at to simulate different response times
                response.created_at = timezone.now() - timedelta(days=random.randint(0, 20))
                response.save()
            
            # Create reminders
            for user in random.sample(eligible_users, min(len(eligible_users), 10)):
                SurveyReminder.objects.create(
                    survey=survey,
                    user=user,
                    reminder_count=random.randint(0, 2),
                    has_responded=user in respondents
                )
            
            surveys.append(survey)
        
        return surveys

    def create_photo_data(self, users, mozes):
        """Create photo albums"""
        albums = []
        
        album_types = [
            ('Community Events', 'Photos from various community gatherings'),
            ('Religious Ceremonies', 'Important religious events and ceremonies'),
            ('Health Camps', 'Medical camps and health awareness programs'),
            ('Educational Programs', 'Academic and educational activities')
        ]
        
        for name, description in album_types:
            creator = random.choice([u for u in users if u.role in ['badri_mahal_admin', 'moze_coordinator']])
            
            album = PhotoAlbum.objects.create(
                name=name,
                description=description,
                created_by=creator,
                moze=random.choice(mozes),
                is_public=True,
                event_date=timezone.now().date() - timedelta(days=random.randint(1, 90))
            )
            
            # Create sample photos
            photos = []
            for i in range(random.randint(5, 12)):
                photo = Photo.objects.create(
                    title=f"{name} Photo {i+1}",
                    description=f"Beautiful moment captured during {name.lower()}",
                    subject_tag=name.lower().replace(' ', '_'),
                    moze=album.moze,
                    uploaded_by=creator,
                    category=random.choice(['event', 'documentation', 'team']),
                    is_public=True,
                    event_date=album.event_date
                )
                photos.append(photo)
            
            # Add photos to album
            album.photos.set(photos)
            if photos:
                album.cover_photo = photos[0]
                album.save()
            
            albums.append(album)
        
        return albums

    def create_evaluation_data(self, users, doctors):
        """Create doctor evaluations"""
        evaluations = []
        
        for _ in range(random.randint(20, 40)):
            evaluator = random.choice([u for u in users if u.role in ['aamil', 'student']])
            doctor = random.choice(doctors)
            
            evaluation = DoctorEvaluation.objects.create(
                doctor=doctor,
                evaluator=evaluator,
                rating=random.randint(3, 5),
                feedback=random.choice([
                    "Excellent doctor with great bedside manner.",
                    "Very professional and thorough examination.",
                    "Highly recommended for consultation.",
                    "Great experience, will visit again.",
                    "Patient and understanding doctor."
                ]),
                is_anonymous=random.choice([True, False])
            )
            evaluations.append(evaluation)
        
        return evaluations

    def create_araz_data(self, users):
        """Create Dua Araz requests"""
        araz_requests = []
        
        categories = [
            'Health & Recovery', 'Family & Relationships', 'Career & Education',
            'Financial Stability', 'Spiritual Growth', 'Community Welfare'
        ]
        
        for _ in range(random.randint(30, 50)):
            requester = random.choice(users)
            
            request = DuaAraz.objects.create(
                requester=requester,
                category=random.choice(categories),
                description=random.choice([
                    "Please pray for my family's health and wellbeing.",
                    "Seeking prayers for success in upcoming exams.",
                    "Request for dua for speedy recovery from illness.",
                    "Prayers needed for family harmony and peace.",
                    "Seeking guidance and blessings for new job.",
                    "Request for community welfare and prosperity."
                ]),
                is_urgent=random.choice([True, False]),
                is_anonymous=random.choice([True, False]),
                status=random.choice(['pending', 'acknowledged', 'completed'])
            )
            araz_requests.append(request)
        
        return araz_requests

    def create_student_data(self, users):
        """Create student academic data"""
        student_users = [u for u in users if u.role == 'student']
        students = []
        
        # Create courses
        courses_data = [
            ('Islamic Studies', 'Comprehensive study of Islamic principles'),
            ('Arabic Language', 'Classical and modern Arabic language'),
            ('Quranic Studies', 'Tafseer and Quranic sciences'),
            ('Islamic History', 'History of Islam and Muslim civilization'),
            ('Islamic Jurisprudence', 'Fiqh and Islamic law'),
            ('Hadith Studies', 'Study of Prophetic traditions')
        ]
        
        courses = []
        for name, description in courses_data:
            course = Course.objects.create(
                name=name,
                description=description,
                credits=random.randint(2, 4),
                duration_weeks=random.randint(12, 16),
                instructor=random.choice([u for u in users if u.role in ['badri_mahal_admin']]),
                is_active=True
            )
            courses.append(course)
        
        # Create students and enrollments
        for student_user in student_users:
            student = Student.objects.create(
                user=student_user,
                student_id=f"STU{random.randint(1000, 9999)}",
                enrollment_date=date.today() - timedelta(days=random.randint(30, 365)),
                academic_level=random.choice(['beginner', 'intermediate', 'advanced']),
                is_active=True
            )
            
            # Enroll in random courses
            enrolled_courses = random.sample(courses, random.randint(2, 4))
            for course in enrolled_courses:
                Enrollment.objects.create(
                    student=student,
                    course=course,
                    enrollment_date=student.enrollment_date,
                    grade=random.choice(['A', 'B', 'C', 'B+', 'A-']) if random.choice([True, False]) else None,
                    is_completed=random.choice([True, False])
                )
            
            students.append(student)
        
        return students