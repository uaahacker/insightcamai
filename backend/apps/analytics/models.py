from django.db import models
from apps.cameras.models import Camera
from django.utils import timezone


class DailyAnalytics(models.Model):
    """Daily aggregated analytics for a camera"""
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name='daily_analytics')
    date = models.DateField()
    
    # People analytics
    peak_people_count = models.IntegerField(default=0)
    average_people_count = models.FloatField(default=0)
    total_people_entered = models.IntegerField(default=0)
    total_people_exited = models.IntegerField(default=0)
    
    # Events
    total_events = models.IntegerField(default=0)
    critical_events = models.IntegerField(default=0)
    
    # Occupancy
    busy_hours = models.JSONField(default=list)  # {hour: people_count}
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('camera', 'date')
        ordering = ['-date']
        indexes = [
            models.Index(fields=['camera', 'date']),
        ]


class HourlyAnalytics(models.Model):
    """Hourly aggregated analytics"""
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    hour = models.DateTimeField()  # Full timestamp with hour
    
    people_count = models.IntegerField(default=0)
    events_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-hour']
        indexes = [
            models.Index(fields=['camera', 'hour']),
        ]


class AnalyticsSnapshot(models.Model):
    """Store frame-level analytics data temporarily"""
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Frame analytics
    people_count = models.IntegerField(default=0)
    tracked_objects = models.JSONField(default=dict)  # {id: {position, class, confidence}}
    detections = models.JSONField(default=list)  # Raw detections
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['camera', 'timestamp']),
        ]
