#!/usr/bin/env python3
"""Create transparent overlay PNG for Thriller redesign (480×856)."""
from PIL import Image, ImageDraw, ImageFont
import math, os

W, H = 480, 856
AMBER = (245, 168, 0, 255)
DARK_BG = (14, 14, 14, 240)
RED_BADGE = (180, 20, 20, 255)
WHITE = (255, 255, 255, 255)
GRAY = (170, 165, 158, 255)

INTER_BOLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
INTER_REG  = "/usr/share/fonts/opentype/inter/Inter-Regular.otf"
DEJAVU     = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
DEJAVU_B   = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.truetype(DEJAVU, size)

out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
draw = ImageDraw.Draw(out)

# ── Top gradient (logo readability, top 180px) ───────────────────────────────
for y in range(180):
    alpha = int(180 * (1 - y / 180) ** 1.4)
    draw.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))

# ── Bottom card gradient (bottom 240px) ───────────────────────────────────────
for y in range(240):
    fy = H - 240 + y          # 616 to 855
    t  = y / 240              # 0 → top of gradient, 1 → bottom
    alpha = int(230 * t ** 0.6)
    draw.line([(0, fy), (W, fy)], fill=(0, 0, 0, alpha))

# ── Vignette (corners) ────────────────────────────────────────────────────────
cx, cy = W / 2, H / 2
max_d  = math.hypot(cx, cy)
for y in range(H):
    for x in range(W):
        d = math.hypot(x - cx, y - cy) / max_d
        if d > 0.65:
            a = int(90 * ((d - 0.65) / 0.35) ** 2)
            px = out.getpixel((x, y))
            new_a = min(255, px[3] + a)
            out.putpixel((x, y), (0, 0, 0, new_a))

# ── Logo (top-left) ────────────────────────────────────────────────────────────
LW, LH = 148, 72
LX, LY = 20, 20

def rrect(draw, x0, y0, x1, y1, r, fill):
    draw.rectangle([x0+r, y0, x1-r, y1], fill=fill)
    draw.rectangle([x0, y0+r, x1, y1-r], fill=fill)
    for cx2, cy2 in [(x0, y0), (x1-2*r, y0), (x0, y1-2*r), (x1-2*r, y1-2*r)]:
        draw.ellipse([cx2, cy2, cx2+2*r, cy2+2*r], fill=fill)

rrect(draw, LX, LY, LX+LW, LY+LH, 10, DARK_BG)

# Amber left accent strip
rrect(draw, LX+6, LY+6, LX+30, LY+LH-6, 7, AMBER)

# VHS cassette icon on amber strip (miniature)
ic = (LX+8, LY+16)
draw.rectangle([ic[0], ic[1], ic[0]+18, ic[1]+14], fill=(14, 14, 14, 240))
draw.ellipse([ic[0]+1, ic[1]+1, ic[0]+7, ic[1]+7], fill=AMBER)
draw.ellipse([ic[0]+11, ic[1]+1, ic[0]+17, ic[1]+7], fill=AMBER)
draw.rectangle([ic[0]+3, ic[1]+10, ic[0]+15, ic[1]+12], fill=AMBER)

# "RP" bold amber
f_rp = load_font(INTER_BOLD, 32)
draw.text((LX+36, LY+8), "RP", font=f_rp, fill=AMBER)

# Hebrew channel name
f_he = load_font(DEJAVU, 13)
draw.text((LX+36, LY+46), "חזרה לעבר", font=f_he, fill=(210, 205, 190, 220))

# ── Bottom info card ───────────────────────────────────────────────────────────
# Artist name  "MICHAEL JACKSON"
f_artist = load_font(INTER_BOLD, 44)
f_title  = load_font(INTER_REG, 28)
f_badge  = load_font(INTER_BOLD, 20)
f_label  = load_font(INTER_BOLD, 11)

# Thin amber line separator
draw.line([(20, H-200), (160, H-200)], fill=(245, 168, 0, 180), width=2)

# LABEL
draw.text((20, H-213), "NOW PLAYING", font=f_label, fill=(245, 168, 0, 200))

# Artist
draw.text((20, H-186), "MICHAEL JACKSON", font=f_artist, fill=WHITE)

# Song title italic (using oblique DejaVu)
f_title_it = load_font("/usr/share/fonts/truetype/freefont/FreeSansOblique.ttf", 28)
draw.text((20, H-136), "Thriller", font=f_title_it, fill=(210, 205, 190, 230))

# Year badge
YBX, YBY = 20, H - 92
year_txt = "1982"
bbox = draw.textbbox((0, 0), year_txt, font=f_badge)
bw, bh = bbox[2] - bbox[0] + 20, bbox[3] - bbox[1] + 10
rrect(draw, YBX, YBY, YBX+bw, YBY+bh, 5, RED_BADGE)
draw.text((YBX+10, YBY+4), year_txt, font=f_badge, fill=WHITE)

# Genre label
f_genre = load_font(INTER_REG, 15)
draw.text((YBX + bw + 14, YBY + 6), "Pop / Funk", font=f_genre, fill=(160, 155, 148, 200))

out_path = "/home/user/bi/temp/overlay_thriller.png"
out.save(out_path)
print(f"Saved: {out_path}  ({W}×{H})")
