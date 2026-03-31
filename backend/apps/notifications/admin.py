from django.contrib import admin
from .models import NotificationChannel, NotificationDelivery


@admin.register(NotificationChannel)
class NotificationChannelAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'channel_type', 'is_active')
    list_filter = ('channel_type', 'is_active')
    search_fields = ('name', 'organization__name')


@admin.register(NotificationDelivery)
class NotificationDeliveryAdmin(admin.ModelAdmin):
    list_display = ('channel', 'recipient', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('recipient',)
    readonly_fields = ('created_at', 'sent_at')
