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
| **3** | **IR Receiver Demodulator** | **VS1838B** (or TSOP38238 / TSOP4838), 38 kHz optical bandpass filter | 1 | `U2` | ₹25 / $0.40 | **₹25 / $0.40** | Demodulates incoming 38kHz optical signal into clean active-LOW pulse trains |
| **4** | **Infrared Emitter LED** | 940nm High-Power IR LED (5mm, water-clear or dark purple package) | 1 | `D1` | ₹10 / $0.15 | **₹10 / $0.15** | Transmits 38kHz pulsed infrared light with 5–8 meter line-of-sight range |
| **5** | **NPN Switching Transistor** | **2N2222** (or 2N3904 / BC547 / SS8050), TO-92 package, $I_C \ge 200\text{mA}$ | 1 | `Q1` | ₹6 / $0.10 | **₹6 / $0.10** | Low-side driver switch; amplifies GP16 PWM output to pulse IR LED to ground |
| **6** | **Base Current Limiter** | **1 kΩ Resistor**, 1/4W, 5% (Color: Brown - Black - Red - Gold) | 1 | `R1` | ₹2 / $0.03 | **₹2 / $0.03** | Limits transistor base current to ~2.6mA to protect RP2040 GPIO pin while saturating Q1 |
| **7** | **LED Current Limiter** | **100 Ω Resistor**, 1/4W or 1/2W, 5% (Color: Brown - Black - Brown - Gold) | 1 | `R2` | ₹2 / $0.03 | **₹2 / $0.03** | Limits IR LED peak pulse current to ~35mA from 4.5V battery rail |
| **8** | **Battery Holder** | 3x AAA Battery Holder with 150mm lead wires (Red/Black) | 1 | `BT1` | ₹40 / $0.55 | **₹40 / $0.55** | Enclosed or open 3x AAA series compartment supplying 4.5V DC to VSYS |
| **9** | **Batteries** | 1.5V AAA Alkaline cells (or 1.2V AAA NiMH rechargeable cells) | 3 | `BAT1-3` | ₹25 / $0.35 | **₹75 / $1.05** | Portable handheld power; Pico operates reliably from 4.5V down to 2.0V |
| **10** | **Main Power Switch** | SPST Miniature Slide Switch (Panel or PCB Mount, 2-pin / 3-pin) | 1 | `SW_PWR` | ₹10 / $0.15 | **₹10 / $0.15** | Disconnects battery from Pico VSYS (Pin 39) for zero standby battery drain |
| **11** | **Breadboard / Perfboard** | Half-size solderless breadboard (400 tie-points) or 5x7cm protoboard | 1 | `PCB` | ₹75 / $1.00 | **₹75 / $1.00** | Prototyping chassis or solderable perfboard for final handheld build |
| **12** | **DuPont Jumper Wires** | Male-to-Female & Male-to-Male 10cm / 20cm flexible jumper wires | ~15 | `W1-W15` | ₹35 / $0.50 | **₹35 / $0.50** | Interconnect wiring between Pico, keypad, optics, and battery holder |
| | **TOTAL ESTIMATED COST** | | | | | **₹750 / ~$9.35** | *(Full kit cost with batteries and prototyping breadboard)* |

> [!TIP]
> **Cost Breakdown & Sourcing Tips:**
> - **Core Electronics Only** (Pico + Keypad + IR Optics + Transistor + Passives): **~₹515 / $6.50**
> - **Full Handheld Kit** (including 3x AAA batteries, battery holder, switch, breadboard, and wires): **~₹750 / $9.35**
> - **Where to Buy**: Readily available at maker stores like Robu.in, Silverline Electronics, Amazon, AliExpress, and local electronics hobby component shops.

---

### 2. Wiring Diagram

```
                 Raspberry Pi Pico (RP2040)
               +---------------------------+
               |                           |
    3.3V (OUT) | [Pin 36]                  |
               |                           |
       GPIO 15 | [Pin 20] <-------+        |
               |                  |        |
       GPIO 16 | [Pin 21] ----+   |        |
               |              |   |        |
           GND | [Pin 18]     |   |        |
               +--------------|---|--------+
                              |   |
      +-----------------------+   |
      |                           |
      v                           v
  [IR Transmitter Circuit]     [IR Receiver: VS1838B]
                              +--------------------+
   GPIO 16                    | Pin 1 (OUT) ------> GPIO 15
      |                       | Pin 2 (GND) ------> Pico GND
    [1kΩ]                     | Pin 3 (VCC) ------> Pico 3.3V
      |                       +--------------------+
      +---> Base (2N2222)
            Collector ---> [100Ω] ---> [IR LED Anode (+)]
                                       [IR LED Cathode (-)] ---> 3.3V or VBUS (5V)*
            Emitter   ---> GND

  * Note: Powering the IR LED through the 100Ω resistor from VBUS (Pin 40, 5V) gives
    longer transmission range (up to 5-10 meters).
```

#### Receiver (VS1838B / TSOP38238)
- **OUT (Signal)** $\rightarrow$ **GPIO 15** (Pin 20)
- **GND** $\rightarrow$ **GND** (Pin 18 or 38)
- **VCC** $\rightarrow$ **3.3V (OUT)** (Pin 36)

#### Transmitter (Driver with NPN Transistor)
- **GPIO 16** $\rightarrow$ **1 kΩ Resistor** $\rightarrow$ **Transistor Base**
- **Transistor Emitter** $\rightarrow$ **Pico GND**
- **Transistor Collector** $\rightarrow$ **IR LED Cathode (short leg / flat edge)**
- **IR LED Anode (long leg)** $\rightarrow$ **100 Ω Resistor** $\rightarrow$ **Battery (+) 4.5V / VSYS (Pin 39)**

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

#### 4x4 Matrix Keypad (16 Buttons - 8 GPIOs)
Standard 4x4 readymade membrane or tactile keypad. Uses 8 GPIOs directly without any extra I2C ICs:
- **Rows (Outputs, Scanned LOW)**:
  - **Row 0** $\rightarrow$ **GPIO 6** (Pin 9)
  - **Row 1** $\rightarrow$ **GPIO 7** (Pin 10)
  - **Row 2** $\rightarrow$ **GPIO 8** (Pin 11)
  - **Row 3** $\rightarrow$ **GPIO 9** (Pin 12)
- **Columns (Inputs with Internal Pull-Ups)**:
  - **Col 0** $\rightarrow$ **GPIO 10** (Pin 14)
  - **Col 1** $\rightarrow$ **GPIO 11** (Pin 15)
  - **Col 2** $\rightarrow$ **GPIO 12** (Pin 16)
  - **Col 3** $\rightarrow$ **GPIO 13** (Pin 17)

##### 4x4 Keypad Remote Layout:
```text
  [ 1 ]    [ 2 ]    [ 3 ]    [ A: MODE (Switch Device) ] <- Row 0 (GP6)
  [ 4 ]    [ 5 ]    [ 6 ]    [ B: VOL ▲                ] <- Row 1 (GP7)
  [ 7 ]    [ 8 ]    [ 9 ]    [ C: VOL ▼                ] <- Row 2 (GP8)
  [ * ]    [ 0 ]    [ # ]    [ D: POWER                ] <- Row 3 (GP9)
    ^        ^        ^        ^
  Col 0    Col 1    Col 2    Col 3
  (GP10)   (GP11)   (GP12)   (GP13)
```

##### Key Action Map:
| Key | Remote Action | Description |
|---|---|---|
| **A** | **MODE** | Cycles target appliance: `TV` $\rightarrow$ `AC` $\rightarrow$ `SOUNDBAR` $\rightarrow$ `PROJECTOR` |
| **D** | **power** | Power On / Off |
| **B** | **vol_up** | Volume Up |
| **C** | **vol_down** | Volume Down |
| **\*** | **mute** | Mute Audio |
| **#** | **enter** | Confirm / OK |
| **0 – 9** | **0 – 9** | Channel and number selection |

---

## File Structure

```text
universal-IR-remote/
├── universal_ir.py        # Core engine: raw timing capture, 38kHz PWM, flash JSON storage
├── keypad.py              # Direct 4x4 matrix keypad scanner (16 keys, 8 GPIOs)
├── main.py                # Interactive CLI menu, 4x4 keypad remote loop, device switcher
├── circuit_visualizer.html# Interactive browser visualizer with clickable 4x4 keypad
└── README.md              # Documentation and wiring guide
```

---

## Interactive Circuit Visualizer

Open [`circuit_visualizer.html`](circuit_visualizer.html) in your browser:
- **Clickable 4x4 Keypad**: Test any of the 16 buttons interactively. Press `A` to change devices!
- **Signal Trace**: Live simulated oscillograms of demodulated 38 kHz pulse trains.
- **Net Filtering**: Highlight Rows, Columns, Power, Ground, RX, and TX lines individually.

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
  keypad                    - Start 4x5 Keypad Matrix (20 keys)
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