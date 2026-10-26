# P.S. Med Spa "Meet Jana" reel: captions, transitions, grade

A 43.2 s vertical reel (1080×1920, 23.976 fps) made from the supplied edit `Meet Jana.mov` (2160×3840, DaVinci Resolve export). The cut and the voice are kept as delivered. It is built with the P.S. Med Spa reel pipeline and follows the same look: the same caption styles, brand colours, fonts, person masking and grade LUT. Per the brief, it uses only a few transitions.

**Output:** [`reel/jana/PS_MedSpa_Meet_Jana_1080x1920.mp4`](../../reel/jana/PS_MedSpa_Meet_Jana_1080x1920.mp4) · share copy [`reel/jana/PS_MedSpa_Meet_Jana_share.mp4`](../../reel/jana/PS_MedSpa_Meet_Jana_share.mp4) · subtitles [`reel/jana/PS_MedSpa_Meet_Jana.srt`](../../reel/jana/PS_MedSpa_Meet_Jana.srt) · Resolve LUT [`reel/jana/PS_MedSpa_Look_Rec709.cube`](../../reel/jana/PS_MedSpa_Look_Rec709.cube)

## Length

The delivered file runs 69.4 s, but its audio is digital silence after 42.27 s. The last 27 s are laser B-roll with no voice and no music. The reel ends on her last words ("…eager to help you."), with a fade to black over the final 0.7 s. To bring the B-roll tail back, raise `NFRAMES`/`NOUT` in `common.py` and add the tail shots to `CUTS` (1086, 1232, 1340, 1567). The tail would then need a music bed.

## Look (same as the P.S. Med Spa reel)

- **Two-line captions:**
  - a light italic grotesk lead-in (white, or charcoal on light walls)
  - a big Fraunces word in near-black or brand red `#EA1D25`. Over walls it sits **behind** her, using the RVM person matte. Over her black top or busy close-ups it sits in front, in red with a soft red glow.
  - sometimes a white italic serif third line ("Strada.", "years,", "through the years,")
- **Small word-by-word captions** in light italic grotesk: white with a soft shadow, or charcoal on white towels and walls.
- **Fonts:** Hanken Grotesk (stand-in for Founders Grotesk) and Fraunces (stand-in for Freight Display Pro), downloaded by `prep.py`.
- **Big words, in order:**
  - Jana
  - injector
  - **19**
  - **P.S. Medical Spa**
  - **listening**
  - skin
  - changing
  - correct
  - **flourish.**
  - maintenance
  - **skin health,**
  - appearance,
  - **health.**
  - **skincare journey,**
  - **help you.**

  Bold = red.
- **Transitions:** three, on 13 cuts:
  - zoom-blur push out of the opening shot
  - one horizontal whip into the storefront
  - brand-red light leak into "health."

  The other ten cuts are hard cuts, with no whoosh on them.
- **Camera:** a slow push-in on every shot, plus vignette, fine grain and a soft bottom gradient.
- **Audio:** the voice gets +6 dB of make-up gain. It was delivered at −21.8 LUFS / −8.8 dBTP and now sits at about −16 LUFS. Quiet whooshes sit under the three transitions. The source has no music bed.

## Grade

The source is display-referred Rec.709 (not log), so the grade uses the P.S. Med Spa look LUT (`grade.py`, also exported as `.cube`). Per-shot balance is measured from neutral highlights and corrected about halfway:

- the interview set reads pink-warm and is cooled slightly
- the treatment rooms read blue under daylight and are warmed
- the syringe tray reads yellow-green
- the storefront (shot through glass) and the tray get a black pull for their milky blacks

## Notes

- **Cuts** come from frame differencing. The bright IPL / laser pulses inside the laser-hair-removal shot (10.4–15.0 s) and the RF shot (32.3–37.2 s) are flashes, not cuts.
- **Spelling.** The name "Strada" matches both the transcript and the "Jana Strada, Medical Aesthetics" embroidery on her top. Whisper wrote the clinic as "PS Medical Spa", and it is captioned "P.S. Medical Spa".
- **Transcript.** Whisper's trailing "Thank you." at 68 s was a hallucination over the silent tail and was dropped from `words.json`.

## Rebuild

```bash
pip install numpy scipy pillow "opencv-python-headless==4.10.0.84" onnxruntime faster-whisper
# workspace/jana/src/: source.mov ('Meet Jana.mov'), rvm_fp16.onnx (huggingface: inverseaibd/rvm_mobilenetv3_fp16)
cd pipeline/jana
python3 prep.py            # fonts, 1440x2560 JPEG frames, words.json (already committed)
python3 matte.py           # person mattes
python3 track.py           # background motion track
python3 render.py frames 4 # all frames
python3 sfx.py             # +6 dB voice, transition whooshes -> mix.wav
python3 encode.py          # -> reel/jana/PS_MedSpa_Meet_Jana_1080x1920.mp4
python3 srt.py             # -> reel/jana/PS_MedSpa_Meet_Jana.srt
python3 grade.py cube      # -> reel/jana/PS_MedSpa_Look_Rec709.cube
```

To preview stills, run `python3 render.py still 1.3,12.9,41.9` (seconds or frame numbers). `qa_sheets.py` builds labelled contact sheets and a caption/timing table. The caption timeline lives in `render.py` (`hero(...)`, `cap(...)`).
