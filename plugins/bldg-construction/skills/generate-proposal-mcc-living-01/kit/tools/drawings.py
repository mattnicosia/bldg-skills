#!/usr/bin/env python3
"""Helpers for building a massing model from 2D drawings.

  python3 tools/drawings.py index  <set.pdf>                       list sheets: page, sheet number, title words
  python3 tools/drawings.py page   <set.pdf> <page> <out.png> [dpi] render one sheet (default 60 dpi to look, 200 to crop)
  python3 tools/drawings.py crop   <sheet.png> x0 y0 x1 y1 <out.jpg> [--clean]
        crop an elevation edge to edge of the building and grade to the highest point. --clean
        whitens the paper, darkens the linework and drops color so it reads as a drawing on the model.
  python3 tools/drawings.py scale  <px> <feet>                     pixels per foot from a known dimension

Workflow: index the set, render the plan and elevation sheets small to find them, render at 200 dpi,
read the footprint and heights off the dimensions, crop each elevation (S, N, E, W) to the building's
extents, then write massing.json (see README). Elevations are projected onto the walls that face them.
"""
import re, subprocess, sys
from PIL import Image, ImageOps, ImageFilter


def index(pdf):
    n = int(re.search(r'Pages:\s+(\d+)', subprocess.run(['pdfinfo', pdf], capture_output=True, text=True).stdout).group(1))
    for p in range(1, n + 1):
        t = subprocess.run(['pdftotext', '-f', str(p), '-l', str(p), '-layout', pdf, '-'], capture_output=True, text=True).stdout
        sheet = (re.findall(r'\b[A-Z]{1,2}-?\d{1,2}\.\d{1,2}\b', t) or ['?'])[-1]
        kinds = [k for k in ('PLAN', 'ELEVATION', 'SECTION', 'DETAIL', 'SITE', 'ROOF', 'FOUNDATION') if k in t.upper()]
        print(f'{p:3d}  {sheet:8s} {", ".join(kinds)}')


def page(pdf, p, out, dpi=60):
    base = out[:-4] if out.endswith('.png') else out
    subprocess.run(['pdftoppm', '-f', str(p), '-l', str(p), '-r', str(dpi), '-png', '-singlefile', pdf, base], check=True)
    print('wrote', base + '.png', Image.open(base + '.png').size)


def crop(src, x0, y0, x1, y1, out, clean=False):
    im = Image.open(src).convert('RGB').crop((int(x0), int(y0), int(x1), int(y1)))
    if clean:
        g = ImageOps.grayscale(im)
        g = g.point(lambda v: 255 if v > 200 else int(v * 0.75))          # paper to white, lines darker
        g = g.filter(ImageFilter.MinFilter(3)) if max(im.size) > 2400 else g  # thicken hairlines on big crops
        im = Image.merge('RGB', (g, g, g))
    im.save(out, quality=90)
    print('wrote', out, im.size)


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a: print(__doc__); sys.exit(2)
    if a[0] == 'index': index(a[1])
    elif a[0] == 'page': page(a[1], int(a[2]), a[3], int(a[4]) if len(a) > 4 else 60)
    elif a[0] == 'crop': crop(a[1], *map(float, a[2:6]), a[6], '--clean' in a)
    elif a[0] == 'scale': print(f'{float(a[1]) / float(a[2]):.3f} px per ft')
    else: print(__doc__)
