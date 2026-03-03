"""
Sphero Robot BLE Controller
Uses spherov2 library for educational BLE communication with Sphero robots.
This implementation allows both real robot control and mock mode for testing.
"""

from spherov2 import scanner
from spherov2.sphero_edu import SpheroEduAPI
from spherov2.types import Color
import time
from typing import Optional


class SpheroController:
    """
    Main controller class for Sphero robot.
    
    This class handles:
    - Connection to Sphero via Bluetooth Low Energy (BLE)
    - Basic movement commands (roll, spin, stop)
    - LED colour control
    - Error handling and connection management
    """
    
    def __init__(self, mock_mode: bool = False):
        """
        Initialize the Sphero controller.
        
        Args:
            mock_mode: If True, runs in test mode without real robot
        """
        self.mock_mode = mock_mode
        self.toy = None
        self.api = None
        self.is_connected = False
        
    def connect(self, timeout: int = 10) -> bool:
        """
        Connect to a Sphero robot via BLE.
        
        How it works:
        1. Scanner searches for BLE devices advertising Sphero services
        2. When found, establishes GATT connection
        3. Creates API wrapper for high-level commands
        
        Args:
            timeout: Seconds to wait for connection
            
        Returns:
            True if connected successfully, False otherwise
        """
        if self.mock_mode:
            print("[MOCK MODE] Simulating connection to Sphero...")
            self.is_connected = True
            return True
        
        try:
            print("Scanning for Sphero robots...")
            print("Make sure your Sphero is powered on and nearby!")
            
            # scanner.find_toy() uses bleak under the hood to:
            # - Scan for BLE advertisements
            # - Filter for Sphero-specific service UUIDs
            # - Return first matching device
            self.toy = scanner.find_toy(timeout=timeout)
            
            if self.toy is None:
                print(" No Sphero found. Make sure it's on and not connected elsewhere.")
                return False
            
            print(f"✓ Found Sphero: {self.toy.name}")
            
            # SpheroEduAPI wraps low-level BLE commands into easy functions
            # It handles the BLE protocol: writing to characteristics, etc.
            self.api = SpheroEduAPI(self.toy)
            self.api.__enter__()  # Initialize connection
            
            self.is_connected = True
            print("✓ Connected successfully!")
            
            # Wake up the robot (some Spheros start in sleep mode)
            self.set_led_color(0, 255, 0)  # Green = ready
            time.sleep(0.5)
            
            return True
            
        except Exception as e:
            print(f" Connection failed: {e}")
            return False
    
    def disconnect(self):
        """
        Safely disconnect from the Sphero.
        Always call this when done to free the BLE connection.
        """
        if self.mock_mode:
            print("[MOCK MODE] Simulating disconnect...")
            self.is_connected = False
            return
        
        try:
            if self.api:
                self.api.__exit__(None, None, None)
                self.api = None
            self.is_connected = False
            print("✓ Disconnected from Sphero")
        except Exception as e:
            print(f"⚠ Disconnect error: {e}")
    
    def set_led_colour(self, red: int, green: int, blue: int):
        """
        Set the main LED colour.
        
        BLE Explanation: This writes RGB values to the LED characteristic.
        The Sphero protocol expects values 0-255 for each colour channel.
        
        Args:
            red: Red value (0-255)
            green: Green value (0-255)
            blue: Blue value (0-255)
        """
        if not self.is_connected:
            print(" Not connected to Sphero")
            return
        
        if self.mock_mode:
            print(f"[MOCK MODE] Setting LED to RGB({red}, {green}, {blue})")
            return
        
        try:
            # Color() creates a color object that the API sends to the robot
            self.api.set_main_led(Color(red, green, blue))
            print(f"✓ LED set to RGB({red}, {green}, {blue})")
        except Exception as e:
            print(f" LED command failed: {e}")
    
    def roll(self, speed: int, heading: int, duration: float = 0):
        """
        Make the Sphero roll in a direction.
        
        BLE Explanation: This sends a drive command with:
        - Speed (0-255): How fast to move
        - Heading (0-359): Direction in degrees (0=forward, 90=right, etc.)
        - Duration: How long to roll (0 = until stopped)
        
        Args:
            speed: Speed from 0-255 (0=stop, 255=max)
            heading: Direction in degrees (0-359)
            duration: Seconds to roll (0 = indefinite)
        """
        if not self.is_connected:
            print(" Not connected to Sphero")
            return
        
        if self.mock_mode:
            print(f"[MOCK MODE] Rolling at speed {speed}, heading {heading}°")
            if duration > 0:
                print(f"[MOCK MODE] Rolling for {duration} seconds")
            return
        
        try:
            # Internally sends BLE command to drive characteristic
            self.api.roll(heading, speed, duration)
            print(f"✓ Rolling at speed {speed}, heading {heading}°")
        except Exception as e:
            print(f" Roll command failed: {e}")
    
    def spin(self, angle: int, duration: float = 1.0):
        """
        Spin the Sphero by a specific angle.
        
        Args:
            angle: Degrees to spin (positive = clockwise)
            duration: Seconds to complete the spin
        """
        if not self.is_connected:
            print(" Not connected to Sphero")
            return
        
        if self.mock_mode:
            print(f"[MOCK MODE] Spinning {angle}° over {duration}s")
            return
        
        try:
            self.api.spin(angle, duration)
            print(f"✓ Spinning {angle}°")
        except Exception as e:
            print(f" Spin command failed: {e}")
    
    def stop(self):
        """
        Stop all movement immediately.
        Sends speed=0 command to drive characteristic.
        """
        if not self.is_connected:
            print(" Not connected to Sphero")
            return
        
        if self.mock_mode:
            print("[MOCK MODE] Stopping movement")
            return
        
        try:
            # Roll with speed 0 = stop
            self.api.roll(0, 0, 0)
            print("✓ Stopped")
        except Exception as e:
            print(f" Stop command failed: {e}")
    
    def demo_pattern(self):
        """
        Run a demo pattern to show the robot is working.
        This is great for your professor demo!
        """
        if not self.is_connected:
            print(" Not connected to Sphero")
            return
        
        print("\n Starting the demo pattern..")
        
        # Flash colours
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        for r, g, b in colours:
            self.set_led_colour(r, g, b)
            time.sleep(0.5)
        
        # Move in a square
        print("Moving in a square pattern...")
        for heading in [0, 90, 180, 270]:
            self.roll(100, heading, 1.5)
            time.sleep(2)  # Roll for 1.5s + pause
        
        # Spin
        self.spin(360, 2)
        time.sleep(2)
        
        # Stop and set to purple
        self.stop()
        self.set_led_colour(128, 0, 128)
        print("✓ Demo complete!")


# Example usage
if __name__ == "__main__":
    # Test in mock mode first
    print("=== MOCK MODE TEST ===")
    controller = SpheroController(mock_mode=True)
    controller.connect()
    controller.set_led_colour(255, 0, 0)
    controller.roll(100, 0, 2)
    controller.spin(180, 1)
    controller.stop()
    controller.disconnect()
    
    print("\n=== READY===")
    print("To connect do the following instructions:")
    print("1. Turn the Sphero on")
    print("2. Run: controller = SpheroController(mock_mode=False)")
    print("3. Run: controller.connect()")
    print("4. Run: controller.demo_pattern()")