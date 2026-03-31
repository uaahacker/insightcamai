from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import requests
import hmac
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_email_alert(rule_id, event_id, recipient):
    """Send email alert"""
    try:
        from apps.rules.models import Rule
        from apps.events.models import Event
        
        rule = Rule.objects.get(id=rule_id)
        event = Event.objects.get(id=event_id)
        
        subject = f"Alert: {rule.name}"
        message = f"""
        A rule has been triggered: {rule.name}
        
        Camera: {event.camera.name}
        Event: {event.get_event_type_display()}
        Time: {event.occurred_at}
        
        {rule.description}
        """
        
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient])
        
        from apps.notifications.models import NotificationDelivery, NotificationChannel
        # Log delivery
        channel = NotificationChannel.objects.filter(channel_type='email').first()
        if channel:
            NotificationDelivery.objects.create(
                channel=channel,
                recipient=recipient,
                subject=subject,
                body=message,
                status='sent',
                sent_at=timezone.now()
            )
    
    except Exception as e:
        logger.error(f"Error sending email alert: {str(e)}")


@shared_task
def deliver_webhook(rule_id, event_id, webhook_url, secret=''):
    """Deliver webhook notification"""
    try:
        from apps.rules.models import Rule
        from apps.events.models import Event
        
        rule = Rule.objects.get(id=rule_id)
        event = Event.objects.get(id=event_id)
        
        payload = {
            'rule_id': str(rule.id),
            'rule_name': rule.name,
            'event_id': str(event.id),
            'event_type': event.event_type,
            'camera_name': event.camera.name,
            'timestamp': event.occurred_at.isoformat(),
            'data': event.data
        }
        
        headers = {'Content-Type': 'application/json'}
        
        # Sign webhook if secret provided
        if secret:
            signature = hmac.new(
                secret.encode(),
                json.dumps(payload).encode(),
                hashlib.sha256
            ).hexdigest()
            headers['X-Webhook-Signature'] = signature
        
        response = requests.post(
            webhook_url,
            json=payload,
            headers=headers,
            timeout=settings.WEBHOOK_TIMEOUT
        )
        
        success = response.status_code < 400
        
        from apps.notifications.models import NotificationDelivery, NotificationChannel
        channel = NotificationChannel.objects.filter(channel_type='webhook').first()
        if channel:
            NotificationDelivery.objects.create(
                channel=channel,
                recipient=webhook_url,
                body=json.dumps(payload),
                status='sent' if success else 'failed',
                sent_at=timezone.now() if success else None,
                last_error=response.text if not success else ''
            )
        
        if not success:
            raise Exception(f"Webhook returned {response.status_code}")
    
    except Exception as e:
        logger.error(f"Error delivering webhook: {str(e)}")


@shared_task
def retry_failed_notifications():
    """Retry failed notification deliveries"""
    from apps.notifications.models import NotificationDelivery
    from django.conf import settings
    
    failed = NotificationDelivery.objects.filter(
        status='failed',
        retry_count__lt=settings.WEBHOOK_MAX_RETRIES
    )[:10]
    
    for delivery in failed:
        if delivery.channel.channel_type == 'email':
            send_email_alert.delay(
                str(delivery.channel.id),
                delivery.recipient
            )
        elif delivery.channel.channel_type == 'webhook':
            deliver_webhook.delay(
                str(delivery.channel.id),
                delivery.recipient,
                delivery.channel.webhook_secret
            )
        
        delivery.retry_count += 1
        delivery.status = 'retrying'
        delivery.save(update_fields=['retry_count', 'status'])
