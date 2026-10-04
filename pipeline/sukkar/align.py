"""CTC forced alignment (wav2vec2 base 960h) for exact word boundaries.

align(path, t0, t1, text) -> [(word, start_s, end_s)] in source-file seconds.
"""
import re
import subprocess

import numpy as np
import torch
import torchaudio

torch.set_num_threads(4)
_bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H
_model = None
_labels = _bundle.get_labels()
_dict = {c: i for i, c in enumerate(_labels)}
SR = _bundle.sample_rate


def _load(path, t0, dur):
    raw = subprocess.run(["ffmpeg", "-v", "quiet", "-ss", f"{t0:.4f}", "-t", f"{dur:.4f}", "-i", path,
                          "-map", "0:a:0", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True).stdout
    return torch.from_numpy(np.frombuffer(raw, np.float32).copy())


def align(path, t0, t1, text):
    global _model
    if _model is None:
        _model = _bundle.get_model().eval()
    wav = _load(path, t0, t1 - t0)
    with torch.inference_mode():
        em, _ = _model(wav[None])
        em = torch.log_softmax(em, dim=-1)
    words = [re.sub(r"[^A-Z']", "", w.upper()) for w in text.split()]
    words = [w for w in words if w]
    transcript = "|".join(words)
    tokens = torch.tensor([[_dict[c] for c in transcript]], dtype=torch.int32)
    ali, scores = torchaudio.functional.forced_align(em, tokens, blank=0)
    ali, scores = ali[0], scores[0].exp()
    spans = torchaudio.functional.merge_tokens(ali, scores)
    frame_s = (t1 - t0) / em.shape[1]
    out, i = [], 0
    for w in words:
        n = len(w)
        seg = spans[i:i + n]
        out.append((w, t0 + seg[0].start * frame_s, t0 + seg[-1].end * frame_s,
                    float(np.mean([s.score for s in seg]))))
        i += n + 1  # skip the '|' separator span
    return out


if __name__ == "__main__":
    import sys
    for w, s, e, sc in align(sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]):
        print(f"{w:12s} {s:9.3f} {e:9.3f}  {sc:.2f}")
