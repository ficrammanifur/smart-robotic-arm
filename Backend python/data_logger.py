import csv
import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import threading
import logging

logger = logging.getLogger(__name__)

class DataLogger:
    def __init__(self, data_dir: str = "../data"):
        """
        Initialize data logger
        
        Args:
            data_dir: Directory to store data files
        """
        self.data_dir = data_dir
        self.csv_file = os.path.join(data_dir, "dataset.csv")
        self.images_dir = os.path.join(data_dir, "images")
        self.lock = threading.Lock()
        
        # Ensure directories exist
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(self.images_dir, exist_ok=True)
        
        # CSV headers
        self.csv_headers = [
            'timestamp', 'mode', 'objects_detected', 'grab_success', 'distance_cm',
            'servo_base', 'servo_shoulder', 'servo_elbow', 'servo_wrist', 'gripper_state',
            'detection_confidence', 'object_class', 'object_position_x', 'object_position_y',
            'execution_time_ms', 'error_message'
        ]
        
        # Initialize CSV file if it doesn't exist
        self._initialize_csv()
    
    def _initialize_csv(self):
        """Initialize CSV file with headers if it doesn't exist"""
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(self.csv_headers)
            logger.info(f"Created new CSV file: {self.csv_file}")
    
    def log_operation(self, 
                     mode: str,
                     objects_detected: int = 0,
                     grab_success: bool = False,
                     distance_cm: float = 0.0,
                     servo_angles: List[int] = None,
                     gripper_state: str = "unknown",
                     detection_data: Dict = None,
                     execution_time_ms: float = 0.0,
                     error_message: str = ""):
        """
        Log a robotic arm operation
        
        Args:
            mode: Operation mode ('auto' or 'manual')
            objects_detected: Number of objects detected
            grab_success: Whether grab operation was successful
            distance_cm: Distance measurement from ultrasonic sensor
            servo_angles: List of servo angles [base, shoulder, elbow, wrist, gripper]
            gripper_state: State of gripper ('open', 'closed', 'unknown')
            detection_data: Vision detection data
            execution_time_ms: Time taken for operation
            error_message: Any error message
        """
        try:
            with self.lock:
                timestamp = datetime.now().isoformat()
                
                # Default servo angles
                if servo_angles is None:
                    servo_angles = [90, 90, 90, 90, 90]
                
                # Extract detection data
                detection_confidence = 0.0
                object_class = ""
                object_position_x = 0.0
                object_position_y = 0.0
                
                if detection_data:
                    detection_confidence = detection_data.get('confidence', 0.0)
                    object_class = detection_data.get('class_name', '')
                    rel_pos = detection_data.get('relative_position', [0.0, 0.0])
                    object_position_x = rel_pos[0]
                    object_position_y = rel_pos[1]
                
                # Prepare row data
                row_data = [
                    timestamp,
                    mode,
                    objects_detected,
                    grab_success,
                    distance_cm,
                    servo_angles[0] if len(servo_angles) > 0 else 90,
                    servo_angles[1] if len(servo_angles) > 1 else 90,
                    servo_angles[2] if len(servo_angles) > 2 else 90,
                    servo_angles[3] if len(servo_angles) > 3 else 90,
                    gripper_state,
                    detection_confidence,
                    object_class,
                    object_position_x,
                    object_position_y,
                    execution_time_ms,
                    error_message
                ]
                
                # Write to CSV
                with open(self.csv_file, 'a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(row_data)
                
                logger.info(f"Logged operation: {mode} mode, {objects_detected} objects, success: {grab_success}")
                
        except Exception as e:
            logger.error(f"Failed to log operation: {e}")
    
    def save_image(self, image_data, filename: str = None) -> str:
        """
        Save image data to file
        
        Args:
            image_data: Image data (numpy array or bytes)
            filename: Optional filename, auto-generated if None
            
        Returns:
            Path to saved image file
        """
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                filename = f"capture_{timestamp}.jpg"
            
            filepath = os.path.join(self.images_dir, filename)
            
            # Save image based on data type
            if hasattr(image_data, 'shape'):  # numpy array
                import cv2
                cv2.imwrite(filepath, image_data)
            else:  # bytes
                with open(filepath, 'wb') as f:
                    f.write(image_data)
            
            logger.info(f"Saved image: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to save image: {e}")
            return ""
    
    def get_statistics(self, days: int = 7) -> Dict[str, Any]:
        """
        Get operation statistics for the last N days
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with statistics
        """
        try:
            import pandas as pd
            
            # Read CSV data
            df = pd.read_csv(self.csv_file)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Filter by date range
            cutoff_date = datetime.now() - pd.Timedelta(days=days)
            recent_df = df[df['timestamp'] >= cutoff_date]
            
            if recent_df.empty:
                return {'error': 'No data available for the specified period'}
            
            # Calculate statistics
            stats = {
                'total_operations': len(recent_df),
                'successful_grabs': recent_df['grab_success'].sum(),
                'success_rate': recent_df['grab_success'].mean() * 100,
                'auto_mode_operations': len(recent_df[recent_df['mode'] == 'auto']),
                'manual_mode_operations': len(recent_df[recent_df['mode'] == 'manual']),
                'total_objects_detected': recent_df['objects_detected'].sum(),
                'average_distance': recent_df['distance_cm'].mean(),
                'average_execution_time': recent_df['execution_time_ms'].mean(),
                'most_detected_object': recent_df['object_class'].mode().iloc[0] if not recent_df['object_class'].mode().empty else 'None',
                'daily_operations': recent_df.groupby(recent_df['timestamp'].dt.date).size().to_dict()
            }
            
            # Convert numpy types to Python types for JSON serialization
            for key, value in stats.items():
                if hasattr(value, 'item'):
                    stats[key] = value.item()
                elif isinstance(value, dict):
                    stats[key] = {str(k): int(v) if hasattr(v, 'item') else v for k, v in value.items()}
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {'error': str(e)}
    
    def export_data(self, format: str = 'json', days: int = 30) -> str:
        """
        Export data in specified format
        
        Args:
            format: Export format ('json' or 'csv')
            days: Number of days to export
            
        Returns:
            Path to exported file
        """
        try:
            import pandas as pd
            
            # Read and filter data
            df = pd.read_csv(self.csv_file)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            cutoff_date = datetime.now() - pd.Timedelta(days=days)
            recent_df = df[df['timestamp'] >= cutoff_date]
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if format.lower() == 'json':
                filename = f"export_{timestamp}.json"
                filepath = os.path.join(self.data_dir, filename)
                recent_df.to_json(filepath, orient='records', date_format='iso')
            else:
                filename = f"export_{timestamp}.csv"
                filepath = os.path.join(self.data_dir, filename)
                recent_df.to_csv(filepath, index=False)
            
            logger.info(f"Exported data to: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to export data: {e}")
            return ""
    
    def cleanup_old_data(self, days: int = 90):
        """
        Clean up data older than specified days
        
        Args:
            days: Keep data newer than this many days
        """
        try:
            import pandas as pd
            
            # Read CSV data
            df = pd.read_csv(self.csv_file)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Filter recent data
            cutoff_date = datetime.now() - pd.Timedelta(days=days)
            recent_df = df[df['timestamp'] >= cutoff_date]
            
            # Backup old data before cleanup
            if len(df) > len(recent_df):
                backup_file = os.path.join(self.data_dir, f"backup_{datetime.now().strftime('%Y%m%d')}.csv")
                df.to_csv(backup_file, index=False)
                logger.info(f"Created backup: {backup_file}")
            
            # Write cleaned data
            recent_df.to_csv(self.csv_file, index=False)
            
            logger.info(f"Cleaned up data older than {days} days. Kept {len(recent_df)} records.")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")

# Example usage
if __name__ == "__main__":
    logger = DataLogger()
    
    # Log some sample operations
    logger.log_operation(
        mode="auto",
        objects_detected=1,
        grab_success=True,
        distance_cm=15.5,
        servo_angles=[90, 45, 120, 90, 180],
        gripper_state="closed",
        detection_data={
            'confidence': 0.85,
            'class_name': 'bottle',
            'relative_position': [0.6, 0.4]
        },
        execution_time_ms=2500.0
    )
    
    # Get statistics
    stats = logger.get_statistics(days=7)
    print("Statistics:", json.dumps(stats, indent=2))
