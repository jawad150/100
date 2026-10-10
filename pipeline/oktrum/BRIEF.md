# Oktrum reels: brief

Contract for every agent. Inputs: INTAKE.md (ask, verified copy, VO scripts), BRAND.md (tokens, contrast pairs,
logo rules), KIT.md / oktrum_kit.py (Oktrum profile and shared widgets), TOOLKIT.md. Timings below are planned at
~2.6 words/s; when the ElevenLabs files land in `media/oktrum/vo/`, the builders re-time each VO phrase to the real
audio (word onsets from the waveform) and keep every on-screen key word within ±2 frames of its spoken word.

## 1. Deliverables
| | reel1 "Every market" | reel2 "Blink" | reel3 "Peace of mind" |
|---|---|---|---|
| module | `reel1.py` | `reel2.py` | `reel3.py` |
| DUR / BPM | 22.0 s / 124 | 22.0 s / 120 | 22.5 s / 110 |
| LOOK | `neon` (Oktrum profile) | `cine` | `airy`, ends on a navy plate |
| CTA | Try Demo Free | Open Live Account | Get Started |
1080x1920, 30 fps, H.264 master + share encode, cover JPG, 48 kHz stem. Audio: VO (voice A) + SFX (`audio.py`
catalog) + procedural music bed; final mix about -14 LUFS, true peak <= -2.0 dBTP, VO ducks music by ~6 dB.
No burned captions: every VO beat shows its key word on screen.

## 2. Verified copy
Only INTAKE.md §3 lines (source: oktrum.com home page, 2026-10-10) and the VO scripts in INTAKE.md §4. Every end
card carries the risk line "Trading involves high risk. You could lose some or all of your investment." (>= 28 px).
Do-not-claim list: INTAKE.md §3. Ticker/price figures are illustrative UI only.

## 3. Brand rules (BRAND.md)
- Dark looks: text IVORY; accents BLUE/CYAN/VIOLET; never put the logo on a glow of its own blue/violet; dark pool
  behind the logo.
- Light look (reel3): text INK or BLUE_DEEP #3A55E0; BLUE/VIOLET only for heroes >= 130 px; UP_DEEP/DOWN_DEEP for
  figures; the gradient wordmark is never placed on the light page: reel3's end card sits on a navy plate.
- Fonts: Inter Tight Black/ExtraBold heroes (`extrude3d_brand`, `deep_glow`, `flat`), Inter UI, JetBrains Mono
  figures, Instrument Serif Italic (`serif_italic`) for ONE accent word per beat.
- Gold (AMBER, `gold` preset) only on reel1's gold beat.

## 4. Safe zones and sizes
Key copy x 70-1010, y 230-1480; CTA bottom <= y 1600; nothing textual below y 1620; no copy at x > 930 for
y 1050-1700. Hero >= 130 px, UI >= 34-40 px (30 px on tilted UI), fine print >= 28 px. No full-frame flash or fade;
motion blur never crosses a cut (switch half a frame early); eased exits; 5-7 samples on fast moves.

## 5. Look matrix
| reel | look | dominance | hero type | signature devices | transitions | camera | SFX palette |
|---|---|---|---|---|---|---|---|
| 1 | neon void, aurora blue/violet, dot grid | BLUE 60 %, VIOLET 25 %, CYAN rim | `extrude3d_brand` slams + serif accent | 3D objects per market (coin_usd, gold_bar, coin_btc, chip), `dot_sphere` assembling, orbit `asset_tag`s, `ticker_tape`, MT5 dashboard window | whip pans, zoom-through the globe, card tunnel | orbit on easy ease, shake on slams | impact_big, whoosh_fast, whip, glass_tap, coin_ring, logo_sting |
| 2 | cine navy, anamorphic cyan streaks, grain, rays | NAVY, CYAN streaks, UP/DOWN data | `serif_italic` giant words + Inter Tight | `blink` hook over `candles`, `trade_window` + cursor BUY + `order_toast`, candles3d fly-by, `light_rays` | blink, light-leak band, speed streaks, whip | slow push-ins, rack focus, one fast whip | heartbeat, flash_hit, ui_click, check_ding, whoosh_by, riser, sub_drop |
| 3 | airy ice-white, faint navy dot grid, violet/cyan blooms -> navy plate | IVORY page, BLUE_DEEP/INK text, DOWN on the crash | INK/`flat` heroes + serif accent | candle_red crash + balance `T.Counter` stopping at 0.00, shield_lock day_anim, feature cards on a light trail, navy plate end | continuous camera (no cuts), navy plate grows from the shield | follow-the-object travel, 6-8 samples on moves | downlifter, impact_soft, glass_tap, toggle_on, shimmer, pop, logo_sting |

## 6. Timelines (t in s; VO times are estimates until the files land)

### 6.1 reel1 "Every market" (DUR 22.0, BPM 124: beat 0.484 s; music drop at 3.871 (on the VO))
| t | VO | on screen | visuals / camera | SFX / music |
|---|---|---|---|---|
| 0.00-0.80 | "Forex." | FOREX (extrude3d_brand ~210 px, y 760) | coin_usd spins in from depth to the lens, whip right | impact_big + whoosh_fast at the slam (0.30) |
| 0.80-1.45 | "Gold." | GOLD (gold preset) | gold_bar punches in, warm rim only here | impact_big 0.95, coin_ring |
| 1.45-2.10 | "Bitcoin." | BITCOIN | coin_btc flip, spin blur | impact_big 1.60, coin_flip |
| 2.10-3.00 | "Nvidia." | NVIDIA | chip slides in with cyan core flare; ticker_tape streaks across y 1300 | impact_big 2.25; riser ending 3.0 |
| 3.00-4.60 | "All on one platform." | "All on *one* platform." (serif accent on "one") | the four objects are pulled to centre and become the `dot_sphere` (assemble 0->1), orbit `asset_tag`s (EUR/USD, XAU/USD, BTC/USD, NVDA, S&P 500, WTI OIL) | drop 3.0, sub_drop, shimmer |
| 4.60-9.00 | "Trade forex, commodities, stocks, indices and crypto on MetaTrader 5." | glass chips appear one per word: Forex · Commodities · Stocks · Indices · Crypto (y 1180-1400); at 7.4 "Powered by MetaTrader 5" | camera orbits the globe; 7.2 zoom-through the sphere into an MT5 multi-asset dashboard window (candles + ticker rows) | glass_tap per chip on beats; air_zoom on the zoom-through |
| 9.00-11.30 | "Spreads from zero point two pips." | Counter rolls 2.0 -> **0.2** PIPS (mono, ~200 px), label "Spreads from" | card tunnel of market cards resolves on the counter | whoosh_by in the tunnel; slot_tick (align start), cash_kaching off, use check_ding at land |
| 11.30-12.80 | "Zero hidden fees." | "0%" slam + "Zero Hidden Fees" | the % glyph shatters a fee tag (`asset_tag` style) | impact_big, glitch_short |
| 12.80-16.40 | "Oktrum. Trade the global markets with precision." | "Trade the global markets with *precision*." | dot_sphere big again (spin), light sweep across the type | riser into 16.4 |
| 16.40-22.00 | "Try a free demo today." | okt_mark night_anim -> flat logo (BRAND.md min width), button "Try Demo Free" (cursor press 17.3), "oktrum.com", risk line | dark pool behind the logo, no particles on logo or copy; settled from 18.3 to 22.0 | logo_sting at 16.6, ui_click + toggle_on 17.3, music resolves |

### 6.2 reel2 "Blink" (DUR 22.0, BPM 120: beat 0.5 s; cinematic hybrid, the hit at 3.0)
| t | VO | on screen | visuals / camera | SFX / music |
|---|---|---|---|---|
| 0.00-1.20 | "Blink..." | giant "Blink." (serif_italic ~260 px) | macro `candles` chart in cine look, last candle ticking; `blink` closes 0.95-1.10 and reopens 1.10-1.35 | heartbeat x2 from 0.0; flash_hit at the closed lid 1.05 (local, lids are dark) |
| 1.20-3.00 | "and the price has already moved." | price tag jumps 67,200 -> 67,420 ▲ (mono, UP) while the lids were shut; "already *moved*." | anamorphic `streaks` on the price tag, slow push-in | tick + whoosh; riser ending 3.0 |
| 3.00-5.80 | "In trading, every millisecond counts." | "Every *millisecond* counts." | candles3d cluster whips past the lens (7 samples), `light_rays` from the top; blurred racing digits with no legible value | sub_drop 3.0, whoosh_by panned |
| 5.80-11.00 | "Oktrum runs on ultra-low-latency servers for instant order filling, on MetaTrader 5." | chips "Ultra-low latency" (6.6) and "Instant order filling" (8.0); `trade_window` BTC/USD; cursor presses BUY at 9.0; `order_toast` "Order Filled — BUY 0.5 BTC @ 67,200" at 9.3; "Powered by MetaTrader 5" at 10.2 | tilted glass window in 3D with rack focus; a cyan light pulse runs from the button out of frame and back (round trip) | ui_click 9.0, check_ding 9.3, toast_chime, glass_tap on chips |
| 11.00-14.40 | "Eliminate lag, and seize every market opportunity." | "Eliminate *lag*." slam, then "Seize every opportunity." | `line_chart` draws up with a light sweep; whip to the end card at 14.4 | impact_big 11.2, whip 14.4 |
| 14.40-22.00 | "Open your live account at oktrum dot com." | okt_mark night_anim -> flat logo, button "Open Live Account" (press 15.8), "oktrum.com", risk line | navy pool, gentle streak behind (not on) the logo; settled 16.8-22.0 | logo_sting 14.6, ui_click + toggle_on 15.8 |

### 6.3 reel3 "Peace of mind" (DUR 22.5, BPM 110: beat 0.545 s; calm, lifts at 10.909)
| t | VO | on screen | visuals / camera | SFX / music |
|---|---|---|---|---|
| 0.00-2.80 | "What happens if the market crashes overnight?" | "What if the market *crashes* overnight?" (INK + serif accent in DOWN_DEEP) | ice-white page; candle_red (day) plunges top to bottom through the frame with a `candles` crash behind; "Balance" `T.Counter` falling fast (illustrative) | downlifter into 2.8, impact_soft at the plunge |
| 2.80-6.00 | "With Oktrum, your account can never go below zero." | counter stops at **0.00** (3.6) and holds; "Your account can never go below *zero*." | shield_lock day_anim slams in front of the counter at 3.6 (padlock click frame -> 3.9) | glass_tap + toggle_on at the click, sub swell |
| 6.00-11.00 | "That's negative balance protection, plus bank-tier encryption and expert support." | cards on a light trail: "Negative Balance Protection" (6.3), "Bank-Tier Encryption" (8.4), "22/5 Expert Support" (9.6); small "PCI DSS Compliant" badge (10.3) | continuous camera travels along a violet->cyan light-trail ribbon from card to card (no cuts) | whoosh_by per move, pop per card, shimmer |
| 11.00-15.60 | "Trade with total peace of mind. Oktrum. Trade with confidence." | "Trade with total *peace of mind*." then "Trade With Confidence" | camera pulls back to all three cards around the shield; a navy plate grows from the shield and fills the frame by 15.2 | music lifts at 11.0, riser into 15.6 |
| 15.60-22.50 | "Get started at oktrum dot com." | on navy: okt_mark night_anim -> flat logo, button "Get Started" (press 16.6), "oktrum.com", risk line | settled 17.4-22.5 | logo_sting 15.8, ui_click + toggle_on 16.6 |

## 7. 3D assets (Blender, `assets3d_oktrum.py`)
okt_mark (night spin, night_anim), shield_lock (day yaw, day_anim, night yaw), coin_btc and coin_usd (night spin),
gold_bar (night yaw), candles3d (night yaw), candle_red (day yaw), chip (night yaw). Builders use labelled
placeholders until `<WS>/assets3d/<name>/<variant>/meta.json` exists.

## 8. Sound and music
Sound designer: `reelN_sfx.py` with the cues above (align='hit', <= 3 sounds per instant). Music supervisor:
`reelN_music.py`, a procedural bed per reel on its BPM grid (reel1 tech-house drive, drop at 3.871; reel2 cinematic
pulse with sub hits and ticking, hit at 3.0; reel3 airy future-garage, lift at 10.909), VO-ducked, final mix
`<WS>/audio/reelN_mix.wav`. Render with `--audio <WS>/audio/reelN_mix.wav`.

## 9. Module contract
`import oktrum_kit as OK` first. `DUR, LOOK, BPM`, `prewarm()`, pure `draw(t)`, `post(cv, t)`, `samples(t)`,
`cues()` (draft until the sound designer delivers). Static sprites cached in `prewarm()`. `draw(t)` never keeps
per-frame state.

## 10. Real VO timings (voice A, `vo_prep.py`; supersedes the VO estimates in §6)
`python3 vo_prep.py` writes `<WS>/audio/reelN_vo.wav` (VO at 0.20 s, pauses tightened to <= 0.34 s, -16 LUFS) and
`reelN_vo.json` (phrase t0/t1 in edit time, also copied next to the code). Builders read `reelN_vo.json` and pin each
§6 beat to its phrase: the scene boundaries in §6 move with the phrases; the look, devices and order stay.
| reel | VO ends | DUR | end card settled by |
|---|---|---|---|
| 1 | 18.51 s | 22.0 | 17.6 (CTA phrase 17.24-18.51) |
| 2 | 17.66 s | 21.5 | 16.4 (CTA phrase 15.15-17.66) |
| 3 | 17.16 s | 21.5 | 16.2 (CTA phrase 15.30-17.16) |
Key phrase onsets: reel1 Forex 0.26, Gold 1.19, Bitcoin 2.10, Nvidia 3.17, "All on one platform" 4.11, list 5.79,
"Spreads" 10.44, "Zero hidden fees" 12.69, "Oktrum" 14.24, "Trade the global markets" 15.08, CTA 17.24.
reel2 Blink 0.24, "price has already moved" 1.16, "every millisecond counts" 3.88, "Oktrum runs" 5.73, "on MetaTrader 5"
10.07, "Eliminate lag" 11.60, "seize" 12.91, CTA 15.15.
reel3 question 0.26, "With Oktrum" 2.66, "never go below zero" 3.76 (counter stops ~4.9 on "zero"), "negative balance
protection" 6.11, "bank-tier encryption" 8.14, "expert support" 9.75, "peace of mind" 11.12, "Oktrum" 13.01,
"Trade with confidence" 13.88, CTA 15.30.
