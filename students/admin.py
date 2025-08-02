from django.contrib import admin
from django.utils.html import format_html
from .models import Student, Course, Grade


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['user', 'student_id', 'academic_level', 'enrollment_status', 'enrollment_date', 'expected_graduation', 'get_moze']
    list_filter = ['academic_level', 'enrollment_status', 'enrollment_date']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'student_id']
    ordering = ['user__last_name', 'user__first_name']
    
    def get_moze(self, obj):
        """Display associated moze if any"""
        # This would need to be implemented based on your moze relationship
        return 'N/A'
    get_moze.short_description = 'Associated Moze'


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'credits', 'is_active']
    list_filter = ['is_active', 'credits']
    search_fields = ['name', 'code', 'description']
    ordering = ['name']


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'points', 'max_points', 'percentage', 'letter_grade', 'date_graded']
    list_filter = ['date_graded', 'letter_grade']
    search_fields = ['student__user__first_name', 'student__user__last_name', 'course__name']
    ordering = ['-date_graded']
