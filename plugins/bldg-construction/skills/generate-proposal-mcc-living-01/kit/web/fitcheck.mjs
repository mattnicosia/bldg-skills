// Stage fit check at several window sizes: does any line of copy cross the drawn model, and does copy run off the screen?
import fs from 'node:fs'; import path from 'node:path'; import http from 'node:http'; import { fileURLToPath } from 'node:url';
const HERE_ = path.dirname(fileURLToPath(import.meta.url));
const KIT_ = process.env.MCC_KIT || path.resolve(HERE_, '..', '..', 'kit');
const { chromium } = await import(path.join(KIT_, 'node_modules', 'playwright-core', 'index.mjs'));
const CHROME_ = process.env.CHROME || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
const out = process.argv[2]; fs.mkdirSync(out, { recursive: true });
const ROOT = process.env.WEB_ROOT || path.join(HERE_, 'netlify');
const LENIS = path.join(KIT_, 'vendor', 'lenis', 'lenis.min.js');
const T = { '.html': 'text/html', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.png': 'image/png' };
const srv = http.createServer((q, r) => { const u = decodeURIComponent(q.url.split('?')[0]); const f = path.join(ROOT, u === '/' ? 'index.html' : u); fs.readFile(f, (e, b) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { 'content-type': T[path.extname(f)] || 'application/octet-stream' }); r.end(b); }); }).listen(4679);
const b = await chromium.launch({ executablePath: CHROME_ });
const sizes = [[1280, 600], [1300, 650], [1366, 768], [1440, 900], [1920, 1080], [1024, 700], [390, 844], [375, 667]];
const steps = [0, 1, 2, 4, 9, 10, 11, 12, 16, 21];   // whole property: 22 steps, Barn then Pool House
const report = [];
for (const [w, h] of sizes) {
  const ctx = await b.newContext({ viewport: { width: w, height: h }, isMobile: w < 500, hasTouch: w < 500 });
  const p = await ctx.newPage();
  await p.route('**/lenis.min.js', (r) => r.fulfill({ path: LENIS, contentType: 'text/javascript' }));
  await p.goto('http://localhost:4679/'); await p.waitForTimeout(3800);
  for (const k of steps) {
    await p.evaluate((kk) => { const s = document.getElementById('stage'); window.scrollTo(0, s.getBoundingClientRect().top + scrollY + (s.offsetHeight - innerHeight) * ((kk + 0.5) / JSON.parse(document.getElementById('cb-data').textContent).steps.length)); }, k);
    await p.waitForTimeout(1500);
    const r = await p.evaluate(() => {
      const fr = document.querySelector('.frame').getBoundingClientRect();
      const m = { l: fr.left + fr.width * 0.04, t: fr.top + fr.height * 0.04, r: fr.right - fr.width * 0.04, b: fr.bottom - fr.height * 0.04 };   // drawn model plus land block
      const bad = [];
      document.querySelectorAll('.stage__copy .w > span, .sc-fig:not(.hide) .odo, .elist:not(.hide) button, .elist:not(.hide) .elist__tot').forEach((el) => {
        const x = el.getBoundingClientRect(); if (!x.width) return;
        const hitModel = innerWidth > 760 && x.right > m.l + 4 && x.left < m.r && x.bottom > m.t && x.top < m.b;
        const off = x.right > innerWidth - 4 || x.bottom > innerHeight - 2 || x.left < 0;
        const rail = document.querySelector('.stage__rail').getBoundingClientRect();
        const hitRail = x.bottom > rail.top + 2 && x.top < rail.bottom && x.right > rail.left && x.left < rail.right;
        if (hitModel || off || hitRail) bad.push((hitModel ? 'model ' : '') + (off ? 'offscreen ' : '') + (hitRail ? 'rail ' : '') + (el.textContent || '').trim().slice(0, 18));
      });
      return { title: document.querySelector('.sc-title').textContent.trim(), bad: [...new Set(bad)].slice(0, 6) };
    });
    if (r.bad.length) report.push(`${w}x${h} ${r.title}: ${r.bad.join(' | ')}`);
    if ((w === 1300 || w === 1280 || w === 390) && (k === 0 || k === 4 || k === 10 || k === 16 || k === 21)) await p.screenshot({ path: `${out}/${w}x${h}_s${k}.jpg`, type: 'jpeg', quality: 76 });
  }
  await p.evaluate(() => document.getElementById('budget').scrollIntoView()); await p.waitForTimeout(2200);
  const clip = await p.evaluate(() => { const o = document.getElementById('budget-odo').getBoundingClientRect(); const wr = document.querySelector('#budget .wrap').getBoundingClientRect(); return o.right > Math.min(innerWidth, wr.right) + 2 ? 'budget figure runs past the column by ' + Math.round(o.right - Math.min(innerWidth, wr.right)) : ''; });
  if (clip) report.push(`${w}x${h} ${clip}`);
  if (w === 1300) await p.screenshot({ path: `${out}/${w}x${h}_budget.jpg`, type: 'jpeg', quality: 76 });
  await ctx.close();
}
await b.close(); srv.close();
console.log(report.length ? report.join('\n') : 'all sizes clean');
