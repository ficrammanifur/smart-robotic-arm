#ifndef CONFIG_H
#define CONFIG_H

// Hardware Configuration
#define SERVO_BASE_PIN 18
#define SERVO_SHOULDER_PIN 19
#define SERVO_ELBOW_PIN 20
#define SERVO_WRIST_PIN 21
#define SERVO_GRIPPER_PIN 22

// Ultrasonic Sensor Pins
#define ULTRASONIC_TRIG_PIN 23
#define ULTRASONIC_ECHO_PIN 24

// Motor Driver Pins
#define MOTOR_PWM_PIN 12
#define MOTOR_DIR1_PIN 16
#define MOTOR_DIR2_PIN 26

// System Configuration
#define MAX_SERVO_ANGLE 180
#define MIN_SERVO_ANGLE 0
#define ULTRASONIC_MAX_DISTANCE 400  // cm
#define SERVO_DELAY_MS 20

// Communication
#define MQTT_BROKER_HOST "localhost"
#define MQTT_BROKER_PORT 1883
#define MQTT_TOPIC_CONTROL "smartarm/control"
#define MQTT_TOPIC_STATUS "smartarm/status"
#define MQTT_TOPIC_DATA "smartarm/data"

// Vision Tracking
#define CAMERA_WIDTH 640
#define CAMERA_HEIGHT 480
#define DETECTION_CONFIDENCE 0.5

#endif // CONFIG_H
