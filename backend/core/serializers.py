from rest_framework import serializers


class BaseSerializer(serializers.ModelSerializer):
    """Base serializer with common fields"""
    
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        fields = ('id', 'created_at', 'updated_at')


class AuditableSerializerMixin:
    """Mixin to add created_by and updated_by fields"""
    
    created_by = serializers.StringRelatedField(read_only=True)
    updated_by = serializers.StringRelatedField(read_only=True)
