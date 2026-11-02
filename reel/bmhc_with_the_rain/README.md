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

## Draft v2 (Option A, revised after client feedback)
- `bmhc_with_the_rain_v2_voice_bed.mp4`: 49 s, 1080×1920, 30 fps, −14 LUFS; background is a voices-only choir drone
  (minor colour before the verse, major after it), silent during the verse. Recommended for BMHC.
- `bmhc_with_the_rain_v2_piano_strings.mp4`: the same edit with "Rebecca on the Shore" (Mixkit Stock Music Free License),
  for use only if BMHC is happy with instruments.
- What changed: faster guide narration (Kokoro, speed 1.08; "Imam" set phonetically), 11 clips instead of 7 (two clips
  each on the "with", "ease" and "support" lines; people consoling and a person on the phone), a different text
  animation per scene, a purposeful transition per cut, a "Speak to an Imam" button with a cursor tap, and a new
  bed blended with the voice and sound design (presence-band carve and ducking under the voice).
- New clips (all checked on their own pages): Mixkit 50098 (father beside daughter's bike), 100417 (park lamps in rain),
  50122/50131 series (father beside son), 50117 (older man), Coverr 1012 (older man answering phone), Coverr 7136
  (two men talking). Rejected as Mixkit Restricted: 39184 (mosque interior), 28091 (mother and son in rain), 35815.
- Build: `vo2.py` → `align2.py` → `timeline3.py` → `gen_lut.py` → `stage1.py` (+ `stage1_v2.json`) → `bmhc_shot.py` →
  `ov2.js` (all text and the end card as one timed HTML page, rendered per frame) → `compose3.py` (rain, the
  transitions, overlay) → `audio_mix2.py vocal|<music>@pre@post` → `finish2.py` (two-pass loudnorm, mux, previews).

## Draft v3 (client changes on v2)
- `bmhc_with_the_rain_v3_voice_bed.mp4` and `bmhc_with_the_rain_v3_piano_strings.mp4` replace the v2 files (same picture, two beds).
- End-card button reads "Start the conversation"; "WITH" sits lower under مَعَ with a dark pool and stronger shadow.
- Two typefaces throughout: Poppins for the body, Playfair Display Bold Italic (OFL, Google Fonts) for key words.
- Colours: "A bill." white, "A loss." and "A worry" blue, "nobody sees." soft white; blue added to "with you," and
  "going through,". Blue is #74C6F2, gold #E9B45A.
- The 24 s ripple sound is now a soft airy water sound (`soft_ripple()` in `audio_mix2.py`).
- New shots from BMHC's own photos via `photo_shot.py`: photo 34 (sisters at a talk in BMHC's hall) for "Not only
  after the hardship. With it.", photo 23 (group discussion at a round table) for "Whatever you are going through,".
