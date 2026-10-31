#!/usr/bin/env python3
"""Website-format presentation build. Job: E26044 The Inn at Kirkside (from the kit reference E260050 The Cooper Barn, v5.2).

Copy this folder to <project>/web/, then change the job-specific blocks marked JOB below: the element and allowance
row maps, the copy (PROSE, STEPS, BASIS, CLAR, EXCL), the schedule milestones and the zip name.

    python3 -I build.py

Every figure comes from the estimate's line items (Estimate sheet), to the cent, so the Elements and MasterFormat
views, the signature elements and the base budget all tie. Writes
    site/       index.html (Artifact page, no skeleton) + assets/
    netlify/    index.html (full document) + assets/ + robots.txt
    E260050_Presentation_Netlify_v5.zip
Stops if a figure does not tie, or client copy breaks the house rules.
"""
import base64, datetime as dt, glob, html, json, os, re, shutil, sys, zipfile
from urllib.parse import quote
from decimal import Decimal as D, ROUND_HALF_UP
import numpy as np
import openpyxl
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
CB = os.path.dirname(HERE)
KIT = os.environ.get('MCC_KIT') or os.path.join(os.path.dirname(CB), 'kit')
LENIS = 'vendor/lenis/lenis.min.js (inlined, lenis 1.1.13)'   # inlined so the page never waits on a CDN
E = lambda s: html.escape(str(s), quote=True)
C = lambda x: D(str(x)).quantize(D('0.01'), ROUND_HALF_UP)
money = lambda v: '${:,.2f}'.format(C(v))
pct = lambda v, of: (lambda x: '<0.1%' if 0 < x < 0.05 else '{:.1f}%'.format(x))(float(D(v) / D(of) * 100))


def die(m):
    print('BUILD STOPPED:', m); sys.exit(1)


P = json.load(open(os.path.join(CB, 'project.json')))
SCH = json.load(open(os.path.join(CB, 'schedule.json')))

# ================================================================ money, from the line items
wb = openpyxl.load_workbook(os.path.join(CB, 'estimate.xlsx'), data_only=True)
ws = wb['Estimate']
LINES, trade = {}, None
ROW_TOTAL = next(i for i, r in enumerate(ws.iter_rows(min_row=1, max_row=ws.max_row, values_only=True), start=1) if r[0] == 'TOTAL -- BASE BID')
for i, r in enumerate(ws.iter_rows(min_row=10, max_row=ROW_TOTAL, values_only=True), start=10):
    code, item, qty, unit, rate, tot = r[:6]
    if code and isinstance(code, str) and code.isupper() and not item and code not in ('TRADE TOTAL', 'SUBTOTAL'): trade = code; continue
    if code in ('TRADE TOTAL', 'SUBTOTAL') or not item: continue
    if isinstance(tot, (int, float)) and tot: LINES[i] = {'code': str(code).strip(), 'item': str(item).strip(), 'trade': trade, 'v': C(tot)}
DIRECT = sum(l['v'] for l in LINES.values())
FEE = C(DIRECT * D('0.06')); INS = C((DIRECT + FEE) * D('0.03')); OP = FEE + INS; BASE = DIRECT + OP   # E26044: fee 6%, insurance 3% (no overhead line)
def mk(v):
    v = C(v); f = C(v * D('0.06')); return v + f + C((v + f) * D('0.03'))
sheet_total = C(ws.cell(ROW_TOTAL, 6).value)
if BASE != sheet_total: die(f'base {BASE} does not tie to the Estimate sheet total {sheet_total}')
ALT_ROWS, VE_ROWS, _cur = {}, {}, None   # alternate and value engineering totals (with markups), by number
for i, r in enumerate(ws.iter_rows(min_row=ROW_TOTAL + 1, max_row=ws.max_row, values_only=True), start=ROW_TOTAL + 1):
    h = str(r[0] or '')
    m_ = re.match(r'ALTERNATE (\d+) --', h) or re.match(r'VE-(\d+) --', h)
    if m_: _cur = (ALT_ROWS if h.startswith('ALTERNATE') else VE_ROWS, int(m_.group(1)))
    if r[0] == 'TOTAL' and isinstance(r[5], (int, float)) and _cur: _cur[0][_cur[1]] = C(r[5]); _cur = None

# JOB: client wording for lines whose estimator notes should not reach the page
ITEM_FIX = {'Levels - Floor Structure': 'Floor Structure', 'F/I Honeywell BMS System': 'F/I Building Management System'}
def clean(item, code=''):   # client wording for a line item: no bracketed estimator notes, no drawing references, no unit rates
    for k, v in ITEM_FIX.items():
        if item.startswith(k): return plain(v)
    s = re.sub(r'\s*\[Allowance[^\]]*\]', ' (Allowance)', item)
    s = re.sub(r'\s*\[[^\]]*\]', '', s); s = s.replace(' (M+L)', '').replace('(M+L)', '')
    s = re.sub(r'\s*\([^()]*\b(?:SD|SEP|DW)-\d[^()]*\)', '', s)            # drawing references
    s = re.sub(r'\s*\((?:Kitchen Layout TBD|Design TBD)\)', '', s)
    s = re.sub(r'\(\$[\d,.]+/(?:SF|Ea|EA|LF)[^)]*Material[^)]*\)', '(Material Allowance)', s)
    s = re.sub(r'\(\$[\d,.]+/(?:SF|Ea|EA|LF)[^)]*\)', '(Allowance)', s)
    s = re.sub(r'\$(\d[\d,]*)(?![\d,]*\.\d)', r'$\1.00', s)   # every dollar figure carries cents
    s = re.sub(r'\s*\(Per (Week|Month|Page|Riser|Hour)\)', '', s)   # the line shows a total, so the unit basis would misread
    s = re.sub(r'\(\$[\d,]+\.\d\d/SF Mat\. Allowance\)', '(Material Allowance)', s)   # no unit rates in the line detail
    s = re.sub(r'\(\$[\d,]+\.\d\d Allowance\)', '(Allowance)', s)
    s = re.sub(r'^(?:FF|WF)-\d+:\s*(?:F/I:?\s*)?', 'F/I ', s) if re.match(r'^(?:FF|WF)-\d+:', s) else s
    s = re.sub(r'\bWF-\d+:?\s*', '', s); s = re.sub(r'\s*\(\s*layers\)', '', s); s = re.sub(r'\s*\((?:Spec,? TBD)\)', '', s)
    for a_, b_ in (('F/II:', 'F/I'), ('F/I:', 'F/I'), ('Inidcator', 'Indicator'), ('Ductowork', 'Ductwork'), ('Cespool', 'Cesspool'), ('Baement', 'Basement'), ('Paneboard', 'Panelboard'), ('Lathe', 'Lath'), ('Coarse', 'Course'), (' @ ', ' at '), ('@', 'at '), ('Kebony,,', 'Kebony,'), ("MEP's", 'MEP Work')): s = s.replace(a_, b_)
    s = s.replace('(~', '(About ').replace('Every ~', 'About Every ').replace('~', 'About ').replace(' @ ', ' at ').replace('SSTS', 'Septic')
    s = re.sub(r'\(Allowance\)\s*\(Allowance\)', '(Allowance)', s)
    s = job_fix(s)
    return directive(plain(re.sub(r'\s{2,}', ' ', s).strip()), code)

def job_fix(s):   # JOB: client wording fixes for this estimate's line names
    s = re.sub(r'^((?:F/I|F/O|I/O)\s+)?(?:Foundation|Levels) - ', lambda m: m.group(1) or '', s)
    s = re.sub(r'\(P-\d+, ref Tag \d+ A-\d+\)\s*', '', s)
    s = re.sub(r'\s*\((?:FF|WF|MF)-?\d+\)', '', s); s = re.sub(r'\b(?:FF|WF)-\d+:?\s*', '', s); s = re.sub(r'\bMF0?\d+\s+', '', s)
    s = re.sub(r'\(\s*(?:Spec,? TBD|Size TBD)\s*\)', '', s); s = re.sub(r',\s*Spec,? TBD', '', s); s = s.replace(' Model #_', '')
    s = re.sub(r'Kohler,(\S)', r'Kohler, \1', s); s = re.sub(r'(K-[\w-]*?-)\s+(\w)', r'\1\2', s)
    s = re.sub(r'^(F/I )(\d+X\d+ Steel Beam)', r'\1W\2', s); s = re.sub(r'^F/I HSS6X4X3/8$', 'F/I HSS6X4X3/8 Steel Tube', s)
    s = re.sub(r'HW Set (\d)\b', r'HW Set 0\1', s).replace('HW Set', 'Hardware Set')
    for a_, b_ in (('Silt Fence Budget', 'Silt Fence'), ('Remaining Demo', 'Remove Remaining Items Shown on the Demolition Plans'), ('Inspections: Stormwater, Weekly', 'Weekly Stormwater Inspections'), (' (7 Can Be Done Each Phase)', ''),
                   (' at In Laundry', ' at Laundry'), ('Ikea', 'IKEA'), ('DIffuser', 'Diffuser'), ('Annodized', 'Anodized'), ('Water Proof', 'Waterproof'),
                   ('Heat Water Cooled', 'Water Cooled'), ("3'7- 1/2\"", "3'-7 1/2\""), ("(4'6 x 1'-9\")", "(4'-6\" x 1'-9\")"), ('Joint Reinf at 2 courses', 'Joint Reinforcing at Every 2 Courses'),
                   ('HWH-1: Wire 54 KW electric hot water heater', 'Wire 54 KW Electric Hot Water Heater (HWH-1)'), (' 100 gal ', ' 100 Gallon '), ('" dia ', '" Diameter '),
                   (',,', ','), ('Shore Window Bay Prior To Demo', 'Shore Window Bay Before Demolition')):
        s = s.replace(a_, b_)
    for w in ('Of', 'To', 'With', 'And', 'For', 'In', 'Into', 'On', 'The'):
        s = re.sub(r'(?<=\S) ' + w + r' (?=\S)', ' ' + w.lower() + ' ', s)
    s = re.sub(r'\(\s*\)', '', s); s = re.sub(r'\s+\)', ')', s); s = re.sub(r'\)\s*\(', ', ', s)
    return re.sub(r'\s{2,}', ' ', s).strip()

VERBS = ('Furnish and Install', 'Furnish Only', 'Install Only', 'Provide', 'Remove', 'Replace', 'Repair', 'Patch', 'Paint', 'Wire', 'Abandon', 'Export', 'Spread', 'Strip',
         'Protect', 'Refinish', 'Scrape', 'Seal', 'Grind', 'Cut', 'Enlarge', 'Fill', 'Infill', 'Shore', 'Underpin', 'Disconnect', 'Relocate', 'Finish', 'Demolish', 'Clean', 'Form and Pour', 'Saw Cut')
def directive(s, code=''):   # JOB: every scope item opens with what Montana does
    m = re.match(r'(?:Furnish and Install|Furnish Only|Install Only) (.*)', s)
    if m and re.match(r'(?:Repair|Replace|Remove|Patch|Paint|Demolish)\b', m.group(1)): s = m.group(1)
    s = re.sub(r'^Demo\b', 'Demolish', s); s = re.sub(r'^Form/Pour\b', 'Form and Pour', s)
    if s.startswith('Spread Footings'): return 'Furnish and Install ' + s
    if re.match(r'(?:' + '|'.join(map(re.escape, VERBS)) + r')\b', s): return s
    if s.startswith('Underpinning'): return 'Provide ' + s
    if s.startswith('Spread Footings'): return 'Furnish and Install ' + s
    if s.startswith('Install '): return 'Install Only ' + s[8:]
    if s.startswith('Furnish '): return 'Furnish Only ' + s[8:]
    return ('Provide ' if code.startswith('01') else 'Furnish and Install ') + s

def plain(s):   # estimator shorthand spelled out for the client
    for k, v in (('F/I ', 'Furnish and Install '), ('F/O ', 'Furnish Only '), ('I/O ', 'Install Only '), (' w/ ', ' with '), (' W/ ', ' with ')):
        s = s.replace(k, v)
    return s

def find_rows(*starts, n=None):   # Estimate rows whose item starts with any of these words
    out = [r for r, l in LINES.items() if l['item'].startswith(starts)]
    if not out or (n is not None and len(out) != n): die(f'expected {n} rows for {starts}, found {len(out)}')
    return out
def code_rows(*prefixes): return [r for r, l in LINES.items() if l['code'].startswith(prefixes)]
trade_names = P.get('trade_names', {})
def tkey(name): return name.upper()
TR = {}
for l in LINES.values(): TR[l['trade']] = TR.get(l['trade'], D(0)) + l['v']
# JOB: rows that belong to another group than their trade (the guard on the parking wall is site work, carried under railings)
ROW_GROUP = {}
GMAP = [('General Requirements', ('01',)), ('Demolition', ('02',)), ('Site, Foundations and Decks', ('03', '04', '31', '32', '33', '05.50', '06.15')),
        ('Structure and Envelope', ('05', '06.10', '06.11', '07', '08')), ('Interiors', ('06.2', '06.43', '09', '10', '11', '12', '14')),
        ('Mechanical, Plumbing and Fire Protection', ('21', '22', '23')), ('Electrical and Fire Alarm', ('26', '27', '28'))]
SCOPE_FIX = {}
def group_of(r, l):
    if l['item'].startswith('F/I New Pergola'): return 'Site, Foundations and Decks'   # JOB
    for g, pre in GMAP:
        if l['code'].startswith(pre) and not (g == 'Structure and Envelope' and l['code'].startswith(('05.50', '06.15'))): return g
    die('line has no group: ' + l['item'])
GROUPS = []
GSCOPE = {'General Requirements': 'Staff, field office, protection, fencing, containers and inspections.', 'Demolition': 'Selective demolition inside the existing building, chimneys and roof openings.',
          'Site, Foundations and Decks': 'Foundations, shoring and underpinning, site work, paving, terraces and the Kebony deck.', 'Structure and Envelope': 'Steel, framing, insulation, roofing, windows, doors and the conservatory glass.',
          'Interiors': 'Millwork, finish carpentry, drywall, tile, wood floors, paint and the elevator.', 'Mechanical, Plumbing and Fire Protection': 'Geothermal and VRF heating and cooling, plumbing and sprinklers.',
          'Electrical and Fire Alarm': 'Service, generator, lighting, devices and fire alarm.'}
for g in [{'name': n} for n, _p in GMAP]:
    rows = [(r, l) for r, l in LINES.items() if group_of(r, l) == g['name']]
    GROUPS.append({'name': g['name'], 'scope': GSCOPE[g['name']], 'v': sum(l['v'] for r, l in rows),
                   'lines': [{'item': clean(l['item'], l['code']), 'v': l['v']} for r, l in rows]})
if sum(g['v'] for g in GROUPS) != DIRECT: die('groups do not tie to direct cost')

MF_TITLES = {'01': 'General Requirements', '02': 'Existing Conditions', '03': 'Concrete', '04': 'Masonry', '05': 'Metals',
             '06': 'Wood, Plastics, and Composites', '07': 'Thermal and Moisture Protection', '08': 'Openings', '09': 'Finishes',
             '10': 'Specialties', '11': 'Equipment', '12': 'Furnishings', '22': 'Plumbing', '23': 'Heating, Ventilating, and Air Conditioning',
             '26': 'Electrical', '27': 'Communications', '28': 'Electronic Safety and Security', '31': 'Earthwork', '32': 'Exterior Improvements',
             '33': 'Utilities', '34': 'Transportation'}
# MasterFormat view = the proposal's Schedule of Values: one row per cost code (subdivision) as the workbook's SOV sheet lists it,
# direct cost, same names as the PDF proposal (SOV_NAMES), so the presentation and the proposal read line for line the same.
SOV_NAMES = {}
_sv, _on, SOV_TRADES = wb['SOV'], False, {}
for r in _sv.iter_rows(values_only=True):
    if r[0] == 'CSI' and r[1] == 'Trade': _on = True; continue
    if _on and r[0] in ('SUBTOTAL',): break
    if _on and r[0]: SOV_TRADES[str(r[0])] = SOV_NAMES.get(r[1], r[1])
MF = {}
for l in LINES.values():
    if l['code'] not in SOV_TRADES: die('line code not on the SOV sheet: ' + l['code'])
    MF.setdefault(l['code'], []).append({'item': clean(l['item'], l['code']), 'v': l['v']})
DIVS = [{'n': k.replace('.', ' '), 'name': SOV_TRADES[k], 'v': sum(x['v'] for x in MF[k]), 'lines': MF[k]} for k in SOV_TRADES if k in MF]
if sum(d['v'] for d in DIVS) != DIRECT: die('SOV cost codes do not tie to direct cost')
for d in DIVS:   # each row must equal the workbook SOV row to the cent
    _w = next(C(r[2]) for r in _sv.iter_rows(values_only=True) if str(r[0]).replace('.', ' ') == d['n'])
    if _w != d['v']: die(f'SOV row {d["n"]} {d["v"]} vs workbook {_w}')

def el(rows):
    return mk(sum(LINES[r]['v'] for r in rows))
# JOB: the signature elements, by Estimate row (found by their words), each x 1.15 with O&P.
EL_ROWS = {
    'windows': code_rows('08.50.00', '07.65.00') + find_rows('I/O Windows', n=1) + find_rows('F/I Exterior Window Casing to Match Existing', n=1),
    'glass': [r for r in code_rows('08.43.00', '08.80.00') if 'Shower Glass' not in LINES[r]['item']],
    'elevator': code_rows('14.20.00') + find_rows('Foundation - Foundation Walls (Elevator Pit Walls)', n=1) + find_rows('Cut Opening In Roof For Elevator Shaft', n=1),
    'deck': code_rows('06.15.00') + find_rows('F/I 2X8 Pressure Treated Deck Framing', n=1) + find_rows('F/I Deck Stairs', n=1),
    'terrace': code_rows('32.14.00', '04.57.00', '05.50.00') + find_rows('F/I New Pergola', n=1),
    'geo': find_rows('F/I Geothermal Wells', n=1) + find_rows('F/I Geothermal Pump', n=1) + find_rows('F/I Hydrokit', n=1) + find_rows('F/I Air Separator', n=1),
}
ELS = [
    ('windows', 'Marvin Windows', el(EL_ROWS['windows']), 'Marvin Signature Ultimate windows, full frame, with sill pans and casings to match.'),
    ('glass', 'Conservatory Glass', el(EL_ROWS['glass']), 'The glass roof over the conservatory and the storefront on the deck side.'),
    ('elevator', 'Passenger Elevator', el(EL_ROWS['elevator']), 'One passenger elevator with its pit and the shaft through the roof.'),
    ('deck', 'Kebony Deck', el(EL_ROWS['deck']), '3,087 SF of thermally modified Kebony decking, stepped down to the lawn.'),
    ('terrace', 'Terraces, Pergola and Fire Pit', el(EL_ROWS['terrace']), 'Bluestone and Medina stone terraces, a new pergola and the fire pit.'),
    ('geo', 'Geothermal Well Field', el(EL_ROWS['geo']), '16 geothermal wells, 495 feet deep, with pumps and hydro kits.'),
]
EL_TOTAL = sum(e[2] for e in ELS)
REST = BASE - EL_TOTAL
EL_ALL = {r for v in EL_ROWS.values() for r in v}
SITE_FDN = mk(sum(l['v'] for r, l in LINES.items() if l['code'][:2] in ('02', '03', '31', '32', '33') and r not in EL_ALL))   # JOB: demolition, site work, utilities and concrete

# JOB: allowances from the Notes sheet (Allowances and Material Allowances), by Estimate row.
ALLOW_ROWS = [('Roofing Repairs', 'Existing roofs, unused amount credited', find_rows('Roofing Repair Allowance', n=1)),
              ('Patching Behind MEP Work', 'Walls and ceilings, unused amount credited', find_rows('Patch Walls & Ceilings Behind MEP', n=1))]
ALLOWS = [{'label': a, 'basis': b, 'v': money(sum(LINES[r]['v'] for r in rows_))} for a, b, rows_ in ALLOW_ROWS]
ALLOW_TOTAL = sum(sum(LINES[r]['v'] for r in rows_) for a, b, rows_ in ALLOW_ROWS)
ALLOWS += [{'label': 'Wood Flooring', 'basis': 'Material', 'v': '$13.00 per SF'}, {'label': 'Marble Tile', 'basis': 'Material', 'v': '$18.00 per SF'},
           {'label': 'Mosaic Tile', 'basis': 'Material', 'v': '$35.00 per SF'}, {'label': 'Countertops', 'basis': 'Material', 'v': '$75.00 per SF'},
           {'label': 'Ceiling Planks', 'basis': 'Material', 'v': '$15.00 per SF'}, {'label': 'Decking', 'basis': 'Material', 'v': '$12.00 per SF'}, {'label': 'Terracotta Border', 'basis': 'Material', 'v': '$10.00 per SF'}, {'label': 'Elevator Flooring', 'basis': 'Material', 'v': '$15.00 per SF'}]

ALTS = [{'id': str(k), 'title': P['alternates'][str(k)]['title'], 'note': P['alternates'][str(k)]['note'], 'v': ALT_ROWS[k]} for k in sorted(ALT_ROWS)]
VES = [{'id': 've' + str(k), 'title': P['ve'][str(k)]['title'], 'note': P['ve'][str(k)]['note'], 'v': VE_ROWS[k]} for k in sorted(VE_ROWS)]
if len(ALTS) != 5 or len(VES) != 12: die('alternates or value engineering items moved')
money_s = lambda v: ('-' if C(v) < 0 else '') + money(abs(C(v)))   # signed figure for the value engineering deducts

# ================================================================ selections (kit v1.7): one card per element, prices from the workbook
sys.path.insert(0, os.path.join(KIT, 'tools', 'sel')); import selbuild
SEL_PATH = os.path.join(CB, 'selections.json')
SELX = {'C': C, 'die': die, 'money': money, 'E': E, 'ws': ws, 'LINES': LINES, 'find_rows': find_rows, 'code_rows': code_rows,
        'ALT_ROWS': ALT_ROWS, 'VE_ROWS': VE_ROWS, 'BASE': BASE, 'CB': CB, 'OP': D('0.0918')}
SEL = selbuild.resolve(json.load(open(SEL_PATH)), SELX) if os.path.exists(SEL_PATH) else None

# ================================================================ schedule, in weeks from mobilization, by phase
d = lambda s: dt.date.fromisoformat(s)
mob = d(SCH['mob'])
PHASES = [('Demolition and Site', ['rel', 'mob', 'demo', 'ust', 'geo', 'util', 'hard', 'top'], '#001a8a'), ('Foundation and Structure', ['fdn', 'frm'], '#0028cc'), ('Envelope', ['roof', 'win', 'ext'], '#3d5bd9'),
          ('Systems', ['mep', 'insp', 'elev', 'pwr'], '#6a82e2'), ('Interiors', ['ins', 'gwb', 'mill', 'fin'], '#93a5ec'), ('Closeout', ['cx', 'pl'], '#b9c5f3')]   # JOB
phase_of = {k: (n, c) for n, ks, c in PHASES for k in ks}
SROWS = []
for r in SCH['rows']:
    n, c = phase_of[r['key']]
    SROWS.append({'name': r['name'], 'a': (d(r['s']) - mob).days / 7, 'b': ((d(r['f']) - mob).days + 1) / 7, 'phase': n, 'c': c})
SPAN = float(SCH['weeks'])   # the chart ends on the Work Complete line
for r in SROWS: r['b'] = min(r['b'], SPAN)   # the last finish date counts its own day, a fraction past the last week
PH_SPANS = [(n, c, min(r['a'] for r in SROWS if r['phase'] == n), max(r['b'] for r in SROWS if r['phase'] == n)) for n, ks, c in PHASES]
# JOB: schedule milestones from the working schedule.
MS = [(m['w'], m['name']) for m in SCH['milestones']]
if MS[-1][0] != SCH['weeks']: die(f"schedule does not end at {SCH['weeks']} weeks")

# ================================================================ model frames: one camera, cropped once for all
MD = os.path.join(HERE, 'model')
FR_C = ['c1_today', 'c0_site', 'c3_add', 'c2_complete']   # JOB
FR_W = ['w1_windows', 'w2_glass', 'w3_elevator', 'w4_deck', 'w5_terrace', 'w6_geo', 'w7_all']
FRAMES = FR_C + FR_W
box = None
for f in FRAMES:
    a = np.array(Image.open(os.path.join(MD, f + '.png')).split()[3])
    ys, xs = np.where(a > 200); b = (xs.min(), ys.min(), xs.max(), ys.max())
    box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
CROP = (max(0, int(box[0]) - 40), max(0, int(box[1]) - 40), min(1600, int(box[2]) + 90), min(1200, int(box[3]) + 50))
FR = (CROP[2] - CROP[0], CROP[3] - CROP[1])
PTS = {k: [x - CROP[0], y - CROP[1]] for k, (x, y) in json.load(open(os.path.join(MD, 'c2_complete.png.points.json'))).items()}
BB = {}
for (k, *_r), f in zip(ELS, FR_W):   # where each element shows in blue: the box the focus brackets draw around
    im = np.array(Image.open(os.path.join(MD, f + '.png')).convert('RGBA')).astype(int)
    blue = (im[..., 2] > im[..., 0] + 70) & (im[..., 2] > im[..., 1] + 50) & (im[..., 3] > 200)
    ys, xs = np.where(blue)
    BB[k] = [int(xs.min()) - CROP[0], int(ys.min()) - CROP[1], int(xs.max()) - CROP[0], int(ys.max()) - CROP[1]]

# ================================================================ copy
LOC = 'Roxbury, NY'
# JOB: the project description (kit v1.14: one paragraph, 40 to 80 words).
PROSE = [
    'The Inn at Kirkside is a historic estate on State Highway 30 in Roxbury, New York, renovated as an inn and restaurant to designs by Mapos. The work covers a full interior renovation, guest suites, a conservatory under a new glass roof, a passenger elevator, a stepped Kebony deck and terraces, and geothermal heating and cooling from 16 wells.',
]
TITLE_EL = 'Signature Elements'
# JOB: the design steps (frames from render_model.sh).
STEPS = [
    {'k': 'today', 'rail': 0, 'title': 'Existing Building', 'fig': money(BASE), 'cap': 'The inn as it stands today. Base budget for the renovation, with fee and insurance.', 'img': 0, 'note': 'Existing Building'},
    {'k': 'site', 'rail': 1, 'title': 'Site and Foundation', 'fig': money(SITE_FDN), 'cap': 'Demolition, underpinning, new foundations and site work, with fee and insurance.', 'img': 1, 'note': 'New Foundations and the Elevator Pit in Montana Blue'},
    {'k': 'add', 'rail': 1, 'title': 'Additions', 'cap': 'The glazed porch, the conservatory and the elevator shaft.', 'img': 2, 'note': 'Additions in Montana Blue'},
    {'k': 'complete', 'rail': 2, 'title': 'Complete', 'cap': 'The renovated inn with its deck, terraces and site.', 'img': 3, 'note': 'Complete'},
]
for i, (k, name, v, spec) in enumerate(ELS):
    STEPS.append({'k': k, 'rail': 3, 'title': TITLE_EL, 'sub': f'<b>{i + 1:02d} / {len(ELS):02d}</b>{E(name)}', 'fig': money(v), 'cap': spec,
                  'img': 4 + i, 'el': i, 'note': 'Shown in Montana Blue'})
STEPS.append({'k': 'all', 'rail': 3, 'title': TITLE_EL, 'sub': 'Six Elements', 'fig': money(EL_TOTAL), 'cap': f'{pct(EL_TOTAL, BASE)} of the {money(BASE)} base budget.',
              'img': 10, 'all': True, 'note': 'Signature Elements in Montana Blue'})
for s in STEPS: s['label'] = '02 / Design'

# JOB: Basis of Budget, Clarifications and Exclusions, from the Notes sheet. Fragments are checked against it below.
_N = json.load(open(os.path.join(CB, 'notes.json')))
BASIS, CLAR, EXCL = _N['Basis of Budget'], _N['Clarifications'], _N['Exclusions']
notes_src = ' '.join(n for n in [str(r[2]) for r in wb['Notes & Clarifications'].iter_rows(min_row=5, values_only=True) if r[2]]) + ' ' + ' '.join(l['item'] for l in LINES.values())
for frag in BASIS + CLAR + EXCL:
    if frag not in notes_src: die('note drifted from the estimate: ' + frag)

# JOB: principals and the Approach copy. Confirm titles.
TEAM = [('Joe Montana', 'Founder and CEO', 'joe-montana-sr-800.webp'), ('Matt Nicosia', 'COO', 'matt-nicosia-800.webp'), ('Chris Lange', 'Director of Construction', 'chris-lange-800.webp')]
# kit v1.10: the team as numbers (1, 1, 3), three short lines each. JOB: the architect and the long-lead item named in the lines.
TIERS = [
    ('1', 'Site Superintendent', 'On site, start to finish', ['Runs the site from mobilization to the punch list.',
        'Checks the work against the drawings before it is covered.', 'Files daily field reports and photos in Montana OS.']),
    ('1', 'Project Manager', 'On every project', ['Runs the schedule, the budget and the submittals with Blejer Architecture.',
        'Prices every change order before the work is approved.', 'Orders the Unilux windows at award.']),
    ('3', 'Principals', 'On every project', ['Joe Montana, Matt Nicosia and Chris Lange stay on every project.',
        'One of them is your contact from the first walkthrough to the final punch list.', 'You are never handed off.']),
]
OS_FEATURES = [('RFIs, Submittals and Change Orders', 'One log. Every item dated and tracked to an answer.'), ('Schedule', 'Roadblocks flagged the day they appear.'),
               ('Field Reports', 'Daily reports and photos from the site.'), ('Drawings and Specs', 'Indexed by sheet and section.'),
               ('Job Cost', 'Tracked against the budget, line by line.'), ('Punch List', 'Tracked to closeout.')]
OS_FOR = [('For Blejer Architecture', 'Every question, answer and decision in one place.'), ('For the Owner', 'The budget, the schedule and the site, live.'),
          ('For the Job', 'The field and the office work from the same information.')]
PHONE, ADDR, EMAIL = '(845) 398-1778', 'Congers, NY and Jefferson, NY', P['decisions']['email']

# pre-construction, as sent on the last pre-con agreement, with nothing project-specific
# kit v1.9: no plus-or-minus ranges anywhere a client reads. A range next to their budget reads as "the number could be 30% low".
# Each phase says what it locks instead; the funnel keeps its shape (width only, never labelled with a percentage).
PC_PHASES = [('Budget Setting and Schematic Design Budget', 'Phase 01', 20, 'Your target budget and the scope it buys', 'About 2 weeks', 'Budget Set'),
             ('Design Development Updates', 'Phase 02', 15, 'Selections in place of allowances', 'About 2 weeks per revision', 'Selections'),
             ('Firm Trade Partner Pricing', 'Phase 03', 8, 'Bids from the trades who will build it', '3 to 4 weeks with Phase 04', 'Trade Bids'),
             ('Value Engineering, Built In', 'Phase 04', 3, 'One Guaranteed Maximum Price', 'GMP delivered', 'GMP')]
PC_CARDS = [('Phase 01', 'Budget Setting and Schematic Design Budget', ['Budget setting session with you', 'Foundation strategy, priced', 'Options priced side by side'],
             'Your target budget and an options menu with three scenarios.'),
            ('Phase 02', 'Design Development Updates', ['Re-priced as the design develops', 'Design-to-budget meetings with your architect', 'Early flags on budget drift'],
             'An updated budget with more detailed line items, plus a preliminary schedule.'),
            ('Phase 03', 'Firm Trade Partner Pricing', ['Our subcontractors and vendors bid the major trades', 'Site walks with the key trades', 'Bids compared line by line'],
             'A budget backed by real pricing.'),
            ('Phase 04', 'Value Engineering, Built In', ['Money-saving options with trade-offs explained', 'Final pricing', 'Guaranteed Maximum Price proposal'],
             'Your GMP and a construction schedule.')]
PC_PROMISES = [('Walk-Away Guarantee', 'Stop after any phase. Keep everything delivered.'),
               ('Unused Reserve Comes Back to You', '100% of unused contingency credited back.'),
               ('One Rate, No Matter Who Is on the Call', 'One hourly rate, one person per meeting.')]
PC_PRINCIPLES = [('You Are Heard From Day One', 'Your vision, your budget, your timeline. We listen before we estimate.'),
                 ('You Understand Every Number', 'We walk you through each line item so you know exactly what drives cost and where tradeoffs live.'),
                 ('You Own the Strategy', 'We produce options, with the price of each one, so the plan at GMP is yours.')]

# ================================================================ assets
SITE, NET = os.path.join(HERE, 'site'), os.path.join(HERE, 'netlify')
for p_ in (SITE, NET): shutil.rmtree(p_, ignore_errors=True)
A = os.path.join(SITE, 'assets'); [os.makedirs(os.path.join(A, s), exist_ok=True) for s in ('m', 'team')]
# proposal PDF (kit v1.8): the one PDF in <job>/proposal/ ships with the page and becomes the Proposal PDF button, top right
PDFS = sorted(glob.glob(os.path.join(CB, 'proposal', '*.pdf')))
if len(PDFS) > 1: die('keep one proposal PDF in proposal/, found ' + ', '.join(os.path.basename(f) for f in PDFS))
PDF = os.path.basename(PDFS[0]) if PDFS else None
if PDF: shutil.copy(PDFS[0], os.path.join(A, PDF))
CACHE = os.path.join(HERE, '.cache'); os.makedirs(os.path.join(CACHE, 'm'), exist_ok=True)
def cached(src, dst):
    c = os.path.join(CACHE, dst)
    if os.path.exists(c) and os.path.getmtime(c) > os.path.getmtime(src): shutil.copy(c, os.path.join(A, dst)); return True
    return False
def keep(dst): shutil.copy(os.path.join(A, dst), os.path.join(CACHE, dst))
def jpg(src, dst, width=None, q=82):
    if cached(src, dst): return
    im = Image.open(src).convert('RGB')
    if width and im.width > width: im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    im.save(os.path.join(A, dst), 'JPEG', quality=q, optimize=True, progressive=True); keep(dst)
H = os.path.join(CB, 'hero')   # JOB: Mapos renderings (A-003, A-004) for the hero, the gallery and the close
jpg(os.path.join(H, 'mapos_west.jpg'), 'hero.jpg', width=2400, q=84); jpg(os.path.join(H, 'mapos_west_p.jpg'), 'hero_p.jpg', q=82)
for n, f in [('g1.jpg', 'mapos_east.jpg'), ('g2.jpg', 'mapos_atrium.jpg'), ('g3.jpg', 'mapos_library.jpg')]: jpg(os.path.join(H, f), n, width=1760, q=80)
jpg(os.path.join(H, 'mapos_dining.jpg'), 'dusk.jpg', width=2400, q=80); jpg(os.path.join(H, 'mapos_dining_p.jpg'), 'dusk_p.jpg', q=80)
def edge_clean(im):
    a = np.asarray(im).copy(); al = a[..., 3].astype(float); al[al < 8] = 0
    h, w = al.shape
    rx = np.minimum(np.clip(np.arange(w) / (0.05 * w), 0, 1), np.clip((w - 1 - np.arange(w)) / (0.10 * w), 0, 1))
    ry = np.minimum(np.clip(np.arange(h) / (0.05 * h), 0, 1), np.clip((h - 1 - np.arange(h)) / (0.07 * h), 0, 1))
    f = (ry[:, None] * rx[None, :]) ** 0.8
    al = np.where(al >= 250, al, al * f); a[..., 3] = al.astype(np.uint8)   # fade only the soft shadow, so the block corners stay crisp
    return Image.fromarray(a, 'RGBA')
for f in FRAMES:
    src = os.path.join(MD, f + '.png')
    if not cached(src, 'm/' + f + '.webp'):
        edge_clean(Image.open(src).convert('RGBA').crop(CROP)).save(os.path.join(A, 'm', f + '.webp'), 'WEBP', quality=88, method=6); keep('m/' + f + '.webp')
for _n, _t, ph in TEAM: shutil.copy(os.path.join(KIT, 'assets', 'img', ph), os.path.join(A, 'team', ph))
IMG = os.path.join(KIT, 'assets', 'img')   # kit v1.5: logos and fonts come from the kit
shutil.copy(os.path.join(IMG, 'mc-wordmark-rev.png'), os.path.join(A, 'mc-white.png'))
shutil.copy(os.path.join(IMG, 'mc-wordmark.png'), os.path.join(A, 'mc-ink.png'))
wm = Image.open(os.path.join(IMG, 'mc-wordmark-rev.png')).convert('RGBA')
Image.merge('RGBA', (Image.new('L', wm.size, 255),) * 3 + (wm.split()[3],)).save(os.path.join(A, 'mc-white-all.png'), optimize=True)
if SEL: SELX.update(A=A, HERO=os.path.join(H, 'mapos_west.jpg')); selbuild.assets(SEL, SELX)   # JOB: the photo the crop: refs read
font = lambda f: base64.b64encode(open(os.path.join(KIT, 'assets', 'fonts', f), 'rb').read()).decode()

# ================================================================ the M, traced from M LOGO 2026 (three pieces)
M_PIECES = ['0,0 0,652 183,652 183,275 380,488 515,350 196,0', '773,124 586,310 586,652 773,652', '773,0 571,0 399,175 533,322 773,82']
def mark(cls, fill='currentColor'):
    return f'<svg class="{cls}" viewBox="0 0 773 652" aria-hidden="true">' + ''.join(f'<polygon class="mp mp{k}" points="{p}" fill="{fill}"/>' for k, p in enumerate(M_PIECES)) + '</svg>'
FAVICON = 'data:image/svg+xml;base64,' + base64.b64encode(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-60 -120 893 893"><rect x="-60" y="-120" width="893" height="893" rx="160" fill="#0028cc"/>{"".join(f"<polygon points=\"{p}\" fill=\"#fff\"/>" for p in M_PIECES)}</svg>'.encode()).decode()

# ================================================================ markup
DLICON = '<svg viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M8 2v8.5M4.5 7 8 10.5 11.5 7M2.5 13.5h11" stroke="currentColor" stroke-width="1.4"/></svg>'
def pdf_link(cls):
    return f'<a class="{cls}" href="assets/{E(PDF)}" download="{E(PDF)}" data-pdf>{DLICON}<span>Proposal PDF</span></a>' if PDF else ''
ARROW = '<svg viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M2 8h11M9 3.5 13.5 8 9 12.5" stroke="currentColor" stroke-width="1.4"/></svg>'
PLUS = '<svg class="pl" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M8 2v12M2 8h12" stroke="currentColor" stroke-width="1.4"/></svg>'
NAV = [('project', 'Project'), ('design', 'Design'), ('budget', 'Budget')] + ([('selections', 'Selections')] if SEL else []) + [('schedule', 'Schedule'), ('approach', 'Approach')]
kick = lambda t, cls='': f'<p class="kick {cls}"><i></i>{E(t)}</p>'
def odo(v, i=''):
    return f'<span class="odo num"{f" id={chr(34)}{i}{chr(34)}" if i else ""} data-v="{E(v)}" role="img" aria-label="{E(v)}">{E(v)}</span>'
def ramp(n, a=(0, 26, 138), b=(207, 216, 247)):
    return ['#%02x%02x%02x' % tuple(round(a[k] + (b[k] - a[k]) * (i / max(1, n - 1))) for k in range(3)) for i in range(n)]
OPC = '#9aa1b2'

s0 = STEPS[0]
stage_imgs = ''.join(f'<img src="assets/m/{f}.webp" alt="" decoding="async"{" loading=lazy" if i > 3 else ""}>' for i, f in enumerate(FRAMES))
nav_links = ''.join(f'<a href="#{i}">{E(t)}</a>' for i, t in NAV)
menu_links = ''.join(f'<a href="#{i}"><small>{k + 1:02d}</small>{E(t)}</a>' for k, (i, t) in enumerate(NAV))
elist = ''.join(f'<button type="button"><span>{i + 1:02d}</span><span>{E(n)}</span><span class="num">{money(v)}</span></button>' for i, (k, n, v, s) in enumerate(ELS))
elist += f'<div class="elist__rest"><span></span><span>Building, Site and Systems</span><span class="num">{money(REST)}</span></div>'
rail = ''.join(f'<button type="button" data-step="{j}"{" class=on" if j == 0 else ""}>{t}</button>' for j, t in [(0, 'Existing Building'), (1, 'New Work'), (2, 'Complete'), (3, TITLE_EL)])

def view_rows(items, colors, expandable):
    out = ''
    for k, (it, c) in enumerate(zip(items, colors)):
        lines = ''.join(f'<li>{"<span class=\"cd num\">" + E(ln["code"]) + "</span>" if ln.get("code") else ""}<span>{E(ln["item"])}</span></li>' for ln in it['lines'])   # line items only, no line pricing
        scope = f'<p>{E(it["scope"])}</p>' if it.get('scope') else ''
        head = f'<span class="sq"></span><div class="brow__t"><h3>{E(it["head"])}</h3>{scope}</div><span class="v num">{money(it["v"])}</span><span class="pct num">{pct(it["v"], DIRECT)}</span>'
        out += (f'<div class="brow" style="--c:{c}" data-k="{k}"><button type="button" class="brow__h" aria-expanded="false">{head}{PLUS}</button><ul class="brow__l" hidden>{lines}</ul></div>')
    return out
gcol = ['#001a8a', '#0028cc', '#2f50d6', '#5a74df', '#8598e8', '#adbbf0', '#cfd8f7']
dcol = ramp(len(DIVS))
EL_ITEMS = [{'head': g['name'], 'scope': g['scope'], 'v': g['v'], 'lines': g['lines']} for g in GROUPS]
MF_ITEMS = [{'head': f'{dv["n"]}  {dv["name"]}', 'v': dv['v'], 'lines': dv['lines']} for dv in DIVS]
def segs(items, colors):
    return ''.join(f'<i style="--w:{float(it["v"] / BASE * 100):.3f}%;--c:{c};--k:{k}" title="{E(it["head"])}"></i>' for k, (it, c) in enumerate(zip(items, colors))) + \
        f'<i style="--w:{float(OP / BASE * 100):.3f}%;--c:{OPC};--k:{len(items)}" title="Fee 6% and Insurance 3%"></i>'
op_row = f'<div class="brow brow--op" style="--c:{OPC}"><div class="brow__h"><span class="sq"></span><div class="brow__t"><h3>Fee and Insurance</h3></div><span class="v num">{money(OP)}</span><span class="pct num">{pct(OP, DIRECT)}</span><span class="pl"></span></div></div>'

g_ms = ''.join(f'<div style="left:{w / SPAN * 100:.3f}%"><b>Week {w}</b><span>{E(l)}</span></div>' for w, l in MS)
g_rows = ''.join(f'<div class="g-row" data-a="{r["a"]:.3f}" data-b="{r["b"]:.3f}"><div class="g-name">{E(r["name"])}</div><div class="g-track"><i class="g-bar" style="left:{r["a"] / SPAN * 100:.3f}%;width:{(r["b"] - r["a"]) / SPAN * 100:.3f}%;--c:{r["c"]}"><b class="g-fill"></b></i></div></div>' for r in SROWS)
g_legend = ''.join(f'<li style="--c:{c}" data-a="{a:.3f}" data-b="{b:.3f}"><i></i><b>{E(n)}</b><span>Weeks {a:.0f} to {b:.0f}</span><em aria-hidden="true"></em></li>' for n, c, a, b in PH_SPANS)
_band = 8 if SPAN > 30 else 5
g_grid = ''.join(f'<u style="left:{a / SPAN * 100:.3f}%;width:{(min(a + _band, SPAN) - a) / SPAN * 100:.3f}%"></u>' for a in range(_band, int(SPAN), 2 * _band)) + \
    ''.join(f'<i style="left:{w / SPAN * 100:.3f}%"></i>' for w in range(0, int(SPAN) + 1, 2 if SPAN > 30 else 1))
_ticks = sorted(set(list(range(0, int(SPAN), _band)) + [int(SPAN)]))
g_axis = '<i></i><div>' + ''.join(f'<span style="left:{t / SPAN * 100:.3f}%">{"Week " if t == 0 else ""}{t}</span>' for t in _ticks) + '</div>'

acard = lambda a: f'<div class="acard"><span class="acard__v num">{E(a["v"])}</span><h3>{E(a["label"])}</h3><p>{E(a["basis"])}</p></div>'
_num = lambda v: float(re.sub(r'[^\d.]', '', v.split(' per ')[0]) or 0)
_al = sorted([a for a in ALLOWS if 'per SF' not in a['v']], key=lambda a: -_num(a['v'])); _amax = _num(_al[0]['v']) if _al else 1   # ranked ledger, a bar per allowance
allow_rows = ''.join(f'<div class="aled__row" style="--w:{_num(a["v"]) / _amax * 100:.2f}%;--k:{k}"><span class="aled__n num">{k + 1:02d}</span><div class="aled__t"><h3>{E(a["label"])}</h3><p>{E(a["basis"])}</p></div><div class="aled__bar" aria-hidden="true"><i></i></div><span class="aled__v num">{E(a["v"])}</span></div>' for k, a in enumerate(_al))
rate_cells = ''.join(f'<div class="arate__c"><div class="arate__t"><h3>{E(a["label"])}</h3><p>{E(a["basis"])}</p></div><span class="arate__v num">{E(a["v"].split(" per ")[0])}<small>per {E(a["v"].split(" per ")[1])}</small></span></div>' for a in ALLOWS if 'per SF' in a['v'])
alts = ''.join(f'<div class="alt"><div><h3>{E(a["title"])}</h3><p>{E(a["note"])}</p></div><span class="v num">{money(a["v"])}</span><button type="button" class="tog" role="switch" aria-checked="false" data-id="{a["id"]}" aria-label="Add {E(re.sub(r"^[0-9]+[.] ", "", a["title"]))}"></button></div>' for a in ALTS)
ves = ''.join(f'<div class="alt alt--ve"><div><h3>{E(a["title"])}</h3><p>{E(a["note"])}</p></div><span class="v num">{money_s(a["v"])}</span><button type="button" class="tog" role="switch" aria-checked="false" data-id="{a["id"]}" aria-label="Apply {E(re.sub(r"^[0-9]+[.] ", "", a["title"]))}"></button></div>' for a in VES)
ncol = lambda h, items: f'<details class="ncol"><summary><h3>{E(h)}</h3><span class="ncol__n num">{len(items):02d}</span></summary><ol>{"".join(f"<li>{E(x)}</li>" for x in items)}</ol></details>'
tiers = ''.join(f'<article class="tier" data-r="up"><b class="tier__n num">{n}</b><h3>{E(h)}</h3><p class="tier__sub">{E(sub)}</p><ul>{"".join(f"<li>{E(x)}</li>" for x in xs)}</ul></article>' for n, h, sub, xs in TIERS)
people = ''.join(f'<figure class="person"><div class="person__img"><img src="assets/team/{ph}" alt="{E(n)}" loading="lazy" decoding="async"></div><figcaption><b>{E(n)}</b><span>{E(t)}</span></figcaption></figure>' for n, t, ph in TEAM)
os_feat = ''.join(f'<li><span class="osx__no">{k + 1:02d}</span><b>{E(a)}</b><em>{E(b)}</em></li>' for k, (a, b) in enumerate(OS_FEATURES))
# Montana OS (kit v1.10): outline OS letters top right, and this job as it opens in the system, its real numbers as tiles
OS_LETTERS = ('<svg class="osx__os" viewBox="-4 -4 548 258" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="miter">'
              '<polygon points="48,0 202,0 250,48 250,202 202,250 48,250 0,202 0,48"/><polygon points="92,62 158,62 180,84 180,166 158,188 92,188 70,166 70,84"/>'
              '<polygon points="342,0 540,0 540,62 378,62 366,74 366,92 378,104 488,104 540,156 540,198 488,250 290,250 290,188 452,188 464,176 464,158 452,146 342,146 290,94 290,52"/></g></svg>')
OS_TILES = [('Base Budget', money(BASE), 'Job cost tracked against it, line by line.', True),
            ('Line Items', f'{len(LINES)}', 'Every line of this budget, in one place.', False),
            ('Schedule', f'{SCH["weeks"]} Weeks', 'From mobilization. Roadblocks flagged the day they appear.', False)]
if SEL: OS_TILES.append(('Selections', f'{len(SEL["elements"])}', 'Each one requested and confirmed in writing.', False))
os_tiles = ''.join(f'<div class="osx__tile{" osx__tile--navy" if hi else ""}"><span class="osx__tk">{E(k)}</span><b class="num">{E(v)}</b><p>{E(d)}</p><em aria-hidden="true">{i + 1:02d}</em></div>' for i, (k, v, d, hi) in enumerate(OS_TILES))
os_for = ''.join(f'<div><p>{E(a)}</p><h4>{E(b)}</h4></div>' for a, b in OS_FOR)
GAL = [('g1.jpg', 'East Elevation'), ('g2.jpg', 'Conservatory'), ('g3.jpg', 'Library')]

# the pre-con funnel: the price gets more certain at each phase (shape only, no percentages)
def funnel(cls='funnel'):   # one tick per phase at its column center, so the labels below line up
    W_, H_, mid, n = 1000, 300, 150, len(PC_PHASES)
    cx = [W_ * (i + .5) / n for i in range(n)]; hw = [p[2] / PC_PHASES[0][2] * 120 for p in PC_PHASES]
    xs, ws = [20] + cx + [W_ - 20], [hw[0]] + hw + [hw[-1]]
    top = f'M{xs[0]},{mid - ws[0]}' + ''.join(f' C{(xs[i - 1] + xs[i]) / 2},{mid - ws[i - 1]} {(xs[i - 1] + xs[i]) / 2},{mid - ws[i]} {xs[i]},{mid - ws[i]}' for i in range(1, len(xs)))
    bot = f'L{xs[-1]},{mid + ws[-1]}' + ''.join(f' C{(xs[i] + xs[i - 1]) / 2},{mid + ws[i]} {(xs[i] + xs[i - 1]) / 2},{mid + ws[i - 1]} {xs[i - 1]},{mid + ws[i - 1]}' for i in range(len(xs) - 1, 0, -1)) + 'Z'
    lines = ''.join(f'<line x1="{x}" y1="{mid - hw[i] - 10}" x2="{x}" y2="{mid + hw[i] + 10}" class="fz-tick"/>' for i, x in enumerate(cx))
    return f'<svg class="{cls}" viewBox="0 0 {W_} {H_}" role="img" aria-label="The price gets more certain across four phases and ends in a Guaranteed Maximum Price"><path class="fz-band" d="{top} {bot}"/><line x1="{xs[0]}" y1="{mid}" x2="{xs[-1]}" y2="{mid}" class="fz-mid"/>{lines}<circle cx="{xs[0]}" cy="{mid}" r="7" class="fz-dot"/></svg>'
pc_cols = ''.join(f'<div class="pcph"><span class="pcph__k">{E(k)}</span><h4>{E(n)}</h4><p class="pcph__lab">Locks In</p><p class="pcph__lock">{E(lk)}</p><span class="pcph__t">{E(t)}</span></div>'
                  for n, k, w, lk, t, short in PC_PHASES)
pc_cards = ''.join(f'<article class="pccard"><div class="pccard__top"><span>{E(k)}</span><span>{E(next(p[4] for p in PC_PHASES if p[1] == k))}</span></div><h4>{E(t)}</h4><ul>{"".join(f"<li>{E(x)}</li>" for x in xs)}</ul><p class="pccard__get"><span>You Get</span>{E(g)}</p></article>' for k, t, xs, g in PC_CARDS)
PCF_LABS = ''.join(f'<span><b>{E(short)}</b>{E(k)}</span>' for n, k, w, lk, t, short in PC_PHASES)
pc_prom = ''.join(f'<div class="pcprom"><h4>{E(a)}</h4><p>{E(b)}</p></div>' for a, b in PC_PROMISES)
pc_prin = ''.join(f'<div class="pcprin"><h4>{E(a)}</h4><p>{E(b)}</p></div>' for a, b in PC_PRINCIPLES)

PNAME = 'The Inn at Kirkside'   # JOB
DATA = {'base': str(BASE), 'frame': list(FR), 'points': {k: PTS[k] for k, *_r in ELS}, 'bb': BB,
        'els': [{'k': k, 'name': n, 'v': str(v)} for k, n, v, s in ELS], 'rest': str(REST),
        'alts': [{'id': a['id'], 'title': a['title'], 'v': str(a['v'])} for a in ALTS + VES], 'span': SPAN, 'weeks': SCH['weeks'], 'name': PNAME, 'job': 'E26044', 'email': EMAIL,
        'sel': selbuild.data(SEL, SELX) if SEL else None,
        'steps': [{k: s.get(k) for k in ('label', 'title', 'sub', 'fig', 'cap', 'body', 'img', 'via', 'el', 'all', 'rail', 'note') if s.get(k) is not None} for s in STEPS]}

BODY = f'''
<div class="loader" id="loader" aria-hidden="true"><div class="loader__in">{mark("loader__m")}<div class="loader__bar"><i id="loader-bar"></i></div></div></div>

<header class="nav" id="nav">
  <a class="nav__logo" href="#top" aria-label="Montana Contracting, back to the top"><img class="lg-white" src="assets/mc-white.png" alt="Montana Contracting" width="240" height="14"><img class="lg-ink" src="assets/mc-ink.png" alt="" width="240" height="14"><img class="lg-allw" src="assets/mc-white-all.png" alt="" width="240" height="14"></a>
  <nav class="nav__links" aria-label="Sections">{nav_links}</nav>
  <div class="nav__right">{pdf_link("nav__cta nav__pdf")}<button type="button" class="nav__menu" id="menu-btn" aria-expanded="false" aria-controls="menu" aria-label="Menu"><span></span><span></span></button></div>
  <i class="nav__prog" aria-hidden="true"></i>
</header>
<div class="menu" id="menu" inert data-lenis-prevent><button type="button" class="menu__close">Close</button><nav aria-label="Sections">{menu_links}</nav>{pdf_link("btn btn--ghost")}</div>

<main>
<section class="hero" id="top" aria-label="{E(PNAME)}">
  <div class="hero__bg"><picture><source media="(max-width: 760px)" srcset="assets/hero_p.jpg"><img id="hero-img" data-crit fetchpriority="high" src="assets/hero.jpg" alt="{E(PNAME)}, rendering by Mapos" width="2400" height="1136"></picture></div>
  <div class="hero__scrim"></div><div class="hero__shade"></div>
  <div class="hero__inner gut">
    <div class="tags"><span class="tag">Budget Presentation</span><span class="tag tag--ghost">{LOC}</span><span class="tag tag--ghost">Inn and Restaurant</span></div>
    <h1 data-r>{E(PNAME)}</h1>
    <p class="eyebrow"><i></i>Mapos · 53865 State Highway 30</p>
  </div>
  <a class="hero__scroll" href="#project">Scroll<i></i></a>
</section>

<section class="intro" id="project" aria-label="Project">
  <div class="wrap">
    {kick("01 / Project")}
    <h2 class="sec-title" data-r>Project Details</h2>
    <div class="intro__grid">
      <dl class="facts" data-r="up">
        <div><dt>Location</dt><dd>{LOC}</dd></div>
        <div><dt>Type</dt><dd>Inn and Restaurant</dd></div>
        <div><dt>Architect</dt><dd>Mapos</dd></div>
        <div><dt>Budget</dt><dd class="num">{money(BASE)}</dd></div>
        <div><dt>Schedule</dt><dd>{SCH["weeks"]} Weeks</dd></div>
      </dl>
      <div class="desc"><p class="lede">{E(PROSE[0])}</p></div>
    </div>
  </div>
</section>

<section class="gallery" id="gallery" aria-label="Gallery">
  <div class="gallery__pin">
    <div class="wrap gallery__head">{kick("Gallery")}<span class="gallery__count num"><b>01</b> / 03</span></div>
    <div class="track">{"".join(f'<figure class="shot"><div class="shot__img"><img src="assets/{f}" alt="{E(PNAME)}, {E(c)}" loading="lazy" decoding="async"></div><figcaption><b>{k + 1:02d}</b>{E(c)}</figcaption></figure>' for k, (f, c) in enumerate(GAL))}</div>
  </div>
</section>

<section class="stage" id="stage" aria-label="Design">
  <span class="stage__anchor" id="design" style="top:0"></span>
  <div class="stage__pin">
    <div class="stage__model"><div class="frame" data-mk="brackets" style="--fa:{FR[0]} / {FR[1]}">{stage_imgs}
      <span class="mk" id="mk" aria-hidden="true"></span>
      <span class="mkb" id="mkb" aria-hidden="true"><i></i><i></i><i></i><i></i></span>
      <span class="mkl" id="mkl" aria-hidden="true"><i></i><b></b></span>
      <span class="mkn" id="mkn" aria-hidden="true"></span>
      {"".join(f'<span class="mks" data-k="{k}" aria-hidden="true">{i + 1}</span>' for i, (k, *_r) in enumerate(ELS))}
    </div></div>
    <div class="stage__copy" aria-live="polite">
      <p class="kick sc-label sw">{E(s0["label"])}</p>
      <h2 class="sc-title sw">{E(s0["title"])}</h2>
      <p class="sc-sub sw"></p>
      <div class="sc-fig">{odo(s0["fig"], "stage-odo")}</div>
      <p class="sc-cap sw">{E(s0["cap"])}</p>
      <p class="sc-body sw"></p>
      <div class="elist hide"><p class="elist__h">Base Budget with Fee and Insurance</p>{elist}<div class="elist__tot"><span></span><span>Base Budget</span><span class="num">{money(BASE)}</span></div></div>
    </div>
    <div class="stage__rail" role="group" aria-label="Steps">{rail}</div>
    <p class="stage__note">{E(s0["note"])}</p>
  </div>
</section>

<section class="budget" id="budget" aria-label="Budget">
  <div class="wrap">
    {kick("03 / Budget")}
    <div class="budget__fig">{odo(money(BASE), "budget-odo")}</div>
    <p class="budget__cap" data-r="up"><span><b>Base Budget</b> with Fee and Insurance</span><span><b class="num">{money(DIRECT)}</b> Direct Cost</span><span><b>6% Fee</b> and <b>3% Insurance</b></span></p>
    <div class="bview" data-view="el">
      <div class="sbar sbar--el" aria-hidden="true">{segs(EL_ITEMS, gcol)}</div>
      <div class="sbar sbar--mf" aria-hidden="true">{segs(MF_ITEMS, dcol)}</div>
      <div class="pills" role="tablist" aria-label="Budget view"><button type="button" role="tab" class="pill on" aria-selected="true" data-v="el">Elements</button><button type="button" role="tab" class="pill" aria-selected="false" data-v="mf">MasterFormat</button></div>
      <div class="brows brows--el" role="tabpanel" aria-label="Elements">{view_rows(EL_ITEMS, gcol, True)}</div>
      <div class="brows brows--mf" role="tabpanel" aria-label="MasterFormat" hidden>{view_rows(MF_ITEMS, dcol, True)}</div>
    </div>
    <div class="btot"><div class="btot__direct"><span>Direct Cost</span><span class="num">{money(DIRECT)}</span></div><div class="btot__op"><span>Design Contingency (TBD), 0%</span><span class="num">{money(0)}</span></div><div class="btot__op" style="--c:{OPC}"><span><i class="sq" aria-hidden="true"></i>Fee 6%</span><span class="num">{money(FEE)}</span></div><div class="btot__op" style="--c:{OPC}"><span><i class="sq" aria-hidden="true"></i>Insurance 3%</span><span class="num">{money(INS)}</span></div><div><span>Base Budget</span><span class="num">{money(BASE)}</span></div></div>
  </div>
</section>

{selbuild.section(SEL, SELX, kick) if SEL else selbuild.sheet(None, E)}

<section class="allow" id="allowances" aria-label="Allowances">
  <div class="wrap">
    {kick("03 / Allowances")}
    <div class="allow__top"><h2 class="sec-title" data-r>Allowances</h2><div class="allow__fig"><span class="big2 num" data-r="up">{money(ALLOW_TOTAL)}</span><p>Included in Base Budget</p></div></div>
    <div class="aled" data-r="up">{allow_rows}</div>
    <div class="arate" data-r="up"><p class="arate__h">Material Allowances, Per SF</p><div class="arate__row">{rate_cells}</div></div>
  </div>
</section>

<section class="alts" id="alternates" aria-label="Alternates">
  <div class="wrap">
    {kick("03 / Alternates")}
    <div class="alts__grid">
      <div>
        <h2 class="sec-title" data-r>Alternates</h2>
        <div class="alist">{alts}</div>
        <h2 class="sec-title alts__ve" id="value-engineering" data-r>Value Engineering</h2>
        <div class="alist">{ves}</div>
      </div>
      <aside class="atot" aria-label="Running total">
        <dl><div><dt>Base Budget</dt><dd class="num">{money(BASE)}</dd></div><div><dt>Requested</dt><dd class="num" id="alt-add">{money(0)}</dd></div></dl>
        <div class="atot__fig"><span class="lab">If Montana Confirms</span>{odo(money(BASE), "alt-odo")}</div>
        <button type="button" class="btn btn--navy" id="alt-send"><span>Send to Montana</span></button>
      </aside>
    </div>
  </div>
</section>

<section class="notes" id="notes" aria-label="Notes and Clarifications">
  <div class="wrap">
    {kick("03 / Notes and Clarifications")}
    <h2 class="sec-title" data-r>Notes and Clarifications</h2>
    <div class="ngrid">{ncol("Basis of Budget", BASIS)}{ncol("Clarifications", CLAR)}{ncol("Exclusions", EXCL)}</div>
  </div>
</section>

<section class="sched" id="schedule" aria-label="Schedule">
  <div class="sched__pin">
    <div class="wrap sched__grid">
      <aside class="sched__side">
        {kick("04 / Schedule")}
        <div class="sched__top">
          <span class="big num" data-r="up">{SCH["weeks"]}</span>
          <h2 data-r>Weeks on site from mobilization.</h2>
        </div>
        <p class="sched__now"><span>Week</span>{odo("00", "week-odo")}<span class="sched__ph" id="week-ph">Demolition and Site</span></p>
        <ul class="g-legend">{g_legend}</ul>
      </aside>
      <div class="gantt" role="img" aria-label="Schedule by trade, {SCH['weeks']} weeks from mobilization to work complete">
        <div class="g-ms">{g_ms}</div>
        <div class="g-body"><div class="g-grid" aria-hidden="true">{g_grid}<b class="g-cursor" id="g-cursor"><span class="g-cursor__l">Week <em id="g-cw">0</em></span></b></div>{g_rows}</div>
        <div class="g-axis">{g_axis}</div>
      </div>
    </div>
  </div>
</section>

<section class="appr" id="approach" aria-label="Approach">
  <div class="wrap">
    {kick("05 / Approach")}
    <h2 class="appr__h" data-r>How We Work</h2>
    <p class="appr__big" data-r="up">Every superintendent is a finish carpenter by trade.</p>
    <div class="yteam">
      <div class="yteam__head" data-r="up"><h3 class="yteam__h">Your Team</h3><p class="yteam__p">Three principals stay on this project from the first walkthrough to the final punch list. You are never handed off.</p></div>
      <div class="people">{people}</div>
    </div>
  </div>
</section>

<section class="pcf" id="pre-construction" aria-label="Pre-Construction">
  <div class="wrap">
    <div class="pcf__card" data-precon role="button" tabindex="0" aria-label="See our pre-construction process">
      {mark("pcf__m")}
      <div class="pcf__txt">
        <p class="kick kick--light"><i></i>Pre-Construction</p>
        <h2 class="pcf__h">See Our <span class="nb">Pre-Construction</span> Process</h2>
        <p class="pcf__p">Four phases. One Guaranteed Maximum Price.</p>
        <span class="btn btn--white pcf__btn">See the Process {ARROW}</span>
      </div>
      <div class="pcf__viz" data-r="up" aria-hidden="true">{funnel("funnel funnel--d")}<div class="pcf__labs">{PCF_LABS}</div></div>
    </div>
  </div>
</section>

<section class="dusk" aria-label="Thank You">
  <picture><source media="(max-width: 760px)" srcset="assets/dusk_p.jpg"><img src="assets/dusk.jpg" alt="{E(PNAME)} at dusk, lit from inside" loading="lazy" decoding="async"></picture>
  <div class="dusk__scrim"></div>
  <div class="dusk__in gut"><h2 data-r>Thank you for the opportunity to partner with you on this project.</h2></div>
</section>

<section class="cta" id="contact" aria-label="Next Step">
  {mark("cta__m")}
  <div class="wrap cta__in">
    {kick("Contact", "kick--light")}
    <div class="cta__act"><a class="btn btn--white mag" href="tel:+18453981778">Call {PHONE} {ARROW}</a></div>
    <dl class="contact"><div><dt>Phone</dt><dd>{PHONE}</dd></div><div><dt>Offices</dt><dd>{E(ADDR)}</dd></div><div><dt>Email</dt><dd>{E(EMAIL)}</dd></div></dl>
  </div>
</section>
<footer class="foot"><div class="wrap foot__in"><img src="assets/mc-white-all.png" alt="Montana Contracting" loading="lazy"><span>General Contractor · Since 1984 · Congers, NY · Jefferson, NY</span><span>© 2026 Montana Contracting</span></div></footer>
</main>

<div class="pc" id="precon" inert>
  <div class="pc__panel" role="dialog" aria-modal="true" aria-labelledby="pc-h" data-lenis-prevent>
    <div class="pc__bar"><img src="assets/mc-white-all.png" alt="Montana Contracting" width="200" height="12"><span>Pre-Construction · Optional Next Step</span><button type="button" class="pc__x">Close</button></div>
    <div class="pc__hero">
      {mark("pc__m")}
      <div class="wrap">
        <p class="kick kick--light"><i></i>Pre-Construction</p>
        <h2 id="pc-h">Know the number<br><em>before</em> you build.</h2>
      </div>
    </div>
    <div class="pc__body">
      <section class="wrap pc__sec">
        <p class="kick"><i></i>01 · Every Phase</p>
        <h3>Your price gets more certain at every phase.</h3>
        <div class="pc__funnel">{funnel()}<div class="pcphs">{pc_cols}</div></div>
      </section>
      <section class="pc__alt"><div class="wrap pc__sec">
        <p class="kick"><i></i>02 · What Each Phase Delivers</p>
        <div class="pccards">{pc_cards}</div>
      </div></section>
      <section class="wrap pc__sec">
        <p class="kick"><i></i>03 · Our Promises</p>
        <div class="pcproms">{pc_prom}</div>
      </section>
      <section class="pc__end"><div class="wrap pc__sec">
        <h3>Ask us about <span class="nb">pre-construction.</span></h3>
        <dl class="contact"><div><dt>Phone</dt><dd>{PHONE}</dd></div><div><dt>Email</dt><dd>{E(EMAIL)}</dd></div><div><dt>Offices</dt><dd>{E(ADDR)}</dd></div></dl>
      </div></section>
    </div>
  </div>
</div>

<script type="application/json" id="cb-data">{json.dumps(DATA).replace("</", "<\\/")}</script>
<script>{open(os.path.join(KIT, "vendor", "lenis", "lenis.min.js")).read()}</script>
<script>{open(os.path.join(HERE, "src", "app.js")).read()}</script>
'''

FONTS = f'''@font-face {{ font-family: "TT Commons Pro"; font-weight: 400; font-style: normal; font-display: block; src: url(data:font/woff2;base64,{font("TTCommonsPro-Regular.woff2")}) format("woff2"); }}
@font-face {{ font-family: "TT Commons Pro"; font-weight: 600 700; font-style: normal; font-display: block; src: url(data:font/woff2;base64,{font("TTCommonsPro-Bold.woff2")}) format("woff2"); }}
'''
CSS = FONTS + open(os.path.join(HERE, 'src', 'style.css')).read()
TITLE = 'The Inn at Kirkside'
def tiny(name, w):   # a ~1 KB blurred stand-in, painted under the hero photo until it is decoded
    import io, base64
    im = Image.open(os.path.join(SITE, 'assets', name)).convert('RGB'); im = im.resize((w, max(1, round(im.height * w / im.width))), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, 'JPEG', quality=60); return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()
PH_D, PH_P = tiny('hero.jpg', 40), tiny('hero_p.jpg', 24)
PRELOAD = ('<link rel="preload" as="image" href="assets/hero.jpg" media="(min-width: 761px)" fetchpriority="high">\n'
           '<link rel="preload" as="image" href="assets/hero_p.jpg" media="(max-width: 760px)" fetchpriority="high">\n')
CSS += f'\n.hero__bg {{ background: #2b2f2a url({PH_D}) center / cover no-repeat; }}\n@media (max-width: 760px) {{ .hero__bg {{ background-image: url({PH_P}); }} }}\n'
HEAD = (PRELOAD + '<script>document.documentElement.classList.add("m")</script>\n' + f'<title>{TITLE}</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n<link rel="icon" href="{FAVICON}">\n'
        f'<meta name="description" content="Montana Contracting budget presentation for The Inn at Kirkside, 53865 State Highway 30, Roxbury, NY.">\n<style>\n{CSS}\n</style>\n')

# ================================================================ house rules on everything a client reads
BANNED = ['stunning', 'beautiful', 'breathtaking', 'luxury', 'luxurious', 'bespoke', 'elevated', 'curated', 'seamless', 'passion', 'dream', 'journey',
          'exceptional', 'world-class', 'premier', 'cutting-edge', 'unparalleled', 'empower', 'transform', 'peace of mind', 'potential risk', 'novaterra',
          'design move', 'nestled', 'state-of-the-art', 'elevate', 'proud to', 'excited', 'grateful']
text = re.sub(r'<script.*?</script>|<svg.*?</svg>', ' ', BODY, flags=re.S)
text = html.unescape(re.sub(r'<[^>]+>', ' ', text))
text += ' ' + ' '.join(str(v) for s in STEPS for v in s.values() if isinstance(v, str))
bad = [name for ch, name in [('—', 'em dash'), ('–', 'en dash'), (';', 'semicolon'), ('!', 'exclamation'), ('?', 'question')] if ch in text]
bad += ['banned: ' + w for w in BANNED if re.search(r'\b' + re.escape(w) + r'\b', re.sub(r'(marvin|signature) elevate', 'marvin product', text.lower()))]
if re.search(r'\b\w+, not \w+', text): bad.append('X, not Y')
if bad: die('copy rules: ' + ', '.join(bad))
if len(PROSE[0].split('. ')[0]) > 155: die('project snippet sentence is over 155 characters')
words = sum(len(p.split()) for p in PROSE)
if len(PROSE) != 1 or not 40 <= words <= 80: die(f'project description is {words} words (kit v1.14: one paragraph, 40 to 80)')
for s_ in STEPS:
    if s_.get('body'): die('design step carries body copy (kit v1.14)')
for v in [money(BASE), money(DIRECT), money(FEE), money(INS), money(EL_TOTAL), money(REST), money(SITE_FDN), money(ALLOW_TOTAL)] + [money(e[2]) for e in ELS]:
    if v not in BODY: die('figure missing from the page: ' + v)
_vis = re.sub(r'<script.*?</script>', '', BODY, flags=re.S)
_nc = re.search(r'\$\d[\d,]*(?![\d,]*\.\d\d)', _vis)
if _nc: die('a dollar figure without cents: ' + _vis[max(0, _nc.start() - 120):_nc.end() + 40])

os.makedirs(SITE, exist_ok=True)
import re as _re
HEAD = _re.sub(r'/\*[^*]*?(Montana OS|walk your plans|NOVATERRA)[^*]*?\*/', '', HEAD, flags=_re.I)
open(os.path.join(SITE, 'index.html'), 'w').write(HEAD + BODY)
shutil.copytree(SITE, NET)
open(os.path.join(NET, 'index.html'), 'w').write(f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n<meta name="robots" content="noindex, nofollow">\n<meta name="mcc-send" content="netlify-forms">\n{HEAD}</head>\n<body>\n{BODY}\n</body>\n</html>\n')
open(os.path.join(NET, 'robots.txt'), 'w').write('User-agent: *\nDisallow: /\n')
# JOB: zip name, <JOB>_Presentation_Netlify_v#.zip
z = os.path.join(HERE, 'E26044_Presentation_Netlify_v1.zip')
with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
    for dp, _d, fs in os.walk(NET):
        for f in fs: zf.write(os.path.join(dp, f), os.path.relpath(os.path.join(dp, f), NET))
json.dump({'base': money(BASE), 'direct': money(DIRECT), 'op': money(OP), 'elements': {n: money(v) for k, n, v, s in ELS}, 'el_total': money(EL_TOTAL), 'rest': money(REST),
           'site_fdn': money(SITE_FDN), 'allow_total': money(ALLOW_TOTAL), 'groups': {g['name']: money(g['v']) for g in GROUPS}, 'divisions': {dv['n'] + ' ' + dv['name']: money(dv['v']) for dv in DIVS},
           'alternates': {a['title']: money(a['v']) for a in ALTS}, 've': {a['title']: money_s(a['v']) for a in VES}, 'allowances': {a['label']: a['v'] for a in ALLOWS}, 'milestones': MS, 'phases': [(n, round(a, 2), round(b, 2)) for n, c, a, b in PH_SPANS]},
          open(os.path.join(HERE, 'figures.json'), 'w'), indent=1)
size = sum(os.path.getsize(os.path.join(dp, f)) for dp, _d, fs in os.walk(SITE) for f in fs)
print(f'built: page {os.path.getsize(os.path.join(SITE, "index.html")) / 1e6:.2f} MB, site {size / 1e6:.2f} MB, {len(STEPS)} steps, crop {CROP}, zip {os.path.getsize(z) / 1e6:.2f} MB')

# hand-off for the PDF proposal (generate-proposal-mcc): the same allowances, alternates and VE the page shows
json.dump({'allowances': ALLOWS, 'allowance_total': str(ALLOW_TOTAL),
           'alternates': [{'id': a['id'], 'title': a['title'], 'note': a['note'], 'v': str(a['v'])} for a in ALTS],
           've': [{'title': a['title'], 'v': str(a['v'])} for a in VES]}, open(os.path.join(HERE, 'proposal_lists.json'), 'w'), indent=1)

# JOB: scope lines by subdivision for the proposal PDF (client wording, no rates)
_sc = {}
for l in LINES.values():
    n = clean(l['item'], l['code'])
    _sc.setdefault(l['code'], [])
    if n not in _sc[l['code']]: _sc[l['code']].append(n)
json.dump({'divs': [{'n': dv['n'], 'name': dv['name'], 'v': str(dv['v'])} for dv in DIVS], 'lines': _sc}, open(os.path.join(HERE, 'scope_lines.json'), 'w'), indent=1)
