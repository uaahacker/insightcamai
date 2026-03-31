from django.db import models
from apps.organizations.models import Organization
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class NotificationChannel(models.Model):
    CHANNEL_TYPE_CHOICES = [
        ('email', 'Email'),
        ('webhook', 'Webhook'),
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    channel_type = models.CharField(max_length=50, choices=CHANNEL_TYPE_CHOICES)
    
    # Email config
    recipients = models.JSONField(default=list)  # List of email addresses
    
    # Webhook config
    webhook_url = models.URLField(blank=True)
    webhook_secret = models.CharField(max_length=255, blank=True)
    
    # SMS/WhatsApp config (future)
    phone_numbers = models.JSONField(default=list)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ('organization', 'name')


class NotificationDelivery(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('retrying', 'Retrying'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    channel = models.ForeignKey(NotificationChannel, on_delete=models.CASCADE)
    recipient = models.CharField(max_length=255)  # Email or webhook URL
    
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField()
    payload = models.JSONField(default=dict)
    
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    retry_count = models.IntegerField(default=0)
    last_error = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['channel', 'status']),
        ]
