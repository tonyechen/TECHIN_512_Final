import board
import busio
import adafruit_adxl34x

class Accelerometer:
    """Handle accelerometer input and shake detection along Z-axis"""
    
    def __init__(self, i2c=None, shake_threshold=15.0, cooldown_time=0.5):
        """
        Initialize the accelerometer
        
        Args:
            shake_threshold: Acceleration threshold in m/s² to detect shake (default 15.0)
            cooldown_time: Minimum time between shake detections in seconds (default 0.5)
        """
        # Setup I2C for accelerometer
        if i2c:
            self.i2c = i2c
        else:
            self.i2c = busio.I2C(board.SCL, board.SDA)
        self.accelerometer = adafruit_adxl34x.ADXL345(self.i2c)
        
        self.shake_threshold = shake_threshold
        self.cooldown_time = cooldown_time
        self.last_shake_time = 0
        self.baseline_z = None
        self.calibration_samples = []
        
    def calibrate(self, num_samples=10):
        """
        Calibrate by taking multiple readings to establish baseline Z-axis value
        Call this when device is at rest
        
        Args:
            num_samples: Number of samples to average for baseline (default 10)
        """
        import time
        self.calibration_samples = []
        
        for _ in range(num_samples):
            x, y, z = self.accelerometer.acceleration
            self.calibration_samples.append(z)
            time.sleep(0.01)
        
        self.baseline_z = sum(self.calibration_samples) / len(self.calibration_samples)
        print(f"Calibrated baseline Z: {self.baseline_z:.2f} m/s²")
    
    def get_acceleration(self):
        """
        Get current acceleration values
        
        Returns:
            Tuple of (x, y, z) acceleration in m/s²
        """
        return self.accelerometer.acceleration
    
    def detect_z_shake(self, current_time):
        """
        Detect shake along Z-axis
        
        Args:
            current_time: Current time in seconds (from time.monotonic())
            
        Returns:
            True if shake detected, False otherwise
        """
        # Check cooldown period
        if current_time - self.last_shake_time < self.cooldown_time:
            return False
        
        x, y, z = self.accelerometer.acceleration
        
        # If not calibrated, use standard gravity as baseline
        if self.baseline_z is None:
            self.baseline_z = 9.8
        
        # Calculate deviation from baseline
        z_deviation = abs(z - self.baseline_z)
        
        # Check if deviation exceeds threshold
        if z_deviation > self.shake_threshold:
            self.last_shake_time = current_time
            print(f"Shake detected! Z deviation: {z_deviation:.2f} m/s²")
            return True
        
        return False
    
    def get_z_deviation(self):
        """
        Get current Z-axis deviation from baseline
        
        Returns:
            Absolute deviation from baseline in m/s²
        """
        if self.baseline_z is None:
            self.baseline_z = 9.8
        
        x, y, z = self.accelerometer.acceleration
        return abs(z - self.baseline_z)