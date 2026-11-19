html_path = r"c:\Users\viswa\OneDrive\Desktop\github_code\universal-IR-remote\pcb_design_v2.html"
with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

replacements = [
    (
        'title="Zoom to 18650 Battery & TP4056 Charger"',
        'title="Zoom to 14500 (AA Size) Battery & TP4056 Charger"'
    ),
    (
        '<!-- REAL-SCALE POWER SUBSYSTEM (1:1 Physical Size: TP4056 + 18650 Battery + Switch) -->',
        '<!-- REAL-SCALE POWER SUBSYSTEM (1:1 Physical Size: TP4056 + 14500 AA Battery + Switch) -->'
    ),
    (
        '3.7V 18650 Li-ion cell (2000mAh) + TP4056 USB-C',
        '3.7V 14500 Li-ion cell (AA Size) + TP4056 USB-C'
    ),
    (
        '<div>• 1× 18650 3.7V 2000mAh Li-ion Battery</div>',
        '<div>• 1× 14500 3.7V 1000mAh Li-ion Battery (AA Size)</div>'
    ),
    (
        '3.7V 18650 (2000mAh) + TP4056',
        '3.7V 14500 AA Li-ion + TP4056'
    ),
    (
        "TP4056 OUT+ (3.7V 18650) ➔ Switch",
        "TP4056 OUT+ (3.7V 14500 AA) ➔ Switch"
    )
]

for old, new in replacements:
    assert old in html, f"Target not found: {old}"
    html = html.replace(old, new, 1)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

print("All remaining 18650 occurrences replaced with 14500 (AA Size) successfully!")
