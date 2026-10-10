# Oktrum reels — production brief

Three vertical Instagram reels (1080×1920, 30 fps, 20–25 s each) for **Oktrum** (oktrum.com), an
international multi-asset brokerage: Forex, Stocks, Commodities, Indices, Crypto on MetaTrader 5.
The goal is lead generation and views on Instagram. The look is cinematic SaaS motion graphics: dark
backgrounds, glass/"liquid glass" UI, glowing 3D objects, kinetic typography that mixes a bold sans
with a high-contrast italic serif, light rays, bloom, film grain and motion blur.

## Brand (taken from oktrum.com CSS)

| token | hex | use |
|---|---|---|
| violet | `#8465F4` | gradient start, accents |
| blue | `#5170FF` | primary brand blue (logo dots) |
| cyan | `#81D4E6` | gradient end, highlights, glows |
| bg void | `#000000` | |
| bg deep | `#07091A` | main background (deep navy-black) |
| up / green | `#34D399` | price up |
| down / red | `#F87171` | price down |

Brand gradient: 135°, violet → cyan. Glows: blue/violet/cyan at about 45 % alpha.
Fonts: Inter Tight (headlines, 700–900), Inter (UI), JetBrains Mono (prices), Instrument Serif Italic
(cinematic accent words). Logo: a halftone dot-sphere mark (blue dots, larger on the lit upper-right side,
fading to tiny dots at the left/bottom limb) plus the "Oktrum" wordmark in a violet→cyan gradient (Montserrat-like geometric sans).

## Layout

```
oktrum/
  pipeline/          code (python). Run everything from here.
  workspace/         (git-ignored) src/, fonts/, assets/<name>/NNN.png, sfx/, music/, tts/, out/
  reels/             final deliverables
```
`REEL_WORKDIR` overrides the workspace path. `workspace/assets/logo_*.png` and
`workspace/logo_contours.json` (wordmark outline, normalised so height = 1, centred) already exist.

## Reels (working titles)

1. **The hidden cost** — spreads from 0.2 pips, ultra-low latency MT5 execution, zero hidden commissions. CTA: comment "TRADE".
2. **One account. Every market.** — gold, bitcoin, NVIDIA, EUR/USD; 5 asset classes; MT5 on all devices; 40+ countries, 22/5 support. CTA: comment "MARKETS".
3. **Trade without fear** — crash hook, negative balance protection, segregated funds, bank-tier encryption, 50 % bonus on $500+ deposits. CTA: comment "BONUS".

Every reel ends with the logo, CTA and a small risk warning.
