"""grp3_audio.py: sound for the Nov 2026 Google Ranker Pro videos 7-10 (grp3_hamza, grp3_zentro, grp3_coventry,
grp3_grace). Same chain as grp2_audio: cleaned clip dialogue (-16 LUFS), each module's SFX cues (-7 dB under the
dialogue), an original synthesised music bed per video (ducked), mastered to -14 LUFS / <= -2 dBTP.

    cd pipeline/fostering && python3 grp3_audio.py hamza|zentro|coventry|grace|all
-> workspace3/audio/grp3/<name>_mix.wav
"""
import os
import sys
import time

import numpy as np

import audio as A
import core as K
import grp2_audio as G2
import music_synth as M

G2.OUT = os.path.join(K.WS, 'audio', 'grp3')
G2.SRC = '/home/user/100/google_ranker_pro_videos/raw2'
G2.CLIPS.update({'hamza': 'v7_hamza_selfie', 'zentro3': 'v8_zentro_position3', 'coventry3': 'v9_coventry_reaction',
                 'grace': 'v10_grace_team'})
G2.FADE.update({'hamza': (19.36, 19.58), 'zentro3': (29.52, 29.9), 'coventry3': (14.88, 15.0),
                'grace': (28.3, 28.7)})

KEY = {'hamza': 'hamza', 'zentro': 'zentro3', 'coventry': 'coventry3', 'grace': 'grace'}
PLAN = {
    'hamza': dict(bpm=104, a=['C', 'G/B', 'Am7', 'Fmaj7'], b=['C', 'G/B', 'Am7', 'Fmaj7'], lift=3.4, full=14.1,
                  end=19.6, fin=('C', 'add9'), colour='bright'),
    'zentro': dict(bpm=108, a=['Bb', 'F/A', 'Gm7', 'Ebmaj7'], b=['Bb', 'F/A', 'Gm7', 'Ebmaj7'], lift=13.2,
                   full=21.0, end=30.0, fin=('Bb', 'add9'), colour='light'),
    'coventry': dict(bpm=100, a=['E', 'B/D#', 'C#m7', 'Amaj7'], b=['E', 'B/D#', 'C#m7', 'Amaj7'], lift=4.54,
                     full=6.4, end=15.0, fin=('E', 'add9'), colour='drive'),
    'grace': dict(bpm=96, a=['Gmaj7', 'Em7', 'Cmaj7', 'Dsus4'], b=['G', 'D/F#', 'Em7', 'Cmaj7'], lift=9.6,
                  full=18.8, end=28.8, fin=('G', 'add9'), colour='warm'),
}


def build(name):
    t0 = time.time()
    os.makedirs(G2.OUT, exist_ok=True)
    mod = __import__('grp3_' + name)
    dur = float(mod.DUR)
    n = int(round(dur * A.SR))
    vo = G2.dialogue(KEY[name], dur)
    rep = A.mix(mod.cues(), dur, out_wav=None, stem_wav=None, bed=None, target_lufs=-18.0, verbose=False)
    sfx = G2.fit(rep['audio'], n) * A.undb(-7.0)
    p = PLAN[name]
    clean = G2.fit(G2.bed(dur, p['bpm'], p['a'], p['b'], p['lift'], p['full'], p['end'], p['fin'], p['colour'],
                          p.get('strip')), n)
    bd, meas = M.render_bed(clean, vo, sfx, mix_ref=vo + sfx, gap_lu=6.5, min_vo_lu=12.0, vo_duck_db=6.0,
                            vo_release=0.65)
    env = np.ones(n)
    a = int((p['end'] - 0.1) * A.SR)
    b = min(n, a + int(0.6 * A.SR))
    env[a:b] = np.linspace(1.0, A.undb(3.0), b - a)
    env[b:] = A.undb(3.0)
    bd = bd * env[:, None]
    mix, mrep = M.master_withmusic(vo, sfx, bd, target=-14.0, ceiling=-2.3, tp_max=-2.0)
    out = os.path.join(G2.OUT, '%s_mix.wav' % name)
    A._write_wav(out, mix, bits=24)
    print('%s: %.2f LUFS %.2f dBTP | music %s LUFS | vo-music %s LU | %.1fs' % (
        name, mrep['lufs'], mrep['true_peak'], mrep['music_lufs'], meas['vo_minus_music_lu'], time.time() - t0),
        flush=True)
    return out


if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'all'
    for nm in (list(PLAN) if which == 'all' else [which]):
        build(nm)
