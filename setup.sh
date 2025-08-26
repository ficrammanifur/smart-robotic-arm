#!/bin/bash

echo "🤖 Smart Robotic Arm Setup Script for Raspberry Pi 5"
echo "=================================================="

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install C++ build tools
echo "🔧 Installing C++ build tools..."
sudo apt install -y cmake build-essential pkg-config

# Install wiringPi for GPIO control
echo "🔌 Installing wiringPi library..."
sudo apt install -y wiringpi

# Install Python and pip
echo "🐍 Installing Python dependencies..."
sudo apt install -y python3 python3-pip python3-venv

# Install OpenCV dependencies
echo "📷 Installing OpenCV system dependencies..."
sudo apt install -y libopencv-dev python3-opencv
sudo apt install -y libatlas-base-dev libhdf5-dev libhdf5-serial-dev
sudo apt install -y libqtgui4 libqtwebkit4 libqt4-test

# Install camera support
echo "📸 Installing camera support..."
sudo apt install -y python3-picamera2

# Install MQTT broker
echo "📡 Installing MQTT broker..."
sudo apt install -y mosquitto mosquitto-clients
sudo systemctl enable mosquitto
sudo systemctl start mosquitto

# Create Python virtual environment
echo "🌐 Setting up Python virtual environment..."
cd "Backend python"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
cd ..

# Set permissions
echo "🔐 Setting up permissions..."
sudo usermod -a -G gpio $USER
sudo usermod -a -G video $USER

# Create data directories
echo "📁 Creating data directories..."
mkdir -p data/images
mkdir -p dashboard/assets/icons

# Build C++ project
echo "🏗️ Building C++ project..."
mkdir -p build
cd build
cmake ..
make
cd ..

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Reboot your Raspberry Pi: sudo reboot"
echo "2. Connect your hardware according to include/config.h"
echo "3. Run: ./build/SmartArm-Vision"
echo "4. In another terminal: cd 'Backend python' && python main.py"
echo "5. Open dashboard/index.html in your browser"
