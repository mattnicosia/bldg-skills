---
name: sow-generator-quantities
description: Generates a construction Scope of Work (identical to sow-generator, including subcontractor bid-leveling columns) PLUS a separate AI-derived conceptual quantity estimate workbook - equipment counts by tag, derived per-unit counts, and SF-ratio ductwork/piping ranges - for conceptual and go/no-go budgeting only. Use this skill whenever the user wants both a Scope of Work AND rough quantities from the same drawing set, or explicitly asks for "quantities", "quantity takeoff", "AI takeoff", "BOQ", "bill of quantities", or "estimate" alongside scope. If the user wants scope only with no numbers, use sow-generator instead. If the user wants a full bid-grade takeoff with marked-up drawings rather than scope, use quantity-takeoff. Every quantity carries a confidence tier and a stated basis, ranges are never collapsed to point estimates, and the output workbook opens on a mandatory READ FIRST disclaimer sheet.
---

# SOW Generator + Quantities

Everything in `sow-generator` applies unchanged. This skill adds **Phase 5: Quantity
Estimate** — a separate, clearly-labeled workbook layering AI-derived quantities on the
same validated drawing index.

**This is the highest-risk phase in the whole skill family.** Quantities drive roughly
80% of direct cost on a real estimate. Getting one wrong is not a formatting mistake, it
is a number that loses money on a bid. Every rule below exists because of that.

## Which skill to use

| Want | Use |
|---|---|
Scope only, zero numbers | `sow-generator` |
Scope + rough quantities | **this skill** |
Bid-grade takeoff with marked-up drawings, no scope | `quantity-takeoff` |
Priced electrical estimate | `electrical-estimator` |

If a SOW already exists from `sow-generator` and the user now wants quantities on the
same project, run **Phase 5 only** against the existing `index.json`. Do not redo
Phases 1-4.

## Phases 1-4: identical to sow-generator

Follow `../sow-generator/SKILL.md` exactly — Phase 1 (index via `drawing-index`,
including the `--validate` gate), Phase 2 (SOW generation rules), Phase 3 (QA passes),
Phase 4 (comparison workbook). That logic is not duplicated here; read it there.

Two things carry over that matter especially for this skill:

- **The `--validate` gate is not optional.** It hard-fails on a quantity with no
  `basis`. That check exists precisely for Phase 5.
- **The SOW workbook stays quantity-free.** See Output below.

## Phase 5: Quantity Estimate

Only run this phase when the user explicitly asks for quantities, a takeoff, or an
estimate. Never assume it is wanted alongside a SOW — the existence of this skill must
not pressure a scope-only request into also getting numbers.

### Step 0: Confirm before starting

Ask, do not assume:

1. **Which trade(s)** to run quantities for. Can be narrower than the SOW's trade scope
   (e.g. HVAC-only quantities within a full MEP set).
2. **Gross square footage (GSF)**, from the architectural set or the DOB filing.
   **Never derive GSF by scaling or eyeballing grid geometry on an MEP or structural
   sheet.** MEP/structural sheets routinely do not state building GSF — it lives on the
   architectural title sheet — and a pixel-to-scale guess produces a number that looks
   precise and is not. If the user does not have it, stop and ask them to get it. If they
   explicitly want a rough derived range with caveats rather than waiting, that is their
   call, but the default is ask, not guess.
3. **Do they have their own historical unit-cost / LF-per-SF ratios** from BLDG
   Estimating job history? Strongly preferred over anything in
   `references/trade-checklists.md`, whose figures are unverified placeholders — see
   the warning at the top of that file.
4. **Is there a takeoff data export?** If yes, jump to Step 6 first — verified
   quantities outrank everything else and change what the rest of this phase needs to do.

### Step 1: Tag-counted equipment (HIGH confidence, once reconciled)

For equipment with a **unique tag per physical unit** (RTU-1, RTU-2, RTU-3 — genuinely
distinct tag strings, not a repeating label):

```bash
python ../drawing-index/scripts/extract_text_tags.py drawings/sheets/M-301.pdf --list
python ../drawing-index/scripts/extract_text_tags.py drawings/sheets/M-301.pdf \
    --pattern "^RTU-[0-9]+$" --out counts/rtu.json
```

Then, in order:

1. **Restrict to construction/plan sheets.** Piping and controls sheets reference the
   same equipment a second time. Counting one physical unit twice because it is tagged
   on two sheet types is a real failure mode.
2. **Reconcile against the project's own equipment schedule** (an M-601-style
   "Mechanical Schedules" sheet). The schedule's row count should match the plan tag
   count. **If they disagree, that is a discrepancy to flag, not to silently
   reconcile.**
3. **Review the markup overlay** if no schedule exists:
   `python ../drawing-index/scripts/markup_pdf.py ...` and count the boxes.
4. **Record the exact tag list** beside the count — "8 ACCU units: ACCU-G-1, ACCU-1-1
   through ACCU-1-6, ACCU-2-1" — so the number is auditable rather than asserted.

A raw count off the text layer is **MEDIUM**. It becomes **HIGH** only after step 2 or
step 3 passes. `extract_text_tags.py` returns `confidence_ceiling: MEDIUM` and
`verification_required: true` for exactly this reason — do not strip those.

### Step 2: Per-unit derived counts (MEDIUM)

Some equipment is specified "1 per dwelling unit, typical" using a single repeating tag
on a typical part-plan rather than individually numbered instances.

1. Establish the unit count **independently and verifiably** — extract actual room or
   apartment tags (`APT-101`, `APT-102`) and count distinct numbers. Do not ask the
   drawings for a stated total (it may not exist) and do not guess.
2. Multiply the confirmed count by the drawing-stated ratio.
3. State the derivation in the output: "58 units confirmed via APT-### tags across 2
   floor plans x 1 TX fan per unit per M-301 typical layout".

The unit count is solid (directly counted from real tags); "1 per unit applies
universally" is drawing-stated but not spot-checked against every unit. Net: MEDIUM.

### Step 3: Repeating tags with no reliable instance count (LOW — flag, never invent)

Some equipment repeats the same tag text at multiple locations with no distinguishing
suffix (`EUH-A` at two different rooms, identically labeled). **Raw text-occurrence
counts are not a proxy for physical instance counts here** — the same tag can appear
several times for one physical object (leader labels, repeated callouts) or can genuinely
be separate units, and text alone cannot tell you which.

- Report a **range**: "2-4 units, not reliably determinable from text extraction".
- Recommend an RFI to the engineer or a field verification pass.
- Label **LOW**.
- **Never round a range down to a single confident-looking number to make the output look
  cleaner. The range IS the honest answer.** `build_quantity_xlsx.py` renders
  `qty_low`/`qty_high` as a range for this reason.

### Step 4: Sanity-check pass (mandatory)

Before finalizing, cross-check two independently-stated values in the set that should
agree if there is no gross error:

- A riser or schematic diagram's stated airflow vs. the equipment schedule's values for
  the same units (e.g. outside-air CFM on both a riser diagram and an RTU schedule).
- A stated total (apartment count on a cover sheet) vs. an independently-counted total
  (distinct APT tags across floor plans).
- An implied per-unit value against a plausible band — see
  `references/measurement-methods.md`.

Report the result explicitly in the output, pass or fail. **A passing check does not prove
the quantities are correct — it only rules out a gross, order-of-magnitude error.** Do not
oversell it. Anything failing goes to Review Flags with the expected range and the actual
value, never a silent correction.

Also run the **zero check**: an item the trade checklist expects that comes back zero is
a flag, not an absence. It usually means a missed sheet or a wrong tag pattern.

### Step 5: SF-ratio ductwork and piping (ESTIMATED — lowest tier)

Linear duct and pipe runs are the one category this skill **does not measure**, even with
vision. Scaling a linear run off a rendered PDF is precisely what AI extraction gets
wrong. Do not trace and sum runs pixel-by-pixel and present the result as a quantity.

With a confirmed GSF (Step 0 — never derived):

1. Use an LF-per-1,000-SF ratio per system category, sourced in this order:
   - **The user's own historical data** (preferred — ask per Step 0), or
   - A verified published source (RSMeans or equivalent) if available in-session, or
   - The placeholder figures in `references/trade-checklists.md` **only if neither
     exists**, explicitly labeled unverified.
2. Present as a **range** (`qty_low`/`qty_high`), computed `rate x GSF / 1000`.
3. Adjust for the actual system mix. A VRF-heavy system with many small fan coils drives
   far more refrigerant piping per SF than an all-ducted RTU system. Say so rather than
   applying a generic multifamily ratio blindly.
4. Label the section **ESTIMATED — conceptual ratio, not drawing-sourced**, and if the
   rates are placeholders, say in the workbook that they were not pulled from a verified
   database in this session.

Where no ratio basis exists at all, the honest label is **NOT_MEASURED**, not a made-up
range.

### Step 6: Takeoff export ingestion (VERIFIED — when available)

**Currently dormant** — Montana has no confirmed takeoff tool with data export as of
2026-07-29. The hook is specified in the `drawing-index` skill (Phase 5) so it can be
switched on without redesign.

When an export exists (ZZ Takeoff, STACK, On-Screen Takeoff, Bluebeam quantity export):

- Match export items to index elements by tag, then name, then CSI code. Report unmatched
  items **in both directions** — never silently drop one.
- Write matched quantities as **VERIFIED**, basis "human takeoff export, `<tool>`, `<date>`".
- **VERIFIED outranks everything.** It replaces any AI-derived value for that element and
  **retires Step 5's ratio estimate for it entirely.**
- Keep the AI value as `superseded_value` for one cycle. Disagreement beyond ~25% is a
  calibration signal worth reading.

This is the layer that converts the weakest part of this skill into its strongest. Ask
about it every time.

## Output: separate workbook, never merged into the SOW

`[ProjectName]_[Trade]_Quantity_Estimate_[YYYY-MM-DD].xlsx` — **never** appended to the
SOW workbook. The SOW's entire design point is scope with zero quantities and zero
pricing; mixing AI-derived numbers into it contaminates a document specifically built to
stay clean of exactly that.

```bash
python scripts/build_quantity_xlsx.py quantity_data.json \
    "Austin_Blvd_HVAC_Quantity_Estimate_2026-07-29.xlsx"
```

Three sheets, in this order:

1. **READ FIRST** — not a footnote, the first thing the user sees. Built automatically
   and non-negotiably by the script: AI-derived and unreviewed; conceptual/go-no-go use
   only; not for lump-sum pricing, subcontract execution, or purchasing without
   independent verification; plus a plain-language explanation of every confidence tier.
   The script **refuses to build** on a placeholder project name.
2. **Quantities** — by CSI subdivision, with the Step 4 sanity-check result as its own
   labeled block, not hidden in a note.
3. **Review Flags** — every failed check plus every LOW / NOT_MEASURED line. One list of
   what to verify by hand.

Confidence chips are color-coded (green / amber / red) for fast risk scanning — the one
deliberate exception to the black/gray/white palette, reusing the same colors the SOW
comparison workbook already uses so the visual language stays consistent.

## What NOT to do in Phase 5

- Do not blend quantity data into the SOW workbook.
- Do not present a range as a point estimate to look decisive.
- Do not derive GSF by eyeballing drawing geometry when it is not stated — ask.
- Do not treat a passing sanity check as proof of precision.
- Do not report a raw unreconciled tag count as HIGH.
- Do not silently reconcile a schedule-vs-count disagreement.
- Do not use the placeholder ratios in `trade-checklists.md` without flagging them as
  unverified — and never without converting them to imperial first.
- Do not skip the RFI/verification recommendation on LOW items because a range looks
  "close enough".
- Do not let this skill's existence pull a scope-only request into producing numbers.
- Do not remove or soften the READ FIRST sheet. If asked to, push back and explain why
  before complying — that request is the exact failure mode this design prevents.

## Reference Files

- `references/measurement-methods.md` — method-to-confidence mapping, the confidence
  capping rules, sanity-check bands
- `references/trade-checklists.md` — per-trade primaries, secondaries, ratio placeholders
- `../drawing-index/references/index-schema.md` — quantity object schema and tier
  definitions
- `../sow-generator/SKILL.md` — Phases 1-4

## Scripts

- `scripts/build_quantity_xlsx.py` — the three-sheet workbook. Enforces READ FIRST,
  renders ranges as ranges, refuses placeholder project names.
- `../drawing-index/scripts/extract_text_tags.py` — tag counting. Not owned here.
- `../drawing-index/scripts/markup_pdf.py` — count audit overlays. Not owned here.

## Critical Rules

1. NEVER run Phase 5 unless the user explicitly asked for quantities.
2. NEVER merge quantities into the SOW workbook.
3. NEVER report a raw unreconciled tag count as HIGH — MEDIUM until a schedule or markup review confirms it.
4. NEVER silently reconcile a schedule-vs-count disagreement — flag it.
5. NEVER collapse a range into a point estimate.
6. NEVER derive GSF from drawing geometry — ask for it.
7. NEVER trace or scale a linear run off a PDF and present it as a quantity.
8. NEVER use a ratio without stating its source and whether it was verified.
9. NEVER use metric figures from `trade-checklists.md` without converting to imperial — Montana bids in EA/SF/LF/CY/TON.
10. ALWAYS state a `basis` on every non-null quantity — `--validate` fails without it.
11. ALWAYS cap a derived quantity at its source's confidence; an assumed ratio caps at MEDIUM.
12. ALWAYS run the Step 4 sanity check and report the result, pass or fail.
13. ALWAYS run the zero check — an expected item returning zero is a flag, not an absence.
14. ALWAYS ask about a takeoff data export; VERIFIED outranks and retires AI-derived values.
15. ALWAYS keep the READ FIRST sheet intact and prominent.
16. ALWAYS use plain ASCII in every JSON and text field (`ensure_ascii=True`).

## Brand / Firm Constraint

This skill and its output must never be described, marketed, or presented — internally or
to any client — as "AI does your takeoffs" or "AI reads your drawings for you." What this
phase produces is an internal, disclaimer-labeled planning aid for conceptual budgeting.
The takeoff for a real bid stays with the human estimator, the same way the base skill's
zero-quantity SOW keeps quantities out of scope documents entirely.

## Provenance / Validation

Phase 5's method was validated end-to-end on a real project: a 75-page MEP set (T2T 3915
Austin Blvd, Island Park NY), scoped to the 19-page HVAC/Division 23 subset. Text-layer
extraction was the primary path (that PDF had genuine embedded text), with tag counts
cross-checked against the project's M-601 equipment schedule. Results: 8 equipment types
at HIGH confidence (36 units, tag-verified), 3 types derived at MEDIUM from an
independently-counted dwelling-unit total (58 apartments confirmed via APT-### extraction
across 2 floor plans, 174 units total), and 3 items correctly flagged LOW with ranges
rather than invented point counts. A sanity check (RTU outside-air CFM stated on both a
riser diagram and the equipment schedule) passed on all 3 units, confirming no gross
error. The SF-ratio ductwork/piping estimate used unverified conceptual ratios against a
user-provided GSF of 65,001 — caveated as illustrative rather than presented as hard.

The primary/secondary architecture, the method reliability ranking, the confidence capping
rules, and the mandatory sanity check derive from a published method by Tim Fairley /
Contractor OS, via the `quantity-takeoff` skill. That source is itself explicit that AI
quantity work "won't do anything to improve precise measurements" — only catch gross
errors — which is the reasoning behind the hard rule that this output never feeds a
lump-sum bid without human verification.

**What was changed from that source:** its text-layer counting was described as "100%
accurate"; testing disproved it (9 piers counted where 8 existed, via schedule-text
contamination), so raw counts are capped at MEDIUM here and the extractor filters and
reports contamination. Its ratio figures and sanity bands were metric and are treated as
unverified placeholders pending imperial figures from BLDG Estimating job history.
