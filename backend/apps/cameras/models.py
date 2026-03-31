from django.db import models
from django.contrib.auth import get_user_model
from apps.organizations.models import Organization, Site
from core.security import CredentialManager
import uuid
import json

User = get_user_model()


class Camera(models.Model):
    CONNECTION_TYPE_CHOICES = [
        ('rtsp', 'RTSP'),
        ('http_mjpeg', 'HTTP MJPEG'),
        ('onvif', 'ONVIF'),
        ('dvr_nvr', 'DVR/NVR'),
        ('custom', 'Custom'),
    ]
    
    HEALTH_STATUS_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('unstable', 'Unstable'),
        ('bad_credentials', 'Bad Credentials'),
        ('unreachable', 'Unreachable'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='cameras')
    site = models.ForeignKey(Site, on_delete=models.SET_NULL, null=True, blank=True, related_name='cameras')
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Connection
    connection_type = models.CharField(max_length=20, choices=CONNECTION_TYPE_CHOICES, default='rtsp')
    host = models.CharField(max_length=255)  # IP address or hostname
    port = models.IntegerField(default=554)
    username = models.CharField(max_length=255, blank=True, null=True)
    encrypted_password = models.TextField(blank=True, null=True)
    stream_path = models.CharField(max_length=500, blank=True, help_text='e.g., /Streaming/channels/101')
    rtsp_url = models.CharField(max_length=500, blank=True, help_text='Full RTSP URL')
    stream_protocol = models.CharField(max_length=20, default='rtsp', choices=[('rtsp', 'RTSP'), ('rtsps', 'RTSPS')])
    stream_profile = models.CharField(max_length=20, default='main', choices=[('main', 'Main'), ('sub', 'Substream')])
    
    # Metadata
    manufacturer = models.CharField(max_length=255, blank=True)
    model = models.CharField(max_length=255, blank=True)
    resolution = models.CharField(max_length=50, blank=True, help_text='e.g., 1920x1080')
    fps = models.IntegerField(default=30)
    
    # Status and Health
    is_enabled = models.BooleanField(default=True)
    health_status = models.CharField(max_length=50, choices=HEALTH_STATUS_CHOICES, default='offline')
    last_health_check = models.DateTimeField(null=True, blank=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    consecutive_failures = models.IntegerField(default=0)
    
    # Analytics
    analytics_enabled = models.BooleanField(default=False)
    people_detection = models.BooleanField(default=True)
    people_counting = models.BooleanField(default=True)
    line_crossing = models.BooleanField(default=False)
    intrusion_detection = models.BooleanField(default=False)
    loitering_detection = models.BooleanField(default=False)
    parking_detection = models.BooleanField(default=False)
    
    # Configuration
    extended_config = models.JSONField(default=dict, blank=True)  # For storing zones, lines, etc.
    
    # Audit
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='cameras_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'is_enabled']),
            models.Index(fields=['health_status']),
            models.Index(fields=['created_at']),
        ]
        unique_together = ('organization', 'name')
    
    def __str__(self):
        return f"{self.name} ({self.organization.name})"
    
    def decrypt_password(self):
        if self.encrypted_password:
            manager = CredentialManager()
            return manager.decrypt_password(self.encrypted_password)
        return None
    
    def encrypt_password(self, password):
        if password:
            manager = CredentialManager()
            self.encrypted_password = manager.encrypt_password(password)
    
    def get_stream_url(self):
        """Generate full stream URL"""
        if self.rtsp_url:
            return self.rtsp_url
        
        password = self.decrypt_password()
        auth = f"{self.username}:{password}@" if self.username and password else ""
        
        if self.connection_type == 'rtsp':
            return f"{self.stream_protocol}://{auth}{self.host}:{self.port}{self.stream_path}"
        
        return None


class CameraHealthLog(models.Model):
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name='health_logs')
    status = models.CharField(max_length=50, choices=Camera.HEALTH_STATUS_CHOICES)
    latency_ms = models.IntegerField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    checked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-checked_at']
        indexes = [
            models.Index(fields=['camera', 'checked_at']),
        ]


class Snapshot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name='snapshots')
    image = models.ImageField(upload_to='snapshots/%Y/%m/%d/')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['camera', 'timestamp']),
        ]


class VideoClip(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name='clips')
    video_file = models.FileField(upload_to='clips/%Y/%m/%d/')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration_seconds = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['camera', 'created_at']),
        ]
