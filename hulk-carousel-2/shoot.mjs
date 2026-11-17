// Render the carousel artboard: the full seamless strip plus each 1080x1350 slide.
//   node hulk-carousel-2/shoot.mjs   (from the repo root)
import { chromium } from '../node_modules/playwright/index.mjs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const DIR = path.dirname(fileURLToPath(import.meta.url));
const b = await chromium.launch({ executablePath: process.env.CHROME || '/opt/pw-browsers/chromium' });
const p = await b.newPage({ viewport: { width: 7560, height: 1350 } });
await p.goto(`file://${DIR}/artboard.html`);
await p.waitForFunction(() => window.ready === true);
await p.waitForTimeout(300);
await p.screenshot({ path: `${DIR}/out/strip.png`, clip: { x: 0, y: 0, width: 7560, height: 1350 } });
for (let i = 0; i < 7; i++) await p.screenshot({ path: `${DIR}/out/slide_${i + 1}.png`, clip: { x: i * 1080, y: 0, width: 1080, height: 1350 } });
await b.close();
console.log('rendered strip + 7 slides');
