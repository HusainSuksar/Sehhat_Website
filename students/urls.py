from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Student management (only existing views)
    path('students/', views.StudentListView.as_view(), name='student_list'),
    path('students/<int:pk>/', views.StudentDetailView.as_view(), name='student_detail'),
    
    # Course management (only existing views)
    path('courses/', views.CourseListView.as_view(), name='course_list'),
    path('courses/<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    
    # Enrollment (only existing views)
    path('courses/<int:course_id>/enroll/', views.enroll_in_course, name='enroll_course'),
    
    # Assignments and submissions (only existing views)
    path('assignments/<int:assignment_id>/', views.assignment_detail, name='assignment_detail'),
    
    # Grades and academic records (only existing views)
    path('grades/', views.my_grades, name='my_grades'),
    
    # Schedule and attendance (only existing views)
    path('schedule/', views.my_schedule, name='my_schedule'),
    path('attendance/', views.attendance_record, name='attendance_record'),
    
    # Analytics and reports (only existing views)
    path('analytics/', views.student_analytics, name='analytics'),
    path('export/', views.export_student_data, name='export_data'),
]