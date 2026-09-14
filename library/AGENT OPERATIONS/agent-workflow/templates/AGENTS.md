# AGENTS.md  -  Router

This file **routes** agents to the right skills, docs, and tools. It is not a novel. Keep product detail in linked docs. Update routes when systems move.

**First 7 lines after this title block in every system doc:** purpose · owner · status · when to update · canonical paths · traps · related routes.

## Product

- **Name:** <PRODUCT>
- **One-liner:** <WHAT IT DOES>
- **Primary cwd for coding:** <PATH>
- **Stack:** <STACK>
- **Deploy:** <WHERE>

## Bootstrap every session

1. Read this file fully once.
2. Load agent-workflow (or `docs/AGENT_WORKFLOW.md` if present).
3. Open/create worksheet under `docs/worksheets/` via agent-session-worksheet.
4. Only then open code.

## Route map (edit per product)

| If you need… | Open |
| --- | --- |
| Product intent / locked decisions | `BRIEF.md` or `docs/…` |
| Architecture / data model | `docs/…` |
| Coding conventions | `docs/CODING_CONVENTIONS.md` or CLAUDE.md sections |
| Session workflow | `docs/AGENT_WORKFLOW.md` |
| Review checklist | `docs/AGENT_REVIEW.md` |
| Test inventory | `docs/TESTS.md` |
| Worksheets | `docs/worksheets/` |
| Agent feedback log | `docs/agent-feedback.md` |
| Scripts helpers | `tools/` · `bin/` · `scripts/` |

## Commands that matter

```bash
# install
…
# dev server (always run for UI work)
…
# test (targeted first, then suite)
…
# lint / typecheck
…
# deploy (only when asked or gated)
…
```

## Firm laws (product-specific)

- List non-negotiables here (brand, RLS, money math, no-AI-takeoffs, etc.)
- Max ~8 bullets. Detail lives elsewhere.

## Self-healing docs

When you change a system: update its greppable 7-line summary **in the same change**. If a route above is wrong, fix AGENTS.md in the same session.

## Review + ship

- Multi-file ship: independent review (requesting-code-review / different model), not only author self-check.
- Commit worksheets with the work. Optional tag: `ws/YYYY-MM-DD-<slug>`.
- End with: targeted tests green, app smoke for touched surfaces, feedback rows.

## Never

- Expand this file into a full manual  -  link out.
- Leave Status/owner wrong on system docs you know you changed.
- Commit secrets into worksheets or docs.
