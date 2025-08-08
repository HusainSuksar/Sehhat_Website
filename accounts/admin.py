from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.shortcuts import redirect
from django.urls import reverse
from .models import AuditLog, User, UserProfile

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined', 'get_full_name_display')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'its_id', 'arabic_full_name')
    ordering = ('username',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {
            'fields': ('role', 'its_id', 'phone_number', 'arabic_full_name', 'age', 'specialty', 'college', 'specialization', 'profile_photo', 'verified_certificate')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {
            'fields': ('role', 'its_id', 'phone_number', 'arabic_full_name', 'age', 'specialty', 'college', 'specialization')
        }),
    )
    
    def get_full_name_display(self, obj):
        """Display full name with role"""
        return format_html('<strong>{}</strong> <br><small>({})</small>', 
                         obj.get_full_name(), obj.get_role_display())
    get_full_name_display.short_description = 'Full Name (Role)'
    
    def get_queryset(self, request):
        """Ensure admin can see all users"""
        return super().get_queryset(request)
    
    def has_module_permission(self, request):
        """Admin has access to all modules"""
        return request.user.is_superuser or request.user.is_staff
    
    def has_view_permission(self, request, obj=None):
        """Admin can view all users"""
        return request.user.is_superuser or request.user.is_staff
    
    def has_add_permission(self, request):
        """Admin can add users"""
        return request.user.is_superuser or request.user.is_staff
    
    def has_change_permission(self, request, obj=None):
        """Admin can change all users"""
        return request.user.is_superuser or request.user.is_staff
    
    def has_delete_permission(self, request, obj=None):
        """Admin can delete users"""
        return request.user.is_superuser or request.user.is_staff
    
    def changelist_view(self, request, extra_context=None):
        """Redirect to custom user directory view"""
        return redirect('accounts:user_directory')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'date_of_birth', 'emergency_contact', 'get_user_role')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'location')
    list_filter = ('date_of_birth', 'user__role')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_user_role(self, obj):
        return obj.user.get_role_display()
    get_user_role.short_description = 'User Role'
    
    def has_module_permission(self, request):
        """Admin has access to all modules"""
        return request.user.is_superuser or request.user.is_staff

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'object_type', 'object_id', 'object_repr')
    search_fields = ('user__username', 'action', 'object_type', 'object_id', 'object_repr')
    list_filter = ('action', 'object_type', 'timestamp')
    readonly_fields = [f.name for f in AuditLog._meta.fields]
    ordering = ('-timestamp',)
    
    def has_module_permission(self, request):
        """Admin has access to all modules"""
        return request.user.is_superuser or request.user.is_staff
