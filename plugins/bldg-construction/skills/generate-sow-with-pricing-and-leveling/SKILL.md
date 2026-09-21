---
name: generate-sow-with-pricing-and-leveling
description: Builds a single client-facing Excel workbook that carries scope, quantities, our unit rates and extended totals, AND four subcontractor bid-leveling columns side by side on the same row - so our number and every sub's number reconcile in one view. Use whenever Matt wants a scope of work that also carries quantities and pricing columns, a quantified bid-leveling sheet, a "SOW with pricing", a takeoff turned into a leveling document, or wants to send subs a quantified scope to price. Organised by trade with CSI codes, indented build-up bullets under assembly line items, a red flag on any line with no quantity, and a Notes & Clarifications sheet written in estimator voice for the GC. For scope with zero numbers use sow-generator. For a separate disclaimer-fronted AI quantity workbook use sow-generator-quantities. For a priced estimate against the cost database use conceptual-estimate.
---

# SOW with Pricing and Leveling

One workbook. Scope on the left, our quantities and money in the middle, the subs' numbers
on the right, every trade reconciling on its own TRADE TOTAL row. It is the document you
level bids against and the document you hand a sub to price, which is why it has to be
clean enough to send out and honest enough to bid from.

## What this produces

`[Project]_SOW_Leveling_Quantified_[YYYY-MM-DD].xlsx`

| Sheet | Audience | Contents |
|---|---|---|
| **Scope of Work** | GC / subs | Trade blocks, quantified scope, our rate and total, four sub columns, then SUBTOTAL -> markup ladder -> TOTAL |
| **SOV** | GC | Trade roll-up: our total against all four sub bids, low bid flagged, same markup ladder |
| **Notes & Clarifications** | GC | Exclusions and clarifications in estimator voice |
| **Quantity Basis** | internal, **hidden** | Per-line basis for anything derived or unquantified |

## The grid -- exact

```
A Scope Item (56) | B Qty (10) | C Unit Type (11) | D Unit Rate (13) | E Total (14)
| F gutter (2.5) | G Sub #1 | H Sub #2 | I Sub #3 | J Sub #4  (15 each)
```

- **F is a deliberate narrow gutter**, not a spare column. Medium rule on both sides, no
  fill, running the full height of every trade block. It separates our money from their
  money visually. Row highlights stop at it rather than bleeding through.
- **D and E are ours. G through J are theirs.** `Total = Qty x Unit Rate`, written as
  `=IF(AND(ISNUMBER($B<r>),ISNUMBER($D<r>)),$B<r>*$D<r>,"")` so a line with no quantity
  computes nothing instead of silently contributing zero.
- **F:J are outline-grouped (level 1)** so one native toggle collapses the whole sub side
  and leaves a clean priced estimate. `summaryRight=False` puts the button on the left.
- Landscape, `fitToWidth=1`, `fitToHeight=0`, print titles rows 1..header, freeze below
  the header. All ten columns must fit one page wide.

### Trade block anatomy

```
[spacer row, 7pt]
[trade header, TWO rows tall]
    A:E merged across both rows = "TRADE NAME  --  CSI 09.29.00, 09.72.00"  (medium gray, white, bold)
    row 1, G:J = "Sub #1".."Sub #4"      (light gray, bold, centred -- overwrite with real names)
    row 2, G:J = lump-sum entry cells     (very light, currency, centred, MEDIUM BOTTOM RULE)
[line rows]        A scope | B qty | C unit | D rate | E total | G:J per-line sub prices
[bullet rows]      A only, indented, 9pt italic -- no qty, no price, no total
[TRADE TOTAL]      A:C merged; E = SUM of our totals; G:J = SUM from the LUMP-SUM ROW down
```

### Close-out ladder (below the last trade)

```
[SUBTOTAL]      A:C merged, bold. Each money column = the sum of that column's TRADE TOTALs
[6 markup rows] A = label (user types) | D = percent (user types) | money columns = compounded
[TOTAL]         A:C merged, bold 12pt. = SUBTOTAL + SUM(markup rows)
```

**Markups compound, they do not stack.** Row 1 applies to the subtotal; row 2 applies to
subtotal plus row 1; and so on. One percent in column D drives all five money columns, so
our total and each sub's total are marked up on the same basis and stay comparable.

```
row 1 : =IF($D<r>="","",ROUND(( <col><sub> )*$D<r>,2))
row n : =IF($D<r>="","",ROUND(( <col><sub>+SUM(<col><m1>:<col><r-1>) )*$D<r>,2))
total : =ROUND(<col><sub>+SUM(<col><m1>:<col><m6>),2)
```

Every markup row guards on an empty percent, so unused rows render blank rather than zero
and the TOTAL equals the SUBTOTAL until someone enters a markup. Per-row `ROUND` to cents is
deliberate -- the total will differ from a pure compound by a cent or two, which is correct
for money.

The TRADE TOTAL sums **two independent ways on the same row** -- our extended total in E,
each sub's column in G:J. That side-by-side is the entire point of the document.

Each sub column sums from the **lump-sum row**, not the first line item, so a sub who bids
one number and a sub who bids line by line both roll up correctly.

## The SOV sheet

One row per trade, not per line item -- a schedule of values is what you award from, and you
award a trade to a sub.

| Column | Contents |
|---|---|
Trade, CSI | from the trade blocks |
Our Total | `='Scope of Work'!E<trade total row>` |
Sub #1..#4 | linked to the same trade's sub totals, blank when the sub has not bid |
Low Bid | `MIN` across the four, blank when nobody has bid |
Low Bidder | `INDEX/MATCH` back to the sub-name header, so renaming Sub #2 follows through |
Low Bid vs Ours | low minus ours -- negative means the market is under our number |

Then the same SUBTOTAL -> markup ladder -> TOTAL, with the labels and percentages **linked
back to the Scope of Work sheet** so markups are entered once and mirrored.

**The low bid in each row is highlighted** by conditional formatting (`MIN` across the four
sub cells, green fill, bold) rather than a static fill, so it re-evaluates the moment a bid
is typed or changed.

Everything on this sheet is a link or a formula. Never hard-code a total here -- a
disconnected SOV that silently disagrees with the scope sheet is worse than no SOV.

## Borders -- the thing that goes wrong

**Excel draws a merged range's edges from every one of its constituent cells.** Border only
the anchor cell and the box renders about a quarter drawn and looks arbitrary. This is the
single most common defect in generated workbooks and it looks like sloppiness, not a bug.

Two rules:

1. **Border every cell in a region**, computing each side from its position. `paint()` in
   `scripts/build_sow_pricing_xlsx.py` does this.
2. **Merge AFTER bordering, never before.** Collect merges in a list and apply them at the
   end. A `MergedCell` will not reliably take a style.

The border system:

| Element | Rule |
|---|---|
Trade block perimeter | medium (charcoal) |
Inside a trade block | hairline, all four sides of every cell |
Under the trade header block | medium |
Above TRADE TOTAL | medium |
Gutter column F | medium left and right, full block height |
Column header row | medium black box |
Legend rows (5-6) | horizontal rules only -- **no verticals** |
Sheet gridlines | `sheet_view.showGridLines=False` -- the table edges are the only lines |

## Row heights

Compute them. Never write a flat height -- an explicit height disables Excel's
double-click auto-fit, so wrapped scope text clips and someone hand-fixes 200 rows.

```python
height = max(22, ceil(len(text)/chars_per_line) * 13)   # line items
height = max(14, ceil(len(text)/50) * 11)               # bullet rows
```

## Highlighting -- red only

**One colour. Red (`FFFFD6D6`) means the line carries no quantity** and cannot be bid until
someone counts it. It renders `--` in the Qty cell, shades the row, and contributes to no
total.

Do **not** ship amber "added by review" highlighting on a client-facing workbook. Use it
while Matt reviews a draft, then strip it before the document goes out. Alternating very
light gray banding is the only other fill on line rows.

## Trade organisation

Group by **trade** -- the entity actually bidding -- with the CSI codes shown in the header.
Levelling is per sub, so a trade block is the unit a sub prices. Consolidations that always
apply:

| Do not use | Use |
|---|---|
Framing, Rough Carpentry, Finish Carpentry, Gypsum Board, Metal Framing | **Drywall & Carpentry** |
Millwork, Casework, architectural woodwork | **Custom Millwork** |
Any `xx 05 00` Common Work Results code | the specific trade subdivision |

Wall types sort to the top of Drywall & Carpentry, numerically, exterior last.

Suggested block order: General Requirements, Masonry, Drywall & Carpentry, Acoustical
Ceilings, Flooring, Tile, Painting, Doors and Hardware, Glass and Glazing, Custom Millwork,
Specialties, Equipment, Furnishings.

## Build-up bullets

Assembly line items -- partition types above all -- carry indented bullets underneath: the
build-up in the drawing's own words. A drywall sub cannot price "Type 2, 250.73 LF"; they
can price the stud size, gauge, spacing, layer count, insulation, sealant and rating.

- Bullets are **verbatim drawing language**. Do not paraphrase, do not normalise. `G.W.B.`
  stays `G.W.B.`
- Carry the rating and the listing in the title -- `2 HR [UL #U419, STC 50-53]` -- because
  that is what determines the assembly a sub buys.
- 5 to 7 bullets is right. Past that it stops being punchy and becomes a spec section.
- Bullets occupy column A only. No quantity, no rate, no total, so they never touch a sum.
- Strip UI-noise prefixes from takeoff exports: `Levels - `, `Walls - ` and similar.

## Quantity rules

1. **Never invent a quantity.** A line the drawings do not support gets `qty: null`, renders
   red, and is named in Notes & Clarifications as requiring a plan count. A blank is a real
   gap; a made-up number is a loss.
2. **Derived quantities state their derivation** in the Quantity Basis sheet -- the inputs,
   the multiplier and the source sheet. Example: new-wall paint = (interior partition LF x 2
   faces) + (single-face runs x 1) x the typical ceiling height stated on the RCP.
3. **Units must match the work.** Paint, wall covering, tile, brick, wall patching and
   flooring are area work and take SF. Before building, scan for a linear unit on area work
   -- it is the most common defect in a takeoff export and it is invisible once priced.
4. **Reconcile counted things against their schedule.** Door types against the door schedule
   TYPE column, hardware sets against the HDW SET column, fixtures against the fixture
   schedule. Report a disagreement, never silently resolve it.
5. **Roll-up lines** such as floor prep are the sum of their component takeoff lines, stated
   as such. Sum only lines sharing the unit.

## Notes & Clarifications -- what goes in, what never does

This sheet is the commercial terms of the bid. It goes to the GC. Write it the way an
estimator writes it.

**Always include** -- these are what is being priced, not commentary:

- Every exclusion with its reason (excluded scope, work by others, missing documents)
- The basis of quantities: which drawing set, which issue date
- Any line carried without a quantity, and what will release it
- Any derived quantity whose basis could move the price (a paint height assumption, an
  allowance against a TBD selection)
- Unresolved product selections: TBD colours, missing model numbers, "or comparable"
- Missing legends and schedules the trade needs (a hardware set legend, a room finish matrix)
- Permit and filing responsibility

**Never include:**

- How the document was produced, what tooling was used, or that any of it was assisted.
  The deliverable is the firm's work product; process notes are not the client's business
  and do not belong in a bid document.
- Internal review language: "flagged", "verify", "derived by review", "recommend
  re-measuring", disagreements between reviewer and estimator.
- Anything that reads as a disclaimer about confidence rather than a term of the bid.

**The line between them is substance, not tone.** Strip the process, keep every
qualification that changes what is being priced. A clarification saying paint is measured to
an 8'-0" ceiling and will be trued up on the final RCP is a commercial term and stays. A
note saying that number was derived rather than measured is process and goes to the hidden
Quantity Basis sheet.

Removing process language must never quietly remove a qualification. If a note is the only
place a real limitation is stated, rewrite it in estimator voice -- do not delete it.

## The hidden sheet

`Quantity Basis` holds the per-line basis for every derived or unquantified line and ships
`sheet_state="hidden"`.

**Hidden is not removed.** It is one right-click away in Excel. Say so when handing the
workbook over. If the content genuinely must not travel, delete the sheet and keep the
basis in the job folder instead.

## Workflow

```
0. CONFIRM   -> project, output folder, whether pricing columns stay blank or carry our rates
1. INDEX     -> drawing-index (--validate clean) if no index.json exists
2. SCOPE     -> sow-generator Phases 2-3: directives, bracket specs, trade splits, QA passes
3. QUANTIFY  -> reuse the internal takeoff if one exists; else construction-takeoff.
                Reconcile against the schedules. Flag unit mismatches. Never invent.
4. ASSEMBLE  -> sow_pricing_data.json per references/workbook-spec.md
5. BUILD     -> python scripts/build_sow_pricing_xlsx.py sow_pricing_data.json out.xlsx
6. VERIFY    -> render to PDF and LOOK at it. Borders, clipping, page width, gutter.
7. DELIVER   -> SendUserFile, then commit into the job folder
```

**Step 6 is not optional.** Convert with LibreOffice and read the rendered pages back:

```bash
soffice --headless --convert-to pdf out.xlsx --outdir /tmp/chk
```

Check the first page, one dense page, and the notes sheet. Border defects, clipped rows and
a table running off the page width are all invisible in the cell data and obvious in the
render.

## Drawing extraction

Run `drawing-index` first and read its `md/` output and `index.json`. Do not route this
through NotebookLM -- the index produces per-sheet extractions with a citation on every
fact, which is what steps 2 and 3 need, and it is cheaper.

**Watch the text-layer verdict.** A raw word count lies on sheets whose notes and schedules
are drawn as outlined vector art -- a "GENERAL NOTES" sheet returning 130 words of titleblock
has no readable notes. Subtract the titleblock (60-80 words typically) before trusting the
verdict, and run a vision pass with high-dpi crops on anything suspect. On rotated sheets
(`/Rotate 270`, text drawn at dir (0,1)) group words by x and read down y, or every schedule
comes out scrambled.

## Critical Rules

1. NEVER invent a quantity. No support in the drawings means `qty: null`, red, and a note.
2. NEVER let a null-quantity line contribute to a total.
3. ALWAYS border every cell in a merged region, and merge only after bordering.
4. ALWAYS compute row heights; never write a flat height.
5. ALWAYS sum each sub column from the lump-sum row down, not from the first line item.
6. ALWAYS keep the gutter column unfilled with medium rules both sides; highlights stop there.
7. NEVER put amber or any "reviewed / added" highlighting on a client-facing workbook. Red only.
8. NEVER paraphrase drawing language in build-up bullets.
9. NEVER put process, tooling or authorship notes in Notes & Clarifications.
10. NEVER let removing process language delete a real qualification -- rewrite it in estimator voice.
11. ALWAYS check units before building: area work takes SF, never LF.
12. ALWAYS reconcile counted items against their own schedule and report disagreements.
13. ALWAYS render to PDF and visually review before delivering.
14. ALWAYS tell the user that a hidden sheet is hidden, not removed.
15. ALWAYS compound markups on the running total, never stack them on the subtotal.
16. ALWAYS guard markup and total formulas on an empty percent so unused rows stay blank.
17. ALWAYS link the SOV to the Scope of Work sheet -- never hard-code a total on it.
18. ALWAYS flag the low bid by conditional formatting so it re-evaluates when a bid changes.
19. ALWAYS use plain ASCII in every JSON and text field (`ensure_ascii=True`).

## Files

- `scripts/build_sow_pricing_xlsx.py` -- the workbook builder. Owns the grid, the borders,
  the formulas and the sheet order.
- `references/workbook-spec.md` -- the `sow_pricing_data.json` contract, field by field.
