from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import AuditLog, User, UserProfile

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'its_id')
    ordering = ('username',)
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'its_id', 'phone_number', 'arabic_name', 'age', 'specialty', 'college', 'specialization')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('role', 'its_id', 'phone_number', 'arabic_name', 'age', 'specialty', 'college', 'specialization')}),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'date_of_birth', 'emergency_contact')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'location')
    list_filter = ('date_of_birth',)

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'object_type', 'object_id', 'object_repr')
    search_fields = ('user__username', 'action', 'object_type', 'object_id', 'object_repr')
    list_filter = ('action', 'object_type', 'timestamp')
    readonly_fields = [f.name for f in AuditLog._meta.fields]
    ordering = ('-timestamp',)
