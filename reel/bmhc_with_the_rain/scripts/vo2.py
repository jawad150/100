import soundfile as sf, numpy as np, json, sys, os
from kokoro_onnx import Kokoro
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
k = Kokoro(os.path.join(B, 'audio', 'kokoro-v1.0.onnx'), os.path.join(B, 'audio', 'voices-v1.0.bin'))
voice = sys.argv[1] if len(sys.argv) > 1 else 'bm_george'
speed = float(sys.argv[2]) if len(sys.argv) > 2 else 1.05
LINES = {
 'L1': "Manchester knows rain. Some days, so do we.",
 'L2': "A bill. A loss. A worry nobody sees.",
 'L3': "Allah says: For indeed, with hardship will be ease. Indeed, with hardship will be ease.",
 'L4': "Notice the word: with. Not only after the hardship. With it.",
 'L5': "Ease often comes while it's still raining: someone who sits with you,",
 'L6': "a friend who calls,",
 'L7': "a door that's open.",
 'L8': "Whatever you are going through, support is just a conversation away.",
 'L9': "Imam Counselling at B. M. H. C.",
}
ONLY = sys.argv[3].split(',') if len(sys.argv) > 3 else list(LINES)
prev = json.load(open(os.path.join(B, 'audio', 'vo', 'lines.json'))) if len(sys.argv) > 3 else {}
out = {k_: {kk: v for kk, v in prev[k_].items() if kk in ('text', 'dur', 'sr')} for k_ in prev}
for key, text in LINES.items():
    if key not in ONLY: continue
    if key in ('L3', 'L9'):
        # pronunciation fixes: "Allah" (not "Alice") and "Imam" (ee-MAAM, not "the Mom")
        ph = k.tokenizer.phonemize(text, 'en-gb').replace('ˈalə', 'ɐlˈɑː', 1).replace('ɪmˈam', 'iːmˈɑːm', 1)
        samples, sr = k.create(ph, voice=voice, speed=speed, is_phonemes=True)
    else:
        samples, sr = k.create(text, voice=voice, speed=speed, lang='en-gb')
    samples = np.asarray(samples, dtype=np.float32)
    a = np.abs(samples); idx = np.where(a > 0.01 * a.max())[0]
    samples = samples[max(0, idx[0] - int(0.03 * sr)): idx[-1] + int(0.08 * sr)]
    sf.write(os.path.join(B, 'audio', 'vo', f'{key}.wav'), samples, sr)
    out[key] = {'text': text, 'dur': round(len(samples) / sr, 3), 'sr': sr}
    print(key, out[key]['dur'], round(len(text.split()) / out[key]['dur'] * 60), 'wpm')
out = {k_: out[k_] for k_ in LINES}
json.dump(out, open(os.path.join(B, 'audio', 'vo', 'lines.json'), 'w'), indent=1)
