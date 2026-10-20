#!/usr/bin/env python3
"""
prefill.py -- draft a readings file from a vector plan sheet.

An accelerator, not a second path. It reads the text layer of one plan sheet (the
per-sheet PDF drawing-index made), finds room tags and dimension strings with their
coordinates, and writes a draft readings file where each room lists the dimension
strings printed nearest to it. A person then orders the edges clockwise from the
north-west corner, sets each heading, fixes the anchor, and confirms. Until then every
entry carries "draft": true and build.py refuses it.

Nothing here measures anything off the image. It only reads printed text.

  python3 -I prefill.py drawings/sheets/A-101.pdf --level L1 --sheet A-101 --out readings.draft.json
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys

try:
    import fitz  # PyMuPDF
except ImportError:  # pragma: no cover
    fitz = None

# Feet, an optional dash, inches, an optional fraction. Spaces may sit anywhere between
# the parts, because Revit prints 11' - 0 1/2" as four separate words.
DIM_RE = re.compile(r"^(\d{1,3})'\s*-?\s*(\d{1,2})(?:\s+(\d{1,2}/\d{1,2}))?\"?$")
ROOM_WORDS = {"ROOM", "KITCHEN", "BEDROOM", "BATH", "BATHROOM", "ENTRY", "FOYER", "HALL", "CORRIDOR", "OFFICE",
              "STUDY", "MECH", "MECHANICAL", "CLOSET", "LAUNDRY", "PANTRY", "DINING", "LIVING", "GREAT", "DECK",
              "PORCH", "GARAGE", "STORAGE", "STOR", "UTILITY", "PRIMARY", "MASTER", "SUITE", "DEN", "MUD", "POWDER"}
NUMBER_RE = re.compile(r"^\d{3}[A-Z]?$")


def words(page):
    for x0, y0, x1, y1, text, *_ in page.get_text("words"):
        yield {"x": (x0 + x1) / 2, "y": (y0 + y1) / 2, "text": text.strip()}


def lines(page):
    """One entry per text line, its spans joined, at the line's centre."""
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            text = re.sub(r"\s+", " ", " ".join(sp["text"] for sp in line["spans"])).strip()
            if text:
                x0, y0, x1, y1 = line["bbox"]
                yield {"x": (x0 + x1) / 2, "y": (y0 + y1) / 2, "text": text}


def join_dims(ls: list[dict]) -> list[dict]:
    """Dimension strings in each line, written the one way geometry.py reads them.

    A string may be one word (33'-0") or split across up to four (11' - 0 1/2"), so try
    the longest run of words first at each position.
    """
    out = []
    for ln in ls:
        toks = ln["text"].split(" ")
        i = 0
        while i < len(toks):
            for k in (4, 3, 2, 1):
                m = DIM_RE.match(" ".join(toks[i:i + k]))
                if m:
                    ft, inch, frac = m.groups()
                    i += k
                    if int(ft) == 0 and int(inch) == 0 and not frac:
                        break  # a level marker's 0'-0", not a length
                    out.append({"text": f"{ft}'-{inch}" + (f" {frac}" if frac else "") + '"', "x": ln["x"], "y": ln["y"]})
                    break
            else:
                i += 1
    return out


def room_tags(ws: list[dict]) -> list[dict]:
    tags = []
    for i, w in enumerate(ws):
        t = w["text"].upper().strip(".,:")
        if t in ROOM_WORDS:
            name = t
            if i + 1 < len(ws) and ws[i + 1]["text"].upper() in ROOM_WORDS:
                name += " " + ws[i + 1]["text"].upper()
            tags.append({"name": name, "x": w["x"], "y": w["y"], "number": None})
        elif NUMBER_RE.match(t):
            tags.append({"name": None, "x": w["x"], "y": w["y"], "number": t})
    return tags


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf")
    ap.add_argument("--page", type=int, default=1, help="1-based page in that PDF")
    ap.add_argument("--level", required=True)
    ap.add_argument("--sheet", required=True, help="sheet number for the citations, as the set prints it")
    ap.add_argument("--near", type=int, default=6, help="how many nearby dimension strings to list per room")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    if fitz is None:
        sys.exit("prefill.py needs PyMuPDF: pip install pymupdf")

    doc = fitz.open(a.pdf)
    page = doc[a.page - 1]
    ws = list(words(page))
    dims = join_dims(list(lines(page)))
    tags = room_tags(ws)
    spaces = []
    for t in tags:
        near = sorted(dims, key=lambda d: math.hypot(d["x"] - t["x"], d["y"] - t["y"]))[: a.near]
        spaces.append({
            "level": a.level, "number": t["number"], "name": t["name"],
            "draft": True, "anchor": [0, 0], "anchorSource": "DRAFT: set from the grid",
            "edges": [{"heading": "?", "length": d["text"], "source": a.sheet,
                       "_atPt": [round(d["x"], 1), round(d["y"], 1)]} for d in near],
            "_tagAtPt": [round(t["x"], 1), round(t["y"], 1)],
        })
    draft = {"job": None, "revision": {"id": None, "label": None, "date": None, "sheets": [a.sheet]},
             "north": {"source": f"{a.sheet} north arrow", "confirmedBy": None},
             "levels": [{"id": a.level, "elevationFt": None}],
             "spaces": spaces, "exterior": [], "roofs": [], "hosts": [],
             "_draft": f"{len(tags)} room tags and {len(dims)} dimension strings read from {a.sheet} page {a.page}. "
                       "Order each room's edges clockwise from the north-west corner, set headings, fix anchors, "
                       "delete strings that belong to another room, then remove the draft flags."}
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(draft, f, indent=1)
    print(f"{a.sheet}: {len(tags)} room tags, {len(dims)} dimension strings -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
