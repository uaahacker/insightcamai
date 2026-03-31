from django.contrib import admin
from .models import Alert


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('title', 'camera', 'status', 'severity', 'triggered_at')
    list_filter = ('status', 'severity', 'triggered_at')
    search_fields = ('title', 'camera__name')
    readonly_fields = ('triggered_at', 'acknowledged_at', 'resolved_at')
