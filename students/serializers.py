"""
Serializers for the Students app
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from .models import (
    Student, Course, Enrollment, Assignment, Submission, Grade, Schedule,
    Attendance, Announcement, StudentGroup, GroupMembership, Event,
    LibraryRecord, Achievement, Scholarship, Fee, Payment, StudentProfile,
    MentorshipRequest, AidRequest, StudentMeeting, StudentAchievement
)
from moze.models import Moze

User = get_user_model()


# Basic User serializer for nested relationships
class UserBasicSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'full_name', 'role']
        read_only_fields = fields
    
    def get_full_name(self, obj):
        return obj.get_full_name()


# Basic Moze serializer for nested relationships
class MozeBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Moze
        fields = ['id', 'name', 'location']
        read_only_fields = fields


# Core Academic Models Serializers
class StudentSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='student'), write_only=True, source='user'
    )
    academic_level_display = serializers.SerializerMethodField()
    enrollment_status_display = serializers.SerializerMethodField()
    days_enrolled = serializers.SerializerMethodField()
    years_enrolled = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = [
            'id', 'user', 'user_id', 'student_id', 'academic_level', 
            'academic_level_display', 'enrollment_status', 'enrollment_status_display',
            'enrollment_date', 'expected_graduation', 'days_enrolled', 'years_enrolled'
        ]
        read_only_fields = ['days_enrolled', 'years_enrolled']
    
    def get_academic_level_display(self, obj):
        return obj.get_academic_level_display()
    
    def get_enrollment_status_display(self, obj):
        return obj.get_enrollment_status_display()
    
    def get_days_enrolled(self, obj):
        return (timezone.now().date() - obj.enrollment_date).days
    
    def get_years_enrolled(self, obj):
        return self.get_days_enrolled(obj) // 365


class CourseSerializer(serializers.ModelSerializer):
    instructor = UserBasicSerializer(read_only=True)
    instructor_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role__in=['doctor', 'badri_mahal_admin']),
        write_only=True, source='instructor', required=False, allow_null=True
    )
    prerequisites = serializers.StringRelatedField(many=True, read_only=True)
    prerequisite_ids = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), many=True, write_only=True, 
        source='prerequisites', required=False
    )
    level_display = serializers.SerializerMethodField()
    enrollment_count = serializers.ReadOnlyField()
    enrollment_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'code', 'name', 'description', 'credits', 'level', 'level_display',
            'prerequisites', 'prerequisite_ids', 'instructor', 'instructor_id',
            'is_active', 'max_students', 'enrollment_count', 'enrollment_percentage',
            'created_at'
        ]
        read_only_fields = ['created_at', 'enrollment_count']
    
    def get_level_display(self, obj):
        return obj.get_level_display()
    
    def get_enrollment_percentage(self, obj):
        if obj.max_students > 0:
            return round((obj.enrollment_count / obj.max_students) * 100, 2)
        return 0


class EnrollmentSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), write_only=True, source='student'
    )
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), write_only=True, source='course'
    )
    status_display = serializers.SerializerMethodField()
    days_enrolled = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'student', 'student_id', 'course', 'course_id', 'status',
            'status_display', 'enrolled_date', 'completion_date', 'grade',
            'days_enrolled', 'is_active'
        ]
        read_only_fields = ['enrolled_date']
    
    def get_status_display(self, obj):
        return obj.get_status_display()
    
    def get_days_enrolled(self, obj):
        end_date = obj.completion_date or timezone.now()
        return (end_date.date() - obj.enrolled_date.date()).days
    
    def get_is_active(self, obj):
        return obj.status == 'enrolled'


class AssignmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), write_only=True, source='course'
    )
    assignment_type_display = serializers.SerializerMethodField()
    days_until_due = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    submission_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Assignment
        fields = [
            'id', 'course', 'course_id', 'title', 'description', 'assignment_type',
            'assignment_type_display', 'assigned_date', 'due_date', 'max_points',
            'is_published', 'allow_late_submission', 'late_penalty_percent',
            'days_until_due', 'is_overdue', 'submission_count'
        ]
        read_only_fields = ['assigned_date']
    
    def get_assignment_type_display(self, obj):
        return obj.get_assignment_type_display()
    
    def get_days_until_due(self, obj):
        return (obj.due_date.date() - timezone.now().date()).days
    
    def get_is_overdue(self, obj):
        return timezone.now() > obj.due_date
    
    def get_submission_count(self, obj):
        return obj.submissions.count()


class SubmissionSerializer(serializers.ModelSerializer):
    assignment = AssignmentSerializer(read_only=True)
    assignment_id = serializers.PrimaryKeyRelatedField(
        queryset=Assignment.objects.all(), write_only=True, source='assignment'
    )
    student = StudentSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), write_only=True, source='student', required=False
    )
    graded_by = UserBasicSerializer(read_only=True)
    days_since_submission = serializers.SerializerMethodField()
    grade_letter = serializers.SerializerMethodField()
    
    class Meta:
        model = Submission
        fields = [
            'id', 'assignment', 'assignment_id', 'student', 'student_id',
            'content', 'file_upload', 'submitted_at', 'is_late', 'attempt_number',
            'is_graded', 'grade_percentage', 'grade_letter', 'feedback',
            'graded_by', 'graded_at', 'days_since_submission'
        ]
        read_only_fields = ['submitted_at', 'graded_at']
    
    def get_days_since_submission(self, obj):
        return (timezone.now().date() - obj.submitted_at.date()).days
    
    def get_grade_letter(self, obj):
        if obj.grade_percentage is not None:
            if obj.grade_percentage >= 90:
                return 'A'
            elif obj.grade_percentage >= 80:
                return 'B'
            elif obj.grade_percentage >= 70:
                return 'C'
            elif obj.grade_percentage >= 60:
                return 'D'
            else:
                return 'F'
        return None


class GradeSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), write_only=True, source='student'
    )
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), write_only=True, source='course'
    )
    assignment = AssignmentSerializer(read_only=True)
    assignment_id = serializers.PrimaryKeyRelatedField(
        queryset=Assignment.objects.all(), write_only=True, source='assignment',
        required=False, allow_null=True
    )
    graded_by = UserBasicSerializer(read_only=True)
    graded_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='graded_by'
    )
    
    class Meta:
        model = Grade
        fields = [
            'id', 'student', 'student_id', 'course', 'course_id', 'assignment',
            'assignment_id', 'points', 'max_points', 'percentage', 'letter_grade',
            'graded_by', 'graded_by_id', 'date_graded', 'comments'
        ]
        read_only_fields = ['date_graded', 'percentage', 'letter_grade']


class ScheduleSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), write_only=True, source='course'
    )
    day_of_week_display = serializers.SerializerMethodField()
    duration_minutes = serializers.SerializerMethodField()
    is_current = serializers.SerializerMethodField()
    
    class Meta:
        model = Schedule
        fields = [
            'id', 'course', 'course_id', 'day_of_week', 'day_of_week_display',
            'start_time', 'end_time', 'duration_minutes', 'room', 'building',
            'effective_from', 'effective_until', 'is_active', 'is_current'
        ]
    
    def get_day_of_week_display(self, obj):
        return obj.get_day_of_week_display()
    
    def get_duration_minutes(self, obj):
        from datetime import datetime, timedelta
        start = datetime.combine(timezone.now().date(), obj.start_time)
        end = datetime.combine(timezone.now().date(), obj.end_time)
        return int((end - start).total_seconds() / 60)
    
    def get_is_current(self, obj):
        today = timezone.now().date()
        return (obj.effective_from <= today and 
                (obj.effective_until is None or obj.effective_until >= today))


class AttendanceSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), write_only=True, source='student'
    )
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), write_only=True, source='course'
    )
    recorded_by = UserBasicSerializer(read_only=True)
    recorded_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='recorded_by'
    )
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'student', 'student_id', 'course', 'course_id', 'date',
            'status', 'status_display', 'notes', 'recorded_by', 'recorded_by_id',
            'recorded_at'
        ]
        read_only_fields = ['recorded_at']
    
    def get_status_display(self, obj):
        return obj.get_status_display()


class AnnouncementSerializer(serializers.ModelSerializer):
    author = UserBasicSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='author',
        required=False, allow_null=True  # Allow view to set this
    )
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), write_only=True, source='course',
        required=False, allow_null=True
    )
    target_level_display = serializers.SerializerMethodField()
    days_since_created = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = Announcement
        fields = [
            'id', 'title', 'content', 'course', 'course_id', 'is_global',
            'target_level', 'target_level_display', 'author', 'author_id',
            'created_at', 'is_published', 'is_urgent', 'expires_at',
            'days_since_created', 'is_expired'
        ]
        read_only_fields = ['created_at']
    
    def get_target_level_display(self, obj):
        return obj.get_target_level_display()
    
    def get_days_since_created(self, obj):
        return (timezone.now().date() - obj.created_at.date()).days
    
    def get_is_expired(self, obj):
        if obj.expires_at:
            return timezone.now() > obj.expires_at
        return False


# Student Groups and Activities
class GroupMembershipSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    role_display = serializers.SerializerMethodField()
    
    class Meta:
        model = GroupMembership
        fields = ['id', 'student', 'role', 'role_display', 'joined_at', 'is_active']
    
    def get_role_display(self, obj):
        return obj.get_role_display()


class StudentGroupSerializer(serializers.ModelSerializer):
    leader = StudentSerializer(read_only=True)
    leader_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), write_only=True, source='leader',
        required=False, allow_null=True
    )
    created_by = UserBasicSerializer(read_only=True)
    created_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='created_by'
    )
    members = GroupMembershipSerializer(many=True, read_only=True, source='groupmembership_set')
    group_type_display = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()
    is_full = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentGroup
        fields = [
            'id', 'name', 'description', 'group_type', 'group_type_display',
            'leader', 'leader_id', 'created_by', 'created_by_id', 'created_at',
            'is_active', 'max_members', 'member_count', 'is_full', 'members'
        ]
        read_only_fields = ['created_at']
    
    def get_group_type_display(self, obj):
        return obj.get_group_type_display()
    
    def get_member_count(self, obj):
        return obj.groupmembership_set.filter(is_active=True).count()
    
    def get_is_full(self, obj):
        return self.get_member_count(obj) >= obj.max_members


class EventSerializer(serializers.ModelSerializer):
    organizer = UserBasicSerializer(read_only=True)
    organizer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='organizer'
    )
    event_type_display = serializers.SerializerMethodField()
    duration_hours = serializers.SerializerMethodField()
    is_upcoming = serializers.SerializerMethodField()
    is_ongoing = serializers.SerializerMethodField()
    days_until_event = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'event_type', 'event_type_display',
            'start_date', 'end_date', 'duration_hours', 'location', 'organizer',
            'organizer_id', 'max_participants', 'registration_required',
            'registration_deadline', 'is_published', 'is_cancelled',
            'is_upcoming', 'is_ongoing', 'days_until_event', 'created_at'
        ]
        read_only_fields = ['created_at']
    
    def get_event_type_display(self, obj):
        return obj.get_event_type_display()
    
    def get_duration_hours(self, obj):
        return (obj.end_date - obj.start_date).total_seconds() / 3600
    
    def get_is_upcoming(self, obj):
        return obj.start_date > timezone.now()
    
    def get_is_ongoing(self, obj):
        now = timezone.now()
        return obj.start_date <= now <= obj.end_date
    
    def get_days_until_event(self, obj):
        if self.get_is_upcoming(obj):
            return (obj.start_date.date() - timezone.now().date()).days
        return None


# Academic Support Services
class LibraryRecordSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), write_only=True, source='student'
    )
    status_display = serializers.SerializerMethodField()
    days_borrowed = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = LibraryRecord
        fields = [
            'id', 'student', 'student_id', 'book_title', 'book_isbn', 'author',
            'borrowed_date', 'due_date', 'returned_date', 'status', 'status_display',
            'fine_amount', 'fine_paid', 'days_borrowed', 'is_overdue'
        ]
    
    def get_status_display(self, obj):
        return obj.get_status_display()
    
    def get_days_borrowed(self, obj):
        end_date = obj.returned_date or timezone.now().date()
        return (end_date - obj.borrowed_date).days
    
    def get_is_overdue(self, obj):
        if obj.status == 'returned':
            return False
        return timezone.now().date() > obj.due_date


class AchievementSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), write_only=True, source='student'
    )
    verified_by = UserBasicSerializer(read_only=True)
    achievement_type_display = serializers.SerializerMethodField()
    days_since_achievement = serializers.SerializerMethodField()
    
    class Meta:
        model = Achievement
        fields = [
            'id', 'student', 'student_id', 'title', 'description', 'achievement_type',
            'achievement_type_display', 'date_awarded', 'awarded_by', 'certificate_file',
            'is_verified', 'verified_by', 'days_since_achievement', 'created_at'
        ]
        read_only_fields = ['created_at']
    
    def get_achievement_type_display(self, obj):
        return obj.get_achievement_type_display()
    
    def get_days_since_achievement(self, obj):
        return (timezone.now().date() - obj.date_awarded).days


class ScholarshipSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), write_only=True, source='student'
    )
    approved_by = UserBasicSerializer(read_only=True)
    scholarship_type_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    amount_formatted = serializers.SerializerMethodField()
    duration_days = serializers.SerializerMethodField()
    
    class Meta:
        model = Scholarship
        fields = [
            'id', 'student', 'student_id', 'name', 'description', 'amount',
            'amount_formatted', 'scholarship_type', 'scholarship_type_display',
            'academic_year', 'start_date', 'end_date', 'duration_days',
            'status', 'status_display', 'approved_by', 'created_at'
        ]
        read_only_fields = ['created_at']
    
    def get_scholarship_type_display(self, obj):
        return obj.get_scholarship_type_display()
    
    def get_status_display(self, obj):
        return obj.get_status_display()
    
    def get_amount_formatted(self, obj):
        return f"${obj.amount:.2f}"
    
    def get_duration_days(self, obj):
        return (obj.end_date - obj.start_date).days


# Financial Management
class FeeSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), write_only=True, source='student'
    )
    fee_type_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    amount_formatted = serializers.SerializerMethodField()
    days_until_due = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = Fee
        fields = [
            'id', 'student', 'student_id', 'fee_type', 'fee_type_display',
            'amount', 'amount_formatted', 'due_date', 'academic_year', 'semester',
            'status', 'status_display', 'days_until_due', 'is_overdue', 'created_at'
        ]
        read_only_fields = ['created_at']
    
    def get_fee_type_display(self, obj):
        return obj.get_fee_type_display()
    
    def get_status_display(self, obj):
        return obj.get_status_display()
    
    def get_amount_formatted(self, obj):
        return f"${obj.amount:.2f}"
    
    def get_days_until_due(self, obj):
        return (obj.due_date - timezone.now().date()).days
    
    def get_is_overdue(self, obj):
        return timezone.now().date() > obj.due_date and obj.status != 'paid'


class PaymentSerializer(serializers.ModelSerializer):
    fee = FeeSerializer(read_only=True)
    fee_id = serializers.PrimaryKeyRelatedField(
        queryset=Fee.objects.all(), write_only=True, source='fee'
    )
    student = StudentSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), write_only=True, source='student'
    )
    received_by = UserBasicSerializer(read_only=True)
    received_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='received_by'
    )
    payment_method_display = serializers.SerializerMethodField()
    amount_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = [
            'id', 'fee', 'fee_id', 'student', 'student_id', 'amount_paid',
            'amount_formatted', 'payment_method', 'payment_method_display',
            'transaction_id', 'payment_date', 'received_by', 'received_by_id',
            'receipt_number', 'notes'
        ]
        read_only_fields = ['payment_date']
    
    def get_payment_method_display(self, obj):
        return obj.get_payment_method_display()
    
    def get_amount_formatted(self, obj):
        return f"${obj.amount_paid:.2f}"


# Extended Student Profile Models
class StudentProfileSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='student'), write_only=True, source='user'
    )
    gender_display = serializers.SerializerMethodField()
    blood_group_display = serializers.SerializerMethodField()
    year_of_study_display = serializers.SerializerMethodField()
    academic_year = serializers.SerializerMethodField()
    completion_percentage = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentProfile
        fields = [
            'id', 'user', 'user_id', 'its_id', 'college', 'specialization',
            'year_of_study', 'year_of_study_display', 'enrollment_date',
            'expected_graduation', 'current_semester', 'date_of_birth', 'age',
            'gender', 'gender_display', 'phone_number', 'emergency_contact',
            'emergency_contact_name', 'current_address', 'permanent_address',
            'city', 'country', 'current_cgpa', 'total_credit_hours',
            'interests', 'career_goals', 'languages_spoken', 'blood_group',
            'blood_group_display', 'medical_conditions', 'scholarship_recipient',
            'financial_aid_required', 'is_active', 'is_verified',
            'academic_year', 'completion_percentage', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_gender_display(self, obj):
        return obj.get_gender_display() if obj.gender else None
    
    def get_blood_group_display(self, obj):
        return obj.get_blood_group_display() if obj.blood_group else None
    
    def get_year_of_study_display(self, obj):
        return obj.get_year_of_study_display()
    
    def get_academic_year(self, obj):
        return obj.get_academic_year()
    
    def get_completion_percentage(self, obj):
        return obj.get_completion_percentage()
    
    def get_age(self, obj):
        if obj.date_of_birth:
            today = timezone.now().date()
            return today.year - obj.date_of_birth.year - (
                (today.month, today.day) < (obj.date_of_birth.month, obj.date_of_birth.day)
            )
        return None


class MentorshipRequestSerializer(serializers.ModelSerializer):
    student = StudentProfileSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=StudentProfile.objects.all(), write_only=True, source='student'
    )
    assigned_mentor = UserBasicSerializer(read_only=True)
    reviewed_by = UserBasicSerializer(read_only=True)
    mentorship_type_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    preferred_mentor_gender_display = serializers.SerializerMethodField()
    preferred_meeting_frequency_display = serializers.SerializerMethodField()
    preferred_meeting_format_display = serializers.SerializerMethodField()
    days_since_request = serializers.SerializerMethodField()
    duration_weeks = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    
    class Meta:
        model = MentorshipRequest
        fields = [
            'id', 'student', 'student_id', 'mentorship_type', 'mentorship_type_display',
            'preferred_mentor_specialization', 'preferred_mentor_gender',
            'preferred_mentor_gender_display', 'description', 'goals', 'specific_areas',
            'preferred_meeting_frequency', 'preferred_meeting_frequency_display',
            'preferred_meeting_format', 'preferred_meeting_format_display',
            'status', 'status_display', 'assigned_mentor', 'requested_date',
            'approved_date', 'matched_date', 'start_date', 'expected_end_date',
            'actual_end_date', 'reviewed_by', 'admin_notes', 'rejection_reason',
            'student_satisfaction_rating', 'mentor_effectiveness_rating',
            'student_feedback', 'mentor_feedback', 'days_since_request',
            'duration_weeks', 'is_active'
        ]
        read_only_fields = ['requested_date']
    
    def get_mentorship_type_display(self, obj):
        return obj.get_mentorship_type_display()
    
    def get_status_display(self, obj):
        return obj.get_status_display()
    
    def get_preferred_mentor_gender_display(self, obj):
        return obj.get_preferred_mentor_gender_display()
    
    def get_preferred_meeting_frequency_display(self, obj):
        return obj.get_preferred_meeting_frequency_display()
    
    def get_preferred_meeting_format_display(self, obj):
        return obj.get_preferred_meeting_format_display()
    
    def get_days_since_request(self, obj):
        return obj.days_since_request()
    
    def get_duration_weeks(self, obj):
        return obj.get_duration_weeks()
    
    def get_is_active(self, obj):
        return obj.is_active()


class AidRequestSerializer(serializers.ModelSerializer):
    student = StudentProfileSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=StudentProfile.objects.all(), write_only=True, source='student'
    )
    approved_by = UserBasicSerializer(read_only=True)
    disbursed_by = UserBasicSerializer(read_only=True)
    aid_type_display = serializers.SerializerMethodField()
    urgency_level_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    family_income_bracket_display = serializers.SerializerMethodField()
    disbursement_method_display = serializers.SerializerMethodField()
    amount_requested_formatted = serializers.SerializerMethodField()
    approved_amount_formatted = serializers.SerializerMethodField()
    days_since_submission = serializers.SerializerMethodField()
    approval_percentage = serializers.SerializerMethodField()
    is_emergency = serializers.SerializerMethodField()
    is_overdue_review = serializers.SerializerMethodField()
    
    class Meta:
        model = AidRequest
        fields = [
            'id', 'student', 'student_id', 'aid_type', 'aid_type_display',
            'amount_requested', 'amount_requested_formatted', 'urgency_level',
            'urgency_level_display', 'reason_for_request', 'circumstances',
            'attempted_solutions', 'family_income_bracket', 'family_income_bracket_display',
            'has_other_aid', 'other_aid_details', 'supporting_documents',
            'status', 'status_display', 'approved_amount', 'approved_amount_formatted',
            'approved_by', 'approval_date', 'approval_conditions', 'disbursement_method',
            'disbursement_method_display', 'disbursed_date', 'disbursed_by',
            'reviewer_notes', 'rejection_reason', 'follow_up_required',
            'follow_up_date', 'submitted_date', 'last_updated', 'is_confidential',
            'days_since_submission', 'approval_percentage', 'is_emergency',
            'is_overdue_review'
        ]
        read_only_fields = ['submitted_date', 'last_updated']
    
    def get_aid_type_display(self, obj):
        return obj.get_aid_type_display()
    
    def get_urgency_level_display(self, obj):
        return obj.get_urgency_level_display()
    
    def get_status_display(self, obj):
        return obj.get_status_display()
    
    def get_family_income_bracket_display(self, obj):
        return obj.get_family_income_bracket_display()
    
    def get_disbursement_method_display(self, obj):
        return obj.get_disbursement_method_display() if obj.disbursement_method else None
    
    def get_amount_requested_formatted(self, obj):
        return f"${obj.amount_requested:.2f}"
    
    def get_approved_amount_formatted(self, obj):
        return f"${obj.approved_amount:.2f}" if obj.approved_amount else None
    
    def get_days_since_submission(self, obj):
        return obj.days_since_submission()
    
    def get_approval_percentage(self, obj):
        return obj.get_approval_percentage()
    
    def get_is_emergency(self, obj):
        return obj.is_emergency()
    
    def get_is_overdue_review(self, obj):
        return obj.is_overdue_review()


class StudentMeetingSerializer(serializers.ModelSerializer):
    student = StudentProfileSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=StudentProfile.objects.all(), write_only=True, source='student'
    )
    facilitator = UserBasicSerializer(read_only=True)
    facilitator_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role__in=['doctor', 'badri_mahal_admin', 'aamil']),
        write_only=True, source='facilitator'
    )
    created_by = UserBasicSerializer(read_only=True)
    rescheduled_from = serializers.StringRelatedField(read_only=True)
    meeting_type_display = serializers.SerializerMethodField()
    meeting_format_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    duration_hours = serializers.SerializerMethodField()
    is_upcoming = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentMeeting
        fields = [
            'id', 'student', 'student_id', 'facilitator', 'facilitator_id',
            'meeting_type', 'meeting_type_display', 'scheduled_date',
            'estimated_duration_minutes', 'location', 'meeting_format',
            'meeting_format_display', 'agenda', 'student_concerns', 'status',
            'status_display', 'actual_duration_minutes', 'summary', 'action_items',
            'follow_up_required', 'follow_up_date', 'outcome_rating',
            'student_satisfaction', 'is_confidential', 'confidentiality_notes',
            'created_by', 'created_date', 'last_modified', 'cancellation_reason',
            'rescheduled_from', 'duration_hours', 'is_upcoming', 'is_overdue'
        ]
        read_only_fields = ['created_date', 'last_modified']
    
    def get_meeting_type_display(self, obj):
        return obj.get_meeting_type_display()
    
    def get_meeting_format_display(self, obj):
        return obj.get_meeting_format_display()
    
    def get_status_display(self, obj):
        return obj.get_status_display()
    
    def get_duration_hours(self, obj):
        return obj.duration_hours()
    
    def get_is_upcoming(self, obj):
        return obj.is_upcoming()
    
    def get_is_overdue(self, obj):
        return obj.is_overdue()


class StudentAchievementSerializer(serializers.ModelSerializer):
    student = StudentProfileSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=StudentProfile.objects.all(), write_only=True, source='student'
    )
    verified_by = UserBasicSerializer(read_only=True)
    recorded_by = UserBasicSerializer(read_only=True)
    recorded_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='recorded_by'
    )
    achievement_type_display = serializers.SerializerMethodField()
    category_display = serializers.SerializerMethodField()
    significance_level_display = serializers.SerializerMethodField()
    tags_list = serializers.SerializerMethodField()
    days_since_achievement = serializers.SerializerMethodField()
    is_recent = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentAchievement
        fields = [
            'id', 'student', 'student_id', 'achievement_type', 'achievement_type_display',
            'title', 'description', 'achievement_date', 'category', 'category_display',
            'significance_level', 'significance_level_display', 'recognizing_organization',
            'certificate_file', 'supporting_documents', 'is_verified', 'verified_by',
            'verification_date', 'verification_notes', 'skills_developed',
            'impact_description', 'featured_achievement', 'public_visibility',
            'recorded_by', 'recorded_by_id', 'recorded_date', 'last_updated',
            'tags', 'tags_list', 'days_since_achievement', 'is_recent'
        ]
        read_only_fields = ['recorded_date', 'last_updated']
    
    def get_achievement_type_display(self, obj):
        return obj.get_achievement_type_display()
    
    def get_category_display(self, obj):
        return obj.get_category_display()
    
    def get_significance_level_display(self, obj):
        return obj.get_significance_level_display()
    
    def get_tags_list(self, obj):
        return obj.get_tags_list()
    
    def get_days_since_achievement(self, obj):
        return obj.days_since_achievement()
    
    def get_is_recent(self, obj):
        return obj.is_recent()


# Statistics Serializers
class StudentStatsSerializer(serializers.Serializer):
    total_students = serializers.IntegerField()
    active_students = serializers.IntegerField()
    new_students_this_month = serializers.IntegerField()
    students_by_level = serializers.DictField()
    students_by_status = serializers.DictField()
    average_cgpa = serializers.FloatField()


class CourseStatsSerializer(serializers.Serializer):
    total_courses = serializers.IntegerField()
    active_courses = serializers.IntegerField()
    total_enrollments = serializers.IntegerField()
    courses_by_level = serializers.DictField()
    average_enrollment_rate = serializers.FloatField()


class AcademicStatsSerializer(serializers.Serializer):
    total_assignments = serializers.IntegerField()
    submitted_assignments = serializers.IntegerField()
    graded_assignments = serializers.IntegerField()
    average_grade_percentage = serializers.FloatField()
    submission_rate = serializers.FloatField()


# Search Serializers
class StudentSearchSerializer(serializers.Serializer):
    student_id = serializers.CharField(required=False)
    name = serializers.CharField(required=False)
    academic_level = serializers.CharField(required=False)
    enrollment_status = serializers.CharField(required=False)
    college = serializers.CharField(required=False)
    specialization = serializers.CharField(required=False)


class CourseSearchSerializer(serializers.Serializer):
    code = serializers.CharField(required=False)
    name = serializers.CharField(required=False)
    instructor = serializers.CharField(required=False)
    level = serializers.CharField(required=False)
    is_active = serializers.BooleanField(required=False)


class AssignmentSearchSerializer(serializers.Serializer):
    course_id = serializers.IntegerField(required=False)
    assignment_type = serializers.CharField(required=False)
    is_published = serializers.BooleanField(required=False)
    due_date_from = serializers.DateField(required=False)
    due_date_to = serializers.DateField(required=False)