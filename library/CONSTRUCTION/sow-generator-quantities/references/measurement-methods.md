# Measurement Methods, Confidence Mapping, and Sanity Checks

Imperial units throughout: `EA`, `SF`, `LF`, `CY`, `TON`, `CFM`, `lb/CY`, `in`, `ft`.
Montana Contracting / BLDG Estimating bids in imperial. Metric figures from earlier
versions of this file were converted, and every converted band is flagged because the
underlying figure was never verified against BLDG job history.

## Method reliability ranking (use the highest available for each item)

1. **Human takeoff export** — a real measured quantity from takeoff software. The only
   fully trustworthy source and the only tier suitable for pricing. Ask whether one
   exists before doing anything below.
2. **Schedule extraction** — a table on the drawings already lists the quantity (pier
   schedule, fixture schedule, panel schedule). The most reliable AI path when the
   schedule is complete. **Always check for a schedule before counting or measuring.**
3. **Text-tag count** (vector PDF) — count selectable tokens programmatically with
   `extract_text_tags.py`. Reliable, but see "The over-count ceiling" below. Not a 100%
   path.
4. **Explicit-dimension extraction** — a dimension noted as text on a plan or section
   (slab depth, member length, duct size). Reliable because it is *read*, not measured.
5. **Vision count** (image-only PDF) — a model counts symbols visually. Significantly
   less reliable. Always LOW. Tell the user to verify every count.
6. **Scaled measurement** — tracing a polyline against the drawing scale (pipe run, slab
   outline with no dimension). Least reliable for AI. Last resort. Always LOW.

## The over-count ceiling (read before assigning HIGH to any count)

A text-layer tag count is **MEDIUM confidence, not HIGH**. The text layer cannot
distinguish a tag placed on a plan from the same string in a schedule row, a legend, a
keynote list, or a revision block. A sheet with 8 physical P1 piers and a schedule reading
`PIER SCHEDULE P1 QTY 8` returns 9 unless filtered.

Verified failure, not a hypothetical. The method this file derives from called text-layer
counting "100% accurate". It is not.

`extract_text_tags.py` filters same-line context keywords by default and reports every
exclusion with its reason. Promote MEDIUM to HIGH only after **one** of:

- **Schedule reconciliation** — the sheet's own schedule row count agrees with the tag
  count. Disagreement is a flag to surface, never a silent pick.
- **Markup review** — generate the overlay with `markup_pdf.py`, open it, count the boxes.

Restrict counts to construction/plan sheets. Piping and controls sheets reference the same
equipment a second time; counting one physical unit twice across two sheet types is a real
failure mode.

## Vector vs. image-only

`drawing-index` classifies every page. Per page:

- **`vector`** — text-tag counts and dimension extraction available. HIGH reachable after
  reconciliation.
- **`sparse`** — thin text layer, commonly a titleblock that read while the rest of the
  page is a bitmap. Counts allowed but MEDIUM at best; verify.
- **`image_only`** — no usable text layer. Vision count or scaled measurement only. LOW.

Never assume vector. A single set is routinely mixed — vector structural sheets, scanned
details, raster MEP schedules.

## Confidence mapping

| Method + condition | Confidence |
|---|---|
| Human takeoff export | VERIFIED |
| Clean schedule extraction | HIGH |
| Text-tag count **reconciled** against a schedule or markup review | HIGH |
| Explicit dimension on a vector/clean page | HIGH |
| Text-tag count, **unreconciled** | MEDIUM |
| Schedule with minor ambiguity, or a partial schedule | MEDIUM |
| Text-tag count on a `sparse` page | MEDIUM |
| Secondary derived from a HIGH primary using an **assumed** ratio | MEDIUM |
| SF-ratio conceptual estimate | ESTIMATED |
| Vision count (image-only) | LOW |
| Scaled measurement (any) | LOW |
| Secondary derived from a LOW primary | LOW (capped) |
| Not determinable from the drawings at all | NOT_MEASURED |

### The two capping rules

The highest-value rules in this file. They structurally prevent laundering a weak
measurement into a strong-looking derived number.

1. **A derived quantity can never exceed its source's confidence.** A concrete volume
   computed from a LOW slab area is LOW, however clean the depth note is.
2. **A derivation whose ratio is *read off the drawings* keeps the source's confidence; a
   derivation whose ratio is *assumed* caps at MEDIUM.** A depth from a section note or a
   unit weight from a steel table is read. "15 LF of cable per outlet" is assumed.

`NOT_MEASURED` is a legitimate, professional answer. It is the correct label for nearly
every linear duct and pipe run. Prefer it over a fabricated range.

## Sanity checks (run on every quantity)

These catch order-of-magnitude errors — off by 5x or 10x — not fine precision. Record
every result, pass or fail. Route failures to Review Flags with the expected range and the
actual value. **Never silently correct a flagged value.**

A passing sanity check does not prove accuracy. It rules out gross error. Do not oversell
it.

### Cross-ratio / geometry check

A run that should span a known building dimension N times should land near N x that
dimension. Building 150 ft long, conduit runs its length twice: expect ~300 LF. A result of
50 LF or 700 LF is a flag.

### Per-unit reasonableness bands

Flag anything outside. **Every band below is a converted placeholder — replace with BLDG
Estimating job-history figures when available.**

| Implied value | Expected band | Status |
|---|---|---|
| Slab thickness = concrete CY x 27 / slab SF | 6 - 16 in | converted, UNVERIFIED |
| Rebar rate = rebar lb / concrete CY | 135 - 420 lb/CY (tighter per element — see trade checklists) | converted, UNVERIFIED |
| Steel unit weight = member TON x 2000 / total LF | sane lb/ft for the section called out | use the section table, never estimate |
| Cable per point = total cable LF / point count | 25 - 65 LF | converted, UNVERIFIED |

### Density / coverage check

Outlets per SF, fixtures per room, piers per structural grid, diffusers per zone — compare
against rough norms for the building type. A warehouse showing residential outlet density
is a flag.

### Schedule vs. count reconciliation

When both a schedule quantity and a tag count exist for the same item, they should agree. A
mismatch is a flag — often a legend or keynote entry being miscounted, or a schedule that
excludes alternates. **Resolve it explicitly; do not pick one quietly.**

### Zero / null check

An item the trade checklist expects but that returns zero (a concrete job with no footing
count) is a **flag**, not an absence. It usually means a missed sheet or a wrong tag
pattern. This inverted check catches gaps that checking only what is present never will.

### Cross-document check

A stated total on one sheet vs. an independently-counted total from another (apartment count
on a cover sheet vs. distinct APT-### tags across floor plans). On a residential set this
is the single most useful confirmation available.

## What a flag must record

For each failed check write to `review_flags`: the **item**, the **issue** (which check
failed), the **expected** range, the **actual** value, and the **recommended action**
(usually "verify by hand" or "confirm ratio against schedule").

Every LOW and NOT_MEASURED line is also surfaced in Review Flags by default, so the
estimator has one consolidated list rather than hunting through the workbook.

## Provenance

Adapted from the `quantity-takeoff` skill, whose content derives from a published method by
Tim Fairley / Contractor OS.

**Kept:** the method reliability ranking, the two capping rules, the assumed-vs-read ratio
distinction, the zero/null check, and schedule-vs-count as a flag rather than a silent pick.

**Changed:** all units and bands converted metric to imperial; text-layer counting demoted
from "100% / HIGH" to a MEDIUM ceiling requiring reconciliation; VERIFIED and NOT_MEASURED
tiers added at the top and bottom of the scale.
