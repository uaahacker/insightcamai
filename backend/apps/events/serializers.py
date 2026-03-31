from rest_framework import serializers
from .models import Event
from core.serializers import BaseSerializer


class EventSerializer(BaseSerializer):
    camera_name = serializers.CharField(source='camera.name', read_only=True)
    event_display = serializers.CharField(source='get_event_type_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    
    class Meta(BaseSerializer.Meta):
        model = Event
        fields = ('id', 'camera', 'camera_name', 'event_type', 'event_display', 'severity',
                  'severity_display', 'data', 'snapshot', 'occurred_at', 'is_processed', 'created_at')
