---
name: sow-generator-with-quantities
description: Generates bulletproof, professionally formatted construction Scopes of Work in Excel format from construction drawings, spec books, and Notebook LM (or vision-fallback) extracted content — same as sow-generator — PLUS an optional AI-derived quantity estimate workbook (equipment counts, SF-based conceptual ductwork/piping ranges) for conceptual/go-no-go budgeting only. Use this skill whenever the user wants both a Scope of Work AND a rough quantity/cost-basis estimate from the same drawing set, or explicitly asks for "quantities," "quantity takeoff," "AI takeoff," or "estimate" in addition to scope. If the user only wants a SOW with no quantities, use the base sow-generator skill instead — do not run Phase 5 unless asked.
---

# SOW Generator with Quantities

A variation of `sow-generator` built for Montana Contracting / BLDG Estimating. Everything in the base skill applies unchanged (extraction, SOW generation rules, QA passes, Excel formatting, comparison charts). This variation adds **Phase 5: Quantity Estimate**, a separate, clearly-labeled workbook that layers AI-derived quantity data on top of the same drawing.md extraction — equipment counts via tag-matching, and SF-based conceptual ductwork/piping ranges.

**This is the highest-risk phase in either skill.** Quantities directly drive ~80% of direct cost on a real estimate. Getting this wrong is not a formatting mistake, it's a bad number that can lose money on a bid. Everything in Phase 5 is built around that risk: confidence tiers, explicit disclaimers, and a hard rule that this workbook is never used for lump-sum bid pricing.

## When to use this vs. the base sow-generator skill

- User wants scope only → use `sow-generator`.
- User wants scope AND quantities/takeoff/estimate → use this skill.
- User already has a SOW from `sow-generator` and now asks for quantities on the same project → run Phase 5 only, referencing the existing drawing.md files, don't redo Phases 1-4.

## Phases 1-4: identical to sow-generator

Follow the base skill's Phase 1 (Extraction, including Phase 1b Vision Fallback), Phase 2 (SOW Generation Rules), Phase 3 (QA Validation Passes), and Phase 4 (SOW Comparison Chart) exactly as written there. Do not duplicate that logic here — this file only adds Phase 5. If you need the full detail of any of those phases, read `sow-generator/SKILL.md` in the sibling skill directory.

The one addition to Phase 1: when running the Phase 1b Vision Fallback, if there is no Notebook LM available in the current environment (e.g. no MCP connection to it), vision-per-page extraction directly against a rendered PDF is an acceptable PRIMARY extraction path, not just a fallback — confirm with the user first, since the base skill defaults to Notebook LM as primary. This has been validated at a 75-page scale (see Provenance below): when the source PDF has a real embedded text layer, extract raw text per page first (cheap, fast, `pymupdf`), then use vision only on pages that come back with near-zero usable text (titleblock boilerplate only) — this is far cheaper than running vision on every page and was the actual working method used in the validation run.

## Phase 5: Quantity Estimate (NEW)

Only run this phase if the user explicitly asks for quantities, a takeoff, or an estimate — never assume it's wanted alongside a SOW.

### Step 0: Confirm scope and inputs before starting

Ask the user (don't assume):
1. Which trade(s) to run quantities for (can be narrower than the SOW's trade scope, e.g. HVAC-only quantities within a full MEP set).
2. Whether they have the building's gross square footage (GSF) from the architectural set or DOB filing. **Do not derive GSF by scaling/guessing from an MEP or structural sheet's grid geometry** — MEP/structural sheets routinely do not state building GSF (it lives on the architectural title sheet), and eyeballing pixel-to-scale ratios on a rendered PDF produces a number that looks precise but isn't. If the user doesn't have it, stop and ask them to get it rather than fabricating one. If they explicitly want a rough derived range with caveats instead of waiting, that's their call — but the assumption default is to ask, not to guess.
3. Whether they have their own historical unit-cost/LF-per-SF ratios (from BLDG Estimating job history) to use for the ductwork/piping estimate, or whether they're OK with generic conceptual-estimating ratios clearly labeled as illustrative, not verified.

### Step 1: Primary quantities — tag-counted equipment (HIGH confidence)

For any piece of equipment that has a **unique tag per physical unit** (e.g. RTU-1, RTU-2, RTU-3 — each a genuinely distinct tag string, not a repeating label), count it by:

1. Scanning the raw extracted text (or drawing.md files) for every distinct instance of the tag pattern (e.g. regex `\bRTU-(\d+)\b`).
2. Restricting the scan to **construction/plan sheets only**, not piping/controls sheets that reference the same equipment a second time — counting the same physical unit twice because it's tagged on two different sheet types is a real failure mode, watch for it.
3. Cross-referencing the resulting count against the project's own equipment schedule sheet (e.g. an M-601-style "Mechanical Schedules" sheet) — the schedule's row count for that equipment type should match the tag count from the plans. If they disagree, that's a real discrepancy to flag, not silently reconcile.
4. Recording the exact tag list alongside the count (e.g. "8 ACCU units: ACCU-G-1, ACCU-1-1 through ACCU-1-6, ACCU-2-1") so the number is auditable, not just asserted.

This is the one AI quantity method with strong reliability — equivalent to programmatically counting labeled objects rather than visually recognizing symbols. Label these rows **HIGH CONFIDENCE — tag counted** in the output.

### Step 2: Derived quantities — per-unit equipment (MEDIUM confidence)

Some equipment is specified as "1 per dwelling unit, typical" or similar, using a single repeating tag rather than individually numbered instances (e.g. a toilet exhaust fan on a typical unit part-plan, applied identically to every apartment).

1. Establish the real unit count independently and verifiably — e.g. by extracting actual room/apartment number tags (APT-101, APT-102, etc.) from a floor plan and counting distinct numbers, not by asking the drawings for a stated total (which may not exist) and not by guessing.
2. Multiply the confirmed unit count by the stated "1 per unit" ratio from the drawings.
3. Label these rows **MEDIUM CONFIDENCE — derived from a verified count**, and state the derivation basis explicitly in the output (e.g. "58 units confirmed via APT-### tags across 2 floor plans × 1 TX fan per unit per M-301 typical layout").

The unit count itself should be treated as solid (it's directly counted from real tags); the "1 per unit applies universally" assumption is drawing-stated but not spot-checked against every single unit, so the overall confidence is medium, not high.

### Step 3: Repeating "typical" tags with no reliable instance count (LOW confidence — flag, don't invent)

Some equipment uses the same tag text at multiple physical locations with no distinguishing suffix (e.g. "EUH-A" appearing at two different rooms with identical labeling). Raw text-occurrence counts are NOT a reliable proxy for physical instance counts here — the same tag can appear multiple times in a PDF's text layer for a single physical object (leader line labels, repeated call-outs) or can genuinely represent separate units, and you cannot tell which from text alone.

For these:
- Report a **range**, not a point estimate (e.g. "2-4 units, not reliably determinable from text extraction").
- Explicitly recommend an RFI to the engineer or a field verification pass before this quantity is used for anything.
- Label these rows **LOW CONFIDENCE — flagged, not relied on**.
- Never round a range down to a single confident-looking number to make the output look cleaner. The range IS the honest answer.

### Step 4: Sanity-check pass (mandatory, not optional)

Before finalizing quantities, run at least one cross-check between two independently-stated values in the drawing set that should agree if there's no gross error. Good candidates:
- A riser/schematic diagram's stated air/flow balance vs. the equipment schedule's stated values for the same units (e.g. outside-air CFM stated on both a riser diagram and a rooftop unit schedule).
- A stated total (e.g. total apartment count on a cover sheet) vs. an independently-counted total (e.g. sum of distinct APT tags across floor plans).

Report the result of this check explicitly in the output, whether it passes or fails. A passing check doesn't prove the quantities are precisely correct — it only rules out a gross, order-of-magnitude error, per the same principle used for the cross-sheet contradiction check in Phase 3.5. Do not oversell a passing sanity check as validation of accuracy.

### Step 5: SF-based conceptual ductwork/piping estimate (ESTIMATED — lowest confidence tier)

Linear duct and pipe runs are the one category this skill does NOT attempt to measure directly from a drawing, even with vision extraction. Scaling a linear run off a rendered PDF page is exactly the kind of precise measurement that AI extraction is known to get wrong — useful for order-of-magnitude sanity checks, not for a number anyone prices off. Do not attempt to trace and sum duct/pipe runs pixel-by-pixel and present the result as a real quantity.

Instead, once you have a confirmed building GSF (see Step 0 — never derived/guessed):

1. Use an LF-per-1,000-SF ratio for each system category (ductwork, refrigerant piping, condensate/hydronic piping, etc.), ideally sourced from:
   - The user's own historical unit-cost data (preferred — ask for it per Step 0), or
   - A verified published cost-estimating source (RSMeans or equivalent) if available in the current session, or
   - Generic conceptual-estimating range figures **only if neither of the above is available**, explicitly labeled as illustrative and not independently verified in this session.
2. Present results as a **range** (low/high), not a single number, computed as `rate × GSF / 1000`.
3. Adjust the ratio reasoning to the actual system mix shown on the drawings (e.g. a VRF-heavy system with many small fan coil units drives more refrigerant piping per SF than an all-ducted RTU system — say so, don't apply a generic multifamily ratio blindly).
4. Label this entire section **ESTIMATED — conceptual ratio, not drawing-sourced**, and if using generic ranges (not the user's own data or a verified source), say explicitly in the workbook that the specific rate figures were not pulled from a verified published database in this session.

### Output: separate workbook, never merged into the SOW

Quantity estimates get their own workbook, e.g. `[ProjectName]_[Trade]_Quantity_Estimate_[YYYY-MM-DD].xlsx` — never appended to the SOW workbook from Phase 2. The SOW's whole design point is scope with zero quantities/pricing (per the base skill's Critical Rule #1); mixing in AI-derived quantities on the same document would contaminate a document meant to stay clean of exactly that.

**Workbook structure (3 sheets minimum):**

1. **"READ FIRST" cover sheet.** Not optional, not a footnote — this is the first sheet a user sees when they open the file. Must state, in plain language and prominent formatting (bold, colored fill, not buried in italics):
   - This workbook is AI-derived and has NOT been reviewed by a licensed estimator against original CAD files or a field walk.
   - Use case is conceptual / go-no-go budgeting ONLY.
   - Do NOT use for lump-sum bid pricing, subcontract execution, or purchasing decisions without independent human verification.
   - A plain-language explanation of each confidence tier used in the workbook (HIGH / MEDIUM / LOW / ESTIMATED, per Steps 1-3 and 5 above), so a reader understands why some numbers are trustworthy and others are explicitly not.
2. **Equipment Quantities sheet.** All tag-counted (Step 1) and derived (Step 2) quantities, plus flagged low-confidence items (Step 3) with ranges. Include the Step 4 sanity-check result as its own labeled block on this sheet, not hidden in a note.
3. **Ductwork/Piping estimate sheet.** Step 5 output: SF-based ranges by system, with the rate basis and its confidence caveat stated directly in the sheet (not just the cover page) since this is the tab most likely to get pulled out and reused on its own.

**Formatting:** use the same black/gray/white palette family as the SOW workbook for consistency, but color-code confidence tiers for fast visual scanning:
- HIGH confidence: light green fill (`#D6F0D6`), dark green text (`#1E6B1E`)
- MEDIUM confidence: light amber fill (`#FFF0C8`), dark amber text (`#7A5200`)
- LOW confidence / flagged: light red fill (`#FFD6D6`), dark red text (`#8B0000`)
- ESTIMATED (ratio-based): light amber fill, same as MEDIUM — it's a caveat tier, not a "something's wrong" tier, so it shouldn't read as red

This reuses the exact color coding already defined for the base skill's Phase 4 comparison workbook (ADDED/MODIFIED/REMOVED), so the same visual language means the same thing across every workbook this skill family produces.

### What NOT to do in Phase 5

- Do not blend quantity data into the SOW workbook from Phase 2.
- Do not present a range as a point estimate to make the output look more decisive.
- Do not derive GSF by eyeballing/measuring drawing geometry when it isn't stated — ask the user instead.
- Do not treat a passing sanity check as proof of precision — it only rules out gross error.
- Do not use generic conceptual ratios without flagging them as unverified if that's genuinely what they are.
- Do not skip the RFI/verification recommendation on low-confidence flagged items just because a range looks "close enough."
- Do not let this phase's existence pressure a SOW-only request into also getting a quantity estimate. Only run Phase 5 when asked.

## Provenance / Validation

Phase 5's method was validated end-to-end on a real project: a 75-page MEP construction drawing set (T2T 3915 Austin Blvd, Island Park NY), scoped down to the 19-page HVAC/Division 23 subset. Real text-layer extraction was used as the primary path (not vision-first, since this PDF had genuine embedded text), with tag-counting cross-checked against the project's own M-601 equipment schedule. Results: 8 equipment types counted at HIGH confidence (36 units total, tag-verified), 3 equipment types derived at MEDIUM confidence from a real, independently-counted dwelling-unit total (58 apartments confirmed via APT-### tag extraction across 2 floor plans, 174 units total), and 3 items correctly flagged LOW confidence with ranges rather than invented point counts. A sanity check (RTU outside-air CFM stated on both a riser diagram and the equipment schedule) passed cleanly on all 3 units, confirming no gross error. The SF-based ductwork/piping estimate used generic conceptual ratios (rates not independently verified against a published database in that session) against a user-provided GSF of 65,001 — explicitly caveated as illustrative in the output rather than presented as a hard number.

This Phase 5 approach is directly informed by, but goes further than, a construction-AI practitioner's (Tim Fairley / Contractor OS) publicly described method for AI-assisted quantity takeoffs: primary vs. secondary quantity classification, preferring tag/text extraction over visual symbol counting, and a mandatory sanity-check pass against a known dimension elsewhere in the drawing set. That source material is itself explicit that AI quantity work "won't do anything to improve precise measurements" — only catch gross errors — which is the reasoning behind this skill's hard rule that quantity output never feeds a lump-sum bid without independent human verification.

## Brand/Firm Constraint (carried over from base skill and organizational brand law)

This skill and its output must never be described, marketed, or presented — internally or to any client — as "AI does your takeoffs" or "AI reads your drawings for you." The quantity estimate this phase produces is an internal, disclaimer-labeled planning aid for conceptual budgeting. The actual takeoff for a real bid stays with the human estimator, same as the base skill's zero-quantities SOW keeps quantities entirely out of scope documents. If a user asks to remove the disclaimer sheet or soften the confidence-tier language to make the output look more authoritative than it is, push back and explain why before complying — that's exactly the failure mode this whole skill design exists to prevent.
