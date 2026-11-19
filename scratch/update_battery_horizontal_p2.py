import re

html_path = r"c:\Users\viswa\OneDrive\Desktop\github_code\universal-IR-remote\pcb_design_v2.html"
with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

new_render_code = """    // -------------------------------------------------------------
    // 5B. REAL-SCALE HORIZONTAL AA / 14500 LI-ION POWER SUBSYSTEM
    // 1:1 PHYSICAL SIZE: AA CELL (50.5 × 14.5 mm) ALIGNED HORIZONTALLY WITH 22-COL WIDTH (53.3 mm)
    // -------------------------------------------------------------
    function renderPowerModule() {
      const g = document.getElementById('powerModuleGroup');
      if (!g) return;

      const pBat = getCoordPos('A', 1); // A1: +VSYS Battery Wire Input
      const pV1 = getCoordPos('V', 1);  // V1: Battery GND Input Rail

      // Bottom Power Subsystem Tray: sits directly below Row 67
      // Matches EXACT width of perfboard (BOARD_W = 584 px)
      const pwrX = BOARD_X;                         // 80
      const pwrY = BOARD_Y + BOARD_H + 20;          // 60 + 1664 + 20 = 1744
      const pwrW = BOARD_W;                         // 584
      const pwrH = 430;                             // 1744 to 2174

      let html = `
        <!-- Power Subsystem Chassis Plate -->
        <g class="power-subsystem">
          <rect x="${pwrX}" y="${pwrY}" width="${pwrW}" height="${pwrH}" rx="14" fill="#090e17" stroke="#1e293b" stroke-width="4" filter="url(#shadow)" />
          <rect x="${pwrX + 6}" y="${pwrY + 6}" width="${pwrW - 12}" height="${pwrH - 12}" rx="10" fill="none" stroke="#059669" stroke-width="1.2" stroke-opacity="0.65" />
          <rect x="${pwrX}" y="${pwrY}" width="${pwrW}" height="${pwrH}" rx="14" fill="url(#fiberglassPattern)" opacity="0.25" />

          <!-- Header Title & Physical Scale Notes -->
          <text x="${pwrX + pwrW / 2}" y="${pwrY + 24}" fill="#10b981" font-size="12" font-weight="900" text-anchor="middle" font-family="monospace">RECHARGEABLE POWER SUBSYSTEM (AA / 14500 HORIZONTAL)</text>
          
          <rect x="${pwrX + 24}" y="${pwrY + 34}" width="${pwrW - 48}" height="28" rx="5" fill="#0f172a" stroke="#334155" stroke-width="1" />
          <text x="${pwrX + pwrW / 2}" y="${pwrY + 52}" fill="#38bdf8" font-size="8.5" font-weight="800" font-family="monospace" text-anchor="middle">1× AA / 14500 Li-ion (50.5 × 14.5 mm) • 1:1 Matched Across 22 Cols (53.3 mm Width)</text>

          <!-- ========================================================= -->
          <!-- 1. 14500 AA BATTERY HOLDER TRAY (HORIZONTAL: 54mm × 16.5mm) -->
          <!-- 54.0 mm * 9.45 = 510 px, 16.5 mm * 9.45 = 156 px          -->
          <!-- Aligns from Col A (x=120) to Col V (x=624)                 -->
          <!-- ========================================================= -->
          ${(() => {
            const hW = 510;
            const hH = 156;
            const hX = pwrX + (pwrW - hW) / 2; // 80 + (584 - 510)/2 = 117 px (Col A=120, Col V=624)
            const hY = pwrY + 74;

            // 14500 Cell dimensions: 50.5 mm * 9.45 = 477 px, 14.5 mm * 9.45 = 137 px
            const cW = 477;
            const cH = 137;
            const cX = hX + (hW - cW) / 2;     // 117 + 16.5 = 133.5 px
            const cY = hY + (hH - cH) / 2;     // seated inside holder

            return `
              <g class="comp-14500-real" data-net="VSYS_BAT">
                <title>14500 3.7V 1000mAh Li-ion Cell (AA Size: 50.5mm × 14.5mm) in Horizontal AA Battery Holder</title>

                <!-- Holder Dimension Callout -->
                <rect x="${hX + hW / 2 - 120}" y="${hY - 14}" width="240" height="13" rx="3" fill="#1e293b" stroke="#10b981" stroke-width="0.8" />
                <text x="${hX + hW / 2}" y="${hY - 4.5}" fill="#a7f3d0" font-size="7" font-weight="800" font-family="monospace" text-anchor="middle">Horizontal AA Holder: 54.0 × 16.5 mm (Span Col A ➔ Col V)</text>

                <!-- Injection-Molded ABS Battery Holder Tray (Horizontal) -->
                <rect x="${hX}" y="${hY}" width="${hW}" height="${hH}" rx="10" fill="#090d16" stroke="#334155" stroke-width="2.5" filter="url(#shadow)" />
                <rect x="${hX + 9}" y="${hY + 9}" width="${hW - 18}" height="${hH - 18}" rx="7" fill="#030712" />

                <!-- Left Positive Nickel-Plated Leaf Contact Button -->
                <rect x="${hX + 6}" y="${hY + hH / 2 - 24}" width="14" height="48" rx="3" fill="url(#metallicCapGrad)" stroke="#94a3b8" stroke-width="1" />
                <circle id="holder_pos_eyelet" cx="${hX + 13}" cy="${hY + 16}" r="5" fill="url(#solderGrad)" stroke="#ef4444" stroke-width="1.2" />
                <text x="${hX + 24}" y="${hY + 20}" fill="#fca5a5" font-size="7.5" font-weight="900" font-family="monospace">[+]</text>

                <!-- Right Negative Conical Spring Contact -->
                <g transform="translate(${hX + hW - 16}, ${hY + hH / 2}) rotate(90)">
                  <path d="M -24 0 C -16 -12, 16 -12, 24 0 C 16 8, -16 8, -12 0 C -8 -4, 8 -4, 12 0" fill="none" stroke="#cbd5e1" stroke-width="2.5" />
                </g>
                <circle id="holder_neg_eyelet" cx="${hX + hW - 13}" cy="${hY + 16}" r="5" fill="url(#solderGrad)" stroke="#38bdf8" stroke-width="1.2" />
                <text x="${hX + hW - 36}" y="${hY + 20}" fill="#7dd3fc" font-size="7.5" font-weight="900" font-family="monospace">[-]</text>

                <!-- ===================================================== -->
                <!-- 14500 (AA SIZE) LI-ION BATTERY CELL (50.5 × 14.5 mm)  -->
                <!-- ===================================================== -->
                <!-- Positive Raised Metallic Nipple (Left Cathode +) -->
                <rect x="${cX - 14}" y="${cY + (cH - 40) / 2}" width="14" height="40" rx="3" fill="url(#metallicCapGrad)" stroke="#94a3b8" stroke-width="1.2" />
                <!-- Insulator Ring underneath nipple -->
                <rect x="${cX - 3}" y="${cY + (cH - 54) / 2}" width="3" height="54" rx="1" fill="#ffffff" />

                <!-- 14500 Horizontal Cylindrical Battery Body -->
                <rect x="${cX}" y="${cY}" width="${cW}" height="${cH}" rx="10" fill="url(#battery14500Grad)" stroke="#16a34a" stroke-width="2" filter="url(#shadow)" />
                <!-- 3D Cylindrical Highlight Bar (Horizontal) -->
                <line x1="${cX + 12}" y1="${cY + cH * 0.28}" x2="${cX + cW - 12}" y2="${cY + cH * 0.28}" stroke="#ffffff" stroke-width="7" opacity="0.38" stroke-linecap="round" />

                <!-- Negative Metallic Base Plate (Right Anode -) -->
                <rect x="${cX + cW - 6}" y="${cY + 8}" width="10" height="${cH - 16}" rx="3" fill="url(#metallicCapGrad)" stroke="#64748b" stroke-width="1.2" />

                <!-- Realistic Metallic Battery Label Badge -->
                <g transform="translate(${cX + cW / 2}, ${cY + cH / 2})">
                  <rect x="-130" y="-48" width="260" height="96" rx="6" fill="rgba(15, 23, 42, 0.94)" stroke="#eab308" stroke-width="1.2" />
                  
                  <text x="0" y="-28" fill="#fef08a" font-size="9.5" font-weight="900" font-family="monospace" text-anchor="middle">ORANGE / PKCELL 14500</text>
                  <text x="0" y="-13" fill="#38bdf8" font-size="11.5" font-weight="900" font-family="monospace" text-anchor="middle">3.7V Li-ion (AA Size)</text>
                  <rect x="-90" y="-6" width="180" height="1.5" fill="#eab308" />

                  <text x="0" y="11" fill="#ffffff" font-size="12" font-weight="900" font-family="monospace" text-anchor="middle">1000 mAh • 3.7 Wh</text>
                  <text x="0" y="26" fill="#a7f3d0" font-size="7.5" font-weight="700" font-family="monospace" text-anchor="middle">Ø 14.5 mm × 50.5 mm • Aligned Across 22-Col Width</text>
                  <text x="0" y="40" fill="#f59e0b" font-size="7" font-weight="800" font-family="monospace" text-anchor="middle">4.2V CUTOFF • PROTECTED VIA TP4056</text>

                  <!-- Polarity Badges -->
                  <text x="-112" y="3" fill="#ef4444" font-size="9" font-weight="900" font-family="monospace" text-anchor="middle">◀ [+]</text>
                  <text x="112" y="3" fill="#38bdf8" font-size="9" font-weight="900" font-family="monospace" text-anchor="middle">[-] ▶</text>
                </g>
              </g>
            `;
          })()}

          <!-- ========================================================= -->
          <!-- 2. SPST MINIATURE SLIDE SWITCH (POWER ON/OFF)             -->
          <!-- 8.5 mm * 9.45 = 80 px, 4.0 mm * 9.45 = 38 px              -->
          <!-- ========================================================= -->
          ${(() => {
            const swW = 84;
            const swH = 38;
            const swX = pwrX + 40;             // 120 (aligned with Column A)
            const swY = pwrY + 258;

            return `
              <g class="comp-switch" data-net="VSYS_BAT">
                <title>Master Power Slide Switch (SPST Miniature, Real Size: 8.5mm × 4.0mm)</title>
                <!-- Switch Label -->
                <text x="${swX + swW / 2}" y="${swY - 8}" fill="#cbd5e1" font-size="7.5" font-weight="800" font-family="monospace" text-anchor="middle">POWER SWITCH</text>
                
                <!-- Metallic Switch Casing -->
                <rect x="${swX}" y="${swY}" width="${swW}" height="${swH}" rx="4" fill="url(#metallicCapGrad)" stroke="#334155" stroke-width="1.6" filter="url(#shadow)" />
                <rect x="${swX + 4}" y="${swY + 4}" width="${swW - 8}" height="${swH - 8}" rx="2" fill="#0f172a" />
                
                <!-- Slider Knob in ON position (slid to left) -->
                <rect x="${swX + 8}" y="${swY + 6}" width="30" height="${swH - 12}" rx="3" fill="#10b981" stroke="#059669" stroke-width="1.2" />
                <text x="${swX + 23}" y="${swY + 23}" fill="#ffffff" font-size="8.5" font-weight="900" font-family="monospace" text-anchor="middle">ON</text>
                <text x="${swX + 58}" y="${swY + 23}" fill="#64748b" font-size="8" font-weight="700" font-family="monospace" text-anchor="middle">OFF</text>

                <!-- Terminals underneath -->
                <circle id="sw_pin_in" cx="${swX + 16}" cy="${swY + swH + 8}" r="5" fill="url(#solderGrad)" stroke="#f59e0b" stroke-width="1.2" />
                <circle id="sw_pin_out" cx="${swX + 38}" cy="${swY + swH + 8}" r="5" fill="url(#solderGrad)" stroke="#f59e0b" stroke-width="1.2" />
              </g>
            `;
          })()}

          <!-- ========================================================= -->
          <!-- 3. TP4056 USB-C CHARGING MODULE (28.0 mm × 17.3 mm)       -->
          <!-- 28.0 mm * 9.45 = 265 px, 17.3 mm * 9.45 = 164 px          -->
          <!-- Facing DOWNWARDS: USB-C port at bottom of remote chassis  -->
          <!-- ========================================================= -->
          ${(() => {
            const tpW = 265;
            const tpH = 135;
            const tpX = pwrX + pwrW - tpW - 40; // 80 + 584 - 265 - 40 = 359 px
            const tpY = pwrY + 245;

            return `
              <g class="comp-tp4056-real" data-net="VSYS_BAT">
                <title>TP4056 1A Linear Li-ion Charger with DW01A/8205A Protection (Real Size: 28.0mm × 17.3mm)</title>
                
                <!-- Dimension Tag above module -->
                <rect x="${tpX}" y="${tpY - 18}" width="124" height="14" rx="3" fill="#1e293b" stroke="#3b82f6" stroke-width="0.8" />
                <text x="${tpX + 62}" y="${tpY - 8}" fill="#93c5fd" font-size="7" font-weight="800" font-family="monospace" text-anchor="middle">TP4056: 28.0 × 17.3 mm</text>

                <!-- Deep Blue FR4 PCB Body with rounded corners -->
                <rect x="${tpX}" y="${tpY}" width="${tpW}" height="${tpH}" rx="8" fill="url(#tp4056PcbGrad)" stroke="#3b82f6" stroke-width="2.2" filter="url(#shadow)" />
                <rect x="${tpX + 6}" y="${tpY + 6}" width="${tpW - 12}" height="${tpH - 12}" rx="5" fill="none" stroke="#60a5fa" stroke-width="0.8" opacity="0.6" />
                
                <!-- 4 Corner Mounting Holes (d = 3.0mm ~ 28px) -->
                <circle cx="${tpX + 16}" cy="${tpY + 16}" r="5" fill="#090e17" stroke="#3b82f6" stroke-width="1" />
                <circle cx="${tpX + tpW - 16}" cy="${tpY + 16}" r="5" fill="#090e17" stroke="#3b82f6" stroke-width="1" />
                <circle cx="${tpX + 16}" cy="${tpY + tpH - 16}" r="5" fill="#090e17" stroke="#3b82f6" stroke-width="1" />
                <circle cx="${tpX + tpW - 16}" cy="${tpY + tpH - 16}" r="5" fill="#090e17" stroke="#3b82f6" stroke-width="1" />

                <!-- Bottom Accessible Type-C Receptacle (pointing down at base) -->
                <rect x="${tpX + tpW / 2 - 40}" y="${tpY + tpH - 10}" width="80" height="28" rx="6" fill="url(#metallicCapGrad)" stroke="#475569" stroke-width="1.8" />
                <rect x="${tpX + tpW / 2 - 34}" y="${tpY + tpH - 5}" width="68" height="16" rx="4" fill="#090d16" />
                <rect x="${tpX + tpW / 2 - 20}" y="${tpY + tpH + 2}" width="40" height="2" fill="#fbbf24" opacity="0.8" />
                <text x="${tpX + tpW / 2}" y="${tpY + tpH + 30}" fill="#94a3b8" font-size="7" font-weight="800" font-family="monospace" text-anchor="middle">5V TYPE-C (BOTTOM ACCESSIBLE)</text>

                <!-- TP4056 Controller IC -->
                <rect x="${tpX + 54}" y="${tpY + 36}" width="50" height="42" rx="3" fill="#0f172a" stroke="#475569" stroke-width="1.2" />
                <text x="${tpX + 79}" y="${tpY + 56}" fill="#f8fafc" font-size="8" font-weight="900" font-family="monospace" text-anchor="middle">TP4056</text>
                <text x="${tpX + 79}" y="${tpY + 68}" fill="#64748b" font-size="6" font-family="monospace" text-anchor="middle">1.0A CC/CV</text>

                <!-- DW01A + 8205A Protection Chips -->
                <rect x="${tpX + 124}" y="${tpY + 34}" width="28" height="22" rx="2" fill="#0f172a" stroke="#334155" stroke-width="1" />
                <text x="${tpX + 138}" y="${tpY + 48}" fill="#cbd5e1" font-size="6" font-weight="900" font-family="monospace" text-anchor="middle">DW01</text>
                <rect x="${tpX + 122}" y="${tpY + 62}" width="32" height="24" rx="2" fill="#0f172a" stroke="#334155" stroke-width="1" />
                <text x="${tpX + 138}" y="${tpY + 77}" fill="#cbd5e1" font-size="6" font-weight="900" font-family="monospace" text-anchor="middle">8205A</text>

                <!-- Status LEDs -->
                <circle cx="${tpX + 30}" cy="${tpY + 46}" r="4" fill="#ef4444" stroke="#f87171" stroke-width="1" />
                <text x="${tpX + 30}" y="${tpY + 60}" fill="#fca5a5" font-size="5.5" font-weight="800" font-family="monospace" text-anchor="middle">CHG</text>
                <circle cx="${tpX + 30}" cy="${tpY + 74}" r="4" fill="#3b82f6" stroke="#93c5fd" stroke-width="1" />
                <text x="${tpX + 30}" y="${tpY + 88}" fill="#93c5fd" font-size="5.5" font-weight="800" font-family="monospace" text-anchor="middle">FULL</text>

                <!-- Solder Eyelet Pads -->
                <!-- B+ Pad (to 14500 positive terminal) -->
                <circle id="tp_pad_bplus" cx="${tpX + 16}" cy="${tpY + 20}" r="8" fill="url(#solderGrad)" stroke="#ef4444" stroke-width="1.8" />
                <text x="${tpX + 16}" y="${tpY + 12}" fill="#fca5a5" font-size="7" font-weight="900" font-family="monospace" text-anchor="middle">B+</text>

                <!-- B- Pad (to 14500 negative terminal) -->
                <circle id="tp_pad_bminus" cx="${tpX + tpW - 16}" cy="${tpY + 20}" r="8" fill="url(#solderGrad)" stroke="#38bdf8" stroke-width="1.8" />
                <text x="${tpX + tpW - 16}" y="${tpY + 12}" fill="#7dd3fc" font-size="7" font-weight="900" font-family="monospace" text-anchor="middle">B-</text>

                <!-- OUT+ Pad (to Switch -> Motherboard A1 VSYS) -->
                <circle id="tp_pad_outplus" cx="${tpX + 16}" cy="${tpY + tpH - 24}" r="8" fill="url(#solderGrad)" stroke="#f59e0b" stroke-width="1.8" />
                <text x="${tpX + 32}" y="${tpY + tpH - 22}" fill="#fde047" font-size="7" font-weight="900" font-family="monospace" text-anchor="start">OUT+</text>

                <!-- OUT- Pad (to Motherboard Pad V1 GND) -->
                <circle id="tp_pad_outminus" cx="${tpX + tpW - 16}" cy="${tpY + tpH - 24}" r="8" fill="url(#solderGrad)" stroke="#64748b" stroke-width="1.8" />
                <text x="${tpX + tpW - 32}" y="${tpY + tpH - 22}" fill="#cbd5e1" font-size="7" font-weight="900" font-family="monospace" text-anchor="end">OUT-</text>
              </g>
            `;
          })()}

          <!-- ========================================================= -->
          <!-- 4. REAL INTERCONNECTING SILICONE WIRING HARNESS           -->
          <!-- ========================================================= -->
          ${(() => {
            const hW = 510;
            const hH = 156;
            const hX = pwrX + (pwrW - hW) / 2; // 117 px
            const hY = pwrY + 74;

            const tpW = 265, tpH = 135;
            const tpX = pwrX + pwrW - tpW - 40; // 359 px
            const tpY = pwrY + 245;

            const swW = 84, swH = 38;
            const swX = pwrX + 40;              // 120 px
            const swY = pwrY + 258;

            // Wire 1: 14500 (+) eyelet -> TP4056 B+
            const w1_start = { x: hX + 13, y: hY + 16 };
            const w1_end = { x: tpX + 16, y: tpY + 20 };

            // Wire 2: 14500 (-) eyelet -> TP4056 B-
            const w2_start = { x: hX + hW - 13, y: hY + 16 };
            const w2_end = { x: tpX + tpW - 16, y: tpY + 20 };

            // Wire 3: TP4056 OUT+ -> Switch In
            const w3_start = { x: tpX + 16, y: tpY + tpH - 24 };
            const w3_end = { x: swX + 16, y: swY + swH + 8 };

            // Wire 4: Switch Out -> Up left chassis duct into Motherboard Pad A1 (+VSYS IN)
            const w4_start = { x: swX + 38, y: swY + swH + 8 };
            const w4_end = { x: pBat.x, y: pBat.y };

            // Wire 5: TP4056 OUT- -> Up right chassis duct into Motherboard Pad V1 (GND)
            const w5_start = { x: tpX + tpW - 16, y: tpY + tpH - 24 };
            const w5_end = { x: pV1.x, y: pV1.y };

            return `
              <g class="power-wiring-harness">
                <!-- Wire 1: 14500 (+) Red to TP4056 B+ -->
                <path d="M ${w1_start.x} ${w1_start.y} C ${w1_start.x - 20} ${w1_start.y + 60}, ${w1_end.x - 40} ${w1_end.y - 40}, ${w1_end.x} ${w1_end.y}" fill="none" stroke="#ef4444" stroke-width="3.5" stroke-linecap="round" />
                <path d="M ${w1_start.x} ${w1_start.y} C ${w1_start.x - 20} ${w1_start.y + 60}, ${w1_end.x - 40} ${w1_end.y - 40}, ${w1_end.x} ${w1_end.y}" fill="none" stroke="#fca5a5" stroke-width="1" stroke-linecap="round" opacity="0.6" />

                <!-- Wire 2: 14500 (-) Black to TP4056 B- -->
                <path d="M ${w2_start.x} ${w2_start.y} C ${w2_start.x + 20} ${w2_start.y + 60}, ${w2_end.x + 40} ${w2_end.y - 40}, ${w2_end.x} ${w2_end.y}" fill="none" stroke="#0284c7" stroke-width="3.5" stroke-linecap="round" />
                <path d="M ${w2_start.x} ${w2_start.y} C ${w2_start.x + 20} ${w2_start.y + 60}, ${w2_end.x + 40} ${w2_end.y - 40}, ${w2_end.x} ${w2_end.y}" fill="none" stroke="#38bdf8" stroke-width="1.2" stroke-linecap="round" opacity="0.7" />

                <!-- Wire 3: TP4056 OUT+ to Switch In -->
                <path d="M ${w3_start.x} ${w3_start.y} C ${w3_start.x - 40} ${w3_start.y + 50}, ${w3_end.x + 40} ${w3_end.y + 50}, ${w3_end.x} ${w3_end.y}" fill="none" stroke="#f59e0b" stroke-width="3.2" stroke-linecap="round" />

                <!-- Wire 4: Switch Out -> Up left side duct to Motherboard Pad A1 (+VSYS IN) -->
                <path d="M ${w4_start.x} ${w4_start.y} C ${w4_start.x - 40} ${w4_start.y + 40}, 50 ${pwrY + 100}, 50 ${BOARD_Y + BOARD_H} L 50 120 C 50 80, ${w4_end.x - 20} 80, ${w4_end.x} ${w4_end.y}" fill="none" stroke="#f59e0b" stroke-width="3.8" stroke-linecap="round" data-net="VSYS_BAT">
                  <title>Switched Battery Power Rail: Runs up left chassis margin duct directly into Pad A1 (+VSYS IN)</title>
                </path>
                <path d="M ${w4_start.x} ${w4_start.y} C ${w4_start.x - 40} ${w4_start.y + 40}, 50 ${pwrY + 100}, 50 ${BOARD_Y + BOARD_H} L 50 120 C 50 80, ${w4_end.x - 20} 80, ${w4_end.x} ${w4_end.y}" fill="none" stroke="#fef08a" stroke-width="1.2" stroke-linecap="round" opacity="0.75" pointer-events="none" />

                <!-- Wire 5: TP4056 OUT- -> Up right side duct to Motherboard Pad V1 (GND) -->
                <path d="M ${w5_start.x} ${w5_start.y} C ${w5_start.x + 40} ${w5_start.y + 40}, ${BOARD_X + BOARD_W + 30} ${pwrY + 100}, ${BOARD_X + BOARD_W + 30} ${BOARD_Y + BOARD_H} L ${BOARD_X + BOARD_W + 30} 120 C ${BOARD_X + BOARD_W + 30} 80, ${w5_end.x + 20} 80, ${w5_end.x} ${w5_end.y}" fill="none" stroke="#475569" stroke-width="3.8" stroke-linecap="round" data-net="GND">
                  <title>Battery Ground Rail: Runs up right chassis margin duct directly into Pad V1 (Row 1 Master Ground)</title>
                </path>
                <path d="M ${w5_start.x} ${w5_start.y} C ${w5_start.x + 40} ${w5_start.y + 40}, ${BOARD_X + BOARD_W + 30} ${pwrY + 100}, ${BOARD_X + BOARD_W + 30} ${BOARD_Y + BOARD_H} L ${BOARD_X + BOARD_W + 30} 120 C ${BOARD_X + BOARD_W + 30} 80, ${w5_end.x + 20} 80, ${w5_end.x} ${w5_end.y}" fill="none" stroke="#94a3b8" stroke-width="1.2" stroke-linecap="round" opacity="0.75" pointer-events="none" />
              </g>
            `;
          })()}
        </g>
      `;

      g.innerHTML = html;
    }"""

start_marker = "    // -------------------------------------------------------------\n    // 5B. REAL-SCALE POWER SUBSYSTEM"
end_marker = "      g.innerHTML = html;\n    }"

start_idx = html.find(start_marker)
assert start_idx != -1, "start_marker not found"
end_idx = html.find(end_marker, start_idx)
assert end_idx != -1, "end_marker not found"
end_idx += len(end_marker)

html = html[:start_idx] + new_render_code + html[end_idx:]

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

print("Part 2: renderPowerModule updated cleanly!")
