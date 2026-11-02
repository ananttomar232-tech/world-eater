"""Renders aetherfall_logo.png (shown in the Forge mod list): gold title over a violet nebula and starfield."""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "src", "main", "resources", "aetherfall_logo.png")
W, H = 480, 160
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"


def main():
    rng = np.random.default_rng(3)
    yy, xx = np.mgrid[0:H, 0:W]
    neb = np.zeros((H, W, 3))
    for _ in range(7):
        cx, cy, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(40, 140)
        g = np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r * r))[..., None]
        neb += g * np.array(rng.choice([[80, 20, 140], [40, 10, 90], [120, 40, 200]]))
    base = np.clip(np.array([10, 6, 18]) + neb * 0.6, 0, 255)
    img = Image.fromarray(base.astype(np.uint8), "RGB").convert("RGBA")
    d = ImageDraw.Draw(img)
    for _ in range(140):
        x, y = rng.integers(0, W), rng.integers(0, H)
        c = int(rng.integers(150, 255))
        d.point((x, y), fill=(c, c - 20, 255, 255))

    title = ImageFont.truetype(FONT, 56)
    sub = ImageFont.truetype(FONT, 20)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.text((W // 2, 66), "AETHERFALL", font=title, anchor="mm", fill=(190, 90, 255, 255))
    glow = glow.filter(ImageFilter.GaussianBlur(7))
    img.alpha_composite(glow)

    # Gold gradient text
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).text((W // 2, 66), "AETHERFALL", font=title, anchor="mm", fill=255)
    grad = np.zeros((H, W, 4), dtype=np.uint8)
    t = np.clip((yy - 36) / 60.0, 0, 1)[..., None]
    top, bot = np.array([255, 240, 170]), np.array([200, 120, 30])
    grad[..., :3] = (top * (1 - t) + bot * t).astype(np.uint8)
    grad[..., 3] = 255
    img.paste(Image.fromarray(grad, "RGBA"), (0, 0), mask)
    outline = mask.filter(ImageFilter.MaxFilter(3))
    edge = Image.new("RGBA", (W, H), (60, 30, 5, 255))
    img.paste(edge, (0, 0), Image.fromarray(np.clip(np.array(outline, int) - np.array(mask, int), 0, 255).astype(np.uint8)))

    d = ImageDraw.Draw(img)
    d.text((W // 2, 122), "T H E   W O R L D   E A T E R", font=sub, anchor="mm", fill=(225, 190, 255, 255))
    half = d.textlength("T H E   W O R L D   E A T E R", font=sub) / 2
    for x0, x1 in ((24, W // 2 - half - 12), (W // 2 + half + 12, W - 24)):
        d.line([(x0, 122), (x1, 122)], fill=(214, 154, 45, 255), width=2)
    img.convert("RGB").save(OUT)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
