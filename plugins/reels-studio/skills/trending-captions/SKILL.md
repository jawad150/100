---
name: trending-captions
description: Animated, trend-style captions for 9:16 talking-head or voice-over reels. A bundled script (make_captions.py) transcribes with faster-whisper (word timestamps, optional) or reads a word-timing JSON, chunks speech into 1-4 word phrases, picks out emphasis words and numbers, lays the phrases out inside the Instagram/TikTok safe zones, and writes a libass .ass file in one of four presets (bold-pop, karaoke, boxed, minimal), an .srt, a QA report, and the ffmpeg burn command. Brand fonts and colours are passed as arguments. Use it to add or restyle burned-in captions, make an SRT for upload, or fix captions that are mistimed, too small, off-brand or under the platform UI.
when_to_use: A reel has speech (talking head, interview, UGC, voice-over) and needs burned-in captions or an SRT; or existing captions need a new style, brand colours, re-timing or safe-zone fixes. Not for designed kinetic headlines inside a motion timeline; those are built in the reel module.
---

# Trending captions

`${CLAUDE_SKILL_DIR}/make_captions.py` turns word timings into styled `.ass` subtitles that ffmpeg burns with
libass, plus an `.srt` and a `.captions.json` QA report. Tested with ffmpeg 6.1 (libass), Pillow 12 (raqm) and
Python 3.13 at 1080x1920, 720x1280, 25 and 30 fps.

Needs: `python3`, Pillow, and ffmpeg built with libass (`ffmpeg -hide_banner -filters | grep " ass "`).
Optional: `faster-whisper` for transcription (`uv pip install faster-whisper`, or pip). On the RTX 4060, run with
`--device cuda`; if CUDA 12 libraries are missing, also run `uv pip install nvidia-cublas-cu12 "nvidia-cudnn-cu12==9.*"`,
or use `--device cpu --compute-type int8`. The script never installs anything. Without faster-whisper it prints
how to install it and exits with code 2.

## Workflow
1. **Words.** Pick the source that applies:
   - Transcribe: `python3 ${CLAUDE_SKILL_DIR}/make_captions.py talk.mp4 --language en --model large-v3 --device cuda --prompt "BrandName, ProductName" -o caps/talk`
     This writes `caps/talk.words.json`, then builds the captions from it.
   - Supply timings yourself: a JSON list of `{"word", "start", "end"}` in seconds. It may also be `{"words": [...]}`, or whisper-style `{"segments": [{"words": [...]}]}`. Add `"emph": true` to a word to force emphasis.
   - Demo file: `--sample words.json` writes one.
2. **Correct the words JSON** against the script or the brief's verified copy:
   - Fix brand names, product names, numbers and units, plus every word listed under "low-confidence words".
   - Captions are a transcript, so keep the speaker's meaning. Never turn speech into a new claim.
   - If the voice-over states a figure the brief has not verified, flag it; don't caption it as fact.
   - Then run the script again on the JSON.
3. **Style.** Choose a preset (table below) and pass the brand font and colours:
   ```bash
   S=${CLAUDE_SKILL_DIR}/make_captions.py
   python3 $S caps/talk.words.json --preset bold-pop --video talk_9x16.mp4 \
     --fontsdir <WS>/fonts --font "Montserrat" --highlight '#F7C204' --emphasis "free,today" -o caps/talk
   ```
   - `--font` takes a TTF/OTF path, a full name ("Poppins Black") or a bare family name ("Poppins"). A family name gets the heaviest weight the preset prefers. Always pass `--fontsdir`: the layout is measured from the real font file, and libass loads the same file.
   - `--video` sets the resolution and fps from the clip (ffprobe). Without it they default to 1080x1920 at 30 fps.
4. **QA before burning.**
   - Read the console report:
     - `SAFE-ZONE` and `SIZE` lines must be gone (`--strict` exits 1 while any remain);
     - check the widest phrase and the block's y range;
     - check the emphasis candidates.
   - Make a QA render with `--guides`. It draws the safe-zone lines into the ASS, so never deliver it.
5. **Burn.** Run the printed command. It is a CRF 14 H.264 High master with bt709 tags, audio copied and +faststart:
   ```bash
   ffmpeg -y -i in.mp4 -vf "ass=caps/talk.ass:fontsdir=<WS>/fonts" -c:v libx264 -preset slow -crf 14 \
     -profile:v high -pix_fmt yuv420p -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
     -c:a copy -movflags +faststart caps/talk_captioned.mp4
   ```
   - Encode the deliverables from this master: 2-pass about 22 Mbps for Instagram, and about 7 Mbps for the chat preview.
   - For a toolkit reel, burn onto `<WS>/out/<module>/<module>.mp4` and write the result as `<WS>/out/<module>_cap/<module>_cap.mp4`. Copy the stem to `<WS>/audio/<module>_cap_sfx_stem.wav`, then run `python3 package.py <module>_cap <slug> --cover T` in the toolkit folder.
6. **Verify the burned file.**
   - `ffprobe -v error -show_entries stream=width,height,r_frame_rate,nb_frames:format=duration -of compact out.mp4`
   - Extract frames: 5 fps across the clip, plus every frame from 0.2 s before to 0.4 s after several word onsets: `ffmpeg -i out.mp4 -vf fps=5 qa/f_%03d.png`.
   - Open the frames and check:
     - the highlight lands on the spoken word, within one frame of the onset in the words JSON;
     - no caption covers eyes, mouth or the product;
     - nothing sits in the like/share column;
     - the colours match the brand (sample a pixel; chroma subsampling shifts it a few values).

## Presets

| preset | look | use it for |
|---|---|---|
| `bold-pop` | Heavy uppercase with a thick outline. The phrase pops in; the active word turns the highlight colour and scales up 12 % then settles; emphasis words stay highlighted and 12 % larger. 3 words per phrase. | Talking heads, hooks, energetic creator content. The default. |
| `karaoke` | Uppercase extra-bold. Each word fills left to right (`\kf`) while it is spoken. Up to 4 words per phrase. | Tutorials, fast voice-over, lyric-like pacing. |
| `boxed` | Sentence case, bold, inside a rounded box (`--box-color`, `--box-opacity`). The active word takes the highlight colour. | Busy or bright footage, brand-led pieces, pill/chip looks. |
| `minimal` | Sentence case, semibold, soft shadow, gentle fades, no highlight. A lower third at y≈1390. | Calm, premium, documentary, interviews, founder stories. |
| `--pill` | Adds a rounded pill (`--pill-color`, `--pill-text`) behind the active word. Works with bold-pop and boxed. | The trending chip look. One pill colour only. |

Main options:
- `--size` sets the em in px at 1080 wide. Defaults: 84 bold-pop, 74 karaoke, 62 boxed, 54 minimal.
- `--case upper|lower|as-is`, `--max-words` (1-4), `--lines` (default 2).
- `--y` sets the block centre; `--y-at "0-3.5:1300,3.5-9:620"` sets it per time range to keep captions off faces. `--x` moves the centre left; this also gives more width.
- Timing: `--lead 0.05` (shows words slightly early), `--hold 0.35`, `--gap 0.45` (a pause longer than this starts a new phrase), `--offset` (shifts all words, for example when the voice-over starts at 1.2 s in the edit).
- `--srt-mode sentences|phrases`. Upload files use sentences: 2 lines of up to 42 characters, at most 6 s each.

## Rules the script enforces, and what you still check
- **Safe zones at 1080x1920.** The script scales them for other sizes.
  - Captions stay inside x 70-1010 and y 230-1480.
  - Nothing goes at x > 930 for y 1050-1700 (the like/share column), and nothing below y 1620.
  - The default caption band is the lower middle (centre y 1240-1260, or 1390 for minimal). It overlaps the column zone, so the maximum line width is about 720-780 px around x 540.
  - A phrase that would overflow first breaks into 2 balanced lines (no line ends on "the", "your", "to" ...). Only then does it shrink. A shrink below 85 % is a `SIZE` warning: shorten the phrase or lower `--size`.
- **Legibility.** The text stays at UI-body size or bigger (well above 34-40 px). Use one accent colour. Highlight sparingly: hooks, numbers, the key noun, the punchline. Numbers, %, £, $ and € are emphasised automatically (`--no-number-emphasis` turns this off). Pass 1-3 keywords per reel with `--emphasis`; if every word is highlighted, none is.
- **Motion.**
  - Consecutive phrases swap on the frame the next phrase starts; the new phrase's pop is the transition.
  - A phrase followed by silence fades and shrinks out over about 110 ms. There are never one-frame exits.
  - Event times are snapped to the video's frame grid.
- **Faces and on-screen copy.**
  - Pick the band per shot so captions never cover eyes, mouth, a 3D object or the product; use `--y-at` to move them.
  - Where a designed headline already shows the same words, delete those words from the JSON for that window so the two don't double up.
- **Pitfalls.**
  - Don't input-seek (`ffmpeg -ss T -i in.mp4 -vf ass=...`). It restarts the clock and the captions vanish or shift. Burn the whole clip, or seek on the output side (`-i in.mp4 -ss T`).
  - Match `--fps` and `--res` to the video you burn onto (use `--video`).
  - The burned result depends on `fontsdir`. If ffmpeg logs `fontselect: ... -> DejaVuSans`, the brand font wasn't found.

## Caption trend notes (checked 2026-10-08; sources are mostly caption-tool vendors, so treat them as informed opinion)
- **Word-by-word is the baseline.** Showing 2-3 words at a time, synced to speech, is now standard. Static full-sentence blocks read as dated or low-effort. (blitzcutai.com/blog/tiktok-caption-trends-2026; subclip.app; opus.pro)
- **"Dynamic minimalism" is rising.** It keeps word timing and a heavy font, but drops flashing keyword colours, a sound effect on every word, and emoji. A subtle scale or fade on entry is enough. For this look use `minimal`, or `bold-pop` with one accent colour.
- **Declining.**
  - The full "Hormozi" package (yellow highlight + all caps + a whoosh per word + emoji) is saturated.
  - Per-word shake or vibrate.
  - Neon green or electric blue as the main colour.
  - Lines in three or more colours.
  - Thin script fonts.
- **Rising.**
  - Coloured pill or chip backgrounds (`boxed`, `--pill`).
  - Typewriter reveals: too slow above about 140 words per minute.
  - Quiet lowercase minimal lines (`minimal --case lower`).
- **Colour.** White with a black outline is still the base. Keyword accents that work: yellow (about #F7C204) for business and education, butter yellow (about #F5D76E) for lifestyle, mint, hot pink. Pure red vibrates against skin, and pure blue vanishes on sky and denim. Prefer the client's brand accent when it passes these tests.
- **Fonts.** Heavy geometric sans faces lead: Montserrat Black, Poppins Black/ExtraBold, Inter, Archivo Black, Anton, Bebas Neue. TikTok Sans has been open source since mid-2025.
- **Placement.** Sources agree on keeping clear of the top bar and the bottom 20-25 % UI. Some prefer slightly above centre, others the lower middle. Our rule is the lower-middle band inside the safe zones, moved per shot for faces.
- **Delivery.** Burn the captions in for everyone, and keep a clean SRT for platform captions, editing and translation. Native auto-captions look generic.
- **Re-check.** Rerun a quick web search before relying on these notes if they are more than about 3 months old.
