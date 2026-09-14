"""
extract_text_tags.py -- Text-tag extraction and counting from vector PDF drawings.

Pulls the PDF's vector text layer and counts matching tags with code instead of asking
a vision model to count symbols. Each match returns its text and (x, y) page
coordinates, which feed markup_pdf.py so every count is visually auditable.

  ####################################################################
  #  A RAW TAG COUNT IS *NOT* A VERIFIED QUANTITY.                   #
  #  It is MEDIUM confidence until reconciled against a schedule or  #
  #  a markup review. See "The over-count problem" below.            #
  ####################################################################

## The over-count problem (why this script is not "100% accurate")

The PDF text layer does not distinguish a tag placed on a plan from the same string
appearing in a schedule table, a legend, a keynote list, or a revision block. A sheet
with 8 physical P1 piers whose pier schedule reads "PIER SCHEDULE  P1 QTY 8" yields a
raw count of 9. Verified failure, not a hypothetical.

Three defenses, all reported in the output so nothing is silent:

  1. --context-exclude   Skip a token when another word on its own text line matches an
                         exclusion keyword (SCHEDULE, QTY, TYPE, MARK, LEGEND, ...).
                         Kills the schedule/legend/keynote case. ON BY DEFAULT.
  2. --exclude-rect      Skip tokens inside explicit rectangles (a schedule block, a
                         titleblock, a keynote column). Use when 1 is not enough.
  3. exclusions[]        Everything skipped is listed WITH its reason and coordinates,
                         so a human can confirm the filter did the right thing.

The output carries `verification_required: true` and a `confidence_ceiling`. Honor them.

Two modes:
  --list                 Dump every distinct text token with its count, most frequent
                         first. ALWAYS run this before choosing a pattern -- discover
                         what tags actually exist rather than guessing a regex.
  --pattern "<regex>"    Count word-tokens whose text matches the regex.
                         e.g. footing tags P1..P9:  --pattern "^P[0-9]+$"
                              receptacles:          --pattern "^RECEP$"
                              door tags:            --pattern "^D[0-9]{2,3}$"
                              RTUs:                 --pattern "^RTU-[0-9]+$"

Coordinates are top-left origin, PDF points (1/72 inch), matching markup_pdf.py.
Rotated pages (/Rotate 90, most real sheets) need no special handling -- PyMuPDF keeps
get_text() and draw_rect() in the same space. Verified.

Usage:
    python extract_text_tags.py <file.pdf> --page 3 --list
    python extract_text_tags.py <file.pdf> --page 3 --pattern "^P[0-9]+$"
    python extract_text_tags.py <file.pdf> --pattern "^RTU-[0-9]+$"          # all pages
    python extract_text_tags.py <file.pdf> --pattern "^P[0-9]+$" \
        --exclude-rect "900,60,1224,792@1" --out matches.json
    python extract_text_tags.py <file.pdf> --pattern "^P[0-9]+$" --no-context-exclude

Requires: PyMuPDF (fitz)

Provenance: mechanism (words -> regex -> centroid) adapted from the quantity-takeoff
skill, whose content derives from Tim Fairley / Contractor OS published method. The
over-count defenses and the confidence ceiling are BLDG additions -- the source
material called this path "100% accurate", which testing disproved.
"""

import sys
import re
import json

import fitz  # PyMuPDF

# A token is dropped when any OTHER word on its own text line matches one of these.
# These are the contexts where a tag string appears as data-about-the-tag rather than
# as a tag placed on the drawing: schedules, legends, keynote lists, revision blocks.
DEFAULT_CONTEXT_EXCLUDE = [
    "SCHEDULE", "SCHED", "QTY", "QUANTITY", "TYPE", "MARK", "TAG",
    "LEGEND", "SYMBOL", "ABBREVIATION", "ABBREV",
    "KEYNOTE", "KEYNOTES", "NOTE", "NOTES", "GENERAL",
    "REVISION", "REV", "ISSUED", "TOTAL", "SUBTOTAL",
    "INDEX", "SHEET", "DRAWING", "DETAIL", "SECTION",
    "REMARKS", "DESCRIPTION", "MANUFACTURER", "MODEL",
]


def get_arg(name, default=None):
    if name in sys.argv:
        idx = sys.argv.index(name)
        if idx + 1 < len(sys.argv):
            return sys.argv[idx + 1]
    return default


def get_all_args(name):
    """Collect every occurrence of a repeatable flag."""
    out = []
    for i, a in enumerate(sys.argv):
        if a == name and i + 1 < len(sys.argv):
            out.append(sys.argv[i + 1])
    return out


def iter_pages(doc, page_arg):
    if page_arg is None:
        for i in range(len(doc)):
            yield i
    else:
        yield int(page_arg) - 1  # 1-based -> 0-based


def words_on_page(page):
    # word tuple: (x0, y0, x1, y1, text, block_no, line_no, word_no)
    return page.get_text("words") or []


def parse_rects(specs):
    """'x0,y0,x1,y1@page' or 'x0,y0,x1,y1' (all pages). Returns [(page|None, Rect)]."""
    out = []
    for s in specs:
        page = None
        body = s
        if "@" in s:
            body, _, pg = s.rpartition("@")
            page = int(pg)
        parts = [float(p) for p in body.split(",")]
        if len(parts) != 4:
            raise ValueError(f"--exclude-rect needs 4 numbers, got: {s}")
        out.append((page, fitz.Rect(*parts)))
    return out


def line_index(words):
    """Map (block_no, line_no) -> list of uppercased word strings on that line."""
    lines = {}
    for w in words:
        key = (w[5], w[6])
        tok = w[4].strip()
        if tok:
            lines.setdefault(key, []).append(tok.upper())
    return lines


def list_tokens(doc, page_arg):
    tally = {}
    for pi in iter_pages(doc, page_arg):
        for w in words_on_page(doc[pi]):
            tok = w[4].strip()
            if not tok:
                continue
            tally[tok] = tally.get(tok, 0) + 1
    ordered = sorted(tally.items(), key=lambda kv: (-kv[1], kv[0]))
    return [{"tag": t, "count": c} for t, c in ordered]


def count_pattern(doc, page_arg, pattern, rects, context_words):
    rx = re.compile(pattern)
    matches, exclusions = [], []
    per_tag = {}

    for pi in iter_pages(doc, page_arg):
        page = doc[pi]
        words = words_on_page(page)
        lines = line_index(words)
        page_rects = [r for (p, r) in rects if p is None or p == pi + 1]

        for w in words:
            tok = w[4].strip()
            if not tok or not rx.match(tok):
                continue

            x0, y0, x1, y1 = w[0], w[1], w[2], w[3]
            cx, cy = round((x0 + x1) / 2, 2), round((y0 + y1) / 2, 2)
            rec = {
                "page": pi + 1,
                "tag": tok,
                "x": cx,
                "y": cy,
                "bbox": [round(x0, 2), round(y0, 2), round(x1, 2), round(y1, 2)],
            }

            # Defense 2: explicit rectangles.
            hit_rect = next((r for r in page_rects
                             if r.contains(fitz.Point(cx, cy))), None)
            if hit_rect is not None:
                rec["excluded_by"] = "rect"
                rec["reason"] = ("inside excluded rect "
                                 f"{tuple(round(v, 1) for v in hit_rect)}")
                exclusions.append(rec)
                continue

            # Defense 1: same-line context keywords.
            if context_words:
                siblings = [s for s in lines.get((w[5], w[6]), [])
                            if s != tok.upper()]
                trigger = next((s for s in siblings
                                if any(kw in s for kw in context_words)), None)
                if trigger is not None:
                    rec["excluded_by"] = "context"
                    rec["reason"] = (f"same text line contains '{trigger}' -- looks "
                                     "like a schedule/legend/keynote row, not a tag "
                                     "placed on the drawing")
                    exclusions.append(rec)
                    continue

            matches.append(rec)
            per_tag[tok] = per_tag.get(tok, 0) + 1

    return matches, per_tag, exclusions


def main():
    page_arg = get_arg("--page")
    pattern = get_arg("--pattern")
    out = get_arg("--out")
    rect_specs = get_all_args("--exclude-rect")

    flag_values = set(filter(None, [page_arg, pattern, out] + rect_specs
                             + [get_arg("--context-exclude")]))
    files = [a for a in sys.argv[1:]
             if not a.startswith("--") and a not in flag_values]
    if not files:
        print(__doc__)
        sys.exit(1)
    path = files[0]

    if "--no-context-exclude" in sys.argv:
        context_words = []
    else:
        extra = get_arg("--context-exclude")
        context_words = ([w.strip().upper() for w in extra.split(",") if w.strip()]
                         if extra else list(DEFAULT_CONTEXT_EXCLUDE))

    try:
        rects = parse_rects(rect_specs)
    except ValueError as e:
        print(f"ERROR: {e}")
        sys.exit(2)

    doc = fitz.open(path)

    if "--list" in sys.argv:
        result = {"file": path, "mode": "list",
                  "tokens": list_tokens(doc, page_arg)}
    elif pattern:
        matches, per_tag, exclusions = count_pattern(
            doc, page_arg, pattern, rects, context_words)
        result = {
            "file": path,
            "mode": "count",
            "pattern": pattern,
            "total": len(matches),
            "per_tag": [{"tag": t, "count": c} for t, c in
                        sorted(per_tag.items(), key=lambda kv: (-kv[1], kv[0]))],
            "matches": matches,
            "excluded_count": len(exclusions),
            "exclusions": exclusions,
            "filters": {
                "context_exclude": context_words,
                "exclude_rects": [{"page": p, "rect": [round(v, 1) for v in r]}
                                  for (p, r) in rects],
            },
            # Consumed downstream by the quantity workbook builder. Do not strip.
            "verification_required": True,
            "confidence_ceiling": "MEDIUM",
            "confidence_note": (
                "A raw text-layer tag count is MEDIUM confidence at best. Promote to "
                "HIGH only after reconciling against the sheet's own schedule "
                "row-count OR reviewing a markup_pdf.py overlay. If schedule and count "
                "disagree, that is a discrepancy to flag -- never silently reconcile."
            ),
        }
    else:
        print("Provide either --list or --pattern \"<regex>\".")
        print(__doc__)
        sys.exit(1)

    doc.close()
    payload = json.dumps(result, indent=2, ensure_ascii=True)

    if out:
        with open(out, "w", encoding="utf-8") as f:
            f.write(payload)
        if result.get("mode") == "count":
            print(f"{result['total']} matches for /{pattern}/ "
                  f"({result['excluded_count']} excluded) -> {out}")
            print("  MEDIUM confidence until reconciled against a schedule "
                  "or markup review.")
        else:
            print(f"{len(result['tokens'])} distinct tokens -> {out}")
    else:
        print(payload)


if __name__ == "__main__":
    main()
