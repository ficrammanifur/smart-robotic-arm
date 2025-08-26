#include "sensor_ultrasonic.h"
#include "../include/config.h"
#include <wiringPi.h>
#include <iostream>
#include <chrono>
#include <thread>
#include <vector>
#include <numeric>

UltrasonicSensor::UltrasonicSensor() : 
    trig_pin(ULTRASONIC_TRIG_PIN), 
    echo_pin(ULTRASONIC_ECHO_PIN), 
    initialized(false) {
}

UltrasonicSensor::~UltrasonicSensor() {
    // Cleanup if needed
}

bool UltrasonicSensor::initialize() {
    if (wiringPiSetupGpio() == -1) {
        std::cerr << "Failed to initialize wiringPi for ultrasonic sensor" << std::endl;
        return false;
    }
    
    pinMode(trig_pin, OUTPUT);
    pinMode(echo_pin, INPUT);
    
    // Ensure trigger is low initially
    digitalWrite(trig_pin, LOW);
    std::this_thread::sleep_for(std::chrono::milliseconds(10));
    
    initialized = true;
    std::cout << "Ultrasonic sensor initialized successfully" << std::endl;
    return true;
}

float UltrasonicSensor::getDistance() {
    if (!initialized) {
        std::cerr << "Ultrasonic sensor not initialized" << std::endl;
        return -1.0f;
    }
    
    // Send trigger pulse
    digitalWrite(trig_pin, HIGH);
    std::this_thread::sleep_for(std::chrono::microseconds(10));
    digitalWrite(trig_pin, LOW);
    
    // Wait for echo start
    auto start_time = std::chrono::high_resolution_clock::now();
    auto timeout = start_time + std::chrono::milliseconds(30);
    
    while (digitalRead(echo_pin) == LOW) {
        if (std::chrono::high_resolution_clock::now() > timeout) {
            std::cerr << "Ultrasonic sensor timeout (echo start)" << std::endl;
            return -1.0f;
        }
    }
    
    // Measure echo duration
    auto echo_start = std::chrono::high_resolution_clock::now();
    timeout = echo_start + std::chrono::milliseconds(30);
    
    while (digitalRead(echo_pin) == HIGH) {
        if (std::chrono::high_resolution_clock::now() > timeout) {
            std::cerr << "Ultrasonic sensor timeout (echo end)" << std::endl;
            return -1.0f;
        }
    }
    
    auto echo_end = std::chrono::high_resolution_clock::now();
    
    // Calculate distance (speed of sound = 343 m/s = 0.0343 cm/μs)
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(echo_end - echo_start);
    float distance = (duration.count() * 0.0343f) / 2.0f; // Divide by 2 for round trip
    
    // Validate reading
    if (distance < 2.0f || distance > ULTRASONIC_MAX_DISTANCE) {
        return -1.0f; // Invalid reading
    }
    
    return distance;
}

float UltrasonicSensor::getAverageDistance(int samples) {
    if (samples <= 0) samples = 1;
    
    std::vector<float> readings;
    readings.reserve(samples);
    
    for (int i = 0; i < samples; i++) {
        float distance = getDistance();
        if (distance > 0) {
            readings.push_back(distance);
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(60)); // Delay between readings
    }
    
    if (readings.empty()) {
        return -1.0f;
    }
    
    float sum = std::accumulate(readings.begin(), readings.end(), 0.0f);
    return sum / readings.size();
}

bool UltrasonicSensor::isObjectInRange(float min_distance, float max_distance) {
    float distance = getAverageDistance(3);
    return (distance >= min_distance && distance <= max_distance);
}
