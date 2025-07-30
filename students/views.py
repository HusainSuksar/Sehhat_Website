from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from django.core.paginator import Paginator
from django.db import transaction
import json
from datetime import datetime, timedelta, date
from decimal import Decimal

from accounts import models

from .models import (
    Student, StudentProfile, Course, Enrollment, Assignment, Submission,
    Grade, Attendance, Schedule, Announcement, StudentGroup, Event,
    LibraryRecord, Achievement, Scholarship, Fee, Payment
)
from accounts.models import User
from moze.models import Moze


@login_required
def dashboard(request):
    """Students dashboard with academic information"""
    user = request.user
    
    # Get student profile
    student_profile = None
    if user.role == 'student':
        student_profile = Student.objects.filter(user=user).first()
    
    # Base queryset based on user role
    if user.role == 'admin':
        students = Student.objects.all()
        enrollments = Enrollment.objects.all()
        courses = Course.objects.all()
        can_manage = True
    elif user.role == 'aamil' or user.role == 'moze_coordinator':
        # Can see students from their moze
        students = Student.objects.filter(
            Q(user__role="aamil") | Q(user__role="moze_coordinator")
        )
        enrollments = Enrollment.objects.filter(
            student__user__role="aamil"
        ) | Enrollment.objects.filter(
            student__user__role="moze_coordinator"
        )
        courses = Course.objects.filter(
            Q(instructor=user) | Q(enrollments__student__user__role="aamil")
        ).distinct()
        can_manage = True
    else:
        # Regular students can only see their own data
        if student_profile:
            students = Student.objects.filter(id=student_profile.id)
            enrollments = Enrollment.objects.filter(student=student_profile)
            courses = Course.objects.filter(enrollments__student=student_profile)
        else:
            students = Student.objects.none()
            enrollments = Enrollment.objects.none()
            courses = Course.objects.none()
        can_manage = False
    
    # Statistics
    total_students = students.count()
    active_students = students.filter(enrollment_status='active').count()
    total_courses = courses.count()
    total_enrollments = enrollments.count()
    
    # Recent activities
    recent_assignments = Assignment.objects.filter(
        course__in=courses
    ).select_related('course').order_by('-due_date')[:5]
    
    recent_submissions = Submission.objects.filter(
        assignment__course__in=courses
    ).select_related('assignment', 'student__user').order_by('-submitted_at')[:5]
    
    recent_announcements = Announcement.objects.filter(
        course__in=courses
            ).select_related('course', 'author').order_by('-created_at')[:5]
    
    # Student-specific data
    my_data = {}
    if student_profile:
        my_enrollments = enrollments.filter(student=student_profile)
        my_data = {
            'current_courses': my_enrollments.filter(status='enrolled').count(),
            'completed_courses': my_enrollments.filter(status='completed').count(),
            'pending_assignments': Assignment.objects.filter(
                course__enrollments__student=student_profile,
                due_date__gte=timezone.now().date()
            ).exclude(
                submissions__student=student_profile
            ).count(),
            'average_grade': Grade.objects.filter(
                student=student_profile
            ).aggregate(avg_grade=Avg('points'))['avg_grade'] or 0,
        }
    
    # Monthly enrollment trends
    monthly_stats = []
    for i in range(6):
        month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
        month_enrollments = enrollments.filter(
            enrolled_date__year=month_start.year,
            enrolled_date__month=month_start.month
        ).count()
        monthly_stats.append({
            'month': month_start.strftime('%b %Y'),
            'count': month_enrollments
        })
    
    # Course statistics
    course_stats = courses.annotate(
        student_count=Count('enrollments')
    ).order_by('-student_count')[:5]
    
    # Upcoming events
    upcoming_events = Event.objects.filter(
        start_date__gte=timezone.now().date()
    ).order_by('start_date')[:5]
    
    context = {
        'total_students': total_students,
        'active_students': active_students,
        'total_courses': total_courses,
        'total_enrollments': total_enrollments,
        'recent_assignments': recent_assignments,
        'recent_submissions': recent_submissions,
        'recent_announcements': recent_announcements,
        'my_data': my_data,
        'monthly_stats': monthly_stats[::-1],
        'course_stats': course_stats,
        'upcoming_events': upcoming_events,
        'student_profile': student_profile,
        'can_manage': can_manage,
        'user_role': user.get_role_display(),
    }
    
    return render(request, 'students/dashboard.html', context)


class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'students/student_list.html'
    context_object_name = 'students'
    paginate_by = 20

    def get_queryset(self):
        user = self.request.user
        print("Logged in as:", user.username, "| Role:", user.role)
        if user.role == 'admin' or user.role == 'aamil' or user.role == 'moze_coordinator' or user.role =='badri_mahal_admin':
            return Student.objects.all()
        else:
            return Student.objects.filter(user=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if user.role == "admin" or user.role == "aamil" or user.role == "moze_coordinator":
            context['moze_options'] = Moze.objects.filter(is_active=True)
        
        context['year_choices'] = [
            ('undergraduate', 'Undergraduate'),
            ('postgraduate', 'Postgraduate'),
            ('doctoral', 'Doctoral'),
            ('diploma', 'Diploma'),
        ]
        context['current_filters'] = {
            'moze': self.request.GET.get('moze', ''),
            'status': self.request.GET.get('status', ''),
            'year': self.request.GET.get('year', ''),
            'search': self.request.GET.get('search', ''),
        }
        return context


class CourseListView(LoginRequiredMixin, ListView):
    """List courses with enrollment information"""
    model = Course
    template_name = 'students/course_list.html'
    context_object_name = 'courses'
    paginate_by = 20
    
    def get_queryset(self):
        user = self.request.user
        
        # Base queryset based on user role
        if user.role == "admin":
            queryset = Course.objects.all()
        elif user.role == "aamil" or user.role == "moze_coordinator":
            queryset = Course.objects.filter(
                Q(instructor=user) | Q(enrollments__student__user__role="aamil")
            ).distinct()
        else:
            # Students can see courses they're enrolled in or available courses
            student_profile = Student.objects.filter(user=user).first()
            if student_profile:
                queryset = Course.objects.filter(
                    Q(enrollments__student=student_profile) | Q(is_active=True)
                ).distinct()
            else:
                queryset = Course.objects.filter(is_active=True)
        
        # Apply filters
        category_filter = self.request.GET.get('category')
        if category_filter:
            queryset = queryset.filter(category=category_filter)
        
        level_filter = self.request.GET.get('level')
        if level_filter:
            queryset = queryset.filter(level=level_filter)
        
        status_filter = self.request.GET.get('status')
        if status_filter == 'active':
            queryset = queryset.filter(is_active=True)
        elif status_filter == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(instructor__first_name__icontains=search) |
                Q(instructor__last_name__icontains=search)
            )
        
        return queryset.select_related('instructor').annotate(
            student_count=Count('enrollments')
        ).order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = [
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
        ]
        context['levels'] = [
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
        ]
        context['current_filters'] = {
            'category': self.request.GET.get('category', ''),
            'level': self.request.GET.get('level', ''),
            'status': self.request.GET.get('status', ''),
            'search': self.request.GET.get('search', ''),
        }
        return context


class CourseDetailView(LoginRequiredMixin, DetailView):
    """Detailed view of a course"""
    model = Course
    template_name = 'students/course_detail.html'
    context_object_name = 'course'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        user = self.request.user
        
        # Enrollments
        enrollments = course.enrollments.select_related('student__user').order_by('enrolled_date')
        context['enrollments'] = enrollments
        context['total_enrollments'] = enrollments.count()
        
        # User's enrollment status
        student_profile = Student.objects.filter(user=user).first()
        if student_profile:
            context['user_enrollment'] = enrollments.filter(student=student_profile).first()
        
        # Assignments
        assignments = course.assignments.order_by('-due_date')
        context['assignments'] = assignments
        
        # Announcements
        context['announcements'] = course.announcements.select_related('author').order_by('-created_at')
        
        # Schedule
        context['schedules'] = course.schedules.order_by('day_of_week', 'start_time')
        
        # Permission checks
        context['can_manage'] = (
            user == course.instructor or 
            user.role == "admin" or 
            (user.role == "aamil" or user.role == "moze_coordinator")
        )
        
        context['can_enroll'] = (
            student_profile and 
            course.is_active and 
            not enrollments.filter(student=student_profile).exists()
        )
        
        # Grade statistics
        if context['can_manage']:
            grades = Grade.objects.filter(student__enrollments__course=course)
            context['average_grade'] = grades.aggregate(avg=Avg('points'))['avg'] or 0
            context['grade_distribution'] = grades.values('grade').annotate(count=Count('id'))
        
        return context


@login_required
def enroll_in_course(request, course_id):
    """Enroll a student in a course"""
    if request.method == 'POST':
        course = get_object_or_404(Course, id=course_id)
        user = request.user
        
        # Check if user is a student
        student_profile = Student.objects.filter(user=user).first()
        if not student_profile:
            return JsonResponse({'error': 'Only students can enroll in courses'}, status=403)
        
        # Check if course is active
        if not course.is_active:
            return JsonResponse({'error': 'This course is not currently active'}, status=400)
        
        # Check if already enrolled
        existing_enrollment = Enrollment.objects.filter(
            student=student_profile,
            course=course
        ).first()
        
        if existing_enrollment:
            return JsonResponse({'error': 'You are already enrolled in this course'}, status=400)
        
        # Create enrollment
        enrollment = Enrollment.objects.create(
            student=student_profile,
            course=course,
            enrolled_date=timezone.now().date(),
            status='enrolled'
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully enrolled in {course.name}'
        })
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def assignment_detail(request, assignment_id):
    """View assignment details and submit work"""
    assignment = get_object_or_404(Assignment, id=assignment_id)
    user = request.user
    
    # Check permissions
    student_profile = Student.objects.filter(user=user).first()
    can_view = (
        user == assignment.course.instructor or
        user.role == "admin" or
        (student_profile and assignment.course.enrollments.filter(student=student_profile).exists())
    )
    
    if not can_view:
        messages.error(request, "You don't have permission to view this assignment.")
        return redirect('students:course_detail', pk=assignment.course.id)
    
    # Get existing submission
    submission = None
    if student_profile:
        submission = Submission.objects.filter(
            assignment=assignment,
            student=student_profile
        ).first()
    
    # Handle submission
    if request.method == 'POST' and student_profile and not submission:
        content = request.POST.get('content', '').strip()
        uploaded_file = request.FILES.get('file')
        
        if content or uploaded_file:
            submission = Submission.objects.create(
                assignment=assignment,
                student=student_profile,
                content=content,
                file=uploaded_file,
                submitted_at=timezone.now()
            )
            messages.success(request, 'Assignment submitted successfully.')
            return redirect('students:assignment_detail', assignment_id=assignment_id)
        else:
            messages.error(request, 'Please provide content or upload a file.')
    
    # Get grade if exists
    grade = None
    if student_profile and submission:
        grade = Grade.objects.filter(
            student=student_profile,
            assignment=assignment
        ).first()
    
    context = {
        'assignment': assignment,
        'submission': submission,
        'grade': grade,
        'can_submit': (
            student_profile and 
            not submission and 
            assignment.due_date >= timezone.now().date()
        ),
        'is_overdue': assignment.due_date < timezone.now().date(),
    }
    
    return render(request, 'students/assignment_detail.html', context)


@login_required
def my_grades(request):
    """View student's grades"""
    user = request.user
    student_profile = Student.objects.filter(user=user).first()
    
    if not student_profile:
        messages.error(request, "You need to have a student profile to view grades.")
        return redirect('students:dashboard')
    
    # Get grades
    grades = Grade.objects.filter(
        student=student_profile
    ).select_related('assignment__course', 'graded_by').order_by('-date_graded')
    
    # Calculate statistics
    total_grades = grades.count()
    if total_grades > 0:
        average_grade = grades.aggregate(avg=Avg('points'))['avg']
        highest_grade = grades.aggregate(max=models.Max('points'))['max']
        latest_grade = grades.first()
    else:
        average_grade = 0
        highest_grade = 0
        latest_grade = None
    
    # Group by course
    grades_by_course = {}
    for grade in grades:
        course = grade.assignment.course
        if course not in grades_by_course:
            grades_by_course[course] = []
        grades_by_course[course].append(grade)
    
    context = {
        'grades': grades,
        'grades_by_course': grades_by_course,
        'total_grades': total_grades,
        'average_grade': average_grade,
        'highest_grade': highest_grade,
        'latest_grade': latest_grade,
        'student_profile': student_profile,
    }
    
    return render(request, 'students/my_grades.html', context)


@login_required
def my_schedule(request):
    """View student's class schedule"""
    user = request.user
    student_profile = Student.objects.filter(user=user).first()
    
    if not student_profile:
        messages.error(request, "You need to have a student profile to view schedule.")
        return redirect('students:dashboard')
    
    # Get enrolled courses
    enrolled_courses = Course.objects.filter(
        enrollments__student=student_profile,
        enrollments__status='enrolled'
    )
    
    # Get schedules
    schedules = Schedule.objects.filter(
        course__in=enrolled_courses
    ).select_related('course').order_by('day_of_week', 'start_time')
    
    # Group by day of week
    schedule_by_day = {}
    for schedule in schedules:
        day = schedule.get_day_of_week_display()
        if day not in schedule_by_day:
            schedule_by_day[day] = []
        schedule_by_day[day].append(schedule)
    
    context = {
        'schedules': schedules,
        'schedule_by_day': schedule_by_day,
        'enrolled_courses': enrolled_courses,
        'student_profile': student_profile,
    }
    
    return render(request, 'students/my_schedule.html', context)


@login_required
def attendance_record(request):
    """View student's attendance record"""
    user = request.user
    student_profile = Student.objects.filter(user=user).first()
    
    if not student_profile:
        messages.error(request, "You need to have a student profile to view attendance.")
        return redirect('students:dashboard')
    
    # Get attendance records
    attendance_records = Attendance.objects.filter(
        student=student_profile
    ).select_related('course').order_by('-date')
    
    # Calculate statistics
    total_classes = attendance_records.count()
    attended_classes = attendance_records.filter(status='present').count()
    attendance_percentage = (attended_classes / total_classes * 100) if total_classes > 0 else 0
    
    # Group by course
    attendance_by_course = {}
    for record in attendance_records:
        course = record.course
        if course not in attendance_by_course:
            attendance_by_course[course] = {
                'records': [],
                'total': 0,
                'present': 0,
                'percentage': 0
            }
        attendance_by_course[course]['records'].append(record)
        attendance_by_course[course]['total'] += 1
        if record.status == 'present':
            attendance_by_course[course]['present'] += 1
    
    # Calculate percentages
    for course_data in attendance_by_course.values():
        if course_data['total'] > 0:
            course_data['percentage'] = (course_data['present'] / course_data['total']) * 100
    
    context = {
        'attendance_records': attendance_records,
        'attendance_by_course': attendance_by_course,
        'total_classes': total_classes,
        'attended_classes': attended_classes,
        'attendance_percentage': attendance_percentage,
        'student_profile': student_profile,
    }
    
    return render(request, 'students/attendance_record.html', context)


@login_required
def student_analytics(request):
    """Analytics dashboard for student management"""
    user = request.user
    
    # Check permissions
    if not (user.role == "admin" or user.role == "aamil" or user.role == "moze_coordinator"):
        messages.error(request, "You don't have permission to view analytics.")
        return redirect('students:dashboard')
    
    # Base queryset
    if user.role == "admin":
        students = Student.objects.all()
        enrollments = Enrollment.objects.all()
        courses = Course.objects.all()
    else:
        students = Student.objects.filter(
            Q(user__role="aamil") | Q(user__role="moze_coordinator")
        )
        enrollments = Enrollment.objects.filter(
            student__in=students
        )
        courses = Course.objects.filter(
            enrollments__student__in=students
        ).distinct()
    
    # Time-based statistics
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    stats = {
        'total_students': students.count(),
        'active_students': students.filter(enrollment_status='active').count(),
        'new_this_week': students.filter(enrollment_date__gte=week_ago).count(),
        'new_this_month': students.filter(enrollment_date__gte=month_ago).count(),
        'total_enrollments': enrollments.count(),
        'active_enrollments': enrollments.filter(status='enrolled').count(),
        'total_courses': courses.count(),
        'active_courses': courses.filter(is_active=True).count(),
    }
    
    # Enrollment trends
    monthly_enrollments = []
    for i in range(12):
        month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
        month_count = enrollments.filter(
            enrolled_date__year=month_start.year,
            enrolled_date__month=month_start.month
        ).count()
        monthly_enrollments.append({
            'month': month_start.strftime('%b %Y'),
            'count': month_count
        })
    
    # Course popularity
    popular_courses = courses.annotate(
        student_count=Count('enrollments')
    ).order_by('-student_count')[:10]
    
    # Grade distribution
    grade_distribution = Grade.objects.filter(
        student__in=students
    ).values('letter_grade').annotate(count=Count('id')).order_by('letter_grade')
    
    # Attendance statistics
    attendance_stats = Attendance.objects.filter(
        student__in=students
    ).aggregate(
        total_classes=Count('id'),
        present_count=Count('id', filter=Q(status='present')),
        absent_count=Count('id', filter=Q(status='absent'))
    )
    
    # Year of study distribution
    year_distribution = students.values('academic_level').annotate(
        count=Count('id')
    ).order_by('academic_level')
    
    context = {
        'stats': stats,
        'monthly_enrollments': monthly_enrollments[::-1],
        'popular_courses': popular_courses,
        'grade_distribution': grade_distribution,
        'attendance_stats': attendance_stats,
        'year_distribution': year_distribution,
        'user_role': user.get_role_display(),
    }
    
    return render(request, 'students/analytics.html', context)


@login_required
def export_student_data(request):
    """Export student data to CSV"""
    import csv
    
    user = request.user
    
    # Check permissions
    if not (user.role == "admin" or user.role == "aamil" or user.role == "moze_coordinator"):
        messages.error(request, "You don't have permission to export data.")
        return redirect('students:dashboard')
    
    data_type = request.GET.get('type', 'students')
    
    # Base queryset
    if user.role == "admin":
        students = Student.objects.all()
        enrollments = Enrollment.objects.all()
    else:
        students = Student.objects.filter(
            Q(user__role="aamil") | Q(user__role="moze_coordinator")
        )
        enrollments = Enrollment.objects.filter(student__in=students)
    
    response = HttpResponse(content_type='text/csv')
    
    if data_type == 'students':
        response['Content-Disposition'] = 'attachment; filename="students.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'Student ID', 'Name', 'ITS ID', 'Email', 'Phone', 
            'Year of Study', 'Moze', 'Active', 'Enrollment Date'
        ])
        
        for student in students.select_related('user'):
            writer.writerow([
                student.student_id,
                student.user.get_full_name(),
                student.user.its_id,
                student.user.email,
                student.user.phone_number,
                student.get_academic_level_display(),
                '',  # Moze field removed from Student model
                'Yes' if student.enrollment_status == 'active' else 'No',
                student.enrollment_date.strftime('%Y-%m-%d')
            ])
    
    elif data_type == 'enrollments':
        response['Content-Disposition'] = 'attachment; filename="enrollments.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'Student', 'Course', 'Enrollment Date', 'Status', 'Grade'
        ])
        
        for enrollment in enrollments.select_related('student__user', 'course'):
            avg_grade = Grade.objects.filter(
                student=enrollment.student,
                assignment__course=enrollment.course
            ).aggregate(avg=Avg('points'))['avg']
            
            writer.writerow([
                enrollment.student.user.get_full_name(),
                enrollment.course.name,
                enrollment.enrolled_date,
                enrollment.get_status_display(),
                f"{avg_grade:.2f}" if avg_grade else 'N/A'
            ])
    
    return response


class StudentDetailView(LoginRequiredMixin, DetailView):
    """Detailed view of a single student"""
    model = Student
    template_name = 'students/student_detail.html'
    context_object_name = 'student'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.object
        
        # Get student's enrollments
        context['enrollments'] = student.enrollments.select_related('course').order_by('-enrolled_date')
        
        # Get student's grades
        try:
            context['grades'] = student.grades.select_related('course').order_by('-created_at')
        except:
            context['grades'] = []
        
        return context
