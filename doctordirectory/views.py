from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import datetime, timedelta, date
from django.core.mail import send_mail
from django.conf import settings

from .models import (
    Doctor, DoctorSchedule, MedicalService, Patient, Appointment, PatientLog
)
from .forms import (
    DoctorForm, DoctorScheduleForm, AppointmentForm
)
from accounts.models import User
from mahalshifa.models import Doctor as MahalShifaDoctor, MedicalRecord


class DoctorAccessMixin(UserPassesTestMixin):
    """Mixin to check if user has access to doctor management"""
    def test_func(self):
        return (self.request.user.is_admin or 
                self.request.user.is_doctor)


@login_required
def dashboard(request):
    """Doctor directory dashboard with comprehensive statistics"""
    user = request.user
    
    # Security check: Only allow doctors and admins
    if not (user.is_admin or user.is_doctor):
        messages.error(request, 'You do not have permission to access the doctor dashboard.')
        return redirect('accounts:profile')
    
    # Get doctor profile from mahalshifa
    try:
        doctor_profile = MahalShifaDoctor.objects.get(user=user)
    except MahalShifaDoctor.DoesNotExist:
        doctor_profile = None
    
    # Get patient profile if user is also a patient
    try:
        # patient_profile is a RelatedManager, need to get the actual Patient instance
        patient_profile = user.patient_profile.first() if hasattr(user, 'patient_profile') else None
    except AttributeError:
        patient_profile = None
    except Exception as e:
        print(f"Error loading patient profile for user {user.username}: {e}")
        patient_profile = None
    
    # Global statistics (for all users) - Use mahalshifa doctors
    total_doctors = MahalShifaDoctor.objects.filter(user__is_active=True).count()
    total_patients_global = Patient.objects.count()
    total_appointments_global = Appointment.objects.count()
    total_medical_records = MedicalRecord.objects.count()
    
    # Weekly statistics
    week_start = timezone.now().date() - timedelta(days=7)
    weekly_appointments = Appointment.objects.filter(
        appointment_date__gte=week_start
    ).count()
    weekly_patients = Patient.objects.filter(
        appointments__appointment_date__gte=week_start
    ).distinct().count()
    
    # Monthly statistics
    month_start = timezone.now().date() - timedelta(days=30)
    monthly_appointments = Appointment.objects.filter(
        appointment_date__gte=month_start
    ).count()
    monthly_patients = Patient.objects.filter(
        appointments__appointment_date__gte=month_start
    ).distinct().count()
    
    # Doctor-specific statistics
    if doctor_profile:
        # For mahalshifa doctors, we need to check if they have corresponding doctordirectory records
        try:
            # Try to get the corresponding doctordirectory doctor
            doctordirectory_doctor = Doctor.objects.get(user=user)
            total_patients = Patient.objects.filter(appointments__doctor=doctordirectory_doctor).distinct().count()
            total_appointments = Appointment.objects.filter(doctor=doctordirectory_doctor).count()
            today_appointments = Appointment.objects.filter(
                doctor=doctordirectory_doctor,
                appointment_date=timezone.now().date()
            ).count()
            pending_appointments = Appointment.objects.filter(
                doctor=doctordirectory_doctor,
                status='scheduled'
            ).count()
            weekly_doctor_appointments = Appointment.objects.filter(
                doctor=doctordirectory_doctor,
                appointment_date__gte=week_start
            ).count()
            monthly_doctor_appointments = Appointment.objects.filter(
                doctor=doctordirectory_doctor,
                appointment_date__gte=month_start
            ).count()
        except Doctor.DoesNotExist:
            # If no doctordirectory doctor exists, show 0 stats
            total_patients = 0
            total_appointments = 0
            today_appointments = 0
            pending_appointments = 0
            weekly_doctor_appointments = 0
            monthly_doctor_appointments = 0
    else:
        total_patients = 0
        total_appointments = 0
        today_appointments = 0
        pending_appointments = 0
        weekly_doctor_appointments = 0
        monthly_doctor_appointments = 0
    
    # Get recent appointments
    if doctor_profile:
        try:
            doctordirectory_doctor = Doctor.objects.get(user=user)
            recent_appointments = Appointment.objects.filter(
                doctor=doctordirectory_doctor
            ).select_related('patient__user').order_by('-appointment_date')[:5]
        except Doctor.DoesNotExist:
            recent_appointments = []
    else:
        recent_appointments = Appointment.objects.all().select_related('patient__user', 'doctor').order_by('-appointment_date')[:5]
    
    # Get recent patient logs
    if doctor_profile:
        try:
            doctordirectory_doctor = Doctor.objects.get(user=user)
            recent_logs = PatientLog.objects.filter(
                seen_by=doctordirectory_doctor
            ).order_by('-timestamp')[:10]
        except Doctor.DoesNotExist:
            recent_logs = []
    else:
        recent_logs = PatientLog.objects.all().order_by('-timestamp')[:10]
    
    # Get top specialties from mahalshifa doctors
    top_specialties = MahalShifaDoctor.objects.values('specialization').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Get appointment status distribution
    appointment_status = Appointment.objects.values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Get recent medical records
    if doctor_profile:
        try:
            doctordirectory_doctor = Doctor.objects.get(user=user)
            recent_medical_records = MedicalRecord.objects.filter(
                doctor=doctordirectory_doctor
            ).select_related('patient').order_by('-created_at')[:5]
        except Doctor.DoesNotExist:
            recent_medical_records = []
    else:
        recent_medical_records = MedicalRecord.objects.all().select_related('patient', 'doctor').order_by('-created_at')[:5]
    
    # Ensure all stats are integers, not None
    context = {
        'doctor_profile': doctor_profile,
        'patient_profile': patient_profile,
        
        # Global statistics
        'total_doctors': total_doctors or 0,
        'total_patients_global': total_patients_global or 0,
        'total_appointments_global': total_appointments_global or 0,
        'total_medical_records': total_medical_records or 0,
        
        # Weekly statistics
        'weekly_appointments': weekly_appointments or 0,
        'weekly_patients': weekly_patients or 0,
        
        # Monthly statistics
        'monthly_appointments': monthly_appointments or 0,
        'monthly_patients': monthly_patients or 0,
        
        # Doctor-specific statistics
        'total_patients': total_patients or 0,
        'total_appointments': total_appointments or 0,
        'todays_appointments': today_appointments or 0,
        'pending_appointments': pending_appointments or 0,
        'weekly_doctor_appointments': weekly_doctor_appointments or 0,
        'monthly_doctor_appointments': monthly_doctor_appointments or 0,
        
        # Recent data
        'recent_appointments': recent_appointments,
        'recent_logs': recent_logs,
        'recent_medical_records': recent_medical_records,
        
        # Analytics data
        'top_specialties': top_specialties,
        'appointment_status': appointment_status,
    }
    
    return render(request, 'doctordirectory/dashboard.html', context)


class DoctorListView(LoginRequiredMixin, ListView):
    """List all doctors with search and filtering"""
    model = Doctor
    template_name = 'doctordirectory/doctor_list.html'
    context_object_name = 'doctors'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Doctor.objects.select_related('user', 'assigned_moze')
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(specialty__icontains=search) |
                Q(assigned_moze__name__icontains=search)
            )
        
        # Filter by specialty
        specialty = self.request.GET.get('specialty')
        if specialty:
            queryset = queryset.filter(specialty__icontains=specialty)
        
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
            specialty__isnull=False
        ).exclude(specialty='').values_list('specialty', flat=True).distinct()
        
        return context


doctor_list = DoctorListView.as_view()


class DoctorDetailView(LoginRequiredMixin, DetailView):
    """Detailed view of a doctor with schedule and appointment booking"""
    model = Doctor
    template_name = 'doctordirectory/doctor_detail.html'
    context_object_name = 'doctor'
    
    def get_queryset(self):
        return Doctor.objects.select_related(
            'user', 
            'user__profile',
            'assigned_moze'
        ).prefetch_related(
            'schedules',
            'appointments__patient__user',
            'medical_services'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doctor = self.object
        today = timezone.now().date()
        
        # Get upcoming availability with optimized query (limit to 7 days ahead)
        next_week = today + timedelta(days=7)
        upcoming_availability = DoctorSchedule.objects.filter(
            doctor=doctor,
            date__range=[today, next_week],
            is_available=True
        ).select_related('doctor').order_by('date', 'start_time')[:10]  # Limit results
        context['upcoming_availability'] = upcoming_availability
        
        # Recent appointments with optimized query (limit to 5)
        recent_appointments = Appointment.objects.filter(
            doctor=doctor,
            status='completed'
        ).select_related(
            'patient__user', 
            'patient__user__profile'
        ).order_by('-appointment_date')[:5]  # Limit to 5 most recent
        context['recent_appointments'] = recent_appointments
        
        # Check if current user can book appointment
        context['can_book_appointment'] = (
            self.request.user.is_authenticated and 
            not self.request.user.is_doctor
        )
        
        # Get doctor's services with optimized query
        services = MedicalService.objects.filter(
            doctor=doctor,
            is_available=True
        ).order_by('name')[:10]  # Limit to 10 services
        context['services'] = services
        
        # Add basic stats (cached for performance)
        context['stats'] = {
            'total_appointments': Appointment.objects.filter(doctor=doctor).count(),
            'completed_appointments': Appointment.objects.filter(
                doctor=doctor, 
                status='completed'
            ).count(),
            'available_today': DoctorSchedule.objects.filter(
                doctor=doctor,
                date=today,
                is_available=True
            ).exists()
        }
        
        return context


doctor_detail = DoctorDetailView.as_view()


@login_required
def patient_list(request):
    """List patients for doctors with optimized queries"""
    user = request.user
    
    if not (user.is_doctor or user.is_admin):
        messages.error(request, "You don't have permission to view patients.")
        return redirect('/')
    
    # Get accessible patients with optimized queries
    if user.is_doctor:
        try:
            # Use select_related to get doctor profile efficiently
            doctor = Doctor.objects.select_related('user', 'assigned_moze').get(user=user)
            # Optimized query with distinct and select_related
            patients = Patient.objects.filter(
                appointments__doctor=doctor
            ).distinct().select_related(
                'user', 
                'user__profile'
            ).prefetch_related(
                'appointments__doctor__user'
            ).order_by('user__first_name', 'user__last_name')
        except Doctor.DoesNotExist:
            patients = Patient.objects.none()
    else:
        # Admin/coordinator view with optimized queries
        patients = Patient.objects.select_related(
            'user', 
            'user__profile'
        ).order_by('user__first_name', 'user__last_name')
    
    # Search functionality with optimized query
    search = request.GET.get('search', '').strip()
    if search:
        patients = patients.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(user__its_id__icontains=search)
        )
    
    # Use efficient pagination with select_related
    paginator = Paginator(patients, 15)  # Reduced page size for better performance
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except Exception:
        page_obj = paginator.get_page(1)
    
    # Get total count efficiently (use cached count if possible)
    try:
        total_patients = patients.count()
    except Exception:
        total_patients = 0
    
    context = {
        'patients': page_obj,
        'search_query': search,
        'total_patients': total_patients,
        'page_obj': page_obj,  # Add page object for better pagination
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
            if patient.user != user:
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
        try:
            doctor = get_object_or_404(Doctor, pk=doctor_id)
            # Ensure doctor is available for appointments
            if not doctor.is_available:
                messages.warning(request, 'This doctor is currently not available for appointments.')
                return redirect('doctordirectory:dashboard')
        except Exception as e:
            messages.error(request, 'Doctor not found.')
            return redirect('doctordirectory:dashboard')
    else:
        doctor = None
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST, doctor=doctor, user=request.user)
        if form.is_valid():
            appointment = form.save(commit=False)
            
            # If no patient was selected in the form and current user is a patient, 
            # automatically assign them as the patient
            if not appointment.patient and hasattr(request.user, 'patient_profile'):
                try:
                    # Get the patient instance (patient_profile is a RelatedManager)
                    appointment.patient = request.user.patient_profile.get()
                except Patient.DoesNotExist:
                    # If current user has no patient profile, they must select a patient
                    if not appointment.patient:
                        messages.error(request, 'Please select a patient for this appointment.')
                        return render(request, 'doctordirectory/appointment_form.html', {'form': form, 'doctor': doctor})
                except Patient.MultipleObjectsReturned:
                    # If multiple patient profiles exist, get the first one
                    appointment.patient = request.user.patient_profile.first()
            
            # Ensure a patient is assigned
            if not appointment.patient:
                messages.error(request, 'Please select a patient for this appointment.')
                return render(request, 'doctordirectory/appointment_form.html', {'form': form, 'doctor': doctor})
            
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
        form = AppointmentForm(doctor=doctor, user=request.user)
    
    context = {
        'form': form,
        'doctor': doctor,
        'title': 'Book Appointment' if doctor else 'Create Appointment'
    }
    
    return render(request, 'doctordirectory/appointment_form.html', context)


@login_required
def appointment_detail(request, pk):
    """Display appointment details"""
    appointment = get_object_or_404(Appointment, pk=pk)
    
    # Check permissions - users can only view their own appointments or if they're admin/doctor
    if not (request.user.is_admin or 
            (hasattr(request.user, 'doctor_profile') and appointment.doctor.user == request.user) or
            (hasattr(request.user, 'patient_profile') and appointment.patient.user == request.user)):
        messages.error(request, 'You do not have permission to view this appointment.')
        return redirect('doctordirectory:dashboard')
    
    context = {
        'appointment': appointment,
        'title': 'Appointment Details'
    }
    
    return render(request, 'doctordirectory/appointment_detail.html', context)


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
    
    availabilities = DoctorSchedule.objects.filter(
        doctor=doctor,
        is_available=True
    ).order_by('date', 'start_time')
    
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
    """Add medical notes for a patient"""
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
        from .forms import MedicalRecordForm
        form = MedicalRecordForm(request.POST)
        if form.is_valid():
            # Since we removed MedicalRecord model, we'll add notes to the most recent appointment
            notes = form.cleaned_data['notes']
            diagnosis = form.cleaned_data.get('diagnosis', '')
            treatment = form.cleaned_data.get('treatment', '')
            
            # Find the most recent appointment for this patient with this doctor
            appointment = Appointment.objects.filter(
                patient=patient,
                doctor=doctor
            ).order_by('-appointment_date', '-appointment_time').first()
            
            if appointment:
                # Combine the notes
                medical_notes = f"DIAGNOSIS: {diagnosis}\n\nTREATMENT: {treatment}\n\nNOTES: {notes}"
                if appointment.notes:
                    appointment.notes += f"\n\n--- Medical Record Added ---\n{medical_notes}"
                else:
                    appointment.notes = medical_notes
                appointment.save()
                
                messages.success(request, 'Medical notes added to appointment successfully!')
            else:
                messages.warning(request, 'No appointment found to attach medical notes.')
            
            return redirect('doctordirectory:patient_detail', pk=patient.pk)
    else:
        from .forms import MedicalRecordForm
        form = MedicalRecordForm()
    
    context = {
        'form': form,
        'patient': patient,
        'doctor': doctor,
    }
    
    return render(request, 'doctordirectory/medical_record_form.html', context)


@login_required
def doctor_analytics(request):
    """Analytics dashboard for doctors - optimized for performance"""
    user = request.user
    
    if not (user.is_doctor or user.is_admin):
        messages.error(request, "You don't have permission to view analytics.")
        return redirect('/')
    
    # Time period filter with reasonable limits
    period = request.GET.get('period', '30')
    try:
        days = min(int(period), 365)  # Limit to 1 year max for performance
    except ValueError:
        days = 30
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Get base appointment queryset with optimized queries
    if user.is_doctor:
        try:
            doctor = Doctor.objects.select_related('user', 'assigned_moze').get(user=user)
            # Use select_related for better performance
            appointments = Appointment.objects.filter(
                doctor=doctor,
                appointment_date__range=[start_date, end_date]
            ).select_related('patient__user', 'doctor__user')
        except Doctor.DoesNotExist:
            appointments = Appointment.objects.none()
    else:
        # Admin view - all appointments with optimized query
        appointments = Appointment.objects.filter(
            appointment_date__range=[start_date, end_date]
        ).select_related('patient__user', 'doctor__user')
    
    # Use aggregate queries for better performance
    from django.db.models import Count, Q
    
    # Get all analytics data in a single query using aggregation
    analytics_aggregates = appointments.aggregate(
        total_appointments=Count('id'),
        completed_appointments=Count('id', filter=Q(status='completed')),
        pending_appointments=Count('id', filter=Q(status='pending')),
        cancelled_appointments=Count('id', filter=Q(status='cancelled'))
    )
    
    # Calculate completion rate
    total = analytics_aggregates['total_appointments']
    completed = analytics_aggregates['completed_appointments']
    completion_rate = round((completed / total) * 100, 1) if total > 0 else 0
    
    analytics_data = {
        **analytics_aggregates,
        'completion_rate': completion_rate
    }
    
    # Optimize daily data with a single query using aggregation
    from django.db.models.functions import TruncDate
    
    # Get daily appointment counts in a single query
    daily_counts = appointments.extra(
        select={'day': 'DATE(appointment_date)'}
    ).values('day').annotate(
        appointments=Count('id')
    ).order_by('day')
    
    # Convert to dictionary for fast lookup
    daily_dict = {item['day'].strftime('%Y-%m-%d'): item['appointments'] for item in daily_counts}
    
    # Build daily data array (limit to reasonable size)
    daily_data = []
    for i in range(min(days, 90)):  # Limit to 90 days max for performance
        date = start_date + timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        daily_data.append({
            'date': date_str,
            'appointments': daily_dict.get(date_str, 0)
        })
    
    context = {
        'analytics_data': analytics_data,
        'daily_data': daily_data,
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
        'max_period': min(days, 90),  # Let template know the actual period used
    }
    
    return render(request, 'doctordirectory/analytics.html', context)
