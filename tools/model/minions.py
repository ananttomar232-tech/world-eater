"""Voidling and Void Meteor models, textures and animations.

    python3 tools/model/minions.py

Voidling bones: root > body > (head, leg_front_left, leg_front_right, leg_back_left, leg_back_right, tail)
Void Meteor bones: root > core > chunks
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from geo import Animation, Cube, Model, export_animations, save_png  # noqa: E402
from materials import PAINTERS  # noqa: E402
from world_eater import ASSETS, mirror_cube, spike  # noqa: E402


def voidling():
    m = Model("geometry.voidling")
    m.bone("root", [0, 0, 0])
    body = m.bone("body", [0, 7, 0], "root")
    body.add(
        Cube([-4, 4, -5], [8, 5, 10], {"*": "scale", "down": "belly"}),
        spike(-1.5, 8, -2, 3, 7, 3, [-20, 0, 0]),
        spike(-1, 8, 2, 2, 5, 2, [-35, 0, 0]),
        spike(1.5, 8, -1, 2, 5, 2, [0, 0, -30]),
        spike(-3.5, 8, -1, 2, 5, 2, [0, 0, 30]),
    )
    head = m.bone("head", [0, 7, -5], "body")
    head.add(
        Cube([-3, 4, -10], [6, 5, 5], "scale"),
        Cube([-1.5, 5.5, -10.5], [3, 2, 1], "eye"),
        Cube([-2.5, 3, -10], [5, 1, 4], {"north": "teeth", "east": "teeth", "west": "teeth"}),
        spike(-2.5, 8.5, -8, 1, 4, 1, [-40, 0, 20], "horn"),
        spike(1.5, 8.5, -8, 1, 4, 1, [-40, 0, -20], "horn"),
    )
    for name, z, rot in (("front", -3, -25), ("back", 3, 25)):
        leg = m.bone(f"leg_{name}_left", [4, 6, z], "body", rotation=[rot, 0, -30])
        cube = Cube([4, 0, z - 1], [2, 7, 2], "claw")
        leg.add(cube)
        leg_r = m.bone(f"leg_{name}_right", [-4, 6, z], "body", rotation=[rot, 0, 30])
        leg_r.add(mirror_cube(cube))
    tail = m.bone("tail", [0, 6, 5], "body", rotation=[-20, 0, 0])
    tail.add(Cube([-1, 5, 5], [2, 2, 6], "scale"), spike(-0.5, 5, 10, 1, 1, 4, None, "crystal"))
    return m


def voidling_animations():
    p = "animation.voidling."
    idle = Animation(p + "idle", 2.0, True)
    idle.pos("body", (0, (0, 0, 0)), (1, (0, 0.6, 0)), (2, (0, 0, 0)))
    idle.rot("head", (0, (0, 0, 0)), (0.5, (-4, 10, 0)), (1.5, (-4, -10, 0)), (2, (0, 0, 0)))
    idle.rot("tail", (0, (0, 0, 0)), (1, (0, 15, 0)), (2, (0, 0, 0)))

    run = Animation(p + "run", 0.4, True)
    for t, k in ((0, 1), (0.2, -1), (0.4, 1)):
        run.rot("leg_front_left", (t, (30 * k, 0, 0)), easing="linear")
        run.rot("leg_back_right", (t, (30 * k, 0, 0)), easing="linear")
        run.rot("leg_front_right", (t, (-30 * k, 0, 0)), easing="linear")
        run.rot("leg_back_left", (t, (-30 * k, 0, 0)), easing="linear")
        run.rot("body", (t, (6, 4 * k, 0)), easing="linear")
        run.rot("tail", (t, (0, 20 * k, 0)), easing="linear")
    run.pos("body", (0, (0, 0, 0)), (0.1, (0, 1, 0)), (0.2, (0, 0, 0)), (0.3, (0, 1, 0)), (0.4, (0, 0, 0)))

    attack = Animation(p + "attack", 0.5, False)
    attack.rot("head", (0, (0, 0, 0)), (0.15, (-30, 0, 0)), (0.25, (25, 0, 0)), (0.5, (0, 0, 0)))
    attack.rot("body", (0, (0, 0, 0)), (0.15, (-10, 0, 0)), (0.25, (12, 0, 0)), (0.5, (0, 0, 0)))
    attack.pos("body", (0, (0, 0, 0)), (0.25, (0, 0, -3)), (0.5, (0, 0, 0)))
    return [idle, run, attack]


def meteor():
    m = Model("geometry.void_meteor")
    m.bone("root", [0, 12, 0])
    core = m.bone("core", [0, 12, 0], "root")
    core.add(
        Cube([-8, 4, -8], [16, 16, 16], "rock"),
        Cube([-6, 2, -9], [12, 12, 12], "rock", rotation=[35, 25, 0], pivot=[0, 12, 0]),
        Cube([-7, 6, -6], [14, 14, 12], "rock", rotation=[0, 45, 30], pivot=[0, 12, 0]),
        Cube([-5, 7, -5], [10, 10, 10], "core", inflate=0.6),
    )
    chunks = m.bone("chunks", [0, 12, 0], "core")
    for i, (o, s) in enumerate((([7, 14, -2], [5, 5, 5]), ([-12, 9, 1], [5, 4, 5]), ([-2, 19, 4], [4, 4, 4]),
                                 ([1, 3, 7], [4, 4, 4]), ([-4, 6, -12], [4, 5, 4]))):
        chunks.add(Cube(o, s, "rock", rotation=[20 * i, 35 * i, 15], pivot=[0, 12, 0], seed=i))
    return m


def meteor_animations():
    spin = Animation("animation.void_meteor.spin", 1.6, True)
    spin.rot("core", (0, (0, 0, 0)), (0.8, (180, 90, 0)), (1.6, (360, 180, 0)), easing="linear")
    spin.rot("chunks", (0, (0, 0, 0)), (1.6, (0, -360, 90)), easing="linear")
    return [spin]


def write(model, name, anims, atlas):
    model.pack(atlas)
    base, glow = model.paint(PAINTERS)
    model.export_geo(os.path.join(ASSETS, "geo", "entity", f"{name}.geo.json"), 3, 3, 1)
    save_png(base, os.path.join(ASSETS, "textures", "entity", f"{name}.png"))
    save_png(glow, os.path.join(ASSETS, "textures", "entity", f"{name}_glow.png"))
    export_animations(os.path.join(ASSETS, "animations", "entity", f"{name}.animation.json"), anims)
    print(f"{name}: {len(model.bones)} bones, texture {model.tex_w}x{model.tex_h}")
    return model, base, glow


def main():
    v = write(voidling(), "voidling", voidling_animations(), 64)
    mt = write(meteor(), "void_meteor", meteor_animations(), 128)
    return v, mt


if __name__ == "__main__":
    out = main()
    preview_dir = os.environ.get("PREVIEW_DIR")
    if preview_dir:
        import preview
        imgs = []
        for (model, base, glow), anim in ((out[0], None), (out[1], None)):
            for yaw in (200, 300):
                img, _, _ = preview.render(model, base, glow, yaw=yaw, pitch=20, size=(360, 300))
                imgs.append(img)
        preview.sheet(imgs, 4, os.path.join(preview_dir, "minions.png"))
