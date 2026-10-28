// Selections check (kit v1.7): every view and both card modes on desktop and phone, the shared requests with the Alternates
// switches, the totals to the cent, and the send path (Netlify form, then the email fallback).
//   node selections_check.mjs <outdir>
import fs from 'node:fs'; import path from 'node:path'; import http from 'node:http'; import { fileURLToPath } from 'node:url';
const HERE_ = path.dirname(fileURLToPath(import.meta.url));
const KIT_ = process.env.MCC_KIT || path.resolve(HERE_, '..', '..', 'kit');
const { chromium } = await import(path.join(KIT_, 'node_modules', 'playwright-core', 'index.mjs'));
const CHROME_ = process.env.CHROME || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
const out = path.resolve(process.argv[2] || 'checks_selections'); fs.mkdirSync(out, { recursive: true });
const ROOT = process.env.WEB_ROOT || path.join(HERE_, 'netlify');
const types = { '.html': 'text/html', '.js': 'text/javascript', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.png': 'image/png', '.txt': 'text/plain' };
let posts = [], postOk = true;
const srv = http.createServer((q, r) => {
  if (q.method === 'POST') { let body = ''; q.on('data', (c) => { body += c; }); q.on('end', () => { posts.push(body); r.writeHead(postOk ? 200 : 404); r.end(); }); return; }
  const u = decodeURIComponent(q.url.split('?')[0]), f = path.join(ROOT, u === '/' ? 'index.html' : u);
  fs.readFile(f, (e, b) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { 'content-type': types[path.extname(f)] || 'application/octet-stream' }); r.end(b); });
}).listen(4679);
const b = await chromium.launch({ executablePath: CHROME_ });
const fails = [], log = (m) => console.log(m);
const want = (ok, m) => { if (!ok) fails.push(m); log((ok ? 'ok   ' : 'FAIL ') + m); };

async function run(name, vp) {
  const ctx = await b.newContext({ viewport: vp, deviceScaleFactor: 1, isMobile: name === 'phone', hasTouch: name === 'phone' });
  const p = await ctx.newPage(); const errs = [];
  p.on('pageerror', (e) => errs.push(e.message)); p.on('console', (m) => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto('http://localhost:4679/', { waitUntil: 'load' }); await p.waitForTimeout(3000);
  const go = async (sel) => { await p.evaluate((s) => { const el = document.querySelector(s); window.scrollTo(0, el.getBoundingClientRect().top + scrollY - 70); }, sel); await p.waitForTimeout(700); };
  const txt = (s) => p.$eval(s, (el) => el.textContent.trim());
  const shot = (n) => p.screenshot({ path: path.join(out, `${name}_${n}.jpg`), type: 'jpeg', quality: 80, fullPage: false });
  const shotEl = (n, s) => p.locator(s).screenshot({ path: path.join(out, `${name}_${n}.jpg`), type: 'jpeg', quality: 80 });
  await go('#selections');
  for (const v of ['out', 'in', 'site', 'list']) {
    await p.click(`.selx__pills .pill[data-view="${v}"]`); await p.waitForTimeout(500);
    await go(name === 'phone' ? '#sx-stage' : '.selx__grid');
    await shot('view_' + v);
    const pins = await p.$$eval('.sx-pin', (a) => a.length);
    want(v === 'list' ? pins === 0 : pins > 0, `${name} ${v}: ${pins} points`);
  }
  // options mode: the driveway, Tar and Chip, request it
  await p.click('.selx__pills .pill[data-view="site"]'); await p.click('.sx-pin[data-el="drive"]'); await p.click('.sx-tile[data-opt="tarchip"]');
  want((await txt('#sx-d')) === '+$39,330.00', `${name} tar and chip shows +$39,330.00`);
  want((await txt('#sx-t')) === '$2,663,635.54', `${name} tar and chip budget $2,663,635.54`);
  const stroke = await p.$eval('#sx-drive', (el) => el.getAttribute('stroke')); want(stroke === 'url(#sxp-tarchip)', `${name} site drive painted tar and chip (${stroke})`);
  await p.click('.sx-ask'); await p.waitForTimeout(200);
  want((await txt('#sx-req')) === '+$39,330.00', `${name} bar requested +$39,330.00`);
  await p.click('.sx-tile[data-opt="grid"]');
  const st2 = await p.$eval('#sx-drive', (el) => el.getAttribute('stroke')), sec2 = await p.$eval('#sx-sec', (el) => el.getAttribute('stroke'));
  want(st2 === 'url(#sxp-stone)' && sec2 === 'url(#sxp-grid)', `${name} grid pavers paint the steep section only`);
  await go('#sx-card'); await shotEl('card_options', '#sx-card');
  // rate mode: siding by the dial to $9.00 equals VE-5
  await p.click('.selx__pills .pill[data-view="out"]'); await p.click('.sx-pin[data-el="siding"]');
  await p.$eval('#sx-range', (el) => { el.value = '9'; el.dispatchEvent(new Event('input', { bubbles: true })); });
  want((await txt('#sx-d')) === '-$20,024.95', `${name} siding at $9.00 is -$20,024.95 (VE-5)`);
  await go('#sx-card'); await shotEl('card_rate', '#sx-card');
  // the EPDM roof swaps the outside render
  await p.click('.sx-pin[data-el="roof"]'); await p.click('.sx-tile[data-opt="epdm"]');
  const src = await p.$eval('.sx-view[data-view="out"] img', (el) => el.getAttribute('src')); want(/out_epdm/.test(src), `${name} EPDM swaps the outside render (${src})`);
  // the Alternates switch for VE-2 is the same request as the roof card
  await go('#alternates');
  await p.click('.tog[data-id="ve2"]'); await p.waitForTimeout(200);
  want((await p.$eval('.tog[data-id="ve2"]', (el) => el.getAttribute('aria-checked'))) === 'true', `${name} VE-2 switch on`);
  want((await txt('#alt-add')) === '-$16,387.50', `${name} alternates total -$16,387.50 (39,330.00 - 55,717.50) got ${await txt('#alt-add')}`);
  await p.click('.tog[data-id="13"]'); await p.waitForTimeout(200);   // millings replace tar and chip: one driveway at a time
  want((await p.$eval('.tog[data-id="12"]', (el) => el.getAttribute('aria-checked'))) === 'false', `${name} Alt 12 off once Alt 13 is on`);
  want((await txt('#alt-add')) === '-$46,657.80', `${name} alternates total -$46,657.80 (9,059.70 - 55,717.50) got ${await txt('#alt-add')}`);
  await go('#selections'); await p.click('.selx__pills .pill[data-view="list"]'); await p.waitForTimeout(300);
  await go(name === 'phone' ? '#sx-stage' : '.selx__grid'); await shot('list_with_requests');
  // send: Netlify form accepted
  posts = []; postOk = true;
  await go('#selections'); await p.click('#sx-send'); await p.waitForTimeout(300);
  await p.fill('#sxs-form input[name=name]', 'Check Run'); await p.fill('#sxs-form input[name=email]', 'check@example.com');
  await shot('send_sheet');
  await p.click('#sxs-form button[type=submit]'); await p.waitForTimeout(600);
  const body = new URLSearchParams(posts[0] || '');
  want(body.get('form-name') === 'selections' && /Driveway Surface: Millings/.test(body.get('requests') || '') && /Green Roof: EPDM Only/.test(body.get('requests') || ''), `${name} form posted with the requests`);
  want(/Sent to Montana/.test(await txt('#sxs-done')), `${name} sent message`);
  await p.click('.sxs__x');
  // send: refused, so the email fallback
  const nErr = errs.length; postOk = false; await p.click('#sx-send'); await p.fill('#sxs-form input[name=name]', 'Check Run'); await p.click('#sxs-form button[type=submit]'); await p.waitForTimeout(600);
  const href = await p.$eval('#sxs-done a', (a) => a.getAttribute('href')).catch(() => ''); want(href.startsWith('mailto:m.nicosia@montanacontracting.com'), `${name} email fallback`);
  await p.click('.sxs__x'); errs.splice(nErr, errs.length - nErr, ...errs.slice(nErr).filter((e) => !/status of 404/.test(e)));   // the refused send is meant to 404
  // saved on this device
  await p.reload({ waitUntil: 'load' }); await p.waitForTimeout(2500);
  want((await txt('#sx-req')) === '-$46,657.80', `${name} requests kept after reload`);
  const ow = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth); want(ow <= 0, `${name} no sideways overflow (${ow})`);
  want(errs.length === 0, `${name} no page errors ${errs.join(' | ')}`);
  await ctx.close();
}
await run('desktop', { width: 1440, height: 900 });
await run('laptop', { width: 1180, height: 800 });
await run('phone', { width: 390, height: 844 });
{ // the Artifact preview has no mcc-send meta (only netlify/index.html carries it), so it emails and posts nothing.
  // Tested on netlify/ with the meta removed: a local site/index.html opens in quirks mode, where the sheet does not lay out.
  const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } }); const p = await ctx.newPage();
  await p.goto('http://localhost:4679/', { waitUntil: 'load' }); await p.waitForTimeout(2000); posts = []; postOk = true;
  await p.evaluate(() => document.querySelector('meta[name="mcc-send"]').remove());
  await p.$eval('.tog[data-id="11"]', (el) => el.click()); await p.$eval('#alt-send', (el) => el.click()); await p.waitForTimeout(300);
  await p.fill('#sxs-form input[name=name]', 'Preview'); await p.click('#sxs-form button[type=submit]'); await p.waitForTimeout(400);
  const href = await p.$eval('#sxs-done a', (a) => a.getAttribute('href')).catch(() => '');
  want(posts.length === 0 && href.startsWith('mailto:'), `preview build emails instead of posting (posts ${posts.length})`);
  const site = fs.readFileSync(path.join(HERE_, 'site', 'index.html'), 'utf8'), net = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8');
  want(!/<meta name="mcc-send"/.test(site) && /<meta name="mcc-send"/.test(net), 'only the Netlify build carries the send meta');
  await ctx.close();
}
await b.close(); srv.close();
console.log(fails.length ? `\n${fails.length} FAILED` : '\nall selections checks pass');
process.exit(fails.length ? 1 : 0);
