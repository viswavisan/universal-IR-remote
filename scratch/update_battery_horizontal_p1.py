import re

html_path = r"c:\Users\viswa\OneDrive\Desktop\github_code\universal-IR-remote\pcb_design_v2.html"
with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Add horizontal 14500 battery gradient in <defs>
old_grad = """          <!-- 18650 3D Cylindrical Li-ion Gradient -->
          <linearGradient id="battery18650Grad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#14532d" />
            <stop offset="12%" stop-color="#16a34a" />
            <stop offset="35%" stop-color="#4ade80" />
            <stop offset="55%" stop-color="#22c55e" />
            <stop offset="85%" stop-color="#15803d" />
            <stop offset="100%" stop-color="#052e16" />
          </linearGradient>"""

new_grad = """          <!-- 14500 (AA Size) 3D Horizontal Cylindrical Li-ion Gradient (Vertical curvature) -->
          <linearGradient id="battery14500Grad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#14532d" />
            <stop offset="12%" stop-color="#16a34a" />
            <stop offset="30%" stop-color="#86efac" />
            <stop offset="50%" stop-color="#22c55e" />
            <stop offset="85%" stop-color="#15803d" />
            <stop offset="100%" stop-color="#052e16" />
          </linearGradient>"""

assert old_grad in html, "old_grad not found"
html = html.replace(old_grad, new_grad, 1)

# 2. Update SCENE coordinates in JS
old_scene = """    const SCENE_MIN_X = -360;
    const SCENE_MAX_X = 720; // Includes Power Subsystem (-360..20) and Motherboard (80..664)
    const SCENE_W = SCENE_MAX_X - SCENE_MIN_X; // 1080px
    const SCENE_CX = (SCENE_MIN_X + SCENE_MAX_X) / 2; // 180px
    const SCENE_CY = BOARD_Y + BOARD_H / 2; // 60 + 808 = 868"""

new_scene = """    const SCENE_MIN_X = 20;
    const SCENE_MAX_X = 724; // Motherboard & Bottom Battery Compartment width: 584px (Cols A..V = 504px)
    const SCENE_W = SCENE_MAX_X - SCENE_MIN_X; // 704px
    const SCENE_CX = BOARD_CX; // Centered at 372px
    const SCENE_CY = (BOARD_Y + BOARD_H + 340) / 2; // ~1032px"""

assert old_scene in html, "old_scene not found"
html = html.replace(old_scene, new_scene, 1)

# 3. Update jumpToSection for 'battery'
old_jump_bat = """      } else if (section === 'battery') {
        const pwrCenterX = -360 + 380 / 2; // -170
        currentScale = 0.84;
        currentX = cW / 2 - pwrCenterX * currentScale;
        currentY = 30 - 60 * currentScale;"""

new_jump_bat = """      } else if (section === 'battery') {
        if (currentScale < 0.75) currentScale = 0.95;
        currentX = cW / 2 - BOARD_CX * currentScale;
        const pwrY = BOARD_Y + BOARD_H + 20;
        currentY = 30 - pwrY * currentScale;"""

assert old_jump_bat in html, "old_jump_bat not found"
html = html.replace(old_jump_bat, new_jump_bat, 1)

# 4. Update Header Subtitle
old_sub = "• 3.7V 18650 2000mAh + TP4056 USB-C • 22×67 Perfboard"
new_sub = "• 3.7V 14500 (AA Size) Li-ion + TP4056 USB-C • 22×67 Perfboard"
if old_sub in html:
    html = html.replace(old_sub, new_sub, 1)

# 5. Update BOM items
old_bom_bat = """        component: "18650 Li-ion Battery",
        spec: "3.7V 2000mAh Cylindrical Li-ion Rechargeable Cell (with battery holder / solder tabs)",
        qty: 1,
        designator: "BAT1",
        price: "₹180",
        link: "https://robu.in/product/orange-icr18650-2000mah-3-7v-lithium-ion-battery/",
        role: "Main 3.7V rechargeable power source (100+ hours of continuous scanning per charge)\""""

new_bom_bat = """        component: "14500 3.7V Li-ion Battery (AA Size)",
        spec: "3.7V 800–1200mAh Cylindrical 14500 Li-ion Rechargeable Cell (Ø14.5mm × 50.5mm, AA Form Factor) + 1× AA Horizontal Holder",
        qty: 1,
        designator: "BAT1",
        price: "₹160",
        link: "https://robu.in/product/orange-icr14500-800mah-3-7v-lithium-ion-battery/",
        role: "Main 3.7V rechargeable power cell (AA size, aligns horizontally across board width: 50.5mm matches 22 cols / 53.3mm)\""""

assert old_bom_bat in html, "old_bom_bat not found"
html = html.replace(old_bom_bat, new_bom_bat, 1)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

print("Part 1: Header, defs, BOM, and scene bounds updated!")
