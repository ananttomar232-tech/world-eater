"""Surface materials for the Aetherfall models. Each returns (base RGBA, glowmask RGBA or None) for one face.

Face orientation: for side faces, row 0 is the top edge; for up/down faces row 0 is the back (+Z) / front edge
respectively (see preview.py). Materials that need orientation receive the face name.
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "assets"))
from palette import GOLD, NEBULA, STAR, VIOLET, hx, value_noise  # noqa: E402

SCALE = [hx("08050d"), hx("100a18"), hx("181022"), hx("21162f"), hx("2c1e3e"), hx("3a2852"), hx("4b3568")]
BELLY = [hx("140d1f"), hx("1d142b"), hx("271b38"), hx("322447"), hx("3f2e58")]
IVORY = [hx("6e5a7e"), hx("a896b8"), hx("d9cde6"), hx("f4eefb")]


def blank(w, h):
    return np.zeros((h, w, 4), dtype=np.uint8)


def noise(w, h, seed, scale=3.0, octaves=2):
    # value_noise needs a square-ish tile; generate at max dim and crop.
    n = max(w, h, 4)
    return value_noise(n, n, seed, scale=scale, octaves=octaves)[:h, :w]


def glyph_bits():
    """5x5 rune glyphs used for gold engravings (the World Eater's script)."""
    raw = [
        ["#...#", ".#.#.", "..#..", ".#.#.", "#...#"],
        ["..#..", ".###.", "#.#.#", "..#..", "..#.."],
        ["####.", "#...#", "####.", "#.#..", "#..##"],  # the 'R' sigil from the reference armour
        ["#.#.#", "#.#.#", ".###.", "..#..", ".###."],
        [".###.", "#...#", "#.#.#", "#...#", ".###."],
        ["#....", "##...", "#.#..", "#..#.", "#####"],
    ]
    return [[[c == "#" for c in row] for row in g] for g in raw]


GLYPHS = glyph_bits()


# ---------------------------------------------------------------------------------------------------------------------

def scales(w, h, face, seed, p):
    rng = np.random.default_rng(seed)
    n = noise(w, h, seed, 2.5)
    img = blank(w, h)
    dark = face in ("down",)
    sheen = p.get("sheen", 0.0)
    for y in range(h):
        for x in range(w):
            row = y // 3
            off = 0 if row % 2 == 0 else 2
            lx = (x + off) % 4
            ly = y % 3
            tone = 2 + (1 if n[y, x] > 0.6 else 0) - (1 if n[y, x] < 0.38 else 0)
            if ly == 2:
                tone += 1 if lx in (1, 2) else 0  # lit lower rim of each scale
            if ly == 0 and lx in (0, 3):
                tone -= 1  # shadow between scales
            if dark:
                tone -= 1
            img[y, x] = SCALE[int(np.clip(tone, 0, len(SCALE) - 1))]
            if sheen and ly == 2 and lx == 1 and rng.random() < sheen:
                img[y, x] = VIOLET[2]
    return img, None


def belly(w, h, face, seed, p):
    n = noise(w, h, seed, 2.0)
    img = blank(w, h)
    for y in range(h):
        band = y % 4
        for x in range(w):
            tone = 2 + (1 if n[y, x] > 0.6 else 0)
            if band == 0:
                tone = 0  # seam between plates
            elif band == 1:
                tone += 1
            img[y, x] = BELLY[int(np.clip(tone, 0, len(BELLY) - 1))]
    return img, None


def gold(w, h, face, seed, p):
    rng = np.random.default_rng(seed)
    n = noise(w, h, seed, 3.0)
    img = blank(w, h)
    glow = blank(w, h)
    for y in range(h):
        grad = 1.0 - y / max(1, h - 1)
        for x in range(w):
            t = 3 + grad * 1.4 + (n[y, x] - 0.5) * 1.2
            if y == 0 or x == 0:
                t += 1.3
            if y == h - 1 or x == w - 1:
                t -= 1.4
            img[y, x] = GOLD[int(np.clip(round(t), 0, 6))]
    # Rivets in the corners of larger plates
    if w >= 8 and h >= 6:
        for (rx, ry) in ((2, 2), (w - 3, 2), (2, h - 3), (w - 3, h - 3)):
            img[ry, rx] = GOLD[6]
            if ry + 1 < h:
                img[ry + 1, rx] = GOLD[2]
    if p.get("rune") and face == p.get("rune_face", "north") and w >= 7 and h >= 7:
        engrave_runes(img, glow, w, h, rng, p.get("sigil", False))
    if p.get("edge_glow"):
        for x in range(w):
            glow[0, x] = (255, 200, 90, 150)
    return img, glow


def engrave_runes(img, glow, w, h, rng, sigil):
    """Cuts glowing violet runes into a gold face: a centred sigil on big plates, a band of script otherwise."""
    if sigil and w >= 11 and h >= 11:
        g = GLYPHS[2]
        s = 2 if (w >= 20 and h >= 16) else 1
        gw = 5 * s
        x0 = (w - gw) // 2
        y0 = (h - gw) // 2
        # dark recessed panel behind the sigil
        for y in range(y0 - 2, y0 + gw + 2):
            for x in range(x0 - 2, x0 + gw + 2):
                if 0 <= x < w and 0 <= y < h:
                    img[y, x] = GOLD[1] if (y in (y0 - 2, y0 + gw + 1) or x in (x0 - 2, x0 + gw + 1)) else hx("1b0f2c")
        for gy in range(5):
            for gx in range(5):
                if g[gy][gx]:
                    for dy in range(s):
                        for dx in range(s):
                            img[y0 + gy * s + dy, x0 + gx * s + dx] = VIOLET[5]
                            glow[y0 + gy * s + dy, x0 + gx * s + dx] = (190, 110, 255, 255)
        return
    count = max(1, (w - 2) // 7)
    y0 = max(1, (h - 5) // 2)
    for i in range(count):
        g = GLYPHS[int(rng.integers(0, len(GLYPHS)))]
        x0 = 1 + i * 7 + ((w - 2) - count * 7) // 2 + 1
        for gy in range(5):
            for gx in range(5):
                x, y = x0 + gx, y0 + gy
                if g[gy][gx] and 0 <= x < w and 0 <= y < h:
                    img[y, x] = VIOLET[4]
                    glow[y, x] = (170, 90, 255, 230)


def crystal(w, h, face, seed, p):
    rng = np.random.default_rng(seed)
    img = blank(w, h)
    glow = blank(w, h)
    tip_top = p.get("tip", "top") == "top"
    for y in range(h):
        t = y / max(1, h - 1)
        heat = (1 - t) if tip_top else t
        for x in range(w):
            edge = x == 0 or x == w - 1
            facet = (x + y // 2) % 5 == 0
            tone = 2 + heat * 3 + (1 if facet else 0) - (1 if edge else 0)
            img[y, x] = VIOLET[int(np.clip(round(tone), 0, 6))]
            a = int(70 + 170 * heat)
            glow[y, x] = (150 + int(80 * heat), 60 + int(90 * heat), 255, a if not edge else a // 2)
    for _ in range(max(1, w * h // 40)):
        x, y = rng.integers(0, w), rng.integers(0, h)
        img[y, x] = STAR
        glow[y, x] = (240, 220, 255, 255)
    return img, glow


def membrane(w, h, face, seed, p):
    """Star-filled wing membrane: deep nebula, constellations, gold-lit edges, optional scalloped trailing edge."""
    rng = np.random.default_rng(seed)
    n = noise(w, h, seed, 3.0, 3)
    n2 = noise(w, h, seed + 7, 6.0, 2)
    img = blank(w, h)
    glow = blank(w, h)
    for y in range(h):
        for x in range(w):
            t = n[y, x] * 0.75 + n2[y, x] * 0.25
            c = NEBULA[int(np.clip(t * len(NEBULA) * 1.15, 0, len(NEBULA) - 1))]
            if t > 0.72:
                c = VIOLET[2]
            img[y, x] = c
            if t > 0.6:
                glow[y, x] = (120, 50, 210, int((t - 0.6) * 300))
    # stars, with a few bright four-point stars
    for _ in range(max(2, w * h // 28)):
        x, y = rng.integers(0, w), rng.integers(0, h)
        bright = rng.random() < 0.18
        img[y, x] = STAR if bright else VIOLET[5]
        glow[y, x] = (255, 240, 255, 255) if bright else (200, 150, 255, 200)
        if bright and rng.random() < 0.5:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if 0 <= x + dx < w and 0 <= y + dy < h:
                    img[y + dy, x + dx] = VIOLET[4]
                    glow[y + dy, x + dx] = (190, 140, 255, 160)
    # Shape: taper (triangle toward one corner) and scalloped trailing edge, both as cut-out alpha.
    taper = p.get("taper")
    scallop = p.get("scallop", 0)
    for y in range(h):
        for x in range(w):
            cut = False
            fx = x / max(1, w - 1)
            fy = y / max(1, h - 1)
            if taper == "outer":   # shrinks toward the wing tip (texture right edge is the outer side)
                cut = fy > 1.0 - 0.85 * fx
            elif taper == "inner":
                cut = fy > 0.25 + 0.75 * fx
            if scallop:
                period = w / scallop
                local = (x % period) / period
                depth = 0.10 + 0.08 * math.sin(math.pi * local)
                if fy > 1.0 - depth * (1.0 - abs(local - 0.5) * 2):
                    cut = True
            if cut:
                img[y, x] = (0, 0, 0, 0)
                glow[y, x] = (0, 0, 0, 0)
    # Gold edging on the outline of what's left (the reference wings' glowing gold borders)
    alpha = img[..., 3] > 0
    edge_px = p.get("edge", 1)
    for y in range(h):
        for x in range(w):
            if not alpha[y, x]:
                continue
            border = (y < 1 and p.get("top_edge", True)) or x < edge_px and p.get("left_edge", False) \
                or x >= w - edge_px and p.get("right_edge", False)
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                xx, yy = x + dx, y + dy
                if 0 <= xx < w and 0 <= yy < h and not alpha[yy, xx]:
                    border = True
            if border:
                img[y, x] = GOLD[4] if (x + y) % 3 else GOLD[5]
                glow[y, x] = (255, 196, 80, 235)
    return img, glow


def wing_bone(w, h, face, seed, p):
    img, _ = scales(w, h, face, seed, {})
    glow = blank(w, h)
    if face in ("up", "north", "south"):
        band = 0 if face != "up" else None
        for x in range(w):
            if face == "up":
                for y in range(h):
                    if y in (h // 2, h // 2 - 1) or h <= 3:
                        img[y, x] = GOLD[4]
                        glow[y, x] = (255, 190, 70, 140)
            else:
                img[band, x] = GOLD[5]
                if h > 3:
                    img[1, x] = GOLD[3]
                glow[band, x] = (255, 200, 90, 200)
    return img, glow


def horn(w, h, face, seed, p):
    img = blank(w, h)
    glow = blank(w, h)
    for y in range(h):
        for x in range(w):
            along = x / max(1, w - 1) if face in ("up", "down", "north", "south") else y / max(1, h - 1)
            t = 2 + 3.5 * along + (1 if (x + y) % 4 == 0 else 0)
            img[y, x] = GOLD[int(np.clip(round(t), 0, 6))]
            if along > 0.7:
                glow[y, x] = (255, 210, 110, int(200 * (along - 0.7) / 0.3))
    return img, glow


def eye(w, h, face, seed, p):
    img = blank(w, h)
    glow = blank(w, h)
    for y in range(h):
        for x in range(w):
            cx = abs(x - (w - 1) / 2) / max(1, w / 2)
            cy = abs(y - (h - 1) / 2) / max(1, h / 2)
            d = max(cx, cy)
            c = STAR if d < 0.34 else VIOLET[5] if d < 0.7 else VIOLET[3]
            img[y, x] = c
            glow[y, x] = (235, 200, 255, 255) if d < 0.34 else (200, 90, 255, 255)
    return img, glow


def mouth(w, h, face, seed, p):
    rng = np.random.default_rng(seed)
    img = blank(w, h)
    glow = blank(w, h)
    for y in range(h):
        for x in range(w):
            ridge = y % 3 == 0
            img[y, x] = VIOLET[1] if ridge else VIOLET[3]
            glow[y, x] = (210, 80, 255, 140 if ridge else 220)
    for _ in range(w * h // 18):
        x, y = rng.integers(0, w), rng.integers(0, h)
        img[y, x] = VIOLET[6]
        glow[y, x] = (255, 220, 255, 255)
    return img, glow


def teeth(w, h, face, seed, p):
    img = blank(w, h)
    up = p.get("up", False)
    period = 3
    for x in range(w):
        local = x % period
        length = h if local == 1 else max(1, h - 1) if local == 0 else 0
        for i in range(length):
            y = (h - 1 - i) if up else i
            img[y, x] = IVORY[2] if i < length - 1 else IVORY[3]
            if x % period == 2:
                img[y, x] = (0, 0, 0, 0)
    return img, None


def claw(w, h, face, seed, p):
    img = blank(w, h)
    glow = blank(w, h)
    tip_down = p.get("tip", "bottom") == "bottom"
    for y in range(h):
        t = y / max(1, h - 1)
        heat = t if tip_down else 1 - t
        for x in range(w):
            img[y, x] = VIOLET[int(np.clip(round(1 + heat * 4.5), 0, 6))] if heat > 0.35 else SCALE[1]
            if heat > 0.6:
                glow[y, x] = (200, 110, 255, int(255 * (heat - 0.6) / 0.4))
    return img, glow


def rock(w, h, face, seed, p):
    """Meteor shell: black basalt shot through with burning violet-gold cracks."""
    rng = np.random.default_rng(seed)
    n = noise(w, h, seed, 2.5, 3)
    img = blank(w, h)
    glow = blank(w, h)
    for y in range(h):
        for x in range(w):
            img[y, x] = SCALE[int(np.clip(1 + n[y, x] * 4, 0, 5))]
    for _ in range(max(1, (w + h) // 6)):
        x, y = int(rng.integers(0, w)), int(rng.integers(0, h))
        for _step in range(int(rng.integers(3, 8))):
            hot = rng.random() < 0.35
            img[y, x] = GOLD[5] if hot else VIOLET[4]
            glow[y, x] = (255, 200, 90, 255) if hot else (190, 90, 255, 255)
            x = int(np.clip(x + rng.integers(-1, 2), 0, w - 1))
            y = int(np.clip(y + rng.integers(-1, 2), 0, h - 1))
    return img, glow


def core(w, h, face, seed, p):
    img = blank(w, h)
    glow = blank(w, h)
    for y in range(h):
        for x in range(w):
            d = math.hypot((x - (w - 1) / 2) / max(1, w / 2), (y - (h - 1) / 2) / max(1, h / 2))
            img[y, x] = STAR if d < 0.4 else GOLD[5] if d < 0.7 else VIOLET[5]
            glow[y, x] = (255, 235, 200, 255) if d < 0.5 else (220, 120, 255, 255)
    return img, glow


PAINTERS = {
    "scale": scales,
    "scale_sheen": lambda w, h, f, s, p: scales(w, h, f, s, {"sheen": 0.25}),
    "belly": belly,
    "gold": gold,
    "gold_rune": lambda w, h, f, s, p: gold(w, h, f, s, {**p, "rune": True}),
    "gold_sigil": lambda w, h, f, s, p: gold(w, h, f, s, {**p, "rune": True, "sigil": True}),
    "crystal": crystal,
    "membrane": membrane,
    "wing_bone": wing_bone,
    "horn": horn,
    "eye": eye,
    "mouth": mouth,
    "teeth": teeth,
    "teeth_up": lambda w, h, f, s, p: teeth(w, h, f, s, {"up": True}),
    "claw": claw,
    "rock": rock,
    "core": core,
}
