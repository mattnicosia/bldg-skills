# Source Verification Checklist

Run monthly. Catches dead URLs, drifted sources, duplicate signals, and stale categories before they corrupt your weekly brief.

This file is read by:

1. The skill itself (workflow step 6) when generating the source list — to set the user's expectations for what source verification will look like.
2. The monthly scheduled task fired by `/schedule` (per `scheduled-task-guide.md`). The scheduled task uses this checklist to evaluate every source and write an entry to `INTELLIGENCE/source-verification-log.md`.

## Per-source checks

For each source in `INTELLIGENCE/signal-stack.md`, answer:

- [ ] **URL still resolves?** (HTTP 200; not redirected to a parking page)
- [ ] **Returns recent content?** (Latest post within last 30 days)
- [ ] **Same publisher/handle?** (Domain unchanged; account not transferred or deleted)
- [ ] **Quality unchanged?** (Tone, depth, editorial standards comparable to when source was added)
- [ ] **Still distinct from other sources?** (Not duplicating signal already covered)

If 3+ checks fail, the source is unhealthy. Mark **remove**, **replace**, or **pause** in the action column.

## Stack-level checks

After all per-source checks, evaluate the stack as a whole:

- [ ] **Coverage still spans all 4 categories?** (customer/audience, competitor, market/category, internal sales/customer feedback)
- [ ] **Any source produced zero useful signals in last 4 weeks?** Drop it.
- [ ] **New buyer venue surfaced in the latest VOC update?** Read `CONTEXT/voc.md` and add any newly-mentioned venues.
- [ ] **Any competitor-move source went silent?** (No posts in 4+ weeks where they used to be active.) Investigate — they may be in a quiet period or the source died.
- [ ] **Stack still ≤25 sources total?** (Past 25, weekly briefs become noisy. Trim back.)

## Output format

Write one line per source per verification pass to `INTELLIGENCE/source-verification-log.md`. Format:

```markdown
| Date | Source | Status | Last modified | Action |
|---|---|---|---|---|
| 2026-06-01 | r/construction-tech | healthy | 2026-05-29 | kept |
| 2026-06-01 | Acme changelog | dead | 2025-11-04 | removed (5 months stale) |
| 2026-06-01 | BLS construction report | healthy | 2026-05-15 | kept |
```

Append, never overwrite. The verification log is a historical record — past entries inform whether a "now stale" source was always low-cadence or genuinely went dark.

## Stack-level entry

After per-source rows, append a stack-level summary row to the same log:

```markdown
| 2026-06-01 | STACK | 4-category coverage maintained | n/a | added 1 source from VOC, removed 1 dead changelog |
```

## Cadence

Monthly. The default `/schedule` prompt for this verification pass is in `scheduled-task-guide.md`.

## When to run off-cycle

- New connector added that surfaces internal-pulse signals (e.g., new Slack workspace) — re-run to add internal sources
- VOC refresh reveals 3+ new buyer venues you weren't watching — re-run to add customer/audience sources
- A weekly brief comes back nearly empty — likely sources are dead; run verification to find out which
- Suspected drift in tone or quality from your agent's briefs — verification catches whether the inputs are degrading
