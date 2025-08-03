from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.urls import reverse_lazy
from django.db.models import Q, Count, Avg, Sum
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models.functions import TruncDate, TruncMonth

from .models import Moze, MozeComment, MozeSettings
from .forms import MozeForm, MozeCommentForm, MozeSettingsForm
from accounts.models import User
from accounts.permissions import can_user_manage_moze, get_moze_data_for_user
from mahalshifa.models import Patient, Appointment, MedicalRecord, Doctor as MahalshifaDoctor
from surveys.models import Survey, SurveyResponse
from evaluation.models import EvaluationForm, EvaluationSubmission
from araz.models import Petition


class MozeAccessMixin(UserPassesTestMixin):
    """Mixin to check if user has access to Moze management"""
    def test_func(self):
        return (self.request.user.is_admin or 
                self.request.user.role == 'aamil' or 
                self.request.user.role == 'moze_coordinator')


@login_required
def dashboard(request):
    """Moze dashboard with analytics and quick actions"""
    user = request.user
    
    # Get user's accessible mozes
    if user.is_admin:
        mozes = Moze.objects.all()
    elif user.role == 'aamil':
        mozes = user.managed_mozes.all()
    elif user.role == 'moze_coordinator':
        mozes = user.coordinated_mozes.all()
    else:
        mozes = Moze.objects.none()
    
    # Statistics
    total_mozes = mozes.count()
    active_mozes = mozes.filter(is_active=True).count()
    team_members_count = User.objects.filter(moze_teams__in=mozes).distinct().count()
    
    # Recent activities
    recent_comments = MozeComment.objects.filter(
        moze__in=mozes,
        is_active=True
    ).select_related('author', 'moze').order_by('-created_at')[:5]
    
    # Moze performance metrics
    moze_stats = []
    for moze in mozes[:6]:  # Top 6 mozes for dashboard
        stats = {
            'moze': moze,
            'team_count': moze.get_team_count(),
            'comments_count': moze.comments.filter(is_active=True).count(),
            'last_activity': moze.comments.filter(is_active=True).first(),
        }
        moze_stats.append(stats)
    
    context = {
        'total_mozes': total_mozes,
        'active_mozes': active_mozes,
        'team_members_count': team_members_count,
        'recent_comments': recent_comments,
        'moze_stats': moze_stats,
        'user_role': user.get_role_display(),
    }
    
    return render(request, 'moze/dashboard.html', context)


@login_required
def moze_profile_dashboard(request, moze_id):
    """
    Comprehensive Moze profile dashboard showing all related data
    """
    moze = get_object_or_404(Moze, id=moze_id)
    user = request.user
    
    # Check if user has access to this Moze
    if not can_user_manage_moze(user, moze):
        messages.error(request, "You don't have permission to view this Moze.")
        return redirect('moze:dashboard')
    
    # Get all related data for this Moze
    patients = Patient.objects.filter(registered_moze=moze)
    appointments = Appointment.objects.filter(moze=moze)
    medical_records = MedicalRecord.objects.filter(moze=moze)
    doctors = MahalshifaDoctor.objects.filter(appointments__moze=moze).distinct()
    
    # Surveys and evaluations
    surveys = Survey.objects.filter(created_by__managed_mozes=moze)
    survey_responses = SurveyResponse.objects.filter(survey__in=surveys)
    evaluations = EvaluationForm.objects.filter(created_by__managed_mozes=moze)
    evaluation_submissions = EvaluationSubmission.objects.filter(evaluation__in=evaluations)
    
    # Petitions/Araz
    petitions = Petition.objects.filter(created_by__managed_mozes=moze)
    
    # Team members
    team_members = moze.team_members.all()
    coordinators = User.objects.filter(coordinated_mozes=moze)
    
    # Statistics
    stats = {
        'total_patients': patients.count(),
        'active_patients': patients.filter(is_active=True).count(),
        'total_appointments': appointments.count(),
        'today_appointments': appointments.filter(appointment_date=timezone.now().date()).count(),
        'upcoming_appointments': appointments.filter(
            appointment_date__gte=timezone.now().date(),
            status__in=['scheduled', 'confirmed']
        ).count(),
        'total_medical_records': medical_records.count(),
        'total_doctors': doctors.count(),
        'active_doctors': doctors.filter(user__is_active=True).count(),
        'total_surveys': surveys.count(),
        'survey_responses': survey_responses.count(),
        'total_evaluations': evaluations.count(),
        'evaluation_submissions': evaluation_submissions.count(),
        'total_petitions': petitions.count(),
        'pending_petitions': petitions.filter(status='pending').count(),
        'team_members_count': team_members.count(),
        'coordinators_count': coordinators.count(),
    }
    
    # Recent activities
    recent_appointments = appointments.order_by('-appointment_date')[:10]
    recent_medical_records = medical_records.order_by('-consultation_date')[:10]
    recent_survey_responses = survey_responses.order_by('-submitted_at')[:10]
    recent_petitions = petitions.order_by('-created_at')[:10]
    
    # Monthly trends (last 6 months)
    months = []
    patient_counts = []
    appointment_counts = []
    
    for i in range(6):
        month = timezone.now() - timedelta(days=30*i)
        month_start = month.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        months.append(month_start.strftime('%B %Y'))
        patient_counts.append(
            patients.filter(registration_date__range=[month_start, month_end]).count()
        )
        appointment_counts.append(
            appointments.filter(appointment_date__range=[month_start, month_end]).count()
        )
    
    # Doctor performance
    doctor_stats = []
    for doctor in doctors[:10]:  # Top 10 doctors
        doctor_appointments = appointments.filter(doctor=doctor)
        doctor_records = medical_records.filter(doctor=doctor)
        
        doctor_stats.append({
            'doctor': doctor,
            'appointments_count': doctor_appointments.count(),
            'medical_records_count': doctor_records.count(),
            'recent_appointments': doctor_appointments.order_by('-appointment_date')[:5],
        })
    
    # Patient demographics
    gender_stats = patients.values('gender').annotate(count=Count('id'))
    age_groups = {
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
    
    context = {
        'moze': moze,
        'stats': stats,
        'patients': patients,
        'appointments': appointments,
        'medical_records': medical_records,
        'doctors': doctors,
        'surveys': surveys,
        'survey_responses': survey_responses,
        'evaluations': evaluations,
        'evaluation_submissions': evaluation_submissions,
        'petitions': petitions,
        'team_members': team_members,
        'coordinators': coordinators,
        'recent_appointments': recent_appointments,
        'recent_medical_records': recent_medical_records,
        'recent_survey_responses': recent_survey_responses,
        'recent_petitions': recent_petitions,
        'doctor_stats': doctor_stats,
        'months': months,
        'patient_counts': patient_counts,
        'appointment_counts': appointment_counts,
        'gender_stats': gender_stats,
        'age_groups': age_groups,
        'user_role': user.get_role_display(),
    }
    
    return render(request, 'moze/moze_profile_dashboard.html', context)


class MozeListView(LoginRequiredMixin, MozeAccessMixin, ListView):
    """List all accessible mozes with search and filtering"""
    model = Moze
    template_name = 'moze/moze_list.html'
    context_object_name = 'mozes'
    paginate_by = 12
    
    def get_queryset(self):
        user = self.request.user
        
        # Base queryset based on user role
        if user.is_admin:
            queryset = Moze.objects.all()
        elif user.role == 'aamil':
            queryset = user.managed_mozes.all()
        elif user.role == 'moze_coordinator':
            queryset = user.coordinated_mozes.all()
        else:
            queryset = Moze.objects.none()
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(location__icontains=search) |
                Q(address__icontains=search)
            )
        
        # Filter by status
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        return queryset.select_related('aamil', 'moze_coordinator')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
        context['user_role'] = self.request.user.get_role_display()
        return context


class MozeDetailView(LoginRequiredMixin, MozeAccessMixin, DetailView):
    """Detailed view of a single Moze with comments and team info"""
    model = Moze
    template_name = 'moze/moze_detail.html'
    context_object_name = 'moze'
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Moze.objects.all()
        elif user.role == 'aamil':
            return user.managed_mozes.all()
        elif user.role == 'moze_coordinator':
            return user.coordinated_mozes.all()
        return Moze.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        moze = self.get_object()
        
        # Get related data
        patients = Patient.objects.filter(registered_moze=moze)
        appointments = Appointment.objects.filter(moze=moze)
        doctors = MahalshifaDoctor.objects.filter(appointments__moze=moze).distinct()
        
        # Statistics
        context.update({
            'patients_count': patients.count(),
            'appointments_count': appointments.count(),
            'doctors_count': doctors.count(),
            'team_members': moze.team_members.all(),
            'comments': moze.comments.filter(is_active=True).select_related('author'),
            'recent_appointments': appointments.order_by('-appointment_date')[:5],
            'recent_patients': patients.order_by('-registration_date')[:5],
            'user_role': self.request.user.get_role_display(),
        })
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle comment creation"""
        moze = self.get_object()
        
        # Debug: Print POST data
        print(f"POST data: {request.POST}")
        
        form = MozeCommentForm(request.POST)
        
        if form.is_valid():
            comment = form.save(commit=False)
            comment.moze = moze
            comment.author = request.user
            comment.save()
            messages.success(request, 'Comment added successfully.')
        else:
            # Add more detailed error messages
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            messages.error(request, f'Error adding comment: {", ".join(error_messages)}')
            print(f"Form errors: {form.errors}")
        
        return redirect('moze:detail', pk=moze.pk)


class MozeCreateView(LoginRequiredMixin, MozeAccessMixin, CreateView):
    """Create a new Moze"""
    model = Moze
    form_class = MozeForm
    template_name = 'moze/moze_form.html'
    success_url = reverse_lazy('moze:list')
    
    def form_valid(self, form):
        # Set the creator as aamil if they are aamil role
        if self.request.user.role == 'aamil':
            form.instance.aamil = self.request.user
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class MozeEditView(LoginRequiredMixin, MozeAccessMixin, UpdateView):
    """Edit an existing Moze"""
    model = Moze
    form_class = MozeForm
    template_name = 'moze/moze_form.html'
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Moze.objects.all()
        elif user.role == 'aamil':
            return user.managed_mozes.all()
        elif user.role == 'moze_coordinator':
            return user.coordinated_mozes.all()
        return Moze.objects.none()
    
    def get_success_url(self):
        return reverse_lazy('moze:detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Moze updated successfully.')
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


@login_required
def moze_delete(request, pk):
    """Delete a Moze"""
    moze = get_object_or_404(Moze, pk=pk)
    
    # Check permissions
    if not can_user_manage_moze(request.user, moze):
        messages.error(request, "You don't have permission to delete this Moze.")
        return redirect('moze:list')
    
    if request.method == 'POST':
        moze.delete()
        messages.success(request, 'Moze deleted successfully.')
        return redirect('moze:list')
    
    return render(request, 'moze/moze_confirm_delete.html', {'moze': moze})


@login_required
def comment_delete(request, pk):
    """Delete a comment"""
    comment = get_object_or_404(MozeComment, pk=pk)
    
    # Check if user can delete this comment
    if not (request.user.is_admin or 
            request.user == comment.author or 
            can_user_manage_moze(request.user, comment.moze)):
        messages.error(request, "You don't have permission to delete this comment.")
        return redirect('moze:detail', pk=comment.moze.pk)
    
    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Comment deleted successfully.')
        return redirect('moze:detail', pk=comment.moze.pk)
    
    return render(request, 'moze/comment_confirm_delete.html', {'comment': comment})


@login_required
def moze_analytics(request):
    """Moze analytics and reporting"""
    user = request.user
    
    # Get accessible mozes
    mozes = get_moze_data_for_user(user)
    if not mozes:
        messages.error(request, "No Mozes accessible.")
        return redirect('moze:dashboard')
    
    # Analytics data
    total_patients = Patient.objects.filter(registered_moze__in=mozes).count()
    total_appointments = Appointment.objects.filter(moze__in=mozes).count()
    total_doctors = MahalshifaDoctor.objects.filter(appointments__moze__in=mozes).distinct().count()
    
    # Monthly trends
    months = []
    patient_counts = []
    appointment_counts = []
    
    for i in range(12):
        month = timezone.now() - timedelta(days=30*i)
        month_start = month.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        months.append(month_start.strftime('%B %Y'))
        patient_counts.append(
            Patient.objects.filter(
                registered_moze__in=mozes,
                registration_date__range=[month_start, month_end]
            ).count()
        )
        appointment_counts.append(
            Appointment.objects.filter(
                moze__in=mozes,
                appointment_date__range=[month_start, month_end]
            ).count()
        )
    
    context = {
        'total_patients': total_patients,
        'total_appointments': total_appointments,
        'total_doctors': total_doctors,
        'months': months,
        'patient_counts': patient_counts,
        'appointment_counts': appointment_counts,
        'user_role': user.get_role_display(),
    }
    
    return render(request, 'moze/moze_analytics.html', context)
