"""Software preview renderer that reproduces GeckoLib's transform rules, for checking models without the game.

GeckoLib (4.x) rules reproduced here, read from its source:
  * Bedrock X is mirrored: cube origin x -> -(x + size.x), pivots x -> -x, animation position x -> -x.
  * Rotations (bone, cube and keyframes) have X and Y negated; applied as Z, then Y, then X (matrix Rz*Ry*Rx).
  * Bone transform: translate(anim offset) * translate(pivot) * R * scale * translate(-pivot), children nested.
  * Per-face UVs map: vertex order per face as in BakedModelFactory.VertexSet with u flipped (non-mirrored).
  * The entity is finally rotated by (180 - yaw) degrees about +Y.
"""
import math

import numpy as np
from PIL import Image


def rot_x(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1]])


def rot_y(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1]])


def rot_z(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])


def trans(x, y, z):
    m = np.eye(4)
    m[:3, 3] = [x, y, z]
    return m


def scale(x, y, z):
    return np.diag([x, y, z, 1.0])


def gecko_rot(r):
    """Bedrock degrees -> GeckoLib rotation matrix."""
    rx, ry, rz = (math.radians(-r[0]), math.radians(-r[1]), math.radians(r[2]))
    return rot_z(rz) @ rot_y(ry) @ rot_x(rx)


def face_quads(cube):
    """Yields (face, 4 vertices in gecko units (px), 4 uvs in texels)."""
    ox, oy, oz = cube.origin
    sx, sy, sz = cube.size
    i = cube.inflate
    x0 = -(ox + sx) - i
    x1 = -(ox + sx) + sx + i
    y0, y1 = oy - i, oy + sy + i
    z0, z1 = oz - i, oz + sz + i
    blb = (x0, y0, z0); brb = (x0, y0, z1); tlb = (x0, y1, z0); trb = (x0, y1, z1)
    tlf = (x1, y1, z0); trf = (x1, y1, z1); blf = (x1, y0, z0); brf = (x1, y0, z1)
    verts = {
        "west": (trb, tlb, blb, brb), "east": (tlf, trf, brf, blf),
        "north": (tlb, tlf, blf, blb), "south": (trf, trb, brb, brf),
        "up": (trb, trf, tlf, tlb), "down": (blb, blf, brf, brb),
    }
    for face, (u, v, w, h) in cube.uv.items():
        fw, fh = cube.face_size(face)
        uvs = ((u + fw, v), (u, v), (u, v + fh), (u + fw, v + fh))
        yield face, verts[face], uvs


def bone_matrices(model, anim=None, t=0.0, extra=None):
    mats = {}
    for bone in model.bones:
        parent = mats[bone.parent] if bone.parent else np.eye(4)
        base_rot = bone.rotation or [0, 0, 0]
        arot = anim.sample(bone.name, "rotation", t, (0, 0, 0)) if anim else (0, 0, 0)
        apos = anim.sample(bone.name, "position", t, (0, 0, 0)) if anim else (0, 0, 0)
        ascl = anim.sample(bone.name, "scale", t, (1, 1, 1)) if anim else (1, 1, 1)
        if extra and bone.name in extra:
            er = extra[bone.name]
            arot = tuple(a + b for a, b in zip(arot, er))
        total = [base_rot[k] + arot[k] for k in range(3)]
        px, py, pz = -bone.pivot[0], bone.pivot[1], bone.pivot[2]
        m = parent @ trans(-apos[0], apos[1], apos[2]) @ trans(px, py, pz) @ gecko_rot(total) @ scale(*ascl) @ trans(-px, -py, -pz)
        mats[bone.name] = m
    return mats


def render(model, base, glow, anim=None, t=0.0, yaw=30.0, pitch=20.0, size=(900, 700), zoom=None, entity_yaw=0.0,
           background=(28, 22, 38), extra=None, centre=None):
    W, H = size
    mats = bone_matrices(model, anim, t, extra)
    ent = rot_y(math.radians(180.0 - entity_yaw))
    cam = rot_x(math.radians(pitch)) @ rot_y(math.radians(yaw))
    tris = []
    light = np.array([0.35, 0.9, -0.45])
    light /= np.linalg.norm(light)
    for bone in model.bones:
        bm = mats[bone.name]
        for cube in bone.cubes:
            cm = np.eye(4)
            if cube.rotation:
                pv = cube.pivot or [cube.origin[i] + cube.size[i] / 2 for i in range(3)]
                p = (-pv[0], pv[1], pv[2])
                cm = trans(*p) @ gecko_rot(cube.rotation) @ trans(-p[0], -p[1], -p[2])
            m = cam @ ent @ bm @ cm
            for face, verts, uvs in face_quads(cube):
                pts = np.array([m @ np.array([*v, 1.0]) for v in verts])[:, :3]
                n = np.cross(pts[1] - pts[0], pts[2] - pts[0])
                nn = np.linalg.norm(n)
                if nn < 1e-9:
                    continue
                n /= nn
                world_n = n
                shade = 0.55 + 0.45 * max(0.0, float(np.dot(world_n, cam[:3, :3] @ light))) + 0.15 * abs(world_n[1])
                tris.append((pts, uvs, min(1.0, shade)))
    allp = np.concatenate([tp[0] for tp in tris]) if tris else np.zeros((1, 3))
    if centre is None:
        mn, mx = allp.min(0), allp.max(0)
        centre = (mn + mx) / 2
        span = max(mx[0] - mn[0], mx[1] - mn[1]) * 1.08
        zoom = zoom or min(W, H) / span
    img = np.zeros((H, W, 3))
    img[:] = np.array(background) / 255.0
    zbuf = np.full((H, W), -1e9)
    tb = base.astype(float) / 255.0
    tg = glow.astype(float) / 255.0
    th, tw = base.shape[:2]
    for pts, uvs, shade in tris:
        sp = np.empty((4, 3))
        sp[:, 0] = (centre[0] - pts[:, 0]) * zoom + W / 2  # camera looks along +Z, so screen-right is -X
        sp[:, 1] = H / 2 - (pts[:, 1] - centre[1]) * zoom
        sp[:, 2] = -pts[:, 2]  # camera looks down -z; larger = closer
        uv = np.array(uvs, dtype=float)
        for a, b, c in ((0, 1, 2), (0, 2, 3)):
            tri = sp[[a, b, c]]
            tuv = uv[[a, b, c]]
            xmin = max(int(math.floor(tri[:, 0].min())), 0)
            xmax = min(int(math.ceil(tri[:, 0].max())), W - 1)
            ymin = max(int(math.floor(tri[:, 1].min())), 0)
            ymax = min(int(math.ceil(tri[:, 1].max())), H - 1)
            if xmin > xmax or ymin > ymax:
                continue
            ys, xs = np.mgrid[ymin:ymax + 1, xmin:xmax + 1]
            px = xs + 0.5
            py = ys + 0.5
            (x0, y0, _), (x1, y1, _), (x2, y2, _) = tri
            den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
            if abs(den) < 1e-9:
                continue
            l0 = ((y1 - y2) * (px - x2) + (x2 - x1) * (py - y2)) / den
            l1 = ((y2 - y0) * (px - x2) + (x0 - x2) * (py - y2)) / den
            l2 = 1 - l0 - l1
            inside = (l0 >= -1e-4) & (l1 >= -1e-4) & (l2 >= -1e-4)
            if not inside.any():
                continue
            z = l0 * tri[0, 2] + l1 * tri[1, 2] + l2 * tri[2, 2]
            u = l0 * tuv[0, 0] + l1 * tuv[1, 0] + l2 * tuv[2, 0]
            v = l0 * tuv[0, 1] + l1 * tuv[1, 1] + l2 * tuv[2, 1]
            ui = np.clip(np.floor(u).astype(int), 0, tw - 1)
            vi = np.clip(np.floor(v).astype(int), 0, th - 1)
            texel = tb[vi, ui]
            mask = inside & (texel[..., 3] > 0.1) & (z > zbuf[ys, xs])
            if not mask.any():
                continue
            colour = texel[..., :3] * shade + tg[vi, ui, :3]  # additive full-bright glow layer (eyes render type)
            yy, xx = ys[mask], xs[mask]
            img[yy, xx] = np.clip(colour[mask], 0, 1)
            zbuf[yy, xx] = z[mask]
    return Image.fromarray((img * 255).astype(np.uint8), "RGB"), centre, zoom


def sheet(images, cols, path, label=None):
    w, h = images[0].size
    rows = (len(images) + cols - 1) // cols
    out = Image.new("RGB", (cols * w, rows * h), (10, 8, 14))
    for i, im in enumerate(images):
        out.paste(im, ((i % cols) * w, (i // cols) * h))
    out.save(path)
