---
name: project-level-up
description: Level up an existing software project when a new frontier model ships. Trigger on project level-up, new model drop, audit all projects, model routing review, UI UX push across a repo, or frontier opportunity scan.
license: MIT
metadata:
  type: workflow
  version: "1.0"
---

# Project Level Up

Run this against one repo after a frontier model drop. Produce a review pack the user can approve. Do not rewrite the product until they say so.

## Mission

Find leverage the new model actually unlocks. Rank it. Write patches as a queue, not as a surprise rewrite.

Priority order never changes:

1. Correctness, data loss, auth, sync invariants
2. AI routing (stale IDs, wrong model class, missing fallbacks)
3. Architecture that will fight the next 12 months
4. UI presence and wow on primary surfaces
5. UX friction the new model can remove
6. Frontier-only product moves

If the repo is offline-first / IndexedDB / Supabase realtime, load and run `cloud-sync-auditor` during the code lane. Sync bugs outrank visual polish.

## Inputs to collect first

If missing, ask once, then proceed with explicit assumptions:

- Project name and repo path
- One-sentence product job
- Name of the new frontier model in the room
- Hard constraints (offline-first, org/multi-user, billing, etc.)
- Whether to write files yet (default no)

## Process

Follow this order. Skip a lane only when the repo has nothing in it. Say what you skipped.

### 1. Map

Identify surfaces, data stores, deploy path, and every AI call site.

Read `references/scan-patterns.md`. Run `scripts/scan-models.sh` on the repo when the path is available. Do not guess call sites — run the scanner or an equivalent ripgrep.

Draw the system map and AI call graph in mermaid. Templates live in `references/report-template.md`.

### 2. Model and AI stack

Load `references/model-registry.md` first. Treat it as the current routing source of truth. If the drop is newer than the registry date, update the registry recommendations in the report and flag the file as stale.

For every hit from the scanner:

- current ID
- recommended ID and class (flagship / workhorse / fast / local / vision / embed)
- why
- risk
- cost or latency delta if known

Rules:

- Route. Do not upgrade every call to the newest flagship.
- Flagship is for hard judgment — architecture, takeoff, design direction, ambiguous tool use.
- Workhorse or fast models handle classification, extraction, routing, cheap summaries.
- Every recommendation includes a fallback ID.
- Propose shrinking prompts that exist only to babysit a weaker model.

### 3. Code

Ranked review only. No linter dump.

Hunt first: data loss, races, auth/RLS, crash paths on sync/upload, unbounded loops, missing verification around agents.

Then: dead 8-month-old agent scaffolding, abstractions that exist because the old model was weak, N+1 and full re-syncs.

Each finding needs `path:line`, blast radius, and a smallest patch. Do not propose a rewrite when a tight patch captures the gain.

### 4. UI

Load `references/ui-wow.md`. Audit primary surfaces only (app shell, landing/signin, the screen users live on).

Score each surface for first-glance hierarchy, material presence, and whether a signature moment exists. Polite even layouts fail this lane.

Do not invent a new brand. Amplify what is there unless the user asked for a restyle.

If `references/novaterra.md` matches this product, apply those tokens and invariants.

### 5. UX and product

Where the new model can change the job, not just the pixels:

- fewer clicks to a trustworthy result
- confidence / human-in-the-loop instead of silent wrong output
- empty, error, offline, and loading states that currently drop people
- agents that propose instead of only extract

### 6. Frontier upside

Ask what the codebase still treats as impossible or too expensive. If this lane is empty, the run was only a code review — call that out as a miss.

Examples: vision self-check on generated UI, collapsing a prompt chain, taking work off a flagship onto a new mid-tier, longer-horizon agents with real verification.

## Output contract

Write one folder, same shape every time:

```text
/audit/<project>-<model>-<YYYYMMDD>/
  SCORECARD.md
  SYSTEM_MAP.md
  AI_ROUTING.md
  CODE_FINDINGS.md
  UI_UX.md
  FRONTIER_UPSIDE.md
  PATCH_QUEUE.md
```

Use the templates in `references/report-template.md`. If the user did not give a write path, emit the same files in the response and offer to save them.

`PATCH_QUEUE.md` is the only working file. Each item is independently shippable and includes problem, why, proposed change, blast radius, verify steps.

Default mode — report only. Do not implement until the user names queue items.

## Ranking

Score every item High/Med/Low on leverage and on risk.

Do this week:

- high leverage / high risk (carefully)
- high leverage / low risk

Ignore low / low unless it is a one-line model ID bump.

## Anti-patterns

- Rewriting half the app while we are here
- Replacing every model ID with the new flagship
- UI animation with no hierarchy change
- Findings without a path or a verify step
- Inventing architecture the current app does not need
- Skipping the scanner and guessing call sites
- Letting wow work outrank data-loss findings on a sync app

## Invocation shape

The user prompt should look like this. If they under-specify, fill from context and state assumptions.

```text
Load project-level-up.

Project: [name + path]
Product job: [one sentence]
New frontier model: [name]
Constraints: [offline-first, org, etc.]
Do not write product code yet.

Run all six lanes. Produce the standard review pack.
Call cloud-sync-auditor if this repo has IDB or Supabase realtime.
```
