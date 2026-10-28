#!/usr/bin/env python3
"""Contact sheet of the render check: python3 tools/sheet.py <project_dir> [desktop|phone]"""
import glob, os, sys
from PIL import Image, ImageDraw
d = os.path.join(sys.argv[1], 'out', 'check'); m = sys.argv[2] if len(sys.argv) > 2 else 'desktop'
fs = sorted(glob.glob(os.path.join(d, m + '_*.png')))
if not fs: sys.exit('no shots')
cols = 4 if m == 'desktop' else 6
w0, h0 = Image.open(fs[0]).size; tw = 480 if m == 'desktop' else 260; th = round(h0 * tw / w0)
rows = -(-len(fs) // cols)
S = Image.new('RGB', (cols * (tw + 12) + 12, rows * (th + 34) + 12), (242, 239, 233)); dr = ImageDraw.Draw(S)
for i, f in enumerate(fs):
    x = 12 + (i % cols) * (tw + 12); y = 12 + (i // cols) * (th + 34)
    S.paste(Image.open(f).convert('RGB').resize((tw, th), Image.LANCZOS), (x, y)); dr.text((x, y + th + 6), os.path.basename(f)[:-4], fill=(15, 19, 23))
out = os.path.join(d, f'_sheet_{m}.png'); S.save(out); print(out)
