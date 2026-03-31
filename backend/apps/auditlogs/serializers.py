from rest_framework import serializers
from .models import AuditLog
from core.serializers import BaseSerializer


class AuditLogSerializer(BaseSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta(BaseSerializer.Meta):
        model = AuditLog
        fields = ('id', 'user', 'user_email', 'action', 'resource_type', 'resource_id',
                  'changes', 'ip_address', 'created_at')
