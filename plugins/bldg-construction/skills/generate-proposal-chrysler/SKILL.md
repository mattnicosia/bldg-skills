---
name: generate-proposal-chrysler
description: Create a Montana Contracting proposal PDF for Chrysler / Stellantis / Mopar / Brix opportunities. Use when the user wants a Chrysler proposal, a Mopar or PDC estimate turned into a proposal, or says "new proposal" in the Chrysler Estimating project. Runs an interview (pricing source, markups, GR/GC, duration, tax by project location), builds the internal pricing worksheet, and renders the branded PDF.
---

# Chrysler Proposal Builder

Interview → internal pricing worksheet → branded 3-page PDF (cover with tax, letter, scope). The interview happens through AskUserQuestion, one round at a time, in the order below — later questions depend on earlier answers.

**The golden rule: Chrysler never sees the math.** Markups, General Requirements, and General Conditions are absorbed into direct costs before anything is printed. The client-facing PDF shows exactly three numbers: Subtotal, Sales Tax, Total — nothing else. The internal worksheet stays in the conversation (and project) only.

## Step 1 — Project basics

Ask for whatever is missing; skip anything already provided:
- Project name (the "Re:" line, e.g. "Mopar PDC Fence Repair")
- Project location (facility + city/state — this drives sales tax)
- Client contact, company, and address (default: Chris Izzi, Brix Corporation, 30591 Schoolcraft Road, Livonia, MI 48150)
- Scope of work items (or the source documents to pull them from)

Done when: name, location, client block, and a scope list all exist.

## Step 2 — Pricing source

Ask which of three paths prices this job:
1. **Subcontractor pricing** — user provides sub quotes; markup gets added.
2. **Internal takeoff** — user either uploads the takeoff (spreadsheet/PDF) or dictates quantities, units, and unit costs in chat.
3. **Combination** — some trades sub-quoted, some taken off internally; collect both.

If a takeoff is uploaded, read it and echo back the line items and total you extracted so the user can correct you before math happens.

Done when: every scope item has a direct cost with a stated source.

## Step 3 — Markups

Ask what the markup should be. Offer: one blended % on all direct costs, or separate %s (e.g. subs vs. self-perform). Never assume a number — always ask.

## Step 4 — General Requirements / General Conditions / neither

Ask which applies (single choice: General Requirements / General Conditions / Neither).

- **General Conditions** → ask one follow-up: what %?
- **General Requirements** → ask for values on these eight items (any can be $0/skip):
  1. Supervision Allocation %
  2. Project Management Allocation %
  3. Temporary Toilets
  4. Dumpsters / waste removal
  5. Temporary fencing & barricades
  6. Site safety, PPE & badging
  7. Final cleaning
  8. Small tools & consumables
  Percentages apply to direct costs; the others are dollar amounts.

## Step 5 — Duration

Ask the project duration (e.g. "5 working days from mobilization"). It appears on the cover and as a sentence in the letter.

## Step 6 — Sales tax (by project location)

Tax is based on the location of the project, and it must appear on the cover sheet — Chrysler requires it. Look up the combined state+local rate for the project's jurisdiction, then confirm it with the user before using it ("Livonia, MI — I have 6.0%, the last proposal used 6.5% — which applies?"). Label it on the PDF as `Sales Tax (X.X%)`.

## Step 7 — Internal pricing worksheet

Compute, in order:

```
direct costs            = Σ line items (subs + takeoff)
markup                  = direct costs × markup %(s)
GR items                = Σ dollar items + (Supervision % + PM %) × direct costs
  or GC                 = direct costs × GC %
SUBTOTAL (client sees)  = direct costs + markup + GR-or-GC
Sales Tax (client sees) = SUBTOTAL × tax rate
TOTAL (client sees)     = SUBTOTAL + tax
```

Show the full worksheet to the user in chat for approval before rendering. Done when the user approves the Subtotal/Tax/Total.

## Step 8 — Build and verify the PDF

1. Write the approved values into a `data.json` matching `example_data.json` (all keys required; `notes` optional → renders "02 / Clarifications & Exclusions"). Scope items are HTML-escaped strings. Signer defaults to Joseph Montana, President.
2. `python3 scripts/build_proposal.py data.json proposal.html`
3. `python3 scripts/render_and_verify.py proposal.html "Montana Proposal - <Project Name>.pdf" --bg 255,255,255`
4. The verifier checks split content across page boundaries and top-of-page gap consistency (spread ≤ 6px). Boundary flags that quote the blue footer band text are expected noise; anything else, read and fix. **Page 1 (cover + letter + signature + acceptance) has a fixed height with overflow hidden — if content is long (many scope items pushed onto page 1's letter section, an unusually long duration sentence, etc.) it can silently clip instead of wrapping to a new page.** Always open every page PNG and confirm the acceptance signature/date captions are visible above the footer band before delivering, not just the boundary-check text.
5. Deliver the PDF. Done when: 2 clean pages, tax visible on the cover, no internal markup/GR/GC numbers anywhere in the PDF, nothing below 14px.

## Design DNA (do not drift)

The template encodes montanacontracting.com: blue `#0028cc`, ink `#101418`, TT Commons Pro (embedded from `assets/`), numbered editorial sections (01/ Scope of Work, 02/ Clarifications & Exclusions on page 2), "Since 1984 · NY + NJ + FL" footer band. The header lockup on every page — cover and interior — is the single-line wordmark "MONTANA / CONTRACTING" (blue slash) with a small three-bar icon on the right; the cover version just runs a couple points larger than the interior running header, it isn't a separate stacked logo treatment. **14px is the type floor — nothing on the page prints smaller than the project-location line on the cover; this was a deliberate legibility fix, don't reintroduce smaller tracked-caps text.** Page 1 consolidates the cover, proposal letter, signature, and acceptance block into one page (the letter no longer repeats the date/address/pricing already shown on the cover — it only adds the narrative, duration sentence, signature, and acceptance). Long scopes: the scope sheet holds ~14 items; beyond that, duplicate the scope sheet div and continue numbering. Edit `template.html` only for structural changes the user asks for — data lives in `data.json`.

## Labor language — never mention it

Chrysler/Stellantis/Mopar/Brix proposals must never say "open shop," "union labor," "non-union," or any other labor-sourcing/union-status language anywhere in the document — not in clarifications, not in scope, not in the letter. Montana's labor structure is not something to disclose to this client. When drafting the `notes` (Clarifications & Exclusions) or scope items, write around it: "Pricing includes all supervision, labor, materials and equipment required to complete the scope above" covers the same ground without naming a labor model. If a user-provided note or uploaded document mentions open shop or union labor, drop that line rather than carrying it into the PDF, and flag to the user that you removed it.
