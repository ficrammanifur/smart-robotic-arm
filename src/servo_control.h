#ifndef SERVO_CONTROL_H
#define SERVO_CONTROL_H

#include <vector>
#include <string>

class ServoControl {
private:
    std::vector<int> servo_pins;
    std::vector<int> current_angles;
    bool initialized;
    
public:
    ServoControl();
    ~ServoControl();
    
    // Initialize servo control system
    bool initialize();
    
    // Set individual servo angle (0-180 degrees)
    bool setServoAngle(int servo_id, int angle);
    
    // Set multiple servo angles at once
    bool setServoAngles(const std::vector<int>& angles);
    
    // Get current servo angle
    int getServoAngle(int servo_id) const;
    
    // Get all current angles
    std::vector<int> getAllAngles() const;
    
    // Move to home position
    void moveToHome();
    
    // Emergency stop - disable all servos
    void emergencyStop();
    
    // Smooth movement between positions
    bool smoothMove(int servo_id, int target_angle, int steps = 10);
    
    // Validate angle range
    bool isValidAngle(int angle) const;
    
    // Get servo status
    bool isInitialized() const { return initialized; }
};

#endif // SERVO_CONTROL_H
