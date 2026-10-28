#!/usr/bin/env python3
"""Build a Montana bid presentation from a project folder.

    python3 build.py <project_dir>

<project_dir>/project.json drives everything (see README.md and example/project.json).
Writes <project_dir>/out/:
    presentation.html            publish with the Artifact tool (self-contained, CDN three.js)
    local.html                   full document for local render checks (three.js from kit/node_modules)
    netlify/                     index.html + robots.txt (noindex), ready to drag onto Netlify
    <JOB>_Presentation_Netlify.zip
Stops with a non-zero exit if the budget does not tie to the workbook or copy breaks the house rules.
"""
import base64, io, json, os, random, re, sys, zipfile, mimetypes
from PIL import Image

KIT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(KIT, 'lib'))
from estimate import read_estimate  # noqa: E402

THREE = '0.186.1'
BANNED = ['stunning', 'beautiful', 'breathtaking', 'luxury', 'luxurious', 'bespoke', 'elevated', 'curated', 'seamless', 'passion',
          'dream', 'journey', 'exceptional', 'world-class', 'premier', 'cutting-edge', 'unparalleled', 'empower', 'transform',
          'peace of mind', 'at the end of the day', 'the truth is', "let's be honest", 'potential risk']
CSI_GROUPS = [  # default grouping by CSI division when project.json gives no groups
    ('Site Work', lambda d, c: d in ('01', '02', '31', '33') and not c.startswith('31.66') and not c.startswith('31 66')),
    ('Foundation and Structure', lambda d, c: d == '03' or c.startswith('05.12') or c.startswith('05 12') or c.startswith('31.66') or c.startswith('31 66') or d == '04'),
    ('Building Package', lambda d, c: d == '13'),
    ('Building Envelope', lambda d, c: d in ('07', '08')),
    ('Interiors', lambda d, c: d in ('05', '06', '09', '10', '11', '12')),
    ('Plumbing, HVAC, Electrical', lambda d, c: d in ('21', '22', '23', '25', '26', '27', '28')),
    ('Hardscape and Landscape', lambda d, c: d == '32'),
]


def die(msg):
    print('BUILD STOPPED:', msg); sys.exit(1)


def data_uri(path, max_px=None, quality=82):
    ext = os.path.splitext(path)[1].lower()
    if max_px and ext in ('.jpg', '.jpeg', '.png', '.webp'):
        im = Image.open(path)
        if max(im.size) > max_px or ext == '.png' and os.path.getsize(path) > 600_000:
            im = im.convert('RGB'); im.thumbnail((max_px, max_px), Image.LANCZOS)
            b = io.BytesIO(); im.save(b, 'JPEG', quality=quality, optimize=True, progressive=True)
            return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()
    mt = mimetypes.guess_type(path)[0] or ('model/gltf-binary' if ext == '.glb' else 'application/octet-stream')
    if ext == '.webp': mt = 'image/webp'
    return f'data:{mt};base64,' + base64.b64encode(open(path, 'rb').read()).decode()


def ramp(n):
    """Montana blue, deep at the ground, light at the finish."""
    a, b = (11, 26, 92), (201, 210, 250)
    return ['#%02x%02x%02x' % tuple(round(a[k] + (b[k] - a[k]) * (i / max(1, n - 1))) for k in range(3)) for i in range(n)]


def lint(texts):
    bad = []
    for where, t in texts:
        if not isinstance(t, str): continue
        if '—' in t or '–' in t and not re.search(r'\d–\d', t): bad.append(f'{where}: dash in "{t[:60]}"')
        if ';' in t: bad.append(f'{where}: semicolon in "{t[:60]}"')
        if '!' in t: bad.append(f'{where}: exclamation in "{t[:60]}"')
        if '?' in t: bad.append(f'{where}: question in "{t[:60]}"')
        low = t.lower()
        for w in BANNED:
            if re.search(r'\b' + re.escape(w) + r'\b', low): bad.append(f'{where}: banned "{w}" in "{t[:60]}"')
        if re.search(r'\b\w+, not \w+', t): bad.append(f'{where}: "X, not Y" in "{t[:60]}"')
    return bad


def walk_text(o, path='stops'):
    if isinstance(o, str): yield path, o
    elif isinstance(o, list):
        for i, x in enumerate(o): yield from walk_text(x, f'{path}[{i}]')
    elif isinstance(o, dict):
        for k, x in o.items():
            if k in ('view', 'type', 'id', 'side', 'reveal', 'show', 'tint', 'html', 'still', 'scrim'): continue
            yield from walk_text(x, f'{path}.{k}')


def main(pdir):
    P = json.load(open(os.path.join(pdir, 'project.json')))
    rel = lambda p: p if os.path.isabs(p) else os.path.join(pdir, p)
    out = os.path.join(pdir, 'out'); os.makedirs(out, exist_ok=True)

    # ---------------- money
    if P.get('estimate'):
        E = read_estimate(rel(P['estimate']))
        if E['workbook_base'] is not None and abs(E['workbook_base'] - E['base']) > 2:
            die(f"base {E['base']} does not tie to the workbook total {E['workbook_base']}")
    elif P.get('budget'):
        B = P['budget']; E = {'trades': B['trades'], 'markups': B['markups'], 'alternates': B.get('alternates', []), 'notes': {'EXCLUSION': [], 'BY OWNER': [], 'CLARIFICATION': []}}
        E['direct'] = sum(t['value'] for t in E['trades'])
    else:
        die('project.json needs "estimate" (the workbook) or "budget"')
    rename = P.get('trade_names', {})
    trades = [{**t, 'name': rename.get(t['trade'], t['trade'])} for t in E['trades']]
    groups = []
    if P.get('groups'):
        used = set()
        for g in P['groups']:
            tr = {}
            for name in g['trades']:
                hit = [t for t in trades if t['trade'] == name or t['name'] == name]
                if not hit: die(f'group "{g["name"]}" lists trade "{name}" that is not in the estimate')
                for t in hit: tr[t['name']] = tr.get(t['name'], 0) + t['value']; used.add(id(t))
            groups.append({'key': g['name'], 'scope': g.get('scope', ''), 'color': g.get('color'), 'trades': tr})
        left = [t for t in trades if id(t) not in used]
        if left: die('trades not in any group: ' + ', '.join(t['trade'] for t in left))
    else:
        bucket = {}
        for t in trades:
            c = t['code']; d = re.sub(r'\D', '', c)[:2] or '00'
            name = next((n for n, f in CSI_GROUPS if f(d, c)), 'Other')
            bucket.setdefault(name, {})[t['name']] = bucket.get(name, {}).get(t['name'], 0) + t['value']
        order = [n for n, _ in CSI_GROUPS] + ['Other']
        groups = [{'key': n, 'scope': '', 'color': None, 'trades': bucket[n]} for n in order if n in bucket]
        if 'Other' in bucket: print('NOTE: trades grouped as Other (no CSI code). Add "groups" to project.json to place them:', ', '.join(bucket['Other']))
    cols = ramp(len(groups))
    for g, c in zip(groups, cols):
        if not g['color']: g['color'] = '#d9d3c7' if g['key'] in ('Building Package',) or 'Modular' in g['key'] else c
    direct = sum(sum(g['trades'].values()) for g in groups)
    assert direct == E['direct'], (direct, E['direct'])

    # ---------------- alternates
    ov = {str(k): v for k, v in P.get('alternates', {}).items()}
    alts = []
    for a in E['alternates']:
        o = ov.get(str(a['id']), {})
        if o.get('hide'): continue
        title = o.get('title') or (f"{a['num']}. {a['label']}" if a['num'] else a['label'])
        if a['deduct'] and 'deduct' not in title.lower() and not o.get('title'): title += ' (Deduct)'
        alts.append({'id': str(a['id']), 'title': title, 'value': a['value'], 'note': o.get('note', ''), 'featured': bool(o.get('featured'))})

    # ---------------- notes, schedule, team, images
    notes = E['notes']
    exclusions = [n['text'] for n in notes['EXCLUSION']] + [n['text'] for n in notes['BY OWNER']] + P.get('exclusions_extra', [])
    clar = [n['text'] for n in notes['CLARIFICATION']] if P.get('include_clarifications') else []
    sched = json.load(open(rel(P['schedule']))) if P.get('schedule') else None
    img = {}
    for f in os.listdir(os.path.join(KIT, 'assets', 'img')):
        img[f] = data_uri(os.path.join(KIT, 'assets', 'img', f))
    pimg = os.path.join(pdir, 'img')
    if os.path.isdir(pimg):
        for f in os.listdir(pimg):
            if re.search(r'\.(png|jpe?g|webp)$', f, re.I): img[f] = data_uri(os.path.join(pimg, f), max_px=2000)
    team = P.get('team') or [{'name': 'Joe Montana', 'title': 'Founder and CEO', 'photo': 'joe-montana-sr-800.webp'},
                             {'name': 'Matt Nicosia', 'title': 'COO', 'photo': 'matt-nicosia-800.webp'},
                             {'name': 'Chris Lange', 'title': 'Director of Construction', 'photo': 'chris-lange-800.webp'}]
    for t in team:
        if t['photo'] not in img: die(f"team photo {t['photo']} not found in kit assets or project img/")

    # ---------------- model
    M = dict(P.get('model', {'mode': 'images'}))
    stills = ''
    if M['mode'] == 'massing':
        mj = json.load(open(rel(M['file'])))
        for k, e in mj.get('elevations', {}).items():
            e['src'] = data_uri(rel(e['image']), max_px=2400, quality=86); e.pop('image', None)
        M['massing'] = mj
    elif M['mode'] == 'glb':
        if M.get('baked'):
            bf = rel(M['file']).replace('.glb', '_baked.glb')
            if not os.path.exists(bf): die(f'model.baked is on but {bf} is missing: run tools/render/bake.py first')
            M['file'] = os.path.relpath(bf, pdir)
            bj = os.path.join(pdir, 'bake', 'bake.json')
            if os.path.exists(bj): M['bakeScale'] = json.load(open(bj)).get('scale', 0.5)
        size = os.path.getsize(rel(M['file']))
        if size > 25e6: die(f'{M["file"]} is {size/1e6:.0f} MB. Decimate or compress it below 25 MB first (see README).')
        M['src'] = data_uri(rel(M['file']))
    elif M['mode'] == 'images':
        files, phones = list(M.get('images', [])), list(M.get('images_phone', []))
        rj = os.path.join(pdir, 'renders.json')
        if M.get('renders') and os.path.exists(rj):   # Cycles stills from tools/render/stills.py, wired to their stops
            R = json.load(open(rj)); files, phones = [], []
            ids = [s.get('id') or s['type'] + str(i) for i, s in enumerate(P['stops'])]
            for sid, s in zip(ids, P['stops']):
                if sid not in R: continue
                idx = []
                for n in sorted(R[sid].get('d', {}), key=int):
                    files.append(os.path.join('img', R[sid]['d'][n])); phones.append(os.path.join('img', R[sid].get('p', {}).get(n, R[sid]['d'][n]))); idx.append(len(files) - 1)
                s['still'] = idx[0] if len(idx) == 1 else idx
        stills = ''.join(f'<img src="{data_uri(rel(f), max_px=2400)}"' + (f' data-phone="{data_uri(rel(phones[i]), max_px=1600)}"' if i < len(phones) and phones[i] != f else '') + ' alt="">' for i, f in enumerate(files))
        if not files: die('model.mode "images" needs model.images: a list of renders or drawings')
    else:
        die('model.mode must be glb, massing or images')
    if M.get('setting') == 'landscape' and M.get('env', 'park') :
        ef = os.path.join(KIT, 'assets', 'env', (M.get('env') or 'park') + '.exr')
        if os.path.exists(ef): M['env'] = 'data:application/octet-stream;base64,' + base64.b64encode(open(ef, 'rb').read()).decode()
        else: M.pop('env', None)
    if M.get('setting') == 'landscape' and M.get('trees', True) is not False:
        tj = os.path.join(KIT, 'assets', 'trees', 'trees.json')
        if os.path.exists(tj):
            M['treeImpostors'] = [{**t, 'src': data_uri(os.path.join(KIT, 'assets', 'trees', t['file']))} for t in json.load(open(tj))]
    M.pop('file', None)

    # ---------------- copy check
    texts = list(walk_text(P.get('stops', []))) + [(f'keys[{i}]', k.get('ours', '')) for i, k in enumerate(P.get('keys', []))]
    bad = lint(texts)
    if bad and not P.get('allow_lint'):
        die('copy breaks the house rules:\n  ' + '\n  '.join(bad) + '\n(fix the copy, or set "allow_lint": true for a draft)')

    pj = P.get('project', {})
    labels = {'book': 'Detailed Budget', 'keys': 'Keys to Success', 'key': 'Key to Success', 'design': 'In the Design', 'ours': 'Our Approach', **P.get('labels', {})}
    data = {
        'project': {'name': pj.get('name', ''), 'address': pj.get('address', ''), 'job': pj.get('job', ''), 'chip': pj.get('chip', 'Budget Proposal')},
        'img': img, 'stops': P['stops'], 'groups': groups, 'markups': [{'label': m['label'], 'rate': m['rate']} for m in E['markups']],
        'alternates': alts, 'altNote': P.get('alt_note'), 'allowances': P.get('allowances', []), 'keys': P.get('keys', []),
        'precon': P.get('precon', [['Budget Review', 'This budget, walked line by line with the design team and the owner. Every allowance gets a price and a date.'],
                                   ['Value Engineering', 'Material swaps, system choices and scope changes, each priced with what it saves and what it changes.'],
                                   ['Trade Partner Pricing', 'At 90% construction documents, our trade partners price the work. Hard numbers from the people who build it.'],
                                   ['GMP', 'One guaranteed maximum price, set before we break ground.']]),
        'preconNote': P.get('precon_note'), 'team': team, 'teamNote': P.get('team_note'), 'nextStep': P.get('next_step'),
        'exclusions': exclusions, 'clarifications': clar, 'schedule': sched, 'phases': P.get('phases', []),
        'labels': labels, 'decisions': P.get('decisions', {}), 'scheduleModel': bool(P.get('schedule_model', False)), 'bookLede': P.get('book_lede'), 'stat': P.get('book_stat'), 'model': M,
    }

    # ---------------- assemble
    T = lambda f: open(os.path.join(KIT, 'template', f)).read()
    css = T('style.css')
    random.seed(1984)
    g = Image.new('L', (128, 128)); g.putdata([max(0, min(255, int(random.gauss(128, 34)))) for _ in range(128 * 128)])
    b = io.BytesIO(); g.save(b, 'PNG', optimize=True)
    fonts = os.path.join(KIT, 'assets', 'fonts')
    css = (css.replace('{{FONT_R}}', base64.b64encode(open(os.path.join(fonts, 'TTCommonsPro-Regular.woff2'), 'rb').read()).decode())
              .replace('{{FONT_B}}', base64.b64encode(open(os.path.join(fonts, 'TTCommonsPro-Bold.woff2'), 'rb').read()).decode())
              .replace('{{NOISE}}', base64.b64encode(b.getvalue()).decode()))
    body = T('body.html')
    poster = data_uri(rel(P['poster']), max_px=1600) if P.get('poster') else 'data:image/gif;base64,R0lGODlhAQABAAAAACw='
    bl = P.get('book_button', {})
    rep = {'{{POSTER}}': poster, '{{STILLS}}': stills, '{{CHIP}}': data['project']['chip'], '{{BOOK_LABEL}}': bl.get('label', labels['book']),
           '{{BOOK_NOTE}}': f' <span class="k">{bl["note"]}</span>' if bl.get('note') else '', '{{BOOK_SHORT}}': bl.get('short', 'Budget'),
           '{{DEC_BUTTON}}': '' if P.get('decisions', {}).get('enabled') is False else '<button class="btn line" id="openDecs" type="button"><span class="lab">Decision List</span><span class="short">Decisions</span><span class="ct" id="decCount"></span></button>', '{{BOOK_BACK}}': bl.get('back', 'Back to the Presentation'),
           '{{CUE}}': P.get('cue', 'Scroll to build it' if M['mode'] != 'images' else 'Scroll'), '{{MODEL_LABEL}}': f"Model of the {data['project']['name']}"}
    for k, v in rep.items(): body = body.replace(k, v)
    body = re.sub(r'\{\{IMG:([^}]+)\}\}', lambda m: img[m.group(1)], body)
    title = P.get('title') or data['project']['name']
    page = (f'<title>{title}</title>\n<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&display=swap">\n<style>{css}</style>\n{body}\n'
            f'<script>window.PROPOSAL = {json.dumps(data)};</script>\n<script>{T("page.js")}</script>\n<script>{T("decisions.js")}</script>\n')
    world = T('world.js') if M['mode'] != 'images' else ''
    cdn = {'imports': {'three': f'https://cdn.jsdelivr.net/npm/three@{THREE}/build/three.module.js', 'three/addons/': f'https://cdn.jsdelivr.net/npm/three@{THREE}/examples/jsm/'}}
    nm = os.path.relpath(os.path.join(KIT, 'node_modules'), out)
    local = {'imports': {'three': f'{nm}/three/build/three.module.js', 'three/addons/': f'{nm}/three/examples/jsm/'}}
    mod = lambda im: (f'<script type="importmap">{json.dumps(im)}</script>\n<script type="module">\n{world}\n</script>' if world else '')
    head = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
    pres = page + mod(cdn)
    open(os.path.join(out, 'presentation.html'), 'w').write(pres)
    open(os.path.join(out, 'local.html'), 'w').write(head + '</head><body>' + page + mod(local) + '</body></html>')
    nd = os.path.join(out, 'netlify'); os.makedirs(nd, exist_ok=True)
    open(os.path.join(nd, 'index.html'), 'w').write(head + '<meta name="robots" content="noindex, nofollow"></head><body>' + pres + '</body></html>')
    open(os.path.join(nd, 'robots.txt'), 'w').write('User-agent: *\nDisallow: /\n')
    zp = os.path.join(out, f"{data['project']['job'] or 'Project'}_Presentation_Netlify.zip")
    with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
        for f in ('index.html', 'robots.txt'): z.write(os.path.join(nd, f), f)
    base = round(direct);
    for m in E['markups']: base += round(base * m['rate'])
    if P.get('decisions', {}).get('enabled') is not False:
        print('Decision List on: publish presentation.html with capabilities {"db": {}, "user": {"scopes": ["profile"]}} so answers save for everyone on the link.')
    print(f"built {out}/presentation.html {len(pres)//1024} KB · direct ${direct:,} · base ${base:,} · {len(groups)} groups · {len(alts)} alternates · {len(P['stops'])} stops · model {M['mode']}")
    if len(pres) > 15e6: print('WARNING: page over 15 MB, the Artifact limit is 16 MB')


if __name__ == '__main__':
    if len(sys.argv) != 2: print(__doc__); sys.exit(2)
    main(sys.argv[1])
