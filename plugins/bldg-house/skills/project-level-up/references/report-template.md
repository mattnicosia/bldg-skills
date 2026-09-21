# Report templates

Create `/audit/<project>-<model>-<YYYYMMDD>/` when the user wants files written. Otherwise use these headings in the reply.

Keep mermaid in the markdown. Do not wrap mermaid in a screenshot unless asked.

---

## SCORECARD.md

```markdown
# Scorecard — <project> — <model> — <date>

| Axis | 1-5 | Note |
|---|---|---|
| Correctness / data integrity | | |
| AI routing efficiency | | |
| UI presence / wow | | |
| UX friction | | |
| Frontier utilization | | |
| Operability (evals, cost, fallbacks) | | |

Executive scan
- ...
- ...
```

---

## SYSTEM_MAP.md

```markdown
# System map

\`\`\`mermaid
flowchart LR
  UI --> API
  API --> IDB
  API --> Cloud
  API --> Models
\`\`\`

Surfaces
- ...

Stores
- ...
```

---

## AI_ROUTING.md

```markdown
# AI routing

\`\`\`mermaid
flowchart TD
  JobA --> ModelA
  JobB --> ModelB
\`\`\`

| File:line | Current | Class | Recommend | Why | Risk |
|---|---|---|---|---|---|
| | | | | | |
```

---

## CODE_FINDINGS.md

```markdown
# Code findings

## P0
### <title>
- Where: `path:line`
- Problem:
- Blast radius:
- Smallest patch:
- Verify:
```

---

## UI_UX.md

```markdown
# UI / UX

## Surface — <name>
- First glance:
- Hierarchy:
- Signature moment:
- Motion vs presence:
- Next prototype (one paragraph, no full rewrite):
```

---

## FRONTIER_UPSIDE.md

```markdown
# Frontier upside

What the new model makes newly cheap or newly possible
- ...

What to stop doing because the old model needed it
- ...
```

---

## PATCH_QUEUE.md

```markdown
# Patch queue

Do not implement until named by the user.

## P0-1 <title>
- Problem:
- Why it matters:
- Proposed change:
- Files:
- Blast radius:
- Verify:
```
