from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.urls import reverse_lazy
from django.db.models import Q, Count, Avg
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Moze, MozeComment, MozeSettings
from .forms import MozeForm, MozeCommentForm, MozeSettingsForm
from accounts.models import User


class MozeAccessMixin(UserPassesTestMixin):
    """Mixin to check if user has access to Moze management"""
    def test_func(self):
        return (self.request.user.is_admin or 
                self.request.user.is_aamil or 
                self.request.user.is_moze_coordinator)


@login_required
def dashboard(request):
    """Moze dashboard with analytics and quick actions"""
    user = request.user
    
    # Get user's accessible mozes
    if user.is_admin:
        mozes = Moze.objects.all()
    elif user.is_aamil:
        mozes = user.managed_mozes.all()
    elif user.is_moze_coordinator:
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
        elif user.is_aamil:
            queryset = user.managed_mozes.all()
        elif user.is_moze_coordinator:
            queryset = user.coordinated_mozes.all()
        else:
            queryset = Moze.objects.none()
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(location__icontains=search) |
                Q(aamil__first_name__icontains=search) |
                Q(aamil__last_name__icontains=search)
            )
        
        # Filter by status
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        # Filter by location
        location = self.request.GET.get('location')
        if location:
            queryset = queryset.filter(location__icontains=location)
        
        return queryset.select_related('aamil', 'moze_coordinator').prefetch_related('team_members')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
        context['location_filter'] = self.request.GET.get('location', '')
        
        # Get unique locations for filter dropdown
        context['locations'] = Moze.objects.values_list('location', flat=True).distinct()
        
        return context


moze_list = MozeListView.as_view()


class MozeDetailView(LoginRequiredMixin, MozeAccessMixin, DetailView):
    """Detailed view of a single Moze with comments and team info"""
    model = Moze
    template_name = 'moze/moze_detail.html'
    context_object_name = 'moze'
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Moze.objects.all()
        elif user.is_aamil:
            return user.managed_mozes.all()
        elif user.is_moze_coordinator:
            return user.coordinated_mozes.all()
        return Moze.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        moze = self.object
        
        # Comments with threading
        comments = moze.comments.filter(
            is_active=True,
            parent__isnull=True
        ).select_related('author').prefetch_related('replies').order_by('-created_at')
        
        # Pagination for comments
        paginator = Paginator(comments, 10)
        page_number = self.request.GET.get('page')
        context['comments'] = paginator.get_page(page_number)
        
        # Comment form
        context['comment_form'] = MozeCommentForm()
        
        # Team statistics
        context['team_stats'] = {
            'total_members': moze.get_team_count(),
            'aamils': moze.team_members.filter(role='aamil').count(),
            'coordinators': moze.team_members.filter(role='moze_coordinator').count(),
            'doctors': moze.team_members.filter(role='doctor').count(),
            'students': moze.team_members.filter(role='student').count(),
        }
        
        # Recent activity
        context['recent_activity'] = moze.comments.filter(
            is_active=True
        ).select_related('author').order_by('-created_at')[:5]
        
        # Check if user can edit
        user = self.request.user
        context['can_edit'] = (
            user.is_admin or 
            (user.is_aamil and moze.aamil == user) or
            (user.is_moze_coordinator and moze.moze_coordinator == user)
        )
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle comment posting"""
        self.object = self.get_object()
        form = MozeCommentForm(request.POST)
        
        if form.is_valid():
            comment = form.save(commit=False)
            comment.moze = self.object
            comment.author = request.user
            
            # Handle reply to another comment
            parent_id = request.POST.get('parent_id')
            if parent_id:
                try:
                    parent_comment = MozeComment.objects.get(id=parent_id, moze=self.object)
                    comment.parent = parent_comment
                except MozeComment.DoesNotExist:
                    pass
            
            comment.save()
            messages.success(request, 'Comment posted successfully!')
            
            # Return JSON response for AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'comment_id': comment.id,
                    'author': comment.author.get_full_name(),
                    'content': comment.content,
                    'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M')
                })
        
        return redirect('moze:detail', pk=self.object.pk)


moze_detail = MozeDetailView.as_view()


class MozeCreateView(LoginRequiredMixin, MozeAccessMixin, CreateView):
    """Create a new Moze"""
    model = Moze
    form_class = MozeForm
    template_name = 'moze/moze_form.html'
    success_url = reverse_lazy('moze:list')
    
    def form_valid(self, form):
        # Set the creator as aamil if they are aamil role
        if self.request.user.is_aamil and not form.cleaned_data.get('aamil'):
            form.instance.aamil = self.request.user
        
        messages.success(self.request, f'Moze "{form.instance.name}" created successfully!')
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


moze_create = MozeCreateView.as_view()


class MozeEditView(LoginRequiredMixin, MozeAccessMixin, UpdateView):
    """Edit an existing Moze"""
    model = Moze
    form_class = MozeForm
    template_name = 'moze/moze_form.html'
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Moze.objects.all()
        elif user.is_aamil:
            return user.managed_mozes.all()
        elif user.is_moze_coordinator:
            return user.coordinated_mozes.all()
        return Moze.objects.none()
    
    def get_success_url(self):
        return reverse_lazy('moze:detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, f'Moze "{form.instance.name}" updated successfully!')
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


moze_edit = MozeEditView.as_view()


@login_required
def moze_delete(request, pk):
    """Delete a Moze (admin only)"""
    if not request.user.is_admin:
        messages.error(request, "You don't have permission to delete Mozes.")
        return redirect('moze:list')
    
    moze = get_object_or_404(Moze, pk=pk)
    
    if request.method == 'POST':
        moze_name = moze.name
        moze.delete()
        messages.success(request, f'Moze "{moze_name}" deleted successfully!')
        return redirect('moze:list')
    
    return render(request, 'moze/moze_confirm_delete.html', {'moze': moze})


@login_required
def comment_delete(request, pk):
    """Delete a comment (author or admin only)"""
    comment = get_object_or_404(MozeComment, pk=pk)
    
    # Check permissions
    if not (request.user.is_admin or comment.author == request.user):
        messages.error(request, "You don't have permission to delete this comment.")
        return redirect('moze:detail', pk=comment.moze.pk)
    
    if request.method == 'POST':
        moze_pk = comment.moze.pk
        comment.is_active = False  # Soft delete
        comment.save()
        messages.success(request, 'Comment deleted successfully!')
        
        # Return JSON response for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        
        return redirect('moze:detail', pk=moze_pk)
    
    return render(request, 'moze/comment_confirm_delete.html', {'comment': comment})


@login_required
def moze_analytics(request):
    """Analytics dashboard for Moze management"""
    if not (request.user.is_admin or request.user.is_moze_coordinator):
        messages.error(request, "You don't have permission to view analytics.")
        return redirect('moze:dashboard')
    
    user = request.user
    
    # Get accessible mozes
    if user.is_admin:
        mozes = Moze.objects.all()
    else:
        mozes = user.coordinated_mozes.all()
    
    # Time period filter
    period = request.GET.get('period', '30')  # Default to 30 days
    try:
        days = int(period)
    except ValueError:
        days = 30
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Analytics data
    analytics_data = {
        'total_mozes': mozes.count(),
        'active_mozes': mozes.filter(is_active=True).count(),
        'total_team_members': User.objects.filter(moze_teams__in=mozes).distinct().count(),
        'total_comments': MozeComment.objects.filter(
            moze__in=mozes,
            created_at__date__range=[start_date, end_date]
        ).count(),
    }
    
    # Moze by location
    location_stats = mozes.values('location').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Activity over time
    activity_data = []
    for i in range(days):
        date = start_date + timedelta(days=i)
        comments = MozeComment.objects.filter(
            moze__in=mozes,
            created_at__date=date
        ).count()
        activity_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'comments': comments
        })
    
    context = {
        'analytics_data': analytics_data,
        'location_stats': location_stats,
        'activity_data': activity_data,
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'moze/analytics.html', context)
