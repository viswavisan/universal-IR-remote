"""
test_all.py - Complete Hardware Diagnostics & Modular Test Suite
Raspberry Pi Pico Universal IR Remote (Finalized V2 Perfboard Layout)

Hardware Pin Configuration (pcb_design_v2.html):
  1. Direct 8x8 Keypad Matrix (16 GPIO Pins, Physical Pins 1 to 20):
     - Rows (Outputs):
         * Row 0 -> GP12 (Physical Pin 16 @ Q12)
         * Row 1 -> GP4  (Physical Pin 6  @ G12)
         * Row 2 -> GP0  (Physical Pin 1  @ B12)
         * Row 3 -> GP15 (Physical Pin 20 @ U12)
         * Row 4 -> GP8  (Physical Pin 11 @ L12)
         * Row 5 -> GP7  (Physical Pin 10 @ K12)
         * Row 6 -> GP3  (Physical Pin 5  @ F12)
         * Row 7 -> GP11 (Physical Pin 15 @ P12)
     - Cols (Inputs with Internal Pull-Up):
         * Col 0 -> GP1  (Physical Pin 2  @ C12)
         * Col 1 -> GP2  (Physical Pin 4  @ E12)
         * Col 2 -> GP5  (Physical Pin 7  @ H12)
         * Col 3 -> GP6  (Physical Pin 9  @ J12)
         * Col 4 -> GP9  (Physical Pin 12 @ M12 ➔ Rail N)
         * Col 5 -> GP10 (Physical Pin 14 @ O12 ➔ Rail P)
         * Col 6 -> GP13 (Physical Pin 17 @ R12)
         * Col 7 -> GP14 (Physical Pin 19 @ T12)

  2. Dedicated IR Optics (Pico Top Header, Physical Pins 21 to 40):
     - IR Transmitter: GP18 (Physical Pin 24 @ R7, 38kHz Hardware PWM)
     - IR Receiver   : GP17 (Physical Pin 22 @ T7, Active-LOW Data IN from R2)
     - Power Rails   : 3.3V System Output from Pico Pin 36 (F5)

  3. Addressable RGB LED Strip (WS2812B / NeoPixel):
     - DIN -> GP16 (Physical Pin 21 @ Perfboard U5)
     - VCC -> 3.3V (Pin 36 @ F5) or VSYS 4.5V (Pin 39 @ C5)
     - GND -> Ground (Pin 23 @ S5)
"""

import time
import json
import gc

try:
    import machine
except ImportError:
    machine = None

# =============================================================================
# HARDWARE PIN DEFINITIONS (V2 Finalized)
# =============================================================================
KEYPAD_ROWS = (12, 4, 3, 11, 8, 7, 0, 15)
KEYPAD_COLS = (1, 2, 5, 6, 9, 10, 13, 14)

PIN_TX_PWM = 18               # GP18 (Physical Pin 24 @ R7) -> 38kHz PWM Transmitter
PIN_RX_OUT = 17               # GP17 (Physical Pin 22 @ T7) -> Demodulated Data IN
PIN_RGB_LED = 16              # GP16 (Physical Pin 21) -> WS2812B NeoPixel DIN
NUM_RGB_LEDS = 8              # 8-pixel addressable strip

# Status LED helper
status_led = None
if machine is not None:
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


# =============================================================================
# 1. INDIVIDUAL TEST: 8x8 DIRECT KEYPAD MATRIX (64 BUTTONS)
# =============================================================================
def test_keypad():
    """
    Test direct 8x8 matrix keypad (64 buttons).
    Scans Rows (GP12, GP4, GP0, GP15, GP8, GP7, GP3, GP11)
    and Columns (GP1, GP2, GP5, GP6, GP9, GP10, GP13, GP14).
    Press any key to see real-time output. Press Ctrl+C to exit.
    """
    print("\n" + "=" * 70)
    print("  [INDIVIDUAL TEST] DIRECT 8x8 MATRIX KEYPAD (64 BUTTONS)")
    print("=" * 70)
    print("Hardware Wiring:")
    print("  Rows (Outputs) -> GP12, GP4, GP0, GP15, GP8, GP7, GP3, GP11")
    print("  Cols (Inputs)  -> GP1, GP2, GP5, GP6, GP9, GP10, GP13, GP14")
    print("-" * 70)
    print("Fixed System Keys (Immutable):")
    print("  Button 02: [FIXED: LEARN] (Amber Cap)  --> Hardcoded IR Learning Trigger")
    print("  Button 03: [FIXED: MODE]  (Emerald Cap)--> Hardcoded Appliance Profile Switcher")
    print("-" * 70)
    print("Programmable Keys (62 Buttons):")
    print("  Buttons 01, and 04 through 64 are ALL fully available for IR Learning!")
    print("-" * 70)
    print("Press any button (1 to 64) on the keypad now! (Press Ctrl+C to stop):\n")

    if machine is None:
        print("[!] Offline mode: machine module not available.")
        return

    from keypad import create_keypad, DEFAULT_KEYMAP_8X8
    kp = create_keypad(row_pins=KEYPAD_ROWS, col_pins=KEYPAD_COLS)

    try:
        while True:
            key = kp.scan()
            if key:
                extra = ""
                if key == "2":
                    extra = " ==> [FIXED SYSTEM KEY: LEARN - Hardware-locked, not changeable]"
                elif key == "3":
                    extra = " ==> [FIXED SYSTEM KEY: MODE - Hardware-locked, not changeable]"
                else:
                    extra = " ==> [LEARNABLE: Available for programming any IR signal]"
                blink(1, 40)
                print(f"--> [BUTTON PRESSED]: Button {int(key):02d}{extra}")
            time.sleep_ms(15)
    except KeyboardInterrupt:
        print("\n[+] Keypad test stopped.")


# =============================================================================
# 2. INDIVIDUAL TEST: IR LED TRANSMITTER (CAMERA BLINK TEST)
# =============================================================================
def test_ir_led():
    """
    Test IR LED Transmitter on GP18 (Pin 24 @ R7).
    Look at the IR LED through your smartphone camera to verify purple flash.
    Press Ctrl+C to exit.
    """
    print("\n" + "=" * 65)
    print("  [INDIVIDUAL TEST] IR LED TRANSMITTER TEST (CAMERA BLINK)")
    print("=" * 65)
    print("Wiring:")
    print("  SIG (Signal) ──> Pico GP18 (Physical Pin 24 @ R7)")
    print("  GND (Ground) ──> Pico Pin 38 (GND @ D5)")
    print("  VCC (Power)  ──> Pico Pin 36 (3V3 @ F5)")
    print("-" * 65)
    print("Point your smartphone camera at the IR LED.")
    print("(You should see it flash bright PURPLE/VIOLET on screen!)")
    print("Press Ctrl+C to stop.\n")

    if machine is None:
        print("[!] Offline mode.")
        return

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
    Test TSOP / VS1838B IR Receiver sensor on GP17 (Pin 22 @ T7).
    Point any household remote (TV, AC) and press any button.
    Press Ctrl+C to exit.
    """
    print("\n" + "=" * 65)
    print("  [INDIVIDUAL TEST] IR RECEIVER TEST (VS1838B / TSOP on GP17)")
    print("=" * 65)
    print("Wiring:")
    print("  DAT (Data)   ──> Pico GP17 (Physical Pin 22 @ T7 via R2)")
    print("  VCC (Power)  ──> Pico Pin 36 (3V3 @ F5)")
    print("  GND (Ground) ──> Pico Pin 28 (GND @ N5)")
    print("-" * 65)

    if machine is None:
        print("[!] Offline mode.")
        return

    rx = machine.Pin(PIN_RX_OUT, machine.Pin.IN, machine.Pin.PULL_UP)
    idle = rx.value()
    print(f"Status: Pin GP17 idle state is {'HIGH [OK - Ready]' if idle == 1 else 'LOW [ERROR - Check GND/VCC wiring!]'}")
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
    Fires 5 bursts of 38kHz PWM on GP18 and verifies reception on GP17.
    """
    print("\n" + "=" * 65)
    print("  [OPTICAL LOOPBACK SELF-TEST] IR TX (GP18) -> IR RX (GP17)")
    print("=" * 65)

    if machine is None:
        print("[!] Offline mode.")
        return

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
    Capture a remote signal, save it, and blast it immediately back.
    """
    print("\n" + "=" * 65)
    print("  [LEARN & INSTANT REPLAY] CAPTURE & TRANSMIT TEST")
    print("=" * 65)

    from universal_ir import UniversalIR
    ir = UniversalIR(rx_pin=PIN_RX_OUT, tx_pin=PIN_TX_PWM, carrier_freq=38000, duty_percent=33)

    print("Point your household remote at the VS1838B sensor (GP17).")
    print("Press a button on your remote NOW to record it...")

    success = ir.learn("test_device", "test_btn", timeout_ms=6000)
    if not success:
        print("[-] Learning timed out. Try holding the remote closer.")
        return

    pulses = ir.get_code("test_device", "test_btn")
    print(f"\n[+] Successfully captured {len(pulses)} raw microsecond transitions!")
    print("Blasting the signal back 3 times on GP18 (38kHz)...")

    time.sleep_ms(1000)
    for i in range(3):
        print(f"  Transmission #{i+1}...")
        blink(1, 60)
        ir.send("test_device", "test_btn", repeat=1)
        time.sleep_ms(500)

    print("[+] Transmission complete!")


# =============================================================================
# 6. INDIVIDUAL TEST: WS2812B RGB ADDRESSABLE LED STRIP
# =============================================================================
def test_rgb_strip():
    """
    Test WS2812B / NeoPixel addressable RGB LED strip on GP16 (Pin 21).
    Demonstrates ambient device colors, transmit flash, learn indicators, and rainbow.
    """
    print("\n" + "=" * 65)
    print("  [INDIVIDUAL TEST] WS2812B RGB ADDRESSABLE LED STRIP TEST")
    print("=" * 65)
    print("Wiring:")
    print("  DIN (Data In)  ──> Pico GP16 (Physical Pin 21 @ Perfboard U5)")
    print("  VCC (Power)    ──> Pico Pin 36 (3V3 @ F5) or Pin 39 (VSYS @ C5)")
    print("  GND (Ground)   ──> Pico Pin 23 (GND @ S5)")
    print("-" * 65)

    from rgb_strip import RGBIndicator
    rgb = RGBIndicator(pin=PIN_RGB_LED, num_leds=NUM_RGB_LEDS, brightness=0.35)

    if not rgb.enabled:
        print("[-] RGB NeoPixel not initialized. (Running in offline/virtual mode)")
        return

    print("[1/5] Running Smooth Rainbow Cycle...")
    rgb.rainbow_cycle(loops=2, speed_ms=6)

    print("[2/5] Demonstrating Appliance Mode Indicator Colors:")
    modes = [("TV", "tv"), ("AC", "ac"), ("SOUNDBAR", "soundbar"), ("PROJECTOR", "projector")]
    for name, mode in modes:
        print(f"      * Mode: [{name}]")
        rgb.set_mode(mode)
        time.sleep_ms(700)

    print("[3/5] Simulating IR Transmit Flash (Emerald Green Pulse)...")
    for _ in range(3):
        rgb.flash_tx(80)
        time.sleep_ms(300)

    print("[4/5] Simulating Handheld Learning Indicators:")
    print("      * Step 1: Destination Key Selected (Pulsing Amber)")
    rgb.show_learn_step1()
    time.sleep_ms(1200)

    print("      * Step 2: Listening for Remote Signal (Flashing Magenta)")
    rgb.show_learn_step2()
    time.sleep_ms(1200)

    print("      * Step 3: Success Cascade Sweep (Bright Green)")
    rgb.flash_success()
    time.sleep_ms(800)

    print("      * Step 4: Error/Timeout Alert (Red Strobe)")
    rgb.flash_error()
    time.sleep_ms(800)

    print("[5/5] Re-establishing TV Ambient Backlight...")
    rgb.set_mode("tv")
    print("[+] RGB Addressable LED Strip Test Completed Successfully!")


# =============================================================================
# 7. ALL-IN-ONE AUTOMATED PRE-FLIGHT DIAGNOSTICS
# =============================================================================
def test_battery():
    """Test 18650 Battery Voltage & Charge Level via Pico internal ADC3 (GP29 / VSYS)."""
    print("\n" + "-" * 60)
    print(">>> Testing 18650 Battery & VSYS via Pico Internal ADC (GP29)...")
    print("-" * 60)
    if machine is None:
        print("[!] MicroPython 'machine' module not available (host simulation mode).")
        print("    Simulated 18650 Battery: 3.85V (Approx. 65% capacity)")
        return

    try:
        # Pico RP2040 internal ADC3 (GPIO 29) measures VSYS divided by 3
        adc = machine.ADC(29)
        raw = adc.read_u16()
        voltage = raw * 3.3 / 65535 * 3
        # 18650 Li-ion voltage profile: 4.2V = 100%, 3.7V = ~50%, 3.2V = ~5%, <3.0V = Cutoff
        pct = max(0, min(100, int((voltage - 3.2) / (4.2 - 3.2) * 100)))

        print(f"[+] Raw ADC (16-bit):                {raw}")
        print(f"[+] Measured VSYS / Battery Voltage: {voltage:.2f} V")
        print(f"[+] Estimated 18650 Charge Level:   {pct}%")

        if voltage > 4.25:
            print("[+] Status: [CHARGING] TP4056 USB-C Charger connected.")
        elif voltage >= 3.70:
            print("[+] Status: [HEALTHY] Normal operating voltage (3.7V - 4.2V).")
        elif voltage >= 3.30:
            print("[!] Status: [LOW BATTERY] Voltage < 3.7V. Recharging recommended.")
        else:
            print("[!] Status: [CRITICAL] Voltage < 3.3V. TP4056 DW01A protection cutoff imminent!")
    except Exception as e:
        print(f"[-] Error reading battery voltage on GP29: {e}")


def test_all_hardware():
    """Run non-interactive hardware checks sequentially."""
    print("\n" + "#" * 65)
    print("  RUNNING COMPLETE HARDWARE DIAGNOSTICS (V2 PERFBOARD)")
    print("#" * 65)

    print("\n>>> Step 1/4: Checking 18650 Battery & VSYS Voltage...")
    test_battery()

    print("\n>>> Step 2/4: Checking RGB Addressable LED Strip...")
    test_rgb_strip()

    print("\n>>> Step 3/4: Checking Optical Loopback (GP18 -> GP17)...")
    test_loopback()

    print("\n>>> Step 4/4: Checking 8x8 Keypad Matrix...")
    print("Press Ctrl+C anytime to finish.")
    test_keypad()


# =============================================================================
# INTERACTIVE TEST MENU
# =============================================================================
def print_menu():
    print("\n" + "=" * 65)
    print("      RASPBERRY PI PICO HARDWARE TEST SUITE (V2 FINALIZED)")
    print("=" * 65)
    print("  1. Test 8x8 Keypad Matrix (64 Buttons: 1..64, LEARN, MODE)")
    print("  2. Test IR LED Transmitter (Camera Flash on GP18)")
    print("  3. Test IR Receiver Sensor (Listen to Remotes on GP17)")
    print("  4. Optical Loopback Self-Test (GP18 TX -> GP17 RX)")
    print("  5. IR Learn & Instant Replay Test")
    print("  6. Test WS2812B RGB Addressable LED Strip (GP16)")
    print("  7. Test 18650 Battery & TP4056 Voltage (Pico GP29 / VSYS)")
    print("  8. Run Full Automated Diagnostics")
    print("  0. Exit")
    print("=" * 65)

def main():
    while True:
        print_menu()
        try:
            choice = input("Select test [0-8]: ").strip()
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
            test_rgb_strip()
        elif choice == "7":
            test_battery()
        elif choice == "8":
            test_all_hardware()
        elif choice == "0":
            print("\nDiagnostics complete. Exiting.")
            break
        else:
            print("[-] Invalid selection. Enter 0 to 8.")

if __name__ == "__main__":
    main()
