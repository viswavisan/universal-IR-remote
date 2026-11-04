"""
test_all.py - Complete Hardware Diagnostics & Modular Test Suite
Raspberry Pi Pico Universal IR Remote

Verified Pin Configuration (Pins 4 to 19):
  1. Direct 4x4 Keypad Matrix (8 Pins):
     - Rows (Outputs):
         * Row 0 -> GP2 (Physical Pin 4)
         * Row 1 -> GP3 (Physical Pin 5)
         * Row 2 -> GP4 (Physical Pin 6)
         * Row 3 -> GP5 (Physical Pin 7)
     - Cols (Inputs with internal Pull-Up):
         * Col 0 -> GP6 (Physical Pin 9)
         * Col 1 -> GP7 (Physical Pin 10)
         * Col 2 -> GP8 (Physical Pin 11)
         * Col 3 -> GP9 (Physical Pin 12)

  2. Standalone IR Receiver Module (VS1838B - 3 Pins):
     - Pin 13: GND  -> Ground (-)
     - Pin 14: GP10 -> Power VCC (3.3V OUT, driven HIGH)
     - Pin 15: GP11 -> Signal OUT (Data IN, Active-LOW)

  3. 3-Pin 5V High-Power IR LED Transmitter Module:
     - Pin 18: GND  -> Ground (-)
     - Pin 19: GP14 -> IN (Signal 38kHz PWM Carrier)
     - Pin 40: VBUS -> 5V Power Supply Rail

  4. 0.96" I2C OLED Display (SSD1306 128x64 - 4 Pins):
     - Pin 21: GP16 -> SDA (I2C0 Data)
     - Pin 22: GP17 -> SCL (I2C0 Clock)
     - Pin 23: GND  -> Ground (-)
     - Pin 36: 3V3  -> Power VCC (3.3V OUT)
"""

import machine
import time
import json
import gc

# =============================================================================
# HARDWARE PIN DEFINITIONS
# =============================================================================
KEYPAD_ROWS = (2, 3, 4, 5)   # GP2..GP5 (Physical Pins 4, 5, 6, 7)
KEYPAD_COLS = (6, 7, 8, 9)   # GP6..GP9 (Physical Pins 9, 10, 11, 12)

PIN_RX_VCC = 10              # GP10 (Physical Pin 14) -> Powers VS1838B (3.3V)
PIN_RX_OUT = 11              # GP11 (Physical Pin 15) -> Demodulated Data IN
PIN_TX_PWM = 14              # GP14 (Physical Pin 19) -> 38kHz PWM Transmitter

PIN_OLED_SDA = 16            # GP16 (Physical Pin 21) -> I2C0 SDA
PIN_OLED_SCL = 17            # GP17 (Physical Pin 22) -> I2C0 SCL

# Status LED helper
try:
    status_led = machine.Pin("LED", machine.Pin.OUT)
except Exception:
    try:
        status_led = machine.Pin(25, machine.Pin.OUT)
    except Exception:
        status_led = None

def blink(times=1, delay_ms=40):
    """Blink the onboard LED for visual confirmation."""
    if status_led:
        for _ in range(times):
            status_led.value(1)
            time.sleep_ms(delay_ms)
            status_led.value(0)
            time.sleep_ms(delay_ms)

def power_on_receiver():
    """Ensure IR receiver power rail (GP10) is driven HIGH (3.3V)."""
    rx_pwr = machine.Pin(PIN_RX_VCC, machine.Pin.OUT)
    rx_pwr.value(1)
    time.sleep_ms(30)
    return rx_pwr


# =============================================================================
# 1. INDIVIDUAL TEST: 4x4 DIRECT KEYPAD MATRIX
# =============================================================================
def test_keypad():
    """
    Test direct 4x4 matrix keypad (16 buttons).
    Scans Rows (GP2-GP5) and Columns (GP6-GP9) with internal pull-ups.
    Press any key to see real-time output. Press Ctrl+C to exit.
    """
    print("\n" + "=" * 65)
    print("  [INDIVIDUAL TEST] DIRECT 4x4 MATRIX KEYPAD (16 KEYS)")
    print("=" * 65)
    print("Wiring:")
    print("  Rows (Pin 1 to 4) -> Pico GP2, GP3, GP4, GP5 (Pins 4, 5, 6, 7)")
    print("  Cols (Pin 5 to 8) -> Pico GP6, GP7, GP8, GP9 (Pins 9, 10, 11, 12)")
    print("-" * 65)
    print("Key Layout:")
    print("  [ 1 ]   [ 2 ]   [ 3 ]   │   [ A : MODE (Switch Dev) ]")
    print("  [ 4 ]   [ 5 ]   [ 6 ]   │   [ B : VOL ▲             ]")
    print("  [ 7 ]   [ 8 ]   [ 9 ]   │   [ C : VOL ▼             ]")
    print("  [ * ]   [ 0 ]   [ # ]   │   [ D : POWER             ]")
    print("-" * 65)
    print("Press any key on the keypad now! (Press Ctrl+C to stop):\n")

    # Setup Row Outputs (idle HIGH)
    row_pins = [machine.Pin(p, machine.Pin.OUT, value=1) for p in KEYPAD_ROWS]
    # Setup Col Inputs with internal Pull-Up (idle HIGH = 1)
    col_pins = [machine.Pin(p, machine.Pin.IN, machine.Pin.PULL_UP) for p in KEYPAD_COLS]

    KEYMAP = [
        ["1", "2", "3", "A"],
        ["4", "5", "6", "B"],
        ["7", "8", "9", "C"],
        ["*", "0", "#", "D"],
    ]

    ACTION_MAP = {
        "A": "MODE (Cycle Target Appliance: TV -> AC -> Soundbar)",
        "D": "POWER (Turn Appliance ON/OFF)",
        "B": "VOL + (Volume Up)",
        "C": "VOL - (Volume Down)",
        "*": "MUTE (Audio Mute)",
        "#": "ENTER (Confirm / OK)",
    }

    try:
        while True:
            for r_idx, r_pin in enumerate(row_pins):
                r_pin.value(0)
                time.sleep_us(5)

                for c_idx, c_pin in enumerate(col_pins):
                    if c_pin.value() == 0:
                        key = KEYMAP[r_idx][c_idx]
                        action = ACTION_MAP.get(key, f"Digit '{key}'")
                        blink(1, 40)
                        print(f"--> [KEY PRESSED]: '{key}'  ==>  Action: {action}")
                        time.sleep_ms(220)  # Debounce delay

                r_pin.value(1)
            time.sleep_ms(15)
    except KeyboardInterrupt:
        for r_pin in row_pins:
            r_pin.value(1)
        print("\n[+] Keypad test stopped.")


# =============================================================================
# 2. INDIVIDUAL TEST: IR LED TRANSMITTER (CAMERA BLINK TEST)
# =============================================================================
def test_ir_led():
    """
    Test IR LED Transmitter module.
    Pulses the transmitter on GP14 (Pin 19).
    Look at the IR LED through your smartphone camera to verify purple flash.
    Press Ctrl+C to exit.
    """
    print("\n" + "=" * 65)
    print("  [INDIVIDUAL TEST] IR LED TRANSMITTER TEST (CAMERA BLINK)")
    print("=" * 65)
    print("Wiring:")
    print("  IN  (Signal) ──> Pico GP14 (Physical Pin 19)")
    print("  GND (Ground) ──> Pico Pin 18 (GND)")
    print("  5V  (Power)  ──> Pico Pin 40 (VBUS 5V)")
    print("-" * 65)
    print("Point your smartphone camera at the 940nm IR LED.")
    print("(You should see it flash bright PURPLE/VIOLET on screen!)")
    print("Press Ctrl+C to stop.\n")

    tx = machine.Pin(PIN_TX_PWM, machine.Pin.OUT)
    count = 1
    try:
        while True:
            tx.value(1)
            if status_led:
                status_led.value(1)
            print(f"  [{count}] IR LED: ON  --> (Check smartphone camera)", end="\r")
            time.sleep_ms(500)

            tx.value(0)
            if status_led:
                status_led.value(0)
            time.sleep_ms(400)
            count += 1
    except KeyboardInterrupt:
        tx.value(0)
        if status_led:
            status_led.value(0)
        print("\n[+] IR LED test stopped.")


# =============================================================================
# 3. INDIVIDUAL TEST: IR RECEIVER (LISTEN TO HOUSEHOLD REMOTES)
# =============================================================================
def test_ir_receiver():
    """
    Test 3-Pin VS1838B IR Receiver sensor.
    Powers sensor via GP10 (Pin 14) and reads Active-LOW pulses on GP11 (Pin 15).
    Point any household remote (TV, AC) and press any button.
    Press Ctrl+C to exit.
    """
    power_on_receiver()

    print("\n" + "=" * 65)
    print("  [INDIVIDUAL TEST] IR RECEIVER TEST (VS1838B 38kHz)")
    print("=" * 65)
    print("Wiring:")
    print("  OUT (Data)   ──> Pico GP11 (Physical Pin 15)")
    print("  VCC (Power)  ──> Pico GP10 (Physical Pin 14, 3.3V)")
    print("  GND (Ground) ──> Pico Pin 13 (GND)")
    print("-" * 65)

    rx = machine.Pin(PIN_RX_OUT, machine.Pin.IN, machine.Pin.PULL_UP)
    idle = rx.value()
    print(f"Status: Pin GP11 idle state is {'HIGH [OK - Ready]' if idle == 1 else 'LOW [ERROR - Check GND/VCC wiring!]'}")
    print("Point ANY TV/AC remote at the sensor and press a button.")
    print("Press Ctrl+C to stop.\n")

    burst_count = 1
    try:
        while True:
            if rx.value() == 0:
                blink(1, 20)
                pulses = 0
                start = time.ticks_ms()
                last_val = 0
                while time.ticks_diff(time.ticks_ms(), start) < 120:
                    val = rx.value()
                    if val != last_val:
                        pulses += 1
                        last_val = val
                print(f"  [{burst_count}] SIGNAL RECEIVED! Captured ~{pulses} pulse transitions (WORKING!)")
                burst_count += 1
                time.sleep_ms(250)
            time.sleep_us(100)
    except KeyboardInterrupt:
        print("\n[+] IR receiver test stopped.")


# =============================================================================
# 4. OPTICAL LOOPBACK SELF-TEST (IR LED BLASTS -> RECEIVER VERIFIES)
# =============================================================================
def test_loopback():
    """
    Automated hardware self-test:
    Fires 5 bursts of 38kHz PWM on GP14 and verifies reception on GP11.
    """
    power_on_receiver()

    print("\n" + "=" * 65)
    print("  [OPTICAL LOOPBACK SELF-TEST] IR LED -> RECEIVER")
    print("=" * 65)
    print("Pico will fire 5 test bursts on GP14 and verify on GP11.")
    print("Make sure the IR LED and IR Receiver can see each other.\n")

    rx = machine.Pin(PIN_RX_OUT, machine.Pin.IN, machine.Pin.PULL_UP)
    pwm = machine.PWM(machine.Pin(PIN_TX_PWM))
    pwm.freq(38000)
    pwm.duty_u16(0)

    duty_33 = int(65535 * 0.33)
    detected = 0

    for i in range(5):
        pwm.duty_u16(duty_33)
        blink(1, 10)
        time.sleep_ms(8)

        rx_val = rx.value()
        pwm.duty_u16(0)
        time.sleep_ms(40)

        if rx_val == 0:
            print(f"  Pulse #{i+1}: [PASS] Receiver detected 38kHz burst!")
            detected += 1
        else:
            print(f"  Pulse #{i+1}: [WAIT] No signal detected.")

    pwm.deinit()
    print("-" * 65)
    if detected >= 3:
        print(f"  RESULT: >>> SUCCESS ({detected}/5 bursts confirmed)! <<<")
    else:
        print(f"  RESULT: Detected {detected}/5. Check aiming/alignment.")


# =============================================================================
# 5. IR LEARN & INSTANT REPLAY TEST
# =============================================================================
def test_learn_replay():
    """
    Capture a remote signal from your existing remote, save it,
    and blast it immediately back to your TV/AC to verify it works.
    """
    power_on_receiver()

    print("\n" + "=" * 65)
    print("  [LEARN & INSTANT REPLAY] CAPTURE & TRANSMIT TEST")
    print("=" * 65)

    from universal_ir import UniversalIR
    ir = UniversalIR(rx_pin=PIN_RX_OUT, tx_pin=PIN_TX_PWM, carrier_freq=38000, duty_percent=33)

    dev = input("Enter device name [default: tv]: ").strip().lower() or "tv"
    btn = input("Enter button name [default: power]: ").strip().lower() or "power"

    print(f"\n[*] Ready to learn [{dev}.{btn}].")
    print(">>> AIM YOUR REMOTE AT SENSOR (GP11) AND PRESS THE BUTTON NOW! <<<")

    blink(2, 50)
    pulses = ir.capture_raw(timeout_ms=10000)

    if not pulses or len(pulses) < 4:
        print("[-] Learning timed out or signal too short.")
        return

    ir.save_code(dev, btn, pulses)
    blink(3, 60)
    print(f"\n[+] Successfully learned [{dev}.{btn}] ({len(pulses)} transitions)!")

    # Instant Replay
    print("\nPoint your Pico IR LED (GP14) at your appliance.")
    while True:
        action = input("Press [ENTER] to Transmit / Test (or 'q' to quit): ").strip().lower()
        if action == 'q':
            break
        print(f"[*] Blasting 38kHz IR signal for '{dev}.{btn}'...")
        blink(1, 80)
        ir.send(dev, btn, repeat=2)
        print(f"[+] Sent! Did your {dev.upper()} respond?")


# =============================================================================
# 6. INDIVIDUAL TEST: 0.96" SSD1306 OLED DISPLAY (I2C)
# =============================================================================
def test_oled():
    """
    Test 0.96" SSD1306 OLED Display (128x64 I2C).
    Wiring:
      - Pin 21: GP16 -> SDA
      - Pin 22: GP17 -> SCL
      - Pin 23: GND  -> GND
      - Pin 36: 3V3  -> VCC
    """
    print("\n" + "=" * 65)
    print("  [INDIVIDUAL TEST] 0.96\" SSD1306 OLED DISPLAY (I2C 128x64)")
    print("=" * 65)
    print(f"I2C Pins: SDA -> GP{PIN_OLED_SDA} (Pin 21) | SCL -> GP{PIN_OLED_SCL} (Pin 22)")
    print("Scanning I2C bus for display address (0x3C or 0x3D)...")

    try:
        from oled_ui import RemoteDisplay
        from ssd1306 import SSD1306_I2C
    except ImportError as e:
        print(f"[-] Missing driver files: {e}")
        return

    try:
        i2c = machine.I2C(0, sda=machine.Pin(PIN_OLED_SDA), scl=machine.Pin(PIN_OLED_SCL), freq=400000)
        devices = i2c.scan()
        print(f"I2C Devices found: {[hex(d) for d in devices]}")

        target_addr = None
        for addr in (0x3C, 0x3D):
            if addr in devices:
                target_addr = addr
                break

        if target_addr is None:
            print("\n[-] FAIL: No SSD1306 OLED detected on I2C0.")
            print("Troubleshooting Checklist:")
            print("  1. Verify VCC is plugged into Physical Pin 36 (3V3_OUT).")
            print("  2. Verify GND is plugged into Physical Pin 23 (GND).")
            print("  3. Verify SCL is plugged into Physical Pin 22 (GP17).")
            print("  4. Verify SDA is plugged into Physical Pin 21 (GP16).")
            return

        print(f"[+] SUCCESS: Found OLED at address 0x{target_addr:02X}!")
        oled = SSD1306_I2C(128, 64, i2c, addr=target_addr)

        # 1. Screen Fill & Header Pattern
        print("[*] Running Pattern & Animation test on OLED...")
        oled.fill(0)
        oled.rect(0, 0, 128, 64, 1)
        oled.fill_rect(4, 4, 120, 16, 1)
        oled.text("OLED TEST OK!", 12, 8, 0)
        oled.text("128x64 SSD1306", 8, 26, 1)
        oled.text("I2C @ 0x3C", 8, 38, 1)
        oled.show()
        time.sleep_ms(1200)

        # 2. Dynamic Progress Bar Animation
        print("[*] Running Progress Bar animation...")
        for p in range(0, 101, 10):
            oled.fill_rect(10, 48, 108, 12, 0)
            oled.rect(10, 48, 108, 12, 1)
            bar_w = int((p / 100.0) * 104)
            oled.fill_rect(12, 50, bar_w, 8, 1)
            oled.show()
            time.sleep_ms(50)

        # 3. Test High-Level Remote UI
        print("[*] Testing Remote Display UI Manager...")
        disp = RemoteDisplay(sda_pin=PIN_OLED_SDA, scl_pin=PIN_OLED_SCL)
        disp.show_splash()
        disp.show_idle(device="TV", last_key="B", last_action="VOL_UP", status="TEST OK")
        print("\n[+] OLED Test Complete! Display is showing Remote Standby UI.")

    except Exception as e:
        print(f"[-] Error during OLED test: {e}")


# =============================================================================
# INTERACTIVE MASTER MENU (Optional)
# =============================================================================
def run_all_tests():
    """Interactive menu to select any test interactively."""
    while True:
        print("\n" + "=" * 65)
        print("   UNIVERSAL IR REMOTE - HARDWARE DIAGNOSTICS MENU")
        print("=" * 65)
        print("  1. Test 4x4 Keypad (Direct 8-Pin GPIO Matrix)")
        print("  2. Test IR LED Transmitter (Camera Purple Glow Test)")
        print("  3. Test IR Receiver Sensor (Listen to any remote)")
        print("  4. Automated Optical Loopback Check (LED -> Receiver)")
        print("  5. Learn & Instant Replay (Capture button & blast to TV/AC)")
        print("  6. Test 0.96\" I2C OLED Display (SSD1306 Graphics & UI)")
        print("  7. Exit")
        print("=" * 65)

        try:
            choice = input("Select an option (1-7): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

        if choice == "1":
            test_keypad()
        elif choice == "2":
            test_ir_led()
        elif choice == "3":
            test_ir_receiver()
        elif choice == "4":
            test_loopback()
        elif choice == "5":
            test_learn_replay()
        elif choice == "6":
            test_oled()
        elif choice == "7":
            print("Finished diagnostics.")
            break
        else:
            print("Invalid selection. Please choose 1 to 7.")


# =============================================================================
# EXECUTION ENTRY POINT
# =============================================================================
if __name__ == "__main__":
    # -------------------------------------------------------------------------
    # MENTION / UNCOMMENT WHAT YOU WANT TO TEST HERE:
    # Simply uncomment the single test function you want to run!
    # -------------------------------------------------------------------------

    test_keypad()        # <-- Check Keypad (16 buttons)
    # test_ir_led()      # <-- Check IR LED Transmitter (Phone camera purple glow)
    # test_ir_receiver() # <-- Check IR Receiver (Listen for any remote signal)
    # test_loopback()    # <-- Check Optical Self-Test (IR LED -> Receiver)
    # test_learn_replay()# <-- Learn a button and test transmit to appliance
    # test_oled()        # <-- Check 0.96" SSD1306 I2C OLED Display
    # run_all_tests()    # <-- Run interactive menu
