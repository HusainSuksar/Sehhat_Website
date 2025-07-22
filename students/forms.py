from django import forms
from django.contrib.auth import get_user_model
from .models import Student, Course, Enrollment, Assignment, Grade, Attendance

User = get_user_model()


class StudentForm(forms.ModelForm):
    """Form for creating and editing student profiles"""
    
    class Meta:
        model = Student
        fields = [
            'student_id', 'year', 'major', 'gpa', 'enrollment_status', 
            'emergency_contact_name', 'emergency_contact_phone', 'address'
        ]
        widgets = {
            'student_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter student ID'
            }),
            'year': forms.Select(attrs={
                'class': 'form-control'
            }),
            'major': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter major/field of study'
            }),
            'gpa': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '4.0'
            }),
            'enrollment_status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'emergency_contact_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency contact name'
            }),
            'emergency_contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency contact phone'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Student address'
            })
        }


class CourseForm(forms.ModelForm):
    """Form for creating and editing courses"""
    
    class Meta:
        model = Course
        fields = [
            'code', 'name', 'description', 'credits', 'department',
            'instructor', 'semester', 'year', 'capacity', 'prerequisites'
        ]
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Course code (e.g., CS101)'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Course name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Course description'
            }),
            'credits': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '6'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Department'
            }),
            'instructor': forms.Select(attrs={
                'class': 'form-control'
            }),
            'semester': forms.Select(attrs={
                'class': 'form-control'
            }),
            'year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '2020',
                'max': '2030'
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '500'
            }),
            'prerequisites': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Prerequisites (comma separated)'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter instructors to only teachers/staff
        self.fields['instructor'].queryset = User.objects.filter(
            role__in=['teacher', 'admin', 'staff'],
            is_active=True
        )


class EnrollmentForm(forms.ModelForm):
    """Form for student enrollment"""
    
    class Meta:
        model = Enrollment
        fields = ['course', 'enrollment_type']
        widgets = {
            'course': forms.Select(attrs={
                'class': 'form-control'
            }),
            'enrollment_type': forms.Select(attrs={
                'class': 'form-control'
            })
        }
    
    def __init__(self, *args, **kwargs):
        student = kwargs.pop('student', None)
        super().__init__(*args, **kwargs)
        
        if student:
            # Exclude courses already enrolled in
            enrolled_courses = student.enrollments.values_list('course', flat=True)
            self.fields['course'].queryset = Course.objects.exclude(
                id__in=enrolled_courses
            ).filter(is_active=True)


class AssignmentForm(forms.ModelForm):
    """Form for creating assignments"""
    
    class Meta:
        model = Assignment
        fields = [
            'title', 'description', 'course', 'due_date', 'total_points',
            'assignment_type', 'instructions'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Assignment title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Assignment description'
            }),
            'course': forms.Select(attrs={
                'class': 'form-control'
            }),
            'due_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'total_points': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '1000'
            }),
            'assignment_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Detailed instructions for students'
            })
        }


class GradeForm(forms.ModelForm):
    """Form for entering grades"""
    
    class Meta:
        model = Grade
        fields = ['student', 'assignment', 'points_earned', 'feedback']
        widgets = {
            'student': forms.Select(attrs={
                'class': 'form-control'
            }),
            'assignment': forms.Select(attrs={
                'class': 'form-control'
            }),
            'points_earned': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.5'
            }),
            'feedback': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Feedback for student'
            })
        }
    
    def __init__(self, *args, **kwargs):
        assignment = kwargs.pop('assignment', None)
        super().__init__(*args, **kwargs)
        
        if assignment:
            # Filter students enrolled in the course
            enrolled_students = Student.objects.filter(
                enrollments__course=assignment.course
            )
            self.fields['student'].queryset = enrolled_students
            self.fields['assignment'].queryset = Assignment.objects.filter(
                id=assignment.id
            )
            self.fields['points_earned'].widget.attrs['max'] = str(assignment.total_points)


class AttendanceForm(forms.ModelForm):
    """Form for marking attendance"""
    
    class Meta:
        model = Attendance
        fields = ['student', 'course', 'date', 'status', 'notes']
        widgets = {
            'student': forms.Select(attrs={
                'class': 'form-control'
            }),
            'course': forms.Select(attrs={
                'class': 'form-control'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Optional notes'
            })
        }


class StudentFilterForm(forms.Form):
    """Form for filtering students"""
    
    year = forms.ChoiceField(
        choices=[('', 'All Years')] + Student.YEAR_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    major = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by major'
        })
    )
    
    enrollment_status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + Student.ENROLLMENT_STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search students...'
        })
    )
