// v5.2 checks: budget totals block, line detail, pre-con card and its open, OS panel, dusk, close, nav.
import fs from 'node:fs'; import path from 'node:path'; import http from 'node:http'; import { fileURLToPath } from 'node:url';
const HERE_ = path.dirname(fileURLToPath(import.meta.url));
const KIT_ = process.env.MCC_KIT || path.resolve(HERE_, '..', '..', 'kit');
const { chromium } = await import(path.join(KIT_, 'node_modules', 'playwright-core', 'index.mjs'));
const CHROME_ = process.env.CHROME || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
const _o = String(process.argv[2] || ''); if (/(^|[\\/])(site|netlify)([\\/]|$)/.test(_o)) { console.error('screenshot folder must be outside site/ and netlify/ (kit v1.16)'); process.exit(2); }
const out = process.argv[2]; fs.mkdirSync(out, { recursive: true });
const ROOT = process.env.WEB_ROOT || path.join(HERE_, 'netlify');
const LENIS = path.join(KIT_, 'vendor', 'lenis', 'lenis.min.js');
const T = { '.html': 'text/html', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.png': 'image/png' };
const srv = http.createServer((q, r) => { const u = decodeURIComponent(q.url.split('?')[0]); const f = path.join(ROOT, u === '/' ? 'index.html' : u); fs.readFile(f, (e, b) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { 'content-type': T[path.extname(f)] || 'application/octet-stream' }); r.end(b); }); }).listen(4687);
const b = await chromium.launch({ executablePath: CHROME_ });
const log = [];
for (const [name, vp] of [['desktop', { width: 1440, height: 900 }], ['phone', { width: 390, height: 844 }]]) {
  const ctx = await b.newContext({ viewport: vp, isMobile: name === 'phone', hasTouch: name === 'phone' }); const p = await ctx.newPage();
  p.on('pageerror', (e) => log.push(name + ' pageerror ' + e.message));
  await p.route('**/lenis.min.js', (r) => r.fulfill({ path: LENIS, contentType: 'text/javascript' }));
  await p.goto('http://localhost:4687/'); await p.waitForTimeout(3600);
  const sh = (n) => p.screenshot({ path: `${out}/${name}_${n}.jpg`, type: 'jpeg', quality: 80 });
  await p.evaluate(() => window.scrollTo(0, innerHeight * 1.4)); await p.waitForTimeout(900); await sh('nav');
  await p.evaluate(() => document.querySelector('.pills').scrollIntoView({ block: 'start' })); await p.waitForTimeout(1200);
  await p.evaluate(() => document.querySelectorAll('.brows--el .brow__h')[0].click()); await p.waitForTimeout(900);
  await p.evaluate(() => window.scrollBy(0, -80)); await p.waitForTimeout(700); await sh('budget_open');
  await p.evaluate(() => document.querySelector('.btot').scrollIntoView({ block: 'center' })); await p.waitForTimeout(900); await sh('btot');
  await p.evaluate(() => document.querySelector('.pill[data-v="mf"]').click()); await p.waitForTimeout(900);
  await p.evaluate(() => { document.querySelectorAll('.brows--mf .brow__h')[7].click(); document.querySelectorAll('.brows--mf .brow__h')[7].scrollIntoView({ block: 'start' }); }); await p.waitForTimeout(900);
  await p.evaluate(() => window.scrollBy(0, -90)); await p.waitForTimeout(600); await sh('budget_mf_open');
  if (await p.evaluate(() => !!document.querySelector('.osx'))) { await p.evaluate(() => document.querySelector('.osx').scrollIntoView({ block: 'start' })); await p.waitForTimeout(1200); await sh('osx'); }   // kit v1.16: Montana OS is optional
  if (await p.evaluate(() => !!document.querySelector('[data-precon]'))) {   // kit v1.16: pre-construction is optional
  await p.evaluate(() => document.querySelector('.pcf').scrollIntoView({ block: 'center' })); await p.waitForTimeout(2600); await sh('pcf');
  await p.evaluate(() => document.querySelector('.pcf__card').click()); await p.waitForTimeout(330); await sh('pcf_opening');
  await p.waitForTimeout(1200); await sh('pcf_open');
  log.push(name + ' precon open from card: ' + await p.evaluate(() => document.getElementById('precon').classList.contains('open') + ' ' + document.querySelector('.pc__panel').classList.contains('from-card')));
  await p.keyboard.press('Escape'); await p.waitForTimeout(400); await sh('pcf_closing'); await p.waitForTimeout(900);
  } else log.push(name + ' precon card: section off');
  await p.evaluate(() => document.querySelector('.dusk').scrollIntoView({ block: 'start' })); await p.waitForTimeout(1500); await sh('dusk');
  await p.evaluate(() => document.getElementById('contact').scrollIntoView({ block: 'start' })); await p.waitForTimeout(1400); await sh('cta');
  log.push(name + ' sideways ' + await p.evaluate(() => document.documentElement.scrollWidth - innerWidth));
  await ctx.close();
}
await b.close(); srv.close(); console.log(log.join('\n'));
