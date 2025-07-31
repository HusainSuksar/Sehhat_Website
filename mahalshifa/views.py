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
import json
import csv
from datetime import datetime, timedelta, date, time
from decimal import Decimal

from .models import (
    Hospital, Department, Doctor, Patient, Appointment, MedicalRecord,
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
    
    # Recent appointments
    recent_appointments = appointments.select_related(
        'patient__user_account', 'doctor__user', 'doctor__hospital'
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
    
    # Department statistics - simplified without complex joins
    dept_stats = []
    if can_manage:
        dept_stats = Department.objects.filter(
            hospital__in=hospitals
        )[:5]
    
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
    ).select_related('patient__user_account', 'room', 'hospital').order_by('-admission_date')[:5]
    
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
            user.role == 'admin' or
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
            return Patient.objects.all()
        elif user.is_aamil or user.is_moze_coordinator:
            return Patient.objects.filter(registered_moze__aamil=user)
        elif user.is_doctor:
            try:
                from .models import Doctor as MahalshifaDoctor
                doctor_profile = MahalshifaDoctor.objects.get(user=user)
                return Patient.objects.filter(appointments__doctor=doctor_profile).distinct()
            except MahalshifaDoctor.DoesNotExist:
                return Patient.objects.none()
            except Exception as e:
                print(f"Error loading doctor patients for user {user.username}: {e}")
                return Patient.objects.none()
        else:
            # Patients can only see their own record
            try:
                return Patient.objects.filter(id=user.patient_record.id)
            except AttributeError:
                return Patient.objects.none()
            except Exception as e:
                print(f"Error loading patient record for user {user.username}: {e}")
                return Patient.objects.none()
    
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
    
    # Check permissions
    can_view = (
        user.is_admin or 
        user.is_aamil or 
        user.is_moze_coordinator or
        appointment.doctor.user == user or
        appointment.patient.user_account == user
    )
    
    if not can_view:
        messages.error(request, 'You do not have permission to view this appointment.')
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
    """Detailed view of a patient"""
    patient = get_object_or_404(Patient, pk=pk)
    user = request.user
    
    # Check permissions
    can_view = (
        user.is_admin or 
        user.is_aamil or 
        user.is_moze_coordinator or
        patient.user_account == user
    )
    
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
    
    def test_func(self):
        return self.request.user.is_admin or self.request.user.is_doctor
    
    def form_valid(self, form):
        form.instance.doctor = self.request.user.mahalshifa_doctor_profile
        messages.success(self.request, 'Medical record created successfully!')
        return super().form_valid(form)


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
