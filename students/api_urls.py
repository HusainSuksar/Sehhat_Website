"""
URL Configuration for the Students API
"""
from django.urls import path
from . import api_views

urlpatterns = [
    # Dashboard
    path('dashboard/', api_views.students_dashboard_api, name='students_dashboard_api'),
    
    # Core Academic Management
    path('students/', api_views.StudentListCreateAPIView.as_view(), name='student_list_create'),
    path('students/<int:pk>/', api_views.StudentDetailAPIView.as_view(), name='student_detail'),
    path('students/search/', api_views.StudentSearchAPIView.as_view(), name='student_search'),
    
    # Course Management
    path('courses/', api_views.CourseListCreateAPIView.as_view(), name='course_list_create'),
    path('courses/<int:pk>/', api_views.CourseDetailAPIView.as_view(), name='course_detail'),
    path('courses/search/', api_views.CourseSearchAPIView.as_view(), name='course_search'),
    
    # Enrollment Management
    path('enrollments/', api_views.EnrollmentListCreateAPIView.as_view(), name='enrollment_list_create'),
    path('enrollments/<int:pk>/', api_views.EnrollmentDetailAPIView.as_view(), name='enrollment_detail'),
    
    # Assignment and Submission Management
    path('assignments/', api_views.AssignmentListCreateAPIView.as_view(), name='assignment_list_create'),
    path('assignments/<int:pk>/', api_views.AssignmentDetailAPIView.as_view(), name='assignment_detail'),
    
    path('submissions/', api_views.SubmissionListCreateAPIView.as_view(), name='student_submission_list_create'),
    path('submissions/<int:pk>/', api_views.SubmissionDetailAPIView.as_view(), name='student_submission_detail'),
    
    # Grading and Assessment
    path('grades/', api_views.GradeListCreateAPIView.as_view(), name='grade_list_create'),
    
    # Academic Support and Services
    path('schedules/', api_views.ScheduleListCreateAPIView.as_view(), name='schedule_list_create'),
    
    path('attendance/', api_views.AttendanceListCreateAPIView.as_view(), name='attendance_list_create'),
    
    # Communication and Announcements
    path('announcements/', api_views.AnnouncementListCreateAPIView.as_view(), name='announcement_list_create'),
    path('announcements/<int:pk>/', api_views.AnnouncementDetailAPIView.as_view(), name='announcement_detail'),
    
    # Student Groups and Activities
    path('groups/', api_views.StudentGroupListCreateAPIView.as_view(), name='student_group_list_create'),
    
    path('events/', api_views.EventListCreateAPIView.as_view(), name='event_list_create'),
    
    # Academic Records and Achievements
    path('library-records/', api_views.LibraryRecordListCreateAPIView.as_view(), name='library_record_list_create'),
    
    path('achievements/', api_views.AchievementListCreateAPIView.as_view(), name='achievement_list_create'),
    
    # Financial Management
    path('scholarships/', api_views.ScholarshipListCreateAPIView.as_view(), name='scholarship_list_create'),
    
    path('fees/', api_views.FeeListCreateAPIView.as_view(), name='fee_list_create'),
    
    path('payments/', api_views.PaymentListCreateAPIView.as_view(), name='payment_list_create'),
    
    # Extended Student Profile
    path('profiles/', api_views.StudentProfileListCreateAPIView.as_view(), name='student_profile_list_create'),
    path('profiles/<int:pk>/', api_views.StudentProfileDetailAPIView.as_view(), name='student_profile_detail'),
    
    # Statistics
    path('stats/students/', api_views.student_stats_api, name='student_stats'),
    path('stats/courses/', api_views.course_stats_api, name='course_stats'),
    path('stats/academic/', api_views.academic_stats_api, name='academic_stats'),
]