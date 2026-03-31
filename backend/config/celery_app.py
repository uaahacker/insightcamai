import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

app = Celery('cctv_analytics')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


# Celery Beat Schedule
app.conf.beat_schedule = {
    'check-camera-health': {
        'task': 'apps.cameras.tasks.check_camera_health',
        'schedule': crontab(minute='*/5'),
    },
    'cleanup-old-snapshots': {
        'task': 'apps.cameras.tasks.cleanup_old_snapshots',
        'schedule': crontab(hour=2, minute=0),
    },
    'process-pending-rules': {
        'task': 'apps.rules.tasks.process_pending_rules',
        'schedule': crontab(minute='*/1'),
    },
    'retry-failed-notifications': {
        'task': 'apps.notifications.tasks.retry_failed_notifications',
        'schedule': crontab(minute='*/5'),
    },
}
