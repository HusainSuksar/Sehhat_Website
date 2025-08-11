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
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods, require_POST
from django.core.exceptions import ValidationError, PermissionDenied
import json
from datetime import datetime, timedelta

from .models import (
    Petition, PetitionCategory, PetitionComment, PetitionAssignment,
    PetitionUpdate, PetitionAttachment, PetitionStatus
)
from .forms import PetitionForm, PetitionCommentForm, PetitionFilterForm
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
    approved_petitions = resolved_petitions  # Alias for template compatibility
    
    # User-specific petitions
    my_petitions = petitions.filter(created_by=user).count()
    
    # Recent petitions
    recent_petitions = petitions.select_related('created_by', 'category', 'moze').order_by('-created_at')[:10]
    recent_my_petitions = petitions.filter(created_by=user).select_related('created_by', 'category', 'moze').order_by('-created_at')[:5]
    
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
        'approved_petitions': approved_petitions,
        'my_petitions': my_petitions,
        'recent_petitions': recent_petitions,
        'recent_my_petitions': recent_my_petitions,
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
        
        # Base queryset with optimized select_related and prefetch_related
        base_queryset = Petition.objects.select_related(
            'created_by', 
            'created_by__profile',
            'category', 
            'moze',
            'moze__aamil',
            'moze__moze_coordinator'
        ).prefetch_related(
            'assignments__assigned_to',
            'assignments__assigned_by',
            'comments__user',
            'updates__created_by'
        )
        
        # Base queryset based on user role
        if user.is_admin:
            queryset = base_queryset
        elif user.is_aamil or user.is_moze_coordinator:
            queryset = base_queryset.filter(
                Q(moze__aamil=user) | Q(moze__moze_coordinator=user) | Q(created_by=user)
            )
        else:
            queryset = base_queryset.filter(created_by=user)
        
        # Apply filters efficiently
        status = self.request.GET.get('status')
        if status and status in ['pending', 'in_progress', 'resolved', 'rejected']:
            queryset = queryset.filter(status=status)
        
        priority = self.request.GET.get('priority')
        if priority and priority in ['low', 'medium', 'high', 'urgent']:
            queryset = queryset.filter(priority=priority)
        
        category = self.request.GET.get('category')
        if category:
            try:
                category_id = int(category)
                queryset = queryset.filter(category_id=category_id)
            except (ValueError, TypeError):
                pass  # Invalid category ID, ignore filter
        
        search = self.request.GET.get('search')
        if search:
            # Sanitize search input
            search = search.strip()[:100]  # Limit search length
            if search:
                queryset = queryset.filter(
                    Q(title__icontains=search) |
                    Q(description__icontains=search) |
                    Q(created_by__first_name__icontains=search) |
                    Q(created_by__last_name__icontains=search) |
                    Q(its_id__icontains=search)
                )
        
        return queryset.order_by('-created_at')
    
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
        
        # Assignable users for managers
        if context['can_manage']:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            if user.is_admin:
                # Admins can assign to anyone
                context['assignable_users'] = User.objects.filter(is_active=True).exclude(id=user.id)
            elif user.is_aamil or user.is_moze_coordinator:
                # Aamils and coordinators can assign to their team members
                assignable_users = User.objects.filter(
                    Q(role__in=['aamil', 'moze_coordinator', 'doctor']) |
                    Q(is_admin=True)
                ).filter(is_active=True).exclude(id=user.id)
                context['assignable_users'] = assignable_users
        
        return context


class PetitionCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Create a new petition with role-based access control"""
    model = Petition
    form_class = PetitionForm
    template_name = 'araz/petition_form.html'
    
    def test_func(self):
        """Check if user has permission to create petitions"""
        user = self.request.user
        # Allow admins, aamils, and students only
        # Block doctors and moze coordinators
        allowed_roles = ['badri_mahal_admin', 'aamil', 'student']
        return user.role in allowed_roles or user.is_admin
    
    def handle_no_permission(self):
        """Custom message for unauthorized users"""
        user = self.request.user
        if user.role in ['doctor', 'moze_coordinator']:
            messages.error(self.request, 
                f'Petition system is not accessible for {user.role.replace("_", " ").title()} role. '
                'Please contact your administrator if you need to submit a petition.')
        else:
            messages.error(self.request, 'You do not have permission to access the petition system.')
        return redirect('accounts:dashboard')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
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
@csrf_protect
@require_POST
def add_comment(request, pk):
    """Add a comment to a petition"""
    try:
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
            raise PermissionDenied("You do not have permission to comment on this petition")
        
        # Validate and sanitize content
        content = request.POST.get('content', '').strip()
        if not content:
            return JsonResponse({'error': 'Comment content is required'}, status=400)
        
        # Validate content length
        if len(content) > 1000:
            return JsonResponse({'error': 'Comment too long (max 1000 characters)'}, status=400)
        
        # Check for spam/malicious content
        if content.count('http') > 3:  # Basic spam detection
            return JsonResponse({'error': 'Comment contains too many links'}, status=400)
        
        with transaction.atomic():
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
            
    except PermissionDenied as e:
        return JsonResponse({'error': str(e)}, status=403)
    except ValidationError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        # Log the error for debugging
        print(f"Error in add_comment: {e}")
        return JsonResponse({'error': 'An unexpected error occurred'}, status=500)


@login_required
@csrf_protect
@require_POST
def assign_petition(request, pk):
    """Assign a petition to a user"""
    try:
        petition = get_object_or_404(Petition, pk=pk)
        
        # Check permissions
        user = request.user
        if not (user.is_admin or user.is_aamil or user.is_moze_coordinator):
            raise PermissionDenied("You do not have permission to assign petitions.")
        
        # Validate input data
        assigned_to_id = request.POST.get('assigned_to')
        notes = request.POST.get('notes', '').strip()
        
        if not assigned_to_id:
            return JsonResponse({'error': 'No user selected for assignment'}, status=400)
        
        # Validate assigned_to_id is a valid integer
        try:
            assigned_to_id = int(assigned_to_id)
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid user ID format'}, status=400)
        
        # Validate notes length
        if len(notes) > 500:
            return JsonResponse({'error': 'Notes too long (max 500 characters)'}, status=400)
        
        with transaction.atomic():
            try:
                assigned_to = User.objects.get(id=assigned_to_id)
                
                # Verify assigned user has appropriate role
                if not (assigned_to.is_admin or assigned_to.is_aamil or assigned_to.is_moze_coordinator or assigned_to.is_doctor):
                    return JsonResponse({'error': 'User cannot be assigned petitions'}, status=400)
                
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
                description = f'Assigned to {assigned_to.get_full_name()}'
                if notes:
                    description += f': {notes}'
                
                PetitionUpdate.objects.create(
                    petition=petition,
                    status='in_progress',
                    description=description,
                    created_by=user
                )
                
                return JsonResponse({
                    'success': True, 
                    'message': f'Petition assigned to {assigned_to.get_full_name()}'
                })
                
            except User.DoesNotExist:
                return JsonResponse({'error': 'Invalid user selected'}, status=400)
                
    except PermissionDenied as e:
        return JsonResponse({'error': str(e)}, status=403)
    except ValidationError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        # Log the error for debugging (in production, use proper logging)
        print(f"Error in assign_petition: {e}")
        return JsonResponse({'error': 'An unexpected error occurred'}, status=500)


@login_required
def update_petition_status(request, pk):
    """Update petition status (Start Processing, Mark Resolved, etc.)"""
    if request.method == 'POST':
        petition = get_object_or_404(Petition, pk=pk)
        
        # Check permissions
        user = request.user
        if not (user.is_admin or user.is_aamil or user.is_moze_coordinator):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        
        # Validate status
        valid_statuses = ['pending', 'in_progress', 'resolved', 'rejected']
        if new_status not in valid_statuses:
            return JsonResponse({'error': 'Invalid status'}, status=400)
        
        # Update petition status
        old_status = petition.status
        petition.status = new_status
        petition.save()
        
        # Create status update record
        status_descriptions = {
            'in_progress': 'Started processing petition',
            'resolved': 'Petition resolved successfully',
            'rejected': 'Petition rejected',
            'pending': 'Petition moved back to pending'
        }
        
        description = status_descriptions.get(new_status, f'Status changed to {new_status}')
        if notes:
            description += f': {notes}'
        
        PetitionUpdate.objects.create(
            petition=petition,
            status=new_status,
            description=description,
            created_by=user
        )
        
        return JsonResponse({
            'success': True, 
            'message': f'Petition status updated to {new_status}',
            'new_status': new_status
        })
    
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
    ).select_related('petition', 'assigned_by').order_by('-assigned_at')
    
    paginator = Paginator(assignments, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'assignments': page_obj,
        'total_assignments': assignments.count(),
    }
    
    return render(request, 'araz/my_assignments.html', context)
