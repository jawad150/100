// Render storyboard frames (1080x1920) from a JSON spec: [{out, bg, bgPos, grade, html}]
const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path');
(async () => {
  const spec = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const base = path.resolve(process.argv[3] || '.');
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  for (const f of spec) {
    const bg = f.bg ? `url('file://${path.resolve(base, f.bg)}')` : 'none';
    const html = `<!doctype html><meta charset="utf-8"><style>
@font-face{font-family:Poppins;font-weight:400;src:url('file://${base}/fonts/Poppins-Regular.ttf')}
@font-face{font-family:Poppins;font-weight:500;src:url('file://${base}/fonts/Poppins-Medium.ttf')}
@font-face{font-family:Poppins;font-weight:600;src:url('file://${base}/fonts/Poppins-SemiBold.ttf')}
@font-face{font-family:Poppins;font-weight:700;src:url('file://${base}/fonts/Poppins-Bold.ttf')}
@font-face{font-family:Hafs;src:url('file://${base}/fonts/UthmanicHafs1Ver18.woff2')}
@font-face{font-family:Amiri;src:url('file://${base}/fonts/Amiri-Regular.ttf')}
html,body{margin:0;width:1080px;height:1920px;overflow:hidden;background:#0b1512}
.bg{position:absolute;inset:0;background:${bg} ${f.bgPos||'center'}/cover no-repeat;filter:${f.grade||'none'}}
.shade{position:absolute;inset:0;background:${f.shade||'linear-gradient(180deg,rgba(0,0,0,.0) 45%,rgba(0,0,0,.45) 70%,rgba(0,0,0,.15) 100%)'}}
.cap{position:absolute;left:60px;right:120px;font-family:Poppins;font-weight:600;color:#fff;font-size:58px;line-height:1.22;text-shadow:0 2px 18px rgba(0,0,0,.7),0 0 4px rgba(0,0,0,.5)}
.cap .k{color:#7fd6cf}.cap .g{color:#e9b45a}
.small{font-family:Poppins;font-weight:500;color:rgba(255,255,255,.85);font-size:30px}
.ar{font-family:Hafs;direction:rtl;color:#f4ece2;text-align:center}
.tc{position:absolute;left:36px;top:36px;font-family:Poppins;font-weight:600;font-size:26px;color:rgba(255,255,255,.75);letter-spacing:.08em}
</style><div class="bg"></div><div class="shade"></div>${f.html||''}${f.tc?`<div class="tc">${f.tc}</div>`:''}`;
    const tmp = path.resolve(base, 'frames', '_tmp_' + path.basename(f.out, '.jpg') + '.html');
    fs.writeFileSync(tmp, html);
    await p.goto('file://' + tmp, { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    await p.waitForTimeout(150);
    await p.screenshot({ path: path.resolve(base, f.out), type: 'jpeg', quality: 88 });
    console.log('ok', f.out);
  }
  await b.close();
})();
