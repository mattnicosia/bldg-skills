// Grow a set of trees with EZ-Tree (vendor/ez-tree, MIT) in a headless browser and export them as one GLB.
//   node tools/make_trees.mjs [out.glb]
// Each tree is a node named "tree|<preset>|<seed>|<bark>|<leaf>" with a bark mesh and a leaf mesh.
// Materials are plain and named bark_<type> / leaf_<type>; the Blender scripts put the real textures on.
import { chromium } from 'playwright-core';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const KIT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const out = path.resolve(process.argv[2] || path.join(KIT, 'assets/trees/ez_trees.glb'));
const SPECS = [
  ['Oak Large', 11], ['Oak Large', 23], ['Oak Large', 37], ['Oak Medium', 5], ['Oak Medium', 41],
  ['Ash Large', 3], ['Ash Large', 17], ['Ash Medium', 29],
  ['Pine Large', 7], ['Pine Large', 19], ['Pine Medium', 13],
  ['Bush 1', 2], ['Bush 2', 4], ['Bush 3', 6],
];
const root = path.parse(KIT).root;
const html = `<!doctype html><meta charset="utf-8"><script type="importmap">${JSON.stringify({ imports: { three: path.join(KIT, 'node_modules/three/build/three.module.js'), 'three/addons/': path.join(KIT, 'node_modules/three/examples/jsm/') + '/' } })}</script>
<script type="module">
import * as THREE from 'three';
import { GLTFExporter } from 'three/addons/exporters/GLTFExporter.js';
import { Tree } from '${path.join(KIT, 'vendor/ez-tree/ez-tree.es.js')}';
try {
  const scene = new THREE.Group(); let tris = 0;
  const clean = (g) => { for (const a of Object.keys(g.attributes)) if (!['position', 'normal', 'uv'].includes(a)) g.deleteAttribute(a); return g; };
  for (const [preset, seed] of ${JSON.stringify(SPECS)}) {
    const t = new Tree(); t.loadPreset(preset); t.options.seed = seed; t.generate();
    const bark = t.options.bark.type, leaf = t.options.leaves.type;
    const g = new THREE.Group(); g.name = ['tree', preset, seed, bark, leaf].join('|');
    const b = new THREE.Mesh(clean(t.branchesMesh.geometry.clone()), new THREE.MeshStandardMaterial({ name: 'bark_' + bark })); b.name = 'bark';
    const l = new THREE.Mesh(clean(t.leavesMesh.geometry.clone()), new THREE.MeshStandardMaterial({ name: 'leaf_' + leaf, side: THREE.DoubleSide })); l.name = 'leaves';
    g.add(b, l); scene.add(g);
    tris += (b.geometry.index ? b.geometry.index.count : b.geometry.attributes.position.count) / 3 + (l.geometry.index ? l.geometry.index.count : l.geometry.attributes.position.count) / 3;
  }
  const buf = await new GLTFExporter().parseAsync(scene, { binary: true });
  const u = new Uint8Array(buf); let s = ''; for (let i = 0; i < u.length; i += 0x8000) s += String.fromCharCode.apply(null, u.subarray(i, i + 0x8000));
  window.__out = { b64: btoa(s), tris };
} catch (e) { window.__out = { error: String(e && e.stack || e) }; }
</script>`;
const srv = http.createServer((q, r) => {
  if (q.url === '/__make') { r.writeHead(200, { 'content-type': 'text/html' }); r.end(html); return; }
  const f = path.join(root, decodeURIComponent(q.url.split('?')[0]));
  fs.readFile(f, (e, b) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { 'content-type': f.endsWith('.js') || f.endsWith('.mjs') ? 'text/javascript' : 'application/octet-stream' }); r.end(b); });
}).listen(4612);
const exe = ['/opt/pw-browsers/chromium-1194/chrome-linux/chrome', process.env.CHROME].find((p) => p && fs.existsSync(p));
const br = await chromium.launch({ executablePath: exe });
const pg = await br.newPage(); const logs = [];
pg.on('console', (m) => logs.push(m.text())); pg.on('pageerror', (e) => logs.push(e.message));
await pg.goto('http://localhost:4612/__make');
await pg.waitForFunction('window.__out', null, { timeout: 300000 }).catch(() => {});
const o = await pg.evaluate(() => window.__out);
await br.close(); srv.close();
if (!o || o.error) { console.error('trees failed', o?.error || logs.join('\n')); process.exit(1); }
fs.mkdirSync(path.dirname(out), { recursive: true });
fs.writeFileSync(out, Buffer.from(o.b64, 'base64'));
console.log(`wrote ${out} ${(fs.statSync(out).size / 1e6).toFixed(1)} MB · ${SPECS.length} trees · ${Math.round(o.tris).toLocaleString()} triangles`);
