from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('camera', 'event_type', 'severity', 'occurred_at', 'is_processed')
    list_filter = ('event_type', 'severity', 'is_processed', 'occurred_at')
    search_fields = ('camera__name',)
    readonly_fields = ('occurred_at', 'created_at', 'processed_at')
