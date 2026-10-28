// Marker style review: the four focus styles on two element steps, plus the all step on a phone.
import fs from 'node:fs'; import path from 'node:path'; import http from 'node:http'; import { fileURLToPath } from 'node:url';
const HERE_ = path.dirname(fileURLToPath(import.meta.url));
const KIT_ = process.env.MCC_KIT || path.resolve(HERE_, '..', '..', 'kit');
const { chromium } = await import(path.join(KIT_, 'node_modules', 'playwright-core', 'index.mjs'));
const CHROME_ = process.env.CHROME || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
const out = process.argv[2]; fs.mkdirSync(out, { recursive: true });
const ROOT = process.env.WEB_ROOT || path.join(HERE_, 'netlify');
const LENIS = path.join(KIT_, 'vendor', 'lenis', 'lenis.min.js');
const T = { '.html': 'text/html', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.png': 'image/png' };
const srv = http.createServer((q, r) => { const u = decodeURIComponent(q.url.split('?')[0]); const f = path.join(ROOT, u === '/' ? 'index.html' : u); fs.readFile(f, (e, b) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { 'content-type': T[path.extname(f)] || 'application/octet-stream' }); r.end(b); }); }).listen(4683);
const b = await chromium.launch({ executablePath: CHROME_ });
const go = async (p, k) => { await p.evaluate((kk) => { const s = document.getElementById('stage'); window.scrollTo(0, s.getBoundingClientRect().top + scrollY + (s.offsetHeight - innerHeight) * ((kk + 0.5) / 11)); }, k); await p.waitForTimeout(1600); };
for (const st of ['brackets', 'dot', 'leader', 'badge']) {
  const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } }); const p = await ctx.newPage();
  await p.route('**/lenis.min.js', (r) => r.fulfill({ path: LENIS, contentType: 'text/javascript' }));
  await p.goto('http://localhost:4683/#mk-' + st); await p.waitForTimeout(3600);
  for (const k of [4, 6]) { await go(p, k); await p.screenshot({ path: `${out}/${st}_${k}.jpg`, type: 'jpeg', quality: 82 }); }
  await ctx.close();
}
const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true }); const p = await ctx.newPage();
await p.route('**/lenis.min.js', (r) => r.fulfill({ path: LENIS, contentType: 'text/javascript' }));
await p.goto('http://localhost:4683/'); await p.waitForTimeout(3600); await go(p, 10); await p.screenshot({ path: `${out}/phone_all.jpg`, type: 'jpeg', quality: 82 });
await b.close(); srv.close(); console.log('ok');
