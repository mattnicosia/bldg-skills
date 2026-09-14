"""
build_index.py -- Element-keyed index skeleton + validator for a drawing set.

## Why element-keyed and not sheet-keyed

A drawing set is organized for humans flipping pages: a site plan here, a section three
sheets later, the equipment schedule at the back. Nothing you actually want to ask about
lives on one sheet. "What's the concrete scope" spans a plan, a section, a schedule, and
a general note.

So this index is keyed by ELEMENT -- the physical thing being built -- with every sheet
that describes it attached to it. That inverts the set into the shape the questions
arrive in. A scope of work is organized by CSI subdivision (i.e. by element and trade),
so an element-keyed index maps one-to-one onto SOW output instead of needing a re-pivot
on every run.

Borrowed from IFC/BIM, where this is exactly how a model is structured. If a real BIM
model exists for the project, use it and skip this whole pipeline.

## What this script does and does not do

DOES:  build the skeleton from sheets.json, validate a finished index, report stats.
DOES NOT: decide what the elements are. That is judgment -- grouping "SLAB ON GRADE"
          across a plan, a section note, and a schedule row is reading comprehension,
          not string processing. The agent fills elements[]; this script checks the work.

Modes:
    --skeleton   Build index.json scaffolding from a sheets.json manifest.
    --validate   Check a finished index.json. Non-zero exit on hard errors.
    --stats      Coverage summary: sheets represented, elements per trade, citation rate.

Usage:
    python build_index.py drawings/sheets.json --skeleton --out drawings/index.json
    python build_index.py drawings/index.json --validate
    python build_index.py drawings/index.json --stats

Requires: stdlib only.
"""

import sys
import json
import os
from collections import Counter, defaultdict

# Every element must carry these. Missing any one is a hard error.
REQUIRED_ELEMENT_FIELDS = ["element", "trade", "csi_subdivision", "source_sheets"]

# Recommended but not fatal.
OPTIONAL_ELEMENT_FIELDS = [
    "category", "location", "specifications", "quantities",
    "notes", "related_elements", "confidence", "unverified",
]

SCHEMA_VERSION = "1.0"


def get_arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_skeleton(manifest):
    sheets = manifest.get("sheets", [])
    return {
        "schema_version": SCHEMA_VERSION,
        "project": {
            "name": "TODO -- from cover-sheet titleblock; never 'Untitled'",
            "address": "TODO",
            "revision": "TODO -- revision number + date from titleblock",
        },
        "extraction": {
            "sheet_count": len(sheets),
            "vector_sheets": sum(1 for s in sheets if s.get("text_layer") == "vector"),
            "sparse_sheets": sum(1 for s in sheets if s.get("text_layer") == "sparse"),
            "image_only_sheets": sum(1 for s in sheets
                                     if s.get("text_layer") == "image_only"),
            "vision_pass_required": [s["sheet_number"] for s in sheets
                                     if s.get("needs_vision")],
            "unnamed_sheets": [s["sheet_number"] for s in sheets
                               if not s.get("sheet_number_found", True)],
        },
        # Mirror of sheets.json so the index is self-contained for consumers.
        "sheets": [{
            "sheet_number": s.get("sheet_number"),
            "discipline": s.get("discipline"),
            "text_layer": s.get("text_layer"),
            "needs_vision": s.get("needs_vision"),
            "title": None,          # agent fills from the sheet
            "summary": None,        # one line: what is on this sheet
        } for s in sheets],
        # The payload. One entry per physical thing being built.
        "elements": [],
        "_element_template": {
            "element": "Slab On Grade",
            "category": "Substructure",
            "trade": "Concrete",
            "csi_subdivision": "03 30 00",
            "location": "Ground floor, entire footprint",
            "source_sheets": ["S-101", "5/S-301"],
            "specifications": [
                {"value": "4000 PSI", "source": "S-101 general note 3"},
                {"value": "6 mil vapor barrier", "source": "5/S-301"}
            ],
            "quantities": [
                {"value": None, "unit": "SF", "basis": "not stated on drawings",
                 "confidence": "NOT_MEASURED"}
            ],
            "notes": ["Verify topping material -- not called out"],
            "related_elements": ["Perimeter Grade Beam"],
            "confidence": "HIGH",
            "unverified": False,
        },
        "open_items": [],   # RFI candidates, unreadable content, contradictions
    }


def validate(index):
    errors, warnings = [], []

    if index.get("schema_version") != SCHEMA_VERSION:
        warnings.append(f"schema_version is {index.get('schema_version')!r}, "
                        f"expected {SCHEMA_VERSION!r}")

    proj = index.get("project") or {}
    name = (proj.get("name") or "").strip()
    if not name or name.lower().startswith("todo") or name.lower() in (
            "untitled", "untitled project"):
        errors.append("project.name is missing or a placeholder "
                      "(Untitled/TODO is a QA failure -- resolve the real name)")

    sheet_numbers = {s.get("sheet_number") for s in index.get("sheets", [])}
    if not sheet_numbers:
        errors.append("index has no sheets[]")

    elements = index.get("elements", [])
    if not elements:
        errors.append("index has no elements[] -- the skeleton was never filled in")

    seen = Counter()
    for i, el in enumerate(elements):
        label = el.get("element") or f"<element index {i}>"
        for field in REQUIRED_ELEMENT_FIELDS:
            if not el.get(field):
                errors.append(f"[{label}] missing required field '{field}'")

        seen[(el.get("element"), el.get("csi_subdivision"))] += 1

        # Citations must resolve to a real sheet. "5/S-301" -> "S-301".
        for ref in el.get("source_sheets", []) or []:
            base = ref.split("/")[-1].strip()
            if sheet_numbers and base not in sheet_numbers:
                errors.append(f"[{label}] source_sheets ref '{ref}' does not resolve "
                              f"to any sheet in the set")

        for spec in el.get("specifications", []) or []:
            if not spec.get("source"):
                errors.append(f"[{label}] specification {spec.get('value')!r} has no "
                              f"source citation")

        # A stated quantity with no basis is the exact failure this index exists to stop.
        for q in el.get("quantities", []) or []:
            if q.get("value") is not None and not q.get("basis"):
                errors.append(f"[{label}] quantity {q.get('value')} has no 'basis' -- "
                              f"an uncited quantity is a hallucination risk")
            if q.get("value") is not None and not q.get("confidence"):
                warnings.append(f"[{label}] quantity {q.get('value')} has no "
                                f"'confidence' tier")

        if not el.get("location"):
            warnings.append(f"[{label}] no 'location' -- hard to scope without it")

    for key, n in seen.items():
        if n > 1:
            warnings.append(f"duplicate element {key[0]!r} in {key[1]!r} "
                            f"appears {n} times -- merge or differentiate")

    pending = index.get("extraction", {}).get("vision_pass_required") or []
    if pending:
        warnings.append(f"{len(pending)} sheet(s) flagged needs_vision: "
                        f"{', '.join(pending[:8])}"
                        f"{' ...' if len(pending) > 8 else ''} -- confirm the vision "
                        f"pass ran before trusting coverage")

    return errors, warnings


def stats(index):
    elements = index.get("elements", [])
    by_trade = Counter(el.get("trade") or "Unknown" for el in elements)
    by_conf = Counter(el.get("confidence") or "UNSET" for el in elements)

    cited = sum(1 for el in elements if el.get("source_sheets"))
    specs_total = sum(len(el.get("specifications") or []) for el in elements)
    specs_cited = sum(1 for el in elements
                      for s in (el.get("specifications") or []) if s.get("source"))

    referenced = set()
    for el in elements:
        for ref in el.get("source_sheets", []) or []:
            referenced.add(ref.split("/")[-1].strip())
    all_sheets = {s.get("sheet_number") for s in index.get("sheets", [])}
    orphans = sorted(all_sheets - referenced)
    # Only refs that resolve to a real sheet count as coverage; a citation to a
    # sheet that isn't in the set is a validation error, not represented content.
    bogus = sorted(referenced - all_sheets)
    referenced &= all_sheets

    print(f"elements: {len(elements)}")
    print(f"citation rate: {cited}/{len(elements)} elements have source_sheets")
    print(f"spec citation rate: {specs_cited}/{specs_total} specs carry a source")
    print("\nby trade:")
    for t, n in by_trade.most_common():
        print(f"  {n:4d}  {t}")
    print("\nby confidence:")
    for c, n in by_conf.most_common():
        print(f"  {n:4d}  {c}")
    print(f"\nsheets represented: {len(referenced)}/{len(all_sheets)}")
    if bogus:
        print(f"UNRESOLVED refs ({len(bogus)}): {', '.join(bogus)} "
              f"-- cited but not in the set; run --validate")
    if orphans:
        print(f"sheets NOT referenced by any element ({len(orphans)}): "
              f"{', '.join(orphans[:15])}{' ...' if len(orphans) > 15 else ''}")
        print("  -> either genuinely no scope on them, or the extraction missed content.")
    unresolved = index.get("open_items") or []
    print(f"\nopen items / RFI candidates: {len(unresolved)}")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out = get_arg("--out")
    args = [a for a in args if a != out]
    if not args:
        print(__doc__)
        sys.exit(1)
    path = args[0]

    if not os.path.exists(path):
        print(f"ERROR: not found: {path}")
        sys.exit(2)
    data = load(path)

    if "--skeleton" in sys.argv:
        skel = build_skeleton(data)
        target = out or "index.json"
        with open(target, "w", encoding="utf-8") as f:
            json.dump(skel, f, indent=2, ensure_ascii=True)
        n = skel["extraction"]["sheet_count"]
        vp = len(skel["extraction"]["vision_pass_required"])
        print(f"skeleton for {n} sheets -> {target}")
        print(f"  {vp} sheet(s) need a vision pass")
        print("  NEXT: fill sheets[].title/summary and elements[] "
              "(see _element_template), then re-run with --validate")
        return

    if "--validate" in sys.argv:
        errors, warnings = validate(data)
        for w in warnings:
            print(f"WARN  {w}")
        for e in errors:
            print(f"ERROR {e}")
        print(f"\n{len(errors)} error(s), {len(warnings)} warning(s)")
        if errors:
            print("Index is NOT ready to generate from. Fix errors first.")
            sys.exit(1)
        print("Index passed validation.")
        return

    if "--stats" in sys.argv:
        stats(data)
        return

    print(__doc__)
    sys.exit(1)


if __name__ == "__main__":
    main()
