from django.db import models
from apps.cameras.models import Camera
import uuid


class Event(models.Model):
    EVENT_TYPE_CHOICES = [
        ('people_detection', 'Person Detected'),
        ('people_count_change', 'People Count Changed'),
        ('line_crossing', 'Line Crossing'),
        ('intrusion', 'Intrusion Detection'),
        ('loitering', 'Loitering'),
        ('parking_occupied', 'Parking Occupied'),
        ('parking_empty', 'Parking Empty'),
        ('object_left', 'Object Left Behind'),
        ('object_removed', 'Object Removed'),
        ('camera_offline', 'Camera Offline'),
        ('camera_online', 'Camera Online'),
    ]
    
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')
    
    # Event Data
    data = models.JSONField(default=dict)  # people_count, coordinates, etc.
    snapshot = models.ImageField(upload_to='event_snapshots/%Y/%m/%d/', null=True, blank=True)
    
    # Timestamps
    occurred_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Tracking
    is_processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-occurred_at']
        indexes = [
            models.Index(fields=['camera', 'event_type', 'occurred_at']),
            models.Index(fields=['is_processed', 'occurred_at']),
            models.Index(fields=['severity']),
        ]
    
    def __str__(self):
        return f"{self.get_event_type_display()} - {self.camera.name}"
