"""
rgb_strip.py - Addressable RGB LED Strip Driver (WS2812B / NeoPixel)
Universal IR Remote Indicator & Keypad Backlight for Raspberry Pi Pico (RP2040)

Hardware Wiring:
  - DIN (Data In)  ──> Pico GP16 (Physical Pin 21 @ Perfboard U5)
  - VCC (Power)    ──> Pico Pin 36 (3V3_OUT @ F5) or Pin 39 (VSYS 4.5V @ C5)
  - GND (Ground)   ──> Pico Pin 23 (GND @ S5)

Visual Feedback Color Scheme:
  1. Active Device Ambient Backlight:
     - TV        : Vibrant Sky Cyan / Deep Blue   (RGB: 0, 140, 255)
     - AC        : Arctic Frost / Crisp Ice White (RGB: 160, 255, 255)
     - SOUNDBAR  : Warm Amber / Golden Sunset     (RGB: 255, 120, 0)
     - PROJECTOR : Deep Neon Purple / Violet      (RGB: 180, 0, 255)

  2. Operation & State Feedback:
     - IR Transmit Burst       : Bright Emerald Flash (RGB: 0, 255, 70)
     - Learn Step 1 (Pick Key) : Gentle Pulsing Amber (RGB: 255, 160, 0)
     - Learn Step 2 (Aim Remote): Fast Flashing Magenta/Pink (RGB: 255, 0, 120)
     - Learn Success           : Running Green Sweep / Triple Flash
     - Learn Error / Timeout   : Rapid Red Warning Blinks (RGB: 255, 0, 0)
     - Button 2/3 Rejected     : Warning Yellow Strobe
"""

import time

try:
    import machine
    import neopixel
except ImportError:
    machine = None
    neopixel = None

# Default Device Color Profiles (R, G, B)
DEVICE_COLORS = {
    "tv": (0, 140, 255),          # Sky Cyan / Deep Blue
    "ac": (160, 255, 255),        # Arctic Frost Ice White
    "soundbar": (255, 120, 0),     # Warm Amber Sunset
    "projector": (180, 0, 255),    # Neon Violet
}

# Special Indicator Colors
COLOR_TX = (0, 255, 70)           # Emerald Green TX Flash
COLOR_LEARN_STEP1 = (255, 160, 0) # Amber
COLOR_LEARN_STEP2 = (255, 0, 120) # Magenta/Pink Aim Remote
COLOR_SUCCESS = (0, 255, 30)      # High-brightness Green
COLOR_ERROR = (255, 0, 0)         # Red Alert
COLOR_WARNING = (255, 200, 0)     # Yellow Strobe
COLOR_OFF = (0, 0, 0)


class RGBIndicator:
    """
    High-level controller for WS2812B / NeoPixel addressable RGB LED strip.
    Handles device status indicators, active transmission bursts, and ambient backlight.
    """

    def __init__(self, pin=16, num_leds=8, brightness=0.25):
        self.pin_num = pin
        self.num_leds = num_leds
        self.brightness = max(0.02, min(1.0, brightness))
        self.current_device = "tv"
        self.enabled = False
        self.np = None
        self.backlight_on = True

        if machine is not None and neopixel is not None:
            try:
                pin_obj = machine.Pin(self.pin_num, machine.Pin.OUT)
                self.np = neopixel.NeoPixel(pin_obj, self.num_leds)
                self.enabled = True
                self.clear()
            except Exception as e:
                print(f"[RGB] NeoPixel init notice: {e} (Running headless/virtual)")
                self.enabled = False

    def _scale(self, color, factor=1.0):
        """Scale RGB color by current brightness and optional factor."""
        b = self.brightness * factor
        r = int(color[0] * b)
        g = int(color[1] * b)
        b_val = int(color[2] * b)
        return (min(255, max(0, r)), min(255, max(0, g)), min(255, max(0, b_val)))

    def show_color(self, color, factor=1.0):
        """Set all LEDs to a single color and latch."""
        if not self.enabled or self.np is None:
            return
        scaled = self._scale(color, factor)
        try:
            for i in range(self.num_leds):
                self.np[i] = scaled
            self.np.write()
        except Exception:
            pass

    def clear(self):
        """Turn off all RGB LEDs."""
        self.show_color(COLOR_OFF)

    # -------------------------------------------------------------------------
    # Mode & Ambient Backlight Control
    # -------------------------------------------------------------------------
    def set_mode(self, device_name):
        """Set ambient backlight color corresponding to active appliance profile."""
        self.current_device = str(device_name).lower()
        if not self.backlight_on:
            return
        color = DEVICE_COLORS.get(self.current_device, (0, 140, 255))
        self.show_color(color)

    def restore_mode(self):
        """Restore active device ambient backlight color."""
        self.set_mode(self.current_device)

    def set_brightness(self, level):
        """Set brightness level (0.05 to 1.0) and refresh."""
        self.brightness = max(0.02, min(1.0, level))
        self.restore_mode()

    def toggle_backlight(self):
        """Toggle ambient backlight ON/OFF."""
        self.backlight_on = not self.backlight_on
        if self.backlight_on:
            self.restore_mode()
        else:
            self.clear()
        return self.backlight_on

    # -------------------------------------------------------------------------
    # Visual Feedback Sequences
    # -------------------------------------------------------------------------
    def flash_tx(self, delay_ms=45):
        """High-intensity Emerald Green burst on IR transmission."""
        if not self.enabled or self.np is None:
            return
        # Bright pulse
        self.show_color(COLOR_TX, factor=1.8)
        time.sleep_ms(delay_ms)
        self.restore_mode()

    def show_learn_step1(self):
        """Step 1: Pulsing Amber glow indicating waiting for destination button."""
        self.show_color(COLOR_LEARN_STEP1, factor=1.2)

    def show_learn_step2(self):
        """Step 2: Vibrant Pink/Magenta indicating sensor listening for remote."""
        self.show_color(COLOR_LEARN_STEP2, factor=1.5)

    def flash_success(self):
        """Cascade Green sweep indicating code captured & saved."""
        if not self.enabled or self.np is None:
            return
        try:
            # Quick chase
            for i in range(self.num_leds):
                self.np[i] = self._scale(COLOR_SUCCESS, factor=1.5)
                self.np.write()
                time.sleep_ms(25)
            time.sleep_ms(150)
            self.restore_mode()
        except Exception:
            self.restore_mode()

    def flash_error(self):
        """Red strobe indicating learning timeout or reception failure."""
        if not self.enabled or self.np is None:
            return
        for _ in range(3):
            self.show_color(COLOR_ERROR, factor=1.6)
            time.sleep_ms(80)
            self.clear()
            time.sleep_ms(60)
        self.restore_mode()

    def flash_warning(self):
        """Yellow alert indicating rejected attempt to overwrite system buttons."""
        if not self.enabled or self.np is None:
            return
        for _ in range(2):
            self.show_color(COLOR_WARNING, factor=1.4)
            time.sleep_ms(90)
            self.clear()
            time.sleep_ms(70)
        self.restore_mode()

    def rainbow_cycle(self, loops=1, speed_ms=10):
        """Smooth rainbow test animation across the strip."""
        if not self.enabled or self.np is None:
            return

        def wheel(pos):
            if pos < 85:
                return (pos * 3, 255 - pos * 3, 0)
            elif pos < 170:
                pos -= 85
                return (255 - pos * 3, 0, pos * 3)
            else:
                pos -= 170
                return (0, pos * 3, 255 - pos * 3)

        for _ in range(loops):
            for j in range(256):
                for i in range(self.num_leds):
                    pixel_index = (i * 256 // self.num_leds) + j
                    color = wheel(pixel_index & 255)
                    self.np[i] = self._scale(color, factor=1.0)
                self.np.write()
                time.sleep_ms(speed_ms)
        self.restore_mode()

