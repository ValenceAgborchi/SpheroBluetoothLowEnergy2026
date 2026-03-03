# Sphero BLE Robot Controller

A Python-based wireless controller for Sphero robots using Bluetooth Low Energy (BLE) protocol.

## Overview

This project demonstrates wireless hardware control using the BLE GATT protocol. Built as an exploration of how wireless medical devices and research equipment communicate, this controller manages LED colors, directional movement, and rotation commands for Sphero robots.

**Key Features:**
- Wireless BLE communication using GATT protocol
- LED color control (RGB)
- Directional movement with speed and heading parameters
- Rotation control with angle-based precision
- Mock mode for hardware-independent testing
- 13 automated tests with PyTest

## Technical Stack

- **Language:** Python 3.13
- **BLE Library:** bleak (cross-platform Bluetooth Low Energy)
- **Sphero API:** spherov2 (educational library from UPenn)
- **Testing:** PyTest
- **Protocol:** BLE GATT (Generic Attribute Profile)

## Project Structure
```
sphero-ble-controller/
├── sphero_controller.py    # Main controller class
├── test_sphero.py          # PyTest test suite (13 tests)
├── demo.py                 # Interactive demonstration script
└── README.md              # This file
```

## Installation

### Prerequisites
- Python 3.7 or higher
- Bluetooth-enabled device (Mac, Windows, or Linux)
- Sphero robot (Mini, BOLT, RVR, etc.)

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/sphero-ble-controller.git
cd sphero-ble-controller
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate  # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

## Usage

### Quick Start (Automated Demo)
```bash
# Turn on your Sphero first!
python demo.py
```

This runs a pre-programmed demonstration:
- LED color cycling (Red → Green → Blue → Yellow → Purple → Cyan)
- Square movement pattern
- Rotation demonstrations

### Interactive Control
```bash
python -i sphero_controller.py
```

Then in the Python prompt:
```python
# Create controller
controller = SpheroController(mock_mode=False)

# Connect to Sphero
controller.connect()

# Control LED color (RGB: 0-255)
controller.set_led_color(255, 0, 0)    # Red
controller.set_led_color(0, 255, 0)    # Green
controller.set_led_color(0, 0, 255)    # Blue

# Movement (speed: 0-255, heading: 0-359°, duration: seconds)
controller.roll(100, 0, 2)      # Forward at medium speed for 2 seconds
controller.roll(150, 90, 2)     # Right at higher speed
controller.roll(100, 180, 2)    # Backward

# Rotation (angle: degrees, duration: seconds)
controller.spin(90, 1)          # Quarter turn
controller.spin(360, 2)         # Full rotation

# Stop
controller.stop()

# Disconnect when done
controller.disconnect()
```

### Mock Mode (Testing Without Hardware)
```bash
python -i sphero_controller.py
```
```python
# Test your code without physical robot
controller = SpheroController(mock_mode=True)
controller.connect()
controller.set_led_color(255, 0, 0)  # Prints mock output
controller.roll(100, 0, 2)           # Simulates movement
```

## Testing

Run the automated test suite:
```bash
# All tests
pytest test_sphero.py -v

# Specific test
pytest test_sphero.py::TestSpheroController::test_connection -v
```

**Test Coverage:**
- Connection/disconnection logic
- LED color control
- Movement commands (roll, spin, stop)
- Command sequencing
- Error handling
- Parameter validation (speed, heading, RGB ranges)

All tests run in mock mode (no hardware required).

## How It Works

### BLE GATT Protocol

Bluetooth Low Energy uses the GATT (Generic Attribute Profile) structure:

**Structure:**
```
Sphero Device
├── Services (functional groups)
│   ├── LED Service
│   │   └── RGB Characteristic (write color values here)
│   └── Motor Service
│       ├── Speed Characteristic
│       └── Heading Characteristic
```

**Communication Flow:**
```
Python Code
    ↓
spherov2 library (formats commands for Sphero protocol)
    ↓
bleak library (BLE GATT operations)
    ↓
Bluetooth Radio (2.4 GHz wireless transmission)
    ↓
Sphero Device (receives and executes)
```

### Key Concepts

**Services:** Groups of related characteristics (e.g., LED Service, Motor Service)

**Characteristics:** Specific data points you can read/write (e.g., RGB color values, motor speed)

**UUIDs:** Unique identifiers for each service/characteristic (allows precise targeting)

**Command Latency:** ~50-100ms from code execution to robot response

## Code Architecture

### SpheroController Class
```python
class SpheroController:
    def __init__(self, mock_mode=False)
        # Initialize controller with optional mock mode
    
    def connect(self, timeout=10) -> bool
        # Scan for BLE devices and establish connection
        # Returns True if successful
    
    def disconnect()
        # Safely close BLE connection
    
    def set_led_color(red, green, blue)
        # Control LED: RGB values 0-255
    
    def roll(speed, heading, duration=0)
        # Movement control
        # speed: 0-255 (0=stop, 255=max)
        # heading: 0-359° (0=forward, 90=right, 180=back, 270=left)
        # duration: seconds (0=indefinite)
    
    def spin(angle, duration=1.0)
        # Rotation control
        # angle: degrees to rotate
        # duration: time to complete rotation
    
    def stop()
        # Stop all movement immediately
    
    def demo_pattern()
        # Execute pre-programmed demonstration
```

### Design Decisions

**Why Mock Mode?**
- Enables testing without physical hardware
- Faster development iteration
- Professional practice for embedded systems development

**Why spherov2?**
- Educational library from UPenn's AI course
- Abstracts complex BLE protocol details
- Handles Sphero-specific UUIDs and byte formatting
- Cross-platform (Mac, Windows, Linux)

**Why PyTest?**
- Industry-standard testing framework
- Clear test structure with fixtures
- Easy to extend with new test cases

## Troubleshooting

### "No Sphero found"
- Ensure Sphero is powered on (double-tap to wake)
- Check Bluetooth is enabled on your computer
- Disconnect Sphero from phone/other devices
- Move closer to computer (within 10 feet)

### "Connection failed"
- Restart Sphero (place in charger, remove)
- Restart Bluetooth on computer
- Try increasing timeout: `controller.connect(timeout=30)`
- On Mac: Check System Settings → Privacy & Security → Bluetooth permissions

### Import Errors
- Ensure virtual environment is activated: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

## What I Learned

### Technical Skills
- **BLE GATT Protocol:** Understanding services, characteristics, and UUID-based communication
- **Wireless Communication:** Real-time command execution and latency considerations
- **Hardware-Software Integration:** Bridging software commands to physical hardware responses
- **Test-Driven Development:** Mock testing for hardware-independent development

### Key Insights
1. **Mock mode is essential** for hardware projects - saved hours of debugging time
2. **BLE communication is asynchronous** - proper error handling is critical
3. **Protocol abstraction matters** - spherov2 saved me from writing low-level BLE code
4. **Real-world hardware is finicky** - connection timeouts, interference, power management

### Applications
This same BLE GATT protocol is used in:
- Neural recording devices
- Brain-computer interfaces (BCIs)
- Medical implants (pacemakers, insulin pumps)
- Wireless lab sensors
- Fitness trackers and wearables

Understanding BLE is foundational for working with modern wireless medical and research equipment.

## Future Enhancements

- [ ] Read sensor data (accelerometer, gyroscope, velocity)
- [ ] Autonomous navigation with obstacle avoidance
- [ ] Multi-robot coordination (control multiple Spheros)
- [ ] Voice/gesture control interface
- [ ] Data logging and visualization
- [ ] Custom movement patterns and choreography

## Resources

- [Sphero API Documentation](https://sdk.sphero.com/docs/api_spec/general_api/)
- [spherov2 Library (GitHub)](https://github.com/artificial-intelligence-class/spherov2.py)
- [bleak Documentation](https://bleak.readthedocs.io/)
- [BLE GATT Overview](https://learn.adafruit.com/introduction-to-bluetooth-low-energy)

## License

MIT License - feel free to use this code for learning and projects.

## Author

**Valence Agborchi**
- LinkedIn: www.linkedin.com/in/valenceagborchi
- GitHub: https://github.com/ValenceAgborchi
- Email: agbo7696@mylaurier.ca

## Acknowledgments

- spherov2 library by UPenn Artificial Intelligence Class
- bleak library for cross-platform BLE support

---

**Built as a learning project to understand wireless communication protocols used in neuroscience research equipment.**
