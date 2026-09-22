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
import re
from collections import Counter, defaultdict

# Every element must carry these. Missing any one is a hard error.
REQUIRED_ELEMENT_FIELDS = ["element", "trade", "csi_subdivision", "source_sheets"]

# Recommended but not fatal.
OPTIONAL_ELEMENT_FIELDS = [
    "category", "location", "specifications", "quantities",
    "notes", "related_elements", "confidence", "unverified",
]

SCHEMA_VERSION = "1.0"


# ---------------------------------------------------------------------------
# WHAT A SHEET IS CALLED, AND WHAT A CITATION TO ONE MEANS
# ---------------------------------------------------------------------------
#
# A drawing refers to its own sheets the way a person writes them. S-001.00
# says "SEE S-100 FOR GENERAL NOTES" and "REINFORCE METAL DECK PER DETAIL
# 3/S-100", while the title block on that sheet prints S-100.00. Matching a
# citation against the printed number rejects every one of those, and the
# error blames the citation, which was transcribed exactly as the drawing
# prints it.
#
# This is a PORT. The rule lives in connie's lib/sheet-identity.ts and the
# functions below mirror it name for name: split_sheet_number is
# splitSheetNumber, subdivided_bases is subdividedBases, sheet_identity is
# resolveSheetIdentity, parse_citation is parseCitation, resolve_citation is
# resolveCitation. Keep them in step. Two rules about what a sheet is called
# is two rules to drift, and the drift is what this fixes: before it, the
# skill refused on the printed number while the module resolved on identity,
# each consistently, with the real drawings sitting between them.
#
# Nothing here infers meaning from the shape of a suffix. ".01" is a revision
# on one set and a subdivided sheet on another, and the difference is visible
# without reading a drawing: a set that subdivides A-101 into A-101.01 and
# A-101.02 SHIPS BOTH, so its own sheet list settles it.


def split_sheet_number(printed):
    """Mirror of splitSheetNumber. -> (base, suffix or None)."""
    m = re.match(r"^(.*?)\.(\d{1,2})$", (printed or "").strip())
    return (m.group(1), m.group(2)) if m else ((printed or "").strip(), None)


def subdivided_bases(printed_numbers):
    """Mirror of subdividedBases: bases this set lists more than one sheet under."""
    counts = Counter(split_sheet_number(n)[0] for n in printed_numbers if n)
    return {base for base, n in counts.items() if n > 1}


def sheet_identity(printed, subdivided):
    """
    Mirror of resolveSheetIdentity with roster=None.

    index.json carries no drawing index, so nothing here vouches for what the
    set calls its sheets, which is the roster=None branch in connie: a
    suffixed sheet whose base is not subdivided IS its base. Where connie
    reads a published index it can instead keep the printed number, and that
    never changes whether a citation resolves, only which string comes back,
    because the base step below catches the same sheet either way.
    """
    base, suffix = split_sheet_number(printed)
    if base in subdivided:
        # Decisive, and checked first: the suffix names a sheet here, not an issue.
        return printed
    if suffix is None:
        return printed
    return base


def parse_citation(source):
    """Mirror of parseCitation. "3/S-100" -> ("S-100", "3"). -> (sheet_number, detail)."""
    trimmed = (source or "").strip()
    slash = trimmed.find("/")
    if slash == -1:
        return trimmed, None
    return trimmed[slash + 1:].strip(), (trimmed[:slash].strip() or None)


def resolve_citation(source, sheets, subdivided):
    """
    Mirror of resolveCitation. Three steps, in order, and the order is the point.

    Returns (printed_sheet, None) when the citation names a sheet in the set,
    or (None, reason) when it does not. The sheet comes back as the number the
    title block prints, because that is the key sheets[] is written in.

    1. The printed number, exactly, so a set with no suffixes takes the path
       it always took. That is what keeps an unsuffixed set provably unchanged.
    2. The identity, which is the fix: S-100.00 IS S-100, so a citation naming
       S-100 has named that sheet.
    3. The base, for the other direction: a citation to S-001.01 in a set that
       ships S-001.00. One sheet under the base means the citation named it.
       Several means it named none of them, and that refusal is deliberate. A
       citation pointed at whichever sheet was listed first is invented
       provenance, which is the one thing this index exists to make impossible.
    """
    sheet_number, _detail = parse_citation(source)
    if not sheet_number:
        return None, "names sheet (blank), which is not in the set"

    for s in sheets:
        if s == sheet_number:
            return s, None

    for s in sheets:
        if sheet_identity(s, subdivided) == sheet_number:
            return s, None

    base = split_sheet_number(sheet_number)[0]
    ambiguous = (f"the set ships more than one sheet numbered {base}.NN, "
                 f"so {sheet_number} names none of them in particular")
    if base in subdivided:
        return None, ambiguous

    under_base = [s for s in sheets if split_sheet_number(s)[0] == base]
    identities = {sheet_identity(s, subdivided) for s in under_base}
    if len(identities) == 1:
        return under_base[0], None
    if len(identities) > 1:
        return None, ambiguous

    return None, f"names sheet {sheet_number}, which is not in the set"


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

    # An ordered list, not a set: resolve_citation tries the printed number
    # first and the set's own sheet list is what settles an ambiguous base.
    sheet_numbers = [s.get("sheet_number") for s in index.get("sheets", [])
                     if s.get("sheet_number")]
    subdivided = subdivided_bases(sheet_numbers)
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

        # Citations must resolve to a real sheet, against what the set decides
        # a sheet is called rather than against what one title block prints.
        for ref in el.get("source_sheets", []) or []:
            if not sheet_numbers:
                continue
            sheet, reason = resolve_citation(ref, sheet_numbers, subdivided)
            if sheet is None:
                errors.append(f"[{label}] source_sheets ref '{ref}' {reason}")

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

    # Coverage is counted against the sheet a citation RESOLVES to, so a sheet
    # printed S-100.00 and cited as S-100 counts as cited. Matching the printed
    # number undercounts twice over: it reports S-100 as cited-but-absent and
    # S-100.00 as cited by nobody, from the same citation.
    sheet_list = [s.get("sheet_number") for s in index.get("sheets", [])
                  if s.get("sheet_number")]
    subdivided = subdivided_bases(sheet_list)
    all_sheets = set(sheet_list)
    referenced, unresolved_refs = set(), set()
    for el in elements:
        for ref in el.get("source_sheets", []) or []:
            sheet, _reason = resolve_citation(ref, sheet_list, subdivided)
            if sheet is None:
                unresolved_refs.add(ref.strip())
            else:
                referenced.add(sheet)
    orphans = sorted(all_sheets - referenced)
    # A citation that resolves to no sheet is a validation error, not content.
    bogus = sorted(unresolved_refs)

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
              f"-- named by an element but resolving to no one sheet; run --validate")
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
