---
name: ROM_Budget_Range
description: Generate a sketch-level budgetary cost estimate for a NYC construction project as a deliverable from a general contractor (O+D Builders is the default) to an architect or owner. Produces a portrait PDF + Excel workbook with CSI-divisional cost breakdown, two-tier finish pricing, HVAC base/add-alternate, takeoff, notes/inclusions/exclusions, and a draft email reply. Triggers when the user wants to estimate, price, or budget a NYC construction project — restaurant, retail, office fit-out, hospitality — especially when there's a project folder with sketch plans (.pdf), an architect's scope email (.msg), or a project number in the format 260XXX. Use this skill whenever the user says "budgetary estimate," "budget proposal," "ROM estimate," "schematic estimate," "Class 5 estimate," "create an estimate for X project," "price the McDougal job," or references the BLDG Estimating workflow. Also use when the user pastes an architect's scope email and asks for a number. Do NOT use for change orders, hard-bid pricing, sub-only quotes, or invoicing — those are different workflows.
---

# O+D Budgetary Estimate

Produces a complete sketch-level budgetary cost estimate as a deliverable from a General Contractor (default: O+D Builders) to an architect or owner. The output is what the architect's email replied with the day they asked "what would this cost?" — a PDF, an editable Excel workbook, and a draft email the GC can send back.

This skill is for BLDG Estimating's workflow. BLDG does the work; the deliverable is branded as the GC. **Never put "BLDG Estimating" on the document or in the email** — the architect should only see the GC's name.

## When this skill is doing its job

The user typically arrives with:
- A project number folder (e.g., `260079 - MacDougal Street Restaurant [O+D Builders]`) under `BLDG Estimating\` in their Dropbox
- A `Bid Documents` subfolder containing an architect's email (.msg) and sketch plans (.pdf)
- A vague scope ("the works," "redo finishes and bathrooms," "move the bar")

The user wants:
- A defensible budget number in a range (not a single point), grounded in NYC 2026 open-shop rates
- A polished PDF the GC can send to the architect as-is
- A live xlsx the GC can adjust line items in

## Workflow

Read all four reference files in order — they capture lessons from real iteration, not just theory.

1. **`references/workflow.md`** — Step-by-step playbook: read sources, ask clarifying questions, build, post-process, deliver
2. **`references/pricing_logic.md`** — How the math works: divisional breakdown, markup structure (GC 7% / Fee 5% / Insurance 3% / Contingency 12%), how to scale by SF, the Paolo benchmark
3. **`references/platform_notes.md`** — Critical Windows/Excel quirks that will waste an hour if you don't know them up front (Pillow conflict, Dropbox PDF export bug, sandbox file permissions)
4. **`assets/notes_library.md`** — Standard inclusions/exclusions/assumptions text. Don't reinvent.

## Quick orientation

The deliverable has six logical sections, each its own Excel tab and PDF page-group:

| Section | Purpose |
|---|---|
| Cover Letter | Project intro, scenario table with totals, basis bullets, attachments list, signature line |
| Cost Totals — Tier A | CSI-divisional breakdown for mid-tier finish package, HVAC reuse base |
| Cost Totals — Tier B | Same, but high-end finish package |
| HVAC Add-Alt | Add-alternate for full HVAC equipment replacement (applies to either tier) |
| Takeoff & Quantities | Per-line quantities and units (no unit prices shown to client) |
| Notes / Assumptions / Inclusions / Exclusions | Complete scope envelope |

Every page has the O+D logo in the print header (so it repeats on every printed page automatically) and an O+D address/phone footer.

## Critical inputs to extract or ask for

Before pricing, lock these down (use `AskUserQuestion` for the ones you can't determine from the source materials):

- **Project number, name, address** — from the folder name and email signatures
- **Architect contact** — from the email "from" line of the original scope request
- **GC contact** — usually the recipient of the forwarded email (default: Edward Tassey @ O+D)
- **FOH / kitchen / bath / circulation / cellar SF** — ask the owner; do NOT scale from drawings unless they confirm. SF is the most common source of large errors.
- **Finish tier(s)** — usually 2 tiers (mid + high-end). Confirm.
- **HVAC strategy** — reuse existing + new distribution (base) with full-replacement (add-alt) is the default split
- **Bar scope** — new in new location vs. relocate existing vs. refresh
- **Kitchen scope** — usually "stays, minimal touch" with hood/gas recert
- **Bathroom allowance** — ask $/bath; default $85K per bath (ADA gut)
- **Schedule** — duration in months; affects General Requirements line
- **Structural & abatement** — usually carry "NO structural" and "NO asbestos testing/abatement"; confirm explicitly

## How to build

The build is two-phase. **Phase 1 is identical on every platform; Phase 2 differs — check
which machine you are on first.** See `references/platform_notes.md` for both paths.

1. **Phase 1 (Python + openpyxl) — cross-platform:** generate the workbook with formulas,
   formatting, multiple tabs. Use `scripts/build_estimate.py` as a starting template —
   edit the data dictionaries (LINE_ITEMS, HVAC_ALT, TAKEOFF, OUT path, project metadata)
   for the new project. A prior project's copy of this script is preserved in its own
   `Bid Documents` folder and is usually a better starting point than the template; for
   620 W 52nd, 260093's copy is the closest match.
   - On Windows, invoke via stdin pipe to dodge Dropbox file locks: `cat scripts/build_estimate.py | py.exe -`
   - On macOS, run it directly: `python3 scripts/build_estimate.py`

2. **Phase 2 (xlsx -> branded PDF):**
   - **macOS / Linux (default): `scripts/export_pdf.py`.** LibreOffice paginates, PyMuPDF
     stamps the logo, title/address, and footer on every page. Writing directly into
     Dropbox is fine. Verified to byte-level content parity against the Windows output of
     260093 v4 (10 pages, 73 numeric tokens, zero missing).
   - **Windows: `scripts/export_pdf.ps1`.** Excel COM sets the print header with the logo
     (`&G`), then exports. **PDF must be written to a non-Dropbox path first**, then moved
     via Bash — Excel's COM export fails silently into Dropbox folders.

**Check the export warnings every run.** `export_pdf.py` reports two failure modes that
are otherwise invisible in a finished-looking PDF:
- **Hidden sheets are omitted** from the PDF by LibreOffice *and* Excel. 260093 v4 has its
  Takeoff tab hidden — re-exporting it silently drops two pages of quantities. Re-run with
  `--include-hidden` when the tab belongs in the deliverable.
- **A page count outside 10-18** means a blank tab or a runaway print area.

The logo (`assets/OD_logo.png`) is bundled. To regenerate from WebP: on macOS use Pillow
(it works fine here); on Windows use `scripts/extract_logo_from_webp.ps1`, since Pillow is
broken in that sandbox.

## Deliverable files

Place outputs in the project's `Bid Documents` folder, named:
- `<NNNNNN>_<ProjectShortName>_Budgetary_Estimate_v<N>.pdf`
- `<NNNNNN>_<ProjectShortName>_Budgetary_Estimate_v<N>.xlsx`
- `<NNNNNN>_<ProjectShortName>_Email_Reply_Draft.txt`

Use `v1`, `v2`, `v3` versioning — don't overwrite, the user often iterates with the architect.

## Sanity-check before delivering

Look at the totals and compare against the Paolo benchmark in `references/pricing_logic.md`. NYC West Village restaurant mid-tier, 2,000 SF, including new kitchen + FF&E = $700/SF gross. Strip kitchen and FF&E and you're at ~$600/SF for renovation-only work. If your number is more than ±30% off the Paolo baseline (after adjusting for scope differences), something is probably wrong — recheck SF or pricing assumptions.

Also check: is the page count reasonable (10–18 pages), does the logo show on every page, do the column totals match the SUM lines (no #REF! or ####).

## Iteration etiquette

The user often sends one or two corrections after seeing v1 — typical: bath allowance, structural assumption, schedule duration, exclude something specific. Apply the change, bump version, regenerate. Each iteration takes ~2 minutes.
