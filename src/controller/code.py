import board
import time
import busio
import displayio
import i2cdisplaybus
import adafruit_displayio_ssd1306
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
from buttons import Buttons
from accelerometer import Accelerometer
from display import DisplayManager
from rotary_encoder import RotaryEncoder
from neopixel_status import NeoPixelStatus

# Release any existing displays
displayio.release_displays()

# Setup I2C for OLED
i2c = busio.I2C(board.SCL, board.SDA)
display_bus = i2cdisplaybus.I2CDisplayBus(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)

# Initialize display manager
display_mgr = DisplayManager(display)

# Initialize accelerometer
accelerometer = Accelerometer(i2c=i2c, shake_threshold=15.0, cooldown_time=0.5)
print("Calibrating accelerometer...")
accelerometer.calibrate(20)
print("Accelerometer ready!")

# Initialize buttons
buttons = Buttons()

# Initialize rotary encoder
encoder = RotaryEncoder(board.D10, board.D9, pulses_per_detent=3)

# Initialize NeoPixel status LED
neopixel_status = NeoPixelStatus(pin=board.D8)

# Initialize BLE
ble = BLERadio()

print("BLE Client Ready")

connection = None
LEVEL_LENGTH = 10
LEVEL1_LENGTH = 10
ADD_TIME = 2
MAX_LEVEL = 10  # Win after completing level 10

while True:
    # ===== CONNECTION PHASE =====
    neopixel_status.show_disconnected()  # Show red while not connected
    display_mgr.show_connection_screen()
    display_mgr.update_connection_status("Scanning...", "")
    print("Searching for BLE Server...")
    
    connection = None
    
    # Scan for devices
    for advertisement in ble.start_scan(ProvideServicesAdvertisement, timeout=10):
        if UARTService in advertisement.services:
            print("Found server! Connecting...")
            display_mgr.update_connection_status("Connecting...", "")
            try:
                connection = ble.connect(advertisement)
                print(f"Connection established: {connection.connected}")
                break
            except Exception as e:
                print(f"Connection failed: {e}")
                connection = None
    
    ble.stop_scan()
    
    if connection and connection.connected:
        print("Connected!")
        neopixel_status.show_connected()  # Show green when connected
        display_mgr.update_connection_status("Connected!", "Initializing...")
        time.sleep(1)
        uart = connection[UARTService]
        
        # ===== MAIN GAME SESSION LOOP =====
        session_active = True
        
        while connection.connected and session_active:
            
            # ===== MENU PHASE =====
            display_mgr.show_menu_screen()
            menu_active = True
            encoder.reset(to_detent=0)
            
            while connection.connected and menu_active:
                # Update encoder and check for rotation
                if encoder.update():
                    delta = encoder.get_delta()
                    
                    if delta > 0:
                        for _ in range(abs(delta)):
                            display_mgr.menu_move_down()
                        print(f"Selected: {display_mgr.get_difficulty_name()}")
                
                # Check for RIGHT button to confirm selection
                button_pressed = buttons.get_pressed_button()
                
                if button_pressed == "RIGHT":
                    selected_difficulty = display_mgr.get_difficulty_name()
                    print(f"Starting game on {selected_difficulty} mode")
                    menu_active = False
                    while buttons.any_button_pressed():
                        time.sleep(0.01)
                    time.sleep(0.1)
                
                time.sleep(0.001)
            
            if not connection.connected:
                break
            
            # ===== GAME PHASE =====
            game_level = 1
            display_mgr.show_game_screen()
            display_mgr.update_level(game_level)
            print(f"Game started! Difficulty: {display_mgr.get_difficulty_name()}")
            
            # Send difficulty to server
            difficulty_msg = f"LEVEL:{str(game_level)}:{display_mgr.get_difficulty_name()}\n"
            uart.write(difficulty_msg.encode('utf-8'))
            print(f"Sent: {difficulty_msg.strip()}")
            
            game_start = time.monotonic()
            print(f"Level {game_level} started at: {game_start}")
            
            # Main game loop
            game_running = True
            
            while connection.connected and game_running:
                
                # ===== PLAYING =====
                if display_mgr.is_game_screen():
                    time_left = LEVEL_LENGTH - (time.monotonic() - game_start)
                    
                    # Level complete
                    if time_left <= 0:
                        # Check if player won (completed level 10)
                        if game_level >= MAX_LEVEL:
                            display_mgr.show_game_win_screen()
                            message = "STOP\n"
                            uart.write(message.encode('utf-8'))
                            print("Game completed! Player wins!")
                            continue
                        
                        # Otherwise, go to next level
                        game_level += 1
                        display_mgr.show_transition_screen(game_level)
                        message = "STOP\n"
                        uart.write(message.encode('utf-8'))
                        print(f"Level {game_level - 1} complete!")
                        continue  # Skip to next iteration to handle transition
                    
                    display_mgr.update_timer(int(time_left))
                    
                    # Check for incoming messages from server (e.g., DEAD)
                    if uart.in_waiting:
                        data = uart.read(uart.in_waiting)
                        if data:
                            received = data.decode('utf-8').strip()
                            print(f"Received (unsolicited): {received}")
                            
                            if "DEAD" in received:
                                reason = "Scrappy Died!"
                                display_mgr.show_game_over_screen(reason)
                                print(f"Game Over: {reason}")
                                continue
                    
                    # Check for player input
                    message = None
                    shake = accelerometer.detect_z_shake(time.monotonic())
                    
                    if shake:
                        message = "MANUAL\n"
                        display_mgr.update_command("Sent: MANUAL")
                    else:
                        button_pressed = buttons.get_pressed_button()
                        if button_pressed:
                            message = f"{button_pressed}\n"
                            display_mgr.update_command(f"Sent: {button_pressed}")
                    
                    if message:
                        uart.write(message.encode('utf-8'))
                        print(f"Sent: {message.strip()}")
                        
                        display_mgr.update_response("Waiting...")
                        response_received = False
                        response_timeout = time.monotonic() + 2  # 2 second timeout
                        
                        while connection.connected and not response_received and time.monotonic() < response_timeout:
                            if uart.in_waiting:
                                data = uart.read(uart.in_waiting)
                                if data:
                                    received = data.decode('utf-8').strip()
                                    print(f"Received: {received}")
                                    
                                    if "DEAD" in received:
                                        reason = "Scrappy Died!"
                                        display_mgr.show_game_over_screen(reason)
                                        LEVEL_LENGTH = LEVEL1_LENGTH
                                        print(f"Game Over: {reason}")
                                        # Don't set game_running = False here either
                                    else:
                                        display_mgr.update_response("ACK OK!")
                                    
                                    response_received = True
                        
                        if not response_received:
                            display_mgr.update_response("Timeout")
                            print("Warning: No response from server")
                        
                        time.sleep(0.1)
                        display_mgr.update_response("")

                
                # ===== LEVEL TRANSITION =====
                elif display_mgr.is_transition_screen():
                    time.sleep(2)
                    
                    LEVEL_LENGTH += ADD_TIME
                    # Clear pending data
                    if uart.in_waiting:
                        uart.read(uart.in_waiting)
                    
                    # Send new level info
                    message = f"LEVEL:{str(game_level)}:{display_mgr.get_difficulty_name()}\n"
                    uart.write(message.encode('utf-8'))
                    print(f"Sent: {message.strip()}")
                    
                    # Wait for ACK
                    response_received = False
                    timeout = time.monotonic() + 5
                    
                    while connection.connected and not response_received and time.monotonic() < timeout:
                        if uart.in_waiting:
                            data = uart.read(uart.in_waiting)
                            if data:
                                received = data.decode('utf-8').strip()
                                print(f"Level ACK: {received}")
                                response_received = True
                    
                    # Return to game and reset timer
                    display_mgr.show_game_screen()
                    display_mgr.update_level(game_level)
                    game_start = time.monotonic()
                    print(f"Level {game_level} started at: {game_start}")
                
                # ===== GAME OVER =====
                elif display_mgr.is_game_over_screen():
                    print("Waiting for shake to restart...")
                    LEVEL_LENGTH = LEVEL1_LENGTH
                    if accelerometer.detect_z_shake(time.monotonic()):
                        print("Restarting game...")
                        game_running = False  # Exit game loop, return to menu
                
                # ===== GAME WIN =====
                elif display_mgr.is_game_win_screen():
                    print("Waiting for shake to return to menu...")
                    LEVEL_LENGTH = LEVEL1_LENGTH
                    if accelerometer.detect_z_shake(time.monotonic()):
                        print("Returning to menu...")
                        game_running = False  # Exit game loop, return to menu
                
                time.sleep(0.01)
            
            # If connection lost during game, exit session
            if not connection.connected:
                session_active = False
        
        print("Disconnected from server")
        neopixel_status.show_disconnected()  # Show red when disconnected
        display_mgr.update_connection_status("Disconnected", "")
        time.sleep(2)
    else:
        print("Server not found or connection failed")
        neopixel_status.show_disconnected()  # Show red when connection failed
        display_mgr.update_connection_status("Not found", "Retrying...")
        time.sleep(2)
