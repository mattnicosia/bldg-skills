---
name: generate-proposal-mcc
description: Render any Montana Contracting Corp. proposal, estimate, or ProEst export into MCC's exact branded proposal PDF — cover + letter + acceptance, Scope of Work, an optional CSI Schedule of Values with the markup stack shown, and Clarifications & Exclusions last. Use whenever Matt asks for an "MCC proposal", a "Montana proposal", to "put this in our proposal format", to reformat/clean up an existing proposal or ProEst PDF onto Montana letterhead, or invokes /generate-proposal-mcc. Works in any project or chat. For Chrysler/Stellantis/Mopar/Brix work use chrysler-proposal; to price a small job from scratch use create-small-estimate — this skill is the shared renderer and is safe to use for any client.
---

# /generate-proposal-mcc — Montana Contracting Branded Proposal Renderer

Takes proposal content from anywhere — an uploaded PDF, a ProEst export, a pasted
scope, or an interview — and renders it into Montana Contracting's branded proposal
PDF. This skill owns **format only**. It does not invent scope and it does not
invent pricing.

## THE DESIGN IS LOCKED

`template.html` is the single source of truth for design. **Do not edit it.** Do not
add, remove, reorder, restyle, or "improve" anything: no other logos or graphic marks, no
new colors, no new fonts, no rules, no section renumbering, no font-size changes, no
spacing tweaks. Data goes in `data.json`; the template is never touched.

If content will not fit, the answer is to shorten the content or let the flow engine
add a continuation page — never to shrink type, tighten padding, or edit the template.
If the user explicitly asks for a structural change, make it in `template.html`, say
so plainly, and treat it as a permanent change to the house format.

### Sheet order — fixed, never varies

1. **Cover**: wordmark top left, the M mark top right, proposal no. + date, project, Prepared For / Prepared By, Investment Summary, letter, signature, acceptance
2. **Scope of Work**
3. **Schedule of Values**: only if requested
4. **Allowances**: dollar allowances with an Allowances Total, then **Unit Price Allowances** (rates like $15.00 per SF) in their own section, only if present
5. **Alternates**: numbered adds, not in the total, in Matt's order (what the owner wants first, may-need items after), only if present
6. **Value Engineering**: numbered deducts, not in the total, only if present
7. **Clarifications & Exclusions**: **always the last page**. Do not repeat allowances, alternates or VE items here; one line points to their sections.

### Design invariants (verify every one before delivering)

| Element | Locked value |
|---|---|
| Blue | `#0028cc` |
| Ink / gray / steel / hairline | `#101418` / `#6E7480` / `#9AA1AD` / `#E4E6EA` |
| Typeface | TT Commons Pro, embedded from `assets/` |
| Type floor | 14px — **nothing** prints smaller, anywhere |
| Header | `MONTANA / CONTRACTING` wordmark, 15px, slash in blue — **identical on every page including the cover** |
| Logos / graphic marks | the M mark (`assets/mc_m_2026.png`, Matt's 2026 logo) top right on the **cover only**, 0.62in tall; no other marks |
| Footer band | blue, `Since 1984 · NY + NJ` left; `montanacontracting.com` on page 1, zero-padded page number (`02`, `03`, …) after |
| Section headings | plain title, no numeric prefix; continuations read `<Title> (continued)` |
| Scope / clarification rows | zero-padded blue number (`01`, `02`, …), hairline rule under each |
| Cover money rows | exactly three: Subtotal, tax line, TOTAL (blue, 28px) |
| Signer default | **Matt Nicosia, Vice President** |

## Pricing disclosure — what shows where

**The cover shows three numbers only: Subtotal, Sales Tax, Total.** No markup
breakdown, no direct costs, no hours or unit rates ever appear on the cover.

**The Schedule of Values shows the full buildup.** CSI line items are listed at
**direct cost**, followed by a `Schedule of Values Subtotal`, then the markup stack
as its own labeled lines, then the grand `Subtotal` that ties to the cover:

```
Schedule of Values Subtotal        Σ direct costs
General Conditions (10%)           direct × 0.10
Fee (7.5%)                         (direct + GC) × 0.075
Insurance (3%)                     (direct + GC + Fee) × 0.03
Subtotal                           = cover Subtotal
```

The stack **compounds** in that order — it is not a flat 22.4% addition. Percentages
are the house default; override per project only when the user says so, and label
each line with the rate actually used. Hours, unit rates, and per-trade cost buildups
still never appear anywhere in the PDF.

## Step 1 — Gather content

Read whatever the user provided (uploaded PDF, ProEst export, pasted text, prior
proposal). Ask via AskUserQuestion only for what is genuinely missing:

1. **Client** — contact, company, and two address lines.
2. **Project name + location** (location drives the tax treatment).
3. **Proposal number + date** — never invent a number silently. Ask, or propose the
   next in sequence and say you are assuming it.
4. **Scope items** — one directive sentence each.
5. **Direct costs by CSI subdivision** and the markup rates, if an SOV is wanted.
6. **Subtotal, tax, total** — take the user's approved numbers. If pricing has not
   been set yet, stop and use `create-small-estimate` to price it first.

Signer defaults to Matt Nicosia, Vice President.

## Step 2 — Normalize the scope

Scope items are plain numbered directive sentences, matching the house voice:
"Furnish and install (15) new parking lot pole light fixtures."

Strip trade-label lead-ins (`Demolition —`, `Tile —`) that ProEst emits; the CSI
codes live on the Schedule of Values, not in the scope narrative. Keep quantities,
sizes and counts exactly as given. Do not add scope the source did not contain.

Use plain-English subdivision names on the SOV, not raw CSI catalog titles — e.g.
`01 56 00` is **Protection**, not "Temporary Barriers and Enclosures".

## Step 3 — Clarifications & Exclusions

Lead with the six house standards, in this order, then append project-specific ones:

1. All work performed in a professional and workman-like manner, licensed as required by law.
2. All work fully covered with compensation and liability insurances.
3. Pricing includes all supervision, labor, materials and equipment required to complete the scope above.
4. Pricing is valid for 30 days.
5. All work to be performed during normal working hours. Overtime is not included.
6. Permits and fees are not included.

Never drop an exclusion that was in the source document — carry every one through.

## Step 4 — Sales tax

- **NY / NJ**: default to tax **excluded**. Cover label `Sales Tax (Excluded)`, amount
  `$0.00`, and a clarification stating a capital improvement certificate is assumed
  prior to the start of construction.
- **Any other state**: the capital-improvement mechanism is NY/NJ-only and does not
  apply. Look up the combined state + local rate, **confirm it with the user**, then
  label it `Sales Tax (X.X%)`.
- **Out-of-state flag**: MCC's stated footprint is NY + NJ. For any other state, flag
  licensing coverage to the user rather than resolving it silently.

## Step 5 — Build

Write `data.json` (see `example_data.json`). `notes`, `sov`, `sov_markups`, `allowances`,
`alternates` and `value_engineering` are optional; omit any that do not apply.
`allowances`: `{name, basis, amount}` where amount is a number or text such as `"$15.00 per SF"`
(text amounts list under Unit Price Allowances). `alternates`: `{name, basis, amount, unit}`
(`unit` like `"per day"`). `value_engineering`: `{name, basis, amount}` with a positive amount;
it prints as a deduct. Optional `allowances_note`, `unit_allowances_note`, `alternates_note`, `ve_note`.
When the job also has a website presentation (generate-proposal-mcc-living-01), take these three
lists from its `web/proposal_lists.json` so the PDF and the page carry the same items and names. `sov` amounts are **direct costs**;
`sov_markups` is a list of `{label, amount}` in compounding order. Scope items and
notes are HTML-escaped strings: `&amp;` for `&`, `&quot;` for `"`.

```bash
python3 scripts/build_proposal.py data.json proposal.html
python3 scripts/render_and_verify.py proposal.html "Montana Proposal - <Project>.pdf" \
    --bg 255,255,255 --pngdir ./verify
```

`build_proposal.py` enforces the sheet order, flows content across continuation
sheets, never leaves a heading with fewer than three rows under it, and prints an
SOV reconciliation check (direct + markups vs cover Subtotal).

## Step 6 — Verify before delivering

The verifier reports boundary flags and top-of-page gaps. Flags quoting the blue
footer band or the wordmark are expected noise; gap spread across interior pages must be ≤ 6px
(page 1 is left out: it starts at the M mark, which sits higher than the wordmark).

Then **open every page PNG in `./verify/` and look at it.** Sheets are fixed-height
with `overflow:hidden`, so anything too long clips silently instead of wrapping.
Confirm:

- Page 1 acceptance lines and their captions sit above the footer band, not under it.
- No row is cut off at the bottom of any page; no heading stranded at a page foot.
- Clarifications & Exclusions is the **last** sheet.
- SOV grand `Subtotal` equals the cover `Subtotal` to the cent, and the markup lines
  sum correctly onto the direct-cost subtotal.
- Nothing smaller than 14px; the wordmark and footer appear on every page; the M mark
  appears top right on the cover and nowhere else.
- Allowances Total equals the sum of the dollar allowances; alternates and VE match the
  workbook to the cent and say they are not in the Subtotal.
- **Grep page 1 for leaked math** — the cover must never carry the markup stack:

```bash
pdftotext -layout -f 1 -l 1 out.pdf - | grep -niE \
  "general condition|overhead|profit|fee \(|insurance \(|markup|ProEst"
```

Must return nothing. Then deliver the PDF with SendUserFile.

## Files

- `template.html` — the locked design. Tokens only; do not restyle.
- `scripts/build_proposal.py` — data → HTML, sheet order, page flow, SOV reconciliation.
- `scripts/render_and_verify.py` — headless-Chrome render + split/gap checks + page PNGs.
- `assets/TTCommonsPro-{Regular,Bold}.woff2` — embedded brand typeface.
- `assets/mc_m_2026.png` — the M mark, transparent, cropped (from Matt's M LOGO 2026, Oct 2026).
- `example_data.json` — a complete worked example including an SOV with markups.
