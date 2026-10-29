"""
universal_ir.py - Universal IR Remote Engine for Raspberry Pi Pico (RP2040)
Captures, stores, and transmits raw infrared pulse timings for universal protocol compatibility.
"""

import machine
import time
import json
import gc

class UniversalIR:
    """
    Universal Infrared Receiver, Transmitter, and Code Database.
    Uses raw microsecond timing capture to support any IR protocol
    (NEC, Sony, Philips RC5/RC6, Samsung, LG, AC remotes, etc.).
    """

    def __init__(self, rx_pin=15, tx_pin=16, carrier_freq=38000, duty_percent=33, storage_file="ir_codes.json"):
        """
        :param rx_pin: GPIO pin connected to demodulating IR receiver (e.g., VS1838B / TSOP38238).
                       Receiver output is typically Active-LOW.
        :param tx_pin: GPIO pin connected to IR LED drive transistor base (via 1k resistor).
        :param carrier_freq: Carrier frequency in Hz (typically 38000 Hz / 38 kHz).
        :param duty_percent: Carrier duty cycle percentage (33% is standard for IR LEDs).
        :param storage_file: Path to JSON database file on Pico flash filesystem.
        """
        self.rx_pin_num = rx_pin
        self.tx_pin_num = tx_pin
        self.carrier_freq = carrier_freq
        self.storage_file = storage_file

        # Calculate duty cycle for 16-bit PWM (0 - 65535)
        # 33% duty cycle ~ 21626
        self.duty_on = int(65535 * (duty_percent / 100.0))
        self.duty_off = 0

        # Initialize IR Receiver pin with pull-up resistor (idle state is HIGH)
        self.rx_pin = machine.Pin(self.rx_pin_num, machine.Pin.IN, machine.Pin.PULL_UP)

        # Initialize IR Transmitter pin with hardware PWM (starts OFF)
        self.tx_pwm = machine.PWM(machine.Pin(self.tx_pin_num))
        self.tx_pwm.freq(self.carrier_freq)
        self.tx_pwm.duty_u16(self.duty_off)

        # In-memory database of learned IR codes
        self.database = {}
        self.load_database()

    # =========================================================================
    # Storage Management
    # =========================================================================

    def load_database(self):
        """Load stored IR codes from flash storage."""
        try:
            with open(self.storage_file, "r") as f:
                self.database = json.load(f)
            print(f"[Storage] Loaded {len(self.database)} device(s) from '{self.storage_file}'.")
        except (OSError, ValueError):
            print(f"[Storage] No valid database found at '{self.storage_file}'. Initializing new database.")
            self.database = {}
            self.save_database()

    def save_database(self):
        """Save the in-memory database to flash storage."""
        try:
            with open(self.storage_file, "w") as f:
                json.dump(self.database, f)
            print(f"[Storage] Database successfully saved to '{self.storage_file}'.")
            return True
        except Exception as e:
            print(f"[Storage Error] Failed to save database: {e}")
            return False

    def save_code(self, device, button, pulses):
        """Save a learned pulse train for a specific device and button."""
        device = device.strip().lower()
        button = button.strip().lower()

        if device not in self.database:
            self.database[device] = {}

        self.database[device][button] = pulses
        return self.save_database()

    def get_code(self, device, button):
        """Retrieve pulse timings for a device and button."""
        device = device.strip().lower()
        button = button.strip().lower()
        return self.database.get(device, {}).get(button, None)

    def delete_code(self, device, button=None):
        """Delete an entire device or a specific button from a device."""
        device = device.strip().lower()
        if device not in self.database:
            return False

        if button is None:
            del self.database[device]
            self.save_database()
            return True
        else:
            button = button.strip().lower()
            if button in self.database[device]:
                del self.database[device][button]
                # Clean up empty device
                if not self.database[device]:
                    del self.database[device]
                self.save_database()
                return True
        return False

    def list_codes(self):
        """Return a dictionary of all devices and their recorded buttons."""
        summary = {}
        for dev, btns in self.database.items():
            summary[dev] = list(btns.keys())
        return summary

    # =========================================================================
    # IR Signal Reception (Learning Mode)
    # =========================================================================

    def capture_raw(self, timeout_ms=8000, end_packet_timeout_us=40000, max_pulses=1000):
        """
        Record a raw IR signal pulse train.
        
        :param timeout_ms: Maximum time in ms to wait for the user to press a button.
        :param end_packet_timeout_us: Microseconds of idle (HIGH) that marks the end of an IR frame.
                                      Standard IR frames have inter-frame gaps > 20ms - 40ms.
        :param max_pulses: Safety cap on number of transitions to record.
        :return: List of pulse durations in microseconds [mark0, space0, mark1, space1, ...]
                 or None if timed out.
        """
        rx = self.rx_pin
        pulses = []

        gc.collect()  # Clean up RAM before time-critical capture

        print(f"[*] Point remote at receiver (GPIO {self.rx_pin_num}) and press the button...")

        # 1. Wait for the signal to start (Receiver goes LOW on first carrier burst)
        start_wait = time.ticks_ms()
        while rx.value() == 1:
            if time.ticks_diff(time.ticks_ms(), start_wait) > timeout_ms:
                print("[-] Timeout: No IR signal detected.")
                return None

        # 2. Capture transitions in a tight timing loop
        current_state = 0  # 0 = LOW (Mark/Carrier present), 1 = HIGH (Space/Idle)
        last_tick = time.ticks_us()

        while len(pulses) < max_pulses:
            # Measure time until pin state changes
            while rx.value() == current_state:
                now = time.ticks_us()
                elapsed = time.ticks_diff(now, last_tick)

                # If pin has stayed HIGH (idle) for longer than end_packet_timeout_us, packet is done
                if current_state == 1 and elapsed > end_packet_timeout_us:
                    # Clean up: we ignore the long trailing idle space
                    return pulses

            # Pin changed state
            now = time.ticks_us()
            duration = time.ticks_diff(now, last_tick)
            last_tick = now
            current_state = 1 if current_state == 0 else 0
            pulses.append(duration)

        return pulses

    def learn(self, device, button, timeout_ms=8000):
        """
        High-level helper to capture and store an IR signal.
        """
        pulses = self.capture_raw(timeout_ms=timeout_ms)
        if not pulses:
            return False

        if len(pulses) < 4:
            print(f"[-] Signal too short ({len(pulses)} transitions). Ignored as noise.")
            return False

        print(f"[+] Successfully captured {len(pulses)} pulse edges!")
        print(f"    Leading mark: {pulses[0]} us, Leading space: {pulses[1]} us")
        
        success = self.save_code(device, button, pulses)
        if success:
            print(f"[+] Stored under Device: '{device}', Button: '{button}'")
        return success

    # =========================================================================
    # IR Signal Transmission (Replication Mode)
    # =========================================================================

    def transmit_raw(self, pulses):
        """
        Transmit a raw pulse duration array using 38kHz PWM carrier modulation.
        
        :param pulses: List of microsecond durations [mark0, space0, mark1, space1, ...].
                       Even index = Mark (Carrier ON), Odd index = Space (Carrier OFF).
        """
        if not pulses or len(pulses) < 2:
            print("[-] Invalid pulse data to transmit.")
            return

        pwm = self.tx_pwm
        duty_on = self.duty_on
        duty_off = self.duty_off

        # Critical: turn interrupts off or minimize GC impact during transmission
        gc.collect()

        # Transmit pulse train
        is_mark = True
        for duration in pulses:
            if is_mark:
                pwm.duty_u16(duty_on)
            else:
                pwm.duty_off = 0
                pwm.duty_u16(duty_off)

            time.sleep_us(duration)
            is_mark = not is_mark

        # Ensure carrier is completely off after transmission
        pwm.duty_u16(duty_off)

    def send(self, device, button, repeat=1, delay_between_repeats_ms=45):
        """
        Send a stored IR command by device and button name.
        
        :param device: Target device name (e.g. 'tv', 'ac', 'soundbar')
        :param button: Target button name (e.g. 'power', 'vol_up')
        :param repeat: Number of times to send the frame (default 1)
        :param delay_between_repeats_ms: Delay in ms between repeat frames
        """
        pulses = self.get_code(device, button)
        if not pulses:
            print(f"[-] Command '{button}' for device '{device}' not found in database.")
            return False

        print(f"[>] Sending '{device}.{button}' ({len(pulses)} pulses, {repeat}x)...")
        for i in range(repeat):
            self.transmit_raw(pulses)
            if i < repeat - 1:
                time.sleep_ms(delay_between_repeats_ms)

        print("[+] Sent successfully.")
        return True
