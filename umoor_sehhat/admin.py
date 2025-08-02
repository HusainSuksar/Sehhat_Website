from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import redirect
from django.http import HttpResponseRedirect


class UmoorSehhatAdminSite(AdminSite):
    """Custom admin site for Umoor Sehhat"""
    site_header = "Umoor Sehhat Administration"
    site_title = "Umoor Sehhat Admin"
    index_title = "Welcome to Umoor Sehhat Administration"
    
    def has_permission(self, request):
        """Ensure admin has access to everything"""
        return request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff)
    
    def index(self, request, extra_context=None):
        """Custom index with dashboard links"""
        extra_context = extra_context or {}
        extra_context.update({
            'dashboard_links': [
                {
                    'name': 'User Management',
                    'url': reverse('admin:accounts_user_changelist'),
                    'count': 'Manage all users'
                },
                {
                    'name': 'Moze Management',
                    'url': reverse('admin:moze_moze_changelist'),
                    'count': 'Manage medical centers'
                },
                {
                    'name': 'Hospital Management',
                    'url': reverse('admin:mahalshifa_hospital_changelist'),
                    'count': 'Manage hospitals and doctors'
                },
                {
                    'name': 'Patient Management',
                    'url': reverse('admin:mahalshifa_patient_changelist'),
                    'count': 'Manage patient records'
                },
                {
                    'name': 'Survey Management',
                    'url': reverse('admin:surveys_survey_changelist'),
                    'count': 'Manage surveys and analytics'
                },
                {
                    'name': 'Evaluation Management',
                    'url': reverse('admin:evaluation_evaluationform_changelist'),
                    'count': 'Manage evaluations'
                },
                {
                    'name': 'Petition Management',
                    'url': reverse('admin:araz_petition_changelist'),
                    'count': 'Manage petitions'
                },
            ]
        })
        return super().index(request, extra_context)


# Create custom admin site instance
admin_site = UmoorSehhatAdminSite(name='umoor_sehhat_admin')


# Admin actions for bulk operations
@admin.action(description="Mark selected items as active")
def make_active(modeladmin, request, queryset):
    queryset.update(is_active=True)
make_active.short_description = "Mark selected items as active"


@admin.action(description="Mark selected items as inactive")
def make_inactive(modeladmin, request, queryset):
    queryset.update(is_active=False)
make_inactive.short_description = "Mark selected items as inactive"


@admin.action(description="Export selected items")
def export_selected(modeladmin, request, queryset):
    """Export selected items to CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{modeladmin.model._meta.verbose_name_plural}.csv"'
    
    writer = csv.writer(response)
    
    # Write headers
    field_names = [field.name for field in modeladmin.model._meta.fields]
    writer.writerow(field_names)
    
    # Write data
    for obj in queryset:
        row = []
        for field_name in field_names:
            value = getattr(obj, field_name)
            row.append(str(value) if value is not None else '')
        writer.writerow(row)
    
    return response
export_selected.short_description = "Export selected items to CSV"


# Custom admin mixin for enhanced functionality
class EnhancedAdminMixin:
    """Mixin to add enhanced functionality to admin models"""
    
    def get_queryset(self, request):
        """Ensure admin can see all records"""
        return super().get_queryset(request)
    
    def has_module_permission(self, request):
        """Admin has access to all modules"""
        return request.user.is_superuser or request.user.is_staff
    
    def has_view_permission(self, request, obj=None):
        """Admin can view all records"""
        return request.user.is_superuser or request.user.is_staff
    
    def has_add_permission(self, request):
        """Admin can add records"""
        return request.user.is_superuser or request.user.is_staff
    
    def has_change_permission(self, request, obj=None):
        """Admin can change all records"""
        return request.user.is_superuser or request.user.is_staff
    
    def has_delete_permission(self, request, obj=None):
        """Admin can delete records"""
        return request.user.is_superuser or request.user.is_staff
    
    def get_actions(self, request):
        """Add custom actions"""
        actions = super().get_actions(request)
        if 'is_active' in [f.name for f in self.model._meta.fields]:
            actions['make_active'] = make_active
            actions['make_inactive'] = make_inactive
        actions['export_selected'] = export_selected
        return actions


# Admin site customization
admin.site.site_header = "Umoor Sehhat Administration"
admin.site.site_title = "Umoor Sehhat Admin"
admin.site.index_title = "Welcome to Umoor Sehhat Administration"

# Add custom CSS and JS for better admin interface
class Media:
    css = {
        'all': ('admin/css/custom_admin.css',)
    }
    js = ('admin/js/custom_admin.js',)