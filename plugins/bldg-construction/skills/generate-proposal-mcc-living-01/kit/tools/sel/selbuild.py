"""Selections for the website presentation (kit v1.7): one card per element, opened from a point on the model.

build.py calls, after ALT_ROWS / VE_ROWS / LINES are known:
    SEL = selbuild.resolve(json.load(open(<job>/selections.json)), ctx)     # prices from the workbook, stops if anything does not tie
    selbuild.assets(SEL, ctx)                                               # images into site/assets/sel/
    DATA['sel'] = selbuild.data(SEL, ctx);  html = selbuild.section(SEL, ctx, kick)

ctx is a dict: C, die, money, E, ws (Estimate sheet), LINES, find_rows, code_rows, ALT_ROWS, VE_ROWS, ALTS, VES, BASE, CB (job), A (site assets),
HERO (photo the crop: refs read, e.g. hero/blejer_nw.jpg), OP (overhead and profit rate as a Decimal, 0.15).

selections.json, per element:
  options: {"id", "view", "at": [x%, y%], "mode": "options", "name", "where", "carried", "options": [{"id", "name", "ref": "ALT 11" | "VE-2", "img", "note"}]}
           the first option is what the budget carries (no ref). "section": true on a driveway option paints the site view's section only.
  rate:    {"mode": "rate", "unit": "SF" | "LF", "base", "min", "max", "step", "rows": [Estimate item starts], "factor": waste, "check_rate": bool,
            "marks": [{"v", "label", "ref"}]}  per unit = sum(row qty) x factor x (1 + OP). A mark with a ref must equal that item to the cent.
           unit "LUMP": "codes": [cost codes]; base = their total, per dollar = 1 + OP.
  img: "sw:<name>" (tools/sel/swatches.py output in <job>/sel/), "crop:hero:x0,y0,x1,y1" or "crop:<sel image stem>:x0,y0,x1,y1" (fractions), "" = a labelled placeholder.
"""
import hashlib, os
from decimal import Decimal as D
from PIL import Image

GROUND = (244, 245, 248)   # the page's off-white, under the RGBA model renders


def _defaults(x):   # a lean build.py may not define these; read them from LINES the same way the full one does
    L = x['LINES']
    x.setdefault('find_rows', lambda *starts: [r for r, l in L.items() if l['item'].startswith(starts)])
    x.setdefault('code_rows', lambda *pre: [r for r, l in L.items() if l['code'].startswith(pre)])
    x.setdefault('VE_ROWS', {}); x.setdefault('OP', D('0.15'))


def resolve(S, x):
    _defaults(x)
    C, die = x['C'], x['die']
    def ref_value(ref):
        kind, _, n = ref.replace('-', ' ').partition(' ')
        n = int(n)
        rows = x['ALT_ROWS'] if kind.upper() == 'ALT' else x['VE_ROWS'] if kind.upper() == 'VE' else None
        if rows is None or n not in rows: die(f'selections: {ref} is not in the workbook')
        return C(rows[n])
    refmap = {}
    views = S['views']
    for k, e in enumerate(S['elements']):
        e['n'] = k + 1
        if e['view'] not in views: die(f'selections: {e["id"]} is on an unknown view {e["view"]}')
        if e['mode'] == 'options':
            if e['options'][0].get('ref'): die(f'selections: the first option of {e["id"]} must be what the budget carries')
            for o in e['options']:
                o['v'] = ref_value(o['ref']) if o.get('ref') else C(0)
                if o.get('ref'): refmap[_alt_id(o['ref'])] = [e['id'], o['id']]
        elif e['mode'] == 'rate':
            op1 = 1 + x['OP']
            if e['unit'] == 'LUMP':
                rows = x['code_rows'](*e['codes'])
                if not rows: die(f'selections: no rows for {e["codes"]}')
                e['base'] = C(sum(x['LINES'][r]['v'] for r in rows)); e['per'] = C(op1)
            else:
                rows = x['find_rows'](*e['rows'])
                qty = sum(D(str(x['ws'].cell(r, 3).value)) for r in rows)
                e['qty'] = qty
                e['per'] = C(qty * D(str(e.get('factor', 1))) * op1)
                if e.get('check_rate'):
                    for r in rows:
                        rate = D(str(x['ws'].cell(r, 5).value))
                        if abs(rate - D(str(e['base'])) * D(str(e.get('factor', 1)))) > D('0.005'):
                            die(f'selections: {e["id"]} base {e["base"]} x {e.get("factor", 1)} does not match row {r} rate {rate}')
            for m in e.get('marks', []):
                if m.get('ref'):
                    got, want = C((D(str(m['v'])) - D(str(e['base']))) * e['per']), ref_value(m['ref'])
                    if got != want: die(f'selections: {e["id"]} at {m["v"]} gives {got}, {m["ref"]} is {want}')
                    refmap[_alt_id(m['ref'])] = [e['id'], m['v']]
        else:
            die(f'selections: unknown mode {e["mode"]}')
    S['refmap'] = refmap
    return S


def _alt_id(ref):   # the ids the Alternates section uses: "11" for ALT 11, "ve2" for VE-2
    kind, _, n = ref.replace('-', ' ').partition(' ')
    return n if kind.upper() == 'ALT' else 've' + n


def _flat(src, width):
    im = Image.open(src)
    if im.mode in ('RGBA', 'LA', 'P'):
        im = im.convert('RGBA'); bg = Image.new('RGBA', im.size, GROUND + (255,)); bg.alpha_composite(im); im = bg
    im = im.convert('RGB')
    if width and im.width > width: im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    return im


def assets(S, x):
    out = os.path.join(x['A'], 'sel'); os.makedirs(out, exist_ok=True)
    sel = os.path.join(x['CB'], 'sel')
    def save(im, name, q=82):
        im.save(os.path.join(out, name), 'JPEG', quality=q, optimize=True, progressive=True)
        return 'assets/sel/' + name
    def img(spec):
        if not spec: return ''
        if spec.startswith('sw:'):
            return save(_flat(os.path.join(sel, f'sw_{spec[3:]}.jpg'), 480), f'sw_{spec[3:]}.jpg', 80)
        if spec.startswith('crop:'):
            _, src, box = spec.split(':', 2)
            path = x['HERO'] if src == 'hero' else os.path.join(sel, src + '.png')
            im = _flat(path, None); f = [float(v) for v in box.split(',')]
            c = im.crop((round(f[0] * im.width), round(f[1] * im.height), round(f[2] * im.width), round(f[3] * im.height)))
            if c.width > 720: c = c.resize((720, round(c.height * 720 / c.width)), Image.LANCZOS)
            return save(c, 'crop_' + hashlib.md5(spec.encode()).hexdigest()[:8] + '.jpg')
        return save(_flat(os.path.join(x['CB'], spec), 1600), os.path.basename(spec).rsplit('.', 1)[0] + '.jpg')
    for v in S['views'].values():
        if v.get('img'): v['src'] = img(v['img'])
        if v.get('plan'): v['src'] = save(_flat(os.path.join(x['CB'], v['plan']), None), 'site_plan.jpg', 86)
        v['swap_src'] = {el: {k: img(p) for k, p in sw.items()} for el, sw in v.get('swap', {}).items()}
    for e in S['elements']:
        if e['mode'] == 'options':
            for o in e['options']: o['src'] = img(o.get('img', ''))
        else:
            e['src'] = img(e.get('img', ''))


def data(S, x):
    s = lambda v: str(v)
    els = []
    for e in S['elements']:
        d = {k: e[k] for k in ('id', 'n', 'view', 'at', 'mode', 'name', 'where', 'carried') if k in e}
        if e['mode'] == 'options':
            d['options'] = [{'id': o['id'], 'name': o['name'], 'v': s(o['v']), 'src': o['src'], 'ph': o.get('ph', 'Supplier Photo'),
                             'note': o['note'], 'section': bool(o.get('section'))} for o in e['options']]
        else:
            d.update({'unit': e['unit'], 'base': s(e['base']), 'min': e['min'], 'max': e['max'], 'step': e['step'], 'per': s(e['per']),
                      'label': e['label'], 'after': e.get('after', ''), 'src': e['src'], 'marks': e.get('marks', [])})
        els.append(d)
    views = [{'id': k, 'label': v['label'], 'src': v.get('src', ''), 'swap': v.get('swap_src', {}), 'el': v.get('el', '')} for k, v in S['views'].items()]
    return {'els': els, 'views': views + [{'id': 'list', 'label': S.get('list_label', 'List')}], 'refmap': S['refmap'],
            'form': S.get('send', {}).get('form', 'selections'), 'subject': S.get('send', {}).get('email_subject', 'Selections')}


def _site_svg(v, E):
    pts = v['path']
    seg = [((pts[i + 1][0] - pts[i][0]) ** 2 + (pts[i + 1][1] - pts[i][1]) ** 2) ** 0.5 for i in range(len(pts) - 1)]
    L = sum(seg)
    def at(t):
        d, acc = t * L, 0
        for i, l in enumerate(seg):
            if acc + l >= d:
                u = (d - acc) / l
                return (pts[i][0] + u * (pts[i + 1][0] - pts[i][0]), pts[i][1] + u * (pts[i + 1][1] - pts[i][1])), i
            acc += l
        return tuple(pts[-1]), len(pts) - 2
    path = lambda p: 'M' + ' L'.join(f'{a:.0f} {b:.0f}' for a, b in p)
    full = path(pts)
    sec = v.get('section')
    sub = ''
    if sec:
        (a1, i1), (a2, i2) = at(sec['from']), at(sec['to'])
        sub = path([a1] + [tuple(p) for p in pts[i1 + 1:i2 + 1]] + [a2])
    w, h = v['size']; wd = v.get('width', 35)
    house = ' '.join(f'{a},{b}' for a, b in v.get('house', []))
    labels = ''.join(f'<text x="{lx}" y="{ly}" font-size="{fs}" class="sx-lab">{E(t)}</text>' for t, lx, ly, fs in v.get('labels', []))
    if sec and sec.get('label'): labels += f'<text x="{sec["label_at"][0]}" y="{sec["label_at"][1]}" font-size="22" class="sx-lab sx-lab--mute">{E(sec["label"])}</text>'
    return (f'<svg class="sx-site" viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="{E(v.get("alt", "Site plan"))}">'
            f'<defs id="sx-pats"></defs><image href="{v["src"]}" x="0" y="0" width="{w}" height="{h}"/>'
            f'<path d="{full}" class="sx-edge" stroke-width="{wd + 7}"/><path d="{full}" class="sx-drive" id="sx-drive" stroke-width="{wd}"/>'
            + (f'<path d="{sub}" class="sx-drive sx-drive--sec" id="sx-sec" stroke-width="{wd}"/>' if sub else '')
            + (f'<polygon points="{house}" class="sx-house"/>' if house else '') + labels + '</svg>')


def section(S, x, kick):
    E, money = x['E'], x['money']
    stage = ''
    for k, v in S['views'].items():
        inner = _site_svg(v, E) if v.get('plan') else f'<img src="{v["src"]}" alt="{E(v["alt"])}" decoding="async" loading="lazy">'
        stage += f'<div class="sx-view" data-view="{k}" hidden>{inner}</div>'
    stage += '<div class="sx-view sx-list" data-view="list" hidden><div class="sx-list__in" id="sx-list"></div></div>'
    pills = ''.join(f'<button type="button" class="pill" data-view="{k}" aria-pressed="false">{E(v["label"])}</button>' for k, v in S['views'].items())
    pills += f'<button type="button" class="pill" data-view="list" aria-pressed="false">{E(S.get("list_label", "List"))}</button>'
    form = S.get('send', {}).get('form', 'selections')
    return f'''
<section class="selx" id="selections" aria-label="Selections">
  <div class="wrap">
    {kick("03 / Selections")}
    <div class="selx__top">
      <div><h2 class="sec-title" data-r>Your Selections</h2>
      <p class="selx__lede" data-r="up">Select a point on the house. Each choice shows what it does to the budget. Requests go to Montana, and nothing changes until we confirm it in writing.</p></div>
      <div class="pills selx__pills" role="group" aria-label="Views">{pills}</div>
    </div>
    <div class="selx__grid">
      <div class="selx__left">
        <div class="sx-stage" id="sx-stage">{stage}<div class="sx-pins" id="sx-pins"></div></div>
        <div class="sx-bar">
          <div><span class="lab">Budget Today</span><b class="num">{money(x["BASE"])}</b></div>
          <div><span class="lab">Requested</span><b class="num sx-req" id="sx-req">$0.00</b></div>
          <div><span class="lab">If Montana Confirms</span><b class="num" id="sx-if">{money(x["BASE"])}</b></div>
          <button type="button" class="btn btn--navy sx-send" id="sx-send" disabled><span>Send to Montana</span></button>
        </div>
      </div>
      <aside class="sx-card" id="sx-card" aria-live="polite"></aside>
    </div>
  </div>
</section>
{sheet(S, E)}'''


def sheet(S, E):
    """The send sheet and the hidden Netlify form. Every build has it, with or without selections, so the Alternates switches can be sent."""
    form = (S or {}).get('send', {}).get('form', 'selections')
    return f'''<form name="{E(form)}" method="POST" data-netlify="true" netlify-honeypot="company" hidden aria-hidden="true">
  <input type="hidden" name="form-name" value="{E(form)}"><input name="job"><input name="name"><input name="email"><input name="role"><input name="company">
  <textarea name="note"></textarea><textarea name="requests"></textarea><input name="change"><input name="total"><textarea name="data"></textarea>
</form>
<div class="sxs" id="sxs" hidden>
  <div class="sxs__bg" data-close></div>
  <div class="sxs__panel" role="dialog" aria-modal="true" aria-labelledby="sxs-h">
    <button type="button" class="sxs__x" data-close aria-label="Close">Close</button>
    <h3 id="sxs-h">Send to Montana</h3>
    <div class="sxs__list" id="sxs-list"></div>
    <form class="sxs__form" id="sxs-form">
      <label><span>Your Name</span><input name="name" autocomplete="name" required></label>
      <label><span>Email</span><input name="email" type="email" autocomplete="email"></label>
      <label><span>You Are</span><select name="role"><option>Owner</option><option>Architect</option><option>Other</option></select></label>
      <label class="wide"><span>Note</span><textarea name="note" rows="3"></textarea></label>
      <button type="submit" class="btn btn--navy"><span>Send Requests</span></button>
    </form>
    <div class="sxs__done" id="sxs-done" hidden></div>
  </div>
</div>'''
