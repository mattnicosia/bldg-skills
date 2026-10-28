#!/usr/bin/env python3
"""Photographic finish for hero frames: gentle tone curve, split tone, vignette, fine sharpening, grain.

    python3 tools/render/post.py <in.png> [out.jpg] [--ev 0.0] [--warm 0.025] [--vignette 0.16] [--grain 0.8] [--lift 0.0]
"""
import sys, numpy as np, imageio.v3 as iio
from PIL import Image, ImageFilter

A = sys.argv
opt = lambda k, d: float(A[A.index(k) + 1]) if k in A else d
src = A[1]; dst = A[2] if len(A) > 2 and not A[2].startswith('--') else src.rsplit('.', 1)[0] + '.jpg'
im = iio.imread(src).astype(np.float32)
im = im[..., :3] / (65535.0 if im.max() > 255 else 255.0)
H, W = im.shape[:2]
# tone: a soft S around the middle, shadows kept open
lift = opt('--lift', 0.0)
ev = opt('--ev', 0.0)   # exposure in stops, applied to the display image before the curve
x = np.clip(im * (2 ** ev), 0, 1)
s = x + 0.10 * np.sin((x - 0.5) * np.pi) * (1 - np.abs(x - 0.5) * 1.2)
s = lift + (1 - lift) * s
# split tone: warm highlights, slightly cool shadows
lum = (0.2126 * s[..., 0] + 0.7152 * s[..., 1] + 0.0722 * s[..., 2])[..., None]
warm = opt('--warm', 0.025)
s = s + warm * np.clip(lum - 0.45, 0, 1) * np.array([1.0, 0.35, -0.8]) + warm * 0.6 * np.clip(0.35 - lum, 0, 1) * np.array([-0.5, 0.0, 0.7])
# vignette, elliptical, very soft
yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / np.sqrt(2)
s = s * (1 - opt('--vignette', 0.16) * np.clip(r - 0.25, 0, 1) ** 1.6)[..., None]
out = Image.fromarray((np.clip(s, 0, 1) * 255 + 0.5).astype(np.uint8))
out = out.filter(ImageFilter.UnsharpMask(radius=1.1, percent=55, threshold=2))
g = opt('--grain', 0.8)
if g:
    a = np.asarray(out).astype(np.float32)
    rng = np.random.default_rng(7); n = rng.normal(0, g, (H, W, 1))
    a = np.clip(a + n * (1.2 - a / 255.0), 0, 255)
    out = Image.fromarray(a.astype(np.uint8))
out.save(dst, quality=93, subsampling=0, optimize=True)
print('wrote', dst)
