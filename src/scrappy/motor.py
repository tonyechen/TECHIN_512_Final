import board
import pwmio
import digitalio
import time

# QT Py ESP32-S3 pin mapping
# You'll need to choose actual pins from: A0, A1, A2, A3, SCK, MISO, MOSI, TX, RX, SCL, SDA
# Here's a suggested mapping using available GPIO pins:

# Motor A pins
ENA = pwmio.PWMOut(board.SCK, frequency=5000)   # Was D8
IN1 = digitalio.DigitalInOut(board.MISO)         # Was D9
IN2 = digitalio.DigitalInOut(board.MOSI)         # Was D10

# Motor B pins
IN3 = digitalio.DigitalInOut(board.A3)         # Was D3
IN4 = digitalio.DigitalInOut(board.A2)        # Was D2
ENB = pwmio.PWMOut(board.A1, frequency=5000) # Was D1

# Configure direction pins as outputs
IN1.direction = digitalio.Direction.OUTPUT
IN2.direction = digitalio.Direction.OUTPUT
IN3.direction = digitalio.Direction.OUTPUT
IN4.direction = digitalio.Direction.OUTPUT

# Initialize motors to stopped state
IN1.value = False
IN2.value = False
IN3.value = False
IN4.value = False

def set_speed(pwm_pin, speed):
    """Set motor speed (0-100%)"""
    time.sleep(0.02)
    duty = int((80 / 100) * 65535)
    pwm_pin.duty_cycle = max(0, min(65535, duty))
    time.sleep(0.01)
    duty = int((speed / 100) * 65535)
    pwm_pin.duty_cycle = max(0, min(65535, duty))

def forward(speed=10):
    """Move both motors forward"""
    # Motor A forward
    IN1.value = True
    IN2.value = False
    set_speed(ENA, speed)
    
    # Motor B forward
    IN3.value = True
    IN4.value = False
    set_speed(ENB, speed)
    print("Moving Forward")

def backward(speed=10):
    """Move both motors backward"""
    # Motor A backward
    IN1.value = False
    IN2.value = True
    set_speed(ENA, speed)
    
    # Motor B backward
    IN3.value = False
    IN4.value = True
    set_speed(ENB, speed)
    print("Moving Backward")

def right(speed=10):
    """Turn left (Motor A backward, Motor B forward)"""
    # Motor A backward
    IN1.value = False
    IN2.value = True
    set_speed(ENA, speed)
    
    # Motor B forward
    IN3.value = True
    IN4.value = False
    set_speed(ENB, speed)
    print("Turning RIGHT")

def left(speed=10):
    """Turn right (Motor A forward, Motor B backward)"""
    # Motor A forward
    IN1.value = True
    IN2.value = False
    set_speed(ENA, speed)
    
    # Motor B backward
    IN3.value = False
    IN4.value = True
    set_speed(ENB, speed)
    print("Turning LEFT")

def stop():
    """Stop both motors"""
    IN1.value = False
    IN2.value = False
    set_speed(ENA, 0)
    
    IN3.value = False
    IN4.value = False
    set_speed(ENB, 0)

def motor_a(speed, forward=True):
    """Control Motor A individually (speed 0-100%)"""
    if forward:
        IN1.value = True
        IN2.value = False
    else:
        IN1.value = False
        IN2.value = True
    set_speed(ENA, abs(speed))

def motor_b(speed, forward=True):
    """Control Motor B individually (speed 0-100%)"""
    if forward:
        IN3.value = True
        IN4.value = False
    else:
        IN3.value = False
        IN4.value = True
    set_speed(ENB, abs(speed))