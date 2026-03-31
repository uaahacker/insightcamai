from django.db import models
from apps.organizations.models import Organization
from apps.cameras.models import Camera
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class Rule(models.Model):
    CONDITION_CHOICES = [
        ('people_count_exceeds', 'People Count Exceeds'),
        ('people_count_below', 'People Count Below'),
        ('line_crossing_detected', 'Line Crossing Detected'),
        ('intrusion_detected', 'Intrusion Detected'),
        ('loitering_detected', 'Loitering Detected'),
        ('camera_offline', 'Camera Offline'),
        ('parking_occupied', 'Parking Occupied'),
        ('parking_empty', 'Parking Empty'),
        ('object_left', 'Object Left Behind'),
        ('object_removed', 'Object Removed'),
    ]
    
    ACTION_CHOICES = [
        ('dashboard_alert', 'Dashboard Alert'),
        ('email_alert', 'Email Alert'),
        ('webhook', 'Webhook'),
        ('sms', 'SMS (Future)'),
        ('whatsapp', 'WhatsApp (Future)'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='rules')
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name='rules', null=True, blank=True)
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Condition
    condition = models.CharField(max_length=50, choices=CONDITION_CHOICES)
    threshold = models.IntegerField(default=0)
    
    # Time window (optional)
    start_time = models.TimeField(null=True, blank=True, help_text='Start time for rule (HH:MM)')
    end_time = models.TimeField(null=True, blank=True, help_text='End time for rule (HH:MM)')
    days_of_week = models.CharField(max_length=50, blank=True, help_text='0-6, comma separated')
    
    # Actions
    actions = models.JSONField(default=list)  # [{'type': 'email', 'recipients': []}]
    
    # Settings
    severity = models.CharField(max_length=20, choices=models.Model._meta.get_field('severity').choices if hasattr(models.Model._meta, 'get_field') else [('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')], default='medium')
    cooldown_minutes = models.IntegerField(default=5, help_text='Minutes to wait before triggering again')
    is_enabled = models.BooleanField(default=True)
    
    # Audit
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'is_enabled']),
            models.Index(fields=['camera']),
        ]
    
    def __str__(self):
        return self.name


class RuleExecution(models.Model):
    """Track when rules are triggered"""
    rule = models.ForeignKey(Rule, on_delete=models.CASCADE, related_name='executions')
    triggered_at = models.DateTimeField(auto_now_add=True)
    event_data = models.JSONField(default=dict)
    actions_executed = models.JSONField(default=list)
    
    class Meta:
        ordering = ['-triggered_at']
        indexes = [
            models.Index(fields=['rule', 'triggered_at']),
        ]
