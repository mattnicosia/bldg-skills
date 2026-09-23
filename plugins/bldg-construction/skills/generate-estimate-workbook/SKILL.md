---
name: generate-estimate-workbook
description: Build Matt's internal estimate workbook (Estimate + SOV with Final Price + Notes + Estimate Review) from a priced estimate export, with alternates, markup ladders and an internal flag review.
---

# Generate Estimate Workbook

One internal Excel workbook built from a priced estimate: every line with our quantity, rate and
total, four sub-bid leveling columns, a Final Price column, alternates carried all the way to a
burdened total, and an internal review of everything that's wrong before the proposal goes out.

Derived from `generate-sow-with-pricing-and-leveling` (grid, borders, gutter, sub columns) and
`generate-estimate-from-unit-cost-report` (SUM-wrapped formulas, derived rates, cached results).
This skill supersedes both for internal estimate reports. The two scripts in `scripts/` are
complete; run them. Do not rebuild them from memory.

## Output

`[project]_Report_v[N].xlsx` (Matt's naming convention; increment N if the file exists), saved to
the job's `04 Deliverables` folder and sent with SendUserFile.

| Tab | Contents |
|---|---|
| **Estimate** | CSI column, then trade blocks (header = trade name only, no CSI), lines with Qty / Unit / Rate / Total, gutter, Sub #1-#4. Base ladder: SUBTOTAL, General Conditions, Fee, Insurance, TOTAL -- BASE BID. **Alternates start at row 401** (pushed to 501, 601... only if the base runs long), each with its own SUBTOTAL / GC / Fee / Insurance / TOTAL. |
| **SOV** | CSI, Trade, Our Total, **Final Price** (yellow input), Sub #1-#4, Low Bid, Low Bidder, Low Bid vs Ours. Our Total and Final Price both carry the full Subtotal / GC / Fee / Insurance / Total ladder (Final Price shows $0.00 until entered). Below it on its own page: **Alternates** table (CSI, Alternate, Our Direct, Final Price, GC, Fee, Insurance, Burdened Total, Proposal Amount, Variance, Proposal Ref); red rows = priced but not on the proposal. |
| **Notes & Clarifications** | Exclusions (red) and clarifications, estimator voice. |
| **Estimate Review** | Internal only. Numbered findings: Priority (HIGH / MED / LOW), Area, Finding, Direct $ at Stake, Action Before Issue. |
| **Quantity Basis** | Hidden. Derivation of every composite or derived line. Hidden is not removed; tell Matt. |

CSI codes always sit to the LEFT of trade / alternate names, in every tab.

## Pipeline

```
1. INPUTS     -> the estimate export (NOVATerra/ProEst .xlsx line items) AND the Cost Detail PDF
                 (base bid + each alternate scenario, line by line). The issued proposal PDF if one exists.
2. PARSE      -> pdftotext -layout the Cost Detail. Walk it: scenario headers ("Base Bid", "Alternate 8 ..."),
                 division headers, and lines (code, desc, qty, unit, $rate, $total). The PDF is the only
                 source of base vs alternate; the xlsx export has no scenario flag.
3. MATCH      -> match each PDF line to the xlsx row on (code, qty +/-0.02, total +/-$1.01), consuming rows
                 in order, to get the full description, status (firm / Allowance / Excluded) and exact total.
                 When the xlsx carries qty 1 but the PDF shows a real qty (it happens), use the PDF qty and
                 the xlsx exact total. Every line must match. Report any that don't.
4. ASSEMBLE   -> data.json (contract below). rate = exact_total / qty, stored unrounded, so Qty x Rate
                 lands on the estimate to the cent.
5. REVIEW     -> build the Estimate Review findings (checklist below). This is the value of the report.
6. BUILD      -> python scripts/build_estimate.py data.json raw.xlsx
7. FINALIZE   -> python scripts/finalize.py raw.xlsx out.xlsx          <- never skip
8. VERIFY     -> see Verification. Render to PDF and look at: page 1, the alternates page, the SOV,
                 the review.
9. DELIVER    -> SendUserFile, then device_commit_files into 04 Deliverables.
```

## Trade mapping (by CSI code)

| Code | Trade block |
|---|---|
01 | General Requirements |
02 | Demolition |
03 | Concrete |
05 | Miscellaneous Metals |
07.50, 07.81 | Roofing & Fireproofing |
06.20, 07.21, 09.05, 09.2x | Drywall & Carpentry |
06.22 | Custom Millwork |
09.51 | Acoustical Ceilings |
09.6x | Flooring |
09.30 | Tile |
09.91 | Painting |
08.43 / 08.81 (not HW sets) | Glass & Glazing |
other 08, and any "HW Set" line | Doors, Frames & Hardware |
10 | Specialties |
11 | Equipment |
12.21 | Window Treatments |
12.36 | Solid Surface Countertops |
21 / 22 / 23 / 26 / 28 | Fire Protection / Plumbing / HVAC / Electrical / Fire Alarm |

An unmapped code stops the build. Extend the map; never drop a line.

**Exploded drywall assemblies** (studs EA, track LF, board sheets EA, taping SF, screws LBS, then a
Primer + 2 Coat line) collapse into one line per assembly: qty = Level 4 taping SF, rate = component
total / taping SF, components listed as indented bullets verbatim ("404 EA -- 3-5/8" 20 ga x 14'
Studs @ $19.60"). The paint line moves to Painting labeled with its assembly letter. Put each
derivation in `basis[]`. Strip export noise: `Levels - `, ` ( layers)`.

**Alternates**: one block per Cost Detail scenario. Prefix each line `[Trade]`. Header reads
`ALTERNATE 8 -- 12TH FLOOR CEILING BAFFLES  |  PROPOSAL NO. 8 (12th)` or `| NOT ON PROPOSAL SCHEDULE`.
Pull proposal amounts from the proposal's Schedule of Alternates so the SOV shows variance.

## data.json contract

```json
{
  "project": "60 Madison Avenue -- 12th & Penthouse Floors",
  "subtitle": "Internal Estimate Report",
  "address": "60 Madison Avenue, New York, NY 10010",
  "date": "2026-09-23", "prepared_by": "BLDG Estimating", "job": "260117", "client": "Keystone Builders",
  "markup_labels": ["General Conditions", "Fee", "Insurance"],
  "markup_pcts": [0.08, 0.05, 0.03],
  "trades": [{"trade": "Demolition", "csi": ["02.41.00"],
              "lines": [{"csi": "02.41.00", "scope": "Remove Floor Tile", "qty": 539.41, "unit": "SF",
                         "rate": 3.5, "bullets": []}]}],
  "alts": [{"trade": "Alternate 8 -- 12th Floor Ceiling Baffles", "csi": ["09.51.00", "21.13.00"],
            "proposal": 315707.59, "proposal_no": "No. 8 (12th)", "lines": [ ...same line shape... ]}],
  "notes":  [{"type": "EXCLUSION" | "CLARIFICATION", "item": "...", "text": "..."}],
  "review": [{"p": "HIGH" | "MED" | "LOW", "area": "...", "finding": "...", "amt": 1234.56 | null, "action": "..."}],
  "basis":  [{"csi": "09.29.00", "trade": "...", "scope": "...", "qty": 0, "unit": "SF", "basis": "..."}]
}
```
Exactly three markups, in that order (GC, Fee, Insurance). An alternate not on the proposal has
`"proposal": null, "proposal_no": "NOT IN PROPOSAL"`. Plain ASCII in every string.

## Formula rules (why the scripts look the way they do)

- **Markups compound on the running total**, one percent per row, entered once on Estimate (col E
  of the base ladder). Every alternate ladder and both SOV ladders link to those three cells.
- **SUM() wraps every chained reference.** Empty trade totals render "-" (text); `+` on text is
  `#VALUE!`, SUM ignores it.
- **Sub columns stay blank until a bid is entered** (guarded on `SUM(sub)=0`); Our Total and
  Final Price always show their ladder.
- **Sub columns sum from the lump-sum row down**, so lump-sum and line-by-line bidders both roll up.
- **Final Price is a pure input.** It references nothing, so it can never be part of a circular
  reference. On the SOV alternates, GC / Fee / Insurance compound on Final Price when one is
  entered, otherwise on Our Direct: `IF(ISNUMBER(D),D,C)`.
- **Low bid** looks only at the four sub columns, highlighted by conditional formatting.

## Two things LibreOffice and openpyxl break (finalize.py fixes both)

1. openpyxl writes formulas with no cached value, so previews and phones show blank money columns.
   finalize.py recalculates through LibreOffice so every result is cached; formulas stay live.
2. **LibreOffice writes a merged range's perimeter onto every cell inside the merge**, and Excel
   then draws lines straight through merged trade headers and total labels. finalize.py rewrites
   every cell inside every merge to carry only the edges on the perimeter. It also restores
   `summaryRight=0` for the sub-column outline group.

## Estimate Review checklist

Reconcile the export, the Cost Detail and the issued proposal. Flag, with direct dollars at stake:
- **Letterhead / signatory**: proposal issued under the wrong company or signer.
- **Alternates priced but missing from the proposal schedule**, and clarifications pointing at alternates that aren't listed.
- **Same rate carried on different units** (e.g. $925 per SF on some storefront lines and per LF on others).
- **Area work in LF or EA** (paint, tile, flooring, wall covering) and wrong units on deducts.
- **Lump sums whose build-up doesn't support the carried number** (the cost detail prints "Components sum to $X; the line carries $Y").
- **Alternate deducts that don't match the base**: deducting more units than the base carries, or at a different rate.
- **Lines filed in the wrong scenario** (base scope sitting in an alternate, alternate scope in base).
- **Counts that disagree across trades** (window jambs vs trim paint vs shades; doors vs hardware sets).
- **Mislabeled lines** (a PH alternate line reading "12th Floor").
- **Proposal cross-references** (alternates citing the wrong clarification number) and **rounding** vs the proposal.
- **Export SOV tabs** that roll alternates into the contract sum; don't send those.
- **Drawing open items** that change price (missing plans, after-hours notes, open-ended violation clauses).

Notes & Clarifications carries commercial terms only: exclusions with reasons, basis of quantities
(drawing set and issue date), allowances, unresolved selections. No process or tooling language.

## Verification (every build)

1. Base TOTAL on the Estimate and on the SOV equals the Cost Detail base bid to the cent.
2. Every alternate TOTAL on the Estimate equals its SOV Burdened Total, and every proposal alternate shows $0.00 variance (or the variance is a Review finding).
3. Scan every formula cell with `data_only=True`: zero `#` / `Err:` values, and a line extension and a TRADE TOTAL come back as numbers.
4. Stress test on a copy: enter a lump-sum sub bid, a line-item sub bid, a base Final Price and an alternate Final Price, change a markup %, recalc through LibreOffice, and check the ladders by hand. No Err:522 / Err:523 (circular).
5. Render to PDF and look: headers clean (no line through the name), alternates start on a new page at row 401, SOV alternates on their own page.
6. Tell Matt the Quantity Basis sheet is hidden, not removed.

## Critical rules

1. NEVER invent a quantity or rate. Rates come from exact_total / qty.
2. NEVER drop a line. Every Cost Detail line matches an export row or the build stops.
3. ALWAYS run finalize.py; ALWAYS verify the merged-cell borders in the render.
4. ALWAYS keep CSI left of the trade name and out of the Estimate trade headers.
5. ALWAYS give every alternate the full Subtotal / GC / Fee / Insurance / Total ladder, linked to the base percentages.
6. NEVER hard-code a total on the SOV; everything links to the Estimate.
7. Version up the file name; never overwrite a delivered version.

## Files

- `scripts/build_estimate.py` -- the workbook builder. Owns the grid, the formulas, the sheet order.
- `scripts/finalize.py` -- recalculates through LibreOffice (caches results), repairs merged-cell borders and the outline setting. Requires `soffice`.
