from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Student management
    path('students/', views.StudentListView.as_view(), name='student_list'),
    path('students/<int:pk>/', views.StudentDetailView.as_view(), name='student_detail'),
    path('students/<int:pk>/edit/', views.StudentUpdateView.as_view(), name='student_update'),
    
    # Course management
    path('courses/', views.CourseListView.as_view(), name='course_list'),
    path('courses/<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('courses/create/', views.CourseCreateView.as_view(), name='course_create'),
    path('courses/<int:pk>/edit/', views.CourseUpdateView.as_view(), name='course_update'),
    
    # Enrollment
    path('courses/<int:course_id>/enroll/', views.enroll_in_course, name='enroll_course'),
    path('enrollments/', views.EnrollmentListView.as_view(), name='enrollment_list'),
    
    # Assignments and submissions
    path('assignments/', views.AssignmentListView.as_view(), name='assignment_list'),
    path('assignments/<int:pk>/', views.assignment_detail, name='assignment_detail'),
    path('assignments/create/', views.AssignmentCreateView.as_view(), name='assignment_create'),
    path('assignments/<int:pk>/submit/', views.submit_assignment, name='submit_assignment'),
    
    # Grades and academic records
    path('grades/', views.my_grades, name='my_grades'),
    path('grades/<int:student_id>/', views.student_grades, name='student_grades'),
    
    # Schedule and attendance
    path('schedule/', views.my_schedule, name='my_schedule'),
    path('attendance/', views.attendance_record, name='attendance_record'),
    path('attendance/<int:course_id>/', views.course_attendance, name='course_attendance'),
    
    # Announcements
    path('announcements/', views.AnnouncementListView.as_view(), name='announcement_list'),
    path('announcements/<int:pk>/', views.AnnouncementDetailView.as_view(), name='announcement_detail'),
    path('announcements/create/', views.AnnouncementCreateView.as_view(), name='announcement_create'),
    
    # Student groups
    path('groups/', views.StudentGroupListView.as_view(), name='group_list'),
    path('groups/<int:pk>/', views.StudentGroupDetailView.as_view(), name='group_detail'),
    path('groups/create/', views.StudentGroupCreateView.as_view(), name='group_create'),
    path('groups/<int:pk>/join/', views.join_group, name='join_group'),
    
    # Events
    path('events/', views.EventListView.as_view(), name='event_list'),
    path('events/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('events/create/', views.EventCreateView.as_view(), name='event_create'),
    path('events/<int:pk>/register/', views.register_for_event, name='register_event'),
    
    # Library records
    path('library/', views.LibraryRecordListView.as_view(), name='library_records'),
    path('library/<int:pk>/', views.LibraryRecordDetailView.as_view(), name='library_record_detail'),
    
    # Achievements
    path('achievements/', views.AchievementListView.as_view(), name='achievement_list'),
    path('achievements/<int:pk>/', views.AchievementDetailView.as_view(), name='achievement_detail'),
    path('achievements/create/', views.AchievementCreateView.as_view(), name='achievement_create'),
    
    # Scholarships and financial aid
    path('scholarships/', views.ScholarshipListView.as_view(), name='scholarship_list'),
    path('scholarships/<int:pk>/', views.ScholarshipDetailView.as_view(), name='scholarship_detail'),
    path('scholarships/apply/', views.apply_scholarship, name='apply_scholarship'),
    
    # Fees and payments
    path('fees/', views.FeeListView.as_view(), name='fee_list'),
    path('fees/<int:pk>/pay/', views.pay_fee, name='pay_fee'),
    path('payments/', views.PaymentListView.as_view(), name='payment_list'),
    path('payments/<int:pk>/', views.PaymentDetailView.as_view(), name='payment_detail'),
    
    # Analytics and reports
    path('analytics/', views.student_analytics, name='analytics'),
    path('export/', views.export_student_data, name='export_data'),
    
    # Profile management
    path('profile/', views.StudentProfileView.as_view(), name='profile'),
    path('profile/edit/', views.StudentProfileUpdateView.as_view(), name='profile_edit'),
]