// The Door That Won't Open (Hulk Marketing): a pure function of time. window.seek(t) paints frame t.
// docs/shotlist.md is the plan; vo_words.json holds the spoken word times the captions are synced to.
// The street is one continuous set driven by story time ts, so the rewind (beat 7) plays it backwards.
import * as M from './lib/motion.js';
import { C, F, SAFE, title, pill, counterPill, spinner, tickBadge, cursor, background, rule, glassPanel, txt, measure,
  arrowUR, rewindIcon, lockIcon, pinIcon, bagIcon, rr, sp, makeGrain, grain, vignette } from './src/kit.js';
import { GROUND, FEET, DOOR_A, DOOR_B, SPIN_A, drawStreet, camStory, herStory, herArrivalB, applyCam, stepLen } from './src/street.js';

const { E, clamp, lerp, prog, TAU, wobble } = M;
const ss = (a, b, x) => { const t = clamp((x - a) / (b - a)); return t * t * (3 - 2 * t); };
const logz = (a, b, p) => a * Math.pow(b / a, p);

// ---------------------------------------------------------------- key times (s), from vo_words.json + shot list
const T = {
  buy: 2.27, open: 4.99, push1: 4.45, push2: 6.17, one: 9.03, two: 10.0, three: 11.01, across: 13.73,
  slow: 19.03, cut6: 21.0, quietly: 22.72, conversions: 23.9, rew0: 25.2, rew1: 26.2,
  fast: 27.18, stable: 27.82, easy: 28.56, shrink: 30.6, in30: 31.93, audit: 34.79, end: 36.5,
};
const ARR_B = herArrivalB();          // ~16.2: she reaches shop B
const DOOR_B_OPEN = ARR_B - 0.42;     // the sliding door glides open as she arrives

// every visual accent (beats = t * 2 at 120 bpm); the score/SFX script reads the same times
const HITS = [
  [0.35 * 2, 'pin drops on shop A', 'pop'], [1.95 * 2, 'bag bubble', 'pop'],
  [T.push1 * 2, 'push 1: dull thud', 'thud'], [T.open * 2, 'spinner appears', 'blip'], [T.push2 * 2, 'push 2: thud', 'thud'],
  [9 * 2, 'counter 0:01', 'tick'], [10 * 2, 'counter 0:02', 'tick'], [11 * 2, 'counter 0:03', 'tick'],
  [DOOR_B_OPEN * 2, 'door B slides', 'whoosh'], [(DOOR_B_OPEN + 0.12) * 2, 'shop bell', 'bell'],
  [18.2 * 2, 'whip back', 'whoosh'], [T.cut6 * 2, 'cut to black', 'sub'], [T.rew0 * 2, 'rewind', 'whoosh'],
  [T.fast * 2, 'door clicks open', 'click'], [27.75 * 2, 'fast check', 'blip'], [27.9 * 2, 'stable check', 'blip'],
  [28.62 * 2, 'easy check', 'blip'], [T.shrink * 2, 'shrink to card', 'whoosh'], [T.audit * 2, 'cta click', 'click'],
];

// ---------------------------------------------------------------- world state at film time t
function slowState(ts) {
  const her = herStory(ts);
  const j1 = ts > T.push1 ? 7 * Math.exp(-(ts - T.push1) * 10) * Math.sin((ts - T.push1) * 62) : 0;
  const j2 = ts > T.push2 ? 9 * Math.exp(-(ts - T.push2) * 9) * Math.sin((ts - T.push2) * 58) : 0;
  const openB = E.inOutCubic(prog(ts, DOOR_B_OPEN, DOOR_B_OPEN + 0.42));
  const spinA = ss(T.open - 0.05, T.open + 0.22, ts);
  const st = {
    her, warmA: 0, swing: 0, judder: j1 + j2, flex: Math.min(1, Math.abs(j1 + j2) / 6), spinA,
    spinAng: ts * 5.6, spinLen: 1.95 * ss(T.open - 0.05, T.open + 0.35, ts) + 0.01, tick: 0, openB,
    bellT: DOOR_B_OPEN + 0.12, spillA: 0,
  };
  // the route she walks across the road
  if (ts > 12.9 && ts < 18.3) {
    st.route = { x0: 430, x1: 1660, y: FEET + 52, p: clamp((Math.min(her.x, 1660) - 430) / (1660 - 430)),
      ring: clamp((ts - ARR_B) / 0.7), alpha: 1 - ss(17.6, 18.15, ts) };
  }
  return st;
}

// replay (beat 7): the door opens the instant she touches it
function fastState(t) {
  const her = herStory(4.2);
  her.reach = lerp(0.84, 1, ss(26.3, 27.0, t));
  her.push = 0.6 * Math.max(0, Math.min(1, (t - 27.02) / 0.1)) * (1 - ss(27.2, 27.5, t));
  her.smile = ss(27.25, 27.6, t);
  her.tilt = 0;
  const swing = clamp(E.outBack(prog(t, T.fast, T.fast + 0.3), 1.2));
  let enterA = false;
  if (t > 27.42) {
    const u = t - 27.42;
    const d = 280 * E.inOutSine(clamp(u / 1.3));
    her.x = 340 + d;
    her.walk = Math.sin(clamp(u / 1.3) * Math.PI) * 0.95 + 0.05;
    her.slope = (GROUND + 6 - FEET) / 280;
    her.phase = stepLen(d, d * her.slope) / 322 * TAU;
    her.reach = her.reach * (1 - ss(27.42, 27.7, t));
    her.y = lerp(FEET, GROUND + 6, E.inOutSine(clamp(u / 1.3)));
    her.scale = lerp(1, 0.9, E.inOutSine(clamp(u / 1.3)));
    her.warm = ss(0.1, 1.0, u);
    enterA = her.x > 360;
  }
  const warmA = ss(T.fast - 0.02, T.fast + 0.45, t);
  return {
    her, enterA, warmA, swing, judder: 0, flex: 0,
    spinA: ss(26.92, 27.04, t), spinAng: t * 9.0, spinLen: lerp(1.95, TAU, E.inOutCubic(prog(t, 27.0, 27.14))),
    tick: ss(27.08, 27.22, t), openB: 1, bellT: -9, spillA: swing * warmA,
  };
}
function fastCam(t) {
  const c0 = camStory(4.2, herStory(4.2));
  const p = E.inOutCubic(prog(t, T.rew1, T.rew1 + 0.75));
  const q = E.inOutSine(prog(t, 27.45, 28.9));
  const drift = prog(t, 28.9, 31.2);
  return { x: lerp(lerp(c0.x, 470, p), 556, q), y: lerp(lerp(c0.y, 1000, p), 985, q), z: logz(c0.z, 1.5, p) * (1 + 0.06 * q) * (1 + 0.025 * drift) };
}

// rewind (beat 7, 25.2-26.2): the story played backwards from the freeze to her arrival
const rewTs = (t) => lerp(20.9, 4.2, E.inOutSine(prog(t, T.rew0, T.rew1)));

// ---------------------------------------------------------------- world-attached UI
function worldUI(ctx, cam, ts, st, mode) {
  applyCam(ctx, cam);
  // map pin on shop A ("she found you")
  if (mode === 'slow' && ts < 4.2) {
    const k = sp(ts - 0.35, 'pop');
    const out = ss(3.45, 3.85, ts);
    if (k > 0.001 && out < 1) {
      const y = 420 - (1 - k) * 260;
      ctx.save(); ctx.globalAlpha = clamp(k * 2) * (1 - out);
      const rg = ctx.createRadialGradient(350, 380, 4, 350, 380, 150);
      rg.addColorStop(0, 'rgba(157,239,105,0.22)'); rg.addColorStop(1, 'rgba(157,239,105,0)');
      ctx.fillStyle = rg; ctx.fillRect(200, 230, 300, 300);
      // landing ring on the sign's cornice
      const rp = clamp((ts - 0.55) / 0.8);
      if (rp > 0 && rp < 1) {
        ctx.strokeStyle = C.lime; ctx.lineWidth = 5; ctx.globalAlpha *= 1 - rp;
        ctx.beginPath(); ctx.ellipse(350, 438, 30 + 120 * rp, 8 + 26 * rp, 0, 0, TAU); ctx.stroke();
        ctx.globalAlpha = clamp(k * 2) * (1 - out);
      }
      ctx.translate(350, y); const sc = lerp(0.6, 1, k) * (1 - 0.3 * out); ctx.scale(sc, sc);
      pinIcon(ctx, 0, 0, 120, C.lime, '#0E1511');
      ctx.restore();
    }
    // speech bubble with a bag ("she wants to buy")
    const bk = sp(ts - 1.95, 'pop');
    const bout = ss(3.4, 3.8, ts);
    if (bk > 0.001 && bout < 1) {
      const h = st.her;
      const bx = h.x + 78, by = h.y - 600 + 6 * Math.sin(ts * 3);
      ctx.save(); ctx.globalAlpha = clamp(bk * 2) * (1 - bout);
      ctx.translate(bx, by); const sc = lerp(0.5, 1, bk); ctx.scale(sc, sc);
      glassPanel(ctx, -62, -54, 124, 104, 30, { border: 'rgba(157,239,105,0.4)' });
      ctx.fillStyle = 'rgba(20,24,21,0.95)';
      ctx.beginPath(); ctx.moveTo(-26, 48); ctx.lineTo(-42, 78); ctx.lineTo(0, 48); ctx.closePath(); ctx.fill();
      bagIcon(ctx, 0, -6, 70, C.lime);
      ctx.restore();
    }
  }
  // browser window built around shop A: the shop *is* the website (beat 5)
  if (mode === 'slow' && ts > 18.4) {
    const x0 = -110, x1 = 810, y0 = 396, y1 = 1530, bar = 96;
    const draw = E.inOutCubic(prog(ts, 18.55, 19.0));
    const barK = E.outCubic(prog(ts, 18.85, 19.1));
    ctx.save();
    // dim outside the window
    ctx.fillStyle = `rgba(6,8,7,${0.5 * draw})`;
    ctx.beginPath(); ctx.rect(-3000, -2000, 7000, 6000); ctx.roundRect(x0, y0, x1 - x0, y1 - y0, 34); ctx.fill('evenodd');
    // title bar
    if (barK > 0) {
      ctx.save(); ctx.beginPath(); ctx.roundRect(x0, y0, x1 - x0, y1 - y0, 34); ctx.clip();
      ctx.fillStyle = 'rgba(18,20,18,0.97)'; ctx.fillRect(x0, y0, x1 - x0, bar * barK);
      ctx.restore();
      for (let i = 0; i < 3; i++) {
        const dk = sp(ts - 19.0 - i * 0.05, 'pop');
        if (dk > 0) { ctx.fillStyle = C.muted; ctx.beginPath(); ctx.arc(x0 + 48 + i * 34, y0 + bar / 2, 11 * dk, 0, TAU); ctx.fill(); }
      }
      const uk = E.outCubic(prog(ts, 19.08, 19.35));
      if (uk > 0) {
        const ux = x0 + 170, uw = (x1 - x0 - 230) * uk;
        ctx.fillStyle = '#2A302A'; rr(ctx, ux, y0 + 22, uw, 52, 26); ctx.fill();
        ctx.strokeStyle = `rgba(157,239,105,${0.35 * uk})`; ctx.lineWidth = 1.5; ctx.stroke();
        ctx.globalAlpha = uk; lockIcon(ctx, ux + 32, y0 + 44, 22, '#5A635A');
        // blank address (no shop names): a skeleton bar with a shimmer
        ctx.fillStyle = '#454D45'; rr(ctx, ux + 60, y0 + 40, Math.max(0, uw - 200), 16, 8); ctx.fill();
        ctx.globalAlpha = 1;
      }
      // loading bar, stuck at about a third, pulsing
      const lk = E.outCubic(prog(ts, 19.25, 19.7));
      if (lk > 0) {
        ctx.fillStyle = 'rgba(157,239,105,0.18)'; ctx.fillRect(x0 + 2, y0 + bar, x1 - x0 - 4, 6);
        ctx.fillStyle = C.lime; ctx.fillRect(x0 + 2, y0 + bar, (x1 - x0) * 0.34 * lk, 6);
        const pulse = (ts * 0.9) % 1;
        ctx.fillStyle = `rgba(255,255,255,${0.5 * (1 - pulse)})`; ctx.fillRect(x0 + 2 + (x1 - x0) * 0.34 * lk * pulse, y0 + bar, 40, 6);
      }
    }
    // skeleton shimmer over the blank sign and the window: content that hasn't loaded
    const sk = E.inOutSine(prog(ts, 19.3, 19.8));
    if (sk > 0) {
      ctx.save(); ctx.globalAlpha = sk;
      ctx.fillStyle = 'rgba(40,62,50,0.95)'; rr(ctx, 40, 494, 420, 22, 11); ctx.fill(); rr(ctx, 40, 526, 260, 18, 9); ctx.fill();
      ctx.fillStyle = 'rgba(20,32,26,0.78)'; rr(ctx, 30, 630, 370, 300, 18); ctx.fill();
      ctx.fillStyle = 'rgba(40,62,50,0.95)'; rr(ctx, 30, 960, 300, 26, 13); ctx.fill(); rr(ctx, 30, 1004, 220, 22, 11); ctx.fill();
      // the shimmer band
      const sx = -200 + ((ts - 19.3) * 600) % 1100;
      const g = ctx.createLinearGradient(sx, 0, sx + 200, 0);
      g.addColorStop(0, 'rgba(157,239,105,0)'); g.addColorStop(0.5, 'rgba(157,239,105,0.10)'); g.addColorStop(1, 'rgba(157,239,105,0)');
      ctx.fillStyle = g; ctx.fillRect(0, 480, 470, 560);
      ctx.restore();
    }
    // window outline draws on
    if (draw > 0) {
      ctx.strokeStyle = 'rgba(157,239,105,0.55)'; ctx.lineWidth = 4;
      const per = 2 * ((x1 - x0) + (y1 - y0));
      ctx.setLineDash([per * draw, per]);
      ctx.beginPath(); ctx.roundRect(x0, y0, x1 - x0, y1 - y0, 34); ctx.stroke(); ctx.setLineDash([]);
    }
    ctx.restore();
  }
}

// ---------------------------------------------------------------- screen overlays
function captions(ctx, t) {
  // beat 1
  title(ctx, t, [[{ t: 'SHE FOUND YOU.', a: false, at: -0.12 }], [{ t: 'SHE WANTS TO ', a: false, at: 1.62 }, { t: 'buy.', a: true, at: T.buy, dur: 0.28 }]],
    { t0: -0.18, out: 3.85, top: 330, size: 74 });
  // beat 2
  title(ctx, t, [[{ t: 'BUT THE DOOR', a: false }], [{ t: 'WON’T ', a: false, at: 4.68 }, { t: 'open.', a: true, at: T.open, dur: 0.32 }]],
    { t0: 4.2, out: 7.5, top: 330, size: 76 });
  // beat 3: left-aligned, the counter sits top-right
  title(ctx, t, [[{ t: 'ONE SECOND.', a: false, at: 8.95 }], [{ t: 'TWO.', a: false, at: T.two - 0.1 }],
    [{ t: 'Three.', a: true, at: T.three - 0.02, dur: 0.3 }]], { t0: 8.95, out: 12.55, top: 352, size: 76, align: 'left', x0: 72 });
  // beat 4
  title(ctx, t, [[{ t: 'SO SHE WALKS', a: false }], [{ t: 'across', a: true, at: T.across, dur: 0.3 }, { t: ' THE ROAD.', a: false, at: 14.02 }]],
    { t0: 13.1, out: 17.55, top: 330, size: 76 });
  // beat 5
  title(ctx, t, [[{ t: 'THAT’S A', a: false }], [{ t: 'slow website.', a: true, at: T.slow, dur: 0.62 }]],
    { t0: 18.42, out: 20.72, top: 328, size: 76 });
  // beat 7
  title(ctx, t, [[{ t: 'WE BUILD SITES', a: false, at: 26.06 }], [{ t: 'THAT ARE ', a: false, at: 26.7 }, { t: 'fast,', a: true, at: T.fast, dur: 0.3 }],
    [{ t: 'STABLE AND EASY TO GROW.', a: false, at: T.stable - 0.05 }]],
    { t0: 26.0, out: 30.3, top: 318, size: 66 });
}

function counter(ctx, t) {
  if (t < 8.3 || t > 13.1) return;
  const k = sp(t - 8.35, 'ui') * (1 - E.inCubic(prog(t, 12.75, 13.0)));
  const secs = clamp(Math.floor(t - 8.0), 0, 3);
  counterPill(ctx, 746, 286, secs, t - Math.floor(t), k);
}

function rewindUI(ctx, t, ts) {
  const a = ss(T.rew0 - 0.02, T.rew0 + 0.08, t) * (1 - ss(T.rew1 - 0.06, T.rew1 + 0.14, t));
  if (a <= 0) return;
  ctx.save(); ctx.globalAlpha = a;
  // tape lines
  ctx.fillStyle = 'rgba(10,11,10,0.22)'; ctx.fillRect(0, 0, 1080, 1920);
  ctx.fillStyle = 'rgba(242,246,238,0.035)';
  for (let y = 0; y < 1920; y += 7) ctx.fillRect(0, y, 1080, 2);
  for (let i = 0; i < 3; i++) {
    const y = ((t * 2400 + i * 640) % 2200) - 140;
    const g = ctx.createLinearGradient(0, y, 0, y + 60);
    g.addColorStop(0, 'rgba(242,246,238,0)'); g.addColorStop(0.5, 'rgba(242,246,238,0.07)'); g.addColorStop(1, 'rgba(242,246,238,0)');
    ctx.fillStyle = g; ctx.fillRect(0, y, 1080, 60);
  }
  // rewind pill (leaves before the beat-7 caption rises into its place at 26.06)
  ctx.globalAlpha = a * (1 - ss(T.rew1 - 0.32, T.rew1 - 0.14, t));
  if (ctx.globalAlpha > 0) {
    glassPanel(ctx, 540 - 70, 300, 140, 84, 42, { border: 'rgba(157,239,105,0.45)' });
    rewindIcon(ctx, 545, 342, 54, C.lime);
  }
  ctx.globalAlpha = a;
  // scrub bar: the playhead runs backwards through the story
  const x0 = 150, x1 = 930, y = 1206;
  ctx.fillStyle = 'rgba(242,246,238,0.18)'; rr(ctx, x0, y - 4, x1 - x0, 8, 4); ctx.fill();
  const px = lerp(x0, x1, clamp(ts / 21));
  ctx.fillStyle = C.lime; rr(ctx, x0, y - 4, px - x0, 8, 4); ctx.fill();
  ctx.beginPath(); ctx.arc(px, y, 15, 0, TAU); ctx.fill();
  ctx.restore();
}

// the three checks (beat 7)
const PILLS = [{ label: 'Fast', at: 27.3, check: 27.72 }, { label: 'Stable', at: T.stable - 0.02, check: 27.9 }, { label: 'Easy to grow', at: T.easy - 0.04, check: 28.62 }];
function pillRow(ctx, t, ctxMeasure) {
  if (t < 27.2 || t > 30.6) return null;
  const out = E.inCubic(prog(t, 30.3, 30.55));
  const size = 39, gap = 14;
  const ws = PILLS.map((p) => pill(ctx, 0, 0, p.label, { size, k: 0 }).w);
  const total = ws.reduce((a, b) => a + b, 0) + gap * 2;
  let x = 540 - total / 2;
  const y = 590;
  const slots = [];
  PILLS.forEach((p, i) => {
    const k = sp(t - p.at, 'ui');
    const cx = x + ws[i] / 2;
    const on = 1;
    const r = pill(ctx, cx, y, p.label, { size, k: k * (1 - out), on, checkP: ss(p.check, p.check + 0.18, t) });
    slots.push({ x: x + 0.24 * size * 1.85 + 0.31 * size * 1.85, y, k });
    x += ws[i] + gap;
  });
  // the line from the site
  const lk = ss(28.75, 29.05, t) * (1 - E.inCubic(prog(t, 30.4, 30.57)));
  if (lk > 0) {
    const line = 'Core Web Vitals tuned and continuously measured.', font = F.ui(34, 600);
    const w = measure(ctx, line, font).w, dy = 10 * (1 - lk);
    ctx.save(); ctx.globalAlpha = lk;
    glassPanel(ctx, 540 - w / 2 - 26, 646 + dy, w + 52, 66, 33);
    ctx.restore();
    txt(ctx, line, 540, 690 + dy, font, C.ink, 'center', 0, lk);
  }
  return slots;
}

// tick badge that pops off the glass and flies into the "Fast" pill
function tickFlight(ctx, t, cam, slots) {
  if (t < T.fast || t > 27.8) return;
  const gx = (SPIN_A.x - cam.x) * cam.z + 540, gy = (SPIN_A.y - cam.y) * cam.z + 960;
  const r0 = SPIN_A.r * 0.92 * cam.z;
  const target = slots && slots[0] ? slots[0] : { x: 380, y: 590 };
  const p = E.inOutCubic(prog(t, 27.36, 27.74));
  const lift = Math.sin(p * Math.PI) * -90;
  const x = lerp(gx, target.x, p), y = lerp(gy, target.y, p) + lift;
  const r = lerp(r0 * (1 + 0.15 * ss(T.fast, 27.32, t)), 0.62 * 32 * 1.85 / 2, p);
  ctx.save();
  ctx.shadowColor = 'rgba(120,233,48,0.6)'; ctx.shadowBlur = 30 * (1 - p);
  tickBadge(ctx, x, y, r, 1, 1 - ss(27.7, 27.78, t));
  ctx.restore();
}

// ---------------------------------------------------------------- the stage (beat 6)
function stage(ctx, t) {
  background(ctx, 0, 0, 0.6);
  rule(ctx, 248, 1); rule(ctx, 1302, 1);
  const k = 1 + 0.035 * E.inOutSine(prog(t, T.cut6, T.rew0));
  ctx.save(); M.zoomAbout(ctx, k, 540, 760);
  // the spinner alone, turning slowly; before the rewind it stalls and reverses
  const tt = t - T.cut6;
  let ang = tt * 2.7;
  const STALL = T.rew0 - 0.45;
  if (t > STALL) { const u = t - STALL; ang = (STALL - T.cut6) * 2.7 + 2.7 * (u - u * u / 0.5) - Math.max(0, u - 0.25) ** 2 * 36; }
  const glowR = ctx.createRadialGradient(540, 610, 40, 540, 610, 420);
  glowR.addColorStop(0, 'rgba(120,233,48,0.10)'); glowR.addColorStop(1, 'rgba(120,233,48,0)');
  ctx.fillStyle = glowR; ctx.fillRect(100, 190, 880, 840);
  spinner(ctx, 540, 610, 176, 26, ang, 1.85, 1, 1.2);
  ctx.restore();
  title(ctx, t, [[{ t: 'EVERY SECOND OF', a: false, at: 21.3 }], [{ t: 'LOAD TIME', a: false, at: 22.1 }],
    [{ t: 'quietly costs you', a: true, at: T.quietly, dur: 1.12 }], [{ t: 'conversions.', a: true, at: T.conversions - 0.06, dur: 0.3 }]],
  { t0: 21.22, top: 960, size: 78, scrim: false });   // no exit: the hard cut to the rewind (T.rew0) takes it
}

// ---------------------------------------------------------------- end card (beat 8)
// stack: rule 222 · shot card 272-682 · headline 703-875 · CTA panel 918-1150 · logo ~1176-1234 · rule 1270
const CARD = { x: 190, y: 272, w: 700, h: 410, r: 30 };
const CTA = { y: 918, h: 232, label: 968, btn: 1030, url: 1124, logo: 1204, rule: 1270 };
function endCard(ctx, t, IMG, drawShot) {
  background(ctx, 0, 0, 0.7);
  const rk = E.inOutCubic(prog(t, 30.95, 31.5));
  rule(ctx, 222, rk); rule(ctx, CTA.rule, rk);
  // the shot shrinking into its card
  const p = E.inOutCubic(prog(t, T.shrink, T.shrink + 0.78));
  const box = { x: lerp(0, CARD.x, p), y: lerp(0, CARD.y, p), w: lerp(1080, CARD.w, p), h: lerp(1920, CARD.h, p), r: lerp(0, CARD.r, p) };
  // headline first and only below the card's bottom edge, so that edge wipes the rule and words on as it rises
  if (t > T.shrink + 0.2) {
    ctx.save(); ctx.beginPath(); ctx.rect(0, box.y + box.h, 1080, 1920); ctx.clip();
    title(ctx, t, [[{ t: 'SEE YOUR OPPORTUNITY', a: false, at: 31.12 }], [{ t: 'in 30 seconds.', a: true, at: T.in30, dur: 1.25 }]],
      { t0: 31.08, top: 782, size: 66, scrim: false });
    ctx.restore();
  }
  ctx.save();
  if (p > 0.02) { ctx.shadowColor = 'rgba(0,0,0,0.6)'; ctx.shadowBlur = 50 * p; ctx.shadowOffsetY = 20 * p; ctx.fillStyle = '#0A0B0A'; rr(ctx, box.x, box.y, box.w, box.h, box.r); ctx.fill(); }
  ctx.restore();
  ctx.save(); rr(ctx, box.x, box.y, box.w, box.h, box.r); ctx.clip();
  drawShot(ctx, p, box);
  ctx.restore();
  if (p > 0) { ctx.save(); ctx.lineWidth = 2; ctx.strokeStyle = `rgba(157,239,105,${0.35 * p})`; rr(ctx, box.x, box.y, box.w, box.h, box.r); ctx.stroke(); ctx.restore(); }
  if (t < T.shrink + 0.2) return;
  // CTA card, sized to its content and centred
  const bfont = F.ui(36, 700), ufont = F.ui(35, 600);
  const line = 'hulkmarketing.co.uk · 07577 764436';
  const tw = measure(ctx, 'Get Free Website Audit', bfont).w;
  const bw = tw + 202, bh = 86;
  const cw = Math.max(bw, measure(ctx, line, ufont).w), X0 = Math.round(540 - cw / 2);
  // the cursor clicks in the empty gap between "Audit" and the arrow, clear of the URL line below
  const curTo = [X0 + 40 + tw + 22, CTA.btn - bh / 2 + 12];
  const ck = sp(t - 32.95, 'ui');
  if (ck > 0.001) {
    ctx.save(); ctx.globalAlpha = clamp(ck * 1.6); ctx.translate(0, (1 - ck) * 40);
    glassPanel(ctx, X0 - 42, CTA.y, cw + 84, CTA.h, 32, { border: 'rgba(157,239,105,0.3)' });
    txt(ctx, 'FREE WEBSITE AUDIT', X0, CTA.label, F.ui(27, 700), C.muted, 'left', 5);
    // the button
    const bk = sp(t - 33.15, 'pop');
    const press = M.bump(t, T.audit + 0.03, 0.09);
    ctx.save(); ctx.translate(X0 + bw / 2, CTA.btn); const bs = lerp(0.8, 1, bk) * (1 - 0.035 * press); ctx.scale(bs, bs);
    ctx.globalAlpha *= clamp(bk * 1.5);
    // hover tint while the cursor is on it, back to brand lime once it has clicked and gone
    const hover = ss(34.45, 34.65, t) * (1 - ss(T.audit + 0.2, T.audit + 0.45, t));
    ctx.fillStyle = M.mix(C.lime, '#B6F58C', hover * 0.6); rr(ctx, -bw / 2, -bh / 2, bw, bh, bh / 2); ctx.fill();
    txt(ctx, 'Get Free Website Audit', -bw / 2 + 40, 13, bfont, '#0A0B0A');
    const nudge = 6 * M.bump(t, T.audit + 0.18, 0.18);
    arrowUR(ctx, bw / 2 - 52 + nudge, -nudge, 30, '#0A0B0A', 4.5);
    ctx.restore();
    // ripple from the click
    const rp = prog(t, T.audit, T.audit + 0.6);
    if (rp > 0 && rp < 1) {
      ctx.strokeStyle = `rgba(157,239,105,${0.8 * (1 - rp)})`; ctx.lineWidth = 4;
      ctx.beginPath(); ctx.arc(curTo[0], curTo[1], 14 + 90 * E.outCubic(rp), 0, TAU); ctx.stroke();
    }
    // URL · phone, typed
    const n = Math.floor(clamp((t - 33.4) / 0.95) * line.length);
    if (n > 0) txt(ctx, line.slice(0, n), X0, CTA.url, ufont, C.ink, 'left', 0.2, 0.92);
    ctx.restore();
  }
  // real logo: lands on "audit.", after the click (the reference's click -> logo -> hold)
  const lk = sp(t - (T.audit + 0.15), 'ui');
  if (lk > 0.001 && IMG.logo) {
    const w = 380, h = w * IMG.logo.height / IMG.logo.width;
    ctx.save(); ctx.globalAlpha = clamp(lk * 1.5);
    ctx.drawImage(IMG.logo, 540 - w / 2, CTA.logo - h / 2 + (1 - lk) * 24, w, h);
    ctx.restore();
  }
  // cursor slides in from off-frame at button height (never over the URL line, the logo or the right-hand rail),
  // clicks on "audit", then eases up and away and fades, so the final hold is clean
  if (t > 33.95 && t < T.audit + 0.8) {
    const cp = E.inOutCubic(prog(t, 33.98, 34.66));
    const x = lerp(1130, curTo[0], cp), y = lerp(960, curTo[1], cp) - Math.sin(cp * Math.PI) * 24;
    const away = E.inOutCubic(prog(t, T.audit + 0.3, T.audit + 0.75));
    ctx.save(); ctx.globalAlpha = ss(33.95, 34.1, t) * (1 - away);
    cursor(ctx, x + 60 * away, y - 50 * away, 1.15, M.bump(t, T.audit + 0.02, 0.08));
    ctx.restore();
  }
}

// ---------------------------------------------------------------- frame
function street(ctx, t, IMG) {
  let ts, st, cam, mode;
  if (t < T.cut6) { ts = t; st = slowState(ts); cam = camStory(ts, st.her); mode = 'slow'; }
  else if (t < T.rew1) { ts = rewTs(t); st = slowState(ts); cam = camStory(ts, st.her); mode = 'slow'; }
  else { ts = t; st = fastState(t); cam = fastCam(t); mode = 'fast'; }
  return { ts, st, cam, mode };
}

function paintStreet(ctx, W, mode, ts, st, cam, t) {
  ctx.save();
  background(ctx, -cam.x * cam.z * 0.25, -cam.y * cam.z * 0.12, 1);
  drawStreet(ctx, cam, ts, st);
  worldUI(ctx, cam, ts, st, mode);
  ctx.restore();
}

// probe for the audio build (audio/probe.mjs): her walk state at any film time
window.PROBE = (t) => { const S = street(null, t); const h = S.st.her; return { x: h.x, phase: h.phase, walk: h.walk, inside: h.inside || 0, enterA: !!S.st.enterA }; };

M.film({
  fonts: [F.caps(80), F.accent(80), F.ui(32, 600), F.ui(32, 500), F.ui(27, 700)],
  images: { logo: 'assets/hulk-marketing-logo.png' },
  hits: HITS,
  samples: (t) => (t > 18.05 && t < 18.35) ? 40 : (t > 25.3 && t < 26.1) ? 32 : (t > 27.34 && t < 27.76) ? 24
    : (t > 17.95 && t < 18.55) || (t > T.rew0 - 0.05 && t < 26.3) ? 10
    : (t > 3.3 && t < 4.5) || (t > 7.4 && t < 8.45) || (t > 30.55 && t < 31.45) || (t > 27.1 && t < 27.8) ? 7 : 4,
  init() { makeGrain(); },
  draw(ctx, u, t, IMG) {
    const S = street(ctx, t, IMG);
    if (t < T.cut6) {
      paintStreet(ctx, 1080, S.mode, S.ts, S.st, S.cam, t);
      captions(ctx, t);
      counter(ctx, t);
    } else if (t < T.rew0) {
      stage(ctx, t);
    } else if (t < T.shrink) {
      paintStreet(ctx, 1080, S.mode, S.ts, S.st, S.cam, t);
      if (t < T.rew1 + 0.2) rewindUI(ctx, t, t < T.rew1 ? S.ts : 4.2);
      captions(ctx, t);
      const slots = pillRow(ctx, t);
      tickFlight(ctx, t, S.cam, slots);
    } else {
      const st = fastState(t), cam0 = fastCam(t);
      endCard(ctx, t, IMG, (c, p, box) => {
        // the shot, re-framed into the card (log zoom), still live
        const camEnd = { x: 372, y: 935, z: 0.6, sx: CARD.x + CARD.w / 2, sy: CARD.y + CARD.h / 2 };
        const cam = { x: lerp(cam0.x, camEnd.x, p), y: lerp(cam0.y, camEnd.y, p), z: logz(cam0.z, camEnd.z, p),
          sx: lerp(540, camEnd.sx, p), sy: lerp(960, camEnd.sy, p) };
        c.save();
        background(c, 0, 0, 1);
        drawStreet(c, cam, t, st);
        c.restore();
      });
    }
  },
  post(ctx, u, t) {
    vignette(ctx, 0.5);
    grain(ctx, Math.round(t * 30), 0.05);
  },
});
