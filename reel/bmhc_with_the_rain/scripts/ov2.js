// v2 overlay layer: every on-screen word and the end card as one timed HTML page.
// Each scene has its own text animation; all times come from timeline.json + the narration word timings.
// Usage: node ov2.js OUTDIR [t1,t2,...]   (with times: render only those stills, as OUTDIR/still_<t>.png)
const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path');
const B = path.resolve(__dirname, '..');
const TL = JSON.parse(fs.readFileSync(path.join(B, 'timeline.json'), 'utf8'));
const VO = JSON.parse(fs.readFileSync(path.join(B, 'audio/vo/lines.json'), 'utf8'));
const OUT = path.resolve(process.argv[2]);
const STILLS = process.argv[3] ? process.argv[3].split(',').map(Number) : null;
fs.mkdirSync(OUT, { recursive: true });

const css = `
@font-face{font-family:Poppins;font-weight:400;src:url('file://${B}/fonts/Poppins-Regular.ttf')}
@font-face{font-family:Poppins;font-weight:500;src:url('file://${B}/fonts/Poppins-Medium.ttf')}
@font-face{font-family:Poppins;font-weight:600;src:url('file://${B}/fonts/Poppins-SemiBold.ttf')}
@font-face{font-family:Poppins;font-weight:700;src:url('file://${B}/fonts/Poppins-Bold.ttf')}
@font-face{font-family:Playfair;font-style:italic;font-weight:700;src:url('file://${B}/fonts/PlayfairDisplay-BoldItalic.ttf')}
@font-face{font-family:Playfair;font-style:italic;font-weight:800;src:url('file://${B}/fonts/PlayfairDisplay-ExtraBoldItalic.ttf')}
@font-face{font-family:Hafs;src:url('file://${B}/fonts/UthmanicHafs1Ver18.woff2')}
html,body{margin:0;width:1080px;height:1920px;background:transparent;overflow:hidden}
*{box-sizing:border-box}
.abs{position:absolute}
.cap{position:absolute;left:64px;right:130px;top:1030px;font-family:Poppins;font-weight:600;color:#fff;font-size:60px;line-height:1.22;
  text-shadow:0 2px 18px rgba(0,0,0,.72),0 0 4px rgba(0,0,0,.5)}
.ln{display:block;white-space:nowrap}
.w{display:inline-block}
.k,.b{color:#74c6f2}.g{color:#e9b45a}
.s{font-family:Playfair,serif;font-style:italic;font-weight:700;font-size:1.12em;letter-spacing:.005em}   /* second typeface: bold serif italic for the key words */
.ar{font-family:Hafs;direction:rtl;color:#f4ece2;text-align:center}
.mask{display:inline-block;overflow:hidden;vertical-align:bottom;padding:0 .04em .06em}
.mask>span{display:inline-block}
`;

const body = `<!doctype html><meta charset="utf-8"><style>${css}</style><body><div id="root"></div>
<script>
const TL = ${JSON.stringify(TL)}, VO = ${JSON.stringify(VO)};
const SH = {}; TL.shots.forEach(s => SH[s.name] = s);
const ms = s => Math.round(s * 1000);
const root = document.getElementById('root');
const el = (html, parent = root) => { const d = document.createElement('div'); d.innerHTML = html.trim(); const n = d.firstChild; parent.appendChild(n); return n; };
// enter animations fill backwards (hidden before), exits fill forwards only, so the two never fight
const enter = (n, kf, t, dur, easing = 'cubic-bezier(.2,.8,.2,1)') => n.animate(kf, { delay: ms(t), duration: Math.max(1, ms(dur)), fill: 'both', easing });
const exit = (n, kf, t, dur, easing = 'cubic-bezier(.4,0,.6,1)') => n.animate(kf, { delay: ms(t), duration: Math.max(1, ms(dur)), fill: 'forwards', easing });
const fadeOut = (n, t, dur, extra = {}) => exit(n, [{ opacity: 1, ...extra.from }, { opacity: 0, ...extra.to }], t, dur);
const W = (L, i) => TL.vo[L] + VO[L].words[i].s;          // absolute time a word is spoken
const words = L => VO[L].words.map(w => w.w);
const span = (txt, cls = '') => '<span class="w ' + cls + '">' + txt + '</span>';
// build a caption: lines = [[wordIndex,...],...], cls = {wordIndex: 'k'|'g'}
function caption(L, lines, cls = {}, style = '', wrap = x => x) {
  const ws = words(L);
  const html = lines.map(line => '<span class="ln">' + line.map(i => wrap(span(ws[i], cls[i] || ''), i)).join(' ') + '</span>').join('');
  return el('<div class="cap" style="' + style + '">' + html + '</div>');
}
const wordEls = n => [...n.querySelectorAll('.w')];

// ---------- 1 · HOOK (curiosity): words condense out of the rain, blurred and falling into focus
{ const c = caption('L1', [[0, 1, 2], [3, 4, 5, 6, 7]], { 2: 'k s', 5: 's', 6: 's', 7: 's' });
  wordEls(c).forEach((w, i) => enter(w, [{ opacity: 0, filter: 'blur(14px)', transform: 'translateY(-30px)' }, { opacity: 1, filter: 'blur(0px)', transform: 'none' }], W('L1', i) - 0.06, 0.55));
  fadeOut(c, SH.window.end - 0.32, 0.26, { to: { filter: 'blur(8px)' } }); }

// ---------- 2 · PROBLEM (seriousness): staccato hard cuts, one weight per phrase, the last words left dim
{ const st = 'left:64px;right:130px;top:1000px;font-size:88px;font-weight:700;line-height:1.1';
  const P = [['A bill.', W('L2', 0), W('L2', 2)], ['<span class="s b">A loss.</span>', W('L2', 2), W('L2', 4)]];
  P.forEach(([txt, a, b]) => { const n = el('<div class="cap" style="' + st + '">' + txt + '</div>');
    enter(n, [{ opacity: 0, transform: 'scale(1.06)' }, { opacity: 1, transform: 'scale(1.06)', offset: .001 }, { opacity: 1, transform: 'scale(1)' }], a - 0.03, 0.16, 'linear');
    exit(n, [{ opacity: 1 }, { opacity: 0 }], b - 0.03, 0.001); });
  const n = el('<div class="cap" style="' + st + '"><span class="ln s">A worry</span><span class="ln b" style="font-weight:500;letter-spacing:.02em">' +
               '<span class="w" id="nb">nobody sees.</span></span></div>');
  enter(n, [{ opacity: 0, transform: 'scale(1.06)' }, { opacity: 1, transform: 'scale(1.06)', offset: .001 }, { opacity: 1, transform: 'scale(1)' }], W('L2', 4) - 0.03, 0.16, 'linear');
  enter(n.querySelector('#nb'), [{ opacity: 0 }, { opacity: 1 }], W('L2', 6) - 0.03, 0.001, 'linear');
  fadeOut(n, SH.man.end - 0.55, 0.35); }

// ---------- 3 · VERSE (the key message): Arabic revealed by a sweep of light, right to left, with each recitation
{ const lines = ['فَإِنَّ مَعَ ٱلۡعُسۡرِ يُسۡرًا ٥', 'إِنَّ مَعَ ٱلۡعُسۡرِ يُسۡرٗا ٦'];
  const tops = [520, 680];
  const reveal = 'linear-gradient(to left, #000 0%, #000 44%, transparent 56%, transparent 100%)';
  const glint = 'linear-gradient(to left, transparent 0%, transparent 43%, #000 49.5%, transparent 56%, transparent 100%)';
  const grp = el('<div class="abs" style="inset:0"></div>');
  [['rec5', 0], ['rec6', 1]].forEach(([k, i]) => {
    const base = 'position:absolute;left:50%;transform:translateX(-50%);white-space:nowrap;padding:0 30px;top:' + tops[i] + 'px;font-size:84px;line-height:1.6;';
    const m = 'mask-image:@@;-webkit-mask-image:@@;mask-size:300% 100%;-webkit-mask-size:300% 100%;mask-repeat:no-repeat;-webkit-mask-repeat:no-repeat;';
    const a = el('<div class="ar" style="' + base + m.replaceAll('@@', reveal) + 'text-shadow:0 2px 24px rgba(0,0,0,.6)">' + lines[i] + '</div>', grp);
    const g = el('<div class="ar" style="' + base + m.replaceAll('@@', glint) + 'color:#ffe2a6;text-shadow:0 0 18px rgba(255,214,140,.9)">' + lines[i] + '</div>', grp);
    const t0 = TL.vo[k] - 0.15, d = (k === 'rec5' ? 4.414 : 4.111) * 0.82;   // sweep follows the recitation
    [a, g].forEach(n => enter(n, [{ maskPosition: '0% 0', webkitMaskPosition: '0% 0' }, { maskPosition: '100% 0', webkitMaskPosition: '100% 0' }], t0, d, 'cubic-bezier(.3,.15,.45,.95)'));
    exit(g, [{ opacity: 1 }, { opacity: 0 }], t0 + d - 0.4, 0.5);
  });
  const tr = (txt, top, t) => { const n = el('<div style="position:absolute;left:90px;right:90px;top:' + top + 'px;text-align:center;font-family:Poppins;font-weight:500;font-size:44px;line-height:1.35;color:#f2ede4;text-shadow:0 2px 16px rgba(0,0,0,.65)">' + txt + '</div>', grp);
    enter(n, [{ opacity: 0, transform: 'translateY(14px)' }, { opacity: 1, transform: 'none' }], t, 0.7); };
  tr('“For indeed, with hardship [will be] ease.', 960, W('L3', 2) - 0.12);
  tr('Indeed, with hardship [will be] ease.”', 1080, W('L3', 9) - 0.12);
  const ref = el('<div style="position:absolute;left:0;right:0;top:1210px;text-align:center;font-family:Poppins;font-weight:600;font-size:28px;color:#e9b45a">ASH-SHARH 94:5–6</div>', grp);
  enter(ref, [{ opacity: 0, letterSpacing: '.5em' }, { opacity: 1, letterSpacing: '.14em' }], TL.vo.L3 - 0.05, 1.0, 'cubic-bezier(.2,.7,.2,1)');
  fadeOut(grp, SH.verse.end - 0.75, 0.5); }

// ---------- 4a · "Notice the word: with." typed letter by letter; "with" then lifts off and becomes the gold مَعَ
let withCap;
{ const ws = words('L4'); const n4 = 4;
  const c = el('<div class="cap"><span class="ln">' + [0, 1, 2].map(i => '<span class="w">' + [...ws[i]].map(ch => '<span class="ch">' + ch + '</span>').join('') + '</span>').join(' ') +
               '</span><span class="ln"><span class="w g s" id="with">' + [...ws[3]].map(ch => '<span class="ch">' + ch + '</span>').join('') + '</span></span></div>');
  const wEls = wordEls(c);
  wEls.forEach((w, i) => { const a = W('L4', i), b = i < 3 ? W('L4', i + 1) : W('L4', i) + 0.32; const chs = [...w.querySelectorAll('.ch')];
    chs.forEach((ch, j) => enter(ch, [{ opacity: 0 }, { opacity: 1 }], a - 0.04 + (b - a) * 0.8 * j / chs.length, 0.001, 'linear')); });
  exit(c, [{ opacity: 1 }, { opacity: 0 }], SH.umbrella.end - 0.03, 0.001);
  withCap = c; }
const MA = el('<div class="abs" style="left:0;right:0;top:330px;height:560px"><div class="ar" id="ma" style="position:absolute;left:0;right:0;top:0;font-size:210px;color:#efb95c;text-shadow:0 3px 10px rgba(0,0,0,.7),0 4px 44px rgba(0,0,0,.75)">مَعَ</div>' +
  '<div id="wi" style="position:absolute;left:0;right:0;top:470px;text-align:center;font-family:Poppins;font-weight:700;font-size:46px;color:#ffe3a8;text-shadow:0 2px 6px rgba(0,0,0,.95),0 0 26px rgba(0,0,0,.85)">WITH</div></div>');
function wireWith() {   // needs layout, so it runs after fonts load
  const src = document.getElementById('with').getBoundingClientRect();
  const fly = el('<div class="abs g" style="left:' + src.left + 'px;top:' + src.top + 'px;font-family:Playfair,serif;font-style:italic;font-weight:700;font-size:67px;line-height:1.22;transform-origin:0 0;text-shadow:0 0 30px rgba(233,180,90,.8)">' + words('L4')[3] + '</div>');
  const t = W('L4', 3) + 0.2;
  const dx = 540 - (src.left + src.width / 2), dy = 470 - (src.top + src.height / 2);
  enter(fly, [{ opacity: 0, transform: 'none' }, { opacity: 1, transform: 'none', offset: .01 }, { opacity: 0, transform: 'translate(' + dx + 'px,' + dy + 'px) scale(2.6)', filter: 'blur(6px)' }], t, 0.6, 'cubic-bezier(.5,0,.3,1)');
  enter(document.getElementById('ma'), [{ opacity: 0, transform: 'scale(.82)', filter: 'blur(10px)' }, { opacity: 1, transform: 'none', filter: 'blur(0px)' }], t + 0.28, 0.6);
  enter(document.getElementById('wi'), [{ opacity: 0, letterSpacing: '.7em' }, { opacity: 1, letterSpacing: '.26em' }], t + 0.42, 0.7);
  fadeOut(MA, SH.with2.end - 0.42, 0.4, { to: { transform: 'translateY(-20px)' } });
}

// ---------- 4b · "Not only after the hardship." slides in word by word, quieter; "With it." lands hard in gold
{ const ws = words('L4');
  const c = el('<div class="cap"><span class="ln" style="font-weight:500;color:rgba(255,255,255,.88)">' + [4, 5, 6].map(i => span(ws[i])).join(' ') + '</span>' +
               '<span class="ln" style="font-weight:500;color:rgba(255,255,255,.88)">' + [7, 8].map(i => span(ws[i])).join(' ') + '</span>' +
               '<span class="ln" style="font-size:84px;line-height:1.25;font-weight:700">' + span(ws[9], 'g s') + ' ' + span(ws[10], 'g s') + '</span>' +
               '<div id="ul" style="height:6px;width:300px;background:#e9b45a;border-radius:3px;transform-origin:0 50%;box-shadow:0 0 14px rgba(233,180,90,.7)"></div></div>');
  const we = wordEls(c);
  we.forEach((w, k) => { const i = 4 + k;
    if (i < 9) enter(w, [{ opacity: 0, transform: 'translateX(-22px)' }, { opacity: 1, transform: 'none' }], W('L4', i) - 0.05, 0.26);
    else enter(w, [{ opacity: 0, transform: 'scale(1.5)', filter: 'blur(4px)' }, { opacity: 1, transform: 'scale(.97)', filter: 'blur(0px)', offset: .7 }, { opacity: 1, transform: 'none' }], W('L4', i) - 0.06, 0.32, 'cubic-bezier(.3,.6,.2,1)'); });
  enter(c.querySelector('#ul'), [{ transform: 'scaleX(0)' }, { transform: 'scaleX(1)' }], W('L4', 10) + 0.05, 0.4);
  fadeOut(c, SH.with2.end - 0.22, 0.2); }

// ---------- 5a · "Ease often comes / while it's still raining:" breathes out: wide tracking settling to normal
{ const ws = words('L5');
  const c = el('<div class="cap" style="left:40px;right:40px;text-align:center;font-weight:500"><span class="ln">' + span(ws[0], 'g s') + ' ' + [1, 2].map(i => span(ws[i])).join(' ') + '</span>' +
               '<span class="ln">' + [3, 4].map(i => span(ws[i])).join(' ') + ' ' + span(ws[5], 'k s') + ' ' + span(ws[6], 'k s') + '</span></div>');
  const L = [...c.querySelectorAll('.ln')];
  [[L[0], W('L5', 0)], [L[1], W('L5', 3)]].forEach(([n, t]) => enter(n, [{ opacity: 0, letterSpacing: '.34em', filter: 'blur(6px)' }, { opacity: 1, letterSpacing: '0em', filter: 'blur(0px)' }], t - 0.08, 0.95, 'cubic-bezier(.15,.7,.2,1)'));
  fadeOut(c, SH.ease.end - 0.3, 0.28, { to: { transform: 'translateY(18px)' } }); }

// ---------- 5b · "someone who sits / with you," rises word by word out of a baseline mask
{ const c = caption('L5', [[7, 8, 9], [10, 11]], { 10: 'k s', 11: 'k s' }, 'top:1040px', x => '<span class="mask">' + x + '</span>');
  wordEls(c).forEach((w, k) => enter(w, [{ transform: 'translateY(108%)' }, { transform: 'none' }], W('L5', 7 + k) - 0.06, 0.42, 'cubic-bezier(.2,.9,.25,1)'));
  exit(c, [{ opacity: 1 }, { opacity: 0 }], SH.console.end - 0.02, 0.001); }

// ---------- 6 · "a friend who calls," arrives as an incoming-call pill that drops in on the buzz
{ const ws = words('L6');
  const p = el('<div class="abs" style="left:64px;top:1010px;height:124px;padding:0 44px 0 22px;display:flex;align-items:center;gap:26px;border-radius:62px;background:rgba(14,40,36,.78);border:1.5px solid rgba(255,255,255,.2);box-shadow:0 18px 50px rgba(0,0,0,.45)">' +
    '<div id="ic" style="width:82px;height:82px;border-radius:50%;background:#76BF43;display:flex;align-items:center;justify-content:center;box-shadow:0 0 0 0 rgba(118,191,67,.6)">' +
    '<svg width="44" height="44" viewBox="0 0 24 24"><path fill="#fff" d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1A17 17 0 0 1 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.3 0 .7-.2 1z"/></svg></div>' +
    '<div style="font-family:Poppins;font-weight:600;font-size:54px;color:#fff;white-space:nowrap">' + ws.map((w, i) => span(w, i === 1 ? 'k s' : '')).join(' ') + '</div></div>');
  const t0 = SH.phonep.start;
  enter(p, [{ opacity: 0, transform: 'translateY(-70px) scale(.92)' }, { opacity: 1, transform: 'translateY(8px) scale(1)', offset: .7 }, { opacity: 1, transform: 'none' }], t0 - 0.02, 0.42, 'cubic-bezier(.2,.8,.3,1)');
  const ic = p.querySelector('#ic');
  enter(ic, [{ transform: 'rotate(0deg)' }, { transform: 'rotate(-14deg)' }, { transform: 'rotate(12deg)' }, { transform: 'rotate(-10deg)' }, { transform: 'rotate(8deg)' }, { transform: 'rotate(0deg)' }], t0 + 0.05, 0.5, 'linear');
  enter(ic, [{ boxShadow: '0 0 0 0 rgba(118,191,67,.6)' }, { boxShadow: '0 0 0 26px rgba(118,191,67,0)' }], t0 + 0.1, 0.9, 'ease-out');
  wordEls(p).forEach((w, i) => enter(w, [{ opacity: 0 }, { opacity: 1 }], W('L6', i) - 0.05, 0.16));
  fadeOut(p, SH.phonep.end - 0.24, 0.24, { to: { transform: 'translateY(-30px)' } }); }

// ---------- 7 · "a door that's open." opens from a centre slit, like the door itself
{ const c = caption('L7', [[0, 1, 2, 3]], { 1: 'g s', 3: 'g s' }, 'left:40px;right:40px;text-align:center;font-size:66px');
  const ln = c.querySelector('.ln');
  enter(ln, [{ clipPath: 'inset(-20% 50% -20% 50%)', opacity: .4 }, { clipPath: 'inset(-20% 0% -20% 0%)', opacity: 1 }], W('L7', 0) - 0.06, 0.95, 'cubic-bezier(.6,0,.2,1)');
  enter(c.querySelectorAll('.w')[3], [{ textShadow: '0 2px 18px rgba(0,0,0,.72)' }, { textShadow: '0 0 34px rgba(255,200,120,.95)' }], W('L7', 3), 0.5);
  fadeOut(c, SH.bmhc.end - 0.32, 0.28, { to: { transform: 'scale(1.08)', filter: 'blur(4px)' } }); }

// ---------- 8a · "Whatever you are / going through," appears dim, each word lit as it is spoken
{ const c = caption('L8', [[0, 1, 2], [3, 4]], { 3: 's', 4: 's' }, 'font-weight:600');
  enter(c, [{ opacity: 0 }, { opacity: 1 }], TL.vo.L8 - 0.2, 0.2);
  wordEls(c).forEach((w, i) => enter(w, i < 3 ? [{ color: 'rgba(255,255,255,.3)' }, { color: 'rgba(255,255,255,1)' }] : [{ color: 'rgba(116,198,242,.3)' }, { color: 'rgba(116,198,242,1)' }], W('L8', i) - 0.03, 0.14, 'linear'));
  fadeOut(c, SH.inside.end - 0.2, 0.2, { to: { filter: 'blur(6px)' } }); }

// ---------- 8b · "support is just / a conversation away." with a gold line drawn under it as it is spoken,
//                that line then runs to the edges and the end card opens out of it
const LINE_Y = 1236;
{ const c = caption('L8', [[5, 6, 7], [8, 9, 10]], { 5: 'k s', 9: 's' }, 'top:1060px');
  wordEls(c).forEach((w, k) => enter(w, [{ opacity: 0, transform: 'translateY(10px)' }, { opacity: 1, transform: 'none' }], W('L8', 5 + k) - 0.05, 0.2));
  fadeOut(c, SH.convo.end - 0.42, 0.3);
  const ln = el('<div class="abs" style="left:0;width:1080px;top:' + LINE_Y + 'px;height:6px;background:#e9b45a;box-shadow:0 0 16px rgba(233,180,90,.75);transform-origin:0 50%"></div>');
  const a = W('L8', 5) - 0.05, b = TL.vo.L8 + VO.L8.dur, E = SH.convo.end;
  // grows under the words (64px -> 680px), then runs out to both edges
  ln.animate([{ clipPath: 'inset(0 1016px 0 64px)', offset: 0 }, { clipPath: 'inset(0 400px 0 64px)', offset: (b - a) / (E + 0.05 - a) },
              { clipPath: 'inset(0 400px 0 64px)', offset: (E - 0.45 - a) / (E + 0.05 - a) }, { clipPath: 'inset(0 0px 0 0px)', offset: 1 }],
             { delay: ms(a), duration: ms(E + 0.05 - a), fill: 'both', easing: 'linear' });
  fadeOut(ln, E + 0.45, 0.35); }

// ---------- 9 · END CARD (brand reveal): the panel opens from the gold line, logo, title, then the button gets tapped
{ const E = SH.endcard.start, L9 = TL.vo.L9;
  const panel = el('<div class="abs" style="inset:0;background:#122F2A"></div>');
  enter(panel, [{ clipPath: 'inset(' + (LINE_Y + 3) + 'px 0 ' + (1920 - LINE_Y - 3) + 'px 0)' }, { clipPath: 'inset(0 0 0 0)' }], E - 0.05, 0.62, 'cubic-bezier(.7,0,.2,1)');
  const bars = el('<div class="abs" style="left:0;right:0;bottom:0;height:22px;display:flex">' + ['#DB225E', '#09999C', '#F26721', '#76BF43'].map(c => '<span style="flex:1;background:' + c + ';transform-origin:0 50%"></span>').join('') + '</div>');
  [...bars.children].forEach((b, i) => enter(b, [{ transform: 'scaleX(0)' }, { transform: 'scaleX(1)' }], E + 0.5 + i * 0.08, 0.45));
  const logo = el('<img class="abs" src="file://${B}/logo_white_4x.png" style="left:250px;top:300px;width:580px">');
  enter(logo, [{ opacity: 0, transform: 'scale(.94)' }, { opacity: 1, transform: 'none' }], E + 0.4, 0.7);
  const title = el('<div class="abs" style="left:60px;right:60px;top:640px;text-align:center;font-family:Poppins;font-weight:700;font-size:66px;line-height:1.16;color:#fff">' +
    '<span class="mask"><span>Imam Counselling</span></span><br><span class="mask"><span class="s" style="font-size:1.04em">at BMHC</span></span></div>');
  [...title.querySelectorAll('.mask>span')].forEach((s, i) => enter(s, [{ transform: 'translateY(105%)' }, { transform: 'none' }], L9 - 0.1 + i * 0.5 + (i ? VO.L9.words[2].s : 0) * 0, 0.55, 'cubic-bezier(.2,.9,.25,1)'));
  // button: outline draws in gold, fills teal, then a cursor taps it
  const BX = 150, BY = 845, BW = 780, BH = 124, RX = 500;   // RX: where the cursor taps, from the button's left edge
  const btn = el('<div class="abs" style="left:' + BX + 'px;top:' + BY + 'px;width:' + BW + 'px;height:' + BH + 'px;transform-origin:50% 50%">' +
    '<svg class="abs" width="' + BW + '" height="' + BH + '" style="left:0;top:0;overflow:visible"><rect id="bo" x="2" y="2" width="' + (BW - 4) + '" height="' + (BH - 4) + '" rx="' + (BH / 2 - 2) + '" fill="none" stroke="#e9b45a" stroke-width="4" pathLength="1000" stroke-dasharray="1000" stroke-dashoffset="1000"/></svg>' +
    '<div id="bf" class="abs" style="inset:0;border-radius:' + BH / 2 + 'px;background:linear-gradient(180deg,#0bb3b5,#09807f);box-shadow:0 14px 40px rgba(0,0,0,.35), inset 0 1px 0 rgba(255,255,255,.35);overflow:hidden">' +
    '<div id="rp" class="abs" style="width:80px;height:80px;margin:-40px 0 0 -40px;border-radius:50%;background:rgba(255,255,255,.55);left:' + RX + 'px;top:70px"></div></div>' +
    '<div id="bl" class="abs" style="inset:0;display:flex;align-items:center;justify-content:center;gap:18px;font-family:Poppins;font-weight:600;font-size:44px;color:#fff;letter-spacing:.01em">Start the conversation' +
    '<svg width="40" height="40" viewBox="0 0 24 24"><path d="M5 12h13M13 6l6 6-6 6" stroke="#fff" stroke-width="2.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg></div></div>');
  const tB = L9 + 1.15;
  enter(btn.querySelector('#bo'), [{ strokeDashoffset: 1000 }, { strokeDashoffset: 0 }], tB, 0.55, 'cubic-bezier(.5,0,.3,1)');
  enter(btn.querySelector('#bf'), [{ opacity: 0 }, { opacity: 1 }], tB + 0.45, 0.3);
  enter(btn.querySelector('#bl'), [{ opacity: 0, transform: 'translateY(8px)' }, { opacity: 1, transform: 'none' }], tB + 0.55, 0.3);
  const tTap = tB + 1.45; window.TAP = tTap;
  enter(btn, [{ transform: 'scale(1)' }, { transform: 'scale(.94)', offset: .35 }, { transform: 'scale(1.02)', offset: .75 }, { transform: 'scale(1)' }], tTap - 0.02, 0.36, 'ease-out');
  enter(btn.querySelector('#rp'), [{ transform: 'scale(0)', opacity: .9 }, { transform: 'scale(9)', opacity: 0 }], tTap, 0.65, 'cubic-bezier(.2,.7,.3,1)');
  enter(btn.querySelector('#bf'), [{ filter: 'brightness(1)' }, { filter: 'brightness(1.28)', offset: .25 }, { filter: 'brightness(1)' }], tTap, 0.5);
  // cursor (arrow) glides in, taps, eases away
  const cur = el('<svg class="abs" width="70" height="96" viewBox="0 0 28 38" style="left:0;top:0;filter:drop-shadow(0 6px 10px rgba(0,0,0,.45));transform-origin:4px 3px">' +
    '<path d="M3 2 L3 31 L10 24.5 L15 35.5 L20.5 33 L15.5 22.5 L25 22.5 Z" fill="#fff" stroke="#111" stroke-width="1.6" stroke-linejoin="round"/></svg>');
  const P0 = [905, 1460], P1 = [BX + RX, BY + 70];
  enter(cur, [{ opacity: 0, transform: 'translate(' + P0[0] + 'px,' + P0[1] + 'px)' }, { opacity: 1, transform: 'translate(' + (P0[0] - 40) + 'px,' + (P0[1] - 60) + 'px)', offset: .15 },
              { opacity: 1, transform: 'translate(' + P1[0] + 'px,' + P1[1] + 'px)' }], tTap - 0.8, 0.72, 'cubic-bezier(.3,.1,.2,1)');
  enter(cur.querySelector('path'), [{ transform: 'scale(1)' }, { transform: 'scale(.82)', offset: .4 }, { transform: 'scale(1)' }], tTap - 0.04, 0.3);
  exit(cur, [{ opacity: 1 }, { opacity: 0 }], tTap + 0.9, 0.35);
  const det = el('<div class="abs" style="left:60px;right:60px;top:1010px;text-align:center;font-family:Poppins;font-weight:500;font-size:36px;line-height:1.5;color:#d9e5e0">Confidential · 0161 881 8062 (opening hours)<br><span style="color:#7fd6cf;font-weight:600">bmhc.org.uk/imam-counselling</span></div>');
  enter(det, [{ opacity: 0, transform: 'translateY(16px)' }, { opacity: 1, transform: 'none' }], tTap + 0.25, 0.5);
  const cri = el('<div class="abs" style="left:90px;right:90px;top:1170px;text-align:center;font-family:Poppins;font-weight:400;font-size:28px;line-height:1.45;color:rgba(255,255,255,.84)">Need to talk? Samaritans, free, day or night: 116 123.<br>Urgent mental health help: NHS 111, mental health option.<br>Emergency: 999.</div>');
  enter(cri, [{ opacity: 0 }, { opacity: 1 }], tTap + 0.65, 0.5);
  const cr = el('<div class="abs" style="left:0;right:0;top:1330px;text-align:center;font-family:Poppins;font-size:21px;color:rgba(255,255,255,.55)">Stock footage · building and community photos are BMHC’s own</div>');
  enter(cr, [{ opacity: 0 }, { opacity: 1 }], tTap + 1.0, 0.5); }

window.setup = async () => { await document.fonts.ready; await new Promise(r => setTimeout(r, 50)); wireWith();
  document.getAnimations().forEach(a => a.pause()); return window.TAP; };
window.seek = t => { const m = t * 1000; document.getAnimations().forEach(a => { a.currentTime = m; }); };
</script>`;

(async () => {
  const tmp = path.join(B, 'overlays', '_ov2.html');
  fs.writeFileSync(tmp, body);
  const b = await chromium.launch();
  const NP = STILLS ? 1 : 4;
  const fps = 30, n = Math.round(TL.end * fps);
  const frames = STILLS ? STILLS.map(t => Math.round(t * fps)) : [...Array(n).keys()];
  let tap = null;
  const work = async k => {
    const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
    await p.goto('file://' + tmp, { waitUntil: 'load' });
    tap = await p.evaluate(() => window.setup());
    for (let j = k; j < frames.length; j += NP) {
      const fi = frames[j];
      await p.evaluate(t => window.seek(t), fi / fps);
      const name = STILLS ? `still_${(fi / fps).toFixed(2)}.png` : `f_${String(fi).padStart(5, '0')}.png`;
      await p.screenshot({ path: path.join(OUT, name), omitBackground: true });
      if (!STILLS && j % 200 < NP) console.log(j, '/', frames.length);
    }
  };
  await Promise.all([...Array(NP).keys()].map(work));
  fs.writeFileSync(path.join(OUT, 'meta.json'), JSON.stringify({ tap, frames: frames.length }));
  await b.close();
  console.log('done tap', tap);
})();
