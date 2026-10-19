# Clinic for Plastic Surgery reel: testimonial captions, B&W difference text, transitions

A 55 s vertical reel (1080×1920, 23.976 fps) made from the supplied ProRes edit `C9246_1.mov`. That file is 2160×3840 with 17 shots of surgery B-roll and a patient testimonial voiceover. The cut and the voice are kept as delivered. The voice gets about 9.5 dB of make-up gain because it was recorded quietly.

**Output:** [`reel/surgery/Surgery_Testimonial_1080x1920.mp4`](../../reel/surgery/Surgery_Testimonial_1080x1920.mp4)

## Look

This reel is built from the P.S. Med Spa pipeline (`../medspa`), restyled in black and white with no red:

- **Captions** use the same fonts: Hanken Grotesk Light Italic, which stands in for Founders Grotesk, and Fraunces SemiBold, which stands in for Freight Display Pro.
- **Small captions** are word-by-word in white. On white walls they switch to black.
- **Two-line captions** follow the client's "using / SEO" sample: a thin white lead-in, then a big serif word drawn with a **black & white difference blend** (`render.diff_blend`).
  - Where the word covers something bright it turns black; where it covers something dark it turns white, so a word crossing a white wall and a dark cap flips mid-word.
  - The blend uses the inverted *luminance* with extra contrast, so it stays black and white on the blue scrubs. A plain colour difference turns orange there.
- **Behind the surgeon.** Where a person is in frame, the big words go behind them using the RVM person matte, e.g. "no pain." and "secure.".
- **Lego brick.** At 4–5 s a glossy blue 2×4 brick pops in next to "Lego" with a slight tilt and a soft shadow. It's a Blender render with a transparent background (`lego_brick.py`), so there is no white box around it.
- **Transitions** at every cut: zoom blur, whip, flash, punch-in, blur dissolve and a white light leak.
- **Grade:** the same look LUT as the P.S. Med Spa reel, with a slight warm-up on the cooler shots.

## Rebuild

```bash
cd pipeline/surgery
# workspace/surgery/src/: source.mov (the ProRes edit), rvm_fp16.onnx
python3 prep.py frames        # 1440x2560 JPEG frames (8-bit, BT.709 -> JPEG BT.601 handled)
python3 matte.py && python3 -c "import track; track.main()"
python3 lego_brick.py         # needs the bpy module (pip install bpy)
python3 render.py frames 4
python3 sfx.py
python3 encode.py             # -> reel/surgery/Surgery_Testimonial_1080x1920.mp4
```

The word timings in `words.json` come from faster-whisper large-v3. The caption timeline is in `render.py`.
