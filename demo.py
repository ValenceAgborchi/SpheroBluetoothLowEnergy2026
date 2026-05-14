from sphero_controller import SpheroController
import time


def main():
    print("=" * 60)
    print("SPHERO BLE CONTROLLER DEMONSTRATION")
    print("=" * 60)
    print()
    
    # Create controller
    print("Initializing Sphero Controller...")
    controller = SpheroController(mock_mode=False)
    
    # Connect to Sphero
    print("\n🔍 Attempting to connect to Sphero via Bluetooth LE...")
    print("(Make sure your Sphero is turned on!)")
    
    if not controller.connect(timeout=15):
        print("\n Failed to connect. Troubleshooting tips:")
        print("   1. Is the Sphero powered on?")
        print("   2. Is Bluetooth enabled on this computer?")
        print("   3. Is the Sphero already connected to another device?")
        print("   4. Try restarting the Sphero")
        return
    
    print("\n✓ Connection successful!")
    input("\nPress ENTER to start the demonstration...")
    
    try:
        # Demo 1: LED Colour Control
        print("\n--- DEMO 1: LED Color Control ---")
        print("Cycling through colors to show BLE LED control...")
        
        colors = [
            ("Red", 255, 0, 0),
            ("Green", 0, 255, 0),
            ("Blue", 0, 0, 255),
            ("Yellow", 255, 255, 0),
            ("Purple", 128, 0, 128),
            ("Cyan", 0, 255, 255),
        ]
        
        for name, r, g, b in colors:
            print(f"   Setting color to {name}...")
            controller.set_led_color(r, g, b)
            time.sleep(1)
        
        input("\nPress ENTER to continue to movement demo...")
        
        # Demo 2: Basic Movement
        print("\n--- DEMO 2: Basic Movement ---")
        print("Testing directional control...")
        
        controller.set_led_color(0, 255, 0)  # Green for moving
        
        directions = [
            ("Forward", 0),
            ("Right", 90),
            ("Backward", 180),
            ("Left", 270),
        ]
        
        for direction, heading in directions:
            print(f"   Rolling {direction} (heading {heading}°)...")
            controller.roll(80, heading, 1.5)  # Speed 80, duration 1.5s
            time.sleep(2.5)  # Wait for movement to complete + pause
        
        controller.stop()
        print("   Stopped.")
        
        input("\nPress ENTER to continue to spin demo...")
        
        # Demo 3: Spinning
        print("\n--- DEMO 3: Rotation Control ---")
        controller.set_led_color(255, 165, 0)  # Orange for spinning
        
        spins = [90, 180, 360]
        for angle in spins:
            print(f"   Spinning {angle}°...")
            controller.spin(angle, 1.5)
            time.sleep(2)
        
        input("\nPress ENTER for full demo pattern...")
        
        # Demo 4: Full Pattern
        print("\n--- DEMO 4: Complete Pattern ---")
        controller.demo_pattern()
        
        print("\n✨ Demonstration complete!")
        
    except KeyboardInterrupt:
        print("\n\n⚠ Demo interrupted by user")
    except Exception as e:
        print(f"\n Error during demo: {e}")
    finally:
        # Always disconnect
        print("\n Disconnecting from Sphero...")
        controller.stop()
        controller.set_led_color(255, 0, 0)  # Red = done
        time.sleep(0.5)
        controller.disconnect()
        print("✓ Disconnected successfully")
    
    print("\n" + "=" * 60)
    print("Thank you for watching the demonstration!")
    print("=" * 60)


if __name__ == "__main__":
    # Quick test mode check
    import sys
    
    if "--test" in sys.argv:
        print("Running in MOCK TEST MODE (no real robot needed)")
        print("=" * 60)
        controller = SpheroController(mock_mode=True)
        controller.connect()
        controller.demo_pattern()
        controller.disconnect()
        print("\n✓ Mock test completed successfully!")
    else:
        main()
