# Smart Robotic Arm with Vision Tracking

A comprehensive robotic arm system with computer vision capabilities, designed for Raspberry Pi 5 with both automatic and manual control via web dashboard.

## 🚀 Features

- **Vision Tracking**: Real-time object detection using YOLO/OpenCV
- **Dual Control Modes**: Automatic vision-based control and manual web interface
- **Web Dashboard**: Real-time monitoring and control interface with dark/light themes
- **Data Logging**: CSV-based data collection and analysis with Jupyter notebooks
- **MQTT Communication**: Wireless control and status updates
- **Hybrid Architecture**: C++ for real-time hardware control, Python for AI processing
- **WebSocket Support**: Real-time dashboard updates and notifications
- **Mobile Responsive**: Dashboard works on tablets and mobile devices

## 📋 Hardware Requirements

### Essential Components
- **Raspberry Pi 5** (4GB+ RAM recommended)
- **5x Servo Motors** (SG90 or MG996R for higher torque)
- **Ultrasonic Sensor** (HC-SR04)
- **Motor Driver Module** (L298N or similar)
- **Camera Module** (Pi Camera v3 or USB webcam)

### Additional Components
- **Power Supply**: 5V 4A for Pi + 6V 2A for servos
- **Breadboard** or custom PCB
- **Jumper Wires** (male-to-male, male-to-female)
- **Servo Brackets** and mounting hardware
- **MicroSD Card** (32GB+ Class 10)

### Optional Enhancements
- **Gripper Mechanism** (custom 3D printed or commercial)
- **LED Status Indicators**
- **Buzzer** for audio feedback
- **External MQTT Broker** (for remote access)

## 🔧 Hardware Setup

### Pin Configuration (GPIO BCM)
\`\`\`
Servo Motors:
- Base Servo:     GPIO 18
- Shoulder Servo: GPIO 19  
- Elbow Servo:    GPIO 20
- Wrist Servo:    GPIO 21
- Gripper Servo:  GPIO 22

Ultrasonic Sensor:
- Trigger Pin:    GPIO 23
- Echo Pin:       GPIO 24

Motor Driver:
- PWM Pin:        GPIO 12
- Direction 1:    GPIO 16
- Direction 2:    GPIO 26

Camera:
- CSI Port (Pi Camera) or USB Port
\`\`\`

### Wiring Diagram
\`\`\`
Pi 5 GPIO Layout:
┌─────────────────────────────────┐
│  3V3  5V  │  5V  GND │  GPIO... │
│  GPIO 2   │  GPIO 3  │  GPIO... │
│  ...      │  ...     │  ...     │
└─────────────────────────────────┘

Connect servos to 6V external power supply
Connect sensor VCC to 5V, GND to GND
Use level shifters for 3.3V GPIO protection
\`\`\`

## ⚡ Quick Start

### 1. System Preparation
\`\`\`bash
# Update Raspberry Pi OS
sudo apt update && sudo apt upgrade -y

# Enable camera and I2C
sudo raspi-config
# Navigate to Interface Options > Camera > Enable
# Navigate to Interface Options > I2C > Enable
\`\`\`

### 2. Automated Installation
\`\`\`bash
# Clone or download the project
git clone <repository-url>
cd SmartArm-Vision

# Make setup script executable and run
chmod +x setup.sh
./setup.sh

# Reboot after installation
sudo reboot
\`\`\`

### 3. Manual Installation (Alternative)
\`\`\`bash
# Install system dependencies
sudo apt install -y cmake build-essential pkg-config wiringpi
sudo apt install -y python3 python3-pip python3-venv
sudo apt install -y libopencv-dev python3-opencv
sudo apt install -y mosquitto mosquitto-clients

# Build C++ components
mkdir build && cd build
cmake ..
make -j4
cd ..

# Setup Python environment
cd "Backend python"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
cd ..
\`\`\`

### 4. Configuration
\`\`\`bash
# Edit hardware configuration
nano include/config.h

# Test hardware connections
./build/SmartArm-Vision --test

# Configure MQTT broker (optional)
sudo nano /etc/mosquitto/mosquitto.conf
\`\`\`

### 5. Running the System
\`\`\`bash
# Terminal 1: Start C++ hardware controller
./build/SmartArm-Vision

# Terminal 2: Start Python backend
cd "Backend python"
source venv/bin/activate
python main.py

# Terminal 3: Open web dashboard
# Navigate to http://localhost:5000 in browser
# Or open dashboard/index.html directly
\`\`\`

## 📁 Project Structure

\`\`\`
SmartArm-Vision/
├── 📁 src/                     # C++ hardware control
│   ├── main.cpp               # Main control loop
│   ├── servo_control.cpp      # Servo motor control
│   ├── sensor_ultrasonic.cpp  # Distance sensing
│   └── driver_motor.cpp       # Motor driver control
├── 📁 include/                # C++ headers
│   └── config.h              # Hardware configuration
├── 📁 Backend python/         # Python AI & web backend
│   ├── main.py               # Flask web server
│   ├── vision_tracking.py    # YOLO object detection
│   ├── data_logger.py        # CSV data logging
│   ├── analysis.ipynb        # Jupyter analysis
│   └── requirements.txt      # Python dependencies
├── 📁 dashboard/              # Web interface
│   ├── index.html            # Main dashboard
│   ├── page.js               # Dashboard logic
│   ├── style.css             # Styling
│   └── assets/               # Images and icons
├── 📁 data/                   # Datasets & logs
│   ├── dataset.csv           # Operation logs
│   └── images/               # Captured images
├── 📁 docs/                   # Documentation
│   ├── API.md                # API documentation
│   ├── HARDWARE.md           # Hardware guide
│   ├── TROUBLESHOOTING.md    # Common issues
│   └── README.zh-en.md       # English documentation
├── 📁 scripts/                # Utility scripts
│   ├── backup.sh             # Data backup
│   ├── monitor.sh            # System monitoring
│   └── update.sh             # System updates
├── CMakeLists.txt             # C++ build configuration
├── setup.sh                  # Installation script
├── README.md                 # This file
└── LICENSE                   # MIT license
\`\`\`

## 🎮 Usage Guide

### Web Dashboard
1. **Access**: Open `http://localhost:5000` in your browser
2. **Mode Selection**: Toggle between Automatic and Manual modes
3. **Manual Control**: Use sliders for servo control or arrow keys
4. **Monitoring**: View real-time statistics and system status
5. **Data Analysis**: Check performance charts and event logs

### Control Modes

#### Automatic Mode
- System detects objects using computer vision
- Automatically moves arm to grab detected objects
- Logs all operations for analysis
- Provides real-time feedback via dashboard

#### Manual Mode
- Direct servo control via web interface
- Keyboard shortcuts for quick movements
- Emergency stop functionality
- Real-time position feedback

### Keyboard Shortcuts (Manual Mode)
- `↑↓←→`: Direction control
- `Space`: Grab/Release
- `Esc`: Emergency stop
- `H`: Home position
- `M`: Toggle mode

## 🔧 Configuration

### Hardware Configuration (`include/config.h`)
\`\`\`cpp
// Servo pin assignments
#define SERVO_BASE_PIN 18
#define SERVO_SHOULDER_PIN 19
// ... other pins

// Movement limits
#define MAX_SERVO_ANGLE 180
#define MIN_SERVO_ANGLE 0

// Detection parameters
#define DETECTION_CONFIDENCE 0.5
\`\`\`

### Python Configuration (`Backend python/.env`)
\`\`\`bash
# Camera settings
CAMERA_WIDTH=640
CAMERA_HEIGHT=480

# MQTT settings
MQTT_BROKER=localhost
MQTT_PORT=1883

# Web server settings
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
\`\`\`

## 📊 Data Analysis

### Jupyter Notebook
\`\`\`bash
cd "Backend python"
source venv/bin/activate
jupyter notebook analysis.ipynb
\`\`\`

### Available Analytics
- Success rate analysis
- Servo movement patterns
- Object detection statistics
- Performance optimization insights
- Machine learning predictions

### Data Export
- CSV format for spreadsheet analysis
- JSON format for web applications
- Automated backup and cleanup

## 🌐 API Documentation

### REST Endpoints
- `GET /api/status` - System status
- `POST /api/control` - Send commands
- `GET /api/statistics` - Performance data
- `GET /api/detections` - Current detections

### WebSocket Events
- `status` - Real-time system updates
- `detections` - Object detection events
- `events` - System event notifications

### MQTT Topics
- `smartarm/control` - Command input
- `smartarm/status` - Status updates
- `smartarm/data` - Data logging

## 🔍 Troubleshooting

### Common Issues

#### Hardware Not Detected
\`\`\`bash
# Check GPIO permissions
sudo usermod -a -G gpio $USER
sudo reboot

# Test individual components
./build/SmartArm-Vision --test-servos
./build/SmartArm-Vision --test-sensor
\`\`\`

#### Camera Issues
\`\`\`bash
# Check camera connection
vcgencmd get_camera

# Test camera
libcamera-hello --timeout 5000

# Python camera test
python3 -c "import cv2; print(cv2.VideoCapture(0).read())"
\`\`\`

#### MQTT Connection Failed
\`\`\`bash
# Check MQTT broker status
sudo systemctl status mosquitto

# Test MQTT connection
mosquitto_pub -h localhost -t test -m "hello"
mosquitto_sub -h localhost -t test
\`\`\`

#### Web Dashboard Not Loading
\`\`\`bash
# Check Python backend
cd "Backend python"
python main.py --debug

# Check port availability
netstat -tulpn | grep :5000

# Browser console for JavaScript errors
\`\`\`

### Performance Optimization
- Use faster SD card (Class 10 or better)
- Increase GPU memory split: `gpu_mem=128`
- Disable unnecessary services
- Use external power for servos
- Optimize camera resolution for performance

## 🤝 Contributing

### Development Setup
\`\`\`bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Code formatting
black Backend\ python/
clang-format -i src/*.cpp include/*.h
\`\`\`

### Code Style
- C++: Follow Google C++ Style Guide
- Python: Follow PEP 8 with Black formatting
- JavaScript: Follow Airbnb JavaScript Style Guide

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenCV community for computer vision tools
- YOLO developers for object detection
- Raspberry Pi Foundation
- Chart.js for data visualization
- MQTT.js for real-time communication

## 📞 Support

- **Documentation**: Check `docs/` folder for detailed guides
- **Issues**: Report bugs via GitHub issues
- **Discussions**: Join community discussions
- **Email**: Contact maintainers for urgent issues

## 🔄 Version History

- **v1.0.0**: Initial release with basic functionality
- **v1.1.0**: Added web dashboard and MQTT support
- **v1.2.0**: Enhanced vision tracking and data analysis
- **v1.3.0**: Mobile responsive design and keyboard controls

---

**Made with ❤️ for the robotics community**
