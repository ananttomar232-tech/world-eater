"""Renders preview sheets of the World Eater: rest pose from several angles, plus sampled animation frames."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import preview  # noqa: E402
import world_eater  # noqa: E402

OUT = os.environ.get("PREVIEW_DIR", "/tmp")


def main(names):
    model, base, glow = world_eater.main()
    anims = {a.name.split(".")[-1]: a for a in world_eater.anims.build()}
    shots = []
    if not names:
        for yaw, pitch in ((200, 12), (160, 12), (270, 8), (20, 25)):
            img, _, _ = preview.render(model, base, glow, yaw=yaw, pitch=pitch, size=(640, 520))
            shots.append(img)
        preview.sheet(shots, 2, os.path.join(OUT, "we_rest.png"))
        return
    for name in names:
        a = anims[name]
        frames = []
        for i in range(6):
            t = a.length * i / 5.0
            img, _, _ = preview.render(model, base, glow, anim=a, t=t, yaw=float(os.environ.get("YAW", 235)), pitch=12, size=(480, 400))
            frames.append(img)
        preview.sheet(frames, 3, os.path.join(OUT, f"we_{name}.png"))


if __name__ == "__main__":
    main(sys.argv[1:])
