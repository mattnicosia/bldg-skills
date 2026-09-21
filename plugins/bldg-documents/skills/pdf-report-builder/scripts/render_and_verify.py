#!/usr/bin/env python3
"""
Render an HTML report to PDF via headless Chrome, then verify every page three
ways: a PNG render per page for a visual look, per-page text extraction so
boundaries can be checked for split words/sentences, and a pixel measurement of
the top-of-page gap on every page -- this last check is the one that's easy to
skip and matters most. A page's top gap = the page margin PLUS whatever leading
margin/padding/border-top the element that happens to land there already had,
and that varies by element (a heading's divider border, a callout's margin, a
plain paragraph's none) -- so pages can look inconsistent even when each one
individually "looks fine" in isolation. Only comparing pages side by side (or
measuring them) catches this.

Usage:
    python3 render_and_verify.py <input.html> <output.pdf> [--dpi 150] [--bg 27,27,27]

Requires: a Chrome/Chromium binary, and PyMuPDF (`pip install pymupdf`).
Prints a page-by-page boundary report and a top-gap measurement per page, and
writes <output_dir>/verify-page-N.png for every page so they can be opened and
looked at directly.
"""
import argparse
import os
import re
import subprocess
import sys


def find_chrome():
    candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium-browser",
        "/usr/bin/chromium",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    raise SystemExit(
        "No Chrome/Chromium binary found. Install Google Chrome, or edit find_chrome() "
        "in this script to point at your browser binary."
    )


def render_pdf(html_path, pdf_path, chrome_path):
    html_abs = os.path.abspath(html_path)
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
    cmd = [
        chrome_path,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        f"--print-to-pdf={pdf_path}",
        "--no-pdf-header-footer",
        "--virtual-time-budget=5000",
        f"file://{html_abs}",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if not os.path.exists(pdf_path):
        raise SystemExit(f"Chrome did not produce a PDF.\nstdout: {result.stdout}\nstderr: {result.stderr}")


def top_gap_pt(pix, dpi, bg, tolerance=5):
    """First row (in points from the top) where a pixel differs from `bg` by
    more than `tolerance` per channel. None if the whole page is background
    (e.g. a trailing blank page)."""
    w, h = pix.width, pix.height
    for y in range(h):
        for x in range(0, w, 3):  # sampling every 3rd column is plenty to catch a full-width element
            p = pix.pixel(x, y)[:3]
            if any(abs(a - b) > tolerance for a, b in zip(p, bg)):
                return round(y / dpi * 72, 1)
    return None


def verify(pdf_path, dpi, bg):
    import fitz  # PyMuPDF

    doc = fitz.open(pdf_path)
    n = doc.page_count
    print(f"\n{n} page(s) rendered.\n")

    out_dir = os.path.dirname(os.path.abspath(pdf_path)) or "."
    texts = []
    gaps = []
    for i in range(n):
        page = doc[i]
        pix = page.get_pixmap(dpi=dpi)
        png_path = os.path.join(out_dir, f"verify-page-{i + 1}.png")
        pix.save(png_path)
        texts.append(page.get_text())
        gaps.append(top_gap_pt(pix, dpi, bg))
        print(f"  saved {png_path}")

    print("\n--- Top-of-page gap (should be the SAME on every page except page 1, which")
    print("    legitimately differs if it has its own header/hero design) ---")
    for i, g in enumerate(gaps):
        print(f"  page {i + 1}: {g}pt" if g is not None else f"  page {i + 1}: (blank)")
    non_first = [g for g in gaps[1:] if g is not None]
    if len(non_first) > 1:
        spread = max(non_first) - min(non_first)
        if spread > 3:
            print(f"\n⚠ Pages 2+ vary by {spread:.1f}pt -- that's a real, visible inconsistency, not noise.")
            print("  Likely cause: some element landing at the top of a page still has its own")
            print("  margin-top/padding-top/border-top (a heading's divider border, a callout's")
            print("  margin, a card's own spacing) stacking on top of the @page margin. Whatever")
            print("  content type differs between the flagged pages is where to look -- zero out")
            print("  that leading spacing in a @media print rule so @page margin is the ONLY")
            print("  source of top-of-page spacing. A few tenths of a point is font-glyph-metric")
            print("  noise (different starting characters have different ascender heights) and is fine.")
        else:
            print(f"\nConsistent within {spread:.1f}pt -- fine, that's glyph-metric noise, not a bug.")

    print("\n--- Page-boundary check ---")
    print("A clean boundary ends the prior page on real closing punctuation (. ! ? : \" or a")
    print("component's own closing text like a label) and starts the next page mid-thought only")
    print("if that's an intentional new block (a heading, a new card, a new list item).\n")

    flagged = 0
    sentence_end = re.compile(r'["\')\]]?[.!?:]\s*$')
    for i in range(n - 1):
        tail = texts[i].rstrip()[-160:]
        head = texts[i + 1].lstrip()[:160]
        tail_ok = bool(sentence_end.search(tail)) or tail.endswith(("below.", "above.", "correctly.", "")) or tail == ""
        # A head that starts with a lowercase letter continuing a word/sentence is the
        # strongest signal of a split -- real new sections start with a capital, a heading,
        # a number, a card title, or similar.
        head_continues = bool(head) and head[0].islower()
        suspicious = head_continues or not tail_ok
        marker = "  ⚠ CHECK THIS BOUNDARY" if suspicious else "  ok"
        if suspicious:
            flagged += 1
        print(f"Page {i + 1} -> {i + 2}: {marker}")
        print(f"  ...tail: {tail!r}")
        print(f"  head...: {head!r}\n")

    if flagged:
        print(f"⚠ {flagged} boundary(ies) flagged -- READ them yourself, don't just trust this heuristic.")
        print("  A false positive (e.g. a new card starting with a lowercase word on purpose) is fine.")
        print("  A false negative is the dangerous direction: always look at the actual PNGs too.")
    else:
        print("No boundary looked suspicious by this heuristic -- still open a couple of the PNGs")
        print("yourself before calling it done. The heuristic catches obvious splits, not everything.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html_path")
    ap.add_argument("pdf_path")
    ap.add_argument("--dpi", type=int, default=150)
    ap.add_argument(
        "--bg",
        default="255,255,255",
        help="Page background color as 'R,G,B' (default white). Set this to your report's "
        "actual background, e.g. --bg 27,27,27 for a dark theme, so the top-gap measurement "
        "knows what counts as 'no content yet'.",
    )
    args = ap.parse_args()
    bg = tuple(int(c) for c in args.bg.split(","))

    chrome = find_chrome()
    render_pdf(args.html_path, args.pdf_path, chrome)
    verify(args.pdf_path, args.dpi, bg)


if __name__ == "__main__":
    main()
