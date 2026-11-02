"""Minimal, fast DSP toolkit for Aetherfall's original sound design and score.

Everything is vectorised numpy: band-limited oscillators (PolyBLEP), coloured noise, static FFT filters,
time-varying STFT filters (formants, sweeps), convolution reverb, saturation and envelopes.
No third-party samples are used anywhere: every sound is synthesised from these primitives.
"""
import os
import subprocess
import tempfile
import wave

import numpy as np

SR = 44100


# ---------------------------------------------------------------------------------------------------------------------
# Time and envelopes
# ---------------------------------------------------------------------------------------------------------------------

def n_samples(seconds):
    return int(round(seconds * SR))


def timeline(seconds):
    return np.arange(n_samples(seconds)) / SR


def curve(seconds, points):
    """Piecewise-linear automation. points: [(time_s, value), ...]."""
    t = timeline(seconds)
    xs, ys = zip(*points)
    return np.interp(t, xs, ys)


def exp_curve(seconds, points):
    """Piecewise-exponential automation (interpolates in log space); values must be > 0."""
    t = timeline(seconds)
    xs, ys = zip(*points)
    return np.exp(np.interp(t, xs, np.log(ys)))


def adsr(seconds, a=0.01, d=0.1, s=0.7, r=0.2):
    n = n_samples(seconds)
    env = np.zeros(n)
    na, nd, nr = n_samples(a), n_samples(d), n_samples(r)
    ns = max(0, n - na - nd - nr)
    seg = []
    seg.append(np.linspace(0, 1, max(na, 1), endpoint=False))
    seg.append(np.linspace(1, s, max(nd, 1), endpoint=False))
    seg.append(np.full(ns, s))
    seg.append(np.linspace(s, 0, max(nr, 1)))
    env_full = np.concatenate(seg)
    env[:min(n, len(env_full))] = env_full[:n]
    return env


def decay(seconds, tau, attack=0.002):
    t = timeline(seconds)
    env = np.exp(-t / tau)
    na = n_samples(attack)
    if na > 0:
        env[:na] *= np.linspace(0, 1, na)
    return env


def smooth_random(seconds, rate_hz, seed, lo=-1.0, hi=1.0):
    """Smoothly wandering random control signal (cosine-interpolated random points)."""
    rng = np.random.default_rng(seed)
    n = n_samples(seconds)
    count = max(2, int(seconds * rate_hz) + 2)
    pts = rng.uniform(lo, hi, count)
    x = np.linspace(0, count - 1, n)
    i = np.floor(x).astype(int)
    f = x - i
    f = (1 - np.cos(f * np.pi)) / 2
    i1 = np.minimum(i + 1, count - 1)
    return pts[i] * (1 - f) + pts[i1] * f


# ---------------------------------------------------------------------------------------------------------------------
# Oscillators
# ---------------------------------------------------------------------------------------------------------------------

def _phase(freq, phase0=0.0):
    freq = np.asarray(freq, dtype=float)
    inc = freq / SR
    return (phase0 + np.cumsum(inc)) % 1.0, inc


def _polyblep(phase, dt):
    dt = np.maximum(dt, 1e-9)
    out = np.zeros_like(phase)
    m1 = phase < dt
    p = phase[m1] / dt[m1]
    out[m1] = p + p - p * p - 1.0
    m2 = phase > 1.0 - dt
    p = (phase[m2] - 1.0) / dt[m2]
    out[m2] = p * p + p + p + 1.0
    return out


def saw(freq, phase0=0.0):
    phase, dt = _phase(freq, phase0)
    dt = np.broadcast_to(dt, phase.shape).copy()
    return 2.0 * phase - 1.0 - _polyblep(phase, dt)


def square(freq, duty=0.5, phase0=0.0):
    phase, dt = _phase(freq, phase0)
    dt = np.broadcast_to(dt, phase.shape).copy()
    sq = np.where(phase < duty, 1.0, -1.0)
    sq += _polyblep(phase, dt)
    sq -= _polyblep((phase + (1 - duty)) % 1.0, dt)
    return sq


def sine(freq, phase0=0.0):
    phase, _ = _phase(freq, phase0)
    return np.sin(2 * np.pi * phase)


def supersaw(freq, voices=7, detune=0.012, seed=0):
    rng = np.random.default_rng(seed)
    out = np.zeros(len(np.atleast_1d(freq)) if np.ndim(freq) else 1)
    total = None
    for v in range(voices):
        spread = (v - (voices - 1) / 2) / max(1, (voices - 1) / 2)
        f = np.asarray(freq) * (1 + detune * spread)
        s = saw(f, rng.random())
        total = s if total is None else total + s
    return total / np.sqrt(voices)


def additive(freq, seconds, amp_fn, max_hz=9000.0, inharm=None, seed=0):
    """Additive synthesis. amp_fn(k, partial_freq_array) -> amplitude array for partial k (1-based).
    inharm: optional list of frequency ratios instead of harmonic series."""
    rng = np.random.default_rng(seed)
    n = n_samples(seconds)
    freq = np.broadcast_to(np.asarray(freq, dtype=float), (n,))
    out = np.zeros(n)
    ratios = inharm if inharm is not None else range(1, 200)
    base_peak = float(np.max(freq))
    for k, ratio in enumerate(ratios, start=1):
        if base_peak * ratio > max_hz:
            break
        pf = freq * ratio
        amp = amp_fn(k, pf)
        if np.all(np.asarray(amp) == 0):
            continue
        out += amp * sine(pf, rng.random())
    return out


# ---------------------------------------------------------------------------------------------------------------------
# Noise
# ---------------------------------------------------------------------------------------------------------------------

def white(seconds, seed):
    return np.random.default_rng(seed).standard_normal(n_samples(seconds))


def coloured(seconds, seed, slope_db_per_oct):
    """Noise with a spectral tilt: 0 = white, -3 = pink, -6 = brown."""
    x = white(seconds, seed)
    spec = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    f[0] = f[1]
    spec *= (f / 1000.0) ** (slope_db_per_oct / 6.02)
    y = np.fft.irfft(spec, len(x))
    return y / (np.std(y) + 1e-12)


def pink(seconds, seed):
    return coloured(seconds, seed, -3.0)


def brown(seconds, seed):
    return coloured(seconds, seed, -6.0)


# ---------------------------------------------------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------------------------------------------------

def fft_filter(x, response):
    """Zero-phase static filter. response(freqs_hz) -> linear gain."""
    spec = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    spec *= response(f)
    return np.fft.irfft(spec, len(x))


def lp_resp(cut, order=2):
    return lambda f: 1.0 / np.sqrt(1.0 + (f / cut) ** (2 * order))


def hp_resp(cut, order=2):
    return lambda f: 1.0 / np.sqrt(1.0 + (cut / np.maximum(f, 1e-3)) ** (2 * order))


def bp_resp(centre, q):
    def r(f):
        f = np.maximum(f, 1e-3)
        return 1.0 / np.sqrt(1.0 + (q * (f / centre - centre / f)) ** 2)
    return r


def lowpass(x, cut, order=2):
    return fft_filter(x, lp_resp(cut, order))


def highpass(x, cut, order=2):
    return fft_filter(x, hp_resp(cut, order))


def bandpass(x, centre, q):
    return fft_filter(x, bp_resp(centre, q))


FRAME = 2048
HOP = 512


def stft(x):
    win = np.hanning(FRAME)
    pad = np.concatenate([np.zeros(FRAME), x, np.zeros(FRAME)])
    frames = 1 + (len(pad) - FRAME) // HOP
    idx = np.arange(FRAME)[None, :] + HOP * np.arange(frames)[:, None]
    return np.fft.rfft(pad[idx] * win, axis=1), len(x)


def istft(spec, length):
    win = np.hanning(FRAME)
    frames = spec.shape[0]
    out = np.zeros(FRAME + HOP * (frames - 1))
    norm = np.zeros_like(out)
    blocks = np.fft.irfft(spec, FRAME, axis=1) * win
    for i in range(frames):
        out[i * HOP:i * HOP + FRAME] += blocks[i]
        norm[i * HOP:i * HOP + FRAME] += win * win
    out /= np.maximum(norm, 1e-6)
    return out[FRAME:FRAME + length]


def tv_filter(x, gain_fn):
    """Time-varying filter. gain_fn(t_frames[:,None], f_bins[None,:]) -> gain matrix."""
    spec, length = stft(x)
    t = (np.arange(spec.shape[0]) * HOP - FRAME) / SR
    t = np.clip(t, 0, None)
    f = np.fft.rfftfreq(FRAME, 1 / SR)
    spec *= gain_fn(t[:, None], f[None, :])
    return istft(spec, length)


def formant_gain(f, formants):
    """Sum of resonances. formants: list of (centre_hz, bandwidth_hz, gain) where centre may be an array over time."""
    g = np.zeros(np.broadcast_shapes(np.shape(f), np.shape(formants[0][0]) if np.ndim(formants[0][0]) else ()))
    for centre, bw, gain in formants:
        g = g + gain / (1.0 + ((f - centre) / (bw / 2.0)) ** 2)
    return g


def sweep_lp(x, cut_curve_fn, order=2):
    """Lowpass whose cutoff follows cut_curve_fn(t) (vectorised over STFT frames)."""
    return tv_filter(x, lambda t, f: 1.0 / np.sqrt(1.0 + (f / np.maximum(cut_curve_fn(t), 20.0)) ** (2 * order)))


def sweep_bp(x, centre_fn, q):
    def g(t, f):
        c = np.maximum(centre_fn(t), 20.0)
        ff = np.maximum(f, 1e-3)
        return 1.0 / np.sqrt(1.0 + (q * (ff / c - c / ff)) ** 2)
    return tv_filter(x, g)


# ---------------------------------------------------------------------------------------------------------------------
# Effects
# ---------------------------------------------------------------------------------------------------------------------

def saturate(x, drive=2.0):
    return np.tanh(drive * x) / np.tanh(drive)


def fold(x, amount=1.5):
    """Wavefolder for aggressive, metallic harmonics."""
    return np.sin(x * amount * np.pi / 2)


def bitcrush(x, bits=8):
    q = 2 ** (bits - 1)
    return np.round(x * q) / q


def make_ir(seconds, seed, damping=0.35, predelay=0.02, stereo=False, early=True):
    """Synthetic hall impulse response: decorrelated noise, exponential decay, high frequencies decay faster."""
    rng = np.random.default_rng(seed)
    chans = 2 if stereo else 1
    n = n_samples(seconds)
    t = np.arange(n) / SR
    out = []
    for c in range(chans):
        noise = rng.standard_normal(n)
        # Frequency-dependent decay: split in 4 bands with shorter tails for higher bands.
        bands = [(0, 300, 1.0), (300, 1500, 0.8), (1500, 5000, 0.55), (5000, 22050, 0.3)]
        ir = np.zeros(n)
        spec = np.fft.rfft(noise)
        f = np.fft.rfftfreq(n, 1 / SR)
        for lo, hi, life in bands:
            mask = ((f >= lo) & (f < hi)).astype(float)
            band = np.fft.irfft(spec * mask, n)
            tau = seconds * life * (1 - damping * 0.5) / 6.9
            ir += band * np.exp(-t / tau)
        if early:
            for k in range(8):
                d = int((predelay + rng.uniform(0.005, 0.06)) * SR)
                if d < n:
                    ir[d] += rng.uniform(-0.6, 0.6)
        pd = int(predelay * SR)
        ir = np.concatenate([np.zeros(pd), ir])[:n]
        ir /= np.sqrt(np.sum(ir ** 2)) + 1e-12
        out.append(ir)
    return np.stack(out) if stereo else out[0]


def convolve(x, ir):
    n = len(x) + len(ir) - 1
    size = 1 << (n - 1).bit_length()
    y = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)[:n]
    return y


def convolve_long(x, ir, block=1 << 17):
    """Overlap-add convolution for long signals (music)."""
    m = len(ir)
    size = 1 << (block + m - 1 - 1).bit_length()
    irf = np.fft.rfft(ir, size)
    y = np.zeros(len(x) + m - 1)
    for start in range(0, len(x), block):
        seg = x[start:start + block]
        conv = np.fft.irfft(np.fft.rfft(seg, size) * irf, size)[:len(seg) + m - 1]
        y[start:start + len(conv)] += conv
    return y


def reverb(x, ir, wet=0.3, keep_length=True):
    w = convolve(x, ir)
    dry = np.concatenate([x, np.zeros(len(w) - len(x))])
    y = dry * (1 - wet * 0.5) + w * wet
    return y if not keep_length else y[:len(x)]


def pitch_resample(x, ratio):
    """Changes pitch and duration together by ratio (>1 = higher, shorter)."""
    n_out = int(len(x) / ratio)
    src = np.arange(n_out) * ratio
    return np.interp(src, np.arange(len(x)), x)


def place(target, x, at_seconds, gain=1.0):
    start = n_samples(at_seconds)
    if start >= len(target):
        return target
    end = min(len(target), start + len(x))
    target[start:end] += x[:end - start] * gain
    return target


def pad_to(x, seconds):
    n = n_samples(seconds)
    if len(x) >= n:
        return x[:n]
    return np.concatenate([x, np.zeros(n - len(x))])


def fade(x, fade_in=0.005, fade_out=0.05):
    y = x.copy()
    ni, no = n_samples(fade_in), n_samples(fade_out)
    if ni > 0:
        y[:ni] *= np.linspace(0, 1, ni)
    if no > 0:
        y[-no:] *= np.linspace(1, 0, no) ** 2
    return y


def normalize(x, peak=0.89):
    m = np.max(np.abs(x)) + 1e-12
    return x * (peak / m)


def dc_block(x):
    return highpass(x, 18.0, 2)


def make_loopable(x, crossfade_s=0.25):
    """Crossfades the tail into the head so the sound loops with no click."""
    nc = n_samples(crossfade_s)
    head = x[:nc]
    tail = x[-nc:]
    w = np.linspace(0, 1, nc)
    body = x[nc:-nc] if len(x) > 2 * nc else x[nc:]
    joined = tail * np.sqrt(1 - w) + head * np.sqrt(w)
    return np.concatenate([joined, body])


def soft_limit(x, ceiling=0.95, knee=0.75):
    """Transparent below the knee, smoothly saturating to the ceiling above it."""
    y = x.copy()
    a = np.abs(y)
    over = a > knee
    span = ceiling - knee
    y[over] = np.sign(y[over]) * (knee + span * np.tanh((a[over] - knee) / span))
    return y


# ---------------------------------------------------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------------------------------------------------

def write_ogg(path, x, quality=6):
    """Writes mono (1D) or stereo (2 x N) audio as Ogg Vorbis via ffmpeg/libvorbis."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = np.asarray(x)
    if data.ndim == 2:
        data = data.T
        channels = 2
    else:
        channels = 1
    pcm = (np.clip(data, -1, 1) * 32767).astype("<i2")
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        with wave.open(tmp_path, "wb") as w:
            w.setnchannels(channels)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(pcm.tobytes())
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp_path, "-c:a", "libvorbis",
                        "-q:a", str(quality), "-map_metadata", "-1", path], check=True)
    finally:
        os.remove(tmp_path)
