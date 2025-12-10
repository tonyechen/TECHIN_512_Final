import time
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
import motor
from movement_patterns import MovementController
from accelerometer import AccelerometerMonitor

ble = BLERadio()
uart = UARTService()
advertisement = ProvideServicesAdvertisement(uart)

# Initialize controllers
movement = MovementController()
accel = AccelerometerMonitor()

# Configuration
MANUAL_MOVE_DURATION = 0.2  # seconds for individual moves
MANUAL_MODE_DURATION = 5.0  # seconds for full manual control mode
BASE_SPEED = 60

def send_response(message):
    """Send response over BLE"""
    try:
        uart.write(f"{message}\n".encode('utf-8'))
        print(f"Sent: {message}")
    except:
        pass

def handle_connection():
    """Handle BLE connection process"""
    print("Waiting for connection...")
    ble.start_advertising(advertisement)
    
    while not ble.connected:
        time.sleep(0.1)
    
    print("Connected!")
    ble.stop_advertising()

accel.calibrate()

while True:
    # Wait for connection
    handle_connection()
    
    # State variables
    state = "WAITING"  # WAITING, AUTO, MANUAL, DEAD
    manual_mode_end_time = 0
    user_move_end_time = 0
    
    movement.reset()
    accel.reset()
    
    # Connection loop
    try:
        while ble.connected:
            current_time = time.monotonic()
            
            # Check for death (only when alive)
            if state != "DEAD" and state != "WAITING":
                if accel.check_impact():
                    motor.stop()
                    state = "DEAD"
                    send_response("DEAD")
                    print("Robot died!")
            
            message = None
            # Handle incoming messages
            if uart.in_waiting:
                data = uart.read(uart.in_waiting)
                message = data.decode('utf-8').strip()
                print(f"Received: {message}")
                
                # LEVEL command - starts/restarts the game
                if message.startswith("LEVEL:"):
                    try:
                        parts = message.split(":")
                        level = int(parts[1])
                        difficulty = parts[2].upper()
                        
                        if difficulty in ["EASY", "MEDIUM", "HARD"]:
                            accel.reset()
                            movement.set_level(level, difficulty)
                            state = "AUTO"
                            user_move_end_time = 0  # Reset user move timer
                            send_response("ACK")
                            print(f"Started level {level} - {difficulty}")
                        else:
                            send_response("ACK")
                    except:
                        send_response("ACK")
                
                # MANUAL mode - 5 seconds of full control
                elif message == "MANUAL":
                    if state == "AUTO":
                        state = "MANUAL"
                        manual_mode_end_time = current_time + MANUAL_MODE_DURATION
                        motor.stop()
                        send_response("ACK")
                        print("Manual mode: 5 seconds of full control")
                
                # Movement commands
                elif message == "UP":
                    if state == "MANUAL":
                        # Continuous movement in manual mode
                        motor.forward(BASE_SPEED)
                    elif state == "AUTO":
                        # Execute user move and block auto for duration
                        motor.stop()  # Stop any current movement first
                        motor.forward(BASE_SPEED)
                        user_move_end_time = current_time + MANUAL_MOVE_DURATION
                    send_response("ACK")
                
                elif message == "DOWN":
                    if state == "MANUAL":
                        motor.backward(BASE_SPEED)
                    elif state == "AUTO":
                        motor.stop()
                        motor.backward(BASE_SPEED)
                        user_move_end_time = current_time + MANUAL_MOVE_DURATION
                    send_response("ACK")
                
                elif message == "LEFT":
                    if state == "MANUAL":
                        motor.left(BASE_SPEED)
                    elif state == "AUTO":
                        motor.stop()
                        motor.left(BASE_SPEED)
                        user_move_end_time = current_time + MANUAL_MOVE_DURATION
                    send_response("ACK")
                
                elif message == "RIGHT":
                    if state == "MANUAL":
                        motor.right(BASE_SPEED)
                    elif state == "AUTO":
                        motor.stop()
                        motor.right(BASE_SPEED)
                        user_move_end_time = current_time + MANUAL_MOVE_DURATION
                    send_response("ACK")
                
                elif message == "STOP":
                    motor.stop()
                    user_move_end_time = 0
                    state = "WAITING"
                    send_response("ACK")
                
                else:
                    send_response("ACK")
            
            # Update movement states
            if state == "AUTO":
                # Only run auto mode if user move timer has expired
                if current_time >= user_move_end_time: # add one here for a short delay before the robot makes another random move
                    # Execute auto random movements
                    movement.update_auto_mode()
                # else: user command is still executing, don't interfere
            
            elif state == "MANUAL":
                # Check if manual mode expired
                if current_time >= manual_mode_end_time:
                    state = "AUTO"
                    motor.stop()
                    movement.reset()
                    user_move_end_time = 0  # Reset timer
                    print("Manual mode ended, back to auto")
            
            elif state == "DEAD":
                motor.stop()
            
    
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        print("Disconnected!")
        motor.stop()
        ble.stop_advertising()
        time.sleep(0.5)
