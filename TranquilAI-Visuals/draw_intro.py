#!/usr/bin/env python3
"""TranquilAI intro banner: one open workshop drawer filling the frame, wordless. Stair on
rose felt beside a thimble, three tiny chairs, bundled matchsticks and veneer, tools laid
down mid job, magnifying glass, one curled shaving bridging two compartments, dark bench
and lamplight pool beyond. No text, letters, numbers, or signage."""
import sys, os, random
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
random.seed(97)
v = sys.argv[1] if len(sys.argv) > 1 else "ship"
os.chdir(os.path.dirname(os.path.abspath(__file__)))
W, H = 1600, 900
BROWN = (92, 62, 38); ROSE = (178, 120, 122); GOLD = (196, 158, 84); WHITE = (238, 232, 218)
img = Image.new("RGB", (W, H), (18, 14, 10)); d = ImageDraw.Draw(img, "RGBA")
d.ellipse([250, 60, 1350, 840], fill=(52, 38, 24))  # lamplight pool on bench
# drawer body
d.rectangle([110, 110, 1490, 800], fill=BROWN, outline=(60, 40, 24), width=10)
cols = [110, 590, 1010, 1490]; rows = [110, 470, 800]
for i in range(3):
    for j in range(1):
        x0, x1 = cols[i], cols[i + 1]; y0, y1 = rows[j], rows[j + 1]
        felt = ROSE if (i == 0 and j == 0) else WHITE if (i + j) % 2 else (206, 188, 168)
        d.rectangle([x0 + 14, y0 + 14, x1 - 14, y1 - 14], fill=felt)
# rear row compartments (second band)
d.rectangle([124, 484, 576, 786], fill=(206, 188, 168)); d.rectangle([604, 484, 996, 786], fill=ROSE); d.rectangle([1024, 484, 1476, 786], fill=WHITE)
# cell 1: miniature staircase on rose felt, six treads, rail, pale top step
for k in range(6):
    x, y = 170 + k * 52, 400 - k * 34
    d.rectangle([x, y, x + 150, y + 30], fill=(214, 186, 138) if k == 5 else GOLD, outline=(110, 84, 48), width=2)
d.line([(180, 396), (500, 196)], fill=(110, 84, 48), width=5)
for k in range(5):
    d.line([(200 + k * 66, 380 - k * 40), (200 + k * 66, 348 - k * 40)], fill=(110, 84, 48), width=4)
# thimble taller than stair is wide
d.polygon([(500, 300), (560, 300), (550, 190), (510, 190)], fill=(186, 188, 190), outline=(120, 122, 124), width=2)
for ry in (214, 244, 272):
    for rx in (516, 534):
        d.ellipse([rx, ry, rx + 9, ry + 9], fill=(130, 132, 134))
# cell 2: three chairs in a row
for ci, col in enumerate(((122, 84, 52), (150, 150, 148), (216, 196, 150))):
    x = 660 + ci * 110; y = 300
    d.rectangle([x, y, x + 62, y + 16], fill=col, outline=(90, 70, 44), width=2)
    d.rectangle([x, y - 74, x + 62, y], fill=col, outline=(90, 70, 44), width=2)
    for lx in (x + 4, x + 50):
        d.line([(lx, y + 16), (lx, y + 62)], fill=col, width=6)
    if ci == 0:  # one leg shorter
        d.line([(x + 50, y + 16), (x + 50, y + 40)], fill=col, width=6)
    if ci == 2:
        d.line([(x + 12, y + 6), (x + 48, y + 6)], fill=(120, 110, 90), width=2)
# cell 3: matchstick bundle, curled veneer, folded sandpaper
for k in range(7):
    d.line([(1090 + k * 16, 380), (1090 + k * 16, 220)], fill=(222, 196, 140), width=7)
    d.ellipse([1084 + k * 16, 206, 1098 + k * 16, 224], fill=(196, 90, 70))
d.line([(1080, 300), (1210, 300)], fill=(150, 60, 50), width=5)
d.arc([1260, 220, 1420, 360], 200, 520, fill=(206, 172, 110), width=14)
d.rectangle([1290, 380, 1400, 440], fill=(168, 130, 96), outline=(110, 84, 56), width=2)
# rear tools: tweezers, capped knife, rule (abstract lines), magnifier
d.line([(180, 560), (330, 640)], fill=(180, 182, 184), width=5); d.line([(180, 590), (330, 640)], fill=(180, 182, 184), width=5)
d.rectangle([640, 560, 830, 592], fill=(36, 36, 40)); d.rectangle([830, 560, 880, 592], fill=(150, 60, 50))
for tx in range(1080, 1440, 36):
    d.line([(tx, 560), (tx, 576)], fill=(120, 110, 90), width=2)
d.rectangle([1060, 556, 1460, 580], outline=(120, 110, 90), width=3)
d.ellipse([700, 610, 880, 760], outline=(190, 192, 194), width=7); d.line([(860, 730), (940, 786)], fill=(110, 84, 48), width=9)
# curled shaving bridging two compartments, the one untidy thing
d.arc([520, 420, 760, 540], 180, 420, fill=(232, 204, 140), width=12)
d.arc([560, 436, 720, 524], 180, 420, fill=(206, 172, 110), width=6)
for _ in range(260):  # wood dust film in gold
    x, y = random.randint(120, 1480), random.randint(120, 790)
    d.ellipse([x, y, x + 3, y + 2], fill=(212, 178, 100, 120))
img = img.filter(ImageFilter.GaussianBlur(0.5))
rng = np.random.default_rng(3); a = np.asarray(img).astype(np.int16); n = rng.normal(0, 4, a.shape[:2])[..., None]
img = Image.fromarray(np.clip(a + n, 0, 255).astype(np.uint8))
out = "intro-banner.png" if v == "ship" else f"scratch/intro-{v}.png"
img.save(out); print(out)
