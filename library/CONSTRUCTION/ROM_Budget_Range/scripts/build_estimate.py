"""
O+D / BLDG Estimating - Budgetary Estimate Build Script

This is a working template seeded with the MacDougal Street Restaurant
project (260079). To use for a new project:

1. Edit the PROJECT METADATA block below.
2. Edit OUT path to point at the project's Bid Documents folder.
3. Edit FOH_SF, GROSS_SF.
4. Edit LINE_ITEMS, HVAC_ALT, TAKEOFF for project-specific pricing/quantities.
5. Edit the cover-letter/notes text strings throughout for project-specific
   facts (address, contact names, dates, scope language).

Run via: cat build_estimate.py | py.exe -

See ../references/workflow.md for the full playbook and
../references/pricing_logic.md for how to derive line items from a benchmark.
"""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ============================================================
# PROJECT METADATA — EDIT FOR EACH NEW PROJECT
# ============================================================
PROJECT_NUMBER = "260079"
PROJECT_SHORTNAME = "MacDougal"             # used in filename
PROJECT_FULL_TITLE = "MacDougal Street Restaurant"
PROJECT_ADDRESS = "69-71 MacDougal St, NY NY 10012"
PROJECT_OWNER_NAME = "Mosconi"              # for "Owner: <X>" line
GC_NAME = "O+D Builders"
GC_CONTACT_NAME = "Edward Tassey"           # who the email is addressed to
ARCHITECT_FIRM = "Sawicki Tarella"
EMAIL_DATE = "05/08/2026"                   # when the architect emailed the scope
SKETCH_PLAN_DATE = "04/29/2024"             # date on the sketch plans
ESTIMATE_DATE = "May 20, 2026"              # date of this estimate

VERSION = 4                                  # bump for each iteration

OUT = (
    r"C:\Users\Matt\Matt Nicosia Dropbox\BLDG\BLDG Estimating"
    rf"\{PROJECT_NUMBER} - {PROJECT_FULL_TITLE} [{GC_NAME}]"
    rf"\Bid Documents\{PROJECT_NUMBER}_{PROJECT_SHORTNAME}_Budgetary_Estimate_v{VERSION}.xlsx"
)

FONT = "Open Sans"
BLACK = "000000"
WHITE = "FFFFFF"
DARK = "1A1A1A"      # OD black bar
LIGHT_BLUE = "DCE6F1" # OD totals row highlight
GRAY_LINE = "BFBFBF"
LIGHT_GRAY = "F2F2F2" # subdivision row

thin = Side(border_style="thin", color=GRAY_LINE)
bottom_line = Side(border_style="thin", color=BLACK)
BORDER_ALL = Border(left=thin, right=thin, top=thin, bottom=thin)
BORDER_BOTTOM = Border(bottom=bottom_line)

def f_body(size=10, bold=False, color=BLACK, italic=False):
    return Font(name=FONT, size=size, bold=bold, color=color, italic=italic)

def fill(c): return PatternFill("solid", start_color=c, end_color=c)

MONEY = '"$"#,##0;("$"#,##0);"-"'
PCT = "0.00%"
NUM2 = "#,##0.00"
NUM0 = "#,##0"

# ============================================================
# DATA — pricing models (Tier A and Tier B)
# ============================================================
FOH_SF = 2138    # FOH renovation area (confirmed by Owner)
GROSS_SF = 6960  # Main level 4,000 SF + Cellar 2,960 SF

# (csi_code, description, tier_a_total, tier_b_total)
LINE_ITEMS = [
    # 01 General Requirements
    ("01 General Requirements", None, None, None, True),
    ("01.0050", "General Requirements (6-Month Build)", 200000, 215000, False),
    ("01.5400", "Scaffolding (Not Required)", 0, 0, False),
    # 02
    ("02 Existing Conditions", None, None, None, True),
    ("02.1000", "Demolition", 85000, 95000, False),
    # 03
    ("03 Concrete", None, None, None, True),
    ("03.3000", "Concrete (Floor Patching & Leveling Only - No Structural)", 10000, 14000, False),
    # 04
    ("04 Masonry", None, None, None, True),
    ("04.2000", "Masonry (Exposed Brick Repair, Repointing)", 20000, 35000, False),
    # 05
    ("05 Metals", None, None, None, True),
    ("05.5000", "Misc Metals (Banquette Frames, Railings, Soffit Hangers)", 25000, 40000, False),
    # 06
    ("06 Wood, Plastic and Composites", None, None, None, True),
    ("06.2200", "Millwork (Bar, Back Bar, Banquettes, Host, Service, Paneling)", 220000, 290000, False),
    # 07
    ("07 Thermal and Moisture Protection", None, None, None, True),
    ("07.0000", "Waterproofing, Insulation, Sealants, Firestopping", 12000, 18000, False),
    # 08
    ("08 Openings", None, None, None, True),
    ("08.1100", "Doors, Frames & HW", 25000, 40000, False),
    ("08.3000", "Eliason Door (Kitchen Pass)", 4000, 5000, False),
    ("08.8200", "Arch. Metal & Glass (Interior Storefront / Vestibule)", 10000, 25000, False),
    # 09
    ("09 Finishes", None, None, None, True),
    ("09.2300", "Drywall & Carpentry", 50000, 65000, False),
    ("09.2500", "Acoustical Ceilings & Treatment", 35000, 60000, False),
    ("09.3013", "Tile & Stone", 50000, 90000, False),
    ("09.6000", "Flooring", 60000, 90000, False),
    ("09.9100", "Painting & Specialty Wall Finishes", 35000, 65000, False),
    # 10
    ("10 Specialties", None, None, None, True),
    ("10.2600", "Wall and Door Protection", 5000, 7000, False),
    ("10.2800", "Bath Accessories (Carried in Bath Allowance)", 0, 0, False),
    # 11
    ("11 Equipment", None, None, None, True),
    ("11.4400", "Kitchen Equipment (Reuse Existing; Hood Cleaning/Cert, Gas Check)", 18000, 22000, False),
    # 12
    ("12 Furnishings", None, None, None, True),
    ("12.2000", "Window Treatments (Built-in Banquettes Carried in Millwork)", 10000, 20000, False),
    # 21
    ("21 Fire Suppression", None, None, None, True),
    ("21.0000", "Sprinkler (Heads/Drops Modification to Suit New Ceiling)", 20000, 25000, False),
    # 22
    ("22 Plumbing", None, None, None, True),
    ("22.0000", "Plumbing (Bar, Bath Rough-In, Minor Kitchen, Water Heater)", 77000, 90000, False),
    ("22.4000", "Plumbing Fixtures (Bar Fittings; Bath Fixtures in Allowance)", 12000, 18000, False),
    # 23
    ("23 Heating, Ventilating and Air-Conditioning", None, None, None, True),
    ("23.0000", "HVAC - Base: Reuse Existing Equipment + New Distribution", 135000, 155000, False),
    # 26
    ("26 Electrical", None, None, None, True),
    ("26.0000", "Electric (Distribution, Branch Wiring, Devices)", 130000, 155000, False),
    ("26.5000", "Lighting Fixtures (Allowance)", 40000, 80000, False),
    # 27
    ("27 Communications", None, None, None, True),
    ("27.1000", "Tel/Data Rough-In (Wiring & Equipment NIC)", 4000, 6000, False),
    ("27.1020", "Audio Visual Rough-In (AV Equipment NIC)", 4000, 6000, False),
    ("27.2100", "Network Equipment Rough-In (Equipment NIC)", 4000, 6000, False),
    # 28
    ("28 Safety and Security", None, None, None, True),
    ("28.4600", "Fire Alarm (Device Add/Relocate, Programming)", 22000, 25000, False),
    ("28.4610", "Security Rough-In (Equipment NIC)", 5000, 7000, False),
    # ALLOW
    ("ALLOWANCES", None, None, None, True),
    ("ALW.01", "Bathroom Allowance (2 Bathrooms @ $85K/EA)", 170000, 170000, False),
    ("ALW.02", "Cellar Refresh Allowance (Paint, LED Relamp, Minor MEP)", 12000, 18000, False),
]

# Markups (parallel, as % of direct cost)
MARKUP_GC = 0.07      # General Conditions overhead
MARKUP_FEE = 0.05     # GC Fee (profit)
MARKUP_INS = 0.03     # Insurance (GL + builder's risk)
MARKUP_CONT = 0.12    # Design contingency (sketch level)

HVAC_ALT = [
    ("23.0050", "HVAC Equipment - New RTU(s) / Split System / Condensers", 185000, 210000),
    ("23.0060", "HVAC Equipment - Demolition & Removal of Existing", 15000, 15000),
    ("23.0070", "Rigging, Curb, Structural Penetration / Patching", 40000, 45000),
    ("26.0050", "Electrical Distribution / Disconnects for New Equipment", 15000, 18000),
]

# ============================================================
# WORKBOOK BUILD
# ============================================================
wb = Workbook()

# ---------- TAB 1: Cover Letter ----------
cover = wb.active
cover.title = "Cover Letter"
cover.sheet_view.showGridLines = False

cover.column_dimensions["A"].width = 1
cover.column_dimensions["B"].width = 42
cover.column_dimensions["C"].width = 19
cover.column_dimensions["D"].width = 14

# OD header band
cover.row_dimensions[1].height = 0.1
cover["B1"] = "O+D BUILDERS"
cover["B1"].font = Font(name=FONT, size=11, bold=True, color=WHITE)
cover["B1"].fill = fill(DARK)
cover["B1"].alignment = Alignment(vertical="center", indent=1)
cover["C1"].fill = fill(DARK); cover["D1"].fill = fill(DARK)
cover["C1"] = "152 West 25th St. Suite 801"
cover["C1"].font = Font(name=FONT, size=10, color=WHITE)
cover["C1"].alignment = Alignment(horizontal="right", vertical="center")
cover["D1"] = "New York, NY 10001  |  (212) 929-8320"
cover["D1"].font = Font(name=FONT, size=10, color=WHITE)
cover["D1"].alignment = Alignment(horizontal="right", vertical="center")
cover.merge_cells("B1:B1")

r = 3
def setc(coord, val, font=None, align=None, fillc=None, border=None, fmt=None):
    c = cover[coord]
    c.value = val
    if font: c.font = font
    if align: c.alignment = align
    if fillc: c.fill = fill(fillc)
    if border: c.border = border
    if fmt: c.number_format = fmt
    return c

setc(f"B{r}", "Date: May 20, 2026", f_body(10))
r += 2
setc(f"B{r}", "Edward Tassey", f_body(10, bold=True))
r += 1
setc(f"B{r}", "O+D Builders", f_body(10))
r += 1
setc(f"B{r}", "152 West 25th St. Suite 801", f_body(10))
r += 1
setc(f"B{r}", "New York, NY 10001", f_body(10))
r += 2
setc(f"B{r}", "Re: 69-71 MacDougal Street Restaurant (Mosconi)", f_body(11, bold=True))
r += 1
setc(f"B{r}", "Architect: Sawicki Tarella  |  Owner: Mosconi (existing tenant - same ownership)", f_body(10, italic=True))
r += 2
setc(f"B{r}", "BUDGETARY ESTIMATE", f_body(11, bold=True), Alignment(horizontal="center"))
cover.merge_cells(f"B{r}:D{r}")
r += 2
setc(f"B{r}", ("Per the sketch plans dated 04/29/2024 (received 05/08/2026) and the project email "
               "thread between Sawicki Tarella and O+D Builders, we have prepared the "
               "following budgetary cost estimate for the renovation of the existing closed restaurant "
               "at 69-71 MacDougal Street. The kitchen remains in its existing location with minimal "
               "modification; the front-of-house is fully renovated."),
     f_body(10), Alignment(wrap_text=True, vertical="top"))
cover.merge_cells(f"B{r}:D{r}")
cover.row_dimensions[r].height = 80
r += 2

# Tiered summary table
setc(f"B{r}", "Scenario", f_body(10, bold=True, color=WHITE), Alignment(horizontal="left", indent=1, vertical="center"), DARK)
setc(f"C{r}", "Construction Total", f_body(10, bold=True, color=WHITE), Alignment(horizontal="center", vertical="center"), DARK)
setc(f"D{r}", "$ / SF FOH", f_body(10, bold=True, color=WHITE), Alignment(horizontal="center", vertical="center"), DARK)
cover.row_dimensions[r].height = 22
r += 1

# Pricing references - will be replaced by direct values for simplicity (cover is summary)
# Compute totals to populate
def compute_tier(items, tier_idx):
    subtotal = sum(it[2 + tier_idx] for it in items if not it[4])
    return subtotal

tier_a_direct = compute_tier(LINE_ITEMS, 0)
tier_b_direct = compute_tier(LINE_ITEMS, 1)
hvac_alt_direct_a = sum(x[2] for x in HVAC_ALT)
hvac_alt_direct_b = sum(x[3] for x in HVAC_ALT)
MARKUP_TOTAL = MARKUP_GC + MARKUP_FEE + MARKUP_INS + MARKUP_CONT  # 0.27

tier_a_total = tier_a_direct * (1 + MARKUP_TOTAL)
tier_b_total = tier_b_direct * (1 + MARKUP_TOTAL)
hvac_alt_a_total = hvac_alt_direct_a * (1 + MARKUP_TOTAL)
hvac_alt_b_total = hvac_alt_direct_b * (1 + MARKUP_TOTAL)

scenarios = [
    ("Tier A - Mid-Tier Upscale (HVAC Reuse Base)", tier_a_total),
    ("Tier A - Mid-Tier Upscale + HVAC Replacement", tier_a_total + hvac_alt_a_total),
    ("Tier B - High-End Signature (HVAC Reuse Base)", tier_b_total),
    ("Tier B - High-End Signature + HVAC Replacement", tier_b_total + hvac_alt_b_total),
]
for label, val in scenarios:
    setc(f"B{r}", label, f_body(10), Alignment(horizontal="left", indent=1, vertical="center"), border=BORDER_ALL)
    setc(f"C{r}", val, f_body(11, bold=True), Alignment(horizontal="center", vertical="center"), border=BORDER_ALL, fmt=MONEY)
    setc(f"D{r}", val/FOH_SF, f_body(10), Alignment(horizontal="center", vertical="center"), border=BORDER_ALL, fmt='"$"#,##0"/SF"')
    cover.row_dimensions[r].height = 20
    r += 1
r += 1

# Range callout
range_low = scenarios[0][1]
range_high = scenarios[3][1]
setc(f"B{r}", f"OVERALL BUDGET RANGE:  ${range_low/1e6:.2f}M  -  ${range_high/1e6:.2f}M",
     f_body(11, bold=True), Alignment(horizontal="center", vertical="center"), LIGHT_BLUE)
cover.merge_cells(f"B{r}:D{r}")
cover.row_dimensions[r].height = 26
r += 2

setc(f"B{r}", "BASIS OF ESTIMATE", f_body(11, bold=True, color=WHITE),
     Alignment(horizontal="left", indent=1, vertical="center"), DARK)
cover.merge_cells(f"B{r}:D{r}")
r += 1
basis = [
    "Class 5 / Order-of-Magnitude estimate per AACE International. Accuracy range -25% to +35%.",
    "Pricing based on sketch plans (existing-conditions filing A-101 / A-102) only.",
    "NYC open shop labor rates, 2026.",
    "6-month construction duration, standard daytime working hours, no acceleration premium.",
    "FOH gut + new bar in new location + new bathrooms (allowance) + new finishes/MEP throughout FOH.",
    "Kitchen equipment remains; light refresh only. Cellar minimal touch.",
    "Two finish tiers presented: Mid-Tier Upscale and High-End Signature.",
    "HVAC presented as base (reuse existing equipment) with add-alternate for full replacement.",
]
for line in basis:
    setc(f"B{r}", f"•  {line}", f_body(10), Alignment(wrap_text=True, vertical="top"))
    cover.merge_cells(f"B{r}:D{r}")
    cover.row_dimensions[r].height = 18
    r += 1

r += 1
setc(f"B{r}", "ATTACHMENTS", f_body(11, bold=True, color=WHITE),
     Alignment(horizontal="left", indent=1, vertical="center"), DARK)
cover.merge_cells(f"B{r}:D{r}")
r += 1
for att in [
    "Cost Totals - Tier A (Mid-Tier Upscale)",
    "Cost Totals - Tier B (High-End Signature)",
    "Cost Totals - HVAC Replacement Add-Alternate",
    "Takeoff & Quantities",
    "Notes, Assumptions, Inclusions & Exclusions",
]:
    setc(f"B{r}", f"•  {att}", f_body(10), Alignment(wrap_text=True, vertical="top"))
    cover.merge_cells(f"B{r}:D{r}")
    r += 1

r += 2
setc(f"B{r}", "Sincerely,", f_body(10))
r += 1
setc(f"B{r}", "O+D Builders", f_body(11, bold=True))
r += 3
setc(f"B{r}", "Accepted By: ________________________________   Date: ____________", f_body(10))

# ============================================================
# Cost Totals Sheet Builder
# ============================================================
def build_cost_totals(ws, title, tier_idx, sf_basis):
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 1
    ws.column_dimensions["B"].width = 9
    ws.column_dimensions["C"].width = 36
    ws.column_dimensions["D"].width = 13
    ws.column_dimensions["E"].width = 9
    ws.column_dimensions["F"].width = 11

    # Header band
    ws.row_dimensions[1].height = 0.1
    ws["B1"] = "O+D BUILDERS"
    ws["B1"].font = Font(name=FONT, size=11, bold=True, color=WHITE)
    ws["B1"].fill = fill(DARK)
    ws["B1"].alignment = Alignment(vertical="center", indent=1)
    for col in ["C", "D", "E", "F"]:
        ws[f"{col}1"].fill = fill(DARK)
    ws["F1"] = "Date: 05/20/2026"
    ws["F1"].font = Font(name=FONT, size=10, color=WHITE)
    ws["F1"].alignment = Alignment(horizontal="right", vertical="center")

    ws["B3"] = "Estimate: 260079 MacDougal Street Restaurant"
    ws["B3"].font = f_body(11, bold=True)
    ws.merge_cells("B3:D3")
    ws["F3"] = "Estimate Cost Totals"
    ws["F3"].font = f_body(11, bold=True)
    ws["F3"].alignment = Alignment(horizontal="right")

    ws["B4"] = title
    ws["B4"].font = f_body(10, italic=True, color="555555")
    ws.merge_cells("B4:D4")
    ws["F4"] = f"Basis: {sf_basis:,} SF FOH Renovation"
    ws["F4"].font = f_body(10, italic=True, color="555555")
    ws["F4"].alignment = Alignment(horizontal="right")

    # Column headers
    r = 6
    hdr = ["Code", "Description", "Total", "% of Cost", "Cost/SF"]
    cells = [f"B{r}", f"C{r}", f"D{r}", f"E{r}", f"F{r}"]
    for cell, h in zip(cells, hdr):
        ws[cell] = h
        ws[cell].font = f_body(10, bold=True)
        ws[cell].alignment = Alignment(horizontal="center" if cell != f"C{r}" else "left", vertical="center")
        ws[cell].border = Border(bottom=bottom_line, top=bottom_line)
        ws[cell].fill = fill(LIGHT_GRAY)
    ws[f"B{r}"].alignment = Alignment(horizontal="left", indent=1)
    ws[f"C{r}"].alignment = Alignment(horizontal="left")
    ws.row_dimensions[r].height = 22
    r += 1

    # Track row positions for direct cost cells (for sum + % formulas)
    direct_rows = []
    sub_header_rows = []
    direct_start = r

    for item in LINE_ITEMS:
        code, desc, ta, tb, is_header = item
        if is_header:
            ws[f"B{r}"] = code
            ws[f"B{r}"].font = f_body(10, bold=True)
            ws[f"B{r}"].fill = fill(LIGHT_GRAY)
            ws[f"B{r}"].alignment = Alignment(horizontal="left", indent=1, vertical="center")
            for col in ["C", "D", "E", "F"]:
                ws[f"{col}{r}"].fill = fill(LIGHT_GRAY)
                ws[f"{col}{r}"].border = Border(bottom=Side(border_style="thin", color=GRAY_LINE))
            ws[f"B{r}"].border = Border(bottom=Side(border_style="thin", color=GRAY_LINE))
            sub_header_rows.append(r)
        else:
            val = ta if tier_idx == 0 else tb
            ws[f"B{r}"] = code
            ws[f"B{r}"].font = f_body(10)
            ws[f"B{r}"].alignment = Alignment(horizontal="left", indent=1)
            ws[f"C{r}"] = desc
            ws[f"C{r}"].font = f_body(10)
            ws[f"C{r}"].alignment = Alignment(horizontal="left", wrap_text=True, vertical="center", indent=1)
            ws[f"D{r}"] = val
            ws[f"D{r}"].font = f_body(10)
            ws[f"D{r}"].number_format = MONEY
            ws[f"D{r}"].alignment = Alignment(horizontal="right")
            # Will be filled with formula once we know SUBTOTAL row
            direct_rows.append(r)
            for col in ["B", "C", "D", "E", "F"]:
                ws[f"{col}{r}"].border = Border(bottom=Side(border_style="thin", color="E0E0E0"))
        r += 1

    # Sub-Total (Direct Cost)
    subtotal_row = r
    ws[f"C{subtotal_row}"] = "Sub-Total (Direct Cost)"
    ws[f"C{subtotal_row}"].font = f_body(11, bold=True)
    ws[f"C{subtotal_row}"].alignment = Alignment(horizontal="left")
    sum_ranges = ",".join(f"D{rr}" for rr in direct_rows)
    ws[f"D{subtotal_row}"] = f"=SUM({sum_ranges})"
    ws[f"D{subtotal_row}"].font = f_body(11, bold=True)
    ws[f"D{subtotal_row}"].number_format = MONEY
    ws[f"D{subtotal_row}"].alignment = Alignment(horizontal="right")
    ws[f"E{subtotal_row}"] = f"=D{subtotal_row}/D{subtotal_row+5}"  # filled later; placeholder
    ws[f"F{subtotal_row}"] = f"=D{subtotal_row}/{sf_basis}"
    ws[f"F{subtotal_row}"].font = f_body(11, bold=True)
    ws[f"F{subtotal_row}"].number_format = '"$"#,##0.00'
    ws[f"F{subtotal_row}"].alignment = Alignment(horizontal="right")
    for col in ["B", "C", "D", "E", "F"]:
        ws[f"{col}{subtotal_row}"].fill = fill(LIGHT_GRAY)
        ws[f"{col}{subtotal_row}"].border = Border(top=bottom_line, bottom=bottom_line)
    ws.row_dimensions[subtotal_row].height = 22
    r = subtotal_row + 1

    # Markup rows
    # HOUSE CONVENTION: contingency is placed FIRST, directly below the subtotal,
    # above all other markups (GC / Fee / Insurance).
    cont_row = r
    ws[f"C{r}"] = "Design Contingency (Sketch Level)"
    ws[f"C{r}"].font = f_body(10)
    ws[f"D{r}"] = f"=D{subtotal_row}*{MARKUP_CONT}"
    ws[f"D{r}"].number_format = MONEY
    ws[f"D{r}"].alignment = Alignment(horizontal="right")
    r += 1

    gc_row = r
    ws[f"C{r}"] = "General Conditions"
    ws[f"C{r}"].font = f_body(10)
    ws[f"D{r}"] = f"=D{subtotal_row}*{MARKUP_GC}"
    ws[f"D{r}"].number_format = MONEY
    ws[f"D{r}"].alignment = Alignment(horizontal="right")
    r += 1

    fee_row = r
    ws[f"C{r}"] = "Fee"
    ws[f"C{r}"].font = f_body(10)
    ws[f"D{r}"] = f"=D{subtotal_row}*{MARKUP_FEE}"
    ws[f"D{r}"].number_format = MONEY
    ws[f"D{r}"].alignment = Alignment(horizontal="right")
    r += 1

    ins_row = r
    ws[f"C{r}"] = "Insurance"
    ws[f"C{r}"].font = f_body(10)
    ws[f"D{r}"] = f"=D{subtotal_row}*{MARKUP_INS}"
    ws[f"D{r}"].number_format = MONEY
    ws[f"D{r}"].alignment = Alignment(horizontal="right")
    r += 1

    # Total Estimate
    total_row = r
    ws[f"C{r}"] = "TOTAL ESTIMATE"
    ws[f"C{r}"].font = f_body(11, bold=True)
    ws[f"D{r}"] = f"=D{subtotal_row}+D{gc_row}+D{fee_row}+D{ins_row}+D{cont_row}"
    ws[f"D{r}"].font = f_body(11, bold=True)
    ws[f"D{r}"].number_format = MONEY
    ws[f"D{r}"].alignment = Alignment(horizontal="right")
    ws[f"E{r}"] = 1
    ws[f"E{r}"].font = f_body(11, bold=True)
    ws[f"E{r}"].number_format = PCT
    ws[f"E{r}"].alignment = Alignment(horizontal="right")
    ws[f"F{r}"] = f"=D{r}/{sf_basis}"
    ws[f"F{r}"].font = f_body(11, bold=True)
    ws[f"F{r}"].number_format = '"$"#,##0.00'
    ws[f"F{r}"].alignment = Alignment(horizontal="right")
    for col in ["B", "C", "D", "E", "F"]:
        ws[f"{col}{r}"].fill = fill(LIGHT_BLUE)
        ws[f"{col}{r}"].border = Border(top=bottom_line, bottom=bottom_line)
    ws.row_dimensions[r].height = 26

    # Fill in percent and cost/SF for direct items + markups (after Total row known)
    for rr in direct_rows:
        ws[f"E{rr}"] = f"=IFERROR(D{rr}/$D${total_row},0)"
        ws[f"E{rr}"].number_format = PCT
        ws[f"E{rr}"].alignment = Alignment(horizontal="right")
        ws[f"E{rr}"].font = f_body(10)
        ws[f"F{rr}"] = f"=D{rr}/{sf_basis}"
        ws[f"F{rr}"].number_format = '"$"#,##0.00'
        ws[f"F{rr}"].alignment = Alignment(horizontal="right")
        ws[f"F{rr}"].font = f_body(10)
    # Subtotal percent
    ws[f"E{subtotal_row}"] = f"=D{subtotal_row}/D{total_row}"
    ws[f"E{subtotal_row}"].number_format = PCT
    ws[f"E{subtotal_row}"].font = f_body(11, bold=True)
    ws[f"E{subtotal_row}"].alignment = Alignment(horizontal="right")
    # Markup percent + $/SF
    for rr in [gc_row, fee_row, ins_row, cont_row]:
        ws[f"E{rr}"] = f"=D{rr}/D{total_row}"
        ws[f"E{rr}"].number_format = PCT
        ws[f"E{rr}"].alignment = Alignment(horizontal="right")
        ws[f"F{rr}"] = f"=D{rr}/{sf_basis}"
        ws[f"F{rr}"].number_format = '"$"#,##0.00'
        ws[f"F{rr}"].alignment = Alignment(horizontal="right")

    return total_row

# ---------- TAB 2: Cost Totals - Tier A ----------
ws_a = wb.create_sheet("Cost Totals - Tier A")
build_cost_totals(ws_a, "Tier A: Mid-Tier Upscale  |  HVAC Reuse (Base)", 0, FOH_SF)

# ---------- TAB 3: Cost Totals - Tier B ----------
ws_b = wb.create_sheet("Cost Totals - Tier B")
build_cost_totals(ws_b, "Tier B: High-End Signature  |  HVAC Reuse (Base)", 1, FOH_SF)

# ---------- TAB 4: HVAC Add-Alternate ----------
ws_h = wb.create_sheet("HVAC Add-Alt")
ws_h.sheet_view.showGridLines = False
for col, w in zip("ABCDE", [1, 9, 42, 11, 11]):
    ws_h.column_dimensions[col].width = w

ws_h.row_dimensions[1].height = 0.1
ws_h["B1"] = "O+D BUILDERS"
ws_h["B1"].font = Font(name=FONT, size=11, bold=True, color=WHITE)
ws_h["B1"].fill = fill(DARK)
ws_h["B1"].alignment = Alignment(vertical="center", indent=1)
for col in "CDE":
    ws_h[f"{col}1"].fill = fill(DARK)
ws_h["E1"] = "Date: 05/20/2026"
ws_h["E1"].font = Font(name=FONT, size=10, color=WHITE)
ws_h["E1"].alignment = Alignment(horizontal="right", vertical="center")

ws_h["B3"] = "Estimate: 260079 MacDougal Street Restaurant"
ws_h["B3"].font = f_body(11, bold=True)
ws_h.merge_cells("B3:C3")
ws_h["D3"] = "HVAC Add-Alt"
ws_h["D3"].font = f_body(11, bold=True)
ws_h["D3"].alignment = Alignment(horizontal="right")
ws_h.merge_cells("D3:E3")

ws_h["B4"] = "Carry as ADD to the Base Estimate (which assumes existing HVAC equipment is reused)."
ws_h["B4"].font = f_body(10, italic=True, color="555555")
ws_h.merge_cells("B4:E4")

r = 6
ws_h[f"B{r}"] = "Code"
ws_h[f"C{r}"] = "Description"
ws_h[f"D{r}"] = "Tier A Add"
ws_h[f"E{r}"] = "Tier B Add"
for cc in [f"B{r}", f"C{r}", f"D{r}", f"E{r}"]:
    ws_h[cc].font = f_body(10, bold=True)
    ws_h[cc].fill = fill(LIGHT_GRAY)
    ws_h[cc].border = Border(top=bottom_line, bottom=bottom_line)
    ws_h[cc].alignment = Alignment(horizontal="center", vertical="center")
ws_h[f"C{r}"].alignment = Alignment(horizontal="left")
ws_h.row_dimensions[r].height = 22

r += 1
hvac_direct_rows = []
for code, desc, va, vb in HVAC_ALT:
    ws_h[f"B{r}"] = code
    ws_h[f"B{r}"].font = f_body(10)
    ws_h[f"B{r}"].alignment = Alignment(horizontal="left", indent=1)
    ws_h[f"C{r}"] = desc
    ws_h[f"C{r}"].font = f_body(10)
    ws_h[f"C{r}"].alignment = Alignment(horizontal="left", wrap_text=True, vertical="center", indent=1)
    ws_h[f"D{r}"] = va
    ws_h[f"E{r}"] = vb
    for cc in [f"D{r}", f"E{r}"]:
        ws_h[cc].font = f_body(10)
        ws_h[cc].number_format = MONEY
        ws_h[cc].alignment = Alignment(horizontal="right")
    hvac_direct_rows.append(r)
    r += 1

hvac_subtotal = r
ws_h[f"C{r}"] = "Sub-Total (Direct Cost)"
ws_h[f"C{r}"].font = f_body(11, bold=True)
ws_h[f"D{r}"] = f"=SUM(D{hvac_direct_rows[0]}:D{hvac_direct_rows[-1]})"
ws_h[f"E{r}"] = f"=SUM(E{hvac_direct_rows[0]}:E{hvac_direct_rows[-1]})"
for cc in [f"D{r}", f"E{r}"]:
    ws_h[cc].font = f_body(11, bold=True)
    ws_h[cc].number_format = MONEY
    ws_h[cc].alignment = Alignment(horizontal="right")
for col in "BCDE":
    ws_h[f"{col}{r}"].fill = fill(LIGHT_GRAY)
    ws_h[f"{col}{r}"].border = Border(top=bottom_line, bottom=bottom_line)
ws_h.row_dimensions[r].height = 22
r += 1

# Markups
# HOUSE CONVENTION: contingency first, directly below the subtotal, above other markups.
mh_con = r
ws_h[f"C{r}"] = "Design Contingency"
ws_h[f"D{r}"] = f"=D{hvac_subtotal}*{MARKUP_CONT}"
ws_h[f"E{r}"] = f"=E{hvac_subtotal}*{MARKUP_CONT}"
r += 1
mh_gc = r
ws_h[f"C{r}"] = "General Conditions"
ws_h[f"D{r}"] = f"=D{hvac_subtotal}*{MARKUP_GC}"
ws_h[f"E{r}"] = f"=E{hvac_subtotal}*{MARKUP_GC}"
r += 1
mh_fee = r
ws_h[f"C{r}"] = "Fee"
ws_h[f"D{r}"] = f"=D{hvac_subtotal}*{MARKUP_FEE}"
ws_h[f"E{r}"] = f"=E{hvac_subtotal}*{MARKUP_FEE}"
r += 1
mh_ins = r
ws_h[f"C{r}"] = "Insurance"
ws_h[f"D{r}"] = f"=D{hvac_subtotal}*{MARKUP_INS}"
ws_h[f"E{r}"] = f"=E{hvac_subtotal}*{MARKUP_INS}"
r += 1
for rr in [mh_gc, mh_fee, mh_ins, mh_con]:
    ws_h[f"C{rr}"].font = f_body(10)
    for cc in [f"D{rr}", f"E{rr}"]:
        ws_h[cc].font = f_body(10)
        ws_h[cc].number_format = MONEY
        ws_h[cc].alignment = Alignment(horizontal="right")

# Total
ws_h[f"C{r}"] = "TOTAL ADD-ALTERNATE"
ws_h[f"C{r}"].font = f_body(11, bold=True)
ws_h[f"D{r}"] = f"=D{hvac_subtotal}+D{mh_gc}+D{mh_fee}+D{mh_ins}+D{mh_con}"
ws_h[f"E{r}"] = f"=E{hvac_subtotal}+E{mh_gc}+E{mh_fee}+E{mh_ins}+E{mh_con}"
for cc in [f"D{r}", f"E{r}"]:
    ws_h[cc].font = f_body(11, bold=True)
    ws_h[cc].number_format = MONEY
    ws_h[cc].alignment = Alignment(horizontal="right")
for col in "BCDE":
    ws_h[f"{col}{r}"].fill = fill(LIGHT_BLUE)
    ws_h[f"{col}{r}"].border = Border(top=bottom_line, bottom=bottom_line)
ws_h.row_dimensions[r].height = 26

# ---------- TAB 5: Takeoff ----------
ws_t = wb.create_sheet("Takeoff")
ws_t.sheet_view.showGridLines = False
for col, w in zip("ABCDE", [1, 36, 10, 6, 18]):
    ws_t.column_dimensions[col].width = w

ws_t.row_dimensions[1].height = 0.1
ws_t["B1"] = "O+D BUILDERS"
ws_t["B1"].font = Font(name=FONT, size=11, bold=True, color=WHITE)
ws_t["B1"].fill = fill(DARK)
ws_t["B1"].alignment = Alignment(vertical="center", indent=1)
for col in "CDE":
    ws_t[f"{col}1"].fill = fill(DARK)
ws_t["E1"] = "Date: 05/20/2026"
ws_t["E1"].font = Font(name=FONT, size=10, color=WHITE)
ws_t["E1"].alignment = Alignment(horizontal="right", vertical="center")

ws_t["B3"] = "Estimate: 260079 MacDougal Street Restaurant"
ws_t["B3"].font = f_body(11, bold=True)
ws_t.merge_cells("B3:C3")
ws_t["D3"] = "Takeoff & Quantities"
ws_t["D3"].font = f_body(11, bold=True)
ws_t["D3"].alignment = Alignment(horizontal="right")
ws_t.merge_cells("D3:E3")
ws_t["B4"] = "Quantities scaled from sketch plans dated 04/29/2024. Subject to verification."
ws_t["B4"].font = f_body(10, italic=True, color="555555")
ws_t.merge_cells("B4:E4")

# Takeoff data
TAKEOFF = [
    ("AREA SUMMARY", None, None, None, True),
    ("Main Level - FOH (Dining + Bar + Cocktail Lounge)", 2138, "SF", "Confirmed by Owner"),
    ("Main Level - Kitchen (light refresh only)", 800, "SF", "Existing equipment to remain"),
    ("Main Level - Bathrooms (allowance basis)", 400, "SF", "2 bathrooms - ADA gut"),
    ("Main Level - Circulation / Utility / Service", 662, "SF", ""),
    ("TOTAL MAIN LEVEL", 4000, "SF", "Confirmed by Owner"),
    ("Cellar Level - BOH / Storage (minimal touch)", 2960, "SF", "Paint, LED relamp only"),
    ("TOTAL GROSS SF", 6960, "SF", "Confirmed by Owner"),

    ("01 GENERAL REQUIREMENTS", None, None, None, True),
    ("General Supervision", 26, "WK", "6-month build, full-time super"),
    ("Project Management (50%)", 26, "WK", ""),
    ("Misc Materials & Protection", 1, "LS", "Floor protection, dust walls, temp partitions"),
    ("Temporary Toilet(s)", 6, "MO", ""),
    ("Hoisting / Dumpsters / Site Logistics", 1, "LS", ""),
    ("Daily / Final Clean", 1, "LS", ""),
    ("Blueprints", 150, "EA", ""),

    ("02 DEMOLITION", None, None, None, True),
    ("Selective Demolition - FOH Gut to Shell", 2138, "SF", "Walls, ceilings, finishes, MEP"),
    ("Bathroom Demolition (Full Gut to Studs)", 2, "BATH", ""),
    ("Bar Demolition (Existing Bar Removal)", 1, "LS", ""),
    ("Light Kitchen Demolition (Selective)", 800, "SF", "Finish refresh prep only"),
    ("Light Cellar Demolition (Selective)", 1, "LS", "Equipment stays"),

    ("03 CONCRETE", None, None, None, True),
    ("Floor Patching / Leveling (Post-Demo)", 2138, "SF", "No structural slab work"),

    ("04 MASONRY", None, None, None, True),
    ("Exposed Brick Repair / Repointing (Feature Walls)", 500, "SF", "Cosmetic only - no structural"),

    ("05 METALS", None, None, None, True),
    ("Banquette Steel Frames", 45, "LF", ""),
    ("Decorative Railings", 20, "LF", ""),
    ("Misc Steel (Ceiling Support, Soffit Hangers)", 1, "LS", "Non-structural only"),

    ("06 MILLWORK", None, None, None, True),
    ("F/I Custom Bar - Front & Top", 22, "LF", "New location"),
    ("F/I Custom Back Bar (Full Height)", 22, "LF", "With shelving for spirits"),
    ("F/I Built-In Banquettes (Upholstered Tops by Others)", 45, "LF", ""),
    ("F/I Host Stand", 1, "EA", ""),
    ("F/I Service Stations", 2, "EA", ""),
    ("F/I Wall Paneling / Wainscot (Tier-Dependent)", 30, "LF", ""),
    ("F/I Base Molding @ FOH", 140, "LF", ""),
    ("F/I Lower Cabinets Behind Bar", 18, "LF", ""),

    ("07 THERMAL & MOISTURE", None, None, None, True),
    ("Waterproofing @ Bathrooms (in Bath Allowance)", 1, "LS", ""),
    ("Acoustic Insulation @ Partitions", 1000, "SF", ""),
    ("Firestopping @ Penetrations", 1, "LS", ""),
    ("Sealants & Caulking", 1, "LS", ""),

    ("08 OPENINGS", None, None, None, True),
    ("F/O Wood Doors @ FOH/BOH", 5, "EA", ""),
    ("F/O HM Doors @ BOH/Service", 2, "EA", ""),
    ("F/O Eliason Swinging Door (Kitchen Pass)", 1, "PR", ""),
    ("Door Hardware Package", 7, "EA", ""),
    ("F/I Interior Storefront / Glass Partition (If Required)", 60, "SF", "Allowance"),

    ("09 FINISHES", None, None, None, True),
    ("F/I 5/8\" GWB Walls (Level 4 Finish)", 3200, "SF", ""),
    ("F/I 3-5/8\" Metal Stud Framing", 1800, "SF", ""),
    ("F/I Soffits / Bulkheads", 150, "SF", ""),
    ("F/I Acoustical Ceiling Treatment @ FOH", 2138, "SF", "Decorative + acoustic"),
    ("F/I Wood Plank / Plaster Ceiling (Feature)", 800, "SF", "Tier-dependent"),
    ("F/I Engineered Hardwood Flooring @ FOH", 1750, "SF", "Tier A; Stone or Specialty in Tier B"),
    ("F/I Tile Flooring @ Bar Area / Vestibule", 400, "SF", ""),
    ("F/I Tile Flooring @ Bathrooms (in Bath Allowance)", 400, "SF", ""),
    ("F/I Wall Tile @ Bar Back (Feature)", 150, "SF", "Tier-dependent"),
    ("F/I Tile Cove Base", 120, "LF", ""),
    ("F/I Stone Countertops @ Bar Top", 70, "SF", "Tier-dependent material grade"),
    ("Painting - Walls (Specialty Finishes in Tier B)", 3200, "SF", ""),
    ("Painting - Ceilings / Exposed Structure", 800, "SF", ""),
    ("Painting - Doors, Trim, Base", 1, "LS", ""),

    ("10 SPECIALTIES", None, None, None, True),
    ("F/I FRP Wall Protection @ BOH", 300, "SF", ""),
    ("Bath Accessories (in Bath Allowance)", 2, "BATH", ""),

    ("11 EQUIPMENT", None, None, None, True),
    ("Kitchen Equipment - Existing to Remain", 1, "LS", "By Owner / Existing"),
    ("Hood Cleaning, Recertification, Damper Test", 1, "LS", ""),
    ("Hood Suppression (Ansul) Recertification", 1, "LS", ""),
    ("Gas Line Pressure Test & Recertification", 1, "LS", ""),

    ("12 FURNISHINGS", None, None, None, True),
    ("Loose Furniture (Tables, Chairs, Barstools)", 1, "LS", "EXCLUDED - Owner Furnished"),
    ("Window Treatments (Drapery / Blinds @ FOH)", 1, "LS", ""),

    ("21 FIRE SUPPRESSION", None, None, None, True),
    ("Sprinkler Heads & Drops Modification", 2138, "SF", "To suit new ceiling layout"),
    ("Sprinkler Permits, Filing, Inspections, Sign-Off", 1, "LS", ""),

    ("22 PLUMBING", None, None, None, True),
    ("Bar Plumbing (Water, Drain, Soda Gun, Draft Drain, Ice Well)", 1, "LS", ""),
    ("Bathroom Rough-In (in Bath Allowance)", 2, "BATH", ""),
    ("F/I Floor Drains @ Bar", 2, "EA", ""),
    ("F/I Floor Sinks", 2, "EA", ""),
    ("F/I Grease Interceptor Inspection / Recert", 1, "EA", ""),
    ("F/I Hot Water Heater (Replace)", 1, "EA", ""),
    ("Gas Line Modifications @ Bar (If Required)", 1, "LS", ""),
    ("Plumbing Fixtures - Bar (Faucet, Sinks)", 1, "LS", ""),

    ("23 HVAC", None, None, None, True),
    ("Base Scope - Reuse Existing Equipment + New Distribution", None, None, None, True),
    ("F/I New Ductwork, Diffusers, Grilles, Insulation @ FOH", 2138, "SF", ""),
    ("F/I New VAVs / Zone Dampers", 4, "EA", ""),
    ("F/I New Controls / BMS / Thermostats", 1, "LS", ""),
    ("F/I New Toilet Exhaust Fans", 2, "EA", ""),
    ("Refrigerant Line Inspection / Refresh @ Existing Equipment", 1, "LS", ""),
    ("Equipment Cleaning / PM / Coil Check", 1, "LS", ""),
    ("Test, Adjust & Balance (TAB)", 1, "LS", ""),
    ("Shop Drawings & Coordination", 1, "LS", ""),
    ("Add-Alt Scope - Full Equipment Replacement (See HVAC Add-Alt Tab)", None, None, None, True),

    ("26 ELECTRICAL", None, None, None, True),
    ("New Distribution from Existing Service (Panels, Feeders)", 1, "LS", ""),
    ("Branch Wiring - FOH Devices, Circuits, Dedicated Outlets", 2138, "SF", ""),
    ("F/I Duplex Receptacles", 22, "EA", ""),
    ("F/I GFI Receptacles", 10, "EA", ""),
    ("F/I Dedicated Equipment Outlets @ Bar / Kitchen", 10, "EA", ""),
    ("F/I Floor-Mounted Duplex + Tel/Data @ Host Station", 2, "EA", ""),
    ("Wire ANSUL Hood Suppression", 1, "LS", ""),
    ("Wire Kitchen Equipment Reconnections", 1, "LS", ""),
    ("Wire Toilet Exhaust Fans", 2, "EA", ""),
    ("Emergency / Exit Lighting Per Code", 1, "LS", ""),
    ("Lighting Controls / Dimming / Scene Control", 1, "LS", ""),

    ("26.5 LIGHTING FIXTURES (ALLOWANCE)", None, None, None, True),
    ("F/O 2x2 Lay-In Fixtures @ BOH ($300/EA Allow)", 6, "EA", ""),
    ("F/O Recessed Downlights @ FOH ($350/EA Allow)", 25, "EA", ""),
    ("F/O Pendant Fixtures Above Bar ($1,500/EA Tier A; $2,500 Tier B)", 6, "EA", ""),
    ("F/O Decorative Sconces @ Dining ($600/EA Tier A; $1,200 Tier B)", 14, "EA", ""),
    ("F/O Statement Chandelier / Feature Fixture", 2, "EA", "Allowance, tier-dependent"),
    ("F/O Linear / Cove Lighting (Tier B)", 35, "LF", ""),

    ("27 COMMUNICATIONS", None, None, None, True),
    ("Tel/Data Outlets - Rough-In Only (Wiring & Equipment NIC)", 6, "EA", ""),
    ("Audio Visual System Rough-In - Conduit, Boxes Only", 2138, "SF", "AV Gear EXCLUDED"),
    ("Network / WiFi System Rough-In", 1, "LS", "Equipment NIC"),

    ("28 SAFETY & SECURITY", None, None, None, True),
    ("Fire Alarm Design-Build (Device Add/Relocate, Reprogramming)", 2138, "SF", ""),
    ("Security System Rough-In", 2138, "SF", "Equipment NIC"),

    ("ALLOWANCES", None, None, None, True),
    ("Bathroom Allowance (2 Bathrooms - Full ADA Gut)", 2, "BATH", "$85K/EA, both tiers"),
    ("Cellar Refresh Allowance (Paint, LED Relamp, Minor MEP)", 2960, "SF", "Minimal touch only"),
]

r = 6
ws_t[f"B{r}"] = "Description"
ws_t[f"C{r}"] = "Quantity"
ws_t[f"D{r}"] = "Unit"
ws_t[f"E{r}"] = "Notes"
for cc in [f"B{r}", f"C{r}", f"D{r}", f"E{r}"]:
    ws_t[cc].font = f_body(10, bold=True)
    ws_t[cc].fill = fill(LIGHT_GRAY)
    ws_t[cc].border = Border(top=bottom_line, bottom=bottom_line)
    ws_t[cc].alignment = Alignment(horizontal="center", vertical="center")
ws_t[f"B{r}"].alignment = Alignment(horizontal="left", indent=1)
ws_t[f"E{r}"].alignment = Alignment(horizontal="left")
ws_t.row_dimensions[r].height = 22
r += 1

for item in TAKEOFF:
    if len(item) == 5 and item[4] is True:
        ws_t[f"B{r}"] = item[0]
        ws_t[f"B{r}"].font = f_body(10, bold=True)
        ws_t[f"B{r}"].fill = fill(LIGHT_GRAY)
        ws_t[f"B{r}"].alignment = Alignment(horizontal="left", indent=1)
        for col in "CDE":
            ws_t[f"{col}{r}"].fill = fill(LIGHT_GRAY)
            ws_t[f"{col}{r}"].border = Border(bottom=Side(border_style="thin", color=GRAY_LINE))
        ws_t[f"B{r}"].border = Border(bottom=Side(border_style="thin", color=GRAY_LINE))
        ws_t.row_dimensions[r].height = 20
    else:
        desc, qty, unit, notes = item
        ws_t[f"B{r}"] = desc
        ws_t[f"B{r}"].font = f_body(10)
        ws_t[f"B{r}"].alignment = Alignment(horizontal="left", indent=2, wrap_text=True, vertical="center")
        if qty is not None:
            ws_t[f"C{r}"] = qty
            ws_t[f"C{r}"].font = f_body(10)
            ws_t[f"C{r}"].number_format = NUM2 if (isinstance(qty, float)) else NUM0
            ws_t[f"C{r}"].alignment = Alignment(horizontal="right")
        if unit is not None:
            ws_t[f"D{r}"] = unit
            ws_t[f"D{r}"].font = f_body(10)
            ws_t[f"D{r}"].alignment = Alignment(horizontal="center")
        if notes:
            ws_t[f"E{r}"] = notes
            ws_t[f"E{r}"].font = f_body(10, italic=True, color="555555")
            ws_t[f"E{r}"].alignment = Alignment(horizontal="left", wrap_text=True, vertical="center")
        for col in "BCDE":
            ws_t[f"{col}{r}"].border = Border(bottom=Side(border_style="thin", color="E8E8E8"))
    r += 1

# ---------- TAB 6: Notes & Clarifications ----------
ws_n = wb.create_sheet("Notes & Clarifications")
ws_n.sheet_view.showGridLines = False
ws_n.column_dimensions["A"].width = 3
ws_n.column_dimensions["B"].width = 80

ws_n.row_dimensions[1].height = 0.1
ws_n["B1"] = "O+D BUILDERS"
ws_n["B1"].font = Font(name=FONT, size=11, bold=True, color=WHITE)
ws_n["B1"].fill = fill(DARK)
ws_n["B1"].alignment = Alignment(vertical="center", indent=1)

ws_n["B3"] = "Notes, Assumptions, Inclusions & Exclusions"
ws_n["B3"].font = f_body(11, bold=True)
ws_n["B4"] = "Estimate: 260079 MacDougal Street Restaurant (Mosconi) - 69-71 MacDougal St, NY NY 10012"
ws_n["B4"].font = f_body(10, italic=True, color="555555")

r = 6
def section(title):
    global r
    ws_n[f"B{r}"] = title
    ws_n[f"B{r}"].font = f_body(11, bold=True, color=WHITE)
    ws_n[f"B{r}"].fill = fill(DARK)
    ws_n[f"B{r}"].alignment = Alignment(horizontal="left", indent=1, vertical="center")
    ws_n.row_dimensions[r].height = 22
    r += 1

def bullet(text):
    global r
    ws_n[f"B{r}"] = f"•  {text}"
    ws_n[f"B{r}"].font = f_body(10)
    ws_n[f"B{r}"].alignment = Alignment(horizontal="left", indent=1, wrap_text=True, vertical="top")
    ws_n.row_dimensions[r].height = max(18, 14 * (len(text) // 95 + 1))
    r += 1

def blank():
    global r
    r += 1

section("BASIS OF ESTIMATE")
bullet("Class 5 / Order-of-Magnitude budgetary estimate per AACE International. Accuracy range: -25% to +35%.")
bullet("Based on sketch plans dated 04/29/2024 (AMP Architecture ALT-CO existing-conditions filing). No design development drawings have been issued.")
bullet("Project email thread between Joseph Tarella (Sawicki Tarella) and Edward Tassey (O+D Builders) dated 05/08/2026 used as scope basis.")
bullet("NYC open shop labor rates, 2026.")
bullet("6-month construction duration, standard daytime working hours (7 AM - 4 PM, M-F), no acceleration premium.")
bullet("Areas confirmed by Owner: Main Level 4,000 SF (FOH gut 2,138 SF + light kitchen 800 SF + bathrooms 400 SF + circulation/utility 662 SF), Cellar 2,960 SF (minimal touch). Total gross 6,960 SF.")
bullet("All cost ranges shown are construction cost only (trades + GC overhead + fee + insurance + design contingency). Owner soft costs are excluded.")
blank()

section("KEY ASSUMPTIONS")
bullet("Existing electrical service is adequate for the proposed program; no Con Edison service upgrade required.")
bullet("Existing kitchen equipment is in good working condition and remains in place. Hood is recent and only requires cleaning, damper testing, and Ansul recertification.")
bullet("NO STRUCTURAL WORK CARRIED. Existing structure assumed adequate for the proposed bar relocation and all other scope. No beam, column, slab, or load-bearing modifications included. If structural work is required after SE review, change order applies.")
bullet("Existing sprinkler service and standpipe remain; only sprinkler heads and drops are modified to suit new ceiling layout.")
bullet("Existing fire alarm panel remains; devices are added/relocated and reprogrammed to suit new layout. If DOB requires panel replacement under the alteration filing, see exclusions.")
bullet("Existing bathrooms are fully gutted to studs. Allowance basis: $85K/bath (both tiers, total $170K for 2 bathrooms) covering plumbing rough-in, fixtures, partitions, tile, finishes, accessories, lighting, exhaust, ADA compliance.")
bullet("Bar relocation: new bar is constructed in a new location with full custom millwork (~22 LF), back bar, underbar equipment rough-in, draft beer system rough-in, soda gun, ice well, and 3-comp sink. Bar equipment package itself (taps, glassware, POS) is owner-furnished.")
bullet("Cellar receives minimal touch only: paint refresh, LED relamp, minor MEP maintenance. No reconfiguration of storage, walk-ins, or prep areas is included.")
bullet("NO ASBESTOS TESTING OR ABATEMENT CARRIED. Owner to provide pre-existing ACM-clear letter or perform testing under separate scope prior to demolition. If ACM, lead paint, or other hazmat is identified or encountered, all testing, abatement, and DEP filings are by change order.")
bullet("Working hours are standard daytime. Restaurant is closed during construction; no off-hours premium is carried.")
blank()

section("INCLUSIONS")
bullet("All construction labor, materials, equipment, and supervision per the Cost Totals breakdown.")
bullet("GC General Conditions, Fee, Insurance, and Design Contingency.")
bullet("Hoisting, dumpsters, daily clean, final clean.")
bullet("Floor and surface protection during construction.")
bullet("Temporary partitions / dust barriers as required.")
bullet("Punchlist and one-year warranty walk per O+D standard.")
blank()

section("EXCLUSIONS")
bullet("New storefront and new exterior staircase (separate timeline per Sawicki Tarella email 05/08/2026).")
bullet("Loose furniture: tables, chairs, barstools, decorative furnishings (owner-furnished).")
bullet("Kitchen equipment: ranges, ovens, refrigeration, dish equipment (existing remains; no new equipment included).")
bullet("FF&E procurement, smallwares, dishware, glassware, POS systems, cash drawers, printers.")
bullet("Audio-visual equipment, music systems, TV displays, projector systems (rough-in only included).")
bullet("Network / WiFi equipment, switches, access points, cabling termination by IT vendor (rough-in only included).")
bullet("Security equipment: cameras, NVR, alarm panel, monitoring service (rough-in only included).")
bullet("Signage: exterior signage, awning, blade signs, interior wayfinding (rough-in for electric where applicable only).")
bullet("Exterior facade work, window replacement, door replacement at storefront (separate timeline).")
bullet("Sidewalk vault repairs, sidewalk replacement, exterior lighting at facade.")
bullet("New Con Edison electrical service, transformer upgrade, vault work.")
bullet("Sales tax (NYS / NYC). Owner to provide certificate of capital improvement or carry tax separately.")
bullet("Permits: DOB filing fees, expediter fees, plumbing/electrical/fire alarm filing fees (owner direct).")
bullet("Architectural, structural, MEP engineering design fees.")
bullet("Liquor license, food service permits, NYC Department of Health inspections and fees.")
bullet("Asbestos testing and abatement (ALL hazmat testing and abatement excluded - by Owner or by change order if encountered).")
bullet("Lead paint, mold, PCB testing or abatement (same as above - change order if encountered).")
bullet("ALL structural work: beam, column, slab, foundation, load-bearing wall, lintel, or any structural reinforcement. No SE-designed work included.")
bullet("Acceleration premium, overtime, off-hours work, or weekend work.")
bullet("Bond premiums (assumed not required for this private project).")
bullet("Owner's contingency, owner's representative fees, project management consulting.")
bullet("Cellar reconfiguration: new walk-in boxes, equipment relocation, new finishes beyond minimal touch.")
bullet("Storefront, new entry stair, vestibule reconfiguration (separate timeline per Sawicki Tarella).")
blank()

section("ALLOWANCES SUMMARY")
bullet("Bathroom Allowance: $170K both tiers ($85K/bath x 2). Includes full ADA gut with plumbing, fixtures, partitions, tile, finishes, lighting, exhaust.")
bullet("Cellar Refresh: $12K (Tier A) or $18K (Tier B). Paint, LED relamp, minor MEP.")
bullet("Lighting Fixtures: $40K (Tier A) or $80K (Tier B). Decorative pendants, sconces, recessed, statement fixtures. Custom statement fixtures above bar are at upper end.")
bullet("Interior Storefront / Vestibule Glazing: $10K (Tier A) or $25K (Tier B). Used if a vestibule glass partition is incorporated into the design.")
blank()

section("SCHEDULE NOTES")
bullet("Construction duration: 6 months from notice to proceed.")
bullet("Reopen-before-end-of-2026 target IS achievable from a construction standpoint, but requires:")
bullet("   - Immediate schematic design + DOB filing alignment by Sawicki Tarella")
bullet("   - Long-lead procurement decisions on millwork, lighting, tile, custom metals within 60 days of contract")
bullet("   - Owner FF&E selections finalized prior to Month 6")
bullet("   - Expediter engaged for DOB filing within 30 days")
bullet("If start date slips past July 2026, December 2026 reopen becomes at risk. Acceleration premium (8-12%) may be required to recover.")
blank()

section("TIER DEFINITIONS")
bullet("TIER A - MID-TIER UPSCALE: Engineered hardwood + tile flooring; painted GWB with wood paneling accents; custom millwork bar; decorative pendant + recessed lighting; mid-grade tile at bar back and bathrooms; standard ADA bathrooms; off-the-shelf hardware. Typical NYC West Village restaurant fit-out.")
bullet("TIER B - HIGH-END SIGNATURE: Wide-plank specialty hardwood or stone flooring; Venetian plaster and specialty wall finishes; premium custom millwork with stone and brass accents; designer lighting package including statement chandeliers; imported tile / natural stone; premium bathroom fixtures and finishes; custom hardware. Comparable to upper-tier restaurants of similar scale in NYC.")
blank()

section("VALIDITY")
bullet("This estimate is valid for 60 days from the date of issue.")
bullet("Re-pricing required upon receipt of design development or construction documents.")
bullet("Trade subcontractor pricing not yet solicited; pricing reflects historical NYC open shop data and internal cost database.")

# Save
wb.save(OUT)
print(f"Saved: {OUT}")

# Echo computed totals for cross-check
print(f"\nTier A direct cost:  ${tier_a_direct:>12,.0f}")
print(f"Tier A total:        ${tier_a_total:>12,.0f}  (${tier_a_total/FOH_SF:.0f}/SF FOH)")
print(f"Tier B direct cost:  ${tier_b_direct:>12,.0f}")
print(f"Tier B total:        ${tier_b_total:>12,.0f}  (${tier_b_total/FOH_SF:.0f}/SF FOH)")
print(f"HVAC alt A total:    ${hvac_alt_a_total:>12,.0f}")
print(f"HVAC alt B total:    ${hvac_alt_b_total:>12,.0f}")
print(f"\nOverall range: ${tier_a_total/1e6:.2f}M (Tier A base) - ${(tier_b_total + hvac_alt_b_total)/1e6:.2f}M (Tier B + HVAC)")
