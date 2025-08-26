#!/bin/bash

# Smart Robotic Arm - System Startup Script
# Starts all components in the correct order

echo "Starting Smart Robotic Arm System..."

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
        exit 1
    fi
}

# Check if running as root (not recommended)
if [ "$EUID" -eq 0 ]; then
    echo -e "${YELLOW}Warning: Running as root is not recommended${NC}"
fi

# Step 1: Start MQTT Broker
echo "Step 1: Starting MQTT Broker..."
sudo systemctl start mosquitto
print_status $? "MQTT Broker started"

# Step 2: Build C++ application if needed
echo "Step 2: Checking C++ build..."
if [ ! -f "build/SmartArm-Vision" ]; then
    echo "Building C++ application..."
    mkdir -p build
    cd build
    cmake ..
    make
    cd ..
fi
print_status $? "C++ application ready"

# Step 3: Start Python backend
echo "Step 3: Starting Python backend..."
cd "Backend python"
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1

# Start Python backend in background
nohup python3 main.py > ../logs/python_backend.log 2>&1 &
PYTHON_PID=$!
cd ..
print_status $? "Python backend started (PID: $PYTHON_PID)"

# Step 4: Start C++ controller
echo "Step 4: Starting C++ controller..."
nohup ./build/SmartArm-Vision > logs/cpp_controller.log 2>&1 &
CPP_PID=$!
print_status $? "C++ controller started (PID: $CPP_PID)"

# Step 5: Wait for services to initialize
echo "Step 5: Waiting for services to initialize..."
sleep 5

# Step 6: Verify all services are running
echo "Step 6: Verifying services..."

# Check MQTT
if nc -z localhost 1883 2>/dev/null; then
    print_status 0 "MQTT service responding"
else
    print_status 1 "MQTT service not responding"
fi

# Check Python backend
if nc -z localhost 5000 2>/dev/null; then
    print_status 0 "Python backend responding"
else
    print_status 1 "Python backend not responding"
fi

# Check WebSocket
if nc -z localhost 8765 2>/dev/null; then
    print_status 0 "WebSocket service responding"
else
    print_status 1 "WebSocket service not responding"
fi

# Check processes
if kill -0 $PYTHON_PID 2>/dev/null; then
    print_status 0 "Python process running"
else
    print_status 1 "Python process not running"
fi

if kill -0 $CPP_PID 2>/dev/null; then
    print_status 0 "C++ process running"
else
    print_status 1 "C++ process not running"
fi

echo
echo "=== System Started Successfully ==="
echo "Python Backend PID: $PYTHON_PID"
echo "C++ Controller PID: $CPP_PID"
echo
echo "Access the dashboard at: http://localhost:5000"
echo "View logs with: tail -f logs/*.log"
echo "Stop system with: ./scripts/stop_system.sh"
echo

# Save PIDs for stop script
echo "$PYTHON_PID" > /tmp/smartarm_python.pid
echo "$CPP_PID" > /tmp/smartarm_cpp.pid
