# QA brief: Hulk Marketing "The Door That Won't Open" (SaaS motion-graphics reel)

Everything a reviewer needs. Paths are relative to `/home/user/100/hulk_marketing/` unless absolute.

## What is under review
- **The cut:** `out/door-that-wont-open/qa/v1.mp4` (1080×1920, 30 fps, 36.5 s, H.264 + AAC; picture + final mix).
- The music-and-SFX-only mix: `door-that-wont-open/audio/mix_novo.wav`. Stems: `door-that-wont-open/audio/stems/{vo,music,sfx}_stem.wav` (pre-master-trim levels; the master adds about +1.6 dB).
- Source (read-only for reviewers): `door-that-wont-open/film.js` (timeline, captions, UI), `door-that-wont-open/src/street.js` (set, camera, character), `door-that-wont-open/src/kit.js` (type, pills, spinner, cursor), `door-that-wont-open/audio/{score,sfx,mix,build_vo}.py`.

## The client's brief and references
- Concept PDF: `/root/.claude/uploads/9c450839-ae81-55f4-a4cb-27f28fd0cdf5/b885559e-saturday_hulk_marketing_ai_video_the_door_that_wont_open.pdf`
  (written for an AI live-action film; the client asked for it to be made as a SaaS-style motion-graphics reel instead).
- Reference reel for the animation style: `/root/.claude/uploads/9c450839-ae81-55f4-a4cb-27f28fd0cdf5/a966bd0f-Whatsapp_Video_2026-11-04_At_11.13.49_Pm_1.mp4`
  (dark forest-black frames, lime accents, glass UI cards and pills, caps + lime italic serif accent words, small lime rule above titles, lime stage rules, typed URL + cursor click on the CTA).
- Brand: hulkmarketing.co.uk (dark theme). Tokens in `door-that-wont-open/assets/brand.json`; lime `#9DEF69`, canvas `#0A0B0A`, forest `#111A16`; fonts Inter Tight (captions, caps 800), Fraunces Italic (the lime accent word), Hanken Grotesk (UI). Real logo: `door-that-wont-open/assets/hulk-marketing-logo.png`.
- Verified copy and sources: `door-that-wont-open/assets/copy.md`. Plan: `door-that-wont-open/docs/shotlist.md`, `docs/style_guide.md`.

## Deliberate adaptations (not defects, unless they hurt the piece)
- Dusk / brand-dark palette instead of the PDF's "sunny" street (the live-action note), to match the reference reel and the brand's dark theme.
- The street is a flat vector set; "across the road" is a side road with a zebra crossing between the two shops.
- Beat 5 adds a browser window built around shop A (the metaphor made literal); beat 7 adds three check pills (Fast / Stable / Easy to grow) and the site line "Core Web Vitals tuned and continuously measured."
- Duration 36.5 s (PDF: about 35 s, "hold the end card 1 s longer if needed").
- Voice: ElevenLabs "Oliver – Warm British Narrator", take verified word-perfect with Whisper.

## Timeline (film seconds) and the VO words captions must follow
VO lines start: She found you 0.40 · She wants to buy 1.70 · But the door won't open 4.30 · One second 9.00 · Two 10.00 · Three 11.00 ·
So she walks across the road 13.20 · That's a slow website 18.50 · Every second… conversions 21.35 · We build sites… easy to grow 26.10 ·
See your opportunity in thirty seconds 31.10 · Get your free website audit 33.75. Every word time: `door-that-wont-open/vo_words.json`.
Cue words: buy 2.27, open 4.99, Three 11.01, across 13.73, slow 19.03, conversions 23.90, fast 27.18, stable 27.82, easy 28.56, audit 34.79.

Picture events: pin drops 0.35 · bag bubble 1.95 · push-in 3.4-4.35 · door pushes (judder + dull thud) 4.45, 6.17 · spinner appears 4.99 ·
pull back 7.5-8.35 · counter ticks 9, 10, 11, 12 · watch check 9.2-10.35 · sigh 11.6-12.45 · step back 12.55 · walk across 12.9-16.2 ·
shop B door glides open ~15.8, bell ~15.92 · she steps in 16.2-17.1 · whip back 18.0-18.45 · browser builds 18.55-19.8 · hard cut to the stage 21.0 ·
spinner stalls/reverses 24.55-25.0 · rewind 25.0-26.2 · spinner fills 27.0-27.14, tick 27.08-27.22 · door swings open 27.18 · tick flies to the "Fast" pill 27.36-27.74 ·
pills 27.3 / 27.8 / 28.5 · CWV line 29.15 · shrink to card 30.6-31.38 · CTA card 32.95 · URL types 33.4-34.35 · logo 33.62 · cursor 33.98-34.66, click 34.79.
SFX cue list: `door-that-wont-open/audio/sfx_cues.json`; footstep times `door-that-wont-open/audio/steps.json`.

## Rules to check against
- PDF safe area: all text inside x 60-960, y 270-1240. Instagram: nothing textual below y 1620; avoid x > 930 for y 1050-1700.
- Captions = the voiceover word for word, one lime cue word each (PDF). Text lands as or just before its words are spoken; it stays ≥ 0.7 s after the line ends.
- Careful claims (PDF): no statistics, no client results, no speed scores; shops fictional with blank signs; the competitor (shop B) not named or mocked; the spinner is Hulk's lime ring, never a browser's or platform's icon.
- Craft: no one-frame pops, ghost frames or flashes at cuts; whips keep both shots on screen; motion blur where things move fast; nothing illegible at phone size (look at frames scaled to 540 px wide); something new every 2-4 s.
- Audio: master -14 LUFS integrated (±0.5), true peak ≤ -1 dBTP; voice intelligible over music and SFX; music drops to silence for the waiting beat (8-13 s); every visible hit has its sound within about ±40 ms.

## How to look
- Frames: `ffmpeg -v error -ss T -i out/door-that-wont-open/qa/v1.mp4 -frames:v 1 x.png`; contact sheets:
  `ffmpeg -v error -i v1.mp4 -vf "fps=5,scale=216:384,tile=10x4" sheet_%02d.png`; exact frames with `-vf "select=eq(n\,N)"`.
- Audio: `ffmpeg -i ... -af ebur128=peak=true -f null -`; faster-whisper is installed (`WhisperModel('small.en', device='cpu', compute_type='int8')`, model already cached; pass a 16 kHz float32 numpy array, not a file path).
- Do NOT start renders of the film (the CPU is shared); work from v1.mp4 and the wav files. Put scratch images in your own folder under
  `/tmp/claude-0/-home-user-100/9c450839-ae81-55f4-a4cb-27f28fd0cdf5/scratchpad/qa/`, never in the repo. Never edit any file in the repo.
