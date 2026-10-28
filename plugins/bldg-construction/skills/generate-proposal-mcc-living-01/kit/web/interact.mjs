// Interaction checks: sheet, menu, alternates total, stage numbers.
import fs from 'node:fs'; import path from 'node:path'; import http from 'node:http'; import { fileURLToPath } from 'node:url';
const HERE_ = path.dirname(fileURLToPath(import.meta.url));
const KIT_ = process.env.MCC_KIT || path.resolve(HERE_, '..', '..', 'kit');
const { chromium } = await import(path.join(KIT_, 'node_modules', 'playwright-core', 'index.mjs'));
const CHROME_ = process.env.CHROME || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
const out = process.argv[2]; fs.mkdirSync(out, { recursive: true });
const ROOT = process.env.WEB_ROOT || path.join(HERE_, 'netlify');
const LENIS = path.join(KIT_, 'vendor', 'lenis', 'lenis.min.js');
const T = { '.html': 'text/html', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.png': 'image/png' };
const srv = http.createServer((q, r) => { const u = decodeURIComponent(q.url.split('?')[0]); const f = path.join(ROOT, u === '/' ? 'index.html' : u); fs.readFile(f, (e, b) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { 'content-type': T[path.extname(f)] || 'application/octet-stream' }); r.end(b); }); }).listen(4678);
const b = await chromium.launch({ executablePath: CHROME_ });
const log = [];
for (const [name, vp] of [['desktop', { width: 1440, height: 900 }], ['phone', { width: 390, height: 844 }]]) {
  const ctx = await b.newContext({ viewport: vp, isMobile: name === 'phone', hasTouch: name === 'phone' });
  const p = await ctx.newPage(); p.on('pageerror', (e) => log.push(name + ' pageerror ' + e.message));
  await p.route('**/lenis.min.js', (r) => r.fulfill({ path: LENIS, contentType: 'text/javascript' }));
  await p.goto('http://localhost:4678/'); await p.waitForTimeout(4000);
  if (name === 'phone') { await p.click('#menu-btn'); await p.waitForTimeout(900); await p.screenshot({ path: `${out}/${name}_menu.jpg`, quality: 78, type: 'jpeg' }); await p.click('.menu__close'); await p.waitForTimeout(900); }
  await p.evaluate(() => document.querySelector('[data-precon]').click()); await p.waitForTimeout(1200);
  await p.screenshot({ path: `${out}/${name}_pc1.jpg`, quality: 78, type: 'jpeg' });
  for (const [k, f] of [[2, 0.25], [3, 0.5], [4, 0.75], [5, 1]]) { await p.evaluate((ff) => { const q = document.querySelector('.pc__panel'); q.scrollTop = (q.scrollHeight - q.clientHeight) * ff; }, f); await p.waitForTimeout(900); await p.screenshot({ path: `${out}/${name}_pc${k}.jpg`, quality: 78, type: 'jpeg' }); }
  await p.keyboard.press('Escape'); await p.waitForTimeout(900);
  log.push(name + ' precon closed: ' + !(await p.evaluate(() => document.getElementById('precon').classList.contains('open'))));
  await p.evaluate(() => document.getElementById('budget').scrollIntoView()); await p.waitForTimeout(1600);
  await p.evaluate(() => document.querySelector('.pill[data-v="mf"]').click()); await p.waitForTimeout(1600);
  log.push(name + ' budget mf view: ' + await p.evaluate(() => document.querySelector('.bview').dataset.view + ' mfHidden=' + document.querySelector('.brows--mf').hidden + ' rows=' + document.querySelectorAll('.brows--mf .brow').length));
  await p.evaluate(() => document.querySelector('.pills').scrollIntoView({ block: 'start' })); await p.waitForTimeout(500);
  await p.evaluate(() => { const h = document.querySelector('.brows--mf .brow__h'); h.click(); }); await p.waitForTimeout(900);
  await p.screenshot({ path: `${out}/${name}_budget_mf_open.jpg`, quality: 78, type: 'jpeg' });
  await p.evaluate(() => document.querySelector('.pill[data-v="el"]').click()); await p.waitForTimeout(900);
  await p.evaluate(() => { const h = document.querySelectorAll('.brows--el .brow__h')[1]; h.click(); }); await p.waitForTimeout(900);
  await p.screenshot({ path: `${out}/${name}_budget_el_open.jpg`, quality: 78, type: 'jpeg' });
  await p.evaluate(() => document.getElementById('alternates').scrollIntoView()); await p.waitForTimeout(800);
  await p.evaluate(() => { const t = document.querySelectorAll('.tog'); t[0].click(); t[2].click(); }); await p.waitForTimeout(1800);
  log.push(name + ' alternates: ' + await p.evaluate(() => document.getElementById('alt-odo').getAttribute('aria-label') + ' add ' + document.getElementById('alt-add').textContent));
  await p.screenshot({ path: `${out}/${name}_alts_on.jpg`, quality: 78, type: 'jpeg' });
  const wk = [];
  for (const f of [0.05, 0.3, 0.55, 0.8, 0.98]) { await p.evaluate((ff) => { const s = document.getElementById('schedule'); window.scrollTo(0, s.getBoundingClientRect().top + scrollY + Math.max(0, s.offsetHeight - innerHeight) * ff); }, f); await p.waitForTimeout(900); wk.push(await p.evaluate(() => document.getElementById('week-odo').getAttribute('aria-label') + ' ' + document.getElementById('week-ph').textContent + (document.querySelector('.sched').classList.contains('nopin') ? ' (nopin)' : ''))); }
  log.push(name + ' schedule: ' + wk.join(' | '));
  const seq = [];
  for (let k = 0; k < 11; k++) {
    await p.evaluate((kk) => { const s = document.getElementById('stage'); const y = s.getBoundingClientRect().top + scrollY + (s.offsetHeight - innerHeight) * ((kk + 0.5) / 11); window.scrollTo(0, y); }, k);
    await p.waitForTimeout(700);
    seq.push(await p.evaluate(() => document.querySelector('.sc-title').textContent.trim() + ' ' + (document.querySelector('.sc-fig').classList.contains('hide') ? '-' : document.getElementById('stage-odo').getAttribute('aria-label'))));
  }
  log.push(name + ' stage: ' + seq.join(' | '));
  const over = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth); log.push(name + ' sideways overflow ' + over);
  await ctx.close();
}
await b.close(); srv.close(); console.log(log.join('\n'));
