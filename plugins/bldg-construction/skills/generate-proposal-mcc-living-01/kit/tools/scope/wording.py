"""Client wording for estimate line items (kit v1.16, from E26044 The Inn at Kirkside).

    from wording import client, merge_key, VERBS
    client('F/I (3) 2x10 Header', '06.10.00')   ->  'Furnish and Install (3) 2x10 Header'

client()     cleans one line name for the presentation and the proposal PDF: no estimator tags, no TBD, every item opens with a directive.
merge_key()  the key two lines share when they are the same item (sizes, counts and bracketed notes ignored). Used by the workbook
             step to merge duplicates within a subdivision (Floor Structure listed four times becomes one line).
"""
import re

# Every scope item opens with what Montana does.
VERBS = ('Furnish and Install', 'Furnish Only', 'Install Only', 'Provide', 'Remove', 'Replace', 'Repair', 'Patch', 'Paint', 'Wire', 'Abandon',
         'Export', 'Spread', 'Strip', 'Protect', 'Refinish', 'Scrape', 'Seal', 'Grind', 'Cut', 'Enlarge', 'Fill', 'Infill', 'Shore', 'Underpin',
         'Disconnect', 'Relocate', 'Finish', 'Demolish', 'Clean', 'Form and Pour', 'Saw Cut')
VERB_RE = re.compile(r'(?:' + '|'.join(map(re.escape, VERBS)) + r')\b')
NOUN_STARTS = ('Spread Footings', 'Finish Carpentry', 'Seal Coat', 'Cleanout', 'Fill Material')   # look like verbs, are things
SERVICE_NOUNS = ('Underpinning',)                                                               # take Provide

# One-off typo and wording fixes seen in Montana estimates. Add to the list, never remove.
FIXES = (('F/II:', 'F/I'), ('F/I:', 'F/I'), ('Inidcator', 'Indicator'), ('Ductowork', 'Ductwork'), ('Cespool', 'Cesspool'), ('Baement', 'Basement'),
         ('Paneboard', 'Panelboard'), ('Lathe', 'Lath'), ('DIffuser', 'Diffuser'), ('Annodized', 'Anodized'), ('Water Proof', 'Waterproof'),
         ('Heat Water Cooled', 'Water Cooled'), ('Silt Fence Budget', 'Silt Fence'), ('Remaining Demo', 'Remove Remaining Items Shown on the Demolition Plans'),
         ('Ikea', 'IKEA'), (' at In ', ' at '), (' @ ', ' at '), ('@', 'at '), (',,', ','), ('SSTS', 'Septic'))
SMALL = ('Of', 'To', 'With', 'And', 'For', 'In', 'Into', 'On', 'The', 'At', 'Or')


def tidy(s):
    """Estimator tags, TBD notes, drawing references and stray punctuation out of a line name."""
    s = re.sub(r'\s*\[Allowance[^\]]*\]', ' (Allowance)', s)
    s = re.sub(r'\s*\[[^\]]*\]', '', s).replace(' (M+L)', '').replace('(M+L)', '')
    s = re.sub(r'^((?:F/I|F/O|I/O)\s+)?(?:Foundation|Levels) - ', lambda m: m.group(1) or '', s)
    s = re.sub(r'^(?:FF|WF)-\d+:\s*(?:F/I:?\s*)?', 'F/I ', s) if re.match(r'^(?:FF|WF)-\d+:', s) else s
    s = re.sub(r'\(P-\d+, ref Tag \d+ A-\d+\)\s*', '', s)
    s = re.sub(r'\s*\((?:FF|WF|MF)-?\d+\)', '', s); s = re.sub(r'\b(?:FF|WF)-\d+:?\s*', '', s); s = re.sub(r'\bMF0?\d+\s+', '', s)
    s = re.sub(r'\(\s*(?:Spec,? TBD|Size TBD|Design TBD|Kitchen Layout TBD)\s*\)', '', s); s = re.sub(r',\s*Spec,? TBD', '', s)
    s = s.replace(' Model #_', '')
    s = re.sub(r'\s*\(\s*layers\)', '', s)
    s = re.sub(r'\(\$[\d,.]+/(?:SF|Ea|EA|LF)[^)]*Material[^)]*\)', '(Material Allowance)', s)
    s = re.sub(r'\(\$[\d,.]+/(?:SF|Ea|EA|LF)[^)]*\)', '(Allowance)', s)
    s = re.sub(r'\(\$[\d,]+(?:\.\d\d)?/SF Mat\. Allowance\)', '(Material Allowance)', s)
    s = re.sub(r'\(\$[\d,]+(?:\.\d\d)? Allowance\)', '(Allowance)', s)
    s = re.sub(r'\$(\d[\d,]*)(?![\d,]*\.\d)', r'$\1.00', s)                       # every dollar figure carries cents
    s = re.sub(r'\s*\(Per (?:Week|Month|Page|Riser|Hour)\)', '', s)               # the line shows a total
    s = re.sub(r'Kohler,(\S)', r'Kohler, \1', s); s = re.sub(r'(K-[\w-]*?-)\s+(\w)', r'\1\2', s)
    s = re.sub(r'^(F/I )(\d+X\d+ Steel Beam)', r'\1W\2', s, flags=re.I)
    s = re.sub(r'HW Set (\d)\b', r'HW Set 0\1', s).replace('HW Set', 'Hardware Set')
    for a, b in FIXES: s = s.replace(a, b)
    s = s.replace('(~', '(About ').replace('Every ~', 'About Every ').replace('~', 'About ')
    for w in SMALL: s = re.sub(r'(?<=\S) ' + w + r' (?=\S)', ' ' + w.lower() + ' ', s)
    s = re.sub(r'\(\s*\)', '', s); s = re.sub(r'\s+\)', ')', s); s = re.sub(r'\)\s*\(', ', ', s)
    s = re.sub(r'\(Allowance, Allowance\)', '(Allowance)', s)
    return re.sub(r'\s{2,}', ' ', s).strip()


def plain(s):   # estimator shorthand spelled out
    for k, v in (('F/I ', 'Furnish and Install '), ('F/O ', 'Furnish Only '), ('I/O ', 'Install Only '), (' w/ ', ' with '), (' W/ ', ' with ')):
        s = s.replace(k, v)
    return s


def directive(s, code=''):
    s = re.sub(r'^Demo\b', 'Demolish', s); s = re.sub(r'^Form/Pour\b', 'Form and Pour', s)
    m = re.match(r'(?:Furnish and Install|Furnish Only|Install Only) (.*)', s)        # "Furnish and Install Repair ..." -> "Repair ..."
    if m and re.match(r'(?:Repair|Replace|Remove|Patch|Paint|Demolish)\b', m.group(1)): s = m.group(1)
    if s.startswith(NOUN_STARTS): return 'Furnish and Install ' + s
    if s.startswith(SERVICE_NOUNS): return 'Provide ' + s
    if VERB_RE.match(s): return s
    if s.startswith('Install '): return 'Install Only ' + s[8:]
    if s.startswith('Furnish '): return 'Furnish Only ' + s[8:]
    return ('Provide ' if str(code).startswith('01') else 'Furnish and Install ') + s


def client(item, code='', extra=None):
    """The line as the client reads it. extra: a job's own fix function, run after tidy()."""
    s = tidy(item)
    if extra: s = extra(s)
    return directive(plain(s), code)


SIZE = re.compile(r"""^(?:W|C|HSS)?\d[\d\-/\.]*(?:"|')?(?:x\d[\d\-/\.]*(?:"|')?)+$|^\d[\d\-/\.]*(?:"|')$""", re.I)


def merge_key(item):
    """Two lines in one subdivision with the same key are the same item: sizes, counts and bracketed notes do not count."""
    t = re.sub(r'^(?:Levels|Foundation) - ', '', item.strip()); t = re.sub(r'\s*\([^()]*\)', '', t)
    t = ' '.join(w for w in t.split() if not SIZE.match(w))
    t = re.sub(r'\b(F/I|F/O|I/O) Column\b', r'\1 Steel Column', t)
    return re.sub(r'\s+', ' ', t).strip().lower()


def merged_name(items):
    """Name for a merged line: the shared name, keeping any bracketed note every line carries."""
    if len(set(items)) == 1: return items[0]
    common = [p for p in re.findall(r'\([^()]*\)', items[0]) if all(p in it for it in items)]
    base = re.sub(r'^(?:Levels|Foundation) - ', '', items[0].strip()); base = re.sub(r'\s*\([^()]*\)', '', base)
    base = ' '.join(w for w in base.split() if not SIZE.match(w))
    return (re.sub(r'\s+', ' ', base) + ' ' + ' '.join(common)).strip()


if __name__ == '__main__':
    for t, c in [('F/I (3) 2x10 Header', '06.10.00'), ('Levels - Floor Structure (2x8)', '06.11.00'), ('Project Manager (60% of Duration)', '01.31.00'),
                 ('FF-01: Repair & Replace Existing Decking as Required ($12/SF Material Allowance)', '06.15.00'), ('Foundation - Spread Footings (F3.0)', '03.30.00'),
                 ('Underpinning Sections 18" Footing Depth', '31.48.00'), ('F/O Wall Mounted Bath Spout (Kohler, Spec TBD, Satin Nickel)', '22.40.00')]:
        print(f'{t!r:80} -> {client(t, c)}')
    print(merge_key('Levels - Floor Structure (2X10 Framing)'), '|', merge_key('Levels - Floor Structure (2x10 @ 12")'), '|', merge_key("2x6x9' Studs"))
