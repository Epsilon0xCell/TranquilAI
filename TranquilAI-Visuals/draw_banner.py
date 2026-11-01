#!/usr/bin/env python3
"""TranquilAI wordmark banner: night workbench under one shaded lamp, drawer pulled fully
out in a compartment grid, stair parts, finished chair, stacked window frames, glue saucer
with a cocktail stick, shavings heap, giant fingertips with tweezers at the top corners,
blurred dollhouse shelves behind, TranquilAI burned into the bench edge in Aoboshi One."""
import sys, os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
random.seed(23)
v = sys.argv[1] if len(sys.argv) > 1 else "ship"
os.chdir(os.path.dirname(os.path.abspath(__file__)))
W, H = 1600, 560
img = Image.new("RGB", (W, H), (22, 16, 12)); d = ImageDraw.Draw(img, "RGBA")
# blurred dollhouse shelves behind
bg = Image.new("RGBA", (W, H), (0, 0, 0, 0)); bd = ImageDraw.Draw(bg)
for sx in (180, 560, 940, 1280):
    bd.rectangle([sx, 40, sx + 240, 190], outline=(150, 120, 84), width=6)
    bd.rectangle([sx + 30, 70, sx + 100, 130], outline=(200, 190, 170), width=3)
    bd.polygon([(sx + 150, 130), (sx + 190, 84), (sx + 230, 130)], outline=(178, 120, 122), width=3)
img = Image.alpha_composite(img.convert("RGBA"), bg.filter(ImageFilter.GaussianBlur(5))).convert("RGB"); d = ImageDraw.Draw(img, "RGBA")
d.ellipse([480, 10, 1120, 430], fill=(58, 44, 28))  # lamp pool
d.polygon([(720, 0), (880, 0), (920, 60), (680, 60)], fill=(238, 232, 218))  # lamp shade
# drawer grid on bench
d.rectangle([220, 150, 1380, 440], fill=(92, 62, 38), outline=(56, 38, 22), width=8)
for i, x0 in enumerate((220, 600, 990)):
    x1 = (600, 990, 1380)[i]
    d.rectangle([x0 + 12, 162, x1 - 12, 428], fill=(178, 120, 122) if i == 0 else (238, 232, 218) if i == 1 else (206, 188, 168))
for k in range(4):  # stair parts sorted by length
    d.rectangle([260 + k * 10, 360 - k * 44, 420 + k * 10, 380 - k * 44], fill=(196, 158, 84), outline=(110, 84, 48), width=2)
d.rectangle([680, 250, 740, 264], fill=(122, 84, 52)); d.rectangle([680, 196, 740, 250], fill=(122, 84, 52))
for k in range(4):  # window frames stacked like cards
    d.rectangle([1060 + k * 14, 200 + k * 12, 1180 + k * 14, 300 + k * 12], outline=(140, 110, 70), width=5)
d.ellipse([1230, 330, 1340, 372], fill=(245, 242, 235), outline=(170, 160, 140), width=2)  # glue saucer
d.line([(1240, 344), (1332, 330)], fill=(150, 118, 66), width=5)
for _ in range(26):  # shavings heap
    x, y = random.randint(820, 960), random.randint(350, 415)
    d.arc([x, y, x + 44, y + 20], 180, 420, fill=(232, 204, 140), width=3)
# giant fingertips with tweezers, top corners
for fx in (90, 1440):
    d.ellipse([fx, -70, fx + 130, 90], fill=(222, 178, 148), outline=(190, 148, 118), width=3)
    d.ellipse([fx + 34, 18, fx + 96, 62], fill=(238, 200, 172))
d.line([(1090, 60), (980, 190)], fill=(185, 187, 189), width=6); d.line([(1130, 60), (1002, 190)], fill=(185, 187, 189), width=6)
d.rectangle([972, 186, 986, 226], fill=(150, 118, 66))  # banister spindle gripped
# bench edge brand
d.rectangle([0, 470, W, 560], fill=(120, 88, 54))
try:
    f = ImageFont.truetype("fonts/AoboshiOne.ttf", 52)
except Exception:
    f = ImageFont.load_default()
bb = d.textbbox((0, 0), "TranquilAI", font=f)
d.text(((W - (bb[2] - bb[0])) / 2, 486), "TranquilAI", font=f, fill=(52, 34, 20))
out = "banner.png" if v == "ship" else f"scratch/banner-{v}.png"
img.save(out); print(out)
