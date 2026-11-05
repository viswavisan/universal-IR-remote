# Universal IR Remote for Raspberry Pi Pico (MicroPython)

A complete, protocol-agnostic Universal Infrared (IR) Remote Controller built for the **Raspberry Pi Pico (RP2040)** and **Pico W** running MicroPython.

It can **learn** any IR remote signal from your existing remotes (TV, AC, Soundbar, Projector, Set-Top Box, Fan, etc.), **save** them permanently to flash memory as JSON, and **replicate/transmit** the exact 38 kHz modulated IR signal so you can control all your appliances from a single remote.

---

## Key Features

- **True Universal Protocol Compatibility**: Instead of hardcoding protocols (like only NEC or Sony), it captures raw microsecond mark/space transitions. This allows it to learn **ANY** IR protocol (NEC, Sony SIRC, Philips RC-5/RC-6, Samsung, Panasonic, Sharp, and even long Air Conditioner remotes with 200+ pulse frames).
- **Persistent Storage**: All learned signals are saved in flash memory (`ir_codes.json`) as structured devices and buttons. They survive reboots and power cycles.
- **Hardware PWM 38 kHz Carrier**: Uses the RP2040's hardware PWM slice to generate an accurate 38 kHz carrier frequency at a standard 33% duty cycle.
- **Interactive Serial CLI**: Learn, test, list, and transmit commands in real-time via USB Serial (Thonny, minicom, PuTTY, or screen).
- **Physical Pushbutton Support**: Easily map physical buttons on Pico GPIO pins to trigger commands (e.g. GPIO 14 = TV Power, GPIO 11 = AC Power).
- **Visual Feedback**: Blinks the on-board LED during learning, transmission, and operation.

---

## Hardware Requirements & Wiring

### 1. Bill of Materials (BOM) & Cost Estimation

| Item | Component | Specification / Model | Qty | Designator | Est. Unit Cost | Est. Total Cost | Purpose / Sourcing Notes |
|:---:|---|---|:---:|:---:|:---:|:---:|---|
| **1** | **Microcontroller Board** | Raspberry Pi Pico / Pico H (RP2040, Dual-Core 133MHz, 2MB Flash) | 1 | `U1` | ₹370 / $4.20 | **₹370 / $4.20** | Main controller: captures raw pulses, scans keypad, generates 38kHz PWM. (Robu, Silverline, Raspberry Pi direct) |
| **2** | **4x4 Matrix Keypad** | 16-Key Membrane / Tactile Matrix (8-pin 2.54mm pitch female header) | 1 | `SW1-SW16` | ₹90 / $1.20 | **₹90 / $1.20** | Remote buttons: 0-9 digits, A (Mode cycle), B (Vol+), C (Vol-), D (Power), * (Mute), # (Enter) |
| **3** | **3-Pin 5V IR LED Module** | High-Power 940nm IR Transmitter Module (with driver transistor & 5V boost) | 1 | `MOD_TX` | ₹30 / $0.40 | **₹30 / $0.40** | High-output transmitter: onboard driver switches 5V VBUS for ~100mA peak pulses with 10–15m range |
| **4** | **IR Receiver Sensor** | VS1838B (or TSOP38238) 38kHz Demodulating IR Receiver | 1 | `U2` | ₹15 / $0.20 | **₹15 / $0.20** | Standalone receiver unit: learns raw 38kHz signals from existing remotes; physically separated to avoid optical crosstalk |
| **5** | **Battery Holder** | 3x AAA Battery Holder with 150mm lead wires (Red/Black) | 1 | `BT1` | ₹40 / $0.55 | **₹40 / $0.55** | Enclosed or open 3x AAA series compartment supplying 4.5V DC to VSYS |
| **6** | **Batteries** | 1.5V AAA Alkaline cells (or 1.2V AAA NiMH rechargeable cells) | 3 | `BAT1-3` | ₹25 / $0.35 | **₹75 / $1.05** | Portable handheld power; Pico operates reliably from 4.5V down to 2.0V |
| **7** | **Main Power Switch** | SPST Miniature Slide Switch (Panel or PCB Mount, 2-pin / 3-pin) | 1 | `SW_PWR` | ₹10 / $0.15 | **₹10 / $0.15** | Disconnects battery from Pico VSYS (Pin 39) for zero standby battery drain |
| **8** | **Breadboard / Perfboard** | Half-size solderless breadboard (400 tie-points) or 5x7cm protoboard | 1 | `PCB` | ₹75 / $1.00 | **₹75 / $1.00** | Prototyping chassis or solderable perfboard for final handheld build |
| **9** | **DuPont Jumper Wires** | Male-to-Female & Male-to-Male 10cm / 20cm flexible jumper wires | ~15 | `W1-W15` | ₹35 / $0.50 | **₹35 / $0.50** | Interconnect wiring between Pico, keypad, optics, and battery holder |
| **10** | **0.96" I2C OLED Display** | 128x64 Monochrome SSD1306 (4-Pin: GND, VCC, SCL, SDA) | 1 | `DISP1` | ₹150 / $1.80 | **₹150 / $1.80** | Visual HUD: Displays target device, key pressed, IR command sent, and learning progress |
| | **TOTAL ESTIMATED COST** | | | | | **₹850 / ~$10.50** | *(Full remote with OLED HUD, battery pack, optics, and keypad)* |

> [!TIP]
> **Cost Breakdown & Sourcing Tips:**
> - **Core Electronics Only** (Pico + Keypad + 3-Pin IR LED Module + VS1838B + 0.96" OLED): **~₹655 / $7.80**
> - **Direct Keypad Driving**: The 4x4 keypad matrix connects directly to 8 Pico GPIOs using RP2040 internal pull-ups (no I2C backpack needed).
> - **OLED on Hardware I2C0**: The OLED screen connects neatly to Pico Pins 21 & 22 (`GP16` SDA & `GP17` SCL) on the right rail.
> - **Optical Layout Advantage**: Positioned with straight horizontal wiring to Pico pins 13, 14, 15, 18, and 19 for minimal trace length and clean routing.

---

### 2. Wiring Diagram & Optical Architecture (Top 5V Blaster & Bottom/Side Learning Eye)

The transmitter (Top 5V IR LED Module) and receiver (Bottom/Side VS1838B) are placed at opposite ends of the remote for **zero optical crosstalk**:

```text
================================================================================
 MODULE A: TOP 3-PIN 5V HIGH-POWER IR TRANSMITTER (3 WIRES)
================================================================================
  Pin 1: 5V (VBUS / VSYS) ────> Pico Pin 40 (VBUS 5V High-Power Rail)
  Pin 2: GND (Ground)     ────> Pico Pin 18 (GND Return)
  Pin 3: IN (Signal)      ────> Pico GP14 (Physical Pin 19, 38kHz PWM Slice 7A)
  
  * Built-in driver transistor pumps ~100mA pulses for 10–15 meter range!
  * Located at the TOP FRONT of remote pointing toward TV/appliances.

================================================================================
 MODULE B: BOTTOM / SIDE 3-PIN VS1838B IR RECEIVER SENSOR (3 WIRES)
================================================================================
                    (Front Facing - Lens Bump Toward Incoming Remote)
                           ┌─────────────────┐
                           │   [VS1838B]     │
                           │     ( █ )       │  <- Dedicated Learning Sensor
                           └────┬───┬───┬────┘
                                │   │   │
                          Pin:  1   2   3
                                │   │   │
  Pin 1: OUT (Active-LOW) ──────┘   │   │  ───> Pico GP11 (Physical Pin 15)
  Pin 2: GND (Ground Return) ───────┘   │  ───> Pico Pin 13 (GND)
  Pin 3: VCC (3.3V Power) ──────────────┘  ───> Pico GP10 (Physical Pin 14, driven HIGH)

  * Positioned at the BOTTOM (or side bezel) dedicated to learning codes.
  * 170mm physical separation prevents transmitter blast from blinding the receiver!

================================================================================
 MODULE C: 0.96" I2C OLED DISPLAY (SSD1306 128x64 - 4 WIRES)
================================================================================
  Pin 1: GND (Ground)  ────> Pico Pin 23 (GND)
  Pin 2: VCC (3.3V)    ────> Pico Pin 36 (3V3_OUT)
  Pin 3: SCL (Clock)   ────> Pico GP17 (Physical Pin 22, I2C0 SCL)
  Pin 4: SDA (Data)    ────> Pico GP16 (Physical Pin 21, I2C0 SDA)

  * Real-time Heads-Up Display (HUD) mounted on top of the remote:
    - Inverted top banner displaying target appliance: [TV], [AC], [SOUNDBAR], [PROJECTOR]
    - Keypress & command telemetry: "Key: [B]" -> "Cmd: VOL_UP"
    - Live transmission feedback & Learning Mode visual prompts ("Aim remote at RX...")
    - Auto-detection: If the display is unplugged, system runs in headless serial mode.
```

#### Why Separate the Top Blaster and the Bottom/Side Receiver?
1. **Zero Optical Blinding / Crosstalk**:
   - The top 5V IR LED fires at full 100mA power forward toward the TV.
   - The bottom/side receiver listens in the opposite direction for original remotes during learning mode.
   - Separated by 170mm across the remote shell, there is zero light leak or receiver saturation.
2. **Intuitive Learning Ergonomics**:
   - Point your old remote at the bottom bezel of the universal remote to teach it commands (standard Logitech Harmony style).
   - Once learned, aim the top of the remote at your TV/AC to control it.
3. **Simple 3-Wire Pinouts**:
   - **Transmitter (Top)**: `[5V: Pin 40 (VBUS), GND: Pin 18, IN: GP14 (Pin 19)]`.
   - **Receiver (Bottom/Side)**: `[DATA: GP11 (Pin 15), GND: Pin 13, VCC: GP10 (Pin 14)]`.
4. **Dedicated 5V High-Power Transistor Boost**:
   - The transmitter module carries an onboard transistor that switches 5V directly to the IR LED, delivering ~100mA peak pulses for 10–15m coverage without loading the RP2040 GPIO.

#### Power Supply: 3x AAA Battery Pack (4.5V Alkaline / 3.6V NiMH)
To make the remote completely wireless and handheld:
- **Components**:
  - **3x AAA Battery Holder** (supports standard 1.5V Alkaline for 4.5V, or rechargeable 1.2V NiMH AAA cells for 3.6V).
  - **SPST Slide Switch** (Main ON/OFF switch).
- **Wiring Details**:
  - **Battery (+) (Red Wire)** $\rightarrow$ **Slide Switch IN**
  - **Slide Switch OUT** $\rightarrow$ **Pico VSYS (Pin 39)** and **IR LED 100Ω Resistor**
  - **Battery (-) (Black Wire)** $\rightarrow$ **Pico GND (Pin 38)**
- **Why Pico VSYS (Pin 39)?**: The Raspberry Pi Pico has a built-in RT6154 buck-boost switching regulator that accepts **1.8V to 5.5V** on VSYS. It easily handles the full discharge curve of 3 AAA batteries (4.5V down to 2.0V) while outputting a stable 3.3V for the RP2040 and IR receiver.
- **Power Switch**: Sliding the switch to OFF cuts all power, eliminating standby battery drain.
- **External USB Access**: The Raspberry Pi Pico is mounted in the lower grip with its micro-USB port facing outward at the bottom of the remote casing. This allows convenient firmware flashing, code updating, and serial monitoring directly via USB without opening the case.
- **Transmission Range**: Powered from 4.5V via the 100Ω current limiter, the 940nm IR LED receives ~30–35mA pulse current for effective 5–8 meter line-of-sight range.

#### 4x4 Matrix Keypad (Direct 8-Pin GPIO Matrix)
The 4x4 matrix keypad connects directly to the Raspberry Pi Pico without requiring any external I2C expander chips, level shifters, or pull-up resistors (the RP2040 internal pull-ups handle everything):

- **Keypad Ribbon Pinout (Pins 1 to 8)**:
  - **Rows 0..3 (Outputs)**:
    - Pin 1 (Row 0) $\rightarrow$ **Pico GP2 (Physical Pin 4)**
    - Pin 2 (Row 1) $\rightarrow$ **Pico GP3 (Physical Pin 5)**
    - Pin 3 (Row 2) $\rightarrow$ **Pico GP4 (Physical Pin 6)**
    - Pin 4 (Row 3) $\rightarrow$ **Pico GP5 (Physical Pin 7)**
  - **Cols 0..3 (Inputs with internal Pull-Up)**:
    - Pin 5 (Col 0) $\rightarrow$ **Pico GP6 (Physical Pin 9)**
    - Pin 6 (Col 1) $\rightarrow$ **Pico GP7 (Physical Pin 10)**
    - Pin 7 (Col 2) $\rightarrow$ **Pico GP8 (Physical Pin 11)**
    - Pin 8 (Col 3) $\rightarrow$ **Pico GP9 (Physical Pin 12)**

> [!TIP]
> **Clean Left-Rail Header (Physical Pins 4 to 19)**:
> All active connections are neatly arranged along the left side of the Raspberry Pi Pico:
> - **Pins 4–7 (GP2–GP5)**: Keypad Rows 0..3
> - **Pin 8 (GND)**: System Ground
> - **Pins 9–12 (GP6–GP9)**: Keypad Cols 0..3
> - **Pin 13 (GND)**: IR Receiver Ground
> - **Pin 14 (GP10)**: IR Receiver 3.3V Power OUT (driven HIGH)
> - **Pin 15 (GP11)**: IR Receiver Demodulated Data IN
> - **Pin 18 (GND)**: IR LED Ground Return
> - **Pin 19 (GP14)**: 38 kHz Hardware PWM TX (IR Transmitter IN)
> - **Pin 40 (VBUS)**: 5V High-Power Rail (IR Transmitter 5V)

##### Remote Keypad Layout:
```text
  [ 1: POWER ON ]   [ 2: UP (▲)  ]   [ 3: POWER OFF ]   [ A: LEARN   ] <- Row 0 (GP2, Pin 4)
  [ 4: LEFT (◀) ]   [ 5: OK/ENT  ]   [ 6: RIGHT (▶) ]   [ B: MODE    ] <- Row 1 (GP3, Pin 5)
  [ 7: VOL -    ]   [ 8: DOWN(▼) ]   [ 9: VOL +     ]   [ C: MUTE    ] <- Row 2 (GP4, Pin 6)
  [ *           ]   [ 0          ]   [ #            ]   [ D: POWER   ] <- Row 3 (GP5, Pin 7)
        ^                 ^                 ^                 ^
      Col 0             Col 1             Col 2             Col 3
      (GP6)             (GP7)             (GP8)             (GP9)
     (Pin 9)           (Pin 10)          (Pin 11)          (Pin 12)
```

##### Key Action Map:
| Key | Remote Action | Description |
|:---:|---|---|
| **`A`** | **LEARN** | Handheld learning mode (Press `A` ➜ Pick Key ➜ Match Signal ➜ Auto-save) |
| **`B`** | **MODE** | Cycle target device: `TV` $\rightarrow$ `AC` $\rightarrow$ `SOUNDBAR` $\rightarrow$ `PROJECTOR` |
| **`1`** | **power_on** | Dedicated Power ON command |
| **`3`** | **power_off** | Dedicated Power OFF command |
| **`2`** | **up** | Directional D-Pad: Navigate UP (▲) |
| **`4`** | **left** | Directional D-Pad: Navigate LEFT (◀) |
| **`5`** | **ok** | Directional D-Pad: OK / ENTER / Select |
| **`6`** | **right** | Directional D-Pad: Navigate RIGHT (▶) |
| **`8`** | **down** | Directional D-Pad: Navigate DOWN (▼) |
| **`7`** | **vol_down** | Volume Down (VOL −) |
| **`9`** | **vol_up** | Volume Up (VOL +) |
| **`C`** | **mute** | Mute / Unmute Audio Toggle |

---

## File Structure

```text
universal-IR-remote/
├── universal_ir.py        # Core engine: raw timing capture, 38kHz PWM, flash JSON storage
├── keypad.py              # Direct 4x4 matrix keypad scanner (8 GPIOs, zero ICs)
├── ssd1306.py             # Official MicroPython SSD1306 I2C framebuf display driver
├── oled_ui.py             # High-level OLED Heads-Up Display manager (HUD, status, prompts)
├── main.py                # Main interactive remote application & 4x4 keypad loop
├── test_all.py            # Complete modular hardware diagnostic & test suite
├── circuit_visualizer.html# Interactive browser visualizer with clickable 4x4 keypad & OLED
├── pcb_design.html        # Interactive 28x36 prototype perfboard PCB designer & solder guide
├── .gitignore             # Standard Python / project ignore rules
└── README.md              # Documentation and wiring guide
```

---

## Interactive Visualizers & PCB Designer

This project includes two complementary browser-based interactive visualizers:

### 1. Circuit Schematic & Virtual Handheld Remote
Open [`circuit_visualizer.html`](circuit_visualizer.html) in your browser:
- **Clickable 4x4 Keypad & Live OLED**: Test any of the 16 buttons interactively with real-time multi-line OLED feedback.
- **2-Step Learn Workflow**: Test `Key A` (Learn), target key selection, and signal matching right in your browser.
- **Device Mode Switching**: Press `Key B` to toggle between TV, AC, Soundbar, and Projector profiles.
- **Live Signal Trace**: Real-time oscillogram of demodulated 38 kHz pulse trains.

### 2. Prototype Perfboard PCB Designer (70×90mm)
Open [`pcb_design.html`](pcb_design.html) in your browser:
- **True 2.54mm (0.1") Prototype Grid**: 28 columns (A–AB) × 36 rows (1–36) matching standard 70×90mm double-sided FR4 protoboards (1,008 plated through-holes).
- **Dual-Perspective Views**:
  - **Top View (Component Side)**: Raspberry Pi Pico DIP-40 socket, 0.96" OLED, 4×4 Keypad socket, IR RX/TX modules, slide switch, battery pads, and color-coded top jumper wires.
  - **Bottom View (Solder Side)**: Mirrored view showing solder bridge rails and bare copper bus wires for hassle-free hand soldering!
  - **X-Ray View**: Translucent composite view of top jumpers and bottom traces simultaneously.
- **Interactive Pad Inspector & Netlist Highlighter**: Click or hover any pad on the perfboard to inspect coordinates (e.g. `J17`), connected component pins, wire color, and physical soldering tips.
- **Step-by-Step Soldering Guide**: Built-in 8-step assembly checklist with safe multimeter continuity testing instructions before powering.

---

## Installation & Setup

1. **Install MicroPython on your Pico**:
   - Download the latest MicroPython `.uf2` from [micropython.org/download/rp2-pico](https://micropython.org/download/rp2-pico/).
   - Hold the `BOOTSEL` button on your Pico, plug it into your computer via USB, and drag the `.uf2` file onto the `RPI-RP2` drive.

2. **Upload the Code**:
   - Open **Thonny IDE**.
   - In Thonny, set interpreter to **MicroPython (Raspberry Pi Pico)**.
   - Save `universal_ir.py`, `keypad.py`, and `main.py` directly to the Pico's root directory (`/`).

3. **Run the Code**:
   - Click the green **Run** button in Thonny or reset the Pico.

---

## How to Use

### 1. Interactive CLI Mode

When running `main.py`, you will see the interactive prompt:

```text
============================================================
      RASPBERRY PI PICO - UNIVERSAL IR REMOTE
============================================================
Available Commands:
  learn <device> <button>   - Record IR signal for a button
  send <device> <button>    - Transmit a stored IR signal
  repeat <dev> <btn> <n>    - Send command n times (e.g. vol_up 5)
  list                      - View all learned devices & buttons
  delete <device> [button]  - Remove a button or entire device
  keypad                    - Start 4x4 Keypad Remote (16 keys)
  help                      - Show this command list
============================================================

IR-Remote>
```

#### Example 1: Learning TV Commands
```text
IR-Remote> learn tv power
[*] Point remote at receiver (GPIO 15) and press the button...
[+] Successfully captured 67 pulse edges!
    Leading mark: 9024 us, Leading space: 4492 us
[Storage] Database successfully saved to 'ir_codes.json'.
[+] Stored under Device: 'tv', Button: 'power'

IR-Remote> learn tv vol_up
[*] Point remote at receiver (GPIO 15) and press the button...
[+] Successfully captured 67 pulse edges!
[Storage] Database successfully saved to 'ir_codes.json'.
[+] Stored under Device: 'tv', Button: 'vol_up'
```

#### Example 2: Learning AC or Soundbar Commands
```text
IR-Remote> learn ac power
[*] Point remote at receiver (GPIO 15) and press the button...
[+] Successfully captured 219 pulse edges!
[Storage] Database successfully saved to 'ir_codes.json'.
[+] Stored under Device: 'ac', Button: 'power'
```

#### Example 3: Transmitting / Replicating Commands
```text
IR-Remote> send tv power
[>] Sending 'tv.power' (67 pulses, 1x)...
[+] Sent successfully.

IR-Remote> repeat tv vol_up 5
[>] Sending 'tv.vol_up' (67 pulses, 5x)...
[+] Sent successfully.
```

#### Example 4: Listing Stored Commands
```text
IR-Remote> list

Stored Devices and Buttons:
  Device: [tv]
    - power           (67 transitions)
    - vol_up          (67 transitions)
    - vol_down        (67 transitions)
  Device: [ac]
    - power           (219 transitions)
```

---

### 2. Standalone Physical Remote Mode

To use the Pico as a standalone handheld remote without a computer:
1. Wire pushbuttons between GPIO 11, 12, 13, 14 and GND.
2. In `main.py`, the `HARDWARE_BUTTONS` dictionary maps pins:
   ```python
   HARDWARE_BUTTONS = {
       14: ("tv", "power"),
       13: ("tv", "vol_up"),
       12: ("tv", "vol_down"),
       11: ("ac", "power"),
   }
   ```
3. Type `hwbuttons` in the CLI, or set `main()` to directly call `handle_hw_buttons(ir)` when starting without serial.
4. Pressing any physical button instantly transmits the assigned IR command!

---

## Technical Details

- **Carrier Modulation**: 38 kHz is synthesized using the RP2040 hardware PWM generator (`machine.PWM`). Carrier bursts ("marks") use a 33% duty cycle, and carrier gaps ("spaces") set duty cycle to 0%.
- **Raw Duration Array**: Stored in `ir_codes.json` as arrays of alternating mark and space microsecond durations: `[mark_0, space_0, mark_1, space_1, ...]`.
- **Automatic Garbage Collection**: `gc.collect()` is triggered right before capturing and transmitting to eliminate timing jitter caused by Python garbage collection.