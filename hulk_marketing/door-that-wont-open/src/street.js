// street.js: the high street set (flat vector, brand-dark dusk) and the customer, as pure functions of story
// time ts. World units: 1 = 1 px at zoom 1; x right, y down. GROUND is the shopfronts' base line.
//   shop A (deep green, blank sign, the door that won't open)  x -60..760
//   side road with a zebra crossing and Belisha beacons       x 760..1500
//   shop B (plum, blank sign, sliding doors)                   x 1500..2320
import { E, clamp, lerp, prog, mix, TAU, hash01, noise1, wobble } from '../lib/motion.js';
import { C, rr, spinner, tickBadge, pinIcon, bagIcon, lockIcon, sp } from './kit.js';

export const GROUND = 1300, KERB = GROUND + 190, FEET = GROUND + 95;
export const DOOR_A = { x0: 470, x1: 700, y0: 700, y1: GROUND, handleX: 502 };
export const DOOR_B = { x0: 1560, x1: 1800, y0: 700, y1: GROUND };
export const SPIN_A = { x: 598, y: 955, r: 64 };   // the spinner's place on door A's glass

const PAINT_A = { base: '#2C5A43', shade: '#1F3F30', light: '#3B7258', sign: '#1A3528', line: '#447A5E' };
const PAINT_B = { base: '#5A2346', shade: '#42183A', light: '#733059', sign: '#3A1430', line: '#7E3A64' };
const WARM = '#F2C27A';

const ss = (a, b, x) => { const t = clamp((x - a) / (b - a)); return t * t * (3 - 2 * t); };

// ------------------------------------------------------------------ camera
export function applyCam(ctx, cam) {
  const sx = cam.sx ?? 540, sy = cam.sy ?? 960;
  ctx.setTransform(cam.z, 0, 0, cam.z, sx - cam.x * cam.z, sy - cam.y * cam.z);
}
const logz = (a, b, p) => a * Math.pow(b / a, p);

// story camera (slow variant), ts in 0..21
export function camStory(ts, her) {
  // tracking wide shot, then push-in to the door
  if (ts < 3.4) {
    const p = E.inOutSine(clamp(ts / 3.4));
    return { x: lerp(-60, 290, p), y: 822, z: lerp(0.9, 0.94, p) };
  }
  if (ts < 7.5) {
    const p = E.inOutCubic(prog(ts, 3.4, 4.35));
    const drift = prog(ts, 4.35, 7.5);
    return { x: lerp(290, 512, p) + drift * 6, y: lerp(822, 1000, p), z: logz(0.94, 2.05, p) * (1 + 0.04 * drift) };
  }
  if (ts < 12.8) {
    const p = E.inOutCubic(prog(ts, 7.5, 8.35));
    const drift = prog(ts, 8.35, 12.8);
    return { x: lerp(518, 360, p), y: lerp(1000, 830, p), z: logz(2.13, 0.95, p) * (1 + 0.045 * E.inOutSine(drift)) };
  }
  if (ts < 18.0) {
    // follow her across the road (lagged), then ease to rest on shop B. outCubic leaves at ~410 px/s, her pace
    // at 15.6, so the pan decelerates instead of stopping dead, and it is at rest by 17.03, before the 18.0 whip.
    const fx = ts < 15.6 ? clamp(her.x + 120, 360, 1690) : lerp(camB0(), 1690, E.outCubic(prog(ts, 15.6, 17.03)));
    const p = E.inOutSine(prog(ts, 12.8, 13.6));
    return { x: lerp(360, fx, p), y: 830, z: lerp(0.993, 0.93, E.inOutSine(prog(ts, 12.8, 16.2))) };
  }
  // whip back to shop A (18.0-18.45), then the freeze framing
  const p = E.inOutCubic(prog(ts, 18.0, 18.45));
  const drift = prog(ts, 18.45, 21);
  return { x: lerp(1690, 350, p), y: lerp(830, 880, p), z: lerp(0.93, 0.98, p) * (1 + 0.035 * drift) };
}

// ------------------------------------------------------------------ her path across the road (ts >= 12.55)
// She sets off from shop A's door, drifting half a step nearer the kerb (FEET -> FEET+46, scale 1 -> 1.05), crosses
// the side road on that line, then curves up off the pavement, over shop B's threshold (GROUND) and a few steps
// into the shop (B_Y). Depth is screen y here, and her scale follows it (the replay's GROUND+6 is 0.9).
// The walk cycle advances one TAU per STRIDE * scale world px of path, so her planted boot stays put.
const STOP = 340, STRIDE = 322;
const WALK_IN_PH = 6 * Math.PI - (STOP + 520) / STRIDE * TAU;   // the stroll ends on phase 6pi: feet together
const KERB_Y = FEET + 46;
const B_X0 = 1330, B_X1 = 1725, B_Y = GROUND - 40;
const depthScale = (y) => 1 + (y - FEET) * (0.05 / 46);
// the set's depth (screen y) is foreshortened against x: a step taken straight into the scene moves her feet
// DEPTH_K px of y per px it would move them along x. Strides are measured in x-equivalent px.
export const DEPTH_K = 0.6;
export const stepLen = (dx, dy) => Math.hypot(dx, dy / DEPTH_K);
export function pathY(x) {
  const a = clamp((x - STOP) / 300), b = clamp((x - B_X0) / (B_X1 - B_X0)), q = b * b;
  return FEET + (KERB_Y - FEET) * E.inOutSine(a) - (KERB_Y - B_Y) * q * q * (3 - 2 * q);
}
function pathSlope(x) {
  const a = (x - STOP) / 300, b = (x - B_X0) / (B_X1 - B_X0);
  let s = 0;
  if (a > 0 && a < 1) s += (KERB_Y - FEET) * Math.PI / 2 * Math.sin(Math.PI * a) / 300;
  if (b > 0 && b < 1) s -= (KERB_Y - B_Y) * 12 * b ** 3 * (1 - b * b) / (B_X1 - B_X0);
  return s;
}
// stride multiplier: 1 on the crossing, easing to SK_B along the turn into shop B (solved below so her last step
// in the shop closes her feet together instead of leaving her standing mid-stride)
const bEase = (x) => { const b = clamp((x - B_X0) / (B_X1 - B_X0)), q = b * b; return q * q * (3 - 2 * q); };
let SK_B = 1;
const strideK = (x) => 1 + (SK_B - 1) * bEase(x);
// arc length (x-equivalent px) and walk cycles along the path, tabulated once per px of x (deterministic)
const PATH_N = B_X1 - STOP + 1;
const ARC = new Float64Array(PATH_N), CYC = new Float64Array(PATH_N);
function tabulate() {
  for (let i = 1; i < PATH_N; i++) {
    const xm = STOP + i - 0.5, dl = stepLen(1, pathSlope(xm));
    ARC[i] = ARC[i - 1] + dl;
    CYC[i] = CYC[i - 1] + dl / (STRIDE * depthScale(pathY(xm)) * strideK(xm));
  }
}
tabulate();
{ // end on phase = 0 mod pi (6pi + TAU * cycles): round the half-cycles down and lengthen the stride to fit
  const want = Math.floor(2 * CYC[PATH_N - 1]) / 2;
  let lo = 1, hi = 1.6;
  for (let i = 0; i < 40; i++) { SK_B = (lo + hi) / 2; tabulate(); if (CYC[PATH_N - 1] > want) lo = SK_B; else hi = SK_B; }
}
function pathAtLen(l) {
  const N = PATH_N - 1;
  if (l <= 0) return { x: STOP, cyc: 0 };
  if (l >= ARC[N]) return { x: STOP + N, cyc: CYC[N] + (l - ARC[N]) / (STRIDE * depthScale(B_Y) * SK_B) };
  let lo = 0, hi = N;
  while (hi - lo > 1) { const m = (lo + hi) >> 1; if (ARC[m] <= l) lo = m; else hi = m; }
  const f = (l - ARC[lo]) / (ARC[hi] - ARC[lo]);
  return { x: STOP + lo + f, cyc: lerp(CYC[lo], CYC[hi], f) };
}
function pathAtCyc(c) {
  const N = PATH_N - 1;
  let x;
  if (c <= 0) x = STOP + c * STRIDE;
  else if (c >= CYC[N]) x = STOP + N + (c - CYC[N]) * STRIDE * depthScale(B_Y) * SK_B;
  else {
    let lo = 0, hi = N;
    while (hi - lo > 1) { const m = (lo + hi) >> 1; if (CYC[m] <= c) lo = m; else hi = m; }
    x = STOP + lo + (c - CYC[lo]) / (CYC[hi] - CYC[lo]);
  }
  return [x, pathY(clamp(x, STOP, STOP + N))];
}
// where her boots are planted (world px of the ground under each ankle), from the path itself, so a boot stays
// exactly put even where the path curves and she shrinks: [far, near], each { at } in stance or { from, to } in swing.
// A stance is centred where the walk cycle puts it (the body passes over the boot at mid-stance).
function plantsAt(phase, cyc) {
  return [phase + Math.PI, phase].map((ph) => {
    const q = ((ph - Math.PI / 2) % TAU + TAU) % TAU, c0 = cyc - (q - Math.PI / 2) / TAU;
    if (q <= Math.PI) return { at: pathAtCyc(c0) };
    const to = pathAtCyc(c0 + 1);
    // her first step: the boot leaves from where it rested beside the other (halfway through this swing at the start)
    return { from: c0 < -0.25 ? [2 * STOP - to[0], 2 * FEET - to[1]] : pathAtCyc(c0), to };
  });
}

// pace along the path: a slow first (turning) step from 12.55, then 410 px/s across the road on exactly the old
// crossing (x = 340 + 410 (ts - 13.075)), then she slows through shop B's door and stops inside at T_IN
const V_WALK = 410, T_GO = 12.55, T_DEC = 16.15;
const X_KERB = STOP + 300, L_KERB = ARC[X_KERB - STOP];             // end of the drift toward the kerb
const T_CRUISE0 = 13.075 - (L_KERB - (X_KERB - STOP)) / V_WALK;       // cruise line l = V (ts - T_CRUISE0)
const T_RAMP = 2 * (T_CRUISE0 - T_GO);
const T_IN = T_DEC + 2 * (ARC[PATH_N - 1] - V_WALK * (T_DEC - T_CRUISE0)) / V_WALK;
const ssInt = (u) => u * u * u - u * u * u * u / 2;   // integral of smoothstep
function lenAt(ts) {
  if (ts <= T_GO) return 0;
  if (ts < T_GO + T_RAMP) return V_WALK * T_RAMP * ssInt((ts - T_GO) / T_RAMP);
  if (ts < T_DEC) return V_WALK * (ts - T_CRUISE0);
  const D = T_IN - T_DEC, u = Math.min(1, (ts - T_DEC) / D);
  return V_WALK * (T_DEC - T_CRUISE0) + V_WALK * D * (u - ssInt(u));
}
function speedAt(ts) {
  if (ts <= T_GO || ts >= T_IN) return 0;
  if (ts < T_GO + T_RAMP) return V_WALK * ss(T_GO, T_GO + T_RAMP, ts);
  return ts < T_DEC ? V_WALK : V_WALK * (1 - ss(T_DEC, T_IN, ts));
}
const CAM_B0 = clamp(herStory(15.6).x + 120, 360, 1690);   // where the camera starts easing onto shop B
const camB0 = () => CAM_B0;

// ------------------------------------------------------------------ the customer's story (slow variant)
// returns the rig state. phase = walk cycle (heel strikes at pi/2 + k*pi), driven by distance so feet don't skate;
// slope = dy/dx of her path (the leg plane's direction); stride = world scale of one STRIDE (defaults to 1).
export function herStory(ts) {
  const s = { x: -520, y: FEET, dir: 1, scale: 1, stride: 1, slope: 0, walk: 0, phase: 0, reach: 0, push: 0, watch: 0,
    sigh: 0, shift: 0, tilt: 0, smile: 0, alpha: 1, warm: 0, inside: 0, look: 0 };
  if (ts < 3.95) {
    // constant stroll, easing to a stop at the door
    const v = 290, tEase = 3.2;
    let d;
    if (ts < tEase) d = v * ts;
    else { const u = ts - tEase, T = 0.75; d = v * tEase + v * (u - u * u / (2 * T)); }
    s.x = -520 + d * ((STOP + 520) / (v * tEase + v * 0.375));
    s.walk = ts < tEase ? 1 : 1 - ss(tEase, 3.95, ts);
  } else s.x = STOP;
  s.phase = (s.x + 520) / STRIDE * TAU + WALK_IN_PH;
  // reach + two pushes
  s.reach = ss(3.85, 4.3, ts) * (1 - ss(7.1, 7.6, ts));
  s.push = Math.max(bumpP(ts, 4.36, 4.46, 4.75), 1.15 * bumpP(ts, 6.05, 6.17, 6.55));
  s.tilt = 0.12 * ss(6.4, 6.7, ts) * (1 - ss(7.3, 7.7, ts));           // puzzled head tilt
  // waiting: watch, weight shift, sigh
  s.watch = ss(9.2, 9.5, ts) * (1 - ss(10.05, 10.35, ts));
  s.shift = Math.sin(clamp((ts - 10.5) / 0.8) * Math.PI) * 1.0 - Math.sin(clamp((ts - 7.6) / 0.7) * Math.PI) * 0.5;
  s.sigh = ts < 11.6 ? 0 : ts < 11.95 ? E.inOutSine(prog(ts, 11.6, 11.95)) : 1 - 2 * E.inOutSine(prog(ts, 11.95, 12.45)) * 0.75;
  if (ts > 12.45) s.sigh = 0.25 * (1 - ss(12.45, 12.8, ts)) - 0.5 * (1 - ss(12.45, 12.8, ts));
  // leave (shot list: she turns 12.7): a slow first step that turns her off the door toward the kerb, then the walk
  // across the road on her path, over shop B's threshold and into the shop, where she stops (T_IN) and stays
  if (ts >= T_GO) {
    const P = pathAtLen(lenAt(ts));
    s.x = P.x; s.y = pathY(P.x); s.slope = pathSlope(P.x);
    s.scale = depthScale(s.y); s.stride = s.scale * strideK(P.x);
    s.phase = 6 * Math.PI + P.cyc * TAU;
    s.plants = plantsAt(s.phase, P.cyc);
    s.walk = ts < T_GO + T_RAMP ? ss(T_GO, 13.05, ts) : clamp(1.5 * speedAt(ts) / V_WALK);
    s.inside = ss(GROUND + 8, GROUND - 12, s.y);          // her feet over the threshold
    s.warm = ss(GROUND + 70, GROUND - 25, s.y);           // the shop's light, from the doorstep in
  }
  return s;
}
function bumpP(t, a, b, c) { if (t <= a || t >= c) return 0; return t < b ? E.outCubic((t - a) / (b - a)) : 1 - E.inOutSine((t - b) / (c - b)); }
export function herArrivalB() { const t0 = 12.9, v = 410; return t0 + (1640 - 350) / v + 0.35 / 2; }

// ------------------------------------------------------------------ helpers
function quad(ctx, p) { ctx.beginPath(); ctx.moveTo(p[0][0], p[0][1]); for (let i = 1; i < p.length; i++) ctx.lineTo(p[i][0], p[i][1]); ctx.closePath(); }
function glassOver(ctx, x, y, w, h, tint = 0.08, seed = 1) {
  ctx.save();
  ctx.fillStyle = `rgba(170,214,198,${tint})`; ctx.fillRect(x, y, w, h);
  ctx.beginPath(); ctx.rect(x, y, w, h); ctx.clip();
  // two diagonal reflection streaks
  ctx.fillStyle = 'rgba(255,255,255,0.06)';
  const o = (seed * 37) % 40;
  ctx.beginPath(); ctx.moveTo(x + w * 0.15 + o, y); ctx.lineTo(x + w * 0.42 + o, y); ctx.lineTo(x + w * 0.02 + o, y + h); ctx.lineTo(x - w * 0.25 + o, y + h); ctx.closePath(); ctx.fill();
  ctx.fillStyle = 'rgba(255,255,255,0.035)';
  ctx.beginPath(); ctx.moveTo(x + w * 0.58 + o, y); ctx.lineTo(x + w * 0.66 + o, y); ctx.lineTo(x + w * 0.3 + o, y + h); ctx.lineTo(x + w * 0.22 + o, y + h); ctx.closePath(); ctx.fill();
  ctx.restore();
}
function sash(ctx, x, y, w, h, lit, frame = '#2B342E') {
  ctx.fillStyle = frame; ctx.fillRect(x - 10, y - 10, w + 20, h + 20);
  ctx.fillStyle = '#121915'; ctx.fillRect(x - 16, y + h + 8, w + 32, 14);  // sill
  const g = ctx.createLinearGradient(0, y, 0, y + h);
  if (lit > 0) { g.addColorStop(0, mix('#151D19', '#7A5A2E', lit)); g.addColorStop(1, mix('#101613', '#C08A44', lit)); }
  else { g.addColorStop(0, '#141C18'); g.addColorStop(1, '#0E1411'); }
  ctx.fillStyle = g; ctx.fillRect(x, y, w, h);
  ctx.fillStyle = frame;
  ctx.fillRect(x, y + h / 2 - 5, w, 10); ctx.fillRect(x + w / 2 - 3, y, 6, h);
  glassOver(ctx, x, y, w, h, 0.03, x);
}

// ------------------------------------------------------------------ interiors
function interior(ctx, x, y, w, h, kind, warm, seed) {
  ctx.save(); ctx.beginPath(); ctx.rect(x, y, w, h); ctx.clip();
  const dim = kind === 'A' ? ['#0F1814', '#152119'] : ['#1C1018', '#24141F'];
  const lit = ['#4A3420', '#7A5530'];
  const g = ctx.createLinearGradient(0, y, 0, y + h);
  g.addColorStop(0, mix(dim[0], lit[0], warm)); g.addColorStop(1, mix(dim[1], lit[1], warm));
  ctx.fillStyle = g; ctx.fillRect(x, y, w, h);
  // shelves with goods, back wall
  const shelfC = mix('#1E2B24', '#6B4A2A', warm);
  for (let i = 0; i < 3; i++) {
    const sy = y + h * (0.32 + i * 0.2);
    ctx.fillStyle = shelfC; ctx.fillRect(x - 10, sy, w + 20, 7);
    for (let j = 0; j < 9; j++) {
      const r = hash01(j + i * 13, seed);
      const gx = x + (j / 9) * w + r * 12, gw = 18 + r * 22, gh = 24 + hash01(j, seed + i) * 40;
      const cols = kind === 'A' ? ['#3E6B52', '#B8833E', '#8C4B3A', '#D9C8A2'] : ['#8C4B6E', '#D0A35A', '#5B7C8A', '#E0CBB0'];
      ctx.fillStyle = mix(mix('#18221D', cols[j % 4], 0.35), cols[j % 4], warm * 0.85);
      rr(ctx, gx, sy - gh, gw, gh, 4); ctx.fill();
    }
  }
  // pendant lamps
  for (let i = 0; i < 2; i++) {
    const lx = x + w * (0.3 + i * 0.4), ly = y + h * 0.12;
    ctx.strokeStyle = mix('#26322B', '#5A4A38', warm); ctx.lineWidth = 3;
    ctx.beginPath(); ctx.moveTo(lx, y); ctx.lineTo(lx, ly); ctx.stroke();
    ctx.fillStyle = mix('#26322B', '#E9B872', warm);
    ctx.beginPath(); ctx.moveTo(lx - 22, ly + 22); ctx.lineTo(lx + 22, ly + 22); ctx.lineTo(lx + 10, ly); ctx.lineTo(lx - 10, ly); ctx.closePath(); ctx.fill();
    if (warm > 0.05) {
      const rg = ctx.createRadialGradient(lx, ly + 26, 4, lx, ly + 40, 210);
      rg.addColorStop(0, `rgba(242,194,122,${0.55 * warm})`); rg.addColorStop(1, 'rgba(242,194,122,0)');
      ctx.fillStyle = rg; ctx.fillRect(lx - 220, ly - 180, 440, 440);
    }
  }
  ctx.restore();
}

// ------------------------------------------------------------------ buildings
function upperFloor(ctx, x0, x1, top, base, wall, lits, seed) {
  ctx.fillStyle = wall; ctx.fillRect(x0, top, x1 - x0, base - top);
  // brick courses, very faint
  ctx.strokeStyle = 'rgba(255,255,255,0.022)'; ctx.lineWidth = 2;
  for (let y = top + 40; y < base; y += 34) { ctx.beginPath(); ctx.moveTo(x0, y); ctx.lineTo(x1, y); ctx.stroke(); }
  // parapet + cornice
  ctx.fillStyle = mix(wall, '#000000', 0.25); ctx.fillRect(x0 - 8, top - 30, x1 - x0 + 16, 30);
  ctx.fillStyle = mix(wall, '#FFFFFF', 0.05); ctx.fillRect(x0 - 12, top - 6, x1 - x0 + 24, 8);
  // chimney stack
  const cx = x0 + (x1 - x0) * (0.7 + 0.1 * hash01(seed, 4));
  ctx.fillStyle = mix(wall, '#000000', 0.3); ctx.fillRect(cx, top - 150, 92, 122);
  ctx.fillStyle = mix(wall, '#FFFFFF', 0.04); ctx.fillRect(cx - 8, top - 158, 108, 14);
  for (let i = 0; i < 3; i++) { ctx.fillStyle = '#2A2420'; ctx.fillRect(cx + 10 + i * 28, top - 190, 18, 34); }
  // sash windows
  const n = lits.length, ww = 170, wh = 290;
  for (let i = 0; i < n; i++) {
    const wx = x0 + (x1 - x0) * ((i + 0.5) / n) - ww / 2;
    sash(ctx, wx, top + 60, ww, wh, lits[i]);
  }
}

function pilaster(ctx, x, y0, y1, P) {
  ctx.fillStyle = P.shade; ctx.fillRect(x, y0, 40, y1 - y0);
  ctx.fillStyle = P.base; ctx.fillRect(x + 6, y0, 28, y1 - y0);
  ctx.fillStyle = P.light; ctx.fillRect(x + 6, y0, 4, y1 - y0);
  ctx.fillStyle = P.base; ctx.fillRect(x - 6, y0 - 4, 52, 70);  // console
  ctx.fillStyle = P.light; ctx.fillRect(x - 6, y0 - 4, 52, 5);
}

function fascia(ctx, x0, x1, P) {
  ctx.fillStyle = P.light; ctx.fillRect(x0 - 26, 438, x1 - x0 + 52, 14);   // cornice
  ctx.fillStyle = P.base; ctx.fillRect(x0 - 16, 452, x1 - x0 + 32, 118);
  ctx.fillStyle = P.sign; ctx.fillRect(x0 + 14, 470, x1 - x0 - 28, 82);    // blank sign panel
  ctx.strokeStyle = P.line; ctx.lineWidth = 3; ctx.strokeRect(x0 + 14, 470, x1 - x0 - 28, 82);
}

// shop A: window left, recessed door right (hinge on the right, handle on the left)
function shopA(ctx, ts, st) {
  const P = PAINT_A;
  upperFloor(ctx, -60, 760, -230, 438, '#18201C', [0, 0.65], 3);
  pilaster(ctx, -60, 520, GROUND, P); pilaster(ctx, 720, 520, GROUND, P);
  fascia(ctx, -20, 720, P);
  ctx.fillStyle = P.base; ctx.fillRect(-20, 570, 740, GROUND - 570);
  // display window
  interior(ctx, 0, 600, 430, 540, 'A', st.warmA * 0.9 + 0.12, 5);
  ctx.fillStyle = P.shade; ctx.fillRect(208, 600, 14, 540);                 // mullion
  glassOver(ctx, 0, 600, 430, 540, 0.07, 2);
  ctx.strokeStyle = P.light; ctx.lineWidth = 6; ctx.strokeRect(0, 600, 430, 540);
  // stallriser
  ctx.fillStyle = P.shade; ctx.fillRect(0, 1150, 430, GROUND - 1150);
  ctx.strokeStyle = P.light; ctx.lineWidth = 3; ctx.strokeRect(20, 1170, 390, GROUND - 1190);
  // transom over the door + recess
  interior(ctx, DOOR_A.x0, 600, DOOR_A.x1 - DOOR_A.x0, 86, 'A', st.warmA * 0.9 + 0.12, 9);
  glassOver(ctx, DOOR_A.x0, 600, DOOR_A.x1 - DOOR_A.x0, 86, 0.08, 4);
  ctx.fillStyle = P.light; ctx.fillRect(DOOR_A.x0 - 8, 686, DOOR_A.x1 - DOOR_A.x0 + 16, 14);
  ctx.fillStyle = '#0B110E'; ctx.fillRect(DOOR_A.x0, DOOR_A.y0, DOOR_A.x1 - DOOR_A.x0, GROUND - DOOR_A.y0);
  // the opening behind the door: interior (seen when the door swings)
  interior(ctx, DOOR_A.x0, DOOR_A.y0, DOOR_A.x1 - DOOR_A.x0, GROUND - DOOR_A.y0 - 6, 'A', st.warmA * 0.95 + 0.1, 12);
  // her, once she crosses the jamb into shop A (replay): the inside part sits behind the swung door
  if (st.her && st.enterA) {
    ctx.save(); ctx.beginPath(); ctx.rect(DOOR_A.x0, DOOR_A.y0, DOOR_A.x1 - DOOR_A.x0, GROUND - DOOR_A.y0 + 200); ctx.clip();
    drawHer(ctx, st.her); ctx.restore();
  }
  doorA(ctx, ts, st);
  // threshold step
  ctx.fillStyle = '#2B332E'; ctx.fillRect(DOOR_A.x0 - 14, GROUND - 6, DOOR_A.x1 - DOOR_A.x0 + 28, 10);
}

// door A panel, swung about its right-hand hinge by st.swing (0 shut .. 1 open ~78 deg), judder st.judder (px)
function doorA(ctx, ts, st) {
  const { x0, x1, y0, y1 } = DOOR_A;
  const W = x1 - x0, H = y1 - y0 - 6;
  const th = st.swing * 1.36, cw = Math.cos(th), taper = Math.sin(th) * 0.07 * H;
  const j = st.judder;
  const M = (u, v) => {   // door-local (u 0..1 left->right, v 0..1 top->bottom) -> world
    const X = x1 - (1 - u) * W * cw + j * (1 - u);
    const Y = y0 + v * H + (1 - u) * taper * (1 - 2 * v) * -1;
    return [X, Y];
  };
  const R = (u0, v0, u1, v1) => [M(u0, v0), M(u1, v0), M(u1, v1), M(u0, v1)];
  const P = PAINT_A;
  ctx.save();
  // frame
  ctx.fillStyle = P.base; quad(ctx, R(0, 0, 1, 1)); ctx.fill();
  // glass (with what's behind it: the interior, dim unless open)
  const gu0 = 22 / W, gu1 = 1 - 22 / W, gv0 = 24 / H, gv1 = 1 - 132 / H;
  ctx.save(); quad(ctx, R(gu0, gv0, gu1, gv1)); ctx.clip();
  interior(ctx, x0, y0, W, H, 'A', st.warmA * 0.9 + 0.12, 21);
  ctx.fillStyle = 'rgba(170,214,198,0.08)'; ctx.fillRect(x0 - 50, y0, W + 100, H);
  // reflection streaks follow the panel
  const g1 = M(0.12, 0), g2 = M(0.42, 0), g3 = M(0.02, 1), g4 = M(-0.25, 1);
  ctx.fillStyle = `rgba(255,255,255,${0.065 + 0.05 * st.flex})`; quad(ctx, [g1, g2, g3, g4]); ctx.fill();
  const h1 = M(0.6, 0), h2 = M(0.68, 0), h3 = M(0.3, 1), h4 = M(0.22, 1);
  ctx.fillStyle = 'rgba(255,255,255,0.035)'; quad(ctx, [h1, h2, h3, h4]); ctx.fill();
  // the spinner lives ON the glass: drawn here so it rides with the panel and sits under the sheen
  if (st.spinA > 0 && st.swing < 0.02) {
    const sx = SPIN_A.x + j * 0.5;
    spinner(ctx, sx, SPIN_A.y, SPIN_A.r * lerp(0.7, 1, E.outBack(clamp(st.spinA))), 15, st.spinAng, st.spinLen, clamp(st.spinA * 1.4), 0.9);
    if (st.tick > 0) tickBadge(ctx, sx, SPIN_A.y, SPIN_A.r * 0.92, st.tick, 1);
    // glass sheen over the spinner so it reads as part of the door
    const sg = ctx.createLinearGradient(sx - 90, SPIN_A.y - 90, sx + 90, SPIN_A.y + 90);
    sg.addColorStop(0.35, 'rgba(255,255,255,0)'); sg.addColorStop(0.5, 'rgba(255,255,255,0.08)'); sg.addColorStop(0.65, 'rgba(255,255,255,0)');
    ctx.fillStyle = sg; ctx.fillRect(sx - 100, SPIN_A.y - 100, 200, 200);
  }
  ctx.restore();
  ctx.strokeStyle = P.light; ctx.lineWidth = 4; quad(ctx, R(gu0, gv0, gu1, gv1)); ctx.stroke();
  // kick panel
  ctx.fillStyle = P.shade; quad(ctx, R(0.06, 1 - 112 / H, 0.94, 1 - 14 / H)); ctx.fill();
  ctx.strokeStyle = P.light; ctx.lineWidth = 2.5; quad(ctx, R(0.12, 1 - 100 / H, 0.88, 1 - 26 / H)); ctx.stroke();
  // brass pull bar (left), with stand-offs
  const hb = R(26 / W, 0.36, 40 / W, 0.62);
  ctx.fillStyle = '#C9A04A'; quad(ctx, hb); ctx.fill();
  ctx.fillStyle = '#E7C574'; quad(ctx, R(28 / W, 0.37, 32 / W, 0.61)); ctx.fill();
  ctx.fillStyle = '#8C6A2A'; quad(ctx, R(24 / W, 0.39, 44 / W, 0.405)); ctx.fill(); quad(ctx, R(24 / W, 0.575, 44 / W, 0.59)); ctx.fill();
  ctx.restore();
}

function shopB(ctx, ts, st) {
  const P = PAINT_B;
  upperFloor(ctx, 1500, 2320, -230, 438, '#1C1820', [0.75, 0, 0.55], 8);
  pilaster(ctx, 1500, 520, GROUND, P); pilaster(ctx, 2280, 520, GROUND, P);
  fascia(ctx, 1540, 2280, P);
  ctx.fillStyle = P.base; ctx.fillRect(1540, 570, 740, GROUND - 570);
  // window right
  interior(ctx, 1850, 600, 410, 540, 'B', 0.78, 31);
  ctx.fillStyle = P.shade; ctx.fillRect(2048, 600, 14, 540);
  glassOver(ctx, 1850, 600, 410, 540, 0.06, 6);
  ctx.strokeStyle = P.light; ctx.lineWidth = 6; ctx.strokeRect(1850, 600, 410, 540);
  ctx.fillStyle = P.shade; ctx.fillRect(1850, 1150, 410, GROUND - 1150);
  ctx.strokeStyle = P.light; ctx.lineWidth = 3; ctx.strokeRect(1870, 1170, 370, GROUND - 1190);
  // transom
  interior(ctx, DOOR_B.x0, 600, DOOR_B.x1 - DOOR_B.x0, 86, 'B', 0.78, 33);
  glassOver(ctx, DOOR_B.x0, 600, DOOR_B.x1 - DOOR_B.x0, 86, 0.06, 7);
  ctx.fillStyle = P.light; ctx.fillRect(DOOR_B.x0 - 8, 686, DOOR_B.x1 - DOOR_B.x0 + 16, 14);
  // doorway interior (brighter when open)
  interior(ctx, DOOR_B.x0, DOOR_B.y0, DOOR_B.x1 - DOOR_B.x0, GROUND - DOOR_B.y0, 'B', 0.78 + 0.22 * st.openB, 35);
  // her, inside, behind the sliding glass (drawn by the caller through st.drawInsideB)
  if (st.drawInsideB) st.drawInsideB(ctx);
  // sliding panels
  const o = st.openB, pw = (DOOR_B.x1 - DOOR_B.x0) / 2;
  ctx.save(); ctx.beginPath(); ctx.rect(DOOR_B.x0, DOOR_B.y0, DOOR_B.x1 - DOOR_B.x0, GROUND - DOOR_B.y0); ctx.clip();
  for (const side of [-1, 1]) {
    const px = side < 0 ? DOOR_B.x0 - o * (pw - 12) : DOOR_B.x0 + pw + o * (pw - 12);
    // aluminium frame + glass (the warm interior shows through)
    glassOver(ctx, px + 8, DOOR_B.y0 + 8, pw - 16, GROUND - DOOR_B.y0 - 20, 0.1, side + 9);
    ctx.strokeStyle = '#3A3A40'; ctx.lineWidth = 12; ctx.strokeRect(px + 6, DOOR_B.y0 + 6, pw - 12, GROUND - DOOR_B.y0 - 16);
    ctx.strokeStyle = '#55555C'; ctx.lineWidth = 2; ctx.strokeRect(px + 12, DOOR_B.y0 + 12, pw - 24, GROUND - DOOR_B.y0 - 28);
    ctx.fillStyle = '#9EA3A0'; ctx.fillRect(px + (side < 0 ? pw - 22 : 14), DOOR_B.y0 + 250, 8, 120);
  }
  ctx.restore();
  // brass shop bell above the door, swings when the door opens
  const bx = DOOR_B.x0 + 30, by = 712;
  const sw = 0.5 * wobble(ts - st.bellT, 2.6, 2.2);
  ctx.save(); ctx.translate(bx, by); ctx.rotate(sw);
  ctx.strokeStyle = '#8C6A2A'; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(0, 16); ctx.stroke();
  ctx.fillStyle = '#D6AE58'; ctx.beginPath(); ctx.moveTo(-14, 42); ctx.quadraticCurveTo(-14, 14, 0, 14); ctx.quadraticCurveTo(14, 14, 14, 42); ctx.closePath(); ctx.fill();
  ctx.fillStyle = '#8C6A2A'; ctx.beginPath(); ctx.arc(0, 45, 4, 0, TAU); ctx.fill();
  ctx.restore();
  ctx.fillStyle = '#3A3036'; ctx.fillRect(DOOR_B.x0 - 14, GROUND - 6, DOOR_B.x1 - DOOR_B.x0 + 28, 10);
}

function neighbour(ctx, x0, x1, wall, lits, seed, shutter = true) {
  upperFloor(ctx, x0, x1, -230, 438, wall, lits, seed);
  const P = { base: '#22262A', shade: '#1A1D20', light: '#30353A', sign: '#1A1D20', line: '#30353A' };
  pilaster(ctx, x0, 520, GROUND, P); pilaster(ctx, x1 - 40, 520, GROUND, P);
  fascia(ctx, x0 + 40, x1 - 40, P);
  ctx.fillStyle = P.base; ctx.fillRect(x0 + 40, 570, x1 - x0 - 80, GROUND - 570);
  if (shutter) {
    ctx.fillStyle = '#1B1F22'; ctx.fillRect(x0 + 70, 610, x1 - x0 - 140, GROUND - 610);
    ctx.strokeStyle = '#262B2F'; ctx.lineWidth = 3;
    for (let y = 624; y < GROUND; y += 18) { ctx.beginPath(); ctx.moveTo(x0 + 70, y); ctx.lineTo(x1 - 70, y); ctx.stroke(); }
  }
}

// the side road between the shops: distant vista, receding road, zebra, beacons
function vista(ctx, cam) {
  const px = (cam.x - 1130) * 0.12;
  ctx.save(); ctx.beginPath(); ctx.rect(760, -400, 740, GROUND + 10 + 400); ctx.clip();
  ctx.translate(px, 0);
  const hz = 760, vx = 1130;
  // distant terraces either side of the side road
  for (const side of [-1, 1]) {
    ctx.fillStyle = '#111814';
    ctx.beginPath();
    const near = side < 0 ? 760 - px : 1500 - px, far = vx + side * 70;
    ctx.moveTo(near, GROUND); ctx.lineTo(near, 120); ctx.lineTo(far, hz - 170); ctx.lineTo(far, hz); ctx.closePath(); ctx.fill();
    // windows in perspective
    for (let i = 0; i < 6; i++) {
      const u = (i + 0.5) / 6, x = lerp(near, far, u), top = lerp(220, hz - 140, u), bot = lerp(GROUND - 300, hz - 20, u);
      const lit = hash01(i, side + 5) > 0.45;
      ctx.fillStyle = lit ? 'rgba(233,184,114,0.55)' : 'rgba(30,40,34,0.9)';
      const w = lerp(34, 6, u);
      ctx.fillRect(x - w / 2, top + (bot - top) * 0.15, w, (bot - top) * 0.22);
      ctx.fillRect(x - w / 2, top + (bot - top) * 0.55, w, (bot - top) * 0.22);
    }
  }
  // road surface
  ctx.fillStyle = '#101513';
  ctx.beginPath(); ctx.moveTo(790 - px, GROUND); ctx.lineTo(vx - 40, hz); ctx.lineTo(vx + 40, hz); ctx.lineTo(1470 - px, GROUND); ctx.closePath(); ctx.fill();
  // pavements of the side road
  ctx.fillStyle = '#151B18';
  ctx.beginPath(); ctx.moveTo(760 - px, GROUND); ctx.lineTo(vx - 70, hz); ctx.lineTo(vx - 40, hz); ctx.lineTo(790 - px, GROUND); ctx.closePath(); ctx.fill();
  ctx.beginPath(); ctx.moveTo(1500 - px, GROUND); ctx.lineTo(vx + 70, hz); ctx.lineTo(vx + 40, hz); ctx.lineTo(1470 - px, GROUND); ctx.closePath(); ctx.fill();
  // dashed centre line receding
  ctx.strokeStyle = 'rgba(200,206,196,0.28)';
  for (let i = 0; i < 7; i++) {
    const u0 = i / 7, u1 = (i + 0.45) / 7;
    const p0 = 1 - Math.pow(1 - u0, 2.2), p1 = 1 - Math.pow(1 - u1, 2.2);
    ctx.lineWidth = lerp(8, 1.5, p0);
    ctx.beginPath(); ctx.moveTo(lerp(1130 - px * 0, vx, p0), lerp(GROUND, hz, p0)); ctx.lineTo(lerp(1130, vx, p1), lerp(GROUND, hz, p1)); ctx.stroke();
  }
  // a distant street lamp
  const lx = vx + 120, ly = hz - 120;
  const rg = ctx.createRadialGradient(lx, ly, 2, lx, ly, 90);
  rg.addColorStop(0, 'rgba(242,194,122,0.5)'); rg.addColorStop(1, 'rgba(242,194,122,0)');
  ctx.fillStyle = rg; ctx.fillRect(lx - 90, ly - 90, 180, 180);
  ctx.fillStyle = '#1C2420'; ctx.fillRect(lx - 2, ly, 4, 110);
  ctx.restore();
}

function lampPost(ctx, x, warm = 1) {
  ctx.fillStyle = '#161B18'; ctx.fillRect(x - 9, GROUND - 640, 18, 640 + 150);
  ctx.fillRect(x - 20, GROUND + 120, 40, 40);
  ctx.fillStyle = '#1E2521'; ctx.fillRect(x - 30, GROUND - 700, 60, 12);
  ctx.fillStyle = mix('#3A3020', WARM, 0.8 * warm);
  ctx.beginPath(); ctx.moveTo(x - 26, GROUND - 690); ctx.lineTo(x + 26, GROUND - 690); ctx.lineTo(x + 18, GROUND - 630); ctx.lineTo(x - 18, GROUND - 630); ctx.closePath(); ctx.fill();
  ctx.fillStyle = '#1E2521'; ctx.fillRect(x - 24, GROUND - 632, 48, 8);
  const rg = ctx.createRadialGradient(x, GROUND - 660, 6, x, GROUND - 640, 260);
  rg.addColorStop(0, `rgba(242,194,122,${0.36 * warm})`); rg.addColorStop(1, 'rgba(242,194,122,0)');
  ctx.fillStyle = rg; ctx.fillRect(x - 270, GROUND - 920, 540, 560);
  // pool of light on the pavement
  const pg = ctx.createRadialGradient(x, GROUND + 100, 10, x, GROUND + 100, 240);
  pg.addColorStop(0, `rgba(242,194,122,${0.12 * warm})`); pg.addColorStop(1, 'rgba(242,194,122,0)');
  ctx.fillStyle = pg; ctx.fillRect(x - 250, GROUND, 500, 190);
}

function beacon(ctx, x, ts) {
  // Belisha beacon: striped pole, amber globe blinking at ~1.2 Hz
  for (let y = GROUND - 330, i = 0; y < GROUND + 170; y += 46, i++) {
    ctx.fillStyle = i % 2 ? '#E8ECE6' : '#151816';
    ctx.fillRect(x - 8, y, 16, Math.min(46, GROUND + 170 - y));
  }
  const on = 0.55 + 0.45 * Math.max(0, Math.sin(ts * TAU * 0.6));
  const rg = ctx.createRadialGradient(x, GROUND - 360, 4, x, GROUND - 360, 120);
  rg.addColorStop(0, `rgba(242,163,58,${0.45 * on})`); rg.addColorStop(1, 'rgba(242,163,58,0)');
  ctx.fillStyle = rg; ctx.fillRect(x - 120, GROUND - 480, 240, 240);
  ctx.fillStyle = mix('#7A4A16', '#F2A33A', on); ctx.beginPath(); ctx.arc(x, GROUND - 360, 28, 0, TAU); ctx.fill();
  ctx.fillStyle = 'rgba(255,255,255,0.25)'; ctx.beginPath(); ctx.arc(x - 9, GROUND - 369, 8, 0, TAU); ctx.fill();
}

function pavement(ctx, x0, x1) {
  ctx.fillStyle = '#171D19'; ctx.fillRect(x0, GROUND, x1 - x0, 190);
  ctx.strokeStyle = '#1F2621'; ctx.lineWidth = 3;
  for (let x = Math.ceil(x0 / 130) * 130; x < x1; x += 130) { ctx.beginPath(); ctx.moveTo(x, GROUND); ctx.lineTo(x - 24, KERB); ctx.stroke(); }
  ctx.beginPath(); ctx.moveTo(x0, GROUND + 92); ctx.lineTo(x1, GROUND + 92); ctx.stroke();
  ctx.fillStyle = '#262E28'; ctx.fillRect(x0, KERB, x1 - x0, 12);
  ctx.fillStyle = '#1B211D'; ctx.fillRect(x0, KERB + 12, x1 - x0, 8);
}

function road(ctx, x0, x1) {
  ctx.fillStyle = '#0D110F'; ctx.fillRect(x0, KERB + 20, x1 - x0, 1400);
  ctx.fillStyle = 'rgba(200,206,196,0.16)';
  for (let x = Math.floor(x0 / 260) * 260; x < x1; x += 260) ctx.fillRect(x, KERB + 330, 140, 10);
}

function zebra(ctx) {
  // the side road's mouth across the pavement band: tarmac + stripes (parallelograms towards the vanishing point)
  ctx.fillStyle = '#101412'; ctx.fillRect(790, GROUND, 680, 190);
  for (let i = 0; i < 7; i++) {
    const x = 810 + i * 96;
    const top = lerp(x, 1130, 0.08), bot = lerp(x, 1130, -0.06);
    ctx.fillStyle = 'rgba(214,220,210,0.78)';
    ctx.beginPath(); ctx.moveTo(top, GROUND + 14); ctx.lineTo(top + 48, GROUND + 14); ctx.lineTo(bot + 52, KERB - 6); ctx.lineTo(bot, KERB - 6); ctx.closePath(); ctx.fill();
  }
  // dropped kerbs
  ctx.fillStyle = '#262E28'; ctx.fillRect(760, GROUND, 30, 190); ctx.fillRect(1470, GROUND, 30, 190);
}

// warm light spilling out of an open door onto the pavement
function spill(ctx, x0, x1, k) {
  if (k <= 0.01) return;
  const g = ctx.createLinearGradient(0, GROUND, 0, KERB + 60);
  g.addColorStop(0, `rgba(242,194,122,${0.42 * k})`); g.addColorStop(1, 'rgba(242,194,122,0)');
  ctx.fillStyle = g;
  ctx.beginPath(); ctx.moveTo(x0, GROUND); ctx.lineTo(x1, GROUND); ctx.lineTo(x1 + 120, KERB + 60); ctx.lineTo(x0 - 120, KERB + 60); ctx.closePath(); ctx.fill();
  const rg = ctx.createRadialGradient((x0 + x1) / 2, (GROUND + 900) / 2 + 300, 20, (x0 + x1) / 2, GROUND - 250, 520);
  rg.addColorStop(0, `rgba(242,194,122,${0.16 * k})`); rg.addColorStop(1, 'rgba(242,194,122,0)');
  ctx.fillStyle = rg; ctx.fillRect(x0 - 520, GROUND - 780, x1 - x0 + 1040, 1000);
}

// ------------------------------------------------------------------ the customer (flat vector rig)
const SKIN = '#9A6545', SKIN_SH = '#7E4F36', HAIR = '#1C1615', COAT = '#C8453A', COAT_SH = '#A2362D', COAT_DK = '#7E2620';
const TIGHTS = '#2A2E3A', TIGHTS_FAR = '#1E212B', BOOT = '#16161A', GLOVE = '#4A2C22', BAG = '#7A4A2A', BAG_L = '#8E5733';
// her paints. The shop's warm light (s.warm) tints her own colours toward WARM by up to 0.22, the same result the
// old source-atop wash gave inside her silhouette, without washing a box over the set around her.
const PAINTS = { SKIN, SKIN_SH, HAIR, COAT, COAT_SH, COAT_DK, TIGHTS, TIGHTS_FAR, BOOT, GLOVE, BAG, BAG_L,
  BRASS: '#C9A04A', SOLE: '#26262C', SOLE_FAR: '#101013', STRAP: '#5E381F', DIAL: '#D9C9A0', HAND: '#2A2420',
  EYE: '#1A1210', MOUTH: '#5A2A22', SHADE: '#5A1410', CHEEK: '#C85A46' };
let K = PAINTS;   // reassigned from s.warm at the top of every drawHer() call: nothing carries between frames
function paints(k) {
  if (k <= 0.001) return PAINTS;
  const o = {};
  for (const n in PAINTS) o[n] = mix(PAINTS[n], WARM, k);
  return o;
}
const rgba = (hex, a) => { const n = parseInt(hex.slice(1), 16); return `rgba(${n >> 16},${(n >> 8) & 255},${n & 255},${a})`; };

function limb(ctx, x, y, a1, l1, a2, l2, w1, w2, col) {
  // a: angle from straight down, + = forward (towards +x)
  const ex = x + Math.sin(a1) * l1, ey = y + Math.cos(a1) * l1;
  const hx = ex + Math.sin(a2) * l2, hy = ey + Math.cos(a2) * l2;
  ctx.strokeStyle = col; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  ctx.lineWidth = w1; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(ex, ey); ctx.stroke();
  ctx.lineWidth = w2; ctx.beginPath(); ctx.moveTo(ex, ey); ctx.lineTo(hx, hy); ctx.stroke();
  return [hx, hy, ex, ey];
}

// legs: a planted-foot walk. One TAU of phase is STRIDE * s.stride world px of path, along her path's direction
// (1, s.slope) in x and depth (depth reads as screen y). Through stance (cos(phase) <= 0) the boot moves back
// linearly at exactly her pace, so it stays put on the ground (rolling onto the heel at the strike and off the toe
// at the end); the swing lifts it forward to the next plant. Each leg is solved by two-bone IK in its walking plane
// and projected to the screen, and the hips ride over the planted leg, lowest when both feet are down.
const LEG1 = 100, LEG2 = 98, LEGL = LEG1 + LEG2, ANKLE_Y = -7;
const HEEL = [-16, 9], TOE = [40, 9];
function pivot(p, piv, a) {   // turn the boot by a about its heel or toe (that point stays on the ground)
  const c = Math.cos(a), s = Math.sin(a);
  p[0] += piv[0] - (piv[0] * c - piv[1] * s); p[1] += piv[1] - (piv[0] * s + piv[1] * c); p[2] = a;
  return p;
}
function stanceFoot(u, G, at) {   // u: 0 heel strike .. 1 toe-off -> [ankle x, ankle y, boot angle], her local px
  let p;
  if (at) p = [(at[0] - G.wx) / G.sc, ANKLE_Y + (at[1] - G.wy) / G.sc, 0];   // the boot's plant on the ground
  else { const w = G.X * (1 - 2 * u); p = [w * G.c, ANKLE_Y + w * G.sl * G.c, 0]; }   // straight path, steady scale
  if (u < 0.16) return pivot(p, HEEL, -0.2 * G.walk * (1 - E.inOutSine(u / 0.16)));
  if (u > 0.66) return pivot(p, TOE, 0.42 * G.walk * E.inOutSine((u - 0.66) / 0.34));
  return p;
}
function footAt(phase, G, pl) {
  const q = ((phase - Math.PI / 2) % TAU + TAU) % TAU;
  if (q <= Math.PI) return stanceFoot(q / Math.PI, G, pl && pl.at);
  const v = (q - Math.PI) / Math.PI, e = (1 - Math.cos(Math.PI * v)) / 2, up = Math.sin(Math.PI * v);
  const a = stanceFoot(1, G, pl && pl.from), b = stanceFoot(0, G, pl && pl.to);
  return [lerp(a[0], b[0], e), lerp(a[1], b[1], e) - 30 * G.walk * up, lerp(a[2], b[2], e) + 0.25 * G.walk * up];
}
function leg(ctx, G, phase, far) {
  const F = footAt(phase, G, G.plants && G.plants[far ? 0 : 1]);
  const hx = (far ? -8 : 6) + G.shift, hy = G.hipY;
  // screen -> walking plane (w along the path, v vertical), IK with the knee forward, and back to the screen
  const Hw = hx / G.c, Hv = hy - hx * G.sl, Fw = F[0] / G.c, Fv = F[1] - F[0] * G.sl;
  let dw = Fw - Hw, dv = Fv - Hv, d = Math.hypot(dw, dv);
  const f = clamp(d / (LEGL * 0.999), 1, 1.08);   // a touch of stretch (the breath, a long toe-off), never a lifted foot
  const l1 = LEG1 * f, l2 = LEG2 * f, L = (l1 + l2) * 0.9995;
  if (d > L) { dw *= L / d; dv *= L / d; d = L; }
  const th = Math.atan2(dw, dv) + Math.acos(clamp((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d), -1, 1));
  const kw = Hw + Math.sin(th) * l1, kv = Hv + Math.cos(th) * l1, aw = Hw + dw, av = Hv + dv;
  const kx = kw * G.c, ky = kv + kw * G.sl * G.c, ax = aw * G.c, ay = av + aw * G.sl * G.c;
  ctx.strokeStyle = far ? K.TIGHTS_FAR : K.TIGHTS; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  ctx.lineWidth = 30; ctx.beginPath(); ctx.moveTo(hx, hy); ctx.lineTo(kx, ky); ctx.stroke();
  ctx.lineWidth = 26; ctx.beginPath(); ctx.moveTo(kx, ky); ctx.lineTo(ax, ay); ctx.stroke();
  // boot
  ctx.save(); ctx.translate(ax, ay); ctx.rotate(F[2]);
  ctx.fillStyle = K.BOOT;
  ctx.beginPath(); ctx.moveTo(-15, -40); ctx.lineTo(13, -40); ctx.lineTo(14, -12); ctx.quadraticCurveTo(40, -10, 42, 6); ctx.lineTo(-16, 8); ctx.closePath(); ctx.fill();
  ctx.fillStyle = far ? K.SOLE_FAR : K.SOLE; ctx.fillRect(-16, 3, 58, 6);
  ctx.restore();
}

function arm(ctx, s, far, swing) {
  // poses override the swing: reach/push the door, check the watch
  let a1 = swing, a2 = swing + 0.25;
  if (!far) {
    const r = s.reach;
    a1 = lerp(a1, 1.45 + 0.1 * s.push, r);
    a2 = lerp(a2, 1.95 - 0.12 * s.push, r);
    const w = s.watch;
    a1 = lerp(a1, -0.12, w); a2 = lerp(a2, 2.0, w);
  }
  const sx = far ? -10 : 4, sy = -366 - 6 * s.sighUp;
  const col = far ? K.COAT_DK : K.COAT_SH;
  const [hx, hy, ex, ey] = limb(ctx, sx, sy, a1, 92, a2, 84, far ? 30 : 32, far ? 26 : 28, col);
  // sleeve cuff + glove (mitten with thumb)
  ctx.fillStyle = K.GLOVE;
  ctx.beginPath(); ctx.ellipse(hx, hy, 15, 17, a2, 0, TAU); ctx.fill();
  ctx.beginPath(); ctx.ellipse(hx + Math.cos(a2) * 9, hy - Math.sin(a2) * 2 - 6, 6, 9, a2 + 0.6, 0, TAU); ctx.fill();
  if (!far && s.watch > 0.3) {
    // the watch face on the wrist
    const wx = lerp(ex, hx, 0.78), wy = lerp(ey, hy, 0.78);
    ctx.fillStyle = K.DIAL; ctx.beginPath(); ctx.arc(wx, wy - 2, 7.5, 0, TAU); ctx.fill();
    ctx.fillStyle = K.HAND; ctx.fillRect(wx - 0.8, wy - 7, 1.6, 6);
  }
  return [hx, hy];
}

export function drawHer(ctx, s) {
  if (s.alpha <= 0) return;
  K = paints(0.22 * (s.warm || 0));
  ctx.save();
  ctx.translate(s.x, s.y);
  ctx.scale(s.scale * s.dir, s.scale);
  ctx.globalAlpha *= s.alpha;
  // contact shadow
  ctx.fillStyle = 'rgba(0,0,0,0.38)'; ctx.beginPath(); ctx.ellipse(4, 4, 70, 10, 0, 0, TAU); ctx.fill();
  const ph = s.phase, sl = s.slope || 0;
  // walk geometry: half a step in her local px along the path, the planted leg's progress, the hips over it
  const X = 0.25 * STRIDE * (s.stride || 1) / s.scale;
  const qn = ((ph - Math.PI / 2) % TAU + TAU) % TAU, us = (qn <= Math.PI ? qn : qn - Math.PI) / Math.PI;
  const wst = Math.min(X * (1 - 2 * us), LEGL * 0.95), breath = 1 + 0.03 * s.sigh;   // breath: rises on the inhale
  const hipY = ANKLE_Y - Math.sqrt(LEGL * LEGL - wst * wst) + 6 * s.walk * (1 - (1 - 2 * us) ** 2) - 205 * (breath - 1);
  s.sighUp = 2 * s.sigh;   // + = shoulders up, - = slump
  const shiftPx = 18 * s.shift;   // weight shift: the hips move over one foot, the feet stay put
  const lean = 0.07 * s.push + 0.035 * s.walk + 0.03 * s.reach - 0.02 * s.sigh + 0.04 * s.shift;
  const G = { X, c: 1 / stepLen(1, sl), sl, walk: s.walk, shift: shiftPx, hipY, plants: s.plants, wx: s.x, wy: s.y, sc: s.scale };
  const body = () => { ctx.translate(shiftPx, hipY + 205 * breath); ctx.scale(1, breath); };
  // legs (far first)
  leg(ctx, G, ph + Math.PI, true);
  // far arm behind the body
  ctx.save(); body(); ctx.rotate(lean * 0.5);
  arm(ctx, s, true, -0.32 * s.walk * Math.sin(ph) + 0.05);
  ctx.restore();
  leg(ctx, G, ph, false);
  // body
  ctx.save(); body();
  ctx.translate(0, -205); ctx.rotate(lean); ctx.translate(0, 205);
  const sw = 4 * s.walk * Math.sin(ph);
  const up = -12 * s.sigh;
  // bag strap (behind coat front) + bag at the back hip
  const bagSw = 0.12 * s.walk * Math.sin(ph + 0.6);
  ctx.save(); ctx.translate(-36, -250); ctx.rotate(bagSw);
  ctx.fillStyle = K.BAG; rr(ctx, -34, 0, 62, 48, 10); ctx.fill();
  ctx.fillStyle = K.BAG_L; rr(ctx, -34, 0, 62, 22, 8); ctx.fill();
  ctx.fillStyle = K.BRASS; ctx.fillRect(-6, 16, 10, 8);
  ctx.restore();
  // coat
  ctx.fillStyle = K.COAT;
  ctx.beginPath();
  ctx.moveTo(-34, -372 + up); ctx.quadraticCurveTo(2, -392 + up, 36, -370 + up);
  ctx.lineTo(42, -250); ctx.lineTo(66 + sw, -140); ctx.lineTo(-62 + sw, -140); ctx.lineTo(-46, -250); ctx.closePath(); ctx.fill();
  // shading on the back half
  const cg = ctx.createLinearGradient(-60, 0, 40, 0);
  cg.addColorStop(0, rgba(K.SHADE, 0.45)); cg.addColorStop(0.55, rgba(K.SHADE, 0));
  ctx.fillStyle = cg; ctx.fill();
  // front edge, belt, buttons, collar
  ctx.strokeStyle = K.COAT_SH; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(30, -365 + up); ctx.lineTo(36, -250); ctx.lineTo(56 + sw, -142); ctx.stroke();
  ctx.fillStyle = K.COAT_SH; ctx.fillRect(-46, -262, 89, 14);
  ctx.fillStyle = K.BRASS; ctx.fillRect(18, -262, 12, 14);
  ctx.fillStyle = K.COAT_DK; for (const by of [-330, -295]) { ctx.beginPath(); ctx.arc(26, by + up * 0.5, 4, 0, TAU); ctx.fill(); }
  ctx.fillStyle = K.COAT_SH; ctx.beginPath(); ctx.moveTo(-26, -376 + up); ctx.lineTo(26, -376 + up); ctx.lineTo(16, -346 + up); ctx.lineTo(0, -362 + up); ctx.lineTo(-18, -346 + up); ctx.closePath(); ctx.fill();
  // strap across the front
  ctx.strokeStyle = K.STRAP; ctx.lineWidth = 6; ctx.beginPath(); ctx.moveTo(-18, -372 + up); ctx.lineTo(30, -262); ctx.stroke();
  // neck + head
  ctx.save(); ctx.translate(4, -388 + up);
  const tilt = s.tilt - 0.22 * s.watch + 0.2 * Math.min(0, s.sigh) + 0.16 * Math.max(0, s.sigh) + 0.05 * s.smile;
  ctx.rotate(-tilt);
  ctx.fillStyle = K.SKIN_SH; ctx.fillRect(-8, -8, 18, 22);
  head(ctx, s);
  ctx.restore();
  // near arm in front
  arm(ctx, s, false, 0.32 * s.walk * Math.sin(ph) + 0.05);
  ctx.restore();
  ctx.restore();
}

function head(ctx, s) {
  // local origin at the neck top; head centre (6, -42)
  const hx = 6, hy = -44;
  // bun (low, at the back)
  ctx.fillStyle = K.HAIR; ctx.beginPath(); ctx.arc(hx - 36, hy + 20, 17, 0, TAU); ctx.fill();
  // face
  ctx.fillStyle = K.SKIN; ctx.beginPath(); ctx.ellipse(hx, hy, 36, 40, 0, 0, TAU); ctx.fill();
  // nose + chin profile
  ctx.beginPath(); ctx.moveTo(hx + 30, hy - 10); ctx.quadraticCurveTo(hx + 46, hy + 4, hx + 34, hy + 8); ctx.closePath(); ctx.fill();
  ctx.beginPath(); ctx.ellipse(hx + 18, hy + 26, 16, 12, 0.3, 0, TAU); ctx.fill();
  // hair cap: covers the back and top, side-swept fringe
  ctx.fillStyle = K.HAIR;
  ctx.beginPath();
  ctx.moveTo(hx + 30, hy - 22);
  ctx.quadraticCurveTo(hx + 22, hy - 48, hx - 6, hy - 44);
  ctx.quadraticCurveTo(hx - 40, hy - 40, hx - 40, hy + 2);
  ctx.quadraticCurveTo(hx - 40, hy + 26, hx - 26, hy + 30);
  ctx.lineTo(hx - 14, hy + 8);
  ctx.quadraticCurveTo(hx - 4, hy - 18, hx + 30, hy - 22);
  ctx.closePath(); ctx.fill();
  // ear
  ctx.fillStyle = K.SKIN_SH; ctx.beginPath(); ctx.ellipse(hx - 8, hy + 2, 6, 9, 0, 0, TAU); ctx.fill();
  // eye + brow
  const blink = 1;
  ctx.fillStyle = K.EYE; ctx.beginPath(); ctx.ellipse(hx + 21, hy - 6, 3.6, 4.6 * blink, 0, 0, TAU); ctx.fill();
  ctx.strokeStyle = K.HAIR; ctx.lineWidth = 3.2; ctx.lineCap = 'round';
  const browUp = 3 * s.tilt * 8 - 2 * Math.max(0, -s.sigh);
  ctx.beginPath(); ctx.moveTo(hx + 14, hy - 15 - browUp * 0.3); ctx.quadraticCurveTo(hx + 21, hy - 19 - browUp, hx + 28, hy - 15); ctx.stroke();
  // mouth: neutral line, smile arc when happy
  ctx.strokeStyle = K.MOUTH; ctx.lineWidth = 2.6;
  ctx.beginPath();
  const m = s.smile;
  const fr = Math.max(0, s.tilt) * 8;  // puzzled: corners down a touch
  ctx.moveTo(hx + 22, hy + 16 - 3 * m + fr * 0.6); ctx.quadraticCurveTo(hx + 27, hy + 16.5 + 5 * m - fr * 0.4, hx + 32, hy + 15.5 - 4 * m + fr * 0.6); ctx.stroke();
  // cheek
  ctx.fillStyle = rgba(K.CHEEK, 0.18 + 0.15 * m); ctx.beginPath(); ctx.arc(hx + 14, hy + 8, 7, 0, TAU); ctx.fill();
}

// ------------------------------------------------------------------ the whole set
// st: { warmA, swing, judder, flex, spinA, spinAng, spinLen, tick, openB, bellT, route, her, herInsideB, pin, bubble }
export function drawStreet(ctx, cam, ts, st) {
  applyCam(ctx, cam);
  vista(ctx, cam);
  neighbour(ctx, -900, -60, '#171C1D', [0.6, 0], 2);
  shopA(ctx, ts, st);
  neighbour(ctx, 2320, 3150, '#171B1D', [0, 0.7], 6);
  // shop B (she is drawn in the main pass below, after the pavement, even once she is inside: see there)
  st.drawInsideB = null;
  shopB(ctx, ts, st);
  // her inside shop A (replay), clipped to the doorway, behind the swung door
  pavement(ctx, -1200, 790); pavement(ctx, 1470, 3400);
  zebra(ctx);
  road(ctx, -1200, 3400);
  spill(ctx, DOOR_A.x0, DOOR_A.x1, st.spillA || 0);
  spill(ctx, DOOR_B.x0, DOOR_B.x1, 0.35 + 0.65 * st.openB);
  lampPost(ctx, -330); lampPost(ctx, 2620);
  // route line (lime, dotted) behind her across the road: it follows her path (r.y is its offset below her feet
  // on the crossing line), so it curves up to shop B's doorstep with her
  if (st.route && st.route.p > 0) {
    const r = st.route, off = r.y - KERB_Y, xe = lerp(r.x0, r.x1, r.p);
    ctx.save(); ctx.globalAlpha *= r.alpha;
    ctx.strokeStyle = C.lime; ctx.lineWidth = 7; ctx.lineCap = 'round'; ctx.setLineDash([2, 22]);
    ctx.beginPath(); ctx.moveTo(r.x0, pathY(r.x0) + off);
    for (let x = r.x0 + 16; x < xe; x += 16) ctx.lineTo(x, pathY(x) + off);
    ctx.lineTo(xe, pathY(xe) + off); ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = C.lime; ctx.beginPath(); ctx.arc(r.x0, pathY(r.x0) + off, 9, 0, TAU); ctx.fill();
    if (r.ring > 0) {
      ctx.strokeStyle = C.lime; ctx.lineWidth = 4; ctx.globalAlpha *= 1 - r.ring;
      ctx.beginPath(); ctx.ellipse(r.x1, pathY(r.x1) + off, 30 + 70 * r.ring, 10 + 22 * r.ring, 0, 0, TAU); ctx.stroke();
    }
    ctx.restore();
  }
  if (st.her) {
    const h = st.her;
    if (st.enterA) {
      // the outside part of her (left of the door's left jamb)
      ctx.save(); ctx.beginPath(); ctx.rect(-3000, -1000, DOOR_A.x0 + 3000, 4000); ctx.clip();
      drawHer(ctx, h); ctx.restore();
    } else if (h.y < GROUND + 8 && h.x > DOOR_B.x0 - 100 && h.x < DOOR_B.x1 + 100) {
      // her feet are over shop B's threshold: she is behind the shopfront now, so the wall hides everything of her
      // above GROUND except what the doorway shows. Below GROUND (the step, her boots and shadow on it) stays
      // visible. She is drawn here, after the pavement, so the pavement never paints over her feet; the switch
      // happens with her whole figure inside the doorway's width, so no part of her pops.
      ctx.save(); ctx.beginPath();
      ctx.rect(DOOR_B.x0 + 6, DOOR_B.y0, DOOR_B.x1 - DOOR_B.x0 - 12, GROUND - DOOR_B.y0);
      ctx.rect(-3000, GROUND, 9000, 3000);
      ctx.clip(); drawHer(ctx, h); ctx.restore();
    } else drawHer(ctx, h);
  }
  beacon(ctx, 790, ts); beacon(ctx, 1470, ts);
}

export { PAINT_A, PAINT_B, WARM, interior, doorA };
