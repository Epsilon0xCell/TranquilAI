#!/usr/bin/env python3
"""TranquilAI logo: open workshop drawer from slightly above, front panel dropped toward
the viewer, tiny six step staircase in its own rose felt compartment, short legged chair,
thread coil, two brass hinges nearby; Aoboshi One wordmark in dust gold stamped beneath.
At small sizes only drawer front, gold stamp, and stair silhouette remain."""
import sys, os
from PIL import Image, ImageDraw, ImageFont
v = sys.argv[1] if len(sys.argv) > 1 else "ship"
os.chdir(os.path.dirname(os.path.abspath(__file__)))
W, H = 900, 700
img = Image.new("RGB", (W, H), (40, 28, 18)); d = ImageDraw.Draw(img, "RGBA")
d.rectangle([170, 120, 730, 430], fill=(92, 62, 38), outline=(56, 38, 22), width=8)
d.rectangle([196, 146, 470, 404], fill=(178, 120, 122))
d.rectangle([486, 146, 704, 270], fill=(238, 232, 218)); d.rectangle([486, 286, 704, 404], fill=(206, 188, 168))
for k in range(6):  # staircase
    x, y = 224 + k * 34, 372 - k * 30
    d.rectangle([x, y, x + 108, y + 22], fill=(196, 158, 84), outline=(110, 84, 48), width=2)
d.line([(232, 368), (428, 196)], fill=(110, 84, 48), width=4)
# chair with one short leg
d.rectangle([530, 190, 580, 202], fill=(122, 84, 52)); d.rectangle([530, 148, 580, 190], fill=(122, 84, 52))
d.line([(534, 202), (534, 232)], fill=(122, 84, 52), width=5); d.line([(574, 202), (574, 218)], fill=(122, 84, 52), width=5)
for r in (26, 18, 10):  # thread coil
    d.ellipse([620 - r, 340 - r, 620 + r, 340 + r], outline=(196, 90, 100), width=4)
for hx in (510, 560):  # brass hinges
    d.rectangle([hx, 320, hx + 30, 360], fill=(196, 158, 84), outline=(120, 94, 44), width=2)
    d.ellipse([hx + 10, 334, hx + 20, 346], fill=(90, 68, 32))
d.polygon([(170, 430), (730, 430), (700, 486), (200, 486)], fill=(76, 50, 30))
try:
    f = ImageFont.truetype("fonts/AoboshiOne.ttf", 62)
except Exception:
    f = ImageFont.load_default()
bb = d.textbbox((0, 0), "TranquilAI", font=f)
d.text(((W - (bb[2] - bb[0])) / 2, 540), "TranquilAI", font=f, fill=(222, 182, 96))
out = "logo.png" if v == "ship" else f"scratch/logo-{v}.png"
img.save(out)
img.resize((64, 64)).save("scratch/logo64-ship.png" if v == "ship" else f"scratch/logo64-{v}.png")
print(out)
