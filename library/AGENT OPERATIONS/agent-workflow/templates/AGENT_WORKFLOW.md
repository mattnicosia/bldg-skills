# AGENT_WORKFLOW

Repo-local pointer to the shared agent-workflow skill.

- Purpose: Tag-in workflow for product coding sessions in this repo.
- Owner: Kron ops
- Status: active
- When to update: session sequence changes globally (prefer updating the Hermes skill, then refresh this stub)
- Canonical paths: Hermes skill `agent-workflow`; worksheets in `docs/worksheets/`
- Traps: Do not fork a full copy here unless this product needs overrides
- Related: AGENTS.md bootstrap · skill `agent-session-worksheet`

## Overrides for this product

(None yet. Add only product-specific steps, ports, or must-run commands.)

## Boot

1. Read root `AGENTS.md` (router).
2. Load skill `agent-workflow` (Hermes / Claude Code / Codex equiv).
3. Create or continue `docs/worksheets/YYYY-MM-DD-<slug>.md`.
4. Plan → implement (run app + tests) → review → wrap + feedback.
