"""
markup_pdf.py -- Stamp counts and dimensions onto a source PDF for visual audit.

The marked-up PDF is the audit trail. Using the (x, y) coordinates captured by
extract_text_tags.py, this draws a highlight box (and optional numbered label) on
every counted tag, and annotates extracted dimensions, so the estimator can open the
result in Bluebeam or any viewer and confirm: "BOQ says 18 pad footings, I see 18
boxes." A miscount or a measurement bleeding into the wrong structural system is
caught visually here, before it reaches the estimate.

markup_data.json schema:
{
  "annotations": [
    { "page": 2, "type": "count", "label": "P1",
      "marks": [ {"x":120.5,"y":300.2}, {"x":210.0,"y":300.2}, ... ] },
    { "page": 1, "type": "dimension", "label": "Slab 100m x 82m",
      "x": 400.0, "y": 250.0 }
  ]
}

The "marks" array for a count is exactly the "matches" array produced by
extract_text_tags.py (each has x, y). You can pass that through directly.

Usage:
    python markup_pdf.py source.pdf markup_data.json output.pdf

Requires: PyMuPDF (fitz)
"""

import json
import sys

import fitz  # PyMuPDF

# All within a restrained black/gray scheme; highlight uses a translucent box.
BOX_COLOR = (0.0, 0.0, 0.0)        # black stroke
BOX_FILL = (0.78, 0.78, 0.78)      # light gray fill
LABEL_COLOR = (0.0, 0.0, 0.0)
HALF = 9.0  # half-size of the highlight box, in points


def stamp_count(page, ann):
    marks = ann.get("marks", [])
    label = ann.get("label", "")
    for i, m in enumerate(marks, start=1):
        x, y = m["x"], m["y"]
        rect = fitz.Rect(x - HALF, y - HALF, x + HALF, y + HALF)
        page.draw_rect(rect, color=BOX_COLOR, fill=BOX_FILL,
                       width=0.8, fill_opacity=0.35, stroke_opacity=0.9)
    # Running tally label near the first mark
    if marks:
        fx, fy = marks[0]["x"], marks[0]["y"]
        page.insert_text((fx + HALF + 2, fy - HALF),
                         f"{label} x{len(marks)}",
                         fontsize=7, color=LABEL_COLOR)


def stamp_dimension(page, ann):
    x, y = ann.get("x", 0), ann.get("y", 0)
    label = ann.get("label", "")
    rect = fitz.Rect(x, y - 8, x + max(60, len(label) * 5), y + 6)
    page.draw_rect(rect, color=BOX_COLOR, fill=(1, 1, 1),
                   width=0.6, fill_opacity=0.85)
    page.insert_text((x + 2, y + 2), label, fontsize=7, color=LABEL_COLOR)


def main():
    if len(sys.argv) < 4:
        print("Usage: python markup_pdf.py source.pdf markup_data.json output.pdf")
        sys.exit(1)

    src, data_path, out = sys.argv[1], sys.argv[2], sys.argv[3]
    with open(data_path, encoding="utf-8") as fh:
        data = json.load(fh)

    doc = fitz.open(src)
    n = 0
    for ann in data.get("annotations", []):
        pi = ann.get("page", 1) - 1
        if pi < 0 or pi >= len(doc):
            continue
        page = doc[pi]
        if ann.get("type") == "count":
            stamp_count(page, ann)
            n += len(ann.get("marks", []))
        elif ann.get("type") == "dimension":
            stamp_dimension(page, ann)
            n += 1

    doc.save(out, garbage=4, deflate=True)
    doc.close()
    print(f"Stamped {n} annotations -> {out}")


if __name__ == "__main__":
    main()
