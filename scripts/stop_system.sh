#!/bin/bash

# Smart Robotic Arm - System Stop Script
# Gracefully stops all components

echo "Stopping Smart Robotic Arm System..."

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
    fi
}

# Send emergency stop command
echo "Sending emergency stop command..."
mosquitto_pub -h localhost -t "smartarm/emergency" -m "STOP" 2>/dev/null

# Stop processes using saved PIDs
if [ -f /tmp/smartarm_python.pid ]; then
    PYTHON_PID=$(cat /tmp/smartarm_python.pid)
    if kill -0 $PYTHON_PID 2>/dev/null; then
        kill -TERM $PYTHON_PID
        sleep 2
        if kill -0 $PYTHON_PID 2>/dev/null; then
            kill -KILL $PYTHON_PID
        fi
        print_status 0 "Python backend stopped"
    fi
    rm -f /tmp/smartarm_python.pid
fi

if [ -f /tmp/smartarm_cpp.pid ]; then
    CPP_PID=$(cat /tmp/smartarm_cpp.pid)
    if kill -0 $CPP_PID 2>/dev/null; then
        kill -TERM $CPP_PID
        sleep 2
        if kill -0 $CPP_PID 2>/dev/null; then
            kill -KILL $CPP_PID
        fi
        print_status 0 "C++ controller stopped"
    fi
    rm -f /tmp/smartarm_cpp.pid
fi

# Kill any remaining processes
pkill -f "SmartArm-Vision" 2>/dev/null
pkill -f "python.*main.py" 2>/dev/null

print_status 0 "All processes stopped"

echo "System stopped successfully!"
