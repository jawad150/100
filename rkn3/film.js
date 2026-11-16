// RKN Accountancy, "In our clients' words": pure function of time. window.seek(t) paints frame t.
// A light, editorial testimonial film: real Google reviews from RKN's website, quoted verbatim (trimmed
// only, per the brand guide), on warm paper with the solid Deep Bronze logo (the light-background variant).
import * as M from './lib/motion.js';

const { W, H, E, prog, lerp, clamp, springU, SPRING, font, text, hash01, bump, mulberry32, wobble } = M;
const C = { paper: '#FBFAF7', white: '#FFFFFF', charcoal: '#212121', jet: '#111111', grey: '#868686', silver: '#DCDCDE',
  bronze: '#A67226', ink: '#80561A', gold: '#CD9734', champagne: '#FFF4A8' };
const DISPLAY = 'Display', ITALIC = 'DisplayI', UI = 'UI';
const BEAT = 0.5;
const b = (t) => t / BEAT;
const sp = (t, t0, cfg = SPRING.snappy) => springU(b(t), b(t0), cfg);

// the reviews (Google reviews on rkn-accountancy-homepage.vercel.app), trimmed only
const REVIEWS = [
  { q: 'Professional, qualified and down to earth.', hi: 'down to earth.', who: 'Idris Mohammed', t0: 3.4, enter: 'up' },
  { q: '…nothing is too much to ask and staff go above and beyond to keep you informed.', hi: 'above and beyond', who: 'Aliya Khan', t0: 6.9, enter: 'right' },
  { q: 'Took lots of pressure off myself and my partner.', hi: 'pressure off', who: 'Jamie-lee Evans', t0: 10.4, enter: 'flip' },
  { q: 'Put me at ease and took care of everything I needed.', hi: 'took care of everything', who: 'BEDC', t0: 13.9, enter: 'drop' },
  { q: 'Very professional and knowledgeable accountants who actually care…', hi: 'actually care', who: 'Blakewater Cars', t0: 17.4, enter: 'right' },
  { q: '…always makes sure everything is done properly and on time.', hi: 'properly and on time.', who: 'Mohammed', t0: 20.9, enter: 'up' },
];
const DUR = 3.5;

const HITS = [
  [b(0.3), "Don't take", 'thud'],
  [b(1.1), 'our word', 'tick'],
  [b(1.4), 'for it.', 'tick'],
  ...[0, 1, 2, 3, 4].map((i) => [b(2.6 + i * 0.12), `star ${i + 1}`, 'pop', { pitch: ['G5', 'A5', 'B5', 'D6', 'G6'][i] }]),
  ...REVIEWS.map((r, i) => [b(r.t0), `review ${i + 1}: ${r.who}`, i % 2 ? 'whoosh' : 'swell', { len: 0.35 }]),
  ...REVIEWS.map((r, i) => [b(r.t0 + 1.6), `highlight ${i + 1}`, 'click']),
  [b(24.6), 'stack', 'thud'],
  [b(25.0), 'logo', 'bell', { pitch: 'G5' }],
];

// ============================================================ helpers
function paperBg(ctx, IMG) {
  ctx.fillStyle = C.paper; ctx.fillRect(0, 0, W, H);
  if (IMG.tex) { ctx.save(); ctx.globalAlpha = 0.5; ctx.globalCompositeOperation = 'multiply'; ctx.drawImage(IMG.tex, 0, 0, W, H); ctx.restore(); }
  const g = ctx.createRadialGradient(W * 0.5, H * 0.4, H * 0.2, W * 0.5, H * 0.5, H * 0.8);
  g.addColorStop(0, 'rgba(255,255,255,0)'); g.addColorStop(1, 'rgba(120,100,70,0.16)');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
}
// faint open circle, slowly turning: the monogram's ring as a watermark device
function ringMark(ctx, t, cx, cy, R, a) {
  const st = -0.49 + t * 0.06, span = Math.PI * 2 - 0.7;
  ctx.save(); ctx.globalAlpha = a; ctx.strokeStyle = C.bronze; ctx.lineWidth = 3;
  ctx.beginPath(); ctx.arc(cx, cy, R, st, st + span); ctx.stroke(); ctx.restore();
}
function star(ctx, x, y, r, color) {
  ctx.beginPath();
  for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + (i * Math.PI) / 5, rr = i % 2 ? r * 0.45 : r; i ? ctx.lineTo(x + Math.cos(a) * rr, y + Math.sin(a) * rr) : ctx.moveTo(x + Math.cos(a) * rr, y + Math.sin(a) * rr); }
  ctx.closePath(); ctx.fillStyle = color; ctx.fill();
}
// word wrap -> [{w, x, line}] with per-word style flags for the highlight phrase
function wrap(ctx, q, hi, size, maxW) {
  const words = q.split(' ');
  const hiStart = q.indexOf(hi), out = [];
  let x = 0, line = 0, pos = 0;
  for (const w of words) {
    const inHi = pos >= hiStart && pos < hiStart + hi.length;
    const f = inHi ? font(size * 1.05, 500, ITALIC) : font(size, 500, DISPLAY);
    ctx.font = f; const ww = ctx.measureText(w + ' ').width, wl = ctx.measureText(w).width;
    if (x + wl > maxW && x > 0) { x = 0; line++; }
    out.push({ w, x, line, f, inHi, wl });
    x += ww; pos += w.length + 1;
  }
  return out;
}

// ============================================================ hook 0-3.4
function hook(ctx, t) {
  const X = 90, s = 150;
  const lines = [[["Don't take", 'r']], [['our word', 'r']], [['for it.', 'i']]];
  const t0s = [0.25, 1.0, 1.35];
  const up = E.inOutCubic(prog(t, 2.4, 3.0)) * 260;
  const out = E.inCubic(prog(t, 3.15, 3.55));
  lines.forEach((ln, i) => {
    const k = sp(t, t0s[i], SPRING.snappy);
    if (k <= 0) return;
    const y = 640 + i * s * 1.02 - up - out * 900;
    ctx.save(); ctx.beginPath(); ctx.rect(0, y - s * 1.0, W, s * 1.35); ctx.clip();
    const [str, st] = ln[0];
    ctx.font = st === 'i' ? font(s * 1.05, 500, ITALIC) : font(s, 500, DISPLAY);
    ctx.fillStyle = st === 'i' ? C.bronze : C.charcoal; ctx.textAlign = 'left';
    ctx.fillText(str, X, y + (1 - k) * s);
    ctx.restore();
  });
  // five stars stamp in with the eyebrow
  for (let i = 0; i < 5; i++) {
    const k = sp(t, 2.6 + i * 0.12, SPRING.bouncy);
    if (k <= 0) continue;
    const x = 90 + 46 + i * 104, y = 1060 - out * 900;
    ctx.save(); ctx.translate(x, y); ctx.scale(k, k); star(ctx, 0, 0, 44, C.bronze); ctx.restore();
  }
  const ek = E.outQuint(prog(t, 2.9, 3.3)) * (1 - out);
  if (ek > 0) { ctx.save(); ctx.globalAlpha = ek; text(ctx, 'IN OUR CLIENTS’ WORDS', 90, 1170 - out * 900, font(30, 600, UI), C.ink, 'left', 7); ctx.restore(); }
}

// ============================================================ review cards
const CARD = { x: 64, w: W - 128, y: 470, h: 980 };
function cardPose(r, t) {
  // enter
  const tIn = r.t0, tOut = r.t0 + DUR;
  let x = 0, y = 0, rot = 0, sx = 1, a = 1;
  const k = sp(t, tIn - 0.05, SPRING.snappy);
  if (r.enter === 'up') { y = (1 - k) * H; rot = (1 - k) * 0.08; }
  if (r.enter === 'right') { x = (1 - k) * W * 1.15; rot = (1 - k) * 0.12; }
  if (r.enter === 'flip') { const f = E.outCubic(prog(t, tIn - 0.1, tIn + 0.35)); sx = Math.max(0.001, f); }
  if (r.enter === 'drop') { const kk = sp(t, tIn - 0.05, SPRING.bouncy); y = (1 - kk) * -H * 0.9; rot = 0.03 + (1 - kk) * -0.2; }
  // exit: the next card's entrance decides how this one leaves
  const nx = REVIEWS[REVIEWS.indexOf(r) + 1];
  const e = nx ? E.inCubic(prog(t, tOut - 0.12, tOut + 0.28)) : 0;
  if (nx && e > 0) {
    if (nx.enter === 'right') { x += -e * W * 1.15; rot += -e * 0.1; }
    if (nx.enter === 'up') { y += -e * H * 0.9; }
    if (nx.enter === 'flip') { sx *= Math.max(0.001, 1 - e * 1.3); }
    if (nx.enter === 'drop') { y += e * 30; rot += e * -0.04; a = 1; }   // stays under the dropped card
  }
  return { x, y, rot, sx, a, visible: t > tIn - 0.4 && t < (nx ? tOut + (nx.enter === 'drop' ? DUR : 0.45) : 24.15) };
}
function reviewCard(ctx, r, i, t) {
  const p = cardPose(r, t);
  if (!p.visible) return;
  const { x: cx0, y: cy0, w, h } = { x: CARD.x, y: CARD.y, w: CARD.w, h: CARD.h };
  ctx.save();
  ctx.translate(W / 2 + p.x, cy0 + h / 2 + p.y); ctx.rotate(p.rot); ctx.scale(p.sx, 1); ctx.translate(-W / 2, -(cy0 + h / 2));
  ctx.globalAlpha = p.a;
  // card: white, silver border, 4 px radius, soft paper shadow
  ctx.shadowColor = 'rgba(60,45,20,0.22)'; ctx.shadowBlur = 60; ctx.shadowOffsetY = 30;
  M.rrect(ctx, cx0, cy0, w, h, 6); ctx.fillStyle = C.white; ctx.fill();
  ctx.shadowColor = 'transparent'; ctx.strokeStyle = C.silver; ctx.lineWidth = 2; ctx.stroke();
  // gold rule at the top edge (graphic language: fine gold rules)
  const g = ctx.createLinearGradient(cx0, 0, cx0 + w, 0); g.addColorStop(0, C.bronze); g.addColorStop(1, C.gold);
  ctx.fillStyle = g; ctx.fillRect(cx0, cy0, w, 8);
  // big opening quote
  ctx.font = font(300, 500, DISPLAY); ctx.fillStyle = 'rgba(166,114,38,0.18)'; ctx.textAlign = 'left';
  ctx.fillText('“', cx0 + 50, cy0 + 260);
  // counter
  text(ctx, `${String(i + 1).padStart(2, '0')} — 06`, cx0 + w - 60, cy0 + 90, font(26, 600, UI), C.grey, 'right', 4);
  // the quote, word by word, then the highlighter sweeps under the key phrase
  const size = r.q.length > 70 ? 86 : 104, lh = size * 1.18, qx = cx0 + 64, qy = cy0 + 330;
  const words = wrap(ctx, r.q, r.hi, size, w - 128);
  const hk = E.inOutCubic(prog(t, r.t0 + 1.55, r.t0 + 2.1));
  // highlighter behind the phrase (champagne: a highlight, never text)
  if (hk > 0) {
    const hw = words.filter((wd) => wd.inHi);
    const byLine = {};
    hw.forEach((wd) => { const L = byLine[wd.line] || (byLine[wd.line] = { x0: wd.x, x1: wd.x + wd.wl }); L.x0 = Math.min(L.x0, wd.x); L.x1 = Math.max(L.x1, wd.x + wd.wl); });
    const lines = Object.entries(byLine);
    const total = lines.reduce((s2, [, L]) => s2 + (L.x1 - L.x0 + 20), 0);
    let acc = total * hk;
    lines.forEach(([ln, L]) => {
      const len = Math.min(L.x1 - L.x0 + 20, Math.max(0, acc)); acc -= L.x1 - L.x0 + 20;
      if (len <= 0) return;
      ctx.fillStyle = 'rgba(255,244,168,0.95)';
      ctx.fillRect(qx + L.x0 - 10, qy + Number(ln) * lh - size * 0.42, len, size * 0.5);
    });
  }
  words.forEach((wd, j) => {
    const k = E.outCubic(prog(t, r.t0 + 0.2 + j * 0.075, r.t0 + 0.55 + j * 0.075));
    if (k <= 0) return;
    ctx.save(); ctx.globalAlpha = p.a * k;
    ctx.font = wd.f; ctx.fillStyle = wd.inHi ? C.ink : C.charcoal; ctx.textAlign = 'left';
    ctx.fillText(wd.w, qx + wd.x, qy + wd.line * lh + (1 - k) * 22);
    ctx.restore();
  });
  // attribution
  const lastLine = words[words.length - 1].line;
  const ay = Math.max(qy + lastLine * lh + 150, cy0 + h - 190);
  const ak = E.outQuint(prog(t, r.t0 + 0.9, r.t0 + 1.4));
  if (ak > 0) {
    ctx.save(); ctx.globalAlpha = p.a * ak;
    ctx.fillStyle = C.silver; ctx.fillRect(qx, ay - 70, w - 128, 2);
    text(ctx, r.who, qx, ay, font(40, 600, UI), C.charcoal, 'left');
    text(ctx, 'Google review', qx, ay + 50, font(28, 500, UI), C.grey, 'left');
    for (let s = 0; s < 5; s++) star(ctx, cx0 + w - 64 - 22 - (4 - s) * 52, ay - 12, 22, C.bronze);
    ctx.restore();
  }
  ctx.restore();
}

// ============================================================ end card 24.6-30
function endCard(ctx, t, IMG) {
  const k = E.inOutCubic(prog(t, 24.5, 25.1));
  if (k <= 0) return;
  const lk = sp(t, 25.0, SPRING.gentle);
  const lw = 620, sc = lw / 712, lh = 474 * sc, lx = (W - lw) / 2, ly = 430;
  if (IMG.logo && lk > 0) {
    ctx.save(); ctx.globalAlpha = clamp(lk); ctx.drawImage(IMG.logo, lx, ly + (1 - lk) * 40, lw, lh); ctx.restore();
  }
  const y0 = ly + lh + 170;
  const line = (str, st, y, t0, size) => {
    const kk = sp(t, t0, SPRING.gentle); if (kk <= 0) return;
    ctx.save(); ctx.beginPath(); ctx.rect(0, y - size, W, size * 1.35); ctx.clip();
    ctx.font = st === 'i' ? font(size * 1.05, 500, ITALIC) : font(size, 500, DISPLAY);
    ctx.fillStyle = st === 'i' ? C.bronze : C.charcoal; ctx.textAlign = 'center';
    ctx.fillText(str, W / 2, y + (1 - kk) * size); ctx.restore();
  };
  line('Personal support.', 'r', y0, 26.4, 96);
  line('In our clients’ words.', 'i', y0 + 112, 27.7, 96);
  const rk = E.outCubic(prog(t, 28.1, 28.6));
  if (rk > 0) { ctx.fillStyle = C.bronze; ctx.fillRect(W / 2 - 75 * rk, y0 + 170, 150 * rk, 4); }
  const ck = E.outQuint(prog(t, 28.2, 28.9));
  if (ck > 0) {
    ctx.save(); ctx.globalAlpha = ck;
    text(ctx, '0161 566 1549', W / 2, y0 + 270 + (1 - ck) * 16, font(54, 600, UI), C.charcoal, 'center', 1);
    text(ctx, 'rknaccountancy.co.uk', W / 2, y0 + 336 + (1 - ck) * 16, font(40, 600, UI), C.ink, 'center', 1);
    text(ctx, 'Millett House, Bury  ·  Mon–Fri 9am–5:30pm', W / 2, y0 + 392 + (1 - ck) * 16, font(29, 500, UI), C.grey, 'center', 1);
    ctx.restore();
  }
}
// the six cards gather into a fanned stack and slide away under the end card
function stackOut(ctx, t) {
  const k = E.inOutCubic(prog(t, 24.1, 24.9));
  if (k <= 0 || t > 25.2) return;
  const a = 1 - prog(t, 24.7, 25.1);
  for (let i = 0; i < 6; i++) {
    ctx.save(); ctx.globalAlpha = a;
    const rot = lerp(0, (i - 2.5) * 0.06, k), s = lerp(1, 0.4, k);
    ctx.translate(W / 2, CARD.y + CARD.h / 2 + k * 700); ctx.rotate(rot); ctx.scale(s, s);
    ctx.shadowColor = 'rgba(60,45,20,0.2)'; ctx.shadowBlur = 40; ctx.shadowOffsetY = 20;
    M.rrect(ctx, -CARD.w / 2, -CARD.h / 2, CARD.w, CARD.h, 6); ctx.fillStyle = C.white; ctx.fill();
    ctx.shadowColor = 'transparent'; ctx.strokeStyle = C.silver; ctx.lineWidth = 2; ctx.stroke();
    ctx.fillStyle = C.bronze; ctx.fillRect(-CARD.w / 2, -CARD.h / 2, CARD.w, 8);
    ctx.restore();
  }
}

// ============================================================ post: light grain + edge warmth
const GRAIN = [];
function makeTextures() {
  for (let k = 0; k < 6; k++) {
    const cv = document.createElement('canvas'); cv.width = 512; cv.height = 512;
    const c = cv.getContext('2d'); const id = c.createImageData(512, 512); const r = mulberry32(500 + k);
    for (let i = 0; i < id.data.length; i += 4) { const v = 128 + (r() - 0.5) * 100; id.data[i] = id.data[i + 1] = id.data[i + 2] = v; id.data[i + 3] = 255; }
    c.putImageData(id, 0, 0); GRAIN.push(cv);
  }
  // paper fibre texture (static)
  const cv = document.createElement('canvas'); cv.width = W; cv.height = H;
  const c = cv.getContext('2d'); c.fillStyle = '#fff'; c.fillRect(0, 0, W, H);
  const r = mulberry32(42);
  for (let i = 0; i < 9000; i++) { c.fillStyle = `rgba(150,130,100,${0.05 * r()})`; c.fillRect(r() * W, r() * H, 1 + r() * 3, 1); }
  return cv;
}
function post(ctx, u, t) {
  const n = Math.floor(t * 24), gr = GRAIN[n % GRAIN.length];
  if (!gr) return;
  ctx.save(); ctx.globalAlpha = 0.05; ctx.globalCompositeOperation = 'overlay';
  ctx.translate(-Math.floor(hash01(n, 3) * 512), -Math.floor(hash01(n, 4) * 512));
  for (let x = 0; x < W + 512; x += 512) for (let y = 0; y < H + 512; y += 512) ctx.drawImage(gr, x, y);
  ctx.restore();
}

// ============================================================ film
let TEX = null;
M.film({
  fonts: [font(100, 500, DISPLAY), font(100, 500, ITALIC), font(40, 600, UI), font(40, 500, UI)],
  images: { logo: 'assets/logo/logo_bronze.png' },
  hits: HITS,
  samples: 4,
  init() { TEX = makeTextures(); },
  draw(ctx, u, t, IMG) {
    IMG.tex = TEX;
    paperBg(ctx, IMG);
    ringMark(ctx, t, W * 0.82, H * 0.16, 360, 0.12);
    if (t < 3.6) hook(ctx, t);
    // draw older cards first so a dropped card lands on top
    REVIEWS.forEach((r, i) => reviewCard(ctx, r, i, t));
    stackOut(ctx, t);
    endCard(ctx, t, IMG);
  },
  post,
});
