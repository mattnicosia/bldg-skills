#!/usr/bin/env python3
"""Consolidate data.json lines before build_estimate.py (E26044 The Inn at Kirkside, Matt 2026-10-30).

    python scripts/consolidate.py data.json data_consolidated.json

1. Trade combinations (house default, override with "combine" in data.json, {} to switch off):
   06.11 Wood Framing -> 06.10 "Rough Carpentry and Framing";
   26.09 / 26.24 / 26.27 / 27.11 -> 26.05 "Electrical"; 26.56 Exterior and Emergency Lighting -> 26.50 "Lighting Fixtures".
   Packaged Generator Assemblies (26.32) and Fire Detection and Alarm (28.46) stay separate.
2. Leveling (optional "level" in data.json): spread a subcontract price over a division's lines pro rata, holding named lines at
   real values first. [{"csi_prefix": "23", "target": 2100000, "hold": {"Honeywell BMS": 200000, "Geothermal Wells": null}}]
   (a number holds the line at that total, null holds it at its own estimate value). Prints any line inflated more than 1.5x.
3. One line per item: lines in the same CSI code that are the same item (sizes, counts and bracketed notes ignored, e.g.
   "Floor Structure (2x8)" and "Floor Structure (2x10 @ 12")") merge into one line. Same unit: quantities add. Mixed units: 1 LS.
   "keep_separate": ["Foundation Walls (Elevator Pit Walls)", ...] protects lines another deliverable depends on.
"""
import json, re, sys
from decimal import Decimal as D, ROUND_HALF_UP
C = lambda x: D(str(x)).quantize(D('0.01'), ROUND_HALF_UP)

COMBINE = {'06.11.00': ('06.10.00', 'Rough Carpentry and Framing'), '26.09.23': ('26.05.00', 'Electrical'), '26.24.00': ('26.05.00', 'Electrical'),
           '26.27.26': ('26.05.00', 'Electrical'), '27.11.00': ('26.05.00', 'Electrical'), '26.05.00': ('26.05.00', 'Electrical'),
           '26.56.00': ('26.50.00', 'Lighting Fixtures'), '26.50.00': ('26.50.00', 'Lighting Fixtures'), '06.10.00': ('06.10.00', 'Rough Carpentry and Framing')}
SIZE = re.compile(r"""^(?:W|C|HSS)?\d[\d\-/\.]*(?:"|')?(?:x\d[\d\-/\.]*(?:"|')?)+$|^\d[\d\-/\.]*(?:"|')$""", re.I)


def base(item):
    t = re.sub(r'^(?:Levels|Foundation) - ', '', item.strip()); t = re.sub(r'\s*\([^()]*\)', '', t)
    t = ' '.join(w for w in t.split() if not SIZE.match(w))
    t = re.sub(r'\b(F/I|F/O|I/O) Column\b', r'\1 Steel Column', t)
    return re.sub(r'\s+', ' ', t).strip()


def merged_name(items):
    if len(set(items)) == 1: return items[0]
    common = [p for p in re.findall(r'\([^()]*\)', items[0]) if all(p in it for it in items)]
    return (base(items[0]) + ' ' + ' '.join(common)).strip()


def total(l): return C(D(str(l['qty'] or 0)) * D(str(l['rate'])))


def main(src, dst):
    d = json.load(open(src))
    comb = {k: tuple(v) for k, v in d.get('combine', COMBINE).items()}
    keep = tuple(d.get('keep_separate', []))
    lines = [dict(l, _trade=t['trade']) for t in d['trades'] for l in t['lines']]
    names = {}
    for l in lines:                                   # 1. trade combinations
        if l['csi'] in comb: l['csi'], names[comb[l['csi']][0]] = comb[l['csi']][0], comb[l['csi']][1]
    for lv in d.get('level', []):                     # 2. leveling with held lines
        rs = [l for l in lines if l['csi'].startswith(lv['csi_prefix'])]
        held, free = [], []
        for l in rs:
            k = next((h for h in lv.get('hold', {}) if h.lower() in l['scope'].lower()), None)
            if k is None: free.append(l); continue
            if lv['hold'][k] is not None: l['rate'] = float(C(D(str(lv['hold'][k])) / D(str(l['qty'] or 1))))
            held.append(l)
        fs = sum(total(l) for l in free); rest = D(str(lv['target'])) - sum(total(l) for l in held)
        f = rest / fs
        for l in free:
            l['rate'] = float(D(str(l['rate'])) * f)
        print(f"level {lv['csi_prefix']}: {len(held)} held, {len(free)} spread x{float(f):.3f}" + ('  CHECK: over 1.5x, hold the real lines' if f > D('1.5') else ''))
    groups = {}                                       # 3. one line per item
    for l in lines:
        k = (l['csi'], l['scope'] if l['scope'].startswith(keep) and keep else base(l['scope']).lower())
        groups.setdefault(k, []).append(l)
    out = []
    for (csi, _), ls in groups.items():
        if len(ls) == 1: out.append(ls[0]); continue
        units = {l['unit'] for l in ls}; tot = sum(total(l) for l in ls)
        q = sum(D(str(l['qty'] or 0)) for l in ls) if len(units) == 1 else D(1)
        out.append(dict(ls[0], scope=merged_name([l['scope'] for l in ls]), qty=float(q), unit=ls[0]['unit'] if len(units) == 1 else 'LS',
                        rate=float(tot / q) if q else float(tot), bullets=sum((l.get('bullets', []) for l in ls), [])))
    trades = {}
    for l in out:
        t = names.get(l['csi']) or l.pop('_trade'); l.pop('_trade', None)
        trades.setdefault(t, []).append(l)
    d['trades'] = [{'trade': t, 'csi': sorted({l['csi'] for l in ls}), 'lines': ls} for t, ls in trades.items()]
    json.dump(d, open(dst, 'w'), indent=1)
    print(f'{len(lines)} lines -> {len(out)} lines, {len(d["trades"])} trades')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
