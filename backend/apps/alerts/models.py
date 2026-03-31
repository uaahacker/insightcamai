from django.db import models
from apps.events.models import Event
from apps.cameras.models import Camera
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class Alert(models.Model):
    STATUS_CHOICES = [
        ('triggered', 'Triggered'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='alerts')
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name='alerts')
    rule = models.ForeignKey('rules.Rule', on_delete=models.SET_NULL, null=True, blank=True)
    
    title = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='triggered')
    severity = models.CharField(max_length=20, choices=Event.SEVERITY_CHOICES, default='medium')
    
    triggered_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    acknowledged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-triggered_at']
        indexes = [
            models.Index(fields=['camera', 'status', 'triggered_at']),
            models.Index(fields=['status', 'severity']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.camera.name}"
