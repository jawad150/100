// kit.js: Hulk Marketing brand kit for the film. Colours from hulkmarketing.co.uk (dark theme), type, and the
// reference reel's UI vocabulary: title block (lime rule + caps + typed lime italic with a caret), glass pills,
// cards, counter pill, spinner, tick badge, cursor and vector icons. Everything is a pure function of time.
import { E, clamp, lerp, prog, spring, mix, TAU, hash01 } from '../lib/motion.js';

export const C = {
  bg: '#0A0B0A', forest: '#111A16', raised: '#121412', raised2: '#1B1E1B', line: '#22261F',
  lime: '#9DEF69', limeGlow: '#78E930', limeDeep: '#2A5C0A',
  ink: '#F2F6EE', muted: '#9AA398', dim: '#646F60',
  grid: '#18201A', red: '#E0695C',
};
export const SAFE = { x0: 60, x1: 960, y0: 270, y1: 1240 };

export const F = {
  caps: (s) => `800 ${s}px Display`,
  accent: (s) => `italic 600 ${s}px Accent`,
  ui: (s, w = 600) => `${w} ${s}px UI`,
};
export const CAPS_TRACK = 0.012;   // em

const SP = { snappy: { stiffness: 380, damping: 30 }, ui: { stiffness: 300, damping: 22 }, pop: { stiffness: 420, damping: 18 } };
export const sp = (t, cfg = 'snappy') => spring(t, SP[cfg] || cfg);

export function rr(ctx, x, y, w, h, r) {
  ctx.beginPath(); ctx.roundRect(x, y, w, h, Math.max(0, Math.min(r, w / 2, h / 2)));
}

// ------------------------------------------------------------------ text measuring (cached)
const mcache = new Map();
export function measure(ctx, str, font, track = 0) {
  const k = `${font}|${track}|${str}`;
  if (mcache.has(k)) return mcache.get(k);
  ctx.save(); ctx.font = font; ctx.letterSpacing = `${track}px`;
  const m = ctx.measureText(str);
  ctx.restore();
  const r = { w: m.width - (str.length ? track : 0), asc: m.actualBoundingBoxAscent, desc: m.actualBoundingBoxDescent };
  mcache.set(k, r);
  return r;
}
export function txt(ctx, str, x, y, font, color, align = 'left', track = 0, alpha = 1) {
  if (alpha <= 0) return;
  ctx.save(); ctx.globalAlpha *= alpha; ctx.font = font; ctx.fillStyle = color; ctx.textAlign = align;
  ctx.letterSpacing = `${track}px`; ctx.fillText(str, x, y); ctx.restore();
}

// ------------------------------------------------------------------ title block (the reference's signature)
// lines: [[seg, ...], ...], seg = { t: 'TEXT ', a: false } caps, or { t: 'word.', a: true, at: s, dur: s } accent
// opts: { t0, out, cx, top, size, maxW, align, rule }
export function title(ctx, t, lines, o) {
  const size0 = o.size || 74, maxW = o.maxW || 2 * (SAFE.x1 - (o.cx ?? 540));
  if (t < o.t0 - 0.1 || (o.out != null && t > o.out + (o.outDur ?? 0.24) + 0.02)) return null;
  // layout at size0, then fit
  const lay = (size) => lines.map((segs) => {
    let w = 0;
    const out = segs.map((s) => {
      const font = s.a ? F.accent(size * 1.13) : F.caps(size);
      const track = s.a ? 0 : CAPS_TRACK * size;
      const m = measure(ctx, s.t, font, track);
      const r = { ...s, font, track, x: w, w: m.w };
      w += m.w;
      return r;
    });
    return { segs: out, w };
  });
  let L = lay(size0);
  const widest = Math.max(...L.map((l) => l.w));
  let size = size0;
  if (widest > maxW) { size = Math.floor(size0 * maxW / widest); L = lay(size); }
  const lh = size * (o.lh || 1.16);
  const top = o.top ?? 300;
  const cx = o.cx ?? 540;
  const exit = o.out != null ? E.inCubic(prog(t, o.out, o.out + (o.outDur ?? 0.24))) : 0;
  const blockA = 1 - exit;
  if (blockA <= 0) return null;
  const lift = -18 * exit;
  const bottom = top + size * 0.74 + lh * (L.length - 1);

  ctx.save();
  // soft scrim so captions read over the set
  if (o.scrim !== false) {
    const sa = 0.62 * clamp((t - o.t0 + 0.1) / 0.3) * blockA * (o.scrim ?? 1);
    const g = ctx.createLinearGradient(0, top - 120, 0, bottom + 110);
    g.addColorStop(0, 'rgba(10,11,10,0)'); g.addColorStop(0.25, `rgba(10,11,10,${sa})`);
    g.addColorStop(0.75, `rgba(10,11,10,${sa})`); g.addColorStop(1, 'rgba(10,11,10,0)');
    ctx.fillStyle = g; ctx.fillRect(0, top - 120, 1080, bottom - top + 230);
  }
  // lime rule above, grows from its centre
  if (o.rule !== false) {
    const rp = E.outCubic(prog(t, o.t0 - 0.08, o.t0 + 0.16));
    const rw = 64 * rp;
    const rx = o.align === 'left' ? (o.x0 ?? 72) : cx - rw / 2;
    ctx.globalAlpha = blockA;
    ctx.fillStyle = C.lime;
    ctx.fillRect(rx, top - size * 0.74 - 30 + lift, rw, 5);
  }
  let caretAt = null;
  L.forEach((line, li) => {
    const x0 = o.align === 'left' ? (o.x0 ?? 72) : cx - line.w / 2;
    const base = top + li * lh + lift;
    line.segs.forEach((s, si) => {
      if (!s.a) {
        // caps: rise per word, staggered
        const words = s.t.split(/(?<= )/);
        let wx = 0;
        words.forEach((wd, wi) => {
          const ww = measure(ctx, wd, s.font, s.track).w;
          const tw = (s.at ?? o.t0) + (li * 0.07) + wi * 0.045 + (s.delay || 0);
          const k = sp(t - tw, 'snappy');
          if (k > 0.001) {
            ctx.save();
            ctx.globalAlpha = blockA * clamp(k * 1.6);
            ctx.font = s.font; ctx.letterSpacing = `${s.track}px`; ctx.fillStyle = s.color || C.ink;
            ctx.fillText(wd, x0 + s.x + wx, base + (1 - k) * 30);
            ctx.restore();
          }
          wx += ww;
        });
      } else {
        // accent: typed on, letter by letter, synced to the spoken word
        const at = s.at ?? (o.t0 + 0.3), dur = Math.max(0.18, s.dur ?? 0.4);
        const n = s.t.length;
        const shown = clamp((t - at) / dur) * n;
        const full = Math.floor(shown);
        const frac = shown - full;
        const part = s.t.slice(0, full);
        if (t >= at - 0.12) {
          ctx.save();
          ctx.globalAlpha = blockA;
          ctx.font = s.font; ctx.fillStyle = C.lime; ctx.letterSpacing = '0px';
          ctx.fillText(part, x0 + s.x, base);
          // the next letter fades in (sub-frame smoothness)
          if (full < n && frac > 0) {
            const pw = measure(ctx, part, s.font).w;
            ctx.globalAlpha = blockA * frac;
            ctx.fillText(s.t[full], x0 + s.x + pw, base);
          }
          ctx.restore();
          const cw = measure(ctx, part, s.font).w + (full < n ? frac * measure(ctx, s.t[full], s.font).w : 0);
          const lastOnLine = si === line.segs.length - 1;
          caretAt = { x: x0 + s.x + cw + 6, y: base, h: size * 1.02, tEnd: at + dur, tStart: at - 0.12, typingOnly: !lastOnLine };
        }
      }
    });
  });
  // caret: solid while typing, blinks twice, leaves
  if (caretAt) {
    const since = t - caretAt.tEnd;
    const on = since < 0 || (!caretAt.typingOnly && since < 1.0 && (since % 0.5) < 0.3);
    if (on) {
      ctx.globalAlpha = blockA;
      ctx.fillStyle = C.lime;
      ctx.fillRect(caretAt.x, caretAt.y - caretAt.h * 0.8, 5, caretAt.h * 0.92);
    }
  }
  ctx.restore();
  return { top, bottom, size };
}

// ------------------------------------------------------------------ icons (none of the faces has ✓ or ↗)
export function check(ctx, x, y, s, color, p = 1, lw = null) {
  if (p <= 0) return;
  const pts = [[-0.42, 0.02], [-0.12, 0.32], [0.46, -0.3]];
  const l1 = Math.hypot(pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]);
  const l2 = Math.hypot(pts[2][0] - pts[1][0], pts[2][1] - pts[1][1]);
  const d = p * (l1 + l2);
  ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = lw ?? s * 0.17; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  ctx.beginPath(); ctx.moveTo(x + pts[0][0] * s, y + pts[0][1] * s);
  if (d <= l1) { const k = d / l1; ctx.lineTo(x + lerp(pts[0][0], pts[1][0], k) * s, y + lerp(pts[0][1], pts[1][1], k) * s); }
  else {
    ctx.lineTo(x + pts[1][0] * s, y + pts[1][1] * s);
    const k = (d - l1) / l2; ctx.lineTo(x + lerp(pts[1][0], pts[2][0], k) * s, y + lerp(pts[1][1], pts[2][1], k) * s);
  }
  ctx.stroke(); ctx.restore();
}
export function cross(ctx, x, y, s, color, lw = null) {
  ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = lw ?? s * 0.14; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.moveTo(x - s * 0.3, y - s * 0.3); ctx.lineTo(x + s * 0.3, y + s * 0.3);
  ctx.moveTo(x + s * 0.3, y - s * 0.3); ctx.lineTo(x - s * 0.3, y + s * 0.3); ctx.stroke(); ctx.restore();
}
export function arrowUR(ctx, x, y, s, color, lw = null) {
  ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = lw ?? s * 0.16; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  ctx.beginPath(); ctx.moveTo(x - s * 0.32, y + s * 0.32); ctx.lineTo(x + s * 0.32, y - s * 0.32);
  ctx.moveTo(x - s * 0.18, y - s * 0.32); ctx.lineTo(x + s * 0.32, y - s * 0.32); ctx.lineTo(x + s * 0.32, y + s * 0.18);
  ctx.stroke(); ctx.restore();
}
export function bagIcon(ctx, x, y, s, color) {
  // shopping tote: flared body, a darker fold band under the rim, two thin strap loops entering the body
  ctx.save(); ctx.fillStyle = color; ctx.strokeStyle = color; ctx.lineCap = 'round';
  ctx.lineWidth = s * 0.055;
  for (const sx of [-0.15, 0.15]) {
    ctx.beginPath(); ctx.moveTo(x + (sx - 0.09) * s, y - 0.06 * s);
    ctx.bezierCurveTo(x + (sx - 0.1) * s, y - 0.44 * s, x + (sx + 0.1) * s, y - 0.44 * s, x + (sx + 0.09) * s, y - 0.06 * s);
    ctx.stroke();
  }
  ctx.beginPath();
  ctx.moveTo(x - s * 0.34, y - s * 0.12); ctx.lineTo(x + s * 0.34, y - s * 0.12);
  ctx.lineTo(x + s * 0.44, y + s * 0.42); ctx.quadraticCurveTo(x + s * 0.45, y + s * 0.48, x + s * 0.38, y + s * 0.48);
  ctx.lineTo(x - s * 0.38, y + s * 0.48); ctx.quadraticCurveTo(x - s * 0.45, y + s * 0.48, x - s * 0.44, y + s * 0.42);
  ctx.closePath(); ctx.fill();
  ctx.fillStyle = 'rgba(10,11,10,0.38)';
  ctx.beginPath(); ctx.moveTo(x - s * 0.345, y - s * 0.09); ctx.lineTo(x + s * 0.345, y - s * 0.09);
  ctx.lineTo(x + s * 0.357, y - s * 0.02); ctx.lineTo(x - s * 0.357, y - s * 0.02); ctx.closePath(); ctx.fill();
  ctx.restore();
}
export function pinIcon(ctx, x, y, s, color, hole = '#0A0B0A') {
  // teardrop map pin with its point at (x, y)
  ctx.save(); ctx.fillStyle = color;
  const r = s * 0.42, cy = y - s * 0.82;
  ctx.beginPath(); ctx.arc(x, cy, r, Math.PI * 0.82, Math.PI * 0.18, false);
  ctx.lineTo(x, y); ctx.closePath(); ctx.fill();
  ctx.fillStyle = hole; ctx.beginPath(); ctx.arc(x, cy, r * 0.42, 0, TAU); ctx.fill();
  ctx.restore();
}
export function rewindIcon(ctx, x, y, s, color) {
  ctx.save(); ctx.fillStyle = color;
  for (const dx of [-0.02, -0.5]) {
    ctx.beginPath(); ctx.moveTo(x + (dx + 0.5) * s, y - 0.34 * s); ctx.lineTo(x + dx * s, y);
    ctx.lineTo(x + (dx + 0.5) * s, y + 0.34 * s); ctx.closePath(); ctx.fill();
  }
  ctx.restore();
}
export function lockIcon(ctx, x, y, s, color) {
  ctx.save(); ctx.fillStyle = color; ctx.strokeStyle = color; ctx.lineWidth = s * 0.12;
  rr(ctx, x - s * 0.32, y - s * 0.05, s * 0.64, s * 0.48, s * 0.08); ctx.fill();
  ctx.beginPath(); ctx.arc(x, y - s * 0.05, s * 0.2, Math.PI, 0); ctx.stroke();
  ctx.restore();
}

// ------------------------------------------------------------------ spinner (Hulk's lime ring, never a browser's)
// ang in radians (head of the arc), len arc length in radians, fill 0..1 grows the arc to a full ring
export function spinner(ctx, x, y, r, lw, ang, len, alpha = 1, glow = 1) {
  if (alpha <= 0) return;
  ctx.save(); ctx.globalAlpha *= alpha; ctx.lineCap = 'round';
  ctx.strokeStyle = 'rgba(242,246,238,0.16)'; ctx.lineWidth = lw;
  ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.stroke();
  if (len > 0.001) {
    if (glow > 0) { ctx.shadowColor = 'rgba(120,233,48,0.55)'; ctx.shadowBlur = lw * 1.6 * glow; }
    ctx.strokeStyle = C.lime; ctx.lineWidth = lw;
    ctx.beginPath(); ctx.arc(x, y, r, ang - len, ang); ctx.stroke();
  }
  ctx.restore();
}

// tick badge: lime disc with a dark check (the spinner's replacement)
export function tickBadge(ctx, x, y, r, p = 1, alpha = 1) {
  if (alpha <= 0 || p <= 0) return;
  ctx.save(); ctx.globalAlpha *= alpha;
  const k = clamp(p * 1.4);
  ctx.fillStyle = C.lime; ctx.beginPath(); ctx.arc(x, y, r * k, 0, TAU); ctx.fill();
  check(ctx, x + r * 0.02, y + r * 0.04, r * 1.05, C.bg, clamp((p - 0.35) / 0.65), r * 0.2);
  ctx.restore();
}

// ------------------------------------------------------------------ glass surfaces
export function glassPanel(ctx, x, y, w, h, r, o = {}) {
  ctx.save();
  if (o.shadow !== false) {
    ctx.shadowColor = 'rgba(0,0,0,0.55)'; ctx.shadowBlur = 40; ctx.shadowOffsetY = 18;
  }
  rr(ctx, x, y, w, h, r);
  const g = ctx.createLinearGradient(0, y, 0, y + h);
  g.addColorStop(0, o.top || 'rgba(27,32,28,0.94)'); g.addColorStop(1, o.bottom || 'rgba(16,19,17,0.94)');
  ctx.fillStyle = g; ctx.fill();
  ctx.shadowColor = 'transparent';
  ctx.lineWidth = o.lw || 1.5; ctx.strokeStyle = o.border || 'rgba(157,239,105,0.22)'; ctx.stroke();
  // inner top highlight
  ctx.save(); rr(ctx, x, y, w, h, r); ctx.clip();
  const hg = ctx.createLinearGradient(0, y, 0, y + 40);
  hg.addColorStop(0, 'rgba(255,255,255,0.06)'); hg.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = hg; ctx.fillRect(x, y, w, 40);
  ctx.restore();
  ctx.restore();
}

// pill with an icon slot: kind 'check' | 'cross' | null; p = status flip 0..1 (cross -> check)
export function pill(ctx, cx, cy, label, o = {}) {
  const size = o.size || 34, h = o.h || size * 1.85, padL = h * 0.24, icon = h * 0.62;
  const tw = measure(ctx, label, F.ui(size, 600)).w;
  const w = padL + icon + size * 0.4 + tw + size * 0.85;
  const k = o.k ?? 1;
  if (k <= 0.001) return { w, h };
  ctx.save();
  ctx.globalAlpha *= clamp(k * 1.5) * (o.alpha ?? 1);
  ctx.translate(cx, cy + (1 - k) * 16); ctx.scale(lerp(0.86, 1, k), lerp(0.86, 1, k));
  glassPanel(ctx, -w / 2, -h / 2, w, h, h / 2, { border: o.border || 'rgba(157,239,105,0.28)', top: 'rgba(24,29,25,0.95)', bottom: 'rgba(15,18,16,0.95)' });
  const ix = -w / 2 + padL + icon / 2;
  const on = o.on ?? 1;
  if (o.icon !== false) {
    ctx.fillStyle = mix('#3A2522', C.lime, on); ctx.beginPath(); ctx.arc(ix, 0, icon / 2, 0, TAU); ctx.fill();
    if (on > 0.5) check(ctx, ix, 2, icon * 0.95, C.bg, o.checkP ?? 1, icon * 0.15);
    else cross(ctx, ix, 0, icon * 0.9, C.red, icon * 0.12);
  }
  txt(ctx, label, ix + icon / 2 + size * 0.4, size * 0.36, F.ui(size, 600), C.ink);
  ctx.restore();
  return { w, h, iconX: cx - w / 2 + padL + icon / 2 };
}

// counter pill: forest-black pill, lime digits; the digit rolls up on each tick
export function counterPill(ctx, x, y, secs, tickT, k = 1) {
  if (k <= 0.001) return;
  const w = 214, h = 92;
  ctx.save(); ctx.globalAlpha *= clamp(k * 1.5);
  ctx.translate(x + w / 2, y + h / 2 + (1 - k) * 14); ctx.scale(lerp(0.85, 1, k), lerp(0.85, 1, k));
  glassPanel(ctx, -w / 2, -h / 2, w, h, h / 2, { top: '#121A15', bottom: '#0E1511', border: 'rgba(157,239,105,0.35)' });
  ctx.save(); rr(ctx, -w / 2, -h / 2, w, h, h / 2); ctx.clip();
  const roll = E.outCubic(clamp(tickT / 0.16));
  const font = F.caps(50);
  const cur = `0:0${secs}`, prev = `0:0${Math.max(0, secs - 1)}`;
  if (roll < 1 && secs > 0) {
    txt(ctx, prev, 0, 18 - roll * 46, font, C.lime, 'center', 1, 1 - roll);
    txt(ctx, cur, 0, 18 + (1 - roll) * 46, font, C.lime, 'center', 1, roll);
  } else txt(ctx, cur, 0, 18, font, C.lime, 'center', 1);
  ctx.restore();
  ctx.restore();
}

// pointer cursor, tip at (x, y)
export function cursor(ctx, x, y, s = 1, press = 0) {
  ctx.save(); ctx.translate(x, y); const k = s * (1 - 0.12 * press); ctx.scale(k, k);
  ctx.shadowColor = 'rgba(0,0,0,0.5)'; ctx.shadowBlur = 10; ctx.shadowOffsetY = 4;
  ctx.beginPath();
  ctx.moveTo(0, 0); ctx.lineTo(0, 46); ctx.lineTo(11, 36); ctx.lineTo(19, 55); ctx.lineTo(27, 51);
  ctx.lineTo(19, 33); ctx.lineTo(33, 32); ctx.closePath();
  ctx.fillStyle = '#FFFFFF'; ctx.fill();
  ctx.shadowColor = 'transparent'; ctx.lineWidth = 2.5; ctx.strokeStyle = '#0A0B0A'; ctx.lineJoin = 'round'; ctx.stroke();
  ctx.restore();
}

// film grain tiles (seeded), drawn in post
let GRAIN = null;
export function makeGrain() {
  GRAIN = [];
  for (let k = 0; k < 6; k++) {
    const cv = document.createElement('canvas'); cv.width = 384; cv.height = 384;
    const c = cv.getContext('2d'); const im = c.createImageData(384, 384);
    for (let i = 0; i < 384 * 384; i++) {
      const v = Math.floor(hash01(i, 11 + k) * 255);
      im.data[i * 4] = v; im.data[i * 4 + 1] = v; im.data[i * 4 + 2] = v; im.data[i * 4 + 3] = 255;
    }
    c.putImageData(im, 0, 0); GRAIN.push(cv);
  }
}
export function grain(ctx, frame, amount = 0.05) {
  if (!GRAIN) return;
  const g = GRAIN[frame % GRAIN.length];
  ctx.save(); ctx.globalAlpha = amount; ctx.globalCompositeOperation = 'overlay';
  const ox = Math.floor(hash01(frame, 3) * 384), oy = Math.floor(hash01(frame, 5) * 384);
  for (let y = -oy; y < 1920; y += 384) for (let x = -ox; x < 1080; x += 384) ctx.drawImage(g, x, y);
  ctx.restore();
}
export function vignette(ctx, amount = 0.55) {
  const g = ctx.createRadialGradient(540, 900, 380, 540, 960, 1250);
  g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, `rgba(0,0,0,${amount})`);
  ctx.save(); ctx.fillStyle = g; ctx.fillRect(0, 0, 1080, 1920); ctx.restore();
}

// background: forest-black with the reference's faint rounded-tile grid (parallax offset ox, oy)
export function background(ctx, ox = 0, oy = 0, lift = 1) {
  const g = ctx.createLinearGradient(0, 0, 0, 1920);
  g.addColorStop(0, '#0B0E0C'); g.addColorStop(0.45, '#0F1612'); g.addColorStop(1, '#0A0B0A');
  ctx.fillStyle = g; ctx.fillRect(0, 0, 1080, 1920);
  if (lift > 0) {
    const rg = ctx.createRadialGradient(540, 860, 60, 540, 900, 900);
    rg.addColorStop(0, `rgba(30,52,38,${0.38 * lift})`); rg.addColorStop(1, 'rgba(30,52,38,0)');
    ctx.fillStyle = rg; ctx.fillRect(0, 0, 1080, 1920);
  }
  const tw = 156, th = 196, gap = 20;
  ctx.save(); ctx.strokeStyle = C.grid; ctx.lineWidth = 1.5;
  const sx = ((ox % (tw + gap)) + (tw + gap)) % (tw + gap), sy = ((oy % (th + gap)) + (th + gap)) % (th + gap);
  for (let y = -sy - (th + gap); y < 1920; y += th + gap) {
    for (let x = -sx - (tw + gap); x < 1080; x += tw + gap) { rr(ctx, x, y, tw, th, 14); ctx.stroke(); }
  }
  ctx.restore();
}

// stage rules: full-width lime line with a darker under-line (reference)
export function rule(ctx, y, p = 1, alpha = 1) {
  if (p <= 0) return;
  ctx.save(); ctx.globalAlpha *= alpha;
  const w = 1080 * p;
  ctx.fillStyle = 'rgba(42,92,10,0.9)'; ctx.fillRect(540 - w / 2, y + 3, w, 6);
  ctx.fillStyle = C.lime; ctx.fillRect(540 - w / 2, y, w, 3);
  ctx.restore();
}
