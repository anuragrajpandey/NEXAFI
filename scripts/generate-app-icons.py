#!/usr/bin/env python3
"""Regenerate NEXAFI TV app icons from the single master PNG.

Run from the repository root. Pillow writes all raster sizes plus multi-resolution
Windows ICO and macOS ICNS files. This script intentionally changes only icon assets.
"""
from pathlib import Path
import re
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ICON_DIR = ROOT / "packages" / "app" / "src-tauri" / "icons"
MASTER = ICON_DIR / "NEXAFI.png"
RESAMPLING = Image.Resampling.LANCZOS

if not MASTER.is_file():
    raise SystemExit(f"Missing master icon: {MASTER}")

with Image.open(MASTER) as opened:
    master = opened.convert("RGBA")

if master.width != master.height:
    raise SystemExit(f"Master icon must be square, got {master.width}x{master.height}")

def target_size(path: Path):
    name = path.stem
    match = re.search(r"(\d+)x(\d+)", name, re.IGNORECASE)
    if match:
        return int(match.group(1)), int(match.group(2))
    match = re.search(r"Square(\d+)x(\d+)", name, re.IGNORECASE)
    if match:
        return int(match.group(1)), int(match.group(2))
    for density, pixels in (
        ("xxxhdpi", 192), ("xxhdpi", 144), ("xhdpi", 96),
        ("hdpi", 72), ("mdpi", 48), ("ldpi", 36),
    ):
        if f"mipmap-{density}" in str(path).lower() or f"drawable-{density}" in str(path).lower():
            return pixels, pixels
    if "storelogo" in name.lower():
        return 50, 50
    if name.lower() in {"nexafi", "icon"}:
        return 512, 512
    return None

updated = []
for path in ICON_DIR.rglob("*.png"):
    if path.resolve() == MASTER.resolve():
        continue
    size = target_size(path)
    if size is None:
        continue
    image = master.resize(size, RESAMPLING)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG", optimize=True)
    updated.append(f"{path.relative_to(ROOT)}: {size[0]}x{size[1]}")

ico = ICON_DIR / "icon.ico"
master.save(ico, format="ICO", sizes=[(16,16), (24,24), (32,32), (48,48), (64,64), (128,128), (256,256)])
icns = ICON_DIR / "icon.icns"
master.save(icns, format="ICNS", sizes=[(16,16), (32,32), (64,64), (128,128), (256,256), (512,512)])

# Validate that the important Tauri icons have the expected formats and sizes.
for relative, expected in (("32x32.png", (32,32)), ("128x128.png", (128,128)), ("128x128@2x.png", (256,256))):
    target = ICON_DIR / relative
    if not target.is_file():
        raise SystemExit(f"Expected Tauri icon was not found: {target}")
    with Image.open(target) as image:
        if image.size != expected:
            raise SystemExit(f"{target} has size {image.size}, expected {expected}")
with Image.open(ico) as image:
    if image.format != "ICO":
        raise SystemExit("Windows icon validation failed")
with Image.open(icns) as image:
    if image.format != "ICNS":
        raise SystemExit("macOS icon validation failed")

print(f"Generated {len(updated)} PNG icon files from {MASTER.name}.")
print("\n".join(updated))
print("Validated multi-resolution icon.ico and icon.icns.")
