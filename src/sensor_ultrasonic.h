#ifndef SENSOR_ULTRASONIC_H
#define SENSOR_ULTRASONIC_H

class UltrasonicSensor {
private:
    int trig_pin;
    int echo_pin;
    bool initialized;
    
public:
    UltrasonicSensor();
    ~UltrasonicSensor();
    
    // Initialize ultrasonic sensor
    bool initialize();
    
    // Get distance measurement in centimeters
    float getDistance();
    
    // Get multiple readings and return average
    float getAverageDistance(int samples = 5);
    
    // Check if object is within specified range
    bool isObjectInRange(float min_distance, float max_distance);
    
    // Get sensor status
    bool isInitialized() const { return initialized; }
};

#endif // SENSOR_ULTRASONIC_H
