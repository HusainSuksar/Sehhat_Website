from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
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
    if user.role == 'admin':
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
        'user_role': user.get_role_display(),
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
        
        # Base queryset based on user role
        if user.role == 'admin':
            queryset = EvaluationForm.objects.all()
        elif user.is_aamil or user.is_moze_coordinator:
            queryset = EvaluationForm.objects.filter(created_by=user)
        else:
            queryset = EvaluationForm.objects.filter(
                Q(target_role=user.role) | Q(target_role='all'),
                is_active=True
            )
        
        # Apply filters
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        evaluation_type = self.request.GET.get('type')
        if evaluation_type:
            queryset = queryset.filter(evaluation_type=evaluation_type)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset.select_related('created_by').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['evaluation_types'] = EvaluationForm.EVALUATION_TYPE_CHOICES
        context['current_filters'] = {
            'status': self.request.GET.get('status', ''),
            'type': self.request.GET.get('type', ''),
            'search': self.request.GET.get('search', ''),
        }
        # Add progress and analytics for each form
        forms = context['forms']
        form_stats = {}
        for form in forms:
            total_targets = form.submissions.count()  # fallback if no target count logic
            total_submissions = form.submissions.filter(is_complete=True).count()
            avg_score = form.submissions.filter(is_complete=True).aggregate(avg=Avg('total_score'))['avg']
            # If you have a way to get total eligible users, use that for total_targets
            # For now, use total_submissions as denominator for progress
            progress = 0
            if total_targets > 0:
                progress = int((total_submissions / total_targets) * 100)
            form_stats[form.pk] = {
                'progress': progress,
                'participation': total_submissions,
                'avg_score': avg_score or 0,
            }
        context['form_stats'] = form_stats
        return context


class EvaluationFormDetailView(LoginRequiredMixin, DetailView):
    """Detailed view of an evaluation form"""
    model = EvaluationForm
    template_name = 'evaluation/form_detail.html'
    context_object_name = 'form'
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'admin':
            return EvaluationForm.objects.all()
        elif user.role == 'aamil' or user.role == 'moze_coordinator':
            return EvaluationForm.objects.filter(
                Q(created_by=user) | Q(target_role="moze_coordinator") | Q(target_role="aamil")
            )
        else:
            # Students can only see forms targeted to them or forms they created
            return EvaluationForm.objects.filter(
                Q(target_role="student") | Q(created_by=user)
            )
    
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
            user.role == 'admin' or 
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
        return user.role == 'admin' or user.is_aamil or user.is_moze_coordinator
    
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
        return (user.role == 'admin' or 
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
    try:
        form = EvaluationForm.objects.get(pk=pk)
    except EvaluationForm.DoesNotExist:
        messages.error(request, "Evaluation form not found.")
        return redirect('evaluation:form_list')
    
    user = request.user
    
    # Check if user can evaluate this form
    if not (user.role == 'admin' or 
            user.role == 'aamil' or 
            user.role == 'moze_coordinator' or
            (user.role == 'student' and form.target_role == 'student')):
        messages.error(request, "You don't have permission to evaluate this form.")
        return redirect('evaluation:form_list')
    
    # Check if already evaluated
    existing_submission = EvaluationSubmission.objects.filter(
        form=form, evaluator=user
    ).first()
    
    if existing_submission:
        messages.info(request, "You have already evaluated this form.")
        return redirect('evaluation:submission_detail', pk=existing_submission.pk)
    
    if request.method == 'POST':
        # Process evaluation submission
        try:
            # Create submission
            submission = EvaluationSubmission.objects.create(
                form=form,
                evaluator=user,
                submitted_at=timezone.now()
            )
            
            # Process criteria ratings
            total_score = 0
            criteria_count = 0
            
            # Get form criteria - use all active criteria since forms don't have direct criteria relationship
            criteria = EvaluationCriteria.objects.filter(is_active=True).order_by('order')
            
            for criteria_item in criteria:
                rating_key = f'criteria_{criteria_item.id}'
                rating_value = request.POST.get(rating_key)
                
                if rating_value:
                    try:
                        rating = int(rating_value)
                        if 1 <= rating <= 5:
                            CriteriaRating.objects.create(
                                submission=submission,
                                criteria=criteria_item,
                                score=rating
                            )
                            total_score += rating
                            criteria_count += 1
                    except ValueError:
                        continue
            
            # Calculate average score
            if criteria_count > 0:
                submission.total_score = total_score / criteria_count
                submission.is_complete = True
                submission.save()
            
            messages.success(request, "Evaluation submitted successfully!")
            return redirect('evaluation:submission_detail', pk=submission.pk)
            
        except Exception as e:
            messages.error(request, f"Error submitting evaluation: {str(e)}")
            return redirect('evaluation:form_list')
    
    # Get form criteria - use all active criteria since forms don't have direct criteria relationship
    criteria = EvaluationCriteria.objects.filter(is_active=True).order_by('order')
    
    context = {
        'form': form,
        'criteria': criteria,
    }
    
    return render(request, 'evaluation/evaluate_form.html', context)


@login_required
def submission_detail(request, pk):
    """View details of a specific submission"""
    submission = get_object_or_404(EvaluationSubmission, pk=pk)
    user = request.user
    
    # Check permissions
    can_view = (
        user == submission.evaluator or
        user == submission.target_user or
        user.role == 'admin' or
        user.is_aamil or
        user.is_moze_coordinator
    )
    
    if not can_view:
        messages.error(request, "You don't have permission to view this submission.")
        return redirect('evaluation:dashboard')
    
    context = {
        'submission': submission,
    }
    
    return render(request, 'evaluation/submission_detail.html', context)


@login_required
def evaluation_analytics(request):
    """Analytics dashboard for evaluations"""
    user = request.user
    
    # Check permissions
    if not (user.role == 'admin' or user.is_aamil or user.is_moze_coordinator):
        messages.error(request, "You don't have permission to view analytics.")
        return redirect('evaluation:dashboard')
    
    # Base queryset
    if user.role == 'admin':
        submissions = EvaluationSubmission.objects.all()
    else:
        submissions = EvaluationSubmission.objects.filter(
            Q(form__created_by=user) | Q(form__target_role="moze_coordinator")
        )
    
    # Time-based statistics
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    stats = {
        'total_submissions': submissions.count(),
        'this_week': submissions.filter(submitted_at__date__gte=week_ago).count(),
        'this_month': submissions.filter(submitted_at__date__gte=month_ago).count(),
        'completed': submissions.filter(is_complete=True).count(),
        'average_score': submissions.filter(is_complete=True).aggregate(
            avg=Avg('total_score')
        )['avg'] or 0,
    }
    
    # Evaluation type breakdown
    type_stats = submissions.values('form__evaluation_type').annotate(
        count=Count('id'),
        avg_score=Avg('total_score')
    ).order_by('-count')
    
    # Monthly trend
    monthly_trend = []
    for i in range(12):
        month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
        month_submissions = submissions.filter(
            submitted_at__year=month_start.year,
            submitted_at__month=month_start.month
        ).count()
        monthly_trend.append({
            'month': month_start.strftime('%b %Y'),
            'count': month_submissions
        })
    
    # Top performing areas (by criteria category) - disabled since CriteriaRating uses evaluation not submission
    category_performance = []
    # category_performance = CriteriaRating.objects.filter(
    #     evaluation__in=evaluations  # Would need actual evaluations
    # ).values('criteria__category').annotate(
    #     avg_rating=Avg('score'),
    #     count=Count('id')
    # ).order_by('-avg_rating')
    
    # Role-based performance
    role_performance = submissions.filter(is_complete=True).values(
        'evaluator__role'
    ).annotate(
        avg_score=Avg('total_score'),
        count=Count('id')
    ).order_by('-avg_score')
    
    context = {
        'stats': stats,
        'type_stats': type_stats,
        'monthly_trend': monthly_trend[::-1],
        'category_performance': category_performance,
        'role_performance': role_performance,
        'user_role': user.get_role_display(),
    }
    
    return render(request, 'evaluation/analytics.html', context)


@login_required
def export_evaluations(request):
    """Export evaluation data to CSV"""
    import csv
    
    user = request.user
    
    # Check permissions
    if not (user.role == 'admin' or user.is_aamil or user.is_moze_coordinator):
        messages.error(request, "You don't have permission to export data.")
        return redirect('evaluation:dashboard')
    
    # Base queryset
    if user.role == 'admin':
        submissions = EvaluationSubmission.objects.all()
    else:
        submissions = EvaluationSubmission.objects.filter(
            Q(form__created_by=user) | Q(form__target_role="moze_coordinator")
        )
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="evaluations.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Submission ID', 'Form Title', 'Evaluation Type', 'Evaluator', 
        'Evaluatee', 'Total Score', 'Submitted At', 'Is Complete'
    ])
    
    for submission in submissions.select_related('form', 'evaluator', 'target_user'):
        writer.writerow([
            submission.id,
            submission.form.title,
            submission.form.get_evaluation_type_display(),
            submission.evaluator.get_full_name(),
            submission.target_user.get_full_name() if submission.target_user else 'N/A',
            submission.total_score,
            submission.submitted_at.strftime('%Y-%m-%d %H:%M') if submission.submitted_at else 'N/A',
            'Yes' if submission.is_complete else 'No'
        ])
    
    return response


@login_required
def create_evaluation_session(request):
    """Create a new evaluation session"""
    if request.method == 'POST':
        user = request.user
        
        # Check permissions
        if not (user.role == 'admin' or user.is_aamil or user.is_moze_coordinator):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        title = request.POST.get('title')
        description = request.POST.get('description')
        scheduled_date = request.POST.get('scheduled_date')
        participant_ids = request.POST.getlist('participants[]')
        
        if not all([title, scheduled_date]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        try:
            session = EvaluationSession.objects.create(
                title=title,
                description=description,
                evaluator=user,
                scheduled_date=scheduled_date,
                created_by=user
            )
            
            # Add participants
            if participant_ids:
                participants = User.objects.filter(id__in=participant_ids)
                session.participants.set(participants)
            
            return JsonResponse({
                'success': True,
                'message': 'Evaluation session created successfully',
                'session_id': session.id
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def my_evaluations(request):
    """View user's evaluation submissions and assignments"""
    user = request.user
    
    # User's submissions
    my_submissions = EvaluationSubmission.objects.filter(
        evaluator=user
    ).select_related('form').order_by('-submitted_at')
    
    # Evaluations where user is the target_user
    evaluations_of_me = EvaluationSubmission.objects.filter(
        target_user=user
    ).select_related('form', 'evaluator').order_by('-submitted_at')
    
    # Pending evaluations
    pending_forms = EvaluationForm.objects.filter(
        Q(target_role=user.role) | Q(target_role='all'),
        is_active=True
    ).exclude(
        id__in=my_submissions.values('form_id')
    )
    
    # Paginate submissions
    submissions_paginator = Paginator(my_submissions, 10)
    submissions_page = request.GET.get('submissions_page')
    submissions_page_obj = submissions_paginator.get_page(submissions_page)
    
    # Paginate evaluations of me
    evaluations_paginator = Paginator(evaluations_of_me, 10)
    evaluations_page = request.GET.get('evaluations_page')
    evaluations_page_obj = evaluations_paginator.get_page(evaluations_page)
    
    context = {
        'my_submissions': submissions_page_obj,
        'evaluations_of_me': evaluations_page_obj,
        'pending_forms': pending_forms,
        'total_submissions': my_submissions.count(),
        'total_evaluations_of_me': evaluations_of_me.count(),
        'pending_count': pending_forms.count(),
    }
    
    return render(request, 'evaluation/my_evaluations.html', context)
