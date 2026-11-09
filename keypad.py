"""
keypad.py - Direct 8x8 Keypad Matrix Driver for Raspberry Pi Pico (RP2040)
Scans 64 tactile buttons (Buttons 1 to 64) across an 8x8 matrix using 16 direct GPIO pins.
Fully matched to the finalized V2 22x78 Perfboard Layout (pcb_design_v2.html).

Wiring (16 GPIO Pins on Pico Bottom Header, Physical Pins 1 to 20):
  Rows (8 Output Pins, active-LOW):
    - Row 0 (Set 1, Row 19): GP11 (Pin 15)
    - Row 1 (Set 2, Row 27): GP4  (Pin 6)
    - Row 2 (Set 3, Row 35): GP3  (Pin 5)
    - Row 3 (Set 4, Row 43): GP12 (Pin 16)
    - Row 4 (Set 5, Row 51): GP8  (Pin 11)
    - Row 5 (Set 6, Row 59): GP7  (Pin 10)
    - Row 6 (Set 7, Row 67): GP0  (Pin 1)
    - Row 7 (Set 8, Row 75): GP15 (Pin 20)

  Cols (8 Input Pins with Internal Pull-Ups, idle HIGH):
    - Col 0 (Col C Rail): GP1  (Pin 2)
    - Col 1 (Col D Rail): GP2  (Pin 4)
    - Col 2 (Col H Rail): GP5  (Pin 7)
    - Col 3 (Col I Rail): GP6  (Pin 9)
    - Col 4 (Col N Rail): GP9  (Pin 12)
    - Col 5 (Col O Rail): GP10 (Pin 14)
    - Col 6 (Col S Rail): GP13 (Pin 17)
    - Col 7 (Col T Rail): GP14 (Pin 19)

Dedicated System Keys:
  - Button 2: LEARN (Row 19 GP11 x Col H GP5)
  - Button 3: MODE  (Row 19 GP11 x Col N GP9)
"""

try:
    import machine
except ImportError:
    machine = None

import time

# Default 8x8 Keymap (Row-by-Row Button Numbering 1 to 64)
# Each element is the button number string "1" through "64"
DEFAULT_KEYMAP_8X8 = [
    ["1",  "5",  "2",  "6",  "3",  "7",  "4",  "8" ],  # Row 0: GP11 (Set 1) -> Upper: 1, 2, 3, 4 | Lower: 5, 6, 7, 8
    ["9",  "13", "10", "14", "11", "15", "12", "16"],  # Row 1: GP4  (Set 2) -> Upper: 9, 10, 11, 12 | Lower: 13, 14, 15, 16
    ["17", "21", "18", "22", "19", "23", "20", "24"],  # Row 2: GP3  (Set 3) -> Upper: 17..20 | Lower: 21..24
    ["25", "29", "26", "30", "27", "31", "28", "32"],  # Row 3: GP12 (Set 4) -> Upper: 25..28 | Lower: 29..32
    ["33", "37", "34", "38", "35", "39", "36", "40"],  # Row 4: GP8  (Set 5) -> Upper: 33..36 | Lower: 37..40
    ["41", "45", "42", "46", "43", "47", "44", "48"],  # Row 5: GP7  (Set 6) -> Upper: 41..44 | Lower: 45..48
    ["49", "53", "50", "54", "51", "55", "52", "56"],  # Row 6: GP0  (Set 7) -> Upper: 49..52 | Lower: 53..56
    ["57", "61", "58", "62", "59", "63", "60", "64"],  # Row 7: GP15 (Set 8) -> Upper: 57..60 | Lower: 61..64
]

DEFAULT_ROW_PINS = (11, 4, 3, 12, 8, 7, 0, 15)
DEFAULT_COL_PINS = (1, 2, 5, 6, 9, 10, 13, 14)


class KeypadMatrix8x8:
    """
    Direct GPIO 8x8 Keypad Matrix Scanner (64 buttons).
    - Rows are driven LOW one at a time.
    - Cols are sampled with RP2040 internal pull-up resistors (Active-LOW).
    """

    def __init__(self, row_pins=DEFAULT_ROW_PINS, col_pins=DEFAULT_COL_PINS,
                 keymap=None, debounce_ms=160):
        self.row_pin_nums = list(row_pins)
        self.col_pin_nums = list(col_pins)
        self.keymap = keymap if keymap is not None else DEFAULT_KEYMAP_8X8
        self.debounce_ms = debounce_ms

        self.rows = []
        self.cols = []

        if machine is not None:
            # Initialize Rows as Outputs (idle HIGH)
            self.rows = [machine.Pin(p, machine.Pin.OUT, value=1) for p in self.row_pin_nums]
            # Initialize Cols as Inputs with internal Pull-Up resistors (idle HIGH)
            self.cols = [machine.Pin(p, machine.Pin.IN, machine.Pin.PULL_UP) for p in self.col_pin_nums]

        self.last_press_time = 0
        self.last_key = None

    def scan(self):
        """
        Scan the 8x8 matrix and return the pressed button string (e.g. '1', '2', ..., '64'),
        or None if no key is currently pressed.
        """
        if machine is None:
            return None

        now = time.ticks_ms()
        if time.ticks_diff(now, self.last_press_time) < self.debounce_ms:
            return None

        detected_key = None

        for r_idx, row_pin in enumerate(self.rows):
            # Drive current row LOW
            row_pin.value(0)
            time.sleep_us(5)

            # Check if any column is pulled LOW by a pressed button
            for c_idx, col_pin in enumerate(self.cols):
                if col_pin.value() == 0:
                    detected_key = self.keymap[r_idx][c_idx]
                    break

            # Restore row back to HIGH
            row_pin.value(1)
            if detected_key is not None:
                break

        if detected_key is not None:
            self.last_press_time = now
            self.last_key = detected_key
            return detected_key

        return None


# Backward-compatible aliases
KeypadMatrix4x4 = KeypadMatrix8x8
KeypadMatrix = KeypadMatrix8x8

def create_keypad(row_pins=DEFAULT_ROW_PINS, col_pins=DEFAULT_COL_PINS, keymap=None):
    """Factory helper to instantiate the direct 8x8 matrix keypad."""
    return KeypadMatrix8x8(row_pins=row_pins, col_pins=col_pins, keymap=keymap)
