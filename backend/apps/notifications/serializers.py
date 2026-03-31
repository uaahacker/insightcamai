from rest_framework import serializers
from .models import NotificationChannel, NotificationDelivery
from core.serializers import BaseSerializer


class NotificationChannelSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = NotificationChannel
        fields = ('id', 'name', 'channel_type', 'recipients', 'webhook_url',
                  'phone_numbers', 'is_active', 'created_at', 'updated_at')
        extra_kwargs = {
            'webhook_secret': {'write_only': True},
        }


class NotificationDeliverySerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = NotificationDelivery
        fields = ('id', 'channel', 'recipient', 'subject', 'body', 'status',
                  'retry_count', 'last_error', 'created_at', 'sent_at')
