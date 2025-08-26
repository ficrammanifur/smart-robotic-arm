#!/bin/bash

# Smart Robotic Arm - System Health Check Script
# This script performs comprehensive system diagnostics

echo "=== Smart Robotic Arm Health Check ==="
echo "Started at: $(date)"
echo

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
    fi
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# System Information
echo "=== System Information ==="
echo "Hostname: $(hostname)"
echo "OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
echo "Kernel: $(uname -r)"
echo "Architecture: $(uname -m)"
echo "Uptime: $(uptime -p)"
echo

# Hardware Check
echo "=== Hardware Status ==="

# CPU Temperature
cpu_temp=$(vcgencmd measure_temp | cut -d'=' -f2 | cut -d"'" -f1)
if (( $(echo "$cpu_temp > 70" | bc -l) )); then
    print_warning "CPU Temperature: ${cpu_temp}°C (High)"
else
    print_status 0 "CPU Temperature: ${cpu_temp}°C"
fi

# Memory Usage
mem_usage=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
if (( $(echo "$mem_usage > 80" | bc -l) )); then
    print_warning "Memory Usage: ${mem_usage}%"
else
    print_status 0 "Memory Usage: ${mem_usage}%"
fi

# Disk Space
disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $disk_usage -gt 80 ]; then
    print_warning "Disk Usage: ${disk_usage}%"
else
    print_status 0 "Disk Usage: ${disk_usage}%"
fi

echo

# GPIO and Hardware Interfaces
echo "=== Hardware Interfaces ==="

# Check if GPIO is accessible
if [ -c /dev/gpiomem ]; then
    print_status 0 "GPIO Interface Available"
else
    print_status 1 "GPIO Interface Not Available"
fi

# Check camera
camera_detected=$(vcgencmd get_camera | grep "detected=1")
if [ -n "$camera_detected" ]; then
    print_status 0 "Camera Detected"
else
    print_status 1 "Camera Not Detected"
fi

# Check I2C
if [ -c /dev/i2c-1 ]; then
    print_status 0 "I2C Interface Available"
else
    print_status 1 "I2C Interface Not Available"
fi

echo

# Software Dependencies
echo "=== Software Dependencies ==="

# Check Python
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version | cut -d' ' -f2)
    print_status 0 "Python 3: $python_version"
else
    print_status 1 "Python 3 Not Found"
fi

# Check pip packages
echo "Checking Python packages..."
cd "Backend python" 2>/dev/null
if [ -f requirements.txt ]; then
    while read requirement; do
        package=$(echo $requirement | cut -d'=' -f1 | cut -d'>' -f1 | cut -d'<' -f1)
        if python3 -c "import $package" 2>/dev/null; then
            print_status 0 "Python package: $package"
        else
            print_status 1 "Python package: $package"
        fi
    done < requirements.txt
fi
cd - > /dev/null

# Check C++ build tools
if command -v gcc &> /dev/null; then
    gcc_version=$(gcc --version | head -n1 | cut -d' ' -f4)
    print_status 0 "GCC: $gcc_version"
else
    print_status 1 "GCC Not Found"
fi

if command -v cmake &> /dev/null; then
    cmake_version=$(cmake --version | head -n1 | cut -d' ' -f3)
    print_status 0 "CMake: $cmake_version"
else
    print_status 1 "CMake Not Found"
fi

echo

# Services Status
echo "=== Services Status ==="

# MQTT Broker
if systemctl is-active --quiet mosquitto; then
    print_status 0 "MQTT Broker (Mosquitto)"
else
    print_status 1 "MQTT Broker (Mosquitto)"
fi

# Check if our applications are running
if pgrep -f "SmartArm-Vision" > /dev/null; then
    print_status 0 "C++ Controller Process"
else
    print_status 1 "C++ Controller Process"
fi

if pgrep -f "python.*main.py" > /dev/null; then
    print_status 0 "Python Backend Process"
else
    print_status 1 "Python Backend Process"
fi

echo

# Network Connectivity
echo "=== Network Connectivity ==="

# Localhost connectivity
if ping -c 1 localhost &> /dev/null; then
    print_status 0 "Localhost Connectivity"
else
    print_status 1 "Localhost Connectivity"
fi

# MQTT port
if nc -z localhost 1883 2>/dev/null; then
    print_status 0 "MQTT Port (1883)"
else
    print_status 1 "MQTT Port (1883)"
fi

# Web server port
if nc -z localhost 5000 2>/dev/null; then
    print_status 0 "Web Server Port (5000)"
else
    print_status 1 "Web Server Port (5000)"
fi

# WebSocket port
if nc -z localhost 8765 2>/dev/null; then
    print_status 0 "WebSocket Port (8765)"
else
    print_status 1 "WebSocket Port (8765)"
fi

echo

# File System Check
echo "=== File System Check ==="

# Check project structure
required_dirs=("src" "include" "Backend python" "dashboard" "data" "docs")
for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        print_status 0 "Directory: $dir"
    else
        print_status 1 "Directory: $dir"
    fi
done

# Check important files
required_files=("CMakeLists.txt" "setup.sh" "README.md")
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        print_status 0 "File: $file"
    else
        print_status 1 "File: $file"
    fi
done

# Check build directory
if [ -d "build" ] && [ -f "build/SmartArm-Vision" ]; then
    print_status 0 "C++ Build Executable"
else
    print_status 1 "C++ Build Executable"
fi

echo

# Performance Metrics
echo "=== Performance Metrics ==="

# Load average
load_avg=$(uptime | awk -F'load average:' '{print $2}' | cut -d',' -f1 | xargs)
echo "Load Average (1min): $load_avg"

# Process count
process_count=$(ps aux | wc -l)
echo "Running Processes: $process_count"

# Network connections
network_connections=$(netstat -an | grep ESTABLISHED | wc -l)
echo "Network Connections: $network_connections"

echo

# Recommendations
echo "=== Recommendations ==="

if (( $(echo "$cpu_temp > 70" | bc -l) )); then
    echo "• Consider adding cooling for CPU temperature"
fi

if (( $(echo "$mem_usage > 80" | bc -l) )); then
    echo "• High memory usage detected - consider closing unnecessary applications"
fi

if [ $disk_usage -gt 80 ]; then
    echo "• Low disk space - consider cleaning up old files"
fi

if ! systemctl is-active --quiet mosquitto; then
    echo "• Start MQTT broker: sudo systemctl start mosquitto"
fi

if ! pgrep -f "SmartArm-Vision" > /dev/null; then
    echo "• Start C++ controller: ./build/SmartArm-Vision"
fi

if ! pgrep -f "python.*main.py" > /dev/null; then
    echo "• Start Python backend: cd 'Backend python' && python3 main.py"
fi

echo
echo "=== Health Check Complete ==="
echo "Completed at: $(date)"

# Exit with error code if critical issues found
if ! systemctl is-active --quiet mosquitto || \
   ! [ -f "build/SmartArm-Vision" ] || \
   [ $disk_usage -gt 90 ]; then
    echo "Critical issues detected!"
    exit 1
else
    echo "System appears healthy!"
    exit 0
fi
