import cv2
import numpy as np
from ultralytics import YOLO
import threading
import time
from typing import List, Tuple, Dict, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VisionTracker:
    def __init__(self, model_path: str = "yolov8n.pt", camera_id: int = 0):
        """
        Initialize vision tracking system
        
        Args:
            model_path: Path to YOLO model file
            camera_id: Camera device ID (0 for default camera)
        """
        self.model_path = model_path
        self.camera_id = camera_id
        self.model = None
        self.cap = None
        self.is_running = False
        self.current_frame = None
        self.detections = []
        self.detection_callback = None
        self.frame_lock = threading.Lock()
        
        # Detection parameters
        self.confidence_threshold = 0.5
        self.target_classes = [0, 39, 41, 42, 43, 44, 45, 46, 47]  # person, bottle, cup, fork, knife, spoon, bowl, banana, apple
        
    def initialize(self) -> bool:
        """Initialize camera and YOLO model"""
        try:
            # Load YOLO model
            logger.info(f"Loading YOLO model: {self.model_path}")
            self.model = YOLO(self.model_path)
            
            # Initialize camera
            logger.info(f"Initializing camera: {self.camera_id}")
            self.cap = cv2.VideoCapture(self.camera_id)
            
            if not self.cap.isOpened():
                logger.error("Failed to open camera")
                return False
                
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            logger.info("Vision tracking system initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize vision tracking: {e}")
            return False
    
    def set_detection_callback(self, callback):
        """Set callback function for detection events"""
        self.detection_callback = callback
    
    def start_tracking(self):
        """Start vision tracking in separate thread"""
        if self.is_running:
            logger.warning("Vision tracking already running")
            return
            
        self.is_running = True
        self.tracking_thread = threading.Thread(target=self._tracking_loop, daemon=True)
        self.tracking_thread.start()
        logger.info("Vision tracking started")
    
    def stop_tracking(self):
        """Stop vision tracking"""
        self.is_running = False
        if hasattr(self, 'tracking_thread'):
            self.tracking_thread.join(timeout=2.0)
        logger.info("Vision tracking stopped")
    
    def _tracking_loop(self):
        """Main tracking loop"""
        while self.is_running:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    logger.warning("Failed to read frame from camera")
                    time.sleep(0.1)
                    continue
                
                # Store current frame
                with self.frame_lock:
                    self.current_frame = frame.copy()
                
                # Run YOLO detection
                results = self.model(frame, conf=self.confidence_threshold, classes=self.target_classes)
                
                # Process detections
                detections = self._process_detections(results[0], frame.shape)
                
                # Update detections
                with self.frame_lock:
                    self.detections = detections
                
                # Call detection callback if set
                if self.detection_callback and detections:
                    self.detection_callback(detections)
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.033)  # ~30 FPS
                
            except Exception as e:
                logger.error(f"Error in tracking loop: {e}")
                time.sleep(0.1)
    
    def _process_detections(self, results, frame_shape) -> List[Dict]:
        """Process YOLO detection results"""
        detections = []
        
        if results.boxes is not None:
            boxes = results.boxes.xyxy.cpu().numpy()
            confidences = results.boxes.conf.cpu().numpy()
            classes = results.boxes.cls.cpu().numpy()
            
            for i, (box, conf, cls) in enumerate(zip(boxes, confidences, classes)):
                x1, y1, x2, y2 = box
                
                # Calculate center point and dimensions
                center_x = int((x1 + x2) / 2)
                center_y = int((y1 + y2) / 2)
                width = int(x2 - x1)
                height = int(y2 - y1)
                
                # Calculate relative position (0-1 range)
                rel_x = center_x / frame_shape[1]
                rel_y = center_y / frame_shape[0]
                
                detection = {
                    'id': i,
                    'class_id': int(cls),
                    'class_name': self.model.names[int(cls)],
                    'confidence': float(conf),
                    'bbox': [int(x1), int(y1), int(x2), int(y2)],
                    'center': [center_x, center_y],
                    'relative_position': [rel_x, rel_y],
                    'size': [width, height],
                    'timestamp': time.time()
                }
                
                detections.append(detection)
        
        return detections
    
    def get_current_frame(self) -> Optional[np.ndarray]:
        """Get current camera frame"""
        with self.frame_lock:
            return self.current_frame.copy() if self.current_frame is not None else None
    
    def get_detections(self) -> List[Dict]:
        """Get current detections"""
        with self.frame_lock:
            return self.detections.copy()
    
    def get_annotated_frame(self) -> Optional[np.ndarray]:
        """Get current frame with detection annotations"""
        frame = self.get_current_frame()
        if frame is None:
            return None
            
        detections = self.get_detections()
        
        # Draw detections on frame
        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            confidence = detection['confidence']
            class_name = detection['class_name']
            
            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw label
            label = f"{class_name}: {confidence:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), (x1 + label_size[0], y1), (0, 255, 0), -1)
            cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
            
            # Draw center point
            center_x, center_y = detection['center']
            cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)
        
        return frame
    
    def find_closest_object(self, target_position: Tuple[float, float] = (0.5, 0.5)) -> Optional[Dict]:
        """Find closest object to target position"""
        detections = self.get_detections()
        if not detections:
            return None
        
        min_distance = float('inf')
        closest_object = None
        
        for detection in detections:
            rel_x, rel_y = detection['relative_position']
            distance = np.sqrt((rel_x - target_position[0])**2 + (rel_y - target_position[1])**2)
            
            if distance < min_distance:
                min_distance = distance
                closest_object = detection
        
        return closest_object
    
    def cleanup(self):
        """Cleanup resources"""
        self.stop_tracking()
        
        if self.cap:
            self.cap.release()
        
        cv2.destroyAllWindows()
        logger.info("Vision tracking cleanup completed")

# Example usage and testing
if __name__ == "__main__":
    def detection_callback(detections):
        print(f"Detected {len(detections)} objects:")
        for det in detections:
            print(f"  - {det['class_name']}: {det['confidence']:.2f} at {det['center']}")
    
    # Initialize vision tracker
    tracker = VisionTracker()
    
    if tracker.initialize():
        tracker.set_detection_callback(detection_callback)
        tracker.start_tracking()
        
        try:
            # Run for 30 seconds
            for i in range(300):
                time.sleep(0.1)
                
                # Display annotated frame every second
                if i % 10 == 0:
                    frame = tracker.get_annotated_frame()
                    if frame is not None:
                        cv2.imshow('Vision Tracking', frame)
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
        
        except KeyboardInterrupt:
            print("Interrupted by user")
        
        finally:
            tracker.cleanup()
    else:
        print("Failed to initialize vision tracker")
