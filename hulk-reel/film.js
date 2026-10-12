// Hulk Marketing: "Marketing with muscle". A pure function of time: window.seek(t) paints frame t.
// Timing is in beats (u) on the measured grid (128 bpm, 0.469 s); docs/shotlist.md is the plan.
//
// One character carries the film, as in the reference: the green dot. It breaks out of a grid of
// grey dots, bounces through what the agency does (as the full stop of each word), flexes and wipes
// the frame green on the drop, lands on real work, climbs the brand's promise, draws the H icon,
// and ends as the full stop of "Anything but ordinary."
import * as M from './lib/motion.js';

const { W, H, E, TAU, prog, lerp, clamp, springU, springKeys, SPRING, wobble, ring, font, layout, glyph,
  text, fill, cover, rrect, shake, noise1, fitSize } = M;

// Brand tokens (assets/brand.json + the logo's own green). One accent: the green.
const C = {
  forest: '#111A16',   // site dark canvas
  ink: '#20392E',      // site headline ink
  cream: '#F4F2E9',    // site paper
  green: '#9DEF69',    // --brand / the logo's green
  grey: '#C3C8BA',     // the "ordinary" dots: a muted step of the cream/ink ramp
  black: '#0B0F0D',    // the logo's black
};
const D = 'Display', UI = 'UI';     // Inter Tight (site headline face), Hanken Grotesk (site UI face)
const CX = 540;

// Every visual accent: [beat, label, sfx, opts]. sfx.mjs voices each one on its frame.
const HITS = [
  [0, 'grid ripples in + "Most brands"', 'thud+tick', { pitch: 140, to: 60, gain: 0.5 }],
  [0.25, 'grid ripple', 'type', { n: 8, len: 0.45, gain: 0.12 }],
  [1, '"blend in."', 'click', { gain: 0.25 }],
  [2, 'one dot turns green', 'blip+pop', { pitch: 'F6', gain: 0.32 }],
  [3, 'dot crouches', 'boing', { pitch: 120, to: 70, len: 0.4, gain: 0.25 }],
  [3.5, 'dot leaps', 'whoosh', { len: 0.45, from: 500, to: 2600, gain: 0.25 }],
  [4, 'STRATEGY + flip', 'tok', { pitch: 'F5', gain: 0.4 }],
  [5, 'CREATIVE + flip', 'tok', { pitch: 'Ab5', gain: 0.4, pan: 0.2 }],
  [6, 'DIGITAL + flip', 'tok', { pitch: 'C6', gain: 0.4, pan: -0.2 }],
  [7, 'AI + flip', 'tok', { pitch: 'Eb6', gain: 0.45 }],
  [8, 'dot lands centre, pump 1', 'thud+boing', { pitch: 110, to: 160, len: 0.35, gain: 0.35 }],
  [9, 'pump 2', 'boing', { pitch: 140, to: 220, len: 0.35, gain: 0.3 }],
  [10, 'pump 3', 'boing', { pitch: 180, to: 300, len: 0.35, gain: 0.32 }],
  [11.6, 'squeeze', 'swell', { len: 0.4, gain: 0.25 }],
  [11.98, 'burst fills the frame', 'riser', { len: 1.6, gain: 0.3 }],
  [12, 'HULK OUT: green wipe + "Marketing"', 'impact', { gain: 0.8 }],
  [13, '"with"', 'thud', { pitch: 160, to: 70, gain: 0.4 }],
  [14, '"MUSCLE."', 'thud+sub', { pitch: 120, to: 45, len: 0.6, gain: 0.55 }],
  [14.75, 'MUSCLE flexes', 'boing', { pitch: 90, to: 150, len: 0.4, gain: 0.2 }],
  [15.6, 'field collapses into a card', 'whoosh', { len: 0.5, from: 2600, to: 500, gain: 0.25 }],
  [16, 'Habibi Manchester photo', 'click', { gain: 0.3 }],
  [17, 'Bodyrade card', 'whoosh+click', { len: 0.35, from: 700, to: 2800, pan: 0.4, gain: 0.25 }],
  [18, 'POS Jaquar card', 'whoosh+click', { len: 0.35, from: 700, to: 2800, pan: -0.4, gain: 0.25 }],
  [19, 'dot drops on the stack', 'tok', { pitch: 'C6', gain: 0.35 }],
  [19.5, 'cards fall away', 'whoosh', { len: 0.4, from: 1800, to: 300, gain: 0.2 }],
  [20, 'NOTICE.', 'blip+tok', { pitch: 'F5', gain: 0.35 }],
  [21, 'CHOOSE.', 'blip+tok', { pitch: 'C6', gain: 0.35 }],
  [22, 'COME BACK.', 'blip+tok', { pitch: 'F6', gain: 0.38 }],
  [23, 'arrow shoots', 'whoosh', { len: 0.4, from: 600, to: 4200, gain: 0.3, pan: 0.3 }],
  [24, 'field flips, dot falls in', 'whoosh', { len: 0.25, from: 2400, to: 600, gain: 0.15 }],
  [24.25, 'dot lands, starts drawing the H', 'thud', { pitch: 150, to: 60, gain: 0.45 }],
  [24.4, 'stroke drawing', 'type', { n: 6, len: 0.5, gain: 0.1 }],
  [25, 'icon floods green, H slams', 'impact', { gain: 0.5 }],
  [26, 'wordmark wipes on', 'whoosh', { len: 0.4, from: 900, to: 3600, gain: 0.22 }],
  [27, '® pops', 'bell', { pitch: 'C7', gain: 0.25 }],
  [28, 'end card: "Anything but"', 'impact', { gain: 0.55 }],
  [28.75, 'dot lands as the full stop', 'tok+pop', { pitch: 'F5', gain: 0.38 }],
  [29.25, 'CTA pill', 'pop+click', { pitch: 'C6', gain: 0.5 }],
  [29.75, 'URL', 'blip+click', { pitch: 'F6', gain: 0.3 }],
];

// ------------------------------------------------------------------ helpers
const frac = (x) => x - Math.floor(x);
const arcY = (p, h) => -h * 4 * p * (1 - p);

// The dot. sx/sy squash about its own centre; `ringed` gives it an ink outline on light fields.
function dot(ctx, x, y, r, { sx = 1, sy = 1, color = C.green, ringed = false } = {}) {
  if (r < 0.5) return;
  ctx.save();
  ctx.translate(x, y); ctx.scale(sx, sy);
  ctx.beginPath(); ctx.arc(0, 0, r, 0, TAU);
  ctx.fillStyle = color; ctx.fill();
  if (ringed) { ctx.lineWidth = Math.max(3, r * 0.16); ctx.strokeStyle = C.ink; ctx.stroke(); }
  ctx.restore();
}
// A dot that lands on a floor at beat L: squash-and-settle after contact, stretch just before.
// Returns {x, y, sx, sy} for a dot whose bottom touches floorY.
function landed(u, L, r) {
  const s = u >= L ? 0.42 * wobble(u - L, 2.6, 5.5) : -0.18 * clamp(1 - (L - u) / 0.18);
  const sy = 1 - s, sx = 1 + s * 0.8;
  return { sx, sy, dy: -r * sy };
}

// Per-glyph rise under a mask; returns the layout.
function riseText(ctx, str, x, base, f, color, u, u0, { track = 0, stagger = 0.03, cfg = SPRING.snappy, align = 'center', skew = 0 } = {}) {
  const L = layout(ctx, str, f, track);
  const x0 = align === 'center' ? x - L.width / 2 : x;
  ctx.save();
  ctx.beginPath(); ctx.rect(0, base - L.asc - 60, W, L.asc + L.desc + 80); ctx.clip();
  L.glyphs.forEach((g, j) => {
    const k = springU(u, u0 + j * stagger, cfg);
    if (k <= 0) return;
    glyph(ctx, g.ch, x0 + g.cx, base + (1 - k) * (L.asc + L.desc + 50), f, color, 1, 1, 0, skew);
  });
  ctx.restore();
  return L;
}
// Whole-word slam: drops from 1.6x to 1x with a snappy spring, scaled about its centre.
function slamText(ctx, str, x, base, f, color, u, u0, { track = 0, sx = 1, sy = 1, skew = 0 } = {}) {
  const k = springU(u, u0, SPRING.snappy);
  if (k <= 0) return null;
  const L = layout(ctx, str, f, track);
  const s = lerp(1.6, 1, k);
  ctx.save();
  ctx.translate(x, base - L.asc / 2); ctx.scale(s * sx, s * sy); ctx.translate(-x, -(base - L.asc / 2));
  L.glyphs.forEach((g) => glyph(ctx, g.ch, x - L.width / 2 + g.cx, base, f, color, 1, 1, 0, skew));
  ctx.restore();
  return L;
}

// The site's ↗ arrow as two strokes.
function arrow(ctx, x0, y0, x1, y1, w, color, head) {
  ctx.save();
  ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.lineWidth = w; ctx.strokeStyle = color;
  ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x1, y1); ctx.stroke();
  if (head > 0) { ctx.beginPath(); ctx.moveTo(x1 - head, y1); ctx.lineTo(x1, y1); ctx.lineTo(x1, y1 + head); ctx.stroke(); }
  ctx.restore();
}

// The site's ✳: eight spokes.
function asterisk(ctx, x, y, r, rot, color, w) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot);
  ctx.lineCap = 'butt'; ctx.lineWidth = w; ctx.strokeStyle = color;
  for (let i = 0; i < 4; i++) {
    const a = (i * Math.PI) / 4;
    ctx.beginPath(); ctx.moveTo(-r * Math.cos(a), -r * Math.sin(a)); ctx.lineTo(r * Math.cos(a), r * Math.sin(a)); ctx.stroke();
  }
  ctx.restore();
}

// ------------------------------------------------------------------ logo (vector-traced from the site's PNG)
const LOGO = { w: 500, h: 76, green: null, dark: null, reg: null };
async function loadLogo() {
  const j = await fetch('assets/logo/logo_paths.json').then((r) => r.json());
  LOGO.w = j.w; LOGO.h = j.h;
  LOGO.green = new Path2D(j.green);
  const subs = j.dark.split(/(?=M)/).map((s) => s.trim()).filter(Boolean);
  const firstX = (s) => parseFloat(s.slice(1));
  LOGO.dark = new Path2D(subs.filter((s) => firstX(s) < 470).join(' '));
  LOGO.reg = new Path2D(subs.filter((s) => firstX(s) >= 470).join(' '));
}
// Wordmark centred at (x, y) with the given width. reveal 0..1 wipes it on left to right.
function wordmark(ctx, x, y, w, { reveal = 1, regK = 1 } = {}) {
  if (!LOGO.green || reveal <= 0) return;
  const s = w / LOGO.w, h = LOGO.h * s;
  ctx.save();
  ctx.beginPath(); ctx.rect(x - w / 2 - 4, y - h, (w + 8) * reveal, h * 2); ctx.clip();
  ctx.translate(x - w / 2, y - h / 2); ctx.scale(s, s);
  ctx.fillStyle = C.green; ctx.fill(LOGO.green, 'evenodd');
  ctx.fillStyle = C.black; ctx.fill(LOGO.dark, 'evenodd');
  ctx.lineWidth = 0.6; ctx.strokeStyle = C.black; ctx.stroke(LOGO.dark);
  if (regK > 0) {
    ctx.translate(482, 8); ctx.scale(regK, regK); ctx.translate(-482, -8);
    ctx.fillStyle = C.green; ctx.fill(LOGO.reg, 'evenodd');
  }
  ctx.restore();
}
// The H icon (site favicon): green rounded square, black H knocked out. Proportions measured
// from assets/logo/icon_0.png. flood 0..1 fills the square from its outline inward; hK slams the H.
function iconFill(ctx, x, y, S, { flood = 1, hK = 1 } = {}) {
  const r = S * 0.1, x0 = x - S / 2, y0 = y - S / 2;
  ctx.save();
  rrect(ctx, x0, y0, S, S, r); ctx.fillStyle = C.green; ctx.fill();
  if (flood < 1) {   // the unflooded centre stays forest, shrinking to nothing
    const k = 1 - flood, iw = (S - S * 0.31) * k, ih = (S - S * 0.22) * k;
    rrect(ctx, x - iw / 2, y - ih / 2, iw, ih, r * k); ctx.fillStyle = C.forest; ctx.fill();
  }
  if (hK > 0) {
    const s = lerp(1.5, 1, hK);
    ctx.translate(x, y); ctx.scale(s, s); ctx.translate(-x, -y);
    ctx.fillStyle = C.black;
    const X = (f) => x0 + f * S, Y = (f) => y0 + f * S;
    ctx.fillRect(X(0.155), Y(0.108), S * 0.236, S * 0.82);
    ctx.fillRect(X(0.6), Y(0.108), S * 0.236, S * 0.82);
    ctx.fillRect(X(0.38), Y(0.42), S * 0.24, S * 0.175);
  }
  ctx.restore();
}
// Centre-line of the icon border as a path starting at top-centre, clockwise; point at distance d.
function iconPath(x, y, S, w) {
  const h = S / 2 - w / 2, r = Math.max(2, S * 0.1 - w / 2);
  const segs = [];   // [kind, ...]
  const L = (x0, y0, x1, y1) => segs.push({ k: 'l', x0, y0, x1, y1, len: Math.hypot(x1 - x0, y1 - y0) });
  const A = (cx, cy, a0) => segs.push({ k: 'a', cx, cy, a0, len: (Math.PI / 2) * r });
  L(x, y - h, x + h - r, y - h); A(x + h - r, y - h + r, -Math.PI / 2);
  L(x + h, y - h + r, x + h, y + h - r); A(x + h - r, y + h - r, 0);
  L(x + h - r, y + h, x - h + r, y + h); A(x - h + r, y + h - r, Math.PI / 2);
  L(x - h, y + h - r, x - h, y - h + r); A(x - h + r, y - h + r, Math.PI);
  L(x - h + r, y - h, x, y - h);
  const total = segs.reduce((s, g) => s + g.len, 0);
  const at = (d) => {
    for (const g of segs) {
      if (d <= g.len) {
        const p = d / g.len;
        if (g.k === 'l') return [lerp(g.x0, g.x1, p), lerp(g.y0, g.y1, p)];
        const a = g.a0 + p * Math.PI / 2;
        return [g.cx + r * Math.cos(a), g.cy + r * Math.sin(a)];
      }
      d -= g.len;
    }
    return [x, y - h];
  };
  const trace = (ctx) => {
    ctx.beginPath(); ctx.moveTo(x, y - h);
    ctx.lineTo(x + h - r, y - h); ctx.arcTo(x + h, y - h, x + h, y - h + r, r);
    ctx.lineTo(x + h, y + h - r); ctx.arcTo(x + h, y + h, x + h - r, y + h, r);
    ctx.lineTo(x - h + r, y + h); ctx.arcTo(x - h, y + h, x - h, y + h - r, r);
    ctx.lineTo(x - h, y - h + r); ctx.arcTo(x - h, y - h, x - h + r, y - h, r);
    ctx.closePath();
  };
  return { total, at, trace };
}

// ------------------------------------------------------------------ S1 hook: "Most brands blend in."  (u 0..4)
const G = { cols: 5, rows: 6, sp: 150, rowH: 128, y0: 820, r: 30, hero: [3, 2] };
const gridXY = (c, r) => [CX + (c - 2) * G.sp, G.y0 + r * G.rowH];
const HERO = gridXY(...G.hero);

function drawGrid(ctx, u, { fall = -1, light = true } = {}) {
  for (let r = 0; r < G.rows; r++) for (let c = 0; c < G.cols; c++) {
    if (c === G.hero[0] && r === G.hero[1]) continue;
    const [x, y] = gridXY(c, r);
    const d = Math.hypot(c - G.hero[0], r - G.hero[1]);
    const k = springU(u, -0.45 + d * 0.13, SPRING.bouncy);
    if (k <= 0) continue;
    // the crowd marches in lockstep on every beat from beat 1: everyone the same
    const hop = u > 1 ? -12 * Math.sin(Math.PI * frac(u)) ** 2 : 0;
    let yy = y + hop, rot = 0;
    if (fall >= 0) {
      const t = Math.max(0, u - fall - c * 0.04 - (G.rows - r) * 0.02);
      yy += 2600 * t * t; rot = t;
      if (yy > H + 60) continue;
    }
    dot(ctx, x, yy, G.r * k, { color: light ? C.grey : '#2B3A33' });
  }
}

function sceneHook(ctx, u) {
  fill(ctx, C.cream);
  const f = font(fitSize(ctx, 'Most brands', 900, D, 780, 170, -0.035), 900, D);
  const size = parseInt(f.split(' ')[1]);
  riseText(ctx, 'Most brands', CX, 470, f, C.ink, u, -0.3, { track: -0.035 * size });
  riseText(ctx, 'blend in.', CX, 470 + size * 0.98, f, C.ink, u, 0.85, { track: -0.035 * size });
  // frame 0 opens tight on the crowd and pulls back to reveal it (camera, not a fade)
  const z = lerp(1.9, 1, springU(u, -0.15, { stiffness: 90, damping: 16 }));
  ctx.save();
  ctx.translate(HERO[0], HERO[1]); ctx.scale(z, z); ctx.translate(-HERO[0], -HERO[1]);
  drawGrid(ctx, u, { fall: 3.75 });
  // the hero dot: grey and marching like the rest, then green, then a crouch
  if (u >= 3.5) return;   // it has leapt (drawn by the bounce)
  const [hx, hy] = HERO;
  const k = springU(u, -0.45, SPRING.bouncy);
  const green = u >= 2;
  const hop = u > 1 && u < 2 ? -12 * Math.sin(Math.PI * frac(u)) ** 2 : 0;
  const pop = green ? 8 * springU(u, 2, SPRING.bouncy) : 0;
  const crouch = E.outCubic(prog(u, 3, 3.45));
  const wob = green ? 0.25 * wobble(u - 2, 3, 5) : 0;
  const r = (G.r + pop) * k;
  const sy = 1 - wob - 0.32 * crouch, sx = 1 + wob * 0.8 + 0.22 * crouch;
  dot(ctx, hx, hy + hop + r * (1 - sy), r, { sx, sy, color: green ? C.green : C.grey, ringed: green });
}
function sceneHookCam(ctx, u) { ctx.save(); sceneHook(ctx, u); ctx.restore(); ctx.restore(); }

// ------------------------------------------------------------------ S2 the bounce: STRATEGY. CREATIVE. DIGITAL. AI.  (u 3.5..8)
const WORDS = ['STRATEGY', 'CREATIVE', 'DIGITAL', 'AI'];
const WORD_BASE = 1000;
function wordGeom(ctx, i) {
  const size = fitSize(ctx, WORDS[i], 900, D, 640, 290, -0.02);   // each word as big as it can go
  const f = font(size, 900, D), r = size * 0.13;
  const L = layout(ctx, WORDS[i], f, -0.02 * size);
  const gap = size * 0.05, comp = L.width + gap + 2 * r;
  const x0 = CX - comp / 2;
  return { f, size, r, L, x0, px: x0 + L.width + gap + r, py: WORD_BASE - r };
}
// Where the dot is between beats 3.5 and 8 (hero -> four full stops -> centre stage)
function bounceDot(ctx, u) {
  const P = WORDS.map((_, i) => wordGeom(ctx, i));
  if (u < 4) {   // leap out of the grid
    const p = E.inOutCubic(prog(u, 3.5, 4)), q = prog(u, 3.5, 4);
    return { x: lerp(HERO[0], P[0].px, p), y: lerp(HERO[1], P[0].py, q) + arcY(q, 420), r: lerp(G.r + 8, P[0].r, p), L: 4 };
  }
  const i = Math.min(3, Math.floor(u - 4));
  const a = P[i];
  if (i < 3 && frac(u) >= 0.45) {   // hop to the next word's full stop
    const b = P[i + 1], q = prog(frac(u), 0.45, 1);
    return { x: lerp(a.px, b.px, E.inOutCubic(q)), y: lerp(a.py, b.py, q) + arcY(q, 260), r: lerp(a.r, b.r, q), L: 5 + i };
  }
  if (u >= 7.5) {   // to centre stage for the flex
    const q = prog(u, 7.5, 8);
    return { x: lerp(a.px, CX, E.inOutCubic(q)), y: lerp(a.py, FLEX_Y, q) + arcY(q, 300), r: lerp(a.r, 30, q), L: 8 };
  }
  return { x: a.px, y: a.py, r: a.r, L: 4 + i };
}

function sceneBounce(ctx, u) {
  const i = Math.floor(u - 4);
  const light = i % 2 === 1;
  fill(ctx, light ? C.cream : C.forest);
  if (u < 5) drawGrid(ctx, u, { fall: 3.75, light: false });
  const g = wordGeom(ctx, i);
  // each word rises into place on its beat, its first glyphs already moving just before
  riseText(ctx, WORDS[i], g.x0, WORD_BASE, g.f, light ? C.ink : C.cream, u, 4 + i - 0.04, { track: -0.02 * g.size, align: 'left', stagger: 0.016, cfg: { stiffness: 520, damping: 32 } });
  // tiny index label: 01..04, the site's numbered-list voice
  text(ctx, `0${i + 1} / 04`, CX, WORD_BASE + 110, font(34, 600, UI), light ? C.ink : C.green, 'center', 4);
  const d = bounceDot(ctx, u);
  const lnd = landed(u, d.L, d.r);
  const onFloor = u >= d.L - 0.001 || frac(u) < 0.45;
  dot(ctx, d.x, d.y + (onFloor ? d.r + lnd.dy : 0), d.r, { sx: onFloor ? lnd.sx : 1, sy: onFloor ? lnd.sy : 1, ringed: light });
}

// ------------------------------------------------------------------ S3 the flex  (u 8..12)
const FLEX_Y = 900;
function sceneFlex(ctx, u) {
  fill(ctx, C.forest);
  // three pumps, each bigger, then a squeeze and the burst
  let R = springKeys(u, [[7.9, 30], [8, 80], [9, 135], [10, 195]], SPRING.wobbly);
  let sq = 0;
  for (const b of [8, 9, 10]) sq += 0.22 * wobble(u - b, 2.4, 4);
  if (u >= 11) R = lerp(R, 46, E.inOutCubic(prog(u, 11, 11.6)));
  const burst = E.inCubic(prog(u, 11.62, 12));
  if (burst > 0) R = lerp(46, 1250, burst);
  // shockwave rings off each pump (thin, green, expanding)
  for (const b of [8, 9, 10]) {
    const p = prog(u, b, b + 0.9);
    if (p <= 0 || p >= 1) continue;
    const rr = springKeys(b + 0.001, [[7.9, 30], [8, 80], [9, 135], [10, 195]], SPRING.wobbly);
    ctx.save();
    ctx.beginPath(); ctx.arc(CX, FLEX_Y, rr * 0.9 + 420 * E.outCubic(p), 0, TAU);
    ctx.lineWidth = 10 * (1 - p); ctx.strokeStyle = C.green; ctx.globalAlpha = 1 - p; ctx.stroke();
    ctx.restore();
  }
  // tension tremble before the squeeze
  const tr = 9 * prog(u, 10.2, 11.5) * (1 - burst);
  const jx = tr * noise1(u * 46, 4), jy = tr * noise1(u * 46, 7);
  dot(ctx, CX + jx, FLEX_Y + jy, R, { sx: 1 + sq * 0.8, sy: 1 - sq });
  // caption: the flex counter, small and quiet
  if (u < 11.6) {
    const n = Math.min(3, Math.floor(u - 8) + 1);
    const k = springU(u, Math.floor(u), SPRING.bouncy);
    ctx.save(); ctx.globalAlpha = clamp(k);
    text(ctx, `REP ${n}`, CX, FLEX_Y + 340, font(44, 700, UI), C.green, 'center', 10);
    ctx.restore();
  }
}

// ------------------------------------------------------------------ S4 drop: "Marketing with MUSCLE."  (u 12..16)
const CARD0 = { x: CX, y: 900, w: 760, h: 500 };
function muscleText(ctx, u) {
  // the block sits centred while it's two words, and makes room as MUSCLE. arrives
  const lift = springKeys(u, [[11, 150], [13.85, 0]], SPRING.snappy);
  ctx.save(); ctx.translate(0, lift);
  const f1 = font(fitSize(ctx, 'Marketing', 900, D, 760, 200, -0.04), 900, D);
  const s1 = parseInt(f1.split(' ')[1]);
  slamText(ctx, 'Marketing', CX, 760, f1, C.forest, u, 11.9, { track: -0.04 * s1 });
  const f2 = font(150, 300, D);
  slamText(ctx, 'with', CX, 905, f2, C.forest, u, 12.9, { track: -3, skew: 0.18 });
  const f3 = font(fitSize(ctx, 'MUSCLE.', 900, D, 780, 260, -0.03), 900, D);
  const s3 = parseInt(f3.split(' ')[1]);
  // the flex: MUSCLE. bulges wide twice, like a bicep
  const flex = 0.1 * ring(u - 14.6, 1.4, 1.6) + 0.06 * Math.max(0, wobble(u - 14, 2.5, 6));
  slamText(ctx, 'MUSCLE.', CX, 905 + s3 * 1.02, f3, C.forest, u, 13.9, { track: -0.03 * s3, sx: 1 + flex, sy: 1 - flex * 0.6 });
  ctx.restore();
}
function sceneMuscle(ctx, u) {
  fill(ctx, C.forest);
  ctx.save();
  shake(ctx, u, 12, 34, 3, 0.18);
  shake(ctx, u, 14, 26, 5, 0.15);
  // collapse into the first work card
  const c = E.inOutCubic(prog(u, 15.45, 16));
  const x = lerp(0, CARD0.x - CARD0.w / 2, c), y = lerp(0, CARD0.y - CARD0.h / 2, c);
  const w = lerp(W, CARD0.w, c), h = lerp(H, CARD0.h, c);
  ctx.save();
  rrect(ctx, x, y, w, h, 34 * c); ctx.fillStyle = C.green; ctx.fill(); ctx.clip();
  const s = lerp(1, CARD0.w / W, c);
  ctx.translate(x + w / 2, y + h / 2); ctx.scale(s, s); ctx.translate(-W / 2, -H / 2);
  muscleText(ctx, u);
  ctx.restore();
  ctx.restore();
}

// ------------------------------------------------------------------ S5 the work (real case studies)  (u 16..20)
const CARDS = [
  { img: 'habibi', name: 'Habibi Manchester', w: 760, h: 500, at: 16, from: [CX, CARD0.y, 0], to: [CX, 740, -4] },
  { img: 'bodyrade', name: 'Bodyrade', w: 560, h: 520, at: 17, from: [1500, 1000, 24], to: [590, 995, 4] },
  { img: 'jaquar', name: 'POS Jaquar', w: 780, h: 440, at: 18, from: [-520, 1225, -22], to: [520, 1228, -2.5] },
];
function card(ctx, IMG, cd, u, dim, fallT) {
  const k = cd.at === 16 ? springU(u, 16.1, SPRING.gentle) : springU(u, cd.at - 0.12, { stiffness: 210, damping: 19 });
  if (k <= 0 && cd.at !== 16) return;
  let [x, y, rot] = cd.from.map((v, j) => lerp(v, cd.to[j], k));
  if (fallT > 0) { y += 2600 * fallT * fallT; rot += fallT * 40 * (cd.to[2] < 0 ? -1 : 1); }
  ctx.save();
  ctx.translate(x, y); ctx.rotate((rot * Math.PI) / 180);
  // soft contact shadow (depth, not glow)
  ctx.save(); ctx.filter = 'blur(30px)'; ctx.globalAlpha = 0.45; ctx.fillStyle = '#000';
  rrect(ctx, -cd.w / 2 + 10, -cd.h / 2 + 34, cd.w, cd.h, 30); ctx.fill(); ctx.restore();
  rrect(ctx, -cd.w / 2, -cd.h / 2, cd.w, cd.h, 30); ctx.fillStyle = C.green; ctx.fill();
  const im = IMG[cd.img];
  // the first card's photo wipes up through the green it was born from
  const wipe = cd.at === 16 ? E.outCubic(prog(u, 15.95, 16.4)) : 1;
  if (im && wipe > 0) {
    ctx.save();
    ctx.beginPath(); ctx.rect(-cd.w / 2, cd.h / 2 - cd.h * wipe, cd.w, cd.h * wipe); ctx.clip();
    cover(ctx, im, -cd.w / 2, -cd.h / 2, cd.w, cd.h, { radius: 30, zoom: 1.04 + 0.03 * prog(u, cd.at, 20) });
    ctx.restore();
  }
  // name pill
  const pk = springU(u, cd.at + 0.3, SPRING.bouncy);
  if (pk > 0) {
    const f = font(34, 600, UI);
    ctx.font = f; const tw = ctx.measureText(cd.name).width;
    const pw = tw + 60, ph = 66, px = -cd.w / 2 + 26, py = cd.h / 2 - 26 - ph;
    ctx.save(); ctx.translate(px, py + ph); ctx.scale(pk, pk); ctx.translate(-px, -(py + ph));
    rrect(ctx, px, py, pw, ph, 30); ctx.fillStyle = C.cream; ctx.fill();
    ctx.beginPath(); ctx.arc(px + 24, py + ph / 2, 7, 0, TAU); ctx.fillStyle = C.green; ctx.fill();
    text(ctx, cd.name, px + 42, py + ph / 2 + 12, f, C.ink);
    ctx.restore();
  }
  if (dim > 0) { rrect(ctx, -cd.w / 2, -cd.h / 2, cd.w, cd.h, 30); ctx.fillStyle = `rgba(17,26,22,${0.5 * dim})`; ctx.fill(); }
  ctx.restore();
}
const STAIR = { xs: [290, 540, 790], w: 190, base: 1385, hs: [250, 470, 690] };
function sceneWork(ctx, u, IMG) {
  fill(ctx, C.forest);
  // header
  riseText(ctx, 'DIFFERENT WORLDS.', CX, 305, font(36, 700, UI), C.green, u, 16.1, { track: 6, stagger: 0.012 });
  const fh = font(fitSize(ctx, 'Same restless ambition.', 800, D, 760, 80, -0.03), 800, D);
  riseText(ctx, 'Same restless ambition.', CX, 395, fh, C.cream, u, 16.35, { track: -2, stagger: 0.015 });
  // the stack pushes in slowly
  ctx.save();
  const z = 1 + 0.05 * E.inOutCubic(prog(u, 16, 20));
  ctx.translate(CX, 960); ctx.scale(z, z); ctx.translate(-CX, -960);
  CARDS.forEach((cd, i) => {
    const next = CARDS[i + 1];
    const dim = next ? clamp(springU(u, next.at, SPRING.gentle)) : 0;
    const fallT = Math.max(0, u - 19.45 - i * 0.07) * 1.6;
    card(ctx, IMG, cd, u, dim, fallT);
  });
  ctx.restore();
  // the dot drops onto the front card, then hops to the first stair
  if (u >= 18.5) {
    const top = CARDS[2].to[1] - CARDS[2].h / 2, r = 26, x = 640;
    if (u < 19) {
      const q = prog(u, 18.5, 19);
      dot(ctx, x, lerp(-60, top - r, E.inQuad(q)), r, { sy: 1 + 0.2 * q, sx: 1 - 0.1 * q });
    } else if (u < 19.5) {
      const l = landed(u, 19, r);
      dot(ctx, x, top + l.dy, r, { sx: l.sx, sy: l.sy });
    } else {
      const q = prog(u, 19.5, 20);
      dot(ctx, lerp(x, STAIR.xs[0], E.inOutCubic(q)), lerp(top - r, STAIR.base - r, q) + arcY(q, 260), r);
    }
  }
}

// ------------------------------------------------------------------ S6 the promise: notice, choose, come back  (u 20..24)
const LABELS = ['NOTICE.', 'CHOOSE.', 'COME BACK.'];
// bar 0 lifts the dot on beat 20; bars 1 and 2 rise while the dot is in the air and catch it on the beat
function stairTop(u, i) { return STAIR.base - STAIR.hs[i] * Math.max(0, springU(u, i === 0 ? 19.98 : 20 + i - 0.42, SPRING.bouncy)); }
function sceneStairs(ctx, u) {
  fill(ctx, C.cream);
  const fh = font(fitSize(ctx, 'Brands people…', 900, D, 760, 150, -0.035), 900, D);
  const sh = parseInt(fh.split(' ')[1]);
  riseText(ctx, 'Brands people…', CX, 420, fh, C.ink, u, 19.85, { track: -0.035 * sh, stagger: 0.02 });
  for (let i = 0; i < 3; i++) {
    const top = stairTop(u, i);
    if (top >= STAIR.base - 1) continue;
    ctx.save();
    ctx.beginPath(); ctx.roundRect(STAIR.xs[i] - STAIR.w / 2, top, STAIR.w, STAIR.base - top, [24, 24, 0, 0]);
    ctx.fillStyle = C.ink; ctx.fill();
    ctx.restore();
    riseText(ctx, LABELS[i], STAIR.xs[i], STAIR.base + 62, font(35, 700, UI), C.ink, u, 20 + i, { track: 1.5, stagger: 0.01 });
  }
  // baseline rule
  ctx.fillStyle = C.ink; ctx.fillRect(STAIR.xs[0] - STAIR.w / 2 - 20, STAIR.base, STAIR.xs[2] - STAIR.xs[0] + STAIR.w + 40, 4);
  // the arrow: the site's ↗, shot out of the top step
  const ap = E.outExpo(prog(u, 23, 23.45));
  if (ap > 0) {
    const x0 = STAIR.xs[2] - 40, y0 = STAIR.base - STAIR.hs[2] - 70;
    const x1 = lerp(x0, 915, ap), y1 = lerp(y0, 470, ap);
    arrow(ctx, x0, y0, x1, y1, 26, C.ink, 110 * prog(ap, 0.5, 1));
  }
  // the dot climbs, riding each step as it springs up
  const r = 26;
  let x, y, sx = 1, sy = 1;
  if (u < 22.5 && frac(u) < 0.5) {
    const i = Math.min(2, Math.floor(u - 20));
    const l = landed(u, 20 + i, r);
    x = STAIR.xs[i]; y = stairTop(u, i) + l.dy; sx = l.sx; sy = l.sy;
  } else if (u < 22.5) {
    const i = Math.floor(u - 20), q = prog(frac(u), 0.5, 1);
    x = lerp(STAIR.xs[i], STAIR.xs[i + 1], E.inOutCubic(q));
    y = lerp(stairTop(u, i), stairTop(u, i + 1), q) - r + arcY(q, 200);
  } else if (u < 23) {
    const l = landed(u, 22, r);
    x = STAIR.xs[2]; y = stairTop(u, 2) + l.dy; sx = l.sx; sy = l.sy;
  } else {   // rides the arrow out of frame
    const q = E.inCubic(prog(u, 23.05, 23.7));
    x = lerp(STAIR.xs[2], 1250, q); y = lerp(STAIR.base - STAIR.hs[2] - r, -120, q);
  }
  dot(ctx, x, y, r, { sx, sy, ringed: true });
}

// ------------------------------------------------------------------ S7 the dot becomes the logo  (u 24..28)
const ICON = { x: CX, y: 860, S: 300 };
function lockup(u) {
  // icon + wordmark positions: build (24-26), lockup (26-28), end card (28+)
  const a = E.inOutCubic(prog(u, 25.55, 26.15)), b = E.inOutCubic(prog(u, 27.6, 28.1));
  return {
    ix: CX, iy: lerp(lerp(ICON.y, 700, a), 455, b), S: lerp(lerp(ICON.S, 190, a), 136, b),
    wy: lerp(905, 615, b), ww: lerp(780, 620, b),
  };
}
function sceneLogo(ctx, u) {
  fill(ctx, C.forest);
  const Lk = lockup(u);
  const w = Lk.S * 0.155, r = w / 2;
  if (u < 25) {
    const path = iconPath(ICON.x, ICON.y, ICON.S, w);
    const top = ICON.y - ICON.S / 2;
    if (u < 24.4) {   // falls in from the top and lands where the border starts
      const q = prog(u, 24, 24.25);
      if (u < 24.25) dot(ctx, ICON.x, lerp(330, top + w / 2, E.inQuad(q)), r * 1.12, { sx: 0.88, sy: 1.18 });
      else { const l = landed(u, 24.25, r * 1.12); dot(ctx, ICON.x, top + w / 2 + r * 1.12 + l.dy, r * 1.12, { sx: l.sx, sy: l.sy }); }
    } else {          // the dot is the pen: it draws the border, clockwise
      const p = E.inOutCubic(prog(u, 24.4, 24.97));
      const d = path.total * p;
      ctx.save();
      path.trace(ctx); ctx.setLineDash([d, path.total + 10]);
      ctx.lineWidth = w; ctx.strokeStyle = C.green; ctx.lineCap = 'round'; ctx.stroke();
      ctx.restore();
      const [px, py] = path.at(d);
      dot(ctx, px, py, r * 1.12);
    }
  } else {
    ctx.save();
    shake(ctx, u, 25, 18, 8, 0.12);
    const flood = E.outCubic(prog(u, 25, 25.22));
    const hK = springU(u, 25.24, SPRING.snappy);
    const pump = 1 + 0.06 * wobble(u - 25.2, 2.2, 5) + 0.05 * Math.max(0, wobble(u - 27, 2.5, 6));
    iconFill(ctx, Lk.ix, Lk.iy, Lk.S * pump, { flood, hK });
    ctx.restore();
  }
  // wordmark wipes on with a green leading edge
  const rv = E.inOutCubic(prog(u, 26, 26.8));
  if (rv > 0) {
    const slide = 40 * (1 - rv);
    wordmark(ctx, CX - slide, Lk.wy, Lk.ww, { reveal: rv, regK: springU(u, 27, SPRING.bouncy) });
    if (rv < 1) {
      const ex = CX - slide - Lk.ww / 2 + (Lk.ww + 8) * rv, h = Lk.ww * LOGO.h / LOGO.w;
      ctx.fillStyle = C.green; ctx.fillRect(ex - 2, Lk.wy - h * 0.75, 10, h * 1.5);
    }
  }
}

// ------------------------------------------------------------------ S8 end card  (u 28..32)
function sceneEnd(ctx, u) {
  sceneLogo(ctx, u);   // the lockup keeps living at the top
  const f1 = font(fitSize(ctx, 'Anything but', 900, D, 720, 140, -0.035), 900, D);
  const s1 = parseInt(f1.split(' ')[1]);
  riseText(ctx, 'Anything but', CX, 880, f1, C.cream, u, 27.9, { track: -0.035 * s1, stagger: 0.018 });
  // "ordinary." set light and slanted, like the site's italic; the dot is its full stop, the ✳ beside it
  const f2 = font(s1 * 1.08, 300, D);
  const L2 = layout(ctx, 'ordinary', f2, -0.03 * s1);
  const rD = s1 * 0.12, gap = s1 * 0.06, astR = s1 * 0.3;
  const comp = L2.width + gap + 2 * rD + s1 * 0.35 + 2 * astR;
  const x0 = CX - comp / 2, base2 = 880 + s1 * 1.08;
  riseText(ctx, 'ordinary', x0, base2, f2, C.cream, u, 28.15, { track: -0.03 * s1, stagger: 0.018, align: 'left', skew: 0.2 });
  const pX = x0 + L2.width + gap + rD, pY = base2 - rD;
  // the dot pops out of the icon and lands as the full stop
  const Lk = lockup(u);
  if (u < 28.75) {
    const q = prog(u, 28.2, 28.75);
    if (q > 0) dot(ctx, lerp(Lk.ix, pX, E.inOutCubic(q)), lerp(Lk.iy, pY, q) + arcY(q, 360), lerp(10, rD, q));
  } else {
    const l = landed(u, 28.75, rD);
    dot(ctx, pX, pY + rD + l.dy, rD, { sx: l.sx, sy: l.sy });
  }
  const ak = springU(u, 28.7, SPRING.bouncy);
  if (ak > 0) asterisk(ctx, pX + rD + s1 * 0.35 + astR, base2 - s1 * 0.38, astR * ak, (1 - ak) * Math.PI + (u - 28.7) * 0.35, C.green, s1 * 0.075);
  // CTA pill
  const pk = springU(u, 29.15, SPRING.bouncy);
  if (pk > 0) {
    const f = font(40, 600, UI), label = 'Let’s make your next move';
    ctx.font = f; const tw = ctx.measureText(label).width;
    const pw = tw + 150, ph = 112, px = CX - pw / 2, py = 1180;
    ctx.save(); ctx.translate(CX, py + ph / 2); ctx.scale(pk, pk); ctx.translate(-CX, -(py + ph / 2));
    rrect(ctx, px, py, pw, ph, ph / 2); ctx.fillStyle = C.green; ctx.fill();
    text(ctx, label, px + 48, py + ph / 2 + 14, f, C.forest);
    const ax = px + pw - 62, ay = py + ph / 2, al = 15;
    ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.lineWidth = 5; ctx.strokeStyle = C.forest;
    ctx.beginPath(); ctx.moveTo(ax - al, ay + al); ctx.lineTo(ax + al, ay - al); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(ax - al * 0.6, ay - al); ctx.lineTo(ax + al, ay - al); ctx.lineTo(ax + al, ay + al * 0.6); ctx.stroke();
    ctx.restore();
  }
  riseText(ctx, 'hulkmarketing.co.uk', CX, 1370, font(34, 500, UI), C.cream, u, 29.7, { track: 1, stagger: 0.008 });
}

M.film({
  fonts: [font(100, 900, D), font(100, 300, D), font(100, 800, D), font(40, 700, UI), font(40, 600, UI), font(40, 500, UI)],
  images: { habibi: 'assets/work/habibi.jpg', bodyrade: 'assets/work/bodyrade.jpg', jaquar: 'assets/work/jaquar.jpg' },
  hits: HITS,
  async init() { await loadLogo(); },
  draw(ctx, u, t, IMG) {
    if (u < 3.5) sceneHookCam(ctx, u);
    else if (u < 4) { sceneHookCam(ctx, Math.min(u, 3.999)); const d = bounceDot(ctx, u); dotAir(ctx, d); }
    else if (u < 8) sceneBounce(ctx, u);
    else if (u < 12) sceneFlex(ctx, u);
    else if (u < 16) sceneMuscle(ctx, u);
    else if (u < 20) sceneWork(ctx, u, IMG);
    else if (u < 24) sceneStairs(ctx, u);
    else if (u < 28) sceneLogo(ctx, u);
    else sceneEnd(ctx, u);
  },
});

// The leap out of the grid draws the dot in flight over the hook (the hero spot is now empty).
function dotAir(ctx, d) {
  // cover the hero's grid slot: it has left
  dot(ctx, d.x, d.y, d.r, { sx: 0.88, sy: 1.14, ringed: true });
}
