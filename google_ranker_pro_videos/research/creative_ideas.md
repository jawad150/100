# Creative research: 15 videos for Google Ranker Pro / Hulk Marketing

Researched 22 Oct 2026. Sources: Pinterest search (20 queries, about 970 pins parsed), web search for 2025-26 short-form trends, and the user's own skills (`human-realism`, `production-consistency`, `cinedance-higgsfield`, `higgsfield-production`).

---

## 0. How Pinterest was researched (and the limits)

- The Pinterest search HTML page (`/search/pins/?q=`) builds its results on the client side, so the raw HTML has no pins in it. However, the site's own JSON endpoint (`/resource/BaseSearchResource/get/`) answered logged-out curl requests with 48 to 50 pins per query. I parsed the title, description, outbound link and video flag for each pin. The script is at `/tmp/claude-0/-home-user-100/753dbccd-034a-5c54-a3a6-3c1d83ca4518/scratchpad/pin_search.py` and the raw data at `.../scratchpad/pins.json`.
- **About the pin IDs:** logged-out responses return encrypted IDs (`e1_…`) in place of numeric ones. The pin URLs below use those IDs. They may only open in a logged-in browser. If one does not open, use the matching search URL in the form `https://www.pinterest.com/search/pins/?q=<query>`.
- **What we found:** Pinterest results for "agency video" are mostly polished motion-graphics promos (South Asian and Gulf digital agencies, "POV: you found the agency…"). These are the **opposite** of what this brief needs. The useful pins are the formats, below: voice-note testimonials, "stop sharing testimonial graphics", talking-head edits, meet-the-team chair spins, day-in-the-life, café-style phone-only reels, and before/after website wipes.
- I found no Pinterest pin showing a UK taxi firm with a strong video. Taxi pins are generic "call us" promos (AtomCabs Yeovil, Nexus Taxis Barnsley/Sheffield, Richmond Taxi), so there is an open lane for real-feeling local footage.

### Pinterest sources used (query → pin)
| # | Query | Pin | What it shows / why it matters |
|---|---|---|---|
| P1 | testimonial video ideas | https://www.pinterest.com/pin/e1_AfqPShxDhZLJwBmAPteuYBfcuPzm13ssfEQZcgEHbj8QwOgYK6MG/ | "STOP sharing testimonial graphics + do this instead": a scripted talking video beats a quote card |
| P2 | testimonial video ideas | https://www.pinterest.com/pin/e1_AfqPShzLPH6QWgeF_4TxplWH9p0dUUxC0C8BctpbfJJBsZ5RXlYD/ | "Voice note testimonials welcome": a client's WhatsApp voice note used as the testimonial audio |
| P3 | testimonial video ideas | https://www.pinterest.com/pin/e1_AfqPShxYXXDrzbtveoBdzQ4a5JqBAbn3zho4U1-biteOuX03eVzJvA/ | "Real client conversation: agency results": a two-person call/meeting format in place of a scripted piece to camera |
| P4 | client testimonial video | https://www.pinterest.com/pin/e1_AfqPShzeds98qQ2MR_nCqRUB3Bqh38Hh-G894WpUKe4plMg1ESqz/ | "Website SEO client feedback": the SEO-specific testimonial genre (mostly low effort, an easy bar to beat) |
| P5 | client testimonial video | https://www.pinterest.com/pin/e1_AfqPShw7nKbwTmJBqUBQxP06Ginvo4qLg8BvFDeb0vPBoMjl_SAI/ | Testimonial edit with a typing effect and star-rating overlay |
| P6 | seo agency video content | https://www.pinterest.com/pin/e1_AfqPShymVahfK_5ddtO9CzbO3XXf1cBqVHUhNieX5qNuHpk0BG14sA/ | "When clients compare our work with others, the reaction says it all": a reaction-led format |
| P7 | marketing agency reels ideas | https://www.pinterest.com/pin/e1_AfqPShz8YYkArAydZs56bvAi8vlwpYocGdGFsA1tCtyRmPAs0YKE/ | "Before: posting just to post. After: strategy" text-driven before/after |
| P8 | marketing agency reels ideas | https://www.pinterest.com/pin/e1_AfqPShzji5zl1kZ2NxRJlpOo-Ieh4zSQ5AvyK5eGY27SaOkaIC-i/ | "POV: when you work with a digital marketing agency" POV hook |
| P9 | before and after website redesign | https://www.pinterest.com/pin/e1_AfqPShzGyrl_paua3tyc-WlV0t9d-wU9l5Mc5Hl-ehYMv8Zd60BhIw/ | Cluttered old homepage vs clean new one with a clear call to action, side by side |
| P10 | before and after website redesign | https://www.pinterest.com/pin/e1_AfqPShzpxXJdeJMkz483ZB7gEWxjPjWACk1FPjYGHa8hp_m67rvtWg/ | Diamond Shine Window Cleaning redesign: a **local service business** case study (closest analogue to the taxi clients) |
| P11 | screen recording reel ideas | https://www.pinterest.com/pin/e1_AfqPShz_7pljoMgdLkfrMNiGNXtnUPk0QncSyYIhJ4qH6Rlc-AvsLQ/ | Putting a screen recording inside an iPhone frame template |
| P12 | screen recording reel ideas | https://www.pinterest.com/pin/e1_AfqPShzwdxrCyf57kQYDrJU9n0b464aqUjz2CYTE7XGllqFI-bcd/ | 3D-tilt motion on a website screen recording (After Effects) |
| P13 | screen recording reel ideas | https://www.pinterest.com/pin/e1_AfqPShzs60HmxRauA3OKJSUa_VH0jbOOy5ZrbbXU9zXpuGLdwe-l/ | Screen-scroll "playlist" effect for Reels |
| P14 | screen recording reel ideas | https://www.pinterest.com/pin/e1_AfqPShy8FwsWWeH7I6EBb_9qn6GqvpcuREND8ZTgrIKaSX5O2XHT/ | Green-screen reveal effect |
| P15 | screen recording reel ideas | https://www.pinterest.com/pin/e1_AfqPShyb7PEqQs0UflHgWtR4bD92P5onOTwLsA7QoE0l0KH2Se88/ | "Grab an object out of your phone": a phone screen as a green screen |
| P16 | talking head video ideas | https://www.pinterest.com/pin/e1_AfqPShxPe5ACs-kCFjluV6ER0AkbfjQYI1xONgFv4I6SfgycLGXw/ | "Talking head prompt: clean home vlog aesthetic": natural window light, smartphone perspective (an AI-realism reference) |
| P17 | talking head video ideas | https://www.pinterest.com/pin/e1_AfqPShywC0MWga3CKg_LiabagEQmras7dQOyH1MlXaHSidMkz_9Nlg/ | Raw talking head turned into a cinematic short (before/after of the edit itself) |
| P18 | meet the team video | https://www.pinterest.com/pin/e1_AfqPShwutlJI1UZG0kClZoZpODm23_AaGMy8xDAZ-t9Dqqp_ZoK61Q/ | "We spun our chairs (literally)": the chair-spin reveal for each team member |
| P19 | meet the team video | https://www.pinterest.com/pin/e1_AfqPShzfGh4GGQTRGwKi9-GDMpHaQnkj0w9k2z_N4E-9peUPbSt-3g/ | "Meet the team (caution: plot twist at the end)": an end-twist hook |
| P20 | meet the team video | https://www.pinterest.com/pin/e1_AfqPShyhqkOXkC11rEwy14kxIMaRnzw5sR3LCXHKTJLobfj9y2MRug/ | "Brains full of tools, tabs and 'just one more edit'": self-deprecating agency humour |
| P21 | day in the life marketing agency | https://www.pinterest.com/pin/e1_AfqPShzVEf14wieLfukS_3sy7KLAgjb1KW79j8odvRoUlVGFCGX_/ | "Co-founders on opposite sides of the world: 10/10 ambition, 2/10 time zones". **This maps directly onto the UK–Pakistan team angle** |
| P22 | day in the life marketing agency | https://www.pinterest.com/pin/e1_AfqPShzGCpAd_jmkfEI-i1bghgZid3Ud5IdocHEjHHwcosaeFKjbMA/ | "A very real day in the life of a marketing agency owner" |
| P23 | day in the life marketing agency | https://www.pinterest.com/pin/e1_AfqPShyGf4Lv-_26zsYbYJ6tNrAibPIcr7cZgqk_VaIUb8YGpZu9/ | Day in the life of a Senior Digital Strategy Manager (role-specific) |
| P24 | day in the life marketing agency | https://www.pinterest.com/pin/e1_AfqPShx9PO9kWcnxX1VrHMX5977ByN35GpKrx56dOSMHHgbH7l522w/ | Monthly behind-the-scenes recap ("see you next month") |
| P25 | behind the scenes agency | https://www.pinterest.com/pin/e1_AfqPShwfDYrQZQYACRVTkc6ldzMGFdVp68w3ArNepNXpwJtd3C91/ | An agency showing its process deck before a client shoot |
| P26 | behind the scenes agency | https://www.pinterest.com/pin/e1_AfqPShypixpsmVcGt0qtHY9AytlWhZF2YJ9wjLQZBtbquYzZ2Yj7/ | Candid office moment, 134 Agency: "authentic branding" stills |
| P27 | founder video ideas | https://www.pinterest.com/pin/e1_AfqPShwzFO-HKmYpdZqKj8quHHBaYV7FIhCcD0GQ1bCjjLuZN8ei/ | "12 ways to film yourself as a brand founder": a B-roll library for founders |
| P28 | founder video ideas | https://www.pinterest.com/pin/e1_AfqPShwwqeez3LNIARg5UWDiKQ09Mjm4jcRBKK7VMXy_rFBLUvAZpA/ | "The little moments in a founder's day you don't see" |
| P29 | founder video ideas | https://www.pinterest.com/pin/e1_AfqPShwhZ-_8dq5xvThtxRKYZ1fLUDlpbt1UZ9Mld61cES8FTdPBeg/ | "#TeamTuesday: our CEO and co-founder, here's how he started" |
| P30 | founder video ideas | https://www.pinterest.com/pin/e1_AfqPShycoWLEoYqZHLzkDO0BX015aMDN09DlI5_vHs3EHWKqpL8h/ | Founder explains "why I left my job to start this" |
| P31 | local business video ideas | https://www.pinterest.com/pin/e1_AfqPShwApNyCDjl48jaRGtFfmtIB147yGVCLADjAygXkxQ11c_eKlw/ | **Inverted-focus trend**: the customer in the foreground is soft-focus, the owners in the background are sharp and watching the reaction |
| P32 | local business video ideas | https://www.pinterest.com/pin/e1_AfqPShxzBK60cPGlar89mcvg7DtbK0T1fbawVcmN_Qm30hROvVAJ/ | Café reel shot only on a phone, with 4 in-camera transitions |
| P33 | local business video ideas | https://www.pinterest.com/pin/e1_AfqPShwASrwnRCsa3ekLYwapuCDOz0LnKOrL1_KR5DnBj9mo9alg/ | Why a Google Business Profile video belongs in local SEO |
| P34 | local business video ideas | https://www.pinterest.com/pin/e1_AfqPShwbPAHyC1u5qRdA6ojiRR5M7Rk-jD6tco-0H80YI4seiMP88Q/ | CapCut "zoom in transform" transition |
| P35 | google ranking results video | https://www.pinterest.com/pin/e1_AfqPShw8PiQCrEGAA-LD67O2hKOviOApGXsC-ZOYnOo0vNfb1U8Y/ | "Real SEO results: client jumped to page 1 position 1": a rank-tracker walkthrough |
| P36 | google ranking results video | https://www.pinterest.com/pin/e1_AfqPShwIn5gjFD13WOr5flL38vlS4vNmrF4r0iech5MaTaDSk0mF/ | "Most buying decisions start with a search. Are you showing up?" Local SEO hook |
| P37 | google ranking results video | https://www.pinterest.com/pin/e1_AfqPShwuEiB6jspgkiqzIdfiBMoia_2LarhLeREAl36-NuN6vLnI/ | A founder (Merit Marketing) gives SEO tips to camera |
| P38 | seo tips reel | https://www.pinterest.com/pin/e1_AfqPShz3S3-BAg9kNELopAW7HHT15KDXk-ArVyOx60vMIvTvux-g/ | "SEO myth vs fact" format |
| P39 | seo tips reel | https://www.pinterest.com/pin/e1_AfqPShzzxXIxz23U7GBvWr2ajGKQOvP-gYNwdCbgsnD7BQ2W7PbC/ | "You don't rank because of content, you rank because of authority": a contrarian tip |
| P40 | taxi company marketing video | https://www.pinterest.com/pin/e1_AfqPShzRQTuEHpyt7ahMF7vOqQWjZjlC-QIl238DQDxiDrZEkHyu/ | AtomCabs Yeovil: a generic taxi promo (shows the low bar in the category) |
| P41 | taxi company marketing video | https://www.pinterest.com/pin/e1_AfqPShzgwOuymVKV45U30yxzoS9Qh5uiT9djDBAa0STXDksQ4CyO/ | Nexus Taxis: "Airport Taxi Sheffield / Airport Transfers": a UK airport-transfer angle |
| P42 | ugc video ideas small business | https://www.pinterest.com/pin/e1_AfqPShxUvgmsgfv9JFqf2qUBZebMnzVoP_HUVh0t6MxHBFSR-boTHg/ | "25 UGC video ideas": demos, reviews, before/after, reactions |
| P43 | ugc video ideas small business | https://www.pinterest.com/pin/e1_AfqPShydYOWZdxlTfyyl3wWJOrDtmsx_uRvyFzl9AC8BYYb4YeMe/ | Product-reveal transition tutorial (hand-cover wipe) |
| P44 | case study video | https://www.pinterest.com/pin/e1_AfqPShxvRyjmTfQ-bjKJDNb7J8uAtNWztVEoDBoKpTlEYTBtFGvJaA/ | Raw talking head turned into a VSL with minimal motion design |
| P45 | case study video | https://www.pinterest.com/pin/e1_AfqPShzANTbh1qBB-169O3T5pfIgnJy4zuoICBkMeK9UFLBA8J51/ | Local Measure × Are Media case-study video structure |

Fallback search URLs: `https://www.pinterest.com/search/pins/?q=testimonial%20video%20ideas` (swap in any query from the table).

### Web sources (2025-26 trends)
- Sendible, *Top Social Media Trends Report 2026*: https://www.sendible.com/insights/latest-social-media-trends-report (vertical short-form keeps its lead; don't chase sounds without a purpose; one clear call to action per video)
- Shoots.video, *How short-form social video is changing local marketing*: https://www.shoots.video/post/how-short-form-social-media-videos-are-changing-local-marketing/ (local discovery is moving to video; BTS, customer reactions and day-in-the-life content beat polish. Vendor blog, so treat its claims as directional)
- Telkom University mirror of *Video marketing trends 2026*: https://forumfilmtelkom.orgs.telkomuniversity.ac.id/2025/12/12/the-video-marketing-trends-every-brand-should-watch-in-2026/ ("a shaky phone recording with a strong opening line outperforms a polished clip with a slow build-up")
- Nonsensical Agency, *How to do TikTok SEO in 2026*: https://nonsensical.agency/webinars/how-to-do-tiktok-seo-in-2026/ (search results autoplay, so put the keyword or metric in the first seconds and on the cover)
- White Rabbit Social, *SEO in short-form content*: https://whiterabbitsocial.com/all-articles/the-seo-revolution-in-short-form-content-tiktok-and-instagram-reels
- Adobe Community, *Tracking an AI-generated screen*: https://community.adobe.com/questions-529/how-do-i-track-this-footage-60652 (planar tracks drift on AI clips without markers)
- Tracking Marker app by DPBOX: https://apps.apple.com/bz/app/tracking-marker-by-dpbox/id6745626443 and CapCut phone-screen green-screen templates: https://www.capcut.com/explore/phone-screen-green-screen

---

## 1. Rules that shape every idea below

1. **Realism comes first.** Everything we generate should look like it was filmed on an iPhone or a mid-range mirrorless camera. Keep one light direction, one texture note, one deliberate imperfection, light grain and a muted grade (`higgsfield-production` §"Keep"). Skin should be age-scaled with visible pores and no beautifying (`human-realism`). Do not stack realism adjectives: too many cancel each other out.
2. **Lo-fi wins on social and is easier to fake honestly.** Arm's-length selfie, phone propped on a dashboard or desk, slight handheld drift, an auto-exposure breathing shift, a car or office room tone. Avoid gimbal-smooth dolly moves, rim-lit studio portraits and shallow cinematic bokeh on UGC pieces. That is the "CGI/advert" look the user wants to avoid.
3. **Never generate readable screens.** Seedance produces gibberish text on laptops and phones. Every screen in a generation is one of these:
   - **(a) angled away / back of device:** we see the person and the glow on their face, not the screen;
   - **(b) shallow-focus blur:** the screen is in frame but out of focus, so there is nothing legible;
   - **(c) flat green or flat white fill held steady:** for screen replacement in the edit. Ask for "a plain uniformly lit bright green screen with no interface, held steady, no glare". Because AI clips track badly without markers, also ask for **four small dark corner dots** on the screen, or keep the device mostly still.
   - **(d) real screen recording:** the real Search Console / GBP / website capture is cut in full-frame, or pushed into a phone/laptop mock-up in the edit.
   Also prompt "no subtitles, no on-screen text, no logos, no readable signage, no number plates readable".
4. **Honesty modes.**
   - **Mode B (real person):** a named client owner, the founder or a named team member, built from their own photos with their permission, saying approved words. Ideally lip-synced to their own voice memo.
   - **Mode A (labelled AI presenter):** may *narrate* a real case study with the real data. It is never presented as the client. Burn in "AI presenter" for the whole time it is on screen.
   - **Faceless:** hands, the back of a head, a POV, a car interior, a phone in hand, a landmark exterior. This is the safest way to show "a client" without a fake face, and it works very well for UGC formats.
5. **Use only the real numbers.** Overlays may only quote these:
   - Golden Line: 312 clicks, 18.2K impressions, avg pos 18.9, "golden line taxis warwick" pos 1.8, "taxi with car seat" pos 1.7, "airport taxi warwick" pos 5.3
   - Coventry Airport Taxis 247: 224 clicks, 15.9K impressions, "pre book taxi to airport" pos 2.3, "coventry airport transfers" pos 6.0 at 10.5% CTR
   - GBP: Leamington Spa 114 calls May–Oct 2026, 25 in Sept; Coventry 79 interactions, peak about 32 in Aug
   - "Ranking no.1" for leamingtonspa-taxis / yorkcars only with a cited, dated ranking source (screenshot of the search plus date and location). Until we have that, label it as unverified.

---

## 2. Reusable devices library

### Hooks (first 1–2 s)
- **H1 Number-first:** the cold open is the metric on a real screen recording ("312 clicks"), with the face cutting in at 0.8 s. TikTok/Shorts search autoplays the start, so put the keyword or metric there (Nonsensical).
- **H2 Inverted focus (P31):** a soft-focus foreground subject (a phone with a report) and a sharp owner reacting behind. It looks very real because it is a "mistake" a phone camera actually makes.
- **H3 The search itself:** a thumb types "taxi warwick" (real screen recording) and the result appears. Cut to the car pulling up outside. "This is what your customers see."
- **H4 Voice-note open (P2):** a black screen or phone on a desk with a WhatsApp voice-note waveform (built in the edit) and the client's real voice: "Honestly, the phone hasn't stopped…"
- **H5 POV caption (P8):** "POV: your taxi firm finally shows up on Google". Text in the edit, over a real-looking dashcam or driver-seat shot.
- **H6 Contrarian line (P39):** "Your website isn't the problem. Your Google Business Profile is."
- **H7 Pattern break:** the phone is slammed face-down on a desk, or a laptop lid snaps open (generated foley), on frame 1.

### Framings that read as "real"
- **F1 Arm's-length selfie:** front camera, slight wide-angle distortion, the arm visible at the frame edge, small hand wobble, eye-line just off the lens (people look at themselves on screen).
- **F2 Propped phone:** low angle from a desk or dashboard, static frame, the subject leans in and out of focus, a mug or keys in the foreground.
- **F3 Over-the-shoulder at a laptop:** the screen is out of focus or green (rule 3), the face reflects screen-glow, a hand on the trackpad.
- **F4 Dashcam / driver-seat:** a windscreen-mounted wide shot of a taxi driver or owner talking at a red light, with real road noise. This is the signature look for the taxi clients.
- **F5 POV hands:** a phone in hand showing a green screen, a thumb scrolling. Faceless, so it is safe for "client" UGC.
- **F6 Interview two-shot (P3):** a 3/4 seated angle, with the interviewer off-camera left. Mode B only.
- **F7 Walk-and-talk:** handheld backwards walk through an office, rank or yard, with a natural bounce in the frame.

### Transitions that suit AI raw footage + edit overlays
- **T1 Before/after wipe (P9, P10):** a vertical bar wipes from the old site to the new one. It uses real captures, so it needs no generation.
- **T2 Phone-screen push-in (P11, P15):** a generated hand holds a phone with a green screen, the edit tracks in the real screen recording, then scales to full-frame.
- **T3 Search Console chart draw-on:** the clicks line draws left to right (a rebuilt vector chart from the real values, or a masked reveal of the real screenshot), with the number counting up to 312.
- **T4 Ranking-ladder climb:** a vertical list of SERP positions with the client's row sliding up to "1.8" or "2.3" (real values only). It works as a transition between talking beats.
- **T5 Map pin drop:** a Google-Maps-style pin drops on Warwick / Leamington / Coventry, with a soft ripple. Recreate the map in a neutral style, not as a fake Google UI.
- **T6 Hand-cover / swipe-up reveal (P43):** a hand passes across the lens and is matched to the next clip, or a swipe-up gesture reveals the report. Generate the hand pass at the end of clip A and the start of clip B.
- **T7 Split screen:** "Before" (May, 0 interactions) and "After" (Aug, about 32) as two halves with the real GBP chart, with the owner in the other half.
- **T8 Green-screen-over-report (P14):** the presenter is keyed over a real Search Console background. Generate the presenter against a flat green or a plain wall, using CINEDANCE's green-screen plate.
- **T9 Zoom-in transform (P34):** a punch-in on the eyes or the screen, matched to the next shot.
- **T10 Monthly-report envelope:** a phone notification ("Your monthly report") is the cut point into the reaction.

### Pacing
- Social pieces (3, 7, 8, 9, 11, 12, 14): a cut or punch-in every 1.5–2.5 s, the payoff at 60–70% of the runtime, and one call to action (Sendible).
- Web pieces (1, 2, 5, 6, 10, 13, 15): slower, with 3–5 s holds on faces. It is fine to let a pause breathe, since that is what reads as human.
- Retention tricks: a jump cut on each new sentence, a 105–110% punch-in on emphasis words, a 1-frame white flash on number reveals (no more than once per video).

### Sound
- Use native Seedance room tone or foley wherever possible: road noise, indicator tick, keyboard, kettle, office hum, the car door clunk. Real ambience sells realism more than visuals do.
- Speech: the client's own voice memo for Mode B, or a labelled AI voice for Mode A. Prompt "no background music" in Seedance and add music in the edit (a licensed bed, mixed low under speech).
- SFX in the edit: a soft tick on each count-up step, a "pop" on the map pin drop, a whoosh limited to transitions T1/T2. Avoid cash-register or "cha-ching" sounds; they cheapen the result.
- Master at −14 LUFS for social.

### Typography / overlays for SEO results
- **Data card:** a flat rounded rectangle, one big number (Inter / General-Sans-style grotesk, tabular figures), a small grey label ("Clicks · last 3 months · Google Search Console"). Always cite the source and the date range under the number.
- **Query chip:** a pill with a magnifier icon and the real query, e.g. `taxi with car seat → pos 1.7`.
- **Delta tags:** a green ▲ only when there is a real before value. GSC screenshots for the last 3 months alone do not show "growth" without a comparison period, so ask the user for a compare or 16-month view before claiming an increase.
- **Captions:** word-timed, in the lower third above the platform UI safe zone. White with a dark shadow, no neon karaoke styles (they read as low-end Fiverr).
- **Disclosure line:** "AI presenter" or "Dramatised reconstruction. Real data from Google Search Console", small and persistent.

---

## 3. Ideas per video (1–15)

**1. Testimonial (60–90 s, homepage + case studies)**
- Mode B only, with a real owner (e.g. the Golden Line or Leamington Spa owner) built from their photos and lip-synced to their own recorded answers to three prompts: problem, change, result. If no consent: a **faceless dashcam testimonial**, where the voice memo plays over F4 driver-seat shots (no face, no name, or a name only with written permission).
- Structure (P1, P3): problem told over a quiet phone on the dashboard, F2 → what changed, over-the-shoulder at the GBP app (green screen, T2) → result: 114 calls May–Oct, 25 in Sept (T7 split with the real GBP chart).
- Open with H4 (voice note). Close on the car pulling away and the client's line, with no slogan.

**2. Results walkthrough (30–45 s)**
- Owner at a kitchen table or office desk, laptop angled 3/4 away, screen glow on the face (F3). The real Search Console capture is cut in full-frame with T3 draw-on.
- Reaction beats: a lean-in, a hand to the mouth, a pointing finger. Generate these as separate short reaction clips (2–4 s) so the edit can place them on the real chart moments.
- Overlays: query chips for "golden line taxis warwick pos 1.8", "airport taxi warwick pos 5.3".

**3. Milestone clip (15–20 s)**
- H1 number-first: "taxi with car seat: position 1.7". Owner's one line in their own words via selfie F1 from the car park or rank.
- Use only milestones the data supports. "1,000 clicks in a month" is **not** supported (Golden Line had 312 in 3 months), so don't use it. Use "page one for 'pre book taxi to airport' (pos 2.3)" or "25 calls from Google in September".

**4. Before and after (20–30 s)**
- T1 vertical wipe old vs new site (real captures, P9/P10), then T7 GBP chart May vs Aug.
- Generated B-roll in between: a phone ringing face-up on a dashboard (screen unreadable), a driver picking up. This is the "after" made human.
- Hook: "Same taxi firm. Same town. Different website."

**5. Premises / team tour (30 s)**
- F7 walk-and-talk handheld through the taxi office or yard: dispatch desk, keys on hooks, cars washed. Mode B owner, or faceless POV if no consent.
- Cutaways: the fleet badge blurred, number plates unreadable, a real Warwick/Leamington landmark establishing shot (generated with no signage text). T5 map pin drop on the town.

**6. Client FAQ short (20–30 s)**
- One question on screen ("Was it worth it?"), with the owner's answer to camera on a propped phone (F2).
- Optional inverted-focus open (H2): the agency person in soft focus in the foreground, the owner sharp in the background.

**7. "What I learned from SEO" selfie (20 s)**
- F1 selfie walking to the car, with three quick lessons as jump cuts. A team member (Mode B) or a labelled AI presenter.
- Lesson examples tied to the data: "Your brand name should rank first: Golden Line is pos 1.8 for its own name"; "Car-seat searches are a niche worth owning"; "Calls come from the Business Profile, not just the website".

**8. Screen recording with voiceover (30 s)**
- Mostly the real screen recording, filmed as a phone-filming-a-laptop look: generate a hand holding a phone that films a laptop with a **green** laptop screen, then key in the real capture at a slight angle with moiré and a glare overlay for that "filmed off the screen" feel.
- Voiceover: "This keyword just hit position 3". Use a real query near 3, e.g. "pre book taxi to airport, 2.3". Do not round it to "3" unless that is honest; say "two point three".

**9. Reaction clip (15 s)**
- T10 notification → H2 inverted focus or F2 propped phone at the dashboard → the reaction (a quiet "no way", a laugh, showing a colleague). Reactions should be understated; big gasps look fake.
- Faceless alternative: hands only, the phone screen as a green fill plus the real report, and the voice reacting off-camera.

**10. Meet the team (30 s, one person per clip)**
- P18 chair-spin reveal: the person spins round in their office chair and says "I'm ___, I do ___ for your Google listing". One generation per person, Mode B (their photos).
- P19 end-twist: the last person is the founder or the office dog. P20 humour line: "brains full of tabs".

**11. Behind the scenes (20 s)**
- Audit or strategy session: over-the-shoulder at a whiteboard sketch of a "map pack" (with no readable words, just boxes and arrows), sticky notes, a laptop at an angle. P25 deck-prep, P26 candid office.
- Fast cuts (1.5 s), with keyboard, marker and kettle foley.

**12. Day in the life (30 s, UK or Pakistan)**
- P21 angle: "UK clients, Pakistan delivery: two time zones, one report". A split-screen morning in Lahore/Karachi (call to prayer outside, chai, laptop) and the UK owner's phone ringing at 9am. Only use real locations of real team members; confirm where the team is before scripting.
- Time stamps in the edit (08:00 PKT / 04:00 UK). Ends with a real GBP call stat.

**13. Founder intro (45–60 s)**
- Mode B founder from their own photos and voice. Sections: who we help (local trades/taxis), why I started, what clients get.
- P27 founder B-roll library: walking in, coffee, writing on a whiteboard, on the phone to a client, a car at a client's rank. Shoot about 8 short B-roll generations to cut between the talking beats.
- Calmer homepage pacing; natural window light (P16).

**14. SEO tip of the week (30 s)**
- Recurring format: the same framing every week (desk, plant, mug), using a P38 myth/fact or P39 contrarian hook. One tip per clip, with T8 green-screen-over-report if the tip shows a GSC view.
- Tip bank from the real data: "Own your brand name (pos 1.8)", "Low CTR at pos 10? Rewrite the title: 'taxi warwick' 665 impressions at pos 10.7", "Add service + niche pages: 'taxi with car seat' pos 1.7".

**15. Founder commentary on results (30–45 s)**
- Founder over-the-shoulder (F3) pointing at the green-screen monitor, which is replaced with the real Coventry GSC chart. T4 ranking ladder for "coventry airport transfers 6.0 / 10.5% CTR".
- "What drove it" should be stated only as what was actually done (get the activity log from the user). Do not invent tactics.

---

## 4. What must be composited in the edit (never generated)
| Element | Videos | Method |
|---|---|---|
| Search Console charts, totals, query tables | 1, 2, 3, 8, 9, 14, 15 | Real screenshots/recordings: draw-on (T3), push-in (T2), keyed over green |
| GBP calls / interactions chart | 1, 3, 4, 12 | Real screenshot with split screen (T7) |
| Old vs new website | 4, (1) | Real captures (Playwright) with a wipe (T1) |
| Google search results page / map pack | 3, 8, H3 | Real screen recording of a live search (dated, location noted); never a generated SERP |
| Map pin drop | 5, 12 | Built in the edit from neutral map tiles |
| Notifications, voice-note waveform, query chips, data cards | 9, 1, all | Built in the edit |
| Any name, logo, number plate, signage | all | Added in the edit if needed; blurred or absent in generation |

## 5. Generation prompt add-ons that support these ideas (for the Seedance prompt writer)
- "Filmed on an iPhone front camera held at arm's length, slight handheld wobble, natural auto-exposure, light sensor grain, no cinematic depth effects."
- "Laptop screen is a plain, evenly lit bright green with four small black dots in the corners, no interface, no text, no reflections." Or: "laptop screen turned away from camera; only its cool glow on her face."
- "No subtitles, no on-screen text, no logos, no readable signs or number plates, no background music; natural room tone only."
- For each clip, generate a 0.5 s hand-pass or swipe at the in/out points so T6 cuts are clean.
