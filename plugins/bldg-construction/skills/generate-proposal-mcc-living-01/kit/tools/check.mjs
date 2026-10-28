// Render check: screenshot every stop on desktop and phone, and report page errors.
//   node tools/check.mjs <project_dir> [desktop|phone|both] [stopId:fraction,...]
// Serves the kit folder on :4610, opens <project_dir>/out/local.html, writes <project_dir>/out/check/*.png.
// Look at every image before publishing.
import { chromium } from 'playwright-core';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const KIT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const proj = path.resolve(process.argv[2] || 'example');
const mode = process.argv[3] || 'both';
const only = process.argv[4];
const outDir = path.join(proj, 'out', 'check'); fs.mkdirSync(outDir, { recursive: true });
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.glb': 'model/gltf-binary' };
const root = path.parse(KIT).root;
const srv = http.createServer((q, r) => {
  const f = path.join(root, decodeURIComponent(q.url.split('?')[0]));
  fs.readFile(f, (e, b) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { 'content-type': TYPES[path.extname(f)] || 'application/octet-stream' }); r.end(b); });
}).listen(4610);
const exe = ['/opt/pw-browsers/chromium-1194/chrome-linux/chrome', process.env.CHROME].find((p) => p && fs.existsSync(p));
const b = await chromium.launch({ executablePath: exe, args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const sizes = { desktop: [1440, 900], narrow: [1113, 929], wide: [1920, 1080], phone: [390, 844] };
let errors = 0;
for (const m of mode === 'both' ? ['desktop', 'phone'] : [mode]) {
  const [W, H] = sizes[m];
  const pg = await b.newPage({ viewport: { width: W, height: H } });
  const logs = []; pg.on('console', (x) => { if (x.type() === 'error' && !/ERR_TUNNEL|ERR_NAME|favicon|status of 404/.test(x.text())) logs.push('console: ' + x.text()); }); pg.on('pageerror', (e) => logs.push('page error: ' + e.message));
  await pg.goto('http://localhost:4610' + path.join(proj, 'out', 'local.html'), { waitUntil: 'commit' });
  try { await pg.waitForFunction('window.__done === true', null, { timeout: 240000 }); } catch (e) { logs.push('TIMEOUT waiting for the first frame'); }
  await pg.addStyleTag({ content: '*,*::before,*::after{transition:none!important;animation-duration:0s!important;animation-delay:0s!important}' });
  const stops = await pg.evaluate(() => window.__stops || []);
  const specs = only ? only.split(',').map((s) => s.split(':')) : stops.map((s, i) => [s.id, i === 0 ? '0' : i === stops.length - 1 ? '1' : '.5']);
  for (const [id, f] of specs) {
    const s = stops.find((x) => x.id === id); if (!s) { logs.push('no stop ' + id); continue; }
    const p = Math.min(1, s.s0 + (s.s1 - s.s0) * +f);
    await pg.evaluate((p) => { const max = document.documentElement.scrollHeight - innerHeight; scrollTo(0, p * max); window.__jump(p); window.__wake && window.__wake(); }, p);
    await pg.waitForTimeout(+(process.env.WAIT || 3500));
    const file = path.join(outDir, `${m}_${String(stops.indexOf(s)).padStart(2, '0')}_${id}.png`);
    await pg.screenshot({ path: file, timeout: 170000 });
    console.log('shot', path.relative(proj, file));
  }
  if (logs.length) { errors += logs.length; console.log(m, 'ERRORS:\n  ' + logs.slice(0, 20).join('\n  ')); }
  await pg.close();
}
await b.close(); srv.close();
console.log(errors ? `${errors} errors` : 'no page errors');
process.exit(errors ? 1 : 0);
