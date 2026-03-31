"""
Stream ingestion and processing tasks
"""

import logging
import cv2
import os
import subprocess
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .processor import VisionProcessor

logger = logging.getLogger(__name__)


@shared_task
def process_camera_stream(camera_id):
    """
    Main task to process a camera stream
    
    This task:
    1. Connects to camera stream
    2. Reads frames
    3. Runs AI analytics
    4. Generates events
    5. Stores metrics
    """
    from apps.cameras.models import Camera
    from apps.events.models import Event
    from apps.analytics.models import DailyAnalytics, AnalyticsSnapshot
    
    try:
        camera = Camera.objects.get(id=camera_id)
        
        if not camera.is_enabled or not camera.analytics_enabled:
            return
        
        # Get stream URL
        stream_url = camera.get_stream_url()
        if not stream_url:
            logger.warning(f"No stream URL for camera {camera.id}")
            return
        
        # Initialize processor
        processor = VisionProcessor()
        if not processor.model:
            logger.error(f"Vision processor not available for camera {camera.id}")
            return
        
        # Connect to stream
        cap = cv2.VideoCapture(stream_url)
        
        if not cap.isOpened():
            logger.error(f"Could not open stream for camera {camera.id}: {stream_url}")
            return
        
        frame_count = 0
        last_event_time = timezone.now()
        
        # Process stream
        while cap.isOpened() and frame_count < 300:  # Process for ~10 seconds at 30 FPS
            ret, frame = cap.read()
            
            if not ret:
                logger.warning(f"Failed to read frame from camera {camera.id}")
                break
            
            frame_count += 1
            
            # Skip frames for performance
            if frame_count % 5 != 0:
                continue
            
            # Process frame
            analytics = processor.process_frame(frame)
            
            # Store analytics snapshot
            try:
                AnalyticsSnapshot.objects.create(
                    camera=camera,
                    people_count=analytics['people_count'],
                    tracked_objects=analytics['tracked_objects'],
                    detections=analytics['detections']
                )
            except Exception as e:
                logger.error(f"Error storing analytics snapshot: {str(e)}")
            
            # Generate events if people count changed
            if camera.people_counting:
                people_count = analytics.get('people_count', 0)
                
                # Create event for people counting
                if people_count > 0:
                    now = timezone.now()
                    if (now - last_event_time).total_seconds() > 60:  # Avoid duplicate events
                        Event.objects.create(
                            camera=camera,
                            event_type='people_count_change',
                            severity='low',
                            data={
                                'people_count': people_count,
                                'detections': len(analytics['detections'])
                            },
                            occurred_at=now
                        )
                        last_event_time = now
        
        cap.release()
        
        # Update daily analytics
        today = timezone.now().date()
        daily, created = DailyAnalytics.objects.get_or_create(
            camera=camera,
            date=today
        )
        daily.total_events = Event.objects.filter(
            camera=camera,
            occurred_at__date=today
        ).count()
        daily.save(update_fields=['total_events'])
        
        logger.info(f"Processed {frame_count} frames from camera {camera.id}")
    
    except Camera.DoesNotExist:
        logger.error(f"Camera {camera_id} not found")
    except Exception as e:
        logger.error(f"Error processing camera stream {camera_id}: {str(e)}")


@shared_task
def convert_stream_to_hls(camera_id):
    """
    Convert RTSP stream to HLS for browser playback
    
    This requires FFmpeg to be installed
    """
    from apps.cameras.models import Camera
    
    try:
        camera = Camera.objects.get(id=camera_id)
        stream_url = camera.get_stream_url()
        
        if not stream_url:
            logger.warning(f"No stream URL for camera {camera.id}")
            return
        
        # HLS output path
        output_dir = f'/tmp/hls/{camera.id}'
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, 'stream.m3u8')
        
        # FFmpeg command to convert RTSP to HLS
        cmd = [
            'ffmpeg',
            '-rtsp_transport', 'tcp',
            '-i', stream_url,
            '-c:v', 'libx264',
            '-preset', 'ultrafast',
            '-c:a', 'aac',
            '-f', 'hls',
            '-hls_time', '2',
            '-hls_list_size', '5',
            '-hls_playlist_type', 'event',
            output_path
        ]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=None  # For Windows, remove this
        )
        
        logger.info(f"Started HLS conversion for camera {camera.id}")
        
        return output_path
    
    except Camera.DoesNotExist:
        logger.error(f"Camera {camera_id} not found")
    except Exception as e:
        logger.error(f"Error converting stream for camera {camera_id}: {str(e)}")
