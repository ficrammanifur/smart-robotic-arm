# Smart Robotic Arm API Documentation

## Overview

The Smart Robotic Arm provides a comprehensive REST API and WebSocket interface for controlling and monitoring the robotic system. This document details all available endpoints, message formats, and usage examples.

## Base URL

\`\`\`
http://localhost:5000/api
\`\`\`

## Authentication

Currently, the API does not require authentication. For production deployments, consider implementing API keys or OAuth2.

## REST API Endpoints

### System Status

#### Get System Status
\`\`\`http
GET /api/status
\`\`\`

**Response:**
\`\`\`json
{
  "mode": "auto",
  "vision_active": true,
  "mqtt_connected": true,
  "last_detection": {
    "timestamp": "2024-01-01T10:00:00Z",
    "count": 1,
    "objects": [
      {
        "class_name": "bottle",
        "confidence": 0.85,
        "bbox": [100, 100, 200, 200],
        "center": [150, 150]
      }
    ]
  },
  "servo_angles": [90, 45, 120, 90, 180],
  "distance_cm": 15.5,
  "motor_speed": 0,
  "grab_count": 5,
  "error_message": ""
}
\`\`\`

### Control Commands

#### Send Control Command
\`\`\`http
POST /api/control
Content-Type: application/json
\`\`\`

**Request Body:**
\`\`\`json
{
  "command": "set_mode",
  "mode": "manual"
}
\`\`\`

**Available Commands:**

##### Set Mode
\`\`\`json
{
  "command": "set_mode",
  "mode": "auto|manual"
}
\`\`\`

##### Manual Servo Control
\`\`\`json
{
  "command": "manual_servo",
  "servo_id": 0,
  "angle": 90
}
\`\`\`

##### Manual Motor Control
\`\`\`json
{
  "command": "manual_motor",
  "speed": 50
}
\`\`\`

##### Emergency Stop
\`\`\`json
{
  "command": "emergency_stop"
}
\`\`\`

##### Home Position
\`\`\`json
{
  "command": "home_position"
}
\`\`\`

**Response:**
\`\`\`json
{
  "success": true,
  "message": "Command executed successfully"
}
\`\`\`

### Statistics

#### Get Performance Statistics
\`\`\`http
GET /api/statistics?days=7
\`\`\`

**Parameters:**
- `days` (optional): Number of days to analyze (default: 7)

**Response:**
\`\`\`json
{
  "total_operations": 150,
  "successful_grabs": 120,
  "success_rate": 80.0,
  "auto_mode_operations": 100,
  "manual_mode_operations": 50,
  "total_objects_detected": 200,
  "average_distance": 18.5,
  "average_execution_time": 2500.0,
  "most_detected_object": "bottle",
  "daily_operations": {
    "2024-01-01": 25,
    "2024-01-02": 30,
    "2024-01-03": 20
  }
}
\`\`\`

### Vision System

#### Get Current Detections
\`\`\`http
GET /api/detections
\`\`\`

**Response:**
\`\`\`json
{
  "detections": [
    {
      "id": 0,
      "class_id": 39,
      "class_name": "bottle",
      "confidence": 0.85,
      "bbox": [100, 100, 200, 200],
      "center": [150, 150],
      "relative_position": [0.6, 0.4],
      "size": [100, 100],
      "timestamp": 1704110400.0
    }
  ]
}
\`\`\`

#### Get Camera Frame
\`\`\`http
GET /api/camera/frame
\`\`\`

**Response:**
\`\`\`json
{
  "frame": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
}
\`\`\`

## WebSocket API

### Connection

Connect to WebSocket endpoint:
\`\`\`
ws://localhost:8765
\`\`\`

### Message Format

All WebSocket messages follow this format:
\`\`\`json
{
  "type": "message_type",
  "data": { ... }
}
\`\`\`

### Incoming Messages (Server to Client)

#### Status Updates
\`\`\`json
{
  "type": "status",
  "data": {
    "mode": "auto",
    "vision_active": true,
    "mqtt_connected": true,
    "servo_angles": [90, 45, 120, 90, 180],
    "distance_cm": 15.5,
    "motor_speed": 0
  }
}
\`\`\`

#### Detection Events
\`\`\`json
{
  "type": "detections",
  "data": [
    {
      "class_name": "bottle",
      "confidence": 0.85,
      "bbox": [100, 100, 200, 200],
      "center": [150, 150]
    }
  ]
}
\`\`\`

#### System Events
\`\`\`json
{
  "type": "event",
  "data": {
    "message": "Object detected: bottle",
    "level": "info",
    "timestamp": "2024-01-01T10:00:00Z"
  }
}
\`\`\`

### Outgoing Messages (Client to Server)

#### Command Messages
\`\`\`json
{
  "type": "command",
  "data": {
    "command": "set_mode",
    "mode": "manual"
  }
}
\`\`\`

## MQTT Topics

### Control Topic
**Topic:** `smartarm/control`

**Message Format:** Plain text commands
\`\`\`
MODE AUTO
MODE MANUAL
SERVO 0 90
MOTOR 50
STOP
HOME
\`\`\`

### Status Topic
**Topic:** `smartarm/status`

**Message Format:** JSON
\`\`\`json
{
  "mode": "auto",
  "distance": 15.5,
  "servos": [90, 45, 120, 90, 180],
  "motor_speed": 0
}
\`\`\`

### Data Topic
**Topic:** `smartarm/data`

**Message Format:** JSON
\`\`\`json
{
  "timestamp": "2024-01-01T10:00:00Z",
  "operation": "grab",
  "success": true,
  "object_detected": "bottle",
  "execution_time": 2500
}
\`\`\`

## Error Handling

### HTTP Status Codes
- `200 OK`: Request successful
- `400 Bad Request`: Invalid request format
- `404 Not Found`: Endpoint not found
- `500 Internal Server Error`: Server error

### Error Response Format
\`\`\`json
{
  "error": "Error description",
  "code": "ERROR_CODE",
  "details": {
    "field": "Additional error details"
  }
}
\`\`\`

### Common Error Codes
- `INVALID_COMMAND`: Unknown command type
- `INVALID_SERVO_ID`: Servo ID out of range
- `INVALID_ANGLE`: Angle out of valid range
- `SYSTEM_NOT_READY`: Hardware not initialized
- `MODE_MISMATCH`: Command not available in current mode

## Rate Limiting

- REST API: 100 requests per minute per IP
- WebSocket: No rate limiting
- MQTT: 10 messages per second per client

## Usage Examples

### Python Client Example
\`\`\`python
import requests
import json

# Get system status
response = requests.get('http://localhost:5000/api/status')
status = response.json()
print(f"Current mode: {status['mode']}")

# Set manual mode
control_data = {
    "command": "set_mode",
    "mode": "manual"
}
response = requests.post(
    'http://localhost:5000/api/control',
    json=control_data
)
print(f"Command result: {response.json()}")

# Move servo
servo_data = {
    "command": "manual_servo",
    "servo_id": 0,
    "angle": 45
}
response = requests.post(
    'http://localhost:5000/api/control',
    json=servo_data
)
\`\`\`

### JavaScript WebSocket Example
\`\`\`javascript
const ws = new WebSocket('ws://localhost:8765');

ws.onopen = function() {
    console.log('Connected to WebSocket');
};

ws.onmessage = function(event) {
    const message = JSON.parse(event.data);
    
    switch(message.type) {
        case 'status':
            console.log('Status update:', message.data);
            break;
        case 'detections':
            console.log('New detections:', message.data);
            break;
        case 'event':
            console.log('System event:', message.data.message);
            break;
    }
};

// Send command
const command = {
    type: 'command',
    data: {
        command: 'set_mode',
        mode: 'auto'
    }
};
ws.send(JSON.stringify(command));
\`\`\`

### MQTT Client Example
\`\`\`python
import paho.mqtt.client as mqtt
import json

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("smartarm/status")

def on_message(client, userdata, msg):
    status = json.loads(msg.payload.decode())
    print(f"Received status: {status}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)

# Send command
client.publish("smartarm/control", "MODE AUTO")

client.loop_forever()
\`\`\`

## SDK and Libraries

### Python SDK
\`\`\`python
from smartarm_sdk import SmartArmClient

client = SmartArmClient('http://localhost:5000')

# Get status
status = client.get_status()

# Set mode
client.set_mode('manual')

# Move servo
client.move_servo(0, 90)

# Get statistics
stats = client.get_statistics(days=7)
\`\`\`

### JavaScript SDK
\`\`\`javascript
import { SmartArmClient } from 'smartarm-js-sdk';

const client = new SmartArmClient('http://localhost:5000');

// Get status
const status = await client.getStatus();

// Set mode
await client.setMode('manual');

// Move servo
await client.moveServo(0, 90);

// WebSocket connection
client.onStatusUpdate((status) => {
    console.log('Status:', status);
});
\`\`\`

## Changelog

### v1.3.0
- Added camera frame endpoint
- Enhanced error handling
- WebSocket event improvements

### v1.2.0
- Added statistics endpoint
- MQTT topic documentation
- Rate limiting implementation

### v1.1.0
- WebSocket API introduction
- Enhanced status information
- Error code standardization

### v1.0.0
- Initial API release
- Basic control endpoints
- Status monitoring
