"""
Unit tests for the Students API
"""
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import date, time, timedelta
from decimal import Decimal
import json

from students.models import (
    Student, Course, Enrollment, Assignment, Submission, Grade, Schedule,
    Attendance, Announcement, StudentGroup, Event, LibraryRecord, Achievement,
    Scholarship, Fee, Payment, StudentProfile
)
from moze.models import Moze

User = get_user_model()


class StudentsAPITestCase(APITestCase):
    """Base test case for Students API tests"""
    
    def setUp(self):
        """Set up test data"""
        # Create users with different roles
        self.admin_user = User.objects.create_user(
            username='admin_user',
            email='admin@test.com',
            password='testpass123',
            role='badri_mahal_admin',
            first_name='Admin',
            last_name='User'
        )
        
        self.instructor_user = User.objects.create_user(
            username='instructor_user',
            email='instructor@test.com',
            password='testpass123',
            role='doctor',
            first_name='Dr. Jane',
            last_name='Smith'
        )
        
        self.student_user = User.objects.create_user(
            username='student_user',
            email='student@test.com',
            password='testpass123',
            role='student',
            first_name='John',
            last_name='Doe'
        )
        
        self.student_user2 = User.objects.create_user(
            username='student_user2',
            email='student2@test.com',
            password='testpass123',
            role='student',
            first_name='Jane',
            last_name='Smith'
        )
        
        # Create Moze for foreign key relationships
        self.moze = Moze.objects.create(
            name='Test Moze',
            location='Test Location',
            aamil=self.admin_user,
            address='123 Test Street'
        )
        
        # Create Student records
        self.student = Student.objects.create(
            user=self.student_user,
            student_id='STU001',
            academic_level='undergraduate',
            enrollment_status='active',
            enrollment_date=date.today() - timedelta(days=365),
            expected_graduation=date.today() + timedelta(days=730)
        )
        
        self.student2 = Student.objects.create(
            user=self.student_user2,
            student_id='STU002',
            academic_level='postgraduate',
            enrollment_status='active',
            enrollment_date=date.today() - timedelta(days=180)
        )
        
        # Create Course
        self.course = Course.objects.create(
            code='CS101',
            name='Introduction to Computer Science',
            description='Basic computer science concepts',
            credits=3,
            level='beginner',
            instructor=self.instructor_user,
            is_active=True,
            max_students=30
        )
        
        # Create Enrollment
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course,
            status='enrolled'
        )
        
        # Create Assignment
        self.assignment = Assignment.objects.create(
            course=self.course,
            title='First Assignment',
            description='Complete the first programming task',
            assignment_type='homework',
            due_date=timezone.now() + timedelta(days=7),
            max_points=100,
            is_published=True
        )
        
        # Create API client
        self.client = APIClient()


class StudentAPITests(StudentsAPITestCase):
    """Test Student API endpoints"""
    
    def test_list_students_admin(self):
        """Test admin can list all students"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('student_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_list_students_student_self_only(self):
        """Test student can only see themselves"""
        self.client.force_authenticate(user=self.student_user)
        url = reverse('student_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['student_id'], 'STU001')
    
    def test_create_student_admin(self):
        """Test admin can create student"""
        new_student_user = User.objects.create_user(
            username='new_student',
            email='newstudent@test.com',
            password='testpass123',
            role='student',
            first_name='New',
            last_name='Student'
        )
        
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('student_list_create')
        data = {
            'user_id': new_student_user.id,
            'student_id': 'STU003',
            'academic_level': 'undergraduate',
            'enrollment_status': 'active',
            'enrollment_date': str(date.today())
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Student.objects.count(), 3)
    
    def test_create_student_non_admin(self):
        """Test non-admin cannot create student"""
        self.client.force_authenticate(user=self.student_user)
        url = reverse('student_list_create')
        data = {
            'user_id': self.student_user2.id,
            'student_id': 'STU004',
            'academic_level': 'undergraduate'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_search_students(self):
        """Test student search functionality"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('student_search')
        response = self.client.get(url, {'student_id': 'STU001'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['student_id'], 'STU001')


class CourseAPITests(StudentsAPITestCase):
    """Test Course API endpoints"""
    
    def test_list_courses_admin(self):
        """Test admin can list all courses"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('course_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['code'], 'CS101')
    
    def test_list_courses_student(self):
        """Test student can see active courses and enrolled courses"""
        self.client.force_authenticate(user=self.student_user)
        url = reverse('course_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_course_instructor(self):
        """Test instructor can create course"""
        self.client.force_authenticate(user=self.instructor_user)
        url = reverse('course_list_create')
        data = {
            'code': 'CS102',
            'name': 'Advanced Programming',
            'description': 'Advanced programming concepts',
            'credits': 4,
            'level': 'intermediate',
            'instructor_id': self.instructor_user.id,
            'is_active': True,
            'max_students': 25
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 2)
    
    def test_create_course_student_forbidden(self):
        """Test student cannot create course"""
        self.client.force_authenticate(user=self.student_user)
        url = reverse('course_list_create')
        data = {
            'code': 'CS999',
            'name': 'Unauthorized Course',
            'credits': 3
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_search_courses(self):
        """Test course search functionality"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('course_search')
        response = self.client.get(url, {'code': 'CS101'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['code'], 'CS101')


class EnrollmentAPITests(StudentsAPITestCase):
    """Test Enrollment API endpoints"""
    
    def test_list_enrollments_admin(self):
        """Test admin can list all enrollments"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('enrollment_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_list_enrollments_student_own_only(self):
        """Test student can only see their own enrollments"""
        self.client.force_authenticate(user=self.student_user)
        url = reverse('enrollment_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['student']['student_id'], 'STU001')
    
    def test_create_enrollment_student(self):
        """Test student can enroll themselves"""
        # Create another course
        course2 = Course.objects.create(
            code='CS201',
            name='Data Structures',
            credits=3,
            level='intermediate',
            instructor=self.instructor_user,
            is_active=True,
            max_students=20
        )
        
        self.client.force_authenticate(user=self.student_user)
        url = reverse('enrollment_list_create')
        data = {
            'course_id': course2.id,
            'status': 'enrolled'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Enrollment.objects.filter(student=self.student).count(), 2)
    
    def test_create_enrollment_admin(self):
        """Test admin can enroll any student"""
        course2 = Course.objects.create(
            code='CS301',
            name='Algorithms',
            credits=3,
            level='advanced',
            instructor=self.instructor_user,
            is_active=True
        )
        
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('enrollment_list_create')
        data = {
            'student_id': self.student2.id,
            'course_id': course2.id,
            'status': 'enrolled'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Enrollment.objects.count(), 2)


class AssignmentAPITests(StudentsAPITestCase):
    """Test Assignment API endpoints"""
    
    def test_list_assignments_instructor(self):
        """Test instructor can list all assignments"""
        self.client.force_authenticate(user=self.instructor_user)
        url = reverse('assignment_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_list_assignments_student_enrolled_courses(self):
        """Test student can see assignments from enrolled courses"""
        self.client.force_authenticate(user=self.student_user)
        url = reverse('assignment_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'First Assignment')
    
    def test_create_assignment_instructor(self):
        """Test instructor can create assignment"""
        self.client.force_authenticate(user=self.instructor_user)
        url = reverse('assignment_list_create')
        data = {
            'course_id': self.course.id,
            'title': 'Second Assignment',
            'description': 'Complete the second task',
            'assignment_type': 'project',
            'due_date': (timezone.now() + timedelta(days=14)).isoformat(),
            'max_points': 150,
            'is_published': True
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Assignment.objects.count(), 2)
    
    def test_create_assignment_student_forbidden(self):
        """Test student cannot create assignment"""
        self.client.force_authenticate(user=self.student_user)
        url = reverse('assignment_list_create')
        data = {
            'course_id': self.course.id,
            'title': 'Unauthorized Assignment',
            'description': 'Should not be created',
            'assignment_type': 'homework'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class SubmissionAPITests(StudentsAPITestCase):
    """Test Submission API endpoints"""
    
    def test_list_submissions_student_own_only(self):
        """Test student can only see their own submissions"""
        # Create a submission
        submission = Submission.objects.create(
            assignment=self.assignment,
            student=self.student,
            content='My solution to the assignment',
            attempt_number=1
        )
        
        self.client.force_authenticate(user=self.student_user)
        url = reverse('student_submission_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['content'], 'My solution to the assignment')
    
    def test_list_submissions_instructor_course_submissions(self):
        """Test instructor can see submissions for their courses"""
        submission = Submission.objects.create(
            assignment=self.assignment,
            student=self.student,
            content='Student solution',
            attempt_number=1
        )
        
        self.client.force_authenticate(user=self.instructor_user)
        url = reverse('student_submission_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_submission_student(self):
        """Test student can create submission"""
        self.client.force_authenticate(user=self.student_user)
        url = reverse('student_submission_list_create')
        data = {
            'assignment_id': self.assignment.id,
            'content': 'Here is my solution',
            'attempt_number': 1
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Submission.objects.count(), 1)
    
    def test_create_submission_non_student_forbidden(self):
        """Test non-student cannot create submission"""
        self.client.force_authenticate(user=self.instructor_user)
        url = reverse('student_submission_list_create')
        data = {
            'assignment_id': self.assignment.id,
            'content': 'Should not be allowed',
            'attempt_number': 1
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class GradeAPITests(StudentsAPITestCase):
    """Test Grade API endpoints"""
    
    def test_list_grades_student_own_only(self):
        """Test student can only see their own grades"""
        grade = Grade.objects.create(
            student=self.student,
            course=self.course,
            assignment=self.assignment,
            points=85,
            max_points=100,
            graded_by=self.instructor_user,
            comments='Good work!'
        )
        
        self.client.force_authenticate(user=self.student_user)
        url = reverse('grade_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['points'], 85.0)
    
    def test_list_grades_instructor_graded_by_them(self):
        """Test instructor can see grades they created"""
        grade = Grade.objects.create(
            student=self.student,
            course=self.course,
            assignment=self.assignment,
            points=90,
            max_points=100,
            graded_by=self.instructor_user
        )
        
        self.client.force_authenticate(user=self.instructor_user)
        url = reverse('grade_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_grade_instructor(self):
        """Test instructor can create grade"""
        self.client.force_authenticate(user=self.instructor_user)
        url = reverse('grade_list_create')
        data = {
            'student_id': self.student.id,
            'course_id': self.course.id,
            'assignment_id': self.assignment.id,
            'points': 88,
            'max_points': 100,
            'comments': 'Excellent work!'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Grade.objects.count(), 1)
        
        # Check that graded_by is automatically set
        grade = Grade.objects.first()
        self.assertEqual(grade.graded_by, self.instructor_user)
    
    def test_create_grade_student_forbidden(self):
        """Test student cannot create grade"""
        self.client.force_authenticate(user=self.student_user)
        url = reverse('grade_list_create')
        data = {
            'student_id': self.student.id,
            'course_id': self.course.id,
            'points': 100,
            'max_points': 100
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ScheduleAPITests(StudentsAPITestCase):
    """Test Schedule API endpoints"""
    
    def test_list_schedules_student_enrolled_courses(self):
        """Test student can see schedules for enrolled courses"""
        schedule = Schedule.objects.create(
            course=self.course,
            day_of_week='monday',
            start_time=time(9, 0),
            end_time=time(10, 30),
            room='Room 101',
            building='Science Building',
            effective_from=date.today(),
            is_active=True
        )
        
        self.client.force_authenticate(user=self.student_user)
        url = reverse('schedule_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['room'], 'Room 101')
    
    def test_create_schedule_admin(self):
        """Test admin can create schedule"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('schedule_list_create')
        data = {
            'course_id': self.course.id,
            'day_of_week': 'wednesday',
            'start_time': '14:00:00',
            'end_time': '15:30:00',
            'room': 'Lab 202',
            'building': 'Tech Building',
            'effective_from': str(date.today()),
            'is_active': True
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Schedule.objects.count(), 1)  # Only the schedule we just created
    
    def test_create_schedule_student_forbidden(self):
        """Test student cannot create schedule"""
        self.client.force_authenticate(user=self.student_user)
        url = reverse('schedule_list_create')
        data = {
            'course_id': self.course.id,
            'day_of_week': 'friday',
            'start_time': '10:00:00',
            'end_time': '11:30:00'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AttendanceAPITests(StudentsAPITestCase):
    """Test Attendance API endpoints"""
    
    def test_list_attendance_student_own_only(self):
        """Test student can only see their own attendance"""
        attendance = Attendance.objects.create(
            student=self.student,
            course=self.course,
            date=date.today(),
            status='present',
            recorded_by=self.instructor_user
        )
        
        self.client.force_authenticate(user=self.student_user)
        url = reverse('attendance_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['status'], 'present')
    
    def test_create_attendance_instructor(self):
        """Test instructor can record attendance"""
        self.client.force_authenticate(user=self.instructor_user)
        url = reverse('attendance_list_create')
        data = {
            'student_id': self.student.id,
            'course_id': self.course.id,
            'date': str(date.today()),
            'status': 'present'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Attendance.objects.count(), 1)
        
        # Check that recorded_by is automatically set
        attendance = Attendance.objects.first()
        self.assertEqual(attendance.recorded_by, self.instructor_user)
    
    def test_create_attendance_student_forbidden(self):
        """Test student cannot record attendance"""
        self.client.force_authenticate(user=self.student_user)
        url = reverse('attendance_list_create')
        data = {
            'student_id': self.student.id,
            'course_id': self.course.id,
            'date': str(date.today()),
            'status': 'present'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AnnouncementAPITests(StudentsAPITestCase):
    """Test Announcement API endpoints"""
    
    def test_list_announcements_student_relevant_only(self):
        """Test student sees relevant announcements"""
        # Global announcement
        global_announcement = Announcement.objects.create(
            title='Global Announcement',
            content='Important news for everyone',
            is_global=True,
            is_published=True,
            author=self.admin_user
        )
        
        # Course-specific announcement
        course_announcement = Announcement.objects.create(
            title='Course Announcement',
            content='Course-specific news',
            course=self.course,
            is_published=True,
            author=self.instructor_user
        )
        
        self.client.force_authenticate(user=self.student_user)
        url = reverse('announcement_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_create_announcement_instructor(self):
        """Test instructor can create announcement"""
        self.client.force_authenticate(user=self.instructor_user)
        url = reverse('announcement_list_create')
        data = {
            'title': 'New Assignment Posted',
            'content': 'Please check the new assignment in CS101',
            'course_id': self.course.id,
            'is_published': True,
            'is_urgent': False
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Announcement.objects.count(), 1)
        
        # Check that author is automatically set
        announcement = Announcement.objects.first()
        self.assertEqual(announcement.author, self.instructor_user)
    
    def test_create_announcement_student_forbidden(self):
        """Test student cannot create announcement"""
        self.client.force_authenticate(user=self.student_user)
        url = reverse('announcement_list_create')
        data = {
            'title': 'Student Announcement',
            'content': 'Should not be allowed',
            'is_published': True
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class StudentGroupAPITests(StudentsAPITestCase):
    """Test Student Group API endpoints"""
    
    def test_list_student_groups(self):
        """Test listing student groups"""
        group = StudentGroup.objects.create(
            name='Study Group 1',
            description='CS101 study group',
            group_type='study_group',
            leader=self.student,
            created_by=self.student_user,
            is_active=True,
            max_members=5
        )
        
        self.client.force_authenticate(user=self.student_user)
        url = reverse('student_group_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Study Group 1')
    
    def test_create_student_group(self):
        """Test creating student group"""
        self.client.force_authenticate(user=self.student_user)
        url = reverse('student_group_list_create')
        data = {
            'name': 'Programming Club',
            'description': 'For programming enthusiasts',
            'group_type': 'club',
            'leader_id': self.student.id,
            'is_active': True,
            'max_members': 10
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(StudentGroup.objects.count(), 1)
        
        # Check that created_by is automatically set
        group = StudentGroup.objects.first()
        self.assertEqual(group.created_by, self.student_user)


class EventAPITests(StudentsAPITestCase):
    """Test Event API endpoints"""
    
    def test_list_events_published_only(self):
        """Test students see only published events"""
        # Published event
        published_event = Event.objects.create(
            title='Tech Conference',
            description='Annual technology conference',
            event_type='academic',
            start_date=timezone.now() + timedelta(days=30),
            end_date=timezone.now() + timedelta(days=31),
            location='Main Auditorium',
            organizer=self.admin_user,
            is_published=True,
            is_cancelled=False
        )
        
        # Unpublished event
        unpublished_event = Event.objects.create(
            title='Private Meeting',
            description='Internal meeting',
            event_type='academic',
            start_date=timezone.now() + timedelta(days=15),
            end_date=timezone.now() + timedelta(days=15),
            organizer=self.admin_user,
            is_published=False
        )
        
        self.client.force_authenticate(user=self.student_user)
        url = reverse('event_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Tech Conference')
    
    def test_create_event_admin(self):
        """Test admin can create event"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('event_list_create')
        data = {
            'title': 'Workshop on AI',
            'description': 'Introduction to Artificial Intelligence',
            'event_type': 'workshop',
            'start_date': (timezone.now() + timedelta(days=45)).isoformat(),
            'end_date': (timezone.now() + timedelta(days=45, hours=3)).isoformat(),
            'location': 'Computer Lab',
            'is_published': True,
            'registration_required': True
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Event.objects.count(), 1)
    
    def test_create_event_student_forbidden(self):
        """Test student cannot create event"""
        self.client.force_authenticate(user=self.student_user)
        url = reverse('event_list_create')
        data = {
            'title': 'Student Event',
            'description': 'Should not be allowed',
            'event_type': 'social'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class StatisticsAPITests(StudentsAPITestCase):
    """Test Statistics API endpoints"""
    
    def test_student_stats_admin(self):
        """Test admin can access student statistics"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('student_stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_students', response.data)
        self.assertIn('active_students', response.data)
        self.assertIn('students_by_level', response.data)
        self.assertIn('students_by_status', response.data)
        self.assertEqual(response.data['total_students'], 2)
    
    def test_course_stats_admin(self):
        """Test admin can access course statistics"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('course_stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_courses', response.data)
        self.assertIn('active_courses', response.data)
        self.assertIn('total_enrollments', response.data)
        self.assertEqual(response.data['total_courses'], 1)
    
    def test_academic_stats_admin(self):
        """Test admin can access academic statistics"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('academic_stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_assignments', response.data)
        self.assertIn('submitted_assignments', response.data)
        self.assertIn('graded_assignments', response.data)
        self.assertIn('submission_rate', response.data)
    
    def test_stats_student_forbidden(self):
        """Test student cannot access statistics"""
        self.client.force_authenticate(user=self.student_user)
        url = reverse('student_stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class DashboardAPITests(StudentsAPITestCase):
    """Test Dashboard API endpoint"""
    
    def test_dashboard_admin(self):
        """Test admin can access comprehensive dashboard"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('students_dashboard_api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('student_stats', response.data)
        self.assertIn('course_stats', response.data)
        self.assertIn('academic_stats', response.data)
        self.assertIn('recent_enrollments', response.data)
    
    def test_dashboard_student(self):
        """Test student can access personal dashboard"""
        # Create some data for the student
        Grade.objects.create(
            student=self.student,
            course=self.course,
            assignment=self.assignment,
            points=85,
            max_points=100,
            graded_by=self.instructor_user
        )
        
        Achievement.objects.create(
            student=self.student,
            title='Dean\'s List',
            description='Made the dean\'s list',
            achievement_type='academic',
            date_awarded=date.today()
        )
        
        self.client.force_authenticate(user=self.student_user)
        url = reverse('students_dashboard_api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('my_enrollments', response.data)
        self.assertIn('my_assignments', response.data)
        self.assertIn('my_grades', response.data)
        self.assertIn('my_achievements', response.data)
        self.assertEqual(len(response.data['my_enrollments']), 1)
        self.assertEqual(len(response.data['my_grades']), 1)
        self.assertEqual(len(response.data['my_achievements']), 1)


class PermissionTests(StudentsAPITestCase):
    """Test API permissions"""
    
    def test_unauthenticated_access_denied(self):
        """Test unauthenticated users cannot access API"""
        url = reverse('student_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_student_cannot_access_other_student_data(self):
        """Test student cannot access another student's data"""
        self.client.force_authenticate(user=self.student_user2)
        url = reverse('student_detail', kwargs={'pk': self.student.id})
        response = self.client.get(url)
        
        # Student2 should not be able to see Student1's details
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_instructor_can_access_course_related_data(self):
        """Test instructor can access data related to their courses"""
        submission = Submission.objects.create(
            assignment=self.assignment,
            student=self.student,
            content='Test submission',
            attempt_number=1
        )
        
        self.client.force_authenticate(user=self.instructor_user)
        url = reverse('student_submission_detail', kwargs={'pk': submission.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class FilteringAndSearchTests(StudentsAPITestCase):
    """Test API filtering and search functionality"""
    
    def test_filter_students_by_level(self):
        """Test filtering students by academic level"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('student_list_create')
        response = self.client.get(url, {'academic_level': 'undergraduate'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['academic_level'], 'undergraduate')
    
    def test_search_students_by_name(self):
        """Test searching students by name"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('student_list_create')
        response = self.client.get(url, {'search': 'John'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_filter_courses_by_level(self):
        """Test filtering courses by level"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('course_list_create')
        response = self.client.get(url, {'level': 'beginner'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['level'], 'beginner')
    
    def test_order_assignments_by_due_date(self):
        """Test ordering assignments by due date"""
        # Create another assignment with different due date
        Assignment.objects.create(
            course=self.course,
            title='Second Assignment',
            description='Second task',
            assignment_type='quiz',
            due_date=timezone.now() + timedelta(days=3),
            max_points=50,
            is_published=True
        )
        
        self.client.force_authenticate(user=self.instructor_user)
        url = reverse('assignment_list_create')
        response = self.client.get(url, {'ordering': 'due_date'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        # Should be ordered by due date (ascending)
        self.assertEqual(response.data['results'][0]['title'], 'Second Assignment')