# Universal IR Remote for Raspberry Pi Pico (MicroPython)

A complete, protocol-agnostic Universal Infrared (IR) Remote Controller built for the **Raspberry Pi Pico (RP2040)** running MicroPython.

It can **learn** any IR remote signal from your existing remotes (TV, AC, Soundbar, Projector, Set-Top Box, Fan, etc.), **save** them permanently to flash memory as JSON, and **replicate/transmit** the exact 38 kHz modulated IR signal to control all your appliances from a single handheld unit.

Featuring an **8x8 tactile keypad matrix (64 buttons)**, an **addressable WS2812B RGB LED strip indicator/backlight**, and a **100% orthogonal dual-sided perfboard PCB layout** (`pcb_design_v2.html`).

---

## Key Features

- **True Universal Protocol Compatibility**: Learns raw microsecond mark/space transitions instead of hardcoded vendor protocols. Compatible with NEC, Sony SIRC, Philips RC-5/RC-6, Samsung, Panasonic, Sharp, and long Air Conditioner remotes with 200+ pulse frames.
- **64-Button Direct Keypad Matrix ($8 \times 8$)**: All 64 tactile buttons are driven directly by 16 Pico GPIOs using RP2040 internal pull-ups (zero external shift registers or I2C expanders needed).
- **Addressable RGB LED Strip (Indicator & Keypad Backlight)**:
  - **Ambient Appliance Mode Backlight**:
    - **TV**: Deep Sky Cyan (`RGB: 0, 140, 255`)
    - **AC**: Arctic Ice White (`RGB: 160, 255, 255`)
    - **SOUNDBAR**: Warm Sunset Amber (`RGB: 255, 120, 0`)
    - **PROJECTOR**: Neon Violet (`RGB: 180, 0, 255`)
  - **Dynamic State Feedback**:
    - **IR Transmit**: Instant bright Emerald Green pulse (`RGB: 0, 255, 70`)
    - **Learn Step 1 (Pick Key)**: Breathing Amber glow (`RGB: 255, 160, 0`)
    - **Learn Step 2 (Aim Remote)**: Vibrant Pink/Magenta pulse (`RGB: 255, 0, 120`)
    - **Learn Success**: Cascading Green chase sequence
    - **Timeout/Error**: Red strobe warning
- **Dedicated System Keys**:
  - **Button 2 (LEARN - Amber Cap)**: Fixed 2-step handheld learning mode (Select Target Button ➜ Aim Original Remote ➜ Auto-Save).
  - **Button 3 (MODE - Emerald Cap)**: Fixed instant device switcher (`TV` $\rightarrow$ `AC` $\rightarrow$ `SOUNDBAR` $\rightarrow$ `PROJECTOR`).
  - *Buttons 2 & 3 are hardware-locked and immutable; all other 62 buttons can be programmed freely.*
- **100% Orthogonal Dual-Sided Perfboard Layout**: Designed for standard 2.54mm perfboard ($22 \times 78$ grid). Zero diagonals, zero short circuits, with an insulated crossover jumper bridge at `F19`.
- **Hardware PWM 38 kHz Carrier**: Uses RP2040 hardware PWM for an accurate 38 kHz carrier frequency at a standard 33% duty cycle.
- **Persistent Flash Storage**: Learned codes are automatically saved to `ir_codes.json` in flash memory and persist across reboots.
- **Comprehensive Test Suite (`test_all.py`)**: Dedicated modular diagnostic suite for keypad matrix, RGB LED strip, IR transmitter camera blink, IR receiver listening, and optical loopback.

---

## Hardware Architecture & Pinout (V2 Finalized)

The remote is built on a $22 \times 78$ double-sided perfboard with a horizontal ($90^\circ$ rotated) Raspberry Pi Pico mounted at Rows 5–12 across Columns B–U.

### 1. Pin Assignment Summary

```
                      +-------------------+
                      |  IR TX  |  IR RX  |  RGB STRIP (Rows 1-5)
                      +-------------------+
                      |  PICO (HORIZONTAL)| (Rows 5-12)
                      +-------------------+
                      |   8x8 KEYPAD (64) | (Rows 14-78)
                      |  Buttons 1 to 64  |
                      +-------------------+
```

#### A. Keypad Matrix: Bottom Header Pins 1 to 20 (Row 12 on Perfboard)
All 16 GPIOs available on the Pico bottom header are 100% utilized for the $8 \times 8$ matrix:

| Function | Net Name | Pico GPIO | Physical Pin | Perfboard Pad | Notes |
|:---:|:---:|:---:|:---:|:---:|---|
| **Col 0 Rail** | Col C | `GP1` | Pin 2 | `C12` | Backside bus rail |
| **Col 1 Rail** | Col D | `GP2` | Pin 4 | `E12` $\rightarrow$ `D15` | Backside bus rail |
| **Col 2 Rail** | Col H | `GP5` | Pin 7 | `H12` | Backside bus rail |
| **Col 3 Rail** | Col I | `GP6` | Pin 9 | `J12` $\rightarrow$ `I15` | Backside bus rail |
| **Col 4 Rail** | Col N | `GP9` | Pin 12 | `M12` $\rightarrow$ `N16` | Backside bus rail |
| **Col 5 Rail** | Col O | `GP10` | Pin 14 | `O12` | Backside bus rail |
| **Col 6 Rail** | Col S | `GP13` | Pin 17 | `R12` $\rightarrow$ `S16` | Backside bus rail |
| **Col 7 Rail** | Col T | `GP14` | Pin 19 | `T12` | Backside bus rail |
| **Row 0 Bus** | Row 19 | `GP11` | Pin 15 | `P12` $\rightarrow$ `Q19` | Front wire (Set 1: Buttons 1–8) |
| **Row 1 Bus** | Row 27 | `GP4` | Pin 6 | `G12` $\rightarrow$ `F27` | Front wire + F19 Jumper (Set 2: Buttons 9–16) |
| **Row 2 Bus** | Row 35 | `GP3` | Pin 5 | `F12` $\rightarrow$ `F35` | Backside corridor wire (Set 3: Buttons 17–24) |
| **Row 3 Bus** | Row 43 | `GP12` | Pin 16 | `Q12` $\rightarrow$ `Q43` | Backside corridor wire (Set 4: Buttons 25–32) |
| **Row 4 Bus** | Row 51 | `GP8` | Pin 11 | `L12` $\rightarrow$ `L51` | Backside corridor wire (Set 5: Buttons 33–40) |
| **Row 5 Bus** | Row 59 | `GP7` | Pin 10 | `K12` $\rightarrow$ `K59` | Backside corridor wire (Set 6: Buttons 41–48) |
| **Row 6 Bus** | Row 67 | `GP0` | Pin 1 | `B12` $\rightarrow$ `A15` $\rightarrow$ `A67` $\rightarrow$ `E67` | Backside outer rail (`B12` $\rightarrow$ `A67`) $\rightarrow$ Front feed link (`A67` $\rightarrow$ `E67`) $\rightarrow$ Row 67 bus (Set 7: Buttons 49–56) |
| **Row 7 Bus** | Row 75 | `GP15` | Pin 20 | `U12` $\rightarrow$ `V15` $\rightarrow$ `V75` $\rightarrow$ `R75` | Backside outer rail (`U12` $\rightarrow$ `V75`) $\rightarrow$ Front feed link (`R75` $\rightarrow$ `V75`) $\rightarrow$ Row 75 bus (Set 8: Buttons 57–64) |

*Ground pins (Pins 3, 8, 13, 18 @ D12, I12, N12, S12) are tied to system ground.*

#### B. Optics, RGB Strip & Power: Top Header Pins 21 to 40 (Row 5 on Perfboard)

| Module | Signal | Pico GPIO | Physical Pin | Perfboard Pad | Notes |
|---|:---:|:---:|:---:|:---:|---|
| **WS2812B RGB Strip** | DIN | `GP16` | Pin 21 | `U5` $\rightarrow$ `U1` | Addressable RGB Data In |
| **WS2812B RGB Strip** | VCC | 3.3V / VSYS | Pin 36 | `T1` $\rightarrow$ `F5` | Power Rail (3.3V or VSYS) |
| **WS2812B RGB Strip** | GND | GND | Pin 23 | `S5` $\rightarrow$ `S1` | System Ground |
| **IR Transmitter** | SIG | `GP28` | Pin 34 | `H5` $\rightarrow$ `H1` | 38 kHz Hardware PWM |
| **IR Transmitter** | VCC | 3.3V | Pin 36 | `F5` $\rightarrow$ `I1` | 3V3 system power rail |
| **IR Transmitter** | GND | GND | Pin 38 | `D5` $\rightarrow$ `G1` | System ground |
| **IR Receiver** | DAT | `GP27` | Pin 32 | `J5` $\rightarrow$ `N1` | Demodulated Active-LOW IN |
| **IR Receiver** | VCC | 3.3V | Pin 36 | `F5` $\rightarrow$ `L1` | 3V3 system power rail |
| **IR Receiver** | GND | GND | Pin 28 | `N5` $\rightarrow$ `M1` | System ground |
| **Power Input** | VSYS | VBAT | Pin 39 | `C5` $\rightarrow$ `C1` | Battery (+) via Slide Switch (1.8V–5.5V) |
| **Power Input** | GND | GND | Pin 38 | `D5` $\rightarrow$ `D1` | Battery (-) Ground |

---

## 64-Button Matrix Layout & Numbering

The buttons are arranged into 8 dual-row button sets (Sets 1 to 8). Button numbers are strictly ordered **1, 2, 3, 4** across each upper row and **5, 6, 7, 8** across each lower row:

```text
===================================================================================
 SET 1 (Row Bus 19, GP11)
   Upper Row (Row 16):  [ 01: POWER ]  [ 02: LEARN ]  [ 03: MODE ]   [ 04: MUTE ]
   Lower Row (Row 20):  [ 05: UP    ]  [ 06: DOWN  ]  [ 07: LEFT ]   [ 08: RIGHT]
-----------------------------------------------------------------------------------
 SET 2 (Row Bus 27, GP4)
   Upper Row (Row 24):  [ 09: OK    ]  [ 10: VOL + ]  [ 11: VOL - ]  [ 12: CH + ]
   Lower Row (Row 28):  [ 13: CH -  ]  [ 14: BACK  ]  [ 15: HOME  ]  [ 16: MENU ]
-----------------------------------------------------------------------------------
 SET 3 (Row Bus 35, GP3)
   Upper Row (Row 32):  [ 17 ]         [ 18 ]         [ 19 ]         [ 20 ]
   Lower Row (Row 36):  [ 21 ]         [ 22 ]         [ 23 ]         [ 24 ]
-----------------------------------------------------------------------------------
 SET 4 (Row Bus 43, GP12)
   Upper Row (Row 40):  [ 25 ]         [ 26 ]         [ 27 ]         [ 28 ]
   Lower Row (Row 44):  [ 29 ]         [ 30 ]         [ 31 ]         [ 32 ]
-----------------------------------------------------------------------------------
 SET 5 (Row Bus 51, GP8)
   Upper Row (Row 48):  [ 33 ]         [ 34 ]         [ 35 ]         [ 36 ]
   Lower Row (Row 52):  [ 37 ]         [ 38 ]         [ 39 ]         [ 40 ]
-----------------------------------------------------------------------------------
 SET 6 (Row Bus 59, GP7)
   Upper Row (Row 56):  [ 41 ]         [ 42 ]         [ 43 ]         [ 44 ]
   Lower Row (Row 60):  [ 45 ]         [ 46 ]         [ 47 ]         [ 48 ]
-----------------------------------------------------------------------------------
 SET 7 (Row Bus 67, GP0)
   Upper Row (Row 64):  [ 49 ]         [ 50 ]         [ 51 ]         [ 52 ]
   Lower Row (Row 68):  [ 53 ]         [ 54 ]         [ 55 ]         [ 56 ]
-----------------------------------------------------------------------------------
 SET 8 (Row Bus 75, GP15)
   Upper Row (Row 72):  [ 57 ]         [ 58 ]         [ 59 ]         [ 60 ]
   Lower Row (Row 76):  [ 61 ]         [ 62 ]         [ 63 ]         [ 64 ]
===================================================================================
```

### Fixed vs. Learnable Buttons
- **Button 2 (LEARN)**: **FIXED & IMMUTABLE SYSTEM BUTTON**
  - Triggers the 2-step handheld learning routine.
  - Locked in hardware logic — cannot be selected as a learning destination and cannot be overwritten.
- **Button 3 (MODE)**: **FIXED & IMMUTABLE SYSTEM BUTTON**
  - Instantly cycles target appliance profiles: `TV` $\rightarrow$ `AC` $\rightarrow$ `SOUNDBAR` $\rightarrow$ `PROJECTOR`.
  - Locked in hardware logic — cannot be selected as a learning destination and cannot be overwritten.
- **Buttons 1, and 4 through 64 (62 Learnable Buttons)**:
  - **Every single one of these 62 buttons can be used to learn and transmit IR signals!**
  - To program any button: Press **Button 2 (LEARN)**, press your desired target button (e.g. Button 1, 4, 15, or 64), aim your household remote at the receiver sensor (`GP27`), and press the remote button. The code is permanently saved in flash memory.

---

## Bill of Materials (BOM)

| # | Component | Specification / Model | Qty | Designator | Unit Price | Total Price | Purchase Link | Sourcing / Circuit Role |
|:---:|---|---|:---:|:---:|:---:|:---:|:---:|---|
| **1** | **Microcontroller Board** | Raspberry Pi Pico (RP2040, 2MB Flash, Dual-Core 133MHz) | 1 | `U1` | ₹500 | ₹500 | [robu.in](https://robu.in/product/raspberry-pi-pico/) | Main controller: captures raw IR pulses, scans 8x8 matrix, drives 38kHz PWM |
| **2** | **Tactile Pushbuttons** | 6x6x5mm 4-pin through-hole momentary tactile switches | 64 | `SW1–SW64` | ~₹0.78 | ₹50 | *[Pending]* | Full 64-button matrix (Buttons 1 to 64) |
| **3** | **Addressable RGB LED Strip** | WS2812B / NeoPixel 5050 RGB LED strip (8 LEDs) | 1 | `RGB1` | ₹25 | ₹25 | *[Pending]* | Status indicator (TV, AC, Soundbar, Projector) and keypad backlight |
| **4** | **IR Transmitter Module** | 940nm High-Power 3-Pin IR LED Module (with onboard driver transistor) | 1 | `TX1` | ₹50 | ₹50 | *[Pending]* | High-intensity 38kHz PWM transmitter for 10–15m range |
| **5** | **IR Receiver Sensor** | VS1838B (or TSOP38238) 38kHz Demodulating IR Receiver | 1 | `RX1` | ₹30 | ₹30 | *[Pending]* | Demodulates incoming raw 38kHz codes from original remotes for learning |
| **6** | **Double-Sided FR4 Perfboard** | 2.54mm (0.1") pitch protoboard (10x20 cm or 10x22 cm, ≥ 22x78 holes) | 1 | `PCB` | ₹260 | ₹260 | *[Pending]* | Main dual-sided chassis board holding Pico, matrix, optics, and RGB strip |
| **7** | **Insulated Jumper Wire** | 30 AWG Kynar / PTFE wire wrap spool (Red & Green) | 1 | `W_JUMP` | ₹50 | ₹50 | *[Pending]* | Red for Matrix Rows, Green for Matrix Columns, insulated crossover at F19 |
| | **TOTAL ESTIMATED COST** | | | | | **₹965.00** | | *(Complete BOM for all core electronic components)* |

---

## Interactive PCB Visualizer (`pcb_design_v2.html`)

Open [`pcb_design_v2.html`](pcb_design_v2.html) directly in any modern browser:

- **Full $22 \times 78$ Grid Visualization**: View component placement, solder joints, traces, and pinout legends.
- **Top / Bottom / X-Ray Perspectives**:
  - **Top View (Component Side)**: Displays tactile buttons, RGB LED strip header, IR optics, Pico headers, and front trace routing.
  - **Bottom View (Solder Side)**: Mirrored view showing all 8 column bus rails, 64 tap-to-rail solder joints, and backside corridor routing.
  - **X-Ray View**: Translucent composite view of both sides simultaneously.
- **High-Contrast Dual Color-Coding**:
  - **GREEN (`#22c55e`)** = **All Column Connections** (8 backside column rails, Pico GPIO column leads, and 64 button taps).
  - **RED (`#ef4444`)** = **All Row Connections** (8 row buses, front jumper wires, and Pico GPIO row leads).
- **F19 Crossover Jumper Bridge**: Clear rendering of the insulated jumper at F19 hopping over the Row 19 bus.
- **Interactive Inspection**: Hover or click any pad, button, or solder joint to see live pin assignments, GPIO nets, and soldering instructions.

---

## File Structure

```text
universal-IR-remote/
├── pcb_design_v2.html     # Interactive 22x78 dual-sided perfboard visualizer & solder guide
├── universal_ir.py        # Core IR engine: microsecond pulse capture, 38kHz PWM, flash storage
├── keypad.py              # Direct 8x8 matrix keypad driver (64 buttons, 16 GPIOs)
├── rgb_strip.py           # Addressable WS2812B NeoPixel RGB LED strip controller
├── main.py                # Main remote application, handheld keypad loop & serial CLI
├── test_all.py            # Comprehensive hardware diagnostics & interactive test suite
├── .gitignore             # Standard git ignore rules
└── README.md              # Project documentation and assembly guide
```

---

## Installation & Setup

1. **Flash MicroPython on Pico**:
   - Download the latest MicroPython UF2 from [micropython.org/download/rp2-pico](https://micropython.org/download/rp2-pico/).
   - Hold `BOOTSEL`, plug Pico into USB, and copy the `.uf2` file onto the `RPI-RP2` drive.

2. **Upload Project Code**:
   - Open **Thonny IDE** and select `MicroPython (Raspberry Pi Pico)`.
   - Copy the following files to the Pico's root flash storage (`/`):
     - `universal_ir.py`
     - `keypad.py`
     - `rgb_strip.py`
     - `main.py`
     - `test_all.py`

3. **Run Hardware Diagnostics**:
   - Run `test_all.py` to verify each hardware subsystem:
     - `1`: 8x8 Keypad Matrix (press buttons 1–64 to verify scan).
     - `2`: IR LED Transmitter (verify purple glow via smartphone camera).
     - `3`: IR Receiver (aim any remote to verify reception).
     - `4`: Optical Loopback Self-Test (GP28 TX blasts $\rightarrow$ GP27 RX verifies).
     - `6`: WS2812B RGB Addressable LED Strip (rainbow, mode colors, pulse test).

4. **Launch Main Remote**:
   - Run `main.py`. The RGB strip will cycle a smooth rainbow on boot, then light up with the active appliance mode color (e.g. Cyan for TV).
   - Press **Button 3 (MODE)** to switch appliance profiles and see the RGB color shift!
   - Press **Button 2 (LEARN)** to program any of the 62 buttons!
