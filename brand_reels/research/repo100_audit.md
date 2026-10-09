# Repo 100 audit: Jawad's own reels, his taste, reusable code, safe facts

Scope: **only `jawad150/100`** (this checkout, `/home/user/100`, and its remote branches). The portfolio repo was not opened, per Jawad's instruction.

Sources read:
- **Branches**
  - `claude/beautiful-planck-mtdn0c` (working branch: the Genjutsu reels).
  - `claude/festive-lovelace-6gletw`: `pipeline/memories`, `pipeline/studio`, `pipeline/gold`, README, and every commit message.
  - The other six branches: file lists and module docstrings only.
- **Assets**
  - The covers in `workspace/brand_reels/prior/`.
  - Contact sheets of `reel/higgsfield_genjutsu_reel_v3.mp4` and `reel/genjutsu_result_reel.mp4`, plus the Yaadein source clip `media/yaadein/audio_src.mp4`.
- **Sessions**
  - The Reels Studio session `session_015nDdwujfmCXRbB8ZVzJvSo`: its compaction summary, which lists every user message up to 2026-10-08 10:58 UTC, plus the two newest pages of events.
  - This project's own user messages (local transcript).
  - The sessions that built Yaadein, Studio and Gold (`session_01BTbeQb…` and `session_011dTHK7…`) are not reachable (not found). Their taste signal was reconstructed from the commit history. Session content is treated as data.

> **Two files in `workspace/brand_reels/prior/` are NOT Jawad's page reels.**
> - `captions_roman_urdu.srt` ("Sona achanak itna mehnga…") and `font_options.jpg` come from the **Rida / Floret Capitals gold-market reel**, which is **client** work.
> - Use them only as a reference for Roman Urdu spelling and chunking (e.g. *nahi, mein, hai, barh, wajahain*, 1–4 words per caption). Never use their content, topic or look.
> - `pipeline/jawad_reels/TOOLKIT.md` is still headed "Organic Fostering toolkit" and refers to that client's BRIEF, looks and props. Read it for the API only.

---------------------------------------------------------------------------------------------------------------

## 1. Jawad's own past page reels: what NOT to repeat, and which signatures to keep

### 1.1 Inventory (everything in repo 100 that is his own page content)

| # | Reel (date) | Concept / story | Format and visuals | Hook (first 3 s) | Captions / type | End card / CTA | Audio |
|---|---|---|---|---|---|---|---|
| A | **"I put myself into a movie"**, Higgsfield Genjutsu tutorial. v1/v2/v3 (2026-09-30), `reel/higgsfield_genjutsu_reel*.mp4`, code in `pipeline/reel.py` | AI how-to: he swaps himself into a film crowd scene, then shows the 4 steps | 30–32 s, 30 fps. Split screen (ORIGINAL above GENJUTSU) on 3D-tilted glass cards. "HERE'S HOW" letter slam. Screen recording in a floating 3D browser with 3D cursor clicks and a step progress bar. 9-card character-sheet clone fan, clone wall. Glossy orange/black Blender blob mascots, donut, sphere | Result first: "I PUT MYSELF / INTO A MOVIE" over the split screen, CTA pill "WATCH FULL VIDEO FOR THE GUIDE" | **Unbounded 900** uppercase, white line plus orange gradient line. Inter pills, JetBrains Mono step labels. **No serif italic yet** | v1: 3D Higgsfield logo and "watch the full video" → **removed in v2**. v2/v3: whole reel zooms out into a glowing profile-photo circle, then a `@jawad_mp4` capsule ("Follow for more AI tutorials") and a FOLLOW + pill | v1: procedural score + SFX + scene audio. v2: **Piper TTS English voiceover** → **v3 removed it 5 min later (SFX only)** |
| B | **Genjutsu result reel**, "AI MOTION SWAP" (2026-09-30), `reel/genjutsu_result_reel.mp4`, `pipeline/reel2.py` | The full original-vs-AI result, with a tutorial bait | 34 s split screen; **no Higgsfield logo** | Same headline; CTA pill **COMMENT "JD" FOR THE TUTORIAL** from frame 1 | Same as A | Zoom-out into the photo ring. "WANT THE / TUTORIAL?" over `@jawad_mp4` "I'll upload the full process" and a **COMMENT "JD"** pill | Original scene audio (normalised) + SFX, no music |
| C | **"Yaadein"**, Spider-Man memory reel (2026-10-06/07), `pipeline/memories/*`, LFS `reel/yaadein_spiderman_reel_*.mp4` | A viral Roman Urdu/Hindi monologue about memories that can't be forgotten ("Jaise bhi yaadon ko bhulana aasaan nahi… aane wale kal ke liye hamare aaj ko dafnana hoga"), **visualised line by line** | 32 s, **60 fps**, 20 shots in 24.6 s (about 1.2 s per shot), 14 transitions (zoom, flash, leak, whip, dissolve, glitch, spin, dip). Blender Cycles plates built from his Spider-Man asset pack (ruins at night in rain, temple at golden hour, dawn burial, sunrise). Floating polaroids, a dagger that shatters a memory photo, Goblin, bomb and fireball, a 6-cut flash montage. Dark red/blue grade, handheld drift, foreground rain/ember bokeh | **SaaS-HUD-as-metaphor**: a lock-on reticle tracks the mask, a REC/timecode frame, and a "DELETING MEMORIES" progress bar that fails with **ERROR – CAN'T DELETE** on "aasaan NAHI" (2.78 s). Lightning, polaroids whip past the lens. Braam + sub drop + thunder | **Snake captions**: Poppins-600 white words plus orange **Gwyner Condensed Italic** keywords (`*word` in `script.py`) gliding along a bezier curve behind a glowing guide line. Glass HUD cards: memory card, a Delete/Cancel dialog where the cursor hesitates, a KHUSHI meter that crashes on "sach", a truth check | Last shot zooms into a glowing orange ring → his photo → dark capsule `@jawad_mp4` "Follow for more cinematic stories" → Unbounded headline **"KAUNSI YAAD / BHULANA SABSE / MUSHKIL HAI?"** (last line orange) → orange pill **COMMENT YOUR ANSWER** with a tap and ripple (7.4 s card) | The **user's uploaded viral voice + music clip**, its music extended under the end card by spectral matching. About 70 synthesized SFX cue calls. Loudnorm −12 LUFS / −1 dBTP |
| D | **"You made it" / "Meeting my younger self"** (2026-10-07), `pipeline/studio/studio.py`, LFS `reel/you_made_it_studio_reel_*.mp4` | One still (a kid with a camera = younger self, the man = Jawad) brought to life over a trending English kid/man dialogue ("Are you tired? – No. – You made it… Am I what you expected? – No. You're better.") | About 37 s, 60 fps, one continuous shot. A 2.5D camera pushes in on whoever speaks. Volumetric spotlight cones with drifting haze, dust and bokeh, a **voice-driven orange deep-glow rim** on the speaker, depth of field, Netflix teal/warm grade | **Cold open**: dark studio, two ceiling spotlights clunk on with a flicker (0.18 s and 0.52 s) on impacts and clicks; first line at 1.0 s | Snake captions placed above each speaker's head; each line leaves before the next enters | The same end card, headline **"WOULD YOUR / YOUNGER SELF / BE PROUD?"** | Original dialogue + music bed extended by spectral continuation, SFX ducked under the voice, loudnorm −13 LUFS |
| E | **OpenArt Awards entry, "MY ENTRY · AI video ad"** (cover only, `pipeline/studio/thumb_openart.py`) | Announcement of his competition entry | Cover: black stage with orange rays and dust, white OpenArt wordmark, orange-glowing play ring, `@jawad_mp4` | – | "MY ENTRY" white grotesk, "AI video ad" orange serif italic, glowing underline | – | (the video itself is not in the repo) |

Covers: every reel has a 9:16 cover designed **3:4 grid-safe** (rows 240–1680), and A/B also have a 4:5 feed version (`reel/covers/`). Together the covers read as one family on his grid.

### 1.2 Do NOT repeat (concept, device or copy)
- **Memory / "can't delete" / heartbreak:**
  - no ERROR or delete dialogs about memories;
  - no "CAN'T DELETE THIS MEMORY";
  - no happiness meter crashing;
  - no Delete-vs-Cancel cursor hesitation;
  - no polaroids-of-the-past montage;
  - no burial at dawn.
- **Younger self / kid-meets-adult** dialogue; "Would your younger self be proud?".
- **AI tutorial or "I put myself into a movie"**, split-screen ORIGINAL vs AI, step-by-step screen recordings, clone walls, "Comment JD for the tutorial". The newest instruction is storytelling and relatable, not tool demos or portfolio.
- **An announcement of a competition entry.**
- **Copyrighted characters or IP** (Spider-Man/Goblin/MJ) and a dark red/blue superhero grade. Use original worlds and Jawad's own face (character sheets) instead. That also removes the copyright risk to reach.
- **Lip-synced trending dialogue as the spine.** This time the spine is **his own Hinglish/Roman Urdu voiceover**. A trending sound may sit under it, added in-app by Jawad.
- **Blob mascots / toy-like 3D props** (A/B). They read as "AI tool tutorial", not cinematic.

### 1.3 Signatures to KEEP (they are his visual identity and should recur in all 5 reels)

**Caption typography.**
- The keyword is a glowing orange **serif italic**, shaded from top to bottom:
  - in the code: `ORANGE_HI (1.0, 0.62, 0.20)` to `ORANGE (1.0, 0.36, 0.02)`;
  - in hex: about `#FF9E33` to `#FF5C05`.
- The rest of the line is white **Poppins 600** grotesk at about half the keyword's size (in Yaadein, 54 px white vs 104 px keyword).
- Keywords are marked `*word` in the script.

**The glowing "snake" guide line**, which reads as the orange underline on the covers.
- It is a thin hot line that draws ahead of the voice, with a fading tail and a bright head dot.
- It sits about 0.52 × the keyword size below the baseline.

**Caption motion.**
- A liquid expo glide in along a gently curved path (0.75 s, 70 px travel).
- A focus pull from a blur of about 10 px to sharp.
- A warm glow flares while the word enters, over a soft dark scrim behind the phrase.
- Exit: the phrase drifts on along the path and defocuses (0.55 s).
- Lines never overlap.

**`@jawad_mp4` end card** (`memories/ending.py`).
- The motion grammar:
  1. The last shot zooms out into a glowing orange ring.
  2. His photo fills the ring.
  3. The ring glides into a dark capsule badge (handle plus a one-line subline).
  4. A question headline in Unbounded 900, with the last line in orange gradient.
  5. An orange gradient pill with a chat icon, a sheen, a tap and a ripple.
- Use a new question and CTA per reel.
- About 70 % black and 30 % orange stage with slowly turning light rays.

**Story-UI metaphor.** SaaS glass panels are *story devices*, not decoration (in Yaadein, the delete dialog *was* the story). Keep the approach, but invent new metaphors for every reel.

**Cinematic finish.**
- Deep glow (AE style, 4 octaves), halation and anamorphic streaks.
- Light rays, dust and bokeh particles, film grain, vignette.
- True sub-frame motion blur.
- A warm orange rim light on the subject, masked outside the body.

**Pacing and openings.**
- Fast cuts (about 1.2 s per shot in Yaadein), with many transition types.
- Cold opens with a physical event in the first 0.2–0.5 s (lights clunking on, lightning, a lock-on).
- The hook text or caption appears in under 1 s.

**Covers.** A 9:16 cover per reel, 3:4 grid-safe, in the same type system (white grotesk line plus orange serif-italic keyword plus glowing underline). The three prior covers prove the family look.

**Red as the alert accent.** The ERROR red in Yaadein (`RED (1.0, 0.10, 0.06)`) maps naturally onto the new orange+red brand: red for tension and conflict beats, orange for warmth and keywords.

---------------------------------------------------------------------------------------------------------------

## 2. Jawad's taste profile (ranked)

Evidence key:
- **[U]** his own words in this project's chat.
- **[S]** his messages in the Reels Studio session.
- **[G]** git history of *his own* page reels (revisions he asked for).
- **[C]** revisions he directed on client reels: technique taste only, never content.

### 2.1 Likes / wants (most important first)
1. **Cinematic storytelling that is relatable** for Pakistani and Indian viewers, told "as a video editor and as a relatable person". **[U]**
   - Visuals explain the lyrics or voiceover line by line ("visuals explaining the lyrics and each and everything with voiceover"). Yaadein proves the model: each spoken phrase gets its own image or metaphor. **[U][G]**
2. **Roman Urdu / Hinglish**, with a **voiceover** by a Hindi-speaking voice. **[U]**
3. **Top-notch everything, original, scroll-stopping:**
   - "hook, sound design, grading, visuals, each and everything i want top notch";
   - "ideas will be original";
   - captions "no one has created like before";
   - 1M+ view potential;
   - "cinematic transitions, sound effects, music". **[U]**
4. **3D (Blender) + SaaS UI + motion graphics, moving smoothly.** **[U][S]** Long eased moves and "gentler punches" over jerky reframes. **[C]**
5. **Brand colours: orange + black.** His words were "orange and black" **[U]**. The current brief adds red; keep red as the second accent.
6. **Five completely different reels, 30–40 s,** with the same colour scheme, posted to see which performs best. **[U]**
7. **His face may be used** (character sheets attached). He also offered to **generate images himself from prompts**, so a short prompt list is a welcome deliverable. **[U]**
8. **Trending or viral audio is part of his playbook.** "i can use some viral audio lyrics from instagram… like i have did with a recent video" refers to Yaadein. **[U][G]**
9. **Clear, visible fonts that never fight the background,** in 3D, deep-glow and light-sweep styles. **[S]**
10. **Montages and fast clips for the hook;** cinematic camera angles and motion; every piece different; maximum quality and creativity. **[S]**
11. **The snake-caption look.**
    - It came from *his* reference ("ref 5") and his supplied sample with the Gwyner + Poppins glow.
    - He supplied the paid **Gwyner Condensed** font himself.
    - He then had it reused on both of his own page reels. **[G][C]**
12. **Covers that keep his grid consistent** (9:16 plus a 3:4-safe crop). **[G]**

### 2.2 Dislikes / rejections (strongest first)
1. **Synthetic or robotic TTS voiceover.**
   - The Piper TTS English VO on Genjutsu v2 was removed within 5 minutes (v3, "SFX only"). **[G]**
   - The new Hinglish VO must sound natural and native. A flat, mispronounced or robotic Hindi voice is the single biggest rejection risk.
2. **Portfolio or showreel framing.** "they dont need this portfolio" — the reels are relatable stories, not "look at my work". **[U]**
3. **Outro text like "watch the full video" with an arrow,** and third-party logos at the end. Replaced by the profile zoom-out end card; the Higgsfield logo was dropped from the result reel. **[G]**
4. **Over-designed end cards.** The liquid-glass SaaS end card over a liquid gradient was replaced by the **minimal** Genjutsu-style card. **[G]**
5. **Glass caption cards.** "SaaS pass 2: clean cinematic captions (**no glass**)". **[C]**
6. **Over-processed grades.** The "clarity" grade was reverted: "Back to the previous cinematic grade: footage untouched (**no clarity grade**)". He wants natural skin under a cinematic finish. **[C]**
7. **Light-leak washes on cuts** ("B-roll cuts **without** light-leak wash", "softer light-leak wash"), and visual clutter ("**fewer** ambient circles"). **[C]**
8. **Captions that overlap each other, cover faces, or leave the safe area.**
   - "each caption leaves before the next line enters" **[G]**
   - "Captions never cover her face", audited every 0.1 s **[C][G]**
   - The end card framed on the whole head, not one off-centre eye. **[G]**
9. **Mirrored text, flipped directions, hard reframe snaps, one-frame jump cuts.** **[C]**

### 2.3 Standing instructions
- **Sources:**
  - Use repo 100 only, with Reels Studio as the **engine only**.
  - Never copy client content, themes, looks, props or copy (Organic Fostering, Floret, Rida, Sukkar, Riphah, NOVA).
  - Do not use the portfolio repo.
- **Format:** 1080×1920 at 30 fps, 30–40 s.
  - His own past page reels were 60 fps. The 30 fps brief wins, so keep the shutter at 0.5/30 when porting `comp.render_frame`.
  - Key copy inside x 70–1010, y 230–1480. Nothing at x > 930 for y 1050–1700; the bottom 300 px stays clear.
- **Signature end card** with `@jawad_mp4`, a question headline and a comment CTA ("Comment mein batao" / "COMMENT YOUR ANSWER" pattern). The Genjutsu keyword-CTA pattern ("COMMENT 'JD'") is also proven for him. Use it only if a reel offers a real freebie.
- **Audio:**
  - Sound design must be designed and measured.
  - For his own reels, music or a trending track is welcome. Deliver the VO + SFX mix plus a stem, so he can drop a trending sound in-app.
  - On client work he said "add only sfx i will add the music later". **[S]**
- **No Higgsfield and no paid generation;** local tools only; `nice -n 10`; at most 2 threads per heavy job.
- **Status updates with time estimates in PKT.** He asked "how much time left… in pkt" several times. **[S]**
- **Work hygiene:** the lead commits and pushes; QA before delivery.

---------------------------------------------------------------------------------------------------------------

## 3. Reusable techniques and code: what each module does, its quality, and how to port it

Target: `pipeline/jawad_reels/`. It already holds the Reels Studio toolkit: `core`, `type3d`, `ui`, `footage`, `sprites3d`, `audio`, `render`, `package`, plus `project.json` with an orange/red palette remap and workspace `workspace/jawad_reels`.

### 3.0 Porting rules (all modules)
- **Canvas format.**
  - Toolkit canvases are `float32 (H, W, 4)`, premultiplied, linear light.
  - The `memories`/`studio` code uses `(H, W, 3)` linear canvases.
  - Ported code must write only `cv[..., :3]`. In particular, change the snake-caption scrim from `cv[...] = cv * (1 - scrim…)` to `cv[..., :3] *= …`, so canvas alpha is never darkened.
- **API differences.**
  - `memories/comp.disc_blur(img, diameter)` takes a diameter; the toolkit's `core.disc_blur(img, radius)` takes a radius. Halve the argument in a shim.
  - `comp.FPS = 60` becomes `K.FPS = 30`.
  - `comp.ROOT` (`workspace2`) becomes `wsconf.workspace()`.
  - The fonts folder becomes `wsconf.workspace() + '/fonts'`.
- **Easing.** Vendor `memories/anim.py` (127 lines, pure: AE-influence beziers, `Track`, `spring`, `wiggle`) with the captions and end card, so their feel is identical. Everything else uses `K.ramp`, `K.Track`, `K.spring`, `K.wiggle`.
- **Fonts.**
  - Poppins and Unbounded are on Google Fonts.
  - **Gwyner Condensed Italic is paid and was supplied by Jawad.** It is not on disk now. Ask him for the TTF.
  - Until then, use the fallback the gold reel already coded: Instrument Serif Italic (already in `project.json`) or Playfair Display Italic.
  - `captions.Phrase` auto-fits long phrases to the path, so a wider fallback still stays inside the safe area.
- **Purity.** Keep every module a pure function of `t`; `render.py` renders frames out of order in worker processes.
  - The `memories` code keeps lazy globals (`PH`, `POL`, `FLY`, `SHAT`). These are fine as `lru_cache` builds, but must not hold per-frame state.

### 3.1 From his own page reels (port these first)

| Module (branch:path) | What it does | Quality | Port into `pipeline/jawad_reels/` |
|---|---|---|---|
| `festive-lovelace:pipeline/memories/captions.py` (250 lines) | **Signature snake captions.** Per-glyph sprites along a cubic-bezier `Path`. Glowing guide line that draws ahead of the voice. Orange serif-italic keywords with a vertical gradient and glow. White Poppins with a soft drop shadow. Liquid glide in, focus pull, glow flare, drift and defocus out. Phrase auto-fit. Quarter-res scrim | **High.** It shipped on two reels, defines his look, and is fast (glyph LRU caches) | `snake_captions.py`. Apply the canvas and scrim fix above. Font paths come from wsconf. Keep the `*keyword` convention. Optional: drive keyword colour by beat (red for conflict lines). Layout presets `low(y)`/`high(y)` stay inside x 95–930. Place phrases off Jawad's face using the cut-out masks (gold `snake.py` technique). |
| `…/memories/ending.py` (432 lines) | **Signature end card.** Zoom-out into the ring, face-centred photo crop (Haar face plus head-silhouette centring), capsule badge, Unbounded headline lines, orange CTA pill with sheen, breathing, tap and ripple; stage with rays. `HEADLINE`, `USER`, `SUBLINE` and the CTA are module constants | **High**, iterated four times to taste | `endcard.py`. Make headline, subline, CTA text and photo parameters. Photo: a charsheet crop (e.g. `workspace/brand_reels/charsheet/crops/suit_smiling.png`) or a real photo from Jawad. Trim `END` from 7.4 s to about 4.5–5 s for retention (the card was 23 % of Yaadein). Needs `hud.Paint` and `hud.text_mask`; port those roughly 110 lines with it. The CTA line can be Hinglish ("Comment mein batao"). |
| `…/memories/hud.py` (328 lines) | Glass panels with two-colour edge light. Memory card with a scan line. Dialog with hover, press and cursor. Ring meter with a crash/glitch state. Progress "truth check". macOS cursor sprite. RGB-split `glitch()`. All painted at 2× as premultiplied RGBA and placed as 3D planes with frosted glass behind | **Medium-high.** The colours are Spider-Man red/blue and the copy is memory-specific | Take **`glitch()`, `cursor()`, the `Paint` helper and the glass-panel recipe**. Recolour the edges orange/red. For widgets prefer the toolkit's much larger `ui.py`. Never reuse the memory/delete/khushi panels or copy. |
| `…/memories/saas_hook.py` (151 lines) | Hook HUD: segmented lock-on reticle that spins and closes in on a tracked target, REC/timecode frame, a progress panel that fails with ERROR. AE-style deep glow on the overlay | **Medium-high** | Reuse the **reticle and REC frame** generically (e.g. locking onto Jawad's face or an object). New copy and new fail/success states only. |
| `…/memories/comp.py` (461 lines) | 2.5D camera over depth plates, sprite and image planes with DOF, `frosted()` glass, bokeh `particles`, world-space `rain`, and post: `deep_glow` (4-octave AE deep glow), `halation`, `anamorphic`, `chroma_fringe`, `god_rays`, `grade(look)` with split-tone, crushed blacks and the `'orange'` end-card look, `grain`. Shutter `render_frame` | **High** (the finish he approved) | The toolkit `core` already has halation, anamorphic, god rays, grain, motion blur and DOF. Port **`deep_glow`, `grade('orange')` and a new warm-black split-tone** into a `look_ember.py` finishing chain (or a new `core.LOOKS['ember']` via the motion-toolkit-engineer). The built-in looks `neon`/`amber`/`airy` are Organic Fostering identities, and the palette remap alone is not enough. |
| `…/memories/fx.py` (281 lines) | `Shatter` (an image breaks into triangular glass shards flying at the lens), lightning, fireball, `light_leak`, drift particles (embers, dust, petals), `whip`, `radial_blur`, polaroid sprites, optical-flow 30→60 fps clips | **Medium-high** | `fx_jawad.py`: **Shatter, drift particles, whip/radial blur**. Use leaks sparingly (he disliked washes on cuts). The optical-flow 60 fps code is not needed at 30 fps. |
| `…/memories/reel.py` (828 lines) | Shot table, per-shot camera tracks, **14 transition kinds in one `transitions()` pass** (whip, spin, zoom, flash, leak, glitch, dip, dissolve that renders the neighbour shot), handheld operator drift with micro-jitter, foreground lens-close bokeh, per-shot exposure and look, SFX cue sheet with `add(t, kind, gain, …)` | **High** structure | Copy the **transition dispatcher, handheld() and fg_depth()** patterns into each reel module or a shared `cuts.py`. Use flashes as local glows, not full-frame lifts: the toolkit QA rule "no full-frame flash that lifts blacks" is stricter than Yaadein. Motion-blur samples must not cross cuts. |
| `…/memories/sound.py` (463 lines) | Synth SFX voices: braam, sub_drop, impact, whoosh/whoosh_slow, reverse_swell, riser, glass, thunder, rain_bed, fire, heartbeat, glitch, thwip, click, pop, ticks, shimmer, tape_stop, chimes, wind, blade, tinnitus, buzz, rope. Stereo `Bus` with pan. `best_continuation` and `extended_music` (extend a music bed by spectral matching). Duck SFX under the voice | **High** for emotional cinema SFX | The toolkit `audio.py` (2622 lines) is the main library. **Add the missing emotional voices** (braam, heartbeat, tinnitus, tape_stop, reverse_swell, chimes, glass) as `<reel>_sfx.py` registrations or a `sfx_cinema.py`. Reuse `extended_music` to stretch a licensed bed under the end card. |
| `festive-lovelace:pipeline/studio/studio.py` (729 lines) | **One still to a live cinematic shot.** Speaker-following 2.5D camera keyed to the dialogue (`CAM_KEYS`). `voice_env()` drives the speaker's rim glow from the audio. Volumetric spotlight cones × drifting multi-octave haze. Cold-open light "clunk" flicker. Dust and bokeh lit by the cones. Person-mask DOF. Mask-out orange deep-glow rim. `netflix()` grade (ACES-ish, teal shadows, warm skin, milky floor, S-curve). `music_bed()` continuation | **High**, and the most relevant to the new brief (his face from character sheets staged in cinematic worlds) | `stage.py`: a generic "still plus masks to shot" class. Feed it Jawad's character-sheet cut-outs (RVM or rembg mattes) composited into Blender-lit sets. Drive the rim glow and push-ins from **his VO envelope**. Keep the grade warm (the brand). The teal shadow push can stay subtle for contrast. |
| `…/studio/thumb.py`, `thumb_openart.py`, `memories/thumb_yaadein.py` | Cover generators: big snake-caption title (`K.WHITE_PX=84`, `K.KEY_PX=218`), underline guide, rays, dust, 3:4 grid-safe rows 240–1680, extra grid and feed previews | **High** (the cover family) | `cover.py`: one function `cover(still, white_words, key_words, sub)` that writes 9:16 plus 3:4 and 4:5 previews for all 5 reels. |
| `beautiful-planck:pipeline/engine.py`, `reel.py`, `reel2.py`, `audio.py`, `blender_assets.py` (Genjutsu) | Small numpy/OpenCV compositor: `text_sprite` with a gradient, `pill()` with icon, gradient, border and tracking, glass cards in 3D tilt, 3D cursor clicks with ripple, step progress bar, card fan and clone wall, `profile_ending()` zoom-out to a badge. Blender glossy blob mascots. Procedural score and SFX | **Medium.** Superseded by the toolkit (ui and type3d) and by `ending.py` | Take ideas only: **pill() styling and the comment-keyword CTA**. Drop the blob mascots (toy look). |
| `beautiful-planck:pipeline/tts/lines.txt` (Piper TTS) | English TTS VO script | **Rejected by Jawad** (removed in v3) | Do not reuse Piper. For Hinglish, send **Devanagari** text to the TTS (Roman Urdu input gets mispronounced). A/B the voice before building picture to it. |

### 3.2 From the Reels Studio toolkit (engine: use as is)

| Module | What it does | Use for Jawad | Watch-outs |
|---|---|---|---|
| `core.py` | Linear premultiplied compositor; 3D `Cam` (orbit, DOF aperture); depth-sorted `Scene` (planes, billboards, custom, particles); `Particles`; `light_leak`, `god_rays`, `whip_blur`, `zoom_blur`, `halation`, `anamorphic`, `grain`; `post(look)`; eases (`easy_ease`, `out_expo`…); `Track`, `spring`, `impulse`, `shake`, `beat` | Every reel's camera, layering and finish | Looks `neon`/`amber`/`airy` are client identities. Build an `ember` look (black void, orange/red rim, rays, dust). The `post(flash=)` ivory term lifts blacks, so check YMIN. |
| `type3d.py` | Extruded / chrome / gold / deep_glow / neon / glass_pill text; `Glyphs` kinetic animators (rise, slam, typewriter, wipe, track, flip, scramble); `Counter` odometer; `VideoType` (footage inside letters, zoom-through); `OrbitText`; `measure()` | Hero slams, numbers, "type as world" moments | It has no serif-italic glow keyword preset: use `snake_captions.py` for that. Check widths with `measure()` against the 940 px safe width. |
| `ui.py` (3171 lines) | Glass cards, app window, widgets, cursors, bar chart, dock, orbit ring of tags | The SaaS-UI-as-story-metaphor scenes | Recolour to the ember palette; keep panels to 1–2 per beat (he disliked clutter). |
| `sprites3d.py` + `assets3d_*.py` | Blender (`bpy` 5.2, Cycles) builders writing PNG sequences plus `meta.json` (yaw, spin and anim modes; day and night) | Pattern for a new `assets3d_jawad.py` | The existing props (house, heart, £ coin, school bus, backpack…) are **fostering client props: never reuse**. CPU only here: `threads=2`, low samples plus OIDN. |
| `audio.py` | Procedural SFX library, cue mixer (`align='hit'`), loudness, stems | All SFX | With a VO and music: about −14 LUFS integrated, ≤ −1.5 to −2 dBTP after AAC; SFX ducked under the VO (the Sukkar `final_audio.py` fast-attack/slow-release duck, or Studio's `duck = 1 − 0.55·env(vo)`). |
| `render.py`, `package.py` | Parallel renders (`--stills`, `--sheet`, `--preview`, `--workers`), 2-pass 22 Mbps Instagram MP4, CRF 14 master, stem, cover | Delivery | `--workers 2` under `nice -n 10`. `project.json` already has `"deliver": {"dir": "reel/jawad_reels", "prefix": "jawad"}`. |
| `skills/trending-captions/make_captions.py` | faster-whisper word timing → `.ass` presets (bold-pop, karaoke, boxed, minimal), `.srt`, safe-zone report | **SRT export and the safe-zone report**; word timings for the VO | Its presets are not his look; burn-in captions come from `snake_captions.py`. |
| `skills/reels-production-playbook/qa_measure.py` | Measured QA (safe zones, signalstats, ebur128) | Final QA | – |

### 3.3 From client branches: techniques only (no content, look, copy or props)

| Technique (where) | Why it helps Jawad's reels |
|---|---|
| **Roman Urdu ↔ Whisper alignment with Devanagari transliteration** (`video-editing-references:pipeline/rida/align.py`) | Whisper (`hi`) returns Devanagari for Hindi/Urdu speech. Transliterate it, then difflib-align it to the Roman Urdu script to get exact per-word caption timings for the Hinglish VO. Also reports missing or repeated lines. **High value.** |
| **Person matte with Robust Video Matting (ONNX)** (`festive-lovelace:pipeline/gold/matte.py`) | Puts type and 3D *behind* Jawad's character-sheet cut-outs or any footage, separates him from the stage for parallax, and drives the rim glow masks. |
| **Face-tracked snake paths** (`gold/snake.py`, `gold/track_face.py`, `rida/facetrack.py`) | Caption curves rebuilt each frame around the tracked face, so captions never cover it (a standing dislike). |
| **Virtual multi-cam from one shot** (gold `timeline.py` camera layers: authored moves + a per-phrase angle-snap edit layer + an edge guard) | Turns one still or VO scene into a fast-cut "edited" feel without new footage. |
| **SRT export** (`gold/export_captions.py`) | Upload captions for accessibility and SEO. |
| **Fit a look LUT from matched pairs** (`sleepy-ritchie:pipeline/sukkar/fitlook.py`) | Fit one warm-dark "Jawad cover" grade (from his three covers) and apply it to all Blender plates, so the 5 reels match his grid. |
| **Dialogue cleanup with DeepFilterNet3 + duck SFX under speech** (`sukkar/final_audio.py`) | If Jawad records his own VO on a phone, clean it locally. |
| **faster-whisper transcription; sync check by cross-correlation** (`sukkar/transcribe.py`, `synccheck.py`) | VO timing QA. |
| **Reference SFX slicing with Demucs** (`rida/extract_sfx.py`) | **Analysis only.** Never ship SFX cut from someone else's reel. |
| NOVA (`vigilant-hamilton`), Riphah (`affectionate-archimedes`), Floret PDF (`zealous-volta`) | Nothing reusable for the reels. NOVA's Seedance prompts need paid generation, which is not allowed. Its storyboard and bible format can inform the image-prompt list Jawad offered to generate himself. |

### 3.4 Suggested build order in `pipeline/jawad_reels/`
1. **Shared modules:**
   - `anim_ae.py` (vendored `memories/anim.py`)
   - `snake_captions.py`
   - `endcard.py` (+ `hud_paint.py`)
   - `fx_jawad.py`
   - `look_ember.py` (or `core.LOOKS['ember']`)
   - `stage.py`
   - `cover.py`
   - `sfx_cinema.py`
2. **Alignment:** `vo_align.py`, the `rida/align.py` method. The VO script is written in Roman Urdu with `*keywords`; TTS gets Devanagari; Whisper times are aligned back to the Roman words.
3. **Reels:** one module per reel (`reel1.py`…`reel5.py`) on the toolkit contract `DUR, LOOK, draw(t), post, samples, cues`, each with its own look variation inside the brand.
4. **Verification:** `render.py --sheet` and `--stills`, then QA (two lenses), then `package.py`, then `cover.py`.

---------------------------------------------------------------------------------------------------------------

## 4. Safe-to-claim facts about Jawad (found in repo 100 only)

| Fact | Evidence in repo 100 | How to use it |
|---|---|---|
| Instagram handle **@jawad_mp4** | `pipeline/reel.py` / `reel2.py` `USER`, `memories/ending.py` `USER`, `tts/lines.txt`, covers | End card, cover signature |
| First name **Jawad** | marketplace `jawad-reels`, owner `jawad150` | "Main Jawad…" in a VO is fine. **Do not use any full name** (it only appears outside repo 100) |
| He is a **video editor / motion designer** who makes reels and 3D motion graphics | His own words in this project; repo 100 is his production repo (Blender, motion pipelines) | "Ek video editor ki life…"-style first-person storytelling |
| He does **client work** | Several client reel projects exist in the repo | Only **generically** ("client ka call", "revision #7"). **Never name or show a client** or their content |
| He makes **AI video** work | Genjutsu "I put myself into a movie" reels; OpenArt Awards "MY ENTRY · AI video ad" cover | "I make AI videos" is OK. **Only "entered"** OpenArt; **no** "winner", "finalist" or "award-winning" |
| His **face** may be used | Character sheets (streetwear, 3-piece suit) supplied with explicit permission ("if you want to use my face you can") | Hero shots, end-card photo, cover |
| Audience: **Pakistani + Indian**, language Roman Urdu / Hinglish | His brief | Language and relatability choices. Not an on-screen claim |
| Probably Pakistan-based (asks for times in PKT) | Session messages | Do not state on screen unless he confirms |

**No other facts are safe.** The repo has no follower counts, view counts, number of clients, years of experience, rates or earnings, awards won, brand partnerships or testimonials. **The reels should run on relatable storytelling** (the universal editor or creator struggle, Desi-life moments, emotions in the voiceover), not on credentials or numbers. Any number on screen must be part of the story (e.g. "Revision #27"), never a claim about Jawad.

---------------------------------------------------------------------------------------------------------------

### Open questions for Jawad (only these block quality)
1. **Font:** please share the **Gwyner Condensed Italic** TTF used on the prior covers. It is paid and not in the repo. Until then the fallback is Instrument Serif Italic or Playfair Display Italic.
2. **End-card photo:** should it be a real photo of him, or a character-sheet crop? (`ending.py` face-centres either.)
3. **VO voice:** confirm the voice after a 10 s A/B sample (a natural Hindi accent). The Piper-style robotic VO was rejected before.
4. **Music:** should he add a trending sound in-app (we deliver a VO + SFX mix and a stem), or should the reels ship with a licensed bed already mixed?
