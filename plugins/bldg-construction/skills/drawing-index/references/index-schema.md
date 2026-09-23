# index.json Schema

The contract between `drawing-index` and every skill that consumes it. Enforced by
`scripts/build_index.py --validate`, which exits non-zero on any hard error.

Version: `1.0`. Bump `schema_version` and update this file together.

## Top level

```json
{
  "schema_version": "1.0",
  "project":    { "name": "...", "address": "...", "revision": "..." },
  "extraction": { "...coverage and vision-pass bookkeeping..." },
  "sheets":     [ { "...one per sheet..." } ],
  "elements":   [ { "...one per physical thing being built..." } ],
  "open_items": [ { "...RFI candidates, contradictions, unreadable content..." } ]
}
```

### `project`

| Field | Required | Notes |
|---|---|---|
`name` | yes | Exactly as on the cover-sheet titleblock. `Untitled`, `Untitled Project`, blank, or anything starting `TODO` is a **hard validation failure** — resolve the real name. Fall back to the name the user confirmed at invocation, never to a placeholder. |
`address` | recommended | |
`revision` | recommended | Revision number + date from the titleblock. Needed for the revision workflow. |

### `extraction`

Written by `--skeleton`. Do not hand-edit except to correct sheet counts after fixing
unnamed sheets.

| Field | Notes |
|---|---|
`sheet_count` | Total sheets processed |
`vector_sheets` / `sparse_sheets` / `image_only_sheets` | Text-layer verdict tallies |
`vision_pass_required` | Sheet numbers needing a vision pass. Non-empty at validation raises a warning — confirm the pass actually ran. |
`unnamed_sheets` | Sheets whose number could not be read. Fix by hand; do not let `page-NNN` reach a citation. |

### `sheets[]`

| Field | Required | Notes |
|---|---|---|
`sheet_number` | yes | `A-101`, `M-601`. Exactly as the title block prints it, suffix and all (`S-100.00`). Citations resolve against it; write the number, do not normalise it. |
`discipline` | yes | Architectural, Structural, Mechanical, ... |
`text_layer` | yes | `vector` \| `sparse` \| `image_only` |
`needs_vision` | yes | boolean |
`title` | recommended | Sheet title from the titleblock |
`summary` | recommended | One line: what is on this sheet |
`source_issue` | on a merged set | Which issue this sheet came from, e.g. `Addendum No.1, 2026-09-17` or `Issued for Owner Review; not reissued`. |
`reissued` | on a merged set | `true` when the latest issue reissued this sheet. |
`superseded_by` | when dead | The sheet number that replaced this one. See below. |

### A sheet that was replaced under a different number

A merged set holds the sheets the latest issue reissued plus the earlier ones it left
alone. That works while a reissue keeps its number, because the new sheet overwrites the
old one by filename.

It breaks when the architect changes the number. Addendum No.1 on job 260120 reissued the
structural framing plan as `S-001.01` rather than `S-001.00`, so the merge kept both: one
live sheet and one dead one. By count that is indistinguishable from a subdivided series
like `A-101.01` / `A-101.02`, so a bare `S-001` named two sheets and resolved to neither.

`reissued: false` cannot express this. It is literally true of `S-001.00`, because the
addendum did not reissue that sheet, it replaced it. Mark the dead sheet instead:

```json
{ "sheet_number": "S-001.00", "reissued": false, "superseded_by": "S-001.01" }
```

Citations then resolve against the live sheets, so `S-001` names `S-001.01`. An explicit
citation to `S-001.00` still resolves, because it names a sheet the set really holds, and
validation warns rather than failing. `superseded_by` naming a sheet outside the set, or
a sheet naming itself, is a hard error.

**Do not delete the dead sheet instead.** It was issued, it is part of the record, and
notes legitimately reason about it: 260120's index says "no construction joints are shown
anywhere on `S-001.00`, `S-001.01` or `S-100.00`", which stops being checkable the moment
the sheet leaves the set.

Where several live sheets share a base and none is marked, validation warns. A subdivided
series is fine and the warning is the prompt to confirm that is what it is.

## `elements[]` — the payload

One entry per physical thing being built. **Not one per sheet.** If you find yourself
writing one element per sheet, stop: you have rebuilt a sheet index and lost the point.

### Required — validation fails without these

| Field | Type | Notes |
|---|---|---|
`element` | string | The thing itself: `Slab On Grade`, `Perimeter Grade Beam`, `Rooftop Unit RTU-1`, `Toilet Exhaust Fan`. Title Case. |
`trade` | string | `Concrete`, `HVAC`, `Electrical`, `Plumbing`, `Drywall & Carpentry` |
`csi_subdivision` | string | 6-digit MasterFormat: `03 30 00`. Must match the code set `sow-generator` uses so scope lines route without translation. |
`source_sheets` | string[] | Every sheet describing this element. `5/S-301` for a detail, `S-301` for a plan. **Write the citation the way the drawing prints it.** A sheet numbered `S-100.00` cited as `S-100` resolves, because the set ships one sheet under that base. A base the set ships several sheets under (`A-101.01`, `A-101.02`) names none of them and hard-fails. |

### Recommended

| Field | Type | Notes |
|---|---|---|
`category` | string | Coarse grouping: `Substructure`, `Superstructure`, `Enclosure`, `Interiors`, `Services`, `Sitework` |
`location` | string | Where it is. Missing this raises a warning — scoping without it is guesswork. |
`specifications` | object[] | See below |
`quantities` | object[] | See below |
`notes` | string[] | Anything a scoper or estimator needs to know |
`related_elements` | string[] | Other `element` values this connects to. What makes the index a graph rather than a list. |
`confidence` | string | `HIGH` \| `MEDIUM` \| `LOW` for the element's overall extraction reliability |
`unverified` | boolean | `true` when content could not be resolved even after a vision pass |

### `specifications[]`

```json
{"value": "4000 PSI", "source": "S-101 general note 3"}
```

`source` is **mandatory**. An uncited spec is a hard validation failure.

Preserve the drawing's exact wording. `[Not Specified]` when the drawing calls out
nothing — never invent, never normalize. Bracket format downstream is
`[Manufacturer Model Color]`, in that order.

### `quantities[]`

```json
{"value": 8, "unit": "EA", "basis": "P1 tag count on S-301, reconciled vs pier schedule",
 "confidence": "HIGH"}
```

| Field | Notes |
|---|---|
`value` | Number, or `null` when not determinable. A range goes in `value_low`/`value_high` — **never collapse a range to a point estimate to look decisive.** |
`unit` | Imperial: `EA`, `SF`, `LF`, `CY`, `TON`, `CFM`, `GAL`. Montana bids in imperial. |
`basis` | **Mandatory when `value` is non-null.** How the number was arrived at. An uncited quantity is a hallucination risk and fails validation. |
`confidence` | See tiers below. Missing raises a warning. |

#### Confidence tiers

| Tier | Meaning |
|---|---|
`VERIFIED` | From a human takeoff export. Outranks everything. Retires any AI-derived value for the same element. |
`HIGH` | Explicitly stated on the drawings, or a clean schedule extraction, or a tag count **reconciled** against a schedule or markup review. |
`MEDIUM` | A raw unreconciled tag count. A schedule with minor ambiguity. A value derived from a HIGH primary using an **assumed** ratio. |
`LOW` | Vision-based count. Any scaled measurement. Anything derived from a LOW primary. |
`NOT_MEASURED` | Genuinely not determinable from the drawings — needs a human takeoff. The honest answer for linear runs. |

Two rules carried from `measurement-methods.md`:

1. **A derived quantity can never exceed its source's confidence.** A volume from a LOW
   area is LOW, however clean the depth note.
2. **A derivation whose ratio is read off the drawings keeps the source's confidence; a
   derivation whose ratio is assumed caps at MEDIUM.**

## `open_items[]`

```json
{"item": "HVAC equipment schedule on M-601",
 "issue": "Raster table, unreadable after vision pass",
 "action": "RFI to engineer",
 "sheets": ["M-601"]}
```

Everything a human has to resolve: unreadable content, cross-sheet contradictions,
schedule-vs-count disagreements, missing specs. This is the list that becomes RFIs.

**Never silently resolve a contradiction.** Two sheets disagreeing is an `open_item`, not
a judgment call to make quietly.

## Validation

```bash
python scripts/build_index.py drawings/index.json --validate   # exit 1 on hard error
python scripts/build_index.py drawings/index.json --stats
```

Hard errors: placeholder project name; no `elements[]`; missing required field;
`source_sheets` ref that resolves to no sheet, or to an ambiguous base; spec with no
`source`; non-null quantity with no `basis`.

Warnings: quantity with no `confidence`; element with no `location`; duplicate
element+CSI pair; sheets still flagged `needs_vision`.

`--stats` additionally reports sheets no element cites. Check those before calling the
index done — they are either scope-free or a gap in extraction.

## Downstream consumers

| Skill | Reads |
|---|---|
`sow-generator` | `elements[]` grouped by `csi_subdivision`; `specifications` for bracket text; `source_sheets` for the Reference column; `open_items` for Conflicts and TBD |
`sow-generator` (quantified mode) | `quantities[]` with tiers; `extraction` for confidence context |
`electrical-estimator` | `elements[]` filtered to Divisions 26/27/28; `quantities[]` as the count basis |
`quantity-takeoff` | `sheets[]` for text-layer verdicts; per-sheet PDFs for counting |

Changing a required field breaks all four. Bump `schema_version` and update them together.
