from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'resource_type', 'created_at')
    list_filter = ('action', 'created_at', 'organization')
    search_fields = ('user__email', 'resource_id')
    readonly_fields = ('created_at',)
