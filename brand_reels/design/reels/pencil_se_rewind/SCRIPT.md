# SCRIPT · Pencil Se Rewind (text-led)

v1, 2026-10-11. Machine copy: `script.json` (lines, tokens with onset frames, VO, hooks). Grid: 112.5 BPM, 16 f / beat,
64 f / bar, DUR 1024 f. `*` = the line's keyword (glowing Instrument Serif Italic, `jw_key`); everything else is white
grotesk (Poppins, `jw_caps` / `jw_caps_bold` / `jw_body`). Captions carry the story with no voice; the VO column is an
optional layer (Roman for captions, Devanagari for TTS, 1:1 tokens).

## 1. Hooks

| rank | id | mechanism | on screen | frame 0 | muted read |
|---|---|---|---|---|---|
| 1 | **A** (public) | pattern interrupt + callback: the object is the answer | `REWIND BUTTON?` / `*Pencil.*` (slam f16) | macro, hex pencil already spinning in the cassette hub, lamp-lit | the picture IS the answer; works with no sound |
| 2 | **B** (Trial Reel, f0-f63 only) | stakes / sound memory: the dying-battery slowdown | `BATTERY` / `*khatam?*` (slam f32) | walkman, REW key held down, amber LED, motor winding down | the held-down key + question read alone |
| 3 | R1 (reserve) | curiosity | `90s ka *scrub tool*` | | gives the twist away |
| 4 | R2 (reserve) | stakes | `CASSETTE *phans gayi?*` | | spends the re-hook |

A and B differ only before the splice f64; L2 ("Walkman ki battery bachani thi,") follows both. The payoff (L14)
repeats hook A's shape, and the outro question hands back to "Rewind button? Pencil." on replay.

## 2. On-screen lines (frames inclusive; exits inside the window)

| id | f in-out | s | shot | kind | Roman (house spelling) | layout |
|---|---|---|---|---|---|---|
| HA | 0-63 | 0.00-2.13 | S1 | lockup | `Rewind button? *Pencil.` | caps `REWIND BUTTON?` jw_caps 86 (817 px) at y 400, mid-rise at f0 (t0 -0.1); key `Pencil.` jw_key 250 (604 px) at y 580 slams f16; underline f24-f44 y 700; exit f56-f63 |
| HB | 0-63 | 0.00-2.13 | S1B | lockup | `Battery *khatam?` | caps `BATTERY` jw_caps 96 at y 400 (t0 -0.1); key `khatam?` jw_key 240 (776 px) slams f32; exit f56-f63 |
| L2 | 70-124 | 2.33-4.17 | S2 | snake, upper | `Walkman ki *battery bachani thi,` | band centre y ~390 |
| L3 | 134-188 | 4.47-6.30 | S3 | snake, upper | `toh pencil se *ghumate the.` | |
| L4 | 198-252 | 6.60-8.43 | S4 | snake, lower | `*Gaana dhoondna ho?` | band centre y ~1380 (label in the middle) |
| L5 | 262-319 | 8.73-10.67 | S5 | lockup | `Sirf *andaza.` | caps `SIRF` 96 at y 420; key `andaza.` 220 (761 px) at y 590, per-glyph rise from f268; exit f312-f319 |
| L6 | 320-383 | 10.67-12.80 | S6 | 8th-note stack | `Play. *Galat! Phir se.` | `Play.` jw_caps_bold 150 y 420 slam f320 · `Galat!` jw_key 200 (442 px) y 590 slam f328 · `Phir se.` jw_caps_bold 150 (606 px) y 760 slam f336; all exit f376-f383 |
| L7 | 384-419 | 12.80-14.00 | S7 | slam | `*Mil gaya!` | jw_key 220 (744 px) y 520, SLAM spring f384; exit f414-f419 |
| L8 | 420-446 | 14.00-14.90 | S7 | snake, upper | `Aur phir...` | no keyword: the ellipsis is the open loop |
| L9 | 448-511 | 14.93-17.07 | S8 | **re-hook lockup** | `Cassette *phans gayi!` | caps `CASSETTE` 96 y 400 rises f448; key `phans gayi!` jw_key 190 (809 px) y 570 SLAM f464 (45.3 %) with D7; exit f504-f511 |
| L10 | 514-574 | 17.13-19.17 | S9 | snake, upper | `Saans rok ke, *pencil se wapas.` | |
| L11 | 588-638 | 19.60-21.30 | S10 | snake, top | `Aaj bhi *wahi karte hain.` | band centre y ~330 (above the NLE viewer) |
| L12 | 640-703 | 21.33-23.43 | S11 | 8th-note slams (replace) | `Peeche. Aage. Peeche. *Yahan.` | one word at a time at (540, 330): Peeche f640 · Aage f648 · Peeche f656 · `Yahan.` jw_key 220 f664-f700; exit f696-f703 |
| L13 | 706-751 | 23.53-25.07 | S12 | snake, top | `Bas tool *badal gaya.` | gone before the drop-out f752 |
| L14 | 768-895 | 25.60-29.87 | S13 | **payoff lockup** | `Pehla editing tool? *Pencil.` | `J.HouseTitle('PEHLA EDITING TOOL?', 'Pencil.', caps_px=74, key_px=260)`: caps (860 px) y 360 f768, key (629 px) y 560 rises from f776, underline f784-f806 y 700; exit f880-f895 |
| L15 | 816-895 | 27.20-29.87 | S13 | 2-line body | `Scrubbing toh *cassette pe sikhi thi.` | `Scrubbing toh` jw_body 56 y 772 / `cassette pe sikhi thi.` jw_body 56 with `cassette` inline jw_key 96, y 846; exit with L14 |
| L16 | 896-1023 | 29.87-34.13 | S14 | profile outro | `Aap ki pehli *cassette kaunsi thi?` | `PO.ProfileOutro(question, key='Pencil ya pen?', dur=128/30)` (question auto-wraps to 2 lines) |
| L16k | 896-1023 | | S14 | outro key | `*Pencil ya pen?` | the card's serif key line |

Holds: every snake line >= words / 3 s (checked in `script.json` `hold_s` vs `need_s`); slam builds follow the
0.27-0.53 s per word rule and the completed phrase holds >= 1.2 s. Never more than 2 text blocks at once (L14 + L15).
Snake words: `start = onset_f / 30` (one word every 5 f from `in_f`), `end = (out_f + 1) / 30`; hide the lockup
windows (HA, HB, L5, L6, L7, L9, L12, L14, L15) from the snake track.

**Spelling notes.** House rule (Bijli SCRIPT): a long vowel is doubled only in a long stressed first syllable, so
`Gaana, Peeche, Aage, Saans, dhoondna` but `andaza, sikhi, ghumate`. `phans` keeps the nasal n. `Galat` (TTS ग़लत with
nukta). `kaunsi` is one token (DEV कौनसी) to stay 1:1. Cross-border check: walkman, cassette, pencil, gaana, andaza,
galat, phans gayi, saans rok ke, wahi, badal gaya are daily speech in Lahore, Karachi, Delhi and Mumbai. No film,
singer, brand or team name anywhere.

## 3. Optional VO (not approved; leave room in the mix)

| id | start f | Roman | Devanagari | delivery |
|---|---|---|---|---|
| V1 (A) | 3 | Rewind button? Pencil. | रिवाइंड बटन? पेंसिल। | dry question, beat, deadpan answer |
| V1B (B) | 3 | Battery khatam? | बैटरी ख़त्म? | alarmed, quick |
| V2 | 70 | Walkman ki battery bachani thi, toh pencil se ghumate the. | वॉकमैन की बैटरी बचानी थी, तो पेंसिल से घुमाते थे। | warm, remembering |
| V3 | 198 | Gaana dhoondna ho? Sirf andaza. | गाना ढूँढना हो? सिर्फ़ अंदाज़ा। | playful |
| V4 | 320 | Play. Galat! Phir se. | प्ले। ग़लत! फिर से। | clipped, on the 8ths |
| V5 | 386 | Mil gaya! Aur phir... | मिल गया! और फिर... | relief, then ominous |
| V6 | 466 | Cassette phans gayi! | कैसेट फँस गई! | panic, after the slam transient |
| V7 | 516 | Saans rok ke, pencil se wapas. | साँस रोक के, पेंसिल से वापस। | whispered, careful |
| V8 | 590 | Aaj bhi wahi karte hain. | आज भी वही करते हैं। | plain, a smile |
| V9 | 640 | Peeche. Aage. Yahan. | पीछे। आगे। यहाँ। | tight (skips the 2nd Peeche) |
| V10 | 708 | Bas tool badal gaya. | बस टूल बदल गया। | dry; ends before f752 |
| V11 | 770 | Pehla editing tool? Pencil. | पहला एडिटिंग टूल? पेंसिल। | the payoff: pause before "Pencil" |
| V12 | 818 | Scrubbing toh cassette pe sikhi thi. | स्क्रबिंग तो कैसेट पे सीखी थी। | proud, light |
| V13 | 930 | Aap ki pehli cassette kaunsi thi? | आप की पहली कैसेट कौनसी थी? | inviting, rising "thi?", ends <= f1005 |

63 words (version A) in ~34 s: comfortable at 2.7 w/s. TTS risks to test first: स्क्रबिंग (cluster), एडिटिंग, फँस.
