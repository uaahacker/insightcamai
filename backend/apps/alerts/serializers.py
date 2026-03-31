from rest_framework import serializers
from .models import Alert
from core.serializers import BaseSerializer


class AlertSerializer(BaseSerializer):
    camera_name = serializers.CharField(source='camera.name', read_only=True)
    
    class Meta(BaseSerializer.Meta):
        model = Alert
        fields = ('id', 'camera', 'camera_name', 'title', 'message', 'status', 'severity',
                  'triggered_at', 'acknowledged_at', 'resolved_at', 'created_at')
