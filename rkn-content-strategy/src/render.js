let pw; try { pw = require('playwright'); } catch (e) { pw = require('/opt/node-tools/node_modules/playwright'); }
const { chromium } = pw;
const path = require('path');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const dir = __dirname;
  await page.goto('file://' + path.join(dir, 'cover.html'), { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({ path: path.join(dir, 'cover.pdf'), format: 'A4', printBackground: true, preferCSSPageSize: true });
  await page.goto('file://' + path.join(dir, 'body.html'), { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({
    path: path.join(dir, 'body.pdf'), format: 'A4', printBackground: true, preferCSSPageSize: true,
    displayHeaderFooter: true,
    headerTemplate: '<div></div>',
    footerTemplate: '<div style="width:100%;font-family:Inter,sans-serif;font-size:7px;color:#8a8478;padding:0 14mm;display:flex;justify-content:space-between;"><span>RKN Accountancy · Video Content Strategy &amp; Shoot Plan · October 2026</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>',
    margin: { top: '14mm', bottom: '17mm', left: '14mm', right: '14mm' }
  });
  await browser.close();
})();
