"""
Joystick Controller for Sphero
Reads input from any gamepad (PS5, Xbox, generic USB) using pygame
and translates stick movements into Sphero roll commands.

Works with real robot or mock mode for testing without hardware.
"""

import pygame
import math
import time
from sphero_controller import SpheroController


# --- CONFIGURATION ---
SPEED_MAX = 150        # Max speed sent to Sphero (0-255), 150 is safe indoors
DEADZONE = 0.15        # Ignore stick movements smaller than this (stops drift)
LOOP_DELAY = 0.05      # How often we check the controller (every 50ms = 20x/sec)


def init_joystick():
    """
    Initialize pygame and find the first connected controller.
    
    pygame.joystick handles all controller types the same way —
    PS5, Xbox, or generic USB all appear as a 'joystick' with axes and buttons.
    
    Returns the joystick object, or None if no controller found.
    """
    pygame.init()
    pygame.joystick.init()

    count = pygame.joystick.get_count()
    print(f"Found {count} controller(s)")

    if count == 0:
        print("No controller found. Plug in your controller and try again.")
        return None

    joystick = pygame.joystick.Joystick(0)  # Use first controller found
    joystick.init()
    print(f"Using controller: {joystick.get_name()}")
    return joystick


def get_movement(joystick):
    """
    Read the left analog stick and convert to speed + heading.
    
    The math:
    - atan2(x, -y) gives us the angle in radians from stick position
    - We convert radians to degrees (0-359) for Sphero heading
    - The stick's distance from center (magnitude) becomes speed  
    """
    # Read raw axis values (-1.0 to 1.0)
    x = joystick.get_axis(0)  # Left stick horizontal
    y = joystick.get_axis(1)  # Left stick vertical

    # Apply deadzone — ignore tiny movements (controller drift)
    if abs(x) < DEADZONE and abs(y) < DEADZONE:
        return 0, 0

    # Calculate heading (direction) in degrees
    angle_rad = math.atan2(x, -y)          # Get angle in radians
    heading = math.degrees(angle_rad)       # Convert to degrees
    if heading < 0:
        heading += 360                       # Keep it 0-359

    # Calculate speed from how far the stick is pushed
    magnitude = math.sqrt(x**2 + y**2)     # Distance from center (0.0 to ~1.0)
    magnitude = min(magnitude, 1.0)         # Cap at 1.0
    speed = int(magnitude * SPEED_MAX)      # Scale to 0-SPEED_MAX
    return speed, int(heading)


def run_joystick_control(mock_mode=False):
    """
    Main control loop.
    
    This runs continuously, checking the controller 20 times per second.
    Each iteration:
    1. pygame processes new controller events
    2. We read the stick position
    3. We send a roll command (or stop) to the Sphero
    4. We wait 50ms and repeat
    
    Press CTRL+C or the controller's Circle/B button to exit.
    """
    # Set up controller
    joystick = init_joystick()
    if joystick is None and not mock_mode:
        return

    # Connect to Sphero
    controller = SpheroController(mock_mode=mock_mode)
    if not controller.connect():
        print("Could not connect to Sphero.")
        pygame.quit()
        return

    controller.set_led_color(0, 255, 0)  # Green = ready
    print("\nController ready! Move left stick to drive.")
    print("Press CTRL+C to quit.\n")

    try:
        while True:
            # Tell pygame to process new events (required every loop)
            pygame.event.pump()

            # Check for quit button (Circle on PS5 = button 1)
            if joystick and joystick.get_button(1):
                print("Quit button pressed.")
                break
            # Get movement from stick
            if joystick:
                speed, heading = get_movement(joystick)
            else:
                # Mock mode without controller: simulate forward movement
                speed, heading = 100, 0

            # Send command to Sphero
            if speed > 0:
                controller.roll(speed, heading)
            else:
                controller.stop()
            time.sleep(LOOP_DELAY)
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        controller.stop()
        controller.set_led_color(255, 0, 0)  # Red = done
        controller.disconnect()
        pygame.quit()

# Run directly or import into GUI
if __name__ == "__main__":
    import sys
    mock = "--mock" in sys.argv
    run_joystick_control(mock_mode=mock)