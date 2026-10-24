"""grp2_audio.py: sound for the Google Ranker Pro testimonial set (grp2_of, grp2_leam, grp2_york, grp2_golden,
grp2_coventry, grp2_zentro).

    cd pipeline/fostering && python3 grp2_audio.py of|leam|york|golden|coventry|zentro|all

Writes workspace3/audio/grp2/<name>_mix.wav (48 kHz 24-bit, -14 LUFS integrated, <= -2 dBTP) plus stems.

DIALOGUE  the clip's own sound (Seedance voice), cleaned like grp_audio.dialogue: 80 Hz high-pass, low-mid dip,
          presence + air, 2.5:1 compression, peak taming, -16 LUFS; faded out after the last word. grp2_of cuts
          the garbled phrase (source 15.85-17.16 s) exactly as the picture does (20 ms crossfade at quiet points).
SFX       each module's cues() through audio.mix, -7 dB under the dialogue.
MUSIC     original beds composed with music_synth (no samples): one shared arranger (bed()) with a different key,
          tempo and colour per client; sparse before the turn in the story, a lift where Google Ranker Pro comes
          in, fuller for the results, a resolve and sting on the end card. Ducked under the dialogue by
          music_synth.render_bed and mastered by master_withmusic.
"""
import os
import subprocess
import sys
import time

import numpy as np

import audio as A
import core as K
import music_synth as M

OUT = os.path.join(K.WS, 'audio', 'grp2')
SR = A.SR
SRC = '/tmp/claude-0/-home-user-100/753dbccd-034a-5c54-a3a6-3c1d83ca4518/scratchpad/edit2/src'
CLIPS = {'of': 'hf_20261024_062502', 'leam': 'hf_20261024_062503', 'york': 'hf_20261024_063833',
         'golden': 'hf_20261024_072608', 'coventry': 'hf_20261024_074103', 'zentro': 'hf_20261024_074729'}
# fade the production sound after the last word: (start, end) in output seconds
FADE = {'of': (28.36, 28.62), 'leam': (29.02, 29.3), 'york': (18.72, 19.0), 'golden': (24.86, 25.0),
        'coventry': (29.8, 30.0), 'zentro': (22.36, 22.8)}
# dips (start, end, dB) on the production sound: generated background babble with no on-screen speaker
DIP = {'coventry': [(7.85, 10.85, -12.0)]}
# remap cuts (output t, source offset) as in the picture
REMAP = {'of': [(15.85, 1.31)]}

# music plan per edit: bpm, progression before / after the turn, turn time, 'full' time, end card time, final
# chord, colour, optional strip-back window
PLAN = {
    'of': dict(bpm=72, a=['Dm7', 'Bbmaj7', 'Fadd9/A', 'Csus4'], b=['F', 'C/E', 'Dm7', 'Bbmaj7'], lift=10.0,
               full=15.85, end=28.6, fin=('F', 'maj9'), colour='tender', strip=(24.3, 28.6)),
    'leam': dict(bpm=120, a=['D', 'A/C#', 'Bm7', 'Gmaj7'], b=['D', 'A/C#', 'Bm7', 'Gmaj7'], lift=7.79,
                 full=16.5, end=29.3, fin=('D', 'add9'), colour='drive'),
    'york': dict(bpm=90, a=['Gmaj7', 'Em7', 'Cmaj7', 'Dsus4'], b=['G', 'D/F#', 'Em7', 'Cmaj7'], lift=9.04,
                 full=12.06, end=19.0, fin=('G', 'add9'), colour='warm'),
    'golden': dict(bpm=100, a=['Am7', 'Fmaj7', 'Dm7', 'E7sus4'], b=['C', 'G/B', 'Am7', 'Fmaj7'], lift=11.2,
                   full=16.25, end=25.0, fin=('C', 'maj9'), colour='bright'),
    'coventry': dict(bpm=96, a=['E', 'B/D#', 'C#m7', 'Amaj7'], b=['E', 'B/D#', 'C#m7', 'Amaj7'], lift=7.67,
                     full=23.08, end=30.0, fin=('E', 'add9'), colour='drive'),
    'zentro': dict(bpm=108, a=['Bb', 'F/A', 'Gm7', 'Ebmaj7'], b=['Bb', 'F/A', 'Gm7', 'Ebmaj7'], lift=5.33,
                   full=14.92, end=22.8, fin=('Bb', 'add9'), colour='light'),
}


def load(path):
    r = A.read_wav(path)
    x = r[0] if isinstance(r, tuple) else r
    return np.asarray(x, np.float64)


def fit(x, n):
    return M.fit(A._st(x), n)


# ---------------------------------------------------------------------------------------------- dialogue
def raw_dialogue(name):
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, '%s_dialogue_raw.wav' % name)
    if not os.path.exists(p):
        src = [f for f in os.listdir(SRC) if f.startswith(CLIPS[name]) and f.endswith('.mp4')][0]
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(SRC, src), '-vn', '-ac', '2', '-ar',
                        str(SR), '-c:a', 'pcm_s24le', p], check=True)
    return load(p)


def remap(x, cuts, xf=0.02):
    """Apply picture remap cuts to audio: at output t_out jump the source forward by off (short crossfade)."""
    for t_out, off in cuts:
        a = int(t_out * SR)
        b = int((t_out + off) * SR)
        n = int(xf * SR)
        head, tail = x[:a + n], x[b:]
        w = np.linspace(0, 1, n)[:, None]
        mid = head[-n:] * (1 - w) + tail[:n] * w
        x = np.concatenate([head[:-n], mid, tail[n:]], 0)
    return x


def dialogue(name, dur):
    x = raw_dialogue(name)
    if name in REMAP:
        x = remap(x, REMAP[name])
    mono = x.mean(1)
    y = A.hp(mono, 80.0, 2)
    y = A.eq(y, 'peak', 240.0, 1.0, -1.5)
    y = A.eq(y, 'peak', 3500.0, 0.9, 2.0)
    y = A.eq(y, 'hs', 9500.0, 0.7, 1.5)
    st = np.stack([y, y], 1)
    st = M.bus_comp(st, thresh_db=-24.0, ratio=2.5, knee_db=6.0, attack=0.006, release=0.12)
    n = int(round(dur * SR))
    st = fit(st, n)
    a, b = int(FADE[name][0] * SR), int(FADE[name][1] * SR)
    env = np.ones(n)
    env[a:b] = np.cos(np.linspace(0, np.pi / 2, b - a)) ** 2
    env[b:] = 0.0
    for d0, d1, db in DIP.get(name, ()):
        r = int(0.05 * SR)
        a, b = int(d0 * SR), int(d1 * SR)
        g = np.ones(n)
        g[a:b] = A.undb(db)
        g[a - r:a] = np.linspace(1, A.undb(db), r)
        g[b:b + r] = np.linspace(A.undb(db), 1, r)
        env = env * g
    st *= env[:, None]
    st *= A.undb(-16.0 - A.loudness(st))
    gl = A.limiter_gain(None, -8.5, pk=A.tp_envelope(st))
    st = st * gl[:, None]
    st *= A.undb(-16.0 - A.loudness(st))
    return st


# ---------------------------------------------------------------------------------------------- music
def bed(dur, bpm, a, b, lift, full, end, fin, colour, strip=None, seed=3):
    g = M.Grid(float(bpm))
    T = {k: M.Track(dur) for k in ('pad', 'keys', 'col', 'bass', 'kick', 'perc', 'fx')}
    rng = np.random.default_rng(seed)
    hum = lambda: rng.uniform(-0.003, 0.003)            # noqa: E731
    pa = M.progression(a, octave=4, lo=57, hi=78)
    pb = M.progression(b, octave=4, lo=57, hi=78)
    nb = int(np.ceil(dur / g.bar_s))
    b_lift = None
    for bi in range(nb):
        t0 = g.bar(bi)
        if t0 >= end - 0.05:
            break
        after = t0 + g.bar_s * 0.5 >= lift
        if after and b_lift is None:
            b_lift = bi
        if not after:
            ch, sym = pa[bi % 4], a[bi % 4]
        else:
            k = (bi - b_lift) % 4
            ch, sym = pb[k], b[k]
        stripped = strip is not None and strip[0] <= t0 < strip[1]
        is_full = t0 >= full - 0.05 and not stripped
        cut = (800 if not after else 1300) + 40 * bi
        T['pad'].add(M.pad(ch, dur=g.bar_s, vel=0.55, attack=0.5 if bi == 0 else 0.3, release=1.1,
                           cutoff=cut, wave='warm' if colour in ('tender', 'warm') else 'saw', seed=bi), t0,
                     gain_db=-15)
        steps = 4 if (not after or stripped) else 8
        pat = [0, 2, 1, 3, 2, 1, 3, 2]
        for s in range(steps):
            nt = ch[pat[s] % len(ch)] + (12 if s in (3, 6) else 0)
            T['keys'].add(M.felt_piano(nt, dur=g.bar_s / steps * 0.9, vel=0.46 + 0.08 * (s % 2 == 0), pedal=True,
                                       tail=2.2), t0 + s * g.bar_s / steps + hum(), gain_db=-11, pan=-0.12)
        root = M.bass_note(sym, 2)
        if after and not stripped:
            T['bass'].add(M.sub_bass(root, dur=g.beat_s * 1.7, vel=0.72), t0, gain_db=-14)
            T['bass'].add(M.sub_bass(root, dur=g.beat_s * 1.2, vel=0.62), g.bar(bi, 2.5 if colour == 'drive' else 2),
                          gain_db=-15)
            T['kick'].add(M.soft_kick(vel=0.8, punch=0.4, tone=48 if colour == 'tender' else 50), t0,
                          gain_db=-8 if colour in ('drive', 'bright') else -10)
            T['kick'].add(M.soft_kick(vel=0.7, punch=0.35), g.bar(bi, 2.5 if colour == 'drive' else 2),
                          gain_db=-9 if colour in ('drive', 'bright') else -11)
            for q in range(4):
                T['perc'].add(M.hat(vel=0.42 + 0.1 * (q % 2)), g.bar(bi, q + 0.5), gain_db=-23, pan=0.25)
        if is_full:
            T['perc'].mix(M.shaker_pattern(1, float(bpm), swing=0.08, vel=0.45, seed=bi), t=t0, gain_db=-25)
            if colour in ('drive', 'bright'):
                T['perc'].add(M.clap(vel=0.6, seed=bi), g.bar(bi, 2) - 0.02, gain_db=-17)
                for s in range(8):
                    nt = ch[[0, 1, 2, 1, 3, 2, 1, 2][s] % len(ch)] + 12
                    T['col'].add(M.pluck_synth(nt, dur=g.beat_s * 0.35, vel=0.5 + 0.2 * (s % 4 == 0), cutoff=900.0),
                                 t0 + s * g.beat_s / 2, gain_db=-21, pan=0.3 * (-1) ** s)
            elif colour in ('tender', 'light', 'warm'):
                for q in range(8):
                    if q % 2 == 1:
                        nt = ch[(q // 2) % len(ch)] + 12
                        T['col'].add(M.marimba(nt, vel=0.5, hardness=0.4), t0 + q * g.beat_s / 2 + hum(),
                                     gain_db=-19, pan=0.3)
                T['col'].add(M.glockenspiel(ch[-1] + 12, vel=0.38), g.bar(bi, 1.5), gain_db=-23, pan=0.2)
    T['fx'].add(M.reverse_swell(1.2, vel=0.5, notes=pb[0]), lift - 1.2, gain_db=-21)
    if full - lift > 1.5:
        T['fx'].add(M.reverse_swell(1.0, vel=0.45, notes=pb[2]), full - 1.0, gain_db=-22)
    T['fx'].add(M.riser(1.5, vel=0.55, note=pb[0][0]), end - 1.5, gain_db=-21)
    T['fx'].add(M.impact_low(vel=0.7), end, gain_db=-16)
    fc = M.chord(fin[0], fin[1], octave=4)
    for k, nt in enumerate(fc):
        T['keys'].add(M.felt_piano(nt, dur=2.8, vel=0.52, pedal=True, tail=3.5), end + 0.014 * k, gain_db=-9)
    T['pad'].add(M.pad(fc, dur=3.0, vel=0.52, attack=0.06, release=1.4, cutoff=1500.0, seed=99), end, gain_db=-14)
    T['bass'].add(M.sub_bass(M.bass_note(fin[0], 2), dur=2.5, vel=0.72), end, gain_db=-15)
    T['col'].add(M.glockenspiel(fc[-1] + 12, vel=0.42), end + 0.05, gain_db=-21)
    music = T['pad'].buf + T['keys'].buf + T['col'].buf + T['bass'].buf
    music = M.duck(music, T['kick'].buf, depth_db=3.5, attack=0.004, release=0.18)
    sends = M.reverb_send(T['pad'].buf + T['keys'].buf, 'hall', wet_db=-14) + \
        M.reverb_send(T['col'].buf + T['perc'].buf, 'plate', wet_db=-16)
    mix = music + T['kick'].buf + T['perc'].buf + T['fx'].buf + sends
    mix = A.hp(mix, 30.0, 2)
    mix = M.bus_comp(mix, thresh_db=-16.0, ratio=1.8, attack=0.012, release=0.2)
    mix = M.fade_in(mix, 0.3)
    mix = M.fade_out(mix, 1.2)
    return M.normalise_peak(mix, -1.0, true_peak=False)


# ---------------------------------------------------------------------------------------------- build
def build(name):
    t0 = time.time()
    os.makedirs(OUT, exist_ok=True)
    mod = __import__('grp2_' + name)
    dur = float(mod.DUR)
    n = int(round(dur * SR))
    vo = dialogue(name, dur)
    rep = A.mix(mod.cues(), dur, out_wav=None, stem_wav=None, bed=None, target_lufs=-18.0, verbose=False)
    sfx = fit(rep['audio'], n) * A.undb(-7.0)
    p = PLAN[name]
    clean = fit(bed(dur, p['bpm'], p['a'], p['b'], p['lift'], p['full'], p['end'], p['fin'], p['colour'],
                    p.get('strip')), n)
    bd, meas = M.render_bed(clean, vo, sfx, mix_ref=vo + sfx, gap_lu=6.5, min_vo_lu=12.0, vo_duck_db=6.0,
                            vo_release=0.65)
    env = np.ones(n)
    a = int((p['end'] - 0.1) * SR)
    b = min(n, a + int(0.6 * SR))
    env[a:b] = np.linspace(1.0, A.undb(3.0), b - a)
    env[b:] = A.undb(3.0)
    bd = bd * env[:, None]
    mix, mrep = M.master_withmusic(vo, sfx, bd, target=-14.0, ceiling=-2.3, tp_max=-2.0)
    A._write_wav(os.path.join(OUT, '%s_mix.wav' % name), mix, bits=24)
    for k, v in mrep['stems'].items():
        A._write_wav(os.path.join(OUT, '%s_%s.wav' % (name, k)), v)
    print('%s: %.2f LUFS %.2f dBTP | music %s LUFS | vo-music %s LU | %.1fs' % (
        name, mrep['lufs'], mrep['true_peak'], mrep['music_lufs'], meas['vo_minus_music_lu'], time.time() - t0),
        flush=True)
    return os.path.join(OUT, '%s_mix.wav' % name)


if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'all'
    for nm in (list(PLAN) if which == 'all' else [which]):
        build(nm)
