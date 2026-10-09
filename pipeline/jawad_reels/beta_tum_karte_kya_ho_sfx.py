#!/usr/bin/env python3
"""beta_tum_karte_kya_ho_sfx.py - SFX layer of Reel 4 / C02 "Beta, tum karte kya ho?" (the Mummy-translate renderer).
Owner: sound-designer.

Binding plan: brand_reels/design/reels/beta_tum_karte_kya_ho/BRIEF.md r2 section 6.12 (cue list), 6.2 (frame-exact beat
table), 6.3 (hooks A and B), 6.7 (VO plan), 6.13 / MUSIC.md (key D minor, Sa = D, chords per bar), 6.14 + section 8 item
13 (mix and QA); SLATE 3.4 (sound motif = the message pop `notif_ping` + the typing-dot tick; bed lofi_desi / tabla;
stings tape stop, bubble_pop, one warm chord) and 5.1 (-14 LUFS, TP <= -2 dBTP, VO >= 8 LU over the bed, <= 3 sounds on
one instant, one drop-out at the reveal, nothing busy in 1-4 kHz under words). Word timings: the FINAL Vlad VO
(workspace/jawad_reels/beta_tum_karte_kya_ho/vo/words.json + vo_stem.wav; words_B.json + _vo_B.wav for version B).
Cue sheet + measurements: SOUND.md in the same design folder.

What this module owns (BRIEF section 7: `cues()`, `BED`, `BED_GAIN_DB`, `build` CLI for the A and B cue sets)
    register()        sfx_jawad + epic_sfx sounds into audio.SOUNDS, plus one local sound (idempotent):
                      btk_haptic = the two 165 Hz haptic pulses of epic_sfx.notif_ping(buzz=1) WITHOUT its ping, at the
                      same absolute level, so a phone buzz and its ping can sit on their own picture events (16.8 / 17.2,
                      18.2 / 18.6) and the ping alone is ducked when it lands on a word.
    events()          the picture events (BRIEF 6.2 frames), overridden key by key by `beta_tum_karte_kya_ho.SFX_EVENTS`
                      when the reel module exists and defines it (lazy import), so a picture retime moves the sound.
    raw_cues(v)       BRIEF 6.12 for version 'A' (public hook) or 'B' (Trial hook: hook-B cues 0-2.8 s + every A cue
                      with t >= 2.8), with the key tuning of MUSIC.md (TUNE) applied, before the VO fit.
    cues(v='A')       raw_cues -> sfx_jawad.fit_under_vo against the final words + VO audio (hero test, duck, carve) +
                      this reel's two corrections (BAND_FIX: tabla_hit is a MID sound, not AIR; BUSY: typing under a
                      word gets lp 1100) + the body carve (an AIR texture whose body runs under a word gets hp 5500);
                      then checks names, <= 3 starts per instant, the drop-out and the hero clearances.
    mix_loop(...)     audio.mix's chain (duck_under -> per-cue render with seed variation -> 'studio' room send -> glue
                      2:1 at target + 8 -> bed sidechained 5 dB under the SFX and anchored at target + BED_GAIN_DB + 8 ->
                      SFX bus gain + 4x true-peak limiter, solved to -18 LUFS / <= -2.0 dBTP) with what this reel needs:
                      (1) the DROP-OUT 27.3-28.0 (bar 9 beat 3 -> bar 10, 1 beat): every cue that hits before 27.3 is
                      cut with its room send at 27.296-27.300 (the music's 4 ms gate edge) and the street bed is out;
                      only room tone and the 27.3 held-breath tick remain until the payoff stack;
                      (2) the LOOP: tails past DUR fold onto t = 0, no tail fade, both beds are seamless loops exactly
                      DUR long, and the glue, sidechain and limiter run on circularly padded signals, so the last
                      sample runs into the first (the card's reverse swell ends on 36.400 and frame 0's impact_soft
                      releases it).
                      Version B is mixed with A's gains (fixed=), so its body equals A's to the sample once the hook-B
                      tails have died (verified in build()).
    build()           SFX stems A + B -> <RW>/audio/beta_tum_karte_kya_ho_sfx_stem.wav (A),
                      ..._hookb_sfx_stem.wav (B) (+ _fx / _bed splits), _cues_{A,B}.json, _sfx_report.json,
                      _sfx_overview_{A,B}.png; -18 LUFS (A), TP <= -2.0 dBTP, 48 kHz 24-bit.
    rough()           rough mixes on the real inputs with the shared epic_mix.mix_reel (VO + this stem + music_full.wav;
                      A and B, each also VO + SFX only) into <RW>/audio/rough/ + every audio measurement of BRIEF 8
                      item 13 -> <RW>/audio/rough/rough_report.json.
    BED, BED_GAIN_DB  BRIEF 6.12 beds (room tone throughout; desi_city street through the window, out in the drop-out),
                      written for audio.mix as well (render.py's fallback build); mix_loop builds them as seamless
                      DUR-long loops.

CLI (run in pipeline/jawad_reels; heavy runs through tools/heavy.sh)
    python3 beta_tum_karte_kya_ho_sfx.py cues [--version A|B]   cue table after the VO fit (light)
    tools/heavy.sh python3 beta_tum_karte_kya_ho_sfx.py build    A + B SFX stems (+ json, overview png)
    tools/heavy.sh python3 beta_tum_karte_kya_ho_sfx.py rough    rough mixes + measurements
    tools/heavy.sh python3 beta_tum_karte_kya_ho_sfx.py all      build + rough
    python3 beta_tum_karte_kya_ho_sfx.py table                   markdown cue table (SOUND.md)

Hand-off: the reel module adopts `from beta_tum_karte_kya_ho_sfx import cues, BED, BED_GAIN_DB` (its cues() then
returns version A). Renders keep this mix with `--no-sfx-build --audio <full mix wav>` (the music-supervisor's run-2 mix
of this stem; the rough mix in <RW>/audio/rough/ is a stand-in until then).
"""
import argparse
import json
import math
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
SFXDIR = os.path.join(REPO, 'workspace', 'brand_reels', 'sfx')
for _p in (SFXDIR, HERE):                      # HERE ends up first: `audio` is this project's toolkit copy
    if _p in sys.path:
        sys.path.remove(_p)
    sys.path.insert(0, _p)

import audio as A  # noqa: E402
from audio import SR, _n, undb  # noqa: E402

MODULE = 'beta_tum_karte_kya_ho'
DUR, BPM, FPS = 36.4, 600.0 / 7.0, 30
BEAT, BAR = 0.7, 2.8                           # 21 / 84 frames
N = _n(DUR)
assert N == 1747200 and abs(60.0 / BPM - BEAT) < 1e-12
RW = os.path.join(REPO, 'workspace', 'jawad_reels', MODULE)
AUD = os.path.join(RW, 'audio')
ROUGH = os.path.join(AUD, 'rough')
VODIR = os.path.join(RW, 'vo')
VO = dict(A=(os.path.join(VODIR, 'vo_stem.wav'), os.path.join(VODIR, 'words.json')),          # vo_stem = _vo_A.wav
          B=(os.path.join(VODIR, MODULE + '_vo_B.wav'), os.path.join(VODIR, 'words_B.json')))
MUSIC = os.path.join(RW, 'music', 'music_full.wav')
STEM = dict(A=os.path.join(AUD, MODULE + '_sfx_stem.wav'), B=os.path.join(AUD, MODULE + '_hookb_sfx_stem.wav'))
SPLICE = 2.8                                   # f84: hook B frames 0-83, A and B identical from here

TARGET_LUFS, TP_CEILING = -18.0, -2.0
DROP = (27.3, 28.0)                            # the one drop-out: bar 9 beat 3 -> payoff (1 beat), BRIEF 6.2 f819-f839
GATE_FADE = 0.004                              # 27.296-27.300, the music's gate edge
WRAP_TAIL = 4.0                                # s rendered past DUR, folded back onto t = 0
CIRC_PAD = 2.0                                 # s of circular padding for glue / sidechain / limiter ballistics
TOL = 1.0 / FPS                                # one frame
BED_ANCHOR_DB = A.BED_ANCHOR_DB                # audio.mix: bed integrated = target + BED_GAIN_DB + 8

# BRIEF 6.12 beds. room_tone carries the two music silences (12.6-14.0, 27.3-28.0); desi_city = the street outside the
# window, out for the drop-out (0.3 s fade into 27.3, 4 ms re-entry on the payoff). params dur=DUR makes both seamless
# DUR-long loops and offset=t0 keeps the street continuous across the gap, so the loop seam 36.4 -> 0 is continuous.
BED = [dict(name='room_tone', t0=0.0, t1=DUR, gain_db=0.0, fade=0.3, params=dict(dur=DUR)),
       dict(name='desi_city', t0=0.0, t1=DROP[0], gain_db=-8.0, fade=0.3, params=dict(dur=DUR)),
       dict(name='desi_city', t0=DROP[1], t1=DUR, gain_db=-8.0, fade=0.004, params=dict(dur=DUR), offset=DROP[1])]
BED_GAIN_DB = -32.0


def F(f):
    """Reel time of frame f (30 fps)."""
    return round(f / FPS, 4)


# ================================================================================================ picture events
# BRIEF r2 section 6.2 / 6.3 (frame-exact, 30 fps; beat = 0.7 s = 21 f, bar = 2.8 s = 84 f).
EV = dict(
    f0=0.0,                      # S0 hook: JD confused + "Mummy" typing pill (dots pulsing); loop landing
    msg=F(11),                   # 0.3667 first 8th: the message lands, H1 legible (motif: notif_ping A6)
    card=3.1,                    # f93 translate card lands after the c1 cut (2.8, splice)
    type1=F(98),                 # 3.2667 "Video editor" types (f98-f116, 12 chars, 0.6 s)
    shaadi=F(126),               # 4.2 beat 1.2: output "Shaadi wala?" pops
    m6=F(147),                   # 4.9 beat 7: M6 carry-over cut (the word rides into the window; fastest point)
    spark=F(159),                # 5.3 the spark landing: sparkle burst, "Happy Wedding" wipes in
    type2=F(190),                # 6.3333 "Motion designer" types (f190-f205, 15 chars, 0.5 s)
    cartoon=F(210),              # 7.0 beat 2.2: "Cartoon?" pill POPs + MOTION rubber-hose wobble (boing 1)
    boing2=F(221),               # 7.3667 boing 2
    whip=F(230),                 # 7.6667 c3 - 1 f: the punch-in's whip
    c3=F(231),                   # 7.7 beat 2.3: c3 cut -> suit_shocked punch-in
    stamp=F(252),                # 8.4 bar 3: c4 cut, card returns, stamp SLAM
    m3=F(336),                   # 11.2 bar 4: M3 momentum swipe (re-hook 1), card swipes left
    m3_land=F(345),              # 11.5 card B lands
    loading=F(364),              # 12.1333 loading dots
    killer=F(378),               # 12.6 beat 4.2: KILLER bubble "Achha. Naukri kab lagegi?" (music silent)
    fold=F(410),                 # 13.6667 card folds away
    c6=F(420),                   # 14.0 bar 5: c6 cut -> suit_neutral
    killer_exit=F(450),          # 15.0 killer bubble exits (f450-f458)
    buzz1=F(504),                # 16.8 bar 6: c7 time skip, chip POPs, buzz 1 (haptic + 6 px creeps at 16.8 / 17.0)
    ping1=F(516),                # 17.2 buzz 1's ping: edge-glow pulse
    buzz2=F(546),                # 18.2 beat 6.2: count pill "Khandaan . 12", buzz 2 (creeps 18.2 / 18.4)
    ping2=F(558),                # 18.6 buzz 2's ping: edge-glow pulse
    roll47=F(567),               # 18.9 ping: count 12 -> 47
    roll99=F(578),               # 19.2667 ping: 47 -> 99
    plus=F(583),                 # 19.4333 ping: "+" -> 99+
    m2=F(588),                   # 19.6 bar 7: M2 hue bridge, "Khandaan" floods (re-hook 2)
    fwd=F(651),                  # 21.7 forwarded reel bubble lands
    kamaal=F(672),               # 22.4 "Kamaal!"
    wah=F(693),                  # 23.1 "Wah!"
    typing_pill=F(756),          # 25.2 bar 9: "Mummy is typing" pill
    resume=F(798),               # 26.6 typing resumes
    drop=F(819),                 # 27.3 drop-out (music gated 1 beat): the held breath
    payoff=F(840),               # 28.0 bar 10: PAYOFF (M1 typing dot -> sun), bubble + lockup P1 build
    cinema=F(847),               # 28.2333 *cinema* starts rising
    c10=F(861),                  # 28.7 c10 cut -> suit_hand_on_chest punch-in
    lockup_exit=F(955),          # 31.8333 payoff lockup + bubble exit (f955-f965)
    card_t0=F(966),              # 32.2 bar 11 beat 2: c11 cut, EndCard t0
    nani=F(1050),                # 35.0 beat 12.2: "Nani" chip + typing pill POP over the end card
    dots1=F(1074),               # 35.8 dots
    dots2=F(1083),               # 36.1 dots
    end=DUR,                     # 36.4 = frame 0 of the loop
)
# Hook B (Trial; BRIEF 6.3 table B)
EV_B = dict(
    b_f0=0.0,                    # card + H2 lockup from f0, MOTION mid-wobble
    b_boing2=F(21),              # 0.7 boing 2 (JELLY re-trigger)
    b_droop=F(42),               # 1.4 MOTION letters droop and squash
    b_flare=F(63),               # 2.1 *cartoon?* halo flare
    b_cut=F(74),                 # 2.4667 hard cut to A's frame 74 (JD + Mummy bubble)
)
# endcard.EndCard('GROUP MEIN', 'bhejo', monogram='JD', dur=4.2).cues(32.2, 36.4), reproduced (checked in verify())
CARD_T_TITLE = 0.35                            # EndCard.t_title with a monogram


def events():
    """EV + EV_B, overridden by the reel module's SFX_EVENTS (only keys that exist; times in seconds)."""
    ev = dict(EV, **EV_B)
    try:
        import importlib
        M = importlib.import_module(MODULE)
    except Exception:            # the module does not exist yet (timeline on placeholders) or fails to import
        return ev
    if abs(float(getattr(M, 'DUR', DUR)) - DUR) > 1e-9:
        raise ValueError('%s.DUR = %s, this sfx module is built for %s' % (MODULE, M.DUR, DUR))
    for k, v in dict(getattr(M, 'SFX_EVENTS', {}) or {}).items():
        if k not in ev:
            raise KeyError('SFX_EVENTS key %r is unknown; known: %s' % (k, ', '.join(ev)))
        ev[k] = float(v)
    return ev


# ================================================================================================ sounds
def btk_haptic(seed=0, pitch=1.1225):
    """The two haptic pulses of epic_sfx.notif_ping(buzz=1) (165 Hz, 0.13 s each, 0.2 s apart, plate) WITHOUT the
    ping that follows at 0.40 s: the same rendered samples cut at 0.385 s with a 40 ms raised-cosine fade
    (0.345-0.385; the ping's flick, bell and shimmer all start at 0.400 and the plate is causal, so nothing of the
    ping is in here). Absolute level kept (no re-normalisation): gain_db=-10 gives exactly the haptic of the
    brief's `notif_ping buzz=1` cue at -10. hit = 0.002 s (first pulse onset)."""
    x = np.array(A.sound('notif_ping', seed=seed, pitch=pitch, buzz=1), dtype=np.float64)
    n0, n1 = _n(0.345), _n(0.385)
    y = x[:n1].copy()
    y[n0:] *= (0.5 * (1.0 + np.cos(np.pi * np.arange(n1 - n0) / (n1 - n0))))[:, None]
    return A.Sfx(y, 0.002, 'btk_haptic')


LOCAL = dict(btk_haptic=('ui', 'two 165 Hz haptic vibration pulses 0.2 s apart (notif_ping buzz=1 without its ping)',
                         'a phone buzzing on a wooden table (C02 time skip 16.8 / 18.2)'))


def register():
    """sfx_jawad + epic_sfx + the local sounds into audio.SOUNDS (idempotent). Returns sfx_jawad."""
    import sfx_jawad as SJ
    import epic_sfx as E
    SJ.register()
    E.register()
    for n, (cat, ch, use) in LOCAL.items():
        if n not in A.SOUNDS:
            A._register(cat, ch, use)(globals()[n])
    return SJ


# ================================================================================================ key tuning
# MUSIC.md section 2/3: D minor, Sa = D4; bar chords: 0 Dm9 | 1 Bbmaj7 | 2 Gm9 | 3 A7b9 | 4 Dm9 | 5 Bbmaj7 |
# 6 Gm9 (16.8-18.2) + A7b9 (18.2-19.6) | 7 Dm9 | 8 Bbmaj7 | 9 Gm9 | 10 D add9 | 11 Bbmaj7 | 12 A7b9.
NOTE = dict(BB5=932.33, D6=1174.66, F6=1396.91, G6=1567.98, A5=880.0, A6=1760.0, CS7=2217.46, D7=2349.32)
PING_HZ = 1567.98                              # notif_ping pitch 1.0 = G6 (epic_sfx: f = 1567.98 * pitch; measured)


def f0_of(name, **p):
    """Dominant partial above 150 Hz (bible 4.2 method: mono, Hann window, whole buffer)."""
    x = np.asarray(A.sound(name, **p), float).mean(1)
    X = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    f = np.fft.rfftfreq(len(x), 1.0 / SR)
    return float(f[np.argmax(X * (f > 150))])


def ridge_hz(name, span=0.15, **p):
    """Pitch of a CHIRP: energy-weighted geometric mean of the STFT ridge (512-sample Hann frames, 2.5 ms hop,
    8192-point FFT, ridge above 300 Hz) over the first `span` s. Used for bubble_pop, whose f0_of jumps between
    its room-reverb modes (1379 / 1504 / 2079 Hz) as `pitch` moves, while this ridge is linear in pitch
    (~1212 Hz x pitch at seed 0)."""
    x = np.asarray(A.sound(name, **p), float).mean(1)
    n, hop, nf = 512, 120, 8192
    win = np.hanning(n)
    f = np.fft.rfftfreq(nf, 1.0 / SR)
    fr, en = [], []
    for i in range(0, min(len(x), _n(span)) - n, hop):
        X = np.abs(np.fft.rfft(x[i:i + n] * win, nf))
        X[f < 300] = 0
        k = int(np.argmax(X))
        fr.append(f[k])
        en.append(X[k] ** 2)
    fr, en = np.asarray(fr), np.asarray(en)
    return float(math.exp(np.sum(en * np.log(fr)) / np.sum(en)))


def cents(f, ref):
    return 1200.0 * math.log2(f / ref)


def tune_exact(name, target_hz, p0=1.0, seed=0, tol_cents=5.0, est='f0', **params):
    """pitch= multiplier that puts the sound's pitch (est 'f0' = f0_of, the bible 4.2 method; 'ridge' = ridge_hz for
    chirps) on target_hz (exact octave), solved iteratively (trim length and window move with `pitch`)."""
    fn = f0_of if est == 'f0' else ridge_hz
    p = p0
    for _ in range(12):
        f = fn(name, pitch=p, seed=seed, **params)
        if abs(cents(f, target_hz)) <= tol_cents:
            break
        p *= target_hz / f
    return round(p, 4)


_TUNED = {}
TUNE = dict(
    ping_a6=lambda: round(NOTE['A6'] / PING_HZ, 4),        # 1.1225 (the brief's A6)
    ping_cs7=lambda: round(NOTE['CS7'] / PING_HZ, 4),      # 1.4142: bar 6's A7b9 half (MUSIC.md 2: D7 clashes there)
    ping_d7=lambda: round(NOTE['D7'] / PING_HZ, 4),        # 1.4983 (the brief's D7; bar 8 Bbmaj7: D is a chord tone)
    pop_a5=lambda: tune_exact('pop', NOTE['A5'], 0.82),    # BRIEF pitch_to(880): A5 is in bars 1, 6 (Gm9) and 9
    # bubble_pop is a chirp: tuned on its ridge (ridge_hz), seed fixed (the seed moves its pitch by up to 0.6 st).
    # The brief's 1.0 -> 0.8 droop becomes a falling major third on chord tones of bar 2 (Gm9): D6 -> Bb5 (x0.794)
    boing1_d6=lambda: tune_exact('bubble_pop', NOTE['D6'], 0.97, est='ridge'),      # 7.0: Gm9 5th
    boing2_bb5=lambda: tune_exact('bubble_pop', NOTE['BB5'], 0.77, est='ridge'),    # 7.367: Gm9 3rd
    hb_boing1_f6=lambda: tune_exact('bubble_pop', NOTE['F6'], 1.15, est='ridge'),   # hook B 0.0, bar 0 Dm9: 3rd
    hb_boing2_d6=lambda: tune_exact('bubble_pop', NOTE['D6'], 0.97, est='ridge'),   # hook B 0.7, Dm9 root (x0.84)
    tap_d7=lambda: tune_exact('glass_tap', NOTE['D7'], 1.12),         # 32.95, bar 11 Bbmaj7: 3rd
)
TUNE_TARGET = dict(ping_a6='A6', ping_cs7='CS7', ping_d7='D7', pop_a5='A5', boing1_d6='D6', boing2_bb5='BB5',
                   hb_boing1_f6='F6', hb_boing2_d6='D6', tap_d7='D7')
TUNE_EST = dict(boing1_d6='ridge', boing2_bb5='ridge', hb_boing1_f6='ridge', hb_boing2_d6='ridge')


def tune(key):
    if key not in _TUNED:
        _TUNED[key] = TUNE[key]()
    return _TUNED[key]


# ================================================================================================ cue list
def _c(t, name, gain_db, why, ev, **kw):
    d = dict(t=round(float(t), 4), name=name, gain_db=float(gain_db), why=why, ev=ev)
    d.update(kw)
    d.setdefault('params', {})
    return d


def hook_a_cues(ev):
    return [
        _c(ev['f0'], 'impact_soft', -8, 'loop landing: the end card swell ends on 36.4 = f0', 'f0'),
        _c(ev['f0'], 'ui_tick', -12, 'typing dots on the Mummy pill (motif, part 2)', 'f0', hp=5000),
        _c(ev['msg'], 'notif_ping', -4, "Mummy's message lands, H1 legible (motif)", 'msg',
           params=dict(pitch=tune('ping_a6'))),
    ]


def hook_b_cues(ev):
    return [
        _c(ev['b_f0'], 'bubble_pop', -4, 'hook B f0: MOTION mid-wobble (boing, F6)', 'b_f0',
           params=dict(pitch=tune('hb_boing1_f6')), seed=0),
        _c(ev['b_f0'], 'impact_soft', -8, 'hook B f0 weight', 'b_f0'),
        _c(ev['b_boing2'], 'bubble_pop', -8, 'hook B boing 2 (JELLY re-trigger, D6)', 'b_boing2',
           params=dict(pitch=tune('hb_boing2_d6')), seed=0),
        _c(ev['b_droop'], 'swish_small', -10, 'hook B MOTION droops and squashes', 'b_droop'),
        _c(ev['b_flare'], 'tabla_hit', -8, "hook B *cartoon?* halo flare (tabla 'na', Sa = D)", 'b_flare',
           params=dict(stroke='na', pitch=1.0)),
        _c(ev['b_cut'], 'notif_ping', -6, "hook B hard cut to A's f74: Mummy's bubble (A6)", 'b_cut',
           params=dict(pitch=tune('ping_a6'))),
    ]


def body_cues(ev):
    a6, cs7, d7, a5 = tune('ping_a6'), tune('ping_cs7'), tune('ping_d7'), tune('pop_a5')
    t0 = ev['card_t0']
    return [
        # ---- S1-S2 translate card, gag 1 (Shaadi wala?) ---------------------------------------------------------
        _c(ev['card'], 'card_slide', -6, 'translate card lands (slide from the c1 cut)', 'card', params=dict(dur=0.42)),
        _c(ev['type1'], 'typing', -14, 'input "Video editor" types (f98-f116)', 'type1', params=dict(n=12, cps=20)),
        _c(ev['shaadi'], 'pop', -4, 'output "Shaadi wala?" pops (A5)', 'shaadi', params=dict(pitch=a5), seed=0),
        _c(ev['m6'], 'whoosh_by', -6, 'M6 carry-over: the word flies into the window (fastest point)', 'm6',
           params=dict(dur=0.8, direction=1), pan=0.1, hero=True),
        _c(ev['m6'], 'shimmer', -8, 'wedding parody: sparkle wipe', 'm6', params=dict(dur=1.2)),
        _c(ev['spark'], 'sparkle', -8, 'M6 spark lands, "Happy Wedding" wipes in', 'spark'),
        # ---- S2-S3 gag 2 (Cartoon?) + punch-in ----------------------------------------------------------------------
        _c(ev['type2'], 'typing', -16, 'input "Motion designer" types (f190-f205)', 'type2', params=dict(n=15, cps=30)),
        _c(ev['cartoon'], 'bubble_pop', -2, '"Cartoon?" pill POPs + MOTION wobble, boing 1 (D6)', 'cartoon',
           params=dict(pitch=tune('boing1_d6')), seed=0),
        _c(ev['boing2'], 'bubble_pop', -6, 'boing 2 (Bb5, the droop)', 'boing2',
           params=dict(pitch=tune('boing2_bb5')), seed=0),
        _c(ev['whip'], 'whip', -6, 'punch-in whip (c3 - 1 f)', 'whip', params=dict(direction=1)),
        _c(ev['c3'], 'impact_soft', -5, 'c3 punch-in to suit_shocked', 'c3', hero=True),
        _c(ev['c3'], 'tabla_hit', -4, "comic bass bend (tabla 'ge'; the bed's theka rests here)", 'c3',
           params=dict(stroke='ge', pitch=1.0)),
        # ---- S4 gag 3 (stamp) -------------------------------------------------------------------------------------
        _c(ev['stamp'], 'impact_soft', -4, 'stamp SLAM on the bar-3 downbeat', 'stamp', hero=True),
        _c(ev['stamp'], 'tabla_hit', -6, "stamp: dry slap (tabla 'ta')", 'stamp', params=dict(stroke='ta', pitch=1.0)),
        _c(ev['stamp'], 'swish_small', -10, 'card returns (c4)', 'stamp'),
        # ---- S5 re-hook 1, the killer --------------------------------------------------------------------------------
        _c(ev['m3'], 'whoosh_fast', -3, 'M3 momentum swipe left (re-hook 1; under "Seedha jawab" by design)', 'm3',
           params=dict(direction=-1), pan=-0.4),
        _c(ev['m3_land'], 'card_slide', -8, 'card B lands pre-filled', 'm3_land', params=dict(dur=0.3)),
        _c(ev['loading'], 'ui_tick', -14, 'loading dots', 'loading'),
        _c(ev['killer'], 'notif_ping', 0, 'KILLER bubble "Achha. Naukri kab lagegi?" (music silent; A6)', 'killer',
           params=dict(pitch=a6), hero=True),
        _c(ev['killer'], 'impact_soft', -8, 'killer weight', 'killer'),
        _c(ev['fold'], 'swish_small', -8, 'card folds away', 'fold'),
        _c(ev['c6'], 'impact_soft', -10, 'c6 cut to suit_neutral', 'c6'),
        _c(ev['killer_exit'], 'swish_small', -14, 'killer bubble exits', 'killer_exit'),
        # ---- S7 time skip: the phone on the table --------------------------------------------------------------------
        _c(ev['buzz1'], 'btk_haptic', -4, 'buzz 1: haptic pulses = the 6 px creeps at 16.8 / 17.0', 'buzz1'),
        _c(ev['buzz1'], 'pop', -10, 'chip "Kuch mahine baad" POPs (A5)', 'buzz1', params=dict(pitch=a5), seed=0),
        _c(ev['ping1'], 'notif_ping', -10, "buzz 1's ping: edge-glow pulse (A6)", 'ping1', params=dict(pitch=a6)),
        _c(ev['buzz2'], 'btk_haptic', -4, 'buzz 2: count pill rises, creeps at 18.2 / 18.4', 'buzz2'),
        _c(ev['ping2'], 'notif_ping', -10, "buzz 2's ping: edge-glow pulse (A6)", 'ping2', params=dict(pitch=a6)),
        _c(ev['roll47'], 'notif_ping', -12, 'ping: count 12 -> 47 (C#7, over A7b9)', 'roll47', params=dict(pitch=cs7)),
        _c(ev['roll99'], 'notif_ping', -12, 'ping: count 47 -> 99 (A6)', 'roll99', params=dict(pitch=a6)),
        _c(ev['plus'], 'notif_ping', -12, 'ping: "+" -> 99+ (C#7, the leading tone into D)', 'plus',
           params=dict(pitch=cs7)),
        # ---- S8 re-hook 2: the family group floods ---------------------------------------------------------------------
        _c(ev['m2'], 'reverse_swell', -6, 'M2: the suck into the hue bridge (ENDS on the cut)', 'm2',
           params=dict(duration=0.3)),
        _c(ev['m2'], 'shimmer', -10, 'M2 hue bridge into the gold group scene', 'm2', params=dict(dur=1.0)),
        _c(ev['m2'], 'whoosh_fast', -8, '"Khandaan" floods (scroll)', 'm2', params=dict(direction=1), hero=True),
        _c(ev['fwd'], 'notif_ping', -6, 'the forwarded reel bubble lands (A6)', 'fwd', params=dict(pitch=a6)),
        _c(ev['kamaal'], 'notif_ping', -8, '"Kamaal!" (D7 over Bbmaj7)', 'kamaal', params=dict(pitch=d7)),
        _c(ev['wah'], 'notif_ping', -8, '"Wah!" (A6)', 'wah', params=dict(pitch=a6)),
        _c(ev['typing_pill'], 'pop', -10, '"Mummy is typing" pill (A5)', 'typing_pill', params=dict(pitch=a5), seed=0),
        _c(ev['typing_pill'], 'ui_tick', -14, 'typing dots', 'typing_pill'),
        _c(ev['resume'], 'ui_tick', -14, 'typing resumes', 'resume'),
        _c(ev['drop'], 'ui_tick', -16, 'held breath: the only start in the drop-out (27.3-28.0)', 'drop'),
        # ---- S9-S10 payoff ---------------------------------------------------------------------------------------------
        _c(ev['payoff'], 'tabla_hit', 0, "PAYOFF: M1 tonal hit (tabla 'dha' on Sa = D over D add9)", 'payoff',
           params=dict(stroke='dha', pitch=1.0), hero=True),
        _c(ev['payoff'], 'sub_drop', -6, 'payoff sub (the bed has no kick / 808 here)', 'payoff',
           params=dict(dur=1.6), lp=120),
        _c(ev['payoff'], 'impact_soft', -3, 'payoff body', 'payoff', hero=True),
        _c(ev['cinema'], 'shimmer', -8, '*cinema* starts rising', 'cinema', params=dict(dur=1.5)),
        _c(ev['c10'], 'swish_small', -12, 'c10 punch-in to hand_on_chest', 'c10'),
        _c(ev['lockup_exit'], 'swish_small', -12, 'payoff lockup + bubble exit', 'lockup_exit'),
        # ---- S11 end card (endcard.EndCard.cues(32.2, 36.4); glass_tap tuned) -----------------------------------------
        _c(t0 + 0.1, 'swish_small', -12, 'end card: monogram ring draws on (align start)', 'card_t0', align='start'),
        _c(t0 + CARD_T_TITLE + 0.22, 'shimmer', -10, 'end card: keyword *bhejo* rises', 'card_t0'),
        _c(t0 + 0.75, 'glass_tap', -12, 'end card: ring closes (D7 over Bbmaj7)', 'card_t0',
           params=dict(pitch=tune('tap_d7')), seed=0),
        # ---- S11-S12 Nani + the loop -------------------------------------------------------------------------------
        _c(ev['nani'], 'notif_ping', -8, "Nani's chip + typing pill: Mummy's message sound (A6)", 'nani',
           params=dict(pitch=a6)),
        _c(ev['dots1'], 'ui_tick', -15, 'Nani typing dots', 'dots1'),
        _c(ev['dots2'], 'ui_tick', -15, 'Nani typing dots', 'dots2'),
        _c(ev['end'], 'reverse_swell', -8, 'loop swell, ENDS on 36.4 = frame 0 (endcard.cues)', 'end',
           params=dict(duration=0.8)),
    ]


def _seed(cs):
    """Fixed variation seeds (0-3 per repeat of a name + params, as audio.mix's vary) counted within one cue group,
    so the body cues carry the same seeds in versions A and B and B's body equals A's to the sample."""
    counts = {}
    for c in sorted(cs, key=lambda c: c['t']):
        k = (c['name'], A._key(c['params']))
        counts[k] = counts.get(k, -1) + 1
        c.setdefault('seed', counts[k] % 4)
    return cs


def raw_cues(version='A', ev=None):
    """The brief's cue list for version 'A' or 'B', before the VO fit."""
    ev = ev or events()
    body = _seed(body_cues(ev))
    if version == 'A':
        return _seed(hook_a_cues(ev)) + body
    if version == 'B':
        return _seed(hook_b_cues(ev)) + [c for c in body if c['t'] >= SPLICE]
    raise ValueError("version must be 'A' or 'B'")


# ================================================================================================ VO fit
BAND_FIX = dict(tabla_hit='mid', btk_haptic='dark')   # sfx_jawad.band_of maps epic_sfx 'texture' -> AIR (hp 5500 would
#                                                     # delete a tabla stroke) and 'ui' -> MID; these are the real bands
BUSY = {'typing'}                                    # key clicks are busy 1-4 kHz: lp 1100 whenever they run under a word
AIR_HP, DARK_LP, DEPTH_DB, MID_EXTRA_DB = 5500.0, 1100.0, -6.0, -2.0
BODY_DB = 20.0                                       # a cue's body = from its hit until it is 20 dB under its own peak
BODY_MIN = 0.10                                      # s of body under speech before the body carve applies
HERO_EXCEPT = {('impact_soft', 28.0): 0.245}         # BRIEF 6.7: payoff hit 28.0 -> VO 28.25 = 250 ms (both locked)
HERO_PRE, HERO_POST, HERO_POST_SMALL = 0.12, 0.30, 0.15


def check_names(cs):
    bad = [c['name'] for c in cs if c['name'] not in A.SOUNDS and c['name'] not in A.ALIASES]
    if bad:
        raise KeyError('unknown sound names (no fuzzy fallback allowed): %s' % bad)


def _render(c):
    """The rendered sound of a cue (params only; seed 0 unless the cue fixes one) and its hit offset."""
    p = dict(c['params'])
    if 'seed' in c:
        p['seed'] = c['seed']
    x = A.sound(c['name'], **p)
    return x, x.hit


def body_len(c):
    """Seconds from the hit until the sound's 10 ms RMS is BODY_DB under its own peak."""
    from scipy.ndimage import uniform_filter1d
    x, hit = _render(c)
    m = np.square(np.asarray(x, float)).mean(1)
    env = 10 * np.log10(uniform_filter1d(m, _n(0.01)) + 1e-20)
    above = np.nonzero(env > env.max() - BODY_DB)[0]
    return max(0.0, above[-1] / SR - hit) if len(above) else 0.0


def hit_time(c):
    x, hit = _render(c)
    return float(c['t']) + (0.0 if c.get('align', 'hit') == 'hit' else hit)


def start_time(c):
    x, hit = _render(c)
    return float(c['t']) - (hit if c.get('align', 'hit') == 'hit' else 0.0)


def _overlap(a, b, wins):
    return sum(max(0.0, min(b, w1) - max(a, w0)) for w0, w1 in wins)


def fit(cs, version='A'):
    """sfx_jawad.fit_under_vo (hero test on words + VO audio, duck + carve) + BAND_FIX + BUSY + the body carve.
    Returns (cues, report)."""
    SJ = register()
    vo, words = VO[version]
    pre = []
    for c in cs:
        c = dict(c)
        if c['name'] in BAND_FIX:                    # sentinels: fit_under_vo's setdefault('hp'/'lp') leaves them
            c.setdefault('hp', 0)
            c.setdefault('lp', 0)
        pre.append(c)
    out, rep = SJ.fit_under_vo(pre, words, depth_db=DEPTH_DB, hero='warn', vo_audio=vo, report=True,
                               hero_pre=HERO_PRE, hero_post=HERO_POST, hero_post_small=HERO_POST_SMALL)
    assert len(out) == len(pre)
    wins = SJ.vo_windows(words)                       # the ducking windows (words padded 60 ms)
    rep['band_fix'], rep['busy'], rep['body_carve'] = [], [], []
    res = []
    for c0, c in zip(pre, out):
        c = dict(c)
        if c0['name'] in BAND_FIX:
            band = BAND_FIX[c0['name']]
            for k in ('hp', 'lp'):                    # drop the sentinels again
                if c.get(k) == 0 and c0.get(k) == 0:
                    c.pop(k)
            if 'vo' in c:                             # it was ducked: redo it with the real band
                g = DEPTH_DB + (MID_EXTRA_DB if band == 'mid' else 0.0)
                c['gain_db'] = float(c0['gain_db']) + g
                if band == 'dark':
                    c['lp'] = DARK_LP
                c['vo'] = '%+.1f dB%s (band %s)' % (g, ', lp %d' % DARK_LP if band == 'dark' else '', band)
                rep['band_fix'].append(dict(name=c['name'], t=c['t'], note=c['vo']))
        if c.get('hero'):
            res.append(c)
            continue
        hit = hit_time(c)
        st = start_time(c)
        if c['name'] in BUSY:
            body_end = hit + body_len(c)
            if _overlap(st, body_end, wins) > 0.0:
                c.setdefault('lp', DARK_LP)
                c['vo'] = (c.get('vo', '') + '; ' if c.get('vo') else '') + 'busy under a word: lp %d' % c['lp']
                rep['busy'].append(dict(name=c['name'], t=c['t'], note=c['vo']))
        elif 'vo' not in c and SJ.band_of(c['name'], c) == 'air' and c['name'] not in BAND_FIX:
            ov = _overlap(hit, hit + body_len(c), wins)
            if ov > BODY_MIN:
                c.setdefault('hp', AIR_HP)
                c['vo'] = 'body under speech %.2f s: hp %d' % (ov, c['hp'])
                rep['body_carve'].append(dict(name=c['name'], t=c['t'], note=c['vo']))
        res.append(c)
    # hero clearances: the bible default everywhere, the brief's one stated exception at the payoff
    rep['hero_ok'] = list(rep['heroes_ok'])
    bad = []
    hwins = rep['hero_windows']
    for v in rep['violations']:
        key = (v['name'], round(v['hit'], 2))
        need = HERO_EXCEPT.get(key)
        nxt = min([a for a, b in hwins if a >= v['hit']], default=None)
        prev = max([b for a, b in hwins if b <= v['hit']], default=None)
        clear_after = None if nxt is None else round(nxt - v['hit'], 3)
        clear_before = None if prev is None else round(v['hit'] - prev, 3)
        v.update(clear_before=clear_before, clear_after=clear_after)
        if need is not None and clear_after is not None and clear_after >= need and (clear_before is None or
                                                                                      clear_before >= HERO_PRE):
            v['accepted'] = 'BRIEF 6.7: %.3f s clear before the next word (>= %.3f)' % (clear_after, need)
            rep['hero_ok'].append(dict(name=v['name'], hit=v['hit'], note=v['accepted']))
        else:
            bad.append(v)
    if bad:
        raise SJ.HeroOnWordError('hero cue on a word: %s' % bad)
    return res, rep


def instants(cs, tol=TOL):
    """Max number of sounds STARTING on one instant (event = hit; risers / swells that END there do not count)."""
    SJ = register()
    ev = sorted(hit_time(c) for c in cs if SJ.band_of(c['name']) != 'span')
    worst, at = 0, None
    for i, e in enumerate(ev):
        k = sum(1 for f in ev[i:] if f - e <= tol + 1e-9)
        if k > worst:
            worst, at = k, e
    return worst, at


def check(cs, version):
    """Names, <= 3 starts per instant, the drop-out (no start in 27.305-27.995), no cue before 0 or after DUR."""
    check_names(cs)
    worst, at = instants(cs)
    if worst > 3:
        raise ValueError('%d sounds start within one frame of %.3f s (max 3)' % (worst, at))
    inside = [(c['name'], c['t']) for c in cs if DROP[0] + 0.005 < hit_time(c) < DROP[1] - 0.005]
    if inside:
        raise ValueError('cue(s) start inside the drop-out %s: %s' % (DROP, inside))
    early = [(c['name'], c['t']) for c in cs if hit_time(c) < -1e-6 or hit_time(c) > DUR + 1e-6]
    if early:
        raise ValueError('cue hit outside 0..DUR: %s' % early)
    return dict(max_starts_per_instant=worst, at=round(at, 4))


def cues(version='A', report=False):
    """The final cue list for version 'A' (default; what the reel module imports) or 'B'."""
    register()
    cs, rep = fit(raw_cues(version), version)
    rep['check'] = check(cs, version)
    return (cs, rep) if report else cs


# ================================================================================================ mixer
def _circ(fn, x, pad=CIRC_PAD):
    """fn applied to x padded circularly by pad seconds on both sides (loop-continuous ballistics), cropped."""
    p = _n(pad)
    xp = np.concatenate([x[-p:], x, x[:p]], axis=0)
    y = fn(xp)
    return y[p:p + len(x)]


def gate_curve(n, t0, fade=GATE_FADE):
    """1 until t0 - fade, raised-cosine to 0 at t0, 0 after (n samples)."""
    g = np.ones(n)
    i0, i1 = _n(t0 - fade), _n(t0)
    g[i0:i1] = 0.5 * (1.0 + np.cos(np.pi * np.arange(i1 - i0) / (i1 - i0)))
    g[i1:] = 0.0
    return g


def desi_gate():
    """The street bed's level curve over one loop: 1, cosine out 27.0-27.3, 0 in the drop-out, 4 ms back in at 28.0."""
    g = np.ones(N)
    a0, a1 = _n(DROP[0] - 0.3), _n(DROP[0])
    g[a0:a1] = 0.5 * (1.0 + np.cos(np.pi * np.arange(a1 - a0) / (a1 - a0)))
    b0, b1 = _n(DROP[1]), _n(DROP[1] + 0.004)
    g[a1:b0] = 0.0
    g[b0:b1] = 0.5 * (1.0 - np.cos(np.pi * np.arange(b1 - b0) / (b1 - b0)))
    return g


def bed_bus():
    """Both beds at unit reference (each loop at its own REF loudness x rel gain), seamless over DUR."""
    room = np.asarray(A.sound('room_tone', dur=DUR), dtype=np.float64)
    city = np.asarray(A.sound('desi_city', dur=DUR), dtype=np.float64)
    assert len(room) == N and len(city) == N, (len(room), len(city), N)
    return room * undb(BED[0]['gain_db']) + city * undb(BED[1]['gain_db']) * desi_gate()[:, None]


def _place(cs, M, vary=True):
    """Render every cue into four buses (pre / post the drop-out, dry / room send) of M samples. A negative start
    (a pre-hit attack before 0 s) wraps to the end of the loop."""
    bus = {k: np.zeros((M, 2)) for k in ('pre', 'post', 'pre_send', 'post_send')}
    placed, counts = [], {}
    for c in sorted(cs, key=lambda c: float(c['t'])):
        k = (c['name'], A._key(c['params']))
        counts[k] = counts.get(k, -1) + 1
        seed = c['seed'] if 'seed' in c else ((counts[k] % 4) if vary else 0)
        y, hit = A._render_cue(c, (counts[k] % 4) if vary else None)
        L = len(y)
        start = float(c['t']) - (hit if c['align'] == 'hit' else 0.0)
        side = 'pre' if start + hit < DROP[0] - 0.002 else 'post'
        cat = A.SOUNDS[c['name']]['category']
        sdb = c.get('send_db', A.SOUNDS[c['name']]['send'] if A.SOUNDS[c['name']]['send'] is not None
                    else A._CAT_SEND[cat])
        i = _n(start)
        if i < 0:                                    # the pre-hit part before 0 s plays at the end of the loop
            head, y = y[:-i], y[-i:]                 # (after the drop-out: post bus, never gated)
            bus['post'][N + i:N] += head
            if sdb is not None and sdb > -60:
                bus['post_send'][N + i:N] += head * undb(sdb)
            i = 0
        m = min(len(y), M - i)
        bus[side][i:i + m] += y[:m]
        if sdb is not None and sdb > -60:
            bus[side + '_send'][i:i + m] += y[:m] * undb(sdb)
        placed.append(dict(t=float(c['t']), name=c['name'], start=round(start, 4), hit=round(start + hit, 4),
                           end=round(start + L / SR, 4), seed=int(seed), gain_db=round(float(c['gain_db']), 2),
                           duck_db=c.get('duck_db', 0.0), side=side, warn='', ev=c.get('ev', ''),
                           hero=bool(c.get('hero'))))
    return bus, placed


def mix_loop(cs, *, target_lufs=TARGET_LUFS, tp_ceiling=TP_CEILING, fixed=None, auto_duck=True, vary=True,
             verbose=True):
    """audio.mix chain + the drop-out gate + loop folding (module docstring). fixed = rep['gains'] of another run
    (version B uses A's gains). Returns a report dict like audio.mix (+ 'gains', 'audio', 'fx', 'bed')."""
    M = N + _n(WRAP_TAIL)
    cs = [A._norm_cue(c) for c in cs]
    if auto_duck and cs:
        cs = A.duck_under(cs)
    bus, placed = _place(cs, M, vary)
    pre = bus['pre'] + A.reverb(bus['pre_send'], 'studio', wet_db=0.0, dry=0.0)[:M]
    post = bus['post'] + A.reverb(bus['post_send'], 'studio', wet_db=0.0, dry=0.0)[:M]
    resid = float(A.db(np.max(np.abs((pre + post)[-_n(0.25):])) + 1e-15))   # nothing may be lost past M
    pre *= gate_curve(M, DROP[0])[:, None]
    fx = pre + post
    out = fx[:N].copy()
    out[:M - N] += fx[N:]                            # fold the tail past DUR onto the head (WRAP_TAIL < DUR)
    fx = out
    # ---- audio.mix gain staging: fx to target, glue 2:1 at target + 8 (circular ballistics)
    g_fx = fixed['g_fx'] if fixed else float(undb(target_lufs - A.loudness(fx)))
    fx = fx * g_fx
    gr_comp = _circ(lambda x: A.compressor_gain(x, thresh_db=target_lufs + 8.0, ratio=2.0), fx)
    fx = fx * undb(gr_comp)[:, None]
    # ---- beds: sidechained 5 dB under the SFX, anchored at target + BED_GAIN_DB + 8 (audio.mix BED_ANCHOR_DB)
    bed = bed_bus()
    bed = _circ(lambda x: A.sidechain(x[:, :2], x[:, 2:], depth_db=5.0), np.concatenate([bed, fx], 1))
    bed_g = fixed['bed_g'] if fixed else float(undb(target_lufs + BED_GAIN_DB + BED_ANCHOR_DB - A.loudness(bed)))
    bed = bed * bed_g
    pk_fx = _circ(A.tp_envelope, fx)
    pk_bed = _circ(A.tp_envelope, bed)

    def _eval(G, ceil):
        gl = _circ(lambda pk: A.limiter_gain(None, ceil, pk=pk), pk_fx * undb(G) + pk_bed)
        y = (fx * undb(G) + bed) * gl[:, None]
        return y, gl, A.loudness(y)

    if fixed:
        G, ceil = fixed['G'], fixed['ceil']
        y, gl, L1 = _eval(G, ceil)
    else:
        G, ceil = 0.0, tp_ceiling - 0.2
        for attempt in range(6):
            lo = hi = best = None
            for it in range(40):
                y, gl, L1 = _eval(G, ceil)
                if best is None or abs(L1 - target_lufs) < abs(best[2] - target_lufs):
                    best = (G, gl, L1, y)
                if abs(L1 - target_lufs) < 0.02:
                    break
                if L1 < target_lufs:
                    lo = (G, L1)
                else:
                    hi = (G, L1)
                if lo and hi:
                    if hi[0] - lo[0] < 1e-4:
                        break
                    G = lo[0] + (target_lufs - lo[1]) * (hi[0] - lo[0]) / max(hi[1] - lo[1], 1e-6)
                    if not (lo[0] < G < hi[0]) or it % 3 == 2:
                        G = 0.5 * (lo[0] + hi[0])
                else:
                    G += float(np.clip(target_lufs - L1, -24, 24))
            G, gl, L1, y = best
            if A.true_peak(y) <= tp_ceiling - 0.05:
                break
            ceil -= A.true_peak(y) - (tp_ceiling - 0.1)
    fx_out = fx * (undb(G) * gl)[:, None]
    bed_out = bed * gl[:, None]
    glc = A.db(np.maximum(gl, 1e-9))
    for p in placed:
        i0, i1 = max(0, _n(p['hit'] - 0.01)), min(N, _n(p['hit'] + 0.15))
        p['limiter_gr_db'] = round(float(-glc[i0:i1].min()), 2) if i1 > i0 else 0.0
        p['glue_gr_db'] = round(float(-gr_comp[i0:i1].min()), 2) if i1 > i0 else 0.0
        if p['end'] > DUR + 0.01:
            p['warn'] = 'tail wrapped to 0 s'
        if p['side'] == 'pre' and p['end'] > DROP[0] + 0.01:
            p['warn'] = (p['warn'] + '; ' if p['warn'] else '') + 'tail cut at the drop-out'
    rep = dict(dur=DUR, cues=len(cs), integrated_lufs=round(A.loudness(y), 2), true_peak_dbtp=round(A.true_peak(y), 2),
               sample_peak_dbfs=round(float(A.db(np.max(np.abs(y)))), 2), lra_lu=round(A.loudness_range(y), 2),
               max_momentary_lufs=round(A.momentary_max(y), 2), max_short_term_lufs=round(A.momentary_max(y, 3.0), 2),
               limiter_max_gr_db=round(max(0.0, float(-A.db(np.min(gl)))), 2),
               comp_max_gr_db=round(float(-np.min(gr_comp)), 2),
               limiter_pct_over_1db=round(100.0 * float(np.mean(gl < undb(-1.0))), 2),
               bed=[dict(name=b['name'], t0=b['t0'], t1=b['t1'], rel_gain_db=b['gain_db']) for b in BED],
               bed_lufs=round(A.loudness(bed_out), 2), placed=placed, files={},
               gains=dict(g_fx=float(g_fx), G=float(G), ceil=float(ceil), bed_g=float(bed_g)),
               tail_residual_dbfs=round(resid, 1), drop=list(DROP), wrap=True)
    rep['audio'] = y.astype(np.float32)
    rep['fx'] = fx_out.astype(np.float32)
    rep['bed_audio'] = bed_out.astype(np.float32)
    if verbose:
        print(A.report_text(rep))
    return rep


# ================================================================================================ build
def _ebur128(path):
    import re
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    s = r[r.rfind('Summary'):]
    get = lambda k: float(re.search(k + r':\s+(-?[\d.]+)', s).group(1))
    return dict(I=get('I'), LRA=get('LRA'), TP=get('Peak'))


def _jsonable(o):
    if isinstance(o, dict):
        return {k: _jsonable(v) for k, v in o.items() if k not in ('audio', 'fx', 'bed_audio')}
    if isinstance(o, (list, tuple)):
        return [_jsonable(v) for v in o]
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, np.bool_):
        return bool(o)
    return o


def build(out_dir=AUD):
    """SFX stems A and B (B at A's gains) + cue sheets + reports + overview PNGs."""
    os.makedirs(out_dir, exist_ok=True)
    allrep = {}
    gains = None
    for v in ('A', 'B'):
        cs, frep = cues(v, report=True)
        rep = mix_loop(cs, fixed=gains)
        if v == 'A':
            gains = rep['gains']
        stem = STEM[v] if out_dir == AUD else os.path.join(out_dir, os.path.basename(STEM[v]))
        base = stem[:-4]
        rep['files'] = dict(stem=A._write_wav(stem, rep['audio'], 24), fx=A._write_wav(base + '_fx.wav', rep['fx'], 24),
                            bed=A._write_wav(base + '_bed.wav', rep['bed_audio'], 24))
        png = os.path.join(out_dir, '%s_sfx_overview_%s.png' % (MODULE, v))
        A.mix_overview(rep, png, '%s SFX stem, version %s' % (MODULE, v))
        rep['files']['overview'] = png
        rep['ffmpeg'] = _ebur128(stem)
        with open(os.path.join(out_dir, '%s_cues_%s.json' % (MODULE, v)), 'w') as fh:
            json.dump(_jsonable(cs), fh, indent=1)
        allrep[v] = dict(mix=_jsonable(rep), fit=_jsonable(frep))
        allrep[v]['_y'] = rep['audio']
    # B equals A once the hook-B tails are gone
    yA, yB = allrep['A'].pop('_y').astype(np.float64), allrep['B'].pop('_y').astype(np.float64)
    d = np.abs(yA - yB).max(1)
    nz = np.nonzero(d[:_n(DROP[0])] > 1e-6)[0]
    same_from = round(float(nz[-1] + 1) / SR, 3) if len(nz) else 0.0
    allrep['splice'] = dict(identical_from_s=same_from,
                            max_abs_diff_after_6s=float(d[_n(6.0):].max()),
                            max_abs_diff_2p8_to_identical_dbfs=round(float(A.db(d[_n(SPLICE):_n(max(same_from,
                                                                                                    SPLICE + 0.01))].max() + 1e-15)), 1))
    with open(os.path.join(out_dir, '%s_sfx_report.json' % MODULE), 'w') as fh:
        json.dump(allrep, fh, indent=1)
    return allrep


# ================================================================================================ rough mix + measurements
def _seg(x, t0, t1):
    return x[max(0, _n(t0)):min(len(x), _n(t1))]


def _rms_db(x, t0, t1):
    s = _seg(x, t0, t1)
    return round(float(10 * np.log10(np.mean(np.square(s)) + 1e-30)), 1)


def _peak_db(x, t0, t1):
    return round(float(A.db(np.max(np.abs(_seg(x, t0, t1))) + 1e-15)), 1)


def _seg_lufs(x, t0, t1):
    """K-weighted loudness of a segment (ungated mean square; for windows shorter than 3 s)."""
    s = _seg(x, t0, t1)
    tt, lv = A.loudness_curve(s, win=min(0.4, (t1 - t0) * 0.99), hop=0.01)
    return round(float(10 * np.log10(np.mean(10 ** (np.asarray(lv) / 10.0)))), 1)


def _momentary(x, hop=0.01):
    tt, lv = A.loudness_curve(x, win=0.4, hop=hop)
    return np.asarray(tt) + 0.2, np.asarray(lv)          # centre of each 400 ms block


def onset_lag(stem, cue, seed=None, search=0.06):
    """Lag (s) of a cue's own rendered waveform (the seed the mixer used) inside a stem (normalised
    cross-correlation over its first 120 ms after the hit, +-search)."""
    c = A._norm_cue(cue)
    if seed is not None:
        c['seed'] = seed
    y, hit = A._render_cue(c, None)
    y = np.asarray(y, float).mean(1)
    start = float(c['t']) - (hit if c.get('align', 'hit') == 'hit' else 0.0)
    L = min(len(y), _n(0.12) + _n(hit))
    tmpl = y[:L]
    s = stem.mean(1)
    best, lag = -2.0, None
    for d in range(-_n(search), _n(search) + 1, 4):
        i = _n(start) + d
        if i < 0 or i + L > len(s):
            continue
        seg = s[i:i + L]
        r = float(np.dot(seg, tmpl) / (np.linalg.norm(seg) * np.linalg.norm(tmpl) + 1e-20))
        if r > best:
            best, lag = r, d
    # refine to the sample around the coarse best
    for d in range(lag - 4, lag + 5):
        i = _n(start) + d
        if i < 0 or i + L > len(s):
            continue
        seg = s[i:i + L]
        r = float(np.dot(seg, tmpl) / (np.linalg.norm(seg) * np.linalg.norm(tmpl) + 1e-20))
        if r >= best:
            best, lag = r, d
    return lag / SR, best


def rough(out_dir=ROUGH):
    """Rough mixes A and B with the shared epic_mix.mix_reel (VO + this SFX stem + music_full.wav) + measurements."""
    import epic_mix as EMX
    SJ = register()
    os.makedirs(out_dir, exist_ok=True)
    report = dict(inputs=dict(vo_A=VO['A'][0], vo_B=VO['B'][0], music=MUSIC, sfx_A=STEM['A'], sfx_B=STEM['B']))
    for v, name in (('A', MODULE), ('B', MODULE + '_hookb')):
        rep = EMX.mix_reel(name, dur=DUR, vo=VO[v][0], sfx=STEM[v], music=MUSIC if os.path.exists(MUSIC) else None,
                           out_dir=out_dir, vo_offset=0.0)
        f = rep['files']
        mix = A._st(A.read_wav(f['mix'])[0]).astype(np.float64)
        vos = A._st(A.read_wav(f['stem_vo'])[0]).astype(np.float64)
        sfx = A._st(A.read_wav(f['stem_sfx'])[0]).astype(np.float64)
        mus = A._st(A.read_wav(f['stem_music'])[0]).astype(np.float64)
        m = dict(epic_mix=_jsonable(rep), ffmpeg_mix=_ebur128(f['mix']), ffmpeg_vo_sfx=_ebur128(f['vo_sfx']))
        # speech windows (words + VO audio activity) for the per-window checks
        wins, src = SJ.hero_windows(VO[v][1], vo_audio=VO[v][0])
        tc, lvo = _momentary(vos)
        _, lsf = _momentary(sfx)
        _, lmu = _momentary(mus)
        _, lms = _momentary(mus + sfx)
        top = lvo.max()
        inwin = np.zeros(len(tc), bool)
        for a, b in wins:
            inwin |= (tc >= a + 0.2) & (tc <= b - 0.2)          # 400 ms blocks fully inside a speech window
        act = inwin & (lvo > top - 15.0)
        d_sfx, d_mus = (lvo - lsf)[act], (lvo - lmu)[act]
        m['speech_blocks'] = int(act.sum())
        m['vo_over_music_lu'] = dict(median=round(float(np.median(d_mus)), 1), p10=round(float(np.percentile(d_mus, 10)), 1),
                                     min=round(float(d_mus.min()), 1))
        m['vo_over_sfx_lu'] = dict(median=round(float(np.median(d_sfx)), 1), p10=round(float(np.percentile(d_sfx, 10)), 1),
                                   min=round(float(d_sfx.min()), 1), at=round(float(tc[act][np.argmin(d_sfx)]), 2))
        # every cue whose hit is in a speech window: VO minus SFX momentary at its hit (block centred on the hit)
        cs = json.load(open(os.path.join(AUD, '%s_cues_%s.json' % (MODULE, v))))
        per = []
        for c in cs:
            h = hit_time(c)
            if any(a <= h <= b for a, b in wins) or c.get('vo'):
                i = int(np.argmin(np.abs(tc - (h + 0.1))))
                per.append(dict(t=c['t'], name=c['name'], vo_minus_sfx_lu=round(float(lvo[i] - lsf[i]), 1),
                                vo_lufs=round(float(lvo[i]), 1), sfx_lufs=round(float(lsf[i]), 1), note=c.get('vo', '')))
        m['cues_in_speech'] = per
        # silences and the drop-out
        m['music_peak_dbfs'] = {'12.62-13.98': _peak_db(mus, 12.62, 13.98), '27.31-27.99': _peak_db(mus, 27.31, 27.99)}
        m['room_tone_in_mix_lufs'] = {'12.62-13.98': _seg_lufs(mix, 12.62, 13.98),
                                      '13.0-13.6 (no cue sounding)': _seg_lufs(mix, 13.0, 13.6),
                                      '27.35-27.95 (drop-out)': _seg_lufs(mix, 27.35, 27.95)}
        m['sfx_stem_dropout_peak_dbfs'] = _peak_db(sfx, 27.31, 27.99)
        m['music_rms_db'] = {'12.10': _rms_db(mus, 12.05, 12.15), '12.62': _rms_db(mus, 12.57, 12.67)}
        # loudest moment of music + SFX (VO excluded)
        i = int(np.argmax(lms))
        m['max_momentary_music_sfx'] = dict(t=round(float(tc[i]), 2), lufs=round(float(lms[i]), 2))
        for a, b in ((7.5, 8.0), (8.2, 8.7), (12.4, 12.9), (19.4, 20.0), (19.6, 27.3), (28.0, 28.4)):
            sel = (tc >= a) & (tc <= b)
            m['max_momentary_music_sfx'][('%.1f-%.1f' % (a, b))] = round(float(lms[sel].max()), 2)
        # loop seam: last frame + first frame of the mix
        f1 = _n(1.0 / FPS)
        m['seam'] = dict(rms_last_frame_dbfs=_rms_db(mix, DUR - 1.0 / FPS, DUR), rms_first_frame_dbfs=_rms_db(mix, 0, 1.0 / FPS),
                         step=round(float(np.abs(mix[0] - mix[-1]).max()), 5),
                         median_step_last_100ms=round(float(np.median(np.abs(np.diff(mix[-_n(0.1):], axis=0)))), 5))
        assert f1 > 0
        # L11 vs the 35.0 notif_ping, the loop swell (35.6-36.4) and the music's 35.7 'tin'
        l11 = [(a, b) for a, b in wins if b > 34.6]
        sel = np.zeros(len(tc), bool)
        for a, b in l11:
            sel |= (tc >= a + 0.2) & (tc <= b - 0.2)
        sel &= lvo > top - 15.0
        m['L11_vo_over'] = dict(sfx_min=round(float((lvo - lsf)[sel].min()), 1), music_min=round(float((lvo - lmu)[sel].min()), 1))
        # hero / r2 cue sync in the SFX stem of the mix (own waveform, normalised cross-correlation)
        sync = []
        srep = json.load(open(os.path.join(AUD, '%s_sfx_report.json' % MODULE)))
        seeds = {(p['t'], p['name']): p['seed'] for p in srep[v]['mix']['placed']}
        for c in cs:
            if c.get('hero') or c['ev'] in ('buzz1', 'buzz2', 'ping1', 'ping2', 'roll47', 'roll99', 'plus', 'nani',
                                            'msg', 'b_cut'):
                lag, r = onset_lag(sfx, c, seeds.get((c['t'], c['name'])))
                sync.append(dict(t=c['t'], name=c['name'], ev=c['ev'], lag_ms=round(lag * 1000, 2), ncc=round(r, 3)))
        m['sync'] = sync
        report[v] = m
    with open(os.path.join(out_dir, 'rough_report.json'), 'w') as fh:
        json.dump(report, fh, indent=1)
    return report


# ================================================================================================ verify + table
def verify():
    """Light checks: the end-card cues match endcard.EndCard, the tuning lands on its notes, the local sound is clean."""
    register()
    out = {}
    try:
        import endcard as E
        ref = E.EndCard('GROUP MEIN', 'bhejo', monogram='JD', dur=4.2).cues(EV['card_t0'], DUR)
        mine = [c for c in body_cues(dict(EV, **EV_B)) if c['ev'] in ('card_t0', 'end')]
        out['endcard'] = sorted((round(c['t'], 4), c['name']) for c in ref) == sorted((round(c['t'], 4), c['name'])
                                                                                       for c in mine)
    except Exception as e:  # noqa: BLE001
        out['endcard'] = 'not checked: %r' % e
    tun = {}
    for k in TUNE:
        p = tune(k)
        nm = ('notif_ping' if k.startswith('ping') else 'pop' if k.startswith('pop') else
              'glass_tap' if k.startswith('tap') else 'bubble_pop')
        f = (ridge_hz if TUNE_EST.get(k) == 'ridge' else f0_of)(nm, pitch=p, seed=0)
        tun[k] = dict(est=TUNE_EST.get(k, 'f0'), pitch=p, f0=round(f, 1), target=TUNE_TARGET[k], cents=round(cents(f, NOTE[TUNE_TARGET[k]]), 1))
    out['tuning'] = tun
    x = A.sound('btk_haptic')
    xa = np.asarray(x, float)
    out['btk_haptic'] = dict(hit=x.hit, len=round(len(x) / SR, 3), qc=A.qc(xa.astype(np.float32), x.hit),
                             stats={k: (round(v, 2) if isinstance(v, float) else v) for k, v in A.stats(xa, x.hit).items()},
                             tp_dbtp=round(A.true_peak(xa), 2))
    ref = np.asarray(A.sound('notif_ping', pitch=1.1225, buzz=1), float)[:_n(0.345)]
    out['btk_haptic']['same_samples_as_notif_ping_buzz_to_0.345s'] = bool(np.array_equal(ref, xa[:_n(0.345)]))
    return out


def table(version='A'):
    cs = cues(version)
    rows = ['| # | t (s) | f | name | params | align | gain dB set -> after VO fit | filters | VO fit | event |',
            '|---|---|---|---|---|---|---|---|---|---|']
    brief = {(c['t'], c['name'], c['ev']): c['gain_db'] for c in raw_cues(version)}
    for i, c in enumerate(sorted(cs, key=lambda c: (c['t'], c['name'])), 1):
        p = dict(c['params'])
        if c.get('seed') is not None:
            p['seed'] = c['seed']
        filt = ', '.join('%s %d' % (k, c[k]) for k in ('hp', 'lp') if c.get(k)) or '-'
        if c.get('pan'):
            filt = ('pan %+.1f' % c['pan']) if filt == '-' else filt + ', pan %+.1f' % c['pan']
        g0 = brief.get((c['t'], c['name'], c['ev']), c['gain_db'])
        rows.append('| %d | %.4f | %d | %s%s | %s | %s | %+.0f -> %+.0f | %s | %s | %s |' % (
            i, c['t'], int(round(c['t'] * FPS)), c['name'], ' **hero**' if c.get('hero') else '',
            ', '.join('%s %s' % (k, v) for k, v in p.items()) or '-', c.get('align', 'hit'), g0, c['gain_db'], filt,
            c.get('vo', '') or '-', c['why']))
    return '\n'.join(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('cmd', nargs='?', default='all', choices=['cues', 'build', 'rough', 'verify', 'table', 'all'])
    ap.add_argument('--version', default='A', choices=['A', 'B'])
    a = ap.parse_args()
    if a.cmd == 'cues':
        cs, rep = cues(a.version, report=True)
        for c in cs:
            print('%8.4f  %-14s %-5s %+6.1f  %-44s %s' % (c['t'], c['name'], c.get('align', 'hit'), c['gain_db'],
                                                         json.dumps(c['params'])[:44], c.get('vo', '')))
        print(json.dumps(_jsonable({k: rep[k] for k in ('check', 'hero_ok', 'violations', 'band_fix', 'busy',
                                                         'body_carve', 'hero_source')}), indent=1))
    elif a.cmd == 'table':
        print(table(a.version))
    elif a.cmd == 'verify':
        print(json.dumps(_jsonable(verify()), indent=1))
    else:
        if a.cmd in ('build', 'all'):
            r = build()
            print(json.dumps({v: {k: r[v]['mix'][k] for k in ('integrated_lufs', 'true_peak_dbtp', 'lra_lu',
                                                               'limiter_max_gr_db', 'comp_max_gr_db', 'bed_lufs',
                                                               'tail_residual_dbfs', 'ffmpeg')} for v in 'AB'},
                             indent=1))
            print('splice', r['splice'])
        if a.cmd in ('rough', 'all'):
            r = rough()
            print(json.dumps({v: {k: r[v][k] for k in ('ffmpeg_mix', 'ffmpeg_vo_sfx', 'vo_over_music_lu',
                                                       'vo_over_sfx_lu')} for v in 'AB'}, indent=1))


if __name__ == '__main__':
    main()
