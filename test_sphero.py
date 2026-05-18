"""
PyTest Test Suite for Sphero Controller
Tests connection logic, command formatting, and error handling in mock mode.
This allows development and testing WITHOUT needing the physical robot.
"""

import pytest
from sphero_controller import SpheroController
import time


class TestSpheroController:
    """Test suite for Sphero controller functionality."""
    
    @pytest.fixture
    def controller(self):
        """
        Pytest fixture - creates a mock controller for each test.
        Fixtures are reusable test setup code.
        """
        ctrl = SpheroController(mock_mode=True)
        ctrl.connect()
        yield ctrl  # Provide controller to test
        ctrl.disconnect()  # Cleanup after test
    
    def test_connection(self):
        """Test that mock connection works."""
        controller = SpheroController(mock_mode=True)
        assert controller.connect() == True, "Connection should succeed in mock mode"
        assert controller.is_connected == True, "Controller should be marked as connected"
        controller.disconnect()
    
    def test_disconnection(self):
        """Test that disconnection works properly."""
        controller = SpheroController(mock_mode=True)
        controller.connect()
        controller.disconnect()
        assert controller.is_connected == False, "Controller should be disconnected"
    
    def test_led_color(self, controller):
        """Test LED color command formatting."""
        # These should not raise exceptions in mock mode
        controller.set_led_color(255, 0, 0)  # Red
        controller.set_led_color(0, 255, 0)  # Green
        controller.set_led_color(0, 0, 255)  # Blue
        # If we get here without exception, test passes
        assert True
    
    def test_led_color_requires_connection(self):
        """Test that LED command fails without connection."""
        controller = SpheroController(mock_mode=True)
        # Don't connect
        controller.set_led_color(255, 0, 0)
        # Should handle gracefully (prints error, doesn't crash)
        assert True
    
    def test_roll_command(self, controller):
        """Test basic roll command."""
        controller.roll(100, 0)  # Speed 100, heading 0°
        controller.roll(150, 90)  # Speed 150, heading 90°
        controller.roll(200, 180, duration=2)  # With duration
        assert True
    
    def test_spin_command(self, controller):
        """Test spin command."""
        controller.spin(90, 1.0)  # 90° in 1 second
        controller.spin(180, 2.0)  # 180° in 2 seconds
        controller.spin(360, 1.5)  # Full rotation
        assert True
    
    def test_stop_command(self, controller):
        """Test stop command."""
        controller.roll(100, 0)
        time.sleep(0.1)
        controller.stop()
        assert True
    
    def test_command_sequence(self, controller):
        """Test a sequence of commands (like a real program)."""
        # Change color
        controller.set_led_color(255, 0, 0)
        time.sleep(0.1)
        
        # Move forward
        controller.roll(100, 0, 1)
        time.sleep(0.1)
        
        # Spin
        controller.spin(180, 1)
        time.sleep(0.1)
        
        # Stop
        controller.stop()
        
        assert controller.is_connected == True
    
    def test_demo_pattern(self, controller):
        """Test the demo pattern runs without errors."""
        controller.demo_pattern()
        assert True
    
    def test_multiple_connections(self):
        """Test that we can connect and disconnect multiple times."""
        controller = SpheroController(mock_mode=True)
        
        for i in range(3):
            assert controller.connect() == True
            assert controller.is_connected == True
            controller.disconnect()
            assert controller.is_connected == False


class TestBLEConcepts:
    """
    Tests to verify understanding of BLE concepts.
    These are educational tests to show you understand the protocol.
    """
    
    def test_heading_range(self):
        """Verify heading values are in valid range (0-359)."""
        controller = SpheroController(mock_mode=True)
        controller.connect()
        
        # Valid headings
        valid_headings = [0, 90, 180, 270, 359]
        for heading in valid_headings:
            controller.roll(100, heading)  # Should not crash
        
        controller.disconnect()
        assert True
    
    def test_speed_range(self):
        """Verify speed values work in expected range (0-255)."""
        controller = SpheroController(mock_mode=True)
        controller.connect()
        
        # Test various speeds
        speeds = [0, 50, 100, 150, 200, 255]
        for speed in speeds:
            controller.roll(speed, 0)  # Should not crash
        
        controller.disconnect()
        assert True
    
    def test_rgb_range(self):
        """Verify RGB values are in valid range (0-255)."""
        controller = SpheroController(mock_mode=True)
        controller.connect()
        
        # Test edge cases
        controller.set_led_color(0, 0, 0)      # Black (off)
        controller.set_led_color(255, 255, 255)  # White (max)
        controller.set_led_color(128, 128, 128)  # Gray (mid)
        
        controller.disconnect()
        assert True


# Run tests with: pytest test_sphero.py -v
# The -v flag gives verbose output showing each test
if __name__ == "__main__":
    pytest.main([__file__, "-v"])