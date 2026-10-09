---
name: motion-web-design
description: Design and motion system for scroll-driven marketing websites (GSAP + ScrollTrigger + Lenis, SVG illustration). Use when building or editing the Treats redesign or any motion-heavy landing page - hero object swaps on scroll, pinned sections, horizontal product scrollers, kinetic type, magnetic UI.
---

# Motion web design

## Stack
- GSAP 3.12 + ScrollTrigger (vendored in `treats-redesign/vendor/`), Lenis 1.1 for smooth scroll.
- Plain HTML/CSS/JS, no build step. Fonts: Bricolage Grotesque (display), DM Sans (body).
- Food is drawn as inline SVG so every layer can be animated (see `.hero__products` and `.xburger`).

## Design tokens (Treats)
| Token | Value | Use |
|---|---|---|
| `--lilac` | #866DAF | Brand colour, sampled from the original logo |
| `--ink` | #1E1430 | Dark sections, text |
| `--cream` | #FFF7EC | Page background |
| `--cheese` | #F7C534 | Accent, highlights, CTAs on dark |
| `--tomato` / `--leaf` / `--crust` | #E5533D / #6FB04A / #E39A3E | Ingredient colours |

The logo motif is a row of six lilac letter tiles (T R E A T S). Reuse it for the loader, header and footer.

## Motion patterns in use
1. **Hero object swap**: pin the hero, one label per product, scrub 0.8, `snap: { snapTo: "labels", inertia: false }`. Outgoing object spins out, incoming spins in with `back.out`, background colour and the giant outline word change with it.
2. **Word-fill statement**: split into words, scrub opacity from 0.14 to 1.
3. **Horizontal product track**: pin, then translate the track by `scrollWidth - innerWidth`. Child tweens use `containerAnimation`.
4. **Exploded build**: SVG layers fly apart on scroll, and a list of facts lights up in step with them.
5. **Line draw**: `strokeDasharray = getTotalLength()`, scrub the offset to 0.
6. **Velocity marquee**: infinite xPercent loop. Scroll velocity changes its timeScale and skew.
7. **Micro-interactions**: a cursor that grows with a label on `[data-cursor]`, and `.magnetic` buttons that use `quickTo` with elastic easing.

## Rules
- Animate transform and opacity only. Use `will-change` sparingly.
- Under `prefers-reduced-motion`: no Lenis, no pins, no loader, and all content visible.
- Touch devices get no custom cursor. The product track becomes a native swipe scroller below 860px.
- Test at 1440x900 and 390x844. Check for no horizontal overflow and no console errors.
