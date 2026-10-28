# Material swatches for the Selections cards, drawn procedurally (illustrative, never a product photo).
#   python3 tools/sel/swatches.py <out_dir> [name ...]     names: stone millings tarchip grid concrete asphalt sedum epdm oak tile
# Writes <out_dir>/sw_<name>.jpg at 720 x 720. Replace any of them with a supplier or job photo of the same name when there is one.
import os, sys
import numpy as np
from scipy.spatial import cKDTree
from scipy.ndimage import gaussian_filter, sobel
from PIL import Image

S = 720
yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
P = np.stack([xx.ravel(), yy.ravel()], 1)


def noise(scale, seed, shape=(S, S)):
    r = np.random.default_rng(seed).random(shape).astype(np.float32)
    n = gaussian_filter(r, scale, mode='wrap')
    return (n - n.min()) / (n.max() - n.min() + 1e-6)


def stones(n, palette, gap=0.7, gapcol=(40, 38, 36), seed=1, shade=1.0):
    """Voronoi stones with rounded shading and dark joints."""
    g = np.random.default_rng(seed)
    pts = g.random((n, 2)) * S
    d, i = cKDTree(pts, boxsize=S).query(P, k=2)
    d1, d2 = d[:, 0].reshape(S, S), d[:, 1].reshape(S, S)
    cols = np.array(palette, np.float32)[g.integers(0, len(palette), n)] * (0.82 + 0.36 * g.random((n, 1)))
    img = cols[i[:, 0].reshape(S, S)]
    edge = d2 - d1
    hs = gaussian_filter(np.sqrt(np.clip(edge / (np.median(d1) + 1e-6), 0, 1.6)), 1.8)
    light = np.clip(1.0 + shade * (-0.55 * sobel(hs, 1) - 0.75 * sobel(hs, 0)), 0.45, 1.5)
    img = img * light[..., None]
    crack = np.clip(edge / gap, 0, 1)[..., None]
    return img * crack + np.array(gapcol, np.float32) * (1 - crack)


def grain(img, amt, seed):
    return img + (np.random.default_rng(seed).random((S, S, 1)).astype(np.float32) - 0.5) * amt


def sw_stone():      # Item 4 crushed stone with fines
    fines = stones(9000, [(150, 148, 143), (128, 126, 122), (170, 166, 158), (112, 110, 106)], gap=0.9, gapcol=(96, 93, 88), seed=11, shade=0.6)
    big = stones(900, [(146, 146, 144), (124, 125, 126), (165, 160, 150), (106, 107, 108), (182, 176, 165)], gap=1.4, gapcol=(78, 76, 72), seed=12)
    return grain(np.where((noise(3, 5) > 0.47)[..., None], big, fines), 14, 3)


def sw_millings():   # recycled asphalt millings
    return grain(stones(5200, [(52, 50, 48), (40, 39, 38), (66, 63, 59), (30, 30, 30), (92, 88, 82)], gap=1.0, gapcol=(18, 18, 18), seed=21, shade=0.9), 16, 3)


def sw_tarchip():    # chips set in a dark binder
    return grain(stones(3600, [(150, 144, 134), (126, 122, 116), (168, 160, 146), (110, 108, 104)], gap=4.6, gapcol=(20, 19, 18), seed=31, shade=1.1), 12, 3)


def sw_asphalt():
    base = 46 + 18 * noise(1.0, 41) + 10 * noise(6, 42)
    spk = gaussian_filter((np.random.default_rng(43).random((S, S)) > 0.985).astype(np.float32), 0.7) * 260
    return grain(np.stack([base + spk * 0.55, base + spk * 0.54, base + spk * 0.52], -1), 6, 3)


def sw_concrete():   # broom finish
    c = 178 + 10 * noise(14, 51)
    st = gaussian_filter(np.random.default_rng(52).random((S, S)).astype(np.float32), (0.6, 22), mode='wrap')
    c = c + 7 * (st - st.mean()) / (st.std() + 1e-6)
    return grain(np.stack([c, c - 2, c - 6], -1), 7, 3)


def sw_grid():       # stone-filled grid pavers
    st = stones(5000, [(150, 148, 143), (128, 126, 122), (170, 166, 158)], gap=1.0, gapcol=(92, 89, 85), seed=61, shade=0.7)
    cell = 60.0
    q = xx / (cell * 0.866); r = yy / cell - 0.5 * (np.floor(q) % 2)
    fx, fy = q - np.floor(q) - 0.5, r - np.floor(r) - 0.5
    wall = (np.minimum(0.5 - np.abs(fx), 0.5 - np.abs(fy)) < 0.045)[..., None]
    return grain(np.where(wall, np.array([34, 36, 34], np.float32), st), 10, 3)


def sw_sedum():
    sed = stones(9000, [(92, 118, 54), (110, 136, 62), (124, 146, 70), (80, 102, 46), (138, 112, 64), (100, 128, 60)], gap=1.6, gapcol=(40, 50, 26), seed=71, shade=0.8)
    return grain(np.stack([gaussian_filter(sed[..., k], 0.8) for k in range(3)], -1), 10, 3)


def sw_epdm():
    e = 38 + 6 * noise(18, 81) + 3 * noise(2, 82)
    e = np.where(np.abs(yy - S * 0.62) < 2.5, e + 14, e)
    return grain(np.stack([e, e, e + 1], -1), 4, 3)


def sw_oak():        # 5 to 7 inch white oak, site finished natural
    rng = np.random.default_rng(5)
    img = np.zeros((S, S, 3), np.float32)
    gr = gaussian_filter(np.random.default_rng(1).random((S, S)).astype(np.float32), (40, 0.8), mode='wrap')
    gr = (gr - gr.mean()) / gr.std()
    x = 0
    while x < S:
        w = int(rng.choice([66, 80, 92])); y = -int(rng.integers(0, 400))
        while y < S:
            L = int(rng.integers(300, 640)); y0, y1 = max(0, y), min(S, y + L)
            img[y0:y1, x:x + w] = np.array([206, 170, 124]) * (0.9 + 0.18 * rng.random())
            img[y0:y1, x:x + w] += gr[y0:y1, x:x + w, None] * 9 + (noise(6, int(rng.integers(1e6)))[y0:y1, x:x + w, None] - .5) * 18
            if 0 < y < S: img[y:y + 2, x:x + w] *= 0.62
            y += L
        img[:, min(S - 1, x + w - 1):min(S, x + w + 1)] *= 0.6
        x += w
    return grain(img, 5, 9)


def sw_tile():       # large-format porcelain, warm grey
    t = 196 + 8 * noise(30, 21) + 5 * noise(4, 22)
    v = gaussian_filter(np.random.default_rng(23).random((S, S)).astype(np.float32), (10, 60), mode='wrap')
    t = t - 10 * np.exp(-np.abs((v - v.mean()) / v.std()) * 3)
    tile = np.stack([t, t - 3, t - 8], -1)
    tile[S // 2 - 2:S // 2 + 2] = (150, 146, 140); tile[:, 0:3] = (150, 146, 140); tile[:, S - 3:] = (150, 146, 140)
    return tile


ALL = {k[3:]: f for k, f in globals().items() if k.startswith('sw_') and callable(f)}

if __name__ == '__main__':
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    for name in (sys.argv[2:] or ALL):
        Image.fromarray(np.clip(ALL[name](), 0, 255).astype(np.uint8)).save(os.path.join(out, f'sw_{name}.jpg'), quality=88)
        print('wrote', f'sw_{name}.jpg')
