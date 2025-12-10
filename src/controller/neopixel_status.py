import board
import neopixel

class NeoPixelStatus:
    """Manage NeoPixel status LED"""
    
    # Color constants
    COLOR_RED = (255, 0, 0)
    COLOR_GREEN = (0, 255, 0)
    
    def __init__(self, pin=board.D8, num_pixels=1, brightness=0.3):
        """
        Initialize NeoPixel
        
        Args:
            pin: Board pin for NeoPixel (default: board.D10)
            num_pixels: Number of pixels (default: 1)
            brightness: Brightness level 0.0-1.0 (default: 0.3)
        """
        self.pixels = neopixel.NeoPixel(pin, num_pixels, brightness=brightness, auto_write=False)
        self.show_disconnected()
    
    def show_disconnected(self):
        """Show red - not connected"""
        self.pixels.fill(self.COLOR_RED)
        self.pixels.show()
    
    def show_connected(self):
        """Show green - connected"""
        self.pixels.fill(self.COLOR_GREEN)
        self.pixels.show()

