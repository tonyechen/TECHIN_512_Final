import displayio
import terminalio
from adafruit_display_text import label
import adafruit_displayio_ssd1306

class DisplayManager:
    """Manage different screens for the game"""
    
    # Screen constants
    SCREEN_CONNECTION = 0
    SCREEN_MENU = 1
    SCREEN_GAME = 2
    SCREEN_GAME_OVER = 3
    SCREEN_LEVEL_TRANSITION = 4
    SCREEN_GAME_WIN = 5
    
    # Difficulty constants
    DIFFICULTY_EASY = 0
    DIFFICULTY_MEDIUM = 1
    DIFFICULTY_HARD = 2
    
    def __init__(self, display):
        self.display = display
        self.current_screen = self.SCREEN_CONNECTION
        self.selected_difficulty = self.DIFFICULTY_EASY
        self.current_level = 1
        self.game_over_reason = ""
        self.response = ""
        
        # Create groups for each screen
        self.connection_group = displayio.Group()
        self.menu_group = displayio.Group()
        self.game_group = displayio.Group()
        self.game_over_group = displayio.Group()
        self.transition_group = displayio.Group()
        self.game_win_group = displayio.Group()
        
        self._setup_connection_screen()
        self._setup_menu_screen()
        self._setup_game_screen()
        self._setup_game_over_screen()
        self._setup_transition_screen()
        self._setup_game_win_screen()
        
        # Show connection screen by default
        self.display.root_group = self.connection_group
    
    def _setup_connection_screen(self):
        """Setup BLE connection screen"""
        self.conn_title = label.Label(terminalio.FONT, text="BLE Client", x=30, y=10)
        self.conn_status = label.Label(terminalio.FONT, text="Scanning...", x=20, y=30)
        self.conn_detail = label.Label(terminalio.FONT, text="", x=10, y=50)
        
        self.connection_group.append(self.conn_title)
        self.connection_group.append(self.conn_status)
        self.connection_group.append(self.conn_detail)
    
    def _setup_menu_screen(self):
        """Setup difficulty selection menu"""
        self.menu_title = label.Label(terminalio.FONT, text="Select Difficulty", x=10, y=5)
        
        # Difficulty options
        self.easy_label = label.Label(terminalio.FONT, text="  EASY", x=20, y=25)
        self.medium_label = label.Label(terminalio.FONT, text="  MEDIUM", x=20, y=40)
        self.hard_label = label.Label(terminalio.FONT, text="  HARD", x=20, y=55)
        
        self.menu_group.append(self.menu_title)
        self.menu_group.append(self.easy_label)
        self.menu_group.append(self.medium_label)
        self.menu_group.append(self.hard_label)
    
    def _setup_game_screen(self):
        """Setup game play screen"""
        self.game_title = label.Label(terminalio.FONT, text="Playing", x=35, y=10)
        self.level_label = label.Label(terminalio.FONT, text="Level: 1", x=30, y=20)
        self.timer_label = label.Label(terminalio.FONT, text="Time: 30s", x=25, y=30)
        self.command_label = label.Label(terminalio.FONT, text="", x=10, y=40)
        self.response_label = label.Label(terminalio.FONT, text="", x=10, y=50)
        
        self.game_group.append(self.game_title)
        self.game_group.append(self.level_label)
        self.game_group.append(self.timer_label)
        self.game_group.append(self.command_label)
        self.game_group.append(self.response_label)
    
    def _setup_game_over_screen(self):
        """Setup game over screen"""
        self.gameover_title = label.Label(terminalio.FONT, text="GAME OVER", x=25, y=15)
        self.gameover_reason = label.Label(terminalio.FONT, text="", x=5, y=35, scale=1)
        self.gameover_instruction = label.Label(terminalio.FONT, text="Shake to restart", x=5, y=55)
        
        self.game_over_group.append(self.gameover_title)
        self.game_over_group.append(self.gameover_reason)
        self.game_over_group.append(self.gameover_instruction)
    
    def _setup_transition_screen(self):
        """Setup level transition screen"""
        self.transition_title = label.Label(terminalio.FONT, text="Level Passed!", x=20, y=20)
        self.transition_message = label.Label(terminalio.FONT, text="Starting next", x=18, y=35)
        self.transition_message2 = label.Label(terminalio.FONT, text=f"level {self.current_level}", x=35, y=48)
        
        self.transition_group.append(self.transition_title)
        self.transition_group.append(self.transition_message)
        self.transition_group.append(self.transition_message2)
    
    def _setup_game_win_screen(self):
        """Setup game win screen"""
        self.gamewin_title = label.Label(terminalio.FONT, text="YOU WIN!", x=30, y=15)
        self.gamewin_message = label.Label(terminalio.FONT, text="All levels", x=25, y=30)
        self.gamewin_message2 = label.Label(terminalio.FONT, text="completed!", x=25, y=42)
        self.gamewin_instruction = label.Label(terminalio.FONT, text="Shake to restart", x=5, y=55)
        
        self.game_win_group.append(self.gamewin_title)
        self.game_win_group.append(self.gamewin_message)
        self.game_win_group.append(self.gamewin_message2)
        self.game_win_group.append(self.gamewin_instruction)
    
    # CONNECTION SCREEN METHODS
    def show_connection_screen(self):
        """Switch to connection screen"""
        self.current_screen = self.SCREEN_CONNECTION
        self.display.root_group = self.connection_group
    
    def update_connection_status(self, status, detail=""):
        """Update connection screen text"""
        self.conn_status.text = status
        self.conn_detail.text = detail
    
    # MENU SCREEN METHODS
    def show_menu_screen(self):
        """Switch to menu screen"""
        self.current_screen = self.SCREEN_MENU
        self.selected_difficulty = self.DIFFICULTY_EASY
        self._update_menu_selection()
        self.display.root_group = self.menu_group
    
    def menu_move_down(self):
        """Move selection down in menu"""
        if self.selected_difficulty < 2:
            self.selected_difficulty += 1
        else:
            self.selected_difficulty = 0
        self._update_menu_selection()
    
    def _update_menu_selection(self):
        """Update menu to show current selection with '>' indicator"""
        # Reset all
        self.easy_label.text = "  EASY"
        self.medium_label.text = "  MEDIUM"
        self.hard_label.text = "  HARD"
        
        # Highlight selected
        if self.selected_difficulty == self.DIFFICULTY_EASY:
            self.easy_label.text = "> EASY"
        elif self.selected_difficulty == self.DIFFICULTY_MEDIUM:
            self.medium_label.text = "> MEDIUM"
        elif self.selected_difficulty == self.DIFFICULTY_HARD:
            self.hard_label.text = "> HARD"
    
    def get_selected_difficulty(self):
        """Get currently selected difficulty"""
        return self.selected_difficulty
    
    def get_difficulty_name(self):
        """Get name of selected difficulty"""
        if self.selected_difficulty == self.DIFFICULTY_EASY:
            return "EASY"
        elif self.selected_difficulty == self.DIFFICULTY_MEDIUM:
            return "MEDIUM"
        else:
            return "HARD"
    
    # GAME SCREEN METHODS
    def show_game_screen(self):
        """Switch to game screen"""
        self.current_screen = self.SCREEN_GAME
        self.display.root_group = self.game_group
    
    def update_response(self, text):
        self.response_label.text = text
    
    def update_level(self, level):
        """Update the level display"""
        self.current_level = level
        self.level_label.text = f"Level: {self.current_level}"
    
    def update_timer(self, seconds_left):
        """Update the timer display"""
        self.timer_label.text = f"Time: {seconds_left}s"
    
    def update_command(self, command_text):
        """Update command label on game screen"""
        self.command_label.text = command_text
    
    # GAME OVER SCREEN METHODS
    def show_game_over_screen(self, reason=""):
        """Switch to game over screen"""
        self.current_screen = self.SCREEN_GAME_OVER
        self.game_over_reason = reason
        # Wrap text if too long
        if len(reason) > 20:
            # Split into two lines
            words = reason.split()
            line1 = ""
            line2 = ""
            for word in words:
                if len(line1) + len(word) < 20:
                    line1 += word + " "
                else:
                    line2 += word + " "
            self.gameover_reason.text = line1.strip() + "\n" + line2.strip()
        else:
            self.gameover_reason.text = reason
        self.display.root_group = self.game_over_group
    
    # TRANSITION SCREEN METHODS
    def show_transition_screen(self, level):
        """Switch to level transition screen"""
        self.current_level = level
        self.current_screen = self.SCREEN_LEVEL_TRANSITION
        # Update the level number text dynamically
        self.transition_message2.text = f"level {self.current_level}"
        self.display.root_group = self.transition_group
    
    # GAME WIN SCREEN METHODS
    def show_game_win_screen(self):
        """Switch to game win screen"""
        self.current_screen = self.SCREEN_GAME_WIN
        self.display.root_group = self.game_win_group
    
    # UTILITY METHODS
    def get_current_screen(self):
        """Get current screen constant"""
        return self.current_screen
    
    def is_menu_screen(self):
        """Check if currently on menu screen"""
        return self.current_screen == self.SCREEN_MENU
    
    def is_game_screen(self):
        """Check if currently on game screen"""
        return self.current_screen == self.SCREEN_GAME
    
    def is_game_over_screen(self):
        """Check if currently on game over screen"""
        return self.current_screen == self.SCREEN_GAME_OVER
    
    def is_transition_screen(self):
        """Check if currently on transition screen"""
        return self.current_screen == self.SCREEN_LEVEL_TRANSITION
    
    def is_game_win_screen(self):
        """Check if currently on game win screen"""
        return self.current_screen == self.SCREEN_GAME_WIN
