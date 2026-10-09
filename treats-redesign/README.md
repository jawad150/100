# Treats Foods: motion redesign concept

This is a pitch redesign of [treatsfoods.co.uk](https://www.treatsfoods.co.uk/). The copy, products, stores and contact details all come from the current site. The visuals and interaction are new. It is a static site with no build step.

![Hero scroll sequence](preview/hero-scroll-sequence.jpg)

## Run it

```bash
cd treats-redesign
npx http-server -p 8080 .   # or any static server, then open http://localhost:8080
```

Opening `index.html` straight from disk also works.

## What's on the page

| Section | Motion |
|---|---|
| Loader | The six lilac letter tiles from the Treats logo drop in, count to 100%, then wipe away. |
| **Hero** | Pinned while you scroll. The product in the centre spins out and the next spins in: Bagel, Croissant, Burger, Finger Roll, Torpedo, Salad. The background colour, the giant outline word, the counter and the list all change with it. A rotating text ring and floating ingredients add parallax. It snaps to each product. |
| Marquee | "Our outlets are open when our customers want them to be" loops forever. It speeds up and skews with scroll speed. |
| About | The statement fills in word by word as you scroll. Stats count up (1978, 20+, 16,000 ft², 3). The Future Vision card shows the 100 / 200 / 2,000 ft² unit sizes as squares that grow in. |
| Products | Pinned horizontal scroll through the six hero products plus a card listing the other 11. On mobile it becomes a native swipe scroller. |
| Sandwich bars / Food | Triangles echo the "distinctive triangular logo" and rotate on scroll. A Treats cup has animated steam. The dish chips pop in. |
| **Factory** | Pinned "exploded burger". The layers fly apart as you scroll, and the factory's production areas (Bakery, Sandwich room / salad, Fryer room, UK supply) light up one by one. |
| Hygiene | The four QC points slide in and their tick marks draw on. |
| Stores | A stylised route line draws on scroll. Station chips filter the 13 store cards. |
| Gallery | Two tilted rows of tiles slide in opposite directions. The tiles carry the gallery's location names. |
| Contact | The phone number rises in letter by letter. Cards for Head Office, Recruitment and Customer Services. |

The whole page also has Lenis smooth scrolling, a cursor with labels, magnetic buttons, a scroll progress bar, a nav that hides as you scroll down and highlights the current section, and a full-screen mobile menu.

## Notes for the pitch

- **Brand colour**: lilac `#866DAF`, sampled from the current logo. The original copy mentions "friendly lilac interiors", so the palette builds on that.
- **Illustrations**: every food item is hand-built inline SVG, so each layer can be animated. The current site's product photos are 89×89 px, too small to reuse. Real photography can go into the gallery tiles once the client supplies it.
- **Copy**: kept as on the live site. Only typos are fixed ("palette" → "palate", "wet their appetites" → "whet their appetites", "operator" → "operators"). The ingredient labels and small UI captions (e.g. "Scroll to taste") are new.
- **Accessibility**: `prefers-reduced-motion` turns off smooth scroll, pins and the loader and shows all content. Without JS the page still reads top to bottom. The custom cursor is off on touch devices.
- **Tested**: Chromium at 1440×900 and 390×844, with no console errors and no horizontal overflow.

## Files

```
index.html        markup + inline SVG illustrations
css/style.css     design tokens, layout, responsive rules
js/main.js        all motion (GSAP 3.12 + ScrollTrigger, Lenis 1.1)
vendor/           GSAP, ScrollTrigger, Lenis (vendored, no CDN needed)
preview/          screenshots for the pitch
```
