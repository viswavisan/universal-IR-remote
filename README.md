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
- **100% Orthogonal Dual-Sided Perfboard Layout**: Designed for standard 2.54mm perfboard ($22 \times 67$ grid). Zero diagonals, zero short circuits, with an insulated crossover jumper bridge at `F20`.
- **Hardware PWM 38 kHz Carrier**: Uses RP2040 hardware PWM for an accurate 38 kHz carrier frequency at a standard 33% duty cycle.
- **Persistent Flash Storage**: Learned codes are automatically saved to `ir_codes.json` in flash memory and persist across reboots.
- **Comprehensive Test Suite (`test_all.py`)**: Dedicated modular diagnostic suite for keypad matrix, RGB LED strip, IR transmitter camera blink, IR receiver listening, and optical loopback.

---

## Hardware Architecture & Pinout (V2 Finalized)

The remote is built on a $22 \times 65$ double-sided perfboard with a horizontal ($90^\circ$ rotated) Raspberry Pi Pico mounted at Rows 5–12 across Columns B–U.

### 1. Pin Assignment Summary

```
                      +-------------------+
                      |  IR TX  |  IR RX  |  RGB STRIP (Rows 1-5)
                      +-------------------+
                      |  PICO (HORIZONTAL)| (Rows 5-12)
                      +-------------------+
                      |   8x8 KEYPAD (64) | (Rows 16-63)
                      |  Buttons 1 to 64  |
                      +-------------------+
```

#### A. Keypad Matrix: Bottom Header Pins 1 to 20 (Row 14 on Perfboard)
All 16 GPIOs available on the Pico bottom header are 100% utilized for the $8 \times 8$ matrix:

| Function | Net Name | Pico GPIO | Physical Pin | Perfboard Pad | Notes |
|:---:|:---:|:---:|:---:|:---:|---|
| **Col 0 Rail** | Col B | `GP1` | Pin 2 | `C14` $\rightarrow$ `C18` $\rightarrow$ `B18` | Backside bus rail (`B18` $\rightarrow$ `B65`) |
| **Col 1 Rail** | Col D | `GP2` | Pin 4 | `E14` $\rightarrow$ `D17` | Backside bus rail (`D17` $\rightarrow$ `D65`) |
| **Col 2 Rail** | Col G | `GP5` | Pin 7 | `H14` $\rightarrow$ `H18` $\rightarrow$ `G18` | Backside bus rail (`G18` $\rightarrow$ `G65`) |
| **Col 3 Rail** | Col I | `GP6` | Pin 9 | `J14` $\rightarrow$ `I17` | Backside bus rail (`I17` $\rightarrow$ `I65`) |
| **Col 4 Rail** | Col N | `GP9` | Pin 12 | `M14` $\rightarrow$ `N17` | Backside bus rail (`N17` $\rightarrow$ `N65`) |
| **Col 5 Rail** | Col P | `GP10` | Pin 14 | `O14` $\rightarrow$ `O18` $\rightarrow$ `P18` | Backside bus rail (`P18` $\rightarrow$ `P65`) |
| **Col 6 Rail** | Col S | `GP13` | Pin 17 | `R14` $\rightarrow$ `S17` | Backside bus rail (`S17` $\rightarrow$ `S65`) |
| **Col 7 Rail** | Col U | `GP14` | Pin 19 | `T14` $\rightarrow$ `U17` | Backside bus rail (`U17` $\rightarrow$ `U65`) |
| **Row 0 Bus** | Row 20 | `GP12` | Pin 16 | `Q14` $\rightarrow$ `Q20` | Top-side rail (`Q14` $\rightarrow$ `Q20`) [Front wire - Red] (Set 1: Buttons 1–8) |
| **Row 1 Bus** | Row 26 | `GP4` | Pin 6 | `G14` $\rightarrow$ `F26` | Front wire + F20 Jumper (Set 2: Buttons 9–16) |
| **Row 2 Bus** | Row 32 | `GP0` | Pin 1 | `B14` $\rightarrow$ `B32` $\rightarrow$ `C32` | Top-side rail (`B14` $\rightarrow$ `B32` $\rightarrow$ `C32`) [Front wire - Red] (Set 3: Buttons 17–24) |
| **Row 3 Bus** | Row 38 | `GP15` | Pin 20 | `U14` $\rightarrow$ `U38` $\rightarrow$ `T38` | Top-side rail (`U14` $\rightarrow$ `U38` $\rightarrow$ `T38`) [Front wire - Red] (Set 4: Buttons 25–32) |
| **Row 4 Bus** | Row 44 | `GP8` | Pin 11 | `L14` $\rightarrow$ `L44` | Backside corridor wire (`L14` $\rightarrow$ `L44`) [Backside - Red] (Set 5: Buttons 33–40) |
| **Row 5 Bus** | Row 50 | `GP7` | Pin 10 | `K14` $\rightarrow$ `K50` | Backside corridor wire (`K14` $\rightarrow$ `K50`) [Backside - Red] (Set 6: Buttons 41–48) |
| **Row 6 Bus** | Row 56 | `GP3` | Pin 5 | `F14` $\rightarrow$ `F56` | Backside corridor wire (`F14` $\rightarrow$ `F56`) [Backside - Red] (Set 7: Buttons 49–56) |
| **Row 7 Bus** | Row 62 | `GP11` | Pin 15 | `P14` $\rightarrow$ `P17` $\rightarrow$ `Q17` $\rightarrow$ `Q62` | Backside corridor wire (`P14` $\rightarrow$ `P17` $\rightarrow$ `Q17` $\rightarrow$ `Q62`) [Backside - Red] (Set 8: Buttons 57–64) |

*Ground pins (Pins 3, 8, 13, 18 @ D14, I14, N14, S14) are tied to system ground.*

#### B. Optics, RGB Strip, Motherboard SMD Resistors & Power: Top Header Pins 21 to 40 (Row 7 on Perfboard)

##### 1. Motherboard 1206 SMD Chip Resistors & IR LEDs (Rows 1–3 above Pico)
To save space and utilize in-hand surface-mount inventory without consuming 4-hole through-hole axial resistor spans:
- **Resistor R2 (22 Ω 1/4W 1206 SMD)**: Bridges adjacent perfboard pads **B1** and **C1**.
- **Resistor R3 (22 Ω 1/4W 1206 SMD)**: Bridges adjacent perfboard pads **F2** and **G2**.
- **Resistor R1 (220 Ω 1/4W 1206 SMD)**: Bridges adjacent perfboard pads **N2** and **O2** (base current limiter for Q1, biases 2N2222 into deep saturation for 15m+ range).
- **Common Power Bus (A1 ➔ A2 & A1 ➔ B1, A2 ➔ F2)**: The vertical power rail runs down Column A (**A1 ➔ A2**, fed from switched battery power via `B5 ➔ A5 ➔ A2`). From pad **A1**, a horizontal trace feeds R2 input at **B1** (`A1 ➔ B1`). From pad **A2**, a horizontal trace feeds R3 input at **B2** (`A2 ➔ F2`), completely freeing Column B.
- **Trace A2 ➔ A5 ➔ B5 (Switched VSYS Power Feed)**: Connects pad **A2** vertically down Column A to **A5**, then turns east along Row 5 to pad **B5**, tapping directly into the master switched 3.7V battery/VSYS rail.
- **Trace C1 ➔ D1 (LED1 Anode Feed)**: Connects the current-limited output of $R_2$ directly from pad **C1** into pad **D1** (Row 1 horizontal trace).
- **Trace G2 ➔ H2 (LED2 Anode Feed)**: Direct 1-pitch horizontal trace connecting the output of $R_3$ from pad **G2** into LED2 Anode at pad **H2**.
- **Trace E1 ➔ I1 (LED1 Cathode Feed)**: Runs horizontally east along Row 1 from pad **E1** directly to pad **I1**.
- **Trace I1 ➔ I2 (LED2 Cathode Feed)**: Vertical connection down Column I between **I1** and **I2**, bringing LED2 Cathode up to Row 1 (pad `I3` line removed).
- **Trace I1 ➔ K1 (Cathode Bus to Q1 Collector)**: Straight horizontal line along Row 1 from pad **I1** directly into Q1 Collector at pad **K1**.
- **Trace GP18 (R7) ➔ R3 ➔ Q2 ➔ O2 (IR TX PWM Drive Line & Crossover)**: Runs straight vertically north up Column R from Pico Pin 24 (**GP18** @ pad **R7**) directly to pad **R3**. From **R3**, it crosses diagonally underneath the crossover jumper into pad **Q2**, then turns west along Row 2 to pad **O2** directly into base resistor $R_1$.
- **Trace N2 ➔ L2 ➔ L1 (Q1 Base Drive Line)**: Orthogonal trace along Row 2 and Column L connecting $R_1$ output at pad **N2** through **L2** directly north into Q1 Base at pad **L1**.
- **Trace M1 ➔ V1 (Q1 Emitter & Row 1 Ground Rail)**: Pad **M1** (Q1 Emitter) sits directly on Row 1, connecting horizontally east along Row 1 across to pad **V1**, directly anchoring Q1 Emitter to the master Row 1 ground bus and battery ground input.
- **Trace C2 ➔ C7 (Pico VSYS Power Line)**: Straight vertical drop down Column C from pad **C2** directly into Pico Pin 39 (**VSYS** @ pad **C7**).
- **Trace 3V3 (F7) ➔ F3 ➔ Q3 ➔ [Jumper] ➔ R2 (IR RX 3.3V Power Rail & Crossover Jumper)**: Runs vertically north up Column F from Pico Pin 36 (**3V3** @ pad **F7**) to **F3**, then turns east along Row 3 directly into pad **Q3** (Receiver VCC land pad). From pad **Q3**, an insulated crossover jumper wire hops over the `R3 ➔ Q2` track directly into pad **R2** (RX1 Pin 3 VCC).
- **Trace T2 ➔ T7 (IR RX Demodulated Signal Line to GP17)**: Straight 1:1 vertical drop down Column T from pad **T2** (RX1 Pin 1 OUT) directly into Pico Pin 22 (**GP17** @ pad **T7**). Zero bends, zero jumpers!
- **Trace S1 ➔ S2 ➔ S7 (IR RX & System Ground Line)**: Straight 1:1 vertical line down Column S connecting Row 1 Ground bus pad **S1** through pad **S2** (RX1 Pin 2 GND) directly into Pico Pin 23 (**GND** @ pad **S7**). Tying into pad **S1**, this cleanly grounds the entire Row 1 ground bus (`M1 ➔ V1`) and transistor Q1 Emitter at pad **M1**.
- **Transistor Q1 (2N2222 TO-92 NPN Low-Side Driver @ K1, L1, M1 - Horizontal Orientation)**:
  - **Collector (C)**: Solder pad **K1** (Row 1: connected directly to IR LED cathode bus via `I1 ➔ K1`).
  - **Base (B)**: Solder pad **L1** (Row 1: driven from base resistor $R_1$ via `N2 ➔ L2 ➔ L1`).
  - **Emitter (E)**: Solder pad **M1** (Row 1: connected directly to Row 1 Ground rail `M1 ➔ V1`, grounded via `S1 ➔ S2 ➔ S7` into Pico Pin 23 GND).
  - **Package**: Standard TO-92 molded epoxy oriented horizontally along Row 1 with pinout `[K1=C, L1=B, M1=E]`.
- **IR LED 1 (940nm High-Power Emitter @ D1–E1)**:
  - **Anode (+)**: Soldered at pad **D1** (fed from $R_2$ via trace C1–D1).
  - **Cathode (-)**: Soldered at pad **E1**.
  - **Orientation**: High-intensity 5mm purple optical dome facing North with wide optical emission cone.
- **IR LED 2 (940nm High-Power Emitter @ H2–I2 with Extended Leads)**:
  - **Anode (+)**: Soldered at pad **H2** (Row 2).
  - **Cathode (-)**: Soldered at pad **I2** (Row 2).
  - **Vertical Level Alignment**: The terminal leads of LED2 are extended in height by 1 grid pitch (2.54mm) from the Row 2 solder pads up to the Row 1 level. Both LED1 and LED2 optical bodies, collar flanges, resin domes, and radiation cones are aligned along the exact same horizontal horizon facing North.
- **IR Receiver Sensor RX1 (VS1838B / TSOP38238 38kHz Demodulator @ R2, S2, T2 - North-Facing Orientation)**:
  - **Pin 1 (OUT)**: Solder pad **T2** (demodulated signal output routed via straight 1:1 vertical line `T2 ➔ T7` to RP2040 Pin 22 [**GP17** @ pad **T7**]).
  - **Pin 2 (GND)**: Solder pad **S2** (system ground tied straight down Column S via `S1 ➔ S2 ➔ S7` to Pico Pin 23 [**GND** @ pad **S7**] and Row 1 Ground bus).
  - **Pin 3 (VCC)**: Solder pad **R2** (clean 3.3V power supply fed from Pico Pin 36 [**3V3** @ pad **F7**] via `F7 ➔ F5 ➔ R5 ➔ R2`).
  - **North-Facing Orientation**: Viewing the board from the rear (dome facing North), Pin 3 (VCC) is at Column R (left), Pin 2 (GND) is at Column S (center), and Pin 1 (OUT) is at Column T (right).
  - **Optical Horizon Alignment**: The metallic leads extend from Row 2 solder pads so that the optical daylight-filtered lens dome sits at the North horizon, aligned with LED1 and LED2.
- **Physical Mounting**: Standard 1206 SMD package ($3.2\text{mm} \times 1.6\text{mm}$) solders directly across standard $2.54\text{mm}$ (0.1") pitch annular copper pads with zero lead bend overhead.

##### 2. Motherboard Power Links
| Module / Signal | Signal Name | Pico GPIO | Physical Pin | Perfboard Pad | Notes |
|---|:---:|:---:|:---:|:---:|---|
| **TP4056 OUT+** | VSYS | VBAT | Pin 39 | `B5` $\rightarrow$ `C5 ➔ C7` | Protected 3.7V from TP4056 via Slide Switch into `B5`, routing to Pico Pin 39 (VSYS @ `C7`) |
| **TP4056 OUT-** | GND | GND | Pin 23 | Flying Lead to `V1` | Protected System Ground flying lead to pad `V1`, directly feeding Row 1 Ground Rail (`K1 ➔ V1`), Q1 Emitter (`K1`), RX1 GND (`S2`), and Pico Pin 23 (GND @ `S7`). Pin 38 (`D7`) connection removed. |
| **IR TX PWM** | IR_TX | `GP18` | Pin 24 | `R7 ➔ R3 ➔ Q2 ➔ O2` | Pico Pin 24 hardware 38kHz PWM drive straight up Column R into R1 base resistor at O2 |
| **IR RX Data** | IR_RX | `GP17` | Pin 26 | `R2 ➔ R6 ➔ P6 ➔ P7` | Demodulated 38kHz signal from RX1 Pin 1 OUT via R3 jumper bridge & Row 6 jog to Pico Pin 26 (GP17) |
| **IR RX Power**| VCC_3V3| `3V3` | Pin 36 | `F7 ➔ F5 ➔ R5 ➔ R2` | Clean 3.3V power into RX1 Pin 3 VCC at R2 |
| **Optics Ground 1** | GND | GND | Row 1 | `M2 ➔ M1 ➔ V1` | Upper ground rail anchoring Q1 Emitter across Row 1 |
| **Battery ADC Monitor**| VSYS/3 | `GP29` (ADC3)| Internal | Internal Divider | RP2040 internal 3:1 divider monitors 14500 (AA size) cell voltage & battery health |

---

### 2. Rechargeable Power Architecture (3.7V 14500 AA-Size Li-ion + TP4056 Type-C)

The remote features a self-contained, rechargeable Lithium-Ion power supply utilizing a compact 14500 (AA form factor) 3.7V cell aligned horizontally across the 22-column (53.3mm) width of the remote:

```text
    +-------------------------------------------------------------+
    |  14500 Li-ion Cell (3.7V Nominal, 4.2V Peak, AA Size 50.5mm)|
    |  Aligned Horizontally Across 22-Column Width (Cols A to V)  |
    +------------------------------+------------------------------+
                                   | B+ / B-
                                   v
    +-------------------------------------------------------------+
    |  TP4056 USB-C Charger & DW01A/8205A Protection Board        |
    |  - Type-C 5V Input (Bottom-accessible charging port)        |
    |  - Dual Status LEDs: RED (Charging), BLUE (Full / Standby)  |
    |  - Over-charge Cutoff: 4.2V ± 1%                            |
    |  - Over-discharge Cutoff: 2.5V (protects 14500 from damage) |
    |  - Over-current Protection: 3.0A                            |
    +---------------+-----------------------------+---------------+
                    | OUT+                        | OUT-
                    v                             v
           [ SPST Slide Switch ]                  |
                    |                             |
                    v                             v
        Perfboard Pad A1 (+VSYS IN)      Perfboard Pad V1 (GND Rail)
```

#### Why 3.7V 14500 (AA Size) Aligned Horizontally with Board Width?
1. **Exact Mechanical Fit**: The 22-column 2.54mm perfboard width is $21 \times 2.54\,\text{mm} = 53.34\,\text{mm}$. A standard AA-sized cell is $50.5\,\text{mm}$ long ($\approx 54\,\text{mm}$ in a single AA horizontal leaf/spring holder). Oriented horizontally across the width, it spans from **Column A (x=120) to Column V (x=624)** with 1:1 symmetry, fitting inside the handheld remote handle!
2. **Li-ion Chemistry Requirement**: You must use a **3.7V 14500 rechargeable Lithium-ion cell** (widely sold in standard AA dimensions: $\varnothing 14.5\,\text{mm} \times 50.5\,\text{mm}$). **Do not use a standard 1.5V alkaline AA**, as 1.5V cannot power the Pico (requires $\ge 1.8\text{V}$) and will be destroyed by the TP4056 4.2V charger.
3. **Zero Dropout**: A single 14500 Li-ion cell discharges from 4.2V down to ~3.0V, remaining fully within the Pico's input window at all times while generating a rock-solid, regulated 3.3V for RP2040 and all sensors.
4. **Internal Hardware ADC Monitoring**: RP2040's internal ADC channel 3 (`GP29`) is hardwired internally to `VSYS / 3` via a 200k/100k resistor divider. You can measure battery voltage and state of charge in software without soldering an extra resistor or wire.
5. **Battery Life**: With 800–1200mAh capacity and an active scanning consumption of only ~18–22 mA, the remote operates for **over 40–60 hours of active use** and **months on standby**.

---

## 64-Button Matrix Layout & Numbering

The buttons are arranged into 8 dual-row button sets (Sets 1 to 8). Each 4.5mm tactile button occupies **3 columns $\times$ 2 rows (3×2 holes)** on the perfboard ($5.08\text{mm} \times 2.54\text{mm}$ pin pitch). Button numbers are strictly ordered **1, 2, 3, 4** across each upper row and **5, 6, 7, 8** across each lower row:

```text
===================================================================================
 SET 1 (Row Bus 18, GP12)
   Upper Row (Rows 16-17):  [ 01: POWER ]  [ 02: LEARN ]  [ 03: MODE ]   [ 04: MUTE ]
   Lower Row (Rows 19-20):  [ 05: UP    ]  [ 06: DOWN  ]  [ 07: LEFT ]   [ 08: RIGHT]
-----------------------------------------------------------------------------------
 SET 2 (Row Bus 24, GP4)
   Upper Row (Rows 22-23):  [ 09: OK    ]  [ 10: VOL + ]  [ 11: VOL - ]  [ 12: CH + ]
   Lower Row (Rows 25-26):  [ 13: CH -  ]  [ 14: BACK  ]  [ 15: HOME  ]  [ 16: MENU ]
-----------------------------------------------------------------------------------
 SET 3 (Row Bus 30, GP3)
   Upper Row (Rows 28-29):  [ 17 ]         [ 18 ]         [ 19 ]         [ 20 ]
   Lower Row (Rows 31-32):  [ 21 ]         [ 22 ]         [ 23 ]         [ 24 ]
-----------------------------------------------------------------------------------
 SET 4 (Row Bus 36, GP11 [Temporarily Disconnected])
   Upper Row (Rows 34-35):  [ 25 ]         [ 26 ]         [ 27 ]         [ 28 ]
   Lower Row (Rows 37-38):  [ 29 ]         [ 30 ]         [ 31 ]         [ 32 ]
-----------------------------------------------------------------------------------
 SET 5 (Row Bus 42, GP8)
   Upper Row (Rows 40-41):  [ 33 ]         [ 34 ]         [ 35 ]         [ 36 ]
   Lower Row (Rows 43-44):  [ 37 ]         [ 38 ]         [ 39 ]         [ 40 ]
-----------------------------------------------------------------------------------
 SET 6 (Row Bus 48, GP7)
   Upper Row (Rows 46-47):  [ 41 ]         [ 42 ]         [ 43 ]         [ 44 ]
   Lower Row (Rows 49-50):  [ 45 ]         [ 46 ]         [ 47 ]         [ 48 ]
-----------------------------------------------------------------------------------
 SET 7 (Row Bus 54, GP0)
   Upper Row (Rows 52-53):  [ 49 ]         [ 50 ]         [ 51 ]         [ 52 ]
   Lower Row (Rows 55-56):  [ 53 ]         [ 54 ]         [ 55 ]         [ 56 ]
-----------------------------------------------------------------------------------
 SET 8 (Row Bus 60, GP15)
   Upper Row (Rows 58-59):  [ 57 ]         [ 58 ]         [ 59 ]         [ 60 ]
   Lower Row (Rows 61-62):  [ 61 ]         [ 62 ]         [ 63 ]         [ 64 ]
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
  - To program any button: Press **Button 2 (LEARN)**, press your desired target button (e.g. Button 1, 4, 15, or 64), aim your household remote at the receiver sensor (`GP17`), and press the remote button. The code is permanently saved in flash memory.

---

## Bill of Materials (BOM)

| # | Component | Specification / Model | Qty | Designator | Unit Price | Total Price | Purchase Link | Sourcing / Circuit Role |
|:---:|---|---|:---:|:---:|:---:|:---:|:---:|---|
| **1** | **Microcontroller Board** | Raspberry Pi Pico (RP2040, 2MB Flash, Dual-Core 133MHz) | 1 | `U1` | ₹500 | ₹500 | [robu.in](https://robu.in/product/raspberry-pi-pico/) | Main controller: captures raw IR pulses, scans 8x8 matrix, drives 38kHz PWM |
| **2** | **Tactile Pushbuttons** | 4.5x4.5mm 4-pin through-hole tactile pushbuttons (5.08x2.54mm pitch: 3x2 holes) | 64 | `SW1–SW64` | ~₹0.78 | ₹50 | *[Pending]* | Full 64-button matrix (Buttons 1 to 64) |
| **3** | **Addressable RGB LED Strip** | WS2812B / NeoPixel 5050 RGB LED strip (8 LEDs) | 1 | `RGB1` | ₹25 | ₹25 | *[Pending]* | Status indicator (TV, AC, Soundbar, Projector) and keypad backlight |
| **4** | **High-Power IR LEDs (940nm)** | 5mm dark purple IR emitting diodes (Motherboard Row 1 & 2: D1 @ D1–E1, D2 @ H2–I2) | 2 | `LED1, LED2` | ₹10 | ₹20 | [robu.in](https://robu.in/product/5mm-940nm-ir-infrared-emitter-led/) | Dual high-power optical transmitters on motherboard facing North for wide 15m optical beam |
| **5** | **NPN Switching Transistor** | 2N2222 TO-92 NPN BJT (Motherboard Row 1: Collector @ K1, Base @ L1, Emitter @ M1) | 1 | `Q1` | ₹5 | ₹5 | [robu.in](https://robu.in/product/2n2222-npn-transistor-to-92/) | Low-side power switch: amplifies RP2040 GP18 hardware PWM pulses to ground |
| **6** | **Base Current Limiter** | 220 Ω 1/4W 1206 SMD chip resistor (Motherboard Row 2: N2–O2) | 1 | `R1` | ₹2 | ₹2 | [robu.in](https://robu.in/product/1206-smd-resistor-220-ohm/) | Biases Q1 base with saturation drive for 15m+ range; 1206 package bridges adjacent N2–O2 pads |
| **7** | **LED Current Limiters** | 22 Ω 1/4W 1206 SMD chip resistors (Motherboard: R2 @ B1–C1, R3 @ F2–G2) | 2 | `R2, R3` | ₹2 | ₹4 | *[In Stock]* | Limits peak pulse current to ~80-100mA per LED from 3.7V VSYS rail. 1206 footprint bridges adjacent 2.54mm annular pads. |
| **8** | **IR Receiver Sensor** | VS1838B (or TSOP38238) 38kHz Demodulating IR Receiver (Motherboard Row 2: VCC @ R2, GND @ S2, OUT @ T2) | 1 | `RX1` | ₹30 | ₹30 | [robu.in](https://robu.in/product/vs1838b-universal-infrared-receiving-sensor/) | Demodulates incoming raw 38kHz codes from original remotes for learning; mounted facing North |
| **10**| **Double-Sided FR4 Perfboard** | 2.54mm (0.1") pitch protoboard (≥ 22x67 holes) | 1 | `PCB` | ₹260 | ₹260 | *[Pending]* | Main motherboard holding Pico, 64-button matrix, optical circuitry, and RGB strip |
| **11**| **Insulated Jumper Wire** | 30 AWG Kynar / PTFE wire wrap spool (Red & Green) | 1 | `W_JUMP` | ₹50 | ₹50 | *[Pending]* | Red for Matrix Rows, Green for Matrix Columns, insulated crossover at F20 |
| **12**| **14500 3.7V Li-ion Battery (AA Size)** | 3.7V 800–1200mAh Cylindrical 14500 Li-ion Cell (Ø14.5mm × 50.5mm, AA Form Factor) + 1× AA Horizontal Holder | 1 | `BAT1` | ₹160 | ₹160 | [robu.in](https://robu.in/product/orange-icr14500-800mah-3-7v-lithium-ion-battery/) | Main 3.7V rechargeable power cell (AA size, aligns horizontally across 22 cols / 53.3mm width) |
| **13**| **TP4056 Charger & Protection**| 5V 1A Li-ion linear charger with Type-C USB port & DW01A protection | 1 | `CHG1` | ₹35 | ₹35 | [robu.in](https://robu.in/product/tp4056-1a-li-ion-lithium-battery-charging-module-with-current-protection-type-c/) | Safe Type-C charging (4.2V cutoff, red/blue status LEDs) and 2.5V cutoff protection |
| **14**| **Power Slide Switch** | Miniature SPST / SPDT 3-pin slide switch | 1 | `SW_PWR` | ₹10 | ₹10 | *[Pending]* | Master hardware ON/OFF power switch between TP4056 OUT+ and Pico Pin 39 (VSYS) |
| | **TOTAL ESTIMATED COST** | | | | | **₹1,151.00** | | *(Complete BOM for all core electronic and power components on single board)* |

---

## Interactive PCB Visualizer (`pcb_design_v2.html`)

Open [`pcb_design_v2.html`](pcb_design_v2.html) directly in any modern browser:

- **Full $22 \times 67$ Grid Visualization**: View component placement, solder joints, traces, and pinout legends.
- **Top / Bottom / X-Ray Perspectives**:
  - **Top View (Component Side)**: Displays tactile buttons, RGB LED strip header, IR optics, Pico headers, and front trace routing.
  - **Bottom View (Solder Side)**: Mirrored view showing all 8 column bus rails, 64 tap-to-rail solder joints, and backside corridor routing.
  - **X-Ray View**: Translucent composite view of both sides simultaneously.
- **High-Contrast Dual Color-Coding**:
  - **GREEN (`#22c55e`)** = **All Column Connections** (8 backside column rails, Pico GPIO column leads, and 64 button taps).
  - **RED (`#ef4444`)** = **All Row Connections** (8 row buses, front jumper wires, and Pico GPIO row leads).
- **F20 Crossover Jumper Bridge**: Clear rendering of the insulated jumper at F20 hopping over the Row 20 bus.
- **Interactive Inspection**: Hover or click any pad, button, or solder joint to see live pin assignments, GPIO nets, and soldering instructions.

---

## File Structure

```text
universal-IR-remote/
├── pcb_design_v2.html     # Interactive 22x67 dual-sided perfboard visualizer & solder guide
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
     - `4`: Optical Loopback Self-Test (GP18 TX blasts $\rightarrow$ GP17 RX verifies).
     - `6`: WS2812B RGB Addressable LED Strip (rainbow, mode colors, pulse test).

4. **Launch Main Remote**:
   - Run `main.py`. The RGB strip will cycle a smooth rainbow on boot, then light up with the active appliance mode color (e.g. Cyan for TV).
   - Press **Button 3 (MODE)** to switch appliance profiles and see the RGB color shift!
   - Press **Button 2 (LEARN)** to program any of the 62 buttons!
