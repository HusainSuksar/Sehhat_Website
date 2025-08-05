from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count, Sum, Avg, F
from django.utils import timezone
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models.functions import TruncDate, TruncMonth
import json
import csv
from datetime import datetime, timedelta, date, time
from decimal import Decimal

from moze.models import Moze
from accounts.permissions import can_user_access, get_patient_data_for_user, get_medical_records_for_user

from .models import (
    Hospital, Department, Doctor, MedicalService, Patient, Appointment, MedicalRecord,
    Prescription, Medication, LabTest, LabResult, VitalSigns, 
    HospitalStaff, Room, Admission, Discharge, TreatmentPlan,
    Inventory, InventoryItem, EmergencyContact, Insurance
)
from accounts.models import User
from .forms import (
    HospitalForm, PatientForm, AppointmentForm, MedicalRecordForm
)


@login_required
def dashboard(request):
    """Mahal Shifa hospital dashboard with comprehensive medical statistics"""
    user = request.user
    
    # Base queryset based on user role
    if user.is_admin:
        hospitals = Hospital.objects.all()
        appointments = Appointment.objects.all()
        patients = Patient.objects.all()
        can_manage = True
    elif user.is_aamil or user.is_moze_coordinator:
        # Hospital administrators can see their hospital data via staff relationship
        user_hospitals = Hospital.objects.filter(staff__user=user).distinct()
        hospitals = user_hospitals
        appointments = Appointment.objects.filter(doctor__hospital__in=user_hospitals)
        patients = Patient.objects.filter(registered_moze__aamil=user)
        can_manage = True
    elif user.is_doctor:
        # Doctors can see their own data
        try:
            from .models import Doctor as MahalshifaDoctor
            doctor_profile = MahalshifaDoctor.objects.get(user=user)
            hospitals = Hospital.objects.filter(id=doctor_profile.hospital.id)
            appointments = Appointment.objects.filter(doctor=doctor_profile)
            patients = Patient.objects.filter(appointments__doctor=doctor_profile).distinct()
        except MahalshifaDoctor.DoesNotExist:
            hospitals = Hospital.objects.none()
            appointments = Appointment.objects.none()
            patients = Patient.objects.none()
        except Exception as e:
            # Log the error for debugging
            print(f"Error loading doctor profile for user {user.username}: {e}")
            hospitals = Hospital.objects.none()
            appointments = Appointment.objects.none()
            patients = Patient.objects.none()
        can_manage = False
    else:
        # Patients can see their own data
        try:
            patient_profile = user.patient_record
            hospitals = Hospital.objects.filter(doctors__appointments__patient=patient_profile).distinct()
            appointments = Appointment.objects.filter(patient=patient_profile)
            patients = Patient.objects.filter(id=patient_profile.id)
        except AttributeError:
            # User doesn't have a patient record
            hospitals = Hospital.objects.none()
            appointments = Appointment.objects.none()
            patients = Patient.objects.none()
        except Exception as e:
            # Log the error for debugging
            print(f"Error loading patient profile for user {user.username}: {e}")
            hospitals = Hospital.objects.none()
            appointments = Appointment.objects.none()
            patients = Patient.objects.none()
        can_manage = False
    
    # Today's statistics
    today = timezone.now().date()
    todays_appointments = appointments.filter(appointment_date=today).count()
    pending_appointments = appointments.filter(status='scheduled').count()
    completed_appointments = appointments.filter(status='completed').count()
    
    # Patient statistics
    total_patients = patients.count()
    active_patients = patients.filter(is_active=True).count()
    
    # Mahal Shifa and doctor statistics
    total_mahal_shifa = hospitals.count()  # Count of Mahal Shifa centers
    available_doctors = 0
    
    if user.is_admin:
        # For admin users, show all doctors
        from .models import Doctor as MahalshifaDoctor
        available_doctors = MahalshifaDoctor.objects.filter(is_available=True).count()
    else:
        # For non-admin users, show relevant doctors
        try:
            from .models import Doctor as MahalshifaDoctor
            available_doctors = MahalshifaDoctor.objects.filter(hospital__in=hospitals, is_available=True).count()
        except:
            available_doctors = 0
    
    # Recent appointments
    recent_appointments = appointments.select_related(
        'patient__user_account', 'doctor__user', 'doctor__hospital'
    ).order_by('-appointment_date')[:10]
    
    # Doctor duty schedule
    if user.is_doctor:
        try:
            doctor_profile = Doctor.objects.get(user=user)
            duty_schedule = appointments.filter(
                doctor=doctor_profile,
                appointment_date__gte=today
            ).order_by('appointment_date', 'appointment_time')[:20]
        except Doctor.DoesNotExist:
            duty_schedule = []
    else:
        duty_schedule = []
    
    # Medical records statistics
    medical_records = get_medical_records_for_user(user)
    if medical_records:
        total_records = medical_records.count()
        recent_records = medical_records.order_by('-consultation_date')[:5]
    else:
        total_records = 0
        recent_records = []
    
    # Monthly trends
    months = []
    appointment_counts = []
    patient_counts = []
    
    for i in range(6):
        month = timezone.now() - timedelta(days=30*i)
        month_start = month.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        months.append(month_start.strftime('%B %Y'))
        appointment_counts.append(
            appointments.filter(appointment_date__range=[month_start, month_end]).count()
        )
        patient_counts.append(
            patients.filter(registration_date__range=[month_start, month_end]).count()
        )
    
    context = {
        'hospitals': hospitals,
        'total_mahal_shifa': total_mahal_shifa,
        'available_doctors': available_doctors,
        'total_patients': total_patients,
        'active_patients': active_patients,
        'todays_appointments': todays_appointments,
        'pending_appointments': pending_appointments,
        'completed_appointments': completed_appointments,
        'total_records': total_records,
        'recent_appointments': recent_appointments,
        'recent_records': recent_records,
        'duty_schedule': duty_schedule,
        'can_manage': can_manage,
        'months': months,
        'appointment_counts': appointment_counts,
        'patient_counts': patient_counts,
        'user_role': user.get_role_display(),
    }
    
    return render(request, 'mahalshifa/dashboard.html', context)


@login_required
def doctor_duty_schedule(request):
    """
    Doctor duty scheduling and management
    """
    user = request.user
    
    # Check permissions
    if not can_user_access(user, 'duty_schedule', 'view'):
        messages.error(request, "You don't have permission to view duty schedules.")
        return redirect('mahalshifa:dashboard')
    
    # Get doctors based on user role
    if user.is_admin:
        doctors = Doctor.objects.all()
    elif user.is_aamil or user.is_moze_coordinator:
        # Get doctors from their Mozes
        mozes = user.managed_mozes.all() if user.is_aamil else user.coordinated_mozes.all()
        doctors = Doctor.objects.filter(appointments__moze__in=mozes).distinct()
    else:
        doctors = Doctor.objects.none()
    
    # Get date range
    start_date = request.GET.get('start_date', timezone.now().date())
    end_date = request.GET.get('end_date', (timezone.now() + timedelta(days=7)).date())
    
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Get appointments for the date range
    appointments = Appointment.objects.filter(
        appointment_date__range=[start_date, end_date],
        doctor__in=doctors
    ).select_related('doctor__user', 'patient', 'moze').order_by('appointment_date', 'appointment_time')
    
    # Group appointments by doctor and date
    duty_schedule = {}
    for appointment in appointments:
        doctor_id = appointment.doctor.id
        date_key = appointment.appointment_date
        
        if doctor_id not in duty_schedule:
            duty_schedule[doctor_id] = {}
        
        if date_key not in duty_schedule[doctor_id]:
            duty_schedule[doctor_id][date_key] = []
        
        duty_schedule[doctor_id][date_key].append(appointment)
    
    # Get doctor statistics
    doctor_stats = []
    for doctor in doctors:
        doctor_appointments = appointments.filter(doctor=doctor)
        doctor_stats.append({
            'doctor': doctor,
            'total_appointments': doctor_appointments.count(),
            'completed_appointments': doctor_appointments.filter(status='completed').count(),
            'pending_appointments': doctor_appointments.filter(status__in=['scheduled', 'confirmed']).count(),
            'today_appointments': doctor_appointments.filter(appointment_date=timezone.now().date()).count(),
        })
    
    context = {
        'doctors': doctors,
        'duty_schedule': duty_schedule,
        'doctor_stats': doctor_stats,
        'start_date': start_date,
        'end_date': end_date,
        'user_role': user.get_role_display(),
    }
    
    return render(request, 'mahalshifa/doctor_duty_schedule.html', context)


@login_required
def patient_visit_log(request):
    """
    Log and manage patient visits
    """
    user = request.user
    
    # Check permissions
    if not can_user_access(user, 'patient', 'view'):
        messages.error(request, "You don't have permission to view patient visits.")
        return redirect('mahalshifa:dashboard')
    
    # Get patients based on user role
    patients = get_patient_data_for_user(user)
    
    if not patients:
        messages.warning(request, "No patients accessible.")
        return redirect('mahalshifa:dashboard')
    
    # Get visit date range
    start_date = request.GET.get('start_date', (timezone.now() - timedelta(days=30)).date())
    end_date = request.GET.get('end_date', timezone.now().date())
    
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Get appointments and medical records for the date range
    appointments = Appointment.objects.filter(
        patient__in=patients,
        appointment_date__range=[start_date, end_date]
    ).select_related('patient', 'doctor__user', 'moze').order_by('-appointment_date')
    
    medical_records = MedicalRecord.objects.filter(
        patient__in=patients,
        consultation_date__date__range=[start_date, end_date]
    ).select_related('patient', 'doctor__user', 'moze').order_by('-consultation_date')
    
    # Patient visit statistics
    visit_stats = {
        'total_visits': appointments.count() + medical_records.count(),
        'appointments': appointments.count(),
        'consultations': medical_records.count(),
        'unique_patients': patients.filter(
            appointments__appointment_date__range=[start_date, end_date]
        ).distinct().count(),
    }
    
    # Recent visits
    recent_visits = []
    
    # Add appointments
    for appointment in appointments[:20]:
        recent_visits.append({
            'type': 'appointment',
            'date': appointment.appointment_date,
            'time': appointment.appointment_time,
            'patient': appointment.patient,
            'doctor': appointment.doctor,
            'status': appointment.status,
            'moze': appointment.moze,
            'object': appointment,
        })
    
    # Add medical records
    for record in medical_records[:20]:
        recent_visits.append({
            'type': 'consultation',
            'date': record.consultation_date.date(),
            'time': record.consultation_date.time(),
            'patient': record.patient,
            'doctor': record.doctor,
            'status': 'completed',
            'moze': record.moze,
            'object': record,
        })
    
    # Sort by date and time
    recent_visits.sort(key=lambda x: (x['date'], x['time']), reverse=True)
    recent_visits = recent_visits[:20]
    
    # Patient demographics
    patient_demographics = {
        'gender_distribution': patients.values('gender').annotate(count=Count('id')),
        'age_groups': {
            '0-18': patients.filter(date_of_birth__gte=timezone.now().date() - timedelta(days=18*365)).count(),
            '19-30': patients.filter(
                date_of_birth__lt=timezone.now().date() - timedelta(days=18*365),
                date_of_birth__gte=timezone.now().date() - timedelta(days=30*365)
            ).count(),
            '31-50': patients.filter(
                date_of_birth__lt=timezone.now().date() - timedelta(days=30*365),
                date_of_birth__gte=timezone.now().date() - timedelta(days=50*365)
            ).count(),
            '51+': patients.filter(date_of_birth__lt=timezone.now().date() - timedelta(days=50*365)).count(),
        }
    }
    
    context = {
        'patients': patients,
        'appointments': appointments,
        'medical_records': medical_records,
        'visit_stats': visit_stats,
        'recent_visits': recent_visits,
        'patient_demographics': patient_demographics,
        'start_date': start_date,
        'end_date': end_date,
        'user_role': user.get_role_display(),
    }
    
    return render(request, 'mahalshifa/patient_visit_log.html', context)


@login_required
def dua_araz_preparation(request):
    """
    Prepare and manage Dua Araz (petitions)
    """
    user = request.user
    
    # Check permissions
    if not can_user_access(user, 'araz', 'view'):
        messages.error(request, "You don't have permission to view petitions.")
        return redirect('mahalshifa:dashboard')
    
    # Get petitions based on user role
    if user.is_admin:
        petitions = Petition.objects.all()
    elif user.is_aamil or user.is_moze_coordinator:
        mozes = user.managed_mozes.all() if user.is_aamil else user.coordinated_mozes.all()
        petitions = Petition.objects.filter(created_by__managed_mozes__in=mozes)
    elif user.is_doctor:
        petitions = Petition.objects.filter(created_by=user)
    else:
        petitions = Petition.objects.none()
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        petitions = petitions.filter(status=status_filter)
    
    # Filter by date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        petitions = petitions.filter(created_at__date__gte=start_date)
    if end_date:
        petitions = petitions.filter(created_at__date__lte=end_date)
    
    # Statistics
    petition_stats = {
        'total': petitions.count(),
        'pending': petitions.filter(status='pending').count(),
        'approved': petitions.filter(status='approved').count(),
        'rejected': petitions.filter(status='rejected').count(),
        'in_progress': petitions.filter(status='in_progress').count(),
    }
    
    # Recent petitions
    recent_petitions = petitions.order_by('-created_at')[:10]
    
    # Monthly trends
    months = []
    petition_counts = []
    
    for i in range(6):
        month = timezone.now() - timedelta(days=30*i)
        month_start = month.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        months.append(month_start.strftime('%B %Y'))
        petition_counts.append(
            petitions.filter(created_at__date__range=[month_start, month_end]).count()
        )
    
    context = {
        'petitions': petitions,
        'petition_stats': petition_stats,
        'recent_petitions': recent_petitions,
        'months': months,
        'petition_counts': petition_counts,
        'status_filter': status_filter,
        'start_date': start_date,
        'end_date': end_date,
        'user_role': user.get_role_display(),
    }
    
    return render(request, 'mahalshifa/dua_araz_preparation.html', context)


class HospitalListView(LoginRequiredMixin, ListView):
    """List all hospitals with filtering"""
    model = Hospital
    template_name = 'mahalshifa/hospital_list.html'
    context_object_name = 'hospitals'
    paginate_by = 20
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Hospital.objects.all()
        elif user.is_aamil or user.is_moze_coordinator:
            # Hospital administrators can see their hospital data via staff relationship
            return Hospital.objects.filter(staff__user=user).distinct()
        elif user.is_doctor:
            # Doctors can see their hospital
            try:
                from .models import Doctor as MahalshifaDoctor
                doctor_profile = MahalshifaDoctor.objects.get(user=user)
                return Hospital.objects.filter(id=doctor_profile.hospital.id)
            except MahalshifaDoctor.DoesNotExist:
                return Hospital.objects.none()
        else:
            # Patients can see hospitals where they have appointments
            try:
                patient_profile = user.patient_record
                return Hospital.objects.filter(doctors__appointments__patient=patient_profile).distinct()
            except AttributeError:
                return Hospital.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hospital_types'] = [
            ('general', 'General Hospital'),
            ('specialty', 'Specialty Hospital'),
            ('clinic', 'Clinic'),
            ('emergency', 'Emergency Center'),
            ('rehabilitation', 'Rehabilitation Center'),
        ]
        context['current_filters'] = {
            'location': self.request.GET.get('location', ''),
            'type': self.request.GET.get('type', ''),
            'search': self.request.GET.get('search', ''),
        }
        return context


class HospitalDetailView(LoginRequiredMixin, DetailView):
    """Detailed view of a specific hospital"""
    model = Hospital
    template_name = 'mahalshifa/hospital_detail.html'
    context_object_name = 'hospital'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hospital = self.object
        user = self.request.user
        
        # Departments
        context['departments'] = hospital.departments.filter(is_active=True)
        
        # Doctors
        context['doctors'] = Doctor.objects.filter(
            hospital=hospital,
            is_available=True
        ).select_related('user')
        
        # Rooms
        context['rooms'] = hospital.rooms.all()
        
        # Recent appointments - fix the field relationship
        context['recent_appointments'] = Appointment.objects.filter(
            doctor__hospital=hospital
        ).select_related('patient', 'doctor__user').order_by('-appointment_date')[:10]
        
        # Statistics - fix the field relationships
        context['total_appointments'] = Appointment.objects.filter(doctor__hospital=hospital).count()
        context['total_patients'] = Patient.objects.filter(appointments__doctor__hospital=hospital).distinct().count()
        context['total_doctors'] = Doctor.objects.filter(hospital=hospital).count()
        
        # Permission checks
        context['can_manage'] = (
            user.is_admin or
            hospital.staff.filter(user=user).exists()
        )
        
        return context


class PatientListView(LoginRequiredMixin, ListView):
    """List patients with role-based access"""
    model = Patient
    template_name = 'mahalshifa/patient_list.html'
    context_object_name = 'patients'
    paginate_by = 20
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin:
            queryset = Patient.objects.all()
        elif user.is_aamil or user.is_moze_coordinator:
            # Fix the relationship - aamil manages mozes, not directly patients
            mozes = user.managed_mozes.all() if user.is_aamil else user.coordinated_mozes.all()
            queryset = Patient.objects.filter(registered_moze__in=mozes)
        elif user.is_doctor:
            try:
                from .models import Doctor as MahalshifaDoctor
                doctor_profile = MahalshifaDoctor.objects.get(user=user)
                queryset = Patient.objects.filter(appointments__doctor=doctor_profile).distinct()
            except MahalshifaDoctor.DoesNotExist:
                queryset = Patient.objects.none()
            except Exception as e:
                print(f"Error loading doctor patients for user {user.username}: {e}")
                queryset = Patient.objects.none()
        else:
            # Patients can only see their own record
            try:
                queryset = Patient.objects.filter(id=user.patient_record.id)
            except AttributeError:
                queryset = Patient.objects.none()
            except Exception as e:
                print(f"Error loading patient record for user {user.username}: {e}")
                queryset = Patient.objects.none()
        
        # Add search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(its_id__icontains=search) |
                Q(phone_number__icontains=search)
            )
        
        # Add status filter
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        return queryset.select_related('registered_moze', 'user_account')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if user.is_admin or user.is_aamil or user.is_moze_coordinator:
            context['hospitals'] = Hospital.objects.filter(is_active=True)
        
        context['current_filters'] = {
            'hospital': self.request.GET.get('hospital', ''),
            'status': self.request.GET.get('status', ''),
            'search': self.request.GET.get('search', ''),
        }
        return context


class AppointmentListView(LoginRequiredMixin, ListView):
    """List appointments with role-based filtering"""
    model = Appointment
    template_name = 'mahalshifa/appointment_list.html'
    context_object_name = 'appointments'
    paginate_by = 20
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin:
            return Appointment.objects.all()
        elif user.is_aamil or user.is_moze_coordinator:
            return Appointment.objects.all()
        elif user.is_doctor:
            try:
                from .models import Doctor as MahalshifaDoctor
                doctor_profile = MahalshifaDoctor.objects.get(user=user)
                return Appointment.objects.filter(doctor=doctor_profile)
            except MahalshifaDoctor.DoesNotExist:
                return Appointment.objects.none()
            except Exception as e:
                print(f"Error loading doctor appointments for user {user.username}: {e}")
                return Appointment.objects.none()
        else:
            # Patients can only see their own appointments
            try:
                return Appointment.objects.filter(patient=user.patient_record)
            except AttributeError:
                return Appointment.objects.none()
            except Exception as e:
                print(f"Error loading patient appointments for user {user.username}: {e}")
                return Appointment.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        context['status_choices'] = Appointment.STATUS_CHOICES
        
        if user.is_admin or user.is_aamil or user.is_moze_coordinator:
            context['doctors'] = Doctor.objects.filter(is_available=True).select_related('user')
        
        context['current_filters'] = {
            'status': self.request.GET.get('status', ''),
            'date': self.request.GET.get('date', ''),
            'doctor': self.request.GET.get('doctor', ''),
        }
        return context


@login_required
def appointment_detail(request, pk):
    """Detailed view of an appointment"""
    appointment = get_object_or_404(Appointment, pk=pk)
    user = request.user
    
    # Enhanced authorization check with proper access control
    can_view = False
    
    if user.is_admin:
        can_view = True
    elif user.is_aamil or user.is_moze_coordinator:
        # Check if this appointment is within their organizational scope
        # Aamils can only view appointments for patients they're responsible for
        if hasattr(appointment.patient, 'registered_moze') and appointment.patient.registered_moze.aamil == user:
            can_view = True
    elif user.is_doctor:
        # Doctors can only view their own appointments
        if hasattr(user, 'mahalshifa_doctor_profile') and appointment.doctor == user.mahalshifa_doctor_profile:
            can_view = True
    elif appointment.patient.user_account == user:
        # Patients can only view their own appointments
        can_view = True
    
    if not can_view:
        messages.error(request, 'You do not have permission to view this appointment.')
        return redirect('mahalshifa:appointment_list')
    
    # Get related data
    medical_records = MedicalRecord.objects.filter(appointment=appointment)
    prescriptions = Prescription.objects.filter(patient=appointment.patient)
    lab_tests = LabTest.objects.filter(patient=appointment.patient)
    vital_signs = VitalSigns.objects.filter(patient=appointment.patient).order_by('-recorded_at')
    
    context = {
        'appointment': appointment,
        'medical_records': medical_records,
        'prescriptions': prescriptions,
        'lab_tests': lab_tests,
        'vital_signs': vital_signs,
        'can_edit': user == appointment.doctor.user or user.is_admin,
    }
    
    return render(request, 'mahalshifa/appointment_detail.html', context)


@login_required
def patient_detail(request, pk):
    """Detailed view of a patient"""
    patient = get_object_or_404(Patient, pk=pk)
    user = request.user
    
    # Enhanced authorization check with proper access control
    can_view = False
    
    if user.is_admin:
        can_view = True
    elif user.is_aamil or user.is_moze_coordinator:
        # Check if this patient is within their organizational scope
        # Aamils can only view patients they're responsible for
        if hasattr(patient, 'registered_moze') and patient.registered_moze.aamil == user:
            can_view = True
    elif user.is_doctor:
        # Doctors can only view patients they have appointments with
        if patient.appointments.filter(doctor__user=user).exists():
            can_view = True
    elif patient.user_account == user:
        # Patients can only view their own records
        can_view = True
    
    if not can_view:
        messages.error(request, 'You do not have permission to view this patient.')
        return redirect('mahalshifa:patient_list')
    
    # Get related data
    appointments = patient.appointments.select_related('doctor__user', 'doctor__hospital').order_by('-appointment_date')
    medical_records = MedicalRecord.objects.filter(patient=patient).order_by('-created_at')
    prescriptions = Prescription.objects.filter(patient=patient).order_by('-created_at')
    lab_tests = LabTest.objects.filter(patient=patient).order_by('-created_at')
    admissions = Admission.objects.filter(patient=patient).order_by('-admission_date')
    emergency_contacts = patient.emergency_contacts.all()
    insurance_info = patient.insurance_policies.all()
    
    # Recent vital signs
    recent_vitals = VitalSigns.objects.filter(
        patient=patient
    ).order_by('-recorded_at')[:5]
    
    context = {
        'patient': patient,
        'appointments': appointments[:10],  # Recent 10
        'medical_records': medical_records[:10],
        'prescriptions': prescriptions[:10],
        'lab_tests': lab_tests[:10],
        'admissions': admissions,
        'emergency_contacts': emergency_contacts,
        'insurance_info': insurance_info,
        'recent_vitals': recent_vitals,
        'can_edit': (
            user.is_admin or
            user.is_aamil or
            user.is_moze_coordinator
        ),
    }
    
    return render(request, 'mahalshifa/patient_detail.html', context)


@login_required
def create_appointment(request):
    """Create a new appointment"""
    if not (request.user.is_admin or request.user.is_aamil or request.user.is_moze_coordinator):
        messages.error(request, 'You do not have permission to create appointments.')
        return redirect('mahalshifa:appointment_list')
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.booked_by = request.user
    
         # 🔽 Add this based on your logic
            if request.user.role == 'aamil':
                appointment.moze = request.user.managed_mozes.first()
            elif request.user.role == 'moze_coordinator':
                  appointment.moze = request.user.coordinated_mozes.first()
            elif request.user.role == 'badri_mahal_admin':  # as you mentioned earlier
                 appointment.moze = Moze.objects.first()  # or allow selecting from all
    
            if appointment.moze is None:
             messages.error(request, "Unable to determine Moze for this appointment.")
             return redirect('mahalshifa:appointment_list')
            appointment.save()
            messages.success(request, 'Appointment created successfully!')
            return redirect('mahalshifa:appointment_detail', pk=appointment.pk)
    else:
        form = AppointmentForm()
    
        

    
    context = {
        'form': form,
        'doctors': Doctor.objects.filter(is_available=True).select_related('user'),
        'patients': Patient.objects.filter(is_active=True),
        'services': MedicalService.objects.filter(is_active=True),
    }
    
    return render(request, 'mahalshifa/create_appointment.html', context)


@login_required
def medical_analytics(request):
    """Medical analytics dashboard"""
    if not (request.user.is_admin or request.user.is_aamil or request.user.is_moze_coordinator):
        messages.error(request, 'You do not have permission to view analytics.')
        return redirect('mahalshifa:dashboard')
    
    # Get date range
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    # Get data based on user role
    user = request.user
    if user.is_admin:
        appointments = Appointment.objects.all()
        patients = Patient.objects.all()
        hospitals = Hospital.objects.all()
    elif user.is_aamil or user.is_moze_coordinator:
        appointments = Appointment.objects.filter(doctor__hospital__staff__user=user).distinct()
        patients = Patient.objects.filter(registered_moze__aamil=user)
        hospitals = Hospital.objects.filter(staff__user=user).distinct()
    else:
        appointments = Appointment.objects.none()
        patients = Patient.objects.none()
        hospitals = Hospital.objects.none()
    
    # Calculate statistics
    total_appointments = appointments.count()
    completed_appointments = appointments.filter(status='completed').count()
    pending_appointments = appointments.filter(status='scheduled').count()
    total_patients = patients.count()
    total_hospitals = hospitals.count()
    
    # Monthly trends
    monthly_data = []
    for i in range(6):
        month_start = end_date.replace(day=1) - timedelta(days=30*i)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        month_appointments = appointments.filter(
            appointment_date__gte=month_start,
            appointment_date__lte=month_end
        ).count()
        monthly_data.append({
            'month': month_start.strftime('%b %Y'),
            'count': month_appointments
        })
    
    # Appointment status distribution
    status_distribution = appointments.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # Hospital statistics
    hospital_stats = hospitals.annotate(
        appointment_count=Count('doctors__appointments'),
        doctor_count=Count('doctors'),
        patient_count=Count('doctors__appointments__patient', distinct=True)
    ).order_by('-appointment_count')
    
    context = {
        'total_appointments': total_appointments,
        'completed_appointments': completed_appointments,
        'pending_appointments': pending_appointments,
        'total_patients': total_patients,
        'total_hospitals': total_hospitals,
        'monthly_data': monthly_data,
        'status_distribution': status_distribution,
        'hospital_stats': hospital_stats,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'mahalshifa/analytics.html', context)


@login_required
def inventory_management(request):
    """Inventory management dashboard"""
    if not (request.user.is_admin or request.user.is_aamil or request.user.is_moze_coordinator):
        messages.error(request, 'You do not have permission to view inventory.')
        return redirect('mahalshifa:dashboard')
    
    # Get inventory data based on user role
    user = request.user
    if user.is_admin:
        inventory_items = InventoryItem.objects.all()
        inventories = Inventory.objects.all()
    elif user.is_aamil or user.is_moze_coordinator:
        inventory_items = InventoryItem.objects.filter(inventory__hospital__staff__user=user)
        inventories = Inventory.objects.filter(hospital__staff__user=user)
    else:
        inventory_items = InventoryItem.objects.none()
        inventories = Inventory.objects.none()
    
    # Calculate statistics
    total_items = inventory_items.count()
    low_stock_items = inventory_items.filter(current_stock__lte=F('minimum_stock')).count()
    expired_items = inventory_items.filter(expiry_date__lt=timezone.now().date()).count()
    
    # Category distribution
    category_distribution = inventory_items.values('category').annotate(
        count=Count('id')
    ).order_by('category')
    
    # Low stock items
    low_stock_list = inventory_items.filter(
        current_stock__lte=F('minimum_stock')
    ).select_related('inventory')[:10]
    
    # Expired items
    expired_list = inventory_items.filter(
        expiry_date__lt=timezone.now().date()
    ).select_related('inventory')[:10]
    
    context = {
        'total_items': total_items,
        'low_stock_items': low_stock_items,
        'expired_items': expired_items,
        'category_distribution': category_distribution,
        'low_stock_list': low_stock_list,
        'expired_list': expired_list,
        'inventories': inventories,
    }
    
    return render(request, 'mahalshifa/inventory.html', context)


@login_required
def export_medical_data(request):
    """Export medical data to CSV"""
    if not (request.user.is_admin or request.user.is_aamil or request.user.is_moze_coordinator):
        messages.error(request, 'You do not have permission to export data.')
        return redirect('mahalshifa:dashboard')
    
    # Get data based on user role
    user = request.user
    if user.is_admin:
        appointments = Appointment.objects.all()
        patients = Patient.objects.all()
        medical_records = MedicalRecord.objects.all()
    elif user.is_aamil or user.is_moze_coordinator:
        appointments = Appointment.objects.filter(doctor__hospital__staff__user=user).distinct()
        patients = Patient.objects.filter(registered_moze__aamil=user)
        medical_records = MedicalRecord.objects.filter(moze__aamil=user)
    else:
        appointments = Appointment.objects.none()
        patients = Patient.objects.none()
        medical_records = MedicalRecord.objects.none()
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="medical_data_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Data Type', 'ID', 'Patient Name', 'Doctor Name', 'Date', 'Status', 'Notes'
    ])
    
    # Export appointments
    for appointment in appointments.select_related('patient', 'doctor__user'):
        writer.writerow([
            'Appointment',
            appointment.id,
            appointment.patient.get_full_name(),
            appointment.doctor.user.get_full_name(),
            appointment.appointment_date,
            appointment.status,
            appointment.reason
        ])
    
    # Export medical records
    for record in medical_records.select_related('patient', 'doctor__user'):
        writer.writerow([
            'Medical Record',
            record.id,
            record.patient.get_full_name(),
            record.doctor.user.get_full_name(),
            record.consultation_date.date(),
            'Completed',
            record.diagnosis
        ])
    
    return response

# Hospital CRUD Views
class HospitalCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Create a new hospital"""
    model = Hospital
    form_class = HospitalForm
    template_name = 'mahalshifa/hospital_create.html'
    success_url = reverse_lazy('mahalshifa:hospital_list')
    
    def test_func(self):
        return self.request.user.is_admin
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Hospital created successfully!')
        return super().form_valid(form)


class HospitalUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update an existing hospital"""
    model = Hospital
    form_class = HospitalForm
    template_name = 'mahalshifa/hospital_edit.html'
    success_url = reverse_lazy('mahalshifa:hospital_list')
    
    def test_func(self):
        return self.request.user.is_admin
    
    def form_valid(self, form):
        messages.success(self.request, 'Hospital updated successfully!')
        return super().form_valid(form)


class HospitalDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a hospital"""
    model = Hospital
    template_name = 'mahalshifa/hospital_confirm_delete.html'
    success_url = reverse_lazy('mahalshifa:hospital_list')
    
    def test_func(self):
        return self.request.user.is_admin
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Hospital deleted successfully!')
        return super().delete(request, *args, **kwargs)


# Patient CRUD Views
class PatientCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Create a new patient"""
    model = Patient
    form_class = PatientForm
    template_name = 'mahalshifa/patient_create.html'
    success_url = reverse_lazy('mahalshifa:patient_list')
    
    def test_func(self):
        return self.request.user.is_admin or self.request.user.is_aamil or self.request.user.is_moze_coordinator
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Patient created successfully!')
        return super().form_valid(form)


class PatientUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update an existing patient"""
    model = Patient
    form_class = PatientForm
    template_name = 'mahalshifa/patient_edit.html'
    success_url = reverse_lazy('mahalshifa:patient_list')
    
    def test_func(self):
        return self.request.user.is_admin or self.request.user.is_aamil or self.request.user.is_moze_coordinator
    
    def form_valid(self, form):
        messages.success(self.request, 'Patient updated successfully!')
        return super().form_valid(form)


class PatientDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a patient"""
    model = Patient
    template_name = 'mahalshifa/patient_confirm_delete.html'
    success_url = reverse_lazy('mahalshifa:patient_list')
    
    def test_func(self):
        return self.request.user.is_admin or self.request.user.is_aamil or self.request.user.is_moze_coordinator
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Patient deleted successfully!')
        return super().delete(request, *args, **kwargs)


# Appointment CRUD Views
class AppointmentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update an existing appointment"""
    model = Appointment
    form_class = AppointmentForm
    template_name = 'mahalshifa/appointment_edit.html'
    success_url = reverse_lazy('mahalshifa:appointment_list')
    
    def test_func(self):
        appointment = self.get_object()
        return (self.request.user.is_admin or 
                self.request.user.is_aamil or 
                self.request.user.is_moze_coordinator or
                appointment.doctor.user == self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Appointment updated successfully!')
        return super().form_valid(form)


class AppointmentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete an appointment"""
    model = Appointment
    template_name = 'mahalshifa/appointment_confirm_delete.html'
    success_url = reverse_lazy('mahalshifa:appointment_list')
    
    def test_func(self):
        appointment = self.get_object()
        return (self.request.user.is_admin or 
                self.request.user.is_aamil or 
                self.request.user.is_moze_coordinator or
                appointment.doctor.user == self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Appointment deleted successfully!')
        return super().delete(request, *args, **kwargs)


# Medical Record CRUD Views
class MedicalRecordListView(LoginRequiredMixin, ListView):
    """List medical records with role-based access"""
    model = MedicalRecord
    template_name = 'mahalshifa/medical_record_list.html'
    context_object_name = 'medical_records'
    paginate_by = 20
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return MedicalRecord.objects.all()
        elif user.is_aamil or user.is_moze_coordinator:
            return MedicalRecord.objects.filter(moze__aamil=user)
        elif user.is_doctor:
            return MedicalRecord.objects.filter(doctor__user=user)
        else:
            return MedicalRecord.objects.filter(patient__user_account=user)


class MedicalRecordCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Create a new medical record"""
    model = MedicalRecord
    form_class = MedicalRecordForm
    template_name = 'mahalshifa/medical_record_create.html'
    success_url = reverse_lazy('mahalshifa:medical_record_list')
    
    def post(self, request, *args, **kwargs):
        """Handle POST request with debugging"""
        print(f"🔍 POST request received for medical record creation")
        print(f"📝 Form data: {request.POST}")
        
        form = self.get_form()
        if form.is_valid():
            print(f"✅ Form is valid")
            return self.form_valid(form)
        else:
            print(f"❌ Form errors: {form.errors}")
            return self.form_invalid(form)
    
    def test_func(self):
        return self.request.user.is_admin or self.request.user.is_doctor
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        
        # If user is a doctor, filter doctor choices to only show their profile
        if user.is_doctor:
            try:
                doctor_profile = user.mahalshifa_doctor_profile
                form.fields['doctor'].queryset = Doctor.objects.filter(id=doctor_profile.id)
                form.fields['doctor'].initial = doctor_profile
            except Doctor.DoesNotExist:
                # If user doesn't have a doctor profile, show all doctors
                pass
        
        return form
    
    def form_valid(self, form):
        user = self.request.user
        
        # If user is a doctor, automatically set the doctor field
        if user.is_doctor:
            try:
                doctor_profile = user.mahalshifa_doctor_profile
                form.instance.doctor = doctor_profile
            except Doctor.DoesNotExist:
                # If user doesn't have a doctor profile, let them choose
                pass
        
        # Save the form
        medical_record = form.save()
        
        # Add success message
        messages.success(self.request, f'Medical record created successfully for {medical_record.patient.get_full_name()}!')
        
        # Redirect to the medical record list
        return redirect('mahalshifa:medical_record_list')


class MedicalRecordDetailView(LoginRequiredMixin, DetailView):
    """Detailed view of a medical record"""
    model = MedicalRecord
    template_name = 'mahalshifa/medical_record_detail.html'
    context_object_name = 'medical_record'
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return MedicalRecord.objects.all()
        elif user.is_aamil or user.is_moze_coordinator:
            return MedicalRecord.objects.filter(moze__aamil=user)
        elif user.is_doctor:
            return MedicalRecord.objects.filter(doctor__user=user)
        else:
            return MedicalRecord.objects.filter(patient__user_account=user)


class MedicalRecordUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update an existing medical record"""
    model = MedicalRecord
    form_class = MedicalRecordForm
    template_name = 'mahalshifa/medical_record_edit.html'
    success_url = reverse_lazy('mahalshifa:medical_record_list')
    
    def test_func(self):
        medical_record = self.get_object()
        return (self.request.user.is_admin or 
                medical_record.doctor.user == self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Medical record updated successfully!')
        return super().form_valid(form)


class MedicalRecordDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a medical record"""
    model = MedicalRecord
    template_name = 'mahalshifa/medical_record_confirm_delete.html'
    success_url = reverse_lazy('mahalshifa:medical_record_list')
    
    def test_func(self):
        medical_record = self.get_object()
        return (self.request.user.is_admin or 
                medical_record.doctor.user == self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Medical record deleted successfully!')
        return super().delete(request, *args, **kwargs)
