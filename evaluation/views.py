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
    if user.is_admin:
        forms = EvaluationForm.objects.all()
        submissions = EvaluationSubmission.objects.all()
        can_manage = True
    elif user.is_aamil or user.is_moze_coordinator:
        # Can see forms for their moze and forms they created
        forms = EvaluationForm.objects.filter(
            Q(moze__aamil=user) | Q(moze__moze_coordinator=user) | Q(created_by=user)
        )
        submissions = EvaluationSubmission.objects.filter(
            Q(form__moze__aamil=user) | Q(form__moze__moze_coordinator=user) | Q(evaluator=user)
        )
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
    recent_forms = forms.select_related('created_by', 'moze').order_by('-created_at')[:10]
    
    # Recent submissions
    recent_submissions = submissions.select_related('form', 'evaluator', 'evaluatee').order_by('-submitted_at')[:10]
    
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
    
    # Average ratings by category
    avg_ratings = []
    if submissions.exists():
        criteria_ratings = CriteriaRating.objects.filter(
            submission__in=submissions
        ).values('criteria__category').annotate(avg_rating=Avg('rating'))
        avg_ratings = list(criteria_ratings)
    
    # Evaluation sessions
    recent_sessions = EvaluationSession.objects.filter(
        Q(evaluator=user) | Q(participants=user)
    ).distinct().order_by('-scheduled_date')[:5]
    
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
        if user.is_admin:
            queryset = EvaluationForm.objects.all()
        elif user.is_aamil or user.is_moze_coordinator:
            queryset = EvaluationForm.objects.filter(
                Q(moze__aamil=user) | Q(moze__moze_coordinator=user) | Q(created_by=user)
            )
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
        
        return queryset.select_related('created_by', 'moze').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['evaluation_types'] = EvaluationForm.EVALUATION_TYPES
        context['current_filters'] = {
            'status': self.request.GET.get('status', ''),
            'type': self.request.GET.get('type', ''),
            'search': self.request.GET.get('search', ''),
        }
        return context


class EvaluationFormDetailView(LoginRequiredMixin, DetailView):
    """Detailed view of an evaluation form"""
    model = EvaluationForm
    template_name = 'evaluation/form_detail.html'
    context_object_name = 'form'
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return EvaluationForm.objects.all()
        elif user.is_aamil or user.is_moze_coordinator:
            return EvaluationForm.objects.filter(
                Q(moze__aamil=user) | Q(moze__moze_coordinator=user) | Q(created_by=user)
            )
        else:
            return EvaluationForm.objects.filter(
                Q(target_role=user.role) | Q(target_role='all'),
                is_active=True
            )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = self.object
        user = self.request.user
        
        # Criteria grouped by category
        criteria_by_category = {}
        for criteria in form.criteria.filter(is_active=True):
            category = criteria.category
            if category not in criteria_by_category:
                criteria_by_category[category] = []
            criteria_by_category[category].append(criteria)
        
        context['criteria_by_category'] = criteria_by_category
        
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
            (user.is_aamil and form.moze and form.moze.aamil == user) or
            (user.is_moze_coordinator and form.moze and form.moze.moze_coordinator == user)
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
    fields = ['title', 'description', 'evaluation_type', 'target_role', 'moze', 'due_date', 'is_active']
    
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


@login_required
def evaluate_form(request, pk):
    """Submit an evaluation for a specific form"""
    form = get_object_or_404(EvaluationForm, pk=pk)
    user = request.user
    
    # Check permissions
    if not (form.target_role == user.role or form.target_role == 'all'):
        messages.error(request, "You don't have permission to evaluate this form.")
        return redirect('evaluation:form_detail', pk=pk)
    
    # Check if already submitted
    existing_submission = EvaluationSubmission.objects.filter(
        form=form,
        evaluator=user
    ).first()
    
    if existing_submission:
        messages.info(request, "You have already submitted an evaluation for this form.")
        return redirect('evaluation:form_detail', pk=pk)
    
    if request.method == 'POST':
        # Get evaluatee if specified
        evaluatee_id = request.POST.get('evaluatee')
        evaluatee = None
        if evaluatee_id:
            try:
                evaluatee = User.objects.get(id=evaluatee_id)
            except User.DoesNotExist:
                pass
        
        # Create submission
        submission = EvaluationSubmission.objects.create(
            form=form,
            evaluator=user,
            evaluatee=evaluatee,
            is_complete=True,
            submitted_at=timezone.now()
        )
        
        # Process criteria ratings
        total_score = 0
        criteria_count = 0
        
        for criteria in form.criteria.filter(is_active=True):
            rating_value = request.POST.get(f'criteria_{criteria.id}')
            comment = request.POST.get(f'comment_{criteria.id}', '')
            
            if rating_value:
                rating = CriteriaRating.objects.create(
                    submission=submission,
                    criteria=criteria,
                    rating=int(rating_value),
                    comment=comment
                )
                total_score += int(rating_value)
                criteria_count += 1
        
        # Calculate and save total score
        if criteria_count > 0:
            submission.total_score = Decimal(total_score) / Decimal(criteria_count)
            submission.save()
        
        messages.success(request, 'Your evaluation has been submitted successfully.')
        return redirect('evaluation:form_detail', pk=pk)
    
    # GET request - show evaluation form
    criteria_by_category = {}
    for criteria in form.criteria.filter(is_active=True):
        category = criteria.category
        if category not in criteria_by_category:
            criteria_by_category[category] = []
        criteria_by_category[category].append(criteria)
    
    # Get potential evaluatees for peer evaluation
    evaluatees = []
    if form.evaluation_type in ['peer', 'upward', 'downward']:
        if user.is_admin:
            evaluatees = User.objects.exclude(id=user.id)
        elif user.is_aamil or user.is_moze_coordinator:
            evaluatees = User.objects.filter(
                Q(role='moze_coordinator') | Q(role='doctor') | Q(role='student')
            ).exclude(id=user.id)
        else:
            evaluatees = User.objects.filter(role=user.role).exclude(id=user.id)
    
    context = {
        'form': form,
        'criteria_by_category': criteria_by_category,
        'evaluatees': evaluatees,
        'rating_choices': range(1, 6),  # 1-5 rating scale
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
        user == submission.evaluatee or
        user.is_admin or
        (user.is_aamil and submission.form.moze and submission.form.moze.aamil == user) or
        (user.is_moze_coordinator and submission.form.moze and submission.form.moze.moze_coordinator == user)
    )
    
    if not can_view:
        messages.error(request, "You don't have permission to view this submission.")
        return redirect('evaluation:dashboard')
    
    # Get ratings grouped by category
    ratings_by_category = {}
    for rating in submission.ratings.select_related('criteria'):
        category = rating.criteria.category
        if category not in ratings_by_category:
            ratings_by_category[category] = []
        ratings_by_category[category].append(rating)
    
    context = {
        'submission': submission,
        'ratings_by_category': ratings_by_category,
    }
    
    return render(request, 'evaluation/submission_detail.html', context)


@login_required
def evaluation_analytics(request):
    """Analytics dashboard for evaluations"""
    user = request.user
    
    # Check permissions
    if not (user.is_admin or user.is_aamil or user.is_moze_coordinator):
        messages.error(request, "You don't have permission to view analytics.")
        return redirect('evaluation:dashboard')
    
    # Base queryset
    if user.is_admin:
        submissions = EvaluationSubmission.objects.all()
    else:
        submissions = EvaluationSubmission.objects.filter(
            Q(form__moze__aamil=user) | Q(form__moze__moze_coordinator=user)
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
    
    # Top performing areas (by criteria category)
    category_performance = CriteriaRating.objects.filter(
        submission__in=submissions
    ).values('criteria__category').annotate(
        avg_rating=Avg('rating'),
        count=Count('id')
    ).order_by('-avg_rating')
    
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
    if not (user.is_admin or user.is_aamil or user.is_moze_coordinator):
        messages.error(request, "You don't have permission to export data.")
        return redirect('evaluation:dashboard')
    
    # Base queryset
    if user.is_admin:
        submissions = EvaluationSubmission.objects.all()
    else:
        submissions = EvaluationSubmission.objects.filter(
            Q(form__moze__aamil=user) | Q(form__moze__moze_coordinator=user)
        )
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="evaluations.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Submission ID', 'Form Title', 'Evaluation Type', 'Evaluator', 
        'Evaluatee', 'Total Score', 'Submitted At', 'Is Complete'
    ])
    
    for submission in submissions.select_related('form', 'evaluator', 'evaluatee'):
        writer.writerow([
            submission.id,
            submission.form.title,
            submission.form.get_evaluation_type_display(),
            submission.evaluator.get_full_name(),
            submission.evaluatee.get_full_name() if submission.evaluatee else 'N/A',
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
        if not (user.is_admin or user.is_aamil or user.is_moze_coordinator):
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
    
    # Evaluations where user is the evaluatee
    evaluations_of_me = EvaluationSubmission.objects.filter(
        evaluatee=user
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
