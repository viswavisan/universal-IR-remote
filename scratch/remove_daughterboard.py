import re

html_path = r"c:\Users\viswa\OneDrive\Desktop\github_code\universal-IR-remote\pcb_design_v2.html"
with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Remove Daughterboard jump button from navbar & update Top button
old_btn = """          <button id="btnJumpBattery" title="Zoom to 18650 Battery & TP4056 Charger"
            style="background:rgba(16, 185, 129, 0.15); color:#6ee7b7; border-color:#059669; font-weight:700;">🔋
            Battery & Charger</button>
          <button id="btnJumpIrModule" title="Zoom to 3-Row IR Transceiver Daughterboard"
            style="background:rgba(168, 85, 247, 0.15); color:#d8b4fe; border-color:#a855f7; font-weight:700;">📡 IR
            Daughterboard</button>"""

new_btn = """          <button id="btnJumpBattery" title="Zoom to 18650 Battery & TP4056 Charger"
            style="background:rgba(16, 185, 129, 0.15); color:#6ee7b7; border-color:#059669; font-weight:700;">🔋
            Battery & Charger</button>"""

assert old_btn in html, "old_btn not found"
html = html.replace(old_btn, new_btn, 1)

# Update Top button title
old_top_btn = '<button id="btnJumpTop" title="Scroll to Pico & Optics">🔭 Top (Pico)</button>'
new_top_btn = '<button id="btnJumpTop" title="Scroll to Pico & Optics">🔭 Top (Pico & Optics)</button>'
if old_top_btn in html:
    html = html.replace(old_top_btn, new_top_btn, 1)

# 2. Remove <g id="irDaughterboardGroup"></g>
old_group = """          <!-- DEDICATED OPTICAL & IR TRANSCEIVER DAUGHTERBOARD MODULE (3-ROW ULTRA-COMPACT) -->
          <g id="irDaughterboardGroup"></g>"""
assert old_group in html, "old_group not found"
html = html.replace(old_group, "", 1)

# 3. Update trace comment
old_trace_comment = "// Top Power & 5-Pin IR Daughterboard Socket Connections:"
new_trace_comment = "// Unified Motherboard Top Power & Optical IR Transceiver Connections (Rows 1–3):"
assert old_trace_comment in html, "old_trace_comment not found"
html = html.replace(old_trace_comment, new_trace_comment, 1)

# 4. Remove renderIrDaughterboard function
start_marker = "    // -------------------------------------------------------------\n    // 5C. ULTRA-COMPACT 3-ROW OPTICAL & IR DAUGHTERBOARD BREAKOUT MODULE"
end_marker = "      g.innerHTML = html;\n    }"

start_idx = html.find(start_marker)
assert start_idx != -1, "start_marker not found"
end_idx = html.find(end_marker, start_idx)
assert end_idx != -1, "end_marker not found"
end_idx += len(end_marker)

html = html[:start_idx] + html[end_idx:]

# 5. Update SCENE bounds
old_scene = """    const SCENE_MIN_X = -360;
    const SCENE_MAX_X = 1220; // Includes Power Subsystem (-360..20), Motherboard (80..664), and IR Daughterboard (740..1200)
    const SCENE_W = SCENE_MAX_X - SCENE_MIN_X; // 1580px
    const SCENE_CX = (SCENE_MIN_X + SCENE_MAX_X) / 2; // 430px"""

new_scene = """    const SCENE_MIN_X = -360;
    const SCENE_MAX_X = 720; // Includes Power Subsystem (-360..20) and Motherboard (80..664)
    const SCENE_W = SCENE_MAX_X - SCENE_MIN_X; // 1080px
    const SCENE_CX = (SCENE_MIN_X + SCENE_MAX_X) / 2; // 180px"""

assert old_scene in html, "old_scene not found"
html = html.replace(old_scene, new_scene, 1)

# 6. Remove irModule from jumpToSection
old_jump_ir = """      } else if (section === 'irModule') {
        const irCenterX = 740 + 460 / 2; // 970
        currentScale = 0.95;
        currentX = cW / 2 - irCenterX * currentScale;
        currentY = 30 - 60 * currentScale;"""

assert old_jump_ir in html, "old_jump_ir not found"
html = html.replace(old_jump_ir, "", 1)

# 7. Remove btnJumpIrModule event listener
old_listener = """    const btnJumpIrModule = document.getElementById('btnJumpIrModule');
    if (btnJumpIrModule) btnJumpIrModule.addEventListener('click', () => jumpToSection('irModule'));\n"""
assert old_listener in html, "old_listener not found"
html = html.replace(old_listener, "", 1)

# 8. Update BOM table items
old_bom_led = """        spec: "5mm dark purple infrared emitting diodes (Mounted on 16×3 IR Daughterboard Row 1: LED1 @ Col 4,5; LED2 @ Col 12,13)",
        qty: 2,
        designator: "LED1, LED2",
        price: "₹20",
        link: "https://robu.in/product/5mm-940nm-ir-infrared-emitter-led/",
        role: "Dual high-intensity infrared transmitters on daughterboard facing North for wide-angle 15m optical beam" """

# Let's do exact regex or substring for BOM item 4
old_bom_led_str = 'spec: "5mm dark purple infrared emitting diodes (Mounted on 16×3 IR Daughterboard Row 1: LED1 @ Col 4,5; LED2 @ Col 12,13)",\n        qty: 2,\n        designator: "LED1, LED2",\n        price: "₹20",\n        link: "https://robu.in/product/5mm-940nm-ir-infrared-emitter-led/",\n        role: "Dual high-intensity infrared transmitters on daughterboard facing North for wide-angle 15m optical beam"'
new_bom_led_str = 'spec: "5mm dark purple infrared emitting diodes (Mounted on Motherboard Row 1 & 2: D1 @ D1–E1; D2 @ H2–I2)",\n        qty: 2,\n        designator: "LED1, LED2",\n        price: "₹20",\n        link: "https://robu.in/product/5mm-940nm-ir-infrared-emitter-led/",\n        role: "Dual high-intensity infrared transmitters on motherboard facing North for wide-angle 15m optical beam"'

assert old_bom_led_str in html, "old_bom_led_str not found"
html = html.replace(old_bom_led_str, new_bom_led_str, 1)

# Update BOM item 8 role (mounted at R2, S2, T2)
old_bom_rx_role = 'role: "Demodulates incoming raw 38kHz codes from original remotes for learning; mounted at P2, Q2, R2 facing North"'
new_bom_rx_role = 'role: "Demodulates incoming raw 38kHz codes from original remotes for learning; mounted at R2, S2, T2 facing North"'
if old_bom_rx_role in html:
    html = html.replace(old_bom_rx_role, new_bom_rx_role, 1)

# Remove BOM item 15 (daughterboard perfboard)
old_bom_15 = """,
      {
        id: 15,
        component: "3-Row IR Daughterboard Perfboard",
        spec: "2.54mm pitch double-sided protoboard strip (16 Columns × 3 Rows)",
        qty: 1,
        designator: "PCB_IR (16×3)",
        price: "₹30",
        link: "",
        role: "Dedicated ultra-compact breakout board for dual optical transmitters, receiver, driver, and 4-hole axial resistors"
      }"""
assert old_bom_15 in html, "old_bom_15 not found"
html = html.replace(old_bom_15, "", 1)

# 9. Remove renderIrDaughterboard() call
old_call = "      renderIrDaughterboard();\n"
assert old_call in html, "old_call not found"
html = html.replace(old_call, "", 1)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

print("pcb_design_v2.html updated cleanly!")
