"""
main.py - Interactive Universal IR Remote Controller for Raspberry Pi Pico
Uses a standard 4x4 Matrix Keypad (16 buttons) directly wired to 8 GPIOs:
  - 4 Rows: GPIO 6, 7, 8, 9
  - 4 Cols: GPIO 10, 11, 12, 13
"""

import machine
import time
import sys
from universal_ir import UniversalIR
from keypad import KeypadMatrix4x4

# =============================================================================
# PIN CONFIGURATION
# =============================================================================
# IR Receiver: TSOP38238 / VS1838B data pin
PIN_IR_RX = 15

# IR Transmitter: Base of NPN transistor driving 940nm IR LED
PIN_IR_TX = 16

# 4x4 Matrix Keypad GPIO Assignments (8 GPIOs Total)
KEYPAD_ROWS = (6, 7, 8, 9)       # Rows 0, 1, 2, 3 -> GP6, GP7, GP8, GP9
KEYPAD_COLS = (10, 11, 12, 13)   # Cols 0, 1, 2, 3 -> GP10, GP11, GP12, GP13

# Available Devices for Multi-Device Remote Mode
SUPPORTED_DEVICES = ["tv", "ac", "soundbar", "projector"]
current_device_index = 0

# Meaningful Action Mappings for the 4x4 Keypad:
# A = Mode (Switch Device)
# B = Vol Up, C = Vol Down, D = Power
# * = Mute, # = Enter/OK, 0-9 = Numbers
KEY_ACTION_MAP = {
    "A": "MODE",
    "B": "vol_up",
    "C": "vol_down",
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
    """Blink the status LED."""
    for _ in range(times):
        status_led.value(1)
        time.sleep_ms(delay_ms)
        status_led.value(0)
        time.sleep_ms(delay_ms)

# =============================================================================
# 4x4 MATRIX KEYPAD RUNNER
# =============================================================================

def handle_keypad_matrix(ir):
    """
    Monitor standard 4x4 Keypad Matrix (16 keys).
    - Press 'A' to cycle target appliance (TV, AC, Soundbar, Projector).
    - Press 'D' for Power.
    - Press 'B' for Vol+, 'C' for Vol-.
    - Press '*' for Mute, '#' for Enter.
    - Press '0'-'9' for numeric channels.
    Press Ctrl+C in serial terminal to return to CLI.
    """
    global current_device_index
    keypad = KeypadMatrix4x4(row_pins=KEYPAD_ROWS, col_pins=KEYPAD_COLS)

    print("\n" + "=" * 60)
    print("      4x4 KEYPAD MATRIX REMOTE ACTIVE (16 BUTTONS)")
    print("=" * 60)
    print("Key Layout:")
    print("  [ 1 ]   [ 2 ]   [ 3 ]   [ A: MODE (Switch Dev) ]")
    print("  [ 4 ]   [ 5 ]   [ 6 ]   [ B: VOL +             ]")
    print("  [ 7 ]   [ 8 ]   [ 9 ]   [ C: VOL -             ]")
    print("  [ * ]   [ 0 ]   [ # ]   [ D: POWER             ]")
    print("=" * 60)
    print(f"Active Device: [{SUPPORTED_DEVICES[current_device_index].upper()}]")
    print("Press key 'A' anytime to change device.")
    print("Press Ctrl+C to return to CLI menu.\n")

    try:
        while True:
            key = keypad.scan()
            if key:
                status_led.value(1)

                action = KEY_ACTION_MAP.get(key, key.lower())

                # Key 'A': Mode switcher
                if action == "MODE":
                    current_device_index = (current_device_index + 1) % len(SUPPORTED_DEVICES)
                    active_dev = SUPPORTED_DEVICES[current_device_index]
                    print(f"\n[🔄 MODE KEY 'A'] Target Device Switched to: ---> [{active_dev.upper()}] <---")
                    led_blink(current_device_index + 1, 60)
                else:
                    active_dev = SUPPORTED_DEVICES[current_device_index]
                    print(f"[*] Pressed [{key}] ({action}) -> Sending '{active_dev}.{action}'")
                    sent = ir.send(active_dev, action)
                    if not sent:
                        print(f"    (Notice: '{action}' for '{active_dev}' not recorded yet. Use 'learn {active_dev} {action}')")

                status_led.value(0)
            time.sleep_ms(15)
    except KeyboardInterrupt:
        print("\nExited 4x4 Keypad Mode.")

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
            status_led.value(1)
            success = ir.learn(device, button)
            status_led.value(0)
            if success:
                led_blink(3, 60)

        elif cmd == "send":
            if len(parts) < 3:
                print("Usage: send <device> <button>  (e.g., send tv power)")
                continue
            device = parts[1]
            button = parts[2]
            status_led.value(1)
            ir.send(device, button)
            status_led.value(0)

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
    led_blink(2, 100)
    ir = UniversalIR(rx_pin=PIN_IR_RX, tx_pin=PIN_IR_TX, carrier_freq=38000, duty_percent=33)
    cli_loop(ir)

if __name__ == "__main__":
    main()
