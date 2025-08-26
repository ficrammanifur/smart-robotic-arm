# Hardware Setup Guide

## Overview

This guide provides detailed instructions for assembling and configuring the hardware components of the Smart Robotic Arm system.

## Component List

### Required Components

| Component | Quantity | Specifications | Estimated Cost |
|-----------|----------|----------------|----------------|
| Raspberry Pi 5 | 1 | 4GB RAM minimum | $75 |
| Servo Motors | 5 | SG90 or MG996R | $25-50 |
| Ultrasonic Sensor | 1 | HC-SR04 | $3 |
| Motor Driver | 1 | L298N or similar | $5 |
| Camera Module | 1 | Pi Camera v3 or USB | $25 |
| Power Supply (Pi) | 1 | 5V 4A USB-C | $15 |
| Power Supply (Servos) | 1 | 6V 2A DC | $10 |
| MicroSD Card | 1 | 32GB Class 10 | $10 |
| Breadboard | 1 | Half-size or larger | $5 |
| Jumper Wires | 1 set | Male-to-male, male-to-female | $5 |
| **Total** | | | **$178-203** |

### Optional Components

| Component | Purpose | Cost |
|-----------|---------|------|
| Servo Brackets | Mechanical assembly | $15 |
| Custom PCB | Clean wiring | $20 |
| LED Indicators | Status display | $3 |
| Buzzer | Audio feedback | $2 |
| Case/Enclosure | Protection | $25 |
| Heat Sinks | Cooling | $5 |

## Wiring Diagram

### GPIO Pin Assignment (BCM Numbering)

\`\`\`
Raspberry Pi 5 GPIO Layout:
     3V3  (1) (2)  5V
   GPIO2  (3) (4)  5V
   GPIO3  (5) (6)  GND
   GPIO4  (7) (8)  GPIO14
     GND  (9) (10) GPIO15
  GPIO17 (11) (12) GPIO18  ← Base Servo
  GPIO27 (13) (14) GND
  GPIO22 (15) (16) GPIO23  ← Ultrasonic Trigger
     3V3 (17) (18) GPIO24  ← Ultrasonic Echo
  GPIO10 (19) (20) GND
   GPIO9 (21) (22) GPIO25
  GPIO11 (23) (24) GPIO8
     GND (25) (26) GPIO7
   GPIO0 (27) (28) GPIO1
   GPIO5 (29) (30) GND
   GPIO6 (31) (32) GPIO12  ← Motor PWM
  GPIO13 (33) (34) GND
  GPIO19 (35) (36) GPIO16  ← Motor Dir1
  GPIO26 (37) (38) GPIO20  ← Elbow Servo
     GND (39) (40) GPIO21  ← Wrist Servo
\`\`\`

### Servo Connections

| Servo | GPIO Pin | Wire Colors |
|-------|----------|-------------|
| Base | GPIO 18 | Red(+6V), Brown(GND), Orange(Signal) |
| Shoulder | GPIO 19 | Red(+6V), Brown(GND), Orange(Signal) |
| Elbow | GPIO 20 | Red(+6V), Brown(GND), Orange(Signal) |
| Wrist | GPIO 21 | Red(+6V), Brown(GND), Orange(Signal) |
| Gripper | GPIO 22 | Red(+6V), Brown(GND), Orange(Signal) |

### Sensor Connections

#### Ultrasonic Sensor (HC-SR04)
| Sensor Pin | Pi GPIO | Wire Color |
|------------|---------|------------|
| VCC | 5V | Red |
| GND | GND | Black |
| Trig | GPIO 23 | Yellow |
| Echo | GPIO 24 | Green |

#### Motor Driver (L298N)
| Driver Pin | Pi GPIO | Purpose |
|------------|---------|---------|
| ENA | GPIO 12 | PWM Speed Control |
| IN1 | GPIO 16 | Direction 1 |
| IN2 | GPIO 26 | Direction 2 |
| VCC | 5V | Logic Power |
| GND | GND | Ground |

## Assembly Instructions

### Step 1: Prepare Raspberry Pi

1. **Flash SD Card**
   \`\`\`bash
   # Download Raspberry Pi Imager
   # Flash Raspberry Pi OS (64-bit) to SD card
   # Enable SSH, Camera, I2C in advanced options
   \`\`\`

2. **Initial Boot Setup**
   \`\`\`bash
   # Insert SD card and boot Pi
   # Complete initial setup wizard
   # Update system
   sudo apt update && sudo apt upgrade -y
   \`\`\`

3. **Enable Required Interfaces**
   \`\`\`bash
   sudo raspi-config
   # Interface Options > Camera > Enable
   # Interface Options > I2C > Enable
   # Interface Options > SPI > Enable (if needed)
   # Reboot when prompted
   \`\`\`

### Step 2: Power Supply Setup

1. **Servo Power Supply**
   - Use dedicated 6V 2A power supply for servos
   - Connect positive to servo red wires (via breadboard)
   - Connect negative to common ground with Pi
   - **Important**: Do not power servos from Pi's 5V rail

2. **Pi Power Supply**
   - Use official 5V 4A USB-C power supply
   - Ensure stable power delivery
   - Consider UPS for critical applications

### Step 3: Servo Assembly

1. **Mechanical Assembly**
   \`\`\`
   Base Servo (GPIO 18):
   - Mount horizontally as rotation base
   - Attach arm segments with servo horns
   - Ensure smooth rotation without binding
   
   Shoulder Servo (GPIO 19):
   - Mount vertically for up/down movement
   - Connect to base servo assembly
   - Test range of motion
   
   Elbow Servo (GPIO 20):
   - Mount at end of shoulder segment
   - Provides forward/backward reach
   - Check for mechanical interference
   
   Wrist Servo (GPIO 21):
   - Mount for end-effector orientation
   - Connect to elbow assembly
   - Verify smooth operation
   
   Gripper Servo (GPIO 22):
   - Mount at end of wrist
   - Connect to gripper mechanism
   - Test open/close operation
   \`\`\`

2. **Electrical Connections**
   \`\`\`
   For each servo:
   1. Connect red wire to +6V power rail
   2. Connect brown/black wire to ground rail
   3. Connect orange/yellow wire to assigned GPIO pin
   4. Use breadboard for clean connections
   \`\`\`

### Step 4: Sensor Installation

1. **Ultrasonic Sensor (HC-SR04)**
   \`\`\`
   Mounting:
   - Position for clear line of sight
   - Mount securely to avoid vibration
   - Angle slightly downward for object detection
   
   Wiring:
   - VCC to 5V (Pin 2 or 4)
   - GND to Ground (Pin 6, 9, 14, 20, 25, 30, 34, or 39)
   - Trig to GPIO 23 (Pin 16)
   - Echo to GPIO 24 (Pin 18)
   \`\`\`

2. **Camera Module**
   \`\`\`
   Pi Camera v3:
   - Connect ribbon cable to CSI port
   - Ensure cable is fully inserted
   - Lock connector by pushing down
   - Position camera for optimal view
   
   USB Camera:
   - Connect to USB 3.0 port for best performance
   - Verify compatibility with OpenCV
   - Test with v4l2-ctl --list-devices
   \`\`\`

### Step 5: Motor Driver (Optional)

1. **L298N Motor Driver**
   \`\`\`
   Connections:
   - VCC to 5V (logic power)
   - GND to Pi ground
   - ENA to GPIO 12 (PWM control)
   - IN1 to GPIO 16 (direction)
   - IN2 to GPIO 26 (direction)
   - Motor terminals to external motor
   - Motor power to separate 12V supply
   \`\`\`

### Step 6: Wiring Best Practices

1. **Use Proper Wire Gauge**
   - 22 AWG for signal wires
   - 18 AWG for power wires
   - Twisted pairs for long runs

2. **Color Coding**
   \`\`\`
   Red:    Positive power (+5V, +6V)
   Black:  Ground (GND)
   Yellow: Digital signals
   Green:  Analog signals
   Blue:   Communication (I2C, SPI)
   White:  Special functions
   \`\`\`

3. **Strain Relief**
   - Secure cables at connection points
   - Use cable ties for organization
   - Avoid sharp bends in wires

4. **Shielding**
   - Use shielded cables for long runs
   - Keep power and signal wires separated
   - Ground shield at one end only

## Testing and Calibration

### Step 1: Basic Hardware Test

\`\`\`bash
# Test GPIO functionality
gpio readall

# Test camera
libcamera-hello --timeout 5000

# Test I2C devices (if any)
i2cdetect -y 1
\`\`\`

### Step 2: Individual Component Tests

1. **Servo Test**
   \`\`\`bash
   # Build and run hardware test
   cd SmartArm-Vision
   mkdir build && cd build
   cmake ..
   make
   ./SmartArm-Vision --test-servos
   \`\`\`

2. **Sensor Test**
   \`\`\`bash
   # Test ultrasonic sensor
   ./SmartArm-Vision --test-sensor
   
   # Expected output: Distance readings in cm
   \`\`\`

3. **Camera Test**
   \`\`\`bash
   # Test camera capture
   python3 -c "
   import cv2
   cap = cv2.VideoCapture(0)
   ret, frame = cap.read()
   print(f'Camera test: {ret}, Frame shape: {frame.shape if ret else None}')
   cap.release()
   "
   \`\`\`

### Step 3: System Integration Test

\`\`\`bash
# Run full system test
./SmartArm-Vision --test-all

# Expected output:
# ✓ Servo control initialized
# ✓ Ultrasonic sensor initialized  
# ✓ Camera initialized
# ✓ MQTT connection established
# ✓ All systems operational
\`\`\`

### Step 4: Calibration

1. **Servo Calibration**
   \`\`\`bash
   # Run calibration routine
   ./SmartArm-Vision --calibrate-servos
   
   # Follow on-screen instructions to:
   # - Set minimum positions
   # - Set maximum positions  
   # - Set home position
   # - Test full range of motion
   \`\`\`

2. **Camera Calibration**
   \`\`\`bash
   # Calibrate camera position and focus
   python3 Backend\ python/vision_tracking.py --calibrate
   
   # Adjust camera:
   # - Focus for sharp images
   # - Position for optimal view
   # - Lighting for good contrast
   \`\`\`

3. **Workspace Calibration**
   \`\`\`bash
   # Define workspace boundaries
   ./SmartArm-Vision --calibrate-workspace
   
   # Mark safe operating area
   # Set object detection zones
   # Configure collision avoidance
   \`\`\`

## Troubleshooting

### Common Hardware Issues

#### Servos Not Moving
**Symptoms:** Servos don't respond to commands
**Causes & Solutions:**
1. **Power Supply Issues**
   - Check 6V supply voltage with multimeter
   - Verify current capacity (2A minimum)
   - Ensure stable power under load

2. **Wiring Problems**
   - Verify GPIO pin connections
   - Check for loose connections
   - Test continuity with multimeter

3. **Software Configuration**
   - Verify pin assignments in config.h
   - Check servo library initialization
   - Test with simple servo sweep program

#### Erratic Servo Movement
**Symptoms:** Servos move unpredictably or jitter
**Causes & Solutions:**
1. **Power Supply Noise**
   - Add capacitors (1000µF) across power rails
   - Use separate power supplies for Pi and servos
   - Check for voltage drops under load

2. **Mechanical Binding**
   - Check for physical obstructions
   - Lubricate moving parts
   - Verify proper assembly alignment

3. **Signal Interference**
   - Use shielded cables for servo signals
   - Keep power and signal wires separated
   - Add ferrite cores on long cable runs

#### Sensor Reading Issues
**Symptoms:** Incorrect or no distance readings
**Causes & Solutions:**
1. **Wiring Verification**
   - Check VCC connection to 5V
   - Verify trigger and echo pin assignments
   - Test with oscilloscope if available

2. **Environmental Factors**
   - Ensure clear line of sight
   - Check for acoustic interference
   - Verify mounting stability

3. **Software Timing**
   - Adjust timeout values in code
   - Check for timing conflicts with other operations
   - Use hardware timers for precision

#### Camera Problems
**Symptoms:** No image or poor quality
**Causes & Solutions:**
1. **Connection Issues**
   - Reseat ribbon cable connections
   - Check for damaged cables
   - Verify camera is detected: `vcgencmd get_camera`

2. **Configuration Problems**
   - Enable camera in raspi-config
   - Check camera permissions
   - Verify OpenCV installation

3. **Image Quality**
   - Adjust focus manually
   - Improve lighting conditions
   - Clean camera lens

### Performance Optimization

#### Reduce Latency
1. **System Configuration**
   \`\`\`bash
   # Increase GPU memory
   echo "gpu_mem=128" | sudo tee -a /boot/config.txt
   
   # Set CPU governor to performance
   echo "performance" | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
   \`\`\`

2. **Real-time Scheduling**
   \`\`\`bash
   # Run control loop with higher priority
   sudo chrt -f 50 ./SmartArm-Vision
   \`\`\`

#### Improve Reliability
1. **Watchdog Timer**
   \`\`\`bash
   # Enable hardware watchdog
   echo "dtparam=watchdog=on" | sudo tee -a /boot/config.txt
   \`\`\`

2. **Automatic Recovery**
   \`\`\`bash
   # Create systemd service for auto-restart
   sudo systemctl enable smartarm.service
   \`\`\`

## Maintenance Schedule

### Daily Checks
- Visual inspection of connections
- Check system logs for errors
- Verify smooth servo operation
- Clean camera lens if needed

### Weekly Maintenance
- Check power supply voltages
- Inspect mechanical components
- Update system logs
- Backup configuration files

### Monthly Service
- Deep clean all components
- Check for loose connections
- Calibrate sensors
- Update software components

### Quarterly Overhaul
- Replace worn mechanical parts
- Check servo performance
- Update system firmware
- Performance optimization review

## Safety Considerations

### Electrical Safety
- Always disconnect power before wiring changes
- Use proper fuses and circuit protection
- Verify polarity before connecting components
- Keep liquids away from electronics

### Mechanical Safety
- Secure all moving parts properly
- Use emergency stop functionality
- Maintain safe distances during operation
- Regular inspection of mechanical wear

### Software Safety
- Implement position limits in software
- Use watchdog timers for fault detection
- Regular backup of configuration
- Monitor system health continuously

This hardware guide provides the foundation for building a reliable and safe robotic arm system. Follow all safety procedures and take time to properly test each component before integration.
