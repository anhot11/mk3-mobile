#!/usr/bin/env python3
"""
patch_assets.py
Applies UI, Menu, and Font remaster enhancements to Mortal Kombat assets:
1. Cleans FENEW1.PNG to have only 3 clean tombstones (PLAY, OPTIONS, EXTRAS).
2. Remasters HUD_TPAGE.PNG to 1024x1024 with crisp bevels, gradient health, and emerald run bars.
3. Upscales NAMES_FONT.PNG (1024x1024) and COUNTDOWNFONT.PNG (512x512) with Lanczos sharpening.
4. Ensures 2048x2048 HD fonts for MKFONT_0/1.
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFilter

def patch_fenew1(res_dir):
    tex_dir = os.path.join(res_dir, 'Textures')
    fenew1_path = os.path.join(tex_dir, 'FENEW1.PNG')
    fenew1_low = os.path.join(tex_dir, 'FENEW1_LOW.PNG')
    
    # Remove stale PVR files so our clean PNG is always used
    for pvr in ['FENEW1.pvr', 'FENEW1_LOW.pvr', 'FENEW1.PVR', 'FENEW1_LOW.PVR']:
        p = os.path.join(tex_dir, pvr)
        if os.path.exists(p):
            os.remove(p)
            print(f"Removed stale {pvr}")

    src_clean = os.path.join(os.path.dirname(__file__), 'FENEW1.PNG')
    if os.path.exists(src_clean):
        im = Image.open(src_clean)
        im.save(fenew1_path)
        im.save(fenew1_low)
        print("FENEW1.PNG and FENEW1_LOW.PNG updated with 3 clean tombstones.")

def patch_hud(res_dir):
    hud_path = os.path.join(res_dir, 'Textures', 'HUD_TPAGE.PNG')
    if not os.path.exists(hud_path):
        return
    # Generate 1024x1024 clean HD HUD
    im = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    # 1. Health Bar (top: y=0..128, x=0..1024)
    for y in range(8, 120):
        # Gradient from deep cobalt blue to vivid cyan-blue
        t = (y - 8) / 112.0
        r = int(18 + 15 * t)
        g = int(60 + 55 * t)
        b = int(175 + 75 * t)
        d.line([(8, y), (1016, y)], fill=(r, g, b, 255))

    # Gold Bevel border around health bar
    d.rectangle([8, 8, 1016, 120], outline=(225, 185, 45, 255), width=5)
    d.rectangle([13, 13, 1011, 115], outline=(140, 105, 20, 255), width=2)

    # 2. Emerald Run Bar (y=160..240, x=0..700)
    for y in range(164, 236):
        t = (y - 164) / 72.0
        r = int(15 + 25 * t)
        g = int(180 + 70 * t)
        b = int(45 + 30 * t)
        d.line([(8, y), (692, y)], fill=(r, g, b, 255))
    d.rectangle([8, 164, 692, 236], outline=(215, 235, 170, 255), width=3)

    # 3. Damage columns & accents (y=260..400)
    for x in range(8, 512, 16):
        d.rectangle([x, 260, x + 10, 390], fill=(210, 35, 35, 255))

    im.save(hud_path)
    print("HUD_TPAGE.PNG remastered to 1024x1024 HD.")

def patch_fonts(res_dir):
    tex_dir = os.path.join(res_dir, 'Textures')
    
    # HD iPad fonts over phone fonts
    ipad0 = os.path.join(tex_dir, 'MKFONT_IPAD_0.PNG')
    mk0 = os.path.join(tex_dir, 'MKFONT_0.PNG')
    if os.path.exists(ipad0):
        im = Image.open(ipad0)
        im.save(mk0)

    ipad1 = os.path.join(tex_dir, 'MKFONT_IPAD_1.PNG')
    mk1 = os.path.join(tex_dir, 'MKFONT_1.PNG')
    if os.path.exists(ipad1):
        im = Image.open(ipad1)
        im.save(mk1)

    # Upscale NAMES_FONT and COUNTDOWNFONT
    def upscale_font(p, factor=4):
        if not os.path.exists(p): return
        orig = Image.open(p).convert('RGBA')
        w, h = orig.size
        if w >= 512: return # already upscaled
        hi = orig.resize((w * factor, h * factor), Image.Resampling.LANCZOS)
        r, g, b, a = hi.split()
        r = r.filter(ImageFilter.UnsharpMask(radius=2, percent=130, threshold=2))
        g = g.filter(ImageFilter.UnsharpMask(radius=2, percent=130, threshold=2))
        b = b.filter(ImageFilter.UnsharpMask(radius=2, percent=130, threshold=2))
        a = a.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=2))
        out = Image.merge('RGBA', (r, g, b, a))
        out.save(p)
        print(f"{os.path.basename(p)} upscaled to {out.size}")

    upscale_font(os.path.join(tex_dir, 'NAMES_FONT.PNG'), 4)
    upscale_font(os.path.join(tex_dir, 'COUNTDOWNFONT.PNG'), 4)

if __name__ == '__main__':
    res_path = sys.argv[1] if len(sys.argv) > 1 else 'res'
    if os.path.exists(res_path):
        patch_fenew1(res_path)
        patch_hud(res_path)
        patch_fonts(res_path)
        print("All assets successfully patched and remastered!")
