"""
detect_pdf_type.py -- Per-page vector vs. image-only detection for construction PDFs.

A vector PDF has a real, selectable text layer -> AI can extract and count text tags
with near-perfect accuracy (HIGH confidence available). An image-only PDF (scan or
compressed raster) has no text layer -> AI must fall back to vision counting (LOW
confidence). This script tells you, per page, which you are dealing with.

Heuristic per page:
  - chars            = number of extractable text characters in the page's text layer
  - words            = number of extractable words
  - images           = number of raster images placed on the page
  - text_coverage    = fraction of page area covered by text bounding boxes
  - verdict:
        "vector"      -> usable text layer (counting is reliable)
        "image_only"  -> negligible text layer, large raster present (vision fallback)
        "sparse"      -> some text but thin; treat counts as MEDIUM, verify

Usage:
    python detect_pdf_type.py <file.pdf | folder>
    python detect_pdf_type.py drawings/ --json        # machine-readable output

Requires: PyMuPDF (fitz)
"""

import sys
import os
import json
import glob

import fitz  # PyMuPDF

# A page needs at least this many extractable words IN THE DRAWING AREA before
# we call its text layer usable.
MIN_WORDS_VECTOR = 25
# Below this, but non-zero, we call it "sparse".
MIN_WORDS_SPARSE = 5

# The verdict is decided on words in the drawing area, never on the page total.
# A scanned sheet plotted with a vector titleblock clears MIN_WORDS_VECTOR on
# titleblock text alone, so a page-total count calls it "vector" and its drawing
# is never read. Titleblocks sit in a right-hand strip, a bottom strip, or both.
# Keep these in agreement with split_and_render.py.
TITLEBLOCK_RIGHT_FRAC = 0.78
TITLEBLOCK_BOTTOM_FRAC = 0.88


def analyze_page(page):
    text = page.get_text("text") or ""
    words = page.get_text("words") or []
    n_words = len(words)
    n_chars = len(text.strip())

    r = page.rect
    x_cut = r.x0 + r.width * TITLEBLOCK_RIGHT_FRAC
    y_cut = r.y0 + r.height * TITLEBLOCK_BOTTOM_FRAC
    n_body = sum(1 for w in words if w[0] < x_cut and w[1] < y_cut)

    try:
        images = page.get_images(full=True)
    except Exception:
        images = []
    n_images = len(images)

    page_area = abs(page.rect.width * page.rect.height) or 1.0
    text_area = 0.0
    for w in words:
        # word = (x0, y0, x1, y1, text, block, line, word_no)
        x0, y0, x1, y1 = w[0], w[1], w[2], w[3]
        text_area += abs((x1 - x0) * (y1 - y0))
    text_coverage = round(min(text_area / page_area, 1.0), 4)

    if n_body >= MIN_WORDS_VECTOR:
        verdict = "vector"
    elif n_body >= MIN_WORDS_SPARSE:
        verdict = "sparse"
    else:
        verdict = "image_only"

    return {
        "chars": n_chars,
        "words": n_words,
        "drawing_area_words": n_body,
        "images": n_images,
        "text_coverage": text_coverage,
        "verdict": verdict,
        # Zero words in the drawing area beside a raster, on a page whose total
        # would have passed as vector: the scanned-sheet-with-titleblock case.
        "scanned_with_vector_titleblock": (
            n_body == 0 and n_words >= MIN_WORDS_VECTOR and n_images > 0),
    }


def analyze_pdf(path):
    doc = fitz.open(path)
    pages = []
    for i, page in enumerate(doc):
        info = analyze_page(page)
        info["page"] = i + 1
        pages.append(info)
    doc.close()

    verdicts = [p["verdict"] for p in pages]
    if verdicts and all(v == "vector" for v in verdicts):
        overall = "vector"
    elif verdicts and all(v == "image_only" for v in verdicts):
        overall = "image_only"
    else:
        overall = "mixed"

    return {"file": os.path.basename(path), "overall": overall, "pages": pages}


def gather_targets(target):
    if os.path.isdir(target):
        return sorted(glob.glob(os.path.join(target, "*.pdf")) +
                      glob.glob(os.path.join(target, "*.PDF")))
    return [target]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    as_json = "--json" in sys.argv

    if not args:
        print(__doc__)
        sys.exit(1)

    targets = gather_targets(args[0])
    if not targets:
        print(f"No PDF files found at: {args[0]}")
        sys.exit(1)

    results = [analyze_pdf(t) for t in targets]

    if as_json:
        print(json.dumps(results, indent=2, ensure_ascii=True))
        return

    for r in results:
        print(f"\n{r['file']}  ->  OVERALL: {r['overall'].upper()}")
        print(f"  {'pg':>3}  {'verdict':<11} {'draw':>6} {'total':>6} {'chars':>7} "
              f"{'imgs':>4}  text_cov")
        for p in r["pages"]:
            flag = "  <- scanned sheet, vector titleblock" if p.get(
                "scanned_with_vector_titleblock") else ""
            print(f"  {p['page']:>3}  {p['verdict']:<11} {p['drawing_area_words']:>6} "
                  f"{p['words']:>6} {p['chars']:>7} {p['images']:>4}  "
                  f"{p['text_coverage']:.3f}{flag}")
        n_vec = sum(1 for p in r["pages"] if p["verdict"] == "vector")
        n_img = sum(1 for p in r["pages"] if p["verdict"] == "image_only")
        n_sp = sum(1 for p in r["pages"] if p["verdict"] == "sparse")
        n_tb = sum(1 for p in r["pages"] if p.get("scanned_with_vector_titleblock"))
        print(f"  -> {n_vec} vector (count reliably), {n_sp} sparse (verify), "
              f"{n_img} image-only (vision fallback, LOW confidence)")
        print("     'draw' is words in the drawing area and decides the verdict; "
              "'total' includes the titleblock.")
        if n_tb:
            print(f"     {n_tb} page(s) are scanned drawings carrying a vector "
                  f"titleblock. A page-total count would call these vector and "
                  f"never read them.")


if __name__ == "__main__":
    main()
