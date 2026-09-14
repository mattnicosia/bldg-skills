"""
build_quantity_xlsx.py -- Conceptual quantity estimate workbook generator.

Reads quantity_data.json and writes a Calibri-throughout workbook:

  Sheet 1: READ FIRST      -- MANDATORY disclaimer + plain-language confidence tiers.
                              First sheet a user sees. Never removed, never softened.
  Sheet 2: Quantities      -- by CSI subdivision; Item | Qty | Unit | Type | Method |
                              Confidence | Source | Derivation/Notes.
  Sheet 3: Review Flags    -- every sanity-check failure and every LOW/NOT_MEASURED line.

This workbook is a conceptual planning aid, NOT a bid document. It is deliberately a
separate file from the SOW so that AI-derived quantities can never contaminate a scope
document, which is guaranteed quantity-free by design.

Usage:
    python build_quantity_xlsx.py quantity_data.json output.xlsx

Requires: openpyxl
"""

import json
import sys

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Structural palette -- black / gray / white, matching the SOW workbook.
WHITE = "FFFFFF"
BLACK = "000000"
DARK_GRAY = "3A3A3A"
MEDIUM_GRAY = "7A7A7A"
LIGHT_GRAY = "D8D8D8"
WHISPER_GRAY = "F2F2F2"

# Confidence chips are the ONE deliberate exception to the black/gray/white rule.
# On an internal risk document, fast visual scanning of what is trustworthy beats
# palette purity -- and these are the same three colors the SOW comparison workbook
# already uses for ADDED / MODIFIED / REMOVED, so the visual language is consistent
# across every workbook this skill family produces.
GREEN_FILL, GREEN_TEXT = "D6F0D6", "1E6B1E"
AMBER_FILL, AMBER_TEXT = "FFF0C8", "7A5200"
RED_FILL, RED_TEXT = "FFD6D6", "8B0000"

CONF_FILL = {
    "VERIFIED": GREEN_FILL,      # human takeoff export -- outranks everything
    "HIGH": GREEN_FILL,
    "MEDIUM": AMBER_FILL,
    "ESTIMATED": AMBER_FILL,     # ratio-based: a caveat tier, not a "wrong" tier
    "LOW": RED_FILL,
    "NOT_MEASURED": RED_FILL,
}
CONF_TEXT = {
    "VERIFIED": GREEN_TEXT,
    "HIGH": GREEN_TEXT,
    "MEDIUM": AMBER_TEXT,
    "ESTIMATED": AMBER_TEXT,
    "LOW": RED_TEXT,
    "NOT_MEASURED": RED_TEXT,
}

# Plain-language tier explanations. Rendered on READ FIRST. Do not abbreviate these
# into jargon -- the whole point is that a reader who is not an estimator understands
# which numbers they may act on.
TIER_TEXT = [
    ("VERIFIED", "Measured by a human in takeoff software and exported. "
                 "Trustworthy. This is the only tier suitable for pricing."),
    ("HIGH", "Explicitly stated on the drawings, or lifted from a schedule, or a tag "
             "count that was reconciled against a schedule or a marked-up drawing. "
             "Reliable for budgeting."),
    ("MEDIUM", "A raw tag count that has NOT been reconciled, or a number derived from "
               "a reliable figure using an assumed ratio. Directionally useful. Verify "
               "before acting on it."),
    ("LOW", "Counted visually, or measured off a scaled drawing. Treat as a rough "
            "indicator only. Must be verified by hand."),
    ("ESTIMATED", "Calculated from a square-foot ratio, not read off the drawings at "
                  "all. For order-of-magnitude context only."),
    ("NOT_MEASURED", "Could not be determined from the drawings. Needs a human takeoff. "
                     "This is the honest answer for most linear runs of duct and pipe."),
]

DISCLAIMER = [
    "This workbook was produced by AI from PDF construction drawings.",
    "It has NOT been reviewed by a licensed estimator against original CAD files "
    "or a field walk.",
    "",
    "USE FOR: conceptual budgeting, go / no-go decisions, feasibility, and as an "
    "independent second check on a takeoff already done by hand.",
    "",
    "DO NOT USE FOR: lump-sum bid pricing, subcontract execution, or purchasing "
    "decisions -- not without independent human verification of every line.",
    "",
    "On a hard-dollar lump-sum job the quantities decide whether the project makes or "
    "loses money. Spend the hours verifying by hand. This workbook accelerates and "
    "cross-checks that work; it does not replace it.",
]


def f(size=10, bold=False, italic=False, color=BLACK, name="Calibri"):
    return Font(name=name, size=size, bold=bold, italic=italic, color=color)


def fill(color):
    return PatternFill("solid", fgColor=color)


def align(h="left", v="center", wrap=True):
    return Alignment(horizontal=h, vertical=v, wrap_text=wrap)


def bottom(weight="thin", color=LIGHT_GRAY):
    return Border(bottom=Side(style=weight, color=color))


def build_cover(wb, data):
    """READ FIRST. The disclaimer is the point of this sheet -- prominent, not buried."""
    ws = wb.create_sheet("READ FIRST")
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 4
    ws.column_dimensions["B"].width = 22
    ws.column_dimensions["C"].width = 96

    ws["B2"] = "READ FIRST"
    ws["B2"].font = f(11, bold=True, color=RED_TEXT)

    name = (data.get("project_name") or "").strip()
    if not name or name.lower() in ("untitled", "untitled project"):
        raise SystemExit("ERROR: project_name is missing or a placeholder. "
                         "Resolve the real project name before building the workbook.")
    ws["B4"] = name
    ws["B4"].font = f(26, bold=True, color=BLACK)
    ws.merge_cells("B4:C4")
    ws.row_dimensions[4].height = 36

    ws["B5"] = data.get("project_address", "")
    ws["B5"].font = f(12, color=MEDIUM_GRAY)
    ws.merge_cells("B5:C5")

    ws["B6"] = "CONCEPTUAL QUANTITY ESTIMATE -- NOT A BID DOCUMENT"
    ws["B6"].font = f(12, bold=True, color=RED_TEXT)
    ws["B6"].fill = fill(RED_FILL)
    ws["C6"].fill = fill(RED_FILL)
    ws.merge_cells("B6:C6")
    ws.row_dimensions[6].height = 22

    r = 8
    for line in DISCLAIMER:
        if line:
            c = ws.cell(r, 2, line)
            c.font = f(10, bold=line.startswith(("USE FOR", "DO NOT USE")), color=BLACK)
            c.alignment = align(wrap=True)
            ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=3)
            ws.row_dimensions[r].height = 15 + 13 * (len(line) // 110)
        r += 1

    r += 1
    ws.cell(r, 2, "PROJECT").font = f(12, bold=True, color=WHITE)
    for col in (2, 3):
        ws.cell(r, col).fill = fill(DARK_GRAY)
    r += 1
    for label, val in [
        ("Trade", data.get("trade", "")),
        ("Prepared by", data.get("prepared_by", "")),
        ("Date", data.get("date_prepared", "")),
        ("Units", data.get("units_system", "imperial")),
        ("Drawing text layer", data.get("pdf_type_summary", "")),
        ("Index source", data.get("index_source", "")),
        ("Takeoff export used", data.get("takeoff_export") or "NONE -- no verified quantities"),
    ]:
        ws.cell(r, 2, label).font = f(10, bold=True, color=MEDIUM_GRAY)
        c = ws.cell(r, 3, str(val))
        c.font = f(11, color=BLACK)
        c.alignment = align()
        r += 1

    s = data.get("summary", {})
    r += 1
    ws.cell(r, 2, "CONFIDENCE BREAKDOWN").font = f(12, bold=True, color=WHITE)
    for col in (2, 3):
        ws.cell(r, col).fill = fill(DARK_GRAY)
    r += 1
    ws.cell(r, 2, "Total line items").font = f(10, color=BLACK)
    ws.cell(r, 3, str(s.get("total_items", ""))).font = f(10, bold=True, color=BLACK)
    r += 1
    for tier, _ in TIER_TEXT:
        n = s.get(tier.lower())
        if n in (None, ""):
            continue
        tc = ws.cell(r, 2, tier)
        tc.font = f(10, bold=True, color=CONF_TEXT.get(tier, BLACK))
        tc.fill = fill(CONF_FILL.get(tier, WHISPER_GRAY))
        tc.alignment = align(h="center")
        ws.cell(r, 3, str(n)).font = f(10, bold=True, color=BLACK)
        r += 1
    ws.cell(r, 2, "Review flags").font = f(10, color=BLACK)
    ws.cell(r, 3, str(s.get("flags", ""))).font = f(10, bold=True, color=BLACK)
    r += 2

    ws.cell(r, 2, "WHAT THE CONFIDENCE LABELS MEAN").font = f(12, bold=True, color=WHITE)
    for col in (2, 3):
        ws.cell(r, col).fill = fill(DARK_GRAY)
    r += 1
    for tier, meaning in TIER_TEXT:
        tc = ws.cell(r, 2, tier)
        tc.font = f(10, bold=True, color=CONF_TEXT.get(tier, BLACK))
        tc.fill = fill(CONF_FILL.get(tier, WHISPER_GRAY))
        tc.alignment = align(h="center")
        mc = ws.cell(r, 3, meaning)
        mc.font = f(10, color=BLACK)
        mc.alignment = align(wrap=True)
        ws.row_dimensions[r].height = 15 + 13 * (len(meaning) // 95)
        r += 1

    return ws


HEADERS = ["Item", "Qty", "Unit", "Type", "Method", "Confidence", "Source", "Derivation / Notes"]
WIDTHS = [34, 10, 8, 11, 24, 12, 16, 50]


def build_quantities(wb, data):
    ws = wb.create_sheet("Quantities")
    ws.sheet_view.showGridLines = False
    for i, w in enumerate(WIDTHS, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

    ws.merge_cells("A1:H1")
    ws["A1"] = f"{data.get('trade','')} -- Conceptual Quantity Estimate"
    ws["A1"].font = f(16, bold=True, color=BLACK)
    ws.row_dimensions[1].height = 28

    # Column header row
    r = 3
    for c, h in enumerate(HEADERS, start=1):
        cell = ws.cell(r, c, h)
        cell.font = f(10, bold=True, color=WHITE)
        cell.fill = fill(DARK_GRAY)
        cell.alignment = align(h="center" if h in ("Qty", "Unit", "Type", "Confidence") else "left")
    ws.freeze_panes = "A4"
    r += 1

    for sub in data.get("subdivisions", []):
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=8)
        title = f"{sub.get('code','')} - {sub.get('title','')}".strip(" -")
        cell = ws.cell(r, 1, title)
        cell.font = f(11, bold=True, color=WHITE)
        cell.fill = fill(MEDIUM_GRAY)
        cell.alignment = align()
        ws.row_dimensions[r].height = 20
        r += 1

        for idx, it in enumerate(sub.get("items", [])):
            shade = WHISPER_GRAY if idx % 2 == 0 else WHITE
            # A range stays a range. Collapsing it to a point estimate to look
            # decisive is the exact dishonesty this workbook exists to avoid.
            if it.get("qty_low") is not None or it.get("qty_high") is not None:
                qty_display = f"{it.get('qty_low','?')} - {it.get('qty_high','?')}"
            else:
                qty_display = it.get("qty", "")
            values = [
                it.get("item", ""),
                qty_display,
                it.get("unit", ""),
                it.get("type", ""),
                it.get("method", ""),
                it.get("confidence", ""),
                it.get("source", ""),
                it.get("notes", ""),
            ]
            for c, v in enumerate(values, start=1):
                cell = ws.cell(r, c, v)
                cell.font = f(10, color=BLACK)
                cell.fill = fill(shade)
                cell.border = bottom()
                if c in (2, 3, 4):
                    cell.alignment = align(h="center")
                else:
                    cell.alignment = align()
            # Confidence cell color-coded
            conf = str(it.get("confidence", "")).upper()
            cc = ws.cell(r, 6)
            if conf in CONF_FILL:
                cc.fill = fill(CONF_FILL[conf])
                cc.font = f(10, bold=True, color=CONF_TEXT[conf])
            cc.alignment = align(h="center")
            ws.row_dimensions[r].height = 30
            r += 1
        r += 1  # spacer between subdivisions

    ws.print_options.horizontalCentered = False
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    return ws


def build_flags(wb, data):
    ws = wb.create_sheet("Review Flags")
    ws.sheet_view.showGridLines = False
    cols = ["Item", "Issue", "Expected", "Actual", "Recommended Action"]
    widths = [28, 48, 22, 18, 36]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

    ws.merge_cells("A1:E1")
    ws["A1"] = "Review Flags -- verify these by hand before pricing"
    ws["A1"].font = f(14, bold=True, color=WHITE)
    ws["A1"].fill = fill(DARK_GRAY)
    ws["A1"].alignment = align()
    ws.row_dimensions[1].height = 24

    r = 2
    for c, h in enumerate(cols, start=1):
        cell = ws.cell(r, c, h)
        cell.font = f(10, bold=True, color=WHITE)
        cell.fill = fill(MEDIUM_GRAY)
        cell.alignment = align()
    r += 1

    flags = data.get("review_flags", [])
    if not flags:
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=5)
        ws.cell(r, 1, "No flags raised. (Still spot-check LOW-confidence items.)").font = \
            f(10, italic=True, color=MEDIUM_GRAY)
        return ws

    for idx, fl in enumerate(flags):
        shade = WHISPER_GRAY if idx % 2 == 0 else WHITE
        values = [fl.get("item", ""), fl.get("issue", ""), fl.get("expected", ""),
                  fl.get("actual", ""), fl.get("action", "")]
        for c, v in enumerate(values, start=1):
            cell = ws.cell(r, c, v)
            cell.font = f(10, color=BLACK)
            cell.fill = fill(shade)
            cell.border = bottom()
            cell.alignment = align()
        ws.row_dimensions[r].height = 30
        r += 1
    return ws


def main():
    if len(sys.argv) < 3:
        print("Usage: python build_quantity_xlsx.py quantity_data.json output.xlsx")
        sys.exit(1)

    with open(sys.argv[1], encoding="utf-8") as fh:
        data = json.load(fh)

    wb = Workbook()
    wb.remove(wb.active)
    build_cover(wb, data)
    build_quantities(wb, data)
    build_flags(wb, data)
    wb.save(sys.argv[2])
    print(f"Wrote {sys.argv[2]}")


if __name__ == "__main__":
    main()
