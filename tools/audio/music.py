"""'Aetherfall - The World Eater': the original battle theme (also the music disc).

Run from the repository root:
    python3 tools/audio/music.py

192.0 s exactly (96 bars at 120 BPM, D minor, rising to E minor for the climax), stereo, 44.1 kHz.
The track begins and ends on the void drone so it loops cleanly as boss music.

Form (bars):
  0-7    Intro     void drone, distant choir, celesta starlight, far-off war drums
  8-23   Theme A   string ostinato, taiko, brass states the World Eater motif (twice, second time doubled)
  24-31  Build     harmonic climb, snare roll, riser
  32-47  Theme B   the choir takes the melody over full percussion
  48-55  Break     the eye of the storm: heartbeat sub, celesta, tremolo strings
  56-71  Theme A'  full orchestra, high string counter-line, crashes
  72-87  Climax    everything up a whole step to E minor
  88-95  Outro     the motif slows, the drone returns, a final boom, silence
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import synth as s  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "src", "main", "resources", "assets", "aetherfall", "sounds", "music", "world_eater.ogg")

BPM = 120
BEAT = 60.0 / BPM
BAR = BEAT * 4
BARS = 96
LENGTH = BARS * BAR  # 192.0 s
N = s.n_samples(LENGTH)


def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def at(bar, beat=0.0):
    return bar * BAR + beat * BEAT


class Bus:
    """A stereo bus with its own reverb send."""

    def __init__(self, name, send=0.25):
        self.name = name
        self.send = send
        self.l = np.zeros(N + s.n_samples(8))
        self.r = np.zeros(N + s.n_samples(8))

    def add(self, x, t, gain=1.0, pan=0.0):
        start = s.n_samples(t)
        if start >= N:
            return
        end = min(len(self.l), start + len(x))
        seg = x[:end - start] * gain
        gl = np.cos((pan + 1) * np.pi / 4)
        gr = np.sin((pan + 1) * np.pi / 4)
        self.l[start:end] += seg * gl
        self.r[start:end] += seg * gr


# ---------------------------------------------------------------------------------------------------------------------
# Instruments
# ---------------------------------------------------------------------------------------------------------------------

_cache = {}


def cached(key, fn):
    if key not in _cache:
        _cache[key] = fn()
    return _cache[key]


VOWELS = {
    "ah": [(800, 90, 1.0), (1150, 110, 0.5), (2900, 170, 0.25), (3900, 250, 0.1)],
    "oh": [(450, 70, 1.0), (800, 80, 0.45), (2830, 160, 0.15), (3800, 250, 0.06)],
    "oo": [(325, 60, 1.0), (700, 70, 0.3), (2530, 170, 0.06), (3500, 250, 0.03)],
}


def choir_note(midi, dur, vowel="ah", seed=0, voices=3, attack=0.35, release=0.6):
    def render():
        t = s.timeline(dur + release)
        out = np.zeros(len(t))
        for v in range(voices):
            vib = 1 + 0.0055 * np.sin(2 * np.pi * (4.8 + 0.37 * v) * t + v * 1.7) \
                + 0.003 * s.smooth_random(dur + release, 2.5, seed * 31 + v)
            f = hz(midi) * vib * (1 + 0.0035 * (v - (voices - 1) / 2))

            def amp(k, pf):
                return (s.formant_gain(pf, VOWELS[vowel]) + 0.012) / k ** 0.55
            out += s.additive(f, dur + release, amp, max_hz=5500, seed=seed * 7 + v)
        breath = s.bandpass(s.white(dur + release, seed + 500), 3000, 0.7) * 0.05 * np.std(out)
        env = s.adsr(dur + release, a=attack, d=0.2, s=0.9, r=release)
        return (out + breath) * env / (np.std(out) + 1e-9)
    return cached(("choir", midi, round(dur, 3), vowel, seed % 4), render)


def string_note(midi, dur, seed=0, bright=2600.0, attack=0.006, release=0.08):
    def render():
        total = dur + release
        f = hz(midi) * (1 + 0.002 * s.smooth_random(total, 5, seed))
        x = s.supersaw(f, 5, 0.008, seed)
        x = s.lowpass(x, bright, 2)
        return x * s.adsr(total, a=attack, d=0.05, s=0.75, r=release)
    return cached(("str", midi, round(dur, 3), int(bright), seed % 3, attack), render)


def string_pad(midi, dur, seed=0, tremolo=0.0):
    def render():
        total = dur + 0.8
        t = s.timeline(total)
        f = hz(midi) * (1 + 0.004 * np.sin(2 * np.pi * 5.2 * t + seed))
        x = s.supersaw(f, 7, 0.01, seed)
        x = s.lowpass(x, 1800, 2)
        if tremolo:
            x *= 0.6 + 0.4 * np.abs(np.sin(2 * np.pi * tremolo * t))
        return x * s.adsr(total, a=0.5, d=0.3, s=0.85, r=0.8)
    return cached(("pad", midi, round(dur, 3), seed % 3, tremolo), render)


def brass_note(midi, dur, seed=0, bright=1.0):
    def render():
        total = dur + 0.25
        t = s.timeline(total)
        f = hz(midi) * (1 + 0.003 * np.sin(2 * np.pi * 5.0 * t) * np.clip(t / 0.4, 0, 1))
        # Lip buzz: saw plus a touch of pulse, two players slightly apart
        x = s.saw(f) + 0.8 * s.saw(f * 1.003, 0.4) + 0.3 * s.square(f * 0.998, 0.45)
        # Filter "blat": the tone opens on attack then settles, like a horn section digging in
        open_curve = lambda tt: (700 + 2200 * bright) * (1 + 1.2 * np.exp(-tt / 0.12)) * np.clip(tt / 0.03, 0.3, 1)
        x = s.sweep_lp(x, open_curve, 2)
        x = s.fft_filter(x, lambda ff: 1 + 0.8 * s.formant_gain(ff, [(1200, 400, 1.0)]))
        x = s.saturate(x * 0.4, 1.6)
        return x * s.adsr(total, a=0.04, d=0.15, s=0.8, r=0.25)
    return cached(("brass", midi, round(dur, 3), seed % 2, bright), render)


def celesta(midi, seed=0):
    def render():
        d = 1.6
        f = hz(midi)
        out = np.zeros(s.n_samples(d))
        for r, a, tau in ((1, 1.0, 0.7), (2, 0.35, 0.35), (3.01, 0.15, 0.2), (4.2, 0.08, 0.12), (6.8, 0.04, 0.06)):
            out += s.sine(np.full(len(out), f * r)) * s.decay(d, tau) * a
        return out
    return cached(("cel", midi), render)


def taiko(pitch=1.0, seed=0, size=1.0):
    def render():
        d = 1.4 * size
        body = s.sine(s.exp_curve(d, [(0, 150 * pitch), (0.04, 70 * pitch), (d, 52 * pitch)])) * s.decay(d, 0.32 * size)
        skin = s.lowpass(s.white(d, seed), 1200) * s.decay(d, 0.05)
        slap = s.bandpass(s.white(0.03, seed + 1), 2500, 1) * s.decay(0.03, 0.006)
        x = s.saturate(body * 1.4, 1.5) + skin * 0.6
        x[:len(slap)] += slap * 0.4
        return x
    return cached(("taiko", pitch, seed % 4, size), render)


def snare(seed=0):
    def render():
        d = 0.35
        body = s.sine(s.exp_curve(d, [(0, 330), (d, 180)])) * s.decay(d, 0.05)
        wires = s.bandpass(s.white(d, seed), 4500, 0.5) * s.decay(d, 0.11)
        return body * 0.6 + wires
    return cached(("snare", seed % 4), render)


def crash(seed=0):
    def render():
        d = 3.5
        x = s.highpass(s.white(d, seed), 4500) * s.decay(d, 0.9)
        x += s.bandpass(s.white(d, seed + 1), 7500, 2) * s.decay(d, 1.4) * 0.5
        return x * 0.5
    return cached(("crash", seed % 2), render)


def boom(seed=0):
    def render():
        d = 4.0
        x = s.sine(s.exp_curve(d, [(0, 110), (0.3, 36), (d, 26)])) * s.decay(d, 1.2)
        x = s.saturate(x * 1.6, 2.0) + s.lowpass(s.brown(d, seed), 300) * s.decay(d, 0.7) * 0.4
        return x
    return cached(("boom", seed % 2), render)


def riser(dur, seed=0):
    x = s.sweep_bp(s.white(dur, seed), lambda t: 300 + 8000 * (t / dur) ** 2, 2.0)
    tone = s.supersaw(s.exp_curve(dur, [(0, 110), (dur, 880)]), 5, 0.03, seed)
    x = x + s.lowpass(tone, 4000) * 0.3
    return x * np.linspace(0, 1, s.n_samples(dur)) ** 2.5


def heartbeat(seed=0):
    def render():
        d = 0.8
        x = s.sine(s.exp_curve(d, [(0, 70), (d, 38)])) * s.decay(d, 0.16)
        return s.lowpass(x, 200)
    return cached(("heart",), render)


# ---------------------------------------------------------------------------------------------------------------------
# Harmony and melody (MIDI numbers; D minor)
# ---------------------------------------------------------------------------------------------------------------------

D2, A2, D3 = 38, 45, 50

CHORDS = {
    "Dm": [38, 50, 53, 57, 62], "Bb": [34, 46, 50, 53, 58], "Gm": [31, 43, 50, 55, 58], "A": [33, 45, 49, 52, 57],
    "F": [29, 41, 48, 53, 57], "C": [36, 48, 52, 55, 60], "Em": [40, 52, 55, 59, 64], "Cmaj": [36, 48, 52, 55, 60],
    "Am": [33, 45, 52, 57, 60], "B": [35, 47, 51, 54, 59], "G": [31, 43, 50, 55, 59], "D": [38, 50, 54, 57, 62],
}

# Theme A: the World Eater motif. (beat offset within the 8-bar phrase, length in beats, midi)
THEME_A = [
    (0, 2, 62), (2, 1, 69), (3, 0.5, 67), (3.5, 0.5, 65),
    (4, 1.5, 64), (5.5, 0.5, 65), (6, 2, 62),
    (8, 2, 65), (10, 1, 70), (11, 0.5, 69), (11.5, 0.5, 67),
    (12, 3, 69),
    (16, 2, 67), (18, 1, 70), (19, 1, 74),
    (20, 1.5, 72), (21.5, 0.5, 70), (22, 2, 69),
    (24, 1, 69), (25, 1, 73), (26, 1, 76), (27, 0.5, 74), (27.5, 0.5, 73),
    (28, 4, 69),
]
PROG_A = ["Dm", "Dm", "Bb", "Bb", "Gm", "Gm", "A", "A"]

THEME_B = [
    (0, 3, 69), (3, 1, 74), (4, 2, 72), (6, 2, 69),
    (8, 3, 67), (11, 1, 64), (12, 4, 73),
    (16, 3, 74), (19, 1, 77), (20, 2, 76), (22, 2, 72),
    (24, 2, 74), (26, 2, 69), (28, 2, 73), (30, 2, 76),
]
PROG_B = ["Dm", "F", "C", "A", "Bb", "C", "Dm", "A"]

# E minor equivalents for the climax (+2 semitones)
UP = {"Dm": "Em", "F": "G", "C": "D", "A": "B", "Bb": "Cmaj", "Gm": "Am"}


def chord(name, shift=0):
    return [m + shift for m in CHORDS[name]]


# ---------------------------------------------------------------------------------------------------------------------
# Arrangement
# ---------------------------------------------------------------------------------------------------------------------

def compose():
    choir = Bus("choir", 0.45)
    strings = Bus("strings", 0.3)
    brass = Bus("brass", 0.3)
    drums = Bus("drums", 0.22)
    fx = Bus("fx", 0.4)
    keys = Bus("keys", 0.5)

    def pad_chords(bar0, prog, bars_per, vowel, gain, shift=0, seed=0):
        for i, c in enumerate(prog):
            notes = chord(c, shift)
            dur = bars_per * BAR
            for j, m in enumerate(notes[1:]):
                x = choir_note(m, dur, vowel, seed + j, voices=3, attack=0.6)
                choir.add(x, at(bar0 + i * bars_per), gain, pan=-0.5 + j * 0.25)

    def ostinato(bar0, prog, bars_per, gain, shift=0, octave=0, bright=2600):
        # 16th-note pulse: root, root, fifth, root, third, root, fifth, octave (the "devouring" figure)
        figure = [0, 0, 7, 0, 3, 0, 7, 12]
        for i, c in enumerate(prog):
            root = CHORDS[c][1] + shift + octave
            third = CHORDS[c][2] - CHORDS[c][1]
            for b in range(bars_per * 16):
                step = figure[b % 8]
                interval = third if step == 3 else step
                m = root + interval
                accent = 1.0 if b % 4 == 0 else 0.72
                x = string_note(m, 0.12, seed=b, bright=bright)
                t = at(bar0 + i * bars_per) + b * BEAT / 4
                strings.add(x, t, gain * accent, pan=-0.35)
                strings.add(string_note(m - 12, 0.12, seed=b + 1, bright=bright * 0.7), t, gain * accent * 0.8, pan=0.35)

    def bass(bar0, prog, bars_per, gain, shift=0):
        for i, c in enumerate(prog):
            m = CHORDS[c][0] + shift
            for half in range(bars_per * 2):
                x = string_note(m, BAR / 2 - 0.05, seed=half, bright=600, attack=0.02, release=0.2)
                strings.add(x, at(bar0 + i * bars_per) + half * BAR / 2, gain)

    def melody(bar0, theme, inst, gain, shift=0, octave=0, pan=0.0, vowel="ah"):
        for (b, d, m) in theme:
            mm = m + shift + octave
            if inst == "brass":
                brass.add(brass_note(mm, d * BEAT), at(bar0, b), gain, pan)
            elif inst == "choir":
                choir.add(choir_note(mm, d * BEAT, vowel, seed=int(b), voices=4, attack=0.12, release=0.4), at(bar0, b), gain, pan)
            elif inst == "strings":
                strings.add(string_note(mm, d * BEAT, seed=int(b), bright=3800, attack=0.05, release=0.3), at(bar0, b), gain, pan)

    def groove(bar0, bars, gain, full=True):
        for bar in range(bar0, bar0 + bars):
            # Big drum on 1 and the "and" of 2, toms answer on 3 and 4: a heavy, stomping 4/4
            drums.add(taiko(1.0, bar, 1.3), at(bar, 0), gain)
            drums.add(taiko(1.0, bar + 1, 1.1), at(bar, 1.5), gain * 0.7)
            drums.add(taiko(1.5, bar + 2), at(bar, 2), gain * 0.6, pan=-0.4)
            drums.add(taiko(1.8, bar + 3), at(bar, 3), gain * 0.55, pan=0.4)
            if full:
                drums.add(taiko(1.8, bar + 4), at(bar, 3.5), gain * 0.45, pan=0.4)
                drums.add(snare(bar), at(bar, 1), gain * 0.5)
                drums.add(snare(bar + 1), at(bar, 3), gain * 0.5)
                for e in range(8):
                    drums.add(snare(e) * 0.25, at(bar, e * 0.5 + 0.25), gain * 0.18, pan=0.2 if e % 2 else -0.2)

    def snare_roll(bar0, bars, gain):
        total = bars * 16
        for i in range(total):
            g = gain * (0.15 + 0.85 * (i / total) ** 2)
            drums.add(snare(i), at(bar0) + i * BEAT / 4, g, pan=0.1 * np.sin(i))

    def starlight(bar0, bars, notes, gain):
        rng = np.random.default_rng(bar0)
        for b in range(bars * 8):
            m = notes[b % len(notes)] + (12 if rng.random() < 0.3 else 0)
            keys.add(celesta(m), at(bar0) + b * BEAT / 2, gain * rng.uniform(0.7, 1.0), pan=rng.uniform(-0.7, 0.7))

    def drone(bar0, bars, gain, midi=D2):
        dur = bars * BAR
        x = s.supersaw(np.full(s.n_samples(dur), hz(midi)), 7, 0.006, bar0)
        x = s.lowpass(x, 260, 2) * s.adsr(dur, a=2.0, d=0.5, s=0.9, r=2.0)
        y = s.sine(np.full(len(x), hz(midi) / 2)) * s.adsr(dur, a=2.0, d=0.5, s=0.9, r=2.0)
        fx.add(x * 0.7 + y * 0.25, at(bar0), gain)

    # Intro (0-7)
    drone(0, 8, 0.2)
    pad_chords(0, ["Dm", "Bb", "Gm", "A"], 2, "oo", 0.1)
    starlight(4, 4, [74, 77, 81, 86, 81, 77], 0.12)
    for bar in (4, 5, 6, 7):
        drums.add(taiko(0.9, bar, 1.5), at(bar), 0.45)
    fx.add(boom(0), at(0), 0.5)
    fx.add(riser(BAR, 1), at(7), 0.35)

    # Theme A (8-23)
    for rep in range(2):
        b0 = 8 + rep * 8
        ostinato(b0, PROG_A, 1, 0.16)
        bass(b0, PROG_A, 1, 0.35)
        pad_chords(b0, PROG_A[::2], 2, "ah", 0.16)
        melody(b0, THEME_A, "brass", 0.42, octave=-12)
        if rep == 1:
            melody(b0, THEME_A, "brass", 0.25, pan=0.15)
        groove(b0, 8, 0.55, full=rep == 1)
    fx.add(boom(1), at(8), 0.6)
    drums.add(crash(0), at(8), 0.35)
    drums.add(crash(1), at(16), 0.35)

    # Build (24-31)
    build = ["Gm", "Gm", "Bb", "Bb", "C", "C", "A", "A"]
    ostinato(24, build, 1, 0.18, bright=3200)
    bass(24, build, 1, 0.38)
    pad_chords(24, build[::2], 2, "oh", 0.2)
    groove(24, 4, 0.5, full=False)
    snare_roll(28, 4, 0.5)
    fx.add(riser(4 * BAR, 2), at(28), 0.45)

    # Theme B (32-47)
    for rep in range(2):
        b0 = 32 + rep * 8
        ostinato(b0, PROG_B, 1, 0.17, bright=3200)
        bass(b0, PROG_B, 1, 0.4)
        melody(b0, THEME_B, "choir", 0.42, vowel="ah")
        melody(b0, THEME_B, "strings", 0.12, octave=12, pan=0.3)
        for i, c in enumerate(PROG_B):
            brass.add(brass_note(CHORDS[c][1], BAR - 0.1, bright=0.7), at(b0 + i), 0.3)
        groove(b0, 8, 0.62)
        drums.add(crash(rep), at(b0), 0.45)
    fx.add(boom(0), at(32), 0.7)

    # Break (48-55)
    breakp = ["Dm", "Bb", "Gm", "A"]
    pad_chords(48, breakp, 2, "oo", 0.15)
    for i, c in enumerate(breakp):
        for m in chord(c)[1:4]:
            strings.add(string_pad(m, 2 * BAR, seed=m, tremolo=6.0), at(48 + 2 * i), 0.07, pan=(m % 5 - 2) * 0.2)
    starlight(48, 8, [62, 65, 69, 74, 69, 65, 69, 72], 0.14)
    for bar in range(48, 56):
        drums.add(heartbeat(), at(bar, 0), 0.6)
        drums.add(heartbeat(), at(bar, 0.5), 0.4)
    fx.add(riser(2 * BAR, 3), at(54), 0.5)
    snare_roll(55, 1, 0.45)

    # Theme A' (56-71)
    for rep in range(2):
        b0 = 56 + rep * 8
        ostinato(b0, PROG_A, 1, 0.19, bright=3400)
        bass(b0, PROG_A, 1, 0.42)
        pad_chords(b0, PROG_A[::2], 2, "ah", 0.2)
        melody(b0, THEME_A, "brass", 0.45, octave=-12)
        melody(b0, THEME_A, "brass", 0.3)
        melody(b0, THEME_A, "choir", 0.22, vowel="oh")
        # High string counter-line: the motif inverted and an octave above, in quavers
        for i, c in enumerate(PROG_A):
            for e in range(8):
                m = chord(c)[2 + (e % 3)] + 12
                strings.add(string_note(m, BEAT / 2, seed=e, bright=4200), at(b0 + i, e * 0.5), 0.07, pan=0.5)
        groove(b0, 8, 0.66)
        for k in (0, 4):
            drums.add(crash(k), at(b0 + k), 0.4)
    fx.add(boom(1), at(56), 0.75)
    fx.add(riser(2 * BAR, 4), at(70), 0.5)

    # Climax (72-87): up a whole step
    for rep in range(2):
        b0 = 72 + rep * 8
        prog = [UP[c] for c in PROG_B]
        ostinato(b0, prog, 1, 0.2, bright=3600)
        bass(b0, prog, 1, 0.44)
        melody(b0, THEME_B, "choir", 0.46, shift=2)
        melody(b0, THEME_B, "brass", 0.34, shift=2, octave=-12)
        melody(b0, THEME_B, "strings", 0.14, shift=2, octave=12, pan=-0.3)
        pad_chords(b0, prog, 1, "ah", 0.12, seed=7)
        groove(b0, 8, 0.7)
        for k in (0, 4):
            drums.add(crash(k), at(b0 + k), 0.45)
    fx.add(boom(0), at(72), 0.8)
    snare_roll(87, 1, 0.55)

    # Outro (88-95)
    slow = [(0, 4, 62), (4, 2, 69), (6, 1, 67), (7, 1, 65), (8, 6, 64), (14, 2, 65), (16, 8, 62)]
    melody(88, slow, "brass", 0.4, octave=-12)
    pad_chords(88, ["Dm", "Bb", "A", "Dm"], 2, "oh", 0.24)
    drone(88, 8, 0.2)
    drums.add(taiko(1.0, 1, 1.5), at(88), 0.7)
    fx.add(boom(1), at(88), 0.8)
    fx.add(boom(0), at(92), 0.6)
    starlight(92, 2, [74, 69, 65, 62], 0.1)

    return [choir, strings, brass, drums, fx, keys]


def mixdown(buses):
    ir = s.make_ir(3.6, seed=42, damping=0.3, predelay=0.025, stereo=True)
    L = np.zeros(N + s.n_samples(8))
    R = np.zeros(N + s.n_samples(8))
    send_l = np.zeros_like(L)
    send_r = np.zeros_like(R)
    for bus in buses:
        L += bus.l
        R += bus.r
        send_l += bus.l * bus.send
        send_r += bus.r * bus.send
    wet_l = s.convolve_long(send_l, ir[0])[:len(L)]
    wet_r = s.convolve_long(send_r, ir[1])[:len(R)]
    L = L + wet_l * 0.9
    R = R + wet_r * 0.9
    out = np.stack([L[:N], R[:N]])
    out = np.stack([s.dc_block(out[0]), s.dc_block(out[1])])
    # Master: normalise, then light glue limiting on drum peaks only. Ceiling leaves headroom for Vorbis overshoot,
    # and the overall level sits close to vanilla Minecraft music so the theme never blasts over the game.
    out /= np.max(np.abs(out)) + 1e-9
    out = s.soft_limit(out * 1.15, ceiling=0.8, knee=0.6)
    # Fade the last bar into the drone tail so the loop seam is inaudible.
    fade_n = s.n_samples(BAR)
    out[:, -fade_n:] *= np.linspace(1, 0, fade_n) ** 1.5
    fade_in = s.n_samples(0.05)
    out[:, :fade_in] *= np.linspace(0, 1, fade_in)
    return out


def main():
    buses = compose()
    audio = mixdown(buses)
    s.write_ogg(OUT, audio, quality=6)
    rms = 20 * np.log10(np.sqrt(np.mean(audio ** 2)))
    print(f"wrote {OUT}: {audio.shape[1] / s.SR:.2f}s stereo, RMS {rms:.1f} dBFS")


if __name__ == "__main__":
    main()
