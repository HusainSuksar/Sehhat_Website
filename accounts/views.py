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
from django.core.paginator import Paginator
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django import forms
from django.db.models import Q
from guardian.shortcuts import assign_perm, remove_perm, get_perms, get_objects_for_user
import json

from .models import User, UserProfile, AuditLog
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
            except AttributeError:
                # User doesn't have a student profile
                pass
            except Exception as e:
                print(f"Error loading student profile for user {user.username}: {e}")
                pass
        elif user.is_doctor:
            try:
                doctor_profile = user.doctor_profile
                context['doctor_profile'] = doctor_profile
            except AttributeError:
                # User doesn't have a doctor profile
                pass
            except Exception as e:
                print(f"Error loading doctor profile for user {user.username}: {e}")
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


class AuditLogListView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'accounts/audit_log_list.html'
    paginate_by = 30

    def test_func(self):
        return self.request.user.is_admin

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        logs = AuditLog.objects.select_related('user').all()
        paginator = Paginator(logs, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        return context


class UserPermissionForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    user_permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['role', 'groups', 'user_permissions']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['groups'].initial = self.instance.groups.all()
            self.fields['user_permissions'].initial = self.instance.user_permissions.all()
            self.fields['role'].initial = self.instance.role

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
            user.groups.set(self.cleaned_data['groups'])
            user.user_permissions.set(self.cleaned_data['user_permissions'])
        return user

class PermissionManagementView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'accounts/permission_management.html'

    def test_func(self):
        return self.request.user.is_admin

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        users = User.objects.all().select_related('profile').prefetch_related('groups', 'user_permissions')
        context['users'] = users
        context['groups'] = Group.objects.all()
        context['permissions'] = Permission.objects.all()
        context['form'] = None
        user_id = self.request.GET.get('edit_user')
        if user_id:
            user = User.objects.get(pk=user_id)
            context['form'] = UserPermissionForm(instance=user)
            context['edit_user'] = user
        return context

    def post(self, request, *args, **kwargs):
        user_id = request.POST.get('user_id')
        user = User.objects.get(pk=user_id)
        form = UserPermissionForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Permissions updated for {user.get_full_name()}.")
            # Audit log for permission change
            AuditLog.objects.create(
                user=request.user,
                action='permission_change',
                object_type='User',
                object_id=str(user.pk),
                object_repr=str(user),
                extra_data={
                    'role': form.cleaned_data['role'],
                    'groups': [g.name for g in form.cleaned_data['groups']],
                    'permissions': [p.codename for p in form.cleaned_data['user_permissions']]
                }
            )
            return redirect('accounts:permission_management')
        else:
            messages.error(request, "Failed to update permissions.")
            # Re-render the page with the form and edit_user context
            context = self.get_context_data()
            context['form'] = form
            context['edit_user'] = user
            return self.render_to_response(context)


class ObjectPermissionForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(), 
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_user'})
    )
    model = forms.ChoiceField(
        choices=[('doctor', 'Doctor'), ('student', 'Student'), ('hospital', 'Hospital')], 
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_model'})
    )
    object_id = forms.ChoiceField(
        choices=[], 
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_object_id'})
    )
    permission = forms.ChoiceField(
        choices=[], 
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_permission'})
    )
    action = forms.ChoiceField(
        choices=[('assign', 'Assign'), ('remove', 'Remove')], 
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize with empty choices, will be populated via AJAX
        self.fields['object_id'].choices = []
        self.fields['permission'].choices = []

    def get_available_objects(self, model_name):
        """Get available objects for the selected model"""
        if model_name == 'doctor':
            from doctordirectory.models import Doctor
            objects = Doctor.objects.all()
            return [(obj.pk, f"{obj.name} (ID: {obj.pk})") for obj in objects]
        elif model_name == 'student':
            from students.models import Student
            objects = Student.objects.all()
            return [(obj.pk, f"{obj.user.get_full_name()} (ID: {obj.pk})") for obj in objects]
        elif model_name == 'hospital':
            from mahalshifa.models import Hospital
            objects = Hospital.objects.all()
            return [(obj.pk, f"{obj.name} (ID: {obj.pk})") for obj in objects]
        return []

    def get_available_permissions(self, model_name):
        """Get available permissions for the selected model"""
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType
        
        if model_name == 'doctor':
            content_type = ContentType.objects.get(app_label='doctordirectory', model='doctor')
        elif model_name == 'student':
            content_type = ContentType.objects.get(app_label='students', model='student')
        elif model_name == 'hospital':
            content_type = ContentType.objects.get(app_label='mahalshifa', model='hospital')
        else:
            return []
        
        permissions = Permission.objects.filter(content_type=content_type)
        return [(perm.codename, f"{perm.codename} - {perm.name}") for perm in permissions]

class ObjectPermissionManagementView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'accounts/object_permission_management.html'

    def test_func(self):
        return self.request.user.is_admin

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ObjectPermissionForm()
        context['result'] = None
        return context

    def get(self, request, *args, **kwargs):
        # AJAX: Get models/objects for a user
        if request.GET.get('action') == 'get_user_objects':
            user_id = request.GET.get('user_id')
            result = {}
            if user_id:
                # For demo, show all models; in real app, could filter by user role
                models = [('doctor', 'Doctor'), ('student', 'Student'), ('hospital', 'Hospital')]
                result['models'] = models
                # For each model, get objects
                form = ObjectPermissionForm()
                objects_by_model = {}
                for model_key, model_label in models:
                    objects = form.get_available_objects(model_key)
                    objects_by_model[model_key] = objects
                result['objects_by_model'] = objects_by_model
            return JsonResponse(result)
        # AJAX: Get permissions for a model
        elif request.GET.get('action') == 'get_permissions':
            model_name = request.GET.get('model')
            form = ObjectPermissionForm()
            permissions = form.get_available_permissions(model_name)
            return JsonResponse({'permissions': permissions})
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = ObjectPermissionForm(request.POST)
        result = None
        if form.is_valid():
            try:
                user = form.cleaned_data['user']
                model = form.cleaned_data['model']
                object_id = form.cleaned_data['object_id']
                permission = form.cleaned_data['permission']
                action = form.cleaned_data['action']
                # Get the object based on model type
                obj = None
                if model == 'doctor':
                    obj = DirDoctor.objects.filter(pk=object_id).first()
                elif model == 'student':
                    obj = Student.objects.filter(pk=object_id).first()
                elif model == 'hospital':
                    obj = Hospital.objects.filter(pk=object_id).first()
                if obj:
                    if action == 'assign':
                        assign_perm(permission, user, obj)
                        result = f"Assigned '{permission}' to {user} for {model} {object_id}."
                    else:
                        remove_perm(permission, user, obj)
                        result = f"Removed '{permission}' from {user} for {model} {object_id}."
                    # Audit log
                    AuditLog.objects.create(
                        user=request.user,
                        action='permission_change',
                        object_type=model.title(),
                        object_id=str(object_id),
                        object_repr=str(obj),
                        extra_data={
                            'target_user': str(user),
                            'permission': permission,
                            'action': action
                        }
                    )
                else:
                    result = f"Object not found for {model} with ID {object_id}."
            except Exception as e:
                result = f"Error: {str(e)}"
        else:
            result = "Invalid form submission."
        context = self.get_context_data()
        context['form'] = form
        context['result'] = result
        return self.render_to_response(context)


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
        'show_audit_log_link': request.user.is_admin,
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required
def user_directory(request):
    """
    Modern user directory view for managing doctors, paramedics, and Umoor Sehhat KGs
    """
    # Get all users with their roles
    users = User.objects.filter(is_active=True).prefetch_related('groups')
    
    # Filter by role if specified
    role_filter = request.GET.get('role')
    if role_filter:
        users = users.filter(role=role_filter)
    
    # Filter by moze if specified (for aamil and moze_coordinator users)
    moze_filter = request.GET.get('moze')
    if moze_filter:
        # Filter users who are aamil or moze_coordinator and associated with this moze
        users = users.filter(
            Q(role='aamil', managed_mozes__id=moze_filter) |
            Q(role='moze_coordinator', coordinated_mozes__id=moze_filter)
        ).distinct()
    
    # Filter by ITS ID if specified
    its_id_filter = request.GET.get('its_id')
    if its_id_filter:
        users = users.filter(its_id__icontains=its_id_filter)
    
    # Get all mozes for filter dropdown
    mozes = Moze.objects.filter(is_active=True)
    
    # Get all jamiat for filter dropdown (if you have a Jamiat model)
    # jamiat_list = Jamiat.objects.filter(is_active=True)
    jamiat_list = []  # Placeholder - replace with actual Jamiat model
    
    # Prepare user data for the template
    user_data = []
    for user in users:
        # Get moze information if user has any moze relationships
        moze_name = ''
        try:
            # Check if user is aamil and has managed mozes
            if user.role == 'aamil' and hasattr(user, 'managed_mozes'):
                moze = user.managed_mozes.first()
                if moze:
                    moze_name = moze.name
            # Check if user is moze_coordinator and has coordinated mozes
            elif user.role == 'moze_coordinator' and hasattr(user, 'coordinated_mozes'):
                moze = user.coordinated_mozes.first()
                if moze:
                    moze_name = moze.name
        except:
            moze_name = ''
        
        user_data.append({
            'id': user.id,
            'name': user.get_full_name(),
            'email': user.email,
            'phone': user.phone_number or '',
            'role': user.get_role_display(),
            'role_key': user.role,
            'moze': moze_name,
            'its_id': user.its_id or '',
            'is_active': user.is_active,
            'date_joined': user.date_joined,
        })
    
    # Get statistics
    total_users = users.count()
    role_stats = {}
    for role_key, role_name in User.ROLE_CHOICES:
        role_stats[role_key] = users.filter(role=role_key).count()
    
    context = {
        'users': user_data,
        'mozes': mozes,
        'jamiat_list': jamiat_list,
        'total_users': total_users,
        'role_choices': User.ROLE_CHOICES,
        'role_stats': role_stats,
        'can_add_user': request.user.is_admin or request.user.role in ['aamil', 'moze_coordinator'],
        'can_edit_user': request.user.is_admin or request.user.role in ['aamil', 'moze_coordinator'],
        'can_delete_user': request.user.is_admin,
        'current_filters': {
            'role': role_filter,
            'moze': moze_filter,
            'its_id': its_id_filter,
        }
    }
    
    return render(request, 'accounts/user_directory.html', context)
