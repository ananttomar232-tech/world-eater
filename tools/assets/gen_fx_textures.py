"""Particle sprites, Void Breath beam layers, the ornate boss bar and the Erosion icon.

    python3 tools/assets/gen_fx_textures.py
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from palette import GOLD, VIOLET, canvas, hx, value_noise  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSETS = os.path.join(ROOT, "src", "main", "resources", "assets", "aetherfall")


def save(img, rel):
    path = os.path.join(ASSETS, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    Image.fromarray(img.astype(np.uint8), "RGBA").save(path)


def particle_json(name, textures):
    path = os.path.join(ASSETS, "particles", name + ".json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump({"textures": [f"aetherfall:{t}" for t in textures]}, f, indent=2)
        f.write("\n")


def radial(size, fn):
    img = np.zeros((size, size, 4))
    c = (size - 1) / 2
    for y in range(size):
        for x in range(size):
            img[y, x] = fn((x - c) / (size / 2), (y - c) / (size / 2))
    return np.clip(img, 0, 255)


# ---------------------------------------------------------------------------------------------------------------------
# Particles (white/grey sprites are tinted in code; flame and shockwave carry their own colour)
# ---------------------------------------------------------------------------------------------------------------------

def spark(frame):
    reach = [1.0, 0.8, 0.6, 0.4][frame]

    def f(dx, dy):
        d = math.hypot(dx, dy)
        ray = min(abs(dx), abs(dy))
        core = max(0.0, 1 - d / (0.35 * reach + 0.12))
        arm = max(0.0, 1 - ray / 0.12) * max(0.0, 1 - d / reach)
        v = max(core, arm * 0.85)
        return (255, 255, 255, 255 * min(1.0, v * 1.4)) if v > 0.05 else (0, 0, 0, 0)
    return radial(8, f)


def star(frame):
    big = frame == 0

    def f(dx, dy):
        d = math.hypot(dx, dy)
        ray = min(abs(dx), abs(dy))
        arm = max(0.0, 1 - ray / (0.16 if big else 0.12)) * max(0.0, 1 - d / (1.0 if big else 0.7))
        core = max(0.0, 1 - d / 0.3)
        v = max(core, arm)
        return (255, 255, 255, 255 * min(1.0, v * 1.5)) if v > 0.08 else (0, 0, 0, 0)
    return radial(8, f)


def ember(frame):
    r = [0.9, 0.7, 0.5][frame]

    def f(dx, dy):
        d = math.hypot(dx, dy) / r
        v = max(0.0, 1 - d)
        return (255, 255, 255, 255 * v ** 0.8) if v > 0.02 else (0, 0, 0, 0)
    return radial(8, f)


def flame(frame):
    n = value_noise(16, 16, 900 + frame, scale=3, octaves=2)
    img = np.zeros((16, 16, 4))
    height = [0.75, 1.0, 0.85, 0.6][frame]
    for y in range(16):
        for x in range(16):
            fy = 1 - y / 15.0  # 0 at bottom, 1 at top
            fx = abs(x - 7.5) / 8.0
            width = (1 - fy / height) ** 0.7 if fy < height else 0
            shape = width - fx - (n[y, x] - 0.5) * 0.35
            if shape <= 0:
                continue
            heat = min(1.0, shape * 0.95)
            if heat > 0.9:
                c = (255, 236, 196)
            elif heat > 0.72:
                c = GOLD[5][:3] if frame < 2 else VIOLET[6][:3]
            elif heat > 0.4:
                c = VIOLET[5][:3]
            elif heat > 0.18:
                c = VIOLET[4][:3]
            else:
                c = VIOLET[2][:3]
            a = min(255, 110 + heat * 150)
            img[y, x] = (*c, a)
    return img


def shockwave():
    def f(dx, dy):
        d = math.hypot(dx, dy)
        ring = max(0.0, 1 - abs(d - 0.82) / 0.12)
        inner = max(0.0, 1 - abs(d - 0.7) / 0.06) * 0.6
        haze = max(0.0, 1 - d / 0.82) * 0.18 if d < 0.82 else 0
        v = max(ring, inner, haze)
        if v <= 0.02:
            return (0, 0, 0, 0)
        if ring > inner:
            c = (255, 214, 120) if ring > 0.7 else VIOLET[5][:3]
        else:
            c = VIOLET[4][:3]
        return (*c, 255 * min(1.0, v))
    return radial(32, f)


# ---------------------------------------------------------------------------------------------------------------------
# Beam layers: u wraps around the tube, v runs along it (tiles every 4 blocks)
# ---------------------------------------------------------------------------------------------------------------------

def beam_core():
    img = np.zeros((32, 32, 4))
    n = value_noise(32, 32, 31, scale=4, octaves=2)
    for y in range(32):
        for x in range(32):
            streak = 0.5 + 0.5 * math.sin((x / 32.0) * math.pi * 6 + y * 0.4)
            v = 0.65 + 0.35 * streak * n[y, x]
            c = (255, 245 - 25 * streak, 215 - 60 * streak)
            img[y, x] = (*c, 255 * v)
    return img


def beam_body():
    img = np.zeros((32, 32, 4))
    n = value_noise(32, 32, 32, scale=3, octaves=3)
    for y in range(32):
        for x in range(32):
            filament = abs(math.sin((x / 32.0) * math.pi * 4 + y * 0.35)) > 0.94
            t = n[y, x]
            if filament:
                c, a = GOLD[5][:3], 230
            else:
                c = VIOLET[int(np.clip(2 + t * 4, 0, 6))][:3]
                a = 150 + 100 * t
            img[y, x] = (*c, a)
    return img


def beam_haze():
    img = np.zeros((32, 32, 4))
    n = value_noise(32, 32, 33, scale=2, octaves=3)
    for y in range(32):
        for x in range(32):
            t = n[y, x]
            img[y, x] = (*VIOLET[4][:3], 40 + 110 * t)
    return img


# ---------------------------------------------------------------------------------------------------------------------
# Boss bar sheet (256x64). Regions are mirrored in WorldEaterBossBar.java.
#   frame (0,0) 240x24, inner bar at (12,8) 216x8; fill (0,24); enraged fill (0,32); trail (0,40);
#   plate (0,48) 176x16; empty well (0,56) 216x8; notch (224,24) 3x12; shine (232,24) 12x8
# ---------------------------------------------------------------------------------------------------------------------

def bar_sheet():
    img = np.zeros((64, 256, 4), dtype=float)
    dark = hx("120a1e")
    rim = hx("2a1640")

    def put(x, y, c):
        img[y, x] = c

    def gold_px(x, y, shade):
        put(x, y, GOLD[int(np.clip(shade, 0, 6))])

    # Frame: ornate gold border around the bar slot, diamond end caps, gem at the centre top and bottom.
    for y in range(24):
        for x in range(240):
            in_slot = 12 <= x < 228 and 8 <= y < 16
            border_outer = 10 <= x < 230 and 6 <= y < 18
            if in_slot:
                continue
            if border_outer:
                edge = y in (6, 17) or x in (10, 229)
                inner = y in (7, 16) or x in (11, 228)
                if edge:
                    gold_px(x, y, 3 if y == 17 else 5)
                elif inner:
                    put(x, y, rim)
                continue
            # end caps: diamonds at both ends
            for cx in (6, 233):
                d = abs(x - cx) + abs(y - 11.5)
                if d <= 7.5:
                    if d > 6.0:
                        gold_px(x, y, 5 if y < 12 else 3)
                    elif d > 3.5:
                        gold_px(x, y, 4 if (x + y) % 2 else 3)
                    else:
                        put(x, y, VIOLET[5] if d < 1.6 else VIOLET[3])
    # Filigree studs along the top and bottom border
    for x in range(22, 222, 20):
        for dx in (-1, 0, 1):
            gold_px(x + dx, 5, 4)
            gold_px(x + dx, 18, 3)
        gold_px(x, 4, 6)
        gold_px(x, 19, 2)
    # Centre gems (top and bottom)
    for cy, base in ((3, 5), (20, 3)):
        for y in range(cy - 3, cy + 4):
            for x in range(114, 127):
                d = abs(x - 120) + abs(y - cy) * 1.6
                if 0 <= y < 24 and d <= 6:
                    if d > 4.5:
                        gold_px(x, y, base)
                    else:
                        put(x, y, VIOLET[6] if d < 1.5 else VIOLET[4])

    # Fills: vertical gradient with a lit top line; enraged runs hotter toward crimson-violet.
    for y in range(8):
        for x in range(216):
            t = y / 7.0
            violet = VIOLET[5] if y == 0 else VIOLET[4] if y <= 2 else VIOLET[3] if y <= 5 else VIOLET[2]
            img[24 + y, x] = violet
            hot = (255, 170, 210, 255) if y == 0 else (230, 80, 170, 255) if y <= 2 else (180, 40, 140, 255) if y <= 5 else (110, 20, 90, 255)
            img[32 + y, x] = hot
            img[40 + y, x] = (255, 236, 190, 230) if y else (255, 250, 230, 255)
            img[56 + y, x] = dark if y else rim
            if (x // 3 + y) % 9 == 0 and y not in (0, 7):
                img[24 + y, x] = VIOLET[5]
    # Title plate: gold-framed dark void panel with notched ends
    for y in range(16):
        for x in range(176):
            notch = (x < 4 and (y < 4 - x or y > 11 + x)) or (x > 171 and (y < x - 171 or y > 186 - x))
            if notch:
                continue
            edge = y in (0, 15) or x in (0, 175) or (x < 5 and abs(y - 7.5) > 7.5 - x - 0.5) or (x > 170 and abs(y - 7.5) > 7.5 - (175 - x) - 0.5)
            if edge:
                gold_px(x, 48 + y, 5 if y < 8 else 3)
            elif y in (1, 14) or x in (1, 174):
                gold_px(x, 48 + y, 2)
            else:
                img[48 + y, x] = dark
    # notch marker and shine
    for y in range(12):
        for x in range(3):
            img[24 + y, 224 + x] = GOLD[5] if x == 1 else GOLD[2]
    for y in range(8):
        for x in range(12):
            a = (1 - abs(x - 5.5) / 6.0) ** 2 * 150
            img[24 + y, 232 + x] = (255, 255, 255, a)
    return img


def erosion_icon():
    img = canvas(18, 18)
    rng = np.random.default_rng(77)
    for y in range(18):
        for x in range(18):
            d = math.hypot(x - 8.5, y - 8.5)
            if d < 7.5:
                t = 1 - d / 7.5
                img[y, x] = VIOLET[int(np.clip(1 + t * 4, 0, 6))]
            if 7.5 <= d < 8.5:
                img[y, x] = VIOLET[0]
    # cracks eating through
    for start in ((4, 3), (13, 5), (6, 14)):
        x, y = start
        for _ in range(7):
            if 0 <= x < 18 and 0 <= y < 18 and math.hypot(x - 8.5, y - 8.5) < 7.5:
                img[y, x] = hx("0b0611")
            x += int(rng.integers(-1, 2))
            y += 1 if start[1] < 9 else -1
    img[6, 7] = (255, 245, 255, 255)
    return img


def main():
    for i in range(4):
        save(spark(i), f"textures/particle/void_spark_{i}.png")
        save(flame(i), f"textures/particle/void_flame_{i}.png")
    for i in range(2):
        save(star(i), f"textures/particle/star_mote_{i}.png")
    for i in range(3):
        save(ember(i), f"textures/particle/void_ember_{i}.png")
    save(shockwave(), "textures/particle/shockwave.png")
    sparks = [f"void_spark_{i}" for i in range(4)]
    particle_json("void_spark", sparks)
    particle_json("gold_spark", sparks)
    particle_json("star_mote", ["star_mote_0", "star_mote_1", "star_mote_0", "star_mote_1"])
    particle_json("void_ember", [f"void_ember_{i}" for i in range(3)])
    particle_json("void_flame", [f"void_flame_{i}" for i in range(4)])
    particle_json("shockwave", ["shockwave"])
    save(beam_core(), "textures/entity/beam/void_breath_core.png")
    save(beam_body(), "textures/entity/beam/void_breath_body.png")
    save(beam_haze(), "textures/entity/beam/void_breath_haze.png")
    save(bar_sheet(), "textures/gui/world_eater_bar.png")
    save(erosion_icon(), "textures/mob_effect/erosion.png")
    print("fx textures written")


if __name__ == "__main__":
    main()
