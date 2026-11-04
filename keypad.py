"""
keypad.py - Direct 4x4 Matrix Keypad Driver for Raspberry Pi Pico (RP2040)
Scans 16 keys (0-9, A, B, C, D, *, #) using 8 direct GPIO pins without any extra ICs.

Wiring (8 Pins to Pico):
  Rows (Outputs):
    - Row 0 -> GP2 (Physical Pin 4)
    - Row 1 -> GP3 (Physical Pin 5)
    - Row 2 -> GP4 (Physical Pin 6)
    - Row 3 -> GP5 (Physical Pin 7)
  Cols (Inputs with Pull-Up):
    - Col 0 -> GP6 (Physical Pin 9)
    - Col 1 -> GP7 (Physical Pin 10)
    - Col 2 -> GP8 (Physical Pin 11)
    - Col 3 -> GP9 (Physical Pin 12)
"""

import machine
import time

# Standard 4x4 Keypad Layout:
# A = MODE (Cycle Target Appliance: TV, AC, Soundbar, Projector)
# B = VOL_UP, C = VOL_DN, D = POWER
# * = MUTE, # = ENTER / OK
DEFAULT_KEYMAP = [
    ["1", "2", "3", "A"],   # Row 0
    ["4", "5", "6", "B"],   # Row 1
    ["7", "8", "9", "C"],   # Row 2
    ["*", "0", "#", "D"],   # Row 3
]


class KeypadMatrix4x4:
    """
    Direct GPIO 4x4 Matrix Keypad Scanner.
    - Rows are driven LOW one at a time.
    - Cols are read with internal pull-up resistors (Active-LOW).
    """

    def __init__(self, row_pins=(2, 3, 4, 5), col_pins=(6, 7, 8, 9), keymap=None, debounce_ms=180):
        self.row_pin_nums = row_pins
        self.col_pin_nums = col_pins
        self.keymap = keymap if keymap else DEFAULT_KEYMAP
        self.debounce_ms = debounce_ms

        # Initialize Rows as Outputs (idle HIGH)
        self.rows = [machine.Pin(p, machine.Pin.OUT, value=1) for p in self.row_pin_nums]

        # Initialize Cols as Inputs with internal Pull-Up resistors (idle is 1)
        self.cols = [machine.Pin(p, machine.Pin.IN, machine.Pin.PULL_UP) for p in self.col_pin_nums]

        self.last_press_time = 0

    def scan(self):
        """
        Scan the 4x4 matrix and return the pressed key string (e.g. '1', 'A'),
        or None if no key is currently pressed.
        """
        now = time.ticks_ms()
        if time.ticks_diff(now, self.last_press_time) < self.debounce_ms:
            return None

        detected_key = None

        for r_idx, row_pin in enumerate(self.rows):
            # Drive current row LOW
            row_pin.value(0)
            time.sleep_us(5)

            # Check if any column is pulled LOW
            for c_idx, col_pin in enumerate(self.cols):
                if col_pin.value() == 0:
                    detected_key = self.keymap[r_idx][c_idx]
                    break

            # Restore row back to HIGH
            row_pin.value(1)
            if detected_key:
                break

        if detected_key:
            self.last_press_time = now
            return detected_key

        return None


def create_keypad(row_pins=(2, 3, 4, 5), col_pins=(6, 7, 8, 9), keymap=None):
    """Factory helper to instantiate the direct 4x4 matrix keypad."""
    return KeypadMatrix4x4(row_pins=row_pins, col_pins=col_pins, keymap=keymap)
