// Renders floret/scene.html frame by frame with headless Chromium.
//   node floret/render.js still 0.8,3,6,10      -> PNG stills in $OUT/stills
//   node floret/render.js video [fps] [secs]    -> $OUT/video_silent.mp4
//   node floret/render.js atlas [fps] [secs]    -> $OUT/atlas/NNNN.jpg + $OUT/atlas/cards.json (Blender textures)
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');
const { chromium } = require(process.env.PLAYWRIGHT_PATH || '/opt/node22/lib/node_modules/playwright');

const OUT = process.env.OUT || path.join(__dirname, 'out');
const URL = 'file://' + path.join(__dirname, 'scene.html');
fs.mkdirSync(OUT, { recursive: true });

async function openPage(browser, atlas) {
  const page = atlas
    ? await browser.newPage({ viewport: { width: 2500, height: 1700 }, deviceScaleFactor: 1.5 })
    : await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await page.goto(URL + (atlas ? '#atlas' : ''));
  await page.evaluate(() => window.ready);
  await page.evaluate(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))));
  return page;
}

async function frame(page, t) {
  await page.evaluate(t => window.render(t), t);
  return page.screenshot({ type: 'png' });
}

async function stills(times) {
  const browser = await chromium.launch();
  const page = await openPage(browser);
  fs.mkdirSync(path.join(OUT, 'stills'), { recursive: true });
  for (const t of times) {
    const f = path.join(OUT, 'stills', `t${t.toFixed(2)}.png`);
    fs.writeFileSync(f, await frame(page, t));
    console.log(f);
  }
  await browser.close();
}

function encoder(file, fps) {
  return spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '14', '-pix_fmt', 'yuv420p', file], { stdio: ['pipe', 'inherit', 'inherit'] });
}

async function video(fps, secs, workers) {
  const total = Math.round(fps * secs);
  const per = Math.ceil(total / workers);
  const browser = await chromium.launch();
  const parts = [];
  await Promise.all([...Array(workers)].map(async (_, w) => {
    const a = w * per, b = Math.min(total, a + per);
    if (a >= b) return;
    const file = path.join(OUT, `part${w}.mp4`);
    parts[w] = file;
    const page = await openPage(browser);
    const enc = encoder(file, fps);
    for (let i = a; i < b; i++) {
      const buf = await frame(page, i / fps);
      if (!enc.stdin.write(buf)) await new Promise(r => enc.stdin.once('drain', r));
      if (w === 0 && (i - a) % 30 === 0) console.log(`frame ${i - a}/${b - a} (worker 0)`);
    }
    enc.stdin.end();
    await new Promise(r => enc.on('close', r));
  }));
  await browser.close();
  const list = path.join(OUT, 'parts.txt');
  fs.writeFileSync(list, parts.filter(Boolean).map(p => `file '${p}'`).join('\n'));
  const out = path.join(OUT, 'video_silent.mp4');
  await new Promise(r => spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', list, '-c', 'copy', out], { stdio: 'inherit' }).on('close', r));
  parts.filter(Boolean).forEach(p => fs.unlinkSync(p)); fs.unlinkSync(list);
  console.log(out);
}

async function atlas(fps, secs, workers) {
  const total = Math.round(fps * secs);
  const dir = path.join(OUT, 'atlas');
  fs.mkdirSync(dir, { recursive: true });
  const states = [];
  const browser = await chromium.launch();
  let next = 0;
  await Promise.all([...Array(workers)].map(async () => {
    const page = await openPage(browser, true);
    for (let i = next++; i < total; i = next++) {
      states[i] = await page.evaluate(t => { window.render(t); return window.cardState; }, i / fps);
      fs.writeFileSync(path.join(dir, String(i + 1).padStart(4, '0') + '.jpg'), await page.screenshot({ type: 'jpeg', quality: 95 }));
      if (i % 60 === 0) console.log(`atlas ${i}/${total}`);
    }
  }));
  await browser.close();
  fs.writeFileSync(path.join(dir, 'cards.json'), JSON.stringify({ fps, frames: total, cards: states }));
  console.log(dir);
}

const [mode, a, b] = process.argv.slice(2);
if (mode === 'still') stills((a || '1,4,8').split(',').map(Number));
else if (mode === 'atlas') atlas(Number(a || 30), Number(b || 12), Number(process.env.WORKERS || 4));
else video(Number(a || 30), Number(b || 12), Number(process.env.WORKERS || 4));
