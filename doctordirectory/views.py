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
    
    # Security check: Allow doctors, admins, aamil, and moze coordinators
    if not (user.is_admin or user.is_doctor or user.is_aamil or user.is_moze_coordinator):
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
    
    # Students count
    from students.models import Student
    total_students = Student.objects.count()
    
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
            # Use the already imported MahalShifaDoctor (no need to re-import)
            recent_medical_records = MedicalRecord.objects.filter(
                doctor=doctor_profile
            ).select_related('patient').order_by('-created_at')[:5]
        except Exception as e:
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
        'total_students': total_students or 0,
        
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
        # Allow admin, patients, aamil, and moze coordinators to book appointments
        # Also allow doctors to book for other doctors (but not themselves)
        user = self.request.user
        context['can_book_appointment'] = (
            user.is_authenticated and (
                user.is_admin or 
                user.is_patient or 
                user.is_aamil or 
                user.is_moze_coordinator or
                (user.is_doctor and doctor.user != user)  # Doctors can book for other doctors
            )
        )
        
        # Get doctor's services with optimized query
        services = MedicalService.objects.filter(
            doctor=doctor,
            is_available=True
        ).order_by('name')[:10]  # Limit to 10 services
        context['services'] = services
        
        # Add comprehensive stats and analytics
        appointments = Appointment.objects.filter(doctor=doctor)
        completed_appointments = appointments.filter(status='completed')
        
        context['stats'] = {
            'total_appointments': appointments.count(),
            'completed_appointments': completed_appointments.count(),
            'pending_appointments': appointments.filter(status__in=['scheduled', 'confirmed']).count(),
            'cancelled_appointments': appointments.filter(status='cancelled').count(),
            'available_today': DoctorSchedule.objects.filter(
                doctor=doctor,
                date=today,
                is_available=True
            ).exists(),
            'total_patients': appointments.values('patient').distinct().count(),
            'avg_rating': 4.5,  # Placeholder - can be calculated from reviews
            'completion_rate': (completed_appointments.count() / appointments.count() * 100) if appointments.count() > 0 else 0
        }
        
        # Enhanced schedule data
        context['schedule_data'] = {
            'this_week': DoctorSchedule.objects.filter(
                doctor=doctor,
                date__range=[today, today + timedelta(days=7)],
                is_available=True
            ).order_by('date', 'start_time'),
            'next_week': DoctorSchedule.objects.filter(
                doctor=doctor,
                date__range=[today + timedelta(days=8), today + timedelta(days=14)],
                is_available=True
            ).order_by('date', 'start_time')[:5],
        }
        
        # Enhanced patient data
        context['patient_data'] = {
            'recent_patients': recent_appointments,
            'total_unique_patients': appointments.values('patient').distinct().count(),
            'returning_patients': appointments.values('patient').annotate(
                visit_count=Count('id')
            ).filter(visit_count__gt=1).count(),
            'new_patients_this_month': appointments.filter(
                appointment_date__gte=today.replace(day=1)
            ).values('patient').distinct().count()
        }
        
        # Analytics data
        
        # Appointment trends (last 6 months)
        six_months_ago = today - timedelta(days=180)
        monthly_appointments = []
        for i in range(6):
            month_start = six_months_ago + timedelta(days=30*i)
            month_end = month_start + timedelta(days=30)
            count = appointments.filter(
                appointment_date__range=[month_start, month_end]
            ).count()
            monthly_appointments.append({
                'month': month_start.strftime('%b %Y'),
                'count': count
            })
        
        context['analytics_data'] = {
            'monthly_trends': monthly_appointments,
            'status_distribution': [
                {'status': 'Completed', 'count': completed_appointments.count(), 'color': '#28a745'},
                {'status': 'Scheduled', 'count': appointments.filter(status='scheduled').count(), 'color': '#007bff'},
                {'status': 'Confirmed', 'count': appointments.filter(status='confirmed').count(), 'color': '#17a2b8'},
                {'status': 'Cancelled', 'count': appointments.filter(status='cancelled').count(), 'color': '#dc3545'},
            ],
            'peak_hours': [
                {'hour': 9, 'count': 15},
                {'hour': 14, 'count': 12},
                {'hour': 10, 'count': 10},
                {'hour': 16, 'count': 8},
                {'hour': 11, 'count': 7},
            ]  # Simplified mock data
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
    
    # Get patient's medical records from Mahal Shifa (if user has corresponding MS patient)
    medical_records = []
    try:
        if patient.user:
            from mahalshifa.models import Patient as MSPatient, MedicalRecord
            try:
                ms_patient = MSPatient.objects.get(user_account=patient.user)
                medical_records = MedicalRecord.objects.filter(patient=ms_patient).select_related('doctor__user').order_by('-created_at')
            except MSPatient.DoesNotExist:
                # No corresponding Mahal Shifa patient, which is normal
                pass
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
    # Check if user has permission to create appointments
    if not (request.user.is_admin or request.user.is_doctor or request.user.is_patient):
        messages.error(request, 'You do not have permission to book appointments.')
        return redirect('doctordirectory:dashboard')
    
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
            # Get patient from form's cleaned_data (the form's clean method should have set it)
            patient = form.cleaned_data.get('patient')
            
            # Final validation - must have a patient
            if not patient:
                messages.error(request, 'Patient information is required. Please enter a valid ITS ID and click "Fetch" to identify the patient.')
                return render(request, 'doctordirectory/appointment_form_with_fetch.html', {'form': form, 'doctor': doctor})
            
            try:
                # Create the appointment with explicit patient assignment
                appointment = form.save(commit=False)
                appointment.patient = patient
                appointment.save()
            except Exception as e:
                messages.error(request, f'Error creating appointment: {str(e)}')
                return render(request, 'doctordirectory/appointment_form_with_fetch.html', {'form': form, 'doctor': doctor})
            
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
            # Form validation failed - show specific error messages
            if form.errors:
                for field, errors in form.errors.items():
                    for error in errors:
                        if field == '__all__':
                            messages.error(request, error)
                        else:
                            field_name = form.fields[field].label or field.replace('_', ' ').title()
                            messages.error(request, f'{field_name}: {error}')
            else:
                messages.error(request, 'Please correct the errors in the form.')
    else:
        form = AppointmentForm(doctor=doctor, user=request.user)
    
    context = {
        'form': form,
        'doctor': doctor,
        'title': 'Book Appointment' if doctor else 'Create Appointment'
    }
    
    return render(request, 'doctordirectory/appointment_form_with_fetch.html', context)


@login_required
def appointment_detail(request, pk):
    """Display appointment details"""
    appointment = get_object_or_404(Appointment, pk=pk)
    
    # Check permissions - users can only view their own appointments or if they're admin/doctor
    user_can_view = False
    
    # Admin can view all appointments
    if request.user.is_admin:
        user_can_view = True
    
    # Doctor can view appointments where they are the doctor
    elif hasattr(request.user, 'doctor_profile'):
        try:
            doctor_profile = request.user.doctor_profile.first()
            if doctor_profile and appointment.doctor == doctor_profile:
                user_can_view = True
        except:
            pass
    
    # Patient can view appointments where they are the patient
    elif hasattr(request.user, 'patient_profile'):
        try:
            patient_profiles = request.user.patient_profile.all()
            if any(appointment.patient == profile for profile in patient_profiles):
                user_can_view = True
        except:
            pass
    
    # Check if doctor user matches appointment doctor
    if not user_can_view and appointment.doctor.user == request.user:
        user_can_view = True
    
    # Check if patient user matches appointment patient  
    if not user_can_view and appointment.patient.user == request.user:
        user_can_view = True
    
    if not user_can_view:
        messages.error(request, 'You do not have permission to view this appointment.')
        return redirect('accounts:profile')
    
    context = {
        'appointment': appointment,
        'title': 'Appointment Details'
    }
    
    return render(request, 'doctordirectory/appointment_detail.html', context)


@login_required
def appointment_list(request):
    """List appointments based on user role"""
    user = request.user
    
    # Base queryset
    if user.is_admin:
        appointments = Appointment.objects.all()
    elif user.is_doctor:
        try:
            doctor_profile = user.doctor_profile.first()
            if doctor_profile:
                appointments = Appointment.objects.filter(doctor=doctor_profile)
            else:
                appointments = Appointment.objects.none()
        except:
            appointments = Appointment.objects.none()
    elif hasattr(user, 'patient_profile'):
        try:
            patient_profiles = user.patient_profile.all()
            appointments = Appointment.objects.filter(patient__in=patient_profiles)
        except:
            appointments = Appointment.objects.none()
    else:
        appointments = Appointment.objects.none()
    
    # Order by most recent first
    appointments = appointments.select_related('doctor', 'patient__user').order_by('-appointment_date', '-appointment_time')
    
    context = {
        'appointments': appointments,
        'title': 'My Appointments' if not user.is_admin else 'All Appointments'
    }
    
    return render(request, 'doctordirectory/appointment_list.html', context)


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
