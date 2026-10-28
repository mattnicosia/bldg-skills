# The Walk Your Plans image: the job's floor plan as light linework laid on a dark floor in perspective (kit v1.9).
#   python3 tools/wyp/plan_floor.py <plan.pdf> <out.jpg> --crop x0,y0,x1,y1 [--page 1] [--erase x0,y0,x1,y1 ...]
# --crop is the house on the sheet as fractions of the page (0 to 1). --erase boxes are fractions of the crop: notes, dimension
# strings and site features that should not glow. Writes 1800 x 930, about 150 KB. Build reads <job>/wyp/wyp_plan.jpg.
# E26049: --crop .1882,.2606,.7608,.7879 --erase 0,.885,.267,1 .798,0,1,.078 0,0,.322,.086 0,0,.027,1 .63,.96,.767,1 0,0,1,.018
import argparse, os, subprocess, tempfile
import numpy as np
from PIL import Image, ImageFilter

ap = argparse.ArgumentParser()
ap.add_argument('pdf'); ap.add_argument('out')
ap.add_argument('--crop', required=True); ap.add_argument('--page', type=int, default=1)
ap.add_argument('--erase', nargs='*', default=[])
a = ap.parse_args()
fl = lambda s: [float(v) for v in s.split(',')]

with tempfile.TemporaryDirectory() as td:
    subprocess.run(['pdftoppm', '-r', '300', '-f', str(a.page), '-l', str(a.page), '-png', a.pdf, os.path.join(td, 'p')], check=True)
    im = Image.open(os.path.join(td, sorted(os.listdir(td))[0])).convert('L')
x0, y0, x1, y1 = fl(a.crop)
c = im.crop((int(x0 * im.width), int(y0 * im.height), int(x1 * im.width), int(y1 * im.height)))
g = np.asarray(c).astype(np.float32) / 255
ink = np.clip((0.92 - g) / 0.92, 0, 1) ** 0.8          # line strength from the drawing's own ink
H, W = ink.shape
for e in a.erase:
    ex0, ey0, ex1, ey1 = fl(e)
    ink[int(ey0 * H):int(ey1 * H), int(ex0 * W):int(ex1 * W)] = 0
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)          # soft edge so the plan dissolves into the dark
d = np.sqrt(((xx - W * .53) / (W * .62)) ** 2 + ((yy - H * .52) / (H * .68)) ** 2)
ink = ink * np.clip(np.clip(1.25 - d, 0, 1) ** 1.2 * 1.15, 0, 1)
m = Image.fromarray((ink * 255).astype(np.uint8))
glow = np.asarray(m.filter(ImageFilter.GaussianBlur(11))).astype(np.float32) / 255
glow2 = np.asarray(m.filter(ImageFilter.GaussianBlur(3))).astype(np.float32) / 255
out = glow[..., None] * np.array([50, 90, 255], np.float32) * 1.5 + glow2[..., None] * np.array([110, 140, 255], np.float32) * .85 \
    + ink[..., None] * np.array([232, 238, 255], np.float32)
flat = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))

def coeffs(src, dst):   # perspective map: output corners -> source corners
    A, B = [], []
    for (x, y), (X, Y) in zip(dst, src):
        A += [[x, y, 1, 0, 0, 0, -X * x, -X * y], [0, 0, 0, x, y, 1, -Y * x, -Y * y]]; B += [X, Y]
    return np.linalg.solve(np.array(A, float), np.array(B, float)).tolist()
OW, OH = 2400, 1240                                        # the far edge narrower: a floor seen from standing height
p = flat.transform((OW, OH), Image.PERSPECTIVE, coeffs([(0, 0), (W, 0), (W, H), (0, H)], [(470, 70), (OW - 470, 70), (OW + 60, OH + 20), (-60, OH + 20)]), Image.BICUBIC)
p.resize((1800, 930), Image.LANCZOS).save(a.out, quality=84, optimize=True, progressive=True)
print('wrote', a.out, os.path.getsize(a.out), 'bytes')
