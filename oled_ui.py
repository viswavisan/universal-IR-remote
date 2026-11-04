"""
oled_ui.py - OLED UI Manager for Universal IR Remote (SSD1306 128x64 I2C)
Displays target device, active keypress, IR transmission status, and learning mode feedback.

Wiring to Raspberry Pi Pico (Right-side I2C Pins):
  - OLED GND -> Pin 23 (GND) or Pin 38 (GND)
  - OLED VCC -> Pin 36 (3V3_OUT)
  - OLED SCL -> Pin 22 (GP17 / I2C0 SCL)
  - OLED SDA -> Pin 21 (GP16 / I2C0 SDA)
"""

import time

try:
    import machine
    from ssd1306 import SSD1306_I2C
except ImportError:
    # Allows offline import / unit testing
    machine = None
    SSD1306_I2C = None


class RemoteDisplay:
    """
    High-level UI Manager for 128x64 SSD1306 OLED Display.
    Fails gracefully if the OLED is disconnected or not installed.
    """

    def __init__(self, sda_pin=16, scl_pin=17, i2c_id=0, width=128, height=64, i2c_freq=400000):
        self.width = width
        self.height = height
        self.enabled = False
        self.oled = None
        self.i2c = None

        if machine is None or SSD1306_I2C is None:
            return

        try:
            # Initialize I2C bus
            self.i2c = machine.I2C(
                i2c_id,
                sda=machine.Pin(sda_pin),
                scl=machine.Pin(scl_pin),
                freq=i2c_freq
            )
            # Scan for display address (standard: 0x3C or 0x3D)
            devices = self.i2c.scan()
            addr = None
            for candidate in (0x3C, 0x3D):
                if candidate in devices:
                    addr = candidate
                    break

            if addr is not None:
                self.oled = SSD1306_I2C(self.width, self.height, self.i2c, addr=addr)
                self.enabled = True
                print(f"[OLED] SSD1306 detected at 0x{addr:02X} on GP{sda_pin}(SDA)/GP{scl_pin}(SCL).")
            else:
                print(f"[OLED] No display found on I2C{i2c_id} (Scanned: {[hex(d) for d in devices]}). Headless mode.")
        except Exception as e:
            print(f"[OLED] Initialization warning: {e}. Running in headless mode.")
            self.enabled = False

    def clear(self):
        if not self.enabled:
            return
        try:
            self.oled.fill(0)
            self.oled.show()
        except Exception:
            pass

    def show_splash(self):
        """Displays boot splash screen."""
        if not self.enabled:
            return
        try:
            self.oled.fill(0)
            # Border frame
            self.oled.rect(0, 0, 128, 64, 1)
            self.oled.rect(2, 2, 124, 60, 1)
            # Inverted Title Bar
            self.oled.fill_rect(5, 6, 118, 16, 1)
            self.oled.text("UNIVERSAL IR", 16, 10, 0)
            # Subtitle
            self.oled.text("Pico Remote v2.0", 4, 30, 1)
            self.oled.text("Direct Matrix 4x4", 4, 44, 1)
            self.oled.show()
            time.sleep_ms(900)
        except Exception:
            pass

    def show_idle(self, device="TV", last_key=None, last_action=None, status="READY"):
        """Displays normal standby screen with active device and ready status."""
        if not self.enabled:
            return
        try:
            self.oled.fill(0)
            # Top Banner (Inverted Header)
            self.oled.fill_rect(0, 0, 128, 14, 1)
            dev_str = f"[{device.upper()}]"
            self.oled.text(dev_str, 4, 3, 0)
            self.oled.text("IR REMOTE", 50, 3, 0)

            # Horizontal Separator line
            self.oled.hline(0, 15, 128, 1)

            # Body Information
            if last_key or last_action:
                self.oled.text(f"Key : [{last_key or '-'}]", 4, 22, 1)
                self.oled.text(f"Cmd : {str(last_action or '-').upper()[:10]}", 4, 34, 1)
            else:
                self.oled.text("Press key on", 4, 24, 1)
                self.oled.text("matrix keypad", 4, 36, 1)

            # Footer Status Bar
            self.oled.hline(0, 48, 128, 1)
            self.oled.text(f"Status: {status[:10]}", 4, 52, 1)

            self.oled.show()
        except Exception:
            pass

    def show_transmitting(self, device, action, key=None):
        """Displays dynamic IR transmission feedback."""
        if not self.enabled:
            return
        try:
            self.oled.fill(0)
            # Top Banner
            self.oled.fill_rect(0, 0, 128, 14, 1)
            self.oled.text(f"[{device.upper()}]", 4, 3, 0)
            self.oled.text("TRANSMIT", 60, 3, 0)

            self.oled.hline(0, 15, 128, 1)

            # Command being transmitted
            if key:
                self.oled.text(f"Key: [{key}]", 4, 20, 1)
            self.oled.text(f"Cmd: {str(action).upper()[:10]}", 4, 32, 1)

            # Graphic IR Wave animation bar
            self.oled.fill_rect(4, 46, 120, 14, 1)
            self.oled.text(">>> TX SEND >>>", 8, 49, 0)

            self.oled.show()
        except Exception:
            pass

    def show_learn_step1(self, device="TV"):
        """Displays Step 1 of handheld learning: choose destination key to store."""
        if not self.enabled:
            return
        try:
            self.oled.fill(0)
            self.oled.fill_rect(0, 0, 128, 14, 1)
            self.oled.text(f"[{device.upper()}] LEARN", 4, 3, 0)
            self.oled.text("STEP 1", 76, 3, 0)
            self.oled.hline(0, 15, 128, 1)
            self.oled.text("PRESS KEY TO", 4, 22, 1)
            self.oled.text("STORE SIGNAL", 4, 34, 1)
            self.oled.text("(e.g. Press '1')", 4, 48, 1)
            self.oled.show()
        except Exception:
            pass

    def show_learn_step2(self, device, key):
        """Displays Step 2 of handheld learning: signal matching from remote."""
        if not self.enabled:
            return
        try:
            self.oled.fill(0)
            self.oled.fill_rect(0, 0, 128, 14, 1)
            self.oled.text(f"[{device.upper()}] KEY [{key}]", 4, 3, 0)
            self.oled.text("STEP 2", 76, 3, 0)
            self.oled.hline(0, 15, 128, 1)
            self.oled.text("SIGNAL MATCHING", 4, 20, 1)
            self.oled.text("Aim remote at RX", 4, 34, 1)
            self.oled.fill_rect(4, 47, 120, 14, 1)
            self.oled.text("PRESS BTN NOW", 12, 50, 0)
            self.oled.show()
        except Exception:
            pass

    def show_learning(self, device, button):
        """Displays learning mode prompt."""
        if not self.enabled:
            return
        try:
            self.oled.fill(0)
            # Inverted Header
            self.oled.fill_rect(0, 0, 128, 14, 1)
            self.oled.text("LEARN IR CODE", 12, 3, 0)

            self.oled.hline(0, 15, 128, 1)
            self.oled.text(f"Dev: {device.upper()[:10]}", 4, 20, 1)
            self.oled.text(f"Btn: {button.upper()[:10]}", 4, 32, 1)

            # Instruction
            self.oled.hline(0, 46, 128, 1)
            self.oled.text("Aim remote at RX", 0, 50, 1)

            self.oled.show()
        except Exception:
            pass

    def show_learn_result(self, device, button, success=True, pulse_count=0):
        """Displays the result of learning an IR button."""
        if not self.enabled:
            return
        try:
            self.oled.fill(0)
            self.oled.fill_rect(0, 0, 128, 14, 1)
            self.oled.text("LEARN RESULT", 16, 3, 0)

            self.oled.hline(0, 15, 128, 1)

            if success:
                self.oled.text("SUCCESS! SAVED", 8, 24, 1)
                self.oled.text(f"{device}.{button}", 4, 38, 1)
                self.oled.text(f"Pulses: {pulse_count}", 4, 52, 1)
            else:
                self.oled.text("TIMEOUT / ERROR", 4, 26, 1)
                self.oled.text("No signal heard", 4, 40, 1)
                self.oled.text("Try again", 4, 52, 1)

            self.oled.show()
        except Exception:
            pass

    def show_message(self, title, line1="", line2="", line3=""):
        """Displays a custom popup/dialog."""
        if not self.enabled:
            return
        try:
            self.oled.fill(0)
            self.oled.fill_rect(0, 0, 128, 14, 1)
            self.oled.text(title[:15], 4, 3, 0)
            self.oled.hline(0, 15, 128, 1)
            if line1:
                self.oled.text(line1[:16], 4, 22, 1)
            if line2:
                self.oled.text(line2[:16], 4, 36, 1)
            if line3:
                self.oled.text(line3[:16], 4, 50, 1)
            self.oled.show()
        except Exception:
            pass
