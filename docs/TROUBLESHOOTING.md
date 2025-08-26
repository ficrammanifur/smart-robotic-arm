# Troubleshooting Guide

## Overview

This guide helps diagnose and resolve common issues with the Smart Robotic Arm system. Issues are organized by category with step-by-step solutions.

## Quick Diagnostic Checklist

Before diving into specific issues, run this quick diagnostic:

```bash
# System health check
./scripts/health_check.sh

# Hardware test
./build/SmartArm-Vision --test-all

# Network connectivity
ping localhost
curl http://localhost:5000/api/status

# Service status
systemctl status mosquitto
ps aux | grep python
```

## Hardware Issues

### Servo Motor Problems

#### Issue: Servos Not Moving
**Symptoms:**
- No servo movement when commands sent
- Servos feel loose or floppy
- No response to manual controls

**Diagnostic Steps:**
```bash
# Test individual servo
./build/SmartArm-Vision --test-servo 0

# Check GPIO status
gpio readall | grep -E "(18|19|20|21|22)"

# Verify power supply
# Use multimeter to check 6V rail
```

**Solutions:**
1. **Power Supply Check**
   ```bash
   # Measure voltage at servo power rail
   # Should read 6V ±0.5V under load
   # Check current capacity (2A minimum)
   ```

2. **Wiring Verification**
   ```bash
   # Check connections:
   # Red wire → +6V power rail
   # Brown/Black wire → Ground rail  
   # Orange/Yellow wire → GPIO pin
   ```

3. **Software Configuration**
   ```bash
   # Verify pin assignments in config.h
   grep -n "SERVO.*PIN" include/config.h
   
   # Rebuild if changes made
   cd build && make
   ```

#### Issue: Erratic Servo Movement
**Symptoms:**
- Servos jitter or move unpredictably
- Inconsistent positioning
- Servo overheating

**Solutions:**
1. **Power Supply Stabilization**
   ```bash
   # Add capacitors to power rails
   # 1000µF across +6V and GND
   # 100µF ceramic capacitors near each servo
   ```

2. **Mechanical Inspection**
   ```bash
   # Check for binding or obstruction
   # Lubricate moving parts with light oil
   # Verify proper servo horn attachment
   ```

3. **Signal Quality**
   ```bash
   # Use shielded cables for long runs
   # Keep power and signal wires separated
   # Add ferrite cores to reduce interference
   ```

### Sensor Issues

#### Issue: Ultrasonic Sensor Not Working
**Symptoms:**
- Distance readings always 0 or -1
- No response from sensor
- Inconsistent measurements

**Diagnostic Steps:**
```bash
# Test sensor directly
./build/SmartArm-Vision --test-sensor

# Check wiring with multimeter
# VCC should read 5V
# Trigger and Echo pins should toggle
```

**Solutions:**
1. **Wiring Check**
   ```bash
   # Verify connections:
   # VCC → 5V (Pin 2 or 4)
   # GND → Ground (Pin 6, 9, 14, etc.)
   # Trig → GPIO 23 (Pin 16)
   # Echo → GPIO 24 (Pin 18)
   ```

2. **Environmental Factors**
   ```bash
   # Ensure clear line of sight
   # Remove acoustic absorbing materials
   # Check for vibration affecting sensor
   ```

3. **Software Timing**
   ```cpp
   // Adjust timeout values in sensor_ultrasonic.cpp
   // Increase delay between measurements
   // Check for timing conflicts
   ```

#### Issue: Camera Not Working
**Symptoms:**
- Black screen or no image
- "Camera not detected" errors
- Poor image quality

**Diagnostic Steps:**
```bash
# Check camera detection
vcgencmd get_camera

# Test with system tools
libcamera-hello --timeout 5000

# Python test
python3 -c "import cv2; print(cv2.VideoCapture(0).read())"
```

**Solutions:**
1. **Hardware Connection**
   ```bash
   # For Pi Camera:
   # - Reseat ribbon cable in CSI port
   # - Ensure cable lock is engaged
   # - Check for cable damage
   
   # For USB Camera:
   # - Try different USB port
   # - Check USB power requirements
   # - Test with different cable
   ```

2. **Software Configuration**
   ```bash
   # Enable camera interface
   sudo raspi-config
   # Interface Options → Camera → Enable
   
   # Check camera permissions
   sudo usermod -a -G video $USER
   
   # Reboot after changes
   sudo reboot
   ```

3. **Image Quality Issues**
   ```bash
   # Adjust camera settings in vision_tracking.py
   # Improve lighting conditions
   # Clean camera lens
   # Adjust focus (if manual focus camera)
   ```

## Software Issues

### System Startup Problems

#### Issue: C++ Controller Won't Start
**Symptoms:**
- "Permission denied" errors
- "Failed to initialize wiringPi" messages
- Segmentation faults

**Solutions:**
1. **Permission Issues**
   ```bash
   # Add user to gpio group
   sudo usermod -a -G gpio $USER
   
   # Set executable permissions
   chmod +x build/SmartArm-Vision
   
   # Reboot to apply group changes
   sudo reboot
   ```

2. **Library Dependencies**
   ```bash
   # Install missing libraries
   sudo apt install -y wiringpi libwiringpi-dev
   
   # Rebuild project
   cd build
   make clean
   cmake ..
   make
   ```

3. **Hardware Initialization**
   ```bash
   # Check if another process is using GPIO
   sudo lsof /dev/gpiomem
   
   # Kill conflicting processes
   sudo pkill -f SmartArm-Vision
   ```

#### Issue: Python Backend Fails to Start
**Symptoms:**
- Import errors for Python modules
- "Port already in use" errors
- Flask application crashes

**Solutions:**
1. **Python Dependencies**
   ```bash
   cd "Backend python"
   
   # Activate virtual environment
   source venv/bin/activate
   
   # Install/update requirements
   pip install -r requirements.txt
   
   # Check for conflicts
   pip check
   ```

2. **Port Conflicts**
   ```bash
   # Check what's using port 5000
   sudo netstat -tulpn | grep :5000
   
   # Kill process using port
   sudo kill -9 <PID>
   
   # Or change port in main.py
   app.run(host='0.0.0.0', port=5001)
   ```

3. **Environment Variables**
   ```bash
   # Create .env file if missing
   cat > "Backend python/.env" << EOF
   FLASK_ENV=production
   CAMERA_WIDTH=640
   CAMERA_HEIGHT=480
   MQTT_BROKER=localhost
   MQTT_PORT=1883
   EOF
   ```

### Communication Issues

#### Issue: MQTT Connection Failed
**Symptoms:**
- "Connection refused" errors
- Dashboard shows "Disconnected"
- No communication between components

**Diagnostic Steps:**
```bash
# Check MQTT broker status
sudo systemctl status mosquitto

# Test MQTT connectivity
mosquitto_pub -h localhost -t test -m "hello"
mosquitto_sub -h localhost -t test

# Check network connectivity
ping localhost
telnet localhost 1883
```

**Solutions:**
1. **MQTT Broker Issues**
   ```bash
   # Start MQTT broker
   sudo systemctl start mosquitto
   sudo systemctl enable mosquitto
   
   # Check broker configuration
   sudo nano /etc/mosquitto/mosquitto.conf
   
   # Restart broker
   sudo systemctl restart mosquitto
   ```

2. **Firewall Issues**
   ```bash
   # Allow MQTT port
   sudo ufw allow 1883
   
   # Check iptables rules
   sudo iptables -L
   
   # Disable firewall temporarily for testing
   sudo ufw disable
   ```

3. **Network Configuration**
   ```bash
   # Check network interfaces
   ip addr show
   
   # Test localhost resolution
   nslookup localhost
   
   # Check for network conflicts
   netstat -rn
   ```

#### Issue: WebSocket Connection Problems
**Symptoms:**
- Dashboard shows connection errors
- Real-time updates not working
- WebSocket connection drops frequently

**Solutions:**
1. **WebSocket Server Issues**
   ```bash
   # Check if WebSocket server is running
   netstat -tulpn | grep :8765
   
   # Test WebSocket connection
   python3 -c "
   import websockets
   import asyncio
   async def test():
       async with websockets.connect('ws://localhost:8765') as ws:
           print('Connected successfully')
   asyncio.run(test())
   "
   ```
2. **Browser Issues**
   ```javascript
   // Check browser console for errors
   // Try different browser
   // Clear browser cache and cookies
   // Disable browser extensions
   ```

3. **Network Proxy Issues**
   ```bash
   # Check for proxy settings
   echo $http_proxy
   echo $https_proxy
   
   # Bypass proxy for localhost
   export no_proxy="localhost,127.0.0.1"
   ```

### Performance Issues

#### Issue: Slow Response Times
**Symptoms:**
- Delayed servo movements
- Laggy web interface
- High CPU usage

**Diagnostic Steps:**
```bash
# Check system resources
htop
iostat 1
free -h

# Check process priorities
ps -eo pid,ppid,cmd,pri,nice

# Monitor network traffic
sudo tcpdump -i lo port 1883
```

**Solutions:**
1. **System Optimization**
   ```bash
   # Increase GPU memory split
   sudo raspi-config
   # Advanced Options → Memory Split → 128
   
   # Optimize CPU governor
   echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
   
   # Disable unnecessary services
   sudo systemctl disable bluetooth
   sudo systemctl disable wifi-powersave
   ```

2. **Application Tuning**
   ```bash
   # Reduce camera resolution in vision_tracking.py
   # Lower frame rate for processing
   # Increase servo update intervals
   # Optimize MQTT message frequency
   ```

3. **Hardware Upgrades**
   ```bash
   # Use faster SD card (Class 10 or better)
   # Add active cooling for Pi
   # Use dedicated power supply (3A minimum)
   # Consider Pi 5 with 8GB RAM
   ```

#### Issue: Memory Leaks
**Symptoms:**
- Gradually increasing memory usage
- System becomes unresponsive over time
- Out of memory errors

**Solutions:**
1. **Python Memory Management**
   ```python
   # Add to vision_tracking.py
   import gc
   
   # Force garbage collection periodically
   if frame_count % 100 == 0:
       gc.collect()
   
   # Release OpenCV resources properly
   cap.release()
   cv2.destroyAllWindows()
   ```

2. **C++ Memory Management**
   ```cpp
   // Check for memory leaks with valgrind
   valgrind --leak-check=full ./build/SmartArm-Vision
   
   // Ensure proper cleanup in destructors
   // Use smart pointers where possible
   ```

## Data and Logging Issues

#### Issue: CSV Data Not Saving
**Symptoms:**
- Empty or missing CSV files
- Permission denied errors
- Corrupted data files

**Solutions:**
1. **File Permissions**
   ```bash
   # Check data directory permissions
   ls -la data/
   
   # Fix permissions
   sudo chown -R $USER:$USER data/
   chmod 755 data/
   chmod 644 data/*.csv
   ```

2. **Disk Space**
   ```bash
   # Check available space
   df -h
   
   # Clean up old logs
   find data/ -name "*.csv" -mtime +30 -delete
   
   # Implement log rotation
   logrotate /etc/logrotate.d/smartarm
   ```

## Emergency Procedures

### Emergency Stop
If the system becomes unresponsive or dangerous:

1. **Immediate Actions**
   ```bash
   # Physical emergency stop
   # Press red emergency button (if installed)
   
   # Software emergency stop
   mosquitto_pub -h localhost -t "smartarm/emergency" -m "STOP"
   
   # Kill all processes
   sudo pkill -f SmartArm-Vision
   sudo pkill -f python.*main.py
   ```

2. **Power Cycle**
   ```bash
   # Safe shutdown
   sudo shutdown -h now
   
   # Wait 10 seconds, then power on
   # Check system logs after restart
   journalctl -u smartarm --since "10 minutes ago"
   ```

### System Recovery

#### Corrupted Installation
```bash
# Backup user data
cp -r data/ ~/smartarm_backup/

# Clean reinstall
rm -rf build/
git clean -fdx
./setup.sh

# Restore data
cp -r ~/smartarm_backup/* data/
```

#### Hardware Damage Assessment
```bash
# Test each component individually
./build/SmartArm-Vision --test-servo 0
./build/SmartArm-Vision --test-servo 1
./build/SmartArm-Vision --test-sensor
./build/SmartArm-Vision --test-camera

# Document any failures
# Replace damaged components
# Recalibrate system after repairs
```

## Getting Help

### Log Collection
Before seeking help, collect these logs:
```bash
# Create support bundle
mkdir ~/smartarm_logs
cp /var/log/syslog ~/smartarm_logs/
cp data/events.csv ~/smartarm_logs/
dmesg > ~/smartarm_logs/dmesg.log
journalctl --since "1 hour ago" > ~/smartarm_logs/journal.log

# System information
uname -a > ~/smartarm_logs/system_info.txt
lscpu >> ~/smartarm_logs/system_info.txt
free -h >> ~/smartarm_logs/system_info.txt
df -h >> ~/smartarm_logs/system_info.txt

# Create archive
tar -czf ~/smartarm_support_$(date +%Y%m%d_%H%M%S).tar.gz ~/smartarm_logs/
```

### Contact Information
- **GitHub Issues**: [Project Repository Issues](https://github.com/ficrammanifur/smart-robotic-arm)
- **Documentation**: Check README.md and docs/ folder
- **Community**: Raspberry Pi forums, robotics communities

### Before Reporting Issues
1. Check this troubleshooting guide
2. Search existing GitHub issues
3. Try the diagnostic steps
4. Collect relevant logs
5. Document steps to reproduce the problem

---

*Last updated: January 2025*
*For additional help, see README.md or create an issue on GitHub*
