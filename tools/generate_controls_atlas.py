#!/usr/bin/env python3
"""
generate_controls_atlas.py
Generates 4K modern horror controls atlas for Ultimate Mortal Kombat 3 Android.
Features:
- Minimalist circular joystick with crisp anti-aliased border & glowing crimson edge
- Solid vibrant red knob ("pelotica" de un solo color rojo sólido, sin relieves viejos)
- Modern horror action buttons: dark obsidian smoky glass, color-accented rings,
  stylized bold combat icons (fist, kick, shield, sprint, flaming skull)
- Pressed states with bright feedback
"""

import os
import sys
import math
from PIL import Image, ImageDraw, ImageFilter

WIDTH = 2048
HEIGHT = 1024
COLS = 8
ROWS = 4
CELL_W = WIDTH // COLS   # 256
CELL_H = HEIGHT // ROWS  # 256

atlas = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))

# Load vector icons
icons = {}
script_dir = os.path.dirname(os.path.abspath(__file__))
icons_dir = os.path.join(script_dir, 'icons')

for name in ['punch', 'kick', 'block', 'run', 'special']:
    p = os.path.join(icons_dir, f'icon_{name}.png')
    if os.path.exists(p):
        im = Image.open(p).convert('RGBA')
    else:
        # Fallback if icon file missing
        im = Image.new('RGBA', (256, 256), (255, 255, 255, 255))
    icons[name] = im

def draw_aa_disc(draw_img, cx, cy, r, color):
    s = 2
    temp = Image.new('RGBA', (r*2*s + 8, r*2*s + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(temp)
    d.ellipse([4, 4, 4 + r*2*s, 4 + r*2*s], fill=color)
    res = temp.resize((r*2 + 4, r*2 + 4), Image.Resampling.LANCZOS)
    draw_img.paste(res, (int(cx - r - 2), int(cy - r - 2)), res)

def draw_aa_ring(draw_img, cx, cy, r, stroke_w, color):
    s = 2
    temp = Image.new('RGBA', (int((r + stroke_w)*2*s + 8), int((r + stroke_w)*2*s + 8)), (0, 0, 0, 0))
    d = ImageDraw.Draw(temp)
    box = [4, 4, 4 + (r*2 + stroke_w)*s, 4 + (r*2 + stroke_w)*s]
    d.ellipse(box, outline=color, width=int(stroke_w * s))
    res = temp.resize((int(r*2 + stroke_w + 4), int(r*2 + stroke_w + 4)), Image.Resampling.LANCZOS)
    draw_img.paste(res, (int(cx - r - stroke_w*0.5 - 2), int(cy - r - stroke_w*0.5 - 2)), res)

# 1. Action buttons
btn_specs = [
    # (col, row, icon_key, color_theme, is_pressed)
    # Row 0: LK, LP, HK, HP
    (0, 0, 'kick',    (0, 200, 255), True),
    (1, 0, 'kick',    (0, 200, 255), False),
    (2, 0, 'punch',   (255, 50, 50), True),
    (3, 0, 'punch',   (255, 50, 50), False),
    (4, 0, 'kick',    (0, 200, 255), True),
    (5, 0, 'kick',    (0, 200, 255), False),
    (6, 0, 'punch',   (255, 50, 50), True),
    (7, 0, 'punch',   (255, 50, 50), False),

    # Row 1: K, P, B, R
    (0, 1, 'kick',    (0, 200, 255), True),
    (1, 1, 'kick',    (0, 200, 255), False),
    (2, 1, 'punch',   (255, 50, 50), True),
    (3, 1, 'punch',   (255, 50, 50), False),
    (4, 1, 'block',   (220, 225, 235), True),
    (5, 1, 'block',   (220, 225, 235), False),
    (6, 1, 'run',     (255, 200, 30), True),
    (7, 1, 'run',     (255, 200, 30), False),

    # Row 2: Special (Cols 0, 1)
    (0, 2, 'special', (40, 240, 170), True),
    (1, 2, 'special', (40, 240, 170), False),
]

btn_r = 106
for col, row, key, theme_col, pressed in btn_specs:
    cx = col * CELL_W + CELL_W // 2
    cy = row * CELL_H + CELL_H // 2

    if pressed:
        # Pressed: radiant glowing colored disc
        glow_col = (theme_col[0], theme_col[1], theme_col[2], 170)
        draw_aa_disc(atlas, cx, cy, btn_r, glow_col)
        draw_aa_ring(atlas, cx, cy, btn_r, 4.0, (255, 255, 255, 255))
    else:
        # Released: dark translucent sleek obsidian disc
        dark_col = (16, 16, 20, 205)
        draw_aa_disc(atlas, cx, cy, btn_r, dark_col)
        ring_col = (theme_col[0], theme_col[1], theme_col[2], 225)
        draw_aa_ring(atlas, cx, cy, btn_r, 3.0, ring_col)

    # Icon symbol
    icon_src = icons[key]
    target_sz = 142
    icon_resized = icon_src.resize((target_sz, target_sz), Image.Resampling.LANCZOS)
    
    icon_colored = Image.new('RGBA', (target_sz, target_sz), (0, 0, 0, 0))
    ic_col = (255, 255, 255) if pressed else (min(255, theme_col[0] + 40), min(255, theme_col[1] + 40), min(255, theme_col[2] + 40))
    for iy in range(target_sz):
        for ix in range(target_sz):
            pix = icon_resized.getpixel((ix, iy))
            if pix[3] > 0:
                icon_colored.putpixel((ix, iy), (ic_col[0], ic_col[1], ic_col[2], pix[3]))

    ix = cx - target_sz // 2
    iy = cy - target_sz // 2
    atlas.paste(icon_colored, (ix, iy), icon_colored)

# 2. Joystick Knob ('pelotica', Col 2, Row 2: 256x256)
knob_cx = 2 * CELL_W + CELL_W // 2
knob_cy = 2 * CELL_H + CELL_H // 2
knob_r = 96
# Solid vibrant arcade red circle: NO SHADING, NO DETAILS, 100% CLEAN
draw_aa_disc(atlas, knob_cx, knob_cy, knob_r, (235, 30, 30, 255))

# 3. Joystick Base ('un borde y ya', Cols 3 & 4, Rows 2 & 3: 512x512)
joy_cx = 3 * CELL_W + CELL_W
joy_cy = 2 * CELL_H + CELL_H
joy_r = 232
# Clean, crisp minimalist circle ring outline (crimson edge)
draw_aa_ring(atlas, joy_cx, joy_cy, joy_r, 4.5, (255, 60, 60, 235))

out_paths = sys.argv[1:] if len(sys.argv) > 1 else ['res/Textures/BUTTONS_TPAGE.PNG', 'res/Textures/BUTTONS_TPAGE_IPAD.PNG']
for out_p in out_paths:
    os.makedirs(os.path.dirname(out_p), exist_ok=True)
    atlas.save(out_p, 'PNG')

print('4K Controls Atlas saved successfully!')
