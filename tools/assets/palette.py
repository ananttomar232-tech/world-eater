"""Shared Aetherfall palette and pixel helpers.

Colours are sampled from the reference concept art: void-black stone with a violet cast,
burning violet rune light, star-white sparkles and warm forged gold.
"""
import numpy as np


def hx(code: str, a: int = 255):
    code = code.lstrip("#")
    return (int(code[0:2], 16), int(code[2:4], 16), int(code[4:6], 16), a)


CLEAR = (0, 0, 0, 0)

# Void stone (masonry), darkest to lightest
STONE = [hx("0b0811"), hx("140f1c"), hx("1c1626"), hx("251e31"), hx("2f273d"), hx("3a3149"), hx("473c58")]
MORTAR = hx("07050b")

# Violet energy, darkest to brightest
VIOLET = [hx("2a0b4a"), hx("4a1380"), hx("6d1fb8"), hx("9333ea"), hx("b45cff"), hx("d39bff"), hx("f1dcff")]

# Forged gold, darkest to brightest
GOLD = [hx("3d2106"), hx("6b3f10"), hx("a3661c"), hx("d69a2d"), hx("f2c14e"), hx("ffe08a"), hx("fff6d6")]

# Starfield
STAR = hx("fbf3ff")
NEBULA = [hx("120624"), hx("1f0a3d"), hx("341063"), hx("501a8c")]


def canvas(w=16, h=16, fill=CLEAR):
    img = np.zeros((h, w, 4), dtype=np.uint8)
    img[:, :] = fill
    return img


def value_noise(w, h, seed, scale=4.0, octaves=3):
    """Tileable smooth value noise in [0, 1]."""
    rng = np.random.default_rng(seed)
    out = np.zeros((h, w))
    amp_total = 0.0
    for o in range(octaves):
        cells = max(1, int(scale * (2 ** o)))
        grid = rng.random((cells, cells))
        ys = np.arange(h) / h * cells
        xs = np.arange(w) / w * cells
        y0 = np.floor(ys).astype(int)
        x0 = np.floor(xs).astype(int)
        fy = ys - y0
        fx = xs - x0
        fy = fy * fy * (3 - 2 * fy)
        fx = fx * fx * (3 - 2 * fx)
        y1 = (y0 + 1) % cells
        x1 = (x0 + 1) % cells
        y0 %= cells
        x0 %= cells
        a = grid[np.ix_(y0, x0)]
        b = grid[np.ix_(y0, x1)]
        c = grid[np.ix_(y1, x0)]
        d = grid[np.ix_(y1, x1)]
        top = a + (b - a) * fx[None, :]
        bot = c + (d - c) * fx[None, :]
        layer = top + (bot - top) * fy[:, None]
        amp = 0.5 ** o
        out += layer * amp
        amp_total += amp
    return out / amp_total


def ramp(colors, t):
    """Pick from a colour ramp with t in [0, 1]."""
    t = min(max(t, 0.0), 0.9999)
    return colors[int(t * len(colors))]


def put(img, x, y, color):
    h, w = img.shape[:2]
    if 0 <= x < w and 0 <= y < h:
        img[y, x] = color


def blend(img, x, y, color, alpha):
    h, w = img.shape[:2]
    if 0 <= x < w and 0 <= y < h:
        base = img[y, x].astype(float)
        c = np.array(color, dtype=float)
        mixed = base * (1 - alpha) + c * alpha
        mixed[3] = max(base[3], c[3] * alpha) if base[3] < 255 else 255
        img[y, x] = mixed.astype(np.uint8)


def from_grid(rows, mapping, w=16, h=16):
    """Build an image from a list of strings. Each char maps to a colour (or is transparent)."""
    img = canvas(w, h)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in mapping:
                img[y, x] = mapping[ch]
    return img
