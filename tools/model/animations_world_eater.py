"""World Eater animations, authored against the rest pose in world_eater.py.

Sign conventions (Bedrock degrees, verified with preview.py):
  rotation X+  pitches a bone forward / nose-down; opens the jaw; swings a hanging leg backward
  rotation X-  raises an arm forward, rears the neck and head up
  left wing Z+ lowers it (downstroke), Z- raises it; left wing Y+ sweeps it forward, Y- back
  right side is mirrored: negate Y and Z

Timings match AttackType at tempo 1.0 (20 ticks = 1 s), so hit frames line up with the server:
  swipe hit 0.70 s, tail hit 0.90 s, gust 0.70 s, roar 1.10 s, gravity implosion 3.10 s, summon 1.30 s.
"""
import math

from geo import Animation

P = "animation.world_eater."
WING_BONES = ("wing_{}", "wing_{}_mid", "wing_{}_tip")


def wings(a, t, base, mid, tip, easing="easeInOutSine"):
    """Sets both wings: values given for the left wing, mirrored for the right."""
    for side, sgn in (("left", 1), ("right", -1)):
        for bone, (x, y, z) in zip(WING_BONES, (base, mid, tip)):
            a.key(bone.format(side), "rotation", t, (x, y * sgn, z * sgn), easing)


def arms(a, t, upper, fore=(0, 0, 0), easing="easeInOutSine"):
    for side, sgn in (("left", 1), ("right", -1)):
        x, y, z = upper
        a.key(f"arm_{side}", "rotation", t, (x, y * sgn, z * sgn), easing)
        fx, fy, fz = fore
        a.key(f"forearm_{side}", "rotation", t, (fx, fy * sgn, fz * sgn), easing)


def legs(a, t, leg, shin=(0, 0, 0), foot=(0, 0, 0), easing="easeInOutSine"):
    for side in ("left", "right"):
        a.key(f"leg_{side}", "rotation", t, leg, easing)
        a.key(f"shin_{side}", "rotation", t, shin, easing)
        a.key(f"foot_{side}", "rotation", t, foot, easing)


def tail(a, t, yaw=0.0, pitch=0.0, lag=1.25, easing="easeInOutSine"):
    for i in range(1, 6):
        f = lag ** (i - 1)
        a.key(f"tail_{i}", "rotation", t, (pitch * (0.6 + 0.1 * i), yaw * f / 2.2, 0), easing)


def neck(a, t, lower, upper, head, jaw=0.0, easing="easeInOutSine"):
    a.key("neck_lower", "rotation", t, lower, easing)
    a.key("neck_upper", "rotation", t, upper, easing)
    a.key("head", "rotation", t, head, easing)
    a.key("jaw", "rotation", t, (jaw, 0, 0), easing)


FOLDED = ((0, -40, 34), (0, 0, 44), (0, 0, -34))     # wings tucked along the back
SPREAD = ((0, 0, 18), (0, 0, 24), (0, 0, 14))      # level, for gliding
RAISED = ((0, 4, -18), (0, 0, -10), (0, 0, -6))    # flared high, menacing


def idle():
    a = Animation(P + "idle", 4.0, True)
    for t, k in ((0, 0), (1, 1), (2, 0), (3, -1), (4, 0)):
        a.rot("chest", (t, (-2 * abs(k), 0, 0)))
        neck(a, t, (-3 * abs(k), 4 * k, 0), (0, 3 * k, 0), (2 * abs(k), 5 * k, 0), jaw=3 * abs(k))
        wings(a, t, (0, 0, -4 * abs(k)), (0, 0, -3 * abs(k)), (0, 0, -2 * abs(k)))
        arms(a, t, (-3 * abs(k), 0, 0))
        tail(a, t, yaw=7 * k)
    a.scale("chest", (0, (1, 1, 1)), (2, (1.02, 1.03, 1.03)), (4, (1, 1, 1)))
    return a


def walk():
    a = Animation(P + "walk", 1.6, True)
    for i, t in enumerate((0, 0.4, 0.8, 1.2, 1.6)):
        phase = math.cos(t / 1.6 * 2 * math.pi)
        a.rot("leg_left", (t, (-24 * phase, 0, 0)))
        a.rot("leg_right", (t, (24 * phase, 0, 0)))
        lift_l = max(0.0, math.sin(t / 1.6 * 2 * math.pi))
        lift_r = max(0.0, -math.sin(t / 1.6 * 2 * math.pi))
        a.rot("shin_left", (t, (22 * lift_l, 0, 0)))
        a.rot("shin_right", (t, (22 * lift_r, 0, 0)))
        a.rot("foot_left", (t, (-14 * lift_l, 0, 0)))
        a.rot("foot_right", (t, (-14 * lift_r, 0, 0)))
        a.pos("body", (t, (0, -1.6 * abs(math.sin(t / 1.6 * 2 * math.pi)), 0)))
        a.rot("body", (t, (4, 4 * phase, 2.5 * phase)))
        a.rot("arm_left", (t, (-6 + 10 * phase, 0, 0)))
        a.rot("arm_right", (t, (-6 - 10 * phase, 0, 0)))
        neck(a, t, (2, -4 * phase, 0), (0, -2 * phase, 0), (-2, -3 * phase, 0), jaw=2)
        tail(a, t, yaw=-9 * phase)
        wings(a, t, *FOLDED)
    return a


def flap(a, t0, period, amp=1.0, body_lift=3.0):
    """One full wingbeat starting at t0 (up -> down -> up)."""
    up = ((0, 2, -26 * amp), (0, 0, -18 * amp), (0, 0, -10 * amp))
    down = ((0, -4, 40 * amp), (0, 0, 22 * amp), (0, 0, 18 * amp))
    wings(a, t0, *up)
    wings(a, t0 + period * 0.45, *down, easing="easeInQuad")
    wings(a, t0 + period, *up)
    a.pos("root", (t0, (0, 0, 0)), (t0 + period * 0.5, (0, body_lift, 0)), (t0 + period, (0, 0, 0)))


def fly_hover():
    a = Animation(P + "fly_hover", 1.2, True)
    flap(a, 0.0, 1.2)
    for t in (0, 0.6, 1.2):
        k = 1 if t == 0.6 else 0
        a.rot("body", (t, (24 - 4 * k, 0, 0)))
        neck(a, t, (-18, 0, 0), (-6, 0, 0), (-6 + 4 * k, 0, 0), jaw=2)
        legs(a, t, (22 + 6 * k, 0, 0), (14, 0, 0), (12, 0, 0))
        arms(a, t, (-40, 0, 0), (-10, 0, 0))
        tail(a, t, pitch=-14 - 6 * k)
    return a


def fly_glide():
    a = Animation(P + "fly_glide", 2.0, True)
    for t in (0, 1.0, 2.0):
        k = 1 if t == 1.0 else 0
        a.rot("body", (t, (68, 0, 3 * (k * 2 - 1) if t == 1.0 else 0)))
        a.pos("root", (t, (0, 18 + 2 * k, 0)))
        neck(a, t, (-42, 0, 0), (-16, 0, 0), (-14, 0, 0), jaw=2)
        legs(a, t, (64, 0, 0), (-8, 0, 0), (30, 0, 0))
        arms(a, t, (-72, 0, 0), (-20, 0, 0))
        tail(a, t, pitch=-54, yaw=6 * (1 if k else -1))
        base, mid, tip = SPREAD
        wings(a, t, (base[0], base[1], base[2] - 8 * k), (mid[0], mid[1], mid[2] - 4 * k), tip)
    return a


def death():
    a = Animation(P + "death", 6.0, "hold_on_last_frame")
    # The last roar
    neck(a, 0, (0, 0, 0), (0, 0, 0), (0, 0, 0))
    neck(a, 0.9, (-34, 0, 0), (-14, 0, 0), (-34, 0, 0), jaw=42)
    wings(a, 0.9, *RAISED)
    arms(a, 0.9, (-80, 0, 30), (-20, 0, 0))
    # Stagger
    a.rot("body", (0, (0, 0, 0)), (1.6, (-6, 0, 8)), (2.4, (10, 0, -6)))
    neck(a, 2.4, (10, 8, 0), (6, 0, 0), (14, 10, 0), jaw=20)
    wings(a, 2.4, (0, -10, 20), (0, 0, 30), (0, 0, 20))
    # Collapse forward onto its chest
    a.rot("body", (3.6, (74, 0, -4)), (6.0, (78, 0, -4)), easing="easeInQuad")
    a.pos("root", (0, (0, 0, 0)), (2.4, (0, 0, 0)), (3.6, (0, -14, -6)), (6.0, (0, -16, -6)), easing="easeInQuad")
    legs(a, 3.6, (-70, 0, 0), (90, 0, 0), (-20, 0, 0))
    arms(a, 3.6, (-60, 0, 50), (-40, 0, 0))
    neck(a, 3.6, (-30, 14, 0), (-10, 6, 0), (-24, 18, 0), jaw=14)
    neck(a, 6.0, (-34, 16, 0), (-10, 8, 0), (-26, 20, 0), jaw=10)
    wings(a, 3.6, (0, -24, 64), (0, 0, 40), (0, 0, 30))
    wings(a, 6.0, (0, -26, 70), (0, 0, 44), (0, 0, 32))
    tail(a, 3.6, yaw=14, pitch=-60)
    return a


def swipe():
    a = Animation(P + "swipe", 1.6, "hold_on_last_frame")
    neck(a, 0, (0, 0, 0), (0, 0, 0), (0, 0, 0))
    a.rot("chest", (0, (0, 0, 0)), (0.55, (-6, 22, 0)), (0.78, (8, -26, 0), ), (1.6, (0, 0, 0)))
    a.rot("arm_right", (0, (0, 0, 0)), (0.55, (-125, 0, -30)), (0.78, (-30, 50, 10)), (1.6, (0, 0, 0)))
    a.rot("forearm_right", (0, (0, 0, 0)), (0.55, (40, 0, 0)), (0.78, (-10, 0, 0)), (1.6, (0, 0, 0)))
    a.rot("arm_left", (0, (0, 0, 0)), (0.55, (-20, 0, 10)), (0.78, (10, 0, 0)), (1.6, (0, 0, 0)))
    neck(a, 0.55, (-8, 10, 0), (0, 6, 0), (-6, 8, 0), jaw=8)
    neck(a, 0.78, (6, -10, 0), (2, -6, 0), (4, -10, 0), jaw=26)
    neck(a, 1.6, (0, 0, 0), (0, 0, 0), (0, 0, 0))
    wings(a, 0, (0, 0, 0), (0, 0, 0), (0, 0, 0))
    wings(a, 0.55, (0, -12, -8), (0, 0, -6), (0, 0, 0))
    wings(a, 0.78, (0, 10, 10), (0, 0, 8), (0, 0, 4))
    wings(a, 1.6, (0, 0, 0), (0, 0, 0), (0, 0, 0))
    a.rot("body", (0, (0, 0, 0)), (0.55, (-4, 0, 0)), (0.78, (8, 0, 0)), (1.6, (0, 0, 0)))
    return a


def tail_sweep():
    a = Animation(P + "tail_sweep", 1.9, "hold_on_last_frame")
    a.rot("body", (0, (0, 0, 0)), (0.45, (10, -18, 0)), (1.3, (6, 18, 0)), (1.9, (0, 0, 0)))
    tail(a, 0)
    tail(a, 0.45, yaw=-40, pitch=4)
    tail(a, 0.95, yaw=46, pitch=8, easing="easeOutQuad")
    tail(a, 1.3, yaw=30, pitch=2)
    tail(a, 1.9)
    neck(a, 0, (0, 0, 0), (0, 0, 0), (0, 0, 0))
    neck(a, 0.45, (4, 14, 0), (0, 8, 0), (2, 10, 0), jaw=10)
    neck(a, 1.3, (0, -10, 0), (0, -6, 0), (0, -6, 0), jaw=6)
    neck(a, 1.9, (0, 0, 0), (0, 0, 0), (0, 0, 0))
    wings(a, 0, (0, 0, 0), (0, 0, 0), (0, 0, 0))
    wings(a, 0.45, (0, -24, 20), (0, 0, 30), (0, 0, 20))
    wings(a, 1.9, (0, 0, 0), (0, 0, 0), (0, 0, 0))
    legs(a, 0, (0, 0, 0))
    legs(a, 0.45, (-10, 0, 0), (24, 0, 0), (-14, 0, 0))
    legs(a, 1.9, (0, 0, 0))
    return a


def breath_charge():
    a = Animation(P + "breath_charge", 1.5, False)
    neck(a, 0, (0, 0, 0), (0, 0, 0), (0, 0, 0))
    neck(a, 1.0, (-26, 0, 0), (-16, 0, 0), (-24, 0, 0), jaw=12)
    neck(a, 1.5, (16, 0, 0), (6, 0, 0), (4, 0, 0), jaw=32, easing="easeOutQuad")
    a.rot("chest", (0, (0, 0, 0)), (1.0, (-9, 0, 0)), (1.5, (8, 0, 0)))
    a.scale("chest", (0, (1, 1, 1)), (1.0, (1.06, 1.05, 1.08)), (1.5, (1, 1, 1)))
    wings(a, 0, (0, 0, 0), (0, 0, 0), (0, 0, 0))
    wings(a, 1.0, *RAISED)
    wings(a, 1.5, (0, 8, -6), (0, 0, -4), (0, 0, 0))
    arms(a, 0, (0, 0, 0))
    arms(a, 1.0, (-30, 0, 20), (-20, 0, 0))
    arms(a, 1.5, (-20, 0, 14), (-10, 0, 0))
    return a


def breath():
    a = Animation(P + "breath", 1.0, True)
    for t, k in ((0, 0), (0.25, 1), (0.5, 0), (0.75, -1), (1.0, 0)):
        neck(a, t, (16, 2 * k, 0), (6, 0, 0), (4 + 1.5 * abs(k), 0, 1.5 * k), jaw=32 + 3 * abs(k))
        a.rot("chest", (t, (8, 0, 0)))
        wings(a, t, (0, 8, -6 + 2 * abs(k)), (0, 0, -4), (0, 0, 0))
        arms(a, t, (-20, 0, 14), (-10, 0, 0))
    a.scale("chest", (0, (1, 1, 1)), (0.5, (0.98, 0.99, 0.97)), (1.0, (1, 1, 1)))
    return a


def meteor_shower():
    a = Animation(P + "meteor_shower", 6.5, "hold_on_last_frame")
    neck(a, 0, (0, 0, 0), (0, 0, 0), (0, 0, 0))
    a.rot("body", (0, (0, 0, 0)), (0.7, (-14, 0, 0)), (5.6, (-14, 0, 0)), (6.5, (0, 0, 0)))
    a.rot("chest", (0, (0, 0, 0)), (0.7, (-10, 0, 0)), (5.6, (-10, 0, 0)), (6.5, (0, 0, 0)))
    neck(a, 0.7, (-30, 0, 0), (-18, 0, 0), (-38, 0, 0), jaw=14)
    neck(a, 1.1, (-32, 0, 0), (-20, 0, 0), (-40, 0, 0), jaw=44, easing="easeOutQuad")
    t = 1.1
    shake = 1
    while t < 5.4:
        t = round(t + 0.3, 2)
        neck(a, t, (-32, 2 * shake, 0), (-20, 0, 0), (-40, 0, 2 * shake), jaw=38 + 4 * shake)
        shake = -shake
    neck(a, 5.6, (-28, 0, 0), (-16, 0, 0), (-34, 0, 0), jaw=20)
    neck(a, 6.5, (0, 0, 0), (0, 0, 0), (0, 0, 0))
    arms(a, 0, (0, 0, 0))
    arms(a, 0.7, (-150, 0, 34), (-30, 0, 0))
    arms(a, 5.6, (-150, 0, 34), (-30, 0, 0))
    arms(a, 6.5, (0, 0, 0))
    wings(a, 0, (0, 0, 0), (0, 0, 0), (0, 0, 0))
    wings(a, 0.7, (0, 8, -22), (0, 0, -12), (0, 0, -8))
    for i, tt in enumerate((1.4, 2.2, 3.0, 3.8, 4.6, 5.4)):
        k = 1 if i % 2 == 0 else 0
        wings(a, tt, (0, 8, -22 + 6 * k), (0, 0, -12 + 4 * k), (0, 0, -8))
    wings(a, 6.5, (0, 0, 0), (0, 0, 0), (0, 0, 0))
    legs(a, 0, (0, 0, 0))
    legs(a, 0.7, (-12, 0, 0), (16, 0, 0), (-4, 0, 0))
    legs(a, 5.6, (-12, 0, 0), (16, 0, 0), (-4, 0, 0))
    legs(a, 6.5, (0, 0, 0))
    tail(a, 0)
    tail(a, 0.7, pitch=-10)
    tail(a, 6.5)
    return a


def wing_gust():
    a = Animation(P + "wing_gust", 2.0, "hold_on_last_frame")
    wings(a, 0, (0, 0, 0), (0, 0, 0), (0, 0, 0))
    wings(a, 0.6, (0, -42, -26), (0, 0, -16), (0, 0, -10))
    wings(a, 0.78, (0, 46, 22), (0, 0, 18), (0, 0, 12), easing="easeInQuad")
    wings(a, 2.0, (0, 0, 0), (0, 0, 0), (0, 0, 0))
    a.rot("body", (0, (0, 0, 0)), (0.6, (-10, 0, 0)), (0.78, (14, 0, 0)), (2.0, (0, 0, 0)))
    neck(a, 0, (0, 0, 0), (0, 0, 0), (0, 0, 0))
    neck(a, 0.6, (-14, 0, 0), (-6, 0, 0), (-10, 0, 0), jaw=10)
    neck(a, 0.78, (10, 0, 0), (4, 0, 0), (6, 0, 0), jaw=28)
    neck(a, 2.0, (0, 0, 0), (0, 0, 0), (0, 0, 0))
    legs(a, 0, (0, 0, 0))
    legs(a, 0.78, (-14, 0, 0), (20, 0, 0), (-6, 0, 0))
    legs(a, 2.0, (0, 0, 0))
    return a


def dive_slam():
    """Rise on two beats, fold and plunge; held until the server signals impact (see dive_impact)."""
    a = Animation(P + "dive_slam", 3.6, "hold_on_last_frame")
    flap(a, 0.0, 0.9, amp=1.1, body_lift=4.0)
    a.rot("body", (0, (24, 0, 0)), (0.9, (24, 0, 0)), (1.2, (82, 0, 0)), (3.6, (82, 0, 0)))
    wings(a, 1.2, (0, -60, 46), (0, 0, 64), (0, 0, 40))
    wings(a, 3.6, (0, -60, 46), (0, 0, 64), (0, 0, 40))
    neck(a, 0, (-18, 0, 0), (-6, 0, 0), (-6, 0, 0), jaw=2)
    neck(a, 1.2, (-14, 0, 0), (-4, 0, 0), (-10, 0, 0), jaw=30)
    neck(a, 3.6, (-14, 0, 0), (-4, 0, 0), (-10, 0, 0), jaw=30)
    arms(a, 0, (-40, 0, 0), (-10, 0, 0))
    arms(a, 1.2, (-120, 0, 10), (-10, 0, 0))
    arms(a, 3.6, (-120, 0, 10), (-10, 0, 0))
    legs(a, 0, (22, 0, 0), (14, 0, 0), (12, 0, 0))
    legs(a, 1.2, (50, 0, 0), (10, 0, 0), (30, 0, 0))
    legs(a, 3.6, (50, 0, 0), (10, 0, 0), (30, 0, 0))
    tail(a, 1.2, pitch=-60)
    tail(a, 3.6, pitch=-60)
    return a


def dive_impact():
    """Triggered by the server the moment the dive hits the ground: crouch, wings slam down, recover."""
    a = Animation(P + "dive_impact", 1.2, False)
    a.rot("body", (0, (40, 0, 0)), (0.15, (18, 0, 0), ), (1.2, (0, 0, 0)))
    a.pos("root", (0, (0, 0, 0)), (0.15, (0, -6, 0)), (1.2, (0, 0, 0)))
    legs(a, 0, (-10, 0, 0), (30, 0, 0), (-20, 0, 0))
    legs(a, 0.15, (-26, 0, 0), (44, 0, 0), (-18, 0, 0))
    legs(a, 1.2, (0, 0, 0))
    wings(a, 0, (0, -20, 30), (0, 0, 30), (0, 0, 20))
    wings(a, 0.15, (0, 10, 46), (0, 0, 20), (0, 0, 14), easing="easeOutQuad")
    wings(a, 1.2, (0, 0, 0), (0, 0, 0), (0, 0, 0))
    neck(a, 0, (-10, 0, 0), (0, 0, 0), (-6, 0, 0), jaw=30)
    neck(a, 0.15, (10, 0, 0), (4, 0, 0), (12, 0, 0), jaw=36)
    neck(a, 1.2, (0, 0, 0), (0, 0, 0), (0, 0, 0))
    arms(a, 0, (-60, 0, 20), (-20, 0, 0))
    arms(a, 0.15, (-30, 0, 30), (-10, 0, 0))
    arms(a, 1.2, (0, 0, 0))
    return a


def gravity_well():
    a = Animation(P + "gravity_well", 4.2, "hold_on_last_frame")
    neck(a, 0, (0, 0, 0), (0, 0, 0), (0, 0, 0))
    neck(a, 0.5, (14, 0, 0), (6, 0, 0), (8, 0, 0), jaw=36)
    for i, t in enumerate((1.0, 1.5, 2.0, 2.5, 3.0)):
        k = 1 if i % 2 == 0 else -1
        neck(a, t, (14, 0, 0), (6, 0, 0), (8, 0, 1.5 * k), jaw=36 + 2 * k)
    neck(a, 3.15, (-8, 0, 0), (-4, 0, 0), (-16, 0, 0), jaw=0, easing="easeOutQuad")
    neck(a, 4.2, (0, 0, 0), (0, 0, 0), (0, 0, 0))
    wings(a, 0, (0, 0, 0), (0, 0, 0), (0, 0, 0))
    wings(a, 0.5, (0, 36, -12), (0, 20, -6), (0, 10, 0))
    wings(a, 3.0, (0, 40, -12), (0, 24, -6), (0, 12, 0))
    wings(a, 3.15, (0, -22, -24), (0, 0, -12), (0, 0, -6), easing="easeOutQuad")
    wings(a, 4.2, (0, 0, 0), (0, 0, 0), (0, 0, 0))
    arms(a, 0, (0, 0, 0))
    arms(a, 0.5, (-50, 0, 40), (-20, 0, 0))
    arms(a, 3.0, (-50, 0, 40), (-20, 0, 0))
    arms(a, 3.15, (-20, 0, 60), (0, 0, 0))
    arms(a, 4.2, (0, 0, 0))
    a.scale("chest", (0, (1, 1, 1)), (0.5, (1.04, 1.04, 1.04)), (3.0, (1.06, 1.06, 1.06)), (3.15, (0.96, 0.97, 0.96)), (4.2, (1, 1, 1)))
    return a


def summon():
    a = Animation(P + "summon", 2.6, "hold_on_last_frame")
    arms(a, 0, (0, 0, 0))
    arms(a, 0.8, (-110, 0, 58), (-20, 0, 0))
    arms(a, 1.3, (-10, 0, 20), (-30, 0, 0), easing="easeInQuad")
    arms(a, 2.6, (0, 0, 0))
    neck(a, 0, (0, 0, 0), (0, 0, 0), (0, 0, 0))
    neck(a, 0.8, (-26, 0, 0), (-12, 0, 0), (-28, 0, 0), jaw=30)
    neck(a, 1.3, (12, 0, 0), (4, 0, 0), (10, 0, 0), jaw=38)
    neck(a, 2.6, (0, 0, 0), (0, 0, 0), (0, 0, 0))
    wings(a, 0, (0, 0, 0), (0, 0, 0), (0, 0, 0))
    wings(a, 0.8, *RAISED)
    wings(a, 1.3, (0, 6, 12), (0, 0, 8), (0, 0, 4))
    wings(a, 2.6, (0, 0, 0), (0, 0, 0), (0, 0, 0))
    a.rot("body", (0, (0, 0, 0)), (0.8, (-8, 0, 0)), (1.3, (10, 0, 0)), (2.6, (0, 0, 0)))
    return a


def roar():
    a = Animation(P + "roar", 4.0, "hold_on_last_frame")
    a.rot("body", (0, (0, 0, 0)), (1.0, (-12, 0, 0)), (1.2, (8, 0, 0)), (3.0, (8, 0, 0)), (4.0, (0, 0, 0)))
    a.rot("chest", (0, (0, 0, 0)), (1.0, (-8, 0, 0)), (1.2, (6, 0, 0)), (3.0, (6, 0, 0)), (4.0, (0, 0, 0)))
    neck(a, 0, (0, 0, 0), (0, 0, 0), (0, 0, 0))
    neck(a, 1.0, (-30, 0, 0), (-14, 0, 0), (-30, 0, 0), jaw=16)
    neck(a, 1.2, (20, 0, 0), (6, 0, 0), (10, 0, 0), jaw=44, easing="easeOutQuad")
    t, k = 1.2, 1
    while t < 2.9:
        t = round(t + 0.2, 2)
        neck(a, t, (20, 3 * k, 0), (6, 0, 0), (10, 0, 2 * k), jaw=40 + 4 * k)
        k = -k
    neck(a, 4.0, (0, 0, 0), (0, 0, 0), (0, 0, 0))
    wings(a, 0, (0, 0, 0), (0, 0, 0), (0, 0, 0))
    wings(a, 1.0, *RAISED)
    wings(a, 1.2, (0, 10, -24), (0, 0, -14), (0, 0, -8))
    wings(a, 3.0, (0, 10, -24), (0, 0, -14), (0, 0, -8))
    wings(a, 4.0, (0, 0, 0), (0, 0, 0), (0, 0, 0))
    arms(a, 0, (0, 0, 0))
    arms(a, 1.0, (-60, 0, 40), (-30, 0, 0))
    arms(a, 3.0, (-60, 0, 40), (-30, 0, 0))
    arms(a, 4.0, (0, 0, 0))
    return a


def takeoff():
    a = Animation(P + "takeoff", 2.0, "hold_on_last_frame")
    a.pos("root", (0, (0, 0, 0)), (0.4, (0, -6, 0)), (0.9, (0, 2, 0)), (2.0, (0, 0, 0)))
    a.rot("body", (0, (0, 0, 0)), (0.4, (10, 0, 0)), (0.9, (18, 0, 0)), (2.0, (24, 0, 0)))
    legs(a, 0, (0, 0, 0))
    legs(a, 0.4, (-20, 0, 0), (40, 0, 0), (-20, 0, 0))
    legs(a, 0.9, (14, 0, 0), (6, 0, 0), (10, 0, 0))
    legs(a, 2.0, (22, 0, 0), (14, 0, 0), (12, 0, 0))
    wings(a, 0, (0, 0, 0), (0, 0, 0), (0, 0, 0))
    wings(a, 0.4, (0, 4, -30), (0, 0, -18), (0, 0, -10))
    wings(a, 0.9, (0, -4, 44), (0, 0, 24), (0, 0, 18), easing="easeInQuad")
    wings(a, 1.3, (0, 2, -26), (0, 0, -18), (0, 0, -10))
    wings(a, 1.7, (0, -4, 40), (0, 0, 22), (0, 0, 18), easing="easeInQuad")
    wings(a, 2.0, (0, 2, -26), (0, 0, -18), (0, 0, -10))
    neck(a, 0, (0, 0, 0), (0, 0, 0), (0, 0, 0))
    neck(a, 0.4, (10, 0, 0), (4, 0, 0), (6, 0, 0))
    neck(a, 2.0, (-18, 0, 0), (-6, 0, 0), (-6, 0, 0), jaw=2)
    arms(a, 0, (0, 0, 0))
    arms(a, 2.0, (-40, 0, 0), (-10, 0, 0))
    tail(a, 2.0, pitch=-14)
    return a


def land():
    """Descent: wings flared as air brakes, legs reaching. Loops until the server triggers land_impact."""
    a = Animation(P + "land", 1.0, True)
    for t, k in ((0, 0), (0.5, 1), (1.0, 0)):
        a.rot("body", (t, (8, 0, 0)))
        wings(a, t, (0, 22, -14 + 10 * k), (0, 10, -6 + 6 * k), (0, 0, -4 + 4 * k))
        legs(a, t, (-28, 0, 0), (10, 0, 0), (-6, 0, 0))
        neck(a, t, (-10, 0, 0), (-4, 0, 0), (-4, 0, 0), jaw=6)
        arms(a, t, (-30, 0, 10), (-10, 0, 0))
        tail(a, t, pitch=-20)
    return a


def land_impact():
    a = Animation(P + "land_impact", 1.0, False)
    a.pos("root", (0, (0, 0, 0)), (0.12, (0, -6, 0)), (1.0, (0, 0, 0)))
    a.rot("body", (0, (8, 0, 0)), (0.12, (16, 0, 0)), (1.0, (0, 0, 0)))
    legs(a, 0, (-28, 0, 0), (10, 0, 0), (-6, 0, 0))
    legs(a, 0.12, (-30, 0, 0), (46, 0, 0), (-18, 0, 0))
    legs(a, 1.0, (0, 0, 0))
    wings(a, 0, (0, 22, -4), (0, 10, 0), (0, 0, 0))
    wings(a, 0.12, (0, 0, 30), (0, 0, 24), (0, 0, 14), easing="easeOutQuad")
    wings(a, 1.0, (0, 0, 0), (0, 0, 0), (0, 0, 0))
    neck(a, 0, (-10, 0, 0), (-4, 0, 0), (-4, 0, 0), jaw=6)
    neck(a, 0.12, (8, 0, 0), (4, 0, 0), (8, 0, 0), jaw=14)
    neck(a, 1.0, (0, 0, 0), (0, 0, 0), (0, 0, 0))
    arms(a, 0, (-30, 0, 10), (-10, 0, 0))
    arms(a, 1.0, (0, 0, 0))
    return a


def build():
    return [idle(), walk(), fly_hover(), fly_glide(), death(), swipe(), tail_sweep(), breath_charge(), breath(),
            meteor_shower(), wing_gust(), dive_slam(), dive_impact(), gravity_well(), summon(), roar(), takeoff(),
            land(), land_impact()]
