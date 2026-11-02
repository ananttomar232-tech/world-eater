"""Aetherfall, the World Eater: geometry, textures and animations for GeckoLib.

    python3 tools/model/world_eater.py
    PREVIEW_DIR=/tmp python3 tools/model/preview_world_eater.py [animation ...]

Packed at 2 texels per model unit (twice vanilla density) for scale, rune and starfield detail.

Bone hierarchy (names referenced by AetherfallModel/AetherfallRenderer and the animation file):

root
└─ body ─┬─ chest ─┬─ neck_lower ─ neck_upper ─ head ─┬─ jaw
         │         │                                   ├─ mouth (locator: Void Breath origin)
         │         │                                   └─ horn_{left,right}_1 ─ _2 ─ _3
         │         ├─ arm_{left,right} ─ forearm_ ─ hand_
         │         └─ wing_{left,right} ─ wing_*_mid ─┬─ wing_*_tip (leading finger) ─ wing_*_claw (locator)
         │                                             ├─ wing_*_finger_2
         │                                             ├─ wing_*_finger_3
         │                                             └─ wing_*_finger_4
         ├─ leg_{left,right} ─ shin_ ─ foot_
         └─ tail_1 ─ tail_2 ─ tail_3 ─ tail_4 ─ tail_5 ─ tail_6
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from geo import Cube, Model, save_png, export_animations  # noqa: E402
from materials import PAINTERS  # noqa: E402
import animations_world_eater as anims  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSETS = os.path.join(ROOT, "src", "main", "resources", "assets", "aetherfall")

# Wing finger layout (shared with the animation file): rest rotation Z of each finger relative to the forearm,
# its length, and the membrane wedge angle down to the next finger.
FINGERS = [  # (bone suffix, rest z, length, wedge angle)
    ("tip", -6, 72, 26),
    ("finger_2", 20, 64, 26),
    ("finger_3", 46, 57, 26),
    ("finger_4", 72, 48, 30),
]
ELBOW_X = 58
WRIST_X = 104


def mirror_cube(c):
    """Mirror a cube across X (left side -> right side). Textures are flipped so asymmetric panels stay correct."""
    o = [-(c.origin[0] + c.size[0]), c.origin[1], c.origin[2]]
    rot = [c.rotation[0], -c.rotation[1], -c.rotation[2]] if c.rotation else None
    piv = [-c.pivot[0], c.pivot[1], c.pivot[2]] if c.pivot else None
    mats = dict(c.materials)
    if "east" in mats or "west" in mats:
        mats["east"], mats["west"] = c.materials.get("west", c.materials.get("*")), c.materials.get("east", c.materials.get("*"))
    params = dict(c.params)
    params["flip"] = not params.get("flip", False)
    return Cube(o, c.size, mats, c.inflate, rot, piv, c.faces, c.seed + 1, **params)


def spike(x, y, z, w, h, d, rot, mat="crystal", **kw):
    return Cube([x, y, z], [w, h, d], mat, rotation=rot, pivot=[x + w / 2, y, z + d / 2], **kw)


def cluster(x, y, z, scale=1.0, lean=(0, 0, 0), seed=0):
    """A clump of 3-4 void crystals of different heights fanning out from one base, as in the reference."""
    lx, ly, lz = lean
    s = scale
    return [
        spike(x - 2 * s, y, z - 2 * s, 5 * s, 18 * s, 5 * s, [lx - 8, ly, lz], seed=seed),
        spike(x + 2 * s, y, z - 1 * s, 4 * s, 13 * s, 4 * s, [lx + 6, ly, lz - 22], seed=seed + 1),
        spike(x - 4 * s, y, z + 2 * s, 3.5 * s, 11 * s, 3.5 * s, [lx - 20, ly, lz + 18], seed=seed + 2),
        spike(x + 0.5 * s, y, z + 3 * s, 3 * s, 8 * s, 3 * s, [lx - 32, ly, lz - 6], seed=seed + 3),
    ]


def sym(bone, *cubes):
    """Adds cubes on the left side and their mirror on the right."""
    for c in cubes:
        bone.add(c, mirror_cube(c))


def build():
    m = Model("geometry.world_eater")
    m.bone("root", [0, 0, 0])

    # ---- Body: pelvis, belt, belly plates ---------------------------------------------------------------------
    body = m.bone("body", [0, 52, 6], "root")
    body.add(
        Cube([-19, 40, -8], [38, 24, 30], {"*": "scale_sheen", "north": "belly", "down": "belly"}),
        Cube([-20, 58, -9], [40, 5, 32], {"*": "gold", "north": "gold_rune"}),
        Cube([-14, 42, -10], [28, 15, 2], {"*": "gold", "north": "belly"}),
        Cube([-15, 40, -9], [30, 3, 2], "gold"),
    )

    # ---- Chest: core, sigil breastplate, rune band, collar, back hump, crystal spine -------------------------------
    chest = m.bone("chest", [0, 62, 4], "body")
    chest.add(
        Cube([-25, 62, -14], [50, 36, 34], {"*": "scale_sheen", "north": "belly"}),
        Cube([-17, 68, -18], [34, 26, 4], {"*": "gold", "north": "gold_sigil"}),
        Cube([-24, 63, -16.5], [48, 5, 3], {"*": "gold", "north": "gold_rune"}),
        Cube([-22, 94, -17], [44, 8, 15], {"*": "gold", "north": "gold_rune"}),
        Cube([-20, 88, 6], [40, 14, 22], "scale_sheen"),
        Cube([-12, 98, 4], [24, 4, 18], "gold"),
    )
    sym(chest, Cube([18, 66, -16], [8, 24, 3], {"*": "gold", "north": "gold_rune"}, rotation=[0, 14, 0], pivot=[18, 78, -16]))
    chest.add(*cluster(0, 100, 10, 1.5, (-18, 0, 0), seed=10))
    chest.add(*cluster(0, 92, 24, 0.9, (-40, 0, 0), seed=20))
    sym(chest, *cluster(9, 97, 14, 0.7, (-25, 0, -22), seed=30))

    # Pauldrons: stacked gold plates with crystal clusters, the reference's crystal-studded shoulders.
    sym(chest,
        Cube([19, 85, -13], [17, 12, 24], {"*": "gold", "north": "gold_rune"}, rotation=[0, 0, -14], pivot=[27, 91, -1]),
        Cube([22, 79, -12], [15, 7, 22], "gold", rotation=[0, 0, -14], pivot=[29, 83, -1]),
        Cube([25, 73, -11], [12, 6, 20], "gold", rotation=[0, 0, -14], pivot=[31, 76, -1]),
        *cluster(27, 96, -3, 1.45, (0, 0, -26), seed=40),
        )

    # ---- Neck -------------------------------------------------------------------------------------------------
    neck_lower = m.bone("neck_lower", [0, 94, -8], "chest", rotation=[-14, 0, 0])
    neck_lower.add(
        Cube([-11, 92, -26], [22, 20, 22], {"*": "scale_sheen", "north": "belly"}),
        Cube([-12, 101, -27], [24, 5, 24], {"*": "gold", "north": "gold_rune"}),
        spike(-2.5, 111, -14, 5, 11, 5, [-30, 0, 0]),
    )
    neck_upper = m.bone("neck_upper", [0, 108, -18], "neck_lower", rotation=[-6, 0, 0])
    neck_upper.add(
        Cube([-10, 106, -34], [20, 17, 20], {"*": "scale_sheen", "north": "belly"}),
        Cube([-11, 112, -35], [22, 4, 22], "gold"),
        spike(-2, 122, -24, 4, 9, 4, [-35, 0, 0]),
    )

    # ---- Head: crowned skull, tiered snout, brow ridges, glowing eyes, cheek frills, teeth, swept gold horns -----
    head = m.bone("head", [0, 116, -30], "neck_upper", rotation=[14, 0, 0])
    head.add(
        Cube([-13, 110, -56], [26, 21, 28], "scale_sheen"),
        Cube([-14, 125, -57], [28, 7, 26], {"*": "gold", "north": "gold_rune"}),
        Cube([-5, 126, -58.5], [10, 11, 2], {"*": "gold", "north": "gold_sigil"}),
        Cube([-10, 110, -79], [20, 12, 24], {"*": "scale_sheen", "down": "mouth"}),
        Cube([-8, 122, -76], [16, 4, 22], "scale_sheen"),
        Cube([-6, 125, -74], [12, 2, 19], "gold"),
        Cube([-10.5, 111, -80], [21, 11, 2], "gold"),
        Cube([-6, 118, -80.6], [3, 2, 1], "eye"),
        Cube([3, 118, -80.6], [3, 2, 1], "eye"),
        Cube([-9.5, 107.5, -79.5], [19, 3, 23], {"north": "teeth", "east": "teeth", "west": "teeth"}),
        spike(-2.5, 132, -52, 5, 12, 5, [-18, 0, 0]),
        spike(-2, 131, -43, 4, 9, 4, [-36, 0, 0]),
        spike(-1.5, 128, -34, 3, 7, 3, [-50, 0, 0]),
    )
    sym(head,
        Cube([-14, 121, -58.5], [10, 4, 7], "gold", rotation=[0, 0, 10], pivot=[-9, 123, -55]),
        Cube([9.5, 115.5, -58.2], [7, 5, 2], "eye"),
        spike(12, 120.5, -58, 3, 6, 3, [-30, 0, -35], "crystal"),
        Cube([12.5, 109, -56], [3, 15, 22], {"*": "gold", "east": "gold_rune", "west": "gold_rune"}),
        Cube([9.5, 110, -79.5], [2, 12, 18], "gold"),
        spike(13, 113, -40, 3, 11, 3, [30, 0, -60], "horn", heat=0.7),
        spike(12, 118, -46, 3, 9, 3, [20, 0, -55], "horn", heat=0.6),
        spike(6, 120, -76, 2, 5, 2, [-20, 0, -30], "crystal"),
        )
    for side, sx in (("left", 1), ("right", -1)):
        def c(o, s, mat, **kw):
            cube = Cube(o, s, mat, **kw)
            return cube if sx > 0 else mirror_cube(cube)
        # Horns rise from outside the crown, sweep up and back, and splay outward.
        h1 = m.bone(f"horn_{side}_1", [16 * sx, 128, -44], "head", rotation=[40, 24 * sx, 0])
        h1.add(c([12.5, 124.5, -44], [7, 7, 18], "horn", heat=0.25))
        h2 = m.bone(f"horn_{side}_2", [16 * sx, 128, -27], f"horn_{side}_1", rotation=[14, 8 * sx, 0])
        h2.add(c([13, 125, -27], [6, 6, 17], "horn", heat=0.55))
        h3 = m.bone(f"horn_{side}_3", [16 * sx, 128, -11], f"horn_{side}_2", rotation=[12, 8 * sx, 0])
        h3.add(c([13.5, 125.5, -11], [5, 5, 15], "horn", heat=0.95))

    # The jaw rests slightly open so the glowing maw and both rows of teeth always read, as in the reference.
    jaw = m.bone("jaw", [0, 112, -52], "head", rotation=[12, 0, 0])
    jaw.add(
        Cube([-9, 104, -78], [18, 8, 24], {"*": "scale_sheen", "up": "mouth", "down": "belly"}),
        Cube([-8.5, 111, -77.5], [17, 3, 22], {"north": "teeth_up", "east": "teeth_up", "west": "teeth_up"}),
        Cube([-8, 103.5, -72], [16, 3, 14], {"*": "gold", "north": "gold_rune"}),
    )
    m.bone("mouth", [0, 113, -80], "head")

    for side, sx in (("left", 1), ("right", -1)):
        def c(o, s, mat, **kw):
            cube = Cube(o, s, mat, **kw)
            return cube if sx > 0 else mirror_cube(cube)

        def sp(*a, **kw):
            cube = spike(*a, **kw)
            return cube if sx > 0 else mirror_cube(cube)

        # ---- Arms --------------------------------------------------------------------------------------------
        arm = m.bone(f"arm_{side}", [26 * sx, 90, -4], "chest", rotation=[-14, 0, -12 * sx])
        arm.add(c([22, 66, -11], [14, 26, 14], "scale_sheen"))
        fore = m.bone(f"forearm_{side}", [29 * sx, 68, -4], f"arm_{side}", rotation=[-60, 0, 0])
        fore.add(
            c([23, 44, -10], [12, 25, 12], "scale_sheen"),
            c([22.5, 48, -10.5], [13, 14, 13], {"*": "gold", "north": "gold_rune", "east": "gold_rune", "west": "gold_rune"}),
            sp(27, 62, 1, 3, 10, 3, [-40, 0, 0]),
            sp(24, 58, 2, 2.5, 7, 2.5, [-30, 0, 15]),
        )
        hand = m.bone(f"hand_{side}", [29 * sx, 46, -4], f"forearm_{side}")
        hand.add(
            c([22.5, 38, -11], [13, 8, 14], "scale_sheen"),
            c([22, 44, -11.5], [14, 3, 15], "gold"),
            c([23, 28, -11], [3, 10, 3], "claw"),
            c([26.5, 27, -12], [3, 11, 3], "claw"),
            c([30, 28, -11], [3, 10, 3], "claw"),
            c([22, 31, -4], [3, 8, 3], "claw"),
        )

        # ---- Legs --------------------------------------------------------------------------------------------
        leg = m.bone(f"leg_{side}", [15 * sx, 50, 4], "body")
        leg.add(
            c([7, 30, -7], [19, 26, 22], "scale_sheen"),
            c([6.5, 34, -8], [20, 14, 3], {"*": "gold", "north": "gold_rune"}),
            c([25.5, 38, -4], [2, 12, 16], "gold"),
        )
        shin = m.bone(f"shin_{side}", [16 * sx, 32, 10], f"leg_{side}", rotation=[28, 0, 0])
        shin.add(
            c([10, 8, 4], [13, 26, 13], "scale_sheen"),
            c([9.5, 12, 3.5], [14, 6, 14], "gold"),
            sp(14.5, 18, 16, 3, 11, 3, [-40, 0, 0]),
        )
        foot = m.bone(f"foot_{side}", [16 * sx, 10, 10], f"shin_{side}", rotation=[-28, 0, 0])
        foot.add(
            c([7, 0, -12], [19, 10, 26], {"*": "scale_sheen", "down": "belly"}),
            c([6.5, 8, -12.5], [20, 3, 12], "gold"),
            c([7.5, 0, -19], [4, 6, 8], "claw", tip="top"),
            c([14.5, 0, -20], [4, 7, 9], "claw", tip="top"),
            c([21.5, 0, -19], [4, 6, 8], "claw", tip="top"),
        )

        # ---- Wings: gold humerus and forearm, four fanned finger spars, nebula wedges between them ------------
        wing = m.bone(f"wing_{side}", [18 * sx, 92, 16], "chest", rotation=[0, -10 * sx, -22 * sx])
        wing.add(
            c([18, 88.5, 12.5], [ELBOW_X - 18, 7, 7], "wing_bone"),
            c([10, 26, 16], [ELBOW_X - 10, 64, 0], "membrane", faces=["north"], scallop=2),
            sp(26, 95, 14, 3, 7, 3, [0, 0, -20], "horn", heat=0.6),
            sp(38, 95, 14, 3, 8, 3, [0, 0, -20], "horn", heat=0.6),
            sp(50, 95, 14, 3, 7, 3, [0, 0, -20], "horn", heat=0.6),
        )
        mid = m.bone(f"wing_{side}_mid", [ELBOW_X * sx, 92, 16], f"wing_{side}", rotation=[0, 0, -28 * sx])
        mid.add(
            c([ELBOW_X, 89, 13], [WRIST_X - ELBOW_X, 6, 6], "wing_bone"),
            c([ELBOW_X - 16, 20, 16.3], [WRIST_X - ELBOW_X + 20, 72, 0], "membrane", faces=["north"], scallop=3),
            c([ELBOW_X - 4, 88, 11], [8, 9, 10], "gold"),
            sp(ELBOW_X - 1, 97, 13, 3, 9, 3, [0, 0, -20], "horn", heat=0.8),
            c([WRIST_X - 4, 88.5, 12.5], [8, 7, 7], "gold"),
        )
        for i, (suffix, rest_z, length, angle) in enumerate(FINGERS):
            bone = m.bone(f"wing_{side}_{suffix}", [WRIST_X * sx, 92, 16], f"wing_{side}_mid", rotation=[0, 0, rest_z * sx])
            thick = 4 if i == 0 else 3
            height = math.ceil(length * math.sin(math.radians(angle)) + 2)
            bone.add(
                c([WRIST_X, 92 - thick / 2, 16 - thick / 2], [length, thick, thick], "wing_bone"),
                c([WRIST_X, 92 - height, 16.6 + 0.3 * i], [length, height, 0], "membrane", faces=["north"],
                  shape="wedge", angle=angle, seed=50 + i),
            )
            if i == 0:
                bone.add(c([WRIST_X + length, 89.5, 13.5], [12, 5, 5], "horn", heat=1.0))
                m.bone(f"wing_{side}_claw", [(WRIST_X + length + 12) * sx, 92, 16], f"wing_{side}_tip")
            else:
                bone.add(c([WRIST_X + length - 1, 90.5, 14.5], [6, 3, 3], "horn", heat=0.9))

    # ---- Tail: six tapering segments, crystal crest, crystal blade tip ----------------------------------------
    segments = [  # (pivot y, pivot z, rest x, origin, size, crystal)
        (50, 22, 12, [-13, 40, 20], [26, 20, 30], (6, 13)),
        (48, 49, 6, [-10, 40, 48], [20, 16, 28], (5, 11)),
        (46, 75, -4, [-8, 40, 74], [16, 13, 26], (4, 9)),
        (45, 99, -6, [-6, 40, 98], [12, 10, 24], (3.5, 8)),
        (44, 121, -6, [-4.5, 40, 120], [9, 8, 22], (3, 7)),
        (43, 141, -4, [-3, 41, 141], [6, 6, 16], (2.5, 6)),
    ]
    parent = "body"
    for i, (py, pz, rx, o, s, (cw, ch)) in enumerate(segments, start=1):
        t = m.bone(f"tail_{i}", [0, py, pz], parent, rotation=[rx, 0, 0])
        top = o[1] + s[1]
        t.add(Cube(o, s, {"*": "scale_sheen", "down": "belly"}))
        t.add(spike(-cw / 2, top - 1, o[2] + 4, cw, ch, cw, [-42, 0, 0], seed=60 + i))
        if s[2] > 20:
            t.add(spike(-cw / 2.5, top - 1, o[2] + s[2] * 0.55, cw * 0.8, ch * 0.8, cw * 0.8, [-46, 0, 0], seed=70 + i))
        if i == 3:
            t.add(Cube([o[0] - 0.5, o[1] - 0.5, o[2] + 10], [s[0] + 1, s[1] + 1, 3], {"*": "gold", "north": "gold_rune"}))
        parent = f"tail_{i}"
    tip = m.by_name["tail_6"]
    tip.add(
        Cube([-1, 34, 150], [2, 22, 20], "crystal"),
        Cube([-8, 42, 152], [16, 2, 14], "crystal"),
        spike(-2, 48, 154, 4, 12, 4, [-55, 0, 0], seed=80),
    )
    return m


def main():
    model = build()
    model.pack(1024, density=2)
    base, glow = model.paint(PAINTERS)
    model.export_geo(os.path.join(ASSETS, "geo", "entity", "world_eater.geo.json"), 28, 18, 8)
    save_png(base, os.path.join(ASSETS, "textures", "entity", "world_eater.png"))
    save_png(glow, os.path.join(ASSETS, "textures", "entity", "world_eater_glow.png"))
    export_animations(os.path.join(ASSETS, "animations", "entity", "world_eater.animation.json"), anims.build())
    cubes = sum(len(b.cubes) for b in model.bones)
    print(f"world_eater: {len(model.bones)} bones, {cubes} cubes, texture {model.tex_w}x{model.tex_h}")
    return model, base, glow


if __name__ == "__main__":
    main()
