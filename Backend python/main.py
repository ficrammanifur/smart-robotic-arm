import asyncio
import json
import logging
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional

import paho.mqtt.client as mqtt
import websockets
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from vision_tracking import VisionTracker
from data_logger import DataLogger

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SmartArmBackend:
    def __init__(self):
        """Initialize Smart Arm Backend System"""
        self.vision_tracker = VisionTracker()
        self.data_logger = DataLogger()
        self.mqtt_client = None
        self.websocket_clients = set()
        
        # System state
        self.system_status = {
            'mode': 'auto',
            'vision_active': False,
            'mqtt_connected': False,
            'last_detection': None,
            'servo_angles': [90, 90, 90, 90, 90],
            'distance_cm': 0.0,
            'motor_speed': 0,
            'grab_count': 0,
            'error_message': ''
        }
        
        # Flask app setup
        self.app = Flask(__name__)
        CORS(self.app)
        self.setup_routes()
        
        # WebSocket server
        self.websocket_server = None
        
    def setup_routes(self):
        """Setup Flask API routes"""
        
        @self.app.route('/api/status', methods=['GET'])
        def get_status():
            """Get current system status"""
            return jsonify(self.system_status)
        
        @self.app.route('/api/control', methods=['POST'])
        def control_system():
            """Control system operations"""
            try:
                data = request.get_json()
                command = data.get('command')
                
                if command == 'set_mode':
                    mode = data.get('mode', 'auto')
                    self.set_mode(mode)
                    return jsonify({'success': True, 'mode': mode})
                
                elif command == 'manual_servo':
                    servo_id = data.get('servo_id')
                    angle = data.get('angle')
                    success = self.manual_servo_control(servo_id, angle)
                    return jsonify({'success': success})
                
                elif command == 'manual_motor':
                    speed = data.get('speed', 0)
                    success = self.manual_motor_control(speed)
                    return jsonify({'success': success})
                
                elif command == 'emergency_stop':
                    success = self.emergency_stop()
                    return jsonify({'success': success})
                
                elif command == 'home_position':
                    success = self.move_to_home()
                    return jsonify({'success': success})
                
                else:
                    return jsonify({'error': 'Unknown command'}), 400
                    
            except Exception as e:
                logger.error(f"Control API error: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/statistics', methods=['GET'])
        def get_statistics():
            """Get system statistics"""
            days = request.args.get('days', 7, type=int)
            stats = self.data_logger.get_statistics(days)
            return jsonify(stats)
        
        @self.app.route('/api/detections', methods=['GET'])
        def get_detections():
            """Get current vision detections"""
            detections = self.vision_tracker.get_detections()
            return jsonify({'detections': detections})
        
        @self.app.route('/api/camera/frame', methods=['GET'])
        def get_camera_frame():
            """Get current camera frame (base64 encoded)"""
            import cv2
            import base64
            
            frame = self.vision_tracker.get_annotated_frame()
            if frame is None:
                return jsonify({'error': 'No frame available'}), 404
            
            # Encode frame as JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            
            return jsonify({'frame': f"data:image/jpeg;base64,{frame_base64}"})
        
        @self.app.route('/dashboard/<path:filename>')
        def serve_dashboard(filename):
            """Serve dashboard files"""
            return send_from_directory('../dashboard', filename)
        
        @self.app.route('/')
        def serve_index():
            """Serve dashboard index"""
            return send_from_directory('../dashboard', 'index.html')
    
    def initialize(self) -> bool:
        """Initialize all backend systems"""
        logger.info("Initializing Smart Arm Backend...")
        
        # Initialize vision tracking
        if not self.vision_tracker.initialize():
            logger.error("Failed to initialize vision tracking")
            return False
        
        self.vision_tracker.set_detection_callback(self.on_vision_detection)
        
        # Initialize MQTT
        if not self.initialize_mqtt():
            logger.error("Failed to initialize MQTT")
            return False
        
        logger.info("Backend initialization completed successfully")
        return True
    
    def initialize_mqtt(self) -> bool:
        """Initialize MQTT client"""
        try:
            self.mqtt_client = mqtt.Client()
            self.mqtt_client.on_connect = self.on_mqtt_connect
            self.mqtt_client.on_message = self.on_mqtt_message
            self.mqtt_client.on_disconnect = self.on_mqtt_disconnect
            
            # Connect to MQTT broker
            self.mqtt_client.connect("localhost", 1883, 60)
            self.mqtt_client.loop_start()
            
            return True
            
        except Exception as e:
            logger.error(f"MQTT initialization failed: {e}")
            return False
    
    def on_mqtt_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            logger.info("Connected to MQTT broker")
            self.system_status['mqtt_connected'] = True
            
            # Subscribe to status updates from C++ controller
            client.subscribe("smartarm/status")
            
        else:
            logger.error(f"MQTT connection failed with code {rc}")
            self.system_status['mqtt_connected'] = False
    
    def on_mqtt_message(self, client, userdata, msg):
        """MQTT message callback"""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            
            if topic == "smartarm/status":
                # Update system status from C++ controller
                self.system_status.update({
                    'servo_angles': payload.get('servos', [90, 90, 90, 90, 90]),
                    'distance_cm': payload.get('distance', 0.0),
                    'motor_speed': payload.get('motor_speed', 0)
                })
                
                # Broadcast to WebSocket clients
                asyncio.create_task(self.broadcast_status())
                
        except Exception as e:
            logger.error(f"MQTT message processing error: {e}")
    
    def on_mqtt_disconnect(self, client, userdata, rc):
        """MQTT disconnect callback"""
        logger.warning("Disconnected from MQTT broker")
        self.system_status['mqtt_connected'] = False
    
    def on_vision_detection(self, detections: List[Dict]):
        """Vision detection callback"""
        self.system_status['last_detection'] = {
            'timestamp': datetime.now().isoformat(),
            'count': len(detections),
            'objects': detections
        }
        
        # Log detection event
        if detections:
            closest_obj = self.vision_tracker.find_closest_object()
            if closest_obj:
                self.data_logger.log_operation(
                    mode=self.system_status['mode'],
                    objects_detected=len(detections),
                    detection_data=closest_obj
                )
        
        # Broadcast to WebSocket clients
        asyncio.create_task(self.broadcast_detections(detections))
    
    def set_mode(self, mode: str):
        """Set system operation mode"""
        if mode in ['auto', 'manual']:
            self.system_status['mode'] = mode
            
            # Send mode change to C++ controller
            if self.mqtt_client:
                command = f"MODE {mode.upper()}"
                self.mqtt_client.publish("smartarm/control", command)
            
            logger.info(f"Mode changed to: {mode}")
    
    def manual_servo_control(self, servo_id: int, angle: int) -> bool:
        """Manual servo control"""
        if self.system_status['mode'] != 'manual':
            return False
        
        if self.mqtt_client:
            command = f"SERVO {servo_id} {angle}"
            self.mqtt_client.publish("smartarm/control", command)
            return True
        
        return False
    
    def manual_motor_control(self, speed: int) -> bool:
        """Manual motor control"""
        if self.system_status['mode'] != 'manual':
            return False
        
        if self.mqtt_client:
            command = f"MOTOR {speed}"
            self.mqtt_client.publish("smartarm/control", command)
            return True
        
        return False
    
    def emergency_stop(self) -> bool:
        """Emergency stop all operations"""
        if self.mqtt_client:
            self.mqtt_client.publish("smartarm/control", "STOP")
            return True
        return False
    
    def move_to_home(self) -> bool:
        """Move to home position"""
        if self.mqtt_client:
            self.mqtt_client.publish("smartarm/control", "HOME")
            return True
        return False
    
    async def websocket_handler(self, websocket, path):
        """WebSocket connection handler"""
        logger.info(f"WebSocket client connected: {websocket.remote_address}")
        self.websocket_clients.add(websocket)
        
        try:
            # Send initial status
            await websocket.send(json.dumps({
                'type': 'status',
                'data': self.system_status
            }))
            
            # Keep connection alive
            async for message in websocket:
                try:
                    data = json.loads(message)
                    # Handle WebSocket commands if needed
                    logger.info(f"WebSocket message: {data}")
                except json.JSONDecodeError:
                    logger.warning(f"Invalid WebSocket message: {message}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket client disconnected")
        finally:
            self.websocket_clients.discard(websocket)
    
    async def broadcast_status(self):
        """Broadcast status to all WebSocket clients"""
        if self.websocket_clients:
            message = json.dumps({
                'type': 'status',
                'data': self.system_status
            })
            
            # Send to all connected clients
            disconnected = set()
            for client in self.websocket_clients:
                try:
                    await client.send(message)
                except websockets.exceptions.ConnectionClosed:
                    disconnected.add(client)
            
            # Remove disconnected clients
            self.websocket_clients -= disconnected
    
    async def broadcast_detections(self, detections: List[Dict]):
        """Broadcast detections to all WebSocket clients"""
        if self.websocket_clients:
            message = json.dumps({
                'type': 'detections',
                'data': detections
            })
            
            disconnected = set()
            for client in self.websocket_clients:
                try:
                    await client.send(message)
                except websockets.exceptions.ConnectionClosed:
                    disconnected.add(client)
            
            self.websocket_clients -= disconnected
    
    def start_vision_tracking(self):
        """Start vision tracking system"""
        self.vision_tracker.start_tracking()
        self.system_status['vision_active'] = True
        logger.info("Vision tracking started")
    
    def stop_vision_tracking(self):
        """Stop vision tracking system"""
        self.vision_tracker.stop_tracking()
        self.system_status['vision_active'] = False
        logger.info("Vision tracking stopped")
    
    def run(self, host='0.0.0.0', port=5000, websocket_port=8765):
        """Run the backend server"""
        logger.info(f"Starting Smart Arm Backend on {host}:{port}")
        
        # Start vision tracking
        self.start_vision_tracking()
        
        # Start WebSocket server
        async def start_websocket_server():
            self.websocket_server = await websockets.serve(
                self.websocket_handler, host, websocket_port
            )
            logger.info(f"WebSocket server started on {host}:{websocket_port}")
        
        # Run WebSocket server in separate thread
        def run_websocket():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(start_websocket_server())
            loop.run_forever()
        
        websocket_thread = threading.Thread(target=run_websocket, daemon=True)
        websocket_thread.start()
        
        # Run Flask app
        try:
            self.app.run(host=host, port=port, debug=False, threaded=True)
        except KeyboardInterrupt:
            logger.info("Shutting down backend...")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up backend resources...")
        
        self.stop_vision_tracking()
        self.vision_tracker.cleanup()
        
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()

# Main entry point
if __name__ == "__main__":
    backend = SmartArmBackend()
    
    if backend.initialize():
        backend.run()
    else:
        logger.error("Failed to initialize backend")
