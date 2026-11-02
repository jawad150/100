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
