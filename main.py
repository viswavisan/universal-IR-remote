"""
main.py - Universal IR Remote Controller for Raspberry Pi Pico (RP2040)
Direct 8x8 Keypad Matrix (64 Buttons, 4.5mm 3x2 Holes) + Dedicated IR TX/RX Optics + RGB Strip
3.7V 18650 2000mAh Rechargeable Battery + TP4056 Type-C USB Charger Subsystem
Finalized V2 22x65 Perfboard Architecture (pcb_design_v2.html).

Hardware Pin Assignment Summary:
  1. Horizontal Pico (90° Rotated): Rows 5 to 12 (Cols B–U).
  2. Direct 8x8 Keypad Matrix (16 GPIOs on Pico Bottom Header, Physical Pins 1 to 20):
       - Rows (8 Outputs, active-LOW):
           * Row 0 -> GP12 (Physical Pin 16 @ Q12 ➔ Row 18 Bus [Top-Side Rail])
           * Row 1 -> GP4  (Physical Pin 6  @ G12 ➔ Row 24 Bus via F18 Jumper)
           * Row 2 -> GP0  (Physical Pin 1  @ B12 ➔ B30 ➔ C30 ➔ Row 30 Bus [Front Wire])
           * Row 3 -> GP15 (Physical Pin 20 @ U12 ➔ U36 ➔ T36 ➔ Row 36 Bus [Front Wire])
           * Row 4 -> GP8  (Physical Pin 11 @ L12 ➔ Row 42 Bus [Backside Lead])
           * Row 5 -> GP7  (Physical Pin 10 @ K12 ➔ Row 48 Bus)
           * Row 6 -> GP3  (Physical Pin 5  @ F12 ➔ F54 ➔ Row 54 Bus [Backside Lead])
           * Row 7 -> GP11 (Physical Pin 15 @ P12 ➔ P15 ➔ Q15 ➔ Q60 ➔ Row 60 Bus [Backside Lead])
       - Columns (8 Inputs with Internal Pull-Ups, idle HIGH):
           * Col 0 (Rail B) -> GP1  (Physical Pin 2  @ C12 ➔ C16 ➔ B16 ➔ B63)
           * Col 1 (Rail D) -> GP2  (Physical Pin 4  @ E12 ➔ D15)
           * Col 2 (Rail G) -> GP5  (Physical Pin 7  @ H12 ➔ H16 ➔ G16 ➔ G63)
           * Col 3 (Rail I) -> GP6  (Physical Pin 9  @ J12 ➔ I15)
           * Col 4 (Rail N) -> GP9  (Physical Pin 12 @ M12 ➔ M15 ➔ N15 ➔ N63)
           * Col 5 (Rail P) -> GP10 (Physical Pin 14 @ O12 ➔ O16 ➔ P16 ➔ P63)
           * Col 6 (Rail S) -> GP13 (Physical Pin 17 @ R12 ➔ R15 ➔ S15 ➔ S63)
           * Col 7 (Rail U) -> GP14 (Physical Pin 19 @ T12 ➔ T15 ➔ U15 ➔ U63)

  3. Dedicated IR Optical Transceivers (Pico Top Header, Physical Pins 21 to 40):
       - IR Transmitter Module:
           * SIG -> GP18 (Physical Pin 24 @ R7, 38kHz Hardware PWM)
           * GND -> Pico Pin 38 (GND @ D5)
           * VCC -> Pico Pin 36 (3.3V System Rail @ F5)
       - IR Demodulating Receiver (VS1838B / TSOP):
           * DAT -> GP17 (Physical Pin 22 @ T7, Active-LOW from R2)
           * GND -> Pico Pin 28 (GND @ M5)
           * VCC -> Pico Pin 36 (3.3V System Rail @ F5)

  4. WS2812B / NeoPixel RGB Addressable LED Strip (Indicator & Keypad Backlight):
       - DIN -> GP16 (Physical Pin 21 @ Perfboard U5)
       - VCC -> Pico Pin 36 (3V3 @ F5) or Pin 39 (VSYS @ C5)
       - GND -> Pico Pin 23 (GND @ S5)

  5. Power Supply (18650 3.7V 2000mAh Battery + TP4056 Type-C Charger):
       - TP4056 OUT+ (via Power Switch) -> Pico Pin 39 (VSYS @ C5)
       - TP4056 OUT- -> Pico Pin 38 (GND @ D5)
       - Battery Monitoring -> GP29 / ADC3 (Internal VSYS/3 divider)

  6. Fixed System Buttons (Hardware-locked & Immutable):
       - Button 2 = LEARN (Amber Cap): Fixed Trigger for Handheld IR Learning
       - Button 3 = MODE  (Emerald Cap): Fixed Appliance Profile Switcher
       * Buttons 2 & 3 CANNOT be changed or overwritten!
       * All other 62 buttons (Button 1, and Buttons 4 to 64) can be programmed/learned freely.
"""

import machine
import time
import sys
from universal_ir import UniversalIR
from keypad import KeypadMatrix8x8, create_keypad, DEFAULT_KEYMAP_8X8
from rgb_strip import RGBIndicator

# =============================================================================
# PIN CONFIGURATION (V2 Layout)
# =============================================================================
PIN_IR_TX = 18       # GP18 (Physical Pin 24 @ R7) -> 38kHz PWM Transmitter
PIN_IR_RX = 17       # GP17 (Physical Pin 22 @ T7) -> Demodulated Data IN (Active-LOW from R2)

# WS2812B NeoPixel RGB Addressable LED Strip
PIN_RGB_LED = 16     # GP16 (Physical Pin 21 @ Perfboard U5) -> WS2812B DIN
NUM_RGB_LEDS = 8     # Number of RGB LEDs on the indicator/backlight strip
rgb = RGBIndicator(pin=PIN_RGB_LED, num_leds=NUM_RGB_LEDS, brightness=0.25)

# Direct 8x8 Keypad Matrix
KEYPAD_ROWS = (11, 4, 3, 12, 8, 7, 0, 15)
KEYPAD_COLS = (1, 2, 5, 6, 9, 10, 13, 14)

# Supported Appliances
SUPPORTED_DEVICES = ["tv", "ac", "soundbar", "projector"]
current_device_index = 0

# =============================================================================
# BUTTON DEFINITIONS & SYSTEM LOCKS
# =============================================================================
# Fixed System Buttons (IMMUTABLE: Cannot be overwritten or selected for learning)
FIXED_SYSTEM_BUTTONS = {
    "2": "LEARN",  # Dedicated Handheld IR Learning Trigger
    "3": "MODE",   # Dedicated Appliance Profile Switcher
}

# Optional Friendly Aliases for standard remote functions.
# All 62 remaining buttons (Button 1, and Buttons 4 to 64) are fully learnable!
BUTTON_ALIASES = {
    "1": "power",
    "4": "mute",
    "5": "up",
    "6": "down",
    "7": "left",
    "8": "right",
    "9": "ok",
    "10": "vol_up",
    "11": "vol_down",
    "12": "ch_up",
    "13": "ch_down",
    "14": "back",
    "15": "home",
    "16": "menu",
}

# On-board LED indicator
try:
    status_led = machine.Pin("LED", machine.Pin.OUT)
except Exception:
    try:
        status_led = machine.Pin(25, machine.Pin.OUT)
    except Exception:
        status_led = None

def led_blink(times=1, delay_ms=50):
    if status_led:
        for _ in range(times):
            status_led.value(1)
            time.sleep_ms(delay_ms)
            status_led.value(0)
            time.sleep_ms(delay_ms)

def wait_for_key_press(keypad, timeout_ms=8000):
    """Wait for any keypress on the keypad with timeout."""
    start = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start) < timeout_ms:
        k = keypad.scan()
        if k:
            return k
        time.sleep_ms(15)
    return None


# =============================================================================
# KEYPAD REMOTE CONTROLLER ENGINE
# =============================================================================
def handle_keypad_matrix(ir):
    """
    Monitor direct 8x8 Keypad Matrix (64 buttons).
    - Button 2 (LEARN): Fixed system key to record new codes into flash.
    - Button 3 (MODE):  Fixed system key to cycle target appliances.
    - All other 62 buttons (Buttons 1, and 4 to 64): Transmit learned signal or learn a new one.
    """
    global current_device_index
    keypad = create_keypad(row_pins=KEYPAD_ROWS, col_pins=KEYPAD_COLS)

    print("\n" + "=" * 70)
    print("      RASPBERRY PI PICO UNIVERSAL IR REMOTE (8x8 MATRIX / 64 KEYS)")
    print("=" * 70)
    print("Hardware Configuration (Finalized V2 Perfboard):")
    print(f"  Rows (8x) -> GP12, GP4, GP0, GP15, GP8, GP7, GP3, GP11")
    print(f"  Cols (8x) -> GP1, GP2, GP5, GP6, GP9, GP10, GP13, GP14")
    print(f"  Optics    -> IR RX @ GP17 (Pin 22) | IR TX @ GP18 (Pin 24)")
    print(f"  RGB Strip -> WS2812B DIN @ GP16 (Pin 21) [{NUM_RGB_LEDS} LEDs Backlight]")
    print("-" * 70)
    print("Fixed System Buttons (IMMUTABLE - CANNOT BE OVERWRITTEN):")
    print("  [ Btn 02: LEARN (Amber Cap) ]  -->  Fixed Handheld IR Learning Trigger")
    print("  [ Btn 03: MODE  (Green Cap) ]  -->  Fixed Appliance Switcher")
    print("-" * 70)
    print("Programmable Buttons (62 Total):")
    print("  Buttons 01, and 04 through 64 are ALL available for IR learning.")
    print("=" * 70)
    active_dev = SUPPORTED_DEVICES[current_device_index]
    rgb.set_mode(active_dev)
    print(f"Active Device: [{active_dev.upper()}] (RGB Backlight Activated)")
    print(">>> REMOTE IS READY! Press any button on the remote... <<<")
    print(">>> Press Button 2 anytime to LEARN a remote button. <<<\n")

    try:
        while True:
            key = keypad.scan()
            if key:
                if status_led:
                    status_led.value(1)

                # =============================================================
                # FIXED BUTTON 2: HANDHELD LEARN TRIGGER (IMMUTABLE)
                # =============================================================
                if key == "2":
                    active_dev = SUPPORTED_DEVICES[current_device_index]
                    print("\n" + "=" * 65)
                    print(f"  [LEARN MODE ACTIVATED] Target Device: [{active_dev.upper()}]")
                    print("  STEP 1: Press the button (1, 4..64) where you want to store the signal.")
                    print("  * Note: Button 2 (LEARN) and Button 3 (MODE) are fixed and cannot be changed.")
                    print("=" * 65)
                    rgb.show_learn_step1()
                    led_blink(2, 60)

                    # Step 1: Wait for destination key to store
                    target_key = wait_for_key_press(keypad, timeout_ms=9000)

                    # Check for timeout or cancel
                    if not target_key:
                        print("[-] Canceled: Timed out waiting for destination key.")
                        print("    Returning to normal remote mode.\n")
                        rgb.restore_mode()
                        if status_led:
                            status_led.value(0)
                        continue

                    # STRICT IMMUTABILITY CHECK: Reject Button 2 or Button 3
                    if target_key in FIXED_SYSTEM_BUTTONS:
                        sys_btn_role = FIXED_SYSTEM_BUTTONS[target_key]
                        print("\n" + "!" * 65)
                        print(f"  [-] REJECTED: Button [{target_key}] is a FIXED SYSTEM BUTTON ({sys_btn_role})!")
                        print(f"      Button {target_key} is permanently locked and CANNOT be overwritten.")
                        print("      Please pick any other button: Button 1, or Buttons 4 through 64.")
                        print("!" * 65 + "\n")
                        rgb.flash_warning()
                        led_blink(4, 40)
                        if status_led:
                            status_led.value(0)
                        continue

                    # Determine naming for the learnable button
                    alias = BUTTON_ALIASES.get(target_key)
                    btn_id = f"btn_{target_key}"
                    label = f"Button [{target_key}] ({alias})" if alias else f"Button [{target_key}]"

                    print("\n" + "=" * 65)
                    print(f"  STEP 2: SIGNAL MATCHING FOR {label}")
                    print(f"  Target Device: [{active_dev.upper()}]")
                    print("  Instructions : Point original remote at the TSOP IR sensor (GP17)")
                    print("                 and press the button NOW!")
                    print("  Waiting for 38kHz infrared pulses (timeout in 7 seconds)...")
                    print("=" * 65)

                    rgb.show_learn_step2()
                    if status_led:
                        status_led.value(1)

                    # Step 2: Signal Matching / Capture IR pulses
                    pulses = ir.capture_raw(timeout_ms=7000)
                    if status_led:
                        status_led.value(0)

                    if pulses and len(pulses) >= 4:
                        # Save under btn_id (e.g. btn_1, btn_4) and also alias if exists
                        ir.save_code(active_dev, btn_id, pulses)
                        if alias:
                            ir.save_code(active_dev, alias, pulses)

                        print("\n" + "*" * 65)
                        print(f"  [+] SIGNAL MATCHED & SAVED SUCCESSFULLY!")
                        print(f"  Device Name    : [{active_dev.upper()}]")
                        print(f"  Assigned Key   : {label}")
                        print(f"  Captured Pulses: {len(pulses)} raw microsecond transitions")
                        print(f"  Storage Keys   : '{btn_id}'" + (f" and '{alias}'" if alias else ""))
                        print(f"  Storage Status : Permanently saved in flash (ir_codes.json)")
                        print("*" * 65)
                        print(f"  --> Press Button [{target_key}] anytime to transmit this signal!\n")

                        rgb.flash_success()
                        led_blink(3, 80)
                        time.sleep_ms(400)
                    else:
                        print("\n[-] SIGNAL MATCHING TIMEOUT: No valid IR signal detected.")
                        print("    Tips:")
                        print("      - Point remote 2-5 cm directly in front of the GP17 receiver.")
                        print("      - Press Button 2 anytime to try again.\n")
                        rgb.flash_error()
                        time.sleep_ms(400)

                # =============================================================
                # FIXED BUTTON 3: APPLIANCE MODE SWITCHER (IMMUTABLE)
                # =============================================================
                elif key == "3":
                    current_device_index = (current_device_index + 1) % len(SUPPORTED_DEVICES)
                    active_dev = SUPPORTED_DEVICES[current_device_index]
                    print(f"\n[MODE BUTTON 3] Target Device Switched to: ---> [{active_dev.upper()}] <---")
                    rgb.set_mode(active_dev)
                    led_blink(current_device_index + 1, 60)

                # =============================================================
                # ALL OTHER 62 BUTTONS (1, and 4 to 64): TRANSMIT LEARNED SIGNAL
                # =============================================================
                else:
                    active_dev = SUPPORTED_DEVICES[current_device_index]
                    alias = BUTTON_ALIASES.get(key)
                    btn_id = f"btn_{key}"
                    label = f"Button [{key}] ({alias})" if alias else f"Button [{key}]"

                    # Check if learned signal exists under btn_id or alias
                    action_to_send = None
                    if ir.get_code(active_dev, btn_id):
                        action_to_send = btn_id
                    elif alias and ir.get_code(active_dev, alias):
                        action_to_send = alias

                    if action_to_send:
                        print(f"[*] Pressed {label} ➜ Transmitting '{active_dev}.{action_to_send}'...")
                        rgb.flash_tx()
                        ir.send(active_dev, action_to_send, repeat=2)
                        print(f"    [+] Transmitted 38kHz signal for {label} successfully!")
                    else:
                        print(f"[*] Pressed {label}")
                        print(f"    [-] NOTICE: Button [{key}] has not been programmed for '{active_dev}' yet.")
                        print(f"        -> Press Button 2 (LEARN) on the remote to program it now!")

                if status_led:
                    status_led.value(0)
            time.sleep_ms(15)
    except KeyboardInterrupt:
        print("\n[!] Exited Keypad Remote Mode. Entering Serial CLI Loop...")
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
    print("  rgb <subcmd>              - RGB strip control (mode, rainbow, on, off)")
    print("  test-ir                   - Test IR LED connection & loopback")
    print("  keypad                    - Start 8x8 Keypad Remote (64 buttons)")
    print("  help                      - Show this command list")
    print("=" * 60)
    print("System Rules:")
    print("  - Button 2 (LEARN) & Button 3 (MODE) are FIXED SYSTEM BUTTONS.")
    print("  - Buttons 1, and 4 to 64 are all fully programmable.")
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
                print("Usage: learn <device> <button>  (e.g., learn tv 1, learn tv power, learn tv 45)")
                continue
            device = parts[1]
            button = parts[2].lower()

            # Protect fixed system buttons 2 and 3
            if button in ("2", "3", "btn_2", "btn_3", "learn", "mode"):
                print(f"[-] ERROR: '{button}' is a FIXED SYSTEM BUTTON and cannot be overwritten.")
                print("    All other buttons (Buttons 1, and 4 to 64) can be programmed freely.")
                continue

            # Standardize button storage key
            storage_key = button
            if button.isdigit():
                storage_key = f"btn_{button}"

            rgb.show_learn_step2()
            if status_led:
                status_led.value(1)
            success = ir.learn(device, storage_key)
            if status_led:
                status_led.value(0)
            if success:
                rgb.flash_success()
                led_blink(3, 60)
            else:
                rgb.flash_error()

        elif cmd == "send":
            if len(parts) < 3:
                print("Usage: send <device> <button>  (e.g., send tv 1, send tv power)")
                continue
            device = parts[1]
            button = parts[2].lower()

            action = button
            if button.isdigit():
                btn_id = f"btn_{button}"
                alias = BUTTON_ALIASES.get(button)
                if ir.get_code(device, btn_id):
                    action = btn_id
                elif alias and ir.get_code(device, alias):
                    action = alias
                else:
                    action = btn_id

            rgb.flash_tx()
            if status_led:
                status_led.value(1)
            ir.send(device, action, repeat=2)
            if status_led:
                status_led.value(0)

        elif cmd == "rgb":
            subcmd = parts[1].lower() if len(parts) >= 2 else "status"
            if subcmd in ("on", "enable"):
                rgb.backlight_on = True
                rgb.restore_mode()
                print("[+] RGB Backlight enabled.")
            elif subcmd in ("off", "disable"):
                rgb.backlight_on = False
                rgb.clear()
                print("[+] RGB Backlight turned off.")
            elif subcmd in ("rainbow", "cycle"):
                print("[*] Running RGB Rainbow Cycle...")
                rgb.rainbow_cycle(loops=2, speed_ms=8)
                print("[+] Done.")
            elif subcmd in SUPPORTED_DEVICES:
                rgb.set_mode(subcmd)
                print(f"[+] RGB set to '{subcmd.upper()}' mode color.")
            elif subcmd.replace(".", "", 1).isdigit():
                lvl = float(subcmd)
                rgb.set_brightness(lvl)
                print(f"[+] RGB brightness set to {int(lvl * 100)}%.")
            else:
                print("Usage: rgb [tv | ac | soundbar | projector | on | off | rainbow | <brightness 0.1-1.0>]")

        elif cmd in ("test", "test-ir"):
            print(f"\n[*] Testing IR LED connection on GP{PIN_IR_TX} (Pin 25)...")
            detected_count = 0
            for i in range(5):
                ir.tx_pwm.duty_u16(ir.duty_on)
                rgb.flash_tx(20)
                if status_led:
                    status_led.value(1)
                time.sleep_ms(8)
                rx_val = ir.rx_pin.value()
                ir.tx_pwm.duty_u16(0)
                if status_led:
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
                print("[-] Result: No loopback detected. Ensure optics can see each other.")

        elif cmd == "repeat":
            if len(parts) < 4:
                print("Usage: repeat <device> <button> <count>  (e.g., repeat tv 1 5)")
                continue
            device = parts[1]
            button = parts[2].lower()
            try:
                count = int(parts[3])
            except ValueError:
                print("[-] Count must be a valid number.")
                continue

            action = button
            if button.isdigit():
                btn_id = f"btn_{button}"
                alias = BUTTON_ALIASES.get(button)
                if ir.get_code(device, btn_id):
                    action = btn_id
                elif alias and ir.get_code(device, alias):
                    action = alias
                else:
                    action = btn_id

            rgb.flash_tx()
            if status_led:
                status_led.value(1)
            ir.send(device, action, repeat=count)
            if status_led:
                status_led.value(0)

        elif cmd == "list":
            codes = ir.list_codes()
            if not codes:
                print("[-] No IR codes stored in database yet.")
                print("    Use: learn <device> <button> or press Button 2 on the remote to record one!")
            else:
                print("\nStored Devices and Buttons:")
                for dev, buttons in codes.items():
                    print(f"  Device: [{dev}]")
                    for b in sorted(buttons):
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
    # Boot sequence: Smooth rainbow wipe, then establish default device ambient color
    rgb.rainbow_cycle(loops=1, speed_ms=4)
    rgb.set_mode(SUPPORTED_DEVICES[0])
    ir = UniversalIR(rx_pin=PIN_IR_RX, tx_pin=PIN_IR_TX, carrier_freq=38000, duty_percent=33)
    # Launch direct Keypad Remote mode immediately on boot
    handle_keypad_matrix(ir)

if __name__ == "__main__":
    main()
