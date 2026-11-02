"""Generates every Aetherfall block and item texture (16x16, vanilla-consistent pixel density).

Run from the repository root:
    python3 tools/assets/gen_textures.py

Output goes straight into src/main/resources/assets/aetherfall/textures/. All art is authored here
(procedural shading plus hand-placed glyph and silhouette grids), so the textures are reproducible
and can be tweaked by changing a seed or a grid.
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from palette import (CLEAR, GOLD, MORTAR, NEBULA, STAR, STONE, VIOLET, blend, canvas, from_grid, hx, put,  # noqa: E402
                     ramp, value_noise)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TEX = os.path.join(ROOT, "src", "main", "resources", "assets", "aetherfall", "textures")


def save(img, rel, frametime=None, interpolate=False):
    path = os.path.join(TEX, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    Image.fromarray(img, "RGBA").save(path)
    meta = path + ".mcmeta"
    if frametime is not None:
        with open(meta, "w") as f:
            json.dump({"animation": {"frametime": frametime, "interpolate": interpolate}}, f, indent=2)
            f.write("\n")
    elif os.path.exists(meta):
        os.remove(meta)


def stack_frames(frames):
    return np.concatenate(frames, axis=0)


# ---------------------------------------------------------------------------------------------------------------------
# Masonry
# ---------------------------------------------------------------------------------------------------------------------

def brick_layout():
    """Returns (brick_id map, list of brick rects). Rows are 4 px (3 px stone + 1 px mortar), bricks 8 px, staggered."""
    ids = -np.ones((16, 16), dtype=int)
    rects = []
    bid = 0
    for row in range(4):
        y0 = row * 4
        offset = 0 if row % 2 == 0 else 4
        for start in range(-8, 16, 8):
            x0 = start + offset
            xs = [x % 16 for x in range(x0, x0 + 7)]  # 7 px stone + 1 px mortar
            for y in range(y0, y0 + 3):
                for x in xs:
                    ids[y, x] = bid
            rects.append((bid, x0, y0))
            bid += 1
    return ids, rects


def void_bricks(seed, crack=False, star_count=1):
    rng = np.random.default_rng(seed)
    n = value_noise(16, 16, seed, scale=3, octaves=3)
    ids, rects = brick_layout()
    img = canvas(fill=MORTAR)
    tones = {bid: rng.integers(2, 5) for bid, _, _ in rects}
    for y in range(16):
        for x in range(16):
            bid = ids[y, x]
            if bid < 0:
                continue
            tone = tones[bid] + (1 if n[y, x] > 0.62 else 0) - (1 if n[y, x] < 0.36 else 0)
            # Bevel: lit from the top-left, as vanilla masonry is.
            above = ids[(y - 1) % 16, x]
            below = ids[(y + 1) % 16, x]
            left = ids[y, (x - 1) % 16]
            right = ids[y, (x + 1) % 16]
            if above != bid or left != bid:
                tone += 1
            if below != bid or right != bid:
                tone -= 1
            img[y, x] = STONE[int(np.clip(tone, 1, len(STONE) - 1))]
    # Star flecks: tiny violet-white inclusions in the stone.
    placed = 0
    while placed < star_count:
        x, y = rng.integers(0, 16, 2)
        if ids[y, x] >= 0:
            img[y, x] = VIOLET[2] if placed % 2 == 0 else VIOLET[1]
            placed += 1
    if crack:
        # Two cracks that wander across the face; violet light bleeds from the deepest part.
        for start, steps in (((3, 0), 9), ((12, 7), 10)):
            x, y = start
            for i in range(steps):
                put(img, x, y, MORTAR)
                if 2 <= i <= steps - 3 and i % 2 == 0:
                    put(img, x + 1, y, VIOLET[2])
                y += 1
                x += int(rng.choice([-1, 0, 1]))
                x = int(np.clip(x, 0, 15))
                if y > 15:
                    break
    return img


CHISELED = [
    "aaaaaaaaaaaaaaaa",
    "abbbbbbbbbbbbbbc",
    "ab............dc",
    "ab.eeeeeeeeee.dc",
    "ab.e...ff...e.dc",
    "ab.e..f..f..e.dc",
    "ab.e.f.gg.f.e.dc",
    "ab.eff.gg.ffe.dc",
    "ab.e.f.gg.f.e.dc",
    "ab.e..f..f..e.dc",
    "ab.e...ff...e.dc",
    "ab.e..f..f..e.dc",
    "ab.eeeeeeeeee.dc",
    "ab............dc",
    "addddddddddddddc",
    "cccccccccccccccc",
]


def chiseled_bricks():
    img = void_bricks(77, star_count=0)
    n = value_noise(16, 16, 78, scale=4)
    mapping = {"a": STONE[6], "b": STONE[5], "c": MORTAR, "d": STONE[1], "e": STONE[1], "f": STONE[0], "g": VIOLET[2]}
    for y, row in enumerate(CHISELED):
        for x, ch in enumerate(row):
            if ch == ".":
                img[y, x] = STONE[3 + (1 if n[y, x] > 0.55 else 0)]
            else:
                img[y, x] = mapping[ch]
    return img


def pillar_side():
    n = value_noise(16, 16, 91, scale=2, octaves=2)
    img = canvas()
    flute = [1, 4, 5, 4, 3, 2, 4, 5, 4, 3, 2, 4, 5, 4, 3, 1]
    for y in range(16):
        for x in range(16):
            t = flute[x] + (1 if n[y, x] > 0.6 else 0) - (1 if n[y, x] < 0.35 else 0)
            img[y, x] = STONE[int(np.clip(t, 0, 6))]
    # Capital and base rings
    for x in range(16):
        img[0, x] = STONE[6]
        img[1, x] = STONE[1]
        img[14, x] = STONE[5]
        img[15, x] = STONE[0]
    for x in (0, 15):
        for y in range(16):
            img[y, x] = STONE[0]
    return img


def pillar_top():
    img = canvas(fill=STONE[2])
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - 7.5, y - 7.5)
            if d > 7.2:
                img[y, x] = STONE[0]
            elif d > 6.2:
                img[y, x] = STONE[5]
            elif d > 5.2:
                img[y, x] = STONE[2]
            elif d > 3.6:
                img[y, x] = STONE[4]
            elif d > 2.4:
                img[y, x] = STONE[1]
            else:
                img[y, x] = STONE[3]
    for x, y in ((7, 7), (8, 8)):
        img[y, x] = VIOLET[2]
    return img


GILDED_BAND = [
    "1222222222222221",
    "2455445544554452",
    "1333333333333331",
]


def gilded_bricks():
    img = void_bricks(55, star_count=1)
    gold = {"1": GOLD[1], "2": GOLD[2], "3": GOLD[3], "4": GOLD[4], "5": GOLD[5]}
    for i, row in enumerate(GILDED_BAND):
        for x, ch in enumerate(row):
            img[i, x] = gold[ch]
            img[13 + i, x] = gold[ch]
    img[3, :] = MORTAR
    img[12, :] = MORTAR
    # A gold diamond rivet in the centre course.
    for x, y, c in ((7, 6, GOLD[5]), (8, 6, GOLD[4]), (7, 7, GOLD[4]), (8, 7, GOLD[3]), (7, 8, GOLD[3]), (8, 8, GOLD[2]),
                    (6, 7, GOLD[3]), (9, 7, GOLD[2])):
        img[y, x] = c
    return img


# ---------------------------------------------------------------------------------------------------------------------
# Runes
# ---------------------------------------------------------------------------------------------------------------------

def runic_base():
    n = value_noise(16, 16, 404, scale=3, octaves=3)
    img = canvas()
    for y in range(16):
        for x in range(16):
            t = 2 + (1 if n[y, x] > 0.58 else 0) - (1 if n[y, x] < 0.38 else 0)
            img[y, x] = STONE[t]
    for i in range(16):
        img[0, i] = STONE[5]
        img[i, 0] = STONE[5]
        img[15, i] = STONE[0]
        img[i, 15] = STONE[0]
        if 1 <= i <= 14:
            img[1, i] = STONE[4]
            img[i, 1] = STONE[4]
            img[14, i] = STONE[1]
            img[i, 14] = STONE[1]
    return img


# '#': rune stroke, '*': hot core of the stroke. Each glyph sits inside the carved frame.
GLYPHS = [
    [  # Aeth - the eye of the void
        "................",
        "................",
        "................",
        "......####......",
        ".....#....#.....",
        "....#..##..#....",
        "...#..#**#..#...",
        "...#..#**#..#...",
        "....#..##..#....",
        ".....#....#.....",
        "......####......",
        ".......##.......",
        "......#..#......",
        ".....#....#.....",
        "................",
        "................",
    ],
    [  # Fall - the descending star
        "................",
        "................",
        ".......##.......",
        ".......**.......",
        "....##.##.##....",
        ".....#.**.#.....",
        "......####......",
        ".......**.......",
        "...#...##...#...",
        "....#..**..#....",
        ".....#.##.#.....",
        "......#**#......",
        ".......##.......",
        "................",
        "................",
        "................",
    ],
    [  # Vor - the devouring jaw
        "................",
        "................",
        "...##########...",
        "...#........#...",
        "...#.#.##.#.#...",
        "...#.#*..*#.#...",
        "...#..#..#..#...",
        "...#...##...#...",
        "...#...**...#...",
        "...#..#..#..#...",
        "...#.#*..*#.#...",
        "...#.#.##.#.#...",
        "...#........#...",
        "...##########...",
        "................",
        "................",
    ],
    [  # Kael - the crown of stars
        "................",
        "................",
        "...#...##...#...",
        "...##..**..##...",
        "...#*#.##.#*#...",
        "...#..####..#...",
        "...#...**...#...",
        "...#########*...",
        ".......##.......",
        ".......**.......",
        ".....######.....",
        ".......##.......",
        "......#..#......",
        ".....#....#.....",
        "................",
        "................",
    ],
]


def glyph_overlay(index, intensity):
    """Cut-out emissive overlay. intensity 0..1 shifts the stroke up the violet ramp (awakened runes run hot)."""
    grid = GLYPHS[index]
    img = canvas()
    stroke = VIOLET[min(6, 3 + int(round(intensity * 2)))]
    core = GOLD[6] if intensity > 0.75 else VIOLET[min(6, 5 + int(round(intensity)))]
    halo = VIOLET[0] if intensity < 0.5 else VIOLET[1]
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            if ch == "#":
                img[y, x] = stroke
            elif ch == "*":
                img[y, x] = core
    # Halo: one pixel of dim violet around every stroke, so the rune reads as light pooling in a carving.
    lit = img[:, :, 3] > 0
    for y in range(16):
        for x in range(16):
            if lit[y, x] or x in (0, 1, 14, 15) or y in (0, 1, 14, 15):
                continue
            if any(lit[min(15, max(0, y + dy)), min(15, max(0, x + dx))] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                img[y, x] = halo
    return img


def awakened_overlay(index):
    """Pulsing animation: 8 frames, interpolated by the game."""
    curve = [0.55, 0.7, 0.85, 1.0, 1.0, 0.85, 0.7, 0.55]
    return stack_frames([glyph_overlay(index, t) for t in curve])


# ---------------------------------------------------------------------------------------------------------------------
# Crystal and scales
# ---------------------------------------------------------------------------------------------------------------------

def crystal_block():
    rng = np.random.default_rng(1203)
    points = [(rng.uniform(0, 16), rng.uniform(0, 16)) for _ in range(9)]
    tones = [int(rng.integers(0, 3)) for _ in points]
    img = canvas()
    for y in range(16):
        for x in range(16):
            dists = []
            for (px, py) in points:
                dx = min(abs(x - px), 16 - abs(x - px))
                dy = min(abs(y - py), 16 - abs(y - py))
                dists.append(math.hypot(dx, dy))
            order = np.argsort(dists)
            nearest, second = dists[order[0]], dists[order[1]]
            tone = tones[order[0]]
            if second - nearest < 0.9:
                tone = min(5, tone + 3)  # facet edge catches the light
            # Facets are lit from the top-left.
            tone += 1 if (x + y) < 10 and tone < 3 else 0
            img[y, x] = VIOLET[int(np.clip(tone, 0, 6))]
    for x, y in ((3, 4), (11, 2), (13, 11), (6, 12)):
        img[y, x] = STAR
    return img


CLUSTER = [
    "................",
    "........#.......",
    ".......#*#......",
    "..#....#*#......",
    "..##...#*#...#..",
    "..#*#..#*#..##..",
    "...#*#.#*#.#*#..",
    "...#*#.#*#.#*#..",
    "....#*##*#.#*#..",
    ".#...#*#*##*#...",
    ".##..#*#*#*#..#.",
    "..#*#.#*#*#..#*.",
    "...#*##*#*#.#*#.",
    "....#*#*#*##*#..",
    ".....######*#...",
    "....gGGGGGGGg...",
]


def crystal_cluster():
    rng = np.random.default_rng(88)
    img = canvas()
    for y, row in enumerate(CLUSTER):
        for x, ch in enumerate(row):
            if ch == "#":
                img[y, x] = VIOLET[2 + int(rng.integers(0, 2))]
            elif ch == "*":
                img[y, x] = VIOLET[5] if y < 6 else VIOLET[4]
            elif ch == "g":
                img[y, x] = GOLD[2]
            elif ch == "G":
                img[y, x] = GOLD[4]
    # Star-white tips
    for x, y in ((8, 1), (2, 3), (13, 4), (1, 9), (14, 10)):
        img[y, x] = STAR
    return img


def nebula_pixel(n, x, y, rng):
    t = n[y, x]
    c = NEBULA[int(np.clip(t * len(NEBULA), 0, len(NEBULA) - 1))]
    return c


def void_scale_block():
    n = value_noise(16, 16, 515, scale=3, octaves=3)
    rng = np.random.default_rng(516)
    img = canvas()
    for y in range(16):
        for x in range(16):
            img[y, x] = nebula_pixel(n, x, y, rng)
    # Fish-scale tiling: each scale is the lower half of an 8x8 disc. Rows are painted top to bottom, so every
    # row overlaps the one above it, exactly like real scales. Staggered by half a scale; tiles seamlessly.
    for row in range(-1, 5):
        cy = row * 4 - 0.5
        offset = 0 if row % 2 == 0 else 4
        for col in range(-1, 3):
            cx = col * 8 + offset + 3.5
            for y in range(int(math.floor(cy)), int(math.ceil(cy + 5))):
                for x in range(int(cx - 4), int(cx + 5)):
                    dx = (x - cx) / 4.0
                    dy = (y - cy) / 4.5
                    if dy < 0 or dx * dx + dy * dy > 1.0:
                        continue
                    d = math.sqrt(dx * dx + dy * dy)
                    px, py = x % 16, y % 16
                    if d > 0.8:
                        c = GOLD[3] if dx < -0.2 else (GOLD[2] if dx < 0.4 else GOLD[1])
                    elif d > 0.62:
                        c = NEBULA[0]
                    else:
                        c = nebula_pixel(n, px, py, rng)
                        if d < 0.35 and dx < 0:
                            c = NEBULA[3]
                    img[py, px] = c
    for x, y in ((2, 1), (10, 5), (5, 9), (13, 13), (9, 14)):
        if img[y, x][0] < 120:
            img[y, x] = STAR if (x + y) % 3 else VIOLET[5]
    return img


# ---------------------------------------------------------------------------------------------------------------------
# Items
# ---------------------------------------------------------------------------------------------------------------------

SHARD = [
    "................",
    "............##..",
    "...........#*#..",
    "..........#**#..",
    ".........#**#...",
    "........#**#....",
    ".......#*##.....",
    "......#*##......",
    ".....#*##.......",
    "....#*##........",
    "...#*##.........",
    "...###..........",
    "..#g#...........",
    "..gg............",
    "................",
    "................",
]


def crystal_shard():
    img = from_grid(SHARD, {"#": VIOLET[2], "*": VIOLET[4], "g": GOLD[3]})
    img[2, 12] = STAR
    img[5, 10] = VIOLET[6]
    return img


SCALE = [
    "................",
    "......gggg......",
    "....ggnnnngg....",
    "...gnnnnnnnng...",
    "..gnnnnnnnnnng..",
    "..gnnnnnnnnnng..",
    ".gnnnnnnnnnnnng.",
    ".gnnnnnnnnnnnng.",
    ".gnnnnnnnnnnnng.",
    "..gnnnnnnnnnng..",
    "..gnnnnnnnnnng..",
    "...gnnnnnnnng...",
    "....gnnnnnng....",
    ".....ggnngg.....",
    ".......gg.......",
    "................",
]


def void_scale():
    n = value_noise(16, 16, 2024, scale=2, octaves=3)
    rng = np.random.default_rng(2025)
    img = canvas()
    for y, row in enumerate(SCALE):
        for x, ch in enumerate(row):
            if ch == "g":
                img[y, x] = GOLD[4] if y < 6 or x < 5 else GOLD[2]
            elif ch == "n":
                img[y, x] = nebula_pixel(n, x, y, rng)
    # Inner gold ridge and starfield
    for x, y in ((5, 4), (10, 6), (4, 8), (9, 10), (11, 3)):
        img[y, x] = STAR
    img[6, 5] = VIOLET[5]
    img[8, 10] = VIOLET[4]
    return img


CORE_CAGE = [
    "................",
    ".......gg.......",
    "....g..gg..g....",
    "....gg.gg.gg....",
    "...g.oooooo.g...",
    "...goooooooog...",
    "..g.oooooooo.g..",
    "..ggoooooooogg..",
    "..g.oooooooo.g..",
    "...goooooooog...",
    "...g.oooooo.g...",
    "....gg.gg.gg....",
    "....g..gg..g....",
    "......gGGg......",
    ".....gGGGGg.....",
    "................",
]


def core_frame(pulse):
    img = canvas()
    for y, row in enumerate(CORE_CAGE):
        for x, ch in enumerate(row):
            if ch == "g":
                img[y, x] = GOLD[4] if (x + y) % 3 else GOLD[3]
            elif ch == "G":
                img[y, x] = GOLD[2]
            elif ch == "o":
                d = math.hypot(x - 7.5, y - 7.5) / 4.3
                heat = (1.0 - d) * (0.75 + 0.25 * pulse)
                if heat > 0.72:
                    img[y, x] = GOLD[6] if pulse > 0.6 else VIOLET[6]
                elif heat > 0.5:
                    img[y, x] = VIOLET[5]
                elif heat > 0.3:
                    img[y, x] = VIOLET[4]
                elif heat > 0.12:
                    img[y, x] = VIOLET[3]
                else:
                    img[y, x] = VIOLET[2]
    # Rim highlight on the cage
    img[1, 7] = GOLD[6]
    img[4, 3] = GOLD[5]
    return img


def worlds_core():
    curve = [0.0, 0.25, 0.5, 0.75, 1.0, 0.75, 0.5, 0.25]
    return stack_frames([core_frame(p) for p in curve])


SIGIL = [
    "................",
    ".....gggggg.....",
    "...ggGGGGGGgg...",
    "..gGG......GGg..",
    "..gG..vvvv..Gg..",
    ".gG..vVVVVv..Gg.",
    ".gG.vVVrrVVv.Gg.",
    ".gG.vVrRRrVv.Gg.",
    ".gG.vVrRRrVv.Gg.",
    ".gG.vVVrrVVv.Gg.",
    ".gG..vVVVVv..Gg.",
    "..gG..vvvv..Gg..",
    "..gGG......GGg..",
    "...ggGGGGGGgg...",
    ".....gggggg.....",
    "................",
]


def void_sigil():
    img = from_grid(SIGIL, {"g": GOLD[2], "G": GOLD[4], "v": VIOLET[2], "V": VIOLET[3], "r": VIOLET[5], "R": GOLD[6]})
    # Rune ticks engraved into the gold ring at the cardinal points
    for x, y in ((7, 3), (8, 3), (3, 7), (3, 8), (12, 7), (12, 8), (7, 12), (8, 12)):
        img[y, x] = VIOLET[4]
    img[2, 6] = GOLD[6]
    img[3, 4] = GOLD[5]
    return img


def music_disc():
    img = canvas()
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - 7.5, y - 7.5)
            if d > 7.4:
                continue
            if d > 6.6:
                img[y, x] = hx("0d0716")
            elif d > 3.4:
                groove = int(d * 2) % 2
                img[y, x] = hx("1a1028") if groove else hx("231536")
            elif d > 2.4:
                img[y, x] = GOLD[3]
            elif d > 1.0:
                img[y, x] = VIOLET[3]
            else:
                img[y, x] = hx("0d0716")
    # Light sheen along one quadrant
    for x, y in ((4, 3), (3, 4), (5, 2), (2, 5)):
        img[y, x] = hx("4b3366")
    img[6, 6] = VIOLET[5]
    return img


def main():
    save(void_bricks(11), "block/void_stone_bricks.png")
    save(void_bricks(12, crack=True), "block/cracked_void_stone_bricks.png")
    save(chiseled_bricks(), "block/chiseled_void_stone_bricks.png")
    save(pillar_side(), "block/void_stone_pillar.png")
    save(pillar_top(), "block/void_stone_pillar_top.png")
    save(gilded_bricks(), "block/gilded_void_bricks.png")
    save(runic_base(), "block/runic_void_stone.png")
    for i in range(len(GLYPHS)):
        save(glyph_overlay(i, 0.0), f"block/runic_void_stone_glyph_{i}.png")
        save(awakened_overlay(i), f"block/runic_void_stone_glyph_{i}_awakened.png", frametime=3, interpolate=True)
    save(crystal_block(), "block/void_crystal_block.png")
    save(crystal_cluster(), "block/void_crystal_cluster.png")
    save(void_scale_block(), "block/void_scale_block.png")

    save(crystal_shard(), "item/void_crystal_shard.png")
    save(void_scale(), "item/void_scale.png")
    save(worlds_core(), "item/world_eaters_core.png", frametime=2, interpolate=True)
    save(void_sigil(), "item/void_sigil.png")
    save(music_disc(), "item/music_disc_world_eater.png")
    print("textures written to", TEX)


if __name__ == "__main__":
    main()
