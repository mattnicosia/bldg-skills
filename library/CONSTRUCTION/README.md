# CONSTRUCTION Skills

Montana Contracting / BLDG Estimating construction skills. Built 2026-07-29.

## The pipeline

```
        drawing PDFs
              |
              v
      +----------------+
      |  drawing-index |   split -> classify -> extract -> element-keyed index.json
      +----------------+   OWNS all extraction. Run this first, always.
         |           |
         v           v
+---------------+  +--------------------------+
| sow-generator |  | sow-generator-quantities |
+---------------+  +--------------------------+
  SOW + leveling     SOW + leveling + separate
  ZERO quantities    quantity workbook
```

| Skill | Use when |
|---|---|
[`drawing-index`](drawing-index/SKILL.md) | Any task that reads drawings. Makes a set AI-readable once; everything else reads the index instead of the PDFs. |
[`sow-generator`](sow-generator/SKILL.md) | Scope of Work with four subcontractor bid-leveling columns. Zero quantities, zero pricing, by design. |
[`sow-generator-quantities`](sow-generator-quantities/SKILL.md) | Same SOW, plus a separate conceptual quantity workbook that opens on a mandatory READ FIRST disclaimer. |
`ROM_Budget_Range` | Rough order-of-magnitude budget ranges. |
`Proest-Export-*` | ProEst proposal and unit-cost exports. |

## System of record for project files

**SharePoint / OneDrive. Founder call 2026-09-08.** The estimate intake flow
files to Microsoft shared drives, not Dropbox. `estimate-intake_process-map_v1.md`
already said this in its header and contradicted itself in its Stage 2 heading;
the heading was the wrong half and is fixed.

One thing this does not settle. `add-to-estimating-bldg` creates BLDG Estimating
job folders in Dropbox at `/BLDG/BLDG Estimating`, with real paths and a real
template. Either that is a second tenant with its own storage, which is what the
adapter design expects, or it needs rewriting against SharePoint. Named as an
open decision for the Rocco map rather than guessed at here.

## Rules that hold across the suite

1. **One extraction pipeline.** `drawing-index` owns it. The other skills invoke it and never restate it. The previous `sow-generator` / `sow-generator-with-leveling` pair drifted 568 lines apart and one cross-referenced a "Phase 1b" that existed only in the other — that is what this structure prevents.
2. **`build_index.py --validate` is a gate, not a suggestion.** Non-zero exit means uncited specs, unresolvable sheet references, a quantity with no basis, or a placeholder project name. Do not generate anything from an index that has not passed.
3. **Scope documents carry no numbers.** Quantities live in their own workbook, in their own skill.
4. **A tag count is MEDIUM until reconciled.** Text-layer counting is not "100% accurate" — the schedule's own text inflates the count. Verified: 9 reported where 8 existed.
5. **Linear runs are never scaled off a PDF.** `NOT_MEASURED` is the honest, professional answer.
6. **Imperial only.** EA / SF / LF / CY / TON / CFM.

## Known gaps

- **Ratio figures in `sow-generator-quantities/references/trade-checklists.md` are unverified placeholders**, converted from metric source material written for another market. Replace with BLDG Estimating job history and mark them `VERIFIED`. Until then they must be labeled `ESTIMATED -- unverified ratio` in any output.
- **Takeoff-export ingestion is built but dormant** — no confirmed tool with data export as of 2026-07-29. Switching it on adds a `VERIFIED` tier that outranks every AI-derived quantity and retires the ratio estimates. This is the single largest available accuracy win.
- **`quantity-takeoff` and `electrical-estimator` still live in `~/.claude/skills/`** and hardcode paths to `~/.claude/skills/quantity-takeoff/scripts/`. They were deliberately left untouched so nothing broke mid-build. Repoint them at `drawing-index/scripts/` when convenient, and convert `trade-checklists.md` before either prices anything.

## Provenance

`detect_pdf_type.py`, `extract_text_tags.py`, `markup_pdf.py`, the primary/secondary
architecture, the confidence capping rules, and the sanity-check framework were adapted
from the `quantity-takeoff` skill, whose content derives from a published method by Tim
Fairley / Contractor OS. Kept the architecture; corrected the accuracy claims; converted
the market assumptions. Each file carries its own Provenance section.

`_archive/` holds the superseded `sow-generator-with-leveling` and
`sow-generator-with-quantities`. Kept rather than deleted — they hold the original
validation writeups (T2T 3915 Austin Blvd, 75-page MEP set).
