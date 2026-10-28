#!/usr/bin/env python3
"""Turn a simple activity table into the schedule.json the presentation reads.

    python3 tools/schedule.py <activities.csv> <schedule.json> [--mob YYYY-MM-DD] [--keys YYYY-MM-DD]

CSV columns (header row required, extra columns ignored):
  group      section label shown on the chart, in the order it first appears ("Before We Start", "On Site")
  who        who the section belongs to, shown beside the group label (first row of each group is enough)
  name       activity name, Title Case ("Foundations and Steel")
  short      short label for phones (optional)
  start      YYYY-MM-DD
  finish     YYYY-MM-DD (same as start for a milestone)
  by         montana | mlight | factory | others | decision   (bar color)
  critical   Y if on the critical path
  milestone  label for a milestone diamond at the finish date (optional), "!" prefix = big milestone
  weather    weather days carried inside the bar (optional, hatched)
  key        optional id (phases in project.json can point at it with "sched": "<key>")

Dates should come from a real schedule (P6, MS Project, a CPM). This tool only draws them.
"""
import csv, json, re, sys, datetime as dt


def main(src, dst, mob=None, keys=None):
    rows, groups, gk = [], [], {}
    for i, r in enumerate(csv.DictReader(open(src, newline=''))):
        r = {k.strip().lower(): (v or '').strip() for k, v in r.items() if k}
        g = r['group']
        if g not in gk:
            gk[g] = re.sub(r'[^a-z0-9]+', '', g.lower())[:12] or f'g{len(gk)}'
            groups.append({'key': gk[g], 'label': g, 'who': r.get('who', '')})
        elif r.get('who') and not groups[[x['label'] for x in groups].index(g)]['who']:
            groups[[x['label'] for x in groups].index(g)]['who'] = r['who']
        row = {'key': r.get('key') or f'a{i}', 'grp': gk[g], 'name': r['name'], 'short': r.get('short') or r['name'][:14],
               's': r['start'], 'f': r['finish'] or r['start'], 'kind': r.get('by') or 'montana',
               'crit': r.get('critical', '').upper().startswith('Y'), 'ms': [], 'wx': int(r['weather']) if r.get('weather') else 0}
        if r.get('milestone'):
            big = r['milestone'].startswith('!')
            row['ms'].append({'d': row['f'], 'label': r['milestone'].lstrip('!'), 'big': big})
        rows.append(row)
    d = lambda s: dt.date.fromisoformat(s)
    start = min(d(r['s']) for r in rows).replace(day=1)
    endd = max(d(r['f']) for r in rows)
    end = (endd.replace(day=28) + dt.timedelta(days=4)).replace(day=1) - dt.timedelta(days=1)
    out = {'start': start.isoformat(), 'end': end.isoformat(), 'groups': groups, 'rows': rows, 'held': []}
    if mob: out['mob'] = mob
    if keys: out['keys'] = keys
    if mob and keys: out['weeks'] = round((d(keys) - d(mob)).days / 7)
    out['milestones'] = [[r['name'], r['f'] if r['s'] == r['f'] else f"{r['s']} to {r['f']}", ''] for r in rows if r['crit'] or r['ms']]
    json.dump(out, open(dst, 'w'), indent=1)
    print('wrote', dst, len(rows), 'activities', len(groups), 'groups', out['start'], 'to', out['end'])


if __name__ == '__main__':
    a = sys.argv[1:]
    if len(a) < 2: print(__doc__); sys.exit(2)
    opt = lambda k: a[a.index(k) + 1] if k in a else None
    main(a[0], a[1], opt('--mob'), opt('--keys'))
