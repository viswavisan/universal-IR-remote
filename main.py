"""
main.py - Universal IR Remote Controller for Raspberry Pi Pico
Direct 4x4 Keypad Matrix + Split IR Transmitter & Receiver + I2C OLED Display

Pin Layout:
  1. Direct 4x4 Keypad Matrix (8 Pins on Pins 4 to 12):
     - Rows (Outputs):
         * Row 0 -> GP2 (Physical Pin 4)
         * Row 1 -> GP3 (Physical Pin 5)
         * Row 2 -> GP4 (Physical Pin 6)
         * Row 3 -> GP5 (Physical Pin 7)
     - Cols (Inputs with Pull-Up):
         * Col 0 -> GP6 (Physical Pin 9)
         * Col 1 -> GP7 (Physical Pin 10)
         * Col 2 -> GP8 (Physical Pin 11)
         * Col 3 -> GP9 (Physical Pin 12)

  2. Standalone IR Receiver Module (VS1838B - 3 Pins):
     - Pin 13: GND  -> Ground (-)
     - Pin 14: GP10 -> Power VCC (3.3V OUT, driven HIGH)
     - Pin 15: GP11 -> Signal OUT (Data IN, Active-LOW)

  3. High-Power IR LED Transmitter Module (3 Pins):
     - Pin 18: GND  -> Ground (-)
     - Pin 19: GP14 -> IN (Signal 38kHz Hardware PWM TX)
     - Pin 40: VBUS -> 5V Power Supply Rail

  4. 0.96" I2C OLED Display (SSD1306 128x64 - 4 Pins):
     - Pin 21: GP16 -> SDA (I2C0 Data)
     - Pin 22: GP17 -> SCL (I2C0 Clock)
     - Pin 23: GND  -> Ground (-)
     - Pin 36: 3V3  -> Power VCC (3.3V OUT)
"""

import machine
import time
import sys
from universal_ir import UniversalIR
from keypad import KeypadMatrix4x4, create_keypad
from oled_ui import RemoteDisplay

# =============================================================================
# PIN CONFIGURATION
# =============================================================================
# 1. Standalone IR Transmitter (GP14 + GND)
PIN_IR_TX = 14       # GP14 (Physical Pin 19)

# 2. Standalone IR Receiver (GP10=VCC, GP11=DATA, GND=Pin 13)
PIN_IR_RX_VCC = 10   # GP10 (Physical Pin 14) -> Powers VS1838B (3.3V)
PIN_IR_RX = 11       # GP11 (Physical Pin 15) -> Demodulated Data IN

# Power up IR Receiver
rx_vcc = machine.Pin(PIN_IR_RX_VCC, machine.Pin.OUT)
rx_vcc.value(1)

# 3. Direct 4x4 Matrix Keypad (8 GPIO Pins)
KEYPAD_ROWS = (2, 3, 4, 5)   # Rows 0..3 -> GP2, GP3, GP4, GP5 (Pins 4, 5, 6, 7)
KEYPAD_COLS = (6, 7, 8, 9)   # Cols 0..3 -> GP6, GP7, GP8, GP9 (Pins 9, 10, 11, 12)

# 4. 0.96" SSD1306 OLED Display (I2C0: GP16 SDA, GP17 SCL)
PIN_OLED_SDA = 16    # GP16 (Physical Pin 21)
PIN_OLED_SCL = 17    # GP17 (Physical Pin 22)

# Initialize Display (Safe fallback if OLED disconnected)
display = RemoteDisplay(sda_pin=PIN_OLED_SDA, scl_pin=PIN_OLED_SCL)

# Supported Devices
SUPPORTED_DEVICES = ["tv", "ac", "soundbar", "projector"]
current_device_index = 0

# Meaningful Action Mappings for Keypad (User Custom Layout):
# A = LEARN (Pick Key + Signal Matching)
# B = MODE (Switch / Add Multiple Devices: TV, AC, Soundbar, Projector)
# C = MUTE
# 1 = POWER ON, 3 = POWER OFF
# 2 = UP, 4 = LEFT, 5 = OK, 6 = RIGHT, 8 = DOWN (D-Pad cluster)
# 7 = VOL -, 9 = VOL +
KEY_ACTION_MAP = {
    "A": "LEARN",
    "B": "MODE",
    "C": "mute",
    "1": "power_on",
    "2": "up",
    "3": "power_off",
    "4": "left",
    "5": "ok",
    "6": "right",
    "7": "vol_down",
    "8": "down",
    "9": "vol_up",
    "D": "power",
    "*": "mute",
    "#": "enter",
}

# On-board LED indicator
try:
    status_led = machine.Pin("LED", machine.Pin.OUT)
except Exception:
    status_led = machine.Pin(25, machine.Pin.OUT)

def led_blink(times=2, delay_ms=80):
    for _ in range(times):
        status_led.value(1)
        time.sleep_ms(delay_ms)
        status_led.value(0)
        time.sleep_ms(delay_ms)

def wait_for_key_press(keypad, timeout_ms=9000):
    """
    Wait until a key is pressed and released.
    First ensures the previous key (e.g. 'A') is fully released.
    """
    start = time.ticks_ms()
    # 1. Wait for previous key release
    while keypad.scan() is not None:
        if time.ticks_diff(time.ticks_ms(), start) > 1200:
            break
        time.sleep_ms(25)

    print("  [Listening for keypad keypress... Press a key like '1', '2', '3'...]")

    # 2. Wait for new key press
    start = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start) < timeout_ms:
        k = keypad.scan()
        if k is not None:
            # Wait for release to prevent repeated triggers
            time.sleep_ms(60)
            while keypad.scan() is not None:
                time.sleep_ms(25)
            print(f"  >>> KEYPAD DETECTED: [{k}] <<<")
            return k
        time.sleep_ms(25)
    return None

# =============================================================================
# 4x4 MATRIX KEYPAD RUNNER
# =============================================================================
def handle_keypad_matrix(ir):
    """
    Monitor direct 4x4 Keypad Matrix (16 keys) with dynamic OLED & Terminal updates.
    - Press 'A' to LEARN: Pick key to store -> Signal matching -> Auto-save!
    - Press 'D' for Power.
    - Press 'B' for Vol+, 'C' for Vol-.
    - Press '*' for Mute, '#' for Enter.
    - Press '0'-'9' for numeric channels or custom learned IR keys.
    Press Ctrl+C in serial terminal to switch to CLI prompt.
    """
    global current_device_index
    keypad = create_keypad(row_pins=KEYPAD_ROWS, col_pins=KEYPAD_COLS)

    print("\n" + "=" * 65)
    print("      RASPBERRY PI PICO UNIVERSAL IR REMOTE - KEYPAD ACTIVE")
    print("=" * 65)
    print("Hardware Wiring:")
    print("  Rows -> GP2, GP3, GP4, GP5 (Pins 4, 5, 6, 7)")
    print("  Cols -> GP6, GP7, GP8, GP9 (Pins 9, 10, 11, 12)")
    print("  IR RX -> GP11 (Pin 15) | IR TX -> GP14 (Pin 19)")
    print("-" * 65)
    print("Key Action Layout:")
    print("  [ 1: PWR ON  ]   [ 2: UP (▲)  ]   [ 3: PWR OFF ]   [ A: LEARN ]")
    print("  [ 4: LEFT(◀) ]   [ 5: OK/ENT  ]   [ 6: RGHT(▶) ]   [ B: MODE  ]")
    print("  [ 7: VOL -   ]   [ 8: DOWN(▼) ]   [ 9: VOL +   ]   [ C: MUTE  ]")
    print("  [ *          ]   [ 0          ]   [ #          ]   [ D: POWER ]")
    print("=" * 65)
    active_dev = SUPPORTED_DEVICES[current_device_index]
    print(f"Active Device: [{active_dev.upper()}]")
    print(">>> REMOTE IS READY! Press any key on the keypad... <<<")
    print(">>> Press key 'A' anytime to LEARN a remote button. <<<")
    print(">>> Press Ctrl+C in terminal if you want to enter CLI mode. <<<\n")

    display.show_idle(device=active_dev, status="READY")

    try:
        while True:
            key = keypad.scan()
            if key:
                status_led.value(1)
                action = KEY_ACTION_MAP.get(key, key.lower())

                # =============================================================
                # Key 'A': HANDHELD LEARN MODE
                # =============================================================
                if action == "LEARN":
                    active_dev = SUPPORTED_DEVICES[current_device_index]
                    print("\n" + "=" * 65)
                    print(f"  [LEARN MODE ACTIVATED] Target Device: [{active_dev.upper()}]")
                    print("  STEP 1: Press the keypad key where you want to store the signal.")
                    print("          (For example, press key '1', '2', '3', etc.)")
                    print("=" * 65)
                    display.show_learn_step1(device=active_dev)
                    led_blink(2, 60)

                    # Step 1: Wait for destination key to store
                    target_key = wait_for_key_press(keypad, timeout_ms=9000)
                    if not target_key or target_key == "A":
                        print("[-] Canceled or timed out waiting for destination key.")
                        print("    Returning to normal remote mode.\n")
                        display.show_message("LEARN CANCELED", "No key selected", "Returning to idle")
                        time.sleep_ms(1000)
                        display.show_idle(device=active_dev, status="READY")
                        status_led.value(0)
                        continue

                    # Determine button storage name (e.g. key '1' -> '1', key 'B' -> 'vol_up')
                    button_name = KEY_ACTION_MAP.get(target_key, target_key.lower())

                    print("\n" + "=" * 65)
                    print(f"  STEP 2: SIGNAL MATCHING FOR KEY [{target_key}]")
                    print(f"  Destination  : Keypad Key [{target_key}] -> '{active_dev}.{button_name}'")
                    print("  Instructions : Point your original remote at the VS1838B IR sensor")
                    print("                 (Pico GP11 / Pin 15) and press the button NOW!")
                    print("  Waiting for 38kHz infrared pulses (timeout in 7 seconds)...")
                    print("=" * 65)

                    display.show_learn_step2(device=active_dev, key=target_key)
                    status_led.value(1)

                    # Step 2: Signal Matching / Capture IR pulses
                    pulses = ir.capture_raw(timeout_ms=7000)
                    status_led.value(0)

                    if pulses and len(pulses) >= 4:
                        ir.save_code(active_dev, button_name, pulses)
                        print("\n" + "*" * 65)
                        print(f"  [+] SIGNAL MATCHED & SAVED SUCCESSFULLY!")
                        print(f"  Device Name    : [{active_dev.upper()}]")
                        print(f"  Assigned Key   : Key [{target_key}]")
                        print(f"  Action Name    : '{button_name}'")
                        print(f"  Captured Pulses: {len(pulses)} raw microsecond transitions")
                        print(f"  Storage Status : Permanently saved in flash (ir_codes.json)")
                        print("*" * 65)
                        print(f"  --> Press key [{target_key}] anytime to transmit this signal!\n")

                        display.show_learn_result(active_dev, target_key, success=True, pulse_count=len(pulses))
                        led_blink(3, 80)
                        time.sleep_ms(1500)
                        display.show_idle(device=active_dev, last_key=target_key, last_action=button_name, status="SAVED OK")
                    else:
                        print("\n[-] SIGNAL MATCHING TIMEOUT: No valid IR signal detected.")
                        print("    Tips:")
                        print("      - Point remote 2-5 cm directly in front of the VS1838B receiver.")
                        print("      - Press key 'A' anytime to try again.\n")

                        display.show_learn_result(active_dev, target_key, success=False)
                        time.sleep_ms(1500)
                        display.show_idle(device=active_dev, status="LEARN FAIL")

                # =============================================================
                # Key 'B': MODE SWITCHER (Cycle target device: TV, AC, etc.)
                # =============================================================
                elif action == "MODE":
                    current_device_index = (current_device_index + 1) % len(SUPPORTED_DEVICES)
                    active_dev = SUPPORTED_DEVICES[current_device_index]
                    print(f"\n[MODE KEY 'B'] Target Device Switched to: ---> [{active_dev.upper()}] <---")
                    display.show_idle(device=active_dev, last_key='B', last_action="MODE", status="DEV CHANGED")
                    led_blink(current_device_index + 1, 60)

                # =============================================================
                # Normal Keys: TRANSMIT STORED SIGNAL
                # =============================================================
                else:
                    active_dev = SUPPORTED_DEVICES[current_device_index]
                    print(f"[*] Pressed Key [{key}] (Action: '{action}') ➜ Transmitting '{active_dev}.{action}'...")
                    display.show_transmitting(device=active_dev, action=action, key=key)
                    sent = ir.send(active_dev, action, repeat=2)
                    if not sent:
                        print(f"    [-] NOTICE: '{action}' has not been learned for '{active_dev}' yet.")
                        print(f"        -> Press key 'A' on the keypad to learn it now!")
                        display.show_idle(device=active_dev, last_key=key, last_action=action, status="NOT LEARNED")
                    else:
                        print(f"    [+] Transmitted 38kHz signal for '{active_dev}.{action}' successfully!")
                        display.show_idle(device=active_dev, last_key=key, last_action=action, status="SENT OK")

                status_led.value(0)
            time.sleep_ms(15)
    except KeyboardInterrupt:
        print("\n[!] Exited 4x4 Keypad Mode. Entering Serial CLI Loop...")
        active_dev = SUPPORTED_DEVICES[current_device_index]
        display.show_idle(device=active_dev, status="CLI MODE")
        cli_loop(ir)

# =============================================================================
# INTERACTIVE CLI & MENUS
# =============================================================================
def print_banner():
    print("=" * 60)
    print("      RASPBERRY PI PICO - UNIVERSAL IR REMOTE")
    print("=" * 60)
    print("Available Commands:")
    print("  learn <device> <button>   - Record IR signal for a button")
    print("  send <device> <button>    - Transmit a stored IR signal")
    print("  repeat <dev> <btn> <n>    - Send command n times (e.g. vol_up 5)")
    print("  list                      - View all learned devices & buttons")
    print("  delete <device> [button]  - Remove a button or entire device")
    print("  test-ir                   - Test IR LED connection & loopback")
    print("  keypad                    - Start 4x4 Keypad Remote (16 keys)")
    print("  help                      - Show this command list")
    print("=" * 60)

def cli_loop(ir):
    """Main interactive serial loop."""
    print_banner()

    while True:
        try:
            line = input("\nIR-Remote> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

        if not line:
            continue

        parts = line.split()
        cmd = parts[0].lower()

        if cmd == "help":
            print_banner()

        elif cmd == "learn":
            if len(parts) < 3:
                print("Usage: learn <device> <button>  (e.g., learn tv power)")
                continue
            device = parts[1]
            button = parts[2]
            display.show_learning(device, button)
            status_led.value(1)
            success = ir.learn(device, button)
            status_led.value(0)
            display.show_learn_result(device, button, success)
            if success:
                led_blink(3, 60)
            time.sleep_ms(800)
            display.show_idle(device=device, last_action=button, status="LEARN DONE")

        elif cmd == "send":
            if len(parts) < 3:
                print("Usage: send <device> <button>  (e.g., send tv power)")
                continue
            device = parts[1]
            button = parts[2]
            display.show_transmitting(device, button)
            status_led.value(1)
            ir.send(device, button, repeat=2)
            status_led.value(0)
            display.show_idle(device=device, last_action=button, status="SENT")

        elif cmd in ("test", "test-ir"):
            print("\n[*] Testing IR LED connection on GP14 (Pin 19)...")
            detected_count = 0
            for i in range(5):
                ir.tx_pwm.duty_u16(ir.duty_on)
                status_led.value(1)
                time.sleep_ms(8)
                rx_val = ir.rx_pin.value()
                ir.tx_pwm.duty_u16(0)
                status_led.value(0)
                time.sleep_ms(35)

                if rx_val == 0:
                    print(f"  Pulse #{i+1}: [PASS] IR received! (LEDs firing & receiver detected signal)")
                    detected_count += 1
                else:
                    print(f"  Pulse #{i+1}: [SENT] 38kHz burst sent")

            if detected_count > 0:
                print(f"[+] Result: SUCCESS ({detected_count}/5 pulses confirmed by receiver).")
            else:
                print("[-] Result: No loopback detected.")

        elif cmd == "repeat":
            if len(parts) < 4:
                print("Usage: repeat <device> <button> <count>  (e.g., repeat tv vol_up 5)")
                continue
            device = parts[1]
            button = parts[2]
            try:
                count = int(parts[3])
            except ValueError:
                print("[-] Count must be a valid number.")
                continue
            status_led.value(1)
            ir.send(device, button, repeat=count)
            status_led.value(0)

        elif cmd == "list":
            codes = ir.list_codes()
            if not codes:
                print("[-] No IR codes stored in database yet.")
                print("    Use: learn <device> <button> to record one!")
            else:
                print("\nStored Devices and Buttons:")
                for dev, buttons in codes.items():
                    print(f"  Device: [{dev}]")
                    for b in buttons:
                        pulse_count = len(ir.get_code(dev, b) or [])
                        print(f"    - {b:<15} ({pulse_count} transitions)")

        elif cmd == "delete":
            if len(parts) < 2:
                print("Usage: delete <device> [button]")
                continue
            device = parts[1]
            button = parts[2] if len(parts) >= 3 else None
            
            if button:
                if ir.delete_code(device, button):
                    print(f"[+] Deleted button '{button}' from device '{device}'.")
                else:
                    print(f"[-] Button '{button}' not found for device '{device}'.")
            else:
                confirm = input(f"Are you sure you want to delete entire device '{device}'? (y/N): ").strip().lower()
                if confirm == "y":
                    if ir.delete_code(device):
                        print(f"[+] Deleted device '{device}'.")
                    else:
                        print(f"[-] Device '{device}' not found.")
                else:
                    print("Canceled.")

        elif cmd == "keypad":
            handle_keypad_matrix(ir)

        else:
            print(f"[-] Unknown command '{cmd}'. Type 'help' for available commands.")

def main():
    display.show_splash()
    led_blink(2, 100)
    ir = UniversalIR(rx_pin=PIN_IR_RX, tx_pin=PIN_IR_TX, carrier_freq=38000, duty_percent=33)
    display.show_idle(device=SUPPORTED_DEVICES[0], status="READY")
    # Launch direct Keypad Remote mode immediately on boot
    handle_keypad_matrix(ir)

if __name__ == "__main__":
    main()
