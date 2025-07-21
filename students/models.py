from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.utils import timezone
from moze.models import Moze


# Core academic models that views expect
class Student(models.Model):
    """Main student model - alias for StudentProfile for views compatibility"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student',
        limit_choices_to={'role': 'student'}
    )
    student_id = models.CharField(max_length=20, unique=True)
    academic_level = models.CharField(
        max_length=20,
        choices=[
            ('undergraduate', 'Undergraduate'),
            ('postgraduate', 'Postgraduate'),
            ('doctoral', 'Doctoral'),
            ('diploma', 'Diploma'),
        ],
        default='undergraduate'
    )
    enrollment_status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('suspended', 'Suspended'),
            ('graduated', 'Graduated'),
            ('withdrawn', 'Withdrawn'),
        ],
        default='active'
    )
    enrollment_date = models.DateField()
    expected_graduation = models.DateField(blank=True, null=True)
    
    class Meta:
        ordering = ['student_id']
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.student_id})"


class Course(models.Model):
    """Academic courses"""
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    credits = models.PositiveIntegerField(default=3)
    
    # Course details
    level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
        ],
        default='beginner'
    )
    prerequisites = models.ManyToManyField('self', blank=True, symmetrical=False)
    
    # Instructor and schedule
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role__in': ['doctor', 'badri_mahal_admin']},
        related_name='courses_taught'
    )
    
    # Course metadata
    is_active = models.BooleanField(default=True)
    max_students = models.PositiveIntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def enrollment_count(self):
        return self.enrollments.filter(status='enrolled').count()


class Enrollment(models.Model):
    """Student enrollment in courses"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('enrolled', 'Enrolled'),
            ('completed', 'Completed'),
            ('dropped', 'Dropped'),
            ('failed', 'Failed'),
        ],
        default='enrolled'
    )
    
    # Enrollment details
    enrolled_date = models.DateTimeField(auto_now_add=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    grade = models.CharField(max_length=5, blank=True)
    
    class Meta:
        unique_together = ['student', 'course']
        ordering = ['-enrolled_date']
    
    def __str__(self):
        return f"{self.student} enrolled in {self.course}"


class Assignment(models.Model):
    """Course assignments"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Assignment details
    assignment_type = models.CharField(
        max_length=20,
        choices=[
            ('homework', 'Homework'),
            ('project', 'Project'),
            ('quiz', 'Quiz'),
            ('exam', 'Exam'),
            ('presentation', 'Presentation'),
        ],
        default='homework'
    )
    
    # Timing
    assigned_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    max_points = models.PositiveIntegerField(default=100)
    
    # Settings
    is_published = models.BooleanField(default=False)
    allow_late_submission = models.BooleanField(default=True)
    late_penalty_percent = models.PositiveIntegerField(default=10)
    
    class Meta:
        ordering = ['-due_date']
    
    def __str__(self):
        return f"{self.course.code} - {self.title}"


class Submission(models.Model):
    """Student assignment submissions"""
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='submissions')
    
    # Submission content
    content = models.TextField(blank=True)
    file_upload = models.FileField(upload_to='submissions/', blank=True, null=True)
    
    # Submission metadata
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_late = models.BooleanField(default=False)
    attempt_number = models.PositiveIntegerField(default=1)
    
    # Grading
    is_graded = models.BooleanField(default=False)
    grade_percentage = models.FloatField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='graded_submissions'
    )
    graded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['assignment', 'student', 'attempt_number']
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.student} - {self.assignment.title}"
    
    def save(self, *args, **kwargs):
        # Check if submission is late
        if self.submitted_at and self.assignment.due_date:
            self.is_late = self.submitted_at > self.assignment.due_date
        super().save(*args, **kwargs)


class Grade(models.Model):
    """Student grades"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='grades')
    assignment = models.ForeignKey(
        Assignment, 
        on_delete=models.CASCADE, 
        related_name='grades',
        null=True,
        blank=True
    )
    
    # Grade details
    points = models.FloatField()
    max_points = models.FloatField()
    percentage = models.FloatField()
    letter_grade = models.CharField(max_length=3, blank=True)
    
    # Grading metadata
    graded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_graded = models.DateTimeField(auto_now_add=True)
    comments = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-date_graded']
    
    def __str__(self):
        return f"{self.student} - {self.course}: {self.percentage}%"
    
    def save(self, *args, **kwargs):
        # Calculate percentage
        if self.max_points > 0:
            self.percentage = (self.points / self.max_points) * 100
        
        # Assign letter grade
        if self.percentage >= 90:
            self.letter_grade = 'A'
        elif self.percentage >= 80:
            self.letter_grade = 'B'
        elif self.percentage >= 70:
            self.letter_grade = 'C'
        elif self.percentage >= 60:
            self.letter_grade = 'D'
        else:
            self.letter_grade = 'F'
        
        super().save(*args, **kwargs)


class Schedule(models.Model):
    """Class schedules"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='schedules')
    
    # Time details
    day_of_week = models.CharField(
        max_length=10,
        choices=[
            ('monday', 'Monday'),
            ('tuesday', 'Tuesday'),
            ('wednesday', 'Wednesday'),
            ('thursday', 'Thursday'),
            ('friday', 'Friday'),
            ('saturday', 'Saturday'),
            ('sunday', 'Sunday'),
        ]
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    # Location
    room = models.CharField(max_length=50, blank=True)
    building = models.CharField(max_length=100, blank=True)
    
    # Schedule metadata
    effective_from = models.DateField()
    effective_until = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.course} - {self.day_of_week} {self.start_time}"


class Attendance(models.Model):
    """Student attendance tracking"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='attendance_records')
    
    # Attendance details
    date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=[
            ('present', 'Present'),
            ('absent', 'Absent'),
            ('late', 'Late'),
            ('excused', 'Excused'),
        ],
        default='present'
    )
    
    # Additional info
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'course', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.student} - {self.course} - {self.date}: {self.status}"


class Announcement(models.Model):
    """Course and general announcements"""
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    # Scope
    course = models.ForeignKey(
        Course, 
        on_delete=models.CASCADE, 
        related_name='announcements',
        null=True,
        blank=True
    )
    is_global = models.BooleanField(default=False)  # Global to all students
    
    # Targeting
    target_level = models.CharField(
        max_length=20,
        choices=[
            ('all', 'All Students'),
            ('undergraduate', 'Undergraduate'),
            ('postgraduate', 'Postgraduate'),
            ('doctoral', 'Doctoral'),
        ],
        default='all'
    )
    
    # Announcement metadata
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)
    is_urgent = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class StudentGroup(models.Model):
    """Student groups and study circles"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Group details
    group_type = models.CharField(
        max_length=20,
        choices=[
            ('study_group', 'Study Group'),
            ('project_team', 'Project Team'),
            ('club', 'Student Club'),
            ('committee', 'Committee'),
        ],
        default='study_group'
    )
    
    # Members
    members = models.ManyToManyField(Student, through='GroupMembership')
    leader = models.ForeignKey(
        Student, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='led_groups'
    )
    
    # Group metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    max_members = models.PositiveIntegerField(default=10)
    
    def __str__(self):
        return self.name


class GroupMembership(models.Model):
    """Through model for StudentGroup membership"""
    group = models.ForeignKey(StudentGroup, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    
    role = models.CharField(
        max_length=20,
        choices=[
            ('member', 'Member'),
            ('leader', 'Leader'),
            ('co_leader', 'Co-Leader'),
        ],
        default='member'
    )
    
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['group', 'student']


class Event(models.Model):
    """Student events and activities"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Event details
    event_type = models.CharField(
        max_length=20,
        choices=[
            ('academic', 'Academic'),
            ('cultural', 'Cultural'),
            ('sports', 'Sports'),
            ('workshop', 'Workshop'),
            ('seminar', 'Seminar'),
            ('social', 'Social'),
        ],
        default='academic'
    )
    
    # Timing and location
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True)
    
    # Event management
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    max_participants = models.PositiveIntegerField(null=True, blank=True)
    registration_required = models.BooleanField(default=False)
    registration_deadline = models.DateTimeField(null=True, blank=True)
    
    # Status
    is_published = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return self.title


class LibraryRecord(models.Model):
    """Library book borrowing records"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='library_records')
    
    # Book details
    book_title = models.CharField(max_length=200)
    book_isbn = models.CharField(max_length=20, blank=True)
    author = models.CharField(max_length=200, blank=True)
    
    # Borrowing details
    borrowed_date = models.DateField()
    due_date = models.DateField()
    returned_date = models.DateField(null=True, blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('borrowed', 'Borrowed'),
            ('returned', 'Returned'),
            ('overdue', 'Overdue'),
            ('lost', 'Lost'),
        ],
        default='borrowed'
    )
    
    # Fines
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fine_paid = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-borrowed_date']
    
    def __str__(self):
        return f"{self.student} - {self.book_title}"


class Achievement(models.Model):
    """Student achievements and awards"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='achievements')
    
    # Achievement details
    title = models.CharField(max_length=200)
    description = models.TextField()
    achievement_type = models.CharField(
        max_length=20,
        choices=[
            ('academic', 'Academic Excellence'),
            ('research', 'Research'),
            ('sports', 'Sports'),
            ('cultural', 'Cultural'),
            ('leadership', 'Leadership'),
            ('community', 'Community Service'),
        ],
        default='academic'
    )
    
    # Achievement metadata
    date_awarded = models.DateField()
    awarded_by = models.CharField(max_length=200)
    certificate_file = models.FileField(upload_to='achievements/', blank=True, null=True)
    
    # Verification
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_awarded']
    
    def __str__(self):
        return f"{self.student} - {self.title}"


class Scholarship(models.Model):
    """Student scholarships and financial aid"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='scholarships')
    
    # Scholarship details
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Scholarship type
    scholarship_type = models.CharField(
        max_length=20,
        choices=[
            ('merit', 'Merit-based'),
            ('need', 'Need-based'),
            ('sports', 'Sports'),
            ('research', 'Research'),
            ('minority', 'Minority'),
        ],
        default='merit'
    )
    
    # Timing
    academic_year = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('applied', 'Applied'),
            ('approved', 'Approved'),
            ('disbursed', 'Disbursed'),
            ('rejected', 'Rejected'),
        ],
        default='applied'
    )
    
    # Management
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student} - {self.name}"


class Fee(models.Model):
    """Student fee structure"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fees')
    
    # Fee details
    fee_type = models.CharField(
        max_length=20,
        choices=[
            ('tuition', 'Tuition Fee'),
            ('library', 'Library Fee'),
            ('laboratory', 'Laboratory Fee'),
            ('examination', 'Examination Fee'),
            ('hostel', 'Hostel Fee'),
            ('transport', 'Transport Fee'),
            ('miscellaneous', 'Miscellaneous'),
        ],
        default='tuition'
    )
    
    # Amount details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    academic_year = models.CharField(max_length=20)
    semester = models.CharField(max_length=20, blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('paid', 'Paid'),
            ('overdue', 'Overdue'),
            ('waived', 'Waived'),
        ],
        default='pending'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-due_date']
    
    def __str__(self):
        return f"{self.student} - {self.fee_type}: ${self.amount}"


class Payment(models.Model):
    """Fee payment records"""
    fee = models.ForeignKey(Fee, on_delete=models.CASCADE, related_name='payments')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments')
    
    # Payment details
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(
        max_length=20,
        choices=[
            ('cash', 'Cash'),
            ('card', 'Credit/Debit Card'),
            ('transfer', 'Bank Transfer'),
            ('cheque', 'Cheque'),
            ('online', 'Online Payment'),
        ],
        default='cash'
    )
    
    # Payment metadata
    transaction_id = models.CharField(max_length=100, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Receipt
    receipt_number = models.CharField(max_length=50, unique=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"{self.student} - {self.receipt_number}: ${self.amount_paid}"


# Keep existing models for backward compatibility
class StudentProfile(models.Model):
    """Extended profile for students"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile',
        limit_choices_to={'role': 'student'}
    )
    its_id = models.CharField(
        max_length=8,
        unique=True,
        validators=[RegexValidator(
            regex=r'^\d{8}$',
            message='ITS ID must be exactly 8 digits'
        )]
    )
    
    # Academic information
    college = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    year_of_study = models.PositiveIntegerField(
        choices=[
            (1, 'First Year'),
            (2, 'Second Year'),
            (3, 'Third Year'),
            (4, 'Fourth Year'),
            (5, 'Fifth Year'),
            (6, 'Sixth Year'),
            (7, 'Postgraduate'),
        ],
        default=1
    )
    enrollment_date = models.DateField()
    expected_graduation = models.DateField(blank=True, null=True)
    current_semester = models.CharField(max_length=20, blank=True, null=True)
    
    # Personal information
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(
        max_length=10,
        choices=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other')
        ],
        blank=True
    )
    
    # Contact information
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    emergency_contact = models.CharField(max_length=15, blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    
    # Address
    current_address = models.TextField(blank=True, null=True)
    permanent_address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    
    # Academic performance
    current_cgpa = models.FloatField(
        blank=True, 
        null=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(4.0)]
    )
    total_credit_hours = models.PositiveIntegerField(default=0)
    
    # Additional information
    interests = models.TextField(blank=True, null=True, help_text='Academic and personal interests')
    career_goals = models.TextField(blank=True, null=True)
    languages_spoken = models.CharField(max_length=200, blank=True, null=True)
    
    # Medical information
    blood_group = models.CharField(
        max_length=5,
        choices=[
            ('A+', 'A+'), ('A-', 'A-'),
            ('B+', 'B+'), ('B-', 'B-'),
            ('AB+', 'AB+'), ('AB-', 'AB-'),
            ('O+', 'O+'), ('O-', 'O-'),
        ],
        blank=True, null=True
    )
    medical_conditions = models.TextField(blank=True, null=True)
    
    # Financial information
    scholarship_recipient = models.BooleanField(default=False)
    financial_aid_required = models.BooleanField(default=False)
    
    # Status flags
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Student Profile'
        verbose_name_plural = 'Student Profiles'
        ordering = ['its_id']
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.its_id})"
    
    def get_academic_year(self):
        """Calculate current academic year based on enrollment date"""
        from datetime import date
        years_enrolled = (date.today() - self.enrollment_date).days // 365
        return min(years_enrolled + 1, 7)  # Cap at 7 for postgraduate
    
    def get_completion_percentage(self):
        """Calculate completion percentage based on year of study"""
        if self.year_of_study == 7:  # Postgraduate
            return 100  # Variable for postgrad
        return (self.year_of_study / 6) * 100  # Assuming 6-year medical program


class MentorshipRequest(models.Model):
    """Student mentorship requests"""
    student = models.ForeignKey(
        StudentProfile, 
        on_delete=models.CASCADE,
        related_name='mentorship_requests'
    )
    
    # Request details
    mentorship_type = models.CharField(
        max_length=30,
        choices=[
            ('academic', 'Academic Guidance'),
            ('career', 'Career Counseling'),
            ('research', 'Research Mentorship'),
            ('personal', 'Personal Development'),
            ('professional', 'Professional Skills'),
            ('leadership', 'Leadership Development'),
        ],
        default='academic'
    )
    
    # Preferred mentor characteristics
    preferred_mentor_specialization = models.CharField(max_length=100, blank=True, null=True)
    preferred_mentor_gender = models.CharField(
        max_length=10,
        choices=[
            ('any', 'No Preference'),
            ('male', 'Male'),
            ('female', 'Female'),
        ],
        default='any'
    )
    
    # Request content
    description = models.TextField(help_text='Describe what kind of mentorship you are seeking')
    goals = models.TextField(help_text='What do you hope to achieve through this mentorship?')
    specific_areas = models.TextField(
        blank=True, 
        null=True,
        help_text='Specific areas where you need guidance'
    )
    
    # Availability
    preferred_meeting_frequency = models.CharField(
        max_length=20,
        choices=[
            ('weekly', 'Weekly'),
            ('biweekly', 'Bi-weekly'),
            ('monthly', 'Monthly'),
            ('as_needed', 'As Needed'),
        ],
        default='monthly'
    )
    
    preferred_meeting_format = models.CharField(
        max_length=20,
        choices=[
            ('in_person', 'In Person'),
            ('video_call', 'Video Call'),
            ('phone_call', 'Phone Call'),
            ('email', 'Email'),
            ('flexible', 'Flexible'),
        ],
        default='flexible'
    )
    
    # Request status
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved - Seeking Mentor'),
        ('matched', 'Matched with Mentor'),
        ('active', 'Active Mentorship'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Mentor assignment
    assigned_mentor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role__in': ['doctor', 'badri_mahal_admin']},
        related_name='mentored_students'
    )
    
    # Important dates
    requested_date = models.DateTimeField(auto_now_add=True)
    approved_date = models.DateTimeField(null=True, blank=True)
    matched_date = models.DateTimeField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    expected_end_date = models.DateField(null=True, blank=True)
    actual_end_date = models.DateField(null=True, blank=True)
    
    # Administrative fields
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_mentorship_requests'
    )
    admin_notes = models.TextField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    # Feedback and evaluation
    student_satisfaction_rating = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Student satisfaction rating (1-5)'
    )
    mentor_effectiveness_rating = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Mentor effectiveness rating (1-5)'
    )
    student_feedback = models.TextField(blank=True, null=True)
    mentor_feedback = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-requested_date']
        verbose_name = 'Mentorship Request'
        verbose_name_plural = 'Mentorship Requests'
    
    def __str__(self):
        return f"Mentorship Request - {self.student.user.get_full_name()} ({self.get_mentorship_type_display()})"
    
    def is_active(self):
        return self.status in ['approved', 'matched', 'active']
    
    def days_since_request(self):
        return (timezone.now().date() - self.requested_date.date()).days
    
    def get_duration_weeks(self):
        if self.start_date and self.actual_end_date:
            return (self.actual_end_date - self.start_date).days // 7
        return None


class AidRequest(models.Model):
    """Student financial aid requests"""
    student = models.ForeignKey(
        StudentProfile, 
        on_delete=models.CASCADE,
        related_name='aid_requests'
    )
    
    # Aid type
    AID_TYPE_CHOICES = [
        ('emergency', 'Emergency Financial Aid'),
        ('tuition', 'Tuition Assistance'),
        ('medical', 'Medical Expense Aid'),
        ('textbook', 'Textbook/Material Aid'),
        ('transportation', 'Transportation Aid'),
        ('housing', 'Housing/Accommodation Aid'),
        ('technology', 'Technology/Equipment Aid'),
        ('food', 'Food/Meal Aid'),
        ('examination', 'Examination Fee Aid'),
        ('research', 'Research Project Funding'),
        ('conference', 'Conference/Travel Aid'),
        ('other', 'Other Financial Need'),
    ]
    aid_type = models.CharField(max_length=30, choices=AID_TYPE_CHOICES)
    
    # Request details
    amount_requested = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text='Amount requested in USD'
    )
    
    urgency_level = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low - Can wait 2-4 weeks'),
            ('medium', 'Medium - Needed within 2 weeks'),
            ('high', 'High - Needed within 1 week'),
            ('emergency', 'Emergency - Needed immediately'),
        ],
        default='medium'
    )
    
    # Detailed explanation
    reason_for_request = models.TextField(
        help_text='Detailed explanation of why this aid is needed'
    )
    circumstances = models.TextField(
        help_text='Describe the circumstances that led to this financial need'
    )
    attempted_solutions = models.TextField(
        blank=True,
        null=True,
        help_text='What steps have you already taken to address this need?'
    )
    
    # Financial information
    family_income_bracket = models.CharField(
        max_length=20,
        choices=[
            ('under_10k', 'Under $10,000'),
            ('10k_25k', '$10,000 - $25,000'),
            ('25k_50k', '$25,000 - $50,000'),
            ('50k_75k', '$50,000 - $75,000'),
            ('75k_100k', '$75,000 - $100,000'),
            ('over_100k', 'Over $100,000'),
            ('prefer_not_say', 'Prefer not to say'),
        ],
        default='prefer_not_say'
    )
    
    has_other_aid = models.BooleanField(
        default=False,
        help_text='Are you receiving aid from other sources?'
    )
    other_aid_details = models.TextField(blank=True, null=True)
    
    # Supporting documentation
    supporting_documents = models.FileField(
        upload_to='aid_requests/',
        blank=True,
        null=True,
        help_text='Upload any supporting documents (receipts, bills, etc.)'
    )
    
    # Request processing
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('additional_info_needed', 'Additional Information Needed'),
        ('approved', 'Approved'),
        ('partially_approved', 'Partially Approved'),
        ('rejected', 'Rejected'),
        ('disbursed', 'Aid Disbursed'),
        ('closed', 'Case Closed'),
    ]
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='submitted')
    
    # Approval details
    approved_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_aid_requests'
    )
    approval_date = models.DateTimeField(null=True, blank=True)
    approval_conditions = models.TextField(blank=True, null=True)
    
    # Disbursement
    disbursement_method = models.CharField(
        max_length=20,
        choices=[
            ('bank_transfer', 'Bank Transfer'),
            ('check', 'Check'),
            ('cash', 'Cash'),
            ('direct_payment', 'Direct Payment to Vendor'),
            ('account_credit', 'Account Credit'),
        ],
        blank=True,
        null=True
    )
    disbursed_date = models.DateTimeField(null=True, blank=True)
    disbursed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='disbursed_aid_requests'
    )
    
    # Administrative notes
    reviewer_notes = models.TextField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    
    # Timestamps
    submitted_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    # Confidentiality
    is_confidential = models.BooleanField(
        default=True,
        help_text='Keep this request confidential from other students'
    )
    
    class Meta:
        ordering = ['-submitted_date']
        verbose_name = 'Financial Aid Request'
        verbose_name_plural = 'Financial Aid Requests'
    
    def __str__(self):
        return f"Aid Request - {self.student.user.get_full_name()} - {self.get_aid_type_display()} (${self.amount_requested})"
    
    def is_emergency(self):
        return self.urgency_level == 'emergency'
    
    def days_since_submission(self):
        return (timezone.now().date() - self.submitted_date.date()).days
    
    def is_overdue_review(self):
        """Check if request is overdue for review based on urgency"""
        days_since = self.days_since_submission()
        if self.urgency_level == 'emergency' and days_since > 1:
            return True
        elif self.urgency_level == 'high' and days_since > 7:
            return True
        elif self.urgency_level == 'medium' and days_since > 14:
            return True
        elif self.urgency_level == 'low' and days_since > 28:
            return True
        return False
    
    def get_approval_percentage(self):
        """Calculate what percentage of requested amount was approved"""
        if self.approved_amount and self.amount_requested:
            return (self.approved_amount / self.amount_requested) * 100
        return 0


class StudentMeeting(models.Model):
    """Student meetings and consultations"""
    student = models.ForeignKey(
        StudentProfile, 
        on_delete=models.CASCADE,
        related_name='meetings'
    )
    
    # Meeting participants
    facilitator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='facilitated_meetings',
        limit_choices_to={'role__in': ['doctor', 'badri_mahal_admin', 'aamil']}
    )
    
    # Meeting details
    MEETING_TYPE_CHOICES = [
        ('academic_advising', 'Academic Advising'),
        ('career_counseling', 'Career Counseling'),
        ('personal_counseling', 'Personal Counseling'),
        ('disciplinary', 'Disciplinary Meeting'),
        ('financial_consultation', 'Financial Consultation'),
        ('health_consultation', 'Health Consultation'),
        ('mentorship', 'Mentorship Session'),
        ('progress_review', 'Progress Review'),
        ('goal_setting', 'Goal Setting'),
        ('conflict_resolution', 'Conflict Resolution'),
        ('emergency_consultation', 'Emergency Consultation'),
        ('routine_checkin', 'Routine Check-in'),
    ]
    meeting_type = models.CharField(max_length=30, choices=MEETING_TYPE_CHOICES)
    
    # Scheduling
    scheduled_date = models.DateTimeField()
    estimated_duration_minutes = models.PositiveIntegerField(default=30)
    location = models.CharField(max_length=200, blank=True, null=True)
    meeting_format = models.CharField(
        max_length=20,
        choices=[
            ('in_person', 'In Person'),
            ('video_call', 'Video Call'),
            ('phone_call', 'Phone Call'),
        ],
        default='in_person'
    )
    
    # Meeting content
    agenda = models.TextField(
        help_text='Topics to be discussed in the meeting'
    )
    student_concerns = models.TextField(
        blank=True,
        null=True,
        help_text='Specific concerns raised by the student'
    )
    
    # Meeting outcomes
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'Student No-Show'),
        ('rescheduled', 'Rescheduled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # Post-meeting documentation
    actual_duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    summary = models.TextField(blank=True, null=True)
    action_items = models.TextField(blank=True, null=True)
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    
    # Outcome tracking
    outcome_rating = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Facilitator rating of meeting outcome (1-5)'
    )
    student_satisfaction = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Student satisfaction rating (1-5)'
    )
    
    # Confidentiality and privacy
    is_confidential = models.BooleanField(default=True)
    confidentiality_notes = models.TextField(
        blank=True,
        null=True,
        help_text='Special confidentiality considerations'
    )
    
    # Administrative
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='scheduled_meetings'
    )
    created_date = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    
    # Cancellation/rescheduling
    cancellation_reason = models.TextField(blank=True, null=True)
    rescheduled_from = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rescheduled_to'
    )
    
    class Meta:
        ordering = ['-scheduled_date']
        verbose_name = 'Student Meeting'
        verbose_name_plural = 'Student Meetings'
    
    def __str__(self):
        return f"{self.get_meeting_type_display()} - {self.student.user.get_full_name()} - {self.scheduled_date.strftime('%Y-%m-%d %H:%M')}"
    
    def is_upcoming(self):
        return self.scheduled_date > timezone.now() and self.status in ['scheduled', 'confirmed']
    
    def is_overdue(self):
        return self.scheduled_date < timezone.now() and self.status in ['scheduled', 'confirmed']
    
    def duration_hours(self):
        if self.actual_duration_minutes:
            return self.actual_duration_minutes / 60
        return self.estimated_duration_minutes / 60


class StudentAchievement(models.Model):
    """Track student achievements and milestones"""
    student = models.ForeignKey(
        StudentProfile, 
        on_delete=models.CASCADE,
        related_name='tracked_achievements'
    )
    
    # Achievement categories
    ACHIEVEMENT_TYPE_CHOICES = [
        ('academic_excellence', 'Academic Excellence'),
        ('research_publication', 'Research Publication'),
        ('conference_presentation', 'Conference Presentation'),
        ('competition_winner', 'Competition Winner'),
        ('leadership_role', 'Leadership Role'),
        ('community_service', 'Community Service'),
        ('volunteer_work', 'Volunteer Work'),
        ('internship_completion', 'Internship Completion'),
        ('certification_earned', 'Professional Certification'),
        ('skill_development', 'Skill Development'),
        ('mentorship_success', 'Successful Mentorship'),
        ('extracurricular_excellence', 'Extracurricular Excellence'),
        ('innovation_project', 'Innovation Project'),
        ('cultural_contribution', 'Cultural Contribution'),
        ('sports_achievement', 'Sports Achievement'),
        ('milestone_completion', 'Academic Milestone'),
    ]
    achievement_type = models.CharField(max_length=30, choices=ACHIEVEMENT_TYPE_CHOICES)
    
    # Achievement details
    title = models.CharField(max_length=200)
    description = models.TextField()
    achievement_date = models.DateField()
    
    # Context and significance
    category = models.CharField(
        max_length=20,
        choices=[
            ('academic', 'Academic'),
            ('research', 'Research'),
            ('leadership', 'Leadership'),
            ('service', 'Community Service'),
            ('personal', 'Personal Development'),
            ('professional', 'Professional'),
            ('creative', 'Creative/Artistic'),
            ('athletic', 'Athletic'),
        ],
        default='academic'
    )
    
    significance_level = models.CharField(
        max_length=20,
        choices=[
            ('local', 'Local/Institutional'),
            ('regional', 'Regional'),
            ('national', 'National'),
            ('international', 'International'),
        ],
        default='local'
    )
    
    # Recognition and verification
    recognizing_organization = models.CharField(
        max_length=200,
        help_text='Organization or entity that recognized this achievement'
    )
    
    # Documentation
    certificate_file = models.FileField(
        upload_to='student_achievements/',
        blank=True,
        null=True,
        help_text='Upload certificate or documentation'
    )
    supporting_documents = models.FileField(
        upload_to='student_achievements/supporting/',
        blank=True,
        null=True,
        help_text='Additional supporting documents'
    )
    
    # Verification
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_student_achievements'
    )
    verification_date = models.DateTimeField(null=True, blank=True)
    verification_notes = models.TextField(blank=True, null=True)
    
    # Impact and outcomes
    skills_developed = models.TextField(
        blank=True,
        null=True,
        help_text='What skills were developed through this achievement?'
    )
    impact_description = models.TextField(
        blank=True,
        null=True,
        help_text='What impact did this achievement have?'
    )
    
    # Recognition within system
    featured_achievement = models.BooleanField(
        default=False,
        help_text='Feature this achievement in student highlights'
    )
    public_visibility = models.BooleanField(
        default=True,
        help_text='Make this achievement visible to other students'
    )
    
    # Metadata
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recorded_achievements'
    )
    recorded_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    # Tags and search
    tags = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text='Comma-separated tags for searching and categorization'
    )
    
    class Meta:
        ordering = ['-achievement_date', '-recorded_date']
        verbose_name = 'Student Achievement'
        verbose_name_plural = 'Student Achievements'
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.title} ({self.achievement_date.year})"
    
    def get_tags_list(self):
        """Return tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []
    
    def days_since_achievement(self):
        return (timezone.now().date() - self.achievement_date).days
    
    def is_recent(self, days=30):
        return self.days_since_achievement() <= days
