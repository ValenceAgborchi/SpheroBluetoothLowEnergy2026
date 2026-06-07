from spherov2 import scanner
from spherov2.sphero_edu import SpheroEduAPI
from spherov2.types import Color
import time
from typing import Optional


class SpheroController:

    def __init__(self, mock_mode: bool = False):
        self.mock_mode = mock_mode
        self.toy = None
        self.api = None
        self.is_connected = False
        self.current_color = None
        self.current_speed = None
        self.current_heading = None
        

    def connect(self, timeout: int = 10) -> bool:

        if self.mock_mode:
            print("[MOCK MODE] Simulating connection to Sphero...")
            self.is_connected = True
            return True
        
        try:
            print("Scanning for Sphero robots...")
            print("Make sure your Sphero is powered on and nearby!")
            
            self.toy = scanner.find_toy(timeout=timeout)
            
            if self.toy is None:
                print(" No Sphero found. Make sure it's on and not connected elsewhere.")
                return False
            
            print(f"✓ Found Sphero: {self.toy.name}")
            
         
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
    



    def set_led_color(self, red: int, green: int, blue: int):
     
        if not self.is_connected:
            print(" Not connected to Sphero")
            return
        
        self.current_color = (red, green, blue) 
        
        if self.mock_mode:
            print(f"[MOCK MODE] Setting LED to RGB({red}, {green}, {blue})")
            return
    


    def roll(self, speed: int, heading: int, duration: float = 0):
    
        if not self.is_connected:
            print(" Not connected to Sphero")
            return
        self.current_speed = speed
        self.current_heading = heading
        
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
        Sends speed=0 command to drive characteristic.
        """
        if not self.is_connected:
            print(" Not connected to Sphero")
            return
        self.current_speed = 0
        
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

        if not self.is_connected:
            print(" Not connected to Sphero")
            return
        
        print("\n Starting the demo pattern ")
        
        
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        for r, g, b in colors:
            self.set_led_color(r, g, b)
            time.sleep(0.5)
        

        print("Moving in a square pattern...")
        for heading in [0, 90, 180, 270]:
            self.roll(100, heading, 1.5)
            time.sleep(2)  # Roll for 1.5s + pause
        
     
        self.spin(360, 2)
        time.sleep(2)
        
   
        self.stop()
        self.set_led_color(128, 0, 128)
        print("✓ Demo complete!")


# Example usage
if __name__ == "__main__":
    # Test in mock mode first
    print("=== MOCK MODE TEST ===")
    controller = SpheroController(mock_mode=True)
    controller.connect()
    controller.set_led_color(255, 0, 0)
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