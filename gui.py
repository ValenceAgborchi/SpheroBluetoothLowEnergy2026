"""
Sphero Control GUI
A tkinter interface with two modes:
- Manual: PS5 controller (via HID) or WASD keyboard control in real time
- Auto: runs a preset sequence of commands
 
Imports SpheroController from sphero_controller.py
Uses 'hid' library for PS5 DualSense controller over USB
"""
 
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import math
import sys
 
from sphero_controller import SpheroController
 
# --- CONFIGURATION ---
SPEED_MAX = 150
DEADZONE = 0.15
LOOP_DELAY = 0.05
 
# PS5 DualSense USB IDs
PS5_VENDOR_ID  = 0x054C
PS5_PRODUCT_ID = 0x0CE6
 
 
class SpheroGUI:
    """
    Main GUI class.
 
    Structure:
    - __init__: builds the window and all widgets
    - connect/disconnect: manages Sphero BLE connection
    - start/stop manual: launches control loop in background thread
    - _read_gamepad: reads PS5 controller via HID in background thread
    - run_auto_sequence: runs preset commands in background thread
    - Keyboard methods: WASD fallback if no controller
    """
 
    def __init__(self, root, mock_mode=False):
        self.root = root
        self.root.title("Sphero BLE Controller")
        self.root.geometry("500x600")
        self.root.resizable(False, False)
 
        self.mock_mode = mock_mode
        self.controller = SpheroController(mock_mode=mock_mode)
 
        # State variables
        self.is_running = False
        self.control_thread = None
 
        # Keyboard state
        self.keys_held = set()
 
        # Gamepad state (updated by _read_gamepad thread)
        self._gamepad_x = 0.0
        self._gamepad_y = 0.0
        self._gamepad_thread_running = False
        self._hid_available = False
 
        self._build_ui()
        self._bind_keys()
 
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
 
    # -------------------------
    # UI CONSTRUCTION
    # -------------------------
 
    def _build_ui(self):
        tk.Label(
            self.root,
            text="Sphero BLE Controller",
            font=("Helvetica", 18, "bold")
        ).pack(pady=10)
 
        # --- Connection ---
        conn_frame = tk.LabelFrame(self.root, text="Connection", padx=10, pady=10)
        conn_frame.pack(fill="x", padx=20, pady=5)
 
        self.connect_btn = tk.Button(
            conn_frame, text="Connect to Sphero",
            command=self.connect, bg="#4CAF50", fg="white", width=20
        )
        self.connect_btn.grid(row=0, column=0, padx=5)
 
        self.disconnect_btn = tk.Button(
            conn_frame, text="Disconnect",
            command=self.disconnect, bg="#f44336", fg="white",
            width=20, state="disabled"
        )
        self.disconnect_btn.grid(row=0, column=1, padx=5)
 
        self.status_label = tk.Label(
            conn_frame, text="Status: Disconnected", fg="red"
        )
        self.status_label.grid(row=1, column=0, columnspan=2, pady=5)
 
        # --- LED Color ---
        led_frame = tk.LabelFrame(self.root, text="LED Color", padx=10, pady=10)
        led_frame.pack(fill="x", padx=20, pady=5)
 
        colors = [
            ("Red", 255, 0, 0),
            ("Green", 0, 255, 0),
            ("Blue", 0, 0, 255),
            ("Purple", 128, 0, 128),
        ]
        for i, (name, r, g, b) in enumerate(colors):
            tk.Button(
                led_frame, text=name, width=8,
                command=lambda r=r, g=g, b=b: self.set_color(r, g, b)
            ).grid(row=0, column=i, padx=3)
 
        # --- Manual Control ---
        manual_frame = tk.LabelFrame(
            self.root, text="Manual Control (PS5 Controller / WASD)", padx=10, pady=10
        )
        manual_frame.pack(fill="x", padx=20, pady=5)
 
        self.start_btn = tk.Button(
            manual_frame, text="Start Manual Control",
            command=self.start_manual, bg="#2196F3", fg="white",
            width=20, state="disabled"
        )
        self.start_btn.grid(row=0, column=0, padx=5)
 
        self.stop_btn = tk.Button(
            manual_frame, text="Stop",
            command=self.stop_manual, bg="#FF9800", fg="white",
            width=20, state="disabled"
        )
        self.stop_btn.grid(row=0, column=1, padx=5)
 
        self.control_label = tk.Label(
            manual_frame,
            text="Speed: 0  |  Heading: 0°",
            font=("Courier", 11)
        )
        self.control_label.grid(row=1, column=0, columnspan=2, pady=5)
 
        tk.Label(
            manual_frame,
            text="Left analog stick or WASD to move",
            fg="gray"
        ).grid(row=2, column=0, columnspan=2)
 
        # --- Auto Sequence ---
        auto_frame = tk.LabelFrame(
            self.root, text="Automated Sequence", padx=10, pady=10
        )
        auto_frame.pack(fill="x", padx=20, pady=5)
 
        self.auto_btn = tk.Button(
            auto_frame, text="Run Demo Sequence",
            command=self.run_auto_sequence, bg="#9C27B0", fg="white",
            width=20, state="disabled"
        )
        self.auto_btn.grid(row=0, column=0, padx=5)
 
        tk.Label(
            auto_frame,
            text="Runs: square pattern → spin → stop",
            fg="gray"
        ).grid(row=1, column=0, columnspan=2, pady=3)
 
        # --- Log ---
        log_frame = tk.LabelFrame(self.root, text="Log", padx=10, pady=5)
        log_frame.pack(fill="both", expand=True, padx=20, pady=5)
 
        self.log_text = tk.Text(log_frame, height=8, state="disabled", fg="#333")
        self.log_text.pack(fill="both", expand=True)
 
    # -------------------------
    # LOGGING
    # -------------------------
 
    def log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"→ {message}\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")
 
    # -------------------------
    # CONNECTION
    # -------------------------
 
    def connect(self):
        self.log("Connecting to Sphero...")
        self.status_label.config(text="Status: Connecting...", fg="orange")
 
        def do_connect():
            success = self.controller.connect()
            if success:
                self.root.after(0, lambda: self.log("Connected!"))
                self.root.after(0, lambda: self.status_label.config(
                    text="Status: Connected ✓", fg="green"))
                self.root.after(0, lambda: self.connect_btn.config(state="disabled"))
                self.root.after(0, lambda: self.disconnect_btn.config(state="normal"))
                self.root.after(0, lambda: self.start_btn.config(state="normal"))
                self.root.after(0, lambda: self.auto_btn.config(state="normal"))
                self._start_gamepad_thread()
            else:
                self.root.after(0, lambda: self.log("Connection failed."))
                self.root.after(0, lambda: self.status_label.config(
                    text="Status: Failed", fg="red"))
 
        threading.Thread(target=do_connect, daemon=True).start()
 
    def disconnect(self):
        self.stop_manual()
        self.controller.disconnect()
        self.status_label.config(text="Status: Disconnected", fg="red")
        self.connect_btn.config(state="normal")
        self.disconnect_btn.config(state="disabled")
        self.start_btn.config(state="disabled")
        self.auto_btn.config(state="disabled")
        self.log("Disconnected.")
 
    # -------------------------
    # LED
    # -------------------------
 
    def set_color(self, r, g, b):
        if self.controller.is_connected:
            self.controller.set_led_color(r, g, b)
            self.log(f"LED → RGB({r},{g},{b})")
 
    # -------------------------
    # PS5 CONTROLLER VIA HID
    # -------------------------
 
    def _start_gamepad_thread(self):
        """Start reading PS5 controller via HID after Sphero connects."""
        self._gamepad_thread_running = True
        t = threading.Thread(target=self._read_gamepad, daemon=True)
        t.start()
 
    def _read_gamepad(self):
        """
        Read PS5 DualSense directly via USB HID.
 
        PS5 HID report byte layout:
        - Byte 1: Left stick X (0-255, 128 = center)
        - Byte 2: Left stick Y (0-255, 128 = center)
 
        We normalize to -1.0 to 1.0 for the control loop.
        """
        try:
            import hid
            device = hid.device()
            device.open(PS5_VENDOR_ID, PS5_PRODUCT_ID)
            device.set_nonblocking(True)
            self._hid_available = True
            self.root.after(0, lambda: self.log("PS5 controller connected via HID!"))
            self.root.after(0, lambda: self.log("Use left analog stick to drive."))
 
            while self._gamepad_thread_running:
                report = device.read(64)
                if report and len(report) > 2:
                    lx = (report[1] - 128) / 128.0
                    ly = (report[2] - 128) / 128.0
                    self._gamepad_x = lx if abs(lx) > 0.05 else 0.0
                    self._gamepad_y = ly if abs(ly) > 0.05 else 0.0
                time.sleep(0.02)
 
            device.close()
 
        except Exception as e:
            self._hid_available = False
            self.root.after(0, lambda: self.log(f"PS5 HID error: {e}"))
            self.root.after(0, lambda: self.log("Using WASD keyboard instead."))
 
    # -------------------------
    # KEYBOARD
    # -------------------------
 
    def _bind_keys(self):
        for key in ["w", "a", "s", "d"]:
            self.root.bind(f"<KeyPress-{key}>", self._key_press)
            self.root.bind(f"<KeyRelease-{key}>", self._key_release)
 
    def _key_press(self, event):
        self.keys_held.add(event.keysym.lower())
 
    def _key_release(self, event):
        self.keys_held.discard(event.keysym.lower())
 
    def _get_keyboard_movement(self):
        """Convert WASD keys to speed + heading."""
        x, y = 0, 0
        if "w" in self.keys_held: y -= 1
        if "s" in self.keys_held: y += 1
        if "a" in self.keys_held: x -= 1
        if "d" in self.keys_held: x += 1
 
        if x == 0 and y == 0:
            return 0, 0
 
        heading = math.degrees(math.atan2(x, -y))
        if heading < 0:
            heading += 360
        return 100, int(heading)
 
    # -------------------------
    # MANUAL CONTROL LOOP
    # -------------------------
 
    def start_manual(self):
        if self.is_running:
            return
        self.is_running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.log("Manual control started.")
        self.control_thread = threading.Thread(
            target=self._control_loop, daemon=True
        )
        self.control_thread.start()
 
    def stop_manual(self):
        self.is_running = False
        self.stop_btn.config(state="disabled")
        self.start_btn.config(state="normal")
        self.controller.stop()
        self.log("Manual control stopped.")
 
    def _control_loop(self):
        """
        Runs in background thread at ~50Hz.
        PS5 controller takes priority over keyboard.
        Converts stick position to speed + heading using atan2 math.
        """
        while self.is_running:
            speed, heading = 0, 0
 
            if self._hid_available:
                x = self._gamepad_x
                y = self._gamepad_y
                if abs(x) > DEADZONE or abs(y) > DEADZONE:
                    angle = math.degrees(math.atan2(x, -y))
                    if angle < 0:
                        angle += 360
                    magnitude = min(math.sqrt(x**2 + y**2), 1.0)
                    speed = int(magnitude * SPEED_MAX)
                    heading = int(angle)
            else:
                speed, heading = self._get_keyboard_movement()
 
            if speed > 0:
                self.controller.roll(speed, heading)
            else:
                self.controller.stop()
 
            # Safely update UI label from background thread
            self.root.after(
                0,
                lambda s=speed, h=heading:
                    self.control_label.config(
                        text=f"Speed: {s}  |  Heading: {h}°"
                    )
            )
 
            time.sleep(LOOP_DELAY)
 
    # -------------------------
    # AUTO SEQUENCE
    # -------------------------
 
    def run_auto_sequence(self):
        """
        Runs a preset list of commands with time delays.
        This is the 'automated mode' — no user input needed.
        """
        self.log("Running auto sequence...")
        self.auto_btn.config(state="disabled")
 
        def sequence():
            steps = [
                ("Red LED",     lambda: self.controller.set_led_color(255, 0, 0)),
                ("Forward 2s",  lambda: self.controller.roll(100, 0, 2)),
                ("Pause",       lambda: time.sleep(2.5)),
                ("Right 2s",    lambda: self.controller.roll(100, 90, 2)),
                ("Pause",       lambda: time.sleep(2.5)),
                ("Backward 2s", lambda: self.controller.roll(100, 180, 2)),
                ("Pause",       lambda: time.sleep(2.5)),
                ("Left 2s",     lambda: self.controller.roll(100, 270, 2)),
                ("Pause",       lambda: time.sleep(2.5)),
                ("Spin 360°",   lambda: self.controller.spin(360, 2)),
                ("Pause",       lambda: time.sleep(2.5)),
                ("Stop",        lambda: self.controller.stop()),
                ("Purple LED",  lambda: self.controller.set_led_color(128, 0, 128)),
            ]
 
            for description, action in steps:
                if not self.controller.is_connected:
                    break
                self.root.after(0, lambda d=description: self.log(d))
                action()
 
            self.root.after(0, lambda: self.log("Sequence complete!"))
            self.root.after(0, lambda: self.auto_btn.config(state="normal"))
 
        threading.Thread(target=sequence, daemon=True).start()
 
    # -------------------------
    # CLEANUP
    # -------------------------
 
    def on_close(self):
        self._gamepad_thread_running = False
        self.is_running = False
        self.controller.stop()
        self.controller.disconnect()
        self.root.destroy()
 
 
if __name__ == "__main__":
    mock = "--mock" in sys.argv
    root = tk.Tk()
    app = SpheroGUI(root, mock_mode=mock)
    root.mainloop()
 