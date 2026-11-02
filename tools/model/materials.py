"""Surface materials for the Aetherfall models. Each returns (base RGBA, glow RGBA or None) for one face.

Faces are painted in texels (the model is packed at 2 texels per unit). For side faces row 0 is the top edge;
for left-wing planes column 0 is the joint and the last column the tip. Mirrored (right-side) cubes receive
params["flip"] and are flipped horizontally so asymmetric shapes (membrane wedges) stay correct.

Glow: the colour drawn additively, full-bright, by EmissiveGlowLayer. Alpha scales it (premultiplied on export),
so alpha 40 is a soft sheen and 255 a hot glow.
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "assets"))
from palette import GOLD, STAR, hx, value_noise  # noqa: E402

# Brighter than vanilla "dark" mobs on purpose: the reference creature reads violet, not black.
SCALE = [hx("140c22"), hx("211533"), hx("2f1f47"), hx("3e2a5c"), hx("503774"), hx("65468f"), hx("7e5aae")]
BELLY = [hx("1f1531"), hx("2c1f43"), hx("3a2a56"), hx("4a376a"), hx("5c4680")]
VIOLET = [hx("3a0f66"), hx("5a189e"), hx("7b2cd6"), hx("9d4dff"), hx("bb7bff"), hx("dbb2ff"), hx("f4e6ff")]
NEBULA = [hx("1a0838"), hx("2c0e5c"), hx("45168a"), hx("6224b4"), hx("8a3ad8"), hx("b65cf0")]
MAGENTA = [hx("5a1070"), hx("8a1ea6"), hx("c040d8")]
IVORY = [hx("7a6890"), hx("b0a0c4"), hx("ddd2ee"), hx("f6f0ff")]

G_VIOLET = (190, 100, 255)
G_GOLD = (255, 190, 80)
G_WHITE = (245, 225, 255)


def blank(w, h):
    return np.zeros((h, w, 4), dtype=np.uint8)


def noise(w, h, seed, scale=3.0, octaves=2):
    n = max(w, h, 4)
    return value_noise(n, n, seed, scale=scale, octaves=octaves)[:h, :w]


def finish(img, glow, p):
    if p.get("flip"):
        img = img[:, ::-1].copy()
        glow = glow[:, ::-1].copy() if glow is not None else None
    return img, glow


GLYPHS = [
    ["#...#", ".#.#.", "..#..", ".#.#.", "#...#"],
    ["..#..", ".###.", "#.#.#", "..#..", "..#.."],
    ["####.", "#...#", "####.", "#.#..", "#..##"],   # the 'R' sigil of the reference armour
    ["#.#.#", "#.#.#", ".###.", "..#..", ".###."],
    [".###.", "#...#", "#.#.#", "#...#", ".###."],
    ["#....", "##...", "#.#..", "#..#.", "#####"],
    ["#####", "..#..", ".###.", "#.#.#", "#...#"],
]
GLYPHS = [[[c == "#" for c in row] for row in g] for g in GLYPHS]


# ---------------------------------------------------------------------------------------------------------------------

def scales(w, h, face, seed, p):
    """Overlapping fish scales (8x6 texels), painted row by row so each row overlaps the one above: violet body,
    lit lower rim with a soft violet glow, shadow where it tucks under the next scale."""
    rng = np.random.default_rng(seed)
    n = noise(w, h, seed, 2.5)
    img = blank(w, h)
    glow = blank(w, h)
    dark = face == "down"
    sheen = p.get("sheen", 0.12)
    base_shift = -1.0 if dark else 0.0
    for y in range(h):
        for x in range(w):
            img[y, x] = SCALE[1]
    cw, ch = 8, 6
    for row in range(-1, h // ch + 2):
        cy = row * ch - 1
        off = 0 if row % 2 == 0 else cw // 2
        for col in range(-1, w // cw + 2):
            cx = col * cw + off + (cw - 1) / 2
            for y in range(int(cy), int(cy + ch + 2)):
                for x in range(int(cx - cw / 2), int(cx + cw / 2 + 1)):
                    if not (0 <= x < w and 0 <= y < h):
                        continue
                    dx = (x - cx) / (cw / 2)
                    dy = (y - cy) / (ch + 1)
                    if dy < 0 or dx * dx + dy * dy > 1.0:
                        continue
                    d = math.sqrt(dx * dx + dy * dy)
                    tone = 2.2 + dy * 1.8 + (n[y, x] - 0.5) * 1.2 + base_shift
                    if d > 0.82:
                        tone += 1.4          # lit rim
                    elif d > 0.7:
                        tone -= 0.6          # groove inside the rim
                    if dx < -0.55:
                        tone -= 0.6          # side shading
                    t = int(np.clip(round(tone), 0, len(SCALE) - 1))
                    img[y, x] = SCALE[t]
                    if d > 0.82 and not dark:
                        glow[y, x] = (*G_VIOLET, 72)
                        if rng.random() < sheen * 0.4:
                            img[y, x] = VIOLET[4]
                            glow[y, x] = (*G_VIOLET, 150)
                    else:
                        glow[y, x] = (0, 0, 0, 0)
    return finish(img, glow, p)


def belly(w, h, face, seed, p):
    """Horizontal armoured belly plates with violet-lit seams."""
    n = noise(w, h, seed, 2.0)
    img = blank(w, h)
    glow = blank(w, h)
    for y in range(h):
        band = y % 6
        for x in range(w):
            tone = 2 + (1 if n[y, x] > 0.62 else 0) - (1 if n[y, x] < 0.36 else 0)
            if band == 0:
                tone = 0
            elif band == 1:
                tone += 1
            elif band == 5:
                tone -= 1
            img[y, x] = BELLY[int(np.clip(tone, 0, len(BELLY) - 1))]
            if band == 0 and (x // 3) % 2 == 0:
                img[y, x] = VIOLET[1]
                glow[y, x] = (*G_VIOLET, 70)
    return finish(img, glow, p)


def gold(w, h, face, seed, p):
    """Polished forged gold: vertical gradient, bevelled edges, rivets, a soft metallic sheen in the glow layer,
    optional glowing rune engravings (rune) or the R sigil (sigil)."""
    rng = np.random.default_rng(seed)
    n = noise(w, h, seed, 3.0)
    img = blank(w, h)
    glow = blank(w, h)
    for y in range(h):
        grad = 1.0 - y / max(1, h - 1)
        for x in range(w):
            t = 3.2 + grad * 1.6 + (n[y, x] - 0.5) * 1.4
            edge_hi = y <= 1 or x <= 1
            edge_lo = y >= h - 2 or x >= w - 2
            if edge_hi:
                t += 1.4
            if edge_lo:
                t -= 1.6
            img[y, x] = GOLD[int(np.clip(round(t), 0, 6))]
            glow[y, x] = (*G_GOLD, 210 if edge_hi else 120)
    if w >= 12 and h >= 10:
        for (rx, ry) in ((3, 3), (w - 4, 3), (3, h - 4), (w - 4, h - 4)):
            img[ry, rx] = GOLD[6]
            img[ry + 1, rx] = GOLD[2]
            glow[ry, rx] = (*G_GOLD, 255)
    if p.get("rune") and face == "north":
        engrave(img, glow, w, h, rng, p.get("sigil", False))
    return finish(img, glow, p)


def engrave(img, glow, w, h, rng, sigil):
    dark = hx("1b0d2e")
    if sigil and w >= 14 and h >= 14:
        g = GLYPHS[2]
        s = max(1, min((w - 6) // 6, (h - 6) // 6))
        gw = 5 * s
        x0 = (w - gw) // 2
        y0 = (h - gw) // 2
        for y in range(y0 - 3, y0 + gw + 3):
            for x in range(x0 - 3, x0 + gw + 3):
                if 0 <= x < w and 0 <= y < h:
                    border = y in (y0 - 3, y0 + gw + 2) or x in (x0 - 3, x0 + gw + 2)
                    img[y, x] = GOLD[1] if border else dark
                    glow[y, x] = (*G_VIOLET, 60) if not border else glow[y, x]
        for gy in range(5):
            for gx in range(5):
                if g[gy][gx]:
                    for dy in range(s):
                        for dx in range(s):
                            img[y0 + gy * s + dy, x0 + gx * s + dx] = VIOLET[5]
                            glow[y0 + gy * s + dy, x0 + gx * s + dx] = (*G_VIOLET, 255)
        return
    if h < 7:
        return
    count = max(1, (w - 2) // 7)
    y0 = (h - 5) // 2
    x_start = (w - count * 7 + 2) // 2
    for i in range(count):
        g = GLYPHS[int(rng.integers(0, len(GLYPHS)))]
        x0 = x_start + i * 7
        for gy in range(5):
            for gx in range(5):
                x, y = x0 + gx, y0 + gy
                if 0 <= x < w and 0 <= y < h:
                    if g[gy][gx]:
                        img[y, x] = VIOLET[4]
                        glow[y, x] = (*G_VIOLET, 255)
                    else:
                        img[y, x] = GOLD[2]


def crystal(w, h, face, seed, p):
    """Faceted void crystal, hotter toward the tip; nearly the whole surface glows."""
    rng = np.random.default_rng(seed)
    img = blank(w, h)
    glow = blank(w, h)
    tip_top = p.get("tip", "top") == "top"
    for y in range(h):
        t = y / max(1, h - 1)
        heat = (1 - t) if tip_top else t
        for x in range(w):
            edge = x == 0 or x == w - 1
            facet = (x * 2 + y) % 7 == 0
            tone = 2.2 + heat * 3.4 + (0.8 if facet else 0) - (1 if edge else 0)
            c = VIOLET[int(np.clip(round(tone), 0, 6))]
            img[y, x] = c
            glow[y, x] = (170 + int(70 * heat), 80 + int(110 * heat), 255, int(160 + 95 * heat) if not edge else 130)
    for _ in range(max(1, w * h // 30)):
        x, y = rng.integers(0, w), rng.integers(0, h)
        img[y, x] = STAR
        glow[y, x] = (*G_WHITE, 255)
    return finish(img, glow, p)


def membrane(w, h, face, seed, p):
    """Cosmic wing membrane: bright violet-magenta nebula, dense stars, gold-lit borders.

    shape: None (rectangle, optional scalloped bottom edge), or "wedge": the triangle between this finger
    (top edge) and the next finger (angle p["angle"] degrees below it), closed by a scalloped trailing edge
    between the two fingertips, exactly the panel of a bat wing.
    """
    rng = np.random.default_rng(seed)
    n = noise(w, h, seed, 3.0, 3)
    n2 = noise(w, h, seed + 7, 7.0, 2)
    n3 = noise(w, h, seed + 13, 1.6, 2)
    img = blank(w, h)
    glow = blank(w, h)
    for y in range(h):
        for x in range(w):
            t = n[y, x] * 0.6 + n2[y, x] * 0.25 + n3[y, x] * 0.15
            c = NEBULA[int(np.clip(t * len(NEBULA) * 1.25 - 0.6, 0, len(NEBULA) - 1))]
            if n3[y, x] > 0.68 and t > 0.55:
                c = MAGENTA[int(np.clip((t - 0.55) * 8, 0, 2))]
            img[y, x] = c
            g = int(np.clip(70 + (t - 0.35) * 260, 40, 190))
            glow[y, x] = (c[0], c[1], c[2], g)
    for _ in range(max(3, w * h // 18)):
        x, y = rng.integers(0, w), rng.integers(0, h)
        bright = rng.random() < 0.2
        img[y, x] = STAR if bright else VIOLET[5]
        glow[y, x] = (*G_WHITE, 255) if bright else (220, 170, 255, 230)
        if bright and rng.random() < 0.6:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if 0 <= x + dx < w and 0 <= y + dy < h:
                    img[y + dy, x + dx] = VIOLET[4]
                    glow[y + dy, x + dx] = (200, 150, 255, 200)

    keep = np.ones((h, w), dtype=bool)
    shape = p.get("shape")
    if shape == "wedge":
        angle = math.radians(p.get("angle", 26.0))
        L = w - 1
        tip_a = np.array([L, 0.0])
        tip_b = np.array([L * math.cos(angle), L * math.sin(angle)])
        chord = tip_b - tip_a
        normal = np.array([-chord[1], chord[0]])
        normal /= np.linalg.norm(normal)
        if np.dot(-tip_a, normal) < 0:
            normal = -normal  # point toward the joint
        clen = np.linalg.norm(chord)
        depth = p.get("scallop_depth", 0.16) * clen
        for y in range(h):
            for x in range(w):
                a = math.atan2(y + 0.5, x + 0.5)
                if a > angle + 0.02:
                    keep[y, x] = False
                    continue
                rel = np.array([x + 0.5, y + 0.5]) - tip_a
                along = np.clip(np.dot(rel, chord) / (clen * clen), 0, 1)
                inward = np.dot(rel, normal)
                if inward < depth * math.sin(math.pi * along):
                    keep[y, x] = False
    else:
        scallop = p.get("scallop", 0)
        for y in range(h):
            for x in range(w):
                fy = y / max(1, h - 1)
                if scallop:
                    period = w / scallop
                    local = (x % period) / period
                    depth = 0.08 + 0.10 * (1.0 - abs(local - 0.5) * 2)
                    if fy > 1.0 - depth:
                        keep[y, x] = False
    img[~keep] = 0
    glow[~keep] = 0
    # Gold border on every cut edge (and the top edge, which is the bone): the reference's glowing gold rims.
    border = np.zeros_like(keep)
    for y in range(h):
        for x in range(w):
            if not keep[y, x]:
                continue
            if y <= 1:
                border[y, x] = True
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (2, 0), (-2, 0), (0, 2), (0, -2)):
                xx, yy = x + dx, y + dy
                if not (0 <= xx < w and 0 <= yy < h) or not keep[yy, xx]:
                    if not (0 <= xx < w and 0 <= yy < h) and (xx < 0 or yy < 0):
                        continue  # the joint side meets the next panel: no border there
                    border[y, x] = True
                    break
    for y, x in zip(*np.nonzero(border)):
        img[y, x] = GOLD[5] if (x + y) % 3 else GOLD[6]
        glow[y, x] = (*G_GOLD, 255)
    return finish(img, glow, p)


def wing_bone(w, h, face, seed, p):
    """Gold-armoured wing spar with a dark core line, glowing gold."""
    img = blank(w, h)
    glow = blank(w, h)
    n = noise(w, h, seed, 4.0)
    for y in range(h):
        for x in range(w):
            centre = abs(y - (h - 1) / 2) / max(1, h / 2)
            t = 4.6 - centre * 2.2 + (n[y, x] - 0.5)
            img[y, x] = GOLD[int(np.clip(round(t), 0, 6))]
            glow[y, x] = (*G_GOLD, 220 if centre < 0.5 else 150)
            if (x // 4) % 6 == 0 and h > 4:
                img[y, x] = GOLD[2]
    return finish(img, glow, p)


def horn(w, h, face, seed, p):
    """Gold horn segment. Each segment is its own cube, so heat (0 base .. 1 tip) is a per-segment parameter:
    the horn brightens and glows hotter toward its tip without depending on face UV orientation."""
    heat = p.get("heat", 0.5)
    n = noise(w, h, seed, 3.0)
    img = blank(w, h)
    glow = blank(w, h)
    for y in range(h):
        for x in range(w):
            ridge = (x + y * 2) % 6 == 0
            t = 2.8 + 2.8 * heat + (n[y, x] - 0.5) * 1.2 + (0.8 if ridge else 0)
            img[y, x] = GOLD[int(np.clip(round(t), 0, 6))]
            glow[y, x] = (*G_GOLD, int(120 + 135 * heat ** 1.5))
    return finish(img, glow, p)


def eye(w, h, face, seed, p):
    img = blank(w, h)
    glow = blank(w, h)
    for y in range(h):
        for x in range(w):
            cx = abs(x - (w - 1) / 2) / max(1, w / 2)
            cy = abs(y - (h - 1) / 2) / max(1, h / 2)
            d = max(cx * 0.8, cy)
            c = STAR if d < 0.35 else VIOLET[5] if d < 0.7 else VIOLET[3]
            img[y, x] = c
            glow[y, x] = (*G_WHITE, 255) if d < 0.35 else (215, 110, 255, 255)
    return finish(img, glow, p)


def mouth(w, h, face, seed, p):
    rng = np.random.default_rng(seed)
    img = blank(w, h)
    glow = blank(w, h)
    for y in range(h):
        for x in range(w):
            ridge = y % 4 == 0
            img[y, x] = MAGENTA[1] if ridge else VIOLET[3]
            glow[y, x] = (225, 90, 255, 160 if ridge else 255)
    for _ in range(w * h // 14):
        x, y = rng.integers(0, w), rng.integers(0, h)
        img[y, x] = VIOLET[6]
        glow[y, x] = (*G_WHITE, 255)
    return finish(img, glow, p)


def teeth(w, h, face, seed, p):
    img = blank(w, h)
    up = p.get("up", False)
    period = 5
    for x in range(w):
        local = x % period
        length = [h - 2, h, h - 1, max(1, h - 3), 0][local]
        for i in range(max(0, length)):
            y = (h - 1 - i) if up else i
            img[y, x] = IVORY[2] if i < length - 1 else IVORY[3]
            if local == 0:
                img[y, x] = IVORY[1]
    return finish(img, None, p)


def claw(w, h, face, seed, p):
    img = blank(w, h)
    glow = blank(w, h)
    tip_down = p.get("tip", "bottom") == "bottom"
    for y in range(h):
        t = y / max(1, h - 1)
        heat = t if tip_down else 1 - t
        for x in range(w):
            if heat > 0.45:
                img[y, x] = VIOLET[int(np.clip(round(2 + heat * 4.5), 0, 6))]
                glow[y, x] = (210, 120, 255, int(100 + 155 * (heat - 0.45) / 0.55))
            else:
                img[y, x] = GOLD[int(np.clip(round(2 + heat * 4), 0, 6))]
                glow[y, x] = (*G_GOLD, 120)
    return finish(img, glow, p)


def rock(w, h, face, seed, p):
    """Meteor shell: black basalt shot through with burning violet-gold cracks."""
    rng = np.random.default_rng(seed)
    n = noise(w, h, seed, 2.5, 3)
    img = blank(w, h)
    glow = blank(w, h)
    for y in range(h):
        for x in range(w):
            img[y, x] = SCALE[int(np.clip(n[y, x] * 4, 0, 5))]
    for _ in range(max(1, (w + h) // 5)):
        x, y = int(rng.integers(0, w)), int(rng.integers(0, h))
        for _step in range(int(rng.integers(3, 9))):
            hot = rng.random() < 0.35
            img[y, x] = GOLD[5] if hot else VIOLET[4]
            glow[y, x] = (*G_GOLD, 255) if hot else (*G_VIOLET, 255)
            x = int(np.clip(x + rng.integers(-1, 2), 0, w - 1))
            y = int(np.clip(y + rng.integers(-1, 2), 0, h - 1))
    return finish(img, glow, p)


def core(w, h, face, seed, p):
    img = blank(w, h)
    glow = blank(w, h)
    for y in range(h):
        for x in range(w):
            d = math.hypot((x - (w - 1) / 2) / max(1, w / 2), (y - (h - 1) / 2) / max(1, h / 2))
            img[y, x] = STAR if d < 0.4 else GOLD[5] if d < 0.7 else VIOLET[5]
            glow[y, x] = (255, 235, 200, 255) if d < 0.5 else (220, 120, 255, 255)
    return finish(img, glow, p)


PAINTERS = {
    "scale": scales,
    "scale_sheen": lambda w, h, f, s, p: scales(w, h, f, s, {**p, "sheen": 0.3}),
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
    "teeth_up": lambda w, h, f, s, p: teeth(w, h, f, s, {**p, "up": True}),
    "claw": claw,
    "rock": rock,
    "core": core,
}
