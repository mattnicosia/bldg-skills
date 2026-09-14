---
name: create-small-estimate
description: Create a quick Montana Contracting proposal PDF for any client (non-Chrysler/Brix — use chrysler-proposal for those). Trigger on "/create-small-estimate" or when the user wants a fast small-job estimate/proposal without going through the full estimating cycle or ProEst. Runs an interview (client, scope, pricing source, markup, tax), builds an internal pricing worksheet, and renders the branded PDF with an optional CSI Schedule of Values addendum.
---

# /create-small-estimate — Montana Contracting Quick Proposal Builder

Interview → internal pricing worksheet → branded PDF (cover/letter/scope/clarifications, plus an
optional Schedule of Values addendum page). The interview happens through AskUserQuestion, one
question at a time — later questions depend on earlier answers. This exists to expedite small
estimates without the full estimating cycle or ProEst; for Chrysler/Stellantis/Mopar/Brix work,
use the `chrysler-proposal` skill instead — this one is for everyone else.

**The golden rule: the client never sees the math.** Markup (GC/Fee/Insurance, plus any add-on) is
compounded into direct costs before anything is printed. The client-facing PDF shows exactly three
numbers on the cover — Subtotal, Sales Tax, Total — never the markup breakdown. The internal
worksheet stays in the conversation only, and the optional Schedule of Values addendum shows
priced line items by CSI subdivision, never the markup stack.

## Step 1 — Client & project basics

Ask in order, skipping anything already provided:
1. **Client name** — check the conversation/project for a list of past clients and offer them as
   options alongside "someone new." If new, get company, contact, and mailing address.
2. **Project name + location** (location drives sales tax and licensing checks).
3. Commercial or Residential.
4. New Construction or Renovation.
5. Single-phase or multi-phase.

Done when: client block, project name/location, and these four classifiers all exist.

## Step 2 — Scope of work

Ask whether the user will dictate scope items in chat or upload source documents (drawings, spec
excerpts, a written scope) — either is fine, decide per project. If uploaded, read them and echo
back the scope list extracted so the user can correct it before pricing starts.

## Step 3 — Delivery method & self-perform limits

Ask Self-Performed / Subbed Out / Hybrid.

**Hard rule: only Carpenter and Laborer trades are self-performed.** Any other trade (electrical,
mechanical, plumbing, etc.) routes to a subcontractor regardless of the answer above — don't price
those with an internal labor rate.

- Standard self-perform rates: **Carpenter $85/hr, Laborer $55/hr.**
- Self-perform hours are given directly by the user per task — don't estimate hours from
  quantities/productivity rates.
- Self-perform materials/equipment costs: either given by the user or researched by you and
  confirmed with the user — decide per project, ask if unclear.
- Subcontractor costs: either pasted into chat or provided via an uploaded written quote — either
  is fine, decide per project.
- Markup is the **same percentage** regardless of whether a line item is self-performed or subbed
  — don't apply a reduced rate to subs.

Done when: every scope item has a direct cost, a stated source, and (if self-performed) is
confirmed to be Carpenter/Laborer scope only.

## Step 4 — Markup

Default stack, compounding in this order (do not apply as flat addition):
```
Step 1 (GC):         direct costs × 1.10
Step 2 (Fee):         Step 1        × 1.075
Step 3 (Insurance):   Step 2        × 1.03
= SUBTOTAL (client sees)
```
Net effect ≈ 22.4% over direct costs. Only ask about markup if the user wants to override this
default for the project — otherwise apply it silently in the worksheet.

Then ask: should an **additional markup** be applied above and beyond standard? If yes, it's a
flat percentage, defined per project, applied as one more multiplication after Insurance:
```
Step 4 (Add-on):      Step 3 × (1 + add-on %)
= SUBTOTAL (client sees)
```

## Step 5 — Sales tax

- **NY/NJ projects**: default to tax **excluded**, with a written exclusion clause assuming Montana
  Contracting will receive a capital improvement certificate from the client. State this
  assumption explicitly in the Clarifications & Exclusions list.
- **Any other state**: the capital improvement certificate concept does not apply (confirmed: it's
  a NY/NJ-specific sales tax mechanism — e.g. Florida taxes materials on real property improvement
  contracts regardless). Look up the combined state+local rate for the project's jurisdiction, then
  **confirm it with the user before using it**. Label it on the PDF as `Sales Tax (X.X%)`.

## Step 6 — Standing flags (not questions — just watch for these)

- **Out-of-state licensing**: Montana Contracting's stated footprint is NY + NJ. If the project is
  in any other state, flag it to the user (e.g. "this is a Florida project — confirm licensing
  coverage or a locally-licensed sub before this goes out") rather than resolving it silently.
- **Non-NY/NJ tax**: never apply the capital-improvement-certificate exclusion outside NY/NJ.

## Step 7 — Internal pricing worksheet

Show the full worksheet to the user in chat for approval before rendering anything:
```
direct costs (self-perform + subs + materials/equipment)
→ × 1.10 (GC)
→ × 1.075 (Fee)
→ × 1.03 (Insurance)
→ × (1 + add-on %) (if applicable)
= SUBTOTAL (client sees)
Sales Tax (client sees) = SUBTOTAL × tax rate (0 if NY/NJ capital-improvement default)
TOTAL (client sees)     = SUBTOTAL + tax
```
Done when the user approves Subtotal/Tax/Total.

## Step 8 — Schedule of Values (optional addendum)

Ask, per project, whether to include a CSI-subdivision Schedule of Values addendum page. If yes:
- Group line items under CSI subdivision headers (e.g. "26 56 00 · Exterior Lighting") with a
  description and dollar amount per row — these are **priced-out direct-cost-plus-markup amounts
  per item**, never a separate markup line.
- **Multi-phase projects get one SOV with a phase column added to each row** — not separate SOVs
  per phase, not separate documents.
- Group + grand totals must reconcile exactly to the client-facing Subtotal.

## Step 9 — Build and verify the PDF

1. Write the approved values into a `data.json` matching `example_data.json` (all keys required;
   `notes` optional; `sov` optional — omit the whole `sov` key if the addendum wasn't requested).
   Scope items and notes are HTML-escaped strings. Signer defaults to Joseph Montana, President.
2. `python3 scripts/build_proposal.py data.json proposal.html`
3. `python3 scripts/render_and_verify.py proposal.html "Montana Proposal - <Project Name>.pdf" --bg 255,255,255`
4. The verifier checks split content across page boundaries and top-of-page gap consistency
   (spread ≤ 6px). Boundary flags quoting the blue footer band text are expected noise; anything
   else, read and fix. **Page 1 (cover + letter + signature + acceptance) has a fixed height with
   overflow hidden** — long content (many scope items, an unusually long duration sentence) can
   silently clip instead of wrapping. Always open every page PNG and confirm the acceptance
   signature/date captions are visible above the footer band, and — if an SOV page was built —
   that its grand total matches the cover's Subtotal exactly, before delivering.
5. Deliver the PDF. Done when: 2 or 3 clean pages (3 only if SOV was requested), tax visible on the
   cover, no internal markup/GC/Fee/Insurance numbers anywhere in the PDF (including the SOV page),
   nothing below 14px.

## Design DNA (do not drift — shared with chrysler-proposal)

Blue `#0028cc`, ink `#101418`, TT Commons Pro (embedded from `assets/`), numbered editorial
sections (01/ Scope of Work, 02/ Clarifications & Exclusions, 03/ Schedule of Values if present),
"Since 1984 · NY + NJ" footer band. 14px is the type floor. Page 1 consolidates cover, letter,
signature, and acceptance into one page. Long scopes: the scope sheet holds ~14 items before you
need to duplicate the scope-sheet div and continue numbering. Edit `template.html` only for
structural changes the user asks for — data lives in `data.json`.
