// Montana bid presentation kit: the page. Builds every stop from project data, runs the money,
// the alternates, the Detailed Budget and the schedule chart. The 3D world (world.js) reads
// window.STOPS and calls window.PAGE.renderStops(p) once per frame.
(() => {
  const D = window.PROPOSAL, ROOT = document.documentElement;
  const $ = (s) => document.querySelector(s);
  const fmt = (n) => (n < 0 ? '-$' : '$') + Math.round(Math.abs(n)).toLocaleString('en-US');
  const short = (n) => '$' + (n / 1e6).toFixed(2) + 'M';
  const esc = (s) => String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const clamp01 = (v) => Math.min(1, Math.max(0, v));
  const ease = (t) => t * t * (3 - 2 * t);
  const NARROW = () => innerWidth < 760;
  const REDUCED = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const IMG = (n) => (D.img && D.img[n]) || n;
  const pct = (r) => +(r * 100).toFixed(2) + '%';

  // ---------------------------------------------------------------- money
  const groups = D.groups.map((g) => ({ ...g, total: Object.values(g.trades).reduce((a, b) => a + b, 0) }));
  const direct = groups.reduce((a, g) => a + g.total, 0);
  let run = direct; const marks = D.markups.map((m) => { const v = Math.round(run * m.rate); run += v; return { ...m, value: v }; });
  const BASE = run;
  window.MONEY = { groups, direct, marks, base: BASE };

  // ---------------------------------------------------------------- stops
  const altFeat = D.alternates.filter((a) => a.featured);
  const altVal = (a) => (a.value == null ? 'Not Priced' : (a.value >= 0 ? '+' : '') + fmt(a.value));
  const altRow = (a, where) => `<li><label><input type="checkbox" id="alt-${where}-${esc(a.id)}" data-alt="${esc(a.id)}"${a.value == null ? ' disabled' : ''}><span>${esc(a.title)}${a.note ? `<span class="m">${esc(a.note)}</span>` : ''}</span><span class="v">${altVal(a)}</span></label></li>`;
  const keyRows = (keys) => keys && keys.length ? `<div class="ra">${keys.map((k) => `<div class="rr"><span class="k">${esc(D.labels.key)}</span><p>${esc(k.key)}</p>${k.design ? `<span class="k">${esc(D.labels.design)}</span><p>${esc(k.design)}</p>` : ''}<span class="k o">${esc(D.labels.ours)}</span><p class="o">${esc(k.ours)}</p></div>`).join('')}</div>` : '';
  const paras = (b) => (b || []).map((t) => `<p>${esc(t)}</p>`).join('');
  const tagP = (t) => (t ? `<p class="tag">${esc(t)}</p>` : '');
  const T = {
    hero: (s) => `${tagP(s.tag)}<h1>${(s.h1 || [D.project.name]).map((l) => `<span class="ln">${esc(l)}</span>`).join(' ')}</h1>${s.lede ? `<p class="lede">${esc(s.lede)}</p>` : ''}${s.facts ? `<p class="facts">${s.facts.map(([b, l]) => `<span><b>${esc(b)}</b>${esc(l)}</span>`).join('')}</p>` : ''}`,
    story: (s) => `${tagP(s.tag)}<h2>${esc(s.h2)}</h2>${paras(s.body)}${s.line ? `<p class="line"><b>${esc(s.line.b)}</b>${esc(s.line.t || '')}</p>` : ''}${keyRows(s.keys)}${s.fine ? `<p class="fine">${esc(s.fine)}</p>` : ''}`,
    budget: (s) => `${tagP(s.tag || 'Base budget')}<span class="num" id="bigNumber"></span><div class="sbar" id="strataBar" aria-hidden="true"></div><div class="strata" id="strata"></div><p class="marks" id="marksLine"></p>`,
    alternates: (s) => `<div class="in"><h2>${esc(s.h2 || 'Alternates')}</h2><p style="color:#2b3038;font-size:15.5px;margin:0">${esc(s.lede || 'Priced with markups.')}</p><ul class="opts">${(altFeat.length ? altFeat : D.alternates).map((a) => altRow(a, 'opt')).join('')}</ul></div><div class="foot"><div class="close-row">${D.decisions && D.decisions.enabled === false ? '' : '<button class="btn" type="button" data-open-decs>Open the Decision List</button>'}<button class="btn${D.decisions && D.decisions.enabled === false ? '' : ' line'}" type="button" data-open-book>${esc(s.button || 'See the ' + D.labels.book)}</button></div></div>`,
    schedule: (s) => `<div class="sh-veil" aria-hidden="true"></div><div class="sh-scrim" aria-hidden="true"></div>
      <div class="sh-head">${tagP(s.tag)}<h2>${esc(s.h2 || 'Preliminary Schedule')}</h2>${s.lede ? `<p class="sh-lede">${esc(s.lede)}</p>` : ''}${s.moves ? `<p class="sh-moves">${esc(s.moves)}</p>` : ''}</div>
      <div class="sh-card"><div class="sh-hud" aria-hidden="true"><span class="sh-meta"><span id="shYr"></span> · <span id="shWk"></span></span><b class="sh-date" id="shDate"></b><span class="sh-now" id="shNow"></span></div>
      <div class="gantt" id="gantt" role="img" aria-label="${esc(s.h2 || 'Preliminary Schedule')}"></div>
      <div class="sh-foot"><div class="sh-held" id="shHeld"></div><div class="sh-key" aria-hidden="true">${(D.schedule?.legend || [['k-m', 'Montana'], ['k-o', 'By Others'], ['k-w', 'Weather Days'], ['k-h', 'Held'], ['k-c', 'Critical Path']]).map(([k, l]) => `<span><i class="${k}"></i>${esc(l)}</span>`).join('')}</div></div></div>`,
    precon: (s) => `${tagP(s.tag || 'Pre-construction')}<h2>${esc(s.h2 || 'Pre-Construction')}</h2>${paras(s.body)}<ol class="pcs">${D.precon.map(([b, t]) => `<li><b>${esc(b)}</b><span>${esc(t)}</span></li>`).join('')}</ol>`,
    job: (s) => `${tagP(s.tag || 'How we run the job')}<h2>${(s.h2 || ['Full-time supervision.', 'Full-time project management.']).map(esc).join('<br>')}</h2><div class="duty">${(s.duties || [['Superintendent', 'On site every working day, from the first excavation to the punch list.'], ['Project Manager', 'Runs the schedule, the budget, the submittals and the coordination with the design team.']]).map(([e, p]) => `<div><em>${esc(e)}</em><p>${esc(p)}</p></div>`).join('')}</div>`,
    principals: (s) => `${tagP(s.tag || 'Montana Contracting · Congers, New York · Since 1984')}<h2>${(s.h2 || [`${D.team.length === 3 ? 'Three' : D.team.length} principals stay on this project.`, 'You are never handed off.']).map(esc).join('<br>')}</h2><div class="trio">${D.team.map((t) => `<figure class="pp sm"><div class="ph"><img src="${IMG(t.photo)}" width="800" height="1000" alt="${esc(t.name)}, ${esc(t.title)}" decoding="async"></div><figcaption><b>${esc(t.name)}</b><span>${esc(t.title)}</span></figcaption></figure>`).join('')}</div>`,
    thanks: (s) => `${tagP(s.tag || 'From the principals')}<h2>${esc(s.h2 || 'Thank you for the opportunity.')}</h2>${paras(s.body)}<p class="sig"><img src="${IMG('mc-m.png')}" width="320" height="271" alt="Montana Contracting"><span>${D.team.map((t) => esc(t.name)).join(' · ')}</span></p><div class="next">${s.next ? `<p>${esc(s.next)}</p>` : ''}<div class="close-row"><button class="btn" type="button" data-open-book>See the ${esc(D.labels.book)}</button></div></div><p class="signoff">${esc(D.project.name)} · ${esc(D.project.chip)}</p>`,
    html: (s) => s.html,
  };
  T.build = T.story;
  const CLS = { hero: 's-hero', story: 's-story', build: 's-build', budget: 's-number s-budget', alternates: 's-options', schedule: 's-sched', precon: 's-precon', job: 's-job', principals: 's-principals', thanks: 's-thanks', html: 's-story' };
  const SIDE = { hero: 'l', budget: 'l', alternates: 'r', schedule: 'r', precon: 'l', job: 'r', principals: 'r', thanks: 'r' };
  const W = { hero: 0.8, story: 1, build: 1.8, budget: 0.9, alternates: 0.95, schedule: 2.6, precon: 1, job: 0.95, principals: 0.95, thanks: 0.9, html: 1 };
  const STOPS = [];
  {
    const list = D.stops.filter((s) => s.type !== 'schedule' || D.schedule);
    const tot = list.reduce((a, s) => a + (s.w ?? W[s.type] ?? 1), 0); let acc = 0;
    list.forEach((s, i) => {
      const w = s.w ?? W[s.type] ?? 1, s0 = acc / tot, s1 = (acc + w) / tot, len = s1 - s0; acc += w;
      const a = i === 0 ? 0 : s0 + 0.14 * len, b = i === list.length - 1 ? 1 : s1 - 0.14 * len;
      const side = s.side || SIDE[s.type] || 'l';
      STOPS.push({ ...s, id: s.id || s.type + i, side, scrim: s.scrim || (s.type === 'hero' ? 't' : side), scrimA: s.type === 'schedule' ? 0 : 1, s0, s1, len, a, b, name: s.name || s.h2 || s.type });
    });
  }
  window.STOPS = STOPS;
  $('#copy').innerHTML = STOPS.map((s) => `<section class="stop ${s.side} ${CLS[s.type] || 's-story'}${s.wide ? ' wide' : ''}" aria-label="${esc(s.name)}">${(T[s.type] || T.story)(s)}</section>`).join('\n');
  $('#ticks').innerHTML = STOPS.map((s, i) => `<li><button type="button" data-go="${i}"><i></i><span>${esc(s.name)}</span></button></li>`).join('');
  $('#spacer').style.height = Math.round(STOPS.reduce((a, s) => a + (s.w ?? W[s.type] ?? 1), 0) * 108) + 'vh';

  // ---------------------------------------------------------------- the number
  if ($('#bigNumber')) {
    $('#bigNumber').textContent = short(BASE);
    $('#strata').innerHTML = groups.map((g) => `<div><em style="background:${g.color}"></em><span>${esc(g.key)}</span><b>${fmt(g.total)}</b></div>`).join('') + `<div class="total"><em></em><span>Direct Cost of the Work</span><b>${fmt(direct)}</b></div>`;
    $('#strataBar').innerHTML = groups.map((g) => `<i style="background:${g.color}" data-w="${(g.total / direct * 100).toFixed(3)}"></i>`).join('');
    $('#marksLine').innerHTML = 'Plus ' + marks.map((m) => `${esc(m.label.toLowerCase())} <b>${pct(m.rate)}</b>`).join(' · ') + '.';
  }
  $('#mobileTotal').textContent = short(BASE);

  // ---------------------------------------------------------------- alternates (one state for the stop and the book)
  const altOn = new Set(); window.ALT_ON = altOn;
  function syncAlts() {
    let add = 0; for (const a of D.alternates) if (altOn.has(String(a.id)) && a.value != null) add += a.value;
    document.querySelectorAll('input[data-alt]').forEach((el) => { el.checked = altOn.has(el.dataset.alt); });
    const bt = $('#bookAltTotal'); if (bt) bt.textContent = fmt(BASE + add);
    document.dispatchEvent(new CustomEvent('alts', { detail: [...altOn] }));
  }
  document.addEventListener('change', (e) => {
    const el = e.target.closest && e.target.closest('input[data-alt]'); if (!el) return;
    if (el.checked) altOn.add(el.dataset.alt); else altOn.delete(el.dataset.alt);
    syncAlts();
  });

  // ---------------------------------------------------------------- the Detailed Budget
  const L = D.labels;
  const sections = [];
  const add = (id, title, sub, html) => sections.push({ id, title, sub, html });
  add('b-sections', 'Schedule of Values', 'Direct cost by trade, before markups. Open a group for its trades.', groups.map((g) => `
    <details class="sec"><summary><span>${esc(g.key)}</span><span class="v">${fmt(g.total)}</span></summary>${g.scope ? `<p class="scope">${esc(g.scope)}</p>` : ''}
      <div class="tbl-wrap"><table><thead><tr><th>Trade</th><th class="r">Direct Cost</th></tr></thead><tbody>
      ${Object.entries(g.trades).map(([t, v]) => `<tr><td>${esc(t)}</td><td class="r">${fmt(v)}</td></tr>`).join('')}</tbody></table></div></details>`).join(''));
  add('b-markups', 'Markups', 'They compound in the order listed.', `<div class="tbl-wrap"><table><thead><tr><th>Line</th><th class="r">Rate</th><th class="r">Amount</th></tr></thead><tbody>
    <tr><td>Direct Cost of the Work</td><td class="r"></td><td class="r">${fmt(direct)}</td></tr>${marks.map((m) => `<tr><td>${esc(m.label)}</td><td class="r">${pct(m.rate)}</td><td class="r">${fmt(m.value)}</td></tr>`).join('')}
    </tbody><tfoot><tr><td>Base Budget</td><td></td><td class="r">${fmt(BASE)}</td></tr></tfoot></table></div>`);
  if (D.allowances.length) add('b-allow', 'Allowances', 'A dollar amount held for something not yet selected.', `<div class="tbl-wrap"><table><thead><tr><th>Allowance</th><th>Basis</th><th class="r">Amount</th></tr></thead><tbody>${D.allowances.map((a) => `<tr><td>${esc(a.label)}</td><td>${esc(a.basis || '')}</td><td class="r">${esc(a.value)}</td></tr>`).join('')}</tbody></table></div>`);
  if (D.alternates.length) add('b-alts', 'Alternates', D.altNote || 'Priced with markups.', `<ul class="opts">${D.alternates.map((a) => altRow(a, 'book')).join('')}</ul><div class="tot"><div class="big"><span>Base Budget With Selected Alternates</span><span id="bookAltTotal">${fmt(BASE)}</span></div></div>`);
  if (D.keys.length) add('b-keys', L.keys, 'What the design calls for, and how we approach it.', `<div class="tbl-wrap"><table><thead><tr><th>${esc(L.key)}</th><th>${esc(L.design)}</th><th>${esc(L.ours)}</th><th>Source</th></tr></thead><tbody>${D.keys.map((r) => `<tr><td>${esc(r.key)}</td><td>${esc(r.design || '')}</td><td><b>${esc(r.ours)}</b></td><td class="mono">${esc(r.source || '')}</td></tr>`).join('')}</tbody></table></div>`);
  if (D.schedule && D.schedule.milestones) add('b-sched', 'Preliminary Schedule', D.schedule.note || '', `<div class="tbl-wrap"><table><thead><tr><th>Milestone</th><th>Date</th><th>By</th></tr></thead><tbody>${D.schedule.milestones.map((r) => `<tr><td>${esc(r[0])}</td><td>${esc(r[1])}</td><td class="mono">${esc(r[2] || '')}</td></tr>`).join('')}</tbody></table></div>`);
  if (D.precon.length) add('b-precon', 'Pre-Construction', D.preconNote || 'Optional, priced separately.', `<div class="tbl-wrap"><table><tbody>${D.precon.map((p, i) => `<tr><td class="mono">${String(i + 1).padStart(2, '0')}</td><td><b>${esc(p[0])}</b></td><td>${esc(p[1])}</td></tr>`).join('')}</tbody></table></div>`);
  if (D.exclusions.length) add('b-ex', 'Exclusions and By Owner', 'From the estimate notes and clarifications.', `<div class="tbl-wrap"><table><tbody>${D.exclusions.map((e) => `<tr><td>${esc(e)}</td></tr>`).join('')}</tbody></table></div>`);
  if (D.clarifications.length) add('b-clar', 'Clarifications', 'The basis of this budget.', `<div class="tbl-wrap"><table><tbody>${D.clarifications.map((e) => `<tr><td>${esc(e)}</td></tr>`).join('')}</tbody></table></div>`);
  add('b-team', 'Team and Next Step', D.teamNote || 'The principals stay on this project. You are never handed off.', `<div class="book-team">${D.team.map((t) => `<div><b>${esc(t.name)}</b><span>${esc(t.title)}</span></div>`).join('')}</div>${D.nextStep ? `<p style="margin-top:22px;font-size:17px">${esc(D.nextStep)}</p>` : ''}`);
  $('#bookIdx').innerHTML = `<a href="#b-summary">Summary</a>` + sections.map((s) => `<a href="#${s.id}">${esc(s.title)}</a>`).join('');
  $('#bookBody').innerHTML = `<p class="ph" id="b-summary">${esc(D.project.name)} · ${esc(D.project.address)}</p><h1>${esc(L.book)}</h1><p class="lede">${esc(D.bookLede || 'General conditions, fee and insurance each sit on their own line.')}</p>
    <div class="nums"><div><span class="k">Direct Cost</span><span class="n">${fmt(direct)}</span></div><div><span class="k">Markups</span><span class="n">${fmt(BASE - direct)}</span></div><div><span class="k">Base Budget</span><span class="n blue">${fmt(BASE)}</span></div><div><span class="k">${esc(D.stat?.[0] || 'Alternates')}</span><span class="n">${esc(D.stat?.[1] || D.alternates.length)}</span></div></div>
    ${sections.map((s) => `<h2 id="${s.id}">${esc(s.title)}</h2>${s.sub ? `<p>${esc(s.sub)}</p>` : ''}${s.html}`).join('\n')}
    <div class="book-foot"><span class="mark"><img src="${IMG('mc-m.png')}" width="320" height="271" alt="Montana Contracting">Montana Contracting Corp. · Congers, New York</span><span class="band">Since 1984 · NY + NJ + FL</span></div>`;
  const book = $('#book');
  const openBook = () => { book.hidden = false; document.body.classList.add('booked'); book.scrollTop = 0; };
  const closeBook = () => { book.hidden = true; document.body.classList.remove('booked'); };
  document.addEventListener('click', (e) => { if (e.target.closest('[data-open-book], #openBook')) openBook(); if (e.target.closest('#closeBook')) closeBook(); });
  addEventListener('keydown', (e) => { if (e.key === 'Escape' && !book.hidden) closeBook(); });
  syncAlts();

  // ---------------------------------------------------------------- the schedule chart
  // One playhead, driven by the scroll, moves through calendar time. Every date comes from schedule.json.
  const SCHED = (() => {
    const S = D.schedule; if (!S) return null;
    const DAY = 864e5, Td = (s) => Date.parse(s + 'T00:00:00');
    const T0 = Td(S.start), T1 = Td(S.end) + DAY, X = (t) => clamp01((t - T0) / (T1 - T0)), P = (t) => (X(t) * 100).toFixed(3) + '%';
    const MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const md = (t) => { const d = new Date(t); return MON[d.getMonth()].toUpperCase() + ' ' + d.getDate(); };
    const range = (a, b) => { const A = new Date(a), B = new Date(b); return A.getMonth() === B.getMonth() ? `${md(a)}–${B.getDate()}` : `${md(a)}–${md(b)}`; };
    const MOB = S.mob ? Td(S.mob) : T0, END = Td(S.keys || S.end) + DAY - 1;
    const KF = S.kf ? S.kf.map(([u, d]) => [u, Td(d)]) : [[0, T0], [0.04, T0], [0.9, END], [1, END]];
    const timeAt = (u) => { let i = 0; while (i < KF.length - 2 && u > KF[i + 1][0]) i++; const [u0, t0] = KF[i], [u1, t1] = KF[i + 1]; return t0 + (t1 - t0) * clamp01((u - u0) / (u1 - u0 || 1)); };
    const rows = S.rows.map((r) => ({ ...r, ts: Td(r.s), tf: Td(r.f) + DAY, hs: r.hold ? Td(r.hold.s) : 0, hf: r.hold ? Td(r.hold.f) + DAY : 0, ms: (r.ms || []).map((m) => ({ ...m, t: Td(m.d) })) }));
    const frac = (key, t) => { const r = rows.find((x) => x.key === key); return r ? clamp01((t - r.ts) / (r.tf - r.ts)) : 1; };
    const g = $('#gantt');
    if (!g) return { timeAt, frac, render() {}, layout() {} };
    let rule = '<div class="g-rule"><div></div><div class="g-tl">';
    const months = []; for (let d = new Date(T0); d.getTime() < T1; d.setMonth(d.getMonth() + 1)) months.push(new Date(d));
    for (const d of months) { const t = d.getTime(); if (t === T0 || d.getMonth() === 0) rule += `<span class="g-yr" style="left:${P(t)}">${d.getFullYear()}</span>`; rule += `<span class="g-mo" style="left:${P(t)}"><span class="f">${MON[d.getMonth()].toUpperCase()}</span><span class="s">${MON[d.getMonth()][0]}</span></span>`; }
    rule += '</div></div>';
    const grid = '<div class="g-grid">' + months.map((d) => `<i class="${d.getMonth() === 0 ? 'y' : ''}" style="left:${P(d.getTime())}"></i>`).join('') + '</div>';
    const tmpl = []; let body = '';
    for (const G of S.groups) {
      body += `<div class="g-row g-grp"><span>${esc(G.label)}<em>${esc(G.who || '')}</em></span></div>`; tmpl.push('17px');
      for (const r of rows.filter((x) => x.grp === G.key)) {
        let tl = ''; const bar = r.tf - r.ts > DAY && r.kind !== 'decision';
        if (bar) {
          let wx = '';
          if (r.wx) { let n = 0, d = new Date(r.tf - DAY); while (n < r.wx) { if (d.getDay() % 6) n++; if (n < r.wx) d.setDate(d.getDate() - 1); } wx = `<i class="g-wx" style="width:${((r.tf - d.getTime()) / (r.tf - r.ts) * 100).toFixed(2)}%"></i>`; }
          tl += `<i class="g-bar" data-b style="left:${P(r.ts)};width:${((X(r.tf) - X(r.ts)) * 100).toFixed(3)}%"><i class="g-fill"></i>${wx}</i>`;
          tl += `<span class="g-note" data-n="${r.ts}" data-x="${X(r.tf)}" data-x0="${X(r.ts)}">${range(r.ts, r.tf - DAY)}</span>`;
        }
        if (r.hold) { tl += `<i class="g-hold" data-h style="left:${P(r.hs)};width:${((X(r.hf) - X(r.hs)) * 100).toFixed(3)}%"><i class="g-fill"></i></i><span class="g-note" data-n="${r.hs}" data-x="${X(r.hf)}" data-x0="${X(r.hs)}" data-left="1">${esc(r.hold.label)}</span>`; }
        for (const m of r.ms) { tl += `<i class="g-ms${m.big ? ' big' : ''}" data-m="${m.t}" style="left:${P(m.t + (m.big ? DAY / 2 : 0))}"></i><span class="g-note ms${m.big ? ' big' : ''}" data-n="${m.t}" data-x="${X(m.t)}" data-x0="${X(m.t)}">${esc(m.label)}${m.big ? ' · ' + md(m.t) : ''}</span>`; }
        body += `<div class="g-row k-${r.kind || 'montana'}${r.crit ? ' crit' : ''}" data-k="${r.key}"><div class="g-lab"><span class="ln">${esc(r.name)}</span><span class="sn">${esc(r.short || r.name)}</span></div><div class="g-tl">${tl}</div></div>`;
        tmpl.push('minmax(0, 1fr)');
      }
    }
    g.innerHTML = rule + `<div class="g-body" style="grid-template-rows:${tmpl.join(' ')}">${grid}<svg class="g-thread" aria-hidden="true"></svg>${body}<div class="g-play"><span class="g-flag"></span></div></div>`;
    $('#shHeld').innerHTML = (S.held || []).map((h) => `<div data-t="${Td(h.at)}"><b>${esc(h.n)}</b><span>${esc(h.unit)}</span><span>${esc(h.note)}</span></div>`).join('');
    const rowEls = [...g.querySelectorAll('.g-row[data-k]')].map((el) => ({ el, r: rows.find((x) => x.key === el.dataset.k), bar: el.querySelector('[data-b] .g-fill'), hold: el.querySelector('[data-h] .g-fill'), ms: [...el.querySelectorAll('[data-m]')], notes: [...el.querySelectorAll('.g-note')] }));
    const heldEls = [...document.querySelectorAll('#shHeld [data-t]')];
    const flag = g.querySelector('.g-flag'), thread = g.querySelector('.g-thread'), gbody = g.querySelector('.g-body');
    const hud = { yr: $('#shYr'), date: $('#shDate'), now: $('#shNow'), wk: $('#shWk') };
    function layout() {
      const lab = g.querySelector('.g-row[data-k] .g-lab'); if (!lab) return;
      const Wd = gbody.clientWidth - lab.offsetWidth, H = gbody.clientHeight; if (Wd <= 0) return;
      thread.setAttribute('viewBox', `0 0 ${Wd} ${H}`);
      const crit = rowEls.filter((o) => o.r.crit).map((o) => { const y = o.el.offsetTop + o.el.offsetHeight / 2, r = o.r, solo = r.tf - r.ts <= DAY && r.hold; return { y, xs: (solo ? X(r.hs) : X(r.ts)) * Wd, xe: (solo ? X(r.hf) : r.tf - r.ts > DAY ? X(r.tf) : X(r.ts + DAY / 2)) * Wd }; });
      let d = '', dots = '';
      for (let i = 0; i < crit.length - 1; i++) { const A = crit[i], B = crit[i + 1];
        if (B.xs >= A.xe - 1) { d += `M${A.xe.toFixed(1)},${A.y.toFixed(1)}V${B.y.toFixed(1)}H${B.xs.toFixed(1)}`; dots += `<circle cx="${A.xe.toFixed(1)}" cy="${A.y.toFixed(1)}" r="2"/>`; }
        else { d += `M${B.xs.toFixed(1)},${A.y.toFixed(1)}V${B.y.toFixed(1)}`; dots += `<circle cx="${B.xs.toFixed(1)}" cy="${A.y.toFixed(1)}" r="2"/>`; } }
      thread.innerHTML = `<path d="${d}"/>${dots}`;
      for (const o of rowEls) {   // each note sits right of its bar; if blocked, left; if neither, hidden
        const els = [...o.el.querySelectorAll('.g-bar,.g-hold,.g-ms')], placed = [];
        for (const n of o.notes.slice().sort((a, b) => +a.dataset.x - +b.dataset.x)) {
          n.classList.remove('l', 'x');
          const own = n.previousElementSibling, w = n.offsetWidth, x = +n.dataset.x * Wd, x0 = +n.dataset.x0 * Wd;
          const items = els.filter((e) => e !== own).map((e) => [e.offsetLeft, e.offsetLeft + e.offsetWidth]);
          const clear = ([l, r]) => l > -2 && r < Wd + 6 && !items.some(([a, b]) => a < r && b > l) && !placed.some(([a, b]) => a < r + 6 && b > l - 6);
          const R = [x + 5, x + 9 + w], Lf = [x0 - 9 - w, x0 - 5];
          const hit = (n.dataset.left ? [['l', Lf], ['r', R]] : [['r', R], ['l', Lf]]).find(([, c]) => clear(c));
          if (!hit) { n.classList.add('x'); continue; }
          n.style.left = ((hit[0] === 'r' ? x : x0) / Wd * 100) + '%'; if (hit[0] === 'l') n.classList.add('l'); placed.push(hit[1]);
        }
      }
    }
    const order = Object.fromEntries(S.groups.map((G, i) => [G.key, i + 1]));
    function nowLabel(t) {
      if (S.keys && t >= Td(S.keys)) return 'Keys';
      let best = null;
      for (const r of rows) { if (r.kind === 'decision') continue; const sc = order[r.grp] * 10 + (r.crit ? 5 : 0); if (t >= r.ts && t < r.tf && (!best || sc > best.sc || (sc === best.sc && r.ts > best.r.ts))) best = { r, sc }; }
      return best ? best.r.name : t < MOB ? 'Before We Mobilize' : 'On Site';
    }
    let lastKey = '';
    function render(u) {
      const t = timeAt(u), key = Math.round(t / 36e5); if (key === lastKey) return t; lastKey = key;
      const x = X(t); g.style.setProperty('--x', x.toFixed(5)); flag.textContent = md(t); flag.classList.toggle('l', x > 0.9);
      for (const o of rowEls) { const r = o.r;
        o.el.classList.toggle('on', t >= (r.kind === 'decision' && r.ms[0] ? r.ms[0].t : r.ts));
        if (o.bar) o.bar.style.setProperty('--f', clamp01((t - r.ts) / (r.tf - r.ts)).toFixed(4));
        if (o.hold) o.hold.style.setProperty('--f', clamp01((t - r.hs) / (r.hf - r.hs)).toFixed(4));
        for (const m of o.ms) m.classList.toggle('on', t >= +m.dataset.m);
        for (const n of o.notes) n.classList.toggle('on', t >= +n.dataset.n); }
      for (const h of heldEls) h.classList.toggle('on', t >= +h.dataset.t);
      const d = new Date(t);
      hud.yr.textContent = d.getFullYear(); hud.date.textContent = String(d.getMonth() + 1).padStart(2, '0') + '.' + String(d.getDate()).padStart(2, '0');
      hud.now.textContent = nowLabel(t);
      hud.wk.textContent = t < MOB ? 'Before We Mobilize' : S.weeks ? `Week ${Math.min(S.weeks, Math.floor((t - MOB) / (7 * DAY)) + 1)} of ${S.weeks}` : 'On Site';
      return t;
    }
    addEventListener('resize', () => { layout(); lastKey = ''; });
    requestAnimationFrame(() => { layout(); render(0); });
    return { timeAt, frac, render, layout };
  })();

  // ---------------------------------------------------------------- per-frame: stops, scrims, ticks
  const stopEls = [...document.querySelectorAll('.stop')], tickEls = [...document.querySelectorAll('[data-go]')];
  const scrimEls = { l: $('#scrimL'), r: $('#scrimR'), t: $('#scrimT') }, scrimNow = { l: -1, r: -1, t: -1 }, scrimFor = { l: -1, r: -1, t: -1 };
  addEventListener('resize', () => { scrimFor.l = scrimFor.r = scrimFor.t = -1; });
  const sbarEls = [...document.querySelectorAll('#strataBar i')]; sbarEls.forEach((el, i) => { el.style.transitionDelay = `${i * 0.09}s`; });
  const SCH = STOPS.find((s) => s.type === 'schedule'), BUD = STOPS.find((s) => s.type === 'budget');
  const schedU = (p) => (SCH ? clamp01((p - SCH.a) / (SCH.b - SCH.a)) : 0);
  let lastActive = -1, sbarOn = false, veilNow = -1;
  function renderStops(p) {
    let active = 0, sheet = false; const sc = { l: 0, r: 0, t: 0 }, who = { l: -1, r: -1, t: -1 };
    STOPS.forEach((s, i) => {
      const el = stopEls[i], fin = 0.012;
      const o = i === 0 ? 1 - clamp01((p - s.b) / fin) : clamp01((p - s.a) / fin) * (s.b >= 1 ? 1 : 1 - clamp01((p - s.b) / fin));
      const os = o.toFixed(3);
      if (el.style.opacity !== os) { el.style.opacity = os; el.style.visibility = o > 0.01 ? 'visible' : 'hidden'; el.style.transform = `translateY(${((1 - o) * 18).toFixed(1)}px)`; }
      if (p >= s.s0 - 0.001) active = i;
      if (s.type === 'schedule' && o > 0.001) {
        const u = schedU(p);
        // the schedule gets its own page by default; schedule_model: true lets the model rebuild above the chart
        const veil = NARROW() || !D.scheduleModel ? 1 : u < 0.03 ? 1 : u < 0.07 ? 1 - ease((u - 0.03) / 0.04) : u < 0.95 ? 0 : ease(clamp01((u - 0.95) / 0.04));
        if (Math.abs(veil - veilNow) > 0.002) { veilNow = veil; el.style.setProperty('--veil', veil.toFixed(3)); }
        sheet = o > 0.999 && veil > 0.999;
        SCHED && SCHED.render(u);
      }
      const oS = i === 0 ? 1 - clamp01((p - s.b) / 0.03) : clamp01((p - s.a + 0.012) / 0.03) * (s.b >= 1 ? 1 : 1 - clamp01((p - s.b - 0.006) / 0.03));
      const v = oS * (s.scrimA ?? 1); if (v > sc[s.scrim]) { sc[s.scrim] = v; who[s.scrim] = i; }
    });
    for (const k in sc) if (Math.abs(sc[k] - scrimNow[k]) > 0.004) { scrimNow[k] = sc[k]; scrimEls[k].style.opacity = sc[k].toFixed(3); }
    for (const k in who) if (who[k] !== scrimFor[k] && who[k] >= 0) { scrimFor[k] = who[k]; scrimEls[k].style.setProperty('--cw', stopEls[who[k]].offsetWidth + 'px'); }
    if (active !== lastActive) { lastActive = active; tickEls.forEach((b, i) => { b.classList.toggle('here', i === active); b.setAttribute('aria-current', i === active ? 'step' : 'false'); }); $('#mobileStop').textContent = STOPS[active].name; }
    ROOT.classList.toggle('moved', p > 0.012);
    if (BUD) { const nOn = p > BUD.a - 0.002 && p < BUD.b + 0.02; if (nOn !== sbarOn) { sbarOn = nOn; sbarEls.forEach((el) => { el.style.width = nOn ? el.dataset.w + '%' : '0%'; }); } }
    return sheet;
  }
  tickEls.forEach((b, i) => b.addEventListener('click', () => {
    const s = STOPS[i], pp = i === 0 ? 0 : i === STOPS.length - 1 ? 1 : s.s0 + s.len * 0.5;
    scrollTo({ top: pp * (document.documentElement.scrollHeight - innerHeight), behavior: REDUCED ? 'auto' : 'smooth' });
  }));
  window.PAGE = { renderStops, schedU, schedTime: SCHED ? SCHED.timeAt : null, schedFrac: SCHED ? SCHED.frac : () => 1 };

  // ---------------------------------------------------------------- no 3D: renders or drawings behind the copy
  if (D.model.mode === 'images') {
    ROOT.classList.add('stills'); if (D.model.fit === 'cover') ROOT.classList.add('cover');
    const imgs = [...document.querySelectorAll('#stills img')];
    // phone renders are framed for a tall screen; swap them in below the phone breakpoint
    let narrowNow = null;
    const pick = () => { const n = NARROW(); if (n === narrowNow) return; narrowNow = n; imgs.forEach((im) => { const want = n && im.dataset.phone ? im.dataset.phone : im.dataset.desk || im.src; if (!im.dataset.desk) im.dataset.desk = im.src; if (im.src !== want) im.src = want; }); };
    pick(); addEventListener('resize', pick);
    const DUSK_I = STOPS.findIndex((s) => s.dusk);
    let pT = 0, pN = 0, cur = -1;
    const read = () => { const max = document.documentElement.scrollHeight - innerHeight; pT = max > 0 ? clamp01(scrollY / max) : 0; };
    addEventListener('scroll', read, { passive: true }); read(); pN = pT;
    window.__jump = (p) => { pT = pN = p; };
    window.__stops = STOPS.map((s) => ({ id: s.id, s0: s.s0, s1: s.s1, a: s.a, b: s.b }));
    const frame = () => {
      pN += (pT - pN) * (REDUCED ? 1 : 0.12);
      let k = 0; STOPS.forEach((s, i) => { if (pN >= s.s0 - 0.001) k = i; });
      const st = STOPS[k];
      // a stop can hold several stills (a build stop, one per phase): they step through as the stop scrolls
      let still = st.still ?? (k ? cur : 0);
      if (Array.isArray(still)) { const u = clamp01((pN - st.a) / (st.b - st.a || 1)); still = still[Math.min(still.length - 1, Math.floor(u * still.length * 1.08))]; }
      const img = Math.max(0, Math.min(imgs.length - 1, still));
      ROOT.dataset.side = st.type === 'hero' ? 't' : st.side;
      ROOT.classList.toggle('dusk', DUSK_I >= 0 && k >= DUSK_I);
      if (img !== cur) { cur = img; imgs.forEach((im, i) => im.classList.toggle('on', i === img)); }
      if (imgs[img]) imgs[img].style.transform = `scale(${(1.03 + 0.06 * clamp01((pN - st.s0) / st.len)).toFixed(4)})`;
      renderStops(pN); requestAnimationFrame(frame);
    };
    ROOT.classList.add('ready'); window.__done = true; requestAnimationFrame(frame);
  }
  // portraits decode before their stop arrives
  const warm = () => document.querySelectorAll('.pp img').forEach((im) => { if (im.decode) im.decode().catch(() => {}); });
  if (document.readyState === 'complete') warm(); else addEventListener('load', warm);
  try { const c = document.createElement('canvas'); if (!(c.getContext('webgl2') || c.getContext('webgl'))) throw 0; } catch (e) { if (D.model.mode !== 'images') ROOT.classList.add('no-webgl'); }
})();
