// Render the model from exact camera poses with the page chrome hidden, for side by side review.
//   node tools/pose.mjs <project_dir> <out_dir> '<json [{name,pos,look,fov,p}]>' [WxH]
import { chromium } from 'playwright-core';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const [proj, outDir, spec, size = '1600x900'] = process.argv.slice(2);
const [W, H] = size.split('x').map(Number);
fs.mkdirSync(outDir, { recursive: true });
const srv = http.createServer((q, r) => { const f = decodeURIComponent(q.url.split('?')[0]); fs.readFile(f, (e, b) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { 'content-type': f.endsWith('.html') ? 'text/html' : f.endsWith('.js') ? 'text/javascript' : 'application/octet-stream' }); r.end(b); }); }).listen(4613);
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const pg = await b.newPage({ viewport: { width: W, height: H } });
pg.on('pageerror', (e) => console.log('ERR', e.message));
await pg.goto('http://localhost:4613' + path.resolve(proj, 'out/local.html'));
await pg.waitForFunction('window.__done === true', null, { timeout: 180000 });
await pg.addStyleTag({ content: 'body > *:not(#world){display:none!important}' });
for (const v of JSON.parse(spec)) {
  await pg.evaluate((v) => { window.__pose = v.pos ? v : null; const p = v.p ?? 0; window.__jump(p); window.__wake && window.__wake(); }, v);
  await pg.waitForTimeout(+(process.env.WAIT || 6000));
  await pg.screenshot({ path: path.join(outDir, v.name + '.png'), timeout: 170000 });
  console.log('shot', v.name);
}
await b.close(); srv.close();
