# A quiet site plan backdrop for the Selections Site view, from the surveyor's drawing.
#   python3 tools/sel/survey.py <survey.png> <out.jpg> <x0,y0,x1,y1>
# Crops the sheet to the lot, drops the colored slope fills and the survey's own grey driveway fill (the page draws its own),
# and fades the linework to about a third so the driveway reads on top. Record the crop and trace the driveway centerline
# in the cropped image's pixels into selections.json (views.site.path). Width of the drawn drive: views.site.width in the same pixels.
import sys
import numpy as np
from PIL import Image

src, out, box = sys.argv[1], sys.argv[2], [int(v) for v in sys.argv[3].split(',')]
im = np.asarray(Image.open(src).convert('RGB').crop(box)).astype(np.float32)
sat = im.max(-1) - im.min(-1); g = im.mean(-1)
g = np.where(sat > 50, 250, g)                                  # slope-analysis color fills
g = np.where((sat < 14) & (g > 95) & (g < 165), 248, g)         # the survey's grey drive fill
a = 255 - (255 - g) * 0.34
Image.fromarray(np.clip(np.stack([a * 0.99 + 2, a * 0.992 + 2, a], -1), 0, 255).astype(np.uint8)).save(out, quality=90)
print('wrote', out, Image.open(out).size)
