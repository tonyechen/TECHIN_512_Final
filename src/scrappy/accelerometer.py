import board
import time
import adafruit_adxl34x
import math

class AccelerometerMonitor:
    """Class to handle accelerometer-based impact detection"""
    
    # thresholds for fall detection
    Z_AXIS_FALL_THRESHOLD = 12  # Z-axis deviation when tipping over
    SUSTAINED_IMPACT_TIME = 0.1  # Impact must last this long (100ms)
    
    def __init__(self):
        """Initialize the accelerometer monitor"""
        # Initialize I2C and accelerometer
        i2c = board.I2C()
        self.accelerometer = adafruit_adxl34x.ADXL345(i2c)
        
        # Calibration offsets
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.offset_z = 0.0
        
        # Robot state
        self._is_alive = True
        self.last_magnitude = 0.0
        
        # Fall detection
        self.impact_start_time = None
        
        print("AccelerometerMonitor initialized")
    
    def calibrate(self, samples=50):
        """
        Perform zero offset calibration
        Robot should be stationary during calibration
        """
        print("Starting accelerometer calibration...")
        print("Keep robot stationary!")
        time.sleep(1)
        
        sum_x = 0.0
        sum_y = 0.0
        sum_z = 0.0
        
        for i in range(samples):
            x, y, z = self.accelerometer.acceleration
            sum_x += x
            sum_y += y
            sum_z += z
            time.sleep(0.02)  # 20ms between samples
            
            if i % 10 == 0:
                print(f"Calibrating... {i}/{samples}")
        
        # Calculate average offsets
        self.offset_x = sum_x / samples
        self.offset_y = sum_y / samples
        self.offset_z = (sum_z / samples)
        
        print(f"Calibration complete!")
        print(f"Offsets: X={self.offset_x:.2f}, Y={self.offset_y:.2f}, Z={self.offset_z:.2f}")
    
    def get_calibrated_acceleration(self):
        """
        Get calibrated acceleration values
        Returns: (x, y, z) in m/s^2
        """
        x, y, z = self.accelerometer.acceleration
        return (
            x - self.offset_x,
            y - self.offset_y,
            z - self.offset_z
        )
    
    def calculate_magnitude(self, x, y, z):
        """
        Calculate magnitude of acceleration vector
        magnitude = sqrt(x^2 + y^2 + z^2)
        """
        return math.sqrt(x*x + y*y + z*z)
    
    def check_impact(self):
        """
        Read accelerometer and check for fall/impact
        Returns: True if impact detected, False otherwise
        """        
        # Get calibrated readings (already has gravity removed)
        x, y, z = self.get_calibrated_acceleration()
        
        # Check for fall: Z-axis changes significantly from 0
        is_tipped = abs(z) > self.Z_AXIS_FALL_THRESHOLD
        if is_tipped:
            print(f"Z magnitiude: {str(abs(z))}")
        return is_tipped
    
    def is_alive(self):
        """Returns the current alive status"""
        return self._is_alive
    
    def reset(self):
        """Reset robot to alive state"""
        self._is_alive = True
        self.impact_start_time = None
        print("Accelerometer status reset - Robot is ALIVE")
    
    def get_status(self):
        """Returns the current robot status"""
        return {
            "alive": self._is_alive,
            "last_magnitude": self.last_magnitude,
        }