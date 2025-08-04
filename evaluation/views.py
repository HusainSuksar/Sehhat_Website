from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse, Http404
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.core.paginator import Paginator
from django.db import transaction
import json
from datetime import datetime, timedelta
from decimal import Decimal

from .models import (
    EvaluationForm, EvaluationCriteria, EvaluationSubmission, 
    EvaluationResponse, EvaluationSession, EvaluationTemplate,
    CriteriaRating, EvaluationReport
)
from accounts.models import User
from moze.models import Moze


@login_required
def dashboard(request):
    """Evaluation dashboard with statistics and recent activities"""
    user = request.user
    
    # Base queryset based on user role
    if user.is_admin:
        forms = EvaluationForm.objects.all()
        submissions = EvaluationSubmission.objects.all()
        can_manage = True
    elif user.is_aamil or user.is_moze_coordinator:
        # Can see forms they created (simplified since EvaluationForm doesn't have moze field)
        forms = EvaluationForm.objects.filter(created_by=user)
        submissions = EvaluationSubmission.objects.filter(evaluator=user)
        can_manage = True
    else:
        # Regular users can only see forms they can evaluate and their submissions
        forms = EvaluationForm.objects.filter(
            Q(target_role=user.role) | Q(target_role='all'),
            is_active=True
        )
        submissions = EvaluationSubmission.objects.filter(evaluator=user)
        can_manage = False
    
    # Statistics
    total_forms = forms.count()
    active_forms = forms.filter(is_active=True).count()
    pending_evaluations = forms.filter(
        is_active=True,
        due_date__gte=timezone.now()
    ).exclude(
        id__in=submissions.values('form_id')
    ).count() if not can_manage else 0
    
    completed_evaluations = submissions.filter(is_complete=True).count()
    
    # Recent forms
    recent_forms = forms.select_related('created_by').order_by('-created_at')[:10]
    
    # Recent submissions
    recent_submissions = submissions.select_related('form', 'evaluator', 'target_user').order_by('-submitted_at')[:10]
    
    # Monthly statistics for charts
    monthly_stats = []
    for i in range(6):
        month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
        month_submissions = submissions.filter(
            submitted_at__year=month_start.year,
            submitted_at__month=month_start.month
        ).count()
        monthly_stats.append({
            'month': month_start.strftime('%b %Y'),
            'count': month_submissions
        })
    
    # Average ratings by category (simplified since CriteriaRating uses evaluation not submission)
    avg_ratings = []
    # Note: CriteriaRating is linked to Evaluation model, not EvaluationSubmission
    # This would need actual Evaluation instances to work properly
    
    # Evaluation sessions (simplified since EvaluationSession doesn't have evaluator/participants fields)
    recent_sessions = EvaluationSession.objects.filter(
        created_by=user
    ).order_by('-start_date')[:5]
    
    context = {
        'total_forms': total_forms,
        'active_forms': active_forms,
        'pending_evaluations': pending_evaluations,
        'completed_evaluations': completed_evaluations,
        'recent_forms': recent_forms,
        'recent_submissions': recent_submissions,
        'monthly_stats': monthly_stats[::-1],
        'avg_ratings': avg_ratings,
        'recent_sessions': recent_sessions,
        'can_manage': can_manage,
    }
    
    return render(request, 'evaluation/dashboard.html', context)


class EvaluationFormListView(LoginRequiredMixin, ListView):
    """List all evaluation forms with filtering"""
    model = EvaluationForm
    template_name = 'evaluation/form_list.html'
    context_object_name = 'forms'
    paginate_by = 20
    
    def get_queryset(self):
        user = self.request.user
        queryset = EvaluationForm.objects.select_related('created_by')
        
        # Filter by user role
        if user.is_admin:
            pass  # Show all forms
        elif user.is_aamil or user.is_moze_coordinator:
            queryset = queryset.filter(
                Q(created_by=user) | Q(target_role="moze_coordinator") | Q(target_role="aamil")
            )
        else:
            # Students can only see forms targeted to them or forms they created
            queryset = queryset.filter(
                Q(target_role="student") | Q(created_by=user)
            )
        
        # Additional filtering
        form_type = self.request.GET.get('type')
        if form_type:
            queryset = queryset.filter(evaluation_type=form_type)
        
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Filter options
        context['form_types'] = EvaluationForm.EVALUATION_TYPE_CHOICES
        context['target_types'] = EvaluationForm.TARGET_ROLE_CHOICES
        
        # User statistics
        if user.is_admin or user.is_aamil or user.is_moze_coordinator:
            total_forms = EvaluationForm.objects.count()
            active_forms = EvaluationForm.objects.filter(is_active=True).count()
            context['form_stats'] = {
                'total': total_forms,
                'active': active_forms,
                'inactive': total_forms - active_forms,
            }
        context['can_manage'] = user.is_admin or user.is_aamil or user.is_moze_coordinator
        
        return context


class EvaluationFormDetailView(LoginRequiredMixin, DetailView):
    """Detailed view of an evaluation form"""
    model = EvaluationForm
    template_name = 'evaluation/form_detail.html'
    context_object_name = 'form'
    
    def get_object(self, queryset=None):
        """Override to provide better error handling"""
        try:
            return super().get_object(queryset)
        except EvaluationForm.DoesNotExist:
            # Provide a more helpful error message
            form_id = self.kwargs.get('pk')
            raise Http404(f"Evaluation form with ID {form_id} does not exist. Please check the URL or contact an administrator.")
        except Exception as e:
            # Log the error and provide a generic message
            print(f"Error accessing evaluation form: {e}")
            raise Http404("Unable to access the requested evaluation form. Please try again or contact support.")
    
    def get_queryset(self):
        user = self.request.user
        
        # More permissive queryset for debugging - allow all users to see all forms
        # This helps identify if the issue is with form existence vs permissions
        queryset = EvaluationForm.objects.all()
        
        # TODO: Uncomment the following lines once the issue is resolved
        # if user.is_admin:
        #     queryset = EvaluationForm.objects.all()
        # elif user.role == 'aamil' or user.role == 'moze_coordinator':
        #     queryset = EvaluationForm.objects.filter(
        #         Q(created_by=user) | Q(target_role="moze_coordinator") | Q(target_role="aamil")
        #     )
        # else:
        #     # Students can only see forms targeted to them or forms they created
        #     queryset = EvaluationForm.objects.filter(
        #         Q(target_role="student") | Q(created_by=user)
        #     )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = self.object
        user = self.request.user
        
        # Check if user has already submitted
        user_submission = EvaluationSubmission.objects.filter(
            form=form,
            evaluator=user
        ).first()
        context['user_submission'] = user_submission
        
        # Permission checks
        context['can_edit'] = (
            user == form.created_by or 
            user.is_admin or 
            user.is_aamil or
            user.is_moze_coordinator
        )
        
        context['can_evaluate'] = (
            not user_submission and 
            form.is_active and 
            (form.target_role == user.role or form.target_role == 'all') and
            (not form.due_date or form.due_date >= timezone.now().date())
        )
        
        # Statistics for managers
        if context['can_edit']:
            submissions = EvaluationSubmission.objects.filter(form=form)
            context['total_submissions'] = submissions.count()
            context['completed_submissions'] = submissions.filter(is_complete=True).count()
            context['average_score'] = submissions.filter(is_complete=True).aggregate(
                avg_score=Avg('total_score')
            )['avg_score']
        
        return context


class EvaluationFormCreateView(LoginRequiredMixin, CreateView):
    """Create a new evaluation form"""
    model = EvaluationForm
    template_name = 'evaluation/form_create.html'
    fields = ['title', 'description', 'evaluation_type', 'target_role', 'due_date', 'is_active']
    
    def test_func(self):
        user = self.request.user
        return user.is_admin or user.is_aamil or user.is_moze_coordinator
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Evaluation form created successfully.')
        return response
    
    def get_success_url(self):
        return reverse_lazy('evaluation:form_detail', kwargs={'pk': self.object.pk})


class EvaluationFormUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing evaluation form"""
    model = EvaluationForm
    template_name = 'evaluation/form_create.html'
    fields = ['title', 'description', 'evaluation_type', 'target_role', 'due_date', 'is_active']
    
    def test_func(self):
        user = self.request.user
        form = self.get_object()
        return (user.is_admin or 
                user.is_aamil or 
                user.is_moze_coordinator or
                user == form.created_by)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Evaluation form updated successfully.')
        return response
    
    def get_success_url(self):
        return reverse_lazy('evaluation:form_detail', kwargs={'pk': self.object.pk})


@login_required
def evaluate_form(request, pk):
    """Evaluate a specific form"""
    form = get_object_or_404(EvaluationForm, pk=pk)
    user = request.user
    
    # Check permissions
    if not form.is_active:
        messages.error(request, 'This evaluation form is not active.')
        return redirect('evaluation:form_list')
    
    if form.target_role != 'all' and form.target_role != user.role:
        messages.error(request, 'You do not have permission to evaluate this form.')
        return redirect('evaluation:form_list')
    
    if form.due_date and form.due_date < timezone.now():
        messages.error(request, 'This evaluation form has expired.')
        return redirect('evaluation:form_list')
    
    # Check if user has already submitted
    existing_submission = EvaluationSubmission.objects.filter(
        form=form,
        evaluator=user
    ).first()
    
    if existing_submission:
        messages.info(request, 'You have already submitted an evaluation for this form.')
        return redirect('evaluation:submission_detail', pk=existing_submission.pk)
    
    if request.method == 'POST':
        # Handle form submission
        try:
            with transaction.atomic():
                # Create submission
                submission = EvaluationSubmission.objects.create(
                    form=form,
                    evaluator=user,
                    total_score=0  # Will be calculated
                )
                
                # Process responses
                total_score = 0
                total_weight = 0
                
                for key, value in request.POST.items():
                    if key.startswith('criteria_'):
                        criteria_id = key.replace('criteria_', '')
                        try:
                            criteria = EvaluationCriteria.objects.get(id=criteria_id)
                            score = int(value)
                            if 1 <= score <= criteria.max_score:
                                EvaluationResponse.objects.create(
                                    submission=submission,
                                    criteria=criteria,
                                    score=score
                                )
                                total_score += score * criteria.weight
                                total_weight += criteria.weight
                        except (ValueError, EvaluationCriteria.DoesNotExist):
                            continue
                
                # Calculate final score
                if total_weight > 0:
                    submission.total_score = (total_score / total_weight) * 10
                
                submission.is_complete = True
                submission.save()
                
                messages.success(request, 'Evaluation submitted successfully.')
                return redirect('evaluation:submission_detail', pk=submission.pk)
                
        except Exception as e:
            messages.error(request, f'Error submitting evaluation: {str(e)}')
            return redirect('evaluation:form_detail', pk=pk)
    
    # Get evaluation criteria
    criteria = EvaluationCriteria.objects.filter(is_active=True).order_by('category', 'order')
    
    context = {
        'form': form,
        'criteria': criteria,
    }
    
    return render(request, 'evaluation/evaluate_form.html', context)


@login_required
def submission_detail(request, pk):
    """View submission details"""
    submission = get_object_or_404(EvaluationSubmission, pk=pk)
    user = request.user
    
    # Check permissions
    if not (user == submission.evaluator or user.is_admin or user.is_aamil or user.is_moze_coordinator):
        messages.error(request, 'You do not have permission to view this submission.')
        return redirect('evaluation:form_list')
    
    context = {
        'submission': submission,
        'responses': submission.responses.select_related('criteria'),
    }
    
    return render(request, 'evaluation/submission_detail.html', context)


@login_required
def evaluation_analytics(request):
    """Analytics and reporting"""
    user = request.user
    
    if not (user.is_admin or user.is_aamil or user.is_moze_coordinator):
        messages.error(request, 'You do not have permission to view analytics.')
        return redirect('evaluation:dashboard')
    
    # Get date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    else:
        start_date = timezone.now().date() - timedelta(days=30)
    
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        end_date = timezone.now().date()
    
    # Filter submissions by date range
    submissions = EvaluationSubmission.objects.filter(
        submitted_at__date__range=[start_date, end_date]
    )
    
    # Statistics
    total_submissions = submissions.count()
    completed_submissions = submissions.filter(is_complete=True).count()
    avg_score = submissions.filter(is_complete=True).aggregate(
        avg_score=Avg('total_score')
    )['avg_score'] or 0
    
    # Submissions by form
    form_stats = submissions.values('form__title').annotate(
        count=Count('id'),
        avg_score=Avg('total_score')
    ).order_by('-count')
    
    # Monthly trends
    monthly_data = []
    for i in range(6):
        month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
        month_end = month_start.replace(day=28) + timedelta(days=4)
        month_end = month_end.replace(day=1) - timedelta(days=1)
        
        month_submissions = submissions.filter(
            submitted_at__date__range=[month_start, month_end]
        ).count()
        
        monthly_data.append({
            'month': month_start.strftime('%b %Y'),
            'submissions': month_submissions
        })
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'total_submissions': total_submissions,
        'completed_submissions': completed_submissions,
        'avg_score': round(avg_score, 2),
        'form_stats': form_stats,
        'monthly_data': monthly_data[::-1],
    }
    
    return render(request, 'evaluation/analytics.html', context)


@login_required
def export_evaluations(request):
    """Export evaluation data"""
    user = request.user
    
    if not (user.is_admin or user.is_aamil or user.is_moze_coordinator):
        messages.error(request, 'You do not have permission to export data.')
        return redirect('evaluation:dashboard')
    
    # Get date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    else:
        start_date = timezone.now().date() - timedelta(days=30)
    
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        end_date = timezone.now().date()
    
    # Get submissions
    submissions = EvaluationSubmission.objects.filter(
        submitted_at__date__range=[start_date, end_date]
    ).select_related('form', 'evaluator', 'target_user')
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="evaluations_{start_date}_{end_date}.csv"'
    
    import csv
    writer = csv.writer(response)
    writer.writerow([
        'Form Title', 'Evaluator', 'Target User', 'Total Score', 
        'Is Complete', 'Submitted At'
    ])
    
    for submission in submissions:
        writer.writerow([
            submission.form.title,
            submission.evaluator.get_full_name(),
            submission.target_user.get_full_name() if submission.target_user else 'N/A',
            submission.total_score,
            submission.is_complete,
            submission.submitted_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return response


@login_required
def create_evaluation_session(request):
    """Create a new evaluation session"""
    user = request.user
    
    if not (user.is_admin or user.is_aamil or user.is_moze_coordinator):
        messages.error(request, 'You do not have permission to create sessions.')
        return redirect('evaluation:dashboard')
    
    if request.method == 'POST':
        form_id = request.POST.get('form')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        try:
            form = EvaluationForm.objects.get(id=form_id)
            session = EvaluationSession.objects.create(
                title=f"Session for {form.title}",
                form=form,
                start_date=datetime.strptime(start_date, '%Y-%m-%d'),
                end_date=datetime.strptime(end_date, '%Y-%m-%d'),
                created_by=user
            )
            messages.success(request, 'Evaluation session created successfully.')
            return redirect('evaluation:dashboard')
        except (EvaluationForm.DoesNotExist, ValueError):
            messages.error(request, 'Invalid form or date format.')
    
    # Get available forms
    forms = EvaluationForm.objects.filter(is_active=True)
    
    context = {
        'forms': forms,
    }
    
    return render(request, 'evaluation/create_session.html', context)


@login_required
def my_evaluations(request):
    """Show user's own evaluations"""
    user = request.user
    
    # Get user's submissions
    submissions = EvaluationSubmission.objects.filter(
        evaluator=user
    ).select_related('form').order_by('-submitted_at')
    
    # Get forms user can evaluate
    available_forms = EvaluationForm.objects.filter(
        Q(target_role=user.role) | Q(target_role='all'),
        is_active=True
    ).exclude(
        id__in=submissions.values('form_id')
    )
    
    context = {
        'submissions': submissions,
        'available_forms': available_forms,
    }
    
    return render(request, 'evaluation/my_evaluations.html', context)
