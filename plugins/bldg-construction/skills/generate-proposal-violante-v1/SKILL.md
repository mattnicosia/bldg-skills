---
name: generate-proposal-violante-v1
description: "Generate a construction proposal in Violante & Sons Inc. Contracting's exact branded format (docx/pdf): letterhead with their real logo and navy accent bar, a cover page with scope narrative + bulleted services + total price, an optional CSI-coded Estimate/SOV breakdown page, and a clarifications/exclusions + signature acceptance page. Use whenever Matt asks for a 'Violante proposal', a 'Violante & Sons proposal', to send a proposal to one of Violante's clients, or references the Violante format/template. Do not use for BLDG Estimating's own letterhead proposals, this is specifically the Violante & Sons brand identity."
license: Proprietary
---

# Violante & Sons Proposal Builder

Generates a proposal docx (then converts to PDF on request) matching Violante & Sons Inc. Contracting's real ProEst-style branding, reverse-engineered pixel-for-pixel from their actual past proposals. Don't freehand the layout, colors, or fonts, use the script and assets in this skill so every proposal is consistent.

## What's here

- `scripts/build_proposal.js` — Node script, reads a JSON config, writes a `.docx`. Run with `node scripts/build_proposal.js <config.json>` (cwd should be wherever you want the output file written, or set `outputName` to an absolute path).
- `assets/violante_logo.png` — their real logo, extracted at source resolution from an actual proposal PDF. Never regenerate or approximate this logo.
- `reference/config.example.json` — a full worked example (the sawcut/slab removal proposal for Flynn Construction, 83 E. Park Ave.). Copy this and edit the fields rather than writing a config from scratch.
- `reference/default-exclusions.json` — the universal boilerplate exclusions Violante uses on every proposal. Start every new exclusions list with these `universal` items, then append scope-specific ones (what's not included in this particular trade, thickness/quantity assumptions, etc.) after.

## Brand spec (do not deviate)

- Accent color / bottom bar: `#24309E` (navy blue)
- Body text: `#333333`, headings: `#1A1A1A`
- Font: Arial throughout
- Company block (top right of every page): "Violante & Sons / 8 Kimberly Court / Lake Grove, NY, 11755 / (516) 404-2772"
- Logo: top left, ~1.25in tall, from `assets/violante_logo.png`
- Thin gray divider rule (`#D9D9D9`) under the header on every page
- Thick navy bar spans the full page width at the bottom of every page (this is a Word footer, not inline content, so it repeats automatically)
- Page 2 (SOV, optional) shading: group-header rows `#F7F7F7`, total row `#E9F3FF`

These values were sampled directly from real Violante & Sons proposal PDFs (pixel color sampling + `pdfimages` logo extraction). If a future proposal from them looks different, re-sample rather than assuming, but don't casually change these without a reason.

## Workflow

0. **Every time this skill runs**, before building anything, ask Matt three yes/no questions (AskUserQuestion, not free text — this is a standing instruction, not optional even if a past proposal answered it a certain way):
   - Include a Schedule of Values / cost breakdown page? (`includeSOV`)
   - Include a Scope of Work section? (`includeScopeOfWork`)
   - Include a Clarifications and Exclusions section? (`includeClarifications`)

   The cover page (page 1: letterhead, scope narrative, bulleted services, total price) is **always** included, don't ask about it. As of Aug 2026 the cover page layout is the current default; Matt's said a variation is coming later, don't change it preemptively.

1. Gather what you need for the config: date, estimate number (ask Matt if not given, or leave `[ESTIMATE #]` as a placeholder), client name/title/company/mailing address, project reference line (job name or address), a couple of intro paragraphs describing the scope, a bulleted services list, the total price. If Scope of Work is yes, write 1-4 short sentences of what's actually being done (not a re-list of the service bullets, plain scope language). If Clarifications is yes, start from `reference/default-exclusions.json`'s universal list and add scope-specific ones.
2. If SOV is yes, break the total into CSI-style line items (group headers like "02 Existing Conditions", child rows with description + dollar total + job % of the grand total, must sum to the total price).
3. **Scope of Work placement is your judgment call, not automatic** — set `scopeOfWorkOwnPage: true/false` in the config yourself:
   - `false` (shares the page with Clarifications + Acceptance): a couple of short sentences, the common case.
   - `true` (own page): the scope runs long, covers multiple phases/trades, needs its own structure, or would crowd Clarifications off a clean single page.
   Use your eye after rendering, not just a word count — if the combined page looks cramped or the Acceptance signature block gets pushed awkwardly, split it.
4. Write the config JSON (base it on `reference/config.example.json`), run the script, convert to PDF with LibreOffice, and **render it to images and look at it** before sending, exactly like verifying any docx (see the docx skill's verification steps). Check: no visible table borders, footer bar is full width and solid, page count matches what the three answers imply, no leftover placeholder text unless intentionally left for Matt to fill in.
5. Name the output file `[Client-or-Project]_Proposal_v1.docx` per the standard naming convention (increment the version if a same-named file already exists), and only bump to `_v2` etc. on real revisions.
6. Deliver the docx (and PDF if asked) with SendUserFile. If any field was left as a placeholder (no estimate number given, no project address given), say so explicitly rather than letting it slip through silently.

## Known footguns (already fixed in the script, don't reintroduce)

- Word tables need `layout: TableLayoutType.FIXED` and explicit `insideHorizontal`/`insideVertical: NONE` borders, or mobile viewers (iOS Quick Look in particular) render visible grid lines and collapse empty cells (like the bottom bar) to near-zero size. LibreOffice hides this bug, so always spot-check on more than one renderer if something looks fragile.
- The bottom navy bar must be a section `Footer`, not inline body content followed by a page break, otherwise it lands at the top of the next page instead of the bottom of the current one.
- Body text touching the footer bar is controlled by `page.margin.footer` (the footer's distance from the page's bottom edge), **not** `page.margin.bottom`. LibreOffice wraps body text against the footer's occupied region regardless of how big `bottom` is set — confirmed by pixel-measuring a render where bumping `bottom` from 900→1350 moved the gap by exactly 0 pixels, while raising `footer` did. If a page looks like it's about to overflow to gain footer clearance, trim paragraph spacing before shrinking `footer` back down, don't just accept text touching the bar.
- Section headings (`h2`), paragraphs (`p`), and numbered clarifications all need real "before/after" spacing (roughly 170-260 twips), not the ~140 twip defaults from the first draft of this skill — tight spacing reads fine with 2-3 sections on a page but goes top-crammed with dead space at the bottom once 3 sections (Scope of Work + Clarifications + Acceptance) share one page. Always render and look, don't just trust the numbers.
