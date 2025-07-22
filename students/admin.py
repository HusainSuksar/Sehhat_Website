from django.contrib import admin
from django.utils.html import format_html
from .models import Student, Course, Enrollment, Assignment, Grade, Attendance


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 0
    readonly_fields = ['enrolled_at']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'student_id', 'year', 'major', 'gpa', 
        'enrollment_status', 'enrollment_count'
    ]
    list_filter = ['year', 'enrollment_status', 'major']
    search_fields = [
        'user__username', 'user__first_name', 'user__last_name', 
        'student_id', 'major'
    ]
    readonly_fields = ['created_at', 'updated_at']
    inlines = [EnrollmentInline]
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Academic Information', {
            'fields': ('student_id', 'year', 'major', 'gpa', 'enrollment_status')
        }),
        ('Contact Information', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'address')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def enrollment_count(self, obj):
        return obj.enrollments.count()
    enrollment_count.short_description = 'Enrollments'


class GradeInline(admin.TabularInline):
    model = Grade
    extra = 0
    readonly_fields = ['graded_at']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'name', 'department', 'instructor', 'credits',
        'semester', 'year', 'enrollment_count', 'is_active'
    ]
    list_filter = ['department', 'semester', 'year', 'is_active', 'credits']
    search_fields = ['code', 'name', 'department', 'instructor__username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'description', 'department')
        }),
        ('Academic Details', {
            'fields': ('credits', 'instructor', 'prerequisites')
        }),
        ('Schedule', {
            'fields': ('semester', 'year', 'capacity')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def enrollment_count(self, obj):
        return obj.enrollments.count()
    enrollment_count.short_description = 'Enrolled'


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = [
        'student', 'course', 'enrollment_type', 'grade', 'enrolled_at'
    ]
    list_filter = ['enrollment_type', 'course__semester', 'course__year', 'enrolled_at']
    search_fields = [
        'student__user__username', 'student__student_id', 
        'course__code', 'course__name'
    ]
    readonly_fields = ['enrolled_at']


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'course', 'assignment_type', 'due_date', 
        'total_points', 'submission_count'
    ]
    list_filter = ['assignment_type', 'course', 'due_date']
    search_fields = ['title', 'course__code', 'course__name']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [GradeInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'course')
        }),
        ('Assignment Details', {
            'fields': ('assignment_type', 'due_date', 'total_points')
        }),
        ('Instructions', {
            'fields': ('instructions',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def submission_count(self, obj):
        return obj.grades.count()
    submission_count.short_description = 'Submissions'


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = [
        'student', 'assignment', 'points_earned', 'total_points',
        'percentage', 'letter_grade', 'graded_at'
    ]
    list_filter = ['assignment__course', 'graded_at', 'letter_grade']
    search_fields = [
        'student__user__username', 'student__student_id',
        'assignment__title', 'assignment__course__code'
    ]
    readonly_fields = ['graded_at', 'percentage']
    
    def total_points(self, obj):
        return obj.assignment.total_points
    total_points.short_description = 'Total Points'
    
    def percentage(self, obj):
        if obj.assignment.total_points > 0:
            pct = (obj.points_earned / obj.assignment.total_points) * 100
            return f"{pct:.1f}%"
        return "N/A"
    percentage.short_description = 'Percentage'


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = [
        'student', 'course', 'date', 'status', 'marked_by'
    ]
    list_filter = ['status', 'course', 'date']
    search_fields = [
        'student__user__username', 'student__student_id',
        'course__code', 'course__name'
    ]
    readonly_fields = ['marked_at']
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.marked_by = request.user
        super().save_model(request, obj, form, change)
