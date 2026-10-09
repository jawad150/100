# HANDOFF: Reel 2 · C11 · Bijli Chali Gayi → motion-timeline-builder

Date 2026-10-09 · Author: creative-director · For: the motion-timeline-builder, who builds `pipeline/jawad_reels/bijli_chali_gayi.py`
next (one module; hook B through `JAWAD_C11_HOOK=B`, the cover through `JAWAD_C11_COVER=1`).

**Read order:** this file, then `BRIEF.md` r2 (§6.1-§6.9 and §7 are still the geometry, light, string and contract spec), then
`FACES.md` §2 and §8 (API and wiring), then `SOUND.md` §8.3 (event frames the sound hits). **Where this file and BRIEF r2 /
`packet.yaml` differ, this file wins** (r3 deltas, §2). LEAD_DECISIONS.md is binding over all of them.

Inputs used: `BRIEF.md` r2, `VO_TIMING.md` (measured), `words.json` / `words_B.json`, `FACES.md`, `SOUND.md`,
`MUSIC_bijli_chali_gayi.md`, `SHARED_REQUESTS.md`, `LEAD_DECISIONS.md`. Measured today from the files: word times
(words.json), a dry run of `SC.Captions` on the real words with the real avoid rects + `BF.jd_rect` (A and B: `check() == []`),
`E.EndCard` (settle 1.85 s, hold 1.79 s), `S3.Asset3D` load + every meta.json label list, a `BF.draw` smoke test at 25.5 s and
29.6 s, imports of every picture-side module.

Conventions: `f = floor(30 t)`; `<RW>` = `/home/user/100/workspace/jawad_reels/bijli_chali_gayi`;
`<P>` = `/home/user/100/pipeline/jawad_reels`; `<D>` = `/home/user/100/brand_reels/design/reels/bijli_chali_gayi`.
90 BPM: beat 20 f, bar 80 f = 2.667 s; DUR 34.667 s = 1,040 frames.

---------------------------------------------------------------------------------------------------------------

## 1. Readiness at a glance

| item | status | note |
|---|---|---|
| VO stems A/B + word timings | **READY** | measured; 62 / 61 words, 100 % of word starts on voice, -16.00 LUFS, -2.00 dBTP, mono, 1,664,000 samples |
| 3D props (8 assets, `S3.Asset3D`) | **READY** | all passes + meta.json on disk (§4); the contact-sheet folder `out/sheets3d/` was lost in the workspace restore (not needed to build) |
| faces module (`bijli_chali_gayi_faces.py`) | **READY** | imports, `prewarm()` + `draw()` at 25.5 / 29.6 s draw JD at eye (440, 1211) / (540, 1150) |
| captions plan | **READY** | dry run on the real words: 21 chunks, `check() == []` for A and B (§6) |
| end card params | **READY** | measured (§8) |
| SFX module (`bijli_chali_gayi_sfx.py`) + stems | **BLOCKED (kit)** | does not import: `epic_sfx` is being rebuilt; stems/cue JSON not on disk. Rebuild after `KIT_READY` (§5) |
| music module (`bijli_chali_gayi_music.py`, harmonium) | **BLOCKED (kit)** | same `epic_sfx` import; `music_full.wav` not on disk |
| final mixes A FULL / A DRY / B FULL | **BLOCKED** | mix stage, after the kit; old LUFS numbers are void |
| reel module `bijli_chali_gayi.py` | **TO BUILD (you)** | nothing exists yet; build picture with `--no-audio` (or mux the VO stem) until the mix exists |
| master render, splice, QA, delivery | blocked on the module and the mix | |

---------------------------------------------------------------------------------------------------------------

## 2. What changed since BRIEF r2 (r3, binding; everything else in BRIEF r2 stands)

LEAD_DECISIONS 3: the measured Vlad takes are final; picture moves to the VO. Each row says exactly what moves.

| # | what | BRIEF r2 | r3 (binding) | why |
|---|---|---|---|---|
| 1 | V9 `Har tees second.` | spoken 22.51-23.32 | **not in the VO** (ladder F4). The last chip at f712 is **U3F `Saved · har 30 sec`** (chip 400 × 76 at (780, 640), f712-f719); the plain `Saved` chip is not spawned at f712 | dense block overran (VO_TIMING ladder). The V9 caption keyword *tees* no longer exists |
| 2 | V2 `Yaad hai?` (hook A) | 2.200-2.600, fallback 1.550-≤ 2.000 | **1.545 → 2.255** (words: Yaad 1.545, hai? 1.898-2.080; voice to 2.255). LED pulses stay on f40/f44 and **f60/f64** (cover frame f60 needs the pulse); the f60/f64 beeps are ducked -8 dB under "hai?" by the SFX fit | every V2 take runs 0.70-0.77 s; LEAD_DECISIONS 3 makes the take final. The QA line "V2 ends ≤ 2.000" is replaced (§13). **Picture: no change** |
| 3 | V8 "Ctrl+S" | onset inside f620-f640 | **21.467 (f644)**; "khud" 21.130-21.467. **Presses stay on the grid**: quarters f580/f600/f620, 8ths f640…f710 (`PRESSES` of the SFX module). The f640 press lands inside "*khud*" (the caption keyword): the finger presses "by itself" a beat before the word is said | moving the 8th run to f644 would push 8 presses 133 ms off the 90-BPM grid that the keycaps carry (no music bed) and fail the bars 7-8 grid check (±15 ms) |
| 4 | V7 end | 18.830 | **19.260** ("dushman" 18.616-19.260) runs over the L8 iris (f551-f570, closed f560 = 18.667). **L8 stays at f560**; its cues stay quiet under the word (SFX fit) | the iris closes on "*dushman*" (the enemy shuts the frame); moving L8 later would collide with the f580 first press |
| 5 | S4 torch path | "finds the copy, then the CRT and the box" | beam on the homework copy (x 70-240, y 1310-1380) **by f340** ("*bachche*" 11.333), sweeps (inout_sine) to the CRT glass **f351-f366** ("bare hue" 11.70-12.49), holds; box + beep f380 | locks the beam to the measured V5 words |
| 6 | Hook B HB3 `YAAD HAI?` | caps rise t0 0.35 | **t0 = 1.25** (rises in the pause after "awaaz" ends 1.244; full opacity by 1.67 = "yaad" 1.667); exit unchanged 2.267-2.617 | picture to the VO: the text arrives with the word, not 1.3 s before it. V1B voice ends 2.347 (< splice 2.667) |
| 7 | payoff lockup exit | `out_t0=29.0` | **`out_t0=28.95`** (0.35 s exit ends 29.30 = f879, gone before the L4 cut f880) | FACES §8: at 29.0 it is still ~14 % on f880 |
| 8 | captions | §6.14 | adds `clear=[(8.0, 8.6), (26.333, 26.667)]` and `BF.jd_rect(t)` in the S7b avoid list (§6) | dry run: "aati thi..." held to 8.50 over the AA GAYI! slam; "nahi sikhai..." exited 26.76 into the payoff ink box |
| 9 | V8 keyword | *khud* | unchanged; V9 *tees* gone (#1) | |
| 10 | QA checklist | BRIEF §8 | §13 below | VO lines re-measured; LRA per LEAD_DECISIONS 1 |

Nothing else moves: every other picture frame in BRIEF §6.1-§6.9 already sits on its measured word (table §3.2).
The SFX module reads its event frames from BRIEF frames (`F(f)`, `PRESSES`, `DROP`, `T_END`); r3 moves no frame it uses,
so its `raw_cues()` need no re-timing (the U3F chip spawns at f712 = the old chip frame; its ui_tick is unchanged).

---------------------------------------------------------------------------------------------------------------

## 3. The final beat table

### 3.1 Bar by bar, with the measured VO

VO words = `<RW>/vo/bijli_chali_gayi_vo_A.words.json` (= `words.json`), reel seconds, `*` = caption keyword. Voice spans
from VO_TIMING (envelope, -55 dBFS). Captions = the §6 dry run (chunk enters → fully gone).

| bar · f (s) | shot · camera | picture (frame-exact; BRIEF §6.2-§6.9) | on-screen text | VO (measured) | captions | r3 |
|---|---|---|---|---|---|---|
| 0 · f0-79 (0.000-2.633) | S1A · CAM_ROOM locked → drift from f20 | lit room f0-f9 (fan, CRT bold edit, tube); brownout f10-f13; mains 0 f14 (8 px CRT line); dot f15; torch f20; beam to box f24-f38; LED f40/44, f60/64; cover f60; splice f80 | H1 `Bijli` f15, H2 `CHALI GAYI.` f18; exit f72-f79 | **Bijli 0.085** · chali 0.583 · gayi. 0.892 (voice ends 1.305) · Yaad 1.545 · hai? 1.898 (voice ends 2.255) | hidden | #2 |
| 1 · f80-159 (2.667-5.300) | S2 · drift, tilt up f140-f159 (+900 px in_cubic) | match flare f80 (push 0.5), candle, pankhi swings on f100/f120/f140, homework copy | none | Light 2.920 · jaati 3.326 · thi, 3.659 · toh 4.260 · poora 4.520 · mohalla 4.870 | `*Light jaati thi` 2.87→4.21 · `toh poora` 4.21→4.82 · `mohalla *chhat pe` 4.82→5.82 (upper band, y 550-790) | none |
| 2 · f160-239 (5.333-7.967) | S3 rooftops · settle f160-f180, drift | haze band, pools, rims; **far window lit f220-f221 only**, child's head turns f224-f230, holds to f300 | none | **chhat 5.351 (f160.5)** · pe 5.685 · hota 5.870 · tha. 6.129 · Jab 6.550 · *wapas 6.784 · aati 7.173 · thi... 7.451 (voice ends 7.850) | `hota tha` 5.82→6.50 · `Jab *wapas` 6.50→7.12 · `aati thi...` 7.12→**8.00** (lower-left, x 82-449, clear of the window and the child) | captions #8 |
| 3 · f240-319 (8.000-10.633) | S3 · LOCKED f240-f299, drift from f300 | bulbs cascade f240-f245, `AA GAYI!` slam, cheer; dies near → far f300-f302 | R1 `AA GAYI!` f240, darken-flicker exit f300-f305 | none (8.0-10.88) | none | none |
| 4 · f320-399 (10.667-13.300) | S4 · L7 f308-f331 (beam crosses x 540 on f320); drift, push 1.00 → 1.04 | torch: copy by f340, CRT f351-f366, box + beep f380 | none | Phir 10.912 · woh 11.130 · *bachche 11.333 (f340) · bare 11.704 · hue. 12.130 (ends 12.492) | `Phir woh *bachche` 10.86→11.65 · `bare hue` 11.65→12.96 (y 600-790, above the CRT) | torch #5 |
| 5 · f400-479 (13.333-15.967) | S5 · LOCKED | on-word cut f400 (push 0.8), lights on; monitor = the CRT's edit (playhead x ≈ 440) + 9:16 rooftop viewer; `RENDERING 63%`, 64 % at f440; brownout f470 | U1, U2 | Kuch 13.130 · ***editor* 13.367 (f401)** · ban 13.904 · gaye. 14.108 (ends 14.543) | `Kuch *editor` 13.08→13.85 (top band y 255-411, above the monitor) · `ban gaye` 13.85→15.19 (lower) | none |
| 6 · f480-559 (16.000-18.633) | S5 · drift from f480 | power dies f480: monitor collapse f480-f485, HUD drain f486-f520 (RED < 20 %), `0%` RED pulsing; L8 f551-f570 | U1, U2 until iris f551-f558 | silence 16.000-16.400 · **Aur 16.400** · bijli 16.635 · ban 17.107 · gayi 17.271 · sab 17.562 · se 17.998 · bari 18.235 · *dushman. 18.616 (ends 19.260) | `Aur bijli` 16.35→17.06 · `ban gayi` →17.51 · `sab se` →18.18 · `bari *dushman` 18.18→19.34 | V7 end #4 |
| 7 · f560-639 (18.667-21.300) | S6 keycaps · locked, macro | L8 closed f560 only, opens on the keycaps; presses f580, f600, f620 (Ctrl leads S by 1 f), chips at p+2 | U3 `Saved` chips; K1/K2 legends | Har 19.390 · desi 19.631 · editor 20.031 · ki 20.395 · ungli 20.576 · *khud 21.130 | `Har desi` 19.34→19.98 · `editor ki ungli` 19.98→21.08 · `*khud Ctrl+S` 21.08→22.27 (lower, y 1240-1435, below the Ctrl cap) | presses #3 |
| 8 · f640-719 (21.333-23.967) | S6 | 8ths f640…f710 (f640 inside "khud"); chips f642…f702; **U3F f712-f719** | chips, U3F | Ctrl+S 21.467 (f644) · dabati 22.322 · hai. 22.795 (ends 23.060) | `dabati hai` 22.27→23.71 | V9 #1 |
| 9 · f720-799 (24.000-26.633) | S7a f720-f739 (candle macro, push 0.3) → S7b f740 (push 0.2), `BF.cam_s7b(t)` | flame leans and recovers; JD profile by candlelight from f740; **drop-out f790-f799** | none | **Bijli 24.000 (f720)** · ne 24.442 · humein 24.624 · *editing 24.969 · nahi 25.369 · sikhai... 25.569 (ends 26.110) | `Bijli ne` 23.95→24.57 (crosses f720, lower) · `humein *editing` 24.57→25.32 (top, y 353-540, above JD) · `nahi sikhai...` 25.32→**26.33** | captions #8 |
| 10 · f800-879 (26.667-29.300) | S7b → S7c (hard cut f840) | payoff lockup rises f800; harmonium peak f820; candle macro f840-f879 under the lockup; riser into f880 | P1/P2 `BIJLI NE SIKHAYA` / `sabr` t0 26.667, **out_t0 28.95** | ***sabr* 27.333 (f820)** · sikhaya. 27.764 (voice ends 28.473) | hidden | exit #7 |
| 11 · f880-959 (29.333-31.967) | S8a · L4 f870-f889, cut f880; locked → S8b f920 (push 0.3) | power returns (loudest): tube strike f882, CRT on f883, fan spin-up, JD smiling f880-f919; lit room f920 = frame-0 world | end card from f920 | silence 28.47-31.43 · Aap 31.430 · ke 31.626 · *ghar 31.853 | hidden | none |
| 12 · f960-1039 (32.000-34.633) | S8b · locked | end card held; settled f975.5, exit f1029-f1039 + loop push; `E.loop_world` | end card | light 32.350 · jaane 32.758 · pe 33.079 · kya 33.330 · hota 33.551 · tha? 33.834 (words end 34.023; voice ends 34.120) | hidden | none |

Hook B (frames 0-79 only; splice f80): BRIEF §6.4, plus r3 #6. V1B measured: Yeh 0.300 · *awaaz... 0.571-1.244 · yaad 1.667 ·
hai? 2.035 (voice ends 2.347). Words from 2.920 on are identical to A (checked: same times, same tokens), so the body
captions and body picture are identical.

### 3.2 VO vs picture: bold anchors (all measured)

| anchor | target | measured | Δ | picture |
|---|---|---|---|---|
| V1 onset | 0.100 | 0.085 | -0.015 | none |
| V1 end (before beep f40 1.333) | ≤ 1.300 | 1.305 | +0.005 | none (still before the beep) |
| "chhat" onset | ≥ f160 | 5.351 (f160.5) | ok | none |
| V4 end (≥ 0.15 s before slam f240) | ≤ 7.850 | 7.850 | 0 | none |
| far window f220 under "...aati thi..." | 7.333 | aati 7.173-7.451 | ok | none |
| "bachche" | f340 | 11.333 | 0 | torch #5 |
| "editor" | f401 | 13.367 | 0 | cut f400 stays |
| V7 onset after 0.4 s silence | 16.400 | 16.400 | 0 | none |
| "Ctrl+S" | f620-f640 | 21.467 (f644) | +0.134 | presses stay (#3) |
| "Bijli" on the candle cut | f720 | 24.000 | 0 | none |
| V10 end before the drop-out | ≤ 26.300 | 26.110 | ok | none |
| "sabr" | f820 | 27.333 | 0 | none |
| V12 end (≥ 0.5 s before the seam) | ≤ 34.100 | voice 34.120 / words 34.023 | ok (0.55 s to DUR) | none |

---------------------------------------------------------------------------------------------------------------

## 4. Every asset, with its path (each checked with `ls` / import on 2026-10-09)

| asset | path | notes |
|---|---|---|
| VO stem A | `<RW>/vo/vo_stem.wav` (byte-identical copy `<RW>/vo/bijli_chali_gayi_vo_A.wav`) | mono 48 kHz, 1,664,000 samples, -16.00 LUFS, -2.00 dBTP |
| VO stem B | `<RW>/vo/vo_stem_B.wav` (= `bijli_chali_gayi_vo_B.wav`) | same format |
| words A / B | `<RW>/vo/bijli_chali_gayi_vo_A.words.json` (= `words.json`), `_vo_B.words.json` (= `words_B.json`) | list of dicts `word, start, end, keyword, line, hide`; reel time, offset 0 |
| VO decisions / ledger | `<RW>/vo/select.json`, `decisions.json`, `credits.json`, `requests.json` | F4 in force |
| desk_plate | `<RW>/assets3d/desk_plate/passes/` labels `lit`, `practicals` | features `tube_xy (235, 268)`, `crt_slot`, `box_slot`; opaque 1080x1920 |
| crt_room | `<RW>/assets3d/crt_room/passes/` labels `room`, `key_l`, `key_r`, `screen_mask`, `emit` | `screen_tl/tr/...` (crop space), `power_led`, `frame_xy` |
| tower_room | `<RW>/assets3d/tower_room/passes/` `room`, `key_l`, `key_r`, `emit` | `frame_xy (732, 1485)`, `hdd_led` |
| box_room | `<RW>/assets3d/box_room/passes/` `room`, `key_l`, `key_r`, `emit` | `frame_xy (725, 1202)`, `led_xy` |
| pankhi | `<RW>/assets3d/pankhi/passes/` `key_l`, `key_r` | `pivot`, `blade_centre` |
| candle | `<RW>/assets3d/candle/passes/` `self`, `key_l`, `key_r` | `wick_tip`, `base`, `candle_base` |
| keycap_ctrl / keycap_s | `<RW>/assets3d/keycap_ctrl/passes/`, `<RW>/assets3d/keycap_s/passes/` `key_l`, `key_r`, `emit` | `legend_centre`, `contact` |
| loader | `S3.Asset3D(name, 'passes', root=RWS + '/assets3d').by_label('key_l')` | `<RW>/props` is a symlink to `assets3d` |
| 3D builder (do not re-run) | `<P>/assets3d_bijli_chali_gayi.py` | |
| faces module | `<P>/bijli_chali_gayi_faces.py` (`BF`; API in FACES §2) | needs an **RGBA** float canvas (1920, 1080, 4) like `K` canvases; a 3-channel array raises in `core._blend` |
| faces preview harness | `<P>/bijli_chali_gayi_faces_preview.py` | stand-in worlds; not production art |
| face sources | `/home/user/100/workspace/brand_reels/charsheet/cutouts/suit_profile.*`, `suit_smiling.*`, `crops/suit_*_2x.png` | read only |
| SFX module | `<P>/bijli_chali_gayi_sfx.py` | **does not import until the kit is back** (`epic_sfx`); outputs `<RW>/audio/bijli_chali_gayi_sfx_{A,B}.wav` + `_cues.json` (not on disk now) |
| music module | `<P>/bijli_chali_gayi_music.py` | same blocker; output `<RW>/music/music_full.wav` (harmonium only; not on disk now) |
| VO module | `<P>/bijli_chali_gayi_vo.py` | do not re-run `assemble` (the stems are final) |
| fonts | `/home/user/100/workspace/jawad_reels/fonts/` | via `type3d` aliases (`jw_key`, `jw_caps`, `jw_caps_bold`, `jw_mono`, `jw_body`, `jw_handle`) |
| tools | `<P>/tools/heavy.sh`, `<P>/tools/commit_step.sh`, `<P>/render.py`, `<P>/package.py` | `qa_measure.py` (named in SOUND §1) is **not** on disk: QA measures with its own scripts |

Output folders: `<RW>/out` does not exist yet. Before the first render: `mkdir -p <RW>/out && ln -sfn <RW>/out /home/user/100/workspace/jawad_reels/out/bijli_chali_gayi`.
Disk: 24 GB free on `/` (keep `<RW>` under ~4 GB; delete scratch frames).

---------------------------------------------------------------------------------------------------------------

## 5. Audio note (read before any render with sound)

- **The bed and the SFX stem are regenerated on the rebuilt sound kit by the mix stage.** `epic_sfx` / `epic_music` /
  `epic_mix` were lost and are being rebuilt in `<P>`; ready only when `/home/user/100/workspace/brand_reels/wf/KIT_READY`
  exists (absent at hand-off). Then read it and `wf/kit_reel_issues.json` for C11 items.
- **Every LUFS / gain number in SOUND.md, MUSIC_bijli_chali_gayi.md and BRIEF §6.10-6.11 was measured on the OLD kit and is
  void.** The mix stage re-measures; nobody quotes them as acceptance evidence.
- The audio layer has **no music bed** (SLATE §3.2): diegetic beds from the SFX module + the one harmonium swell
  (`bijli_chali_gayi_music.py`, peak f820). One harmonium source only (MUSIC hand-off notes).
- The reel module sets `BED = None` and keeps `cues()` empty; render with `--no-sfx-build` and either `--no-audio` (picture
  previews) or `--audio <RW>/audio/bijli_chali_gayi_mix_A_full.wav` (master, once it exists). For a picture preview with
  sound, mux `<RW>/vo/vo_stem.wav` with ffmpeg.
- Rebuild order after KIT_READY (from `<P>`, all through heavy.sh): `bijli_chali_gayi_sfx.py audition` → `build --hook AB` →
  `bijli_chali_gayi_music.py` (harmonium) → mix stage (A FULL, A DRY, B FULL) → `bijli_chali_gayi_sfx.py verify`.
  Mono VO: re-normalise to -16 LUFS after duplicating to stereo (SHARED_REQUESTS #5).

---------------------------------------------------------------------------------------------------------------

## 6. Captions plan (snake_captions; dry run on the real words: A and B `cap.check() == []`, 21 chunks each)

```python
def avoid_at(t):                       # rects (x0, y0, x1, y1) px
    r = []
    if 80/30 <= t < 160/30:  r += [(60, 1150, 1020, 1660), (440, 780, 640, 1020)]          # S2 table + flame
    elif 160/30 <= t < 8.0:  r += [(290, 995, 370, 1085), (650, 1280, 870, 1430)]          # S3 far window, child + pankhi
    elif 320/30 <= t < 400/30: r += [(250, 1010, 690, 1380)]                               # S4 CRT
    elif 400/30 <= t < 560/30: r += [(100, 440, 980, 960), (110, 990, 920, 1110)]          # S5 monitor, HUD
    elif 560/30 <= t < 720/30: r += [(165, 900, 495, 1200), (585, 720, 855, 990), (600, 380, 960, 720)]  # keycaps, chips
    elif 720/30 <= t < 740/30: r += [(380, 600, 700, 1300)]                                # S7a flame
    elif 740/30 <= t < 840/30:
        r += [(700, 1040, 900, 1560)]                                                      # S7b candle
        h = BF.jd_rect(t)
        if h: r.append(tuple(h))                                                           # JD (incl. back hair, x from 0)
    return r

WORDS = RWS + '/vo/bijli_chali_gayi_vo_%s.words.json' % HOOK
cap = SC.Captions(WORDS, band='auto', avoid=avoid_at, white_px=64, key_px=128,
                  hide=[(0.0, 80/30), (800/30, 880/30), (920/30, DUR)],
                  clear=[(8.0, 8.6), (26.333, 26.667)])
assert cap.check() == []
cap.save_srt(RWS + '/captions/bijli_chali_gayi_%s.srt' % HOOK)
```

- Hidden: hook (designed text), payoff V11 (the lockup shows *sabr*), end card V12. `clear` keeps the slam f240 and the
  drop-out / payoff start caption-free (measured: "aati thi..." now gone 8.000, "nahi sikhai..." gone 26.333).
- Keywords (from words.json): *Light*, *chhat*, *wapas*, *bachche*, *editor*, *dushman*, *khud*, *editing* (V9 *tees* gone);
  *Ctrl+S* stays white. Caption text = the ROM tokens (house spelling bari / nahi / sikhai; never "sikhaayi").
- If the avoid rects change after you build (real prop positions), re-run the dry run and `check()`.

---------------------------------------------------------------------------------------------------------------

## 7. Transitions (jawad_tx; 3 features: L7 ★, L8, L4 ★; BRIEF §6.8 unchanged)

```python
PLAN = X.Plan([
    ('L7', 320/30, dict(src=(540, -900), a0=-40, a1=40, width=2.2, haze=0.45, rays=0.0)),   # f308-f331, crosses x 540 on f320
    ('L8', 560/30, dict(n=7, black=0)),                                                      # f551-f570, fully closed f560 only
    ('L4', 880/30),                                                                          # f870-f889, no options
])
cv = PLAN.draw(t, [WORLD_A, WORLD_B, WORLD_C, WORLD_D])   # A: hook+S2+S3 (t ≤ 11.07) · B: S4+S5 · C: S6+S7a-c · D: S8a+S8b
CUTS = [(0.0, 0.6), (80/30, 0.5), (160/30, 0.25), (240/30, 0.5), (400/30, 0.8), (720/30, 0.3), (740/30, 0.2), (920/30, 0.3)]
```
- Glue cuts f80, f160, f400, f720, f740, f840 (no push), f920: hard cuts inside the world functions with `X.side_b(t, c)`;
  pushes only through `cuts=` in `G.tx_finish`. Never pass `push_gain` to a Plan step (SHARED_REQUESTS #1).
- Motion blur never crosses a cut: switch the shot half a frame early (`side_b`).
- `post(cv, t)`: `kw = PLAN.post_kw(t); kw['push'] = kw.get('push', 0.0) + card.post_kw(t, T_END, DUR).get('push', 0.0);
  return G.tx_finish(cv, t, 'dusk', cuts=CUTS, **kw)`.

---------------------------------------------------------------------------------------------------------------

## 8. End card (measured today with `endcard.EndCard`)

```python
card = E.EndCard('COMMENT MEIN', 'batao', sub='Chhat ya candle?', monogram='JD', dur=4.0,
                 y_mono=360.0, y_key=730.0, y_sub=965.0, y_sig=1575.0)
T_END = 920 / 30          # literal frame (DUR - card.dur = 30.66666666666666 by float rounding; SHARED_REQUESTS #2)
card.draw(cv, t, T_END)   # last call in draw(t)
```
Measured: `settle` 1.85 s (settled f975.5), `hold` 1.79 s (≥ 1.5), exit over the last 0.36 s with the loop push. Raised
layout keeps the keyword (y 658-882) and sub (y 945-985) above the CRT glass (y 1050-1290). V12 runs 31.430-34.120 under the hold.

---------------------------------------------------------------------------------------------------------------

## 9. Loop bridge

- S8b (f920-f1039) is the frame-0 world: every time-varying element (fan angle, CRT playhead, tube flicker) reads the lit-room
  clock at `t - DUR`, so f1039 is frame -1 of the lit room. `E.loop_world(world, t, DUR, d=0.6)` cross-fades identical content.
- Frame 0 carries `cuts=[(0.0, 0.6)]`; the card's exit push is the other half.
- Audio (mix stage): room_mains bed runs to DUR and restarts at f0 at the same gain, no fade; the end card's reverse_swell ends
  on DUR, the f0 impact_soft is its release. V12's question ("...kya hota tha?") is answered by V1 "Bijli chali gayi."
- Version A replays the power death at f10. Version B's seam (lit card → torch-lit f0) is a deliberate hard cut.
- Check: `E.seam_report(...)['ok'] is True`.

---------------------------------------------------------------------------------------------------------------

## 10. Commands (from `<P>`; every render.py call carries `--no-sfx-build` and `--no-audio` until the mix exists)

```bash
mkdir -p $RW/out && ln -sfn $RW/out /home/user/100/workspace/jawad_reels/out/bijli_chali_gayi
# gate stills (BRIEF §7 gates 2-3), then a 360x640 INTER_AREA copy of each, Read both
tools/heavy.sh python3 render.py bijli_chali_gayi --stills 0.0,0.3,0.4667,0.5,0.6667,2.0,6.5,7.3334,8.1,11.4,14.0,16.1,21.4,23.8,25.5,27.6,29.4,33.0 --workers 1 --no-sfx-build --no-audio
tools/heavy.sh python3 render.py bijli_chali_gayi --sheet 16 --samples 1 --workers 1 --no-sfx-build --no-audio
# hook B (frames 0-79) into its own folder, splice onto A f80-f1039 (frame-exact, one re-encode)
JAWAD_C11_HOOK=B tools/heavy.sh python3 render.py bijli_chali_gayi --range 0 2.6667 --workers 1 --no-sfx-build --no-audio
# cover still
JAWAD_C11_COVER=1 tools/heavy.sh python3 render.py bijli_chali_gayi --stills 2.0 --workers 1 --jpg --no-sfx-build --no-audio
# master, only after the mix stage has written the mix
FOSTER_NICE=10 tools/heavy.sh python3 render.py bijli_chali_gayi --workers 1 --no-sfx-build --audio $RW/audio/bijli_chali_gayi_mix_A_full.wav
```
(`$RW` = `<RW>`. Hook B's render writes the same output names as A: move them to `<RW>/out/hookB/` at once.)

---------------------------------------------------------------------------------------------------------------

## 11. Open risks (owner · what to do)

1. **Sound kit not ready** (`KIT_READY` absent; `epic_sfx` missing): SFX + music modules do not import, no stems/mix on disk.
   Owner: kit workflow → mix stage. Picture work is not blocked; master + delivery are.
2. **V2 "hai?" under the f60/f64 beeps** (hook A, 1.898-2.255 vs 2.000-2.203): accepted per LEAD_DECISIONS 3 with the beeps
   ducked -8 dB. Mix stage verifies V2's words stay ≥ 7-8 LU over the SFX (one-syllable tolerance).
3. **V1 "Bijli"** heard विजली by whisper medium on 4/5 takes (small hears बिजली): QA's V1 intelligibility test uses whisper
   small or accepts either spelling. A re-take would cost ≤ 0.23 credits but V1 must still end before 1.333; only if QA fails.
4. **V3b `मुहल्ला` spelling / nukta sounds (आवाज़, ख़ुद)**: ASR cannot judge; nobody can listen. Listed, not blocking.
5. **3D `key_l`/`key_r` warm back rim** on box/tower faces (BRIEF §10 item 8): apply the torch passes only under the beam mask;
   if the box still reads flat orange at 360 px, list it (LEAD_DECISIONS 7) rather than re-render Blender.
6. **LRA**: rough mixes read 2.9-3.0 LU on the old kit; LEAD_DECISIONS 1 now accepts 2.0-9 LU. Re-measure on the new kit.
7. **Lost proof folders** (`out/brief_proofs*`, `out/sheets3d/`, `out/faces_preview/`): the numbers quoted in BRIEF/FACES are
   from them; the gate stills of §10 replace them as evidence.
8. **S7b handheld is ~1 px** (FACES §8: the 4 px / 0.3° cap through `K.wiggle`): accepted as written; do not raise it.
9. **Truth (GATE minor 8)**: JD's profile under "Bijli ne humein…" may read as his own memory; VO is the collective
   "humein", no claim about him. Lead confirms with Jawad before posting.

---------------------------------------------------------------------------------------------------------------

## 12. Shared requests (`SHARED_REQUESTS.md`; every one worked around locally, none blocks)

| # | module | issue | C11 workaround |
|---|---|---|---|
| 1 | jawad_tx | `Plan` crashes on post-only options (`push_gain`) for L3/L4/D7 | Plan holds only L7/L8/L4 with valid options; glue cuts via `side_b` + `cuts=` |
| 2 | endcard | `dur=DUR - T_END` rejected by float rounding | literal `dur=4.0`, `T_END = 920/30` |
| 3 | vo_chain | `voiced_runs` under-measures tight clips | VO module's own `runs_abs` (done; stems final) |
| 4 | epic_sfx | `crowd_cheer_real` contains English words | `bijli_chali_gayi_sfx.mohalla_cheer` granular re-synthesis (re-check on the new kit) |
| 5 | epic_mix | mono VO +3.01 LU when duplicated to stereo | re-normalise the stereo VO to -16 LUFS before the mix |

New in this hand-off: none.

---------------------------------------------------------------------------------------------------------------

## 13. QA acceptance checklist (r3; supersedes BRIEF §8 where they differ; every other BRIEF §8 box still applies)

**Format**
- [ ] ffprobe 1080x1920, 30/1, nb_frames 1040, 34.667 s ±1 f (A and spliced B); A and B frames 80-1039 bit-identical (PNG hashes).

**Copy / layout (lens A)**
- [ ] Strings exactly as BRIEF §6.6 **plus U3F `Saved · har 30 sec` at f712-f719** (the only chip on f712-f719); no `Saved` chip spawned at f712.
- [ ] Ink inside x 70-1010, y 230-1480; nothing at x > 930 in y 1050-1700; ≤ 2 text blocks at once outside the end card.
- [ ] Captions: `cap.check() == []` for A and B; **no caption visible on f240-f257** (slam) **or f790-f799**; none inside
      `BF.jd_rect(t)` on f740-f839; hidden in [0, 2.667), [26.667, 29.333), [30.667, DUR]; caption words = words.json tokens; no *tees*.
- [ ] Payoff lockup fully gone on f880 (`out_t0=28.95`); `BIJLI NE SIKHAYA` at 86 px; no "SIKHAAYA" / "sikhaayi" anywhere.
- [ ] Hook B: HB3 `YAAD HAI?` at 0 % before 1.25 s, ≥ 95 % opacity on the frame of "yaad" (f50).
- [ ] Cover: `JAWAD_C11_COVER=1` still at 2.0 s, H1 at 1.0, window mean luma ≤ 10 (full range), keyword inside y 240-1680.

**Picture (lens B)** (BRIEF §8 picture boxes unchanged: f0/f9 YAVG ≥ 35 + p99 ≥ 200; power-off frames ≥ 2,000 px above
luma 90; f560 the only dark frame; tease f220-f221; darken-only power events; L4 p10 ≤ 40 / ≥ 250 share ≤ 2 %; hue top5; camera law; faces; seam) plus:
- [ ] S4: torch hotspot inside the copy box (x 70-240, y 1310-1380) on f340; inside the CRT glass (x 300-640, y 1050-1290) on f366-f379.
- [ ] Keycap presses on f580, f600, f620, f640, f650 … f710 exactly (Ctrl 1 f before S); chips at p+2.
- [ ] L7 beam crosses x 540 on f320 ±1; L8 fully closed on f560 only; L4 cut on f880.
- [ ] Measure the picture at phone size: every gate still also Read at 360 px.

**Audio (lens B; re-measured on the NEW kit only)**
- [ ] Mixes A FULL / A DRY / B FULL: -14.0 LUFS ±0.5, TP ≤ -2.0 dBTP (wav), ≤ -1.5 after AAC, **LRA 2.0-9 LU** (LEAD_DECISIONS 1).
- [ ] VO ≥ 8 LU over bed + SFX on every word (7 LU on one-syllable words, e.g. "hai?" under the f60 beep).
- [ ] VO timing in the mix = words.json (cross-correlate the mix's VO against `vo_stem.wav`: offset 0 ±1 ms): onset A 0.085 / B 0.300;
      V1 ends ≤ 1.31; hook VO ends ≤ 2.40 (A) / ≤ 2.40 (B); chhat ≥ 5.334; editor 13.33-13.40; V7 ≥ 16.40; Ctrl+S 21.43-21.50;
      Bijli 24.00 ±0.02; V10 ends ≤ 26.30; sabr 27.30-27.37; V12 ends ≤ 34.17.
- [ ] Drop-out f791-f798 RMS ≤ -45 dBFS, peak ≤ -30 dBFS; harmonium peak f820 ±1; loudest momentary inside 29.333-29.933 s.
- [ ] Sync ±1 f: beeps ↔ LED f40/f44/f60/f64 (B f0/f4/f40/f44); thocks ↔ presses; power_thunk ↔ f240/f300/f400/f480/f880; match ↔ f80.
- [ ] Cheer wordless (faster-whisper small hi/en on 8.0-10.0 and 29.5-31.1: no word p ≥ 0.5); V1 intelligibility per BRIEF §8 (whisper small).
- [ ] Loop: bed level last 0.5 s within 1 dB of the first 0.5 s; reverse_swell ends on DUR ±10 ms.

**Brand / truth**: BRIEF §8 unchanged (nothing from Organic Fostering / Floret; no UPS/inverter label; VO never "main/meri";
`@jawad_mp4` settled ≥ 1.5 s; one CTA; AI info on; audio named "Original audio · Bijli chali gayi · @jawad_mp4").

---------------------------------------------------------------------------------------------------------------

## 14. Who runs next

1. **motion-timeline-builder**: `bijli_chali_gayi.py` per BRIEF §6-§7 + this file; gate stills (§10) Read at full size and
   360 px; picture QA boxes; commit WIP after each working section.
2. **mix stage (sound-designer → music-supervisor)**, after `KIT_READY`: rebuild SFX stems, harmonium, mixes A FULL / A DRY /
   B FULL on the new kit; re-measure everything; kit problems to `workspace/brand_reels/wf/kit_bugs/bijli_chali_gayi.md`.
3. master render with the mix → motion-qa-reviewer (lenses A + B + verifier, §13) → delivery-packager (BRIEF §7, §6.15).
