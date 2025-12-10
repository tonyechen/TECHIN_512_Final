import time
import random
import motor

class MovementController:
    """Class to handle random movement patterns for the robot"""
    
    # Difficulty settings
    DIFFICULTY_SETTINGS = {
        "EASY": {
            "speed_range": (55, 60),
            "duration_range": (0.2, 0.5),
            "pause_range": (1.5, 2.0)
        },
        "MEDIUM": {
            "speed_range": (60, 65),
            "duration_range": (0.4, 0.6),
            "pause_range": (0.0, 1.5)
        },
        "HARD": {
            "speed_range": (70, 75),
            "duration_range": (0.3, 1.0),
            "pause_range": (0.4, 0.5)
        }
    }
    
    def __init__(self):
        """Initialize the movement controller"""
        self.current_level = 0
        self.current_difficulty = "EASY"
        
        # Auto mode state tracking
        self.move_end_time = 0
        self.is_pausing = False
        
        print("MovementController initialized")
    
    def reset(self):
        """Reset the movement controller"""
        motor.stop()
        self.move_end_time = 0
        self.is_pausing = False
        print("MovementController reset")
    
    def set_level(self, level, difficulty):
        """Set game level and difficulty"""
        self.current_level = level
        self.current_difficulty = difficulty.upper()
        self.reset()
        print(f"Level set to {level} - {self.current_difficulty}")
    
    def get_random_move(self):
        """Generate a random movement command"""
        settings = self.DIFFICULTY_SETTINGS[self.current_difficulty]
        
        return {
            "direction": random.choice(["forward", "backward", "left", "right"]),
            "speed": random.randint(*settings["speed_range"]),
            "duration": random.uniform(*settings["duration_range"]),
            "pause": random.uniform(*settings["pause_range"])
        }
    
    def update_auto_mode(self):
        """Update auto mode movement (non-blocking)"""
        current_time = time.monotonic()
        
        # Check if current action finished
        if current_time < self.move_end_time:
            return 
        
        if self.is_pausing:
            # Pause finished, start new move
            move = self.get_random_move()
            
            # Execute motor command
            if move["direction"] == "forward":
                motor.forward(move["speed"])
            elif move["direction"] == "backward":
                motor.backward(move["speed"])
            elif move["direction"] == "left":
                motor.left(move["speed"])
            elif move["direction"] == "right":
                motor.right(move["speed"])
            
            self.move_end_time = current_time + move["duration"]
            self.is_pausing = False
            print(f"Auto: {move['direction']} @ {move['speed']}% for {move['duration']:.1f}s")
        
        else:
            # Move finished, start pause
            motor.stop()
            move = self.get_random_move()
            self.move_end_time = current_time + move["pause"]
            self.is_pausing = True
            print(f"Pausing for {move['pause']:.1f}s")
