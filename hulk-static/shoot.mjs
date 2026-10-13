// Render the static post variants to PNG, then the concept deck to PDF.
//   node hulk-static/shoot.mjs            (run from the repo root)
import { chromium } from '../node_modules/playwright/index.mjs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const DIR = path.dirname(fileURLToPath(import.meta.url));
const SIZES = { '4x5': [1080, 1350], '1x1': [1080, 1080], '9x16': [1080, 1920] };
const only = process.argv[2];
const b = await chromium.launch();
if (only !== 'deck') {
  for (const [fmt, [w, h]] of Object.entries(SIZES)) for (const theme of ['dark', 'light']) {
    const p = await b.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
    await p.goto(`file://${DIR}/post.html?fmt=${fmt}&theme=${theme}`);
    await p.waitForFunction(() => window.ready === true);
    await p.locator('#post').screenshot({ path: `${DIR}/out/post_${fmt}_${theme}.png` });
    await p.close();
    console.log(`post_${fmt}_${theme}.png`);
  }
}
if (only !== 'posts') {
  const p = await b.newPage();
  await p.goto(`file://${DIR}/deck.html`);
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(400);
  await p.pdf({ path: `${DIR}/out/Hulk_Marketing_Static_Post_Concept.pdf`, width: '1920px', height: '1080px', printBackground: true, preferCSSPageSize: true });
  console.log('deck pdf');
}
await b.close();
