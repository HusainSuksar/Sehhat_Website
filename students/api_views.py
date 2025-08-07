"""
API Views for the Students app
"""
from rest_framework import generics, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg, Count
from django.utils import timezone
from datetime import timedelta

from .models import (
    Student, Course, Enrollment, Assignment, Submission, Grade, Schedule,
    Attendance, Announcement, StudentGroup, GroupMembership, Event,
    LibraryRecord, Achievement, Scholarship, Fee, Payment, StudentProfile,
    MentorshipRequest, AidRequest, StudentMeeting, StudentAchievement
)
from .serializers import (
    StudentSerializer, CourseSerializer, EnrollmentSerializer, AssignmentSerializer,
    SubmissionSerializer, GradeSerializer, ScheduleSerializer, AttendanceSerializer,
    AnnouncementSerializer, StudentGroupSerializer, EventSerializer,
    LibraryRecordSerializer, AchievementSerializer, ScholarshipSerializer,
    FeeSerializer, PaymentSerializer, StudentProfileSerializer,
    MentorshipRequestSerializer, AidRequestSerializer, StudentMeetingSerializer,
    StudentAchievementSerializer, StudentStatsSerializer, CourseStatsSerializer,
    AcademicStatsSerializer, StudentSearchSerializer, CourseSearchSerializer,
    AssignmentSearchSerializer
)


# Custom Permission Classes
class IsAdminOrInstructor(permissions.BasePermission):
    """
    Permission for admins and instructors to manage academic content
    """
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                (request.user.is_admin or request.user.role in ['doctor', 'badri_mahal_admin']))


class IsStudentOwnerOrStaff(permissions.BasePermission):
    """
    Permission for students to access their own data or staff to access all
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Admin and staff can access all
        if request.user.is_admin or request.user.role in ['doctor', 'badri_mahal_admin', 'aamil']:
            return True
        
        # Students can only access their own data
        if hasattr(obj, 'student'):
            return obj.student.user == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False


class IsStudentOrStaff(permissions.BasePermission):
    """
    Permission for students and staff
    """
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                request.user.role in ['student', 'doctor', 'badri_mahal_admin', 'aamil'])


# Access Control Mixins
class StudentAccessMixin:
    """
    Mixin to filter student data based on user role
    """
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            # Admin can see all students
            return Student.objects.all()
        elif user.role in ['doctor', 'badri_mahal_admin', 'aamil']:
            # Staff can see all active students
            return Student.objects.filter(enrollment_status='active')
        elif user.role == 'student':
            # Students can only see themselves
            try:
                student = Student.objects.get(user=user)
                return Student.objects.filter(id=student.id)
            except Student.DoesNotExist:
                return Student.objects.none()
        
        return Student.objects.none()


class CourseAccessMixin:
    """
    Mixin to filter course data based on user role
    """
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            # Admin can see all courses
            return Course.objects.all()
        elif user.role in ['doctor', 'badri_mahal_admin']:
            # Instructors can see all courses
            return Course.objects.all()
        elif user.role == 'student':
            # Students can see active courses and their enrolled courses
            try:
                student = Student.objects.get(user=user)
                enrolled_courses = student.enrollments.values_list('course', flat=True)
                return Course.objects.filter(
                    Q(is_active=True) | Q(id__in=enrolled_courses)
                ).distinct()
            except Student.DoesNotExist:
                return Course.objects.filter(is_active=True)
        
        return Course.objects.filter(is_active=True)


class EnrollmentAccessMixin:
    """
    Mixin to filter enrollment data based on user role
    """
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            return Enrollment.objects.all()
        elif user.role in ['doctor', 'badri_mahal_admin']:
            return Enrollment.objects.all()
        elif user.role == 'student':
            try:
                student = Student.objects.get(user=user)
                return Enrollment.objects.filter(student=student)
            except Student.DoesNotExist:
                return Enrollment.objects.none()
        
        return Enrollment.objects.none()


# Core Academic API Views
class StudentListCreateAPIView(StudentAccessMixin, generics.ListCreateAPIView):
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['academic_level', 'enrollment_status']
    search_fields = ['student_id', 'user__first_name', 'user__last_name', 'user__email']
    ordering_fields = ['student_id', 'enrollment_date', 'user__first_name']
    ordering = ['student_id']
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminOrInstructor()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        serializer.save()


class StudentDetailAPIView(StudentAccessMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StudentSerializer
    permission_classes = [IsStudentOwnerOrStaff]


class CourseListCreateAPIView(CourseAccessMixin, generics.ListCreateAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['level', 'is_active', 'instructor']
    search_fields = ['code', 'name', 'description']
    ordering_fields = ['code', 'name', 'created_at']
    ordering = ['code']
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminOrInstructor()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        serializer.save()


class CourseDetailAPIView(CourseAccessMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdminOrInstructor()]
        return [permissions.IsAuthenticated()]


class EnrollmentListCreateAPIView(EnrollmentAccessMixin, generics.ListCreateAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'course', 'student']
    search_fields = ['course__code', 'course__name', 'student__student_id']
    ordering_fields = ['enrolled_date', 'course__code']
    ordering = ['-enrolled_date']
    
    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'student':
            # Students can enroll themselves
            try:
                student = Student.objects.get(user=user)
                # Force the student to be the current user for student enrollments
                serializer.save(student=student)
            except Student.DoesNotExist:
                raise PermissionDenied("Student profile not found.")
        elif user.is_admin or user.role in ['doctor', 'badri_mahal_admin']:
            # Staff can enroll any student
            serializer.save()
        else:
            raise PermissionDenied("Insufficient permissions to create enrollment.")


class EnrollmentDetailAPIView(EnrollmentAccessMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [IsStudentOwnerOrStaff]


# Assignment and Submission Management
class AssignmentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['assignment_type', 'course', 'is_published']
    search_fields = ['title', 'description', 'course__code']
    ordering_fields = ['due_date', 'assigned_date', 'title']
    ordering = ['-due_date']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            return Assignment.objects.all()
        elif user.role in ['doctor', 'badri_mahal_admin']:
            # Instructors can see all assignments
            return Assignment.objects.all()
        elif user.role == 'student':
            # Students can see published assignments from their enrolled courses
            try:
                student = Student.objects.get(user=user)
                enrolled_courses = student.enrollments.filter(status='enrolled').values_list('course', flat=True)
                return Assignment.objects.filter(course__in=enrolled_courses, is_published=True)
            except Student.DoesNotExist:
                return Assignment.objects.none()
        
        return Assignment.objects.none()
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminOrInstructor()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        serializer.save()


class AssignmentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser or user.role in ['doctor', 'badri_mahal_admin']:
            return Assignment.objects.all()
        elif user.role == 'student':
            try:
                student = Student.objects.get(user=user)
                enrolled_courses = student.enrollments.filter(status='enrolled').values_list('course', flat=True)
                return Assignment.objects.filter(course__in=enrolled_courses, is_published=True)
            except Student.DoesNotExist:
                return Assignment.objects.none()
        
        return Assignment.objects.none()
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdminOrInstructor()]
        return [permissions.IsAuthenticated()]


class SubmissionListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_graded', 'is_late', 'assignment', 'student']
    search_fields = ['assignment__title', 'student__student_id']
    ordering_fields = ['submitted_at', 'grade_percentage']
    ordering = ['-submitted_at']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            return Submission.objects.all()
        elif user.role in ['doctor', 'badri_mahal_admin']:
            # Instructors can see submissions for their courses
            instructor_courses = Course.objects.filter(instructor=user)
            return Submission.objects.filter(assignment__course__in=instructor_courses)
        elif user.role == 'student':
            # Students can see their own submissions
            try:
                student = Student.objects.get(user=user)
                return Submission.objects.filter(student=student)
            except Student.DoesNotExist:
                return Submission.objects.none()
        
        return Submission.objects.none()
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return super().get_permissions()
    
    def create(self, request, *args, **kwargs):
        # Check permission BEFORE serializer validation
        user = request.user
        if user.role != 'student':
            raise PermissionDenied("Only students can create submissions.")
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        user = self.request.user
        try:
            student = Student.objects.get(user=user)
            serializer.save(student=student)
        except Student.DoesNotExist:
            raise PermissionDenied("Student profile not found.")


class SubmissionDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SubmissionSerializer
    permission_classes = [IsStudentOwnerOrStaff]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            return Submission.objects.all()
        elif user.role in ['doctor', 'badri_mahal_admin']:
            instructor_courses = Course.objects.filter(instructor=user)
            return Submission.objects.filter(assignment__course__in=instructor_courses)
        elif user.role == 'student':
            try:
                student = Student.objects.get(user=user)
                return Submission.objects.filter(student=student)
            except Student.DoesNotExist:
                return Submission.objects.none()
        
        return Submission.objects.none()


# Grading and Assessment
class GradeListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = GradeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['letter_grade', 'course', 'student', 'assignment']
    search_fields = ['student__student_id', 'course__code']
    ordering_fields = ['date_graded', 'percentage']
    ordering = ['-date_graded']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            return Grade.objects.all()
        elif user.role in ['doctor', 'badri_mahal_admin']:
            return Grade.objects.filter(graded_by=user)
        elif user.role == 'student':
            try:
                student = Student.objects.get(user=user)
                return Grade.objects.filter(student=student)
            except Student.DoesNotExist:
                return Grade.objects.none()
        
        return Grade.objects.none()
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminOrInstructor()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        serializer.save(graded_by=self.request.user)


# Academic Support and Services
class ScheduleListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['day_of_week', 'course', 'is_active']
    search_fields = ['course__code', 'course__name', 'room', 'building']
    ordering_fields = ['day_of_week', 'start_time']
    ordering = ['day_of_week', 'start_time']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser or user.role in ['doctor', 'badri_mahal_admin']:
            return Schedule.objects.all()
        elif user.role == 'student':
            try:
                student = Student.objects.get(user=user)
                enrolled_courses = student.enrollments.filter(status='enrolled').values_list('course', flat=True)
                return Schedule.objects.filter(course__in=enrolled_courses, is_active=True)
            except Student.DoesNotExist:
                return Schedule.objects.none()
        
        return Schedule.objects.filter(is_active=True)
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminOrInstructor()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        serializer.save()


class AttendanceListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'course', 'student', 'date']
    search_fields = ['student__student_id', 'course__code']
    ordering_fields = ['date', 'recorded_at']
    ordering = ['-date']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            return Attendance.objects.all()
        elif user.role in ['doctor', 'badri_mahal_admin']:
            return Attendance.objects.all()
        elif user.role == 'student':
            try:
                student = Student.objects.get(user=user)
                return Attendance.objects.filter(student=student)
            except Student.DoesNotExist:
                return Attendance.objects.none()
        
        return Attendance.objects.none()
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminOrInstructor()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        serializer.save(recorded_by=self.request.user)


# Communication and Announcements
class AnnouncementListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = AnnouncementSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_global', 'target_level', 'is_urgent', 'is_published', 'course']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'is_urgent']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            return Announcement.objects.all()
        elif user.role in ['doctor', 'badri_mahal_admin']:
            return Announcement.objects.filter(is_published=True)
        elif user.role == 'student':
            # Students see global announcements and course-specific ones
            try:
                student = Student.objects.get(user=user)
                enrolled_courses = student.enrollments.filter(status='enrolled').values_list('course', flat=True)
                return Announcement.objects.filter(
                    is_published=True
                ).filter(
                    Q(is_global=True) | 
                    Q(course__in=enrolled_courses) |
                    Q(target_level=student.academic_level) |
                    Q(target_level='all')
                ).distinct()
            except Student.DoesNotExist:
                return Announcement.objects.filter(is_published=True, is_global=True)
        
        return Announcement.objects.filter(is_published=True, is_global=True)
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminOrInstructor()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class AnnouncementDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AnnouncementSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Use same logic as list view
        return AnnouncementListCreateAPIView().get_queryset()
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdminOrInstructor()]
        return [permissions.IsAuthenticated()]


# Student Groups and Activities
class StudentGroupListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = StudentGroupSerializer
    permission_classes = [IsStudentOrStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['group_type', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser or user.role in ['doctor', 'badri_mahal_admin', 'aamil']:
            return StudentGroup.objects.all()
        elif user.role == 'student':
            return StudentGroup.objects.filter(is_active=True)
        
        return StudentGroup.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class EventListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['event_type', 'is_published', 'is_cancelled']
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['start_date', 'created_at']
    ordering = ['start_date']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser or user.role in ['doctor', 'badri_mahal_admin']:
            return Event.objects.all()
        else:
            return Event.objects.filter(is_published=True, is_cancelled=False)
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminOrInstructor()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)


# Academic Records and Achievements
class LibraryRecordListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = LibraryRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'student']
    search_fields = ['book_title', 'book_isbn', 'author', 'student__student_id']
    ordering_fields = ['borrowed_date', 'due_date']
    ordering = ['-borrowed_date']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser or user.role in ['doctor', 'badri_mahal_admin']:
            return LibraryRecord.objects.all()
        elif user.role == 'student':
            try:
                student = Student.objects.get(user=user)
                return LibraryRecord.objects.filter(student=student)
            except Student.DoesNotExist:
                return LibraryRecord.objects.none()
        
        return LibraryRecord.objects.none()
    
    def perform_create(self, serializer):
        if not self.request.user.is_admin and self.request.user.role not in ['doctor', 'badri_mahal_admin']:
            raise PermissionDenied("Only library staff can create library records.")
        serializer.save()


class AchievementListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = AchievementSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['achievement_type', 'is_verified', 'student']
    search_fields = ['title', 'description', 'awarded_by']
    ordering_fields = ['date_awarded', 'created_at']
    ordering = ['-date_awarded']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser or user.role in ['doctor', 'badri_mahal_admin']:
            return Achievement.objects.all()
        elif user.role == 'student':
            try:
                student = Student.objects.get(user=user)
                return Achievement.objects.filter(student=student)
            except Student.DoesNotExist:
                return Achievement.objects.none()
        
        return Achievement.objects.none()
    
    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'student':
            try:
                student = Student.objects.get(user=user)
                serializer.save(student=student)
            except Student.DoesNotExist:
                raise PermissionDenied("Student profile not found.")
        elif user.is_admin or user.role in ['doctor', 'badri_mahal_admin']:
            serializer.save()
        else:
            raise PermissionDenied("Insufficient permissions to create achievement.")


# Financial Management
class ScholarshipListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ScholarshipSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['scholarship_type', 'status', 'student']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'amount']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser or user.role in ['doctor', 'badri_mahal_admin']:
            return Scholarship.objects.all()
        elif user.role == 'student':
            try:
                student = Student.objects.get(user=user)
                return Scholarship.objects.filter(student=student)
            except Student.DoesNotExist:
                return Scholarship.objects.none()
        
        return Scholarship.objects.none()
    
    def perform_create(self, serializer):
        if not self.request.user.is_admin and self.request.user.role not in ['doctor', 'badri_mahal_admin']:
            raise PermissionDenied("Only administrators can create scholarships.")
        serializer.save()


class FeeListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = FeeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['fee_type', 'status', 'student', 'academic_year']
    search_fields = ['student__student_id', 'academic_year']
    ordering_fields = ['due_date', 'created_at']
    ordering = ['due_date']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser or user.role in ['doctor', 'badri_mahal_admin']:
            return Fee.objects.all()
        elif user.role == 'student':
            try:
                student = Student.objects.get(user=user)
                return Fee.objects.filter(student=student)
            except Student.DoesNotExist:
                return Fee.objects.none()
        
        return Fee.objects.none()
    
    def perform_create(self, serializer):
        if not self.request.user.is_admin and self.request.user.role not in ['doctor', 'badri_mahal_admin']:
            raise PermissionDenied("Only administrators can create fee records.")
        serializer.save()


class PaymentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['payment_method', 'student', 'fee']
    search_fields = ['receipt_number', 'transaction_id', 'student__student_id']
    ordering_fields = ['payment_date']
    ordering = ['-payment_date']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser or user.role in ['doctor', 'badri_mahal_admin']:
            return Payment.objects.all()
        elif user.role == 'student':
            try:
                student = Student.objects.get(user=user)
                return Payment.objects.filter(student=student)
            except Student.DoesNotExist:
                return Payment.objects.none()
        
        return Payment.objects.none()
    
    def perform_create(self, serializer):
        if not self.request.user.is_admin and self.request.user.role not in ['doctor', 'badri_mahal_admin']:
            raise PermissionDenied("Only staff can record payments.")
        serializer.save(received_by=self.request.user)


# Extended Student Profile and Support Services
class StudentProfileListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['college', 'specialization', 'year_of_study', 'is_active', 'is_verified']
    search_fields = ['its_id', 'user__first_name', 'user__last_name', 'college']
    ordering_fields = ['its_id', 'created_at']
    ordering = ['its_id']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser or user.role in ['doctor', 'badri_mahal_admin', 'aamil']:
            return StudentProfile.objects.all()
        elif user.role == 'student':
            return StudentProfile.objects.filter(user=user)
        
        return StudentProfile.objects.none()
    
    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'student':
            serializer.save(user=user)
        elif user.is_admin or user.role in ['doctor', 'badri_mahal_admin']:
            serializer.save()
        else:
            raise PermissionDenied("Insufficient permissions to create student profile.")


class StudentProfileDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StudentProfileSerializer
    permission_classes = [IsStudentOwnerOrStaff]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser or user.role in ['doctor', 'badri_mahal_admin', 'aamil']:
            return StudentProfile.objects.all()
        elif user.role == 'student':
            return StudentProfile.objects.filter(user=user)
        
        return StudentProfile.objects.none()


# Search API Views
class StudentSearchAPIView(generics.ListAPIView):
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering = ['student_id']
    
    def get_queryset(self):
        # Use StudentAccessMixin logic
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            queryset = Student.objects.all()
        elif user.role in ['doctor', 'badri_mahal_admin', 'aamil']:
            queryset = Student.objects.filter(enrollment_status='active')
        elif user.role == 'student':
            try:
                student = Student.objects.get(user=user)
                queryset = Student.objects.filter(id=student.id)
            except Student.DoesNotExist:
                queryset = Student.objects.none()
        else:
            queryset = Student.objects.none()
        
        # Apply search filters from query params directly
        student_id = self.request.query_params.get('student_id')
        name = self.request.query_params.get('name')
        academic_level = self.request.query_params.get('academic_level')
        enrollment_status = self.request.query_params.get('enrollment_status')
        
        if student_id:
            queryset = queryset.filter(student_id__icontains=student_id)
        if name:
            queryset = queryset.filter(
                Q(user__first_name__icontains=name) |
                Q(user__last_name__icontains=name)
            )
        if academic_level:
            queryset = queryset.filter(academic_level=academic_level)
        if enrollment_status:
            queryset = queryset.filter(enrollment_status=enrollment_status)
        
        return queryset.distinct().order_by('student_id')


class CourseSearchAPIView(generics.ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering = ['code']
    
    def get_queryset(self):
        # Use CourseAccessMixin logic
        user = self.request.user
        
        if user.is_admin or user.is_superuser or user.role in ['doctor', 'badri_mahal_admin']:
            queryset = Course.objects.all()
        elif user.role == 'student':
            try:
                student = Student.objects.get(user=user)
                enrolled_courses = student.enrollments.values_list('course', flat=True)
                queryset = Course.objects.filter(
                    Q(is_active=True) | Q(id__in=enrolled_courses)
                ).distinct()
            except Student.DoesNotExist:
                queryset = Course.objects.filter(is_active=True)
        else:
            queryset = Course.objects.filter(is_active=True)
        
        # Apply search filters from query params directly
        code = self.request.query_params.get('code')
        name = self.request.query_params.get('name')
        instructor = self.request.query_params.get('instructor')
        level = self.request.query_params.get('level')
        is_active = self.request.query_params.get('is_active')
        
        if code:
            queryset = queryset.filter(code__icontains=code)
        if name:
            queryset = queryset.filter(name__icontains=name)
        if instructor:
            queryset = queryset.filter(instructor__username__icontains=instructor)
        if level:
            queryset = queryset.filter(level=level)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.distinct().order_by('code')


# Statistics API Views
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def student_stats_api(request):
    """Get student statistics"""
    user = request.user
    
    if not (user.is_admin or user.role in ['doctor', 'badri_mahal_admin', 'aamil']):
        raise PermissionDenied("Insufficient permissions to view statistics.")
    
    # Base queryset
    students = Student.objects.all()
    
    # Calculate stats
    total_students = students.count()
    active_students = students.filter(enrollment_status='active').count()
    
    # New students this month
    current_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    new_students_this_month = students.filter(enrollment_date__gte=current_month).count()
    
    # Students by level
    students_by_level = dict(students.values_list('academic_level').annotate(count=Count('id')))
    
    # Students by status
    students_by_status = dict(students.values_list('enrollment_status').annotate(count=Count('id')))
    
    # Average CGPA (from StudentProfile)
    avg_cgpa = StudentProfile.objects.filter(current_cgpa__isnull=False).aggregate(
        avg=Avg('current_cgpa')
    )['avg'] or 0
    
    stats = {
        'total_students': total_students,
        'active_students': active_students,
        'new_students_this_month': new_students_this_month,
        'students_by_level': students_by_level,
        'students_by_status': students_by_status,
        'average_cgpa': round(avg_cgpa, 2)
    }
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def course_stats_api(request):
    """Get course statistics"""
    user = request.user
    
    if not (user.is_admin or user.role in ['doctor', 'badri_mahal_admin']):
        raise PermissionDenied("Insufficient permissions to view course statistics.")
    
    # Base queryset
    courses = Course.objects.all()
    
    # Calculate stats
    total_courses = courses.count()
    active_courses = courses.filter(is_active=True).count()
    total_enrollments = Enrollment.objects.count()
    
    # Courses by level
    courses_by_level = dict(courses.values_list('level').annotate(count=Count('id')))
    
    # Average enrollment rate
    avg_enrollment_rate = 0
    if active_courses > 0:
        enrollment_rates = []
        for course in courses.filter(is_active=True):
            if course.max_students > 0:
                rate = (course.enrollment_count / course.max_students) * 100
                enrollment_rates.append(rate)
        
        if enrollment_rates:
            avg_enrollment_rate = sum(enrollment_rates) / len(enrollment_rates)
    
    stats = {
        'total_courses': total_courses,
        'active_courses': active_courses,
        'total_enrollments': total_enrollments,
        'courses_by_level': courses_by_level,
        'average_enrollment_rate': round(avg_enrollment_rate, 2)
    }
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def academic_stats_api(request):
    """Get academic performance statistics"""
    user = request.user
    
    if not (user.is_admin or user.role in ['doctor', 'badri_mahal_admin']):
        raise PermissionDenied("Insufficient permissions to view academic statistics.")
    
    # Assignment and submission stats
    total_assignments = Assignment.objects.count()
    submitted_assignments = Submission.objects.count()
    graded_assignments = Submission.objects.filter(is_graded=True).count()
    
    # Average grade percentage
    avg_grade = Submission.objects.filter(
        is_graded=True, grade_percentage__isnull=False
    ).aggregate(avg=Avg('grade_percentage'))['avg'] or 0
    
    # Submission rate
    submission_rate = 0
    if total_assignments > 0:
        # Calculate based on published assignments and enrolled students
        published_assignments = Assignment.objects.filter(is_published=True).count()
        if published_assignments > 0:
            submission_rate = (submitted_assignments / published_assignments) * 100
    
    stats = {
        'total_assignments': total_assignments,
        'submitted_assignments': submitted_assignments,
        'graded_assignments': graded_assignments,
        'average_grade_percentage': round(avg_grade, 2),
        'submission_rate': round(submission_rate, 2)
    }
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def students_dashboard_api(request):
    """Get comprehensive dashboard data for students app"""
    user = request.user
    
    if not user.is_authenticated:
        raise PermissionDenied("Authentication required.")
    
    dashboard_data = {}
    
    try:
        # Role-specific dashboard data
        if user.is_admin or user.role in ['doctor', 'badri_mahal_admin', 'aamil']:
            # Staff dashboard - compute stats directly
            # Student stats
            students = Student.objects.all()
            total_students = students.count()
            active_students = students.filter(enrollment_status='active').count()
            current_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            new_students_this_month = students.filter(enrollment_date__gte=current_month).count()
            students_by_level = dict(students.values_list('academic_level').annotate(count=Count('id')))
            students_by_status = dict(students.values_list('enrollment_status').annotate(count=Count('id')))
            avg_cgpa = StudentProfile.objects.filter(current_cgpa__isnull=False).aggregate(avg=Avg('current_cgpa'))['avg'] or 0
            
            dashboard_data['student_stats'] = {
                'total_students': total_students,
                'active_students': active_students,
                'new_students_this_month': new_students_this_month,
                'students_by_level': students_by_level,
                'students_by_status': students_by_status,
                'average_cgpa': round(avg_cgpa, 2)
            }
            
            # Course stats
            courses = Course.objects.all()
            total_courses = courses.count()
            active_courses = courses.filter(is_active=True).count()
            total_enrollments = Enrollment.objects.count()
            courses_by_level = dict(courses.values_list('level').annotate(count=Count('id')))
            
            dashboard_data['course_stats'] = {
                'total_courses': total_courses,
                'active_courses': active_courses,
                'total_enrollments': total_enrollments,
                'courses_by_level': courses_by_level,
                'average_enrollment_rate': 0  # Will calculate if needed
            }
            
            # Academic stats
            total_assignments = Assignment.objects.count()
            submitted_assignments = Submission.objects.count()
            graded_assignments = Submission.objects.filter(is_graded=True).count()
            avg_grade = Submission.objects.filter(is_graded=True, grade_percentage__isnull=False).aggregate(avg=Avg('grade_percentage'))['avg'] or 0
            
            dashboard_data['academic_stats'] = {
                'total_assignments': total_assignments,
                'submitted_assignments': submitted_assignments,
                'graded_assignments': graded_assignments,
                'average_grade_percentage': round(avg_grade, 2),
                'submission_rate': 0  # Will calculate if needed
            }
            
            # Recent activities
            dashboard_data['recent_enrollments'] = EnrollmentSerializer(
                Enrollment.objects.select_related('student', 'course').order_by('-enrolled_date')[:5],
                many=True
            ).data
            
            dashboard_data['recent_submissions'] = SubmissionSerializer(
                Submission.objects.select_related('student', 'assignment').order_by('-submitted_at')[:5],
                many=True
            ).data
            
        elif user.role == 'student':
            # Student dashboard - personal data
            try:
                student = Student.objects.get(user=user)
                
                # Personal stats
                dashboard_data['my_enrollments'] = EnrollmentSerializer(
                    student.enrollments.filter(status='enrolled').select_related('course'),
                    many=True
                ).data
                
                dashboard_data['my_assignments'] = AssignmentSerializer(
                    Assignment.objects.filter(
                        course__in=student.enrollments.filter(status='enrolled').values_list('course', flat=True),
                        is_published=True
                    ).order_by('-due_date')[:10],
                    many=True
                ).data
                
                dashboard_data['my_grades'] = GradeSerializer(
                    Grade.objects.filter(student=student).order_by('-date_graded')[:10],
                    many=True
                ).data
                
                dashboard_data['my_achievements'] = AchievementSerializer(
                    Achievement.objects.filter(student=student).order_by('-date_awarded')[:5],
                    many=True
                ).data
                
            except Student.DoesNotExist:
                dashboard_data['error'] = 'Student profile not found'
        
        # Common data for all users
        dashboard_data['recent_announcements'] = AnnouncementSerializer(
            Announcement.objects.filter(is_published=True).order_by('-created_at')[:5],
            many=True
        ).data
        
        dashboard_data['upcoming_events'] = EventSerializer(
            Event.objects.filter(
                is_published=True,
                is_cancelled=False,
                start_date__gte=timezone.now()
            ).order_by('start_date')[:5],
            many=True
        ).data
        
    except Exception as e:
        dashboard_data['error'] = str(e)
    
    return Response(dashboard_data)