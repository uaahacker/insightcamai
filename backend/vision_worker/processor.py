"""
Vision Worker - Handles AI-powered video analytics

This module processes video streams from cameras and performs:
- Person detection and tracking
- People counting
- Line crossing detection
- Intrusion detection
- Event generation
"""

import cv2
import numpy as np
from ultralytics import YOLO
import logging
from datetime import datetime
from typing import Dict, List, Tuple
import os

logger = logging.getLogger(__name__)


class ObjectTracker:
    """Simple object tracker using centroid tracking"""
    
    def __init__(self, max_disappeared=50):
        self.next_object_id = 0
        self.objects = {}
        self.disappeared = {}
        self.max_disappeared = max_disappeared
    
    def register(self, centroid):
        self.objects[self.next_object_id] = centroid
        self.disappeared[self.next_object_id] = 0
        self.next_object_id += 1
    
    def deregister(self, object_id):
        del self.objects[object_id]
        del self.disappeared[object_id]
    
    def update(self, rects):
        """Update tracker with new detections"""
        if len(rects) == 0:
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
            return self.objects
        
        input_centroids = np.zeros((len(rects), 2), dtype="int")
        for (i, (startX, startY, endX, endY)) in enumerate(rects):
            cX = (startX + endX) // 2
            cY = (startY + endY) // 2
            input_centroids[i] = (cX, cY)
        
        if len(self.objects) == 0:
            for i in range(0, len(input_centroids)):
                self.register(input_centroids[i])
        else:
            object_ids = list(self.objects.keys())
            object_centroids = list(self.objects.values())
            
            # Simple distance matching
            if len(object_centroids) <= len(input_centroids):
                for (i, input_centroid) in enumerate(input_centroids):
                    distances = [np.linalg.norm(oc - input_centroid) for oc in object_centroids]
                    j = np.argmin(distances)
                    
                    if distances[j] < 50:
                        self.objects[object_ids[j]] = input_centroid
                        self.disappeared[object_ids[j]] = 0
                    else:
                        self.register(input_centroid)
            else:
                for (i, input_centroid) in enumerate(input_centroids):
                    distances = [np.linalg.norm(oc - input_centroid) for oc in object_centroids]
                    j = np.argmin(distances)
                    
                    if distances[j] < 50:
                        self.objects[object_ids[j]] = input_centroid
                        self.disappeared[object_ids[j]] = 0
                
                for object_id in object_ids:
                    if object_id not in self.objects:
                        self.deregister(object_id)
        
        return self.objects


class VisionProcessor:
    """Main vision processing pipeline"""
    
    def __init__(self, model_path='yolov8n.pt'):
        """Initialize vision processor with YOLO model"""
        try:
            self.model = YOLO(model_path)
            self.tracker = ObjectTracker()
            self.person_count = 0
            self.last_frame = None
            logger.info("Vision processor initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing vision processor: {str(e)}")
            self.model = None
    
    def process_frame(self, frame: np.ndarray) -> Dict:
        """
        Process a single frame and extract analytics
        
        Returns:
            Dictionary with:
            - people_count: Number of people detected
            - detections: List of detection bboxes
            - tracked_objects: Dict of tracked objects
            - events: List of detected events
        """
        if self.model is None:
            return {'people_count': 0, 'detections': [], 'events': []}
        
        try:
            # Run inference
            results = self.model(frame, verbose=False)
            result = results[0]
            
            # Extract person detections
            person_boxes = []
            if result.boxes is not None:
                for box in result.boxes:
                    conf = float(box.conf)
                    cls = int(box.cls)
                    
                    # Class 0 is person in YOLO
                    if cls == 0 and conf > 0.5:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        person_boxes.append((x1, y1, x2, y2))
            
            # Update tracker
            self.tracker.update(person_boxes)
            
            # Count people
            self.person_count = len(self.tracker.objects)
            
            self.last_frame = frame.copy()
            
            return {
                'people_count': self.person_count,
                'detections': person_boxes,
                'tracked_objects': self.tracker.objects,
                'timestamp': datetime.now().isoformat(),
                'events': []
            }
        
        except Exception as e:
            logger.error(f"Error processing frame: {str(e)}")
            return {
                'people_count': 0,
                'detections': [],
                'tracked_objects': {},
                'events': [],
                'error': str(e)
            }
    
    def detect_line_crossing(self, boxes: List[Tuple], line_coords: Tuple) -> List[Dict]:
        """
        Detect line crossings
        line_coords: (x1, y1, x2, y2)
        """
        events = []
        # Implementation placeholder - would track object positions against line
        return events
    
    def detect_intrusion(self, boxes: List[Tuple], restricted_area: Tuple) -> List[Dict]:
        """
        Detect intrusions into restricted areas
        restricted_area: (x1, y1, x2, y2) or polygon
        """
        events = []
        # Implementation placeholder
        return events
    
    def detect_loitering(self, tracked_objects: Dict, threshold_frames=100) -> List[Dict]:
        """
        Detect loitering (people staying in one place too long)
        """
        events = []
        # Implementation placeholder
        return events
