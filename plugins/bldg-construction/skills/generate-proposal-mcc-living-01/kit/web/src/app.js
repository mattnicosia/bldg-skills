(() => {
  'use strict';
  const D = JSON.parse(document.getElementById('cb-data').textContent);
  const root = document.documentElement;
  const RM = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const FINE = matchMedia('(pointer: fine)').matches;
  root.classList.add('m');
  if (RM) root.classList.add('rm');
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const smooth = (a, b, v) => { const t = clamp((v - a) / (b - a), 0, 1); return t * t * (3 - 2 * t); };
  const cents = (s) => Math.round(parseFloat(s) * 100);
  const money = (c) => (c < 0 ? '-$' : '$') + (Math.abs(c) / 100).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  let vw = innerWidth, vh = innerHeight;
  const isPhone = () => vw <= 760;

  // ---------------------------------------------------------------- words that rise out of a mask
  function split(el) {
    if (el.dataset.split === '1') return;
    el.dataset.split = '1';
    let i = 0;
    const walk = (node) => {
      [...node.childNodes].forEach((c) => {
        if (c.nodeType === 3) {
          const frag = document.createDocumentFragment();
          c.textContent.split(/(\s+)/).forEach((t) => {
            if (!t) return;
            if (/^\s+$/.test(t)) { frag.appendChild(document.createTextNode(t)); return; }
            const w = document.createElement('span'); w.className = 'w';
            const s = document.createElement('span'); s.textContent = t; s.style.setProperty('--i', i++);
            w.appendChild(s); frag.appendChild(w);
          });
          c.replaceWith(frag);
        } else if (c.nodeType === 1 && !c.classList.contains('odo') && c.tagName !== 'BR') walk(c);
      });
    };
    walk(el);
  }
  $$('[data-r]').forEach((el) => { if (el.dataset.r !== 'up') split(el); });
  $$('.sw').forEach(split);
  const lede = $('.lede'); if (lede) split(lede);
  const ledeW = lede ? $$('.w > span', lede) : [];
  // the lede darkens word by word with scroll. Color, not opacity: opacity below 1 flips Windows text from ClearType to grayscale
  // and back on every frame, which reads as the words glitching.
  const rgb = (c) => (c.match(/\d+(\.\d+)?/g) || [255, 255, 255]).slice(0, 3).map(Number);
  let INK = [10, 13, 24], BG = [255, 255, 255];
  if (lede) { INK = rgb(getComputedStyle(lede).color); let n = lede; while (n && n !== document.body) { const b = getComputedStyle(n).backgroundColor; if (b && !/rgba\(0, 0, 0, 0\)|transparent/.test(b)) { BG = rgb(b); break; } n = n.parentElement; } }
  const tone = (o) => `rgb(${INK.map((v, i) => Math.round(BG[i] + (v - BG[i]) * o)).join(',')})`;
  if (RM) ledeW.forEach((w) => { w.style.color = ''; }); else ledeW.forEach((w) => { w.style.color = tone(.14); });

  function swap(el, html) {
    if (el._html === html) return;
    const had = el._html !== undefined && el.textContent.trim() !== '';
    el._html = html; clearTimeout(el._t);
    if (RM) { el.innerHTML = html; return; }
    el.classList.remove('in'); el.classList.add('out');
    el._t = setTimeout(() => {
      el.innerHTML = html; el.dataset.split = ''; split(el);
      el.classList.remove('out'); void el.offsetWidth; el.classList.add('in');
    }, had ? 300 : 0);
  }

  // ---------------------------------------------------------------- rolling numbers
  class Odo {
    constructor(el) { this.el = el; this.sig = null; this.cols = []; }
    set(str, instant) {
      this.el.setAttribute('aria-label', str);
      const sig = str.replace(/\d/g, '0'), chars = [...str];
      let fresh = false;
      if (sig !== this.sig) {
        fresh = true; this.sig = sig; this.cols = [];
        const inner = document.createElement('span'); inner.className = 'odo__in'; inner.setAttribute('aria-hidden', 'true');
        chars.forEach((ch) => {
          if (/\d/.test(ch)) {
            const c = document.createElement('span'); c.className = 'odo__c';
            const s = document.createElement('span'); s.className = 'odo__s';
            for (let k = 0; k < 30; k++) { const d = document.createElement('span'); d.textContent = k % 10; s.appendChild(d); }
            c.appendChild(s); inner.appendChild(c); this.cols.push(s);
          } else { const k = document.createElement('span'); k.className = 'odo__k'; k.textContent = ch; inner.appendChild(k); }
        });
        this.el.replaceChildren(inner);
      }
      const digits = chars.filter((c) => /\d/.test(c)).map(Number);
      const go = () => this.cols.forEach((s, i) => {
        s.style.transitionDelay = (RM || instant) ? '0ms' : (i * 40) + 'ms';
        s.style.transitionDuration = (RM || instant) ? '0ms' : '';
        s.style.transform = `translate3d(0, ${-(10 + digits[i]) * 1.08}em, 0)`;
      });
      if (fresh && !instant && !RM) {
        this.cols.forEach((s) => { s.style.transitionDuration = '0ms'; s.style.transform = 'translate3d(0,0,0)'; });
        requestAnimationFrame(() => requestAnimationFrame(go));
      } else go();
    }
  }
  const odos = new Map();
  $$('.odo').forEach((el) => { const o = new Odo(el); odos.set(el, o); o.set(el.dataset.v || el.textContent.trim(), true); });

  // ---------------------------------------------------------------- smooth scroll
  let lenis = null;
  if (!RM && window.Lenis) { try { lenis = new window.Lenis({ lerp: 0.085, smoothWheel: true, wheelMultiplier: 0.95 }); } catch (e) { lenis = null; } }
  const scrollToY = (y) => { if (lenis) lenis.scrollTo(y, { duration: 1.5 }); else window.scrollTo({ top: y, behavior: RM ? 'auto' : 'smooth' }); };
  const absTop = (el) => el.getBoundingClientRect().top + window.scrollY;
  document.addEventListener('click', (e) => {
    const a = e.target.closest('a[href^="#"]'); if (!a) return;
    const t = document.getElementById(a.getAttribute('href').slice(1)); if (!t) return;
    e.preventDefault(); closeMenu(); closePrecon(true);
    scrollToY(Math.max(0, absTop(t)));
  });

  // ---------------------------------------------------------------- reveals
  const io = new IntersectionObserver((es) => es.forEach((e) => {
    if (!e.isIntersecting) return;
    e.target.classList.add('in'); io.unobserve(e.target);
    if (e.target._odo) e.target._odo();
  }), { threshold: 0.18, rootMargin: '0px 0px -6% 0px' });
  let started = false;
  function startReveals() {
    if (started) return; started = true;
    $$('[data-r]').forEach((el) => { if (el.closest('.hero')) el.classList.add('in'); else io.observe(el); });
  }
  const bOdo = $('#budget-odo');
  bOdo._odo = () => odos.get(bOdo).set(bOdo.dataset.v); bOdo.dataset.r = 'up'; io.observe(bOdo);
  odos.get(bOdo).set(bOdo.dataset.v.replace(/\d/g, '0'), true);
  $$('.sbar').forEach((b) => io.observe(b));

  // ---------------------------------------------------------------- nav, menu
  const nav = $('#nav'), prog = $('.nav__prog'), menu = $('#menu'), navLinks = $$('.nav__links a');
  function openMenu() { menu.classList.add('open'); menu.removeAttribute('inert'); $('#menu-btn').setAttribute('aria-expanded', 'true'); lenis && lenis.stop(); setTimeout(() => $('.menu__close').focus(), 50); }
  function closeMenu() { if (!menu.classList.contains('open')) return; menu.classList.remove('open'); menu.setAttribute('inert', ''); $('#menu-btn').setAttribute('aria-expanded', 'false'); lenis && lenis.start(); }
  $('#menu-btn').addEventListener('click', openMenu);
  $('.menu__close').addEventListener('click', () => { closeMenu(); $('#menu-btn').focus(); });

  // proposal PDF: a plain download link (Netlify, a local file); inside a claude.ai artifact the save goes through the downloads capability
  $$('[data-pdf]').forEach((a) => a.addEventListener('click', async (ev) => {
    const cl = window.claude;
    if (!cl || typeof cl.use !== 'function') return;
    ev.preventDefault();
    const href = a.getAttribute('href'), name = a.getAttribute('download') || 'Proposal.pdf';
    try {
      const dl = await cl.use('downloads');
      if (!dl) { window.open(href, '_blank', 'noopener'); return; }
      const blob = await (await fetch(href)).blob();
      await dl.save({ filename: name, data: blob });
    } catch (e) { if (!e || e.code !== 'declined') window.open(href, '_blank', 'noopener'); }
  }));

  // ---------------------------------------------------------------- pre-construction: an optional view, opened on request
  const pc = $('#precon'); let lastFocus = null;
  const pcPanel = $('.pc__panel');
  function openPrecon(e) {
    closeMenu(); lastFocus = document.activeElement;
    const card = e && e.currentTarget && e.currentTarget.classList && e.currentTarget.classList.contains('pcf__card') ? e.currentTarget : null;
    if (card) {   // the card opens into the full view: the panel starts clipped to the card and grows to the screen
      const r = card.getBoundingClientRect();
      pcPanel.style.setProperty('--ci', `${r.top.toFixed(1)}px ${(innerWidth - r.right).toFixed(1)}px ${(innerHeight - r.bottom).toFixed(1)}px ${r.left.toFixed(1)}px round 28px`);
      pcPanel.style.transition = 'none'; pcPanel.classList.add('from-card'); void pcPanel.offsetWidth; pcPanel.style.transition = '';   // jump to the card, then grow
    } else { pcPanel.style.transition = 'none'; pcPanel.classList.remove('from-card'); void pcPanel.offsetWidth; pcPanel.style.transition = ''; }
    pc.classList.add('open'); pc.removeAttribute('inert'); lenis && lenis.stop(); document.body.style.overflow = 'hidden';
    $('.pc__panel').scrollTop = 0; setTimeout(() => $('.pc__x').focus(), 80);
  }
  function closePrecon(silent) {
    if (!pc || !pc.classList.contains('open')) return;
    pc.classList.remove('open'); pc.setAttribute('inert', ''); lenis && lenis.start(); document.body.style.overflow = '';
    if (!silent && lastFocus && lastFocus.focus) lastFocus.focus();
  }
  $$('[data-precon]').forEach((b) => b.addEventListener('click', openPrecon));
  $$('.pcf__card').forEach((c) => c.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openPrecon({ currentTarget: c }); } }));
  const pcX = $('.pc__x'); if (pcX) pcX.addEventListener('click', () => closePrecon());   // kit v1.16: pre-construction is optional
  addEventListener('keydown', (e) => { if (e.key === 'Escape') { if (pc && pc.classList.contains('open')) closePrecon(); else closeMenu(); } });

  // ---------------------------------------------------------------- budget: Elements or MasterFormat, and the detail under each line
  const bview = $('.bview');
  $$('.pill', bview).forEach((p) => p.addEventListener('click', () => {
    const v = p.dataset.v; if (bview.dataset.view === v) return;
    bview.dataset.view = v;
    $$('.pill', bview).forEach((q) => { const on = q === p; q.classList.toggle('on', on); q.setAttribute('aria-selected', on ? 'true' : 'false'); });
    $('.brows--el').hidden = v !== 'el'; $('.brows--mf').hidden = v !== 'mf';
    const bar = $('.sbar--' + v); bar.classList.remove('in'); void bar.offsetWidth; requestAnimationFrame(() => bar.classList.add('in'));
  }));
  $$('.brow__h').forEach((h) => {
    if (h.tagName !== 'BUTTON') return;
    h.addEventListener('click', () => {
      const open = h.getAttribute('aria-expanded') !== 'true'; h.setAttribute('aria-expanded', open ? 'true' : 'false');
      const ul = h.nextElementSibling; ul.hidden = !open; if (open) { ul.classList.remove('rise'); void ul.offsetWidth; ul.classList.add('rise'); }
    });
  });
  const opLine = $('.btot__op');
  if (opLine) {
    opLine.addEventListener('mouseenter', () => { const bar = $('.bview').dataset.view === 'mf' ? $('.sbar--mf') : $('.sbar--el'), segs = $$('i', bar); bar.classList.add('hl'); segs[segs.length - 1].classList.add('on'); });
    opLine.addEventListener('mouseleave', () => $$('.sbar').forEach((bar) => { bar.classList.remove('hl'); $$('i', bar).forEach((s) => s.classList.remove('on')); }));
  }
  $$('.brows').forEach((panel) => {
    const bar = panel.classList.contains('brows--el') ? $('.sbar--el') : $('.sbar--mf');
    const segs = $$('i', bar);
    $$('.brow', panel).forEach((r, k) => {
      r.addEventListener('mouseenter', () => { bar.classList.add('hl'); segs[r.classList.contains('brow--op') ? segs.length - 1 : k] && segs[r.classList.contains('brow--op') ? segs.length - 1 : k].classList.add('on'); });
      r.addEventListener('mouseleave', () => { bar.classList.remove('hl'); segs.forEach((s) => s.classList.remove('on')); });
    });
  });

  // ---------------------------------------------------------------- selections and alternates: one set of requests, in cents, saved on this device until sent
  const BASE = cents(D.base), aOdoEl = $('#alt-odo'), aOdo = aOdoEl ? odos.get(aOdoEl) : null;
  const esc = (t) => String(t == null ? '' : t).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const sign = (c) => c === 0 ? 'No Change' : (c > 0 ? '+' : '') + money(c);
  const SX = D.sel || { els: [], views: [], refmap: {}, form: 'selections', subject: 'Selections' };
  const EL = {}; SX.els.forEach((e) => { EL[e.id] = e; });
  const ALT = {}; D.alts.forEach((a) => { ALT[a.id] = a; });
  const KEY = 'mcc-sel-' + (D.job || D.name || 'job');
  const store = { picks: {}, alts: {}, sent: null };
  try { const s0 = JSON.parse(localStorage.getItem(KEY) || 'null'); if (s0 && s0.picks) { store.picks = s0.picks; store.alts = s0.alts || {}; store.sent = s0.sent || null; } } catch (e) {}
  const persist = () => { try { localStorage.setItem(KEY, JSON.stringify(store)); } catch (e) {} };
  const carried = (e) => e.mode === 'rate' ? +e.base : e.options[0].id;
  const valC = (e, pick) => e.mode === 'rate' ? Math.round((pick - +e.base) * parseFloat(e.per) * 100) : cents((e.options.find((o) => o.id === pick) || { v: '0' }).v);
  Object.keys(store.picks).forEach((k) => { if (!EL[k]) delete store.picks[k]; });   // a request for an element this page no longer has
  Object.keys(store.alts).forEach((k) => { if (!ALT[k] || SX.refmap[k]) delete store.alts[k]; });
  const reqSum = (skip) => Object.keys(store.picks).reduce((t, k) => k === skip ? t : t + valC(EL[k], store.picks[k]), 0) + Object.keys(store.alts).reduce((t, k) => t + cents(ALT[k].v), 0);
  const reqCount = () => Object.keys(store.picks).length + Object.keys(store.alts).length;
  const pickLabel = (e, pick) => e.mode === 'rate' ? (e.unit === 'LUMP' ? money(Math.round(pick * 100)) + ' Allowance' : money(Math.round(pick * 100)) + ' per ' + e.unit) : (e.options.find((o) => o.id === pick) || e.options[0]).name;
  function reqLines() {
    const out = [];
    SX.els.forEach((e) => { if (store.picks[e.id] !== undefined) out.push({ name: e.name, pick: pickLabel(e, store.picks[e.id]), v: valC(e, store.picks[e.id]) }); });
    D.alts.forEach((a) => { if (store.alts[a.id]) out.push({ name: a.title.replace(/^[0-9]+[.] /, ''), pick: cents(a.v) < 0 ? 'Value Engineering' : 'Alternate', v: cents(a.v) }); });
    return out;
  }

  // the Alternates and Value Engineering list: a switch that belongs to a card element moves that element's choice
  function altState(id) {
    const m = SX.refmap[id];
    if (m) { const e = EL[m[0]]; return e && store.picks[e.id] !== undefined && String(store.picks[e.id]) === String(m[1]); }
    return !!store.alts[id];
  }
  $$('.tog').forEach((t) => t.addEventListener('click', () => {
    const id = t.dataset.id, m = SX.refmap[id], on = !altState(id);
    if (m) { if (on) store.picks[m[0]] = EL[m[0]].mode === 'rate' ? +m[1] : m[1]; else delete store.picks[m[0]]; delete prev[m[0]]; }
    else if (on) store.alts[id] = true; else delete store.alts[id];
    persist(); refresh();
  }));
  const altSend = $('#alt-send'); if (altSend) altSend.addEventListener('click', openSend);

  // the stage: Exterior, Interior, Site and List, with a point for every element
  const sx = D.sel ? $('#selections') : null, card = $('#sx-card'), pinsEl = $('#sx-pins'), prev = {};
  let view = SX.views.length ? SX.views[0].id : 'list', act = SX.els.length ? SX.els[0].id : null;
  const pickOf = (e) => prev[e.id] !== undefined ? prev[e.id] : (store.picks[e.id] !== undefined ? store.picks[e.id] : carried(e));
  function setView(v) {
    view = v;
    if (sx) {
      $$('.sx-view', sx).forEach((el) => { el.hidden = el.dataset.view !== v; });
      $$('.selx__pills .pill', sx).forEach((b) => { const on = b.dataset.view === v; b.classList.toggle('on', on); b.setAttribute('aria-pressed', on ? 'true' : 'false'); });
      const cur = EL[act];
      if (v !== 'list' && (!cur || cur.view !== v)) { const first = SX.els.find((e) => e.view === v); if (first) act = first.id; }
    }
    refresh();
  }
  function sxStage() {
    if (!sx) return;
    SX.views.forEach((v) => {   // a render made for a choice replaces the view while that choice is picked
      Object.keys(v.swap || {}).forEach((elId) => {
        const img = $(`.sx-view[data-view="${v.id}"] img`, sx), e = EL[elId], alt = e && (v.swap[elId][pickOf(e)]);
        if (img) { const want = alt || v.src; if (img.getAttribute('src') !== want) img.setAttribute('src', want); }
      });
      if (v.el && EL[v.el]) {   // the site plan's driveway in the picked surface
        const e = EL[v.el], pick = pickOf(e), o = e.options.find((x) => x.id === pick) || e.options[0], defs = $('#sx-pats');
        if (defs && !defs.childNodes.length) defs.innerHTML = e.options.filter((x) => x.src).map((x) => `<pattern id="sxp-${x.id}" patternUnits="userSpaceOnUse" width="150" height="150"><image href="${x.src}" width="150" height="150"/></pattern>`).join('');
        const main = o.section ? e.options[0] : o, d = $('#sx-drive'), sec = $('#sx-sec');
        if (d) d.setAttribute('stroke', `url(#sxp-${main.id})`);
        if (sec) sec.setAttribute('stroke', `url(#sxp-${o.id})`);
      }
    });
    pinsEl.innerHTML = view === 'list' ? '' : SX.els.filter((e) => e.view === view).map((e) =>
      `<button type="button" class="sx-pin${e.id === act ? ' on' : ''}${store.picks[e.id] !== undefined ? ' req' : ''}" style="left:${e.at[0]}%;top:${e.at[1]}%" data-el="${e.id}" aria-label="${esc(e.name)}"><span>${e.n}</span></button>`).join('');
    const list = $('#sx-list');
    if (list && view === 'list') {
      const VN = {}; SX.views.forEach((v) => { VN[v.id] = v.label; });
      list.innerHTML = `<div class="sx-row sx-row--h"><span>No.</span><span>Item</span><span>In the Budget or Requested</span><span class="r">Change</span><span class="r">Status</span></div>` +
        SX.els.map((e) => { const r = store.picks[e.id] !== undefined;
          return `<button type="button" class="sx-row${e.id === act ? ' on' : ''}" data-el="${e.id}"><span class="sx-n">${e.n}</span><span class="sx-item"><b>${esc(e.name)}</b><small>${esc(VN[e.view] || '')}</small></span><span class="cut">${esc(r ? pickLabel(e, store.picks[e.id]) : e.carried)}</span><span class="r num">${r ? sign(valC(e, store.picks[e.id])) : 'No Change'}</span><span class="r"><i class="sx-st${r ? ' sx-st--req' : ''}">${r ? 'Requested' : 'In the Budget'}</i></span></button>`; }).join('');
    }
  }
  function cardHtml(e) {
    const pick = pickOf(e), d = valC(e, pick), isBase = pick === carried(e), isReq = store.picks[e.id] !== undefined && String(store.picks[e.id]) === String(pick);
    let body = '';
    if (e.mode === 'options') {
      const sel = e.options.find((o) => o.id === pick) || e.options[0], many = e.options.length > 2;
      body = `<div class="sx-tiles${many ? ' sx-tiles--3' : ''}">` + e.options.map((o, k) => { const on = o.id === pick, rq = store.picks[e.id] === o.id;
        return `<button type="button" class="sx-tile${on ? ' on' : ''}" data-opt="${o.id}" aria-pressed="${on}"><span class="sx-tile__img">${o.src ? `<img src="${o.src}" alt="" loading="lazy" decoding="async">` : `<i>${esc(o.ph)}</i>`}${rq ? '<em>Requested</em>' : ''}</span><b>${esc(o.name)}</b><span class="num${k === 0 ? ' base' : ''}">${k === 0 ? 'In the Budget' : sign(cents(o.v))}</span></button>`; }).join('') +
        `</div><p class="sx-note">${esc(sel.note)}</p>`;
    } else {
      const pos = (v) => ((v - e.min) / (e.max - e.min) * 100).toFixed(2) + '%';
      const per = parseFloat(e.per), perTxt = e.unit === 'LUMP' ? `Every $1,000 moves the budget ${money(Math.round(per * 100000))}.` : e.unit === 'LF' ? `Every $100 per LF moves the budget ${money(Math.round(per * 10000))}.` : `Every $1.00 per SF moves the budget ${money(Math.round(per * 100))}.`;
      const marks = [{ v: +e.base, label: 'In the Budget', base: true }].concat(e.marks || []);
      body = `<div class="sx-banner">${e.src ? `<img src="${e.src}" alt="" loading="lazy" decoding="async">` : '<i>Supplier Photos</i>'}</div>
        <div class="sx-rate"><b class="num" id="sx-rate">${money(Math.round(pick * 100))}</b><span>${e.unit === 'LUMP' ? 'Allowance' : 'per ' + e.unit}</span></div>
        <label class="sx-dial"><span class="lab">${esc(e.label)}</span><input type="range" id="sx-range" min="${e.min}" max="${e.max}" step="${e.step}" value="${pick}"></label>
        <div class="sx-marks"><span${marks.some((m) => (m.v - e.min) / (e.max - e.min) < 0.16) ? ' hidden' : ''}>${money(e.min * 100)}</span><span${marks.some((m) => (m.v - e.min) / (e.max - e.min) > 0.84) ? ' hidden' : ''}>${money(e.max * 100)}</span>${marks.map((m) => `<em class="${m.base ? 'base' : ''}" style="left:${pos(m.v)}">${esc(m.label)}</em>`).join('')}</div>
        <p class="sx-note"><b>${perTxt}</b> ${esc(e.after)}</p>`;
    }
    return `<div class="sx-card__h"><span class="sx-n">${e.n}</span><h3>${esc(e.name)}</h3></div>
      <p class="sx-where">${esc(e.where)}</p><p class="sx-carried"><b>In the Budget:</b> ${esc(e.carried)}</p>${body}
      <div class="sx-stats"><div><span class="lab">This Choice</span><b class="num${d < 0 ? ' neg' : ''}" id="sx-d">${sign(d)}</b></div><div><span class="lab">Budget With It</span><b class="num" id="sx-t">${money(BASE + reqSum(e.id) + d)}</b></div></div>
      <div class="sx-act" id="sx-act">${actHtml(e, pick, isBase, isReq)}</div>`;
  }
  function actHtml(e, pick, isBase, isReq) {
    if (isBase) return '<div class="sx-in">In the Budget</div>';
    if (isReq) return '<div class="sx-reqd"><span>Requested. Montana confirms it in writing.</span><button type="button" data-undo>Withdraw</button></div>';
    return `<button type="button" class="btn btn--navy sx-ask"><span>Request ${esc(pickLabel(e, pick))}</span></button>`;
  }
  function rateUpdate(e) {   // while the dial moves: numbers only, so the input keeps the pointer
    const pick = pickOf(e), d = valC(e, pick), isReq = store.picks[e.id] !== undefined && +store.picks[e.id] === pick;
    $('#sx-rate').textContent = money(Math.round(pick * 100));
    const dd = $('#sx-d'); dd.textContent = sign(d); dd.classList.toggle('neg', d < 0);
    $('#sx-t').textContent = money(BASE + reqSum(e.id) + d);
    $('#sx-act').innerHTML = actHtml(e, pick, pick === +e.base, isReq);
  }
  function sxBar() {
    const sum = reqSum(null), n = reqCount();
    if (sx) {
      $('#sx-req').textContent = n ? sign(sum) : '$0.00'; $('#sx-if').textContent = money(BASE + sum);
      const b = $('#sx-send'); b.disabled = n === 0; $('span', b).textContent = n ? `Send ${n} to Montana` : 'Send to Montana';
    }
    const altAdd = $('#alt-add'); if (altAdd) altAdd.textContent = n ? sign(sum) : money(0); if (aOdo) aOdo.set(money(BASE + sum));
    $$('.tog').forEach((t) => t.setAttribute('aria-checked', altState(t.dataset.id) ? 'true' : 'false'));
  }
  function refresh() { if (sx && act && EL[act]) card.innerHTML = cardHtml(EL[act]); sxStage(); sxBar(); }
  if (sx) {
    $$('.selx__pills .pill', sx).forEach((b) => b.addEventListener('click', () => setView(b.dataset.view)));
    sx.addEventListener('click', (ev) => {
      const pin = ev.target.closest('[data-el]');
      if (pin && sx.contains(pin)) { act = pin.dataset.el; refresh(); if (isPhone() && view !== 'list') card.scrollIntoView({ block: 'nearest' }); return; }
      const e = EL[act]; if (!e) return;
      const tile = ev.target.closest('.sx-tile');
      if (tile) { prev[e.id] = tile.dataset.opt; refresh(); return; }
      if (ev.target.closest('.sx-ask')) { store.picks[e.id] = pickOf(e); delete prev[e.id]; persist(); refresh(); return; }
      if (ev.target.closest('[data-undo]')) { delete store.picks[e.id]; delete prev[e.id]; persist(); refresh(); return; }
    });
    sx.addEventListener('input', (ev) => { if (ev.target.id === 'sx-range') { const e = EL[act]; prev[e.id] = +ev.target.value; rateUpdate(e); sxStage(); } });
    $('#sx-send').addEventListener('click', openSend);
  }

  // send: a Netlify form on the live page; anywhere else, the same list by email
  const sxs = $('#sxs');
  function openSend() {
    if (!sxs) return;
    const lines = reqLines(), sum = reqSum(null);
    $('#sxs-list').innerHTML = (lines.length ? lines.map((l) => `<div><span>${esc(l.name)}</span><span>${esc(l.pick)}</span><b class="num">${sign(l.v)}</b></div>`).join('') : '<p>No requests yet. Pick an option on any card, then Request it.</p>') +
      `<div class="tot"><span>If Montana Confirms</span><span></span><b class="num">${money(BASE + sum)}</b></div>`;
    $('#sxs-form').hidden = !lines.length; $('#sxs-done').hidden = true;
    sxs.hidden = false; lenis && lenis.stop(); document.body.style.overflow = 'hidden';
    setTimeout(() => { const f = $('#sxs-form input[name=name]'); f && !$('#sxs-form').hidden ? f.focus() : $('.sxs__x', sxs).focus(); }, 40);
  }
  function closeSend() { if (!sxs || sxs.hidden) return; sxs.hidden = true; lenis && lenis.start(); document.body.style.overflow = ''; }
  if (sxs) {
    $$('[data-close]', sxs).forEach((b) => b.addEventListener('click', closeSend));
    sxs.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeSend(); });
    $('#sxs-form').addEventListener('submit', (ev) => {
      ev.preventDefault();
      const f = new FormData(ev.target), lines = reqLines(), sum = reqSum(null);
      const text = lines.map((l) => `${l.name}: ${l.pick} (${sign(l.v)})`).join('\n') + `\nIf Montana confirms: ${money(BASE + sum)}`;
      const body = new URLSearchParams({ 'form-name': SX.form, job: D.job || '', name: f.get('name') || '', email: f.get('email') || '', role: f.get('role') || '', company: '',
        note: f.get('note') || '', requests: text, change: sign(sum), total: money(BASE + sum), data: JSON.stringify({ picks: store.picks, alts: store.alts }) });
      const btn = $('#sxs-form button[type=submit] span'); btn.textContent = 'Sending';
      const done = (ok) => {
        btn.textContent = 'Send Requests'; $('#sxs-form').hidden = true; const box = $('#sxs-done'); box.hidden = false;
        if (ok) { store.sent = { at: new Date().toISOString(), n: lines.length }; persist(); box.innerHTML = '<p><b>Sent to Montana.</b> We confirm each change in writing, then it moves into the next revision of the budget.</p>'; }
        else {
          const mail = `mailto:${D.email}?subject=${encodeURIComponent(SX.subject)}&body=${encodeURIComponent(`${f.get('name') || ''}${f.get('note') ? '\n' + f.get('note') : ''}\n\n${text}`)}`;
          box.innerHTML = `<p>This copy of the page cannot send on its own. Email the list instead.</p><a class="btn btn--navy" href="${mail}"><span>Email the List</span></a>`;
        }
      };
      if (!document.querySelector('meta[name="mcc-send"]') || !/^https?:$/.test(location.protocol)) { done(false); return; }   // only the Netlify build posts; the preview and a local file email instead
      fetch('/', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: body.toString() }).then((r) => done(r.ok)).catch(() => done(false));
    });
  }
  if (sx) setView(view); else sxBar();

  // ---------------------------------------------------------------- magnetic buttons
  if (FINE && !RM) $$('.mag').forEach((b) => {
    b.addEventListener('pointermove', (e) => { const r = b.getBoundingClientRect(); b.style.transform = `translate3d(${(e.clientX - r.left - r.width / 2) * 0.22}px, ${(e.clientY - r.top - r.height / 2) * 0.3}px, 0)`; });
    b.addEventListener('pointerleave', () => { b.style.transform = ''; });
  });

  // ---------------------------------------------------------------- the model stage
  const stage = $('#stage'), frameEl = $('.frame'), imgs = $$('.frame img');
  const S = D.steps, N = S.length;
  const scLabel = $('.sc-label'), scTitle = $('.sc-title'), scSub = $('.sc-sub'), scFig = $('.sc-fig'), scCap = $('.sc-cap'), scBody = $('.sc-body');
  const sOdo = odos.get($('#stage-odo'));
  const elists = $$('.elist'), eBtns = $$('.elist button');   // one list per building on a whole-property job (data-b), or one list
  const wallx = $('.wallx'), scCopy = $('.stage__copy');   // optional wall assembly panel on a step with s.wall
  const mk = $('#mk'), mkb = $('#mkb'), mkl = $('#mkl'), mkn = $('#mkn'), mks = $$('.mks'), rail = $$('.stage__rail button'), note = $('.stage__note');
  const STYLES = ['brackets', 'dot', 'leader', 'badge'];
  const hs = (location.hash || '').replace('#mk-', ''); if (STYLES.includes(hs)) frameEl.dataset.mk = hs;
  const pt = (k) => { const p = D.points[k]; return [p[0] / D.frame[0] * 100, p[1] / D.frame[1] * 100]; };
  const sameB = (a, b) => (a.dataset.b || '') === (b.dataset.b || '');
  function placeMks() {   // numbered badges: start at each element, then push apart any that would overlap at this size
    const fr = $('.frame').getBoundingClientRect(); if (!fr.width) return;
    const P = mks.map((m) => { const p = pt(m.dataset.k); return [p[0] / 100 * fr.width, p[1] / 100 * fr.height]; }), gap = 27;
    for (let it = 0; it < 24; it++) for (let a = 0; a < P.length; a++) for (let b = a + 1; b < P.length; b++) {
      if (!sameB(mks[a], mks[b])) continue;
      let dx = P[b][0] - P[a][0], dy = P[b][1] - P[a][1]; if (Math.hypot(dx, dy) < 0.5) { dx = 1; dy = 0; } const d = Math.hypot(dx, dy);
      if (d < gap) { const k = (gap - d) / 2, ux = dx / d, uy = dy / d; P[a][0] -= ux * k; P[a][1] -= uy * k; P[b][0] += ux * k; P[b][1] += uy * k; }
    }
    mks.forEach((m, i) => { m.style.left = (P[i][0] / fr.width * 100).toFixed(2) + '%'; m.style.top = (P[i][1] / fr.height * 100).toFixed(2) + '%'; });
  }
  placeMks(); addEventListener('resize', placeMks); addEventListener('load', placeMks);
  let cur = -1;
  function place(el, k) { const p = pt(k); el.style.left = p[0] + '%'; el.style.top = p[1] + '%'; }
  function setStep(i) {
    if (i === cur) return;
    cur = i; const s = S[i];
    swap(scLabel, s.label); swap(scTitle, s.title); swap(scSub, s.sub || ''); swap(scCap, s.cap || ''); swap(scBody, s.body || '');
    if (s.fig) { scFig.classList.remove('hide'); sOdo.set(s.fig); } else scFig.classList.add('hide');
    elists.forEach((e) => e.classList.toggle('hide', !(s.all && (!s.bld || !e.dataset.b || e.dataset.b === s.bld))));
    if (wallx) { wallx.classList.toggle('hide', !s.wall); scCopy.classList.toggle('wall-on', !!s.wall); }
    const isEl = s.el != null;
    [mk, mkb, mkl, mkn].forEach((m) => m.classList.toggle('show', isEl));
    if (isEl) {
      const k = D.els[s.el].k, b = D.bb[k];
      const no = String(s.no || s.el + 1).padStart(2, '0');   // numbered within its building
      place(mk, k); place(mkl, k); place(mkn, k); mkn.textContent = no; mkl.querySelector('b').textContent = no;
      const pad = 10;
      mkb.style.left = ((b[0] - pad) / D.frame[0] * 100) + '%'; mkb.style.top = ((b[1] - pad) / D.frame[1] * 100) + '%';
      mkb.style.width = ((b[2] - b[0] + pad * 2) / D.frame[0] * 100) + '%'; mkb.style.height = ((b[3] - b[1] + pad * 2) / D.frame[1] * 100) + '%';
    }
    mks.forEach((m) => m.classList.toggle('show', !!s.all && (!s.bld || m.dataset.b === s.bld)));
    rail.forEach((b, k) => b.classList.toggle('on', k === s.rail));
    const rb = rail[s.rail], rw = rb && rb.parentElement;   // on a phone the rail scrolls sideways, so keep the current step in view
    if (rw && rw.scrollWidth > rw.clientWidth + 2) rw.scrollTo({ left: Math.max(0, rb.offsetLeft - (rw.clientWidth - rb.offsetWidth) / 2), behavior: 'smooth' });
    if (note) note.textContent = s.note || '';
  }
  const stepH = () => (stage.offsetHeight - vh) / N;
  const stepY = (k) => absTop(stage) + (k + 0.05) * stepH();
  rail.forEach((b) => b.addEventListener('click', () => scrollToY(stepY(S.findIndex((s) => s.rail === +b.dataset.step)))));
  eBtns.forEach((b, k) => b.addEventListener('click', () => scrollToY(stepY(S.findIndex((s) => s.el === k)))));
  setStep(0);

  // ---------------------------------------------------------------- layout
  const gal = $('#gallery'), track = $('.track'), shots = $$('.shot'), galCount = $('.gallery__count b');
  const sched = $('#schedule'), gantt = $('.gantt');
  function layout() {
    vw = innerWidth; vh = innerHeight;
    stage.style.height = (N * vh * 0.8 + vh) + 'px';
    if (isPhone()) { gal.style.height = ''; track.style.transform = ''; }
    else gal.style.height = (track.scrollWidth - vw + vh) + 'px';
    sched.classList.remove('nopin'); sched.style.height = '';
    const pinH = $('.sched__grid').getBoundingClientRect().height + 120;   // the odometer strips overflow, so scrollHeight overstates it
    if (isPhone() || pinH > vh + 4) sched.classList.add('nopin');   // pin only when the whole chart fits the screen
    else sched.style.height = (vh + vh * 1.3) + 'px';
  }
  layout();
  let rT; addEventListener('resize', () => { clearTimeout(rT); rT = setTimeout(layout, 120); });

  // ---------------------------------------------------------------- schedule: a week cursor plays the job out as you scroll
  const gRows = $$('.g-row'), gFills = $$('.g-fill'), gCursor = $('#g-cursor'), wOdo = odos.get($('#week-odo')), wPh = $('#week-ph');
  const PH = $$('.g-legend li').map((li) => ({ el: li, name: li.querySelector('b').textContent, a: +li.dataset.a, b: +li.dataset.b })), gCw = $('#g-cw'), gCl = $('.g-cursor__l');
  const rowsAB = gRows.map((r) => [+r.dataset.a, +r.dataset.b]);
  const rowPhase = gRows.map((r) => { const c = r.querySelector('.g-bar').style.getPropertyValue('--c').trim(); const li = PH.find((p) => p.el.style.getPropertyValue('--c').trim() === c); return li ? li.name : ''; });
  let lastWeek = -1;
  function weekAt(p) {
    const w = p * D.span;
    rowsAB.forEach(([a, b], k) => {
      const s = clamp((w - a) / (b - a), 0, 1);
      if (gFills[k]._s !== s) { gFills[k].style.transform = `scaleX(${s.toFixed(3)})`; gFills[k]._s = s; }
      gRows[k].classList.toggle('on', w >= a && w <= b);
    });
    gCursor.style.left = (p * 100) + '%'; gCl.style.transform = `translateX(${(-p * 100).toFixed(2)}%)`;
    PH.forEach((ph) => { const q = clamp((w - ph.a) / Math.max(0.01, ph.b - ph.a), 0, 1); if (ph._q !== q) { ph.el.style.setProperty('--p', q.toFixed(3)); ph._q = q; } });
    const wk = Math.min(D.weeks, Math.round(w));
    if (wk !== lastWeek) {
      lastWeek = wk; wOdo.set(String(wk).padStart(2, '0')); gCw.textContent = wk;
      let name = PH[PH.length - 1].name;
      for (let k = rowsAB.length - 1; k >= 0; k--) { const [a, b] = rowsAB[k]; if (w >= a && w <= b) { name = rowPhase[k]; break; } }
      if (wk === 0) name = PH[0].name;
      wPh.textContent = name; PH.forEach((p) => p.el.classList.toggle('on', p.name === name));
    }
  }
  if (RM) weekAt(1);

  // ---------------------------------------------------------------- one frame of scroll
  const dusk = $('.dusk'), duskImg = $('.dusk img'), contact = $('#contact');
  const heroBg = $('.hero__bg'), heroIn = $('.hero__inner'), heroShade = $('.hero__shade');
  const secs = ['project', 'stage', 'budget', 'selections', 'schedule', 'approach'].map((id) => document.getElementById(id)).filter(Boolean);
  const spanK = secs.findIndex((x) => x.id === 'selections') >= 0 ? secs.findIndex((x) => x.id === 'selections') : secs.findIndex((x) => x.id === 'budget');
  const budgetEnd = $('#notes');
  const snap = (v) => { const d = window.devicePixelRatio || 1; return Math.round(v * d) / d; };
  const put = (el, k, v) => { const c = '_' + k; if (el[c] !== v) { el.style[k] = v; el[c] = v; } };
  function frame() {
    const y = window.scrollY;
    if (y < vh * 1.15) {
      // whole device pixels only, and no scale: a photo of thin battens moved by fractions of a pixel shimmers on a standard-density screen
      const p = clamp(y / vh, 0, 1.2);
      put(heroBg, 'transform', `translate3d(0, ${snap(p * vh * 0.28)}px, 0)`);
      put(heroIn, 'transform', `translate3d(0, ${snap(-p * vh * 0.14)}px, 0)`);
      put(heroIn, 'opacity', clamp(1 - p * 1.5, 0, 1).toFixed(3)); put(heroShade, 'opacity', (p * 0.55).toFixed(3));
    }
    const dR = dusk.getBoundingClientRect(), cR = contact.getBoundingClientRect();
    const overDusk = dR.top <= 64 && dR.bottom > 64, overNavy = cR.top <= 64;
    nav.classList.toggle('solid', y > vh * 0.86 && !overDusk && !overNavy); nav.classList.toggle('navy', overNavy);
    const max = document.documentElement.scrollHeight - vh; put(prog, 'transform', `scaleX(${(max > 0 ? y / max : 0).toFixed(4)})`);
    let on = -1;
    secs.forEach((s, k) => { const r = s.getBoundingClientRect(); const bottom = k === spanK ? budgetEnd.getBoundingClientRect().bottom : r.bottom; if (r.top < vh * 0.45 && bottom > vh * 0.45) on = k; });
    navLinks.forEach((a, k) => a.classList.toggle('on', k === on));
    if (lede && !RM) {
      const r = lede.getBoundingClientRect();
      if (r.top < vh && r.bottom > 0) {
        const p = clamp((vh * 0.9 - r.top) / (r.height + vh * 0.4), 0, 1), n = ledeW.length;
        ledeW.forEach((w, k) => { const o = (.14 + .86 * smooth(k / n - .08, k / n + .04, p)).toFixed(2); if (w._o !== o) { w.style.color = tone(+o); w._o = o; } });
      }
    }
    if (!isPhone()) {
      const r = gal.getBoundingClientRect();
      if (r.top < vh && r.bottom > 0) {
        const p = clamp(-r.top / Math.max(1, r.height - vh), 0, 1), maxX = Math.max(0, track.scrollWidth - vw);
        const tx = snap(-p * maxX); put(track, 'transform', `translate3d(${tx}px, 0, 0)`);
        let best = 0, bd = 1e9;
        shots.forEach((s, k) => { const c = Math.abs(s.offsetLeft + tx + s.offsetWidth / 2 - vw / 2); if (c < bd) { bd = c; best = k; } });
        const gc = String(best + 1).padStart(2, '0'); if (galCount.textContent !== gc) galCount.textContent = gc;
      }
    }
    const sr = stage.getBoundingClientRect();
    if (sr.top < vh && sr.bottom > 0) {
      const p = clamp(-sr.top / Math.max(1, sr.height - vh), 0, 1), x = p * N, i = Math.min(N - 1, Math.floor(x)), f = x - i;
      const want = S[i].img, next = i + 1 < N ? S[i + 1].img : -1, via = S[i].via;
      const o = imgs.map(() => 0);
      if (via != null && next >= 0) {
        o[want] = f < 0.72 ? 1 : 0; o[via] = smooth(0.38, 0.68, f); if (f >= 0.72) o[via] = 1; o[next] = Math.max(o[next], smooth(0.72, 1, f));
      } else { o[want] = 1; if (next >= 0 && next !== want) o[next] = smooth(0.62, 1, f); }
      imgs.forEach((im, k) => { if (im._o !== o[k]) { im.style.opacity = o[k]; im._o = o[k]; } });
      setStep(i);
    }
    const cr = sched.getBoundingClientRect();
    if (cr.top < vh && cr.bottom > 0 && !RM) {
      const free = sched.classList.contains('nopin'), gr = free ? gantt.getBoundingClientRect() : null;
      const p = free ? clamp((vh * 0.72 - gr.top) / Math.max(1, gr.height), 0, 1) : clamp(-cr.top / Math.max(1, cr.height - vh), 0, 1);
      weekAt(smooth(0.04, 0.92, p));
    }
  }
  function loop(t) { if (lenis) lenis.raf(t); frame(); requestAnimationFrame(loop); }

  // ---------------------------------------------------------------- loader: the M assembles while the entry photo loads, then lifts
  const loader = $('#loader'), lbar = $('#loader-bar');
  // the photo counts as ready only once it is decoded, so it never paints in pieces after the loader lifts
  const ready = (im) => (im.complete ? Promise.resolve() : new Promise((r) => { im.addEventListener('load', r, { once: true }); im.addEventListener('error', r, { once: true }); }))
    .then(() => (im.decode ? im.decode().catch(() => {}) : null));
  const crit = [document.fonts ? document.fonts.ready : Promise.resolve(), ...$$('[data-crit]').map(ready)];
  let done = 0; crit.forEach((p) => p.then(() => { done++; lbar.style.setProperty('--p', done / crit.length); }));
  let lifted = false;
  function lift() {
    if (lifted) return; lifted = true;
    layout(); root.classList.add('go'); loader.classList.add('out');
    setTimeout(() => loader.remove(), 1200); startReveals(); setTimeout(warm, 1400);
  }
  // decode the rest of the photos and model frames in the background, one at a time, before the reader scrolls to them
  let lastScroll = 0; addEventListener('scroll', () => { lastScroll = performance.now(); }, { passive: true });
  function warm() {
    const ims = $$('img').filter((im) => !im.hasAttribute('data-crit'));
    const idle = window.requestIdleCallback || ((f) => setTimeout(f, 60));
    const next = () => { if (performance.now() - lastScroll < 700) return void setTimeout(next, 350);
      const im = ims.shift(); if (!im) return; im.loading = 'eager';
      const go = () => (im.decode ? im.decode() : Promise.resolve()).catch(() => {}).then(() => idle(next));
      if (im.complete) go(); else { im.addEventListener('load', go, { once: true }); im.addEventListener('error', () => idle(next), { once: true }); } };
    idle(next);
  }
  if (RM) { loader.remove(); root.classList.add('go'); startReveals(); }
  else { const t0 = performance.now(); Promise.all(crit).then(() => setTimeout(lift, Math.max(250, 1100 - (performance.now() - t0)))); setTimeout(lift, 7000); }
  requestAnimationFrame(loop);
})();
