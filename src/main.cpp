#include <iostream>
#include <thread>
#include <chrono>
#include <signal.h>
#include <atomic>
#include <string>
#include <sstream>
#include <mosquitto.h>
#include "servo_control.h"
#include "sensor_ultrasonic.h"
#include "../include/config.h"

// Global components
ServoControl servo_control;
UltrasonicSensor ultrasonic;
struct mosquitto *mosq = nullptr;
std::atomic<bool> running(true);
std::atomic<bool> auto_mode(true);

// External motor driver functions
extern "C" {
    bool motor_initialize();
    void motor_set_speed(int speed);
    void motor_stop();
    int motor_get_speed();
}

// Signal handler for graceful shutdown
void signal_handler(int signal) {
    std::cout << "\nReceived signal " << signal << ", shutting down..." << std::endl;
    running = false;
}

// MQTT message callback
void on_message(struct mosquitto *mosq, void *userdata, const struct mosquitto_message *message) {
    std::string topic(message->topic);
    std::string payload((char*)message->payload, message->payloadlen);
    
    std::cout << "Received MQTT message - Topic: " << topic << ", Payload: " << payload << std::endl;
    
    if (topic == MQTT_TOPIC_CONTROL) {
        // Parse control commands
        std::istringstream iss(payload);
        std::string command;
        iss >> command;
        
        if (command == "MODE") {
            std::string mode;
            iss >> mode;
            auto_mode = (mode == "AUTO");
            std::cout << "Switched to " << (auto_mode ? "AUTO" : "MANUAL") << " mode" << std::endl;
        }
        else if (command == "SERVO" && !auto_mode) {
            int servo_id, angle;
            if (iss >> servo_id >> angle) {
                servo_control.setServoAngle(servo_id, angle);
                std::cout << "Manual servo control: " << servo_id << " -> " << angle << "°" << std::endl;
            }
        }
        else if (command == "MOTOR" && !auto_mode) {
            int speed;
            if (iss >> speed) {
                motor_set_speed(speed);
                std::cout << "Manual motor control: " << speed << std::endl;
            }
        }
        else if (command == "STOP") {
            servo_control.emergencyStop();
            motor_stop();
            std::cout << "Emergency stop activated" << std::endl;
        }
        else if (command == "HOME") {
            servo_control.moveToHome();
            std::cout << "Moving to home position" << std::endl;
        }
    }
}

// MQTT connection callback
void on_connect(struct mosquitto *mosq, void *userdata, int result) {
    if (result == 0) {
        std::cout << "Connected to MQTT broker" << std::endl;
        mosquitto_subscribe(mosq, nullptr, MQTT_TOPIC_CONTROL, 0);
    } else {
        std::cerr << "Failed to connect to MQTT broker: " << result << std::endl;
    }
}

// Initialize MQTT
bool initialize_mqtt() {
    mosquitto_lib_init();
    
    mosq = mosquitto_new(nullptr, true, nullptr);
    if (!mosq) {
        std::cerr << "Failed to create MQTT client" << std::endl;
        return false;
    }
    
    mosquitto_connect_callback_set(mosq, on_connect);
    mosquitto_message_callback_set(mosq, on_message);
    
    int result = mosquitto_connect(mosq, MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60);
    if (result != MOSQ_ERR_SUCCESS) {
        std::cerr << "Failed to connect to MQTT broker: " << result << std::endl;
        return false;
    }
    
    return true;
}

// Publish status data
void publish_status() {
    if (!mosq) return;
    
    std::ostringstream status;
    status << "{"
           << "\"mode\":\"" << (auto_mode ? "AUTO" : "MANUAL") << "\","
           << "\"distance\":" << ultrasonic.getDistance() << ","
           << "\"servos\":[";
    
    auto angles = servo_control.getAllAngles();
    for (size_t i = 0; i < angles.size(); i++) {
        status << angles[i];
        if (i < angles.size() - 1) status << ",";
    }
    
    status << "],"
           << "\"motor_speed\":" << motor_get_speed()
           << "}";
    
    std::string status_str = status.str();
    mosquitto_publish(mosq, nullptr, MQTT_TOPIC_STATUS, status_str.length(), status_str.c_str(), 0, false);
}

// Main control loop
void control_loop() {
    while (running) {
        if (auto_mode) {
            // Automatic vision-based control logic
            float distance = ultrasonic.getAverageDistance(3);
            
            if (distance > 0 && distance < 20.0f) {
                // Object detected within range - perform grab sequence
                std::cout << "Object detected at " << distance << "cm - executing grab sequence" << std::endl;
                
                // Move arm to grab position
                servo_control.smoothMove(1, 45, 5);  // Shoulder down
                servo_control.smoothMove(2, 120, 5); // Elbow extend
                servo_control.smoothMove(4, 0, 3);   // Open gripper
                
                std::this_thread::sleep_for(std::chrono::milliseconds(500));
                
                // Close gripper
                servo_control.smoothMove(4, 180, 3); // Close gripper
                
                std::this_thread::sleep_for(std::chrono::milliseconds(500));
                
                // Lift object
                servo_control.smoothMove(1, 90, 5);  // Shoulder up
                servo_control.smoothMove(2, 90, 5);  // Elbow retract
                
                std::cout << "Grab sequence completed" << std::endl;
                
                // Wait before next detection
                std::this_thread::sleep_for(std::chrono::seconds(3));
            }
        }
        
        // Publish status every second
        static auto last_status = std::chrono::steady_clock::now();
        auto now = std::chrono::steady_clock::now();
        if (std::chrono::duration_cast<std::chrono::seconds>(now - last_status).count() >= 1) {
            publish_status();
            last_status = now;
        }
        
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
}

int main() {
    std::cout << "Smart Robotic Arm with Vision Tracking v1.0" << std::endl;
    std::cout << "=============================================" << std::endl;
    
    // Set up signal handlers
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    
    // Initialize hardware components
    std::cout << "Initializing hardware components..." << std::endl;
    
    if (!servo_control.initialize()) {
        std::cerr << "Failed to initialize servo control" << std::endl;
        return 1;
    }
    
    if (!ultrasonic.initialize()) {
        std::cerr << "Failed to initialize ultrasonic sensor" << std::endl;
        return 1;
    }
    
    if (!motor_initialize()) {
        std::cerr << "Failed to initialize motor driver" << std::endl;
        return 1;
    }
    
    // Initialize MQTT communication
    std::cout << "Initializing MQTT communication..." << std::endl;
    if (!initialize_mqtt()) {
        std::cerr << "Failed to initialize MQTT" << std::endl;
        return 1;
    }
    
    std::cout << "System initialized successfully!" << std::endl;
    std::cout << "Mode: " << (auto_mode ? "AUTO" : "MANUAL") << std::endl;
    std::cout << "Press Ctrl+C to stop..." << std::endl;
    
    // Start MQTT loop in separate thread
    std::thread mqtt_thread([&]() {
        while (running) {
            mosquitto_loop(mosq, 100, 1);
        }
    });
    
    // Run main control loop
    control_loop();
    
    // Cleanup
    std::cout << "Shutting down..." << std::endl;
    
    if (mqtt_thread.joinable()) {
        mqtt_thread.join();
    }
    
    servo_control.emergencyStop();
    motor_stop();
    
    if (mosq) {
        mosquitto_disconnect(mosq);
        mosquitto_destroy(mosq);
    }
    mosquitto_lib_cleanup();
    
    std::cout << "Shutdown complete." << std::endl;
    return 0;
}
