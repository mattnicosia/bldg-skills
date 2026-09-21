"""
split_and_render.py -- Split a drawing set into per-sheet PDFs and render only the
pages that actually need a vision pass.

This is the step that makes everything downstream cheap. A 75-page, 12 MB drawing set
never enters a context window again after this runs. Instead you get:

  sheets/A-101.pdf, sheets/A-102.pdf, ...   one small PDF per sheet, named by sheet no.
  images/M-601.png, ...                     rendered ONLY for pages with no text layer
  sheets.json                               the manifest: page -> sheet no, discipline,
                                            text-layer verdict, needs_vision flag

Why render selectively: on a set with a real embedded text layer, rendering every page
to an image and running vision on all of them costs orders of magnitude more than
pulling text per page and using vision only where text extraction comes back empty.
That selective approach is the validated method -- do not render the whole set by reflex.

Sheet numbers are read from the titleblock text (bottom-right quadrant, largest type
wins). When no sheet number can be found the page is named `page-NNN` and flagged
`sheet_number_found: false` -- fix those by hand rather than trusting a guess.

Usage:
    python split_and_render.py <set.pdf> --out drawings/
    python split_and_render.py <set.pdf> --out drawings/ --dpi 220
    python split_and_render.py <set.pdf> --out drawings/ --render-all   # rarely correct
    python split_and_render.py <folder-of-pdfs>/ --out drawings/

Requires: PyMuPDF (fitz)
"""

import sys
import os
import re
import glob
import json

import fitz  # PyMuPDF

# Same thresholds as detect_pdf_type.py -- keep these two files in agreement.
MIN_WORDS_VECTOR = 25
MIN_WORDS_SPARSE = 5

# Construction sheet numbers: A-101, A101, A1.01, M-601, S-3.01, FA-101, C-1, G-001.
SHEET_RX = re.compile(r"^[A-Z]{1,3}[-.]?\d{1,3}(?:\.\d{1,2})?[A-Z]?$")

DISCIPLINE = {
    "G": "General", "GN": "General", "T": "Title/General", "CS": "General",
    "C": "Civil", "L": "Landscape", "LS": "Life Safety",
    "A": "Architectural", "AD": "Architectural Demolition", "AS": "Architectural Site",
    "DM": "Demolition", "D": "Demolition",
    "ID": "Interior Design", "FN": "Finishes", "EQ": "Equipment",
    "S": "Structural", "SD": "Structural Details",
    "M": "Mechanical", "MD": "Mechanical Demolition",
    "P": "Plumbing", "PD": "Plumbing Demolition",
    "FP": "Fire Protection", "FS": "Fire Suppression", "SP": "Sprinkler",
    "E": "Electrical", "ED": "Electrical Demolition", "EL": "Lighting",
    "FA": "Fire Alarm", "LV": "Low Voltage", "TC": "Telecom", "AV": "Audio Visual",
    "K": "Kitchen", "Q": "Kitchen/Foodservice",
}


def get_arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default


def page_stats(page):
    words = page.get_text("words") or []
    n_words = len(words)
    try:
        n_images = len(page.get_images(full=True))
    except Exception:
        n_images = 0
    if n_words >= MIN_WORDS_VECTOR:
        verdict = "vector"
    elif n_words >= MIN_WORDS_SPARSE:
        verdict = "sparse"
    else:
        verdict = "image_only"
    return verdict, n_words, n_images


def find_sheet_number(page):
    """Titleblock-first sheet-number detection. Returns (sheet_no|None, how)."""
    try:
        d = page.get_text("dict")
    except Exception:
        return None, "no_text"

    r = page.rect
    # Titleblock is conventionally the bottom-right corner of the sheet.
    tb_x, tb_y = r.x0 + r.width * 0.62, r.y0 + r.height * 0.55

    candidates = []
    for block in d.get("blocks", []):
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                size = span.get("size", 0)
                bbox = span.get("bbox", (0, 0, 0, 0))
                for tok in (span.get("text") or "").split():
                    tok = tok.strip().strip(":").upper()
                    if not tok or not any(c.isdigit() for c in tok):
                        continue
                    if not SHEET_RX.match(tok):
                        continue
                    in_tb = bbox[0] >= tb_x and bbox[1] >= tb_y
                    candidates.append((in_tb, size, tok))

    if not candidates:
        return None, "not_found"
    # Prefer titleblock region, then largest type.
    candidates.sort(key=lambda c: (c[0], c[1]), reverse=True)
    best = candidates[0]
    return best[2], ("titleblock" if best[0] else "page_body")


def discipline_for(sheet_no):
    if not sheet_no:
        return "Unknown"
    m = re.match(r"^([A-Z]{1,3})", sheet_no)
    if not m:
        return "Unknown"
    prefix = m.group(1)
    return DISCIPLINE.get(prefix) or DISCIPLINE.get(prefix[0]) or "Unknown"


def safe_name(name, used):
    base = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    out, n = base, 2
    while out in used:
        out = f"{base}_{n}"
        n += 1
    used.add(out)
    return out


def process(paths, outdir, dpi, render_all):
    sheets_dir = os.path.join(outdir, "sheets")
    images_dir = os.path.join(outdir, "images")
    os.makedirs(sheets_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)

    manifest, used_names = [], set()
    global_page = 0

    for path in paths:
        doc = fitz.open(path)
        for pi in range(len(doc)):
            global_page += 1
            page = doc[pi]
            verdict, n_words, n_images = page_stats(page)
            sheet_no, how = find_sheet_number(page)
            found = sheet_no is not None
            name = safe_name(sheet_no or f"page-{global_page:03d}", used_names)

            # One-page PDF per sheet.
            sheet_pdf = os.path.join(sheets_dir, f"{name}.pdf")
            one = fitz.open()
            one.insert_pdf(doc, from_page=pi, to_page=pi)
            one.save(sheet_pdf, garbage=4, deflate=True)
            one.close()

            needs_vision = verdict in ("image_only", "sparse")
            image_path = None
            if needs_vision or render_all:
                pix = page.get_pixmap(dpi=dpi)
                # Some vision endpoints reject very large images; cap the long edge.
                if max(pix.width, pix.height) > 2200:
                    scale = 2200 / max(pix.width, pix.height)
                    pix = page.get_pixmap(dpi=int(dpi * scale))
                image_path = os.path.join(images_dir, f"{name}.png")
                pix.save(image_path)

            manifest.append({
                "sheet_number": sheet_no or name,
                "sheet_number_found": found,
                "sheet_number_source": how,
                "discipline": discipline_for(sheet_no),
                "source_file": os.path.basename(path),
                "source_page": pi + 1,
                "global_page": global_page,
                "text_layer": verdict,
                "words": n_words,
                "raster_images": n_images,
                "needs_vision": needs_vision,
                "sheet_pdf": os.path.relpath(sheet_pdf, outdir),
                "image": os.path.relpath(image_path, outdir) if image_path else None,
                "extracted": False,
            })
        doc.close()

    with open(os.path.join(outdir, "sheets.json"), "w", encoding="utf-8") as f:
        json.dump({"sheet_count": len(manifest), "sheets": manifest},
                  f, indent=2, ensure_ascii=True)
    return manifest


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    outdir = get_arg("--out")
    if not args or not outdir:
        print(__doc__)
        sys.exit(1)
    outdir = get_arg("--out")
    args = [a for a in args if a != outdir and a != get_arg("--dpi")]

    dpi = int(get_arg("--dpi", "200"))
    render_all = "--render-all" in sys.argv

    target = args[0]
    if os.path.isdir(target):
        paths = sorted(glob.glob(os.path.join(target, "*.pdf")))
    else:
        paths = [target]
    if not paths:
        print(f"No PDFs found at {target}")
        sys.exit(1)

    os.makedirs(outdir, exist_ok=True)
    m = process(paths, outdir, dpi, render_all)

    vec = sum(1 for s in m if s["text_layer"] == "vector")
    sp = sum(1 for s in m if s["text_layer"] == "sparse")
    io = sum(1 for s in m if s["text_layer"] == "image_only")
    unnamed = sum(1 for s in m if not s["sheet_number_found"])
    rendered = sum(1 for s in m if s["image"])

    print(f"{len(m)} sheets -> {outdir}")
    print(f"  text layer: {vec} vector | {sp} sparse | {io} image-only")
    print(f"  rendered for vision: {rendered} "
          f"({'all pages, --render-all' if render_all else 'sparse + image-only only'})")
    if unnamed:
        print(f"  WARNING: {unnamed} sheet(s) had no readable sheet number "
              f"-> named page-NNN. Fix these by hand in sheets.json.")
    print("  manifest: sheets.json")


if __name__ == "__main__":
    main()
