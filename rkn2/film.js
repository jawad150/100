// RKN Accountancy, "Behind every business": pure function of time. window.seek(t) paints frame t.
// People film: RKN's own footage (website hero film, frames in assets/frames) + the website's client
// photos. Timed in seconds to the ElevenLabs VO (audio/vo.wav, take A +0.12 s); docs/shotlist.md.
import * as M from './lib/motion.js';

const { W, H, FORMAT, E, prog, lerp, clamp, springU, SPRING, font, layout, text, hash01, bump, mulberry32 } = M;
const P = FORMAT.portrait;
const C = { charcoal: '#212121', jet: '#111111', white: '#FFFFFF', grey: '#868686', gold: '#CD9734', bronze: '#A67226', bright: '#E4BC54', champagne: '#FFF4A8' };
const DISPLAY = 'Display', ITALIC = 'DisplayI', UI = 'UI';
const BEAT = 0.625;                                   // 96 bpm
const b = (t) => t / BEAT;                            // seconds -> beats (for HITS)
const sp = (t, t0, cfg = SPRING.snappy) => springU(b(t), b(t0), cfg);

// [beat, label, sfx, opts], placed on the VO's words
const HITS = [
  [b(0.0), 'open on hands', 'swell', { len: 0.6 }],
  [b(2.45), 'person', 'bell', { pitch: 'F5' }],
  [b(3.75), 'card: sole trader', 'thud'],
  [b(5.1), 'card: growing team', 'thud'],
  [b(6.55), 'card: paperwork', 'thud'],
  [b(9.3), 'ring draws', 'whoosh', { len: 1.2, from: 300, to: 1800 }],
  [b(12.35), 'iris into Millett House', 'impact'],
  [b(14.55), "that's us: door", 'whoosh', { len: 0.4 }],
  [b(15.25), 'A real team', 'click'],
  [b(16.75), 'Qualified', 'click'],
  [b(17.5), 'down to earth', 'click'],
  [b(18.45), 'always reachable', 'click'],
  [b(24.7), 'handshake', 'swell', { len: 0.8 }],
  [b(26.75), 'end card', 'bell', { pitch: 'C6' }],
];

// ============================================================ footage (RKN hero film, frames f0001 = source 2.5 s, 30 fps)
const FPS = 30, SRC0 = 2.5, NFR = 1110;
const fidx = (src) => clamp(Math.round((src - SRC0) * FPS) + 1, 1, NFR);
const cache = new Map();
async function loadFrame(i) {
  if (cache.has(i)) return cache.get(i);
  const p = fetch(`assets/frames/f${String(i).padStart(4, '0')}.jpg`).then((r) => r.blob()).then((bl) => createImageBitmap(bl));
  cache.set(i, p);
  const bmp = await p; cache.set(i, bmp);
  if (cache.size > 48) { const k = cache.keys().next().value; const v = cache.get(k); if (v && v.close) v.close(); cache.delete(k); }
  return bmp;
}
const frameNow = (i) => { const v = cache.get(i); return v && !(v instanceof Promise) ? v : null; };

// clips: source range, playback rate, crop focus (fx) and push-in (z0 -> z1)
const CLIPS = {
  drone:   { s: 3.0, rate: 1.0, fx: 0.48, fy: 0.55, z0: 1.0, z1: 1.12 },
  door:    { s: 7.7, rate: 0.8, fx: 0.47, fy: 0.5, z0: 1.05, z1: 1.15 },
  recept:  { s: 11.6, rate: 0.9, fx: 0.62, fy: 0.5, z0: 1.12, z1: 1.2 },
  meeting: { s: 18.0, rate: 0.9, fx: 0.58, fy: 0.5, z0: 1.0, z1: 1.08 },
  desks:   { s: 22.0, rate: 0.9, fx: 0.42, fy: 0.55, z0: 1.0, z1: 1.08 },
  office:  { s: 30.0, rate: 0.9, fx: 0.5, fy: 0.55, z0: 1.0, z1: 1.06 },
  lounge:  { s: 25.8, rate: 0.85, fx: 0.62, fy: 0.55, z0: 1.0, z1: 1.1 },
  pair:    { s: 23.2, rate: 0.6, fx: 0.72, fy: 0.5, z0: 1.05, z1: 1.14 },
  shake:   { s: 34.0, rate: 0.85, fx: 0.5, fy: 0.5, z0: 1.0, z1: 1.12 },
};
// the edit: [start, end, clip] (film seconds). Layers overlap where a transition blends them.
const EDIT = [
  [12.2, 14.6, 'drone'],
  [14.55, 15.35, 'door'],
  [15.25, 16.8, 'recept'],
  [16.75, 17.55, 'meeting'],
  [17.5, 18.5, 'desks'],
  [18.45, 20.3, 'office'],
  [19.9, 22.55, 'lounge'],
  [22.3, 24.95, 'pair'],
  [24.7, 30.0, 'shake'],
];
const srcAt = (clip, t, t0) => CLIPS[clip].s + (t - t0) * CLIPS[clip].rate;
function layersAt(t) { return EDIT.filter(([a, e]) => t >= a && t < e); }

// draw a clip full-bleed (vertical crop of 16:9), with grade and a push-in
function drawClip(ctx, clip, t, t0, t1, alpha = 1) {
  const c = CLIPS[clip], img = frameNow(fidx(srcAt(clip, t, t0)));
  if (!img || alpha <= 0) return;
  const z = Math.exp(lerp(Math.log(c.z0), Math.log(c.z1), prog(t, t0, t1)));
  const sh = img.height / z, sw = Math.min(img.width, sh * (W / H));
  const sx = clamp(c.fx * img.width - sw / 2, 0, img.width - sw), sy = clamp(c.fy * img.height - sh / 2, 0, img.height - sh);
  ctx.save(); ctx.globalAlpha = alpha;
  const bl = clip === 'shake' ? 16 * E.inOutCubic(prog(t, 26.2, 27.0)) : 0;
  ctx.filter = `saturate(0.9) contrast(1.06) brightness(0.98)${bl > 0.3 ? ` blur(${bl.toFixed(1)}px)` : ''}`;
  ctx.drawImage(img, sx, sy, sw, sh, 0, 0, W, H);
  ctx.filter = 'none'; ctx.restore();
}

// ============================================================ type
function goldFill(ctx, y, s) {
  const g = ctx.createLinearGradient(0, y - s * 0.8, 0, y + s * 0.15);
  g.addColorStop(0, C.champagne); g.addColorStop(0.45, C.bright); g.addColorStop(1, C.gold);
  return g;
}
// words rise from under a mask, per word (this film reads calmer than film 1's per-glyph snap)
function line(ctx, parts, x, y, size, t, t0, t1, opts = {}) {
  if (t < t0 - 0.05 || t > t1 + 0.5) return;
  const exit = E.inCubic(prog(t, t1, t1 + 0.35));
  const items = []; let cx = 0;
  for (const [str, st] of parts) {
    for (const w of str.split(/(?<= )/)) {
      const f = st === 'i' ? font(size * 1.04, 500, ITALIC) : font(size, 500, DISPLAY);
      ctx.font = f; const wd = ctx.measureText(w).width;
      items.push({ w, st, f, x: cx }); cx += wd;
    }
  }
  const dx = opts.align === 'center' ? -cx / 2 : 0;
  ctx.save(); ctx.beginPath(); ctx.rect(0, y - size * 1.1, W, size * 1.45); ctx.clip();
  items.forEach((it, i) => {
    const k = sp(t, t0 + i * (opts.stagger ?? 0.07), SPRING.gentle);
    if (k <= 0) return;
    const yy = y + (1 - k) * size * 1.05 - exit * size * 1.2;
    ctx.font = it.f; ctx.textAlign = 'left';
    if (opts.shadow !== false) { ctx.shadowColor = 'rgba(0,0,0,0.55)'; ctx.shadowBlur = size * 0.35; ctx.shadowOffsetY = size * 0.04; }
    ctx.fillStyle = it.st === 'i' ? goldFill(ctx, yy, size) : (opts.color || C.white);
    ctx.fillText(it.w, x + dx + it.x, yy);
  });
  ctx.restore();
}
function eyebrow(ctx, str, x, y, t, t0, t1, align = 'left', size = 26, color = C.bright) {
  const k = E.outQuint(prog(t, t0, t0 + 0.45)) * (1 - prog(t, t1, t1 + 0.3));
  if (k <= 0) return;
  ctx.save(); ctx.globalAlpha = k;
  ctx.font = font(size, 600, UI); ctx.letterSpacing = `${size * 0.22}px`;
  const w = ctx.measureText(str).width, x0 = align === 'center' ? x - w / 2 : x;
  ctx.beginPath(); ctx.rect(x0 - 4, y - size * 1.2, (w + 8) * k, size * 1.6); ctx.clip();
  ctx.shadowColor = 'rgba(0,0,0,0.6)'; ctx.shadowBlur = 10;
  ctx.fillStyle = color; ctx.textAlign = 'left'; ctx.fillText(str, x0, y);
  ctx.letterSpacing = '0px'; ctx.restore();
}
function goldRule(ctx, x, y, w, k, align = 'left') {
  if (k <= 0) return;
  const ww = w * k, x0 = align === 'center' ? x - ww / 2 : x;
  const g = ctx.createLinearGradient(x0, 0, x0 + ww, 0);
  g.addColorStop(0, C.bronze); g.addColorStop(0.6, C.bright); g.addColorStop(1, C.champagne);
  ctx.fillStyle = g; ctx.fillRect(x0, y, ww, 4);
}
// charcoal gradients behind type (brand: 60-75% charcoal behind gold/white type on photography)
function scrimBottom(ctx, k, from = 0.55) {
  if (k <= 0) return;
  const g = ctx.createLinearGradient(0, H * from, 0, H);
  g.addColorStop(0, 'rgba(17,17,17,0)'); g.addColorStop(0.45, `rgba(17,17,17,${0.7 * k})`); g.addColorStop(1, `rgba(17,17,17,${0.85 * k})`);
  ctx.fillStyle = g; ctx.fillRect(0, H * from, W, H * (1 - from));
}
function scrimTop(ctx, k, to = 0.4) {
  if (k <= 0) return;
  const g = ctx.createLinearGradient(0, 0, 0, H * to);
  g.addColorStop(0, `rgba(17,17,17,${0.8 * k})`); g.addColorStop(0.55, `rgba(17,17,17,${0.5 * k})`); g.addColorStop(1, 'rgba(17,17,17,0)');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H * to);
}

// ============================================================ backgrounds
function charcoalBg(ctx) {
  const g = ctx.createRadialGradient(W * 0.5, H * 0.42, 0, W * 0.5, H * 0.45, H * 0.75);
  g.addColorStop(0, '#2c2824'); g.addColorStop(0.5, '#1d1c1a'); g.addColorStop(1, '#0e0e0e');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
}

// a photograph as a printed card: 4 px radius, soft contact shadow, slight warm grade
function photoCard(ctx, img, cx, cy, w, h, rot, k, crop = null) {
  if (!img || k <= 0) return;
  ctx.save(); ctx.translate(cx, cy); ctx.rotate(rot); ctx.scale(k, k);
  ctx.shadowColor = 'rgba(0,0,0,0.6)'; ctx.shadowBlur = 50; ctx.shadowOffsetY = 26;
  ctx.fillStyle = '#f4f1ea'; M.rrect(ctx, -w / 2 - 10, -h / 2 - 10, w + 20, h + 20, 6); ctx.fill();
  ctx.shadowColor = 'transparent';
  M.rrect(ctx, -w / 2, -h / 2, w, h, 4); ctx.clip();
  ctx.filter = 'saturate(0.9) contrast(1.04)';
  const [sx, sy, sw, sh] = crop || coverCrop(img, w, h, 0.5, 0.5);
  ctx.drawImage(img, sx, sy, sw, sh, -w / 2, -h / 2, w, h);
  ctx.filter = 'none';
  ctx.restore();
}
function coverCrop(img, w, h, fx, fy, zoom = 1) {
  const s = Math.max(w / img.width, h / img.height) * zoom;
  const sw = w / s, sh = h / s;
  return [clamp(fx * img.width - sw / 2, 0, img.width - sw), clamp(fy * img.height - sh / 2, 0, img.height - sh), sw, sh];
}

// ============================================================ scenes
const X = 84;
// S1 0-3.6: tight on her hands at the laptop, pull out to her face on "person"
function sHook(ctx, t, IMG) {
  const img = IMG.sole; if (!img) return;
  const p = E.inOutCubic(prog(t, 0, 3.0));
  const z = Math.exp(lerp(Math.log(2.3), Math.log(1.0), p));
  const fx = lerp(0.74, 0.5, p), fy = lerp(0.8, 0.5, p);
  const [sx, sy, sw, sh] = coverCrop(img, W, H, fx, fy, z);
  // S1 -> S2: the full-bleed photo shrinks into card 1
  const k = E.inOutCubic(prog(t, 3.45, 4.0));
  if (k > 0) return; // card handles it
  ctx.save(); ctx.filter = 'saturate(0.9) contrast(1.05)';
  ctx.drawImage(img, sx, sy, sw, sh, 0, 0, W, H); ctx.filter = 'none'; ctx.restore();
  scrimTop(ctx, 1, 0.45);
  line(ctx, [['Behind every ', 'r'], ['business...', 'r']], X, 400, 96, t, 0.15, 3.3);
  line(ctx, [["there's a ", 'r'], ['person.', 'i']], X, 520, 108, t, 2.3, 3.3);
}

// S2/S3 3.45-12.5: three photo cards on charcoal, then the ring draws around them
const CARDS = [
  { key: 'sole', label: 'START-UPS & SOLE TRADERS', t0: 3.75, crop: [0.5, 0.42], home: [0.5, 0.215], rot: -0.035, row: [0.22, 0.47] },
  { key: 'team', label: 'OWNER-MANAGED BUSINESSES', t0: 5.1, crop: [0.5, 0.5], home: [0.5, 0.37], rot: 0.03, row: [0.5, 0.47] },
  { key: 'files', label: 'INDIVIDUALS & LANDLORDS', t0: 6.55, crop: [0.55, 0.5], home: [0.5, 0.525], rot: -0.02, row: [0.78, 0.47] },
];
function sCards(ctx, t, IMG) {
  charcoalBg(ctx);
  const fan = E.inOutCubic(prog(t, 8.7, 9.6));           // to a row of three
  const cw = 720, ch = 480;                               // 3:2 cards
  CARDS.forEach((c, i) => {
    const img = IMG[c.key]; if (!img) return;
    let k, cx, cy, w = cw, h = ch, rot = c.rot;
    if (i === 0) {
      // morph from the full-bleed hook photo into card 1
      const m = E.inOutCubic(prog(t, 3.45, 4.05));
      cx = lerp(W / 2, c.home[0] * W, m); cy = lerp(H / 2, c.home[1] * H, m);
      w = lerp(W, cw, m); h = lerp(H, ch, m); rot = lerp(0, c.rot, m); k = 1;
    } else {
      k = sp(t, c.t0 - 0.12, SPRING.snappy);
      const from = i === 1 ? [W * 1.6, H * 0.45] : [-W * 0.6, H * 0.8];
      cx = lerp(from[0], c.home[0] * W, k); cy = lerp(from[1], c.home[1] * H, k); rot = c.rot + (1 - k) * (i === 1 ? 0.4 : -0.4);
      k = k > 0 ? 1 : 0;
    }
    // fan into a row of small portraits inside the ring
    if (fan > 0) {
      cx = lerp(cx, c.row[0] * W, fan); cy = lerp(cy, c.row[1] * H, fan);
      w = lerp(w, 300, fan); h = lerp(h, 400, fan); rot = lerp(rot, 0, fan);
    }
    const crop = coverCrop(img, w, h, c.crop[0], c.crop[1]);
    photoCard(ctx, img, cx, cy, w, h, rot, k, crop);
  });
  // phrase supers, bottom
  const fs = 84, y = H - 400;
  line(ctx, [['The sole ', 'r'], ['trader.', 'i']], X, y, fs, t, 3.75, 4.95);
  line(ctx, [['The growing ', 'r'], ['team.', 'i']], X, y, fs, t, 5.1, 6.4);
  line(ctx, [['The paperwork', 'r']], X, y - fs * 1.1, fs, t, 6.55, 8.6);
  line(ctx, [['that never ', 'r'], ['stops.', 'i']], X, y, fs, t, 6.8, 8.6);
  CARDS.forEach((c) => eyebrow(ctx, c.label, X, y - fs * (c.key === 'files' ? 2.35 : 1.25), t, c.t0, c.t0 + (c.key === 'files' ? 2.0 : 1.2)));
  // S3: the open circle draws around the three portraits
  const rk = E.inOutCubic(prog(t, 9.3, 11.2));
  if (rk > 0) {
    const R = 470, cx = W / 2, cy = H * 0.47;
    ringStroke(ctx, cx, cy, R, rk, 6);
  }
  line(ctx, [['Every one of them deserves', 'r']], W / 2, H * 0.78, 64, t, 9.25, 12.1, { align: 'center' });
  line(ctx, [['someone in their ', 'r'], ['corner.', 'i']], W / 2, H * 0.78 + 84, 76, t, 10.3, 12.1, { align: 'center' });
}
// the open circle: a ring broken at the upper right, drawn on clockwise from the gap
const GAP_A = -68 * Math.PI / 180, GAP_B = -28 * Math.PI / 180;     // canvas angles (y down): gap upper right
function ringStroke(ctx, cx, cy, R, k, lw) {
  const start = GAP_B, span = Math.PI * 2 - (GAP_B - GAP_A);
  const g = ctx.createLinearGradient(cx - R, cy - R, cx + R, cy + R);
  g.addColorStop(0, C.bronze); g.addColorStop(0.5, C.bright); g.addColorStop(1, C.champagne);
  ctx.save(); ctx.strokeStyle = g; ctx.lineWidth = lw; ctx.lineCap = 'round';
  ctx.shadowColor = 'rgba(0,0,0,0.5)'; ctx.shadowBlur = 12;
  ctx.beginPath(); ctx.arc(cx, cy, R, start, start + span * k); ctx.stroke(); ctx.restore();
}

// S4+ footage scenes with transitions
function sFootage(ctx, t) {
  const L = layersAt(t);
  for (const [a, e, clip] of L) {
    let alpha = 1;
    // soft dissolves where the edit overlaps by more than a cut
    if (clip === 'lounge') alpha = E.inOutSine(prog(t, 19.9, 20.3));
    if (clip === 'pair') alpha = E.inOutSine(prog(t, 22.3, 22.55));
    if (clip === 'shake') alpha = E.inOutSine(prog(t, 24.7, 24.95));
    drawClip(ctx, clip, t, a, e, alpha);
  }
}

// gold rule wipe at 14.55 (drone -> door) and the S3 -> S4 ring iris
function irisReveal(ctx, t, IMG) {
  // 12.2-12.6: the ring expands past the frame; inside it, the drone shot
  const k = E.inExpo(prog(t, 12.0, 12.6));
  const R = lerp(470, Math.hypot(W, H) * 0.62, k), cx = W / 2, cy = H * 0.47;
  ctx.save(); ctx.beginPath(); ctx.arc(cx, cy, R, 0, Math.PI * 2); ctx.clip();
  drawClip(ctx, 'drone', t, 12.2, 14.6);
  ctx.restore();
  ringStroke(ctx, cx, cy, R, 1, lerp(6, 18, k));
}

function overlayFootage(ctx, t) {
  // S4 Millett House
  if (t > 12.3 && t < 15.3) {
    scrimBottom(ctx, 1, 0.55);
    eyebrow(ctx, 'MILLETT HOUSE  ·  BURY BL9 0JA', X, H - 600, t, 12.6, 14.9);
    line(ctx, [['At Millett House', 'r']], X, H - 500, 88, t, 12.55, 14.9);
    line(ctx, [['in Bury... ', 'r'], ["that's us.", 'i']], X, H - 395, 88, t, 13.25, 14.9);
    goldRule(ctx, X, H - 350, 160, E.outCubic(prog(t, 14.1, 14.6)) * (1 - prog(t, 14.9, 15.2)));
  }
  // gold wipe line across the drone -> door cut
  const wk = prog(t, 14.45, 14.7);
  if (wk > 0 && wk < 1) { const x = lerp(-40, W + 40, E.inOutCubic(wk)); ctx.fillStyle = C.bright; ctx.fillRect(x, 0, 6, H); }
  // S5 the team: one word per cut
  if (t > 15.2 && t < 20.1) {
    scrimBottom(ctx, 1, 0.6);
    eyebrow(ctx, 'THE TEAM', X, H - 560, t, 15.3, 19.6);
    line(ctx, [['A real ', 'r'], ['team.', 'i']], X, H - 440, 110, t, 15.25, 16.65);
    line(ctx, [['Qualified.', 'r']], X, H - 440, 110, t, 16.78, 17.45);
    line(ctx, [['Down to ', 'r'], ['earth.', 'i']], X, H - 440, 110, t, 17.52, 18.4);
    line(ctx, [['Always ', 'r'], ['reachable.', 'i']], X, H - 440, 110, t, 18.47, 19.7);
  }
  // S6 advice
  if (t > 20.0 && t < 24.8) {
    scrimBottom(ctx, 1, 0.55);
    line(ctx, [['Clear advice,', 'r']], X, H - 560, 92, t, 20.15, 24.4);
    line(ctx, [['in plain ', 'r'], ['English.', 'i']], X, H - 455, 92, t, 20.75, 24.4);
    line(ctx, [['The decision is', 'r']], X, H - 330, 64, t, 22.45, 24.4, { color: 'rgba(255,255,255,0.92)' });
    line(ctx, [['always ', 'r'], ['yours.', 'i']], X, H - 250, 64, t, 23.2, 24.4);
  }
  // S7 brand line
  if (t > 24.9 && t < 27) {
    scrimBottom(ctx, 1, 0.6);
    eyebrow(ctx, 'RKN ACCOUNTANCY', X, H - 440, t, 25.05, 26.5, 'left', 34);
  }
}

// light leak for the 22.3 dissolve and the end card
function lightLeak(ctx, t) {
  const a = bump(t, 22.45, 0.5) * 0.5 + bump(t, 24.85, 0.45) * 0.35;
  if (a <= 0.01) return;
  ctx.save(); ctx.globalCompositeOperation = 'screen';
  const x = lerp(W * 1.1, -W * 0.1, prog(t, 21.9, 25.3)), y = H * 0.35;
  const g = ctx.createRadialGradient(x, y, 0, x, y, H * 0.7);
  g.addColorStop(0, `rgba(255,190,110,${0.75 * a})`); g.addColorStop(0.4, `rgba(205,130,52,${0.35 * a})`); g.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); ctx.restore();
}

// S8 end card over the darkened handshake
const LOGO = { w: 712, h: 474 };
function endCard(ctx, t, IMG) {
  const k = E.inOutCubic(prog(t, 26.3, 27.0));
  if (k <= 0) return;
  ctx.save(); ctx.fillStyle = `rgba(20,20,20,${0.84 * k})`; ctx.fillRect(0, 0, W, H); ctx.restore();
  const lk = E.outCubic(prog(t, 26.55, 27.3));
  const lw = 640, sc = lw / LOGO.w, lx = (W - lw) / 2, ly = H * 0.25;
  if (IMG.logo && lk > 0) {
    ctx.save(); ctx.globalAlpha = lk;
    ctx.drawImage(IMG.logo, lx, ly + (1 - lk) * 24, lw, LOGO.h * sc);
    ctx.restore();
  }
  const y0 = ly + LOGO.h * sc + 150;
  line(ctx, [['Your business. ', 'r'], ['Our focus.', 'i']], W / 2, y0, 92, t, 26.75, 99, { align: 'center', stagger: 0.12 });
  goldRule(ctx, W / 2, y0 + 50, 150, E.outCubic(prog(t, 27.6, 28.2)), 'center');
  const k3 = E.outQuint(prog(t, 27.8, 28.5));
  if (k3 > 0) {
    ctx.save(); ctx.globalAlpha = k3;
    text(ctx, '0161 566 1549', W / 2, y0 + 150 + (1 - k3) * 16, font(52, 600, UI), C.white, 'center', 1);
    text(ctx, 'rknaccountancy.co.uk', W / 2, y0 + 216 + (1 - k3) * 16, font(40, 500, UI), C.bright, 'center', 1);
    text(ctx, 'Millett House, Bury  ·  Mon–Fri 9am–5:30pm', W / 2, y0 + 270 + (1 - k3) * 16, font(29, 500, UI), '#9a9a9a', 'center', 1);
    ctx.restore();
  }
}

// ============================================================ post: vignette + grain
const GRAIN = [];
function makeGrain() {
  for (let k = 0; k < 6; k++) {
    const cv = document.createElement('canvas'); cv.width = 512; cv.height = 512;
    const c = cv.getContext('2d'); const id = c.createImageData(512, 512); const r = mulberry32(300 + k);
    for (let i = 0; i < id.data.length; i += 4) { const v = 128 + (r() - 0.5) * 120; id.data[i] = id.data[i + 1] = id.data[i + 2] = v; id.data[i + 3] = 255; }
    c.putImageData(id, 0, 0); GRAIN.push(cv);
  }
}
function post(ctx, u, t) {
  const g = ctx.createRadialGradient(W / 2, H / 2, Math.min(W, H) * 0.4, W / 2, H / 2, Math.hypot(W, H) * 0.6);
  g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,0.45)');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  const n = Math.floor(t * 24), gr = GRAIN[n % GRAIN.length];
  if (gr) {
    ctx.save(); ctx.globalAlpha = 0.08; ctx.globalCompositeOperation = 'overlay';
    ctx.translate(-Math.floor(hash01(n, 3) * 512), -Math.floor(hash01(n, 4) * 512));
    for (let x = 0; x < W + 512; x += 512) for (let y = 0; y < H + 512; y += 512) ctx.drawImage(gr, x, y);
    ctx.restore();
  }
}

// ============================================================ film
await M.film({
  fonts: [font(100, 500, DISPLAY), font(100, 500, ITALIC), font(40, 600, UI), font(40, 500, UI)],
  images: {
    sole: 'assets/audience-sole-trader-web.jpg', team: 'assets/audience-limited-company-web.jpg',
    files: 'assets/audience-personal-tax-web.jpg', logo: 'assets/logo/logo_full.png',
  },
  hits: HITS,
  samples: 3,
  shutter: 0.5,
  init() { makeGrain(); },
  draw(ctx, u, t, IMG) {
    if (t < 3.45) sHook(ctx, t, IMG);
    else if (t < 12.6) sCards(ctx, t, IMG);
    if (t >= 12.0 && t < 12.6) irisReveal(ctx, t, IMG);
    if (t >= 12.6) sFootage(ctx, t);
    lightLeak(ctx, t);
    overlayFootage(ctx, t);
    endCard(ctx, t, IMG);
  },
  post,
});

// frames load asynchronously: before each seek, fetch every footage frame the sub-samples will need
const seekSync = window.seek;
window.seek = async (t) => {
  const need = new Set();
  for (const dt of [0, 0.5 / 30, 1 / 30]) {
    const tt = t + dt;
    for (const [a, , clip] of layersAt(tt)) need.add(fidx(srcAt(clip, tt, a)));
    if (tt >= 12.0 && tt < 12.6) need.add(fidx(srcAt('drone', tt, 12.2)));
  }
  await Promise.all([...need].map(loadFrame));
  seekSync(t);
};
