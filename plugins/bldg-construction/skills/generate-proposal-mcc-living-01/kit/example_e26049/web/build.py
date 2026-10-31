#!/usr/bin/env python3
"""Website-format presentation build. Job: E26049 1004 Old Albany Post Rd (from the kit reference E260050 The Cooper Barn, v5.2).

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
pct = lambda v, of: '{:.1f}%'.format(float(D(v) / D(of) * 100))


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
OP = C(DIRECT * D('0.15')); BASE = DIRECT + OP
sheet_total = C(ws.cell(ROW_TOTAL, 6).value)
if BASE != sheet_total: die(f'base {BASE} does not tie to the Estimate sheet total {sheet_total}')
ALT_ROWS, VE_ROWS, _cur = {}, {}, None   # alternate and value engineering totals (with markups), by number
for i, r in enumerate(ws.iter_rows(min_row=ROW_TOTAL + 1, max_row=ws.max_row, values_only=True), start=ROW_TOTAL + 1):
    h = str(r[0] or '')
    m_ = re.match(r'ALTERNATE (\d+) --', h) or re.match(r'VE-(\d+) --', h)
    if m_: _cur = (ALT_ROWS if h.startswith('ALTERNATE') else VE_ROWS, int(m_.group(1)))
    if r[0] == 'TOTAL' and isinstance(r[5], (int, float)) and _cur: _cur[0][_cur[1]] = C(r[5]); _cur = None

# JOB: client wording for lines whose estimator notes should not reach the page
ITEM_FIX = {'Import Topsoil (Thin on Rocky Lot': 'Import Topsoil (6" Minimum Over the Septic Area)',
            'F/I Roof Edge Metal / Gravel Stop': 'F/I Roof Edge Metal / Gravel Stop',
            'Floating Stair, Steel Stringer': 'Floating Stair, Steel Stringer w/ White Oak Treads (Allowance)',
            'SPDES Weekly Inspections': 'SPDES Weekly Inspections & Reports',
            'F/O Washer & Dryer': 'F/O Washer & Dryer',
            'Driveway Apron & Culvert': 'Driveway Apron & Culvert at Old Albany Post Rd',
            'Driveway Cut / Fill & Shaping': 'Driveway Cut / Fill & Shaping on Slope (Hairpin, Up to 14%)',
            'Freight, Duty / Tariff & Port Handling': 'Freight, Duty / Tariff & Port Handling on the Unilux Order',
            'Passive Radon Rough-In': 'Passive Radon Rough-In',
            'Crawl Space Dehumidifier': 'Crawl Space Dehumidifier',
            'Project Manager II': 'Project Manager'}
def clean(item):   # client wording for a line item: no bracketed estimator notes, no drawing references, no unit rates
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
    s = s.replace('(~', '(About ').replace('Every ~', 'About Every ').replace('~', 'About ').replace(' @ ', ' at ').replace('SSTS', 'Septic')
    s = re.sub(r'\(Allowance\)\s*\(Allowance\)', '(Allowance)', s)
    return plain(re.sub(r'\s{2,}', ' ', s).strip())

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
ROW_GROUP = {r: 'Site, Utilities and Driveway' for r in find_rows('Guard / Fence at Top of Parking Retaining Wall', n=1)}
SCOPE_FIX = {}
def group_of(r, l):
    if r in ROW_GROUP: return ROW_GROUP[r]
    for g in P['groups']:
        if l['trade'] in [tkey(t) for t in g['trades']]: return g['name']
    die('line has no group: ' + l['item'])
GROUPS = []
for g in P['groups']:
    rows = [(r, l) for r, l in LINES.items() if group_of(r, l) == g['name']]
    GROUPS.append({'name': g['name'], 'scope': SCOPE_FIX.get(g['name'], g['scope']), 'v': sum(l['v'] for r, l in rows),
                   'lines': [{'item': clean(l['item']), 'v': l['v']} for r, l in rows]})
if sum(g['v'] for g in GROUPS) != DIRECT: die('groups do not tie to direct cost')

MF_TITLES = {'01': 'General Requirements', '02': 'Existing Conditions', '03': 'Concrete', '04': 'Masonry', '05': 'Metals',
             '06': 'Wood, Plastics, and Composites', '07': 'Thermal and Moisture Protection', '08': 'Openings', '09': 'Finishes',
             '10': 'Specialties', '11': 'Equipment', '12': 'Furnishings', '22': 'Plumbing', '23': 'Heating, Ventilating, and Air Conditioning',
             '26': 'Electrical', '27': 'Communications', '28': 'Electronic Safety and Security', '31': 'Earthwork', '32': 'Exterior Improvements',
             '33': 'Utilities', '34': 'Transportation'}
# MasterFormat view = the proposal's Schedule of Values: one row per cost code (subdivision) as the workbook's SOV sheet lists it,
# direct cost, same names as the PDF proposal (SOV_NAMES), so the presentation and the proposal read line for line the same.
SOV_NAMES = {'Base Courses (RCA Driveway)': 'Gravel Driveway', 'Hardscaping (Patio Only)': 'Stone Patio',   # JOB: plain names, as on the proposal
             'Final Grading & Seeding (Landscaping Excluded)': 'Final Grading & Seeding', 'HVAC Testing, Balancing & Envelope Testing': 'HVAC & Envelope Testing',
             'Vegetated Roof (Green Roof)': 'Green Roof', 'Metal Stairs': 'Floating Stair'}
_sv, _on, SOV_TRADES = wb['SOV'], False, {}
for r in _sv.iter_rows(values_only=True):
    if r[0] == 'CSI' and r[1] == 'Trade': _on = True; continue
    if _on and r[0] in ('SUBTOTAL',): break
    if _on and r[0]: SOV_TRADES[str(r[0])] = SOV_NAMES.get(r[1], r[1])
MF = {}
for l in LINES.values():
    if l['code'] not in SOV_TRADES: die('line code not on the SOV sheet: ' + l['code'])
    MF.setdefault(l['code'], []).append({'item': clean(l['item']), 'v': l['v']})
DIVS = [{'n': k.replace('.', ' '), 'name': SOV_TRADES[k], 'v': sum(x['v'] for x in MF[k]), 'lines': MF[k]} for k in SOV_TRADES if k in MF]
if sum(d['v'] for d in DIVS) != DIRECT: die('SOV cost codes do not tie to direct cost')
for d in DIVS:   # each row must equal the workbook SOV row to the cent
    _w = next(C(r[2]) for r in _sv.iter_rows(values_only=True) if str(r[0]).replace('.', ' ') == d['n'])
    if _w != d['v']: die(f'SOV row {d["n"]} {d["v"]} vs workbook {_w}')

def el(rows):
    return C(sum(LINES[r]['v'] for r in rows) * D('1.15'))
# JOB: the signature elements, by Estimate row (found by their words), each x 1.15 with O&P.
EL_ROWS = {
    'windows': code_rows('08.54.00'),
    'cantilever': find_rows('Structural Steel: Cantilevered', n=1) + find_rows('F/I Closed-Cell Spray Foam @ Cantilevered Floor', n=1),
    'greenroof': code_rows('07.33.63', '08.62.00'),
    'siding': code_rows('07.46.00'),
    'stair': find_rows('Floating Stair', n=1) + find_rows('Frameless Glass Guard at Stair', n=1) + find_rows('Wall Handrail at Floating Stair', n=1),
    'porch': code_rows('10.71.00') + find_rows('Screened Deck Framing', n=1) + find_rows('Cumaru / Red Balau Decking @ Screened Deck', n=1),
}
if len(EL_ROWS['windows']) != 3 or len(EL_ROWS['greenroof']) != 4 or len(EL_ROWS['siding']) != 6 or len(EL_ROWS['porch']) != 3: die('element rows moved')
ELS = [
    ('windows', 'Unilux Window Walls and Lift-Slides', el(EL_ROWS['windows']), 'Triple-glazed Unilux Design Line windows and lift-slides, 1,429 SF of glass including the north glass wall, with freight and installation.'),
    ('cantilever', 'Cantilevered Upper Volume', el(EL_ROWS['cantilever']), 'The steel frame that carries the upper volume 6 feet 8 inches past the glass wall, with spray foam at the cantilevered floor.'),
    ('greenroof', 'Green Roofs and Skylights', el(EL_ROWS['greenroof']), 'A sedum tray system over 1,220 SF of the first-floor roofs, with a gravel edge, the first year of care and four Velux flat-roof skylights.'),
    ('siding', 'Vertical Wood Siding', el(EL_ROWS['siding']), '2,637 SF of vertical wood siding and 529 SF of matching soffits on a rain screen, with the metal trim and flashings.'),
    ('stair', 'Floating Stair', el(EL_ROWS['stair']), 'White oak treads on a steel stringer, 20 risers, with a frameless glass guard and a wall rail.'),
    ('porch', 'Screened Porch', el(EL_ROWS['porch']), '361 SF of hardwood decking on a framed deck, with Centor retractable screens at the openings.'),
]
EL_TOTAL = sum(e[2] for e in ELS)
REST = BASE - EL_TOTAL
SITE_FDN = C(sum(l['v'] for l in LINES.values() if l['code'][:2] in ('03', '31', '32', '33', '34')) * D('1.15'))   # JOB: site work, utilities and concrete

# JOB: allowances from the Notes sheet (Allowances and Material Allowances), by Estimate row.
ALLOW_ROWS = [('Structural Steel', 'Cantilever and glass wall beams and posts', find_rows('Structural Steel: Cantilevered', n=1)),
              ('Floating Stair', 'Steel stringer and white oak treads', find_rows('Floating Stair', n=1)),
              ('Cabinetry and Vanities', 'Kitchen, island, panels and bath vanities', code_rows('06.41.00')),
              ('Countertops', 'Supply, 100 SF', find_rows('Supply Countertops', n=1)),
              ('Appliances', 'Kitchen and laundry', code_rows('11.31.00')),
              ('Plumbing Fixtures', 'Mid-high end residential', code_rows('22.40.00')),
              ('Lighting Fixtures', 'Amerilux interior fixtures and exterior lights', code_rows('26.50.00')),
              ('Green Roof', 'Sedum tray system, 1,220 SF', find_rows('Green Roof Sedum Tray System', n=1)),
              ('Wood Siding and Soffits', 'Material, 3,166 SF', find_rows('F/O Wood Siding Material', 'F/O Wood Soffit Material', n=2)),
              ('Central Hudson Line Extension', 'Transformer pad and line extension', find_rows('Transformer Pad & Central Hudson', n=1)),
              ('Water Treatment', 'At the well', find_rows('Water Treatment', n=1))]
ALLOWS = [{'label': a, 'basis': b, 'v': money(sum(LINES[r]['v'] for r in rows_))} for a, b, rows_ in ALLOW_ROWS]
ALLOW_TOTAL = sum(sum(LINES[r]['v'] for r in rows_) for a, b, rows_ in ALLOW_ROWS)
ALLOWS += [{'label': 'Unilux Windows and Doors', 'basis': 'Supply', 'v': '$145.56 per SF'}, {'label': 'Siding and Soffits', 'basis': 'Material', 'v': '$14.00 per SF'},
           {'label': 'White Oak Flooring', 'basis': 'Material, site finished', 'v': '$15.00 per SF'}, {'label': 'Tile', 'basis': 'Material', 'v': '$50.00 per SF'},
           {'label': 'Countertops', 'basis': 'Material', 'v': '$75.00 per SF'}]

ALTS = [{'id': str(k), 'title': P['alternates'][str(k)]['title'], 'note': P['alternates'][str(k)]['note'], 'v': ALT_ROWS[k]} for k in sorted(ALT_ROWS)]
VES = [{'id': 've' + str(k), 'title': P['ve'][str(k)]['title'], 'note': P['ve'][str(k)]['note'], 'v': VE_ROWS[k]} for k in sorted(VE_ROWS)]
if len(ALTS) != 15 or len(VES) != 8: die('alternates or value engineering items moved')
money_s = lambda v: ('-' if C(v) < 0 else '') + money(abs(C(v)))   # signed figure for the value engineering deducts

# ================================================================ selections (kit v1.7): one card per element, prices from the workbook
sys.path.insert(0, os.path.join(KIT, 'tools', 'sel')); import selbuild
SEL_PATH = os.path.join(CB, 'selections.json')
SELX = {'C': C, 'die': die, 'money': money, 'E': E, 'ws': ws, 'LINES': LINES, 'find_rows': find_rows, 'code_rows': code_rows,
        'ALT_ROWS': ALT_ROWS, 'VE_ROWS': VE_ROWS, 'BASE': BASE, 'CB': CB, 'OP': D('0.15')}
SEL = selbuild.resolve(json.load(open(SEL_PATH)), SELX) if os.path.exists(SEL_PATH) else None

# ================================================================ schedule, in weeks from mobilization, by phase
d = lambda s: dt.date.fromisoformat(s)
mob = d(SCH['mob'])
PHASES = [('Site and Foundation', ['mob', 'drv', 'fdn', 'utl'], '#001a8a'), ('Structure', ['frm', 'stl'], '#0028cc'), ('Envelope', ['rfg', 'win', 'sid'], '#3d5bd9'),
          ('Systems', ['mep', 'gwb'], '#6a82e2'), ('Interiors', ['mill', 'flr'], '#93a5ec'), ('Closeout', ['site', 'pun'], '#b9c5f3')]   # JOB
phase_of = {k: (n, c) for n, ks, c in PHASES for k in ks}
SROWS = []
for r in SCH['rows']:
    n, c = phase_of[r['key']]
    SROWS.append({'name': r['name'], 'a': (d(r['s']) - mob).days / 7, 'b': ((d(r['f']) - mob).days + 1) / 7, 'phase': n, 'c': c})
SPAN = float(SCH['weeks'])   # the chart ends on the Work Complete line
for r in SROWS: r['b'] = min(r['b'], SPAN)   # the last finish date counts its own day, a fraction past the last week
PH_SPANS = [(n, c, min(r['a'] for r in SROWS if r['phase'] == n), max(r['b'] for r in SROWS if r['phase'] == n)) for n, ks, c in PHASES]
# JOB: schedule milestones from the working schedule.
MS = [tuple(m) for m in SCH['milestones']]
if MS[-1][0] != SCH['weeks']: die(f"schedule does not end at {SCH['weeks']} weeks")

# ================================================================ model frames: one camera, cropped once for all
MD = os.path.join(HERE, 'model')
FR_C = ['c0_site', 'c0b_backfill', 'c1_first', 'c2_upper', 'c3_exterior']   # JOB
FR_W = ['w1_windows', 'w2_cantilever', 'w3_greenroof', 'w4_siding', 'w5_stair', 'w6_porch', 'w7_all']
FRAMES = FR_C + FR_W
box = None
for f in FRAMES:
    a = np.array(Image.open(os.path.join(MD, f + '.png')).split()[3])
    ys, xs = np.where(a > 200); b = (xs.min(), ys.min(), xs.max(), ys.max())
    box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
CROP = (max(0, int(box[0]) - 40), max(0, int(box[1]) - 40), min(1600, int(box[2]) + 90), min(1200, int(box[3]) + 50))
FR = (CROP[2] - CROP[0], CROP[3] - CROP[1])
PTS = {k: [x - CROP[0], y - CROP[1]] for k, (x, y) in json.load(open(os.path.join(MD, 'c3_exterior.png.points.json'))).items()}
BB = {}
for (k, *_r), f in zip(ELS, FR_W):   # where each element shows in blue: the box the focus brackets draw around
    im = np.array(Image.open(os.path.join(MD, f + '.png')).convert('RGBA')).astype(int)
    blue = (im[..., 2] > im[..., 0] + 70) & (im[..., 2] > im[..., 1] + 50) & (im[..., 3] > 200)
    ys, xs = np.where(blue)
    BB[k] = [int(xs.min()) - CROP[0], int(ys.min()) - CROP[1], int(xs.max()) - CROP[0], int(ys.max()) - CROP[1]]

# ================================================================ copy
LOC = 'Garrison, NY'
# JOB: the project description, in the Project description voice (see the skill). Three paragraphs, 90 to 220 words.
PROSE = [
    'A 2,800-square-foot, two-story house on a wooded 2.1-acre lot in Garrison, New York, designed by Blejer Architecture + Design. The lot falls to the north and borders Fahnestock State Park.',
    'The site drops about 60 feet from the road to the house, so a new 650-foot driveway comes down at up to 14 percent. Concrete retaining walls run along the turn and the parking area. The house stands on a crawl space with 2x6 walls, dense-pack cellulose, ZIP sheathing and vertical wood siding on a rain screen, under sedum green roofs. A 52-foot wall of Unilux Design Line glass runs the north side of the first floor, and the upper volume cantilevers past it.',
    'Inside, the great room, kitchen and dining open to the glass wall and to a screened porch with hardwood decking and Centor screens. A floating white oak stair rises to the primary suite, with a walk-in closet and a curbless shower. Site-finished white oak floors run throughout, and cold-climate heat pumps with an ERV heat and cool the house.',
]
TITLE_EL = 'Signature Elements'
# JOB: the design steps (frames from render_model.sh).
STEPS = [
    {'k': 'site', 'rail': 0, 'title': 'Site and Foundation', 'fig': money(SITE_FDN), 'cap': 'Site work, utilities and foundations, with overhead and profit.',
     'body': 'Clearing, the 650-foot driveway and its concrete retaining walls, the well, the septic system and 700 feet of underground electric. A crawl space on 24 inch footings with 10 inch walls.',
     'img': 0, 'via': 1, 'note': 'Excavation, Footings and Crawl Space Walls'},
    {'k': 'first', 'rail': 1, 'title': 'First Floor', 'body': 'The great room, kitchen, bedroom and bath under a flat roof, with the stair bay on the south and the screened porch to the west.', 'img': 2, 'note': 'First Floor and Screened Porch'},
    {'k': 'upper', 'rail': 2, 'title': 'Upper Volume', 'body': 'A 22 by 44 foot volume set across the first floor on a steel frame, cantilevered past the glass wall. It holds the primary suite and the second bedroom.', 'img': 3, 'note': 'Upper Volume'},
    {'k': 'exterior', 'rail': 3, 'title': 'Exterior', 'body': 'Vertical wood siding on a rain screen, Unilux glass, sedum green roofs with four Velux skylights and a stone patio at the glass wall.', 'img': 4, 'note': 'Complete Building'},
]
for i, (k, name, v, spec) in enumerate(ELS):
    STEPS.append({'k': k, 'rail': 4, 'title': TITLE_EL, 'sub': f'<b>{i + 1:02d} / {len(ELS):02d}</b>{E(name)}', 'fig': money(v), 'cap': spec,
                  'img': 5 + i, 'el': i, 'note': 'Shown in Montana Blue'})
STEPS.append({'k': 'all', 'rail': 4, 'title': TITLE_EL, 'sub': 'Six Elements', 'fig': money(EL_TOTAL), 'cap': f'{pct(EL_TOTAL, BASE)} of the {money(BASE)} base budget.',
              'img': 11, 'all': True, 'note': 'Signature Elements in Montana Blue'})
for s in STEPS: s['label'] = '02 / Design'

# JOB: Basis of Budget, Clarifications and Exclusions, from the Notes sheet. Fragments are checked against it below.
BASIS = ['Blejer Architecture + Design SD Pricing Package dated September 9, 2026 (SD Presentation 02), the Noviello Well and Septic Plan revised November 20, 2025 and the Badey & Watson Composite Map dated July 1, 2026.',
         'Quantities measured from the schematic plans, sections and renderings.',
         'Structural and MEP drawings are not yet issued. Final framing and systems follow those drawings.']
CLAR = ['Priced with open-shop labor for Putnam County, NY.',
        'All-electric systems: two cold-climate ducted heat pumps, an ERV and a heat pump water heater.',
        'Unilux Design Line windows and lift-slides carried as an allowance of $145.56 per SF supply, with freight, duty and installation.',
        'Exterior walls: 2x6 framing, R-22 dense-pack cellulose, ZIP R-9 sheathing, a rain screen and wood siding.',
        'Insulation: Rockwool Safe\'n\'Sound at interior walls, R-47 dense-pack cellulose at the roofs with 4" rigid insulation above the deck, and R-30 Rockwool at the crawl space ceiling.',
        'Material allowances: siding and soffits $14.00 per SF, white oak flooring $15.00 per SF site finished, tile $50.00 per SF and countertops $75.00 per SF.',
        'Clearing limited to the driveway, the house footprint and the septic area. Hardscape is the stone patio and final grading.',
        '12\' wide gravel driveway: 10" RCA subbase, a 2" Item 4 wearing course and stone water bars on the steep section, with a hammerhead turnaround.',
        'Septic per the Noviello plan: gravity flow, a 1,250 gallon tank and 375 LF of absorption trenches. Well drilling carried at 500 LF, with added depth at $34.50 per LF.',
        'Allowance amounts are carried before overhead and profit. Overhead and profit of 15% applies to the base budget, the alternates and the value engineering options.',
        'None of the alternates or value engineering options is in the base budget.']
EXCL = ['Building permit, Health Department and Town driveway permit fees, and utility fees beyond the Central Hudson allowance.',
        'Architectural, structural and civil design, septic redesign and SWPPP preparation. Engineering for the driveway retaining walls is included.',
        'Temporary power, temporary heat and winter conditions.',
        'Rock removal, unless selected as Alternate 8, priced per day. Removal and disposal of unsuitable soils.',
        'Landscaping and planting, the tiered landscape retaining walls and insulation at the crawl space perimeter walls.',
        'Window treatments, furniture, EV charging, irrigation, driveway lighting and gates, hydrofracking and hazardous materials.']
notes_src = ' '.join(n for n in [str(r[2]) for r in wb['Notes & Clarifications'].iter_rows(min_row=5, values_only=True) if r[2]]) + ' ' + ' '.join(l['item'] for l in LINES.values())
for frag in ['SD Pricing Package', 'open-shop labor for Putnam County', 'two cold-climate ducted heat pumps', 'Unilux Design Line', '$145.56/SF', 'R-22 dense-pack cellulose',
             'ZIP R-9', "Safe'n'Sound", 'R-47 dense-pack', '4" rigid', 'R-30', '$14/SF', '$15/SF', '$50/SF', '$75/SF', 'Clearing limited to the driveway', 'patio and final grading',
             "12' wide", '10" RCA subbase', 'water bars', 'hammerhead', 'gravity flow, 1,250 gal tank, 375 LF', '500 LF of drilling', 'Building permit, Health Dept, Town driveway permit', 'beyond the allowance', 'Retaining Wall PE Design', 'Unit Price Beyond', 'structural or MEP drawings', 'insulation at crawl space perimeter walls', 'hydrofracking, hazardous materials',
             'septic redesign', 'SWPPP', 'Temporary power, temporary heat and winter conditions', 'Alternate 8', 'unsuitable soils', 'tiered landscape retaining walls',
             'Window treatments, furniture, EV charging, irrigation, driveway lighting and gates']:
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
PHONE, ADDR, EMAIL = '(845) 398-1778', '173 N. Route 9W, Congers, NY 10920', P['decisions']['email']

# pre-construction, as sent on the last pre-con agreement, with nothing project-specific
# kit v1.9: no plus-or-minus ranges anywhere a client reads. A range next to their budget reads as "the number could be 30% low".
# Each phase says what it locks instead; the funnel keeps its shape (width only, never labelled with a percentage).
PC_PHASES = [('Budget Setting and Schematic Design Budget', 'Phase 01', 20, 'Your target budget and the scope it buys', 'About 2 weeks', 'Budget Set'),
             ('Design Development Updates', 'Phase 02', 15, 'Selections in place of allowances', 'About 2 weeks per revision', 'Selections'),
             ('Firm Trade Partner Pricing', 'Phase 03', 8, 'Bids from the trades who will build it', '3 to 4 weeks with Phase 04', 'Trade Bids'),
             ('Value Engineering, Built In', 'Phase 04', 3, 'One Guaranteed Maximum Price', 'GMP delivered', 'GMP')]
PC_CARDS = [('Phase 01', 'Budget Setting and Schematic Design Budget', ['Budget setting session with you', 'Survey and soils engineer coordinated', 'Foundation strategy, priced', 'Options priced side by side'],
             'Your target budget and an options menu with three scenarios.'),
            ('Phase 02', 'Design Development Updates', ['Re-priced as the design develops', 'Design-to-budget meetings with your architect', 'Early flags on anything drifting over budget'],
             'An updated budget with more detailed line items, plus a preliminary schedule.'),
            ('Phase 03', 'Firm Trade Partner Pricing', ['Major trades bid to our subcontractors and vendors', 'Site walks with the key trades', 'Bids compared line by line'],
             'A budget backed by real pricing.'),
            ('Phase 04', 'Value Engineering, Built In', ['Money-saving options with trade-offs explained', 'Final pricing', 'Guaranteed Maximum Price proposal'],
             'Your GMP and a construction schedule.')]
PC_PROMISES = [('Walk-Away Guarantee', 'Stop at the end of any phase. You pay only for the phases started and keep everything delivered.'),
               ('Unused Reserve Comes Back to You', '100% of unused contingency is credited back. It is used only with written notice.'),
               ('One Rate, No Matter Who Is on the Call', 'One hourly rate, billed for one person per meeting.')]
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
H = os.path.join(CB, 'hero')   # JOB: Blejer renderings (SD-12, SD-10) for the hero and gallery, Montana dusk render for the close
jpg(os.path.join(H, 'blejer_nw.jpg'), 'hero.jpg', width=2400, q=84); jpg(os.path.join(H, 'blejer_nw_p.jpg'), 'hero_p.jpg', q=82)
for n, f in [('g1.jpg', 'blejer_nw.jpg'), ('g2.jpg', 'blejer_approach.jpg'), ('g3.jpg', 'hero_dusk.png')]: jpg(os.path.join(H, f), n, width=1760, q=80)
jpg(os.path.join(H, 'hero_dusk.png'), 'dusk.jpg', q=80); jpg(os.path.join(H, 'hero_dusk_p.png'), 'dusk_p.jpg', q=80)
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
if SEL: SELX.update(A=A, HERO=os.path.join(H, 'blejer_nw.jpg')); selbuild.assets(SEL, SELX)   # JOB: the photo the crop: refs read
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
rail = ''.join(f'<button type="button" data-step="{j}"{" class=on" if j == 0 else ""}>{t}</button>' for j, t in [(0, 'Site and Foundation'), (1, 'First Floor'), (2, 'Upper Volume'), (3, 'Exterior'), (4, TITLE_EL)])

def view_rows(items, colors, expandable):
    out = ''
    for k, (it, c) in enumerate(zip(items, colors)):
        lines = ''.join(f'<li>{"<span class=\"cd num\">" + E(ln["code"]) + "</span>" if ln.get("code") else ""}<span>{E(ln["item"])}</span></li>' for ln in it['lines'])   # line items only, no line pricing
        scope = f'<p>{E(it["scope"])}</p>' if it.get('scope') else ''
        head = f'<span class="sq"></span><div class="brow__t"><h3>{E(it["head"])}</h3>{scope}</div><span class="v num">{money(it["v"])}</span><span class="pct num">{pct(it["v"], BASE)}</span>'
        out += (f'<div class="brow" style="--c:{c}" data-k="{k}"><button type="button" class="brow__h" aria-expanded="false">{head}{PLUS}</button><ul class="brow__l" hidden>{lines}</ul></div>')
    return out
gcol = ['#001a8a', '#0028cc', '#2f50d6', '#5a74df', '#8598e8', '#adbbf0', '#cfd8f7']
dcol = ramp(len(DIVS))
EL_ITEMS = [{'head': g['name'], 'scope': g['scope'], 'v': g['v'], 'lines': g['lines']} for g in GROUPS]
MF_ITEMS = [{'head': f'{dv["n"]}  {dv["name"]}', 'v': dv['v'], 'lines': dv['lines']} for dv in DIVS]
def segs(items, colors):
    return ''.join(f'<i style="--w:{float(it["v"] / BASE * 100):.3f}%;--c:{c};--k:{k}" title="{E(it["head"])}"></i>' for k, (it, c) in enumerate(zip(items, colors))) + \
        f'<i style="--w:{float(OP / BASE * 100):.3f}%;--c:{OPC};--k:{len(items)}" title="Overhead and Profit"></i>'
op_row = f'<div class="brow brow--op" style="--c:{OPC}"><div class="brow__h"><span class="sq"></span><div class="brow__t"><h3>Overhead and Profit</h3><p>15% on the direct cost.</p></div><span class="v num">{money(OP)}</span><span class="pct num">{pct(OP, BASE)}</span><span class="pl"></span></div></div>'

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
ncol = lambda h, items: f'<div class="ncol"><h3>{E(h)}</h3><ol>{"".join(f"<li>{E(x)}</li>" for x in items)}</ol></div>'
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
GAL = [('g1.jpg', 'Northwest'), ('g2.jpg', 'From the Driveway'), ('g3.jpg', 'Northwest at Dusk')]

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

PNAME = '1004 Old Albany Post Road'   # JOB
DATA = {'base': str(BASE), 'frame': list(FR), 'points': {k: PTS[k] for k, *_r in ELS}, 'bb': BB,
        'els': [{'k': k, 'name': n, 'v': str(v)} for k, n, v, s in ELS], 'rest': str(REST),
        'alts': [{'id': a['id'], 'title': a['title'], 'v': str(a['v'])} for a in ALTS + VES], 'span': SPAN, 'weeks': SCH['weeks'], 'name': PNAME, 'job': 'E26049', 'email': EMAIL,
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
  <div class="hero__bg"><picture><source media="(max-width: 760px)" srcset="assets/hero_p.jpg"><img id="hero-img" data-crit fetchpriority="high" src="assets/hero.jpg" alt="{E(PNAME)}, rendering by Blejer Architecture + Design" width="2400" height="1198"></picture></div>
  <div class="hero__scrim"></div><div class="hero__shade"></div>
  <div class="hero__inner gut">
    <div class="tags"><span class="tag">Budget Presentation</span><span class="tag tag--ghost">{LOC}</span><span class="tag tag--ghost">Single-Family Residence</span></div>
    <h1 data-r>{E(PNAME)}</h1>
    <p class="eyebrow"><i></i>Blejer Architecture + Design · Philipstown</p>
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
        <div><dt>Type</dt><dd>Single-Family Residence</dd></div>
        <div><dt>Architect</dt><dd>Blejer Architecture + Design</dd></div>
        <div><dt>Budget</dt><dd class="num">{money(BASE)}</dd></div>
        <div><dt>Schedule</dt><dd>{SCH["weeks"]} Weeks</dd></div>
      </dl>
      <div class="desc"><p class="lede">{E(PROSE[0])}</p>{"".join(f"<p data-r=up>{E(p)}</p>" for p in PROSE[1:])}</div>
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
      <p class="sc-body sw">{E(s0["body"])}</p>
      <div class="elist hide"><p class="elist__h">Base Budget with Overhead and Profit</p>{elist}<div class="elist__tot"><span></span><span>Base Budget</span><span class="num">{money(BASE)}</span></div></div>
    </div>
    <div class="stage__rail" role="group" aria-label="Steps">{rail}</div>
    <p class="stage__note">{E(s0["note"])}</p>
  </div>
</section>

<section class="budget" id="budget" aria-label="Budget">
  <div class="wrap">
    {kick("03 / Budget")}
    <div class="budget__fig">{odo(money(BASE), "budget-odo")}</div>
    <p class="budget__cap" data-r="up"><span><b>Base Budget</b> with Overhead and Profit</span><span><b class="num">{money(DIRECT)}</b> Direct Cost</span><span><b>15%</b> Overhead and Profit</span></p>
    <div class="bview" data-view="el">
      <div class="sbar sbar--el" aria-hidden="true">{segs(EL_ITEMS, gcol)}</div>
      <div class="sbar sbar--mf" aria-hidden="true">{segs(MF_ITEMS, dcol)}</div>
      <div class="pills" role="tablist" aria-label="Budget view"><button type="button" role="tab" class="pill on" aria-selected="true" data-v="el">Elements</button><button type="button" role="tab" class="pill" aria-selected="false" data-v="mf">MasterFormat</button><span class="pills__hint">Lines at direct cost. Open any line for its detail.</span></div>
      <div class="brows brows--el" role="tabpanel" aria-label="Elements">{view_rows(EL_ITEMS, gcol, True)}</div>
      <div class="brows brows--mf" role="tabpanel" aria-label="MasterFormat" hidden>{view_rows(MF_ITEMS, dcol, True)}</div>
    </div>
    <div class="btot"><div class="btot__direct"><span>Direct Cost</span><span class="num">{money(DIRECT)}</span></div><div class="btot__op" style="--c:{OPC}"><span><i class="sq" aria-hidden="true"></i>Overhead and Profit, 15%</span><span class="num">{money(OP)}</span></div><div><span>Base Budget</span><span class="num">{money(BASE)}</span></div></div>
  </div>
</section>

{selbuild.section(SEL, SELX, kick) if SEL else selbuild.sheet(None, E)}

<section class="allow" id="allowances" aria-label="Allowances">
  <div class="wrap">
    {kick("03 / Allowances")}
    <div class="allow__top"><h2 class="sec-title" data-r>Allowances</h2><div class="allow__fig"><span class="big2 num" data-r="up">{money(ALLOW_TOTAL)}</span><p>Carried in the base budget, before overhead and profit.</p></div></div>
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
        <p class="alts__lede" data-r="up">Priced with overhead and profit. None of the fifteen is in the base budget.</p>
        <div class="alist">{alts}</div>
        <h2 class="sec-title alts__ve" id="value-engineering" data-r>Value Engineering</h2>
        <p class="alts__lede" data-r="up">Ways to reduce the base budget, priced with overhead and profit. Select any option to see it in the total.</p>
        <div class="alist">{ves}</div>
      </div>
      <aside class="atot" aria-label="Running total">
        <dl><div><dt>Base Budget</dt><dd class="num">{money(BASE)}</dd></div><div><dt>Requested</dt><dd class="num" id="alt-add">{money(0)}</dd></div></dl>
        <div class="atot__fig"><span class="lab">If Montana Confirms</span>{odo(money(BASE), "alt-odo")}</div>
        <button type="button" class="btn btn--navy" id="alt-send"><span>Send to Montana</span></button>
        <p class="atot__send">These count with your choices in Selections. They stay on this device until you send them.</p>
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
        <p class="sched__now"><span>Week</span>{odo("00", "week-odo")}<span class="sched__ph" id="week-ph">Site and Foundation</span></p>
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
    <p class="appr__lede" data-r="up">The person running the schedule can pick up a tool and close a gap in it. Every detail is checked by someone who has built it.</p>
    <div class="yteam">
      <div class="yteam__head" data-r="up"><h3 class="yteam__h">Your Team</h3><p class="yteam__p">Three principals stay on this project from the first walkthrough to the final punch list. You are never handed off.</p></div>
      <div class="people">{people}</div>
    </div>
  </div>
  <div class="osx">
    {OS_LETTERS}
    <div class="wrap osx__in">
      {kick("Montana OS")}
      <h3 class="osx__h" data-r>One system for every job.</h3>
      <p class="osx__lede" data-r="up">We built our own operating system for scheduling, cost and field reporting. It gives the owner and the design team a live, honest view of the work as it happens.</p>
      <div class="osx__app" data-r="up">
        <div class="osx__bar"><span class="osx__brand">{mark("osx__bm")}Montana <b>OS</b></span><span class="osx__job">{E(PNAME)}</span><span class="osx__live"><i></i>Opens at Award</span></div>
        <div class="osx__tiles">{os_tiles}</div>
      </div>
      <ol class="osx__feat">{os_feat}</ol>
      <div class="osx__for">{os_for}</div>
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
        <p class="pcf__p">Four phases. Each one locks more of the price. The last is a Guaranteed Maximum Price.</p>
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
    {kick("Next Step", "kick--light")}
    <h2 data-r>{E(P["next_step"])}</h2>
    <div class="cta__act"><a class="btn btn--white mag" href="tel:+18453981778">Call {PHONE} {ARROW}</a></div>
    <dl class="contact"><div><dt>Phone</dt><dd>{PHONE}</dd></div><div><dt>Address</dt><dd>{E(ADDR)}</dd></div><div><dt>Email</dt><dd>{E(EMAIL)}</dd></div></dl>
  </div>
</section>
<footer class="foot"><div class="wrap foot__in"><img src="assets/mc-white-all.png" alt="Montana Contracting" loading="lazy"><span>General Contractor · Since 1984 · NY + NJ + FL</span><span>© 2026 Montana Contracting</span></div></footer>
</main>

<div class="pc" id="precon" inert>
  <div class="pc__panel" role="dialog" aria-modal="true" aria-labelledby="pc-h" data-lenis-prevent>
    <div class="pc__bar"><img src="assets/mc-white-all.png" alt="Montana Contracting" width="200" height="12"><span>Pre-Construction · Optional Next Step</span><button type="button" class="pc__x">Close</button></div>
    <div class="pc__hero">
      {mark("pc__m")}
      <div class="wrap">
        <p class="kick kick--light"><i></i>Pre-Construction</p>
        <h2 id="pc-h">Know the number<br><em>before</em> you build.</h2>
        <p class="pc__lede">We set the budget with you first, then price the building at every design stage until we can offer a Guaranteed Maximum Price.</p>
      </div>
    </div>
    <div class="pc__body">
      <section class="wrap pc__sec">
        <p class="kick"><i></i>01 · Every Phase</p>
        <h3>Your price gets more certain at every phase.</h3>
        <p class="pc__p">Each phase locks part of the price. At the end of Phase 04 the whole number is a Guaranteed Maximum Price.</p>
        <div class="pc__funnel">{funnel()}<div class="pcphs">{pc_cols}</div></div>
      </section>
      <section class="pc__alt"><div class="wrap pc__sec">
        <p class="kick"><i></i>02 · What Each Phase Delivers</p>
        <h3>Each phase makes the estimate more accurate.</h3>
        <p class="pc__p">Each phase ends with an updated budget and a decision about whether to keep going. You can stop at the end of any phase.</p>
        <div class="pccards">{pc_cards}</div>
      </div></section>
      <section class="wrap pc__sec">
        <p class="kick"><i></i>03 · Our Promises</p>
        <h3>Built in from the first phase.</h3>
        <div class="pcproms">{pc_prom}</div>
        <div class="pcprins">{pc_prin}</div>
      </section>
      <section class="pc__end"><div class="wrap pc__sec">
        <h3>Ask us about <span class="nb">pre-construction.</span></h3>
        <p class="pc__p">One of the three principals will walk you through it.</p>
        <dl class="contact"><div><dt>Phone</dt><dd>{PHONE}</dd></div><div><dt>Email</dt><dd>{E(EMAIL)}</dd></div><div><dt>Address</dt><dd>{E(ADDR)}</dd></div></dl>
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
TITLE = 'Old Albany Post Road'
def tiny(name, w):   # a ~1 KB blurred stand-in, painted under the hero photo until it is decoded
    import io, base64
    im = Image.open(os.path.join(SITE, 'assets', name)).convert('RGB'); im = im.resize((w, max(1, round(im.height * w / im.width))), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, 'JPEG', quality=60); return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()
PH_D, PH_P = tiny('hero.jpg', 40), tiny('hero_p.jpg', 24)
PRELOAD = ('<link rel="preload" as="image" href="assets/hero.jpg" media="(min-width: 761px)" fetchpriority="high">\n'
           '<link rel="preload" as="image" href="assets/hero_p.jpg" media="(max-width: 760px)" fetchpriority="high">\n')
CSS += f'\n.hero__bg {{ background: #2b2f2a url({PH_D}) center / cover no-repeat; }}\n@media (max-width: 760px) {{ .hero__bg {{ background-image: url({PH_P}); }} }}\n'
HEAD = (PRELOAD + '<script>document.documentElement.classList.add("m")</script>\n' + f'<title>{TITLE}</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n<link rel="icon" href="{FAVICON}">\n'
        f'<meta name="description" content="Montana Contracting budget presentation for 1004 Old Albany Post Road, Garrison, NY.">\n<style>\n{CSS}\n</style>\n')

# ================================================================ house rules on everything a client reads
BANNED = ['stunning', 'beautiful', 'breathtaking', 'luxury', 'luxurious', 'bespoke', 'elevated', 'curated', 'seamless', 'passion', 'dream', 'journey',
          'exceptional', 'world-class', 'premier', 'cutting-edge', 'unparalleled', 'empower', 'transform', 'peace of mind', 'potential risk', 'novaterra',
          'design move', 'nestled', 'state-of-the-art', 'elevate', 'proud to', 'excited', 'grateful']
text = re.sub(r'<script.*?</script>|<svg.*?</svg>', ' ', BODY, flags=re.S)
text = html.unescape(re.sub(r'<[^>]+>', ' ', text))
text += ' ' + ' '.join(str(v) for s in STEPS for v in s.values() if isinstance(v, str))
bad = [name for ch, name in [('—', 'em dash'), ('–', 'en dash'), (';', 'semicolon'), ('!', 'exclamation'), ('?', 'question')] if ch in text]
bad += ['banned: ' + w for w in BANNED if re.search(r'\b' + re.escape(w) + r'\b', text.lower())]
if re.search(r'\b\w+, not \w+', text): bad.append('X, not Y')
if bad: die('copy rules: ' + ', '.join(bad))
if len(PROSE[0].split('. ')[0]) > 155: die('project snippet sentence is over 155 characters')
words = sum(len(p.split()) for p in PROSE)
if not 90 <= words <= 220: die(f'project description is {words} words')
for v in [money(BASE), money(DIRECT), money(OP), money(EL_TOTAL), money(REST), money(SITE_FDN), money(ALLOW_TOTAL)] + [money(e[2]) for e in ELS]:
    if v not in BODY: die('figure missing from the page: ' + v)
_vis = re.sub(r'<script.*?</script>', '', BODY, flags=re.S)
_nc = re.search(r'\$\d[\d,]*(?![\d,]*\.\d\d)', _vis)
if _nc: die('a dollar figure without cents: ' + _vis[max(0, _nc.start() - 120):_nc.end() + 40])

os.makedirs(SITE, exist_ok=True)
open(os.path.join(SITE, 'index.html'), 'w').write(HEAD + BODY)
shutil.copytree(SITE, NET)
open(os.path.join(NET, 'index.html'), 'w').write(f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n<meta name="robots" content="noindex, nofollow">\n<meta name="mcc-send" content="netlify-forms">\n{HEAD}</head>\n<body>\n{BODY}\n</body>\n</html>\n')
open(os.path.join(NET, 'robots.txt'), 'w').write('User-agent: *\nDisallow: /\n')
# JOB: zip name, <JOB>_Presentation_Netlify_v#.zip
z = os.path.join(HERE, 'E26049_Presentation_Netlify_v1.zip')
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
