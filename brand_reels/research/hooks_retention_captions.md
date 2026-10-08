# Hooks, Retention & Captions Playbook: @jawad_mp4

**For:** Jawad (@jawad_mp4), a video editor and motion designer with a Pakistani and Indian audience. This is his own brand: orange-red embers on warm black.
**Reels:** Hinglish / Roman Urdu voice-over, 30-40 s, 1080x1920, 30 fps.
**Roles:** reels-studio `script-hook-writer` and `caption-designer` combined. Checked 2026-10-08.
**Scope:** hook science and 40 original hooks · retention architecture · on-screen kinetic captions (house style, fonts, safe zones, timing, 10 original caption devices with toolkit build notes) · post-caption copywriting and 5 templates · cover rules.
**Originality:** everything here is written for Jawad. Nothing is taken from the Organic Fostering or Floret projects: no 'neon', 'amber' or 'airy' looks, no houses, hearts or £ props, no copy.
**Brand alignment:** this playbook follows the `jawad-brand-reels` skill, `pipeline/jawad_reels/BRAND.md`, `project.json` and `jawad_kit.py`. Those are the source of truth for palette, fonts, looks and the end card. All type sizes and widths below were measured with the kit's real house styles (`jw_caps`, `jw_body`, `jw_key`) through `T.measure`.

> **Evidence labels used below.** **[Meta]**: Meta's own documentation or blog. **[2nd]**: secondary reporting (trade press or vendor blogs) that I could not check against a primary source. **[Measured]**: I measured it here (fonts, colours, reference reels). **[Inference]**: my reasoning, to be tested on Jawad's own Insights. Platform numbers change, so re-check anything marked [2nd] that a decision depends on.

---

## 0. The 12 rules (read this if nothing else)

1. **All 3 hook layers land by 1.5 s.**
   - Motion is already running on frame 0.
   - On-screen text (max 5 words) is readable by 0.5 s.
   - The spoken line starts within 3 frames (the brand's hard limit is 0.3 s).
   - No logo, no "Assalam-o-alaikum / Namaste doston", no fade-in from black, no "wait for the end".
2. **The text hook is the headline version of the spoken hook, not a transcript.** Muted viewers get the whole idea from 1-5 words. Sound-on viewers get the full sentence.
3. **One serif-italic ember keyword per text block.** If everything glows, nothing does.
4. **Every 3-5 s something new happens:** a visual event, a verbal turn or a sonic hit. Nothing is static for more than 2 s.
5. **Re-hook at about 45-50 % of the running time** with a pattern break: 0.3 s of silence, a whip or a flame exposure push (no full-frame white flashes: brand rule), and a new visual world.
6. **The payoff lands at 65-80 % of the running time.** The last 15-20 % is for the bonus beat and the end card. The end card holds the single CTA and the loop bridge.
7. **Build the loop into the end card.** The brand end card holds ≥ 1.5 s settled, over the living world rather than on black. Under it, the last VO half-sentence completes the first line and the camera glides back to the frame-0 composition. Never fade to black or to silence.
8. **Ask for one thing.** Either comment a keyword, or send it to a named person, or save it. Never all three.
9. **Write for the send.** Every reel needs a "send line": who the viewer will send it to and what that send says on their behalf. Desi viewers send reels to say what they can't say directly.
10. **Use pan-desi Hindustani.** Use neutral words, Jawad's house spellings (§2.5, from his own SRT), no currency figures, and no Indo-Pak politics or rivalry.
11. **Captions stay inside the safe zones.** x 70-1010 and y 230-1480, nothing at x > 930 for y 1050-1700, and the bottom 300 px stay clear.
12. **Every claim is true.** Personal-story lines (first paid edit, a family photo, a cut count) need Jawad's confirmation before they are rendered. They are flagged ⚑ below.

---

## 1. What Instagram rewards (October 2026)

| signal / fact | what it means for Jawad | evidence |
|---|---|---|
| **Watch time, likes per reach and sends per reach** are the three main ranking signals. Sends weigh most for reaching **non-followers**. | Design every reel to be *sent*: identity mirrors, indirect messages and in-group jokes (§3.7). | [2nd] Mosseri (Jan 2025), via [Unfollr](https://www.unfollr.com/blog/how-instagram-algorithm-works) and [Stackinfluence](https://stackinfluence.com/blog/how-does-the-algorithm-for-reels-work). One report says send rate outranks watch time ([watsspace](https://watsspace.com/blog/adam-mosseri-explains-how-instagram-ranking-really-works/)); the order is unresolved. |
| **Skip rate** = the share of viewers who swipe away in the first **3 s**. It sits in Reels Insights next to a **retention curve**, and has done since Aug 2025. Meta's ranking explainer lists "watched at least 3 s" as an input. | The hook window is 3 s. Aim to land it in 1.5 s. Use skip rate to judge the hook and the retention curve to judge the story. | [2nd] [Social Media Today](https://www.socialmediatoday.com/news/instagram-adds-retention-insights-reels/758464/), [Metricool](https://metricool.com/instagram-reel-analytics/). Benchmarks are unofficial: under 30-40 % skip is "healthy", over 50 % means a weak hook. |
| **Views count replays.** A loop or a scroll-back counts as a new view. Reach counts unique accounts. | Seamless loops raise views and time watched. Judge real audience growth on **reach** and **sends**, not views. | [2nd] [socialcrawl](https://www.socialcrawl.dev/blog/how-instagram-counts-views), [SocialPilot](https://www.socialpilot.co/instagram-marketing/instagram-views-metrics-changes) |
| **Originality.** Accounts that mostly post unoriginal content are removed from recommendations. In Apr 2026 this was extended from Reels to photos and carousels. Recommendation is assessed over a rolling 30 days. | Jawad's fully original renders are an advantage. Avoid other people's IP (e.g. superhero characters) in brand reels. | [Meta] [creators.instagram.com, 30 Apr 2026](https://creators.instagram.com/blog/rewarding-original-creators-on-instagram) |
| **5 hashtags per post at most**, counting caption and comments together. Hashtags are labels for context and search, not a reach lever. | Use 3-5 precise tags (§5.4). | [2nd] [Sirency, citing The Verge](https://www.sirency.com/blog/instagram-hashtag-limit), [Social Media Today](https://www.socialmediatoday.com/news/instagrams-testing-new-limits-how-many-hashtags-you-can-add/707471/). Dates conflict (Dec 2025 vs Jun 2026); the cap itself is consistent. |
| **Google indexes public posts from professional accounts** (since 10 Jul 2025). | Captions are search copy: put English keywords in the first 2 lines (§5.3). | [2nd] [Vaizle](https://insights.vaizle.com/?p=8751), [ovrdrv](https://www.ovrdrv.com/insights/google-indexing-instagram-content) |
| **Trial Reels** go to non-followers only, so you can test before sharing widely. They can only be set in the app (the API has no flag). | A/B test hooks: keep the body identical and swap only the first 3 s (§2.7). | [2nd] [Publer](https://publer.com/blog/instagram-trial-reels-guide/), [brandid](https://brandid.app/blog/instagram-trial-reels/) |
| **Comment-to-DM ("private reply") rules:** one message per commenter, sent within **7 days** of the comment. Follow-ups only if they reply, and within 24 h of that reply. The DM lands in Requests if they don't follow you, and it carries a link to the post. | A "comment KEYWORD" CTA must deliver something real in the **first** message (§3.6). | [Meta] [Private Replies docs, updated 2 Jul 2026](https://developers.facebook.com/docs/instagram-platform/private-replies/) |
| **About 55-60 characters** of the caption show in the Reels viewer before "more" (about 125 in the feed). | Line 1 of the post caption is ≤ 55 characters and carries the hook (§5.1). | [2nd] [lettercounter](https://lettercounter.org/blog/instagram-reels-caption-length/), [bundle.social](https://bundle.social/blog/instagram-character-limits-guide) |
| **Meta AI voice translation** supports Hindi (since Oct 2025). Urdu was reportedly not supported. | Leave it **off** for these reels: a dub would contradict the burned-in Roman Urdu captions. | [2nd] [Business Today](https://www.businesstoday.in/amp/technology/news/story/meta-adds-hindi-ai-translation-for-reels-on-instagram-and-facebook-497661-2025-10-10), [Meta newsroom JP, Jul 2026](https://about.fb.com/ja/news/2026/07/meta-ai-translation/) |
| **What the trend reports say:** "authentic beats polished" for personal brands, but the first 1-2 s and the pacing still decide. "Wait for it" openers read as low quality. | Jawad's edge is polish *about* real, relatable life. The craft must serve a human moment, not replace it. | [2nd] [opus.pro, May/Oct 2026](https://www.opus.pro/blog/editing-aesthetics-dominating-short-form-2026), [blitzcut](https://blitzcutai.com/blog/best-instagram-reels-hooks-2026) |

**What the reference reels show [Measured]:**
- **ref3** (21 s personal-brand reel, transcribed with faster-whisper):
  - 70 words, **3.36 words/s**, VO from frame 0.
  - The hook is a conditional call-out: "If you're dreaming of charging … and your page looks like this, then stop dreaming".
  - The payoff runs to 18.5 s, then the CTA "**Comment 'roadmap' and I'll show you how**" in the last 2 s.
- **ref2** (35 s kinetic type):
  - 95 words in 32 s, **2.97 words/s**.
  - Opens on a spoken question at 0.0 s ("What do you think creativity is?", 1.9 s long).
  - Only 5 hard cuts. Retention comes from type and camera motion, not cuts.
- Both refs pair a **tight sans with a light editorial serif-italic**, which is the same family of pairing as Jawad's house style. Jawad's ember glow and underline are what make his version recognisable.

---

## 2. Hook science

### 2.1 The 3-layer hook, frame by frame (30 fps)

| frames | time | visual (motion) | on-screen text | spoken (VO) | sound |
|---|---|---|---|---|---|
| **f0** | 0.00 | **Already mid-motion and bright.** Start the camera `K.Track` keys at t = -0.4 s so frame 0 is mid-move. Use motion blur (`samples(t)` = 5-7). No black and no fade. | Optional: one grotesk word already present (e.g. "RUKO."). | First syllable at f0-f3. No breath and no greeting before it. | A transient on f0-f2 (`impact_soft`, `glitch_short`, `ui_click` or `whip`). |
| f3-f12 | 0.1-0.4 s | A second motion layer (parallax, a UI pop, a 3D prop entering). | The grotesk words rise in (`jw_caps`; a `Glyphs.slam` is allowed on hook grotesk words only). The simplest route is `J.HouseTitle(caps, key).draw(cv, t, x, y, t0=-0.1)`: caps rise over 0.6 s, the keyword rises per glyph from 0.22 s, the underline draws on from 0.55 s. | Hook line continues. | — |
| **f12-f18** | 0.4-0.6 s | — | The **serif-italic keyword** (`jw_key`) settles. Rise or wipe only: **no bounce on brand type**. The underline (`J.underline`) starts drawing on. The whole block is readable by f18. | — | A soft hit on the keyword (`shimmer` or `impact_soft`, -3 dB). |
| f18-f36 | 0.6-1.2 s | **Escalation:** the second visual event by 1.0 s (reveal, push-in, scale break). | Holds, or is joined by a second block (max 2 blocks). | The hook sentence completes. At 2.8 words/s, 1.5 s holds about 4 words, so the first sentence is 4-8 words. | — |
| f36-f45 | 1.2-1.5 s | An **open-loop picture**: something unresolved (a stuck 99 %, a "Seen" with no reply, a photo about to move). | — | The open-loop phrase: "…aur phir", "dekho kya hua", "ruko". | A riser starts, if the next beat pays off within 3 s. |

**Checks:**
- Frame 0 must work as a still with the sound off.
- The hook is understood without the VO, and without the text.
- The hook line is spoken by 2.5-3.0 s, inside the 3 s skip window.

### 2.2 Hook mechanisms

| mechanism | psychological lever | best for | risk |
|---|---|---|---|
| **Call-out** ("Agar tum bhi…", "Sirf editors…") | Self-identification: "this is about me" | Editors, freelancers, creators | Too broad a call-out = no one feels called. Be hyper-specific (3 a.m. render, the "Seen" at 2:14 AM). |
| **Relatable pain + open loop** ("Bas ek chhota sa change… aur phir") | Recognition, then an unfinished story | Everyone who has had a client or boss | The payoff must top the setup. |
| **Contradiction / myth-bust** ("Content bura nahi, pehla second bura hai") | Cognitive dissonance; the viewer wants to resolve it | Creators, business owners | Must be Jawad's honest opinion, framed as an opinion. No fake stats. |
| **Curiosity gap** ("Har reel mein ek skip button chhupa hota hai") | The information gap pulls the viewer on (Loewenstein) | Creators, the general audience | Close the gap before 80 %. An unpaid gap breeds distrust. |
| **Dialogue / scene** ("Beta, kya karte ho?") | Instant shared culture, a mini-sitcom | The general desi audience | Keep it affectionate, never mocking elders or a region. |
| **Pattern interrupt** (the video edits itself, a power cut, a misplaced caption) | Breaks scroll autopilot | Everyone; shows Jawad's craft | It must connect to the message within 2 s, or it reads as a gimmick. |
| **Number / challenge** ("[N] cuts. Gin ke dikhao") | Gamification, comments, rewatches | Editors, creators | The number must be literally true in the final cut ⚑. |
| **Nostalgia + transformation** ("Ye photo 20 saal purani hai") | Emotion, family sends | The general desi audience | Consent and AI disclosure (§3.6, §5). |
| **Meta hook** ("Ye reel tumhe 2 second mein pakdegi") | Self-proving, and flatters the viewer's savvy | Creators, editors | One per month at most; it gets old. |
| **POV** ("POV: tumne editor ko bola 'bas cinematic bana do'") | The viewer is inside the joke | Everyone | A common format: the visual escalation must be what makes it his. |
| **"Send this to…"** | Hands the viewer a social use for the reel | Freelancer pain, friendship humour | Say it once, at the end or in the text block, not as the opening line. |

### 2.3 Pattern-interrupt toolbox built for the toolkit

All of these are Jawad's craft shown, not borrowed.
- **The frame becomes a timeline.** At 0.3 s the image shrinks into a viewer window. A playhead and clip blocks appear, and a razor cut slices to the next shot. Build: `ui.app_window` with a custom ember `ui.Look`, `win.plane`, and the `ui.Surf` clip blocks from §4.8-1.
- **Render reveal.** Frame 0 shows a wireframe or clay version of the hero shot. A Cycles-style bucket sweep resolves it to the final grade in 0.6 s. Build: §4.8-3 applied to the whole frame (mosaic, then sharp, behind a moving edge).
- **Error pop-up.** A glass dialog slams in: "ERROR · client_feedback_v9 can't be opened". This is a house device (see the "ERROR: can't delete this memory" cover). Build: `ui.glass_card` + `ui.put_text` + `K.impulse` shake + `glitch_short`.
- **Blackout.** Bright for 0.3 s, a power-cut drop to black, then only the ember keyword glows. Build: an exposure ramp in `K.post(..., exposure=)`, the keyword drawn after post with additive glow, and a UPS beep (custom sound).
- **Out-of-frame 3D.** A Blender prop breaks the frame edge toward the lens. Use DOF with `aperture` 40-60 and a near-plane fly-by (planes are clipped at the near plane).
- **Keyframe freeze.** Everything freezes, and keyframe diamonds and a motion path appear over the action. Build: §4.8-2.
- **Sound before picture.** Use a recognisable editor sound on f0 (a timeline-scrub chirp, or a Windows-style error "ding" made procedurally). The picture explains it at f6.

### 2.4 Hook-writing rules for Hinglish / Roman Urdu

- **Spoken hook:** 4-8 words, then a period. Use a loaded first word: *Client, Beta, Ruko, Light, Free, Tumhara, Ye photo*. Never start with "Aaj main aapko…", "Doston…" or "Kya aap jaante hain…".
- **Text hook:** 1-5 words in 2-3 short lines. Exactly **one** ember keyword, 1-2 words long and ≤ 10 characters (measured limits in §4.5).
- **Text ≠ VO verbatim.** The text is the compressed punchline ("BAS EK *chhota sa* CHANGE"); the VO is the full line.
- **Desi register:** spoken, warm and a little self-roasting. Use "tum" for peers and "aap" for business owners. Never mock elders, regions or professions.
- **Avoid:**
  - "wait for the end", "aakhir tak dekhna", "part 2 comment karo" (low-quality signals);
  - giveaway bait;
  - fake urgency;
  - unverifiable superlatives ("sabse best editor", "100 % viral").

### 2.5 Pan-desi language sheet

These are canonical spellings for VO scripts, captions and post copy. They are chosen to read naturally to both Indian Hinglish and Pakistani Roman Urdu readers.

| meaning | write | don't write | note |
|---|---|---|---|
| not | **nahi** | nahin, nai, nhi | |
| very | **bohot** | bahut, bohat, boht | the common internet spelling on both sides |
| is / are | **hai / hain** | he, h, hy | |
| in / I | **mein / main** | me, mai | keep these two distinct |
| so, then | **toh** | to | "to" clashes with English |
| what / why | **kya / kyun** | kia, kiun | |
| difference | **farq** | fark, farak | |
| life | **zindagi** | jindagi | z, not j, for Pakistani ears ⚑ VO |
| thing(s) | **cheez / cheezein** | cheej | |
| lie / truth | **jhoot / sach** | jhooth, jhut | |
| wedding | **shaadi** | shadi | |
| understand | **samajh** | samaj | |
| before / after | **pehle / baad** | pahle | |
| money | **paise** | pese | no ₹ or Rs figures: they split the audience |
| time | **time** | samay, waqt | the English loanword is universal |
| problem | **problem** | masla (PK), dikkat (IN) | prefer the loanword when the two sides differ |
| family | **ghar wale**, mummy-papa | ammi (PK-leaning), maa | use Jawad's own word only in his true-story reels |
| work / less | **kaam / kam** | | different words; check them |

**Safe shared culture:** chai, shaadi (mehndi or sangeet), rishtedaar and "beta kya karte ho", power cuts (light chali gayi), nani ka ghar, summer vacations, gali cricket, Nokia-era phones, exam results, the family WhatsApp group, a cheap phone with a cracked screen.

**Avoid:** Indo-Pak politics, flags and maps, team-vs-team cricket, religious comparisons, and caste or region jokes. These bring comment wars, which look like engagement but poison the brand and invite restrictions.

**VO note for the sound team (TTS with a Hindi voice) ⚑:**
- Feed the TTS **Devanagari with nukta letters** (ज़िंदगी, फ़र्क़, ख़्वाब, ग़लती if Jawad pronounces it) so "zindagi" is not voiced as "jindagi".
- Feed English words in Latin script if the engine handles code-switching; otherwise transliterate them.
- The captions always follow the spoken word in the Roman spellings above.

### 2.6 The 40 hooks (★ = top 10)

**How to read the table:**
- **Audience:** E editors · F freelancers · C creators · B small-business owners · G the general desi audience.
- **On-screen:** `/` = line break, CAPS = white grotesk, *italic* = the glowing serif keyword.
- **Fit:** every on-screen line was measured [Measured]. Grotesk caps fit at **96 px Poppins Bold** (widest 841 px) and every keyword at **150 px Playfair Display Bold Italic** (widest 875 px), within the 940 px safe width plus glow budget.
- **Upper band only:** lines marked ↑ are wider than 780 px. Place them in the upper band (y 300-1000), or drop to 80 px grotesk / 130 px serif in the lower band (y 1050-1480).

| # | aud | mechanism | spoken line (VO) | on-screen text | frame-0 visual (toolkit) | flags |
|---|---|---|---|---|---|---|
| **1 ★** | E F G | relatable pain + open loop + **sentence loop** | "Client ne bola, 'bas ek chhota sa change'… aur teen din chale gaye." | BAS EK / *chhota sa* / CHANGE | A glass chat bubble slides in with "Seen 2:47 AM". Behind it, the project timeline explodes into 40 clip blocks. | — |
| **2 ★** | G E | dialogue / desi scene | "Beta, kya karte ho? — Video editing. — Achha… shaadi ki video?" | BETA, KYA / KARTE HO? / *shaadi ki* / VIDEO? | Jawad (suit sheet, 'confused' headshot, red-orange rim) faces a glowing speech-bubble UI. The second bubble pops on the beat. | Keep it affectionate. |
| 3 | E C | number challenge | "Is reel mein [N] cuts hain. Gin ke dikhao." | [N] *cuts* / GIN KE DIKHAO | `T.Counter` rolling to N over a timeline that strobes on every cut. | ⚑ N = the true count in the final edit |
| 4 | E | relatable in-joke | "final, final_v2, final_FINAL… sach mein final." | FINAL_v7 / *sach mein* / FINAL | A file-rename field typing (`ui.search_bar`, caret), with a stack of file icons behind it. | — |
| 5 | E C | hyper-specific call-out | "Agar raat ke 3 baje render bar ko ghoor rahe ho… ye tumhare liye hai." | RAAT KE / *3 baje* / RENDER | A dark room, one glowing progress bar, and a wall clock at 3:00 in DOF. | — |
| **6 ★** | E F G | pattern interrupt (blackout) + pan-desi pain | "Light chali gayi. Aur Ctrl+S aakhri baar do ghante pehle dabaya tha." | LIGHT / *chali gayi* / CTRL + S ? | A bright timeline for 0.3 s, a hard blackout, and only the ember keyword glowing. A UPS beep. | — |
| **7 ★** | E C | meta pattern interrupt | "Ruko. Ye video khud ko edit kar raha hai." | RUKO. / *khud ko* / EDIT KAR RAHA | The reel's own frame shrinks into an NLE viewer. A playhead runs, and a razor cuts at 0.9 s to the next shot. | — |
| 8 | C | meta hook | "Ye reel tumhe pehle do second mein pakad legi. Dekho kaise." | PEHLE / *2 second* / MEIN PAKDUNGA ↑ | A `ui.progress_ring` counts 2 s. Hook elements are labelled live: "motion ✓ text ✓ voice ✓". | Explain the mechanics honestly afterwards. |
| **9 ★** | C B | contradiction | "Tumhara content bura nahi hai. Tumhara pehla second bura hai." | CONTENT NAHI / *pehla second* ↑ / BURA HAI | The word CONTENT is struck through by a razor line. A frame-0 thumbnail cracks. | — |
| **10 ★** | C B | comparison + comment trigger | "Same footage. Do edit. Batao, kaunsa scroll rokega?" | SAME FOOTAGE / DO EDIT / *kaunsa?* | A split screen: left is flat log-grey, right is the graded ember version. "L" and "R" chips. | Both edits must be real. |
| 11 | C G | muted-viewer call-out | "Tum ye mute pe dekh rahe ho. Mujhe pata hai." | MUTE PE / *dekh rahe ho* ↑ | A huge 3D muted-speaker icon cracks; the cracks glow ember. | Then reward turning the sound on. |
| 12 | C | myth-bust | "Trending audio laga do, viral ho jaoge — sabse bada jhoot." | TRENDING AUDIO ↑ / = *jhoot* | A music-note chip is slammed with a red "✕" stamp. | Opinion: Jawad must agree. |
| 13 | C | curiosity gap | "Har reel ke andar ek skip button chhupa hota hai. Main dikhata hoon kahan." | HAR REEL MEIN / SKIP BUTTON / *chhupa hai* | An x-ray scan line passes over a phone and reveals a glowing button inside the first second of a timeline. | — |
| 14 | C B | before/after reveal | "Phone ki ek boring video… aur das second baad." | BORING CLIP / *10 sec baad* | A shaky phone clip with a "RAW" tag, then a whip into the cinematic ember grade. | Real footage only. |
| 15 | F | confession | "Mera pehla paid edit itna sasta tha, batate hue sharam aati hai." | PEHLA PAID EDIT / *itna sasta* | A 3D price tag spins and refuses to show its number (curiosity). | ⚑ Jawad's true story |
| 16 | F | wordplay | "'Exposure milega' — freelancing ka sabse mehenga word." | *exposure* / MILEGA | A camera exposure dial spins to "∞" while a cost meter climbs. | — |
| **17 ★** | F G | send trigger | "'Free mein kar do na, tum toh dost ho.' — Ye reel usi dost ko bhejo." | FREE MEIN / *kar do na* | A chat bubble from "Dost 😇" with the share icon already bouncing. | — |
| 18 | F | relatable pain | "'Rate kya hai bhai?' — ye sawaal sun ke dimaag hang ho jata hai." | RATE KYA HAI? / *hang* | Jawad's face freeze-frames under a "Not responding" glass dialog with a spinning cursor. | — |
| 19 | F B | contrarian list | "Client portfolio nahi dekhta. Ye teen cheezein dekhta hai." | PORTFOLIO NAHI ↑ / *3 cheezein* | A portfolio grid folds away and 3 glowing slots stay empty (open loop). | Opinion; the 3 items must be Jawad's real process. |
| 20 | F G | horror parody | "Client ka 'Seen'… freelancer ki sabse darawni horror movie." | *seen* / 2:14 AM | The "Seen" label pulses like a jump-scare. Red flash, `sub_drop`. | — |
| **21 ★** | B | contrast | "Aapka product achha hai. Aapka video usse sasta dikhata hai." | PRODUCT ACHHA ↑ / VIDEO / *sasta* | A product on a turntable: crisp and graded on the left, phone-flat and grey on the right. A verdict stamp. | — |
| 22 | B E | visual gag | "'Logo thoda bada karo' — har business owner ki pehli demand." | LOGO / *thoda bada* | A logo plate grows on every beat until it pushes the frame edges out of the screen. | Use a fictional logo, not a real brand. |
| 23 | B | number contrast (rhetorical) | "Customer aapko teen second deta hai. Aapka intro aath second ka hai." | CUSTOMER: / *3 sec* / INTRO: 8 SEC | Two timers race. The 3 s one ends and "SKIP" fires before the intro finishes. | The 3 s mirrors IG's skip-rate window; the 8 s intro is a hypothetical. |
| 24 | B G | metaphor | "Aapka Instagram page aapki dukaan ka shutter hai. Abhi aadha band hai." | PAGE = SHUTTER ↑ / *aadha band* ↑ | A 3D rolling shutter, half down over a glowing storefront. | — |
| 25 | B | curiosity | "Chhoti dukaan, bada brand — farq sirf ek cheez ka hai." | CHHOTI DUKAAN ↑ / *bada brand* ↑ | A tiny storefront model that casts a giant cinematic shadow. | — |
| 26 | G | family scene | "Ghar walon ko aaj tak samajh nahi aaya main karta kya hoon." | GHAR WALE: / YE KARTA / *kya hai?* | A family-group chat UI: "beta job kab lagegi?" is typing. | — |
| 27 | G | relatable wedding | "Chaar ghante ki shaadi ki video… aur sab sirf gaane wala part dekhte hain." | 4 GHANTE / KI SHAADI / *gaane wala* / PART | A long timeline. Fast-forward streaks, then it stops on one glowing clip with dancing silhouettes. | — |
| **28 ★** | G | nostalgia + AI transformation | "Ye photo bees saal purani hai. Aaj ye phir se chali." | *20 saal* / PURANI PHOTO | A torn and faded print in a glass frame. A breath of motion starts at 1.2 s. | ⚑ Jawad's own photo, with the family's consent; disclose "AI se animate kiya". |
| 29 | G | comment prompt | "Bachpan ki ek yaad wapas la sakte, toh kaunsi laate?" | *bachpan* / KI EK YAAD | Memory fragments (a cassette, a Nokia, a gali-cricket ball) float in ember dust. | ⚑ Only promise what he will actually make. |
| **30 ★** | G E | universal pain | "Chai thandi ho gayi. Render abhi bhi ninety-nine pe hai." | CHAI THANDI / RENDER / *99%* | A 3D chai glass with its steam fading, next to a progress bar frozen at 99 %. | — |
| 31 | G | universal meme | "Duniya ka sabse bada jhoot: 'Estimated time: 2 minutes'." | ESTIMATED TIME: ↑ / *2 minutes* | The time counter goes *up* while the bar goes down. | — |
| 32 | G E | cricket analogy (neutral) | "Last over, chhe ball, barah run — aur editor ki deadline. Dil dono mein ek jaisa dhadakta hai." | LAST OVER / = *deadline* | A scoreboard UI morphs into a render queue. No teams and no flags. | — |
| 33 | C E | topical debate | "Kya AI editors ki job kha jayega? Pehle ye dekh lo." | KYA AI / *editor* / KHA JAYEGA? | An AI chat box types a prompt. Jawad's hand drags its output onto a timeline and fixes it. | Keep it balanced, not anti-AI. |
| 34 | G C | underdog story | "Ek laptop. Ek kamra. Aur ek sapna jo ghar mein kisi ko samajh nahi aaya." | EK LAPTOP / EK KAMRA / *ek sapna* | A single desk lamp in a dark room; a laptop glow lights the dust. | ⚑ True story |
| 35 | G E | underdog / proof | "Mujhe bola gaya tha, 'ye toh koi bhi kar leta hai'." | KOI BHI / *kar leta hai?* ↑ | A finished shot explodes into its 30 layers: the complexity is the answer. | ⚑ True story |
| 36 | E C | teach-by-doing | "Ye ek cut dekho. Isi cut ki wajah se tum abhi tak ruke ho." | YE CUT / *dekha?* | A match cut happens *at* 0.6 s and is replayed with a glowing marker. | — |
| 37 | C E | caption-glitch interrupt | "Ruko, ye text galat jagah pe hai." | YE TEXT / *galat jagah* / PE HAI | The caption starts deliberately under the like/share column, then snaps into the safe zone along keyframes. | The misplaced state lasts ≤ 0.4 s. |
| 38 | G C | POV | "POV: tumne editor ko bola 'bas cinematic bana do'." | POV: / *cinematic* / BANA DO | A plain phone clip escalates into lens flares, a 3D logo and slow-mo in 2 s. | — |
| 39 | E F | in-group code + send | "Ye reel sirf editors samjhenge. Baaki log… maaf karna." | SIRF EDITORS / *samjhenge* | Insider glyphs flash by: J-K-L keys, red "media offline" frames, a ripple-delete. | — |
| 40 | G B | concession + reveal | "Mobile pe bhi toh edit ho jata hai — haan, ho jata hai. Ab ye dekho." | MOBILE PE BHI / *ho jata hai* | A phone UI edit, then the camera pulls back through the phone into a full 3D scene. | — |

### 2.7 Top 10: why they rank, and the A/B plan

Each hook is scored 1-5 on six criteria:
- **Stop:** frame-0 stopping power.
- **Breadth:** pan-desi reach beyond editors.
- **Niche:** fit with Jawad's editor/motion brand.
- **Send:** send potential.
- **Build:** buildable locally in the toolkit on CPU.
- **Loop:** loopability.

[Inference]

| rank | # | stop | breadth | niche | send | build | loop | total | why |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 chhota sa change | 4 | 5 | 5 | 5 | 5 | 5 | 29 | Universal client/boss pain; the perfect sentence loop (the ending "…aur phir client ne bola—" restarts it). |
| 2 | 2 shaadi ki video? | 4 | 5 | 5 | 5 | 4 | 3 | 26 | Every desi editor has lived this; non-editors laugh and send it to siblings. |
| 3 | 30 chai + 99 % | 5 | 5 | 4 | 4 | 5 | 4 | 27 | Simplest, most visual pain; the 3D chai glass is a desi icon. |
| 4 | 6 light chali gayi | 5 | 5 | 4 | 4 | 5 | 3 | 26 | A blackout is the strongest possible pattern interrupt, and pan-desi. |
| 5 | 9 pehla second | 4 | 3 | 5 | 4 | 5 | 4 | 25 | A value reel that proves its own point; draws saves and creator sends. |
| 6 | 17 free mein kar do na | 3 | 5 | 4 | 5 | 5 | 3 | 25 | A built-in indirect-message send ("bhejo usi dost ko"). |
| 7 | 21 video sasta | 4 | 3 | 5 | 4 | 4 | 3 | 23 | Speaks to paying clients (business owners); lead generation. |
| 8 | 28 purani photo | 4 | 5 | 4 | 5 | 3 | 3 | 24 | Jawad's AI-video strength; family and nostalgia sends. Needs consent. |
| 9 | 10 kaunsa? | 4 | 3 | 5 | 3 | 5 | 4 | 24 | A binary comment trigger (L/R); a craft showcase. |
| 10 | 7 khud ko edit | 5 | 3 | 5 | 3 | 4 | 5 | 25 | A meta pattern interrupt that is pure Jawad; loops naturally. |

Honourable mentions: #26 ghar wale, #38 POV cinematic, #33 AI vs editor, #20 Seen horror.

**Suggested hook pairs for the 5 reels.** This is a suggestion only; the creative director decides. Each reel uses a different mechanism, and B differs from A in the first 3 s only.

| reel angle | A (main) | B (Trial Reel) | mechanism family |
|---|---|---|---|
| Client revisions (loop reel) | #1 | #20 | pain + open loop |
| Desi family / identity | #2 | #26 | dialogue scene |
| AI nostalgia / yaadein | #28 | #29 | transformation |
| Creator lesson ("the first second") | #9 | #7 | contradiction vs meta interrupt |
| Business owners | #21 | #22 | contrast vs visual gag |
| *(spare)* universal pain | #30 | #6 | universal pain vs blackout |

**How to run the A/B test:**
- Post A publicly. Post B as a **Trial Reel** (non-followers only) within 24 h.
- After 72 h compare **skip rate first**, then sends per reach, then the retention curve.
- If B wins clearly, consider making B the next reel's opening pattern.
- Toolkit: keep `DUR` identical. Render only the hook range for the variant (`render.py reelN --range 0 3.2`) and concat it onto the master body. Make sure the cut lands on a frame where both versions share the same picture.

---

## 3. Retention architecture (30-40 s)

### 3.1 Beat map template (34 s example, 30 fps; scale proportionally for 30-40 s)

| t (s) | % | beat | what happens | micro-hook type | VO words |
|---|---|---|---|---|---|
| 0.0-1.5 | 0-4 | **HOOK** | 3-layer hook (§2.1) | visual + text + voice | 4-6 |
| 1.5-4.0 | 4-12 | **STAKES / LOOP OPEN** | Why it matters, plus a promise: "Dekho kya hua", "teen cheezein, teesri sabse zaroori". | verbal open loop | 7-9 |
| 4-8 | 12-24 | **BEAT 1** | Context or the first point. A new visual world (camera orbit, new 3D set). | visual change at ~6 s | 10-12 |
| 8-12 | 24-35 | **BEAT 2 + re-hook** | Turn: "Lekin…" or "Aur yahin galti hoti hai". | verbal turn at ~10.5 s | 10-12 |
| 12-16.5 | 35-48 | **BEAT 3 / escalation** | Stakes rise (a bigger number, a worse client, a darker world). | sonic hit at ~14 s | 10-12 |
| **16.5-17.2** | **48-50** | **MIDPOINT PATTERN BREAK** | 0.3-0.5 s of VO silence, then a flash or whip, a scale break (macro to wide), or a palette dip to near-black with the ember only. | all three | 0 |
| 17.2-24 | 50-70 | **BUILD** | Last step before the payoff. A riser under it (`riser`, duration = time to payoff). | visual every 2 s | 16-18 |
| **24-28** | **70-82** | **PAYOFF** | The biggest 3D or motion moment: the hero keyword with underline and light sweep. The answer is said plainly. | the release | 8-10 |
| 28-31.5 | 82-93 | **BONUS + CTA** | One extra twist or a warm line, then **one** CTA (spoken ≤ 2 s plus a pill). | — | 6-8 |
| 31.5-34 | 93-100 | **LOOP BRIDGE** | The VO half-sentence that completes line 1. Visuals glide back to the frame-0 composition. The @jawad_mp4 signature stays small. | the loop | 3-5 |

**VO budget:**
- The Hindi TTS rate is about 2.6-3.0 words/s [Inference]. The references measured 2.97 and 3.36 words/s.
- A 34 s reel with about 3 s of VO-free beats leaves about **80-90 words**. For 30 s plan 70-80 words; for 40 s plan 95-110.
- Measure the TTS output and re-time the beats to the real word timings, not the other way round.

### 3.2 Micro-hooks and re-hooks

- **Cadence rule:** within any 3 s window there is at least one new event: visual (cut, camera move, new element), verbal (turn word), sonic (SFX hit) or textual (keyword slam). Nothing is static for more than 2.0 s.
- **Verbal re-hook bank** (pan-desi, use 2-3 per reel, never the same one twice in a set):
  - "Lekin asli game yahan hai."
  - "Aur yahin sab galti karte hain."
  - "Ab dhyaan se dekho."
  - "Ruko, ek cheez aur."
  - "Sach bataun?"
  - "Yahan se kahani palti."
  - "Teesri wali sabse zaroori hai."
  - "Ab woh part jo koi nahi batata."

  Use the last one sparingly; it is overused.
- **Visual re-hooks native to Jawad:** a razor cut on the beat, a timeline zoom-out, a "render" reveal, a 3D prop breaking the frame, an ember particle burst, a focus pull (aperture 20 to 60), the error pop-up device.
- **Never** stack a verbal turn, a big SFX and a scene change on every beat. Alternate them so each one stays noticeable.

### 3.3 Seamless loops: four kinds, ideally combined

1. **Sentence loop.** The last VO line is an unfinished clause that the first line completes.
   - Ending: "…aur tab client ne bola—"
   - Restart: "Bas ek chhota sa change."

   Keep the ending pitch rising, with no final cadence. Trim the TTS tail so there is **no** breath or pause after the last word: cut at the word end + 40 ms.
2. **Visual match loop.**
   - Frame DUR−1/30 and frame 0 share their composition: the same object in the same screen position and scale, with only a lighting or state difference.
   - In the toolkit, `draw(t)` is pure, so make the camera `K.Track` end on the pose it had at t = −0.4 s (the pre-roll pose), and move the hero element back to its frame-0 position over the last 1.5 s.
   - Check it by rendering `--stills 0,<DUR-0.033>` and flipping between them.
3. **Audio loop.**
   - Never fade the audio to silence.
   - End on a `reverse_swell` or `riser` whose end is exactly DUR. Its release is then the frame-0 transient (`impact_soft` or `glitch_short` cued at t = 0.0).
   - Music, if any, ends on a bar line, with the downbeat being frame 0.
4. **Story loop.** The ending reframes the beginning, so a second watch means more. Example: the "client" at the end is revealed to be Jawad's younger self.

**Avoid:** a black end card, a "follow for more" freeze, or a logo sting with a fade. The signature `@jawad_mp4` lives as a small grotesk line on top of the action (as on the prior covers), not on a separate end card.

### 3.4 Payoff timing

- Deliver the promised answer at **65-80 %** of the running time. Viewers who stay that long are rewarded, and the remaining 20 % holds the bonus beat and the loop.
- An open loop must be closed before 80 %. Unpaid curiosity reads as bait and kills shares.
- **Two payoffs beat one:** the main payoff (information or emotion) plus a smaller bonus (a joke, a twist, an Easter egg) just before the loop. The bonus makes viewers send it ("end wala dekh").

### 3.5 CTA placement

- **One CTA per reel**, spoken at 82-93 % of the running time and shown as a verb-first pill of ≤ 5 words (`T.render(..., 'glass_pill')` restyled in the ember tokens, or `ui.button`). The pill sits at y ≤ 1480; nothing textual below y 1620.
- **A mid-roll soft CTA** ("save kar lo, kaam aayega") only on value or list reels, at 55-65 %, and never alongside the end CTA's ask.
- The CTA's job differs by reel type:

  | reel type | CTA |
  |---|---|
  | relatable humour | **send** |
  | value | **save** or a **keyword comment** |
  | nostalgia | **comment a memory** |
  | business | **keyword comment for DM** |
  | craft showcase | **comment a guess** |

### 3.6 Comment triggers

| trigger | example line (Hinglish) | best reel | note |
|---|---|---|---|
| **A or B** (lowest effort) | "Left wala ya right wala? Comment mein bas L ya R." | #10 comparison | One-letter comments get the most replies. |
| **Count / find** | "Is reel mein kitne cuts hain? Sahi jawab pinned comment mein." | #3 | ⚑ It must be true; pin the answer after 24 h. |
| **Hidden frame** | "Ek frame mein maine kuch chhupaya hai. Mila?" | any (loops) | Hide a single-frame Easter egg (e.g. a tiny ember "JK" glyph). Drives rewatches. ⚑ It must exist. |
| **Fill the blank** | "Tumhare client ne kya bola tha? 'Bas ek ______'" | #1 | Pin the funniest reply; this brings stories and a community feel. |
| **Number confession** | "Tumhara sabse lamba render kitne ghante ka tha?" | #30 | Easy to answer, competitive. |
| **Memory prompt** | "Apni ek bachpan ki yaad comment karo. Best wali next reel mein." | #29 | ⚑ Only promise what he will make. Never use other people's photos without consent. |
| **Team debate** (friendly) | "Mobile editing ya laptop editing — team batao." | #40 | Keep it craft-only, never national. |
| **Keyword for a resource** (DM automation) | "Comment **EMBER** — glow wala preset main DM kar dunga." | value / BTS | See the rules below. |

**Keyword-to-DM rules** [Meta] + [Inference]:
- **Pick one distinctive uppercase keyword per reel**: EMBER, HOOK, LOOP, GRADE, BRAND. Avoid YES, ME, LINK or HI, which fire on ordinary replies.
- The deliverable must **exist and be free**: a preset, a checklist PDF, a hook list, a 3-idea brief.
- **The first DM is the only automatic message** (one private reply within 7 days). It must contain the deliverable or its link, plus one question that invites a reply. That reply is what opens the 24 h window for follow-ups.
- Write the first DM in the same voice, for example: "Ye lo tumhara EMBER preset 🔥 [link]. Tum zyada reels banate ho ya client work?"
- Don't use message tags to send promos after the window closes.
- Mention in the caption that the DM may land in **Requests** for non-followers: "DM Requests check karna".

### 3.7 Share triggers: why desi viewers send a reel

A send is a social act: the viewer uses the reel as their message. Design the send line first. [Inference, grounded in sharing research: social-interaction motives drive video sharing ([UNIR](https://reunir.unir.net/handle/123456789/1763)) and self-enhancement ([Frontiers 2022](https://doaj.org/article/2c5ae278affb43e6883a4baf18afb157)); see also Berger's STEPPS model (social currency, emotion, practical value).]

| # | send driver | what the send says | example line / reel |
|---|---|---|---|
| 1 | **"Ye tu hai"** (identity mirror) | "This is literally you." | #5 3 a.m. render, #4 final_v7 |
| 2 | **Indirect message** (the strongest desi driver) | Says what you can't say to a client, boss, rishtedaar or parent. | #17 "usi dost ko bhejo", #1 "client ko bhejo, shayad samajh jaye", #26 to the family |
| 3 | **Shared nostalgia** | "Remember this?" to siblings and school friends. | #28, #29 (Nokia, gali cricket, nani ka ghar) |
| 4 | **In-group code** | "Only we get this." | #39 sirf editors samjhenge |
| 5 | **Practical value** | "This will help you." | #9 pehla second, #19 3 cheezein |
| 6 | **Pride / awe** | "Look what one of us made." | Craft BTS ("ye sab ek laptop pe bana") ⚑ verify the claim |
| 7 | **Aspiration / support** | "Tere liye, don't give up." | #34 ek sapna, #35 koi bhi kar leta hai |
| 8 | **Laugh together** | "Haha, look." | #2 shaadi ki video, #38 POV cinematic |

**Rule:** say the send instruction only once, naming a specific person ("us dost ko", "apne client ko", "bhai/behen ko"). "Share karo" alone does nothing.

### 3.8 Retention killers (QA checklist)

- [ ] A logo, intro card, greeting or "doston" before the hook.
- [ ] Frame 0 is dark, blank, faded or static.
- [ ] The first VO word comes later than 0.1 s.
- [ ] Hook text appears later than 0.5 s, or has more than 5 words.
- [ ] The answer comes in the first 5 s with nothing left to want.
- [ ] Anything holds static for more than 2 s; there is a 3 s window without an event.
- [ ] More than 2 text blocks on screen; text covers most of the frame.
- [ ] Captions sit under the like/share column or the bottom UI.
- [ ] The CTA comes before the payoff, or there are several CTAs.
- [ ] It ends on black or fades to silence (this kills the loop).
- [ ] Music masks the VO. Mix the VO about 8-10 LU above the bed.
- [ ] An unverified claim, number or personal story.

---

## 4. On-screen kinetic captions

### 4.1 Two caption layers, never doubled

| layer | what | built with | rule |
|---|---|---|---|
| **Designed headlines** | Hook text, keywords, chapter lines, the payoff word, the CTA | The reel module (`type3d`, `ui`, `core`), as part of the motion design | 1-5 words, one ember keyword, upper or middle band |
| **VO subtitles** | A transcript of the voice-over, word-synced | The trending-captions pipeline for words, phrases and the SRT; the burn route is described in §4.7 | 1-3 words per phrase, lower-middle band, moved per shot |

Where a headline already shows the words being spoken, **delete those words from the subtitle JSON** for that window (caption-designer rule).

### 4.2 Where caption style stands (Oct 2026)

- Word-by-word, 1-3 words at a time, synced to speech, is the baseline. Static sentence blocks read as dated.
- **"Dynamic minimalism"** is rising: heavy font, word timing, one accent, a subtle scale or fade, no SFX on every word.
- The full "Hormozi" package (yellow highlight, all caps, a whoosh per word, emoji) is saturated.
- Pills and chips are rising.
- Avoid per-word shake, neon green or electric blue, and lines in 3+ colours.
- Sources: the reels-studio trending-captions SKILL notes (checked 2026-10-08) and [opus.pro 2026](https://www.opus.pro/blog/editing-aesthetics-dominating-short-form-2026).
- **Jawad's angle:** the editorial serif-italic + sans pairing is what premium cinematic creators use (ref2 and ref3 both do it [Measured]). Jawad's **ember glow + underline** on that pairing is a recognisable signature in his feed. Keep it as the baseline. Then give each reel **one** signature caption device from §4.8 for 1-3 moments, not the whole reel, so legibility never suffers.

### 4.3 House style "EMBER TYPE": spec

**Colour tokens.** Measured from his prior covers (median pixel colours) [Measured]. They are new tokens: do not reuse the toolkit's 'amber' look; build a custom `ui.Look('ember', …)` and pass hex colours to `type3d`.

| token | hex | measured from | use |
|---|---|---|---|
| `EMBER` | **#F6591D** | keyword cores, "yaadein" cover (p25 #E64B03 to p75 #FD6465) | Keyword fill, bottom of its gradient |
| `EMBER_HOT` | **#FF9A3C** | the lighter keyword core, "you're better" cover (p75 #F6912B) | Keyword fill, top of its gradient; light sweep |
| `FLAME_RED` | **#E2361C** | the glow transition (inferred between core and halo) | Inner glow; underline glow |
| `EMBER_DEEP` | **#7F2212** | glow halo, median of 2 covers (#7F2212, #822A19) | Outer halo, shadows, the scrim tint |
| `WARM_WHITE` | **#F5EFE8** | grotesk words (not pure white) | Grotesk text |
| `VOID` | **#0A0605** | darkest background, median #020103-#201107 | Background base |
| `SMOKE` | **#201107** | warm lifted blacks (OpenArt cover) | Background lift, glass tint |

- **Contrast:** EMBER on VOID ≈ 6:1 (passes 4.5:1). Over footage, add `scrim=0.75-0.85` (`deep_glow`-style backing) or a `EMBER_DEEP` soft box.
- **Faces:** keep `FLAME_RED` for glows only, never as a text fill over skin (pure red vibrates against skin).

**Typography and layout:**
- **Keyword:** Playfair Display **Bold Italic** (700). It matched the "yaadein" and "younger self" letterforms best in a side-by-side test [Measured]: high contrast, ball terminals, readable glow.
  - Fill: gradient `('#FF9A3C', '#F6591D')` at angle −90 (top to bottom).
  - Glow: 3 radii, about 0.05 / 0.15 / 0.35 em, weights 0.9 / 0.8 / 0.6, colour `FLAME_RED` × 1.6-2.2.
  - A thin `EMBER_HOT` light sweep on landing.
- **Grotesk words:** Poppins **SemiBold** (captions) or **Bold** (headlines), WARM_WHITE, with a faint warm glow (0.15 em, `EMBER_DEEP`). Poppins matches the house "KUCH / MEETING MY / MY ENTRY" forms.
- **Size ratio:** keyword ≈ **1.6-2.0× the grotesk cap height**, matching the covers. Headlines: grotesk 80-96 px, keyword 150-200 px. Subtitles: grotesk 72-84 px, keyword 110-130 px.
- **Underline:**
  - A hand-drawn-feeling stroke, slightly tapered at both ends and 3-5 % off horizontal, like the covers.
  - Core `EMBER_HOT` with 2 px of near-white at its centre, glow `FLAME_RED`.
  - It draws on left to right in 0.25-0.35 s ('out_cubic') right after the keyword lands.
  - Use it **max 3 times per reel** (hook, payoff, CTA or signature).
  - Build: `ui.parse_path` / `ui.trim_polyline` + `ui.stroke_mask` + `K.glow`.
- **Italic overhang spacing [Measured]:** the italic keyword's swash runs into the next upright word (in the test sheet "yaadein NAHI" collided at normal spacing). Rules:
  - add **0.25 em of the grotesk size after** an italic keyword, and 0.12 em before it;
  - or put the keyword on its own line, which is the house default;
  - baseline-align mixed lines (`anchor='baseline'`), not centre-align.
- **Case:**
  - Roman Urdu body words in **lowercase or sentence case**. Roman Urdu spelling isn't standardised, so readers rely on word shapes, and long all-caps Roman Urdu reads slowly [Inference].
  - Caps only for short grotesk labels of 1-2 words (KUCH, BETA, RUKO, LOGO), as on the covers.
- **Signature:** `@jawad_mp4` in Poppins Medium, 30-34 px, WARM_WHITE at 70 %, under the final underline, inside y ≤ 1480.

### 4.4 Fonts (all free on Google Fonts, verified available 2026-10-08)

The "em/char" figures are average advance width per character on a Roman Urdu corpus [Measured with Pillow].

| role | font | em/char (mixed / CAPS) | why |
|---|---|---|---|
| **Keyword (primary)** | **Playfair Display Bold Italic** (700) | 0.460 / 0.604 | Closest to the house keyword; ball terminals hold the glow. |
| Keyword (tight fit) | DM Serif Display Italic | 0.435 / 0.532 | About 5 % narrower and softer. Use it when a keyword is too wide. |
| Keyword (quiet / elegant) | Instrument Serif Italic | 0.367 / 0.413 | The narrowest, but strokes are thin, so the glow washes them out. Use only at ≥ 180 px or for no-glow "minimal" moments. |
| Avoid for keywords | Fraunces Black Italic, Bodoni Moda Bold Italic | — | Fraunces is too blobby; Bodoni's hairlines break up under glow and compression. |
| **Grotesk (primary)** | **Poppins SemiBold / Bold** | 0.525 / 0.576 (SemiBold) | Matches the house words; large x-height (0.55 em) reads well for Roman Urdu. |
| Grotesk (tighter, modern) | Inter Tight ExtraBold | 0.471 / 0.573 | About 10 % more characters per line in mixed case. |
| Grotesk (personality) | Bricolage Grotesque ExtraBold | 0.502 / 0.585 | For playful reels (#2, #38). |
| Condensed slam (rare) | Anton | 0.414 / 0.417 | Single-word slams only. Don't use it for Roman Urdu sentences. |
| Mono (timecodes, UI, file names) | JetBrains Mono Bold (or Geist Mono) | 0.600 | NLE-authentic: timecodes, `final_v7.mp4`, render percentages. |
| Handwriting (clapperboard chalk) | Kalam Bold (by the Indian Type Foundry) or Caveat Bold | — | Kalam has a desi handwritten feel. |

- Roman Urdu mixed case runs about 3-4 % wider per character than English in the same fonts [Measured: Poppins SemiBold 0.525 vs 0.507].
- **Install:** download the TTFs into `<WS>/fonts` (the toolkit and libass both read it). Pass them to `type3d` as TTF basenames, e.g. `font='PlayfairDisplay-BoldItalic'`, or map aliases in project.json `font_map`.

### 4.5 Safe zones and measured line limits

```
1080 x 1920
y    0-230   top UI (status, "Reels", audio)         -> no copy
y  230-1000  UPPER BAND: hooks, headlines, keywords  -> full 940 px (x 70-1010)
y 1000-1050  buffer
y 1050-1480  LOWER BAND: VO subtitles, CTA pill      -> 780 px, right edge <= x 930 (like/share column)
y 1480-1620  CTA pill may reach y 1600 (script-hook-writer rule); nothing else textual
y 1620-1920  bottom 300 px: caption, handle, audio   -> nothing textual, nothing important
Cover-crop safe (3:4 grid and 4:5 feed): y 285-1635.  Strictest (1:1): y 420-1500.
```

**Measured characters per line**, including spaces, Roman Urdu [Measured]. Glows, extrusions and pills add width beyond these; keep 40-60 px spare.

| font @ px | mixed case, 940 / 780 px | CAPS, 940 / 780 px |
|---|---|---|
| Poppins SemiBold @ 64 | 27 / 23 | 25 / 21 |
| Poppins SemiBold @ 80 | 22 / 18 | 20 / 16 |
| Poppins SemiBold @ 96 | 18 / 15 | 17 / 14 |
| Poppins Bold @ 130 | 13 / 11 | 12 / 10 |
| Inter Tight ExtraBold @ 80 | 24 / 20 | 20 / 17 |
| Playfair Display Bold Italic @ 130 | 15 / 13 | 11 / 9 |
| Playfair Display Bold Italic @ 160 | 12 / 10 | 9 / 8 |
| Playfair Display Bold Italic @ 200 | 10 / 8 | 7 / 6 |
| DM Serif Display Italic @ 160 | 13 / 11 | 11 / 9 |

Spot checks at 96 px Poppins Bold caps:
- "BETA KYA KARTE HO?" = 1012 px: it overflows, so it must break into 2 lines.
- "TUMHARA CONTENT" = 965 px: it overflows.
- At 200 px Playfair Black Italic, "chhota sa" = 891 px: it fits the upper band only.

**Words and lines:**
- VO subtitles: **1-3 words per phrase, max 2 lines, max 16 characters per line** at 80 px in the lower band.
- Headlines: **≤ 5 words**, 2-3 lines, one keyword of ≤ 10 characters.
- Break at phrase boundaries; never leave a lone short word ("ka", "hai", "to") at a line end.

### 4.6 Timing rules

- **VO-synced subtitles:**
  - A phrase appears 0.05 s before its first word (`--lead 0.05`) and holds 0.35 s after its last word.
  - A pause longer than 0.45 s starts a new phrase.
  - The swap to the next phrase is instant: the new phrase's pop is the transition.
  - An exit into silence eases out over about 110 ms.
  - The highlight changes on frame round((word.start − 0.05) × 30) ± 1.
- **Designed headlines** (no VO, or reinforcing it):
  - Settled hold ≥ words / 3 s, and ≥ 0.8 s per sentence.
  - For Roman Urdu, add +0.3 s to holds longer than 3 words [Inference: non-standard spelling decodes more slowly].
  - Single-word slams: 0.4-0.5 s each, building one phrase; the completed phrase then follows the hold rule.
- **Entrances:**
  - Grotesk: `Glyphs.rise` (dur 0.25-0.35, dist 0.25-0.45, blur 6-10, stagger 0.02-0.03).
  - Keyword: `Glyphs.slam` (s0 1.3-1.5, dur 0.4) or `wipe` (angle 0, soft 0.12, edge 1.0) with the light sweep.
  - Use **one** entrance family per reel.
- **Fades:** always pass an ease to `K.ramp` ('inout_sine' or 'linear' for fades, 'in_cubic' for exits). The default 'out_expo' makes ghost frames.
- **Sound:** no SFX on every word. Keywords get a soft hit at most (`shimmer` or `impact_soft`, −3 dB), and at most 3 caption SFX per reel.

### 4.7 How to burn the house style

The trending-captions script `make_captions.py` (v. in repo) has **one font per style** plus a colour highlight. It has **no per-word font switch**, so it cannot do "white Poppins + Playfair Italic keyword" natively [Measured by reading its CLI]. Two routes:

- **Route A (recommended for these reels): render subtitles in the toolkit.**
  1. Use `make_captions.py` to get the corrected `words.json`, the phrase chunks (`<module>.captions.json`) and the **SRT deliverable**.
  2. Load the chunks in the reel module (`lru_cache`d) and draw each phrase with `type3d`: grotesk words via `T.render(word, 'flat', font='Poppins-SemiBold', px=80, fill='#F5EFE8', glow=…)`, the keyword via `T.render(..., font='PlayfairDisplay-BoldItalic', fill=('#FF9A3C', '#F6591D'), fill_angle=-90, glow_color=('#E2361C', 2.0))`.
  3. Draw them in the reel's `draw(t)`. This gives linear-light glow, DOF and motion blur, consistent with the headlines.
  4. QA with the caption-designer's ink scan on a grey-background render.
- **Route B (quick talking-head cuts): patch `make_captions.py`.**
  1. Have the motion-toolkit-engineer add `--emph-font` (and `--emph-italic`), writing inline ASS overrides `{\fnPlayfair Display\i1\c&H…&}word{\r}`.
  2. Approximate the glow with a duplicate layer underneath: `\bord6\blur8\3c` in EMBER_DEEP.
  3. Measure emphasis widths with the emphasis font in the layout pass, or the safe-zone check will be wrong.
- **Hinglish transcription gotcha:**
  - faster-whisper with `--language hi` returns **Devanagari**.
  - `--language en` mangles Hindi words.
  - Because the VO is generated from a known script, take word timings from `--language hi` and **map them 1:1 onto the Roman script tokens**, after checking the counts match.
  - Or write `words.json` from the TTS engine's own timestamps if it provides them.
  - Then follow the caption-designer's correction rules (names, numbers, deleting doubled words).

### 4.8 Ten original caption devices for an editor's brand

These are ten devices built for this brief, each showing the editor's craft inside the caption itself. They come with toolkit build notes. "Never done before" can't be proven; in this research pass I found none of them as a packaged caption style (trend reports list word-pop, karaoke, pills, typewriter). Run one more search before claiming novelty in public copy.

#### 1. RAZOR TIMELINE CAPTIONS (subtitles are clips that get cut)
- **Look:**
  - The VO words are **clip blocks on a 3D NLE timeline** lying in perspective below the subject. Word clips are warm grey; the keyword clip has the ember gradient.
  - A glowing ember **playhead** stays fixed at x 540 while the track scrolls.
  - When the playhead reaches a word, the clip **lifts out of the track** and stands up as the readable caption.
  - On the keyword, a **razor cursor slices** the clip and the keyword flies up in serif italic.
  - Filler words are **ripple-deleted**: the block collapses and later clips slide left.
- **Why:** every subtitle shows the editing process. Editors recognise it instantly (#39 in-group); non-editors see "the video is editing itself" (#7).
- **Build:**
  - Lanes are a static `ui.Surf(1000, 260)` sprite: `.rrect` lanes V1 and A1, clip blocks via `.rrect_grad`, and a small waveform drawn into the A1 clips. Clip labels in `ui.put_text` JetBrains Mono 28 px are decoration only.
  - Lay the lanes as a floor: `K.draw_plane(cv, lanes, cam, (x_scroll, 420, 0), 1100, rot=(-62, 0, 0))`. A negative rx tips the top edge away from the camera. `x_scroll = -(t - t_ref) * 260`.
  - The lifted word: `T.Glyphs(word, 'flat', font='Poppins-SemiBold', px=80, fill='#F5EFE8').rise(cv, t, 540, 1180, t0=w['start']-0.05, dist=0.6, dur=0.25)`.
  - The keyword: `T.Glyphs(kw, 'flat', font='PlayfairDisplay-BoldItalic', px=120, fill=('#FF9A3C', '#F6591D'), fill_angle=-90, glow=…, glow_color=('#E2361C', 2.0)).slam(...)`.
  - The razor cursor is an SVG blade via `ui.parse_path` + `ui.fill_mask`, moved with `K.Track`, with a click `K.impulse`. The split is the clip sprite drawn as two halves whose gap opens 0–8 px over 0.12 s, plus a small spark from a `K.Particles` burst.
  - Ripple-delete: the block's x-scale goes to 0 ('in_cubic', 0.15 s), and later clips follow a `K.Track`.
- **SFX:** `ui_tick` on every 2nd clip passing (−12 dB), `ui_click` + `glitch_short` for the razor, `card_slide` for the ripple close.
- **Cost:** a static sprite, plus one plane and 1-2 type draws per frame (about 60-120 ms).
- **Safe zone:** lifted words at y 1100-1260 and ≤ 780 px; the timeline floor (decoration) at y 1300-1480 inside x 70-930.
- **Best in:** reels #1, #7, #39.

#### 2. KEYFRAME-GRAPH CAPTIONS (the keyword obeys its own speed graph)
- **Look:**
  - When the keyword arrives, a glass **graph-editor panel** fades in behind it: grid, axes, two keyframe diamonds.
  - The bezier **curve draws on**, and the word's scale and position follow the curve live.
  - **Gag version:** pass 1 is *linear*, so the word moves robotically and gets a red ✕ chip. A cursor drags the bezier handle, pass 2 is *eased* (out_back), and the word glides in with a ✓.
- **Why:** it teaches easing in 2 s and flexes motion craft, which suits value reels (#9, #36).
- **Build:**
  - Panel: `ui.glass_card(820, 480, r=36, look=EMBER_LOOK)`.
  - Grid lines on a `ui.Surf`.
  - Curve: points from `K.EASE['out_back']` (or a cubic bezier), revealed with `ui.trim_polyline(pts, 0, u)`, then `ui.stroke_mask(width=6)` tinted `EMBER` + `K.glow`.
  - Keyframe diamonds: `K.rrect_alpha(22, 22, 4)` drawn with `rot=45`.
  - Word: `ts.draw(cv, x(u), y, scale=lerp(0.6, 1, curve(u)))`, with `samples(t)=5` during the move.
  - Cursor: `ui.draw_cursor(..., 'arrow', press=K.impulse(t, tc, 9))`.
- **SFX:** `ui_click` (grab), `slider_drag` (align='start', duration = the drag), `whoosh_fast` on the eased pass.
- **Cost:** low.
- **Safe zone:** the panel inside x 130-950 and y 420-980 (upper band); keyword ≤ 160 px.

#### 3. RENDER-BAR CAPTIONS (the house underline is a render progress bar)
- **Look:**
  - The glowing ember **underline is a progress bar** that fills left to right as the phrase is spoken.
  - Letters ahead of the bar are a dim, **blocky low-res ghost**. At the bar's leading edge they resolve through **Cycles-style render buckets** (small white tile outlines) into sharp glowing type.
  - A tiny mono `%` counter rides the bar end.
  - **Gag:** the bar **stalls at 99 %** (hook #30), shakes, then completes on the payoff.
- **Why:** the brand's signature underline becomes functional and makes "rendering" a visual metaphor; non-editors still read it as loading or suspense.
- **Build:**
  - `ts = T.render(phrase, …)`. Cache `sharp = ts.sprite` and `ghost = cv2.resize(cv2.resize(sharp, (w//14, h//14), interpolation=cv2.INTER_AREA), (w, h), interpolation=cv2.INTER_NEAREST) * 0.3` once.
  - Per frame, composite column ranges: `[0, bx)` sharp, `[bx, bx+48)` the bucket band (sharp × a checker mask with 1 px tile outlines), `[bx+48, w)` ghost. Draw with `K.draw` at the sprite anchor (`ts.sprite_anchor`).
  - Bar: `K.rrect_alpha(int(w*p), 6, 3)` tinted `('#FF9A3C', 2.4)` + `K.glow(..., K.hexlin('#E2361C'), (4, 14, 40), 1.2)`.
  - Counter: `T.Counter('flat', px=34, suffix='%', decimals=0, font='JetBrainsMono-Bold')`.
  - Progress p = speech progress through the phrase (word timings).
- **SFX:** `ui_tick` per 25 % (−14 dB), `check_ding` at 100 %, `glitch_short` + `K.impulse` shake on the 99 % stall.
- **Cost:** low (numpy slicing).
- **Safe zone:** standard subtitle band; the bar is included in the width budget.

#### 4. CLAPPERBOARD CHAPTERS (re-hooks on a 3D slate)
- **Look:**
  - At each chapter break (the 3-4 re-hooks) a **Blender clapperboard** swings in.
  - Its sticks carry **ember-and-black stripes**, a brand twist on the usual black and white.
  - The chalk face holds `SCENE 02 · TAKE 7` plus the re-hook line in handwriting ("Take 7: client ka 'bas ek change'").
  - The **clap is the transition**: the sticks snap shut on the beat, a flash, then a whip to the next scene.
- **Why:** each chapter feels like a new "take", which is a natural micro-hook every 6-9 s.
- **Build:**
  - The blender-3d-artist builds a new prop module in the project pipeline (the `assets3d_*` pattern; Cycles on CPU, about 64 samples + OIDN, 720 px, `nice -n 10`, 2 threads).
  - Variants: `night` (yaw 49) and `clap` (anim 18 frames, last frame closed).
  - Export **features** for the 4 corners of the chalk area.
  - Text: `T.render(line, 'flat', font='Kalam-Bold', px=64, fill='#F5EFE8')`, with grain via a noise multiply on a copy. Warp it onto the slate with `ts.draw_quad(cv, quad)`, where the quad is the projected feature corners.
  - Clap: at `t_clap`, the next frame of the `clap` sequence, `K.post(..., flash=0.35*K.impulse(t, t_clap))`, `K.whip_blur`.
- **SFX:** a custom clap (`impact_soft` layered with `camera_shutter`, high-passed; the sound-designer makes it), then `whip`.
- **Cost:** Blender pre-render about 67 frames once; per frame it's cheap.
- **Safe zone:** slate text ≥ 56 px after perspective; chalk lines ≤ 4 words.

#### 5. COLLISION CAPTIONS (words with physics, meeting a Blender prop)
- **Look:**
  - The white grotesk words **fall and collide** with a hero Blender prop (a 3D chai glass for #30, a hard drive for #6, a big glossy "RENDER" key), tumble and pile up.
  - The **serif keyword drops last**, lands upright on top and glows.
  - **Variant:** the prop rolls through a settled sentence, knocking out every word except the keyword ("the only word that matters").
- **Why:** physical comedy; it combines 3D and typography in a way that's hard to copy with CapCut templates.
- **Build:**
  - **Deterministic physics precomputed once:** a tiny numpy impulse solver for boxes vs. a circle/box approximating the prop's alpha silhouette, or `pymunk` from pip (deterministic for a fixed step).
  - Simulate at 240 Hz for the scene's duration inside an `lru_cache`. Index by frame, so `draw(t)` stays pure and out-of-order rendering works.
  - Words: cached `T.render` sprites drawn with `ts.draw(cv, x, y, rot=deg)` (rot clockwise).
  - Prop: a `sprites3d` sequence (`S3.get(...)`) with a known screen anchor.
  - Contacts: `K.impulse` on prop shake + `impact_soft` (one SFX per *major* contact only, max 3).
- **Legibility rule:** the settled sentence must hold ≥ words/3 s with word rotation within ±12°.
- **Cost:** solver negligible; draws about 5 ms per word.

#### 6. WAVEFORM CAPTIONS (the voice draws its own words)
- **Look:**
  - The VO's real **waveform** is a glowing ember line scrolling across the lower band.
  - Each word floats above **its own waveform segment**. The segment under the active word burns brighter, and past segments cool to `EMBER_DEEP`.
  - The keyword's **size and glow follow loudness**: louder means bigger, so emphasis literally comes from the voice.
  - Ember sparks lift off the peaks.
- **Why:** it shows the sound side of editing; it's calm and premium, good for the emotional reels (#28, #34).
- **Build:**
  - The envelope is the RMS of the VO wav per 1/60 s, computed once in numpy (`lru_cache`).
  - Visible window t ± 1.6 s mapped to x 90-910. Draw the polyline with `ui.stroke_mask` (width 4) + `K.glow`.
  - Word positions come from the words JSON segment centres. `glow gain = 1 + 1.5*rms_norm(t)` and keyword `scale = 1 + 0.12*rms_norm`.
  - Sparks: `K.Particles(60, seed=…, colors=[EMBER, EMBER_HOT])` emitted at local maxima.
- **SFX:** none; the VO is the sound.
- **Cost:** very low.
- **Safe zone:** the waveform at y 1380-1460, words at y 1180-1320, all ≤ x 930.

#### 7. EXPORT-DIALOG CTA (the reel exports itself, then loops)
- **Look:**
  - The CTA and signature arrive as an **export settings dialog**. Fields autocomplete:
    - File name: `jawad_mp4_tumhare_liye.mp4`
    - Format: `H.264 · 1080x1920 · 30 fps` (the true spec)
    - Destination: `tumhara feed`
  - The **CTA is the button label** ("Comment EMBER").
  - A cursor presses **Export**, a `progress_ring` completes, and on 100 % the frame whips into frame 0: the reel has "exported" itself and starts again.
- **Why:** a CTA that is also a loop bridge and an editor joke.
- **Build:**
  - Panel: `ui.glass_card(860, 860, look=EMBER_LOOK)`. Labels via `p.text(...)`.
  - Fields: `ui.search_bar(text, n=chars(t), w=700, placeholder='')` for typing.
  - Button: `ui.button('Comment EMBER', hover=…, press=…, ripple=t-tc)` restyled to the ember gradient (`grad=`).
  - Ring: `ui.progress_ring(p, colors=…)`. Cursor: `ui.draw_cursor`.
- **SFX:** `typing` (n, cps), `ui_click`, `bar_grow` (align='start'), and a frame-0 transient as the loop landing.
- **Safe zone:** the dialog body inside x 110-930 and y 520-1460.

#### 8. MOTION-TRACK CAPTIONS (text pinned with a visible tracker)
- **Look:**
  - A caption is **attached to a moving thing** (Jawad's hand from the character sheet cut-out, a 3D prop, a phone) by an After Effects-style **tracking reticle**: a square with a "+" centre, corner ticks, a dotted trail of past positions and a tiny mono label `TRACK 01 · 98.6%`.
  - The caption is **corner-pinned** in perspective.
  - On "lock", the reticle turns from white to ember with a click.
- **Why:** it turns a VFX technique into a caption device; great for "dekho kaise" moments.
- **Build:**
  - Path: `K.Track` (plus `.vel` for the blur).
  - Reticle: `ui.Surf` strokes (cache the static pieces). Label: `ui.put_text(..., 'JetBrainsMono-Bold', 28)`, decoration only.
  - Trail: sample the track at t−0.6…t and draw dots with fading opacity.
  - Corner pin: project the 4 corners of a small plane attached to the object through `cam.project` → `ts.draw_quad(cv, quad)`.
- **SFX:** `ui_tick` while tracking (sparse), `toggle_on` on lock.

#### 9. GRADE-WHEEL KEYWORD (bonus): the brand colour is "graded in"
- **Look:**
  - The keyword appears **flat log-grey**. A colour-wheel UI (lift/gamma/gain) slides in, the cursor drags the wheel toward orange-red, and the keyword is **graded live** from grey to the ember glow.
  - A tiny RGB parade shifts beside it.
- **Why:** it's a literal brand reveal; perfect for #25 *bada brand* and #21 *sasta*, and for the business-owner reel.
- **Build:**
  - Two cached sprites of the same keyword: grey `fill='#8C8C8C'` with no glow, and the ember version. Crossfade them with `grade(t)` ('inout_sine'), with the glow layer's opacity at `grade²`.
  - Wheel: a numpy HSV ring sprite, built once.
  - Parade: `ui.bar_chart([r, g, b], grow=…, colors=…, w=220, h=160)`.
- **SFX:** `slider_drag`, then `shimmer` at full grade.

#### 10. CTRL+Z CAPTIONS (bonus): a wrong belief is undone on screen
- **Look:**
  - The myth types out ("trending audio = viral").
  - Keycaps **CTRL + Z** press twice and the text **un-types in reverse**.
  - A small **History panel** lists `Type "trending audio = viral"`, `Undo`, `Type "pehla second"`, and then the truth types out with the ember keyword.
- **Why:** a native editor gesture for myth-busting (#12, #19, #9).
- **Build:**
  - `T.Glyphs(myth, 'flat', font='Poppins-SemiBold').typewriter(cv, t_eff, …)`, where `t_eff = t` before the undo and `t_undo - (t - t_undo)*1.6` after it (reverse at 1.6×).
  - Keycaps: `ui.chip('CTRL', sel=K.impulse(...))`.
  - Panel: `ui.glass_card` + `p.text` rows.
- **SFX:** `typing` (n, cps), `ui_click` ×2, `glitch_short` on the undo.

**Assignment rule:** use one signature device per reel, all different across the 5 reels, for its 1-3 key moments. The rest of the VO uses the house EMBER subtitles (§4.3) so the set feels like one brand.

---

## 5. Instagram post caption (the text under the reel)

### 5.1 Structure

```
L1  HOOK LINE        <= 55 characters (what shows in the Reels viewer). Roman Urdu, restates or extends the hook.
L2  context          1 line: the story or the promise.
    (blank line)
L3-5 body            2-4 short lines OR 3 numbered points (value reels). Use line breaks; keep each line under 60 chars.
    (blank line)
L6  keyword line     English search keywords, natural sentence: "Video editing, motion graphics aur AI video — sab ek laptop pe."
L7  CTA              ONE ask: send / save / comment KEYWORD / comment a memory.
L8  hashtags         3-5 (hard cap 5 incl. comments).
```

- **Length:** 400-900 characters total is fine; reels captions are read mostly by people who are already engaged and by search.
- **Emoji:** 0-2, never in on-screen type. Allowed in the post caption: 🔥 (on-brand ember), 😅, 👇.
- **Disclosure:** on AI-animated photos, write "AI se animate kiya" in the body and use Instagram's AI label if it applies. On paid or collab work, use the Paid Partnership label.

### 5.2 Roman Urdu vs English mix

- **Line 1 (hook): Roman Urdu / Hinglish**, for relatability and the desi scroll-stop.
- **The keyword line: English.** People and Google search English craft terms: video editing, video editor, motion graphics, AI video, Blender 3D, reels editing, cinematic edit. [Inference based on Google indexing and IG keyword search: put English terms in the first 2-3 lines when possible, e.g. "Video editing ka sabse bada jhoot".]
- **Roman Urdu searches people type** (add 1-2 naturally): "video editing kaise sikhe", "reels kaise banaye", "editing seekho". Spelling varies, so don't stuff variants.
- Use the canonical spellings from §2.5.

### 5.3 Keyword bank

- **Craft:** video editing, video editor, motion graphics, motion design, AI video, AI animation, Blender 3D, 3D animation, cinematic edit, color grading, sound design, kinetic typography, reels editing, short-form video.
- **Audience:** freelancer life, client revisions, content creator, small business video, brand video, personal brand, Instagram reels tips.
- **Desi/identity** (use lightly): desi creator, Hinglish, Roman Urdu.
- **Profile:** make the name field "Jawad · Video Editor & Motion Designer" (keyword-bearing; the name field is searchable). ⚑ Jawad decides. If he takes local clients, add his city to the bio (⚑ unknown).

### 5.4 Hashtags (3-5, labels not levers)

| reel type | set |
|---|---|
| Editor-life humour (#1, #4, #30, #39) | #videoediting #editorlife #videoeditor #desicreator #jawadmp4 |
| Creator lesson (#9, #10, #36) | #reelstips #contentcreator #videoediting #hinglish #jawadmp4 |
| Business (#21, #22, #24) | #smallbusiness #brandvideo #videomarketing #videoeditor #jawadmp4 |
| AI nostalgia (#28, #29) | #aivideo #nostalgia #yaadein #aianimation #jawadmp4 |
| 3D / motion showcase | #motiondesign #blender3d #motiongraphics #cinematic #jawadmp4 |

- `#jawadmp4` is the brand tag; keep it on every post so the brand page collects them.
- Don't use country tags (they invite rivalry comments) or generic mega-tags (#viral #explore #trending).

### 5.5 Other metadata (cheap wins)

- **Rename "Original audio"** to a hook-bearing title, e.g. "Bas ek chhota sa change · @jawad_mp4". It shows on the reel and on the audio page when others reuse it.
- **Pinned comment:** pin the answer, the keyword instructions, or the funniest viewer reply (the community signal).
- **Custom cover** set at upload (it can't be changed later) [2nd].
- **Collab invite** to a creator friend on co-made reels: one post, both audiences.
- **Alt text:** describe the scene plus keywords in plain words (accessibility and search).

### 5.6 Five caption templates (filled examples; first lines ≤ 60 characters, counted [Measured])

**T1: Relatable humour / send (for #1 "chhota sa change"), first line 48 characters**

```
Bas ek chhota sa change... aur 3 din chale gaye.
Har editor, har designer, har freelancer ke saath hua hai. Sach batao.

Client: "bas logo thoda bada"
Client: "music thoda aur energetic"
Client: "pehle wala hi theek tha" 🙃

Video editing aur motion graphics ki asli zindagi — 30 second mein.
Us client ko bhejo. Shayad samajh jaye 😅

#videoediting #editorlife #videoeditor #desicreator #jawadmp4
```

**T2: Value / save + keyword (for #9 "pehla second"), first line 53 characters**

```
Tumhara content bura nahi hai. Pehla second bura hai.
Reels editing mein ye 3 cheezein pehle 1.5 second mein honi chahiye:

1. Motion — frame 0 pe kuch chal raha ho
2. Text — 5 words se kam, 0.5 second tak readable
3. Voice — pehla lafz bina saans liye

Video editing tips for reels, Hinglish mein.
Comment HOOK — main tumhe apni hook checklist DM kar dunga (DM Requests check karna).

#reelstips #contentcreator #videoediting #hinglish #jawadmp4
```

⚑ The HOOK checklist must exist before posting. "pehla lafz" is Urdu-leaning; "pehla word" also works.

**T3: Business owner / lead (for #21 "video sasta"), first line 58 characters**

```
Product achha hai, video sasta dikhta hai. Farq yahan hai:
Same product, same phone — sirf edit, light aur sound ka farq.

Brand video ya product video ke liye 3 sawaal pehle poocho:
kya pehla second rokta hai? kya colours brand ke hain? kya sound mehenga lagta hai?

Small business video editing · brand video · product reels
Comment VIDEO — aapke product ke liye 3 free reel ideas DM karunga.

#smallbusiness #brandvideo #videomarketing #videoeditor #jawadmp4
```

⚑ Only if Jawad will actually send 3 ideas per comment; otherwise change the CTA to "DM 'BRAND' likho".

**T4: Nostalgia / AI (for #28 "purani photo"), first line 50 characters**

```
Ye photo 20 saal purani hai. Aaj ye phir se chali.
Ghar ki album se nikali, ghar walon ki ijazat se, AI se animate kiya.

Kuch yaadein delete nahi hoti — bas thodi dhundhli ho jati hain.

AI video · AI animation · photo to video
Apni ek yaad comment karo. Aur us bhai/behen ko bhejo jo ye yaad karta hai.

#aivideo #nostalgia #yaadein #aianimation #jawadmp4
```

⚑ The photo's age, ownership and consent are confirmed. The AI label applies.

**T5: Craft showcase / BTS (3D or motion reel), first line 54 characters**

```
Ye 35 second ka reel ek laptop pe bana hai. Breakdown:
Blender mein 3D, code se motion, aur har sound khud design kiya.

→ 3D props: Blender (CPU render)
→ Type + UI animation: Python motion toolkit
→ Voice + captions: Hinglish

Motion graphics · Blender 3D · kinetic typography
Kaunsa shot sabse mushkil tha? Guess karo 👇

#motiondesign #blender3d #motiongraphics #cinematic #jawadmp4
```

⚑ Every production claim must match how the reel was actually made: duration, laptop, tools.

---

## 6. Cover / thumbnail frame rules

1. **Always upload a custom 1080x1920 cover.** It shows in the profile grid (3:4 crop, 1080x1440, since Jan 2025 [2nd, [Hopper](https://www.hopperhq.com/blog/instagram-reel-size/)]), in shares and DMs, and in Explore tiles. It can't be changed after posting [2nd].
2. **Composition safe area:**
   - The title, face and keyword sit inside **y 285-1635**, the band common to the 3:4 grid and 4:5 feed crops.
   - Key copy sits inside **y 285-1480**, which also clears the Reels UI.
   - For the strictest square crops, keep the keyword inside y 420-1500.
3. **The house cover formula** (from his 3 prior covers):
   - a warm-black cinematic world;
   - the subject with a red-orange **rim light**;
   - a small **grotesk caps line** (2-3 words);
   - a big **glowing serif-italic keyword** (≥ 170 px);
   - a **glowing underline**;
   - `@jawad_mp4` in small type;
   - ember particles or bokeh.

   Keep this formula. It is his recognisable grid.
4. **2-5 words maximum on the cover.** The cover title is the **topic label**, not the full hook: "BAS EK *chhota sa* CHANGE", "*shaadi ki* VIDEO?", "RENDER *99%*".
5. **Grid rhythm:** put every cover's keyword band at the same height (e.g. a centre line at y ≈ 1050-1150). Across a 3-wide profile row the ember keywords then line up into one glowing band, so the profile reads as a designed series. Alternate the subject between the left and right thirds for movement.
6. **Faces:** use the character-sheet expressions that match the hook: *shocked* (#6, #30), *confused* (#2, #26), *smirk* (#9, #21), *hand-on-chest* (#28, #34). The eye-line points at the keyword. The face sits inside x 140-940.
7. **The thumbnail legibility test:** downscale the cover to 240 px wide (about the size of a grid tile on a phone). The keyword must still be readable and the face's emotion clear. If not, cut words or enlarge them.
8. **Frame 0 ≠ cover, but both must work.** The Reels tab autoplays from frame 0, so frame 0 is the real hook. The cover can be a more composed still of the same idea (often the payoff frame with the title added).
9. **Original only:** no copyrighted characters, logos or film stills on brand covers (originality ranking and IP risk). Jawad's character-sheet likeness and original 3D worlds only.
10. **Colour:** ember on warm black. Keep blue and green to small accents (e.g. a UI detail), so the grid stays on-brand. The prior "yaadein" cover's purple-blue background was a one-off and shouldn't become the norm. ⚑ Jawad decides.

---

## 7. Pre-publish checklist (per reel)

**Hook**
- [ ] Frame 0 is moving and bright, with a transient on f0-f2.
- [ ] Text ≤ 5 words, readable by 0.5 s, one ember keyword.
- [ ] VO starts by f3; the hook sentence ends by 3.0 s.

**Structure**
- [ ] Events every ≤ 3 s; midpoint break at 45-50 %; payoff at 65-80 %.
- [ ] One CTA at 82-93 %; the loop bridge holds and frame DUR−1 matches frame 0.
- [ ] No fade to black, no silent tail.

**Captions**
- [ ] Ink scan inside x 70-1010 and y 230-1480; max x ≤ 930 in y 1050-1700; nothing textual below y 1620.
- [ ] No doubled words between headline and subtitles.
- [ ] Highlight within ±1 frame of word onsets.
- [ ] The SRT is exported (sentence mode).

**Language**
- [ ] Canonical spellings (§2.5); no currency figures, politics or rivalry.
- [ ] TTS pronunciation checked (z / f / q sounds).

**Claims**
- [ ] Every ⚑ line confirmed by Jawad: personal stories, counts, deliverables, consent, tool claims.

**Post**
- [ ] L1 ≤ 55 characters; English keywords in the first 2-3 lines.
- [ ] One CTA; ≤ 5 hashtags.
- [ ] Audio renamed; cover uploaded; AI or paid labels if they apply.
- [ ] Trial Reel B ready if A/B testing.

---

## 8. Sources

**Meta (primary)**
- Rewarding original creators on Instagram (30 Apr 2026): https://creators.instagram.com/blog/rewarding-original-creators-on-instagram
- Instagram Platform, Private Replies (updated 2 Jul 2026): https://developers.facebook.com/docs/instagram-platform/private-replies/
- Meta AI translation expansion (JP newsroom, Jul 2026): https://about.fb.com/ja/news/2026/07/meta-ai-translation/

**Secondary (trade press and vendor blogs; treat as informed opinion)**
- Ranking signals: https://www.unfollr.com/blog/how-instagram-algorithm-works · https://stackinfluence.com/blog/how-does-the-algorithm-for-reels-work · https://watsspace.com/blog/adam-mosseri-explains-how-instagram-ranking-really-works/
- Skip rate and retention: https://www.socialmediatoday.com/news/instagram-adds-retention-insights-reels/758464/ · https://metricool.com/instagram-reel-analytics/
- Views and replays: https://www.socialcrawl.dev/blog/how-instagram-counts-views · https://www.socialpilot.co/instagram-marketing/instagram-views-metrics-changes
- Hashtag cap: https://www.sirency.com/blog/instagram-hashtag-limit · https://www.socialmediatoday.com/news/instagrams-testing-new-limits-how-many-hashtags-you-can-add/707471/
- Google indexing: https://insights.vaizle.com/?p=8751 · https://www.ovrdrv.com/insights/google-indexing-instagram-content
- Trial Reels: https://publer.com/blog/instagram-trial-reels-guide/ · https://brandid.app/blog/instagram-trial-reels/
- Caption truncation: https://lettercounter.org/blog/instagram-reels-caption-length/ · https://bundle.social/blog/instagram-character-limits-guide
- Reel and cover sizes: https://www.hopperhq.com/blog/instagram-reel-size/ · https://socialk.it/en/sizes/instagram-reel-size
- Hindi AI dubbing: https://www.businesstoday.in/amp/technology/news/story/meta-adds-hindi-ai-translation-for-reels-on-instagram-and-facebook-497661-2025-10-10
- Editing aesthetics 2026: https://www.opus.pro/blog/editing-aesthetics-dominating-short-form-2026
- Hook types 2026: https://blitzcutai.com/blog/best-instagram-reels-hooks-2026
- Hinglish engagement (IIT Delhi study on X): https://www.dtnext.in/lifestyle/wellbeing/hinglish-helps-users-engage-more-effectively-with-a-broader-audience-study-790290
- Video-sharing motives: https://reunir.unir.net/handle/123456789/1763 · https://doaj.org/article/2c5ae278affb43e6883a4baf18afb157

**Measured here**
- Fonts from the Google Fonts CSS2 API, downloaded to a scratch folder and measured with Pillow/raqm (em/char, line widths of all 101 on-screen hook lines). Serif-italic house-style comparison sheet rendered.
- Colour tokens sampled from `workspace/brand_reels/prior/*_cover_1080x1920.jpg`.
- ref2 and ref3 word rates via faster-whisper (base, int8, CPU); ref2's own whisper JSON.
