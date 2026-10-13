#!/usr/bin/env python3
"""
generate_controls_atlas.py
Generates ultra-crisp (2048x1024) 4K modern horror controls atlas for Ultimate Mortal Kombat 3 Android.
Features:
- OpenMW-style minimalist modern circular joystick with razor-sharp anti-aliased border & glowing crimson edge
- 3D dark-metallic ruby thumbstick knob ("pelotica") with sleek concave thumb grip
- Modern horror action buttons: dark obsidian smoky glass, sinister blood-red bevels,
  stylized bold combat icons (fist, boot, gothic shield, sprinting ninja, flaming skull)
- Pressed states with fiery infernal ignition and bright luminous feedback
"""

import math
import struct
import zlib
import os
import sys

WIDTH = 2048
HEIGHT = 1024
COLS = 8
ROWS = 4
CELL_W = WIDTH // COLS   # 256
CELL_H = HEIGHT // ROWS  # 256

# 32-bit RGBA buffer
pixels = bytearray(WIDTH * HEIGHT * 4)

def set_pixel(x, y, r, g, b, a):
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        idx = (y * WIDTH + x) * 4
        sa = a / 255.0
        if sa <= 0:
            return
        da = pixels[idx + 3] / 255.0
        out_a = sa + da * (1.0 - sa)
        if out_a > 0:
            out_r = (r * sa + pixels[idx] * da * (1.0 - sa)) / out_a
            out_g = (g * sa + pixels[idx + 1] * da * (1.0 - sa)) / out_a
            out_b = (b * sa + pixels[idx + 2] * da * (1.0 - sa)) / out_a
            pixels[idx]     = int(min(255, max(0, out_r)))
            pixels[idx + 1] = int(min(255, max(0, out_g)))
            pixels[idx + 2] = int(min(255, max(0, out_b)))
            pixels[idx + 3] = int(min(255, max(0, out_a * 255.0)))

def draw_aa_circle(cx, cy, radius, r, g, b, a, fill=True, stroke_width=2.0):
    min_x = max(0, int(cx - radius - stroke_width - 2))
    max_x = min(WIDTH - 1, int(cx + radius + stroke_width + 2))
    min_y = max(0, int(cy - radius - stroke_width - 2))
    max_y = min(HEIGHT - 1, int(cy + radius + stroke_width + 2))

    for y in range(min_y, max_y + 1):
        dy = y - cy
        for x in range(min_x, max_x + 1):
            dx = x - cx
            dist = math.hypot(dx, dy)
            if fill:
                delta = dist - radius
                if delta <= -0.5:
                    alpha = a
                elif delta < 0.5:
                    alpha = int(a * (0.5 - delta))
                else:
                    continue
                set_pixel(x, y, r, g, b, alpha)
            else:
                half_w = stroke_width * 0.5
                delta = abs(dist - radius) - half_w
                if delta <= -0.5:
                    alpha = a
                elif delta < 0.5:
                    alpha = int(a * (0.5 - delta))
                else:
                    continue
                set_pixel(x, y, r, g, b, alpha)

def draw_polygon_filled(points, r, g, b, a):
    if len(points) < 3:
        return
    min_x = max(0, int(min(p[0] for p in points)) - 1)
    max_x = min(WIDTH - 1, int(max(p[0] for p in points)) + 1)
    min_y = max(0, int(min(p[1] for p in points)) - 1)
    max_y = min(HEIGHT - 1, int(max(p[1] for p in points)) + 1)

    n = len(points)
    for y in range(min_y, max_y + 1):
        py = y + 0.5
        nodes = []
        for i in range(n):
            j = (i + 1) % n
            y1, y2 = points[i][1], points[j][1]
            x1, x2 = points[i][0], points[j][0]
            if (y1 < py <= y2) or (y2 < py <= y1):
                nodes.append(x1 + (py - y1) / (y2 - y1) * (x2 - x1))
        nodes.sort()
        for i in range(0, len(nodes) - 1, 2):
            x_start = int(nodes[i])
            x_end = int(nodes[i + 1])
            for x in range(x_start, x_end + 1):
                set_pixel(x, y, r, g, b, a)

def draw_thick_line(x1, y1, x2, y2, thickness, r, g, b, a):
    dx = x2 - x1
    dy = y2 - y1
    dist = math.hypot(dx, dy)
    if dist < 0.001:
        return
    nx = -dy / dist * (thickness * 0.5)
    ny = dx / dist * (thickness * 0.5)
    poly = [
        (x1 + nx, y1 + ny),
        (x2 + nx, y2 + ny),
        (x2 - nx, y2 - ny),
        (x1 - nx, y1 - ny)
    ]
    draw_polygon_filled(poly, r, g, b, a)

# -------------------------------------------------------------
# Joystick Rendering (OpenMW / 4K Modern Minimalist Style)
# -------------------------------------------------------------

def render_joystick_base(origin_x, origin_y, size):
    """
    Renders OpenMW-style minimalist joystick base:
    - Elegant, crisp circular border line
    - Highly translucent dark glass interior (non-obstructive)
    - Blood-crimson / silver neon edge glow
    - Minimalist cardinal notches
    """
    cx = origin_x + size * 0.5
    cy = origin_y + size * 0.5
    outer_r = size * 0.44  # ~225 px
    ring_thick = 4.5

    for y in range(int(cy - outer_r - 20), int(cy + outer_r + 20)):
        dy = y - cy
        for x in range(int(cx - outer_r - 20), int(cx + outer_r + 20)):
            dx = x - cx
            dist = math.hypot(dx, dy)

            # 1. Subtle crimson / horror outer glow
            if outer_r < dist <= outer_r + 16:
                glow_factor = (1.0 - (dist - outer_r) / 16.0) ** 2.0
                set_pixel(x, y, 230, 30, 40, int(120 * glow_factor))

            # 2. Razor-sharp circular border line ("línea de borde")
            ring_delta = abs(dist - outer_r) - ring_thick * 0.5
            if ring_delta < 0.5:
                cov = 1.0 if ring_delta <= -0.5 else (0.5 - ring_delta)
                norm_y = dy / outer_r
                r_val = int(245 + 10 * norm_y)
                g_val = int(80 + 40 * norm_y)
                b_val = int(90 + 40 * norm_y)
                set_pixel(x, y, r_val, g_val, b_val, int(250 * cov))

            # 3. Translucent dark smoky glass interior (OpenMW style: see-through)
            elif dist < outer_r - ring_thick * 0.5:
                ratio = dist / outer_r
                disc_a = int(18 + 40 * (ratio ** 2.0))
                disc_r = int(22 + 30 * ratio)
                disc_g = int(14 + 10 * ratio)
                disc_b = int(20 + 15 * ratio)
                set_pixel(x, y, disc_r, disc_g, disc_b, disc_a)

    # 4. Minimalist cardinal tick notches (N, S, E, W)
    tick_len = 15.0
    for angle in [0, math.pi * 0.5, math.pi, math.pi * 1.5]:
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        for t in range(int(outer_r - tick_len), int(outer_r + 6)):
            tx = cx + cos_a * t
            ty = cy + sin_a * t
            for w in (-1.0, 0.0, 1.0):
                px = int(round(tx - sin_a * w))
                py = int(round(ty + cos_a * w))
                set_pixel(px, py, 255, 70, 85, 230)

    # 5. Concentric subtle inner guide ring
    draw_aa_circle(cx, cy, outer_r * 0.42, 190, 45, 55, 45, fill=False, stroke_width=1.5)

def render_joystick_knob(origin_x, origin_y, size):
    """
    Renders 3D dark-chrome ruby thumbstick knob ("pelotica"):
    - Spherical shading with Blinn-Phong specular highlight
    - Concave ergonomic thumb depression
    - Modern minimalist high-DPI finish
    """
    cx = origin_x + size * 0.5
    cy = origin_y + size * 0.5
    radius = size * 0.38  # ~97 px

    # Light vector from top-left
    lx, ly, lz = -0.45, -0.55, 0.70
    llen = math.hypot(lx, ly, lz)
    lx, ly, lz = lx / llen, ly / llen, lz / llen

    for y in range(int(cy - radius - 8), int(cy + radius + 8)):
        dy = y - cy
        for x in range(int(cx - radius - 8), int(cx + radius + 8)):
            dx = x - cx
            dist = math.hypot(dx, dy)

            # Drop shadow
            if radius < dist <= radius + 12:
                shadow_a = int(160 * ((1.0 - (dist - radius) / 12.0) ** 1.6))
                set_pixel(x, y, 0, 0, 0, shadow_a)
                continue

            if dist > radius:
                continue

            # Sphere normal
            nz = math.sqrt(max(0.0, 1.0 - (dist / radius) ** 2))
            nx = dx / radius
            ny = dy / radius

            # Diffuse lighting
            diff = max(0.0, nx * lx + ny * ly + nz * lz)
            # Specular highlight
            hx, hy, hz = lx, ly, lz + 1.0
            hlen = math.hypot(hx, hy, hz)
            hx, hy, hz = hx / hlen, hy / hlen, hz / hlen
            spec = max(0.0, nx * hx + ny * hy + nz * hz) ** 28.0

            # Fresnel rim
            fresnel = (1.0 - nz) ** 2.2

            # Dark metallic ruby base
            base_r = 150 * diff + 55 + fresnel * 95
            base_g = 20 * diff + 12 + fresnel * 25
            base_b = 30 * diff + 18 + fresnel * 35

            # Specular shine
            final_r = min(255, int(base_r + 230 * spec))
            final_g = min(255, int(base_g + 210 * spec))
            final_b = min(255, int(base_b + 210 * spec))

            # Concave thumb grip ring
            grip_r = radius * 0.54
            grip_dist = abs(dist - grip_r)
            if grip_dist < 4.5:
                gf = 1.0 - grip_dist / 4.5
                final_r = int(final_r * (1.0 - 0.45 * gf))
                final_g = int(final_g * (1.0 - 0.45 * gf))
                final_b = int(final_b * (1.0 - 0.45 * gf))

            # Edge anti-aliasing
            edge_delta = radius - dist
            alpha = 255 if edge_delta >= 1.0 else int(255 * edge_delta)

            set_pixel(x, y, final_r, final_g, final_b, alpha)

# -------------------------------------------------------------
# Action Button Base (Dark Horror Obsidian Bevels)
# -------------------------------------------------------------

def render_button_base(cx, cy, radius, theme_color, is_pressed):
    tr, tg, tb = theme_color
    outer_r = radius

    for y in range(int(cy - outer_r - 10), int(cy + outer_r + 10)):
        dy = y - cy
        for x in range(int(cx - outer_r - 10), int(cx + outer_r + 10)):
            dx = x - cx
            dist = math.hypot(dx, dy)

            # 1. Outer glow
            if is_pressed:
                if outer_r < dist <= outer_r + 14:
                    gf = (1.0 - (dist - outer_r) / 14.0) ** 1.4
                    set_pixel(x, y, min(255, tr + 80), min(255, tg + 60), min(255, tb + 60), int(190 * gf))
            else:
                if outer_r < dist <= outer_r + 8:
                    gf = (1.0 - (dist - outer_r) / 8.0)
                    set_pixel(x, y, tr, tg, tb, int(70 * gf))

            if dist > outer_r:
                continue

            edge_cov = 1.0 if (outer_r - dist) >= 1.0 else (outer_r - dist)

            # Beveled metallic / horror rim
            rim_w = 9.0
            if dist >= outer_r - rim_w:
                ang = math.atan2(dy, dx)
                light = math.cos(ang + 0.75 * math.pi) * 0.5 + 0.5
                if is_pressed:
                    rim_r = int(tr * 0.85 + 130 * light)
                    rim_g = int(tg * 0.85 + 110 * light)
                    rim_b = int(tb * 0.85 + 110 * light)
                    rim_a = int(250 * edge_cov)
                else:
                    rim_r = int(55 + 75 * light + tr * 0.4)
                    rim_g = int(48 + 60 * light + tg * 0.4)
                    rim_b = int(60 + 60 * light + tb * 0.4)
                    rim_a = int(240 * edge_cov)
                set_pixel(x, y, min(255, rim_r), min(255, rim_g), min(255, rim_b), rim_a)

            # Inner button body (Dark smoky obsidian glass)
            else:
                ratio = dist / (outer_r - rim_w)
                if is_pressed:
                    core_f = (1.0 - ratio) ** 1.2
                    br = min(255, int(tr * 0.8 + 190 * core_f))
                    bg = min(255, int(tg * 0.7 + 100 * core_f))
                    bb = min(255, int(tb * 0.7 + 100 * core_f))
                    ba = int(235 * edge_cov)
                else:
                    shade = ratio ** 1.6
                    br = int(22 + 32 * shade + tr * 0.16)
                    bg = int(18 + 24 * shade + tg * 0.16)
                    bb = int(26 + 30 * shade + tb * 0.16)
                    ba = int(175 + 45 * shade)
                set_pixel(x, y, br, bg, bb, ba)

# -------------------------------------------------------------
# High-End Stylized Martial Arts & Horror Icons (Large & Bold)
# -------------------------------------------------------------

def render_fist_icon(cx, cy, scale, angle_deg, color, is_pressed):
    """
    Renders an unmistakable martial arts clenched combat fist:
    - Arm / forearm coming from the left/bottom
    - Curved palm & knuckles
    - 4 clenched finger segments with deep ridges
    - Heavy folded thumb locking the fingers
    - Knuckle highlights & impact lines
    """
    r, g, b = color
    rad = math.radians(angle_deg)
    cos_a, sin_a = math.cos(rad), math.sin(rad)

    def rot(lx, ly):
        rx = lx * cos_a - ly * sin_a
        ry = lx * sin_a + ly * cos_a
        return (cx + rx * scale, cy + ry * scale)

    # 1. Arm / wrist block
    wrist = [rot(-44, 18), rot(-14, 17), rot(-14, -17), rot(-44, -15)]
    draw_polygon_filled(wrist, r, g, b, 245)

    # Wrist bandage / brace band
    draw_thick_line(rot(-28, 18)[0], rot(-28, 18)[1], rot(-28, -17)[0], rot(-28, -17)[1], 5.0 * scale,
                    min(255, r + 55), min(255, g + 55), min(255, b + 55), 255)

    # 2. Main hand / fist mass
    palm = [rot(-16, 22), rot(20, 24), rot(30, 14), rot(30, -18), rot(-16, -20)]
    draw_polygon_filled(palm, r, g, b, 255)

    # 3. Four clenched fingers (curled knuckles)
    knuckle_data = [
        (-14, 20, 16, 21, 30, 18),   # Index
        (-10, 9,  22, 9,  34, 7),    # Middle (longest)
        (-10, -4, 20, -4, 32, -5),   # Ring
        (-12, -15,16, -15,28, -15),  # Pinky
    ]
    for x0, y0, x1, y1, x2, y2 in knuckle_data:
        p1 = rot(x0, y0)
        p2 = rot(x1, y1)
        p3 = rot(x2, y2)
        draw_thick_line(p1[0], p1[1], p2[0], p2[1], 8.0 * scale, r, g, b, 255)
        draw_thick_line(p2[0], p2[1], p3[0], p3[1], 7.5 * scale, r, g, b, 255)
        draw_aa_circle(p3[0], p3[1], 4.8 * scale, min(255, r + 60), min(255, g + 60), min(255, b + 60), 255)

    # 4. Folded thumb firmly clamping across the front
    thumb_base = [rot(-6, 20), rot(18, 18), rot(20, 2), rot(2, 4)]
    draw_polygon_filled(thumb_base, min(255, r + 45), min(255, g + 45), min(255, b + 45), 255)
    t_cap = rot(20, 2)
    draw_aa_circle(t_cap[0], t_cap[1], 5.0 * scale, min(255, r + 65), min(255, g + 65), min(255, b + 65), 255)

    # 5. Dynamic impact shockwave arcs
    if is_pressed:
        for offset in (44, 52, 60):
            p_top = rot(offset, -20)
            p_mid = rot(offset + 9, 0)
            p_bot = rot(offset, 20)
            draw_thick_line(p_top[0], p_top[1], p_mid[0], p_mid[1], 4.0 * scale, 255, 235, 190, 240)
            draw_thick_line(p_mid[0], p_mid[1], p_bot[0], p_bot[1], 4.0 * scale, 255, 235, 190, 240)

def render_boot_kick_icon(cx, cy, scale, angle_deg, color, is_pressed):
    """
    Renders an unmistakable martial arts kicking boot / leg:
    - Slanted muscular calf & shin
    - Ankle support & combat boot tongue
    - Reinforced heel, heavy tread sole with grip ridges
    - Pointed steel toe kicking forward
    - Dynamic impact swoosh
    """
    r, g, b = color
    rad = math.radians(angle_deg)
    cos_a, sin_a = math.cos(rad), math.sin(rad)

    def rot(lx, ly):
        rx = lx * cos_a - ly * sin_a
        ry = lx * sin_a + ly * cos_a
        return (cx + rx * scale, cy + ry * scale)

    # 1. Muscular calf & shin (leg descending into boot)
    shin = [
        rot(-38, 28), rot(-8, 20), rot(-12, -4), rot(-40, 4)
    ]
    draw_polygon_filled(shin, r, g, b, 240)

    # Shin guard plate line
    s_top = rot(-36, 24)
    s_bot = rot(-14, 16)
    draw_thick_line(s_top[0], s_top[1], s_bot[0], s_bot[1], 4.0 * scale,
                    min(255, r + 65), min(255, g + 65), min(255, b + 65), 255)

    # 2. Combat boot ankle & upper foot
    boot_upper = [
        rot(-10, 20),  # top instep
        rot(20, 18),   # instep curve
        rot(40, 10),   # toe curve
        rot(46, -2),   # toe tip
        rot(44, -13),  # toe sole corner
        rot(6, -15),   # arch
        rot(-12, -15), # heel corner
        rot(-16, -2)   # Achilles tendon
    ]
    draw_polygon_filled(boot_upper, r, g, b, 255)

    # 3. Reinforced heavy sole with grip tread
    sole_poly = [
        rot(-14, -15), rot(46, -13), rot(46, -21), rot(-14, -23)
    ]
    draw_polygon_filled(sole_poly, min(255, r + 55), min(255, g + 55), min(255, b + 55), 255)

    # Tread teeth
    for tx in (-6, 6, 18, 30):
        t1 = rot(tx, -21)
        t2 = rot(tx + 4, -25)
        draw_thick_line(t1[0], t1[1], t2[0], t2[1], 3.0 * scale,
                        min(255, r + 85), min(255, g + 85), min(255, b + 85), 255)

    # 4. Steel toe cap highlight
    draw_thick_line(rot(34, 12)[0], rot(34, 12)[1], rot(46, -2)[0], rot(46, -2)[1], 4.5 * scale,
                    min(255, r + 75), min(255, g + 75), min(255, b + 75), 255)

    # 5. Dynamic kick impact swoosh
    arc1 = rot(50, 18)
    arc2 = rot(58, 0)
    arc3 = rot(50, -18)
    draw_thick_line(arc1[0], arc1[1], arc2[0], arc2[1], 4.0 * scale, 255, 235, 170, 235)
    draw_thick_line(arc2[0], arc2[1], arc3[0], arc3[1], 4.0 * scale, 255, 235, 170, 235)

def render_gothic_shield_icon(cx, cy, scale, color, is_pressed):
    """
    Renders an imposing gothic spiked battle shield (Block icon).
    """
    r, g, b = color

    outer_pts = [
        (cx - 40 * scale, cy - 38 * scale),  # Top-left wing
        (cx, cy - 44 * scale),               # Top center peak
        (cx + 40 * scale, cy - 38 * scale),  # Top-right wing
        (cx + 38 * scale, cy + 10 * scale),  # Right flank
        (cx, cy + 48 * scale),               # Bottom spike tip
        (cx - 38 * scale, cy + 10 * scale)   # Left flank
    ]
    draw_polygon_filled(outer_pts, r, g, b, 245)

    inner_pts = [
        (cx - 28 * scale, cy - 30 * scale),
        (cx, cy - 34 * scale),
        (cx + 28 * scale, cy - 30 * scale),
        (cx + 26 * scale, cy + 6 * scale),
        (cx, cy + 34 * scale),
        (cx - 28 * scale, cy + 6 * scale)
    ]
    draw_polygon_filled(inner_pts, min(255, r + 50), min(255, g + 50), min(255, b + 50), 255)

    # Reinforced steel cross
    draw_thick_line(cx, cy - 28 * scale, cx, cy + 24 * scale, 8.0 * scale, 255, 245, 230, 255)
    draw_thick_line(cx - 22 * scale, cy - 8 * scale, cx + 22 * scale, cy - 8 * scale, 8.0 * scale, 255, 245, 230, 255)

    # Spikes on top corners
    draw_thick_line(cx - 38 * scale, cy - 38 * scale, cx - 46 * scale, cy - 46 * scale, 4.0 * scale, 255, 240, 220, 255)
    draw_thick_line(cx + 38 * scale, cy - 38 * scale, cx + 46 * scale, cy - 46 * scale, 4.0 * scale, 255, 240, 220, 255)

def render_ninja_sprint_icon(cx, cy, scale, color, is_pressed):
    """
    Renders an athletic ninja sprinting forward at high speed (Run icon).
    """
    r, g, b = color

    # 1. Masked ninja head
    draw_aa_circle(cx + 14 * scale, cy - 28 * scale, 10.5 * scale, r, g, b, 255)
    draw_thick_line(cx + 6 * scale, cy - 28 * scale, cx - 24 * scale, cy - 34 * scale, 4.0 * scale,
                    min(255, r + 55), min(255, g + 55), min(255, b + 55), 245)

    # 2. Torso
    torso = [
        (cx + 10 * scale, cy - 20 * scale),
        (cx + 24 * scale, cy - 18 * scale),
        (cx + 8 * scale, cy + 8 * scale),
        (cx - 6 * scale, cy + 6 * scale)
    ]
    draw_polygon_filled(torso, r, g, b, 255)

    # 3. Front leg
    front_leg = [
        (cx + 6 * scale, cy + 8 * scale),
        (cx + 32 * scale, cy + 16 * scale),
        (cx + 28 * scale, cy + 40 * scale),
        (cx + 44 * scale, cy + 42 * scale),
        (cx + 42 * scale, cy + 46 * scale),
        (cx + 20 * scale, cy + 40 * scale),
        (cx + 22 * scale, cy + 18 * scale)
    ]
    draw_polygon_filled(front_leg, r, g, b, 255)

    # 4. Back leg
    back_leg = [
        (cx - 4 * scale, cy + 6 * scale),
        (cx - 26 * scale, cy - 2 * scale),
        (cx - 42 * scale, cy + 18 * scale),
        (cx - 48 * scale, cy + 14 * scale),
        (cx - 44 * scale, cy + 24 * scale),
        (cx - 24 * scale, cy + 8 * scale)
    ]
    draw_polygon_filled(back_leg, r, g, b, 255)

    # 5. Speed streaks
    streaks = [
        (cx - 18 * scale, cy - 24 * scale, cx - 48 * scale, cy - 24 * scale),
        (cx - 24 * scale, cy - 14 * scale, cx - 56 * scale, cy - 14 * scale),
        (cx - 28 * scale, cy - 4 * scale, cx - 54 * scale, cy - 4 * scale)
    ]
    for x1, y1, x2, y2 in streaks:
        draw_thick_line(x1, y1, x2, y2, 4.0 * scale, min(255, r + 65), min(255, g + 65), min(255, b + 65), 230)

def render_mk_flaming_skull_icon(cx, cy, scale, color, is_pressed):
    """
    Renders an ominous Mortal Kombat flaming skull (Special icon).
    """
    r, g, b = color

    # 1. Cranium
    draw_aa_circle(cx, cy - 8 * scale, 28.0 * scale, r, g, b, 255)

    # 2. Vicious curved cheekbones & jaw
    jaw = [
        (cx - 17 * scale, cy + 10 * scale),
        (cx + 17 * scale, cy + 10 * scale),
        (cx + 15 * scale, cy + 32 * scale),
        (cx - 15 * scale, cy + 32 * scale)
    ]
    draw_polygon_filled(jaw, r, g, b, 255)

    # 3. Menacing hollow eye sockets
    draw_aa_circle(cx - 11 * scale, cy - 4 * scale, 8.5 * scale, 15, 12, 18, 255)
    draw_aa_circle(cx + 11 * scale, cy - 4 * scale, 8.5 * scale, 15, 12, 18, 255)
    # Burning pupils
    draw_aa_circle(cx - 11 * scale, cy - 4 * scale, 4.0 * scale, 255, 95, 45, 255)
    draw_aa_circle(cx + 11 * scale, cy - 4 * scale, 4.0 * scale, 255, 95, 45, 255)

    # 4. Triangular nasal cavity
    nose = [
        (cx, cy + 4 * scale),
        (cx + 5 * scale, cy + 13 * scale),
        (cx - 5 * scale, cy + 13 * scale)
    ]
    draw_polygon_filled(nose, 18, 15, 22, 255)

    # 5. Jagged teeth
    for tx in (-9, -4, 0, 4, 9):
        draw_thick_line(cx + tx * scale, cy + 18 * scale, cx + tx * scale, cy + 30 * scale, 2.4 * scale,
                        25, 20, 28, 245)

    # 6. Hellfire plumes rising from the skull
    flames = [
        (cx - 18 * scale, cy - 32 * scale, cx - 28 * scale, cy - 52 * scale),
        (cx, cy - 36 * scale, cx, cy - 58 * scale),
        (cx + 18 * scale, cy - 32 * scale, cx + 28 * scale, cy - 52 * scale),
    ]
    for fx1, fy1, fx2, fy2 in flames:
        draw_thick_line(fx1, fy1, fx2, fy2, 5.0 * scale, 255, 155, 45, 245)

# -------------------------------------------------------------
# Main Generation
# -------------------------------------------------------------

def generate_atlas():
    print(f"Generating High-End 4K Controls Atlas ({WIDTH}x{HEIGHT})...")

    COLOR_PUNCH = (255, 60, 50)     # Infernal Crimson Punch
    COLOR_KICK  = (50, 190, 255)    # Arc Electric Cyan Kick
    COLOR_BLOCK = (185, 215, 235)   # Gothic Slate Silver Block
    COLOR_RUN   = (255, 215, 35)    # Lightning Gold Run
    COLOR_SPEC  = (80, 250, 150)    # Necrotic Flame Green Special

    btn_radius = 104.0

    cells_spec = [
        # Row 0: LK, LP, HK, HP
        (0, 0, 'kick',  -28, COLOR_KICK,  True,  'LK Pressed'),
        (1, 0, 'kick',  -28, COLOR_KICK,  False, 'LK Released'),
        (2, 0, 'punch', -22, COLOR_PUNCH, True,  'LP Pressed'),
        (3, 0, 'punch', -22, COLOR_PUNCH, False, 'LP Released'),
        (4, 0, 'kick',   42, COLOR_KICK,  True,  'HK Pressed'),
        (5, 0, 'kick',   42, COLOR_KICK,  False, 'HK Released'),
        (6, 0, 'punch',  32, COLOR_PUNCH, True,  'HP Pressed'),
        (7, 0, 'punch',  32, COLOR_PUNCH, False, 'HP Released'),

        # Row 1: K, P, B, R
        (0, 1, 'kick',   12, COLOR_KICK,  True,  'K Pressed'),
        (1, 1, 'kick',   12, COLOR_KICK,  False, 'K Released'),
        (2, 1, 'punch',   0, COLOR_PUNCH, True,  'P Pressed'),
        (3, 1, 'punch',   0, COLOR_PUNCH, False, 'P Released'),
        (4, 1, 'block',   0, COLOR_BLOCK, True,  'B Pressed'),
        (5, 1, 'block',   0, COLOR_BLOCK, False, 'B Released'),
        (6, 1, 'run',     0, COLOR_RUN,   True,  'R Pressed'),
        (7, 1, 'run',     0, COLOR_RUN,   False, 'R Released'),

        # Row 2: Special (Cols 0 & 1)
        (0, 2, 'special', 0, COLOR_SPEC,  True,  'S Pressed'),
        (1, 2, 'special', 0, COLOR_SPEC,  False, 'S Released'),
    ]

    for col, row, kind, ang, color, is_pressed, desc in cells_spec:
        cx = col * CELL_W + CELL_W // 2
        cy = row * CELL_H + CELL_H // 2

        # 1. Action button base
        render_button_base(cx, cy, btn_radius, color, is_pressed)

        # 2. Bold, large stylized icon
        scale = 1.32
        icon_color = (255, 255, 255) if is_pressed else color
        if kind == 'kick':
            render_boot_kick_icon(cx, cy, scale, ang, icon_color, is_pressed)
        elif kind == 'punch':
            render_fist_icon(cx, cy, scale, ang, icon_color, is_pressed)
        elif kind == 'block':
            render_gothic_shield_icon(cx, cy, scale, icon_color, is_pressed)
        elif kind == 'run':
            render_ninja_sprint_icon(cx, cy, scale, icon_color, is_pressed)
        elif kind == 'special':
            render_mk_flaming_skull_icon(cx, cy, scale, icon_color, is_pressed)

    # 3. Joystick Knob ("pelotica", Col 2, Row 2: 256x256)
    knob_origin_x = 2 * CELL_W
    knob_origin_y = 2 * CELL_H
    render_joystick_knob(knob_origin_x, knob_origin_y, CELL_W)

    # 4. Joystick Base (Col 3 & 4, Rows 2 & 3: 512x512)
    joy_origin_x = 3 * CELL_W
    joy_origin_y = 2 * CELL_H
    render_joystick_base(joy_origin_x, joy_origin_y, CELL_W * 2)

    print("Atlas rendering complete. Compressing to PNG...")

def save_png(filename):
    raw = bytearray()
    for y in range(HEIGHT):
        raw.append(0)
        raw.extend(pixels[y * WIDTH * 4 : (y + 1) * WIDTH * 4])
    compressed = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)

    ihdr = struct.pack('>IIBBBBB', WIDTH, HEIGHT, 8, 6, 0, 0, 0)
    png_bytes = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) + chunk(b'IDAT', compressed) + chunk(b'IEND', b'')

    with open(filename, 'wb') as f:
        f.write(png_bytes)
    print(f"Saved: {filename} ({len(png_bytes)} bytes)")

if __name__ == '__main__':
    generate_atlas()
    out_target = sys.argv[1] if len(sys.argv) > 1 else 'test_buttons_tpage.png'
    save_png(out_target)
