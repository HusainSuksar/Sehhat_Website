from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'object_type', 'object_id', 'object_repr')
    search_fields = ('user__username', 'action', 'object_type', 'object_id', 'object_repr')
    list_filter = ('action', 'object_type', 'timestamp')
    readonly_fields = [f.name for f in AuditLog._meta.fields]
    ordering = ('-timestamp',)
