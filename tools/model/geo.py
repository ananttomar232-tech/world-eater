"""Tiny model toolkit for GeckoLib (Bedrock geometry 1.12.0).

Models are authored in Bedrock/Blockbench space: 16 units per block, +Y up, the creature faces -Z (north).
Every cube uses per-face UVs, packed automatically into one atlas, and every face is painted by a material
function, producing a base texture and a matching emissive glowmask (GeckoLib's AutoGlowingGeoLayer reads
`<texture>_glowmask.png`).
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "assets"))

FACES = ("north", "south", "east", "west", "up", "down")


class Cube:
    def __init__(self, origin, size, material, inflate=0.0, rotation=None, pivot=None, faces=None, seed=0, **params):
        self.origin = [float(v) for v in origin]
        self.size = [float(v) for v in size]
        self.inflate = inflate
        self.rotation = rotation
        self.pivot = pivot
        self.seed = seed
        self.params = params
        # material: str for all faces, or dict face -> material (missing faces fall back to "*" or are omitted)
        if isinstance(material, str):
            material = {"*": material}
        self.materials = material
        self.faces = faces  # explicit face list or None = all faces with non-zero area
        self.uv = {}

    def face_size(self, face):
        x, y, z = self.size
        return {"north": (x, y), "south": (x, y), "east": (z, y), "west": (z, y), "up": (x, z), "down": (x, z)}[face]

    def active_faces(self):
        out = []
        for face in self.faces or FACES:
            w, h = self.face_size(face)
            if w <= 0 or h <= 0:
                continue
            if face not in self.materials and "*" not in self.materials:
                continue
            out.append(face)
        return out

    def material(self, face):
        return self.materials.get(face, self.materials.get("*"))


class Bone:
    def __init__(self, name, pivot, parent=None, rotation=None, cubes=None):
        self.name = name
        self.pivot = [float(v) for v in pivot]
        self.parent = parent
        self.rotation = rotation
        self.cubes = cubes or []

    def add(self, *cubes):
        self.cubes.extend(cubes)
        return self


class Model:
    def __init__(self, identifier):
        self.identifier = identifier
        self.bones = []
        self.by_name = {}

    def bone(self, name, pivot, parent=None, rotation=None):
        b = Bone(name, pivot, parent, rotation)
        self.bones.append(b)
        self.by_name[name] = b
        return b

    # -------------------------------------------------------------------------------------------------------------
    # Atlas packing (shelf packer, tallest first). Faces of 1 px or more, rounded up to whole texels.
    # -------------------------------------------------------------------------------------------------------------
    def pack(self, width):
        rects = []
        for bone in self.bones:
            for cube in bone.cubes:
                for face in cube.active_faces():
                    w, h = cube.face_size(face)
                    rects.append((max(1, math.ceil(w)), max(1, math.ceil(h)), cube, face))
        rects.sort(key=lambda r: (-r[1], -r[0]))
        x = y = shelf = 0
        pad = 1
        for w, h, cube, face in rects:
            if w + pad > width:
                raise ValueError(f"face {w}x{h} wider than atlas")
            if x + w + pad > width:
                x = 0
                y += shelf + pad
                shelf = 0
            cube.uv[face] = (x, y, w, h)
            x += w + pad
            shelf = max(shelf, h)
        height = y + shelf + pad
        self.tex_w = width
        self.tex_h = 1 << (height - 1).bit_length()
        return self.tex_w, self.tex_h

    # -------------------------------------------------------------------------------------------------------------
    def paint(self, painters):
        base = np.zeros((self.tex_h, self.tex_w, 4), dtype=np.uint8)
        glow = np.zeros((self.tex_h, self.tex_w, 4), dtype=np.uint8)
        for bone in self.bones:
            for ci, cube in enumerate(bone.cubes):
                for face, (u, v, w, h) in cube.uv.items():
                    mat = cube.material(face)
                    fn = painters[mat]
                    seed = hash((bone.name, ci, face, cube.seed)) & 0xFFFFFFF
                    b, g = fn(w, h, face, seed, cube.params)
                    base[v:v + h, u:u + w] = b
                    if g is not None:
                        glow[v:v + h, u:u + w] = g
        return base, self.premultiply_glow(glow)

    @staticmethod
    def premultiply_glow(glow):
        """The glow texture is drawn by EmissiveGlowLayer with the additive, full-bright `eyes` render type, so only
        RGB matters: premultiply by the authored alpha (soft glows become dimmer additions) and make the result opaque
        where it emits anything. The base texture is never modified."""
        a = glow[..., 3:4].astype(float) / 255.0
        rgb = (glow[..., :3].astype(float) * a).round().astype(np.uint8)
        out = np.zeros_like(glow)
        out[..., :3] = rgb
        out[..., 3] = np.where(rgb.max(axis=-1) > 0, 255, 0)
        return out

    # -------------------------------------------------------------------------------------------------------------
    def export_geo(self, path, visible_w, visible_h, visible_y):
        bones = []
        for bone in self.bones:
            entry = {"name": bone.name, "pivot": bone.pivot}
            if bone.parent:
                entry["parent"] = bone.parent
            if bone.rotation:
                entry["rotation"] = bone.rotation
            cubes = []
            for cube in bone.cubes:
                c = {"origin": cube.origin, "size": cube.size, "uv": {}}
                if cube.inflate:
                    c["inflate"] = cube.inflate
                if cube.rotation:
                    c["rotation"] = cube.rotation
                    c["pivot"] = cube.pivot or [cube.origin[i] + cube.size[i] / 2 for i in range(3)]
                for face, (u, v, w, h) in cube.uv.items():
                    fw, fh = cube.face_size(face)
                    c["uv"][face] = {"uv": [u, v], "uv_size": [fw, fh]}
                cubes.append(c)
            if cubes:
                entry["cubes"] = cubes
            bones.append(entry)
        doc = {
            "format_version": "1.12.0",
            "minecraft:geometry": [{
                "description": {
                    "identifier": self.identifier,
                    "texture_width": self.tex_w,
                    "texture_height": self.tex_h,
                    "visible_bounds_width": visible_w,
                    "visible_bounds_height": visible_h,
                    "visible_bounds_offset": [0, visible_y, 0],
                },
                "bones": bones,
            }],
        }
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(doc, f, indent=1)
            f.write("\n")


# ---------------------------------------------------------------------------------------------------------------------
# Animations
# ---------------------------------------------------------------------------------------------------------------------

class Animation:
    """keys[bone][channel] = list of (time_s, (x, y, z), easing)."""

    def __init__(self, name, length, loop):
        self.name = name
        self.length = length
        self.loop = loop  # True, False or "hold_on_last_frame"
        self.keys = {}

    def key(self, bone, channel, time, vec, easing="easeInOutSine"):
        self.keys.setdefault(bone, {}).setdefault(channel, []).append((round(time, 4), tuple(float(v) for v in vec), easing))
        return self

    def rot(self, bone, *frames, easing="easeInOutSine"):
        for t, vec in frames:
            self.key(bone, "rotation", t, vec, easing)
        return self

    def pos(self, bone, *frames, easing="easeInOutSine"):
        for t, vec in frames:
            self.key(bone, "position", t, vec, easing)
        return self

    def scale(self, bone, *frames, easing="easeInOutSine"):
        for t, vec in frames:
            self.key(bone, "scale", t, vec, easing)
        return self

    def to_json(self):
        bones = {}
        for bone, channels in self.keys.items():
            out = {}
            for channel, frames in channels.items():
                frames = sorted(frames, key=lambda f: f[0])
                out[channel] = {f"{t:g}": {"vector": list(v), "easing": e} for t, v, e in frames}
            bones[bone] = out
        doc = {"animation_length": self.length, "bones": bones}
        if self.loop:
            doc["loop"] = self.loop
        return doc

    def sample(self, bone, channel, t, default):
        """Evaluates a channel the way GeckoLib does (easing applied on the segment into each keyframe)."""
        frames = sorted(self.keys.get(bone, {}).get(channel, []), key=lambda f: f[0])
        if not frames:
            return default
        if t <= frames[0][0]:
            return frames[0][1]
        for (t0, v0, _), (t1, v1, e1) in zip(frames, frames[1:]):
            if t0 <= t <= t1:
                p = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
                p = ease(e1, p)
                return tuple(a + (b - a) * p for a, b in zip(v0, v1))
        return frames[-1][1]


def ease(name, p):
    name = name.lower()
    if name in ("linear", "none"):
        return p
    if name == "easeinoutsine":
        return -(math.cos(math.pi * p) - 1) / 2
    if name == "easeinsine":
        return 1 - math.cos(p * math.pi / 2)
    if name == "easeoutsine":
        return math.sin(p * math.pi / 2)
    if name == "easeinquad":
        return p * p
    if name == "easeoutquad":
        return 1 - (1 - p) * (1 - p)
    if name == "easeincubic":
        return p ** 3
    if name == "easeoutcubic":
        return 1 - (1 - p) ** 3
    if name == "easeoutback":
        c1 = 1.70158
        c3 = c1 + 1
        return 1 + c3 * (p - 1) ** 3 + c1 * (p - 1) ** 2
    return p


def export_animations(path, animations):
    doc = {"format_version": "1.8.0", "animations": {a.name: a.to_json() for a in animations}}
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(doc, f, indent=1)
        f.write("\n")


def save_png(img, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    Image.fromarray(img, "RGBA").save(path)
