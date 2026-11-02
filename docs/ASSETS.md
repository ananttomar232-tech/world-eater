# Aetherfall asset guide

Every model, texture, animation, sound and the score is generated from the scripts in `tools/`. You can
edit the scripts and regenerate, or replace any file with hand-made art (for example from Blockbench),
as long as you keep the names below. The Java code depends on these names.

```bash
python3 tools/model/world_eater.py      # boss geometry, textures, animations
python3 tools/model/minions.py          # Voidling and Void Meteor
python3 tools/assets/gen_textures.py    # blocks and items
python3 tools/assets/gen_fx_textures.py # particles, beam, boss bar, effect icon
PREVIEW_DIR=/tmp python3 tools/model/preview_world_eater.py idle swipe   # optional preview sheets
```

`tools/model/preview.py` is a software renderer that uses GeckoLib's own transform rules (mirrored X,
negated X/Y rotations, Z-Y-X order, 180 − yaw). It lets you check a model or animation without starting
the game.

## Files

| Path (under `assets/aetherfall/`) | What |
|---|---|
| `geo/entity/world_eater.geo.json` | Boss geometry (Bedrock 1.12.0, per-face UV) |
| `animations/entity/world_eater.animation.json` | Boss animations |
| `textures/entity/world_eater.png` | Boss base texture (512x256) |
| `textures/entity/world_eater_glow.png` | Boss emissive layer (same size) |
| `geo/entity/voidling.geo.json`, `animations/entity/voidling.animation.json`, `textures/entity/voidling(_glow).png` | Voidling |
| `geo/entity/void_meteor.geo.json`, `animations/entity/void_meteor.animation.json`, `textures/entity/void_meteor(_glow).png` | Meteor |
| `textures/entity/beam/void_breath_{core,body,haze}.png` | The three beam layers |
| `textures/gui/world_eater_bar.png` | Ornate boss bar sheet |
| `textures/particle/*.png` + `particles/*.json` | Particle sprites |

## World Eater bones

The model faces **north (−Z)** in Blockbench, 16 units per block, feet at y = 0.

```
root                         whole-body offsets (flight lift, death slump)
└─ body                      pelvis; pitched forward ~70° when gliding
   ├─ chest                  torso, gold sigil plate
   │  ├─ neck_lower          ┐ head look is spread 30% / 30% / 40%
   │  │  └─ neck_upper       │ across these three bones
   │  │     └─ head          ┘
   │  │        ├─ jaw        opens with rotation X+
   │  │        └─ mouth      EMPTY locator: Void Breath origin, place at the jaw tip
   │  ├─ arm_left ─ forearm_left ─ hand_left
   │  ├─ arm_right ─ forearm_right ─ hand_right
   │  ├─ wing_left ─ wing_left_mid ─ wing_left_tip         wing_left_tip: star trail origin
   │  └─ wing_right ─ wing_right_mid ─ wing_right_tip
   ├─ leg_left ─ shin_left ─ foot_left
   ├─ leg_right ─ shin_right ─ foot_right
   └─ tail_1 ─ tail_2 ─ tail_3 ─ tail_4 ─ tail_5
```

Code uses the bones `mouth`, `wing_left_tip`, `wing_right_tip` (tracked by `AetherfallRenderer`) and
`neck_lower`, `neck_upper`, `head` (head look, `AetherfallModel`). Every other bone is only referenced by
the animation file.

## World Eater animations

All names are prefixed `animation.world_eater.`. Lengths are at tempo 1.0; the attack controller speeds
up by ×1.15 in phase 2 and ×1.35 when enraged.

| Name | Loop | Length | Used for | Key frame |
|---|---|---|---|---|
| `idle` | loop | 4.0 s | standing | |
| `walk` | loop | 1.6 s | ground movement | |
| `fly_hover` | loop | 1.2 s | flying slowly | |
| `fly_glide` | loop | 2.0 s | flying fast | |
| `death` | hold | 6.0 s | death sequence | |
| `swipe` | hold | 1.6 s | `SWIPE` | hit at 0.70 s |
| `tail_sweep` | hold | 1.9 s | `TAIL_SWEEP` | hit at 0.90 s |
| `breath_charge` → `breath` | play → loop | 1.5 s / 1.0 s | `VOID_BREATH` | beam starts 1.5 s |
| `meteor_shower` | hold | 6.5 s | `METEOR_SHOWER` | sky cracks 0.70 s |
| `wing_gust` | hold | 2.0 s | `WING_GUST` | blast at 0.70 s |
| `dive_slam` | hold | 3.6 s | `DIVE_SLAM` | lock-on 0.90 s |
| `dive_impact` | triggered | 1.2 s | server-triggered on impact | |
| `gravity_well` | hold | 4.2 s | `GRAVITY_WELL` | implosion 3.10 s |
| `summon` | hold | 2.6 s | `SUMMON_VOIDLINGS` | spawn 1.30 s |
| `roar` | hold | 4.0 s | `PHASE_ROAR` | roar 1.10 s |
| `takeoff` | hold | 2.0 s | `TAKEOFF` | lift-off 0.40 s |
| `land` | loop | 1.0 s | `LAND` (descending) | |
| `land_impact` | triggered | 1.0 s | server-triggered on touchdown | |

Voidling: `animation.voidling.idle`, `.run`, `.attack`. Meteor: `animation.void_meteor.spin`.

## Emissive (glowing) textures

Each entity has a second texture with the same name plus `_glow`, at the same size and UV layout. It is
drawn by `EmissiveGlowLayer`: the model is rendered a second time through vanilla's additive, full-bright
`eyes` render type, the same pipeline Enderman eyes use.

* **Black or transparent = no glow.** Only the parts that emit light have colour.
* **The colour is the glow.** Additive blending adds the RGB on top of the lit base, so a dim colour gives a
  soft glow and a bright colour a hot one. Alpha doesn't matter (keep it at 255 where there is colour).
* **The base texture is not modified.** This differs from GeckoLib's `AutoGlowingGeoLayer`, which
  removes `_glowmask` pixels from the base and only supports fully glowing pixels.

What glows on the World Eater, matching the reference art:

| Surface | Glow colour |
|---|---|
| Eyes | white-violet core, violet rim |
| Rune engravings on the gold armour, the `R` sigil | violet `#BE6EFF` |
| Gold borders of the wings and the wing bones | gold `#FFC450` |
| Stars and nebula in the wing membranes | white to violet, soft |
| Crystal spikes | violet, hotter toward the tip |
| Mouth interior | magenta-violet (shows when the jaw opens) |
| Horn and claw tips | gold or violet, fading in |

### Geometry: one cube with per-face UVs

```json
{
  "origin": [-15, 60, -15], "size": [30, 24, 3],
  "uv": {
    "north": {"uv": [0, 0], "uv_size": [30, 24]},
    "south": {"uv": [31, 0], "uv_size": [30, 24]},
    "east":  {"uv": [62, 0], "uv_size": [3, 24]},
    "west":  {"uv": [66, 0], "uv_size": [3, 24]},
    "up":    {"uv": [70, 0], "uv_size": [30, 3]},
    "down":  {"uv": [70, 4], "uv_size": [30, 3]}
  }
}
```

The glow texture uses exactly the same `uv` rectangles: paint glow pixels in the same places on
`world_eater_glow.png`. Zero-thickness wing membranes use a single `north` face; the renderer draws
both sides (cut-out, no culling).

### Animation keyframes

```json
"animation.world_eater.swipe": {
  "loop": "hold_on_last_frame",
  "animation_length": 1.6,
  "bones": {
    "arm_right": {
      "rotation": {
        "0":    {"vector": [0, 0, 0],       "easing": "easeInOutSine"},
        "0.55": {"vector": [-125, 0, -30],  "easing": "easeInOutSine"},
        "0.78": {"vector": [-30, 50, 10],   "easing": "easeInOutSine"},
        "1.6":  {"vector": [0, 0, 0],       "easing": "easeInOutSine"}
      }
    }
  }
}
```

Sign conventions (Blockbench degrees):
* Rotation X+ pitches a bone forward (nose down) and opens the jaw.
* X− raises an arm forward and rears the neck up.
* On the left wing, Z+ lowers it (downstroke) and Y+ sweeps it forward.
* Right-side bones mirror Y and Z.

## Boss bar sheet (`textures/gui/world_eater_bar.png`, 256x64)

| Region | Position | Size |
|---|---|---|
| Frame (gold border, diamond end caps, centre gems) | 0,0 | 240x24, bar slot at 12,8 (216x8) |
| Fill | 0,24 | 216x8 |
| Enraged fill (below 33%) | 0,32 | 216x8 |
| Damage trail | 0,40 | 216x8 |
| Title plate | 0,48 | 176x16 |
| Empty well | 0,56 | 216x8 |
| Phase notch | 224,24 | 3x12 |
| Shine sweep | 232,24 | 12x8 |

The title is the boss's display name, upper-cased and drawn in gold (`#F2C14E`, turning `#FFB070` when
enraged) on the plate. The client config option `bossBarPosition` puts the bar at the `BOTTOM` (as in the
reference art) or the `TOP`.
