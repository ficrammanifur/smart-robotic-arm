#include "../include/config.h"
#include <wiringPi.h>
#include <softPwm.h>
#include <iostream>
#include <algorithm>

class MotorDriver {
private:
    int pwm_pin;
    int dir1_pin;
    int dir2_pin;
    bool initialized;
    int current_speed;
    
public:
    MotorDriver() : 
        pwm_pin(MOTOR_PWM_PIN),
        dir1_pin(MOTOR_DIR1_PIN),
        dir2_pin(MOTOR_DIR2_PIN),
        initialized(false),
        current_speed(0) {
    }
    
    bool initialize() {
        if (wiringPiSetupGpio() == -1) {
            std::cerr << "Failed to initialize wiringPi for motor driver" << std::endl;
            return false;
        }
        
        pinMode(dir1_pin, OUTPUT);
        pinMode(dir2_pin, OUTPUT);
        pinMode(pwm_pin, OUTPUT);
        
        if (softPwmCreate(pwm_pin, 0, 100) != 0) {
            std::cerr << "Failed to create PWM for motor driver" << std::endl;
            return false;
        }
        
        stop();
        initialized = true;
        std::cout << "Motor driver initialized successfully" << std::endl;
        return true;
    }
    
    void setSpeed(int speed) {
        if (!initialized) return;
        
        // Clamp speed to valid range (-100 to 100)
        speed = std::max(-100, std::min(100, speed));
        current_speed = speed;
        
        if (speed == 0) {
            stop();
            return;
        }
        
        int pwm_value = abs(speed);
        
        if (speed > 0) {
            // Forward direction
            digitalWrite(dir1_pin, HIGH);
            digitalWrite(dir2_pin, LOW);
        } else {
            // Reverse direction
            digitalWrite(dir1_pin, LOW);
            digitalWrite(dir2_pin, HIGH);
        }
        
        softPwmWrite(pwm_pin, pwm_value);
    }
    
    void stop() {
        if (!initialized) return;
        
        digitalWrite(dir1_pin, LOW);
        digitalWrite(dir2_pin, LOW);
        softPwmWrite(pwm_pin, 0);
        current_speed = 0;
    }
    
    int getCurrentSpeed() const {
        return current_speed;
    }
    
    bool isInitialized() const {
        return initialized;
    }
};

// Global motor driver instance
static MotorDriver motor_driver;

extern "C" {
    bool motor_initialize() {
        return motor_driver.initialize();
    }
    
    void motor_set_speed(int speed) {
        motor_driver.setSpeed(speed);
    }
    
    void motor_stop() {
        motor_driver.stop();
    }
    
    int motor_get_speed() {
        return motor_driver.getCurrentSpeed();
    }
}
