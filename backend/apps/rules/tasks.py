from celery import shared_task
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task
def process_pending_rules():
    """Process rules that may have been triggered by recent events"""
    from apps.rules.models import Rule, RuleExecution
    from apps.events.models import Event
    from apps.alerts.models import Alert
    
    rules = Rule.objects.filter(is_enabled=True)
    
    for rule in rules:
        # Get recent events
        recent_events = Event.objects.filter(
            camera=rule.camera,
            occurred_at__gte=timezone.now() - timedelta(minutes=5)
        ).order_by('-occurred_at')
        
        if not recent_events.exists():
            continue
        
        # Check if rule condition is met
        should_trigger = False
        
        if rule.condition == 'people_count_exceeds':
            latest_event = recent_events.first()
            if latest_event and latest_event.data.get('people_count', 0) > rule.threshold:
                should_trigger = True
        
        if should_trigger:
            # Check cooldown
            latest_execution = rule.executions.order_by('-triggered_at').first()
            if latest_execution:
                time_since = (timezone.now() - latest_execution.triggered_at).total_seconds() / 60
                if time_since < rule.cooldown_minutes:
                    should_trigger = False
        
        if should_trigger:
            # Execute rule actions
            event = recent_events.first()
            execute_rule_actions(rule, event)


def execute_rule_actions(rule, event):
    """Execute actions defined in a rule"""
    from apps.rules.models import RuleExecution
    from apps.notifications.tasks import send_email_alert, deliver_webhook
    
    actions_executed = []
    
    for action in rule.actions:
        try:
            if action.get('type') == 'email_alert':
                for recipient in action.get('recipients', []):
                    send_email_alert.delay(
                        rule.id.__str__(),
                        event.id.__str__(),
                        recipient
                    )
                    actions_executed.append(f"email:{recipient}")
            
            elif action.get('type') == 'webhook':
                deliver_webhook.delay(
                    rule.id.__str__(),
                    event.id.__str__(),
                    action.get('url'),
                    action.get('secret', '')
                )
                actions_executed.append(f"webhook:{action.get('url')}")
            
            elif action.get('type') == 'dashboard_alert':
                # Create alert
                from apps.alerts.models import Alert
                Alert.objects.create(
                    event=event,
                    camera=event.camera,
                    rule=rule,
                    title=rule.name,
                    message=f"Rule '{rule.name}' triggered",
                    severity=rule.severity
                )
                actions_executed.append("dashboard_alert")
        
        except Exception as e:
            logger.error(f"Error executing action {action} for rule {rule.id}: {str(e)}")
    
    # Log execution
    RuleExecution.objects.create(
        rule=rule,
        event_data=event.data,
        actions_executed=actions_executed
    )
