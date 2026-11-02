"""Aetherfall sound effects: every entity, block, item and effect sound in the mod.

Run from the repository root:
    python3 tools/audio/sfx.py            # all sounds
    python3 tools/audio/sfx.py roar step  # only names containing these words

Writes mono Ogg Vorbis files (mono is required for positional audio in Minecraft) to
src/main/resources/assets/aetherfall/sounds/.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import synth as s  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "src", "main", "resources", "assets", "aetherfall", "sounds")

HALL = s.make_ir(3.8, seed=7, damping=0.3, predelay=0.03)      # the ruined temple: huge stone hall
ROOM = s.make_ir(1.2, seed=8, damping=0.5, predelay=0.01)      # close, for small sounds
CAVERN = s.make_ir(6.0, seed=9, damping=0.2, predelay=0.05)    # the void itself


def finish(x, ir=None, wet=0.25, tail=0.0, peak=0.89, fade_out=0.08, target_rms_db=-16.0):
    if tail > 0:
        x = np.concatenate([x, np.zeros(s.n_samples(tail))])
    if ir is not None:
        x = s.reverb(x, ir, wet)
    x = s.dc_block(x)
    x = s.fade(x, 0.003, fade_out)
    x = s.normalize(x, peak)
    # Loudness levelling: transient-heavy sounds get up to +9 dB into a soft limiter so every effect in the mod
    # sits at a consistent perceived level (sounds.json volume then sets the mix).
    rms = np.sqrt(np.mean(x ** 2)) + 1e-9
    gain = min(10 ** (target_rms_db / 20) / rms, 10 ** (9 / 20))
    if gain > 1.0:
        x = s.soft_limit(x * gain, ceiling=peak, knee=peak * 0.7)
    return x


# ---------------------------------------------------------------------------------------------------------------------
# Voice of the World Eater
# ---------------------------------------------------------------------------------------------------------------------

def vocal(dur, f0_points, jaw_points, seed, breath=0.35, growl=0.6, drive=2.5, screech=0.0, size=1.0):
    """A colossal creature voice.

    f0_points:  pitch automation [(t, hz)], the throat's fundamental.
    jaw_points: openness automation [(t, 0..1)], drives the formants (closed rumble -> open bellow).
    growl:      sub-harmonic roughness (period-doubling, the "rattle" of a huge larynx).
    screech:    adds a high, strained harmonic band (pain, fury).
    size:       > 1 lowers the formants (a bigger throat).
    """
    t = s.timeline(dur)
    f0 = s.curve(dur, f0_points)
    f0 = f0 * (1 + 0.035 * s.smooth_random(dur, 9, seed)) * (1 + 0.012 * np.sin(2 * np.pi * 5.3 * t))
    jaw = np.clip(s.curve(dur, jaw_points), 0, 1)

    # Larynx: bright saw + period-doubled saw (growl), amplitude-modulated at a rough, irregular rate.
    rough = 0.5 + 0.5 * np.sin(2 * np.pi * np.cumsum(28 + 10 * s.smooth_random(dur, 4, seed + 1)) / s.SR)
    tone = s.saw(f0) + growl * s.saw(f0 * 0.5, 0.3) * rough + 0.35 * s.square(f0 * 1.004, 0.3)
    tone *= 1 - 0.45 * growl * (1 - rough)

    # Turbulent air through a huge throat.
    air = s.pink(dur, seed + 2)
    src = tone * (1 - breath) + air * breath * (0.6 + 0.8 * jaw)

    # Formants move with the jaw. Large-creature formants sit low, dropped further by size.
    k = 1.0 / size
    jaw_ds = jaw[::256]
    jaw_t = np.linspace(0, dur, len(jaw_ds))

    def g(tt, ff):
        j = np.interp(tt, jaw_t, jaw_ds)
        f1 = (220 + 420 * j) * k
        f2 = (620 + 520 * j) * k
        f3 = (1900 + 500 * j) * k
        f4 = 3100 * k
        gain = s.formant_gain(ff, [(f1, 160 + 160 * j, 1.0), (f2, 260, 0.65), (f3, 420, 0.32 + 0.3 * screech),
                                   (f4, 600, 0.12 + 0.35 * screech)])
        body = 1.0 / (1.0 + (ff / (5200 * k + 2500 * screech)) ** 4)
        return (0.08 + gain) * body

    voice = s.tv_filter(src, g)
    if screech > 0:
        band = s.bandpass(s.saw(f0 * 3.01) * (0.5 + 0.5 * jaw), 2400 * k, 2.0)
        voice += band * screech * 0.8
    voice = s.saturate(voice / (np.std(voice) * 3 + 1e-9), drive)

    # Chest: a sub sine an octave below, felt more than heard.
    chest = s.lowpass(s.sine(f0 * 0.5), 140) * 0.6 * (0.3 + 0.7 * jaw)
    return voice + chest


def amp_env(dur, points):
    return np.clip(s.curve(dur, points), 0, None)


def world_eater_ambient(v):
    rng = np.random.default_rng(100 + v)
    dur = 2.6 + 0.4 * v
    base = 52 + 6 * v
    x = vocal(dur, [(0, base), (dur * 0.5, base * 1.12), (dur, base * 0.92)],
              [(0, 0.05), (dur * 0.45, 0.35 + 0.1 * v), (dur, 0.08)], seed=110 + v, breath=0.45, growl=0.85,
              drive=2.0, size=1.5)
    x *= amp_env(dur, [(0, 0), (0.35, 0.9), (dur * 0.6, 1.0), (dur, 0)])
    # Rumbling exhale through the nostrils at the end
    exhale = s.lowpass(s.pink(dur, 120 + v), 900) * amp_env(dur, [(0, 0), (dur * 0.6, 0), (dur * 0.8, 0.35), (dur, 0)])
    return finish(x + exhale * float(rng.uniform(0.8, 1.2)), HALL, 0.3, tail=1.2)


def world_eater_hurt(v):
    dur = 0.95
    p = 105 + 18 * v
    x = vocal(dur, [(0, p * 1.3), (0.12, p * 1.55), (dur, p * 0.85)], [(0, 0.6), (0.1, 1.0), (dur, 0.3)],
              seed=200 + v, breath=0.3, growl=0.5, drive=3.5, screech=0.55, size=1.15)
    x *= amp_env(dur, [(0, 0), (0.02, 1.0), (0.3, 0.8), (dur, 0)])
    return finish(x, HALL, 0.25, tail=0.8)


def world_eater_roar(v):
    dur = 3.6
    p = 70 + 8 * v
    x = vocal(dur, [(0, p * 0.8), (0.5, p * 1.5), (1.6, p * 1.75), (2.8, p * 1.2), (dur, p * 0.7)],
              [(0, 0.1), (0.35, 0.85), (1.2, 1.0), (2.6, 0.8), (dur, 0.1)], seed=300 + v, breath=0.32, growl=0.7,
              drive=3.8, screech=0.35, size=1.3)
    # A second throat a fifth above, slightly late: the double-voiced roar of something far too large.
    y = vocal(dur, [(0, p * 1.2), (0.6, p * 2.2), (1.7, p * 2.6), (2.8, p * 1.8), (dur, p)],
              [(0, 0.0), (0.5, 0.7), (1.3, 0.9), (2.6, 0.6), (dur, 0.0)], seed=310 + v, breath=0.4, growl=0.3,
              drive=3.0, screech=0.6, size=1.1)
    env = amp_env(dur, [(0, 0), (0.25, 0.7), (0.6, 1.0), (2.7, 0.9), (dur, 0)])
    mix = (x + 0.55 * s.pad_to(np.concatenate([np.zeros(s.n_samples(0.08)), y]), dur)) * env
    # Ground-shaking sub that swells under the roar
    sub = s.sine(s.curve(dur, [(0, 38), (1.5, 46), (dur, 30)])) * amp_env(dur, [(0, 0), (0.6, 0.8), (2.8, 0.7), (dur, 0)])
    return finish(mix + sub * 0.5, CAVERN, 0.35, tail=2.5)


def world_eater_death():
    dur = 7.5
    roar = vocal(4.2, [(0, 90), (0.6, 150), (1.8, 135), (3.0, 80), (4.2, 38)],
                 [(0, 0.2), (0.4, 1.0), (2.5, 0.9), (4.2, 0.0)], seed=400, breath=0.35, growl=0.8, drive=3.5,
                 screech=0.5, size=1.35)
    roar *= amp_env(4.2, [(0, 0), (0.3, 1.0), (3.0, 0.8), (4.2, 0)])
    out = np.zeros(s.n_samples(dur))
    s.place(out, roar, 0.0)
    # Crystalline armour shattering, a cascade of tuned glass partials
    rng = np.random.default_rng(401)
    for i in range(40):
        f = rng.uniform(1800, 7000)
        d = rng.uniform(0.3, 1.2)
        ping = s.sine(np.full(s.n_samples(d), f)) * s.decay(d, d / 5)
        s.place(out, ping, 2.6 + rng.uniform(0, 1.6), rng.uniform(0.04, 0.12))
    # Implosion: reversed swell then the void collapses with a deep boom
    swell = s.sweep_lp(s.white(1.4, 402), lambda t: 200 + 6000 * (t / 1.4) ** 2) * np.linspace(0, 1, s.n_samples(1.4)) ** 3
    s.place(out, swell * 0.8, 4.0)
    boom_d = 3.0
    boom = s.sine(s.exp_curve(boom_d, [(0, 90), (0.25, 38), (boom_d, 22)])) * s.decay(boom_d, 0.9)
    boom = s.saturate(boom * 1.5, 2.0) + s.lowpass(s.brown(boom_d, 403), 400) * s.decay(boom_d, 0.6) * 0.6
    s.place(out, boom, 5.4)
    return finish(out, CAVERN, 0.35, tail=1.5, fade_out=1.0)


# ---------------------------------------------------------------------------------------------------------------------
# Body
# ---------------------------------------------------------------------------------------------------------------------

def thud(dur, f_start, f_end, tau, seed, debris=0.4):
    body = s.sine(s.exp_curve(dur, [(0, f_start), (0.08, f_end * 1.4), (dur, f_end)])) * s.decay(dur, tau)
    click = s.highpass(s.white(0.02, seed), 1500) * s.decay(0.02, 0.004)
    rumble = s.lowpass(s.brown(dur, seed + 1), 250) * s.decay(dur, tau * 1.4)
    grit = s.bandpass(s.white(dur, seed + 2), 2500, 0.8) * s.decay(dur, 0.12) * debris
    x = s.saturate(body * 1.3, 1.8) + 0.5 * rumble + grit
    x[:len(click)] += click * 0.5
    return x


def world_eater_step(v):
    x = thud(0.9, 120 - 10 * v, 34 + 3 * v, 0.22, 500 + v, debris=0.5)
    # Crystal spines rattle on every step
    rng = np.random.default_rng(510 + v)
    for _ in range(6):
        f = rng.uniform(2500, 5200)
        d = 0.25
        s.place(x, s.sine(np.full(s.n_samples(d), f)) * s.decay(d, 0.05), rng.uniform(0.03, 0.12), 0.05)
    return finish(x, HALL, 0.2, tail=0.6)


def whoosh(dur, f_from, f_to, seed, q=1.2, shape=2.0):
    n = s.white(dur, seed)
    env = np.sin(np.pi * np.linspace(0, 1, s.n_samples(dur))) ** shape
    swept = s.sweep_bp(n, lambda t: f_from + (f_to - f_from) * np.clip(t / dur, 0, 1), q)
    return swept * env


def world_eater_wing_flap(v):
    dur = 0.85
    air = whoosh(dur, 300 + 40 * v, 120, 600 + v, q=0.8, shape=1.5)
    # The membrane snaps taut: leathery flutter
    flutter = s.lowpass(s.white(dur, 610 + v), 1400) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 34 * s.timeline(dur))))
    flutter *= s.decay(dur, 0.12) * 0.7
    thump = s.sine(s.exp_curve(dur, [(0, 90), (dur, 40)])) * s.decay(dur, 0.12)
    shimmer = s.highpass(s.white(dur, 620 + v), 6000) * np.sin(np.pi * np.linspace(0, 1, s.n_samples(dur))) ** 4 * 0.15
    return finish(air + flutter + thump * 0.8 + shimmer, HALL, 0.25, tail=0.6)


def world_eater_takeoff():
    dur = 2.6
    out = np.zeros(s.n_samples(dur))
    for i, at in enumerate((0.0, 0.7, 1.35)):
        s.place(out, world_eater_wing_flap(i % 3) * (1.0 - 0.15 * i), at)
    wind = s.sweep_lp(s.pink(dur, 650), lambda t: 200 + 2500 * (t / dur)) * np.linspace(0.1, 1, s.n_samples(dur)) ** 1.5
    return finish(out + wind * 0.4, HALL, 0.25, tail=0.8)


def world_eater_land(v):
    dur = 2.0
    x = thud(dur, 150, 28, 0.55, 700 + v, debris=0.9)
    rng = np.random.default_rng(710 + v)
    for _ in range(18):
        d = rng.uniform(0.05, 0.2)
        chip = s.bandpass(s.white(d, int(rng.integers(1e6))), rng.uniform(1500, 5000), 3) * s.decay(d, d / 4)
        s.place(x, chip, rng.uniform(0.1, 1.2), rng.uniform(0.1, 0.35))
    return finish(x, CAVERN, 0.3, tail=1.4)


# ---------------------------------------------------------------------------------------------------------------------
# Attacks
# ---------------------------------------------------------------------------------------------------------------------

def claw_ring(dur, seed):
    rng = np.random.default_rng(seed)
    out = np.zeros(s.n_samples(dur))
    base = rng.uniform(900, 1300)
    for r in (1.0, 2.31, 3.89, 5.12):
        out += s.sine(np.full(len(out), base * r)) * s.decay(dur, 0.25 / r) / r
    return out


def world_eater_swipe(v):
    dur = 0.6
    air = whoosh(dur, 2600 + 300 * v, 400, 800 + v, q=1.6, shape=3)
    ring = claw_ring(dur, 810 + v) * 0.25
    return finish(air + ring, HALL, 0.2, tail=0.5)


def world_eater_tail_sweep(v):
    dur = 1.2
    air = whoosh(dur, 900 + 100 * v, 160, 900 + v, q=0.9, shape=2)
    rng = np.random.default_rng(910 + v)
    rattle = np.zeros(s.n_samples(dur))
    for _ in range(16):
        f = rng.uniform(2200, 6000)
        d = 0.2
        s.place(rattle, s.sine(np.full(s.n_samples(d), f)) * s.decay(d, 0.04), rng.uniform(0.2, 0.8), 0.06)
    return finish(air + rattle + 0.4 * thud(dur, 80, 40, 0.15, 920 + v, 0.2), HALL, 0.25, tail=0.6)


def world_eater_wing_gust():
    dur = 2.0
    blast = s.sweep_lp(s.pink(dur, 1000), lambda t: 300 + 5000 * np.exp(-((t - 0.45) ** 2) / 0.08)) * \
        amp_env(dur, [(0, 0), (0.35, 1), (1.0, 0.6), (dur, 0)])
    howl = s.bandpass(s.white(dur, 1001), 700, 12) * 3 * amp_env(dur, [(0, 0), (0.4, 1), (1.4, 0.4), (dur, 0)])
    thump = s.sine(s.exp_curve(dur, [(0, 70), (dur, 30)])) * s.decay(dur, 0.3)
    return finish(blast + howl + thump, HALL, 0.3, tail=0.8)


def energy(dur, f0, seed, spread=0.02, buzz=0.5):
    """Dense, unstable void energy: detuned supersaw cluster + ring-modulated buzz + plasma crackle."""
    t = s.timeline(dur)
    wob = 1 + 0.01 * s.smooth_random(dur, 6, seed)
    tone = s.supersaw(f0 * wob, 7, spread, seed) + 0.6 * s.supersaw(f0 * 1.5 * wob, 5, spread, seed + 1)
    ring = s.saw(f0 * 0.5) * s.sine(np.full(len(t), 63.0))
    crackle = s.white(dur, seed + 2) * (np.random.default_rng(seed + 3).random(len(t)) > 0.996) * 4
    crackle = s.bandpass(crackle, 3500, 0.7)
    return tone + buzz * ring + crackle


def world_eater_breath_charge():
    dur = 1.6
    f = s.exp_curve(dur, [(0, 55), (dur, 220)])
    e = energy(dur, f, 1100, spread=0.03, buzz=0.4)
    e = s.sweep_lp(e, lambda t: 300 + 5000 * (t / dur) ** 2)
    inhale = s.sweep_bp(s.pink(dur, 1101), lambda t: 400 + 1500 * (t / dur), 1.5) * np.linspace(0, 1, s.n_samples(dur)) * 0.8
    x = (s.saturate(e * 0.4, 2.0) + inhale) * np.linspace(0, 1, s.n_samples(dur)) ** 1.6
    return finish(x, HALL, 0.25, tail=0.3, fade_out=0.02)


def world_eater_breath_loop():
    dur = 4.0
    e = energy(dur, 110.0, 1200, spread=0.025, buzz=0.6)
    e = s.lowpass(e, 3800)
    roar = s.lowpass(s.pink(dur, 1201), 1600) * 0.8
    trem = 0.8 + 0.2 * np.sin(2 * np.pi * 7.5 * s.timeline(dur))
    x = s.saturate((e * 0.35 + roar) * trem, 2.2)
    x = s.dc_block(x)
    x = s.make_loopable(x, 0.4)
    return s.normalize(x, 0.85)


def sky_crack(dur, seed):
    """Thunder-like crack: dense impulses whose density and brightness fall away."""
    rng = np.random.default_rng(seed)
    n = s.n_samples(dur)
    imp = np.zeros(n)
    t = np.arange(n) / s.SR
    density = np.exp(-t / 0.35)
    mask = rng.random(n) < density * 0.02
    imp[mask] = rng.standard_normal(mask.sum())
    crack = s.sweep_lp(imp, lambda tt: 8000 * np.exp(-tt / 0.5) + 300) * 3
    rumble = s.lowpass(s.brown(dur, seed + 1), 180) * s.decay(dur, dur / 3)
    return crack + rumble


def world_eater_meteor_summon():
    dur = 3.5
    out = sky_crack(dur, 1300)
    # Glass sky shattering: falling cascade of bright partials
    rng = np.random.default_rng(1301)
    for i in range(55):
        f = rng.uniform(2000, 9000)
        d = rng.uniform(0.2, 0.9)
        s.place(out, s.sine(np.full(s.n_samples(d), f)) * s.decay(d, d / 6), rng.uniform(0.05, 1.6), rng.uniform(0.03, 0.1))
    swell = s.lowpass(s.supersaw(np.full(s.n_samples(dur), 41.2), 5, 0.02, 1302), 300) * amp_env(dur, [(0, 0), (1.0, 0.8), (dur, 0)])
    return finish(out + swell * 0.6, CAVERN, 0.35, tail=1.5)


def world_eater_gravity_well():
    dur = 2.8
    t = s.timeline(dur)
    pulse = 0.5 + 0.5 * np.sin(2 * np.pi * s.curve(dur, [(0, 2), (dur, 9)]).cumsum() / s.SR)
    sub = s.sine(s.curve(dur, [(0, 60), (dur, 32)])) * pulse
    # Reversed swell: air being dragged inward
    pull = s.sweep_bp(s.pink(dur, 1400), lambda tt: 3000 - 2600 * (tt / dur), 2.0) * np.linspace(0, 1, len(t)) ** 2
    phaser = s.tv_filter(s.supersaw(np.full(len(t), 82.4), 5, 0.03, 1401),
                         lambda tt, ff: 0.3 + np.abs(np.sin(ff / (300 + 250 * np.sin(2 * np.pi * 0.7 * tt)))))
    x = sub * 0.9 + pull + s.lowpass(phaser, 2500) * 0.25
    return finish(x * amp_env(dur, [(0, 0), (0.4, 1), (dur - 0.3, 1), (dur, 0)]), HALL, 0.3, tail=0.8)


def choir_chord(dur, midis, vowel="ah", seed=0, breath=0.08):
    formants = {"ah": [(800, 90, 1.0), (1150, 110, 0.5), (2900, 170, 0.25), (3900, 250, 0.1)],
                "oh": [(450, 70, 1.0), (800, 80, 0.45), (2830, 160, 0.15), (3800, 250, 0.06)],
                "oo": [(325, 60, 1.0), (700, 70, 0.3), (2530, 170, 0.06), (3500, 250, 0.03)]}[vowel]
    out = np.zeros(s.n_samples(dur))
    t = s.timeline(dur)
    for i, m in enumerate(midis):
        f = 440 * 2 ** ((m - 69) / 12)
        for voice in range(3):
            vib = 1 + 0.006 * np.sin(2 * np.pi * (5.0 + 0.4 * voice) * t + voice) + 0.004 * s.smooth_random(dur, 2, seed + i * 7 + voice)
            fv = f * vib * (1 + 0.004 * (voice - 1))

            def amp(k, pf):
                g = s.formant_gain(pf, formants)
                return (g + 0.01) / k ** 0.6
            out += s.additive(fv, dur, amp, max_hz=6000, seed=seed + i * 13 + voice)
    out += s.bandpass(s.white(dur, seed + 99), 2500, 0.6) * breath * np.std(out)
    return out / (np.std(out) + 1e-9) * 0.25


def world_eater_phase_shift():
    dur = 4.5
    ch = choir_chord(dur, [38, 45, 50, 53, 57, 62], "ah", seed=1500)
    ch *= amp_env(dur, [(0, 0), (1.6, 1.0), (3.4, 0.9), (dur, 0)])
    boom = thud(2.5, 110, 26, 0.7, 1501, debris=0.3)
    out = ch * 1.4
    s.place(out, boom, 1.4, 0.9)
    s.place(out, world_eater_roar(0) * 0.45, 1.55)
    return finish(out, CAVERN, 0.35, tail=1.5, fade_out=0.6)


# ---------------------------------------------------------------------------------------------------------------------
# Meteors
# ---------------------------------------------------------------------------------------------------------------------

def fire_crackle(dur, seed, density=0.004):
    rng = np.random.default_rng(seed)
    n = s.n_samples(dur)
    imp = (rng.random(n) < density) * rng.standard_normal(n)
    return s.bandpass(imp, 2800, 0.6) * 2 + s.lowpass(s.pink(dur, seed + 1), 1200) * 0.4


def void_meteor_fall(v):
    dur = 2.6
    # Descending scream (Doppler-like) of something huge burning through the sky
    f = s.exp_curve(dur, [(0, 1700 + 200 * v), (dur, 380)])
    tone = s.sweep_bp(s.white(dur, 1600 + v), lambda t: np.interp(t, s.timeline(dur)[::512], f[::512]), 9) * 2.5
    roar = s.lowpass(s.pink(dur, 1610 + v), 900) * np.linspace(0.2, 1, s.n_samples(dur))
    x = (tone + roar + fire_crackle(dur, 1620 + v) * 0.6) * np.linspace(0.05, 1, s.n_samples(dur)) ** 1.3
    return finish(x, HALL, 0.25, tail=0.3, fade_out=0.15)


def void_meteor_impact(v):
    dur = 2.4
    x = thud(dur, 180, 30, 0.6, 1700 + v, debris=1.0) * 1.2
    blast = s.sweep_lp(s.white(dur, 1710 + v), lambda t: 9000 * np.exp(-t / 0.18) + 200) * s.decay(dur, 0.35)
    x += blast * 0.9
    rng = np.random.default_rng(1720 + v)
    for _ in range(30):
        f = rng.uniform(1800, 7500)
        d = rng.uniform(0.15, 0.7)
        s.place(x, s.sine(np.full(s.n_samples(d), f)) * s.decay(d, d / 6), rng.uniform(0.05, 0.9), rng.uniform(0.02, 0.07))
    x += fire_crackle(dur, 1730 + v, 0.002) * s.decay(dur, 0.9) * 0.4
    return finish(s.saturate(x * 0.8, 1.6), CAVERN, 0.3, tail=1.2)


# ---------------------------------------------------------------------------------------------------------------------
# Voidlings
# ---------------------------------------------------------------------------------------------------------------------

def chitter(dur, rate, f, seed):
    rng = np.random.default_rng(seed)
    out = np.zeros(s.n_samples(dur))
    t = 0.0
    while t < dur - 0.05:
        d = rng.uniform(0.012, 0.03)
        click = s.bandpass(s.white(d, int(rng.integers(1e6))), f * rng.uniform(0.8, 1.3), 5) * s.decay(d, d / 3)
        s.place(out, click, t, rng.uniform(0.6, 1.0))
        t += 1.0 / rate * rng.uniform(0.6, 1.4)
    return out


def voidling_ambient(v):
    dur = 1.1
    c = chitter(dur, 22 + 4 * v, 2600 + 300 * v, 1800 + v)
    squeak = s.sine(s.curve(dur, [(0, 900), (0.4, 1400 + 100 * v), (dur, 1000)])) * amp_env(dur, [(0, 0), (0.3, 0.3), (0.6, 0), (dur, 0)])
    return finish(c + squeak * 0.4, ROOM, 0.2, tail=0.3)


def voidling_hurt(v):
    dur = 0.45
    sq = s.saw(s.curve(dur, [(0, 1500 + 200 * v), (dur, 700)]))
    sq = s.bandpass(sq, 1800, 1.5) * s.decay(dur, 0.12)
    return finish(sq + chitter(dur, 40, 3000, 1900 + v) * 0.5, ROOM, 0.2, tail=0.2)


def voidling_death():
    dur = 1.2
    sq = s.bandpass(s.saw(s.exp_curve(dur, [(0, 1600), (dur, 200)])), 1400, 1.2) * s.decay(dur, 0.25)
    dissolve = s.sweep_bp(s.white(dur, 1950), lambda t: 6000 - 5000 * t / dur, 3) * amp_env(dur, [(0, 0), (0.2, 1), (dur, 0)])
    return finish(sq + dissolve * 0.7, ROOM, 0.3, tail=0.4)


# ---------------------------------------------------------------------------------------------------------------------
# Arena
# ---------------------------------------------------------------------------------------------------------------------

def bell(dur, f, seed, tau=2.5):
    ratios = [0.5, 1.0, 1.183, 1.506, 2.0, 2.514, 2.662, 3.011, 4.166, 5.433]
    out = np.zeros(s.n_samples(dur))
    rng = np.random.default_rng(seed)
    for i, r in enumerate(ratios):
        d = s.decay(dur, tau / (1 + i * 0.35))
        out += s.sine(np.full(len(out), f * r * (1 + rng.uniform(-0.001, 0.001)))) * d / (1 + i * 0.4)
    return out


def void_altar_activate():
    dur = 5.0
    out = bell(dur, 98.0, 2000, tau=3.0) * 0.8
    s.place(out, bell(dur - 0.8, 146.8, 2001, tau=2.5) * 0.6, 0.8)
    ch = choir_chord(dur, [50, 57, 62, 65, 69], "oh", seed=2002) * amp_env(dur, [(0, 0), (2.0, 1.0), (dur, 0)])
    ignite = s.sweep_lp(s.pink(1.2, 2003), lambda t: 300 + 7000 * (t / 1.2)) * np.linspace(0, 1, s.n_samples(1.2)) ** 2
    s.place(out, ignite * 0.6, 1.5)
    s.place(out, thud(2.0, 120, 30, 0.6, 2004, 0.2) * 0.7, 2.7)
    return finish(out + ch, CAVERN, 0.35, tail=1.5, fade_out=0.8)


def void_altar_ambient():
    dur = 6.0
    t = s.timeline(dur)
    hum = s.sine(np.full(len(t), 55.0)) + 0.5 * s.sine(np.full(len(t), 110.3)) + 0.25 * s.sine(np.full(len(t), 164.6))
    hum *= 0.8 + 0.2 * np.sin(2 * np.pi * 0.5 * t)
    shimmer = np.zeros(len(t))
    for f in (1318.5, 1760.0, 2349.3):
        shimmer += s.sine(np.full(len(t), f)) * (0.5 + 0.5 * np.sin(2 * np.pi * (0.33 + f / 10000) * t)) * 0.06
    x = s.reverb(hum * 0.5 + shimmer, HALL, 0.3)
    x = s.make_loopable(s.dc_block(x), 0.8)
    return s.normalize(x, 0.6)


def runic_stone_awaken(v):
    dur = 1.6
    whomp = s.sweep_lp(s.pink(dur, 2100 + v), lambda t: 200 + 2500 * np.exp(-((t - 0.25) ** 2) / 0.02)) * s.decay(dur, 0.4)
    shimmer = bell(dur, 523.25 * (1 + 0.12 * v), 2110 + v, tau=1.0) * 0.4
    return finish(whomp + shimmer, HALL, 0.3, tail=0.6)


# ---------------------------------------------------------------------------------------------------------------------
# Gear and effects
# ---------------------------------------------------------------------------------------------------------------------

def void_greatsword_slash(v):
    dur = 0.8
    air = whoosh(dur, 3200, 500, 2200 + v, q=1.8, shape=2.5)
    tear = s.sweep_bp(s.supersaw(np.full(s.n_samples(dur), 220.0 + 30 * v), 5, 0.04, 2210 + v),
                      lambda t: 4000 * np.exp(-t / 0.15) + 300, 4) * s.decay(dur, 0.2)
    return finish(air + tear * 0.6 + claw_ring(dur, 2220 + v) * 0.15, HALL, 0.2, tail=0.5)


def staff_fire(v):
    dur = 0.9
    f = s.exp_curve(dur, [(0, 900 + 100 * v), (dur, 120)])
    zap = s.saturate(energy(dur, f / 4, 2300 + v, 0.04, 0.3) * 0.4, 2.0) * s.decay(dur, 0.25)
    pew = s.sine(f) * s.decay(dur, 0.12) * 0.5
    return finish(zap + pew, HALL, 0.25, tail=0.5)


def armor_equip(v):
    dur = 0.7
    rng = np.random.default_rng(2400 + v)
    out = np.zeros(s.n_samples(dur))
    for at in (0.0, 0.11, 0.2):
        d = 0.4
        clink = np.zeros(s.n_samples(d))
        base = rng.uniform(1700, 2300)
        for r in (1.0, 2.76, 5.4):
            clink += s.sine(np.full(len(clink), base * r)) * s.decay(d, 0.08 / r)
        s.place(out, clink, at + rng.uniform(0, 0.02), 0.4)
    rustle = s.bandpass(s.white(dur, 2410 + v), 4000, 0.8) * amp_env(dur, [(0, 0), (0.05, 0.5), (0.3, 0.3), (dur, 0)])
    return finish(out + rustle * 0.6, ROOM, 0.2, tail=0.2)


def void_blink():
    dur = 0.7
    rev = whoosh(dur, 300, 5000, 2500, q=1.4, shape=1) * np.linspace(0, 1, s.n_samples(dur)) ** 2
    pop = s.sine(s.exp_curve(0.2, [(0, 1200), (0.2, 200)])) * s.decay(0.2, 0.04)
    out = s.pad_to(rev, 1.0)
    s.place(out, pop, 0.68, 0.8)
    return finish(out, HALL, 0.25, tail=0.4)


def erosion_apply():
    dur = 1.2
    crumble = np.zeros(s.n_samples(dur))
    rng = np.random.default_rng(2600)
    for _ in range(60):
        d = rng.uniform(0.01, 0.05)
        s.place(crumble, s.bandpass(s.white(d, int(rng.integers(1e6))), rng.uniform(800, 3000), 2) * s.decay(d, d / 3),
                rng.uniform(0, 0.9), rng.uniform(0.1, 0.4))
    dark = s.lowpass(s.supersaw(np.full(s.n_samples(dur), 73.4), 5, 0.03, 2601), 600) * amp_env(dur, [(0, 0), (0.2, 0.6), (dur, 0)])
    hiss = s.highpass(s.white(dur, 2602), 5000) * amp_env(dur, [(0, 0), (0.1, 0.25), (dur, 0)])
    return finish(crumble + dark * 0.5 + hiss, ROOM, 0.25, tail=0.3)


# ---------------------------------------------------------------------------------------------------------------------

SOUNDS = {
    "entity/world_eater/ambient1": lambda: world_eater_ambient(0),
    "entity/world_eater/ambient2": lambda: world_eater_ambient(1),
    "entity/world_eater/ambient3": lambda: world_eater_ambient(2),
    "entity/world_eater/hurt1": lambda: world_eater_hurt(0),
    "entity/world_eater/hurt2": lambda: world_eater_hurt(1),
    "entity/world_eater/hurt3": lambda: world_eater_hurt(2),
    "entity/world_eater/death": world_eater_death,
    "entity/world_eater/roar1": lambda: world_eater_roar(0),
    "entity/world_eater/roar2": lambda: world_eater_roar(1),
    "entity/world_eater/step1": lambda: world_eater_step(0),
    "entity/world_eater/step2": lambda: world_eater_step(1),
    "entity/world_eater/step3": lambda: world_eater_step(2),
    "entity/world_eater/wing_flap1": lambda: world_eater_wing_flap(0),
    "entity/world_eater/wing_flap2": lambda: world_eater_wing_flap(1),
    "entity/world_eater/wing_flap3": lambda: world_eater_wing_flap(2),
    "entity/world_eater/takeoff": world_eater_takeoff,
    "entity/world_eater/land1": lambda: world_eater_land(0),
    "entity/world_eater/land2": lambda: world_eater_land(1),
    "entity/world_eater/swipe1": lambda: world_eater_swipe(0),
    "entity/world_eater/swipe2": lambda: world_eater_swipe(1),
    "entity/world_eater/swipe3": lambda: world_eater_swipe(2),
    "entity/world_eater/tail_sweep1": lambda: world_eater_tail_sweep(0),
    "entity/world_eater/tail_sweep2": lambda: world_eater_tail_sweep(1),
    "entity/world_eater/wing_gust": world_eater_wing_gust,
    "entity/world_eater/breath_charge": world_eater_breath_charge,
    "entity/world_eater/breath_loop": world_eater_breath_loop,
    "entity/world_eater/meteor_summon": world_eater_meteor_summon,
    "entity/world_eater/gravity_well": world_eater_gravity_well,
    "entity/world_eater/phase_shift": world_eater_phase_shift,
    "entity/void_meteor/fall1": lambda: void_meteor_fall(0),
    "entity/void_meteor/fall2": lambda: void_meteor_fall(1),
    "entity/void_meteor/impact1": lambda: void_meteor_impact(0),
    "entity/void_meteor/impact2": lambda: void_meteor_impact(1),
    "entity/void_meteor/impact3": lambda: void_meteor_impact(2),
    "entity/voidling/ambient1": lambda: voidling_ambient(0),
    "entity/voidling/ambient2": lambda: voidling_ambient(1),
    "entity/voidling/hurt1": lambda: voidling_hurt(0),
    "entity/voidling/hurt2": lambda: voidling_hurt(1),
    "entity/voidling/death": voidling_death,
    "block/void_altar/activate": void_altar_activate,
    "block/void_altar/ambient": void_altar_ambient,
    "block/runic_void_stone/awaken1": lambda: runic_stone_awaken(0),
    "block/runic_void_stone/awaken2": lambda: runic_stone_awaken(1),
    "item/void_greatsword/slash1": lambda: void_greatsword_slash(0),
    "item/void_greatsword/slash2": lambda: void_greatsword_slash(1),
    "item/world_eater_staff/fire1": lambda: staff_fire(0),
    "item/world_eater_staff/fire2": lambda: staff_fire(1),
    "item/armor/equip_void_scale1": lambda: armor_equip(0),
    "item/armor/equip_void_scale2": lambda: armor_equip(1),
    "item/void_scale_armor/blink": void_blink,
    "effect/erosion/apply": erosion_apply,
}


def main(filters):
    for name, fn in SOUNDS.items():
        if filters and not any(f in name for f in filters):
            continue
        audio = fn()
        s.write_ogg(os.path.join(OUT, name + ".ogg"), audio, quality=5)
        print(f"{name:45s} {len(audio) / s.SR:5.2f}s")


if __name__ == "__main__":
    main(sys.argv[1:])
