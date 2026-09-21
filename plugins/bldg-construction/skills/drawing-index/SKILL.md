---
name: drawing-index
description: Turns 2D PDF construction drawings into a cheap, queryable, element-keyed data layer (per-sheet PDFs, per-sheet markdown, index.json keyed by the physical things being built) so downstream AI work never re-ingests the raw drawing set. Use whenever the user points at a folder of construction PDFs and wants it indexed, split, or made AI-readable -- and ALWAYS as phase one of any estimating, scope-of-work, takeoff, scheduling, procurement, or RFI task that depends on reading drawings. Trigger on "index the drawings", "extract the drawing set", "split these drawings", "build the drawing database", "what's on these sheets", or when a downstream skill (sow-generator, electrical-estimator, quantity-takeoff) needs drawing.md files or index.json that don't exist yet. Replaces NotebookLM as the primary drawing-extraction path (NotebookLM still wins for spec books) -- local text-layer extraction is deterministic, gives per-sheet citations, and costs a fraction of the tokens.
---

# Drawing Index

2D PDF construction drawings are a bad input to an AI model. This skill converts a
drawing set into a data layer that is cheap to query, honest about what it could not
read, and organized by what is being built rather than by what page it is on.

Every other construction skill in this folder depends on this one. Run it first.

## The four reasons raw drawings fail, and what this skill does about each

| Problem | Fix |
|---|---|
**File size.** A 15-sheet civil set is 6 MB; sets over 10 MB often will not even attach. Working "in the folder" instead just means re-ingesting the whole file on every query. | `split_and_render.py` splits the set into one small PDF per sheet. The multi-MB original is never read again.
**Context rot.** The more you put in the window, the less reliable the answer. Drafting a concrete scope needs the mix design and slab depth, not 75 sheets. | The index is a small text/JSON layer. A real query costs single-digit thousands of tokens instead of tens of thousands, and the answer quality goes UP because the context is small.
**Wrong organization.** A slab appears on a plan, its depth on a section three sheets later, its mix in a schedule at the back. Sheet order is for humans flipping pages. | `index.json` is keyed by **element** -- the physical thing being built -- with every sheet that describes it attached. This is how IFC/BIM models are structured, and it maps one-to-one onto CSI-organized scope output.
**Precise measurement.** Models read images approximately. A hot-water line and a cold-water line are two dashed lines. Top models read an analog clock at roughly half of human accuracy; distinguishing `CW` from `HW` on a dense schematic is the same class of task. | Text layer first, always. Counts come from `extract_text_tags.py`, not from vision. Linear measurement off a scaled PDF is never attempted. Anything that must be measured is flagged for a human, not guessed.

## The three layers

1. **Vector text layer** (`extract_text_tags.py`) -- exact strings and coordinates. Precise but meaningless alone: a pile of tokens.
2. **Image layer** (rendered pages + vision) -- conceptual understanding. Models are good at "this is a plumbing riser with hydraulic positioning" and bad at "that line is 20.7 LF." Use it for comprehension, never for measurement.
3. **Human takeoff export** (optional, see Phase 5) -- real measured quantities with assemblies. The only layer that produces trustworthy linear quantities.

Layers 1 and 2 are what this skill builds. Layer 3 is dormant until Montana has a takeoff
tool with data export; the hook is specified below so it can be switched on without
redesign.

**If a real BIM/IFC model exists for the project, use it and skip this pipeline
entirely.** The whole design is a reconstruction of what an IFC model already gives you.

## Phase 0: Confirm scope before extracting anything

Ask, do not assume:

1. **Drawing folder or file path**, and the output folder for the index.
2. **Which disciplines/trades are in scope.** Extracting all 75 sheets when the user
   wants HVAC wastes tokens and produces a bloated index. Narrow first.
3. **Are spec books included?** Specs are a text corpus, not drawings -- see
   "When NotebookLM is still the right tool" below.
4. **Is there a prior index in the folder?** If so, this is a revision run -- see
   Revision Workflow. Never re-extract a whole set to pick up a revision.

Then present the sheet list from `sheets.json` and get confirmation on which sheets to
extract before doing the expensive part. Same discipline as showing a measurement plan
before measuring: cheap to correct now, expensive to correct later.

## Phase 1: Split and detect

```bash
python scripts/split_and_render.py <set.pdf|folder/> --out drawings/
```

Produces `drawings/sheets/<SheetNo>.pdf`, `drawings/images/<SheetNo>.png` (only where
needed), and `drawings/sheets.json`.

Per page it records a text-layer verdict:

- **`vector`** -- real selectable text layer. Extract text; counts can be reliable.
- **`sparse`** -- a text layer exists but is thin (commonly a titleblock succeeded and
  the rest of the page is a bitmap). Extract text AND run vision. Treat counts as
  MEDIUM.
- **`image_only`** -- no usable text. Vision only. Everything LOW confidence.

The three-way split matters. A page with 5 words is neither vector nor image-only, and
treating it as either loses content.

**Do not use `--render-all`.** On a set with a real text layer, rendering every page and
running vision on all of them costs orders of magnitude more than extracting text per
page and using vision only where text comes back empty. Selective rendering is the
validated method.

Check the warning about sheets with no readable sheet number. Fix those by hand in
`sheets.json` rather than letting `page-007` propagate into citations.

## Phase 2: Per-sheet extraction

For each in-scope sheet, write `drawings/md/<SheetNo>.md`. Run these as sub-agents
batched by discipline group so the main context stays clean — four batches covers a
typical set (General/Site, Architectural, Finishes/Schedules, MEP/Structural).

Each sheet's `.md` captures, verbatim, with a citation for every item:

- Sheet number, title, discipline
- What the sheet shows (one-paragraph scope)
- Every dimension and measurement explicitly called out
- Every material, finish, and specification **in the exact language on the drawing** --
  do not normalize
- Every manufacturer, model number, color callout, schedule tag
- Every schedule, table structure preserved
- All general notes and keynotes
- All detail callouts (`Detail 5 on Sheet A-201` -> `5/A-201`)
- All cross-references to other sheets and to specs
- All tag references (`T-L-1`, `D-1`, `RTU-3`)

Citation format is the same everywhere downstream: `5/A-201` for a detail, `A-201` for a
plan, comma-separated for multiple. If a fact cannot be sourced to a location, mark it
`[UNVERIFIED]`.

**Never calculate, infer, or assume a quantity during extraction.** Record only
quantities explicitly stated on the drawings. An inferred quantity that enters the index
looks identical to a stated one three steps later.

For `sparse` and `image_only` sheets, run a vision pass on the rendered PNG asking for
the same detail list, and merge it into the same `.md` with the same citation format.
This has recovered real content on sheets that text extraction alone could not read --
rebar development tables, steel beam schedules, equipment schedules. Only fall back to
`[UNVERIFIED]` / RFI if vision also cannot resolve it. Acceptable note when it genuinely
cannot: "HVAC equipment schedule could not be extracted -- RFI to engineer required."

### Counting tags

Discover before you pattern-match:

```bash
python scripts/extract_text_tags.py drawings/sheets/S-301.pdf --list
```

That dumps every distinct token with its frequency. Choose a regex from what is actually
there rather than guessing.

```bash
python scripts/extract_text_tags.py drawings/sheets/S-301.pdf \
    --pattern "^P[0-9]+$" --out counts/S-301_piers.json
```

**A raw tag count is MEDIUM confidence, not HIGH.** The text layer cannot tell a tag
placed on a plan from the same string in a schedule row, a legend, or a keynote list. A
sheet with 8 physical P1 piers and a schedule reading `PIER SCHEDULE P1 QTY 8` returns 9
unless filtered. That is a verified failure, not a hypothetical — the source material
this script came from called it "100% accurate" and it is not.

The script defends against it by default (same-line context keywords) and reports every
exclusion with its reason. Two things still remain your job:

1. **Reconcile against the sheet's own schedule.** If the schedule says 8 and the count
   says 9, that is a discrepancy to flag, never to silently resolve.
2. **Review the markup overlay** before promoting anything to HIGH:

```bash
python scripts/markup_pdf.py drawings/sheets/S-301.pdf markup.json S-301_marked.pdf
```

The markup PDF is the audit trail. Open it, count the boxes, confirm. It works correctly
on rotated sheets (`/Rotate 90`), which is most real drawings. Promote a count to HIGH
only after (1) or (2) passes.

## Phase 3: Build the element-keyed index

```bash
python scripts/build_index.py drawings/sheets.json --skeleton --out drawings/index.json
```

Then fill `elements[]` from the per-sheet `.md` files. This is the judgment step and it
is the point of the whole skill: you are inverting a page-ordered document into an
element-ordered one.

One entry per physical thing being built. Schema and worked examples in
`references/index-schema.md`; the skeleton also carries `_element_template`.

```json
{
  "element": "Perimeter Grade Beam",
  "category": "Substructure",
  "trade": "Concrete",
  "csi_subdivision": "03 30 00",
  "location": "Building perimeter, grids A-F",
  "source_sheets": ["S-101", "5/S-301", "S-601"],
  "specifications": [
    {"value": "4000 PSI", "source": "S-101 general note 3"},
    {"value": "24 in x 36 in", "source": "5/S-301"}
  ],
  "quantities": [
    {"value": null, "unit": "LF", "basis": "not stated on drawings",
     "confidence": "NOT_MEASURED"}
  ],
  "related_elements": ["Slab On Grade"],
  "confidence": "HIGH",
  "unverified": false
}
```

Then validate. This is a gate, not a suggestion:

```bash
python scripts/build_index.py drawings/index.json --validate   # non-zero exit on error
python scripts/build_index.py drawings/index.json --stats
```

Validation hard-fails on: a placeholder project name, a citation pointing at a sheet
that is not in the set, a specification with no source, a quantity with no basis, a
missing required field. Do not proceed to a downstream skill until it exits clean.

`--stats` reports which sheets no element cites. Those are either genuinely scope-free or
the extraction missed them — check before calling the index complete.

## Phase 4: Store it properly

`index.json` is fine up to a few hundred elements. Past that, or once several skills are
querying it concurrently, move to SQLite (`drawings/index.db`) with the same schema —
one row per element, tables for specifications, quantities, and source_sheets. A flat
JSON file has to be read whole to answer anything, which reintroduces the context
problem this skill exists to solve.

Rule of thumb: under ~200 elements JSON is simpler and fine; over that, SQLite.

## Phase 5: Takeoff export ingestion (dormant hook)

The third layer. **Not active** — Montana has no confirmed takeoff tool with a data
export as of 2026-07-29. Specified here so it can be switched on without redesign.

When a takeoff export exists (ZZ Takeoff, STACK, On-Screen Takeoff, Bluebeam quantity
export), it carries human-measured quantities plus the assemblies they roll into. That
is the only trustworthy source of linear quantities in this whole pipeline.

On ingestion:

1. Match export items to index elements by tag, then by name, then by CSI code. Report
   unmatched items in both directions — never silently drop one.
2. Write matched quantities with `"confidence": "VERIFIED"` and
   `"basis": "human takeoff export, <tool>, <date>"`.
3. **`VERIFIED` outranks everything.** A verified quantity replaces any AI-derived value
   for the same element and retires the ratio-based estimate for it entirely.
4. Keep the AI-derived value alongside as `superseded_value` for one cycle. If the two
   disagree by more than ~25%, that is a calibration signal worth reading.

Until then, linear quantities stay `NOT_MEASURED` or come from explicitly-labeled
conceptual ratios in `sow-generator/references/trade-checklists.md`, which carries its own
READ FIRST warning that every figure in it is an unverified placeholder.

## When NotebookLM is still the right tool

NotebookLM is **not** the primary extraction path anymore. Local text-layer extraction is
deterministic, cites exact per-sheet locations, costs a fraction of the tokens, and does
not depend on scraping a browser SPA. Two cases where NotebookLM still wins:

1. **Spec books and narrative documents.** A 500-page spec book or a Landlord SOW
   narrative is a text corpus, and semantic Q&A across it genuinely beats per-page
   extraction. Use NotebookLM for specs; use this skill for drawings.
2. **When Python is blocked.** On managed Windows machines AV/EDR can block PyMuPDF
   (`PermissionError` on `fitz/__init__.py`) even after a clean `pip install`. Do not
   fight it with venvs in TEMP or user installs — the same policy blocks those. Fall
   back to `pdftotext` (poppler) for text pages and NotebookLM for graphical ones.

If you do use NotebookLM, batch queries by discipline group (four batches for a typical
set), never one query per sheet. Its SPA virtualizes the chat, so `body.innerText` caps
around 60K chars and long responses truncate silently — capture via a recursive DOM walk
into a variable and blob-download it, then parse.

## Revision workflow

When the user says drawings were updated, do NOT re-run the whole pipeline.

1. Re-run `split_and_render.py` into a fresh folder.
2. Diff `sheets.json` against the prior one: new sheets, removed sheets, changed page
   counts.
3. For sheets present in both, compare revision number/date from the titleblock.
4. Re-extract **only** changed and new sheets. Merge into the existing `index.json`.
5. Log what changed in `index_revisions.md` — sheet, old rev, new rev, elements touched.
6. Re-run `--validate` and `--stats` on the merged index.

Archive the prior `index.json` as `index_rev[N].json` before merging. Never overwrite.

## File output

```
drawings/
  sheets/<SheetNo>.pdf        one PDF per sheet
  images/<SheetNo>.png        rendered only where text extraction was insufficient
  md/<SheetNo>.md             per-sheet extraction, everything cited
  counts/<SheetNo>_<item>.json  tag-count output with exclusions
  markup/<SheetNo>_marked.pdf   count audit overlays
  sheets.json                 manifest
  index.json                  the element-keyed index  <-- what downstream skills read
  index_revisions.md          revision log
```

Treat `index.json`, `sheets.json`, and everything in `md/` as permanent project
deliverables. Never delete them in cleanup.

## Scripts

| Script | Purpose |
|---|---|
`split_and_render.py` | Split a set into per-sheet PDFs; detect sheet numbers from titleblocks; classify text layer; render only pages that need vision. |
`detect_pdf_type.py` | Standalone per-page vector/sparse/image_only detection with text-density metric. Use for a quick read on a set before committing to it. |
`extract_text_tags.py` | Text-layer tag counting with coordinates. `--list` to discover tags, `--pattern` to count. Over-count defenses on by default; every exclusion reported. |
`markup_pdf.py` | Stamp counted tags onto the sheet PDF for visual audit. Correct on rotated pages. |
`build_index.py` | `--skeleton` from a manifest, `--validate` as a hard gate, `--stats` for coverage. |

## Critical Rules

1. ALWAYS confirm scope and disciplines BEFORE extracting — never extract a whole set by reflex.
2. ALWAYS split first; NEVER re-ingest the full multi-MB set to answer a question.
3. ALWAYS extract the text layer before reaching for vision; use vision only on `sparse` / `image_only` pages.
4. NEVER use `--render-all` unless the set genuinely has no text layer anywhere.
5. NEVER treat a raw tag count as HIGH confidence — MEDIUM until reconciled against a schedule or a markup review.
6. NEVER silently reconcile a schedule/count disagreement — flag it.
7. NEVER attempt linear measurement by tracing or scaling a PDF; flag it `NOT_MEASURED` for a human.
8. NEVER calculate or infer a quantity during extraction — record only what is explicitly stated.
9. ALWAYS cite every fact to a sheet (and detail where applicable); `[UNVERIFIED]` when it cannot be sourced.
10. NEVER normalize specification language — preserve the drawing's exact wording.
11. ALWAYS run `--validate` to a clean exit before any downstream skill consumes the index.
12. ALWAYS check `--stats` for uncited sheets before declaring the index complete.
13. ALWAYS key the index by element, never by sheet — sheet-keyed output recreates the problem this skill solves.
14. NEVER re-extract a whole set on a revision — diff, then extract only what changed.
15. ALWAYS fix unreadable sheet numbers by hand rather than letting `page-NNN` propagate into citations.
16. ALWAYS use plain ASCII in every `.md` and JSON field (`ensure_ascii=True`) — no em-dashes, smart quotes, or degree symbols.

## Provenance

`detect_pdf_type.py`, `extract_text_tags.py`, and `markup_pdf.py` were adapted from the
`quantity-takeoff` skill, whose content derives from a published method by Tim Fairley /
Contractor OS. Kept: the three-way text-layer verdict, the tag-discovery-then-pattern
workflow, and markup-as-audit-trail. Changed: the source called text-layer counting
"100% accurate"; testing disproved that (9 counted where 8 existed, via schedule text
contamination), so the over-count defenses, the exclusion reporting, and the MEDIUM
confidence ceiling are BLDG additions.

The element-keyed index structure is modeled on IFC/BIM, per the same source's
observation that a 3D model would make this pipeline unnecessary.

The selective-render approach (text first, vision only on empty pages) was validated on a
75-page MEP set at 3915 Austin Blvd, Island Park NY.
