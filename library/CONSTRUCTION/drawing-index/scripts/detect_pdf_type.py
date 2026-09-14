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

# A page needs at least this many extractable words before we call its text layer usable.
MIN_WORDS_VECTOR = 25
# Below this, but non-zero, we call it "sparse".
MIN_WORDS_SPARSE = 5


def analyze_page(page):
    text = page.get_text("text") or ""
    words = page.get_text("words") or []
    n_words = len(words)
    n_chars = len(text.strip())

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

    if n_words >= MIN_WORDS_VECTOR:
        verdict = "vector"
    elif n_words >= MIN_WORDS_SPARSE:
        verdict = "sparse"
    else:
        verdict = "image_only"

    return {
        "chars": n_chars,
        "words": n_words,
        "images": n_images,
        "text_coverage": text_coverage,
        "verdict": verdict,
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
        print(f"  {'pg':>3}  {'verdict':<11} {'words':>6} {'chars':>7} {'imgs':>4}  text_cov")
        for p in r["pages"]:
            print(f"  {p['page']:>3}  {p['verdict']:<11} {p['words']:>6} "
                  f"{p['chars']:>7} {p['images']:>4}  {p['text_coverage']:.3f}")
        n_vec = sum(1 for p in r["pages"] if p["verdict"] == "vector")
        n_img = sum(1 for p in r["pages"] if p["verdict"] == "image_only")
        n_sp = sum(1 for p in r["pages"] if p["verdict"] == "sparse")
        print(f"  -> {n_vec} vector (count reliably), {n_sp} sparse (verify), "
              f"{n_img} image-only (vision fallback, LOW confidence)")


if __name__ == "__main__":
    main()
