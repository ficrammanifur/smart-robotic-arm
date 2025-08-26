#include "servo_control.h"
#include "../include/config.h"
#include <wiringPi.h>
#include <softPwm.h>
#include <iostream>
#include <thread>
#include <chrono>
#include <algorithm>

ServoControl::ServoControl() : initialized(false) {
    servo_pins = {
        SERVO_BASE_PIN,
        SERVO_SHOULDER_PIN,
        SERVO_ELBOW_PIN,
        SERVO_WRIST_PIN,
        SERVO_GRIPPER_PIN
    };
    current_angles.resize(servo_pins.size(), 90); // Initialize to middle position
}

ServoControl::~ServoControl() {
    if (initialized) {
        emergencyStop();
    }
}

bool ServoControl::initialize() {
    if (wiringPiSetupGpio() == -1) {
        std::cerr << "Failed to initialize wiringPi" << std::endl;
        return false;
    }
    
    // Initialize PWM for each servo
    for (size_t i = 0; i < servo_pins.size(); i++) {
        pinMode(servo_pins[i], OUTPUT);
        if (softPwmCreate(servo_pins[i], 0, 200) != 0) {
            std::cerr << "Failed to create PWM for servo " << i << std::endl;
            return false;
        }
    }
    
    initialized = true;
    moveToHome();
    
    std::cout << "Servo control system initialized successfully" << std::endl;
    return true;
}

bool ServoControl::setServoAngle(int servo_id, int angle) {
    if (!initialized) {
        std::cerr << "Servo control not initialized" << std::endl;
        return false;
    }
    
    if (servo_id < 0 || servo_id >= static_cast<int>(servo_pins.size())) {
        std::cerr << "Invalid servo ID: " << servo_id << std::endl;
        return false;
    }
    
    if (!isValidAngle(angle)) {
        std::cerr << "Invalid angle: " << angle << std::endl;
        return false;
    }
    
    // Convert angle to PWM value (typical servo: 1ms-2ms pulse width)
    // PWM range 0-200, servo range 0-180 degrees
    int pwm_value = (angle * 200) / 180;
    pwm_value = std::max(5, std::min(25, pwm_value)); // Clamp to safe range
    
    softPwmWrite(servo_pins[servo_id], pwm_value);
    current_angles[servo_id] = angle;
    
    // Small delay for servo movement
    std::this_thread::sleep_for(std::chrono::milliseconds(SERVO_DELAY_MS));
    
    return true;
}

bool ServoControl::setServoAngles(const std::vector<int>& angles) {
    if (angles.size() != servo_pins.size()) {
        std::cerr << "Angle array size mismatch" << std::endl;
        return false;
    }
    
    bool success = true;
    for (size_t i = 0; i < angles.size(); i++) {
        if (!setServoAngle(i, angles[i])) {
            success = false;
        }
    }
    
    return success;
}

int ServoControl::getServoAngle(int servo_id) const {
    if (servo_id < 0 || servo_id >= static_cast<int>(current_angles.size())) {
        return -1;
    }
    return current_angles[servo_id];
}

std::vector<int> ServoControl::getAllAngles() const {
    return current_angles;
}

void ServoControl::moveToHome() {
    std::vector<int> home_position = {90, 90, 90, 90, 90}; // Middle positions
    setServoAngles(home_position);
    std::cout << "Moved to home position" << std::endl;
}

void ServoControl::emergencyStop() {
    if (!initialized) return;
    
    for (int pin : servo_pins) {
        softPwmWrite(pin, 0); // Stop PWM signal
    }
    std::cout << "Emergency stop activated" << std::endl;
}

bool ServoControl::smoothMove(int servo_id, int target_angle, int steps) {
    if (!initialized || servo_id < 0 || servo_id >= static_cast<int>(servo_pins.size())) {
        return false;
    }
    
    int current = current_angles[servo_id];
    int step_size = (target_angle - current) / steps;
    
    for (int i = 1; i <= steps; i++) {
        int intermediate_angle = current + (step_size * i);
        if (i == steps) intermediate_angle = target_angle; // Ensure exact final position
        
        setServoAngle(servo_id, intermediate_angle);
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
    }
    
    return true;
}

bool ServoControl::isValidAngle(int angle) const {
    return angle >= MIN_SERVO_ANGLE && angle <= MAX_SERVO_ANGLE;
}
