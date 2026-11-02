"""Aetherfall, the World Eater: geometry, textures and animations for GeckoLib.

    python3 tools/model/world_eater.py            # write geo, animations, textures
    python3 tools/model/world_eater.py --preview  # also render preview sheets into the scratch dir given by $PREVIEW_DIR

Bone hierarchy (names are referenced by AetherfallModel.java and the animation file):

root
└─ body ─┬─ chest ─┬─ neck_lower ─ neck_upper ─ head ─┬─ jaw
         │         │                                   └─ mouth (locator: Void Breath origin)
         │         ├─ arm_left ─ forearm_left ─ hand_left
         │         ├─ arm_right ─ forearm_right ─ hand_right
         │         ├─ wing_left ─ wing_left_mid ─ wing_left_tip
         │         └─ wing_right ─ wing_right_mid ─ wing_right_tip
         ├─ leg_left ─ shin_left ─ foot_left
         ├─ leg_right ─ shin_right ─ foot_right
         └─ tail_1 ─ tail_2 ─ tail_3 ─ tail_4 ─ tail_5
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from geo import Cube, Model, save_png, export_animations  # noqa: E402
from materials import PAINTERS  # noqa: E402
import animations_world_eater as anims  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSETS = os.path.join(ROOT, "src", "main", "resources", "assets", "aetherfall")


def mirror_cube(c):
    """Mirror a cube across X (left side -> right side)."""
    o = [-(c.origin[0] + c.size[0]), c.origin[1], c.origin[2]]
    rot = [c.rotation[0], -c.rotation[1], -c.rotation[2]] if c.rotation else None
    piv = [-c.pivot[0], c.pivot[1], c.pivot[2]] if c.pivot else None
    mats = dict(c.materials)
    if "east" in mats or "west" in mats:
        mats["east"], mats["west"] = c.materials.get("west", c.materials.get("*")), c.materials.get("east", c.materials.get("*"))
    m = Cube(o, c.size, mats, c.inflate, rot, piv, c.faces, c.seed + 1, **c.params)
    return m


def spike(x, y, z, w, h, d, rot, mat="crystal", **kw):
    return Cube([x, y, z], [w, h, d], mat, rotation=rot, pivot=[x + w / 2, y, z + d / 2], **kw)


def build():
    m = Model("geometry.world_eater")
    m.bone("root", [0, 0, 0])

    # ---- Body -------------------------------------------------------------------------------------------------
    body = m.bone("body", [0, 46, 8], "root")
    body.add(
        Cube([-16, 36, -4], [32, 22, 26], {"*": "scale", "north": "belly", "down": "belly"}),
        Cube([-17, 52, -5], [34, 4, 28], {"*": "gold", "north": "gold_rune"}),
    )

    chest = m.bone("chest", [0, 56, 4], "body")
    chest.add(
        Cube([-21, 56, -12], [42, 30, 30], {"*": "scale_sheen", "north": "belly"}),
        Cube([-15, 60, -15], [30, 24, 3], {"*": "gold", "north": "gold_sigil"}),
        Cube([-19, 82, -15], [38, 6, 10], {"*": "gold", "north": "gold_rune"}),
        Cube([-21, 62, -14], [5, 18, 3], "gold"),
        Cube([16, 62, -14], [5, 18, 3], "gold"),
        # spine crystals (the reference's crystalline back)
        spike(-3, 84, 4, 6, 17, 6, [-18, 0, 0]),
        spike(-2.5, 84, 14, 5, 13, 5, [-32, 0, 0]),
        spike(-2, 80, 24, 4, 10, 4, [-48, 0, 0]),
    )
    shoulder = Cube([15, 78, -10], [13, 10, 18], {"*": "gold", "north": "gold_rune"}, rotation=[0, 0, -12], pivot=[21, 83, -1])
    s_spike1 = spike(18, 87, -5, 5, 15, 5, [8, 0, -24])
    s_spike2 = spike(22, 84, 3, 4, 11, 4, [-10, 0, -42])
    chest.add(shoulder, mirror_cube(shoulder), s_spike1, mirror_cube(s_spike1), s_spike2, mirror_cube(s_spike2))

    # ---- Neck and head ------------------------------------------------------------------------------------------
    neck_lower = m.bone("neck_lower", [0, 84, -6], "chest", rotation=[-12, 0, 0])
    neck_lower.add(
        Cube([-9, 82, -22], [18, 16, 18], {"*": "scale", "north": "belly"}),
        Cube([-10, 90, -23], [20, 4, 20], "gold"),
        spike(-2, 96, -12, 4, 9, 4, [-30, 0, 0]),
    )
    neck_upper = m.bone("neck_upper", [0, 96, -14], "neck_lower", rotation=[-8, 0, 0])
    neck_upper.add(
        Cube([-8, 94, -28], [16, 14, 16], {"*": "scale", "north": "belly"}),
        spike(-2, 107, -20, 4, 8, 4, [-30, 0, 0]),
    )
    head = m.bone("head", [0, 104, -24], "neck_upper", rotation=[16, 0, 0])
    cheek = Cube([10.5, 103, -43], [2, 8, 14], "gold")
    eye = Cube([8, 108, -45], [3, 3, 1], "eye")
    horn1 = Cube([7, 114, -30], [4, 4, 22], "horn", rotation=[-38, -14, 0], pivot=[9, 116, -30])
    horn2 = Cube([9, 107, -31], [3, 3, 15], "horn", rotation=[-14, -32, 0], pivot=[10, 108, -31])
    head.add(
        Cube([-11, 100, -44], [22, 18, 22], "scale"),
        Cube([-12, 113, -45], [24, 6, 18], {"*": "gold", "north": "gold_rune"}),
        Cube([-8, 101, -62], [16, 11, 19], {"*": "scale", "down": "mouth"}),
        Cube([-6, 112, -61], [12, 2, 16], "gold"),
        Cube([-7.5, 98.5, -61.5], [15, 2.5, 15], {"north": "teeth", "east": "teeth", "west": "teeth"}),
        cheek, mirror_cube(cheek), eye, mirror_cube(eye), horn1, mirror_cube(horn1), horn2, mirror_cube(horn2),
        spike(-1.5, 118, -38, 3, 8, 3, [-22, 0, 0]),
        spike(-1, 118, -31, 2, 6, 2, [-38, 0, 0]),
    )
    jaw = m.bone("jaw", [0, 102, -42], "head")
    jaw.add(
        Cube([-7, 95, -60], [14, 6, 18], {"*": "scale", "up": "mouth", "down": "belly"}),
        Cube([-6.5, 101, -59.5], [13, 2.5, 14], {"north": "teeth_up", "east": "teeth_up", "west": "teeth_up"}),
        Cube([-6, 94.5, -56], [12, 2, 10], "gold"),
    )
    m.bone("mouth", [0, 103, -62], "head")

    # ---- Arms ------------------------------------------------------------------------------------------------
    for side, sx in (("left", 1), ("right", -1)):
        def c(o, s, mat, **kw):
            cube = Cube(o, s, mat, **kw)
            return cube if sx > 0 else mirror_cube(cube)

        arm = m.bone(f"arm_{side}", [22 * sx, 78, -2], "chest", rotation=[-10, 0, -10 * sx])
        arm.add(c([20, 62, -7], [10, 20, 10], "scale"))
        fore = m.bone(f"forearm_{side}", [25 * sx, 64, -2], f"arm_{side}", rotation=[-55, 0, 0])
        fore.add(
            c([21, 46, -6], [9, 19, 9], "scale"),
            c([20.5, 50, -6.5], [10, 10, 10], {"*": "gold", "north": "gold_rune"}),
            c([24.5, 58, 2], [2, 7, 2], "crystal", rotation=[-35, 0, 0], pivot=[25.5, 58, 3]),
        )
        hand = m.bone(f"hand_{side}", [25 * sx, 47, -2], f"forearm_{side}")
        hand.add(
            c([21, 41, -7], [9, 6, 10], "scale"),
            c([21.5, 34, -7.5], [2, 7, 2], "claw"),
            c([24, 33, -8], [2, 8, 2], "claw"),
            c([26.5, 34, -7.5], [2, 7, 2], "claw"),
            c([21, 37, -2], [2, 6, 2], "claw"),
        )

        # ---- Legs --------------------------------------------------------------------------------------------
        leg = m.bone(f"leg_{side}", [13 * sx, 44, 4], "body")
        leg.add(
            c([6, 26, -5], [15, 22, 18], "scale"),
            c([6.5, 26, -6], [14, 8, 3], {"*": "gold", "north": "gold_rune"}),
        )
        shin = m.bone(f"shin_{side}", [13 * sx, 28, 8], f"leg_{side}", rotation=[28, 0, 0])
        shin.add(
            c([8, 8, 3], [11, 21, 11], "scale"),
            c([12, 16, 13], [3, 9, 3], "crystal", rotation=[-40, 0, 0], pivot=[13.5, 16, 14.5]),
        )
        foot = m.bone(f"foot_{side}", [13 * sx, 10, 9], f"shin_{side}", rotation=[-28, 0, 0])
        foot.add(
            c([6, 0, -9], [15, 8, 20], {"*": "scale", "down": "belly"}),
            c([6.5, 0, -14], [3, 4, 5], "claw", tip="top"),
            c([11, 0, -15], [3, 5, 6], "claw", tip="top"),
            c([15.5, 0, -14], [3, 4, 5], "claw", tip="top"),
        )

        # ---- Wings: three-segment star-membrane wings with gold-lit leading edges ----------------------------
        wing = m.bone(f"wing_{side}", [14 * sx, 86, 14], "chest", rotation=[0, -10 * sx, -25 * sx])
        wing.add(
            c([14, 83, 11], [42, 6, 6], "wing_bone"),
            c([6, 22, 14], [50, 64, 0], "membrane", faces=["north"], scallop=2),
            c([20, 89, 12], [3, 6, 3], "gold", rotation=[0, 0, -20], pivot=[21.5, 89, 13.5]),
            c([34, 89, 12], [3, 7, 3], "gold", rotation=[0, 0, -20], pivot=[35.5, 89, 13.5]),
            c([48, 89, 12], [3, 6, 3], "gold", rotation=[0, 0, -20], pivot=[49.5, 89, 13.5]),
        )
        mid = m.bone(f"wing_{side}_mid", [56 * sx, 86, 14], f"wing_{side}", rotation=[0, 0, -25 * sx])
        mid.add(
            c([56, 83.5, 11.5], [46, 5, 5], "wing_bone"),
            # overlaps back across the joint so the fan has no gap; offset in depth to avoid z-fighting
            c([38, 18, 14.35], [64, 68, 0], "membrane", faces=["north"], scallop=3),
            c([60, 30, 13.2], [2, 55, 2], "wing_bone", rotation=[0, 0, 16], pivot=[61, 85, 14.2]),
            c([82, 36, 13.2], [2, 49, 2], "wing_bone", rotation=[0, 0, 8], pivot=[83, 85, 14.2]),
            c([53, 84, 10], [6, 7, 7], "gold"),
        )
        tip = m.bone(f"wing_{side}_tip", [102 * sx, 86, 14], f"wing_{side}_mid", rotation=[0, 0, -15 * sx])
        tip.add(
            c([102, 84, 12], [40, 4, 4], "wing_bone"),
            c([86, 38, 14.7], [56, 48, 0], "membrane", faces=["north"], taper="outer", scallop=2),
            c([106, 46, 13.5], [2, 39, 2], "wing_bone", rotation=[0, 0, 12], pivot=[107, 85, 14.5]),
            c([141, 83, 11], [10, 6, 6], "horn"),
        )

    # ---- Tail ------------------------------------------------------------------------------------------------
    t1 = m.bone("tail_1", [0, 44, 20], "body", rotation=[12, 0, 0])
    t1.add(
        Cube([-11, 34, 18], [22, 18, 28], {"*": "scale", "down": "belly"}),
        spike(-2, 51, 22, 4, 10, 4, [-40, 0, 0]),
        spike(-2, 50, 34, 4, 9, 4, [-45, 0, 0]),
    )
    t2 = m.bone("tail_2", [0, 42, 45], "tail_1", rotation=[6, 0, 0])
    t2.add(
        Cube([-8, 34, 44], [16, 14, 28], {"*": "scale", "down": "belly"}),
        spike(-1.5, 47, 50, 3, 8, 3, [-45, 0, 0]),
        spike(-1.5, 46, 62, 3, 7, 3, [-45, 0, 0]),
    )
    t3 = m.bone("tail_3", [0, 40, 71], "tail_2", rotation=[-4, 0, 0])
    t3.add(
        Cube([-6, 34, 70], [12, 11, 26], {"*": "scale", "down": "belly"}),
        Cube([-6.5, 33.5, 80], [13, 12, 3], "gold"),
        spike(-1, 44, 74, 2, 7, 2, [-45, 0, 0]),
    )
    t4 = m.bone("tail_4", [0, 39, 95], "tail_3", rotation=[-6, 0, 0])
    t4.add(
        Cube([-4.5, 35, 94], [9, 8, 24], {"*": "scale", "down": "belly"}),
        spike(-1, 42, 100, 2, 6, 2, [-45, 0, 0]),
    )
    t5 = m.bone("tail_5", [0, 39, 117], "tail_4", rotation=[-6, 0, 0])
    t5.add(
        Cube([-3, 36, 116], [6, 6, 18], "scale"),
        Cube([-1, 30, 126], [2, 18, 18], "crystal"),
        Cube([-6, 37, 128], [12, 2, 12], "crystal"),
    )
    return m


def main():
    model = build()
    model.pack(512)
    base, glow = model.paint(PAINTERS)
    model.export_geo(os.path.join(ASSETS, "geo", "entity", "world_eater.geo.json"), 22, 14, 6)
    save_png(base, os.path.join(ASSETS, "textures", "entity", "world_eater.png"))
    save_png(glow, os.path.join(ASSETS, "textures", "entity", "world_eater_glow.png"))
    export_animations(os.path.join(ASSETS, "animations", "entity", "world_eater.animation.json"), anims.build())
    cubes = sum(len(b.cubes) for b in model.bones)
    print(f"world_eater: {len(model.bones)} bones, {cubes} cubes, texture {model.tex_w}x{model.tex_h}")
    return model, base, glow


if __name__ == "__main__":
    main()
