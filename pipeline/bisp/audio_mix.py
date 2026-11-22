"""BISP reel audio: cleaned presenter voice + original music bed + synced SFX -> -14 LUFS master and stems.

    python3 audio_mix.py            -> workspace_bisp/audio_out/{voice,music,sfx}_stem.wav, mix.wav

Voice: each clip runs through ffmpeg (high-pass 85 Hz, FFT denoise, -2.5 dB at 280 Hz to take out the room box,
+2.5 dB presence at 3.8 kHz, air shelf, de-esser, 2.8:1 compression), is loudness-matched per clip, then cut to the
edit (edl.SEGMENTS) with 12 ms fades at every cut.
Music: synthesised with pipeline/fostering/music_synth.py (no samples), G major, 100 BPM, I-V-vi-IV; sections
follow the story (hook lift, sparse minor "Pehle", bright "Ab" groove, a pulse-only "Zaroori hidayat",
the final build and a resolve on the end card). Kept low and dark under speech (low-pass + ducked).
SFX: pipeline/fostering/audio.py library, cue sheet = reel.sfx_cues() (same plan as the graphics).
"""
import os, sys, subprocess, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'fostering'))
import edl
import audio as A
import music_synth as M

SR = A.SR
WS = edl.WS
OUT = os.path.join(WS, 'audio_out')
os.makedirs(OUT, exist_ok=True)
TL = edl.timeline()
DUR = TL.dur
N = int(round(DUR * SR))

VOICE_CHAIN = ('highpass=f=85,afftdn=nr=10:nf=-44:tn=1,equalizer=f=280:t=q:w=1.2:g=-2.5,'
               'equalizer=f=3800:t=q:w=1.0:g=2.5,highshelf=f=9000:g=2,deesser=i=0.3,'
               'acompressor=threshold=-24dB:ratio=2.8:attack=6:release=140:makeup=3dB')


def clip_voice(clip):
    p = os.path.join(OUT, f'v_{clip}.wav')
    if not os.path.exists(p):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(WS, 'src', clip + '.MOV'), '-vn', '-ac', '1',
                        '-ar', str(SR), '-af', VOICE_CHAIN, '-c:a', 'pcm_f32le', p], check=True)
    import soundfile as sf
    x, _ = sf.read(p, dtype='float64')
    return x


def build_voice():
    clips = {}
    v = np.zeros(N)
    # per-clip loudness from the parts we use
    for s in TL.segs:
        if s['clip'] not in clips:
            clips[s['clip']] = clip_voice(s['clip'])
    gains = {}
    for c, x in clips.items():
        parts = [x[int(s['a'] * SR):int(s['b'] * SR)] for s in TL.segs if s['clip'] == c]
        L = A.loudness(np.concatenate(parts))
        gains[c] = A.undb(-17.0 - L)
    segs = TL.segs
    for j, s in enumerate(segs):
        x = clips[s['clip']][int(round(s['a'] * SR)):int(round(s['b'] * SR))] * gains[s['clip']]
        x = x.copy()
        # 12 ms fades at cuts between clips; 6 ms inside one take, so a cut within a sentence flows without a dip
        same_prev = j > 0 and segs[j - 1]['clip'] == s['clip']
        same_next = j + 1 < len(segs) and segs[j + 1]['clip'] == s['clip']
        fi, fo = int((0.006 if same_prev else 0.012) * SR), int((0.006 if same_next else 0.012) * SR)
        x[:fi] *= np.linspace(0, 1, fi); x[-fo:] *= np.linspace(1, 0, fo)
        i0 = int(round(s['t0'] * SR))
        n = min(len(x), N - i0)
        v[i0:i0 + n] += x[:n]
    return np.stack([v, v], -1), gains


# ---- music ----------------------------------------------------------------------------------------------------------
BPM = 100.0
G = M.Grid(BPM)


def sections():
    s = {x['id']: x for x in TL.segs}
    snap = lambda t: round(t / G.beat_s) * G.beat_s
    return [
        ('hook', 0.0, snap(s['wallets']['t0'])),
        ('main', snap(s['wallets']['t0']), snap(s['pehle']['t0'])),
        ('pehle', snap(s['pehle']['t0']), snap(s['ab']['t0'])),
        ('ab', snap(s['ab']['t0']), snap(s['steps_a']['t0'])),
        ('steps', snap(s['steps_a']['t0']), snap(s['hidayat']['t0'])),
        ('hidayat', snap(s['hidayat']['t0']), snap(s['crore']['t0'])),
        ('final', snap(s['crore']['t0']), snap(TL.speech_end)),
        ('end', snap(TL.speech_end), DUR),
    ]


PROG = {'major': ['G', 'D/F#', 'Em7', 'Cmaj7'], 'minor': ['Em', 'Cmaj7', 'Am7', 'D'],
        'hid': ['Am7', 'Em7', 'Cmaj7', 'D'], 'end': ['Cmaj7', 'D', 'G', 'G']}


def compose():
    keys, pad, bass, drums, arp, fx = (M.Track(DUR) for _ in range(6))
    secs = sections()
    voiced = {}
    for name, t0, t1 in secs:
        b0 = int(round(t0 / G.beat_s))
        b1 = int(round(t1 / G.beat_s))
        prog = PROG['minor'] if name == 'pehle' else PROG['hid'] if name == 'hidayat' else \
            PROG['end'] if name == 'end' else PROG['major']
        vl = M.progression(prog, octave=4)
        beat = b0
        while beat < b1:
            bar_i = (beat - b0) // 4
            ch_name = prog[bar_i % 4]
            ch = vl[bar_i % 4]
            t = beat * G.beat_s
            nb = min(4, b1 - beat)
            dur = nb * G.beat_s
            # pad: always, soft
            pad.add(M.pad(ch, dur=dur + 0.1, vel=0.5 if name != 'end' else 0.6, wave='warm', attack=0.5, release=1.2,
                          cutoff=1100 if name in ('pehle', 'hidayat') else 1500), t,
                    gain_db=-6 if name != 'hidayat' else -9)
            # bass
            bn = M.bass_note(ch_name, 2)
            if name not in ('pehle',):
                bass.add(M.sub_bass(bn, dur=G.beat_s * 1.8, vel=0.7), t, gain_db=-4)
                if nb > 2 and name not in ('hidayat', 'end'):
                    bass.add(M.sub_bass(bn, dur=G.beat_s * 1.6, vel=0.6), t + 2 * G.beat_s, gain_db=-6)
            else:
                bass.add(M.sub_bass(bn, dur=dur, vel=0.55), t, gain_db=-8)
            # piano: broken chord 8ths (gentle), sparse in pehle
            if name in ('main', 'ab', 'steps', 'final', 'hook'):
                pat = [0, 2, 1, 2, 0, 2, 1, 3] if name != 'hook' else [0, 1, 2, 3, 2, 1, 2, 3]
                for k in range(nb * 2):
                    n = ch[pat[k % 8] % len(ch)] + (12 if k % 4 == 3 else 0)
                    keys.add(M.felt_piano(n, dur=G.beat_s * 0.6, vel=0.42 if k % 2 else 0.5, seed=k),
                             t + k * G.beat_s / 2, gain_db=-8, pan=-0.15 + 0.3 * ((k % 4) / 3))
            elif name in ('pehle', 'end'):
                keys.add(M.felt_piano(ch[0] - 12, dur=dur, vel=0.45, pedal=True), t, gain_db=-7)
                keys.add(M.felt_piano(ch[-1], dur=dur, vel=0.35, pedal=True), t + G.beat_s, gain_db=-10)
            # drums
            if name in ('main', 'ab', 'steps', 'final'):
                for q in range(nb):
                    if q % 2 == 0:
                        drums.add(M.soft_kick(vel=0.75), t + q * G.beat_s, gain_db=-6)
                    for e8 in range(2):
                        drums.add(M.shaker(vel=0.5 if e8 else 0.35), t + q * G.beat_s + e8 * G.beat_s / 2,
                                  gain_db=-16, pan=0.3)
                if name == 'final':
                    for q in (1, 3):
                        if q < nb:
                            drums.add(M.clap(vel=0.55), t + q * G.beat_s, gain_db=-14)
            elif name == 'hidayat':
                for q in range(nb):
                    drums.add(M.soft_kick(vel=0.55, decay=0.2), t + q * G.beat_s, gain_db=-12)
            # bright pluck arp in the "Ab" + final sections
            if name in ('ab', 'final', 'hook'):
                for k in range(nb * 4):
                    n = ch[k % len(ch)] + 12
                    arp.add(M.pluck_synth(n, dur=0.12, vel=0.45, cutoff=900), t + k * G.beat_s / 4,
                            gain_db=-15, pan=0.35 * (1 if k % 2 else -1))
            beat += 4
    # hook riser into INTEROPERABILITY, swell into the end card
    s = {x['id']: x for x in TL.segs}
    P = __import__('reel').PLAN
    fx.add(M.riser(dur=2.2, vel=0.6), P['hook_interop'] - 2.2, gain_db=-12)
    fx.add(M.impact_low(vel=0.7), P['hook_interop'], gain_db=-10)
    fx.add(M.reverse_swell(dur=1.6, vel=0.5), TL.speech_end - 1.6, gain_db=-12)
    for k, n in enumerate(['G5', 'B5', 'D6']):
        fx.add(M.bell(n, vel=0.5), TL.speech_end + 0.3 + k * 0.3, gain_db=-14)
    harm = pad.buf + keys.buf + arp.buf
    harm = M.duck(harm + bass.buf, drums.buf, depth_db=3)
    music = harm + drums.buf + fx.buf
    music += M.reverb_send(keys.buf + arp.buf, 'hall', wet_db=-14)
    # keep the music out of the voice's way: darker overall, extra dip at the presence band
    music = A.lp(music, 6500)
    music = A.eq(music, 'peak', 2800, q=0.8, gain_db=-4)
    music = M.fade_out(M.fade_in(music, 0.3), 1.2, end=DUR)
    return music


def main():
    import soundfile as sf
    sys.path.insert(0, HERE)
    import reel
    voice, gains = build_voice()
    print('voice gains', {k: round(20 * np.log10(v), 1) for k, v in gains.items()})
    music = M.fit(compose(), N)
    rep = A.mix(reel.sfx_cues(), DUR, target_lufs=-20.0, verbose=False)
    sfx = M.fit(np.asarray(rep['audio'], np.float64), N)
    # levels: voice at -16 LUFS, SFX ~ -24, music ~ -31 under speech (ducked 6 dB by the voice)
    voice *= A.undb(-16.0 - A.loudness(voice))
    sfx *= A.undb(-24.5 - A.loudness(sfx))
    music *= A.undb(-26.0 - A.loudness(music))
    music = A.sidechain(music, voice, depth_db=6, attack=0.05, release=0.5)
    sfx = A.sidechain(sfx, voice, depth_db=6, attack=0.01, release=0.25)
    mix = voice + sfx + music
    g = A.undb(-14.0 - A.loudness(mix))
    for it in range(6):
        y = mix * g
        lim = A.limiter_gain(y, -2.2)
        y = y * lim[:, None] if lim.ndim == 1 else y * lim
        L = A.loudness(y)
        if abs(L + 14.0) < 0.15: break
        g *= A.undb(-14.0 - L)
    tp = A.true_peak(y)
    print('master LUFS %.2f  TP %.2f dBTP' % (A.loudness(y), tp))
    print('stems (pre-master) voice %.1f  music %.1f  sfx %.1f LUFS' % (A.loudness(voice), A.loudness(music), A.loudness(sfx)))
    sf.write(os.path.join(OUT, 'mix.wav'), y.astype(np.float32), SR, subtype='PCM_24')
    for nm, x in (('voice', voice), ('music', music), ('sfx', sfx)):
        sf.write(os.path.join(OUT, f'{nm}_stem.wav'), (x * g).astype(np.float32), SR, subtype='PCM_24')
    json.dump(dict(lufs=float(A.loudness(y)), tp=float(tp)), open(os.path.join(OUT, 'mix.json'), 'w'))


if __name__ == '__main__':
    main()
