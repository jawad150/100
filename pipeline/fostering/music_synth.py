"""music_synth.py: procedural music instruments, arrangement helpers, mix effects and the music delivery chain
(background-music beds under the VO versions of the Organic Fostering reels). numpy/scipy only, 48 kHz float64,
deterministic (seeded). Importing has no side effects.

Builds on audio.py (import audio as A) and does not duplicate it: A.SR, A.lp/hp/bp/eq, A.reverb (presets room,
studio, dark, plate, hall, air, outdoor), A.sidechain, A.loudness / loudness_curve / true_peak, A.limiter_gain,
A._write_wav / read_wav, A.undb, A._st.

CONVENTIONS
    note   MIDI number (60 = C4 = 261.63 Hz; floats allowed) or a name 'C4', 'F#3', 'Bb2' (octave 4 if omitted).
    dur    held (gate) length in seconds. Returned arrays also contain the release / natural tail.
    vel    0..1: level AND brightness. Every instrument normalises one event so its sample peak is
           PEAK * vel**1.5 (PEAK = 0.5, i.e. -6 dBFS at vel 1, -7.5 dBFS at vel 0.8). Balance with Track.add(gain_db).
    shape  mono (N,) float64 unless stated "stereo" (N, 2). Every event starts and ends at exactly 0 (no clicks),
           no DC. Place events with Track.add(x, t, gain_db, pan) (equal-power pan, centre = unity).
    times  seconds. Grid(bpm) gives exact beat / bar / 16th times (beat n = n * 60 / bpm, bar = 4 beats).

PITCH / TIME / HARMONY
    midi(note) -> MIDI number; hz(note) -> Hz; hz_to_midi(f); note_name(m, flats=False) -> 'A3'
    beat_time(n, bpm), bar_time(n, bpm, beats_per_bar=4)
    Grid(bpm, beats_per_bar=4, offset=0, swing=0): .beat_s .bar_s .step_s; .beat(n) .bar(n, beat=0)
        .step(n16, swing=None) (odd 16ths delayed by swing * step_s) .t(bar, beat, step) .n_bars(dur) .beats(t)
    Track(dur): stereo bus. .add(x, t, gain_db=0, pan=0, gain=1) mono or stereo event at t (s); .mix(x, gain_db);
        .buf (N, 2) array; np.asarray(track) works. Events starting before 0 / running past the end are cut.
    chord('Am7') / chord('A', 'm7', octave=3) / chord(57, 'm7') / chord('C/E') -> [MIDI...]; qualities: '' maj m
        dim aug sus2 sus4 7 maj7 m7 m7b5 dim7 mmaj7 6 m6 add9 madd9 9 maj9 m9 7sus4 add11 5
    invert(notes, k); voice_lead(prev_notes, 'Fmaj7', lo=None, hi=None) -> the inversion/octave of the target
        closest to prev (least total semitone movement); progression(['Am7', 'Fmaj7', 'C', 'G'], octave=4) ->
        voice-led list of note lists; bass_note('C/E', octave=2) -> 40
    SCALES: major minor lydian dorian mixolydian harmonic_minor pent_major pent_minor (+ ionian aeolian)
    scale('A', 'minor', octave=3, n=8); degree('C', 'lydian', 4, octave=4) -> 66 (F#4); triad(root, mode, d,
        octave, seventh=False, ninth=False); snap(note, root, mode) -> nearest scale note

INSTRUMENTS (one note/event -> array; all accept seed=)
    karplus_strong(note, dur=1.5, vel=0.8, kind='nylon'|'steel'|'uke', pluck=None, damping=None, t60=None,
        body=True, release=0.12)                      plucked string, fractional-delay KS + body resonances, mono
    strum(notes, dur=2.0, vel=0.8, direction='down'|'up', spread=0.012, kind='nylon', width=0.5) -> stereo;
        strings spread `spread` s apart (8-25 ms), low->high on down, high->low (lighter, faster) on up
    fm_epiano(note, dur=1.0, vel=0.8, release=0.3, bright=1.0, tine=1.0, detune=0.6) 2-op FM Rhodes, mono
    felt_piano(note, dur=1.0, vel=0.7, pedal=False, release=0.25, felt=1.0, tail=6.0) additive piano, mono
    marimba(note, vel=0.8, hardness=0.5, decay=1.0); glockenspiel(note, vel=0.7, hardness=0.6, decay=1.0);
    bell(note, vel=0.7, kind='hand'|'church', decay=1.0)  modal synthesis, mono
    pad(notes, dur=4.0, vel=0.7, wave='saw'|'warm'|'tri'|'square', voices=5, detune=14 (cents), attack=0.6,
        release=1.5, cutoff=1600, q=0.7, sweep=0.0 (octaves of LFO), sweep_rate=0.08 Hz, open_to=None (Hz at
        dur), chorus_mix=0.35, width=0.8, drift=2.0)  -> stereo
    pluck_synth(note, dur=0.2, vel=0.8, cutoff=700, env_oct=3.0, decay=0.12, amp_decay=0.35, q=1.2, wave='saw',
        detune=7.0, release=0.08)                     filtered saw with a fast filter envelope (arps), mono
    sub_bass(note, dur=0.5, vel=0.8, glide_from=None, glide=0.06, drive=1.6, harm=0.12, attack=0.006,
        release=0.06)                                 sine + gentle tanh saturation, optional glide, mono
    bass_pluck(note, dur=0.3, vel=0.8, cutoff=320, env_oct=2.5, decay=0.09, sub=0.6, release=0.06) mono
    DRUMS: soft_kick(vel=0.9, punch=0.5, tone=50, decay=0.30, click=0.25, drive=1.4) mono;
        clap(vel=0.8, tone=1300, bursts=4, spread=0.0105, decay=0.09, room='room', wet_db=-7) stereo;
        shaker(vel=0.7, length=0.07, tone=7500, attack=0.012) mono;
        shaker_pattern(bars, bpm, swing=0.12, accents=(1, .45, .75, .5), vel=0.7, ...) -> stereo (bars * bar);
        hat(vel=0.7, open=False, decay=None, tone=1.0) mono; brush(vel=0.6, length=0.22) mono;
        snare_soft(vel=0.7, tone=185, snappy=0.5, decay=0.14) mono;
        reverse_swell(dur=1.0, vel=0.8, notes=None, bright=1.0) stereo, ENDS (peaks) at dur;
        riser(dur=2.0, vel=0.8, f_start=250, f_end=7000, note=None) stereo, ENDS at dur;
        impact_low(vel=0.9, dur=2.5, tone=40, room='hall', wet_db=-10) stereo soft boom

OSCILLATORS / FILTERS
    osc(freq, n, shape='saw'|'warm'|'square'|'tri'|'sine', phase=0) band-limited wavetable oscillator (freq Hz,
        scalar or per-sample array for glides); tv_lowpass(x, fc, q=0.707) 2-pole LP, fc scalar or per-sample.

EFFECTS / MIX / QA
    chorus(x, rate=0.7, depth_ms=2.2, delay_ms=13, mix=0.4, voices=2) stereo; haas(x, ms=12, side='right');
    widen(x, w) (A.width); autopan(x, rate=0.25, depth=0.4);
    bus_comp(x, thresh_db=-18, ratio=2, knee_db=6, attack=0.01, release=0.15, makeup_db=0);
    tilt_eq(x, gain_db=1.5, pivot=900) (+ = brighter); duck(x, key, depth_db=6, attack=0.005, release=0.16)
        (wraps A.sidechain; key = kick track or any array); pump(x, times, depth_db=6, attack=0.004,
        release=0.18) synthetic kick-pump envelope; reverb_send(x, preset='plate', wet_db=-12, hp_hz=180)
        wet-only stereo (same length); fade_in(x, sec), fade_out(x, sec, end=None), gain_ramp(x, [(t, db), ...]);
    normalise_peak(x, peak_db=-1.0, true_peak=True); normalise_lufs(x, target=-16, tp_ceiling=-1.0) -> (y, info);
    click_report(x, ratio=6, isolation=2.5) -> {clean, count, worst_ratio, events}; dc_report(x) -> {dc,
        sub20_db, sub40_db, ok}; qa(x) -> all of it + peak / true peak / LUFS
    fit(x, n) pad/trim (stereo); load_reel_stems('reel1') -> dict(vo, sfx, mix, dur) from <AUD>/<name>_vo_*.wav

DELIVERY (used by every composer)
    bed, m = render_bed(clean, vo_stem, sfx_stem, mix_ref, gap_lu=7.0, min_vo_lu=10.0)
        ducks the music 9 dB under the VO (A.sidechain, attack 0.04, release 0.4) and 3 dB under the SFX (0.01 /
        0.25), then sets its level so the median short-term (3 s) loudness of the music in VO gaps is gap_lu below
        the reference mix's integrated loudness, unless the median voice-minus-music under speech would drop
        below min_vo_lu (then the music goes lower). m: gain_db, gap_st_lufs, gap_target_lufs, ref_lufs,
        vo_minus_music_lu, limited_by, speech_pct, ...
    mix, rep = master_withmusic(vo_stem, sfx_stem, bed, target=-14.0, tol=0.2, ceiling=-2.3, tp_max=-2.0)
        sum, re-gain + A.limiter_gain(-2.3) until -14.0 +- 0.2 LUFS and <= -2.0 dBTP; rep: lufs, true_peak,
        limiter_max_gr_db, music_lufs, stems (vo/sfx/music after the master gain), ok
    speech_mask(vo) -> per-sample bool (speech in a VO stem; used by render_bed)
    demo_arrangement(bpm=120, bars=16) -> (mix, info): a complete arrangement; read its source as a template
    write_mp3(wav_or_array, path, title, artist=None) -> ffmpeg libmp3lame 320k CBR 48 kHz + ID3 title
    make_preview(video_in, audio_wav_or_array, out_mp4) -> ffmpeg -c:v copy, AAC 192k, -shortest, +faststart
    beat_grid_check(x_or_wav, bpm) -> {tempo, phase (s, + = late; bias-corrected), tempo_coarse, phase_beatgrid
        (the raw reels-studio beatgrid.py number, which reads on-grid onsets ~15-19 ms early), strength, ok}

CLI
    python3 music_synth.py selftest [out_dir]   -> every instrument (2 bars), a 16-bar demo, delivery chain, asserts
    python3 music_synth.py demo out.wav [bpm] [bars]
    python3 music_synth.py beatgrid file.wav bpm

EXAMPLE
    import audio as A, music_synth as M
    BPM, DUR = 120, 49.5
    g, prog = M.Grid(BPM), M.progression(['Am7', 'Fmaj7', 'C', 'G'], octave=4)
    keys, bass, drums = M.Track(DUR), M.Track(DUR), M.Track(DUR)
    for b in range(M.Grid(BPM).n_bars(DUR)):
        ch = prog[b % 4]
        keys.add(M.felt_piano(ch[0], dur=g.bar_s, vel=0.6, pedal=True), g.bar(b), gain_db=-4, pan=-0.2)
        bass.add(M.sub_bass(M.bass_note(['Am7', 'Fmaj7', 'C', 'G'][b % 4], 2), dur=g.beat_s * 3), g.bar(b))
        for q in range(4):
            drums.add(M.soft_kick(vel=0.85), g.bar(b, q))
    music = M.duck(keys.buf + bass.buf, drums.buf, depth_db=5) + drums.buf
    music += M.reverb_send(keys.buf, 'hall', wet_db=-14)
    st = M.load_reel_stems('reel1')
    bed, m = M.render_bed(music, st['vo'], st['sfx'], st['mix'])
    mix, rep = M.master_withmusic(st['vo'], st['sfx'], bed)
    A._write_wav(A.AUDIO + '/reel1_vo_withmusic.wav', mix); M.write_mp3(bed, 'reel1_music.mp3', 'Reel 1 music')
"""
import functools
import math
import os
import shutil
import subprocess
import sys
import tempfile
import time

import numpy as np
from scipy import signal
from scipy.ndimage import uniform_filter1d

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import audio as A  # noqa: E402

SR = A.SR
TWO_PI = 2.0 * np.pi
PEAK = 0.5                 # sample peak of one event at vel = 1 (see _norm)
SELFTEST_DIR = os.environ.get(
    'MUSIC_SYNTH_SELFTEST',
    '/tmp/claude-0/-home-user-100/bb73d22e-ad11-5aa0-a0b2-8033920f7c07/scratchpad/music_synth_selftest')


# ============================================================================================ pitch
_PC = dict(C=0, D=2, E=4, F=5, G=7, A=9, B=11)
NOTE_NAMES = ('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B')
FLAT_NAMES = ('C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B')


def _pc_parse(s):
    """'F#m7' -> (6, 'm7'): pitch class of the leading note name (# / b accidentals) and the rest."""
    s = s.strip()
    if not s or s[0].upper() not in _PC:
        raise ValueError('not a note name: %r' % s)
    pc, i = _PC[s[0].upper()], 1
    while i < len(s) and s[i] in '#b♯♭':
        pc += 1 if s[i] in '#♯' else -1
        i += 1
    return pc, s[i:]


def midi(note):
    """MIDI number of a note: 69 -> 69, 'A4' -> 69, 'C#3' -> 49, 'Bb' -> 70 (octave 4 when omitted)."""
    if isinstance(note, str):
        pc, rest = _pc_parse(note)
        octave = int(rest) if rest.strip() else 4
        return 12 * (octave + 1) + pc
    return note


def hz(note):
    """Frequency (Hz) of a MIDI number or note name (A4 = 440 Hz, equal temperament)."""
    return 440.0 * 2.0 ** ((float(midi(note)) - 69.0) / 12.0)


midi_to_hz = hz


def hz_to_midi(f):
    """Fractional MIDI number of a frequency (Hz)."""
    return 69.0 + 12.0 * math.log2(float(f) / 440.0)


def note_name(note, flats=False):
    """60 -> 'C4', 70 -> 'A#4' (or 'Bb4' with flats=True)."""
    m = int(round(float(midi(note))))
    return '%s%d' % ((FLAT_NAMES if flats else NOTE_NAMES)[m % 12], m // 12 - 1)


# ============================================================================================ time
def beat_time(n, bpm, offset=0.0):
    """Time (s) of beat n (0-based) at bpm: offset + n * 60 / bpm."""
    return offset + n * 60.0 / bpm


def bar_time(n, bpm, beats_per_bar=4, offset=0.0):
    """Time (s) of the start of bar n (0-based)."""
    return offset + n * beats_per_bar * 60.0 / bpm


class Grid:
    """Beat grid at a BPM. beat_s / bar_s / step_s (16th) in seconds; all methods return seconds.
    g = Grid(120); g.bar(2) -> 4.0; g.bar(2, 1.5) -> 4.75; g.step(3) -> 0.375 (+ swing on odd 16ths)."""

    def __init__(self, bpm, beats_per_bar=4, offset=0.0, swing=0.0):
        self.bpm, self.bpb, self.offset, self.swing = float(bpm), int(beats_per_bar), float(offset), float(swing)
        self.beat_s = 60.0 / self.bpm
        self.bar_s = self.beat_s * self.bpb
        self.step_s = self.beat_s / 4.0

    def beat(self, n):
        """Time of beat n (float allowed: 2.5 = the 'and' of beat 2)."""
        return self.offset + n * self.beat_s

    def bar(self, n, beat=0.0):
        """Time of bar n plus `beat` beats."""
        return self.offset + n * self.bar_s + beat * self.beat_s

    def step(self, n, swing=None):
        """Time of 16th-note step n; odd steps are delayed by swing * step_s (0.33 ~ triplet shuffle)."""
        sw = self.swing if swing is None else swing
        return self.offset + n * self.step_s + (sw * self.step_s if int(n) % 2 == 1 else 0.0)

    def t(self, bar=0, beat=0.0, step=0, swing=None):
        """Time of (bar, beat, 16th step) with swing applied to odd steps."""
        return self.bar(bar, beat) + self.step(step, swing) - self.offset

    def n_bars(self, dur):
        """Whole bars that fit in dur seconds."""
        return int((dur - self.offset) // self.bar_s + 1e-9)

    def beats(self, t):
        """Seconds -> beats (float)."""
        return (t - self.offset) / self.beat_s

    def __repr__(self):
        return 'Grid(%.2f BPM, beat %.4f s, bar %.4f s)' % (self.bpm, self.beat_s, self.bar_s)


class Track:
    """A stereo bus of fixed length: place mono or stereo events at times with gain and equal-power pan.
    t = Track(30.0); t.add(M.soft_kick(), 0.5, gain_db=-3, pan=0); y = t.buf  (N, 2) float64."""

    def __init__(self, dur, name=''):
        self.dur = float(dur)
        self.N = int(round(self.dur * SR))
        self._b = np.zeros((2, self.N))         # channel-major storage: contiguous adds
        self.name = name

    @property
    def buf(self):
        """The mix as an (N, 2) float64 array (a view: edits write through)."""
        return self._b.T

    @buf.setter
    def buf(self, v):
        v = fit(v, self.N)
        self._b = np.ascontiguousarray(v.T)

    def add(self, x, t, gain_db=0.0, pan=0.0, gain=1.0):
        """Add event x (mono (n,) or stereo (n, 2)) starting at t seconds. pan -1..1: equal-power for mono
        (centre unity, -3 dB law), balance for stereo. Parts before 0 / after the end are cut (with a 2 ms
        fade at the cut so it cannot click)."""
        x = np.asarray(x, dtype=np.float64)
        g = float(gain) * 10.0 ** (gain_db / 20.0)
        i0 = int(round(t * SR))
        s0 = 0
        if i0 < 0:
            s0, i0 = -i0, 0
        m = min(len(x) - s0, self.N - i0)
        if m <= 0:
            return self
        th = (min(max(float(pan), -1.0), 1.0) + 1.0) * (np.pi / 4)
        gl, gr = g * math.sqrt(2) * math.cos(th), g * math.sqrt(2) * math.sin(th)
        seg = x[s0:s0 + m]
        if s0 > 0 or m < len(x) - s0:             # an edge was cut: 2 ms fade there (no click)
            seg = seg.copy()
            nf = min(m // 2, _n(0.002))
            if nf > 1:
                w = _rc_up(nf)
                w2 = w[:, None] if seg.ndim == 2 else w
                if s0 > 0:
                    seg[:nf] *= w2
                if m < len(x) - s0:
                    seg[-nf:] *= w2[::-1]
        if seg.ndim == 1:
            self._b[0, i0:i0 + m] += gl * seg
            self._b[1, i0:i0 + m] += gr * seg
        else:
            self._b[0, i0:i0 + m] += gl * seg[:, 0]
            self._b[1, i0:i0 + m] += gr * seg[:, 1]
        return self

    def mix(self, x, gain_db=0.0, t=0.0):
        """Add a whole array (or another Track) at t (default 0)."""
        return self.add(x.buf if isinstance(x, Track) else x, t, gain_db)

    def __array__(self, dtype=None, copy=None):
        return self._b.T if dtype is None else self._b.T.astype(dtype)

    def peak_db(self):
        return float(A.db(np.max(np.abs(self._b)) + 1e-12))


def fit(x, n):
    """Stereo copy of x padded with zeros / trimmed to n samples (a trimmed end gets a 10 ms fade)."""
    x = A._st(np.asarray(x.buf if isinstance(x, Track) else x, dtype=np.float64))
    if len(x) >= n:
        y = x[:n].copy()
        if len(x) > n:
            y = fade_out(y, 0.01)
        return y
    return np.pad(x, ((0, n - len(x)), (0, 0)))


# ============================================================================================ harmony
CHORD_QUALITIES = {
    '': (0, 4, 7), 'm': (0, 3, 7), 'dim': (0, 3, 6), 'aug': (0, 4, 8), 'sus2': (0, 2, 7), 'sus4': (0, 5, 7),
    '7': (0, 4, 7, 10), 'maj7': (0, 4, 7, 11), 'm7': (0, 3, 7, 10), 'm7b5': (0, 3, 6, 10), 'dim7': (0, 3, 6, 9),
    'mmaj7': (0, 3, 7, 11), '6': (0, 4, 7, 9), 'm6': (0, 3, 7, 9), 'add9': (0, 4, 7, 14), 'madd9': (0, 3, 7, 14),
    '9': (0, 4, 7, 10, 14), 'maj9': (0, 4, 7, 11, 14), 'm9': (0, 3, 7, 10, 14), '7sus4': (0, 5, 7, 10),
    'add11': (0, 4, 7, 17), '5': (0, 7),
}
_QALIAS = {'maj': '', 'M': '', 'major': '', 'min': 'm', '-': 'm', 'minor': 'm', 'M7': 'maj7', 'ma7': 'maj7',
           'Δ': 'maj7', 'Δ7': 'maj7', 'min7': 'm7', '-7': 'm7', 'ø': 'm7b5', 'ø7': 'm7b5',
           '°': 'dim', 'o': 'dim', '°7': 'dim7', 'o7': 'dim7', '+': 'aug', 'sus': 'sus4', 'mM7': 'mmaj7',
           'M9': 'maj9', 'min9': 'm9', '2': 'add9', 'add2': 'add9', 'madd2': 'madd9', 'dom7': '7'}


def _quality(q):
    q = q.strip()
    q = _QALIAS.get(q, q)
    if q not in CHORD_QUALITIES:
        raise ValueError('unknown chord quality %r (known: %s)' % (q, ', '.join(sorted(CHORD_QUALITIES))))
    return CHORD_QUALITIES[q]


def invert(notes, k=1):
    """k-th inversion: move the lowest note up an octave k times (k < 0: highest note down)."""
    v = sorted(int(n) for n in notes)
    for _ in range(abs(int(k))):
        if k > 0:
            v = sorted(v[1:] + [v[0] + 12])
        else:
            v = sorted([v[-1] - 12] + v[:-1])
    return v


def chord(root, quality=None, octave=4, inversion=0):
    """Chord as a sorted list of MIDI notes.
    chord('Am7') -> [69, 72, 76, 79] (root at `octave`, A4 = 69); chord('A', 'm7', octave=3) -> [57, 60, 64, 67];
    chord(57, 'm7'); chord('C/E') (slash: E lowest; a non-chord bass is added below); inversion k rotates."""
    bass_pc = None
    if quality is None and isinstance(root, str):
        pc, rest = _pc_parse(root)
        if '/' in rest:
            rest, b = rest.split('/', 1)
            bass_pc = _pc_parse(b)[0] % 12
        r = 12 * (octave + 1) + pc
        iv = _quality(rest)
    else:
        if isinstance(root, str):
            pc, rest = _pc_parse(root)
            r = 12 * (int(rest) + 1 if rest.strip() else octave + 1) + pc
        else:
            r = int(round(float(root)))
        iv = _quality(quality or '')
    notes = [r + i for i in iv]
    if inversion:
        notes = invert(notes, inversion)
    if bass_pc is not None:
        if bass_pc in [n % 12 for n in notes]:
            while notes[0] % 12 != bass_pc:
                notes = invert(notes, 1)
        else:
            b = notes[0] - ((notes[0] - bass_pc) % 12 or 12)
            notes = [b] + notes
    return sorted(notes)


def _movement(prev, cand):
    p, c = sorted(prev), sorted(cand)
    if len(p) == len(c):
        return float(sum(abs(a - b) for a, b in zip(p, c)))
    return float(sum(min(abs(a - b) for b in p) for a in c) + sum(min(abs(a - b) for b in c) for a in p))


def voice_lead(prev, target, lo=None, hi=None):
    """Voicing of `target` (symbol or note list) that moves least from `prev` (sum of semitone moves between
    sorted voices; ties -> smaller centre shift). Tries every inversion in octaves -2..+2; lo/hi (MIDI) bound
    the result. voice_lead([57, 60, 64, 67], 'Fmaj7') -> [57, 60, 64, 65]."""
    tgt = chord(target) if isinstance(target, str) else sorted(int(n) for n in target)
    best, best_cost = None, None
    mean_p = float(np.mean(prev))
    for inv in range(len(tgt)):
        v = invert(tgt, inv)
        for o in range(-36, 37, 12):
            c = [n + o for n in v]
            if (lo is not None and c[0] < lo) or (hi is not None and c[-1] > hi):
                continue
            cost = _movement(prev, c) + 0.01 * abs(float(np.mean(c)) - mean_p)
            if best_cost is None or cost < best_cost:
                best, best_cost = c, cost
    if best is None:
        raise ValueError('no voicing of %r inside lo=%s hi=%s' % (target, lo, hi))
    return best


def progression(symbols, octave=4, lead=True, lo=None, hi=None):
    """List of chord symbols -> list of note lists. The first chord is in root position at `octave`; the
    others are voice-led from the previous one (lead=False: all root position)."""
    out = []
    for i, s in enumerate(symbols):
        c = chord(s, octave=octave) if isinstance(s, str) else sorted(s)
        if lead and i > 0:
            c = voice_lead(out[-1], c, lo, hi)
        out.append(c)
    return out


def bass_note(symbol, octave=2):
    """Root (or slash bass) of a chord symbol at `octave`: bass_note('Am7', 2) -> 45, bass_note('C/E') -> 40."""
    pc, rest = _pc_parse(symbol)
    if '/' in rest:
        pc = _pc_parse(rest.split('/', 1)[1])[0]
    return 12 * (octave + 1) + pc % 12


SCALES = dict(major=(0, 2, 4, 5, 7, 9, 11), ionian=(0, 2, 4, 5, 7, 9, 11), minor=(0, 2, 3, 5, 7, 8, 10),
              aeolian=(0, 2, 3, 5, 7, 8, 10), dorian=(0, 2, 3, 5, 7, 9, 10), lydian=(0, 2, 4, 6, 7, 9, 11),
              mixolydian=(0, 2, 4, 5, 7, 9, 10), harmonic_minor=(0, 2, 3, 5, 7, 8, 11),
              pent_major=(0, 2, 4, 7, 9), pent_minor=(0, 3, 5, 7, 10))


def _root_midi(root, octave):
    if isinstance(root, str):
        pc, rest = _pc_parse(root)
        return 12 * ((int(rest) if rest.strip() else octave) + 1) + pc
    return int(round(float(root)))


def degree(root, mode, d, octave=4):
    """MIDI note of scale degree d (1-based; 8 = octave up, 0 = degree 7 below) of root/mode.
    degree('C', 'lydian', 4) -> 66 (F#4)."""
    steps = SCALES[mode]
    i = int(d) - 1
    return _root_midi(root, octave) + 12 * (i // len(steps)) + steps[i % len(steps)]


def scale(root, mode='major', octave=4, n=None):
    """Ascending scale notes from root: scale('A', 'minor', 3) -> [57, 59, 60, 62, 64, 65, 67, 69]."""
    n = len(SCALES[mode]) + 1 if n is None else n
    return [degree(root, mode, d + 1, octave) for d in range(n)]


def triad(root, mode, d, octave=4, seventh=False, ninth=False):
    """Diatonic chord on degree d (stacked scale thirds): triad('A', 'minor', 6, octave=3) -> [65, 69, 72]
    (F major); seventh / ninth add the 7th / 9th."""
    ks = [0, 2, 4] + ([6] if seventh or ninth else []) + ([8] if ninth else [])
    return [degree(root, mode, d + k, octave) for k in ks]


def snap(note, root, mode='major'):
    """Nearest note of the scale (ties go down)."""
    m = int(round(float(midi(note))))
    pcs = {(_root_midi(root, 4) + s) % 12 for s in SCALES[mode]}
    for k in range(7):
        for c in (m - k, m + k):
            if c % 12 in pcs:
                return c
    return m


# ============================================================================================ synthesis helpers
def _n(sec):
    return max(1, int(round(sec * SR)))


def _vamp(vel):
    return float(np.clip(vel, 0.0, 1.0)) ** 1.5


def _norm(x, vel, peak=None):
    """Scale an event so its sample peak is PEAK * vel**1.5 (the library's level convention)."""
    pk = np.max(np.abs(x))
    return x * ((PEAK if peak is None else peak) * _vamp(vel) / pk) if pk > 0 else x


def _rc_up(n):
    """Raised-cosine ramp 0 -> 1 over n samples (first sample exactly 0)."""
    return 0.5 - 0.5 * np.cos(np.pi * np.arange(n) / max(n, 1))


def _gate(N, dur, attack, release, curve='cos'):
    """Gate envelope: raised-cosine attack, sustain 1, raised-cosine release from dur, 0 after."""
    e = np.ones(N)
    na = min(N, _n(attack)) if attack > 0 else 0
    if na > 1:
        e[:na] = _rc_up(na)
    i1 = min(N, int(round(dur * SR)))
    nr = _n(release)
    seg = e[i1:i1 + nr]
    if len(seg):
        seg *= 0.5 + 0.5 * np.cos(np.pi * np.arange(1, len(seg) + 1) / nr)
    e[i1 + nr:] = 0.0
    return e


def _finish(x, tail=0.004, hp_hz=None, head=0.0005):
    """Event clean-up: optional DC/subsonic high-pass, raised-cosine head and tail (exact zeros at both ends)."""
    x = np.array(x, dtype=np.float64)
    if hp_hz:
        x = A.hp(x, hp_hz, 2)
    nh = _n(head)
    if nh > 1 and len(x) > 2 * nh:
        w = _rc_up(nh)
        x[:nh] *= w[:, None] if x.ndim == 2 else w
    x = A._taper(x, 1.0, sec=tail)
    if x.ndim == 2:
        x[-1] = 0.0
    else:
        x[-1] = 0.0
    return x


def _trim_silence(x, rel_db=-90.0, min_len=0.05):
    """Drop the trailing part quieter than rel_db re the peak (keeps 20 ms extra)."""
    a = np.abs(x) if x.ndim == 1 else np.abs(x).max(1)
    pk = a.max()
    if pk <= 0:
        return x[:_n(min_len)]
    nz = np.flatnonzero(a > pk * 10 ** (rel_db / 20.0))
    end = min(len(x), max(_n(min_len), (nz[-1] if len(nz) else 0) + _n(0.02)))
    return x[:end]


_TS = 4096                 # wavetable size


@functools.lru_cache(maxsize=512)
def _wavetable(shape, nh):
    """Single-cycle band-limited table with nh harmonics: saw | warm (1/k^1.4) | square | tri | sine."""
    k = np.arange(1, nh + 1, dtype=np.float64)
    if shape == 'saw':
        a = 1.0 / k
    elif shape == 'warm':
        a = 1.0 / k ** 1.4
    elif shape == 'square':
        a = np.where(k % 2 == 1, 1.0 / k, 0.0)
    elif shape == 'tri':
        a = np.where(k % 2 == 1, (-1.0) ** ((k - 1) // 2) / k ** 2, 0.0)
    elif shape == 'sine':
        a = (k == 1).astype(np.float64)
    else:
        raise ValueError('wave shape %r' % shape)
    X = np.zeros(_TS // 2 + 1, dtype=complex)
    X[1:nh + 1] = -1j * a * (_TS / 2)
    tb = np.fft.irfft(X, _TS)
    tb /= np.max(np.abs(tb))
    tb = np.append(tb, tb[0])
    tb.setflags(write=False)
    return tb


def _table_read(ph, fmax, shape):
    """Read the band-limited table for a top frequency fmax at phases ph (cycles, any range)."""
    nh = int(max(1, min(_TS // 2 - 1, 0.45 * SR / max(fmax, 1.0))))
    if nh > 24:                                       # fewer distinct tables (quarter-octave steps)
        nh = int(2 ** (math.floor(math.log2(nh) * 4) / 4))
    tb = _wavetable(shape, nh)
    ph = ph - np.floor(ph)
    idx = ph * _TS
    i = idx.astype(np.int64)
    fr = idx - i
    return tb[i] + fr * (tb[i + 1] - tb[i])


def osc(freq, n, shape='saw', phase=0.0):
    """Band-limited wavetable oscillator (no aliasing). freq: Hz scalar or (n,) array (glides / vibrato),
    phase in cycles (0..1). Returns (n,) in -1..1."""
    fmax = float(np.max(freq)) if np.ndim(freq) else float(freq)
    if np.ndim(freq) == 0:
        ph = phase + (float(freq) / SR) * np.arange(n)
    else:
        ph = phase + np.cumsum(np.asarray(freq, dtype=np.float64)[:n]) / SR - float(np.asarray(freq).flat[0]) / SR
    return _table_read(ph, fmax, shape)


def _modes(freqs, taus, amps, N, floor=1e-5):
    """Sum of exponentially decaying sines (modal resonator bank via 2-pole lfilter impulse responses, sine
    phase so each mode starts at exactly 0). Each mode is only computed until it decays below `floor`."""
    out = np.zeros(N)
    for f, tau, a in zip(freqs, taus, amps):
        if a == 0 or f <= 0 or f >= 0.45 * SR or tau <= 0:
            continue
        w = TWO_PI * f / SR
        r = math.exp(-1.0 / (tau * SR))
        nk = min(N, int(tau * SR * math.log(max(abs(a) / floor, 1.0001))) + 2)
        imp = np.zeros(nk)
        imp[0] = 1.0
        out[:nk] += signal.lfilter([0.0, a * math.sin(w)], [1.0, -2.0 * r * math.cos(w), r * r], imp)
    return out


def _harm_bank(f0, N, amp_fn, shape='saw', kmax=None):
    """Additive harmonic oscillator with per-harmonic, time-varying amplitudes amp_fn(fk) -> (N,) or scalar.
    Harmonics up to 0.45 SR (no aliasing). sin(k phi) via the Chebyshev recursion (one cos per call).
    Used for filter-enveloped plucks: amp_fn = waveform weight * filter magnitude at fk over time."""
    phi = TWO_PI * f0 * np.arange(N) / SR
    s1, s0 = np.sin(phi), np.zeros(N)
    c2 = 2.0 * np.cos(phi)
    K = int(min(kmax or 400, 0.45 * SR / f0))
    out = np.zeros(N)
    sk, skm1 = s1, s0
    for k in range(1, K + 1):                 # saw / warm start mid-ramp (value 0, no edge at the onset)
        sg = 1.0 if k % 2 else -1.0
        if shape == 'saw':
            w = sg / k
        elif shape == 'square':
            w = 1.0 / k if k % 2 else 0.0
        else:                                   # 'warm'
            w = sg / k ** 1.4
        if w:
            out += (w * amp_fn(k * f0)) * sk
        sk, skm1 = c2 * sk - skm1, sk
    return out


def _lp_mag(f, fc, q):
    """|H| of a 2-pole low-pass (resonance q) at frequency f for cutoff fc (arrays broadcast)."""
    r = f / fc
    return 1.0 / np.sqrt((1.0 - r * r) ** 2 + (r / q) ** 2)


# ============================================================================================ plucked strings
_KS = {
    # t60 (s at 196 Hz), loop low-pass s (0..0.5, higher = darker), excitation low-pass (Hz at vel 1),
    # pluck position (fraction of the string), body peaks (Hz, Q, dB)
    'nylon': dict(t60=3.0, s=0.40, exc=2800.0, pluck=0.17, body=((98, 1.4, 5.0), (204, 2.0, 3.5), (410, 2.5, 2.0),
                                                                  (2400, 0.9, -3.0))),
    'steel': dict(t60=4.6, s=0.22, exc=6500.0, pluck=0.12, body=((108, 1.6, 4.0), (220, 2.0, 2.5), (3200, 0.9, 2.5))),
    'uke': dict(t60=1.7, s=0.33, exc=3800.0, pluck=0.20, body=((250, 1.8, 4.5), (520, 2.4, 3.0), (1150, 2.0, 1.5))),
}


def _ks_taps(P, s, f0):
    """Integer delay L and 3-tap loop FIR (one-zero damping * linear fractional delay) tuned so the total
    phase delay at f0 equals P samples. Returns L, taps, |H(f0)|."""
    w = TWO_PI * f0 / SR
    L = int(math.floor(P - s))
    d = P - s - L
    e = np.exp(-1j * w * np.arange(3))
    for _ in range(6):
        h = np.convolve([1.0 - s, s], [1.0 - d, d])
        H = np.sum(h * e)
        d += P - (L - np.angle(H) / w)
        while d < 0:
            d += 1.0
            L -= 1
        while d >= 1:
            d -= 1.0
            L += 1
    h = np.convolve([1.0 - s, s], [1.0 - d, d])
    return L, h, float(abs(np.sum(h * e)))


@functools.lru_cache(maxsize=1024)
def _ks_cached(m, dur, vel, kind, pluck, damping, t60, body, release, seed):
    prm = _KS[kind]
    f0 = hz(m)
    P = SR / f0
    s = prm['s'] if damping is None else 0.04 + 0.46 * float(np.clip(damping, 0, 1))
    T60 = (prm['t60'] if t60 is None else t60) * (196.0 / f0) ** 0.35
    T60 = float(np.clip(T60, 0.4, 10.0))
    beta = prm['pluck'] if pluck is None else float(np.clip(pluck, 0.03, 0.5))
    N = _n(dur + release + 0.01)
    rng = np.random.default_rng([seed & 0xFFFFFFFF, int(m * 100) & 0xFFFF, 77])
    # excitation: one period of low-passed noise (brighter when harder), pluck-position comb, soft onset
    Pi = max(2, int(round(P)))
    exc = rng.standard_normal(Pi + 64)
    fc = prm['exc'] * (0.35 + 0.65 * vel)
    a1 = math.exp(-TWO_PI * fc / SR)
    exc = signal.lfilter([1 - a1], [1, -a1], exc)[64:]
    k = max(1, int(round(beta * P)))
    exc = exc - np.concatenate([np.zeros(k), exc[:-k]])
    exc -= exc.mean()
    on = min(Pi, _n(0.0006))
    exc[:on] *= _rc_up(on)
    exc /= np.sqrt(np.mean(exc ** 2)) + 1e-12
    L, h, Hm = _ks_taps(P, s, f0)
    g = min(0.99995, 10.0 ** (-3.0 / (T60 * f0)) / max(Hm, 1e-6))
    g0, g1, g2 = (g * h).tolist()
    off = L + 3
    y = np.zeros(off + N)
    e = np.zeros(off + N)
    e[off:off + min(len(exc), N)] = exc[:N]
    for s0 in range(off, off + N, L):           # block recursion: every tap reaches >= L samples back
        s1 = min(s0 + L, off + N)
        m_ = s1 - s0
        a = s0 - L
        y[s0:s1] = e[s0:s1] + g0 * y[a:a + m_] + g1 * y[a - 1:a - 1 + m_] + g2 * y[a - 2:a - 2 + m_]
    y = y[off:]
    if body:
        for fb, qb, gb in prm['body']:
            y = A.eq(y, 'peak', fb, qb, gb)
    y = A.hp(y, 45.0, 2)
    y *= _gate(N, dur, 0.0, release)
    y = _finish(y, tail=0.003)
    y = _norm(y, vel)
    y.setflags(write=False)
    return y


def karplus_strong(note, dur=1.5, vel=0.8, kind='nylon', pluck=None, damping=None, t60=None, body=True,
                   release=0.12, seed=0):
    """Plucked string (extended Karplus-Strong). kind: 'nylon' (warm classical guitar), 'steel' (bright
    acoustic), 'uke' (short, high). pluck: position 0.03..0.5 (0.12 bright near the bridge .. 0.3 round);
    damping 0..1 (loop low-pass: higher = darker, faster treble decay); t60: ring time (s) at G3, scaled by
    pitch; body: guitar-body resonance peaks; the string is damped over `release` s after dur.
    Typical: dur 0.3-4 s, vel 0.5-0.9. Returns mono, len = dur + release."""
    m = float(midi(note))
    return np.array(_ks_cached(round(m, 3), round(float(dur), 4), round(float(vel), 3), kind,
                               None if pluck is None else round(float(pluck), 3),
                               None if damping is None else round(float(damping), 3),
                               None if t60 is None else round(float(t60), 3), bool(body), round(float(release), 4),
                               int(seed)))


def strum(notes, dur=2.0, vel=0.8, direction='down', spread=0.012, kind='nylon', width=0.5, humanize=0.002,
          seed=0, **ks):
    """Strummed chord: notes (MIDI list, e.g. chord('Am', octave=3)) played spread s apart (0.008-0.025 s per
    string). direction 'down' = low -> high, accent on the first strings; 'up' = high -> low, 15 % faster and
    lighter. All strings are damped together at dur (from the first string). width: stereo spread of the strings
    (low left .. high right). **ks: karplus_strong options (pluck, damping, t60, body, release).
    Returns stereo; the first string starts at sample 0."""
    up = str(direction).lower().startswith('u')
    order = sorted(notes, reverse=up)
    rank = {n: i for i, n in enumerate(sorted(notes))}
    rng = np.random.default_rng([int(seed) & 0xFFFFFFFF, 31])
    step = spread * (0.85 if up else 1.0)
    n_str = len(order)
    parts = []
    for k, nt in enumerate(order):
        tk = k * step + (rng.uniform(-humanize, humanize) if k else 0.0)
        tk = max(tk, 0.0)
        vk = vel * (0.82 if up else 1.0) * (1.0 - 0.045 * k) * (1.0 + rng.uniform(-0.04, 0.04))
        x = karplus_strong(nt, max(0.05, dur - tk), float(np.clip(vk, 0.05, 1.0)), kind, seed=seed * 31 + k, **ks)
        p = width * (2.0 * rank[nt] / max(n_str - 1, 1) - 1.0)
        parts.append((tk, x, p))
    N = max(int(round(tk * SR)) + len(x) for tk, x, _ in parts)
    out = Track(N / SR)
    for tk, x, p in parts:
        out.add(x, tk, pan=p)
    return out.buf * (1.0 / math.sqrt(max(n_str, 1) / 2.0))


# ============================================================================================ keys
@functools.lru_cache(maxsize=1024)
def _epiano_cached(m, dur, vel, release, bright, tine, detune, seed):
    f = hz(m)
    N = _n(dur + release + 0.01)
    t = np.arange(N) / SR
    tau = float(np.clip(1.7 * (261.6 / f) ** 0.55, 0.35, 5.0))
    amp = 0.72 * np.exp(-t / tau) + 0.28 * np.exp(-t / (0.18 * tau))
    I = bright * ((0.35 + 2.0 * vel ** 2) * np.exp(-t / 0.42) + 0.22 * vel)
    ph = TWO_PI * f * t
    ph2 = TWO_PI * (f + detune) * t
    body = np.sin(ph + I * np.sin(ph)) + 0.55 * np.sin(ph2 + 0.6 * I * np.sin(ph2))
    tl = tine * 0.42 * vel ** 1.2 * float(np.clip((1300.0 - f) / 500.0, 0.0, 1.0))      # tine fades out up high
    if tl > 0:
        body += tl * np.exp(-t / 0.07) * np.sin(ph + (0.6 + 1.6 * vel) * np.exp(-t / 0.012) * np.sin(14.0 * ph))
    x = body * amp * _gate(N, dur, 0.0015, release)
    x = _finish(A.hp(x, 30.0, 2), tail=0.003)
    x = _norm(x, vel)
    x.setflags(write=False)
    return x


def fm_epiano(note, dur=1.0, vel=0.8, release=0.3, bright=1.0, tine=1.0, detune=0.6, seed=0):
    """FM electric piano (Rhodes-like): 1:1 carrier/modulator pair whose index falls after the strike
    (velocity -> brightness: soft = round, hard = barky), a 14:1 'tine' pair for the metallic attack, and a
    slightly detuned second pair (detune Hz) for movement. release: key-up fade (s). Typical vel 0.4-0.85,
    bright 0.6-1.4. Returns mono, len = dur + release."""
    return np.array(_epiano_cached(round(float(midi(note)), 3), round(float(dur), 4), round(float(vel), 3),
                                   round(float(release), 4), round(float(bright), 3), round(float(tine), 3),
                                   round(float(detune), 3), int(seed)))


@functools.lru_cache(maxsize=1024)
def _piano_cached(m, dur, vel, pedal, release, felt, tail, seed):
    f0 = hz(m)
    rng = np.random.default_rng([int(seed) & 0xFFFFFFFF, int(m * 100) & 0xFFFF, 5])
    B = 3e-4 * 2.0 ** ((m - 60) / 14.0)                         # inharmonicity coefficient
    fc = (650.0 + 2600.0 * vel ** 1.6) * (2.2 - 1.2 * float(np.clip(felt, 0, 1)))   # felt low-pass
    tau0 = float(np.clip(4.2 * (261.6 / f0) ** 0.65, 0.5, 14.0))
    hold = dur + (tail if pedal else 0.0)
    N = _n(hold + release + 0.01)
    freqs, taus, amps = [], [], []
    for n in range(1, 60):
        fn = n * f0 * math.sqrt(1.0 + B * n * n)
        if fn > min(0.42 * SR, 7.0 * fc + f0):
            break
        a = n ** -0.85 * (0.25 + abs(math.sin(math.pi * n * 0.118))) / (1.0 + (fn / fc) ** 4) ** 0.5
        if n == 1:
            a *= 1.15
        tp = tau0 * 0.32 / (1.0 + 0.10 * (n - 1) + (fn / 3500.0) ** 1.5)       # prompt sound
        ta = tau0 / (1.0 + 0.06 * (n - 1) + (fn / 5000.0) ** 1.5)               # aftersound
        dl = (0.25 + 0.75 * rng.random()) * 0.6 / 1200.0 * math.log(2)          # unison detune ~0.15-0.6 cent
        freqs += [fn * (1 + dl), fn * (1 - dl)]
        taus += [tp, ta]
        amps += [a * 0.68, a * 0.32]
    x = _modes(freqs, taus, amps, N)
    nh = _n(0.012)                                              # felt hammer: soft thump of low-passed noise
    hn = A.lp(rng.standard_normal(nh + 200), 900.0 + 1600.0 * vel, 2)[200:] * np.exp(-np.arange(nh) / (0.003 * SR))
    hn *= _rc_up(nh) ** 0.5
    x[:nh] += hn * (0.10 * vel) * np.max(np.abs(x[:_n(0.05)]) + 1e-9) / (np.max(np.abs(hn)) + 1e-9)
    on = _n(0.0025 - 0.0013 * vel)
    x[:on] *= _rc_up(on)
    if not pedal:                                               # dampers: fast smooth decay after key-up
        i1 = min(N, _n(dur))
        u = np.arange(N - i1) / SR
        x[i1:] *= np.exp(-u / max(release / 5.0, 0.01)) * (0.5 + 0.5 * np.cos(np.pi * np.clip(u / release, 0, 1)))
    x = _trim_silence(x, -80.0)
    x = _finish(A.hp(x, 25.0, 2), tail=min(0.03, release * 0.5))
    x = _norm(x, vel)
    x.setflags(write=False)
    return x


def felt_piano(note, dur=1.0, vel=0.7, pedal=False, release=0.25, felt=1.0, tail=6.0, seed=0):
    """Felt / soft upright piano (additive modal: slightly inharmonic partials f_n = n f0 sqrt(1 + B n^2),
    hammer-position comb, felt low-pass whose cutoff rises with vel, two-stage (prompt + aftersound) decay from
    detuned unison strings, soft hammer thump). pedal=False: dampers after dur (release s); pedal=True: the
    note rings up to dur + tail s (natural decay). felt 0 (bright) .. 1 (muffled). Typical vel 0.3-0.8.
    Returns mono (trailing silence trimmed)."""
    return np.array(_piano_cached(round(float(midi(note)), 3), round(float(dur), 4), round(float(vel), 3),
                                  bool(pedal), round(float(release), 4), round(float(felt), 3),
                                  round(float(tail), 3), int(seed)))


# ============================================================================================ mallets / bells
@functools.lru_cache(maxsize=1024)
def _mallet_cached(kind, m, vel, hardness, decay, sub, seed):
    f0 = hz(m)
    rng = np.random.default_rng([int(seed) & 0xFFFFFFFF, int(m * 100) & 0xFFFF, len(kind)])
    h = float(np.clip(hardness, 0.0, 1.0))
    if kind == 'marimba':
        ratios = [1.0, 3.98, 9.85]
        t1 = float(np.clip(0.6 * (262.0 / f0) ** 0.7, 0.12, 2.2)) * decay
        taus = [t1, t1 * 0.28, t1 * 0.12]
        amps = [1.0, 0.22 + 0.45 * h * vel, 0.06 + 0.35 * h * h * vel]
        contact = 0.0022 - 0.0016 * h
        split = 0.0
    elif kind == 'glockenspiel':
        ratios = [1.0, 2.756, 5.404, 8.933, 13.344]
        t1 = float(np.clip(2.6 * (1000.0 / f0) ** 0.3, 0.6, 5.0)) * decay
        taus = [t1, t1 * 0.45, t1 * 0.22, t1 * 0.12, t1 * 0.07]
        amps = [1.0, 0.12 + 0.4 * h, 0.05 + 0.25 * h, 0.03 + 0.12 * h, 0.06 * h]
        contact = 0.0006 - 0.0004 * h
        split = 0.0
    elif kind == 'church':       # strike note = prime; hum (0.5), tierce (minor third), quint, nominal (2.0), ...
        ratios = [0.5, 1.0, 1.183, 1.506, 2.0, 2.514, 2.662, 3.011, 4.166]
        s = float(np.clip((500.0 / f0) ** 0.3, 0.5, 2.0)) * decay
        taus = [9.0 * s, 6.0 * s, 4.0 * s, 3.0 * s, 3.2 * s, 1.6 * s, 1.3 * s, 1.1 * s, 0.8 * s]
        amps = [0.55, 0.8, 0.5, 0.3, 1.0, 0.35, 0.22, 0.2, 0.12 * (0.5 + h)]
        contact = 0.0012 - 0.0008 * h
        split = 1.2
    else:                        # 'hand': handbell, tuned fundamental + twelfth (consonant in any key)
        ratios = [1.0, 3.0, 4.16, 5.43, 6.8]
        s = float(np.clip((800.0 / f0) ** 0.35, 0.5, 2.5)) * decay
        taus = [3.4 * s, 2.0 * s, 1.1 * s, 0.75 * s, 0.5 * s]
        amps = [1.0, 0.5, 0.18 + 0.15 * h, 0.12 + 0.12 * h, 0.06 + 0.1 * h]
        contact = 0.001 - 0.0006 * h
        split = 0.9
    fr, tu, am = [], [], []
    for r, ta, a in zip(ratios, taus, amps):
        f = f0 * r
        if split:
            sp = split * (0.6 + 0.8 * rng.random()) * (f / f0) ** 0.5
            fr += [f, f + sp]
            tu += [ta, ta * 0.92]
            am += [a / 1.4, a * 0.4 / 1.4]
        else:
            fr.append(f * (1 + rng.uniform(-0.0004, 0.0004)))
            tu.append(ta)
            am.append(a)
    N = _n(min(max(tu) * 7.0, 14.0))
    x = _modes(fr, tu, am, N)
    if sub:
        nk = _n(0.006)                                          # mallet knock (wood / metal tick)
        kn = A.bp(rng.standard_normal(nk + 256), 1500.0 if kind == 'marimba' else 5000.0,
                  6000.0 if kind == 'marimba' else 14000.0, 2)[256:]
        kn *= np.exp(-np.arange(nk) / (0.0012 * SR))
        x[:nk] += kn * sub * h * np.max(np.abs(x)) / (np.max(np.abs(kn)) + 1e-9)
    on = _n(max(contact, 0.0002))
    x[:on] *= _rc_up(on)
    x = _trim_silence(x, -80.0)
    x = _finish(A.hp(x, 30.0, 2), tail=0.02)
    x = _norm(x, vel)
    x.setflags(write=False)
    return x


def marimba(note, vel=0.8, hardness=0.5, decay=1.0, seed=0):
    """Marimba (tuned bar modes 1 : 3.98 : 9.85, resonated fundamental, short wood knock). hardness 0 (yarn,
    round) .. 1 (hard, clicky); decay scales the ring (low notes ~1.5 s, high ~0.2 s). Returns mono."""
    return np.array(_mallet_cached('marimba', round(float(midi(note)), 3), round(float(vel), 3),
                                   round(float(hardness), 3), round(float(decay), 3), 0.25, int(seed)))


def glockenspiel(note, vel=0.7, hardness=0.6, decay=1.0, seed=0):
    """Glockenspiel (free-free steel bar modes 1 : 2.756 : 5.404 : 8.933 : 13.34, long ring, metal tick).
    Use the sounding pitch (glock sounds high: C6-C8, MIDI 84-108). Returns mono."""
    return np.array(_mallet_cached('glockenspiel', round(float(midi(note)), 3), round(float(vel), 3),
                                   round(float(hardness), 3), round(float(decay), 3), 0.15, int(seed)))


def bell(note, vel=0.7, kind='hand', hardness=0.5, decay=1.0, seed=0):
    """Bell by modal synthesis with beating doublets. kind 'hand' (handbell: fundamental + tuned twelfth,
    consonant - the default for music), 'church' (true church-bell partials: hum 0.5, prime 1, minor-third
    tierce 1.183, quint 1.5, nominal 2, ...; minor colour). note = strike pitch (prime). Returns mono."""
    return np.array(_mallet_cached('church' if kind == 'church' else 'hand', round(float(midi(note)), 3),
                                   round(float(vel), 3), round(float(hardness), 3), round(float(decay), 3), 0.0,
                                   int(seed)))


# ============================================================================================ synths
def _biquad_lp_coefs(fc, q):
    w0 = TWO_PI * np.clip(fc, 10.0, 0.45 * SR) / SR
    cw, sw = np.cos(w0), np.sin(w0)
    al = sw / (2.0 * q)
    a0 = 1.0 + al
    b0 = (1.0 - cw) / 2.0 / a0
    return b0, 2.0 * b0, b0, -2.0 * cw / a0, (1.0 - al) / a0


def tv_lowpass(x, fc, q=0.707, block=256):
    """2-pole resonant low-pass with a time-varying cutoff. fc: Hz scalar or per-sample array (len(x)).
    Coefficients update every `block` samples with the filter state carried as input/output history (direct
    form I semantics), so sweeps are smooth and click-free. Mono or stereo."""
    x = np.asarray(x, dtype=np.float64)
    mono = x.ndim == 1
    X = x[:, None] if mono else x
    n = len(X)
    if np.ndim(fc) == 0:
        b0, b1, b2, a1, a2 = _biquad_lp_coefs(float(fc), q)
        y = signal.lfilter([b0, b1, b2], [1.0, a1, a2], X, axis=0)
        return y[:, 0] if mono else y
    fc = np.asarray(fc, dtype=np.float64)
    nb = (n + block - 1) // block
    centre = np.minimum(np.arange(nb) * block + block // 2, n - 1)
    B0, B1, B2, A1, A2 = _biquad_lp_coefs(fc[np.minimum(centre, len(fc) - 1)], q)
    y = np.empty_like(X)
    ch = X.shape[1]
    xm1, xm2, ym1, ym2 = np.zeros(ch), np.zeros(ch), np.zeros(ch), np.zeros(ch)
    for k in range(nb):
        s, e = k * block, min(n, (k + 1) * block)
        b1, b2, a1, a2 = B1[k], B2[k], A1[k], A2[k]
        zi = np.stack([b1 * xm1 - a1 * ym1 + b2 * xm2 - a2 * ym2, b2 * xm1 - a2 * ym1])
        yb, _ = signal.lfilter([B0[k], b1, b2], [1.0, a1, a2], X[s:e], axis=0, zi=zi)
        y[s:e] = yb
        if e - s >= 2:
            xm1, xm2, ym1, ym2 = X[e - 1], X[e - 2], yb[-1], yb[-2]
        else:
            xm2, xm1, ym2, ym1 = xm1, X[e - 1], ym1, yb[-1]
    return y[:, 0] if mono else y


def pad(notes, dur=4.0, vel=0.7, wave='saw', voices=5, detune=14.0, attack=0.6, release=1.5, cutoff=1600.0,
        q=0.7, sweep=0.0, sweep_rate=0.08, open_to=None, chorus_mix=0.35, width=0.8, drift=2.0, seed=0):
    """Analogue-style pad: per note `voices` band-limited oscillators (wave 'saw' | 'warm' | 'tri' | 'square')
    spread over +-detune cents with slow random pitch drift (cents) and spread across the stereo field (width),
    raised-cosine attack / release (s), 2-pole low-pass at cutoff (Hz, q) with an optional slow LFO sweep
    (sweep = depth in octaves, sweep_rate Hz) and/or a ramp that opens the filter to open_to Hz at dur, then
    stereo chorus. notes: a MIDI list (chord) or one note. Returns stereo, len = dur + release."""
    notes = [notes] if np.ndim(notes) == 0 and not isinstance(notes, (list, tuple)) else list(notes)
    rng = np.random.default_rng([int(seed) & 0xFFFFFFFF, 11])
    N = _n(dur + release + 0.01)
    t = np.arange(N) / SR
    L, R = np.zeros(N), np.zeros(N)
    nv = max(1, int(voices))
    kd = drift * math.log(2) / 1200.0
    for nt in notes:
        f = hz(nt)
        I = []                                  # integrals of two slow LFOs (closed form): shared drift basis
        for _ in range(2):
            r_, p_ = rng.uniform(0.04, 0.17), rng.uniform(0, TWO_PI)
            I.append((math.cos(p_) - np.cos(TWO_PI * r_ * t + p_)) / (TWO_PI * r_))
        for v in range(nv):
            c = detune * (2.0 * v / (nv - 1) - 1.0) if nv > 1 else 0.0
            fv = f * 2.0 ** (c / 1200.0)
            ph = rng.random() + fv * t
            if drift:
                a_, b_ = rng.uniform(-1, 1, 2)
                ph = ph + fv * kd * (a_ * I[0] + b_ * I[1])
            y = _table_read(ph, fv * (1.0 + 2 * kd), wave)
            p = width * ((2.0 * v / (nv - 1) - 1.0) if nv > 1 else 0.0) * (1 if (v + len(notes)) % 2 else -1)
            th = (p + 1.0) * np.pi / 4
            L += math.cos(th) * y
            R += math.sin(th) * y
    x = np.stack([L, R], 1) * (math.sqrt(2) / math.sqrt(len(notes) * nv))
    fcur = np.full(N, float(cutoff))
    if open_to:
        fcur *= (float(open_to) / cutoff) ** np.clip(t / max(dur, 1e-3), 0.0, 1.0)
    if sweep:
        fcur *= 2.0 ** (sweep * np.sin(TWO_PI * sweep_rate * t + rng.uniform(0, TWO_PI)))
    x = tv_lowpass(x, fcur if (sweep or open_to) else float(cutoff), q)
    x *= _gate(N, dur, attack, release)[:, None]
    if chorus_mix > 0:
        x = chorus(x, mix=chorus_mix, seed=seed)
    x = _finish(A.hp(x, 35.0, 2), tail=0.01)
    return _norm(x, vel)


@functools.lru_cache(maxsize=2048)
def _pluck_cached(m, dur, vel, cutoff, env_oct, decay, amp_decay, q, wave, detune, release, sub, seed):
    f0 = hz(m)
    N = _n(dur + release + 0.005)
    t = np.arange(N) / SR
    fc = cutoff * 2.0 ** (env_oct * (0.4 + 0.6 * vel) * np.exp(-t / max(decay, 1e-3)))

    def amp(fk):
        return _lp_mag(fk, fc, q)

    x = _harm_bank(f0, N, amp, wave)
    if detune:
        x += 0.7 * _harm_bank(f0 * 2.0 ** (detune / 1200.0), N, amp, wave)
    if sub:
        x += sub * np.sin(TWO_PI * f0 * t) * 1.2
    env = np.exp(-t / max(amp_decay, 1e-3)) * _gate(N, dur, 0.0015, release)
    x = _finish(A.hp(x * env, 30.0, 2), tail=0.003)
    x = _norm(x, vel)
    x.setflags(write=False)
    return x


def pluck_synth(note, dur=0.2, vel=0.8, cutoff=700.0, env_oct=3.0, decay=0.12, amp_decay=0.35, q=1.2, wave='saw',
                detune=7.0, release=0.08, seed=0):
    """Synth pluck for arps: alias-free saw/square/warm (two oscillators `detune` cents apart) through a 2-pole
    low-pass whose cutoff starts env_oct octaves above `cutoff` (scaled by vel) and falls with time constant
    `decay` s; amplitude decays with amp_decay s and is gated at dur (+ release). Typical: 16ths, dur 0.1-0.3,
    cutoff 500-1500, env_oct 2-4. Returns mono."""
    return np.array(_pluck_cached(round(float(midi(note)), 3), round(float(dur), 4), round(float(vel), 3),
                                  round(float(cutoff), 1), round(float(env_oct), 3), round(float(decay), 4),
                                  round(float(amp_decay), 4), round(float(q), 3), wave, round(float(detune), 2),
                                  round(float(release), 4), 0.0, int(seed)))


def bass_pluck(note, dur=0.3, vel=0.8, cutoff=320.0, env_oct=2.5, decay=0.09, sub=0.6, release=0.06, q=1.0,
               wave='saw', seed=0):
    """Plucky synth bass: filtered saw (fast filter envelope, like pluck_synth) plus a sine sub at the
    fundamental (sub = level). Use MIDI 33-52. Returns mono."""
    return np.array(_pluck_cached(round(float(midi(note)), 3), round(float(dur), 4), round(float(vel), 3),
                                  round(float(cutoff), 1), round(float(env_oct), 3), round(float(decay), 4),
                                  round(float(max(dur, 0.05) * 1.5 + 0.2), 4), round(float(q), 3), wave, 0.0,
                                  round(float(release), 4), round(float(sub), 3), int(seed)))


@functools.lru_cache(maxsize=1024)
def _sub_cached(m, dur, vel, glide_from, glide, drive, harm, attack, release):
    f = hz(m)
    N = _n(dur + release + 0.005)
    t = np.arange(N) / SR
    if glide_from is not None:
        fg = hz(glide_from)
        freq = f + (fg - f) * np.exp(-t / max(glide / 4.0, 1e-4))
        ph = TWO_PI * np.cumsum(freq) / SR - TWO_PI * freq[0] / SR
    else:
        ph = TWO_PI * f * t
    x = np.sin(ph) + harm * np.sin(2.0 * ph) + 0.35 * harm * np.sin(3.0 * ph)
    x = np.tanh(drive * x) / math.tanh(drive)
    x *= _gate(N, dur, attack, release)
    x = _finish(A.hp(x, 20.0, 1), tail=0.002)
    x = _norm(x, vel)
    x.setflags(write=False)
    return x


def sub_bass(note, dur=0.5, vel=0.8, glide_from=None, glide=0.06, drive=1.6, harm=0.12, attack=0.006,
             release=0.06):
    """Sub bass: sine (+ harm x 2nd/3rd harmonic so it reads on phones) through gentle tanh saturation
    (drive 1 clean .. 3 warm). glide_from: previous note -> portamento over ~glide s. Use MIDI 28-50
    (E1-D3). Returns mono, len = dur + release."""
    return np.array(_sub_cached(round(float(midi(note)), 3), round(float(dur), 4), round(float(vel), 3),
                                None if glide_from is None else round(float(midi(glide_from)), 3),
                                round(float(glide), 4), round(float(drive), 3), round(float(harm), 3),
                                round(float(attack), 4), round(float(release), 4)))


# ============================================================================================ drums
@functools.lru_cache(maxsize=256)
def _kick_cached(vel, punch, tone, decay, click, drive, seed):
    rng = np.random.default_rng([int(seed) & 0xFFFFFFFF, 1])
    N = _n(decay * 4.0 + 0.06)
    t = np.arange(N) / SR
    f_hi = tone * (2.2 + 4.5 * punch)
    tp = 0.045 - 0.022 * punch
    f = tone + (f_hi - tone) * np.exp(-t / tp)
    ph = TWO_PI * (np.cumsum(f) - f[0]) / SR
    env = np.exp(-t / (decay * 0.55)) * (0.75 + 0.25 * np.exp(-t / 0.03))
    body = np.sin(ph) * env
    body = np.tanh(drive * body) / math.tanh(drive)
    nc = _n(0.012)
    cl = A.bp(rng.standard_normal(nc + 300), 1500.0, 7000.0, 2)[300:]
    cl *= np.exp(-np.arange(nc) / (0.0022 * SR))
    cl[:_n(0.0003)] *= _rc_up(_n(0.0003))
    x = body
    x[:nc] += cl * (click * (0.5 + punch)) * 0.6 / (np.max(np.abs(cl)) + 1e-9)
    on = _n(0.0008)
    x[:on] *= _rc_up(on)
    x = _finish(A.hp(x, 24.0, 2), tail=0.02)
    x = _norm(x, vel)
    x.setflags(write=False)
    return x


def soft_kick(vel=0.9, punch=0.5, tone=50.0, decay=0.30, click=0.25, drive=1.4, seed=0):
    """Soft kick: sine swept from tone * (2.2 + 4.5 punch) down to `tone` Hz (sweep time shorter with punch),
    body decay ~decay s, short band-passed click (click level), gentle saturation (drive). punch 0 (pillowy)
    .. 1 (tight, modern); tone 42-60 Hz. Returns mono; the onset is sample 0."""
    return np.array(_kick_cached(round(float(vel), 3), round(float(punch), 3), round(float(tone), 2),
                                 round(float(decay), 4), round(float(click), 3), round(float(drive), 3), int(seed)))


@functools.lru_cache(maxsize=256)
def _clap_cached(vel, tone, bursts, spread, decay, room, wet_db, seed):
    rng = np.random.default_rng([int(seed) & 0xFFFFFFFF, 2])
    N = _n(bursts * spread + decay * 7.0 + 0.02)
    t = np.arange(N) / SR
    nz = A.bp(rng.standard_normal(N + 400), tone * 0.55, min(tone * 4.0, 16000.0), 2)[400:]
    nz += 0.25 * A.hp(rng.standard_normal(N), 5000.0, 2)
    env = np.zeros(N)
    for k in range(bursts):
        t0 = k * spread * (1.0 + rng.uniform(-0.15, 0.15)) if k else 0.0
        last = k == bursts - 1
        u = t - t0
        tau = decay if last else 0.0035
        e = np.where(u >= 0, np.exp(-np.maximum(u, 0) / tau), 0.0) * (1.0 if last else 0.75 + 0.25 * rng.random())
        e *= np.clip(u / 0.0004, 0, 1)
        env = np.maximum(env, e)
    x = nz * env
    x = A.eq(x, 'peak', tone, 1.2, 3.0)
    x = _finish(x, tail=0.01)
    y = A.reverb(x, room, wet_db) if room else A._st(x)
    y = _trim_silence(y, -75.0)
    y = _finish(y, tail=0.03)
    y = _norm(y, vel)
    y.setflags(write=False)
    return y


def clap(vel=0.8, tone=1300.0, bursts=4, spread=0.0105, decay=0.09, room='room', wet_db=-7.0, seed=0):
    """Hand clap: `bursts` band-passed noise bursts ~spread s apart (the flam of many hands), the last one
    decaying over `decay` s, plus a reverb tail (A.reverb preset `room`, wet_db; room=None = dry). Returns
    stereo; the first burst is sample 0 (the perceived hit is ~ (bursts - 1) * spread later)."""
    return np.array(_clap_cached(round(float(vel), 3), round(float(tone), 1), int(bursts), round(float(spread), 5),
                                 round(float(decay), 4), room, round(float(wet_db), 2), int(seed)))


@functools.lru_cache(maxsize=512)
def _shaker_cached(vel, length, tone, attack, seed):
    rng = np.random.default_rng([int(seed) & 0xFFFFFFFF, 3])
    N = _n(attack + length * 4.0 + 0.01)
    t = np.arange(N) / SR
    nz = A.bp(rng.standard_normal(N + 400), tone * 0.6, min(tone * 2.0, 19000.0), 2)[400:]
    rise = np.clip(t / max(attack, 1e-4), 0.0, 1.0) ** 2
    env = np.where(t < attack, rise, np.exp(-(t - attack) / (length * 0.45)))
    x = _finish(nz * env, tail=0.004)
    x = _norm(x, vel)
    x.setflags(write=False)
    return x


def shaker(vel=0.7, length=0.07, tone=7500.0, attack=0.012, seed=0):
    """One shaker stroke: band-passed noise (tone .. 2 tone Hz) with a soft swelling attack (beads
    accelerating, `attack` s) and a decay of ~length s. Returns mono; peaks `attack` s after sample 0."""
    return np.array(_shaker_cached(round(float(vel), 3), round(float(length), 4), round(float(tone), 1),
                                   round(float(attack), 4), int(seed)))


def shaker_pattern(bars, bpm, swing=0.12, accents=(1.0, 0.45, 0.75, 0.5), vel=0.7, steps_per_beat=4,
                   beats_per_bar=4, humanize=0.003, width=0.25, tone=7500.0, seed=0):
    """A shaker groove: one stroke per 16th (steps_per_beat) for `bars` bars at bpm; accents cycle per beat
    (one value per step); odd steps are swung late by swing * step (0 straight .. 0.33 shuffle); strokes
    alternate slightly in tone / pan (forward / back) and are humanised by +-humanize s. Each stroke is placed
    so its PEAK (after its soft attack) lands on the step time. Returns stereo, len = bars * bar."""
    beat = 60.0 / bpm
    st = beat / steps_per_beat
    total = bars * beats_per_bar * steps_per_beat
    rng = np.random.default_rng([int(seed) & 0xFFFFFFFF, 4])
    tr = Track(bars * beats_per_bar * beat)
    att = 0.010
    for k in range(total):
        a = accents[k % len(accents)]
        tt = k * st + (swing * st if k % 2 else 0.0) + rng.uniform(-humanize, humanize)
        fwd = k % 2 == 0
        x = shaker(vel * a * (1.0 + rng.uniform(-0.06, 0.06)), 0.055 if fwd else 0.075,
                   tone * (1.06 if fwd else 0.94), att, seed=seed * 1000 + k % 8)
        tr.add(x, max(0.0, tt - att), pan=width * (0.5 if fwd else -0.5))
    return _finish(tr.buf, tail=0.01)


_HAT_F = (205.3, 304.4, 369.6, 522.7, 540.0, 800.0)


@functools.lru_cache(maxsize=256)
def _hat_cached(vel, open_, decay, tone, seed):
    rng = np.random.default_rng([int(seed) & 0xFFFFFFFF, 5])
    dec = decay if decay else (0.32 if open_ else 0.045)
    N = _n(dec * 5.0 + 0.01)
    t = np.arange(N) / SR
    metal = sum(osc(f * 1.7 * tone, N, 'square', rng.random()) for f in _HAT_F) / 6.0
    x = 0.65 * metal + 0.35 * rng.standard_normal(N)
    x = A.hp(A.bp(x, 6500.0 * tone, min(17000.0, 15000.0 * tone), 2), 5500.0 * tone, 2)
    env = np.exp(-t / dec) if not open_ else np.exp(-t / dec) * (0.6 + 0.4 * np.exp(-t / 0.02))
    on = _n(0.0004)
    env[:on] *= _rc_up(on)
    x = _finish(x * env, tail=0.006)
    x = _norm(x, vel)
    x.setflags(write=False)
    return x


def hat(vel=0.7, open=False, decay=None, tone=1.0, seed=0):
    """Hi-hat: six inharmonic band-limited square oscillators (808 ratios) + noise, band/high-passed around
    6.5-15 kHz (tone scales it). open=False: ~45 ms decay; open=True: ~320 ms (decay overrides). Returns mono."""
    return np.array(_hat_cached(round(float(vel), 3), bool(open), None if decay is None else round(float(decay), 4),
                                round(float(tone), 3), int(seed)))


@functools.lru_cache(maxsize=256)
def _brush_cached(vel, length, seed):
    rng = np.random.default_rng([int(seed) & 0xFFFFFFFF, 6])
    N = _n(length * 2.5 + 0.01)
    t = np.arange(N) / SR
    nz = A.bp(rng.standard_normal(N + 400), 1800.0, 9000.0, 2)[400:]
    att = length * 0.18
    env = np.where(t < att, (t / att) ** 1.5, np.exp(-(t - att) / (length * 0.4)))
    tap = A.lp(rng.standard_normal(N), 2500.0, 2) * np.exp(-t / 0.006) * 0.8
    x = nz * env + tap
    on = _n(0.001)
    x[:on] *= _rc_up(on)
    x = _finish(x, tail=0.006)
    x = _norm(x, vel)
    x.setflags(write=False)
    return x


def brush(vel=0.6, length=0.22, seed=0):
    """Brush stroke on a snare: a soft tap plus a band-passed (1.8-9 kHz) noise swish swelling over 18 % of
    `length` s and decaying. Returns mono."""
    return np.array(_brush_cached(round(float(vel), 3), round(float(length), 4), int(seed)))


@functools.lru_cache(maxsize=256)
def _snare_cached(vel, tone, snappy, decay, seed):
    rng = np.random.default_rng([int(seed) & 0xFFFFFFFF, 7])
    N = _n(decay * 5.0 + 0.02)
    t = np.arange(N) / SR
    f = tone * (1.0 + 0.25 * np.exp(-t / 0.012))
    ph = TWO_PI * (np.cumsum(f) - f[0]) / SR
    body = (np.sin(ph) + 0.45 * np.sin(1.6 * ph + 0.3)) * np.exp(-t / 0.07)
    nz = A.lp(A.bp(rng.standard_normal(N + 400), 1200.0, 8000.0, 2)[400:], 9000.0, 2)
    nz *= np.exp(-t / decay) * (0.5 + 0.5 * np.exp(-t / 0.02))
    x = 0.8 * body + snappy * 1.4 * nz / (np.max(np.abs(nz)) + 1e-9)
    on = _n(0.0009)
    x[:on] *= _rc_up(on)
    x = _finish(A.hp(x, 60.0, 2), tail=0.01)
    x = _norm(x, vel)
    x.setflags(write=False)
    return x


def snare_soft(vel=0.7, tone=185.0, snappy=0.5, decay=0.14, seed=0):
    """Soft snare (no rim crack): tuned body at `tone` Hz (slight pitch drop, 1.6x mode) + band-passed snare
    noise (snappy = level, decay s). Good for fills and ghost notes; add reverb_send for size. Returns mono."""
    return np.array(_snare_cached(round(float(vel), 3), round(float(tone), 2), round(float(snappy), 3),
                                  round(float(decay), 4), int(seed)))


def reverse_swell(dur=1.0, vel=0.8, notes=None, bright=1.0, seed=0):
    """Reverse swell that ENDS on its peak at exactly `dur` (place it at hit_time - dur): rising band-noise
    (600 Hz -> 6 kHz x bright, widening) plus, if notes (MIDI list) are given, reversed decaying tones of those
    notes (a 'reverse piano/pad' in key). Ends with a 12 ms fade to 0. Returns stereo, len = dur."""
    rng = np.random.default_rng([int(seed) & 0xFFFFFFFF, 8])
    N = _n(dur)
    t = np.arange(N) / SR
    p = t / max(dur, 1e-3)
    nz = A.noise_band(dur, rng, [(0, 600.0), (1, 6000.0 * bright)], [(0, 0.9), (1, 1.6)], width=0.7)[:N]
    env = (np.exp(4.0 * p) - 1.0) / (math.e ** 4 - 1.0)
    x = nz * env[:, None] * 0.6
    if notes:
        tone = np.zeros(N)
        rv = np.exp(-(dur - t) / max(0.3 * dur, 0.05))
        for k, nt in enumerate(notes):
            f = hz(nt)
            tone += (np.sin(TWO_PI * f * t + k) + 0.3 * np.sin(TWO_PI * 2 * f * t + k)) * rv
        tone /= max(len(notes), 1)
        x += A._st(tone) * 0.9 / (np.max(np.abs(tone)) + 1e-9) * np.max(np.abs(x))
    nf = _n(0.012)
    x[-nf:] *= (0.5 + 0.5 * np.cos(np.pi * np.arange(1, nf + 1) / nf))[:, None]
    x = _finish(A.hp(x, 40.0, 2), tail=0.002, head=0.01)
    return _norm(x, vel)


def riser(dur=2.0, vel=0.8, f_start=250.0, f_end=7000.0, note=None, seed=0):
    """Riser that ENDS at exactly `dur` (place at hit_time - dur): band-noise whose centre sweeps f_start ->
    f_end Hz (log), narrowing, with an accelerating tremolo and rising level; note (MIDI) adds a saw tone
    gliding up an octave from it. Ends with a 15 ms fade. Returns stereo, len = dur."""
    rng = np.random.default_rng([int(seed) & 0xFFFFFFFF, 9])
    N = _n(dur)
    t = np.arange(N) / SR
    p = t / max(dur, 1e-3)
    nz = A.noise_band(dur, rng, [(0, f_start), (1, f_end)], [(0, 1.4), (1, 0.7)], width=[(0, 0.2), (1, 0.9)])[:N]
    trem_rate = 3.0 + 13.0 * p ** 2
    trem = 0.75 + 0.25 * np.sin(TWO_PI * np.cumsum(trem_rate) / SR)
    env = p ** 1.8 * trem
    x = nz * env[:, None]
    if note is not None:
        f = hz(note) * 2.0 ** p
        tn = osc(f, N, 'saw') * p ** 2
        tn = tv_lowpass(tn, 400.0 + 6000.0 * p ** 2, 0.9)
        x += A._st(tn) * 0.5
    nf = _n(0.015)
    x[-nf:] *= (0.5 + 0.5 * np.cos(np.pi * np.arange(1, nf + 1) / nf))[:, None]
    x = _finish(A.hp(x, 60.0, 2), tail=0.002, head=0.01)
    return _norm(x, vel)


@functools.lru_cache(maxsize=64)
def _impact_cached(vel, dur, tone, room, wet_db, seed):
    rng = np.random.default_rng([int(seed) & 0xFFFFFFFF, 10])
    N = _n(dur)
    t = np.arange(N) / SR
    f = tone + tone * 1.1 * np.exp(-t / 0.09)
    ph = TWO_PI * (np.cumsum(f) - f[0]) / SR
    body = np.sin(ph) * np.exp(-t / (dur * 0.28))
    body = np.tanh(1.6 * body) / math.tanh(1.6)
    th = A.lp(rng.standard_normal(N + 400), 220.0, 2)[400:] * np.exp(-t / 0.07)
    x = body + 0.6 * th / (np.max(np.abs(th)) + 1e-9)
    x[:_n(0.004)] *= _rc_up(_n(0.004))
    x = A.bass_enhance(A._st(x), amount=0.5)[:, 0]
    x = _finish(A.hp(x, 22.0, 2), tail=0.05)
    y = A.reverb(x, room, wet_db) if room else A._st(x)
    y = _trim_silence(y, -75.0)
    y = _finish(y, tail=0.08)
    y = _norm(y, vel)
    y.setflags(write=False)
    return y


def impact_low(vel=0.9, dur=2.5, tone=40.0, room='hall', wet_db=-10.0, seed=0):
    """Soft low boom for downbeats / drops / the final hit: sine falling 2.1x -> tone Hz, saturated, decaying
    over ~dur, a low-passed noise thump, phone harmonics (A.bass_enhance) and a reverb tail (preset room).
    Returns stereo; onset at sample 0."""
    return np.array(_impact_cached(round(float(vel), 3), round(float(dur), 3), round(float(tone), 2), room,
                                   round(float(wet_db), 2), int(seed)))


# ============================================================================================ effects
def chorus(x, rate=0.7, depth_ms=2.2, delay_ms=13.0, mix=0.4, voices=2, seed=0):
    """Stereo chorus: `voices` modulated delay taps per channel (sine LFOs, L/R in quadrature), fractional
    delays by linear interpolation. mix = wet level added to the dry signal (0.2-0.5). Returns stereo."""
    x = A._st(x)
    n = len(x)
    rng = np.random.default_rng([int(seed) & 0xFFFFFFFF, 12])
    t = np.arange(n) / SR
    base = np.arange(n, dtype=np.float64)
    wet = np.zeros_like(x)
    for v in range(voices):
        ph0 = rng.uniform(0, TWO_PI)
        rv = rate * (1.0 + 0.23 * v)
        for c in range(2):
            d = (delay_ms + depth_ms * np.sin(TWO_PI * rv * t + ph0 + c * np.pi / 2)) * SR / 1000.0
            q = base - d
            i = np.floor(q).astype(np.int64)
            fr = q - i
            ok = i >= 0
            i0 = np.clip(i, 0, n - 1)
            i1 = np.clip(i + 1, 0, n - 1)
            wet[:, c] += np.where(ok, x[i0, c] * (1.0 - fr) + x[i1, c] * fr, 0.0)
    return x + wet * (mix / voices)


def haas(x, ms=12.0, side='right', level_db=0.0):
    """Haas widening of a mono (or the mid of a stereo) source: one side delayed by ms (8-25) at level_db.
    Not mono-safe for big delays (comb filter on fold-down) - keep ms < 20 and use on non-bass parts."""
    m = np.asarray(x, dtype=np.float64)
    m = m.mean(1) if m.ndim == 2 else m
    d = max(1, int(round(ms * SR / 1000.0)))
    dl = np.concatenate([np.zeros(d), m[:-d]]) * 10.0 ** (level_db / 20.0)
    return np.stack([m, dl], 1) if side == 'right' else np.stack([dl, m], 1)


def widen(x, w=1.3):
    """Mid/side width (A.width): 0 mono, 1 unchanged, > 1 wider."""
    return A.width(x, w)


def autopan(x, rate=0.25, depth=0.4, phase=0.0):
    """Slow sine auto-pan (Rhodes-suitcase style tremolo at higher rates). Returns stereo."""
    x = A._st(x)
    p = depth * np.sin(TWO_PI * rate * np.arange(len(x)) / SR + phase)
    th = (p + 1.0) * np.pi / 4
    m = x.mean(1)
    return np.stack([m * np.sqrt(2) * np.cos(th), m * np.sqrt(2) * np.sin(th)], 1)


def bus_comp(x, thresh_db=-18.0, ratio=2.0, knee_db=6.0, attack=0.01, release=0.15, makeup_db=0.0):
    """Gentle bus compressor (A.compressor_gain: feed-forward RMS, soft knee, stereo-linked).
    Returns stereo."""
    x = A._st(x)
    g = A.compressor_gain(x, thresh_db, ratio, knee_db, attack, release)
    return x * A.undb(g + makeup_db)[:, None]


def tilt_eq(x, gain_db=1.5, pivot=900.0):
    """Tilt EQ around pivot Hz: gain_db > 0 brighter (highs +g/2, lows -g/2), < 0 darker."""
    y = A.eq(x, 'ls', pivot, 0.5, -gain_db / 2.0)
    return A.eq(y, 'hs', pivot, 0.5, gain_db / 2.0)


def duck(x, key, depth_db=6.0, attack=0.005, release=0.16, thresh_rel_db=-26.0):
    """Sidechain duck of x under key (a kick Track/array, a VO stem, ...): wraps A.sidechain (50 ms centred
    key level, gain reduction up to depth_db once the key is within 6 dB of its max). Kick pump: depth 4-7,
    attack 0.003-0.008, release 0.12-0.22. Returns stereo."""
    key = key.buf if isinstance(key, Track) else key
    x = x.buf if isinstance(x, Track) else x
    return A.sidechain(x, key, depth_db=depth_db, attack=attack, release=release, thresh_rel_db=thresh_rel_db)


def pump(x, times, depth_db=6.0, attack=0.004, release=0.18):
    """Synthetic sidechain 'pump': gain dips depth_db, fully down at each time in `times` (ramping in over
    `attack` s before it) and recovering with a raised-cosine over `release` s. Exact and detector-free.
    Returns stereo."""
    x = A._st(x.buf if isinstance(x, Track) else x)
    n = len(x)
    gr = np.zeros(n)
    na, nr = _n(attack), _n(release)
    shape = np.concatenate([_rc_up(na), 0.5 + 0.5 * np.cos(np.pi * np.arange(nr) / nr)])
    for tm in times:
        i0 = int(round(tm * SR)) - na
        a, b = max(0, i0), min(n, i0 + len(shape))
        if b > a:
            gr[a:b] = np.maximum(gr[a:b], shape[a - i0:b - i0])
    return x * A.undb(-depth_db * gr)[:, None]


def reverb_send(x, preset='plate', wet_db=-12.0, hp_hz=180.0, keep_tail=False, **kw):
    """Wet-only reverb return (A.reverb with dry=0) for a send: preset room | studio | dark | plate | hall |
    air | outdoor (or make_ir kwargs), wet_db relative to the input, hp_hz high-passes the send (keeps the low
    end dry). Same length as x unless keep_tail. Returns stereo."""
    x = A._st(x.buf if isinstance(x, Track) else x)
    y = A.reverb(x, preset, wet_db, dry=0.0, send_hp=hp_hz, **kw)
    return y if keep_tail else y[:len(x)]


def fade_in(x, sec, shape='cos'):
    """Fade in over the first sec seconds (shape 'cos' raised-cosine, 'lin', 'exp' (slow start))."""
    return _fade(x, 0.0, sec, True, shape)


def fade_out(x, sec, end=None, shape='cos'):
    """Fade out over sec seconds ending at `end` (s; default the end of x); everything after end = 0."""
    x = np.array(x, dtype=np.float64, copy=True)
    e = len(x) / SR if end is None else end
    return _fade(x, e - sec, sec, False, shape)


def _fade(x, t0, sec, fin, shape):
    x = np.array(x, dtype=np.float64, copy=True)
    n = len(x)
    i0, m = int(round(t0 * SR)), max(1, _n(sec))
    a, b = min(max(i0, 0), n), min(max(i0 + m, 0), n)
    u = (np.arange(a, b) - i0) / m
    if shape == 'lin':
        w = u
    elif shape == 'exp':
        w = u ** 3
    else:
        w = 0.5 - 0.5 * np.cos(np.pi * u)
    if not fin:
        w = 1.0 - w
    x[a:b] *= w[:, None] if x.ndim == 2 else w
    if fin:
        x[:a] = 0.0
    else:
        x[b:] = 0.0
    return x


def gain_ramp(x, points):
    """Volume automation: points [(t_s, gain_db), ...] linearly interpolated in dB (held outside)."""
    x = np.asarray(x, dtype=np.float64)
    pts = np.asarray(points, dtype=np.float64)
    g = A.undb(np.interp(np.arange(len(x)) / SR, pts[:, 0], pts[:, 1]))
    return x * (g[:, None] if x.ndim == 2 else g)


def normalise_peak(x, peak_db=-1.0, true_peak=True):
    """Scale so the (true) peak is peak_db (dBTP / dBFS). Pure gain, never clips."""
    x = np.asarray(x, dtype=np.float64)
    pk = A.true_peak(x) if true_peak else float(A.db(np.max(np.abs(x)) + 1e-12))
    return x * A.undb(peak_db - pk)


def normalise_lufs(x, target=-16.0, tp_ceiling=-1.0, limit=True, tol=0.05):
    """Scale to `target` integrated LUFS (A.loudness). If the true peak would exceed tp_ceiling, a gentle
    lookahead limiter (A.limiter_gain) is applied and the gain re-iterated (limit=False: report only).
    Returns (y, info{lufs, true_peak, gain_db, limiter_max_gr_db, ok})."""
    x = A._st(x)
    g = target - A.loudness(x)
    ceil = tp_ceiling - 0.3
    gl = np.ones(len(x))
    y = x * A.undb(g)
    for _ in range(10):
        y0 = x * A.undb(g)
        if limit and A.true_peak(y0) > tp_ceiling - 0.05:
            gl = A.limiter_gain(y0, ceil)
        y = y0 * gl[:, None]
        L, tp = A.loudness(y), A.true_peak(y)
        if abs(L - target) <= tol and (tp <= tp_ceiling or not limit):
            break
        g += target - L
        if limit and tp > tp_ceiling:
            ceil -= tp - tp_ceiling + 0.05
    L, tp = A.loudness(y), A.true_peak(y)
    return y, dict(lufs=round(L, 2), true_peak=round(tp, 2), gain_db=round(float(g), 2),
                   limiter_max_gr_db=round(float(-A.db(np.min(gl))), 2),
                   ok=bool(abs(L - target) <= max(tol, 0.1) and (tp <= tp_ceiling + 0.01 or not limit)))


# ============================================================================================ QA
def click_report(x, ratio=6.0, isolation=2.5, floor_db=-60.0, win_ms=10.0, ctx_ms=25.0, max_events=8):
    """Click / discontinuity detector (max sample-step vs local RMS). Every sample step d = |x[n] - x[n-1]|
    (silence assumed before and after the array) is compared with the RMS of the steps in the surrounding
    win_ms window, excluding itself. A click is a step louder than floor_db that is > `ratio` x that local
    step-RMS AND > `isolation` x every other step within +-ctx_ms (outside +-0.5 ms around it). The second test
    stops periodic waveform edges (a bright low saw's ramp reset every period, ratio up to ~15) from counting;
    cut-off notes, DC jumps, spikes and buffer seams fail both. Steady noise reaches ~5-6 but is never isolated.
    Returns {clean, count, worst_ratio (largest step / local-RMS anywhere, informational), worst_t,
    events: [(t_s, ratio, isolation, step_db), ...] worst first}."""
    x = A._st(x)
    z = np.zeros((1, 2))
    d = np.abs(np.diff(np.concatenate([z, x, z]), axis=0)).max(1)       # len n + 1, worst channel
    e = d * d
    W = max(3, _n(win_ms / 1000.0))
    loc = uniform_filter1d(e, W, mode='constant')
    excl = np.maximum((loc * W - e) / (W - 1), 0.0)
    r = np.where(d > 10.0 ** (floor_db / 20.0), d / np.sqrt(excl + 1e-24), 0.0)
    idx = np.flatnonzero(r > ratio)
    events = []
    if len(idx):
        ex, cw = _n(0.0005), _n(ctx_ms / 1000.0)
        for gp in np.split(idx, np.flatnonzero(np.diff(idx) > _n(0.005)) + 1):
            j = int(gp[np.argmax(r[gp])])
            nb = np.concatenate([d[max(0, j - cw):max(0, j - ex)], d[j + ex + 1:j + cw + 1]])
            iso = float(d[j] / (nb.max() + 1e-24)) if len(nb) else 1e9
            if iso > isolation:
                events.append((round(j / SR, 4), round(float(r[j]), 1), round(min(iso, 1e6), 1),
                               round(float(A.db(d[j])), 1)))
        events.sort(key=lambda ev: -ev[1])
    return dict(clean=not events, count=len(events), worst_ratio=round(float(r.max()), 1),
                worst_t=round(float(np.argmax(r)) / SR, 4), events=events[:max_events])


def dc_report(x):
    """DC and sub-sonic QA: per-channel mean (dc), energy below 20 Hz and 40 Hz relative to the total (dB) and
    the share below 60 Hz. ok = |dc| < 1e-3 and sub20 < -30 dB."""
    x = A._st(x)
    dc = np.abs(x.mean(0))
    P = np.abs(np.fft.rfft(x - x.mean(0), axis=0)) ** 2
    f = np.fft.rfftfreq(len(x), 1.0 / SR)
    tot = P.sum() + 1e-30
    sub20 = 10 * np.log10(P[f < 20].sum() / tot + 1e-30)
    sub40 = 10 * np.log10(P[f < 40].sum() / tot + 1e-30)
    low60 = 100.0 * P[f < 60].sum() / tot
    return dict(dc=[round(float(v), 6) for v in dc], sub20_db=round(float(sub20), 1), sub40_db=round(float(sub40), 1),
                low60_pct=round(float(low60), 1), ok=bool(dc.max() < 1e-3 and sub20 < -30.0))


def qa(x):
    """Everything at once: finite, sample peak dBFS, true peak dBTP, integrated LUFS, dc_report, click_report."""
    x = A._st(x)
    fin = bool(np.all(np.isfinite(x)))
    out = dict(finite=fin, dur=round(len(x) / SR, 3))
    if not fin:
        return out
    pk = float(np.max(np.abs(x)))
    out.update(peak_dbfs=round(float(A.db(pk + 1e-12)), 2), clip=bool(pk >= 1.0), true_peak=round(A.true_peak(x), 2),
               lufs=round(A.loudness(x), 2), dcrep=dc_report(x), clicks=click_report(x))
    return out


# ============================================================================================ beat grid
_FLUX_NPERSEG, _FLUX_HOP = 2048, 240
FLUX_BIAS = 0.0                # set below by calibration: true onset time = flux index * hop + FLUX_BIAS


def _flux(x):
    _, tt, Z = signal.stft(x, SR, nperseg=_FLUX_NPERSEG, noverlap=_FLUX_NPERSEG - _FLUX_HOP)
    fl = np.maximum(np.diff(np.log1p(np.abs(Z) * 100), axis=1), 0).sum(0)
    return fl, tt


def _grid_score(fl, tend, bpm, offs, hop):
    per = 60.0 / bpm
    nb = int(tend / per) + 2
    tms = offs[:, None] + np.arange(nb)[None, :] * per
    ok = tms < tend
    idx = np.clip(np.round(tms / hop).astype(np.int64), 0, len(fl) - 1)
    ok &= np.round(tms / hop) < len(fl)
    return np.where(ok, fl[idx], 0.0).sum(1) / np.maximum(ok.sum(1), 1)


def _beat_grid_measure(x, bpm, lo=0.97, hi=1.03, tol_bpm=0.3, tol_phase=0.015):
    """Measure tempo and beat phase (spectral-flux onsets, the reels-studio beatgrid.py method: STFT 2048 /
    hop 240 log-magnitude flux; search bpm * [lo..hi] in 0.25 % steps and the offset in 5 ms steps), then refine:
    the flux peak near every predicted beat (parabolic interpolation) is fitted with a weighted line, giving
    sub-ms tempo and phase. Phases are bias-corrected (FLUX_BIAS: the flux of a centred 2048 window peaks ~17 ms
    before the onset). x: array or wav path. Returns {tempo, phase (s, + = onsets late vs the grid t = n*60/bpm),
    tempo_coarse, phase_coarse, phase_beatgrid (raw beatgrid.py number, ~-15..-19 ms for on-grid audio),
    strength (on-grid flux / mean, > 2 = clearly on a grid), n_beats, ok}."""
    if isinstance(x, str):
        x = A.read_wav(x)[0]
    m = np.asarray(x, dtype=np.float64)
    m = m.mean(1) if m.ndim == 2 else m
    fl, tt = _flux(m)
    hop = _FLUX_HOP / SR
    tend = tt[-1]
    best = (-1.0, bpm, 0.0)
    for b in bpm * np.arange(lo, hi, 0.0025):
        offs = np.arange(0, 60.0 / b, 0.005)
        sc = _grid_score(fl, tend, b, offs, hop)
        j = int(np.argmax(sc))
        if sc[j] > best[0]:
            best = (float(sc[j]), float(b), float(offs[j]))
    s, b0, off0 = best
    per0 = 60.0 / b0
    raw_phase = (off0 + per0 / 2) % per0 - per0 / 2
    # refine: local flux peaks near each predicted beat, weighted linear fit time = c + k * period
    ks, ts, ws = [], [], []
    thr = np.median(fl) + 2.0 * np.std(fl)
    w = int(round(0.03 / hop))
    for k in range(int((tend - off0) / per0) + 1):
        c = int(round((off0 + k * per0) / hop))
        a, e = max(1, c - w), min(len(fl) - 1, c + w + 1)
        if e - a < 3:
            continue
        j = a + int(np.argmax(fl[a:e]))
        if fl[j] < thr or j <= 0 or j >= len(fl) - 1:
            continue
        y0, y1, y2 = fl[j - 1], fl[j], fl[j + 1]
        den = y0 - 2 * y1 + y2
        dj = 0.5 * (y0 - y2) / den if den < 0 else 0.0
        ks.append(k)
        ts.append((j + float(np.clip(dj, -0.5, 0.5))) * hop)
        ws.append(fl[j])
    tempo, phase = b0, raw_phase + FLUX_BIAS
    if len(ks) >= 4:
        K, T, Wt = np.array(ks, float), np.array(ts), np.array(ws)
        keep = np.ones(len(K), bool)
        for _ in range(3):
            pfit = np.polyfit(K[keep], T[keep], 1, w=np.sqrt(Wt[keep]))
            res = T - np.polyval(pfit, K)
            nk = np.abs(res) < max(0.008, 2.5 * np.std(res[keep]))
            if nk.sum() < 4 or np.array_equal(nk, keep):
                break
            keep = nk
        per, c0 = float(pfit[0]), float(pfit[1]) + FLUX_BIAS
        tempo = 60.0 / per
        phase = (c0 + per / 2) % per - per / 2
    out = dict(tempo=round(tempo, 3), phase=round(phase, 4), tempo_coarse=round(b0, 3),
               phase_coarse=round(((raw_phase + FLUX_BIAS) + per0 / 2) % per0 - per0 / 2, 4),
               phase_beatgrid=round(raw_phase, 4), strength=round(float(s / (fl.mean() + 1e-12)), 2), n_beats=len(ks))
    out['ok'] = bool(abs(out['tempo'] - bpm) <= tol_bpm and abs(out['phase']) <= tol_phase)
    return out


def _calibrate_flux_bias():
    """Flux-onset timing bias for a train of soft kicks exactly on a 120 BPM grid (deterministic)."""
    N = _n(12.0)
    x = np.zeros(N)
    k = np.array(_kick_cached(0.9, 0.5, 50.0, 0.3, 0.25, 1.4, 0))
    for b in range(1, 22):
        i = int(round(b * 0.5 * SR))
        m = min(len(k), N - i)
        x[i:i + m] += k[:m]
    global FLUX_BIAS
    FLUX_BIAS = 0.0
    r = _beat_grid_measure(x, 120.0)
    FLUX_BIAS = -r['phase']
    return FLUX_BIAS


@functools.lru_cache(maxsize=1)
def _bias_ready():
    return _calibrate_flux_bias()


def beat_grid_check(x, bpm, lo=0.97, hi=1.03, tol_bpm=0.3, tol_phase=0.015):
    _bias_ready()
    return _beat_grid_measure(x, bpm, lo, hi, tol_bpm, tol_phase)


beat_grid_check.__doc__ = _beat_grid_measure.__doc__


# ============================================================================================ delivery
def load_reel_stems(name):
    """Stems of a finished VO version from <AUD> (A.AUDIO): name 'reel1' or 'reel1_vo' -> dict(vo, sfx, mix,
    dur, n) read from <name>_vo_vo_stem.wav, <name>_vo_sfx_stem.wav, <name>_vo_mix.wav (48 kHz stereo)."""
    base = name if name.endswith('_vo') else name + '_vo'
    out = {}
    for key, suf in (('vo', '_vo_stem'), ('sfx', '_sfx_stem'), ('mix', '_mix')):
        p = os.path.join(A.AUDIO, base + suf + '.wav')
        x, sr = A.read_wav(p)
        if sr != SR:
            raise ValueError('%s is %d Hz' % (p, sr))
        out[key] = A._st(x)
    n = len(out['mix'])
    for k in ('vo', 'sfx'):
        out[k] = fit(out[k], n)
    out['n'], out['dur'] = n, n / SR
    return out


def speech_mask(vo, floor_db=-50.0, rel_db=-30.0, fill=0.3, win=0.05):
    """Boolean per-sample mask of speech in a VO stem: 50 ms RMS above max(floor_db, loudest + rel_db),
    pauses shorter than `fill` s inside phrases filled."""
    m = A._st(vo).mean(1)
    p = uniform_filter1d(m * m, _n(win))
    lv = 10 * np.log10(np.maximum(p, 1e-20))
    act = lv > max(floor_db, float(lv.max()) + rel_db)
    idx = np.flatnonzero(act)
    if len(idx) > 1:
        gaps = np.flatnonzero(np.diff(idx) > 1)
        for g in gaps:
            a, b = idx[g] + 1, idx[g + 1]
            if b - a < _n(fill):
                act[a:b] = True
    return act


def _dilate(mask, before, after):
    """Grow True regions by `before` / `after` seconds."""
    m = mask.astype(np.float64)
    nb, na = _n(before), _n(after)
    c = np.concatenate([[0.0], np.cumsum(m)])
    n = len(m)
    i = np.arange(n)
    lo = np.clip(i - na, 0, n)
    hi = np.clip(i + nb + 1, 0, n)
    return (c[hi] - c[lo]) > 0


def _bed_measure(bed, lv, gap):
    """Median short-term (3 s) loudness of the bed over the concatenated VO-gap samples, and the median
    momentary voice-minus-music difference over speech frames (lv = the VO's momentary loudness curve;
    frames within 15 LU of its max)."""
    g = bed[gap]
    if len(g) >= _n(3.2):
        _, st = A.loudness_curve(g, win=3.0, hop=0.1)
    elif len(g) >= _n(0.5):
        _, st = A.loudness_curve(g, win=0.4, hop=0.05)
    else:
        st = np.array([-120.0])
    st = st[st > -70.0]
    gap_st = float(np.median(st)) if len(st) else -120.0
    _, lm = A.loudness_curve(bed)
    sel = lv > lv.max() - 15.0
    vm = float(np.median((lv - lm)[sel])) if sel.any() else 99.0
    return gap_st, vm


def render_bed(clean, vo_stem, sfx_stem, mix_ref=None, gap_lu=7.0, min_vo_lu=10.0, vo_duck_db=9.0, vo_attack=0.04,
               vo_release=0.4, sfx_duck_db=3.0, sfx_attack=0.01, sfx_release=0.25, ref_lufs=None, verbose=True):
    """Music bed for a VO version. clean: the music render (any level, stereo, ideally exactly the VO mix length;
    it is padded / trimmed to len(vo_stem)). Ducks it vo_duck_db under the VO (A.sidechain keyed on vo_stem,
    attack / release vo_attack / vo_release) and sfx_duck_db under the SFX stem, then searches the level:
    target = the median short-term (3 s) loudness of the music over the VO gaps (speech mask dilated 0.05 s
    before / vo_release after) is `gap_lu` LU below the reference mix's integrated loudness (mix_ref, or
    ref_lufs, or -14), but the median voice-minus-music momentary difference under speech must stay
    >= min_vo_lu (the music is lowered further if needed). Returns (bed (N, 2), measurements dict)."""
    vo, sfx = A._st(vo_stem), A._st(sfx_stem)
    N = len(vo)
    sfx = fit(sfx, N)
    x = fit(clean, N)
    d = A.sidechain(x, vo, depth_db=vo_duck_db, attack=vo_attack, release=vo_release)
    if sfx_duck_db > 0 and np.any(sfx):
        d = A.sidechain(d, sfx, depth_db=sfx_duck_db, attack=sfx_attack, release=sfx_release)
    ref = A.loudness(fit(mix_ref, N)) if mix_ref is not None else (ref_lufs if ref_lufs is not None else -14.0)
    sp = speech_mask(vo)
    gap = ~_dilate(sp, 0.05, vo_release)
    if gap.sum() < _n(1.0):                       # wall-to-wall VO: measure where the speech mask is off
        gap = ~sp
    target = ref - gap_lu
    _, lv = A.loudness_curve(vo)
    gap0, vm0 = _bed_measure(d, lv, gap)
    g = min(target - gap0, vm0 - min_vo_lu - 0.2)
    limited = 'gap' if (target - gap0) <= (vm0 - min_vo_lu - 0.2) else 'vo'
    bed = d * A.undb(g)
    for _ in range(4):
        gst, vm = _bed_measure(bed, lv, gap)
        adj = 0.0
        if vm < min_vo_lu:
            adj = vm - min_vo_lu - 0.1
        elif limited == 'gap' and abs(gst - target) > 0.1:
            adj = min(target - gst, vm - min_vo_lu - 0.1)
        if abs(adj) < 0.02:
            break
        g += adj
        bed = d * A.undb(g)
    gst, vm = _bed_measure(bed, lv, gap)
    duck_gr = A.db(np.abs(d).max(1) + 1e-12) - A.db(np.abs(x).max(1) + 1e-12)
    meas = dict(gain_db=round(float(g), 2), ref_lufs=round(float(ref), 2), gap_target_lufs=round(float(target), 2),
                gap_st_lufs=round(gst, 2), gap_minus_ref_lu=round(gst - ref, 2), vo_minus_music_lu=round(vm, 2),
                limited_by=limited, speech_pct=round(float(100.0 * sp.mean()), 1),
                music_lufs=round(A.loudness(bed), 2),
                duck_median_under_speech_db=round(float(np.median(duck_gr[sp & (np.abs(x).max(1) > 1e-4)]))
                                                  if (sp & (np.abs(x).max(1) > 1e-4)).any() else 0.0, 2),
                ok=bool(vm >= min_vo_lu - 0.05 and (limited == 'vo' or abs(gst - target) <= 0.3)))
    if verbose:
        print('render_bed: gain %+.2f dB | gap short-term %.2f LUFS (target %.2f = ref %.2f - %.1f) | voice-music '
              '%.2f LU (>= %.1f) | music %.2f LUFS | limited by %s' % (g, gst, target, ref, gap_lu, vm, min_vo_lu,
                                                                      meas['music_lufs'], limited))
    return bed, meas


def master_withmusic(vo_stem, sfx_stem, bed, target=-14.0, tol=0.2, ceiling=-2.3, tp_max=-2.0, max_iter=12,
                     verbose=True):
    """Final 'with music' master: vo + sfx + bed (all same length as the VO stem) -> gain + A.limiter_gain at
    `ceiling` dBTP (lookahead, true-peak), re-gained until |LUFS - target| <= 0.05 (must end within tol) and the
    true peak <= tp_max (the ceiling is lowered if inter-sample overs remain). Returns (mix (N, 2), rep{lufs,
    true_peak, gain_db, limiter_max_gr_db, iterations, ceiling, lra, music_lufs, stems{vo, sfx, music}, ok})."""
    vo = A._st(vo_stem)
    N = len(vo)
    sfx, bd = fit(sfx_stem, N), fit(bed, N)
    bus = vo + sfx + bd
    g = target - A.loudness(bus)
    ceil = ceiling
    it = 0
    for it in range(1, max_iter + 1):
        y0 = bus * A.undb(g)
        gl = A.limiter_gain(None, ceil, pk=A.tp_envelope(y0))
        y = y0 * gl[:, None]
        L, tp = A.loudness(y), A.true_peak(y)
        if abs(L - target) <= 0.05 and tp <= tp_max - 0.02:
            break
        if abs(L - target) > 0.05:
            g += target - L
        if tp > tp_max - 0.02:
            ceil -= tp - (tp_max - 0.08)
    G = A.undb(g) * gl[:, None]
    stems = dict(vo=vo * G, sfx=sfx * G, music=bd * G)
    rep = dict(lufs=round(L, 2), true_peak=round(tp, 2), gain_db=round(float(g), 2),
               limiter_max_gr_db=round(float(-A.db(np.min(gl))), 2), iterations=it, ceiling=round(ceil, 2),
               lra=round(A.loudness_range(y), 2), music_lufs=round(A.loudness(stems['music']), 2), stems=stems,
               ok=bool(abs(L - target) <= tol and tp <= tp_max))
    if verbose:
        print('master_withmusic: %.2f LUFS  %.2f dBTP  (gain %+.2f dB, limiter max %.2f dB, %d it, ceiling %.2f)  '
              'music stem %.2f LUFS  ok=%s' % (L, tp, g, rep['limiter_max_gr_db'], it, ceil, rep['music_lufs'],
                                               rep['ok']))
    return y, rep


def _ffmpeg(args):
    exe = shutil.which('ffmpeg')
    if not exe:
        raise RuntimeError('ffmpeg not found')
    r = subprocess.run([exe, '-y', '-hide_banner', '-loglevel', 'error'] + args, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError('ffmpeg failed: %s' % r.stderr[-800:])


def _probe(path):
    exe = shutil.which('ffprobe')
    if not exe:
        return {}
    import json
    r = subprocess.run([exe, '-v', 'error', '-show_streams', '-show_format', '-of', 'json', path],
                       capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except ValueError:
        return {}


def write_mp3(src, path, title='', artist=None, album=None, comment=None):
    """MP3 delivery: src = wav path or float array (written to a temp 24-bit wav first) -> ffmpeg libmp3lame
    320 kb/s CBR, 48 kHz stereo, ID3v2.3 tags (title, optional artist / album / comment). Returns {path, dur,
    bit_rate, sample_rate, title}."""
    tmpd = None
    try:
        if isinstance(src, str):
            wav = src
        else:
            tmpd = tempfile.mkdtemp(prefix='msmp3_')
            wav = A._write_wav(os.path.join(tmpd, 'in.wav'), A._st(src), 24)
        os.makedirs(os.path.dirname(os.path.abspath(path)) or '.', exist_ok=True)
        meta = ['-metadata', 'title=%s' % title]
        for k, v in (('artist', artist), ('album', album), ('comment', comment)):
            if v:
                meta += ['-metadata', '%s=%s' % (k, v)]
        _ffmpeg(['-i', wav, '-map', '0:a:0', '-map_metadata', '-1', '-c:a', 'libmp3lame', '-b:a', '320k',
                 '-ar', '48000', '-ac', '2', '-id3v2_version', '3'] + meta + [path])
    finally:
        if tmpd:
            shutil.rmtree(tmpd, ignore_errors=True)
    pr = _probe(path)
    st = (pr.get('streams') or [{}])[0]
    fm = pr.get('format', {})
    return dict(path=path, dur=float(fm.get('duration', 0) or 0), bit_rate=int(st.get('bit_rate', 0) or 0),
                sample_rate=int(st.get('sample_rate', 0) or 0), title=(fm.get('tags') or {}).get('title', ''))


def make_preview(video_in, audio, out_mp4, audio_bitrate='192k'):
    """Preview mp4: the video stream copied (-c:v copy) with `audio` (wav path or float array) as AAC
    192 kb/s 48 kHz, -shortest, +faststart. Returns out_mp4."""
    tmpd = None
    try:
        if isinstance(audio, str):
            wav = audio
        else:
            tmpd = tempfile.mkdtemp(prefix='msprev_')
            wav = A._write_wav(os.path.join(tmpd, 'a.wav'), A._st(audio), 24)
        os.makedirs(os.path.dirname(os.path.abspath(out_mp4)) or '.', exist_ok=True)
        _ffmpeg(['-i', video_in, '-i', wav, '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy', '-c:a', 'aac',
                 '-b:a', audio_bitrate, '-ar', '48000', '-shortest', '-movflags', '+faststart', out_mp4])
    finally:
        if tmpd:
            shutil.rmtree(tmpd, ignore_errors=True)
    return out_mp4


# ============================================================================================ demo arrangement
def demo_arrangement(bpm=120.0, bars=16, seed=0, verbose=False):
    """A complete 16-bar example (the template for composers): A-minor progression Am7 - Fmaj7 - Cadd9 - G,
    felt-piano intro, pad (filter sweep, chorus), e-piano stabs, nylon strums, sub bass with glide + bass
    pluck after the drop, a pluck arp, soft kick / clap / hats / shaker groove, a riser into the drop
    (bar bars // 2) with an impact, sidechain pump keyed on the kick, plate / hall sends, bus comp + tilt EQ.
    Returns (stereo mix peaking at -1 dBFS, info{bpm, bars, dur, drop_bar, render_s})."""
    t0 = time.time()
    g = Grid(bpm)
    dur = bars * g.bar_s
    syms = ['Am7', 'Fmaj7', 'Cadd9', 'G']
    prog = progression(syms, octave=4, lo=55, hi=79)
    drop = bars // 2
    groove0 = 2
    last = bars - 1
    T = {k: Track(dur, k) for k in ('pad', 'keys', 'gtr', 'bass', 'arp', 'kick', 'perc', 'fx')}
    rng = np.random.default_rng(seed)
    hum = lambda: rng.uniform(-0.003, 0.003)               # noqa: E731
    for b in range(bars):
        ch, sym = prog[b % 4], syms[b % 4]
        # pad: one chord per bar (2 bars intro open, filter opening into the drop)
        if b < last:
            T['pad'].add(pad(ch, dur=g.bar_s, vel=0.6, attack=0.35 if b else 0.8, release=0.9,
                             cutoff=900.0 if b < drop else 1500.0, sweep=0.5, sweep_rate=0.11,
                             open_to=2400.0 if b == drop - 1 else None, seed=b), g.bar(b), gain_db=-13)
        else:
            T['pad'].add(pad(ch, dur=g.bar_s * 0.75, vel=0.6, release=1.2, cutoff=1200.0, seed=b), g.bar(b),
                         gain_db=-13)
        # keys: felt piano broken chords in the intro, e-piano stabs after
        if b < groove0:
            for k in range(8):
                nt = ch[[0, 1, 2, 3, 2, 1, 0, 1][k] % len(ch)]
                T['keys'].add(felt_piano(nt, dur=g.beat_s * 0.9, vel=0.55 + 0.1 * (k % 2 == 0), pedal=True,
                                         tail=2.0), g.bar(b, 0.5 * k) + hum(), gain_db=-7, pan=-0.15)
        elif b < last:
            for bt, v in ((0.0, 0.62), (1.5, 0.5), (2.5, 0.55)):
                for nt in ch:
                    T['keys'].add(fm_epiano(nt, dur=g.beat_s * 0.8, vel=v), g.bar(b, bt) + hum(), gain_db=-15,
                                  pan=-0.25)
        else:
            for k, nt in enumerate(ch):
                T['keys'].add(felt_piano(nt, dur=g.bar_s, vel=0.55, pedal=True, tail=3.0), g.bar(b) + 0.01 * k,
                              gain_db=-9)
        # nylon strums (down on 1, up on the 'and' of 2) from the groove on
        if groove0 <= b < last:
            gch = chord(sym.replace('add9', '').replace('maj7', '').replace('7', ''), octave=3)
            T['gtr'].add(strum(gch, dur=g.beat_s * 1.4, vel=0.7, direction='down', seed=b), g.bar(b), gain_db=-12,
                         pan=0.35)
            T['gtr'].add(strum(gch, dur=g.beat_s * 1.2, vel=0.55, direction='up', seed=100 + b), g.bar(b, 1.5),
                         gain_db=-13, pan=0.35)
        # bass
        root = bass_note(sym, 2)
        prev = bass_note(syms[(b - 1) % 4], 2) if b else None
        if groove0 <= b < last:
            T['bass'].add(sub_bass(root, dur=g.beat_s * 1.6, vel=0.8, glide_from=prev if b % 2 == 0 else None),
                          g.bar(b), gain_db=-6)
            T['bass'].add(sub_bass(root, dur=g.beat_s * 1.1, vel=0.7), g.bar(b, 2.5), gain_db=-7)
            if b >= drop:
                for e in range(8):
                    if e % 2 == 1:
                        T['bass'].add(bass_pluck(root + 12, dur=g.beat_s * 0.4, vel=0.6), g.bar(b, 0.5 * e),
                                      gain_db=-16)
        elif b == last:
            T['bass'].add(sub_bass(bass_note('A', 1) + 12, dur=g.bar_s * 0.8, vel=0.8), g.bar(b), gain_db=-6)
        # arp: 16ths over the chord tones, from bar 4
        if 4 <= b < last:
            pat = [0, 1, 2, 3, 2, 1, 2, 3]
            for s in range(16):
                nt = ch[pat[s % 8] % len(ch)] + 12
                T['arp'].add(pluck_synth(nt, dur=g.step_s * 0.9, vel=0.55 + 0.25 * (s % 4 == 0), cutoff=850.0),
                             g.bar(b) + g.step(s, 0.08) - g.offset, gain_db=-17, pan=0.3 * (-1) ** s)
        # drums
        if groove0 <= b < last:
            for q in range(4):
                T['kick'].add(soft_kick(vel=0.9 if q % 2 == 0 else 0.82, punch=0.55), g.bar(b, q), gain_db=-3)
            for q in range(4):
                T['perc'].add(hat(vel=0.55 + 0.1 * (q % 2)), g.bar(b, q + 0.5), gain_db=-17, pan=0.25)
            if b % 2 == 1:
                T['perc'].add(hat(vel=0.5, open=True), g.bar(b, 3.5), gain_db=-19, pan=0.25)
            if b >= 4:
                for q in (1, 3):
                    T['perc'].add(clap(vel=0.75, seed=(b % 2) * 4 + q), g.bar(b, q) - 0.03, gain_db=-11)
            T['perc'].mix(shaker_pattern(1, bpm, swing=0.1, vel=0.55, seed=b), t=g.bar(b), gain_db=-19)
        if b == drop - 1:                                  # snare fill + riser into the drop
            for s in range(8, 16):
                T['perc'].add(snare_soft(vel=0.35 + 0.05 * (s - 8)), g.bar(b) + g.step(s, 0.0), gain_db=-15)
            T['fx'].add(riser(g.bar_s, vel=0.7, note=ch[0]), g.bar(b), gain_db=-17)
        if b in (drop, last):
            T['fx'].add(impact_low(vel=0.8), g.bar(b), gain_db=-8)
            if b == last:
                T['kick'].add(soft_kick(vel=0.95, punch=0.6), g.bar(b), gain_db=-3)
        if b == last - 1:
            T['fx'].add(reverse_swell(g.beat_s * 2, vel=0.6, notes=prog[(last) % 4]), g.bar(b, 2), gain_db=-18)
    music = T['pad'].buf + T['keys'].buf + T['gtr'].buf + T['bass'].buf + T['arp'].buf
    music = duck(music, T['kick'], depth_db=5.0, attack=0.004, release=0.17)
    sends = (reverb_send(T['pad'].buf + T['keys'].buf, 'hall', wet_db=-13)
             + reverb_send(T['arp'].buf + T['gtr'].buf + T['perc'].buf, 'plate', wet_db=-15))
    mix = music + T['kick'].buf + T['perc'].buf + T['fx'].buf + sends
    mix = A.hp(mix, 28.0, 2)
    mix = bus_comp(mix, thresh_db=-16.0, ratio=1.8, attack=0.012, release=0.2)
    mix = tilt_eq(mix, 1.0)
    mix = fade_out(mix, 0.6)
    mix = normalise_peak(mix, -1.0, true_peak=False)
    info = dict(bpm=bpm, bars=bars, dur=dur, drop_bar=drop, render_s=round(time.time() - t0, 2))
    if verbose:
        print('demo_arrangement: %d bars at %.1f BPM = %.2f s rendered in %.1f s' % (bars, bpm, dur, info['render_s']))
    return mix, info


# ============================================================================================ self-test
def _two_bars(name, bpm=120.0):
    """2 bars (+ 2 s tail) of one instrument at bpm, as a stereo array."""
    g = Grid(bpm)
    tr = Track(2 * g.bar_s + 2.0)
    am, f_ = chord('Am7', octave=3), chord('Fmaj7', octave=3)
    if name.startswith('karplus_'):
        kind = name.split('_')[1]
        shapes = [chord('Am', octave=3), chord('F', octave=3)] if kind != 'uke' else [chord('Am', octave=4),
                                                                                       chord('F', octave=4)]
        for b in range(2):
            for bt, dirn, v in ((0, 'down', 0.75), (1.5, 'up', 0.55), (2, 'down', 0.7), (3, 'up', 0.55)):
                tr.add(strum(shapes[b], dur=g.beat_s * 1.2, vel=v, direction=dirn, kind=kind, seed=b * 10 + bt),
                       g.bar(b, bt))
    elif name == 'fm_epiano':
        for b, ch in enumerate((am, f_)):
            for bt in (0, 1.5, 2.5):
                for nt in ch:
                    tr.add(fm_epiano(nt + 12, dur=g.beat_s * 0.9, vel=0.7), g.bar(b, bt), gain_db=-6)
    elif name == 'felt_piano':
        for b, ch in enumerate((am, f_)):
            for k in range(8):
                tr.add(felt_piano(ch[k % 4] + 12, dur=g.beat_s * 0.45, vel=0.6, pedal=k == 0, tail=2.0),
                       g.bar(b, 0.5 * k))
            tr.add(felt_piano(ch[0], dur=g.bar_s, vel=0.55, pedal=True, tail=2.0), g.bar(b), gain_db=-3)
    elif name in ('marimba', 'glockenspiel', 'bell'):
        fn = dict(marimba=marimba, glockenspiel=glockenspiel, bell=bell)[name]
        sc = scale('A', 'minor', 4 if name == 'marimba' else (6 if name == 'glockenspiel' else 5))
        stepb = 0.5 if name != 'bell' else 2.0
        k = 0
        tb = 0.0
        while tb < 8 - 1e-9:
            tr.add(fn(sc[[0, 2, 4, 7, 4, 2, 1, 3][k % 8]], vel=0.7), g.beat(tb), gain_db=-6 if name != 'bell' else 0)
            k += 1
            tb += stepb
    elif name == 'pad':
        tr.add(pad(am + [am[0] + 12], dur=g.bar_s, vel=0.7, sweep=0.6, sweep_rate=0.3), 0.0)
        tr.add(pad(voice_lead(am, f_), dur=g.bar_s, vel=0.7, open_to=3000.0), g.bar(1))
    elif name == 'pluck_synth':
        for s in range(32):
            ch = am if s < 16 else f_
            tr.add(pluck_synth(ch[s % 4] + 12, dur=g.step_s * 0.9, vel=0.7), g.step(s, 0.08), pan=0.3 * (-1) ** s)
    elif name == 'sub_bass':
        seq = [(45, 0, 1.5, None), (45, 1.5, 1.0, None), (41, 4, 1.5, 45), (43, 6, 1.5, 41)]
        for nt, bt, dl, gl in seq:
            tr.add(sub_bass(nt, dur=g.beat_s * dl, vel=0.8, glide_from=gl), g.beat(bt))
    elif name == 'bass_pluck':
        for e in range(16):
            tr.add(bass_pluck(45 if e < 8 else 41, dur=g.beat_s * 0.4, vel=0.8 - 0.2 * (e % 2)), g.beat(0.5 * e))
    elif name == 'soft_kick':
        for q in range(8):
            tr.add(soft_kick(vel=0.9, punch=0.3 + 0.1 * (q % 4)), g.beat(q))
    elif name == 'clap':
        for q in (1, 3, 5, 7):
            tr.add(clap(vel=0.8, seed=q), g.beat(q))
    elif name == 'shaker':
        tr.add(shaker_pattern(2, bpm, swing=0.15, vel=0.8), 0.0)
    elif name == 'hat':
        for e in range(16):
            tr.add(hat(vel=0.7 if e % 2 else 0.5, open=(e % 8 == 7)), g.beat(0.5 * e))
    elif name == 'brush':
        for q in range(8):
            tr.add(brush(vel=0.6 + 0.2 * (q % 2)), g.beat(q))
    elif name == 'snare_soft':
        for s in range(16):
            tr.add(snare_soft(vel=0.3 + 0.04 * s), g.beat(4 + 0.25 * s))
        tr.add(snare_soft(vel=0.8), g.beat(1))
        tr.add(snare_soft(vel=0.8), g.beat(3))
    elif name == 'reverse_swell':
        tr.add(reverse_swell(g.bar_s, vel=0.8, notes=am), 0.0)
        tr.add(impact_low(vel=0.7), g.bar(1))
    elif name == 'riser':
        tr.add(riser(2 * g.bar_s, vel=0.8, note=57), 0.0)
    elif name == 'impact_low':
        tr.add(impact_low(vel=0.9), 0.0)
        tr.add(impact_low(vel=0.7, tone=45.0, room='plate'), g.bar(1))
    else:
        raise ValueError(name)
    return fade_out(tr.buf, 0.4)


INSTRUMENT_DEMOS = ('karplus_nylon', 'karplus_steel', 'karplus_uke', 'fm_epiano', 'felt_piano', 'marimba',
                    'glockenspiel', 'bell', 'pad', 'pluck_synth', 'sub_bass', 'bass_pluck', 'soft_kick', 'clap',
                    'shaker', 'hat', 'brush', 'snare_soft', 'reverse_swell', 'riser', 'impact_low')


def _fake_vo_sfx(dur, seed=1):
    """Synthetic speech-like VO (formant-filtered pulse/noise bursts in phrases, -16 LUFS) and a sparse SFX
    stem (soft hits / whooshes, -20 LUFS) for testing the delivery chain."""
    rng = np.random.default_rng(seed)
    N = _n(dur)
    vo = np.zeros(N)
    t = 0.6
    while t < dur - 2.0:
        ln = rng.uniform(1.4, 3.2)
        n0, n1 = _n(t), min(N, _n(t + ln))
        tt = np.arange(n1 - n0) / SR
        f0 = 140 + 25 * np.sin(TWO_PI * 0.7 * tt)
        src = osc(f0, n1 - n0, 'saw') + 0.3 * rng.standard_normal(n1 - n0)
        y = sum(A.bp(src, fc * 0.8, fc * 1.25, 2) for fc in (500.0, 1500.0, 2500.0))
        syl = 0.5 + 0.5 * np.sin(TWO_PI * rng.uniform(3.5, 5.0) * tt) ** 2
        vo[n0:n1] += y * syl * _gate(n1 - n0, ln - 0.08, 0.03, 0.08)
        t += ln + rng.uniform(0.35, 1.6)
    vo = A._st(vo)
    vo *= A.undb(-16.0 - A.loudness(vo))
    sfx = Track(dur)
    for tm in np.arange(0.3, dur - 1, 3.7):
        sfx.add(impact_low(vel=0.5, dur=1.2, room='room'), tm, gain_db=-6)
        sfx.add(hat(vel=0.6, open=True), tm + 1.3, gain_db=-8)
    s = sfx.buf * A.undb(-21.0 - A.loudness(sfx.buf))
    gref = A.undb(-14.0 - A.loudness(vo + s))
    return vo * gref, s * gref, (vo + s) * gref


def selftest(out_dir=None):
    """Render 2 bars of every instrument and the 16-bar demo; assert finite / no clipping / |DC| < 1e-3 / click
    detector clean; demo tempo within 0.3 BPM and phase within 15 ms (bias-corrected flux onsets); demo
    normalisable to -16 LUFS; a 50 s arrangement renders in < 60 s; delivery chain (render_bed,
    master_withmusic, write_mp3, make_preview) on synthetic and (if present) real reel stems."""
    out_dir = out_dir or SELFTEST_DIR
    os.makedirs(out_dir, exist_ok=True)
    fails = []
    T0 = time.time()

    def check(cond, msg):
        if not cond:
            fails.append(msg)
        return cond

    print('music_synth selftest -> %s' % out_dir)
    print('%-15s %6s %7s %7s %7s %9s %7s %6s  %s' % ('instrument', 'dur', 'peak', 'TP', 'LUFS', 'dc', 'click', 'sub20',
                                                     'render'))
    cat = []
    for name in INSTRUMENT_DEMOS:
        t1 = time.time()
        x = _two_bars(name)
        rt = time.time() - t1
        q = qa(x)
        ok = check(q['finite'], '%s: non-finite samples' % name)
        if ok:
            check(not q['clip'], '%s: clipping (peak %.2f dBFS)' % (name, q['peak_dbfs']))
            check(max(q['dcrep']['dc']) < 1e-3, '%s: DC %s' % (name, q['dcrep']['dc']))
            check(q['clicks']['clean'], '%s: clicks %s' % (name, q['clicks']['events'][:3]))
            print('%-15s %6.2f %7.2f %7.2f %7.2f %9.6f %7.1f %6.1f  %.2fs' % (
                name, q['dur'], q['peak_dbfs'], q['true_peak'], q['lufs'], max(q['dcrep']['dc']),
                q['clicks']['worst_ratio'], q['dcrep']['sub20_db'], rt))
        A._write_wav(os.path.join(out_dir, 'inst_%s.wav' % name), x, 24)
        cat.append(normalise_lufs(x, -20.0, -3.0)[0])
        cat.append(np.zeros((_n(0.4), 2)))
    A._write_wav(os.path.join(out_dir, 'instruments_catalog.wav'), np.concatenate(cat), 24)
    # ---- demo
    bpm = 120.0
    mix, info = demo_arrangement(bpm, 16)
    q = qa(mix)
    print('demo 16 bars @ %.0f BPM: %.2f s, rendered in %.1f s | peak %.2f dBFS, TP %.2f, %.2f LUFS, DC %s, '
          'clicks worst %.1f, sub20 %.1f dB' % (bpm, info['dur'], info['render_s'], q['peak_dbfs'], q['true_peak'],
                                               q['lufs'], q['dcrep']['dc'], q['clicks']['worst_ratio'],
                                               q['dcrep']['sub20_db']))
    check(q['finite'] and not q['clip'], 'demo: clipping / non-finite')
    check(max(q['dcrep']['dc']) < 1e-3, 'demo: DC %s' % q['dcrep']['dc'])
    check(q['clicks']['clean'], 'demo: clicks %s' % q['clicks']['events'][:3])
    bg = beat_grid_check(mix, bpm)
    print('demo beat grid: tempo %.3f BPM (coarse %.2f), phase %+.1f ms (coarse %+.1f ms; raw beatgrid.py %+.1f ms),'
          ' strength x%.1f, %d beats fitted, FLUX_BIAS %+.1f ms' % (
              bg['tempo'], bg['tempo_coarse'], bg['phase'] * 1e3, bg['phase_coarse'] * 1e3,
              bg['phase_beatgrid'] * 1e3, bg['strength'], bg['n_beats'], FLUX_BIAS * 1e3))
    check(abs(bg['tempo'] - bpm) <= 0.3, 'demo tempo %.3f vs %.1f' % (bg['tempo'], bpm))
    check(abs(bg['tempo_coarse'] - bpm) <= 0.3, 'demo coarse tempo %.3f vs %.1f' % (bg['tempo_coarse'], bpm))
    check(abs(bg['phase']) <= 0.015, 'demo phase %.1f ms' % (bg['phase'] * 1e3))
    check(abs(bg['phase_coarse']) <= 0.015, 'demo coarse phase %.1f ms' % (bg['phase_coarse'] * 1e3))
    y16, inf16 = normalise_lufs(mix, -16.0, -1.0)
    print('demo -> -16 LUFS: %.2f LUFS, %.2f dBTP, gain %+.2f dB, limiter %.2f dB' % (
        inf16['lufs'], inf16['true_peak'], inf16['gain_db'], inf16['limiter_max_gr_db']))
    check(inf16['ok'] and abs(inf16['lufs'] + 16.0) <= 0.1 and inf16['true_peak'] <= -1.0,
          'demo not normalisable to -16 LUFS: %s' % inf16)
    A._write_wav(os.path.join(out_dir, 'demo_16bars.wav'), y16, 24)
    try:
        img = A.spectro_image(y16, 1100, 420, title='music_synth demo: 16 bars @ 120 BPM',
                              sub='%.2f LUFS  %.2f dBTP  tempo %.2f  phase %+.1f ms' % (
                                  inf16['lufs'], inf16['true_peak'], bg['tempo'], bg['phase'] * 1e3))
        img.save(os.path.join(out_dir, 'demo_16bars.png'))
    except Exception as ex:                              # pragma: no cover (PIL / fonts missing)
        print('  (spectrogram skipped: %s)' % ex)
    mp3 = write_mp3(y16, os.path.join(out_dir, 'demo_16bars.mp3'), 'music_synth demo 16 bars')
    print('mp3: %s  %.2f s  %d b/s  %d Hz  title %r' % (mp3['path'], mp3['dur'], mp3['bit_rate'],
                                                         mp3['sample_rate'], mp3['title']))
    check(mp3['bit_rate'] == 320000 and mp3['sample_rate'] == 48000 and mp3['title'] == 'music_synth demo 16 bars',
          'mp3 wrong: %s' % mp3)
    # ---- 50 s performance render (26 bars at 124 BPM = 50.3 s)
    t1 = time.time()
    perf, pinfo = demo_arrangement(124.0, 26, seed=3)
    pt = time.time() - t1
    pq = qa(perf)
    pb = beat_grid_check(perf, 124.0)
    print('perf: 26 bars @ 124 BPM = %.2f s rendered in %.1f s (limit 60 s) | clicks %.1f | tempo %.3f phase %+.1f ms'
          % (pinfo['dur'], pt, pq['clicks']['worst_ratio'], pb['tempo'], pb['phase'] * 1e3))
    check(pt < 60.0, '50 s render took %.1f s' % pt)
    check(pq['clicks']['clean'] and not pq['clip'], 'perf render: clicks / clip')
    check(pb['ok'], 'perf grid %s' % pb)
    # ---- delivery chain on synthetic stems
    dur = pinfo['dur']
    vo, sfx, ref = _fake_vo_sfx(dur)
    bed, m = render_bed(perf, vo, sfx, ref)
    check(m['vo_minus_music_lu'] >= 10.0, 'bed: voice-music %.2f LU' % m['vo_minus_music_lu'])
    check(m['limited_by'] == 'vo' or abs(m['gap_minus_ref_lu'] + 7.0) <= 0.3,
          'bed: gap %.2f LU re ref' % m['gap_minus_ref_lu'])
    y, rep = master_withmusic(vo, sfx, bed)
    check(rep['ok'] and abs(rep['lufs'] + 14.0) <= 0.2 and rep['true_peak'] <= -2.0, 'master: %s' % {
        k: v for k, v in rep.items() if k != 'stems'})
    A._write_wav(os.path.join(out_dir, 'delivery_synthetic_withmusic.wav'), y, 24)
    # ---- real reel stems if present
    for reel in ('reel1',):
        try:
            st = load_reel_stems(reel)
        except (OSError, FileNotFoundError, ValueError) as ex:
            print('real stems %s: skipped (%s)' % (reel, ex))
            continue
        g = Grid(120.0)
        bars = int(math.ceil(st['dur'] / g.bar_s))
        mus, _ = demo_arrangement(120.0, bars, seed=5)
        mus = fade_out(fit(mus, st['n']), 1.5)
        bed, m = render_bed(mus, st['vo'], st['sfx'], st['mix'])
        y, rep = master_withmusic(st['vo'], st['sfx'], bed)
        check(rep['ok'] and m['vo_minus_music_lu'] >= 10.0, '%s delivery: %s %s' % (reel, m, rep['lufs']))
        A._write_wav(os.path.join(out_dir, 'delivery_%s_withmusic.wav' % reel), y, 24)
        mp3 = write_mp3(bed, os.path.join(out_dir, 'delivery_%s_bed.mp3' % reel), '%s music bed (selftest)' % reel)
        check(mp3['bit_rate'] == 320000, 'bed mp3 %s' % mp3)
    # ---- make_preview on a generated 3 s test video
    vid = os.path.join(out_dir, '_test_video.mp4')
    try:
        _ffmpeg(['-f', 'lavfi', '-i', 'color=c=0x223344:s=270x480:r=30:d=3', '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                 vid])
        pv = make_preview(vid, y16[:_n(5.0)], os.path.join(out_dir, 'preview_test.mp4'))
        pr = _probe(pv)
        kinds = sorted(s.get('codec_name') for s in pr.get('streams', []))
        d = float(pr.get('format', {}).get('duration', 0))
        print('preview: %s streams %s dur %.2f s' % (pv, kinds, d))
        check(kinds == ['aac', 'h264'] and abs(d - 3.0) < 0.15, 'preview wrong: %s %.2f' % (kinds, d))
    except RuntimeError as ex:
        check(False, 'make_preview: %s' % ex)
    finally:
        if os.path.exists(vid):
            os.remove(vid)
    print('selftest %s in %.1f s' % ('PASSED' if not fails else 'FAILED', time.time() - T0))
    for f in fails:
        print('  FAIL: %s' % f)
    return not fails


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'selftest'
    if cmd == 'selftest':
        sys.exit(0 if selftest(sys.argv[2] if len(sys.argv) > 2 else None) else 1)
    elif cmd == 'demo':
        bpm_ = float(sys.argv[3]) if len(sys.argv) > 3 else 120.0
        bars_ = int(sys.argv[4]) if len(sys.argv) > 4 else 16
        y_, inf_ = demo_arrangement(bpm_, bars_, verbose=True)
        A._write_wav(sys.argv[2], normalise_lufs(y_, -16.0)[0], 24)
    elif cmd == 'beatgrid':
        print(beat_grid_check(sys.argv[2], float(sys.argv[3])))
    else:
        print(__doc__)
