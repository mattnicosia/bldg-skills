---
name: sow-generator
description: Generates bulletproof, professionally formatted construction Scopes of Work in Excel format from construction drawings, spec books, and Notebook LM extracted content. Use this skill whenever the user mentions creating a scope of work, SOW, scoping a project, scoping out a trade, scoping a sub, generating subcontractor scope, or asks to break a project into trades by CSI subdivision. Also trigger when the user references drawing.md files, has uploaded construction drawings or specifications, or mentions Montana Contracting / BLDG Estimating scope output. Always use this skill for any scope of work generation - it enforces directive language (F/I, F/O, I/O, Remove, Provide), bracket spec format, citation tracking, conflict detection, TBD tracking, trade-specific scope splitting rules, multi-pass QA validation that prevents hallucination, and a polished black/gray/white professional Excel output organized by CSI subdivision.
---

# SOW Generator

A scope of work generation skill built for Montana Contracting / BLDG Estimating. Outputs professional, polished Excel SOWs organized by CSI subdivision with citation tracking and zero tolerance for hallucination.

## Workflow Overview

This skill runs in three phases:

1. **EXTRACT** — Pull drawing data into structured drawing.md files (one per sheet) via Notebook LM MCP
2. **GENERATE** — Build the SOW Excel file from the drawing.md files using the rules below
3. **VALIDATE** — Run multi-pass QA checks to flag any hallucination, missing citations, or unverifiable specs

Always run all three phases. Never skip validation.

If a prior SOW exists in the project folder, also run:

4. **COMPARE** — Generate a side-by-side comparison workbook (see Phase 4 below)

## Phase 1: Extraction Prompt

When the user invokes this skill, first confirm:
- Notebook LM notebook name for this project
- Project name/address
- Output folder location
- Whether spec books are included alongside drawings
- **Output mode: one combined workbook, or a separate Excel file per trade** (see Output Mode below)

Then run this extraction prompt against the Notebook LM MCP:

```
Query the Notebook LM notebook "[NOTEBOOK NAME]". For each drawing in the notebook, create a separate .md file named by drawing number (e.g., A001.md, S003.md, P201.md).

Each file must contain:
- Drawing title and sheet number
- Drawing discipline (architectural, structural, MEP, civil, etc.)
- Full scope description of what is shown
- All dimensions and measurements explicitly called out
- All materials, finishes, and specifications referenced (preserve exact spec language as it appears - do NOT normalize)
- All product manufacturer names, model numbers, color callouts, and schedule tags exactly as shown
- Equipment, fixture, door, finish, and hardware schedules if present (preserve table structure)
- All notes, general notes, and keynotes on the sheet
- All detail callouts (Detail X on Sheet Y)
- Cross-references to other drawings or specifications
- Tag references (e.g., T-L-1, D-1, P-101)

For every piece of information extracted, note the exact location it came from:
- Sheet number (e.g., A-201)
- Detail reference if applicable (e.g., 5/A-201)
- Schedule row reference
- Note number reference

If a piece of information cannot be sourced to a specific location, flag it as [UNVERIFIED].

Do NOT calculate, infer, or assume any quantities. Only record quantities explicitly stated on the drawings.

Save all files to the current folder.
```

After extraction completes, verify drawing.md files exist before proceeding to Phase 2.

### Phase 1b: Vision Fallback for Graphical/Bitmap Sheets

Notebook LM's OCR will fail on some sheets not because the content is ambiguous, but because the sheet is fully graphical — a raster table image, a dense equipment schedule, or a CAD sheet with near-zero embedded text (this is common: a real drawing set can have text extraction succeed on the titleblock only and return 0 characters of usable content on the rest of the page). Before flagging one of these sheets as `[UNVERIFIED]` / RFI, run one more step:

1. Identify sheets where Notebook LM extraction returned little or no usable content (titleblock boilerplate only, or an explicit OCR failure).
2. Render that specific sheet to a high-resolution image (200dpi minimum; `pymupdf`'s `get_pixmap` works — see the `ocr-and-documents` skill). Downscale to roughly 2200px on the longest edge if the image is large (some vision endpoints reject very large images).
3. Run a targeted vision extraction pass on that single page image, asking for: sheet number/title, drawing type, every distinct labeled component with dimensions/callouts, and every cross-reference tag to other sheets. This is the same extraction detail Phase 1's Notebook LM prompt asks for — just run against the rendered image instead of the PDF text layer.
4. Merge the vision-extracted content into that sheet's drawing.md file, same citation format as everything else (sheet number, detail reference).
5. Only fall back to `[UNVERIFIED]` / RFI if the vision pass ALSO cannot resolve the content (e.g., the image itself is too low-resolution to read, or genuinely ambiguous).

This has been validated on a real 14-page vector CAD drawing set where text extraction returned near-zero content on 11 of 14 pages: vision-per-page extraction correctly read rebar development-length tables, a steel beam schedule, and equipment schedules (sump pump specs) — exactly the graphical content type that used to be an automatic RFI. See `spikes/001-drawing-indexer` for the validation writeup if it exists in this project's history.

Do not use this as a replacement for Notebook LM extraction generally — it is a targeted fallback for specific sheets that fail, not a parallel extraction pipeline. Keep Notebook LM as the primary extraction path per Phase 1.

## Phase 2: SOW Generation Rules

### Output Mode (ASK THE USER FIRST)

Before generating, ask the user one question:

> "Do you want one combined workbook with all trades, or a separate Excel file for each trade?"

- **Combined:** all subdivisions stacked in a single worksheet ("Scope of Work").
- **Separate per trade:** one workbook per subdivision, each containing only that trade's scope plus its own leveling block. Name each file `[ProjectName]_SOW_[TradeCode]_[YYYY-MM-DD].xlsx`.

Build whichever mode the user selects. Every other rule below applies identically in both modes.

### Output Structure

Single worksheet (Sheet 1: "Scope of Work"). **No QA Report sheet or section is shown in the deliverable.** The QA validation passes (Phase 3) still run internally to catch hallucination and missing citations, but the report is for your own verification only and is never printed into the workbook.

Sheet 1 sections in this order:

1. **Project Header Block** (project name, address, date prepared, prepared by)
2. **Directive Legend** (small reference: F/I, F/O, I/O, Remove, Provide definitions)
3. **Scope of Work** organized by CSI Master Format **subdivisions**, each with its own subcontractor leveling block (see below)
4. **Notes and Clarifications**
5. **Conflicts**
6. **TBD Items**

### Subcontractor Leveling Columns

To the right of the scope of every trade, add **four subcontractor leveling columns** (Columns C, D, E, F). These let the estimator drop multiple sub quotes side by side and compare them. The leveling cells are left blank for manual entry — the SOW doubles as a bid-leveling template, but bids will not always be present, so the layout must read cleanly whether or not any prices are filled in.

Each trade/subdivision section is built like this:

1. **Trade header block — TWO rows tall.** Merge `A:B` across **both** rows and put `[Subdivision Code] — [Title]` in it (medium gray fill, white text, bold, vertically centered). On the right side of this two-row block:
   - **Row 1, Columns C–F:** the sub names, defaulting to `Sub #1`, `Sub #2`, `Sub #3`, `Sub #4` (bold, **centered**, editable — the estimator overwrites them with real sub names).
   - **Row 2, Columns C–F:** the **lump-sum entry cells** — blank currency cells, **centered**, where a sub who bid a single number for the whole trade enters it. There is NO label in the scope column for this row; the two-row merged trade header on the left is what frees column B from needing a placeholder. Give these cells a very light gray fill and a **medium bottom border** so the lump-sum row is clearly divided from the itemized lines below it.
2. **Scope line item rows** — Reference in A, scope item in B (as today), and blank currency cells in C–F for per-line pricing (right aligned).
3. **Trade Total row** (bottom of the section) — `TRADE TOTAL` in the merged A:B cell (bold). Columns C–F each contain a `SUM` formula spanning **from the lump-sum row (row 2 of the header block) down to the last scope line** of that trade, so a sub who bid lump-sum and a sub who bid line-by-line both roll up to a correct trade total. Currency formatted, bold.

**Centering:** sub-name cells and lump-sum cells (the header block) are center aligned. Itemized line-item price cells and the Trade Total cells are right aligned (standard currency).

**All C–F price cells** (lump-sum row, line item rows, Trade Total row) use currency number formatting (`$#,##0.00`). Empty entry cells stay blank (no zero) until a price is typed; empty totals display a dash.

**Show/Hide toggle.** Group columns C–F as an Excel outline group (outline level 1) so the sheet shows a native expand/collapse button above the columns. The estimator clicks it to hide the leveling columns entirely (leaving a clean two-column scope) or show them again. Default state: expanded (shown). No macros are used — this is built-in column grouping so the file stays a plain `.xlsx`.

The Notes, Conflicts, and TBD sections at the bottom span the full width and do not get leveling columns.

### Organization: SUBDIVISIONS, Not Divisions

The scope is organized by CSI Master Format subdivisions. Use the 6-digit MasterFormat number (e.g., 03 30 00 Cast-in-Place Concrete, 09 30 13 Ceramic Tiling).

Subdivision header rows show: `[Subdivision Code] — [Subdivision Title]` (e.g., `09 30 13 — Ceramic Tiling`)

See `references/csi-subdivisions.md` for the full subdivision list and selection logic.

**Mandatory consolidation rules for commercial projects:**

| Do NOT use | Use instead |
|------------|-------------|
| `06 10 00 Rough Carpentry` | `09 20 00 Drywall & Carpentry` |
| `06 20 00 Finish Carpentry` | `09 20 00 Drywall & Carpentry` |
| `09 22 16 Non-Structural Metal Framing` | `09 20 00 Drywall & Carpentry` |
| `09 29 00 Gypsum Board` | `09 20 00 Drywall & Carpentry` |
| Any `xx 05 00 Common Work Results` code | Fold items into the relevant trade subdivision |

All framing, blocking, furring, drywall, taping, and carpentry scope (rough and finish) belongs under `09 20 00 Drywall & Carpentry` for commercial work. Do not split into separate Rough Carpentry or Finish Carpentry sections.

**Electrical consolidation rule:** All electrical scope — wiring, devices, panels, lighting (installation), disconnects, safe-offs, temporary power, fire alarm, low-voltage — belongs under Division 26. Do not use `26 05 00 Common Work Results for Electrical` as a catchall. Assign each item to its specific subdivision (e.g., `26 05 19 Low-Voltage Electrical Power Conductors and Cables`, `26 24 16 Panelboards`, `26 51 13 Interior Lighting`). If a specific subdivision does not fit neatly, use `26 00 00 Electrical` as the fallback — never a Common Work Results code.

### Line Item Format

Every scope line item uses two columns:

| Reference | Scope Item |
|-----------|------------|
| 5/A-201 | F/I T-L-1 Floor Tile [Daltile Model XYZ Charcoal Gray] |
| A-400 | F/I Membrane Roofing [Carlisle Sure-Weld TPO White] |
| 5/A-201, 3/A-301 | F/I T-L-1 Floor Tile [Daltile Model XYZ Charcoal Gray] |
| [UNVERIFIED] | Provide Temporary Power and Lighting |

**Reference Column Rules:**
- If on a detail: `[detail#]/[sheet#]` format (e.g., `5/A-201`)
- If on a plan with no detail callout: just sheet number (e.g., `A-400`)
- If on multiple pages: comma-separated (e.g., `5/A-201, 3/A-301, A-401`)
- If source cannot be identified: `[UNVERIFIED]`

**Scope Item Column Rules:**
- Begin with directive: `F/I`, `F/O`, `I/O`, `Remove`, or `Provide`
- Tag immediately after directive if applicable (e.g., `T-L-1`, `D-1`, `P-101`)
- Description with first letter of every word capitalized (Title Case)
- Specifications in square brackets at the end
- Bracket format: `[Manufacturer Model Color]` in that order
- If no spec called out on drawings: `[Not Specified]`
- Preserve exact spec language as it appears on drawings — do not normalize
- Industry-standard abbreviations OK (HVAC, MEP, etc.) EXCEPT CSI codes which must match Master Format exactly

### Directive Definitions

| Directive | Use For |
|-----------|---------|
| F/I | Furnish and Install |
| F/O | Furnish Only |
| I/O | Install Only |
| Remove | Demolition |
| Provide | Services, shop drawings, mockups, non-material work |

**Do NOT stack a directive onto a scope item that already contains one.** If the scope item's action word is inherently a directive (e.g., `Replace`, `Refinish`, `Patch`, `Repair`, `Seal`, `Flash`), use that word as-is — do not prepend F/I, F/O, or I/O. Examples:

- Correct: `Replace Existing CMU at Modified Opening`
- Wrong: `F/I Replace Existing CMU at Modified Opening`
- Correct: `Patch and Repair Existing Concrete Slab`
- Wrong: `Provide Patch and Repair Existing Concrete Slab`

Only prepend a directive when the scope item does not already begin with an action word that implies one.

**Painting scope:** Never write `F/I Paint`. Painting is always written as `Prep and Paint [Surface] [Spec]` (e.g., `Prep and Paint Gypsum Board Walls [Benjamin Moore Regal Select Eggshell]`). `Prep and Paint` is its own action phrase — do NOT prepend F/I, F/O, or I/O to it. This applies to all painting and coatings line items (walls, ceilings, doors/frames field-painted, etc.).

### Trade-Specific Scope Splitting Rules

These rules are mandatory and override what may be shown on drawings. See `references/trade-rules.md` for full examples.

**HVAC Demolition:** HVAC sub does drain down/disconnect appropriate to equipment. Demo sub removes. (HVAC sub may remove on case-by-case basis.)

**Sprinkler Demolition:** Sprinkler sub does drain down/disconnect. Demo sub removes.

**Electrical Demolition:** Electrical sub does disconnects and safe-offs (always include for renovations even if not on drawings). Demo sub removes. Always include "Provide Temporary Power and Lighting" for renovations.

**Doors, Frames, Hardware:** F/O in Division 08 subdivisions. I/O in `09 20 00 Drywall & Carpentry`.

**Bathroom/Toilet Accessories:** F/O in Division 10 subdivisions. I/O in `09 20 00 Drywall & Carpentry`.

**Lighting Fixtures:** F/O in the appropriate Division 26 lighting subdivision (e.g., `26 51 13 Interior Lighting`). I/O as a companion line item in the same `26 51 13` section (or relevant lighting subdivision). Do NOT put lighting fixture installation in a separate carpentry or general section.

**Plumbing Fixtures (F/O):** Always pair with corresponding I/O rough-in line item in the appropriate Division 22 subdivision. Do not use `22 05 00 Common Work Results` — assign to the specific plumbing subdivision.

**Owner-Supplied Materials:** Prefix with `I/O Owner-Supplied`. Always include companion delivery acceptance and coordination line item.

**No Common Work Results codes:** Never use `xx 05 00` codes (22 05 00, 23 05 00, 26 05 00, etc.). Assign all items to specific trade subdivisions. Scope that would have gone to Common Work Results belongs in the primary trade subdivision for that discipline (e.g., pipe insulation goes in `22 07 00 Plumbing Insulation`, disconnects and safe-offs go in `26 05 19` or `26 00 00 Electrical`).

### Auto-Inserted Line Items

**Sprinkler subdivisions (21 13 00 etc.):** Provide Shop Drawings, Provide Hydrostatic Testing, Provide Permits, Provide Inspections, Provide Signoff. (No cost references.)

**Always insert "Provide Shop Drawings" for these trades:**
- Architectural Metalwork and Glass
- Millwork
- HVAC
- Sprinkler

**Drawing/spec dependent (insert if called out):**
- Composite Materials
- Plumbing (case by case)

**Per-trade boilerplate line items — applied CONDITIONALLY, never blanket:**

Do NOT drop the same boilerplate lines on every subdivision. Apply them by trade type:

- **Cleanup** ("Provide Cleanup of Own Work into Centralized Container Provided by GC") — add to every trade that performs **on-site work** (install or demolition). Not on furnish-only material trades.
- **Testing** — add ONLY to trades that actually test or commission something: the wet / air / life-safety systems (sprinkler hydrostatic, plumbing pressure & disinfection, HVAC air/water balancing, fire-alarm acceptance) and a flooring slab-moisture / RH test. Prefer the **specific, drawing-sourced** test line in the trade's own scope over a generic "Provide All Testing" catch-all. Do NOT put any testing line on finish / architectural trades (painting, ceilings, tile, base, doors, glazing, millwork, specialties, shades) — they have nothing to test.
- **Permits** — JURISDICTION-DRIVEN. Determine which trades pull their **own** permit from the project location, and put the permit line ONLY on those. Every other trade falls under the GC's overall **building / alteration permit** (state that once in the Notes section — do not repeat it per trade).
- **Pure furnish-only (F/O) material trades** (e.g., Frames `08 11 13`, Doors `08 14 16`, Hardware `08 71 00`, Appliances `11 31 00`): add **NONE** of the three — the supplier only delivers material; it does not install, test, clean up, or permit. The install/test/cleanup happens under the installing trade (e.g., doors installed under `09 20 00`).

**Permit-by-jurisdiction rule.** Most U.S. municipalities (including Connecticut / Stamford): the **GC pulls the building/alteration permit** covering demolition and all architectural & finish trades (concrete, drywall & carpentry, ceilings, flooring, tile, painting, millwork, glazing, door *installation*, specialties, shades). The trades that pull their **own separate permit** are the licensed MEP + fire trades: **Electrical, Plumbing, Mechanical (HVAC), Fire Suppression / Sprinkler, and Fire Alarm.** Confirm against the stamped MEP/FP sets — each typically states its contractor obtains permits. (Dense jurisdictions such as NYC file more trades separately and may require a standalone demolition permit — adjust the permit-pulling set to the actual AHJ before generating.) When one sub bids a trade split across several subdivisions (e.g., plumbing across `22 11 00 / 22 13 00 / 22 40 00`, electrical across `26 24 16 / 26 27 26 / 26 51 13`), put the permit line **once** on the lead subdivision, not on each. If a subdivision already carries a drawing-sourced permit/inspection line (sprinkler sign-off, HVAC filing, fire-alarm FD inspection), do not add a duplicate generic permit line.

Leave the Reference column **blank** (empty cell) for these boilerplate/auto-inserted line items. Do NOT write `[UNVERIFIED]` next to them — `[UNVERIFIED]` is only for scope items that purport to cite a specific drawing location but that citation could not be verified. Boilerplate requirements are not drawing-sourced and need no citation.

**Coordination items:** Include where genuinely required as part of the relevant trade scope.

**Existing Conditions Protection:** Place at the BOTTOM of the relevant trade subdivision section.

### Conflict Detection

If the same item appears with conflicting specifications:
- Use the FIRST spec encountered in the actual SOW line item
- List ALL conflicting versions in the "Conflicts" section at the bottom
- Format: `Item Name | Spec A (Source) vs. Spec B (Source) vs. Spec C (Source)`

### TBD Items

Any item shown as TBD on the drawings:
- Include in SOW with `[Not Specified]` or `[TBD]`
- Add to dedicated "TBD Items" section at the bottom
- Format: `Item Name | What is TBD | Source Page`

### What NOT to Include

- Quantities (unless explicitly called out on drawings/schedules)
- Cost references or pricing
- Submittal language (assumed)
- Cut sheet language (assumed)
- Schedule dependencies or sequencing
- Quality standard language ("per industry standards," "per GC approval")
- Warranty/guarantee language
- Substitution language
- Change order trigger language
- Standard general notes footer (30-day pricing, normal hours, etc.)
- Allowance line items
- As-built documentation language

### Notes and Clarifications Section

Two sub-sections at bottom of SOW:

**Standard Clarifications** (always included): See `references/standard-clarifications.md`

**Drawing-Specific Clarifications:** Pulled from drawing.md files where ambiguity exists. Format: `Item | Clarification Needed | Source Page`

## Phase 3: QA Validation Passes

Run these passes IN ORDER before Excel output:

**Pass 1 — Citation Verification:** Every line item has a Reference column value that exists in drawing.md files and matches what those files say. Failures: mark `[UNVERIFIED]`.

**Pass 2 — Spec Verification:** Every bracketed spec appears verbatim in drawing.md files at cited location. Failures: change to `[Not Specified]` and add to TBD section.

**Pass 3 — Omission Check:** Reverse query against drawing.md files to find any scope item in drawings but missing from SOW. Add any missed items.

**Pass 3.5 — Cross-Sheet Contradiction Check:** For any object/component/system that appears on 2+ sheets (a component referenced in more than one drawing.md file), compare its stated disposition across every appearance — existing-to-remain vs. remove/replace vs. repair, or conflicting dimensions/specs for the same tagged item. Real drawing sets do contain genuine contradictions (e.g., one sheet marking an item "DO NOT DISTURB" while another calls for its removal) — these are not extraction errors, they are conflicts in the source documents themselves, and a human estimator needs to see them before pricing goes out. Any contradiction found here gets logged to the **Conflicts** section using the existing format (`Item Name | Spec A (Source) vs. Spec B (Source)`), not silently resolved by picking one. This pass is a natural extension of the existing Conflict Detection rule (same item, different specs) — the difference is triggering the check by cross-referencing an item across every sheet it appears on, not just noticing a conflict when writing a single line item.

**Pass 4 — Trade Split Audit:** Confirm trade splitting rules applied (HVAC/Sprinkler/Electrical demo splits, Doors F/O Div 8 + I/O Div 9, Bathroom Accessories F/O Div 10 + I/O Div 9, Plumbing F/O paired with I/O rough-in, auto-shop drawings, Owner-Supplied paired with delivery coordination).

**Pass 5 — Format Audit:** Every line item has valid directive, Title Case, bracket spec or `[Not Specified]`, tag positioning, Reference populated.

**Pass 6 — Final Validation Report:** Generate a QA report counting line items, [UNVERIFIED] citations, [Not Specified] specs, conflicts, TBDs, trade splits applied, and auto-inserted items. **This report is for internal validation only — do NOT add it to the Excel workbook.** Use it to confirm the SOW is clean, then present a short summary of any flags to the user in chat instead.

## Phase 4: SOW Comparison Chart

When a prior-version SOW `.xlsx` exists in the project folder, generate a comparison workbook automatically after the current SOW is finalized.

### When to Generate

- Any time there is more than one `*_SOW_*.xlsx` file in the project folder
- When the user explicitly requests a comparison ("compare these two SOWs", "what changed")
- Always generate after a re-extraction / full fresh run so the user can see exactly what changed from the prior version

### Output File

Save as: `SOW_Comparison_[YYYY-MM-DD].xlsx` in the project root.

### Script

Use `.sow_work/compare_sow.py` (or generate a fresh one using the template below). Run via stdin piping to avoid Dropbox file locks:

```
py - < .sow_work/compare_sow.py
```

### Workbook Structure (2 sheets)

**Sheet 1 — Summary**

Division-level comparison table with columns:

| CSI Code | Division Title | May-06 Items | May-15 Items | Added | Removed | Status |

Status values: `NEW DIVISION` / `MODIFIED` / `REMOVED DIVISION` / `UNCHANGED`

Include a totals row and a legend at the bottom.

**Sheet 2 — Line Item Detail**

Full side-by-side comparison of every line item across both versions. Columns:

| REF (Prior) | SCOPE ITEM — Prior | REF (Current) | SCOPE ITEM — Current | STATUS |

Status values per row: `ADDED` / `REMOVED` / `UNCHANGED`

Group rows under division header rows (medium gray band showing the CSI code and title). Separate divisions with a small blank spacer row.

### Color Coding (strict — matches SOW palette)

| Status | Row Fill | Status Text Color |
|--------|----------|------------------|
| ADDED / NEW DIVISION | `#D6F0D6` (light green) | `#1E6B1E` (dark green) |
| REMOVED / REMOVED DIVISION | `#FFD6D6` (light red) | `#8B0000` (dark red) |
| MODIFIED | `#FFF0C8` (light amber) | `#7A5200` (dark amber) |
| UNCHANGED | `#F5F5F5` (very light gray) | `#555555` (medium gray) |

Header band, title band, and division rows use the same `#1A1A1A` / `#4D4D4D` charcoal palette as the SOW.

### Fuzzy Match Logic

When comparing line items across versions, normalize before matching:
- Strip all bracketed spec text (e.g., `[Daltile Model XYZ]`)
- Collapse whitespace, lowercase
- Match on normalized text — a bracket spec update does NOT count as a new item, it counts as UNCHANGED

This avoids false positives from minor spec edits or bracket reformatting.

### What to Show the User After Generating

Print a concise summary:
- Total items: prior → current (net change)
- Total divisions: prior → current (net change)
- List all NEW DIVISION entries with item counts
- List all REMOVED DIVISION entries with item counts
- List MODIFIED divisions with `+X added / -Y removed` per division
- Count of UNCHANGED divisions

---

## Excel Output: Professional Formatting Requirements

Use the script at `scripts/build_sow_xlsx.py` to generate the Excel file. The script enforces:

### Visual Design Standards

**Color Palette (STRICT — no other colors):**
- Pure White: `#FFFFFF` (backgrounds)
- Black: `#000000` (text, primary borders)
- Charcoal Gray: `#3A3A3A` (header backgrounds, strong dividers)
- Medium Gray: `#7A7A7A` (subdivision header backgrounds)
- Light Gray: `#E8E8E8` (alternating row shading, light borders)
- Very Light Gray: `#F5F5F5` (subdued backgrounds)

**Typography:**
- Primary font: **Calibri** (modern, clean sans-serif, professional standard)
- Project Title: 18pt, Bold, Black
- Section Headers (Notes, Conflicts, TBD): 14pt, Bold, White text on Charcoal Gray fill
- Subdivision Headers: 11pt, Bold, White text on Medium Gray fill
- Line Items: 10pt, Black, regular weight
- Reference Column: 10pt, Black, slightly lighter (use Charcoal Gray text on light gray fill for visual distinction)
- Footer/Legend: 9pt, Italic, Medium Gray

### Layout Specifications

**Column Widths:**
- Column A (Reference): 18 characters
- Column B (Scope Item): 60 characters (narrowed from 80 to make room for leveling columns on one page)
- Columns C–F (Sub #1–Sub #4 leveling): 16 characters each
- Set print area so all six columns fit on one page wide

**Row Heights:**
- Project Title row: 30pt
- Header rows: 22pt
- Subdivision header rows: 20pt (each of the two trade-header rows)
- Line item rows: **compute the height to fit the wrapped text — 30pt minimum, growing ~15pt per additional wrapped line.** Do NOT write a flat fixed height: any explicit height you set disables Excel's double-click auto-fit, so a fixed 18pt clips every scope item that wraps to two or three lines and forces the estimator to hand-fix rows. Enable wrap on BOTH the Reference and Scope columns, then set `height = max(30, lines*15)` where `lines = max(ceil(len(scope_text)/60), ceil(len(reference)/17))` (60 = Scope column width, 17 = Reference column width; deliberately conservative chars-per-line so rows are never too short). Example helper:
  ```python
  import math
  def calc_height(specs, min_h=30, line_pt=15):   # specs = [(text, chars_per_line), ...]
      lines = max([1] + [math.ceil(len(str(t))/cpl) for t, cpl in specs if t])
      return max(min_h, lines*line_pt)
  # line item:  ws.row_dimensions[r].height = calc_height([(reference,17),(scope,60)])
  ```
- Notes / Conflicts / TBD rows (merged full width): merged cells NEVER auto-fit in Excel, so compute their height the same way with `calc_height([(text,130)])` (130 ≈ characters per line across the merged A–F width). Minimum 30pt.

**Borders:**
- Outer table border: Medium Black
- Section dividers: Medium Charcoal Gray
- Line item separators: Thin Light Gray
- No borders inside header text blocks

**Alignment:**
- Reference column: Left aligned, vertically centered
- Scope Item column: Left aligned, vertically centered, wrap text enabled
- Sub #1–Sub #4 header block (sub-name cells and lump-sum cells): **center** aligned, vertically centered
- Itemized line-item price cells and Trade Total cells (C–F): right aligned, vertically centered
- Headers: Left aligned (no centering — looks more professional for documents)

**Leveling column visibility:** Columns C–F are grouped as an Excel outline (level 1) so a native show/hide toggle button appears above them. Default expanded.

**Page Setup:**
- Orientation: Landscape (needed so all six columns — scope plus four leveling columns — fit across one page)
- Margins: Narrow (0.5" all sides)
- Print scaling: **Fit to 1 page wide** (height runs to as many pages as the line count needs; the goal is that columns never spill onto a second page sideways)
- Header: Project Name (left) | Page X of Y (right)
- Footer: "Confidential - Montana Contracting" (center) | Date (right)
- Repeat the project header rows and the column/sub-name header on every printed page

**Freeze Panes:** Freeze through the column header row (row 7) so the project info and the Reference / Scope Item / Sub #1–#4 headers stay visible when scrolling.

### Layout Pattern (Top to Bottom)

1. **Row 1:** Project Title (merged A1:F1, 18pt Bold)
2. **Row 2:** Project Address (merged A2:F2, 11pt regular)
3. **Row 3:** Date Prepared | Prepared By (in A:B), remainder of row blank
4. **Row 4:** Empty spacer with bottom border
5. **Row 5:** Directive Legend (merged A5:F5, 9pt italic, light gray fill: "F/I = Furnish and Install | F/O = Furnish Only | I/O = Install Only | Remove = Demolition | Provide = Services")
6. **Row 6:** Empty spacer
7. **Row 7:** Column Headers — "Reference" (A) | "Scope Item" (B) | "Sub #1" (C) | "Sub #2" (D) | "Sub #3" (E) | "Sub #4" (F) (Bold, charcoal gray fill, white text). The Sub #1–#4 labels here are the default header; each trade section also restates them so they can be overwritten per trade.
8. **Rows 8+:** Subdivision sections — each starts with its two-row trade header block (trade name merged on the left across both rows; Sub #1–#4 names on row 1 and lump-sum entry cells on row 2 of the right side), then line items, then the Trade Total row (see Subdivision Section Pattern)
9. **After all subdivisions:** Notes and Clarifications section header, then content (full width, no leveling columns)
10. **Conflicts section header, then content**
11. **TBD Items section header, then content**

### Subdivision Section Pattern

```
[Empty row]
[Trade header block — TWO rows tall]:
    A:B  (merged across BOTH rows) = "09 30 13 — Ceramic Tiling"  (Medium Gray fill, white text, bold, 11pt, vertically centered)
    Row 1, C:F = "Sub #1"  "Sub #2"  "Sub #3"  "Sub #4"  (bold, CENTERED, light gray fill — editable)
    Row 2, C:F = blank lump-sum entry cells (CENTERED, currency $#,##0.00, very light gray fill,
                 MEDIUM BOTTOM BORDER to divide the lump-sum row from the lines below)
[Line item row]:  A = Reference | B = Scope Item | C:F = blank cells, currency, right aligned
[Line item row]
[Line item row]
...
[Trade Total row]:
    A:B (merged) = "TRADE TOTAL"  (bold)
    C:F = =SUM(from the lump-sum row [row 2 of header block] down to the last line item row), currency, bold, right aligned
[Empty row]
```

The two-row merged trade header is what lets the lump-sum row exist without a placeholder label in the scope column. The medium border under the lump-sum cells makes that row read clearly as the lump-sum price, separate from the itemized line prices.

The `SUM` in each Trade Total cell spans from the lump-sum row through the last scope line of that trade, so whether a sub bids one lump number or itemizes line by line, their column rolls up to the correct total.

Group columns C:F as an outline (level 1) so a native show/hide button sits above them; default expanded.

Apply alternating row shading (very light gray) to the scope line item rows within each subdivision for readability. Do not shade the trade header block or Trade Total row.

### Section Headers (Notes, Conflicts, TBD, QA)

Section headers use:
- Charcoal Gray (#3A3A3A) fill
- White text
- 14pt Bold
- Full width merge across columns A and B
- Heavy black bottom border

## File Output

- **Combined mode:** save as `[ProjectName]_SOW_[YYYY-MM-DD].xlsx`
- **Separate-per-trade mode:** save one file per trade as `[ProjectName]_SOW_[TradeCode]_[YYYY-MM-DD].xlsx` (e.g., `Kirkside_SOW_093013_2026-06-17.xlsx`)

Save to the user-specified output folder.

## Invocation Pattern

When user invokes this skill:

1. Confirm Notebook LM notebook name, project details, and **output mode (combined workbook vs. separate file per trade)**
2. Check for any prior `*_SOW_*.xlsx` files in project folder (note for comparison step)
3. Run Phase 1 extraction (write drawing.md files via NotebookLM — see Extraction Guidance below), running the Phase 1b vision fallback on any sheet that returns no usable content
4. Verify `.md` files exist and `sow_nbml_capture.txt` has been saved
5. Run Phase 2 generation (build SOW from `.md` files via `gen_sow.py`)
6. Run all 7 QA validation passes via `qa.py` — **internal verification only; the QA report is not written into the workbook**
7. Generate Excel output via `scripts/build_sow_xlsx.py` (one workbook, or one per trade, per the chosen output mode — each trade section includes its four subcontractor leveling columns and Trade Total)
8. If a prior SOW exists, generate comparison workbook via `compare_sow.py`
9. Present file(s) to user with a short chat summary of any QA flags and comparison highlights

## NotebookLM Extraction Guidance

### Batching Strategy

Do NOT run one narrow query per drawing sheet — that wastes browser round-trips and can hit NotebookLM response limits. Instead, batch by discipline group (4 batches covers a typical set):

- **Batch 1:** General / Code / Life Safety / Site (Cover, GN, AS sheets + Attachment B specs)
- **Batch 2:** All Architectural sheets (demo plans, proposed plans, RCP, elevations, wall sections, partition details, ceiling details, window/door schedule, interior elevations, millwork)
- **Batch 3:** All Finish, Interior Design, and Schedule sheets (finish plan, hardware schedule, finish schedule, door schedule)
- **Batch 4:** All MEP + Structural sheets (M, P, E, S, FA sheets)

Each batch prompt asks NotebookLM to extract all keynotes, schedules, notes, model numbers, dimensions, cross-references, and general notes verbatim with source-page citations. Ask it to flag anything it cannot read as `[UNVERIFIED]`.

### Capturing NotebookLM Responses

NotebookLM's SPA virtualizes the chat — `body.innerText` only shows ~60K chars regardless of response length. Long responses (Batch 2+ on complex projects) will be silently truncated if you only read `body.innerText`.

**Reliable capture method:**
1. After each batch response, run a deep recursive DOM walk (piercing shadow roots) to build full text in `window.__SOW`
2. Blob-download `window.__SOW` to a local file via JS: `new Blob([window.__SOW], {type:'text/plain'})` — this lands the file in Chrome's configured download directory
3. Parse the downloaded file to extract each batch's answer (use batch boundary markers in the prompt to make parsing reliable)
4. Assemble all batches into `sow_nbml_capture.txt` and `.sow_work/batches_clean.json`

### Graphical Sheets (MEP Equipment Schedules, Panel Schedules)

MEP sheets that are fully graphical (raster table images, no selectable text) cannot be read by any text-only extraction tool — not pdftotext, not PyMuPDF, not NotebookLM OCR when the table is a high-density bitmap. Before marking these `[UNVERIFIED]` / RFI, run the **Phase 1b Vision Fallback** (see above): render the specific sheet to an image and run a targeted vision extraction pass on it. This has recovered real data (equipment schedules, rebar tables, beam schedules) on sheets that were previously unrecoverable by text extraction alone. Only fall back to `[UNVERIFIED]` / RFI if the vision pass also cannot resolve the content. Acceptable note when it truly can't be resolved: "HVAC equipment schedule could not be extracted — RFI to engineer required."

### Python Execution on Windows / Dropbox

Dropbox sync can lock freshly-written `.py` files, causing `PermissionError` if you try to run them by path immediately after writing. Always run scripts via stdin piping instead:

```
py - < .sow_work/gen_sow.py
py - < .sow_work/qa.py
py - < .sow_work/compare_sow.py
```

Use `py` (not `python`) on Windows environments where `python` is an alias to the Microsoft Store redirect.

### PyMuPDF / AV Interference

On managed Windows machines, PyMuPDF (`import fitz`) may be blocked by AV/EDR even after a successful `pip install` — `PermissionError` on `fitz/__init__.py`. If this happens, do not attempt workarounds (venv in TEMP, user install, etc.) — they will all be blocked by the same policy. Use `pdftotext` (poppler) for text-selectable PDF pages instead, and NotebookLM for graphical pages.

## Artifact Retention

These files are **permanent project deliverables** — never delete them during cleanup:

| File | Purpose |
|------|---------|
| `sow_nbml_capture.txt` | Full raw NotebookLM extraction capture — audit trail |
| `.sow_work/batches_clean.json` | Parsed batch answers — source of truth for reconstruction |
| `.sow_work/gen_sow.py` | SOW data generator for this project |
| `.sow_work/qa.py` | QA validator for this project |
| `.sow_work/compare_sow.py` | Comparison chart generator for this project |
| `.sow_work/nbml/batch*.md` | Hand-curated batch captures (if any) |
| `drawing_extraction.md` | Assembled extraction from all batches |
| `sow_data.json` | Structured SOW data |
| `*_SOW_*.xlsx` | All SOW versions (prior versions preserved, not overwritten) |
| `SOW_Comparison_*.xlsx` | Comparison workbooks |
| `.sow_backups/` | Timestamped backups of prior run artifacts |

Only clean up genuinely redundant scratch — e.g., re-downloaded byte-identical copies of source files. If unsure whether something is wanted, ask before deleting.

## Reference Files

- `references/csi-subdivisions.md` — Full CSI Master Format subdivision list with selection logic
- `references/standard-clarifications.md` — Boilerplate clarifications text
- `references/trade-rules.md` — Detailed trade scope-splitting examples

## Scripts

- `scripts/build_sow_xlsx.py` — Excel generation with all professional formatting baked in
- `scripts/recalc.py` — Formula recalculation (from xlsx skill)
- `.sow_work/gen_sow.py` — Project-specific SOW data generator (lives in project folder, not skills folder)
- `.sow_work/qa.py` — Project-specific QA validator (lives in project folder)
- `.sow_work/compare_sow.py` — Comparison chart generator; reads two `*_SOW_*.xlsx` files from the project root and outputs `SOW_Comparison_[date].xlsx`. Lives in project `.sow_work/` folder.

## Critical Rules Summary

1. NEVER calculate or infer quantities
2. NEVER normalize spec language — preserve exact drawing text
3. NEVER skip a QA validation pass
4. NEVER output without citation in Reference column (use [UNVERIFIED] if needed)
5. NEVER include cost references in scope
6. NEVER use colors outside the black/gray/white palette
7. ALWAYS organize by CSI subdivision (6-digit), not top-level division
8. ALWAYS apply trade splitting rules even if drawings don't show them
9. ALWAYS run omission check (Pass 3) before final output
9b. ALWAYS run the cross-sheet contradiction check (Pass 3.5) before final output — flag conflicting dispositions/specs for any item appearing on 2+ sheets to the Conflicts section, never silently resolve
9c. ALWAYS attempt the Phase 1b vision fallback (render sheet to image, run targeted vision extraction) on graphical/bitmap sheets that return no usable text before falling back to [UNVERIFIED] / RFI
10. ALWAYS run the QA validation passes internally, but NEVER print the QA Report into the workbook — summarize flags in chat instead
11. ALWAYS use [Not Specified] when spec is missing — never invent
12. ALWAYS list conflicts in the Conflicts section, never silently pick one
13. ALWAYS use Calibri font, professional spacing, and the strict color palette

13. ALWAYS generate a comparison workbook when a prior SOW version exists in the project folder
14. NEVER delete `sow_nbml_capture.txt`, `.sow_work/`, or any SOW Excel version — treat all as permanent deliverables
15. ALWAYS run scripts via `py - < script.py` (stdin piping) on Windows/Dropbox to avoid file lock errors
16. ALWAYS batch NotebookLM queries by discipline group (4 batches) — never one query per sheet
17. NEVER invent HVAC/electrical schedule data that cannot be read — flag as [UNVERIFIED] and note as RFI
18. NEVER prepend F/I, F/O, or I/O to a scope item that already begins with its own action directive (Replace, Patch, Refinish, etc.)
19. NEVER use Rough Carpentry (06 10 00) or Finish Carpentry (06 20 00) on commercial projects — all carpentry, framing, and drywall goes under 09 20 00 Drywall & Carpentry
20. NEVER use any Common Work Results cost code (xx 05 00) — assign all items to specific trade subdivisions
21. ALWAYS place all electrical scope under Division 26; never scatter electrical items into Common Work Results codes
22. ALWAYS split lighting fixtures as F/O + I/O within the Division 26 lighting subdivision
23. NEVER write [UNVERIFIED] on boilerplate auto-inserted line items — leave their Reference cell blank
24. ALWAYS ask the user up front whether they want one combined workbook or a separate Excel file per trade
25. ALWAYS build the trade header as a TWO-row-tall merged A:B block, with Sub #1–#4 names on row 1 and the lump-sum entry cells on row 2 of the right side; never put a lump-sum label in the scope column
26. ALWAYS center the sub-name and lump-sum cells, give the lump-sum row a medium bottom divider border, and currency-format ($#,##0.00) every price cell (blank entry cells stay empty; empty totals show a dash)
27. ALWAYS group columns C–F as an outline so a native show/hide toggle button hides or shows the leveling columns; default expanded
28. ALWAYS set the sheet to landscape, fit-to-1-page-wide so the scope plus four leveling columns never spill sideways onto a second page
29. ALWAYS write painting scope as "Prep and Paint [Surface] [Spec]" — never "F/I Paint"
30. ALWAYS compute and bake in line-item row heights (min 30pt, +~15pt per wrapped line) with wrap enabled on the Reference and Scope columns, and compute heights for the merged Notes/Conflicts/TBD rows too — NEVER write a flat fixed row height (it disables Excel auto-fit and clips wrapped scope items, forcing manual row-by-row fixing)
31. NEVER blanket-insert boilerplate on every trade — every auto-inserted line (permit, testing, cleanup, shop drawings) must be APPLICABLE to that trade and project location. **Permits:** the GC's building/alteration permit covers demolition + all architectural/finish trades; only licensed trades that file their own permit get a permit line (default CT / most U.S. municipalities: Electrical, Plumbing, HVAC, Fire Sprinkler, Fire Alarm); state GC building-permit coverage once in the Notes section. **Testing:** only trades that actually test/commission (sprinkler, plumbing, HVAC, life-safety, flooring moisture) — never on finish trades. **Cleanup:** every on-site working trade. **Furnish-only material trades** (doors, frames, hardware, appliances) get NO permit/cleanup/testing boilerplate at all.

The goal of this skill is zero hallucination AND a polished, professional document. If a fact cannot be verified to a drawing source, it must be flagged. Better to flag a real item as [UNVERIFIED] than silently include an invented one.
