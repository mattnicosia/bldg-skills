"""Read a Montana estimate workbook (the house format built by generate-estimate-workbook) into the
budget data the presentation needs.

Sheets read (found by name, case-insensitive, partial match):
  SOV                    header row with 'CSI', 'Trade', and a 'Final Price' column (falls back to
                         'Our Total'). Trade rows run until a row whose first cell is 'SUBTOTAL'.
                         Markup rows follow: label in col A ('General Conditions', 'Fee', 'Insurance',
                         'Contingency', ...), rate in col B (0.07), amount in the price column.
                         An 'ALTERNATES' block follows with a header row 'CSI', 'Alternate', ...,
                         'Final Price'. Rows read 'Alternate 4 -- Deduct -- Cable Railings ...'.
  Notes & Clarifications header 'Type', 'Item', 'Clarification'. Types: EXCLUSION, BY OWNER, CLARIFICATION.

Anything the workbook does not hold (allowances, groups, keys to success) comes from project.json.
"""
import re
import openpyxl

MARKUP_WORDS = ('general condition', 'fee', 'insurance', 'contingency', 'escalation', 'overhead', 'profit', 'bond')


def _sheet(wb, *names):
    for n in names:
        for ws in wb.worksheets:
            if n.lower() in ws.title.lower():
                return ws
    return None


def _num(v):
    return float(v) if isinstance(v, (int, float)) else None


def read_estimate(path):
    wb = openpyxl.load_workbook(path, data_only=True)
    sov = _sheet(wb, 'sov', 'schedule of values')
    if sov is None:
        raise SystemExit(f'{path}: no SOV sheet')
    rows = [list(r) for r in sov.iter_rows(values_only=True)]

    # ---- base trades
    hdr = next(i for i, r in enumerate(rows) if r and str(r[0]).strip().upper() == 'CSI')
    cols = [str(c or '').strip().lower() for c in rows[hdr]]
    price = next((i for i, c in enumerate(cols) if c == 'final price'), None)
    if price is None:
        price = next(i for i, c in enumerate(cols) if 'total' in c)
    tcol = next(i for i, c in enumerate(cols) if c in ('trade', 'description', 'scope'))
    trades, i = [], hdr + 1
    while i < len(rows):
        r = rows[i]
        first = str(r[0] or '').strip().upper()
        if first.startswith('SUBTOTAL') or str(r[tcol] or '').strip().upper().startswith('SUBTOTAL'):
            break
        v = _num(r[price]) if len(r) > price else None
        if r[tcol] and v is not None:
            trades.append({'code': str(r[0] or '').strip(), 'trade': str(r[tcol]).strip(), 'value': round(v)})
        i += 1
    subtotal_row = rows[i] if i < len(rows) else None

    # ---- markups (compound in the order listed)
    markups = []
    j = i + 1
    while j < len(rows):
        r = rows[j]
        lab = str(r[0] or '').strip()
        if lab.upper().startswith('TOTAL'):
            break
        if lab and any(w in lab.lower() for w in MARKUP_WORDS) and _num(r[1]) is not None:
            markups.append({'label': lab, 'rate': float(r[1]), 'value': round(_num(r[price]) or 0)})
        j += 1
    base_row = rows[j] if j < len(rows) else None
    base = round(_num(base_row[price])) if base_row and _num(base_row[price]) is not None else None

    # ---- alternates
    alternates = []
    ah = next((k for k in range(j, len(rows)) if rows[k] and str(rows[k][0] or '').strip().upper() == 'CSI'), None)
    if ah is not None:
        acols = [str(c or '').strip().lower() for c in rows[ah]]
        ap = next((k for k, c in enumerate(acols) if c == 'final price'), price)
        al = next((k for k, c in enumerate(acols) if 'alternate' in c), 1)
        for r in rows[ah + 1:]:
            name = str(r[al] or '').strip()
            if not name.lower().startswith('alternate'):
                if name.upper().startswith('TOTAL') or str(r[0] or '').upper().startswith('TOTAL'):
                    break
                continue
            m = re.match(r'alternate\s*(\d+)?\s*-*\s*(.*)', name, re.I)
            num, rest = m.group(1), m.group(2)
            deduct = bool(re.match(r'deduct\s*-*', rest, re.I))
            rest = re.sub(r'^deduct\s*-*\s*', '', rest, flags=re.I)
            rest = re.sub(r'\s*\[[^\]]*\]\s*$', '', rest).strip()
            v = _num(r[ap]) if len(r) > ap else None
            alternates.append({'id': num or re.sub(r'[^a-z0-9]+', '-', rest.lower()).strip('-')[:24],
                               'num': int(num) if num else None, 'label': rest, 'deduct': deduct,
                               'code': str(r[0] or '').strip(),
                               'value': round(v) if v is not None else None})

    # ---- notes
    notes = {'EXCLUSION': [], 'BY OWNER': [], 'CLARIFICATION': []}
    ns = _sheet(wb, 'notes', 'clarification')
    if ns is not None:
        for r in ns.iter_rows(values_only=True):
            t = str(r[0] or '').strip().upper()
            if t in notes and len(r) > 2 and r[2]:
                notes[t].append({'item': str(r[1] or '').strip(), 'text': str(r[2]).strip()})

    direct = sum(t['value'] for t in trades)
    run = direct
    for m in markups:   # recompute so the page and the workbook agree to the dollar
        m['value'] = round(run * m['rate']); run += m['value']
    return {'trades': trades, 'direct': direct, 'markups': markups, 'base': run,
            'workbook_base': base, 'alternates': alternates, 'notes': notes}


if __name__ == '__main__':
    import json, sys
    d = read_estimate(sys.argv[1])
    print(json.dumps({k: (v if k != 'trades' else v[:5]) for k, v in d.items()}, indent=1)[:4000])
    print('direct', d['direct'], 'base', d['base'], 'workbook', d['workbook_base'], 'trades', len(d['trades']), 'alts', len(d['alternates']))
