// Local screenshots of the v5 presentation at set scroll points, desktop and phone.
//   node shoot.mjs <outdir> [desktop|phone|both]
import fs from 'node:fs'; import path from 'node:path'; import http from 'node:http'; import { fileURLToPath } from 'node:url';
const HERE_ = path.dirname(fileURLToPath(import.meta.url));
const KIT_ = process.env.MCC_KIT || path.resolve(HERE_, '..', '..', 'kit');
const { chromium } = await import(path.join(KIT_, 'node_modules', 'playwright-core', 'index.mjs'));
const CHROME_ = process.env.CHROME || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';

const _o = String(process.argv[2] || ''); if (/(^|[\\/])(site|netlify)([\\/]|$)/.test(_o)) { console.error('screenshot folder must be outside site/ and netlify/ (kit v1.16)'); process.exit(2); }
const out = path.resolve(process.argv[2] || 'shots'); fs.mkdirSync(out, { recursive: true });
const which = process.argv[3] || 'both';
const ROOT = process.env.WEB_ROOT || path.join(HERE_, 'netlify');
const LENIS = path.join(KIT_, 'vendor', 'lenis', 'lenis.min.js');
const types = { '.html': 'text/html', '.js': 'text/javascript', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.png': 'image/png', '.txt': 'text/plain' };
const srv = http.createServer((q, r) => {
  const f = path.join(ROOT, decodeURIComponent(q.url.split('?')[0]) === '/' ? 'index.html' : decodeURIComponent(q.url.split('?')[0]));
  fs.readFile(f, (e, b) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { 'content-type': types[path.extname(f)] || 'application/octet-stream' }); r.end(b); });
}).listen(4677);
const b = await chromium.launch({ executablePath: CHROME_, args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] });
const errs = [];
async function run(name, vp, points) {
  const ctx = await b.newContext({ viewport: vp, deviceScaleFactor: 1, isMobile: name === 'phone', hasTouch: name === 'phone' });
  const p = await ctx.newPage();
  p.on('console', (m) => { if (m.type() === 'error' || m.type() === 'warning') errs.push(`${name}: ${m.text()}`); });
  p.on('pageerror', (e) => errs.push(`${name} pageerror: ${e.message}`));
  await p.route('**/lenis.min.js', (r) => r.fulfill({ path: LENIS, contentType: 'text/javascript' }));
  await p.goto('http://localhost:4677/', { waitUntil: 'load' });
  await p.waitForTimeout(4200);
  for (const [label, target] of points) {
    const y = await p.evaluate((t) => {
      const vh = innerHeight;
      if (typeof t === 'number') return t * vh;
      const [sel, frac] = t.split('@');
      const el = document.querySelector(sel); if (!el) return 0;
      const top = el.getBoundingClientRect().top + scrollY;
      if (frac === undefined) return top;
      return top + (el.offsetHeight - vh) * parseFloat(frac);
    }, target);
    await p.evaluate((yy) => { window.scrollTo(0, yy); }, y);
    await p.waitForTimeout(1900);
    await p.screenshot({ path: path.join(out, `${name}_${label}.jpg`), type: 'jpeg', quality: 78 });
  }
  const over = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth);
  if (over > 0) errs.push(`${name}: page scrolls sideways by ${over}px`);
  await ctx.close();
}
const N = Number(process.env.STEPS || 11);   // one design step per scroll slot
const stagePts = (k) => ['#stage@' + ((k + 0.45) / N).toFixed(4)];
const ONLY = process.env.ONLY;   // 'stage' for the design steps alone
const st = Array.from({ length: N }, (_, k) => ['s' + String(k).padStart(2, '0'), stagePts(k)[0]]);
const rest = [['00_entry', 0], ['01_entry_scrolled', 0.5], ['02_intro', '#project'], ['02b_intro', 1.6], ['03_gallery_a', '#gallery@0.05'], ['04_gallery_b', '#gallery@0.7'],
  ['13_budget', '#budget'], ['14_budget_b', '.pills'], ['15_budget_c', '.btot'], ['16_allow', '#allowances'], ['16b_allow', '.aled@0.6'], ['16c_rates', '.arate'], ['17_alts', '#alternates'], ['18_notes', '#notes'],
  ['19_sched', '#schedule@0.1'], ['20_sched_b', '#schedule@0.6'], ['21_sched_c', '#schedule@0.95'],
  ['22_appr', '#approach'], ['23_tiers', '.yteam'], ['24_people', '.people'], ['25_osx', '.osx'], ['26_osx_b', '.osx__for'], ['27_walk', '#walk'], ['28_pcf', '#pre-construction'],
  ['29_dusk', '.dusk'], ['30_cta', '#contact']];
const ONLYP = process.env.PTS ? process.env.PTS.split(',') : null;
const pts0 = ONLY === 'stage' ? st : ONLY === 'rest' ? rest : [...rest.slice(0, 6), ...st, ...rest.slice(6)];
const pts = ONLYP ? pts0.filter((p) => ONLYP.includes(p[0])) : pts0;
if (which !== 'phone') await run('desktop', { width: 1440, height: 900 }, pts);
if (which !== 'desktop') await run('phone', { width: 390, height: 844 }, pts);
await b.close(); srv.close();
fs.writeFileSync(path.join(out, 'errors.txt'), errs.join('\n'));
console.log('done', errs.length ? errs.join('\n') : 'no errors');
