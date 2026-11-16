// RKN Accountancy, "Signed off.": pure function of time. window.seek(t) paints frame t.
// Timing in beats (u, 120 bpm, 1 beat = 0.5 s). docs/shotlist.md is the plan this file follows.
// One 3-D world (three.js) with four stations along +x; 2-D type, grade and grain on top.
import * as M from './lib/motion.js';
import * as G from './lib/gl.js';

const THREE = G.THREE;
const { W, H, FORMAT, E, prog, lerp, clamp, springU, SPRING, wobble, font, layout, text, hash01, bump, mulberry32 } = M;
const P = FORMAT.portrait;

// Brand tokens (RKN brand guidelines v1.0). Gold is the one accent.
const C = {
  charcoal: '#212121', jet: '#111111', white: '#FFFFFF', grey: '#868686', silver: '#DCDCDE',
  gold: '#CD9734', bronze: '#A67226', bright: '#E4BC54', champagne: '#FFF4A8', ink: '#80561A',
};
const DISPLAY = 'Display', ITALIC = 'DisplayI', UI = 'UI';

// [beat, label, sfx, opts]
const HITS = [
  [0, 'storm + Receipts.', 'impact'],
  [2, 'Deadlines.', 'whoosh', { len: 0.35 }],
  [4, 'HMRC letters.', 'whoosh', { len: 0.35, pan: 0.3 }],
  [6, 'It all adds up.', 'thud'],
  [8, 'page 28 tears', 'swish'],
  [9, 'page 29 tears', 'swish'],
  [10, 'page 30 tears', 'swish'],
  [10, '31 January', 'tick'],
  [12, 'push to 31', 'riser', { len: 2 }],
  [15.3, 'tick slices in', 'whoosh', { len: 0.35, from: 400, to: 3200 }],
  [16, 'TIME STOPS', 'impact'],
  [17, 'paper flies to stack', 'whoosh', { len: 1.5, from: 2400, to: 500 }],
  [18, 'Leave it with us.', 'pop', { pitch: 'D5' }],
  [22, 'tick lands on stack', 'thud'],
  [23, 'Taxation', 'tick'],
  [24, 'Accounting & Bookkeeping', 'tick'],
  [25, 'Business Advisory', 'tick'],
  [26, 'Compliance & Filing', 'tick'],
  [27.6, 'whip to counter', 'whoosh', { len: 0.4 }],
  [28.5, 'drums roll', 'riser', { len: 1.6 }],
  [32, '16 lands', 'thud'],
  [35.6, 'whip to stars', 'whoosh', { len: 0.4 }],
  [36, 'star 1', 'pop', { pitch: 'D5' }],
  [36.5, 'star 2', 'pop', { pitch: 'F5' }],
  [37, 'star 3', 'pop', { pitch: 'A5' }],
  [37.5, 'star 4', 'pop', { pitch: 'C6' }],
  [38, 'star 5', 'pop', { pitch: 'D6' }],
  [43.6, 'whip to ring', 'whoosh', { len: 0.4 }],
  [44, 'Accurate.', 'thud'],
  [45.5, 'Personal.', 'thud'],
  [47, 'Proactive.', 'thud'],
  [48.5, 'work for you.', 'pop', { pitch: 'A5' }],
  [52.4, 'tick flies to ring', 'whoosh', { len: 0.4 }],
  [53.5, 'logo', 'bell', { pitch: 'D6' }],
  [55, 'Your numbers. Our care.', 'tick'],
];

// ============================================================ helpers
const tmpV = new THREE.Vector3();
function toScreen(cam, x, y, z) {
  tmpV.set(x, y, z).project(cam);
  return [(tmpV.x + 1) / 2 * W, (1 - tmpV.y) / 2 * H, tmpV.z];
}
const seg = (u, a, b, ease = E.inOutCubic) => ease(prog(u, a, b));
const lerp3 = (a, b, p) => [lerp(a[0], b[0], p), lerp(a[1], b[1], p), lerp(a[2], b[2], p)];

// ============================================================ textures (props in the world)
function tex(w, h, fn) {
  const cv = document.createElement('canvas'); cv.width = w; cv.height = h;
  const c = cv.getContext('2d'); fn(c, w, h);
  const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
  return t;
}
const bars = (c, x, y, w, h, col = '#cfcfcf') => { c.fillStyle = col; c.fillRect(x, y, w, h); };
function paperTone(c, w, h, base) {
  c.fillStyle = base; c.fillRect(0, 0, w, h);
  const r = mulberry32(w * 7 + h);
  for (let i = 0; i < 900; i++) { c.fillStyle = `rgba(0,0,0,${0.012 * r()})`; c.fillRect(r() * w, r() * h, 2, 2); }
  const g = c.createLinearGradient(0, 0, w, h); g.addColorStop(0, 'rgba(255,255,255,0.05)'); g.addColorStop(1, 'rgba(0,0,0,0.05)');
  c.fillStyle = g; c.fillRect(0, 0, w, h);
}
const DOCS = [
  { name: 'invoice', w: 0.42, h: 0.594, px: [512, 724], draw(c, w, h) {
    paperTone(c, w, h, '#fbfaf6');
    text(c, 'INVOICE', 40, 78, font(38, 600, UI), '#222');
    text(c, 'No. 0427', w - 40, 78, font(20, 500, UI), '#777', 'right');
    bars(c, 40, 110, 160, 10); bars(c, 40, 130, 120, 10); bars(c, w - 200, 110, 160, 10, '#ddd');
    c.fillStyle = '#e9e6dc'; c.fillRect(40, 190, w - 80, 34);
    for (let i = 0; i < 7; i++) { bars(c, 52, 250 + i * 40, 190, 9, '#d6d6d6'); text(c, `£${(120 + i * 37).toFixed(2)}`, w - 52, 262 + i * 40, font(18, 500, UI), '#555', 'right'); }
    c.fillStyle = '#222'; c.fillRect(40, 560, w - 80, 2);
    text(c, 'Amount due', 40, 610, font(24, 500, UI), '#333');
    text(c, '£1,250.00', w - 40, 612, font(32, 600, UI), '#111', 'right');
  } },
  { name: 'receipt', w: 0.17, h: 0.44, px: [256, 664], draw(c, w, h) {
    paperTone(c, w, h, '#f3f0e7');
    text(c, 'RECEIPT', w / 2, 60, font(26, 600, UI), '#333', 'center');
    for (let i = 0; i < 11; i++) { bars(c, 24, 100 + i * 34, 110, 7, '#cfcbbf'); text(c, (2 + i * 1.35).toFixed(2), w - 24, 109 + i * 34, font(15, 500, UI), '#666', 'right'); }
    text(c, 'TOTAL', 24, 520, font(20, 600, UI), '#222'); text(c, '£48.20', w - 24, 520, font(20, 600, UI), '#222', 'right');
    const r = mulberry32(5); for (let x = 28; x < w - 28; x += 3) if (r() > 0.45) c.fillRect(x, 560, r() > 0.5 ? 2 : 1, 60);
  } },
  { name: 'sa100', w: 0.42, h: 0.594, px: [512, 724], draw(c, w, h) {
    paperTone(c, w, h, '#fbfbf8');
    text(c, 'Tax return', 40, 74, font(36, 600, UI), '#222'); text(c, 'SA100', w - 40, 74, font(26, 600, UI), '#666', 'right');
    text(c, 'Tax year 6 April 2025 to 5 April 2026', 40, 108, font(17, 400, UI), '#666');
    c.strokeStyle = '#999'; c.lineWidth = 2;
    for (let i = 0; i < 9; i++) { bars(c, 40, 160 + i * 56, 150, 9, '#d8d8d8'); for (let k = 0; k < 7; k++) c.strokeRect(232 + k * 34, 146 + i * 56, 30, 34); }
  } },
  { name: 'bank', w: 0.42, h: 0.594, px: [512, 724], draw(c, w, h) {
    paperTone(c, w, h, '#fafafa');
    c.fillStyle = '#2b2b2b'; c.fillRect(0, 0, w, 90); text(c, 'Statement', 40, 58, font(30, 600, UI), '#fff');
    for (let i = 0; i < 14; i++) {
      if (i % 2) { c.fillStyle = '#f0f0ee'; c.fillRect(30, 130 + i * 38, w - 60, 38); }
      bars(c, 44, 144 + i * 38, 70, 8, '#ccc'); bars(c, 130, 144 + i * 38, 150, 8, '#d6d6d6');
      text(c, (hash01(i, 3) * 900 + 20).toFixed(2), w - 44, 154 + i * 38, font(16, 500, UI), '#555', 'right');
    }
  } },
  { name: 'vat', w: 0.42, h: 0.594, px: [512, 724], draw(c, w, h) {
    paperTone(c, w, h, '#fcfbf7');
    text(c, 'VAT return', 40, 76, font(36, 600, UI), '#222');
    text(c, 'Making Tax Digital', 40, 108, font(17, 500, UI), '#777');
    for (let i = 1; i <= 9; i++) {
      text(c, `Box ${i}`, 40, 160 + i * 52, font(19, 600, UI), '#444');
      bars(c, 120, 150 + i * 52, 170, 8, '#d6d6d6');
      c.strokeStyle = '#aaa'; c.lineWidth = 2; c.strokeRect(w - 190, 132 + i * 52, 150, 38);
      text(c, (hash01(i, 9) * 9000).toFixed(2), w - 52, 158 + i * 52, font(17, 500, UI), '#333', 'right');
    }
  } },
  { name: 'envelope', w: 0.40, h: 0.26, px: [512, 333], draw(c, w, h) {
    paperTone(c, w, h, '#c29a6b');
    c.fillStyle = 'rgba(255,255,255,0.75)'; c.fillRect(40, 140, 250, 110);
    bars(c, 58, 166, 180, 10, '#9a9a9a'); bars(c, 58, 190, 150, 10, '#a8a8a8'); bars(c, 58, 214, 120, 10, '#a8a8a8');
    text(c, 'PRIVATE & CONFIDENTIAL', 40, 70, font(16, 600, UI), 'rgba(40,25,10,0.7)');
    c.fillStyle = 'rgba(60,35,10,0.6)'; c.fillRect(w - 110, 30, 70, 50);
  } },
];

// ============================================================ shapes
// The check mark, traced from the tick in the RKN monogram. Origin at the valley; units = ring radii.
function tickShape() {
  const s = new THREE.Shape();
  s.moveTo(-0.31, 0.36);
  s.lineTo(-0.255, 0.405);
  s.quadraticCurveTo(-0.11, 0.24, 0.025, 0.115);
  s.quadraticCurveTo(0.22, 0.62, 0.375, 1.205);
  s.quadraticCurveTo(0.24, 0.52, 0.03, -0.045);
  s.quadraticCurveTo(-0.15, 0.17, -0.31, 0.36);
  return s;
}
function starShape(R = 1, r = 0.45) {
  const s = new THREE.Shape();
  for (let i = 0; i < 10; i++) {
    const a = Math.PI / 2 + (i * Math.PI) / 5, rr = i % 2 ? r : R;
    const x = Math.cos(a) * rr, y = Math.sin(a) * rr;
    i ? s.lineTo(x, y) : s.moveTo(x, y);
  }
  return s;
}

// ============================================================ the world
const ST = { A: 0, B: 16, C: 32, D: 48 };     // station x positions
const FLOOR = -0.92;
const N_PER = 30;                              // papers per doc type
const S = {};

function goldMat(rough = 0.26) {
  return new THREE.MeshPhysicalMaterial({ color: 0xd9a441, metalness: 1, roughness: rough, clearcoat: 0.4, clearcoatRoughness: 0.2, envMapIntensity: 1.25 });
}

function buildWorld() {
  const scene = new THREE.Scene();
  scene.environment = G.ENV;
  const cam = G.camera(FORMAT.pick({ '9x16': 40, '16x9': 30 }), 0.05, 200);

  // light: warm key from top-left (shadows at station A), gold rim from behind, low fill
  const key = new THREE.SpotLight(0xffe9cf, 48, 20, 0.55, 0.6, 1.4);
  key.position.set(-2.4, 4.6, 3.2); key.target.position.set(0, -0.5, 0);
  key.castShadow = true; key.shadow.mapSize.set(1024, 1024); key.shadow.bias = -0.0004; key.shadow.radius = 4;
  scene.add(key, key.target);
  const rim = new THREE.DirectionalLight(0xffc77a, 2.2); rim.position.set(3, 2.5, -4); scene.add(rim);
  scene.add(new THREE.HemisphereLight(0xfff2e0, 0x141210, 0.45));
  const front = new THREE.DirectionalLight(0xfff3e4, 0.45); front.position.set(0.5, 1, 6); scene.add(front);

  // floor: catches shadows only (2-D void shows through)
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(14, 14), new THREE.ShadowMaterial({ opacity: 0.55 }));
  floor.rotation.x = -Math.PI / 2; floor.position.y = FLOOR; floor.receiveShadow = true; scene.add(floor);

  // --- papers (instanced, one mesh per document type)
  const papers = DOCS.map((d, k) => {
    const g = new THREE.PlaneGeometry(d.w, d.h, 10, 6);
    const pos = g.attributes.position, curl = k === 1 ? 0.05 : 0.025;
    for (let i = 0; i < pos.count; i++) {
      const x = pos.getX(i) / d.w, y = pos.getY(i) / d.h;
      pos.setZ(i, curl * (x * x * 4 - 1) * 0.5 + 0.012 * Math.sin(y * 5 + k));
    }
    g.computeVertexNormals();
    const map = tex(d.px[0], d.px[1], d.draw);
    const m = new THREE.MeshStandardMaterial({ map, roughness: 0.82, metalness: 0, side: THREE.DoubleSide, envMapIntensity: 0.35 });
    m.onBeforeCompile = (sh) => {
      sh.fragmentShader = sh.fragmentShader.replace('#include <map_fragment>',
        `#ifdef USE_MAP
          vec4 sampledDiffuseColor = texture2D( map, vMapUv );
          if (!gl_FrontFacing) sampledDiffuseColor = vec4(sampledDiffuseColor.rgb * 0.15 + vec3(0.80), 1.0);
          diffuseColor *= sampledDiffuseColor;
        #endif`);
    };
    const im = new THREE.InstancedMesh(g, m, N_PER);
    im.castShadow = true; im.receiveShadow = true; im.frustumCulled = false;
    scene.add(im);
    return im;
  });
  // per-paper parameters (seeded)
  const N = N_PER * DOCS.length;
  const PP = [];
  const order = [...Array(N).keys()].sort((a, b) => hash01(a, 77) - hash01(b, 77));
  for (let i = 0; i < N; i++) {
    const h = (s) => hash01(i, s);
    PP.push({
      type: Math.floor(i / N_PER), idx: i % N_PER,
      r: 0.62 + 2.1 * h(1) ** 1.3, th: h(2) * Math.PI * 2, om: (0.22 + 0.3 * h(3)) * (h(4) > 0.15 ? 1 : -1),
      z0: h(5) * 34, vz: 0.85 + 0.75 * h(6),
      rx: h(7) * 6, ry: h(8) * 6, rz: h(9) * 6, wx: 0.5 + 1.1 * h(10), wy: 0.3 + 0.9 * h(11), wz: 0.2 + 0.6 * h(12),
      slot: order.indexOf(i),
      jx: (h(13) - 0.5) * 0.03, jz: (h(14) - 0.5) * 0.03, jyaw: (h(15) - 0.5) * 0.16,
    });
  }

  // --- tear-off desk calendar (station A)
  const cal = new THREE.Group(); scene.add(cal);
  const leather = new THREE.MeshStandardMaterial({ color: 0x1b1b1b, roughness: 0.55, metalness: 0.1 });
  const block = new THREE.Mesh(new THREE.BoxGeometry(0.64, 0.66, 0.16), new THREE.MeshStandardMaterial({ color: 0xf1efe8, roughness: 0.9 }));
  block.position.set(0, 0, -0.08); block.castShadow = true; cal.add(block);
  const back = new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.78, 0.04), leather); back.position.set(0, 0.02, -0.18); back.castShadow = true; cal.add(back);
  const stand = new THREE.Mesh(new THREE.BoxGeometry(0.74, 0.06, 0.42), leather); stand.position.set(0, -0.37, -0.08); stand.castShadow = true; cal.add(stand);
  const bar = new THREE.Mesh(new THREE.BoxGeometry(0.68, 0.07, 0.19), goldMat(0.3)); bar.position.set(0, 0.36, -0.07); cal.add(bar);
  const pages = [28, 29, 30, 31].map((d, k) => {
    const map = tex(512, 528, (c, w, h) => {
      paperTone(c, w, h, '#fbfaf6');
      c.fillStyle = C.charcoal; c.fillRect(0, 0, w, 120);
      text(c, 'JANUARY', w / 2, 82, font(46, 600, UI), C.bright, 'center', 10);
      text(c, String(d), w / 2, 420, font(300, 500, DISPLAY), C.charcoal, 'center');
      text(c, d === 31 ? 'SELF ASSESSMENT DEADLINE' : ['WEDNESDAY', 'THURSDAY', 'FRIDAY'][k], w / 2, 492, font(22, 600, UI), d === 31 ? C.ink : '#888', 'center', 4);
    });
    const piv = new THREE.Group(); piv.position.set(0, 0.33, 0.003 + (3 - k) * 0.002);
    const pg = new THREE.Mesh(new THREE.PlaneGeometry(0.62, 0.64, 6, 6), new THREE.MeshStandardMaterial({ map, roughness: 0.85, side: THREE.DoubleSide }));
    pg.position.y = -0.32; pg.castShadow = true; piv.add(pg); cal.add(piv);
    return piv;
  });

  // --- the hero tick (stations A and D)
  const tickGeo = new THREE.ExtrudeGeometry(tickShape(), { depth: 0.07, bevelEnabled: true, bevelThickness: 0.018, bevelSize: 0.012, bevelSegments: 3, curveSegments: 24 });
  tickGeo.translate(0, 0, -0.035);
  const tickA = new THREE.Mesh(tickGeo, goldMat(0.22)); tickA.castShadow = true; scene.add(tickA);
  const tickD = new THREE.Mesh(tickGeo, goldMat(0.22)); scene.add(tickD);

  // --- counter drums (station B)
  const drumMap = (shift) => tex(2048, 512, (c, w, h) => {
    const g = c.createLinearGradient(0, 0, w, 0); g.addColorStop(0, '#1d1d1d'); g.addColorStop(1, '#232323');
    c.fillStyle = g; c.fillRect(0, 0, w, h);
    for (let d = 0; d < 10; d++) {
      const cx = ((d + 0.5) / 10) * w;
      c.save(); c.translate(cx, h / 2); c.rotate(Math.PI / 2);
      c.font = font(176, 500, DISPLAY); c.textAlign = 'center'; c.textBaseline = 'middle';
      const gg = c.createLinearGradient(0, -80, 0, 80); gg.addColorStop(0, C.champagne); gg.addColorStop(0.5, C.bright); gg.addColorStop(1, C.gold);
      c.fillStyle = gg; c.fillText(String((d + shift) % 10), 0, 8);
      c.restore();
      c.fillStyle = 'rgba(205,151,52,0.35)'; c.fillRect(Math.round((d / 10) * w), 0, 3, h);
    }
  });
  const drums = [0, 1].map((k) => {
    const grp = new THREE.Group();
    const cyl = new THREE.Mesh(new THREE.CylinderGeometry(0.42, 0.42, 0.5, 96, 1, false),
      [new THREE.MeshStandardMaterial({ map: drumMap(0), roughness: 0.45, metalness: 0.35 }), new THREE.MeshStandardMaterial({ color: 0x1a1a1a, roughness: 0.5 }), new THREE.MeshStandardMaterial({ color: 0x1a1a1a, roughness: 0.5 })]);
    cyl.rotation.order = 'ZYX'; cyl.rotation.z = Math.PI / 2; grp.add(cyl);
    for (const sx of [-1, 1]) {
      const cap = new THREE.Mesh(new THREE.CylinderGeometry(0.47, 0.47, 0.035, 96), goldMat(0.28));
      cap.rotation.z = Math.PI / 2; cap.position.x = sx * 0.268; grp.add(cap);
    }
    grp.position.set(ST.B + (k ? 0.29 : -0.29), 0.32, 0);
    scene.add(grp);
    return { grp, cyl };
  });
  const axle = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 1.4, 32), goldMat(0.3));
  axle.rotation.z = Math.PI / 2; axle.position.set(ST.B, 0.32, 0); scene.add(axle);
  // housing: a charcoal face plate with a window onto the front digits, gold-edged
  const plate = new THREE.Shape(); plate.moveTo(-0.72, -0.5); plate.lineTo(0.72, -0.5); plate.lineTo(0.72, 0.5); plate.lineTo(-0.72, 0.5); plate.lineTo(-0.72, -0.5);
  const hole = new THREE.Path(); hole.moveTo(-0.56, -0.17); hole.lineTo(-0.56, 0.17); hole.lineTo(0.56, 0.17); hole.lineTo(0.56, -0.17); hole.lineTo(-0.56, -0.17);
  plate.holes.push(hole);
  const housing = new THREE.Mesh(new THREE.ExtrudeGeometry(plate, { depth: 0.06, bevelEnabled: true, bevelThickness: 0.012, bevelSize: 0.012, bevelSegments: 2 }),
    new THREE.MeshStandardMaterial({ color: 0x232323, roughness: 0.38, metalness: 0.6 }));
  housing.position.set(ST.B, 0.32, 0.44); scene.add(housing);
  const trimG = new THREE.EdgesGeometry(new THREE.BoxGeometry(1.12, 0.34, 0.001));
  const sep = new THREE.Mesh(new THREE.BoxGeometry(0.02, 0.34, 0.02), goldMat(0.3)); sep.position.set(ST.B, 0.32, 0.47); scene.add(sep);
  const frameBars = [[0, 0.18, 1.14, 0.018], [0, -0.18, 1.14, 0.018], [-0.57, 0, 0.018, 0.38], [0.57, 0, 0.018, 0.38]].map(([x, y, w, h]) => {
    const b = new THREE.Mesh(new THREE.BoxGeometry(w, h, 0.03), goldMat(0.26)); b.position.set(ST.B + x, 0.32 + y, 0.515); scene.add(b); return b; });
  const housingParts = [housing, sep, axle, ...frameBars];

  // --- stars (station C)
  const starGeo = new THREE.ExtrudeGeometry(starShape(0.15, 0.066), { depth: 0.045, bevelEnabled: true, bevelThickness: 0.02, bevelSize: 0.014, bevelSegments: 3 });
  starGeo.translate(0, 0, -0.022);
  const stars = [0, 1, 2, 3, 4].map(() => { const m = new THREE.Mesh(starGeo, goldMat(0.24)); scene.add(m); return m; });

  // --- the open circle (station D): a ring broken at the upper right, like the monogram
  const GAP0 = THREE.MathUtils.degToRad(28), GAP1 = THREE.MathUtils.degToRad(68);
  const ringGeo = new THREE.TorusGeometry(1, 0.022, 20, 260, Math.PI * 2 - (GAP1 - GAP0));
  ringGeo.rotateZ(GAP1);
  const ring = new THREE.Mesh(ringGeo, goldMat(0.24)); scene.add(ring);

  return { scene, camera: cam, key, papers, PP, N, cal, pages, tickA, tickD, drums, housingParts, stars, ring, update: updateWorld };
}

// ------------------------------------------------------------ camera path
// Storm time: normal flow, a speed ramp into beat 16, then time stops.
function tau(u) {
  if (u <= 14) return u;
  if (u <= 16) return 14 + (u - 14) + 0.6 * (u - 14) ** 2;
  return 18.4 + 0.12 * (1 - Math.exp(-(u - 16) * 5)) + 0.01 * (u - 16);
}
const CAMK = FORMAT.portrait ? 1 : 0.85; // landscape sits a touch closer (wider lens covers more)
const TY = FORMAT.portrait ? -1.15 : -0.5;
function camAt(u) {
  // station A: one continuous move
  const A = (uu) => {
    if (uu < 8) { const p = E.outQuad(prog(uu, -2, 8)); return [[lerp(0.6, 0.12, p), lerp(0.55, 0.42, p), Math.exp(lerp(Math.log(15), Math.log(7.4), p))], [0, 0.3, 0]]; }
    if (uu < 15.3) { const p = E.inOutSine(prog(uu, 8, 15.3)); return [[lerp(0.12, 0.04, p), lerp(0.42, 0.34, p), Math.exp(lerp(Math.log(7.4), Math.log(2.75), p))], [0, lerp(0.3, 0.24, p), 0]]; }
    if (uu < 17) { const k = springU(uu, 15.6, SPRING.gentle); return [[0.04 + 0.12 * k, 0.34 + 0.06 * k, 2.75 + 0.55 * k], [0, 0.24, 0]]; }
    if (uu < 21.5) { const p = E.inOutCubic(prog(uu, 17, 21.5)); return [[lerp(0.16, 1.55, p), lerp(0.4, 1.05, p), lerp(3.3, 4.4, p)], [0, lerp(0.24, TY, p), 0]]; }
    const a = lerp(Math.atan2(1.55, 4.4), -0.38, E.inOutSine(prog(uu, 21.5, 28))), r = Math.hypot(1.55, 4.4) - 0.25 * prog(uu, 21.5, 28);
    return [[r * Math.sin(a), lerp(1.05, 0.85, prog(uu, 21.5, 28)), r * Math.cos(a)], [0, TY, 0]];
  };
  const B = (uu) => { const p = prog(uu, 28, 36); return [[ST.B + 0.15 - 0.3 * p, 0.62 - 0.05 * p, lerp(5.6, 4.7, E.outQuad(p))], [ST.B, P ? 0.0 : 0.25, 0]]; };
  const Cc = (uu) => { const p = prog(uu, 36, 44); return [[ST.C - 0.2 + 0.4 * p, 0.62, lerp(5.6, 4.9, E.outQuad(p))], [ST.C, P ? 0.25 : 0.3, 0]]; };
  const D = (uu) => {
    const p = E.inOutCubic(prog(uu, 50.5, 54));
    const dEnd = P ? 14 : 11.9, yEnd = P ? -1.43 : -0.9;
    return [[ST.D + lerp(0.6, 0, p), lerp(0.1, yEnd, p), Math.exp(lerp(Math.log(6.6 - 0.4 * prog(uu, 44, 50)), Math.log(dEnd), p))], [ST.D, lerp(0, yEnd, p), 0]];
  };
  const whip = (uu, a, b, f0, f1) => {
    const p = E.inOutQuint(prog(uu, a, b));
    const [p0, t0] = f0(a), [p1, t1] = f1(b);
    return [lerp3(p0, p1, p), lerp3(t0, t1, p)];
  };
  let r;
  if (u < 27.6) r = A(u);
  else if (u < 28.3) r = whip(u, 27.6, 28.3, A, B);
  else if (u < 35.6) r = B(u);
  else if (u < 36.3) r = whip(u, 35.6, 36.3, B, Cc);
  else if (u < 43.6) r = Cc(u);
  else if (u < 44.3) r = whip(u, 43.6, 44.3, Cc, D);
  else r = D(u);
  if (!FORMAT.portrait) { // landscape: subject right of centre, a bit closer
    if (u < 50) { r[0] = [r[0][0], r[0][1], r[0][2] * CAMK]; r[1] = [r[1][0] - 0.45 * (u > 17 ? 1 : 0.4) * (1 - prog(u, 44, 46)), r[1][1], r[1][2]]; }
  }
  return r;
}
if (!E.inOutQuint) E.inOutQuint = (t) => (t < 0.5 ? 16 * t ** 5 : 1 - (-2 * t + 2) ** 5 / 2);

// ------------------------------------------------------------ update (pure function of u)
const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), q2 = new THREE.Quaternion(), eul = new THREE.Euler(), sc = new THREE.Vector3(), v3 = new THREE.Vector3();
const STACK_Q = new THREE.Quaternion().setFromEuler(new THREE.Euler(-Math.PI / 2, 0, 0));
function paperPose(p, uu) {
  const T = tau(uu);
  const th = p.th + p.om * T;
  const z = -20 + ((p.z0 + p.vz * T) % 34);
  const r = p.r + 0.12 * Math.sin(T * 0.7 + p.th);
  const pos = [Math.cos(th) * r * (P ? 0.75 : 1.25), 0.3 + Math.sin(th) * r, z];
  eul.set(p.rx + p.wx * T * 0.6, p.ry + p.wy * T * 0.6, p.rz + p.wz * T * 0.6);
  return [pos, eul];
}
function updateWorld(t, u) {
  const W3 = this;
  const [cp, ct] = camAt(u);
  G.lookFrom(W3.camera, cp, ct, u < 16 ? 0.03 * Math.sin(u * 0.4) : 0);

  // papers: storm, freeze, then fly into one neat stack
  const counts = new Array(DOCS.length).fill(0);
  const visibleA = u < 30;
  for (let i = 0; i < W3.N; i++) {
    const p = W3.PP[i], d = DOCS[p.type];
    let pos, quat;
    if (!visibleA) { m4.makeScale(0, 0, 0); W3.papers[p.type].setMatrixAt(p.idx, m4); continue; }
    const [fp, fe] = paperPose(p, Math.min(u, 30));
    q.setFromEuler(fe);
    const s0 = 17 + 4.2 * (p.slot / W3.N), k = prog(u, s0, s0 + 1.25);
    if (k > 0) {
      const e = E.outCubic(k);
      const top = FLOOR + 0.0032 * (p.slot + 0.5);
      const sp = [p.jx, top, p.jz];
      pos = lerp3(fp, sp, e); pos[1] += Math.sin(Math.PI * e) * 0.35;
      q2.copy(STACK_Q).multiply(new THREE.Quaternion().setFromAxisAngle(v3.set(0, 0, 1), p.jyaw));
      quat = q.clone().slerp(q2, E.outQuad(k));
      // stack settles when the tick lands
      if (u > 22) pos[1] -= 0.004 * wobble(u - 22, 3, 6) * (p.slot / W3.N);
    } else { pos = fp; quat = q; }
    sc.set(1, 1, 1);
    m4.compose(v3.set(...pos), quat, sc);
    W3.papers[p.type].setMatrixAt(p.idx, m4);
    counts[p.type]++;
  }
  W3.papers.forEach((m) => { m.instanceMatrix.needsUpdate = true; });

  // calendar: pages 28-30 tear off on beats 8, 9, 10; it falls away after the freeze
  W3.cal.visible = u < 19.5;
  const fall = E.inCubic(prog(u, 16.8, 19));
  W3.cal.position.set(0, 0.26 - fall * 2.4, -fall * 1.4);
  W3.cal.rotation.set(-fall * 1.2 + 0.04 * Math.sin(u * 0.5), 0.12 * Math.sin(u * 0.23) * (1 - prog(u, 12, 15)) - fall * 0.5, 0);
  W3.pages.forEach((pv, k) => {
    if (k === 3) { pv.rotation.set(0, 0, 0); pv.position.set(0, 0.33, 0.003); return; }
    const t0 = 8 + k, e = prog(u, t0 - 0.08, t0 + 1.6);
    pv.visible = e < 1;
    const ee = E.outCubic(e), lift = E.inQuad(prog(u, t0 + 0.15, t0 + 1.6));
    pv.rotation.set(-ee * 2.6, (hash01(k, 4) - 0.5) * lift * 2, (hash01(k, 5) - 0.5) * lift * 3);
    pv.position.set((hash01(k, 6) - 0.5) * 1.6 * lift, 0.33 + lift * 0.9, 0.003 + (3 - k) * 0.002 + lift * 2.6);
  });

  // hero tick A: slices in on 15.3-16, lands on "31", hovers, then stands on top of the stack (beat 22)
  const tA = W3.tickA;
  tA.visible = u > 15.0 && u < 29;
  if (tA.visible) {
    const S0 = 0.42;
    const pIn = E.outExpo(prog(u, 15.3, 16));
    let pos = lerp3([-1.6, -1.5, 2.2], [-0.05, 0.08, 0.16], pIn);
    let rot = [lerp(1.2, 0, pIn), lerp(-1.4, 0, pIn), lerp(-0.9, -0.08, pIn)];
    let s = S0;
    // after the freeze: drift up and over the stack
    const pUp = E.inOutCubic(prog(u, 17.2, 21));
    if (pUp > 0) {
      pos = lerp3(pos, [0.0, 0.25, 0.0], pUp); rot = [rot[0], lerp(0, Math.PI * 2, pUp), rot[2]];
      s = lerp(S0, 0.5, pUp);
    }
    // stamp onto the stack top at beat 22
    const pDn = E.inQuad(prog(u, 21.3, 22));
    const stackTop = FLOOR + 0.0032 * W3.N;
    if (pDn > 0) pos = [pos[0], lerp(pos[1], stackTop + 0.03, pDn), pos[2]];
    const sq = u > 22 ? 0.08 * wobble(u - 22, 2.4, 5) : 0;
    tA.position.set(pos[0], pos[1] + (u < 17.2 ? 0.01 * Math.sin(u * 3) * prog(u, 16, 17) : 0), pos[2]);
    tA.rotation.set(rot[0], rot[1] + (u > 22 ? 0.2 * Math.sin((u - 22) * 0.6) : 0), rot[2]);
    tA.scale.set(s * (1 + sq), s * (1 - sq), s);
  }

  // counter: 00 -> 16 between beats 28.5 and 32, with a mechanical settle
  const roll = (u0, u1, turns) => {
    const p = E.inOutCubic(prog(u, u0, u1));
    return turns * p + (u > u1 ? 0.02 * wobble((u - u1), 3, 5) : 0);
  };
  const DIG = (d) => -((d) / 10) * Math.PI * 2;  // rotation that brings digit d to the front (calibrated below)
  W3.drums[0].cyl.rotation.y = DRUM0 + DIG(roll(28.6, 31.4, 1));
  W3.drums[1].cyl.rotation.y = DRUM0 + DIG(roll(28.5, 32, 16));
  W3.drums.forEach((d) => { d.grp.visible = u > 26 && u < 38; });
  W3.housingParts.forEach((m) => { m.visible = u > 26 && u < 38; });

  // stars drop in one by one on beats 36..38
  W3.stars.forEach((m, i) => {
    const u0 = 35.7 + i * 0.5, k = springU(u, u0, SPRING.bouncy);
    m.visible = u > 34 && u < 46 && k > 0;
    const x = ST.C + (i - 2) * 0.34;
    m.position.set(x, 0.45 + (1 - k) * 1.6, 0);
    m.rotation.set(0, (1 - k) * 4 + 0.15 * Math.sin(u * 0.7 + i), 0);
    m.scale.setScalar(Math.max(0.001, k));
  });

  // the open circle: turns slowly behind the promise, then faces camera for the logo
  const R = W3.ring, fr = E.inOutCubic(prog(u, 50.5, 53.5));
  R.visible = u > 42;
  R.position.set(ST.D, 0, 0);
  const spinY = lerp(1.05 + 0.18 * (u - 44), 0, fr), spinX = lerp(0.35 - 0.02 * (u - 44), 0, fr);
  R.rotation.set(spinX, spinY, 0);
  R.scale.setScalar(1);
  // the tick flies into the gap
  const tD = W3.tickD, pk = E.outExpo(prog(u, 52.4, 53.5));
  tD.visible = u > 52.3;
  tD.position.copy(lerp3([ST.D + 2.6, 2.8, 1.5], [ST.D + 0.61, -0.46, 0], pk).reduce((v, x, i) => (v.setComponent(i, x), v), new THREE.Vector3()));
  tD.rotation.set(lerp(-1.3, 0, pk), lerp(2.4, 0, pk), lerp(0.8, 0, pk));
  tD.scale.setScalar(1);
}
let DRUM0 = -Math.PI / 10;

// ============================================================ 2-D: background, type, post
function background(ctx, u, cam) {
  const g = ctx.createRadialGradient(W * 0.5, H * 0.42, 0, W * 0.5, H * 0.45, Math.max(W, H) * 0.75);
  g.addColorStop(0, '#2b2724'); g.addColorStop(0.45, '#1c1b1a'); g.addColorStop(1, '#0d0d0d');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  // a warm pool of light behind the subject, parallax with the camera
  const px = W * 0.5 - (cam.position.x % 16 - 0) * 18, py = H * (P ? 0.42 : 0.45);
  const g2 = ctx.createRadialGradient(px, py, 0, px, py, Math.min(W, H) * 0.7);
  g2.addColorStop(0, 'rgba(205,151,52,0.13)'); g2.addColorStop(1, 'rgba(205,151,52,0)');
  ctx.fillStyle = g2; ctx.fillRect(0, 0, W, H);
}

// gold gradient fill for a line of type at baseline y, size s
function goldFill(ctx, y, s) {
  const g = ctx.createLinearGradient(0, y - s * 0.8, 0, y + s * 0.15);
  g.addColorStop(0, C.champagne); g.addColorStop(0.45, C.bright); g.addColorStop(1, C.gold);
  return g;
}
// A rich line: parts = [[str, 'r'|'i'], ...]. Glyphs rise from under a mask on a spring; exit wipes up.
function richLine(ctx, parts, x, y, size, u, u0, u1, opts = {}) {
  if (u < u0 - 0.1 || u > u1 + 0.6) return;
  const stag = opts.stagger ?? 0.025;
  const exit = E.inCubic(prog(u, u1, u1 + 0.45));
  let cx = x, n = 0;
  const items = [];
  for (const [str, st] of parts) {
    const f = st === 'i' ? font(size * 1.04, 500, ITALIC) : font(size, 500, DISPLAY);
    const L = layout(ctx, str, f, -0.01 * size);
    items.push({ str, st, f, L, x0: cx });
    cx += L.width + (st === 'r' && !str.endsWith(' ') ? 0 : 0);
  }
  const total = cx - x;
  const dx = opts.align === 'center' ? -total / 2 : opts.align === 'right' ? -total : 0;
  ctx.save();
  ctx.beginPath(); ctx.rect(0, y - size * 1.15 - exit * size * 1.3, W, size * 1.5); ctx.clip();
  for (const it of items) {
    for (const gph of it.L.glyphs) {
      const k = springU(u, u0 + n * stag, SPRING.snappy); n++;
      if (k <= 0 || gph.ch === ' ') continue;
      const yy = y + (1 - k) * size * 1.1 - exit * size * 1.3;
      ctx.font = it.f; ctx.textAlign = 'center';
      ctx.fillStyle = it.st === 'i' ? goldFill(ctx, yy, size) : (opts.color || C.white);
      ctx.fillText(gph.ch, it.x0 + dx + gph.cx, yy);
    }
  }
  ctx.restore();
}
function eyebrow(ctx, str, x, y, u, u0, u1, align = 'left', size = 26) {
  const k = E.outQuint(prog(u, u0, u0 + 0.8)) * (1 - prog(u, u1, u1 + 0.4));
  if (k <= 0) return;
  ctx.save(); ctx.globalAlpha = k;
  const f = font(size, 600, UI);
  ctx.font = f; ctx.letterSpacing = `${size * 0.22}px`;
  const w = ctx.measureText(str).width;
  const x0 = align === 'center' ? x - w / 2 : x;
  // reveal left to right
  ctx.beginPath(); ctx.rect(x0 - 4, y - size * 1.2, (w + 8) * k, size * 1.6); ctx.clip();
  ctx.fillStyle = C.bright; ctx.textAlign = 'left'; ctx.fillText(str, x0, y);
  ctx.letterSpacing = '0px'; ctx.restore();
}
// short gold gradient rule (graphic language: fine gold rules)
function goldRule(ctx, x, y, w, k, align = 'left') {
  if (k <= 0) return;
  const ww = w * k, x0 = align === 'center' ? x - ww / 2 : x;
  const g = ctx.createLinearGradient(x0, 0, x0 + ww, 0);
  g.addColorStop(0, C.bronze); g.addColorStop(0.6, C.bright); g.addColorStop(1, C.champagne);
  ctx.fillStyle = g; ctx.fillRect(x0, y, ww, 4);
}
// a 2-D check mark bullet (draws on with k)
function tickGlyph(ctx, x, y, s, k, color = C.bright) {
  if (k <= 0) return;
  ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = s * 0.16; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  const pts = [[x, y], [x + s * 0.36, y + s * 0.36], [x + s * 1.0, y - s * 0.5]];
  const L1 = Math.hypot(s * 0.36, s * 0.36), L2 = Math.hypot(s * 0.64, s * 0.86), Lt = (L1 + L2) * k;
  ctx.beginPath(); ctx.moveTo(...pts[0]);
  if (Lt <= L1) ctx.lineTo(x + s * 0.36 * Lt / L1, y + s * 0.36 * Lt / L1);
  else { ctx.lineTo(...pts[1]); const r = (Lt - L1) / L2; ctx.lineTo(pts[1][0] + s * 0.64 * r, pts[1][1] - s * 0.86 * r); }
  ctx.stroke(); ctx.restore();
}
// charcoal gradient behind lower-third type (brand: charcoal 60-75% overlay behind gold/white type)
function scrim(ctx, k, top = true) {
  if (k <= 0) return;
  ctx.save(); ctx.globalAlpha = k;
  const y0 = P ? H * 0.42 : 0;
  if (P) {
    const g = ctx.createLinearGradient(0, y0, 0, H); g.addColorStop(0, 'rgba(17,17,17,0)'); g.addColorStop(0.4, 'rgba(17,17,17,0.78)'); g.addColorStop(1, 'rgba(17,17,17,0.9)');
    ctx.fillStyle = g; ctx.fillRect(0, y0, W, H - y0);
    if (top) { const g2 = ctx.createLinearGradient(0, 0, 0, H * 0.32); g2.addColorStop(0, 'rgba(17,17,17,0.7)'); g2.addColorStop(1, 'rgba(17,17,17,0)'); ctx.fillStyle = g2; ctx.fillRect(0, 0, W, H * 0.32); }
  } else {
    const g = ctx.createLinearGradient(0, 0, W * 0.55, 0); g.addColorStop(0, 'rgba(17,17,17,0.8)'); g.addColorStop(1, 'rgba(17,17,17,0)');
    ctx.fillStyle = g; ctx.fillRect(0, 0, W * 0.55, H);
  }
  ctx.restore();
}

const SECTORS = ['Automotive', 'Construction', 'Hospitality', 'Healthcare & Social Care', 'Technology & IT', 'Retail & E-Commerce',
  'Housing & Real Estate', 'Manufacturing', 'Creative Industries', 'Legal & Law Firms', 'Education', 'Transport & Logistics',
  'Media & Communications', 'Non-Profit & Charities', 'Pharma & Life Sciences', 'Sports & Leisure'];

function overlay(ctx, u, IMG, W3) {
  const s = FORMAT.safe;
  const X = s.x + (P ? 6 : 40);
  const big = FORMAT.pick({ '9x16': 112, '16x9': 104 });
  const baseY = P ? s.y + s.h - 30 : H * 0.62;

  // ---- S1 hook: three nouns stack, then "It all adds up."
  scrim(ctx, prog(u, -1, 0.2) * (1 - prog(u, 15.6, 16.4)) + (u > 16 && u < 27.8 ? 1 - prog(u, 27.4, 27.9) : 0), false);
  if (u < 8.2) {
    const lines = [['Receipts.', 0], ['Deadlines.', 2], ['HMRC letters.', 4]];
    lines.forEach(([w, u0], i) => {
      const y = baseY - big * 1.02 * (2 - i) - big * 1.05;
      richLine(ctx, [[w, 'r']], X, y, big * 0.86, u, u0 - 0.12, 5.75, { color: i === 2 ? C.white : 'rgba(255,255,255,0.92)' });
    });
    richLine(ctx, [['It all ', 'r'], ['adds up.', 'i']], X, baseY, big, u, 6, 7.7);
  }
  // ---- S2 the date
  if (u > 9.6 && u < 15.4) {
    eyebrow(ctx, 'SELF ASSESSMENT', X, baseY - big * 1.25, u, 10, 14.7);
    richLine(ctx, [['31 January ', 'r'], ["won't wait.", 'i']], X, baseY, big * 0.9, u, 10.2, 14.8);
  }
  // ---- S3/S4 freeze + order
  if (u > 16 && u < 22.2) {
    richLine(ctx, [['Leave it ', 'r'], ['with us.', 'i']], X, baseY - big * 0.7, big * 1.05, u, 17.8, 21.6);
    eyebrow(ctx, 'RKN ACCOUNTANCY  ·  BURY', X, baseY + 10, u, 19, 21.6, 'left', 26);
  }
  // ---- S5 services as check-mark bullets
  if (u > 22 && u < 28.2) {
    const items = ['Taxation', 'Accounting & Bookkeeping', 'Business Advisory', 'Compliance & Filing'];
    const fs = FORMAT.pick({ '9x16': 74, '16x9': 62 }), gap = fs * 1.38;
    const y0 = P ? baseY - gap * 3 - 10 : H * 0.36;
    eyebrow(ctx, 'WHAT WE HANDLE', X, y0 - fs * 1.35, u, 22.2, 27.4);
    items.forEach((it, i) => {
      const u0 = 23 + i, y = y0 + i * gap;
      tickGlyph(ctx, X + 4, y - fs * 0.33, fs * 0.5, E.outCubic(prog(u, u0, u0 + 0.35)) * (1 - prog(u, 27.4, 27.8)));
      richLine(ctx, [[it, 'r']], X + fs * 0.95, y, fs, u, u0 - 0.15, 27.4, { stagger: 0.012 });
    });
  }
  // ---- S6 counter caption + sector flicker
  if (u > 28 && u < 36.2) {
    const cam = W3.camera;
    const [, dy] = toScreen(cam, ST.B, -0.25, 0);
    const cy = P ? Math.max(dy + 110, H * 0.62) : H * 0.74;
    const cxx = P ? W / 2 : W * 0.5 + 0;
    eyebrow(ctx, 'SECTORS WE SERVE', cxx, cy, u, 28.6, 35.6, 'center');
    const idx = Math.min(SECTORS.length - 1, Math.floor(prog(u, 28.6, 32) * SECTORS.length));
    const fs = FORMAT.pick({ '9x16': 64, '16x9': 58 });
    if (u > 28.6 && u < 33.3) {
      const name = SECTORS[idx];
      const k = (u - 28.6) * SECTORS.length / 3.4 % 1;
      ctx.save(); ctx.globalAlpha = (1 - prog(u, 33, 33.3)) * (0.55 + 0.45 * (1 - k));
      text(ctx, name, cxx, cy + fs * 1.45, font(fs, 500, DISPLAY), C.white, 'center');
      ctx.restore();
    }
    richLine(ctx, [['From start-up to ', 'r'], ['scale-up.', 'i']], cxx, cy + fs * 1.45, fs, u, 33.4, 35.5, { align: 'center', stagger: 0.015 });
  }
  // ---- S7 the review
  if (u > 36 && u < 44.2) {
    const fs = FORMAT.pick({ '9x16': 76, '16x9': 70 });
    const [, sy] = toScreen(W3.camera, ST.C, 0.1, 0);
    const y0 = P ? Math.max(sy + 120, H * 0.55) : H * 0.68;
    const cxx = W / 2;
    richLine(ctx, [['“Professional, qualified', 'i']], cxx, y0, fs, u, 38.4, 43.4, { align: 'center', stagger: 0.012 });
    richLine(ctx, [['and down to earth.”', 'i']], cxx, y0 + fs * 1.2, fs, u, 38.9, 43.4, { align: 'center', stagger: 0.012 });
    eyebrow(ctx, 'GOOGLE REVIEW', cxx, y0 + fs * 2.6, u, 39.8, 43.4, 'center', 24);
  }
  // ---- S8 promise over the turning ring
  if (u > 43.8 && u < 52.2) {
    const fs = FORMAT.pick({ '9x16': 132, '16x9': 120 });
    const cxx = W / 2, yc = H * (P ? 0.5 : 0.5);
    const words = [['Accurate.', 44], ['Personal.', 45.5], ['Proactive.', 47]];
    words.forEach(([w, u0], i) => {
      const y = yc - fs * 1.15 + i * fs * 1.15 + fs * 0.35;
      richLine(ctx, [[w, i === 2 ? 'i' : 'r']], cxx, y, fs, u, u0 - 0.1, 48.2, { align: 'center' });
    });
    const f2 = FORMAT.pick({ '9x16': 100, '16x9': 100 });
    if (P) {
      richLine(ctx, [['Accounting services', 'r']], cxx, yc - f2 * 0.2, f2, u, 48.4, 51.6, { align: 'center', stagger: 0.012 });
      richLine(ctx, [['that ', 'r'], ['work for you.', 'i']], cxx, yc + f2 * 1.0, f2, u, 48.7, 51.6, { align: 'center', stagger: 0.012 });
    } else {
      richLine(ctx, [['Accounting services that ', 'r'], ['work for you.', 'i']], cxx, yc + f2 * 0.35, f2, u, 48.4, 51.6, { align: 'center', stagger: 0.01 });
    }
    goldRule(ctx, cxx, yc + (P ? f2 * 1.45 : f2 * 0.8), 180, E.outCubic(prog(u, 49.4, 50.3)) * (1 - prog(u, 51.6, 52)), 'center');
  }
  // ---- S9 logo: the 3-D ring + tick match-cut to the real logo artwork
  if (u > 53.2) logoCard(ctx, u, IMG, W3);
}

// logo artwork geometry (assets/logo/logo_full.png, 712x474): ring centre + radius, measured
const LOGO = { w: 712, h: 474, cx: 348, cy: 182, r: 174 };
function logoCard(ctx, u, IMG, W3) {
  const cam = W3.camera;
  const [cx, cy] = toScreen(cam, ST.D, 0, 0);
  const [ex] = toScreen(cam, ST.D + 1, 0, 0);
  const rpx = Math.abs(ex - cx);
  const sc = rpx / LOGO.r;
  const k = E.inOutCubic(prog(u, 53.4, 54.1));
  // the monogram artwork exactly over the 3-D ring (crossfade), then the wordmark and lines below
  ctx.save();
  ctx.globalAlpha = k;
  ctx.fillStyle = C.charcoal; ctx.globalAlpha = k * 0.0; ctx.restore();
  ctx.save(); ctx.globalAlpha = k;
  const mono = IMG.logo;
  if (mono) {
    // monogram region only (rows 0..371), the wordmark reveals separately
    const sx = 0, sy = 0, sw = LOGO.w, sh = 372;
    ctx.drawImage(mono, sx, sy, sw, sh, cx - LOGO.cx * sc, cy - LOGO.cy * sc, sw * sc, sh * sc);
  }
  ctx.restore();
  // wordmark (exact artwork) wipes in
  const kw = E.outCubic(prog(u, 54.2, 55.0));
  if (mono && kw > 0) {
    const sy = 410, sh = 64, dy = cy - LOGO.cy * sc + sy * sc;
    ctx.save(); ctx.beginPath(); ctx.rect(cx - LOGO.cx * sc, dy - 4, LOGO.w * sc * kw + 1, sh * sc + 8); ctx.clip();
    ctx.drawImage(mono, 0, sy, LOGO.w, sh, cx - LOGO.cx * sc, dy + (1 - kw) * 8, LOGO.w * sc, sh * sc);
    ctx.restore();
  }
  const below = cy - LOGO.cy * sc + LOGO.h * sc;
  const fs = FORMAT.pick({ '9x16': 92, '16x9': 84 });
  const tx = cx - LOGO.cx * sc + (LOGO.w * sc) / 2;
  richLine(ctx, [['Your numbers. ', 'r'], ['Our care.', 'i']], tx, below + fs * 1.6, fs, u, 55, 99, { align: 'center', stagger: 0.02 });
  goldRule(ctx, tx, below + fs * 2.15, 150, E.outCubic(prog(u, 55.8, 56.6)), 'center');
  const k3 = E.outQuint(prog(u, 56.2, 57));
  if (k3 > 0) {
    ctx.save(); ctx.globalAlpha = k3;
    const f3 = FORMAT.pick({ '9x16': 40, '16x9': 34 });
    text(ctx, '0161 566 1549', tx, below + fs * 2.95 + (1 - k3) * 20, font(f3 * 1.25, 600, UI), C.white, 'center', 1);
    text(ctx, 'rknaccountancy.co.uk', tx, below + fs * 2.95 + f3 * 1.6 + (1 - k3) * 20, font(f3, 500, UI), C.bright, 'center', 1);
    text(ctx, 'Millett House, Bury  ·  Mon–Fri 9am–5:30pm', tx, below + fs * 2.95 + f3 * 2.9 + (1 - k3) * 20, font(f3 * 0.72, 500, UI), C.grey, 'center', 1);
    ctx.restore();
  }
}

// light flare where the tick hits "31" on beat 16
function flare(ctx, u, W3) {
  const a = bump(u, 16.05, 0.9) * 0.9 + bump(u, 53.55, 0.8) * 0.35;
  if (a <= 0.01) return;
  const cam = W3.camera;
  const [x, y] = u < 30 ? toScreen(cam, -0.05, 0.25, 0.16) : toScreen(cam, ST.D + 0.75, 0.2, 0);
  ctx.save(); ctx.globalCompositeOperation = 'lighter';
  const R = Math.max(W, H) * 0.5;
  const g = ctx.createRadialGradient(x, y, 0, x, y, R);
  g.addColorStop(0, `rgba(255,236,190,${0.55 * a})`); g.addColorStop(0.15, `rgba(228,188,84,${0.22 * a})`); g.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  // anamorphic streak
  const g2 = ctx.createLinearGradient(0, 0, W, 0);
  g2.addColorStop(0, 'rgba(228,188,84,0)'); g2.addColorStop(x / W, `rgba(255,240,200,${0.5 * a})`); g2.addColorStop(1, 'rgba(228,188,84,0)');
  ctx.fillStyle = g2; ctx.fillRect(0, y - 3, W, 6);
  ctx.restore();
}

// ============================================================ post: grade, vignette, grain
const GRAIN = [];
function makeGrain() {
  for (let k = 0; k < 6; k++) {
    const cv = document.createElement('canvas'); cv.width = 512; cv.height = 512;
    const c = cv.getContext('2d'); const id = c.createImageData(512, 512); const r = mulberry32(100 + k);
    for (let i = 0; i < id.data.length; i += 4) { const v = 128 + (r() - 0.5) * 120; id.data[i] = id.data[i + 1] = id.data[i + 2] = v; id.data[i + 3] = 255; }
    c.putImageData(id, 0, 0); GRAIN.push(cv);
  }
}
function post(ctx, u, t) {
  // vignette
  const g = ctx.createRadialGradient(W / 2, H / 2, Math.min(W, H) * 0.35, W / 2, H / 2, Math.hypot(W, H) * 0.6);
  g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,0.55)');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  // film grain (seeded, one of six plates per frame)
  const gr = GRAIN[Math.floor(t * 24) % GRAIN.length];
  if (gr) {
    ctx.save(); ctx.globalAlpha = 0.07; ctx.globalCompositeOperation = 'overlay';
    const ox = Math.floor(hash01(Math.floor(t * 24), 3) * 512), oy = Math.floor(hash01(Math.floor(t * 24), 4) * 512);
    ctx.translate(-ox, -oy);
    for (let x = 0; x < W + 512; x += 512) for (let y = 0; y < H + 512; y += 512) ctx.drawImage(gr, x, y);
    ctx.restore();
  }
}

// ============================================================ film
let WORLD = null;
M.film({
  fonts: [font(100, 500, DISPLAY), font(100, 500, ITALIC), font(40, 600, UI), font(40, 500, UI), font(40, 400, UI)],
  images: { logo: 'assets/logo/logo_full.png' },
  hits: HITS,
  samples: (t) => 4,
  shutter: 0.5,
  async init() {
    await G.initGL({ exposure: 0.86 });
    WORLD = buildWorld();
    makeGrain();
  },
  draw(ctx, u, t, IMG) {
    WORLD.update(t, u);
    background(ctx, u, WORLD.camera);
    G.renderSet(ctx, { scene: WORLD.scene, camera: WORLD.camera, update() {} }, t, u);
    flare(ctx, u, WORLD);
    overlay(ctx, u, IMG, WORLD);
  },
  post,
});
