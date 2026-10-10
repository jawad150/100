# Oktrum kit: shared widgets for the three reel timelines

`oktrum_kit.py` part A applies the Oktrum profile on import (looks incl. `'cine'`, type / ui overrides, colours
`OK.BLUE VIOLET CYAN NAVY UP DOWN BLUE_DEEP UP_DEEP DOWN_DEEP INK IVORY`, fonts `OK.FONT_*`, `OK.ink(look)`).
Part B, documented here, is the widgets the three reels share. Every widget is a pure function of its arguments
and `t`. Static parts are cached.

```python
import oktrum_kit as OK                      # first import of every Oktrum module (applies the profile)
from oktrum_kit import K, T, ui, F, S3
```

Self-test: `nice -n 10 python3 oktrum_kit.py selftest [widgets|looks]` writes stills and timings to
`workspace_oktrum/out/kit/` (`kit_*.png` and `kit_report.json`).

Which reel uses what: reel1 night neon uses `dot_sphere`, `asset_tag` on `ui.orbit_ring`, `ticker_tape`, `candles`
and `trade_window`. reel2 `'cine'` uses `blink`, `candles`, `line_chart`, `trade_window`, `order_toast`, `streaks`
and `light_rays`. reel3 light (`'airy'`) uses `candles(crash=...)`, `asset_tag`, `dot_sphere(look='airy')` and
`ticker_tape`.

## API (one example each)

| widget | example | returns |
|---|---|---|
| `dot_sphere(cv, cam, center, radius, t, rot=(-14, 0, -8), spin=12, assemble=1, n=2600, dot=0.30, light=(.45, .32, -.83), back=0.22, look, glow=1, tint=0.35, core=0.8, opacity=1, dof=True)` | `OK.dot_sphere(cv, cam, (0, -120, 0), 330, t, assemble=K.ramp(t, 0.2, 1.6, 'linear'))` | draws in place, returns `dict(xy, r, bbox)` (screen centre / radius) |
| `candles(n=28, w=900, h=560, progress=1, t=0, seed=7, crash=0, look, price=67200, vol=.004, trend=.3, axis=True, drop=0, grid=4, glow=1, tick=1, info=False)` | `K.draw(cv, OK.candles(28, 900, 560, K.ramp(t, .3, 2, 'linear'), t, look='cine'), 540, 900)` | writable sprite `(h + 2*PAD + drop, w + 2*PAD)`; `info=True` returns `(spr, dict(last, tip, price))` |
| `ticker_tape(cv, t, y=1500, items=None, speed=110, look, plane=None, h=88, size=32, w=None, fade=None, opacity=1)` | `OK.ticker_tape(cv, t, 1560, look='neon')`; 3D: `plane=dict(cam=cam, center=(0, 420, 120), width=1600, rot=(8, -24, -7))` | draws in place |
| `line_chart(w=900, h=420, values=None, progress=1, look, color=None, fill=.30, glow=1, width=4, dot=True, smooth=8, seed=5)` | `K.draw(cv, OK.line_chart(900, 420, None, K.ramp(t, .5, 2.5, 'inout_sine'), 'cine'), 540, 1100)` | read-only sprite `(h + 2*PAD, w + 2*PAD)` |
| `trade_window(pair='BTC/USD', bid=67180, ask=67200, lot=0.5, look, w=760, h=720, chart='line'/'candles'/None, hover=0, press=0, which='buy', sub, change=2.34)` | `win = OK.trade_window(look='cine', hover=hv, press=pr); win.plane(cv, cam, P, 760, rot=(6, -12, 0))` | `ui.Panel`; `win.meta['buy' / 'sell' / 'chart'] = (x, y, w, h)` in card px |
| `order_toast(text='Order Filled — BUY 0.5 BTC @ 67,200', look, w=760)` | `OK.order_toast(look='cine').draw(cv, 540, 1240 + 40 * (1 - u), opacity=u)` | `ui.Panel` |
| `asset_tag(label, price=None, change=None, look, color=None, size=32, h=80)` | `ui.orbit_ring(cv, cam, [OK.asset_tag(*r, look='neon', size=26, h=64) for r in OK.TICKERS[:6]], phase=t * .05, radius=(440, 440), look='neon', mid=lambda c: OK.dot_sphere(c, cam, (0, 0, 0), 300, t))` | `ui.Panel` (also `tag.draw(cv, x, y)`, `tag.plane(...)`) |
| `blink(cv, u, color=None, soft=1, rim=0.08, meet=0.55)` | `OK.blink(cv, K.remap(t, 0.6, 1.3))`, after the scene and before `K.post` | in place. `OK.blink_closure(u)` gives the closure 0..1 |
| `streaks(cv, points, strength=1, color=None, length=560, thickness=7, wide=0.35)` | `OK.streaks(cv, [(820, 640, 1.0), (300, 1210, 0.5)], strength=K.impulse(t, 2.1, 5))` | in place, emissive |
| `light_rays(cv, origin, strength=0.6, t=0, color=None, length=1100, angle=90, cone=360, n=18, seed=0)` | `OK.light_rays(cv, (760, 380), 0.5, t, angle=120, cone=110)` | in place, emissive |

Constants: `OK.TICKERS` (INTAKE.md section 3 ticker rows as `(label, price_str, change_pct)`), `OK.PAD = 40` (the
padding around chart sprites; the plot box starts at `(PAD, PAD)`).

## Measured cost

Single process, 1 sample, warm caches, `nice -n 10`, with a Blender job sharing the 4 cores (from
`kit_report.json`):

| call | ms |
|---|---|
| dot_sphere n=2600 (assembled / assemble 0.5, cloud fills the frame) | 25 / 57 |
| dot_sphere n=6000 dot=0.22 | 33 |
| candles 28 (build / crash) per frame | 20 / 24 |
| ticker_tape 2D / plane | 8 / 14 |
| line_chart (new progress value; same value is a cache hit) | 36 |
| trade_window new hover/press state (base cached) / first base | 16 / 10 |
| trade_window.draw 2D (frost + shadow) | 50 |
| order_toast.draw | 22 |
| asset_tag build (cached after) | 1 |
| ui.orbit_ring 6 asset_tags + dot_sphere in mid | 105-155 |
| light_rays (length 1100) | 43 |
| streaks x3 | 13 |
| blink (only on blink frames; scales with how much lid covers the frame) | 40-95 |
| full look frame: background + sphere + candle card + tape + 2 tags + post | neon 437, cine 296, airy 204 |

## Gotchas

- **dot_sphere on dark looks is pure light** (alpha 0, additive). It never hides what is behind it, and drawn after
  a glass card it adds light on top of the card. Draw it before the cards, or depth-sort it with
  `sc.custom(center, lambda c, cm: OK.dot_sphere(c, cm, center, R, t))`. On `'airy'` it is flat BLUE paint like
  the logo (back dots hidden). The poster's fine particle look is `n=6000, dot=0.22`. The default is the logo's
  coarse halftone. The neon backdrop is bright behind the sphere, so `K.background(..., intensity=0.6)` gets the
  poster's black void.
- dot_sphere `assemble < 1` spreads the dots over the whole frame (cost 57 ms, bokeh from the camera DOF on near
  dots). Use `opacity` for a fade, because `assemble=0` is a fully visible cloud.
- `candles` reserves one empty slot on the right for the crash candle, so the layout does not jump when the crash
  starts. With `drop > 0` the sprite is taller, so anchor on the plot: `anchor=(0.5, (PAD + h/2) / spr.shape[0])`.
  The crash tag price is clamped at 0. `info=True` returns `tip` (crash candle bottom, sprite px) for a camera that
  follows the crash (reel3). On the light look it uses UP_DEEP / DOWN_DEEP bodies and white text on the tag
  (BRAND.md contrast). The series is seeded, and `trend` > 0 rises. The newest candle wiggles with `t`
  (`tick=0` freezes it).
- Ticker prices are strings. Only EUR/USD, BTC/USD and XAU/USD carry figures from the site. The other rows are
  illustrative UI values: never present them as live quotes. Pass your own `items` for a beat about one market.
- `trade_window` / `line_chart` are cached in a byte-budgeted LRU (`OKTRUM_KIT_CACHE_MB`, default 160 MB per
  worker). `hover` / `press` are quantised to 1/12 and line `progress` to 1/400. Animate the press with
  `K.impulse` and add `ui.click_ring` / `ui.draw_cursor` yourself. The BUY / SELL labels are INK on UP / DOWN
  (white on UP / DOWN fails contrast) and white on the deep colours on the light look.
- `order_toast` splits the title from the detail at `' — '` (em dash, as in the verified copy). It colours the
  first detail word BUY / SELL.
- `blink` covers the whole frame (it is meant to). The lids are closed for `u` in 0.40..0.52: tick the price /
  swap the shot there. It sets alpha to 1. Call it before `K.post` so grain and vignette sit on the lids.
- `streaks` / `light_rays` are emissive and bloom in `K.post`. Keep strength <= 1 or the cine bloom turns them into
  a flash. They are local by design. The cine look's own `K.post` anamorphic pass also streaks very bright pixels
  (e.g. a hovered BUY button), so don't stack `OK.streaks` on the same spot.
- Asset tags on `ui.orbit_ring` at 1080 px wide: keep `radius <= 440` with `size=26, h=64`, or the side tags
  leave the frame.
- Fonts: labels Inter SemiBold (`OK.FONT_UI`), figures JetBrains Mono (ui aliases `'mono'`, `'mono_bold'`,
  `'mono_reg'`). Arrows ▲▼ are drawn as triangles, not glyphs.
