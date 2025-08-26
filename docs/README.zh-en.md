# Smart Robotic Arm with Vision Tracking - English Documentation

## Overview

The Smart Robotic Arm with Vision Tracking is an advanced robotics project designed for educational and research purposes. This system combines computer vision, real-time control, and web-based interfaces to create a comprehensive robotic arm solution.

## System Architecture

### Hardware Layer
- **Raspberry Pi 5**: Main computing unit
- **Servo Motors**: 5-axis movement control
- **Vision System**: Camera-based object detection
- **Sensors**: Ultrasonic distance measurement
- **Communication**: MQTT wireless protocol

### Software Layer
- **C++ Controller**: Real-time hardware control
- **Python Backend**: AI processing and web services
- **Web Dashboard**: User interface and monitoring
- **Data System**: Logging and analysis tools

## Technical Specifications

### Performance Metrics
- **Detection Accuracy**: >90% for common objects
- **Response Time**: <100ms for manual commands
- **Operating Range**: 50cm radius workspace
- **Precision**: ±2° servo positioning
- **Uptime**: 24/7 continuous operation

### Supported Objects
- Bottles and containers
- Fruits and vegetables
- Tools and utensils
- Custom trained objects
- Geometric shapes

### Communication Protocols
- **HTTP/REST**: Web API endpoints
- **WebSocket**: Real-time updates
- **MQTT**: IoT messaging
- **Serial**: Hardware communication

## Installation Guide

### Prerequisites
- Raspberry Pi 5 with 4GB+ RAM
- MicroSD card (32GB+ Class 10)
- Stable internet connection
- Basic electronics knowledge

### Step-by-Step Installation

#### 1. Prepare Raspberry Pi
```bash
# Flash Raspberry Pi OS (64-bit recommended)
# Enable SSH, Camera, and I2C in raspi-config
sudo raspi-config
```

#### 2. Hardware Assembly
- Connect servos to designated GPIO pins
- Install camera module
- Wire ultrasonic sensor
- Connect power supplies
- Test all connections

#### 3. Software Installation
```bash
# Download project
git "clone https://github.com/ficrammanifur/smart-robotic-arm"
cd SmartArm-Vision

# Run automated setup
chmod +x setup.sh
./setup.sh

# Reboot system
sudo reboot
```

#### 4. Configuration
```bash
# Edit hardware settings
nano include/config.h

# Configure network settings
nano Backend\ python/.env

# Test system components
./build/SmartArm-Vision --test
```

#### 5. First Run
```bash
# Start hardware controller
./build/SmartArm-Vision &

# Start web backend
cd "Backend python"
python main.py &

# Access dashboard
# Open http://localhost:5000 in browser
```

## User Manual

### Dashboard Interface

#### Main Sections
1. **Header**: Connection status and theme toggle
2. **Control Panel**: Mode selection and manual controls
3. **Monitoring**: Real-time system statistics
4. **Charts**: Performance analytics
5. **Event Log**: System activity history

#### Control Modes

##### Automatic Mode
- Enables computer vision detection
- Autonomous object grabbing
- Continuous operation
- Data logging active

##### Manual Mode
- Direct servo control
- Keyboard shortcuts
- Real-time feedback
- Emergency stop available

### Operation Procedures

#### Starting the System
1. Power on Raspberry Pi
2. Wait for boot completion
3. Run startup scripts
4. Access web dashboard
5. Select operation mode

#### Object Detection Setup
1. Position camera for optimal view
2. Ensure adequate lighting
3. Clear workspace of obstacles
4. Calibrate detection parameters
5. Test with sample objects

#### Manual Control
1. Switch to manual mode
2. Use sliders for precise control
3. Employ keyboard shortcuts for speed
4. Monitor servo positions
5. Use emergency stop if needed

#### Data Analysis
1. Access Jupyter notebook
2. Load operation data
3. Generate performance reports
4. Identify optimization opportunities
5. Export results

## Maintenance Guide

### Regular Maintenance
- **Daily**: Check system status and logs
- **Weekly**: Clean camera lens and sensors
- **Monthly**: Update software components
- **Quarterly**: Calibrate servo positions
- **Annually**: Replace worn components

### Backup Procedures
```bash
# Backup configuration
./scripts/backup.sh config

# Backup data
./scripts/backup.sh data

# Full system backup
./scripts/backup.sh full
```

### Update Procedures
```bash
# Update system packages
sudo apt update && sudo apt upgrade

# Update project code
git pull origin main

# Rebuild components
./scripts/update.sh
```

## Safety Guidelines

### Electrical Safety
- Use proper power supplies
- Check connections regularly
- Avoid water near electronics
- Use surge protection
- Ground all metal components

### Mechanical Safety
- Secure all moving parts
- Maintain safe distances
- Use emergency stop frequently
- Regular mechanical inspection
- Proper workspace setup

### Software Safety
- Regular security updates
- Strong passwords
- Network security
- Data backup
- Access control

## Troubleshooting

### Hardware Issues

#### Servo Not Moving
1. Check power supply voltage
2. Verify GPIO connections
3. Test servo individually
4. Check for mechanical binding
5. Replace if necessary

#### Camera Not Working
1. Check camera connection
2. Enable camera in raspi-config
3. Test with libcamera-hello
4. Verify permissions
5. Try different camera

#### Sensor Readings Incorrect
1. Check wiring connections
2. Verify power supply
3. Test sensor individually
4. Check for interference
5. Calibrate if needed

### Software Issues

#### Web Dashboard Not Loading
1. Check Python backend status
2. Verify port availability
3. Check browser console
4. Test network connectivity
5. Restart services

#### MQTT Connection Failed
1. Check broker status
2. Verify network settings
3. Test with MQTT client
4. Check firewall rules
5. Restart broker service

#### Vision Detection Poor
1. Improve lighting conditions
2. Clean camera lens
3. Adjust detection parameters
4. Retrain model if needed
5. Check camera focus

## Advanced Configuration

### Custom Object Training
```bash
# Prepare training data
python scripts/prepare_dataset.py

# Train custom model
python scripts/train_model.py --data custom_dataset

# Deploy trained model
cp custom_model.pt Backend\ python/models/
```

### Network Configuration
```bash
# Configure static IP
sudo nano /etc/dhcpcd.conf

# Setup port forwarding
sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 5000

# Configure firewall
sudo ufw allow 5000
sudo ufw allow 1883
```

### Performance Tuning
```bash
# Increase GPU memory
echo "gpu_mem=128" | sudo tee -a /boot/config.txt

# Optimize CPU governor
echo "performance" | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Disable unnecessary services
sudo systemctl disable bluetooth
sudo systemctl disable wifi-powersave
```

## API Reference

### REST API Endpoints

#### System Status
```http
GET /api/status
Response: {
  "mode": "auto|manual",
  "vision_active": boolean,
  "mqtt_connected": boolean,
  "servo_angles": [int, int, int, int, int],
  "distance_cm": float,
  "motor_speed": int
}
```

#### Control Commands
```http
POST /api/control
Body: {
  "command": "set_mode|manual_servo|emergency_stop",
  "mode": "auto|manual",
  "servo_id": int,
  "angle": int
}
```

#### Statistics
```http
GET /api/statistics?days=7
Response: {
  "total_operations": int,
  "success_rate": float,
  "daily_operations": object
}
```

### WebSocket Events

#### Status Updates
```javascript
{
  "type": "status",
  "data": {
    "mode": "auto",
    "servo_angles": [90, 90, 90, 90, 90],
    "distance_cm": 15.5
  }
}
```

#### Detection Events
```javascript
{
  "type": "detections",
  "data": [{
    "class_name": "bottle",
    "confidence": 0.85,
    "bbox": [100, 100, 200, 200]
  }]
}
```

## Development Guide

### Setting Up Development Environment
````bash
# Install development tools
sudo apt install -y git cmake gdb valgrind
pip install -r requirements-dev.txt

# Setup pre-commit hooks
pre-commit install

# Run tests
make test
python -m pytest
```

### Code Structure

#### C++ Components
- `main.cpp`: Main control loop and MQTT handling
- `servo_control.cpp`: Servo motor control class
- `sensor_ultrasonic.cpp`: Distance sensor interface
- `driver_motor.cpp`: Motor driver control

#### Python Components
- `main.py`: Flask web server and API
- `vision_tracking.py`: YOLO-based object detection
- `data_logger.py`: CSV data logging system
- `analysis.ipynb`: Data analysis notebook

#### Web Components
- `index.html`: Dashboard structure
- `page.js`: Dashboard logic and WebSocket handling
- `style.css`: Responsive styling with theme support

### Contributing Guidelines
1. Fork the repository
2. Create feature branch
3. Follow coding standards
4. Add tests for new features
5. Submit pull request

### Testing Procedures
```bash
# Unit tests
python -m pytest tests/unit/

# Integration tests
python -m pytest tests/integration/

# Hardware tests (requires hardware)
./build/SmartArm-Vision --test-all

# Web interface tests
npm test
```

## Frequently Asked Questions

### General Questions

**Q: What is the maximum payload the arm can handle?**
A: With SG90 servos, approximately 100-200g. Use MG996R servos for heavier loads up to 500g.

**Q: Can I use this project commercially?**
A: Yes, the MIT license allows commercial use with proper attribution.

**Q: What objects can be detected?**
A: The system uses YOLO which can detect 80+ common objects. Custom training is possible for specific objects.

### Technical Questions

**Q: Why use both C++ and Python?**
A: C++ provides real-time hardware control while Python offers rich AI libraries and web frameworks.

**Q: Can I run this on other single-board computers?**
A: Yes, but GPIO pin assignments and some libraries may need modification.

**Q: How accurate is the object detection?**
A: Typically >90% accuracy for common objects under good lighting conditions.

### Troubleshooting Questions

**Q: The arm moves erratically, what should I check?**
A: Check power supply stability, servo connections, and mechanical binding.

**Q: Web dashboard shows "disconnected" status?**
A: Verify MQTT broker is running and network connectivity between components.

**Q: Camera shows black image?**
A: Check camera connection, enable camera in raspi-config, and verify permissions.

## Resources and References

### Documentation
- [Raspberry Pi Official Documentation](https://www.raspberrypi.org/documentation/)
- [OpenCV Python Tutorials](https://docs.opencv.org/master/d6/d00/tutorial_py_root.html)
- [YOLO Object Detection](https://pjreddie.com/darknet/yolo/)
- [MQTT Protocol Specification](http://mqtt.org/)

### Hardware Suppliers
- [Adafruit](https://www.adafruit.com/) - Electronics components
- [SparkFun](https://www.sparkfun.com/) - Sensors and modules
- [Amazon](https://amazon.com/) - General components
- [AliExpress](https://aliexpress.com/) - Budget components

### Software Tools
- [Visual Studio Code](https://code.visualstudio.com/) - Code editor
- [Thonny](https://thonny.org/) - Python IDE for Raspberry Pi
- [Fritzing](https://fritzing.org/) - Circuit design
- [Fusion 360](https://www.autodesk.com/products/fusion-360/) - 3D modeling

### Community
- [Raspberry Pi Forums](https://www.raspberrypi.org/forums/)
- [Reddit r/raspberry_pi](https://www.reddit.com/r/raspberry_pi/)
- [Arduino Community](https://forum.arduino.cc/)
- [OpenCV Community](https://forum.opencv.org/)

---

This documentation provides comprehensive guidance for users of all skill levels, from beginners to advanced developers. For additional support, please refer to the troubleshooting section or contact the development team.
