---
name: agent-workflow
description: "Use when starting or running a product coding session in a BLDG repo. Standard session workflow: bootstrap AGENTS.md router, worksheet, plan/build/review loop, keep docs greppable, finish with run-app + feedback."
license: MIT
metadata:
  version: 1.0.0
  author: Kron / BLDG Labs
  platforms: [linux, macos]
  hermes:
    tags: [workflow, agents-md, coding, session, jamon]
    related_skills: [agent-session-worksheet, plan, test-driven-development, requesting-code-review, systematic-debugging, simplify-code]
---

# Agent Workflow

Standard coding session for BLDG product repos (Capture, NOVATERRA, bldg-labs, and peers). Tag or load this in most product sessions.

**Core principle:** The agent runs a recoverable process, not a chat. Router first. Worksheet second. App and tests as it goes. Different-model review when shipping. Feedback closed at wrap.

## When to Use

- Starting work in a product repo (feature, bugfix, refactor, async/night stretch)
- User tags `@AGENT_WORKFLOW`, `@agent-workflow`, or says "use the standard workflow"
- Autonomous or multi-hour work that another agent may need to continue

**Don't use for:** pure research outside a repo, single-line ops with no code, Kron CoS non-coding tasks.

## Session sequence

### 0. Bootstrap (completion: router + worksheet exist, goal written)

1. Read repo root `AGENTS.md` first. It is a **router**, not a dump. Follow its route map; do not invent a parallel map.
2. If missing, create from `templates/AGENTS.md` in this skill and fill product-specific routes.
3. Init a session worksheet via skill `agent-session-worksheet` (or create `docs/worksheets/YYYY-MM-DD-<slug>.md` using that template).
4. Write goal, constraints, stop conditions on the worksheet in the first 2 minutes.
5. Prefer loading `docs/AGENT_WORKFLOW.md` in-repo if present (repo-local overrides). Else this skill is the default.

### 1. Orient (completion: you can state current system truth in 5 lines)

1. Use AGENTS.md routes to open only the docs you need.
2. Prefer greppable docs: first **7 lines after title** of every system doc should summarize purpose, owner, status, when to update. If stale, fix during wrap (self-heal).
3. Skim open worksheets for incomplete handoffs.

### 2. Plan (completion: checkable plan on worksheet; no code yet unless trivial)

1. Load skill `plan` for non-trivial work. Save plan path on the worksheet.
2. Split work into bite-sized tasks with verification for each.
3. Name risks and the test that would catch each.
4. For money, RLS, sync, auth: escalate model/effort per repo CLAUDE/AGENTS rules.

### 3. Implement in a tight loop (completion: each task has proof, not intention)

1. Prefer skill `test-driven-development` for behavior changes.
2. **Always run the app** for UI/runtime changes. Fix what you break before claiming done.
3. Run targeted tests as you go. Add missing tests when behavior is new.
4. Update the worksheet after each meaningful step: what changed, what's left, how to resume.
5. Update greppable system docs when behavior/contract changes (same PR/commit as code).
6. Custom scripts that save tokens go under repo `tools/` or `bin/`; document in AGENTS.md route map when added.

### 4. Review gates (completion: at least one gate when shipping)

Stages where independent review is required:

| Stage | When | Who |
|-------|------|-----|
| Research | ambiguous design or multi-path choice | different model or persona pass |
| Plan | before large implementation | plan critique / grill |
| Implementation | before commit of multi-file work | skill `requesting-code-review` |
| Wrap-up | before merge / handoff | different model than author if available |

Personas (pick what fits): maintainability, security, performance, AI smells, domain expert (e.g. estimating, lead-ops). Prefer a reviewer that is not the author model.

If CLI multi-agent review exists (`tools/bin/agent_review` later), use it. Until then: `delegate_task` or separate model pass with the review checklist in AGENTS.md / `docs/AGENT_REVIEW.md`.

### 5. Wrap (completion: tests/app green for touched paths, worksheet closed, feedback row written)

1. Run targeted tests + lint/typecheck for touched areas.
2. Run full suite when the change is cross-cutting or end-of-shift.
3. Commit worksheet with the work (and git tag if the worksheet skill calls for it).
4. Append session feedback rows (what worked, what burned tokens, what to change in AGENTS.md / this skill). Prefer `docs/agent-feedback.md` or the worksheet Feedback section.
5. If docs are wrong relative to code, fix them now. Stale docs are people debt the next agent pays interest on.
6. Leave the worksheet state as `done` or `handoff` with exact next command.

## Repo conventions this workflow expects

- `AGENTS.md` at the directory the agent uses as cwd (usually repo root; Capture may use `web/` for dashboard work  -  open both root and web routers).
- Greppable docs house style: see `references/docs-house-style.md`.
- Optional in-repo copy of this workflow: `docs/AGENT_WORKFLOW.md`.
- Worksheets: `docs/worksheets/`.
- Coding conventions stay short in `docs/CODING_CONVENTIONS.md` or AGENTS route; bulk go into linters.

## Self-heal rule

If you discover a missing route, broken command, or wrong doc summary while working:

1. Fix the AGENTS.md route or the doc header in the same session.
2. Note the fix on the worksheet under Feedback.
3. Do not open a separate "docs later" task without a written handoff.

## Rationalizations (Don't let yourself get away with these)

Every agent tries to skip steps. Here are the excuses you will hear yourself make, and why each one is wrong.

| The excuse you'll think | Why it's wrong | What to do instead |
|---|---|---|
| "This is a quick fix, I don't need a worksheet." | "Quick fix" is how every multi-hour debugging session starts. Without a worksheet, the next agent (or you after a context switch) has zero state. | Create the worksheet. Writing "trivial fix to X" takes 30 seconds. Skipping costs hours when you get pulled away. |
| "The plan is obvious, I'll just start coding." | Obvious plans are the ones with hidden assumptions. Coding without a plan is exploration dressed as implementation. When it takes longer than expected, you have no checkpoint to return to. | Run `plan` for anything non-trivial. A bad plan is a checkpoint. No plan is not a strategy. |
| "The tests pass, I don't need to run the app." | A green test suite with a blank page or broken layout is a failed session. Tests assert logic, not rendering. The user sees the app, not your test results. | Always run the app for UI or runtime changes. Fix visual breaks before calling anything done. |
| "I'm the same model, I'll review my own work." | You cannot catch your own blind spots. You wrote the code with your assumptions baked in. A different model or persona sees what you assumed away. | Route multi-file changes through `requesting-code-review` or a different model pass. Same-model review is a speed bump, not a gate. |
| "I'll update the docs later." | "Later" is a graveyard. The next agent loads stale docs, wastes time, and trusts wrong information. Stale docs are people debt — you borrow against the next agent's time. | Update the doc in the same commit. If the behavior changed, the doc changes with it. No separate PR, no tracking issue, no "later." |
| "I fixed it, no need to update the worksheet." | The worksheet is the handoff. The next agent reading it sees the old unfinished state and assumes the work is still open. They redo work or chase dead ends. | Update the worksheet: what changed, what's left, next command. One line minimum. |
| "I'll add the feedback row next time." | There is no next time. The session ends, you move on, and the lesson evaporates. Feedback that isn't written is feedback that didn't happen. | Append the feedback row before closing the session. What worked, what burned tokens, what to change. |
| "This is just a one-line change, I'll skip the review gate." | One-line changes break production. A missing null check, a wrong default, a typo in a key — the blast radius is the same. | Every multi-file change hits a review gate. Single-file behavioral changes still get a different-model pass if they touch money, auth, or data. |

## Technical Hazards (Environmental, not rationalizations)

These are not excuses you'll make — they are environmental risks to actively guard against.

1. **Sibling subagent conflicts.** When Hermes spawns concurrent subagents (`sa-1-*`, `sa-2-*`), they may modify the same files you're editing. The `patch` tool's `_warning` field is your signal: "file was modified by sibling subagent at HH:MM:SS — re-read before writing." When you see this:
   - **Re-read the file immediately** before any further edits.
   - **Switch to `write_file`** (full atomic replacement) instead of `patch` (text-matching). `patch` relies on exact string matches that sibling edits can break — `write_file` replaces the whole file in one shot.
   - **Check for corruption**: orphaned code fragments, extra closing braces, duplicated sections, or misordered blocks. Sibling subagents can leave files in a structurally broken state.
   - If corruption is found, re-read the full file and use `write_file` with a corrected version. Don't try incremental patches on a corrupted file — you'll chase ghosts.
   - If the sibling subagent is working against your task (e.g., restoring code you're removing), complete your work in one atomic `write_file` pass and let the build verify correctness.
2. **Concurrent subagent overwrite on multi-file features.** When you need to modify files A and B and they depend on each other (e.g. a hook exports a function and the component imports it), do NOT write A, then write B using `patch()` — a sibling subagent can overwrite A between the two writes, producing a type mismatch. The `write_file` tool warns about this with "modified by sibling subagent… after this agent's last read" but incremental patches can still land out of sync. **Fix:** write both files with `write_file` (not `patch`) in immediate succession without intermediate reads, then build. If the build still fails with a mismatch, read both files fresh and rewrite them atomically in a single turn. For 3+ interdependent files, write them all in one response turn with no tool calls between.
3. **Em-dashes in user-facing product copy.** Brand law. Use periods, commas, colons, or hyphens.

## Verification (Evidence required — "seems right" is not sufficient)

Every checkpoint below requires proof. You cannot mentally tick a box. Produce the evidence or the session is not done.

| What to verify | Evidence required | Why "done" isn't enough |
|---|---|---|
| AGENTS.md read; correct routes opened | State which routes you opened, by section name, in the worksheet's first entry. "I read it" is not evidence — which routes? | Loading the wrong docs wastes the first 20 minutes. Name them so the next agent knows your context boundary. |
| Worksheet init with goal + resume notes | The worksheet file exists at a known path and contains a filled goal line. Paste the path and the goal line to the chat. | A missing worksheet means the next agent has no state. The path is the handoff address. |
| Plan exists for non-trivial work | Plan file path written on the worksheet, or "no plan — trivial" with a one-line justification. | Plans without paths are ghost plans. Justification without a location is intention without a location. |
| App actually run for runtime changes | Paste the console line showing the dev server started successfully, or a screenshot of a rendered page. "It builds" is not "it runs." | A green build with a dead page is a failed session. The user sees the page, not your build output. |
| Targeted tests written/run for behavior changes | Paste the test command and its output (pass/fail counts). For new tests, name the test file and describe what it covers. | "I'm sure it works" is not evidence. Test output is. If you can't point to a passing test, you haven't verified. |
| Review gate hit before shipping multi-file work | Name the reviewer (model, persona, or skill) and paste one concrete finding or "no issues found." | Unreviewed multi-file changes are the #1 source of production regressions. A review with zero findings is still a review — but you must name who did it. |
| Docs self-healed if stale | State which doc changed and what the header now says. "Updated docs" is not evidence — which doc, what changed? | Stale docs poison the next agent. Vague self-heal claims are the same as no self-heal. |
| Feedback row written; worksheet status set | Paste the feedback row and the final status line (`done` or `handoff` with next command). | Feedback that isn't written didn't happen. A worksheet without a status is a session that never closed. |

## One-shot boot prompt (paste into a coding agent)

```text
Load skill agent-workflow (or @docs/AGENT_WORKFLOW.md).
Read AGENTS.md as router only.
Open/create session worksheet for this goal: <GOAL>.
Then plan, implement, run the app and tests, and wrap with feedback.
```
