from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q, Count, Avg
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta, date
from django.core.mail import send_mail
from django.conf import settings

from .models import (
    Doctor, DoctorSchedule, PatientLog, DoctorAvailability,
    MedicalService, Patient, Appointment, MedicalRecord, Prescription, LabTest, VitalSigns
)
from .forms import (
    DoctorForm, DoctorScheduleForm, PatientLogForm, DoctorAvailabilityForm,
    AppointmentForm, MedicalRecordForm, PrescriptionForm, LabTestForm, VitalSignsForm
)
from accounts.models import User


class DoctorAccessMixin(UserPassesTestMixin):
    """Mixin to check if user has access to doctor management"""
    def test_func(self):
        return (self.request.user.is_admin or 
                self.request.user.is_doctor or 
                self.request.user.is_moze_coordinator)


@login_required
def dashboard(request):
    """Doctor directory dashboard"""
    user = request.user
    
    # Get doctor profile
    try:
        from .models import Doctor
        doctor_profile = Doctor.objects.get(user=user)
    except Doctor.DoesNotExist:
        # Create doctor profile if doesn't exist
        try:
            doctor_profile = Doctor.objects.create(
                user=user,
                name=user.get_full_name(),
                specialization="General Medicine"
            )
        except Exception as e:
            print(f"Error creating doctor profile for user {user.username}: {e}")
            doctor_profile = None
    
    # Get patient profile if user is also a patient
    try:
        patient_profile = user.patient_profile
    except AttributeError:
        patient_profile = None
    except Exception as e:
        print(f"Error loading patient profile for user {user.username}: {e}")
        patient_profile = None
    
    # Get statistics
    if doctor_profile:
        total_patients = Patient.objects.filter(appointments__doctor=doctor_profile).distinct().count()
        total_appointments = Appointment.objects.filter(doctor=doctor_profile).count()
        today_appointments = Appointment.objects.filter(
            doctor=doctor_profile,
            appointment_date=timezone.now().date()
        ).count()
        pending_appointments = Appointment.objects.filter(
            doctor=doctor_profile,
            status='scheduled'
        ).count()
    else:
        total_patients = 0
        total_appointments = 0
        today_appointments = 0
        pending_appointments = 0
    
    # Get recent appointments
    if doctor_profile:
        recent_appointments = Appointment.objects.filter(
            doctor=doctor_profile
        ).select_related('patient__user').order_by('-appointment_date')[:5]
    else:
        recent_appointments = []
    
    context = {
        'doctor_profile': doctor_profile,
        'patient_profile': patient_profile,
        'total_patients': total_patients,
        'total_appointments': total_appointments,
        'today_appointments': today_appointments,
        'pending_appointments': pending_appointments,
        'recent_appointments': recent_appointments,
    }
    
    return render(request, 'doctordirectory/dashboard.html', context)


class DoctorListView(LoginRequiredMixin, ListView):
    """List all doctors with search and filtering"""
    model = Doctor
    template_name = 'doctordirectory/doctor_list.html'
    context_object_name = 'doctors'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Doctor.objects.filter(is_verified=True).select_related('user', 'assigned_moze')
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(user__specialty__icontains=search) |
                Q(assigned_moze__name__icontains=search)
            )
        
        # Filter by specialty
        specialty = self.request.GET.get('specialty')
        if specialty:
            queryset = queryset.filter(user__specialty__icontains=specialty)
        
        # Filter by availability
        available = self.request.GET.get('available')
        if available == 'true':
            today = timezone.now().date()
            queryset = queryset.filter(
                availabilities__date=today,
                availabilities__is_available=True
            )
        
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['specialty_filter'] = self.request.GET.get('specialty', '')
        context['available_filter'] = self.request.GET.get('available', '')
        
        # Get unique specialties for filter
        context['specialties'] = Doctor.objects.filter(
            is_verified=True,
            user__specialty__isnull=False
        ).exclude(user__specialty='').values_list('user__specialty', flat=True).distinct()
        
        return context


doctor_list = DoctorListView.as_view()


class DoctorDetailView(LoginRequiredMixin, DetailView):
    """Detailed view of a doctor with schedule and appointment booking"""
    model = Doctor
    template_name = 'doctordirectory/doctor_detail.html'
    context_object_name = 'doctor'
    
    def get_queryset(self):
        return Doctor.objects.filter(is_verified=True).select_related('user', 'assigned_moze')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doctor = self.object
        today = timezone.now().date()
        
        # Get upcoming availability (use DoctorSchedule, not DoctorAvailability)
        upcoming_availability = DoctorSchedule.objects.filter(
            doctor=doctor,
            date=today,
            is_available=True
        ).order_by('date', 'start_time')[:7]  # Next 7 available slots
        context['upcoming_availability'] = upcoming_availability
        
        # Recent patient feedback/reviews (if implemented)
        context['recent_appointments'] = Appointment.objects.filter(
            doctor=doctor,
            status='completed'
        ).select_related('patient').order_by('-appointment_date')[:5]
        
        # Check if current user can book appointment
        context['can_book_appointment'] = (
            self.request.user.is_authenticated and 
            not self.request.user.is_doctor
        )
        
        # Get doctor's services
        context['services'] = MedicalService.objects.filter(
            doctor=doctor,
            is_active=True
        )
        
        return context


doctor_detail = DoctorDetailView.as_view()


@login_required
def patient_list(request):
    """List patients for doctors"""
    user = request.user
    
    if not (user.is_doctor or user.is_admin or user.is_moze_coordinator):
        messages.error(request, "You don't have permission to view patients.")
        return redirect('/')
    
    # Get accessible patients
    if user.is_doctor:
        try:
            doctor = Doctor.objects.get(user=user)
            patients = Patient.objects.filter(
                appointments__doctor=doctor
            ).distinct().select_related('user')
        except Doctor.DoesNotExist:
            patients = Patient.objects.none()
    else:
        patients = Patient.objects.all().select_related('user')
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        patients = patients.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(user__its_id__icontains=search) |
            Q(user__phone_number__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(patients, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'patients': page_obj,
        'search_query': search or '',
        'total_patients': patients.count(),
    }
    
    return render(request, 'doctordirectory/patient_list.html', context)


@login_required
def patient_detail(request, pk):
    """Detailed view of a specific patient"""
    try:
        patient = Patient.objects.get(pk=pk)
    except Patient.DoesNotExist:
        messages.error(request, "Patient not found.")
        return redirect('doctordirectory:patient_list')
    
    user = request.user
    
    # Check permissions
    if user.role == 'admin':
        pass  # Admin can see all patients
    elif user.role == 'doctor':
        try:
            from .models import Doctor
            doctor_profile = Doctor.objects.get(user=user)
            if not patient.appointments.filter(doctor=doctor_profile).exists():
                messages.error(request, "You don't have permission to view this patient.")
                return redirect('doctordirectory:patient_list')
        except Doctor.DoesNotExist:
            messages.error(request, "Doctor profile not found.")
            return redirect('doctordirectory:patient_list')
        except Exception as e:
            print(f"Error checking doctor permissions for user {user.username}: {e}")
            messages.error(request, "Error checking permissions.")
            return redirect('doctordirectory:patient_list')
    else:
        # Patients can only see their own record
        try:
            if patient.user_account != user:
                messages.error(request, "You don't have permission to view this patient.")
                return redirect('doctordirectory:patient_list')
        except AttributeError:
            messages.error(request, "You don't have permission to view this patient.")
            return redirect('doctordirectory:patient_list')
    
    # Get patient's appointments
    try:
        appointments = patient.appointments.select_related('doctor__user').order_by('-appointment_date')
    except Exception as e:
        print(f"Error loading appointments for patient {patient.pk}: {e}")
        appointments = []
    
    # Get patient's medical records
    try:
        medical_records = patient.medical_records.select_related('doctor__user').order_by('-created_at')
    except Exception as e:
        print(f"Error loading medical records for patient {patient.pk}: {e}")
        medical_records = []
    
    context = {
        'patient': patient,
        'appointments': appointments,
        'medical_records': medical_records,
    }
    
    return render(request, 'doctordirectory/patient_detail.html', context)


@login_required
def create_appointment(request, doctor_id=None):
    """Create a new appointment"""
    if doctor_id:
        doctor = get_object_or_404(Doctor, pk=doctor_id)
    else:
        doctor = None
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST, doctor=doctor)
        if form.is_valid():
            appointment = form.save(commit=False)
            
            # Set patient based on current user if they are a patient
            if hasattr(request.user, 'patient_profile'):
                appointment.patient = request.user.patient_profile
            
            appointment.save()
            
            # Send confirmation email
            if appointment.patient.user.email:
                try:
                    send_mail(
                        'Appointment Confirmation',
                        f'Your appointment with Dr. {appointment.doctor.user.get_full_name()} '
                        f'has been scheduled for {appointment.appointment_date} at {appointment.appointment_time}.',
                        settings.DEFAULT_FROM_EMAIL,
                        [appointment.patient.user.email],
                        fail_silently=True,
                    )
                except Exception:
                    pass
            
            messages.success(request, 'Appointment created successfully!')
            return redirect('doctordirectory:appointment_detail', pk=appointment.pk)
    else:
        form = AppointmentForm(doctor=doctor)
    
    context = {
        'form': form,
        'doctor': doctor,
        'title': 'Book Appointment' if doctor else 'Create Appointment'
    }
    
    return render(request, 'doctordirectory/appointment_form.html', context)


@login_required
def schedule_management(request):
    """Doctor schedule management"""
    user = request.user
    
    if not user.is_doctor:
        messages.error(request, "Only doctors can manage schedules.")
        return redirect('/')
    
    try:
        doctor = Doctor.objects.get(user=user)
    except Doctor.DoesNotExist:
        messages.error(request, "Doctor profile not found.")
        return redirect('/')
    
    # Get current month's schedule
    today = timezone.now().date()
    month_start = today.replace(day=1)
    if month_start.month == 12:
        month_end = month_start.replace(year=month_start.year + 1, month=1) - timedelta(days=1)
    else:
        month_end = month_start.replace(month=month_start.month + 1) - timedelta(days=1)
    
    schedules = DoctorSchedule.objects.filter(
        doctor=doctor,
        date__range=[month_start, month_end]
    ).order_by('date')
    
    availabilities = DoctorAvailability.objects.filter(
        doctor=doctor,
        is_active=True
    ).order_by('day_of_week', 'start_time')
    
    context = {
        'doctor': doctor,
        'schedules': schedules,
        'availabilities': availabilities,
        'month_start': month_start,
        'month_end': month_end,
        'today': today,
    }
    
    return render(request, 'doctordirectory/schedule_management.html', context)


@login_required
def add_medical_record(request, patient_id):
    """Add medical record for a patient"""
    user = request.user
    
    if not user.is_doctor:
        messages.error(request, "Only doctors can add medical records.")
        return redirect('/')
    
    patient = get_object_or_404(Patient, pk=patient_id)
    
    try:
        doctor = Doctor.objects.get(user=user)
    except Doctor.DoesNotExist:
        messages.error(request, "Doctor profile not found.")
        return redirect('/')
    
    if request.method == 'POST':
        form = MedicalRecordForm(request.POST)
        if form.is_valid():
            medical_record = form.save(commit=False)
            medical_record.patient = patient
            medical_record.doctor = doctor
            medical_record.save()
            
            messages.success(request, 'Medical record added successfully!')
            return redirect('doctordirectory:patient_detail', pk=patient.pk)
    else:
        form = MedicalRecordForm()
    
    context = {
        'form': form,
        'patient': patient,
        'doctor': doctor,
    }
    
    return render(request, 'doctordirectory/medical_record_form.html', context)


@login_required
def doctor_analytics(request):
    """Analytics dashboard for doctors"""
    user = request.user
    
    if not (user.is_doctor or user.is_admin):
        messages.error(request, "You don't have permission to view analytics.")
        return redirect('/')
    
    # Time period filter
    period = request.GET.get('period', '30')
    try:
        days = int(period)
    except ValueError:
        days = 30
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    if user.is_doctor:
        try:
            doctor = Doctor.objects.get(user=user)
            # Doctor-specific analytics
            appointments = Appointment.objects.filter(
                doctor=doctor,
                appointment_date__range=[start_date, end_date]
            )
        except Doctor.DoesNotExist:
            appointments = Appointment.objects.none()
    else:
        # Admin view - all appointments
        appointments = Appointment.objects.filter(
            appointment_date__range=[start_date, end_date]
        )
    
    # Analytics data
    analytics_data = {
        'total_appointments': appointments.count(),
        'completed_appointments': appointments.filter(status='completed').count(),
        'pending_appointments': appointments.filter(status='pending').count(),
        'cancelled_appointments': appointments.filter(status='cancelled').count(),
    }
    
    # Completion rate
    if analytics_data['total_appointments'] > 0:
        analytics_data['completion_rate'] = round(
            (analytics_data['completed_appointments'] / analytics_data['total_appointments']) * 100, 1
        )
    else:
        analytics_data['completion_rate'] = 0
    
    # Daily appointment data for chart
    daily_data = []
    for i in range(days):
        date = start_date + timedelta(days=i)
        daily_appointments = appointments.filter(appointment_date=date).count()
        daily_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'appointments': daily_appointments
        })
    
    context = {
        'analytics_data': analytics_data,
        'daily_data': daily_data,
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'doctordirectory/analytics.html', context)
