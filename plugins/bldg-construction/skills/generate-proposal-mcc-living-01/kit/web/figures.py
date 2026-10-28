"""Every figure on the page, to the cent, from the estimate's line items (Estimate sheet). Kit v1.5: paths relative to the project.
    python3 -I figures.py        (run in <project>/web/)
"""
import json, os, openpyxl
from decimal import Decimal as D, ROUND_HALF_UP
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
C = lambda x: D(str(x)).quantize(D('0.01'), ROUND_HALF_UP)
OP_RATE = D('0.15')
wb = openpyxl.load_workbook(os.path.join(PROJ, 'estimate.xlsx'), data_only=True)
ws = wb['Estimate']
ROW_TOTAL = next(i for i, r in enumerate(ws.iter_rows(min_row=1, max_row=ws.max_row, values_only=True), start=1) if r[0] == 'TOTAL -- BASE BID')
lines, trade = [], None
for i, r in enumerate(ws.iter_rows(min_row=10, max_row=ROW_TOTAL, values_only=True), start=10):
    code, item, qty, unit, rate, tot = r[:6]
    if code and isinstance(code, str) and code.isupper() and not item and code not in ('TRADE TOTAL', 'SUBTOTAL'): trade = code; continue
    if code in ('TRADE TOTAL', 'SUBTOTAL') or not item: continue
    if isinstance(tot, (int, float)) and tot:
        lines.append({'row': i, 'code': code, 'item': item, 'trade': trade, 'v': C(tot)})
direct = sum(l['v'] for l in lines)
op = C(direct * OP_RATE); base = direct + op
print('direct', direct, 'op', op, 'base', base, '| sheet TOTAL -- BASE BID', C(ws.cell(ROW_TOTAL, 6).value))
trades = {}
for l in lines: trades[l['trade']] = trades.get(l['trade'], D(0)) + l['v']
for t, v in trades.items(): print(f'  {t:48s} {v}')
json.dump({'direct': str(direct), 'op': str(op), 'base': str(base)}, open(os.path.join(HERE, 'numbers_check.json'), 'w'))
