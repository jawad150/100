# Oktrum reels: producer intake

Source of truth for every agent until `BRIEF.md` exists. Written by the lead (producer) session.

## 1. The ask (client: JAWAD, for the brand Oktrum, https://www.oktrum.com)
- 3 Instagram reels for **business and leads** (views + lead generation), 9:16, 1080x1920, 30 fps.
- **Maximum 20-25 s each.** A hook that stops the scroll in the **first 3 s**.
- Look: premium **SaaS motion graphics**, "top-notch, smooth, like After Effects", cinematic, different effects.
  3D elements rendered in **Blender**. Glass/"liquid glass" UI, UI/UX kit mockups, kinetic typography.
- Audio: **ElevenLabs voiceover** (generated on Higgsfield by another session, delivered as files into
  `media/oktrum/vo/`), **sound design from the SFX library** (toolkit `audio.py` catalog) **and music**
  (procedural score; there is no AI music source available here).
- Use the Oktrum logo and colour scheme from the site. Content decided from the site. Benchmark XM, FxPro,
  Exness, Binance.
- Commit a short storyboard with each reel.

## 2. Brand tokens (from oktrum.com CSS and logo; brand-kit-builder confirms)
| role | hex | note |
|---|---|---|
| primary blue | #5170FF | buttons, key glows |
| violet | #8465F4 | logo gradient start |
| cyan | #81D4E6 | logo gradient end |
| extra blues | #6180FF #4A65FF #3A55E0 #81AAFF | hovers / highlights |
| brand gradient | 135 deg violet #8465F4 -> cyan #81D4E6 | the wordmark gradient |
| background | #000000, #07091A (navy black) | site is dark |
| glass card | white 4 % fill, border rgba(129,212,230,.12) | site cards |
| up / down | #34D399 / #F87171 | tickers, P&L |
| fonts | Inter Tight (display), Inter (body/UI), a mono for tickers | site |
| logo | `workspace_oktrum/intake/site/logo.png` (1563 px, transparent): halftone blue dot sphere + "Oktrum" wordmark in a violet->cyan gradient (geometric sans, Montserrat-like) | never recolour or re-typeset the wordmark |
| site hero art | `workspace_oktrum/intake/site/poster.jpg`: particle dot sphere/torus, neon cyan-blue rings, candlesticks, particle waves, grid floor | the brand's visual world |

Creative addition (lead's call, matches the references): an editorial **serif italic accent** for single emphasised
words (Instrument Serif Italic, Google Fonts), mixed with Inter Tight. Use it sparingly (one word per beat).

## 3. Verified copy (oktrum.com home page, fetched 2026-10-10). Use exactly; nothing else may be claimed.
- Title: "Trade the Global Markets with Confidence"; hero: "Trade the Global Markets with Precision"
- "Forex · Commodities · Stocks · Indices · Crypto"
- "Equities at Your Fingertips" - "Apple, Tesla, NVIDIA — global stocks with institutional execution"
- "Real Markets. Real Value." - "Gold. Silver. Crude oil. Natural gas. Trade the commodities that move the world."
- "Powered by MetaTrader 5" - "The world's most advanced trading platform — built for serious traders";
  MetaTrader 5 on Windows, macOS, iOS and Android
- "Borderless Market Entry" - "Connect to the world's leading financial hubs through a single, intuitive interface"
- "High-Velocity Execution" - "Ultra-low latency. Instantaneous order filling. Seize every opportunity."
  / "Leverage ultra-low latency server architecture for instantaneous order filling. Eliminate lag and seize every
  market opportunity."
- "Elite Security Standards" - "Bank-tier encryption. Regulated infrastructure. Negative balance protection."
  / "Trade with total peace of mind on a fully regulated platform backed by bank-tier encryption and negative
  balance protection."
- "Negative Balance Protection" - "Your account can never go below zero"
- "0.2 PIPS" "Min spread"; "22/5 Expert support"; "0% Hidden commissions"; "Zero Hidden Fees"; "40+ Countries";
  "EST. 2014 · GLOBAL BROKERAGE"; "10+ Years"
- Badges: "PCI DSS Compliant", "Bank-Tier Encryption", "Negative Balance Protection"
- Platform bullets: "Maximize Execution Speed", "Access Institutional Liquidity", "Optimized Strategy Management",
  "Deploy Advanced Charting Tools", "Integrated Multi-Asset Dashboard"
- "Trade With Confidence"; "A new era in trading: where bold strategy meets precision technology";
  "Get an easy start with Oktrum now."
- Buttons: "Open Live Account", "Try Demo", "Try Demo Free", "Get Started"
- Site UI elements we may mock up: ticker rows (EUR/USD 1.0847 ▲ +0.12 %, BTC/USD 67,420 ▲ +2.34 %, XAU/USD
  2,338.40 ▼ -0.44 %, AAPL, GBP/USD, ETH/USD, NVDA, S&P 500, USD/JPY, WTI OIL, TSLA, NASDAQ, SOL/USD, DAX 40,
  XAG/USD), and the toast "Order Filled — BUY 0.5 BTC @ 67,200". Prices on screen are illustrative UI, never
  presented as live quotes or results.
- Risk line for every end card (fine print >= 28 px): "Trading involves high risk. You could lose some or all of
  your investment." (the site footer's risk disclosure, shortened)

**Do not claim** (on the site but unverifiable or unsafe in ads): "97.8% positive trade outcomes", "98%
satisfaction", "500+ goals achieved", "Regulated"/"fully regulated" (no regulator is named on the site), "Segregated
funds", the "50% Bonus on $500+ deposit" promo, "1,247 traders active now", testimonials, any profit, return,
win-rate or "guaranteed" language, any millisecond figure.

## 4. Voiceover scripts v1 (locked; files arrive in media/oktrum/vo/, voice A male, voice B female)
- **reel1 (markets):** "Forex. Gold. Bitcoin. Nvidia. All on one platform. Trade forex, commodities, stocks,
  indices and crypto on MetaTrader 5. Spreads from zero point two pips. Zero hidden fees. Oktrum. Trade the global
  markets with precision. Try a free demo today."
- **reel2 (speed):** "Blink... and the price has already moved. In trading, every millisecond counts. Oktrum runs
  on ultra-low-latency servers for instant order filling, on MetaTrader 5. Eliminate lag, and seize every market
  opportunity. Open your live account at oktrum dot com."
- **reel3 (trust):** "What happens if the market crashes overnight? With Oktrum, your account can never go below
  zero. That's negative balance protection, plus bank-tier encryption and expert support. Trade with total peace of
  mind. Oktrum. Trade with confidence. Get started at oktrum dot com."
Each runs about 16-19 s at ElevenLabs ad pace; the reel adds a ~0.3 s pre-roll and a >= 1.5 s settled end card,
so DUR is about 21-24 s. Until the files arrive, plan word timings at ~2.6 words/s with the pauses at full stops.

## 5. Concepts and look matrix (lead's direction; creative-director details it)
| reel | job | look | hook (0-3 s) | signature devices | end CTA |
|---|---|---|---|---|---|
| reel1 "Every market" | multi-asset, one platform | **Night neon** in Oktrum blue/violet/cyan: aurora void, dot grid, halftone dot globe | four word slams on the beat: FOREX / GOLD / BITCOIN / NVIDIA, each with its 3D object (gold bar, coin, chip/ticker) punching in | 3D halftone dot globe (logo mark) with orbiting glass asset tags; ticker ribbon; card tunnel of market cards; MT5 multi-asset dashboard window | "Try Demo Free" |
| reel2 "Blink" | execution speed | **Cinematic dashboard**: navy-black, anamorphic cyan streaks, film grain, light rays (refs 1-2), editorial serif italic accents | an eyelid "blink" wipe over a live candle chart; the price ticks during the blink; "Blink." in serif italic | glass MT5 order window, cursor press on BUY, "Order Filled" toast; 3D glass candlesticks; speed streaks and whip pans; light sweep | "Open Live Account" |
| reel3 "Peace of mind" | trust and safety | **Clean SaaS light** ("follow the object"): ice-white page, faint navy dot grid, violet/cyan depth glows | a red candle crashes down through the frame, the balance counter plunges and **stops at 0.00** as a glass shield slams in | 3D glass shield + lock (Blender); balance counter; feature chips (bank-tier encryption, negative balance protection, 22/5 expert support, PCI DSS compliant); one continuous camera journey | "Get Started" |

No two reels share a signature device or transition family. All three end on the Oktrum logo end card (flat logo
or the 3D dot-sphere mark resolving to yaw 0), CTA button with cursor press, "oktrum.com", the risk line.

## 6. References (stills in `workspace_oktrum/intake/refs/`, the videos themselves are not available)
- ref1_sheet.jpg: cinematic dark, warm practical light, volumetric rays, film grain, anamorphic flares, serif italic
  + small sans pairs ("it may be *frustrating* at start"), footage in rounded glass cards.
- ref2_sheet.jpg: cinematic personal-brand ad: big serif italic words over moody light ("Dreaming", "Good Money",
  "Possible"), glass app UI with glowing buttons, crystal object on white with "WHICH TURNS YOUR VIEWERS INTO
  CUSTOMERS", film-frame borders.
- ref3_sheet.jpg: SaaS motion showreel: glowing blob lights, glossy pills, orbit text round a 3D icon, dark app
  cards with icon rows (Safer / On-Cloud / Chat / Faster) and edge glows, 3D phone and shield, globe with orbiting
  words, extruded 3D type.

## 7. Competitor benchmark (what to borrow as devices, never copy)
- Exness: calm confidence, trust + speed claims, product UI close-ups, bold single-colour type.
- XM: energetic, promo-led, big numbers, fast cuts.
- FxPro: "trade like a pro", dark navy, platform UI and award badges, execution speed.
- Binance: black + one bright brand colour, 3D coins, app UI hero, simple steps and a strong "join" CTA.
Common winning structure: hook (question or bold statement) -> 2-3 proof beats with UI -> brand + CTA + risk line.

## 8. Production rules
- Toolkit rules in TOOLKIT.md and the reels-production-playbook apply (safe zones, sizes, no full-frame flash, motion
  blur never crosses a cut, eased exits, pure `draw(t)`).
- Compute: 4 cores, 15 GB. At most 4 live render workers in total across all agents; Blender counts as one (threads
  2, `nice`). Builders iterate at `--workers 1`.
- Agents commit only their own paths (`git add <paths>`, never `-A`), never fetch, merge or push.
