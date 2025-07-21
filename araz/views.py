from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count
from django.utils import timezone
from django.core.paginator import Paginator
from django.db import transaction
import json
from datetime import datetime, timedelta

from .models import (
    Petition, PetitionCategory, PetitionComment, PetitionAssignment,
    PetitionUpdate, PetitionAttachment, PetitionStatus
)
from accounts.models import User


@login_required
def dashboard(request):
    """Araz (Petition) dashboard with statistics and recent activities"""
    user = request.user
    
    # Base queryset based on user role
    if user.is_admin:
        petitions = Petition.objects.all()
        can_manage = True
    elif user.is_aamil or user.is_moze_coordinator:
        petitions = Petition.objects.filter(
            Q(moze__aamil=user) | Q(moze__moze_coordinator=user) | Q(created_by=user)
        )
        can_manage = True
    else:
        petitions = Petition.objects.filter(created_by=user)
        can_manage = False
    
    # Statistics
    total_petitions = petitions.count()
    pending_petitions = petitions.filter(status='pending').count()
    in_progress_petitions = petitions.filter(status='in_progress').count()
    resolved_petitions = petitions.filter(status='resolved').count()
    
    # Recent petitions
    recent_petitions = petitions.select_related('created_by', 'category', 'moze').order_by('-created_at')[:10]
    
    # Monthly statistics for charts
    monthly_stats = []
    for i in range(6):
        month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
        month_petitions = petitions.filter(
            created_at__year=month_start.year,
            created_at__month=month_start.month
        ).count()
        monthly_stats.append({
            'month': month_start.strftime('%b %Y'),
            'count': month_petitions
        })
    
    # Category statistics
    category_stats = petitions.values('category__name').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Priority distribution
    priority_stats = petitions.values('priority').annotate(
        count=Count('id')
    )
    
    # My assignments (for coordinators/admins)
    my_assignments = []
    if can_manage:
        my_assignments = PetitionAssignment.objects.filter(
            assigned_to=user,
            is_active=True
        ).select_related('petition')[:5]
    
    context = {
        'total_petitions': total_petitions,
        'pending_petitions': pending_petitions,
        'in_progress_petitions': in_progress_petitions,
        'resolved_petitions': resolved_petitions,
        'recent_petitions': recent_petitions,
        'monthly_stats': monthly_stats[::-1],  # Reverse for chronological order
        'category_stats': category_stats,
        'priority_stats': priority_stats,
        'my_assignments': my_assignments,
        'can_manage': can_manage,
        'user_role': user.get_role_display(),
    }
    
    return render(request, 'araz/dashboard.html', context)


class PetitionListView(LoginRequiredMixin, ListView):
    """List all petitions with filtering and pagination"""
    model = Petition
    template_name = 'araz/petition_list.html'
    context_object_name = 'petitions'
    paginate_by = 20
    
    def get_queryset(self):
        user = self.request.user
        
        # Base queryset based on user role
        if user.is_admin:
            queryset = Petition.objects.all()
        elif user.is_aamil or user.is_moze_coordinator:
            queryset = Petition.objects.filter(
                Q(moze__aamil=user) | Q(moze__moze_coordinator=user) | Q(created_by=user)
            )
        else:
            queryset = Petition.objects.filter(created_by=user)
        
        # Apply filters
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(created_by__first_name__icontains=search) |
                Q(created_by__last_name__icontains=search)
            )
        
        return queryset.select_related('created_by', 'category', 'moze').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = PetitionCategory.objects.filter(is_active=True)
        context['status_choices'] = Petition.STATUS_CHOICES
        context['priority_choices'] = Petition.PRIORITY_CHOICES
        context['current_filters'] = {
            'status': self.request.GET.get('status', ''),
            'priority': self.request.GET.get('priority', ''),
            'category': self.request.GET.get('category', ''),
            'search': self.request.GET.get('search', ''),
        }
        return context


class PetitionDetailView(LoginRequiredMixin, DetailView):
    """Detailed view of a specific petition"""
    model = Petition
    template_name = 'araz/petition_detail.html'
    context_object_name = 'petition'
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Petition.objects.all()
        elif user.is_aamil or user.is_moze_coordinator:
            return Petition.objects.filter(
                Q(moze__aamil=user) | Q(moze__moze_coordinator=user) | Q(created_by=user)
            )
        else:
            return Petition.objects.filter(created_by=user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        petition = self.object
        
        # Comments
        context['comments'] = petition.comments.select_related('user').order_by('created_at')
        
        # Updates/Timeline
        context['updates'] = petition.updates.select_related('created_by').order_by('created_at')
        
        # Assignments
        context['assignments'] = petition.assignments.filter(is_active=True).select_related('assigned_to')
        
        # Attachments
        context['attachments'] = petition.attachments.all()
        
        # Permission checks
        user = self.request.user
        context['can_edit'] = (
            user == petition.created_by or 
            user.is_admin or 
            (user.is_aamil and petition.moze and petition.moze.aamil == user) or
            (user.is_moze_coordinator and petition.moze and petition.moze.moze_coordinator == user)
        )
        context['can_manage'] = user.is_admin or user.is_aamil or user.is_moze_coordinator
        
        return context


class PetitionCreateView(LoginRequiredMixin, CreateView):
    """Create a new petition"""
    model = Petition
    template_name = 'araz/petition_form.html'
    fields = ['title', 'description', 'category', 'priority', 'moze', 'is_anonymous']
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        
        # Create initial status update
        PetitionUpdate.objects.create(
            petition=self.object,
            status='pending',
            description='Petition submitted',
            created_by=self.request.user
        )
        
        messages.success(self.request, 'Your petition has been submitted successfully.')
        return response
    
    def get_success_url(self):
        return reverse_lazy('araz:petition_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = PetitionCategory.objects.filter(is_active=True)
        return context


class PetitionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update an existing petition"""
    model = Petition
    template_name = 'araz/petition_form.html'
    fields = ['title', 'description', 'category', 'priority', 'status']
    
    def test_func(self):
        petition = self.get_object()
        user = self.request.user
        return (
            user == petition.created_by or 
            user.is_admin or 
            (user.is_aamil and petition.moze and petition.moze.aamil == user) or
            (user.is_moze_coordinator and petition.moze and petition.moze.moze_coordinator == user)
        )
    
    def form_valid(self, form):
        # Check if status changed
        if 'status' in form.changed_data:
            PetitionUpdate.objects.create(
                petition=self.object,
                status=form.cleaned_data['status'],
                description=f'Status changed to {form.cleaned_data["status"]}',
                created_by=self.request.user
            )
        
        response = super().form_valid(form)
        messages.success(self.request, 'Petition updated successfully.')
        return response
    
    def get_success_url(self):
        return reverse_lazy('araz:petition_detail', kwargs={'pk': self.object.pk})


@login_required
def add_comment(request, pk):
    """Add a comment to a petition"""
    if request.method == 'POST':
        petition = get_object_or_404(Petition, pk=pk)
        
        # Check permissions
        user = request.user
        can_comment = (
            user == petition.created_by or 
            user.is_admin or 
            (user.is_aamil and petition.moze and petition.moze.aamil == user) or
            (user.is_moze_coordinator and petition.moze and petition.moze.moze_coordinator == user)
        )
        
        if not can_comment:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        content = request.POST.get('content', '').strip()
        if content:
            comment = PetitionComment.objects.create(
                petition=petition,
                user=user,
                content=content
            )
            
            return JsonResponse({
                'success': True,
                'comment': {
                    'id': comment.id,
                    'content': comment.content,
                    'user': comment.user.get_full_name(),
                    'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M'),
                }
            })
        
        return JsonResponse({'error': 'Comment content is required'}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def assign_petition(request, pk):
    """Assign a petition to a user"""
    if request.method == 'POST':
        petition = get_object_or_404(Petition, pk=pk)
        
        # Check permissions
        user = request.user
        if not (user.is_admin or user.is_aamil or user.is_moze_coordinator):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        assigned_to_id = request.POST.get('assigned_to')
        notes = request.POST.get('notes', '')
        
        try:
            assigned_to = User.objects.get(id=assigned_to_id)
            
            # Deactivate previous assignments
            PetitionAssignment.objects.filter(petition=petition, is_active=True).update(is_active=False)
            
            # Create new assignment
            assignment = PetitionAssignment.objects.create(
                petition=petition,
                assigned_to=assigned_to,
                assigned_by=user,
                notes=notes
            )
            
            # Update petition status
            petition.status = 'in_progress'
            petition.save()
            
            # Create status update
            PetitionUpdate.objects.create(
                petition=petition,
                status='in_progress',
                description=f'Assigned to {assigned_to.get_full_name()}',
                created_by=user
            )
            
            return JsonResponse({'success': True, 'message': 'Petition assigned successfully'})
            
        except User.DoesNotExist:
            return JsonResponse({'error': 'Invalid user selected'}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def petition_analytics(request):
    """Analytics dashboard for petitions"""
    user = request.user
    
    # Check permissions
    if not (user.is_admin or user.is_aamil or user.is_moze_coordinator):
        messages.error(request, "You don't have permission to view analytics.")
        return redirect('araz:dashboard')
    
    # Base queryset
    if user.is_admin:
        petitions = Petition.objects.all()
    else:
        petitions = Petition.objects.filter(
            Q(moze__aamil=user) | Q(moze__moze_coordinator=user)
        )
    
    # Time-based statistics
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    stats = {
        'total': petitions.count(),
        'this_week': petitions.filter(created_at__date__gte=week_ago).count(),
        'this_month': petitions.filter(created_at__date__gte=month_ago).count(),
        'pending': petitions.filter(status='pending').count(),
        'in_progress': petitions.filter(status='in_progress').count(),
        'resolved': petitions.filter(status='resolved').count(),
        'rejected': petitions.filter(status='rejected').count(),
    }
    
    # Category breakdown
    category_stats = petitions.values('category__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Monthly trend
    monthly_trend = []
    for i in range(12):
        month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
        month_petitions = petitions.filter(
            created_at__year=month_start.year,
            created_at__month=month_start.month
        ).count()
        monthly_trend.append({
            'month': month_start.strftime('%b %Y'),
            'count': month_petitions
        })
    
    # Response time analysis
    resolved_petitions = petitions.filter(status='resolved')
    avg_resolution_time = None
    if resolved_petitions.exists():
        resolution_times = []
        for petition in resolved_petitions:
            last_update = petition.updates.filter(status='resolved').first()
            if last_update:
                resolution_time = (last_update.created_at.date() - petition.created_at.date()).days
                resolution_times.append(resolution_time)
        
        if resolution_times:
            avg_resolution_time = sum(resolution_times) / len(resolution_times)
    
    context = {
        'stats': stats,
        'category_stats': category_stats,
        'monthly_trend': monthly_trend[::-1],
        'avg_resolution_time': avg_resolution_time,
        'user_role': user.get_role_display(),
    }
    
    return render(request, 'araz/analytics.html', context)


@login_required
def export_petitions(request):
    """Export petitions to CSV"""
    import csv
    from django.http import HttpResponse
    
    user = request.user
    
    # Check permissions
    if not (user.is_admin or user.is_aamil or user.is_moze_coordinator):
        messages.error(request, "You don't have permission to export data.")
        return redirect('araz:dashboard')
    
    # Base queryset
    if user.is_admin:
        petitions = Petition.objects.all()
    else:
        petitions = Petition.objects.filter(
            Q(moze__aamil=user) | Q(moze__moze_coordinator=user)
        )
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="petitions.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Title', 'Category', 'Priority', 'Status', 'Created By', 
        'Moze', 'Created At', 'Description'
    ])
    
    for petition in petitions.select_related('created_by', 'category', 'moze'):
        writer.writerow([
            petition.id,
            petition.title,
            petition.category.name if petition.category else '',
            petition.get_priority_display(),
            petition.get_status_display(),
            petition.created_by.get_full_name(),
            petition.moze.name if petition.moze else '',
            petition.created_at.strftime('%Y-%m-%d %H:%M'),
            petition.description[:100] + '...' if len(petition.description) > 100 else petition.description
        ])
    
    return response


@login_required
def bulk_update_status(request):
    """Bulk update status of multiple petitions"""
    if request.method == 'POST':
        user = request.user
        
        # Check permissions
        if not (user.is_admin or user.is_aamil or user.is_moze_coordinator):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        petition_ids = request.POST.getlist('petition_ids[]')
        new_status = request.POST.get('status')
        
        if not petition_ids or not new_status:
            return JsonResponse({'error': 'Missing required parameters'}, status=400)
        
        # Base queryset based on permissions
        if user.is_admin:
            petitions = Petition.objects.filter(id__in=petition_ids)
        else:
            petitions = Petition.objects.filter(
                Q(id__in=petition_ids) &
                (Q(moze__aamil=user) | Q(moze__moze_coordinator=user))
            )
        
        updated_count = 0
        with transaction.atomic():
            for petition in petitions:
                petition.status = new_status
                petition.save()
                
                # Create status update
                PetitionUpdate.objects.create(
                    petition=petition,
                    status=new_status,
                    description=f'Bulk status update to {new_status}',
                    created_by=user
                )
                updated_count += 1
        
        return JsonResponse({
            'success': True, 
            'message': f'{updated_count} petitions updated successfully'
        })
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def my_assignments(request):
    """View assignments for the current user"""
    user = request.user
    
    assignments = PetitionAssignment.objects.filter(
        assigned_to=user,
        is_active=True
    ).select_related('petition', 'assigned_by').order_by('-created_at')
    
    paginator = Paginator(assignments, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'assignments': page_obj,
        'total_assignments': assignments.count(),
    }
    
    return render(request, 'araz/my_assignments.html', context)
