# BMHC · "With the Rain" · production files

Storyboard options for the BMHC Reel (concept: `static_posts/bmhc_ai_video_with_the_rain.pdf`).
The storyboard PDF is `static_posts/bmhc_video_with_the_rain_storyboard.pdf`.

- `frames/`: the storyboard frames (540×960 previews; A = Option A, B = Option B)
- `picks/`: the chosen stock clips per shot, with source pages, licences, in/out points and crops
- `scripts/source.py`: collects candidate clips from Mixkit and Coverr
- `scripts/prep_frames.py`: grades frames, adds the generated rain layer, crops BMHC's photos
- `scripts/frames.js` + `frames_spec.json`: renders frames with on-screen text (Playwright)

Clips are Mixkit (Free licence only; "Restricted" items rejected) and Coverr (Coverr licence).
The full-resolution clips are not committed; re-download them from the URLs in `picks/`.

## Draft v1 (Option A)
- `bmhc_with_the_rain_v1_draft.mp4`: 51 s, 1080×1920, 30 fps, −14 LUFS, with a placeholder vocal-pad bed
- `bmhc_with_the_rain_v1_draft_no_music.mp4`: the same edit, voice + recitation + rain/ambience only
- Placeholders to replace: the guide narration (Kokoro TTS, British male; "Allah" set phonetically) → the client's human
  voiceover; the recitation (Mishary Alafasy, 94:5–6, everyayah.com) → BMHC's imam; the vocal pad (stretched from the
  Mixkit "Angelical choir" sound effect) → a licensed vocal-only nasheed.
- Build: `vo.py` → `align.py` → `timeline.py` → `gen_lut.py` → `stage1.py` (ffmpeg grade/push per shot) →
  `bmhc_shot.py` (BMHC tower-to-door move with door glow) → `overlays.js` (captions/verse/end card) →
  `compose2.py` (rain, transitions, captions) → `audio_mix.py` → loudnorm and mux.
  The timeline is driven by the voice and recitation lengths, so swapping in new recordings re-times everything.
