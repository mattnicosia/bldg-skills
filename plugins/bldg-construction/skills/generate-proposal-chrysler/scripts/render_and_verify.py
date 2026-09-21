#!/usr/bin/env python3
"""Render an HTML proposal to PDF via headless Chrome and verify the result.

Checks (per the pdf-report-builder skill):
  1. No text unit split across a page boundary (heuristic + report for human read).
  2. Consistent top-of-page content gap on every page (measured in pixels at 150dpi).
  3. Renders every page to PNG for visual inspection.

Usage: python3 render_and_verify.py input.html output.pdf [--bg R,G,B]
"""
import argparse, os, re, shutil, subprocess, sys, tempfile

CHROME_CANDIDATES = [
    "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
    shutil.which("google-chrome"), shutil.which("chromium"),
    shutil.which("chromium-browser"),
]

def find_chrome():
    for c in CHROME_CANDIDATES:
        if c and os.path.exists(c):
            return c
    # glob any pw-browsers chromium
    import glob
    hits = glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome")
    if hits:
        return hits[0]
    sys.exit("No Chrome/Chromium binary found — cannot render at full fidelity.")

def render(chrome, html, pdf):
    cmd = [chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
           "--no-pdf-header-footer", "--print-to-pdf=" + pdf,
           "--virtual-time-budget=10000", "file://" + os.path.abspath(html)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if not os.path.exists(pdf):
        sys.exit("Chrome failed to produce PDF:\n" + r.stderr[-2000:])

def page_texts(pdf):
    out = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True,
                         text=True).stdout
    return out.split("\f")

def check_boundaries(pages):
    flags = []
    for i in range(len(pages) - 1):
        a = pages[i].rstrip()
        b = pages[i + 1].lstrip()
        if not a or not b:
            continue
        last = a.splitlines()[-1].strip() if a.splitlines() else ""
        first = b.splitlines()[0].strip() if b.splitlines() else ""
        # suspicious if previous page ends without terminal punctuation
        if last and last[-1] not in ".:;!?•)\"'”" and not re.match(r"^\d", last):
            flags.append((i + 1, last, first))
    return flags

def check_top_gaps(pdf, bg, outdir):
    """Render pages to PNG and measure the first non-background row per page."""
    from PIL import Image
    subprocess.run(["pdftoppm", "-r", "150", "-png", pdf,
                    os.path.join(outdir, "page")], check=True)
    pngs = sorted(f for f in os.listdir(outdir) if f.endswith(".png"))
    gaps = []
    for p in pngs:
        im = Image.open(os.path.join(outdir, p)).convert("RGB")
        w, h = im.size
        px = im.load()
        gap = h
        for y in range(h):
            row_hit = False
            for x in range(0, w, 4):
                r, g, b = px[x, y]
                if abs(r - bg[0]) > 12 or abs(g - bg[1]) > 12 or abs(b - bg[2]) > 12:
                    row_hit = True
                    break
            if row_hit:
                gap = y
                break
        gaps.append((p, gap))
    return gaps, pngs

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html"); ap.add_argument("pdf")
    ap.add_argument("--bg", default="255,255,255")
    ap.add_argument("--pngdir", default=None)
    a = ap.parse_args()
    bg = tuple(int(v) for v in a.bg.split(","))
    chrome = find_chrome()
    render(chrome, a.html, a.pdf)
    pages = page_texts(a.pdf)
    n = len([p for p in pages if p.strip()])
    print(f"PDF rendered: {a.pdf} — {n} page(s)")

    flags = check_boundaries(pages)
    if flags:
        print("\n== Boundary check: READ THESE ==")
        for pg, last, first in flags:
            print(f"  p{pg}->p{pg+1}: ...'{last[-60:]}' | '{first[:60]}'...")
    else:
        print("Boundary check: clean")

    outdir = a.pngdir or tempfile.mkdtemp(prefix="verify_")
    os.makedirs(outdir, exist_ok=True)
    gaps, pngs = check_top_gaps(a.pdf, bg, outdir)
    vals = [g for _, g in gaps]
    print("\nTop-of-page gaps (px @150dpi):")
    for p, g in gaps:
        print(f"  {p}: {g}")
    spread = max(vals) - min(vals) if vals else 0
    print(f"Gap spread: {spread}px " + ("OK" if spread <= 6 else "!! INCONSISTENT — fix top spacing"))
    print(f"Page PNGs in: {outdir}")

if __name__ == "__main__":
    main()
