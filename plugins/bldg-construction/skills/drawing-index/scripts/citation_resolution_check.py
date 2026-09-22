"""
citation_resolution_check.py -- the citation rule, exercised.

Run:  python3 citation_resolution_check.py

This guards a rule that is a PORT. resolve_citation in build_index.py mirrors
resolveCitation in connie's lib/sheet-identity.ts, and the two halves of the
pipeline have already drifted apart once: the skill refused a citation on the
printed number while the module resolved it on identity, each consistently,
with the real drawings sitting between them. On job 260120 that produced 22
hard errors on citations transcribed exactly as the drawings print them.

The cases below are the ones from connie's scripts/citation-resolution-check.ts,
plus the three real sheet lists from job 260120.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build_index import (  # noqa: E402
    parse_citation,
    resolve_citation,
    split_sheet_number,
    subdivided_bases,
    sheet_identity,
    validate,
)

failed = 0


def check(name, got, want):
    global failed
    if got != want:
        failed += 1
        print(f"FAIL  {name}\n        got:  {got!r}\n        want: {want!r}")
    else:
        print(f"ok    {name}")


def resolve(cite, sheets):
    return resolve_citation(cite, sheets, subdivided_bases(sheets))


# --- parse_citation, matching connie's parts() cases ---------------------
check("a detail and a sheet split apart", parse_citation("3/S-100"), ("S-100", "3"))
check("a bare sheet carries no detail", parse_citation("S-100"), ("S-100", None))
check("surrounding space is not part of either", parse_citation(" 3 / S-100 "), ("S-100", "3"))
check("an empty reference names no sheet and says so",
      resolve("", ["E-200"])[1], "names sheet (blank), which is not in the set")

# --- a set with no suffixes behaves exactly as it always did -------------
PLAIN = ["A-105", "E-200", "M-301", "P-100"]
check("an unsuffixed citation still resolves", resolve("E-200", PLAIN), ("E-200", None))
check("as does one naming a details sheet", resolve("M-301", PLAIN), ("M-301", None))
check("and one carrying a detail number", resolve("5/A-105", PLAIN), ("A-105", None))
check("an absent sheet still hard-fails, and names the sheet",
      resolve("1/X-100", PLAIN)[1], "names sheet X-100, which is not in the set")

# --- the fix: a citation written the way the drawings print it -----------
SUFFIXED = ["S-100.00", "A-105.00", "E-200"]
check("a citation to the base resolves to the suffixed sheet",
      resolve("S-100", SUFFIXED), ("S-100.00", None))
check("carrying its detail number changes nothing",
      resolve("3/S-100", SUFFIXED), ("S-100.00", None))
check("the printed number itself still resolves, first and exactly",
      resolve("S-100.00", SUFFIXED), ("S-100.00", None))
check("an unsuffixed sheet in a mixed set is untouched",
      resolve("E-200", SUFFIXED), ("E-200", None))

# --- and the other direction: cite .01 where the set ships .00 -----------
check("a citation to one revision finds the one the set ships",
      resolve("S-001.01", ["S-001.00"]), ("S-001.00", None))

# --- a genuinely ambiguous base is refused, never guessed ----------------
SUBDIV = ["A-101.01", "A-101.02", "A-101.03"]
check("a bare base naming a subdivided series resolves to nothing",
      resolve("A-101", SUBDIV)[0], None)
check("and says why, rather than picking the first",
      resolve("A-101", SUBDIV)[1],
      "the set ships more than one sheet numbered A-101.NN, "
      "so A-101 names none of them in particular")
check("while a citation to one of them exactly still resolves",
      resolve("A-101.02", SUBDIV), ("A-101.02", None))
check("a subdivided sheet keeps its printed number as its identity",
      sheet_identity("A-101.01", subdivided_bases(SUBDIV)), "A-101.01")
check("where a revised one takes its base",
      sheet_identity("S-100.00", subdivided_bases(SUFFIXED)), "S-100")

# --- split_sheet_number ---------------------------------------------------
check("a two-digit suffix splits off", split_sheet_number("S-001.00"), ("S-001", "00"))
check("a sheet with no suffix is its own base", split_sheet_number("E-200"), ("E-200", None))
check("a three-digit tail is not a suffix",
      split_sheet_number("A-101.123"), ("A-101.123", None))

# --- the claim made in sheet_identity's docstring, asserted --------------
# "identity never changes WHETHER a citation resolves, only which string
# comes back, because the base step catches the same sheet either way."
def resolve_without_identity_step(cite, sheets):
    subdivided = subdivided_bases(sheets)
    sheet_number, _ = parse_citation(cite)
    if not sheet_number:
        return None
    for s in sheets:
        if s == sheet_number:
            return s
    base = split_sheet_number(sheet_number)[0]
    if base in subdivided:
        return None
    under = [s for s in sheets if split_sheet_number(s)[0] == base]
    return under[0] if len(under) == 1 else None


equivalent = True
for sheets in (PLAIN, SUFFIXED, SUBDIV, ["S-001.00", "S-001.01", "S-100.00"]):
    probes = list(sheets) + [split_sheet_number(s)[0] for s in sheets] + ["X-100", "A-101", ""]
    for cite in probes:
        if resolve(cite, sheets)[0] != resolve_without_identity_step(cite, sheets):
            equivalent = False
            print(f"        diverged: {cite!r} against {sheets}")
check("the identity step never changes an outcome while no roster is read", equivalent, True)

# --- the three real sheet lists from job 260120 --------------------------
ADDENDUM = ["A-001", "A-100", "A-101", "A-102", "A-103", "A-104", "A-105", "A-401",
            "E-200", "E-300", "FA-200", "M-200", "M-300", "M-301", "P-100", "P-200",
            "P-300", "S-001.01", "SP-200", "T-001"]
SUPERCEDED = ["A-001", "A-100", "A-105", "E-100", "E-200", "M-100", "P-100",
              "S-001.00", "S-100.00", "T-001"]
COMBINED = SUPERCEDED + ["S-001.01"]

check("on the addendum set, the drawings' own 'S-001' resolves",
      resolve("S-001", ADDENDUM), ("S-001.01", None))
check("on the superseded set, the same citation finds that issue's sheet",
      resolve("S-001", SUPERCEDED), ("S-001.00", None))
check("and 'DETAIL 3/S-100', which S-001.00 actually prints, resolves",
      resolve("3/S-100", SUPERCEDED), ("S-100.00", None))
# The working folder flattens both issues into one sheet list, so it really
# does ship two sheets under S-001 and a bare citation names neither.
check("on the combined set, a bare 'S-001' is ambiguous and refused",
      resolve("S-001", COMBINED)[0], None)
check("while 'S-100' still resolves there",
      resolve("S-100", COMBINED), ("S-100.00", None))

# --- validate() end to end ------------------------------------------------
def index_with(sheets, refs):
    return {
        "schema_version": "1.0",
        "project": {"name": "Adjuvant Health"},
        "sheets": [{"sheet_number": s} for s in sheets],
        "elements": [{
            "element": "Metal Deck", "trade": "Structural Steel",
            "csi_subdivision": "05 31 00", "location": "Roof",
            "source_sheets": refs,
        }],
    }


errs, _ = validate(index_with(["S-100.00", "E-200"], ["S-100", "3/S-100", "E-200"]))
check("validate() passes citations written as the drawings print them", errs, [])

errs, _ = validate(index_with(["S-100.00"], ["1/X-100"]))
check("validate() still hard-fails an absent sheet, and names it", len(errs), 1)
check("with the sheet in the message", "X-100" in errs[0], True)

errs, _ = validate(index_with(["A-101.01", "A-101.02"], ["A-101"]))
check("validate() refuses an ambiguous base rather than picking one", len(errs), 1)

print(f"\n{failed} FAILED" if failed else "\nAll citation-resolution checks passed.")
sys.exit(1 if failed else 0)
