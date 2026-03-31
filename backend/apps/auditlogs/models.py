from django.db import models
from apps.organizations.models import Organization
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('permission_change', 'Permission Change'),
        ('camera_added', 'Camera Added'),
        ('camera_removed', 'Camera Removed'),
        ('rule_triggered', 'Rule Triggered'),
        ('alert_acknowledged', 'Alert Acknowledged'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='audit_logs')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    resource_type = models.CharField(max_length=100)  # Camera, Rule, Alert, etc.
    resource_id = models.CharField(max_length=255, blank=True)
    
    changes = models.JSONField(default=dict)  # Before/after values
    ip_address = models.CharField(max_length=45, blank=True)  # IPv4 or IPv6
    user_agent = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['action']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.action} on {self.resource_type}"
