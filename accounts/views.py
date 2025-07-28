from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import (
    TemplateView, ListView, DetailView, UpdateView, CreateView
)
from django.urls import reverse_lazy
from django.http import JsonResponse
import json

from .models import User, UserProfile
from .forms import (
    CustomLoginForm, UserRegistrationForm, UserProfileForm, 
    UserEditForm, ITSVerificationForm
)

from students.models import Student, Course
from moze.models import Moze
from mahalshifa.models import Hospital
from doctordirectory.models import Doctor as DirDoctor
from surveys.models import Survey
from araz.models import Petition
from photos.models import PhotoAlbum


class CustomLoginView(LoginView):
    """Custom login view with role-based redirection"""
    form_class = CustomLoginForm
    template_name = 'accounts/login.html'
    
    def get_success_url(self):
        user = self.request.user
        if user.is_admin:
            return reverse_lazy('accounts:dashboard')
        elif user.is_aamil:
            return reverse_lazy('moze:dashboard')
        elif user.is_moze_coordinator:
            return reverse_lazy('moze:dashboard')
        elif user.is_doctor:
            return reverse_lazy('doctordirectory:dashboard')
        elif user.is_student:
            return reverse_lazy('students:dashboard')
        else:
            return reverse_lazy('accounts:profile')


class RegisterView(CreateView):
    """User registration view"""
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request, 
            'Registration successful! Please log in with your credentials.'
        )
        return response


class ProfileView(LoginRequiredMixin, TemplateView):
    """User profile view"""
    template_name = 'accounts/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get or create user profile
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        context.update({
            'user': user,
            'profile': profile,
            'role_display': user.get_role_display(),
        })
        
        # Add role-specific context
        if user.is_student:
            try:
                student_profile = user.student_profile
                context['student_profile'] = student_profile
            except:
                pass
        elif user.is_doctor:
            try:
                doctor_profile = user.doctor_profile
                context['doctor_profile'] = doctor_profile
            except:
                pass
        
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    """Edit user profile view"""
    model = User
    form_class = UserProfileForm
    template_name = 'accounts/edit_profile.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)


class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """List all users (admin only)"""
    model = User
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.is_admin
    
    def get_queryset(self):
        queryset = User.objects.select_related('profile')
        
        # Filter by role if specified
        role = self.request.GET.get('role')
        if role:
            queryset = queryset.filter(role=role)
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            from django.db import models as django_models
            queryset = queryset.filter(
                django_models.Q(username__icontains=search) |
                django_models.Q(first_name__icontains=search) |
                django_models.Q(last_name__icontains=search) |
                django_models.Q(email__icontains=search) |
                django_models.Q(its_id__icontains=search)
            )
        
        return queryset.order_by('username')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['role_choices'] = User.ROLE_CHOICES
        context['current_role'] = self.request.GET.get('role', '')
        context['search_query'] = self.request.GET.get('search', '')
        return context


class UserDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """User detail view (admin only)"""
    model = User
    template_name = 'accounts/user_detail.html'
    context_object_name = 'user_obj'
    
    def test_func(self):
        return self.request.user.is_admin
    
    def get_queryset(self):
        return User.objects.select_related('profile')


class UserEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Edit user view (admin only)"""
    model = User
    form_class = UserEditForm
    template_name = 'accounts/user_edit.html'
    
    def test_func(self):
        return self.request.user.is_admin
    
    def get_success_url(self):
        return reverse_lazy('accounts:user_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'User updated successfully!')
        return super().form_valid(form)


class VerifyITSView(LoginRequiredMixin, TemplateView):
    """Verify ITS ID via mock API"""
    template_name = 'accounts/verify_its.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ITSVerificationForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = ITSVerificationForm(request.POST)
        
        if form.is_valid():
            its_id = form.cleaned_data['its_id']
            
            # Mock ITS API call
            mock_data = self.mock_its_api_call(its_id)
            
            if mock_data:
                return JsonResponse({
                    'success': True,
                    'data': mock_data
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'ITS ID not found in the system'
                })
        
        return JsonResponse({
            'success': False,
            'error': 'Invalid ITS ID format'
        })
    
    def mock_its_api_call(self, its_id):
        """Mock ITS API call - replace with real API integration"""
        # This is a mock implementation
        mock_database = {
            '12345678': {
                'name': 'Ahmed Ali',
                'arabic_name': 'أحمد علي',
                'age': 25,
                'photo_url': '/media/profile_photos/default.jpg',
                'email': 'ahmed.ali@example.com',
                'phone': '+1234567890'
            },
            '87654321': {
                'name': 'Fatima Hassan',
                'arabic_name': 'فاطمة حسن',
                'age': 23,
                'photo_url': '/media/profile_photos/default.jpg',
                'email': 'fatima.hassan@example.com',
                'phone': '+0987654321'
            }
        }
        
        return mock_database.get(its_id)


@login_required
def dashboard_view(request):
    """Simple dashboard view"""
    context = {
        'user': request.user,
        'role_display': request.user.get_role_display(),
        'total_users': User.objects.count(),
        'total_students': Student.objects.count(),
        'total_doctors': DirDoctor.objects.count(),
        'total_moze': Moze.objects.count(),
        'total_hospitals': Hospital.objects.count(),
        'total_surveys': Survey.objects.count(),
        'total_petitions': Petition.objects.count(),
        'total_albums': PhotoAlbum.objects.count(),
    }
    return render(request, 'accounts/dashboard.html', context)
