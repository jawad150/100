const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path');
const B = path.resolve(__dirname, '..');
const V = JSON.parse(fs.readFileSync(path.join(B, 'audio/vo/lines.json'), 'utf8'));
const KEY = { L1: {'rain.': 'k'}, L2: {'worry': 'k'}, L4: {'with.': 'g', 'With': 'g', 'it.': 'g'}, L5: {'still': 'k', 'raining:': 'k'}, L6: {'friend': 'k'}, L7: {'door': 'k'}, L8: {'support': 'k'} };
const css = `
@font-face{font-family:Poppins;font-weight:400;src:url('file://${B}/fonts/Poppins-Regular.ttf')}
@font-face{font-family:Poppins;font-weight:500;src:url('file://${B}/fonts/Poppins-Medium.ttf')}
@font-face{font-family:Poppins;font-weight:600;src:url('file://${B}/fonts/Poppins-SemiBold.ttf')}
@font-face{font-family:Poppins;font-weight:700;src:url('file://${B}/fonts/Poppins-Bold.ttf')}
@font-face{font-family:Hafs;src:url('file://${B}/fonts/UthmanicHafs1Ver18.woff2')}
html,body{margin:0;width:1080px;height:1920px;background:transparent;overflow:hidden}
.cap{position:absolute;left:60px;right:120px;top:1040px;font-family:Poppins;font-weight:600;color:#fff;font-size:58px;line-height:1.22;text-shadow:0 2px 18px rgba(0,0,0,.7),0 0 4px rgba(0,0,0,.5)}
.k{color:#7fd6cf}.g{color:#e9b45a}.h{visibility:hidden}
.ar{font-family:Hafs;direction:rtl;color:#f4ece2;text-align:center}
`;
const page = (body) => `<!doctype html><meta charset="utf-8"><style>${css}</style>${body}`;
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  const shot = async (name, body) => {
    const tmp = path.join(B, 'overlays', '_' + name + '.html');
    fs.writeFileSync(tmp, page(body));
    await p.goto('file://' + tmp, { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    await p.screenshot({ path: path.join(B, 'overlays', name + '.png'), omitBackground: true });
  };
  for (const L of ['L1', 'L2', 'L4', 'L5', 'L6', 'L7', 'L8']) {
    const words = V[L].words.map(w => w.w);
    for (let k = 1; k <= words.length; k++) {
      const html = words.map((w, i) => {
        const cls = [(KEY[L] || {})[w] || '', i >= k ? 'h' : ''].join(' ').trim();
        return cls ? `<span class="${cls}">${w}</span>` : w;
      }).join(' ');
      await shot(`cap_${L}_${k}`, `<div class="cap">${html}</div>`);
    }
    console.log('caps', L, words.length);
  }
  await shot('verse_ar', '<div class="ar" style="position:absolute;left:60px;right:60px;top:560px;font-size:84px;line-height:1.75;text-shadow:0 2px 24px rgba(0,0,0,.6)">فَإِنَّ مَعَ ٱلۡعُسۡرِ يُسۡرًا ٥<br>إِنَّ مَعَ ٱلۡعُسۡرِ يُسۡرٗا ٦</div>');
  await shot('verse_tr', '<div style="position:absolute;left:90px;right:90px;top:960px;text-align:center;font-family:Poppins;font-weight:500;font-size:44px;line-height:1.35;color:#f2ede4;text-shadow:0 2px 16px rgba(0,0,0,.6)">“For indeed, with hardship [will be] ease. Indeed, with hardship [will be] ease.”</div><div style="position:absolute;left:0;right:0;top:1150px;text-align:center;font-family:Poppins;font-weight:600;font-size:28px;letter-spacing:.12em;color:#e9b45a">ASH-SHARH 94:5–6</div>');
  await shot('with_ar', '<div class="ar" style="position:absolute;left:0;right:0;top:380px;font-size:200px;color:#e9b45a;text-shadow:0 4px 40px rgba(0,0,0,.55)">مَعَ</div><div style="position:absolute;left:0;right:0;top:880px;text-align:center;font-family:Poppins;font-weight:600;font-size:40px;letter-spacing:.25em;color:#f2d79e">WITH</div>');
  await shot('end_bg', '<div style="position:absolute;inset:0;background:#122F2A"></div><div style="position:absolute;left:0;right:0;bottom:0;height:22px;display:flex"><span style="flex:1;background:#DB225E"></span><span style="flex:1;background:#09999C"></span><span style="flex:1;background:#F26721"></span><span style="flex:1;background:#76BF43"></span></div>');
  await shot('end_logo', `<img src="file://${B}/logo_white_4x.png" style="position:absolute;left:240px;top:330px;width:600px">`);
  await shot('end_title', '<div style="position:absolute;left:60px;right:60px;top:690px;text-align:center;font-family:Poppins;font-weight:700;font-size:64px;line-height:1.15;color:#fff">Imam Counselling<br>at BMHC</div>');
  await shot('end_details', '<div style="position:absolute;left:60px;right:60px;top:880px;text-align:center;font-family:Poppins;font-weight:500;font-size:36px;line-height:1.5;color:#d9e5e0">Confidential · 0161 881 8062 (opening hours)<br><span style="color:#7fd6cf;font-weight:600">bmhc.org.uk/imam-counselling</span></div>');
  await shot('end_crisis', '<div style="position:absolute;left:90px;right:90px;top:1060px;text-align:center;font-family:Poppins;font-weight:400;font-size:28px;line-height:1.45;color:rgba(255,255,255,.82)">Need to talk? Samaritans, free, day or night: 116 123.<br>Urgent mental health help: NHS 111, mental health option.<br>Emergency: 999.</div>');
  await shot('end_ai', '<div style="position:absolute;left:0;right:0;top:1215px;text-align:center;font-family:Poppins;font-size:21px;color:rgba(255,255,255,.55)">Stock footage · the building is from our own photos</div>');
  await b.close();
  console.log('done');
})();
