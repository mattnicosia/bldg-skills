---
name: generate-proposal-montana
description: "Generate a Montana Contracting Corp. client proposal PDF in the company's classic ProEst-style letterhead format: a proposal letter, Scope of Work, Clarifications & Exclusions, and a Schedule of Values broken out by CSI MasterFormat subdivision with General Conditions/Fee/Insurance shown below the subtotal. Use this whenever someone at Montana Contracting asks for a client proposal, a bathroom/kitchen/renovation proposal, a scope-of-work-plus-pricing document, or wants project numbers turned into a formal branded PDF to send a client — even if they just paste in a scope and a list of prices without saying 'use the Montana format.' This is the general-purpose Montana Contracting proposal builder for any client (school, camp, homeowner, commercial); for Chrysler/Stellantis/Mopar/Brix work use the chrysler-proposal skill instead, which has a different brand template and internal markup rules."
---

# Montana Contracting Proposal Generator

Builds the exact 4-page proposal PDF format Montana Contracting sends to clients: a cover letter, a Scope of Work page, a Clarifications & Exclusions page, and a Schedule of Values page organized by real CSI MasterFormat subdivision codes with General Conditions, Fee, and Insurance broken out below the subtotal. This format was refined directly against real approved proposals (Camp Ramah bathroom renovation, Boggy Creek Light Poles) — the numbers and layout here are proven, not a first draft, so stick to the structure below rather than improvising a new layout.

## The golden rule

**The client PDF only ever shows: Schedule of Values line items → Subtotal → General Conditions → Fee → Insurance → Subtotal → Sales Tax → TOTAL.** No internal notes, no markup rationale, no mention of how a number was derived beyond what's in that visible chain. If you're computing pricing from raw direct costs and percentages, do that math in the conversation with the user (or in your own scratch notes) — never print an extra "internal" line on the document itself.

**Never include a "pricing is based on open shop labor" clarification.** This client has explicitly and repeatedly said not to include it. Every other clarification is fair game and should be tailored to the project, but leave that one out even if a source document you're working from includes it.

## Step 1 — Gather project basics

Ask for whatever isn't already in the conversation:
- Client contact name, company, and mailing address (street + city/state/zip)
- Project name (used as both the "Re:" line and the running page-header label — keep it short, e.g. "Camp Ramah – Bathroom Renovation")
- Today's date (or the date the user wants shown)
- Signer (defaults to Joseph Montana, President — only ask if the user wants someone else)

## Step 2 — Scope of Work

Get a list of scope items as short label + description pairs, e.g. `Demolition — Remove and dispose of existing bathroom finishes and fixtures.` These render as bold-label, em-dash items on their own page. Pull them from whatever the user gives you — a pasted scope, an old proposal, a takeoff — and ask for anything missing rather than inventing scope.

## Step 3 — Pricing: Schedule of Values by CSI subdivision

This is the part most likely to need real construction knowledge, so take care here.

**Categorize by subdivision, not division.** Every line item gets its own specific 6-digit CSI MasterFormat subdivision code (e.g. `09 30 13` Ceramic Tiling, `22 40 00` Plumbing Fixtures) — never lump multiple unrelated trades under one broad division header like "09 Finishes." If several of the user's cost lines fall under the same subdivision (e.g. several plumbing fixture types), it's fine to combine them into one subdivision row, but don't group *different* subdivisions under a shared division banner. `references/csi_subdivisions.md` has the common subdivisions this type of renovation work tends to need — check it before guessing a code from memory.

Ask the user (or infer from what they've given you) whether they already have:
- **(a) A finished Schedule of Values** — CSI codes and dollar amounts already assigned. Just use it.
- **(b) Raw direct-cost line items** that need subdivision codes assigned and markups applied. Assign the codes yourself (using the reference file), then move to the markup step below.

**Markup: General Conditions, Fee, and Insurance cascade — they do not all apply to the same base.** This compounding order was checked against real numbers a Montana Contracting estimator approved and it matched exactly, so it's the one to use:

```
sov_subtotal = sum of all Schedule of Values line items
running       = sov_subtotal
GC            = running * gc_pct         ; running += GC
Fee           = running * fee_pct        ; running += Fee
Insurance     = running * insurance_pct  ; running += Insurance
pricing_subtotal = running               (this is the SECOND "Subtotal" on the page)
tax           = pricing_subtotal * tax_pct   (or a flat amount, or $0 if excluded)
TOTAL         = pricing_subtotal + tax
```

Ask the user for the GC / Fee / Insurance percentages — don't assume a default, since these vary by job and client relationship. If any of the three don't apply to this job, it's fine to omit that line entirely (pass `0` for that percentage in data.json and the build script will skip printing the row).

**Tax:** ask whether sales tax applies. If the client is providing a capital improvement certificate (common for schools, camps, nonprofits, religious institutions in NY), tax is typically excluded — label the row `Sales Tax (NY — excluded, capital improvement certificate assumed)` with a `$0.00` amount, same as the reference example. If tax does apply, get the jurisdiction and rate the same way the chrysler-proposal skill does (look it up, confirm the rate with the user before using it).

**Show the full worksheet in chat and get explicit approval before rendering.** Once you have the Schedule of Values subtotal, GC/Fee/Insurance amounts, pricing subtotal, tax, and total, state all of it plainly to the user and wait for a yes before building the PDF — these are real dollar figures going to a real client.

## Step 4 — Clarifications & Exclusions

Ask what should be excluded or clarified — permit fees, tax treatment, scope boundaries (e.g. "excludes drilling for plumbing"), electrical/HVAC exclusions, pricing validity period, insurance coverage statement, and anything else specific to this job. Write each as one clear sentence; they render as a numbered list. Remember: no open-shop-labor line, ever.

## Step 5 — Build, verify, and deliver

1. Write a `data.json` following the schema in `example_data.json` (every field there is real, taken from an approved proposal — copy its structure exactly). Key fields:
   - `date_long`, `client_contact`, `client_company`, `client_addr1`, `client_addr2`, `project_name`, `signer_name` (optional, defaults to Joseph Montana)
   - `scope_items`: array of `{label, description}`
   - `clarifications`: array of strings (numbered automatically)
   - `sov_items`: array of `{code, description, amount}` — will be sorted by code automatically, so don't worry about the order you list them in
   - `gc_pct`, `fee_pct`, `insurance_pct`: decimals like `0.10` (omit or set to `0` to skip that line entirely)
   - `tax_label`: the exact string to print next to the tax amount
   - `tax_amount` (flat dollar amount) OR `tax_pct` (applied to the pricing subtotal) — use whichever the situation calls for
   - `expected_total` (optional but recommended when the user gave you a target number): the script warns loudly if its computed total doesn't match, which catches typos in your `sov_items` before the client ever sees them

2. `node scripts/build_proposal.js data.json proposal.docx` — this prints the full computed worksheet (Schedule of Values subtotal, GC, Fee, Insurance, pricing subtotal, tax, total) to the console. Read that output and confirm it matches what you approved with the user in Step 3 before moving on.

3. Convert to PDF: `python3 scripts/office/soffice.py --headless --convert-to pdf proposal.docx`

4. Verify before sending: render every page to an image and actually look at them — `pdftoppm -jpeg -r 100 proposal.pdf page` then read each `page-N.jpg`. Confirm: the letter's stated sum matches the Schedule of Values TOTAL, nothing is clipped or overflowing a page, the Schedule of Values is flat by subdivision (no division-level grouping headers), and GC/Fee/Insurance appear below the subtotal exactly as computed. This step matters — catching a rendering issue yourself beats a client noticing one.

5. Deliver the PDF to the user.

## Design reference (don't drift from this without being asked)

- Header (every page): Montana logo top-left (`assets/logo.png`), company name/address/phone right-aligned, thin gray rule below.
- Footer (every page): navy band (`#0B4F8C`), centered white bold `www.montanacontracting.com`, smaller centered `Powered by ProEst` beneath it.
- Font: Open Sans, 10pt, throughout — no exceptions, no headline font swap.
- Page order: Letter → Scope of Work → Clarifications & Exclusions → Schedule of Values + Pricing Summary. The attachments list on the letter should name them in that same order.
- Schedule of Values table: black header row, white bold text, columns CSI Subdivision / Description / Amount, flat and sorted ascending by code, "Subtotal" row shaded light blue (`#E4E9F5`) spanning the first two columns.
- Pricing Summary table directly below it: "Subtotal (Schedule of Values)" shaded `#E4E9F5`, then GC/Fee/Insurance rows unshaded, then "Subtotal" shaded `#E4E9F5` again, then tax, then "TOTAL" shaded darker blue (`#C9D6EE`).

If a user asks for a structural change (different page order, a new section, different shading), that's a legitimate request — just make it deliberately and update this file's description of the design so the next run stays consistent, rather than treating every request as one-off.
