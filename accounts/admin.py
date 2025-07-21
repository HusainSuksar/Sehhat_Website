from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, UserProfile


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('role', 'its_id', 'email')


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = UserChangeForm.Meta.fields


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'its_id', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'its_id', 'arabic_name')
    ordering = ('username',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role & ITS Information', {
            'fields': ('role', 'its_id', 'arabic_name', 'age', 'phone_number')
        }),
        ('Professional Information', {
            'fields': ('specialty', 'verified_certificate', 'college', 'specialization')
        }),
        ('Media', {
            'fields': ('profile_photo',)
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role & ITS Information', {
            'fields': ('role', 'its_id', 'email')
        }),
    )
    
    inlines = [UserProfileInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('profile')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'date_of_birth', 'emergency_contact_name', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'location')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Personal Details', {
            'fields': ('bio', 'location', 'date_of_birth')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact', 'emergency_contact_name')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
