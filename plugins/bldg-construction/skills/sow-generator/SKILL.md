---
name: sow-generator
description: Generates construction Scopes of Work from drawings and spec books, in Excel and PDF, in one of two modes - scope only (zero quantities, zero pricing) or quantified and priced with four subcontractor bid-leveling columns per trade. Use whenever the user mentions creating a scope of work, SOW, scoping a project or a trade, scoping a sub, leveling sub bids, a "SOW with pricing", a quantified bid-leveling sheet, a takeoff turned into a leveling document, or breaking a project into trades by CSI. Also trigger when the user references drawing.md files or index.json, has uploaded construction drawings or specifications, or mentions Montana Contracting / BLDG Estimating scope output. Enforces directive language (F/I, F/O, I/O, Remove, Provide), bracket spec format, citation tracking, trade-splitting rules, conflict and TBD detection, six QA passes that prevent hallucination, and a landlord/tenant responsibility split. For a priced estimate against a cost database use conceptual-estimate.
---

# SOW Generator

Scope of work generation for Montana Contracting and BLDG Estimating. One rulebook, two
output modes, Excel and PDF from the same data file, and zero tolerance for hallucination.

This skill was two skills. `sow-generator` held the construction knowledge and wrote a
two-column scope; `generate-sow-with-pricing-and-leveling` held the workbook craft and
wrote a quantified leveling sheet with none of the rules. Each carried its own Excel
builder. They are merged because the second one's workflow already called the first one at
its step 2: they were never rivals, they were a rulebook and a renderer filed apart.

## The two modes

`mode` in the data file picks the grid. Nothing else changes.

| | `scope` | `quantified` |
|---|---|---|
| Columns | Reference, Scope Item, [Resp.], gutter, Sub #1-4 | adds Qty, Unit Type, Unit Rate, Total |
| Needs a takeoff | No | Yes |
| Close-out | SUBTOTAL across the sub columns | SUBTOTAL, markup ladder, TOTAL |
| Goes to | Subs, in a bid package, before anything is counted | The GC, to level bids against our own number |

**Ask which one at step 0.** The default is `quantified` only because most requests carry a
takeoff. A scope with no takeoff belongs in `scope` mode; forcing it into `quantified`
renders every line red and tells the reader nothing.

`landlord_tenant: true` adds a Resp. column in either mode.

## What gets produced

Excel, always: `[Project]_SOW_[YYYY-MM-DD].xlsx`

| Sheet | Audience | Contents |
|---|---|---|
| **Scope of Work** | GC and subs | Trade blocks, scope, four sub columns, close-out, then Conflicts and TBD Items |
| **SOV** | GC | Trade roll-up, low bid flagged, the same ladder mirrored |
| **Notes & Clarifications** | GC | Exclusions and clarifications in estimator voice |
| **Quantity Basis** | internal, **hidden** | Per-line basis for anything derived or unquantified |

PDF, on request: `[Project]_SOW_[YYYY-MM-DD].pdf`. A typeset editorial document from the
same data file: cover, contents, scope by trade, appendix of notes, conflicts and TBD.
With `--responsibility Landlord` or `Tenant` it writes the split version.

## Workflow

```
0. CONFIRM   -> project, address, prepared by, output folder, MODE, landlord/tenant,
                combined workbook or one file per trade
1. INDEX     -> drawing-index, --validate clean. Never re-implement extraction here
2. SCOPE     -> Phase 2 rules: directives, bracket specs, trade splits, boilerplate
3. QUANTIFY  -> quantified mode only. Reuse the internal takeoff if one exists, else
                construction-takeoff. Reconcile against the schedules. Never invent
4. QA        -> the six passes in Phase 3. Internal only, never printed into a deliverable
5. ASSEMBLE  -> sow_data.json per references/workbook-spec.md
6. BUILD     -> python scripts/build_sow_xlsx.py sow_data.json out.xlsx
                python scripts/build_sow_pdf.py  sow_data.json out.pdf     (if wanted)
7. VERIFY    -> render and LOOK at it. Borders, clipping, page width, the gutter
8. COMPARE   -> if a prior SOW is in the folder, Phase 4
9. DELIVER   -> SendUserFile, then into the job folder
```

**Step 7 is not optional.**

```bash
soffice --headless --convert-to pdf out.xlsx --outdir /tmp/chk
```

Read back the first page, one dense page, the ladder and the notes sheet. Border defects,
clipped rows and a table running off the page are invisible in the cell data and obvious in
the render.

> If `soffice` is missing or is a broken shim, say so rather than skipping the step
> silently, and check the grid structurally instead: column headers per mode, every money
> column on TOTAL holding a formula, and no number written into a text column.

## Phase 1: Index the drawings (delegated)

**Extraction is not this skill's job.** Run `drawing-index` and consume its output. One
extraction pipeline in one place is why this skill does not drift; three copies of one
pipeline is how the earlier SOW skills ended up 568 divergent lines apart.

1. Reuse a current `index.json` if the folder has one. Do not re-extract.
2. Otherwise invoke `drawing-index` against the drawing folder.
3. **Gate, do not proceed until it passes:**

```bash
python <drawing-index>/scripts/build_index.py drawings/index.json --validate
python <drawing-index>/scripts/build_index.py drawings/index.json --stats
```

`--validate` must exit 0. A non-zero exit means a placeholder project name, an uncited
spec, a citation pointing at a sheet not in the set, or a quantity with no basis. Every one
becomes a defect in the SOW.

Check `--stats` for sheets no element cites. Those are either genuinely scope-free or an
extraction gap, and a missed sheet is missed scope. Confirm which.

**If `index.json` cannot be built**, stop and say so rather than generating scope from
memory or from a chat-attached PDF. A SOW with no traceable citations is the failure mode
this skill exists to prevent.

## Phase 2: Scope generation rules

### Organization: trade blocks, CSI codes in the header

**A trade block is the unit, and the CSI subdivisions it covers are listed in its header.**

This is a deliberate change from the older rule, which organized by 6-digit subdivision.
Leveling is per sub, and a sub bids a trade, not a subdivision. Splitting Drywall from
Metal Framing into two blocks hands one bidder two totals that reconcile nowhere. The old
rule was already pulling this way through its own consolidation table.

```
DRYWALL & CARPENTRY  --  CSI 09 20 00, 09 29 00, 09 72 00
```

Use the 6-digit MasterFormat number in the header list. See `references/csi-subdivisions.md`
for the full list and selection logic.

**Mandatory consolidations for commercial work:**

| Do NOT use | Use |
|---|---|
| `06 10 00` Rough Carpentry, `06 20 00` Finish Carpentry, `09 22 16` Metal Framing, `09 29 00` Gypsum Board | **Drywall & Carpentry** |
| Millwork, Casework, architectural woodwork | **Custom Millwork** |
| Any `xx 05 00` Common Work Results code | the specific trade subdivision |

All framing, blocking, furring, drywall, taping and carpentry belongs in Drywall &
Carpentry on commercial work.

**Electrical:** everything under Division 26. Wiring, devices, panels, lighting install,
disconnects, safe-offs, temporary power, fire alarm, low voltage. Assign specific
subdivisions (`26 05 19`, `26 24 16`, `26 51 13`); fall back to `26 00 00`, never to a
Common Work Results code.

Wall types sort to the top of Drywall & Carpentry, numerically, exterior last.

Suggested block order: General Requirements, Masonry, Drywall & Carpentry, Acoustical
Ceilings, Flooring, Tile, Painting, Doors and Hardware, Glass and Glazing, Custom Millwork,
Specialties, Equipment, Furnishings.

### Line item format

| Reference | Scope Item |
|---|---|
| 5/A-201 | F/I T-L-1 Floor Tile [Daltile Model XYZ Charcoal Gray] |
| A-400 | F/I Membrane Roofing [Carlisle Sure-Weld TPO White] |
| 5/A-201, 3/A-301 | F/I T-L-1 Floor Tile [Daltile Model XYZ Charcoal Gray] |
| [UNVERIFIED] | Provide Temporary Power and Lighting |

**Reference column:**
- On a detail: `[detail#]/[sheet#]`, e.g. `5/A-201`
- On a plan with no detail callout: the sheet number, e.g. `A-400`
- On several sheets: comma separated
- Source cannot be identified: `[UNVERIFIED]`
- Auto-inserted boilerplate: **blank**, never `[UNVERIFIED]`

**Scope Item column:**
- Begins with a directive
- Tag immediately after the directive if there is one (`T-L-1`, `D-1`, `P-101`)
- Title Case
- Spec in square brackets at the end, `[Manufacturer Model Color]` in that order
- No spec called out: `[Not Specified]`
- Preserve exact drawing spec language, never normalize it
- Industry abbreviations are fine except CSI codes, which match MasterFormat exactly

### Directives

| Directive | Use for |
|---|---|
| F/I | Furnish and Install |
| F/O | Furnish Only |
| I/O | Install Only |
| Remove | Demolition |
| Provide | Services, shop drawings, mockups, non-material work |

**Never stack a directive onto a scope item that already carries one.** If the action word
is itself a directive (Replace, Refinish, Patch, Repair, Seal, Flash), use it as-is.

- Right: `Replace Existing CMU at Modified Opening`
- Wrong: `F/I Replace Existing CMU at Modified Opening`

**Painting is always `Prep and Paint [Surface] [Spec]`.** Never `F/I Paint`. `Prep and
Paint` is its own action phrase and takes no directive in front of it.

### Trade-splitting rules

Mandatory, and they override what the drawings show. Full examples in
`references/trade-rules.md`.

| Scope | Split |
|---|---|
| HVAC demolition | HVAC sub drains down and disconnects. Demo sub removes |
| Sprinkler demolition | Sprinkler sub drains down and disconnects. Demo sub removes |
| Electrical demolition | Electrical sub does disconnects and safe-offs, always on renovations even if not drawn. Demo sub removes. Always add "Provide Temporary Power and Lighting" |
| Doors, frames, hardware | F/O in Division 08. I/O in Drywall & Carpentry |
| Toilet accessories | F/O in Division 10. I/O in Drywall & Carpentry |
| Lighting fixtures | F/O and I/O as companion lines in the same Division 26 lighting subdivision. Never in carpentry |
| Plumbing fixtures | F/O always paired with an I/O rough-in line in the specific Division 22 subdivision |
| Owner-supplied | Prefix `I/O Owner-Supplied`, always with a delivery acceptance and coordination line |

### Auto-inserted line items

**Shop drawings** always for Architectural Metalwork and Glass, Millwork, HVAC, Sprinkler.
Drawing dependent for Composite Materials and Plumbing.

**Sprinkler** also gets Hydrostatic Testing, Permits, Inspections, Signoff.

**Boilerplate is conditional, never blanket.**

| Line | Applies to |
|---|---|
| Cleanup | Every trade doing on-site work. Not furnish-only material trades |
| Testing | Only trades that test or commission: sprinkler hydrostatic, plumbing pressure and disinfection, HVAC balancing, fire alarm acceptance, flooring moisture. Prefer the specific drawing-sourced test over a generic catch-all. **Never on finish trades** (painting, ceilings, tile, base, doors, glazing, millwork, specialties, shades) |
| Permits | Jurisdiction driven, see below |
| Pure F/O material trades (frames, doors, hardware, appliances) | **None of the three.** The supplier delivers material. Install, test, cleanup and permit sit with the installing trade |

**Permit-by-jurisdiction.** In most US municipalities the GC pulls the building or
alteration permit, covering demolition and all architectural and finish trades. The trades
that pull their own are the licensed MEP and fire trades: Electrical, Plumbing, Mechanical,
Fire Suppression, Fire Alarm. Confirm against the stamped MEP and FP sets. Dense
jurisdictions such as NYC file more trades separately and may require a standalone
demolition permit, so adjust to the actual AHJ before generating. State the GC's
building-permit coverage **once** in Notes, not per trade. When one sub bids a trade split
across several subdivisions, put the permit line once on the lead block.

**Existing conditions protection** goes at the bottom of its trade block.

### Build-up bullets

Assembly line items, partition types above all, carry indented bullets underneath: the
build-up in the drawing's own words. A drywall sub cannot price "Type 2, 250.73 LF"; they
can price the stud size, gauge, spacing, layer count, insulation, sealant and rating.

- **Verbatim drawing language.** Do not paraphrase, do not normalize. `G.W.B.` stays `G.W.B.`
- Carry the rating and listing in the title: `2 HR [UL #U419, STC 50-53]`
- Five to seven bullets. Past that it stops being punchy and becomes a spec section
- Bullets occupy the scope column only. No quantity, no rate, no total, so they never touch a sum
- Strip UI-noise prefixes from takeoff exports: `Levels - `, `Walls - `

### Quantity rules (quantified mode)

1. **Never invent a quantity.** No support in the drawings means `qty: null`, which renders
   red, totals nothing, and is named in Notes as requiring a plan count. A blank is a real
   gap; a made-up number is a loss.
2. **Derived quantities state their derivation** in the Quantity Basis sheet: the inputs,
   the multiplier, the source sheet.
3. **Units must match the work.** Paint, wall covering, tile, brick, wall patching and
   flooring are area work and take SF. Scan for a linear unit on area work before building.
   It is the most common defect in a takeoff export and it is invisible once priced.
4. **Reconcile counted things against their schedule.** Doors against the door schedule TYPE
   column, hardware against HDW SET, fixtures against the fixture schedule. Report a
   disagreement, never silently resolve it.
5. **Roll-up lines** such as floor prep are the sum of their component lines, stated as
   such. Sum only lines sharing a unit.

### Conflict detection

Same item, conflicting specs: use the **first** spec encountered in the line item, and list
every version in the Conflicts block.

`Item Name | Spec A (Source) vs. Spec B (Source)`

### TBD items

Anything shown TBD: carry it with `[Not Specified]` or `[TBD]` and add it to the TBD block.

`Item Name | What is TBD | Source Page`

### What never goes in the scope

Cost references. Submittal and cut-sheet language (assumed). Schedule dependencies or
sequencing. Quality-standard language ("per industry standards"). Warranty, substitution and
change-order-trigger language. Standard general-notes footers. Allowances. As-built
documentation language. In `scope` mode, quantities.

## Phase 3: QA validation passes

Run in order, before building. **Internal only. The report is never printed into the
workbook or the PDF.** Summarize the flags in chat.

| Pass | Check | On failure |
|---|---|---|
| 1 Citation | Every Reference exists in the drawing.md files and says what the line says | Mark `[UNVERIFIED]` |
| 2 Spec | Every bracketed spec appears verbatim at the cited location | Change to `[Not Specified]`, add to TBD |
| 3 Omission | Reverse query the drawings for scope missing from the SOW | Add what was missed |
| 3.5 Cross-sheet contradiction | For any item on 2+ sheets, compare its disposition across every appearance: existing-to-remain against remove or replace, conflicting dimensions or specs for the same tag | Log to Conflicts. **Never silently resolve** |
| 4 Trade split audit | Every rule in Phase 2 applied | Fix |
| 5 Format audit | Directive, Title Case, bracket spec, tag position, Reference populated | Fix |
| 6 Report | Count lines, unverified, not-specified, conflicts, TBDs, splits, auto-inserts | Read it in chat, do not print it |

Pass 3.5 exists because real drawing sets contain genuine contradictions. One sheet marking
an item "DO NOT DISTURB" while another calls for its removal is not an extraction error, it
is a conflict in the source documents, and a human needs to see it before pricing goes out.

Pass 3 is the scope-miss check. It is the pass to run when someone hands you a finished
estimate and asks what it missed.

## Phase 4: SOW comparison

When a prior `*_SOW_*.xlsx` sits in the project folder, build a comparison after the current
SOW is finalized. Also on explicit request, and always after a fresh re-extraction.

Save as `SOW_Comparison_[YYYY-MM-DD].xlsx`.

**Sheet 1, Summary.** Per trade: prior item count, current item count, added, removed,
status (`NEW` / `MODIFIED` / `REMOVED` / `UNCHANGED`). Totals row and a legend.

**Sheet 2, Line Item Detail.** Side by side: prior ref, prior scope, current ref, current
scope, status (`ADDED` / `REMOVED` / `UNCHANGED`), grouped under trade bands.

**Fuzzy matching.** Normalize before comparing: strip bracketed spec text, collapse
whitespace, lowercase. A spec edit is `UNCHANGED`, not a new item. Without this, every
bracket reformat reads as churn.

**Colors** stay in the palette: added `#D6F0D6` on `#1E6B1E`, removed `#FFD6D6` on
`#8B0000`, modified `#FFF0C8` on `#7A5200`, unchanged `#F5F5F5` on `#555555`.

## The workbook

### The grid

```
scope       Reference (16) | Scope Item (76) | [Resp. (12)] | gutter (2.5) | Sub #1-4 (15 each)
quantified  Reference (16) | Scope Item (52) | Qty (10) | Unit Type (11)
            | Unit Rate (13) | Total (14) | [Resp. (12)] | gutter (2.5) | Sub #1-4 (15 each)
```

- **The gutter is a deliberate narrow empty column**, not a spare. Medium rule both sides,
  no fill, full height of every trade block. It separates our money from their money. Row
  highlights stop at it rather than bleeding through.
- **Our columns are left of the gutter, the subs' are right.** `Total = Qty x Unit Rate`,
  written so a line with no quantity computes nothing instead of contributing a silent zero.
- **The gutter and the sub columns are outline-grouped**, so one native toggle collapses the
  sub side and leaves a clean scope or a clean priced estimate. `summaryRight=False` puts
  the button on the left.
- Landscape, `fitToWidth=1`, `fitToHeight=0`, print titles through the header, freeze below it.

### Trade block anatomy

```
[spacer row, 7pt]
[trade header, TWO rows tall]
    merged across both rows, left of the gutter = "TRADE NAME  --  CSI 09 20 00, 09 29 00"
    row 1, sub columns = "Sub #1".."Sub #4"   (overwrite with real names)
    row 2, sub columns = lump-sum entry cells (MEDIUM BOTTOM RULE)
[line rows]     reference | scope | [qty | unit | rate | total] | [resp] | per-line sub prices
[bullet rows]   scope column only, indented, 9pt italic, no numbers
[TRADE TOTAL]   our total, and each sub summed FROM THE LUMP-SUM ROW DOWN
```

Each sub column sums from the lump-sum row, not the first line item, so a sub who bids one
number and a sub who bids line by line both roll up correctly.

### Close-out ladder (quantified mode only)

```
[SUBTOTAL]      each money column = the sum of that column's TRADE TOTALs
[6 markup rows] label (user types) | percent in Unit Rate (user types) | money compounded
[TOTAL]         SUBTOTAL + SUM(markup rows)
```

**Markups compound, they do not stack.** Row 1 applies to the subtotal, row 2 to subtotal
plus row 1, and so on. One percent in the rate column drives all five money columns, so our
total and each sub's total are marked up on the same basis and stay comparable. Every markup
row guards on an empty percent, so unused rows render blank and TOTAL equals SUBTOTAL until
someone enters one. Per-row rounding to cents is deliberate: the total differs from a pure
compound by a cent or two, which is correct for money.

**Scope mode gets no ladder.** There is no money of ours to mark up, and the only free
column would be Scope Item, which would put a percentage under a text heading and mirror it
onto the SOV. SUBTOTAL across the sub columns stays so bids still level.

### The SOV sheet

One row per trade, because a schedule of values is what you award from, and you award a
trade to a sub.

| Column | Contents |
|---|---|
| Trade, CSI | from the trade blocks |
| Our Total | linked to that trade's total (quantified mode) |
| Sub #1-4 | linked to the same trade's sub totals, blank when nobody has bid |
| Low Bid | `MIN` across the four |
| Low Bidder | `INDEX/MATCH` back to the sub-name header, so renaming Sub #2 follows through |
| Low Bid vs Ours | negative means the market is under our number (quantified mode) |

Then the same ladder, with labels and percentages **linked back** to the Scope of Work sheet
so markups are entered once.

The low bid is flagged by conditional formatting, not a static fill, so it re-evaluates the
moment a bid is typed.

**Everything here is a link or a formula.** A disconnected SOV that silently disagrees with
the scope sheet is worse than no SOV.

### Borders, the thing that goes wrong

**Excel draws a merged range's edges from every one of its constituent cells.** Border only
the anchor and the box renders about a quarter drawn and looks arbitrary. This is the single
most common defect in a generated workbook, and it reads as sloppiness rather than as a bug.

1. **Border every cell in a region**, computing each side from its position. `paint()` does this.
2. **Merge AFTER bordering, never before.** Collect merges and apply them at the end. A
   `MergedCell` will not reliably take a style.

| Element | Rule |
|---|---|
| Trade block perimeter | medium charcoal |
| Inside a trade block | hairline, all four sides of every cell |
| Under the trade header, above TRADE TOTAL | medium |
| Gutter | medium left and right, full block height |
| Column header row | medium black box |
| Legend rows | horizontal rules only, no verticals |
| Sheet gridlines | off. The table edges are the only lines |

### Row heights

Compute them. **Never write a flat height**: it disables Excel's double-click auto-fit, so
wrapped scope text clips and someone hand-fixes 200 rows.

### Highlighting: red only

**One color. Red means the line carries no quantity** and cannot be bid until someone counts
it. It renders `--`, shades the row, and contributes to no total.

Never ship amber "added by review" highlighting on a client-facing workbook. Use it while
reviewing a draft, then strip it before the document goes out. Light gray banding is the
only other fill on line rows.

### The hidden sheet

`Quantity Basis` ships `hidden`. **Hidden is not removed**, it is one right-click away. Say
so when handing the workbook over. If the content genuinely must not travel, delete the
sheet and keep the basis in the job folder.

## Notes & Clarifications: what goes in, what never does

This sheet is the commercial terms of the bid. Write it the way an estimator writes it.

**Always include:**
- Every exclusion with its reason
- The basis of quantities: which drawing set, which issue date
- Any line carried without a quantity, and what will release it
- Any derived quantity whose basis could move the price
- Unresolved product selections: TBD colors, missing model numbers, "or comparable"
- Missing legends and schedules the trade needs
- Permit and filing responsibility, stated once

**Never include:**
- How the document was produced, what tooling was used, or that any of it was assisted
- Internal review language: "flagged", "verify", "derived by review", reviewer disagreements
- Anything reading as a disclaimer about confidence rather than a term of the bid
- The QA report, in any form, on any surface

**The line is substance, not tone.** A clarification saying paint is measured to an 8'-0"
ceiling and will be trued up on the final RCP is a commercial term and stays. A note saying
that number was derived rather than measured is process and goes to the hidden sheet.

Removing process language must never quietly remove a qualification. If a note is the only
place a real limitation is stated, rewrite it in estimator voice. Do not delete it.

## Landlord / tenant split

Set `landlord_tenant: true` and tag every line `responsibility`: `Landlord`, `Tenant` or
`Both`. Classification priority, highest first:

1. **Explicit assignment in a Landlord SOW document.** "Landlord shall provide X" wins over
   the drawings
2. **Explicit drawing callout.** "By Tenant", "By Owner", "N.I.C.", "By Others"
3. **Industry-convention defaults**, only when neither of the above addresses the item

Full rules in `references/landlord-tenant-rules.md`. The PDF builder writes the split
versions:

```bash
python scripts/build_sow_pdf.py sow_data.json landlord.pdf --responsibility Landlord
python scripts/build_sow_pdf.py sow_data.json tenant.pdf   --responsibility Tenant
```

An untagged line is kept in both outputs, so a missing tag is visible rather than silently
dropping scope.

## Output modes and file names

Ask at step 0: one combined workbook, or one file per trade.

- Combined: `[Project]_SOW_[YYYY-MM-DD].xlsx`
- Per trade: `[Project]_SOW_[TradeCode]_[YYYY-MM-DD].xlsx`
- PDF: `[Project]_SOW_[YYYY-MM-DD].pdf`

**Project name fallback:** use the cover-sheet titleblock name, in `index.json` at
`project.name`. If there is none, fall back to the name confirmed at step 0. **Never emit
`Untitled`.** `drawing-index --validate` hard-fails on this, so a clean index has already
handled it.

## Running the scripts

```bash
python scripts/build_sow_xlsx.py sow_data.json out.xlsx
python scripts/build_sow_pdf.py  sow_data.json out.pdf [--responsibility Landlord|Tenant|All]
```

Both read the same `sow_data.json` through one normalizer, so a file that builds a workbook
always builds the matching PDF.

On Windows or a synced Dropbox folder, run project-local scripts through stdin piping,
because sync can lock a freshly written `.py`:

```
py - < .sow_work/gen_sow.py
```

Use `py`, not `python`, where `python` is the Microsoft Store redirect. If PyMuPDF is
blocked by AV or EDR, do not fight it: use `pdftotext` for text pages, and see
`drawing-index` for graphical ones.

## Artifact retention

Permanent project deliverables. Never delete during cleanup: `drawings/index.json`,
`drawings/sheets.json`, `drawings/md/*.md`, `drawings/index_rev*.json`, `.sow_work/*.py`,
`sow_data.json`, every `*_SOW_*.xlsx` and `.pdf`, `SOW_Comparison_*.xlsx`, `.sow_backups/`.

Prior SOW versions are preserved, never overwritten. Clean only genuinely redundant scratch,
and ask when unsure.

## Files

- `scripts/build_sow_xlsx.py` — the workbook. Owns the grid, borders, formulas, sheet order
- `scripts/build_sow_pdf.py` — the typeset PDF, and the landlord/tenant filter
- `scripts/sample_test_data.json` — a worked example
- `references/workbook-spec.md` — the `sow_data.json` contract, field by field
- `references/csi-subdivisions.md` — subdivision list and selection logic
- `references/trade-rules.md` — trade-splitting examples
- `references/standard-clarifications.md` — boilerplate clarification text
- `references/landlord-tenant-rules.md` — the split rules
- `../drawing-index/` — extraction. Not owned here, never copied here

## Critical rules

1. ALWAYS build or reuse a validated `index.json`, and NEVER proceed past a non-zero `--validate`
2. NEVER re-implement extraction here. That is `drawing-index`'s job
3. NEVER invent a quantity. No drawing support means `qty: null`, red, and a note
4. NEVER let a null-quantity line contribute to a total
5. NEVER normalize spec language. Preserve exact drawing text
6. NEVER paraphrase drawing language in build-up bullets
7. NEVER output a line without a Reference. Use `[UNVERIFIED]` when the source cannot be found
8. NEVER write `[UNVERIFIED]` on auto-inserted boilerplate. Leave its Reference blank
9. NEVER skip a QA pass, and NEVER print the QA report onto any deliverable
10. ALWAYS run Pass 3 (omission) and Pass 3.5 (cross-sheet contradiction) before output
11. ALWAYS list conflicts in the Conflicts block. Never silently pick one
12. ALWAYS use `[Not Specified]` when a spec is missing. Never invent
13. ALWAYS apply the trade-splitting rules even when the drawings do not show them
14. NEVER blanket-insert boilerplate. Permits, testing and cleanup are conditional by trade
15. NEVER use a Common Work Results code (`xx 05 00`), Rough Carpentry or Finish Carpentry on commercial work
16. NEVER prepend a directive to a scope item that already carries its own action word
17. ALWAYS write painting as `Prep and Paint [Surface] [Spec]`
18. ALWAYS check units before building: area work takes SF, never LF
19. ALWAYS reconcile counted items against their own schedule and report disagreements
20. ALWAYS border every cell in a merged region, and merge only after bordering
21. ALWAYS compute row heights. Never write a flat height
22. ALWAYS sum each sub column from the lump-sum row down
23. ALWAYS keep the gutter unfilled with medium rules both sides. Highlights stop there
24. NEVER put amber or any "reviewed" highlighting on a client-facing document. Red only
25. ALWAYS compound markups on the running total, and guard every markup row on an empty percent
26. ALWAYS link the SOV to the Scope of Work sheet. Never hard-code a total on it
27. ALWAYS flag the low bid by conditional formatting so it re-evaluates
28. NEVER put process, tooling or authorship notes in Notes & Clarifications
29. NEVER let removing process language delete a real qualification. Rewrite it in estimator voice
30. ALWAYS tell the user that the hidden sheet is hidden, not removed
31. ALWAYS render and read the output back before delivering, or say plainly that you could not
32. ALWAYS generate a comparison when a prior SOW version is in the folder
33. NEVER delete `index.json`, `drawings/md/`, `.sow_work/`, or any SOW version
34. ALWAYS ask the mode and the output shape at step 0. Never assume a takeoff exists
35. ALWAYS use plain ASCII in every JSON and text field (`ensure_ascii=True`)

The goal is zero hallucination and a document clean enough to send. If a fact cannot be
verified to a drawing source, flag it. Better a real item marked `[UNVERIFIED]` than an
invented one shipped quietly.
