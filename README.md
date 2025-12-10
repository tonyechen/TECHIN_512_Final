# Don't Let Scrappy Die! 🤖

A 90s-style handheld electronic game where you control a rebellious robot car named Scrappy who's determined to drive off the table. Your mission: keep Scrappy alive by countering his chaotic movements before time runs out!

## 🎮 How to Play

### Setup
1. Place Scrappy on the flat operating platform (3D printed table)
2. Turn on both the **Controller** and **Scrappy** (the robot car)
3. Wait for the NeoPixel on the controller to turn **green**
4. The OLED screen will display the connection status
5. Once connected, the main menu appears - Bluetooth connection established!

### Game Start
1. Use the **rotary encoder** to select difficulty (Easy, Medium, Hard)
2. Press the **right button** to begin the game
3. Keep Scrappy from driving off the table!

### Controls

| Button | Action | Description |
|--------|--------|-------------|
| **UP** | Forward | Prompt Scrappy to move forward |
| **DOWN** | Backward | Prompt Scrappy to move backward |
| **LEFT** | Turn Left | Prompt Scrappy to turn left |
| **RIGHT** | Turn Right | Prompt Scrappy to turn right |
| **SHAKE** (Accelerometer) | Manual Mode | Take full control for 5 seconds |

### Movement
- Scrappy will briefly in direction entered

### Manual Mode (Shake to Activate)
- **Duration:** 5 seconds of full control
- **Warning:** Scrappy will NOT automatically stop during manual mode
- **Strategy:** Use wisely! Once you input a command, Scrappy follows it continuously until you send a new command

### Game Progression
- **10 Levels Total**
- **Level 1:** 10 seconds
- **Each Additional Level:** +2 seconds (Level 10 = 28 seconds)
- Successfully keep Scrappy alive for the time limit to advance

### Difficulty Settings

| Difficulty | Behavior |
|------------|----------|
| **EASY** | Slow, predictable movements |
| **MEDIUM** | Moderate speed, unpredictable |
| **HARD** | Fast, chaotic, sudden changes |

Higher difficulty = more irrational behavior and sudden movements!

### Win/Lose Conditions
- **GAME OVER:** Scrappy drives off the table (detected by ADXL345 accelerometer)
- **WIN:** Complete all 10 levels without Scrappy falling
- Shake the controller to restart after Game Over (no power cycling needed!)

---

## 🔧 Components Used

### Controller (Handheld Device)
- **XIAO ESP32C3** - Main microcontroller with Bluetooth
- **SSD1306 OLED (128x64)** - Display for menus, levels, and status
- **Rotary Encoder** - Difficulty selection and menu navigation
- **ADXL345 Accelerometer** - Shake detection for manual mode activation
- **4x Tactile Buttons** - Directional controls (UP, DOWN, LEFT, RIGHT)
- **NeoPixel LEDs** - Status indicators (connection, game state, battery)
- **3.7V LiPo Battery** - Portable power supply
- **On/Off Switch** - Power control

### Scrappy (Robot Car)
- **Adafruit QT Py ESP32-S3** - Robot microcontroller with Bluetooth
- **L298N Motor Driver** - Dual H-bridge for motor control
- **2x DC Motors** - Drive system for movement
- **ADXL345 Accelerometer** - Impact/fall detection (death sensor)
- **9V Alkaline Battery** - Robot power supply
- **On/Off Switch** - Robot power control

## 💾 Software Requirements

### CircuitPython Version
- **CircuitPython 10+** (Both controller and Scrappy)

### Controller Libraries
```
lib/
├── adafruit_displayio_ssd1306    # OLED display driver
├── adafruit_display_text         # OLED display text
├── adafruit_ble/                 # Bluetooth Low Energy
├── adafruit_adxl34x.mpy          # ADXL345 accelerometer
├── adafruit_bus_device/          # I2C/SPI support
├── neopixel.mpy                  # NeoPixel LED control
└── rainbow.mpy
```

### Scrappy Libraries
```
lib/
├── adafruit_ble/                 # Bluetooth Low Energy
├── adafruit_adxl34x.mpy          # ADXL345 accelerometer
└── adafruit_bus_device/          # I2C support
```


## 🎯 Implementation Details

### Bluetooth Communication (BLE UART)
- **Protocol:** Nordic UART Service over Bluetooth Low Energy
- **Range:** ~10 meters
- **Messages:**
  - `LEVEL:X:DIFFICULTY` - Start game at level X with difficulty
  - `UP`, `DOWN`, `LEFT`, `RIGHT` - Movement commands
  - `MANUAL` - Activate 5-second manual mode
  - `STOP` - Stop Scrappy between levels and  after Game Over
- **Responses:**
  - `CONNECTED` - Initial connection established
  - `ACK` - Command received successfully
  - `DEAD` - Scrappy has fallen (Game Over)

### Accelerometer Calibration & Filtering
#### Controller (Shake Detection)
- **Calibration:** Zero-offset calibration on startup (50 samples)
- **Filtering:** z axis magnitude detection
- **Threshold:** Configurable shake sensitivity
- **Purpose:** Detect shake gesture for manual mode

#### Scrappy Robot (Fall Detection)
- **Calibration:** Zero-offset calibration on startup
- **Detection Method:** Z-axis monitoring for sudden drops
- **Threshold:** Adjustable threshold for fall detection sensitivity
- **Purpose:** Detect when Scrappy falls off the table

### Movement System
- **Random Behavior:** Algorithm generates random directions, speeds, and durations
- **Speed Ranges:**
  - Easy: 55-60% motor power
  - Medium: 60-65% motor power
  - Hard: 65-70% motor power
- **Counter-Steering:** Override Scrappy Auto Movements

### NeoPixel Indicators
| Color | Status |
|-------|--------|
| **Red** | Not connected |
| **Green** | Connected to Scrappy |

### Display States
1. **Splash Screen** - Game title and version
2. **Connection Screen** - Shows "BLE Client" status
3. **Main Menu** - Difficulty selection
4. **Level Screen** - Shows current level, difficulty, last command sent, and response status from Scrappy
5. **Game Over Screen** - "Scrappy Died!" with restart option
6. **Victory Screen** - "You Win!" with celebration and restart option

---

## 📦 Enclosure Design

### Controller Enclosure
**Design Philosophy:** Sci-fi inspired components with functional layout

**Layout:**
- **Top Surface:** OLED screen and control buttons
- **Side Mounted:** Rotary encoder for easy thumb access
- **Bottom Front:** On/Off switch
- **Bottom Access:** USB-C charging port slot

### Scrappy Robot Enclosure
**Design Philosophy:** Inspired by Perry the Platypus. Hat serves as the opening for the enclosure

**Layout:**
- **Bottom Back:** On/Off switch
- **Side Mounted**: Wheels for controlling movement
---

## 📁 Repository Structure

```
├── src/
│   ├── controller/
│   │   ├── code.py                 # Main controller program
│   │   ├── display.py              # OLED display management
│   │   ├── controls.py             # Button and rotary encoder handling
│   │   ├── accelerometer.py        # Shake detection
│   │   └── README.md               # Hardware and Software requirement
│   └── scrappy/
│       ├── code.py                 # Main robot program
│       ├── motor.py                # L298N motor control
│       ├── movement_patterns.py    # Random movement logic
│       ├── accelerometer.py        # Fall detection
│       └── README.md               # Hardware and Software requirement
├── Documentation/
│   ├── system_diagram.png          # Overall system architecture
│   ├── Scrappy.kicad_sch           # Circuit Diagram for Scrappy
│   └── Controller.kicad_sch        # Circuit Diagram for Controller
└── README.md                       # This file
```

---

## 🚀 Getting Started

### Software Installation
1. Install CircuitPython 10.0+ on both ESP32 boards
2. Copy all files from `src/controller/` to the controller's CIRCUITPY drive
3. Copy all files from `src/scrappy/` to Scrappy's CIRCUITPY drive
4. Ensure all required libraries are present in `lib/` for each microcontroller

### Hardware Assembly
1. Follow circuit diagrams in `Documentation/` folder
2. Connect components according to pin configuration above
3. Secure batteries with proper polarity
4. Test all connections before enclosing
5. Install firmware and test functionality
6. Assemble into enclosures

---

## 🎓 Educational Value

This project demonstrates:
- **Wireless Communication:** BLE UART protocol implementation
- **Sensor Fusion:** Accelerometer calibration and filtering
- **State Machine Design:** Game states and transitions
- **Real-Time Control:** Motor PWM control and response timing
- **User Interface:** OLED graphics and menu systems
- **Embedded Systems:** Power management, resource constraints
- **Mechanical Design:** Enclosure design and assembly
- **Version Control:** Git/GitHub workflow

---

## 🏆 Credits

**Project Type:** Final Project for Embedded Systems Course  
**Inspired By:** 90s handheld games (Bop It, Brain Warp)  
**Platform:** CircuitPython on ESP32  
**License:** MIT

**Special Thanks:**
- TECHIN 512 Teaching team for guidance and component provision
- Maker Space for tools and materials
- Adafruit for excellent CircuitPython libraries

---

## 📝 License

MIT License - Feel free to modify and share!

---

**Remember:** Scrappy wants to die. Don't let him. Good luck! 🎮🤖