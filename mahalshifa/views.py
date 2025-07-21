from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from django.core.paginator import Paginator
from django.db import transaction
import json
from datetime import datetime, timedelta, date, time
from decimal import Decimal

from .models import (
    Hospital, Department, Doctor, Patient, Appointment, MedicalRecord,
    Prescription, Medication, LabTest, LabResult, VitalSigns, 
    HospitalStaff, Room, Admission, Discharge, TreatmentPlan,
    Inventory, InventoryItem, EmergencyContact, Insurance
)
from accounts.models import User


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
        # Hospital administrators can see their hospital data
        user_hospitals = Hospital.objects.filter(
            Q(administrator=user) | Q(staff__user=user)
        ).distinct()
        hospitals = user_hospitals
        appointments = Appointment.objects.filter(hospital__in=user_hospitals)
        patients = Patient.objects.filter(hospital__in=user_hospitals)
        can_manage = True
    elif user.is_doctor:
        # Doctors can see their own data
        doctor_profile = Doctor.objects.filter(user=user).first()
        if doctor_profile:
            hospitals = Hospital.objects.filter(id=doctor_profile.hospital.id)
            appointments = Appointment.objects.filter(doctor=doctor_profile)
            patients = Patient.objects.filter(appointments__doctor=doctor_profile).distinct()
        else:
            hospitals = Hospital.objects.none()
            appointments = Appointment.objects.none()
            patients = Patient.objects.none()
        can_manage = False
    else:
        # Patients can see their own data
        patient_profile = Patient.objects.filter(user=user).first()
        if patient_profile:
            hospitals = Hospital.objects.filter(id=patient_profile.hospital.id)
            appointments = Appointment.objects.filter(patient=patient_profile)
            patients = Patient.objects.filter(id=patient_profile.id)
        else:
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
    
    # Recent appointments
    recent_appointments = appointments.select_related(
        'patient__user', 'doctor__user', 'hospital'
    ).order_by('-appointment_date', '-appointment_time')[:10]
    
    # Hospital statistics
    total_hospitals = hospitals.count()
    
    # Monthly appointment trends
    monthly_stats = []
    for i in range(6):
        month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
        month_appointments = appointments.filter(
            appointment_date__year=month_start.year,
            appointment_date__month=month_start.month
        ).count()
        monthly_stats.append({
            'month': month_start.strftime('%b %Y'),
            'count': month_appointments
        })
    
    # Department statistics
    dept_stats = []
    if can_manage:
        dept_stats = Department.objects.filter(
            hospital__in=hospitals
        ).annotate(
            appointment_count=Count('doctors__appointments')
        ).order_by('-appointment_count')[:5]
    
    # Emergency cases
    emergency_cases = appointments.filter(
        appointment_type='emergency',
        appointment_date=today
    ).count()
    
    # Lab tests pending
    pending_lab_tests = LabTest.objects.filter(
        patient__in=patients,
        status='pending'
    ).count()
    
    # Recent admissions
    recent_admissions = Admission.objects.filter(
        patient__in=patients
    ).select_related('patient__user', 'room', 'hospital').order_by('-admission_date')[:5]
    
    context = {
        'todays_appointments': todays_appointments,
        'pending_appointments': pending_appointments,
        'completed_appointments': completed_appointments,
        'total_patients': total_patients,
        'active_patients': active_patients,
        'total_hospitals': total_hospitals,
        'emergency_cases': emergency_cases,
        'pending_lab_tests': pending_lab_tests,
        'recent_appointments': recent_appointments,
        'recent_admissions': recent_admissions,
        'monthly_stats': monthly_stats[::-1],
        'dept_stats': dept_stats,
        'can_manage': can_manage,
        'user_role': user.get_role_display(),
    }
    
    return render(request, 'mahalshifa/dashboard.html', context)


class HospitalListView(LoginRequiredMixin, ListView):
    """List all hospitals with filtering"""
    model = Hospital
    template_name = 'mahalshifa/hospital_list.html'
    context_object_name = 'hospitals'
    paginate_by = 20
    
    def get_queryset(self):
        user = self.request.user
        
        # Base queryset based on user role
        if user.is_admin:
            queryset = Hospital.objects.all()
        elif user.is_aamil or user.is_moze_coordinator:
            queryset = Hospital.objects.filter(
                Q(administrator=user) | Q(staff__user=user)
            ).distinct()
        else:
            # Public view for doctors and patients
            queryset = Hospital.objects.filter(is_active=True)
        
        # Apply filters
        location = self.request.GET.get('location')
        if location:
            queryset = queryset.filter(location__icontains=location)
        
        hospital_type = self.request.GET.get('type')
        if hospital_type:
            queryset = queryset.filter(hospital_type=hospital_type)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(location__icontains=search) |
                Q(contact_email__icontains=search)
            )
        
        return queryset.order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hospital_types'] = Hospital.HOSPITAL_TYPES
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
            is_active=True
        ).select_related('user')
        
        # Rooms
        context['rooms'] = hospital.rooms.all()
        
        # Recent appointments
        context['recent_appointments'] = Appointment.objects.filter(
            hospital=hospital
        ).select_related('patient__user', 'doctor__user').order_by('-appointment_date')[:10]
        
        # Statistics
        context['total_appointments'] = Appointment.objects.filter(hospital=hospital).count()
        context['total_patients'] = Patient.objects.filter(hospital=hospital).count()
        context['total_doctors'] = Doctor.objects.filter(hospital=hospital).count()
        
        # Permission checks
        context['can_manage'] = (
            user.is_admin or
            hospital.administrator == user or
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
        
        # Base queryset based on user role
        if user.is_admin:
            queryset = Patient.objects.all()
        elif user.is_aamil or user.is_moze_coordinator:
            user_hospitals = Hospital.objects.filter(
                Q(administrator=user) | Q(staff__user=user)
            )
            queryset = Patient.objects.filter(hospital__in=user_hospitals)
        elif user.is_doctor:
            doctor_profile = Doctor.objects.filter(user=user).first()
            if doctor_profile:
                queryset = Patient.objects.filter(
                    appointments__doctor=doctor_profile
                ).distinct()
            else:
                queryset = Patient.objects.none()
        else:
            # Patients can only see themselves
            queryset = Patient.objects.filter(user=user)
        
        # Apply filters
        hospital = self.request.GET.get('hospital')
        if hospital:
            queryset = queryset.filter(hospital_id=hospital)
        
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(user__its_id__icontains=search) |
                Q(patient_id__icontains=search)
            )
        
        return queryset.select_related('user', 'hospital').order_by('-created_at')
    
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
        
        # Base queryset based on user role
        if user.is_admin:
            queryset = Appointment.objects.all()
        elif user.is_aamil or user.is_moze_coordinator:
            user_hospitals = Hospital.objects.filter(
                Q(administrator=user) | Q(staff__user=user)
            )
            queryset = Appointment.objects.filter(hospital__in=user_hospitals)
        elif user.is_doctor:
            doctor_profile = Doctor.objects.filter(user=user).first()
            if doctor_profile:
                queryset = Appointment.objects.filter(doctor=doctor_profile)
            else:
                queryset = Appointment.objects.none()
        else:
            # Patients can only see their appointments
            patient_profile = Patient.objects.filter(user=user).first()
            if patient_profile:
                queryset = Appointment.objects.filter(patient=patient_profile)
            else:
                queryset = Appointment.objects.none()
        
        # Apply filters
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        date_filter = self.request.GET.get('date')
        if date_filter == 'today':
            queryset = queryset.filter(appointment_date=timezone.now().date())
        elif date_filter == 'week':
            week_start = timezone.now().date() - timedelta(days=timezone.now().weekday())
            week_end = week_start + timedelta(days=6)
            queryset = queryset.filter(appointment_date__range=[week_start, week_end])
        
        doctor_filter = self.request.GET.get('doctor')
        if doctor_filter:
            queryset = queryset.filter(doctor_id=doctor_filter)
        
        return queryset.select_related(
            'patient__user', 'doctor__user', 'hospital'
        ).order_by('-appointment_date', '-appointment_time')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        context['status_choices'] = Appointment.STATUS_CHOICES
        
        if user.is_admin or user.is_aamil or user.is_moze_coordinator:
            context['doctors'] = Doctor.objects.filter(is_active=True).select_related('user')
        
        context['current_filters'] = {
            'status': self.request.GET.get('status', ''),
            'date': self.request.GET.get('date', ''),
            'doctor': self.request.GET.get('doctor', ''),
        }
        return context


@login_required
def appointment_detail(request, pk):
    """Detailed view of a specific appointment"""
    appointment = get_object_or_404(Appointment, pk=pk)
    user = request.user
    
    # Check permissions
    can_view = (
        user.is_admin or
        user == appointment.patient.user or
        user == appointment.doctor.user or
        appointment.hospital.administrator == user or
        appointment.hospital.staff.filter(user=user).exists()
    )
    
    if not can_view:
        messages.error(request, "You don't have permission to view this appointment.")
        return redirect('mahalshifa:appointment_list')
    
    # Get related data
    medical_records = MedicalRecord.objects.filter(appointment=appointment)
    prescriptions = Prescription.objects.filter(appointment=appointment)
    lab_tests = LabTest.objects.filter(appointment=appointment)
    vital_signs = VitalSigns.objects.filter(appointment=appointment).order_by('-recorded_at')
    
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
    """Detailed view of a specific patient"""
    patient = get_object_or_404(Patient, pk=pk)
    user = request.user
    
    # Check permissions
    can_view = (
        user.is_admin or
        user == patient.user or
        patient.hospital.administrator == user or
        patient.hospital.staff.filter(user=user).exists() or
        patient.appointments.filter(doctor__user=user).exists()
    )
    
    if not can_view:
        messages.error(request, "You don't have permission to view this patient.")
        return redirect('mahalshifa:patient_list')
    
    # Get patient data
    appointments = patient.appointments.select_related('doctor__user', 'hospital').order_by('-appointment_date')
    medical_records = MedicalRecord.objects.filter(patient=patient).order_by('-created_at')
    prescriptions = Prescription.objects.filter(patient=patient).order_by('-created_at')
    lab_tests = LabTest.objects.filter(patient=patient).order_by('-created_at')
    admissions = Admission.objects.filter(patient=patient).order_by('-admission_date')
    emergency_contacts = patient.emergency_contacts.all()
    insurance_info = patient.insurance.all()
    
    # Recent vital signs
    recent_vitals = VitalSigns.objects.filter(
        appointment__patient=patient
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
            patient.hospital.administrator == user or
            patient.appointments.filter(doctor__user=user).exists()
        ),
    }
    
    return render(request, 'mahalshifa/patient_detail.html', context)


@login_required
def create_appointment(request):
    """Create a new appointment"""
    if request.method == 'POST':
        user = request.user
        
        # Get form data
        patient_id = request.POST.get('patient')
        doctor_id = request.POST.get('doctor')
        hospital_id = request.POST.get('hospital')
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        appointment_type = request.POST.get('appointment_type', 'regular')
        notes = request.POST.get('notes', '')
        
        try:
            patient = Patient.objects.get(id=patient_id)
            doctor = Doctor.objects.get(id=doctor_id)
            hospital = Hospital.objects.get(id=hospital_id)
            
            # Check permissions
            can_create = (
                user.is_admin or
                user == patient.user or
                hospital.administrator == user or
                hospital.staff.filter(user=user).exists()
            )
            
            if not can_create:
                return JsonResponse({'error': 'Permission denied'}, status=403)
            
            # Create appointment
            appointment = Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                hospital=hospital,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                appointment_type=appointment_type,
                notes=notes,
                status='scheduled'
            )
            
            messages.success(request, 'Appointment created successfully.')
            return JsonResponse({
                'success': True,
                'appointment_id': appointment.id,
                'redirect_url': f'/mahalshifa/appointments/{appointment.id}/'
            })
            
        except (Patient.DoesNotExist, Doctor.DoesNotExist, Hospital.DoesNotExist):
            return JsonResponse({'error': 'Invalid selection'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    # GET request - show form
    user = request.user
    
    if user.is_admin:
        patients = Patient.objects.filter(is_active=True)
        doctors = Doctor.objects.filter(is_active=True)
        hospitals = Hospital.objects.filter(is_active=True)
    elif user.is_aamil or user.is_moze_coordinator:
        user_hospitals = Hospital.objects.filter(
            Q(administrator=user) | Q(staff__user=user)
        )
        patients = Patient.objects.filter(hospital__in=user_hospitals, is_active=True)
        doctors = Doctor.objects.filter(hospital__in=user_hospitals, is_active=True)
        hospitals = user_hospitals
    else:
        # Patients can create appointments for themselves
        patient_profile = Patient.objects.filter(user=user).first()
        if patient_profile:
            patients = Patient.objects.filter(id=patient_profile.id)
            doctors = Doctor.objects.filter(hospital=patient_profile.hospital, is_active=True)
            hospitals = Hospital.objects.filter(id=patient_profile.hospital.id)
        else:
            patients = Patient.objects.none()
            doctors = Doctor.objects.none()
            hospitals = Hospital.objects.none()
    
    context = {
        'patients': patients,
        'doctors': doctors,
        'hospitals': hospitals,
        'appointment_types': Appointment.APPOINTMENT_TYPES,
    }
    
    return render(request, 'mahalshifa/create_appointment.html', context)


@login_required
def medical_analytics(request):
    """Medical analytics dashboard"""
    user = request.user
    
    # Check permissions
    if not (user.is_admin or user.is_aamil or user.is_moze_coordinator):
        messages.error(request, "You don't have permission to view analytics.")
        return redirect('mahalshifa:dashboard')
    
    # Base queryset
    if user.is_admin:
        hospitals = Hospital.objects.all()
        appointments = Appointment.objects.all()
        patients = Patient.objects.all()
    else:
        hospitals = Hospital.objects.filter(
            Q(administrator=user) | Q(staff__user=user)
        )
        appointments = Appointment.objects.filter(hospital__in=hospitals)
        patients = Patient.objects.filter(hospital__in=hospitals)
    
    # Time-based statistics
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    stats = {
        'total_appointments': appointments.count(),
        'this_week': appointments.filter(appointment_date__gte=week_ago).count(),
        'this_month': appointments.filter(appointment_date__gte=month_ago).count(),
        'total_patients': patients.count(),
        'active_patients': patients.filter(is_active=True).count(),
        'emergency_cases': appointments.filter(appointment_type='emergency').count(),
    }
    
    # Department performance
    dept_performance = Department.objects.filter(
        hospital__in=hospitals
    ).annotate(
        appointment_count=Count('doctors__appointments'),
        patient_count=Count('doctors__appointments__patient', distinct=True)
    ).order_by('-appointment_count')
    
    # Monthly appointment trends
    monthly_trends = []
    for i in range(12):
        month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
        month_appointments = appointments.filter(
            appointment_date__year=month_start.year,
            appointment_date__month=month_start.month
        ).count()
        monthly_trends.append({
            'month': month_start.strftime('%b %Y'),
            'count': month_appointments
        })
    
    # Top doctors by appointments
    top_doctors = Doctor.objects.filter(
        hospital__in=hospitals
    ).annotate(
        appointment_count=Count('appointments')
    ).order_by('-appointment_count')[:10]
    
    # Hospital comparison
    hospital_stats = hospitals.annotate(
        appointment_count=Count('appointments'),
        patient_count=Count('patients'),
        doctor_count=Count('doctors')
    ).order_by('-appointment_count')
    
    context = {
        'stats': stats,
        'dept_performance': dept_performance,
        'monthly_trends': monthly_trends[::-1],
        'top_doctors': top_doctors,
        'hospital_stats': hospital_stats,
        'user_role': user.get_role_display(),
    }
    
    return render(request, 'mahalshifa/analytics.html', context)


@login_required
def inventory_management(request):
    """Inventory management for hospitals"""
    user = request.user
    
    # Check permissions
    if not (user.is_admin or user.is_aamil or user.is_moze_coordinator):
        messages.error(request, "You don't have permission to manage inventory.")
        return redirect('mahalshifa:dashboard')
    
    # Base queryset
    if user.is_admin:
        hospitals = Hospital.objects.all()
    else:
        hospitals = Hospital.objects.filter(
            Q(administrator=user) | Q(staff__user=user)
        )
    
    inventory_items = InventoryItem.objects.filter(
        inventory__hospital__in=hospitals
    ).select_related('inventory__hospital')
    
    # Low stock items
    low_stock_items = inventory_items.filter(
        current_stock__lte=models.F('minimum_stock')
    )
    
    # Recently updated items
    recent_updates = inventory_items.order_by('-last_updated')[:10]
    
    # Inventory by hospital
    hospital_inventory = {}
    for hospital in hospitals:
        hospital_inventory[hospital] = inventory_items.filter(
            inventory__hospital=hospital
        ).count()
    
    context = {
        'hospitals': hospitals,
        'inventory_items': inventory_items,
        'low_stock_items': low_stock_items,
        'recent_updates': recent_updates,
        'hospital_inventory': hospital_inventory,
        'total_items': inventory_items.count(),
        'low_stock_count': low_stock_items.count(),
    }
    
    return render(request, 'mahalshifa/inventory.html', context)


@login_required
def export_medical_data(request):
    """Export medical data to CSV"""
    import csv
    
    user = request.user
    
    # Check permissions
    if not (user.is_admin or user.is_aamil or user.is_moze_coordinator):
        messages.error(request, "You don't have permission to export data.")
        return redirect('mahalshifa:dashboard')
    
    data_type = request.GET.get('type', 'appointments')
    
    # Base queryset
    if user.is_admin:
        hospitals = Hospital.objects.all()
    else:
        hospitals = Hospital.objects.filter(
            Q(administrator=user) | Q(staff__user=user)
        )
    
    response = HttpResponse(content_type='text/csv')
    
    if data_type == 'appointments':
        response['Content-Disposition'] = 'attachment; filename="appointments.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Patient', 'Doctor', 'Hospital', 'Date', 'Time', 
            'Type', 'Status', 'Notes'
        ])
        
        appointments = Appointment.objects.filter(
            hospital__in=hospitals
        ).select_related('patient__user', 'doctor__user', 'hospital')
        
        for appointment in appointments:
            writer.writerow([
                appointment.id,
                appointment.patient.user.get_full_name(),
                appointment.doctor.user.get_full_name(),
                appointment.hospital.name,
                appointment.appointment_date,
                appointment.appointment_time,
                appointment.get_appointment_type_display(),
                appointment.get_status_display(),
                appointment.notes
            ])
    
    elif data_type == 'patients':
        response['Content-Disposition'] = 'attachment; filename="patients.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'Patient ID', 'Name', 'ITS ID', 'Hospital', 'Blood Group', 
            'Phone', 'Email', 'Created Date'
        ])
        
        patients = Patient.objects.filter(
            hospital__in=hospitals
        ).select_related('user', 'hospital')
        
        for patient in patients:
            writer.writerow([
                patient.patient_id,
                patient.user.get_full_name(),
                patient.user.its_id,
                patient.hospital.name,
                patient.blood_group,
                patient.user.phone_number,
                patient.user.email,
                patient.created_at.strftime('%Y-%m-%d')
            ])
    
    return response
