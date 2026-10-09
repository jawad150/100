"""ek_frame_ki_keemat_sfx.py - SFX layer of Reel 3 / C08 "Ek Frame ki Keemat" (the exploded frame). Owner: sound-designer.

Binding plan: brand_reels/design/reels/ek_frame_ki_keemat/BRIEF.md r2 section 11 (cue list), section 5 (frame-exact beat
table), section 6 (hooks A and B), section 4 + 18 (sound rules and QA), SLATE section 3.3 (sound motif = the PAUSE CLICK:
mouse click + glass creak) and section 5.1 (-14 LUFS, TP <= -2 dBTP, VO >= 8 LU over the bed, <= 3 sounds on one instant,
one drop-out at the reveal, nothing busy in 1-4 kHz under words). Key / harmony per bar: MUSIC_ek_frame_ki_keemat.md
(D Phrygian-dominant, Sa = D4 293.66 Hz). Word timings: the FINAL Vlad VO (VO_TIMING.md). Cue sheet + measurements: SOUND.md
in the same design folder.

What this module owns (BRIEF 17.1: `cues(hook='A')`, `build()` -> SFX stem files)
    register()          sfx_jawad + epic_sfx sounds into audio.SOUNDS (idempotent); no local sounds are needed
    events()            the picture events the cues sit on: BRIEF r2 section 5 (EV), overridden key by key by
                        `ek_frame_ki_keemat.SFX_EVENTS` when the reel module exists and defines it (lazy import), so a
                        picture retime (VO_TIMING.md section 4) moves the sound with it. Keys: see EV below.
    raw_cues(hook)      the brief's cue list for 'A' (public hook) or 'B' (Trial hook, 0-3.0 s replaced), before the VO fit,
                        with three measured-VO adjustments (clear_spans) and the key tuning (TUNE)
    cues(hook)          raw_cues -> sfx_jawad.fit_under_vo against the final words + the VO audio (hero test); raises
                        HeroOnWordError if a hero lands on speech; checks names and the <= 3 starts per instant rule
    mix_loop(...)       audio.mix's chain (duck_under -> per-cue render with seed variation -> 'studio' room send -> glue
                        2:1 at target + 8 -> loudness to -18 LUFS + 4x true-peak limiter) with the two things this reel needs:
                        (1) the drop-out: cues that start before 25.800 s (and their room sends) are cut at 25.796-25.800 and
                        stay cut, so 25.800-26.066 is digital silence and the play click at f782 is the only sound until the
                        C8 whip's lead-in and the flash_hit suck; (2) the loop: tails that run past DUR wrap onto t = 0
                        (no tail fade; the card's reverse swell ends exactly on 33.600 and frame 0's impact_soft releases it).
                        checked against audio.mix (same cues, no gate, no wrap): see verify()
    build(hook)         SFX stems -> <RW>/audio/ek_frame_ki_keemat_sfx_stem.wav (A) and ..._hookb_sfx_stem.wav (B: hook-B cues
                        0-3.0 s + the A body, rendered at A's exact gains so the 3.000 s splice is seamless), _cues.json,
                        _sfx_report.json, _sfx_overview.png; -18 LUFS (A), TP <= -2.0 dBTP, 48 kHz 24-bit
    rough()             the final chain on the real inputs (ek_frame_ki_keemat_music.mix: epic_mix.mix_reel A + B and the
                        hook-B splice) into <RW>/audio/rough/ + every measurement of BRIEF 18 "Sound" -> rough_report.json
    BED, BED_GAIN_DB    None: no SFX bed (BRIEF 11: the void is silent apart from the score)

CLI (run in pipeline/jawad_reels; heavy runs through tools/heavy.sh)
    python3 ek_frame_ki_keemat_sfx.py cues [--hook A|B]     cue table after the VO fit
    python3 ek_frame_ki_keemat_sfx.py build                 A + B SFX stems (+ json, overview png)
    python3 ek_frame_ki_keemat_sfx.py rough                 rough mixes A / B / hook B + measurements
    python3 ek_frame_ki_keemat_sfx.py verify                mixer equivalence + stem checks

The reel module's cues() stays [] (BRIEF 17.2). Renders use `--no-sfx-build --audio <RW>/audio/ek_frame_ki_keemat_mix.wav`
(the music-supervisor's final mix of this stem).
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

MODULE = 'ek_frame_ki_keemat'
DUR, BPM, FPS = 33.6, 100.0, 30
BEAT = 60.0 / BPM                              # 0.6 s = 18 f
N = _n(DUR)
assert N == 1612800
RW = os.path.join(REPO, 'workspace', 'jawad_reels', MODULE)
AUD = os.path.join(RW, 'audio')
VODIR = os.path.join(RW, 'vo')
VO_A = os.path.join(VODIR, 'vo_stem.wav')                                  # = ek_frame_ki_keemat_vo.wav (FINAL)
VO_A_WORDS = os.path.join(VODIR, MODULE + '_vo.words.json')               # = words.json = vo_stem.words.json
VO_B = os.path.join(VODIR, MODULE + '_hookb_vo.wav')
VO_B_WORDS = os.path.join(VODIR, MODULE + '_hookb_vo.words.json')
MUSIC = os.path.join(RW, 'music', 'music_full.wav')
STEM_A = os.path.join(AUD, MODULE + '_sfx_stem.wav')
STEM_B = os.path.join(AUD, MODULE + '_hookb_sfx_stem.wav')
ROUGH = os.path.join(AUD, 'rough')
SPLICE = 3.0                                   # hook B frames 0-89; A and B identical from f90

BED, BED_GAIN_DB = None, -30.0                 # no SFX bed
TARGET_LUFS, TP_CEILING = -18.0, -2.0
DROP = (25.8, 26.4)                            # drop-out: 1 beat [10.3] -> [11.0], digital silence to the play click
GATE_FADE = 0.004                              # 25.796-25.800, the music's gate edge
WRAP_TAIL = 4.0                                # s rendered past DUR, folded back onto t = 0
SPAN_MIN = 0.5                                 # a swell shortened to clear speech must still last >= 0.5 s


def F(f):
    """Reel time of frame f (30 fps)."""
    return round(f / FPS, 4)


# ================================================================================================ picture events
# BRIEF r2 section 5 (frame-exact, 30 fps; beat = 0.6 s). The reel module may override any key with SFX_EVENTS.
EV = dict(
    f0=0.0,                      # S1 the finished frame playing (loop release)
    pause=0.3,                   # f9   PAUSE: chip > -> II (motif)
    seams=0.6,                   # f18  seam glint sweep (motif part 2: glass)
    separate=0.9,                # f27  layers separate in z
    pullback=1.6,                # f48  camera pull-back
    orbit=2.4,                   # f72  orbit to side-on starts
    roll12=3.0,                  # f90  counter 00 -> 12 starts (splice)
    land12=4.8,                  # f144 side-on lands, counter 12 settles (L3 push 0.3)
    swoop=5.7,                   # f171 swoop into the fly-through (pass)
    tags=(6.0, 6.6, 7.2, 7.8, 8.4, 9.0, 9.6, 10.2, 10.8, 11.4),   # tag arrivals 01..11 (09+10 share 10.8)
    rehook=12.0,                 # f360 stop on pane 12 (L3 push 0.35)
    swing=12.6,                  # f378 swing to frontal
    flicks=(13.2, 13.5, 13.8, 14.4),   # OFF, ON, OFF, ON (resolved "with")
    alive=14.43,                 # the frame comes alive (sparkle)
    c3=16.8,                     # f504 C3 portal cut (plan cues: swell ends 16.7333)
    c3_swell=(16.0, 16.7333),    # the plan's reverse_swell (0.733 s)
    wave=16.9,                   # f507 light wave down the corridor
    roll360=18.9,                # f567 counter 12 -> 360 starts
    surge=(19.2, 19.8),          # surge passes
    land360=20.4,                # f612 360 lands (L3 push 0.5)
    lanes=21.9,                  # f657 three audio lanes rise
    rush=(24.3, 24.75, 25.2),    # stacks fly back
    play_click=F(782),           # 26.0667 the play click (held-breath element)
    c8_whip=F(791),              # 26.3667 C8 punch (plan whip)
    payoff=26.4,                 # f792 reveal (C8 cut, push 1.0, music drop)
    keyword=26.62,               # payoff keyword glyphs rise
    card=29.4,                   # f882 end card t0
)


def events():
    """EV, overridden by the reel module's SFX_EVENTS (only keys that exist in EV; times in seconds)."""
    ev = dict(EV)
    try:
        import importlib
        M = importlib.import_module(MODULE)
    except Exception:            # the module does not exist yet (timeline on placeholders) or fails to import
        return ev
    if abs(float(getattr(M, 'DUR', DUR)) - DUR) > 1e-9:
        raise ValueError('%s.DUR = %s, this sfx module is built for %s' % (MODULE, M.DUR, DUR))
    for k, v in dict(getattr(M, 'SFX_EVENTS', {}) or {}).items():
        if k not in EV:
            raise KeyError('SFX_EVENTS key %r is unknown; known: %s' % (k, ', '.join(EV)))
        ev[k] = v
    return ev


# ================================================================================================ sounds and tuning
def register():
    import sfx_jawad as SJ
    import epic_sfx as E
    SJ.register()
    E.register()
    return SJ


def f0_of(name, **p):
    """Dominant partial above 150 Hz (bible 4.2)."""
    x = np.asarray(A.sound(name, **p), float).mean(1)
    X = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    f = np.fft.rfftfreq(len(x), 1.0 / SR)
    return float(f[np.argmax(X * (f > 150))])


def pitch_to(name, target_hz, octave=None):
    """pitch= multiplier that puts the sound's dominant partial on target_hz's nearest octave (bible 4.2), or, with
    octave=k, exactly on target_hz * 2**k."""
    f0 = f0_of(name)
    if octave is not None:
        return round(target_hz * 2.0 ** octave / f0, 4)
    r = target_hz / f0
    return round(r * 2.0 ** -round(math.log2(r)), 4)


D4, A4, EB4, BB4 = 293.66, 440.0, 311.13, 466.16
# Tonal SFX into the bar's harmony (MUSIC map: bar 0 drone D; bars 1-4 i i bVI i; bar 5 bII (Eb); bar 6 i; bars 7-10
# bVI i bVI bVII; bar 11 i; bar 12 bVI; bar 13 bVII -> i). Values are computed once from the rendered sounds.
TUNE = dict(
    tick_d=lambda: pitch_to('jd_ui_tick', D4, octave=4),     # D8 4699 Hz: tag ticks sit ABOVE the 1-4 kHz VO band ...
    tick_a=lambda: pitch_to('jd_ui_tick', A4, octave=4),     # A8 7040 Hz  ... alternating (brief: 1.0 / 1.12)
    tap_d=lambda: pitch_to('glass_tap', 587.33),             # D7: "12" lands (bar 2, i) and the card tap (bar 12, bVI)
    tap_a=lambda: pitch_to('glass_tap', A4),                 # A6: "360" lands (bar 8, i)
    tap_eb=lambda: pitch_to('glass_tap', EB4),               # Eb7: the near-invisible pane 12 (bar 5, bII = Eb G Bb)
    click_a=lambda: pitch_to('ui_click', A4),                # A6: glass_truth's leading click (bars 2 and 8, i)
    flick_g=lambda: pitch_to('jd_ui_click', 392.0),          # G6: flick OFF clicks (bar 5, bII: G is its 3rd)
    lanes_bb=lambda: pitch_to('bar_grow', BB4),              # Bb4: lanes rise (bar 9, bVI = Bb D F)
)
_TUNED = {}


def tune(key):
    if key not in _TUNED:
        _TUNED[key] = TUNE[key]()
    return _TUNED[key]


# ================================================================================================ cue list
# Levels that differ from BRIEF 11 (each cue keeps the brief value as 'brief_db'). The brief's levels were set before
# the stem existed. Measured through mix_loop (-18 LUFS stem) AND the final chain (epic_mix A, real VO + music), these
# levels give: the reveal = the loudest momentary of mix A (window centred 26.55 s, >= 1.1 LU over the next loudest),
# every VO word >= 6 dB (K-weighted) over the SFX under it, the riser / rush >= 6 LU and C3 >= 3.5 LU under the reveal
# in the stem, and the stem limiter <= ~4 dB (it shaves only the stacked crack of flash_hit + impact_big at 26.397).
# Why the cuts are this large: epic_mix places the SFX stem by its INTEGRATED loudness (-18 LUFS); in this sparse stem
# the integrated is set by a few loud VO-free events, so every carve or duck under the VO raises the gain on the rest.
# The VO-free events therefore have to be balanced against the reveal inside the stem (SOUND.md "levels").
LV = dict(
    pause_click=-2.0,            # brief +4 (crest 21.9 dB: limited at +4); fit_under_vo takes -8 more inside "Aap"
    play_click=-11.0,            # brief +4: 10 dB of limiting at +4 on the lone click after the 8-frame silence
    c3_swell=-7.0, c3_air=-9.0, c3_hit=-5.0,       # brief -3 / -6 / -1 (plan cues): C3 was the stem's loudest moment
    rush=(-10.0, -10.0, -12.0),  # brief -6 / -6 / -8: the rush + music build at 25.6 out-shouted the reveal
    riser=-8.0,                  # brief -4: bible 4.5, a riser stays >= 4 LU under the hit it feeds
    flash_hit=-15.0,             # brief -3: its crack lands 3 ms before impact_big's and the two stack in the limiter
    impact_big=0.0,              # brief 0; + transient saturation (SAT)
    c8_whip=-16.0,               # brief -6 (crest 15.5 dB, 30 ms before the slam, same limiter event)
)
# Transient saturation drives (sat_transient: loudness-matched, tail from 0.5 s untouched), measured on the raw sounds,
# true peak minus max momentary: impact_big 8: 9.9 -> 4.7 dB (first 50 ms -2.1 dB, 0.1-0.3 s +1.0/+1.2 dB);
# flash_hit 3: 14.5 -> 8.3 dB; impact_soft 4 (C3): 9.8 -> 3.7 dB. The reveal is dense rather than spiky, so it keeps its
# loudness through the master's glue + limiter.
SAT = dict(impact_big=8.0, flash_hit=3.0, c3_hit=4.0)


def _c(t, name, gain_db=0.0, why='', **kw):
    d = dict(t=round(float(t), 4), name=name, gain_db=float(gain_db), why=why)
    d.update(kw)
    d.setdefault('params', {})
    return d


def hook_a_cues(ev):
    """0-3.0 s of hook A (BRIEF 6.1 + 11)."""
    return [
        _c(ev['f0'], 'impact_soft', -8, 'f0 transient + loop release; ends before the pause (frame sound stops)',
           align='start', dur=0.25),
        _c(ev['pause'], 'jd_mouse_click', LV['pause_click'], 'MOTIF: pause click (chip > -> II, chip at x 760)', pan=0.2,
           brief_db=4),
        _c(ev['seams'], 'jd_glass_slide', -2, 'MOTIF part 2: glass on glass, lands on the seam glint',
           params=dict(dur=0.3)),
        _c(ev['separate'], 'card_slide', -8, 'layers separate in z', lp=1100),
        _c(ev['pullback'], 'whoosh_slow', -10, 'camera pull-back', params=dict(direction=1)),
        _c(ev['orbit'], 'whoosh_slow', -8, 'orbit to side-on starts', pan=0.3, params=dict(direction=-1)),
    ]


def hook_b_cues(ev):
    """0-3.0 s of hook B (BRIEF 6.2 + 11): corridor mid-surge, rush back, meets hook A's orbit state at 3.0."""
    return [
        _c(0.0, 'impact_soft', -6, 'B f0 transient (corridor mid-surge)', align='start'),
        _c(0.2, 'whoosh_by', -4, 'B surge pass 1', params=dict(direction=1)),
        _c(0.6, 'whoosh_by', -6, 'B surge pass 2', params=dict(direction=-1)),
        _c(1.2, 'whoosh_by', -8, 'B surge pass 3', params=dict(direction=1)),
        _c(SPLICE, 'jd_reverse_swell', -8, 'B: stacks rush back, swell lands on the splice', params=dict(duration=1.2)),
    ]


def body_cues(ev, SJ):
    """3.0-33.6 s (identical in A and B)."""
    tk = [tune('tick_d'), tune('tick_a')]
    c = []
    c.append(_c(ev['roll12'], 'slot_tick', -12, 'counter 00 -> 12 (rolls to the landing)', align='start',
                params=dict(n=12, dur=round(ev['land12'] - ev['roll12'], 4)), hp=4500))
    g = SJ.glass_truth(ev['land12'], pitch=tune('tap_d'))
    for x in g:
        x['why'] = '"12" lands, side-on stack (glass_truth stack)'
        if x['name'] == 'ui_click':
            x['params'] = dict(pitch=tune('click_a'))
    c += g
    c.append(_c(ev['swoop'], 'whoosh_slow', -6, 'swoop into the fly-through (pass)', params=dict(direction=1)))
    for i, t in enumerate(ev['tags']):
        c.append(_c(t, 'jd_ui_tick', -14, 'tag %s arrives' % ('09/10' if i == 8 else '%02d' % (i + 1 + (i > 8))),
                    params=dict(pitch=tk[i % 2])))
    c.append(_c(ev['rehook'], 'impact_soft', -8, 'RE-HOOK: stop on pane 12'))
    c.append(_c(ev['rehook'], 'glass_tap', -10, 'the near-invisible pane 12', params=dict(pitch=tune('tap_eb'))))
    c.append(_c(ev['swing'], 'whoosh_slow', -10, 'swing to frontal', params=dict(direction=-1)))
    for t, st in zip(ev['flicks'], ('OFF', 'ON', 'OFF', 'ON')):
        if st == 'OFF':
            c.append(_c(t, 'jd_ui_click', -6, 'flick OFF (pane 12 hidden)', params=dict(pitch=tune('flick_g'))))
        else:
            c.append(_c(t, 'toggle_on', -8 if t != ev['flicks'][-1] else -6,
                        'flick ON' + (' (resolved "with")' if t == ev['flicks'][-1] else '')))
    c.append(_c(ev['alive'], 'jd_sparkle', -12, 'the frame comes alive'))
    s0, s1 = ev['c3_swell']
    c.append(_c(s1, 'reverse_swell', LV['c3_swell'], 'C3 approach into the portal disc (plan cue)',
                params=dict(duration=round(s1 - s0, 4)), tx='C3', span_min=SPAN_MIN, brief_db=-3))
    c.append(_c(ev['c3'], 'air_zoom', LV['c3_air'], 'C3 portal cut (plan cue)', tx='C3', brief_db=-6))
    c.append(_c(ev['c3'], 'impact_soft', LV['c3_hit'], 'C3 portal cut, corridor (plan cue)', tx='C3', brief_db=-1,
                **({'sat': SAT['c3_hit']} if SAT.get('c3_hit') else {})))
    c.append(_c(ev['wave'], 'jd_sparkle', -12, 'light wave runs down the corridor'))
    c.append(_c(ev['roll360'], 'slot_tick', -10, 'counter 12 -> 360 (rolls to the landing)', align='start',
                params=dict(n=29, dur=round(ev['land360'] - ev['roll360'], 4)), hp=4500))
    for t, d, p in zip(ev['surge'], (1, -1), (-0.4, 0.4)):
        c.append(_c(t, 'whoosh_by', -6, 'surge pass down the corridor', pan=p, params=dict(dur=1.4, direction=d)))
    g = SJ.glass_truth(ev['land360'], pitch=tune('tap_a'))
    for x in g:
        x['why'] = '"360" lands (glass_truth stack)'
        if x['name'] == 'ui_click':
            x['params'] = dict(pitch=tune('click_a'))
    c += g
    c.append(_c(ev['lanes'], 'bar_grow', -10, 'three audio lanes rise', align='start',
                params=dict(duration=0.3, pitch=tune('lanes_bb'))))
    for t, gdb, bdb, d, p in zip(ev['rush'], LV['rush'], (-6, -6, -8), (1, -1, 1), (-0.5, 0.5, -0.5)):
        c.append(_c(t, 'whoosh_by', gdb, 'rush: frame-stacks fly back', pan=p, params=dict(dur=1.0, direction=d),
                    brief_db=bdb, **({'sat': SAT['rush']} if SAT.get('rush') else {})))
    slam = SJ.ember_slam(ev['payoff'], bpm=BPM, riser_beats=2, gap_beats=1)
    for x in slam:
        x['why'] = ('riser into the drop-out (stops dead at 25.8)' if x['name'] == 'riser'
                    else 'REVEAL: reassembly slam, payoff (ember_slam)')
        if x['name'] in ('flash_hit', 'impact_big', 'riser'):
            x['brief_db'] = x['gain_db']
            x['gain_db'] = LV[x['name']]
        if x['name'] in SAT:
            x['sat'] = SAT[x['name']]
    c += slam
    c.append(_c(ev['play_click'], 'jd_mouse_click', LV['play_click'],
                'MOTIF: the play click (held-breath element after 8 f silence)', brief_db=4))
    c.append(_c(ev['c8_whip'], 'whip', LV['c8_whip'], 'C8 punch-in (plan cue)', params=dict(direction=1), tx='C8',
                brief_db=-6))
    c.append(_c(ev['keyword'], 'shimmer', -10, 'payoff keyword rises', hp=5500))
    # end card (endcard.EndCard(...).cues(29.4, 33.6), measured: swish 29.5 start, tap 30.15, shimmer 29.97, swell 33.6)
    t0 = ev['card']
    c.append(_c(t0 + 0.1, 'swish_small', -12, 'card: JD monogram ring draws on', align='start'))
    c.append(_c(t0 + 0.57, 'shimmer', -10, 'card: CTA keyword "bhejo"'))
    c.append(_c(t0 + 0.75, 'glass_tap', -12, 'card: monogram settles', params=dict(pitch=tune('tap_d'))))
    c.append(_c(DUR, 'reverse_swell', -8, 'loop bridge into frame 0 (ends exactly on 33.600)',
                params=dict(duration=0.8), span_min=SPAN_MIN))
    return c


def _words(hook):
    """(word dicts in reel time, VO audio (samples, sr)) for the hook: B = hook-B VO before 3.0 s + the A body."""
    wa = json.load(open(VO_A_WORDS))
    xa, sr = A.read_wav(VO_A)
    if hook == 'A':
        return wa, (xa, sr)
    wb = json.load(open(VO_B_WORDS))
    xb, srb = A.read_wav(VO_B)
    assert sr == srb == SR
    xa = A._st(xa).copy()
    xb = A._st(xb)
    i = _n(SPLICE)
    xa[:i] = 0.0
    xa[:min(i, len(xb))] = xb[:min(i, len(xb))]
    return [w for w in wb if w['start'] < SPLICE] + [w for w in wa if w['start'] >= SPLICE], (xa, sr)


def _speech(words, vo, pad=0.06):
    import sfx_jawad as SJ
    return SJ.hero_windows(words, 0.0, pad, vo)[0]


def clear_spans(cues, words, vo, pad=0.06):
    """Risers / reverse swells never overlap words (bible 4.5): a span cue whose body starts inside the (padded) speech
    is shortened so it starts after that speech ends, if it then still lasts >= its 'span_min' (1 beat); otherwise it
    is left for fit_under_vo to duck and darken. Measured speech = words (padded) + VO audio activity."""
    sp = _speech(words, vo, pad)
    out = []
    for c in cues:
        c = dict(c)
        smin = c.pop('span_min', None)
        if smin is not None and c.get('align', 'hit') == 'hit':
            d = float(c['params'].get('duration', c['params'].get('dur')))
            hit = float(c['t'])
            for a, b in sp:
                if a < hit and b > hit - d:
                    nd = round(hit - b, 4)
                    if nd >= smin:
                        c['params'] = dict(c['params'], duration=nd)
                        c['span_note'] = 'shortened %.3f -> %.3f s: starts %.3f, after speech ending %.3f' % (
                            d, nd, hit - nd, b)
                    else:
                        c['span_note'] = 'kept %.3f s (cleared length %.3f < %.2f); ducked by fit_under_vo' % (d, nd, smin)
                    break
        out.append(c)
    return out


def _seed(cs):
    """Explicit seeds 0..3 per repeated (name, params) in the order of the list (audio.mix's 'vary' rule), assigned
    separately to the hook part and to the body, so the body renders identically in hooks A and B."""
    n = {}
    for c in sorted(cs, key=lambda c: float(c['t'])):
        c.setdefault('params', {})
        k = (A.resolve(c['name']), A._key(c['params']))
        n[k] = n.get(k, -1) + 1
        c.setdefault('seed', n[k] % 4)
    return cs


def raw_cues(hook='A', ev=None):
    SJ = register()
    ev = ev or events()
    head = hook_a_cues(ev) if hook == 'A' else hook_b_cues(ev)
    return _seed(head) + _seed(body_cues(ev, SJ))


def check_names(cues):
    bad = [c['name'] for c in cues if c['name'] not in A.SOUNDS]
    if bad:
        raise KeyError('cue names not in audio.SOUNDS (no fuzzy fallback allowed): %s' % bad)


def event_time(c):
    """The audible instant of a cue: the hit for align='hit' (the start for spans: their END is the hit), the start
    for align='start'."""
    x = A.sound(c['name'], **c['params'])
    if c.get('align', 'hit') == 'start':
        return float(c['t'])
    if A.SOUNDS[c['name']]['category'] == 'transition' and c['name'] in ('riser', 'reverse_swell', 'jd_reverse_swell',
                                                                          'shepard_riser', 'reverse_cymbal'):
        return float(c['t']) - x.hit
    return float(c['t'])


def instants(cues, tol=0.025):
    """Clusters of cue events within tol (25 ms; the glass_truth sparkle at +30 ms counts as its own instant, as in
    BRIEF 11). Risers / swells count at their start (the end lands on a hit and does not count, bible 4.2)."""
    ts = sorted((event_time(c), c['name']) for c in cues)
    out, cur = [], []
    for t, n in ts:
        if cur and t - cur[0][0] > tol:
            out.append(cur)
            cur = []
        cur.append((t, n))
    if cur:
        out.append(cur)
    return out


CARVE_DB = dict(hero=-14.0, other=-8.0)   # body/tail of a cue under speech (the hit itself is never carved)
CARVE_LEAD, CARVE_RAMP, CARVE_GUARD = 0.015, 0.03, 0.03


def assign_carve(cs, words, vo):
    """Tails (and pre-hit bodies) of cues that fit_under_vo did not duck, where they run under speech (words + VO
    activity, unpadded): carve 'carve_db' there (heroes -14 dB, others -8 dB), starting CARVE_LEAD before the speech,
    CARVE_RAMP ramps, never within [hit - 20 ms, hit + CARVE_GUARD]. The hit stays whole; the boom's hall, the sub and
    the shimmer bloom step back under the line (bible 4.1: SFX >= 6 LU under the VO in VO windows)."""
    import sfx_jawad as SJ
    sp = SJ.hero_windows(words, 0.0, 0.0, vo)[0]
    out = []
    for c in cs:
        c = dict(c)
        if not c.get('vo'):
            x = A.sound(c['name'], **c['params'])
            ln = c['dur'] if c.get('dur') else len(x) / SR
            st = float(c['t']) - (x.hit if c.get('align', 'hit') == 'hit' else 0.0)
            hit = st + x.hit
            wins = []
            for a, b in sp:
                a, b = a - CARVE_LEAD, b
                if b <= st or a >= st + ln:
                    continue
                for lo, hi in ((st, hit - 0.02), (hit + CARVE_GUARD, st + ln)):
                    lo2, hi2 = max(a, lo), min(b, hi)
                    if hi2 - lo2 > 0.01:
                        wins.append((round(lo2, 4), round(hi2, 4)))
            if wins:
                c['carve'] = wins
                c['carve_db'] = CARVE_DB['hero' if SJ.band_of(c['name'], c) == 'hero' or c.get('stack') == 'ember_slam'
                                         else 'other']
        out.append(c)
    return out


def carve_env(n, start, wins, depth_db, ramp=CARVE_RAMP):
    """Gain envelope (n samples, cue starting at reel time `start`) that is depth_db inside the windows (reel time),
    with raised-cosine ramps of `ramp` s outside each window edge."""
    t = start + np.arange(n) / SR
    d = np.zeros(n)
    for a, b in wins:
        u = np.minimum(np.clip((t - (a - ramp)) / ramp, 0, 1), np.clip(((b + ramp) - t) / ramp, 0, 1))
        d = np.maximum(d, 0.5 - 0.5 * np.cos(np.pi * u))
    return undb(depth_db * d)


def cues(hook='A', report=False):
    """Fitted cue list (BRIEF 11): clear_spans + sfx_jawad.fit_under_vo against the final VO (words + audio)."""
    SJ = register()
    words, vo = _words(hook)
    c = clear_spans(raw_cues(hook), words, vo)
    check_names(c)
    fitted, rep = SJ.fit_under_vo(c, words, vo_audio=vo, report=True)       # hero='raise'
    fitted = assign_carve(fitted, words, vo)
    rep['carved'] = [dict(name=x['name'], t=x['t'], carve_db=x['carve_db'], windows=x['carve'])
                     for x in fitted if x.get('carve')]
    worst = max(len(g) for g in instants(fitted))
    if worst > 3:
        raise ValueError('more than 3 sounds on one instant: %s' % [g for g in instants(fitted) if len(g) > 3])
    return (fitted, rep) if report else fitted


# ================================================================================================ mixer
def sat_transient(y, hit, drive, t1=0.30, xf=0.20, pre=0.005):
    """Loudness-matched saturation of a hit's TRANSIENT only (bible 4.2: "saturation helps the hit cut through"):
    sfx_jawad.shape (alias-safe tanh, 8x oversampled) of the cue normalised to the peak of [hit - pre, hit + t1],
    cross-faded in over 2 ms before the hit and out over xf after hit + t1, scaled so the cue's max momentary loudness
    is unchanged. The tail after hit + t1 + xf is the raw sound. impact_big, drive 8: true peak - max momentary
    9.9 -> 4.7 dB, first 50 ms -2.1 dB, 0.1-0.3 s +1.0/+1.2 dB, decay from 0.5 s identical (measured)."""
    import sfx_jawad as SJ
    y = np.asarray(y, dtype=np.float64)
    t = np.arange(len(y)) / SR
    i0, i1 = max(0, _n(hit - pre)), min(len(y), _n(hit + t1))
    pk = float(np.max(np.abs(y[i0:i1])))
    if pk <= 0:
        return y
    s = SJ.shape(y / pk, drive) * pk
    w = np.clip((t - (hit - pre)) / 0.002 + 1.0, 0, 1) * np.clip(1.0 - (t - (hit + t1)) / xf, 0, 1)
    w = (0.5 - 0.5 * np.cos(np.pi * w))[:, None]
    m0 = A.momentary_max(y)
    lo, hi = 0.01, 1.0
    for _ in range(36):
        k = math.sqrt(lo * hi)
        z = y * (1 - w) + s * k * w
        if A.momentary_max(z) > m0:
            hi = k
        else:
            lo = k
    return y * (1 - w) + s * lo * w


def _place_cues(cs, M, drop0, vary=True):
    """Render cues into pre/post-drop-out buses (dry, send) of length M; returns buses + placement report."""
    from audio import _render_cue, _add, _CAT_SEND
    bus = {k: np.zeros((M, 2)) for k in ('pre', 'post', 'pre_send', 'post_send')}
    placed, counts = [], {}
    for c in sorted(cs, key=lambda c: float(c['t'])):
        k = (c['name'], A._key(c['params']))
        counts[k] = counts.get(k, -1) + 1
        y, hit = _render_cue(c, (counts[k] % 4) if vary else None)
        if c.get('sat'):
            y = sat_transient(y, hit, float(c['sat']))
        start = float(c['t']) - (hit if c['align'] == 'hit' else 0.0)
        if c.get('carve'):
            y = y * carve_env(len(y), start, c['carve'], float(c['carve_db']))[:, None]
        side = 'pre' if (drop0 is not None and start < drop0) else 'post'
        _add(bus[side], y, start)
        cat = A.SOUNDS[c['name']]['category']
        sdb = c.get('send_db', A.SOUNDS[c['name']]['send'] if A.SOUNDS[c['name']]['send'] is not None
                    else _CAT_SEND[cat])
        if sdb is not None and sdb > -60:
            _add(bus[side + '_send'], y * undb(sdb), start)
        placed.append(dict(t=float(c['t']), name=c['name'], start=round(start, 4), hit=round(start + hit, 4),
                           end=round(start + len(y) / SR, 4), len=round(len(y) / SR, 3), gain_db=round(c['gain_db'], 2),
                           duck_db=c.get('duck_db', 0.0), bus=side, why=c.get('why', ''), vo=c.get('vo', ''),
                           params=c['params'], lp=c.get('lp'), hp=c.get('hp'), pan=c.get('pan', 0.0),
                           align=c['align'], cue_dur=c.get('dur'),
                           warn='hit before 0 s' if (start < -1e-3 and start + hit < 0) else ''))
    return bus, placed


def gate_curve(M, t0, fade=GATE_FADE):
    """1 before t0 - fade, raised-cosine to 0 at t0, 0 after (the pre-drop-out world stops dead)."""
    t = np.arange(M) / SR
    g = np.ones(M)
    u = np.clip((t - (t0 - fade)) / fade, 0.0, 1.0)
    g = 0.5 * (1 + np.cos(np.pi * u))
    g[t >= t0] = 0.0
    return g


def mix_loop(cues_, dur=DUR, *, target_lufs=TARGET_LUFS, tp_ceiling=TP_CEILING, drop=DROP, wrap=True, room_send=True,
             glue=True, auto_duck=True, vary=True, fixed=None, verbose=True):
    """audio.mix chain + drop-out gate + circular tails (see module docstring). fixed = (g_fx, G, ceil) from another
    mix_loop run (hook B uses A's gains so its body is A's to the sample). Returns a report dict like audio.mix
    (+ 'gains', 'audio')."""
    Nn = _n(dur)
    M = Nn + (_n(WRAP_TAIL) if wrap else 0)
    cs = [A._norm_cue(c) for c in cues_]
    if auto_duck and cs:
        cs = A.duck_under(cs)
    bus, placed = _place_cues(cs, M, drop[0] if drop else None, vary)
    fx = np.zeros((M, 2))
    for side in ('pre', 'post'):
        x = bus[side]
        if room_send and np.any(bus[side + '_send']):
            x = x + A.reverb(bus[side + '_send'], 'studio', wet_db=0.0, dry=0.0)[:M]
        if side == 'pre' and drop:
            x = x * gate_curve(M, drop[0])[:, None]
        fx += x
    if wrap:
        out = fx[:Nn].copy()
        tail = fx[Nn:]
        k = 0
        while k < len(tail):                    # fold every DUR-long chunk of the tail back onto the start
            seg = tail[k:k + Nn]
            out[:len(seg)] += seg
            k += Nn
        fx = out
    else:
        fx = fx[:Nn]
    # ---- the audio.mix gain staging: fx to target, glue 2:1 at target + 8, then G + true-peak limiter
    g_fx = fixed[0] if fixed else (undb(target_lufs - A.loudness(fx)) if np.any(fx) else 1.0)
    fx = fx * g_fx
    gr_comp = np.zeros(Nn)
    if glue and np.any(fx):
        gr_comp = A.compressor_gain(fx, thresh_db=target_lufs + 8.0, ratio=2.0)
        fx = fx * undb(gr_comp)[:, None]
    pk = A.tp_envelope(fx)

    def _eval(G, ceil):
        gl = A.limiter_gain(None, ceil, pk=pk * undb(G))
        y = fx * (undb(G) * gl)[:, None]
        return y, gl, A.loudness(y)

    if fixed:
        G, ceil = fixed[1], fixed[2]
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
    glc = A.db(np.maximum(gl, 1e-9))
    for p in placed:
        i0, i1 = max(0, _n(p['hit'] - 0.01)), min(Nn, _n(p['hit'] + 0.15))
        p['limiter_gr_db'] = round(float(-glc[i0:i1].min()), 2) if i1 > i0 else 0.0
        p['glue_gr_db'] = round(float(-gr_comp[i0:i1].min()), 2) if i1 > i0 else 0.0
    for p in placed:
        if p['end'] > dur + 0.01:
            p['warn'] = (p['warn'] + '; ' if p['warn'] else '') + ('tail wrapped to 0 s' if wrap else 'tail cut at end')
    rep = dict(dur=dur, cues=len(cs), integrated_lufs=round(A.loudness(y), 2), true_peak_dbtp=round(A.true_peak(y), 2),
               sample_peak_dbfs=round(float(A.db(np.max(np.abs(y)))), 2), lra_lu=round(A.loudness_range(y), 2),
               max_momentary_lufs=round(A.momentary_max(y), 2), max_short_term_lufs=round(A.momentary_max(y, 3.0), 2),
               limiter_max_gr_db=round(max(0.0, float(-A.db(np.min(gl)))), 2),
               limiter_max_gr_at_s=round(float(np.argmin(gl)) / SR, 4),
               comp_max_gr_db=round(float(-np.min(gr_comp)), 2),
               limiter_pct_over_1db=round(100.0 * float(np.mean(gl < undb(-1.0))), 2),
               bed=[], bed_lufs=None, placed=placed, files={}, gains=(float(g_fx), float(G), float(ceil)),
               drop=list(drop) if drop else None, wrap=wrap)
    rep['audio'] = y.astype(np.float32)
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
        return {k: _jsonable(v) for k, v in o.items() if k != 'audio'}
    if isinstance(o, (list, tuple)):
        return [_jsonable(v) for v in o]
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    return o


def build(hooks='AB', out_dir=AUD):
    os.makedirs(out_dir, exist_ok=True)
    res = {}
    ca, fa = cues('A', report=True)
    ra = mix_loop(ca)
    p = os.path.join(out_dir, MODULE + '_sfx_stem.wav')
    ra['files']['stem'] = A._write_wav(p, ra['audio'], 24)
    A.mix_overview(ra, os.path.join(out_dir, MODULE + '_sfx_overview.png'), MODULE + ' SFX (A)')
    ra['ebur128'] = _ebur128(p)
    ra['fit_under_vo'] = fa
    res['A'] = ra
    if 'B' in hooks:
        cb, fb = cues('B', report=True)
        rb = mix_loop(cb, fixed=ra['gains'])
        p = os.path.join(out_dir, MODULE + '_hookb_sfx_stem.wav')
        rb['files']['stem'] = A._write_wav(p, rb['audio'], 24)
        A.mix_overview(rb, os.path.join(out_dir, MODULE + '_hookb_sfx_overview.png'), MODULE + ' SFX (hook B)')
        rb['ebur128'] = _ebur128(p)
        rb['fit_under_vo'] = fb
        d = np.abs(ra['audio'].astype(np.float64) - rb['audio'].astype(np.float64)).max(1)
        nz = np.nonzero(d > 2 ** -23)[0]
        rb['body_vs_A'] = dict(last_differing_sample_s=round(float(nz[-1]) / SR, 4) if len(nz) else None,
                               max_abs_after_3s=float(d[_n(SPLICE):].max()),
                               note='A and B differ after 3.0 s only by the tails of the hook-A cues (whoosh_slow at '
                                    '2.4 s runs to ~5.5 s) and their room sends; the music module splices B (< 3.0 s) '
                                    'onto A (>= 3.0 s)')
        res['B'] = rb
    json.dump(_jsonable(dict(module=MODULE, dur=DUR, events=events(), tuned=_TUNED,
                             A=dict(cues=ca), B=dict(cues=res['B']['placed']) if 'B' in res else None)),
              open(os.path.join(out_dir, MODULE + '_cues.json'), 'w'), indent=1)
    json.dump(_jsonable(res), open(os.path.join(out_dir, MODULE + '_sfx_report.json'), 'w'), indent=1)
    return res


# ================================================================================================ rough mix + QA
def rough(out_dir=ROUGH):
    """Final chain on the real inputs (music-supervisor's ek_frame_ki_keemat_music.mix: epic_mix.mix_reel, A and B, hook-B
    splice) into out_dir, then the BRIEF 18 "Sound" measurements."""
    import ek_frame_ki_keemat_music as MM
    os.makedirs(out_dir, exist_ok=True)
    # The FINAL VO stems are mono; audio.read_wav returns them as (N, 1), audio._st passes 2-D arrays through and
    # epic_mix.mix_reel's np.concatenate with a (n, 2) zero block raises (SHARED_REQUESTS R7). Workaround: dual-mono
    # stereo copies (identical samples in L and R) in a temporary folder, deleted afterwards.
    tmp = os.path.join(out_dir, '_vo_stereo')
    os.makedirs(tmp, exist_ok=True)
    vo2 = {}
    for k, src in (('A', VO_A), ('B', VO_B)):
        x, sr = A.read_wav(src)
        assert sr == SR
        x = np.asarray(x, dtype=np.float64).reshape(len(x), -1)
        if x.shape[1] == 1:
            x = np.repeat(x, 2, axis=1)
        vo2[k] = A._write_wav(os.path.join(tmp, 'vo_%s.wav' % k), x, 24)
    try:
        rep = MM.mix(hook='B', vo=vo2['A'], sfx=STEM_A, music=MUSIC, vo_b=vo2['B'], sfx_b=STEM_B, out_dir=out_dir)
    finally:
        for f in os.listdir(tmp):
            os.remove(os.path.join(tmp, f))
        os.rmdir(tmp)
    rep['inputs'] = dict(vo=VO_A, vo_b=VO_B, sfx=STEM_A, sfx_b=STEM_B, music=MUSIC, note='VO fed as dual-mono stereo')
    rep['measure'] = measure(out_dir)
    json.dump(_jsonable(rep), open(os.path.join(out_dir, MODULE + '_rough_report.json'), 'w'), indent=1)
    return rep


def _rms_db(x, t0, t1):
    a = A._st(x)[_n(t0):_n(t1)]
    return float(10 * np.log10(np.mean(np.square(a)) + 1e-30))


def _curve(x, win=0.4, hop=0.01):
    return A.loudness_curve(x, win, hop)


def measure(out_dir=ROUGH):
    P = lambda s: os.path.join(out_dir, MODULE + s)
    mixA = A._st(A.read_wav(P('_mix.wav'))[0])
    vosfx = A._st(A.read_wav(P('_vo_sfx.wav'))[0])
    v = A._st(A.read_wav(P('_stem_vo.wav'))[0])
    s = A._st(A.read_wav(P('_stem_sfx.wav'))[0])
    m = A._st(A.read_wav(P('_stem_music.wav'))[0])
    words = json.load(open(VO_A_WORDS))
    out = {}
    out['ebur128'] = {k: _ebur128(P(k2)) for k, k2 in (('A_mix', '_mix.wav'), ('B_vo_sfx', '_vo_sfx.wav'),
                                                       ('hookB_mix', '_hookb_mix.wav'),
                                                       ('hookB_vo_sfx', '_hookb_vo_sfx.wav'))}
    # VO clarity on voiced frames (400 ms momentary, 10 ms hop): words padded 0 s, frames whose centre is in a word
    tt, lv = _curve(v)
    _, ls = _curve(s)
    _, lm = _curve(m)
    voiced = np.zeros(len(tt), bool)
    for w in words:
        voiced |= (tt >= w['start']) & (tt <= w['end'])
    voiced &= lv > lv.max() - 20
    dvs, dvm = (lv - ls)[voiced], (lv - lm)[voiced]
    worst = np.argsort(dvs)[:5]
    out['vo_over_sfx_lu'] = dict(median=round(float(np.median(dvs)), 1), p10=round(float(np.percentile(dvs, 10)), 1),
                                 min=round(float(dvs.min()), 1),
                                 worst_frames=[(round(float(tt[voiced][i]), 2), round(float(dvs[i]), 1)) for i in worst],
                                 pct_below_6=round(100.0 * float(np.mean(dvs < 6.0)), 1))
    out['vo_over_music_lu'] = dict(median=round(float(np.median(dvm)), 1), p10=round(float(np.percentile(dvm, 10)), 1),
                                   min=round(float(dvm.min()), 1))
    # drop-out and the held breath
    out['dropout'] = dict(
        mix_f774_f781_rms_dbfs=round(_rms_db(mixA, F(774), F(782)), 1),
        sfx_f774_f781_peak=float(np.max(np.abs(s[_n(F(774)):_n(F(782))]))),
        music_f774_f781_peak=float(np.max(np.abs(m[_n(F(774)):_n(F(782))]))),
        vo_f774_f781_peak=float(np.max(np.abs(v[_n(F(774)):_n(F(782))]))),
        first_sfx_sample_after_25p8=round(float(_n(25.8) + np.argmax(np.abs(s[_n(25.8):]).max(1) > 0)) / SR, 4),
        first_music_sample_after_25p8=round(float(_n(25.8) + np.argmax(np.abs(m[_n(25.8):]).max(1) > 0)) / SR, 4),
        mix_f782_f791_rms_dbfs=round(_rms_db(mixA, F(782), F(792)), 1),
        mix_f792_f800_rms_dbfs=round(_rms_db(mixA, F(792), F(801)), 1))
    # loudest moment
    for k, x in (('A_mix', mixA), ('B_vo_sfx', vosfx)):
        t2, l2 = _curve(x)
        i = int(np.argmax(l2))
        out['max_momentary_' + k] = dict(lufs=round(float(l2[i]), 2), window_centre=round(float(t2[i]), 3),
                                         window=(round(float(t2[i]) - 0.2, 3), round(float(t2[i]) + 0.2, 3)),
                                         contains_26p4=bool(t2[i] - 0.2 <= 26.4 <= t2[i] + 0.2),
                                         centre_minus_26p4=round(float(t2[i]) - 26.4, 3))
        # second-highest region outside the reveal
        far = np.abs(t2 - 26.6) > 0.8
        j = int(np.argmax(np.where(far, l2, -200)))
        out['max_momentary_' + k]['best_outside_reveal'] = (round(float(t2[j]), 2), round(float(l2[j]), 2))
    # phone check at the reveal (momentary max in 26.2-27.0)
    ph = A.hp(mixA, 250.0, 4)
    seg = lambda x: x[_n(26.2):_n(27.0)]
    out['phone_check_reveal_loss_db'] = round(A.momentary_max(seg(mixA)) - A.momentary_max(seg(ph)), 2)
    # the 0.3 s pause click inside V1A: SFX stem vs VO stem, 2-9 kHz, 5 ms windows around the click
    def band_pk(x, t0, t1):
        y = A.bp(A._st(x).mean(1)[_n(t0 - 0.05):_n(t1 + 0.05)], 2000.0, 9000.0)
        y = y[_n(0.05):len(y) - _n(0.05)]
        return float(20 * np.log10(np.max(np.abs(y)) + 1e-12))
    out['pause_click_0p3'] = dict(sfx_2to9k_peak_dbfs=round(band_pk(s, 0.299, 0.31), 1),
                                  vo_2to9k_peak_dbfs_same_window=round(band_pk(v, 0.299, 0.31), 1),
                                  vo_2to9k_peak_dbfs_word_Aap=round(band_pk(v, 0.10, 0.329), 1),
                                  mix_2to9k_jump_db=round(band_pk(mixA, 0.299, 0.31) - band_pk(mixA, 0.27, 0.297), 1))
    # loop seam (mix A)
    out['loop'] = dict(last_50ms_rms_dbfs=round(_rms_db(mixA, DUR - 0.05, DUR), 1),
                       first_50ms_rms_dbfs=round(_rms_db(mixA, 0.0, 0.05), 1),
                       seam_step=round(float(np.max(np.abs(mixA[0] - mixA[-1]))), 5),
                       median_step=round(float(np.median(np.abs(np.diff(mixA, axis=0)).max(1))), 5),
                       p99_step=round(float(np.percentile(np.abs(np.diff(mixA, axis=0)).max(1), 99)), 5))
    return out


def onsets(x, cues_placed, names=None, win=0.06):
    """Measured onset near each placed hit: first sample whose 2 ms RMS envelope is >= 9 dB over the mean envelope of
    the 20 ms before it (searched within +-win of the hit) -> error in ms."""
    y = A._st(x).mean(1)
    k = _n(0.002)
    env = np.sqrt(np.convolve(y * y, np.ones(k) / k, 'same')) + 1e-9
    cs = np.concatenate([[0.0], np.cumsum(env)])
    a, b = _n(0.021), _n(0.001)
    out = []
    for p in cues_placed:
        if names and p['name'] not in names:
            continue
        h = p['hit'] if p['align'] == 'hit' else p['start']
        i0, i1 = max(_n(h - win), a), min(_n(h + win), len(y) - 1)
        if i1 <= i0:
            continue
        idx = np.arange(i0, i1)
        ref = (cs[idx - b] - cs[idx - a]) / (a - b)
        hitmask = env[idx] > ref * 2.82
        best = int(idx[np.argmax(hitmask)]) if hitmask.any() else None
        out.append(dict(name=p['name'], t=p['t'], hit=h, onset=None if best is None else round(best / SR, 4),
                        err_ms=None if best is None else round((best / SR - h) * 1000, 1)))
    return out


def verify():
    """(1) mix_loop == audio.mix on the same cues when the gate and the wrap are off (chain equivalence);
    (2) the stems: format, loudness, TP, drop-out silence, loop seam, hook-B body identity, hero onsets."""
    rep = {}
    ca = cues('A')
    ref = A.mix(ca, DUR, None, None, target_lufs=TARGET_LUFS, tp_ceiling=TP_CEILING, tail_fade=0.0, verbose=False)
    mine = mix_loop(ca, drop=None, wrap=False, verbose=False)
    r64, m64 = ref['audio'].astype(np.float64), mine['audio'].astype(np.float64)
    d = np.abs(r64 - m64)
    kk = float(np.sum(r64 * m64) / np.sum(r64 * r64))
    res = m64 - kk * r64
    rep['equivalence_vs_audio_mix'] = dict(max_abs=float(d.max()), max_abs_dbfs=round(float(20 * np.log10(d.max() + 1e-12)), 1),
                                           gain_ratio_db=round(20 * math.log10(kk), 3),
                                           residual_after_gain_db_re_rms=round(float(10 * np.log10(np.mean(res ** 2) /
                                                                                              np.mean(m64 ** 2))), 1),
                                           ref_I=ref['integrated_lufs'], mine_I=mine['integrated_lufs'],
                                           ref_TP=ref['true_peak_dbtp'], mine_TP=mine['true_peak_dbtp'])
    xa, sr = A.read_wav(STEM_A)
    xb, srb = A.read_wav(STEM_B)
    xa, xb = A._st(xa), A._st(xb)
    rep['format'] = dict(sr=(sr, srb), samples=(len(xa), len(xb)), expect=N)
    rep['A'] = dict(I=round(A.loudness(xa), 2), TP=round(A.true_peak(xa), 2), ebur128=_ebur128(STEM_A),
                    drop_f774_f781_peak=float(np.max(np.abs(xa[_n(F(774)):_n(F(782))]))),
                    silence_from=None, silence_to=None)
    nz = np.abs(xa).max(1) > 0
    i = _n(25.7)
    while i < len(xa) and nz[i]:
        i += 1
    j = i
    while j < len(xa) and not nz[j]:
        j += 1
    rep['A']['silence_from'], rep['A']['silence_to'] = round(i / SR, 5), round(j / SR, 5)
    rep['A']['last_50ms_rms_dbfs'] = round(_rms_db(xa, DUR - 0.05, DUR), 1)
    rep['A']['first_50ms_rms_dbfs'] = round(_rms_db(xa, 0.0, 0.05), 1)
    rep['B'] = dict(I=round(A.loudness(xb), 2), TP=round(A.true_peak(xb), 2), ebur128=_ebur128(STEM_B),
                    body_max_abs_diff_from_3p5=float(np.max(np.abs(xa[_n(3.5):] - xb[_n(3.5):]))),
                    at_splice_max_abs_diff_2p9_3p1=float(np.max(np.abs(xa[_n(2.9):_n(3.1)] - xb[_n(2.9):_n(3.1)]))))
    placed = mix_loop(ca, verbose=False)['placed']
    heroes = ('impact_soft', 'jd_mouse_click', 'glass_tap', 'impact_big', 'whip', 'jd_ui_click', 'toggle_on', 'air_zoom')
    rep['onsets'] = onsets(xa, placed, heroes)
    return rep


# ================================================================================================ CLI
def _table(cs):
    rows = []
    for c in sorted(cs, key=lambda c: c['t']):
        rows.append('%7.3f  f%-6s %-16s %+6.1f dB  %-5s %-34s %s%s%s' % (
            c['t'], '%.1f' % (c['t'] * FPS), c['name'], c['gain_db'], c.get('align', 'hit'),
            json.dumps(c['params'])[:34], c.get('why', ''),
            ('  [VO: %s]' % c['vo']) if c.get('vo') else '', ('  [%s]' % c['span_note']) if c.get('span_note') else ''))
    return '\n'.join(rows)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('cmd', choices=('cues', 'build', 'rough', 'verify'))
    ap.add_argument('--hook', default='A', choices=('A', 'B'))
    a = ap.parse_args()
    if a.cmd == 'cues':
        cs, rep = cues(a.hook, report=True)
        print(_table(cs))
        print('heroes ok:', rep['heroes_ok'])
        print('ducked:', len(rep['ducked']), ' spans:', rep['spans'])
        print('instants > 1:', [[(round(t, 3), n) for t, n in g] for g in instants(cs) if len(g) > 1])
    elif a.cmd == 'build':
        r = build()
        print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk not in ('placed', 'fit_under_vo', 'audio')}
                          for k, v in r.items()}, indent=1, default=str))
    elif a.cmd == 'rough':
        r = rough()
        print(json.dumps(_jsonable({k: v for k, v in r.items()}), indent=1, default=str))
    else:
        print(json.dumps(_jsonable(verify()), indent=1, default=str))
