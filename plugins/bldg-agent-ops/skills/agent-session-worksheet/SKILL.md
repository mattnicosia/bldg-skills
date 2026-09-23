---
name: agent-session-worksheet
description: "Use when starting, continuing, or handing off agentic coding work. Session worksheet traces: init, update, handoff, git tag optional. Another agent must be able to finish from the sheet alone."
license: MIT
metadata:
  version: 1.0.0
  author: Kron / BLDG Labs
  platforms: [linux, macos]
  hermes:
    tags: [worksheet, handoff, session, recoverable, jamon]
    related_skills: [agent-workflow, plan, requesting-code-review]
---

# Agent Session Worksheet

Live session trace so a mid-failure agent can be replaced without re-discovery.

**Core principle:** If you cannot hand this file to a cold agent and have it resume in under 5 minutes, the worksheet is incomplete.

## When to Use

- Start of any multi-step product coding session
- Autonomous / night / async runs
- Before context-risk work (large refactors, long tool chains)
- Whenever work might pause partial

**Don't use for:** single-file typo, pure Q&A, irreversible external sends (those need human gates outside this sheet).

## Location and naming

```
docs/worksheets/YYYY-MM-DD-<short-slug>.md
```

- Slug: lowercase, hyphens, goal-derived (`capture-sms-retry`, `nova-rls-audit`).
- One active worksheet per goal. New goal = new file. Same goal across days: keep one file, append day sections.
- Always commit the worksheet with the related code.

Optional git tag (recommended for multi-hour autonomous blocks):

```bash
git tag "ws/YYYY-MM-DD-<short-slug>"
# after successful close (optional annotated):
git tag -a "ws/YYYY-MM-DD-<short-slug>-done" -m "worksheet closed"
```

## Init (completion: file exists, status active, goal + resume blank filled)

1. Create `docs/worksheets/` if missing.
2. Copy `templates/worksheet.md` from this skill (or inline structure below).
3. Fill: Goal, Success criteria, Constraints, Repo/cwd, Branch, Started, Status=`active`.
4. Add first log line: "Session opened. Goal locked."
5. Link the worksheet path into any `plan` file and professor/todo lists you open.

## Update discipline (completion: another agent could resume after each code chunk)

Update after every meaningful chunk (not every tool call):

- Files touched (paths)
- Commands that matter (dev server port, test cmd, migration)
- Decisions and why (one line each)
- Open risks / blockers
- Exact next step (imperative: "Run X then fix Y")

If the agent suspects session death risk (long stretch, model switch, crashy tools): update **before** the risky step.

## Handoff (completion: next agent can start without asking the previous one)

Set Status=`handoff` and fill:

1. **Resume command** (exact)
2. **Done so far** (bullet list, evidence not vibes)
3. **Not done**
4. **Do not redo** (settled decisions)
5. **Known landmines**
6. Related commit SHAs or tag name

## Close (completion: Status done or aborted, feedback written)

1. Status=`done` or `aborted` with one-line reason.
2. Feedback section: tools that helped, false paths, AGENTS.md/workflow patches suggested.
3. Commit worksheet with final work. Tag if policy above applies.
4. Point any follow-up worksheet at this one if work continues under a new slug.

## Template (inline)

```markdown
# Worksheet: <slug>

- Status: active | handoff | done | aborted
- Started: YYYY-MM-DD HH:MM TZ
- Closed:
- Repo / cwd:
- Branch:
- Goal:
- Success criteria:
- Constraints / non-goals:
- Plan path (if any):
- Git tag:

## Resume (keep current)

Exact next action:

## Done

-

## Not done

-

## Decisions

- Decision  -  why

## Files / surfaces

|

## Commands that worked

```
```

## Landmines

-

## Log

| Time | Note |
|------|------|
| | Session opened. Goal locked. |

## Feedback (session end)

- Worked:
- Burned tokens / dead ends:
- Patch AGENTS.md or agent-workflow?:
```

## Failure recovery recipe

When continuing after a dead session:

1. Open the newest `docs/worksheets/*` with Status active/handoff for this goal.
2. Trust **Resume** over chat memory.
3. Grep for the worksheet slug in git log/tags: `git log --oneline -- docs/worksheets/` and `git tag -l 'ws/*'`.
4. Re-run listed commands to re-establish environment before inventing new steps.
5. Append a log line: "Resumed by <agent> after handoff/fail."

## Common Pitfalls

1. **Vague next steps** like "continue implementation." Write the next shell command or file edit.
2. **Worksheet only at the end.** That is a diary, not a recovery tool.
3. **Storing secrets** (tokens, keys) on the worksheet. Link to env names only.
4. **Multiple active worksheets** for one goal. Merge log streams or close one.
5. **Skipping commit of the worksheet.** Future you will not find it.

## Verification Checklist

- [ ] Path under `docs/worksheets/` with dated slug
- [ ] Goal + success criteria + constraints filled
- [ ] Resume section always current while active
- [ ] Log shows progress, not just start
- [ ] Handoff fields complete when status=handoff
- [ ] Feedback filled when done/aborted
- [ ] Committed with related code; tag if multi-hour autonomous
