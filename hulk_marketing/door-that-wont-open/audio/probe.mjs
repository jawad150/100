// probe.mjs: sample the film's walk cycle and write audio/steps.json (heel-strike times) for the SFX build.
//   node door-that-wont-open/audio/probe.mjs   (from hulk_marketing/)
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const ROOT = process.cwd(), FILM = 'door-that-wont-open';
const types = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.woff2': 'font/woff2', '.png': 'image/png' };
const server = http.createServer((req, res) => {
  const f = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
  if (!fs.existsSync(f)) { res.writeHead(404); res.end(); return; }
  res.writeHead(200, { 'content-type': types[path.extname(f)] || 'application/octet-stream' }); fs.createReadStream(f).pipe(res);
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const b = await chromium.launch();
const page = await b.newPage();
await page.goto(`http://127.0.0.1:${server.address().port}/${FILM}/index.html?render=1&format=9x16&fps=30`);
await page.waitForFunction(() => window.filmReady === true, null, { timeout: 60000 });
const samples = await page.evaluate(() => { const out = []; for (let t = 0; t < 36.5; t += 1 / 240) out.push([t, window.PROBE(t)]); return out; });
await b.close(); server.close();
// heel strikes: phase crosses pi/2 + k*pi while walking (and not during the rewind)
const steps = [];
for (let i = 1; i < samples.length; i++) {
  const [t, s] = samples[i], [, p] = samples[i - 1];
  if (t > 24.9 && t < 26.25) continue;
  if (s.walk < 0.3) continue;
  const k0 = Math.floor((p.phase - Math.PI / 2) / Math.PI), k1 = Math.floor((s.phase - Math.PI / 2) / Math.PI);
  if (k1 > k0) steps.push({ t: +t.toFixed(3), x: +s.x.toFixed(1), walk: +s.walk.toFixed(2), inside: s.inside > 0.3 || s.enterA });
}
fs.writeFileSync(path.join(ROOT, FILM, 'audio', 'steps.json'), JSON.stringify(steps, null, 1));
console.log(`${steps.length} steps:`, steps.map((s) => s.t).join(' '));
