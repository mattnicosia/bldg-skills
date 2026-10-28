// Proposal PDF button (kit v1.8): top right on desktop over the photo and on the white nav, in the menu on a phone,
// downloads the PDF from the Netlify build, and inside an artifact hands the file to the downloads capability.
//   node pdf_check.mjs <outdir>
import fs from 'node:fs'; import path from 'node:path'; import http from 'node:http'; import { fileURLToPath } from 'node:url';
const HERE_ = path.dirname(fileURLToPath(import.meta.url));
const KIT_ = process.env.MCC_KIT || path.resolve(HERE_, '..', '..', 'kit');
const { chromium } = await import(path.join(KIT_, 'node_modules', 'playwright-core', 'index.mjs'));
const CHROME_ = process.env.CHROME || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
const out = path.resolve(process.argv[2] || 'checks_pdf'); fs.mkdirSync(out, { recursive: true });
const ROOT = path.join(HERE_, 'netlify');
const types = { '.html': 'text/html', '.js': 'text/javascript', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.png': 'image/png', '.pdf': 'application/pdf' };
const srv = http.createServer((q, r) => { const u = decodeURIComponent(q.url.split('?')[0]); const f = path.join(ROOT, u === '/' ? 'index.html' : u);
  fs.readFile(f, (e, b) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { 'content-type': types[path.extname(f)] || 'application/octet-stream' }); r.end(b); }); }).listen(4683);
const b = await chromium.launch({ executablePath: CHROME_ });
const fails = []; const want = (ok, m) => { if (!ok) fails.push(m); console.log((ok ? 'ok   ' : 'FAIL ') + m); };
const pdfName = fs.readdirSync(path.join(ROOT, 'assets')).find((f) => f.endsWith('.pdf'));
const pdfSize = fs.statSync(path.join(ROOT, 'assets', pdfName)).size;
for (const [name, vp] of [['desktop', { width: 1440, height: 900 }], ['laptop', { width: 1200, height: 800 }], ['tablet', { width: 900, height: 1000 }], ['phone', { width: 390, height: 844 }]]) {
  const ctx = await b.newContext({ viewport: vp, acceptDownloads: true, isMobile: name === 'phone', hasTouch: name === 'phone' }); const p = await ctx.newPage(); const errs = [];
  p.on('pageerror', (e) => errs.push(e.message));
  await p.goto('http://localhost:4683/', { waitUntil: 'load' }); await p.waitForTimeout(3200);
  const box = async () => p.$eval('.nav__pdf', (el) => { const r = el.getBoundingClientRect(), s = getComputedStyle(el); return { x: r.left, r: r.right, w: r.width, vis: s.display !== 'none' && r.width > 0 }; });
  const nb = await box();
  if (name === 'phone') {
    want(!nb.vis, `${name}: nav button hidden, the menu carries it`);
    await p.click('#menu-btn'); await p.waitForTimeout(900);
    await p.screenshot({ path: path.join(out, `${name}_menu.jpg`), type: 'jpeg', quality: 80 });
    const [d] = await Promise.all([p.waitForEvent('download'), p.click('.menu [data-pdf]')]);
    want(d.suggestedFilename() === pdfName, `${name}: menu button downloads ${d.suggestedFilename()}`);
  } else {
    want(nb.vis && nb.r <= vp.width - 20, `${name}: button top right (${Math.round(nb.x)} to ${Math.round(nb.r)} of ${vp.width})`);
    const links = await p.$eval('.nav__links', (el) => { const r = el.getBoundingClientRect(); return getComputedStyle(el).display === 'none' ? null : r.right; });
    if (links !== null) want(links < nb.x - 12, `${name}: clears the section links (${Math.round(links)} < ${Math.round(nb.x)})`);
    await p.screenshot({ path: path.join(out, `${name}_hero.jpg`), type: 'jpeg', quality: 80, clip: { x: 0, y: 0, width: vp.width, height: 90 } });
    await p.evaluate(() => window.scrollTo(0, innerHeight * 2)); await p.waitForTimeout(900);
    const solid = await p.$eval('#nav', (el) => el.classList.contains('solid'));
    await p.screenshot({ path: path.join(out, `${name}_solid.jpg`), type: 'jpeg', quality: 80, clip: { x: 0, y: 0, width: vp.width, height: 90 } });
    const col = await p.$eval('.nav__pdf', (el) => getComputedStyle(el).color);
    want(solid && /0, 40, 204|0, 26, 138/.test(col), `${name}: navy on the white nav (${col})`);
    const [d] = await Promise.all([p.waitForEvent('download'), p.click('.nav__pdf')]);
    const fp = path.join(out, `${name}.pdf`); await d.saveAs(fp);
    want(d.suggestedFilename() === pdfName && fs.statSync(fp).size === pdfSize, `${name}: downloads ${d.suggestedFilename()} (${fs.statSync(fp).size} bytes)`);
  }
  want(errs.length === 0, `${name}: no page errors ${errs.join(' | ')}`);
  await ctx.close();
}
{ // inside a claude.ai artifact: the click hands the PDF to downloads.save instead of following the link
  const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } }); const p = await ctx.newPage();
  await p.addInitScript(() => { window.__saved = null; window.claude = { use: async (n) => n === 'downloads' ? { save: async (r) => { window.__saved = { filename: r.filename, size: r.data.size, type: r.data.constructor.name }; return { status: 'saved' }; } } : null }; });
  await p.goto('http://localhost:4683/', { waitUntil: 'load' }); await p.waitForTimeout(2500);
  await p.click('.nav__pdf'); await p.waitForTimeout(800);
  const s = await p.evaluate(() => window.__saved);
  want(s && s.filename === pdfName && s.size === pdfSize && s.type === 'Blob', `artifact: downloads.save got ${JSON.stringify(s)}`);
  await ctx.close();
}
await b.close(); srv.close();
console.log(fails.length ? `\n${fails.length} FAILED` : '\nall pdf checks pass'); process.exit(fails.length ? 1 : 0);
