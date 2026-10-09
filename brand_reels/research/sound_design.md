# Sound design for the @jawad_mp4 reels: SFX library, music beds, mix and master spec

Roles: reels-studio **sound-designer** + **music-supervisor**. Date: 2026-10-08.
Scope: an inventory of the toolkit's procedural SFX library (`audio.py`), the epic/cinematic and desi sounds it
was missing (now built), a curated CC0 / public-domain sample kit, original music-bed options (tested on this
CPU-only machine), and the mix/master spec for VO-led reels.

> Client brief: *"use sound designer agent as well for sfx and the sound library we installed for cinematic sfx
> to make the story telling more epic"*. Jawad's page is his own brand, so nothing here reuses the Organic
> Fostering / Floret sounds-by-story (coins, £, seed plips, birds). Their *engine* (audio.py) is reused; the new
> sounds and beds are his.

---------------------------------------------------------------------------------------------------------------
## 0. TL;DR

| Deliverable | Path | Status |
|---|---|---|
| New sound module (registers into audio.py via `register()`, audio.py untouched) | `workspace/brand_reels/sfx/epic_sfx.py` | **40 sounds** (29 synthesised + 11 CC0/PD samples), all `qc() == []` |
| Spectrogram sheets of every new sound | `workspace/brand_reels/sfx/out/epic_sheet_{1..4}.png` | viewed, notes in section 3 |
| Audition WAV of all non-bed sounds, plus a time index | `workspace/brand_reels/sfx/out/epic_catalog.wav` (+ `_index.json`) | 135.8 s, -18.0 LUFS, -2.2 dBTP |
| CC0 / PD sample kit + licences | `workspace/brand_reels/sfx/library/` + `library/LICENSES.md` | 27 MB: Kenney x5, OpenGameArt x6, Wikimedia PD/CC0 x6 |
| Original procedural music beds (4 styles) | `workspace/brand_reels/sfx/epic_music.py` | 30 s bed renders in 6-10 s; tempo exact, phase <= 10 ms |
| VO-reel mix + master (A: full mix, B: VO+SFX only, stems, AAC two-pass loudnorm) | `workspace/brand_reels/sfx/epic_mix.py` (+ `mixtest.py`) | tested end to end: A -14.06 LUFS / -2.30 dBTP, AAC -13.9 LUFS / -2.0 dBTP |
| Local AI music test (ACE-Step 1.5, MIT, CPU) | `workspace/brand_reels/sfx/aimusic/` | works on CPU. Run 2 (LM codes + Q8 DiT): 6.7 min per 30 s, on grid (x11.7), but the music stops at 22 s. Usable as a source, not a drop-in bed (section 5.3) |

Recommendation:
- Bed for version A: the **procedural numpy bed** (`epic_music.py`). It is licence-clean (we own every note),
  sits exactly on the edit's BPM grid, and is fast.
- Version B: **VO + SFX only**, delivered for every reel so Jawad can add a trending Instagram sound in-app.
- ACE-Step 1.5 (MIT): a second, optional bed source when Jawad wants a "produced track" feel. Generate 40 s,
  cut and loop on bar lines with `beatgrid`, then limit (section 5.3).
- MusicGen: excluded. Its weights are CC-BY-NC.
- Stable Audio Open Small: needs a Hugging Face token plus acceptance of the Stability licence. Open question
  for the lead.

---------------------------------------------------------------------------------------------------------------
## 1. Inventory: the installed library (`audio.py`, 45 sounds)

Run: `cd pipeline/jawad_reels && python3 audio.py catalog` (10.8 s). `audio.py` is identical in
`plugins/reels-studio/toolkit/` and `pipeline/jawad_reels/`.

Conventions:
- 48 kHz stereo float, deterministic (seeded).
- Each sound's max momentary loudness is pre-balanced to REF -20 LUFS plus a per-sound offset, so `gain_db=0`
  is the correct starting level.
- `hit` = the designed hit: the transient for impacts; the end for risers and reverse sounds; the end of the
  motion for motion-tracking sounds (cue those with `align='start'`).
- Every sound passes `qc()`: no clicks, no DC, peak <= -1 dBFS.

| sound | cat | params | sound | cat | params |
|---|---|---|---|---|---|
| `heartbeat` | impact | n=2, bpm=62 | `ui_click` | ui | pitch=1 |
| `impact_big` | impact | tail=1 | `ui_tick` | ui | pitch=1 |
| `impact_soft` | impact | - | `ui_hover` | ui | - |
| `sub_drop` | impact | dur=2.4 | `typing` | ui | n=12, cps=11 |
| `flash_hit` | impact | - | `pop` / `bubble_pop` | ui | pitch=1 |
| `logo_sting` | impact | tone=1 | `check_ding` / `toast_chime` | ui | pitch=1 |
| `whip` | transition | direction=1 | `toggle_on` | ui | - |
| `whoosh_fast` / `whoosh_slow` | transition | direction=1 | `glass_tap` | ui | pitch=1 |
| `whoosh_by` | transition | dur=1.4, speed=62, dist=1.6, direction | `card_slide` | ui | dur=0.42 |
| `swish_small` | transition | direction=1 | `puzzle_click` | ui | - |
| `air_zoom` | transition | - | `camera_shutter` | ui | - |
| `riser` | transition | duration=2 | `slider_drag` | ui | duration=1, detents=28 |
| `reverse_swell` | transition | duration=1.5 | `bar_grow` | ui | duration=0.8, pitch=1 |
| `downlifter` | transition | dur=2 | `shimmer` / `ripple` | texture | dur |
| `glitch_short` | ui | - | `sparkle` | texture | - |
| `coin_flip` / `coin_ring` / `coins_burst` / `cash_kaching` | money | (pitch / n) | `grow_swell` | texture | duration=2.5 |
| `slot_tick` | money | n=16, dur=1.2, ease | `seed_plip` / `leaf_rustle` | texture | (dur) |
| `room_tone` / `night_air` / `outdoor_birds` | bed | dur (loops) | | | |

Brand note:
- Usable for Jawad: impacts, whooshes, risers, UI, `camera_shutter`, `typing`, `glitch_short`, `shimmer`,
  `logo_sting`, `room_tone`, `night_air`.
- Fostering-flavoured and to avoid as signature sounds: coins, cash, `seed_plip`, `grow_swell`, `leaf_rustle`,
  `outdoor_birds`.

### Gap analysis (requested epic sounds vs the installed library)
| Requested | In audio.py? | Now provided by |
|---|---|---|
| braam / trailer horn | no | `braam` (synth, root D1) |
| deep cinematic boom with long tail | partial (`impact_big`, 6 s) | `cinematic_boom` (9-10 s thunder roll + canyon echoes) |
| sub-bass drop | **yes** (`sub_drop`) | (use as-is) |
| reverse cymbal | partial (`reverse_swell`) | `reverse_cymbal` (synthetic crash reversed with its hall) |
| tension drone | no | `tension_drone` (cue) + `dark_drone` (bed loop) |
| heartbeat build | partial (`heartbeat` at a fixed bpm) | `heartbeat_build` (accelerating, last beat on the hit) |
| clock ticking | no | `clock_tick` (synth, accelerating option) + `clock_real` (PD sample) |
| glitch / data corruption | partial (`glitch_short`, 0.6 s, tasteful) | `glitch_corrupt` (tear + stutter + bitcrush + sample-and-hold + dropouts) |
| tape stop | no | `tape_stop` + `tape_stop_fx(x, t0, dur)` to stop the real bed |
| vinyl rewind | no | `vinyl_rewind` (backspin, ends on the cut) |
| film projector | no | `projector_start` (spin-up to 24 fps) + `projector_loop` (bed) |
| camera shutter | **yes** (`camera_shutter`) | (use as-is) |
| crowd gasp / cheer | no | `crowd_ooh` (synth fallback) + `crowd_cheer_real`, `crowd_ahh_real`, `crowd_ooh_real`, `applause_real`, `applause_build_real` |
| phone notification | partial (`toast_chime`) | `notif_ping` (original pop + G6 bell, optional haptic buzz) |
| keyboard typing | partial (`typing`, soft laptop) | `keyboard_burst` (mechanical thock) + `typing_modelm_real` |
| mouse clicks | partial (`ui_click`) | `mouse_click` (micro-switch press + release, double) |
| Premiere / AE UI sounds | partial (UI kit) | `timeline_scrub` (audio-scrub chatter), `mouse_click`, `keyboard_burst` |
| render-complete ding | partial (`check_ding`) | `render_complete` (original rising arpeggio + sparkle) |
| laptop fan spin-up | no | `laptop_fan` |
| rain / night-city ambience | partial (`night_air`) | `rain_city_night` (synth bed), `rain_real`, `rain_thunder_real` (samples) |
| tabla hit | no | `tabla_hit` (strokes na/tin/ta/ge/ke/dha/dhin, pitchable) |
| dholak roll | no | `dholak_roll` (crescendo fill ending on an accented "dha") |
| sitar pluck | no | `sitar_pluck` (jawari buzz, taraf shimmer, meend bend) |
| harmonium swell | no | `harmonium_swell` (two-reed bellows swell, any chord) |
| azaan-free city ambience | no | `desi_city` (traffic, horns, 2-stroke rickshaw pass, murmur; no azaan, no music) |
| *(extra)* dhol slam, taiko/anvil trailer hit, Shepard riser, editor-room bed | no | `dhol_hit`, `trailer_hit`, `shepard_riser`, `edit_suite` |

---------------------------------------------------------------------------------------------------------------
## 2. Free, legally usable SFX sources (reachability tested from this machine on 2026-10-08)

| Source | Reachable | Licence | Verdict |
|---|---|---|---|
| **Kenney.nl** audio packs | yes | **CC0 1.0** (`License.txt` in every zip) | **Used**: interface-sounds, impact-sounds, ui-audio, sci-fi-sounds, digital-audio (418 OGG, 10 MB) |
| **OpenGameArt.org** (CC0 filter) | yes | **CC0**, checked per page | **Used**: applause (church), crowd shouting, crowd "ooo", rain loop, high-traffic road, "30 CC0 SFX loops" |
| **Wikimedia Commons** (CC0 / PD only) | yes, but `upload.wikimedia.org` rate-limits (HTML error pages) | CC0 / public domain (many PD files come from the old PDSounds archive) | **Used**: rain+thunder, slow-starting applause, "ohhh ahhh", clock ticking, Model M typing, laptop typing. 6 more files queued (`LICENSES.md`) |
| Hugging Face datasets | yes | mixed | `MoamenElSayed/freesound-commercial-50k`: 83 GB, per-row licence column (CC0 = 0). The datasets-server filter index did not load in 5 min. Option for later: pull CC0 rows by title. `SoundSafari/Public-Domain-Music`: CC0 music, possible bed source. Other freesound mirrors (`benjamin-paine/freesound-laion-640k-commercial-16khz`) are 16 kHz and CC-BY: not used |
| archive.org | yes | per item | Search is noisy (speech, full albums). No clean CC0 SFX pack found in the time box. Not used |
| freesound.org / pixabay.com | **blocked (403)** | (CC0 / Pixabay licence) | Not used |
| Sonniss GDC bundles | **blocked (403)** | royalty-free (terms not re-verifiable here) | Not used. The bundles are also tens of GB |
| Mixkit | yes | Mixkit "Free" SFX licence: commercial and social OK, no attribution, no redistribution as a pack | Usable, but not CC0 and has no bulk download. Left out to keep the kit CC0/PD-only |
| **BBC Sound Effects (RemArc)** | yes | **personal / educational / research only** | **Do not use**: Jawad's page is a commercial personal brand |
| Wikimedia CC BY / BY-SA (sitar, tabla, projector recordings) | yes | attribution, share-alike | Skipped. Attribution in every Reel caption is impractical, and BY-SA is viral |

Kit:
- Location: `workspace/brand_reels/sfx/library/<source>/...`, 27 MB, well under the 400 MB budget.
- Per-file licences and URLs: `library/LICENSES.md` and `library/wikimedia/manifest.json`.
- Downloads are untrusted data. Each source has its own folder; the files were only ever decoded by ffmpeg into
  `sfx/samples48/`, and nothing in them is executed.

---------------------------------------------------------------------------------------------------------------
## 3. `epic_sfx.py`: the new sounds (registered into audio.py's catalog)

### Usage
- Pattern: the one from sound-designer.md step 4. `audio.py` is never edited.
- Put `import epic_sfx; epic_sfx.register()` at the top of `cues()` in `<module>_sfx.py`.
- Path setup: add `workspace/brand_reels/sfx` to `sys.path`, or copy `epic_sfx.py` next to `audio.py` in
  `pipeline/jawad_reels/` (recommended so it is committed). It finds the toolkit itself: `pipeline/jawad_reels`
  first, then the plugin.
- Sample sounds register only when their files exist under `LIB` (override with `EPIC_SFX_LIB`).
- Sample files are decoded by ffmpeg into `samples48/`, never imported. All three modules work under `python3 -I`,
  which was verified; use it when sample sounds are involved.
- Verify: `python3 epic_sfx.py check [names]` prints stats and qc and writes spectrogram sheets.
- Audition one sound: `python3 epic_sfx.py play braam '{"dur": 3}' out.wav` writes the wav and a PNG.

Measured (`out/epic_check.txt`):
- `qc() == []` for all 40 new sounds.
- Synth render time 0.0-1.0 s per sound and 0.5-5.5 s per bed (cached after the first render).
- Beds loop seamlessly: the wrap step is below the 99.9th-percentile sample step.

| name | cat | hit | dur s | Mmax LUFS | params | best use for Jawad |
|---|---|---|---|---|---|---|
| `braam` | impact | 0.04 | 6.9 | -17 | root=36.71 (D1), dur, growl, bright | title slam / "AI video ad" reveal / cut to black |
| `cinematic_boom` | impact | 0.003 | 10.4 | -16 | tail | the one hero slam per reel (black frame, keyword lands) |
| `trailer_hit` | impact | 0.003 | 4.5 | -17 | pitch | word slams on the beat, montage hits |
| `dhol_hit` | impact | 0.003 | 3.8 | -18 | pitch | desi energy cut, "bas!" moments |
| `heartbeat_build` | impact | **end** | 5.3 | -21 | duration, bpm0, bpm1 | suspense before a reveal (lands on the reveal frame) |
| `shepard_riser` | transition | **end** | 5.7 | -21 | duration, octaves_per_s | endless-rise tension into the drop |
| `reverse_cymbal` | transition | **end** | 2.0 | -22 | duration | suck into a slam (pair with braam/boom) |
| `glitch_corrupt` | transition | 0 | 1.4 | -24 | dur, intensity | "ERROR / can't delete this memory" device, corrupt-timeline transitions |
| `tape_stop` | transition | 0 | 1.0 | -24 | dur, tone | "music dies" beat before a punchline (or `tape_stop_fx` on the bed itself) |
| `vinyl_rewind` | transition | **end** | 1.1 | -23 | dur | "ruko... rewind" flashback cut |
| `dholak_roll` | transition | **end** | 2.5 | -22 | n, bpm | desi fill into a hit |
| `notif_ping` | ui | 0 / 0.40 (buzz) | 2.6 | -24 | pitch, buzz | client DMs / "new message" pops |
| `keyboard_burst` | ui | 0.001 | 1.7 | -29 | n, cps | prompt typing, editor at work |
| `mouse_click` | ui | 0.001 | 0.4 | -31 | double | cursor clicks in the NLE UI |
| `render_complete` | ui | 0.001 (first note) | 4.0 | -22 | pitch | render bar hits 100 % (in D minor use `pitch=0.7937` = Bb major, the VI chord) |
| `timeline_scrub` | ui | 0 (align start) | 1.8 | -31 | duration, speed | playhead scrub / J-K-L shuttle |
| `clock_tick` | ui | 0.001 | 5.8 | -29 | n, bpm, accel | deadline pressure (accel 1.05-1.1) |
| `tension_drone` | texture | **end** | 8.8 | -26 | duration, root | under the problem / setup section |
| `laptop_fan` | texture | **end** (align start) | 4.1 | -30 | duration | "render shuru" (render starts), machine working hard |
| `projector_start` | texture | **end** (align start) | 2.9 | -29 | duration | flashback / "film" opener |
| `tabla_hit` | texture | 0.002 | 1.5 | -23 | stroke, pitch | desi accents on beats (tuned D4 by default) |
| `sitar_pluck` | texture | 0.002 | 4.4 | -24 | note, meend, dur | tonal sting in key (note=62 = D4) |
| `harmonium_swell` | texture | peak at 0.72 x duration | 3.5 | -26 | duration, notes | emotional desi swell (yaadein / "younger self" moods) |
| `crowd_ooh` | texture | 0.08 | 4.4 | -24 | n | synthetic fallback only; prefer the real samples |
| `dark_drone` | bed | loop 24 s | | (-20 int.) | dur | dark storytelling floor |
| `rain_city_night` | bed | loop 20 s | | | dur | night edit-suite mood |
| `desi_city` | bed | loop 24 s | | | dur | street / "Karachi-Mumbai" texture (no azaan, no music) |
| `edit_suite` | bed | loop 16 s | | | dur | editor's room floor |
| `projector_loop` | bed | loop 8 s | | | dur, fps | cinema / flashback |
| `rain_real`, `rain_thunder_real`, `traffic_real` | bed | loops 16-20 s | | | - | real-world beds (CC0/PD) |
| `applause_real`, `applause_build_real`, `crowd_cheer_real`, `crowd_ahh_real`, `crowd_ooh_real` | texture | onset | 1.9-12 | -25 / -26 | - | win, "you made it", reaction beats |
| `clock_real`, `typing_modelm_real` | ui | onset | 4-6 | -29 / -30 | - | real ticks / clacky vintage typing |
| `bell_impact_real` | impact | 0 | 1.5 | -26 | - | deadline bell (Kenney CC0) |

### Spectrogram review (sheets viewed)
- Impacts: `braam` shows the brass harmonic stack, a sub under 60 Hz and a hall tail. `cinematic_boom` has sub
  energy decaying over about 8 s with a rolling LFO.
- Tails: early `trailer_hit`, `dhol_hit` and `tabla_hit` had hard low-frequency cut-offs at their buffer end.
  They were fixed with tapers and shorter decays; the re-check is clean.
- `reverse_cymbal`: the first version was dull, with 300-1 kHz dominating. It was re-voiced (modes above 700 Hz,
  brighter tilt, crescendo shaping) and now builds to the hit with 3-15 kHz energy.
- `rain_city_night`: the first version was rumble-heavy. It was rebalanced; the droplets and wash now dominate
  1-12 kHz.
- `desi_city`: horns were raised and are now visible as 0.4-1.2 kHz tonal bursts.
- Desi instruments:
  - `sitar_pluck`: the sweep of the jawari brightness peak shows in the first 0.5 s.
  - `tabla_hit`: harmonic dayan modes (1-5x) plus the upward bayan glide.
  - `harmonium_swell`: the bellows swell peaks at 72 % of its duration.
- Honest limits: everything synthetic was judged from spectrograms and numbers only, not by ear. The weakest
  sounds are:
  - `crowd_ooh`: reads as a broadband formant mush. Use the real crowd samples instead.
  - `sitar_pluck` / `tabla_hit`: plausible timbres, but not a recorded instrument.
  - Action for a human listen: audition `out/epic_catalog.wav` (index in `epic_catalog_index.json`) before the
    master.

---------------------------------------------------------------------------------------------------------------
## 4. Epic storytelling: sound playbook for Jawad's reels

The house devices:
- the **glowing serif keyword slam**;
- the **"ERROR" glass-UI card**;
- **editor world** UI (timeline, render bar, cursor);
- **warm dark cinematic** spaces;
- the **desi** heart.

Mapped to sound:

| Moment | Recipe (cue list) | Notes |
|---|---|---|
| Hook, frame 0 | `trailer_hit` + `sub_drop` (-4 dB) at t=0, or `braam` if the first frame is the keyword | Sound on frame 0 stops the scroll. Keep the VO start at 0.3 s so the hit is heard first |
| Keyword slam (serif word lands) | `reverse_cymbal` (duration = whip length, ends on the land) -> `trailer_hit` at the land; underline draw-on = `swish_small` (align start) | One slam family per reel; never a braam on every word |
| The big reveal (1 per reel) | `shepard_riser` (2-4 bars) + `reverse_cymbal` into it, then **0.25-0.4 s of near-silence** (`tape_stop` or `tape_stop_fx` on the bed), then `braam` + `cinematic_boom` on the cut | Silence before the hit is what makes it epic: the bed ducks to nothing |
| Tension / problem setup | `tension_drone` (align start, ends on the turn) + `clock_tick` (accel 1.06) or `heartbeat_build` landing on the turn | Pick one pulse source, not both |
| "ERROR" card / memory glitch | `glitch_corrupt` on the card pop, `mouse_click` on the X | glitch at -3..-6 dB under VO |
| Editor-at-work montage | `keyboard_burst`, `mouse_click`, `timeline_scrub` (align start at playhead drag), `notif_ping` (client message), `laptop_fan` (render starts, align start), `render_complete` on 100 % | UI layer at -6..-10 dB under VO; pan to screen x |
| Flashback / younger-self | `vinyl_rewind` (ends on the cut) or `projector_start`, bed `projector_loop` at -30; `harmonium_swell` peaking on the emotional line | Pitch tonal sounds into the bed key (D) |
| Desi accent | `tabla_hit` (dha/na) on 2 beats, `dhol_hit` on the drop, `sitar_pluck` note=62 as a 1-note sting, `dholak_roll` into a section | Max 2-3 desi accents per reel unless the bed is desi |
| Win / social proof / CTA | `applause_build_real` or `crowd_cheer_real` (-6 dB), `logo_sting` (toolkit) on the end card | Real crowd samples over the synthetic `crowd_ooh` |
| End card (@jawad_mp4, hold >= 1.5 s) | `logo_sting` on the mark + bed tail; `cinematic_boom` only if the reel has not used it | The tail must fit inside DUR |

Rules:
- These stay as in sound-designer.md:
  - **never a sound without a visible cause**;
  - **no more than ~3 sounds on one instant**;
  - hero hits only on hero events;
  - exits get tails, never hard stops.
- Under VO, keep busy SFX out of 1-4 kHz. Use the cue keys `lp` / `hp`, or drop the cue 4-8 dB.

---------------------------------------------------------------------------------------------------------------
## 5. Music beds: two versions per reel, plus the options tested

### 5.1 Policy: two deliverables per reel
| Version | Contents | File | Use |
|---|---|---|---|
| **A: full mix** | VO + SFX + **original instrumental bed** (ours, licence-clean) | `<module>_mix.wav` -> master MP4 | Default upload; also safe for ads and cross-posting |
| **B: VO + SFX only** | VO + SFX, mastered on its own to -14 LUFS | `<module>_vo_sfx.wav` -> `<module>_vo_sfx.mp4` | Jawad adds a **trending Instagram sound in-app** (Instagram licenses it). Suggested in-app balance: original audio 100 %, added track about 10-25 % |
| Stems | `_stem_vo`, `_stem_sfx`, `_stem_music` at the exact mix gains (they sum to A) | wav 48 kHz / 24-bit | Re-balancing in CapCut / Premiere |

Rules:
- Never bake a copyrighted or trending song into an export.
- Trending audio goes in only through Instagram's in-app picker, and the music library depends on the account
  type:
  - Third-party guides (no official Meta page found for 2026) say **Business** accounts are limited to Meta's
    royalty-free Sound Collection and often cannot pick trending licensed songs. **Creator** accounts keep the
    full library.
  - Lead to confirm Jawad's account type
    ([instantdm](https://instantdm.com/blog/instagram-creator-vs-business-account-which-one-actually-drives-growth),
    [kompozy](https://kompozy.io/how-to/use-instagram-trending-sounds)).

### 5.2 Original-bed options compared
| Option | Licence / commercial use | CPU feasibility here | Verdict |
|---|---|---|---|
| **Procedural numpy (`epic_music.py`)** | We own it (all synthesis in-repo) | **6-10 s for a 30 s bed** (single thread, load-dependent) | **Use for every A version.** Exact BPM grid, drop and end hit on bar lines, stems, key-matched SFX |
| CC0 music (HF `SoundSafari/Public-Domain-Music`, FMA CC0) | CC0 / PD (verify per track) | trivial | Possible, but files.freemusicarchive.org is 403 here. Content ID risk: PD recordings are sometimes claimed by third parties. Fallback only |
| MusicGen-small (Meta, audiocraft) | **Weights CC-BY-NC 4.0 = non-commercial** | no torch installed; slow | **Excluded**: Jawad's page is commercial self-promotion |
| Stable Audio Open Small (341M) | Stability AI **Community Licence**: commercial use allowed under USD 1M annual revenue ([Stability](https://stability.ai/news/stability-ai-and-arm-release-stable-audio-open-small-enabling-real-world-deployment-for-on-device-audio-control)) | CPU-oriented, max about 11 s per clip | **Blocked**: HF repo is gated (401 without token + licence acceptance). Good for loops/SFX, not 30 s beds. Open question |
| **ACE-Step 1.5** (via `acestep.cpp`, GGML) | **MIT** (GitHub + HF card) ([HF](https://huggingface.co/ACE-Step/Ace-Step1.5), [acestep.cpp](https://github.com/ServeurpersoCom/acestep.cpp)) | Built from source CPU-only. Tested twice (5.3): 220 s (Q4, no LM) and 404 s (LM 0.6B + Q8) per 30 s on 2 threads | **Second choice.** With LM codes it is on grid and full-band, but ends early (22 s of 30) and peaks above 0 dBTP. Usable after bar-line looping + limiting. Its output counts as AI-generated audio |

### 5.3 Test evidence

**Procedural beds** (`python3 epic_music.py <style> 30`):
- Outputs go to `sfx/out/music/`. All four spectrograms are combined in `all_styles.png` (viewed).
- Each output is mastered to -16 LUFS with a -3 dBTP limiter, and has a level rider so it sits under VO.

| style | BPM | render | LUFS | dBTP | LRA | drop (bar) | end hit | beat grid (expected BPM / phase / strength) |
|---|---|---|---|---|---|---|---|---|
| `dark_pulse`: cinematic hybrid (strings ostinato, taiko, 808, braam on the drop, piano motif) | 120 | 8.1 s | -16.04 | -3.30 | 2.9 | 12.00 s (6) | 28.00 s | 120.00 / -10 ms / x8.7 |
| `desi_drill`: sliding 808, hat triplet rolls, half-time clap, sitar hook (D Phrygian-dominant) | 142 | 9.5 s | -16.05 | -3.30 | 3.3 | 10.14 s (6) | 27.04 s | 142.00 / -7.5 ms / x6.0 |
| `lofi_desi`: tabla kaharwa groove, EP chords Dm9-Bbmaj7-Gm9-A7b9, harmonium swells, crackle, tape-stop end | 84 | 7.2 s | -16.02 | -3.30 | 3.2 | 11.43 s (4) | 25.71 s | 84.00 / -9.3 ms / x3.8 |
| `desi_epic`: dhol chaal, harmonium drone, strings ostinato, dhol + braam on the drop, sitar hook | 100 | 8.7 s | -16.03 | -3.30 | 5.4 | 12.00 s (5) | 26.40 s | 100.00 / -10 ms / x7.6 |

- The first pass had raw instruments 15-30 dB hotter than the SFX library: the 808 measured +9.6 LUFS momentary.
  The intros sat about 20 LU under the drops, and the lofi bed failed the grid (84.6 BPM, phase -299 ms,
  strength 1.7).
- Fixed by calibrating every instrument to the library's reference (`CAL` table) and adding a slow level rider.
  The re-renders above are all on grid, within the music-supervisor's +-15 ms.

**ACE-Step 1.5, run 1** (dit-only, `acestep-v15-turbo-Q4_K_M`, 8 steps, 2 CPU threads, load average about 8 from
the other agents):
- Request: caption "dark cinematic trap ... no vocals", 90 BPM, D minor, 30 s, seed 7.
- Wall time **220 s for 30 s** of audio: text encoder about 1 s, DiT **69 s**, VAE decode **135 s**, model loads
  about 15 s. Peak RSS about 1 GB.
- Output: `aimusic/runs/ace_dark_trap0.wav` + `.png` (viewed).
  - -14.88 LUFS, **TP +0.01 dBTP** (it must be limited), LRA 16.4.
  - **Almost no top end**: energy above 8 kHz sits -73 dB below the total, and there are no visible hats.
  - The music stops at about 24 s.
  - Beat-grid strength x1.3 at 90 BPM (< 2 = not clearly on a grid).
- Verdict: fast enough on CPU, but this configuration (Q4 + no LM codes) is not production quality.

**ACE-Step 1.5, run 2** (with the 0.6B LM planner: `ace-lm` -> audio codes, then the turbo **Q8_0** DiT):
- Request: same caption, 90 BPM, D minor, 30 s, seed 7. LM 0.6B Q8 wrote 150 audio codes (5 Hz).
- Wall time **404 s for 30 s**: LM 58 s, DiT 168 s (Q8 weights plus heavier machine load than run 1), VAE 161 s.
- Output: `aimusic/runs/ace_full00.wav` + `ace_full0.png` (viewed).
  - **-12.70 LUFS, TP +0.18 dBTP** (it must be limited), LRA 2.7.
  - Full band: 808 sub, punchy drums with transients to 10 kHz+, energy above 8 kHz -30 dB rel (normal for trap).
  - **Beat grid 90.00 BPM, phase -6.7 ms, strength x11.7**: clearly on the requested grid.
  - **The music stops at 22.1 s** of the requested 30 s.
- Verdict: LM codes are what make ACE usable.
  - Workflow: request DUR + 10 s, then cut and loop on bar lines with `beatgrid` +-15 ms, `acrossfade` 20 ms,
    `atrim`.
  - Then run it through `epic_mix` like any bed.
  - About 7 min per try on 2 threads, so budget 2-3 seeds per reel. Treat it as AI-generated music: label per
    the lead's AI-disclosure decision.
  - It cannot place the drop on our reveal bar. That is why the procedural bed stays first choice.

Models and sizes:
- On disk under `sfx/aimusic/acestep.cpp/models/`: text encoder Qwen3-Embedding-0.6B-Q8 (784 MB), DiT turbo Q4_K_M
  (1.45 GB), DiT turbo Q8_0 (2.55 GB), LM 0.6B Q8 (710 MB), VAE BF16 (337 MB).
- Re-run: `cd sfx/aimusic/runs && nice -n 10 ../acestep.cpp/build/ace-synth --models ../acestep.cpp/models --request ace_dark_trap.json`.

### 5.4 Music-supervisor procedure per reel
1. Music map: set BPM = the edit's BPM. Put the drop on the bar of the reveal, the end hit on the end-card
   settle, and the tail by DUR.
2. Render: `python3 epic_music.py <style> <DUR> --bpm <BPM> --key D --drop-bar <n> --out <AUD>/<module>_music.wav`.
3. Verify with the JSON it writes:
   - tempo within 0.2 BPM;
   - phase within 15 ms (beat-grid strength > 2);
   - LUFS -16 +-0.2;
   - TP <= -3.
4. Final mix: `epic_mix.mix_reel(...)` (section 6).

---------------------------------------------------------------------------------------------------------------
## 6. Mix / master spec for VO reels (implemented in `epic_mix.py`)

| Stage | Spec |
|---|---|
| VO (Hindi TTS) | - Place at 0.3 s (after the frame-0 hit).<br>- HPF 80 Hz (12 dB/oct); -2 dB @ 300 Hz (Q 1.0); +2 dB @ 3.2 kHz (Q 0.9); +1.5 dB high shelf @ 10 kHz.<br>- 3:1 compressor, soft knee 6 dB, 8 ms / 120 ms, threshold 4 dB under the 90th-percentile level (about 4-6 dB GR on peaks).<br>- **-16.0 LUFS integrated (VO alone).** |
| SFX stem | - Sound-designer build: `A.mix(cues, DUR, target_lufs=-18, tp_ceiling=-2.0, split_stems=True)` with auto-duck, room send and glue.<br>- In the VO mix: sidechain under VO **-4 dB** (30 ms / 300 ms).<br>- Cue-level ducking inside spoken lines: -4..-8 dB; busy high-mid SFX get `lp` 3-4 kHz or `hp` cues. |
| SFX relative levels (cue `gain_db`) | - hero hits (1-2 per reel) **0 dB**<br>- transitions -3..-6<br>- UI clicks / typing -6..-10<br>- desi accents -4..-8<br>- textures and crowds -6..-10<br>- bed (BED_GAIN_DB) **-30** (felt) to -26 for rain/city<br>- at most about 3 sounds per instant |
| Music bed | - **-18 LUFS alone** (-16 if the reel has no VO).<br>- Ducked **3 dB under SFX** hits (10 ms / 250 ms) and **9 dB under VO** (40 ms / 400 ms).<br>- Never renormalise after ducking. |
| Bus / master | - Sum, then glue compressor 2:1 (threshold 3 dB under the 98th-percentile 10 ms level, 6 ms / 150 ms).<br>- Gain, then 4x-oversampled true-peak lookahead limiter at **-2.3 dBFS**, iterated to **-14.0 +-0.1 LUFS**.<br>- Result **<= -2.0 dBTP**. |
| Checks | - Speech >= **8 LU** above the ducked music (median over speech frames).<br>- Speech >= 10 LU above SFX.<br>- Limiter GR > 3 dB only on hero hits, under 0.1 s in total.<br>- LRA 2-8 LU. |
| Version B | VO + SFX with the same internal balance, mastered on its own to -14 LUFS / <= -2.0 dBTP. |
| Export (AAC) | Two-pass `loudnorm`, `linear=true`, I=-14, TP=-1.5 (headroom for AAC overshoot), AAC 320k, 48 kHz, `+faststart`. `epic_mix.mux(video, wav, out)` runs pass 1 (measure JSON), then pass 2 with the measured values, then re-measures with `ebur128`. |

Reference check:
- The three reference reels measure **-14.2 / -14.1 / -14.1 LUFS** integrated (LRA 6.7 / 4.7 / 2.4).
- Their true peaks are +0.4 / -0.6 / -0.8 dBTP: they clip after AAC. We stay at -2.0 in the wav and about -2.0
  in the AAC.
- So the -14 LUFS target matches what the platform already serves.

### End-to-end test (`mixtest.py`; outputs in `sfx/out/mix/`, `mixtest_mix.png` viewed)
Inputs (30 s):
- VO: Kokoro `hm_omega` Devanagari audition (20.7 s) from `tts/auditions/`.
- SFX: 18 cues (trailer_hit + sub_drop hook; glitch; keyboard; mouse; scrub; notif; fan; shepard + reverse
  cymbal into braam + boom at 12.0 s; tabla; render_complete; heartbeat_build; dhol + logo_sting), bed
  `edit_suite` at -30.
- Music: `dark_pulse` 120 BPM.

| measure | A full mix | B VO+SFX |
|---|---|---|
| integrated | **-14.05 LUFS** (ffmpeg: -14.1) | **-14.04 LUFS** (ffmpeg: -14.0) |
| true peak | **-2.30 dBTP** (ffmpeg: -2.3) | -2.30 dBTP |
| LRA | 2.2 LU | 6.4 LU |
| limiter max GR | 3.7 dB, > 2 dB for only about **70 ms** in total (frame-0 hook hit, 27 s end slam) | 4.2 dB |
| VO over music (speech frames) | **10.9 LU** (>= 8 required) | n/a |
| VO over SFX (speech frames) | 13.9 LU | |
| AAC after two-pass loudnorm (`mixtest_mix.m4a`) | **I -13.9 LUFS, TP -2.0 dBTP**, LRA 2.2 | |
| run time | 21.6 s (SFX mix + VO chain + ducking + 2 masters + stems + report) | |

Call:
```python
import sys; sys.path.insert(0, '/home/user/100/workspace/brand_reels/sfx')
import epic_mix as M
rep = M.mix_reel('reel1', DUR, vo=AUD + '/reel1_vo.wav', music=AUD + '/reel1_music.wav',
                 sfx_cues=reel1_sfx.cues(), bed=reel1_sfx.BED, bed_gain_db=reel1_sfx.BED_GAIN_DB,
                 out_dir=AUD, vo_offset=0.3)
M.mux(OUT + '/reel1/reel1.mp4', rep['files']['mix'], OUT + '/reel1/reel1_final.mp4')        # version A
M.mux(OUT + '/reel1/reel1.mp4', rep['files']['vo_sfx'], OUT + '/reel1/reel1_vo_sfx.mp4')    # version B
```

---------------------------------------------------------------------------------------------------------------
## 7. Open issues / questions for the lead
1. **Account type** (Creator vs Business) decides whether trending songs are available in-app for version B.
2. **Stable Audio Open Small** needs an HF token plus acceptance of the Stability Community Licence. Do not
   proceed without the user's OK.
3. **Wikimedia rate-limit**: 6 CC0/PD files are queued (stereo CC0 rain 42 MB, crash cymbals for
   `reverse_cymbal_real`, Tick2). Retry with `python3 sfx/tools/commons_get.py "rain::File:Light Rain Distant Thunder July 5th 2016.wav" ...` later; the entries register
   automatically when present.
4. No human has listened to these sounds yet. Before the masters, someone with ears should audition
   `out/epic_catalog.wav` and the four beds. Priority: `crowd_ooh` (prefer the real samples), `sitar_pluck`,
   `braam`.
5. **Repo location**: the code lives in the git-ignored workspace (`workspace/brand_reels/sfx/{epic_sfx,epic_music,
   epic_mix}.py`). Copy it to `pipeline/jawad_reels/` to commit it. The library and `samples48/` stay in the
   workspace (27 MB of CC0/PD, rebuildable from `LICENSES.md`).
6. AI disclosure: the VO is AI (TTS), so Meta's AI label question stays with the lead. The music beds are
   procedural, not generative AI. An ACE-Step bed would be AI-generated audio.
7. **Disk**:
   - `sfx/aimusic/` holds 5.6 GB: the acestep.cpp clone, its CPU build and the GGUF weights. Delete it if
     ACE-Step is not adopted.
   - The clone is third-party code, built and run only for this test, under `nice` with 2 threads.
