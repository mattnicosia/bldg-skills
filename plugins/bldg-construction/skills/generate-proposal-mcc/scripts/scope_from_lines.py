#!/usr/bin/env python3
"""Scope of Work rows from a presentation's web/scope_lines.json (kit v1.16).

    python3 scripts/scope_from_lines.py web/scope_lines.json > scope_items.json

One row per cost code: "<Trade>: item; item; item." A trade with more than 18 items is split evenly into "(continued)" rows.
Items keep their directives. Output is HTML-escaped, ready for data.json "scope_items".
"""
import html, json, sys

sc = json.load(open(sys.argv[1]))
rows = []
for dv in sc['divs']:
    ls = list(sc['lines'][dv['n'].replace(' ', '.')])
    ls = [l[len(dv['name']) + 2:] if l.startswith(dv['name'] + ': ') else l for l in ls]
    n = -(-len(ls) // 18); per = -(-len(ls) // n)
    for j, k in enumerate(range(0, len(ls), per)):
        rows.append(html.escape(f"{dv['name']}{' (continued)' if j else ''}: " + '; '.join(ls[k:k + per]) + '.', quote=True))
json.dump(rows, sys.stdout, indent=1)
