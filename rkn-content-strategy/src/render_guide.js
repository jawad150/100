let pw; try { pw = require('playwright'); } catch (e) { pw = require('/opt/node-tools/node_modules/playwright'); }
const { chromium } = pw;
const path = require('path');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const dir = __dirname;
  await page.goto('file://' + path.join(dir, 'guide_cover.html'), { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({ path: path.join(dir, 'guide_cover.pdf'), format: 'A4', printBackground: true, preferCSSPageSize: true });
  await page.goto('file://' + path.join(dir, 'guide.html'), { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({
    path: path.join(dir, 'guide_body.pdf'), format: 'A4', printBackground: true, preferCSSPageSize: true,
    displayHeaderFooter: true,
    headerTemplate: '<div></div>',
    footerTemplate: '<div style="width:100%;font-family:Inter,sans-serif;font-size:7px;color:#8a8478;padding:0 14mm;display:flex;justify-content:space-between;"><span>RKN Accountancy · On-Set Shooting Guide · 21 October 2026</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>',
    margin: { top: '14mm', bottom: '17mm', left: '14mm', right: '14mm' }
  });
  await browser.close();
})();
