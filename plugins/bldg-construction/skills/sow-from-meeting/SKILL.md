---
name: sow-from-meeting
description: Generates a written (Word/.docx) construction Scope of Work organized by CSI MasterFormat division/subdivision from a meeting transcript (Fireflies, Zoom, Otter.ai, or pasted text) — typically an early budget or design-walkthrough call, not a finished drawing set. Use whenever Matt shares a meeting/call transcript or link (e.g. a Fireflies.ai URL) and wants a scope of work, budget scope, or CSI-organized breakdown from it — especially schematic-phase conversations about rooms, systems, allowances, or budget. Trigger on "turn this meeting into a scope of work," "make a SOW from this call," "scope this out from the transcript," or when Matt pastes a transcript and wants it organized by trade/division. This is the transcript-first counterpart to sow-generator (full drawing set + spec book -> bid-leveling Excel via NotebookLM) — use this one when the source is a conversation rather than issued construction documents, and the deliverable is a written narrative document, not a bid-leveling spreadsheet.
---

# SOW From Meeting

Builds a written, CSI-organized preliminary Scope of Work from a construction project meeting transcript — the kind of budget/design walkthrough call that happens before full construction documents exist. Companion to `sow-generator` (which is for bid-leveling Excel output from complete drawing sets); this skill is for the earlier, conversational stage of a project.

## When This Applies

Trigger this skill when:
- Matt shares a meeting transcript, call recording link (Fireflies.ai, Zoom, Otter.ai, etc.), or pasted conversation about a construction project and wants a scope of work out of it
- The conversation is a budget/appraisal-support call, an owner/architect walkthrough, or a design-development discussion — not a fully engineered, issued drawing set
- He asks to organize the discussion "by CSI subdivision," "by trade," or wants a written scope rather than a bid-leveling spreadsheet

If instead Matt has a complete drawing set and spec book and wants a subcontractor bid-leveling Excel workbook, use `sow-generator` instead (or in addition, once drawings are issued).

## Workflow

### 1. Get the transcript

If given a link (e.g. `app.fireflies.ai/view/...`), try `WebFetch` first — it will usually fail because Fireflies requires login. Next try Chrome browser automation (`mcp__claude-in-chrome__*`) in case the user's own browser session is already authenticated. If both fail, tell the user plainly that the link needs authentication your tools don't have, and ask them to paste the transcript text or upload an exported file (txt/docx/pdf). Do not guess at content you can't verify.

### 2. Pull in supporting drawings, if any

Check the project folder (via the device bridge, or uploads) for schematic plans, annotated take-off PDFs, or spec sheets referenced in the call. Estimators frequently annotate their own working plan with red call-outs during a walkthrough — these annotations (e.g. "Alternate," "FF&E Not Millwork," "Requires Drains & Water," "Terrazzo Patching?") are gold: they mirror exactly what's being discussed and often confirm or sharpen a transcript-only read. Stage and read (`Read` handles PDFs directly) any such files before writing the scope — they materially improve citation quality and catch things a transcript alone won't (dimensions, sheet numbers, room labels).

### 3. Extract and classify every scope item

Go through the transcript system-by-system / room-by-room and sort everything into one of five buckets:

1. **Construction scope** — real work assignable to a CSI MasterFormat division/subdivision
2. **FF&E / Owner-furnished exclusions** — anything explicitly carved out as furniture, equipment the owner sources themselves, or "would shake out of the building if you turned it upside down" (a phrase worth listening for — owners often define their own FF&E boundary in almost exactly these terms)
3. **Allowances & budget figures** — any $ amount, $/SF rate, or ballpark number actually said in the meeting. Preserve it as a placeholder allowance, not a firm bid, and note who supplied it (owner's own quote, GC's gut number, etc.)
4. **Alternates / strike items** — anything the owner wants priced as an independent line so it can be added or removed later without redrawing (classic tell: "put it in its own category," "so we can easily just remove it," "make it its own line item")
5. **Open items / TBD / clarifications** — anything pending a decision, an engineer's confirmation, a not-yet-engaged subcontractor, or a design choice not yet made. Never silently resolve these — list them.

Do not invent quantities, dimensions, or costs beyond what was actually said or shown on a drawing. If a detail is genuinely ambiguous or unheard, mark it `[TBD]` or `[UNVERIFIED]` rather than guessing — this mirrors `sow-generator`'s zero-hallucination rule and matters just as much for a narrative document as an Excel one.

### 4. Apply directive-language and organization conventions

Reuse the scope-writing conventions from `sow-generator` (see that skill's SKILL.md for full detail) even though the output format here is different:

- Directives: `F/I` (Furnish and Install), `F/O` (Furnish Only), `I/O` (Install Only), `Remove` (Demolition), `Provide` (services/non-material). Don't stack a directive onto an item whose action word already implies one (`Replace`, `Patch and Repair`, `Prep and Paint`).
- Organize by 6-digit CSI MasterFormat subdivision under its parent Division, not just the top-level Division.
- Fold all rough/finish carpentry, framing, and drywall into `09 20 00 Drywall & Carpentry` on commercial work — don't split them out.
- Keep all electrical scope under Division 26; never use an `xx 05 00` Common Work Results code for any trade — assign to the specific subdivision.
- Split doors (F/O Division 08 + I/O Division 09) and bathroom accessories (F/O Division 10 + I/O Division 09) per the standard trade-split rule.
- Pair plumbing fixtures (F/O) with their rough-in (I/O) in the relevant Division 22 subdivision.

### 5. Cite every line

Each scope item gets a source citation: a drawing sheet reference if the item also appears on a plan (`Sheet A-100.00`, or with a quoted annotation like `Sheet A-100.00 "Alternate"`), or `Per Meeting, [date]` when it only comes from the conversation. Never leave a line uncited.

### 6. Build the document

Output is a **Word (.docx) document**, not an Excel workbook — this is a written, narrative scope of work, not a subcontractor bid-leveling template. Read the `docx` skill's SKILL.md before building (for docx-js gotchas, page setup, and the render-and-verify step). Use `scripts/build_sow_docx_template.js` in this skill as a starting template — it has the header/footer, division/subdivision heading styles, bulleted line-item helper (with inline `[TBD]` / `[ALLOWANCE]` / `[ALTERNATE]` tags and italic source citations), and section-header styling already built. Copy it, swap in the project's actual content, and adjust.

Structure the document in this order:

1. **Cover block** — project name, address, prepared by/for, date, basis of scope (meeting date + attendees, drawing sheets referenced)
2. **Purpose & Limitations** — state plainly that this is a preliminary/schematic-level scope supporting whatever the actual purpose was (bank appraisal, budget conversation, etc.), not an issued-CD bid scope, and that items are refined as design/engineering progress
3. **Directive legend**
4. **Scope of Work by CSI Division** — subdivision-headed bullet lists, each line using the directive-language format and ending in an italic source citation
5. **FF&E / Owner-Furnished Exclusions**
6. **Allowances & Budget Assumptions** — every $ figure actually discussed, with its source
7. **Alternates / Strike Items**
8. **Open Items / Clarifications Needed**

Use a restrained black/gray/white palette (matching `sow-generator`'s visual language) so a reader can tell at a glance this comes from the same shop, even though the layout itself is a flowing document rather than a spreadsheet.

### 7. Verify before delivering

Render to PDF and read the page images (see the `docx` skill) to check pagination, that tags/citations rendered correctly, and nothing got cut off. Then re-read your own draft against the transcript one more time — for every line, ask "did someone actually say or show this, or did I infer it?" Cut or re-flag anything you can't source.

### 8. Deliver

`SendUserFile` the `.docx`. If a project folder is connected via the device bridge, also write it there with `device_commit_files` so it lands alongside the drawings it was built from.

## Relationship to `sow-generator`

| | `sow-from-meeting` | `sow-generator` |
|---|---|---|
| Source | Meeting transcript (+ any available drawings) | Full drawing set + spec book, via NotebookLM extraction |
| Project stage | Schematic / pre-construction-document budget conversation | Issued or near-final construction documents |
| Output | Written Word document, narrative | Excel workbook, subcontractor bid-leveling template |
| Citation granularity | Sheet reference where available, else "Per Meeting" | Sheet + detail + schedule row, multi-pass QA against drawing.md files |

If a project has both a transcript and a full drawing set, use this skill for the early budget document and hand off to `sow-generator` once real CDs exist and it's time to level subcontractor bids.
