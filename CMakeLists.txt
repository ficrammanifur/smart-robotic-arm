cmake_minimum_required(VERSION 3.16)
project(SmartArm-Vision VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find required packages
find_package(PkgConfig REQUIRED)

# Check for wiringPi (Raspberry Pi GPIO library)
pkg_check_modules(WIRINGPI REQUIRED wiringpi)

# Include directories
include_directories(include)
include_directories(${WIRINGPI_INCLUDE_DIRS})

# Source files
set(SOURCES
    src/main.cpp
    src/servo_control.cpp
    src/sensor_ultrasonic.cpp
    src/driver_motor.cpp
)

# Create executable
add_executable(${PROJECT_NAME} ${SOURCES})

# Link libraries
target_link_libraries(${PROJECT_NAME} 
    ${WIRINGPI_LIBRARIES}
    pthread
)

# Compiler flags
target_compile_options(${PROJECT_NAME} PRIVATE ${WIRINGPI_CFLAGS_OTHER})

# Install target
install(TARGETS ${PROJECT_NAME} DESTINATION bin)

# Debug build options
if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    target_compile_definitions(${PROJECT_NAME} PRIVATE DEBUG_MODE)
endif()
