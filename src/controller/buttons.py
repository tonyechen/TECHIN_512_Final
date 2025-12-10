import board
import digitalio

class Buttons:
    """Handle button inputs with pull-up resistors"""
    
    def __init__(self):
        # Setup buttons with pull-up resistors
        self.button_right = digitalio.DigitalInOut(board.D0)
        self.button_right.direction = digitalio.Direction.INPUT
        self.button_right.pull = digitalio.Pull.UP
        
        self.button_left = digitalio.DigitalInOut(board.D1)
        self.button_left.direction = digitalio.Direction.INPUT
        self.button_left.pull = digitalio.Pull.UP
        
        self.button_down = digitalio.DigitalInOut(board.D2)
        self.button_down.direction = digitalio.Direction.INPUT
        self.button_down.pull = digitalio.Pull.UP
        
        self.button_up = digitalio.DigitalInOut(board.D3)
        self.button_up.direction = digitalio.Direction.INPUT
        self.button_up.pull = digitalio.Pull.UP
    
    def get_pressed_button(self):
        """
        Check which button is pressed and return the string.
        Returns None if no button is pressed.
        Note: LOW = pressed with pull-up resistors
        """
        if not self.button_right.value:
            return "RIGHT"
        elif not self.button_left.value:
            return "LEFT"
        elif not self.button_down.value:
            return "DOWN"
        elif not self.button_up.value:
            return "UP"
        return None
    
    def any_button_pressed(self):
        """Check if any button is currently pressed"""
        return (not self.button_right.value or 
                not self.button_left.value or 
                not self.button_down.value or 
                not self.button_up.value)
