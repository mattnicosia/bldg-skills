// Build a project's model/build.js in a headless browser and export it as a GLB.
//   node tools/make_glb.mjs <project_dir> [out.glb] [model/build.js]
// model/build.js exports a default function that returns a THREE.Group (see tools/glb/parts.js).
import { chromium } from 'playwright-core';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const KIT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const proj = path.resolve(process.argv[2]);
const out = path.resolve(process.argv[3] || path.join(proj, 'model.glb'));
const src = process.argv[4] ? path.resolve(process.argv[4]) : path.join(proj, 'model/build.js');   // optional: another build file, e.g. one with element tags
const root = path.parse(KIT).root;
const html = `<!doctype html><meta charset="utf-8"><script type="importmap">${JSON.stringify({ imports: { three: path.join(KIT, 'node_modules/three/build/three.module.js'), 'three/addons/': path.join(KIT, 'node_modules/three/examples/jsm/') + '/' } })}</script>
<script type="module">
import * as THREE from 'three';
import { GLTFExporter } from 'three/addons/exporters/GLTFExporter.js';
import build from '${src}';
try {
  const g = build();
  let tris = 0, meshes = 0; g.traverse((m) => { if (m.isMesh) { meshes++; tris += m.geometry.attributes.position.count / 3; } });
  const buf = await new GLTFExporter().parseAsync(g, { binary: true });
  const b = new Uint8Array(buf); let s = ''; for (let i = 0; i < b.length; i += 0x8000) s += String.fromCharCode.apply(null, b.subarray(i, i + 0x8000));
  window.__out = { b64: btoa(s), tris, meshes };
} catch (e) { window.__out = { error: String(e && e.stack || e) }; }
</script>`;
const srv = http.createServer((q, r) => {
  if (q.url === '/__make') { r.writeHead(200, { 'content-type': 'text/html' }); r.end(html); return; }
  const f = path.join(root, decodeURIComponent(q.url.split('?')[0]));
  fs.readFile(f, (e, b) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { 'content-type': f.endsWith('.js') || f.endsWith('.mjs') ? 'text/javascript' : 'application/octet-stream' }); r.end(b); });
}).listen(4611);
const exe = ['/opt/pw-browsers/chromium-1194/chrome-linux/chrome', process.env.CHROME].find((p) => p && fs.existsSync(p));
const b = await chromium.launch({ executablePath: exe });
const pg = await b.newPage(); const logs = [];
pg.on('console', (m) => logs.push(m.text())); pg.on('pageerror', (e) => logs.push(e.message));
await pg.goto('http://localhost:4611/__make');
await pg.waitForFunction('window.__out', null, { timeout: 120000 }).catch(() => {});
const o = await pg.evaluate(() => window.__out);
await b.close(); srv.close();
if (!o || o.error) { console.error('build failed', o?.error || logs.join('\n')); process.exit(1); }
fs.writeFileSync(out, Buffer.from(o.b64, 'base64'));
console.log(`wrote ${out} ${(fs.statSync(out).size / 1e6).toFixed(2)} MB · ${o.meshes} meshes · ${Math.round(o.tris).toLocaleString()} triangles`);
