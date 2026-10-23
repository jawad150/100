"""grp_audio.py: sound for the Google Ranker Pro client edits (grp_leam, grp_of).

    cd pipeline/fostering && python3 grp_audio.py leam|of|all

Writes workspace3/audio/grp/<edit>_mix.wav (48 kHz 24-bit, -14 LUFS integrated, <= -2 dBTP) plus the stems
(_dialogue, _sfx, _music) and an overview PNG. render.py muxes the mix with --audio.

DIALOGUE  the clip's own production sound (Seedance, effectively mono): 80 Hz high-pass for the low rumble, a small
          low-mid dip, presence and air lifts, gentle 2.5:1 compression, faded out after the last word.
SFX       cue lists from the edit modules' cues() -> audio.mix (pre-balanced procedural library), then -7 dB
          under the dialogue so they colour the graphics without competing with the words.
MUSIC     original beds composed here with music_synth (no samples, no downloads):
          Leam  120 BPM (half-time feel), D major I-V-vi-IV, piano + pad intro, kick / bass / plucks build at the
                monitor shot (8.0 s = bar 4), fuller from the selfie (17.0 s), resolve + logo sting at the end card.
          OF    72 BPM, F major, tender felt piano + warm pad for the problem (bars 0-2), lift at "Then we brought in
                Hulk Marketing" (10.0 s = bar 3) with marimba pulse and soft kick, fuller at the close-up (17.5 s),
                stripped back for "Honestly..." and a warm resolve on the end card.
          render_bed ducks the music 9 dB under the dialogue, 3 dB under the SFX, and sets its level 7 LU below
          the mix in the gaps; master_withmusic sums and masters to -14 LUFS / -2 dBTP.
"""
import os
import sys
import time

import numpy as np

import audio as A
import core as K
import music_synth as M

OUT = os.path.join(K.WS, 'audio', 'grp')
SR = A.SR


def load(path):
    r = A.read_wav(path)
    x = r[0] if isinstance(r, tuple) else r
    return np.asarray(x, np.float64)


def fit(x, n):
    return M.fit(A._st(x), n)


# ---------------------------------------------------------------------------------------------- dialogue
def dialogue(name, dur, fade_at):
    x = load(os.path.join(OUT, '%s_dialogue_raw.wav' % name))
    mono = x.mean(1)
    y = A.hp(mono, 80.0, 2)
    y = A.eq(y, 'peak', 240.0, 1.0, -1.5)
    y = A.eq(y, 'peak', 3500.0, 0.9, 2.0)
    y = A.eq(y, 'hs', 9500.0, 0.7, 1.5)
    st = np.stack([y, y], 1)
    st = M.bus_comp(st, thresh_db=-24.0, ratio=2.5, knee_db=6.0, attack=0.006, release=0.12)
    n = int(round(dur * SR))
    st = fit(st, n)
    # fade the production sound out after the last word (the end card runs on music only)
    a, b = int(fade_at[0] * SR), int(fade_at[1] * SR)
    env = np.ones(n)
    env[a:b] = np.cos(np.linspace(0, np.pi / 2, b - a)) ** 2
    env[b:] = 0.0
    st *= env[:, None]
    st *= A.undb(-16.0 - A.loudness(st))
    # tame the generated voice's transient peaks (about 3 dB on the loudest syllables) so the master
    # limiter has little left to do
    gl = A.limiter_gain(None, -8.5, pk=A.tp_envelope(st))
    st = st * gl[:, None]
    st *= A.undb(-16.0 - A.loudness(st))
    return st


# ---------------------------------------------------------------------------------------------- music: Leam
def music_leam(dur=33.0, seed=1):
    bpm = 120.0
    g = M.Grid(bpm)
    T = {k: M.Track(dur) for k in ('pad', 'keys', 'pluck', 'bass', 'kick', 'perc', 'fx')}
    syms = ['D', 'A/C#', 'Bm7', 'Gmaj7']
    prog = M.progression(syms, octave=4, lo=57, hi=78)
    rng = np.random.default_rng(seed)
    hum = lambda: rng.uniform(-0.003, 0.003)            # noqa: E731
    nb = int(np.ceil(dur / g.bar_s))
    for b in range(nb):
        t0 = g.bar(b)
        if t0 >= 29.5:
            break
        ch, sym = prog[b % 4], syms[b % 4]
        # pad all the way, filter opening across the edit
        cut = 700 + 90 * b
        T['pad'].add(M.pad(ch, dur=g.bar_s, vel=0.55, attack=0.5 if b == 0 else 0.25, release=0.9, cutoff=cut,
                           sweep=0.3, seed=b), t0, gain_db=-15)
        # felt piano: broken 8ths (sparser in the intro)
        pat = [0, 2, 1, 3, 2, 1, 3, 2]
        for k in range(8):
            if b == 0 and k % 2:
                continue
            nt = ch[pat[k] % len(ch)] + (12 if k in (3, 6) else 0)
            T['keys'].add(M.felt_piano(nt, dur=g.beat_s * 0.8, vel=0.48 + 0.08 * (k % 2 == 0), pedal=True, tail=2.0),
                          t0 + 0.5 * k * g.beat_s * 2 / 2 + hum(), gain_db=-11, pan=-0.12)
        root = M.bass_note(sym, 2)
        # build from the monitor shot (bar 4 = 8.0 s)
        if b >= 4:
            T['bass'].add(M.sub_bass(root, dur=g.beat_s * 1.7, vel=0.75), t0, gain_db=-13)
            T['bass'].add(M.sub_bass(root, dur=g.beat_s * 1.2, vel=0.65), g.bar(b, 2.5), gain_db=-14)
            T['kick'].add(M.soft_kick(vel=0.85, punch=0.45), t0, gain_db=-7)
            T['kick'].add(M.soft_kick(vel=0.75, punch=0.4), g.bar(b, 2.5), gain_db=-8)
            for q in range(4):
                T['perc'].add(M.hat(vel=0.45 + 0.1 * (q % 2)), g.bar(b, q + 0.5), gain_db=-22, pan=0.25)
        if b >= 8:                                         # selfie (17.0 s): fuller
            T['perc'].add(M.clap(vel=0.65, seed=b), g.bar(b, 2) - 0.02, gain_db=-16)
            T['perc'].mix(M.shaker_pattern(1, bpm, swing=0.08, vel=0.5, seed=b), t=t0, gain_db=-24)
            for s in range(8):
                nt = ch[[0, 1, 2, 1, 3, 2, 1, 2][s] % len(ch)] + 12
                T['pluck'].add(M.pluck_synth(nt, dur=g.beat_s * 0.35, vel=0.5 + 0.2 * (s % 4 == 0), cutoff=900.0),
                               t0 + 0.5 * s * g.beat_s * 2 / 2, gain_db=-21, pan=0.3 * (-1) ** s)
    # accents: riser into the monitor shot, swell on "and then here", riser + impact into the end card
    T['fx'].add(M.reverse_swell(1.2, vel=0.55, notes=prog[0]), 8.0 - 1.2, gain_db=-20)
    T['fx'].add(M.reverse_swell(1.0, vel=0.5, notes=prog[2]), 14.3 - 1.0, gain_db=-21)
    T['fx'].add(M.riser(1.6, vel=0.6, note=prog[0][0]), 29.5 - 1.6, gain_db=-20)
    T['fx'].add(M.impact_low(vel=0.75), 29.5, gain_db=-15)
    # end card: D add9 held, felt piano chord + pad + sub
    fin = M.chord('D', 'add9', octave=4)
    for k, nt in enumerate(fin):
        T['keys'].add(M.felt_piano(nt, dur=3.0, vel=0.55, pedal=True, tail=3.5), 29.5 + 0.012 * k, gain_db=-9)
    T['pad'].add(M.pad(fin, dur=3.2, vel=0.55, attack=0.05, release=1.4, cutoff=1500.0, seed=99), 29.5, gain_db=-14)
    T['bass'].add(M.sub_bass(M.bass_note('D', 2), dur=2.6, vel=0.75), 29.5, gain_db=-15)
    music = T['pad'].buf + T['keys'].buf + T['pluck'].buf + T['bass'].buf
    music = M.duck(music, T['kick'].buf, depth_db=4.0, attack=0.004, release=0.17)
    sends = M.reverb_send(T['pad'].buf + T['keys'].buf, 'hall', wet_db=-14) + \
        M.reverb_send(T['pluck'].buf + T['perc'].buf, 'plate', wet_db=-16)
    mix = music + T['kick'].buf + T['perc'].buf + T['fx'].buf + sends
    mix = A.hp(mix, 30.0, 2)
    mix = M.bus_comp(mix, thresh_db=-16.0, ratio=1.8, attack=0.012, release=0.2)
    mix = M.tilt_eq(mix, 0.8)
    mix = M.fade_in(mix, 0.25)
    mix = M.fade_out(mix, 1.2)
    return M.normalise_peak(mix, -1.0, true_peak=False)


# ---------------------------------------------------------------------------------------------- music: OF
def music_of(dur=33.0, seed=2):
    bpm = 72.0
    g = M.Grid(bpm)
    T = {k: M.Track(dur) for k in ('pad', 'keys', 'mar', 'bass', 'kick', 'perc', 'fx', 'glk')}
    rng = np.random.default_rng(seed)
    hum = lambda: rng.uniform(-0.004, 0.004)            # noqa: E731
    problem = ['Dm7', 'Bbmaj7', 'Fadd9/A', 'Csus4']        # bars 0-2 (0-10 s): softer, unresolved
    lift = ['F', 'C/E', 'Dm7', 'Bbmaj7']
    nb = int(np.ceil(dur / g.bar_s))
    pp = M.progression(problem, octave=4, lo=57, hi=77)
    pl = M.progression(lift, octave=4, lo=57, hi=77)
    for b in range(nb):
        t0 = g.bar(b)
        if t0 >= 30.0:
            break
        if b < 3:
            ch, sym = pp[b % 4], problem[b % 4]
        else:
            ch, sym = pl[(b - 3) % 4], lift[(b - 3) % 4]
        close = (26.3 <= t0 < 30.0)                         # "Honestly..." strip back
        T['pad'].add(M.pad(ch, dur=g.bar_s, vel=0.55, attack=0.8 if b == 0 else 0.35, release=1.2,
                           cutoff=900 + (500 if b >= 3 else 0), wave='warm', seed=b), t0, gain_db=-14)
        # felt piano: quarter-note broken chords (8ths from the lift)
        steps = 4 if (b < 3 or close) else 8
        pat = [0, 2, 1, 3, 2, 1, 3, 2]
        for k in range(steps):
            nt = ch[pat[k] % len(ch)] + (12 if k == 3 else 0)
            T['keys'].add(M.felt_piano(nt, dur=g.beat_s * (0.9 if steps == 4 else 0.5), vel=0.45 + 0.08 * (k % 2 == 0),
                                       pedal=True, tail=2.5), t0 + k * g.bar_s / steps + hum(), gain_db=-10, pan=-0.1)
        root = M.bass_note(sym, 2)
        if b >= 3 and not close:
            T['bass'].add(M.sub_bass(root, dur=g.beat_s * 1.8, vel=0.7), t0, gain_db=-14)
            T['bass'].add(M.sub_bass(root, dur=g.beat_s * 1.6, vel=0.6), g.bar(b, 2), gain_db=-15)
            for q in range(8):                               # marimba off-beat 8ths
                if q % 2 == 1:
                    nt = ch[(q // 2) % len(ch)] + 12
                    T['mar'].add(M.marimba(nt, vel=0.5, hardness=0.4), t0 + q * g.beat_s / 2 + hum(), gain_db=-19,
                                 pan=0.3)
        if t0 >= 17.4 and not close:                         # close-up results: soft kick + shaker + glock
            T['kick'].add(M.soft_kick(vel=0.75, punch=0.35, tone=48), t0, gain_db=-9)
            T['kick'].add(M.soft_kick(vel=0.65, punch=0.3, tone=48), g.bar(b, 2), gain_db=-10)
            T['perc'].mix(M.shaker_pattern(1, bpm, swing=0.1, vel=0.45, seed=b), t=t0, gain_db=-25)
            T['glk'].add(M.glockenspiel(ch[-1] + 12, vel=0.4), g.bar(b, 1.5), gain_db=-22, pan=0.2)
    T['fx'].add(M.reverse_swell(1.3, vel=0.5, notes=pl[0]), 10.0 - 1.3, gain_db=-21)
    T['fx'].add(M.reverse_swell(1.0, vel=0.45, notes=pl[0]), 17.5 - 1.0, gain_db=-22)
    T['fx'].add(M.riser(1.4, vel=0.5, note=pl[0][0]), 30.0 - 1.4, gain_db=-22)
    T['fx'].add(M.impact_low(vel=0.6), 30.0, gain_db=-17)
    fin = M.chord('F', 'maj9', octave=4)
    for k, nt in enumerate(fin):
        T['keys'].add(M.felt_piano(nt, dur=2.6, vel=0.5, pedal=True, tail=3.5), 30.0 + 0.015 * k, gain_db=-9)
    T['pad'].add(M.pad(fin, dur=2.8, vel=0.5, attack=0.1, release=1.5, cutoff=1500.0, wave='warm', seed=77), 30.0,
                 gain_db=-13)
    T['bass'].add(M.sub_bass(M.bass_note('F', 2), dur=2.4, vel=0.7), 30.0, gain_db=-16)
    T['glk'].add(M.glockenspiel(M.midi('F6'), vel=0.45), 30.0, gain_db=-20)
    music = T['pad'].buf + T['keys'].buf + T['mar'].buf + T['bass'].buf + T['glk'].buf
    music = M.duck(music, T['kick'].buf, depth_db=3.0, attack=0.004, release=0.2)
    sends = M.reverb_send(T['pad'].buf + T['keys'].buf + T['glk'].buf, 'hall', wet_db=-13) + \
        M.reverb_send(T['mar'].buf + T['perc'].buf, 'plate', wet_db=-16)
    mix = music + T['kick'].buf + T['perc'].buf + T['fx'].buf + sends
    mix = A.hp(mix, 30.0, 2)
    mix = M.bus_comp(mix, thresh_db=-16.0, ratio=1.7, attack=0.015, release=0.25)
    mix = M.fade_in(mix, 0.4)
    mix = M.fade_out(mix, 1.2)
    return M.normalise_peak(mix, -1.0, true_peak=False)


# ---------------------------------------------------------------------------------------------- build
def build(name):
    t0 = time.time()
    os.makedirs(OUT, exist_ok=True)
    mod = __import__({'leam': 'grp_leam', 'of': 'grp_of'}[name])
    dur = float(mod.DUR)
    n = int(round(dur * SR))
    fade = {'leam': (29.45, 29.95), 'of': (29.92, 30.04)}[name]
    vo = dialogue(name, dur, fade)
    rep = A.mix(mod.cues(), dur, out_wav=None, stem_wav=None, bed=None, target_lufs=-18.0, verbose=False)
    sfx = fit(rep['audio'], n) * A.undb(-7.0)
    clean = (music_leam if name == 'leam' else music_of)(dur)
    clean = fit(clean, n)
    bed, meas = M.render_bed(clean, vo, sfx, mix_ref=vo + sfx, gap_lu=6.5, min_vo_lu=12.0, vo_duck_db=6.0,
                             vo_release=0.65)
    # the end card has no dialogue: let the music come up to a proper level there
    tail0 = {'leam': 29.35, 'of': 29.95}[name]
    env = np.ones(n)
    a = int(tail0 * SR)
    b = min(n, a + int(0.6 * SR))
    env[a:b] = np.linspace(1.0, A.undb(3.0), b - a)
    env[b:] = A.undb(3.0)
    bed = bed * env[:, None]
    mix, mrep = M.master_withmusic(vo, sfx, bed, target=-14.0, ceiling=-2.3, tp_max=-2.0)
    A._write_wav(os.path.join(OUT, '%s_mix.wav' % name), mix, bits=24)
    for k, v in mrep['stems'].items():
        A._write_wav(os.path.join(OUT, '%s_%s.wav' % (name, k)), v)
    try:
        im = A.spectro_image(mix, 1800, 360, None, 'grp_%s mix  %.2f LUFS  %.2f dBTP' % (name, mrep['lufs'],
                                                                                     mrep['true_peak']), '')
        im.save(os.path.join(OUT, '%s_mix.png' % name))
    except Exception as e:                                   # overview is a nicety
        print('overview skipped:', e)
    print('%s: %.2f LUFS %.2f dBTP | music %s LUFS | vo-music %s LU | %.1fs' % (
        name, mrep['lufs'], mrep['true_peak'], mrep['music_lufs'], meas['vo_minus_music_lu'], time.time() - t0))
    return os.path.join(OUT, '%s_mix.wav' % name)


if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'all'
    for nm in (['leam', 'of'] if which == 'all' else [which]):
        build(nm)
