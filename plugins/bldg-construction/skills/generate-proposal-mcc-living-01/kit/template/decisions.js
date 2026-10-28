// ---------------------------------------------------------------- the decision list
// Every open choice on the house: the alternates and the selection dates the factory needs.
// In the shared Montana link each answer saves for everyone (db: decisions/<item>, log/<auto>).
// Anywhere else (Netlify, a saved file) it works for this visit and can be emailed to Montana.
(() => {
  const D = window.PROPOSAL, M = window.MONEY, CFG = D.decisions || {};
  if (CFG.enabled === false) return;
  const $ = (s) => document.querySelector(s);
  const fmt = (n) => (n < 0 ? '-$' : '$') + Math.round(Math.abs(n)).toLocaleString('en-US');
  const esc = (s) => String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const LD = (s) => new Date(s + 'T00:00:00').toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
  const when = (iso) => { const d = new Date(iso); return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) + ', ' + d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' }); };
  const ALT_STATES = [['include', 'Include'], ['notnow', 'Not Now'], ['discuss', 'Discuss']];
  const SEL_STATES = [['confirmed', 'Confirmed'], ['open', 'Open']];
  const VERB = { include: 'included', notnow: 'set aside', discuss: 'marked for discussion', confirmed: 'confirmed', open: 'reopened', note: 'added a note to' };
  const dec = D.schedule ? D.schedule.rows.filter((r) => r.kind === 'decision').flatMap((r) => r.ms || []) : [];
  const ITEMS = [
    ...D.alternates.map((a) => ({ id: 'alt-' + a.id, kind: 'alt', alt: a.id, title: a.title, value: a.value, note: a.note })),
    ...dec.map((m, i) => ({ id: 'sel-' + (i + 1), kind: 'sel', title: m.label.replace(', ', ' and ') + ' Selections', due: m.d })),
  ];
  const byId = Object.fromEntries(ITEMS.map((x) => [x.id, x]));
  const state = {};            // id -> { s, note, by, at }
  let log = [], db = null, user = null, me = null, canWrite = false, mode = 'local';

  // ---- markup
  const seg = (it) => (it.kind === 'alt' ? ALT_STATES : SEL_STATES).map(([k, l]) => `<button type="button" data-s="${k}" aria-pressed="false">${l}</button>`).join('');
  const row = (it) => `<div class="dec-row" data-id="${it.id}">
      <div class="t">${esc(it.title)}<span class="m">${it.kind === 'sel' ? 'Needed by ' + esc(LD(it.due)) : esc((it.note || '').replace(/\.$/, ''))}</span></div>
      <div class="v${it.kind === 'alt' && !it.value ? ' np' : ''}">${it.kind === 'sel' ? '' : it.value ? (it.value > 0 ? '+' : '') + fmt(it.value) : 'Not Priced'}</div>
      <div class="dec-ctl"><span class="seg" role="group" aria-label="${esc(it.title)}">${seg(it)}</span><input class="dec-note" type="text" maxlength="400" placeholder="${esc(CFG.placeholder || 'Add a note for Montana')}" aria-label="Note on ${esc(it.title)}"></div>
      <div class="dec-who"></div></div>`;
  $('#decBody').innerHTML = `
    <p class="ph" id="d-summary">${esc(D.project.name)} · ${esc(D.project.address)}</p>
    <h1>Decision List</h1>
    <p class="lede">${esc(CFG.lede || 'Every open choice on the project, with its price and the date it is needed.')}</p>
    <p class="dec-status" id="decStatus"><i></i><span>Loading</span></p>
    <div class="nums">
      <div><span class="k">Base Budget</span><span class="n">${fmt(M.base)}</span></div>
      <div><span class="k">Included Alternates</span><span class="n" id="dIncl">$0</span></div>
      <div><span class="k">Working Total</span><span class="n blue" id="dTotal">${fmt(M.base)}</span></div>
      <div><span class="k">Open Decisions</span><span class="n" id="dOpen">${ITEMS.length}</span></div>
    </div>
    <h2 id="d-alts">Alternates</h2><p>Priced with markups. Include adds it to the working total.</p>
    ${ITEMS.filter((x) => x.kind === 'alt').map(row).join('')}
    ${dec.length ? `<h2 id="d-sel">Selections</h2><p>The dates the trades need answers, from the preliminary schedule.</p>${ITEMS.filter((x) => x.kind === 'sel').map(row).join('')}` : ''}
    <h2 id="d-log">Activity</h2><p>Every answer, newest first.</p>
    <ul class="dec-log" id="decLog"><li class="none">No decisions yet.</li></ul>
    <div class="dec-send"><a class="btn" id="decMail" href="#">Email This List to Montana</a></div>
    <div class="book-foot"><span class="mark"><img src="${(D.img && D.img['mc-m.png']) || ''}" width="320" height="271" alt="Montana Contracting">Montana Contracting Corp. · Congers, New York</span><span class="band">Since 1984 · NY + NJ + FL</span></div>`;
  const rows = Object.fromEntries([...document.querySelectorAll('.dec-row')].map((el) => [el.dataset.id, el]));

  // ---- render from state
  async function render() {
    let incl = 0, open = 0;
    for (const it of ITEMS) {
      const st = state[it.id] || {}, el = rows[it.id];
      el.querySelectorAll('.seg button').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.s === st.s)));
      const n = el.querySelector('.dec-note'); if (document.activeElement !== n) n.value = st.note || '';
      n.readOnly = !canWrite && mode === 'shared'; el.classList.toggle('ro', !canWrite && mode === 'shared');
      if (it.kind === 'alt' && st.s === 'include' && it.value) incl += it.value;
      if (!st.s || st.s === 'discuss' || st.s === 'open') open++;
    }
    $('#dIncl').textContent = (incl > 0 ? '+' : '') + fmt(incl);
    $('#dTotal').textContent = fmt(M.base + incl);
    $('#dOpen').textContent = `${open} of ${ITEMS.length}`;
    $('#decCount').textContent = open ? String(open) : '';
    // names resolve at render time from ids; never stored
    const ids = [...new Set([...Object.values(state).map((x) => x.by), ...log.map((x) => x.by)].filter(Boolean))];
    const ps = user && ids.length ? await user.profiles(ids) : {};
    const nm = (id) => (mode !== 'shared' ? 'You' : (id && ps[id] && ps[id].name) || (id && me && id === me ? 'You' : 'Someone'));
    for (const it of ITEMS) { const st = state[it.id]; rows[it.id].querySelector('.dec-who').textContent = st && st.at ? `${nm(st.by)} · ${when(st.at)}` : ''; }
    $('#decLog').innerHTML = log.length ? log.slice(0, 25).map((e) => { const it = byId[e.item]; if (!it) return ''; return `<li>${esc(nm(e.by))} ${esc(VERB[e.s] || 'updated')} ${esc(it.title)}<span>${esc(when(e.at))}</span></li>`; }).join('') : '<li class="none">No decisions yet.</li>';
    mailLink();
  }
  function mailLink() {
    const lines = [D.project.name + ', Decision List', ''];
    for (const it of ITEMS) {
      const st = state[it.id] || {}, lab = (it.kind === 'alt' ? ALT_STATES : SEL_STATES).find(([k]) => k === st.s);
      lines.push(`${it.title}: ${lab ? lab[1] : 'Open'}${it.kind === 'alt' && it.value ? ' (' + fmt(it.value) + ')' : ''}${st.note ? ', note: ' + st.note : ''}`);
    }
    lines.push('', 'Working total: ' + $('#dTotal').textContent);
    $('#decMail').href = 'mailto:' + (CFG.email || 'estimating@montanacontracting.com') + '?subject=' + encodeURIComponent(D.project.name + ' Decision List') + '&body=' + encodeURIComponent(lines.join('\n'));
  }
  function status(cls, text) { const s = $('#decStatus'); s.className = 'dec-status ' + cls; s.querySelector('span').textContent = text; }

  // ---- writes: one per user action, one at a time per item
  const busy = {};
  async function save(id, patch, verb) {
    const prev = state[id] || {};
    const next = { s: prev.s || null, note: prev.note || '', ...patch, by: me, at: new Date().toISOString() };
    state[id] = next;
    if (mode !== 'shared') { log.unshift({ item: id, s: verb, by: null, at: next.at }); render(); return; }
    render();
    if (!canWrite) return;
    if (busy[id]) await busy[id];
    busy[id] = (async () => {
      try {
        await db.doc('decisions/' + id).set(next);
        await db.collection('log').add({ item: id, s: verb, by: me, at: next.at });
      } catch (e) {
        if (e && e.code === 'invalid_argument') { canWrite = false; status('ro', 'View only. Ask Montana for edit access to record decisions.'); }
        else status('ro', 'Not saved. Check the connection and try again.');
        render();
      }
    })();
    await busy[id]; busy[id] = null;
  }
  document.addEventListener('click', (e) => {
    const b = e.target.closest('.dec-row .seg button'); if (!b) return;
    if (mode === 'shared' && !canWrite) return;
    const id = b.closest('.dec-row').dataset.id, cur = (state[id] || {}).s;
    const s = cur === b.dataset.s ? null : b.dataset.s;
    save(id, { s }, s || 'open');
    // an included alternate shows on the house
    const it = byId[id];
    if (it.kind === 'alt' && window.ALT_ON) { if (s === 'include') window.ALT_ON.add(it.alt); else window.ALT_ON.delete(it.alt); document.querySelectorAll(`input[data-alt="${it.alt}"]`).forEach((x) => { x.checked = s === 'include'; }); document.dispatchEvent(new CustomEvent('alts', { detail: [...window.ALT_ON] })); }
  });
  document.addEventListener('change', (e) => {
    const n = e.target.closest && e.target.closest('.dec-note'); if (!n) return;
    const id = n.closest('.dec-row').dataset.id, v = n.value.trim();
    if (v === ((state[id] || {}).note || '')) return;
    save(id, { note: v }, 'note');
  });

  // ---- open and close
  const open = () => { $('#decs').hidden = false; document.body.classList.add('booked'); $('#decs').scrollTop = 0; $('#closeDecs').focus(); };
  const close = () => { $('#decs').hidden = true; if ($('#book').hidden) document.body.classList.remove('booked'); };
  window.__openDecisions = open;
  $('#openDecs').addEventListener('click', open);
  document.querySelectorAll('[data-open-decs]').forEach((b) => b.addEventListener('click', open));
  $('#closeDecs').addEventListener('click', close);
  addEventListener('keydown', (e) => { if (e.key === 'Escape' && !$('#decs').hidden) close(); });

  // ---- connect: shared in the Montana link, this visit only anywhere else
  status('', 'Answers stay in this browser for this visit. Use the email button to send them to Montana.');
  render();
  (async () => {
    if (!window.claude || !window.claude.use) return;
    db = await window.claude.use('db'); user = await window.claude.use('user');
    if (!db) return;
    me = user ? await user.id() : null;
    const w = user ? await user.can('data.write') : null;
    canWrite = w !== false; mode = 'shared';
    status(canWrite ? 'live' : 'ro', canWrite ? 'Saved for everyone on this link, as you answer.' : 'View only. Ask Montana for edit access to record decisions.');
    let first = true;
    db.collection('decisions').onSnapshot((snap) => {
      for (const d of snap.docs) { const v = d.data(); if (byId[d.id]) state[d.id] = { s: v.s || null, note: v.note || '', by: v.by || null, at: v.at || null }; }
      for (const c of snap.docChanges()) if (c.type === 'removed') delete state[c.doc.id];
      if (first) { first = false; for (const it of ITEMS) if (it.kind === 'alt' && state[it.id] && state[it.id].s === 'include' && window.ALT_ON) window.ALT_ON.add(it.alt); document.querySelectorAll('input[data-alt]').forEach((x) => { x.checked = window.ALT_ON.has(x.dataset.alt); }); document.dispatchEvent(new CustomEvent('alts', { detail: [...window.ALT_ON] })); }
      render();
    }, () => status('ro', 'Live updates stopped. Reload to see the latest answers.'));
    db.collection('log').orderBy('at', 'desc').limit(40).onSnapshot((snap) => { log = snap.docs.map((d) => d.data()); render(); }, () => {});
  })();
})();
