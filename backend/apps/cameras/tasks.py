from celery import shared_task
from django.utils import timezone
from django.db import transaction
import logging
from .models import Camera, CameraHealthLog
from .stream_tester import StreamConnectionTester

logger = logging.getLogger(__name__)


@shared_task
def check_camera_health():
    """Check health of all enabled cameras"""
    cameras = Camera.objects.filter(is_enabled=True)
    
    for camera in cameras:
        try:
            success, message = test_stream_connection(camera)
            
            old_status = camera.health_status
            
            if success:
                new_status = 'online'
                camera.consecutive_failures = 0
                camera.last_seen = timezone.now()
            else:
                camera.consecutive_failures += 1
                if camera.consecutive_failures >= 3:
                    if 'credential' in message.lower() or 'unauthorized' in message.lower():
                        new_status = 'bad_credentials'
                    elif 'timeout' in message.lower():
                        new_status = 'unreachable'
                    else:
                        new_status = 'offline'
                else:
                    new_status = 'unstable'
            
            camera.health_status = new_status
            camera.last_health_check = timezone.now()
            
            # Log health check
            CameraHealthLog.objects.create(
                camera=camera,
                status=new_status,
                error_message=message if not success else ''
            )
            
            camera.save(update_fields=['health_status', 'last_health_check', 'consecutive_failures', 'last_seen'])
            
            if old_status != new_status:
                logger.info(f"Camera {camera.name} status changed: {old_status} -> {new_status}")
        
        except Exception as e:
            logger.error(f"Error checking health for camera {camera.id}: {str(e)}")


def test_stream_connection(camera):
    """Test stream connection for a camera"""
    if camera.connection_type == 'rtsp':
        return StreamConnectionTester.test_rtsp_stream(
            camera.host,
            camera.port,
            camera.username,
            camera.decrypt_password(),
            camera.stream_path,
            camera.stream_protocol
        )
    elif camera.connection_type == 'http_mjpeg':
        return StreamConnectionTester.test_http_stream(
            camera.host,
            camera.port,
            camera.stream_path,
            camera.username,
            camera.decrypt_password()
        )
    else:
        return False, "Unsupported connection type"


@shared_task
def cleanup_old_snapshots():
    """Remove old snapshots based on retention policy"""
    from datetime import timedelta
    retention_days = __import__('django.conf', fromlist=['settings']).settings.SNAPSHOT_RETENTION_DAYS
    
    cutoff_date = timezone.now() - timedelta(days=retention_days)
    
    try:
        from .models import Snapshot
        snapshots = Snapshot.objects.filter(timestamp__lt=cutoff_date)
        
        # Delete image files
        for snapshot in snapshots:
            if snapshot.image:
                snapshot.image.delete()
        
        # Delete records
        count = snapshots.count()
        snapshots.delete()
        
        logger.info(f"Cleaned up {count} old snapshots")
    except Exception as e:
        logger.error(f"Error cleaning up snapshots: {str(e)}")
