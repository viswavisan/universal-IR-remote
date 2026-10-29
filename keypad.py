"""
keypad.py - 4x4 Matrix Keypad Scanner for Raspberry Pi Pico (RP2040)
Scans 4 rows and 4 columns (16 keys) directly using 8 GPIO pins.
Includes debouncing and multi-device mapping support.
"""

import machine
import time

class KeypadMatrix4x4:
    """
    Scans a standard 4x4 matrix keypad (4 rows, 4 columns = 16 keys).
    Rows are configured as Outputs (driven LOW during scan).
    Columns are configured as Inputs with internal Pull-Up resistors (read LOW when pressed).
    """

    # Standard 4x4 Keypad Layout:
    # Key 'A' is used as MODE (device switcher: TV, AC, Soundbar, Projector)
    # Key 'B' is VOL_UP, Key 'C' is VOL_DN, Key 'D' is POWER
    # Key '*' is MUTE, Key '#' is ENTER / OK
    DEFAULT_KEYMAP = [
        ["1", "2", "3", "A"],   # Row 0 -> A = MODE (Cycle Device)
        ["4", "5", "6", "B"],   # Row 1 -> B = VOL_UP
        ["7", "8", "9", "C"],   # Row 2 -> C = VOL_DN
        ["*", "0", "#", "D"],   # Row 3 -> * = MUTE, # = ENTER, D = POWER
    ]

    def __init__(self, row_pins=(6, 7, 8, 9), col_pins=(10, 11, 12, 13), keymap=None, debounce_ms=180):
        """
        :param row_pins: 4 GPIO pin numbers for matrix rows (Outputs)
        :param col_pins: 4 GPIO pin numbers for matrix columns (Inputs with pull-ups)
        :param keymap: 4x4 nested list of key names
        :param debounce_ms: Debounce delay in milliseconds
        """
        self.row_pin_nums = row_pins
        self.col_pin_nums = col_pins
        self.keymap = keymap if keymap else self.DEFAULT_KEYMAP
        self.debounce_ms = debounce_ms

        # Initialize Row Pins as Outputs (idle HIGH)
        self.rows = [machine.Pin(p, machine.Pin.OUT, value=1) for p in self.row_pin_nums]

        # Initialize Column Pins as Inputs with Pull-Up (idle HIGH, pressed LOW)
        self.cols = [machine.Pin(p, machine.Pin.IN, machine.Pin.PULL_UP) for p in self.col_pin_nums]

        self.last_press_time = 0

    def scan(self):
        """
        Scan 4x4 matrix and return the key name if pressed, or None if idle.
        """
        now = time.ticks_ms()
        if time.ticks_diff(now, self.last_press_time) < self.debounce_ms:
            return None

        detected_key = None

        for r_idx, row_pin in enumerate(self.rows):
            # Drive current row LOW
            row_pin.value(0)
            time.sleep_us(5)

            # Check all 4 columns
            for c_idx, col_pin in enumerate(self.cols):
                if col_pin.value() == 0:  # Key is pressed
                    detected_key = self.keymap[r_idx][c_idx]
                    break

            # Restore row to HIGH
            row_pin.value(1)

            if detected_key:
                break

        if detected_key:
            self.last_press_time = now
            return detected_key

        return None
