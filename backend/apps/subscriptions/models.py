from django.db import models
from apps.organizations.models import Organization
from django.utils import timezone
from datetime import timedelta
import uuid


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2)
    price_annual = models.DecimalField(max_digits=10, decimal_places=2)
    
    max_cameras = models.IntegerField(default=5)
    max_users = models.IntegerField(default=5)
    
    features = models.JSONField(default=list)  # List of feature strings
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['price_monthly']
    
    def __str__(self):
        return self.name


class Subscription(models.Model):
    BILLING_CYCLE_CHOICES = [
        ('monthly', 'Monthly'),
        ('annual', 'Annual'),
    ]
    
    STATUS_CHOICES = [
        ('trial', 'Trial'),
        ('active', 'Active'),
        ('canceled', 'Canceled'),
        ('suspended', 'Suspended'),
        ('expired', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True, blank=True)
    
    billing_cycle = models.CharField(max_length=50, choices=BILLING_CYCLE_CHOICES, default='monthly')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='trial')
    
    started_at = models.DateTimeField(auto_now_add=True)
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    
    stripe_customer_id = models.CharField(max_length=255, blank=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.organization.name} - {self.status}"
    
    def is_trial(self):
        return self.status == 'trial'
    
    def is_active(self):
        return self.status in ['active', 'trial']
    
    def days_until_expiry(self):
        if self.is_active():
            return (self.current_period_end - timezone.now()).days
        return 0
